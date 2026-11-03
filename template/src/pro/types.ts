// E2A Pro editing system: an episode is plain JSON (no per-video TSX), so the daily
// automation only writes data. Timing is anchored to the narration: `at` is either a
// phrase that appears in `words` (resolved to its start time) or a number of seconds.
import type {CourtSpec} from '../Daily';

export type Word = {text: string; start: number; end: number};
export type Anchor = string | number;

export type StoryType = 'record' | 'player' | 'tactical' | 'comparison' | 'curiosity';

export type CameraMove =
  | 'push-in'
  | 'pull-out'
  | 'pan-left'
  | 'pan-right'
  | 'tilt-up'
  | 'tilt-down'
  | 'drift'
  | 'static';

export type Transition = 'cut' | 'whip' | 'punch' | 'flash' | 'zoom-through' | 'slide-up';

export type SfxName =
  | 'whoosh'
  | 'whip'
  | 'impact'
  | 'riser'
  | 'tick'
  | 'bounce'
  | 'shutter'
  | 'buzzer';

export type SfxCue = {at: Anchor; name: SfxName; volume?: number; offset?: number};

/** Every image or clip must say where it came from and under which licence. */
export type Media = {
  src: string; // path inside public/, e.g. "media/2026-11-04/naismith.jpg"
  kind: 'photo' | 'video' | 'archive' | 'recreation';
  credit: string; // shown on screen, e.g. "Photo: Library of Congress"
  license: string; // e.g. "Public domain", "CC BY-SA 4.0", "Licensed (Getty #123)"
  sourceUrl?: string;
  focus?: [number, number]; // 0..1 point the camera moves toward
  startFrom?: number; // seconds into a video clip
};

export type Backdrop = 'arena' | 'navy' | 'spotlight' | 'archive';

type Base = {
  at: Anchor;
  offset?: number; // seconds added to the resolved anchor
  transition?: Transition;
  camera?: CameraMove;
  backdrop?: Backdrop;
  kicker?: string; // small gold line above the main graphic
  beats?: Anchor[]; // quick scale punches synced to words
  sfx?: SfxCue[];
  callouts?: {at: Anchor; text: string; tone?: 'gold' | 'white' | 'red'}[]; // stamped over the scene
};

export type ScoreTeam = {name: string; score: [Anchor, number][]; accent?: boolean};

export type SceneSpec =
  | (Base & {type: 'media'; media: Media; title?: string; subtitle?: string})
  | (Base & {type: 'headline'; lines: string[]; accent?: number[]; size?: number})
  | (Base & {
      type: 'stat';
      value: number;
      from?: number;
      decimals?: number;
      prefix?: string;
      suffix?: string;
      label: string;
      countFor?: number; // seconds of count-up
      second?: {at: Anchor; value: string; label: string};
    })
  | (Base & {
      type: 'scoreboard';
      label?: string;
      home: ScoreTeam;
      away: ScoreTeam;
      timer?: {start: Anchor; end: Anchor; to: number; label: string};
    })
  | (Base & {
      type: 'timeline';
      title?: string;
      items: {at: Anchor; label: string; value?: string; tone?: 'gold' | 'white' | 'red'}[];
    })
  | (Base & {
      type: 'split';
      title?: string;
      left: {name: string; media?: Media; stats: [string, string][]};
      right: {name: string; media?: Media; stats: [string, string][]};
      winner?: 'left' | 'right';
    })
  | (Base & {type: 'court'; court: CourtSpec; label?: string});

export type Episode = {
  id: string;
  title: string;
  style: StoryType;
  fps?: 30 | 60;
  voice: string; // path in public/, e.g. "audio/v1.mp3"
  words: Word[];
  /** phrase -> on-screen text for subtitles, e.g. {"eight point nine": "8.9"} */
  display?: Record<string, string>;
  /** extra words to highlight in subtitles (numbers are highlighted automatically) */
  emphasis?: string[];
  scenes: SceneSpec[];
  outro?: {seconds?: number; line?: string};
  music?: {src?: string; volume?: number};
  ambience?: boolean;
  sources: string[]; // fact-check sources, required by the validator
};
