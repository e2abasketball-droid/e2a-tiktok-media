// E2A 3D engine — one 3D viewport of a play at a given play time: court, lights, ten animated
// athletes, ball, world-space tactical graphics, and the camera.
import React from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {FIBA} from '../tactical/geometry.ts';
import type {V3} from '../tactical/geometry.ts';
import {posAt, realismV2, realismV3, sample} from '../tactical/play.ts';
import {clothAt} from './cloth2.ts';
import {Athlete, SKINS, W3} from './Athlete';
import type {FaceState} from './Athlete';
import {ArenaLights, Court3D, type SceneEnv} from './Court3D';
import type {PlayWithActions} from './rig.ts';
import {poseAt} from './rig.ts';
import type {Cam3} from './camera3d.ts';
import {CLIP_GLB} from './clips/index.ts';
import './players/index.ts'; // side effect: registers the player rigs
import type {PlayWithSkel} from './skelclip.ts';
import {bonesFromPose, getClip, meshScale, skelPoseAt} from './skelclip.ts';
import {SkinnedAthlete, useGlbs} from './SkinnedAthlete';
import {KITS} from './Athlete';
import {PLAYER3D, describePlan, planPlayers3d, playWithPlan} from './player3d.ts';
import {PLAYER3D_V3, isV3, isV31, isV32, isV33} from './realism-v3/index.ts';
import {PLAYER3D_V33, athleteV33, ballV33} from './realism-v3-3/index.ts';
import {PLAYER3D_V32} from './realism-v3-2/index.ts';
import {athleteV32} from './realism-v3-2/scene32.ts';
import type {Athlete32, Motion} from './realism-v3-2/scene32.ts';
import {ballV32} from './realism-v3-2/motion32.ts';
import {PLAYER3D_V31} from './realism-v3-1/index.ts';
import {ballV31, clothV31, framesV31, motionV31} from './realism-v3-1/motion.ts';
import type {AthleteRenderer} from './realism-v3/index.ts';
import {bonesV3, weightShift} from './realism-v3/athleteV3.ts';

/** render log (once per tab and play): which character / animation each player uses and why */
const logged = new Set<string>();
const logPlan = (msg: string) => {
  if (logged.has(msg)) return;
  logged.add(msg);
  console.warn(msg);
};

const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];

/** where an expression's `look` points (2026-11-17 V3): 'ball' (default), a player id (his head), 'rim', or 'down'
 *  (the floor a metre in front, between the player and the ball). Undefined = the ball. */
const lookPoint = (play: PlayWithActions, look: string | undefined, pt: number, ballPos: V3, head: V3): V3 | undefined => {
  if (!look || look === 'ball') return undefined;
  if (look === 'rim') return RIM;
  if (look === 'down') {
    const dx = ballPos[0] - head[0];
    const dy = ballPos[1] - head[1];
    const d = Math.max(0.3, Math.hypot(dx, dy));
    return [head[0] + (dx / d) * 1.0, head[1] + (dy / d) * 1.0, 0.05];
  }
  if (!play.tracks[look]) return undefined;
  const q = posAt(play.tracks[look], Math.max(0, Math.min(play.duration, pt)));
  return [q[0], q[1], head[2]];
};
const exprOf = (play: PlayWithActions, id: string, t: number) => exprAt((play as PlayWithActions & {expr?: Record<string, ExprKey[]>}).expr?.[id], t);

const faceOf = (play: PlayWithActions, id: string, i: number, pt: number, ballPos: V3, head: V3, cfg: FaceCfg): FaceState => {
  const e = exprOf(play, id, pt);
  const gaze: V3 = lookPoint(play, e.look, pt, ballPos, head) ?? ballPos;
  return {gaze, brow: e.brow, smile: e.smile, open: e.open, blink: Math.max(e.blink, autoBlink(i, pt)), headScale: cfg.headScale ?? 1.3, hair: cfg.hair?.[id] ?? '#2B1A10'};
};

