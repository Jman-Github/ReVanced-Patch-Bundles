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
import java.net.URLEncoder
import java.net.URL
import java.nio.charset.StandardCharsets
import java.util.Locale
import java.util.Base64
import kotlin.comparisons.compareBy

private const val BUNDLE_FILE_STEM = "-patches-bundle"
private const val PATCH_LIST_SUFFIX = "patches-list.json"

private val prioritizedReleaseTags = listOf("latest", "dev", "stable")

private val prettyJson = Json { prettyPrint = true }
private val parsingJson = Json { ignoreUnknownKeys = true }

private val patchCache = mutableMapOf<String, JsonArray>()
private val githubAuthToken = sequenceOf(
    System.getenv("GH_PAT"),
    System.getenv("GITHUB_TOKEN")
).filterNotNull().firstOrNull { it.isNotBlank() }
private const val GITHUB_API_BASE = "https://api.github.com"
private const val USER_AGENT = "revanced-patch-bundles/1.0 (+https://github.com/Jman-Github/ReVanced-Patch-Bundles)"

private data class GitHubRateLimitInfo(
    val limit: String?,
    val remaining: String?,
    val reset: String?,
    val resource: String?,
    val retryAfter: String?,
)

private fun Throwable.rootCause(): Throwable {
    var cause = this
    while (cause.cause != null && cause.cause !== cause) {
        cause = cause.cause!!
    }
    return cause
}

private fun Throwable.formatForLog(): String {
    val root = rootCause()
    val type = root::class.simpleName ?: root::class.java.name
    val message = root.message?.takeIf { it.isNotBlank() } ?: "no message"
    return "$type: $message"
}

private fun HttpURLConnection.rateLimitInfo(): GitHubRateLimitInfo = GitHubRateLimitInfo(
    limit = getHeaderField("x-ratelimit-limit"),
    remaining = getHeaderField("x-ratelimit-remaining"),
    reset = getHeaderField("x-ratelimit-reset"),
    resource = getHeaderField("x-ratelimit-resource"),
    retryAfter = getHeaderField("retry-after"),
)

private fun GitHubRateLimitInfo.formatForLog(): String {
    val parts = buildList {
        limit?.let { add("limit=$it") }
        remaining?.let { add("remaining=$it") }
        reset?.let { add("reset=$it") }
        resource?.let { add("resource=$it") }
        retryAfter?.let { add("retry-after=$it") }
    }
    return if (parts.isEmpty()) {
        "no rate-limit headers"
    } else {
        parts.joinToString(", ")
    }
}

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

private fun parseGeneratedPatchArray(jsonText: String): JsonArray? {
    return try {
        val element: JsonElement = Json.parseToJsonElement(jsonText)
        val array = element as? JsonArray
        if (array == null) {
            Logger.warning("Generated patches are not a JSON array.")
            return null
        }
        array
    } catch (_: SerializationException) {
        Logger.warning("Generated patches are not valid JSON.")
        null
    } catch (_: IllegalArgumentException) {
        Logger.warning("Generated patches are not valid JSON.")
        null
    }
}

private fun requireNonEmptyPatchArray(jsonText: String, source: String): JsonArray {
    val parsed = parseGeneratedPatchArray(jsonText)
        ?: throw IllegalStateException("$source did not produce a valid patch array.")
    if (parsed.isEmpty()) {
        throw IllegalStateException("$source produced an empty patch array.")
    }
    return parsed
}

private fun generateRevancedPatchList(downloadUri: URI): JsonArray? {
    return try {
        requireNonEmptyPatchArray(generatePatchesFromUrl(downloadUri), "Patcher 22")
    } catch (_: FileNotFoundException) {
        Logger.warning("The patch bundle file was not found.")
        null
    } catch (e: Exception) {
        Logger.warning("Failed to generate patches from ${downloadUri} with patcher 22. ${e.formatForLog()}")
        try {
            Logger.info("Retrying ${downloadUri} with legacy patcher 21.1.0-dev.5...")
            requireNonEmptyPatchArray(
                generatePatchesFromUrlWithLegacyPatcher(downloadUri),
                "Legacy patcher 21.1.0-dev.5"
            )
        } catch (legacyError: Exception) {
            Logger.warning(
                "Legacy patcher fallback also failed for ${downloadUri}. ${legacyError.formatForLog()}"
            )
            null
        }
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
        Logger.warning("Failed to parse legacy patch bundle. ${e.formatForLog()}")
        null
    } finally {
        patchesFile.delete()
    }
}

