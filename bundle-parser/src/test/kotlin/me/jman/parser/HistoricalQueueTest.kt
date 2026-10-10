package me.jman.parser

import kotlinx.serialization.decodeFromString
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.io.path.createTempDirectory
import java.io.File
import kotlin.test.assertEquals

class HistoricalQueueTest {
    private val directory = createTempDirectory("historical-queue-").toFile()

    private fun entry(name: String, attempted: String?, fingerprint: String?, verified: Boolean = false): File {
        val folder = File(directory, "$name-patch-bundles").apply { mkdirs() }
        File(folder, "$name-stable-patches-bundle.json").writeText(
            """{"version":"v1","download_url":"https://example.test/bundle.rvp"}""")
        val patches = File(folder, "$name-stable-patches-list.json").apply {
            writeText("""{"version":"v1","patches":[{"name":"Patch"}],"metadata_schema_version":${PATCH_METADATA_SCHEMA_VERSION}}""")
        }
        val record = ExtractionRecord("v1", "https://example.test/bundle.rvp",
            if (verified) "verified" else "failed", "hash", null,
            if (verified) sha256(patches) else null, attempted, fingerprint)
        File(folder, "$name-stable-extraction.json").writeText(Json.encodeToString(record))
        return folder
    }

    @Test fun `malformed metadata does not stop the historical queue`() {
        val malformed = entry("malformed", null, null)
        File(malformed, "malformed-stable-patches-bundle.json").writeText("""{"patches":[],"bundle_type":{},"provider_digest":{}}""")
        val next = entry("next", null, null)
        assertEquals(listOf(malformed, next), historicalCandidates(directory, 2, "runtime"))
        directory.deleteRecursively()
    }

    @Test fun `disabled history does not consume the extraction batch`() {
        val disabled = entry("disabled", null, null)
        val enabled = entry("enabled", null, null)
        assertEquals(listOf(enabled), historicalCandidates(directory, 1, "runtime", setOf(disabled.name)))
        directory.deleteRecursively()
    }

    @Test fun `bounded history queue skips verified work and rotates failures`() {
        val old = entry("old", "2026-01-01", "runtime")
        entry("new", "2026-02-01", "runtime")
        entry("verified", null, null, true)
        assertEquals(listOf(old), historicalCandidates(directory, 1, "runtime"))
        val changed = entry("changed", "2026-03-01", "previous-runtime")
        assertEquals(listOf(changed, old), historicalCandidates(directory, 2, "runtime"))
        directory.deleteRecursively()
    }
    @Test fun `changed provider digest requeues verified historical metadata`() {
        val folder = entry("changed", null, null, true)
        val input = File(folder, "changed-stable-patches-bundle.json")
        val recordFile = File(folder, "changed-stable-extraction.json")
        val original = Json.decodeFromString<ExtractionRecord>(recordFile.readText())
        recordFile.writeText(Json.encodeToString(original.copy(file_hash = "a".repeat(64))))
        input.writeText("""{"version":"v1","download_url":"https://example.test/bundle.rvp",
            "provider_digest":"SHA256:${"A".repeat(64)}"}""")
        assertEquals(emptyList(), historicalCandidates(directory, 1, "runtime"))
        input.writeText("""{"version":"v1","download_url":"https://example.test/bundle.rvp",
            "provider_digest":"sha256:${"b".repeat(64)}"}""")
        assertEquals(listOf(folder), historicalCandidates(directory, 1, "runtime"))
        directory.deleteRecursively()
    }

    @Test fun `superseded history folders do not consume the extraction batch`() {
        entry("obsolete", null, null)
        val active = entry("selected", null, null)
        File(directory, "sources.json").writeText(
            """{"selected":{"cache_path":"internal/cache/history/${active.name}/selected-stable-patches-bundle.json"}}""")
        assertEquals(listOf(active), historicalCandidates(directory, 1, "runtime"))
        directory.deleteRecursively()
    }

