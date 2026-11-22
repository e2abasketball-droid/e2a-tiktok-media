#!/usr/bin/env python3
"""CHICAGO ACTION V3 reel (owner master brief 432aece7-E2A_CHICAGO_ACTION_V3_MASTER_NO_ELEVENLABS.md, 2026-11-22).
AUDIO-LOCKED RE-EDIT: the V2 narration and music are reused BYTE-FOR-BYTE (no TTS, no transcription, no ElevenLabs call):
  voice  public/tactical/chicago-v2/voice.wav      (Deuce take of 2026-11-21, gaps by scripts/tactical-voice.py)
  mix    public/tactical/chicago-v2/voice.mix.wav  (its EQ/compressed mix, 38.0 s)
  music  public/tactical/chicago-v2/music.mp3      (E2A in-house synth bed, no samples, no ball sounds)
  words  tactical/episodes/chicago-action-v2.words.json (Scribe timings of 2026-11-21, already paid; reused, not re-run)
The episode carries `audioReuseOnly` + `disallowTTS` + `audioLock` (sha256 of every audio input): scripts/test-audio-lock.mjs
fails if a file changes or if any V3 pipeline script references a TTS / ElevenLabs endpoint, and tactical-voice.py refuses
to run on an episode with disallowTTS. Plays: tactical/plays/chicago-v3-{trail-drive,under-three}.json (realism 3).
  python3 tactical/specs/_gen-chicago-v3.py            -> plays
  python3 tactical/episodes/_gen-chicago-v3.py         -> chicago-action-v3.json (+ .words.json)
  node scripts/tactical-props.mjs tactical/episodes/chicago-action-v3.json out/blob/chicago-action-v3.props.json
Storyboard (brief sec. 6, slid to the real word anchors): A hook = split screen TRAIL -> DRIVE (layup) over UNDER -> THREE
(make) | B watch the defender (elevated 3/4) | C pin-down, ONE continuous medium-wide 3/4 (no legs-only close-up) | D
hand-off, ONE continuous low 3/4 medium-wide (hands, ball, feet) | E TRAIL -> DRIVE (chase cam, layup through the net) |
F SAME SETUP -> UNDER -> THREE (gap wedge, make) | G recap: pin-down -> DHO (same angle) -> split payoffs | H CTA: moving
split replay, X2's two routes | I outro: slow orbit on the net + logo. Repo axes: x = -brief x; orbit yaw 0 = camera on
the half-court side (basket at the top), pitch from vertical."""
import hashlib, json, os, sys
D = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(os.path.dirname(D))
orb = lambda tg, dist, pitch, yaw, fov=42: {"type": "orbit", "target": tg, "dist": dist, "pitch": pitch, "yaw": yaw, "fov": fov}
fol = lambda ids, z=1.0, **k: {"follow": ids, "z": z, **k}
key = lambda at, rig, ease=None: {"at": at, "rig": rig, **({"ease": ease} if ease else {})}
EID = "chicago-action-v3"
RED, GOLD, BLUE, WHITE = "#E5483A", "#FFC447", "#6EA8FF", "#FFFFFF"
AUDIO = {"voice": "tactical/chicago-v2/voice.wav", "voiceMix": "tactical/chicago-v2/voice.mix.wav", "music": "tactical/chicago-v2/music.mp3"}
WORDS_SRC = "chicago-action-v2.words.json"
SEAM_Y = 905          # captions sit on the seam of the split screen (between the two outcomes)

