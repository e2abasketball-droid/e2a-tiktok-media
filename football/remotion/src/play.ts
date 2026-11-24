// E2A Football — play data and deterministic sampling.
// Pitch convention (same as football/engine/pitch.py): metres and seconds, origin at the centre spot,
// the attacking team attacks towards +x, y across the pitch, z up.
// Everything is precomputed on a fixed 1/120 s grid from t = 0, so any frame can be rendered alone
// (Remotion renders frames out of order) and still be identical to a sequential render.

export type Key = [number, number, number];
export type Action = {type: 'dive'; t0: number; t1: number; side: 1 | -1};
export type FBPlayer = {id: string; team: 'attack' | 'defence'; role: string; number: number; track: Key[]; actions?: Action[]};
export type BallEvent = {
  t: number;
  type: 'hold' | 'dribble' | 'pass' | 'cross' | 'through' | 'shot' | 'clear' | 'out' | 'rest';
  by?: string;
  to?: string;
  height?: 'ground' | 'low' | 'lofted';
  t1?: number;
  target?: [number, number];
  lift?: number;
  net?: [number, number];
  /** 'rest': the ball lies still at this point (corner arc, free-kick spot) until the next event */
  at?: [number, number];
  /** ground-pass physics v2 (FB-SETPIECE-001): constant rolling deceleration in m/s^2 (grass ~1-2.5).
   *  When set, the pass starts from where the ball really is (no snap to the foot), the speed profile is
   *  derived from it, and the receiver cushions the ball (see `cushion`). Plays without it are unchanged. */
  decel?: number;
  /** reception cushion time constant in s (default 0.07): the ball keeps its arrival speed for a few cm
   *  in front of the receiving foot and is absorbed, so the velocity is continuous at the first touch */
  cushion?: number;
  /** animation v2: 'inside' = side-foot technique (turned-out foot, short back-swing, follow-through to the target) */
  foot?: 'inside' | 'instep';
};
export type FBPlay = {
  id: string;
  version: number;
  title: string;
  duration: number;
  teams: {attack: {name: string; colour: string}; defence: {name: string; colour: string}};
  players: FBPlayer[];
  ball: {events: BallEvent[]};
  /** FB-SETPIECE-001+: animate the reception pose for passes received (older plays keep their look) */
  receivePose?: boolean;
  /** optional set-piece context (for QC and the library), not rendered */
  setPiece?: Record<string, unknown>;
  /** FB-SETPIECE-001 V03+: animation v2 (run cycle, side-foot kicks, guard / keeper stances, side-steps and
   *  backpedal, smooth dribble touches). Older plays keep the v1 look exactly. */
  animV2?: boolean;
  /** V05+: heads turn towards the ball (older plays keep a fixed head) */
  headLook?: boolean;
  /** V07+: MASTER MATCH TIMELINE — named events (one time source for runs, contacts, reactions, camera and
   *  graphics), run book and off-ball roles; validated by scripts/fb_timeline.py, not rendered */
  timeline?: {id: string; t: number; who: string[]; kind: 'ball' | 'run' | 'reaction'; what: string}[];
  runs?: Record<string, unknown>[];
  offBallRoles?: Record<string, string[]>;
};
/** V07: event time by name from the master timeline (throws if the name does not exist: no silent drift) */
export const ev = (play: FBPlay, id: string): number => {
  const e = (play.timeline ?? []).find((x) => x.id === id);
  if (!e) throw new Error(`timeline event ${id} not found`);
  return e.t;
};
export type V2 = [number, number];
export type V3 = [number, number, number];

export const BALL_R = 0.11;
const DT = 1 / 120;
const clamp = (x: number, a: number, b: number) => Math.max(a, Math.min(b, x));
export const smooth = (x: number) => {
  const u = clamp(x, 0, 1);
  return u * u * (3 - 2 * u);
};

