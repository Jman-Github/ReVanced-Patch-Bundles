package me.jman.parser

import app.revanced.patcher.patch.loadPatches
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.InputStream
import java.lang.reflect.InvocationTargetException
import java.lang.reflect.Modifier
import java.net.URI
import java.net.URL
import java.net.URLClassLoader
import java.util.jar.JarFile

private const val LEGACY_PATCHER_CLASSPATH_PROPERTY = "revanced.patcher21.classpath"

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
    }.getInputStream().use { input: InputStream ->
        outputFile.outputStream().use { fileOut ->
            input.copyTo(fileOut)
        }
    }

fun generatePatchesFromUrl(uri: URI): String{
    val patchesFile = File.createTempFile("patches", ".jar")
    try {
        downloadToFile(uri.toURL(), patchesFile)

        val serializedJson = ByteArrayOutputStream().apply {
            loadPatches(patchesFile) { file, throwable ->
                throw IllegalStateException("Failed to load patches from ${file.name}", throwable)
            }.serializeTo(this, false)
        }.toString(Charsets.UTF_8)

        return serializedJson
    } finally {
        patchesFile.delete()
    }
}

fun generatePatchesFromUrlWithLegacyPatcher(uri: URI): String {
    val classpathProperty = System.getProperty(LEGACY_PATCHER_CLASSPATH_PROPERTY)
        ?.takeIf { it.isNotBlank() }
        ?: throw IllegalStateException("Legacy patcher classpath is not configured.")

    val classpathFiles = classpathProperty
        .split(File.pathSeparator)
        .map { it.trim() }
        .filter { it.isNotEmpty() }
        .map(::File)
        .filter(File::exists)

    if (classpathFiles.isEmpty()) {
        throw IllegalStateException("Legacy patcher classpath is empty.")
    }

    val patchesFile = File.createTempFile("patches-legacy", ".jar")
    try {
        downloadToFile(uri.toURL(), patchesFile)

        URLClassLoader(classpathFiles.map { it.toURI().toURL() }.toTypedArray(), null).use { classLoader ->
            try {
                val patches = loadLegacyPatchesFromJar(patchesFile, classLoader)

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
    } finally {
        patchesFile.delete()
    }
}

private fun loadLegacyPatchesFromJar(
    patchesFile: File,
    legacyClassLoader: ClassLoader
): Set<Any> {
    val patchClass = Class.forName("app.revanced.patcher.patch.Patch", true, legacyClassLoader)
    val getPatchName = patchClass.methods.firstOrNull { it.name == "getName" && it.parameterCount == 0 }
        ?: throw NoSuchMethodException("Patch.getName() not found in legacy patcher.")

    val classNames = JarFile(patchesFile).use { jar ->
        jar.entries().toList()
            .filter { it.name.endsWith(".class") && !it.name.startsWith("META-INF/") }
            .map { it.name.substringBeforeLast('.').replace('/', '.') }
    }

    URLClassLoader(arrayOf(patchesFile.toURI().toURL()), legacyClassLoader).use { bundleClassLoader ->
        val patches = linkedSetOf<Any>()

        for (className in classNames) {
            val loadedClass = try {
                bundleClassLoader.loadClass(className)
            } catch (_: Throwable) {
                continue
            }

            loadedClass.methods
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

            loadedClass.fields
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
