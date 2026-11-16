# E2A Instagram automation (cloud)

Autonomous production + scheduling of 8 static posts and 6 Reels per week for E2A Basketball Academy.
Start with `CLAUDE.md`, rules in `SPEC.md`, daily routine prompt in `ROUTINE_PROMPT.md`. See `CLAUDE.md` for the verified status and recipes.

Quick checks: `bash scripts/check-media-url.sh <url> video/` ; `node scripts/verify-reel.mjs <mp4>` ;
`cd breakdown-template && npm install` ; `node scripts/render-reel.mjs episodes/ep02-horns/episode.json out.mp4`.
Do not touch `videos/`, `template/`, `assets/`, `test/` (TikTok automation).
