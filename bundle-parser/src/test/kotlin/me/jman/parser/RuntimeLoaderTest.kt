package me.jman.parser

import java.io.File
import java.util.jar.JarEntry
import java.util.jar.JarOutputStream
import javax.tools.ToolProvider
import kotlin.io.path.createTempDirectory
import kotlin.test.*
import kotlinx.serialization.json.*

class RuntimeLoaderTest {
    @Test fun modernRuntimeNeedsNoPatcherInTheParentClassloader() = withRuntime(
        "app/revanced/patcher/patch/PatchKt.java",
        """package app.revanced.patcher.patch;
           public class PatchKt {
             public static java.util.List<Patch> getPatches(java.util.List<String> names, ClassLoader loader) {
               return java.util.List.of(new Patch());
             }
           }"""
    ) { jar, artifact ->
        System.setProperty("revanced.patcher22.classpath", jar.path)
        checkPatch(Json.parseToJsonElement(generatePatchesFromUrl(artifact.toURI())).jsonArray)
    }

    @Test fun v20AndV21FacadeNeedsNoModernBridgeOrSerializationLibrary() = withRuntime(
        "app/revanced/patcher/patch/PatchKt.java",
        """package app.revanced.patcher.patch;
           public class PatchKt {
             public static java.util.List<Patch> loadPatchesFromJar(java.util.Set<java.io.File> files) {
               return java.util.List.of(new Patch());
             }
           }"""
    ) { jar, artifact ->
        System.clearProperty("revanced.patcher22.classpath")
        System.setProperty("revanced.patcher21.classpath", jar.path)
        checkPatch(Json.parseToJsonElement(generatePatchesFromUrlWithLegacyPatcher(artifact.toURI())).jsonArray)
    }

    @Test fun v14ToV19LoaderReadsObjectMetadata() = withRuntime(
        "app/revanced/patcher/PatchBundleLoader.java",
        """package app.revanced.patcher;
           public class PatchBundleLoader {
             public static class Jar implements Iterable<app.revanced.patcher.patch.Patch> {
               public Jar(java.io.File[] files) {}
               public java.util.Iterator<app.revanced.patcher.patch.Patch> iterator() {
                 return java.util.List.of(new app.revanced.patcher.patch.Patch()).iterator();
               }
             }
           }"""
    ) { jar, artifact ->
        System.setProperty("revanced.patcher21.classpath", jar.path)
        checkPatch(generateV3PatchList(artifact))
    }

    @Test fun v6ToV13LoaderUsesArchivePathAndLoadPatches() = withRuntime(
        "app/revanced/patcher/util/patch/PatchBundle.java",
        """package app.revanced.patcher.util.patch;
           public class PatchBundle {
             public static class Jar {
               public Jar(String path) {}
               public java.util.List<app.revanced.patcher.patch.Patch> loadPatches() {
                 return java.util.List.of(new app.revanced.patcher.patch.Patch());
               }
             }
           }"""
    ) { jar, artifact ->
        System.setProperty("revanced.patcher21.classpath", jar.path)
        checkPatch(generateV3PatchList(artifact))
    }

    @Test fun nullableNamesRetainDescriptionsAndCompatibility() = withRuntime(
        "app/revanced/patcher/patch/PatchKt.java",
        """package app.revanced.patcher.patch;
           public class PatchKt {
             public static java.util.List<Patch> getPatches(java.util.List<String> names, ClassLoader loader) {
               return java.util.Arrays.asList(null, new Patch() {
                 public String getName() { return null; }
               });
             }
           }"""
    ) { jar, artifact ->
        System.setProperty("revanced.patcher22.classpath", jar.path)
        val patches = Json.parseToJsonElement(generatePatchesFromUrl(artifact.toURI())).jsonArray
        val patch = patches.single().jsonObject
        assertEquals(JsonNull, patch["name"])
        assertEquals("Isolated runtime", patch["description"]?.jsonPrimitive?.content)
        assertEquals(listOf("1.0"), patch.getValue("compatiblePackages").jsonObject
            .getValue("com.runtime.app").jsonArray.map { it.jsonPrimitive.content })
    }

