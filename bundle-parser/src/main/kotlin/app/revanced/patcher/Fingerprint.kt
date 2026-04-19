@file:Suppress("MemberVisibilityCanBePrivate", "unused")

package app.revanced.patcher

import com.android.tools.smali.dexlib2.Opcode
import com.android.tools.smali.dexlib2.iface.ClassDef
import com.android.tools.smali.dexlib2.iface.Method

/**
 * Minimal compatibility model for newer patch bundles that reference the modern
 * [Fingerprint] type at class-load time.
 *
 * The bundle parser only needs to deserialize patch definitions, so this class
 * intentionally stores the constructor state without implementing matching logic.
 */
class Fingerprint internal constructor(
    val accessFlags: Int?,
    val returnType: String?,
    val parameters: List<String>?,
    val opcodes: List<Opcode?>?,
    val strings: List<String>?,
    val custom: ((method: Method, classDef: ClassDef) -> Boolean)?,
    val fuzzyPatternScanThreshold: Int,
)
