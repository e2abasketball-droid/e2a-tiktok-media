// E2A Realism V3.3 (2026-11-22) — anatomical ball-body volumes, shared by the contact solver (motion33.clearBall) and the QC (added NEXT TO the original V3.2 capsule
// detector, which is kept unchanged as the reference). Radii = MEDIAN (P50) distance of the skin + garment vertices of
// each region to its bone axis, measured on public/players3d/e2a_player_off_v32.glb with bpy
// (produccion/realism-v3-3/qa/anat_radii_off.json, script tools/blender/measure_anat_v33.py):
//   trunk  elliptic section: front 0.150 m, back 0.105 m, lateral 0.185 m (hips -> neck)
//   upper arm 0.068 -> 0.052, forearm 0.044 -> 0.030 (elbow -> wrist), thigh 0.123 -> 0.085, head 0.115
// depth = how far the ball surface is inside that median surface (m); > 0 = contact or penetration.
import type {V3} from '../../tactical/geometry.ts';

export const ANAT33 = {
  source: 'bpy P50 vertex-to-bone distance, e2a_player_off_v32.glb (skin + garments, dominant weight >= 0.5)',
  trunk: {front: 0.15, back: 0.105, lateral: 0.185},
  upperarm: [0.068, 0.052], forearm: [0.044, 0.03], thigh: [0.123, 0.085], head: 0.115, ballR: 0.121,
};
const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const mul = (a: V3, k: number): V3 => [a[0] * k, a[1] * k, a[2] * k];
const dot = (a: V3, b: V3) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const len = (a: V3) => Math.hypot(a[0], a[1], a[2]);
const norm = (a: V3): V3 => mul(a, 1 / Math.max(1e-9, len(a)));

const tapered = (p: V3, a: V3, b: V3, r0: number, r1: number) => {
  const ab = sub(b, a);
  const u = Math.max(0, Math.min(1, dot(sub(p, a), ab) / Math.max(1e-9, dot(ab, ab))));
  return {d: len(sub(p, add(a, mul(ab, u)))), r: r0 + (r1 - r0) * u};
};

/** every region the ball (centre p) touches or enters, with its depth */
export const anatomicalHits = (J: Record<string, V3>, p: V3, minDepth = 0): {region: string; depth: number}[] => {
  const R = ANAT33.ballR;
  const out: {region: string; depth: number}[] = [];
  // trunk: elliptic section in the trunk frame (lateral = shoulder line, forward = lateral x axis)
  {
    const A = J.pelvis, B = J.neck;
    const ax = sub(B, A);
    const u = Math.max(0, Math.min(1, dot(sub(p, A), ax) / Math.max(1e-9, dot(ax, ax))));
    const c = add(A, mul(ax, u));
    const up = norm(ax);
    let lat = sub(J.shR, J.shL);
    lat = norm(sub(lat, mul(up, dot(lat, up))));
    const fw = norm(cross(up, lat)); // up x right = forward (right-handed, z up)
    const d = sub(p, c);
    const x = dot(d, lat), y = dot(d, fw);
    const L = Math.hypot(x, y);
    if (L > 1e-6) {
      const ry = y >= 0 ? ANAT33.trunk.front : ANAT33.trunk.back;
      const rx = ANAT33.trunk.lateral;
      // ellipse radius along the direction (x, y)
      const re = 1 / Math.sqrt((x / L) ** 2 / rx ** 2 + (y / L) ** 2 / ry ** 2);
      const depth = re + R - L;
      // above the neck end / below the hips the capsule cap is spherical with the lateral radius
      if (depth > minDepth && u > 0 && u < 1) out.push({region: 'trunk', depth});
    }
  }
  const caps: [string, V3, V3, number, number][] = [
    ['head', J.neck, add(J.head, [0, 0, 0.08]), ANAT33.head, ANAT33.head],
    ['upperarmL', J.shL, J.elL, ANAT33.upperarm[0], ANAT33.upperarm[1]], ['upperarmR', J.shR, J.elR, ANAT33.upperarm[0], ANAT33.upperarm[1]],
    ['forearmL', J.elL, J.wrL, ANAT33.forearm[0], ANAT33.forearm[1]], ['forearmR', J.elR, J.wrR, ANAT33.forearm[0], ANAT33.forearm[1]],
    ['thighL', J.hipL, J.knL, ANAT33.thigh[0], ANAT33.thigh[1]], ['thighR', J.hipR, J.knR, ANAT33.thigh[0], ANAT33.thigh[1]],
  ];
  for (const [nm, a, b, r0, r1] of caps) {
    const q = tapered(p, a, b, r0, r1);
    const depth = q.r + R - q.d;
    if (depth > minDepth) out.push({region: nm, depth});
  }
  return out;
};
