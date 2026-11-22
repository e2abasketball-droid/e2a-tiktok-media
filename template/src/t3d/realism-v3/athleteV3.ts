// E2A Realism V3 (2026-11-22) — AthleteV3 pose bridge: engine Pose (rig.ts, unchanged) -> bone rotations of the V3
// player (27 bones: the 21 of e2a-player-v1 + fingers1 / fingers2 / thumb per hand), corrective morph weights and the
// hand-ball grip. PURE function of (rig, pose, scale, ball): no state, no simulation -> the same frame whether Remotion
// plays, seeks, slows down or rewinds (brief sec. 3 "Reto fundamental"; checked by scripts/qc-realism-v3.mts seek test).
//
// Opt-in only: athleteRenderer 'v3' (episode / shot / split). The default renderer stays 'legacy' (flag.ts).
//   fingers   a grip solver per hand: when the ball is within reach of the palm, the curls of fingers1 (knuckle) and
//             fingers2 (middle joint) that put BOTH the middle joint and the fingertip on the ball surface (wrap, no
//             penetration) are chosen by a fixed 2-D search over the rest geometry exported by build_player.py
//             (rig.fingers); thumb by a 1-D search; far from the ball the hand relaxes. Blended by distance (no pop).
//   weight    weightShift(play, id, t): track deceleration / lateral acceleration (window +-0.2 s) -> hips drop + trunk
//             tilt (back on a brake, into the turn on a cut), legs re-solved by 2-bone IK so the ankles stay planted.
//             Off while the player has the ball. Pure function of the play and t (seek-safe).
//   morphs    knee / elbow pose-space correctives (delta-mush shape keys, build_player.py --rig v3): weight = joint
//             flexion beyond rest / key angle, clamped to [0, 1].
//   head      the neutral head of bonesFromPose kept the eyes level but the mesh still read "chin up" (open defect of
//             the MPFB lab, 2026-11-19): V3 adds HEAD_PITCH_FIX degrees of chin-down on the head (half on the neck).
import type {V3} from '../../tactical/geometry.ts';
import type {Pose} from '../rig.ts';
import type {ClipBone, Q, SkelRig} from '../skelclip.ts';
import {bonesFromPose, qconj, qmul, qrot, qslerp} from '../skelclip.ts';
import type {Play} from '../../tactical/play.ts';
import {posAt, sample} from '../../tactical/play.ts';

export type FingerRest = {K: V3; M: V3; T: V3; TB: V3; TT: V3; W: V3; palm: V3; axis: V3; thumbAxis: V3; palmN: V3};
export type CorrectiveDesc = {name: string; bone: string; parent: string; key: number; axis?: V3; mode?: 'angle' | 'flex'};
export type RigV3 = SkelRig & {version: string; variant: 'off' | 'def'; H: number; kit: Record<string, string>; fingers: Record<'L' | 'R', FingerRest>; correctives: CorrectiveDesc[]};

export const ATHLETE_V3 = {
  headPitchFixDeg: 7, // chin down on top of bonesFromPose's neutral head (measured on the V3 close-ups, see QA_REPORT)
  relaxCurl: 0.32, // rad, natural curl of a hand that holds nothing (fingers1; fingers2 gets 1.15x, thumb 0.5x)
  gripReach: 0.3, // m: palm-to-ball-centre distance where the grip starts to blend in
  gripFull: 0.17, // m: full grip under this distance
  skin: 0.006, // m: fingertip pad thickness kept between the tip joint and the ball surface
  ballR: 0.121,
};

const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a: V3, k: number): V3 => [a[0] * k, a[1] * k, a[2] * k];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const norm = (a: V3): V3 => mul(a, 1 / Math.max(1e-9, len(a)));
const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const smooth = (x: number) => {
  const u = clamp(x);
  return u * u * (3 - 2 * u);
};
const axisAngle = (ax: V3, th: number): Q => {
  const s = Math.sin(th / 2);
  const n = norm(ax);
  return [n[0] * s, n[1] * s, n[2] * s, Math.cos(th / 2)];
};
/** rotate point p about the axis through c */
const rotAbout = (p: V3, c: V3, q: Q): V3 => add(c, qrot(q, sub(p, c)));

