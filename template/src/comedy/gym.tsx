// E2A YouTube Comedy — reusable court: a clean community gym built around the E2A engine's
// maple floor + basket (t3d/Court3D) with plain walls instead of an arena crowd, so "the court
// is empty" reads instantly. Coordinates: three.js, y up, baseline at z = 0, court toward -z.
import React from 'react';
import * as THREE from 'three';
import {Basket, buildFloor} from '../t3d/Court3D';

export const RIM = new THREE.Vector3(0, 3.05, -1.575);

const Wall: React.FC<{pos: [number, number, number]; rotY: number; w: number}> = ({pos, rotY, w}) => (
  <group position={pos} rotation={[0, rotY, 0]}>
    {/* lower padded band (navy) with a gold line, upper wall warm grey, high windows */}
    <mesh position={[0, 1.0, 0]} receiveShadow>
      <boxGeometry args={[w, 2, 0.2]} />
      <meshStandardMaterial color="#0E2147" roughness={0.8} />
    </mesh>
    <mesh position={[0, 2.03, 0.11]}>
      <boxGeometry args={[w, 0.06, 0.02]} />
      <meshStandardMaterial color="#C9A24D" roughness={0.4} metalness={0.3} />
    </mesh>
    <mesh position={[0, 5.5, -0.02]} receiveShadow>
      <boxGeometry args={[w, 7, 0.2]} />
      <meshStandardMaterial color="#C9C3B8" roughness={0.95} />
    </mesh>
    {Array.from({length: Math.floor(w / 4)}, (_, i) => (
      <mesh key={i} position={[-w / 2 + 2 + i * 4, 6.6, 0.09]}>
        <planeGeometry args={[2.6, 1.3]} />
        <meshBasicMaterial color="#E9F1FF" toneMapped={false} />
      </mesh>
    ))}
  </group>
);

export const Gym: React.FC<{swish?: number}> = ({swish = 0}) => {
  const tex = React.useMemo(() => buildFloor(), []);
  return (
    <group>
      {/* maple floor texture covers x -8.5..8.5, z 1.5..-15.5 */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, -7]} receiveShadow>
        <planeGeometry args={[17, 17]} />
        <meshStandardMaterial map={tex.map} roughnessMap={tex.rough} roughness={0.78} envMapIntensity={0.7} />
      </mesh>
      {/* run-off floor (plain maple tone) beyond the lines */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.004, -8]} receiveShadow>
        <planeGeometry args={[40, 40]} />
        <meshStandardMaterial color="#9C6B3E" roughness={0.85} />
      </mesh>
      <Wall pos={[0, 0, 3.2]} rotY={Math.PI} w={26} />
      <Wall pos={[-10.5, 0, -8]} rotY={Math.PI / 2} w={26} />
      <Wall pos={[10.5, 0, -8]} rotY={-Math.PI / 2} w={26} />
      <Wall pos={[0, 0, -19]} rotY={0} w={26} />
      {/* folded bleachers on the right sideline wall */}
      <mesh position={[10.0, 1.3, -8]} castShadow receiveShadow>
        <boxGeometry args={[0.7, 2.6, 9]} />
        <meshStandardMaterial color="#6E4C2C" roughness={0.8} />
      </mesh>
      {/* ceiling + light panels */}
      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, 9, -8]}>
        <planeGeometry args={[30, 30]} />
        <meshStandardMaterial color="#2A2D33" roughness={1} />
      </mesh>
      {Array.from({length: 12}, (_, i) => (
        <mesh key={i} position={[((i % 3) - 1) * 5.5, 8.9, -1 - Math.floor(i / 3) * 5]} rotation={[Math.PI / 2, 0, 0]}>
          <planeGeometry args={[2.2, 0.7]} />
          <meshBasicMaterial color="#FFF7EA" toneMapped={false} side={THREE.DoubleSide} />
        </mesh>
      ))}
      <Basket swish={swish} />
    </group>
  );
};

/** warm, soft gym lighting with a key that follows the action */
export const GymLights: React.FC<{focus: [number, number, number]}> = ({focus}) => {
  const target = React.useMemo(() => new THREE.Object3D(), []);
  target.position.set(...focus);
  return (
    <>
      <hemisphereLight args={['#E8EEFF', '#5A3B22', 0.9]} />
      <primitive object={target} />
      <spotLight position={[focus[0] + 2.5, 8.5, focus[2] + 4.5]} target={target} angle={0.75} penumbra={0.9} intensity={210} decay={2} color="#FFF1DE"
        castShadow shadow-mapSize-width={2048} shadow-mapSize-height={2048} shadow-bias={-0.0002} shadow-normalBias={0.02} shadow-radius={5} />
      <spotLight position={[focus[0] - 5, 6, focus[2] + 3]} target={target} angle={0.9} penumbra={1} intensity={70} decay={2} color="#DCE6FF" />
      <directionalLight position={[focus[0] - 1, 5, focus[2] - 8]} target={target} intensity={1.4} color="#FFE2B0" />
      <ambientLight intensity={0.25} />
    </>
  );
};
