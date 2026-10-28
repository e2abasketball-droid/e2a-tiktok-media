import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Fonts are bundled locally (the headless browser has no direct internet access).
loadFont({family: 'Anton', url: staticFile('anton.woff2'), weight: '400'});
loadFont({family: 'Inter', url: staticFile('inter.woff2'), weight: '100 900'});

export const DISPLAY = 'Anton, Impact, sans-serif';
export const BODY = 'Inter, Arial, sans-serif';

export const NAVY = '#081428';
export const NAVY_2 = '#12294D';
export const GOLD = '#E2B33C';
export const GOLD_SOFT = 'rgba(226,179,60,0.18)';
export const WHITE = '#FFFFFF';
export const MUTED = 'rgba(255,255,255,0.65)';
export const RED = '#D7263D';
