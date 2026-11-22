// E2A Realism V3.3 (2026-11-22) — copy of qc-realism-v32.mts (unchanged there) with motion 'v33' added. The ORIGINAL
// detectors and thresholds are byte-identical below; V3.3 adds (a) an anatomical ball-body detector with tapered
// mesh-measured radii and a contact classification, (b) a per-frame ball/event CSV, (c) the V3.3 source per player.
// --- V3.2 header follows ---
// E2A Realism V3.2 (2026-11-22) — per-frame motion QC on the SOLVED bones (the same code path as the render:
// realism-v3-2/scene32.athleteV32), for any motion generation on the same V3.2 skeleton (engine = legacy motion,
// v31, v32), so the three generations are measured with one ruler.
//   npx tsx scripts/qc-realism-v32.mts <play.json> [--players O1] [--motion v32|v31|engine] [--props ep.props.json]
//        [--json out.json] [--frames out-frames.json]
// Checks (tolerances from sport sizes, provisional, see produccion/realism-v3-2/QA.md):
//   foot slide   ball-of-foot horizontal travel while that point is on the floor (z < 1.5 cm) for >= 3 frames (120 Hz)
//                tolerance 2 cm per contact (a planted sneaker does not slide; > 2 cm reads as skating)
//   floor        lowest heel / ball point: < -1 cm = the foot sinks into the court
//   joints       knee flexion > 150 deg or < -3 deg (hyper-extension), elbow > 155 deg, neck yaw off the chest > 80 deg
//   pops         pelvis acceleration > 60 m/s^2 outside a landing window (a landing peaks ~ 50-120 m/s^2 for 0.1 s),
//                hands > 400 m/s^2 outside release / catch windows; per-frame 2nd difference at 120 Hz
//   ball / hand  palm gap to the ball surface while held (target 1.2 cm, visible gap > 5 cm), first contact time
//   ball / body  ball centre inside a body capsule (trunk 0.14 m, upper arm 0.05, forearm 0.04 over the elbow -> 80 % of the wrist (the palm holds the ball against the wrist), thigh 0.08, head
//                0.11) + ball radius - 1 cm, while the ball is not in the hands of this player or in flight far away
//   limbs        shoulder -> wrist distance / arm length > 0.995 (locked straight, the IK popping), apparent
//                hip -> ankle / leg > 1.0
//   visibility   (with --props) ray camera -> head / hands / feet / ball blocked by another player's capsule (r 0.28 m)
// Writes the per-frame defect rows (t, kind, value) for the defect contact sheet (scripts/defect_sheet_v32.py).
import fs from 'node:fs';
import '../src/t3d/rig.ts';
import '../src/t3d/players/index.ts';
import type {V3} from '../src/tactical/geometry.ts';
import {posAt, sample} from '../src/tactical/play.ts';
import type {PlayWithActions} from '../src/t3d/rig.ts';
import {qconj, qmul, qrot} from '../src/t3d/skelclip.ts';
import {fkHeads, palmWorld} from '../src/t3d/realism-v3/athleteV3.ts';
import {PLAYER3D_V32} from '../src/t3d/realism-v3-2/index.ts';
import {athleteV32} from '../src/t3d/realism-v3-2/scene32.ts';
import type {Motion} from '../src/t3d/realism-v3-2/scene32.ts';
import {ballV32, resetV32Caches} from '../src/t3d/realism-v3-2/motion32.ts';
import {ballV31} from '../src/t3d/realism-v3-1/motion.ts';
import {athleteV33} from '../src/t3d/realism-v3-3/scene33.ts';
import {ballV33, ballOwner33, resetV33Caches} from '../src/t3d/realism-v3-3/motion33.ts';
import {ANAT33, anatomicalHits} from './qc-anat33.mts';
import {camera3At} from '../src/t3d/camera3d.ts';
import {remapAt, resolveRemap, localResolver} from '../src/tactical/edit.ts';

