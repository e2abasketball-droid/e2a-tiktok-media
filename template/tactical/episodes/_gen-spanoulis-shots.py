#!/usr/bin/env python3
"""SPANOULIS ACTION, three versions on ONE master narration (same voice file, same word timings, same core timeline).
Spain pick-and-roll method: basket at the top, high three-quarter view, gold for offense, red for the deciding defender.
  hook      0 -> "Watch"       DIFFERENT per version (A cinematic push-in / B freeze-frame mystery / C defender POV)
  setup     "Watch what happens before the handoff."           rewind -> starting spots
  reveal    "The guard sets a backscreen ... to the rim."      backscreen + cut (B: more emphasis on the defenders)
  hook2     "But here's what makes the Spanoulis Action ..."   freeze on the guard about to come back
  loop2     "The same guard comes back for the handoff. Now watch his defender."
  readA     "If he trails, attack the gap."                    play A: X2 trails, drive, layup
  readB     "If he goes under, pull up and shoot."             rewind, play B: X2 under, pull-up three
  recapA/B  "Same action. Two completely different answers."   quick replays of both reads
  close     "For more European basketball."                    title + logo, then back to THIS version's first frame (loop)
Usage: python3 tactical/episodes/_gen-spanoulis-shots.py   (writes spanoulis-main / -trial-01 / -trial-02 .json + words)"""
import copy, json, math, os, shutil
D = os.path.dirname(os.path.abspath(__file__))
base = json.load(open(os.path.join(D, "spanoulis.json")))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
RED = "#E5483A"
SCREEN_FACING = round(math.atan2(6.85 - 6.1, 2.85 - 2.75), 3)   # O2 at (2.75, 6.1) faces X4 above him

SET = orb([1.35, 6.6, 0], 16.5, 38, 0, 40)            # whole action: handler, guard, cutter, rim
SET2 = orb([1.7, 6.3, 0], 15.6, 40, 0, 40)
GUARD = orb([3.2, 7.4, 0.8], 10.0, 46, -6, 42)       # hook 2: the guard about to come back
READ_A = orb([2.1, 6.3, 0], 14.0, 42, 6, 42)         # drive from the slot to the rim
RIM_A = orb([0.4, 2.9, 1.2], 6.8, 62, 12, 46)
READ_B = orb([2.2, 7.0, 0], 12.5, 44, -6, 42)        # hand-off, under, pull-up
SHOOT_B = orb([1.9, 7.6, 1.3], 7.4, 60, -30, 46)
TAKE = orb([2.0, 6.2, 0], 15.6, 40, 0, 40)

# ---------------------------------------------------------------- version-specific openings and loops
HOOK_A0 = orb([1.9, 6.6, 0.8], 10.8, 48, -14, 44)   # above and slightly behind the ball handler
HOOK_A1 = orb([1.8, 6.4, 0.8], 9.2, 50, -10, 44)    # subtle push-in
TOP_B = orb([2.55, 5.75, 0], 16.4, 10, 0, 42)          # high, nearly top-down
TOP_B1 = orb([2.55, 5.75, 0], 15.6, 10, 0, 42)
POV0 = {"type": "pov", "behind": "X2", "look": "O2", "back": 2.9, "height": 3.1, "side": 0.5, "fov": 56, "lookZ": 1.0}
POV1 = {"type": "pov", "behind": "X2", "look": "O4", "back": 2.9, "height": 3.1, "side": 0.5, "fov": 56, "lookZ": 1.0}
POV2 = {"type": "pov", "behind": "X2", "look": "O1", "back": 3.0, "height": 3.2, "side": 0.5, "fov": 56, "lookZ": 1.0}

