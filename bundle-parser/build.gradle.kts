plugins {
    alias(libs.plugins.kotlin)
    alias(libs.plugins.kotlin.serialization)
    application
}

val hardcodedGprUser = ""
val hardcodedGprToken = ""
val gprUser: String? = providers.gradleProperty("gpr.user").orNull
val gprKey: String? = providers.gradleProperty("gpr.key").orNull

repositories {
    mavenCentral()
    google()
    maven { url = uri("https://jitpack.io") }

    maven {
        name = "GitHubPackages"
        url = uri("https://maven.pkg.github.com/revanced/registry")
        credentials {
            username = when {
                hardcodedGprUser.isNotBlank() -> hardcodedGprUser
                !gprUser.isNullOrBlank() -> gprUser
                else -> System.getenv("GITHUB_ACTOR")
            }
            password = when {
                hardcodedGprToken.isNotBlank() -> hardcodedGprToken
                !gprKey.isNullOrBlank() -> gprKey
                else -> System.getenv("GITHUB_TOKEN")
            }
        }
    }
    maven {
        name = "ReVancedPatcherPackages"
        url = uri("https://maven.pkg.github.com/revanced/revanced-patcher")
        credentials {
            username = when {
                hardcodedGprUser.isNotBlank() -> hardcodedGprUser
                !gprUser.isNullOrBlank() -> gprUser
                else -> System.getenv("GITHUB_ACTOR")
            }
            password = when {
                hardcodedGprToken.isNotBlank() -> hardcodedGprToken
                !gprKey.isNullOrBlank() -> gprKey
                else -> System.getenv("GITHUB_TOKEN")
            }
        }
    }
    maven {
        name = "ReVancedLibraryPackages"
        url = uri("https://maven.pkg.github.com/revanced/revanced-library")
        credentials {
            username = when {
                hardcodedGprUser.isNotBlank() -> hardcodedGprUser
                !gprUser.isNullOrBlank() -> gprUser
                else -> System.getenv("GITHUB_ACTOR")
            }
            password = when {
                hardcodedGprToken.isNotBlank() -> hardcodedGprToken
                !gprKey.isNullOrBlank() -> gprKey
                else -> System.getenv("GITHUB_TOKEN")
            }
        }
    }
    maven {
        name = "MorphePackages"
        url = uri("https://maven.pkg.github.com/MorpheApp/registry")
        credentials {
            username = when {
                hardcodedGprUser.isNotBlank() -> hardcodedGprUser
                !gprUser.isNullOrBlank() -> gprUser
                else -> System.getenv("GITHUB_ACTOR")
            }
            password = when {
                hardcodedGprToken.isNotBlank() -> hardcodedGprToken
                !gprKey.isNullOrBlank() -> gprKey
                else -> System.getenv("GITHUB_TOKEN")
            }
        }
    }
}

dependencies {
    implementation(libs.kotlinx.serialization.json)
    implementation(libs.kotlin.stdlib)
    implementation(libs.morphe.patcher)
    implementation(libs.revanced.patcher)
    implementation(libs.asm)
    implementation(libs.smali)
    compileOnly(libs.jsr305)
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
