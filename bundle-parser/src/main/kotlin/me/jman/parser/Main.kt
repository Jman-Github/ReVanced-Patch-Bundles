package me.jman.parser

import app.revanced.library.serializeTo
import app.revanced.patcher.patch.loadPatchesFromJar
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.InputStream
import java.net.URI
import java.net.URL
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse

fun fetchJsonText(uri: URI): String {
    val client = HttpClient.newHttpClient()
    val request = HttpRequest.newBuilder()
        .uri(uri)
        .build()

    val response = client.send(request, HttpResponse.BodyHandlers.ofString())

    if (response.statusCode() == 200) {
        return response.body()
    } else {
        error("Failed to fetch JSON: ${response.statusCode()}")
    }
}

fun downloadToFile(url: URL, outputFile: File) =
        url.openStream().use { input: InputStream ->
            outputFile.outputStream().use { fileOut ->
                input.copyTo(fileOut)
            }
        }

@Serializable
data class PatchBundleJson(
    val created_at: String,
    val description: String,
    val download_url: String,
    val signature_download_url: String,
    val version: String
)

fun main(args: Array<String>) {
    val bundleJson = Json.decodeFromString<PatchBundleJson>(
        fetchJsonText(
            URI("https://raw.githubusercontent.com/Jman-Github/ReVanced-Patch-Bundles/bundles/patch-bundles/revanced-patch-bundles/revanced-latest-patches-bundle.json")
        )
    )
    val patchesFile = File("patches.jar")

    downloadToFile(
        URI(bundleJson.download_url).toURL(),
        patchesFile
    )

    println("Downloaded to: ${patchesFile.absolutePath}")

    val serializedJson = ByteArrayOutputStream().apply(
        loadPatchesFromJar(setOf(patchesFile))::serializeTo
    )

    println(serializedJson)
}