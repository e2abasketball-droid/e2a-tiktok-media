// Builds src/episodes/demo.json (Horns concept, synthetic timings) used ONLY to smoke-test the renderer.
import fs from 'node:fs';
const script = "What makes Horns so hard to defend? Two bigs at the elbows, and the ball up top. Five sets the screen. The guard attacks it. Option one: hit the roller. Option two: kick to the corner. One set. Multiple threats.";
const words = script.split(/\s+/);
const total = 14.6; const per = total / words.length;
const w = words.map((x, i) => ({w: x, s: +(0.3 + i * per).toFixed(2), e: +(0.3 + (i + 0.9) * per).toFixed(2)}));
const P = (id, team, label, path) => ({id, team, label, path: path.map(([t, x, y, dribble]) => ({t, x, y, dribble: !!dribble}))});
const ep = {
  id: 'demo-horns', title: 'Horns Set', kicker: 'OFFENCE', concept: 'horns', durationSec: 19.2, voice: 'demo_vo.mp3', words: w,
  players: [
    P('O1', 'o', '1', [[0, 25, 29], [3.2, 25, 29], [5.2, 34, 28, 1], [6.6, 30, 15, 1], [18, 30, 15]]),
    P('O4', 'o', '4', [[0, 19, 19], [18, 19, 19]]),
    P('O5', 'o', '5', [[0, 31, 19], [3.4, 31, 19], [4.6, 33, 26], [6.4, 33, 26], [7.8, 27, 9], [18, 27, 9]]),
    P('O2', 'o', '2', [[0, 5, 24], [18, 5, 24]]),
    P('O3', 'o', '3', [[0, 45, 9], [18, 45, 9]]),
    P('X1', 'd', '', [[0, 25, 32], [5.2, 31, 30], [6.6, 33, 22], [18, 33, 22]]),
    P('X4', 'd', '', [[0, 20, 22], [18, 20, 22]]),
    P('X5', 'd', '', [[0, 30, 22], [5.6, 33, 28], [7.2, 28, 14], [18, 28, 14]]),
    P('X2', 'd', '', [[0, 7, 14], [18, 7, 14]]),
    P('X3', 'd', '', [[0, 43, 13], [8, 43, 13], [9.4, 41, 12], [18, 41, 12]]),
  ],
  ball: [{t: 0, at: 'O1'}, {t: 8.4, at: 'O1'}, {t: 9.2, at: 'O3'}, {t: 11, at: 'O3'}, {t: 11.5, x: 25, y: 5.25}, {t: 18, x: 25, y: 5.25}],
  arrows: [
    {kind: 'screen', from: 'O5', to: [33, 26.5], t0: 3.4, t1: 4.6},
    {kind: 'dribble', from: [25, 29], to: [34, 28], t0: 4.4, t1: 5.4, show: 1.2},
    {kind: 'dribble', from: [34, 28], to: [30, 15], t0: 5.4, t1: 6.8, show: 1.5},
    {kind: 'cut', from: [33, 26], to: [27, 9], t0: 6.4, t1: 7.8, show: 1.6},
    {kind: 'pass', from: [30, 15], to: [45, 9], t0: 8.4, t1: 9.2, show: 1.6},
  ],
  highlights: [{x: 33, y: 26, r: 4, t0: 3.4, t1: 6.2}, {x: 45, y: 9, r: 4.5, t0: 8.8, t1: 11.2}],
  steps: [
    {t0: 0, t1: 3.0, tag: 'HOOK', label: 'Two bigs at the elbows', focus: {x: 25, y: 22, zoom: 1}},
    {t0: 3.0, t1: 6.8, tag: 'THE KEY', label: 'Screen + attack', focus: {x: 30, y: 24, zoom: 1.25}},
    {t0: 6.8, t1: 8.6, tag: 'OPTION 1', label: 'Hit the roller', focus: {x: 29, y: 14, zoom: 1.3}},
    {t0: 8.6, t1: 12.5, tag: 'OPTION 2', label: 'Kick to the corner', focus: {x: 38, y: 12, zoom: 1.3}},
    {t0: 12.5, t1: 19.2, tag: 'SUMMARY', label: 'One set. Multiple threats.', focus: {x: 25, y: 23, zoom: 1}},
  ],
  sfx: [{t: 3.4, file: 'pop'}, {t: 6.4, file: 'whoosh'}, {t: 9.2, file: 'catch'}, {t: 11.5, file: 'swish'}, {t: 16, file: 'sting'}],
};
fs.writeFileSync(new URL('../breakdown-template/src/episodes/demo.json', import.meta.url), JSON.stringify(ep, null, 1));
