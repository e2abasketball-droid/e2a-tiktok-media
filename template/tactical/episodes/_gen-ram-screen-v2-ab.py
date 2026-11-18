#!/usr/bin/env python3
"""RAM Screen V2 — editorial A/B (V4, 2026-11-15). ONE variable: camera grammar.
Control = ram-screen-v2.json unchanged. Variant B = same plays, same voice/mix/music/SFX, same shot timings,
same overlays and titles; only the camera keys change:
  * open on a HIGH tactical shot (low pitch = more top-down) with X5, the ball (O1) and the court visible from frame 0;
  * hold ONE axis (yaw AXIS) through the first screen, the head start and the ball screen (no drift/orbit);
  * the camera moves only to reveal the advantage (readA1 push on the pull-up, readA2/readB2 unchanged,
    readB1 widening on the blitz), then returns to the opening framing for the CTA.
The audio track of the variant is muxed from the control master, so audio is byte-identical.
Owner proposal 2026-11-14 16:30Z. Usage: python3 tactical/episodes/_gen-ram-screen-v2-ab.py"""
import copy, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
ep = json.load(open(os.path.join(HERE, 'ram-screen-v2.json')))
AXIS = -30
WIDE = {"type": "orbit", "target": [-0.2, 6.6, 0.4], "dist": 15.0, "pitch": 38, "yaw": AXIS, "fov": 42}
def rig(**kw):
    r = copy.deepcopy(WIDE); r.update(kw); return r
cams = {
    # same frame for the whole hook: decision (X5), ball (O1) and both screeners readable at once
    'hook': [{"at": 0, "rig": rig()}, {"at": "@end", "rig": rig(dist=14.6), "ease": "linear"}],
    # rewind on the SAME axis (no orbit): only a slow 0.6 m push so the first screen reads
    'reveal': [{"at": 0, "rig": rig()}, {"at": "@end", "rig": rig(target=[-0.4, 6.4, 0.4], dist=14.0), "ease": "linear"}],
    # ball screen: same axis, push in on X5's decision
    'question': [{"at": 0, "rig": rig(target=[0.3, 8.0, 0.8], dist=12.6, pitch=44)},
                 {"at": "@end", "rig": rig(target=[0.4, 8.2, 0.9], dist=11.6, pitch=46), "ease": "linear"}],
    # the advantage: the camera moves only now (drop -> O1's space -> the pull-up)
    'readA1': [{"at": 0, "rig": rig(target=[0.4, 8.2, 0.9], dist=11.6, pitch=46)},
               {"at": "backs up.>", "rig": rig(target={"follow": ["O1", "X5"], "z": 1.1}, dist=9.6, pitch=56, yaw=-48), "ease": "inOut"},
               {"at": "the pull-up", "rig": {"type": "orbit", "target": {"follow": "O1", "z": 1.3}, "dist": 7.2, "pitch": 64, "yaw": -52, "fov": 44}, "ease": "inOut"},
               {"at": "@end", "rig": {"type": "orbit", "target": {"follow": "O1", "z": 1.4}, "dist": 7.0, "pitch": 64, "yaw": -48, "fov": 44}, "ease": "linear"}],
    # read B starts on the SAME axis and frame as the question shot, widens to reveal the gap
    'readB1': [{"at": 0, "rig": rig(target=[0.4, 8.2, 0.9], dist=11.6, pitch=46)},
               {"at": "Now both", "rig": rig(target=[0.4, 8.2, 0.9], dist=11.6, pitch=46), "ease": "linear"},
               {"at": "the ball.>", "rig": rig(target=[-0.1, 9.6, 0.9], dist=13.4, pitch=46), "ease": "inOut"},
               {"at": "@end", "rig": rig(target=[-0.1, 9.6, 0.9], dist=13.2, pitch=46), "ease": "linear"}],
    'cmpA': [{"at": 0, "rig": rig(target=[0.0, 8.0, 0.5], dist=14.5, pitch=40)}],
    'cmpB': [{"at": 0, "rig": rig(target=[0.0, 8.0, 0.5], dist=14.5, pitch=40)}],
    'cta': [{"at": 0, "rig": rig(target=[0.0, 8.0, 0.5], dist=14.5, pitch=40)}, {"at": "@end", "rig": rig(), "ease": "inOut"}],
}
for s in ep['shots']:
    if s['id'] in cams:
        s['camera'] = cams[s['id']]
ep['id'] = 'ram-screen-v2-ab'
ep['title'] = 'RAM SCREEN V2 — variant B (high open, held axis)'
ep['abOf'] = {'control': 'ram-screen-v2', 'variable': 'camera grammar only', 'audio': 'muxed from control master'}
json.dump(ep, open(os.path.join(HERE, 'ram-screen-v2-ab.json'), 'w'), indent=1)
print('wrote ram-screen-v2-ab.json')
