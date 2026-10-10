/*
 * regc_locale.c --
 *
 *	This file contains locale-specific regexp routines.
 *	This file is #included by regcomp.c.
 *
 * Copyright (c) 1998 by Scriptics Corporation.
 *
 * This software is copyrighted by the Regents of the University of
 * California, Sun Microsystems, Inc., Scriptics Corporation, ActiveState
 * Corporation and other parties.  The following terms apply to all files
 * associated with the software unless explicitly disclaimed in
 * individual files.
 *
 * The authors hereby grant permission to use, copy, modify, distribute,
 * and license this software and its documentation for any purpose, provided
 * that existing copyright notices are retained in all copies and that this
 * notice is included verbatim in any distributions. No written agreement,
 * license, or royalty fee is required for any of the authorized uses.
 * Modifications to this software may be copyrighted by their authors
 * and need not follow the licensing terms described here, provided that
 * the new terms are clearly indicated on the first page of each file where
 * they apply.
 *
 * IN NO EVENT SHALL THE AUTHORS OR DISTRIBUTORS BE LIABLE TO ANY PARTY
 * FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES
 * ARISING OUT OF THE USE OF THIS SOFTWARE, ITS DOCUMENTATION, OR ANY
 * DERIVATIVES THEREOF, EVEN IF THE AUTHORS HAVE BEEN ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 * THE AUTHORS AND DISTRIBUTORS SPECIFICALLY DISCLAIM ANY WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.  THIS SOFTWARE
 * IS PROVIDED ON AN "AS IS" BASIS, AND THE AUTHORS AND DISTRIBUTORS HAVE
 * NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
 * MODIFICATIONS.
 *
 * GOVERNMENT USE: If you are acquiring this software on behalf of the
 * U.S. government, the Government shall have only "Restricted Rights"
 * in the software and related documentation as defined in the Federal
 * Acquisition Regulations (FARs) in Clause 52.227.19 (c) (2).  If you
 * are acquiring the software on behalf of the Department of Defense, the
 * software shall be classified as "Commercial Computer Software" and the
 * Government shall have only "Restricted Rights" as defined in Clause
 * 252.227-7013 (c) (1) of DFARs.  Notwithstanding the foregoing, the
 * authors grant the U.S. Government and others acting in its behalf
 * permission to use and distribute the software in accordance with the
 * terms specified in this license.
 *
 * src/backend/regex/regc_locale.c
 */

// Character-name mappings adapted from PostgreSQL 17 regc_locale.c.
// https://github.com/postgres/postgres/blob/35c508af520963bf1245b86f437c21f834cc2be0/src/backend/regex/regc_locale.c
// The upstream notice above applies to this mapping. Matcher logic is separate.
const controls = "NUL SOH STX ETX EOT ENQ ACK BEL BS HT LF VT FF CR SO SI DLE DC1 DC2 DC3 DC4 NAK SYN ETB CAN EM SUB ESC FS GS RS US".split(" ");
const names = new Map(controls.map((name,index) => [name,String.fromCodePoint(index)]));
const aliases = {
  alert:7, backspace:8, tab:9, newline:10, "vertical-tab":11, "form-feed":12,
  "carriage-return":13, IS4:28, IS3:29, IS2:30, IS1:31, space:32,
  "exclamation-mark":33, "quotation-mark":34, "number-sign":35, "dollar-sign":36,
  "percent-sign":37, ampersand:38, apostrophe:39, "left-parenthesis":40,
  "right-parenthesis":41, asterisk:42, "plus-sign":43, comma:44, hyphen:45,
  "hyphen-minus":45, period:46, "full-stop":46, slash:47, solidus:47,
  colon:58, semicolon:59, "less-than-sign":60, "equals-sign":61,
  "greater-than-sign":62, "question-mark":63, "commercial-at":64,
  "left-square-bracket":91, backslash:92, "reverse-solidus":92,
  "right-square-bracket":93, circumflex:94, "circumflex-accent":94,
  underscore:95, "low-line":95, "grave-accent":96, "left-brace":123,
  "left-curly-bracket":123, "vertical-line":124, "right-brace":125,
  "right-curly-bracket":125, tilde:126, DEL:127
};
for (const [name,code] of Object.entries(aliases)) names.set(name,String.fromCodePoint(code));
"zero one two three four five six seven eight nine".split(" ").forEach((name,index) => names.set(name,String(index)));
export function collatingCharacter(name) { return names.get(name); }