const args = process.argv.slice(2);
const opt = (k: string, d: string) => (args.includes(k) ? args[args.indexOf(k) + 1] : d);
const file = args[0];
const play = JSON.parse(fs.readFileSync(file, 'utf8')) as PlayWithActions;
const ids = opt('--players', 'O1').split(',');
const motion = opt('--motion', 'v32') as Motion | 'v33';
const HZ = 120;
const N = Math.round(play.duration * HZ);
const BALL_R = 0.121;
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a: V3, k: number): V3 => [a[0] * k, a[1] * k, a[2] * k];
const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const r3 = (x: number) => Math.round(x * 1000) / 1000;
const ang = (a: V3, b: V3) => (Math.acos(Math.max(-1, Math.min(1, dot(a, b) / (len(a) * len(b) || 1)))) * 180) / Math.PI;
const segDist = (p: V3, a: V3, b: V3) => {
  const ab = sub(b, a);
  const u = Math.max(0, Math.min(1, dot(sub(p, a), ab) / Math.max(1e-9, dot(ab, ab))));
  return len(sub(p, add(a, mul(ab, u))));
};
const rigOf = (id: string) => PLAYER3D_V32[play.players.find((p) => p.id === id)?.team === 'X' ? 'def' : 'off'].rig;
const ballAt = (t: number): V3 => {
  const e = sample(play, t).ball.pos as V3;
  if (motion === 'v33') return ballV33(play, t);
  if (motion === 'v32') return ballV32(play, t, rigOf) ?? e;
  if (motion === 'v31') return ballV31(play, t, rigOf) ?? e;
  return e;
};
type J = Record<string, V3>;
// the play's dribble holds (same window for every motion generation, so the palm gap is measured on equal terms)
const dribbling = (t: number) => (play.ball as {type: string; dribble?: boolean; from?: number; to?: number}[]).some((e) => e.type === 'hold' && e.dribble && t >= (e.from as number) && t < (e.to as number));
const jointsOf = (id: string, t: number) => {
  const rig = rigOf(id);
  const b = sample(play, t).ball;
  const bc = {holder: b.holder, pos: b.pos, lag: sample(play, Math.max(0, t - 0.2)).ball.pos};
  const a = motion === 'v33' ? athleteV33(play, id, t, rig, bc) : athleteV32(play, id, t, rig, bc, motion);
  const at = fkHeads(rig, a.fr.bones, a.fr.hips, a.sc);
  const by = new Map(rig.bones.map((x) => [x.name, x] as const));
  const pt = (bone: string, k: string): V3 => {
    const fb = by.get(bone)!;
    const D = qmul(a.fr.bones[bone], qconj(fb.R));
    return add(at(bone), qrot(D, mul(sub(rig.restJoints[k], fb.head), a.sc)));
  };
  const j: J = {pelvis: at('hips'), chest: at('chest'), neck: at('neck'), head: at('head')};
  for (const s of ['L', 'R']) {
    j[`sh${s}`] = at(`upperarm.${s}`);
    j[`el${s}`] = at(`forearm.${s}`);
    j[`wr${s}`] = at(`hand.${s}`);
    j[`hip${s}`] = at(`thigh.${s}`);
    j[`kn${s}`] = at(`shin.${s}`);
    j[`an${s}`] = at(`foot.${s}`);
    j[`heel${s}`] = pt(`foot.${s}`, `heel${s}`);
    j[`ball${s}`] = pt(`foot.${s}`, `ball${s}`);
    j[`palm${s}`] = palmWorld(rig, a.fr.bones, a.fr.hips, a.sc, s as 'L' | 'R');
  }
  const R = rig.restJoints;
  const arm = (len(sub(R.elbowL, R.shoulderL)) + len(sub(R.wristL, R.elbowL))) * a.sc;
  const leg = (len(sub(R.kneeL, R.hipL)) + len(sub(R.ankleL, R.kneeL))) * a.sc;
  return {j, arm, leg, debug: a.debug, headYaw: a.pose.headYaw, chestYaw: a.pose.chestYaw, source: (a as {source?: string}).source ?? motion};
};

// optional camera (visibility): the first shot of the props' episode
let camAt: ((t: number) => V3) | undefined;
if (args.includes('--props')) {
  const ep = JSON.parse(fs.readFileSync(opt('--props', ''), 'utf8')).episode;
  const sh = ep.shots[0];
  const pn = sh.panels?.[0];
  const keys = (pn?.camera ?? sh.camera).map((k: {at: number}) => ({...k, at: k.at}));
  const rm = resolveRemap(sh.remap, play, localResolver(() => 0, 0, play.duration) as never);
  camAt = (t: number) => camera3At(play, keys, t, remapAt(rm, t)).pos;
}

