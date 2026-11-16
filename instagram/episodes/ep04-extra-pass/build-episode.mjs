// Source of truth for Ep04 (The Extra Pass) choreography. Run: node build-episode.mjs → episode.json (timings from words.json).
import fs from 'node:fs';
const dir = new URL('.', import.meta.url);
const words = JSON.parse(fs.readFileSync(new URL('words.json', dir), 'utf8'));
const DUR = 89.9;
class Path {
  constructor(x, y) { this.pts = [{t: 0, x, y, dribble: false}]; this.x = x; this.y = y; }
  go(t0, t1, x, y, dribble = false) { this.pts.push({t: t0, x: this.x, y: this.y, dribble: false}, {t: t1, x, y, dribble}); this.x = x; this.y = y; return this; }
  done() { this.pts.push({t: DUR, x: this.x, y: this.y, dribble: false}); return this.pts; }
}
const START = {O1: [38, 27], O2: [45, 9], O3: [25, 33], O4: [13, 27], O5: [5, 9], X1: [36, 24.5], X2: [43, 12.5], X3: [26, 29.5], X4: [14.5, 23.5], X5: [7, 12.5]};
const P = Object.fromEntries(Object.entries(START).map(([k, v]) => [k, new Path(...v)]));
const reset = (t0, t1) => { for (const k in P) if (P[k].x !== START[k][0] || P[k].y !== START[k][1]) P[k].go(t0, t1, ...START[k]); };
const DR = [31, 21], HELP = [28.5, 24];
// KEY (16.8-27.6): X3 leaves the top player to help -> O3 open
P.X3.go(18.4, 20.4, ...HELP);
reset(26.6, 27.6);
// OPTION 1 (27.7-44.2): drive, helper steps in, kick to open top player, shot
P.O1.go(30.5, 33.9, ...DR, true);
P.X3.go(32.3, 34.3, ...HELP);
P.X1.go(30.6, 33.9, 33.5, 22.5);
reset(42.8, 44.0);
// OPTION 2 (44.3-64.9): helper recovers in time -> extra pass to O4 whose defender shifted in -> second closeout -> open shot
P.O1.go(45.0, 46.8, ...DR, true);
P.X3.go(45.2, 46.8, ...HELP).go(47.9, 49.2, 25.8, 31.5);
P.X1.go(45.0, 46.8, 33.5, 22.5);
P.X4.go(46.0, 48.2, 18.5, 23);
P.X4.go(55.4, 57.3, 14, 26.5);
reset(62.8, 64.0);
// VARIATION 1 (65.7-71): O3 gets the ball, X3 flies out, O3 attacks the closeout
P.X3.go(64.8, 65.8, ...HELP).go(67.3, 68.6, 25.6, 32.4);
P.O3.go(69.3, 70.9, 19, 24, true);
reset(71.0, 71.6);
// VARIATION 2 (71.7-77.4): nobody helps -> take the shot you already have
P.O1.go(72.6, 74.1, 33, 23, true);
reset(76.9, 77.5);
// SUMMARY (77.5-): good shot passed up -> great shot
P.X3.go(77.9, 78.8, ...HELP).go(78.9, 79.7, 25.8, 31.5);
P.X4.go(79.0, 80.4, 18.5, 23).go(81.0, 82.2, 14, 26.5);
reset(88.0, 89.0);
const players = Object.keys(P).map((id) => ({id, team: id[0].toLowerCase(), label: id[0] === 'O' ? id.slice(1) : '', path: P[id].done()}));
const B = [0, 'O1'];
const ball = [
  {t: 0, at: 'O1'}, {t: 37.2, at: 'O1'}, {t: 37.9, at: 'O3'}, {t: 39.4, at: 'O3'}, {t: 40.0, x: 25, y: 5.25}, {t: 43.0, x: 25, y: 5.25}, {t: 44.2, at: 'O1'},
  {t: 47.2, at: 'O1'}, {t: 47.9, at: 'O3'}, {t: 50.7, at: 'O3'}, {t: 51.4, at: 'O4'}, {t: 58.9, at: 'O4'}, {t: 59.5, x: 25, y: 5.25}, {t: 62.8, x: 25, y: 5.25}, {t: 64.2, at: 'O1'},
  {t: 65.6, at: 'O1'}, {t: 66.3, at: 'O3'}, {t: 70.9, at: 'O3'}, {t: 71.5, at: 'O1'},
  {t: 75.4, at: 'O1'}, {t: 76.0, x: 25, y: 5.25}, {t: 77.0, x: 25, y: 5.25}, {t: 77.7, at: 'O1'},
  {t: 77.9, at: 'O1'}, {t: 78.6, at: 'O3'}, {t: 79.9, at: 'O3'}, {t: 80.6, at: 'O4'}, {t: 82.0, at: 'O4'}, {t: 82.7, x: 25, y: 5.25}, {t: DUR, x: 25, y: 5.25},
];
const arrows = [
  {kind: 'pass', from: 'O1', to: 'O3', t0: 24.6, t1: 25.9, show: 1.8},
  {kind: 'dribble', from: [38, 27], to: DR, t0: 30.5, t1: 33.9, show: 1.0},
  {kind: 'cut', from: [26, 29.5], to: HELP, t0: 32.3, t1: 34.3, show: 3.0},
  {kind: 'pass', from: DR, to: [25, 33], t0: 37.2, t1: 37.9, show: 2.4},
  {kind: 'dribble', from: [38, 27], to: DR, t0: 45.0, t1: 46.8, show: 1.0},
  {kind: 'pass', from: DR, to: [25, 33], t0: 47.2, t1: 47.9, show: 1.6},
  {kind: 'cut', from: HELP, to: [25.8, 31.5], t0: 47.9, t1: 49.2, show: 2.0},
  {kind: 'pass', from: [25, 33], to: [13, 27], t0: 50.7, t1: 51.4, show: 4.0},
  {kind: 'cut', from: [18.5, 23], to: [14, 26.5], t0: 55.4, t1: 57.3, show: 2.5},
  {kind: 'pass', from: DR, to: [25, 33], t0: 65.6, t1: 66.3, show: 1.6},
  {kind: 'dribble', from: [25, 33], to: [19, 24], t0: 69.3, t1: 70.9, show: 1.5},
  {kind: 'dribble', from: [38, 27], to: [33, 23], t0: 72.6, t1: 74.1, show: 1.5},
  {kind: 'pass', from: [38, 27], to: [25, 33], t0: 77.9, t1: 78.6, show: 1.8},
  {kind: 'pass', from: [25, 33], to: [13, 27], t0: 79.9, t1: 80.6, show: 2.2},
];
const highlights = [
  {x: 33, y: 27, r: 6, t0: 3.2, t1: 6.5},
  {x: 38, y: 27, r: 3.4, t0: 12.4, t1: 15.6},
  {x: 25, y: 33, r: 3.8, t0: 21.2, t1: 24.6}, {x: 28.5, y: 24, r: 4, t0: 19.0, t1: 21.0},
  {x: 25, y: 33, r: 3.8, t0: 35.6, t1: 39.0}, {x: 28.5, y: 24, r: 4.2, t0: 33.3, t1: 36.0},
  {x: 25, y: 31.5, r: 4, t0: 48.0, t1: 50.4}, {x: 18.5, y: 23, r: 4.5, t0: 52.7, t1: 55.2},
  {x: 14, y: 27, r: 4, t0: 57.5, t1: 60.3},
  {x: 25, y: 32, r: 4, t0: 67.5, t1: 69.2}, {x: 19, y: 24, r: 4, t0: 70.0, t1: 71.0},
  {x: 33, y: 23, r: 4, t0: 74.2, t1: 76.4},
  {x: 25, y: 33, r: 3.6, t0: 80.0, t1: 81.2}, {x: 14, y: 27, r: 4.2, t0: 81.4, t1: 83.6},
];
const steps = [
  {t0: 0, t1: 7.8, tag: 'HOOK', label: 'Good shot, or a great one?', focus: {x: 28, y: 26, zoom: 1}},
  {t0: 7.8, t1: 16.7, tag: 'SET-UP', label: 'Five out, ball on the wing', focus: {x: 27, y: 25, zoom: 1.02}},
  {t0: 16.7, t1: 27.6, tag: 'THE KEY', label: 'Help leaves someone open', focus: {x: 30, y: 26, zoom: 1.06}},
  {t0: 27.6, t1: 44.2, tag: 'OPTION 1', label: 'Drive and kick, pass early', focus: {x: 29, y: 24, zoom: 1.06}},
  {t0: 44.2, t1: 65.6, tag: 'OPTION 2', label: 'Extra pass: force a 2nd closeout', focus: {x: 25, y: 26, zoom: 1.0}},
  {t0: 65.6, t1: 71.6, tag: 'WATCH FOR', label: 'Closeout too fast? Attack it', focus: {x: 28, y: 28, zoom: 1.06}},
  {t0: 71.6, t1: 77.5, tag: 'WATCH FOR', label: 'No help? Take your shot', focus: {x: 31, y: 25, zoom: 1.06}},
  {t0: 77.5, t1: DUR, tag: 'SUMMARY', label: 'Pass the good shot up', focus: {x: 25, y: 26, zoom: 1}},
];
const sfx = [
  ...[7.8, 16.7, 27.6, 44.2, 65.6, 71.6, 77.5].map((t) => ({t, file: 'pop', volume: 0.35})),
  ...[27.0, 43.6, 64.8, 71.0, 77.0].map((t) => ({t, file: 'whoosh', volume: 0.35})),
  ...[37.9, 47.9, 51.4, 66.3, 78.6, 80.6].map((t) => ({t, file: 'catch', volume: 0.5})),
  ...[40.0, 59.5, 76.0, 82.7].map((t) => ({t, file: 'swish', volume: 0.55})),
  {t: DUR - 3.0, file: 'sting', volume: 0.45},
];
const ep = {id: 'ep04-extra-pass', title: 'The Extra Pass', kicker: 'TEAM PRINCIPLE', concept: 'extra-pass', durationSec: DUR, voice: 'vo.mp3', words, players, ball, arrows, highlights, steps, sfx};
fs.writeFileSync(new URL('episode.json', dir), JSON.stringify(ep));
console.log('episode.json written', JSON.stringify(ep).length, 'bytes');
