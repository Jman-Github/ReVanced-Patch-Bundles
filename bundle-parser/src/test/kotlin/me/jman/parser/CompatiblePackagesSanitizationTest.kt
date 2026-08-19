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

        val result = convertCompatibilityArray(compatiblePackages)

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