    @Test fun emptyCollectionIsSuccessfulButNullLoaderResultIsRejected() {
        for (body in listOf("java.util.List.of()", "null")) withRuntime(
            "app/revanced/patcher/patch/PatchKt.java",
            """package app.revanced.patcher.patch;
               public class PatchKt {
                 public static java.util.List<Patch> getPatches(java.util.List<String> names, ClassLoader loader) {
                   return $body;
                 }
               }"""
        ) { jar, artifact ->
            System.setProperty("revanced.patcher22.classpath", jar.path)
            if (body == "null") assertFails { generatePatchesFromUrl(artifact.toURI()) }
            else assertEquals(JsonArray(emptyList()),
                Json.parseToJsonElement(generatePatchesFromUrl(artifact.toURI())).jsonArray)
        }
    }

    @Test fun morphePreservesUnnamedMetadataAndEmptyLists() {
        for (result in listOf("java.util.List.of()", """java.util.List.of(new app.revanced.patcher.patch.Patch() {
            public String getName() { return null; }
        })""")) withRuntime(
            "app/morphe/patcher/patch/PatchKt.java",
            """package app.morphe.patcher.patch;
               public class PatchKt {
                 public static java.util.List<app.revanced.patcher.patch.Patch> loadPatchesFromJar(java.util.Set files) {
                   return $result;
                 }
               }"""
        ) { jar, artifact ->
            System.setProperty("morphe.patcher.classpath", jar.path)
            val patches = assertNotNull(generateMorphePatchList(artifact.toURI()))
            if (result == "java.util.List.of()") assertTrue(patches.isEmpty())
            else {
                val patch = patches.single().jsonObject
                assertEquals(JsonNull, patch["name"])
                assertEquals("Isolated runtime", patch["description"]?.jsonPrimitive?.content)
                assertEquals(listOf("1.0"), patch.getValue("compatiblePackages").jsonObject
                    .getValue("com.runtime.app").jsonArray.map { it.jsonPrimitive.content })
            }
        }
    }

    @Test fun morpheIterableCompatibilityPreservesNullEmptyAndAbsentDescriptions() {
        for (collection in listOf("List", "Set"))
            for (versions in listOf("null", "java.util.Set.of()", "java.util.Set.of(\"1.0\")"))
                withRuntime(
                    "app/morphe/patcher/patch/PatchKt.java",
                    """package app.morphe.patcher.patch;
                       public class PatchKt {
                         public static java.util.List<app.revanced.patcher.patch.Patch> loadPatchesFromJar(java.util.Set files) {
                           return java.util.List.of(new app.revanced.patcher.patch.Patch());
                         }
                       }""",
                    patchSource = """package app.revanced.patcher.patch;
                        public class Patch {
                          public String getName() { return "Nullable compatibility"; }
                          public String getDescription() { return null; }
                          public java.util.$collection<Compatible> getCompatiblePackages() {
                            return java.util.$collection.of(new Compatible());
                          }
                          public static class Compatible {
                            public String getName() { return "com.runtime.app"; }
                            public java.util.Set<String> getVersions() { return $versions; }
                          }
                        }"""
                ) { jar, artifact ->
                    System.setProperty("morphe.patcher.classpath", jar.path)
                    val patch = assertNotNull(generateMorphePatchList(artifact.toURI())).single().jsonObject
                    assertEquals(JsonNull, patch["description"])
                    val compatible = patch.getValue("compatiblePackages").jsonObject.getValue("com.runtime.app")
                    when (versions) {
                        "null" -> assertEquals(JsonNull, compatible)
                        "java.util.Set.of()" -> assertEquals(JsonArray(emptyList()), compatible)
                        else -> assertEquals(listOf("1.0"), compatible.jsonArray.map { it.jsonPrimitive.content })
                    }
                }
    }

