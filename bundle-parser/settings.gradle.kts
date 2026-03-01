rootProject.name = "bundle-parser"

pluginManagement {
    val localProperties = java.util.Properties().apply {
        val propertiesFile = sequenceOf(
            file("local.properties"),
            file("../local.properties")
        ).firstOrNull { it.isFile }

        if (propertiesFile != null) {
            propertiesFile.inputStream().use { input -> load(input) }
        }
    }
    val localGprUser = localProperties.getProperty("gpr.user")
        ?.let { value -> if (value.isNotBlank()) value else null }
    val localGprKey = localProperties.getProperty("gpr.key")
        ?.let { value -> if (value.isNotBlank()) value else null }

    repositories {
        gradlePluginPortal()
        google()
        maven {
            name = "GitHubPackages"
            url = uri("https://maven.pkg.github.com/revanced/registry")
            credentials {
                username = providers.gradleProperty("gpr.user").orNull
                    ?.takeIf { it.isNotBlank() }
                    ?: localGprUser
                    ?: System.getenv("GITHUB_ACTOR")
                password = providers.gradleProperty("gpr.key").orNull
                    ?.takeIf { it.isNotBlank() }
                    ?: localGprKey
                    ?: System.getenv("GITHUB_TOKEN")
            }
        }
    }
}
