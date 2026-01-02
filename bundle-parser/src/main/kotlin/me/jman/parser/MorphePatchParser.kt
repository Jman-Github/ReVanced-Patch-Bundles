package me.jman.parser

import app.morphe.patcher.patch.Option
import app.morphe.patcher.patch.Patch
import app.morphe.patcher.patch.loadPatchesFromJar
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import java.io.File
import java.io.FileNotFoundException
import java.net.URI

internal fun generateMorphePatchList(downloadUri: URI): JsonArray? {
    val patchesFile = File.createTempFile("morphe-patches", ".mpp")
    return try {
        downloadToFile(downloadUri.toURL(), patchesFile)
        val patches = loadPatchesFromJar(setOf(patchesFile))
        val jsonPatches = patches.filterIsInstance<Patch<*>>().map(::convertMorphePatch)
        JsonArray(jsonPatches)
    } catch (_: FileNotFoundException) {
        Logger.warning("The patch bundle file was not found.")
        null
    } catch (e: Exception) {
        Logger.warning("Failed to parse Morphe patch bundle. ${e.message}")
        null
    } finally {
        patchesFile.delete()
    }
}

private fun convertMorphePatch(patch: Patch<*>): JsonObject {
    val compatiblePackages = convertMorpheCompatiblePackages(patch.compatiblePackages ?: emptySet<Any?>())
    val dependencies = JsonArray(
        patch.dependencies
            .mapNotNull { it as? Patch<*> }
            .map { JsonPrimitive(dependencyLabel(it)) }
    )
    val options = JsonArray(
        patch.options.values
            .mapNotNull { it as? Option<*> }
            .map(::convertMorpheOption)
    )
    return buildJsonObject {
        put("name", JsonPrimitive(patch.name))
        put("description", JsonPrimitive(patch.description))
        put("use", JsonPrimitive(patch.use))
        put("dependencies", dependencies)
        put("compatiblePackages", compatiblePackages)
        put("options", options)
    }
}

private fun dependencyLabel(patch: Patch<*>): String {
    return patch.name?.takeIf { it.isNotBlank() }
        ?: patch.javaClass.simpleName.takeIf { it.isNotBlank() }
        ?: patch.javaClass.name
}

private fun convertMorpheOption(option: Option<*>): JsonObject {
    val name = option.name.orEmpty()
    val key = name.ifBlank { option.key.orEmpty() }
    val title = option.title.orEmpty().ifBlank { name.ifBlank { key } }
    val description = option.description.orEmpty()
    val values = option.values ?: emptyMap<String, Any?>()
    return buildJsonObject {
        put("key", JsonPrimitive(key))
        put("title", JsonPrimitive(title))
        put("description", JsonPrimitive(description))
        put("required", JsonPrimitive(option.required ?: false))
        put("type", JsonPrimitive(option.type?.toString() ?: "kotlin.Any"))
        put("default", toJsonValue(option.default))
        put("values", if (values.isEmpty()) JsonNull else mapToJsonObject(values))
    }
}

private fun convertMorpheCompatiblePackages(compatiblePackages: Set<*>): JsonElement {
    if (compatiblePackages.isEmpty()) {
        return JsonNull
    }
    val mapped = linkedMapOf<String, List<String>>()
    var ignoredCount = 0
    for (entry in compatiblePackages) {
        when (entry) {
            is Pair<*, *> -> {
                val name = entry.first as? String ?: continue
                mapped[name] = parseCompatibleVersions(entry.second)
            }
            is Map.Entry<*, *> -> {
                val name = entry.key as? String ?: continue
                mapped[name] = parseCompatibleVersions(entry.value)
            }
            is String -> mapped[entry] = emptyList()
            else -> ignoredCount++
        }
    }
    if (ignoredCount > 0) {
        Logger.warning("Skipped $ignoredCount compatible package entries with unsupported types.")
    }
    if (mapped.isEmpty()) {
        return JsonNull
    }
    return buildJsonObject {
        for ((name, versions) in mapped) {
            put(name, JsonArray(versions.map(::JsonPrimitive)))
        }
    }
}

private fun parseCompatibleVersions(value: Any?): List<String> {
    return when (value) {
        is Iterable<*> -> value.mapNotNull { it?.toString()?.takeIf(String::isNotBlank) }
        is Array<*> -> value.mapNotNull { it?.toString()?.takeIf(String::isNotBlank) }
        is String -> listOfNotNull(value.takeIf(String::isNotBlank))
        else -> emptyList()
    }
}

private fun toJsonValue(value: Any?): JsonElement {
    return when (value) {
        null -> JsonNull
        is String -> JsonPrimitive(value)
        is Number -> JsonPrimitive(value)
        is Boolean -> JsonPrimitive(value)
        else -> JsonPrimitive(value.toString())
    }
}

private fun mapToJsonObject(values: Map<*, *>): JsonObject {
    val mapped = values.entries.mapNotNull { (rawKey, rawValue) ->
        val key = rawKey?.toString()?.takeIf(String::isNotBlank) ?: return@mapNotNull null
        key to toJsonValue(rawValue)
    }.toMap()
    return JsonObject(mapped)
}
