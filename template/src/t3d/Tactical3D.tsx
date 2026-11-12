// E2A 3D tactical composition ("Tactical3D"): plays + edit + narration timings -> vertical video.
// The edit is data (tactical/episodes/<id>.json): shots anchored to words of the real narration,
// play-time remaps (real speed, slow motion, freeze, rewind), 3D camera keys, world-space graphics
// (inside the 3D scene) and screen-space graphics (titles, stamps, labels, subtitles).
import React from 'react';
import {AbsoluteFill, Audio, Sequence, continueRender, delayRender, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import type {V2} from '../tactical/geometry.ts';
import type {Anchor, RemapKey} from '../tactical/edit.ts';
import {localResolver, makeTacticalResolver, remapAt, resolveRemap} from '../tactical/edit.ts';
import {posAt, routeOf} from '../tactical/play.ts';
import type {CamKey3} from './camera3d.ts';
import {camera3At} from './camera3d.ts';
import type {LiveOv3, Ov3} from './overlays3d';
import {Overlays3D, projector} from './overlays3d';
import type {PlayWithActions} from './rig.ts';
import {Scene3D} from './Scene';
import {FreezeFrame, KineticTitle, Logo, PinLabel, PremiumSubtitles, RewindTag, Stamp} from './screen3d';
import '../theme';

type Word = {text: string; start: number; end: number};
type Timed = {from: Anchor; to?: Anchor};
type ScreenItem = Timed & ({type: 'title'; lines: string[]; y?: number; size?: number; gold?: number[]; sub?: string} | {type: 'stamp'; text: string; y?: number; tone?: 'gold' | 'white'; badge?: string} | {type: 'pin'; player: string; text: string; tone?: 'gold' | 'red' | 'white'; dy?: number; z?: number} | {type: 'freeze'; label?: string} | {type: 'rewind'} | {type: 'logo'; big?: boolean} | {type: 'grade'});
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

export const Tactical3D: React.FC<{episode: Episode3}> = ({episode: ep}) => {
  const frame = useCurrentFrame();
  const {fps, width: W, height: H} = useVideoConfig();
  const logo = useLogo();
  const t = frame / fps;
  const laid = React.useMemo(() => layout(ep), [ep]);
  const T = React.useMemo(() => makeTacticalResolver(ep.words), [ep]);
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
        <Scene3D play={play} pt={pt} cam={cam} W={W} H={H} hide={shot.hide} logo={logo}>
          <Overlays3D play={play} pt={pt} items={ov} />
        </Scene3D>
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
            const p = posAt(play.tracks[s.player], Math.max(0, Math.min(play.duration, pt))) as V2;
            const q = proj([p[0], p[1], s.z ?? 2.25]);
            return q.visible ? <PinLabel key={i} x={q.x} y={q.y} text={s.text} age={s.age} dur={s.dur} tone={s.tone} dy={s.dy} /> : null;
          }
          case 'freeze':
            return <FreezeFrame key={i} age={s.age} dur={s.dur} label={s.label} />;
          case 'rewind':
            return <RewindTag key={i} age={s.age} dur={s.dur} />;
          case 'logo':
            return <Logo key={i} age={s.age} big={s.big} />;
          default:
            return null;
        }
      })}
      <PremiumSubtitles words={ep.words} t={t} keys={ep.keywords ?? []} hideRanges={subHide} />
      <Audio src={staticFile(ep.voiceMix ?? ep.voice)} />
      {ep.music?.src && <Audio src={staticFile(ep.music.src)} volume={ep.music.volume ?? 1} />}
      {laid.flatMap((l) =>
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
