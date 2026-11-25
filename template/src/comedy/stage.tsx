// E2A YouTube Comedy — the 3D stage: canvas, camera, gym, lights, cast, ball.
import React from 'react';
import {ThreeCanvas} from '@remotion/three';
import {useThree} from '@react-three/fiber';
import * as THREE from 'three';
import {Gym, GymLights} from './gym';

export type Cam = {pos: [number, number, number]; target: [number, number, number]; fov: number; roll?: number};

const CameraSync: React.FC<{cam: Cam}> = ({cam}) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  camera.position.set(...cam.pos);
  camera.up.set(0, 1, 0);
  camera.lookAt(...cam.target);
  if (cam.roll) camera.rotateZ(cam.roll);
  camera.fov = cam.fov;
  camera.near = 0.05;
  camera.far = 80;
  camera.updateProjectionMatrix();
  return null;
};

let ballTex: THREE.Texture | null = null;
const getBallTex = () => {
  if (ballTex) return ballTex;
  const c = document.createElement('canvas');
  c.width = 512;
  c.height = 256;
  const g = c.getContext('2d')!;
  g.fillStyle = '#D2652A';
  g.fillRect(0, 0, 512, 256);
  for (let i = 0; i < 5000; i++) {
    g.fillStyle = i % 2 ? 'rgba(0,0,0,0.09)' : 'rgba(255,220,180,0.07)';
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
  ballTex = new THREE.CanvasTexture(c);
  ballTex.colorSpace = THREE.SRGBColorSpace;
  return ballTex;
};

export const Ball: React.FC<{pos: THREE.Vector3; spin?: number}> = ({pos, spin = 0}) => (
  <mesh position={pos} rotation={[spin, spin * 0.3, 0]} castShadow>
    <sphereGeometry args={[0.121, 32, 20]} />
    <meshStandardMaterial map={getBallTex()} roughness={0.6} />
  </mesh>
);

export const Stage: React.FC<{cam: Cam; W: number; H: number; focus: [number, number, number]; swish?: number; children: React.ReactNode}> = ({cam, W, H, focus, swish, children}) => (
  <ThreeCanvas
    width={W}
    height={H}
    shadows
    gl={{antialias: true, toneMapping: THREE.ACESFilmicToneMapping, toneMappingExposure: 1.08, outputColorSpace: THREE.SRGBColorSpace}}
    onCreated={({gl}) => {
      gl.shadowMap.type = THREE.PCFSoftShadowMap;
    }}
    camera={{fov: cam.fov, near: 0.05, far: 80}}
  >
    <CameraSync cam={cam} />
    <color attach="background" args={['#2A2D33']} />
    <GymLights focus={focus} />
    <Gym swish={swish} />
    {children}
  </ThreeCanvas>
);
