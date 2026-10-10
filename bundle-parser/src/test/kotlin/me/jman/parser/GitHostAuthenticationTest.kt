package me.jman.parser

import java.net.URL
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class GitHostAuthenticationTest {
    @Test fun `a token belongs only to its configured authority`() {
        val tokens = """{"codeberg.org":"codeberg-token"}"""
        assertEquals(mapOf("Authorization" to "Bearer codeberg-token"),
            gitHostHeaders(URL("https://codeberg.org/owner/repo/releases/download/v1/p.rvp"), tokens))
        assertTrue(gitHostHeaders(URL("https://downloads.example.test/p.rvp"), tokens).isEmpty())
        assertTrue(gitHostHeaders(URL("https://codeberg.org:8443/p.rvp"), tokens).isEmpty())
    }
}
