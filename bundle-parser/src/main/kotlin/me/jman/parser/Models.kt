package me.jman.parser

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonArray

@Serializable
data class BundleFile(
    @SerialName("created_at") val createdAt: String? = null,
    @SerialName("description") val description: String? = null,
    @SerialName("download_url") val downloadUrl: String? = null,
    @SerialName("signature_download_url") val signatureDownloadUrl: String? = null,
    @SerialName("version") val version: String? = null
)

@Serializable
data class LegacyBundleAsset(
    val version: String? = null,
    val url: String? = null
)

@Serializable
data class LegacyBundleFile(
    val patches: LegacyBundleAsset? = null,
    val integrations: LegacyBundleAsset? = null
)

@Serializable
data class LocalPatchesFile(
    val version: String,
    val patches: JsonArray
)
