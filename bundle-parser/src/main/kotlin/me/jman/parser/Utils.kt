package me.jman.parser

import java.io.ByteArrayOutputStream
import java.io.File
import java.io.InputStream
import java.lang.reflect.InvocationTargetException
import java.lang.reflect.Method
import java.lang.reflect.Modifier
import java.net.URI
import java.net.URL
import java.net.URLClassLoader
import java.util.jar.JarFile
import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject

private const val PATCHER22_CLASSPATH_PROPERTY = "revanced.patcher22.classpath"
private const val LEGACY_PATCHER_CLASSPATH_PROPERTY = "revanced.patcher21.classpath"
private const val GITHUB_DOWNLOAD_USER_AGENT =
    "revanced-patch-bundles/1.0 (+https://github.com/Jman-Github/ReVanced-Patch-Bundles)"

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
        setRequestProperty("User-Agent", GITHUB_DOWNLOAD_USER_AGENT)
    }.getInputStream().use { input: InputStream ->
        outputFile.outputStream().use { fileOut ->
            input.copyTo(fileOut)
        }
    }

fun generatePatchesFromUrl(uri: URI): String {
    val classpathFiles = runtimeClasspathFiles(
        PATCHER22_CLASSPATH_PROPERTY,
        "Modern patcher 22 classpath"
    )
    val patchesFile = File.createTempFile("patches-modern", ".jar")
    try {
        downloadToFile(uri.toURL(), patchesFile)

        URLClassLoader(
            classpathFiles.map { it.toURI().toURL() }.toTypedArray(),
            Class.forName("app.revanced.patcher.Fingerprint").classLoader
        ).use { classLoader ->
            val patches = loadModernPatchesFromJar(patchesFile, classLoader, classpathFiles)
            return JsonArray(patches.map(::convertRevancedPatch)).toString()
        }
    } finally {
        patchesFile.delete()
    }
}

fun generatePatchesFromUrlWithLegacyPatcher(uri: URI): String {
    val classpathFiles = runtimeClasspathFiles(
        LEGACY_PATCHER_CLASSPATH_PROPERTY,
        "Legacy patcher classpath"
    )
    val bridgeClasspathFiles = runtimeClasspathFiles(
        PATCHER22_CLASSPATH_PROPERTY,
        "Modern patcher 22 classpath"
    )
    val patchesFile = File.createTempFile("patches-legacy", ".jar")
    try {
        downloadToFile(uri.toURL(), patchesFile)

        URLClassLoader(classpathFiles.map { it.toURI().toURL() }.toTypedArray(), null).use { classLoader ->
            URLClassLoader(bridgeClasspathFiles.map { it.toURI().toURL() }.toTypedArray(), classLoader).use { bridgeClassLoader ->
                try {
                    val patches = loadLegacyPatchesFromJar(patchesFile, classLoader, bridgeClassLoader)

                    val serializationClass = Class.forName("app.revanced.library.SerializationKt", true, classLoader)
                    val serializeMethod = serializationClass.methods.firstOrNull {
                        it.name == "serializeTo" && it.parameterCount == 3
                    } ?: throw NoSuchMethodException("serializeTo(Set, OutputStream, Boolean) not found in legacy library.")

                    val output = ByteArrayOutputStream()
                    serializeMethod.invoke(null, patches, output, false)
                    return output.toString(Charsets.UTF_8)
                } catch (e: InvocationTargetException) {
                    val target = e.targetException ?: e
                    throw IllegalStateException("Legacy patcher failed to load ${patchesFile.name}", target)
                }
            }
        }
    } finally {
        patchesFile.delete()
    }
}

private fun runtimeClasspathFiles(propertyName: String, displayName: String): List<File> {
    val classpathProperty = System.getProperty(propertyName)
        ?.takeIf { it.isNotBlank() }
        ?: throw IllegalStateException("$displayName is not configured.")

    val classpathFiles = classpathProperty
        .split(File.pathSeparator)
        .map { it.trim() }
        .filter { it.isNotEmpty() }
        .map(::File)
        .filter(File::exists)

    if (classpathFiles.isEmpty()) {
        throw IllegalStateException("$displayName is empty.")
    }

    return classpathFiles
}

