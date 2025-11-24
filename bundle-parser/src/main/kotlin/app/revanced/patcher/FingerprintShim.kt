@file:JvmName("FingerprintKt")
@file:Suppress("unused")

package app.revanced.patcher

import kotlin.jvm.functions.Function1

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

@JvmName("fingerprint\$default")
fun fingerprintDefault(
    fuzzyPatternScanThreshold: Int,
    block: Function1<FingerprintBuilder, Unit>,
    mask: Int,
    ignored: Any?,
): Fingerprint {
    val threshold = if (mask and 0x1 != 0) 0 else fuzzyPatternScanThreshold
    val builderBlock: FingerprintBuilder.() -> Unit = { block.invoke(this) }
    return fingerprint(threshold, builderBlock)
}
