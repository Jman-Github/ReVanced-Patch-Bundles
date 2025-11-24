package me.jman.parser

import kotlinx.serialization.SerializationException
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.jsonArray
import java.io.File
import java.io.FileNotFoundException
import java.net.URI
import java.net.URISyntaxException
import java.util.Locale
import kotlin.comparisons.compareBy

private const val BUNDLE_FILE_STEM = "-patches-bundle"
private const val PATCH_LIST_SUFFIX = "patches-list.json"

private val prioritizedReleaseTags = listOf("latest", "dev", "stable")

private val prettyJson = Json { prettyPrint = true }
private val parsingJson = Json { ignoreUnknownKeys = true }

private val patchCache = mutableMapOf<String, JsonArray>()

private enum class ReleaseType(
    val priority: Int,
    private vararg val aliases: String
) {
    LATEST(0, "latest", "nightly"),
    DEV(1, "dev", "alpha", "beta", "snapshot", "preview", "canary"),
    STABLE(2, "stable", "release"),
    OTHER(3);

    companion object {
        fun fromTag(tag: String): ReleaseType {
            val normalized = tag.lowercase(Locale.ROOT)
            return values().firstOrNull { type ->
                if (type.aliases.isEmpty()) {
                    false
                } else {
                    type.aliases.any { it == normalized }
                }
            } ?: OTHER
        }
    }
}

private data class BundleVariant(
    val file: File,
    val releaseTag: String,
    val releaseType: ReleaseType
)

private data class ParsedBundle(
    val version: String,
    val downloadUrl: String
)

private fun extractReleaseTag(bundleName: String, fileName: String): String {
    val withoutExtension = fileName.removeSuffix(".json")
    val prefix = "$bundleName-"
    val withoutPrefix = when {
        withoutExtension.startsWith(prefix) -> withoutExtension.removePrefix(prefix)
        withoutExtension == bundleName -> ""
        else -> withoutExtension
    }
    val trimmed = when {
        withoutPrefix.endsWith(BUNDLE_FILE_STEM) -> withoutPrefix.removeSuffix(BUNDLE_FILE_STEM)
        withoutPrefix.endsWith("-patches") -> withoutPrefix.removeSuffix("-patches")
        withoutPrefix.endsWith("-bundle") -> withoutPrefix.removeSuffix("-bundle")
        else -> withoutPrefix
    }
    val cleaned = trimmed.trim('-')
    val releaseTag = cleaned.substringBefore('-').ifBlank { cleaned }
    if (releaseTag.isNotBlank()) {
        return releaseTag
    }
    val fallback = withoutPrefix.ifBlank { withoutExtension }
    val fallbackTrimmed = fallback
        .removeSuffix(BUNDLE_FILE_STEM)
        .removeSuffix("-patches")
        .removeSuffix("-bundle")
        .trim('-')
    return fallbackTrimmed.ifBlank { fallback }
}

private fun normalizeMetadataValue(value: String?): String? {
    if (value == null) {
        return null
    }
    val trimmed = value.trim()
    if (trimmed.isEmpty()) {
        return null
    }
    if (trimmed.equals("N/A", ignoreCase = true)) {
        return null
    }
    return trimmed
}

private fun parseBundleMetadata(variant: BundleVariant): ParsedBundle? {
    val content = variant.file.readText()
    val parsedModern = try {
        parsingJson.decodeFromString<BundleFile>(content)
    } catch (_: SerializationException) {
        null
    }
    if (parsedModern != null) {
        val version = normalizeMetadataValue(parsedModern.version)
        if (version == null) {
            Logger.warning("Version is invalid.")
            return null
        }
        val downloadUrl = normalizeMetadataValue(parsedModern.downloadUrl)
        if (downloadUrl == null) {
            Logger.warning("Download URL is invalid.")
            return null
        }
        return ParsedBundle(version, downloadUrl)
    }

    val parsedLegacy = try {
        parsingJson.decodeFromString<LegacyBundleFile>(content)
    } catch (_: SerializationException) {
        null
    }
    if (parsedLegacy != null) {
        val patches = parsedLegacy.patches
        val version = normalizeMetadataValue(patches?.version)
        if (version == null) {
            Logger.warning("Version is invalid.")
            return null
        }
        val downloadUrl = normalizeMetadataValue(patches?.url)
        if (downloadUrl == null) {
            Logger.warning("Download URL is invalid.")
            return null
        }
        return ParsedBundle(version, downloadUrl)
    }

    Logger.warning("Bundle is not supported.")
    return null
}

