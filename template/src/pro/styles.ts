// Story-type presets. The episode picks a style; the preset decides the default
// rhythm (transitions, camera moves, texture, sound) so two videos never cut the same way.
import type {CameraMove, SfxName, StoryType, Transition} from './types';

export type StylePreset = {
  transitions: Transition[]; // cycled scene by scene unless a scene sets its own
  cameras: CameraMove[]; // cycled for scenes without a camera
  grain: number; // 0..1 film grain strength
  vignette: number; // 0..1
  leak: boolean; // warm light leak drifting across
  ambience: number; // arena bed volume (0 = off)
  transitionSfx: Partial<Record<Transition, SfxName>>;
  captionSize: number;
  musicVolume: number; // under narration; doubled when nobody is speaking
};

const base: StylePreset = {
  transitions: ['whip', 'punch', 'zoom-through', 'whip', 'flash'],
  cameras: ['push-in', 'pan-right', 'pull-out', 'pan-left', 'tilt-up'],
  grain: 0.35,
  vignette: 0.55,
  leak: true,
  ambience: 0,
  transitionSfx: {whip: 'whip', punch: 'impact', 'zoom-through': 'whoosh', flash: 'shutter', 'slide-up': 'whoosh'},
  captionSize: 84,
  musicVolume: 0.1,
};

export const STYLES: Record<StoryType, StylePreset> = {
  // Big numbers, archive texture, hits on every reveal.
  record: {...base, transitions: ['punch', 'whip', 'flash', 'punch', 'zoom-through'], grain: 0.45, ambience: 0.05},
  // Photo-led, slower camera, timeline graphics, fewer hits.
  player: {...base, transitions: ['zoom-through', 'whip', 'slide-up'], cameras: ['push-in', 'pan-left', 'drift', 'pan-right'], grain: 0.3},
  // The court is the hero: clean picture, quiet transitions, smaller subtitles.
  tactical: {...base, transitions: ['slide-up', 'cut', 'whip'], cameras: ['static', 'drift'], grain: 0.12, vignette: 0.35, leak: false, captionSize: 72, musicVolume: 0.08},
  // Split screens and stat rows, symmetrical rhythm.
  comparison: {...base, transitions: ['whip', 'punch', 'whip'], cameras: ['push-in', 'static', 'pull-out'], grain: 0.25},
  // Fast montage, more cuts, a final reveal.
  curiosity: {...base, transitions: ['whip', 'flash', 'punch', 'zoom-through', 'whip'], grain: 0.35},
};
