package me.jman.parser

import kotlinx.serialization.json.JsonArray
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import org.objectweb.asm.AnnotationVisitor
import org.objectweb.asm.ClassReader
import org.objectweb.asm.ClassVisitor
import org.objectweb.asm.Opcodes
import org.objectweb.asm.Type
import java.io.File
import java.util.jar.JarFile

private const val PATCH_ANNOTATION_DESCRIPTOR = "Lapp/revanced/patcher/patch/annotation/Patch;"
private const val COMPATIBLE_PACKAGE_DESCRIPTOR =
    "Lapp/revanced/patcher/patch/annotation/CompatiblePackage;"

private data class LegacyPatch(
    val className: String,
    val name: String,
    val description: String?,
    val use: Boolean,
    val compatiblePackages: Map<String, List<String>>,
    val dependencyClassNames: List<String>
) {
    fun toJson(allPatches: Map<String, LegacyPatch>): JsonElement {
        val compatiblePackagesJson = buildJsonObject {
            for ((pkg, versions) in compatiblePackages) {
                put(pkg, JsonArray(versions.map(::JsonPrimitive)))
            }
        }
        val dependencyNames = dependencyClassNames.map { dependency ->
            allPatches[dependency]?.name ?: dependency.substringAfterLast('.')
        }
        return buildJsonObject {
            put("name", JsonPrimitive(name))
            put("description", JsonPrimitive(description ?: ""))
            put("compatiblePackages", compatiblePackagesJson)
            put("dependencies", JsonArray(dependencyNames.map(::JsonPrimitive)))
            put("options", JsonArray(emptyList()))
            put("use", JsonPrimitive(use))
        }
    }
}

private class LegacyPatchClassVisitor : ClassVisitor(Opcodes.ASM9) {
    private var className: String = ""
    var patch: LegacyPatch? = null
        private set

    override fun visit(
        version: Int,
        access: Int,
        name: String?,
        signature: String?,
        superName: String?,
        interfaces: Array<out String>?,
    ) {
        className = name?.replace('/', '.') ?: ""
        super.visit(version, access, name, signature, superName, interfaces)
    }

    override fun visitAnnotation(descriptor: String?, visible: Boolean): AnnotationVisitor? {
        if (descriptor != PATCH_ANNOTATION_DESCRIPTOR) {
            return super.visitAnnotation(descriptor, visible)
        }
        val builder = LegacyPatchBuilder(className)
        return builder.asVisitor { built ->
            if (patch == null) {
                patch = built
            }
        }
    }
}

private data class LegacyCompatiblePackage(
    val name: String,
    val versions: List<String>
)

private class LegacyCompatiblePackageBuilder {
    private var name: String? = null
    private val versions = mutableListOf<String>()

    fun asVisitor(onComplete: (LegacyCompatiblePackage?) -> Unit): AnnotationVisitor =
        object : AnnotationVisitor(Opcodes.ASM9) {
            override fun visit(name: String?, value: Any?) {
                if (name == "name") {
                    this@LegacyCompatiblePackageBuilder.name = value as? String
                }
            }

            override fun visitArray(name: String?): AnnotationVisitor? {
                return if (name == "versions") {
                    object : AnnotationVisitor(Opcodes.ASM9) {
                        override fun visit(name: String?, value: Any?) {
                            (value as? String)?.let(versions::add)
                        }
                    }
                } else {
                    super.visitArray(name)
                }
            }

            override fun visitEnd() {
                val pkgName = name
                if (!pkgName.isNullOrBlank()) {
                    onComplete(
                        LegacyCompatiblePackage(
                            pkgName,
                            versions.filter { it.isNotBlank() }
                        )
                    )
                } else {
                    onComplete(null)
                }
            }
        }
}

private class LegacyPatchBuilder(private val className: String) {
    private var patchName: String? = null
    private var description: String? = null
    private var use: Boolean = true
    private val dependencies = mutableListOf<String>()
    private val compatiblePackages = linkedMapOf<String, LinkedHashSet<String>>()

    fun asVisitor(onComplete: (LegacyPatch?) -> Unit): AnnotationVisitor =
        object : AnnotationVisitor(Opcodes.ASM9) {
            override fun visit(name: String?, value: Any?) {
                when (name) {
                    "name" -> patchName = value as? String
                    "description" -> description = value as? String
                    "use" -> use = (value as? Boolean) ?: true
                }
            }

            override fun visitArray(name: String?): AnnotationVisitor? {
                return when (name) {
                    "dependencies" -> object : AnnotationVisitor(Opcodes.ASM9) {
                        override fun visit(name: String?, value: Any?) {
                            when (value) {
                                is Type -> dependencies.add(value.className)
                                is String -> dependencies.add(value)
                            }
                        }
                    }

                    "compatiblePackages" -> object : AnnotationVisitor(Opcodes.ASM9) {
                        override fun visitAnnotation(name: String?, descriptor: String?): AnnotationVisitor? {
                            if (descriptor != COMPATIBLE_PACKAGE_DESCRIPTOR) {
                                return super.visitAnnotation(name, descriptor)
                            }
                            val pkgBuilder = LegacyCompatiblePackageBuilder()
                            return pkgBuilder.asVisitor { pkg ->
                                if (pkg != null) {
                                    val currentVersions = compatiblePackages.getOrPut(pkg.name) {
                                        linkedSetOf()
                                    }
                                    currentVersions.addAll(pkg.versions)
                                }
                            }
                        }
                    }

                    else -> super.visitArray(name)
                }
            }

            override fun visitEnd() {
                onComplete(build())
            }
        }

    private fun build(): LegacyPatch? {
        val finalName = patchName?.takeIf { it.isNotBlank() } ?: return null
        val compat = compatiblePackages.mapValues { (_, versions) ->
            versions.toList()
        }
        return LegacyPatch(
            className = className,
            name = finalName,
            description = description,
            use = use,
            compatiblePackages = compat,
            dependencyClassNames = dependencies
        )
    }
}

fun parseLegacyPatchBundle(file: File): JsonArray {
    val patches = mutableListOf<LegacyPatch>()
    JarFile(file).use { jar ->
        val entries = jar.entries()
        while (entries.hasMoreElements()) {
            val entry = entries.nextElement()
            if (!entry.name.endsWith(".class") || entry.name.startsWith("META-INF/")) {
                continue
            }
            jar.getInputStream(entry).use { input ->
                val reader = ClassReader(input)
                val collector = LegacyPatchClassVisitor()
                reader.accept(
                    collector,
                    ClassReader.SKIP_CODE or ClassReader.SKIP_DEBUG or ClassReader.SKIP_FRAMES
                )
                collector.patch?.let(patches::add)
            }
        }
    }
    val patchesByClass = patches.associateBy { it.className }
    val jsonPatches = patches.map { it.toJson(patchesByClass) }
    return JsonArray(jsonPatches)
}
