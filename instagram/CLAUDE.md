# Instagram automation — Claude Code instructions
Read `instagram/SPEC.md` first (authoritative), then `instagram/STATUS.md` (what works / what is blocked). Daily routine prompt: `instagram/ROUTINE_PROMPT.md`.
Rules: stay inside `instagram/`; never touch TikTok/YouTube files; no force-push; no secrets in git; never claim a step passed unless verified; if the target day already has ≥2 IG posts in Metricool, schedule nothing.
Env: Chromium at `/opt/pw-browsers/chromium-*/chrome-linux64/chrome` (pass `--browser-executable`); run `bash instagram/scripts/check-env.sh`.
Metricool brand 7681319, tz Australia/Sydney. Media URL check: `instagram/scripts/check-media-url.sh <url>`.
