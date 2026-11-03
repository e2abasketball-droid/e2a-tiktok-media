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
  | 'buzzer'
  | 'bass_hit'
  | 'impact_big'
  | 'swish'
  | 'squeak'
  | 'crowd_cheer'
  | 'reverse_cymbal';

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
  /** "cover" fills the frame (default). "print" shows the whole picture as a framed archive print
   *  over a blurred copy: use it for small or landscape archive photos that would blur or lose
   *  their subject if cropped to 9:16. */
  fit?: 'cover' | 'print';
  tilt?: number; // degrees of rotation for a print (default -2)
};

export type Backdrop = 'arena' | 'navy' | 'spotlight' | 'archive';

/** A real photo/clip behind a graphic. duotone = navy/gold brand grade (default), tint = natural
 *  colours darkened, blur = soft out-of-focus plate. */
export type PhotoBg = Media & {treatment?: 'duotone' | 'tint' | 'blur'};

/** Where the graphic sits over its backdrop. center (default); low = lower half, the photo shows
 *  above it; high = upper half; compact = smaller centred card with more photo around it;
 *  corner = small broadcast-style bug top-left (for scoreboards over a full photo). */
export type Layout = 'center' | 'low' | 'high' | 'compact' | 'corner';

type Base = {
  at: Anchor;
  offset?: number; // seconds added to the resolved anchor
  transition?: Transition;
  camera?: CameraMove;
  backdrop?: Backdrop;
  kicker?: string; // small gold line above the main graphic
  beats?: Anchor[]; // quick scale punches synced to words
  sfx?: SfxCue[];
  /** play the style's transition sound on this cut (off by default: cuts are clean) */
  sfxTransition?: boolean;
  callouts?: {at: Anchor; text: string; tone?: 'gold' | 'white' | 'red'}[]; // stamped over the scene
  /** Real photo/footage behind a graphic scene instead of a dark backdrop (needs credit + licence). */
  bg?: PhotoBg;
  layout?: Layout;
  /** subtitles position in this scene: low (default) or high, when a face or the action is low in the frame */
  captions?: 'low' | 'high';
  /** Framed photo card beside the graphic (picture-in-picture). at = when it slides in. */
  inset?: Media & {corner?: 'tl' | 'tr'; at?: Anchor; caption?: string};
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
  /**
   * Music. By default render-pro.sh builds a bed for this episode with music/e2a_music.py and sets
   * premixed=true (level, ducking and fades are baked in, so it plays at volume 1).
   * story: music story type (defaults from style); dropAt / payoffAt: anchors for the two drops
   * (default: the scene cuts nearest 30% and 75% of the narration); engine "file" keeps src as-is.
   * hits: seconds of the music drops, written by episode-music.mjs; the picture shakes and flashes on them.
   */
  music?: {src?: string; volume?: number; premixed?: boolean; engine?: 'e2a' | 'file'; story?: string; track?: string; dropAt?: Anchor; payoffAt?: Anchor; hits?: number[]};
  ambience?: boolean;
  /** Opening template for the first 2 s (rotate between videos):
   *  stat-slam = big figure slams in over a photo; photo-line = full-bleed photo with a slow push and the
   *  hook line; split = two images/figures wipe in side by side; clock = hard cut onto a running game clock. */
  hook?: 'stat-slam' | 'photo-line' | 'split' | 'clock';
  /** How the story ends (rotate; about 1 in 3 debate): debate = an open, arguable closing line;
   *  surprise = a twist; fact = a final striking figure; emotion = a memorable human line. */
  ending?: 'debate' | 'surprise' | 'fact' | 'emotion';
  /** Public texts in English: short caption, a comment to pin by hand, and a reply to keep the thread going. */
  social?: {caption: string; pinnedComment?: string; reply?: string; hashtags?: string[]};
  /** max automatic highlight effects (default 3); a scene's own sfx always play */
  sfxBudget?: number;
  sources: string[]; // fact-check sources, required by the validator
};
