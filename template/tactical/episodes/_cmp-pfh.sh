#!/bin/bash
# keep | give side-by-side (left keep, right give), from out/pfh/pfh-cmp-*.raw.mp4 (frames 0-119 of each props).
#   bash tactical/episodes/_cmp-pfh.sh <deliver_dir>
set -euo pipefail
cd "$(dirname "$0")/../.."
O=$1; W=out/pfh; mkdir -p "$O"
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
# clean: no text, no graphic, no audio (the test the brief asks for: can you tell keep from give?)
ffmpeg -v error -y -i $W/pfh-cmp-keep-clean.raw.mp4 -i $W/pfh-cmp-give-clean.raw.mp4 -filter_complex \
  "[0:v]scale=540:960[a];[1:v]scale=540:960[b];[a][b]hstack=inputs=2,pad=1080:1920:0:480:black[v]" \
  -map "[v]" -an -c:v libx264 -crf 16 -pix_fmt yuv420p -r 30 "$O/E2A-pfh-test-keep-vs-give-sin-overlays.mp4"
# hands: close 3/4, engine phase box (phase, owner, play time S) + edit time E and S frame burnt in the bottom band
ffmpeg -v error -y -i $W/pfh-cmp-keep-hands.raw.mp4 -i $W/pfh-cmp-give-hands.raw.mp4 -filter_complex \
  "[0:v]scale=540:960[a];[1:v]scale=540:960[b];[a][b]hstack=inputs=2,pad=1080:1920:0:480:black,\
drawtext=fontfile=$FONT:fontsize=40:fontcolor=white:x=40:y=1500:text='E %{pts\\:flt} s',\
drawtext=fontfile=$FONT:fontsize=40:fontcolor=0xFFD34D:x=40:y=1560:text='S %{eif\\:30+n*36/120\\:d}  (0.30x, S030 -> S066)',\
drawtext=fontfile=$FONT:fontsize=34:fontcolor=white:x=40:y=1640:text='left KEEP (O2 keeps it)   right GIVE (hand-off to O1)'[v]" \
  -map "[v]" -an -c:v libx264 -crf 16 -pix_fmt yuv420p -r 30 "$O/E2A-pfh-test-keep-vs-give-manos-fase.mp4"
echo "$O"
