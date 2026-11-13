// Bounds QC for Tactical3D episodes: checks that EVERY screen element (titles, title subs, stamps/result
// badges incl. numbers, player pins, subtitles, freeze/rewind tags, final CTA titles and the logo) stays
// inside the frame and inside the Reels/TikTok/Shorts safe area THROUGHOUT its animation, not on one still.
//
// How: the real composition runs in the real browser with the real fonts, but with `qcProbe` on — the 3D
// scene and audio are skipped and every frame reports the layout box of each [data-qc] element
// (renderFrames, imageFormat 'none', so no pixels are encoded). Boxes with opacity < 0.05 are ignored.
//
// Run: node --experimental-strip-types scripts/qc-bounds.mts <bundle.json> [report.json] [--every N]
// Exit code 1 when any element leaves its area.
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {renderFrames, selectComposition} from '@remotion/renderer';

const args = process.argv.slice(2);
const every = args.includes('--every') ? Number(args[args.indexOf('--every') + 1]) : 1;
const [bundlePath, outFile] = args.filter((a, i) => !a.startsWith('--') && args[i - 1] !== '--every');
// 'default' = the composition's own default props (the Stagger Screen V2 reference episode)
const props = {...(bundlePath === 'default' ? {} : JSON.parse(fs.readFileSync(bundlePath, 'utf8'))), qcProbe: true};
const CHROME = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';

const W = 1080;
const H = 1920;
const FRAME = {left: 24, right: W - 24, top: 24, bottom: H - 24}; // never cut by the frame edge
const SAFE = {left: 40, right: W - 40, top: 220, bottom: H - 420}; // platform header (top) and caption (bottom)
// the platforms' action-button column (like/comment/share) covers the right 150 px between ~y 760 and the caption
const RAIL = {x: W - 150, y0: 760, y1: H - 420};
const SAFE_KINDS = new Set(['title', 'title-sub', 'stamp', 'pin', 'subtitle', 'freeze', 'rewind']);
const TOL = 2;

type Box = {kind: string; text: string; x0: number; y0: number; x1: number; y1: number; op: number};
const viol = new Map<string, {kind: string; text: string; area: string; frames: number[]; worst: number; side: string}>();
let frames = 0;
let boxesSeen = 0;

const outside = (b: Box, a: typeof SAFE, rail = false) => {
  const inRailBand = rail && b.y1 > RAIL.y0 && b.y0 < RAIL.y1;
  const right = inRailBand ? Math.min(a.right, RAIL.x) : a.right;
  const d = {left: a.left - b.x0, right: b.x1 - right, top: a.top - b.y0, bottom: b.y1 - a.bottom};
  const [side, px] = Object.entries(d).sort((x, y) => y[1] - x[1])[0];
  return px > TOL ? {side, px} : null;
};

const entry = path.resolve('src/index.ts');
const serveUrl = await bundle({entryPoint: entry});
const composition = await selectComposition({serveUrl, id: 'Tactical3DV2', inputProps: props, browserExecutable: CHROME});
await renderFrames({
  serveUrl,
  composition,
  inputProps: props,
  imageFormat: 'none',
  everyNthFrame: every,
  concurrency: 4,
  browserExecutable: CHROME,
  outputDir: null,
  onStart: () => undefined,
  onFrameUpdate: () => undefined,
  onBrowserLog: (log) => {
    if (!log.text.startsWith('QCBOX ')) return;
    const {frame, boxes} = JSON.parse(log.text.slice(6)) as {frame: number; boxes: Box[]};
    frames++;
    for (const b of boxes) {
      if (b.op < 0.05) continue;
      boxesSeen++;
      const checks: [string, typeof SAFE][] = [['frame', FRAME]];
      if (SAFE_KINDS.has(b.kind)) checks.push(['safe', SAFE]);
      for (const [area, a] of checks) {
        const o = outside(b, a, area === 'safe');
        if (!o) continue;
        const key = `${b.kind}|${b.text}|${area}`;
        const v = viol.get(key) ?? {kind: b.kind, text: b.text, area, frames: [], worst: 0, side: o.side};
        v.frames.push(frame);
        if (o.px > v.worst) Object.assign(v, {worst: o.px, side: o.side});
        viol.set(key, v);
      }
    }
  },
});

const list = [...viol.values()].map((v) => ({
  kind: v.kind, text: v.text, area: v.area, side: v.side, worst_px: v.worst,
  first_s: +(Math.min(...v.frames) / 30).toFixed(2), last_s: +(Math.max(...v.frames) / 30).toFixed(2), frames: v.frames.length,
}));
const report = {bundle: bundlePath, frames_checked: frames, every_nth_frame: every, boxes_checked: boxesSeen, frame_area: FRAME, safe_area: SAFE, right_rail: RAIL,
  pass: list.length === 0 && frames > 0, violations: list};
for (const v of list) console.log(`FAIL  ${v.kind} "${v.text}" leaves the ${v.area} area (${v.side}, ${v.worst_px}px) ${v.first_s}–${v.last_s}s`);
console.log(`${report.pass ? 'PASS' : 'FAIL'}  bounds: ${frames} frames, ${boxesSeen} boxes, ${list.length} violations`);
if (outFile) fs.writeFileSync(outFile, JSON.stringify(report, null, 1));
process.exit(report.pass ? 0 : 1);
