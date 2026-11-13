#!/usr/bin/env node
// E2A media library: find, licence-check, download and catalogue real images/clips for episodes.
// Sources (free, no paid services):
//   - Wikimedia Commons (players, teams, arenas, history)      no key
//   - Openverse (CC search across Flickr and others)           no key
//   - Pexels / Pixabay (generic B-roll photos AND video clips)  free keys: PEXELS_API_KEY, PIXABAY_API_KEY
// Only public domain, CC0, CC BY and CC BY-SA (or the Pexels/Pixabay licences, for generic B-roll) pass.
// Everything is catalogued in media-library.json (source, licence, author, year, local file), so the same
// search or file is never fetched twice and files are reused across episodes.
//
//   node scripts/media-library.mjs search "Reggie Miller" --role subject [--max 6] [--video]
//   node scripts/media-library.mjs fetch <id> [public/media/library/<file>]
//   node scripts/media-library.mjs list [--role broll] [--q hoop]
//
// role: subject (the player/team/person: Commons + Openverse only, never stock), place (arena, city),
// broll (generic basketball: ball, hoop, crowd, court; stock allowed). The printed `media` object can be
// pasted into an episode (media / bg / inset). Credits for stock are labelled as generic footage.
import fs from 'node:fs';
import path from 'node:path';

const LIB = new URL('../media-library.json', import.meta.url).pathname;
const PUB = new URL('../public/', import.meta.url).pathname;
const UA = {'User-Agent': 'E2A-Reels-Bot/1.0 (sports video production; github.com/e2abasketball-droid)'};
const lib = fs.existsSync(LIB) ? JSON.parse(fs.readFileSync(LIB, 'utf8')) : {searches: {}, items: {}};
const save = () => fs.writeFileSync(LIB, JSON.stringify(lib, null, 1));

const args = process.argv.slice(2);
const cmd = args[0];
const opt = (k, d) => {
  const i = args.indexOf(`--${k}`);
  return i < 0 ? d : args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
};
const strip = (s = '') => String(s).replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/** fetch with polite retries: honours Retry-After on 429/503, max 3 tries */
async function get(url, init = {}, tries = 3) {
  for (let k = 0; k < tries; k++) {
    const r = await fetch(url, {...init, headers: {...UA, ...(init.headers ?? {})}});
    if (r.status !== 429 && r.status !== 503) return r;
    const wait = Math.min(120, parseInt(r.headers.get('retry-after') ?? '20', 10) || 20);
    console.error(`  ${r.status} from ${new URL(url).host}, waiting ${wait}s`);
    await sleep(wait * 1000);
  }
  throw new Error(`rate-limited: ${url}`);
}

const ALLOWED = (lic) => {
  const l = lic.toLowerCase();
  if (/\bnc\b|non-?commercial|\bnd\b|no ?deriv/.test(l)) return false;
  return /public domain|^pd\b|pdm|cc0|cc[ -]by(-sa)?\b|pexels|pixabay/.test(l);
};
const yearOf = (s = '') => (String(s).match(/\b(18|19|20)\d{2}\b/) ?? [])[0];

