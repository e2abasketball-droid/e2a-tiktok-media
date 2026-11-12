// Stagger Screen episode bundle (edit + real narration timings + plays) for the Tactical3D composition.
import edit from '../../tactical/episodes/stagger-screen.json';
import words from '../../tactical/episodes/stagger-screen.words.json';
import playA from '../../tactical/plays/stagger-a-trail.json';
import playB from '../../tactical/plays/stagger-b-backdoor.json';
import type {Episode3} from './Tactical3D';

export const staggerEpisode = {...edit, words, plays: {A: playA, B: playB}} as unknown as Episode3;
