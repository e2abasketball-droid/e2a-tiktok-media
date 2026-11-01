#!/usr/bin/env bash
# Environment/network preflight for the Instagram pipeline. Exit 1 if a hard requirement fails.
fail=0
for t in node npm python3 ffmpeg; do command -v $t >/dev/null && echo "OK  $t $($t --version 2>&1 | head -1)" || { echo "FAIL $t missing"; fail=1; }; done
CH=$(ls /opt/pw-browsers/chromium-*/chrome-linux64/chrome 2>/dev/null | head -1)
[ -n "$CH" ] && echo "OK  chromium $CH" || { echo "FAIL chromium not found"; fail=1; }
for u in https://cdn.jsdelivr.net/gh/e2abasketball-droid/e2a-tiktok-media@main/README.md \
         https://raw.githubusercontent.com/e2abasketball-droid/e2a-tiktok-media/main/README.md \
         https://registry.npmjs.org/remotion https://pypi.org/simple/pip/ https://app.metricool.com; do
  c=$(curl -sL -o /dev/null -w '%{http_code}' --max-time 15 "$u"); [ "$c" = 200 ] && echo "OK  $c $u" || { echo "FAIL $c $u"; fail=1; }
done
exit $fail
