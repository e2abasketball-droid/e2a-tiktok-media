// E2A Tactical composition: turns a TacticalEpisode (plays + edit + narration timings) into the video.
import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {BODY, DISPLAY, GOLD, NAVY, NAVY_DEEP, WHITE} from '../pro/brand';
import {Flash, Grain, Vignette} from '../pro/fx';
import {Subtitles} from '../pro/subtitles';
import {cameraAt} from './camera.ts';
import type {Overlay, Shot, TacticalEpisode} from './edit.ts';
import {localResolver, makeTacticalResolver, remapAt, resolveRemap} from './edit.ts';
import {sample} from './play.ts';
import type {LiveOverlay} from './TacticalView';
import {TacticalView} from './TacticalView';
import {DecisionBranch, Fork, FreezeFrameOverlay, Kicker, LogoBug, ResultStamp, RewindFX, TacticalText, TimingBar} from './screen';

export const tacticalDuration = (ep: TacticalEpisode) => ep.words[ep.words.length - 1].end + ep.tail;

type Laid = {shot: Shot; start: number; end: number};

const layout = (ep: TacticalEpisode): Laid[] => {
  const T = makeTacticalResolver(ep.words);
  const starts = ep.shots.map((s, i) => (i === 0 ? 0 : T(s.at, s.offset ?? 0)));
  const total = tacticalDuration(ep);
  return ep.shots.map((shot, i) => ({shot, start: starts[i], end: i + 1 < starts.length ? starts[i + 1] : total}));
};

const SCREEN = new Set(['fork', 'title', 'stamp', 'freeze', 'rewind', 'timing', 'branch', 'logo', 'kicker', 'flash', 'dim']);