const FINGER_BONES = new Set(['fingers1.L', 'fingers2.L', 'thumb.L', 'fingers1.R', 'fingers2.R', 'thumb.R']);
const baseCache = new WeakMap<RigV3, SkelRig>();
/** the 21-bone view of the V3 rig (same rest frames): bonesFromPose solves the body, the bridge adds the hands */
const baseRig = (r: RigV3): SkelRig => {
  let b = baseCache.get(r);
  if (!b) {
    b = {bones: r.bones.filter((x) => !FINGER_BONES.has(x.name)), restJoints: r.restJoints};
    baseCache.set(r, b);
  }
  return b;
};

/** world positions of the bone heads (play space) by forward kinematics of world rotations */
const fkHeads = (rig: RigV3, bones: Record<string, Q>, hips: V3, scale: number) => {
  const by = new Map(rig.bones.map((b) => [b.name, b] as const));
  const pos: Record<string, V3> = {[rig.bones[0].name]: hips};
  const at = (name: string): V3 => {
    if (pos[name]) return pos[name];
    const b = by.get(name)!;
    const p = by.get(b.parent!)!;
    const local = qrot(qconj(p.R), mul(sub(b.head, p.head), scale));
    pos[name] = add(at(p.name), qrot(bones[p.name], local));
    return pos[name];
  };
  return at;
};

export type GripInfo = {side: 'L' | 'R'; w: number; curl: number; thumb: number; tipGap: number; thumbGap: number; palmGap: number};
export type BallCtx = {pos: V3; held: boolean};

/** WRAP of the fingers on the ball (2-D search, deterministic): fingers1 curl th (knuckle) and fingers2 extra curl th2
 *  (middle joint) chosen so that BOTH the middle joint and the fingertip sit on the ball surface (+ pad), never inside:
 *  the fingers follow the sphere instead of touching it with the tips only */
const solveCurl = (K: V3, M: V3, T: V3, ax: V3, c: V3, r: number) => {
  let best = {th: ATHLETE_V3.relaxCurl, th2: ATHLETE_V3.relaxCurl * 0.15, err: Infinity, gap: 0};
  const pad = r + ATHLETE_V3.skin;
  for (let i = 0; i <= 40; i++) {
    const th = -0.3 + (i / 40) * 1.75; // -17 deg (fingers lifted off a ball the engine sank into the palm) .. 83 deg
    const q1 = axisAngle(ax, th);
    const M1 = rotAbout(M, K, q1);
    const gM = len(sub(M1, c)) - pad;
    const T0 = rotAbout(T, K, q1);
    for (let j = 0; j <= 32; j++) {
      const th2 = (j / 32) * 1.5;
      const T1 = rotAbout(T0, M1, axisAngle(ax, th2));
      const gap = len(sub(T1, c)) - pad;
      const err = Math.abs(gap) + 0.6 * Math.abs(gM) + 4 * Math.abs(Math.min(0, gM)) + 4 * Math.abs(Math.min(0, gap)) + 0.002 * (Math.abs(th) + th2);
      if (err < best.err) best = {th, th2, err, gap};
    }
  }
  return best;
};

/** Realism V3 weight layer (brief sec. 6/8: "peso corporal"): what the engine track says about deceleration and turning,
 *  as a pure function of (play, player, t). A hard brake drops the hips and sets the trunk back, a cut banks the trunk
 *  into the turn. Acceleration from the track, averaged over +-0.15 s (no step jitter); off while the player has the ball
 *  (hands stay on the engine's ball), blended over +-0.2 s around catches and releases. */
