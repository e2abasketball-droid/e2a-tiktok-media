#!/usr/bin/env python3
"""SPAIN PICK & ROLL 2.0: shots on the approved narration (owner brief 2026-11-19, ENCARGO-spain-pnr-2).
Same story as the published original (E2A-TACTICAL-2026-11-15-V02): HOOK -> MECHANISM (ball screen, back screen) ->
DECISION (X2, the back-screener's defender) -> READ A + PAYOFF (pocket pass, easy two) -> VISUAL REHOOK (rewind,
SAME ACTION. DIFFERENT READ.) -> READ B + PAYOFF (pop, open three) -> TAKEAWAY -> CTA. No third read.
Graphic grammar: ONE visual idea at a time. Gold = offence / the option, coral-red = the defender who decides,
white = neutral (pass lanes, tethers). Camera families: OVER (tactical overview), HERO (3/4 hook), DEC (decision,
close on X2), FIN (finish: roll to the rim / pop to the arc).
  python3 tactical/episodes/_gen-spain-pnr-2-shots.py   -> spain-pnr-2-main.json (+ words)"""
import copy, json, os, shutil, sys
D = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(D, "spain-pnr-2.json")))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
fol = lambda ids, z=0.9, w=0.5: {"follow": ids, "z": z, "window": w}
GOLD, CORAL, WHITE, RED = "#F2C76A", "#F06A55", "#FFFFFF", "#E5483A"
FACE5 = 0.7                      # O5's screen angle (tactical/specs/_gen-spain2.py)
FACE2 = 2.21                     # O2's back screen, facing X5

# camera families
HERO0 = orb(fol(["O5", "O1"], 1.0), 8.6, 58, 202, 46)
HERO1 = orb(fol(["O5", "O1", "O2"], 1.0), 9.4, 56, 192, 46)
HERO2 = orb(fol(["O5", "O1", "O2"], 1.0), 7.6, 54, 188, 44)       # push-in on "This is Spain"
OVER = orb([-0.9, 6.6, 0], 13.0, 38, 0, 40)
OVER_IN = orb([-0.9, 6.3, 0.3], 12.0, 40, -6, 40)
SLIDE = orb([-1.0, 5.9, 0.5], 10.8, 44, -24, 42)                  # mini orbit that discovers the back screen
DEC = orb([-0.5, 5.9, 0.9], 9.0, 50, 16, 42)                      # decision camera: X2 + O2 + roller + O1
DEC_W = orb([-0.9, 4.9, 0.7], 10.8, 52, 12, 42)                   # pocket pass: passer, window, roller
FIN_A = orb(fol("O5", 1.2), 7.0, 62, 32, 46)                      # roll to the rim, rim in view
FIN_A2 = orb(fol("O5", 1.5), 6.4, 64, 34, 46)
FIN_B = orb(fol(["O2", "O1"], 1.0), 10.0, 54, -10, 44)             # pop: shooter + passer
FIN_B2 = orb(fol("O2", 1.4), 7.4, 60, -4, 44)                      # push on the shot
TAKE = orb([-0.7, 6.5, 0.2], 15.0, 27, 0, 40)
TAKE2 = orb([-0.6, 6.3, 0.2], 14.0, 29, 0, 40)