# ---- cameras (play metres; rim (0, 1.575, 3.05))
DRV_TOP0 = orb(fol(["O2"], 1.0, window=0.5), 7.8, 62, 14, 40)          # split top: drive lane from behind O2, rim in frame
DRV_TOP1 = orb([-0.45, 3.0, 1.6], 7.2, 64, 20, 40)
THR_BOT0 = orb([-2.3, 7.3, 1.4], 8.2, 64, 70, 40)          # split bottom: shooter behind the arc + rim, oblique
THR_BOT1 = orb([-1.35, 5.1, 2.0], 10.4, 66, 60, 40)
WATCH0 = orb([-2.4, 6.3, 0.9], 13.5, 46, -36, 42)              # elevated 3/4 (pitch 48 from vertical): the decision trio
WATCH1 = orb([-3.9, 5.0, 0.9], 10.5, 52, 8, 42)
PD0 = orb([-4.45, 4.7, 1.0], 9.4, 70, 74, 40)                 # pin-down: court-level 3/4, medium-wide, full bodies
PD1 = orb([-4.2, 6.2, 1.0], 9.8, 68, 62, 40)
HO0 = orb([-2.95, 8.25, 1.0], 7.4, 74, 150, 40)               # hand-off: low 3/4, medium-wide (hands, ball, feet)
HO1 = orb([-2.8, 8.2, 1.0], 7.0, 74, 146, 40)
CHASE0 = orb(fol(["O2"], 1.1, window=0.6), 9.2, 60, 16, 42)    # TRAIL -> DRIVE: behind O2, rim ahead
CHASE1 = orb([-0.55, 3.4, 1.5], 8.6, 63, 22, 42)
UND0 = orb([-3.7, 4.6, 1.0], 12.0, 60, 58, 42)                # UNDER -> THREE: elevated sideline oblique
UND1 = orb([-2.55, 7.9, 1.2], 11.0, 62, 54, 42)
UND2 = orb([-1.75, 6.3, 1.9], 11.4, 64, 52, 42)
RC0 = orb([-3.9, 6.1, 1.0], 12.5, 62, 60, 42)                 # recap: one 3/4 angle for pin-down AND hand-off
RC1 = orb([-3.3, 7.4, 1.0], 11.0, 64, 64, 42)
NET0 = orb([0.0, 1.575, 2.55], 4.2, 74, 25, 44)               # outro: slow orbit round the net
NET1 = orb([0.0, 1.575, 2.6], 4.0, 76, 62, 44)


def lane():
    """the TRAIL lane: floor channel from O2's outside hip after the hand-off to the rim (elongated ellipse)"""
    return {"type": "openSpace", "at": [-1.2, 5.7], "r": 0.55, "rx": 2.3, "angle": -1.42, "color": GOLD}


def gap():
    """the UNDER gap: floor wedge between X2 (under the hand-off) and O2 behind the arc"""
    return {"type": "openSpace", "at": [-2.95, 8.05], "r": 0.6, "rx": 0.95, "angle": 0.3, "color": BLUE}


