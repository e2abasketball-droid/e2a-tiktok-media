#!/bin/bash
# V2 of Double Drag A = V1 + the re-rendered frames F0..F1 (only the payoff captions moved, QC-V1). The engine is a pure
# function of the frame (determinism test: isolated still vs sequential frame, PSNR 44 dB = codec only), so a range
# re-render splices without a seam. Audio = V1's (unchanged).
#   bash tactical/episodes/_splice-ddtr-v2.sh 420 510
set -euo pipefail
cd "$(dirname "$0")/../.."
F0=$1; F1=$2; W=out/ddtr
CHROME=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell
npx remotion render src/index.ts Tactical3DV2 $W/ddtr-main-a.part.mp4 --props=$W/ddtr-main-a.props.json --gl=swangle \
  --browser-executable=$CHROME --concurrency=4 --timeout=180000 --frames=$F0-$F1 > $W/ddtr-main-a.part.log 2>&1
ffmpeg -v error -y -i $W/ddtr-main-a.raw.mp4 -i $W/ddtr-main-a.part.mp4 -filter_complex \
 "[0:v]trim=end_frame=$F0,setpts=PTS-STARTPTS[a];[1:v]setpts=PTS-STARTPTS[b];[0:v]trim=start_frame=$((F1+1)),setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]" \
 -map "[v]" -map 0:a -c:v libx264 -preset slow -crf 14 -pix_fmt yuv420p -r 30 -c:a copy $W/ddtr-main-a.v2.raw.mp4
ffprobe -v error -count_frames -select_streams v -show_entries stream=nb_read_frames -of csv=p=0 $W/ddtr-main-a.v2.raw.mp4
