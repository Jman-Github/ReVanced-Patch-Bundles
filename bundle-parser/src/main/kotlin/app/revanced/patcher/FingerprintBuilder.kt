@file:Suppress("MemberVisibilityCanBePrivate", "unused")

package app.revanced.patcher

import com.android.tools.smali.dexlib2.AccessFlags
import com.android.tools.smali.dexlib2.Opcode
import com.android.tools.smali.dexlib2.iface.ClassDef
import com.android.tools.smali.dexlib2.iface.Method
import kotlin.Function2

/**
 * Lightweight re-implementation of the upstream [FingerprintBuilder]. This exists solely so the
 * bundle parser can satisfy the binary API expected by patches compiled against newer patcher
 * releases while still delegating to the legacy [Fingerprint] matching logic bundled with this
 * project.
 */
class FingerprintBuilder internal constructor(
    private val fuzzyPatternScanThreshold: Int = 0,
) {
    private var accessFlags: Int? = null
    private var returnType: String? = null
    private var parameters: List<String>? = null
    private var opcodes: List<Opcode?>? = null
    private var strings: List<String>? = null
    private var customBlock: ((method: Method, classDef: ClassDef) -> Boolean)? = null

    fun accessFlags(accessFlags: Int) {
        this.accessFlags = accessFlags
    }

    fun accessFlags(vararg accessFlags: AccessFlags) {
        this.accessFlags = accessFlags.fold(0) { acc, it -> acc or it.value }
    }

    fun returns(returnType: String) {
        this.returnType = returnType
    }

    fun parameters(vararg parameters: String) {
        this.parameters = parameters.toList()
    }

    fun opcodes(vararg opcodes: Opcode?) {
        this.opcodes = opcodes.toList()
    }

    fun opcodes(instructions: String) {
        this.opcodes = instructions.trimIndent()
            .split("\n")
            .filter { it.isNotBlank() }
            .map { line ->
                val name = line.trim().takeWhile { char -> !char.isWhitespace() }
                if (name == "null") return@map null
                opcodesByName[name] ?: throw Exception("Unknown opcode: $name")
            }
    }

    fun strings(vararg strings: String) {
        this.strings = strings.toList()
    }

    fun custom(customBlock: (method: Method, classDef: ClassDef) -> Boolean) {
        this.customBlock = customBlock
    }

    /**
     * Compatibility entry point for the instruction filtering DSL introduced upstream.
     * The parser never evaluates these filters, so accepting them is a no-op.
     */
    fun instructions(vararg filters: InstructionFilter) {
        if (filters.isEmpty()) return
        // Intentionally ignored. We merely need a method with this signature to exist so
        // patches compiled against newer patcher versions can link successfully.
    }

    internal fun build(): Fingerprint = fingerprintConstructor.newInstance(
        accessFlags,
        returnType,
        parameters,
        opcodes,
        strings,
        customBlock,
        fuzzyPatternScanThreshold,
    )

    private companion object {
        val fingerprintConstructor = Fingerprint::class.java.getDeclaredConstructor(
            Int::class.javaObjectType,
            String::class.java,
            List::class.java,
            List::class.java,
            List::class.java,
            Function2::class.java,
            Int::class.javaPrimitiveType,
        ).apply { isAccessible = true }

        val opcodesByName = Opcode.entries.associateBy { it.name }
    }
}