const CameraSync: React.FC<{cam: Cam3}> = ({cam}) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  const [px, py, pz] = W3(cam.pos);
  const [tx, ty, tz] = W3(cam.target);
  camera.position.set(px, py, pz);
  const [ux, uy, uz] = W3(cam.up);
  camera.up.set(ux, uy, uz);
  camera.lookAt(tx, ty, tz);
  if (cam.roll) camera.rotateZ((cam.roll * Math.PI) / 180);
  if (camera.fov !== cam.fov) {
    camera.fov = cam.fov;
  }
  camera.near = 0.1;
  camera.far = 120;
  camera.updateProjectionMatrix();
  return null;
};

/** V2: soft contact shadows under each shoe (darkest when the foot is planted) — the weight on the floor */
const contactTex = (() => {
  let t: THREE.Texture | null = null;
  return () => {
    if (t) return t;
    const c = document.createElement('canvas');
    c.width = c.height = 128;
    const g = c.getContext('2d')!;
    const r = g.createRadialGradient(64, 64, 4, 64, 64, 62);
    r.addColorStop(0, 'rgba(0,0,0,0.85)');
    r.addColorStop(0.5, 'rgba(0,0,0,0.35)');
    r.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = r;
    g.fillRect(0, 0, 128, 128);
    t = new THREE.CanvasTexture(c);
    return t;
  };
})();
const contactMats = new Map<number, THREE.MeshBasicMaterial>();
const ContactShadows: React.FC<{pose: ReturnType<typeof poseAt>}> = ({pose}) => {
  const out: React.ReactNode[] = [];
  for (let i = 0; i < 2; i++) {
    const a = pose.ankle[i], toe = pose.toe[i];
    const hgt = Math.max(0, Math.min(a[2], toe[2]) - 0.02);
    const op = Math.round(Math.max(0, 0.55 * (1 - hgt / 0.22)) * 20) / 20;
    if (op <= 0) continue;
    let m = contactMats.get(op);
    if (!m) {
      m = new THREE.MeshBasicMaterial({map: contactTex(), transparent: true, opacity: op, depthWrite: false, toneMapped: false});
      contactMats.set(op, m);
    }
    const mid: V3 = [(a[0] + toe[0]) / 2, (a[1] + toe[1]) / 2, 0.004];
    const yaw = Math.atan2(toe[1] - a[1], toe[0] - a[0]);
    out.push(
      <mesh key={i} position={W3(mid)} rotation={[-Math.PI / 2, 0, yaw]} material={m} renderOrder={1}>
        <planeGeometry args={[0.42, 0.22]} />
      </mesh>,
    );
  }
  return <>{out}</>;
};

const Ball: React.FC<{pos: V3; spin?: [V3, number]}> = ({pos, spin}) => {
  const tex = React.useMemo(() => {
    const c = document.createElement('canvas');
    c.width = 512;
    c.height = 256;
    const g = c.getContext('2d')!;
    g.fillStyle = '#D2652A';
    g.fillRect(0, 0, 512, 256);
    for (let i = 0; i < 4000; i++) {
      g.fillStyle = i % 2 ? 'rgba(0,0,0,0.08)' : 'rgba(255,220,180,0.06)';
      g.fillRect((i * 7919) % 512, (i * 3571) % 256, 2, 2);
    }
    g.strokeStyle = '#1a0d06';
    g.lineWidth = 6;
    [0, 128, 256, 384].forEach((x) => {
      g.beginPath();
      g.moveTo(x, 0);
      g.lineTo(x, 256);
      g.stroke();
    });
    g.beginPath();
    g.moveTo(0, 128);
    g.lineTo(512, 128);
    g.stroke();
    const t = new THREE.CanvasTexture(c);
    t.colorSpace = THREE.SRGBColorSpace;
    return t;
  }, []);
  const q = React.useMemo(() => {
    if (!spin) return new THREE.Quaternion();
    const ax = new THREE.Vector3(...W3(spin[0]));
    return ax.lengthSq() < 1e-9 ? new THREE.Quaternion() : new THREE.Quaternion().setFromAxisAngle(ax.normalize(), spin[1]);
  }, [spin]);
  return (
    <mesh position={W3(pos)} quaternion={q} castShadow>
      <sphereGeometry args={[0.121, 32, 20]} />
      <meshStandardMaterial map={tex} roughness={0.62} />
    </mesh>
  );
};

