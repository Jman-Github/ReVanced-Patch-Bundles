/* Character classes and simple case maps exported from PostgreSQL libc
 * en_US.utf8, using the generator in internal/generate_locale_data.mjs.
 * Reference: https://www.postgresql.org/docs/17/functions-matching.html
 * Generated lookup data; no PostgreSQL implementation code is incorporated.
 */
import data from "./postgres-locales.json" with {type:"json"};
import { CatalogError } from "../../shared/catalog.js";

const profiles=new Map();
function contains(ranges, code) {
  let low=0,high=ranges.length/2-1;
  while(low<=high) {
    const middle=(low+high)>>1;
    if(code<ranges[middle*2]) high=middle-1;
    else if(code>ranges[middle*2+1]) low=middle+1;
    else return true;
  }
  return false;
}
export function regexLocale(name,portable) {
  const normalized=String(name).toLowerCase().replace(/[-_.]/g,"");
  if(["c","posix"].includes(normalized)) return portable;
  const key=["enusutf8","cutf8"].includes(normalized) ? "en_US.utf8" : name;
  const profile=data[key];
  if(!profile) throw new CatalogError("Unsupported PostgreSQL locale profile: "+name,503);
  if(profiles.has(key)) return profiles.get(key);
  const inverse=new Map();
  for(const mapping of [profile.lower,profile.upper]) for(const [from,to] of Object.entries(mapping)) {
    if(!inverse.has(to)) inverse.set(to,new Set());
    inverse.get(to).add(String.fromCodePoint(Number(from)));
  }
  const result = {
    caseSources:char=>[char,...(inverse.get(char.codePointAt(0))??[])],
    classes:Object.fromEntries(Object.entries(profile.classes).map(([key,ranges])=>
      [key,char=>contains(ranges,char.codePointAt(0))])),
    fold:value=>Array.from(value,c=>String.fromCodePoint(profile.lower[c.codePointAt(0)]??c.codePointAt(0))).join(""),
    upper:value=>Array.from(value,c=>String.fromCodePoint(profile.upper[c.codePointAt(0)]??c.codePointAt(0))).join("")
  };
  profiles.set(key,result);
  return result;
}
