#!/usr/bin/env bash
# Usage: check-media-url.sh <url> [expected-content-type-prefix]
# Verifies a media URL is publicly reachable (follows redirects) and returns a sane type/size.
set -euo pipefail
url="$1"; want="${2:-}"
out=$(curl -sSL -o /dev/null -m 30 -w '%{http_code} %{content_type} %{size_download}' -r 0-1048575 "$url")
read -r code ctype size <<<"$out"
echo "$url -> $code $ctype ${size}B"
[[ "$code" == 200 || "$code" == 206 ]] || { echo "FAIL: HTTP $code"; exit 1; }
[[ -z "$want" || "$ctype" == "$want"* ]] || { echo "FAIL: content-type $ctype != $want*"; exit 1; }
[[ "$size" -gt 0 ]] || { echo "FAIL: empty body"; exit 1; }
echo OK
