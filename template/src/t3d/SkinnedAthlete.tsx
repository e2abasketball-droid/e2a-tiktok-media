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
import type {Cloth} from './cloth2.ts';
import {GARMENT3, garment3Follow, garment3Shorts} from './garment3.ts';
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

// ---------------------------------------------------------------- Realism V2 apparel (2026-11-21, cloth2.ts)
// v2 meshes (build_player.py --garment v2) carry _E2A_HEM / _E2A_EASE on the jersey. The trim (piping) along the hem gets
// the values of its nearest jersey vertex (bind pose), so the piping swings WITH the cloth. One set of uniforms per
// instance (sway, twist, flutter, stride phase, pelvis; object space), updated every frame from clothAt().
type ClothU = {uSway: {value: THREE.Vector3}; uTwist: {value: number}; uFlutter: {value: number}; uPhase: {value: number}; uPelvis: {value: THREE.Vector3}};
const clothAttrsDone = new WeakSet<THREE.BufferGeometry>();
const copyClothAttrs = (jersey: THREE.BufferGeometry, trim: THREE.BufferGeometry) => {
  if (clothAttrsDone.has(trim) || trim.getAttribute('_e2a_hem')) return;
  const PJ = jersey.attributes.position, H = jersey.getAttribute('_e2a_hem'), E = jersey.getAttribute('_e2a_ease');
  if (!H || !E) return;
  const PT = trim.attributes.position;
  const h = new Float32Array(PT.count), e = new Float32Array(PT.count);
  for (let i = 0; i < PT.count; i++) {
    let best = 1e9, bi = 0;
    const x = PT.getX(i), y = PT.getY(i), z = PT.getZ(i);
    for (let j = 0; j < PJ.count; j++) {
      const d = (PJ.getX(j) - x) ** 2 + (PJ.getY(j) - y) ** 2 + (PJ.getZ(j) - z) ** 2;
      if (d < best) {
        best = d;
        bi = j;
      }
    }
    h[i] = H.getX(bi);
    e[i] = E.getX(bi);
  }
  trim.setAttribute('_e2a_hem', new THREE.BufferAttribute(h, 1));
  trim.setAttribute('_e2a_ease', new THREE.BufferAttribute(e, 1));
  clothAttrsDone.add(trim);
};
/** v2 cloth material: secondary motion before the projection (object space), small depth bias after it (skin poking
 *  through at the straps / armholes), inside of the shirt drawn darker (DoubleSide: the loose hem shows its inside) */
const cloth2Material = (mat: THREE.Material, U: ClothU, bias: number, strap: number, inside: boolean, v3 = false) => {
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, U);
    sh.vertexShader =
      'uniform vec3 uSway; uniform float uTwist; uniform float uFlutter; uniform float uPhase; uniform vec3 uPelvis;\nattribute float _e2a_hem; attribute float _e2a_ease;\n' +
      (strap ? 'attribute float e2aStrap;\n' : '') +
      sh.vertexShader;
    sh.vertexShader = sh.vertexShader.replace('#include <skinning_vertex>', `#include <skinning_vertex>
  {
    float hem = _e2a_hem;
    if (hem > 0.0) {
      vec3 n = normalize(objectNormal);
      vec2 r = transformed.xz - uPelvis.xz;
      float a = uTwist * hem; float ca = cos(a); float sa = sin(a);
      vec2 rr = vec2(r.x * ca + r.y * sa, -r.x * sa + r.y * ca);
      vec3 d = vec3(rr.x - r.x, 0.0, rr.y - r.y) + uSway * hem;${v3 ? `
      // garment3 panel: the hem flares more on the side it swings toward (no rigid ring)
      { vec2 sh2 = uSway.xz; float sl = length(sh2); float rl = length(r);
        if (sl > 1e-5 && rl > 1e-5) { float pf = ${GARMENT3.panel.toFixed(3)} * dot(r / rl, sh2 / sl) * min(1.0, sl / ${GARMENT3.panelRef.toFixed(4)}); d.xz += sh2 * hem * pf; } }` : ''}
      float ang = atan(-r.y, r.x);
      d += n * (uFlutter * hem * sin(6.0 * ang + 6.2831853 * uPhase));
      vec2 nh = n.xz; float nl = length(nh);
      if (nl > 1e-5) { nh /= nl; float inward = -dot(d.xz, nh); float lim = 0.85 * _e2a_ease; if (inward > lim) d.xz += nh * (inward - lim); }
      transformed += d;
    }
  }`);
    sh.vertexShader = sh.vertexShader.replace('#include <project_vertex>', `#include <project_vertex>
  {
    vec4 mvB = mvPosition; mvB.z += ${bias.toFixed(4)}${strap ? ` + ${strap.toFixed(4)} * e2aStrap` : ''};
    vec4 pB = projectionMatrix * mvB;
    gl_Position.z = pB.z / pB.w * gl_Position.w;
  }`);
    if (inside) sh.fragmentShader = sh.fragmentShader.replace('#include <map_fragment>', '#include <map_fragment>\n  if (!gl_FrontFacing) diffuseColor.rgb *= 0.42;');
  };
  mat.customProgramCacheKey = () => `e2a-cloth2-${bias}-${strap}-${inside ? 1 : 0}${v3 ? '-g3' : ''}`;
  mat.needsUpdate = true;
};

