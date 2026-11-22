// E2A Realism V3.3 (2026-11-22) — copy of the V3.2 library (realism-v3-2/library.ts, untouched) extended for full-court
// plays compiled from data (compile33.ts): several ball windows per player (catch -> pass/shot, start with the ball),
// multi-bounce live dribbles ('dribbleRun'), hand-offs, a 'screen' stance, facing the ball, body profiles (height /
// build / cadence / intensity / handedness) and adaptive catch-and-shoot timing. V3.2 behaviour is NOT changed (its
// own file keeps rendering 'v32').
// --- V3.2 header follows ---
// E2A Realism V3.2 (2026-11-22) — PARAMETRISED motion library. Replaces the per-play hand keys of V3.1 (clips.ts):
// a clip is now BUILT from a short script of reusable primitives on top of the player's tactical track, with
// per-player variation (seed -> timing, amplitude, posture), so two players never repeat the same gesture 1:1.
//
// Primitives (Seg.k)       what the builder derives from it
//   stand   (ready / triple / defense / relaxed / closeout) stance width, pelvis drop, arm mode, facing
//   move    (run / shuffle / backpedal / closeout)          footsteps from the track SPEED: cadence 2.0-4.4 steps/s,
//                                                            duty factor 0.62 (walk) -> 0.30 (sprint), stride length and
//                                                            foot placement from speed; acceleration -> forward lean,
//                                                            deceleration -> counter-lean (both from the track), heading
//                                                            from the velocity (or a facing target for shuffle/backpedal)
//   plant   one forced footstep (side, time): braking heel strike ahead of the body + optional cut (shoulders lead,
//           trunk banks into the new direction, explosive first step = shorter ground contact after it)
//   step    one explicit footstep (jab, step-back, 1-2 stop) with offsets
//   pivot   rotation on the ball of a planted foot
//   catch   hands up 0.45 s before the ball arrives, palms to the ball, give (elbows absorb) 0.38 s, then pocket
//   dribble push / floor / catch times of one bounce
//   pass    ball from the chest pocket to the receiver (arms extend, thumbs down follow-through)
//   jumpshot full cycle from the release time: gather, dip, load, takeoff, rise, release (just before the apex),
//           follow-through, descent, landing (absorption), recovery — ONE phase clock drives legs, pelvis, trunk, arms
//           and ball (motion32.ts shotPhase), flight time from the jump height (ballistic, g = 9.81)
// Output: the Clip32 consumed by motion32.ts (steps, channels, arm / look keys, ball, shot) — pure data, deterministic.
import type {V3} from '../../tactical/geometry.ts';
import type {Play} from '../../tactical/play.ts';
import {posAt, sample} from '../../tactical/play.ts';
import type {ArmKey, Clip31, Key, Step} from '../realism-v3-1/clips.ts';

export type Face = 'path' | 'rim' | string | number;
export type Stance = 'ready' | 'triple' | 'defense' | 'relaxed' | 'closeout' | 'screen';
export type Seg =
  | {k: 'stand'; t0: number; t1: number; pose?: Stance; face?: Face}
  | {k: 'move'; t0: number; t1: number; mode?: 'run' | 'shuffle' | 'backpedal' | 'closeout'; face?: Face}
  | {k: 'plant'; t: number; side: 0 | 1; cut?: number; wide?: number}
  | {k: 'step'; side: 0 | 1; lift: number; land: number; f: number; l: number; heel?: number; h?: number; toeOff?: number; yaw?: number}
  | {k: 'pivot'; side: 0 | 1; t0: number; t1: number; dyaw: number}
  | {k: 'catch'; t: number; from?: string; style?: PassStyle}
  | {k: 'dribble'; push: number; floor: number; catch: number}
  | {k: 'dribbleRun'; t0: number; t1: number; hand?: 1 | -1; floors: number[]}
  | {k: 'pass'; t: number; to: string; style?: PassStyle; t1?: number}
  | {k: 'jumpshot'; release: number; H?: number; quick?: boolean};
