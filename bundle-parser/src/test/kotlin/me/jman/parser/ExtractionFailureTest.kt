package me.jman.parser

import java.io.File
import java.net.URI
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.jsonArray
import kotlin.io.path.createTempDirectory
import kotlin.test.Test
import kotlin.test.assertContentEquals
import kotlin.test.assertEquals
import kotlin.test.assertNull

class ExtractionFailureTest {
    @Test
    fun `historical legacy bundle metadata reaches the legacy extractor`() {
        val root = createTempDirectory("historical-legacy-").toFile()
        val folder = File(root, "demo-patch-bundles").apply { mkdir() }
        val patches = Json.parseToJsonElement("""[{"name":"Historical patch"}]""").jsonArray
        var calls = 0
        try {
            File(folder, "demo-stable-patches-bundle.json").writeText(
                """{"version":"v1","created_at":"2026-01-01T00:00:00Z","description":"Old release",
                   "patches":{"version":"v1","url":"https://example.test/patches.jar"}}"""
            )
            processBundle(folder, extract = { uri, legacy ->
                assertEquals(URI("https://example.test/patches.jar"), uri)
                assertEquals(true, legacy)
                calls++
                RuntimeResult(patches, "verified", "a".repeat(64), "builtin:annotation-reader:1")
            }, fallback = { _, _ -> error("Binary extraction should succeed") })
            assertEquals(1, calls)
            val output = File(folder, "demo-stable-patches-list.json")
            assertEquals(patches, Json.decodeFromString<LocalPatchesFile>(output.readText()).patches)
            val record = Json.decodeFromString<ExtractionRecord>(
                File(folder, "demo-stable-extraction.json").readText())
            assertEquals("verified", record.status)
        } finally {
            folder.listFiles()?.forEach { it.delete() }
            folder.delete()
            root.delete()
        }
    }

    @Test
    fun `opaque asset URL keeps its declared bundle family through extraction`() {
        val root = createTempDirectory("opaque-bundle-").toFile()
        val folder = File(root, "demo-patch-bundles").apply { mkdir() }
        val configProperty = "catalog.runtime.config"
        val manifestProperty = "catalog.runtime.manifest"
        val oldConfig = System.getProperty(configProperty)
        val oldManifest = System.getProperty(manifestProperty)
        try {
            val artifact = File(root, "123")
            val manifest = java.util.jar.Manifest().apply {
                mainAttributes.putValue("Manifest-Version", "1.0")
                mainAttributes.putValue("Patcher-Version", "1.9.0")
            }
            java.util.jar.JarOutputStream(artifact.outputStream(), manifest).use { }
            val config = File(root, "runtimes.json").apply {
                writeText("""{"worker":{},"runtimes":[{"id":"morphe","family":"Morphe:V1",
                    "loader":"morphe","coordinate":"test:morphe:1","dependencies":[],
                    "range":">=1.0.0 <2.0.0"}]}""")
            }
            val installed = File(root, "installed.json").apply { writeText("{}") }
            System.setProperty(configProperty, config.absolutePath)
            System.setProperty(manifestProperty, installed.absolutePath)
            File(folder, "demo-latest-patches-bundle.json").writeText(
                """{"version":"v1","download_url":"${artifact.toURI()}","bundle_type":"Morphe:V1"}"""
            )
            processBundle(folder, fallback = { _, _ -> null })
            val record = Json.decodeFromString<ExtractionRecord>(
                File(folder, "demo-latest-extraction.json").readText())
            // The matching runtime is deliberately absent. Reaching this status
            // proves the default extractor downloaded and selected the Morphe family.
            assertEquals("runtime_initialization_failure", record.status)
            assertEquals(sha256(artifact), record.file_hash)
            assertEquals("unsupported_format", extractWithRuntimes(artifact.toURI(), false).status)
            assertEquals("missing_compatible_runtime",
                extractWithRuntimes(artifact.toURI(), false, "ReVanced:V4").status)
        } finally {
            if (oldConfig == null) System.clearProperty(configProperty)
            else System.setProperty(configProperty, oldConfig)
            if (oldManifest == null) System.clearProperty(manifestProperty)
            else System.setProperty(manifestProperty, oldManifest)
            folder.listFiles()?.forEach { it.delete() }
            folder.delete()
            root.listFiles()?.forEach { it.delete() }
            root.delete()
        }
    }