    @Test fun repeatedCompatibilityRetainsVersionsAndUnrestrictedLinksAcrossRuntimes() {
        for (morphe in listOf(false, true)) for (unrestricted in listOf(false, true)) {
            val namespace = if (morphe) "app.morphe" else "app.revanced"
            val method = if (morphe) "loadPatchesFromJar(java.util.Set files)"
                else "getPatches(java.util.List<String> names, ClassLoader loader)"
            withRuntime(
                "${namespace.replace('.', '/')}/patcher/patch/PatchKt.java",
                """package $namespace.patcher.patch;
                   public class PatchKt {
                     public static java.util.List<app.revanced.patcher.patch.Patch> $method {
                       return java.util.List.of(new app.revanced.patcher.patch.Patch());
                     }
                   }""",
                patchSource = """package app.revanced.patcher.patch;
                    public class Patch {
                      public String getName() { return "Repeated compatibility"; }
                      public String getDescription() { return null; }
                      public java.util.List<Compatible> getCompatiblePackages() {
                        return java.util.List.of(
                          new Compatible(java.util.List.of("1.0", "1.0")),
                          new Compatible(java.util.List.of("2.0", "1.0")),
                          new Compatible(${if (unrestricted) "null" else "java.util.List.of()"}));
                      }
                      public static class Compatible {
                        private final java.util.List<String> versions;
                        Compatible(java.util.List<String> versions) { this.versions = versions; }
                        public String getName() { return "com.runtime.app"; }
                        public java.util.List<String> getVersions() { return versions; }
                      }
                    }"""
            ) { jar, artifact ->
                System.setProperty(if (morphe) "morphe.patcher.classpath" else "revanced.patcher22.classpath", jar.path)
                val patches = if (morphe) assertNotNull(generateMorphePatchList(artifact.toURI()))
                    else Json.parseToJsonElement(generatePatchesFromUrl(artifact.toURI())).jsonArray
                val compatible = patches.single().jsonObject.getValue("compatiblePackages")
                val restricted = if (unrestricted) {
                    val entries = compatible.jsonArray.map { it.jsonObject }
                    assertEquals(2, entries.size)
                    assertEquals(JsonNull, entries.first().getValue("versions"))
                    entries.last().getValue("versions")
                } else compatible.jsonObject.getValue("com.runtime.app")
                assertEquals(listOf("1.0", "2.0"), restricted.jsonArray.map { it.jsonPrimitive.content })
            }
        }
    }

    private fun checkPatch(patches: JsonArray) {
        val patch = patches.single().jsonObject
        assertEquals("Runtime patch", patch["name"]?.jsonPrimitive?.content)
        assertEquals(listOf("1.0"), patch.getValue("compatiblePackages").jsonObject
            .getValue("com.runtime.app").jsonArray.map { it.jsonPrimitive.content })
    }

    private fun withRuntime(path: String, facade: String, patchSource: String? = null, run: (File, File) -> Unit) {
        val root = createTempDirectory("isolated-runtime-").toFile()
        val properties = listOf("revanced.patcher21.classpath", "revanced.patcher22.classpath", "morphe.patcher.classpath")
        val previous = properties.associateWith(System::getProperty)
        try {
            val sources = mapOf(path to facade, "app/revanced/patcher/patch/Patch.java" to (patchSource ?: """
                package app.revanced.patcher.patch;
                public class Patch {
                  public String getName() { return "Runtime patch"; }
                  public String getDescription() { return "Isolated runtime"; }
                  public java.util.Set<Compatible> getCompatiblePackages() {
                    return java.util.Set.of(new Compatible());
                  }
                  public static class Compatible {
                    public String getName() { return "com.runtime.app"; }
                    public java.util.Set<String> getVersions() { return java.util.Set.of("1.0"); }
                  }
                }
            """))
            val files = sources.map { (name, text) ->
                File(root, name).apply { parentFile.mkdirs(); writeText(text) }
            }
            val classes = File(root, "classes").apply { mkdir() }
            assertEquals(0, ToolProvider.getSystemJavaCompiler().run(null, null, null,
                "-d", classes.path, *files.map { it.path }.toTypedArray()))
            val jar = File(root, "runtime.jar")
            JarOutputStream(jar.outputStream()).use { output ->
                classes.walkTopDown().filter { it.isFile }.forEach {
                    output.putNextEntry(JarEntry(it.relativeTo(classes).invariantSeparatorsPath))
                    output.write(it.readBytes()); output.closeEntry()
                }
            }
            val artifact = File(root, "fixture.rvp")
            JarOutputStream(artifact.outputStream()).use {}
            run(jar, artifact)
        } finally {
            previous.forEach { (key, value) ->
                if (value == null) System.clearProperty(key) else System.setProperty(key, value)
            }
            root.deleteRecursively()
        }
    }
}
