package me.jman.parser

import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import java.io.File
import java.io.FileNotFoundException
import java.lang.reflect.InvocationTargetException
import java.lang.reflect.Method
import java.lang.reflect.Modifier
import java.net.URI
import java.net.URLClassLoader
import java.util.jar.JarFile

private const val MORPHE_PATCHER_CLASSPATH_PROPERTY = "morphe.patcher.classpath"

internal fun generateMorphePatchList(downloadUri: URI): JsonArray? {
    val patchesFile = File.createTempFile("morphe-patches", ".mpp")
    return try {
        val classpathFiles = morpheClasspathFiles()
        downloadToFile(downloadUri.toURL(), patchesFile)
        URLClassLoader(classpathFiles.map { it.toURI().toURL() }.toTypedArray(), null).use { classLoader ->
            val patches = loadMorphePatchesFromJar(patchesFile, classLoader)
            val jsonPatches = patches.map(::convertMorphePatch)
            if (jsonPatches.isEmpty()) {
                Logger.warning("No patches were found in the Morphe patch bundle.")
                null
            } else {
                JsonArray(jsonPatches)
            }
        }
    } catch (_: FileNotFoundException) {
        Logger.warning("The patch bundle file was not found.")
        null
    } catch (e: Exception) {
        Logger.warning("Failed to parse Morphe patch bundle. ${e.describeForLog()}")
        null
    } finally {
        patchesFile.delete()
    }
}

private fun Throwable.describeForLog(): String {
    val chain = generateSequence(this) { it.cause }
        .take(5)
        .map { throwable ->
            val type = throwable::class.simpleName ?: throwable::class.java.name
            val message = throwable.message?.takeIf { it.isNotBlank() } ?: "no message"
            "$type: $message"
        }
        .toList()

    return if (chain.isEmpty()) {
        val type = this::class.simpleName ?: this::class.java.name
        "$type: no message"
    } else {
        chain.joinToString(" <- ")
    }
}

private fun morpheClasspathFiles(): List<File> {
    val classpathProperty = System.getProperty(MORPHE_PATCHER_CLASSPATH_PROPERTY)
        ?.takeIf { it.isNotBlank() }
        ?: throw IllegalStateException("Morphe patcher classpath is not configured.")

    val classpathFiles = classpathProperty
        .split(File.pathSeparator)
        .map { it.trim() }
        .filter { it.isNotEmpty() }
        .map(::File)
        .filter(File::exists)

    if (classpathFiles.isEmpty()) {
        throw IllegalStateException("Morphe patcher classpath is empty.")
    }

    return classpathFiles
}

private fun loadMorphePatchesFromJar(
    patchesFile: File,
    morpheClassLoader: ClassLoader
): List<Any> {
    val loadMethod = findMorpheLoadMethod(morpheClassLoader)
    val patches = try {
        loadMethod.invoke(null, setOf(patchesFile))
    } catch (e: InvocationTargetException) {
        val target = e.targetException ?: e
        val type = target::class.simpleName ?: target::class.java.name
        val message = target.message?.takeIf { it.isNotBlank() } ?: "no message"
        throw IllegalStateException(
            "Morphe patcher failed to load ${patchesFile.name}. $type: $message",
            target
        )
    } ?: throw IllegalStateException("Morphe patcher returned no patches for ${patchesFile.name}.")

    val loaded = when (patches) {
        is Iterable<*> -> patches.mapNotNull(::retainNamedPatch)
        is Array<*> -> patches.mapNotNull(::retainNamedPatch)
        else -> throw IllegalStateException("Unexpected Morphe patch result type: ${patches::class.java.name}")
    }

    if (loaded.isEmpty()) {
        throw IllegalStateException("No Morphe patch entries were discovered in ${patchesFile.name}.")
    }

    return loaded
}

private fun findMorpheLoadMethod(classLoader: ClassLoader): Method {
    val candidateClasses = morpheLoaderClasses(classLoader)

    return candidateClasses.asSequence()
        .flatMap { it.methods.asSequence() }
        .firstOrNull { method ->
            method.name == "loadPatchesFromJar" &&
                Modifier.isStatic(method.modifiers) &&
                method.parameterCount == 1
        }
        ?: throw NoSuchMethodException("loadPatchesFromJar(Set<File>) not found in Morphe patcher runtime.")
}

private fun morpheLoaderClasses(classLoader: ClassLoader): List<Class<*>> {
    val classpathFiles = morpheClasspathFiles()

    return classpathFiles.flatMap { jarFile ->
        if (!jarFile.extension.equals("jar", ignoreCase = true)) {
            return@flatMap emptyList()
        }

        JarFile(jarFile).use { jar ->
            jar.entries().toList()
                .filter { entry ->
                    entry.name.startsWith("app/morphe/patcher/patch/") &&
                        entry.name.endsWith(".class") &&
                        !entry.name.startsWith("META-INF/")
                }
                .mapNotNull { entry ->
                    val className = entry.name.substringBeforeLast('.').replace('/', '.')
                    try {
                        classLoader.loadClass(className)
                    } catch (_: Throwable) {
                        null
                    }
                }
        }
    }
}

