// E2A Pro shell: turns an Episode (JSON) into a finished Reel.
import React from 'react';
import {AbsoluteFill, Audio, Img, Sequence, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {Court} from '../Daily';
import {BackdropView, Inset, MediaView, PhotoBackdrop} from './backdrops';
import {BODY, GOLD, NAVY_DEEP, RED, WHITE} from './brand';
import {Camera} from './camera';
import {Flash, Grain, LightLeak, Vignette} from './fx';
import {Callout, Credit, Headline, Kicker, SceneCtx, Scoreboard, Split, Stat, Timeline, useAt} from './graphics';
import {STYLES, StylePreset} from './styles';
import {Subtitles} from './subtitles';
import {Timed, layoutScenes, makeResolver, totalSeconds, voiceEnd} from './timing';
import type {CameraMove, Episode, Layout, SceneSpec, SfxCue, SfxName, Transition} from './types';
import MIX from '../../audio-mix.json';

const OVERLAP: Record<Transition, number> = {cut: 0, flash: 0, whip: 0.22, punch: 0.14, 'zoom-through': 0.3, 'slide-up': 0.28};

const transitionOf = (sc: Timed, style: StylePreset): Transition =>
  sc.index === 0 ? 'cut' : sc.spec.transition ?? style.transitions[(sc.index - 1) % style.transitions.length];
const cameraOf = (sc: Timed, style: StylePreset): CameraMove => sc.spec.camera ?? style.cameras[sc.index % style.cameras.length];

const ease = (x: number) => 1 - Math.pow(1 - Math.min(1, Math.max(0, x)), 3);

/** transform for a scene entering (p 0->1) or leaving (q 0->1) */
const enterStyle = (tr: Transition, p: number): React.CSSProperties => {
  const e = ease(p);
  switch (tr) {
    case 'whip':
      return {transform: `translateX(${(1 - e) * 110}%)`, filter: `blur(${(1 - e) * 26}px)`};
    case 'punch':
      return {transform: `scale(${1.4 - 0.4 * e})`, opacity: Math.min(1, p * 3)};
    case 'zoom-through':
      return {transform: `scale(${0.82 + 0.18 * e})`, opacity: e, filter: `blur(${(1 - e) * 14}px)`};
    case 'slide-up':
      return {transform: `translateY(${(1 - e) * 100}%)`};
    default:
      return {};
  }
};
const exitStyle = (tr: Transition, q: number): React.CSSProperties => {
  const e = ease(q);
  switch (tr) {
    case 'whip':
      return {transform: `translateX(${-e * 55}%)`, filter: `blur(${e * 26}px)`};
    case 'zoom-through':
      return {transform: `scale(${1 + 0.7 * e})`, opacity: 1 - e, filter: `blur(${e * 10}px)`};
    case 'slide-up':
      return {transform: `translateY(${-e * 35}%)`, filter: `brightness(${1 - 0.5 * e})`};
    default:
      return {};
  }
};

/** Where the graphic sits. Graphics are drawn for the centre; layouts move and scale the whole layer. */
const LAYOUT: Record<Layout, React.CSSProperties> = {
  center: {},
  low: {transform: 'translateY(250px) scale(0.78)', transformOrigin: '50% 30%'},
  high: {transform: 'translateY(-90px) scale(0.86)', transformOrigin: '50% 20%'},
  compact: {transform: 'scale(0.74)', transformOrigin: '50% 42%'},
  corner: {transform: 'translateY(-190px) scale(0.56)', transformOrigin: '70px 470px'},
};

const SceneBody: React.FC<{spec: SceneSpec; seed: string; startFrame: number}> = ({spec, seed, startFrame}) => {
  const at = useAt();
  const backdrop = spec.backdrop ?? (spec.type === 'court' ? 'navy' : 'arena');
  const credits = [spec.bg, spec.inset].filter(Boolean).map((m) => `${m!.kind === 'recreation' ? 'Recreation · ' : ''}${m!.credit}`);
  return (
    <AbsoluteFill>
      {spec.type === 'media' ? <MediaView media={spec.media} /> : spec.bg ? <PhotoBackdrop media={spec.bg} layout={spec.layout} /> : <BackdropView kind={backdrop} seed={seed} />}
      {spec.type !== 'media' && credits.length > 0 && <Credit text={credits.join(' · ')} />}
      {spec.inset && <Inset media={spec.inset} at={spec.inset.at !== undefined ? at(spec.inset.at) : 0.1} corner={spec.inset.corner} caption={spec.inset.caption} />}
      <AbsoluteFill style={LAYOUT[spec.layout ?? 'center']}>
      {spec.type === 'media' && (spec.title || spec.subtitle) && <Headline lines={[spec.title ?? '', spec.subtitle ?? ''].filter(Boolean)} accent={[1]} size={130} top={1000} />}
      {spec.type === 'media' && <Credit text={`${spec.media.kind === 'recreation' ? 'Recreation · ' : ''}${spec.media.credit}`} />}
      {spec.type === 'headline' && <Headline lines={spec.lines} accent={spec.accent} size={spec.size} />}
      {spec.type === 'stat' && (
        <Stat
          value={spec.value}
          from={spec.from}
          decimals={spec.decimals}
          prefix={spec.prefix}
          suffix={spec.suffix}
          label={spec.label}
          countFor={spec.countFor}
          second={spec.second ? {at: at(spec.second.at), value: spec.second.value, label: spec.second.label} : undefined}
        />
      )}
      {spec.type === 'scoreboard' && (
        <>
          <Scoreboard
            label={spec.label}
            home={spec.home}
            away={spec.away}
            timer={spec.timer ? {start: at(spec.timer.start), end: at(spec.timer.end), to: spec.timer.to, label: spec.timer.label} : undefined}
          />
        </>
      )}
      {spec.type === 'timeline' && <Timeline title={spec.title} items={spec.items.map((i) => ({...i, at: at(i.at)}))} />}
      {spec.type === 'split' && <Split title={spec.title} left={spec.left} right={spec.right} winner={spec.winner} />}
      {spec.type === 'court' && (
        // Court keyframes are in absolute seconds, so give it the absolute clock back.
        <Sequence from={-startFrame} layout="none">
          <AbsoluteFill style={{transform: 'translateY(40px)'}}>
            <Court spec={spec.court} />
          </AbsoluteFill>
        </Sequence>
      )}
      </AbsoluteFill>
      {(spec.callouts ?? []).map((c, i) => (
        <Callout key={i} at={at(c.at)} text={c.text} color={c.tone === 'red' ? RED : c.tone === 'white' ? WHITE : GOLD} top={spec.layout === 'low' ? 520 : spec.type === 'scoreboard' ? 1150 : 1120} />
      ))}
      {spec.kicker && <Kicker text={spec.kicker} top={spec.layout === 'corner' ? 700 : spec.type === 'scoreboard' ? 330 : 300} boxed={spec.type === 'media' || !!spec.bg} />}
    </AbsoluteFill>
  );
};

const Outro: React.FC<{line?: string}> = ({line = 'MORE THAN A GAME'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const s = spring({frame, fps, config: {damping: 13, mass: 0.6}});
  const l = spring({frame: frame - 6, fps, config: {damping: 18}});
  return (
    <AbsoluteFill style={{background: `rgba(6,15,34,${0.85 * Math.min(1, frame / 5)})`, justifyContent: 'center', alignItems: 'center', flexDirection: 'column', gap: 28}}>
      <Img src={staticFile('e2a_logo_white.png')} style={{width: 470, transform: `scale(${0.7 + 0.3 * s})`, opacity: s}} />
      <div style={{display: 'flex', alignItems: 'center', gap: 20, opacity: l}}>
        <div style={{width: 80 * l, height: 4, background: GOLD}} />
        <div style={{fontFamily: BODY, fontWeight: 800, fontSize: 34, letterSpacing: 9, color: GOLD}}>{line}</div>
        <div style={{width: 80 * l, height: 4, background: GOLD}} />
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- sound
const SFX_VOL: Record<SfxName, number> = {
  whoosh: 0.9, whip: 0.45, impact: 0.55, riser: 0.35, tick: 0.25, bounce: 0.6, shutter: 0.4, buzzer: 0.35,
  bass_hit: 0.5, impact_big: 0.45, swish: 0.5, squeak: 0.35, crowd_cheer: 0.3, reverse_cymbal: 0.3,
};

/** Moments where the picture hits: numbers landing, score changes, stamps, music drops and the hook. */
export type Hit = {t: number; power: number; shake?: boolean};
const buildHits = (ep: Episode, scenes: Timed[]): Hit[] => {
  const T = makeResolver(ep.words);
  const hits: Hit[] = [{t: 0, power: ep.hook === 'photo-line' || ep.hook === 'clock' ? 0.5 : 1.2, shake: ep.hook !== 'photo-line' && ep.hook !== 'clock'}];
  scenes.forEach((sc) => {
    const s = sc.spec;
    if (s.type === 'stat') {
      if (sc.index > 0) hits.push({t: sc.start + 0.05 + (s.countFor ?? 0.7), power: 1});
      if (s.second) hits.push({t: T(s.second.at), power: 0.8});
    }
    if (s.type === 'scoreboard') [s.home, s.away].forEach((team) => team.score.slice(1).forEach(([a]) => hits.push({t: T(a), power: 1})));
  });
  // the climax (music payoff, or the strongest late hit) is the only other moment that shakes
  const payoff = ep.music?.hits?.[1];
  if (payoff !== undefined && !hits.some((h) => Math.abs(h.t - payoff) < 0.2)) hits.push({t: payoff, power: 0.7});
  const late = hits.filter((h) => h.t > 0.5);
  const climax = payoff !== undefined ? late.reduce<Hit | undefined>((a, h) => (!a || Math.abs(h.t - payoff) < Math.abs(a.t - payoff) ? h : a), undefined) : late[late.length - 1];
  if (climax) climax.shake = true;
  return hits.sort((a, b) => a.t - b.t);
};

/** Screen shake + punch zoom from the hits: decaying, deterministic jitter. */
const shakeAt = (hits: Hit[], t: number) => {
  let x = 0;
  let y = 0;
  let z = 0;
  for (const h of hits) {
    const a = t - h.t;
    if (!h.shake || a < 0 || a > 0.4) continue;
    const d = Math.exp(-a * 11) * h.power;
    x += Math.sin(a * 95 + h.t * 7) * 22 * d;
    y += Math.cos(a * 81 + h.t * 3) * 16 * d;
    z += 0.035 * d;
  }
  return {x, y, z};
};

/**
 * Sound design v5: fewer, better effects. Cuts are clean by default (the music carries the edit).
 * Candidate moments are ranked; only `sfxBudget` of them (default 3) get a sound, at least 1.5 s
 * apart and never on top of a music drop. Effects that fall on a spoken word play 6 dB lower.
 * A scene's own `sfx` cues are always kept and count toward the budget.
 */
// levels from the central mix config (audio-mix.json -> sfx): effects are details, never above the voice
const SFX_GAIN = 10 ** (MIX.sfx.gainDb / 20);
const SFX_ON_SPEECH = 10 ** (MIX.sfx.onSpeechDb / 20);
const buildCues = (ep: Episode, scenes: Timed[], style: StylePreset): {t: number; name: SfxName; volume: number}[] => {
  const T = makeResolver(ep.words);
  const musicHits = [0, ...(ep.music?.hits ?? [])];
  type C = {t: number; name: SfxName; v: number; prio: number; forced?: boolean};
  const cand: C[] = [];
  scenes.forEach((sc) => {
    const s = sc.spec;
    if (s.type === 'stat' && sc.index > 0) cand.push({t: sc.start + 0.05 + (s.countFor ?? 0.7), name: 'impact', v: 0.9, prio: 3});
    if (s.type === 'stat' && s.second) cand.push({t: T(s.second.at), name: 'bass_hit', v: 0.8, prio: 2});
    if (s.type === 'scoreboard') [s.home, s.away].forEach((team) => team.score.slice(1).forEach(([a]) => cand.push({t: T(a), name: MIX.sfx.scoreSound as SfxName, v: 0.9, prio: 3})));
    (s.callouts ?? []).forEach((c) => cand.push({t: T(c.at), name: 'impact', v: 0.6, prio: 2}));
    (s.sfx ?? []).forEach((c: SfxCue) => cand.push({t: T(c.at, c.offset ?? 0), name: c.name, v: c.volume ?? 1, prio: 9, forced: true}));
    if (s.sfxTransition && sc.index > 0) {
      const snd = style.transitionSfx[transitionOf(sc, style)];
      if (snd) cand.push({t: sc.start, name: snd, v: 0.7, prio: 9, forced: true});
    }
  });
  const budget = ep.sfxBudget ?? MIX.sfx.budget;
  const picked: C[] = [];
  const free = (c: C) => picked.every((p) => Math.abs(p.t - c.t) >= 1.5) && (c.forced || musicHits.every((m) => Math.abs(m - c.t) >= 0.25));
  cand
    .sort((x, y) => y.prio - x.prio || x.t - y.t)
    .forEach((c) => {
      if ((c.forced || picked.length < budget) && (c.forced || free(c))) picked.push(c);
    });
  const speaking = (t: number) => ep.words.some((w) => t >= w.start - 0.05 && t <= w.end);
  return picked
    .filter((c) => c.t >= 0)
    .sort((x, y) => x.t - y.t)
    .map((c) => ({t: c.t, name: c.name, volume: SFX_VOL[c.name] * c.v * SFX_GAIN * (speaking(c.t) ? SFX_ON_SPEECH : 1)}));
};

/** Music ducks under the voice and comes up in the gaps. */
const useMusicCurve = (ep: Episode, fps: number, total: number, base: number) =>
  React.useMemo(() => {
    const n = Math.ceil(total * fps);
    const out = new Float32Array(n);
    let v = 0;
    for (let f = 0; f < n; f++) {
      const t = f / fps;
      const speaking = ep.words.some((w) => t >= w.start - 0.15 && t <= w.end + 0.3);
      const target = speaking ? base : base * 2.2;
      v += (target - v) * 0.12;
      const fadeIn = Math.min(1, f / 12);
      const fadeOut = Math.min(1, (n - f) / 18);
      out[f] = v * fadeIn * fadeOut;
    }
    return out;
  }, [ep.words, fps, total, base]);

// ---------------------------------------------------------------- main
export const Pro: React.FC<{episode: Episode}> = ({episode: ep}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const t = frame / fps;
  const style = STYLES[ep.style];
  const scenes = React.useMemo(() => layoutScenes(ep), [ep]);
  const resolve = React.useMemo(() => makeResolver(ep.words), [ep.words]);
  const total = totalSeconds(ep);
  const outroAt = voiceEnd(ep.words) + 0.25;
  const music = useMusicCurve(ep, fps, total, ep.music?.volume ?? style.musicVolume);
  const cues = React.useMemo(() => buildCues(ep, scenes, style), [ep, scenes, style]);
  const hits = React.useMemo(() => buildHits(ep, scenes), [ep, scenes]);
  const sh = shakeAt(hits, t);
  // Hook entrance (first frames), one of several openings so videos don't all start the same way.
  const hook = ep.hook ?? 'stat-slam';
  let hookS = 1;
  let hookBlur = 0;
  let hookX = 0;
  if (hook === 'stat-slam') {
    const p = Math.min(1, t / 0.32); // slams in from 1.3x with motion blur
    hookS = 1 + 0.3 * Math.pow(1 - p, 3);
    hookBlur = 14 * Math.pow(1 - p, 2);
  } else if (hook === 'photo-line') {
    const p = Math.min(1, t / 1.6); // slow cinematic push onto the photo
    hookS = 1.12 - 0.12 * (1 - Math.pow(1 - p, 2));
  } else if (hook === 'split') {
    const p = Math.min(1, t / 0.28); // whips in from the right
    hookX = 1080 * Math.pow(1 - p, 3);
    hookBlur = 20 * Math.pow(1 - p, 2);
  } // clock: hard cut, the running clock is the motion

  return (
    <AbsoluteFill style={{backgroundColor: NAVY_DEEP}}>
      <AbsoluteFill
        style={{
          isolation: 'isolate',
          overflow: 'hidden',
          transform: `translate(${sh.x + hookX}px, ${sh.y}px) scale(${hookS * (1 + sh.z)})`,
          filter: hookBlur > 0.3 ? `blur(${hookBlur}px)` : undefined,
        }}
      >
      {scenes.map((sc) => {
        const tr = transitionOf(sc, style);
        const next = scenes[sc.index + 1];
        const nextTr = next ? transitionOf(next, style) : 'cut';
        const tail = next ? OVERLAP[nextTr] : 0;
        if (t < sc.start || t >= sc.end + tail) return null;
        const startFrame = Math.round(sc.start * fps);
        const dur = Math.round((sc.end + tail - sc.start) * fps);
        const pIn = OVERLAP[tr] ? (t - sc.start) / OVERLAP[tr] : 1;
        const qOut = tail ? (t - sc.end) / tail : 0;
        const st: React.CSSProperties = t >= sc.end ? exitStyle(nextTr, qOut) : pIn < 1 ? enterStyle(tr, pIn) : {};
        const beats = (sc.spec.beats ?? []).map((b) => Math.round((resolve(b) - sc.start) * fps));
        return (
          <AbsoluteFill key={sc.index} style={{...st, zIndex: t >= sc.end ? 0 : 1}}>
            <Sequence from={startFrame} durationInFrames={dur} layout="none">
              <SceneCtx.Provider value={{resolve, start: sc.start, end: sc.end}}>
                <Camera move={cameraOf(sc, style)} durationInFrames={dur} beats={beats}>
                  <SceneBody spec={sc.spec} seed={`${ep.id}-${sc.index}`} startFrame={startFrame} />
                </Camera>
              </SceneCtx.Provider>
            </Sequence>
          </AbsoluteFill>
        );
      })}
      </AbsoluteFill>
      {scenes.slice(1).map((sc) => {
        const tr = transitionOf(sc, style);
        if (tr !== 'flash' && tr !== 'punch') return null;
        return <Flash key={sc.index} age={t - sc.start} color={tr === 'punch' ? '#FFE3A1' : '#FFFFFF'} strength={tr === 'punch' ? 0.45 : 0.85} />;
      })}
      {hits.map((h, i) => (
        <Flash key={`h${i}`} age={t - h.t} color={i === 0 ? '#FFFFFF' : '#FFE3A1'} strength={i === 0 ? 0.9 : (h.shake ? 0.3 : 0.14) * h.power} />
      ))}
      {style.leak && <LightLeak />}
      <Vignette amount={style.vignette} />
      <Grain amount={style.grain} />
      <Subtitles highRanges={scenes.filter((sc) => sc.spec.captions === 'high').map((sc) => [sc.start, sc.end] as [number, number])} words={ep.words} display={ep.display} emphasis={ep.emphasis} size={style.captionSize} hideAfter={outroAt} />
      <Sequence from={Math.round(outroAt * fps)}>
        <Outro line={ep.outro?.line} />
      </Sequence>

      <Audio src={staticFile(ep.voice)} />
      {ep.music?.premixed ? (
        <Audio src={staticFile(ep.music.src ?? 'music.mp3')} volume={1} />
      ) : (
        <Audio src={staticFile(ep.music?.src ?? 'music.mp3')} loop volume={(f) => music[Math.min(music.length - 1, f)] ?? 0} />
      )}
      {(ep.ambience ?? (!ep.music?.premixed && style.ambience > 0)) && <Audio src={staticFile('sfx/arena.mp3')} loop volume={style.ambience || 0.05} />}
      {cues.map((c, i) => (
        <Sequence key={i} from={Math.round(c.t * fps)} layout="none">
          <Audio src={staticFile(`sfx/${c.name}.mp3`)} volume={c.volume} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const proDuration = (ep: Episode, fps: number) => Math.ceil(totalSeconds(ep) * fps);
