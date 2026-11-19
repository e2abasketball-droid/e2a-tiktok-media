#!/usr/bin/env python3
"""BLIND PIG V2 + Trial B (MASTER-PROMPT-blind-pig.md, 2026-11-19). V1 (_gen-blind-pig*.py) is kept untouched.
  python3 tactical/episodes/_gen-blind-pig-v2.py base     -> blind-pig-v2.json, blind-pig-trialb.json (voice plans)
  python3 scripts/tactical-voice.py tactical/episodes/blind-pig-v2.json   (and blind-pig-trialb.json)
  python3 tactical/episodes/_gen-blind-pig-v2.py shots    -> blind-pig-v2-main.json, blind-pig-trialb-main.json (+ words)
Voice: the main Deuce take is kept (sec. 4: same mechanism, hook, two reads); _splice-blind-pig.py drops
"Now the defender can't see both." and adds "Easy layup." / the Trial B hook from ONE extra short take.
Plays: blindpig2-* = master sec. 5 layout (x mirrored to repo axes: master +x = offence's right = repo -x).
Storyboard = master sec. 10, cameras = sec. 9 (A hook 3/4 low, B/F explanation = the SAME oblique camera, C angle
change, D backdoor diagonal, E finish, G kick-out + shot). At most 3 tactical overlays at once (qc-overlays.mts).
No screens anywhere; read B is labelled as OUR counter. Only SFX: soft whoosh/tick/shutter/reverse cymbal/impact at
the beats listed in sec. 13; NO ball sounds (autoSfx off, music --no-sfx).
Trial B (sec. 19): only the opening changes (hook line + its pictures); everything from "Watch the defender" on is the
same shot list, cameras, music bed and end."""
import copy, json, os, shutil, sys
D = os.path.dirname(os.path.abspath(__file__))
MODE = sys.argv[1] if len(sys.argv) > 1 else "shots"
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
GOLD, CORAL, WHITE, RED = "#F2C76A", "#F06A55", "#FFFFFF", "#E5483A"
HIGH = [-0.2, 5.8]

COMMON_GAPS = [
  {"after": "on the right.", "sec": 0.55, "why": "lock ring + DENIAL land on X2"},
  {"after": "high post.", "sec": 0.75, "why": "O4 arrives at the high post, hands up"},
  {"after": "behind him.", "sec": 0.6, "why": "the cut is on; mini rewind to the entry pass"},
  {"after": "the denial.", "sec": 0.6, "why": "in-stride catch"},
  {"after": "Easy layup.", "sec": 3.3, "why": "the whole action again at REAL SPEED, no graphics (sec. 10)"},
  {"after": "force it.", "sec": 0.5, "why": "the bounce lane is closed (X3 in it)"},
  {"after": "just left.", "sec": 1.9, "why": "catch, shot (overlays off), make, OPEN 3"},
  {"after": "Blind Pig.", "sec": 1.7, "why": "reveal: DENY -> BACKDOOR, then HELP -> KICKOUT"},
  {"after": "Deny the pass...", "sec": 0.35, "why": "DENY OR HELP? lands before 'or protect the rim?'"}]


def base():
    for eid, raw, words, hook_gap in (("blind-pig-v2", "voice-raw-v2.wav", "blind-pig-v2.words-raw.json", {"after": "the layup.", "sec": 0.95, "why": "result stamp, then the rewind (open loop)"}),
                                      ("blind-pig-trialb", "voice-raw-trialb.wav", "blind-pig-trialb.words-raw.json", {"after": "spot it?", "sec": 1.9, "why": "freeze before the cut, then the result"})):
        ep = {"id": eid, "title": "Blind Pig", "fps": 30,
              "voiceRaw": f"tactical/blindpig/{raw}", "wordsRaw": words,
              "voice": f"tactical/blindpig/{eid.replace('blind-pig-', 'voice-')}.wav", "voiceMix": f"tactical/blindpig/{eid.replace('blind-pig-', 'voice-')}.mix.wav",
              "preroll": 0.1, "tail": 1.6, "gaps": [hook_gap] + COMMON_GAPS,
              "plays": {"A": "blindpig2-a-layup", "B": "blindpig2-b-kick"}, "shots": []}
        json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
        print("base", eid)


