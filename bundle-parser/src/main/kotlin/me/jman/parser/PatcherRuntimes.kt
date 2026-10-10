package me.jman.parser

import kotlinx.serialization.Serializable
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import java.io.File
import java.net.URI
import java.security.MessageDigest
import java.util.concurrent.TimeUnit
import java.util.jar.JarFile

@Serializable
internal data class WorkerSettings(
    val timeout_seconds: Long = 90, val max_heap: String = "512m", val restart_attempts: Int = 1
)
@Serializable
internal data class RuntimeDefinition(
    val id: String, val family: String, val loader: String, val coordinate: String,
    val dependencies: List<String>, val range: String? = null, val fallback: Boolean = false
)
@Serializable
internal data class RuntimeConfiguration(
    val worker: WorkerSettings, val runtimes: List<RuntimeDefinition>
)
@Serializable
internal data class InstalledRuntime(val classpath: String = "", val available: Boolean = false)
@Serializable
internal data class ExtractionRecord(
    val version: String, val download_url: String, val status: String,
    val file_hash: String? = null, val runtime: String? = null,
    val patch_list_hash: String? = null,
    val attempted_at: String? = null, val failure_fingerprint: String? = null,
    val provider_digest: String? = null,
    val terminal: Boolean = false, val bundle_type: String? = null,
    val runtime_config_hash: String? = null
)
internal data class RuntimeResult(val patches: JsonArray?, val status: String,
                                  val hash: String? = null, val runtime: String? = null,
                                  val terminal: Boolean = false, val paused: Boolean = false)

private val runtimeJson = Json { ignoreUnknownKeys = true; prettyPrint = true }
private val runtimeResults = mutableMapOf<String, RuntimeResult>()

/** A deliberately bounded range language: whitespace-separated semver comparators. */
internal data class PatcherVersion(val numbers: List<Int>, val prerelease: List<String>) :
    Comparable<PatcherVersion> {
    override fun compareTo(other: PatcherVersion): Int {
        numbers.zip(other.numbers).forEach { (left, right) ->
            if (left != right) return left.compareTo(right)
        }
        if (prerelease.isEmpty() || other.prerelease.isEmpty()) {
            return when {
                prerelease.isEmpty() && other.prerelease.isEmpty() -> 0
                prerelease.isEmpty() -> 1
                else -> -1
            }
        }
        prerelease.zip(other.prerelease).forEach { (left, right) ->
            if (left != right) {
                val l = left.toIntOrNull()
                val r = right.toIntOrNull()
                return when {
                    l != null && r != null -> l.compareTo(r)
                    l != null -> -1
                    r != null -> 1
                    else -> left.compareTo(right)
                }
            }
        }
        return prerelease.size.compareTo(other.prerelease.size)
    }
    companion object {
        fun parse(value: String): PatcherVersion {
            val match = Regex("^(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)\\.(0|[1-9][0-9]*)(?:-([0-9A-Za-z.-]+))?(?:\\+[0-9A-Za-z.-]+)?$")
                .matchEntire(value) ?: error("Invalid patcher semantic version")
            val pre = match.groupValues[4].takeIf(String::isNotEmpty)?.split('.') ?: emptyList()
            require(pre.all { it.isNotEmpty() && !(it.all(Char::isDigit) && it.length > 1 && it[0] == '0') })
            return PatcherVersion((1..3).map { match.groupValues[it].toInt() }, pre)
        }
    }
}
internal fun matchesPatcherRange(range: String, version: String): Boolean {
    if (range == "*") return true
    val current = PatcherVersion.parse(version)
    require(range.isNotBlank())
    return range.trim().split(Regex("\\s+")).all { term ->
        val match = Regex("^(>=|<=|>|<|=)?(.+)$").matchEntire(term) ?: error("Invalid range")
        val compared = current.compareTo(PatcherVersion.parse(match.groupValues[2]))
        when (match.groupValues[1]) {
            ">" -> compared > 0
            ">=" -> compared >= 0
            "<" -> compared < 0
            "<=" -> compared <= 0
            "", "=" -> compared == 0
            else -> error("Invalid range comparator")
        }
    }
}

internal fun selectRuntimes(config: RuntimeConfiguration, family: String, declared: String?):
    List<RuntimeDefinition> {
    require(config.runtimes.map { it.id }.distinct().size == config.runtimes.size)
    require(config.worker.timeout_seconds in 1..600)
    require(config.worker.restart_attempts in 0..3)
    require(Regex("^[1-9][0-9]*[mMgG]$").matches(config.worker.max_heap))
    require(config.runtimes.all { it.loader in setOf("revanced-modern", "revanced-legacy",
                                                   "morphe", "revanced-v3", "legacy-bytecode") })
    // Only Morphe declares a version that selects a runtime range. ReVanced
    // bundles use the ordered fallback chain, including older V3 APIs.
    val ranged = family == "Morphe:V1" && declared != null
    val candidates = config.runtimes.filter { it.family == family }.filter {
        if (ranged) it.range?.let { range -> matchesPatcherRange(range, declared) } == true else it.fallback
    }
    require(!ranged || candidates.size <= 1) { "Overlapping runtime compatibility ranges" }
    return candidates
}

