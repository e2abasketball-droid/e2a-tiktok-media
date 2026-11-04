// Source of truth for Ep05 (The Euro Step) choreography. Run: node build-episode.mjs → episode.json (timings from words.json).
import fs from 'node:fs';
const dir = new URL('.', import.meta.url);
const words = JSON.parse(fs.readFileSync(new URL('words.json', dir), 'utf8'));
const DUR = 85;
class Path {
  constructor(x, y) { this.pts = [{t: 0, x, y, dribble: false}]; this.x = x; this.y = y; }
  go(t0, t1, x, y, dribble = false) { this.pts.push({t: t0, x: this.x, y: this.y, dribble: false}, {t: t1, x, y, dribble}); this.x = x; this.y = y; return this; }
  done() { this.pts.push({t: DUR, x: this.x, y: this.y, dribble: false}); return this.pts; }
}
const START = {O1: [38, 26], O2: [25, 33], O3: [12, 26], O4: [4, 9], O5: [21, 6.5], X1: [36, 23.5], X2: [26, 29.5], X3: [15, 23], X4: [7, 12], X5: [14, 12]};
const P = Object.fromEntries(Object.entries(START).map(([k, v]) => [k, new Path(...v)]));
const reset = (t0, t1) => { for (const k in P) if (P[k].x !== START[k][0] || P[k].y !== START[k][1]) P[k].go(t0, t1, ...START[k]); };
const G = [36, 19], S1 = [37.5, 14.5], S2 = [30.5, 10.5], FRONT = [33.2, 16.2], SLID = [35.6, 14.2], RIM = [25, 5.25];
// SET-UP (7.2-17.4): defender slides in front to cut off the lane
P.X1.go(11.3, 13.0, 34, 21);
reset(16.0, 17.0);
// OPTION 1 (28.8-46.5): gather, wide first step (defender slides), second step opposite way, finish
P.O1.go(31.0, 32.4, ...G, true).go(33.7, 34.5, ...S1).go(37.6, 38.6, ...S2);
P.X1.go(31.0, 32.4, ...FRONT).go(34.3, 36.2, ...SLID);
reset(43.0, 44.4);
// OPTION 2 (46.5-62.1): helper waits at rim; same two steps; helper steps out; pass to O5; easy finish
P.X5.go(46.6, 48.0, 24.5, 9.5);
P.O1.go(47.9, 48.7, ...G, true).go(48.9, 49.6, ...S1).go(49.9, 50.7, ...S2);
P.X1.go(47.9, 48.7, ...FRONT).go(49.3, 50.4, ...SLID);
P.X5.go(51.2, 52.6, 28.8, 12.4);
reset(60.6, 61.8);
// COUNTER 1 (62.1-68.5): defender does not follow step one -> finish straight through the gap
P.O1.go(63.3, 64.2, ...G, true).go(64.8, 65.5, ...S1).go(66.3, 67.2, 29.5, 9.5);
P.X1.go(63.3, 64.2, ...FRONT);
reset(68.2, 68.9);
// COUNTER 2 (69.0-72): defender stays tight -> protect the ball with the outside hand, keep it high
P.O1.go(69.0, 69.8, ...G, true).go(70.4, 71.4, 37.2, 16.6);
P.X1.go(69.0, 69.8, 34.4, 17.4).go(70.4, 71.4, 35.4, 16.2);
reset(72.0, 73.0);
// SUMMARY (73.4-): one gather, two steps, one direction he cannot guard
P.O1.go(73.4, 74.1, ...G, true).go(74.6, 75.3, ...S1).go(75.9, 76.7, ...S2);
P.X1.go(73.4, 74.1, ...FRONT).go(74.9, 76.2, ...SLID);
reset(81.0, 82.0);
const players = Object.keys(P).map((id) => ({id, team: id[0].toLowerCase(), label: id[0] === 'O' ? id.slice(1) : '', path: P[id].done()}));
const R = {x: RIM[0], y: RIM[1]};
const ball = [
  {t: 0, at: 'O1'}, {t: 40.0, at: 'O1'}, {t: 40.7, ...R}, {t: 42.5, ...R}, {t: 44.0, at: 'O1'},
  {t: 54.4, at: 'O1'}, {t: 55.1, at: 'O5'}, {t: 56.0, at: 'O5'}, {t: 56.6, ...R}, {t: 59.6, ...R}, {t: 61.4, at: 'O1'},
  {t: 67.0, at: 'O1'}, {t: 67.6, ...R}, {t: 68.0, ...R}, {t: 68.6, at: 'O1'},
  {t: 77.0, at: 'O1'}, {t: 77.7, ...R}, {t: DUR, ...R},
];
const arrows = [
  {kind: 'dribble', from: START.O1, to: G, t0: 31.0, t1: 32.4, show: 1.0},
  {kind: 'cut', from: G, to: S1, t0: 33.7, t1: 34.5, show: 6.0},
  {kind: 'cut', from: S1, to: S2, t0: 37.6, t1: 38.6, show: 4.0},
  {kind: 'dribble', from: START.O1, to: G, t0: 47.9, t1: 48.7, show: 1.0},
  {kind: 'cut', from: G, to: S1, t0: 48.9, t1: 49.6, show: 3.0},
  {kind: 'cut', from: S1, to: S2, t0: 49.9, t1: 50.7, show: 3.0},
  {kind: 'pass', from: S2, to: [21, 6.5], t0: 54.5, t1: 55.1, show: 2.2},
  {kind: 'cut', from: G, to: S1, t0: 64.8, t1: 65.5, show: 2.0},
  {kind: 'cut', from: S1, to: [29.5, 9.5], t0: 66.3, t1: 67.2, show: 2.0},
  {kind: 'dribble', from: G, to: [37.2, 16.6], t0: 70.4, t1: 71.4, show: 1.2},
  {kind: 'cut', from: G, to: S1, t0: 74.6, t1: 75.3, show: 3.0},
  {kind: 'cut', from: S1, to: S2, t0: 75.9, t1: 76.7, show: 3.0},
];
const highlights = [
  {x: 37, y: 20, r: 6, t0: 3.6, t1: 6.8},
  {x: 34, y: 21, r: 4.2, t0: 12.4, t1: 15.8},
  {x: 37.5, y: 14.5, r: 3.8, t0: 18.8, t1: 21.2}, {x: 30.5, y: 10.5, r: 3.8, t0: 21.4, t1: 24.6},
  {x: 37.5, y: 14.5, r: 3.8, t0: 34.0, t1: 37.0}, {x: 30.5, y: 10.5, r: 3.8, t0: 37.8, t1: 41.0},
  {x: 24.5, y: 9.5, r: 4, t0: 47.0, t1: 50.2}, {x: 28.8, y: 12.4, r: 4, t0: 52.2, t1: 54.4},
  {x: 21, y: 6.5, r: 4, t0: 54.6, t1: 57.6},
  {x: 33.2, y: 16.2, r: 4, t0: 64.4, t1: 66.2}, {x: 29.5, y: 9.5, r: 3.8, t0: 66.4, t1: 68.0},
  {x: 37, y: 16.8, r: 4, t0: 70.5, t1: 72.0},
  {x: 30.5, y: 10.5, r: 4, t0: 76.3, t1: 79.0},
];
const steps = [
  {t0: 0, t1: 7.2, tag: 'HOOK', label: 'Past a defender in two steps', focus: {x: 31, y: 18, zoom: 1}},
  {t0: 7.2, t1: 17.4, tag: 'SET-UP', label: 'Attacking from the wing', focus: {x: 31, y: 20, zoom: 1.02}},
  {t0: 17.4, t1: 28.8, tag: 'THE KEY', label: 'Step 1 moves him, step 2 beats him', focus: {x: 32, y: 16, zoom: 1.06}},
  {t0: 28.8, t1: 46.5, tag: 'OPTION 1', label: 'Wide step, then sideways', focus: {x: 32, y: 14, zoom: 1.08}},
  {t0: 46.5, t1: 62.1, tag: 'OPTION 2', label: 'Helper steps out: pass', focus: {x: 28, y: 12, zoom: 1.04}},
  {t0: 62.1, t1: 68.9, tag: 'WATCH FOR', label: 'No reaction? Go straight', focus: {x: 32, y: 13, zoom: 1.06}},
  {t0: 68.9, t1: 73.0, tag: 'WATCH FOR', label: 'Tight? Protect the ball', focus: {x: 34, y: 17, zoom: 1.08}},
  {t0: 73.0, t1: DUR, tag: 'SUMMARY', label: 'One gather. Two steps.', focus: {x: 31, y: 15, zoom: 1.04}},
];
const sfx = [
  ...[7.2, 17.4, 28.8, 46.5, 62.1, 68.9, 73.0].map((t) => ({t, file: 'pop', volume: 0.35})),
  ...[28.2, 45.9, 61.5, 68.4, 72.5].map((t) => ({t, file: 'whoosh', volume: 0.35})),
  ...[55.1].map((t) => ({t, file: 'catch', volume: 0.5})),
  ...[40.7, 56.6, 67.6, 77.7].map((t) => ({t, file: 'swish', volume: 0.55})),
  {t: DUR - 2.8, file: 'sting', volume: 0.45},
];
const ep = {id: 'ep05-euro-step', title: 'The Euro Step', kicker: 'INDIVIDUAL SKILL', concept: 'euro-step', durationSec: DUR, voice: 'vo.mp3', words, players, ball, arrows, highlights, steps, sfx};
fs.writeFileSync(new URL('episode.json', dir), JSON.stringify(ep));
console.log('episode.json written', JSON.stringify(ep).length, 'bytes');
