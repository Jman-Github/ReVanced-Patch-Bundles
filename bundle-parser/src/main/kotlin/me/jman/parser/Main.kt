package me.jman.parser

import kotlinx.serialization.SerializationException
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import java.io.File
import java.io.FileNotFoundException
import java.net.URI

fun main() {
    val fileSuffix = "patches-list.json"

    val prettyJson = Json {
        prettyPrint = true
    }

    fun processBundle(bundleFolder: File) {
        val bundleName = bundleFolder.name.substringBefore("-patch-bundles")

        bundleFolder
            .listFiles()
            ?.filterNot { it.name.endsWith(fileSuffix) }
            ?.forEachGroupLogged(
                { "Processing file ${it.name}" }
            ) processFile@{ bundleJsonFile ->
                try {
                    val releaseTag = bundleJsonFile.name
                        .substringAfter("$bundleName-")
                        .substringBefore("-")

                    val parsedJsonContent: BundleFile

                    try {
                        Logger.info("Processing $releaseTag release...")
                        parsedJsonContent = Json.decodeFromString<BundleFile>(
                            bundleJsonFile.readText()
                        ).also {
                            if (it.version == "N/A") {
                                Logger.warning("Version is invalid.")
                                return@processFile
                            }
                        }
                    } catch (_: SerializationException) {
                        Logger.warning("Bundle is not supported.")
                        return
                    }

                    try {
                        val outputPatchesFile = File(bundleFolder, "$bundleName-$releaseTag-$fileSuffix")

                        var latestProcessedPatchesVersion: String? = null

                        if (outputPatchesFile.exists()) {
                            latestProcessedPatchesVersion = Json.decodeFromString<LocalPatchesFile>(
                                outputPatchesFile.readText()
                            ).version.also {
                                if (it == parsedJsonContent.version) {
                                    Logger.info("Patches are up to date.")
                                    return@processFile
                                }
                            }
                        }

                        if (latestProcessedPatchesVersion != null)
                            Logger.info("Version $latestProcessedPatchesVersion -> ${parsedJsonContent.version}")
                        else
                            Logger.info("No previous version found. Processing for the first time...")

                        Logger.info("Downloading .rvp from ${parsedJsonContent.downloadUrl}...")
                        generatePatchesFromUrl(
                            URI(parsedJsonContent.downloadUrl)
                        ).also {
                            Logger.info("Writing to ${outputPatchesFile.name}...")

                            outputPatchesFile.writeText(
                                prettyJson.encodeToString(
                                    LocalPatchesFile(parsedJsonContent.version, Json.parseToJsonElement(it).jsonArray)
                                )
                            )
                        }

                    } catch (_: FileNotFoundException) {
                        Logger.warning("The .rvp file was not found.")
                        return@processFile
                    }
                } catch (e: Exception) {
                    Logger.error("Something went wrong. ${e.message}, ${e.stackTrace}")
                    return@processFile
                }
            }
    }

    File("..", "patch-bundles").listFiles()!!.forEach {
        Logger.info("Fetching bundle ${it.name}")
        processBundle(it)
    }
}