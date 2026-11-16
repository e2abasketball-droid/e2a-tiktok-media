#!/usr/bin/env python3
"""VEER ACTION edit (owner brief 2026-11-16 03:27Z), anchored to the real narration (veer-action.words.json) and to play
time. Style reference: the Spain pick-and-roll reel (most viral E2A video, 1.28 M IG views): short top title per beat,
3/4 high tactical camera with the rim at the top, red rings/labels on the defender who decides, gold routes on the
offence, slow motion only on the decision, CTA over the moving play. Every read uses ONE camera family (yaw -20, high
3/4) so the viewer compares the same picture.
  hook    0-2.04    play A: the kick-out already in the air -> cut on the catch.            WHO GOT HIM OPEN?
  loop1   2.04-4.83 back to the start of the possession, same family of frame: the big (gold ring) walks up and sets
                    the ball screen; the shooter waits low on the veer side.
  dev     4.83-8.89 guard tight off the ball screen, attacks the lane; X2's real help step (short red arrow) HELP STEP
  resp1   8.89-14.73 the big turns (gold route follows him), plants the down screen (VEER ACTION), the shooter comes off
                    shoulder to shoulder (second gold route), kick-out in the EXACT hook frame, then the three.
  hook2   14.73-18.96 play B, just before the second screen: X2 stays attached and trails (red ring) HE CHASES...
                    hold on the plant foot so the viewer can anticipate the pass.
  resp2   18.96-23.91 the curl tight around the big (CURL INSIDE), lead pass, catch in stride, layup, net.
  cmpA    23.91-26.09 play A from the second screen, same frame.   HELP -> KICK-OUT
  cmpB    26.09-28.95 play B from the second screen, same frame.   CHASE -> CURL
  cta     28.95-end  play A back toward the opening pass; the last frame is the frame before the hook's first one."""
import json, os
D = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(D, "veer-action.json")
ep = json.load(open(P))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED, GOLD = "#E5483A", "#C9A24D"
T = lambda lines, frm, to, gold=(0,), **k: {"type": "title", "lines": lines, "gold": list(gold), "from": frm, "to": to, "y": 252, "size": 100, **k}
SETUP = orb([-1.88, 6.02, 0.6], 17.5, 56, -10)     # basket at the top (Spain reel look): guard, big, shooter, rim
VEERMID = orb([-2.63, 5.88, 0.6], 16.5, 56, -10)
READ = orb([-3.2, 4.4, 0.6], 15.7, 56, 5)           # the read frame: ball, big, shooter, his defender and the rim
HOOK = orb([-3.61, 6.91, 0.6], 11.5, 56, 10)         # the opening pass, tight
THREE = orb([-2.95, 4.68, 0.6], 15.75, 56, 0)       # back out after the release: shooter, flight and rim
FINISH = orb([-2.76, 3.93, 0.6], 15.5, 56, 0)
CTA = orb([-2.39, 4.61, 0.6], 15.0, 56, -10)