export type SceneProps = {
  play: PlayWithActions;
  pt: number;
  cam: Cam3;
  W: number;
  H: number;
  hide?: string[];
  children?: React.ReactNode; // world-space graphics (overlays3d)
  dimTeam?: 'O' | 'X';
  logo?: HTMLImageElement;
  /** 2026-11-17 character episodes: warm open practice gym vs cold full game arena (default: the arena as before);
   *  2026-11-20 'academy' look profile (Court3D SceneEnv) */
  env?: SceneEnv;
  faces?: FaceCfg;
  /** 2026-11-19: 'C' (default) = E2A deformable players (player3d.ts); 'A' = legacy capsule athletes */
  players3d?: 'A' | 'C';
  /** 2026-11-22 (Chicago V3 split screen): instance namespace so the same player can live in two canvases at once */
  instNs?: string;
  /** 2026-11-22 Realism V3: 'legacy' (default) or 'v3' (AthleteV3, realism-v3/); only the deformable players change */
  athleteRenderer?: AthleteRenderer;
  /** Realism V3.2 test switches (renderer 'v32' only): body motion source, mesh generation, neutral materials, contact debug */
  athleteMotion?: Motion;
  athleteMesh?: 'v31' | 'v32';
  neutral?: boolean;
  debug32?: boolean;
};

/** expression keys in PLAY time (so freezes and rewinds carry the face with the body) */
export type ExprKey = {t: number; brow?: number; smile?: number; open?: number; blink?: number; look?: string};
export type FaceCfg = {headScale?: number; hair?: Record<string, string>; skin?: Record<string, string>; nums?: Record<string, string>};
const EXPR_DEF = {brow: 0, smile: 0, open: 0, blink: 0};
const exprAt = (keys: ExprKey[] | undefined, t: number) => {
  const out = {...EXPR_DEF, look: undefined as string | undefined};
  if (!keys?.length) return out;
  for (const f of ['brow', 'smile', 'open', 'blink'] as const) {
    const ks = keys.filter((k) => k[f] !== undefined);
    if (!ks.length) continue;
    let v = ks[0][f] as number;
    for (let i = 0; i < ks.length; i++) {
      const a = ks[i];
      const b = ks[i + 1];
      if (t >= a.t && (!b || t < b.t)) {
        v = !b ? (a[f] as number) : (a[f] as number) + ((b[f] as number) - (a[f] as number)) * Math.min(1, Math.max(0, (t - a.t) / Math.max(1e-3, b.t - a.t)));
        break;
      }
    }
    out[f] = v;
  }
  const lk = keys.filter((k) => k.look !== undefined && k.t <= t);
  out.look = lk.length ? lk[lk.length - 1].look : undefined;
  return out;
};
/** automatic blinks: deterministic per player (period 2.6-3.8 s, 0.13 s each) */
const autoBlink = (i: number, t: number) => {
  const P = 2.6 + ((i * 0.37) % 1.2);
  const ph = (t + i * 0.83) % P;
  return ph < 0.13 ? Math.sin((Math.PI * ph) / 0.13) : 0;
};

