#!/usr/bin/env python3
"""BLIND PIG: shots on the approved narration (owner brief 2026-11-19, ENCARGO-blind-pig).
Content type: TACTICAL EXPLAINER, but CLARITY > FRAMEWORK: the brief's own structure is used —
contradictory result (hook) -> open loop (rewind, "watch the defender on the right") -> mechanism (deny, flash, sell,
cut, the defender can't see both) -> payoff (bounce pass, layup) -> rehook (rewind, the low defender helps) ->
second payoff (kick-out, three) -> name ("That's Blind Pig.") -> question (deny the pass or protect the rim?).
NO SCREENS anywhere: no screen marker, no "screen" label. The rehook is labelled as OUR read.
Graphic grammar: ONE visual idea at a time and at most THREE tactical overlays on screen at once (3D ov3 items + pins +
HUD chips; checked by scripts/qc-overlays.mts). Gold = offence / the option, coral-red = the defender who decides,
white = neutral (lanes, eyes on the ball, tethers).
  python3 tactical/episodes/_gen-blind-pig-shots.py [v1|v2]   -> blind-pig-main.json (+ words)"""
import copy, json, os, shutil, sys
D = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(D, "blind-pig.json")))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
fol = lambda ids, z=0.9, w=0.5: {"follow": ids, "z": z, "window": w}
GOLD, CORAL, WHITE, RED = "#F2C76A", "#F06A55", "#FFFFFF", "#E5483A"
HIGH = [-0.25, 5.85]
VER = sys.argv[1] if len(sys.argv) > 1 else "v1"

# camera families (yaw 0 = from half court, basket at the top; x < 0 = right of the screen)
HOOK1 = orb(fol(["X2", "O2"], 1.0), 7.4, 56, 160, 44)
HOOK1b = orb(fol(["X2", "O2"], 1.0), 6.8, 55, 166, 44)
HOOK2 = orb(fol(["O2"], 1.1), 7.6, 60, -18, 46)
HOOK2b = orb(fol(["O2"], 1.2), 6.8, 62, -12, 46)
OVER = orb([-1.0, 6.5, 0], 17.5, 30, -25, 42)
OVER_IN = orb([-1.0, 6.3, 0.2], 16.5, 32, -25, 42)
FLASH = orb([-0.9, 6.0, 0.3], 16.0, 34, -20, 42)
DEC = orb([-1.6, 5.8, 0.8], 12.5, 40, -10, 42)
DEC2 = orb([-1.5, 5.5, 0.8], 12.5, 42, -12, 42)
FRZ = orb([-1.8, 6.6, 0.9], 8.8, 46, 8, 42)
FRZ2 = orb([-1.8, 6.6, 0.9], 8.4, 47, 10, 42)
PAY = orb([-0.9, 5.5, 0.5], 13.5, 38, -8, 42)
FIN = orb(fol(["O2"], 1.1), 7.4, 60, -22, 46)
RE = orb([-2.9, 3.5, 0.5], 17.0, 32, -10, 42)
KICK = orb([-3.0, 3.8, 0.6], 13.5, 38, -20, 44)
KICK2 = orb(fol(["O3"], 1.3), 8.6, 58, -40, 44)
TAKE = orb([-0.9, 5.6, 0.2], 17.5, 18, -15, 42)
TAKE2 = orb([-0.9, 5.5, 0.2], 16.8, 20, -15, 42)
CTA = orb([-1.0, 6.4, 0.4], 17.0, 32, -20, 42)