# cameras (repo axes; yaw 0 = from half court, x < 0 = right of the screen). Probed with scripts/_camprobe.mts + frame-fit.
A_HOOK = orb([-1.7, 3.6, 1.0], 10.5, 60, 30, 46)        # A: low 3/4 down the cut: O2, X2 chasing, ball, rim
A_HOOKb = orb([-1.5, 3.3, 1.0], 9.0, 62, 30, 46)
EXPL = orb([-1.05, 5.6, 0.0], 20.5, 36, -46, 42)          # B = F: oblique high; O1, O2, X2, O4, lane, high post, rim, corner
EXPL_IN = orb([-1.15, 5.7, 0.2], 19.5, 37, -46, 42)
CUTD = orb([-2.2, 5.8, 0.6], 13.0, 42, -80, 42)          # D: diagonal from the ball side: X2's back, O2's path behind him
CUTDb = orb([-2.0, 5.5, 0.6], 12.5, 43, -82, 42)
PAYC = orb([-1.2, 5.4, 0.2], 19.5, 38, -46, 42)          # C: same family as B, pushes from the denied lane to the high post
FINE = orb([-1.2, 2.8, 1.1], 8.5, 62, 30, 46)   # E: lower, rim and ball in frame
FINEb = orb([-1.1, 2.7, 1.1], 8.0, 63, 30, 46)
KICKG = orb([-3.6, 3.6, 0.6], 13.0, 42, -35, 44)         # G1: O4, the help, O3 and the closeout distance
SHOTG = orb([-4.2, 1.8, 1.0], 10.5, 58, 75, 46)          # G2: behind the shooter to the rim (no cut during the release)
TB_HOOK = orb([-1.4, 7.4, 0.9], 13.5, 46, -58, 44)       # Trial B: X2 stepping into the denial, ball in frame
TB_HOOKb = orb([-1.6, 7.2, 0.9], 12.5, 47, -58, 44)


def opening_main():
    return [{"id": "hook", "name": "HOOK (cam A): O2 already behind X2, the pass arrives, micro speed ramp on the catch, layup; DENIED -> LAYUP?",
      "at": 0, "play": "A",
      "remap": [[0, 3.62], ["pass...", 3.88], ["gave", 4.0], ["up", 4.1], ["layup.", 4.62], ["layup.>", 5.1], ["@end", 5.25]],
      "camera": [key(0, A_HOOK), key("layup.", A_HOOKb, "inOut"), key("@end", A_HOOKb)],
      "ov3": [{"type": "lockRing", "player": "X2", "from": 0.05, "to": "@end"},
              {"type": "spot", "player": "O2", "r": 0.95, "from": "and", "to": "layup."},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "layup.>-0.1", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["DENIED.", "LAYUP?"], "gold": [1], "from": 0.0, "to": "@end", "y": 262, "size": 100},
                 {"type": "punch", "amount": 0.03, "from": "layup.>-0.1", "to": "layup.>+0.3"}],
      "sfx": [{"at": 0, "name": "whoosh", "volume": 0.1}, {"at": "layup.>-0.05", "name": "impact", "volume": 0.12}]}]


