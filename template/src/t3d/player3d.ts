// E2A 3D engine — DEFAULT PLAYER PACKAGE (2026-11-19, e2a-player-v1).
// Every Tactical3D / Tactical3DV2 scene draws its players with the deformable E2A player (skinned MakeHuman-based mesh,
// offense and defense variants, public/players3d/*.glb) unless something prevents it; then it falls back to the
// procedural capsule athlete (Athlete.tsx, look 'A') and the reason is reported (console in the render log,
// scripts/qc-tactical3d.mts "players3d" section, scripts/players3d-plan.mts).
//
// Which animation drives each player (pure function of the play, no state):
//   1. play.skel[id]                      explicit clip (lab plays; look 'A' there = keep the capsule for that player)
//   2. CLIP_LIBRARY, auto                 a validated clip whose action pattern the player performs AND whose placement
//                                         fits the play geometry (rotation the engine must add to the clip ≤ limits)
//   3. compatible rig animation           the procedural rig / authored choreography pose (rig.ts / choreo.ts)
//                                         re-solved onto the mesh skeleton (skelclip.bonesFromPose)
// Opt-outs (data, never a prompt reminder): episode.players3d = 'A' (legacy look), shot.players3d = 'A', or
// episode.faces (character episodes with stylised faces keep the capsule head rig: the mesh has a neutral face).
import type {PlayWithActions} from './rig.ts';
import {actionsOf} from './rig.ts';
import type {PlayWithSkel, SkelRig, SkelSpec} from './skelclip.ts';
import {getClip, skelPlan} from './skelclip.ts';

export type PlayerRig = SkelRig & {version: string; variant: 'off' | 'def'; H: number; kit: Record<string, string>; source: string};
// rigs are registered by ./players/index.ts in the bundle (JSON imports) and by the node QC scripts (fs)
const RIGS: Partial<Record<'off' | 'def', PlayerRig>> = {};
export const registerPlayerRig = (v: 'off' | 'def', r: PlayerRig) => {
  RIGS[v] = r;
};
export const PLAYER3D = {
  version: 'e2a-player-v1',
  off: {glb: 'players3d/e2a_player_off.glb', rigFile: 'src/t3d/players/e2a-off.rig.json', get rig() { return RIGS.off; }},
  def: {glb: 'players3d/e2a_player_def.glb', rigFile: 'src/t3d/players/e2a-def.rig.json', get rig() { return RIGS.def; }},
};

/** validated clips by action pattern (see tactical/reports/3d-animation-mpfb-2026-11-19/INFORME.md, clip register) */
export type ClipEntry = {clip: string; pattern: string[]; side: 'left' | 'right'; validated: string; maxAddDeg: number};
export const CLIP_LIBRARY: ClipEntry[] = [
  // screen then roll, pivot on the right ball, opens to his LEFT (5452 mirrored, = 5451's side)
  {clip: 'screen-roll-5452m', pattern: ['screen', 'roll'], side: 'left', validated: '2026-11-19 screen-roll-lab qc-contact 1.45 mm', maxAddDeg: 35},
  // same take unmirrored: pivot on the left ball, opens to his RIGHT
  {clip: 'screen-roll-5452', pattern: ['screen', 'roll'], side: 'right', validated: '2026-11-19 placement only (no lab play on that side yet)', maxAddDeg: 35},
];

export type Look = 'A' | 'B' | 'C';
export type PlayerPlan = {id: string; look: Look; variant: 'off' | 'def'; clip?: string; anim: 'clip' | 'rig' | 'choreo'; reason?: string};
export type PlanOpts = {force?: 'A' | 'C'; faces?: boolean};

const planCache = new WeakMap<object, Map<string, Record<string, PlayerPlan>>>();

/** try a library clip on a player: returns the spec if its placement fits the play, else the reason */
const tryClip = (play: PlayWithActions, id: string, e: ClipEntry): {spec?: SkelSpec; why?: string} => {
  if (!getClip(e.clip)) return {why: `${e.clip}: clip data not loaded`};
  const probe = {...play, skel: {...((play as PlayWithSkel).skel ?? {}), [id]: {clip: e.clip, look: 'C' as const}}} as PlayWithSkel;
  const plan = skelPlan(probe, id);
  if (!plan) return {why: `${e.clip}: no plan (needs ${e.pattern.join('+')})`};
  const th = plan.info as Record<string, number>;
  const wrapDeg = (d: number) => ((((d + 180) % 360) + 360) % 360) - 180;
  const add = Math.abs(wrapDeg(th.thetaRunDeg - th.thetaHoldDeg));
  const app = Math.abs(wrapDeg(th.thetaApproachDeg - th.thetaHoldDeg));
  if (add > e.maxAddDeg) return {why: `${e.clip}: the play turns ${add.toFixed(0)}° more than the take (limit ${e.maxAddDeg}°)`};
  if (app > 60) return {why: `${e.clip}: approach ${app.toFixed(0)}° off the take`};
  return {spec: {clip: e.clip, look: 'C'}};
};