export const Scene3D: React.FC<SceneProps> = ({play, pt, cam, W, H, hide = [], children, logo, env, faces, players3d, instNs, athleteRenderer, athleteMotion, athleteMesh, neutral, debug32}) => {
  const f = sample(play, pt);
  const ball = f.ball;
  // eyes first, head after (2026-11-17 V2): heads turn toward where the ball was 0.2 s ago, the eyes (faceOf) to where it is
  const ballLag = sample(play, Math.max(0, pt - 0.2)).ball.pos;
  // ball spin (2026-11-13): backspin in the air (shots, layups, passes), rolling forward when dribbled or
  // carried. Axis from the ball's real horizontal velocity, angle from the time spent in the event.
  const spin = ((): [V3, number] | undefined => {
    const prev = sample(play, Math.max(0, pt - 1 / 60)).ball.pos;
    const v: V3 = [(ball.pos[0] - prev[0]) * 60, (ball.pos[1] - prev[1]) * 60, 0];
    const sp = Math.hypot(v[0], v[1]);
    if (sp < 0.05) return undefined;
    const ev = ball.event as {t0?: number; t1?: number; from?: number; make?: boolean; type?: string} | undefined;
    const since = pt - (ev?.t0 ?? ev?.from ?? 0);
    if (!ball.inFlight && ev?.type === 'shot' && ev.make === false && ev.t1 !== undefined && ev.t0 !== undefined) {
      // missed shot (2026-11-17 V2): one fixed axis from the kick-out direction; the backspin carried into the ring
      // keeps turning and slowly dies (no angle jumps at each floor bounce)
      const a = sample(play, ev.t1 + 0.01).ball.pos;
      const b = sample(play, ev.t1 + 0.05).ball.pos;
      const kv: V3 = [b[0] - a[0], b[1] - a[1], 0];
      const th1 = (ev.t1 - ev.t0) * 2 * Math.PI * 2.3;
      const dt = pt - ev.t1;
      return [[-kv[1], kv[0], 0], th1 + (14 / 0.7) * (1 - Math.exp(-0.7 * dt))];
    }
    const up: V3 = [0, 0, 1];
    const cr = (a: V3, b: V3): V3 => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
    if (ball.inFlight) return [cr(v, up), since * 2 * Math.PI * (ball.inFlight === 'pass' ? 3 : 2.3)];
    return [cr(up, v), (since * sp) / 0.121];
  })();
  const swish = (() => {
    const shot = play.ball.find((e) => (e.type === 'shot' || e.type === 'layup') && e.make !== false) as {t1: number} | undefined;
    if (!shot) return 0;
    const u = (pt - shot.t1) / 0.6;
    return u > 0 && u < 1 ? u : 0;
  })();
  // DEFAULT PLAYERS (e2a-player-v1, player3d.ts): deformable E2A mesh for every player, validated clips by action,
  // compatible rig / choreo animation otherwise; capsule athlete (A) only when the data asks for it or a .glb fails
  const force = players3d === 'A' ? 'A' : undefined;
  const plan = planPlayers3d(play, {force, faces: !!faces});
  const playP = playWithPlan(play, {force, faces: !!faces});
  const skel = playP.skel;
  const anyC = !force && !faces;
  const labGlbs = skel ? [...new Set(Object.values(skel).filter((s) => s.look === 'C' && s.glb).map((s) => s.glb!))] : [];
  // Realism V2 (play.realism >= 2): v2 apparel meshes + cloth2 secondary motion; every other play keeps e2a-player-v1
  const rv2 = realismV2(play);
  const rv3 = realismV3(play);
  const av3 = isV3(athleteRenderer);
  const av31 = isV31(athleteRenderer);
  const av32 = isV32(athleteRenderer);
  // Realism V3.3 (opt-in): same V3.2 meshes, motion33 bodies and ONE ball (ballV33) for every player and the ball mesh
  const av33 = isV33(athleteRenderer);
  const PK32 = athleteMesh === 'v31' ? PLAYER3D_V31 : PLAYER3D_V32;
  const mot32: Motion = athleteMotion ?? 'v32';
  const offGlb = av33 ? PLAYER3D_V33.off.glb : av32 ? PK32.off.glb : av31 ? PLAYER3D_V31.off.glb : av3 ? PLAYER3D_V3.off.glb : rv2 ? PLAYER3D.off.glbV2 : PLAYER3D.off.glb;
  const defGlb = av33 ? PLAYER3D_V33.def.glb : av32 ? PK32.def.glb : av31 ? PLAYER3D_V31.def.glb : av3 ? PLAYER3D_V3.def.glb : rv2 ? PLAYER3D.def.glbV2 : PLAYER3D.def.glb;
  // Realism V3.1: while an authored clip holds the ball, the ball is its hand socket (else the engine ball)
  const rig31 = (id: string) => PLAYER3D_V31[play.players.find((q) => q.id === id)?.team === 'X' ? 'def' : 'off'].rig;
  const rig32 = (id: string) => PK32[play.players.find((q) => q.id === id)?.team === 'X' ? 'def' : 'off'].rig;
  const ballPos = av33 ? ballV33(play, pt) : av32 ? (mot32 === 'v32' ? ballV32(play, pt, rig32) : mot32 === 'v31' ? ballV31(play, pt, rig32) : undefined) ?? ball.pos : av31 ? ballV31(play, pt, rig31) ?? ball.pos : ball.pos;
  const dbg32: Athlete32[] = [];
  const glbs = useGlbs(anyC ? [offGlb, defGlb, ...labGlbs] : labGlbs);
  // the canvas only renders on frame changes (Remotion ThreeCanvas): mount it once the meshes are loaded (or failed)
  const glbWanted = anyC ? [offGlb, defGlb, ...labGlbs] : labGlbs;
  const glbReady = glbWanted.every((g) => glbs[g]);
  const failed = Object.entries(glbs).filter(([, g]) => g.error).map(([k, g]) => `${k}: ${g.error}`);
  logPlan(`[E2A players3d] ${PLAYER3D.version} play ${play.id}: ${describePlan(plan).join(' | ')}${failed.length ? ` | FALLBACK A for mesh players: ${failed.join('; ')}` : ''}`);
  if (!glbReady) return null;
  return (
    <ThreeCanvas
      width={W}
      height={H}
      shadows
      gl={{antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.05, outputColorSpace: THREE.SRGBColorSpace}}
      onCreated={({gl}) => {
        gl.shadowMap.type = THREE.PCFSoftShadowMap;
      }}
      camera={{fov: cam.fov, near: 0.1, far: 120}}
    >
      <CameraSync cam={cam} />
      <color attach="background" args={[env === 'practice' ? '#1B140E' : env === 'academy' ? '#04070F' : env === 'cinema' ? '#071022' : '#050A15']} />
      <fog attach="fog" args={[env === 'practice' ? '#1B140E' : env === 'academy' ? '#04070F' : env === 'cinema' ? '#071022' : '#050A15', env === 'academy' ? 12 : env === 'cinema' ? 22 : 14, env === 'academy' ? 34 : env === 'cinema' ? 58 : 40]} />
      <ArenaLights focus={W3([cam.target[0] * 0.5, Math.max(2, cam.target[1] * 0.7 + 1.5), 0])} env={env} />
      <Court3D logo={logo} swish={swish} env={env} netSnap={realismV3(play)} />
      {play.players.map((p, i) => {
        if (hide.includes(p.id)) return null;
        const pp = plan[p.id];
        const spec = skel?.[p.id];
        const variant = p.team === 'X' ? 'def' : 'off';
        const pkg = PLAYER3D[variant];
        const pkgGlb = av33 ? PLAYER3D_V33[variant].glb : av32 ? PK32[variant].glb : av31 ? PLAYER3D_V31[variant].glb : av3 ? PLAYER3D_V3[variant].glb : rv2 ? pkg.glbV2 : pkg.glb;
        const glbSrc = spec?.glb ?? pkgGlb;
        const cloth = rv2 && !spec?.glb ? clothAt(play, p.id, pt) : undefined;
        const glb = glbs[glbSrc]?.scene ?? null;
        const skin = SKINS[i % SKINS.length];
        const num = p.id.slice(1);
        if (spec && spec.look !== 'A') {
          const sp = skelPoseAt(playP, p.id, pt, {holder: ball.holder, pos: ball.pos, lag: ballLag}, RIM, spec.look === 'C');
          const clip = getClip(spec.clip);
          if (spec.look === 'C' && !(glb && clip && sp.bones && sp.hips)) logPlan(`[E2A players3d] ${p.id} clip ${spec.clip}: capsule this frame (glb ${!!glb}, clip ${!!clip}, bones ${!!sp.bones})`);
          return (
            <React.Fragment key={p.id}>
              {spec.look === 'C' && glb && clip && sp.bones && sp.hips ? (
                <SkinnedAthlete scene={glb} clipBones={clip.bones} bones={sp.bones} hips={sp.hips} inst={`${instNs ?? ''}${p.id}`} skin={skin} num={num} kit={KITS[p.team]} look={env === 'academy' || env === 'cinema' ? 'academy' : undefined} cloth={cloth} g3={rv3} />
              ) : (
                <Athlete pose={sp.pose} team={p.team} num={num} skin={skin} />
              )}
              <ContactShadows pose={sp.pose} />
            </React.Fragment>
          );
        }
        if (av33 && pp?.look === 'C' && glb) {
          // Realism V3.3: compiled / compat motion33 clip (engine pose fallback, reported by the QA), V3.2 mesh + cloth
          const rig = PLAYER3D_V33[variant].rig;
          const a = athleteV33(play, p.id, pt, rig, {holder: ball.holder, pos: ball.pos, lag: ballLag});
          if (debug32 && a.debug) dbg32.push(a);
          return (
            <React.Fragment key={p.id}>
              <SkinnedAthlete scene={glb} clipBones={rig.bones} bones={a.fr.bones} hips={a.fr.hips} inst={`${instNs ?? ''}v33:${neutral ? 'n' : 'c'}:${p.id}`} scale={a.sc} skin={skin} num={num} kit={KITS[p.team]}
                look={env === 'academy' || env === 'cinema' ? 'academy' : undefined} cloth32={a.cloth} v3 morph={a.fr.morph} neutral={neutral} />
              <ContactShadows pose={a.pose} />
            </React.Fragment>
          );
        }
        if (av32 && pp?.look === 'C' && glb) {
          // Realism V3.2: parametrised library motion (or, for Test A, the V3.1 / engine motion on the same mesh), V3.2 or
          // V3.1 mesh (Test B), separate jersey / shorts cloth; neutral materials for the motion-only comparison
          const rig = PK32[variant].rig;
          const a = athleteV32(play, p.id, pt, rig, {holder: ball.holder, pos: ball.pos, lag: ballLag}, mot32);
          if (debug32 && a.debug) dbg32.push(a);
          const meshV32 = athleteMesh !== 'v31';
          return (
            <React.Fragment key={p.id}>
              <SkinnedAthlete scene={glb} clipBones={rig.bones} bones={a.fr.bones} hips={a.fr.hips} inst={`${instNs ?? ''}v32:${athleteMesh ?? 'v32'}:${mot32}:${neutral ? 'n' : 'c'}:${p.id}`} scale={a.sc} skin={skin} num={num} kit={KITS[p.team]}
                look={env === 'academy' || env === 'cinema' ? 'academy' : undefined} cloth={meshV32 ? undefined : a.cloth.jersey} cloth32={meshV32 ? a.cloth : undefined} v3 morph={a.fr.morph} neutral={neutral} />
              <ContactShadows pose={a.pose} />
            </React.Fragment>
          );
        }
        if (av31 && pp?.look === 'C' && glb) {
          // Realism V3.1: AUTHORED body motion when this player has a hand-keyed clip (motion.ts), else the V3 bridge on
          // the engine pose; V3.1 body / shoes / loose apparel; cloth driven by the authored pelvis
          const rig = PLAYER3D_V31[variant].rig;
          const m = motionV31(play, p.id, pt, rig);
          const pose = m ? m.pose : poseAt(play, p.id, pt, {holder: ball.holder, pos: ball.pos, lag: ballLag}, RIM);
          const sc = meshScale(rig, pose);
          const fr = m ? framesV31(rig, m) : bonesV3(rig, pose, sc, {pos: ball.pos, held: ball.holder === p.id});
          const cl = (m ? clothV31(play, p.id, pt, rig) : undefined) ?? clothAt(play, p.id, pt);
          return (
            <React.Fragment key={p.id}>
              <SkinnedAthlete scene={glb} clipBones={rig.bones} bones={fr.bones} hips={fr.hips} inst={`${instNs ?? ''}v31:${p.id}`} scale={sc} skin={skin} num={num} kit={KITS[p.team]} look={env === 'academy' || env === 'cinema' ? 'academy' : undefined} cloth={cl} v3 morph={fr.morph} />
              <ContactShadows pose={pose} />
            </React.Fragment>
          );
        }
        if (av3 && pp?.look === 'C' && glb) {
          // Realism V3: same engine pose (rig.ts), V3 bones + hands + correctives (athleteV3.ts), V3 apparel / cloth
          const rig3 = PLAYER3D_V3[variant].rig;
          const pose = poseAt(play, p.id, pt, {holder: ball.holder, pos: ball.pos, lag: ballLag}, RIM);
          const sc = meshScale(rig3, pose);
          const fr = bonesV3(rig3, pose, sc, {pos: ball.pos, held: ball.holder === p.id}, weightShift(play, p.id, pt));
          return (
            <React.Fragment key={p.id}>
              <SkinnedAthlete scene={glb} clipBones={rig3.bones} bones={fr.bones} hips={fr.hips} inst={`${instNs ?? ''}v3:${p.id}`} scale={sc} skin={skin} num={num} kit={KITS[p.team]} look={env === 'academy' || env === 'cinema' ? 'academy' : undefined} cloth={clothAt(play, p.id, pt)} v3 morph={fr.morph} />
              <ContactShadows pose={pose} />
            </React.Fragment>
          );
        }
        if (pp?.look === 'C' && glb && pkg.rig) {
          const pose = poseAt(play, p.id, pt, {holder: ball.holder, pos: ball.pos, lag: ballLag}, RIM);
          const sc = meshScale(pkg.rig, pose);
          const r = bonesFromPose(pkg.rig, pose, sc);
          return (
            <React.Fragment key={p.id}>
              <SkinnedAthlete scene={glb} clipBones={pkg.rig.bones} bones={r.bones} hips={r.hips} inst={`${instNs ?? ''}${p.id}`} scale={sc} skin={skin} num={num} kit={KITS[p.team]} look={env === 'academy' || env === 'cinema' ? 'academy' : undefined} cloth={cloth} g3={rv3} />
              <ContactShadows pose={pose} />
            </React.Fragment>
          );
        }
        // the head follows an explicit look target after the eyes (eyes first, head after): the target is averaged over
        // 0.06-0.30 s ago, so a new look turns the head smoothly instead of snapping it
        let lookP: V3 | undefined;
        let down = 0;
        let chestP: V3 | undefined;
        if (faces) {
          const acc: V3 = [0, 0, 0];
          let nLook = 0;
          const LAGS = [0.06, 0.12, 0.18, 0.24, 0.3];
          for (const lag of LAGS) {
            const tl = Math.max(0, pt - lag);
            const lk = exprOf(play, p.id, tl).look;
            const fr = sample(play, tl);
            const pp = fr.players[p.id]?.pos ?? [0, 0];
            const q = lookPoint(play, lk, tl, fr.ball.pos, [pp[0], pp[1], 1.7]) ?? fr.ball.pos;
            if (lk && lk !== 'ball') nLook++;
            if (lk === 'down') down += 1 / LAGS.length;
            acc[0] += q[0] / LAGS.length;
            acc[1] += q[1] / LAGS.length;
            acc[2] += q[2] / LAGS.length;
          }
          if (nLook) lookP = acc;
          // shoulders: the same target, later (0.30-0.54 s ago)
          if (lookP) {
            const c: V3 = [0, 0, 0];
            const CL = [0.3, 0.36, 0.42, 0.48, 0.54];
            for (const lag of CL) {
              const tl = Math.max(0, pt - lag);
              const fr = sample(play, tl);
              const pp = fr.players[p.id]?.pos ?? [0, 0];
              const q = lookPoint(play, exprOf(play, p.id, tl).look, tl, fr.ball.pos, [pp[0], pp[1], 1.7]) ?? fr.ball.pos;
              c[0] += q[0] / CL.length;
              c[1] += q[1] / CL.length;
              c[2] += q[2] / CL.length;
            }
            chestP = c;
          }
        }
        const pose = poseAt(play, p.id, pt, {holder: ball.holder, pos: ball.pos, lag: ballLag, look: lookP, down, chest: chestP}, RIM);
        return (
          <React.Fragment key={p.id}>
            <Athlete pose={pose} team={p.team} num={faces?.nums?.[p.id] ?? p.id.slice(1)} skin={faces?.skin?.[p.id] ?? SKINS[i % SKINS.length]} face={faces ? faceOf(play, p.id, i, pt, ball.pos, pose.head, faces) : undefined} />
            <ContactShadows pose={pose} />
          </React.Fragment>
        );
      })}
      <Ball pos={ballPos} spin={spin} />
      {debug32 && <Debug32 items={dbg32} ball={ballPos} />}
      {children}
    </ThreeCanvas>
  );
};