private fun loadBundleVariants(bundleFolder: File, bundleName: String): List<BundleVariant> {
    val grouped = linkedMapOf<String, MutableList<BundleVariant>>()

    bundleFolder
        .listFiles()
        ?.asSequence()
        ?.filter { it.isFile }
        ?.filter { it.extension.equals("json", ignoreCase = true) }
        ?.filterNot { it.name.endsWith(PATCH_LIST_SUFFIX, ignoreCase = true) }
        ?.forEach { file ->
            val releaseTag = extractReleaseTag(bundleName, file.name)
            val releaseType = ReleaseType.fromTag(releaseTag)
            val key = releaseTag.lowercase(Locale.ROOT)
            grouped.getOrPut(key) { mutableListOf() }.add(
                BundleVariant(
                    file = file,
                    releaseTag = releaseTag,
                    releaseType = releaseType
                )
            )
        }

    val ordered = mutableListOf<BundleVariant>()

    for (preferred in prioritizedReleaseTags) {
        grouped.remove(preferred)?.let { variants ->
            variants.sortBy { it.file.name }
            ordered.addAll(variants)
        }
    }

    grouped.values
        .flatten()
        .sortedWith(compareBy<BundleVariant> { it.releaseType.priority }.thenBy { it.file.name })
        .let(ordered::addAll)

    return ordered
}

private fun readExistingPatches(file: File): LocalPatchesFile? {
    if (!file.exists()) {
        return null
    }
    return try {
        parsingJson.decodeFromString<LocalPatchesFile>(file.readText())
    } catch (_: SerializationException) {
        Logger.warning("Existing patch list is invalid JSON.")
        null
    } catch (_: IllegalArgumentException) {
        Logger.warning("Existing patch list is invalid JSON.")
        null
    }
}

private fun canonicalizeElement(element: JsonElement): JsonElement {
    return when (element) {
        is JsonObject -> {
            val sortedKeys = element.keys.sorted()
            buildJsonObject {
                for (key in sortedKeys) {
                    put(key, canonicalizeElement(element.getValue(key)))
                }
            }
        }
        is JsonArray -> JsonArray(element.map(::canonicalizeElement))
        else -> element
    }
}

private fun extractPatchName(element: JsonElement): String {
    val obj = element as? JsonObject ?: return ""
    val primitive = obj["name"] as? JsonPrimitive ?: return ""
    return primitive.contentOrNull?.trim() ?: ""
}

private fun canonicalizePatchArray(patches: JsonArray): JsonArray {
    val cleaned = sanitizeDependencies(patches)
    val canonicalized = cleaned.mapIndexed { index, element ->
        Triple(index, extractPatchName(element), canonicalizeElement(element))
    }
    val comparator = compareBy<Triple<Int, String, JsonElement>> { it.second.lowercase(Locale.ROOT) }
        .thenBy { it.second }
        .thenBy { it.first }
    val sorted = canonicalized.sortedWith(comparator).map { it.third }
    return JsonArray(sorted)
}

