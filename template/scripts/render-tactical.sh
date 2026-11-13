#!/usr/bin/env bash
# Render a tactical episode end to end:
#   tactical tests -> engine QC -> narration with pauses -> music bed -> Remotion render (Tactical)
#   -> H.264 yuv420p + loudness -14 LUFS / -1.5 dBTP -> skill QC + contact sheet.
# Usage: scripts/render-tactical.sh tactical/episodes/<id>.json out/<id>.mp4 [--skip-voice] [--skip-music]
# Needs the narration already generated (voiceRaw + wordsRaw in the episode); never calls ElevenLabs.
set -euo pipefail
EP=$1; OUT=$2; shift 2
SKIP_VOICE=0; SKIP_MUSIC=0
for a in "$@"; do [ "$a" = --skip-voice ] && SKIP_VOICE=1; [ "$a" = --skip-music ] && SKIP_MUSIC=1; done
CHROME=${CHROME:-$(ls /opt/pw-browsers/chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell 2>/dev/null | head -1)}
ID=$(node -e "console.log(require('./$EP').id)")
DIR=public/tactical/$ID; mkdir -p "$DIR" "$(dirname "$OUT")"
TMP=$(mktemp -d)
PLAYS=$(node -e "const e=require('./$EP');console.log(Object.values(e.plays).map(p=>'tactical/plays/'+p+'.json').join(' '))")
echo "== tactical accuracy tests"; TACTICAL_REPORT="${OUT%.mp4}_tactical-tests.json" node --experimental-strip-types scripts/test-tactical.mts $PLAYS
if [ $SKIP_VOICE = 0 ]; then
  echo "== narration (pauses only, never sped up)"; python3 scripts/tactical-voice.py "$EP"
  VOICE=$(node -e "console.log(require('./$EP').voice)")
  ffmpeg -y -loglevel error -i "public/$VOICE" -af "highpass=f=80,equalizer=f=3200:t=q:w=1.0:g=2.0,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120,loudnorm=I=-16:TP=-2:LRA=7" -ac 1 -ar 44100 "$DIR/voice.mix.wav"
fi
WORDS=${EP%.json}.words.json
DUR=$(node -e "const e=require('./$EP');const w=require('./$WORDS');console.log((w.at(-1).end+e.tail).toFixed(3))")
if [ $SKIP_MUSIC = 0 ]; then
  echo "== music bed (E2A engine, ducked under the voice)"
  DROP=$(node scripts/tactical-cue.mjs "$EP" musicDrop)
  PAY=$(node scripts/tactical-cue.mjs "$EP" musicPayoff)
  python3 ../music/e2a_music.py --words "$WORDS" --story tactical --duration "$DUR" --voice "$DIR/voice.mix.wav" --out "$DIR/music.mp3" ${DROP:+--drop-at $DROP} ${PAY:+--payoff-at $PAY} --history "" >/dev/null
fi
node scripts/tactical-props.mjs "$EP" "$TMP/props.json" --music "$DIR/music.mp3"
echo "== engine QC (players in frame, camera smoothness, play clock)"; node --experimental-strip-types scripts/qc-tactical.mts "$TMP/props.json" "${OUT%.mp4}_qc-engine.json"
echo "== render"
npx remotion render src/index.ts Tactical "$TMP/raw.mp4" --props="$TMP/props.json" ${CHROME:+--browser-executable="$CHROME"} --codec=h264 --crf=16 --x264-preset=medium --concurrency=${CONCURRENCY:-4} --log=error
ffmpeg -y -loglevel error -i "$TMP/raw.mp4" -c:v libx264 -preset slow -crf ${CRF:-18} -pix_fmt yuv420p -profile:v high -movflags +faststart \
  -af "loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -c:a aac -b:a 192k "$OUT"
echo "== done: $OUT"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate:format=duration -of compact "$OUT"
