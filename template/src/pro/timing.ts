import type {Anchor, Episode, SceneSpec, Word} from './types';

export const norm = (s: string) => s.toLowerCase().replace(/[^a-z0-9]/g, '');

/** Resolve an anchor (phrase in the narration, or seconds) to seconds. "phrase#2" = 2nd occurrence. */
export const makeResolver = (words: Word[]) => {
  const keys = words.map((w) => norm(w.text));
  return (a: Anchor, off = 0): number => {
    if (typeof a === 'number') return a + off;
    const [phrase, occ] = a.split('#');
    const want = occ ? parseInt(occ, 10) - 1 : 0;
    const p = phrase.split(/\s+/).map(norm).filter(Boolean);
    let seen = 0;
    for (let i = 0; i + p.length <= keys.length; i++) {
      if (p.every((w, k) => keys[i + k] === w)) {
        if (seen === want) return words[i].start + off;
        seen++;
      }
    }
    throw new Error(`Anchor not found in narration: "${a}"`);
  };
};

export const voiceEnd = (words: Word[]) => (words.length ? words[words.length - 1].end : 0);
export const outroSeconds = (ep: Episode) => ep.outro?.seconds ?? 1.4;
export const totalSeconds = (ep: Episode) => voiceEnd(ep.words) + 0.25 + outroSeconds(ep);

export type Timed = {spec: SceneSpec; start: number; end: number; index: number};

/** Scenes run from their anchor to the next scene's anchor; the last one runs to the outro. */
export const layoutScenes = (ep: Episode): Timed[] => {
  const T = makeResolver(ep.words);
  const starts = ep.scenes.map((s) => T(s.at, s.offset ?? 0));
  const outroAt = voiceEnd(ep.words) + 0.25;
  return ep.scenes.map((spec, index) => ({
    spec,
    index,
    start: index === 0 ? 0 : starts[index],
    end: index + 1 < starts.length ? starts[index + 1] : outroAt,
  }));
};
