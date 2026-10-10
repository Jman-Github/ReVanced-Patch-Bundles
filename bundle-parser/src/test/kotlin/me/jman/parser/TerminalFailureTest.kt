package me.jman.parser

import java.io.File
import java.util.jar.JarOutputStream
import java.util.jar.Manifest
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import kotlin.io.path.createTempDirectory
import kotlin.test.*

class TerminalFailureTest {
    @Test fun unchangedRejectionsPauseButRuntimeAndArtifactChangesResume() {
        val root = createTempDirectory("terminal-failure-").toFile()
        val config = File(root, "config.json").apply { writeText("""{"worker":{},"runtimes":[]}""") }
        val installed = File(root, "installed.json").apply { writeText("{}") }
        val properties = listOf("catalog.runtime.config", "catalog.runtime.manifest")
        val previous = properties.associateWith(System::getProperty)
        try {
            System.setProperty(properties[0], config.path)
            System.setProperty(properties[1], installed.path)
            val artifact = File(root, "bundle.rvp")
            JarOutputStream(artifact.outputStream(), Manifest().apply {
                mainAttributes.putValue("Manifest-Version", "1.0")
            }).use {}
            val folder = File(root, "demo-patch-bundles").apply { mkdir() }
            File(folder, "demo-latest-patches-bundle.json").writeText(
                """{"version":"v1","download_url":"${artifact.toURI()}"}""")
            val recordFile = File(folder, "demo-latest-extraction.json")
            var fallbacks = 0
            fun refresh() = processBundle(folder, fallback = { _, _ -> fallbacks++; null })
            refresh()
            val first = Json.decodeFromString<ExtractionRecord>(recordFile.readText())
            assertTrue(first.terminal)
            assertEquals("missing_compatible_runtime", first.status)
            val original = recordFile.readText()
            refresh()
            assertEquals(1, fallbacks)
            assertEquals(original, recordFile.readText())
            config.appendText(" ")
            refresh()
            assertEquals(2, fallbacks)
            val changed = Json.decodeFromString<ExtractionRecord>(recordFile.readText())
            assertNotEquals(first.failure_fingerprint, changed.failure_fingerprint)
            artifact.writeText("replaced invalid binary")
            refresh()
            assertEquals(3, fallbacks)
            val replaced = Json.decodeFromString<ExtractionRecord>(recordFile.readText())
            assertTrue(replaced.terminal)
            assertEquals("runtime_parsing_failure", replaced.status)
            assertEquals(sha256(artifact), replaced.file_hash)
            assertNotEquals(first.file_hash, replaced.file_hash)
        } finally {
            previous.forEach { (key, value) ->
                if (value == null) System.clearProperty(key) else System.setProperty(key, value)
            }
            root.deleteRecursively()
        }
    }
}