export type WeightShift = {drop: number; tilt: V3; w: number; brake: number; lat: number};
export const V3_WEIGHT = {dropPerG: 0.075, backRad: 0.2, sideRad: 0.16, a0: 1.5, a1: 9};
export const weightShift = (play: Play, id: string, t: number): WeightShift => {
  const wp = play.tracks[id];
  const none = {drop: 0, tilt: [0, 0, 0] as V3, w: 0, brake: 0, lat: 0};
  if (!wp || wp.length < 2) return none;
  const P = (x: number) => posAt(wp, Math.min(play.duration, Math.max(0, x)));
  const h = 1 / 30;
  const vel = (x: number): [number, number] => {
    const a = P(x - h), b = P(x + h);
    return [(b[0] - a[0]) / (2 * h), (b[1] - a[1]) / (2 * h)];
  };
  let ax = 0, ay = 0, vx = 0, vy = 0, spm = 0;
  const K = 8;
  for (let k = -K; k <= K; k++) {
    const x = t + (k / K) * 0.2;
    const v0 = vel(x - h), v1 = vel(x + h), v = vel(x);
    ax += (v1[0] - v0[0]) / (2 * h); ay += (v1[1] - v0[1]) / (2 * h);
    vx += v[0]; vy += v[1]; spm += Math.hypot(v[0], v[1]);
  }
  ax /= 2 * K + 1; ay /= 2 * K + 1; vx /= 2 * K + 1; vy /= 2 * K + 1; spm /= 2 * K + 1;
  // direction of travel over the window (still defined at the plant of a stop: the window reaches into the run-in)
  const sp = Math.hypot(vx, vy);
  if (sp < 0.05 || spm < 0.25) return none;
  const fx = vx / sp, fy = vy / sp;
  const brake = Math.max(0, -(ax * fx + ay * fy));
  const lat = ax * -fy + ay * fx; // + = accelerating toward the left of the motion
  const g = (a: number) => smooth((a - V3_WEIGHT.a0) / (V3_WEIGHT.a1 - V3_WEIGHT.a0));
  // the layer is off while this player has the ball (soft, +-0.2 s)
  let hold = 0;
  for (let k = -4; k <= 4; k++) if (sample(play, Math.min(play.duration, Math.max(0, t + k * 0.05))).ball.holder === id) hold++;
  const w = (1 - hold / 9) * smooth(spm / 1.0);
  const gb = g(brake), gl = g(Math.abs(lat)) * Math.sign(lat);
  const tilt: V3 = [(-fx * gb * V3_WEIGHT.backRad + -fy * gl * V3_WEIGHT.sideRad) * w, (-fy * gb * V3_WEIGHT.backRad + fx * gl * V3_WEIGHT.sideRad) * w, 0];
  return {drop: (gb * 0.8 + Math.abs(gl) * 0.4) * V3_WEIGHT.dropPerG * w, tilt, w, brake, lat};
};

/** shortest rotation taking direction a to direction b */
const fromTo = (a: V3, b: V3): Q => {
  const u = norm(a), v = norm(b);
  const c = dot(u, v);
  if (c > 1 - 1e-9) return [0, 0, 0, 1];
  const x: V3 = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]];
  const q: Q = [x[0], x[1], x[2], 1 + c];
  const l = Math.hypot(q[0], q[1], q[2], q[3]);
  return [q[0] / l, q[1] / l, q[2] / l, q[3] / l];
};
const UPPER = ['spine', 'chest', 'neck', 'head', 'clavicle.L', 'upperarm.L', 'forearm.L', 'hand.L', 'clavicle.R', 'upperarm.R', 'forearm.R', 'hand.R'];

/** apply a WeightShift on solved bones: hips root lowered, upper body tilted rigidly about the spine base, both legs
 *  re-solved (2-bone IK, same knee plane) so the ankles stay exactly where the engine planted them */
const applyWeight = (rig: RigV3, bones: Record<string, Q>, hips: V3, scale: number, ws: WeightShift): V3 => {
  if (ws.drop < 1e-4 && Math.hypot(ws.tilt[0], ws.tilt[1]) < 1e-4) return hips;
  const at0 = fkHeads(rig, bones, hips, scale);
  const by = new Map(rig.bones.map((b) => [b.name, b] as const));
  const keep: Record<string, V3> = {};
  for (const s of ['L', 'R']) for (const n of [`thigh.${s}`, `shin.${s}`, `foot.${s}`]) keep[n] = at0(n);
  const hips2: V3 = [hips[0], hips[1], hips[2] - ws.drop];
  const ang = Math.hypot(ws.tilt[0], ws.tilt[1]);
  if (ang > 1e-5) {
    // tilt the trunk toward ws.tilt: rotation axis = up x tilt direction
    const L = axisAngle([-ws.tilt[1], ws.tilt[0], 0], ang);
    for (const n of UPPER) bones[n] = qmul(L, bones[n]);
  }
  const at1 = fkHeads(rig, bones, hips2, scale);
  for (const s of ['L', 'R']) {
    const H0 = keep[`thigh.${s}`], K0 = keep[`shin.${s}`], A = keep[`foot.${s}`], H1 = at1(`thigh.${s}`);
    const l1 = len(sub(by.get(`shin.${s}`)!.head, by.get(`thigh.${s}`)!.head)) * scale;
    const l2 = len(sub(by.get(`foot.${s}`)!.head, by.get(`shin.${s}`)!.head)) * scale;
    const dv = sub(A, H1);
    const d = Math.min(len(dv), (l1 + l2) * 0.999);
    const n = norm(dv);
    const a = (l1 * l1 - l2 * l2 + d * d) / (2 * d);
    const hh = Math.sqrt(Math.max(0, l1 * l1 - a * a));
    const kp = sub(K0, H1);
    const pole = norm(sub(kp, mul(n, dot(kp, n))));
    const K1 = add(add(H1, mul(n, a)), mul(pole, hh));
    bones[`thigh.${s}`] = qmul(fromTo(sub(K0, H0), sub(K1, H1)), bones[`thigh.${s}`]);
    bones[`shin.${s}`] = qmul(fromTo(sub(A, K0), sub(A, K1)), bones[`shin.${s}`]);
  }
  return hips2;
};