export type PassStyle = 'chest' | 'bounce' | 'overhead' | 'handoff';
/** V3.3 body profile: deterministic per player (compile33 derives it from the play: role, height table, seed) */
export type Profile = {height?: number; cadence?: number; intensity?: number; posture?: number; hand?: 1 | -1};
export type Vary = {seed: number; timing?: number; amp?: number; profile?: Profile};
export type ArmKey32 = Omit<ArmKey, 'm'> & {m: ArmKey['m'] | 'closeout' | 'pass' | 'jumpshot' | 'relaxed' | 'screen' | 'handoff' | 'take'};
export type Clip32 = Omit<Clip31, 'arms'> & {
  arms: ArmKey32[];
  shot?: {release: number; t0: number; t1: number; H: number; dipT: number; gatherT: number; recoverT: number; armT?: number; quick?: boolean};
  pass?: {t: number; to: string};
  stanceW: Key[]; // extra half-width of the stance (m) added to every planted lateral offset
  /** V3.3: every ball window of the player [start, end) with how it starts (catch / start / handoff) and ends */
  windows: {a: number; b: number; start: 'catch' | 'start' | 'handoff'; end: 'pass' | 'shot' | 'handoff' | 'none'; from?: string; to?: string}[];
  dribbles: {t0: number; t1: number; hand: 1 | -1; floors: number[]; push?: number[]; catch?: number[]}[];
  passes: {t: number; to: string; style: PassStyle; t1?: number}[];
  catches: {t: number; from?: string; style: PassStyle}[];
  stances: {t0: number; t1: number; pose?: Stance}[];
  profile: Required<Profile>;
  vary: Required<Vary> & {k: {cad: number; lean: number; drop: number; swing: number; width: number}};
  script: Seg[];
  facing: Key[]; // heading used by stand / shuffle / backpedal segments (already merged into heading)
};

const PUSH33 = 0.17; // = motion33 PUSH (leg extension before take-off)
/** V3.3 possession windows from the script: a catch (or the start of a player who has the ball at t = 0) opens one,
 *  the next pass / shot release closes it */
export const windowsOf = (segs: Seg[], shot?: {release: number}): Clip32['windows'] => {
  type W = Clip32['windows'][number];
  const opens: {t: number; start: W['start']; from?: string}[] = segs.filter((s): s is Extract<Seg, {k: 'catch'}> => s.k === 'catch').map((s) => ({t: s.t, start: s.style === 'handoff' ? 'handoff' : 'catch', from: s.from}));
  const closes: {t: number; end: W['end']; to?: string}[] = [
    ...segs.filter((s): s is Extract<Seg, {k: 'pass'}> => s.k === 'pass').map((s) => ({t: s.style === 'handoff' ? s.t1 ?? s.t + 0.2 : s.t, end: (s.style === 'handoff' ? 'handoff' : 'pass') as W['end'], to: s.to})),
    ...(shot ? [{t: shot.release, end: 'shot' as const}] : []),
  ].sort((a, b) => a.t - b.t);
  const startsWithBall = segs.some((s) => (s.k === 'dribbleRun' && s.t0 < 0.05) || (s.k === 'stand' && s.t0 < 0.05 && s.pose === 'triple'));
  if (startsWithBall && (!opens.length || closes.length && closes[0].t < opens[0].t)) opens.unshift({t: 0, start: 'start'});
  opens.sort((a, b) => a.t - b.t);
  const out: W[] = [];
  for (const o of opens) {
    const c = closes.find((x) => x.t > o.t + 1e-6);
    out.push({a: o.t, b: c ? c.t : Infinity, start: o.start, end: c ? c.end : 'none', from: o.from, to: c?.to});
  }
  return out;
};

// ---------------------------------------------------------------- deterministic variation
const hash = (s: number) => {
  let x = Math.imul(s ^ 0x9e3779b9, 0x85ebca6b) >>> 0;
  x = Math.imul(x ^ (x >>> 13), 0xc2b2ae35) >>> 0;
  return ((x ^ (x >>> 16)) >>> 0) / 4294967296;
};
const vr = (seed: number, k: number, amp: number) => (hash(seed * 7919 + k * 104729) * 2 - 1) * amp;

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const smooth = (x: number) => {
  const u = clamp(x);
  return u * u * (3 - 2 * u);
};
const wrap = (a: number) => Math.atan2(Math.sin(a), Math.cos(a));
const RIM: [number, number] = [0, 1.575];

/** biomechanics of locomotion vs speed (m/s): step cadence (steps/s), duty factor (share of the stride a foot is on
 *  the ground), landing offset ahead of the pelvis, swing height — literature ranges: walking 1.8-2 steps/s duty 0.6,
 *  jogging 2.6-2.9 / 0.4, sprint 4-4.5 / 0.28-0.32 */
export const gait = (v: number) => ({
  cad: clamp(1.9 + 0.5 * v, 1.9, 4.4),
  duty: clamp(0.62 - 0.065 * v, 0.3, 0.62),
  fwd: clamp(0.05 + 0.05 * v, 0.05, 0.3),
  h: clamp(0.06 + 0.022 * v, 0.06, 0.17),
});

type Ctx = {play: Play; id: string; dur: number; root: (t: number) => [number, number]; vel: (t: number) => [number, number]; speed: (t: number) => number};
const ctxOf = (play: Play, id: string): Ctx => {
  const tr = play.tracks[id];
  const root = (t: number): [number, number] => {
    const p = posAt(tr, clamp(t, 0, play.duration));
    return [p[0], p[1]];
  };
  const vel = (t: number): [number, number] => {
    const a = root(t - 0.04), b = root(t + 0.04);
    return [(b[0] - a[0]) / 0.08, (b[1] - a[1]) / 0.08];
  };
  return {play, id, dur: play.duration, root, vel, speed: (t) => Math.hypot(...vel(t))};
};

