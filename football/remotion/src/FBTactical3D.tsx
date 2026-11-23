// E2A Football — FBTactical3D: one play + an edit (shots with play-time remaps, three camera modes,
// pitch graphics, screen graphics and timed captions) -> 1080x1920 YouTube Short.
import React from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {AbsoluteFill, Audio, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Athlete, KITS, SKINS, W3} from './athlete';
import type {Cam, CamKey} from './camera';
import {camAt, projector} from './camera';
import type {LiveOv, Ov} from './overlays3d';
import {Overlays3D} from './overlays3d';
import type {FBPlay, V2, V3} from './play';
import {BALL_R, ballAt, kicksOf, playerAt} from './play';
import {Lights, Pitch3D} from './pitch3d';
import type {Word} from './screen';
import {EndCard, Flash, KineticTitle, LogoBug, Pin, Stamp, Subtitles, Tag} from './screen';
import './brand';

type Timed = {from: number; to?: number};
export type ScreenItem = Timed &
  (
    | {type: 'title'; lines: string[]; y?: number; size?: number; gold?: number[]; sub?: string; align?: 'left' | 'center'}
    | {type: 'stamp'; text: string; y?: number; tone?: 'gold' | 'white' | 'red'; badge?: string}
    | {type: 'pin'; player?: string; p?: V2; text: string; tone?: 'gold' | 'white' | 'red'; dy?: number; dx?: number; size?: number; z?: number}
    | {type: 'tag'; text: string; icon?: 'pause' | 'replay' | 'slow'}
    | {type: 'scrim'; opacity?: number}
    | {type: 'end'}
  );
export type Shot = {
  name: string;
  from: number; // video seconds
  remap: [number, number][]; // [local video s, play s], linear between keys, held after the last
  cam: CamKey[];
  ov?: (Timed & Ov & {draw?: number})[];
  screen?: ScreenItem[];
  freeze?: [number, number][]; // local ranges with the freeze grade
  flash?: number;
};
export type Episode = {id: string; title: string; duration: number; play: FBPlay; words: Word[]; keywords: string[]; shots: Shot[]; music?: {src: string; volume: number}; logoBug?: boolean; subtitleHide?: [number, number][]};

const remapAt = (r: [number, number][], lt: number) => {
  if (lt <= r[0][0]) return r[0][1];
  for (let i = 0; i < r.length - 1; i++) {
    const [a, pa] = r[i];
    const [b, pb] = r[i + 1];
    if (lt <= b) return pa + ((pb - pa) * (lt - a)) / Math.max(1e-6, b - a);
  }
  return r[r.length - 1][1];
};

const CameraSync: React.FC<{cam: Cam}> = ({cam}) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  camera.position.set(...W3(cam.pos));
  camera.up.set(0, 1, 0);
  camera.lookAt(...W3(cam.target));
  camera.fov = cam.fov;
  camera.near = 0.8;
  camera.far = 400;
  camera.updateProjectionMatrix();
  return null;
};

let ballTex: THREE.Texture | null = null;
const ballTexture = () => {
  if (ballTex) return ballTex;
  // equirectangular map: 12 dark pentagon patches at the icosahedron vertices, white hexagon panels
  const Wt = 512;
  const Ht = 256;
  const c = document.createElement('canvas');
  c.width = Wt;
  c.height = Ht;
  const g = c.getContext('2d')!;
  const img = g.createImageData(Wt, Ht);
  const phi = (1 + Math.sqrt(5)) / 2;
  const V = [
    [-1, phi, 0], [1, phi, 0], [-1, -phi, 0], [1, -phi, 0], [0, -1, phi], [0, 1, phi], [0, -1, -phi], [0, 1, -phi], [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1],
  ].map((v) => {
    const l = Math.hypot(v[0], v[1], v[2]);
    return [v[0] / l, v[1] / l, v[2] / l];
  });
  for (let j = 0; j < Ht; j++)
    for (let i = 0; i < Wt; i++) {
      const lon = (i / Wt) * 2 * Math.PI;
      const lat = (j / Ht) * Math.PI;
      const d = [Math.sin(lat) * Math.cos(lon), Math.cos(lat), Math.sin(lat) * Math.sin(lon)];
      let best = -1;
      let second = -1;
      for (const v of V) {
        const dot = d[0] * v[0] + d[1] * v[1] + d[2] * v[2];
        if (dot > best) {
          second = best;
          best = dot;
        } else if (dot > second) second = dot;
      }
      const ang = Math.acos(Math.min(1, best));
      let col = 244;
      if (ang < 0.33) col = 26; // pentagon
      else if (best - second < 0.012) col = 150; // seam
      const k = (j * Wt + i) * 4;
      img.data[k] = col;
      img.data[k + 1] = col;
      img.data[k + 2] = col + (col > 200 ? 4 : 0);
      img.data[k + 3] = 255;
    }
  g.putImageData(img, 0, 0);
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  ballTex = t;
  return t;
};

const Ball: React.FC<{pos: V3; q: [number, number, number, number]}> = ({pos, q}) => (
  <group position={W3(pos)}>
    <mesh quaternion={new THREE.Quaternion(q[0], q[1], q[2], q[3])} castShadow>
      <sphereGeometry args={[BALL_R, 32, 20]} />
      <meshStandardMaterial map={ballTexture()} roughness={0.45} />
    </mesh>
  </group>
);

