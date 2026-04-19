@file:JvmName("InstructionFilterKt")
@file:Suppress("unused")

package app.revanced.patcher

import com.android.tools.smali.dexlib2.Opcode

/**
 * Compatibility models for the new instruction filtering DSL introduced in the
 * upstream patcher. The bundle parser only needs these types to exist so that
 * patch jars compiled against the latest APIs can be loaded.
 */
sealed interface InstructionLocation {
    /**
     * Matches at the first available instruction.
     */
    class MatchFirst : InstructionLocation

    /**
     * Matches an instruction immediately following the previous filter.
     */
    class MatchAfterImmediately : InstructionLocation

    /**
     * Matches an instruction anywhere after the previous filter.
     */
    class MatchAfterAnywhere : InstructionLocation

    /**
     * Matches an instruction after the previous filter but within a specific window.
     */
    data class MatchAfterWithin(val window: Int) : InstructionLocation
}

/**
 * Marker for synthesized instruction filters.
 */
interface InstructionFilter {
    val location: InstructionLocation
}

enum class StringComparisonType {
    CONTAINS,
    STARTS_WITH,
    ENDS_WITH,
    EQUALS,
}

data class StringFilter(
    val value: String,
    override val location: InstructionLocation,
    val comparisonType: StringComparisonType = StringComparisonType.CONTAINS,
) : InstructionFilter

data class LiteralFilter<T : Number>(
    val value: T,
    val registers: List<Int>?,
    override val location: InstructionLocation,
) : InstructionFilter

data class MethodCallFilter(
    val owner: String?,
    val name: String?,
    val parameterTypes: List<String>?,
    val returnType: String?,
    val argumentTypes: List<String>?,
    override val location: InstructionLocation,
) : InstructionFilter

data class FieldAccessFilter(
    val fieldDescriptor: String,
    val registers: List<Int>?,
    override val location: InstructionLocation,
) : InstructionFilter

data class OpcodeFilter(
    val opcode: Opcode,
    override val location: InstructionLocation,
) : InstructionFilter

data class CheckCastFilter(
    val type: String,
    override val location: InstructionLocation,
) : InstructionFilter

data class NewInstanceFilter(
    val type: String,
    override val location: InstructionLocation,
) : InstructionFilter

data class AnyInstruction(
    val filters: List<InstructionFilter>,
    override val location: InstructionLocation,
) : InstructionFilter

fun string(
    value: String,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): StringFilter = StringFilter(value, location)

fun literal(
    value: Int,
    registers: List<Int>? = null,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): LiteralFilter<Int> = LiteralFilter(value, registers, location)

fun literal(
    value: Long,
    registers: List<Int>? = null,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): LiteralFilter<Long> = LiteralFilter(value, registers, location)

fun literal(
    value: Float,
    registers: List<Int>? = null,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): LiteralFilter<Float> = LiteralFilter(value, registers, location)

fun literal(
    value: Double,
    registers: List<Int>? = null,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): LiteralFilter<Double> = LiteralFilter(value, registers, location)

fun literal(
    supplier: () -> Number,
    registers: List<Int>? = null,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): LiteralFilter<Number> = LiteralFilter(0, registers, location)

fun methodCall(
    owner: String? = null,
    name: String? = null,
    parameterTypes: List<String>? = null,
    returnType: String? = null,
    argumentTypes: List<String>? = null,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): MethodCallFilter = MethodCallFilter(owner, name, parameterTypes, returnType, argumentTypes, location)

fun methodCall(
    name: String?,
    parameterTypes: List<String>?,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): MethodCallFilter = MethodCallFilter(null, name, parameterTypes, null, null, location)

fun fieldAccess(
    fieldDescriptor: String,
    registers: List<Int>? = null,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): FieldAccessFilter = FieldAccessFilter(fieldDescriptor, registers, location)

fun fieldAccess(
    owner: String?,
    name: String?,
    fieldDescriptor: String,
    opcode: Opcode? = null,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): FieldAccessFilter = FieldAccessFilter(fieldDescriptor, null, location)

fun opcode(
    opcode: Opcode,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): OpcodeFilter = OpcodeFilter(opcode, location)

fun checkCast(
    type: String,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): CheckCastFilter = CheckCastFilter(type, location)

fun newInstance(
    type: String,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): NewInstanceFilter = NewInstanceFilter(type, location)

fun anyInstruction(
    vararg filters: InstructionFilter,
    location: InstructionLocation = InstructionLocation.MatchFirst(),
): AnyInstruction = AnyInstruction(filters.toList(), location)