private fun loadRuntimeConfiguration(): RuntimeConfiguration {
    val path = System.getProperty("catalog.runtime.config")
        ?: File("..", "config/patcher-runtimes.json").absolutePath
    return runtimeJson.decodeFromString(File(path).readText())
}
private fun installedRuntimes(): Map<String, InstalledRuntime> {
    val path = System.getProperty("catalog.runtime.manifest")
        ?: File("build", "runtime-classpaths.json").absolutePath
    return runtimeJson.decodeFromString(File(path).readText())
}
internal fun sha256(file: File): String {
    val hash = MessageDigest.getInstance("SHA-256")
    file.inputStream().use { input ->
        val buffer = ByteArray(65536)
        while (true) {
            val count = input.read(buffer)
            if (count < 0) break
            hash.update(buffer, 0, count)
        }
    }
    return hash.digest().joinToString("") { "%02x".format(it) }
}

/** Independently implements upstream worker restart/deadline behavior.
 * Reference: https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/workers/PatchWorkerClient.kt
 */
private fun extractWithRuntime(
    artifact: File, hash: String, runtime: RuntimeDefinition,
    installation: InstalledRuntime, settings: WorkerSettings
): RuntimeResult {
    val deadline = System.nanoTime() + TimeUnit.SECONDS.toNanos(settings.timeout_seconds)
    var failure = "runtime_initialization_failure"
    for (attempt in 0..settings.restart_attempts) {
        if (System.nanoTime() >= deadline) return RuntimeResult(null, "runtime_timeout", hash)
        val output = File.createTempFile("catalog-result", ".json")
        val log = File.createTempFile("catalog-worker", ".log")
        var process: Process? = null
        try {
            val java = File(System.getProperty("java.home"), "bin/java").absolutePath
            // Some patchers use the system loader as parent; isolate one runtime per JVM.
            process = ProcessBuilder(
                java, "-Xmx${settings.max_heap}",
                "-Drevanced.patcher22.classpath=${installation.classpath}",
                "-Drevanced.patcher21.classpath=${installation.classpath}",
                "-Dmorphe.patcher.classpath=${installation.classpath}",
                "-cp", listOf(System.getProperty("java.class.path"), installation.classpath)
                    .filter(String::isNotBlank).joinToString(File.pathSeparator),
                "me.jman.parser.MainKt", "--runtime-worker", runtime.loader,
                artifact.absolutePath, output.absolutePath
            ).redirectErrorStream(true).redirectOutput(log).start()
            val remaining = deadline - System.nanoTime()
            if (remaining <= 0 || !process.waitFor(remaining, TimeUnit.NANOSECONDS))
                return RuntimeResult(null, "runtime_timeout", hash)
            when (process.exitValue()) {
                // Explicit responses mean the worker ran and rejected this bundle.
                2 -> return RuntimeResult(null, "runtime_parsing_failure", hash, terminal = true)
                3 -> return RuntimeResult(null, "invalid_patch_metadata", hash, terminal = true)
                0 -> {
                    val patches = runtimeJson.decodeFromString<JsonArray>(output.readText())
                    if (!isUsablePatchArray(patches))
                        return RuntimeResult(null, "invalid_patch_metadata", hash, terminal = true)
                    return RuntimeResult(patches, "verified", hash, runtime.coordinate)
                }
                else -> failure = "runtime_initialization_failure"
            }
        } catch (_: InterruptedException) {
            Thread.currentThread().interrupt()
            return RuntimeResult(null, "runtime_initialization_failure", hash)
        } catch (_: Exception) {
            // Startup/transport failures can recover in a fresh JVM within the same deadline.
            failure = "runtime_initialization_failure"
        } finally {
            if (process?.isAlive == true) {
                process.destroyForcibly()
                try { process.waitFor(5, TimeUnit.SECONDS) }
                catch (_: InterruptedException) { Thread.currentThread().interrupt() }
            }
            output.delete()
            log.delete()
        }
    }
    return RuntimeResult(null, failure, hash)
}

