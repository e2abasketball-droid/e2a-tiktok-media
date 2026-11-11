// TacticalCourt: FIBA half court projected through the camera (floor, planks, paint, lines,
// brand apron, light pool) and the basket (stanchion, backboard, rim, net) as a depth-sorted item.
import React from 'react';
import {GOLD, NAVY} from '../pro/brand';
import type {Projector, V3} from './geometry.ts';
import {FIBA, courtLines, floorPath, polyPath, segPath, arc} from './geometry.ts';

export const COURT = {
  wood: '#A8784C',
  woodDark: '#8C603A',
  apron: '#0E2246',
  paint: NAVY,
  line: 'rgba(255,255,255,0.92)',
};

export const TacticalCourt: React.FC<{pr: Projector; id: string}> = ({pr, id}) => {
  const {halfW, halfL, keyHalfW, ftY, ftR} = FIBA;
  const ppm = pr.p([0, 6, 0]).s; // pixels per metre around the key: line widths follow the zoom
  const lw = Math.max(1.6, Math.min(7, ppm * 0.05));
  const planks: React.ReactNode[] = [];
  for (let x = -halfW; x <= halfW + 1e-6; x += 0.5) {
    const d = segPath(pr, [x, 0, 0], [x, halfL, 0]);
    if (d) planks.push(<path key={x} d={d} stroke={Math.round((x + 10) * 2) % 3 === 0 ? 'rgba(60,30,10,0.22)' : 'rgba(255,230,190,0.07)'} strokeWidth={Math.max(0.6, lw * 0.35)} />);
  }
  const apron = polyPath(pr, [[-halfW - 2.2, -1.8, 0], [halfW + 2.2, -1.8, 0], [halfW + 2.2, halfL + 3, 0], [-halfW - 2.2, halfL + 3, 0]]);
  const floor = polyPath(pr, [[-halfW, 0, 0], [halfW, 0, 0], [halfW, halfL, 0], [-halfW, halfL, 0]]);
  const paint = polyPath(pr, [[-keyHalfW, 0, 0.002], [keyHalfW, 0, 0.002], [keyHalfW, ftY, 0.002], [-keyHalfW, ftY, 0.002]]);
  const ftTop = floorPath(pr, arc([0, ftY], ftR, 0, Math.PI), true, 0.002);
  const centre = floorPath(pr, arc([0, halfL], FIBA.centreR, Math.PI, 2 * Math.PI), true, 0.002);
  const pool = pr.p([0, 5, 0]);
  return (
    <g>
      <defs>
        <radialGradient id={`pool-${id}`} cx={pool.x} cy={pool.y} r={Math.max(500, ppm * 11)} gradientUnits="userSpaceOnUse">
          <stop offset="0" stopColor="rgba(255,236,200,0.30)" />
          <stop offset="0.55" stopColor="rgba(255,236,200,0.06)" />
          <stop offset="1" stopColor="rgba(0,0,0,0.38)" />
        </radialGradient>
        <linearGradient id={`wood-${id}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={COURT.woodDark} />
          <stop offset="1" stopColor={COURT.wood} />
        </linearGradient>
      </defs>
      {apron && <path d={apron} fill={COURT.apron} />}
      {floor && <path d={floor} fill={`url(#wood-${id})`} />}
      <g clipPath={floor ? undefined : undefined}>{planks}</g>
      {paint && <path d={paint} fill={COURT.paint} opacity={0.94} />}
      {ftTop && <path d={ftTop} fill={COURT.paint} opacity={0.94} />}
      {centre && <path d={centre} fill={COURT.paint} opacity={0.94} />}
      {floor && <path d={floor} fill={`url(#pool-${id})`} />}
      <g fill="none" stroke={COURT.line} strokeLinejoin="round" strokeLinecap="round">
        {courtLines().map((l, i) => {
          const d = floorPath(pr, l.pts, l.close, 0.004);
          return d ? <path key={i} d={d} strokeWidth={lw * (l.w ?? 1)} /> : null;
        })}
        {/* free-throw circle, lower half dashed */}
        {(() => {
          const d = floorPath(pr, arc([0, ftY], ftR, Math.PI, 2 * Math.PI), false, 0.004);
          return d ? <path d={d} strokeWidth={lw} strokeDasharray={`${lw * 3} ${lw * 3}`} /> : null;
        })()}
        {/* lane marks */}
        {[1.75, 2.6, 3.45].map((y) =>
          [-1, 1].map((s) => {
            const d = segPath(pr, [s * keyHalfW, y, 0.004], [s * (keyHalfW + 0.1), y, 0.004]);
            return d ? <path key={`${y}${s}`} d={d} strokeWidth={lw} /> : null;
          }),
        )}
      </g>
      {/* gold brand stripe on the baseline apron */}
      {(() => {
        const d = polyPath(pr, [[-halfW, -0.55, 0.003], [halfW, -0.55, 0.003], [halfW, -0.45, 0.003], [-halfW, -0.45, 0.003]]);
        return d ? <path d={d} fill={GOLD} opacity={0.75} /> : null;
      })()}
    </g>
  );
};

/** Basket parts in world space; drawn as one depth-sorted item. */
export const Basket: React.FC<{pr: Projector; netSwish?: number}> = ({pr, netSwish = 0}) => {
  const {basket, rimZ, rimR, boardY, boardHalfW, boardZ0, boardZ1} = FIBA;
  const s = pr.p([0, boardY, rimZ]).s;
  const lw = Math.max(1, s * 0.03);
  const board = polyPath(pr, [[-boardHalfW, boardY, boardZ0], [boardHalfW, boardY, boardZ0], [boardHalfW, boardY, boardZ1], [-boardHalfW, boardY, boardZ1]]);
  const inner = polyPath(pr, [[-0.295, boardY - 0.01, rimZ + 0.15], [0.295, boardY - 0.01, rimZ + 0.15], [0.295, boardY - 0.01, rimZ + 0.6], [-0.295, boardY - 0.01, rimZ + 0.6]]);
  const pole = null; // the stanchion is left out: from behind the baseline it would cover the play
  const arm = segPath(pr, [0, boardY + 0.02, boardZ1], [0, boardY - 0.25, boardZ1 + 0.25]);
  const rimPts: V3[] = Array.from({length: 24}, (_, i) => [basket[0] + rimR * Math.cos((i / 24) * 2 * Math.PI), basket[1] + rimR * Math.sin((i / 24) * 2 * Math.PI), rimZ]);
  const rim = polyPath(pr, rimPts);
  const net: React.ReactNode[] = [];
  const sway = Math.sin(netSwish * 18) * Math.exp(-netSwish * 3) * 0.06;
  for (let i = 0; i < 12; i++) {
    const a = (i / 12) * 2 * Math.PI;
    const top: V3 = [basket[0] + rimR * Math.cos(a), basket[1] + rimR * Math.sin(a), rimZ];
    const bot: V3 = [basket[0] + rimR * 0.55 * Math.cos(a + 0.4) + sway, basket[1] + rimR * 0.55 * Math.sin(a + 0.4), rimZ - 0.42 + Math.abs(sway)];
    const d = segPath(pr, top, bot);
    if (d) net.push(<path key={i} d={d} stroke="rgba(255,255,255,0.75)" strokeWidth={lw * 0.6} />);
  }
  const near = pr.p([basket[0], basket[1], rimZ]).z < 1.2; // camera next to the rim: skip it rather than smear it
  if (near) return null;
  return (
    <g>
      {void pole}
      {arm && <path d={arm} stroke="#1A2B4C" strokeWidth={Math.max(2, s * 0.07)} strokeLinecap="round" />}
      {board && <path d={board} fill="rgba(210,230,255,0.22)" stroke="rgba(255,255,255,0.9)" strokeWidth={lw} />}
      {inner && <path d={inner} fill="none" stroke="rgba(255,255,255,0.9)" strokeWidth={lw * 0.8} />}
      {net}
      {rim && <path d={rim} fill="none" stroke="#E4572E" strokeWidth={Math.max(1.5, s * 0.035)} />}
    </g>
  );
};
