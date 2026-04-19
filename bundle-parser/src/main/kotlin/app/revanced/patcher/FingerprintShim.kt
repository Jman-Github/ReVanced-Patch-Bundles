@file:JvmName("FingerprintKt")
@file:Suppress("unused")

package app.revanced.patcher

import kotlin.Function1

private val fingerprintBuilderConstructor =
    FingerprintBuilder::class.java.getDeclaredConstructor(Int::class.javaPrimitiveType).apply {
        isAccessible = true
    }
private val fingerprintBuilderBuildMethod =
    FingerprintBuilder::class.java.declaredMethods.first { it.name.startsWith("build") }.apply {
        isAccessible = true
    }

private fun newBuilder(threshold: Int): FingerprintBuilder =
    fingerprintBuilderConstructor.newInstance(threshold)

private fun FingerprintBuilder.buildCompat(): Fingerprint =
    fingerprintBuilderBuildMethod.invoke(this) as Fingerprint

/**
 * Compatibility shim for patches compiled against newer ReVanced Patcher builds
 * that added an overload without the fuzzyThreshold parameter.
 *
 * This project still depends on an older artifact so we provide the exact API
 * surface expected by the patches. Remove once the dependency can be upgraded.
 */
fun fingerprint(
    block: FingerprintBuilder.() -> Unit,
): Fingerprint = newBuilder(0).apply(block).buildCompat()

fun fingerprint(
    fuzzyPatternScanThreshold: Int,
    block: Function1<FingerprintBuilder, Unit>,
): Fingerprint = newBuilder(fuzzyPatternScanThreshold).apply { block.invoke(this) }.buildCompat()

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