// ---------------------------------------------------------------- Chicago V3 apparel (2026-11-22, garment3.ts)
// realism >= 3: the shorts (and their piping) get the garment3 corrections (tuck under the shirt, looser leg openings with
// a cloth band). Geometry is CLONED per template (a v2 player in the same render keeps the original buffers).
const g3Cache = new WeakMap<THREE.BufferGeometry, THREE.BufferGeometry>();
const g3Base = new WeakMap<THREE.BufferGeometry, ReturnType<typeof garment3Shorts>>();
const arrOf = (g: THREE.BufferGeometry) => ({P: g.attributes.position.array as Float32Array, N: g.attributes.normal.array as Float32Array,
  J: g.getAttribute('skinIndex').array as ArrayLike<number>, W: Float32Array.from(g.getAttribute('skinWeight').array as ArrayLike<number>)});
const g3Geometry = (src: THREE.BufferGeometry, out: {P: Float32Array; J: Uint16Array; W: Float32Array; hem: Float32Array; ease: Float32Array}) => {
  const g = src.clone();
  g.setAttribute('position', new THREE.BufferAttribute(out.P, 3));
  g.setAttribute('skinIndex', new THREE.Uint16BufferAttribute(out.J, 4));
  g.setAttribute('skinWeight', new THREE.BufferAttribute(out.W, 4));
  g.setAttribute('_e2a_hem', new THREE.BufferAttribute(out.hem, 1));
  g.setAttribute('_e2a_ease', new THREE.BufferAttribute(out.ease, 1));
  g.computeBoundingSphere();
  return g;
};

