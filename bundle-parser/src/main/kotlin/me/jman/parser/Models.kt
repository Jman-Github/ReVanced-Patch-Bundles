package me.jman.parser

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonArray

@Serializable
data class BundleFile(
    @SerialName("created_at") val createdAt: String,
    @SerialName("description") val description: String,
    @SerialName("download_url") val downloadUrl: String,
    @SerialName("signature_download_url") val signatureDownloadUrl: String,
    @SerialName("version") val version: String
)

@Serializable
data class LocalPatchesFile(
    val version: String,
    val patches: JsonArray
)
