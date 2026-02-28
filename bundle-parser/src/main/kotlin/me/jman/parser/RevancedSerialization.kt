package me.jman.parser

import app.revanced.patcher.patch.Option
import app.revanced.patcher.patch.Patch
import app.revanced.patcher.patch.VersionName
import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.KSerializer
import kotlinx.serialization.builtins.ListSerializer
import kotlinx.serialization.builtins.MapSerializer
import kotlinx.serialization.builtins.SetSerializer
import kotlinx.serialization.builtins.nullable
import kotlinx.serialization.builtins.serializer
import kotlinx.serialization.descriptors.buildClassSerialDescriptor
import kotlinx.serialization.descriptors.element
import kotlinx.serialization.encoding.Decoder
import kotlinx.serialization.encoding.Encoder
import kotlinx.serialization.encoding.encodeStructure
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.encodeToStream
import kotlinx.serialization.serializer
import java.io.OutputStream

private class PatchSerializer : KSerializer<Patch> {
    override val descriptor = buildClassSerialDescriptor("Patch") {
        element<String?>("name")
        element<String?>("description")
        element<Boolean>("use")
        element<List<String>>("dependencies")
        element<Map<String, Set<VersionName>?>?>("compatiblePackages")
        element("options", OptionSerializer.descriptor)
    }

    override fun deserialize(decoder: Decoder) = throw NotImplementedError("Deserialization is unsupported")

    @OptIn(ExperimentalSerializationApi::class)
    override fun serialize(encoder: Encoder, value: Patch) {
        encoder.encodeStructure(descriptor) {
            encodeNullableSerializableElement(
                descriptor,
                0,
                String.serializer(),
                value.name,
            )
            encodeNullableSerializableElement(
                descriptor,
                1,
                String.serializer(),
                value.description,
            )
            encodeBooleanElement(
                descriptor,
                2,
                value.use,
            )
            encodeSerializableElement(
                descriptor,
                3,
                ListSerializer(String.serializer()),
                value.dependencies.map { it.name ?: it.toString() },
            )
            encodeNullableSerializableElement(
                descriptor,
                4,
                MapSerializer(String.serializer(), SetSerializer(String.serializer()).nullable),
                value.compatiblePackages?.associate { (packageName, versions) -> packageName to versions },
            )
            encodeSerializableElement(
                descriptor,
                5,
                SetSerializer(OptionSerializer),
                value.options.values.toSet(),
            )
        }
    }

    private object OptionSerializer : KSerializer<Option<*>> {
        override val descriptor = buildClassSerialDescriptor("Option") {
            element<String>("name")
            element<String?>("description")
            element<Boolean>("required")
            element<String>("type")
            element<String?>("default")
            element<Map<String, String?>?>("values")
        }

        override fun deserialize(decoder: Decoder) = throw NotImplementedError("Deserialization is unsupported")

        @OptIn(ExperimentalSerializationApi::class)
        override fun serialize(encoder: Encoder, value: Option<*>) {
            encoder.encodeStructure(descriptor) {
                encodeStringElement(descriptor, 0, value.name)
                encodeNullableSerializableElement(descriptor, 1, String.serializer(), value.description)
                encodeBooleanElement(descriptor, 2, value.required)
                encodeSerializableElement(descriptor, 3, String.serializer(), value.type.toString())
                encodeNullableSerializableElement(descriptor, 4, serializer(value.type), value.default)
                encodeNullableSerializableElement(
                    descriptor,
                    5,
                    MapSerializer(String.serializer(), serializer(value.type)),
                    value.values,
                )
            }
        }
    }
}

private val patchPrettySerializer by lazy { Json { prettyPrint = true } }
private val patchSerializer by lazy { Json }

@OptIn(ExperimentalSerializationApi::class)
fun Set<Patch>.serializeTo(
    outputStream: OutputStream,
    prettyPrint: Boolean = true,
) = if (prettyPrint) {
    patchPrettySerializer
} else {
    patchSerializer
}.encodeToStream(SetSerializer(PatchSerializer()), this, outputStream)
