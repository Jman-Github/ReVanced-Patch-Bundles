package me.jman.parser

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertNotNull

class CompatiblePackagesSanitizationTest {
    @Test fun `fallback conversion preserves unrestricted and empty versions`() {
        val metadata = Json.parseToJsonElement("""
            [{"name":"unrestricted","versions":null},{"name":"empty","versions":[]},
             {"name":"omitted"},{"name":"no-targets","targets":[]},
             {"name":"restricted","versions":["1.0"]}]
        """).jsonArray
        val result = convertCompatibilityArray(metadata).jsonObject
        assertEquals(JsonNull, result["unrestricted"])
        assertEquals(JsonNull, result["omitted"])
        assertEquals(0, result.getValue("empty").jsonArray.size)
        assertEquals(0, result.getValue("no-targets").jsonArray.size)
        assertEquals("1.0", result.getValue("restricted").jsonArray.single().jsonPrimitive.content)
        val patch = assertNotNull(convertPatchMetadataPayload(
            """[{"name":"Patch","compatiblePackages":{"com.any":null,"com.none":[]}}]"""
        )).single().jsonObject
        assertEquals(JsonNull, patch.getValue("compatiblePackages").jsonObject["com.any"])
        assertEquals(0, patch.getValue("compatiblePackages").jsonObject.getValue("com.none").jsonArray.size)
    }

    @Test fun `fallback keeps repeated restricted and unrestricted package links`() {
        val compatible = Json.parseToJsonElement("""[
            {"name":"com.app","versions":["1.0","1.0"]},
            {"name":"com.app","versions":["2.0","1.0"]},
            {"name":"com.app","versions":null}
        ]""").jsonArray
        val entries = convertCompatibilityArray(compatible).jsonArray.map { it.jsonObject }
        assertEquals(JsonNull, entries.first()["versions"])
        assertEquals(listOf("1.0", "2.0"), entries.last().getValue("versions").jsonArray.map { it.jsonPrimitive.content })
    }

    private fun compatiblePackage(json: String) = sanitizeCompatiblePackages(
        Json.parseToJsonElement(json).jsonArray
    )[0].jsonObject["compatiblePackages"]!!.jsonArray[0].jsonObject

    @Test
    fun `derives missing versions from targets`() {
        val result = compatiblePackage(
            """[{"compatiblePackages":[{"name":"RailOne","packageName":"org.cris.aikyam","targets":[{"version":"2.1.62"},{"version":null},{"version":"2.1.62"},{"version":"2.1.63"}]}]}]"""
        )

        assertEquals(listOf("2.1.62", "2.1.63"), result["versions"]!!.jsonArray.map { it.jsonPrimitive.content })
        assertNotNull(result["targets"])
    }

    @Test
    fun `preserves explicit versions instead of targets`() {
        val result = compatiblePackage(
            """[{"compatiblePackages":[{"name":"RailOne","versions":["explicit"],"targets":[{"version":"2.1.62"}]}]}]"""
        )

        assertEquals(listOf("explicit"), result["versions"]!!.jsonArray.map { it.jsonPrimitive.content })
    }

    @Test
    fun `release metadata conversion derives missing versions from targets`() {
        val compatiblePackages = Json.parseToJsonElement(
            """[{"name":"RailOne","targets":[{"version":"2.1.62"},{"version":null},{"version":"2.1.62"}]}]"""
        ).jsonArray

        val result = convertCompatibilityArray(compatiblePackages).jsonObject

        assertEquals(
            listOf("2.1.62"),
            result["RailOne"]!!.jsonArray.map { it.jsonPrimitive.content }
        )
    }

    @Test
    fun `preserves explicit null versions`() {
        val result = compatiblePackage(
            """[{"compatiblePackages":[{"name":"RailOne","versions":null,"targets":[{"version":"2.1.62"}]}]}]"""
        )

        assertEquals(JsonNull, result["versions"])
    }
}