def opening_trialb():
    return [{"id": "tbhook", "name": "TRIAL B HOOK: X2 steps into the passing lane (ball in frame); freeze right before the cut: ONE MISTAKE. SPOT IT?",
      "at": 0, "play": "A",
      "remap": [[0, 0.75], ["mistake...", 1.45], ["mistake...>", 1.7], ["Can", 2.2], ["spot it?", 2.6], ["spot it?>", 2.62], ["@end", 2.63]],
      "camera": [key(0, TB_HOOK), key("@end", TB_HOOKb, "linear")],
      "ov3": [{"type": "lockRing", "player": "X2", "from": "defender", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["ONE MISTAKE.", "SPOT IT?"], "gold": [1], "from": 0.0, "to": "@end", "y": 262, "size": 100},
                 {"type": "freeze", "label": "FREEZE", "from": "spot it?>", "to": "@end"}],
      "sfx": [{"at": "spot it?>", "name": "shutter", "volume": 0.12}]},
     {"id": "tbresult", "name": "TRIAL B RESULT (cam A): unfreeze, O2 behind X2, catch and layup",
      "at": "spot it?>+0.5", "play": "A",
      "remap": [[0, 3.55], ["@end", 5.2]],
      "camera": [key(0, A_HOOK), key("@end", A_HOOKb, "inOut")],
      "ov3": [{"type": "lockRing", "player": "X2", "from": 0, "to": "@end"},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "@end-0.25", "to": "@end"}],
      "screen": [{"type": "flash", "color": "#FFFFFF", "strength": 0.18, "from": 0.0, "to": 0.25},
                 {"type": "title", "lines": ["DENIED.", "LAYUP."], "gold": [1], "from": 0.0, "to": "@end", "y": 262, "size": 100}],
      "sfx": [{"at": 0, "name": "whoosh", "volume": 0.1}, {"at": "@end-0.3", "name": "impact", "volume": 0.12}]}]


