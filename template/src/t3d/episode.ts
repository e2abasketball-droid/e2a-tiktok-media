// Stagger Screen episode bundle (edit + real narration timings + plays) for the Tactical3D composition.
import edit from '../../tactical/episodes/stagger-screen.json';
import editV2 from '../../tactical/episodes/stagger-screen-v2.json';
import words from '../../tactical/episodes/stagger-screen.words.json';
import playA from '../../tactical/plays/stagger-a-trail.json';
import playB from '../../tactical/plays/stagger-b-backdoor.json';
import playBLowLock from '../../tactical/plays/stagger-b-backdoor-lowlock.json';
import type {Episode3} from './Tactical3D';

export const staggerEpisode = {...edit, words, plays: {A: playA, B: playB}} as unknown as Episode3;

/** V2 (2026-11-12): new licensed music bed, softer SFX, localized visual polish. V1 stays untouched. */
/** prototype 2026-11-13: V2 uses the low top-lock pose (revert: plays B = playB) */
export const staggerEpisodeV2 = {...editV2, words, plays: {A: playA, B: playBLowLock}} as unknown as Episode3;
