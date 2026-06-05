import java.util.Properties

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
    else -> System.getenv("GITHUB_TOKEN")
}

val patcher21Runtime by configurations.creating {
    isCanBeConsumed = false
    isCanBeResolved = true
}

val patcher22Runtime by configurations.creating {
    isCanBeConsumed = false
    isCanBeResolved = true
}

val morpheRuntime by configurations.creating {
    isCanBeConsumed = false
    isCanBeResolved = true
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
    }
}

dependencies {
    implementation(libs.kotlinx.serialization.json)
    implementation(libs.kotlin.stdlib)
    implementation(libs.asm)
    implementation(libs.smali)
    compileOnly(libs.jsr305)

    patcher22Runtime(libs.revanced.patcher)
    patcher22Runtime(libs.revanced.library)
    patcher21Runtime(libs.revanced.patcher.legacy)
    patcher21Runtime(libs.revanced.library.legacy)
    morpheRuntime(libs.morphe.patcher)
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

tasks.named<JavaExec>("run") {
    doFirst {
        val modernClasspath = patcher22Runtime.files.joinToString(File.pathSeparator) { it.absolutePath }
        val legacyClasspath = patcher21Runtime.files.joinToString(File.pathSeparator) { it.absolutePath }
        val morpheClasspath = morpheRuntime.files.joinToString(File.pathSeparator) { it.absolutePath }
        systemProperty("revanced.patcher22.classpath", modernClasspath)
        systemProperty("revanced.patcher21.classpath", legacyClasspath)
        systemProperty("morphe.patcher.classpath", morpheClasspath)
    }
}

tasks.register("assembleRelease") {
    group = "build"
    description = "Alias for assemble to support CI validation on this JVM application module."
    dependsOn(tasks.named("assemble"))
}
