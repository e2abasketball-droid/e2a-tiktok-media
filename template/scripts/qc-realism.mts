// REALISM V2 QA gates (2026-11-21, owner brief E2A_REALISM_V2_PROMPT_CLAUDE_CODE.md sec. 9). Measured on what is DRAWN:
// the deformable mesh skeleton driven exactly as Scene3D drives it (poseAt -> bonesFromPose -> forward kinematics) and,
// for the clothes, the GLB vertices skinned on the CPU (linear blend skinning, same bones) plus the cloth2 secondary
// motion of v2 meshes. Any play; legacy plays are measured with their own (v1) meshes.
//   npx tsx scripts/qc-realism.mts tactical/plays/<id>.json [--legacy] [--range t0:t1] [--json out.json] [--no-cloth]
//     --legacy   drop play.realism (the A/B baseline: same play, engine without the Realism V2 module, v1 meshes)
// Gates (thresholds are CALIBRATION STARTING POINTS from the brief, not universal truths; every value is reported):
//   foot_plant      planted sole (mesh heel + ball of the foot) horizontal drift over each plant window: WARN > 2 cm,
//                   FAIL > 5 cm; planted sole below the floor (< -1 cm) or floating (> 4 cm) counted; pivots (yaw > 20°)
//                   reported apart (allowed)
//   contact_pose    palm centre (mesh) to the ball SURFACE while the player holds the ball (not dribbling) or shares it
//                   in a hand-off: FAIL if a palm is buried > 2 cm, or BOTH palms > 5 cm off the ball
//   swept_ball      the ball sphere swept at 8 sub-steps per frame against mesh capsules of every player (trunk, head,
//                   upper arms, forearms, thighs): FAIL > 2 cm in a trunk/head/upper arm, > 3 cm in a forearm/thigh
//                   (the holder's own forearms and both players' forearms in a hand-off are contact, not collision)
//   ball_continuity 240 Hz: position step > 6 cm or |dv| > 4 m/s outside declared impacts (floor bounce, release,
//                   catch/hand-off contact +-0.05 s, rim/net) = FAIL
//   ik_reach        engine arms/legs: target beyond reach (saturated > 0.995 of the chain) frames, elbow pole flips
//                   (> 90° in one frame), knees bent backward (> 2 cm behind the hip-ankle line)
//   root_foot       heading rate > 900°/s FAIL, > 720°/s WARN (instant turns), root moving > 0.6 m/s with BOTH feet planted for > 0.25 s (glide)
//   blocking        each `screen` action: screener speed <= 0.2 m/s from 0.15 s after the screen starts, both feet
//                   planted at the closest approach of the defender he faces; trunk capsules never overlap > 2 cm
//   cloth_clip      (C meshes) skin poking OUT of the jersey/shorts by > 1 cm for > 3 frames (bind pairs body-under-
//                   cloth), arms INSIDE the jersey shell by > 1 cm for > 3 frames, shorts poking through the jersey
//   cloth_stability jersey edge stretch vs bind (> 1.30 = FAIL), per-vertex acceleration (> 12 m/s² at the hem =
//                   vibration WARN), number region (front/back) stretch > 1.15 WARN
//   court           ball radius / rim / basket constants, mesh soles inside the court (+-10 cm), make passes the
//                   ring (centre within 0.10 m at the rim plane)
import fs from 'node:fs';
import '../src/t3d/rig.ts';
import '../src/t3d/players/index.ts';
import {FIBA} from '../src/tactical/geometry.ts';
import type {V3} from '../src/tactical/geometry.ts';
import {posAt, realismV2, sample} from '../src/tactical/play.ts';
import {BALL_R, bodyRowAt, poseAt} from '../src/t3d/rig.ts';
import type {PlayWithActions, Pose} from '../src/t3d/rig.ts';
import {bonesFromPose, meshScale, qconj, qrot} from '../src/t3d/skelclip.ts';
import type {ClipBone, Q} from '../src/t3d/skelclip.ts';
import {PLAYER3D, planPlayers3d} from '../src/t3d/player3d.ts';
import {clothAt, clothDisplace} from '../src/t3d/cloth2.ts';

const args = process.argv.slice(2);
const opt = (k: string) => (args.includes(k) ? args[args.indexOf(k) + 1] : undefined);
const legacy = args.includes('--legacy');
const noCloth = args.includes('--no-cloth');
const jsonOut = opt('--json');
const range = opt('--range')?.split(':').map(Number);
const files = args.filter((a, i) => a.endsWith('.json') && args[i - 1] !== '--json');
const FPS = 30;
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a: V3, k: number): V3 => [a[0] * k, a[1] * k, a[2] * k];
const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const dist = (a: V3, b: V3) => len(sub(a, b));
const segDist = (p: V3, a: V3, b: V3) => {
  const ab = sub(b, a);
  const u = Math.max(0, Math.min(1, dot(sub(p, a), ab) / Math.max(1e-9, dot(ab, ab))));
  return dist(p, add(a, mul(ab, u)));
};