def body(rewind_from):
    S = []
    S.append({"id": "loop", "name": "OPEN LOOP (cam B): rewind to the start, X2 identified (lock ring, focus, DENIAL)",
      "at": "Watch-0.14", "play": "A",
      "remap": [[0, rewind_from], [0.45, 0.3, "inOut"], ["right.>", 0.95], ["@end", 1.1]],
      "camera": [key(0, EXPL), key("@end", EXPL, "linear")],
      "ov3": [{"type": "lockRing", "player": "X2", "from": "defender on", "to": "@end"}],
      "screen": [{"type": "rewind", "from": 0, "to": 0.45},
                 {"type": "focus", "player": "X2", "r": 300, "strength": 0.38, "from": "defender on", "to": "@end"},
                 {"type": "pin", "player": "X2", "text": "DENIAL", "tone": "red", "from": "right.", "to": "@end", "size": 42}],
      "sfx": [{"at": 0, "name": "reverse_cymbal", "volume": 0.11}, {"at": "defender", "name": "tick", "volume": 0.12}]})
    S.append({"id": "deny", "name": "DENIAL + FLASH (cam B): red denied lane, then the gold flash arrow, then HIGH POST (sequential)",
      "at": "He jumps-0.12", "play": "A",
      "remap": [[0, 1.1], ["lane,>", 1.6], ["big", 1.8], ["post.", 2.45], ["@end", 2.5]],
      "camera": [key(0, EXPL), key("big", EXPL), key("@end", EXPL_IN, "inOut")],
      "ov3": [{"type": "lockRing", "player": "X2", "from": 0, "to": "big"},
              {"type": "passLane", "src": "O1", "dst": "O2", "color": RED, "from": "jumps", "to": "post."},
              {"type": "arrow3d", "player": "O4", "t0": 1.75, "t1": 2.97, "draw": 0.6, "from": "big", "to": "@end"}],
      "screen": [{"type": "pin", "player": "X2", "text": "DENIED", "tone": "red", "from": "jumps", "to": "so-0.05", "size": 42},
                 {"type": "pin", "player": "O4", "text": "HIGH POST", "from": "high", "to": "@end", "size": 42}],
      "sfx": [{"at": "flashes", "name": "whoosh", "volume": 0.08}]})
    S.append({"id": "cut", "name": "BACKDOOR (cam D): O2 shows for the ball, very short freeze before the cut, X2's ghost, curved cut behind him",
      "at": "The wing-0.12", "play": "A",
      "remap": [[0, 2.35], ["ball...", 2.6], ["ball...>", 2.62], ["then", 2.64], ["him.>", 3.5], ["@end", 3.55]],
      "camera": [key(0, CUTD), key("then", CUTD), key("@end", CUTDb, "inOut")],
      "ov3": [{"type": "spot", "player": "O2", "r": 0.85, "from": "wing", "to": "ball...>"},
              {"type": "lockRing", "player": "X2", "from": 0, "to": "@end"},
              {"type": "ghost", "player": "X2", "t": 2.62, "link": True, "from": "then", "to": "@end"},
              {"type": "arrow3d", "player": "O2", "t0": 2.83, "t1": 4.06, "consume": True, "draw": 0.45, "from": "ball...>", "to": "@end"}],
      "screen": [{"type": "freeze", "label": "FREEZE", "from": "ball...>", "to": "then"}],
      "sfx": [{"at": "ball...>", "name": "shutter", "volume": 0.1}, {"at": "cuts", "name": "whoosh", "volume": 0.08}]})
    S.append({"id": "payoff", "name": "MECHANISM (cam C): mini rewind; 'One pass' = O1 -> O4 trajectory, 'the next' = O4 -> O2 trajectory",
      "at": "One pass-0.45", "play": "A",
      "remap": [[0, 3.55], [0.3, 2.42, "inOut"], ["One pass", 2.5], ["angle.", 2.99], ["next", 3.5], ["beats", 3.64], ["@end", 4.06]],
      "camera": [key(0, PAYC), key("@end", PAYC)],
      "ov3": [{"type": "ballPath", "src": "O1", "dst": "O4", "draw": 0.4, "from": "One pass", "to": "next-0.05"},
              {"type": "ballPath", "src": "O4", "dst": "O2", "draw": 0.4, "from": "next", "to": "@end"}],
      "screen": [{"type": "rewind", "from": 0, "to": 0.3}],
      "sfx": [{"at": "One pass", "name": "tick", "volume": 0.1}, {"at": "beats", "name": "tick", "volume": 0.12}]})
    S.append({"id": "finish", "name": "PAYOFF (cam E, lower): in-stride catch on the right of the rim, gather, layup, EASY LAYUP",
      "at": "denial.", "play": "A",
      "remap": [[0, 4.06], ["Easy", 4.25], ["Easy layup.", 4.72], ["Easy layup.>", 5.12], ["@end", 5.2]],
      "camera": [key(0, FINE), key("@end", FINEb, "linear")],
      "ov3": [{"type": "spot", "player": "O2", "r": 1.0, "from": 0, "to": "Easy layup."},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "Easy layup.>-0.1", "to": "@end"}],
      "screen": [{"type": "punch", "amount": 0.025, "from": "Easy layup.>-0.1", "to": "Easy layup.>+0.2"},
                 {"type": "stamp", "text": "LAYUP", "from": "Easy layup.>-0.1", "to": "@end", "y": 600}]})
    S.append({"id": "real", "name": "REAL SPEED (cam B): the whole action again at 1x, no graphics but a REAL SPEED chip",
      "at": "Easy layup.>+0.25", "play": "A",
      "remap": [[0, 2.15], ["@end", 5.15]],
      "camera": [key(0, EXPL), key("@end", EXPL_IN, "linear")],
      "screen": [{"type": "hud", "tag": "1×", "text": "REAL SPEED", "from": 0.05, "to": "@end-0.1"}],
      "sfx": [{"at": 0, "name": "whoosh", "volume": 0.08}]})
    S.append({"id": "rehook", "name": "REHOOK (cam F = cam B): back to the moment before the final pass, X3 starts to leave O3: lock ring, HELP, short freeze",
      "at": "But-0.3", "play": "B",
      "remap": [[0, 4.0], [0.3, 3.0, "inOut"], ["low", 3.12], ["helps,", 3.6], ["helps,>", 3.66], ["don't", 3.67], ["force it.>", 4.22], ["@end", 4.24]],
      "camera": [key(0, EXPL), key("@end", EXPL_IN, "linear")],
      "ov3": [{"type": "lockRing", "player": "X3", "from": "low", "to": "@end"},
              {"type": "tether", "a": "X3", "b": "O3", "rest": 1.6, "snap": 3.3, "from": "helps,", "to": "@end"},
              {"type": "blocked", "at": [-1.3, 4.7], "from": "force", "to": "@end"}],
      "screen": [{"type": "rewind", "from": 0, "to": 0.3},
                 {"type": "pin", "player": "X3", "text": "HELP", "tone": "red", "from": "helps,", "to": "force-0.05", "size": 44},
                 {"type": "freeze", "label": "FREEZE", "from": "helps,>", "to": "don't"},
                 {"type": "title", "lines": ["OUR COUNTER"], "gold": [0], "from": "don't", "to": "@end", "y": 262, "size": 84}],
      "sfx": [{"at": 0, "name": "reverse_cymbal", "volume": 0.11}, {"at": "helps,>", "name": "shutter", "volume": 0.1}]})
    S.append({"id": "kick", "name": "KICK-OUT (cam G1): O4 turns to the corner, trajectory to O3, X3's ghost spot + spotlight on the open shooter",
      "at": "Kick-0.1", "play": "B",
      "remap": [[0, 4.22], ["shooter", 4.62], ["left.", 4.97], ["@end", 5.0]],
      "camera": [key(0, KICKG), key("@end", KICKG)],
      "ov3": [{"type": "ballPath", "src": "O4", "dst": "O3", "draw": 0.35, "from": 0.02, "to": "@end"},
              {"type": "ghost", "player": "X3", "t": 3.1, "link": True, "from": "out to", "to": "@end"},
              {"type": "spot", "player": "O3", "r": 0.9, "from": "shooter", "to": "@end"}],
      "screen": [], "sfx": [{"at": "Kick", "name": "whoosh", "volume": 0.08}]})
    S.append({"id": "shot3", "name": "SHOT (cam G2, no cut during the release): catch, feet, rise, release, late closeout, make; overlays off; OPEN 3",
      "at": "left.", "play": "B",
      "remap": [[0, 4.97], ["@end", 6.42]],
      "camera": [key(0, SHOTG), key("@end", SHOTG)],
      "ov3": [{"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "@end-0.45", "to": "@end"}],
      "screen": [{"type": "stamp", "text": "OPEN 3", "from": "@end-0.45", "to": "@end", "y": 760}],
      "sfx": [{"at": "@end-0.5", "name": "bass_hit", "volume": 0.1}]})
    S.append({"id": "nameA", "name": "REVEAL 1/2 (cam B): read A frozen at the catch: backdoor arrow; BLIND PIG / DENY → BACKDOOR",
      "at": "That's-0.25", "play": "A",
      "remap": [[0, 3.95], ["@end", 4.1]],
      "camera": [key(0, EXPL_IN), key("@end", EXPL_IN)],
      "ov3": [{"type": "arrow3d", "player": "O2", "t0": 2.83, "t1": 4.06, "draw": 0.3, "from": 0.05, "to": "@end"}],
      "screen": [{"type": "title", "lines": ["BLIND PIG"], "sub": "DENY? BACKDOOR.", "gold": [0], "from": "Blind-0.05", "to": "@end", "y": 262, "size": 120}],
      "sfx": [{"at": "Blind", "name": "impact", "volume": 0.13}]})
    S.append({"id": "nameB", "name": "REVEAL 2/2 (cam B): read B at the kick-out: trajectory to the corner; BLIND PIG / HELP → KICKOUT",
      "at": "Pig.>+0.55", "play": "B",
      "remap": [[0, 4.5], ["@end", 4.75]],
      "camera": [key(0, EXPL_IN), key("@end", EXPL_IN)],
      "ov3": [{"type": "ballPath", "src": "O4", "dst": "O3", "draw": 0.3, "from": 0.0, "to": "@end"}],
      "screen": [{"type": "title", "lines": ["BLIND PIG"], "sub": "HELP? KICKOUT.", "gold": [0], "from": 0, "to": "@end", "y": 262, "size": 120}],
      "sfx": [{"at": 0, "name": "tick", "volume": 0.1}]})
    S.append({"id": "cta", "name": "CTA (cam B): back to the denial, O4 starts to flash, freeze before the decision: DENY OR HELP?; discreet logo; loops to the hook",
      "at": "Deny-0.12", "play": "A",
      "remap": [[0, 1.45], ["Deny the pass...>", 1.86], ["@end", 1.9]],
      "camera": [key(0, EXPL), key("@end", EXPL_IN, "linear")],
      "ov3": [{"type": "lockRing", "player": "X2", "from": "Deny", "to": "@end"},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 1.0, "strength": 0.7, "from": "protect", "to": "@end"}],
      "screen": [{"type": "freeze", "label": "YOUR CALL", "from": "Deny the pass...>", "to": "@end"},
                 {"type": "title", "lines": ["DENY OR HELP?"], "gold": [0], "from": "Deny", "to": "@end", "y": 300, "size": 96},
                 {"type": "logo", "from": "choosing?", "to": "@end"}],
      "sfx": [{"at": "Deny the pass...>", "name": "shutter", "volume": 0.1}]})
    return S


def groups(words):
    """caption units of 3-7 words: one sentence per unit; a longer sentence is split at its comma / ellipsis, and a piece
    still over 7 words is halved (only "Easy layup." stays a 2-word unit: it is the whole sentence)"""
    sents, cur = [], []
    for w in words:
        cur.append(w["text"])
        if w["text"][-1] in ".?!" and not w["text"].endswith("..."):
            sents.append(cur); cur = []
    if cur:
        sents.append(cur)
    out = []
    for snt in sents:
        pieces, cur = [], []
        for t in snt:
            cur.append(t)
            if (t.endswith(",") or t.endswith("...")) and len(cur) >= 3 and len(snt) > 7:
                pieces.append(cur); cur = []
        if cur:
            pieces.append(cur)
        for pc in pieces:
            n = len(pc)
            while n > 7:
                h = (n + 1) // 2 if n <= 14 else 7
                out.append(h); n -= h
            out.append(n)
    return out


def build(eid, src, opening, rewind_from, hide_until):
    ep = copy.deepcopy(json.load(open(os.path.join(D, f"{src}.json"))))
    ep["id"], ep["title"] = eid, "Blind Pig"
    ep.pop("wordsRaw", None)
    ep["shots"] = opening + body(rewind_from)
    ep["pinV2"] = True
    ep["noScreens"] = True
    ep["autoSfx"] = False
    ep["keywords"] = ["denied", "layup", "defender", "right", "passing lane", "big", "high post", "wing", "cuts behind him",
                      "One pass", "angle", "beats the denial", "Easy layup", "low defender", "helps", "Kick it out", "shooter",
                      "Blind Pig", "protect the rim", "mistake", "spot it"]
    ep["subtitleHide"] = [[0, hide_until], ["left.>", "That's-0.3"], ["choosing?>", "choosing?>+5"]]
    ep["subtitleY"] = 1560
    ep["subtitleGroups"] = groups(json.load(open(os.path.join(D, f"{src}.words.json"))))   # 3-7 word sense units (sec. 12)
    ep["subtitleBlock"] = True     # the unit appears at once: no word-by-word bounce (sec. 11 KineticCaptions)
    ep["subtitleYAt"] = [["Kick-0.1", "left.>", 330]]   # the passer's feet sit low in cam G1: captions go to the top there
    ep["music"] = {"src": "tactical/blindpig/music-v2.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, f"{src}.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")


if __name__ == "__main__":
    if MODE == "base":
        base()
    else:
        build("blind-pig-v2-main", "blind-pig-v2", opening_main(), 5.25, "Watch-0.05")
        build("blind-pig-trialb-main", "blind-pig-trialb", opening_trialb(), 5.2, "Watch-0.05")
