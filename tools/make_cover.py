#!/usr/bin/env python3
"""Instagram cover for a Tactical Studio reel: one frame of the reel itself, E2A palette, a 2–5 word English
title and a small logo, checked against the profile-grid crops.

    python3 tools/make_cover.py VIDEO.mp4 --at 2.5 --title "Catch or Backdoor?" --out cover.jpg [--report r.json] [--previews DIR]

Rules it enforces (so a cover never reaches Metricool broken):
- the frame comes from the reel (ffmpeg, exact timestamp), 1080×1920, no stock or generated imagery;
- title: English, 2–5 words, ≤ 2 lines, fully inside the 1:1 crop (the strictest profile crop) and the 3:4 grid crop;
- logo: small, inside the 3:4 grid crop, outside the title box;
- output: baseline JPEG, sRGB, no alpha, ≤ 8 MB (Metricool videoThumbnailUrl accepts jpg/jpeg/png only).
The reel burns its own titles (top) and captions (bottom) into every frame: only the action band between them is
used, enlarged and set on navy, so the cover shows one title only. Font: Anton (SIL OFL) as tools/fonts/anton.ttf, converted from template/public/anton.woff2.
"""
import argparse, hashlib, io, json, os, re, subprocess, sys, tempfile

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1080, 1920
NAVY, GOLD, WHITE = (11, 28, 61), (201, 162, 77), (255, 255, 255)
# what Instagram shows of a 9:16 reel: profile grid (3:4, current), legacy square grid (1:1), feed (4:5)
CROPS = {"grid_3x4": (0, 240, 1080, 1680), "square_1x1": (0, 420, 1080, 1500), "feed_4x5": (0, 285, 1080, 1635)}
SIDE = 80                 # horizontal safe margin for text
TITLE_BOTTOM = 1440       # title block ends here: inside 1:1 (1500) with 60 px air
LOGO_W, LOGO_CY = 132, 1585
MAX_BYTES = 8 * 1024 * 1024


class CoverError(Exception):
    pass


def font(path, size):
    if path.endswith((".woff2", ".woff")):
        from fontTools.ttLib import TTFont  # pip install fonttools brotli
        f = TTFont(path); f.flavor = None; b = io.BytesIO(); f.save(b); b.seek(0)
        return ImageFont.truetype(b, size)
    return ImageFont.truetype(path, size)


def check_title(title):
    words = title.split()
    if not 2 <= len(words) <= 5:
        raise CoverError(f"title must have 2–5 words, got {len(words)}: {title!r}")
    if not re.fullmatch(r"[A-Za-z0-9'’&?!.,:\- ]+", title):
        raise CoverError(f"title must be plain English text: {title!r}")
    return words


def grab_frame(video, at):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "f.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{at:.3f}", "-i", video, "-frames:v", "1",
                        "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", out], check=True)
        return Image.open(out).convert("RGB")


def gradient(img, y0, y1, alpha0, alpha1):
    """Navy overlay whose opacity goes linearly from alpha0 at y0 to alpha1 at y1."""
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for y in range(min(y0, y1), max(y0, y1) + 1):
        t = (y - y0) / (y1 - y0) if y1 != y0 else 1
        d.line([(0, y), (W, y)], fill=NAVY + (int(255 * (alpha0 + (alpha1 - alpha0) * t)),))
    return Image.alpha_composite(img.convert("RGBA"), ov)


def wrap(words, fnt, maxw, draw):
    """Best split into ≤ 2 balanced lines that fit."""
    best = None
    for k in range(1, len(words) + 1):
        lines = [" ".join(words[:k])] + ([" ".join(words[k:])] if k < len(words) else [])
        widths = [draw.textlength(l, font=fnt) for l in lines]
        if max(widths) <= maxw and (best is None or max(widths) < best[1]):
            best = (lines, max(widths))
    return best[0] if best else None


def inside(box, rect):
    return box[0] >= rect[0] and box[1] >= rect[1] and box[2] <= rect[2] and box[3] <= rect[3]


