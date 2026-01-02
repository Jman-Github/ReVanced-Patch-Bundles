package me.jman.parser

import kotlinx.serialization.SerializationException
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlinx.serialization.json.booleanOrNull
import java.io.File
import java.io.FileNotFoundException
import java.net.URI
import java.net.HttpURLConnection
import java.net.URISyntaxException
import java.net.URL
import java.util.Locale
import kotlin.comparisons.compareBy

private const val BUNDLE_FILE_STEM = "-patches-bundle"
private const val PATCH_LIST_SUFFIX = "patches-list.json"

private val prioritizedReleaseTags = listOf("latest", "dev", "stable")

private val prettyJson = Json { prettyPrint = true }
private val parsingJson = Json { ignoreUnknownKeys = true }

private val patchCache = mutableMapOf<String, JsonArray>()
private val githubAuthToken = System.getenv("GH_PAT")?.takeIf { it.isNotBlank() }
private const val GITHUB_API_BASE = "https://api.github.com"
private const val USER_AGENT = "revanced-patch-bundles/1.0 (+https://github.com/Jman-Github/ReVanced-Patch-Bundles)"

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

private enum class BundleFormat {
    MODERN,
    LEGACY
}

private data class ParsedBundle(
    val version: String,
    val downloadUrl: String,
    val format: BundleFormat
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
    parsedModern?.takeIf { modern ->
        listOf(
            modern.version,
            modern.downloadUrl,
            modern.signatureDownloadUrl,
            modern.createdAt,
            modern.description
        ).any { !it.isNullOrBlank() }
    }?.let { modern ->
        val version = normalizeMetadataValue(modern.version)
        if (version == null) {
            Logger.warning("Version is invalid.")
            return null
        }
        val downloadUrl = normalizeMetadataValue(modern.downloadUrl)
        if (downloadUrl == null) {
            Logger.warning("Download URL is invalid.")
            return null
        }
        return ParsedBundle(version, downloadUrl, BundleFormat.MODERN)
    }

    val parsedLegacy = try {
        parsingJson.decodeFromString<LegacyBundleFile>(content)
    } catch (_: SerializationException) {
        null
    }
    parsedLegacy?.takeIf { legacy ->
        legacy.patches != null || legacy.integrations != null
    }?.let { legacy ->
        val patches = legacy.patches
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
        return ParsedBundle(version, downloadUrl, BundleFormat.LEGACY)
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

private fun generateModernPatchList(downloadUri: URI): JsonArray? {
    val patches = if (isMorphePatchBundle(downloadUri)) {
        generateMorphePatchList(downloadUri)
    } else {
        generateRevancedPatchList(downloadUri)
    } ?: return null
    return canonicalizePatchArray(patches)
}

private fun isMorphePatchBundle(downloadUri: URI): Boolean {
    return downloadUri.path.lowercase(Locale.ROOT).endsWith(".mpp")
}

private fun generateRevancedPatchList(downloadUri: URI): JsonArray? {
    return try {
        val jsonText = generatePatchesFromUrl(downloadUri)
        val element: JsonElement = Json.parseToJsonElement(jsonText)
        val array = element as? JsonArray
        if (array == null) {
            Logger.warning("Generated patches are not a JSON array.")
            return null
        }
        array
    } catch (_: FileNotFoundException) {
        Logger.warning("The patch bundle file was not found.")
        null
    } catch (_: SerializationException) {
        Logger.warning("Generated patches are not valid JSON.")
        null
    } catch (_: IllegalArgumentException) {
        Logger.warning("Generated patches are not valid JSON.")
        null
    }
}

private fun generateLegacyPatchList(downloadUri: URI): JsonArray? {
    val patchesFile = File.createTempFile("legacy-patches", ".jar")
    return try {
        downloadToFile(downloadUri.toURL(), patchesFile)
        val parsed = parseLegacyPatchBundle(patchesFile)
        if (parsed.isEmpty()) {
            Logger.warning("No patches were found in the legacy patch bundle.")
            null
        } else {
            canonicalizePatchArray(parsed)
        }
    } catch (_: FileNotFoundException) {
        Logger.warning("The patch bundle file was not found.")
        null
    } catch (e: SerializationException) {
        Logger.warning("Generated patches are not valid JSON. ${e.message}")
        null
    } catch (e: IllegalArgumentException) {
        Logger.warning("Generated patches are not valid JSON. ${e.message}")
        null
    } catch (e: Exception) {
        Logger.warning("Failed to parse legacy patch bundle. ${e.message}")
        null
    } finally {
        patchesFile.delete()
    }
}

private fun generatePatchListFromReleaseAsset(downloadUri: URI): JsonArray? {
    val location = parseReleaseLocation(downloadUri) ?: return null
    val releaseJson = fetchReleaseMetadata(location) ?: return null
    val assetUrl = findPatchMetadataAsset(releaseJson) ?: run {
        Logger.warning("No patch metadata asset found in ${location.owner}/${location.repo} release ${location.tag}.")
        return null
    }
    val payload = downloadPlainText(assetUrl) ?: return null
    val parsed = convertPatchMetadataPayload(payload) ?: return null
    return canonicalizePatchArray(parsed)
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
            Logger.info("Downloading patch bundle from ${parsedBundle.downloadUrl}...")
            val created = when (parsedBundle.format) {
                BundleFormat.MODERN -> generateModernPatchList(downloadUri)
                BundleFormat.LEGACY -> generateLegacyPatchList(downloadUri)
            } ?: if (parsedBundle.format == BundleFormat.LEGACY) {
                Logger.info("Falling back to release metadata for ${parsedBundle.downloadUrl}...")
                generatePatchListFromReleaseAsset(downloadUri)
            } else {
                null
            } ?: return@processVariant
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

private data class ReleaseLocation(
    val owner: String,
    val repo: String,
    val tag: String
)

private val releaseDownloadRegex = Regex("^/([^/]+)/([^/]+)/releases/download/([^/]+)/.+$")

private fun parseReleaseLocation(uri: URI): ReleaseLocation? {
    if (!uri.host.equals("github.com", ignoreCase = true)) {
        return null
    }
    val match = releaseDownloadRegex.matchEntire(uri.path) ?: return null
    val (owner, repo, tag) = match.destructured
    if (owner.isBlank() || repo.isBlank() || tag.isBlank()) {
        return null
    }
    return ReleaseLocation(owner, repo, tag)
}

private fun fetchReleaseMetadata(location: ReleaseLocation): JsonObject? {
    val apiUrl = "$GITHUB_API_BASE/repos/${location.owner}/${location.repo}/releases/tags/${location.tag}"
    val connection = (URL(apiUrl).openConnection() as HttpURLConnection)
    return try {
        connection.requestMethod = "GET"
        connection.setRequestProperty("Accept", "application/vnd.github+json")
        connection.setRequestProperty("User-Agent", USER_AGENT)
        githubAuthToken?.let { connection.setRequestProperty("Authorization", "Bearer $it") }
        val code = connection.responseCode
        if (code != HttpURLConnection.HTTP_OK) {
            Logger.warning("Failed to fetch release metadata for ${location.owner}/${location.repo} ($code).")
            null
        } else {
            val body = connection.inputStream.bufferedReader().use { it.readText() }
            Json.parseToJsonElement(body).jsonObject
        }
    } catch (e: Exception) {
        Logger.warning("Failed to fetch release metadata. ${e.message}")
        null
    } finally {
        connection.disconnect()
    }
}

private fun findPatchMetadataAsset(releaseJson: JsonObject): String? {
    val assets = releaseJson["assets"]?.jsonArray ?: return null
    val candidates = assets.mapNotNull { it as? JsonObject }
    fun JsonObject.downloadUrl(): String? = this["browser_download_url"]?.jsonPrimitive?.contentOrNull
    fun JsonObject.assetName(): String = this["name"]?.jsonPrimitive?.contentOrNull.orEmpty()

    val prioritized = candidates.firstOrNull { it.assetName().equals("patches.json", ignoreCase = true) }
        ?: candidates.firstOrNull {
            val lower = it.assetName().lowercase(Locale.ROOT)
            lower.endsWith("patches.json") || (lower.contains("patch") && lower.endsWith(".json"))
        }
    return prioritized?.downloadUrl()
}

private fun downloadPlainText(url: String): String? {
    val connection = (URL(url).openConnection() as HttpURLConnection)
    return try {
        connection.requestMethod = "GET"
        connection.setRequestProperty("User-Agent", USER_AGENT)
        val code = connection.responseCode
        if (code !in 200..299) {
            Logger.warning("Failed to download $url ($code).")
            null
        } else {
            connection.inputStream.bufferedReader().use { it.readText() }
        }
    } catch (e: Exception) {
        Logger.warning("Failed to download $url. ${e.message}")
        null
    } finally {
        connection.disconnect()
    }
}

private fun convertPatchMetadataPayload(payload: String): JsonArray? {
    val element = try {
        Json.parseToJsonElement(payload)
    } catch (e: SerializationException) {
        Logger.warning("Patch metadata is not valid JSON. ${e.message}")
        return null
    } catch (e: IllegalArgumentException) {
        Logger.warning("Patch metadata is not valid JSON. ${e.message}")
        return null
    }
    val patches = when (element) {
        is JsonArray -> element
        is JsonObject -> element["patches"]?.jsonArray
        else -> null
    } ?: return null
    val converted = patches.mapNotNull { convertExternalPatchObject(it) }
    return JsonArray(converted)
}

private fun convertExternalPatchObject(element: JsonElement): JsonObject? {
    val obj = element as? JsonObject ?: return null
    val compatObject = convertCompatibilityArray(obj["compatiblePackages"] as? JsonArray)
    val dependencies = (obj["dependencies"] as? JsonArray) ?: JsonArray(emptyList())
    val options = (obj["options"] as? JsonArray) ?: JsonArray(emptyList())
    val hasUseField = "use" in obj
    return buildJsonObject {
        for ((key, value) in obj) {
            when (key) {
                "compatiblePackages" -> put(key, compatObject)
                "dependencies" -> put(key, dependencies)
                "options" -> put(key, options)
                else -> put(key, value ?: JsonNull)
            }
        }
        if ("compatiblePackages" !in obj) {
            put("compatiblePackages", compatObject)
        }
        if ("dependencies" !in obj) {
            put("dependencies", dependencies)
        }
        if ("options" !in obj) {
            put("options", options)
        }
        if (!hasUseField) {
            val excluded = obj["excluded"]?.jsonPrimitive?.booleanOrNull ?: false
            put("use", JsonPrimitive(!excluded))
        }
    }
}

private fun convertCompatibilityArray(array: JsonArray?): JsonObject {
    if (array == null) {
        return JsonObject(emptyMap())
    }
    val mapped = array.mapNotNull { entry ->
        val compatObj = entry as? JsonObject ?: return@mapNotNull null
        val packageName = compatObj["name"]?.jsonPrimitive?.contentOrNull ?: return@mapNotNull null
        val versionsElement = compatObj["versions"]
        val versions = when (versionsElement) {
            is JsonArray -> versionsElement.mapNotNull { it.jsonPrimitive.contentOrNull }
            is JsonPrimitive -> versionsElement.contentOrNull?.let { listOf(it) } ?: emptyList()
            else -> emptyList()
        }
        packageName to JsonArray(versions.map(::JsonPrimitive))
    }
    return JsonObject(mapped.toMap())
}
