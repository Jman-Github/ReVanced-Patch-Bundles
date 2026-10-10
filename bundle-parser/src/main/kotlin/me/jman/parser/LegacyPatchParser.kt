package me.jman.parser

import java.io.File
import java.util.jar.JarFile
import kotlinx.serialization.json.*
import org.objectweb.asm.*

private const val PATCH = "Lapp/revanced/patcher/patch/annotation/Patch;"
private const val NAME = "Lapp/revanced/patcher/annotation/Name;"
private const val DESCRIPTION = "Lapp/revanced/patcher/annotation/Description;"
private const val COMPATIBILITY = "Lapp/revanced/patcher/annotation/Compatibility;"

private data class BinaryAnnotation(val descriptor: String, val values: MutableMap<String, Any?> = linkedMapOf())
private data class AnnotatedClass(val name: String, val annotationType: Boolean,
                                  val annotations: MutableList<BinaryAnnotation> = mutableListOf())

/** Read metadata without initializing old patch classes or their Android dependencies. */
private fun annotationReader(annotation: BinaryAnnotation): AnnotationVisitor =
    object : AnnotationVisitor(Opcodes.ASM9) {
        override fun visit(name: String?, value: Any?) { if (name != null) annotation.values[name] = value }
        override fun visitAnnotation(name: String?, descriptor: String): AnnotationVisitor {
            val child = BinaryAnnotation(descriptor)
            annotation.values[name.orEmpty()] = child
            return annotationReader(child)
        }
        override fun visitArray(name: String?): AnnotationVisitor {
            val values = mutableListOf<Any?>()
            annotation.values[name.orEmpty()] = values
            return object : AnnotationVisitor(Opcodes.ASM9) {
                override fun visit(name: String?, value: Any?) { values += value }
                override fun visitAnnotation(name: String?, descriptor: String): AnnotationVisitor {
                    val child = BinaryAnnotation(descriptor)
                    values += child
                    return annotationReader(child)
                }
            }
        }
    }

fun parseLegacyPatchBundle(file: File, patchClassNames: Set<String>? = null): JsonArray {
    val classes = linkedMapOf<String, AnnotatedClass>()
    JarFile(file).use { jar ->
        for (entry in jar.entries().asSequence()) {
            if (!entry.name.endsWith(".class") || entry.name.startsWith("META-INF/")) continue
            jar.getInputStream(entry).use { input ->
                ClassReader(input).accept(object : ClassVisitor(Opcodes.ASM9) {
                    private lateinit var data: AnnotatedClass
                    override fun visit(version: Int, access: Int, name: String, signature: String?,
                                       superName: String?, interfaces: Array<out String>?) {
                        data = AnnotatedClass(name.replace('/', '.'), access and Opcodes.ACC_ANNOTATION != 0)
                        classes["L$name;"] = data
                    }
                    override fun visitAnnotation(descriptor: String, visible: Boolean): AnnotationVisitor {
                        val annotation = BinaryAnnotation(descriptor)
                        data.annotations += annotation
                        return annotationReader(annotation)
                    }
                }, ClassReader.SKIP_CODE or ClassReader.SKIP_DEBUG or ClassReader.SKIP_FRAMES)
            }
        }
    }
    fun flattened(data: AnnotatedClass): List<BinaryAnnotation> {
        val result = mutableListOf<BinaryAnnotation>()
        val visited = mutableSetOf<String>()
        fun collect(annotation: BinaryAnnotation) {
            result += annotation
            if (visited.add(annotation.descriptor))
                classes[annotation.descriptor]?.annotations?.forEach(::collect)
        }
        data.annotations.forEach(::collect)
        return result
    }
    val patches = classes.values.filterNot { it.annotationType }.mapNotNull { data ->
        val annotations = flattened(data)
        val marker = annotations.firstOrNull { it.descriptor == PATCH }
        val name = (marker?.values?.get("name") ?:
            annotations.firstOrNull { it.descriptor == NAME }?.values?.get("name")) as? String
        // Loaded V3 classes are already selected by the patcher. The standalone
        // bytecode fallback still needs a metadata marker to exclude helper classes.
        if (patchClassNames != null) {
            if (data.name !in patchClassNames) return@mapNotNull null
        } else if (marker == null && annotations.none { it.descriptor in setOf(NAME, COMPATIBILITY) }) {
            return@mapNotNull null
        }
        val compatibility = marker ?: annotations.firstOrNull { it.descriptor == COMPATIBILITY }
        val packages = (compatibility?.values?.get("compatiblePackages") as? List<*>).orEmpty()
            .filterIsInstance<BinaryAnnotation>()
        val dependencies = (marker?.values?.get("dependencies") as? List<*>).orEmpty()
            .filterIsInstance<Type>().map { it.className }
        data.name to buildJsonObject {
            put("name", name?.let(::JsonPrimitive) ?: JsonNull)
            put("description", ((marker?.values?.get("description") ?:
                annotations.firstOrNull { it.descriptor == DESCRIPTION }?.values?.get("description")) as? String).orEmpty())
            put("use", marker?.values?.get("use") as? Boolean ?: true)
            put("compatiblePackages", buildJsonObject {
                packages.forEach { pkg ->
                    val packageName = pkg.values["name"] as? String ?: return@forEach
                    val versions = (pkg.values["versions"] as? List<*>).orEmpty()
                        .filterIsInstance<String>().filter(String::isNotBlank)
                    // Legacy annotations use an empty/default array for unrestricted compatibility.
                    put(packageName, if (versions.isEmpty()) JsonNull else JsonArray(versions.map(::JsonPrimitive)))
                }
            })
            put("dependencies", JsonArray(dependencies.map(::JsonPrimitive)))
            put("options", JsonArray(emptyList()))
        }
    }.toMap()
    return JsonArray(patches.values.map { patch ->
        JsonObject(patch + ("dependencies" to JsonArray(patch.getValue("dependencies").jsonArray.map {
            val className = it.jsonPrimitive.content
            val label = (patches[className]?.get("name") as? JsonPrimitive)?.contentOrNull
            JsonPrimitive(label?.takeIf { it.isNotBlank() } ?: className.substringAfterLast('.'))
        })))
    })
}