/** cubic Hermite through the keyframes (Catmull-Rom tangents in time): continuous velocity, no kinks */
export const trackPos = (tr: Key[], t: number): V2 => {
  if (tr.length === 1 || t <= tr[0][0]) return [tr[0][1], tr[0][2]];
  const n = tr.length;
  if (t >= tr[n - 1][0]) return [tr[n - 1][1], tr[n - 1][2]];
  let i = 0;
  while (i < n - 2 && t > tr[i + 1][0]) i++;
  const tan = (k: number): V2 => {
    const a = tr[Math.max(0, k - 1)];
    const b = tr[Math.min(n - 1, k + 1)];
    const dt = b[0] - a[0];
    return dt > 0 ? [(b[1] - a[1]) / dt, (b[2] - a[2]) / dt] : [0, 0];
  };
  const [t0, x0, y0] = tr[i];
  const [t1, x1, y1] = tr[i + 1];
  const h = t1 - t0;
  const u = (t - t0) / h;
  const m0 = tan(i);
  const m1 = tan(i + 1);
  // the first and last keys hold the player still unless the data keeps moving
  const u2 = u * u;
  const u3 = u2 * u;
  const h00 = 2 * u3 - 3 * u2 + 1;
  const h10 = u3 - 2 * u2 + u;
  const h01 = -2 * u3 + 3 * u2;
  const h11 = u3 - u2;
  return [h00 * x0 + h10 * h * m0[0] + h01 * x1 + h11 * h * m1[0], h00 * y0 + h10 * h * m0[1] + h01 * y1 + h11 * h * m1[1]];
};

export type Kick = {t: number; power: number; inside?: boolean; shot?: boolean}; // a kick by this player at time t
export type PlayerState = {
  pos: V2;
  vel: V2;
  speed: number;
  accel: number; // tangential acceleration, m/s^2
  heading: number; // radians, world angle of the facing direction (atan2(fy, fx))
  turn: number; // heading rate, rad/s (for banking)
  phase: number; // gait phase (radians), advances with distance travelled
};
export type BallState = {pos: V3; holder?: string; spin: [number, number, number, number]; speed: number; netHit?: {t: number; at: V3}};

type Pre = {
  n: number;
  players: Record<string, {pos: V2[]; heading: number[]; phase: number[]; speed: number[]}>;
  kicks: Record<string, Kick[]>;
  ball: {pos: V3[]; quat: [number, number, number, number][]; holder: (string | undefined)[]};
  netHit?: {t: number; at: V3};
};

const cache = new WeakMap<FBPlay, Pre>();

const sub = (a: V2, b: V2): V2 => [a[0] - b[0], a[1] - b[1]];
const len = (a: V2) => Math.hypot(a[0], a[1]);
const angDiff = (a: number, b: number) => {
  let d = a - b;
  while (d > Math.PI) d -= 2 * Math.PI;
  while (d < -Math.PI) d += 2 * Math.PI;
  return d;
};

/** stride length (two steps) as a function of ground speed: ~1.4 m walking, ~2.4 m jogging, ~3.6 m sprinting */
export const strideLen = (v: number) => clamp(0.75 + 0.45 * v - 0.012 * v * v, 0.9, 4.2);

const sortedEvents = (play: FBPlay) => [...play.ball.events].sort((a, b) => a.t - b.t);

/** pass profile: the ball leaves fast and arrives slower (rolling friction), never stops mid-way.
 *  s(u) = u + k u (1-u) is quadratic in time, i.e. a constant deceleration a = 2 k D / T^2. */
const passS = (u: number, k = 0.45) => u + k * u * (1 - u);
/** k for a measured rolling deceleration (m/s^2) over distance D in time T; capped so the ball never stops early */
export const decelK = (a: number, T: number, D: number) => (D > 1e-6 ? clamp((a * T * T) / (2 * D), 0, 0.9) : 0);
/** speed (m/s) at the start and at the arrival of a v2 ground pass */
export const passSpeeds = (a: number, T: number, D: number) => {
  const k = decelK(a, T, D);
  return {v0: ((1 + k) * D) / T, v1: ((1 - k) * D) / T, k};
};

