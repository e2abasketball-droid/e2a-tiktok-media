// Source of truth for the Ep02 choreography. Run: node build-episode.mjs  → episode.json (timings from words.json).
import fs from 'node:fs';
const dir = new URL('.', import.meta.url);
const words = JSON.parse(fs.readFileSync(new URL('words.json', dir), 'utf8'));
const DUR = 73.8;
// Court feet: basket (25,5.25). x 0..50, y 0..47.
class Path {
  constructor(x, y) { this.pts = [{t: 0, x, y, dribble: false}]; this.x = x; this.y = y; }
  go(t0, t1, x, y, dribble = false) { // hold until t0, arrive at t1
    this.pts.push({t: t0, x: this.x, y: this.y, dribble: false}, {t: t1, x, y, dribble});
    this.x = x; this.y = y; return this;
  }
  done() { this.pts.push({t: DUR, x: this.x, y: this.y, dribble: false}); return this.pts; }
}
const START = {O1: [25, 29], O4: [19, 19], O5: [31, 19], O2: [5, 8], O3: [45, 8], X1: [25, 32], X4: [19, 22], X5: [31, 22], X2: [6, 12], X3: [44, 12]};
const P = Object.fromEntries(Object.entries(START).map(([k, v]) => [k, new Path(...v)]));
const reset = (t0, t1) => { for (const k in P) P[k].go(t0, t1, ...START[k]); };
const SCR = [33, 28.5];

// OPTION 1 (23.4-35.3): screen, drive, defender stops ball, roller finishes
P.O5.go(24.6, 25.6, ...SCR).go(28.0, 29.6, 27, 10).go(31.1, 32.8, 25, 6.8);
P.X5.go(24.6, 25.6, 31, 26).go(27.4, 28.6, 33, 21);
P.O1.go(25.8, 27.4, 35.5, 26, true).go(27.4, 29.2, 32, 16, true);
P.X1.go(25.8, 27.6, 31.5, 30.5).go(27.6, 30, 35, 22);
reset(34.0, 35.2);
// OPTION 2 (36.7-49.8): screen, drive, defence collapses, corner defender helps, kick-out three
P.O5.go(37.0, 37.9, ...SCR).go(38.3, 39.6, 28, 12);
P.X5.go(37.0, 37.9, 31, 26).go(38.6, 39.6, 28, 13);
P.O1.go(38.0, 39.4, 35.5, 26, true).go(39.4, 40.9, 33, 19, true);
P.X1.go(38.0, 39.6, 31.5, 30.5).go(39.6, 41, 35, 24);
P.X3.go(40.0, 41.2, 38, 14);
reset(48.4, 49.6);
// VARIATION: TWIST (51.2-55.5): off one screen, back off the other
P.O5.go(51.5, 52.3, ...SCR);
P.O4.go(53.1, 54.1, 19.5, 27.5);
P.O1.go(52.5, 53.7, 35.5, 26, true).go(53.9, 55.3, 21, 26, true);
P.X1.go(52.5, 53.8, 31.5, 30.5).go(54.0, 55.4, 25, 29);
reset(55.6, 56.5);
// VARIATION: FLARE (55.6-61.7): the first screener flares out off the other big's screen
P.O5.go(56.8, 57.4, ...SCR).go(58.4, 60.2, 10, 24);
P.O1.go(57.5, 58.6, 34, 26, true);
P.O4.go(58.2, 59.0, 17, 25.5);
P.X5.go(58.4, 60.4, 12.5, 25);
reset(61.0, 61.8);

