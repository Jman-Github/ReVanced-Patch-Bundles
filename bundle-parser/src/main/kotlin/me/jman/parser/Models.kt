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
    @SerialName("version") val version: String? = null,
    @SerialName("provider_digest") val providerDigest: String? = null,
    @SerialName("bundle_type") val bundleType: String? = null
)

@Serializable
data class LegacyBundleAsset(
    val version: String? = null,
    val url: String? = null
)

@Serializable
data class LegacyBundleFile(
    val patches: LegacyBundleAsset? = null,
    val integrations: LegacyBundleAsset? = null,
    @SerialName("provider_digest") val providerDigest: String? = null
)

internal const val PATCH_METADATA_SCHEMA_VERSION = 3

@Serializable
data class LocalPatchesFile(
    val version: String,
    val patches: JsonArray,
    val metadata_schema_version: Int = 0
)