// ------------------------------------------------------------------ sources
async function commons(q, max) {
  const u = new URL('https://commons.wikimedia.org/w/api.php');
  u.search = new URLSearchParams({action: 'query', format: 'json', generator: 'search', gsrsearch: `${q} filetype:bitmap`, gsrnamespace: '6', gsrlimit: String(max * 2), prop: 'imageinfo', iiprop: 'url|size|extmetadata', iiurlwidth: '1920'}).toString();
  const j = await (await get(u)).json();
  return Object.values(j.query?.pages ?? {}).map((p) => {
    const i = p.imageinfo?.[0] ?? {};
    const m = i.extmetadata ?? {};
    return {
      id: `commons:${p.pageid}`, source: 'Wikimedia Commons', title: p.title.replace(/^File:/, ''), kind: 'photo',
      url: i.thumburl ?? i.url, w: i.thumbwidth ?? i.width, h: i.thumbheight ?? i.height, sourceUrl: i.descriptionurl,
      license: strip(m.LicenseShortName?.value), author: strip(m.Artist?.value) || 'Unknown',
      year: yearOf(m.DateTimeOriginal?.value) ?? yearOf(p.title), description: strip(m.ImageDescription?.value).slice(0, 200),
    };
  });
}
async function openverse(q, max) {
  const u = new URL('https://api.openverse.org/v1/images/');
  u.search = new URLSearchParams({q, license_type: 'commercial,modification', page_size: String(max * 2)}).toString();
  const j = await (await get(u)).json();
  return (j.results ?? []).map((r) => ({
    id: `openverse:${r.id}`, source: r.source ?? 'Openverse', title: r.title ?? q, kind: 'photo', url: r.url, w: r.width, h: r.height,
    sourceUrl: r.foreign_landing_url, license: `${r.license === 'pdm' ? 'Public domain' : r.license === 'cc0' ? 'CC0' : `CC ${r.license.toUpperCase()}`} ${r.license_version ?? ''}`.trim(),
    author: r.creator ?? 'Unknown', year: yearOf(r.title), description: (r.tags ?? []).map((t) => t.name).slice(0, 8).join(', '),
  }));
}
async function pexels(q, max, video) {
  const key = process.env.PEXELS_API_KEY;
  if (!key) return [];
  const u = new URL(video ? 'https://api.pexels.com/videos/search' : 'https://api.pexels.com/v1/search');
  u.search = new URLSearchParams({query: q, per_page: String(max), orientation: 'portrait'}).toString();
  const j = await (await get(u, {headers: {Authorization: key}})).json();
  return (video ? j.videos : j.photos ?? []).map((r) => {
    const f = video ? (r.video_files ?? []).filter((x) => x.file_type === 'video/mp4').sort((a, b) => Math.abs(a.height - 1920) - Math.abs(b.height - 1920))[0] : null;
    return {
      id: `pexels:${video ? 'v' : 'p'}${r.id}`, source: 'Pexels', title: r.alt || q, kind: video ? 'video' : 'photo',
      url: video ? f?.link : r.src?.large2x, w: video ? f?.width : r.width, h: video ? f?.height : r.height, sourceUrl: r.url,
      license: 'Pexels License', author: video ? r.user?.name : r.photographer, year: undefined, description: r.alt ?? '',
    };
  });
}
async function pixabay(q, max, video) {
  const key = process.env.PIXABAY_API_KEY;
  if (!key) return [];
  const u = new URL(video ? 'https://pixabay.com/api/videos/' : 'https://pixabay.com/api/');
  u.search = new URLSearchParams({key, q, per_page: String(Math.max(3, max)), safesearch: 'true'}).toString();
  const j = await (await get(u)).json();
  return (j.hits ?? []).map((r) => {
    const f = video ? r.videos?.large ?? r.videos?.medium : null;
    return {
      id: `pixabay:${video ? 'v' : 'p'}${r.id}`, source: 'Pixabay', title: r.tags || q, kind: video ? 'video' : 'photo',
      url: video ? f?.url : r.largeImageURL, w: video ? f?.width : r.imageWidth, h: video ? f?.height : r.imageHeight, sourceUrl: r.pageURL,
      license: 'Pixabay Content License', author: r.user, year: undefined, description: r.tags ?? '',
    };
  });
}

// ------------------------------------------------------------------ ranking
const score = (it, q, role) => {
  const words = q.toLowerCase().split(/\s+/).filter((w) => w.length > 2);
  const hay = `${it.title} ${it.description}`.toLowerCase();
  const match = words.filter((w) => hay.includes(w)).length / Math.max(1, words.length);
  const px = Math.min(1, ((it.w ?? 0) * (it.h ?? 0)) / (1080 * 1350));
  const portrait = (it.h ?? 0) >= (it.w ?? 1) ? 0.15 : 0;
  const video = it.kind === 'video' ? 0.2 : 0;
  // a subject must actually be named in the title/description, or it is not the subject
  if (role === 'subject' && match < 1) return -1;
  return +(match * 0.55 + px * 0.3 + portrait + video).toFixed(3);
};

const asMedia = (it, role) => ({
  src: it.local ?? `(run: node scripts/media-library.mjs fetch ${it.id})`,
  kind: it.kind === 'video' ? 'video' : 'photo',
  credit: `${role === 'broll' && !it.year ? 'Basketball footage' : it.title.replace(/\.(jpe?g|png|webp|tiff?)$/i, '').slice(0, 48)}${it.year ? `, ${it.year}` : ''} · ${it.author.split(' from ')[0].slice(0, 40)} · ${it.license}`,
  license: it.license,
  sourceUrl: it.sourceUrl,
});