def shots():
    S = []
    # 1 HOOK -------------------------------------------------------------------------------------------------
    S.append({"id": "hook", "name": "HOOK: inside the action, hero 3/4. 1 PICK-AND-ROLL; micro-freeze on 'Two screens' with SCREEN 1 then SCREEN 2 pulses; push-in + SPAIN / PICK & ROLL",
      "at": 0, "play": "A",
      "remap": [[0, 0.32], ["Two", 0.88], ["Two>+0.42", 0.88], ["This", 1.02], ["@end", 1.5, "out"]],
      "camera": [key(0, HERO0), key("Two", HERO1, "inOut"), key("This", HERO1), key("@end", HERO2, "inOut")],
      "ov3": [{"type": "spot", "player": "O5", "r": 0.85, "from": "One", "to": "Two-0.02"},
              {"type": "ripple", "player": "O5", "r": 1.5, "from": "Two", "to": "Two>+0.6"},
              {"type": "ring", "player": "O5", "size": 0.9, "from": "Two", "to": "This"},
              {"type": "ripple", "player": "O2", "r": 1.5, "from": "screens.", "to": "screens.>+0.4"},
              {"type": "spot", "player": "O2", "r": 0.85, "from": "screens.", "to": "This"}],
      "screen": [{"type": "title", "lines": ["1 PICK-AND-ROLL"], "from": 0.04, "to": "Two-0.04", "y": 262, "size": 104},
                 {"type": "grade", "from": "Two", "to": "Two>+0.42"},
                 {"type": "flash", "color": "#F2C76A", "strength": 0.22, "from": "Two", "to": "Two>+0.3"},
                 {"type": "punch", "amount": 0.035, "from": "Two", "to": "Two>+0.45"},
                 {"type": "pin", "player": "O5", "text": "SCREEN 1", "from": "Two", "to": "This-0.1", "size": 42},
                 {"type": "pin", "player": "O2", "text": "SCREEN 2", "from": "screens.", "to": "This-0.1", "size": 42},
                 {"type": "whip", "amount": 6, "dir": 1, "from": "This-0.05", "to": "This>+0.2"},
                 {"type": "title", "lines": ["SPAIN", "PICK & ROLL"], "gold": [0], "from": "This", "to": "@end-0.05", "y": 262, "size": 120}],
      "sfx": [{"at": 0, "name": "whoosh", "volume": 0.12}, {"at": "Two", "name": "impact", "volume": 0.32},
              {"at": "screens.", "name": "tick", "volume": 0.22}, {"at": "This-0.05", "name": "whip", "volume": 0.16},
              {"at": "Spain.", "name": "bass_hit", "volume": 0.16}]})
    # 2 MECHANISM: ball screen -------------------------------------------------------------------------------
    S.append({"id": "ballscreen", "name": "MECHANISM 1: tactical overview; O5's arrival arrow, spotlight, BALL SCREEN, contact ripple + screen marker",
      "at": "It-0.1", "play": "A",
      "remap": [[0, 0.12], ["ball screen", 0.7], ["screen>", 0.9], ["top.>", 1.2], ["@end", 1.32]],
      "camera": [key(0, OVER), key("@end", OVER_IN, "linear")],
      "ov3": [{"type": "route", "player": "O5", "t0": 0.12, "t1": 0.86, "draw": 0.55, "width": 0.14, "from": "starts", "to": "top.>"},
              {"type": "spot", "player": "O5", "r": 0.8, "strength": 0.7, "beam": False, "from": "ball", "to": "@end"},
              {"type": "ripple", "player": "O5", "r": 1.4, "from": "screen>-0.1", "to": "screen>+0.6"},
              {"type": "screen", "player": "O5", "n": 1, "facing": FACE5, "from": "screen>-0.1", "to": "@end"}],
      "screen": [{"type": "pin", "player": "O5", "text": "BALL SCREEN", "from": "ball", "to": "@end", "size": 44}],
      "sfx": [{"at": 0, "name": "whoosh", "volume": 0.08}, {"at": "screen>-0.1", "name": "tick", "volume": 0.24}]})
    # 3 MECHANISM: back screen -> the decision ---------------------------------------------------------------
    S.append({"id": "backscreen", "name": "MECHANISM 2: mini orbit discovers the back screen; O2's route to X5, contact + freeze, BACK SCREEN; DROP BIG; then the decision: X2 spotlit, frame dims, READ THE DEFENDER",
      "at": "Then-0.12", "play": "A",
      "remap": [[0, 1.32], ["back screen", 1.5], ["hits", 1.7, "out"], ["hits>+0.24", 1.7], ["drops", 1.78], ["roll.>", 1.85], ["@end", 1.85]],
      "camera": [key(0, OVER_IN), key("hits", SLIDE, "inOut"), key("@end", orb([-1.0, 5.9, 0.6], 10.4, 46, -18, 42), "inOut")],
      "ov3": [{"type": "route", "player": "O2", "t0": 0.2, "t1": 1.7, "draw": 0.55, "width": 0.14, "from": "back screen", "to": "big-0.1"},
              {"type": "ripple", "player": "X5", "r": 1.4, "color": GOLD, "from": "hits-0.05", "to": "hits>+0.6"},
              {"type": "screen", "player": "O2", "n": 2, "facing": FACE2, "from": "hits-0.05", "to": "roll.>"},
              {"type": "ring", "player": "X5", "color": RED, "size": 0.9, "from": "big", "to": "@end"}],
      "screen": [{"type": "punch", "amount": 0.03, "from": "hits-0.05", "to": "hits>+0.35"},
                 {"type": "grade", "from": "hits", "to": "hits>+0.24"},
                 {"type": "pin", "player": "O2", "text": "BACK SCREEN", "from": "hits-0.05", "to": "big-0.1", "size": 44},
                 {"type": "pin", "player": "X5", "text": "DROP BIG", "tone": "red", "from": "big", "to": "@end", "size": 40}],
      "sfx": [{"at": "back screen", "name": "tick", "volume": 0.2}, {"at": "hits-0.05", "name": "impact", "volume": 0.26},
              {"at": "drops", "name": "tick", "volume": 0.12}]})
    # 4 READ A -----------------------------------------------------------------------------------------------
    S.append({"id": "readA", "name": "READ A: X2 stays attached (ghost trail + tether) -> nobody takes the roller (spotlight, OPEN window) -> pocket pass travels -> finish camera, rim flash, EASY 2",
      "at": "roll.>", "play": "A",
      "remap": [[0, 1.85], ["stays", 1.85], ["attached,>", 2.1], ["nobody", 2.12], ["roller.", 2.2], ["roller.>+0.12", 2.22], ["Pocket", 2.3],
                ["pass.>", 3.0], ["Easy", 3.05], ["rim.", 3.62], ["@end", 4.0, "out"]],
      "camera": [key(0, DEC), key("nobody", DEC), key("Pocket", DEC_W, "inOut"), key("pass.>", DEC_W), key("Easy+0.6", FIN_A, "inOut"), key("@end", FIN_A2, "inOut")],
      "ov3": [{"type": "spot", "player": "X2", "color": CORAL, "r": 0.9, "from": 0, "to": "attached,>"},
              {"type": "ghostTrail", "player": "X2", "len": 0.35, "from": "stays", "to": "attached,>+0.15"},
              {"type": "separation", "a": "X2", "b": "O2", "color": WHITE, "from": "stays+0.1", "to": "attached,>"},
              {"type": "spot", "player": "O5", "r": 0.95, "from": "nobody", "to": "Pocket"},
              {"type": "openSpace", "at": [0.6, 3.7], "r": 1.25, "rx": 1.05, "from": "nobody", "to": "Pocket"},
              {"type": "floorText", "text": "OPEN", "at": [0.6, 3.3], "yaw": 16, "size": 0.75, "from": "takes", "to": "Pocket"},
              {"type": "ring", "player": "X5", "color": RED, "size": 0.8, "from": "takes", "to": "Pocket"},
              {"type": "passLane", "src": "O1", "dst": "O5", "dstAt": 3.0, "travel": 0.5, "from": "Pocket", "to": "pass.>+0.15"},
              {"type": "ballTrail", "from": "Pocket", "to": "@end"},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "rim.", "to": "@end"},
              {"type": "ripple", "at": [0, 1.575], "r": 1.3, "from": "rim.", "to": "@end"}],
      "screen": [{"type": "focus", "player": "X2", "r": 230, "strength": 0.5, "from": 0, "to": "attached,>"},
                 {"type": "grade", "from": 0, "to": "stays"},
                 {"type": "hud", "tag": "?", "text": "HE HAS TO CHOOSE", "from": 0.08, "to": "stays-0.05"},
                 {"type": "whip", "amount": 5, "dir": 1, "from": 0, "to": 0.2},
                 {"type": "hud", "tag": "A", "text": "HE STAYS", "from": "stays", "to": "roller.>"},
                 {"type": "grade", "from": "roller.", "to": "roller.>+0.12"},
                 {"type": "punch", "amount": 0.025, "from": "rim.", "to": "rim.>+0.3"},
                 {"type": "stamp", "text": "EASY 2", "from": "rim.", "to": "@end", "y": 400}],
      "sfx": [{"at": 0, "name": "shutter", "volume": 0.2}, {"at": "nobody", "name": "tick", "volume": 0.2}, {"at": "Pocket", "name": "whoosh", "volume": 0.16},
              {"at": "rim.+0.03", "name": "swish", "volume": 0.42}]})
    # 5 VISUAL REHOOK ----------------------------------------------------------------------------------------
    S.append({"id": "rehook", "name": "REHOOK (visual, not narrated): fast rewind back to the decision frame, whip, impact on the return; SAME ACTION. / DIFFERENT READ.",
      "at": "rim.>+0.3", "play": "A",
      "remap": [[0, 4.0], [0.42, 1.85, "inOut"], ["@end", 1.85]],
      "camera": [key(0, orb([-0.5, 5.6, 0.9], 9.6, 52, 22, 42)), key(0.42, DEC, "inOut"), key("@end", DEC)],
      "ov3": [{"type": "spot", "player": "X2", "color": CORAL, "r": 0.9, "from": 0.4, "to": "@end", "fout": 0.001}],
      "screen": [{"type": "rewind", "from": 0, "to": 0.42},
                 {"type": "whip", "amount": 10, "dir": -1, "from": 0, "to": 0.42},
                 {"type": "flash", "color": "#FFFFFF", "strength": 0.25, "from": 0.42, "to": 0.7},
                 {"type": "title", "lines": ["SAME ACTION.", "DIFFERENT READ."], "gold": [1], "from": 0.28, "to": "@end", "y": 262, "size": 96}],
      "sfx": [{"at": 0, "name": "reverse_cymbal", "volume": 0.14}, {"at": 0.02, "name": "whip", "volume": 0.2}, {"at": 0.42, "name": "impact", "volume": 0.22}]})
    # 6 READ B -----------------------------------------------------------------------------------------------
    S.append({"id": "readB", "name": "READ B: same frame; X2 steps up (spotlight, ghost trail, red vector) -> the screener is free (spotlight moves, arc lights) -> POP route grows ahead of O2 -> pass travels, push, shot, swish, OPEN 3",
      "at": "steps-0.15", "play": "B",
      "remap": [[0, 1.85], ["steps", 1.9], ["roller,#2>", 2.28], ["free.", 2.34], ["He pops", 2.4], ["arc.>", 2.95], ["Open", 3.1], ["three.", 3.5],
                ["three.>+0.75", 4.65], ["@end", 4.85, "out"]],
      "camera": [key(0, DEC), key("free.", DEC), key("He pops", FIN_B, "inOut"), key("Open", FIN_B), key("three.", FIN_B2, "inOut"), key("@end", FIN_B2)],
      "ov3": [{"type": "spot", "player": "X2", "color": CORAL, "r": 0.9, "from": 0, "to": "free.", "fin": 0.001},
              {"type": "ghostTrail", "player": "X2", "len": 0.4, "from": "steps", "to": "free.>"},
              {"type": "route", "player": "X2", "t0": 1.85, "t1": 2.6, "trail": True, "color": RED, "width": 0.13, "from": "steps", "to": "free."},
              {"type": "ring", "player": "O5", "size": 0.8, "from": "stop#2", "to": "free."},
              {"type": "spot", "player": "O2", "r": 0.95, "from": "free.", "to": "arc.>"},
              {"type": "glow", "at": [0.2, 8.8], "r": 1.5, "strength": 0.55, "from": "free.", "to": "Open"},
              {"type": "route", "player": "O2", "t0": 2.05, "t1": 3.2, "consume": True, "draw": 0.45, "width": 0.17, "from": "He pops", "to": "Open"},
              {"type": "passLane", "src": "O1", "dst": "O2", "dstAt": 3.2, "travel": 0.55, "from": "arc.-0.2", "to": "Open>"},
              {"type": "ballTrail", "from": "arc.", "to": "@end"},
              {"type": "glow", "at": [0, 1.575], "hoop": True, "r": 0.8, "strength": 0.8, "from": "three.>+0.75", "to": "@end"}],
      "screen": [{"type": "focus", "player": "X2", "r": 230, "strength": 0.5, "from": 0, "to": "roller,#2>"},
                 {"type": "hud", "tag": "B", "text": "HE STEPS UP", "from": "steps", "to": "free."},
                 {"type": "pin", "player": "O2", "text": "POP", "from": "pops", "to": "arc.>", "size": 46},
                 {"type": "punch", "amount": 0.03, "from": "three.", "to": "three.>+0.4"},
                 {"type": "stamp", "text": "OPEN 3", "from": "three.", "to": "@end", "y": 400}],
      "sfx": [{"at": "steps", "name": "whoosh", "volume": 0.14}, {"at": "free.", "name": "tick", "volume": 0.2},
              {"at": "pops", "name": "whoosh", "volume": 0.12}, {"at": "three.>+0.78", "name": "swish", "volume": 0.42},
              {"at": "three.>+0.78", "name": "impact", "volume": 0.18}]})
    # 7 TAKEAWAY ---------------------------------------------------------------------------------------------
    S.append({"id": "takeaway", "name": "TAKEAWAY: elevated, frozen structure: SCREEN 1 + SCREEN 2 (hierarchy, thin link) -> the trapped defender (ONE DEFENDER. TWO PROBLEMS.) -> two ghost routes, two endpoints (EASY 2 / OPEN 3)",
      "at": "Two#3-0.15", "play": "A",
      "remap": [[0, 1.72], ["@end", 1.8]],
      "camera": [key(0, TAKE), key("@end", TAKE2, "linear")],
      "ov3": [{"type": "screen", "player": "O5", "n": 1, "facing": FACE5, "from": "Two#3", "to": "One#2"},
              {"type": "screen", "player": "O2", "n": 2, "facing": FACE2, "from": "screens.#2-0.1", "to": "One#2"},
              {"type": "floorText", "text": "1", "player": "O5", "offset": [1.0, -0.5], "yaw": 0, "size": 0.8, "plate": True, "from": "Two#3", "to": "One#2"},
              {"type": "floorText", "text": "2", "player": "O2", "offset": [-1.1, 0.0], "yaw": 0, "size": 0.8, "plate": True, "from": "screens.#2-0.1", "to": "One#2"},
              {"type": "separation", "a": "O5", "b": "O2", "color": WHITE, "from": "screens.#2>", "to": "One#2"},
              {"type": "spot", "player": "X2", "color": CORAL, "r": 1.0, "from": "One#2", "to": "@end-0.15"},
              {"type": "route", "player": "O5", "fromPlay": "A", "t0": 1.85, "t1": 3.0, "draw": 0.5, "width": 0.16, "from": "defence", "to": "@end-0.1"},
              {"type": "route", "player": "O2", "fromPlay": "B", "t0": 2.05, "t1": 3.2, "draw": 0.5, "width": 0.16, "color": WHITE, "from": "defence+0.15", "to": "@end-0.1"},
              {"type": "floorText", "text": "EASY 2", "at": [0.4, 1.7], "yaw": 0, "size": 0.8, "plate": True, "from": "give", "to": "@end-0.1"},
              {"type": "floorText", "text": "OPEN 3", "at": [-1.35, 7.75], "yaw": 0, "size": 0.7, "plate": True, "color": WHITE, "from": "something", "to": "@end-0.1"}],
      "screen": [{"type": "focus", "player": "X2", "r": 260, "strength": 0.42, "from": "One#2", "to": "defence"},
                 {"type": "title", "lines": ["ONE DEFENDER.", "TWO PROBLEMS."], "gold": [1], "from": "One#2", "to": "defence-0.08", "y": 262, "size": 100}],
      "sfx": [{"at": "Two#3", "name": "impact", "volume": 0.18}, {"at": "One#2", "name": "tick", "volume": 0.2}, {"at": "defence", "name": "whoosh", "volume": 0.12}]})
    # 8 CTA --------------------------------------------------------------------------------------------------
    S.append({"id": "cta", "name": "CTA: back to the decision, freeze: the defender selected, ROLL? / POP? (two options only); logo",
      "at": "How-0.12", "play": "B",
      "remap": [[0, 1.86], ["@end", 1.88]],
      "camera": [key(0, DEC), key("@end", orb([-0.5, 5.9, 0.9], 9.8, 48, 14, 42), "linear")],
      "ov3": [{"type": "spot", "player": "X2", "color": CORAL, "r": 0.95, "from": 0, "to": "Follow"},
              {"type": "route", "player": "O5", "fromPlay": "A", "t0": 1.86, "t1": 2.7, "draw": 0.4, "width": 0.13, "dashed": True, "from": "guarding", "to": "Follow"},
              {"type": "route", "player": "O2", "fromPlay": "B", "t0": 2.05, "t1": 2.9, "draw": 0.4, "width": 0.13, "dashed": True, "color": WHITE, "from": "guarding+0.1", "to": "Follow"}],
      "screen": [{"type": "freeze", "label": "YOUR CALL", "from": 0, "to": "Follow"},
                 {"type": "pin", "player": "O5", "text": "ROLL?", "from": "guarding", "to": "Follow", "size": 46},
                 {"type": "pin", "player": "O2", "text": "POP?", "tone": "white", "from": "guarding+0.1", "to": "Follow", "size": 46},
                 {"type": "scrim", "opacity": 0.6, "from": "Follow", "to": "@end"},
                 {"type": "logo", "big": True, "from": "Follow", "to": "@end"}],
      "sfx": [{"at": 0, "name": "shutter", "volume": 0.16}, {"at": "Follow", "name": "whoosh", "volume": 0.12}]})
    return S


def build(eid="spain-pnr-2-main", tweak=None):
    ep = copy.deepcopy(base)
    ep["id"], ep["title"] = eid, "Spain Pick & Roll 2.0"
    ep.pop("wordsRaw", None)
    ep["shots"] = shots()
    if tweak:
        tweak(ep)
    ep["pinV2"] = True
    ep["autoSfx"] = False            # zero ball sounds (owner rule): bounces/catches never; swish placed by hand on the makes
    ep["keywords"] = ["pick-and-roll", "two screens", "Spain", "ball screen", "back screen", "big", "roller", "attached", "Pocket pass",
                      "Easy two", "steps up", "free", "pops", "Open three", "One defender", "give something up"]
    ep["subtitleHide"] = [[0, "It-0.05"], ["Follow-0.05", "basketball.>+2"]]
    ep["subtitleY"] = 1330
    ep["music"] = {"src": "tactical/spain2/music.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "spain-pnr-2.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")


if __name__ == "__main__":
    build()
