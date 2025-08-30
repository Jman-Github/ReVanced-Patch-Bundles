package me.jman.parser

import app.revanced.library.serializeTo
import app.revanced.patcher.patch.loadPatchesFromJar
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
    url.openStream().use { input: InputStream ->
        outputFile.outputStream().use { fileOut ->
            input.copyTo(fileOut)
        }
    }

fun generatePatchesFromUrl(uri: URI): String{
    val patchesFile = File.createTempFile("patches", ".jar")
    try {
        downloadToFile(uri.toURL(), patchesFile)

        val serializedJson = ByteArrayOutputStream().apply {
            loadPatchesFromJar(setOf(patchesFile)).serializeTo(this, false)
        }.toString()

        return serializedJson
    } finally {
        patchesFile.delete()
    }
}