export type V3Frame = {bones: Record<string, Q>; hips: V3; morph: Record<string, number>; grip: GripInfo[]};

/** the V3 bones of one player at one instant: body from bonesFromPose (unchanged engine solve), then head fix, hands, morphs */
export const bonesV3 = (rig: RigV3, P: Pose, scale: number, ball?: BallCtx, weight?: WeightShift, hipsUp?: V3): V3Frame => {
  const base = bonesFromPose(baseRig(rig), P, scale, hipsUp);
  const bones: Record<string, Q> = {...base.bones};
  const hips0 = weight ? applyWeight(rig, bones, base.hips, scale, weight) : base.hips;
  const by = new Map(rig.bones.map((b) => [b.name, b] as const));
  // head: chin down by HEAD_PITCH_FIX about the head's own left axis (half of it on the neck)
  {
    const hb = by.get('head')!;
    const left = qrot(qmul(bones.head, qconj(hb.R)), [1, 0, 0] as V3); // rest left axis of the body is +x (rest faces -y)
    const fix = (ATHLETE_V3.headPitchFixDeg * Math.PI) / 180;
    bones.head = qmul(axisAngle(left, fix), bones.head);
    bones.neck = qmul(axisAngle(left, fix * 0.5), bones.neck);
  }
  const at = fkHeads(rig, bones, hips0, scale);
  const grip: GripInfo[] = [];
  for (const s of ['L', 'R'] as const) {
    const fr = rig.fingers[s];
    const hand = by.get(`hand.${s}`)!;
    const D = qmul(bones[`hand.${s}`], qconj(hand.R)); // world delta of the hand from its rest
    const wrist = at(`hand.${s}`);
    const W = (x: V3): V3 => add(wrist, qrot(D, mul(sub(x, fr.W), scale)));
    const ax = qrot(D, fr.axis);
    const tax = qrot(D, fr.thumbAxis);
    const K = W(fr.K), M = W(fr.M), T = W(fr.T), TB = W(fr.TB), TT = W(fr.TT), palm = W(fr.palm);
    let curl = ATHLETE_V3.relaxCurl;
    let curl2 = ATHLETE_V3.relaxCurl * 0.15;
    let thumb = ATHLETE_V3.relaxCurl * 0.5;
    let w = 0;
    let tipGap = NaN, thumbGap = NaN, palmGap = NaN;
    if (ball) {
      const r = ATHLETE_V3.ballR;
      const dPalm = len(sub(ball.pos, palm));
      w = smooth((ATHLETE_V3.gripReach - dPalm) / (ATHLETE_V3.gripReach - ATHLETE_V3.gripFull));
      if (w > 0) {
        const sol = solveCurl(K, M, T, ax, ball.pos, r);
        curl = ATHLETE_V3.relaxCurl + (sol.th - ATHLETE_V3.relaxCurl) * w;
        curl2 = curl2 + (sol.th2 - curl2) * w;
        // thumb: same search on its own chain (one segment)
        let tb = {th: thumb, err: Infinity};
        for (let i = 0; i <= 48; i++) {
          const th = (i / 48) * 1.1;
          const t1 = rotAbout(TT, TB, axisAngle(tax, th));
          const err = Math.abs(len(sub(t1, ball.pos)) - r - ATHLETE_V3.skin) + 0.002 * th;
          if (err < tb.err) tb = {th, err};
        }
        thumb = thumb + (tb.th - thumb) * w;
      }
      const q1 = axisAngle(ax, curl);
      const M1 = rotAbout(M, K, q1);
      const T1 = rotAbout(rotAbout(T, K, q1), M1, axisAngle(ax, curl2));
      tipGap = len(sub(T1, ball.pos)) - r;
      thumbGap = len(sub(rotAbout(TT, TB, axisAngle(tax, thumb)), ball.pos)) - r;
      palmGap = dPalm - r;
    }
    bones[`fingers1.${s}`] = qmul(qmul(axisAngle(ax, curl), D), by.get(`fingers1.${s}`)!.R);
    bones[`fingers2.${s}`] = qmul(qmul(axisAngle(ax, curl + curl2), D), by.get(`fingers2.${s}`)!.R);
    bones[`thumb.${s}`] = qmul(qmul(axisAngle(tax, thumb), D), by.get(`thumb.${s}`)!.R);
    grip.push({side: s, w, curl, thumb, tipGap, thumbGap, palmGap});
  }
  // corrective morph weights from the joint flexion (angle between parent and child bone directions, minus rest)
  const morph: Record<string, number> = {};
  const dirOf = (name: string, q: Q) => {
    const b = by.get(name)!;
    return norm(qrot(qmul(q, qconj(b.R)), sub(b.tail, b.head)));
  };
  for (const c of rig.correctives ?? []) {
    const pb = by.get(c.parent)!, cb = by.get(c.bone)!;
    if (c.mode === 'flex') {
      // signed sagittal flexion of the child seen in the parent's rest frame (body rest faces -y, z up): forward swing > 0
      const Dp = qmul(bones[c.parent], qconj(pb.R));
      const d = qrot(qconj(Dp), dirOf(c.bone, bones[c.bone]));
      const r0 = norm(sub(cb.tail, cb.head));
      const flex = Math.atan2(-d[1], -d[2]) - Math.atan2(-r0[1], -r0[2]);
      morph[c.name] = clamp(flex / ((c.key * Math.PI) / 180));
      continue;
    }
    const rest = Math.acos(clamp(dot(norm(sub(pb.tail, pb.head)), norm(sub(cb.tail, cb.head))), -1, 1));
    const now = Math.acos(clamp(dot(dirOf(c.parent, bones[c.parent]), dirOf(c.bone, bones[c.bone])), -1, 1));
    morph[c.name] = clamp((now - rest) / ((c.key * Math.PI) / 180));
  }
  return {bones, hips: hips0, morph, grip};
};