const precompute = (play: FBPlay): Pre => {
  const n = Math.ceil(play.duration / DT) + 1;
  const ev = sortedEvents(play);
  const byId: Record<string, FBPlayer> = Object.fromEntries(play.players.map((p) => [p.id, p]));
  // pass 1: centres, velocities
  const raw: Record<string, {pos: V2[]; vel: V2[]; speed: number[]}> = {};
  for (const p of play.players) {
    const pos: V2[] = [];
    for (let i = 0; i < n; i++) pos.push(trackPos(p.track, i * DT));
    const vel: V2[] = pos.map((_, i) => {
      const a = pos[Math.max(0, i - 2)];
      const b = pos[Math.min(n - 1, i + 2)];
      const dt = (Math.min(n - 1, i + 2) - Math.max(0, i - 2)) * DT;
      return [(b[0] - a[0]) / dt, (b[1] - a[1]) / dt];
    });
    raw[p.id] = {pos, vel, speed: vel.map(len)};
  }
  // rough ball (holder centre) to aim headings at
  const roughBall = (t: number): V2 => {
    let cur = ev[0];
    for (const e of ev) if (e.t <= t) cur = e;
    const at = (id: string, tt: number) => trackPos(byId[id].track, tt);
    if (cur.type === 'rest') return cur.at!;
    if ((cur.type === 'pass' || cur.type === 'through' || cur.type === 'shot' || cur.type === 'cross') && cur.t1 !== undefined && t < cur.t1) {
      const a = at(cur.by!, cur.t);
      const b = cur.target ?? at(cur.to!, cur.t1);
      const u = passS((t - cur.t) / (cur.t1 - cur.t));
      return [a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u];
    }
    if (cur.type === 'shot') return cur.net ?? cur.target ?? at(cur.by!, cur.t);
    const h = cur.to ?? cur.by!;
    return at(h, t);
  };
  // kick directions (to orient the body before a pass / set / shot)
  const kickDir: Record<string, {t: number; ang: number}[]> = {};
  for (const e of ev) {
    if (!e.by || !['pass', 'through', 'shot', 'cross', 'clear'].includes(e.type)) continue;
    const a = trackPos(byId[e.by].track, e.t);
    const b = e.target ?? trackPos(byId[e.to!].track, e.t1 ?? e.t + 1);
    (kickDir[e.by] ??= []).push({t: e.t, ang: Math.atan2(b[1] - a[1], b[0] - a[0])});
  }
  // pass 2: headings with a turn-rate limit, gait phase
  const players: Pre['players'] = {};
  for (const p of play.players) {
    const {pos, vel, speed} = raw[p.id];
    const heading: number[] = [];
    const phase: number[] = [];
    let h = 0;
    let ph = (p.number * 1.37) % (2 * Math.PI); // de-synchronise players
    for (let i = 0; i < n; i++) {
      const t = i * DT;
      const b = roughBall(t);
      const toBall = sub(b, pos[i]);
      const ballAng = len(toBall) > 0.3 ? Math.atan2(toBall[1], toBall[0]) : h;
      const v = speed[i];
      const velAng = v > 0.05 ? Math.atan2(vel[i][1], vel[i][0]) : ballAng;
      // slow defenders moving away from the ball shuffle backwards, still facing it
      const backpedal = v < 3.2 && Math.cos(angDiff(velAng, ballAng)) < -0.25;
      const w = backpedal ? 0 : clamp((v - 0.6) / 2.6, 0, 1);
      let want = ballAng + angDiff(velAng, ballAng) * w;
      for (const kd of kickDir[p.id] ?? []) if (t > kd.t - 0.5 && t < kd.t + 0.12) want = kd.ang;
      if (i === 0) h = want;
      else {
        const maxTurn = (5.5 + 3.5 * clamp(1 - v / 8, 0, 1)) * DT; // fast runners turn more slowly
        const d = angDiff(want, h);
        h += clamp(d * 0.18, -maxTurn, maxTurn);
      }
      heading.push(h);
      if (i > 0) ph += (2 * Math.PI * v * DT) / strideLen(v);
      phase.push(ph);
    }
    players[p.id] = {pos, heading, phase, speed};
  }
  // kicks
  const kicks: Record<string, Kick[]> = {};
  for (const e of ev) {
    if (!e.by || !['pass', 'through', 'shot', 'cross', 'clear'].includes(e.type)) continue;
    (kicks[e.by] ??= []).push({t: e.t, power: e.type === 'shot' ? 1 : e.type === 'through' ? 0.55 : 0.7, inside: e.foot === 'inside', shot: e.type === 'shot'});
  }
  // pass 3: exact ball (at the foot, in front of the body)
  const idx = (t: number) => clamp(Math.round(t / DT), 0, n - 1);
  const foot = (id: string, t: number, ahead = 0.42): V2 => {
    const P = players[id];
    const i = idx(t);
    const hh = P.heading[i];
    return [P.pos[i][0] + Math.cos(hh) * ahead, P.pos[i][1] + Math.sin(hh) * ahead];
  };
  const bpos: V3[] = [];
  const holder: (string | undefined)[] = [];
  const passStart: Record<number, V2> = {};
  let netHit: Pre['netHit'];
  for (let i = 0; i < n; i++) {
    const t = i * DT;
    let k = 0;
    for (let j = 0; j < ev.length; j++) if (ev[j].t <= t) k = j;
    const e = ev[k];
    const flying = (e.type === 'pass' || e.type === 'through' || e.type === 'cross' || e.type === 'shot') && e.t1 !== undefined;
    const prev = k > 0 ? ev[k - 1] : undefined;
    if (e.type === 'rest') {
      bpos.push([e.at![0], e.at![1], BALL_R]);
      holder.push(undefined);
    } else if (flying && t < e.t1!) {
      if (e.decel !== undefined && passStart[k] === undefined) passStart[k] = i > 0 ? [bpos[i - 1][0], bpos[i - 1][1]] : foot(e.by!, e.t, 0.38);
      const a = e.decel !== undefined ? passStart[k] : foot(e.by!, e.t, 0.38);
      const b = e.target ?? foot(e.to!, e.t1!, 0.4);
      const u = (t - e.t) / (e.t1! - e.t);
      const s = e.type === 'shot' ? passS(u, 0.15) : passS(u, e.decel !== undefined ? decelK(e.decel, e.t1! - e.t, Math.hypot(b[0] - a[0], b[1] - a[1])) : 0.45);
      const z = BALL_R + (e.type === 'shot' ? (e.lift ?? 0.4) * Math.sin(Math.PI * Math.min(1, u * 1.05)) : 0) + (e.height === 'lofted' ? 4 * u * (1 - u) * 3 : 0);
      bpos.push([a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s, z]);
      holder.push(undefined);
    } else if (e.type === 'shot' && flying) {
      // into the net: the ball keeps going to the back netting, drops and settles
      const b = e.target!;
      const nt = e.net ?? [b[0] + 1.6, b[1]];
      const dtn = t - e.t1!;
      const u = clamp(dtn / 0.16, 0, 1);
      const back = 1 - Math.pow(1 - u, 2);
      const x = b[0] + (nt[0] - b[0]) * back - (dtn > 0.16 ? Math.min(0.35, (dtn - 0.16) * 0.9) : 0);
      const y = b[1] + (nt[1] - b[1]) * back;
      const z0 = BALL_R + (e.lift ?? 0.4) * Math.sin(Math.PI * 1.0) + 0.05;
      const fall = dtn > 0.16 ? Math.min(1, (dtn - 0.16) / 0.35) : 0;
      const bounce = fall >= 1 ? Math.abs(Math.sin((dtn - 0.51) * 9)) * 0.06 * Math.exp(-(dtn - 0.51) * 6) : 0;
      bpos.push([x, y, Math.max(BALL_R, z0 * (1 - fall * fall) + BALL_R * fall * fall) + bounce]);
      holder.push(undefined);
      if (!netHit && dtn >= 0.16) netHit = {t, at: [nt[0], nt[1], z0]};
    } else {
      const hId = e.type === 'hold' || e.type === 'dribble' ? e.by! : (e.to ?? e.by!);
      const P = players[hId];
      const ii = idx(t);
      // v2 reception: the arriving ball is absorbed in front of the foot (continuous velocity)
      const rcv = e.decel !== undefined && e.t1 !== undefined ? e : prev && prev.decel !== undefined && prev.t1 !== undefined && prev.to === hId && (e.type === 'hold' || e.type === 'dribble') ? prev : undefined;
      if (rcv && rcv.to === hId && t >= rcv.t1!) {
        const dtc = t - rcv.t1!;
        const tau = rcv.cushion ?? 0.07;
        if (dtc < tau * 8) {
          const ri = ev.indexOf(rcv);
          const a0 = passStart[ri] ?? foot(rcv.by!, rcv.t, 0.38);
          const b0 = foot(hId, rcv.t1!, 0.4);
          const D = Math.hypot(b0[0] - a0[0], b0[1] - a0[1]);
          const T = rcv.t1! - rcv.t;
          const vEnd = ((1 - decelK(rcv.decel!, T, D)) * D) / T;
          const dir: V2 = D > 1e-6 ? [(b0[0] - a0[0]) / D, (b0[1] - a0[1]) / D] : [0, 0];
          const off = vEnd * dtc * Math.exp(-dtc / tau);
          const f = foot(hId, t, 0.4);
          bpos.push([f[0] + dir[0] * off, f[1] + dir[1] * off, BALL_R]);
          holder.push(hId);
          continue;
        }
      }
      let ahead = 0.4;
      if (play.animV2) {
        // v2: touches fade in with speed and after the reception, and fade out before the next kick (no jumps)
        const nk = ev.find((x) => x.t > t && x.by === hId && ['pass', 'through', 'shot', 'cross', 'clear'].includes(x.type));
        const w = smooth((P.speed[ii] - 1.6) / 1.4) * smooth((t - e.t - 0.45) / 0.4) * (nk ? smooth((nk.t - t - 0.12) / 0.45) : 1);
        const u = ((P.phase[ii] / (4 * Math.PI)) % 1 + 1) % 1;
        const push = 0.3 + 0.07 * P.speed[ii];
        ahead = 0.4 + w * (u < 0.18 ? push * smooth(u / 0.18) : push * (1 - smooth((u - 0.18) / 0.82)));
      } else if (e.type === 'dribble' || P.speed[ii] > 2.5) {
        // close control: a touch every two strides, the runner then catches the ball up
        const u = ((P.phase[ii] / (4 * Math.PI)) % 1 + 1) % 1;
        const push = 0.35 + 0.08 * P.speed[ii];
        ahead = 0.42 + (u < 0.14 ? push * smooth(u / 0.14) : push * (1 - (u - 0.14) / 0.86));
      }
      const f = foot(hId, t, ahead);
      bpos.push([f[0], f[1], BALL_R]);
      holder.push(hId);
    }
  }
  // spin: roll without slipping on the ground (axis perpendicular to motion)
  const quat: [number, number, number, number][] = [];
  let q: [number, number, number, number] = [0, 0, 0, 1];
  for (let i = 0; i < n; i++) {
    if (i > 0) {
      const dx = bpos[i][0] - bpos[i - 1][0];
      const dy = bpos[i][1] - bpos[i - 1][1];
      const d = Math.hypot(dx, dy);
      if (d > 1e-6) {
        // world axis (z up): (-dy, dx, 0)/d ; three.js axis: (x, z, -y) -> (-dy, 0, -dx)/d
        const ang = d / BALL_R;
        const ax = [-dy / d, 0, -dx / d];
        const s = Math.sin(ang / 2);
        const r: [number, number, number, number] = [ax[0] * s, ax[1] * s, ax[2] * s, Math.cos(ang / 2)];
        // q = r * q
        q = [
          r[3] * q[0] + r[0] * q[3] + r[1] * q[2] - r[2] * q[1],
          r[3] * q[1] - r[0] * q[2] + r[1] * q[3] + r[2] * q[0],
          r[3] * q[2] + r[0] * q[1] - r[1] * q[0] + r[2] * q[3],
          r[3] * q[3] - r[0] * q[0] - r[1] * q[1] - r[2] * q[2],
        ];
        const m = Math.hypot(...q);
        q = [q[0] / m, q[1] / m, q[2] / m, q[3] / m];
      }
    }
    quat.push(q);
  }
  return {n, players, kicks, ball: {pos: bpos, quat, holder}, netHit};
};