private fun sanitizeDependencies(patches: JsonArray): JsonArray {
    return JsonArray(
        patches.map { element ->
            val obj = element as? JsonObject ?: return@map element
            val dependencies = obj["dependencies"] as? JsonArray ?: return@map element
            val sanitized = JsonArray(
                dependencies.map { dep ->
                    val primitive = dep as? JsonPrimitive ?: return@map dep
                    JsonPrimitive(primitive.content.substringBefore("@"))
                }
            )
            buildJsonObject {
                for ((key, value) in obj) {
                    if (key == "dependencies") {
                        put(key, sanitized)
                    } else {
                        put(key, value)
                    }
                }
            }
        }
    )
}

private fun generatePatchList(downloadUri: URI): JsonArray? {
    return try {
        val jsonText = generatePatchesFromUrl(downloadUri)
        val element: JsonElement = Json.parseToJsonElement(jsonText)
        val array = element as? JsonArray
        if (array == null) {
            Logger.warning("Generated patches are not a JSON array.")
            return null
        }
        canonicalizePatchArray(array)
    } catch (_: FileNotFoundException) {
        Logger.warning("The .rvp file was not found.")
        null
    } catch (_: SerializationException) {
        Logger.warning("Generated patches are not valid JSON.")
        null
    } catch (_: IllegalArgumentException) {
        Logger.warning("Generated patches are not valid JSON.")
        null
    }
}

private fun writePatchList(outputFile: File, version: String, patches: JsonArray) {
    val payload = LocalPatchesFile(version, patches)
    outputFile.writeText(prettyJson.encodeToString(payload))
}

private fun processBundle(bundleFolder: File) {
    val bundleName = bundleFolder.name.removeSuffix("-patch-bundles")
    val variants = loadBundleVariants(bundleFolder, bundleName)

    variants.forEachGroupLogged({ "Processing file ${it.file.name}" }) processVariant@{ variant ->
        Logger.info("Processing ${variant.releaseTag} release...")
        val parsedBundle = parseBundleMetadata(variant) ?: return@processVariant

        val outputPatchesFile = File(bundleFolder, "$bundleName-${variant.releaseTag}-$PATCH_LIST_SUFFIX")
        val existingContent = readExistingPatches(outputPatchesFile)
        if (existingContent == null) {
            Logger.info("No previous version found. Processing for the first time...")
        } else if (existingContent.version != parsedBundle.version) {
            Logger.info("Version ${existingContent.version} -> ${parsedBundle.version}")
        } else {
            Logger.info("Version ${parsedBundle.version} exists; verifying content")
        }

        val downloadUri = try {
            URI(parsedBundle.downloadUrl)
        } catch (_: URISyntaxException) {
            Logger.warning("Download URL is invalid.")
            return@processVariant
        } catch (_: IllegalArgumentException) {
            Logger.warning("Download URL is invalid.")
            return@processVariant
        }

        val cacheKey = downloadUri.toString()
        val generated = patchCache[cacheKey]?.also {
            Logger.info("Reusing cached patches for ${parsedBundle.downloadUrl}.")
        } ?: run {
            Logger.info("Downloading .rvp from ${parsedBundle.downloadUrl}...")
            val created = generatePatchList(downloadUri) ?: return@processVariant
            patchCache[cacheKey] = created
            created
        }

        if (existingContent != null && existingContent.version == parsedBundle.version && existingContent.patches == generated) {
            Logger.info("Patches are up to date.")
            return@processVariant
        }

        Logger.info("Writing to ${outputPatchesFile.name}...")
        writePatchList(outputPatchesFile, parsedBundle.version, generated)
    }
}

fun main() {
    val bundleRoot = File("..", "patch-bundles")
    bundleRoot.listFiles()
        ?.asSequence()
        ?.filter { it.isDirectory }
        ?.sortedBy { it.name }
        ?.forEach { directory ->
            Logger.info("Fetching bundle ${directory.name}")
            try {
                processBundle(directory)
            } catch (e: Exception) {
                Logger.error("Something went wrong. ${e.message}, ${e.stackTrace}")
            }
        }
}
