import React from 'react';
import {Composition} from 'remotion';
import {Shell, Word} from './Daily';
import {Main} from './Main';
import {PLANS, DUR} from './plans';
import {Pro, proDuration} from './pro/Pro';
import type {Episode} from './pro/types';
import pilot from '../episodes/pilot.json';

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
  </>
);
