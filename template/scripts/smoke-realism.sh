#!/bin/bash
# Realism V2 smoke tests (2026-11-21). Run from template/: bash scripts/smoke-realism.sh [play ids of a V2 episode...]
# 1) legacy plays render the same poses/ball as the pre-V2 engine  2) every V2 play passes the tactical tests and the
# contact QCs  3) the realism gates are printed for V2 and legacy (the A/B numbers; thresholds are reported, not all pass)
set -u
cd "$(dirname "$0")/.."
fail=0
npx tsx scripts/regress-poses.mts || fail=1
for id in "${@:-chicago-v2-a-trail chicago-v2-b-under}"; do
  for p in $id; do
    f=tactical/plays/$p.json
    npx tsx scripts/test-play.mts $f > /tmp/smoke-$p.log 2>&1; grep -q FAIL /tmp/smoke-$p.log && { echo "FAIL test-play $p"; fail=1; } || echo "PASS test-play $p"
    for q in qc-contact qc-catch qc-handoff; do
      npx tsx scripts/$q.mts $f > /tmp/smoke-$p-$q.log 2>&1; grep -q FAIL /tmp/smoke-$p-$q.log && { echo "FAIL $q $p"; fail=1; } || echo "PASS $q $p"
    done
    npx tsx scripts/qc-realism.mts $f --no-cloth | sed 's/^/  V2     /'
  done
done
exit $fail