internal fun extractWithRuntimes(
    uri: URI, legacy: Boolean, familyHint: String? = null, previous: ExtractionRecord? = null
): RuntimeResult {
    val family = when {
        legacy -> "ReVanced:V3"
        familyHint in setOf("Morphe:V1", "ReVanced:V4") -> familyHint!!
        uri.path.lowercase().endsWith(".mpp") -> "Morphe:V1"
        uri.path.lowercase().endsWith(".rvp") -> "ReVanced:V4"
        else -> return RuntimeResult(null, "unsupported_format")
    }
    val cacheKey = "$family:$uri"
    runtimeResults[cacheKey]?.let { return it }
    val artifact = File.createTempFile("catalog-bundle", ".jar")
    return try {
        try {
            downloadToFile(uri.toURL(), artifact)
        } catch (_: Exception) {
            return RuntimeResult(null, "artifact_unavailable")
        }
        val hash = sha256(artifact)
        // Download current releases to notice replacements even at an unchanged URL,
        // but do not run workers again for an unchanged, permanently rejected binary.
        if (previous?.terminal == true && previous.file_hash == hash &&
            previous.bundle_type == family && previous.failure_fingerprint == runtimeFingerprint()) {
            return RuntimeResult(null, previous.status, hash, terminal = true, paused = true)
        }
        val declared = try {
            JarFile(artifact).use { it.manifest?.mainAttributes?.getValue("Patcher-Version") }
                ?.trim()?.takeIf(String::isNotEmpty)
        } catch (_: Exception) {
            return RuntimeResult(null, "runtime_parsing_failure", hash, terminal = true)
        }
        val config = loadRuntimeConfiguration()
        val candidates = try {
            selectRuntimes(config, family, declared)
        } catch (_: Exception) {
            return RuntimeResult(null, "runtime_configuration_failure", hash, terminal = true)
        }
        if (candidates.isEmpty()) return RuntimeResult(null, "missing_compatible_runtime", hash, terminal = true)
        val installed = installedRuntimes()
        var failure = "runtime_initialization_failure"
        var allRejected = true
        for (runtime in candidates) {
            val installation = installed[runtime.id]
            if (installation?.available != true) {
                allRejected = false
                continue
            }
            val result = extractWithRuntime(artifact, hash, runtime, installation, config.worker)
            if (result.status == "verified") return result.also { runtimeResults[cacheKey] = it }
            if (Thread.currentThread().isInterrupted) return result
            allRejected = allRejected && result.terminal
            failure = result.status
        }
        RuntimeResult(null, failure, hash, terminal = allRejected)
    } catch (_: Exception) {
        RuntimeResult(null, "runtime_initialization_failure")
    } finally {
        artifact.delete()
    }
}

internal fun recordExtraction(
    output: File, list: File, version: String, uri: URI, result: RuntimeResult,
    providerDigest: String? = null, family: String? = null
) {
    val record = ExtractionRecord(version, uri.toString(), result.status, result.hash,
                                  result.runtime, if (result.status == "verified") sha256(list) else null,
                                  java.time.Instant.now().toString(),
                                  if (result.status == "verified") null else runtimeFingerprint(), providerDigest,
                                  result.terminal, family, runtimeConfigHash())
    atomicWriteText(output, runtimeJson.encodeToString(record) + "\n")
}

internal fun runtimeWorker(args: Array<String>) {
    val uri = File(args[2]).toURI()
    val patches = try {
        when (args[1]) {
            "legacy-bytecode" -> parseLegacyPatchBundle(File(args[2]))
            "revanced-v3" -> generateV3PatchList(File(args[2]))
            "revanced-modern" -> runtimeJson.decodeFromString<JsonArray>(generatePatchesFromUrl(uri))
            "revanced-legacy" -> runtimeJson.decodeFromString<JsonArray>(generatePatchesFromUrlWithLegacyPatcher(uri))
            "morphe" -> generateMorphePatchList(uri) ?: error("Morphe runtime rejected bundle")
            else -> error("Unsupported worker loader")
        }
    } catch (error: Exception) {
        System.err.println("Patcher rejected bundle: " + error.javaClass.simpleName)
        kotlin.system.exitProcess(2)
    }
    if (!isUsablePatchArray(patches)) kotlin.system.exitProcess(3)
    File(args[3]).writeText(patches.toString())
}

/** Provider SHA-256 hashes invalidate proof when an artifact changes at its URL. */
internal fun matchesProviderDigest(expected: String?, actual: String?, recorded: String? = null): Boolean {
    val normalized = expected?.trim()?.lowercase() ?: return true
    if (normalized.isEmpty()) return true
    val value = normalized.removePrefix("sha256:")
    if (!Regex("[a-f0-9]{64}").matches(value)) return expected == recorded
    return value == actual?.lowercase()
}
