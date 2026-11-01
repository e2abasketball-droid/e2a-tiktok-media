# Cloud routine setup (create in claude.ai/code → Routines → New)
- Name: `E2A — Daily Instagram Automation`; schedule: daily 08:00, timezone Australia/Sydney
- Repository: `e2abasketball-droid/e2a-tiktok-media`, branch `main` (only after the PR is merged); environment: Full network access, connectors Metricool, Google Drive/Sheets, ElevenLabs, GitHub.

## Prompt
You operate E2A's Instagram automation. First read `instagram/SPEC.md`, `instagram/CLAUDE.md` and `instagram/STATUS.md`. Then execute the daily workflow in SPEC §12 for tomorrow (Australia/Sydney): run `bash instagram/scripts/check-env.sh`, fetch tomorrow's Metricool schedule for brand 7681319, and fill only free slots without exceeding 2 IG publications that day. Actually create, render, upload, verify and schedule the media and update the Google Sheet tracker; do not just plan. On Mondays also run the weekly analytics (§13). Commit new media under `instagram/YYYY-MM-DD/` to the working branch. If a requirement can't be verified, skip that slot and send a PushNotification explaining why; notify also on errors or when something needs the owner. Stay silent if everything is routine.