private fun generatePatchListFromReleaseAsset(downloadUri: URI, expectedVersion: String): JsonArray? {
    val location = parseReleaseLocation(downloadUri) ?: return null
    val releaseJson = fetchReleaseMetadata(location) ?: return generatePatchListFromRepositoryFile(location, expectedVersion)
    val assetUrl = findPatchMetadataAsset(releaseJson) ?: run {
        Logger.warning("No patch metadata asset found in ${location.owner}/${location.repo} release ${location.tag}.")
        return generatePatchListFromRepositoryFile(location, expectedVersion)
    }
    val payload = downloadPlainText(assetUrl) ?: return generatePatchListFromRepositoryFile(location, expectedVersion)
    val parsed = convertPatchMetadataPayload(payload) ?: return generatePatchListFromRepositoryFile(location, expectedVersion)
    return canonicalizePatchArray(parsed)
}

private fun generateMorphePatchListFromSource(downloadUri: URI, expectedVersion: String): JsonArray? {
    parseReleaseLocation(downloadUri)?.let { location ->
        return generatePatchListFromRepositoryFile(location, expectedVersion, logMissing = false)
    }

    parseGitLabReleaseLocation(downloadUri)?.let { location ->
        return generatePatchListFromGitLabRepositoryFile(location, expectedVersion)
    }

    return null
}

private fun writePatchList(outputFile: File, version: String, patches: JsonArray) {
    val payload = LocalPatchesFile(version, patches)
    outputFile.writeText(prettyJson.encodeToString(payload))
}

private fun processBundle(bundleFolder: File) {
    val bundleName = bundleFolder.name.removeSuffix("-patch-bundles")
    val variants = loadBundleVariants(bundleFolder, bundleName)

    variants.forEachGroupLogged({ "Processing file ${it.file.name}" }) processVariant@{ variant ->
        try {
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
                Logger.info("Resolving patch list for ${parsedBundle.downloadUrl}...")
                val created = when (parsedBundle.format) {
                    BundleFormat.MODERN -> {
                        if (isMorphePatchBundle(downloadUri)) {
                            generateMorphePatchListFromSource(downloadUri, parsedBundle.version)
                                ?: generateModernPatchList(downloadUri)
                        } else {
                            generateModernPatchList(downloadUri)
                        }
                    }
                    BundleFormat.LEGACY -> generateLegacyPatchList(downloadUri)
                } ?: run {
                    Logger.info("Falling back to release metadata for ${parsedBundle.downloadUrl}...")
                    generatePatchListFromReleaseAsset(downloadUri, parsedBundle.version)
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
        } catch (e: Exception) {
            Logger.error("Failed processing ${variant.file.name}. ${e.formatForLog()}")
        }
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
                Logger.error("Something went wrong while processing ${directory.name}. ${e.formatForLog()}")
            }
        }
}

private data class ReleaseLocation(
    val owner: String,
    val repo: String,
    val tag: String
)

private data class GitLabReleaseLocation(
    val projectPath: String,
    val tag: String
)

private val releaseDownloadRegex = Regex("^/([^/]+)/([^/]+)/releases/download/([^/]+)/.+$")
private val gitLabReleaseDownloadRegex = Regex("^/(.+)/-/releases/([^/]+)/downloads/.+$")

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

private fun parseGitLabReleaseLocation(uri: URI): GitLabReleaseLocation? {
    if (!uri.host.equals("gitlab.com", ignoreCase = true)) {
        return null
    }
    val match = gitLabReleaseDownloadRegex.matchEntire(uri.path) ?: return null
    val (projectPath, tag) = match.destructured
    if (projectPath.isBlank() || tag.isBlank()) {
        return null
    }
    return GitLabReleaseLocation(projectPath, tag)
}

