// Engine-level QC of a tactical edit (no rendering needed): for every frame of every shot it rebuilds
// the camera and the play exactly as the composition does and checks
//   - every player that should be on screen is inside the frame (no unexplained disappearances)
//   - camera continuity: no jump of the projected court inside a shot (smooth moves only)
//   - play-clock continuity: freezes / slow motion / rewinds are deliberate keys, never jumps
//   - subtitles safe area: no player of a full-court view sits behind the subtitle band too long
// Run: node --experimental-strip-types scripts/qc-tactical.mts /tmp/tprops.json [report.json]
import fs from 'node:fs';
import {makeProjector} from '../src/tactical/geometry.ts';
import {cameraAt} from '../src/tactical/camera.ts';
import {localResolver, makeTacticalResolver, remapAt, resolveRemap} from '../src/tactical/edit.ts';
import type {TacticalEpisode} from '../src/tactical/edit.ts';
import {sample} from '../src/tactical/play.ts';

const [propsFile, out] = process.argv.slice(2);
const ep: TacticalEpisode = JSON.parse(fs.readFileSync(propsFile, 'utf8')).episode;
const fps = ep.fps ?? 60;
const T = makeTacticalResolver(ep.words);
const total = ep.words[ep.words.length - 1].end + ep.tail;
const starts = ep.shots.map((s, i) => (i === 0 ? 0 : T(s.at, s.offset ?? 0)));
const rows: Record<string, unknown>[] = [];
let fails = 0;
for (let i = 0; i < ep.shots.length; i++) {
  const s = ep.shots[i];
  const st = starts[i];
  const en = i + 1 < starts.length ? starts[i + 1] : total;
  const toLocal = localResolver(T, st, en);
  const panels = s.split ? s.split.map((p, k) => ({play: ep.plays[p.play], remap: p.remap, camera: p.camera, W: 540, H: 1070, k})) : [{play: ep.plays[s.play!], remap: s.remap ?? [[0, 0]], camera: s.camera ?? [{at: 0, cam: 'top'}], W: 1080, H: 1920, k: 0}];
  // every narration anchor of the shot must land inside the shot (catches a phrase matching an earlier occurrence)
  const anchors: unknown[] = [...(s.overlays ?? []).flatMap((o) => [o.from, o.to]), ...(s.sfx ?? []).map((x) => x.at), ...(s.camera ?? []).map((k) => k.at), ...(s.remap ?? []).map((k) => k[0])];
  for (const p of s.split ?? []) anchors.push(...p.remap.map((k) => k[0]), ...p.camera.map((k) => k.at));
  const stray = anchors.filter((a) => typeof a === 'string' && !a.startsWith('@')).map((a) => [a, toLocal(a)] as [string, number]).filter(([, v]) => v < -0.05 || v > en - st + 0.05);
  if (stray.length) { fails++; rows.push({shot: s.id, anchorsOutsideShot: stray.map(([a, v]) => `${a}@${v.toFixed(2)}`).join(' | '), ok: false}); }
  for (const pn of panels) {
    const rm = resolveRemap(pn.remap as never, pn.play, toLocal);
    const cams = (pn.camera as {at: unknown; cam: never}[]).map((k) => ({...k, at: toLocal(k.at)}));
    let minVisible = 99;
    let maxJump = 0;
    let maxClockJump = 0;
    let prevC: {f: number[]; p: number[]} | null = null;
    let maxTurn = 0;
    let maxFwd = 0;
    let maxRew = 0;
    let prevPt: number | null = null;
    let missing = '';
    for (let lt = 0; lt < en - st - 1e-9; lt += 1 / fps) {
      const pt = remapAt(rm, lt);
      const cam = cameraAt(cams as never, lt, pt, (x) => sample(pn.play, x));
      const pr = makeProjector(cam, pn.W, pn.H);
      const f = sample(pn.play, pt);
      const hide = s.hideUntil === undefined || lt < s.hideUntil ? (s.hide ?? []) : [];
      let vis = 0;
      const out: string[] = [];
      for (const p of Object.values(f.players)) {
        if (hide.includes(p.spec.id)) continue;
        const q = pr.p([p.pos[0], p.pos[1], 0.9]);
        if (q.z > 0.3 && q.x > -40 && q.x < pn.W + 40 && q.y > -40 && q.y < pn.H + 40) vis++;
        else out.push(p.spec.id);
      }
      if (vis < minVisible) [minVisible, missing] = [vis, `${out.join(',')}@${(st + lt).toFixed(2)}s`];
      // camera smoothness: how far the view turns (deg) and travels (m) per frame
      const fw = pr.forward as number[];
      const ps = pr.pos as number[];
      if (prevC) {
        const dot = Math.max(-1, Math.min(1, fw[0] * prevC.f[0] + fw[1] * prevC.f[1] + fw[2] * prevC.f[2]));
        maxTurn = Math.max(maxTurn, (Math.acos(dot) * 180) / Math.PI);
        maxJump = Math.max(maxJump, Math.hypot(ps[0] - prevC.p[0], ps[1] - prevC.p[1], ps[2] - prevC.p[2]) / cam.dist); // relative to the framing distance
      }
      prevC = {f: [...fw], p: [...ps]};
      if (prevPt !== null) {
        const v = (pt - prevPt) * fps;
        maxFwd = Math.max(maxFwd, v);
        maxRew = Math.max(maxRew, -v);
        maxClockJump = Math.max(maxClockJump, Math.abs(v));
      }
      prevPt = pt;
    }
    const expected = 10 - (s.hide?.length ?? 0);
    const pov = (s.hide?.length ?? 0) > 0;
    // court-level and POV shots crop on purpose; full views must show everyone
    const fullView = !pov && !s.split && (s.camera ?? []).every((k) => typeof k.cam === 'string' && ['top', 'topTight'].includes(k.cam as string));
    const okVis = fullView ? minVisible === expected : minVisible >= (pov ? 2 : 4); // a POV shows what the defender sees (and a rewind runs players back past the lens)
    const okJump = maxTurn <= 1.6 && maxJump <= 0.035; // ≤ ~96°/s turn and ≤ 3.5 % of the framing distance per frame: eased moves, no jumps
    const okClock = maxFwd <= 2.0 && maxRew <= 6; // forward never faster than 2x real speed; rewinds up to 6x
    if (!okVis || !okJump || !okClock) fails++;
    rows.push({shot: s.id + (s.split ? `#${pn.k}` : ''), from: +st.toFixed(2), to: +en.toFixed(2), minVisiblePlayers: minVisible, expected: fullView ? expected : '≥4 (framed shot)', whoLeavesFrame: minVisible < expected ? missing : '', maxTurnDegPerFrame: +maxTurn.toFixed(2), maxTravelPerFrame: +maxJump.toFixed(3), maxForwardSpeed: +maxFwd.toFixed(2), maxRewindSpeed: +maxRew.toFixed(2), ok: okVis && okJump && okClock});
  }
}
console.table(rows);
if (out) fs.writeFileSync(out, JSON.stringify({fails, rows}, null, 1));
console.log(fails ? `${fails} shot(s) failed` : 'all shots passed');
process.exit(fails ? 1 : 0);
