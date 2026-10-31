#!/usr/bin/env node
// Usage: node render-carousel.mjs <spec.json> <outDir> [prefix]   → <prefix>_slide01.png … (1080x1350)
// Spec: {pillar, accent, slides:[{type:'cover'|'diagram'|'text'|'cta', kicker, title, body, diagram?:{players,arrows,...}}]}
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const require = createRequire('/opt/node-tools/node_modules/');
const {chromium} = require('playwright');
const here = path.dirname(fileURLToPath(import.meta.url));
const pub = path.join(here, '../breakdown-template/public');
const [specF, outDir, prefix = 'post'] = process.argv.slice(2);
const spec = JSON.parse(fs.readFileSync(specF, 'utf8'));
fs.mkdirSync(outDir, {recursive: true});
const b64 = (f, m) => `data:${m};base64,${fs.readFileSync(f).toString('base64')}`;
const FONT = `@font-face{font-family:Anton;src:url(${b64(path.join(pub, 'anton.woff2'), 'font/woff2')})}@font-face{font-family:Inter;font-weight:100 900;src:url(${b64(path.join(pub, 'inter.woff2'), 'font/woff2')})}`;
const LOGO = b64(path.join(here, '../assets/E2A_LOGO_white.png'), 'image/png');
const N = '#0B1B36', G = '#C9A44C', W = '#fff';
const S = 17.6, CW = 50 * S, CH = 47 * S;
const px = ([x, y]) => [x * S, (47 - y) * S];
function court(d) {
  const bx = 25 * S, by = (47 - 5.25) * S, R = 22.1 * S, L = 16 * S;
  let s = `<svg width="${CW}" height="${CH}" viewBox="0 0 ${CW} ${CH}" style="border-radius:22px;border:3px solid ${G}"><rect width="${CW}" height="${CH}" fill="#102a52"/>`;
  s += `<g fill="none" stroke="rgba(255,255,255,.75)" stroke-width="4"><rect x="${(CW - L) / 2}" y="${CH - 19 * S}" width="${L}" height="${19 * S}" fill="rgba(201,164,76,.14)"/><circle cx="${bx}" cy="${CH - 19 * S}" r="${6 * S}"/><path d="M ${bx - R} ${CH} L ${bx - R} ${by} A ${R} ${R} 0 0 1 ${bx + R} ${by} L ${bx + R} ${CH}"/><circle cx="${bx}" cy="${by}" r="${.75 * S}" stroke="${G}" stroke-width="5"/></g>`;
  for (const z of d.zones ?? []) { const [x, y] = px(z); s += `<circle cx="${x}" cy="${y}" r="${z[2] * S}" fill="rgba(215,38,61,.18)" stroke="#D7263D" stroke-width="4" stroke-dasharray="10 8"/>`; }
  for (const a of d.arrows ?? []) {
    const f = px(a.from), t = px(a.to), ang = Math.atan2(t[1] - f[1], t[0] - f[0]) * 180 / Math.PI;
    const col = a.kind === 'gold' ? G : '#fff';
    s += `<line x1="${f[0]}" y1="${f[1]}" x2="${t[0]}" y2="${t[1]}" stroke="${col}" stroke-width="6" stroke-linecap="round" ${a.kind === 'pass' ? 'stroke-dasharray="4 16"' : a.kind === 'measure' ? 'stroke-dasharray="14 10"' : ''}/>`;
    if (a.kind !== 'measure') s += `<polygon points="0,0 -22,-11 -22,11" fill="${col}" transform="translate(${t[0]} ${t[1]}) rotate(${ang})"/>`;
    if (a.label) s += `<text x="${(f[0] + t[0]) / 2}" y="${(f[1] + t[1]) / 2 - 12}" text-anchor="middle" font-family="Inter" font-weight="800" font-size="30" fill="${G}" stroke="#102a52" stroke-width="6" paint-order="stroke">${a.label}</text>`;
  }
  for (const p of d.players) { const [x, y] = px(p.at); s += p.d
    ? `<g transform="translate(${x} ${y})" stroke="#fff" stroke-width="9" stroke-linecap="round"><line x1="-17" y1="-17" x2="17" y2="17"/><line x1="17" y1="-17" x2="-17" y2="17"/></g>`
    : `<g transform="translate(${x} ${y})"><circle r="30" fill="${N}" stroke="${G}" stroke-width="6"/><text text-anchor="middle" dy="13" font-family="Anton" font-size="36" fill="#fff">${p.n}</text></g>`; }
  if (d.ball) { const [x, y] = px(d.ball); s += `<circle cx="${x + 24}" cy="${y + 24}" r="15" fill="#E07B2A" stroke="#6b2f08" stroke-width="3"/>`; }
  return s + '</svg>';
}
const head = (sl, i, n) => `<div class="top"><div class="logo"><img src="${LOGO}"></div><div class="pill">${spec.pillar}</div><div class="pg">${i + 1} / ${n}</div></div>`;
function slide(sl, i, n) {
  let inner = '';
  if (sl.type === 'cover') inner = `<div class="cov"><div class="kick">${sl.kicker}</div><h1>${sl.title}</h1><p class="sub">${sl.body}</p><div class="swipe">SWIPE ➜</div></div>`;
  else if (sl.type === 'diagram') inner = `<div class="mid"><div class="kick">${sl.kicker}</div><h2>${sl.title}</h2><div class="dg">${court(sl.diagram)}</div><p class="cap">${sl.body}</p></div>`;
  else if (sl.type === 'cta') inner = `<div class="cov"><div class="bigl"><img src="${LOGO}"></div><h2 style="font-size:92px;text-align:center">${sl.title}</h2><p class="sub" style="text-align:center">${sl.body}</p><div class="swipe" style="align-self:center">MORE THAN A GAME</div></div>`;
  else inner = `<div class="mid txt"><div class="kick">${sl.kicker}</div><h2>${sl.title}</h2><p class="cap">${sl.body}</p></div>`;
  return `<section>${head(sl, i, n)}${inner}<div class="foot">@e2a_basketball · Connecting Australia and Europe through basketball</div></section>`;
}
const css = `${FONT}*{box-sizing:border-box;margin:0}body{background:#000}section{width:1080px;height:1350px;position:relative;overflow:hidden;background:radial-gradient(circle at 30% 20%,#17335f,${N} 65%);color:${W};font-family:Inter;display:flex;flex-direction:column;padding:56px}
.top{display:flex;align-items:center;gap:20px}.logo{width:150px;height:113px}.logo img{width:150px}
.pill{font:600 24px Inter;letter-spacing:5px;color:${G};text-transform:uppercase;flex:1}.pg{font:700 26px Inter;color:rgba(255,255,255,.6)}
.cov{flex:1;display:flex;flex-direction:column;justify-content:center;gap:28px}.kick{font:400 34px Anton;letter-spacing:6px;color:${G};text-transform:uppercase}
h1{font:400 150px/1 Anton;text-transform:uppercase}h2{font:400 84px/1.02 Anton;text-transform:uppercase}.sub{font:500 40px/1.35 Inter;color:rgba(255,255,255,.85)}
.swipe{font:400 34px Anton;letter-spacing:4px;color:${N};background:${G};padding:14px 30px;border-radius:12px;align-self:flex-start}
.mid{flex:1;display:flex;flex-direction:column;justify-content:flex-start;gap:16px;padding-top:34px;padding-bottom:50px}.dg{display:flex;justify-content:center}.dg svg{zoom:.78}.cap{font:500 35px/1.3 Inter;color:rgba(255,255,255,.9)}h2{font-size:76px}
.mid.txt{justify-content:center;gap:30px;padding-top:0}.mid.txt h2{font-size:96px}.mid.txt .cap{font-size:42px;line-height:1.35}.bigl{width:560px;align-self:center}.bigl img{width:560px}
.foot{position:absolute;left:56px;right:56px;bottom:22px;font:600 22px Inter;color:rgba(255,255,255,.55);text-align:center;letter-spacing:1px}`;
const html = `<html><head><meta charset=utf-8><style>${css}</style></head><body>${spec.slides.map((s, i) => slide(s, i, spec.slides.length)).join('')}</body></html>`;
const browser = await chromium.launch();
const page = await browser.newPage({viewport: {width: 1080, height: 1350}});
await page.setContent(html); await page.evaluate(() => document.fonts.ready);
const secs = await page.$$('section');
for (let i = 0; i < secs.length; i++) await secs[i].screenshot({path: path.join(outDir, `${prefix}_slide${String(i + 1).padStart(2, '0')}.png`)});
await browser.close(); console.log(`${secs.length} slides → ${outDir}`);
