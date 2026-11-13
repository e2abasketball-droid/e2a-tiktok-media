// E2A 3D tactical composition ("Tactical3D"): plays + edit + narration timings -> vertical video.
// The edit is data (tactical/episodes/<id>.json): shots anchored to words of the real narration,
// play-time remaps (real speed, slow motion, freeze, rewind), 3D camera keys, world-space graphics
// (inside the 3D scene) and screen-space graphics (titles, stamps, labels, subtitles).
import React from 'react';
import {AbsoluteFill, Audio, Sequence, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import type {V2} from '../tactical/geometry.ts';
import type {Anchor, RemapKey} from '../tactical/edit.ts';
import {localResolver, makeTacticalResolver, remapAt, resolveRemap} from '../tactical/edit.ts';
import {posAt, routeOf, sample} from '../tactical/play.ts';
import type {CamKey3} from './camera3d.ts';
import {camera3At} from './camera3d.ts';
import type {LiveOv3, Ov3} from './overlays3d';
import {Overlays3D, projector} from './overlays3d';
import type {PlayWithActions} from './rig.ts';
import {Scene3D} from './Scene';
import {choosePin, placePin} from './pinPlace';
import {FreezeFrame, KineticTitle, Logo, PinLabel, PremiumSubtitles, RewindTag, Stamp} from './screen3d';
import '../theme';

type Word = {text: string; start: number; end: number};
type Timed = {from: Anchor; to?: Anchor};
type ScreenItem = Timed & ({type: 'title'; lines: string[]; y?: number; size?: number; gold?: number[]; sub?: string} | {type: 'stamp'; text: string; y?: number; tone?: 'gold' | 'white'; badge?: string} | {type: 'pin'; player: string; text: string; tone?: 'gold' | 'red' | 'white'; dy?: number; z?: number; size?: number} | {type: 'freeze'; label?: string} | {type: 'rewind'} | {type: 'logo'; big?: boolean} | {type: 'grade'} | {type: 'scrim'; opacity?: number});
type CamKeyA = Omit<CamKey3, 'at'> & {at: Anchor};
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
  /** sound by event (2026-11-13): bounces, catches, braking squeaks and the net, placed on their visible
   *  contact through each shot's remap (silent in freezes, rewinds and slow motion below 0.3x) */
  autoSfx?: boolean | {bounce?: number; catch?: number; squeak?: number; swish?: number; land?: number; players?: string[]};
  /** V2 pins: anchored to the posed head, flipped below the feet when they would cover another player */
  pinV2?: boolean;
  /** arena room tone under everything (looped) */
  ambience?: {src: string; volume?: number};
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
  const vol: Record<string, [string, number]> = {bounce: ['bounce', cfg.bounce ?? 0.2], catch: ['bounce', cfg.catch ?? 0.13], squeak: ['squeak', cfg.squeak ?? 0.1], swish: ['swish', cfg.swish ?? 0.3], land: ['bounce', cfg.land ?? 0.08]};
  const out: Cue[] = [];
  for (const l of laid) {
    const play = ep.plays[l.shot.play];
    const evs = playEvents(play, cfg.players ?? ['O1', 'O5', 'X1', 'X5']);
    const rm = resolveRemap(l.shot.remap, play, localResolver(T, l.start, l.end));
    const n = Math.round((l.end - l.start) * fps);
    for (let f = 0; f < n; f++) {
      const p0 = remapAt(rm, f / fps);
      const p1 = remapAt(rm, (f + 1) / fps);
      if (p1 - p0 < 0.3 / fps) continue;
      for (const e of evs) if (e.pt > p0 && e.pt <= p1) out.push({t: l.start + (f + (e.pt - p0) / (p1 - p0)) / fps, name: vol[e.name][0], volume: vol[e.name][1]});
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
    img.src = staticFile('e2a_logo_white.png');
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
  const proj = projector(cam, W, H);
  const freezeOn = scr.some((s) => s.type === 'freeze' || s.type === 'grade');
  const subHide = (ep.subtitleHide ?? []).map(([a, b]) => [T(a), T(b)] as [number, number]);

  return (
    <AbsoluteFill style={{background: '#050A15'}}>
      <AbsoluteFill style={{filter: freezeOn ? 'saturate(0.72) brightness(0.94) contrast(1.04)' : undefined}}>
        {!qcProbe && (
          <Scene3D play={play} pt={pt} cam={cam} W={W} H={H} hide={shot.hide} logo={logo}>
            <Overlays3D play={play} pt={pt} items={ov} />
          </Scene3D>
        )}
      </AbsoluteFill>
      {/* cinematic grade: vignette + top/bottom falloff that also protects text */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 55%, rgba(3,8,20,0.55) 100%)'}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(5,10,21,0.55) 0%, rgba(5,10,21,0) 22%, rgba(5,10,21,0) 62%, rgba(5,10,21,0.6) 100%)'}} />
      {scr.map((s, i) => {
        switch (s.type) {
          case 'title':
            return <KineticTitle key={i} lines={s.lines} age={s.age} dur={s.dur} y={s.y} size={s.size} gold={s.gold} sub={s.sub} />;
          case 'stamp':
            return <Stamp key={i} text={s.text} age={s.age} dur={s.dur} y={s.y} tone={s.tone} badge={s.badge} />;
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
          case 'logo':
            return <Logo key={i} age={s.age} big={s.big} />;
          default:
            return null;
        }
      })}
      <PremiumSubtitles words={ep.words} t={t} keys={ep.keywords ?? []} hideRanges={subHide} />
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
