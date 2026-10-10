/* Independent PostgreSQL ARE boolean matcher.
 * Syntax reference: https://www.postgresql.org/docs/17/functions-matching.html
 * Matching is interpreted with a work budget; user patterns never execute in
 * the native backtracking engine. Locale profiles select character classes and case maps.
 */
import { CatalogError } from "../../shared/catalog.js";
import { regexLocale } from "./regex-locale.js";
import { collatingCharacter } from "./postgres-character-names.js";
const cache = new Map();
const fail = message => { throw new CatalogError("Invalid PostgreSQL regex: " + message); };
const fold = value => value.replace(/[A-Z]/g,c => c.toLowerCase());
const upper = value => value.replace(/[a-z]/g,c => c.toUpperCase());
const literal = value => ({ type: "literal", value });
const classes = {
  alnum: c => /^[a-z0-9]$/i.test(c), alpha: c => /^[a-z]$/i.test(c),
  ascii: c => c.codePointAt(0) < 128, blank: c => c === " " || c === "\t",
  cntrl: c => c.codePointAt(0) < 32 || c === "\x7f",
  digit: c => /^[0-9]$/.test(c), graph: c => /^[\x21-\x7e]$/.test(c),
  lower: c => /^[a-z]$/.test(c), print: c => /^[\x20-\x7e]$/.test(c),
  punct: c => /^[!-/:-@[-`{-~]$/.test(c), space: c => /^[ \t\r\n\v\f]$/.test(c),
  upper: c => /^[A-Z]$/.test(c), word: c => /^[a-z0-9_]$/i.test(c),
  xdigit: c => /^[a-f0-9]$/i.test(c)
};
function similarPattern(pattern) {
  let out = "(?:", bracket = false, quotes = 0;
  for (let i = 0; i < pattern.length; i++) {
    const c = pattern[i];
    if (c === "\\") {
      if (++i === pattern.length) fail("incomplete SIMILAR escape");
      if (pattern[i] === '"' && !bracket) {
        if (++quotes > 2) fail("SIMILAR TO permits at most two escape-double-quote separators");
        out += ")(?:";
      } else out += "\\" + pattern[i];
    } else if (bracket && c === "[" && ":.=".includes(pattern[i+1] ?? "")) {
      const end = pattern.indexOf(pattern[i+1]+"]",i+2);
      if (end < 0) fail("unclosed bracket element");
      out += pattern.slice(i,end+2); i = end+1;
    } else if (c === "[") { bracket = true; out += c; }
    else if (c === "]") { bracket = false; out += c; }
    else if (bracket) out += c;
    else if (c === "%") out += ".*";
    else if (c === "_") out += ".";
    else if (c === "(") out += "(?:";
    else out += ".^$".includes(c) ? "\\" + c : c;
  }
  return "\\A(?:" + out + "))\\Z";
}
class Parser {
  constructor(pattern, insensitive, similar) {
    this.insensitive = insensitive; this.newline = "s"; this.mode = "a";
    this.expanded = false; this.capture = 0; this.closed = new Set(); this.look = 0;
    if (similar) pattern = similarPattern(pattern);
    else {
      if (pattern.startsWith("***=")) { this.mode = "q"; pattern = pattern.slice(4); }
      else if (pattern.startsWith("***:")) pattern = pattern.slice(4);
      const options = this.mode !== "q" && pattern.match(/^\(\?([a-z]+)\)/);
      if (options) {
        for (const flag of options[1]) {
          if ("beq".includes(flag)) this.mode = flag;
          else if (flag === "i" || flag === "c") this.insensitive = flag === "i";
          else if ("nmpsw".includes(flag)) this.newline = flag === "m" ? "n" : flag;
          else if (flag === "x" || flag === "t") this.expanded = flag === "x";
          else fail("unknown embedded option");
        }
        pattern = pattern.slice(options[0].length);
      }
    }
    // BRE's grouping and bounds are escaped, while + ? | are ordinary.
    if (this.mode === "b") {
      let converted = "", bracket = false;
      for (let i = 0; i < pattern.length; i++) {
        const c = pattern[i];
        if (c === "\\" && !bracket) {
          const next = pattern[++i]; if (next === undefined) fail("trailing escape");
          converted += "(){}".includes(next) ? next : "\\" + next;
        } else {
          if (c === "[") bracket = true;
          if (c === "]") bracket = false;
          const ordinary = !bracket && ("()+?|{}".includes(c) ||
            (c === "^" && i !== 0 && pattern.slice(i-2,i) !== "\\(") ||
            (c === "$" && i !== pattern.length-1 && pattern.slice(i+1,i+3) !== "\\)") ||
            (c === "*" && (i === 0 || pattern.slice(i-2,i) === "\\(")));
          converted += ordinary ? "\\" + c : c;
        }
      }
      pattern = converted;
    }
    this.source = Array.from(pattern); this.position = 0;
  }
  skip() {
    while (this.position < this.source.length) {
      if (this.mode === "a" && this.source.slice(this.position,this.position+3).join("") === "(?#") {
        this.position += 3;
        while (this.position < this.source.length && this.source[this.position] !== ")") this.position++;
        if (this.source[this.position++] !== ")") fail("unclosed comment");
      } else if (this.expanded && classes.space(this.source[this.position])) this.position++;
      else if (this.expanded && this.source[this.position] === "#") {
        while (this.position < this.source.length && this.source[this.position] !== "\n") this.position++;
      } else break;
    }
  }
  peek() { this.skip(); return this.source[this.position]; }
  take() { this.skip(); return this.source[this.position++]; }
  parse() {
    if (this.mode === "q") return { type: "seq", nodes: this.source.map(literal) };
    const node = this.branch(0);
    if (this.peek() !== undefined) fail("unbalanced parentheses");
    return node;
  }
  branch(depth) {
    if (depth > 64) fail("excessively nested pattern");
    const alternatives = [];
    do {
      const nodes = [];
      while (this.peek() !== undefined && this.peek() !== ")" && this.peek() !== "|") {
        let node = this.atom(depth);
        const q = this.peek();
        if (q && ("*+?".includes(q) || (q === "{" && /^[0-9]$/.test(this.source[this.position + 1] ?? "")))) {
          if (node.type === "anchor" || node.type === "look") fail("quantified constraint");
          this.take();
          let min = q === "+" ? 1 : 0, max = q === "?" ? 1 : Infinity;
          if (q === "{") {
            let bounds = "";
            while (this.peek() !== undefined && this.peek() !== "}") bounds += this.take();
            if (this.take() !== "}" || !/^\d+(,\d*)?$/.test(bounds)) fail("invalid repetition bounds");
            const values = bounds.split(",");
            min = Number(values[0]); max = values.length === 1 ? min : values[1] ? Number(values[1]) : Infinity;
            if (min > 255 || (max !== Infinity && max > 255) || min > max) fail("bounds must be between 0 and 255");
          }
          if (this.peek() === "?" && this.mode === "a") this.take();
          node = { type: "repeat", node, min, max };
        }
        nodes.push(node);
      }
      alternatives.push({ type: "seq", nodes });
      if (this.peek() !== "|") break;
      this.take();
    } while (true);
    return alternatives.length === 1 ? alternatives[0] : { type: "alt", nodes: alternatives };
  }
  atom(depth) {
    const c = this.take();
    if ("*+?".includes(c)) fail("quantifier without atom");
    if (c === "(") {
      let kind = "capture", index;
      if (this.peek() === "?") {
        if (this.mode !== "a") fail("ARE group in basic/extended expression");
        this.take(); const symbol = this.take();
        if (symbol === "#") {
          while (this.peek() !== undefined && this.peek() !== ")") this.take();
          if (this.take() !== ")") fail("unclosed comment");
          return { type: "seq", nodes: [] };
        }
        if (symbol === ":") kind = "group";
        else if (symbol === "=" || symbol === "!") kind = symbol === "=" ? "ahead" : "notAhead";
        else if (symbol === "<") {
          const sign = this.take();
          if (!"=!".includes(sign ?? "")) fail("invalid lookbehind");
          kind = sign === "=" ? "behind" : "notBehind";
        } else fail("invalid group");
      }
      const assertion = !["capture", "group"].includes(kind);
      if (assertion) this.look++;
      if (kind === "capture" && !this.look) index = ++this.capture;
      const node = this.branch(depth + 1);
      if (this.take() !== ")") fail("unclosed group");
      if (assertion) { this.look--; return { type: "look", kind, node }; }
      if (index) { this.closed.add(index); return { type: "capture", index, node }; }
      return node;
    }
    if (c === "[") return this.bracket();
    if (c === ".") return { type: "dot" };
    if (c === "^" || c === "$") return { type: "anchor", kind: c };
    if (c === "\\") return this.escape(false);
    return literal(c);
  }
  escape(inBracket) {
    const c = this.source[this.position++];
    if (c === undefined) fail("trailing escape");
    if (!/^[a-z0-9]$/i.test(c)) return literal(c);
    if (this.mode !== "a" && !(this.mode === "b" && /^[1-9]$/.test(c))) return literal(c);
    if ("dDsSwW".includes(c)) return { type: "class", entries: [{ name: {d:"digit",s:"space",w:"word"}[c.toLowerCase()], negated: c !== c.toLowerCase() }], negated: false };
    if ("AmMyYZ".includes(c)) {
      if (inBracket) fail("constraint inside bracket");
      return { type: "anchor", kind: c };
    }
    const simple = { a:"\x07", b:"\b", B:"\\", e:"\x1b", f:"\f", n:"\n", r:"\r", t:"\t", v:"\v" };
    if (c in simple) return literal(simple[c]);
    if (c === "c") {
      const next = this.source[this.position++]; if (next === undefined) fail("incomplete control escape");
      return literal(String.fromCodePoint(next.codePointAt(0) & 31));
    }
    if ("uUx".includes(c)) {
      const length = c === "u" ? 4 : c === "U" ? 8 : Infinity;
      let hex = "";
      while (hex.length < length && /^[0-9a-f]$/i.test(this.source[this.position] ?? "")) hex += this.source[this.position++];
      if (!hex || (length !== Infinity && hex.length !== length)) fail("invalid hexadecimal escape");
      const value = Number.parseInt(hex, 16);
      if (value > 0x10ffff || (value >= 0xd800 && value <= 0xdfff)) fail("invalid Unicode escape");
      return literal(String.fromCodePoint(value));
    }
    if (/^[0-9]$/.test(c)) {
      let digits = c;
      while (/^[0-9]$/.test(this.source[this.position] ?? "")) digits += this.source[this.position++];
      const n = Number(digits);
      if (c !== "0" && (digits.length === 1 || this.closed.has(n))) {
        if (inBracket || this.look || !this.closed.has(n)) fail("invalid backreference");
        return { type: "backref", index: n };
      }
      const octal = digits.match(/^[0-7]{1,3}/)?.[0];
      if (!octal) fail("invalid octal escape");
      this.position -= digits.length - octal.length;
      return literal(String.fromCodePoint(Number.parseInt(octal, 8)));
    }
    fail("unknown escape");
  }
  bracket() {
    const rest = this.source.slice(this.position).join("");
    if (rest.startsWith("[:<:]]") || rest.startsWith("[:>:]]")) {
      this.position += 6; return { type: "anchor", kind: rest[2] === "<" ? "m" : "M" };
    }
    let negated = false;
    if (this.source[this.position] === "^") { negated = true; this.position++; }
    const entries = [];
    const entry = () => {
      const c = this.source[this.position++];
      if (c === undefined) fail("unclosed bracket");
      if (c === "[" && ":.=".includes(this.source[this.position] ?? "")) {
        const marker = this.source[this.position++]; let name = "";
        while (this.position < this.source.length &&
               !(this.source[this.position] === marker && this.source[this.position + 1] === "]"))
          name += this.source[this.position++];
        if (this.position >= this.source.length) fail("unclosed bracket element");
        this.position += 2;
        if (marker === ":") {
          if (!Object.hasOwn(classes,name)) fail("unknown character class");
          return { name };
        }
        const value = Array.from(name).length === 1 ? name : collatingCharacter(name);
        if (value === undefined) fail("invalid collating element");
        return { value };
      }
      if (c === "\\" && this.mode === "a") {
        const escaped = this.escape(true);
        return escaped.type === "literal" ? { value: escaped.value } : { nested: escaped };
      }
      return { value: c };
    };
    do {
      const first = entry();
      if (this.source[this.position] === "-" && this.source[this.position + 1] !== "]") {
        this.position++; const last = entry();
        if (first.value === undefined || last.value === undefined ||
            first.value.codePointAt(0) > last.value.codePointAt(0)) fail("invalid character range");
        entries.push({ range: [first.value, last.value] });
        if (this.source[this.position] === "-" && this.source[this.position+1] !== "]")
          fail("overlapping character ranges");
      } else entries.push(first);
    } while (this.source[this.position] !== "]" && this.position < this.source.length);
    if (this.source[this.position++] !== "]") fail("unclosed bracket");
    return { type: "class", entries, negated };
  }
}
function classMatch(node, c, insensitive, locale) {
  const {classes,fold,upper}=locale;
  const found = node.entries.some(e => {
    if (e.nested) return classMatch(e.nested, c, insensitive, locale);
    if (e.name) {
      const yes = classes[e.name](c) || (insensitive && ["upper","lower"].includes(e.name) && (classes.alpha(c)));
      return e.negated ? !yes : yes;
    }
    if (e.range) {
      const test = v => v.codePointAt(0) >= e.range[0].codePointAt(0) && v.codePointAt(0) <= e.range[1].codePointAt(0);
      return test(c) || (insensitive && locale.caseSources(c).some(test));
    }
    return insensitive ? fold(e.value) === c || upper(e.value) === c : e.value === c;
  });
  return node.negated ? !found : found;
}
function capturesWithin(node) {
  if (!node.captureIndexes) node.captureIndexes = [
    ...(node.type === "capture" ? [node.index] : []),
    ...(node.node ? capturesWithin(node.node) : []),
    ...(node.nodes ?? []).flatMap(capturesWithin)
  ];
  return node.captureIndexes;
}
function resetCaptures(state,node) {
  const indexes = capturesWithin(node);
  if (!indexes.some(index => Object.hasOwn(state.captures,index))) return state;
  const captures = {...state.captures};
  for (const index of indexes) delete captures[index];
  return {...state,captures};
}
function testPattern(parsed, value, budget, locale) {
  const {classes,fold,upper}=locale;
  const text = Array.from(value), newlineDot = ["n","p"].includes(parsed.newline),
    newlineAnchor = ["n","w"].includes(parsed.newline);
  const equal = (value,pattern) => parsed.insensitive ?
    value === fold(pattern) || value === upper(pattern) : value === pattern;
  function* run(node, state) {
    if (--budget.remaining < 0) throw new CatalogError("Regex matching exceeds work budget; narrow the filter", 422);
    const pos = state.pos, c = text[pos];
    switch (node.type) {
      case "seq": {
        function* sequence(i, current) {
          if (i === node.nodes.length) { yield current; return; }
          for (const next of run(node.nodes[i], current)) yield* sequence(i + 1, next);
        }
        yield* sequence(0, state); return;
      }
      case "alt": for (const child of node.nodes) yield* run(child, state); return;
      case "literal": if (c !== undefined && equal(c, node.value)) yield { ...state, pos: pos + 1 }; return;
      case "dot": if (c !== undefined && (!newlineDot || c !== "\n")) yield { ...state, pos: pos + 1 }; return;
      case "class": if (c !== undefined && !(newlineDot && node.negated && c === "\n") &&
          classMatch(node, c, parsed.insensitive, locale)) yield { ...state, pos: pos + 1 }; return;
      case "capture": for (const next of run(node.node, resetCaptures(state,node)))
        yield { ...next, captures: { ...next.captures, [node.index]: text.slice(pos,next.pos).join("") } }; return;
      case "backref": {
        const captured = state.captures[node.index];
        if (captured !== undefined) {
          const chars = Array.from(captured);
          if (chars.every((char,i) => text[pos+i] !== undefined && (parsed.insensitive ? fold(char) === fold(text[pos+i]) : char === text[pos+i])))
            yield { ...state, pos: pos + chars.length };
        }
        return;
      }
      case "anchor": {
        const before = pos > 0 && classes.word(text[pos-1]), after = pos < text.length && classes.word(c);
        const ok = { "^":pos === 0 || (newlineAnchor && text[pos-1] === "\n"),
          "$":pos === text.length || (newlineAnchor && c === "\n"),
          A:pos === 0, Z:pos === text.length, m:!before && after, M:before && !after,
          y:before !== after, Y:before === after }[node.kind];
        if (ok) yield state; return;
      }
      case "look": {
        let found = false;
        if (node.kind.endsWith("Ahead") || node.kind === "ahead")
          found = !run(node.node,state).next().done;
        else for (let start = 0; start <= pos && !found; start++)
          for (const next of run(node.node,{...state,pos:start}))
            if (next.pos === pos) { found = true; break; }
        if (found !== node.kind.startsWith("not")) yield state;
        return;
      }
      case "repeat": {
        const stack = [{ state, count:0 }];
        const seen = new Set();
        while (stack.length) {
          if (--budget.remaining < 0) throw new CatalogError("Regex matching exceeds work budget; narrow the filter", 422);
          const current = stack.pop();
          const key = current.state.pos + ":" + Math.min(current.count,node.min) + ":" + JSON.stringify(current.state.captures);
          if (seen.has(key) && node.max === Infinity) continue;
          seen.add(key);
          if (current.count >= node.min) yield current.state;
          if (current.count >= node.max) continue;
          for (const next of run(node.node,resetCaptures(current.state,node.node))) {
            // Empty repeats must still meet finite minimums; thereafter no new match is possible.
            if (next.pos === current.state.pos && current.count >= node.min &&
                JSON.stringify(next.captures) === JSON.stringify(current.state.captures)) continue;
            if (stack.length >= 8192) throw new CatalogError("Regex matching exceeds memory budget; narrow the filter",422);
            stack.push({state:next,count:current.count+1});
          }
        }
        return;
      }
    }
  }
  for (let start = 0; start <= text.length; start++)
    if (!run(parsed.ast,{pos:start,captures:{}}).next().done) return true;
  return false;
}
export function createPostgresMatcher(localeName = "C") {
  const locale=regexLocale(localeName,{classes,fold,upper,caseSources:c=>[c,fold(c),upper(c)]});
  // One budget per query, shared by every row and filter.
  const budget = { remaining: 1000000 };
  const matcher = (value, pattern, operator) => {
    if (typeof pattern !== "string" || pattern.length > 512)
      throw new CatalogError("Regex pattern must contain at most 512 characters");
    const key = operator + ":" + pattern;
    if (!cache.has(key)) {
      const parser = new Parser(pattern,operator.includes("iregex"),operator.endsWith("similar"));
      parser.ast = parser.parse();
      if (cache.size >= 100) cache.clear();
      cache.set(key,parser);
    }
    return testPattern(cache.get(key),value,budget,locale);
  };
  matcher.fold = locale.fold;
  return matcher;
}
