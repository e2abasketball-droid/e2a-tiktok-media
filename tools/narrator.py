#!/usr/bin/env python3
"""E2A narrator standard (2026-11-27): the ONE place every production gets its narration settings from.
Config: config/e2a-narrator-default.json (Nathaniel 9rR45HW0vcBmpCbkc4m9, eleven_v4, one take, inline direction tags).

Speech is generated through the ElevenLabs MCP tool (mcp__ElevenLabs__creative_generate_speech), not from code, so this
module produces exactly what that call must contain and guards it:

  python3 tools/narrator.py params  script.json            # JSON for creative_generate_speech (voice_id, model_id, 1 take, prompt)
  python3 tools/narrator.py prompt  script.json            # only the direction-tagged prompt
  python3 tools/narrator.py check   --voice-id X --model-id Y [--episode ep.json]   # exit 1 if not the standard (CI / agents)
  python3 tools/narrator.py process --voice v.wav --words w.json --curve c.json --out v.mix.wav [--music m.wav --mix-out mix.wav --duration s]
                                                           # prints (or --run runs) the standard voice-dynamics chain

script.json: {"lines": [["hook", "You're watching the wrong player."], ["suspense", "Watch this defender."], ...]}
  Each line has a phase from config performance.arc (hook, setup, suspense, explanation, pre-reveal, reveal, payoff,
  lesson, close) or an explicit tag: ["tag:slower, confident teaching", "Great passers ..."].
  Tags are emitted only when the delivery changes (a tag holds until the next one).

Override: an episode may use another narrator ONLY with {"narrator_override": true, "override_owner_message": "<date, thread>"}
in its own config, after an explicit owner instruction. Without both fields `check` fails.
"""
import argparse, json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "config", "e2a-narrator-default.json")))
PHASE_TAG = {p["phase"]: p["tags"][-1] for p in CFG["performance"]["arc"]}


def build_prompt(lines):
    out, last = [], None
    for phase, text in lines:
        tag = phase[4:] if phase.startswith("tag:") else PHASE_TAG.get(phase)
        if tag is None:
            sys.exit(f"unknown phase {phase!r}; use one of {sorted(PHASE_TAG)} or 'tag:<words>'")
        out.append((f"[{tag}] " if tag != last else "") + text.strip())
        last = tag
    return "\n\n".join(out)


def params(lines):
    return {"model_id": CFG["synthesis"]["model_id"], "voice_id": CFG["voice"]["voice_id"],
            "generations_count": CFG["synthesis"]["generations_count"], "prompt": build_prompt(lines),
            "_note": "leave voice_settings unset (the approved V3 take used the connector defaults); never re-run a call to retry"}


def check(voice_id, model_id, episode=None):
    ep = json.load(open(episode)) if episode else {}
    if ep.get("narrator_override") is True:
        if not ep.get("override_owner_message"):
            return False, "narrator_override is true but override_owner_message (owner's explicit instruction) is missing"
        return True, f"override accepted (owner: {ep['override_owner_message']})"
    errs = []
    if voice_id != CFG["voice"]["voice_id"]:
        errs.append(f"voice_id {voice_id} is not the E2A narrator {CFG['voice']['voice_id']} ({CFG['voice']['voice_name']})")
    if model_id != CFG["synthesis"]["model_id"]:
        errs.append(f"model_id {model_id} is not {CFG['synthesis']['model_id']}")
    return (not errs), ("; ".join(errs) or "OK: E2A narrator standard")


def process_cmd(a):
    cmd = ["python3", os.path.join(ROOT, "template", "scripts", "voice-dynamics.py"), "--voice", a.voice, "--words", a.words,
           "--curve", a.curve, "--out", a.out, "--preserve", "--mix-lufs", "-16"]
    if a.music:
        cmd += ["--music", a.music, "--mix-out", a.mix_out, "--duration", str(a.duration)]
    if a.report:
        cmd += ["--report", a.report]
    return cmd


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("params", "prompt"):
        s = sub.add_parser(n); s.add_argument("script")
    c = sub.add_parser("check"); c.add_argument("--voice-id", required=True); c.add_argument("--model-id", required=True); c.add_argument("--episode")
    p = sub.add_parser("process")
    for f in ("--voice", "--words", "--curve", "--out"):
        p.add_argument(f, required=True)
    p.add_argument("--music"); p.add_argument("--mix-out"); p.add_argument("--duration", type=float); p.add_argument("--report"); p.add_argument("--run", action="store_true")
    a = ap.parse_args()
    if a.cmd in ("params", "prompt"):
        lines = json.load(open(a.script))["lines"]
        print(json.dumps(params(lines), indent=1, ensure_ascii=False) if a.cmd == "params" else build_prompt(lines))
    elif a.cmd == "check":
        ok, msg = check(a.voice_id, a.model_id, a.episode)
        print(msg)
        sys.exit(0 if ok else 1)
    else:
        cmd = process_cmd(a)
        print(" ".join(cmd))
        if a.run:
            sys.exit(subprocess.run(cmd).returncode)
