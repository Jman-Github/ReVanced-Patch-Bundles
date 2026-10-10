/* Independent reader for the generated en_US.utf8 collation tables.
 * Data: glibc 2.36 locale definitions (no copyright claimed in locale data).
 * Format references: https://github.com/bminor/glibc/tree/glibc-2.36/locale
 * PostgreSQL semantics: https://www.postgresql.org/docs/17/collation.html
 */
import data from "./postgres-collation-data.json" with {type:"json"};

const decode = value => Uint8Array.from(atob(value), c => c.charCodeAt(0));
const weights = decode(data.weights), rules = decode(data.rules), extra = decode(data.extra);
const table = new DataView(decode(data.table).buffer);
const indirect = new DataView(decode(data.indirect).buffer);
const extraView = new DataView(extra.buffer);
const encoder = new TextEncoder();
const lexical = (a,b) => {
  for (let i=0;i<Math.min(a.length,b.length);i++) if (a[i] !== b[i]) return a[i]-b[i];
  return a.length-b.length;
};
function tokens(bytes) {
  const result = [];
  for (let start=0;start<bytes.length;) {
    let packed = table.getInt32(bytes[start++]*4,true);
    if (packed < 0) {
      let offset = -packed;
      while (true) {
        const target = extraView.getInt32(offset,true), length = extra[offset+4];
        const first = offset+5;
        if (target >= 0) {
          if (lexical(bytes.subarray(start,start+length),extra.subarray(first,first+length)) === 0) {
            packed=target; start+=length; break;
          }
          offset=(first+length+3)&~3;
        } else {
          const current=bytes.subarray(start,start+length);
          const low=extra.subarray(first,first+length), high=extra.subarray(first+length,first+2*length);
          if (current.length === length && lexical(current,low)>=0 && lexical(current,high)<=0) {
            let difference=0;
            for(let i=0;i<length;i++) difference=difference*256+current[i]-low[i];
            packed=indirect.getInt32((-target+difference)*4,true); start+=length; break;
          }
          offset=(first+2*length+3)&~3;
        }
      }
    }
    const levels = [];
    let offset=packed&0xffffff;
    for(let pass=0;pass<4;pass++) {
      const length=weights[offset++];
      levels.push(weights.subarray(offset,offset+length)); offset+=length;
    }
    result.push({rule:packed>>>24,levels});
  }
  return result;
}
function level(parts, pass) {
  const ordered = [];
  for(let i=0;i<parts.length;) {
    if (rules[parts[i].rule*4+pass]&2) {
      let end=i+1;
      while(end<parts.length && (rules[parts[end].rule*4+pass]&2)) end++;
      const run=parts.slice(i,end).reverse();
      // libc strcoll skips the penultimate backward element when a forward
      // element follows the run; its strxfrm sort keys behave differently.
      if(end<parts.length && run.length>1)run.splice(1,1);
      ordered.push(...run); i=end;
    } else ordered.push(parts[i++]);
  }
  const output = [];
  let distance=0;
  for(const part of ordered) {
    distance++;
    const value=part.levels[pass];
    if (!value.length) continue;
    if (rules[pass]&4) { output.push([distance,...value]); distance=0; }
    else output.push(...value);
  }
  return output;
}
export function createPostgresComparator(locale="en_US.utf8") {
  const name=String(locale).toLowerCase().replace(/[-_.]/g,"");
  const binary=["c","posix","cutf8"].includes(name);
  if (!binary && name !== "enusutf8") throw new Error("Unsupported PostgreSQL collation: "+locale);
  const cache = new Map();
  let cachedCharacters=0;
  function key(value) {
    if (cache.has(value)) return cache.get(value);
    const bytes=encoder.encode(value);
    const parts=binary ? [] : tokens(bytes);
    const result={bytes,levels:binary ? [] : [0,1,2,3].map(pass=>level(parts,pass))};
    if(value.length<=1024 && cache.size<4096 && cachedCharacters+value.length<=131072) {
      cache.set(value,result); cachedCharacters+=value.length;
    }
    return result;
  }
  const compare=(left,right)=>{
    if(left===right)return 0;
    const a=key(left),b=key(right);
    if (!left.length || !right.length) return left.length ? 1 : -1;
    for(let pass=0;pass<a.levels.length;pass++) {
      const x=a.levels[pass],y=b.levels[pass];
      if(rules[pass]&4) {
        for(let i=0;i<Math.min(x.length,y.length);i++) {
          const difference=lexical(x[i],y[i]); if(difference)return difference;
        }
        if(x.length!==y.length)return x.length-y.length;
      } else {
        const difference=lexical(x,y); if(difference)return difference;
      }
    }
    // Deterministic PostgreSQL collations break libc ties by UTF-8 bytes.
    return lexical(a.bytes,b.bytes);
  };
  compare.profile=binary ? "C" : data.profile;
  return compare;
}
