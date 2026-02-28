package me.jman.parser

import app.revanced.library.serializeTo
import app.revanced.patcher.patch.loadPatches
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.InputStream
import java.net.URI
import java.net.URL

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

fun downloadToFile(url: URL, outputFile: File) =
    url.openConnection().apply {
        connectTimeout = 10_000
        readTimeout = 30_000
    }.getInputStream().use { input: InputStream ->
        outputFile.outputStream().use { fileOut ->
            input.copyTo(fileOut)
        }
    }

fun generatePatchesFromUrl(uri: URI): String{
    val patchesFile = File.createTempFile("patches", ".jar")
    try {
        downloadToFile(uri.toURL(), patchesFile)

        val serializedJson = ByteArrayOutputStream().apply {
            loadPatches(patchesFile) { file, throwable ->
                throw IllegalStateException("Failed to load patches from ${file.name}", throwable)
            }.serializeTo(this, false)
        }.toString(Charsets.UTF_8)

        return serializedJson
    } finally {
        patchesFile.delete()
    }
}
