#!/usr/bin/env python3
"""E2A HORNS: THE DEFENDER'S DILEMMA (owner brief 2026-11-22) - the edit, as Remotion props for Tactical3DV2.
One fixed tactical camera (basket up, behind the offence, all ten players), one micro zoom at the decision, two
branches from the SAME decision frame (play A horns-rp-a-help / play B horns-rp-b-stay, sample-identical to 6.6 s).
Timing source: --words <words.json> (real narration, from scripts/tactical-voice.py) or the GUIDE timings below
(no approved voice yet: subtitles follow the guide and the MP4 is labelled VISUAL_MASTER_PENDING_AUDIO).
Every shot is anchored to the line it illustrates (LINES[...]['start'/'end']), so a new voice take only moves cuts.
  python3 tactical/episodes/_gen-horns-roll-pop.py --out props.json [--words w.json] [--voice path] [--music path]
         [--preview]   (preview = same edit, rendered at --scale 0.5 by the caller)"""
import argparse, json, math, os

D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
A = json.load(open(os.path.join(T, "tactical", "plays", "horns-rp-a-help.json")))
B = json.load(open(os.path.join(T, "tactical", "plays", "horns-rp-b-stay.json")))
DEC = 6.6          # the shared decision frame (both plays sample-identical, V3.3 ball too, up to 6.65 s)
GOLD, NAVY, ROLLC, WHITE = "#C9A24D", "#0B1C3D", "#8EC5F0", "#FFFFFF"

# the authorised script (brief sec. 03), one entry per subtitle line; GUIDE start/end in video seconds (~2.6 w/s)
LINES = [
    ("hook1", "Don't watch the ball.", 0.15, 1.2),
    ("hook2", "Watch this defender.", 1.3, 2.4),
    ("horns", "This is Horns.", 3.0, 3.95),
    ("bigs", "Two bigs at the elbows,", 4.25, 5.6),
    ("corners", "with shooters in both corners.", 5.7, 7.4),
    ("screen", "The guard takes Five's screen.", 8.7, 10.5),
    ("roll", "Five rolls hard to the rim.", 11.0, 12.8),
    ("pop", "Four pops behind the arc.", 13.3, 15.0),
    ("read", "Now this defender has to read both.", 16.95, 19.15),
    ("help", "If he tags the roll,", 20.3, 21.55),
    ("three", "Four is open for three.", 21.7, 23.1),
    ("stay", "If he stays with Four,", 28.3, 29.65),
    ("inside", "the pass inside might be there.", 29.8, 31.7),
    ("setup", "Same setup.", 35.5, 36.3),
    ("threats", "Two threats.", 36.65, 37.5),
    ("pressure", "That's the pressure Horns creates.", 37.95, 40.0),
]


def guide_words():
    out = []
    for _, text, a, b in LINES:
        ws = text.split()
        tot = sum(len(w) + 1 for w in ws)
        t = a
        for w in ws:
            d = (b - a) * (len(w) + 1) / tot
            out.append({"text": w, "start": round(t, 3), "end": round(t + d * 0.92, 3)})
            t += d
    return out


def line_times(words):
    """start/end of every LINE from the word list (real or guide): lines are matched in order by word count"""
    res, i = {}, 0
    for key, text, _, _ in LINES:
        n = len(text.split())
        seg = words[i:i + n]
        res[key] = (seg[0]["start"], seg[-1]["end"])
        i += n
    assert i == len(words), (i, len(words))
    return res


def pos(play, pid, t):
    tr = play["tracks"][pid]
    for a, b in zip(tr, tr[1:]):
        if a[0] <= t <= b[0]:
            u = (t - a[0]) / max(1e-9, b[0] - a[0])
            return [round(a[1] + (b[1] - a[1]) * u, 3), round(a[2] + (b[2] - a[2]) * u, 3)]
    return tr[-1][1:3]


orb = lambda tg, dist, pitch, yaw=0, fov=50: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
MAIN = orb([0.0, 7.45, 0.6], 22.0, 52)                 # fit-search: all ten, feet + head, safe 440-1360 px, 2.4-9.4 s
ZOOM = orb([1.0, 6.45, 0.6], 19.8, 52)                  # decision: ~10 % closer on the X4 / O5 / O4 triangle, same axis