/** Realism V3.1: world palm centre of one hand for solved bones (hand IK correction onto the ball) */
export const palmWorld = (rig: RigV3, bones: Record<string, Q>, hips: V3, scale: number, s: 'L' | 'R'): V3 => {
  const at = fkHeads(rig, bones, hips, scale);
  const fr = rig.fingers[s];
  const hb = rig.bones.find((b) => b.name === `hand.${s}`)!;
  const D = qmul(bones[`hand.${s}`], qconj(hb.R));
  return add(at(`hand.${s}`), qrot(D, mul(sub(fr.palm, fr.W), scale)));
};
export {baseRig, fkHeads};

/** legacy hand (no finger bones: the fingers keep the rest curl, rigid on `hand`) measured with the same geometry, for QA */
export const legacyTipGap = (rig: RigV3, P: Pose, scale: number, ball: V3) => {
  const base = bonesFromPose(baseRig(rig), P, scale);
  const at = fkHeads(rig, base.bones, base.hips, scale);
  const by = new Map(rig.bones.map((b) => [b.name, b] as const));
  return (['L', 'R'] as const).map((s) => {
    const fr = rig.fingers[s];
    const D = qmul(base.bones[`hand.${s}`], qconj(by.get(`hand.${s}`)!.R));
    const W = (x: V3): V3 => add(at(`hand.${s}`), qrot(D, mul(sub(x, fr.W), scale)));
    return {side: s, tipGap: len(sub(W(fr.T), ball)) - ATHLETE_V3.ballR, thumbGap: len(sub(W(fr.TT), ball)) - ATHLETE_V3.ballR, palmGap: len(sub(W(fr.palm), ball)) - ATHLETE_V3.ballR};
  });
};

export const ALL_V3_BONES = (rig: RigV3): ClipBone[] => rig.bones;
export {qslerp};
