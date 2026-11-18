// E2A 3D engine — QC of the default player meshes (player3d.ts) on a play without rendering: forward kinematics of
// the mesh skeleton from the same bone rotations the render uses (Scene3D), against the engine pose. Pure (no fs):
// used by scripts/qc-players3d.mts and scripts/qc-tactical3d.mts. Needs the rigs and clips registered.
import {FIBA} from '../tactical/geometry.ts';
import type {V3} from '../tactical/geometry.ts';
import {sample} from '../tactical/play.ts';
import {poseAt} from './rig.ts';
import type {PlayWithActions} from './rig.ts';
import {bonesFromPose, getClip, meshScale, qconj, qrot, skelPoseAt} from './skelclip.ts';
import type {ClipBone, Q} from './skelclip.ts';
import {PLAYER3D, planPlayers3d, playWithPlan} from './player3d.ts';
import type {PlanOpts} from './player3d.ts';

export const meshQC = (play: PlayWithActions, fps = 30, opts: PlanOpts = {}) => {
  const plan = planPlayers3d(play, opts);
  const playP = playWithPlan(play, opts);
  const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];

  const sub = (a: V3, b: V3): V3 => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const add = (a: V3, b: V3): V3 => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const dist = (a: V3, b: V3) => Math.hypot(a[0] - b[0], a[1] - b[1], a[2] - b[2]);
  const fk = (bones: ClipBone[], rot: Record<string, Q>, hips: V3, s: number) => {
    const P: Record<string, V3> = {[bones[0].name]: hips};
    const by = Object.fromEntries(bones.map((b) => [b.name, b]));
    for (const b of bones) {
      if (!b.parent) continue;
      const p = by[b.parent];
      const local = qrot(qconj(p.R), sub(b.head, p.head));
      P[b.name] = add(P[b.parent], qrot(rot[b.parent], [local[0] * s, local[1] * s, local[2] * s]));
    }
    return P;
  };
  const facePitch = (q: Q) => {
    const z = qrot(q, [0, 0, 1]);
    return (Math.asin(Math.max(-1, Math.min(1, z[2]))) * 180) / Math.PI;
  };

  type W = {v: number; at: string};
  const worst: Record<string, W> = {ankle: {v: 0, at: ''}, slide: {v: 0, at: ''}, wrist: {v: 0, at: ''}, reach: {v: 0, at: ''}, headUp: {v: -99, at: ''}, headDown: {v: 99, at: ''}, seek: {v: 0, at: ''}};
  const upd = (k: string, v: number, at: string, max = true) => {
    if (max ? v > worst[k].v : v < worst[k].v) worst[k] = {v, at};
  };
  const prev: Record<string, {eng: V3[]; mesh: V3[]}> = {};
  const n = Math.floor(play.duration * fps);
  for (let f = 0; f <= n; f++) {
    const t = f / fps;
    const b = sample(play, t).ball;
    const ballLag = sample(play, Math.max(0, t - 0.2)).ball.pos;
    for (const p of play.players) {
      const pp = plan[p.id];
      if (pp.look !== 'C') continue;
      const pkg = PLAYER3D[pp.variant];
      const rig = pkg.rig!;
      let bones: Record<string, Q>;
      let hips: V3;
      let desc: ClipBone[];
      let s = 1;
      let eng;
      if (pp.clip) {
        const sp = skelPoseAt(playP, p.id, t, {holder: b.holder, pos: b.pos, lag: ballLag}, RIM, true);
        bones = sp.bones!;
        hips = sp.hips!;
        desc = getClip(pp.clip)!.bones;
        eng = sp.pose;
        const again = skelPoseAt(playP, p.id, t, {holder: b.holder, pos: b.pos, lag: ballLag}, RIM, true);
        upd('seek', Math.max(...Object.keys(bones).map((k) => Math.max(...bones[k].map((x, j) => Math.abs(x - again.bones![k][j]))))), `${p.id}@${t.toFixed(2)}`);
      } else {
        eng = poseAt(play, p.id, t, {holder: b.holder, pos: b.pos, lag: ballLag}, RIM);
        s = meshScale(rig, eng);
        const r = bonesFromPose(rig, eng, s);
        bones = r.bones;
        hips = r.hips;
        desc = rig.bones;
        const r2 = bonesFromPose(rig, poseAt(play, p.id, t, {holder: b.holder, pos: b.pos, lag: ballLag}, RIM), s);
        upd('seek', Math.max(...Object.keys(bones).map((k) => Math.max(...bones[k].map((x, j) => Math.abs(x - r2.bones[k][j]))))), `${p.id}@${t.toFixed(2)}`);
      }
      const J = fk(desc, bones, hips, s);
      const at = `${p.id}@${t.toFixed(2)}s`;
      const mesh: V3[] = [J['foot.L'], J['foot.R']];
      const aOff = pp.clip ? 0 : rig.restJoints.ankleL[2] * s - eng.dims.ankleH; // soles on the floor: the mesh ankle sits higher
      const engA: V3[] = [add(eng.ankle[0], [0, 0, aOff]), add(eng.ankle[1], [0, 0, aOff])];
      if (!pp.clip) {
        for (let i = 0; i < 2; i++) upd('ankle', dist(mesh[i], engA[i]) * 1000, at);
        // mesh fingertip (hand bone head + rest wrist->tip offset rotated by the hand bone) vs the engine hand point
        for (let i = 0; i < 2; i++) {
          const sd = i ? 'R' : 'L';
          const hb = desc.find((x) => x.name === `hand.${sd}`)!;
          const off = qrot(qconj(hb.R), sub(rig.restJoints[`hand${sd}`], rig.restJoints[`wrist${sd}`]));
          const tip = add(J[`hand.${sd}`], qrot(bones[`hand.${sd}`], [off[0] * s, off[1] * s, off[2] * s]));
          if (b.holder === p.id) upd('wrist', dist(tip, eng.hand[i]) * 1000, at);
        else upd('reach', dist(tip, eng.hand[i]) * 1000, at);
        }
      }
      const pr = prev[p.id];
      if (pr) for (let i = 0; i < 2; i++) if (dist(engA[i], pr.eng[i]) < 0.0005 && engA[i][2] < 0.2) upd('slide', dist(mesh[i], pr.mesh[i]) * 1000, at);
      prev[p.id] = {eng: engA, mesh};
      const hp = facePitch(bones.head);
      const shooting = play.ball.some((e) => (e.type === 'shot' || e.type === 'layup') && t >= e.t0 - 0.6 && t <= e.t1 + 0.6);
      upd('headUp', hp - (shooting ? 20 : 0), at);
      upd('headDown', hp, at, false);
    }
  }
  const checks = [
    ['mesh ankle on the engine ankle (≤ 15 mm)', worst.ankle.v <= 15, `${worst.ankle.v.toFixed(1)} mm (${worst.ankle.at})`],
    ['planted mesh foot does not slide (≤ 2 mm/frame)', worst.slide.v <= 2, `${worst.slide.v.toFixed(2)} mm/frame (${worst.slide.at})`],
    ['ball holder: mesh fingertips on the engine hand point (≤ 40 mm)', worst.wrist.v <= 40, `${worst.wrist.v.toFixed(1)} mm (${worst.wrist.at})`],
    ['other players: fingertips vs engine hand (info, arms at full stretch clamp)', true, `${worst.reach.v.toFixed(1)} mm (${worst.reach.at})`],
    ['head never looks up (face pitch ≤ +15°, +35° while a shot is up)', worst.headUp.v <= 15, `${worst.headUp.v.toFixed(1)}° (${worst.headUp.at})`],
    ['head not buried (face pitch ≥ -35°)', worst.headDown.v >= -35, `${worst.headDown.v.toFixed(1)}° (${worst.headDown.at})`],
    ['same time, same bones (seek = playback)', worst.seek.v < 1e-9, `${worst.seek.v.toExponential(1)}`],
  ] as const;

  return {plan, worst, checks};
};
