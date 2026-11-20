#!/usr/bin/env python3
"""PISTOL FAKE HANDOFF in transition (owner brief E2A-Prompt-Claude-Pistol-Fake-Handoff-PCD.md, 2026-11-20).
Tactical branches (inside the files): keep = play A pfh-keep (O2 fakes the handoff back, keeps it, baseline drive, layup)
                                      give = play B pfh-give (X2 holds the baseline, the real handoff back to O1)
Edit variants (file names): Hook-A ("This handoff is a lie.") / Hook-B ("He sold a handoff that never happened."): SAME
hook shot, camera, remap, duration (2.80 s), music and body; only the opening voice + its title card change.
  python3 tactical/specs/_gen-pfh.py                                   (plays pfh-keep / pfh-give + QC claims)
  python3 scripts/tactical-voice.py tactical/episodes/pfh-a.json       (ONE Deuce take; gaps; gapFill silence)
  python3 tactical/episodes/_voice-pfh.py                              (hook B take spliced in; mixes)
  python3 tactical/episodes/_gen-pfh.py                                -> pfh-main-a.json, pfh-main-b.json
  python3 tactical/episodes/_bundle-blind-pig.py out/pfh pfh-main-a pfh-main-b
  bash out/pfh/render.sh pfh-main-a ; bash out/pfh/render.sh pfh-main-b 0-95 -hook
  python3 tactical/episodes/_finish-pfh.py <deliver_dir>
Hands rehearsal (real vs fake, 3/4 + lateral + game view, no overlays): tactical/episodes/_rehearsal-pfh.py.
PCD sheet: produccion/tactical/pcd/pistol-fake-handoff.md.
Repo axes: x = -brief x (the right wing of the brief is x < 0 here), y from the attacked baseline, rim (0, 1.575, 3.05).
Orbit yaw 0 = camera on the half-court side looking at the basket; yaw -90 = camera at x > 0 (court middle, for this
wing); pitch = angle from the vertical (90 = horizontal). No ball / bounce SFX, voice + music only."""
import json, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
orb = lambda tg, dist, pitch, yaw, fov=40: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
S = lambda n: round(n / 30, 4)
RED = "#E5483A"

# the handoff point (brief (5.35, 6.58) -> repo (-5.35, 6.58)); O2 sits at (-5.70, 6.55), X2 inside-low at (-4.95, 5.60)
HOOK = orb([-5.3, 6.2, 1.0], 5.4, 60, -20)           # close 3/4 from the inside-high: ball, O1's hands, O2's chest, X2
HOOK_IN = orb([-5.3, 6.2, 1.05], 4.8, 62, -22)       # slow push-in (lens/position, no nervous zoom)
ENTRY0 = orb({"follow": ["O1", "O2"], "z": 0.8}, 10.5, 52, -12, 44)   # tracking from the right slot (behind O1, high)
ENTRY1 = orb({"follow": ["O1", "O2"], "z": 0.9}, 8.0, 56, -14, 42)
# fake / give / mirror: elevated lateral from the half-court side (probe 2026-11-20: keep S047-S054 and give S051-S055
# keep the ball visible between both pairs of hands; the low lateral (pitch 80) and the baseline 3/4 hid it behind O1/X2)
FAKE = orb([-5.2, 6.3, 0.95], 6.2, 57, -8)
FAKE_IN = orb([-5.2, 6.3, 0.95], 5.7, 57, -10)
REVEAL0 = orb({"follow": "O2", "z": 1.0, "window": 0.5}, 6.6, 64, -22)
REVEAL1 = orb({"follow": "O2", "z": 0.9, "window": 0.5}, 7.4, 62, -40)
# drive: 3/4 from the inside (court side of the lane), following O2; then the rim, net and landing. The first version
# (yaw -128, baseline side) sat behind the basket stanchion: the padded post covered the drive and the layup.
DRIVE0 = orb({"follow": "O2", "z": 0.9, "lead": 0.25, "window": 0.6}, 8.5, 66, -75, 44)
DRIVE1 = orb([-1.2, 2.2, 1.6], 8.5, 70, -80, 44)
REPLAY = orb([-5.0, 5.9, 0.4], 8.0, 24, -10, 44)    # elevated choice view (apparent vs real route)
CLOSE = HOOK

HOOK_END = 2.80       # B's line ends 2.74 s, A's "lie." 2.10 s; the body ("The") starts at 2.879 s in both tracks
HOOK_REMAP = [[0, S(41)], [0.55, S(45.5)], [1.35, S(49.5)], [HOOK_END, S(52.5)]]   # cut before O1 clears the ball (S054)


