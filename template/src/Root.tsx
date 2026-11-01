import React from 'react';
import {Composition} from 'remotion';
import {Shell, Word} from './Daily';
import {PLANS, DUR} from './plans';

export const FPS = 30;

type DailyProps = {n: number; words: Word[]};

const Daily: React.FC<DailyProps> = ({n, words}) => {
  const plan = PLANS[n](words);
  return <Shell plan={plan} words={words} n={n} total={DUR(words)} />;
};

export const Root: React.FC = () => (
  <>
    <Composition
      id="Daily"
      component={Daily}
      durationInFrames={1500}
      fps={FPS}
      width={1080}
      height={1920}
      defaultProps={{n: 2, words: [] as Word[]}}
      calculateMetadata={({props}) => ({durationInFrames: DUR(props.words)})}
    />
  </>
);