// ------------------------------------------------------------------ commands
if (cmd === 'search') {
  const q = args[1];
  const role = opt('role', 'broll');
  const max = parseInt(opt('max', '6'), 10);
  const video = opt('video', false) === true;
  if (!q || !['subject', 'place', 'broll'].includes(role)) {
    console.error('usage: media-library.mjs search "<query>" --role subject|place|broll [--max 6] [--video]');
    process.exit(2);
  }
  const key = `${role}|${video ? 'v' : 'p'}|${q.toLowerCase()}`;
  let ids = lib.searches[key]?.ids;
  if (!ids) {
    const jobs = [commons(q, max), openverse(q, max)];
    if (role !== 'subject') jobs.push(pexels(q, max, video), pixabay(q, max, video)); // stock only for generic shots
    const settled = await Promise.allSettled(jobs);
    const failed = settled.filter((r) => r.status === 'rejected').length;
    const res = settled.flatMap((r) => (r.status === 'fulfilled' ? r.value : (console.error(`  source failed: ${r.reason?.message ?? r.reason}`), [])));
    ids = [];
    const seenUrl = new Set(Object.values(lib.items).map((x) => x.sourceUrl));
    for (const it of res) {
      if (!it.url || !ALLOWED(it.license ?? '')) continue;
      if (lib.items[it.id]) {
        ids.push(it.id);
        continue;
      }
      if (seenUrl.has(it.sourceUrl)) continue; // same file found through another source
      seenUrl.add(it.sourceUrl);
      lib.items[it.id] = {...it, roles: [role]};
      ids.push(it.id);
    }
    if (!failed) lib.searches[key] = {ids, at: new Date().toISOString()}; // never cache a partial search
    save();
  }
  const ranked = ids
    .map((id) => lib.items[id])
    .map((it) => ({it, s: score(it, q, role)}))
    .filter((x) => x.s >= 0)
    .sort((a, b) => b.s - a.s)
    .slice(0, max);
  console.log(JSON.stringify(ranked.map(({it, s}) => ({id: it.id, score: s, title: it.title, year: it.year, size: `${it.w}x${it.h}`, license: it.license, source: it.source, local: it.local, media: asMedia(it, role)})), null, 1));
  if (!ranked.length) console.error(role === 'subject' ? 'no free-licence image names this subject: use place/broll images, never a lookalike' : 'nothing found');
} else if (cmd === 'fetch') {
  const it = lib.items[args[1]];
  if (!it) throw new Error(`unknown id ${args[1]}: run search first`);
  if (it.local && fs.existsSync(path.join(PUB, it.local))) {
    console.log(JSON.stringify({id: it.id, local: it.local, cached: true}));
    process.exit(0);
  }
  const ext = it.kind === 'video' ? '.mp4' : (/\.(png|webp)(\?|$)/i.exec(it.url)?.[0]?.replace('?', '') ?? '.jpg');
  const rel = args[2] ? path.relative(PUB, path.resolve(args[2])) : `media/library/${it.id.replace(/[^a-z0-9]+/gi, '-')}${ext}`;
  const r = await get(it.url);
  if (!r.ok) throw new Error(`download failed ${r.status}`);
  fs.mkdirSync(path.dirname(path.join(PUB, rel)), {recursive: true});
  fs.writeFileSync(path.join(PUB, rel), Buffer.from(await r.arrayBuffer()));
  it.local = rel;
  it.fetchedAt = new Date().toISOString();
  save();
  console.log(JSON.stringify({id: it.id, local: rel, media: asMedia(it, it.roles?.[0] ?? 'broll')}, null, 1));
} else if (cmd === 'list') {
  const role = opt('role');
  const q = opt('q');
  const items = Object.values(lib.items).filter((it) => (!role || it.roles?.includes(role)) && (!q || `${it.title} ${it.description}`.toLowerCase().includes(String(q).toLowerCase())));
  console.log(JSON.stringify(items.map((it) => ({id: it.id, title: it.title, license: it.license, local: it.local ?? null})), null, 1));
} else {
  console.error('commands: search | fetch | list (see the header of this file)');
  process.exit(2);
}
