import java.util.Properties
import groovy.json.JsonSlurper
import groovy.json.JsonOutput

plugins {
    alias(libs.plugins.kotlin)
    alias(libs.plugins.kotlin.serialization)
    application
}

val hardcodedGprUser = ""
val hardcodedGprToken = ""
val gprUser: String? = providers.gradleProperty("gpr.user").orNull
val gprKey: String? = providers.gradleProperty("gpr.key").orNull
val localProperties = Properties().apply {
    val propertiesFile = sequenceOf(
        rootDir.resolve("local.properties"),
        rootDir.parentFile?.resolve("local.properties")
    ).firstOrNull { it?.isFile == true }

    if (propertiesFile != null) {
        propertiesFile.inputStream().use(::load)
    }
}
val localGprUser: String? = localProperties.getProperty("gpr.user")?.takeIf { it.isNotBlank() }
val localGprKey: String? = localProperties.getProperty("gpr.key")?.takeIf { it.isNotBlank() }
val resolvedGprUser: String? = when {
    hardcodedGprUser.isNotBlank() -> hardcodedGprUser
    !gprUser.isNullOrBlank() -> gprUser
    !localGprUser.isNullOrBlank() -> localGprUser
    else -> System.getenv("GITHUB_ACTOR")
}
val resolvedGprKey: String? = when {
    hardcodedGprToken.isNotBlank() -> hardcodedGprToken
    !gprKey.isNullOrBlank() -> gprKey
    !localGprKey.isNullOrBlank() -> localGprKey
    else -> sequenceOf("GITHUB_PACKAGES_TOKEN", "GITHUB_TOKEN", "GIT_TOKEN")
        .mapNotNull { System.getenv(it)?.takeIf(String::isNotBlank) }.firstOrNull()
}

repositories {
    mavenCentral()
    google()
    maven {
        url = uri("https://jitpack.io")
        content {
            includeGroup("com.github.iBotPeaches.smali")
            includeGroup("com.github.MorpheApp")
            includeGroup("com.github.MorpheApp.smali")
            includeGroup("com.github.REAndroid")
        }
    }

    maven {
        name = "GitHubPackages"
        url = uri("https://maven.pkg.github.com/revanced/registry")
        content {
            includeGroup("app.revanced")
        }
        credentials {
            username = resolvedGprUser
            password = resolvedGprKey
        }
        authentication {
            create<org.gradle.authentication.http.BasicAuthentication>("basic")
        }
    }
    maven {
        name = "ReVancedPatcherPackages"
        url = uri("https://maven.pkg.github.com/revanced/revanced-patcher")
        content {
            includeGroup("app.revanced")
        }
        credentials {
            username = resolvedGprUser
            password = resolvedGprKey
        }
        authentication {
            create<org.gradle.authentication.http.BasicAuthentication>("basic")
        }
    }
    maven {
        name = "ReVancedLibraryPackages"
        url = uri("https://maven.pkg.github.com/revanced/revanced-library")
        content {
            includeGroup("app.revanced")
        }
        credentials {
            username = resolvedGprUser
            password = resolvedGprKey
        }
        authentication {
            create<org.gradle.authentication.http.BasicAuthentication>("basic")
        }
    }
    maven {
        name = "MorphePackages"
        url = uri("https://maven.pkg.github.com/MorpheApp/morphe-patcher")
        content {
            includeGroup("app.morphe")
        }
        credentials {
            username = resolvedGprUser
            password = resolvedGprKey
        }
        authentication {
            create<org.gradle.authentication.http.BasicAuthentication>("basic")
        }
    }
    maven {
        name = "MorpheRegistryPackages"
        url = uri("https://maven.pkg.github.com/MorpheApp/registry")
        content {
            includeGroup("app.morphe")
        }
        credentials {
            username = resolvedGprUser
            password = resolvedGprKey
        }
        authentication {
            create<org.gradle.authentication.http.BasicAuthentication>("basic")
        }
    }
}

dependencies {
    implementation(libs.kotlinx.serialization.json)
    implementation(libs.kotlin.stdlib)
    implementation(libs.asm)
    implementation(libs.smali)
    compileOnly(libs.jsr305)
    testImplementation(kotlin("test"))
}

kotlin {
    jvmToolchain(17)
    compilerOptions {
        freeCompilerArgs.add("-Xskip-prerelease-check")
    }
}

java {
    targetCompatibility = JavaVersion.VERSION_17
    sourceCompatibility = JavaVersion.VERSION_17
}

application {
    mainClass.set("me.jman.parser.MainKt")
}

tasks.register("assembleRelease") {
    group = "build"
    description = "Alias for assemble to support CI validation on this JVM application module."
    dependsOn(tasks.named("assemble"))
}

// Each configuration resolves independently; an unavailable runtime is recorded, not fatal.
@Suppress("UNCHECKED_CAST")
val configuredRuntimes = (JsonSlurper().parse(rootDir.parentFile.resolve("config/patcher-runtimes.json"))
    as Map<String, Any>)["runtimes"] as List<Map<String, Any>>
val configurableRuntimeDependencies = configuredRuntimes.associate { runtime ->
    val id = runtime["id"] as String
    require(id.matches(Regex("[a-z0-9-]+"))) { "Invalid runtime id" }
    val configuration = configurations.create("catalogRuntime_" + id.replace("-", "_")) {
        isCanBeConsumed = false
        isCanBeResolved = true
    }
    (runtime["dependencies"] as List<*>).forEach { coordinate ->
        dependencies.add(configuration.name, coordinate as String)
    }
    id to configuration
}
val runtimeManifest = layout.buildDirectory.file("runtime-classpaths.json")
val prepareCatalogRuntimes = tasks.register("prepareCatalogRuntimes") {
    inputs.file(rootDir.parentFile.resolve("config/patcher-runtimes.json"))
    outputs.file(runtimeManifest)
    outputs.upToDateWhen { false } // Retry runtime artifact outages on the next workflow run.
    doLast {
        val installed = configurableRuntimeDependencies.mapValues { (id, configuration) ->
            try {
                mapOf("available" to true,
                      "classpath" to configuration.files.joinToString(File.pathSeparator) { it.absolutePath })
            } catch (failure: Exception) {
                logger.warn("Runtime {} unavailable ({}). GitHub Packages requires a valid token with read:packages; " +
                    "set GITHUB_PACKAGES_TOKEN or gpr.key.", id, failure.javaClass.simpleName)
                mapOf("available" to false, "classpath" to "")
            }
        }
        runtimeManifest.get().asFile.apply {
            parentFile.mkdirs()
            writeText(JsonOutput.prettyPrint(JsonOutput.toJson(installed)))
        }
    }
}
tasks.named<JavaExec>("run") {
    dependsOn(prepareCatalogRuntimes)
    doFirst {
        systemProperty("catalog.runtime.config", rootDir.parentFile.resolve("config/patcher-runtimes.json"))
        systemProperty("catalog.runtime.manifest", runtimeManifest.get().asFile)
    }
}
tasks.named<Test>("test") {
    dependsOn(tasks.named("installDist"))
}
val runtimeSmoke = tasks.register<Exec>("runtimeSmoke") {
    group = "verification"
    description = "Validate runtime isolation, deadlines and extraction failure handling."
    dependsOn(tasks.named("installDist"), prepareCatalogRuntimes)
    workingDir(rootDir.parentFile)
    commandLine(providers.environmentVariable("PYTHON").orElse("python").get(), "scripts/runtime_smoke.py")
}
tasks.named("assembleRelease") {
    dependsOn(tasks.named("test"), runtimeSmoke)
}
