// E2A YouTube Comedy — character pose model (shared by every episode).
// A pose is a flat record of joint angles (radians) + root transform + face controls, so any two
// poses can be blended and any action can override only the channels it cares about.

export type Face = {
  /** brow height per side, -1 (down/angry) .. 1 (raised) */
  browL: number;
  browR: number;
  /** brow tilt: + inner ends up (worried/sad), - inner ends down (angry/annoyed) */
  browTilt: number;
  /** upper lid closure 0 open .. 1 closed */
  lid: number;
  /** lower lid squint 0 .. 1 */
  squint: number;
  /** mouth corner curve -1 frown .. 1 smile */
  smile: number;
  /** extra mouth opening (added to lip-sync) 0..1 */
  open: number;
  /** mouth width multiplier */
  wide: number;
  /** gaze offset in head space: x right(-1..1), y up(-1..1) */
  gazeX: number;
  gazeY: number;
  /** cheek/sneer asymmetry: + raises the right corner (smirk) */
  smirk: number;
};

export type Pose = {
  // root (world, metres / radians)
  x: number;
  z: number;
  /** pelvis height offset from standing (m); negative = crouch, positive = airborne */
  lift: number;
  yaw: number;
  /** whole-body lean forward(+)/back(-) at the hips */
  lean: number;
  /** whole-body roll (side tilt) */
  roll: number;
  /** sitting on the floor 0..1 (moves pelvis down to the floor) */
  sit: number;
  // spine
  spineBend: number; // forward +
  spineTwist: number; // + turn left
  spineSide: number;
  // head/neck
  headYaw: number; // + look left
  headPitch: number; // + look down
  headRoll: number;
  // arms: shoulder pitch (+ forward/up), shoulder abduction (+ out to the side), elbow bend (+), wrist
  lShPitch: number;
  lShOut: number;
  lShTwist: number;
  lElbow: number;
  rShPitch: number;
  rShOut: number;
  rShTwist: number;
  rElbow: number;
  /** index finger point 0..1 */
  lPoint: number;
  rPoint: number;
  // legs: hip pitch (+ forward), hip abduction, knee bend (+), ankle (+ toes up)
  lHip: number;
  lHipOut: number;
  lKnee: number;
  lAnkle: number;
  rHip: number;
  rHipOut: number;
  rKnee: number;
  rAnkle: number;
  face: Face;
};

export const FACE0: Face = {browL: 0, browR: 0, browTilt: 0, lid: 0.12, squint: 0, smile: 0, open: 0, wide: 1, gazeX: 0, gazeY: 0, smirk: 0};

export const POSE0: Pose = {
  x: 0, z: 0, lift: 0, yaw: 0, lean: 0, roll: 0, sit: 0,
  spineBend: 0.03, spineTwist: 0, spineSide: 0,
  headYaw: 0, headPitch: 0, headRoll: 0,
  lShPitch: 0.05, lShOut: 0.16, lShTwist: 0, lElbow: 0.25,
  rShPitch: 0.05, rShOut: 0.16, rShTwist: 0, rElbow: 0.25,
  lPoint: 0, rPoint: 0,
  lHip: 0.02, lHipOut: 0.06, lKnee: 0.06, lAnkle: 0,
  rHip: 0.02, rHipOut: 0.06, rKnee: 0.06, rAnkle: 0,
  face: FACE0,
};

export type PosePatch = Partial<Omit<Pose, 'face'>> & {face?: Partial<Face>};

export const clamp = (v: number, a = 0, b = 1) => Math.max(a, Math.min(b, v));
export const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
export const smooth = (u: number) => {
  const v = clamp(u);
  return v * v * (3 - 2 * v);
};
export const easeOut = (u: number) => 1 - (1 - clamp(u)) ** 3;
export const easeIn = (u: number) => clamp(u) ** 3;
/** overshoot ease (cartoon settle) */
export const backOut = (u: number, s = 1.6) => {
  const v = clamp(u) - 1;
  return 1 + v * v * ((s + 1) * v + s);
};

export const apply = (p: Pose, patch: PosePatch | undefined): Pose => {
  if (!patch) return p;
  const {face, ...rest} = patch;
  return {...p, ...rest, face: face ? {...p.face, ...face} : p.face};
};

export const mix = (a: Pose, b: Pose, u: number): Pose => {
  if (u <= 0) return a;
  if (u >= 1) return b;
  const out = {...a} as Record<string, unknown>;
  for (const k of Object.keys(a) as (keyof Pose)[]) {
    if (k === 'face') continue;
    out[k] = lerp(a[k] as number, b[k] as number, u);
  }
  const f = {...a.face} as Record<string, number>;
  for (const k of Object.keys(a.face) as (keyof Face)[]) f[k] = lerp(a.face[k], b.face[k], u);
  out.face = f;
  return out as Pose;
};

/** keyframed channel track: [time, patch][] with smooth interpolation between consecutive keys */
export type Key = {t: number; p: PosePatch; ease?: 'smooth' | 'out' | 'in' | 'back' | 'step' | 'linear'};

const E = {smooth, out: easeOut, in: easeIn, back: (u: number) => backOut(u), step: (u: number) => (u >= 1 ? 1 : 0), linear: clamp};

/** evaluate keys at t over a base pose: each key's patch is accumulated (later keys inherit earlier channels) */
export const evalKeys = (base: Pose, keys: Key[], t: number): Pose => {
  if (!keys.length) return base;
  // resolve absolute poses per key (cumulative)
  let acc = base;
  const abs: Pose[] = keys.map((k) => (acc = apply(acc, k.p)));
  if (t <= keys[0].t) return abs[0];
  for (let i = 0; i < keys.length - 1; i++) {
    const a = keys[i];
    const b = keys[i + 1];
    if (t < b.t) {
      const u = (t - a.t) / Math.max(1e-6, b.t - a.t);
      return mix(abs[i], abs[i + 1], E[b.ease ?? 'smooth'](u));
    }
  }
  return abs[abs.length - 1];
};
