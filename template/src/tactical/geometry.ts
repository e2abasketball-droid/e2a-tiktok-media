// E2A Tactical engine — court geometry and the 2.5D camera.
// World units are METRES on a FIBA half court:
//   x across the court (-7.5 .. 7.5, 0 = centre line of the basket),
//   y from the baseline (0) toward half court (14),
//   z up from the floor.
// The camera is a real pinhole perspective projection of 3D points. Players and the ball are
// drawn as depth-scaled billboards on top of the projected floor, so the result is 2.5D:
// correct perspective, scale, occlusion order and shadows, but not a 3D renderer.

export type V2 = [number, number];
export type V3 = [number, number, number];

export const FIBA = {
  halfW: 7.5,
  halfL: 14,
  basket: [0, 1.575] as V2,
  rimZ: 3.05,
  rimR: 0.225,
  boardY: 1.2,
  boardHalfW: 0.9,
  boardZ0: 2.9,
  boardZ1: 3.95,
  keyHalfW: 2.45,
  ftY: 5.8,
  ftR: 1.8,
  threeR: 6.75,
  cornerX: 6.6,
  restrictedR: 1.25,
  centreR: 1.8,
};

/** y where the straight corner three meets the arc */
export const threeJoinY = FIBA.basket[1] + Math.sqrt(FIBA.threeR ** 2 - FIBA.cornerX ** 2);

export const distToBasket = (p: V2) => Math.hypot(p[0] - FIBA.basket[0], p[1] - FIBA.basket[1]);

/** true if a floor point is behind the FIBA three-point line */
export const isThree = (p: V2) => (p[1] <= threeJoinY ? Math.abs(p[0]) >= FIBA.cornerX : distToBasket(p) >= FIBA.threeR);

export type CameraState = {
  /** point the camera looks at (metres) */
  target: V3;
  /** distance from the target (metres) */
  dist: number;
  /** degrees from straight down: 0 = top-down, 90 = horizontal */
  pitch: number;
  /** degrees around the vertical axis: 0 = looking from the baseline toward half court */
  yaw: number;
  /** vertical field of view in degrees */
  fov: number;
  /** screen offset of the target in px (to frame the action above the subtitles) */
  shiftY?: number;
  /** roll in degrees (subtle, for dynamic angles) */
  roll?: number;
};

export type Projector = {
  /** screen point and depth; depth <= near means behind the camera */
  p: (w: V3) => {x: number; y: number; z: number; s: number};
  cam: CameraState;
  W: number;
  H: number;
  forward: V3;
  pos: V3;
};

const rad = (d: number) => (d * Math.PI) / 180;
export const NEAR = 0.25;

export const makeProjector = (cam: CameraState, W: number, H: number): Projector => {
  const ph = rad(cam.pitch);
  const ps = rad(cam.yaw);
  const f: V3 = [Math.sin(ph) * Math.sin(ps), Math.sin(ph) * Math.cos(ps), -Math.cos(ph)];
  const r: V3 = [Math.cos(ps), -Math.sin(ps), 0];
  const u: V3 = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]];
  const pos: V3 = [cam.target[0] - f[0] * cam.dist, cam.target[1] - f[1] * cam.dist, cam.target[2] - f[2] * cam.dist];
  const focal = H / 2 / Math.tan(rad(cam.fov) / 2);
  const cx = W / 2;
  const cy = H / 2 + (cam.shiftY ?? 0);
  const roll = rad(cam.roll ?? 0);
  const cr = Math.cos(roll);
  const sr = Math.sin(roll);
  return {
    cam,
    W,
    H,
    forward: f,
    pos,
    p: (w) => {
      const v = [w[0] - pos[0], w[1] - pos[1], w[2] - pos[2]];
      const xc = v[0] * r[0] + v[1] * r[1] + v[2] * r[2];
      const yc = v[0] * u[0] + v[1] * u[1] + v[2] * u[2];
      const zc = v[0] * f[0] + v[1] * f[1] + v[2] * f[2];
      const z = Math.max(zc, 1e-4);
      const s = focal / z; // px per metre at that depth
      const sx = xc * s;
      const sy = -yc * s;
      return {x: cx + sx * cr - sy * sr, y: cy + sx * sr + sy * cr, z: zc, s};
    },
  };
};

/** Project a floor polyline to an SVG path, splitting where it goes behind the camera. */
export const floorPath = (pr: Projector, pts: V2[], close = false, z = 0): string => {
  let d = '';
  let pen = false;
  pts.forEach((q) => {
    const s = pr.p([q[0], q[1], z]);
    if (s.z <= NEAR) {
      pen = false;
      return;
    }
    d += `${pen ? 'L' : 'M'}${s.x.toFixed(1)} ${s.y.toFixed(1)}`;
    pen = true;
  });
  return close && d ? d + 'Z' : d;
};

export const arc = (c: V2, r: number, a0: number, a1: number, n = 48): V2[] => {
  const out: V2[] = [];
  for (let i = 0; i <= n; i++) {
    const a = a0 + ((a1 - a0) * i) / n;
    out.push([c[0] + r * Math.cos(a), c[1] + r * Math.sin(a)]);
  }
  return out;
};

export const seg = (a: V2, b: V2, n = 12): V2[] => Array.from({length: n + 1}, (_, i) => [a[0] + ((b[0] - a[0]) * i) / n, a[1] + ((b[1] - a[1]) * i) / n] as V2);