def opening(variant):
    lines = ["THIS HANDOFF", "IS A LIE."] if variant == "a" else ["HE SOLD A HANDOFF", "THAT NEVER HAPPENED"]
    return [{"id": "hook", "name": f"HOOK {variant.upper()} (cam HOOK close 3/4, keep S041->S052.5): ball before O2's hip, O1's hands arriving, X2 turns; cut before the ball's owner is resolved",
             "at": 0, "play": "A", "branch": "keep",
             "remap": HOOK_REMAP,
             "camera": [key(0, HOOK), key(HOOK_END, HOOK_IN, "linear")],
             "ov3": [{"type": "spot", "player": "X2", "r": 0.45, "color": RED, "strength": 0.5, "from": 0.55, "to": HOOK_END}],
             "screen": [{"type": "title", "lines": lines, "gold": [1], "from": -0.6, "to": HOOK_END, "y": 252, "size": 76}]}]


def body():
    sh = []
    sh.append({"id": "entry", "name": "ENTRY (cam tracking from the right slot): keep S000->S038, O1 pushes it ahead (S010), O2 catches in front (S029), O1 chases his pass",
               "at": HOOK_END, "play": "A", "branch": "keep",
               "remap": [[0, S(0)], ["pushes", S(10)], ["ahead,>", S(29)], ["Watch-0.03", S(38)]],
               "camera": [key(0, ENTRY0), key("Watch-0.03", ENTRY1, "inOut")],
               "ov3": [{"type": "ballPath", "src": "O1", "dst": "O2", "draw": 0.3, "from": "pushes", "to": "ahead,>"}],
               "screen": []})
    sh.append({"id": "fake", "name": "FAKE (cam lateral from the inside): keep S038->S050, O2 settled on both feet, presents the ball, O1 offers hands; X2's first step inside",
               "at": "Watch-0.03", "play": "A", "branch": "keep",
               "remap": [[0, S(38)], ["hands.", S(45)], ["He bites-0.04", S(50)]],
               "camera": [key(0, FAKE), key("He bites-0.04", FAKE_IN, "linear")],
               "ov3": [{"type": "route", "player": "O1", "t0": S(38), "t1": S(55), "width": 0.06, "draw": 0.5, "from": 0.1, "to": "hands.>"},   # thin, off before the fingers
                       {"type": "spot", "player": "X2", "r": 0.45, "color": RED, "strength": 0.5, "from": "Now", "to": "He bites-0.04"}],
               "screen": []})
    sh.append({"id": "reveal", "name": "REVEAL (cam 3/4 following O2): keep S050->S070, O1 passes empty-handed, O2 pulls the ball back across his body, first bounce, X2 replants",
               "at": "He bites-0.04", "play": "A", "branch": "keep",
               "remap": [[0, S(50)], ["on the handoff.>", S(53.5)], ["keeps it.>", S(60)], ["way.>+0.08", S(70)]],
               "camera": [key(0, REVEAL0), key("way.>+0.08", REVEAL1, "inOut")],
               "ov3": [],
               # a stamp, not a pin: the pin over O2's head sat on O4 in the background (qc-tactical3d pin check)
               "screen": [{"type": "stamp", "text": "STILL HIS BALL", "tone": "gold", "y": 300, "from": "keeps", "to": "way."}]})
    sh.append({"id": "drive", "name": "BASELINE DRIVE (cam 3/4 from the inside of the lane): keep S070->S152, drive, X5 late from the top, gather, layup S110->S124, ball through the rim, landing",
               "at": "way.>+0.08", "play": "A", "branch": "keep",
               "remap": [[0, S(70)], ["baseline.>", S(100)], ["baseline.>+1.3", S(126)], ["baseline.>+2.95", S(152)]],
               "camera": [key(0, DRIVE0), key("baseline.>", DRIVE0), key("baseline.>+1.0", DRIVE1, "inOut"), key("baseline.>+2.95", DRIVE1)],
               "ov3": [{"type": "openSpace", "at": [-4.3, 3.3], "r": 0.5, "rx": 2.1, "angle": 0.65, "from": 0, "to": "baseline."}],   # thin baseline lane strip
               "screen": []})
    sh.append({"id": "replay", "name": "REPLAY (cam elevated): keep S043->S062, the fake again: dashed apparent route (handoff back) vs solid real route (O2 to the baseline)",
               "at": "baseline.>+2.95", "play": "A", "branch": "keep",
               "remap": [[0, S(152)], [0.3, S(43), "inOut"], ["Same-0.1", S(62)]],
               "camera": [key(0, REPLAY), key("Same-0.1", REPLAY)],
               "ov3": [{"type": "route", "player": "O2", "pts": [[-5.55, 6.55], [-4.75, 6.35], [-3.9, 5.95]], "t0": 0, "t1": 1, "dashed": True, "width": 0.09, "draw": 0.4,
                        "color": "#FFFFFF", "from": 0.35, "to": "Same-0.1"},
                       {"type": "route", "player": "O2", "t0": S(54), "t1": S(84), "width": 0.11, "draw": 0.6, "from": 0.8, "to": "Same-0.1"}],
               "screen": [{"type": "rewind", "from": 0, "to": 0.3}]})
    sh.append({"id": "give", "name": "GIVE (cam FAKE, same frame): give S036->S066, X2 keeps the baseline, O2 presents, the real handoff S047->S055, O1 the new owner, first step inside",
               "at": "Same-0.1", "play": "B", "branch": "give",
               "remap": [[0, S(36)], ["shut,>", S(45)], ["back.>", S(56)], ["back.>+0.35", S(64)]],
               "camera": [key(0, FAKE), key("back.>+0.35", FAKE_IN, "linear")],
               "ov3": [{"type": "spot", "player": "X2", "r": 0.45, "color": RED, "strength": 0.45, "from": "If", "to": "shut,>"}],
               "screen": []})
    sh.append({"id": "mirror-keep", "name": "MIRROR KEEP (cam FAKE, same frame and play frames as the give mirror): keep S046->S058",
               "at": "back.>+0.35", "play": "A", "branch": "keep",
               "remap": [[0, S(46)], ["back.>+1.2", S(58)]],
               "camera": [key(0, FAKE)],
               "screen": [{"type": "stamp", "text": "KEEP", "tone": "gold", "y": 300, "from": 0.05, "to": "back.>+1.2"}]})
    sh.append({"id": "mirror-give", "name": "MIRROR GIVE (cam FAKE): give S046->S058",
               "at": "back.>+1.2", "play": "B", "branch": "give",
               "remap": [[0, S(46)], ["That's-0.08", S(58)]],
               "camera": [key(0, FAKE)],
               "screen": [{"type": "stamp", "text": "GIVE", "tone": "white", "y": 300, "from": 0.05, "to": "That's-0.08"}]})
    sh.append({"id": "close", "name": "CLOSE (cam HOOK): back to the decision frame, keep S036->S046 (ends on the hook's opening image); title, question, logo",
               "at": "That's-0.08", "play": "A", "branch": "keep",
               "remap": [[0, S(34)], ["bite?>+2.3", S(41)]],
               "camera": [key(0, CLOSE), key("bite?>+2.3", HOOK)],
               "ov3": [],
               "screen": [{"type": "title", "lines": ["PISTOL", "FAKE HANDOFF"], "gold": [1], "from": "That's", "to": "Would-0.1", "y": 252, "size": 76},
                          {"type": "title", "lines": ["WOULD YOU BITE?"], "gold": [0], "from": "Would-0.1", "to": "bite?>+2.3", "y": 252, "size": 76},
                          {"type": "logo", "from": "bite?>+0.2", "to": "bite?>+2.3"}]})
    return sh