/** per-player plan for one play (cached per play object and options) */
export const planPlayers3d = (play: PlayWithActions, opts: PlanOpts = {}): Record<string, PlayerPlan> => {
  const key = `${opts.force ?? ''}|${opts.faces ? 1 : 0}`;
  let m = planCache.get(play);
  if (!m) planCache.set(play, (m = new Map()));
  const hit = m.get(key);
  if (hit) return hit;
  const out: Record<string, PlayerPlan> = {};
  const skel = (play as PlayWithSkel).skel ?? {};
  const choreo = (play as unknown as {choreo?: Record<string, unknown>}).choreo ?? {};
  for (const p of play.players) {
    const variant = p.team === 'X' ? 'def' : 'off';
    const anim0: PlayerPlan['anim'] = choreo[p.id] ? 'choreo' : 'rig';
    if (opts.force === 'A') {
      out[p.id] = {id: p.id, look: 'A', variant, anim: anim0, reason: 'players3d = A (legacy look requested in the data)'};
      continue;
    }
    if (opts.faces) {
      out[p.id] = {id: p.id, look: 'A', variant, anim: anim0, reason: 'episode.faces: stylised face expressions need the capsule head rig (the E2A mesh has a neutral face)'};
      continue;
    }
    const sp = skel[p.id];
    if (sp) {
      out[p.id] = {id: p.id, look: sp.look ?? 'C', variant, clip: sp.look === 'A' ? undefined : sp.clip, anim: sp.look === 'A' ? anim0 : 'clip', reason: sp.look === 'A' ? 'play.skel look A' : undefined};
      continue;
    }
    // automatic clip choice by action pattern
    const types = actionsOf(play, p.id).map((a) => a.type as string);
    const cands = CLIP_LIBRARY.filter((e) => e.pattern.every((t) => types.includes(t)));
    let chosen: SkelSpec | undefined;
    const whys: string[] = [];
    if (!choreo[p.id]) {
      for (const e of cands) {
        const r = tryClip(play, p.id, e);
        if (r.spec) {
          chosen = r.spec;
          break;
        }
        whys.push(r.why!);
      }
    }
    if (chosen) out[p.id] = {id: p.id, look: 'C', variant, clip: chosen.clip, anim: 'clip'};
    else out[p.id] = {id: p.id, look: 'C', variant, anim: anim0, reason: whys.length ? `no validated clip fits (${whys.join('; ')}): compatible rig animation` : undefined};
  }
  m.set(key, out);
  return out;
};

/** the play with the automatically chosen clips written into play.skel (what Scene3D / qc-contact consume) */
const withCache = new WeakMap<object, Map<string, PlayWithSkel>>();
export const playWithPlan = (play: PlayWithActions, opts: PlanOpts = {}): PlayWithSkel => {
  const key = `${opts.force ?? ''}|${opts.faces ? 1 : 0}`;
  let m = withCache.get(play);
  if (!m) withCache.set(play, (m = new Map()));
  const hit = m.get(key);
  if (hit) return hit;
  const plan = planPlayers3d(play, opts);
  const skel: Record<string, SkelSpec> = {...((play as PlayWithSkel).skel ?? {})};
  for (const pp of Object.values(plan)) if (pp.clip && !skel[pp.id]) skel[pp.id] = {clip: pp.clip, look: pp.look};
  const out = Object.keys(skel).length ? ({...play, skel} as PlayWithSkel) : (play as PlayWithSkel);
  m.set(key, out);
  return out;
};

/** one line per player for logs / QC reports */
export const describePlan = (plan: Record<string, PlayerPlan>) =>
  Object.values(plan).map((p) => `${p.id}:${p.look}${p.look !== 'A' ? `/${p.variant}` : ''}/${p.clip ?? p.anim}${p.reason ? ` (${p.reason})` : ''}`);
