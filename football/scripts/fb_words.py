#!/usr/bin/env python3
"""Export the caption timing of an FB episode script as word timings [{text,start,end}].

Mirrors line() in football/remotion/src/episodes/*.ts: each script line's words are spread over the
line window by length. Used for the silent cut (music bed sync) until a real voice take exists.
"""
import json
import re
import sys


def words_from_ts(path):
    src = open(path, encoding='utf-8').read()
    block = src.split('export const SCRIPT', 1)[1].split('];', 1)[0]
    out = []
    for a, b, q, text in re.findall(r"\[([\d.]+),\s*([\d.]+),\s*(['\"])(.*?)\3\]", block):
        a, b = float(a), float(b)
        text = text.replace("\\'", "'")
        ws = text.split()
        wt = [0.6 + len(re.sub(r'[^A-Za-z0-9]', '', w)) for w in ws]
        tot = sum(wt)
        t = a
        for w, k in zip(ws, wt):
            d = (b - a) * k / tot
            out.append({'text': w, 'start': round(t, 3), 'end': round(t + d * 0.92, 3)})
            t += d
    return out


if __name__ == '__main__':
    json.dump(words_from_ts(sys.argv[1]), sys.stdout, indent=0, ensure_ascii=False)
