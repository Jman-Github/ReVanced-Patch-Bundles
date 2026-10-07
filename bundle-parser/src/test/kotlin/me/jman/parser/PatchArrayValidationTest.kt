package me.jman.parser

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlin.test.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

class PatchArrayValidationTest {
    @Test
    fun `accepts named patch objects`() {
        assertTrue(isUsablePatchArray(Json.parseToJsonElement("""[{"name":"Valid patch"}]""").jsonArray))
    }

    @Test
    fun `rejects invalid patch entries before writing`() {
        for (payload in listOf(
            """["broken"]""",
            """[{"name":"Valid patch"},"broken"]""",
            """[null]""",
            """[{"name":42}]""",
            """[{"name":" "}]""",
            """[{}]""",
            """[]""",
        )) {
            assertFalse(isUsablePatchArray(Json.parseToJsonElement(payload).jsonArray), payload)
        }
    }
}