HOOK = {
 "A": {"id": "hook", "name": "Hook A - cinematic: both threats live, gold arrows", "at": 0, "play": "A",
       "remap": [[0, 2.15], ["both.>", 3.7], ["@end", 3.75]],
       "camera": [key(0, HOOK_A0), key("@end", HOOK_A1, "inOut")],
       "ov3": [{"type": "route", "player": "O4", "t0": 2.15, "t1": 2.95, "draw": 0.7, "from": "One", "to": "@end"},
               {"type": "route", "player": "O2", "t0": 2.4, "t1": 4.0, "draw": 0.9, "from": "Two", "to": "@end"},
               {"type": "ring", "player": "O1", "from": 0, "to": "@end"}],
       "screen": [{"type": "title", "lines": ["ONE SCREEN."], "from": 0.05, "to": "Two-0.05", "y": 262, "size": 112},
                  {"type": "title", "lines": ["ONE SCREEN.", "TWO THREATS."], "gold": [1], "from": "Two", "to": "@end", "y": 262, "size": 104}]},
 "B": {"id": "hook", "name": "Hook B - freeze-frame mystery: who would you guard? A or B?", "at": 0, "play": "A",
       "remap": [[0, 3.3], ["@end", 3.3]],
       "camera": [key(0, TOP_B), key("@end", TOP_B1, "linear")],
       "ov3": [{"type": "passLane", "src": "O1", "dst": "O4", "from": "One", "to": "@end"},
               {"type": "passLane", "src": "O1", "dst": "O2", "from": "Two", "to": "@end"},
               {"type": "ring", "player": "O4", "from": "One", "to": "@end", "pulse": True},
               {"type": "ring", "player": "O2", "from": "Two", "to": "@end", "pulse": True}],
       "screen": [{"type": "grade", "from": 0, "to": "@end"},
                  {"type": "title", "lines": ["WHO WOULD", "YOU GUARD?"], "from": 0.05, "to": "Two-0.05", "y": 262, "size": 100},
                  {"type": "title", "lines": ["WHO WOULD", "YOU GUARD?", "A OR B?"], "gold": [2], "from": "Two", "to": "@end", "y": 262, "size": 100},
                  {"type": "pin", "player": "O4", "text": "A ?", "from": "One", "to": "@end", "size": 48},
                  {"type": "pin", "player": "O2", "text": "B ?", "from": "Two", "to": "@end", "size": 48}]},
 "C": {"id": "hook", "name": "Hook C - defender POV: you are X2, the backscreen, the cutter, then the hand-off", "at": 0, "play": "A",
       "remap": [[0, 1.0], ["Two", 2.0], ["both.>", 3.4], ["@end", 3.55]],
       "camera": [key(0, POV0), key("Two", POV1, "inOut"), key("defense", POV1), key("both.>", POV2, "inOut"), key("@end", POV2)],
       "ov3": [{"type": "ring", "player": "O4", "from": "Two", "to": "defense"},
               {"type": "ring", "player": "O2", "from": "both.>", "to": "@end", "pulse": True}],
       "screen": [{"type": "title", "lines": ["YOU HAVE TO"], "from": 0.05, "to": "Two-0.05", "y": 262, "size": 112},
                  {"type": "title", "lines": ["YOU HAVE TO", "DEFEND BOTH."], "gold": [1], "from": "Two", "to": "@end", "y": 262, "size": 104}]},
}
CLOSE_VIS = {   # the last 0.8 s returns to this version's first frame, so the replay is seamless
 "A": {"remap": [[0, 1.5], ["basketball.>+0.5", 2.15], ["@end", 2.15]],
       "camera": [key(0, TAKE), key("basketball.>+0.5", HOOK_A0, "inOut"), key("@end", HOOK_A0)]},
 "B": {"remap": [[0, 2.6], ["basketball.>+0.5", 3.3], ["@end", 3.3]],
       "camera": [key(0, TAKE), key("basketball.>+0.5", TOP_B, "inOut"), key("@end", TOP_B)],
       "ov3": [{"type": "ring", "player": "O4", "from": "basketball.>+0.55", "to": "@end", "pulse": True},
               {"type": "ring", "player": "O2", "from": "basketball.>+0.55", "to": "@end", "pulse": True}],
       "screen": [{"type": "pin", "player": "O4", "text": "A ?", "from": "basketball.>+0.55", "to": "@end", "size": 48},
                  {"type": "pin", "player": "O2", "text": "B ?", "from": "basketball.>+0.55", "to": "@end", "size": 48}]},
 "C": {"remap": [[0, 0.6], ["basketball.>+0.5", 1.0], ["@end", 1.0]],
       "camera": [key(0, POV0), key("@end", POV0)]},
}


