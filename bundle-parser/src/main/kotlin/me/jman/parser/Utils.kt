package me.jman.parser

import app.revanced.library.serializeTo
import app.revanced.patcher.patch.loadPatchesFromJar
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.IOException
import java.io.InputStream
import java.net.HttpURLConnection
import java.net.URI
import java.net URL

inline fun <T> List<T>.forEachGroupLogged(groupName: (T) -> String, action: (T) -> Unit) {
    for (item in this) {
        println("::group::${groupName(item)}")
        try {
            action(item)
        } finally {
            println("::endgroup::")
        }
    }
}

fun downloadToFile(url: URL, outputFile: File) {
    var currentUrl = url
    var redirects = 0
    while (true) {
        val connection = currentUrl.openConnection() as HttpURLConnection
        connection.instanceFollowRedirects = false
        val token = System.getenv("GITHUB_TOKEN")
        if (token != null && (currentUrl.host.contains("github"))) {
            connection.setRequestProperty("Authorization", "token $token")
        }
        connection.setRequestProperty("Accept", "application/octet-stream")
        connection.setRequestProperty("User-Agent", "bundle-parser")
        connection.connect()
        val code = connection.responseCode
        if (code in 300..399) {
            val location = connection.getHeaderField("Location")
                ?: throw IOException("Redirect without Location for $currentUrl")
            if (redirects++ >= 5) {
                throw IOException("Too many redirects for $url")
            }
            currentUrl = URL(location)
            continue
        }
        if (code != HttpURLConnection.HTTP_OK) {
            val error = connection.errorStream?.bufferedReader()?.readText()
            throw IOException("Failed to download $currentUrl: HTTP $code $error")
        }
        connection.inputStream.use { input: InputStream ->
            outputFile.outputStream().use { fileOut ->
                input.copyTo(fileOut)
            }
        }
        val expected = connection.getHeaderField("Content-Length")?.toLongOrNull()
        if (expected != null && outputFile.length() != expected) {
            throw IOException("Incomplete download for $currentUrl: expected $expected bytes, got ${outputFile.length()}")
        }
        if (outputFile.length() <= 0) {
            throw IOException("Downloaded file is empty for $currentUrl")
        }
        break
    }
}

fun generatePatchesFromUrl(uri: URI): String {
    val patchesFile = File.createTempFile("patches", ".jar")
    try {
        downloadToFile(uri.toURL(), patchesFile)
        val serializedJson = ByteArrayOutputStream().apply {
            loadPatchesFromJar(setOf(patchesFile)).serializeTo(this, false)
        }.toString()
        if (serializedJson.isBlank()) {
            throw IOException("Generated JSON is empty for ${uri.toURL()}")
        }
        return serializedJson
    } finally {
        patchesFile.delete()
    }
}
