package me.jman.parser

import app.revanced.library.serializeTo
import app.revanced.patcher.patch.loadPatchesFromJar
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.IOException
import java.net.HttpURLConnection
import java.net URI
import java.net URL
import java.util.zip.ZipFile

fun <T> List<T>.forEachGroupLogged(groupName: (T) -> String, action: (T) -> Unit) {
    for (item in this) {
        println("::group::${groupName(item)}")
        try {
            action(item)
        } finally {
            println("::endgroup::")
        }
    }
}

@Throws(IOException::class)
private fun downloadToFile(url: URL, outputFile: File) {
    var current = url
    var redirects = 0
    while (true) {
        var connection: HttpURLConnection? = null
        try {
            connection = current.openConnection() as HttpURLConnection
            connection.instanceFollowRedirects = false
            connection.connectTimeout = 15000
            connection.readTimeout = 15000
            System.getenv("GITHUB_TOKEN")?.let { token ->
                if (current.host.contains("github")) {
                    connection.setRequestProperty("Authorization", "token $token")
                }
            }
            connection.setRequestProperty("Accept", "application/octet-stream")
            connection.setRequestProperty("User-Agent", "bundle-parser")
            connection.setRequestProperty("Accept-Encoding", "identity")
            connection.connect()
            val code = connection.responseCode
            if (code in 300..399) {
                val location = connection.getHeaderField("Location") ?: throw IOException("Redirect without Location for $current")
                if (++redirects > 5) throw IOException("Too many redirects for $url")
                current = URL(location)
                continue
            }
            if (code != HttpURLConnection.HTTP_OK) {
                val error = connection.errorStream?.bufferedReader()?.readText()
                throw IOException("Failed to download $current: HTTP $code $error")
            }
            connection.inputStream.use { input ->
                outputFile.outputStream().use { out ->
                    input.copyTo(out)
                }
            }
            val expected = connection.getHeaderField("Content-Length")?.toLongOrNull()
            if (expected != null && outputFile.length() != expected) {
                throw IOException("Incomplete download for $current: expected $expected bytes, got ${outputFile.length()}")
            }
            if (outputFile.length() <= 0) {
                throw IOException("Downloaded file is empty for $current")
            }
            try {
                ZipFile(outputFile).close()
            } catch (e: IOException) {
                throw IOException("Downloaded file is not a valid zip for $current", e)
            }
            break
        } finally {
            connection?.disconnect()
        }
    }
}

fun generatePatchesFromUrl(uri: URI): String {
    val file = File.createTempFile("patches", ".jar")
    return try {
        downloadToFile(uri.toURL(), file)
        val json = ByteArrayOutputStream().apply {
            loadPatchesFromJar(setOf(file)).serializeTo(this, false)
        }.toString()
        if (json.isBlank()) throw IOException("Generated JSON is empty for ${uri.toURL()}")
        json
    } finally {
        file.delete()
    }
}
