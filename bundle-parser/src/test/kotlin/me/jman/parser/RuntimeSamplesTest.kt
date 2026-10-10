package me.jman.parser

import java.io.File
import java.util.concurrent.TimeUnit
import kotlin.io.path.createTempDirectory
import kotlinx.serialization.json.*
import kotlin.test.*

/** Optional local artifacts exercise real third-party runtimes without network access in tests. */
class RuntimeSamplesTest {
    @Test fun extractRepresentativeArtifacts() {
        val manifest = System.getenv("CATALOG_RUNTIME_SAMPLES") ?: return
        val samples = Json.parseToJsonElement(File(manifest).readText()).jsonArray
        assertTrue(samples.isNotEmpty())
        val libraries = File("build/install/bundle-parser/lib").listFiles().orEmpty()
            .filter { it.extension == "jar" }.joinToString(File.pathSeparator) { it.absolutePath }
        assertTrue(libraries.isNotEmpty(), "Parser distribution is missing")
        val root = createTempDirectory("real-runtime-samples-").toFile()
        try {
            for ((index, item) in samples.withIndex()) {
                val sample = item.jsonObject
                val path = File(sample.getValue("path").jsonPrimitive.content)
                val classpath = sample.getValue("classpath").jsonPrimitive.content
                val loader = sample.getValue("loader").jsonPrimitive.content
                val output = File(root, "$index.json")
                val log = File(root, "$index.log")
                val process = ProcessBuilder(
                    File(System.getProperty("java.home"), "bin/java").absolutePath, "-Xmx512m",
                    "-Drevanced.patcher21.classpath=$classpath",
                    "-Drevanced.patcher22.classpath=$classpath",
                    "-Dmorphe.patcher.classpath=$classpath",
                    "-cp", listOf(libraries, classpath).filter(String::isNotBlank).joinToString(File.pathSeparator),
                    "me.jman.parser.MainKt", "--runtime-worker", loader, path.absolutePath, output.absolutePath
                ).redirectErrorStream(true).redirectOutput(log).start()
                try {
                    assertTrue(process.waitFor(90, TimeUnit.SECONDS), "$loader timed out: ${path.name}")
                    assertEquals(0, process.exitValue(), "$loader failed for ${path.name}: ${log.readText()}")
                    val patches = Json.parseToJsonElement(output.readText()).jsonArray
                    assertTrue(isUsablePatchArray(patches), "$loader rejected $path")
                    println("Real runtime sample: $loader extracted ${patches.size} patches from ${path.name}")
                } finally {
                    if (process.isAlive) {
                        process.destroyForcibly()
                        process.waitFor(5, TimeUnit.SECONDS)
                    }
                }
            }
        } finally {
            root.deleteRecursively()
        }
    }
}
