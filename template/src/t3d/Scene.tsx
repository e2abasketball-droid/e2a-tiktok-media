// E2A 3D engine — one 3D viewport of a play at a given play time: court, lights, ten animated
// athletes, ball, world-space tactical graphics, and the camera.
import React from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {FIBA} from '../tactical/geometry.ts';
import type {V3} from '../tactical/geometry.ts';
import {posAt, sample} from '../tactical/play.ts';
import {Athlete, SKINS, W3} from './Athlete';
import type {FaceState} from './Athlete';
import {ArenaLights, Court3D} from './Court3D';
import type {PlayWithActions} from './rig.ts';
import {poseAt} from './rig.ts';
import type {Cam3} from './camera3d.ts';

const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];

const faceOf = (play: PlayWithActions, id: string, i: number, pt: number, ballPos: V3, head: V3, cfg: FaceCfg): FaceState => {
  const e = exprAt((play as PlayWithActions & {expr?: Record<string, ExprKey[]>}).expr?.[id], pt);
  let gaze: V3 = ballPos;
  if (e.look && e.look !== 'ball' && play.tracks[e.look]) {
    const q = posAt(play.tracks[e.look], Math.max(0, Math.min(play.duration, pt)));
    gaze = [q[0], q[1], head[2]];
  }
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
  /** 2026-11-17 character episodes: warm open practice gym vs cold full game arena (default: the arena as before) */
  env?: 'practice' | 'game';
  faces?: FaceCfg;
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

export const Scene3D: React.FC<SceneProps> = ({play, pt, cam, W, H, hide = [], children, logo, env, faces}) => {
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
      <color attach="background" args={[env === 'practice' ? '#1B140E' : '#050A15']} />
      <fog attach="fog" args={[env === 'practice' ? '#1B140E' : '#050A15', 14, 40]} />
      <ArenaLights focus={W3([cam.target[0] * 0.5, Math.max(2, cam.target[1] * 0.7 + 1.5), 0])} env={env} />
      <Court3D logo={logo} swish={swish} env={env} />
      {play.players.map((p, i) => {
        if (hide.includes(p.id)) return null;
        const pose = poseAt(play, p.id, pt, {holder: ball.holder, pos: ball.pos, lag: ballLag}, RIM);
        return (
          <React.Fragment key={p.id}>
            <Athlete pose={pose} team={p.team} num={faces?.nums?.[p.id] ?? p.id.slice(1)} skin={faces?.skin?.[p.id] ?? SKINS[i % SKINS.length]} face={faces ? faceOf(play, p.id, i, pt, ball.pos, pose.head, faces) : undefined} />
            <ContactShadows pose={pose} />
          </React.Fragment>
        );
      })}
      <Ball pos={ball.pos} spin={spin} />
      {children}
    </ThreeCanvas>
  );
};
