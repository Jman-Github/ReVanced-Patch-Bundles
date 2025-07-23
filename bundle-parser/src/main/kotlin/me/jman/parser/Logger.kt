package me.jman.parser

object Logger {
    fun info(message: String) = println(message)

    fun warning(message: String) = println("::warning::$message")

    fun error(message: String) = println("::error::$message")
}