// ---------------------------------------------------------------- Realism V3.2 contact debug (tests only)
// planted foot = green disc under the ball of the foot, swinging foot = red; palm target = yellow (held) sphere;
// ball halo colour = ball state (white FREE, cyan INCOMING / FIRST_CONTACT, green CONTROLLED / SECURED, orange
// DRIBBLE, magenta SHOOT_PREP / RELEASE, grey FLIGHT / PASS)
const STATE_COL: Record<string, string> = {FREE: '#FFFFFF', INCOMING: '#3FE0FF', FIRST_CONTACT: '#3FE0FF', CONTROLLED: '#43F06A', SECURED: '#43F06A', DRIBBLE: '#FF9A2E', SHOOT_PREP: '#FF4FD8', RELEASE: '#FF4FD8', FLIGHT: '#9A9A9A', PASS: '#9A9A9A'};
const Debug32: React.FC<{items: Athlete32[]; ball: V3}> = ({items, ball}) => {
  const held = items.find((a) => a.debug && a.debug.owner && a.debug.state !== 'FREE');
  const st = held?.debug?.state ?? items[0]?.debug?.state ?? 'FREE';
  return (
    <group>
      {items.flatMap((a, i) =>
        (a.debug?.feet ?? []).map((f, k) => (
          <mesh key={`f${i}${k}`} position={W3([f.g[0], f.g[1], 0.006])} rotation={[-Math.PI / 2, 0, 0]}>
            <circleGeometry args={[0.07, 20]} />
            <meshBasicMaterial color={f.planted ? '#2BE36B' : '#FF3B3B'} transparent opacity={0.85} depthWrite={false} />
          </mesh>
        )),
      )}
      {items.flatMap((a, i) =>
        (a.debug?.palm ?? []).map((p, k) =>
          p ? (
            <mesh key={`p${i}${k}`} position={W3(p)}>
              <sphereGeometry args={[0.022, 12, 8]} />
              <meshBasicMaterial color="#FFE14A" depthTest={false} transparent opacity={0.9} />
            </mesh>
          ) : null,
        ),
      )}
      <mesh position={W3(ball)}>
        <sphereGeometry args={[0.15, 20, 14]} />
        <meshBasicMaterial color={STATE_COL[st] ?? '#FFFFFF'} wireframe transparent opacity={0.8} depthTest={false} />
      </mesh>
    </group>
  );
};