const useAssets = () => {
  const [ok, setOk] = React.useState(false);
  const [h] = React.useState(() => delayRender('fonts'));
  React.useEffect(() => {
    Promise.all([document.fonts.load('150px Anton'), document.fonts.load('900 40px Inter')]).then(() => {
      setOk(true);
      continueRender(h);
    });
  }, [h]);
  return ok;
};

const Scene: React.FC<{play: FBPlay; pt: number; cam: Cam; W: number; H: number; ov: LiveOv[]}> = ({play, pt, cam, W, H, ov}) => {
  const ball = ballAt(play, pt);
  const hit = ball.netHit && pt >= ball.netHit.t && pt - ball.netHit.t < 2.5 ? {age: pt - ball.netHit.t, at: ball.netHit.at} : null;
  return (
    <ThreeCanvas
      width={W}
      height={H}
      shadows
      gl={{antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.0, outputColorSpace: THREE.SRGBColorSpace}}
      onCreated={({gl}) => {
        gl.shadowMap.type = THREE.PCFSoftShadowMap;
      }}
      camera={{fov: cam.fov, near: 0.8, far: 400}}
    >
      <CameraSync cam={cam} />
      <color attach="background" args={['#070D1A']} />
      <fog attach="fog" args={['#0A1426', 70, 190]} />
      <Lights focus={[cam.target[0], cam.target[1]]} />
      <Pitch3D hit={hit} />
      {play.players.map((p, i) => (
        <Athlete
          key={p.id}
          s={playerAt(play, p.id, pt)}
          t={pt}
          kit={p.role === 'GK' ? KITS.keeper : p.team === 'attack' ? KITS.navy : KITS.white}
          number={p.number}
          skin={SKINS[(i * 3) % SKINS.length]}
          hairIdx={i}
          kicks={kicksOf(play, p.id)}
          actions={p.actions}
        />
      ))}
      <Ball pos={ball.pos} q={ball.spin} />
      <Overlays3D play={play} pt={pt} items={ov} />
    </ThreeCanvas>
  );
};

export const FBTactical3D: React.FC<{episode: Episode}> = ({episode: ep}) => {
  const frame = useCurrentFrame();
  const {fps, width: W, height: H} = useVideoConfig();
  const ready = useAssets();
  const t = frame / fps;
  if (!ready) return null;
  const shots = ep.shots;
  let si = 0;
  while (si < shots.length - 1 && t >= shots[si + 1].from) si++;
  const shot = shots[si];
  const end = si + 1 < shots.length ? shots[si + 1].from : ep.duration;
  const lt = t - shot.from;
  const pt = remapAt(shot.remap, lt);
  const play = ep.play;
  const cam = camAt(play, shot.cam, lt, pt);
  const live = <X extends Timed>(items: X[] = []) =>
    items
      .map((o) => {
        const to = o.to ?? end - shot.from;
        return {...o, age: lt - o.from, dur: to - o.from};
      })
      .filter((o) => o.age >= 0 && o.age < o.dur);
  const ov = live(shot.ov) as unknown as LiveOv[];
  const scr = live(shot.screen);
  const proj = projector(cam, W, H);
  const frozen = (shot.freeze ?? []).some(([a, b]) => lt >= a && lt < b);
  const ending = scr.some((s) => s.type === 'end');
  return (
    <AbsoluteFill style={{background: '#070D1A'}}>
      <AbsoluteFill style={{filter: frozen ? 'saturate(0.7) brightness(0.92) contrast(1.05)' : 'saturate(1.04) contrast(1.03)'}}>
        <Scene play={play} pt={pt} cam={cam} W={W} H={H} ov={ov} />
      </AbsoluteFill>
      {/* grade: vignette + top/bottom falloff that also keeps the text readable */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 58%, rgba(3,8,20,0.5) 100%)'}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(7,13,26,0.6) 0%, rgba(7,13,26,0) 24%, rgba(7,13,26,0) 60%, rgba(7,13,26,0.62) 100%)'}} />
      {scr.map((s, i) => {
        switch (s.type) {
          case 'title':
            return <KineticTitle key={i} lines={s.lines} age={s.age} dur={s.dur} y={s.y} size={s.size} gold={s.gold} sub={s.sub} align={s.align} />;
          case 'stamp':
            return <Stamp key={i} text={s.text} age={s.age} dur={s.dur} y={s.y} tone={s.tone} badge={s.badge} />;
          case 'pin': {
            const p = s.p ?? playerAt(play, s.player!, pt).pos;
            const q = proj([p[0], p[1], s.z ?? 2.1]);
            return q.visible ? <Pin key={i} x={q.x} y={q.y} text={s.text} age={s.age} dur={s.dur} tone={s.tone} dy={s.dy} dx={s.dx} size={s.size} /> : null;
          }
          case 'tag':
            return <Tag key={i} text={s.text} age={s.age} dur={s.dur} icon={s.icon} />;
          case 'scrim':
            return <AbsoluteFill key={i} style={{background: '#0B1C3D', opacity: (s.opacity ?? 0.55) * Math.min(1, s.age / 0.4)}} />;
          case 'end':
            return <EndCard key={i} age={s.age} />;
          default:
            return null;
        }
      })}
      {!ending && !(ep.subtitleHide ?? []).some(([a, b]) => t >= a && t < b) && <Subtitles words={ep.words} t={t} keys={ep.keywords} />}
      {ep.logoBug !== false && !ending && <LogoBug opacity={0.92} />}
      {shot.flash !== undefined && lt < 0.25 && <Flash age={lt} strength={shot.flash} />}
      {ep.music && <Audio src={staticFile(ep.music.src)} volume={ep.music.volume} />}
    </AbsoluteFill>
  );
};
