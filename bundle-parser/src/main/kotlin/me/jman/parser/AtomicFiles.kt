package me.jman.parser

import java.io.File
import java.nio.file.AtomicMoveNotSupportedException
import java.nio.file.Files
import java.nio.file.StandardCopyOption

/** Readers see either the previous complete file or the new complete file. */
internal fun atomicWriteText(output: File, text: String) {
    val target = output.toPath().toAbsolutePath()
    val temporary = Files.createTempFile(target.parent, output.name, ".tmp")
    try {
        Files.writeString(temporary, text)
        try {
            Files.move(temporary, target, StandardCopyOption.REPLACE_EXISTING,
                StandardCopyOption.ATOMIC_MOVE)
        } catch (_: AtomicMoveNotSupportedException) {
            Files.move(temporary, target, StandardCopyOption.REPLACE_EXISTING)
        }
    } finally {
        Files.deleteIfExists(temporary)
    }
}
