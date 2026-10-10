package me.jman.parser

import java.io.File
import kotlinx.serialization.decodeFromString
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFalse
import kotlin.test.assertFailsWith
import kotlin.test.assertTrue

class PatcherRuntimeSelectionTest {
    private fun definition(id: String, family: String, range: String, fallback: Boolean = false) =
        RuntimeDefinition(id, family, "morphe", "test:runtime:$id", emptyList(), range, fallback)
    private val configuration = RuntimeConfiguration(WorkerSettings(), listOf(
        definition("early", "Morphe:V1", ">=1.0.0 <=1.2.0", true),
        definition("new", "Morphe:V1", ">1.2.0 <=1.14.1", true),
        definition("v4", "ReVanced:V4", "*", true),
        definition("v3", "ReVanced:V3", "*", true)
    ))

    @Test fun shippedConfigurationKeepsAllLegacyAndModernFallbacks() {
        val shipped = Json.decodeFromString<RuntimeConfiguration>(
            File("../config/patcher-runtimes.json").readText()
        )
        assertEquals(listOf("revanced-v3-19", "revanced-v3-15", "revanced-v3-11", "revanced-v3-bytecode"),
            selectRuntimes(shipped, "ReVanced:V3", "legacy").map { it.id })
        assertEquals(listOf("revanced-22", "revanced-21", "revanced-20"),
            selectRuntimes(shipped, "ReVanced:V4", "22.1.0-dev.1").map { it.id })
    }

    @Test fun shippedConfigurationSelectsMorpheRuntimes() {
        val shipped = Json.decodeFromString<RuntimeConfiguration>(
            File("../config/patcher-runtimes.json").readText()
        )
        val expected = mapOf(
            "0.9.0" to "morphe-12",
            "1.1.1" to "morphe-12",
            "1.2.0-rc.1" to "morphe-12",
            "1.2.0" to "morphe-12",
            "1.2.1" to "morphe-latest",
            "1.9.0" to "morphe-latest",
            "2.0.0" to "morphe-latest",
            "1.15.1" to "morphe-latest"
        )
        for ((version, runtime) in expected) {
            assertEquals(listOf(runtime),
                selectRuntimes(shipped, "Morphe:V1", version).map { it.id }, version)
        }
        assertEquals(listOf("morphe-early"),
            selectRuntimes(shipped, "Morphe:V1", null).map { it.id })
    }

    @Test fun fallbackOnlyRuntimesDoNotMatchDeclaredVersions() {
        val fallback = RuntimeDefinition("fallback", "Morphe:V1", "morphe",
            "test:runtime:1", emptyList(), fallback = true)
        val config = RuntimeConfiguration(WorkerSettings(), listOf(fallback))
        assertEquals(listOf(fallback), selectRuntimes(config, "Morphe:V1", null))
        assertTrue(selectRuntimes(config, "Morphe:V1", "1.0.0").isEmpty())
    }

    @Test fun versionsSelectTheCompatibleRuntime() {
        assertEquals(listOf("early"), selectRuntimes(configuration, "Morphe:V1", "1.2.0").map { it.id })
        assertEquals(listOf("new"), selectRuntimes(configuration, "Morphe:V1", "1.9.0").map { it.id })
        assertEquals(listOf("new"), selectRuntimes(configuration, "Morphe:V1", "1.14.1").map { it.id })
        assertTrue(selectRuntimes(configuration, "Morphe:V1", "2.0.0").isEmpty())
    }
    @Test fun undeclaredBundlesRetainOrderedFallbacks() {
        assertEquals(listOf("early", "new"),
                     selectRuntimes(configuration, "Morphe:V1", null).map { it.id })
        assertEquals("v4", selectRuntimes(configuration, "ReVanced:V4", null).single().id)
        assertEquals("v3", selectRuntimes(configuration, "ReVanced:V3", null).single().id)
    }
    @Test fun prereleaseOrderingIsSemantic() {
        assertTrue(matchesPatcherRange(">=21.1.0-dev.5 <22.0.0", "21.1.0-dev.10"))
        assertFalse(matchesPatcherRange(">=21.1.0", "21.1.0-dev.10"))
        assertTrue(matchesPatcherRange("=1.2.0", "1.2.0+build.4"))
        assertFailsWith<IllegalStateException> { matchesPatcherRange(">=1.0.0", "broken") }
    }
    @Test fun wildcardReaderRetainsLegacyManifestDeclarations() {
        assertTrue(matchesPatcherRange("*", "legacy"))
        assertEquals("v3", selectRuntimes(configuration, "ReVanced:V3", "legacy").single().id)
    }
    @Test fun conflictingRulesFailWithoutChoosingAnArbitraryRuntime() {
        val overlap = configuration.copy(runtimes = configuration.runtimes +
            definition("overlap", "Morphe:V1", "*"))
        assertFailsWith<IllegalArgumentException> { selectRuntimes(overlap, "Morphe:V1", "1.9.0") }
    }
    @Test fun configurationCanAddACompatibleVersionWithoutChangingSelectionCode() {
        val added = configuration.copy(runtimes = configuration.runtimes +
            definition("future", "Morphe:V1", ">=2.0.0 <3.0.0"))
        assertEquals("future", selectRuntimes(added, "Morphe:V1", "2.1.0").single().id)
        assertTrue(selectRuntimes(added, "Unknown:V1", null).isEmpty())
    }
}
