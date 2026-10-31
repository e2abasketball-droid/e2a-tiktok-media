// Source of truth for the Ep03 (ICE) choreography. Run: node build-episode.mjs  → episode.json (timings from words.json).
import fs from 'node:fs';
const dir = new URL('.', import.meta.url);
const words = JSON.parse(fs.readFileSync(new URL('words.json', dir), 'utf8'));
const DUR = 88.8;
// Court feet: basket (25,5.25). x 0..50, y 0..47. Ball on the right wing; ball side = right.
class Path {
  constructor(x, y) { this.pts = [{t: 0, x, y, dribble: false}]; this.x = x; this.y = y; }
  go(t0, t1, x, y, dribble = false) { this.pts.push({t: t0, x: this.x, y: this.y, dribble: false}, {t: t1, x, y, dribble}); this.x = x; this.y = y; return this; }
  done() { this.pts.push({t: DUR, x: this.x, y: this.y, dribble: false}); return this.pts; }
}
const START = {O1: [38, 28], O5: [29, 34], O4: [12, 27], O2: [5, 9], O3: [45, 9], X1: [36.5, 25], X5: [29, 29], X4: [14, 23], X2: [7, 13], X3: [43, 13]};
const P = Object.fromEntries(Object.entries(START).map(([k, v]) => [k, new Path(...v)]));
const reset = (t0, t1) => { for (const k in P) P[k].go(t0, t1, ...START[k]); };
const SCR = [32, 30]; // screener's spot, angled toward the middle

// SET-UP (9.7-21.5): the big walks up to set the ball screen
P.O5.go(13.6, 16.8, ...SCR);
P.X5.go(14.0, 17.0, 30, 27);
// THE KEY (21.5-35.7): defender gets on the high side, pushes the dribbler baseline, big drops back
P.O1.go(29.0, 30.6, 38, 28, true).go(31.2, 34.2, 44, 19, true);
P.X1.go(27.4, 29.0, 35.5, 28.5).go(31.2, 34.4, 42, 22);
P.X5.go(29.0, 31.5, 36, 19);
reset(35.0, 36.2);
// OPTION 1 (35.7-47.8): on-ball defender gets above the ball and forces the sideline
P.O5.go(36.8, 37.6, ...SCR);
P.O1.go(38.5, 40.0, 38, 28, true).go(40.2, 42.6, 44.5, 20, true);
P.X1.go(38.4, 40.0, 35.5, 28.5).go(40.2, 42.8, 42.5, 22.5);
P.X5.go(39.0, 41.0, 37, 19);
reset(46.4, 47.6);
// OPTION 2 (47.8-62.4): screener's defender drops between ball and basket and calls it
P.O5.go(49.0, 50.2, ...SCR);
P.X5.go(50.6, 52.4, 34, 20);
P.O1.go(52.0, 53.4, 38, 28, true).go(56.8, 59.5, 43.5, 21, true);
P.X1.go(52.0, 53.4, 35.5, 28.5).go(56.8, 59.5, 41.5, 23.5);
reset(61.0, 62.2);
// WATCH 1: POP (62.4-68.4): screener pops to the three-point line, big recovers to the shooter
P.O5.go(63.0, 63.8, ...SCR).go(64.6, 66.0, 31, 33.5);
P.X5.go(63.0, 64.0, 34, 20).go(65.0, 66.4, 31.5, 30.5);
reset(67.6, 68.4);
// WATCH 2: REJECT (68.6-75.1): dribbler turns away from the screen, defender keeps the angle, big stays back
P.O5.go(69.0, 69.8, ...SCR);
P.O1.go(70.4, 71.8, 38, 28, true).go(72.0, 73.8, 45, 24, true);
P.X1.go(70.4, 71.8, 36, 28).go(72.0, 74.0, 43, 25.5);
P.X5.go(70.0, 71.6, 36, 21);
reset(75.0, 76.2);

