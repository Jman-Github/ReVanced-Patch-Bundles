package me.jman.parser

import java.io.File
import java.util.jar.JarEntry
import java.util.jar.JarOutputStream
import kotlin.io.path.createTempDirectory
import kotlin.test.*
import kotlinx.serialization.json.*
import org.objectweb.asm.*

class LegacyPatchParserTest {
    @Test fun oldMetadataCanBeNestedInCustomAnnotations() {
        withArchive { jar ->
            addClass(jar, "demo/Metadata", annotationType = true) {
                visitAnnotation("Ldemo/Metadata;", true).visitEnd() // Cycle must terminate.
                visitAnnotation("Lapp/revanced/patcher/annotation/Name;", true).apply {
                    visit("name", "Old patch"); visitEnd()
                }
                visitAnnotation("Lapp/revanced/patcher/annotation/Description;", true).apply {
                    visit("description", "Older metadata"); visitEnd()
                }
                visitAnnotation("Lapp/revanced/patcher/annotation/Compatibility;", true).apply {
                    visitArray("compatiblePackages").apply {
                        visitAnnotation(null, "Lapp/revanced/patcher/annotation/Package;").apply {
                            visit("name", "com.old.app")
                            visitArray("versions").apply { visit(null, "1.2.3"); visitEnd() }
                            visitEnd()
                        }
                        visitEnd()
                    }
                    visitEnd()
                }
            }
            addClass(jar, "demo/OldPatch") {
                visitAnnotation("Ldemo/Metadata;", true).visitEnd()
            }
        }.also { patches ->
            assertEquals(1, patches.size)
            val patch = patches.single().jsonObject
            assertEquals("Old patch", patch.getValue("name").jsonPrimitive.content)
            assertEquals("Older metadata", patch.getValue("description").jsonPrimitive.content)
            assertEquals(listOf("1.2.3"), patch.getValue("compatiblePackages").jsonObject
                .getValue("com.old.app").jsonArray.map { it.jsonPrimitive.content })
        }
    }

    @Test fun directAnnotationsKeepDependenciesAndUnrestrictedPackages() {
        withArchive { jar ->
            for (name in listOf("Dependency", "Patch")) addClass(jar, "demo/$name") {
                visitAnnotation("Lapp/revanced/patcher/patch/annotation/Patch;", true).apply {
                    if (name == "Patch") visit("name", name)
                    if (name == "Patch") {
                        visit("use", false)
                        visitArray("dependencies").apply {
                            visit(null, Type.getObjectType("demo/Dependency")); visitEnd()
                        }
                        visitArray("compatiblePackages").apply {
                            visitAnnotation(null, "Lapp/revanced/patcher/patch/annotation/CompatiblePackage;").apply {
                                visit("name", "com.any.version"); visitEnd()
                            }
                            visitEnd()
                        }
                    }
                    visitEnd()
                }
            }
        }.also { patches ->
            assertEquals(2, patches.size)
            assertEquals(1, patches.count { it.jsonObject["name"] == JsonNull })
            val patch = patches.map { it.jsonObject }.single { it["name"]?.jsonPrimitive?.content == "Patch" }
            assertEquals(false, patch["use"]?.jsonPrimitive?.boolean)
            assertEquals("Dependency", patch["dependencies"]?.jsonArray?.single()?.jsonPrimitive?.content)
            assertEquals(JsonNull, patch["compatiblePackages"]?.jsonObject?.get("com.any.version"))
        }
    }

    @Test fun unnamedAnnotatedPatchesRetainMetadataAndExcludeHelpers() {
        val patches = withArchive { jar ->
            addClass(jar, "demo/Helper") {}
            addClass(jar, "demo/Unnamed") {
                visitAnnotation("Lapp/revanced/patcher/patch/annotation/Patch;", true).apply {
                    visit("description", "Unnamed legacy patch")
                    visitEnd()
                }
            }
        }
        assertEquals(JsonNull, patches.single().jsonObject["name"])
        assertEquals("Unnamed legacy patch", patches.single().jsonObject["description"]?.jsonPrimitive?.content)
    }

    private fun withArchive(write: (JarOutputStream) -> Unit): JsonArray {
        val root = createTempDirectory("legacy-metadata-").toFile()
        try {
            val file = File(root, "patches.jar")
            JarOutputStream(file.outputStream()).use(write)
            return parseLegacyPatchBundle(file)
        } finally { root.deleteRecursively() }
    }

    private fun addClass(jar: JarOutputStream, name: String, annotationType: Boolean = false,
                         annotations: ClassWriter.() -> Unit) {
        val writer = ClassWriter(0)
        writer.visit(Opcodes.V11, Opcodes.ACC_PUBLIC or
            (if (annotationType) Opcodes.ACC_ANNOTATION or Opcodes.ACC_INTERFACE or Opcodes.ACC_ABSTRACT else 0),
            name, null, "java/lang/Object", null)
        writer.annotations()
        writer.visitEnd()
        jar.putNextEntry(JarEntry("$name.class")); jar.write(writer.toByteArray()); jar.closeEntry()
    }
}