    @Test fun `terminal rejections pause until artifact family identity or runtime changes`() {
        val folder = entry("rejected", "2026-01-01", "runtime")
        try {
            val recordFile = File(folder, "rejected-stable-extraction.json")
            val record = Json.decodeFromString<ExtractionRecord>(recordFile.readText()).copy(
                status = "runtime_parsing_failure", terminal = true,
                bundle_type = "ReVanced:V4", file_hash = "a".repeat(64))
            recordFile.writeText(Json.encodeToString(record))
            assertEquals(emptyList(), historicalCandidates(directory, 1, "runtime"))
            assertEquals(listOf(folder), historicalCandidates(directory, 1, "new-runtime"))
            val raw = File(folder, "rejected-stable-patches-bundle.json")
            for (changed in listOf(
                """"provider_digest":"sha256:${"b".repeat(64)}",""",
                """"bundle_type":"Morphe:V1",""",
            )) {
                raw.writeText("""{$changed"version":"v1","download_url":"https://example.test/bundle.rvp"}""")
                assertEquals(listOf(folder), historicalCandidates(directory, 1, "runtime"))
            }
            for ((version, url) in listOf("v2" to record.download_url, "v1" to "https://example.test/new.rvp")) {
                raw.writeText("""{"version":"$version","download_url":"$url"}""")
                assertEquals(listOf(folder), historicalCandidates(directory, 1, "runtime"))
            }
        } finally { directory.deleteRecursively() }
    }

    @Test fun `old Morphe and legacy compatibility metadata is refreshed once`() {
        for (family in listOf("Morphe:V1", "ReVanced:V3", "ReVanced:V4")) {
            val folder = entry("schema", null, null, true)
            val input = File(folder, "schema-stable-patches-bundle.json")
            input.writeText("""{"version":"v1","download_url":"https://example.test/bundle.rvp","bundle_type":"$family"}""")
            val patches = File(folder, "schema-stable-patches-list.json")
            patches.writeText("""{"version":"v1","patches":[],"metadata_schema_version":2}""")
            val oldMarker = File(folder, "schema-stable-extraction.json")
            val oldRecord = Json.decodeFromString<ExtractionRecord>(oldMarker.readText())
            oldMarker.writeText(Json.encodeToString(oldRecord.copy(patch_list_hash = sha256(patches))))
            assertEquals(listOf(folder), historicalCandidates(directory, 1, "runtime"))
            patches.writeText("""{"version":"v1","patches":[],"metadata_schema_version":${PATCH_METADATA_SCHEMA_VERSION}}""")
            val marker = File(folder, "schema-stable-extraction.json")
            val record = Json.decodeFromString<ExtractionRecord>(marker.readText())
            marker.writeText(Json.encodeToString(record.copy(patch_list_hash = sha256(patches))))
            assertEquals(emptyList(), historicalCandidates(directory, 1, "runtime"))
            folder.deleteRecursively()
        }
        directory.deleteRecursively()
    }

    @Test fun `latest history runs outside the ordinary batch and keeps verification policies`() {
        val first = entry("latest-stable", "2026-03-01", "runtime")
        val second = entry("latest-dev", "2026-03-01", "runtime")
        val older = entry("ordinary", null, null)
        val verified = entry("verified-latest", null, null, true)
        val disabled = entry("disabled-latest", null, null)
        val folders = listOf(first, second, older, verified, disabled)
        val registry = kotlinx.serialization.json.buildJsonObject {
            for (folder in folders) put(folder.name, kotlinx.serialization.json.buildJsonObject {
                put("cache_path", kotlinx.serialization.json.JsonPrimitive(
                    "internal/cache/history/${folder.name}/bundle.json"))
                put("is_latest", kotlinx.serialization.json.JsonPrimitive(folder != older))
            })
        }
        File(directory, "sources.json").writeText(registry.toString())
        val work = historicalWork(directory, 1, "runtime", setOf(disabled.name))
        assertEquals(setOf(first, second), work.latest.toSet())
        assertEquals(listOf(older), work.historical)
        directory.deleteRecursively()
    }

    @Test fun `opaque digests invalidate earlier extraction markers`() {
        assertEquals(false, matchesProviderDigest("new-digest", "hash", "old-digest"))
        assertEquals(true, matchesProviderDigest("new-digest", "hash", "new-digest"))
    }

}
