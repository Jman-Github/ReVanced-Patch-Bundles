package me.jman.parser

import kotlinx.serialization.SerializationException
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import java.io.File
import java.io.FileNotFoundException
import java.net.URI
import java.util.Locale
import kotlin.comparisons.compareBy

private enum class ReleaseType(val priority: Int) {
    LATEST(0),
    STABLE(1),
    DEV(2),
    OTHER(3);

    companion object {
        fun fromTag(tag: String): ReleaseType {
            return when (tag.lowercase(Locale.ROOT)) {
                "latest" -> LATEST
                "stable" -> STABLE
                "dev" -> DEV
                else -> OTHER
            }
        }
    }
}

private data class BundleVariant(
    val file: File,
    val releaseTag: String,
    val releaseType: ReleaseType
)

private fun extractReleaseTag(bundleName: String, fileName: String): String {
    val prefix = "$bundleName-"
    val withoutPrefix = if (fileName.startsWith(prefix)) fileName.removePrefix(prefix) else fileName
    val releaseTag = withoutPrefix.substringBefore("-")
    return releaseTag.ifEmpty { withoutPrefix }
}

fun main() {
    val fileSuffix = "patches-list.json"

    val prettyJson = Json {
        prettyPrint = true
    }

    fun processBundle(bundleFolder: File) {
        val bundleName = bundleFolder.name.substringBefore("-patch-bundles")

        val variants = bundleFolder
            .listFiles()
            ?.asSequence()
            ?.filter { it.isFile }
            ?.filter { it.extension.lowercase(Locale.ROOT) == "json" }
            ?.filterNot { it.name.endsWith(fileSuffix) }
            ?.map { file ->
                val releaseTag = extractReleaseTag(bundleName, file.name)
                BundleVariant(
                    file = file,
                    releaseTag = releaseTag,
                    releaseType = ReleaseType.fromTag(releaseTag)
                )
            }
            ?.sortedWith(
                compareBy<BundleVariant> { it.releaseType.priority }.thenBy { it.file.name }
            )
            ?.toList()
            ?: emptyList()

        variants
            .forEachGroupLogged(
                { "Processing file ${it.file.name}" }
            ) processVariant@{ variant ->
                try {
                    val parsedJsonContent: BundleFile

                    try {
                        Logger.info("Processing ${variant.releaseTag} release...")
                        parsedJsonContent = Json.decodeFromString<BundleFile>(
                            variant.file.readText()
                        ).also {
                            if (it.version == "N/A") {
                                Logger.warning("Version is invalid.")
                                return@processVariant
                            }
                        }
                    } catch (_: SerializationException) {
                        Logger.warning("Bundle is not supported.")
                        return@processVariant
                    }

                    try {
                        val outputPatchesFile = File(bundleFolder, "$bundleName-${variant.releaseTag}-$fileSuffix")

                        var existingContent: LocalPatchesFile? = null

                        if (outputPatchesFile.exists()) {
                            existingContent = Json.decodeFromString<LocalPatchesFile>(
                                outputPatchesFile.readText()
                            ).also {
                                if (it.version != parsedJsonContent.version) {
                                    Logger.info("Version ${it.version} -> ${parsedJsonContent.version}")
                                } else {
                                    Logger.info("Version ${parsedJsonContent.version} exists; verifying content")
                                }
                            }
                        } else {
                            Logger.info("No previous version found. Processing for the first time...")
                        }

                        Logger.info("Downloading .rvp from ${parsedJsonContent.downloadUrl}...")
                        val generated = Json.parseToJsonElement(
                            generatePatchesFromUrl(
                                URI(parsedJsonContent.downloadUrl)
                            )
                        ).jsonArray

                        if (existingContent != null && existingContent.version == parsedJsonContent.version && existingContent.patches == generated) {
                            Logger.info("Patches are up to date.")
                            return@processVariant
                        }

                        Logger.info("Writing to ${outputPatchesFile.name}...")

                        outputPatchesFile.writeText(
                            prettyJson.encodeToString(
                                LocalPatchesFile(parsedJsonContent.version, generated)
                            )
                        )
                    } catch (_: FileNotFoundException) {
                        Logger.warning("The .rvp file was not found.")
                        return@processVariant
                    }
                } catch (e: Exception) {
                    Logger.error("Something went wrong. ${e.message}, ${e.stackTrace}")
                    return@processVariant
                }
            }
    }

    File("..", "patch-bundles").listFiles()!!.forEach {
        Logger.info("Fetching bundle ${it.name}")
        processBundle(it)
    }
}
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

                        var existingContent: LocalPatchesFile? = null

                        if (outputPatchesFile.exists()) {
                            existingContent = Json.decodeFromString<LocalPatchesFile>(
                                outputPatchesFile.readText()
                            ).also {
                                if (it.version != parsedJsonContent.version) {
                                    Logger.info("Version ${it.version} -> ${parsedJsonContent.version}")
                                } else {
                                    Logger.info("Version ${parsedJsonContent.version} exists; verifying content")
                                }
                            }
                        } else {
                            Logger.info("No previous version found. Processing for the first time...")
                        }

                        Logger.info("Downloading .rvp from ${parsedJsonContent.downloadUrl}...")
                        val generated = Json.parseToJsonElement(
                            generatePatchesFromUrl(
                                URI(parsedJsonContent.downloadUrl)
                            )
                        ).jsonArray

                        if (existingContent != null && existingContent.version == parsedJsonContent.version && existingContent.patches == generated) {
                            Logger.info("Patches are up to date.")
                            return@processFile
                        }

                        Logger.info("Writing to ${outputPatchesFile.name}...")

                        outputPatchesFile.writeText(
                            prettyJson.encodeToString(
                                LocalPatchesFile(parsedJsonContent.version, generated)
                            )
                        )
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
