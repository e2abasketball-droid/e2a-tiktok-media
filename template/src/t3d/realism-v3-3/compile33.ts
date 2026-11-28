// E2A Realism V3.3 (2026-11-22) — MotionCompiler: a full-court play (tracks, ball events, actions, marks, roles) ->
// one script of library primitives per player (library33.ts Seg[]), so 10 players move with the parametric library
// WITHOUT per-player hand keys. Pure and deterministic (same play -> same scripts).
//   locomotion   moving / standing intervals from the TRACK speed (hysteresis), sharp direction changes -> 'plant' with
//                the outside foot (cut angle from the track), defenders: shuffle / backpedal / run chosen from the angle
//                between their travel and the man (or ball) they face
//   stances      offence: triple threat while holding, 'screen' inside screen actions, ready otherwise, relaxed after
//                the basket; defence: defensive stance on the man they guard, closeout / contest windows, relaxed after
//   ball         hold+dribble -> 'dribbleRun' (bounce schedule from the handler's speed, ends in the hand), pass ->
//                'pass' (passer) + 'catch' (receiver, style kept), hand-off, shot -> 'jumpshot' (jump height from the
//                time between the catch and the release)
//   report       every player gets a role summary and the list of play events it could NOT express (fallbacks)
import type {Play, BallEvent} from '../../tactical/play.ts';
import {posAt} from '../../tactical/play.ts';
import type {Profile, Seg, Stance, Face} from './library33.ts';

type Act = {type: string; from: number; to: number; face?: string | number};
export type Compiled33 = {script: Seg[]; profile: Profile; role: string; unsupported: string[]; summary: string[]};

