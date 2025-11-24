@file:Suppress("unused")

package app.revanced.patcher

/**
 * Compatibility shim for patches compiled against newer ReVanced Patcher builds
 * that added an overload without the fuzzyThreshold parameter.
 *
 * This project still depends on an older artifact so we provide the exact API
 * surface expected by the patches. Remove once the dependency can be upgraded.
 */
fun fingerprint(
    block: FingerprintBuilder.() -> Unit,
): Fingerprint = fingerprint(0, block)
