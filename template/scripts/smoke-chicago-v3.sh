#!/bin/bash
# Chicago V3 smoke (2026-11-22): every engine-side gate of the V3 reel, no render. Exit != 0 on the first hard failure.
#   bash scripts/smoke-chicago-v3.sh
set -e
cd "$(dirname "$0")/.."
N="node --experimental-strip-types --no-warnings"
python3 tactical/specs/_gen-chicago-v3.py > /dev/null
python3 tactical/episodes/_gen-chicago-v3.py > /dev/null
echo "== plays";       $N scripts/test-play.mts tactical/plays/chicago-v3-trail-drive.json tactical/plays/chicago-v3-under-three.json | tail -1
echo "== branches";    $N scripts/test-branches.mts tactical/plays/chicago-v3-trail-drive.json tactical/plays/chicago-v3-under-three.json | tail -1
echo "== contacts";    for s in qc-contact qc-catch qc-handoff; do $N scripts/$s.mts tactical/plays/chicago-v3-trail-drive.json tactical/plays/chicago-v3-under-three.json > /tmp/smoke-$s.log 2>&1 || { tail -5 /tmp/smoke-$s.log; exit 1; }; echo "$s PASS"; done
echo "== audio lock";  node scripts/test-audio-lock.mjs tactical/episodes/chicago-action-v3.json tactical/specs/_gen-chicago-v3.py tactical/episodes/_finish-chicago-v3.py | tail -1
# the guard must also FAIL when it should (changed hash / generation request / TTS endpoint in a pipeline script)
python3 -c "
import json;e=json.load(open('tactical/episodes/chicago-action-v3.json'));e['audioLock']['files']['tactical/chicago-v2/music.mp3']='0'*64;e['voiceRaw']='x.mp3';json.dump(e,open('/tmp/smoke-neg.json','w'))"
printf 'requests.post("https://api.elevenlabs.io/v1/text-to-speech/x")\n' > /tmp/smoke-bad.py
if node scripts/test-audio-lock.mjs /tmp/smoke-neg.json > /dev/null; then echo "audio guard did NOT catch a changed stem"; exit 1; fi
if node scripts/test-audio-lock.mjs tactical/episodes/chicago-action-v3.json /tmp/smoke-bad.py > /dev/null; then echo "audio guard did NOT catch a TTS endpoint"; exit 1; fi
echo "audio guard negative tests PASS"
echo "== episode";     $N scripts/qc-tactical3d.mts tactical/episodes/chicago-action-v3.json /tmp/smoke-qct3d.json | tail -1
$N scripts/qc-overlays.mts tactical/episodes/chicago-action-v3.json | grep -E "^(PASS|FAIL)"
echo "== regression";  npx tsx scripts/regress-poses.mts | tail -1
npx tsx scripts/regress-poses.mts --ref tactical/reports/chicago-v3-2026-11-22/regression-hashes-rv2.json | tail -1
echo "SMOKE CHICAGO V3 OK"
