#!/usr/bin/env bash
# Usage: check-media-url.sh <url>  — follows redirects, reports final status/type/size.
set -u
u="${1:?url}"
curl -sSL --max-time 30 -o /dev/null -w "final_status=%{http_code} type=%{content_type} bytes=%{size_download} redirects=%{num_redirects} url=%{url_effective}\n" "$u"
