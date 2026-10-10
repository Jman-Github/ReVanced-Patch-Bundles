package me.jman.parser

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.io.File
import java.net.URL

/** Tokens are scoped to explicit authorities and never forwarded between hosts. */
internal fun gitHostHeaders(url: URL, tokens: String? = System.getenv("GIT_HOST_TOKENS")): Map<String, String> {
    val authority = url.authority.lowercase()
    val configured = File("../config/git-hosts.json").takeIf { it.isFile }?.let {
        Json.parseToJsonElement(it.readText()) as? JsonObject
    }
    val kind = configured?.get(authority)?.jsonPrimitive?.content ?: when (authority) {
        "github.com", "api.github.com" -> "github"
        "gitlab.com" -> "gitlab"
        "codeberg.org", "gitea.com" -> "gitea"
        else -> return emptyMap()
    }
    val scoped = tokens?.takeIf { it.isNotBlank() }?.let {
        (Json.parseToJsonElement(it) as? JsonObject)?.get(authority)?.jsonPrimitive?.content
    }
    val token = scoped ?: when (authority) {
        "github.com", "api.github.com" -> System.getenv("GH_PAT")
        "gitlab.com" -> System.getenv("GITLAB_TOKEN")
        else -> null
    }
    if (token.isNullOrBlank()) return emptyMap()
    return if (kind == "gitlab") mapOf("PRIVATE-TOKEN" to token)
        else mapOf("Authorization" to "Bearer $token")
}
