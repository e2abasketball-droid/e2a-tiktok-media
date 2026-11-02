#!/usr/bin/env bash
# Network + toolchain preflight for the Instagram routine. Exit 1 if any critical check fails.
fail=0
chk(){ code=$(curl -s -o /dev/null -L -m 20 -w '%{http_code}' "$1"); printf '%-55s %s\n' "$1" "$code"; [ "$code" -ge 200 ] && [ "$code" -lt 500 ] || fail=1; }
for u in https://cdn.jsdelivr.net/gh/e2abasketball-droid/e2a-tiktok-media@main/README.md \
 https://raw.githubusercontent.com/e2abasketball-droid/e2a-tiktok-media/main/README.md \
 https://registry.npmjs.org/remotion https://pypi.org/simple/faster-whisper/ \
 https://storage.googleapis.com https://www.googleapis.com https://api.elevenlabs.io https://app.metricool.com; do chk "$u"; done
for c in node npm ffmpeg python3; do command -v $c >/dev/null && echo "ok $c $($c --version 2>&1 | head -1)" || { echo "MISSING $c"; fail=1; }; done
echo "chrome: ${CHROME_BIN:-${PUPPETEER_EXECUTABLE_PATH:-none}}"
[ -d "$(dirname "$0")/../breakdown-template/node_modules" ] || echo "note: run 'npm ci || npm install' in instagram/breakdown-template"
exit $fail