const players = Object.keys(P).map((id) => ({id, team: id[0].toLowerCase(), label: id[0] === 'O' ? id.slice(1) : '', path: P[id].done()}));
const ball = [{t: 0, at: 'O1'}, {t: DUR, at: 'O1'}];
const arrows = [
  {kind: 'screen', from: 'O5', to: SCR, t0: 13.6, t1: 16.8, show: 5.0},
  {kind: 'dribble', from: [38, 28], to: [44, 19], t0: 31.2, t1: 34.2, show: 1.2},
  {kind: 'cut', from: [36.5, 25], to: [35.5, 28.5], t0: 27.4, t1: 29.0, show: 3.5},
  {kind: 'cut', from: [29, 29], to: [36, 19], t0: 29.0, t1: 31.5, show: 3.2},
  {kind: 'screen', from: 'O5', to: SCR, t0: 36.8, t1: 37.6, show: 3.0},
  {kind: 'dribble', from: [38, 28], to: [44.5, 20], t0: 40.2, t1: 42.6, show: 1.5},
  {kind: 'cut', from: [36.5, 25], to: [42.5, 22.5], t0: 40.2, t1: 42.8, show: 1.6},
  {kind: 'screen', from: 'O5', to: SCR, t0: 49.0, t1: 50.2, show: 2.5},
  {kind: 'cut', from: [30, 27], to: [34, 20], t0: 50.6, t1: 52.4, show: 5.0},
  {kind: 'dribble', from: [38, 28], to: [43.5, 21], t0: 56.8, t1: 59.5, show: 1.2},
  {kind: 'cut', from: SCR, to: [31, 33.5], t0: 64.6, t1: 66.0, show: 2.0},
  {kind: 'cut', from: [34, 20], to: [31.5, 30.5], t0: 65.0, t1: 66.4, show: 2.0},
  {kind: 'dribble', from: [38, 28], to: [45, 24], t0: 72.0, t1: 73.8, show: 1.3},
];
const highlights = [
  {x: 38, y: 28, r: 3.4, t0: 11.4, t1: 14.0}, {x: 32, y: 30, r: 3.4, t0: 16.0, t1: 19.0},
  {x: 30, y: 22, r: 6, t0: 23.5, t1: 27.2}, {x: 35.5, y: 28.5, r: 3.6, t0: 28.0, t1: 33.5},
  {x: 44, y: 19, r: 4, t0: 33.0, t1: 35.2},
  {x: 38, y: 27, r: 3.6, t0: 38.6, t1: 42.2}, {x: 44.5, y: 20, r: 4, t0: 42.6, t1: 46.0},
  {x: 34, y: 20, r: 4.2, t0: 51.8, t1: 56.0}, {x: 34, y: 21, r: 5.5, t0: 54.3, t1: 56.0},
  {x: 31, y: 33.5, r: 3.6, t0: 65.8, t1: 68.0}, {x: 43, y: 25.5, r: 3.8, t0: 73.0, t1: 75.0},
  {x: 30, y: 22, r: 7, t0: 77.6, t1: 81.0},
];
const steps = [
  {t0: 0, t1: 9.6, tag: 'HOOK', label: 'ICE: send them away from the middle', focus: {x: 33, y: 24, zoom: 1}},
  {t0: 9.6, t1: 21.4, tag: 'SET-UP', label: 'Wing ball screen, angled to the middle', focus: {x: 33, y: 25, zoom: 1.05}},
  {t0: 21.4, t1: 35.6, tag: 'THE KEY', label: 'High side: close the door', focus: {x: 35, y: 24, zoom: 1.08}},
  {t0: 35.6, t1: 47.7, tag: 'OPTION 1', label: 'On-ball: get above, force the sideline', focus: {x: 37, y: 23, zoom: 1.08}},
  {t0: 47.7, t1: 62.3, tag: 'OPTION 2', label: 'Screener’s defender: drop and call "Ice!"', focus: {x: 35, y: 24, zoom: 1.08}},
  {t0: 62.3, t1: 68.5, tag: 'WATCH FOR', label: 'Pop: big recovers to the shooter', focus: {x: 33, y: 27, zoom: 1.06}},
  {t0: 68.5, t1: 75.0, tag: 'WATCH FOR', label: 'Reject: keep the same angle', focus: {x: 36, y: 25, zoom: 1.06}},
  {t0: 75.0, t1: DUR, tag: 'SUMMARY', label: 'One plan. Close the middle.', focus: {x: 30, y: 23, zoom: 1}},
];
const sfx = [
  ...[9.6, 21.4, 35.6, 47.7, 62.3, 68.5, 75.0].map((t) => ({t, file: 'pop', volume: 0.35})),
  ...[35.0, 46.8, 61.4, 67.8, 74.6].map((t) => ({t, file: 'whoosh', volume: 0.35})),
  {t: 54.5, file: 'pop', volume: 0.5},
  {t: 85.3, file: 'sting', volume: 0.45},
];
const ep = {id: 'ep03-ice', title: 'ICE Ball-Screen Defence', kicker: 'DEFENCE', concept: 'ice-ball-screen-defence', durationSec: DUR, voice: 'vo.mp3', words, players, ball, arrows, highlights, steps, sfx};
fs.writeFileSync(new URL('episode.json', dir), JSON.stringify(ep));
console.log('episode.json written', JSON.stringify(ep).length, 'bytes');