export const pre = (play: FBPlay) => {
  let p = cache.get(play);
  if (!p) {
    p = precompute(play);
    cache.set(play, p);
  }
  return p;
};

const lerpIdx = (play: FBPlay, t: number) => {
  const P = pre(play);
  const x = clamp(t, 0, play.duration) / DT;
  const i = Math.min(P.n - 2, Math.floor(x));
  return {P, i, f: Math.min(1, x - i)};
};

export const playerAt = (play: FBPlay, id: string, t: number): PlayerState => {
  const {P, i, f} = lerpIdx(play, t);
  const S = P.players[id];
  const L = (a: number, b: number) => a + (b - a) * f;
  const pos: V2 = [L(S.pos[i][0], S.pos[i + 1][0]), L(S.pos[i][1], S.pos[i + 1][1])];
  const j0 = Math.max(0, i - 3);
  const j1 = Math.min(P.n - 1, i + 3);
  const vel: V2 = [(S.pos[j1][0] - S.pos[j0][0]) / ((j1 - j0) * DT), (S.pos[j1][1] - S.pos[j0][1]) / ((j1 - j0) * DT)];
  const k0 = Math.max(0, i - 12);
  const k1 = Math.min(P.n - 1, i + 12);
  const accel = (S.speed[k1] - S.speed[k0]) / ((k1 - k0) * DT);
  const turn = angDiff(S.heading[Math.min(P.n - 1, i + 6)], S.heading[Math.max(0, i - 6)]) / (12 * DT);
  return {pos, vel, speed: L(S.speed[i], S.speed[i + 1]), accel, heading: S.heading[i] + angDiff(S.heading[i + 1], S.heading[i]) * f, turn, phase: L(S.phase[i], S.phase[i + 1])};
};

