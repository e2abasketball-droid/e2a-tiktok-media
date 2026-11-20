// E2A 3D engine — deformable player (skinned MakeHuman-based mesh exported from Blender as .glb) driven by bone
// world rotations in play coordinates (skelclip.ts). The .glb animation is NOT played with a mixer: every frame the
// bones are set from the pose of that play time (pure function of the frame: same image when played, slowed down or
// reached by seeking).
// 2026-11-19 (e2a-player-v1): one INSTANCE per player (SkeletonUtils.clone: own skeleton, own pose state), uniform
// scale to the player's height, per-player skin tone and jersey number (canvas texture with the same UV layout as
// tools/blender/build_player.py). A .glb that fails to load does not stop the render: useGlb reports the error and
// Scene3D falls back to the capsule athlete (reason in the render log).
import React from 'react';
import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import * as SkeletonUtils from 'three/examples/jsm/utils/SkeletonUtils.js';
import {continueRender, delayRender, staticFile} from 'remotion';
import type {V3} from '../tactical/geometry.ts';
import type {ClipBone, Q} from './skelclip.ts';
import {W3} from './Athlete';

type GlbState = {scene: THREE.Group | null; error?: string};
const cache = new Map<string, Promise<THREE.Group>>();
/** load .glb files from public/ once per tab, holding the render until they are ready (or failed) */
export const useGlbs = (srcs: string[]): Record<string, GlbState> => {
  const key = srcs.join('|');
  const [st, setSt] = React.useState<Record<string, GlbState>>({});
  const [h] = React.useState(() => (srcs.length ? delayRender(`glb ${key}`, {timeoutInMilliseconds: 120000}) : null));
  React.useEffect(() => {
    if (!srcs.length) return;
    Promise.all(
      srcs.map((src) => {
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
        return p.then(
          (scene) => [src, {scene}] as const,
          (e: Error) => {
            console.error(`[E2A players3d] FALLBACK: ${src} did not load (${e?.message ?? e}) -> capsule athlete`);
            return [src, {scene: null, error: String(e?.message ?? e)}] as const;
          },
        );
      }),
    ).then((rs) => setSt(Object.fromEntries(rs)));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  // release the frame only once the loaded scenes are COMMITTED (continuing in the same tick as setState let Remotion
  // take the screenshot before React re-rendered: the players were drawn as capsules)
  const ready = srcs.every((s) => st[s]);
  React.useEffect(() => {
    if (ready && h !== null) continueRender(h);
  }, [ready, h]);
  return st;
};
/** single-file version (lab) */
export const useGlb = (src?: string) => {
  const st = useGlbs(src ? [src] : []);
  return src ? (st[src]?.scene ?? null) : null;
};

/** play-space quaternion -> three.js space (x, z, -y), same mapping as W3 */
const toThree = (q: Q) => new THREE.Quaternion(q[0], q[2], -q[1], q[3]);

// ---------------------------------------------------------------- per-player jersey texture (number front and back)
const jerseyTex = new Map<string, THREE.Texture>();
const shade = (hex: string, f: number) => {
  const c = new THREE.Color(hex);
  return `#${c.multiplyScalar(f).getHexString()}`;
};
export const jerseyTexture = (kit: Record<string, string>, num: string) => {
  const key = `${kit.jersey}|${kit.trim}|${kit.number}|${num}`;
  const hit = jerseyTex.get(key);
  if (hit) return hit;
  const W = 1024;
  const H = 512;
  const c = document.createElement('canvas');
  c.width = W;
  c.height = H;
  const g = c.getContext('2d')!;
  g.fillStyle = kit.jersey;
  g.fillRect(0, 0, W, H);
  const dark = new THREE.Color(kit.jersey).getHSL({h: 0, s: 0, l: 0}).l < 0.5;
  // mesh fabric: deterministic speckle (same idea as the .blend texture)
  const n1 = shade(kit.jersey, dark ? 1.35 : 1.03);
  const n2 = shade(kit.jersey, dark ? 0.62 : 0.94);
  for (let i = 0; i < 9000; i++) {
    g.fillStyle = i % 2 ? n1 : n2;
    g.fillRect((i * 7919) % W, (i * 3571) % H, 1, 1);
  }
  // side piping under the arms (u = 0, 0.5, 1)
  g.fillStyle = kit.trim;
  for (const u of [0, 0.5, 1]) g.fillRect(u * W - 4, 0, 8, H);
  // number: front at u = 0.25, back at u = 0.75 (bigger), centred at 42 % from the top (v grows downward, flipY off)
  g.textAlign = 'center';
  g.textBaseline = 'middle';
  for (const [u, s] of [
    [0.25, 1.0],
    [0.75, 1.25],
  ] as const) {
    g.save();
    g.translate(u * W, H * 0.42);
    // the cylindrical UV stretches v ~1.37x relative to u on the torso: squash vertically so the digits keep Anton's shape
    g.scale(1.05 * s, 0.74 * s);
    g.font = '900 230px Anton, Impact, sans-serif';
    g.lineJoin = 'round';
    g.lineWidth = 12;
    g.strokeStyle = kit.trim;
    g.strokeText(num, 0, 0);
    g.fillStyle = kit.number;
    g.fillText(num, 0, 0);
    g.restore();
  }
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.flipY = false;
  t.anisotropy = 4;
  jerseyTex.set(key, t);
  return t;
};

type Rig = {bones: Map<string, THREE.Bone>; rest3: Map<string, THREE.Quaternion>; root: THREE.Object3D};
const rigOf = (scene: THREE.Object3D, clipBones: ClipBone[]): Rig => {
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
  return {bones, rest3, root: bones.get(clipBones[0].name)!.parent!};
};


// ---------------------------------------------------------------- cloth fix (2026-11-20, Pistol Fake Handoff close 3/4)
// At hook distance the posed body skin poked through the jersey / shorts near the straps, neck and hems (jagged white /
// skin edges that read as torn shirts). 'academy' look only. Tried and dropped: dropping the skin triangles under the
// cloth + inflating the cloth (the straps sank deeper than the margin: shredded shoulders) and copying the body's skin
// weights onto the cloth (nearest / K-nearest: shards following the arms, the piping flew off).
// Kept: (1) the jersey and shorts are drawn FRONT faces only (the glb marks them double-sided: the navy / white
// triangles at the straps and neck were the INSIDE of the shirt seen through the gaps); (2) a view-space depth bias:
// jersey 3 cm (+5 cm on the top 12 cm: straps, neck), shorts 5 cm, piping 3.6 cm (+5 cm on the straps).
// view-space depth bias: the cloth is drawn as if it were d metres closer to the camera (depth only: position on screen
// unchanged), so skin that pokes through it by less than d stays hidden behind the jersey / shorts; the trims get a
// little more so the piping stays on top of the cloth edge. An arm in front of the torso is > d away in practice.
const clothBias = (mat: THREE.Material, d: number, strap = 0) => {
  mat.onBeforeCompile = (sh) => {
    if (strap) sh.vertexShader = 'attribute float e2aStrap;\n' + sh.vertexShader;
    sh.vertexShader = sh.vertexShader.replace('#include <project_vertex>', `#include <project_vertex>
  {
    vec4 mvB = mvPosition; mvB.z += ${d.toFixed(4)}${strap ? ` + ${strap.toFixed(4)} * e2aStrap` : ''};
    vec4 pB = projectionMatrix * mvB;
    gl_Position.z = pB.z / pB.w * gl_Position.w;
  }`);
  };
  mat.customProgramCacheKey = () => `e2a-clothbias-${d}-${strap}`;
  mat.needsUpdate = true;
};
// shoulder straps and neck: the top 12 cm of the jersey (bind pose, y up) get up to `strap` more bias (they sank up to
// ~7 cm under the posed deltoid / trapezius skin), fading out over the next 8 cm
const strapWeights = (g: THREE.BufferGeometry) => {
  if (g.getAttribute('e2aStrap')) return;
  const P = g.attributes.position; let top = -1e9;
  for (let i = 0; i < P.count; i++) top = Math.max(top, P.getY(i));
  const w = new Float32Array(P.count);
  for (let i = 0; i < P.count; i++) { const dy = top - P.getY(i); w[i] = dy <= 0.12 ? 1 : Math.max(0, 1 - (dy - 0.12) / 0.08); }
  g.setAttribute('e2aStrap', new THREE.BufferAttribute(w, 1));
};

/** one independent instance of a player mesh: own skeleton (pose state), own skin and jersey materials */
type Inst = {obj: THREE.Object3D; rig: Rig};
const instances = new Map<string, Inst>();
const instanceOf = (template: THREE.Group, key: string, bonesDesc: ClipBone[], look: {skin?: string; num?: string; kit?: Record<string, string>; profile?: 'academy'}) => {
  const k = `${template.uuid}|${key}|${look.skin}|${look.num}|${look.profile ?? ''}`;
  let it = instances.get(k);
  if (it) return it;
  const obj = SkeletonUtils.clone(template);
  obj.traverse((o) => {
    const m = o as THREE.Mesh;
    if (!m.isMesh) return;
    const mats = (Array.isArray(m.material) ? m.material : [m.material]).map((mt) => {
      const mm = mt as THREE.MeshStandardMaterial;
      // 'academy' look (2026-11-20): matte cloth with a soft sheen, satin skin, shoes and soles with their own response
      const matte = (c: THREE.MeshStandardMaterial) => {
        if (look.profile !== 'academy') return c;
        const n = c.name;
        const set = (r: number) => (c.roughness = r);
        if (n.startsWith('E2A_jersey') || n.startsWith('E2A_shorts')) {
          set(0.93);
          const ph = c as THREE.MeshPhysicalMaterial;
          if (ph.isMeshPhysicalMaterial) {
            ph.sheen = 0.55;
            ph.sheenRoughness = 0.85;
          }
        } else if (n.startsWith('E2A_skin')) set(0.62);
        else if (n.startsWith('E2A_shoe')) set(0.55);
        else if (n.startsWith('E2A_trim')) set(0.75);
        c.envMapIntensity = 0.6;
        return c;
      };
      if (mm.name.startsWith('E2A_skin') && look.skin) {
        const c = mm.clone();
        c.color = new THREE.Color(look.skin);
        return matte(c);
      }
      if (mm.name.startsWith('E2A_jersey') && look.num && look.kit) {
        const c = mm.clone();
        c.map = jerseyTexture(look.kit, look.num);
        c.color = new THREE.Color('#ffffff');
        return matte(c);
      }
      return look.profile === 'academy' ? matte(mm.clone()) : mm;
    });
    m.material = Array.isArray(m.material) ? mats : mats[0];
  });
  if (look.profile === 'academy') {
    obj.traverse((o) => {
      const m = o as THREE.Mesh;
      if (!m.isMesh) return;
      for (const mt of Array.isArray(m.material) ? m.material : [m.material]) {
        if (mt.name.startsWith('E2A_jersey')) { strapWeights(m.geometry); clothBias(mt, 0.03, 0.05); mt.side = THREE.FrontSide; }
        else if (mt.name.startsWith('E2A_shorts')) { clothBias(mt, 0.05); mt.side = THREE.FrontSide; }
        else if (mt.name.startsWith('E2A_trim') && m.name.includes('Jersey')) { strapWeights(m.geometry); clothBias(mt, 0.036, 0.05); }
        else if (mt.name.startsWith('E2A_trim')) clothBias(mt, 0.036);
      }
    });
  }
  // rest orientations measured on the template's bind pose (the clone shares it)
  it = {obj, rig: rigOf(obj, bonesDesc)};
  instances.set(k, it);
  return it;
};

export const SkinnedAthlete: React.FC<{
  scene: THREE.Group;
  clipBones: ClipBone[];
  bones: Record<string, Q>;
  hips: V3;
  /** instance key (player id); one skeleton per key */
  inst?: string;
  /** uniform scale (player height / rig height) */
  scale?: number;
  skin?: string;
  num?: string;
  kit?: Record<string, string>;
  /** 2026-11-20 look profile ('academy': matte cloth, satin skin) */
  look?: 'academy';
}> = ({scene, clipBones, bones, hips, inst = 'lab', scale = 1, skin, num, kit, look}) => {
  const {obj, rig} = instanceOf(scene, inst, clipBones, {skin, num, kit, profile: look});
  obj.scale.setScalar(scale);
  obj.updateMatrixWorld(true);
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
  obj.updateMatrixWorld(true);
  return <primitive object={obj} />;
};
