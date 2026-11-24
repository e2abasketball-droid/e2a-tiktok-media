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
import {BALL_R, ballAt, kicksOf, playerAt, receivesOf} from './play';
import type {Look} from './pitch3d';
import {Lights, Pitch3D} from './pitch3d';
import type {Word} from './screen';
import {Chip, Cue, EndCard, Flash, GoalAccent, KineticTitle, LogoBug, Pin, Signature, Stamp, Steps, Subtitles, Tag} from './screen';
import './brand';

type Timed = {from: number; to?: number};
export type ScreenItem = Timed &
  (
    | {type: 'title'; lines: string[]; y?: number; size?: number; gold?: number[]; sub?: string; align?: 'left' | 'center'}
    | {type: 'stamp'; text: string; y?: number; tone?: 'gold' | 'white' | 'red'; badge?: string}
    | {type: 'pin'; player?: string; p?: V2; text: string; tone?: 'gold' | 'white' | 'red'; dy?: number; dx?: number; size?: number; z?: number}
    | {type: 'chip'; player?: string; p?: V2; text: string; tone?: 'gold' | 'white' | 'red'; dy?: number; dx?: number; size?: number; z?: number; letter?: boolean}
    | {type: 'tag'; text: string; icon?: 'pause' | 'replay' | 'slow'}
    | {type: 'scrim'; opacity?: number}
    | {type: 'end'}
    // V07 off-ball timing layer
    | {type: 'cue'; player?: string; p?: V2; text: string; kicker?: string; now?: boolean; dy?: number; dx?: number; z?: number}
    | {type: 'steps'; steps: [string, number][]; y?: number; x?: number; fin?: number; fout?: number}
    | {type: 'accent'}
    | {type: 'sig'}
  );
/** V07 picture-in-picture: a second camera on the SAME play instant (e.g. the corner execution while the main
 *  picture holds the box). x/y/w/h in composition pixels. */
export type Pip = {from: number; to: number; cam: CamKey[]; x: number; y: number; w: number; h: number; label?: string; style?: 'min'};
/** V07 focus shift: everybody except `keep` is muted (k 0..1) */
export type Focus = {from: number; to?: number; keep: string[]; k?: number};
export type Shot = {
  name: string;
  from: number; // video seconds
  remap: [number, number][]; // [local video s, play s], linear between keys, held after the last
  cam: CamKey[];
  ov?: (Timed & Ov & {draw?: number; contIn?: boolean; contOut?: boolean})[];
  screen?: ScreenItem[];
  freeze?: [number, number][]; // local ranges with the freeze grade
  flash?: number;
  /** V07: 'live' shots continue the same play clock across cuts (checked by qa/qc_edit.mjs); 'replay' may rewind */
  kind?: 'live' | 'replay';
  pip?: Pip[];
  focus?: Focus[];
};
export type Episode = {
  id: string;
  title: string;
  duration: number;
  play: FBPlay;
  words: Word[];
  keywords: string[];
  shots: Shot[];
  music?: {src: string; volume: number};
  logoBug?: boolean;
  subtitleHide?: [number, number][];
  subtitleY?: number;
  /** V09: 'keys' = white subtitles with gold only on the tactical keywords, on a soft navy band */
  subtitleStyle?: 'karaoke' | 'keys';
  subtitleSize?: number;
  /** V03+: 'day' = bright match lighting (default 'night' keeps older episodes identical) */
  look?: Look;
  /** V03+: 'clean' = no vignette, only a light top band behind titles (default 'classic') */
  grade?: 'classic' | 'clean';
  /** V03+: graphics v2 (smoothed tapered arrows, thin rings, soft zones) */
  graphicsV2?: boolean;
  /** V03+: no subtitles (silent cut) */
  subtitles?: boolean;
};

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