export const ballAt = (play: FBPlay, t: number): BallState => {
  const {P, i, f} = lerpIdx(play, t);
  const a = P.ball.pos[i];
  const b = P.ball.pos[i + 1];
  const pos: V3 = [a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, a[2] + (b[2] - a[2]) * f];
  const speed = Math.hypot(b[0] - a[0], b[1] - a[1], b[2] - a[2]) / DT;
  return {pos, holder: P.ball.holder[i], spin: P.ball.quat[i], speed, netHit: P.netHit};
};

export const kicksOf = (play: FBPlay, id: string) => pre(play).kicks[id] ?? [];

/** arrival times of passes to this player (for the reception pose) */
export const receivesOf = (play: FBPlay, id: string): number[] => {
  // a first-time strike (the same player kicks within 0.3 s of the arrival) has no cushioning pose
  const kicks = play.ball.events.filter((e) => e.by === id && ['pass', 'through', 'shot', 'cross', 'clear'].includes(e.type)).map((e) => e.t);
  return play.ball.events
    .filter((e) => e.to === id && e.t1 !== undefined && ['pass', 'through', 'cross'].includes(e.type))
    .map((e) => e.t1!)
    .filter((t1) => !kicks.some((k) => k >= t1 - 0.05 && k <= t1 + 0.3));
};

/** route of a player between two play times (for run arrows) */
export const routeOf = (play: FBPlay, id: string, t0: number, t1: number, step = 1 / 30): V2[] => {
  const out: V2[] = [];
  for (let t = t0; t <= t1 + 1e-6; t += step) out.push(playerAt(play, id, t).pos);
  return out;
};

/** ball path between two play times (for pass lines that follow the real ball) */
export const ballPath = (play: FBPlay, t0: number, t1: number, step = 1 / 30): V2[] => {
  const out: V2[] = [];
  for (let t = t0; t <= t1 + 1e-6; t += step) {
    const b = ballAt(play, t).pos;
    out.push([b[0], b[1]]);
  }
  return out;
};

/** offside line for the attack (towards +x): second-last defender or the ball, never inside the own half */
export const offsideLine = (play: FBPlay, t: number) => {
  const xs = play.players.filter((p) => p.team === 'defence').map((p) => playerAt(play, p.id, t).pos[0]).sort((a, b) => b - a);
  const bx = ballAt(play, t).pos[0];
  return Math.max(xs[1] ?? 0, bx, 0);
};