const out: Record<string, unknown> = {play: play.id, motion, hz: HZ, players: {}};
const rows: {t: number; id: string; kind: string; v: number; note?: string}[] = [];
const csv: string[] = ['player,t,owner,state,ball_xyz,anat_region,anat_depth_m,anat_class'];
resetV32Caches();
resetV33Caches();
for (const id of ids) {
  const fr: {t: number; J: J; arm: number; leg: number; dbg: ReturnType<typeof jointsOf>['debug']; hy: number; cy: number; src: string}[] = [];
  for (let f = 0; f <= N; f++) {
    const t = f / HZ;
    const q = jointsOf(id, t);
    fr.push({t, J: q.j, arm: q.arm, leg: q.leg, dbg: q.debug, hy: q.headYaw, cy: q.chestYaw, src: q.source});
  }
  // --dump ID:t0:t1 prints the wrist / head trace (diagnosis only, does not change any metric)
  const dumpArg = args.includes('--dump') ? args[args.indexOf('--dump') + 1].split(':') : null;
  if (dumpArg && dumpArg[0] === id) for (const r of fr) if (r.t >= +dumpArg[1] && r.t <= +dumpArg[2]) console.error(r.t.toFixed(3), 'wrL', r.J.wrL.map((v) => v.toFixed(3)).join(' '), 'wrR', r.J.wrR.map((v) => v.toFixed(3)).join(' '), 'head', r.J.head.map((v) => v.toFixed(3)).join(' '), 'pel', r.J.pelvis.map((v) => v.toFixed(3)).join(' '), JSON.stringify(r.dbg));
  // ---- foot slide / floor
  const slides: {side: string; t0: number; t1: number; slide: number}[] = [];
  let floorMin = 1, floorAt = 0;
  for (const s of ['L', 'R']) {
    let run: {t0: number; p0: V3; path: number; prev: V3} | null = null;
    for (const r of fr) {
      const p = r.J[`ball${s}`];
      const h = r.J[`heel${s}`];
      const lo = Math.min(p[2], h[2]);
      if (lo < floorMin) [floorMin, floorAt] = [lo, r.t];
      if (p[2] < 0.015) {
        if (!run) run = {t0: r.t, p0: p, path: 0, prev: p};
        else {
          run.path += Math.hypot(p[0] - run.prev[0], p[1] - run.prev[1]);
          run.prev = p;
        }
      } else if (run) {
        if (r.t - run.t0 >= 3 / HZ) slides.push({side: s, t0: r3(run.t0), t1: r3(r.t), slide: r3(run.path)});
        run = null;
      }
    }
    if (run) slides.push({side: s, t0: r3(run.t0), t1: r3(play.duration), slide: r3(run.path)});
  }
  for (const s of slides) if (s.slide > 0.02) rows.push({t: s.t0, id, kind: 'footSlide', v: s.slide, note: `${s.side} ${s.t0}-${s.t1}`});
  if (floorMin < -0.01) rows.push({t: floorAt, id, kind: 'floorPen', v: r3(floorMin)});
  // ---- joints
  let kneeMax = 0, kneeMin = 180, elbowMax = 0, neckMax = 0;
  for (const r of fr) {
    for (const s of ['L', 'R']) {
      const kf = 180 - ang(sub(r.J[`hip${s}`], r.J[`kn${s}`]), sub(r.J[`an${s}`], r.J[`kn${s}`]));
      const ef = 180 - ang(sub(r.J[`sh${s}`], r.J[`el${s}`]), sub(r.J[`wr${s}`], r.J[`el${s}`]));
      kneeMax = Math.max(kneeMax, kf);
      kneeMin = Math.min(kneeMin, kf);
      elbowMax = Math.max(elbowMax, ef);
      if (kf > 150 && r.t * HZ % 4 === 0) rows.push({t: r3(r.t), id, kind: 'kneeFlex', v: r3(kf)});
      if (ef > 155 && r.t * HZ % 4 === 0) rows.push({t: r3(r.t), id, kind: 'elbowFlex', v: r3(ef)});
    }
    const ny = Math.abs((((r.hy - r.cy) * 180) / Math.PI + 540) % 360 - 180);
    neckMax = Math.max(neckMax, ny);
  }
  // ---- pops (2nd difference at 120 Hz)
  const accMax: Record<string, {a: number; t: number}> = {};
  const landings = new Set<number>();
  for (const r of fr) if (r.dbg?.stage === 'landing') landings.add(Math.round(r.t * 10));
  for (const k of ['pelvis', 'head', 'wrL', 'wrR', 'anL', 'anR']) {
    accMax[k] = {a: 0, t: 0};
    for (let i = 1; i < fr.length - 1; i++) {
      const a = len(add(sub(fr[i + 1].J[k], mul(fr[i].J[k], 2)), fr[i - 1].J[k])) * HZ * HZ;
      if (a > accMax[k].a) accMax[k] = {a: r3(a), t: r3(fr[i].t)};
      const lim = k === 'pelvis' || k === 'head' ? 60 : k.startsWith('wr') ? 400 : 600;
      if (a > lim && !landings.has(Math.round(fr[i].t * 10)) && i % 4 === 0) rows.push({t: r3(fr[i].t), id, kind: `pop:${k}`, v: r3(a)});
    }
  }
  // ---- ball vs hands / body
  const gaps: number[] = [];
  let bodyHits = 0;
  let firstContact: number | null = null;
  for (const r of fr) {
    const b = ballAt(r.t);
    // held = in this player's hands: a dribble's floor phase is not a palm gap (the engine keeps `holder` through it)
    const held = sample(play, r.t).ball.holder === id && !sample(play, r.t).ball.inFlight && !dribbling(r.t);
    const pg = Math.min(len(sub(r.J.palmL, b)), len(sub(r.J.palmR, b))) - BALL_R;
    if (held) gaps.push(pg);
    if (firstContact === null && pg < 0.03 && r.dbg?.state && r.dbg.state !== 'FREE') firstContact = r3(r.t);
    if (held && pg > 0.05 && Math.round(r.t * HZ) % 4 === 0) rows.push({t: r3(r.t), id, kind: 'palmGap', v: r3(pg)});
    const caps: [V3, V3, number, string][] = [[r.J.pelvis, r.J.chest, 0.14, 'trunk'], [r.J.neck, add(r.J.head, [0, 0, 0.08]), 0.11, 'head'],
      [r.J.shL, r.J.elL, 0.05, 'upperarmL'], [r.J.shR, r.J.elR, 0.05, 'upperarmR'], [r.J.elL, add(r.J.elL, mul(sub(r.J.wrL, r.J.elL), 0.8)), 0.04, 'forearmL'], [r.J.elR, add(r.J.elR, mul(sub(r.J.wrR, r.J.elR), 0.8)), 0.04, 'forearmR'],
      [r.J.hipL, r.J.knL, 0.08, 'thighL'], [r.J.hipR, r.J.knR, 0.08, 'thighR']];
    for (const [a, c, rad, nm] of caps) {
      const d = segDist(b, a, c);
      if (d < rad + BALL_R - 0.01) {
        bodyHits++;
        if (Math.round(r.t * HZ) % 4 === 0) rows.push({t: r3(r.t), id, kind: 'ballBody', v: r3(rad + BALL_R - d), note: nm});
      }
    }
  }
  // ---- V3.3 anatomical ball-body detector (tapered, mesh-measured radii) + classification + per-frame CSV
  const anat = {contactAllowed: 0, minor: 0, visible: 0, maxDepth: 0, maxAt: 0, maxRegion: '', events: [] as {t0: number; t1: number; region: string; depthMax: number; cls: string; state: string}[]};
  let cur: {t0: number; t1: number; region: string; depthMax: number; cls: string; state: string} | null = null;
  for (const r of fr) {
    const b = ballAt(r.t);
    const st = r.dbg?.state ?? '';
    const hands = (r.dbg as {hands?: string[]} | undefined)?.hands ?? [];
    const own = sample(play, r.t).ball.holder === id || ['FIRST_CONTACT', 'CONTROLLED', 'SECURED', 'DRIBBLE', 'SHOOT_PREP', 'RELEASE'].includes(st);
    const hs = anatomicalHits(r.J, b);
    let worst: {region: string; depth: number; cls: string} | null = null;
    for (const h of hs) {
      // contact of the holding hand's distal forearm with its own ball = a grip, not a penetration (<= 1.5 cm)
      const side = h.region.endsWith('L') ? 'L' : h.region.endsWith('R') ? 'R' : '';
      const cls = own && h.region.startsWith('forearm') && hands.includes(side) && h.depth <= 0.015 ? 'contactAllowed' : h.depth > 0.01 ? 'visible' : 'minor';
      if (!worst || h.depth > worst.depth) worst = {...h, cls};
    }
    if (worst) {
      (anat as Record<string, number>)[worst.cls]++;
      if (worst.depth > anat.maxDepth) [anat.maxDepth, anat.maxAt, anat.maxRegion] = [r3(worst.depth), r3(r.t), worst.region];
      if (cur && cur.region === worst.region && r.t - cur.t1 < 1.5 / HZ) {
        cur.t1 = r3(r.t);
        cur.depthMax = Math.max(cur.depthMax, r3(worst.depth));
        if (worst.cls === 'visible') cur.cls = 'visible';
      } else {
        if (cur) anat.events.push(cur);
        cur = {t0: r3(r.t), t1: r3(r.t), region: worst.region, depthMax: r3(worst.depth), cls: worst.cls, state: st};
      }
    }
    csv.push([id, r3(r.t), motion === 'v33' ? ballOwner33(play, r.t) ?? '' : sample(play, r.t).ball.holder ?? '', st, b.map(r3).join(' '), worst ? worst.region : '', worst ? r3(worst.depth) : '', worst ? worst.cls : ''].join(','));
  }
  if (cur) anat.events.push(cur);
  // ---- limbs
  let armRatio = 0, legRatio = 0;
  for (const r of fr) {
    for (const s of ['L', 'R']) {
      armRatio = Math.max(armRatio, len(sub(r.J[`wr${s}`], r.J[`sh${s}`])) / r.arm);
      legRatio = Math.max(legRatio, len(sub(r.J[`an${s}`], r.J[`hip${s}`])) / r.leg);
    }
  }
  // ---- visibility
  let occluded = 0;
  if (camAt) {
    for (let i = 0; i < fr.length; i += 4) {
      const r = fr[i];
      const cp = camAt(r.t);
      const others = play.players.filter((p) => p.id !== id).map((p) => {
        const q = posAt(play.tracks[p.id], r.t);
        return [[q[0], q[1], 0.2], [q[0], q[1], 1.9]] as [V3, V3];
      });
      const pts: [string, V3][] = [['head', r.J.head], ['handL', r.J.wrL], ['handR', r.J.wrR], ['footL', r.J.anL], ['footR', r.J.anR], ['ball', ballAt(r.t)]];
      for (const [nm, p] of pts) {
        for (const [a, c] of others) {
          // closest approach between the ray cam -> p and the capsule axis (sampled)
          let dmin = 1e9;
          for (let k = 1; k < 40; k++) {
            const x = add(cp, mul(sub(p, cp), k / 40));
            dmin = Math.min(dmin, segDist(x, a, c));
          }
          if (dmin < 0.28) {
            occluded++;
            rows.push({t: r3(r.t), id, kind: 'occluded', v: r3(dmin), note: nm});
            break;
          }
        }
      }
    }
  }
  const q = (xs: number[], p: number) => {
    const s = [...xs].sort((a, b) => a - b);
    return s.length ? r3(s[Math.min(s.length - 1, Math.floor(p * (s.length - 1)))]) : null;
  };
  (out.players as Record<string, unknown>)[id] = {
    footContacts: slides.length, footSlideMax: r3(Math.max(0, ...slides.map((s) => s.slide))), footSlideOver2cm: slides.filter((s) => s.slide > 0.02).length,
    floorMin: r3(floorMin), floorMinAt: r3(floorAt),
    kneeFlexMax: r3(kneeMax), kneeFlexMin: r3(kneeMin), elbowFlexMax: r3(elbowMax), neckYawMax: r3(neckMax),
    accMax, palmGap: {median: q(gaps, 0.5), p95: q(gaps, 0.95), max: q(gaps, 1), n: gaps.length}, firstContact,
    ballBodyFrames120: bodyHits, anatomical: anat, source: [...new Set(fr.map((r) => r.src))].join('+'), armReachMax: r3(armRatio), legReachMax: r3(legRatio), occludedSamples30: occluded,
  };
}
out.defects = rows.length;
fs.writeFileSync(opt('--json', '/dev/stdout'), JSON.stringify(out, null, 1));
if (args.includes('--frames')) fs.writeFileSync(opt('--frames', ''), JSON.stringify(rows));
if (args.includes('--csv')) fs.writeFileSync(opt('--csv', ''), csv.join('\n'));
out.anatomicalRadii = ANAT33;
console.error(`qc-realism-v33 ${play.id} motion ${motion}: ${rows.length} defect rows`);