private fun loadModernPatchesFromJar(
    patchesFile: File,
    modernClassLoader: ClassLoader,
    classpathFiles: List<File>
): List<Any> {
    val loadMethods = findStaticMethodsInPackage(
        classLoader = modernClassLoader,
        classpathFiles = classpathFiles,
        packagePathPrefix = "app/revanced/patcher/patch/",
        methodName = "loadPatches"
    ) { method ->
        method.isModernLoadPatchesWithClassLoader() || method.isModernLoadPatchesDefault()
    }
    val loadMethod = loadMethods.firstOrNull(Method::isModernLoadPatchesWithClassLoader)
        ?: loadMethods.firstOrNull(Method::isModernLoadPatchesDefault)
        ?: throw NoSuchMethodException("loadPatches was not found in app/revanced/patcher/patch/.")

    val patches = try {
        invokeModernLoadPatches(loadMethod, patchesFile, modernClassLoader)
    } catch (e: InvocationTargetException) {
        val target = e.targetException ?: e
        throw IllegalStateException("Modern patcher failed to load ${patchesFile.name}", target)
    } ?: throw IllegalStateException("Modern patcher returned no patches for ${patchesFile.name}.")

    val loaded = asReflectiveList(patches).mapNotNull(::retainNamedPatch)
    if (loaded.isEmpty()) {
        throw IllegalStateException("No patch entries were discovered in ${patchesFile.name}.")
    }
    return loaded
}

private fun Method.isModernLoadPatchesDefault(): Boolean =
    parameterCount == 2 &&
        isFileOrFileArray(parameterTypes[0])

private fun Method.isModernLoadPatchesWithClassLoader(): Boolean =
    parameterCount == 4 &&
        isFileOrFileArray(parameterTypes[0]) &&
        ClassLoader::class.java.isAssignableFrom(parameterTypes[2])

private fun isFileOrFileArray(type: Class<*>): Boolean =
    type == File::class.java ||
        (type.isArray && type.componentType == File::class.java)

private fun invokeModernLoadPatches(
    loadMethod: Method,
    patchesFile: File,
    modernClassLoader: ClassLoader
): Any? {
    val patchesFileArgument: Any = if (loadMethod.parameterTypes[0].isArray) {
        arrayOf(patchesFile)
    } else {
        patchesFile
    }
    val onFailedToLoad = { file: File, throwable: Throwable? ->
        throw IllegalStateException("Failed to load patches from ${file.name}", throwable)
    }

    if (loadMethod.isModernLoadPatchesWithClassLoader()) {
        val getBinaryClassNames = { file: File -> readJarClassNames(file) }
        URLClassLoader(arrayOf(patchesFile.toURI().toURL()), modernClassLoader).use { bundleClassLoader ->
            return loadMethod.invoke(
                null,
                patchesFileArgument,
                getBinaryClassNames,
                bundleClassLoader,
                onFailedToLoad
            )
        }
    }

    return loadMethod.invoke(null, patchesFileArgument, onFailedToLoad)
}

private fun readJarClassNames(file: File): List<String> =
    JarFile(file).use { jar ->
        jar.entries().toList()
            .filter { entry ->
                entry.name.endsWith(".class") && !entry.name.startsWith("META-INF/")
            }
            .map { entry -> entry.name.substringBeforeLast('.').replace('/', '.') }
    }

private fun findStaticMethodInPackage(
    classLoader: ClassLoader,
    classpathFiles: List<File>,
    packagePathPrefix: String,
    methodName: String,
    predicate: (Method) -> Boolean
): Method {
    return findStaticMethodsInPackage(classLoader, classpathFiles, packagePathPrefix, methodName, predicate)
        .firstOrNull()
        ?: throw NoSuchMethodException("$methodName was not found in $packagePathPrefix.")
}

private fun findStaticMethodsInPackage(
    classLoader: ClassLoader,
    classpathFiles: List<File>,
    packagePathPrefix: String,
    methodName: String,
    predicate: (Method) -> Boolean
): List<Method> =
    loadClassesFromPackage(classLoader, classpathFiles, packagePathPrefix)
        .asSequence()
        .flatMap { it.methods.asSequence() }
        .filter { method ->
            method.name == methodName &&
                Modifier.isStatic(method.modifiers) &&
                predicate(method)
        }
        .toList()