def shots(v):
    reveal_ov = [{"type": "screen", "player": "O2", "n": 1, "facing": SCREEN_FACING, "from": "backscreen-0.15", "to": "@end"},
                 {"type": "route", "player": "O4", "t0": 1.6, "t1": 2.95, "trail": True, "from": "sending", "to": "@end"},
                 {"type": "ring", "player": "X4", "from": "backscreen", "to": "@end"}]
    reveal_scr = [{"type": "title", "lines": ["BACKSCREEN"], "gold": [0], "from": "backscreen", "to": "sending-0.05", "y": 262, "size": 104},
                  {"type": "title", "lines": ["BACKSCREEN", "+ CUT TO THE RIM"], "gold": [0], "from": "sending", "to": "@end", "y": 262, "size": 88}]
    if v == "B":   # trial 1: a little more weight on the defenders during the first reveal
        reveal_ov += [{"type": "ring", "player": "X2", "from": "teammate", "to": "@end", "pulse": True},
                      {"type": "route", "player": "X4", "t0": 2.1, "t1": 2.95, "trail": True, "width": 0.14, "color": RED, "from": "sending", "to": "@end"}]
        reveal_scr += [{"type": "pin", "player": "X2", "text": "HELPS", "tone": "red", "from": "straight", "to": "@end"}]
    close = {"id": "close", "name": "CTA + rewatch loop", "at": "For more-0.15", "play": "B" if False else "A",
             "remap": CLOSE_VIS[v]["remap"], "camera": CLOSE_VIS[v]["camera"], "ov3": CLOSE_VIS[v].get("ov3", []),
             "screen": [{"type": "scrim", "opacity": 0.55, "from": 0, "to": "basketball.>+0.45"},
                        {"type": "title", "lines": ["FOR MORE", "EUROPEAN", "BASKETBALL"], "gold": [1, 2], "from": 0.05, "to": "basketball.>+0.45", "y": 560, "size": 132},
                        {"type": "logo", "big": True, "from": "European", "to": "basketball.>+0.45"}]}
    close["screen"] += CLOSE_VIS[v].get("screen", [])
    if v == "B":
        close["screen"] += [{"type": "grade", "from": "basketball.>+0.5", "to": "@end"}]
    return [
     copy.deepcopy(HOOK[v]),
     {"id": "setup", "name": "Loop 1 - rewind to the starting spots", "at": "Watch-0.15", "play": "A",
      "remap": [[0, 0.0], ["happens", 0.0], ["@end", 1.3]],
      "camera": [key(0, SET), key("@end", SET2, "linear")],
      "ov3": [{"type": "ring", "player": "O1", "from": "Watch", "to": "@end"},
              {"type": "ring", "player": "O2", "from": "before", "to": "@end", "pulse": True}],
      "screen": [{"type": "rewind", "from": 0, "to": 0.4}]},
     {"id": "reveal", "name": "Reveal 1 - backscreen, cut to the rim", "at": "The guard-0.15", "play": "A",
      "remap": [[0, 1.3], ["backscreen,>", 1.95], ["rim.>", 2.95], ["@end", 3.05]],
      "camera": [key(0, SET2), key("rim.>", orb([1.5, 5.4, 0], 13.4, 42, 0, 40), "inOut"), key("@end", orb([1.5, 5.4, 0], 13.2, 42, 0, 40))],
      "ov3": reveal_ov, "screen": reveal_scr},
     {"id": "hook2", "name": "Hook 2 - freeze on the guard: Spanoulis Action", "at": "But-0.15", "play": "A",
      "remap": [[0, 3.05], ["here's>+0.3", 3.25], ["@end", 3.25]],
      "camera": [key(0, orb([1.5, 5.4, 0], 13.2, 42, 0, 40)), key("here's>+0.3", GUARD, "inOut"), key("@end", GUARD)],
      "ov3": [{"type": "ring", "player": "O2", "from": "here's", "to": "@end", "pulse": True},
              {"type": "route", "player": "O2", "t0": 3.25, "t1": 4.0, "draw": 0.8, "from": "Spanoulis", "to": "@end"}],
      "screen": [{"type": "freeze", "label": "FREEZE", "from": "here's>+0.3", "to": "@end"},
                 {"type": "title", "lines": ["SPANOULIS ACTION"], "gold": [0], "sub": "Backscreen + dribble handoff", "from": "Spanoulis", "to": "@end", "y": 262, "size": 104}]},
     {"id": "loop2", "name": "Loop 2 - back for the hand-off, now watch his defender", "at": "The same-0.15", "play": "A",
      "remap": [[0, 3.25], ["for the handoff.>", 4.15], ["@end", 4.3]],
      "camera": [key(0, GUARD), key("for the handoff.>", READ_A, "inOut"), key("@end", READ_A)],
      "ov3": [{"type": "route", "player": "O2", "t0": 3.25, "t1": 4.05, "trail": True, "from": "comes back", "to": "@end"},
              {"type": "ring", "player": "O1", "from": "for the handoff", "to": "Now"},
              {"type": "ring", "player": "X2", "color": RED, "from": "Now", "to": "@end", "pulse": True}],
      "screen": [{"type": "title", "lines": ["DRIBBLE HANDOFF"], "gold": [0], "from": "comes back", "to": "@end", "y": 262, "size": 96},
                 {"type": "pin", "player": "X2", "text": "HIS DEFENDER", "tone": "red", "from": "watch his", "to": "@end"}]},
     {"id": "readA", "name": "Read A - he trails: attack the gap", "at": "If he trails-0.15", "play": "A",
      "remap": [[0, 4.3], ["trails,>", 4.7], ["gap.>", 5.45], ["@end", 6.45]],
      "camera": [key(0, READ_A), key("gap.>-0.3", READ_A), key("gap.>+0.9", RIM_A, "inOut"), key("@end", orb([0.4, 2.8, 1.35], 6.3, 64, 12, 46), "linear")],
      "ov3": [{"type": "ring", "player": "X2", "from": "trails", "to": "attack"},
              {"type": "route", "player": "X2", "t0": 4.2, "t1": 5.3, "trail": True, "width": 0.14, "color": RED, "from": "trails", "to": "gap.>+0.4"},
              {"type": "route", "player": "O2", "t0": 4.15, "t1": 5.85, "trail": True, "from": "attack", "to": "@end"},
              {"type": "openSpace", "at": [1.25, 6.3], "r": 1.0, "from": "attack", "to": "gap.>"},
              {"type": "ring", "player": "O2", "from": "gap.>+0.5", "to": "@end", "pulse": True}],
      "screen": [{"type": "pin", "player": "X2", "text": "TRAILS", "tone": "red", "from": "trails", "to": "attack"},
                 {"type": "title", "lines": ["HE TRAILS"], "from": "trails", "to": "gap.>+0.3", "y": 262, "size": 104},
                 {"type": "stamp", "text": "ATTACK THE GAP", "badge": "+2", "from": "gap.>+0.6", "to": "@end", "y": 330}]},
     {"id": "readB", "name": "Read B - rewind, he goes under: pull up and shoot", "at": "If he goes-0.15", "play": "B",
      "remap": [[0, 3.55], ["under,>", 4.35], ["shoot.>", 4.95], ["@end", 6.15]],
      "camera": [key(0, READ_B), key("shoot.>-0.1", READ_B), key("shoot.>+0.45", SHOOT_B, "inOut"), key("@end", orb([1.9, 7.6, 1.4], 6.9, 62, -30, 46), "linear")],
      "ov3": [{"type": "ring", "player": "X2", "from": "goes under", "to": "pull"},
              {"type": "route", "player": "X2", "t0": 3.9, "t1": 4.75, "trail": True, "width": 0.14, "color": RED, "from": "goes under", "to": "shoot.>"},
              {"type": "route", "player": "O2", "t0": 4.0, "t1": 4.88, "trail": True, "from": "pull", "to": "@end"},
              {"type": "separation", "a": "O2", "b": "X2", "from": "pull", "to": "shoot.>+0.3"},
              {"type": "ring", "player": "O2", "from": "shoot.>", "to": "@end", "pulse": True}],
      "screen": [{"type": "rewind", "from": 0, "to": 0.35},
                 {"type": "pin", "player": "X2", "text": "GOES UNDER", "tone": "red", "from": "goes under", "to": "pull"},
                 {"type": "title", "lines": ["HE GOES UNDER"], "from": "goes under", "to": "shoot.>+0.3", "y": 262, "size": 104},
                 {"type": "stamp", "text": "PULL-UP THREE", "badge": "+3", "from": "shoot.>+0.75", "to": "@end", "y": 330}]},
     {"id": "recapA", "name": "Recap - same action (read A replay)", "at": "Same action-0.15", "play": "A",
      "remap": [[0, 4.0], ["@end", 5.6]],
      "camera": [key(0, TAKE), key("@end", orb([1.4, 5.8, 0], 14.2, 40, 0, 40), "linear")],
      "ov3": [{"type": "route", "player": "O2", "t0": 4.0, "t1": 5.85, "draw": 0.7, "from": 0.1, "to": "@end"},
              {"type": "ring", "player": "X2", "from": 0, "to": "@end"}],
      "screen": [{"type": "title", "lines": ["SAME ACTION."], "from": 0.05, "to": "@end", "y": 262, "size": 112},
                 {"type": "pin", "player": "X2", "text": "TRAILS", "tone": "red", "from": 0.1, "to": "@end", "size": 36}]},
     {"id": "recapB", "name": "Recap - two different answers (read B replay + both routes)", "at": "Two completely-0.15", "play": "B",
      "remap": [[0, 4.0], ["answers.>", 5.3], ["@end", 5.6]],
      "camera": [key(0, TAKE), key("@end", orb([1.6, 6.2, 0], 13.8, 40, 0, 40), "linear")],
      "ov3": [{"type": "route", "player": "O2", "fromPlay": "A", "t0": 4.0, "t1": 5.85, "draw": 0.6, "from": 0.1, "to": "@end"},
              {"type": "route", "player": "O2", "t0": 4.0, "t1": 4.88, "draw": 0.6, "color": "#FFFFFF", "from": "completely", "to": "@end"},
              {"type": "ring", "player": "X2", "from": 0, "to": "@end"}],
      "screen": [{"type": "title", "lines": ["SAME ACTION.", "TWO ANSWERS."], "gold": [1], "from": 0.05, "to": "@end", "y": 262, "size": 104},
                 {"type": "pin", "player": "X2", "text": "UNDER", "tone": "red", "from": 0.1, "to": "@end", "size": 36}]},
     close,
    ]


