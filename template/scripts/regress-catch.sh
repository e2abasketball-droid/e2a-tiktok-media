#!/bin/bash
# Regression (Double Drag V2, 2026-11-20, owner brief sec. 7 "prueba de contacto"): a pass THROUGH a body must FAIL.
# tactical/regress/regress-pass-through-body.json = ddtr-a-roll with X5 parked on the pass line at chest height.
# Exit 0 only if qc-catch rejects it on ball_torso naming X5 (and still accepts the real plays).
cd "$(dirname "$0")/.."
out=$(node --experimental-strip-types scripts/qc-catch.mts tactical/regress/regress-pass-through-body.json 2>/dev/null); rc=$?
echo "$out" | grep "trunk"
if [ $rc -ne 0 ] && echo "$out" | grep -q "FAIL .*ball never sinks into a trunk.*X5@"; then echo "REGRESSION OK: pass through X5's body rejected"; else echo "REGRESSION BROKEN: qc-catch accepted a pass through a body"; exit 1; fi
node --experimental-strip-types scripts/qc-catch.mts tactical/plays/ddtr-a-roll.json tactical/plays/ddtr-b-skip.json >/dev/null 2>&1 && echo "real plays still PASS" || { echo "real plays FAIL"; exit 1; }