/** v2 guard stance: defenders lower their centre near the ball carrier (and a little when marking in the box) */
const guardOf = (play: FBPlay, id: string, pt: number, ball: {pos: V3; holder?: string}) => {
  const me = play.players.find((p) => p.id === id)!;
  if (me.team !== 'defence' || me.role === 'GK') return 0;
  const q = playerAt(play, id, pt).pos;
  const d = Math.hypot(ball.pos[0] - q[0], ball.pos[1] - q[1]);
  const near = ball.holder && play.players.find((p) => p.id === ball.holder)?.team === 'attack' ? Math.max(0, Math.min(1, (5 - d) / 2.5)) : 0;
  const inBox = q[0] > 36 && Math.abs(q[1]) < 20.2 ? 0.35 : 0;
  return Math.max(near, inBox);
};

const Scene: React.FC<{play: FBPlay; pt: number; cam: Cam; W: number; H: number; ov: LiveOv[]; look?: Look; gv2?: boolean; dimOf?: (id: string) => number; shadows?: boolean}> = ({play, pt, cam, W, H, ov, look, gv2, dimOf, shadows = true}) => {
  const ball = ballAt(play, pt);
  const day = look === 'day';
  const hit = ball.netHit && pt >= ball.netHit.t && pt - ball.netHit.t < 2.5 ? {age: pt - ball.netHit.t, at: ball.netHit.at} : null;
  return (
    <ThreeCanvas
      width={W}
      height={H}
      shadows={shadows}
      gl={{antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: day ? 1.08 : 1.0, outputColorSpace: THREE.SRGBColorSpace}}
      onCreated={({gl}) => {
        gl.shadowMap.type = THREE.PCFSoftShadowMap;
      }}
      camera={{fov: cam.fov, near: 0.8, far: 400}}
    >
      <CameraSync cam={cam} />
      <color attach="background" args={[day ? '#A9C8E6' : '#070D1A']} />
      <fog attach="fog" args={day ? ['#BCD2E6', 150, 420] : ['#0A1426', 70, 190]} />
      <Lights focus={[cam.target[0], cam.target[1]]} look={look} />
      <Pitch3D hit={hit} look={look} />
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
          receives={play.receivePose ? receivesOf(play, p.id) : undefined}
          v2={play.animV2}
          keeper={play.animV2 && p.role === 'GK'}
          guard={play.animV2 ? guardOf(play, p.id, pt, ball) : undefined}
          lookAt={play.headLook ? [ball.pos[0], ball.pos[1]] : undefined}
          dim={dimOf ? dimOf(p.id) : undefined}
        />
      ))}
      <Ball pos={ball.pos} q={ball.spin} />
      <Overlays3D play={play} pt={pt} items={ov} v2={gv2} />
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
  // V07 focus shift (fades in/out over 0.25 s)
  const foc = (shot.focus ?? []).find((f) => lt >= f.from && lt < (f.to ?? end - shot.from));
  const fk = foc ? (foc.k ?? 0.75) * Math.min(1, (lt - foc.from) / 0.25, ((foc.to ?? end - shot.from) - lt) / 0.25) : 0;
  const dimOf = foc ? (id: string) => (foc.keep.includes(id) ? 0 : fk) : undefined;
  const pips = (shot.pip ?? []).filter((p) => lt >= p.from && lt < p.to);
  return (
    <AbsoluteFill style={{background: '#070D1A'}}>
      <AbsoluteFill style={{filter: frozen ? (ep.grade === 'clean' ? 'saturate(0.82) contrast(1.04)' : 'saturate(0.7) brightness(0.92) contrast(1.05)') : 'saturate(1.04) contrast(1.03)'}}>
        <Scene play={play} pt={pt} cam={cam} W={W} H={H} ov={ov} look={ep.look} gv2={ep.graphicsV2} dimOf={dimOf} />
      </AbsoluteFill>
      {pips.map((p, i) => {
        const a = Math.min(1, (lt - p.from) / 0.22, (p.to - lt) / 0.22);
        const pc = camAt(play, p.cam, lt - p.from, pt);
        const mn = p.style === 'min';
        // V09 'min': thin gold edge, soft shadow, plain fade (no scale pop), small label
        return (
          <div key={`pip${i}`} style={{position: 'absolute', left: p.x, top: p.y, width: p.w, height: p.h, opacity: a, transform: mn ? undefined : `scale(${0.94 + 0.06 * a})`, borderRadius: mn ? 14 : 18, overflow: 'hidden', border: mn ? '2px solid rgba(201,162,77,0.95)' : '4px solid #C9A24D', boxShadow: mn ? '0 8px 22px rgba(0,0,0,0.35)' : '0 14px 36px rgba(0,0,0,0.45)'}}>
            <Scene play={play} pt={pt} cam={pc} W={p.w} H={p.h} ov={[]} look={ep.look} gv2={ep.graphicsV2} shadows={mn} />
            {p.label && <div style={{position: 'absolute', left: mn ? 10 : 12, top: mn ? 8 : 10, fontFamily: 'Inter, Arial, sans-serif', fontWeight: 900, fontSize: mn ? 16 : 20, letterSpacing: 3, color: '#FFFFFF', background: 'rgba(11,28,61,0.8)', padding: mn ? '3px 8px' : '4px 10px', borderRadius: 6}}>{p.label}</div>}
          </div>
        );
      })}
      {ep.grade === 'clean' ? (
        // clean grade (V03): no vignette; a light navy band only at the top, behind the titles and the logo
        <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(11,28,61,0.42) 0%, rgba(11,28,61,0.12) 15%, rgba(11,28,61,0) 24%)'}} />
      ) : (
        <>
          {/* grade: vignette + top/bottom falloff that also keeps the text readable */}
          <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 58%, rgba(3,8,20,0.5) 100%)'}} />
          <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(7,13,26,0.6) 0%, rgba(7,13,26,0) 24%, rgba(7,13,26,0) 60%, rgba(7,13,26,0.62) 100%)'}} />
        </>
      )}
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
          case 'chip': {
            const p = s.p ?? playerAt(play, s.player!, pt).pos;
            const q = proj([p[0], p[1], s.z ?? 2.05]);
            return q.visible ? <Chip key={i} x={q.x} y={q.y} text={s.text} age={s.age} dur={s.dur} tone={s.tone} dy={s.dy} dx={s.dx} size={s.size} letter={s.letter} /> : null;
          }
          case 'tag':
            return <Tag key={i} text={s.text} age={s.age} dur={s.dur} icon={s.icon} />;
          case 'scrim':
            return <AbsoluteFill key={i} style={{background: '#0B1C3D', opacity: (s.opacity ?? 0.55) * Math.min(1, s.age / 0.4)}} />;
          case 'end':
            return <EndCard key={i} age={s.age} />;
          case 'cue': {
            const p = s.p ?? playerAt(play, s.player!, pt).pos;
            const q = proj([p[0], p[1], s.z ?? 2.05]);
            return q.visible ? <Cue key={i} x={q.x} y={q.y} text={s.text} kicker={s.kicker} now={s.now} age={s.age} dur={s.dur} dy={s.dy} dx={s.dx} /> : null;
          }
          case 'steps':
            return <Steps key={i} steps={s.steps} pt={pt} age={s.age} dur={s.dur} y={s.y} x={s.x} fin={s.fin} fout={s.fout} />;
          case 'accent':
            return <GoalAccent key={i} age={s.age} dur={s.dur} />;
          case 'sig':
            return <Signature key={i} age={s.age} />;
          default:
            return null;
        }
      })}
      {ep.subtitles !== false && !ending && !(ep.subtitleHide ?? []).some(([a, b]) => t >= a && t < b) && <Subtitles words={ep.words} t={t} keys={ep.keywords} y={ep.subtitleY} mode={ep.subtitleStyle} size={ep.subtitleSize} />}
      {ep.logoBug !== false && !ending && <LogoBug opacity={0.92} />}
      {shot.flash !== undefined && lt < 0.25 && <Flash age={lt} strength={shot.flash} />}
      {ep.music && <Audio src={staticFile(ep.music.src)} volume={ep.music.volume} />}
    </AbsoluteFill>
  );
};