SFX = {"hook": [{"at": 0, "name": "whoosh", "volume": 0.12}, {"at": "Two", "name": "impact", "volume": 0.09}],
       "setup": [{"at": 0, "name": "reverse_cymbal", "volume": 0.12}],
       "reveal": [{"at": "backscreen", "name": "tick", "volume": 0.17}],
       "hook2": [{"at": "here's>+0.3", "name": "impact", "volume": 0.08}],
       "loop2": [{"at": "Now", "name": "tick", "volume": 0.17}],
       "readA": [{"at": "trails", "name": "whip", "volume": 0.1}],
       "readB": [{"at": 0, "name": "whip", "volume": 0.1}],
       "recapA": [{"at": 0, "name": "tick", "volume": 0.17}],
       "recapB": [{"at": 0, "name": "tick", "volume": 0.17}],
       "close": [{"at": 0, "name": "impact", "volume": 0.08}]}
VERSIONS = {"A": "spanoulis-main", "B": "spanoulis-trial-01", "C": "spanoulis-trial-02"}
TITLES = {"A": "Spanoulis Action - A main reel (cinematic tactical reveal)",
          "B": "Spanoulis Action - B trial reel 1 (freeze-frame mystery)",
          "C": "Spanoulis Action - C trial reel 2 (defensive POV)"}
for v, eid in VERSIONS.items():
    ep = copy.deepcopy(base)
    ep["id"], ep["title"], ep["version"] = eid, TITLES[v], v
    ep.pop("wordsRaw", None)
    ep["shots"] = shots(v)
    for sh in ep["shots"]:
        sh["sfx"] = copy.deepcopy(SFX[sh["id"]])
    ep["pinV2"] = True
    ep["musicDrop"] = "If he trails"
    ep["musicPayoff"] = "Same action"
    ep["keywords"] = ["two threats", "backscreen", "Spanoulis Action", "handoff", "his defender", "trails", "attack the gap",
                      "goes under", "pull up and shoot", "two completely different answers"]
    ep["subtitleHide"] = [["For more-0.05", "basketball.>+3"]]
    ep["music"] = {"src": "tactical/spanoulis/music-mix.mp3", "volume": 1}
    json.dump(ep, open(os.path.join(D, f"{eid}.json"), "w"), indent=1, ensure_ascii=False)
    shutil.copyfile(os.path.join(D, "spanoulis.words.json"), os.path.join(D, f"{eid}.words.json"))
    print(eid, len(ep["shots"]), "shots")