const faceAngle = (c: Ctx, f: Face | undefined, t: number, fallback: number): number => {
  if (f === undefined || f === 'path') return fallback;
  if (typeof f === 'number') return f;
  const r = c.root(t);
  let p: [number, number];
  if (f === 'rim') p = RIM;
  else if (f === 'ball') {
    const b = sample(c.play, clamp(t, 0, c.dur)).ball.pos;
    p = [b[0], b[1]];
    if (Math.hypot(p[0] - r[0], p[1] - r[1]) < 0.4) return fallback; // the holder does not "face" the ball in his hands
  } else {
    const q = posAt(c.play.tracks[f], clamp(t, 0, c.dur));
    p = [q[0], q[1]];
  }
  return Math.atan2(p[1] - r[1], p[0] - r[0]);
};

/** sample a function into monotone-cubic keys every dt (the evaluator interpolates them) */
const keysOf = (f: (t: number) => number, t0: number, t1: number, dt = 0.05): Key[] => {
  const out: Key[] = [];
  for (let t = t0; t <= t1 + 1e-9; t += dt) out.push([Math.round(t * 1000) / 1000, Math.round(f(t) * 10000) / 10000]);
  return out;
};

/** build the Clip32 of player `id` from a script of primitives (sorted by time) */
export const buildClip = (play: Play, id: string, script: Seg[], vary: Vary, label: string): Clip32 => {
  const c = ctxOf(play, id);
  const V = {seed: vary.seed, timing: vary.timing ?? 1, amp: vary.amp ?? 1};
  // V3.3 profile: cadence scales the step rate, posture lowers / raises the base drop and lean, intensity the arm swing
  const PF: Required<Profile> = {height: vary.profile?.height ?? 2.0, cadence: vary.profile?.cadence ?? 1, intensity: vary.profile?.intensity ?? 1, posture: vary.profile?.posture ?? 0, hand: vary.profile?.hand ?? 1};
  const K = {cad: (1 + vr(V.seed, 1, 0.05)) * PF.cadence, lean: vr(V.seed, 2, 0.035) * V.amp + 0.04 * PF.posture, drop: vr(V.seed, 3, 0.018) * V.amp + 0.025 * PF.posture, swing: (1 + vr(V.seed, 4, 0.1) * V.amp) * PF.intensity, width: vr(V.seed, 5, 0.018)};
  const segs = [...script];
  const of = <T extends Seg['k']>(k: T) => segs.filter((s) => s.k === k) as Extract<Seg, {k: T}>[];
  const shotSeg = of('jumpshot')[0];
  // ---------------------------------------------------------------- heading (path direction, or facing targets)
  let lastH = faceAngle(c, (segs.find((s) => s.k === 'stand') as {face?: Face} | undefined)?.face ?? 'rim', 0, 0);
  const rawHeading = (t: number): number => {
    const seg = segs.find((s) => (s.k === 'stand' || s.k === 'move') && t >= s.t0 - 1e-6 && t <= s.t1 + 1e-6) as Extract<Seg, {k: 'stand' | 'move'}> | undefined;
    const v = c.vel(t + 0.06); // anticipation: the body turns toward where the track goes 60 ms later
    const sp = Math.hypot(v[0], v[1]);
    const pathH = sp > 0.35 ? Math.atan2(v[1], v[0]) : lastH;
    if (seg?.k === 'move' && (seg.mode === 'shuffle' || seg.mode === 'backpedal')) return faceAngle(c, seg.face ?? 'rim', t, pathH);
    if (seg?.k === 'stand') return faceAngle(c, seg.face, t, lastH);
    return seg?.k === 'move' && seg.face && seg.face !== 'path' ? faceAngle(c, seg.face, t, pathH) : pathH;
  };
  const hs: Key[] = [];
  for (let t = 0; t <= c.dur + 1e-9; t += 0.05) {
    const h = rawHeading(t);
    const prev = hs.length ? hs[hs.length - 1][1] : h;
    const u = prev + wrap(h - prev);
    lastH = u;
    hs.push([Math.round(t * 1000) / 1000, u]);
  }
  // pivots override the heading (the body turns with the pivot foot)
  for (const pv of of('pivot')) {
    const h0 = hs.find((k) => k[0] >= pv.t0 - 1e-6)![1];
    for (const k of hs) if (k[0] >= pv.t0) k[1] = h0 + pv.dyaw * smooth((k[0] - pv.t0) / (pv.t1 - pv.t0)) + (k[0] > pv.t1 ? wrap(k[1] - (h0 + pv.dyaw)) * 0 : 0);
    // after the pivot the facing of the following stand segment takes over smoothly (rawHeading already faces it)
  }
  // turn-rate limit 6 rad/s, centred (mean of a forward and a backward rate-limited pass: the turn starts before and
  // ends after the raw switch). A raw facing switch turned the body 99 deg in 0.13 s (QC trio O2 0.73 s, head pop)
  {
    const W = 6 * 0.05;
    const fw = hs.map((k) => k[1]), bw = hs.map((k) => k[1]);
    for (let i = 1; i < fw.length; i++) fw[i] = fw[i - 1] + clamp(fw[i] - fw[i - 1], -W, W);
    for (let i = bw.length - 2; i >= 0; i--) bw[i] = bw[i + 1] + clamp(bw[i] - bw[i + 1], -W, W);
    hs.forEach((k, i) => (k[1] = (fw[i] + bw[i]) / 2));
  }
  // light smoothing (3-tap) so the heading has no corners
  const heading: Key[] = hs.map((k, i) => [k[0], i === 0 || i === hs.length - 1 ? k[1] : (hs[i - 1][1] + 2 * k[1] + hs[i + 1][1]) / 4] as Key);
  const hAt = (t: number) => {
    const i = Math.max(0, Math.min(heading.length - 1, Math.round(t / 0.05)));
    return heading[i][1];
  };
  // ---------------------------------------------------------------- footsteps
  const steps: Step[] = [];
  const forced = [...of('plant').map((p) => ({t: p.t, side: p.side, p})), ...of('step').map((s) => ({t: s.land, side: s.side, s}))].sort((a, b) => a.t - b.t);
  let lastSide: 0 | 1 = 1; // the first auto step is made with the left foot unless forced otherwise
  const lastLand: [number, number] = [-1, -1];
  const lastSpot: [[number, number] | null, [number, number] | null] = [null, null];
  const push = (st: Step) => {
    steps.push(st);
    lastLand[st.s] = st.land;
    lastSide = st.s;
    const r = c.root(st.land), v = c.vel(st.land), n = Math.hypot(v[0], v[1]);
    lastSpot[st.s] = n > 0.3 ? [r[0] + (v[0] / n) * st.f, r[1] + (v[1] / n) * st.f] : r;
  };
  // a planted foot leaves before the pelvis outruns it: the leg reaches ~0.5 m behind the hips at toe-off (QC: a
  // 0.69 m trailing foot at 2.75 s dragged the pelvis 19 cm down, then released it in 3 frames)
  const BEHIND = 0.5;
  const reachLift = (s: 0 | 1, prev: number, lift: number) => {
    const sp = lastSpot[s];
    if (prev < 0 || !sp) return lift;
    for (let t = prev + 0.1; t < lift; t += 0.005) {
      const r = c.root(t);
      if (Math.hypot(r[0] - sp[0], r[1] - sp[1]) > BEHIND) return t;
    }
    return lift;
  };
  for (const mv of of('move')) {
    const mode = mv.mode ?? 'run';
    // anchors inside this move: forced steps, and the end of the move
    const fz = forced.filter((f) => f.t > mv.t0 + 0.05 && f.t <= mv.t1 + 0.02);
    let ta = mv.t0;
    const marks = [...fz.map((f) => ({t: f.t, side: f.side as 0 | 1 | -1, f})), ...(fz.length && Math.abs(fz[fz.length - 1].t - mv.t1) < 0.03 ? [] : [{t: mv.t1, side: -1 as const, f: undefined}])];
    for (const mk of marks) {
      // integrate the cadence over [ta, mk.t]
      let ph = 0;
      for (let t = ta; t < mk.t; t += 0.01) ph += gait(c.speed(t)).cad * K.cad * 0.01;
      let n = Math.max(1, Math.round(ph));
      // side parity: the forced foot lands last
      const firstSide = (1 - lastSide) as 0 | 1;
      const sideOfLast = (n % 2 === 1 ? firstSide : lastSide) as 0 | 1;
      if (mk.side !== -1 && sideOfLast !== mk.side) n = n > 1 && ph < n ? n - 1 : n + 1;
      if (mk.side === -1 && c.speed(mk.t) < 0.3 && n > 1) {
        // a move that ends at rest finishes with both feet down (the last step closes the stance)
      }
      const nAuto = mk.side === -1 ? n : n - 1;
      // landings at equal cadence phase
      const landAt: number[] = [];
      let acc = 0, k = 1;
      for (let t = ta; t < mk.t && k <= nAuto; t += 0.005) {
        acc += gait(c.speed(t)).cad * K.cad * 0.005 * (n / Math.max(1e-6, ph));
        if (acc >= k) {
          landAt.push(t);
          k++;
        }
      }
      while (landAt.length < nAuto) landAt.push(mk.t - 0.02 * (nAuto - landAt.length));
      for (const tl of landAt) {
        const s = (1 - lastSide) as 0 | 1;
        const v = c.speed(tl);
        const g = gait(v);
        const T = 2 / (g.cad * K.cad);
        const prev = lastLand[s];
        let lift = prev < 0 ? Math.max(ta, tl - 0.3) : Math.max(prev + g.duty * T, tl - (1 - g.duty) * T);
        lift = Math.min(lift, tl - 0.12);
        lift = Math.max(tl - Math.max(0.38, (1 - g.duty) * T + 0.04), reachLift(s, prev, lift)); // never a floating swing
        if (prev >= 0) lift = Math.max(lift, prev + 0.08);
        const sg = s === 0 ? -1 : 1;
        const first = steps.length === 0 || tl - mv.t0 < 0.35;
        if (mode === 'shuffle') {
          push({s, lift, land: tl, f: 0.02, l: sg * (0.27 + K.width), h: 0.05, heel: 0, toeOff: 0.15});
        } else if (mode === 'backpedal') {
          push({s, lift, land: tl, f: -0.05, l: sg * (0.15 + K.width), h: 0.07, toeOff: 0.25});
        } else {
          const acc0 = (c.speed(tl + 0.05) - c.speed(tl - 0.05)) / 0.1;
          const brake = acc0 < -3.5;
          push({s, lift, land: tl, f: g.fwd + (brake ? 0.14 : 0) + (first ? -0.04 : 0), l: sg * (0.085 + 0.6 * K.width), h: g.h, heel: brake ? -0.2 : v > 3 ? 0.1 : 0.03, toeOff: v > 2 ? 0.55 : 0.4});
        }
      }
      if (mk.f && mk.side !== -1) {
        const f0 = mk.f as {p?: Extract<Seg, {k: 'plant'}>; s?: Extract<Seg, {k: 'step'}>};
        const s = mk.side as 0 | 1;
        const v = c.speed(mk.t - 0.1);
        const g = gait(Math.max(v, 1));
        const prev = lastLand[s];
        const T = 2 / (g.cad * K.cad);
        if (f0.p) {
          const sg = s === 0 ? -1 : 1;
          let lift = prev < 0 ? mk.t - 0.3 : Math.max(prev + g.duty * T, mk.t - 0.32);
          lift = Math.min(lift, mk.t - 0.14);
          lift = Math.max(prev + 0.08, mk.t - 0.4, reachLift(s, prev, lift));
          // braking plant: wide, ahead, turned into the cut, heel strike
          push({s, lift, land: mk.t, f: 0.36, l: sg * (f0.p.wide ?? 0.36), yaw: (f0.p.cut ?? 0) * 0.35, heel: -0.22, h: 0.11});
        } else if (f0.s) {
          const st = f0.s;
          push({s, lift: Math.max(prev + 0.08, st.land - 0.4, Math.min(st.lift, reachLift(s, prev, st.lift))), land: st.land, f: st.f, l: st.l, heel: st.heel, h: st.h, toeOff: st.toeOff, yaw: st.yaw});
        }
      }
      ta = mk.t;
    }
  }
  // explicit steps outside move segments
  for (const st of of('step')) if (!steps.some((x) => Math.abs(x.land - st.land) < 1e-6 && x.s === st.side)) push({s: st.side, lift: st.lift, land: st.land, f: st.f, l: st.l, heel: st.heel, h: st.h, toeOff: st.toeOff, yaw: st.yaw});
  // the jump shot: both feet leave at takeoff, land on the balls of the feet, slightly forward and wider
  let shot: Clip32['shot'];
  if (shotSeg) {
    const H = shotSeg.H ?? 0.46;
    const Tf = 2 * Math.sqrt((2 * H) / 9.81);
    const t0 = shotSeg.release + 0.035 - Tf / 2; // release 35 ms before the apex
    const t1 = t0 + Tf;
    // V3.3: catch-and-shoot timing adapts to the time the play gives after the catch (the dip IS the catch absorption
    // when the release comes < 1 s after the catch); the fixed 1.05 s gather of V3.2 started the shot before the catch
    const lastCatch = Math.max(-Infinity, ...of('catch').map((x) => x.t).filter((x) => x < shotSeg.release));
    const armT = Math.max(t0 - 1.05, Number.isFinite(lastCatch) ? lastCatch + 0.02 : -Infinity);
    // quick catch-and-shoot (catch < ~0.4 s before the takeoff): the legs start the dip DURING the 1-2 hop, before the
    // ball is in the hands (armT = when the hands own the shot); otherwise gather = armT as in V3.2
    const gatherT = shotSeg.quick ? Math.min(armT, t0 - PUSH33 - 0.24) : armT;
    const dipT = Math.max(t0 - 0.5, gatherT + 0.35 * (t0 - PUSH33 - gatherT));
    shot = {release: shotSeg.release, t0, t1, H, dipT, gatherT, recoverT: t1 + 0.55, armT, quick: !!shotSeg.quick};
    push({s: 1, lift: t0, land: t1, f: 0.08, l: 0.17 + K.width, heel: 0.3, air: true});
    push({s: 0, lift: t0, land: t1, f: 0.06, l: -0.17 - K.width, heel: 0.3, air: true});
  }
  steps.sort((a, b) => a.land - b.land || a.s - b.s);
  // sanity: per foot, lift after the previous landing of that foot
  for (const s of [0, 1] as const) {
    const fs = steps.filter((x) => x.s === s);
    for (let i = 1; i < fs.length; i++) if (fs[i].lift < fs[i - 1].land + 0.06) fs[i].lift = Math.min(fs[i].land - 0.1, fs[i - 1].land + 0.06);
  }
  // ---------------------------------------------------------------- stance width (wider in defense / triple threat)
  const stanceOf = (x: number): Stance | undefined => {
    const t = clamp(x, 0, c.dur);
    return (segs.find((s) => s.k === 'stand' && t >= s.t0 - 1e-6 && t <= s.t1 + 1e-6) as {pose?: Stance} | undefined)?.pose;
  };
  // stance changes (ready -> defense, ...) are low-passed over +-0.24 s: a step in the pelvis drop popped the hips
  // (QC 11.10 s: 16 cm in 2 frames)
  const lowpass = (f: (t: number) => number) => (t: number) => {
    let a = 0, w = 0;
    for (let k = -4; k <= 4; k++) {
      const q = Math.exp(-((k / 2.5) ** 2));
      a += q * f(t + k * 0.06);
      w += q;
    }
    return a / w;
  };
  const widthOf = (t: number) => {
    const p = stanceOf(t);
    return p === 'defense' ? 0.14 : p === 'screen' ? 0.15 : p === 'closeout' ? 0.08 : p === 'triple' ? 0.06 : p === 'ready' ? 0.04 : 0;
  };
  const stanceW = keysOf((t) => (widthOf(t - 0.15) + widthOf(t) + widthOf(t + 0.15)) / 3, 0, c.dur, 0.1);
  // ---------------------------------------------------------------- trunk / pelvis channels from the track and segments
  const accAt = (t: number) => (c.speed(t + 0.08) - c.speed(t - 0.08)) / 0.16;
  const plants = of('plant');
  const catches = of('catch');
  const leanF = (t: number) => {
    const v = c.speed(t);
    // acceleration leans forward, braking counter-leans (the trunk resists the deceleration), both low-passed
    let a = 0;
    for (const d of [-0.1, -0.05, 0, 0.05, 0.1]) a += accAt(t + d) / 5;
    let L = 0.1 + 0.035 * Math.min(v, 6) + 0.05 * clamp(a, -6, 6);
    const p = stanceOf(t);
    if (p === 'defense') L = 0.34;
    else if (p === 'screen') L = 0.14;
    else if (p === 'triple') L = 0.26;
    else if (p === 'ready') L = 0.2;
    else if (p === 'closeout') L = 0.12;
    // V3.3: same counter-lean / drive, spread over +-0.13 s (the head popped 60-115 m/s^2 on every plant in V3.2)
    for (const pl of plants) L -= 0.2 * Math.exp(-(((t - pl.t + 0.02) / 0.13) ** 2)); // counter-lean on the plant
    for (const pl of plants) L += 0.16 * Math.exp(-(((t - pl.t - 0.24) / 0.13) ** 2)); // explosive first step after it
    for (const ct of catches) L += 0.08 * Math.exp(-(((t - ct.t - 0.15) / 0.15) ** 2)); // the catch loads forward
    return clamp(L + K.lean, -0.3, 0.6);
  };
  const dropF = (t: number) => {
    const v = c.speed(t);
    const p = stanceOf(t);
    let d = p === 'defense' ? 0.22 : p === 'screen' ? 0.15 : p === 'triple' ? 0.15 : p === 'ready' ? 0.1 : p === 'closeout' ? 0.12 : p === 'relaxed' ? 0.02 : 0.05 + 0.012 * Math.min(v, 6);
    for (const pl of plants) d += 0.1 * Math.exp(-(((t - pl.t - 0.03) / 0.12) ** 2)); // centre of mass drops on the plant
    for (const ct of catches) d += 0.05 * Math.exp(-(((t - ct.t - 0.12) / 0.13) ** 2)); // elbows and knees absorb the catch
    return Math.max(0, d + K.drop);
  };
  // shoulders lead turns / cuts: the chest offset anticipates the heading change by ~0.15 s
  const chestF = (t: number) => {
    const ahead = wrap(hAt(t + 0.18) - hAt(t));
    let ch = clamp(0.8 * ahead, -0.5, 0.5);
    for (const pl of plants) if (pl.cut) ch += 0.45 * Math.sign(pl.cut) * Math.exp(-(((t - pl.t + 0.05) / 0.14) ** 2));
    return ch;
  };
  const rollF = (t: number) => {
    let r = 0;
    for (const pl of plants) if (pl.cut) r += 0.24 * Math.sign(pl.cut) * Math.exp(-(((t - pl.t - 0.12) / 0.18) ** 2)); // bank into the cut
    // banking in curved running: lean into the turn (v^2 / R ~ v * dheading/dt)
    const v = c.speed(t);
    const om = wrap(hAt(t + 0.05) - hAt(t - 0.05)) / 0.1;
    return clamp(r + 0.05 * v * om, -0.35, 0.35);
  };
  const pelvisRollF = (t: number) => {
    let r = 0;
    for (const pl of plants) r += -0.1 * (pl.side === 1 ? 1 : -1) * Math.exp(-(((t - pl.t - 0.05) / 0.12) ** 2));
    return r;
  };
  // the jump shot owns lean / drop during its cycle (motion32 shotPhase); keep the keys neutral there
  const inShot = (t: number) => !!shot && t > shot.gatherT && t < shot.recoverT;
  const lean = keysOf(lowpass((t) => (inShot(t) ? 0.12 : leanF(t))), 0, c.dur);
  const drop = keysOf(lowpass((t) => (inShot(t) ? 0.1 : dropF(t))), 0, c.dur);
  const chest = keysOf((t) => (inShot(t) ? 0.12 : chestF(t)), 0, c.dur);
  const roll = keysOf(rollF, 0, c.dur);
  const pelvisRoll = keysOf(pelvisRollF, 0, c.dur);
  // ---------------------------------------------------------------- arms
  const jt = (k: number) => vr(V.seed, 50 + k, 0.025) * V.timing; // small timing variation of free arm changes
  const arms: ArmKey32[] = [];
  const timeline: {t: number; m: ArmKey32['m']; b: number}[] = [];
  for (const s of segs) {
    if (s.k === 'stand') timeline.push({t: s.t0, m: s.pose === 'defense' ? 'defense' : s.pose === 'screen' ? 'screen' : s.pose === 'triple' ? 'triple' : s.pose === 'closeout' ? 'closeout' : s.pose === 'relaxed' ? 'relaxed' : 'ready', b: 0.35});
    if (s.k === 'move') timeline.push({t: s.t0 + jt(timeline.length), m: s.mode === 'shuffle' ? 'defense' : s.mode === 'closeout' ? 'closeout' : 'run', b: 0.25});
    if (s.k === 'plant') timeline.push({t: s.t - 0.3, m: 'brake', b: 0.18}, {t: s.t + 0.14, m: 'run', b: 0.22});
    if (s.k === 'catch' && s.style === 'handoff') timeline.push({t: s.t - 0.42, m: 'take', b: 0.3}, {t: s.t, m: 'give', b: 0}, {t: s.t + 0.3, m: 'pocket', b: 0.2});
    else if (s.k === 'catch') timeline.push({t: s.t - 0.45, m: 'reach', b: 0.3}, {t: s.t, m: 'give', b: 0}, {t: s.t + 0.42, m: 'pocket', b: 0.2});
    if (s.k === 'dribbleRun') timeline.push({t: s.t0, m: 'dribble', b: s.t0 < 0.05 ? 0 : 0.2}, {t: s.t1, m: 'gather', b: 0.22});
    // V3.3: the gather after a bounce blends over 0.25 s (0.08 s in V3.2 = the 994 m/s^2 wrist pop at the pick-up)
    // and the dribble mode owns the ball 0.18 s BEFORE the push (V3.2 switched jab -> dribble AT the push, while the
    // ball already falls: 900 m/s^2 wrist pop at 6.10 s in V3.3's first pass)
    if (s.k === 'dribble') timeline.push({t: s.push - 0.32, m: 'jab', b: 0.12}, {t: s.push - 0.18, m: 'dribble', b: 0.16}, {t: s.catch + 0.06, m: 'gather', b: 0.25});
    if (s.k === 'pass' && s.style === 'handoff') timeline.push({t: Math.max(s.t - 0.36, Math.max(-1, ...segs.filter((d): d is Extract<Seg, {k: 'dribbleRun'}> => d.k === 'dribbleRun' && d.t1 <= s.t).map((d) => d.t1)) + 0.1), m: 'handoff', b: 0.26}, {t: (s.t1 ?? s.t + 0.2) + 0.32, m: 'screen', b: 0.35});
    else if (s.k === 'pass') timeline.push({t: s.t - 0.3, m: 'pocket', b: 0.15}, {t: s.t - 0.14, m: 'pass', b: 0.1}, {t: s.t + 0.45, m: 'ready', b: 0.4});
    if (s.k === 'jumpshot' && shot) timeline.push({t: shot.armT ?? shot.gatherT, m: 'jumpshot', b: 0.2}, {t: shot.recoverT, m: 'ready', b: 0.45});
  }
  timeline.sort((a, b) => a.t - b.t);
  // ball windows own the arms: between the catch (or the start, for a player who has the ball) and the release only
  // ball modes are taken, and inside the jump-shot cycle only the jump shot (a stand 'ready' key at 7.4 s took the
  // ball out of the hands mid-shot: QC palm gap 0.8 m at the release)
  // V3.3: every possession window (catch -> release, or start -> release); inside a window only ball modes are taken
  const BALL = ['reach', 'take', 'give', 'pocket', 'triple', 'jab', 'dribble', 'gather', 'jumpshot', 'pass', 'handoff'];
  const wins = windowsOf(segs, shot);
  for (const k of timeline) {
    if (shot && k.t > (shot.armT ?? shot.gatherT) + 1e-6 && k.t < shot.recoverT - 1e-6) continue;
    if (wins.some((w) => k.t > w.a - (w.start === 'catch' ? 0.45 : w.start === 'handoff' ? 0.42 : 0) + 1e-6 && k.t < w.b - 1e-6) && !BALL.includes(k.m as string)) continue;
    arms.push({t: Math.max(0, k.t), m: k.m, b: k.b});
  }
  // a player holding the ball at t = 0 starts in a ball mode (triple threat / dribble), not 'ready'
  if (wins.some((w) => w.start === 'start') && arms.length && !BALL.includes(arms[0].m as string)) arms[0] = {...arms[0], m: of('dribbleRun').some((d) => d.t0 < 0.05) ? 'dribble' : 'triple'};
  // ---------------------------------------------------------------- look
  const look: Clip31['look'] = [{t: 0, at: 'path'}];
  for (const s of segs) {
    if (s.k === 'stand') look.push({t: s.t0, at: typeof s.face === 'string' && s.face !== 'path' ? s.face : 'path', b: 0.3});
    if (s.k === 'move') look.push({t: s.t0, at: s.mode === 'shuffle' || s.mode === 'backpedal' || s.mode === 'closeout' ? (typeof s.face === 'string' ? s.face : 'rim') : 'path', b: 0.3});
    if (s.k === 'plant' && s.cut) look.push({t: s.t - 0.25, at: 'ahead', b: 0.2});
    if (s.k === 'catch') look.push({t: s.t - 1.2, at: s.from ?? 'ball', b: 0.3}, {t: s.t - 0.35, at: 'ball', b: 0.2}, {t: s.t + 0.25, at: 'rim', b: 0.4});
    if (s.k === 'pass') look.push({t: s.t - 0.6, at: s.to, b: 0.25});
    if (s.k === 'jumpshot' && shot) look.push({t: shot.armT ?? shot.gatherT, at: 'rim', b: 0.25}, {t: shot.release + 0.1, at: 'ball', b: 0.3}, {t: shot.t1 + 0.4, at: 'rim', b: 0.4});
  }
  look.sort((a, b) => a.t - b.t);
  // ---------------------------------------------------------------- ball
  const dr = of('dribble')[0];
  const ct = catches[0];
  const ps = of('pass')[0];
  const passes = of('pass').map((p) => ({t: p.t, to: p.to, style: p.style ?? 'chest', t1: p.t1}));
  const ball: Clip31['ball'] = {
    catchT: ct?.t,
    releaseT: shot?.release ?? ps?.t,
    dribble: dr ? {push: dr.push, floor: dr.floor, catch: dr.catch} : undefined,
  };
  return {
    label, heading, chest, lean, roll, pelvisRoll, drop,
    init: [{f: 0.04, l: -0.17 - 0.5 * K.width}, {f: -0.08, l: 0.19 + 0.5 * K.width}],
    steps, pivots: of('pivot').map((p) => ({s: p.side, t0: p.t0, t1: p.t1, dyaw: p.dyaw})),
    jump: shot ? {t0: shot.t0, t1: shot.t1, H: shot.H} : undefined,
    look, arms, ball, shot, pass: ps ? {t: ps.t, to: ps.to} : undefined,
    stanceW, vary: {...V, profile: PF, k: K}, script, facing: heading,
    windows: wins, passes,
    // single bounces of a script ('dribble' push / floor / catch) run on the SAME live-dribble model with their exact times
    dribbles: [...of('dribbleRun').map((d) => ({t0: d.t0, t1: d.t1, hand: d.hand ?? 1, floors: d.floors})),
      ...of('dribble').map((d) => ({t0: d.push - 0.18, t1: d.catch + 0.3, hand: 1 as const, floors: [d.floor], push: [d.push], catch: [d.catch]}))].sort((a, b) => a.t0 - b.t0),
    catches: catches.map((x) => ({t: x.t, from: x.from, style: x.style ?? 'chest'})),
    stances: of('stand').map((x) => ({t0: x.t0, t1: x.t1, pose: x.pose})), profile: PF,
  };
};

export type {V3};
