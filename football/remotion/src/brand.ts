// E2A Football — official palette (football/config/brand.json) and fonts.
// Fonts and the 2026 logo are staged into football/remotion/public/ by football/scripts/fb_stage.py
// from the shared engine (read-only); nothing is copied into Git.
import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

loadFont({family: 'Anton', url: staticFile('anton.woff2'), weight: '400'});
loadFont({family: 'Inter', url: staticFile('inter.woff2'), weight: '100 900'});

export const NAVY = '#0B1C3D';
export const GOLD = '#C9A24D';
export const GOLD_DEEP = '#A9842F';
export const WHITE = '#FFFFFF';
export const RED = '#E0484F'; // only for "danger" accents on the defending side
export const DISPLAY = 'Anton, Impact, sans-serif';
export const BODY = 'Inter, Arial, sans-serif';
export const LOGO = 'e2a_logo_2026_white.png';