export const Tactical: React.FC<{episode: TacticalEpisode}> = ({episode: ep}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const laid = React.useMemo(() => layout(ep), [ep]);
  const T = React.useMemo(() => makeTacticalResolver(ep.words), [ep]);
  const idx = Math.max(0, laid.findIndex((l) => t >= l.start && t < l.end));
  const cur = laid[idx === -1 ? laid.length - 1 : idx] ?? laid[laid.length - 1];
  const {shot, start, end} = cur;
  const lt = t - start;
  const toLocal = localResolver(T, start, end);

  const live = (shot.overlays ?? [])
    .map((o: Overlay) => {
      const from = toLocal(o.from);
      const to = o.to !== undefined ? toLocal(o.to) : end - start;
      return {...o, age: lt - from, dur: to - from} as LiveOverlay;
    })
    .filter((o) => o.age >= 0 && o.age < o.dur);

  const views: React.ReactNode[] = [];
  if (shot.split) {
    shot.split.forEach((pn, i) => {
      const play = ep.plays[pn.play];
      const rm = resolveRemap(pn.remap, play, toLocal);
      const pt = remapAt(rm, lt);
      const cam = cameraAt(pn.camera.map((k) => ({...k, at: toLocal(k.at)})), lt, pt, (x) => sample(play, x));
      const ov = live.filter((o) => o.panel === i && !SCREEN.has(o.type));
      const dim = live.find((o) => o.type === 'dim' && o.panel === i);
      views.push(
        <div key={i} style={{position: 'absolute', left: i * 540, top: 300, width: 540, height: 1070, overflow: 'hidden', opacity: dim ? 1 - 0.55 * Math.min(1, dim.age / 0.3) : 1, transition: 'none'}}>
          <TacticalView play={play} pt={pt} cam={cam} W={540} H={1070} overlays={ov} id={`${shot.id}-${i}`} tagScale={0.8} />
          <div style={{position: 'absolute', top: 18, left: 0, right: 0, textAlign: 'center'}}>
            <span style={{fontFamily: DISPLAY, fontSize: 52, letterSpacing: 2, color: i === 0 ? GOLD : '#7BE0A8', textShadow: '0 4px 16px rgba(0,0,0,0.7)'}}>{pn.label}</span>
          </div>
          {pn.result && pt >= (play.marks.make ?? 99) - 0.01 && (
            <div style={{position: 'absolute', bottom: 26, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
              <span style={{fontFamily: BODY, fontWeight: 900, fontSize: 30, letterSpacing: 3, color: NAVY, background: i === 0 ? GOLD : '#7BE0A8', padding: '8px 18px', borderRadius: 10}}>{pn.result}</span>
            </div>
          )}
        </div>,
      );
    });
    views.push(<div key="div" style={{position: 'absolute', left: 537, top: 300, width: 6, height: 1070, background: GOLD}} />);
  } else if (shot.play) {
    const play = ep.plays[shot.play];
    const rm = resolveRemap(shot.remap ?? [[0, 0]], play, toLocal);
    const pt = remapAt(rm, lt);
    const cam = cameraAt((shot.camera ?? [{at: 0, cam: 'top'}]).map((k) => ({...k, at: toLocal(k.at)})), lt, pt, (x) => sample(play, x));
    const ov = live.filter((o) => !SCREEN.has(o.type));
    const hl = live.filter((o) => o.type === 'ring').map((o) => o.player as string);
    views.push(<TacticalView key="v" play={play} pt={pt} cam={cam} W={1080} H={1920} overlays={ov} id={shot.id} focus={shot.focus} highlightIds={hl} hideIds={shot.hideUntil === undefined || lt < shot.hideUntil ? shot.hide : []} />);
    // screen overlays that need the play clock
    live
      .filter((o) => o.type === 'timing')
      .forEach((o, i) => views.push(<TimingBar key={`tb${i}`} phases={(o.phases as {label: string; t: number | string}[]).map((p) => ({label: p.label, t: typeof p.t === 'string' ? play.marks[p.t] : p.t}))} pt={pt} age={o.age} y={(o.y as number) ?? 1250} />));
  }

  // enter transition of the shot
  let enter: React.CSSProperties = {};
  if (shot.enter === 'whip' && lt < 0.28) {
    const e = 1 - Math.pow(1 - lt / 0.28, 3);
    enter = {transform: `translateX(${(1 - e) * 60}%)`, filter: `blur(${(1 - e) * 22}px)`};
  }

  const screen = live.filter((o) => SCREEN.has(o.type) && o.type !== 'timing');
  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 40%, #13294F 0%, ${NAVY} 45%, ${NAVY_DEEP} 100%)`}}>
      <AbsoluteFill style={enter}>{views}</AbsoluteFill>
      <Vignette amount={0.45} />
      {screen.map((o, i) => {
        const g = (k: string) => o[k] as never;
        switch (o.type) {
          case 'title':
            return <TacticalText key={i} text={g('text')} age={o.age} dur={o.dur} y={g('y')} size={g('size')} accent={g('accent')} sub={g('sub')} />;
          case 'stamp':
            return <ResultStamp key={i} text={g('text')} age={o.age} dur={o.dur} tone={g('tone')} y={g('y')} badge={g('badge')} scale={g('scale')} />;
          case 'freeze':
            return <FreezeFrameOverlay key={i} age={o.age} dur={o.dur} label={g('label')} />;
          case 'rewind':
            return <RewindFX key={i} age={o.age} dur={o.dur} />;
          case 'branch':
            return <DecisionBranch key={i} age={o.age} root={g('root')} left={g('left')} right={g('right')} highlight={g('highlight')} y={g('y')} />;
          case 'fork':
            return <Fork key={i} age={o.age} dur={o.dur} left={g('left')} right={g('right')} y={g('y')} />;
          case 'logo':
            return <LogoBug key={i} age={o.age} big={g('big')} />;
          case 'kicker':
            return <Kicker key={i} text={g('text')} age={o.age} tone={g('tone')} />;
          case 'flash':
            return <Flash key={i} age={o.age} color={g('color') ?? '#FFFFFF'} strength={g('strength') ?? 0.7} />;
          default:
            return null;
        }
      })}
      {shot.enter === 'flash' && <Flash age={lt} strength={0.55} />}
      <Grain amount={0.1} />
      <Subtitles words={ep.words} display={ep.display} emphasis={ep.emphasis} size={62} />
      <Audio src={staticFile(ep.voice)} />
      {ep.music?.src && <Audio src={staticFile(ep.music.src)} volume={ep.music.volume ?? 1} />}
      {laid.flatMap((l) =>
        (l.shot.sfx ?? []).map((s, i) => {
          const at = l.start + localResolver(T, l.start, l.end)(s.at);
          return (
            <Sequence key={`${l.shot.id}-${i}`} from={Math.max(0, Math.round(at * fps))} durationInFrames={Math.round(3 * fps)}>
              <Audio src={staticFile(`sfx/${s.name}.mp3`)} volume={s.volume ?? 0.35} />
            </Sequence>
          );
        }),
      )}
      {false && <div style={{color: WHITE}} />}
    </AbsoluteFill>
  );
};
