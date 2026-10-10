import assert from "node:assert/strict";
import test from "node:test";
import { createPostgresMatcher } from "../src/postgres-regex.js";

const check = (value, pattern, expected = true, operator = "_regex") =>
  assert.equal(createPostgresMatcher()(value,pattern,operator),expected,JSON.stringify({value,pattern,operator}));
test("PostgreSQL ARE backreferences, lookaround, word boundaries and escapes", () => {
  check("bb","([bc])\\1"); check("bc","([bc])\\1",false);
  check("word word","(\\w+) \\1");
  check("abc","a(?=b)b"); check("abc","a(?!b)",false);
  check("abc","(?<=ab)c"); check("abc","(?<!ab)c",false);
  check("xabcy","\\mabc\\M",false); check("-abc-","\\mabc\\M");
  check("abc","[[:<:]]abc[[:>:]]"); check("a\bb","a\\bb");
  check("abc\n","abc$",false); check("abc\n","(?n)abc$");
  check("\n","."); check("\n","(?n).",false); check("\n","(?p)[^a]",false);
  check("\n","(?w).");
  check("abc","***=a.c",false); check("a.c","***=a.c");
  check("ABC","(?c)abc",false,"_iregex"); check("ABC","(?i)abc");
  check("ab","(?x) a #comment\n b"); check("ab","a(?#comment)b");
  check("A","[[:upper:]]"); check("a","[[:upper:]]",false);
  check("a","[[:upper:]]",true,"_iregex"); check("!","[[:punct:]]");
  check("o","[[=o=]]"); check("a","[[.a.]]"); check("]","[]a]");
  check("AA","(?b)\\(A\\)\\1"); check("aaa","(?b)a\\{3\\}");
  check("+","(?b)+"); check("d","(?e)\\d"); check("3","(?e)\\d",false);
  check("aab","(a|aa)b");
  check("abab","^(a(b)?)+\\2$",false); check("abb","^(a(b)?)+\\2$");
  check("abba","^((a)?b)+\\2$",false);
  check("\t","[[.tab.]]"); check("\n","[[=newline=]]");
  check("-","[[.hyphen-minus.]]"); check("7","[[.seven.]]");
  check("\r","[[.CR.]]"); check("_","[[.low-line.]]");
  check("*a","(?b)*a"); check("a^b","(?b)a^b"); check("a$b","(?b)a$b");
  check("3","(a*)?\\1"); check("3","a(?#ignored)*");
  check("É","(?i)é",false); check("K","(?i)[a-z]",false); check("aa","(a?)*");
});
test("SIMILAR TO covers the whole value and preserves bracket and SQL wildcard semantics", () => {
  check("abc","%(b|d)%",true,"_similar"); check("abc","a",false,"_similar");
  check("-abc-","%\\mabc\\M%",true,"_similar");
  check("axb","a.b",false,"_similar"); check("a.b","a.b",true,"_similar");
  check("%","[%]",true,"_similar"); check("_","\\_",true,"_similar");
  check("a\n","a_",true,"_similar");
  check(".","[[:alpha:]%]",false,"_similar");
  check("%","[[:alpha:]%]",true,"_similar");
  check("a",'\\"a\\"',true,"_similar");
});
test("invalid ARE patterns and expensive backtracking stop without executing native regex", () => {
  for (const pattern of ["(a)\\2","[\\m]","(?=a\\1)","a{256}","a**","\\k","[","[a-c-e]","[[:constructor:]]","[[.constructor.]]"])
    assert.throws(() => createPostgresMatcher()("a",pattern,"_regex"),/Invalid PostgreSQL regex/);
  assert.throws(() => createPostgresMatcher()("a".repeat(1000)+"!","^(a+)+$","_regex"),/work budget/);
  assert.throws(() => createPostgresMatcher()("a","a".repeat(513),"_regex"),/512/);
});