def groups(words):
    """caption units: one sentence per unit, split at a comma when longer than 5"""
    out, cur = [], []
    for w in words:
        cur.append(w["text"])
        if w["text"][-1] in ".?!" or (w["text"].endswith(",") and len(cur) >= 3):
            n = len(cur)
            while n > 6:
                out.append(n // 2); n -= n // 2
            out.append(n); cur = []
    if cur:
        out.append(len(cur))
    return out


def build(variant):
    src = json.load(open(os.path.join(D, "pfh-a.json")))
    ep = {k: v for k, v in src.items() if k not in ("wordsRaw", "gaps", "voiceRaw", "gapFill")}
    eid = f"pfh-main-{variant}"
    ep["id"], ep["title"] = eid, "Pistol Fake Handoff"
    ep["variant"] = f"Hook-{variant.upper()}"
    ep["branches"] = {"keep": "A", "give": "B"}
    ep["voice"] = f"tactical/pfh/voice-{variant}.wav"
    ep["voiceMix"] = f"tactical/pfh/voice-{variant}.mix.wav"
    ep["env"] = "academy"
    ep["shots"] = opening(variant) + body()
    ep["pinV2"] = True
    ep["autoSfx"] = False
    ep["keywords"] = ["handoff", "hands", "defender", "bites", "keeps", "wrong way", "baseline", "Same setup", "lane", "handoff back", "Pistol", "fake handoff", "bite"]
    ep["subtitleHide"] = [[0, "The-0.05"], ["That's-0.3", "bite?>+2.3"]]   # the title cards own the hook and the close
    ep["subtitleY"] = 1350
    words = json.load(open(os.path.join(D, f"pfh-{variant}.words.json")))
    ep["subtitleGroups"] = groups(words)
    ep["subtitleBlock"] = True
    ep["music"] = {"src": "tactical/pfh/music.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, f"pfh-{variant}.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")


if __name__ == "__main__":
    for v in ("a", "b"):
        build(v)
