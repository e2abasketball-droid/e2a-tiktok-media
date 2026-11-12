import React from 'react';
import {Composition} from 'remotion';
import {Shell, Word} from './Daily';
import {Main} from './Main';
import {PLANS, DUR} from './plans';
import {Pro, proDuration} from './pro/Pro';
import type {Episode} from './pro/types';
import pilot from '../episodes/pilot.json';
import {Probe} from './t3d/Probe';
import {Tactical3D, tactical3dDuration} from './t3d/Tactical3D';
import {staggerEpisode, staggerEpisodeV2} from './t3d/episode';
import {Tactical, tacticalDuration} from './tactical/Tactical';
import type {TacticalEpisode} from './tactical/edit';
import elevatorEdit from '../tactical/episodes/elevator-screen.json';
import elevatorWords from '../tactical/episodes/elevator-screen.words.json';
import playA from '../tactical/plays/elevator-a-chase.json';
import playB from '../tactical/plays/elevator-b-switch.json';

const elevator = {...elevatorEdit, words: elevatorWords, plays: {A: playA, B: playB}} as unknown as TacticalEpisode;

export const FPS = 30;

type DailyProps = {n: number; words: Word[]};

const Daily: React.FC<DailyProps> = ({n, words}) => {
  const plan = PLANS[n](words);
  return <Shell plan={plan} words={words} n={n} total={DUR(words)} />;
};

export const Root: React.FC = () => (
  <>
    {/* legacy v1 template (40-58 s videos): kept so older instructions still render */}
    <Composition id="Main" component={Main} durationInFrames={1660} fps={FPS} width={1080} height={1920} />
    <Composition
      id="Daily"
      component={Daily}
      durationInFrames={1500}
      fps={FPS}
      width={1080}
      height={1920}
      defaultProps={{n: 2, words: [] as Word[]}}
      calculateMetadata={({props}) => ({durationInFrames: props.words.length ? DUR(props.words) : 1500})}
    />
    {/* Pro editing system: render with --props=episodes/<id>.json wrapped as {"episode": ...} */}
    <Composition
      id="Pro"
      component={Pro}
      durationInFrames={750}
      fps={FPS}
      width={1080}
      height={1920}
      defaultProps={{episode: pilot as unknown as Episode}}
      calculateMetadata={({props}) => {
        const fps = props.episode.fps ?? FPS;
        return {fps, durationInFrames: proDuration(props.episode, fps)};
      }}
    />
    {/* Tactical engine (2.5D court, data-driven plays): render with --props={"episode": ...} from scripts/tactical-props.mjs */}
    <Composition
      id="Tactical"
      component={Tactical}
      durationInFrames={60 * 76}
      fps={60}
      width={1080}
      height={1920}
      defaultProps={{episode: elevator}}
      calculateMetadata={({props}) => {
        const fps = props.episode.fps ?? 60;
        return {fps, durationInFrames: Math.ceil(tacticalDuration(props.episode) * fps)};
      }}
    />
    {/* 3D tactical engine (real 3D: Three.js athletes, court, cameras) — Episode 02 Stagger Screen */}
    <Composition
      id="Tactical3D"
      component={Tactical3D}
      durationInFrames={30 * 34}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{episode: staggerEpisode}}
      calculateMetadata={({props}) => {
        const fps = props.episode.fps ?? 30;
        return {fps, durationInFrames: Math.ceil(tactical3dDuration(props.episode) * fps)};
      }}
    />
    <Composition
      id="Tactical3DV2"
      component={Tactical3D}
      durationInFrames={30 * 34}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{episode: staggerEpisodeV2}}
      calculateMetadata={({props}) => {
        const fps = props.episode.fps ?? 30;
        return {fps, durationInFrames: Math.ceil(tactical3dDuration(props.episode) * fps)};
      }}
    />
    <Composition id="Probe3D" component={Probe} durationInFrames={300} fps={60} width={1080} height={1920} defaultProps={{cam: 'broadcast'}} />
  </>
);