def build(words, voice, music, preview):
    L = line_times(words)
    x4, o5, o4 = pos(A, "X4", DEC), pos(A, "O5", DEC), pos(A, "O4", DEC)
    # where each read takes X4 (from the real branch tracks) - the two thin options drawn at the decision
    helpTo, stayTo = pos(A, "X4", 7.7), pos(B, "X4", 7.55)
    ROLL_PTS = [[-0.5, 8.23], [-0.85, 7.35], [-0.78, 5.4], [-0.55, 3.4]]
    POP_PTS = [[2.45, 5.85], [3.6, 6.3], [4.95, 6.9]]
    T0 = 0.0
    t_setup = L["hook2"][1] + 0.45                  # hook ends after "Watch this defender." + a breath
    t_action = L["corners"][1] + 1.0
    t_read = L["pop"][1] + 1.6
    t_a = L["read"][1] + 0.65
    t_b = L["three"][1] + 4.2                       # the three flies, drops, the shooter lands
    t_close = L["inside"][1] + 3.0                  # the catch, the finish, the make
    t_end = L["pressure"][1] + 3.0
    shots = []
    # 1 HOOK: the critical moment (play 5.95 -> 6.6), then a short freeze on X4 with the gold halo
    d = t_setup - T0
    shots.append({"id": "hook", "name": "Hook - don't watch the ball, watch this defender", "at": T0, "play": "A",
                  "remap": [[0, 5.95], [1.15, DEC], [d, DEC]], "camera": [key(0, MAIN)],
                  "ov3": [{"type": "ring", "player": "X4", "color": GOLD, "from": 0.15, "to": d}],
                  "screen": [{"type": "title", "lines": ["DON'T WATCH", "THE BALL."], "gold": [], "from": 0.0, "to": 1.15, "y": 236, "size": 96},
                             {"type": "title", "lines": ["WATCH HIM."], "gold": [0], "from": 1.15, "to": d - 0.1, "y": 236, "size": 104},
                             {"type": "freeze", "from": 1.15, "to": d}]})
    # 2 SETUP: the formation from the walk-up (real time), then the set (slower), HORNS label, elbows and corners lit
    d = t_action - t_setup
    lb = L["bigs"][0] - t_setup
    lc = L["corners"][0] - t_setup
    shots.append({"id": "setup", "name": "Setup - Horns 1-2-2: bigs at the elbows, shooters in the corners", "at": t_setup, "play": "A",
                  "remap": [[0, 0.0], [2.55, 2.55], [d, 3.9]], "camera": [key(0, MAIN)],
                  "ov3": [{"type": "ring", "player": "O4", "color": GOLD, "from": lb, "to": lb + 2.6},
                          {"type": "ring", "player": "O5", "color": GOLD, "from": lb, "to": lb + 2.6},
                          {"type": "ring", "player": "O2", "color": WHITE, "from": lc, "to": d - 0.2},
                          {"type": "ring", "player": "O3", "color": WHITE, "from": lc, "to": d - 0.2}],
                  "screen": [{"type": "title", "lines": ["HORNS"], "gold": [0], "from": 0.15, "to": d - 0.15, "y": 236, "size": 110}]})
    # 3 ACTION: screen (0.67x), then the roll and the pop at ~0.24x with one arrow each, stopping on the decision frame
    d = t_read - t_action
    lr, lp = L["roll"][0] - t_action, L["pop"][0] - t_action
    k1 = L["screen"][1] - t_action + 0.2
    shots.append({"id": "action", "name": "Screen, roll, pop - one movement per phrase", "at": t_action, "play": "A",
                  "remap": [[0, 3.9], [k1, 5.5], [d - 0.5, DEC], [d, DEC]], "camera": [key(0, MAIN)],
                  "ov3": [{"type": "route", "player": "O5", "t0": 0, "t1": 1, "pts": ROLL_PTS, "color": ROLLC, "dashed": False, "width": 0.09,
                           "label": "ROLL", "labelYaw": 0, "labelSize": 0.9, "from": lr - 0.2, "to": d},
                          {"type": "route", "player": "O4", "t0": 0, "t1": 1, "pts": POP_PTS, "color": GOLD, "dashed": False, "width": 0.09,
                           "label": "POP", "labelYaw": 0, "labelSize": 0.9, "from": lp - 0.2, "to": d}],
                  "screen": []})
    # 4 READ (rehook): the decision frame held, ~10 % closer, X4 outlined, his two options as thin dashed lines
    d = t_a - t_read
    shots.append({"id": "read", "name": "Rehook - now this defender has to read both", "at": t_read, "play": "A",
                  "remap": [[0, DEC], [d, DEC]], "camera": [key(0, MAIN), key(0.9, ZOOM, "inOut"), key(d, ZOOM)],
                  "ov3": [{"type": "ring", "player": "X4", "color": GOLD, "from": 0.1, "to": d},
                          {"type": "route", "player": "X4", "t0": 0, "t1": 1, "pts": [x4, helpTo], "color": ROLLC, "dashed": True, "width": 0.1, "from": 1.1, "to": d},
                          {"type": "route", "player": "X4", "t0": 0, "t1": 1, "pts": [x4, stayTo], "color": GOLD, "dashed": True, "width": 0.1, "from": 1.1, "to": d}],
                  "screen": [{"type": "freeze", "from": 0.0, "to": d}]})
    # 5 BRANCH A: X4 tags the roll -> kick-out -> the three (the camera is back on the wide frame BEFORE the pass)
    d = t_b - t_a
    lh, l3 = L["help"][0] - t_a, L["three"][0] - t_a
    shots.append({"id": "branchA", "name": "A - he tags the roll, Four is open for three", "at": t_a, "play": "A",
                  "remap": [[0, DEC], [2.4, 7.55], [4.6, 8.75], [d, 10.2]],
                  "camera": [key(0, ZOOM), key(0.8, MAIN, "inOut"), key(d, MAIN)],
                  "ov3": [{"type": "ring", "player": "X4", "color": GOLD, "from": 0.0, "to": 2.4},
                          {"type": "passLane", "src": "O1", "dst": "O4", "color": WHITE, "from": 2.3, "to": 3.4}],
                  "screen": [{"type": "pin", "player": "X4", "text": "HELP", "tone": "gold", "from": lh + 0.1, "to": lh + 0.9, "size": 40},
                             {"type": "pin", "player": "O4", "text": "OPEN THREE", "tone": "white", "from": l3 + 0.2, "to": l3 + 1.3, "size": 40}]})
    # 6 BRANCH B: back to the same moment (0.3 s before the decision frame), X4 stays, the pass inside, the finish
    d = t_close - t_b
    ls, li = L["stay"][0] - t_b, L["inside"][0] - t_b
    shots.append({"id": "branchB", "name": "B - same action, different help: he stays, the pass inside", "at": t_b, "play": "B",
                  "remap": [[0, 6.3], [1.1, DEC], [ls + 1.6, 7.55], [li + 1.6, 8.2], [d - 0.5, 9.7], [d, 9.75]],
                  "camera": [key(0, MAIN)],
                  "ov3": [{"type": "ring", "player": "X4", "color": GOLD, "from": 0.9, "to": ls + 1.6},
                          {"type": "passLane", "src": "O1", "dst": "O5", "color": WHITE, "from": ls + 1.5, "to": li + 1.4}],
                  "screen": [{"type": "stamp", "text": "SAME ACTION. DIFFERENT HELP.", "tone": "white", "from": 0.0, "to": 0.85, "y": 250, "instant": True},
                             {"type": "pin", "player": "X4", "text": "STAY", "tone": "gold", "from": ls + 0.1, "to": ls + 0.8, "size": 40},
                             {"type": "pin", "player": "O5", "text": "ROLL", "tone": "white", "from": li + 0.3, "to": li + 1.2, "size": 40}]})
    # 7 CLOSE: the decision frame again, the two reads as clean lines, ONE SET. TWO READS., HELP OR STAY?, logo
    d = t_end - t_close
    shots.append({"id": "close", "name": "Close - one set, two reads", "at": t_close, "play": "A",
                  "remap": [[0, DEC], [d, DEC]], "camera": [key(0, MAIN)],
                  "ov3": [{"type": "route", "player": "O5", "t0": 0, "t1": 1, "pts": ROLL_PTS, "color": ROLLC, "dashed": False, "width": 0.08, "from": 0.1, "to": d - 1.6},
                          {"type": "route", "player": "O4", "t0": 0, "t1": 1, "pts": POP_PTS, "color": GOLD, "dashed": False, "width": 0.08, "from": 0.1, "to": d - 1.6},
                          {"type": "ring", "player": "X4", "color": GOLD, "from": d - 1.6, "to": d}],
                  "screen": [{"type": "title", "lines": ["ONE SET.", "TWO READS."], "gold": [1], "from": 0.3, "to": d - 1.7, "y": 236, "size": 90},
                             {"type": "title", "lines": ["HELP OR STAY?"], "gold": [0], "from": d - 1.6, "to": d, "y": 236, "size": 96},
                             {"type": "logo", "big": False, "from": d - 1.6, "to": d}]})
    ep = {
        "id": "horns-roll-pop-minimal", "title": "HORNS: THE DEFENDER'S DILEMMA", "fps": 30,
        "voice": voice, "tail": round(t_end - words[-1]["end"], 3), "autoSfx": False, "pinV2": True, "env": "cinema",
        "athleteRenderer": "v33",
        "words": words,
        # subtitle lines = the script lines (1-2 lines on screen, 2-6 words)
        "subtitleGroups": [len(t.split()) for _, t, _, _ in LINES],
        "subtitleBlock": True, "subtitleY": 1390, "subtitleHide": [[t_close + (t_end - t_close) - 1.7, 999]],
        "keywords": ["Horns", "defender", "screen", "rolls", "pops", "read", "both", "tags", "open", "three", "stays", "inside", "threats"],
        "gradeBottom": 0.3,
        "shots": shots, "plays": {"A": A, "B": B},
    }
    if music:
        ep["music"] = {"src": music, "volume": 1}
    meta = {"duration": round(t_end, 3), "cuts": {s["id"]: round(s["at"], 3) for s in shots}, "lines": L}
    return {"episode": ep}, meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--words")
    ap.add_argument("--voice", default="tactical/realism-v3-3/silence.mp3")
    ap.add_argument("--music")
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    words = json.load(open(a.words)) if a.words else guide_words()
    props, meta = build(words, a.voice, a.music, a.preview)
    json.dump(props, open(a.out, "w"))
    print(json.dumps(meta))
