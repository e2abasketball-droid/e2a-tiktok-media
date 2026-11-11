// One tactical viewport: court + basket + 10 players + ball through a camera, with world overlays.
// Used full-frame and twice side by side (ComparisonSplitScreen).
import React from 'react';
import type {CameraState} from './geometry.ts';
import {FIBA, makeProjector} from './geometry.ts';
import type {Overlay} from './edit.ts';
import type {Frame, Play} from './play.ts';
import {sample} from './play.ts';
import {Basket, TacticalCourt} from './Court';
import {BallShadow, BallSprite, PlayerAvatar, PlayerDefs, PlayerShadow} from './Player';
import type {OvCtx} from './overlays';
import {AnimatedRoute, Corridor, Doors, OpenSpace, PassLane, Ring, Separation, ShotWindow, SwitchArrow, TagBounds, Trail, WorldLabel, resolveT} from './overlays';

export type LiveOverlay = Overlay & {age: number; dur: number};

const FLOOR = new Set(['route', 'trail', 'corridor', 'doors', 'passLane', 'openSpace', 'separation', 'switch']);

const renderOverlay = (o: LiveOverlay, c: OvCtx, i: number): React.ReactNode => {
  const g = (k: string) => o[k] as never;
  switch (o.type) {
    case 'route':
      return <AnimatedRoute key={i} c={c} player={g('player')} from={resolveT(c.play, o.t0 ?? 0)} to={resolveT(c.play, o.t1 ?? c.play.duration)} age={o.age} mode={g('mode')} tone={g('tone')} dashed={g('dashed')} opacity={g('opacity')} />;
    case 'trail':
      return <Trail key={i} c={c} player={g('player')} len={g('len')} age={o.age} />;
    case 'corridor':
      return <Corridor key={i} c={c} a={g('a')} b={g('b')} lineY={g('lineY') ?? FIBA.ftY} age={o.age} label={g('label')} />;
    case 'doors':
      return <Doors key={i} c={c} a={g('a')} b={g('b')} lineY={g('lineY') ?? FIBA.ftY} contact={o.contact !== undefined ? resolveT(c.play, o.contact) : undefined} age={o.age} />;
    case 'separation':
      return <Separation key={i} c={c} a={g('a')} b={g('b')} label={g('label')} age={o.age} />;
    case 'passLane':
      return <PassLane key={i} c={c} from={g('passer')} to={g('receiver')} at={resolveT(c.play, o.at)} age={o.age} label={g('label')} />;
    case 'openSpace':
      return <OpenSpace key={i} c={c} at={g('at')} r={g('r') ?? 1.6} age={o.age} label={g('label')} tone={g('tone')} />;
    case 'switch':
      return <SwitchArrow key={i} c={c} from={g('defender')} toPoint={g('toPoint')} age={o.age} label={g('label')} />;
    case 'ring':
      return <Ring key={i} c={c} player={g('player')} age={o.age} label={g('label')} tone={g('tone')} />;
    case 'shotWindow':
      return <ShotWindow key={i} c={c} player={g('player')} age={o.age} label={g('label')} />;
    case 'label':
      return <WorldLabel key={i} c={c} at={g('at')} text={g('text')} tone={g('tone')} size={g('size')} />;
    default:
      return null;
  }
};

export const TacticalView: React.FC<{
  play: Play;
  pt: number;
  cam: CameraState;
  W: number;
  H: number;
  overlays: LiveOverlay[];
  id: string;
  focus?: 'O' | 'X';
  dimIds?: string[];
  highlightIds?: string[];
  labels?: boolean;
  hideIds?: string[];
  tagScale?: number;
  motionBlur?: number;
}> = ({play, pt, cam, W, H, overlays, id, focus, dimIds = [], highlightIds = [], labels = true, tagScale = 1, hideIds = []}) => {
  const pr = makeProjector(cam, W, H);
  const frameAt = (t: number): Frame => sample(play, t);
  const f = frameAt(pt);
  const c: OvCtx = {pr, play, f, pt, frameAt, id};
  // depth sort: far first
  const items: {z: number; node: React.ReactNode}[] = [];
  Object.values(f.players).forEach((p) => {
    if (hideIds.includes(p.spec.id)) return;
    const z = pr.p([p.pos[0], p.pos[1], 0.9]).z;
    const dim = (focus && p.spec.team !== focus ? 0.6 : 0) + (dimIds.includes(p.spec.id) ? 0.7 : 0);
    items.push({z, node: <PlayerAvatar key={p.spec.id} pr={pr} p={p} look={{dim: Math.min(1, dim), highlight: highlightIds.includes(p.spec.id), label: labels}} badgeMin={26 * tagScale} />});
  });
  const made = play.ball.find((e) => (e.type === 'shot' || e.type === 'layup') && e.make && pt >= e.t1);
  const swishAge = made ? pt - (made as {t1: number}).t1 : 0;
  items.push({z: pr.p([0, FIBA.boardY, 3.0]).z, node: <Basket key="basket" pr={pr} netSwish={swishAge} />});
  const spin = pt * 720;
  items.push({z: pr.p(f.ball.pos).z - 0.05, node: <BallSprite key="ball" pr={pr} pos={f.ball.pos} spin={spin} />});
  items.sort((a, b) => b.z - a.z);
  const floor = overlays.filter((o) => FLOOR.has(o.type));
  const top = overlays.filter((o) => !FLOOR.has(o.type));
  return (
    <TagBounds.Provider value={W === 1080 ? {x0: 70, x1: 1010, y0: 250, y1: 1290, scale: tagScale} : {x0: 12, x1: W - 12, y0: 40, y1: H - 40, scale: tagScale}}>
      <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} style={{position: 'absolute', left: 0, top: 0, overflow: 'hidden'}}>
        <PlayerDefs />
        <TacticalCourt pr={pr} id={id} />
        {floor.map((o, i) => renderOverlay(o, c, i))}
        {Object.values(f.players).filter((p) => !hideIds.includes(p.spec.id)).map((p) => (
          <PlayerShadow key={p.spec.id} pr={pr} p={p} />
        ))}
        <BallShadow pr={pr} pos={f.ball.pos} />
        {items.map((it) => it.node)}
        {top.map((o, i) => renderOverlay(o, c, i))}
      </svg>
    </TagBounds.Provider>
  );
};
