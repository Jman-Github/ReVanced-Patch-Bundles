import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import test from "node:test";
import { createPostgresComparator } from "../../shared/postgres-collation.js";

test("Python catalog statistics and Worker collation agree across Unicode and contractions",()=>{
  const values=["a","A","AAAD Premium","ab","a-b","\u00e9","e\u0301","l\u00b7",
    "\u004c\u0387","\u0418\u0306","\u0e40\u0e01","\u00df","ss",""," ","!"];
  let seed=17;
  for(let i=0;i<512;i++) {
    seed=(Math.imul(seed,1664525)+1013904223)>>>0;
    const point=1+seed%0x10ffff;
    if(point>=0xd800 && point<=0xdfff)continue;
    values.push(String.fromCodePoint(point)+"a", "x"+String.fromCodePoint(point));
  }
  const reference=spawnSync("python",["-c",
    "import json,sys; from scripts.postgres_collation import text_key; data=json.load(sys.stdin); print(json.dumps(sorted(data,key=text_key),ensure_ascii=True))"],
    {cwd:new URL("../../",import.meta.url),input:JSON.stringify(values),encoding:"utf8",
      env:{...process.env,PYTHONUTF8:"1"}});
  assert.equal(reference.status,0,reference.stderr);
  assert.deepEqual(values.sort(createPostgresComparator()),JSON.parse(reference.stdout));
});

test("collation matches native libc strcoll for backward runs and combining marks",()=>{
  // Verified with native strcoll using the pinned glibc 2.36 LC_COLLATE data.
  // strxfrm alone gives a different order for backward runs before letters.
  const expected=["00_a","00a","0!a","0_a","0_a_","0_A","0..a.","0._a","0a","0a ",
    "0\u0301_a","0_\u0301a","0\u0306\u0301a","0\u0301\u0306a","a-b","ab"];
  const compare=createPostgresComparator();
  assert.deepEqual([...expected].reverse().sort(compare),expected);
  assert.ok(compare("0_a","0a")<0);
  assert.ok(compare("0_A","0a ")<0);
});
