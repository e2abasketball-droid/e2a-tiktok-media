import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

// Fonts are bundled locally: the render must not depend on external requests.
loadFont({family: 'Anton', url: staticFile('anton.woff2'), weight: '400'});
loadFont({family: 'Inter', url: staticFile('inter.woff2'), weight: '100 900'});

export const DISPLAY = 'Anton, Impact, sans-serif';
export const BODY = 'Inter, Arial, sans-serif';
// Instagram brand colours (SPEC section 5)
export const NAVY = '#0B1B36';
export const NAVY_2 = '#12294D';
export const GOLD = '#C9A44C';
export const WHITE = '#FFFFFF';
export const MUTED = 'rgba(255,255,255,0.65)';
export const FPS = 30;
export const W = 1080;
export const H = 1920;
// Safe areas (SPEC section 13)
export const SAFE = {top: 250, bottom: 450, right: 150};
