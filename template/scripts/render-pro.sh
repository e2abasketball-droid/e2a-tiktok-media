#!/usr/bin/env bash
# Render a Pro episode end to end: render -> H.264 yuv420p re-encode + loudness -> QC.
# Usage: scripts/render-pro.sh episodes/<id>.json out/<id>.mp4 [--min 20 --max 26]
set -euo pipefail
EP=$1; OUT=$2; shift 2
CHROME=${CHROME:-$(ls /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | head -1)}
mkdir -p "$(dirname "$OUT")"
TMP=$(mktemp -d)
node scripts/validate-episode.mjs "$EP"
# music bed fitted to this episode (E2A music engine); falls back to the episode's own music file
node scripts/episode-music.mjs "$EP" "$TMP/props.json"
npx remotion render src/index.ts Pro "$TMP/raw.mp4" --props="$TMP/props.json" \
  ${CHROME:+--browser-executable="$CHROME"} --codec=h264 --crf=16 --x264-preset=medium --log=error
# final encode: broadcast-safe pixel format, high-quality H.264, loudness -14 LUFS / -1.5 dBTP
ffmpeg -y -loglevel error -i "$TMP/raw.mp4" -c:v libx264 -preset slow -crf ${CRF:-19} -pix_fmt yuv420p -profile:v high \
  -movflags +faststart -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k "$OUT"
node scripts/qc-pro.mjs "$OUT" "$@" --frames "${OUT%.mp4}_qc"