    @Test
    fun `invalid fallback revokes previous artifact proof`() = checkFailedFallback(fallback = { _, _ ->
        Json.parseToJsonElement("""["broken"]""").jsonArray
    })

    @Test
    fun `throwing fallback revokes previous artifact proof`() = checkFailedFallback(fallback = { _, _ ->
        error("Fallback metadata is malformed")
    })

    @Test
    fun `cleanup failure revokes previous artifact proof`() {
        val malformed = Json.parseToJsonElement(
            """[{"name":"Patch","compatiblePackages":[{"name":{}}]}]"""
        ).jsonArray
        checkFailedFallback(
            fallback = { _, _ -> error("Fallback must not run for extracted patches") },
            extraction = RuntimeResult(malformed, "verified", "a".repeat(64), "test:runtime:1"),
            expectedStatus = "metadata_processing_failure"
        )
    }

    @Test
    fun `successful extraction replaces pending artifact proof`() {
        val patches = Json.parseToJsonElement("""[{"name":"New patch"}]""").jsonArray
        checkFailedFallback(
            fallback = { _, _ -> error("Fallback must not run for extracted patches") },
            extraction = RuntimeResult(patches, "verified", "a".repeat(64), "test:runtime:1"),
            expectedStatus = "verified"
        )
    }


    @Test
    fun `successful empty extraction replaces old patches and verifies its artifact`() {
        checkFailedFallback(
            fallback = { _, _ -> error("An extracted empty list must not use fallback metadata") },
            extraction = RuntimeResult(JsonArray(emptyList()), "verified", "a".repeat(64), "test:runtime:1"),
            expectedStatus = "verified"
        )
    }

    @Test
    fun `provider digest mismatch revokes binary proof`() {
        val root = createTempDirectory("digest-mismatch-").toFile()
        val folder = File(root, "demo-patch-bundles").apply { mkdir() }
        val patches = Json.parseToJsonElement("""[{"name":"Existing patch"}]""").jsonArray
        try {
            File(folder, "demo-latest-patches-bundle.json").writeText(
                """{"version":"v1","download_url":"https://example.test/demo.rvp",
                    "provider_digest":"sha256:${"b".repeat(64)}"}""")
            processBundle(folder,
                extract = { _, _ -> RuntimeResult(patches, "verified", "a".repeat(64)) },
                fallback = { _, _ -> null })
            val record = Json.decodeFromString<ExtractionRecord>(
                File(folder, "demo-latest-extraction.json").readText())
            assertEquals("artifact_digest_mismatch", record.status)
            assertEquals("sha256:" + "b".repeat(64), record.provider_digest)
            assertNull(record.patch_list_hash)
        } finally {
            root.deleteRecursively()
        }
    }

    private fun checkFailedFallback(
        fallback: (URI, String) -> JsonArray?,
        extraction: RuntimeResult = RuntimeResult(null, "runtime_parsing_failure", "a".repeat(64)),
        expectedStatus: String = "runtime_parsing_failure",
    ) {
        val root = createTempDirectory("extraction-proof-").toFile()
        val folder = File(root, "demo-patch-bundles").apply { mkdir() }
        val uri = URI("https://example.test/demo.rvp")
        val patches = Json.parseToJsonElement("""[{"name":"Existing patch"}]""").jsonArray
        val list = File(folder, "demo-latest-patches-list.json")
        val recordFile = File(folder, "demo-latest-extraction.json")
        val hash = "a".repeat(64)
        try {
            File(folder, "demo-latest-patches-bundle.json").writeText(
                """{"version":"v1","download_url":"$uri"}"""
            )
            list.writeText("""{"version":"v1","patches":$patches}""")
            val previous = list.readBytes()
            recordExtraction(recordFile, list, "v1", uri,
                RuntimeResult(patches, "verified", hash, "test:runtime:1"))
            processBundle(folder,
                extract = { _, _ -> extraction },
                fallback = fallback)
            val record = Json.decodeFromString<ExtractionRecord>(recordFile.readText())
            assertEquals(expectedStatus, record.status)
            assertEquals(hash, record.file_hash)
            if (expectedStatus == "verified") {
                assertEquals(sha256(list), record.patch_list_hash)
                assertEquals(extraction.patches, Json.decodeFromString<LocalPatchesFile>(list.readText()).patches)
            } else {
                assertNull(record.patch_list_hash)
                assertContentEquals(previous, list.readBytes())
            }
        } finally {
            folder.listFiles()?.forEach { it.delete() }
            folder.delete()
            root.delete()
        }
    }
}