// ---------------------------------------------------------------- GLB (node: fs + manual parse)
type Mesh = {P: Float32Array; N: Float32Array; J: Uint16Array | Uint8Array; W: Float32Array; n: number; idx: Uint32Array; hem?: Float32Array; ease?: Float32Array; uv?: Float32Array};
const glbCache = new Map<string, Record<string, Mesh>>();
const loadGlb = (file: string) => {
  const hit = glbCache.get(file);
  if (hit) return hit;
  const b = fs.readFileSync(file);
  const jl = b.readUInt32LE(12);
  const J = JSON.parse(b.subarray(20, 20 + jl).toString());
  const bin0 = 20 + jl + 8;
  const acc = (i: number) => {
    const a = J.accessors[i], bv = J.bufferViews[a.bufferView];
    const n = ({SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4} as Record<string, number>)[a.type];
    const off = bin0 + (bv.byteOffset ?? 0) + (a.byteOffset ?? 0);
    const buf = b.buffer.slice(b.byteOffset + off, b.byteOffset + off + a.count * n * ({5126: 4, 5123: 2, 5121: 1, 5125: 4} as Record<number, number>)[a.componentType]);
    return a.componentType === 5126 ? new Float32Array(buf) : a.componentType === 5123 ? new Uint16Array(buf) : a.componentType === 5121 ? new Uint8Array(buf) : new Uint32Array(buf);
  };
  const out: Record<string, Mesh> = {};
  for (const m of J.meshes) {
    const prims = m.primitives;
    // merge primitives (body: skin + sock)
    const parts = prims.map((p: {attributes: Record<string, number>; indices: number}) => ({
      P: acc(p.attributes.POSITION) as Float32Array, N: acc(p.attributes.NORMAL) as Float32Array, J: acc(p.attributes.JOINTS_0) as Uint16Array,
      W: acc(p.attributes.WEIGHTS_0) as Float32Array, I: acc(p.indices) as Uint32Array,
      H: p.attributes._E2A_HEM !== undefined ? (acc(p.attributes._E2A_HEM) as Float32Array) : undefined,
      E: p.attributes._E2A_EASE !== undefined ? (acc(p.attributes._E2A_EASE) as Float32Array) : undefined,
      U: p.attributes.TEXCOORD_0 !== undefined ? (acc(p.attributes.TEXCOORD_0) as Float32Array) : undefined,
    }));
    const n = parts.reduce((s: number, p: {P: Float32Array}) => s + p.P.length / 3, 0);
    const P = new Float32Array(n * 3), N = new Float32Array(n * 3), Jx = new Uint16Array(n * 4), W = new Float32Array(n * 4);
    const hem = parts[0].H ? new Float32Array(n) : undefined, ease = parts[0].E ? new Float32Array(n) : undefined, uv = parts[0].U ? new Float32Array(n * 2) : undefined;
    const idx: number[] = [];
    let o = 0;
    for (const p of parts) {
      const k = p.P.length / 3;
      for (let i = 0; i < k; i++) {
        // three (x, y up, z) -> play (x, -z, y)
        P[(o + i) * 3] = p.P[i * 3]; P[(o + i) * 3 + 1] = -p.P[i * 3 + 2]; P[(o + i) * 3 + 2] = p.P[i * 3 + 1];
        N[(o + i) * 3] = p.N[i * 3]; N[(o + i) * 3 + 1] = -p.N[i * 3 + 2]; N[(o + i) * 3 + 2] = p.N[i * 3 + 1];
        for (let c = 0; c < 4; c++) {
          Jx[(o + i) * 4 + c] = p.J[i * 4 + c];
          W[(o + i) * 4 + c] = p.W[i * 4 + c];
        }
        if (hem && p.H) hem[o + i] = p.H[i];
        if (ease && p.E) ease[o + i] = p.E[i];
        if (uv && p.U) { uv[(o + i) * 2] = p.U[i * 2]; uv[(o + i) * 2 + 1] = p.U[i * 2 + 1]; }
      }
      for (const v of p.I) idx.push(v + o);
      o += k;
    }
    out[m.name] = {P, N, J: Jx, W, n, idx: new Uint32Array(idx), hem, ease, uv};
  }
  // joint order of the skin = node names
  (out as unknown as {__joints: string[]}).__joints = J.skins[0].joints.map((i: number) => J.nodes[i].name);
  glbCache.set(file, out);
  return out;
};

// forward kinematics of the mesh skeleton (same as player3dqc)
const fk = (bones: ClipBone[], rot: Record<string, Q>, hips: V3, s: number) => {
  const P: Record<string, V3> = {[bones[0].name]: hips};
  const by = Object.fromEntries(bones.map((b) => [b.name, b]));
  for (const b of bones) {
    if (!b.parent) continue;
    const p = by[b.parent];
    const local = qrot(qconj(p.R), sub(b.head, p.head));
    P[b.name] = add(P[b.parent], qrot(rot[b.parent], mul(local, s)));
  }
  return P;
};
const qmul = (a: Q, b: Q): Q => [
  a[3] * b[0] + a[0] * b[3] + a[1] * b[2] - a[2] * b[1],
  a[3] * b[1] - a[0] * b[2] + a[1] * b[3] + a[2] * b[0],
  a[3] * b[2] + a[0] * b[1] - a[1] * b[0] + a[2] * b[3],
  a[3] * b[3] - a[0] * b[0] - a[1] * b[1] - a[2] * b[2],
];
/** world point of a rest joint carried by a bone (heel, ball of the foot, palm) */
const carried = (desc: ClipBone[], rot: Record<string, Q>, J: Record<string, V3>, bone: string, rest: V3, s: number) => {
  const b = desc.find((x) => x.name === bone)!;
  return add(J[bone], qrot(rot[bone], mul(qrot(qconj(b.R), sub(rest, b.head)), s)));
};

type Gate = {gate: string; status: 'PASS' | 'WARN' | 'FAIL'; value: string; detail?: unknown};

