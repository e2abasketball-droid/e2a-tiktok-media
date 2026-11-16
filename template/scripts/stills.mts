// Quick review stills of a Tactical3DV2 episode: one bundle, one browser, a list of frames (or every Nth).
// Run: node --experimental-strip-types scripts/stills.mts <props.json> <outDir> <scale> <frames: "0,30,95" | "every:15">
import fs from 'node:fs';
import path from 'node:path';
import {bundle} from '@remotion/bundler';
import {openBrowser, renderStill, selectComposition} from '@remotion/renderer';
const [propsPath, outDir, scaleS, framesS] = process.argv.slice(2);
const props = JSON.parse(fs.readFileSync(propsPath, 'utf8'));
const CHROME = '/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell';
fs.mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts')});
const browser = await openBrowser('chrome', {browserExecutable: CHROME, chromiumOptions: {gl: 'swangle'}});
const composition = await selectComposition({serveUrl, id: 'Tactical3DV2', inputProps: props, puppeteerInstance: browser});
const frames = framesS.startsWith('every:') ? Array.from({length: Math.ceil(composition.durationInFrames / +framesS.slice(6))}, (_, i) => i * +framesS.slice(6)) : framesS.split(',').map(Number);
const q = [...frames];
const worker = async () => {
  for (let f = q.shift(); f !== undefined; f = q.shift()) {
    await renderStill({serveUrl, composition, inputProps: props, frame: f, output: path.join(outDir, `f${String(f).padStart(4, '0')}.jpg`), imageFormat: 'jpeg', jpegQuality: 85, scale: +scaleS, puppeteerInstance: browser, timeoutInMilliseconds: 180000, chromiumOptions: {gl: 'swangle'}});
  }
};
await Promise.all([worker(), worker(), worker()]);
await browser.close({silent: true});
console.log('stills', frames.length, outDir);
