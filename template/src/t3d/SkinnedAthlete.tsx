// E2A 3D engine — LAB: deformable player (skinned MakeHuman-based mesh exported from Blender as .glb) driven by bone
// world rotations in play coordinates (skelclip.ts). The .glb animation is NOT played with a mixer: every frame the
// bones are set from the pose of that play time (pure function of the frame).
import React from 'react';
import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {cancelRender, continueRender, delayRender, staticFile} from 'remotion';
import type {V3} from '../tactical/geometry.ts';
import type {ClipBone, Q} from './skelclip.ts';
import {W3} from './Athlete';

const cache = new Map<string, Promise<THREE.Group>>();
/** load a .glb from public/ once per tab, holding the render until it is ready */
export const useGlb = (src?: string) => {
  const [g, setG] = React.useState<THREE.Group | null>(null);
  const [h] = React.useState(() => (src ? delayRender(`glb ${src}`) : null));
  React.useEffect(() => {
    if (!src) return;
    let p = cache.get(src);
    if (!p) {
      p = new GLTFLoader().loadAsync(staticFile(src)).then((r) => {
        r.scene.traverse((o) => {
          const m = o as THREE.Mesh;
          if (m.isMesh) {
            m.castShadow = true;
            m.receiveShadow = true;
            m.frustumCulled = false; // the bind-pose bounds sit at the origin, the player does not
          }
        });
        return r.scene;
      });
      cache.set(src, p);
    }
    p.then((s) => {
      setG(s);
      if (h !== null) continueRender(h);
    }).catch((e) => cancelRender(e));
  }, [src, h]);
  return g;
};

/** play-space quaternion -> three.js space (x, z, -y), same mapping as W3 */
const toThree = (q: Q) => new THREE.Quaternion(q[0], q[2], -q[1], q[3]);

type Rig = {bones: Map<string, THREE.Bone>; rest3: Map<string, THREE.Quaternion>; order: string[]; root: THREE.Object3D};
const rigCache = new WeakMap<THREE.Group, Rig>();
const rigOf = (scene: THREE.Group, clipBones: ClipBone[]): Rig => {
  let r = rigCache.get(scene);
  if (r) return r;
  scene.updateMatrixWorld(true);
  const bones = new Map<string, THREE.Bone>();
  const rest3 = new Map<string, THREE.Quaternion>();
  for (const b of clipBones) {
    // GLTFLoader sanitizes node names (PropertyBinding: 'clavicle.L' -> 'clavicleL')
    const o = (scene.getObjectByName(b.name) ?? scene.getObjectByName(THREE.PropertyBinding.sanitizeNodeName(b.name))) as THREE.Bone | undefined;
    if (!o) throw new Error(`bone ${b.name} missing in the glb`);
    bones.set(b.name, o);
    rest3.set(b.name, o.getWorldQuaternion(new THREE.Quaternion()));
  }
  r = {bones, rest3, order: clipBones.map((b) => b.name), root: bones.get(clipBones[0].name)!.parent!};
  rigCache.set(scene, r);
  return r;
};

export const SkinnedAthlete: React.FC<{scene: THREE.Group; clipBones: ClipBone[]; bones: Record<string, Q>; hips: V3}> = ({scene, clipBones, bones, hips}) => {
  const rig = rigOf(scene, clipBones);
  const world = new Map<string, THREE.Quaternion>();
  for (const b of clipBones) {
    // delta from the rest orientation, in play space, carried to three space and applied to the glb rest
    const d = toThree(bones[b.name]).multiply(toThree(b.R).invert());
    world.set(b.name, d.multiply(rig.rest3.get(b.name)!));
  }
  rig.root.updateWorldMatrix(true, false);
  const rootQ = rig.root.getWorldQuaternion(new THREE.Quaternion());
  for (const b of clipBones) {
    const bone = rig.bones.get(b.name)!;
    const parentQ = b.parent ? world.get(b.parent)! : rootQ;
    bone.quaternion.copy(parentQ.clone().invert().multiply(world.get(b.name)!));
    if (!b.parent) {
      const p = W3(hips);
      bone.position.copy(rig.root.worldToLocal(new THREE.Vector3(p[0], p[1], p[2])));
    }
  }
  scene.updateMatrixWorld(true);
  return <primitive object={scene} />;
};
