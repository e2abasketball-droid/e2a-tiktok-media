// E2A 3D engine — one 3D viewport of a play at a given play time: court, lights, ten animated
// athletes, ball, world-space tactical graphics, and the camera.
import React from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {FIBA} from '../tactical/geometry.ts';
import type {V3} from '../tactical/geometry.ts';
import {sample} from '../tactical/play.ts';
import {Athlete, SKINS, W3} from './Athlete';
import {ArenaLights, Court3D} from './Court3D';
import type {PlayWithActions} from './rig.ts';
import {poseAt} from './rig.ts';
import type {Cam3} from './camera3d.ts';
import {CLIP_GLB} from './clips/index.ts';
import type {PlayWithSkel} from './skelclip.ts';
import {getClip, skelPoseAt} from './skelclip.ts';
import {SkinnedAthlete, useGlb} from './SkinnedAthlete';

const RIM: V3 = [FIBA.basket[0], FIBA.basket[1], FIBA.rimZ];

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

const Ball: React.FC<{pos: V3}> = ({pos}) => {
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
  return (
    <mesh position={W3(pos)} castShadow>
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
};

export const Scene3D: React.FC<SceneProps> = ({play, pt, cam, W, H, hide = [], children, logo}) => {
  const f = sample(play, pt);
  const ball = f.ball;
  const swish = (() => {
    const shot = play.ball.find((e) => e.type === 'shot' || e.type === 'layup') as {t1: number} | undefined;
    if (!shot) return 0;
    const u = (pt - shot.t1) / 0.6;
    return u > 0 && u < 1 ? u : 0;
  })();
  // LAB (opt-in): skeletal clips for some players (play.skel), look B = capsule athlete, C = deformable mesh
  const skel = (play as PlayWithSkel).skel;
  const meshSpec = skel ? Object.values(skel).find((s) => s.look === 'C') : undefined;
  const glb = useGlb(meshSpec ? (meshSpec.glb ?? CLIP_GLB[meshSpec.clip]) : undefined);
  const RIMv = RIM;
  const playerNode = (p: (typeof play.players)[number], i: number) => {
    const spec = skel?.[p.id];
    const hint = {holder: ball.holder, pos: ball.pos};
    if (spec && spec.look !== 'A') {
      const sp = skelPoseAt(play as PlayWithSkel, p.id, pt, hint, RIMv, spec.look === 'C');
      const clip = getClip(spec.clip);
      if (spec.look === 'C' && glb && clip && sp.bones && sp.hips) return <SkinnedAthlete key={p.id} scene={glb} clipBones={clip.bones} bones={sp.bones} hips={sp.hips} />;
      return <Athlete key={p.id} pose={sp.pose} team={p.team} num={p.id.slice(1)} skin={SKINS[i % SKINS.length]} />;
    }
    return <Athlete key={p.id} pose={poseAt(play, p.id, pt, hint, RIMv)} team={p.team} num={p.id.slice(1)} skin={SKINS[i % SKINS.length]} />;
  };
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
      <color attach="background" args={['#050A15']} />
      <fog attach="fog" args={['#050A15', 14, 40]} />
      <ArenaLights focus={W3([cam.target[0] * 0.5, Math.max(2, cam.target[1] * 0.7 + 1.5), 0])} />
      <Court3D logo={logo} swish={swish} />
      {play.players.map((p, i) => (hide.includes(p.id) ? null : playerNode(p, i)))}
      <Ball pos={ball.pos} />
      {children}
    </ThreeCanvas>
  );
};