const clamp = (x: number, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const wrap = (a: number) => Math.atan2(Math.sin(a), Math.cos(a));
const r3 = (x: number) => Math.round(x * 1000) / 1000;

const cache = new Map<string, Record<string, Compiled33>>();
export const compilePlay33 = (play: Play): Record<string, Compiled33> => {
  const hit = cache.get(play.id);
  if (hit) return hit;
  const out: Record<string, Compiled33> = {};
  for (const p of play.players) out[p.id] = compilePlayer(play, p.id);
  cache.set(play.id, out);
  return out;
};

const compilePlayer = (play: Play, id: string): Compiled33 => {
  const P = play.players.find((q) => q.id === id)!;
  const def = P.team === 'X';
  const dur = play.duration;
  const tr = play.tracks[id];
  const acts = ((play as Play & {actions?: Record<string, Act[]>}).actions?.[id] ?? []) as Act[];
  const marks = (play.marks ?? {}) as Record<string, number>;
  const tEnd = marks.make !== undefined ? marks.make + 0.5 : Infinity; // the possession is over: bodies relax
  const unsupported: string[] = [];
  const summary: string[] = [];
  const pos = (t: number): [number, number] => {
    const q = posAt(tr, clamp(t, 0, dur));
    return [q[0], q[1]];
  };
  const vel = (t: number): [number, number] => {
    const a = pos(t - 0.04), b = pos(t + 0.04);
    return [(b[0] - a[0]) / 0.08, (b[1] - a[1]) / 0.08];
  };
  const speed = (t: number) => Math.hypot(...vel(t));
  // ---------------------------------------------------------------- faces from the actions
  const guards = (P as {guards?: string}).guards;
  const faceAt = (t: number): Face => {
    const a = [...acts].reverse().find((x) => x.face !== undefined && t >= x.from - 1e-6 && t <= x.to + 1e-6);
    if (a) return a.face as Face;
    return def ? guards ?? 'ball' : 'ball';
  };
  const actAt = (t: number, type: string) => acts.some((x) => x.type === type && t >= x.from - 1e-6 && t <= x.to + 1e-6);
  // ---------------------------------------------------------------- ball events of this player
  const ev = play.ball as BallEvent[];
  const holds = ev.filter((e): e is Extract<BallEvent, {type: 'hold'}> => e.type === 'hold' && e.player === id);
  const passesOut = ev.filter((e): e is Extract<BallEvent, {type: 'pass'}> => e.type === 'pass' && e.from === id);
  const passesIn = ev.filter((e): e is Extract<BallEvent, {type: 'pass'}> => e.type === 'pass' && e.to === id);
  const shots = ev.filter((e): e is Extract<BallEvent, {type: 'shot'}> => e.type === 'shot' && e.player === id);
  const layups = ev.filter((e): e is Extract<BallEvent, {type: 'layup'}> => e.type === 'layup' && e.player === id);
  if (!(play as Play & {v4?: boolean}).v4) for (const l of layups) unsupported.push(`layup ${r3(l.t0)} s (no layup primitive yet: jump shot used)`);
  const holding = (t: number) => holds.some((h) => t >= h.from && t < h.to && !h.dribble);
  const dribbling = (t: number) => holds.some((h) => t >= h.from && t < h.to && !!h.dribble);
  // ---------------------------------------------------------------- moving / standing intervals
  const DT = 0.02;
  const mv: boolean[] = [];
  let on = false;
  // opt-in (2026-11-24, 4 Rules reel): intervals where the body centre glides over planted feet (a pivot, a jab) stay
  // 'stand' whatever the track speed; the feet move only through explicit v33extra steps / pivots
  const still = ((play as Play & {v33still?: Record<string, [number, number][]>}).v33still ?? {})[id] ?? [];
  for (let t = 0; t <= dur + 1e-9; t += DT) {
    const v = speed(t);
    on = on ? v > 0.1 : v > 0.18;
    if (still.some(([a, b]) => t >= a - 1e-6 && t <= b + 1e-6)) on = false;
    mv.push(on);
  }
  type Iv = {a: number; b: number; moving: boolean};
  let ivs: Iv[] = [];
  for (let i = 0; i < mv.length; i++) {
    const t = i * DT;
    if (!ivs.length || ivs[ivs.length - 1].moving !== mv[i]) ivs.push({a: t, b: t, moving: mv[i]});
    ivs[ivs.length - 1].b = Math.min(dur, t + DT);
  }
  // a stand shorter than 0.3 s between two moves is part of the move (the feet keep stepping); a move shorter than
  // 0.2 s stays a move (every metre of the track must be stepped, never slid)
  for (let changed = true; changed; ) {
    changed = false;
    for (let i = 1; i + 1 < ivs.length; i++) {
      if (!ivs[i].moving && ivs[i].b - ivs[i].a < 0.3 && ivs[i - 1].moving && ivs[i + 1].moving) {
        ivs[i - 1].b = ivs[i + 1].b;
        ivs.splice(i, 2);
        changed = true;
        break;
      }
    }
  }
  ivs = ivs.filter((x) => x.b - x.a > 1e-6);
  ivs[0].a = 0;
  ivs[ivs.length - 1].b = dur;
  // ---------------------------------------------------------------- stances (standing intervals)
  // E2A Motion Engine V4 (2026-11-28) opt-in: play.v4 = true -> running layups (no jump shot), trap / help stances
  const V4 = !!(play as Play & {v4?: boolean}).v4;
  const stanceAt = (t: number): Stance => {
    if (t > tEnd) return 'relaxed';
    if (V4 && def && actAt(t, 'trap')) return 'trap';
    if (V4 && def && actAt(t, 'help')) return 'help';
    if (def) return actAt(t, 'closeout') || actAt(t, 'contest') ? 'closeout' : 'defense';
    if (holding(t)) return 'triple';
    if (actAt(t, 'screen')) return 'screen';
    return 'ready';
  };
  const script: Seg[] = [];
  const pushStands = (a: number, b: number) => {
    // split where the stance or the facing changes (sampled every 0.05 s, min 0.25 s per piece)
    let t0 = a;
    let cur = {pose: stanceAt(a + 1e-3), face: faceAt(a + 1e-3)};
    for (let t = a + 0.05; t < b - 1e-6; t += 0.05) {
      const nx = {pose: stanceAt(t), face: faceAt(t)};
      if ((nx.pose !== cur.pose || nx.face !== cur.face) && t - t0 >= 0.25 && b - t >= 0.2) {
        script.push({k: 'stand', t0: r3(t0), t1: r3(t), pose: cur.pose, face: cur.face});
        t0 = t;
        cur = nx;
      }
    }
    script.push({k: 'stand', t0: r3(t0), t1: r3(b), pose: cur.pose, face: cur.face});
  };
  // ---------------------------------------------------------------- moves (+ defender footwork + plants)
  const modeAt = (t: number): 'run' | 'shuffle' | 'backpedal' => {
    if (!def) return 'run';
    const v = vel(t);
    const sp = Math.hypot(v[0], v[1]);
    // a defender shuffles only at shuffle speeds (<= 1.8 m/s) and backpedals only up to 2.6 m/s; faster he turns and
    // runs (first 5v5 compile: X4 shuffled 7 m at 2.8 m/s, long flight phases, pelvis pops 150-350 m/s^2)
    if (sp > 2.6) return 'run';
    const f = faceAt(t);
    let tgt: [number, number] | null = null;
    if (typeof f === 'string' && play.tracks[f]) {
      const q = posAt(play.tracks[f], clamp(t, 0, dur));
      tgt = [q[0], q[1]];
    } else if (f === 'ball') {
      const h = ev.find((e): e is Extract<BallEvent, {type: 'hold'}> => e.type === 'hold' && t >= e.from && t < e.to);
      if (h && play.tracks[h.player]) {
        const q = posAt(play.tracks[h.player], clamp(t, 0, dur));
        tgt = [q[0], q[1]];
      }
    }
    if (!tgt) return 'run';
    const r = pos(t);
    const fa = Math.atan2(tgt[1] - r[1], tgt[0] - r[0]);
    const a = Math.abs(wrap(Math.atan2(v[1], v[0]) - fa));
    if (a > 0.96 && a < 2.18) return sp <= 1.8 ? 'shuffle' : 'run';
    if (a >= 2.18 && sp < 3.0) return 'backpedal';
    return 'run';
  };
  const pushMove = (a: number, b: number) => {
    // footwork modes, majority over 0.05 s samples, pieces >= 0.6 s (a shuffle-run-shuffle switch every 0.4 s re-planted the feet and dropped the pelvis 16 cm)
    const samples: {t: number; m: ReturnType<typeof modeAt>}[] = [];
    for (let t = a; t < b - 1e-6; t += 0.05) samples.push({t, m: modeAt(t + 0.025)});
    const pieces: {a: number; b: number; m: ReturnType<typeof modeAt>}[] = [];
    for (const s of samples) {
      if (!pieces.length || pieces[pieces.length - 1].m !== s.m) pieces.push({a: s.t, b: s.t + 0.05, m: s.m});
      else pieces[pieces.length - 1].b = s.t + 0.05;
    }
    for (let changed = true; changed; ) {
      changed = false;
      for (let i = 0; i < pieces.length; i++) {
        if (pieces.length > 1 && pieces[i].b - pieces[i].a < 0.6) {
          const j = i === 0 ? 1 : i - 1;
          pieces[j].a = Math.min(pieces[j].a, pieces[i].a);
          pieces[j].b = Math.max(pieces[j].b, pieces[i].b);
          pieces.splice(i, 1);
          changed = true;
          break;
        }
      }
    }
    pieces[0].a = a;
    pieces[pieces.length - 1].b = b;
    for (let i = 1; i < pieces.length; i++) pieces[i].a = pieces[i - 1].b;
    // V4: the 0.6 s merge could swallow a fast run into a shuffle (X4 iq02 shuffled at 2.5 m/s: legs at full
    // reach, pelvis dropped 0.2 m, 246 m/s^2 pop). A shuffle piece whose peak speed exceeds 2.1 m/s is run instead.
    if (V4 && def) for (const pc of pieces) {
      if (pc.m !== 'shuffle') continue;
      let vmax = 0;
      for (let t = pc.a; t <= pc.b; t += 0.025) { const v = vel(t); vmax = Math.max(vmax, Math.hypot(v[0], v[1])); }
      if (vmax > 2.1) pc.m = 'run';
    }
    // V4: a shuffle / backpedal piece is split where a trap or help window starts or ends (the arms change, the feet
    // keep the same footwork), so the trap arms cover exactly the trap
    if (V4 && def) {
      const cuts = acts.filter((x) => x.type === 'trap' || x.type === 'help').flatMap((x) => [x.from, x.to]);
      for (const ct of cuts) {
        const i = pieces.findIndex((pc) => pc.m !== 'run' && ct > pc.a + 0.15 && ct < pc.b - 0.15);
        if (i >= 0) pieces.splice(i, 1, {a: pieces[i].a, b: ct, m: pieces[i].m}, {a: ct, b: pieces[i].b, m: pieces[i].m});
      }
    }
    for (const pc of pieces) {
      const f = faceAt((pc.a + pc.b) / 2);
      const mid = (pc.a + pc.b) / 2;
      const armsV4 = V4 && def && pc.m !== 'run' ? (actAt(mid, 'trap') ? 'trap' as const : actAt(mid, 'help') ? 'wall' as const : undefined) : undefined;
      script.push({k: 'move', t0: r3(pc.a), t1: r3(pc.b), mode: pc.m, face: pc.m === 'run' ? 'path' : f, ...(armsV4 ? {arms: armsV4} : {})});
      if (pc.m !== 'run') summary.push(`${pc.m} ${r3(pc.a)}-${r3(pc.b)} s`);
    }
    // plants: sharp heading changes at speed inside run pieces (outside foot, cut = signed turn)
    let lastPlant = -9;
    for (let t = a + 0.35; t < b - 0.3; t += 0.02) {
      if (modeAt(t) !== 'run') continue;
      const v0 = vel(t - 0.16), v1 = vel(t + 0.16);
      const s0 = Math.hypot(...v0), s1 = Math.hypot(...v1);
      if (s0 < 1.3 || s1 < 1.3) continue;
      const d = wrap(Math.atan2(v1[1], v1[0]) - Math.atan2(v0[1], v0[0]));
      if (Math.abs(d) < 0.85 || t - lastPlant < 0.6) continue;
      // local maximum of the turn
      const dPrev = wrap(Math.atan2(vel(t + 0.14)[1], vel(t + 0.14)[0]) - Math.atan2(vel(t - 0.18)[1], vel(t - 0.18)[0]));
      const dNext = wrap(Math.atan2(vel(t + 0.18)[1], vel(t + 0.18)[0]) - Math.atan2(vel(t - 0.14)[1], vel(t - 0.14)[0]));
      if (Math.abs(dNext) > Math.abs(d) + 1e-3 && Math.abs(dNext) >= Math.abs(dPrev)) continue;
      script.push({k: 'plant', t: r3(t), side: d > 0 ? 1 : 0, cut: r3(clamp(d, -1.6, 1.6))});
      summary.push(`plant ${d > 0 ? 'R' : 'L'} ${r3(t)} s cut ${r3(d)} rad`);
      lastPlant = t;
    }
  };
  // shot off the move (catch-and-shoot coming out of a cut / curl): the run ends in a 1-2 stop just before the takeoff,
  // the feet are planted when the jump starts (V3.3 first 5v5 compile: the run's auto steps overlapped the jump's air
  // steps, the pelvis jumped 3.5 km/s^2 at O2 6.33 s)
  const takeoffs = [...shots, ...layups].map((s) => {
    const lastCatch = Math.max(-Infinity, ...passesIn.map((p) => p.t1).filter((x) => x < s.t0));
    // opt-in event H (free throw hop, Zero Cut V2 layup take-off): the take-off matches the jump the primitive plays
    const Hx = (s as {H?: number}).H;
    const H = Hx ?? (Number.isFinite(lastCatch) && s.t0 - lastCatch < 0.7 ? 0.22 : 0.44);
    return s.t0 + 0.035 - Math.sqrt((2 * H) / 9.81);
  });
  const oneTwo: Seg[] = [];
  // V4: a running layup keeps moving into the take-off: legal 1-2 gather steps INSIDE the run (step 1 = the knee-drive
  // foot, step 2 = the take-off foot, which pushes for 0.17 s), the run ends at the take-off, the body lands and stands
  const v4Lay = V4 ? layups.map((l) => {
    const H = (l as {H?: number}).H ?? 0.42;
    const tk = l.t0 + 0.035 - Math.sqrt((2 * H) / 9.81);
    return {l, H, tk, hand: ((l as {hand?: number}).hand ?? 1) as 1 | -1};
  }) : [];
  for (const v of v4Lay) {
    const i = ivs.findIndex((x) => x.moving && x.a < v.tk - 0.45 && x.b > v.tk - 0.05);
    if (i >= 0) {
      const after = ivs[i].b;
      ivs[i].b = v.tk;
      if (ivs[i + 1] && !ivs[i + 1].moving) ivs[i + 1].a = v.tk;
      else if (after > v.tk + 1e-6) ivs.splice(i + 1, 0, {a: v.tk, b: after, moving: false});
    }
    const tkF = (v.hand === 1 ? 0 : 1) as 0 | 1, kdF = (1 - tkF) as 0 | 1;
    const sg = (sd: 0 | 1) => (sd === 0 ? -1 : 1);
    oneTwo.push({k: 'step', side: kdF, lift: r3(v.tk - 0.62), land: r3(v.tk - 0.4), f: 0.26, l: sg(kdF) * 0.1, heel: -0.12, h: 0.12},
      {k: 'step', side: tkF, lift: r3(v.tk - 0.38), land: r3(v.tk - 0.17), f: 0.3, l: sg(tkF) * 0.11, heel: -0.18, h: 0.1});
    summary.push(`layup gather: step ${kdF ? 'R' : 'L'} ${r3(v.tk - 0.4)} s, step ${tkF ? 'R' : 'L'} ${r3(v.tk - 0.17)} s, take-off ${r3(v.tk)} s, ${v.hand === 1 ? 'right' : 'left'} hand`);
  }
  for (const tk of V4 ? takeoffs.slice(0, shots.length) : takeoffs) {
    const stop = tk - 0.06;
    const i = ivs.findIndex((x) => x.moving && x.a < stop - 0.3 && x.b > stop);
    if (i < 0) continue;
    const after = ivs[i].b;
    ivs[i].b = stop;
    if (ivs[i + 1] && !ivs[i + 1].moving) ivs[i + 1].a = stop;
    else ivs.splice(i + 1, 0, {a: stop, b: after, moving: false});
    const lead = (hand: number) => (hand === 1 ? 0 : 1) as 0 | 1; // right-handed shooter: left foot first ("1"), right foot "2"
    const h = shots.length ? 1 : 1;
    oneTwo.push({k: 'step', side: lead(h), lift: r3(tk - 0.42), land: r3(tk - 0.24), f: 0.2, l: -0.1, heel: -0.16, h: 0.08},
      {k: 'step', side: (1 - lead(h)) as 0 | 1, lift: r3(tk - 0.25), land: r3(tk - 0.08), f: 0.12, l: 0.16, heel: -0.08, h: 0.07});
    summary.push(`1-2 stop into the shot: steps ${r3(tk - 0.24)} / ${r3(tk - 0.08)} s, takeoff ${r3(tk)} s`);
  }
  for (const iv of ivs) (iv.moving ? pushMove : pushStands)(iv.a, iv.b);
  script.push(...oneTwo);
  // ---------------------------------------------------------------- ball primitives
  for (const h of holds.filter((x) => x.dribble)) {
    // bounce schedule: rate 1.75-2.35 bounces / s from the handler's speed (the engine's live dribble cadence), the
    // last floor contact leaves the ball time to rise into the hand before the pick-up
    const t0 = h.from, t1 = h.to;
    const start = t0 < 0.05 ? 0.12 : t0 + 0.15;
    const endF = t1 - 0.22;
    const rate = (t: number) => 1.75 + 0.6 * Math.min(1, speed(t) / 5);
    let ph = 0;
    for (let t = start; t < endF; t += 0.01) ph += rate(t) * 0.01;
    const n = Math.max(1, Math.round(ph));
    const floors: number[] = [];
    let acc = 0, k = 0;
    for (let t = start; t < endF && floors.length < n; t += 0.005) {
      acc += rate(t) * 0.005 * (n / Math.max(1e-6, ph));
      if (acc >= k + 0.5) {
        floors.push(r3(t));
        k++;
      }
    }
    script.push({k: 'dribbleRun', t0: r3(t0), t1: r3(t1), hand: (h.hand ?? 1) as 1 | -1, floors});
    summary.push(`dribble ${r3(t0)}-${r3(t1)} s, ${floors.length} bounces`);
  }
  for (const p of passesOut) {
    script.push({k: 'pass', t: r3(p.t0), to: p.to, style: p.style ?? 'chest', t1: r3(p.t1)});
    summary.push(`${p.style ?? 'chest'} pass to ${p.to} ${r3(p.t0)} s`);
  }
  for (const p of passesIn) {
    script.push({k: 'catch', t: r3(p.t1), from: p.from, style: p.style ?? 'chest'});
    summary.push(`catch from ${p.from} ${r3(p.t1)} s`);
  }
  for (const v of v4Lay) script.push({k: 'layup', release: r3(v.l.t0), H: v.H, hand: v.hand});
  for (const s of [...shots, ...(V4 ? [] : layups)]) {
    const lastCatch = Math.max(-Infinity, ...passesIn.map((p) => p.t1).filter((x) => x < s.t0));
    const quick = Number.isFinite(lastCatch) && s.t0 - lastCatch < 0.7;
    // opt-in (2026-11-24, 4 Rules reel): a shot event may carry its own jump height H (free throw = a small hop)
    const Hx = (s as {H?: number}).H;
    script.push({k: 'jumpshot', release: r3(s.t0), H: Hx ?? (quick ? 0.22 : 0.44), quick: Hx !== undefined ? Hx < 0.3 : quick});
    summary.push(`jump shot release ${r3(s.t0)} s${quick ? ' (quick catch-and-shoot, low jump)' : ''}`);
  }
  // ---------------------------------------------------------------- profile (deterministic per role / id)
  const num = Number(id.slice(1)) || 1;
  const big = !def ? num >= 4 : (() => {
    const g = guards ? Number(guards.slice(1)) : num;
    return g >= 4;
  })();
  const onBall = holds.length > 0 || passesIn.length > 0;
  const profile: Profile = {
    cadence: big ? 0.94 : 1.04,
    intensity: onBall ? 1.08 : def ? 1.0 : 0.88,
    posture: def ? 0.4 : big ? 0.15 : 0,
    hand: (holds.find((h) => h.hand)?.hand ?? 1) as 1 | -1,
  };
  // opt-in per play (HORNS 2026-11-23): two branches of one action need the SAME body profile before the fork, even
  // when only one branch gives the player the ball (the profile otherwise depends on post-fork events)
  Object.assign(profile, ((play as Play & {v33profile?: Record<string, Partial<Profile>>}).v33profile ?? {})[id] ?? {});
  const role = (P as {role?: string}).role ?? (def ? 'defender' : 'attacker');
  // opt-in per play (2026-11-24, 4 Rules reel): explicit footwork primitives added to the compiled script (a pivot,
  // a lifted pivot foot that comes back down = travelling) — plays without the key compile exactly as before
  const extra = ((play as Play & {v33extra?: Record<string, Seg[]>}).v33extra ?? {})[id];
  if (extra?.length) {
    script.push(...extra.map((x) => ({...x})));
    summary.push(`${extra.length} explicit primitives (v33extra)`);
  }
  script.sort((a, b) => tOf(a) - tOf(b));
  return {script, profile, role, unsupported, summary};
};
const tOf = (s: Seg) => ('t0' in s ? s.t0 : 't' in s ? s.t : 'release' in s ? s.release : 'land' in s ? s.land : 'push' in s ? s.push : 0);