shots = [
 {"id": "hook", "name": "Hook - the kick-out already in the air, cut on the catch", "at": 0, "play": "A",
  "remap": [[0, 5.03], [1.3, 5.33], ["@end", "catch"]],
  "camera": [key(0, HOOK)],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "size": 0.75, "from": 0.35, "to": "@end"}],
  "screen": [T(["WHO GOT", "HIM OPEN?"], 0, "@end", gold=(1,), size=110)]},
 {"id": "loop1", "name": "Loop 1 - back to the start: the big walks up and screens, the shooter waits low", "at": "Watch-0.3", "play": "A",
  "remap": [[0, 0.0], [0.75, 0.0], ["@end", "screen1", "in"]],
  "camera": [key(0, SETUP)],
  "ov3": [{"type": "ring", "player": "O5", "color": GOLD, "pulse": True, "from": "big-0.1", "to": "@end"}],
  "screen": [{"type": "pin", "player": "O5", "text": "THE BIG", "tone": "gold", "from": "big-0.1", "to": "pick.>", "size": 42},
             {"type": "pin", "player": "O2", "text": "SHOOTER", "tone": "white", "from": "after", "to": "@end", "size": 38}]},
 {"id": "dev", "name": "Development - tight off the ball screen, the corner defender's help step", "at": "He-0.1", "play": "A",
  "remap": [[0, "screen1"], ["guard.>", 1.55], ["help", 2.05], ["help.>", 2.25], ["@end", 2.45]],
  "camera": [key(0, SETUP)],
  "ov3": [{"type": "screen", "player": "O5", "n": 1, "facing": 0.6, "from": 0, "to": "guard.>"},
          {"type": "route", "player": "X2", "t0": 1.5, "t1": 2.2, "trail": True, "color": RED, "width": 0.16, "from": "corner", "to": "@end"},
          {"type": "ring", "player": "X2", "color": RED, "from": "corner", "to": "@end"}],
  "screen": [{"type": "pin", "player": "X2", "text": "HELP STEP", "tone": "red", "from": "steps", "to": "@end", "size": 42}]},
 {"id": "resp1", "name": "Answer 1 - the big turns and plants the veer screen, shoulder to shoulder, kick-out three", "at": "The big TURNS-0.2", "play": "A",
  "remap": [[0, 2.45], ["TURNS", 2.7], ["screens him.>", "set"], ["That's", "go"], ["Veer.>", 5.2], ["@end", 7.15]],
  "camera": [key(0, SETUP), key("TURNS+0.2", VEERMID, "inOut"), key("screens him.>-0.2", READ, "inOut"), key("Veer.>-0.25", READ), key("Veer.>+0.15", HOOK, "inOut"), key("Veer.>+0.85", HOOK), key("@end-0.8", THREE, "inOut")],
  "ov3": [{"type": "route", "player": "O5", "t0": 2.4, "t1": 4.17, "trail": True, "color": GOLD, "from": "TURNS-0.15", "to": "That's"},
          {"type": "screen", "player": "O5", "n": 2, "facing": 2.6, "from": "screens him.>-0.15", "to": "Veer.>"},
          {"type": "route", "player": "O2", "t0": 4.29, "t1": 5.6, "trail": True, "color": GOLD, "from": "That's", "to": "Veer.>+0.2"}],
  "screen": [T(["VEER ACTION"], "screens him.>-0.15", "Veer.>+0.1", size=112)]},
 {"id": "hook2", "name": "Hook 2 - same spot, he chases: hold on the plant foot", "at": "Now-0.2", "play": "B",
  "remap": [[0, 3.85], ["chases", 4.3], ["going?>", "plant"], ["@end", 5.4]],
  "camera": [key(0, READ)],
  "ov3": [{"type": "screen", "player": "O5", "n": 2, "facing": 2.6, "from": 0.3, "to": "@end"},
          {"type": "ring", "player": "X2", "color": RED, "pulse": True, "from": "chases-0.3", "to": "@end"}],
  "screen": [T(["HE CHASES…"], "chases-0.1", "@end", size=104),
             {"type": "pin", "player": "X2", "text": "ON HIS BACK", "tone": "red", "from": "Where's", "to": "@end", "size": 38}]},
 {"id": "resp2", "name": "Answer 2 - the curl, the pass in front of him, catch in stride, layup", "at": "He curls-0.15", "play": "B",
  "remap": [[0, 5.4], ["inside.>", 5.75], ["hits", "pass"], ["stride.>", 6.45], ["@end", 7.85]],
  "camera": [key(0, READ), key("hits", READ), key("stride.>", FINISH, "inOut"), key("@end", FINISH)],
  "ov3": [{"type": "route", "player": "O2", "t0": 5.3, "t1": 6.6, "trail": True, "color": GOLD, "from": "curls-0.1", "to": "stride.>"}],
  "screen": [{"type": "pin", "player": "O2", "text": "CURL INSIDE", "tone": "gold", "from": "curls-0.1", "to": "hits-0.1", "size": 42}]},
 {"id": "cmpA", "name": "Compare A - from the second screen: he helps, kick it out", "at": "Help? Kick-0.25", "play": "A",
  "remap": [[0, 4.1], ["@end", 6.15]],
  "camera": [key(0, READ)],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"},
          {"type": "route", "player": "O2", "t0": 4.29, "t1": 5.6, "trail": True, "color": GOLD, "from": 0, "to": "@end"}],
  "screen": [T(["HELP → KICK-OUT"], 0.05, "@end", gold=(0,), size=96)]},
 {"id": "cmpB", "name": "Compare B - from the second screen: he chases, hit the curl", "at": "Chase?-0.3", "play": "B",
  "remap": [[0, 4.1], ["@end", 6.75]],
  "camera": [key(0, READ)],
  "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"},
          {"type": "route", "player": "O2", "t0": 4.29, "t1": 6.6, "trail": True, "color": GOLD, "from": 0, "to": "@end"}],
  "screen": [T(["CHASE → CURL"], 0.05, "@end", gold=(0,), size=96)]},
 {"id": "cta", "name": "CTA - over the play, back to the opening pass, last frame before the hook's first", "at": "For more-0.3", "play": "A",
  "remap": [[0, 3.3], [2.61, 4.8], ["@end", 5.03]],
  "camera": [key(0, CTA), key(1.6, CTA), key(2.61, HOOK, "inOut"), key("@end", HOOK)],
  "ov3": [],
  "screen": [T(["FOR MORE", "EUROPEAN BASKETBALL"], 0.2, "@end-0.25", gold=(1,), size=92),
             {"type": "logo", "big": False, "from": 0.6, "to": "@end-0.25"}]},
]
SFX = {"hook": [{"at": 1.95, "name": "bounce", "volume": 0.09}],
       "loop1": [{"at": 0, "name": "whoosh", "volume": 0.08}],
       "dev": [{"at": 0.35, "name": "bounce", "volume": 0.07}, {"at": "steps", "name": "squeak", "volume": 0.11}],
       "resp1": [{"at": "TURNS", "name": "squeak", "volume": 0.13}, {"at": "screens him.>-0.15", "name": "impact_big", "volume": 0.16},
                 {"at": "Veer.>+0.55", "name": "bounce", "volume": 0.07}, {"at": "@end-0.35", "name": "swish", "volume": 0.17}],
       "hook2": [{"at": "going?>", "name": "squeak", "volume": 0.12}],
       "resp2": [{"at": "hits", "name": "bounce", "volume": 0.07}, {"at": "@end-0.45", "name": "swish", "volume": 0.16}],
       "cmpA": [{"at": 0, "name": "whoosh", "volume": 0.06}],
       "cmpB": [{"at": 0, "name": "whoosh", "volume": 0.06}],
       "cta": []}
for sh in shots:
    sh["sfx"] = SFX.get(sh["id"], [])
ep["shots"] = shots
ep["keywords"] = ["big", "pick", "guard", "corner defender", "help", "TURNS", "screens him", "Veer", "watch", "chases", "pass going",
                  "curls inside", "hits him", "stride", "Kick it out", "Hit the curl", "European"]
ep["subtitleGroups"] = [5, 3, 3, 2, 3, 3, 4, 3, 3, 3, 2, 2, 3, 4, 3, 4, 2, 4, 4, 4]
ep["subtitleBlock"] = True
ep["subtitleHide"] = [[0, "open?>+0.2"], ["For more-0.3", 40]]
ep["subtitleY"] = 1400
ep["gradeBottom"] = 0.38
ep["autoSfx"] = False
ep["ambience"] = {"src": "sfx/arena.mp3", "volume": 0.05}
ep["music"] = {"src": "tactical/veer/music-mix.mp3", "volume": 1}
json.dump(ep, open(P, "w"), indent=1, ensure_ascii=False)
print("shots", len(shots), "words", sum(ep["subtitleGroups"]))
