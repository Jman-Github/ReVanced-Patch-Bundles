package me.jman.parser

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertEquals
import kotlin.test.assertNotNull
import kotlin.test.assertNull
import kotlin.test.assertTrue

class PatchArrayValidationTest {
    @Test
    fun `accepts named patch objects`() {
        assertTrue(isUsablePatchArray(Json.parseToJsonElement("""[{"name":"Valid patch"}]""").jsonArray))
    }

    @Test
    fun `accepts unnamed patches and successful empty lists`() {
        for (payload in listOf("""[{"name":null,"description":"Unnamed"}]""",
            """[{"name":""}]""", """[{"name":" "}]""", """[{}]""", "[]")) {
            assertTrue(isUsablePatchArray(Json.parseToJsonElement(payload).jsonArray), payload)
        }
    }

    @Test
    fun `fallback conversion rejects malformed entries instead of manufacturing an empty list`() {
        for (payload in listOf(
            """["broken"]""", """[null]""", """[{"name":"Valid patch"},"broken"]""",
            """{"patches":[{"name":42}]}""", """{"patches":{}}"""
        )) {
            assertNull(convertPatchMetadataPayload(payload), payload)
        }
        assertEquals(0, assertNotNull(convertPatchMetadataPayload("[]")).size)
        assertEquals(0, assertNotNull(convertPatchMetadataPayload("""{"patches":[]}""")).size)
        assertEquals(1, assertNotNull(convertPatchMetadataPayload(
            """[{"name":null,"description":"Unnamed fallback"}]""")).size)
    }

    @Test
    fun `rejects invalid patch entries before writing`() {
        for (payload in listOf(
            """["broken"]""",
            """[{"name":"Valid patch"},"broken"]""",
            """[null]""",
            """[{"name":42}]""",
        )) {
            assertFalse(isUsablePatchArray(Json.parseToJsonElement(payload).jsonArray), payload)
        }
    }
}
