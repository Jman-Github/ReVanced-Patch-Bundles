@file:JvmName("FingerprintKt")
@file:Suppress("unused")

package app.revanced.patcher

import kotlin.jvm.functions.Function1

private class CompatFingerprintBuilder(
    private var fuzzyPatternScanThreshold: Int = 0,
) : FingerprintBuilder() {
    init {
        fuzzyPatternScanThreshold(fuzzyPatternScanThreshold)
    }

    fun setFuzzyPatternScanThreshold(value: Int) {
        fuzzyPatternScanThreshold = value
        fuzzyPatternScanThreshold(value)
    }

    fun buildFingerprint(): Fingerprint = build()
}

/**
 * Compatibility shim for patches compiled against newer ReVanced Patcher builds
 * that added an overload without the fuzzyThreshold parameter.
 *
 * This project still depends on an older artifact so we provide the exact API
 * surface expected by the patches. Remove once the dependency can be upgraded.
 */
fun fingerprint(
    block: FingerprintBuilder.() -> Unit,
): Fingerprint = CompatFingerprintBuilder().apply(block).buildFingerprint()

fun fingerprint(
    fuzzyPatternScanThreshold: Int,
    block: Function1<FingerprintBuilder, Unit>,
): Fingerprint = CompatFingerprintBuilder(fuzzyPatternScanThreshold).apply { block.invoke(this) }.buildFingerprint()

@JvmName("fingerprint\$default")
fun fingerprintDefault(
    fuzzyPatternScanThreshold: Int,
    block: Function1<FingerprintBuilder, Unit>,
    mask: Int,
    ignored: Any?,
): Fingerprint = fingerprint(
    if (mask and 0x1 != 0) 0 else fuzzyPatternScanThreshold,
    block
)
