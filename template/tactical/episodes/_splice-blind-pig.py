#!/usr/bin/env python3
"""BLIND PIG V2 / Trial B narration sources (master prompt 2026-11-19, sec. 4 'Si la voz ya está grabada').
The main take (535 credits) is KEPT: its mechanism, hook, two reads and length match the final script.
Two edits, both made only at acoustic silences (quietest 10 ms inside the silence, 8 ms fades, no stretch):
  - V2:      drop "Now the defender can't see both." (removed from the final script; it also over-claims what X2 sees)
             and add "Easy layup." after "the denial." from take B.
  - Trial B: as V2, but the hook "He denied the pass... and gave up the layup." is replaced by take B's
             "This defender made one mistake... Can you spot it?".
Take B = ONE extra short Deuce take (eleven_v4, 84 credits, same flow g5DXlcDEXV4pY5NtWFbB), Scribe 0 credits.
Take B is level-matched to the main take (speech RMS) so the splice is not audible as a jump.
  python3 tactical/episodes/_splice-blind-pig.py   (from template/)
Writes public/tactical/blindpig/voice-raw-v2.wav, voice-raw-trialb.wav and the matching *.words-raw.json."""
import json, os, subprocess
import numpy as np

SR = 44100
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)
E = P('tactical', 'episodes')


def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()


A = load(P('public', 'tactical', 'blindpig', 'voice-raw.mp3'))
B = load(P('public', 'tactical', 'blindpig', 'voice-raw-b.mp3'))
WA = json.load(open(os.path.join(E, 'blind-pig.words-raw.json')))
WB = json.load(open(os.path.join(E, 'blind-pig-b.words-raw.json')))


def rms10(x):
    hop = int(0.01 * SR)
    n = len(x) // hop
    return np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)


def speech_rms(x):
    r = rms10(x)
    return float(np.sqrt(np.mean(r[20 * np.log10(r) > -35] ** 2)))


B *= speech_rms(A) / speech_rms(B)


def cut_in(x, s0, s1):
    """quietest 10 ms in the middle half of the acoustic silence [s0, s1] (seconds)"""
    r = rms10(x)
    lo, hi = int((s0 + 0.25 * (s1 - s0)) * 100), int((s0 + 0.75 * (s1 - s0)) * 100) + 1
    return (lo + int(np.argmin(r[lo:hi]))) * 0.01 + 0.005


# acoustic silences measured with silencedetect -45 dB (see the voice report)
A_HIM = cut_in(A, 11.143, 11.492)    # after "...cuts behind him."
A_BOTH = cut_in(A, 13.872, 14.203)   # after "...can't see both."
A_DEN = cut_in(A, 17.699, 18.100)    # after "...beats the denial."
A_HOOK = cut_in(A, 2.532, 3.021)     # after "...gave up the layup."
B_SPOT = cut_in(B, 3.491, 3.958)     # after "Can you spot it?"
B_END = 4.95                         # tail of "Easy layup." (silence from 4.78)


def build(segs, out_wav, out_words):
    FADE = int(0.008 * SR)
    parts, words, t = [], [], 0.0
    for src, ws, a, b in segs:
        seg = src[int(a * SR):int(b * SR)].copy()
        n = min(FADE, len(seg) // 2)
        seg[:n] *= np.linspace(0, 1, n)
        seg[-n:] *= np.linspace(1, 0, n)
        parts.append(seg)
        for w in ws:
            mid = (w['start'] + w['end']) / 2
            if a <= mid < b:
                words.append({'text': w['text'], 'start': round(w['start'] - a + t, 3), 'end': round(min(w['end'], b) - a + t, 3)})
        t += len(seg) / SR
    y = np.concatenate(parts)
    pcm = (np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-', out_wav], input=pcm, check=True)
    json.dump(words, open(out_words, 'w'))
    print(os.path.basename(out_wav), f'{len(y) / SR:.2f} s', ' '.join(w['text'] for w in words))
    return [(os.path.basename(out_wav), round(a, 3), round(b, 3), 'A' if src is A else 'B') for src, _, a, b in segs]


v2 = [(A, WA, 0.0, A_HIM), (A, WA, A_BOTH, A_DEN), (B, WB, B_SPOT, B_END), (A, WA, A_DEN, len(A) / SR)]
tb = [(B, WB, 0.0, B_SPOT), (A, WA, A_HOOK, A_HIM), (A, WA, A_BOTH, A_DEN), (B, WB, B_SPOT, B_END), (A, WA, A_DEN, len(A) / SR)]
rep = {'v2': build(v2, P('public', 'tactical', 'blindpig', 'voice-raw-v2.wav'), os.path.join(E, 'blind-pig-v2.words-raw.json')),
       'trialb': build(tb, P('public', 'tactical', 'blindpig', 'voice-raw-trialb.wav'), os.path.join(E, 'blind-pig-trialb.words-raw.json')),
       'take_b_gain': round(float(speech_rms(A) / speech_rms(load(P('public', 'tactical', 'blindpig', 'voice-raw-b.mp3')))), 3),
       'segments': 'source, start, end (seconds) of take A (main, 535 credits) or take B (84 credits), cut at acoustic silences'}
json.dump(rep, open(os.path.join(E, 'blind-pig-splice-report.json'), 'w'), indent=1)