private fun loadClassesFromPackage(
    classLoader: ClassLoader,
    classpathFiles: List<File>,
    packagePathPrefix: String
): List<Class<*>> {
    return classpathFiles.flatMap { jarFile ->
        if (!jarFile.extension.equals("jar", ignoreCase = true)) {
            return@flatMap emptyList()
        }

        JarFile(jarFile).use { jar ->
            jar.entries().toList()
                .filter { entry ->
                    entry.name.startsWith(packagePathPrefix) &&
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

private fun convertRevancedPatch(patch: Any): JsonObject {
    val compatiblePackages = convertRevancedCompatiblePackages(readReflectiveMemberValue(patch, "compatiblePackages"))
    val dependencies = JsonArray(
        asReflectiveList(readReflectiveMemberValue(patch, "dependencies"))
            .mapNotNull(::retainNamedPatch)
            .map { JsonPrimitive(patchLabel(it)) }
    )
    val optionsValue = readReflectiveMemberValue(patch, "options")
    val options = JsonArray(
        when (optionsValue) {
            is Map<*, *> -> optionsValue.values
            else -> asReflectiveList(optionsValue)
        }.mapNotNull(::convertRevancedOption)
    )

    return buildJsonObject {
        put("name", JsonPrimitive(readReflectiveString(patch, "name").orEmpty()))
        put("description", toJsonElement(readReflectiveMemberValue(patch, "description")))
        put("use", JsonPrimitive(readReflectiveBoolean(patch, "use") ?: true))
        put("dependencies", dependencies)
        put("compatiblePackages", compatiblePackages)
        put("options", options)
    }
}

private fun convertRevancedOption(option: Any?): JsonObject? {
    option ?: return null

    val name = readReflectiveString(option, "name").orEmpty()
    val values = readReflectiveMemberValue(option, "values") as? Map<*, *> ?: emptyMap<String, Any?>()

    return buildJsonObject {
        put("name", JsonPrimitive(name))
        put("description", toJsonElement(readReflectiveMemberValue(option, "description")))
        put("required", JsonPrimitive(readReflectiveBoolean(option, "required") ?: false))
        put("type", JsonPrimitive(readReflectiveMemberValue(option, "type")?.toString() ?: "kotlin.Any"))
        put("default", toJsonElement(readReflectiveMemberValue(option, "default")))
        put("values", if (values.isEmpty()) JsonNull else mapToJsonObject(values))
    }
}

private fun convertRevancedCompatiblePackages(value: Any?): JsonElement {
    return when (value) {
        is Map<*, *> -> mapCompatiblePackages(value)
        is Iterable<*> -> iterableCompatiblePackages(value)
        else -> JsonNull
    }
}

private fun mapCompatiblePackages(compatiblePackages: Map<*, *>): JsonElement {
    if (compatiblePackages.isEmpty()) return JsonNull

    return buildJsonObject {
        for ((rawPackageName, rawVersions) in compatiblePackages) {
            val packageName = rawPackageName?.toString()?.takeIf(String::isNotBlank) ?: continue
            put(packageName, toCompatibleVersions(rawVersions))
        }
    }
}

private fun iterableCompatiblePackages(compatiblePackages: Iterable<*>): JsonElement {
    val entries = compatiblePackages.mapNotNull { entry ->
        val pair = entry as? Pair<*, *> ?: return@mapNotNull null
        val packageName = pair.first?.toString()?.takeIf(String::isNotBlank) ?: return@mapNotNull null
        packageName to pair.second
    }
    if (entries.isEmpty()) return JsonNull

    return buildJsonObject {
        for ((packageName, rawVersions) in entries) {
            put(packageName, toCompatibleVersions(rawVersions))
        }
    }
}

private fun toCompatibleVersions(rawVersions: Any?): JsonElement {
    if (rawVersions == null) return JsonNull

    val versions = when (rawVersions) {
        is Iterable<*> -> rawVersions
        is Array<*> -> rawVersions.asIterable()
        else -> listOf(rawVersions)
    }.mapNotNull { version -> version?.toString()?.takeIf(String::isNotBlank) }

    return JsonArray(versions.map(::JsonPrimitive))
}

private fun patchLabel(patch: Any): String {
    return readReflectiveString(patch, "name")?.takeIf { it.isNotBlank() }
        ?: patch.javaClass.simpleName.takeIf { it.isNotBlank() }
        ?: patch.javaClass.name
}

private fun retainNamedPatch(candidate: Any?): Any? {
    candidate ?: return null
    return candidate.takeIf { patchLabel(it).isNotBlank() }
}

private fun toJsonElement(value: Any?): JsonElement {
    return when (value) {
        null -> JsonNull
        is String -> JsonPrimitive(value)
        is Number -> JsonPrimitive(value)
        is Boolean -> JsonPrimitive(value)
        is Iterable<*> -> JsonArray(value.map(::toJsonElement))
        is Array<*> -> JsonArray(value.map(::toJsonElement))
        is Map<*, *> -> mapToJsonObject(value)
        else -> JsonPrimitive(value.toString())
    }
}

private fun mapToJsonObject(values: Map<*, *>): JsonObject {
    val mapped = values.entries.mapNotNull { (rawKey, rawValue) ->
        val key = rawKey?.toString()?.takeIf(String::isNotBlank) ?: return@mapNotNull null
        key to toJsonElement(rawValue)
    }.toMap()
    return JsonObject(mapped)
}

private fun asReflectiveList(value: Any?): List<Any> {
    return when (value) {
        is Iterable<*> -> value.filterNotNull()
        is Array<*> -> value.filterNotNull()
        null -> emptyList()
        else -> emptyList()
    }
}

private fun readReflectiveString(target: Any, vararg names: String): String? {
    return readReflectiveMemberValue(target, *names)?.toString()
}

private fun readReflectiveBoolean(target: Any, vararg names: String): Boolean? {
    return when (val value = readReflectiveMemberValue(target, *names)) {
        is Boolean -> value
        is String -> value.toBooleanStrictOrNull()
        else -> null
    }
}

private fun readReflectiveMemberValue(target: Any, vararg names: String): Any? {
    for (name in names) {
        findReflectiveAccessor(target.javaClass, name)?.let { accessor ->
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

private fun findReflectiveAccessor(type: Class<*>, name: String): Method? {
    val capitalized = name.replaceFirstChar { it.uppercaseChar() }
    val candidates = listOf(name, "get$capitalized", "is$capitalized")

    return type.methods.firstOrNull { method ->
        method.parameterCount == 0 && method.name in candidates
    }
}

private fun loadLegacyPatchesFromJar(
    patchesFile: File,
    legacyClassLoader: ClassLoader,
    bundleDependencyClassLoader: ClassLoader
): Set<Any> {
    val patchClass = Class.forName("app.revanced.patcher.patch.Patch", true, legacyClassLoader)
    val getPatchName = patchClass.methods.firstOrNull { it.name == "getName" && it.parameterCount == 0 }
        ?: throw NoSuchMethodException("Patch.getName() not found in legacy patcher.")

    val classNames = JarFile(patchesFile).use { jar ->
        jar.entries().toList()
            .filter { it.name.endsWith(".class") && !it.name.startsWith("META-INF/") }
            .map { it.name.substringBeforeLast('.').replace('/', '.') }
    }

    URLClassLoader(arrayOf(patchesFile.toURI().toURL()), bundleDependencyClassLoader).use { bundleClassLoader ->
        val patches = linkedSetOf<Any>()

        for (className in classNames) {
            val loadedClass = try {
                bundleClassLoader.loadClass(className)
            } catch (_: Throwable) {
                continue
            }

            val publicMethods = try {
                loadedClass.methods.toList()
            } catch (_: LinkageError) {
                continue
            }

            publicMethods
                .filter { method ->
                    Modifier.isPublic(method.modifiers) &&
                        Modifier.isStatic(method.modifiers) &&
                        method.parameterCount == 0 &&
                        patchClass.isAssignableFrom(method.returnType)
                }
                .forEach { method ->
                    try {
                        val patch = method.invoke(null) ?: return@forEach
                        val name = getPatchName.invoke(patch) as? String
                        if (!name.isNullOrBlank()) {
                            patches += patch
                        }
                    } catch (_: Throwable) {
                        // Ignore per-entry load errors so other patches can still be parsed.
                    }
                }

            val publicFields = try {
                loadedClass.fields.toList()
            } catch (_: LinkageError) {
                continue
            }

            publicFields
                .filter { field ->
                    Modifier.isPublic(field.modifiers) &&
                        Modifier.isStatic(field.modifiers) &&
                        patchClass.isAssignableFrom(field.type)
                }
                .forEach { field ->
                    try {
                        val patch = field.get(null) ?: return@forEach
                        val name = getPatchName.invoke(patch) as? String
                        if (!name.isNullOrBlank()) {
                            patches += patch
                        }
                    } catch (_: Throwable) {
                        // Ignore per-entry load errors so other patches can still be parsed.
                    }
                }
        }

        if (patches.isEmpty()) {
            throw IllegalStateException("No legacy patch entries were discovered in ${patchesFile.name}.")
        }

        return patches
    }
}
