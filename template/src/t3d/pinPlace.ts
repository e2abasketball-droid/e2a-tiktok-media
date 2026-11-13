// Pin placement (V2, 2026-11-13): a label pinned to a player must point at THAT player and never sit on
// another one. The anchor is the real head of the posed body (not a fixed 2.25 m, which in high cameras
// floated the label onto the player behind: the "X5 over #4" bug of RAM Screen V1). Candidates: above the
// head, then below the feet; the first that covers no other body wins (else the least covered).
import type {V2, V3} from '../tactical/geometry.ts';
import {FIBA} from '../tactical/geometry.ts';
import {posAt, sample} from '../tactical/play.ts';
import type {PlayWithActions} from './rig.ts';
import {poseAt} from './rig.ts';

type Proj = (p: V3) => {x: number; y: number; visible?: boolean};
const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];
export type PinPlace = {x: number; y: number; dy: number; dx: number; box: [number, number, number, number]; cover: number; on: string | null};

const bodyBox = (play: PlayWithActions, id: string, pt: number, proj: Proj, ball: {holder?: string; pos: V3}) => {
  const pose = poseAt(play, id, pt, ball, RIM);
  const p = posAt(play.tracks[id], pt) as V2;
  const f = proj([p[0], p[1], 0]);
  const h = proj([p[0], p[1], pose.head[2] + 0.12]);
  const half = Math.max(18, Math.abs(f.y - h.y) * 0.2);
  return {head: h, feet: f, box: [Math.min(f.x, h.x) - half, Math.min(f.y, h.y), Math.max(f.x, h.x) + half, Math.max(f.y, h.y)] as [number, number, number, number]};
};

const overlap = (a: number[], b: number[]) => Math.max(0, Math.min(a[2], b[2]) - Math.max(a[0], b[0])) * Math.max(0, Math.min(a[3], b[3]) - Math.max(a[1], b[1]));

export const placePin = (play: PlayWithActions, id: string, pt: number, proj: Proj, text: string, size = 40, dyWanted?: number, zFixed?: number, only?: number): PinPlace => {
  const t = Math.max(0, Math.min(play.duration, pt));
  const ball = sample(play, t).ball;
  const me = bodyBox(play, id, t, proj, ball);
  const others = play.players.filter((q) => q.id !== id).map((q) => ({id: q.id, ...bodyBox(play, q.id, t, proj, ball)}));
  const w = text.length * size * 0.66 + 38;
  const hgt = size * 1.45 + 12;
  const cands: {x: number; y: number; dy: number; dx: number}[] = [];
  if (zFixed !== undefined) {
    const p = posAt(play.tracks[id], t) as V2;
    const q = proj([p[0], p[1], zFixed]);
    cands.push({x: q.x, y: q.y, dy: dyWanted ?? -40, dx: 0});
  } else {
    const midY = (me.head.y + me.feet.y) / 2;
    cands.push({x: me.head.x, y: me.head.y, dy: dyWanted ?? -36, dx: 0});
    // beside the chest, on the side with more room, then the other side, then under the feet
    const firstRight = me.head.x < 540;
    for (const sgn of firstRight ? [1, -1] : [-1, 1]) cands.push({x: me.head.x, y: midY - hgt / 2, dy: hgt / 2 + 6, dx: sgn * (w / 2 + (me.box[2] - me.box[0]) / 2 + 22)});
    cands.push({x: me.feet.x, y: me.feet.y, dy: hgt + 30, dx: 0});
  }
  let best: PinPlace | null = null;
  const list = only !== undefined ? [cands[Math.min(only, cands.length - 1)]] : cands;
  for (const c of list) {
    const ty = Math.max(220 + size * 1.5, c.y + c.dy);
    const cx = Math.min(Math.max(c.x + c.dx, 40 + w / 2), 1040 - w / 2);
    const box: [number, number, number, number] = [cx - w / 2, ty - hgt, cx + w / 2, ty];
    let cover = 0;
    let on: string | null = null;
    for (const o of others) {
      const a = overlap(box, o.box) / (w * hgt);
      if (a > cover) [cover, on] = [a, o.id];
    }
    // the label must not cover its own player either (side placement)
    const self = c.dx !== 0 ? overlap(box, me.box) / (w * hgt) : 0;
    if (only === undefined && self > 0.08) continue;
    if (self > cover) [cover, on] = [self, null];
    const cand = {x: c.x, y: c.y, dy: c.dy, dx: c.dx, box, cover, on: cover > 0.08 ? on : null};
    if (!best || cand.cover < best.cover - 0.02) best = cand;
    if (cover <= 0.08) break;
  }
  return best!;
};

/** one placement for the whole life of a pin (no jumping between spots): the candidate whose worst sample
 *  covers the least, evaluated over `samples` = [{pt, proj}] spread across the pin's time window. */
export const choosePin = (play: PlayWithActions, id: string, samples: {pt: number; proj: Proj}[], text: string, size = 40, dyWanted?: number, zFixed?: number): number => {
  if (zFixed !== undefined) return 0;
  let bestI = 0, bestCover = Infinity;
  for (let i = 0; i < 4; i++) {
    let worst = 0;
    for (const sm of samples) {
      const r = placePin(play, id, sm.pt, sm.proj, text, size, dyWanted, zFixed, i);
      worst = Math.max(worst, r.cover);
    }
    if (worst < bestCover - 0.02) [bestI, bestCover] = [i, worst];
    if (worst <= 0.08) break;
  }
  return bestI;
};