const runPlay = (file: string): {id: string; gates: Gate[]; stats: Record<string, unknown>} => {
  const play0 = JSON.parse(fs.readFileSync(file, 'utf8')) as PlayWithActions & {realism?: number};
  if (legacy) {
    delete play0.realism;
    play0.id += '-legacy';
  }
  const play = play0;
  const rv2 = realismV2(play);
  const plan = planPlayers3d(play, {});
  const t0 = range ? range[0] : 0, t1 = range ? range[1] : play.duration;
  const f0 = Math.ceil(t0 * FPS), f1 = Math.floor(t1 * FPS);
  const ids = play.players.map((p) => p.id);
  const gates: Gate[] = [];
  const meshOf = (id: string) => {
    const v = play.players.find((p) => p.id === id)!.team === 'X' ? 'def' : 'off';
    const pkg = PLAYER3D[v];
    return {rig: pkg.rig!, glb: loadGlb(`public/${rv2 ? pkg.glbV2 : pkg.glb}`)};
  };
  // per frame, per player: engine pose + mesh joints (cached by time key)
  type St = {pose: Pose; rot: Record<string, Q>; hips: V3; s: number; J: Record<string, V3>; desc: ClipBone[]};
  const cache = new Map<string, St>();
  const stateAt = (id: string, t: number): St => {
    const k = `${id}|${t.toFixed(5)}`;
    const hit = cache.get(k);
    if (hit) return hit;
    const b = sample(play, t).ball;
    const lag = sample(play, Math.max(0, t - 0.2)).ball.pos;
    const pose = poseAt(play, id, t, {holder: b.holder, pos: b.pos, lag}, RIM);
    const {rig} = meshOf(id);
    const s = meshScale(rig, pose);
    const r = bonesFromPose(rig, pose, s);
    const st = {pose, rot: r.bones, hips: r.hips, s, J: fk(rig.bones, r.bones, r.hips, s), desc: rig.bones};
    if (cache.size > 60000) cache.clear();
    cache.set(k, st);
    return st;
  };
  const restJ = (id: string) => meshOf(id).rig.restJoints;
  const soles = (id: string, st: St, i: number) => {
    const sd = i ? 'R' : 'L';
    const R = restJ(id);
    // the ball of the foot rides on the TOE bone (it is the toe joint's pivot), the heel on the foot bone
    const toe = st.J[`toe.${sd}`];
    const toeRest = meshOf(id).rig.bones.find((b) => b.name === `toe.${sd}`)?.head;
    const ball = toe && toeRest ? [toe[0], toe[1], toe[2] - (toeRest[2] - R[`ball${sd}`][2]) * st.s] as V3 : carried(st.desc, st.rot, st.J, `foot.${sd}`, R[`ball${sd}`], st.s);
    return {heel: carried(st.desc, st.rot, st.J, `foot.${sd}`, R[`heel${sd}`], st.s), ball};
  };
  const palm = (id: string, st: St, i: number) => {
    const sd = i ? 'R' : 'L';
    const R = restJ(id);
    const mid = mul(add(R[`wrist${sd}`], R[`hand${sd}`]), 0.5);
    return carried(st.desc, st.rot, st.J, `hand.${sd}`, mid, st.s);
  };

  // ---------------------------------------------------------------- 1. foot plant drift (mesh soles)
  {
    const res: {id: string; foot: string; from: number; to: number; drift: number; yaw: number; zmin: number; zmax: number}[] = [];
    for (const id of ids) {
      if (plan[id].look !== 'C') continue;
      for (let i = 0; i < 2; i++) {
        let win: {from: number; p0: V3; yaw0: number; drift: number; yaw: number; zmin: number; zmax: number} | undefined;
        const close = (t: number) => {
          if (win && t - win.from >= 3 / FPS) res.push({id, foot: i ? 'R' : 'L', from: win.from, to: t, drift: win.drift, yaw: win.yaw, zmin: win.zmin, zmax: win.zmax});
          win = undefined;
        };
        for (let f = f0; f <= f1; f++) {
          const t = f / FPS;
          const planted = bodyRowAt(play, id, t).lift[i] === 0 && poseAt.length >= 0;
          const st = stateAt(id, t);
          const so = soles(id, st, i);
          const mid: V3 = mul(add(so.heel, so.ball), 0.5);
          const yaw = Math.atan2(so.ball[1] - so.heel[1], so.ball[0] - so.heel[0]);
          const zlow = Math.min(so.heel[2], so.ball[2]);
          if (planted) {
            if (!win) win = {from: t, p0: mid, yaw0: yaw, drift: 0, yaw: 0, zmin: zlow, zmax: zlow};
            win.drift = Math.max(win.drift, Math.hypot(mid[0] - win.p0[0], mid[1] - win.p0[1]));
            win.yaw = Math.max(win.yaw, Math.abs(Math.atan2(Math.sin(yaw - win.yaw0), Math.cos(yaw - win.yaw0))) * 180 / Math.PI);
            win.zmin = Math.min(win.zmin, zlow);
            win.zmax = Math.max(win.zmax, zlow);
          } else close(t);
        }
        close(f1 / FPS);
      }
    }
    const nonPivot = res.filter((r) => r.yaw <= 20);
    const worst = nonPivot.reduce((a, r) => (r.drift > a.drift ? r : a), {drift: 0} as (typeof res)[number]);
    const warn = nonPivot.filter((r) => r.drift > 0.02).length, fail = nonPivot.filter((r) => r.drift > 0.05).length;
    // sole height reference: the lowest planted sole of the play (the mesh sole sits a few mm above the floor)
    const zRef = Math.min(...res.map((r) => r.zmin));
    const zs = res.map((r) => r.zmin).sort((a, b) => a - b), zMed = zs[Math.floor(zs.length / 2)] ?? 0;
    const sink = res.filter((r) => r.zmin < zMed - 0.02).length, float = res.filter((r) => r.zmin - Math.max(0, zRef) > 0.04).length;
    gates.push({gate: 'foot_plant', status: fail ? 'FAIL' : warn ? 'WARN' : 'PASS',
      value: `${res.length} plants, worst drift ${(worst.drift * 100).toFixed(1)} cm (${worst.id ?? '-'} ${worst.foot ?? ''} @${worst.from?.toFixed(2) ?? '-'}s), >2 cm: ${warn}, >5 cm: ${fail}; pivots (yaw > 20°): ${res.length - nonPivot.length}; planted sole z min ${(zRef * 100).toFixed(1)} cm / median ${(zMed * 100).toFixed(1)} cm, plants dipping > 2 cm under the median: ${sink}, floating > 4 cm: ${float}`,
      detail: {plants: res.length, warn, fail, worst}});
  }

  // ---------------------------------------------------------------- ball sampling helpers
  const ballAt = (t: number) => sample(play, t).ball;
  const handoffs = play.ball.filter((e) => e.type === 'pass' && e.style === 'handoff') as {from: string; to: string; t0: number; t1: number}[];
  const inHandoff = (t: number) => handoffs.find((h) => t >= h.t0 - 0.3 && t <= h.t1 + 0.05);

  // ---------------------------------------------------------------- 2. contact pose (mesh palms vs ball surface)
  {
    let buried = {v: 0, at: ''}, off = {v: 0, at: ''};
    let frames = 0;
    for (let f = f0; f <= f1; f++) {
      const t = f / FPS;
      const b = ballAt(t);
      const ho = handoffs.find((h) => t >= h.t0 && t <= h.t1);
      const who: string[] = [];
      const holdEv = play.ball.find((e) => e.type === 'hold' && t >= e.from && t <= e.to) as {player: string; dribble?: boolean; from: number} | undefined;
      if (holdEv && !holdEv.dribble && b.holder) {
        // gather/shot arms ride the ball until the release; a fresh catch gets 0.1 s to close the hands
        const fromPass = play.ball.some((e) => e.type === 'pass' && e.to === holdEv.player && Math.abs(e.t1 - holdEv.from) < 1e-6 && e.style !== 'handoff');
        if (!fromPass || t - holdEv.from > 0.1) who.push(b.holder);
      }
      if (ho) who.push(ho.from, ho.to);
      for (const id of new Set(who)) {
        if (plan[id].look !== 'C') continue;
        const st = stateAt(id, t);
        const g = [0, 1].map((i) => dist(palm(id, st, i), b.pos) - BALL_R);
        frames++;
        const mn = Math.min(...g), mx = Math.min(...g.map((x) => Math.max(0, x)));
        if (-mn > buried.v) buried = {v: -mn, at: `${id}@${t.toFixed(2)}`};
        if (mx > off.v) off = {v: mx, at: `${id}@${t.toFixed(2)}`};
      }
    }
    const st = buried.v > 0.02 || off.v > 0.05 ? 'FAIL' : buried.v > 0.01 || off.v > 0.03 ? 'WARN' : 'PASS';
    gates.push({gate: 'contact_pose', status: st, value: `${frames} grip frames; deepest palm in the ball ${(buried.v * 100).toFixed(1)} cm (${buried.at || '-'}), nearest palm farthest off ${(off.v * 100).toFixed(1)} cm (${off.at || '-'})`, detail: {buried, off}});
  }

  // ---------------------------------------------------------------- 3. swept ball vs mesh capsules
  {
    type Cap = {name: string; a: V3; b: V3; r: number; lim: number};
    const caps = (id: string, st: St): Cap[] => {
      const J = st.J, k = st.pose.dims.H / 2;
      const c: Cap[] = [
        {name: 'trunk', a: J['hips'], b: J['neck'], r: 0.125 * k, lim: 0.02},
        {name: 'head', a: J['head'], b: add(J['head'], [0, 0, 0.16 * k]), r: 0.1 * k, lim: 0.02},
      ];
      for (const sd of ['L', 'R']) {
        c.push({name: `upperarm.${sd}`, a: J[`upperarm.${sd}`], b: J[`forearm.${sd}`], r: 0.045 * k, lim: 0.02});
        c.push({name: `forearm.${sd}`, a: J[`forearm.${sd}`], b: J[`hand.${sd}`], r: 0.035 * k, lim: 0.03});
        c.push({name: `thigh.${sd}`, a: J[`thigh.${sd}`], b: J[`shin.${sd}`], r: 0.07 * k, lim: 0.03});
      }
      return c;
    };
    let worst = {pen: 0, at: '', part: '', lim: 0.02};
    const fails: string[] = [];
    const SUB = 8;
    for (let f = f0; f < f1; f++) {
      for (let k = 0; k < SUB; k++) {
        const t = (f + k / SUB) / FPS;
        const b = ballAt(t);
        if (b.pos[2] > 3.2) continue;
        const ho = inHandoff(t);
        for (const id of ids) {
          const pp = posAt(play.tracks[id], t);
          if (Math.hypot(pp[0] - b.pos[0], pp[1] - b.pos[1]) > 1.4) continue;
          const st = stateAt(id, t);
          for (const c of caps(id, st)) {
            const contact = c.name.startsWith('forearm') && (b.holder === id || (ho && (ho.from === id || ho.to === id)) ||
              play.ball.some((e) => e.type === 'pass' && e.to === id && t >= e.t1 - 0.12 && t <= e.t1 + 0.1));
            if (contact) continue;
            const pen = c.r + BALL_R - segDist(b.pos, c.a, c.b);
            if (pen > c.lim && fails.length < 12) fails.push(`${id}.${c.name}@${t.toFixed(3)} ${(pen * 100).toFixed(1)} cm`);
            if (pen - c.lim > worst.pen - worst.lim) worst = {pen, at: `${id}@${t.toFixed(3)}`, part: c.name, lim: c.lim};
          }
        }
      }
    }
    gates.push({gate: 'swept_ball', status: fails.length ? 'FAIL' : 'PASS', value: `worst ${(worst.pen * 100).toFixed(1)} cm into ${worst.part || '-'} (${worst.at || '-'}, limit ${(worst.lim * 100).toFixed(0)} cm); ${fails.length} sub-steps over the limit`, detail: {fails}});
  }

  // ---------------------------------------------------------------- 4. ball event continuity (240 Hz)
  {
    const dt = 1 / 240;
    const impacts: number[] = [];
    for (const e of play.ball) {
      if (e.type === 'pass') impacts.push(e.t0, e.t1);
      if (e.type === 'shot' || e.type === 'layup') impacts.push(e.t0, e.t1);
      if (e.type === 'hold') impacts.push(e.from);
    }
    let prev: V3 | undefined, pv: V3 | undefined;
    const bad: string[] = [];
    let maxStep = 0, maxDv = 0;
    for (let t = t0; t <= t1; t += dt) {
      const b = ballAt(t);
      const p = b.pos as V3;
      const nearImpact = impacts.some((x) => Math.abs(t - x) < 0.05) || p[2] < 0.25 || (Math.abs(p[0] - RIM[0]) < 0.6 && Math.abs(p[1] - RIM[1]) < 0.6 && p[2] > 2.6 && p[2] < 3.4);
      if (prev) {
        const step = dist(p, prev);
        const v = mul(sub(p, prev), 1 / dt);
        if (pv && !nearImpact) {
          const dv = dist(v, pv);
          maxDv = Math.max(maxDv, dv);
          if (dv > 4 && bad.length < 10) bad.push(`|dv| ${dv.toFixed(1)} m/s @${t.toFixed(3)}`);
        }
        if (!nearImpact) maxStep = Math.max(maxStep, step);
        if (step > 0.06 && bad.length < 10) bad.push(`step ${(step * 100).toFixed(1)} cm @${t.toFixed(3)}`);
        pv = v;
      }
      prev = p;
    }
    gates.push({gate: 'ball_continuity', status: bad.length ? 'FAIL' : 'PASS', value: `max step ${(maxStep * 100).toFixed(2)} cm / (1/240 s), max |dv| ${maxDv.toFixed(2)} m/s outside impacts; ${bad.length} violations`, detail: {bad}});
  }

  // ---------------------------------------------------------------- 5. IK reachability, elbow flips, knees
  {
    let sat = 0, flips = 0, knees = 0, frames = 0;
    const flipAt: string[] = [];
    const prevE: Record<string, V3[]> = {};
    for (let f = f0; f <= f1; f++) {
      const t = f / FPS;
      for (const id of ids) {
        const st = stateAt(id, t);
        const P = st.pose, D = P.dims;
        frames++;
        const sh = [P.shoulder?.[0], P.shoulder?.[1]] as (V3 | undefined)[];
        const eDirs: V3[] = [];
        for (let i = 0; i < 2; i++) {
          const s = sh[i] ?? st.J[i ? 'upperarm.R' : 'upperarm.L'];
          const reach = dist(s, P.wrist[i]) / (D.upper + D.fore);
          if (reach > 0.995) sat++;
          const ax = sub(P.wrist[i], s);
          const al = dot(ax, ax);
          const proj = add(s, mul(ax, Math.max(0, Math.min(1, dot(sub(P.elbow[i], s), ax) / Math.max(1e-9, al)))));
          eDirs.push(sub(P.elbow[i], proj));
        }
        const pe = prevE[id];
        if (pe) for (let i = 0; i < 2; i++) {
          const a = eDirs[i], b = pe[i];
          if (len(a) > 0.03 && len(b) > 0.03 && dot(a, b) / (len(a) * len(b)) < 0) {
            flips++;
            if (flipAt.length < 8) flipAt.push(`${id}.${i ? 'R' : 'L'}@${t.toFixed(2)}`);
          }
        }
        prevE[id] = eDirs;
        // knees: forward of the hip-ankle line (in the heading frame)
        const row = bodyRowAt(play, id, t);
        const F: V3 = [Math.cos(row.heading), Math.sin(row.heading), 0];
        for (let i = 0; i < 2; i++) {
          const hip = P.hip?.[i] ?? st.J[i ? 'thigh.R' : 'thigh.L'];
          const ax = sub(P.ankle[i], hip);
          const proj = add(hip, mul(ax, Math.max(0, Math.min(1, dot(sub(P.knee[i], hip), ax) / Math.max(1e-9, dot(ax, ax))))));
          if (dot(sub(P.knee[i], proj), F) < -0.02) knees++;
        }
      }
    }
    gates.push({gate: 'ik_reach', status: flips || knees ? 'FAIL' : sat / Math.max(1, frames * 2) > 0.05 ? 'WARN' : 'PASS',
      value: `arm chain saturated in ${(100 * sat / Math.max(1, frames * 2)).toFixed(1)} % of hand-frames; elbow pole flips ${flips}${flipAt.length ? ` (${flipAt.join(', ')})` : ''}; knees bent backward ${knees}`});
  }

  // ---------------------------------------------------------------- 6. root / foot concordance
  {
    let maxTurn = {v: 0, at: ''}, skate = 0, skateAt = '';
    const dsRun: Record<string, number> = {};
    for (let f = f0; f <= f1; f++) {
      const t = f / FPS;
      for (const id of ids) {
        const a = bodyRowAt(play, id, t), b = bodyRowAt(play, id, t + 1 / 120);
        const tr = Math.abs(Math.atan2(Math.sin(b.heading - a.heading), Math.cos(b.heading - a.heading))) * 120 * 180 / Math.PI;
        if (tr > maxTurn.v) maxTurn = {v: tr, at: `${id}@${t.toFixed(2)}`};
        // double support while walking is normal (~0.1-0.15 s); > 0.25 s on two planted feet while the root moves
        // > 0.6 m/s is a glide
        dsRun[id] = a.lift[0] === 0 && a.lift[1] === 0 && a.speed > 0.6 ? (dsRun[id] ?? 0) + 1 : 0;
        if (dsRun[id] > 0.25 * FPS) { skate++; skateAt ||= `${id}@${t.toFixed(2)}`; }
      }
    }
    gates.push({gate: 'root_foot', status: maxTurn.v > 900 || skate > 3 ? 'FAIL' : maxTurn.v > 720 ? 'WARN' : 'PASS', value: `max heading rate ${maxTurn.v.toFixed(0)}°/s (${maxTurn.at}); frames gliding (> 0.6 m/s on two planted feet for > 0.25 s): ${skate}${skateAt ? ` (first ${skateAt})` : ''}`});
  }

  // ---------------------------------------------------------------- 7. blocking plausibility
  {
    const out: string[] = [];
    let ok = true;
    for (const id of ids) {
      for (const a of (play.actions?.[id] ?? []).filter((x) => x.type === 'screen')) {
        if (a.to < t0 || a.from > t1) continue;
        let vmax = 0;
        for (let t = a.from + 0.15; t <= a.to; t += 1 / 60) {
          const p = posAt(play.tracks[id], t), q = posAt(play.tracks[id], t + 1 / 60);
          vmax = Math.max(vmax, Math.hypot(q[0] - p[0], q[1] - p[1]) * 60);
        }
        // the defender the screen is set on: the `face` player, or (a set angle) the nearest opponent during the screen (not his own defender)
        let tgt = typeof a.face === 'string' && play.tracks[a.face] ? a.face : undefined;
        if (!tgt) {
          const team = play.players.find((p) => p.id === id)!.team;
          let best = 99;
          for (const o of play.players.filter((p) => p.team !== team && (p as {guards?: string}).guards !== id)) for (let t = a.from; t <= a.to; t += 1 / 30) {
            const d = Math.hypot(...(posAt(play.tracks[id], t).map((v, k) => v - posAt(play.tracks[o.id], t)[k]) as [number, number]));
            if (d < best) { best = d; tgt = o.id; }
          }
        }
        let close = {d: 99, t: a.from};
        if (tgt) for (let t = a.from; t <= a.to; t += 1 / 60) {
          const d = Math.hypot(...(posAt(play.tracks[id], t).map((v, k) => v - posAt(play.tracks[tgt], t)[k]) as [number, number]));
          if (d < close.d) close = {d, t};
        }
        const row = bodyRowAt(play, id, close.t);
        const both = row.lift[0] === 0 && row.lift[1] === 0;
        let overlap = 0;
        if (tgt) for (let t = a.from; t <= a.to; t += 1 / 30) {
          const A = stateAt(id, t), B = stateAt(tgt, t);
          const dd = Math.hypot(A.J.hips[0] - B.J.hips[0], A.J.hips[1] - B.J.hips[1]) - 0.125 * (A.pose.dims.H / 2) - 0.125 * (B.pose.dims.H / 2);
          overlap = Math.max(overlap, -dd);
        }
        const good = vmax <= 0.2 && both && overlap <= 0.02;
        ok = ok && good;
        out.push(`${id} screen ${a.from.toFixed(2)}-${a.to.toFixed(2)}s on ${tgt ?? '?'}: max speed ${vmax.toFixed(2)} m/s, closest ${close.d.toFixed(2)} m @${close.t.toFixed(2)}s, both feet planted there: ${both ? 'yes' : 'NO'}, trunk overlap ${(overlap * 100).toFixed(1)} cm`);
      }
    }
    gates.push({gate: 'blocking', status: out.length === 0 ? 'PASS' : ok ? 'PASS' : 'FAIL', value: out.length ? out.join(' | ') : 'no screen in range'});
  }

  // ---------------------------------------------------------------- 8/9. cloth clipping + stability (CPU skinning)
  const stats: Record<string, unknown> = {};
  if (!noCloth) {
    const skin = (m: Mesh, joints: string[], st: St, rest: Record<string, ClipBone>) => {
      const out = new Float32Array(m.n * 3), nrm = new Float32Array(m.n * 3);
      const dq: Record<string, Q> = {};
      for (const nm of joints) dq[nm] = qmul(st.rot[nm], qconj(rest[nm].R));
      for (let v = 0; v < m.n; v++) {
        const p: V3 = [m.P[v * 3], m.P[v * 3 + 1], m.P[v * 3 + 2]];
        const n: V3 = [m.N[v * 3], m.N[v * 3 + 1], m.N[v * 3 + 2]];
        let x = 0, y = 0, z = 0, nx = 0, ny = 0, nz = 0;
        for (let c = 0; c < 4; c++) {
          const w = m.W[v * 4 + c];
          if (w <= 0) continue;
          const nm = joints[m.J[v * 4 + c]];
          const q = dq[nm];
          const r = qrot(q, mul(sub(p, rest[nm].head), st.s));
          const h = st.J[nm];
          x += w * (h[0] + r[0]); y += w * (h[1] + r[1]); z += w * (h[2] + r[2]);
          const rn = qrot(q, n);
          nx += w * rn[0]; ny += w * rn[1]; nz += w * rn[2];
        }
        const nl = Math.hypot(nx, ny, nz) || 1;
        out[v * 3] = x; out[v * 3 + 1] = y; out[v * 3 + 2] = z;
        nrm[v * 3] = nx / nl; nrm[v * 3 + 1] = ny / nl; nrm[v * 3 + 2] = nz / nl;
      }
      return {P: out, N: nrm};
    };
    // bind-pose pairs: for each vertex of `a`, the nearest vertex of `b` (brute force, once per mesh pair)
    const pairCache = new Map<string, {ia: Int32Array; ib: Int32Array; s0: Float32Array}>();
    const pairs = (key: string, A: Mesh, B: Mesh, maxD: number, inside: boolean, filter?: (v: number) => boolean) => {
      const hit = pairCache.get(key);
      if (hit) return hit;
      const ia: number[] = [], ib: number[] = [], s0: number[] = [];
      for (let v = 0; v < A.n; v++) {
        if (filter && !filter(v)) continue;
        let best = 1e9, bi = -1;
        for (let u = 0; u < B.n; u++) {
          const d = (A.P[v * 3] - B.P[u * 3]) ** 2 + (A.P[v * 3 + 1] - B.P[u * 3 + 1]) ** 2 + (A.P[v * 3 + 2] - B.P[u * 3 + 2]) ** 2;
          if (d < best) { best = d; bi = u; }
        }
        if (Math.sqrt(best) > maxD) continue;
        const sd = (A.P[v * 3] - B.P[bi * 3]) * B.N[bi * 3] + (A.P[v * 3 + 1] - B.P[bi * 3 + 1]) * B.N[bi * 3 + 1] + (A.P[v * 3 + 2] - B.P[bi * 3 + 2]) * B.N[bi * 3 + 2];
        if (inside && sd >= 0) continue;
        // a cloth vertex with a mostly vertical normal (the underside of a hem) measures a HEIGHT, not a penetration
        if (Math.abs(B.N[bi * 3 + 2]) > 0.6) continue;
        ia.push(v); ib.push(bi); s0.push(sd);
      }
      const r = {ia: Int32Array.from(ia), ib: Int32Array.from(ib), s0: Float32Array.from(s0)};
      pairCache.set(key, r);
      return r;
    };
    const clip = {skinOut: {v: 0, at: '', run: 0}, armIn: {v: 0, at: '', run: 0}, shortsOut: {v: 0, at: '', run: 0}};
    let stretchMax = {v: 0, at: ''}, numStretch = {v: 0, at: ''}, accMax = {v: 0, at: ''};
    const stretchAll: number[] = [], accAll: number[] = [];
    for (const id of ids) {
      if (plan[id].look !== 'C') continue;
      const {glb, rig} = meshOf(id);
      const joints = (glb as unknown as {__joints: string[]}).__joints;
      const rest = Object.fromEntries(rig.bones.map((b) => [b.name, b]));
      const body = glb.E2A_Body, jer = glb.E2A_Jersey, sho = glb.E2A_Shorts;
      const vkey = rv2 ? 'v2' : 'v1';
      const armBones = new Set(['upperarm.L', 'upperarm.R', 'forearm.L', 'forearm.R'].map((n) => joints.indexOf(n)));
      const pBJ = pairs(`${vkey}|${id[0]}|bodyJ`, body, jer, 0.04, true);
      const pBS = pairs(`${vkey}|${id[0]}|bodyS`, body, sho, 0.04, true);
      const pSJ = pairs(`${vkey}|${id[0]}|shoJ`, sho, jer, 0.04, true);
      const armV: number[] = [];
      for (let v = 0; v < body.n; v++) {
        let w = 0;
        for (let c = 0; c < 4; c++) if (armBones.has(body.J[v * 4 + c])) w += body.W[v * 4 + c];
        if (w > 0.5) armV.push(v);
      }
      // jersey edges (for stretch) and number region (uv)
      const edges: [number, number, number][] = [];
      for (let k = 0; k < jer.idx.length; k += 3) for (const [a, b] of [[jer.idx[k], jer.idx[k + 1]], [jer.idx[k + 1], jer.idx[k + 2]], [jer.idx[k + 2], jer.idx[k]]]) {
        const l = Math.hypot(jer.P[a * 3] - jer.P[b * 3], jer.P[a * 3 + 1] - jer.P[b * 3 + 1], jer.P[a * 3 + 2] - jer.P[b * 3 + 2]);
        if (l > 0.01) edges.push([a, b, l]); // edges under 1 cm (seam slivers, iso-cut slivers) give meaningless ratios
      }
      const inNum = (v: number) => !!jer.uv && ((jer.uv[v * 2] > 0.17 && jer.uv[v * 2] < 0.33) || (jer.uv[v * 2] > 0.67 && jer.uv[v * 2] < 0.83)) && jer.uv[v * 2 + 1] > 0.2 && jer.uv[v * 2 + 1] < 0.7;
      const runs = {skinOut: new Map<number, number>(), armIn: new Map<number, number>(), shortsOut: new Map<number, number>()};
      const hemPrev: Float32Array[] = [];
      let hemZ = 9;
      for (let v = 0; v < jer.n; v++) hemZ = Math.min(hemZ, jer.P[v * 3 + 2]);
      for (let f = f0; f <= f1; f++) {
        const t = f / FPS;
        const st = stateAt(id, t);
        const B = skin(body, joints, st, rest), Jm = skin(jer, joints, st, rest), S = skin(sho, joints, st, rest);
        if (rv2 && jer.hem) {
          const c = clothAt(play, id, t);
          for (let v = 0; v < jer.n; v++) {
            const h = jer.hem[v];
            if (h <= 0) continue;
            const q = clothDisplace([Jm.P[v * 3], Jm.P[v * 3 + 1], Jm.P[v * 3 + 2]], [Jm.N[v * 3], Jm.N[v * 3 + 1], Jm.N[v * 3 + 2]], h, (jer.ease?.[v] ?? 0) * st.s, c, st.hips);
            Jm.P[v * 3] = q[0]; Jm.P[v * 3 + 1] = q[1]; Jm.P[v * 3 + 2] = q[2];
          }
        }
        const at = `${id}@${t.toFixed(2)}`;
        const track = (kind: keyof typeof runs, v: number, pen: number) => {
          const r = (runs[kind].get(v) ?? 0) + 1;
          runs[kind].set(v, r);
          if (r > 3 && pen > clip[kind].v) clip[kind] = {v: pen, at, run: r};
        };
        const resetMissing = (kind: keyof typeof runs, seen: Set<number>) => {
          for (const k of runs[kind].keys()) if (!seen.has(k)) runs[kind].delete(k);
        };
        // skin poking OUT of jersey / shorts (pairs body-under-cloth in bind)
        const seenS = new Set<number>();
        for (const [pr, M] of [[pBJ, Jm], [pBS, S]] as const) {
          for (let k = 0; k < pr.ia.length; k++) {
            const v = pr.ia[k], u = pr.ib[k];
            const s = (B.P[v * 3] - M.P[u * 3]) * M.N[u * 3] + (B.P[v * 3 + 1] - M.P[u * 3 + 1]) * M.N[u * 3 + 1] + (B.P[v * 3 + 2] - M.P[u * 3 + 2]) * M.N[u * 3 + 2];
            if (s > 0.01) {
              const key = v + (M === S ? 1e6 : 0);
              seenS.add(key);
              track('skinOut', key, s);
            }
          }
        }
        resetMissing('skinOut', seenS);
        // shorts poking through the jersey
        const seenSJ = new Set<number>();
        for (let k = 0; k < pSJ.ia.length; k++) {
          const v = pSJ.ia[k], u = pSJ.ib[k];
          const s = (S.P[v * 3] - Jm.P[u * 3]) * Jm.N[u * 3] + (S.P[v * 3 + 1] - Jm.P[u * 3 + 1]) * Jm.N[u * 3 + 1] + (S.P[v * 3 + 2] - Jm.P[u * 3 + 2]) * Jm.N[u * 3 + 2];
          if (s > 0.005) {
            seenSJ.add(v);
            track('shortsOut', v, s);
          }
        }
        resetMissing('shortsOut', seenSJ);
        // arms INSIDE the jersey shell: grid of jersey vertices (6 cm cells), arm vertex vs nearest jersey vertex
        const cell = 0.06, grid = new Map<string, number[]>();
        for (let u = 0; u < jer.n; u++) {
          const k = `${Math.floor(Jm.P[u * 3] / cell)},${Math.floor(Jm.P[u * 3 + 1] / cell)},${Math.floor(Jm.P[u * 3 + 2] / cell)}`;
          (grid.get(k) ?? grid.set(k, []).get(k)!).push(u);
        }
        const seenA = new Set<number>();
        for (const v of armV) {
          const x = B.P[v * 3], y = B.P[v * 3 + 1], z = B.P[v * 3 + 2];
          const cx = Math.floor(x / cell), cy = Math.floor(y / cell), cz = Math.floor(z / cell);
          let best = 1e9, bu = -1;
          for (let a = -1; a <= 1; a++) for (let b = -1; b <= 1; b++) for (let c = -1; c <= 1; c++) {
            for (const u of grid.get(`${cx + a},${cy + b},${cz + c}`) ?? []) {
              const d = (x - Jm.P[u * 3]) ** 2 + (y - Jm.P[u * 3 + 1]) ** 2 + (z - Jm.P[u * 3 + 2]) ** 2;
              if (d < best) { best = d; bu = u; }
            }
          }
          if (bu < 0 || best > 0.05 * 0.05) continue;
          const s = (x - Jm.P[bu * 3]) * Jm.N[bu * 3] + (y - Jm.P[bu * 3 + 1]) * Jm.N[bu * 3 + 1] + (z - Jm.P[bu * 3 + 2]) * Jm.N[bu * 3 + 2];
          if (s < -0.01) {
            seenA.add(v);
            track('armIn', v, -s);
          }
        }
        resetMissing('armIn', seenA);
        // stability: edge stretch, number region, hem acceleration
        const sc = st.s;
        for (const [a, b, l0] of edges) {
          const l = Math.hypot(Jm.P[a * 3] - Jm.P[b * 3], Jm.P[a * 3 + 1] - Jm.P[b * 3 + 1], Jm.P[a * 3 + 2] - Jm.P[b * 3 + 2]) / (l0 * sc);
          if (l > stretchMax.v) stretchMax = {v: l, at};
          if (f % 3 === 0) stretchAll.push(l);
          if (inNum(a) && inNum(b) && l > numStretch.v) numStretch = {v: l, at};
        }
        // hem band (both versions): jersey vertices within 8 cm of the lowest jersey vertex in bind; acceleration of
        // the vertex RELATIVE to the pelvis joint (cloth vibration, not the player's own acceleration)
        const rel = Jm.P.slice();
        for (let v = 0; v < jer.n; v++) { rel[v * 3] -= st.hips[0]; rel[v * 3 + 1] -= st.hips[1]; rel[v * 3 + 2] -= st.hips[2]; }
        hemPrev.push(rel);
        if (hemPrev.length > 3) hemPrev.shift();
        if (hemPrev.length === 3) {
          for (let v = 0; v < jer.n; v++) {
            if (jer.P[v * 3 + 2] > hemZ + 0.08) continue;
            const ax = (hemPrev[2][v * 3] - 2 * hemPrev[1][v * 3] + hemPrev[0][v * 3]) * FPS * FPS;
            const ay = (hemPrev[2][v * 3 + 1] - 2 * hemPrev[1][v * 3 + 1] + hemPrev[0][v * 3 + 1]) * FPS * FPS;
            const az = (hemPrev[2][v * 3 + 2] - 2 * hemPrev[1][v * 3 + 2] + hemPrev[0][v * 3 + 2]) * FPS * FPS;
            const a = Math.hypot(ax, ay, az);
            if (a > accMax.v) accMax = {v: a, at};
            accAll.push(a);
          }
        }
      }
    }
    const clipFail = clip.skinOut.v > 0 || clip.armIn.v > 0 || clip.shortsOut.v > 0;
    gates.push({gate: 'cloth_clip', status: clipFail ? 'FAIL' : 'PASS',
      value: `skin out of jersey/shorts > 1 cm for > 3 frames: ${clip.skinOut.v ? `${(clip.skinOut.v * 100).toFixed(1)} cm (${clip.skinOut.at})` : 'none'}; arms inside the jersey > 1 cm for > 3 frames: ${clip.armIn.v ? `${(clip.armIn.v * 100).toFixed(1)} cm (${clip.armIn.at})` : 'none'}; shorts through the jersey: ${clip.shortsOut.v ? `${(clip.shortsOut.v * 100).toFixed(1)} cm (${clip.shortsOut.at})` : 'none'}`,
      detail: clip});
    const q = (arr: number[], k: number) => { const s2 = arr.slice().sort((a, b) => a - b); return s2.length ? s2[Math.min(s2.length - 1, Math.floor(k * s2.length))] : 0; };
    const st999 = q(stretchAll, 0.999), acc99 = q(accAll, 0.99);
    gates.push({gate: 'cloth_stability', status: st999 > 1.3 ? 'FAIL' : numStretch.v > 1.15 || acc99 > 12 ? 'WARN' : 'PASS',
      value: `jersey edge stretch (edges >= 1 cm) p99.9 ×${st999.toFixed(2)}, max ×${stretchMax.v.toFixed(2)} (${stretchMax.at}); number region max ×${numStretch.v.toFixed(2)} (${numStretch.at}); hem band acceleration vs pelvis p99 ${acc99.toFixed(1)} m/s², max ${accMax.v.toFixed(1)} m/s² (${accMax.at})${rv2 ? ' [v2 apparel + cloth2]' : ' [v1 apparel, skin-tight]'}`});
    stats.cloth = {clip, stretchMax, st999, numStretch, accMax, acc99};
  }

  // ---------------------------------------------------------------- 10. court geometry
  {
    const notes: string[] = [];
    let ok = Math.abs(BALL_R - 0.121) < 1e-6 && Math.abs(FIBA.rimZ - 3.05) < 1e-6 && Math.abs(FIBA.basket[1] - 1.575) < 1e-6;
    let out = 0;
    for (let f = f0; f <= f1; f += 3) {
      const t = f / FPS;
      for (const id of ids) {
        if (plan[id].look !== 'C') continue;
        const st = stateAt(id, t);
        for (let i = 0; i < 2; i++) {
          const s = soles(id, st, i);
          for (const q of [s.heel, s.ball]) if (Math.abs(q[0]) > 7.6 || q[1] < -0.1 || q[1] > 14.1) out++;
        }
      }
    }
    if (out) notes.push(`${out} sole samples outside the court`);
    for (const e of play.ball) {
      if ((e.type === 'shot' || e.type === 'layup') && e.make !== false && e.t1 >= t0 && e.t1 <= t1 + 0.5) {
        let best = 9;
        for (let t = e.t1 - 0.15; t <= e.t1 + 0.2; t += 1 / 480) {
          const a = ballAt(t).pos, b = ballAt(t + 1 / 480).pos;
          if (a[2] >= RIM[2] && b[2] < RIM[2]) best = Math.min(best, Math.hypot(a[0] - RIM[0], a[1] - RIM[1]));
        }
        notes.push(`${e.type} ${e.player} make: crosses the rim plane ${best < 9 ? `${(best * 100).toFixed(1)} cm from the centre` : 'NOT detected'}`);
        if (best > 0.1) ok = false;
      }
    }
    ok = ok && out === 0;
    gates.push({gate: 'court', status: ok ? 'PASS' : 'FAIL', value: `ball r ${BALL_R} m, rim ${FIBA.rimZ} m at (${FIBA.basket.join(', ')}); ${notes.join('; ') || 'no make in range'}`});
  }
  return {id: play.id, gates, stats};
};

const reports = [];
let anyFail = false;
for (const f of files) {
  const t = Date.now();
  const r = runPlay(f);
  console.log(`\n=== ${r.id}${legacy ? ' (LEGACY: realism module off, v1 meshes)' : ''}${range ? ` range ${range.join('-')} s` : ''}  [${((Date.now() - t) / 1000).toFixed(1)} s]`);
  for (const g of r.gates) {
    console.log(`${g.status.padEnd(4)}  ${g.gate.padEnd(16)} ${g.value}`);
    if (g.status === 'FAIL') anyFail = true;
  }
  reports.push(r);
}
if (jsonOut) fs.writeFileSync(jsonOut, JSON.stringify({generated: new Date().toISOString(), legacy, range, reports}, null, 1));
process.exitCode = anyFail ? 1 : 0;
