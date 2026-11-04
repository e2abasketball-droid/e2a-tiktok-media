#!/usr/bin/env node
// Download a freely licensed image from Wikimedia Commons with its credit and licence, ready to
// drop into an episode as a `media` scene. Refuses anything that is not public domain / CC0 / CC BY / CC BY-SA.
// Usage: node scripts/fetch-commons.mjs "File:James Naismith.jpg" public/media/2026-11-04/naismith.jpg
// Needs network access to commons.wikimedia.org and upload.wikimedia.org.
import fs from 'node:fs';
import path from 'node:path';

const [title, out] = process.argv.slice(2);
if (!title || !out) {
  console.error('usage: fetch-commons.mjs "File:<name>" public/media/<date>/<file>');
  process.exit(2);
}
const api = new URL('https://commons.wikimedia.org/w/api.php');
api.search = new URLSearchParams({action: 'query', titles: title, prop: 'imageinfo', iiprop: 'url|extmetadata|size', iiurlwidth: '2160', format: 'json', origin: '*'}).toString();
const ua = {'User-Agent': 'E2A-Reels-Bot/1.0 (video production; contact via GitHub e2abasketball-droid)'};
const j = await (await fetch(api, {headers: ua})).json();
const page = Object.values(j.query.pages)[0];
const info = page.imageinfo?.[0];
if (!info) throw new Error(`not found on Commons: ${title}`);
const meta = info.extmetadata ?? {};
const strip = (s = '') => s.replace(/<[^>]+>/g, '').trim();
const license = strip(meta.LicenseShortName?.value);
const artist = strip(meta.Artist?.value) || 'Unknown';
const ok = /public domain|pd|cc0|cc by(-sa)? \d/i.test(license) && !/nc|nd/i.test(license);
if (!ok) {
  console.error(`REFUSED: licence "${license}" is not allowed (need PD, CC0, CC BY or CC BY-SA)`);
  process.exit(1);
}
const res = await fetch(info.thumburl ?? info.url, {headers: ua});
fs.mkdirSync(path.dirname(out), {recursive: true});
fs.writeFileSync(out, Buffer.from(await res.arrayBuffer()));
const media = {
  src: out.replace(/^public\//, ''),
  kind: /1[89]\d\d|archive/i.test(`${meta.DateTimeOriginal?.value ?? ''}`) ? 'archive' : 'photo',
  credit: `${artist} / Wikimedia Commons`.slice(0, 80),
  license,
  sourceUrl: info.descriptionurl,
};
console.log(JSON.stringify(media, null, 1));