private fun fetchReleaseMetadata(location: ReleaseLocation): JsonObject? {
    val apiUrl = "$GITHUB_API_BASE/repos/${location.owner}/${location.repo}/releases/tags/${location.tag}"
    val attemptAuthFirst = !githubAuthToken.isNullOrBlank()
    val attempts = if (attemptAuthFirst) listOf(true, false) else listOf(false)

    for (useAuth in attempts) {
        val connection = (URL(apiUrl).openConnection() as HttpURLConnection)
        try {
            connection.requestMethod = "GET"
            connection.setRequestProperty("Accept", "application/vnd.github+json")
            connection.setRequestProperty("User-Agent", USER_AGENT)
            if (useAuth) {
                connection.setRequestProperty("Authorization", "Bearer $githubAuthToken")
            }
            val code = connection.responseCode
            val rateLimitInfo = connection.rateLimitInfo()
            if (code == HttpURLConnection.HTTP_OK) {
                val body = connection.inputStream.bufferedReader().use { it.readText() }
                if (useAuth) {
                    Logger.info(
                        "GitHub API rate limit for ${location.owner}/${location.repo}: ${rateLimitInfo.formatForLog()}"
                    )
                }
                return Json.parseToJsonElement(body).jsonObject
            }
            if (code == HttpURLConnection.HTTP_UNAUTHORIZED && useAuth) {
                Logger.warning(
                    "GitHub token was rejected for ${location.owner}/${location.repo}; " +
                        "retrying release metadata anonymously. ${rateLimitInfo.formatForLog()}"
                )
                continue
            }
            Logger.warning(
                "Failed to fetch release metadata for ${location.owner}/${location.repo} ($code). " +
                    rateLimitInfo.formatForLog()
            )
            return null
        } catch (e: Exception) {
            if (useAuth) {
                Logger.warning("Authenticated release metadata fetch failed. ${e.message}")
                continue
            }
            Logger.warning("Failed to fetch release metadata. ${e.message}")
            return null
        } finally {
            connection.disconnect()
        }
    }

    return null
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

private fun generatePatchListFromRepositoryFile(
    location: ReleaseLocation,
    expectedVersion: String,
    logMissing: Boolean = true,
): JsonArray? {
    val attempts = listOf(location.tag, null)

    for (ref in attempts) {
        val payload = downloadRepositoryFile(location, "patches-list.json", ref) ?: continue
        val sourceLabel = ref?.let { "ref $it" } ?: "default branch"
        val parsed = parseRepositoryPatchListPayload(payload, expectedVersion)
        if (parsed == null) {
            Logger.warning(
                "Repository patches-list.json from ${location.owner}/${location.repo} ($sourceLabel) " +
                    "is not usable for version $expectedVersion."
            )
            continue
        }
        Logger.info("Using repository patches-list.json from ${location.owner}/${location.repo} ($sourceLabel).")
        return canonicalizePatchArray(parsed)
    }

    if (logMissing) {
        Logger.warning(
            "No usable repository patches-list.json found for ${location.owner}/${location.repo} " +
                "release ${location.tag}."
        )
    }
    return null
}

private fun generatePatchListFromGitLabRepositoryFile(
    location: GitLabReleaseLocation,
    expectedVersion: String,
): JsonArray? {
    val attempts = listOf(location.tag, "main", "master")

    for (ref in attempts) {
        val payload = downloadGitLabRepositoryFile(location, "patches-list.json", ref) ?: continue
        val parsed = parseRepositoryPatchListPayload(payload, expectedVersion)
        if (parsed == null) {
            Logger.warning(
                "Repository patches-list.json from ${location.projectPath} (ref $ref) " +
                    "is not usable for version $expectedVersion."
            )
            continue
        }
        Logger.info(
            "Using repository patches-list.json from ${location.projectPath} (ref $ref)."
        )
        return canonicalizePatchArray(parsed)
    }

    return null
}

private fun parseRepositoryPatchListPayload(payload: String, expectedVersion: String): JsonArray? {
    val parsed = try {
        parsingJson.decodeFromString<LocalPatchesFile>(payload)
    } catch (e: SerializationException) {
        Logger.warning("Repository patches-list.json is not valid JSON. ${e.message}")
        return null
    } catch (e: IllegalArgumentException) {
        Logger.warning("Repository patches-list.json is not valid JSON. ${e.message}")
        return null
    }

    if (!versionsMatch(parsed.version, expectedVersion)) {
        Logger.warning(
            "Repository patches-list.json version ${parsed.version} does not match expected $expectedVersion."
        )
        return null
    }

    return parsed.patches
}

private fun versionsMatch(left: String, right: String): Boolean =
    normalizeVersionForComparison(left) == normalizeVersionForComparison(right)

private fun normalizeVersionForComparison(value: String): String =
    value.trim().removePrefix("v").removePrefix("V").lowercase(Locale.ROOT)

private fun downloadRepositoryFile(location: ReleaseLocation, path: String, ref: String?): String? {
    val encodedPath = path.split('/').joinToString("/") {
        URLEncoder.encode(it, StandardCharsets.UTF_8).replace("+", "%20")
    }
    val refQuery = ref?.let {
        "?ref=" + URLEncoder.encode(it, StandardCharsets.UTF_8).replace("+", "%20")
    }.orEmpty()
    val apiUrl = "$GITHUB_API_BASE/repos/${location.owner}/${location.repo}/contents/$encodedPath$refQuery"
    val attemptAuthFirst = !githubAuthToken.isNullOrBlank()
    val attempts = if (attemptAuthFirst) listOf(true, false) else listOf(false)

    for (useAuth in attempts) {
        val connection = (URL(apiUrl).openConnection() as HttpURLConnection)
        try {
            connection.requestMethod = "GET"
            connection.setRequestProperty("Accept", "application/vnd.github+json")
            connection.setRequestProperty("User-Agent", USER_AGENT)
            if (useAuth) {
                connection.setRequestProperty("Authorization", "Bearer $githubAuthToken")
            }

            val code = connection.responseCode
            val rateLimitInfo = connection.rateLimitInfo()
            when (code) {
                HttpURLConnection.HTTP_OK -> {
                    val body = connection.inputStream.bufferedReader().use { it.readText() }
                    val response = Json.parseToJsonElement(body).jsonObject
                    val downloadUrl = response["download_url"]?.jsonPrimitive?.contentOrNull
                    if (!downloadUrl.isNullOrBlank()) {
                        return downloadPlainText(downloadUrl)
                    }

                    val content = response["content"]?.jsonPrimitive?.contentOrNull
                    val encoding = response["encoding"]?.jsonPrimitive?.contentOrNull
                    if (!content.isNullOrBlank() && encoding.equals("base64", ignoreCase = true)) {
                        val normalized = content.replace("\n", "").replace("\r", "")
                        return String(Base64.getDecoder().decode(normalized), StandardCharsets.UTF_8)
                    }

                    Logger.warning(
                        "Repository file response for ${location.owner}/${location.repo} did not include usable content."
                    )
                    return null
                }

                HttpURLConnection.HTTP_NOT_FOUND -> continue

                HttpURLConnection.HTTP_UNAUTHORIZED -> {
                    if (useAuth) {
                        Logger.warning(
                            "GitHub token was rejected for ${location.owner}/${location.repo}; " +
                                "retrying repository file fetch anonymously. ${rateLimitInfo.formatForLog()}"
                        )
                        continue
                    }
                    return null
                }

                else -> {
                    Logger.warning(
                        "Failed to fetch repository file for ${location.owner}/${location.repo} ($code). " +
                            rateLimitInfo.formatForLog()
                    )
                    return null
                }
            }
        } catch (e: Exception) {
            if (useAuth) {
                Logger.warning("Authenticated repository file fetch failed. ${e.message}")
                continue
            }
            Logger.warning("Failed to fetch repository file. ${e.message}")
            return null
        } finally {
            connection.disconnect()
        }
    }

    return null
}

private fun downloadGitLabRepositoryFile(
    location: GitLabReleaseLocation,
    path: String,
    ref: String,
): String? {
    val encodedPath = path.split('/').joinToString("/") {
        URLEncoder.encode(it, StandardCharsets.UTF_8).replace("+", "%20")
    }
    val encodedRef = URLEncoder.encode(ref, StandardCharsets.UTF_8).replace("+", "%20")
    val url = "https://gitlab.com/${location.projectPath}/-/raw/$encodedRef/$encodedPath"
    return downloadPlainText(url)
}

private fun downloadPlainText(url: String): String? {
    val connection = (URL(url).openConnection() as HttpURLConnection)
    return try {
        connection.requestMethod = "GET"
        connection.setRequestProperty("User-Agent", USER_AGENT)
        val code = connection.responseCode
        if (code in 200..299) {
            connection.inputStream.bufferedReader().use { it.readText() }
        } else {
            Logger.warning("Failed to download $url ($code). ${connection.rateLimitInfo().formatForLog()}")
            null
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
                else -> put(key, value)
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