def shots():
    S = []
    # 1a HOOK (contradictory result): inside the denial, close; he took the lane away ------------------------------
    S.append({"id": "hook", "name": "HOOK 1/2: close 3/4 on X2 jumping the passing lane; lock ring + the lane he takes away; DENIED THE PASS.",
      "at": 0, "play": "A",
      "remap": [[0, 0.85], ["pass...>", 1.42], ["@end", 1.5]],
      "camera": [key(0, HOOK1), key("@end", HOOK1b, "inOut")],
      "ov3": [{"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": 0.05, "to": "@end"},
              {"type": "lockRing", "player": "X2", "from": "denied", "to": "@end"}],
      "screen": [{"type": "title", "lines": ["DENIED THE PASS."], "from": 0.05, "to": "@end", "y": 262, "size": 104}]})
    # 1b HOOK: ...and gave up the layup (jump cut forward on a whip) ------------------------------------------------
    S.append({"id": "hook2", "name": "HOOK 2/2: whip forward to the end of the play: the cutter catches behind him and lays it in; GAVE UP THE LAYUP.",
      "at": "and-0.06", "play": "A",
      "remap": [[0, 3.48], ["layup.", 4.2], ["layup.>", 4.6], ["@end", 4.78]],
      "camera": [key(0, HOOK2), key("@end", HOOK2b, "inOut")],
      "ov3": [{"type": "ballTrail", "from": 0, "to": "layup."},
              {"type": "spot", "player": "O2", "r": 0.9, "from": 0.05, "to": "layup.>"},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "layup.>-0.1", "to": "@end"}],
      "screen": [{"type": "whip", "amount": 9, "dir": 1, "from": 0, "to": 0.22},
                 {"type": "flash", "color": "#FFFFFF", "strength": 0.18, "from": 0.0, "to": 0.25},
                 {"type": "title", "lines": ["DENIED THE PASS.", "GAVE UP THE LAYUP."], "gold": [1], "from": 0.02, "to": "@end", "y": 262, "size": 96},
                 {"type": "punch", "amount": 0.03, "from": "layup.>-0.1", "to": "layup.>+0.3"}],
      "sfx": [{"at": 0, "name": "whip", "volume": 0.14}]})
    # 2 OPEN LOOP: rewind to the start, the defender on the right ---------------------------------------------------
    S.append({"id": "loop", "name": "OPEN LOOP: rewind to the start (overview), lock on the defender on the right (X2)",
      "at": "Watch-0.14", "play": "A",
      "remap": [[0, 4.78], [0.45, 0.0, "inOut"], ["right.>", 0.5], ["@end", 0.72]],
      "camera": [key(0, OVER), key("@end", OVER_IN, "linear")],
      "ov3": [{"type": "lockRing", "player": "X2", "from": "defender", "to": "@end"}],
      "screen": [{"type": "rewind", "from": 0, "to": 0.45},
                 {"type": "whip", "amount": 8, "dir": -1, "from": 0, "to": 0.45}],
      "sfx": [{"at": 0, "name": "reverse_cymbal", "volume": 0.12}]})
    # 3 MECHANISM 1: the denial, then the flash (only after the denial exists), the entry --------------------------
    S.append({"id": "deny", "name": "MECHANISM 1: X2 jumps the lane (DENIED pin, lane), then the big flashes (raised arrow, HIGH POST), entry pass travels",
      "at": "He jumps-0.12", "play": "A",
      "remap": [[0, 0.72], ["lane,>", 1.38], ["big", 1.58], ["post.", 2.1], ["@end", 2.26]],
      "camera": [key(0, OVER_IN), key("big", OVER_IN), key("@end", FLASH, "inOut")],
      "ov3": [{"type": "lockRing", "player": "X2", "from": 0, "to": "@end"},
              {"type": "passLane", "src": "O1", "dst": "O2", "color": WHITE, "from": "jumps", "to": "so-0.05"},
              {"type": "arrow3d", "player": "O4", "t0": 1.575, "t1": 2.685, "draw": 0.6, "from": "big", "to": "@end"},
              {"type": "passLane", "src": "O1", "dst": "O4", "dstAt": 2.685, "travel": 0.45, "color": GOLD, "from": "post.-0.05", "to": "@end"}],
      "screen": [{"type": "pin", "player": "X2", "text": "DENIED", "tone": "red", "from": "jumps", "to": "so-0.05", "size": 42},
                 {"type": "pin", "player": "O4", "text": "HIGH POST", "from": "flashes", "to": "post.-0.08", "size": 42}]})
    # 4 MECHANISM 2: the sell, then the backdoor behind X2 ---------------------------------------------------------
    S.append({"id": "cut", "name": "MECHANISM 2: close on the right slot; O2 sells the catch (spot), plants, raised arrow behind X2; tether X2-O2 stretches",
      "at": "The wing-0.12", "play": "A",
      "remap": [[0, 2.24], ["ball...>", 2.36], ["then", 2.4], ["him.>", 2.7], ["@end", 2.72]],
      "camera": [key(0, DEC), key("then", DEC), key("@end", DEC2, "inOut")],
      "ov3": [{"type": "spot", "player": "O2", "r": 0.85, "from": "wing", "to": "then"},
              {"type": "lockRing", "player": "X2", "from": 0, "to": "@end"},
              {"type": "arrow3d", "player": "O2", "t0": 2.52, "t1": 3.78, "consume": True, "draw": 0.45, "from": "cuts-0.05", "to": "@end"},
              {"type": "tether", "a": "X2", "b": "O2", "rest": 1.2, "snap": 2.6, "from": "behind", "to": "@end"}],
      "screen": [{"type": "pin", "player": "O2", "text": "SELLS THE CATCH", "from": "shows", "to": "then-0.05", "size": 40}]})
    # 5 MECHANISM 3: freeze — he can't see both ---------------------------------------------------------------------
    S.append({"id": "freeze", "name": "DECISION FREEZE (TacticalFreezeHUD): X2's two lines of sight, ball (O4) vs man (O2), the angle splits red; CAN'T SEE BOTH",
      "at": "Now-0.1", "play": "A",
      "remap": [[0, 2.72], ["both.>", 2.735], ["@end", 2.74]],
      "camera": [key(0, FRZ), key("@end", FRZ2, "linear")],
      "ov3": [{"type": "vision", "player": "X2", "man": "O2", "split": 95, "len": 3.2, "from": 0.05, "to": "@end"},
              {"type": "lockRing", "player": "X2", "from": 0, "to": "@end"}],
      "screen": [{"type": "freeze", "label": "FREEZE", "from": 0, "to": "@end"},
                 {"type": "focus", "player": "X2", "r": 300, "strength": 0.42, "from": 0, "to": "@end"},
                 {"type": "hud", "tag": "!", "text": "BALL OR MAN?", "from": "defender#2", "to": "@end-0.05"}],
      "sfx": [{"at": 0, "name": "shutter", "volume": 0.14}]})
    # 6 PAYOFF: one pass changed the angle, the next one beats the denial -----------------------------------------
    S.append({"id": "payoff", "name": "PAYOFF: the entry that changed the angle (gold lane), then the bounce pass trajectory into space, in-stride catch, layup, rim, EASY 2",
      "at": "One-0.14", "play": "A",
      "remap": [[0, 2.74], ["next", 3.2], ["beats", 3.37], ["denial.", 3.66], ["denial.>", 3.99], ["@end", 4.75]],
      "camera": [key(0, PAY), key("next", PAY), key("denial.>", FIN, "inOut"), key("@end", FIN)],
      "ov3": [{"type": "passLane", "src": "O1", "dst": HIGH, "color": GOLD, "from": "One", "to": "next-0.05"},
              {"type": "floorText", "text": "NEW ANGLE", "at": [0.75, 6.75], "yaw": 0, "size": 0.62, "plate": True, "from": "changes", "to": "next-0.05"},
              {"type": "ballPath", "src": "O4", "dst": "O2", "draw": 0.4, "from": "next", "to": "denial.>"},
              {"type": "ballTrail", "from": "beats", "to": "denial.>"},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "denial.>+0.5", "to": "@end"}],
      "screen": [{"type": "punch", "amount": 0.025, "from": "denial.>+0.5", "to": "denial.>+0.8"},
                 {"type": "stamp", "text": "LAYUP", "from": "denial.>+0.5", "to": "@end", "y": 400}]})
    # 7 REHOOK: rewind, same action, different read: the low defender helps --------------------------------------
    S.append({"id": "rehook", "name": "REHOOK: fast rewind to the cut (visual), SAME ACTION. / DIFFERENT READ.",
      "at": "denial.>+1.2", "play": "A",
      "remap": [[0, 4.75], ["@end", 2.5, "inOut"]],
      "camera": [key(0, RE), key("@end", RE)],
      "screen": [{"type": "rewind", "from": 0, "to": "@end"},
                 {"type": "whip", "amount": 10, "dir": -1, "from": 0, "to": "@end"},
                 {"type": "title", "lines": ["SAME ACTION.", "DIFFERENT READ."], "gold": [1], "from": 0.12, "to": "@end", "y": 262, "size": 96}],
      "sfx": [{"at": 0, "name": "reverse_cymbal", "volume": 0.12}]})
    S.append({"id": "readB", "name": "READ B: the low defender leaves his shooter (coral spot, tether stretches and snaps), the bounce lane is shut (red X)",
      "at": "But-0.06", "play": "B",
      "remap": [[0, 2.5], ["helps,", 2.98], ["helps,>", 3.45], ["it.>", 3.93], ["@end", 3.96]],
      "camera": [key(0, RE), key("@end", RE)],
      "ov3": [{"type": "spot", "player": "X3", "color": CORAL, "r": 0.9, "from": "low", "to": "don't-0.05"},
              {"type": "tether", "a": "X3", "b": "O3", "rest": 1.6, "snap": 3.3, "from": "low", "to": "@end"},
              {"type": "blocked", "at": [-1.95, 3.15], "from": "force", "to": "@end"}],
      "screen": [{"type": "flash", "color": "#FFFFFF", "strength": 0.2, "from": 0, "to": 0.25},
                 {"type": "title", "lines": ["SAME ACTION.", "DIFFERENT READ."], "gold": [1], "from": 0, "to": "low-0.1", "y": 262, "size": 96},
                 {"type": "hud", "tag": "B", "text": "OUR COUNTER", "from": "don't", "to": "@end"}]})
    # 8 SECOND PAYOFF: kick it out to the shooter he just left ---------------------------------------------------
    S.append({"id": "kick", "name": "SECOND PAYOFF: overhead kick-out trajectory, ghost of X3's spot by the shooter, catch, late closeout, three, OPEN 3",
      "at": "Kick-0.1", "play": "B",
      "remap": [[0, 3.95], ["shooter", 4.5], ["left.", 4.97], ["left.>", 5.32], ["@end", 6.12]],
      "camera": [key(0, KICK), key("left.", KICK2, "inOut"), key("@end", KICK2)],
      "ov3": [{"type": "ballPath", "src": "O4", "dst": "O3", "draw": 0.35, "from": 0.02, "to": "shooter>"},
              {"type": "ghost", "player": "X3", "t": 2.6, "link": True, "from": "shooter", "to": "left.>"},
              {"type": "spot", "player": "O3", "r": 0.9, "from": "shooter", "to": "left.>"},
              {"type": "ballTrail", "from": "left.", "to": "@end"},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "@end-0.22", "to": "@end"}],
      "screen": [{"type": "stamp", "text": "OPEN 3", "from": "@end-0.2", "to": "@end", "y": 400}]})
    # 9 NAME: that's Blind Pig — the whole structure, frozen, from above --------------------------------------------
    S.append({"id": "name", "name": "NAME: high frozen view of read A: flash arrow, entry lane, backdoor arrow; BLIND PIG / DENY - FLASH - BACKDOOR",
      "at": "That's-0.25", "play": "A",
      "remap": [[0, 2.62], ["@end", 2.64]],
      "camera": [key(0, TAKE), key("@end", TAKE2, "linear")],
      "ov3": [{"type": "arrow3d", "player": "O4", "t0": 1.55, "t1": 2.62, "draw": 0.35, "from": 0.05, "to": "@end-0.1"},
              {"type": "passLane", "src": "O1", "dst": "O4", "color": GOLD, "from": 0.25, "to": "@end-0.1"},
              {"type": "arrow3d", "player": "O2", "t0": 2.5, "t1": 3.76, "draw": 0.4, "from": "Blind", "to": "@end-0.1"}],
      "screen": [{"type": "title", "lines": ["BLIND PIG"], "sub": "DENY · FLASH · BACKDOOR", "gold": [0], "from": "Blind-0.05", "to": "@end-0.05", "y": 262, "size": 120}],
      "sfx": [{"at": "Blind", "name": "impact", "volume": 0.14}]})
    # 10 CTA: the defender's choice --------------------------------------------------------------------------------
    S.append({"id": "cta", "name": "CTA: back to the denial, freeze: DENY? on X2 / RIM? at the basket; logo",
      "at": "Deny-0.12", "play": "A",
      "remap": [[0, 1.36], ["@end", 1.4]],
      "camera": [key(0, CTA), key("@end", orb([-1.0, 6.3, 0.4], 16.5, 33, -20, 42), "linear")],
      "ov3": [{"type": "lockRing", "player": "X2", "from": "Deny", "to": "choosing?>"},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 1.0, "strength": 0.7, "from": "protect", "to": "choosing?>"}],
      "screen": [{"type": "freeze", "label": "YOUR CALL", "from": 0, "to": "choosing?>"},
                 {"type": "pin", "player": "X2", "text": "DENY?", "tone": "red", "from": "Deny", "to": "choosing?>", "size": 46},
                 {"type": "scrim", "opacity": 0.6, "from": "choosing?>", "to": "@end"},
                 {"type": "logo", "big": True, "from": "choosing?>", "to": "@end"}]})
    return S


def build(eid="blind-pig-main", tweak=None):
    ep = copy.deepcopy(base)
    ep["id"], ep["title"] = eid, "Blind Pig"
    ep.pop("wordsRaw", None)
    ep["shots"] = shots()
    if tweak:
        tweak(ep)
    ep["pinV2"] = True
    ep["noScreens"] = True          # Blind Pig has no screens: qc-overlays refuses any screen marker or SCREEN label
    ep["autoSfx"] = False            # owner rule: zero ball sounds (no bounces, catches, nets); music has --no-sfx
    ep["keywords"] = ["denied", "layup", "defender", "right", "passing lane", "big", "high post", "wing", "cuts behind him",
                      "can't see both", "One pass", "angle", "beats the denial", "low defender", "helps", "Kick it out", "shooter",
                      "Blind Pig", "protect the rim"]
    ep["subtitleHide"] = [[0, "Watch-0.05"], ["choosing?>", "choosing?>+5"]]
    ep["subtitleY"] = 1330
    ep["music"] = {"src": "tactical/blindpig/music.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "blind-pig.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")


if __name__ == "__main__":
    build()
