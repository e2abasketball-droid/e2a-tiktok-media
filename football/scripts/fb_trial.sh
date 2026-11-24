#!/usr/bin/env bash
# E2A Football — TRIAL variant of a finished reel (owner rule 2026-11-16: two versions per reel, same voice take,
# file not identical): 3 % zoom, slightly more saturation/contrast/sharpness, soft voice-band EQ, loudness -14 LUFS
# re-measured, full re-encode. Football-only copy of the convention; the basketball tools are not touched.
#   bash football/scripts/fb_trial.sh <main.mp4> <trial.mp4>
set -euo pipefail
IN=$1; OUT=$2
[ -e "$OUT" ] && { echo "refusing to overwrite $OUT"; exit 1; }
VF="scale=1112:1978:flags=lanczos,crop=1080:1920,eq=saturation=1.06:contrast=1.03,unsharp=5:5:0.45"
AF="equalizer=f=2800:t=q:w=1.4:g=1.2,equalizer=f=180:t=q:w=1:g=-1"
J=$(ffmpeg -nostdin -hide_banner -i "$IN" -vn -af "$AF,loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
MI=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(f\"measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}\")")
ffmpeg -nostdin -loglevel error -i "$IN" -vf "$VF" -af "$AF,loudnorm=I=-14:TP=-1.5:LRA=11:$MI:linear=true,alimiter=limit=0.84:level=false" \
  -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$OUT"
ffmpeg -nostdin -hide_banner -i "$IN" -i "$OUT" -lavfi "[0:v][1:v]ssim" -f null - 2>&1 | grep -o "All:[0-9.]*"
