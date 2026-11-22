// E2A 3D tactical composition ("Tactical3D"): plays + edit + narration timings -> vertical video.
// The edit is data (tactical/episodes/<id>.json): shots anchored to words of the real narration,
// play-time remaps (real speed, slow motion, freeze, rewind), 3D camera keys, world-space graphics
// (inside the 3D scene) and screen-space graphics (titles, stamps, labels, subtitles).
import React from 'react';
import {AbsoluteFill, Audio, Sequence, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import type {V2} from '../tactical/geometry.ts';
import type {Anchor, RemapKey} from '../tactical/edit.ts';
import {localResolver, makeTacticalResolver, remapAt, resolveRemap} from '../tactical/edit.ts';
import {ballPhase, posAt, routeOf, sample} from '../tactical/play.ts';
import type {CamKey3} from './camera3d.ts';
import {camera3At} from './camera3d.ts';
import type {LiveOv3, Ov3} from './overlays3d';
import {Overlays3D, projector} from './overlays3d';
import type {PlayWithActions} from './rig.ts';
import {Scene3D} from './Scene';
import type {AthleteRenderer} from './realism-v3/index.ts';
import type {FaceCfg} from './Scene';
import {choosePin, placePin} from './pinPlace';
import {FocusVignette, FreezeFrame, KineticTitle, Logo, OfferCounter, PinLabel, PremiumSubtitles, RewindTag, Stamp, StepBadge, StepCounter, TacticalHUD, sceneFx} from './screen3d';
import {Flash} from '../pro/fx';
import {countedSteps} from './overlays3d';
import '../theme';
import {LOGO} from '../brand';

type Word = {text: string; start: number; end: number};
type Timed = {from: Anchor; to?: Anchor};
type ScreenItem = Timed & ({type: 'title'; lines: string[]; y?: number; size?: number; gold?: number[]; sub?: string} | {type: 'stamp'; text: string; y?: number; tone?: 'gold' | 'white'; badge?: string; /** fully on from its first frame (hook frame 0: no fade-in) */ instant?: boolean} | {type: 'pin'; player: string; text: string; tone?: 'gold' | 'red' | 'white'; dy?: number; z?: number; size?: number} | {type: 'freeze'; label?: string} | {type: 'rewind'} | {type: 'logo'; big?: boolean; y?: number; width?: number} | {type: 'grade'} | {type: 'scrim'; opacity?: number} | {type: 'step'; n: number; text: string; y?: number} | {type: 'counter'; steps: Anchor[]; total?: number; y?: number; base?: number} | {type: 'stepCount'; player: string; labels: string[]; y?: number; gatherLabel?: boolean}
  /** 2026-11-19 (Spain PnR 2.0): frame dims around one player; small read chip; punch-in / whip on the 3D layer; flash */
  | {type: 'focus'; player: string; r?: number; strength?: number; z?: number} | {type: 'hud'; tag: string; text: string; y?: number}
  /** 2026-11-19 (catch fix): DIAGNOSTIC ONLY, never in a delivered episode: ball phase, owner, play time and a label */
  | {type: 'debugPhase'; label?: string}
  | {type: 'punch'; amount?: number} | {type: 'whip'; amount?: number; dir?: number} | {type: 'flash'; color?: string; strength?: number}
  /** 2026-11-21 (2-3 Zone): small caption chip (ILLUSTRATIVE COVERAGE); WrongTempo red edge tint */
  | {type: 'micro'; text: string; y?: number} | {type: 'tint'; color?: string; strength?: number}
  /** 2026-11-22 (Chicago V3): outcome chip (red TRAIL / blue UNDER / gold), anchored to a screen side and height */
  | {type: 'chip'; text: string; y?: number; tone?: 'red' | 'blue' | 'gold'; align?: 'left' | 'center' | 'right'; size?: number});
/** 2026-11-22 (Chicago V3 split screen): a SECOND live 3D view stacked under the shot's own view (same clock, own play,
 *  remap, camera and world graphics). The shot's view takes the top `ratio` of the frame. Shots without `split` are
 *  rendered exactly as before. */
export type Split3 = {play: string; remap: RemapKey[]; camera: CamKeyA[]; ov3?: (Timed & Ov3)[]; hide?: string[]; ratio?: number; athleteRenderer?: AthleteRenderer};
type CamKeyA = Omit<CamKey3, 'at'> & {at: Anchor};
/** 2026-11-22 Realism V3.2 comparison panels: N live 3D views stacked top to bottom with equal heights (same clock),
 *  each with its own renderer / motion / mesh / material switches; play, remap and camera default to the shot's.
 *  Shots without `panels` are rendered exactly as before. */
export type Panel3 = {play?: string; remap?: RemapKey[]; camera?: CamKeyA[]; hide?: string[]; athleteRenderer?: AthleteRenderer;
  athleteMotion?: 'engine' | 'v31' | 'v32'; athleteMesh?: 'v31' | 'v32'; neutral?: boolean; debug32?: boolean};
export type Shot3 = {
  id: string;
  at: Anchor;
  name: string;
  play: string;
  remap: RemapKey[];
  camera: CamKeyA[];
  ov3?: (Timed & Ov3 & {fromPlay?: string})[];
  screen?: ScreenItem[];
  sfx?: {at: Anchor; name: string; volume?: number}[];
  hide?: string[];
  /** 2026-11-17: warm practice gym or cold game arena (default: the arena as before); 2026-11-20: 'academy' look */
  env?: 'practice' | 'game' | 'academy' | 'cinema';
  /** 2026-11-19: 'A' = legacy capsule athletes in this shot (default: the episode's choice, else the E2A players) */
  players3d?: 'A' | 'C';
  /** 2026-11-18 (V4): gain on this shot's automatic sfx (0 = none, e.g. a quiet memory echo of the rim done by hand) */
  autoGain?: number;
  split?: Split3;
  /** 2026-11-22 Realism V3: athlete renderer of this shot (default: the episode's, else 'legacy') */
  athleteRenderer?: AthleteRenderer;
  /** 2026-11-22 Realism V3.2: stacked comparison panels (A/B/C, Test A / B / C) and single-view test switches */
  panels?: Panel3[];
  athleteMotion?: 'engine' | 'v31' | 'v32';
  athleteMesh?: 'v31' | 'v32';
  neutral?: boolean;
  debug32?: boolean;
};
export type Episode3 = {
  id: string;
  title: string;
  fps?: number;
  voice: string;
  voiceMix?: string;
  words: Word[];
  tail: number;
  music?: {src?: string; volume?: number};
  plays: Record<string, PlayWithActions>;
  shots: Shot3[];
  keywords?: string[];
  subtitleHide?: [Anchor, Anchor][];
  /** optional explicit subtitle bursts: number of words per burst, in order (must add up to the word count) */
  subtitleGroups?: number[]; subtitleY?: number; subtitleBlock?: boolean; subtitleYAt?: [Anchor, Anchor, number][]; gradeBottom?: number;
  /** sound by event (2026-11-13): bounces, catches, braking squeaks and the net, placed on their visible
   *  contact through each shot's remap (silent in freezes, rewinds and slow motion below 0.3x) */
  autoSfx?: boolean | {bounce?: number; catch?: number; squeak?: number; swish?: number; land?: number; rim?: number; players?: string[]};
  /** V2 pins: anchored to the posed head, flipped below the feet when they would cover another player */
  pinV2?: boolean;
  /** arena room tone under everything (looped) */
  ambience?: {src: string; volume?: number};
  /** stylised character heads with faces (expressions keyed per play in play.expr) */
  faces?: FaceCfg;
  /** 2026-11-19 default player package (src/t3d/player3d.ts): omitted or 'C' = E2A deformable players (offense /
   *  defense variants, validated clips by action, compatible rig animation otherwise); 'A' = legacy capsule athletes */
  players3d?: 'A' | 'C';
  /** 2026-11-20: look profile for every shot that does not set its own `env` ('academy' = master prompt 3D sec. 7.1) */
  env?: 'practice' | 'game' | 'academy' | 'cinema';
  /** 2026-11-22 Realism V3 feature flag: 'legacy' (default when omitted) | 'v3' (AthleteV3, src/t3d/realism-v3/) */
  athleteRenderer?: AthleteRenderer;
};

type Cue = {t: number; name: string; volume: number};
const eventCache = new Map<string, {pt: number; name: string; key: string}[]>();
/** contact events of a play, in play time (cached per play) */
const playEvents = (play: PlayWithActions, players: string[]) => {
  const hit = eventCache.get(play.id);
  if (hit) return hit;
  const ev: {pt: number; name: string; key: string}[] = [];
  // dribble bounces: local minima of the ball height while it is held and dribbled
  const step = 1 / 240;
  let z0 = Infinity;
  let z1 = Infinity;
  for (let t = 0; t <= play.duration; t += step) {
    const b = sample(play, t).ball;
    const dribbling = b.holder && b.event && b.event.type === 'hold' && (b.event as {dribble?: boolean}).dribble;
    const z = dribbling ? b.pos[2] : Infinity;
    if (z1 < 0.3 && z1 <= z0 && z1 < z) ev.push({pt: t - step, name: 'bounce', key: 'bounce'});
    z0 = z1;
    z1 = z;
  }
  for (const e of play.ball) {
    if (e.type === 'pass') ev.push({pt: e.t1, name: 'catch', key: 'catch'});
    if ((e.type === 'shot' || e.type === 'layup') && e.make !== false) ev.push({pt: e.t1, name: 'swish', key: 'swish'});
    if ((e.type === 'shot' || e.type === 'layup') && e.make === false) ev.push({pt: e.t1, name: 'rim', key: 'rim'});
    if (e.type === 'shot') ev.push({pt: e.t0 + 0.32, name: 'land', key: 'land'});
    if (e.type === 'layup') ev.push({pt: e.t0 + 0.48, name: 'land', key: 'land'});
  }
  // braking plants: a key player decelerates hard from a run (sneaker squeak)
  for (const id of players) {
    const wp = play.tracks[id];
    if (!wp) continue;
    const sp = (t: number) => {
      const a = posAt(wp, t - 0.01);
      const b = posAt(wp, t + 0.01);
      return Math.hypot(b[0] - a[0], b[1] - a[1]) / 0.02;
    };
    let last = -9;
    for (let t = 0.1; t < play.duration - 0.3; t += 0.02) {
      if (t - last > 0.6 && sp(t) > 3.4 && sp(t + 0.3) < 1.3) {
        ev.push({pt: t + 0.2, name: 'squeak', key: `squeak-${id}`});
        last = t;
      }
    }
  }
  eventCache.set(play.id, ev);
  return ev;
};

const autoCues = (ep: Episode3, laid: {shot: Shot3; start: number; end: number}[], T: (a: Anchor, off?: number) => number, fps: number): Cue[] => {
  if (!ep.autoSfx) return [];
  const cfg = typeof ep.autoSfx === 'object' ? ep.autoSfx : {};
  const vol: Record<string, [string, number]> = {bounce: ['bounce', cfg.bounce ?? 0], catch: ['bounce', cfg.catch ?? 0], squeak: ['squeak', cfg.squeak ?? 0.1], swish: ['swish', cfg.swish ?? 0.3], land: ['bounce', cfg.land ?? 0], rim: ['rim', cfg.rim ?? cfg.swish ?? 0.3]};
  const out: Cue[] = [];
  for (const l of laid) {
    const g = l.shot.autoGain ?? 1;
    if (g <= 0) continue;
    const play = ep.plays[l.shot.play];
    const evs = playEvents(play, cfg.players ?? ['O1', 'O5', 'X1', 'X5']);
    const rm = resolveRemap(l.shot.remap, play, localResolver(T, l.start, l.end));
    const n = Math.round((l.end - l.start) * fps);
    for (let f = 0; f < n; f++) {
      const p0 = remapAt(rm, f / fps);
      const p1 = remapAt(rm, (f + 1) / fps);
      if (p1 - p0 < 0.3 / fps) continue;
      for (const e of evs) if (e.pt > p0 && e.pt <= p1) out.push({t: l.start + (f + (e.pt - p0) / (p1 - p0)) / fps, name: vol[e.name][0], volume: vol[e.name][1] * g});
    }
  }
  return out;
};

export const tactical3dDuration = (ep: Episode3) => ep.words[ep.words.length - 1].end + ep.tail;

const layout = (ep: Episode3) => {
  const T = makeTacticalResolver(ep.words);
  const starts = ep.shots.map((s, i) => (i === 0 ? 0 : T(s.at)));
  const total = tactical3dDuration(ep);
  return ep.shots.map((shot, i) => ({shot, start: starts[i], end: i + 1 < starts.length ? starts[i + 1] : total}));
};

const useLogo = () => {
  const [logo, setLogo] = React.useState<HTMLImageElement | undefined>();
  const [h] = React.useState(() => delayRender('logo + fonts'));
  React.useEffect(() => {
    const img = new Image();
    img.src = staticFile(LOGO);
    Promise.all([new Promise((r) => (img.onload = r)), document.fonts.load('150px Anton'), document.fonts.load('900 40px Inter')]).then(() => {
      setLogo(img);
      continueRender(h);
    });
  }, [h]);
  return logo;
};

/** Bounds QC probe: after each frame is laid out, report every on-screen text/graphic box (data-qc) in
 *  composition pixels. Used by scripts/qc-bounds.mts through renderFrames (imageFormat none). */
const BoundsProbe: React.FC<{frame: number}> = ({frame}) => {
  const ref = React.useRef<HTMLDivElement>(null);
  React.useLayoutEffect(() => {
    const root = ref.current?.parentElement;
    if (!root) return;
    const rr = root.getBoundingClientRect();
    const k = rr.width / 1080;
    const boxes: {kind: string; text: string; x0: number; y0: number; x1: number; y1: number; op: number}[] = [];
    root.querySelectorAll<HTMLElement>('[data-qc]').forEach((el) => {
      let op = 1;
      for (let e: HTMLElement | null = el; e && e !== root; e = e.parentElement) op *= parseFloat(getComputedStyle(e).opacity || '1');
      let r: DOMRect;
      if (el.dataset.qcText) {
        const range = document.createRange();
        range.selectNodeContents(el);
        r = range.getBoundingClientRect();
      } else r = el.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return;
      boxes.push({kind: el.dataset.qc ?? '?', text: (el.textContent ?? '').trim().slice(0, 40), op: Math.round(op * 100) / 100,
        x0: Math.round((r.left - rr.left) / k), y0: Math.round((r.top - rr.top) / k), x1: Math.round((r.right - rr.left) / k), y1: Math.round((r.bottom - rr.top) / k)});
    });
    console.log('QCBOX ' + JSON.stringify({frame, boxes}));
  });
  return <div ref={ref} style={{display: 'none'}} />;
};

export const Tactical3D: React.FC<{episode: Episode3; qcProbe?: boolean}> = ({episode: ep, qcProbe}) => {
  const frame = useCurrentFrame();
  const {fps, width: W, height: H} = useVideoConfig();
  const logo = useLogo();
  const t = frame / fps;
  const laid = React.useMemo(() => layout(ep), [ep]);
  const T = React.useMemo(() => makeTacticalResolver(ep.words), [ep]);
  const cues = React.useMemo(() => autoCues(ep, laid, T, fps), [ep, laid, T, fps]);
  if (!logo) return null;
  const cur = laid.find((l) => t >= l.start && t < l.end) ?? laid[laid.length - 1];
  const {shot, start, end} = cur;
  const lt = t - start;
  const toLocal = localResolver(T, start, end);
  const play = ep.plays[shot.play];
  const rm = resolveRemap(shot.remap, play, toLocal);
  const pt = remapAt(rm, lt);
  const cam = camera3At(play, shot.camera.map((k) => ({...k, at: toLocal(k.at)})), lt, pt);
  const live = <X extends Timed>(items: X[] = []) =>
    items
      .map((o) => {
        const from = toLocal(o.from);
        const to = o.to !== undefined ? toLocal(o.to) : end - start;
        return {...o, age: lt - from, dur: to - from};
      })
      .filter((o) => o.age >= 0 && o.age < o.dur);
  const ov = live(shot.ov3).map((o) => {
    if (o.type === 'route' && o.fromPlay) return {...o, pts: routeOf(ep.plays[o.fromPlay], o.player, o.t0, o.t1, 1 / 30)};
    return o;
  }) as unknown as LiveOv3[];
  const scr = live(shot.screen);
  // split screen (2026-11-22): the second view runs on the same local clock
  const split = shot.split
    ? (() => {
        const sp = shot.split;
        const h1 = Math.round(H * (sp.ratio ?? 0.5));
        const play2 = ep.plays[sp.play];
        const rm2 = resolveRemap(sp.remap, play2, toLocal);
        const pt2 = remapAt(rm2, lt);
        const cam2 = camera3At(play2, sp.camera.map((k) => ({...k, at: toLocal(k.at)})), lt, pt2);
        const ov2 = live(sp.ov3) as unknown as LiveOv3[];
        return {h1, play: play2, pt: pt2, cam: cam2, cam1: cam, ov: ov2, hide: sp.hide, renderer: sp.athleteRenderer};
      })()
    : undefined;
  const panels = shot.panels
    ? shot.panels.map((pn, i) => {
        const n = shot.panels!.length;
        const y0 = Math.round((H * i) / n), y1 = Math.round((H * (i + 1)) / n);
        const playN = pn.play ? ep.plays[pn.play] : play;
        const rmN = pn.remap ? resolveRemap(pn.remap, playN, toLocal) : rm;
        const ptN = remapAt(rmN, lt);
        const camN = camera3At(playN, (pn.camera ?? shot.camera).map((k) => ({...k, at: toLocal(k.at)})), lt, ptN);
        return {pn, y0, h: y1 - y0, play: playN, pt: ptN, cam: camN};
      })
    : undefined;
  const proj = projector(cam, W, H);
  const freezeOn = scr.some((s) => s.type === 'freeze' || s.type === 'grade');
  const fx = sceneFx(scr as unknown as {type: string; age: number; dur: number; amount?: number; dir?: number}[]);
  const subHide = (ep.subtitleHide ?? []).map(([a, b]) => [T(a), T(b)] as [number, number]);

  return (
    <AbsoluteFill style={{background: '#050A15'}}>
      <AbsoluteFill style={{filter: [freezeOn ? 'saturate(0.72) brightness(0.94) contrast(1.04)' : '', fx.blur > 0.05 ? `blur(${fx.blur.toFixed(2)}px)` : ''].join(' ').trim() || undefined, transform: fx.scale !== 1 || fx.tx !== 0 ? `translateX(${fx.tx.toFixed(1)}px) scale(${fx.scale.toFixed(4)})` : undefined}}>
        {!qcProbe && panels && (
          <>
            {panels.map((P, i) => (
              <div key={i} style={{position: 'absolute', left: 0, top: P.y0, width: W, height: P.h, overflow: 'hidden'}}>
                <Scene3D play={P.play} pt={P.pt} cam={P.cam} W={W} H={P.h} hide={P.pn.hide ?? shot.hide} logo={logo} env={shot.env ?? ep.env} faces={ep.faces} players3d={shot.players3d ?? ep.players3d} instNs={`p${i}:`}
                  athleteRenderer={P.pn.athleteRenderer ?? shot.athleteRenderer ?? ep.athleteRenderer} athleteMotion={P.pn.athleteMotion} athleteMesh={P.pn.athleteMesh} neutral={P.pn.neutral} debug32={P.pn.debug32} />
              </div>
            ))}
            {panels.slice(1).map((P, i) => (
              <div key={`b${i}`} style={{position: 'absolute', left: 0, right: 0, top: P.y0 - 2, height: 4, background: '#FFC447', boxShadow: '0 0 12px rgba(0,0,0,0.6)'}} />
            ))}
          </>
        )}
        {!qcProbe && !split && !panels && (
          <Scene3D play={play} pt={pt} cam={cam} W={W} H={H} hide={shot.hide} logo={logo} env={shot.env ?? ep.env} faces={ep.faces} players3d={shot.players3d ?? ep.players3d} athleteRenderer={shot.athleteRenderer ?? ep.athleteRenderer}
            athleteMotion={shot.athleteMotion} athleteMesh={shot.athleteMesh} neutral={shot.neutral} debug32={shot.debug32}>
            <Overlays3D play={play} pt={pt} items={ov} />
          </Scene3D>
        )}
        {!qcProbe && split && !panels && (
          <>
            <div style={{position: 'absolute', left: 0, top: 0, width: W, height: split.h1, overflow: 'hidden'}}>
              <Scene3D play={play} pt={pt} cam={split.cam1} W={W} H={split.h1} hide={shot.hide} logo={logo} env={shot.env ?? ep.env} faces={ep.faces} players3d={shot.players3d ?? ep.players3d} athleteRenderer={shot.athleteRenderer ?? ep.athleteRenderer}>
                <Overlays3D play={play} pt={pt} items={ov} />
              </Scene3D>
            </div>
            <div style={{position: 'absolute', left: 0, top: split.h1, width: W, height: H - split.h1, overflow: 'hidden'}}>
              <Scene3D play={split.play} pt={split.pt} cam={split.cam} W={W} H={H - split.h1} hide={split.hide} logo={logo} env={shot.env ?? ep.env} faces={ep.faces} players3d={shot.players3d ?? ep.players3d} instNs="split:" athleteRenderer={split.renderer ?? shot.athleteRenderer ?? ep.athleteRenderer}>
                <Overlays3D play={split.play} pt={split.pt} items={split.ov} />
              </Scene3D>
            </div>
            <div style={{position: 'absolute', left: 0, right: 0, top: split.h1 - 3, height: 6, background: 'linear-gradient(90deg, rgba(229,72,58,0.95), #FFC447 50%, rgba(110,168,255,0.95))', boxShadow: '0 0 18px rgba(0,0,0,0.6)'}} />
          </>
        )}
      </AbsoluteFill>
      {/* cinematic grade: vignette + top/bottom falloff that also protects text */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(3,8,20,0.55) 100%)'}} />
      <AbsoluteFill style={{background: `linear-gradient(180deg, rgba(5,10,21,0.55) 0%, rgba(5,10,21,0) 22%, rgba(5,10,21,0) 62%, rgba(5,10,21,${ep.gradeBottom ?? 0.6}) 100%)`}} />
      {scr.map((s, i) => {
        switch (s.type) {
          case 'title':
            return <KineticTitle key={i} lines={s.lines} age={s.age} dur={s.dur} y={s.y} size={s.size} gold={s.gold} sub={s.sub} />;
          case 'stamp':
            return <Stamp key={i} text={s.text} age={s.instant ? s.age + 0.3 : s.age} dur={s.instant ? s.dur + 0.3 : s.dur} y={s.y} tone={s.tone} badge={s.badge} />;
          case 'pin': {
            // V2: anchored to the posed head (or below the feet when the head spot covers another player)
            if (ep.pinV2) {
              const lt0 = lt - s.age;
              const samples = [0, 0.2, 0.4, 0.6, 0.8, 1].map((u) => {
                const l = lt0 + u * s.dur * 0.999;
                const p2 = remapAt(rm, l);
                return {pt: p2, proj: projector(camera3At(play, shot.camera.map((k) => ({...k, at: toLocal(k.at)})), l, p2), W, H)};
              });
              const pick = choosePin(play, s.player, samples, s.text, s.size ?? 40, s.dy, s.z);
              const q = placePin(play, s.player, pt, proj, s.text, s.size ?? 40, s.dy, s.z, pick);
              return <PinLabel key={i} x={q.x} y={q.y} text={s.text} age={s.age} dur={s.dur} tone={s.tone} dy={q.dy} dx={q.dx} size={s.size} />;
            }
            const p = posAt(play.tracks[s.player], Math.max(0, Math.min(play.duration, pt))) as V2;
            const q = proj([p[0], p[1], s.z ?? 2.25]);
            return q.visible ? <PinLabel key={i} x={q.x} y={q.y} text={s.text} age={s.age} dur={s.dur} tone={s.tone} dy={s.dy} size={s.size} /> : null;
          }
          case 'freeze':
            return <FreezeFrame key={i} age={s.age} dur={s.dur} label={s.label} />;
          case 'rewind':
            return <RewindTag key={i} age={s.age} dur={s.dur} />;
          case 'scrim':
            // navy veil that lifts a closing question off the court
            return <AbsoluteFill key={i} style={{background: '#050A15', opacity: (s.opacity ?? 0.5) * Math.min(1, s.age / 0.3)}} />;
          case 'step':
            return <StepBadge key={i} n={s.n} text={s.text} age={s.age} dur={s.dur} y={s.y} />;
          case 'counter':
            return <OfferCounter key={i} steps={s.steps.map((a) => toLocal(a) - (lt - s.age))} total={s.total ?? 3} base={s.base} age={s.age} dur={s.dur} y={s.y} />;
          case 'logo':
            return <Logo key={i} age={s.age} big={s.big} y={s.y} width={s.width} />;
          case 'focus': {
            const p = posAt(play.tracks[s.player], Math.max(0, Math.min(play.duration, pt))) as V2;
            const q = proj([p[0], p[1], s.z ?? 1.1]);
            return q.visible ? <FocusVignette key={i} x={q.x} y={q.y} age={s.age} dur={s.dur} r={s.r} strength={s.strength} /> : null;
          }
          case 'hud':
            return <TacticalHUD key={i} tag={s.tag} text={s.text} age={s.age} dur={s.dur} y={s.y} />;
          case 'debugPhase': {
            const ph = ballPhase(play, pt);
            return (
              <div key={i} style={{position: 'absolute', left: 40, top: 60, padding: '14px 22px', background: 'rgba(0,0,0,0.72)', color: '#fff', font: '600 38px Inter, sans-serif', lineHeight: 1.35, borderRadius: 10}}>
                <div style={{color: '#FFD34D'}}>DEBUG {s.label ?? ''}</div>
                <div>{ph.phase}{ph.owner ? ` · ${ph.owner}` : ''}</div>
                <div>play t = {pt.toFixed(3)} s</div>
              </div>
            );
          }
          case 'micro': {
            const o = Math.min(1, s.age / 0.2, (s.dur - s.age) / 0.25);
            return (
              <div key={i} style={{position: 'absolute', left: 0, right: 0, top: s.y ?? 330, display: 'flex', justifyContent: 'center', opacity: Math.max(0, o)}}>
                <div data-qc="stamp" style={{padding: '8px 18px', borderRadius: 8, background: 'rgba(5,10,21,0.62)', border: '1.5px solid rgba(243,180,107,0.7)', color: '#FFE6B8', font: '700 30px Inter, sans-serif', letterSpacing: 3}}>{s.text}</div>
              </div>
            );
          }
          case 'chip': {
            const o = Math.max(0, Math.min(1, s.age / 0.18, (s.dur - s.age) / 0.22));
            const col = s.tone === 'red' ? '#E5483A' : s.tone === 'blue' ? '#6EA8FF' : '#FFC447';
            const k = 0.92 + 0.08 * Math.min(1, s.age / 0.18);
            const al = s.align ?? 'left';
            return (
              <div key={i} style={{position: 'absolute', left: 110, right: 110, top: s.y ?? 420, display: 'flex', justifyContent: al === 'left' ? 'flex-start' : al === 'right' ? 'flex-end' : 'center', opacity: o}}>
                <div data-qc="stamp" style={{transform: `scale(${k.toFixed(3)})`, transformOrigin: al === 'left' ? 'left center' : al === 'right' ? 'right center' : 'center', padding: '10px 22px 8px', borderRadius: 10, background: 'rgba(5,10,21,0.78)', borderLeft: `8px solid ${col}`, color: '#FFFFFF', font: `400 ${s.size ?? 58}px Anton, Impact, sans-serif`, letterSpacing: 2, lineHeight: 1.05, boxShadow: '0 6px 22px rgba(0,0,0,0.45)'}}>
                  {s.text.split('→').map((part, j, arr) => (
                    <React.Fragment key={j}>
                      <span style={{color: j === 0 ? '#FFFFFF' : col}}>{part.trim()}</span>
                      {j < arr.length - 1 && <span style={{color: col, padding: '0 12px'}}>→</span>}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            );
          }
          case 'tint': {
            const o = Math.max(0, Math.min(1, s.age / 0.3, (s.dur - s.age) / 0.3)) * (s.strength ?? 0.5);
            return <AbsoluteFill key={i} style={{boxShadow: `inset 0 0 160px 40px ${s.color ?? 'rgba(229,72,58,0.9)'}`, opacity: o}} />;
          }
          case 'flash':
            return <Flash key={i} age={s.age} color={s.color} strength={s.strength ?? 0.35} />;
          case 'stepCount': {
            const cs = countedSteps(play, s.player).slice(0, s.labels.length);
            const g = (play as unknown as {choreo: Record<string, {ev: {gather: number}}>}).choreo[s.player].ev.gather;
            return <StepCounter key={i} pt={pt} gather={g} lands={cs.map((x) => x.land)} labels={s.labels} age={s.age} dur={s.dur} y={s.y} gatherLabel={s.gatherLabel} />;
          }
          default:
            return null;
        }
      })}
      <PremiumSubtitles words={ep.words} t={t} keys={ep.keywords ?? []} hideRanges={subHide} sizes={ep.subtitleGroups} block={ep.subtitleBlock} y={(ep.subtitleYAt ?? []).map(([a, b, yy]) => [T(a), T(b), yy] as [number, number, number]).find(([a, b]) => t >= a && t < b)?.[2] ?? ep.subtitleY ?? 1290} />
      {qcProbe && <BoundsProbe frame={frame} />}
      {!qcProbe && <Audio src={staticFile(ep.voiceMix ?? ep.voice)} />}
      {!qcProbe && ep.music?.src && <Audio src={staticFile(ep.music.src)} volume={ep.music.volume ?? 1} />}
      {!qcProbe && ep.ambience && <Audio src={staticFile(ep.ambience.src)} volume={ep.ambience.volume ?? 0.1} loop />}
      {!qcProbe && cues.map((c, i) => (
        <Sequence key={`cue-${i}`} from={Math.max(0, Math.round(c.t * fps))} durationInFrames={Math.round(1.2 * fps)}>
          <Audio src={staticFile(`sfx/${c.name}.mp3`)} volume={c.volume} />
        </Sequence>
      ))}
      {!qcProbe && laid.flatMap((l) =>
        (l.shot.sfx ?? []).map((s, i) => {
          const at = l.start + localResolver(T, l.start, l.end)(s.at);
          return (
            <Sequence key={`${l.shot.id}-${i}`} from={Math.max(0, Math.round(at * fps))} durationInFrames={Math.round(2.5 * fps)}>
              <Audio src={staticFile(`sfx/${s.name}.mp3`)} volume={s.volume ?? 0.3} />
            </Sequence>
          );
        }),
      )}
    </AbsoluteFill>
  );
};
