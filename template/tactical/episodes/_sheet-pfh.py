#!/usr/bin/env python3
"""Contact sheets of the Pistol Fake Handoff hands rehearsal (keep vs give, before / at / after the contact).
  python3 tactical/episodes/_sheet-pfh.py <frames_dir> <out_dir>
frames_dir = PNG sequence of out/pfh/pfh-rehearsal.props.json (2 frames per shot, see out/pfh/pfh-rehearsal.index.json);
labels from out/pfh/hands-{keep,give}.json (scripts/hands-table.mts: ball phase, owner, fingertip-ball distances)."""
import json, os, sys, glob
from PIL import Image, ImageDraw, ImageFont
T = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
idx = json.load(open(os.path.join(T, "out", "pfh", "pfh-rehearsal.index.json")))
hands = {b: {r["S"]: r for r in json.load(open(os.path.join(T, "out", "pfh", f"hands-{b}.json")))} for b in ("keep", "give")}
files = sorted(glob.glob(os.path.join(src, "*.png")))
F = lambda n: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", n)
CW, CH = 360, 640
NOTE = {"keep": {43: "settled, 2 feet", 47: "offer", 49: "offer (peak)", 51: "X2 bites", 53: "O1 runs by, empty", 54: "keep: ball back", 56: "dribble out", 59: "1st bounce", 62: "baseline step", 66: "past X2", 72: "drive"},
        "give": {43: "settled", 45: "present", 47: "hand-off starts", 49: "both hands", 51: "both hands", 53: "O1 grips", 55: "O1 owner", 58: "O1 1st step", 62: "O1 inside"}}


def label(br, s):
    r = hands[br].get(s)
    if not r:
        return f"S{s:03d}"
    own = r["owner"] or "-"
    o1 = min(r["hands"]["O1"]); o2 = min(r["hands"]["O2"])
    return f"S{s:03d} {r['phase']} owner {own}\nO1 tip {o1*100:.0f} cm  O2 tip {o2*100:.0f} cm\n{NOTE[br].get(s, '')}"


cells = {}
for i, e in enumerate(idx):
    br, cam, s = e["shot"].split("-"); s = int(s[1:])
    im = Image.open(files[e["frame"]]).convert("RGB")
    cells.setdefault((br, cam), []).append((s, im))
for br in ("keep", "give"):
    for cam in ("C34", "LAT", "GAME"):
        row = cells[(br, cam)]
        sheet = Image.new("RGB", (CW * len(row), CH + 92), (18, 22, 34))
        d = ImageDraw.Draw(sheet)
        for k, (s, im) in enumerate(row):
            sheet.paste(im.resize((CW, CH)), (k * CW, 92))
            d.multiline_text((k * CW + 8, 4), label(br, s), font=F(17), fill=(255, 220, 120) if br == "keep" else (170, 220, 255), spacing=3)
        sheet.save(os.path.join(out, f"ensayo-{br}-{cam}.jpg"), quality=86)
        print(os.path.join(out, f"ensayo-{br}-{cam}.jpg"))
# before / at / after the sensitive contact, keep vs give side by side (3/4 + lateral)
pick = {"keep": [47, 51, 54], "give": [47, 53, 55]}
for cam in ("C34", "LAT"):
    sheet = Image.new("RGB", (CW * 3, 2 * (CH + 92)), (18, 22, 34)); d = ImageDraw.Draw(sheet)
    for j, br in enumerate(("keep", "give")):
        row = dict(cells[(br, cam)])
        for k, s in enumerate(pick[br]):
            y0 = j * (CH + 92)
            sheet.paste(row[s].resize((CW, CH)), (k * CW, y0 + 92))
            d.multiline_text((k * CW + 8, y0 + 4), f"{br.upper()} {['before', 'at', 'after'][k]}\n" + label(br, s), font=F(16),
                             fill=(255, 220, 120) if br == "keep" else (170, 220, 255), spacing=2)
    sheet.save(os.path.join(out, f"contacto-antes-en-despues-{cam}.jpg"), quality=86)
    print(os.path.join(out, f"contacto-antes-en-despues-{cam}.jpg"))