/** one independent instance of a player mesh: own skeleton (pose state), own skin and jersey materials */
type Inst = {obj: THREE.Object3D; rig: Rig; cloth?: ClothU};
const instances = new Map<string, Inst>();
const instanceOf = (template: THREE.Group, key: string, bonesDesc: ClipBone[], look: {skin?: string; num?: string; kit?: Record<string, string>; profile?: 'academy'; cloth2?: boolean; g3?: boolean}) => {
  const k = `${template.uuid}|${key}|${look.skin}|${look.num}|${look.profile ?? ''}|${look.cloth2 ? 2 : 1}${look.g3 ? '|g3' : ''}`;
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
  let clothU: ClothU | undefined;
  if (look.cloth2) {
    // Realism V2: jersey + its trims swing with cloth2 (needs the v2 attributes; a v1 mesh keeps the v1 path below)
    let jg: THREE.BufferGeometry | undefined;
    obj.traverse((o) => {
      const m = o as THREE.Mesh;
      if (m.isMesh && m.name.includes('Jersey') && !m.name.includes('Trim') && m.geometry.getAttribute('_e2a_hem')) jg = m.geometry;
    });
    if (jg) {
      clothU = {uSway: {value: new THREE.Vector3()}, uTwist: {value: 0}, uFlutter: {value: 0}, uPhase: {value: 0}, uPelvis: {value: new THREE.Vector3()}};
      obj.traverse((o) => {
        const m = o as THREE.Mesh;
        if (!m.isMesh) return;
        const mats = Array.isArray(m.material) ? m.material : [m.material];
        if (m.name.includes('Jersey') && m.name.includes('Trim')) copyClothAttrs(jg!, m.geometry);
        if (m.name.includes('Jersey')) {
          if (!m.geometry.getAttribute('e2aStrap')) strapWeights(m.geometry);
          const ms = mats.map((mt) => mt.clone());
          for (const mt of ms) {
            const isTrim = mt.name.startsWith('E2A_trim');
            if (!isTrim) mt.side = THREE.DoubleSide;
            cloth2Material(mt, clothU!, isTrim ? 0.016 : 0.012, 0.03, !isTrim, !!look.g3);
          }
          m.material = Array.isArray(m.material) ? ms : ms[0];
        } else if (look.g3 && m.name.includes('Shorts')) {
          // garment3: corrected shorts / piping geometry + the cloth band on the leg openings (same uniforms as the jersey)
          let sm: THREE.Mesh | undefined;
          obj.traverse((o2) => { const q = o2 as THREE.Mesh; if (q.isMesh && q.name.includes('Shorts') && !q.name.includes('Trim')) sm = q; });
          if (sm) {
            const srcG = (m.geometry.userData.g3src as THREE.BufferGeometry | undefined) ?? m.geometry;
            const shortsG = (sm.geometry.userData.g3src as THREE.BufferGeometry | undefined) ?? sm.geometry;
            let g = g3Cache.get(srcG);
            if (!g) {
              let base = g3Base.get(shortsG);
              if (!base) {
                const hips = (sm as THREE.SkinnedMesh).skeleton?.bones.findIndex((b) => b.name === 'hips') ?? 0;
                base = garment3Shorts(arrOf(jg!), arrOf(shortsG), Math.max(0, hips));
                g3Base.set(shortsG, base);
              }
              g = srcG === shortsG ? g3Geometry(srcG, base) : g3Geometry(srcG, garment3Follow(arrOf(srcG), arrOf(shortsG), base));
              g.userData.g3src = srcG;
              g3Cache.set(srcG, g);
            }
            m.geometry = g;
            const ms = mats.map((mt) => mt.clone());
            for (const mt of ms) {
              const isTrim = mt.name.startsWith('E2A_trim');
              mt.side = THREE.FrontSide;
              cloth2Material(mt, clothU!, isTrim ? 0.036 : 0.05, 0, false, true);
            }
            m.material = Array.isArray(m.material) ? ms : ms[0];
          }
        } else if (look.profile === 'academy') {
          for (const mt of mats) {
            if (mt.name.startsWith('E2A_shorts')) { clothBias(mt, 0.05); mt.side = THREE.FrontSide; }
            else if (mt.name.startsWith('E2A_trim')) clothBias(mt, 0.036);
          }
        }
      });
    }
  }
  if (look.profile === 'academy' && !clothU) {
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
  it = {obj, rig: rigOf(obj, bonesDesc), cloth: clothU};
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
  /** Realism V2 (cloth2.ts): the cloth state of this player at this frame (play space); needs a --garment v2 mesh */
  cloth?: Cloth;
  /** Chicago V3 (garment3.ts, play.realism >= 3): shorts tuck + loose leg openings + jersey panel swing */
  g3?: boolean;
}> = ({scene, clipBones, bones, hips, inst = 'lab', scale = 1, skin, num, kit, look, cloth, g3}) => {
  const {obj, rig, cloth: cu} = instanceOf(scene, inst, clipBones, {skin, num, kit, profile: look, cloth2: !!cloth, g3: !!cloth && !!g3});
  if (cu && cloth) {
    // object space of the instance = three world / scale (no rotation, origin at 0)
    const sw = W3(cloth.sway);
    cu.uSway.value.set(sw[0] / scale, sw[1] / scale, sw[2] / scale);
    cu.uTwist.value = cloth.twist;
    cu.uFlutter.value = cloth.flutter / scale;
    cu.uPhase.value = cloth.phase % 1;
    const pv = W3(hips);
    cu.uPelvis.value.set(pv[0] / scale, pv[1] / scale, pv[2] / scale);
  }
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