def shots():
    return [
        {"id": "01-hook", "name": "HOOK (split): TRAIL -> DRIVE layup on top, UNDER -> THREE make below, same action, same second",
         "at": 0, "play": "D", "remap": [[0, 2.9], ["@end", 5.6]],
         "camera": [key(0, DRV_TOP0), key("@end", DRV_TOP1, "inOut")],
         "split": {"play": "U", "remap": [[0, 2.55], ["@end", 4.75]], "camera": [key(0, THR_BOT0), key("@end", THR_BOT1, "inOut")],
                   "ov3": []},
         "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": -0.3, "to": 1.4}],
         "screen": [{"type": "title", "lines": ["ONE SCREEN.", "TWO BAD CHOICES."], "gold": [1], "from": -0.3, "to": "@end", "y": 250, "size": 72},
                    {"type": "chip", "text": "TRAIL → DRIVE", "tone": "red", "y": 440, "from": -0.3, "to": "@end", "size": 52},
                    {"type": "chip", "text": "UNDER → THREE", "tone": "blue", "y": 1050, "from": -0.3, "to": "@end", "size": 52}]},
        {"id": "02-watch", "name": "WATCH THE DEFENDER: elevated 3/4 on the trio (O2, X2, O4) + O1, X2 ringed, O2's path previewed",
         "at": "Watch-0.1", "play": "D", "remap": [[0, 0.0], ["@end", 0.5]],
         "camera": [key(0, WATCH0), key("@end", WATCH1, "inOut")],
         "ov3": [{"type": "ring", "player": "X2", "color": GOLD, "pulse": True, "from": 0.05, "to": "@end"},
                 {"type": "route", "player": "O2", "t0": 0.55, "t1": 2.45, "fromPlay": "D", "color": GOLD, "draw": 0.6, "dashed": True, "width": 0.09, "from": "decisions.", "to": "seconds.-0.05"}],
         "screen": [{"type": "chip", "text": "X2 = THE DEFENDER", "tone": "gold", "y": 250, "from": "defender.", "to": "@end", "size": 50},
                    {"type": "pin", "player": "O4", "text": "PIN-DOWN", "from": "Two", "to": "@end", "size": 38},
                    {"type": "pin", "player": "O1", "text": "HANDOFF", "from": "seconds.", "to": "@end", "size": 38}]},
        {"id": "03a-pindown", "name": "PIN-DOWN: ONE continuous medium-wide 3/4 - O4 arrives, plants (both feet) BEFORE O2 passes, O2 flies off",
         "at": "First,-0.1", "play": "D", "remap": [[0, 0.45], ["@end", 2.3]],
         "camera": [key(0, PD0), key("@end", PD1, "inOut")],
         "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": -1.85, "from": "pin-down.-0.3", "to": "@end"},
                 {"type": "route", "player": "O2", "t0": 0.55, "t1": 2.4, "trail": True, "color": GOLD, "width": 0.09, "from": "shooter", "to": "@end"}],
         "screen": [{"type": "title", "lines": ["PIN-DOWN"], "gold": [0], "from": 0.05, "to": "@end", "y": 250, "size": 96}]},
        {"id": "03b-chase", "name": "THE CHASE: from behind X2, he has to go over the top of the screen, a step late (D 1.2 -> 2.38)",
         "at": "and-0.06", "play": "D", "remap": [[0, 1.2], ["@end", 2.38]],
         "camera": [key(0, orb(fol(["X2"], 1.0, window=0.5), 8.2, 62, 70, 42)), key("@end", orb(fol(["X2", "O2"], 1.0, window=0.5), 8.6, 62, 62, 42), "inOut")],
         "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"},
                 {"type": "route", "player": "X2", "t0": 1.1, "t1": 2.45, "color": RED, "trail": True, "width": 0.08, "from": 0.1, "to": "@end"}],
         "screen": [{"type": "chip", "text": "X2 CHASES", "tone": "red", "y": 230, "from": "defender#2", "to": "@end", "size": 56}]},
        {"id": "04-handoff", "name": "HANDOFF: ONE continuous low 3/4 medium-wide - offer, both hands on the ball, release, turn the corner",
         "at": "Then,-0.1", "play": "D", "remap": [[0, 2.0], ["handoff.>", 2.66], ["@end", 2.82]],
         "camera": [key(0, HO0), key("@end", HO1, "linear")],
         "ov3": [{"type": "glow", "player": "O1", "r": 0.5, "color": GOLD, "strength": 0.35, "from": "handoff.-0.3", "to": "handoff.>"}],
         "screen": [{"type": "title", "lines": ["HANDOFF"], "gold": [0], "from": 0.05, "to": "@end", "y": 250, "size": 96}]},
        {"id": "05-trail", "name": "TRAIL -> DRIVE: X2 chases over the hand-off, O2 turns the corner, two dribbles, gather, layup, through the net",
         "at": "Trail-0.1", "play": "D", "remap": [[0, 2.62], ["@end", 5.55]],
         "camera": [key(0, CHASE0), key("recover.", CHASE1, "inOut")],
         "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "turns-0.25"},
                 {"type": "route", "player": "X2", "t0": 2.55, "t1": 3.6, "color": RED, "trail": True, "width": 0.08, "from": 0.1, "to": "before"},
                 {**lane(), "from": "turns", "to": "before"}],
         "screen": [{"type": "chip", "text": "TRAIL → DRIVE", "tone": "red", "y": 230, "from": 0.05, "to": "@end", "size": 64},
                    {"type": "stamp", "text": "LAYUP", "badge": "+2", "from": "recover.>+0.25", "to": "@end", "y": 340}]},
        {"id": "06-under", "name": "SAME SETUP -> UNDER -> THREE: X2 goes under the pin-down and the hand-off, the gap, catch behind the arc, three",
         "at": "But-0.1", "play": "U", "remap": [[0, 0.95], ["under?>", 2.0], ["up.>", 3.96], ["@end", 4.62]],
         "camera": [key(0, UND0), key("under?", UND0, "hold"), key("leave", UND1, "inOut"), key("up.", UND2, "inOut")],
         "ov3": [{"type": "ring", "player": "X2", "color": BLUE, "from": 0.2, "to": "under?>"},
                 {"type": "route", "player": "X2", "t0": 0.9, "t1": 2.6, "color": BLUE, "trail": True, "width": 0.08, "from": 0.3, "to": "space"},
                 {**gap(), "from": "leave", "to": "rise"}],
         "screen": [{"type": "rewind", "from": 0, "to": 0.4},
                    {"type": "micro", "text": "SAME SETUP", "y": 330, "from": 0, "to": 0.9},
                    {"type": "chip", "text": "UNDER → THREE", "tone": "blue", "y": 230, "from": "under?", "to": "@end", "size": 64},
                    {"type": "stamp", "text": "THREE", "badge": "+3", "from": "up.>+0.55", "to": "@end", "y": 340}]},
        {"id": "07a-recap", "name": "RECAP pin-down: one 3/4 angle, key trio, CHICAGO ACTION reveal (D 0.9 -> 2.25)",
         "at": "That's-0.1", "play": "D", "remap": [[0, 0.85], ["@end", 2.25]],
         "camera": [key(0, RC0), key("@end", RC1, "inOut")],
         "ov3": [{"type": "screen", "player": "O4", "n": 1, "facing": -1.85, "from": 0.1, "to": "@end"},
                 {"type": "route", "player": "O2", "t0": 0.9, "t1": 2.3, "trail": True, "color": GOLD, "width": 0.09, "from": "cut,-0.3", "to": "@end"}],
         "screen": [{"type": "title", "lines": ["CHICAGO ACTION"], "gold": [0], "sub": "PIN-DOWN → DHO", "from": 0.05, "to": "@end", "y": 250, "size": 96}]},
        {"id": "07b-recap", "name": "RECAP hand-off: SAME angle, the DHO (D 2.25 -> 2.75)",
         "at": "one handoff,-0.06", "play": "D", "remap": [[0, 2.25], ["@end", 2.78]],
         "camera": [key(0, RC1), key("@end", {**RC1, "dist": 10.2}, "linear")],
         "ov3": [{"type": "glow", "player": "O1", "r": 0.5, "color": GOLD, "strength": 0.3, "from": 0.0, "to": "@end"}],
         "screen": [{"type": "chip", "text": "PIN-DOWN → DHO", "tone": "gold", "y": 230, "from": 0, "to": "@end", "size": 56}]},
        {"id": "07c-recap", "name": "RECAP payoffs (split): drive layup on top, three below, at speed",
         "at": "two very-0.06", "play": "D", "remap": [[0, 3.55], ["@end", 5.05]],
         "camera": [key(0, DRV_TOP1), key("@end", {**DRV_TOP1, "dist": 9.0}, "linear")],
         "split": {"play": "U", "remap": [[0, 2.75], ["@end", 4.25]], "camera": [key(0, THR_BOT1), key("@end", {**THR_BOT1, "dist": 10.6}, "linear")]},
         "screen": [{"type": "chip", "text": "TRAIL → DRIVE", "tone": "red", "y": 250, "from": 0, "to": "@end", "size": 52},
                    {"type": "chip", "text": "UNDER → THREE", "tone": "blue", "y": 1050, "from": 0, "to": "@end", "size": 52}]},
        {"id": "08-cta", "name": "CTA (split, moving): the same fork replayed slowly, X2's TRAIL route (red) vs UNDER route (blue)",
         "at": "You're-0.1", "play": "D", "remap": [[0, 2.45], ["@end", 3.55]],
         "camera": [key(0, orb([-2.0, 7.1, 1.0], 11.0, 58, 16, 40)), key("@end", orb([-1.6, 6.3, 1.0], 10.0, 60, 22, 40), "inOut")],
         "ov3": [{"type": "ring", "player": "X2", "color": RED, "from": 0, "to": "@end"},
                 {"type": "route", "player": "X2", "t0": 2.3, "t1": 3.7, "color": RED, "trail": True, "width": 0.09, "from": 0.2, "to": "@end"},
                 {**lane(), "from": "Trail#2", "to": "@end"}],
         "split": {"play": "U", "remap": [[0, 1.6], ["@end", 2.95]],
                   "camera": [key(0, orb([-3.0, 6.6, 1.0], 11.0, 60, 58, 40)), key("@end", orb([-2.6, 7.0, 1.2], 10.4, 62, 50, 40), "inOut")],
                   "ov3": [{"type": "ring", "player": "X2", "color": BLUE, "from": 0, "to": "@end"},
                           {"type": "route", "player": "X2", "t0": 1.0, "t1": 2.6, "color": BLUE, "trail": True, "width": 0.09, "from": 0.2, "to": "@end"},
                           {**gap(), "from": "under?#2", "to": "@end"}]},
         "screen": [{"type": "chip", "text": "TRAIL", "tone": "red", "y": 390, "from": "Trail#2", "to": "@end", "size": 60},
                    {"type": "chip", "text": "UNDER", "tone": "blue", "y": 1050, "from": "under?#2", "to": "@end", "size": 60},
                    {"type": "micro", "text": "WHAT'S YOUR COVERAGE?", "y": 290, "from": "Tell", "to": "@end"}]},
        {"id": "09-outro", "name": "OUTRO: slow orbit round the net as the three drops through, E2A logo (no static hold)",
         "at": "Follow-0.1", "play": "U", "remap": [[0, 3.6], ["@end", 5.0]],
         "camera": [key(0, NET0), key("@end", NET1, "inOut")],
         "screen": [{"type": "scrim", "opacity": 0.2, "from": 0.6, "to": "@end"},
                    {"type": "logo", "y": 1060, "width": 300, "from": 0.5, "to": "@end"}]},
    ]


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def build():
    v2 = json.load(open(os.path.join(D, "chicago-action-v2.json")))
    words = json.load(open(os.path.join(D, WORDS_SRC)))
    ep = {"id": EID, "title": "Chicago Action V3: one screen, two bad choices (audio-locked re-edit)", "fps": 30,
          "voice": AUDIO["voice"], "voiceMix": AUDIO["voiceMix"], "preroll": v2["preroll"],
          "plays": {"D": "chicago-v3-trail-drive", "U": "chicago-v3-under-three"},
          "branches": {"trail": "D", "under": "U"}}
    ep["tail"] = round(38.0 - words[-1]["end"], 3)          # 38.00 s = 1140 frames, the V2 soundtrack length
    ep["env"] = "cinema"
    ep["shots"] = shots()
    ep["pinV2"] = True
    ep["autoSfx"] = False                                   # voice + music only: no ball-bounce or any other SFX
    ep["keywords"] = v2["keywords"]
    ep["subtitleY"] = 1350
    # captions on the seam while the screen is split (both outcomes stay clear), elsewhere in the 1350 band
    ep["subtitleYAt"] = [[0, "Watch-0.1", SEAM_Y], ["two very-0.06", "Follow-0.1", SEAM_Y]]
    ep["subtitleGroups"] = v2["subtitleGroups"]
    ep["subtitleBlock"] = True
    ep["music"] = {"src": AUDIO["music"], "volume": 1}
    # ---- audio guard (brief sec. 0): reuse only, never generate
    ep["audioReuseOnly"] = True
    ep["disallowTTS"] = True
    pub = os.path.join(T, "public")
    ep["audioLock"] = {"source": "Chicago V2 stems of 2026-11-21 (one Deuce take, generation YSsSfdFXlO54uKYjQCcI, already paid); reused unchanged",
                       "files": {AUDIO[k]: sha(os.path.join(pub, AUDIO[k])) for k in ("voice", "voiceMix", "music")},
                       "words": {f"tactical/episodes/{WORDS_SRC}": sha(os.path.join(D, WORDS_SRC))},
                       "elevenlabsCreditsSpentForV3": 0}
    json.dump(ep, open(os.path.join(D, f"{EID}.json"), "w"), indent=1, ensure_ascii=False)
    json.dump(words, open(os.path.join(D, f"{EID}.words.json"), "w"), indent=0)
    print(EID, len(ep["shots"]), "shots, tail", ep["tail"])


def cover(out):
    """clean cover (no text, no overlays): low 3/4 on the hand-off, both hands on the ball (D 2.47)"""
    ep = json.load(open(os.path.join(D, f"{EID}.json")))
    plays = {k: json.load(open(os.path.join(T, "tactical", "plays", f"{v}.json"))) for k, v in ep["plays"].items()}
    sh = [{"id": "cover", "name": "cover", "at": 0, "play": "D", "remap": [[0, 2.47], [1.0, 2.47]],
           "camera": [key(0, orb([-2.95, 8.3, 1.1], 6.4, 76, 150, 40))], "ov3": [], "screen": []}]
    e2 = {**ep, "id": f"{EID}-cover", "shots": sh, "words": [{"text": "cover", "start": 0, "end": 1.0}], "plays": plays,
          "subtitleHide": [[0, 99]], "subtitleGroups": [1], "subtitleYAt": [], "voice": AUDIO["voice"], "tail": 0}
    e2.pop("voiceMix", None)
    e2.pop("music", None)
    json.dump({"episode": e2}, open(out, "w"))
    print("cover props", out)


if __name__ == "__main__":
    if "--cover" in sys.argv:
        cover(sys.argv[sys.argv.index("--cover") + 1])
    else:
        build()