/** Court line polylines (FIBA half court), densely sampled so perspective bends them correctly. */
export const courtLines = (): {pts: V2[]; close?: boolean; w?: number}[] => {
  const {halfW, halfL, basket, keyHalfW, ftY, ftR, threeR, cornerX, restrictedR, centreR} = FIBA;
  const ang = Math.asin((threeJoinY - basket[1]) / threeR);
  return [
    {pts: [...seg([-halfW, 0], [halfW, 0], 30), ...seg([halfW, 0], [halfW, halfL], 30).slice(1), ...seg([halfW, halfL], [-halfW, halfL], 30).slice(1), ...seg([-halfW, halfL], [-halfW, 0], 30).slice(1)], w: 1.3},
    {pts: [...seg([-keyHalfW, 0], [-keyHalfW, ftY]), ...seg([-keyHalfW, ftY], [keyHalfW, ftY]).slice(1), ...seg([keyHalfW, ftY], [keyHalfW, 0]).slice(1)]},
    {pts: arc([0, ftY], ftR, 0, Math.PI)},
    {pts: [...seg([-cornerX, 0], [-cornerX, threeJoinY], 6), ...arc(basket, threeR, Math.PI - ang, ang, 90).slice(1), ...seg([cornerX, threeJoinY], [cornerX, 0], 6).slice(1)]},
    {pts: [...seg([-restrictedR, basket[1]], [-restrictedR, 1.2], 2), ...arc(basket, restrictedR, Math.PI, 0, 30)].concat(seg([restrictedR, basket[1]], [restrictedR, 1.2], 2))},
    {pts: arc([0, halfL], centreR, Math.PI, 2 * Math.PI)},
  ];
};

/** Solve the 3x3 homography that maps the unit square to 4 screen points (CSS matrix3d). */
export const homographyCss = (q: {x: number; y: number}[], w: number, h: number): string => {
  // maps (0,0),(w,0),(w,h),(0,h) -> q0..q3
  const [p0, p1, p2, p3] = q;
  const dx1 = p1.x - p2.x;
  const dx2 = p3.x - p2.x;
  const dy1 = p1.y - p2.y;
  const dy2 = p3.y - p2.y;
  const sx = p0.x - p1.x + p2.x - p3.x;
  const sy = p0.y - p1.y + p2.y - p3.y;
  const det = dx1 * dy2 - dx2 * dy1;
  const g = (sx * dy2 - dx2 * sy) / det;
  const hh = (dx1 * sy - sx * dy1) / det;
  const a = p1.x - p0.x + g * p1.x;
  const b = p3.x - p0.x + hh * p3.x;
  const c = p0.x;
  const d = p1.y - p0.y + g * p1.y;
  const e = p3.y - p0.y + hh * p3.y;
  const f = p0.y;
  // scale from unit square to w x h
  const m = [a / w, d / w, 0, g / w, b / h, e / h, 0, hh / h, 0, 0, 1, 0, c, f, 0, 1];
  return `matrix3d(${m.map((v) => +v.toFixed(8)).join(',')})`;
};

/** camera-space depth of a world point */
const depth = (pr: Projector, w: V3) => {
  const f = pr.forward;
  return (w[0] - pr.pos[0]) * f[0] + (w[1] - pr.pos[1]) * f[1] + (w[2] - pr.pos[2]) * f[2];
};

/** Project a 3D polygon, clipped against the near plane (Sutherland–Hodgman, one plane). */
export const polyPath = (pr: Projector, pts: V3[]): string => {
  const out: V3[] = [];
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i];
    const b = pts[(i + 1) % pts.length];
    const da = depth(pr, a) - NEAR;
    const db = depth(pr, b) - NEAR;
    if (da >= 0) out.push(a);
    if ((da >= 0) !== (db >= 0)) {
      const u = da / (da - db);
      out.push([a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u]);
    }
  }
  if (out.length < 3) return '';
  return out.map((w, i) => {
    const s = pr.p(w);
    return `${i ? 'L' : 'M'}${s.x.toFixed(1)} ${s.y.toFixed(1)}`;
  }).join('') + 'Z';
};

/** Project a 3D segment clipped against the near plane; null if fully behind. */
export const segPath = (pr: Projector, a: V3, b: V3): string | null => {
  let A = a;
  let B = b;
  const da = depth(pr, A) - NEAR;
  const db = depth(pr, B) - NEAR;
  if (da < 0 && db < 0) return null;
  if (da < 0) {
    const u = da / (da - db);
    A = [A[0] + (B[0] - A[0]) * u, A[1] + (B[1] - A[1]) * u, A[2] + (B[2] - A[2]) * u];
  } else if (db < 0) {
    const u = da / (da - db);
    B = [A[0] + (B[0] - A[0]) * u, A[1] + (B[1] - A[1]) * u, A[2] + (B[2] - A[2]) * u];
  }
  const s = pr.p(A);
  const e = pr.p(B);
  return `M${s.x.toFixed(1)} ${s.y.toFixed(1)}L${e.x.toFixed(1)} ${e.y.toFixed(1)}`;
};

/** floor circle as a polygon path */
export const floorCircle = (pr: Projector, c: V2, r: number, n = 28, z = 0.005): string =>
  polyPath(pr, Array.from({length: n}, (_, i) => [c[0] + r * Math.cos((i / n) * 2 * Math.PI), c[1] + r * Math.sin((i / n) * 2 * Math.PI), z] as V3));