def make_cover(video, at, title, out, title_font=None, logo=None, band=(480, 1180), zoom=1.2, focus_x=0.55, place_y=250):
    words = check_title(title)
    title_font = title_font or os.path.join(ROOT, "tools/fonts/anton.ttf")  # TTF: Pillow needs no fontTools
    logo = logo or os.path.join(ROOT, "template/public/e2a_logo_white.png")
    frame = grab_frame(video, at)
    # the reel burns its own title in the top band and captions in the bottom band: keep only the action band
    # between them, enlarge it a little and set it on navy, so the cover shows one title (ours)
    b0, b1 = band
    if not (0 <= b0 < b1 <= H) or zoom < 1:
        raise CoverError("bad band/zoom")
    crop = frame.crop((0, b0, W, b1))
    cw, ch = round(W * zoom), round((b1 - b0) * zoom)
    crop = crop.resize((cw, ch), Image.LANCZOS)
    x0 = min(max(0, round(cw * focus_x - W / 2)), cw - W)
    crop = crop.crop((x0, 0, x0 + W, ch))
    img = Image.new("RGBA", (W, H), NAVY + (255,))
    img.paste(crop, (0, place_y))
    img = gradient(img, place_y, place_y + 160, 1.0, 0.0)
    img = gradient(img, place_y + ch - 330, place_y + ch, 0.0, 1.0)
    draw = ImageDraw.Draw(img)
    upper = [w.upper() for w in words]
    for size in range(190, 70, -4):
        f = font(title_font, size)
        lines = wrap(upper, f, W - 2 * SIDE, draw)
        if lines:
            break
    else:
        raise CoverError("title does not fit in two lines")
    lh = int(size * 1.02)
    y = TITLE_BOTTOM - lh * len(lines)
    boxes = []
    rule_y = y - 34
    draw.rectangle([SIDE, rule_y, SIDE + 120, rule_y + 8], fill=GOLD)
    for i, l in enumerate(lines):
        x = SIDE
        bb = draw.textbbox((x, y + i * lh), l, font=f)
        fill = GOLD if i == len(lines) - 1 and len(lines) > 1 else WHITE
        draw.text((x, y + i * lh), l, font=f, fill=fill)
        boxes.append(bb)
    tbox = (min(b[0] for b in boxes), min(min(b[1] for b in boxes), rule_y), max(b[2] for b in boxes), max(b[3] for b in boxes))
    lg = Image.open(logo).convert("RGBA")
    lg = lg.resize((LOGO_W, round(lg.height * LOGO_W / lg.width)), Image.LANCZOS)
    a = lg.getchannel("A").point(lambda v: int(v * 0.85)); lg.putalpha(a)
    lx, ly = (W - lg.width) // 2, LOGO_CY - lg.height // 2
    img.alpha_composite(lg, (lx, ly))
    lbox = (lx, ly, lx + lg.width, ly + lg.height)
    rgb = img.convert("RGB")
    rgb.save(out, "JPEG", quality=90, optimize=True, progressive=False, subsampling=0)
    size_b = os.path.getsize(out)
    checks = {
        "size_1080x1920": Image.open(out).size == (W, H),
        "title_2_to_5_words": True,
        "title_lines_le_2": len(lines) <= 2,
        "title_in_square_1x1": inside(tbox, CROPS["square_1x1"]) and tbox[0] >= SIDE - 2 and tbox[2] <= W - SIDE + 2,
        "title_in_grid_3x4": inside(tbox, CROPS["grid_3x4"]),
        "title_in_feed_4x5": inside(tbox, CROPS["feed_4x5"]),
        "logo_in_grid_3x4": inside(lbox, CROPS["grid_3x4"]),
        "logo_clear_of_title": lbox[1] > tbox[3],
        "jpeg_le_8MB": size_b <= MAX_BYTES,
    }
    rep = {"video": os.path.basename(video), "video_sha256": sha(video), "at_s": at, "band": list(band), "zoom": zoom, "title": title, "lines": lines,
           "font_px": size, "title_box": tbox, "logo_box": lbox, "crops": CROPS, "checks": checks,
           "ok": all(checks.values()), "out": out, "bytes": size_b, "sha256": sha(out)}
    if not rep["ok"]:
        raise CoverError("cover failed checks: " + ", ".join(k for k, v in checks.items() if not v))
    return rep


def previews(cover, outdir):
    """What the profile shows: each crop at grid size, plus a 3-column profile mock with the cover in the middle."""
    os.makedirs(outdir, exist_ok=True)
    im = Image.open(cover)
    paths = {}
    for k, box in CROPS.items():
        c = im.crop(box); c.thumbnail((360, 480)); p = os.path.join(outdir, f"crop-{k}.png"); c.save(p); paths[k] = p
    tile = im.crop(CROPS["grid_3x4"]).resize((360, 480), Image.LANCZOS)
    grid = Image.new("RGB", (3 * 360 + 4, 2 * 480 + 2), (250, 250, 250))
    for i in range(6):
        x, y = (i % 3) * 362, (i // 3) * 482
        grid.paste(tile if i == 1 else Image.new("RGB", (360, 480), (225, 228, 235)), (x, y))
    p = os.path.join(outdir, "profile-grid-mock.png"); grid.save(p); paths["profile_mock"] = p
    return paths


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("video"); ap.add_argument("--at", type=float, required=True, help="seconds into the reel")
    ap.add_argument("--title", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--report"); ap.add_argument("--previews")
    ap.add_argument("--band", type=int, nargs=2, default=[480, 1180], help="action band of the reel frame, y0 y1")
    ap.add_argument("--zoom", type=float, default=1.2); ap.add_argument("--focus-x", type=float, default=0.55)
    a = ap.parse_args(argv)
    try:
        rep = make_cover(a.video, a.at, a.title, a.out, band=tuple(a.band), zoom=a.zoom, focus_x=a.focus_x)
    except CoverError as e:
        print(json.dumps({"ok": False, "error": str(e)})); return 2
    if a.previews:
        rep["previews"] = previews(a.out, a.previews)
    if a.report:
        json.dump(rep, open(a.report, "w"), indent=1)
    print(json.dumps(rep, indent=1)); return 0


if __name__ == "__main__":
    sys.exit(main())
