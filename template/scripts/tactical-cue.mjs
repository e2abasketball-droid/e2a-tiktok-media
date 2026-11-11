// Resolve an episode cue (number or narration anchor "phrase[>][+-offset]") to seconds on the final voice.
// Usage: node scripts/tactical-cue.mjs tactical/episodes/<id>.json <key>   (e.g. musicDrop)
import fs from 'node:fs';
const [epFile, key] = process.argv.slice(2);
const ep = JSON.parse(fs.readFileSync(epFile, 'utf8'));
const words = JSON.parse(fs.readFileSync(epFile.replace(/\.json$/, '.words.json'), 'utf8'));
let a = ep[key];
if (a === undefined || a === null) process.exit(0);
if (typeof a === 'number') { console.log(a); process.exit(0); }
const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]/g, '');
let off = 0;
const m = a.match(/([+-]\d+(?:\.\d+)?)$/);
if (m) { off = parseFloat(m[1]); a = a.slice(0, -m[1].length); }
const atEnd = a.trim().endsWith('>');
const p = a.replace(/>\s*$/, '').split(/\s+/).map(norm).filter(Boolean);
const k = words.map((w) => norm(w.text));
for (let i = 0; i + p.length <= k.length; i++)
  if (p.every((x, j) => k[i + j] === x)) { console.log(((atEnd ? words[i + p.length - 1].end : words[i].start) + off).toFixed(2)); process.exit(0); }
throw new Error(`cue not found: ${ep[key]}`);
