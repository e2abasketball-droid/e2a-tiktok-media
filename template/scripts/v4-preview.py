#!/usr/bin/env python3
"""V4 low-cost previews (owner brief 2026-11-14 16:52Z): no new voice, no credits, no Metricool.
Clean Course3D render of a play (real play speed, high tactical camera) + a freeze on the READ before the outcome
+ timed subtitles burned in with ffmpeg. One MP4 per play, 1280x720, silent.

  python3 scripts/v4-preview.py <play_id> <out.mp4>          (cues in CUES below, in PLAY seconds)
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.dirname(HERE)
CHROME = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell"
FONT = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FREEZE = 1.4
# (from, to, text) in play time; "freeze" = play time where the clip holds on the read
CUES = {
    "v4-horns-twist": {"freeze": 2.8, "freeze_text": "READ: watch Four. A second screen on the switched big.", "lines": [
        (0.0, 1.05, "Horns: two bigs at the elbows."), (1.05, 2.1, "First ball screen. The defence switches."),
        (2.1, 2.8, "Now a big is guarding the guard."), (2.8, 4.85, "The twist: the guard turns the corner."),
        (4.85, 6.4, "Downhill to the rim. +2")]},
    "v4-ice-contain": {"freeze": 1.6, "freeze_text": "READ: where is the big? Already on the baseline side.", "lines": [
        (0.0, 1.05, "Side ball screen on the wing."), (1.05, 1.6, "ICE: the guard's defender jumps to the top."),
        (1.6, 3.25, "Forced baseline. The big is waiting."), (3.25, 5.0, "Contained. The ball goes back out.")]},
    "v4-ice-reject": {"freeze": 1.15, "freeze_text": "READ: the big is still up with the screener.", "lines": [
        (0.0, 1.15, "Same setup: they ICE the screen."), (1.15, 3.05, "Reject: baseline, before he drops."),
        (3.05, 4.8, "Layup. The counter to ICE.")]},
    "v4-corner-help": {"freeze": 2.1, "freeze_text": "WHAT WOULD YOU DO? Kick or attack?", "lines": [
        (0.0, 0.5, "Drive from the slot."), (0.5, 2.1, "Watch the corner defender."),
        (2.1, 3.05, "His feet stopped: kick."), (3.05, 5.6, "Corner three. Comment KICK or ATTACK.")]},
}


def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace(",", "\\,")


def main(play_id, out):
    cue = CUES[play_id]
    play = json.load(open(os.path.join(T, "tactical", "plays", f"{play_id}.json")))
    with tempfile.TemporaryDirectory() as td:
        props = os.path.join(td, "p.json")
        json.dump({"play": play, "from": 0, "to": play["duration"], "mirrorX": True}, open(props, "w"))
        raw = os.path.join(td, "raw.mp4")
        subprocess.run(["npx", "remotion", "render", "src/course3d/index.tsx", "Course3D", raw, f"--props={props}",
                        f"--browser-executable={CHROME}", "--gl=swangle", "--timeout=180000",
                        f"--concurrency={os.environ.get('CONCURRENCY', '2')}", "--codec=h264", "--crf=18", "--log=error"],
                       cwd=T, check=True)
        fz = cue["freeze"]
        shift = lambda t: t if t < fz else t + FREEZE
        draws = [f"drawtext=fontfile={FONT}:text='PREVIEW · {esc(play_id)} · silent · shadow':x=24:y=20:fontsize=22:fontcolor=white@0.7"]
        for a, b, txt in cue["lines"]:
            draws.append(f"drawtext=fontfile={FONT}:text='{esc(txt)}':x=(w-text_w)/2:y=h-96:fontsize=40:fontcolor=white:"
                         f"box=1:boxcolor=0x0B1C3D@0.78:boxborderw=18:enable='between(t,{shift(a):.3f},{shift(b) - 0.001:.3f})'")
        draws.append(f"drawtext=fontfile={FONT}:text='{esc(cue['freeze_text'])}':x=(w-text_w)/2:y=h-96:fontsize=40:fontcolor=0x0B1C3D:"
                     f"box=1:boxcolor=0xC9A24D@0.95:boxborderw=18:enable='between(t,{fz:.3f},{fz + FREEZE - 0.001:.3f})'")
        fc = (f"[0:v]trim=0:{fz},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={FREEZE}[a];"
              f"[0:v]trim={fz},setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1[c];[c]{','.join(draws)}[v]")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-filter_complex", fc, "-map", "[v]", "-c:v", "libx264",
                        "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