private fun retainNamedPatch(candidate: Any?): Any? {
    candidate ?: return null
    return candidate.takeIf { dependencyLabel(it).isNotBlank() }
}

private fun convertMorphePatch(patch: Any): JsonObject {
    val compatiblePackages = convertMorpheCompatiblePackages(
        readMemberValue(patch, "compatiblePackages") as? Set<*> ?: emptySet<Any?>()
    )
    val dependencies = JsonArray(
        asIterable(readMemberValue(patch, "dependencies"))
            .mapNotNull(::retainNamedPatch)
            .map { JsonPrimitive(dependencyLabel(it)) }
    )
    val optionsValue = readMemberValue(patch, "options")
    val options = JsonArray(
        when (optionsValue) {
            is Map<*, *> -> optionsValue.values
            else -> asIterable(optionsValue)
        }.mapNotNull(::convertMorpheOption)
    )

    return buildJsonObject {
        put("name", JsonPrimitive(readStringMember(patch, "name").orEmpty()))
        put("description", JsonPrimitive(readStringMember(patch, "description").orEmpty()))
        put("use", JsonPrimitive(readBooleanMember(patch, "use") ?: true))
        put("dependencies", dependencies)
        put("compatiblePackages", compatiblePackages)
        put("options", options)
    }
}

private fun dependencyLabel(patch: Any): String {
    return readStringMember(patch, "name")?.takeIf { it.isNotBlank() }
        ?: patch.javaClass.simpleName.takeIf { it.isNotBlank() }
        ?: patch.javaClass.name
}

private fun convertMorpheOption(option: Any?): JsonObject? {
    option ?: return null

    val name = readStringMember(option, "name").orEmpty()
    val key = name.ifBlank { readStringMember(option, "key").orEmpty() }
    val title = readStringMember(option, "title").orEmpty().ifBlank { name.ifBlank { key } }
    val description = readStringMember(option, "description").orEmpty()
    val values = readMemberValue(option, "values") as? Map<*, *> ?: emptyMap<String, Any?>()

    return buildJsonObject {
        put("key", JsonPrimitive(key))
        put("title", JsonPrimitive(title))
        put("description", JsonPrimitive(description))
        put("required", JsonPrimitive(readBooleanMember(option, "required") ?: false))
        put("type", JsonPrimitive(readMemberValue(option, "type")?.toString() ?: "kotlin.Any"))
        put("default", toJsonValue(readMemberValue(option, "default")))
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
        when {
            entry is Map.Entry<*, *> -> {
                val name = entry.key as? String ?: continue
                mapped[name] = parseCompatibleVersions(entry.value)
            }
            entry is String -> mapped[entry] = emptyList()
            entry != null && entry.javaClass.name == "kotlin.Pair" -> {
                val name = readMemberValue(entry, "first") as? String ?: continue
                mapped[name] = parseCompatibleVersions(readMemberValue(entry, "second"))
            }
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

private fun asIterable(value: Any?): List<Any> {
    return when (value) {
        is Iterable<*> -> value.filterNotNull()
        is Array<*> -> value.filterNotNull()
        null -> emptyList()
        else -> emptyList()
    }
}

private fun readStringMember(target: Any, vararg names: String): String? {
    return readMemberValue(target, *names)?.toString()
}

private fun readBooleanMember(target: Any, vararg names: String): Boolean? {
    return when (val value = readMemberValue(target, *names)) {
        is Boolean -> value
        is String -> value.toBooleanStrictOrNull()
        else -> null
    }
}

private fun readMemberValue(target: Any, vararg names: String): Any? {
    for (name in names) {
        findAccessor(target.javaClass, name)?.let { accessor ->
            try {
                return accessor.invoke(target)
            } catch (_: Throwable) {
                // Try the next accessor candidate.
            }
        }

        target.javaClass.fields.firstOrNull { it.name == name }?.let { field ->
            try {
                return field.get(target)
            } catch (_: Throwable) {
                // Try the next accessor candidate.
            }
        }
    }

    return null
}

private fun findAccessor(type: Class<*>, name: String): Method? {
    val capitalized = name.replaceFirstChar { it.uppercaseChar() }
    val candidates = listOf(name, "get$capitalized", "is$capitalized")

    return type.methods.firstOrNull { method ->
        method.parameterCount == 0 && method.name in candidates
    }
}
