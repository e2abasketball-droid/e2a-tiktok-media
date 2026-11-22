// E2A 3D engine — GARMENT3 apparel corrections (Chicago V3 brief sec. 9, 2026-11-22, opt-in play.realism >= 3).
// Works on the v2 apparel meshes (tools/blender/build_player.py --garment v2) at load time, no new GLB, no cloth solver,
// same frame for every process (pure function of the bind-pose arrays) -> deterministic in the parallel render.
//   tuck     the part of the SHORTS that is covered by the jersey (bind pose: inside the shirt, above its hem band)
//            follows the PELVIS (75 % hips weight) instead of the thighs and sits 1.2 cm further in: on a high knee the
//            thigh-weighted waist of the shorts no longer pushes through the shirt (qc-realism cloth_clip "shorts through
//            the jersey": 6.8 cm in V2). Hidden under the shirt by construction, so it cannot show.
//   leg      the leg openings of the shorts are cut looser, A-line (outward along the normal, 0 -> 2.8 cm over the last 13 cm) and that
//            band gets a cloth weight (_e2a_hem) so the openings swing with the same deterministic spring as the jersey
//            (cloth2.ts) at half amplitude, with the stride flutter: shorts read as loose mesh fabric, not leg tubes.
//   trim     piping (shorts trim) follows the nearest shorts vertex (same displacement, same weights): no gap at the hem.
//   panel    (cloth2 option) the jersey hem flares MORE on the side it swings toward and presses less on the other side,
//            instead of translating as a rigid ring (V2 close-ups: "a slightly rigid bell").
// Coordinates: GLB/three frame (y up) when up = 1, play frame (z up) when up = 2 (qc-realism). Mirrored in GLSL in
// SkinnedAthlete (cloth2Material v3) and on the CPU in qc-realism.
export const GARMENT3 = {tuckK: 0.75, tuckIn: 0.012, tuckBand0: 0.025, tuckBand: 0.03, coverD: 0.06, legFlare: 0.028, legBand: 0.13, legSway: 0.5, panel: 0.3, panelRef: 0.02};

type Arr = {P: Float32Array; N: Float32Array; J?: ArrayLike<number>; W?: Float32Array};
export type G3Out = {P: Float32Array; J: Uint16Array; W: Float32Array; hem: Float32Array; ease: Float32Array; delta: Float32Array};

const nearest = (P: Float32Array, n: number, x: number, y: number, z: number) => {
  let best = 1e9, bi = 0;
  for (let j = 0; j < n; j++) {
    const d = (P[j * 3] - x) ** 2 + (P[j * 3 + 1] - y) ** 2 + (P[j * 3 + 2] - z) ** 2;
    if (d < best) { best = d; bi = j; }
  }
  return {i: bi, d: Math.sqrt(best)};
};

/** add k of `bone` to a 4-slot weight set (keeps the 4 largest, renormalised) */
const addWeight = (J: ArrayLike<number>, W: Float32Array, v: number, bone: number, k: number, oJ: Uint16Array, oW: Float32Array) => {
  const m = new Map<number, number>();
  for (let c = 0; c < 4; c++) if (W[v * 4 + c] > 0) m.set(J[v * 4 + c], (m.get(J[v * 4 + c]) ?? 0) + W[v * 4 + c] * (1 - k));
  m.set(bone, (m.get(bone) ?? 0) + k);
  const top = [...m.entries()].sort((a, b) => b[1] - a[1]).slice(0, 4);
  const s = top.reduce((a, b) => a + b[1], 0) || 1;
  for (let c = 0; c < 4; c++) {
    oJ[v * 4 + c] = top[c]?.[0] ?? 0;
    oW[v * 4 + c] = (top[c]?.[1] ?? 0) / s;
  }
};

