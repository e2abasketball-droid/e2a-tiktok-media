#!/bin/bash
# Trial-reel copy of a finished Reel (owner rule: every Reel gets a second, slightly different FILE for Instagram trial
# reels; same voice take, same edit). Video: ~3 % zoom (centre crop, keeps the safe areas), a touch more saturation,
# contrast and sharpness. Audio: soft voice EQ (presence +1.5 dB, low-mid -1 dB) and the same fixed master gain idea
# (no loudnorm, no limiter). Prints the SSIM against the source (target ~0.7-0.8).
#   bash scripts/trial-variant.sh <reel.mp4> <trial.mp4> [zoom=1.03]
set -euo pipefail
IN=$1; OUT=$2; Z=${3:-1.03}
ffmpeg -v error -y -i "$IN" \
  -vf "scale=trunc(iw*${Z}/2)*2:trunc(ih*${Z}/2)*2:flags=lanczos,crop=1080:1920,eq=saturation=1.10:contrast=1.05:brightness=0.005,unsharp=5:5:0.6:5:5:0.0,format=yuv420p" \
  -af "equalizer=f=2800:t=q:w=1.2:g=1.5,equalizer=f=250:t=q:w=1.0:g=-1.0,volume=-0.3dB" \
  -c:v libx264 -preset slow -crf 19 -r 30 -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT"
ffmpeg -nostats -i "$IN" -i "$OUT" -lavfi "[0:v]scale=540:960[a];[1:v]scale=540:960[b];[a][b]ssim" -f null - 2>&1 | grep -o "SSIM.*" | tail -1 || true
ffmpeg -nostats -i "$OUT" -map 0:a -af ebur128=peak=true -f null - 2>&1 | grep -E "^ +(I|Peak):" | tail -2