const rand = []; const players = Object.keys(P).map((id) => ({id, team: id[0].toLowerCase(), label: id[0] === 'O' ? id.slice(1) : '', path: P[id].done()}));
const ball = [
  {t: 0, at: 'O1'}, {t: 30.4, at: 'O1'}, {t: 31.1, at: 'O5'}, {t: 32.8, at: 'O5'}, {t: 33.2, x: 25, y: 5.25}, {t: 34.0, x: 25, y: 5.25}, {t: 35.2, at: 'O1'},
  {t: 40.9, at: 'O1'}, {t: 41.8, at: 'O3'}, {t: 42.4, at: 'O3'}, {t: 43.3, x: 25, y: 5.25}, {t: 44.0, x: 25, y: 5.25}, {t: 49.6, at: 'O1'},
  {t: 61.5, at: 'O1'}, {t: DUR, at: 'O1'},
];
const arrows = [
  // hook / set-up labels
  {kind: 'dribble', from: [25, 29], to: [34, 26], t0: 19.0, t1: 20.2, show: 1.0},
  {kind: 'dribble', from: [25, 29], to: [16, 26], t0: 20.6, t1: 21.8, show: 1.0},
  // option 1
  {kind: 'screen', from: 'O5', to: SCR, t0: 24.6, t1: 25.6, show: 2.5},
  {kind: 'dribble', from: [25, 29], to: [35.5, 26], t0: 25.8, t1: 27.4, show: 1.0},
  {kind: 'cut', from: SCR, to: [27, 10], t0: 28.0, t1: 29.6, show: 1.8},
  {kind: 'pass', from: [32, 16], to: [27, 10], t0: 30.4, t1: 31.1, show: 1.6},
  // option 2
  {kind: 'screen', from: 'O5', to: SCR, t0: 37.0, t1: 37.9, show: 2.0},
  {kind: 'dribble', from: [25, 29], to: [35.5, 26], t0: 38.0, t1: 39.4, show: 1.0},
  {kind: 'cut', from: SCR, to: [28, 12], t0: 38.3, t1: 39.6, show: 1.4},
  {kind: 'pass', from: [33, 19], to: [45, 8], t0: 40.9, t1: 41.8, show: 3.5},
  // twist
  {kind: 'screen', from: 'O5', to: SCR, t0: 51.5, t1: 52.3, show: 2.8},
  {kind: 'dribble', from: [25, 29], to: [35.5, 26], t0: 52.5, t1: 53.7, show: 1.2},
  {kind: 'screen', from: 'O4', to: [19.5, 27.5], t0: 53.1, t1: 54.1, show: 1.8},
  {kind: 'dribble', from: [35.5, 26], to: [21, 26], t0: 53.9, t1: 55.3, show: 0.6},
  // flare
  {kind: 'screen', from: 'O5', to: SCR, t0: 56.8, t1: 57.4, show: 1.2},
  {kind: 'screen', from: 'O4', to: [17, 26], t0: 58.2, t1: 59.0, show: 2.4},
  {kind: 'cut', from: SCR, to: [10, 24], t0: 58.4, t1: 60.2, show: 1.0},
];
const highlights = [
  {x: 19, y: 19, r: 3.2, t0: 9.2, t1: 12.0}, {x: 31, y: 19, r: 3.2, t0: 9.6, t1: 12.0},
  {x: 5, y: 8, r: 3.2, t0: 11.8, t1: 14.8}, {x: 45, y: 8, r: 3.2, t0: 12.2, t1: 14.8},
  {x: 25, y: 29, r: 3.6, t0: 17.0, t1: 21.8},
  {x: 33, y: 28.5, r: 3.4, t0: 24.8, t1: 27.0}, {x: 27, y: 10, r: 3.8, t0: 29.6, t1: 33.0},
  {x: 33, y: 20, r: 6, t0: 44.9, t1: 47.2}, {x: 45, y: 8, r: 4.2, t0: 47.0, t1: 48.6},
  {x: 10, y: 24, r: 4, t0: 59.6, t1: 61.4},
];
const steps = [
  {t0: 0, t1: 6.6, tag: 'HOOK', label: 'One set. Three ways to score.', focus: {x: 25, y: 22, zoom: 1}},
  {t0: 6.6, t1: 16.1, tag: 'SET-UP', label: 'Guard on top, bigs at the elbows', focus: {x: 25, y: 20, zoom: 1.03}},
  {t0: 16.1, t1: 23.2, tag: 'THE KEY', label: 'Attack either screen', focus: {x: 25, y: 26, zoom: 1.04}},
  {t0: 23.2, t1: 35.2, tag: 'OPTION 1', label: 'Hit the roller early', focus: {x: 30, y: 19, zoom: 1.04}},
  {t0: 35.2, t1: 49.3, tag: 'OPTION 2', label: 'Draw two, pass to the open player', focus: {x: 34, y: 17, zoom: 1.04}},
  {t0: 49.3, t1: 55.6, tag: 'VARIATION', label: 'Twist: back off the second screen', focus: {x: 26, y: 26, zoom: 1.04}},
  {t0: 55.6, t1: 61.7, tag: 'VARIATION', label: 'Flare: screener steps out', focus: {x: 20, y: 22, zoom: 1.08}},
  {t0: 61.7, t1: DUR, tag: 'SUMMARY', label: 'One set. Multiple threats.', focus: {x: 25, y: 23, zoom: 1}},
];
const sfx = [
  ...[6.6, 16.1, 23.2, 35.2, 49.3, 61.7].map((t) => ({t, file: 'pop', volume: 0.35})),
  ...[34.1, 48.5, 55.6, 61.2].map((t) => ({t, file: 'whoosh', volume: 0.35})),
  {t: 31.1, file: 'catch', volume: 0.5}, {t: 41.8, file: 'catch', volume: 0.5},
  {t: 33.2, file: 'swish', volume: 0.5}, {t: 43.3, file: 'swish', volume: 0.5},
  {t: 70.5, file: 'sting', volume: 0.45},
];
const ep = {id: 'ep02-horns', title: 'The Horns Set', kicker: 'OFFENCE', concept: 'horns-set', durationSec: DUR, voice: 'vo.mp3', words, players, ball, arrows, highlights, steps, sfx};
fs.writeFileSync(new URL('episode.json', dir), JSON.stringify(ep));
console.log('episode.json written', JSON.stringify(ep).length, 'bytes');