/** the corrected SHORTS (positions, weights, cloth band) from the bind-pose jersey and shorts */
export const garment3Shorts = (jersey: Arr, shorts: Arr, hipsBone: number, up = 1): G3Out => {
  const G = GARMENT3;
  const nj = jersey.P.length / 3, ns = shorts.P.length / 3;
  const h0 = up === 1 ? 0 : 0, h1 = up === 1 ? 2 : 1;
  let hemUp = 1e9;
  for (let j = 0; j < nj; j++) hemUp = Math.min(hemUp, jersey.P[j * 3 + up]);
  const P = new Float32Array(shorts.P), J = new Uint16Array(ns * 4), W = new Float32Array(ns * 4);
  for (let i = 0; i < ns * 4; i++) { J[i] = shorts.J![i]; W[i] = shorts.W![i]; }
  const hem = new Float32Array(ns), ease = new Float32Array(ns), delta = new Float32Array(ns * 3);
  // leg openings: lowest shorts vertex on each side (x sign)
  const bottom = [1e9, 1e9];
  for (let v = 0; v < ns; v++) {
    const s = shorts.P[v * 3] < 0 ? 0 : 1;
    bottom[s] = Math.min(bottom[s], shorts.P[v * 3 + up]);
  }
  for (let v = 0; v < ns; v++) {
    const x = shorts.P[v * 3], y = shorts.P[v * 3 + 1], z = shorts.P[v * 3 + 2];
    const nx = shorts.N[v * 3], ny = shorts.N[v * 3 + 1], nz = shorts.N[v * 3 + 2];
    const hgt = shorts.P[v * 3 + up];
    // tuck: covered by the shirt in bind (nearest jersey vertex close, shorts vertex on its inner side), above the hem band
    const q = nearest(jersey.P, nj, x, y, z);
    const sd = (x - jersey.P[q.i * 3]) * jersey.N[q.i * 3] + (y - jersey.P[q.i * 3 + 1]) * jersey.N[q.i * 3 + 1] + (z - jersey.P[q.i * 3 + 2]) * jersey.N[q.i * 3 + 2];
    const band = Math.max(0, Math.min(1, (hgt - (hemUp + G.tuckBand0)) / G.tuckBand));
    const tuck = q.d < G.coverD && sd < 0 ? band : 0;
    let dx = 0, dy = 0, dz = 0;
    if (tuck > 0) {
      addWeight(shorts.J!, shorts.W!, v, hipsBone, G.tuckK * tuck, J, W);
      dx -= nx * G.tuckIn * tuck; dy -= ny * G.tuckIn * tuck; dz -= nz * G.tuckIn * tuck;
    }
    // leg band: looser opening + cloth weight
    const s = x < 0 ? 0 : 1;
    const lh = hgt < hemUp ? Math.max(0, Math.min(1, 1 - (hgt - bottom[s]) / G.legBand)) : 0;
    if (lh > 0) {
      const hn = [shorts.N[v * 3 + h0], shorts.N[v * 3 + h1]], hl = Math.hypot(hn[0], hn[1]);
      if (hl > 1e-6) {
        const o = [0, 0, 0];
        o[h0] = (hn[0] / hl) * G.legFlare * lh;
        o[h1] = (hn[1] / hl) * G.legFlare * lh;
        dx += o[0]; dy += o[1]; dz += o[2];
      }
      hem[v] = G.legSway * lh;
      ease[v] = G.legFlare * lh + 0.004;
    }
    P[v * 3] += dx; P[v * 3 + 1] += dy; P[v * 3 + 2] += dz;
    delta[v * 3] = dx; delta[v * 3 + 1] = dy; delta[v * 3 + 2] = dz;
  }
  return {P, J, W, hem, ease, delta};
};

/** a trim (piping) that follows its nearest shorts vertex: same displacement, weights and cloth band */
export const garment3Follow = (trim: Arr, shorts: Arr, g: G3Out): G3Out => {
  const nt = trim.P.length / 3, ns = shorts.P.length / 3;
  const P = new Float32Array(trim.P), J = new Uint16Array(nt * 4), W = new Float32Array(nt * 4);
  const hem = new Float32Array(nt), ease = new Float32Array(nt), delta = new Float32Array(nt * 3);
  for (let v = 0; v < nt; v++) {
    const q = nearest(shorts.P, ns, trim.P[v * 3], trim.P[v * 3 + 1], trim.P[v * 3 + 2]);
    for (let c = 0; c < 3; c++) { P[v * 3 + c] += g.delta[q.i * 3 + c]; delta[v * 3 + c] = g.delta[q.i * 3 + c]; }
    for (let c = 0; c < 4; c++) { J[v * 4 + c] = g.J[q.i * 4 + c]; W[v * 4 + c] = g.W[q.i * 4 + c]; }
    hem[v] = g.hem[q.i];
    ease[v] = g.ease[q.i];
  }
  return {P, J, W, hem, ease, delta};
};

/** panel factor of the jersey hem swing (cloth2 v3): r = vertex - pelvis (horizontal), s = horizontal sway */
export const panelFactor = (rx: number, ry: number, sx: number, sy: number) => {
  const sl = Math.hypot(sx, sy), rl = Math.hypot(rx, ry);
  if (sl < 1e-5 || rl < 1e-5) return 1;
  return 1 + GARMENT3.panel * ((rx * sx + ry * sy) / (rl * sl)) * Math.min(1, sl / GARMENT3.panelRef);
};
