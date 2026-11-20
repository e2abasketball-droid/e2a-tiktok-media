#!/bin/bash
# Regression (Double Drag V2, 2026-11-20, owner brief sec. 7 "prueba de contacto"): a pass THROUGH a body must FAIL.
# tactical/regress/regress-pass-through-body.json = ddtr-a-roll with X5 parked on the pass line at chest height.
# Exit 0 only if qc-catch rejects it on ball_torso naming X5 (and still accepts the real plays).
cd "$(dirname "$0")/.."
out=$(node --experimental-strip-types scripts/qc-catch.mts tactical/regress/regress-pass-through-body.json 2>/dev/null); rc=$?
echo "$out" | grep "trunk"
if [ $rc -ne 0 ] && echo "$out" | grep -q "FAIL .*ball never sinks into a trunk.*X5@"; then echo "REGRESSION OK: pass through X5's body rejected"; else echo "REGRESSION BROKEN: qc-catch accepted a pass through a body"; exit 1; fi
# (2026-11-20, pass + audio fix) the phased skip: X4 parked on O1's two-hand pocket S074-S084 -> ball inside X4's trunk
out2=$(node --experimental-strip-types scripts/qc-catch.mts tactical/regress/regress-skip-ball-in-body.json 2>/dev/null); rc2=$?
echo "$out2" | grep "trunk"
if [ $rc2 -ne 0 ] && echo "$out2" | grep -q "FAIL .*ball never sinks into a trunk.*X4@"; then echo "REGRESSION OK: ball inside X4's body during the skip gather rejected"; else echo "REGRESSION BROKEN: qc-catch accepted a ball inside a body (skip gather)"; exit 1; fi
node --experimental-strip-types scripts/qc-catch.mts tactical/plays/ddtr-a-roll.json tactical/plays/ddtr-b-skip.json >/dev/null 2>&1 && echo "real plays still PASS" || { echo "real plays FAIL"; exit 1; }
# (2026-11-20, Pistol Fake Handoff) clean vs deliberately defective hand-off cases (scripts/qc-handoff.mts):
#  - regress-pfh-keep-owner-change: the ball changes owner during the fake (O2 -> O1 -> O2) -> 'one owner' must FAIL
#  - regress-pfh-hand-in-ball: play.handBallClear off -> fingers inside someone else's ball -> must FAIL
out3=$(node --experimental-strip-types scripts/qc-handoff.mts tactical/regress/regress-pfh-keep-owner-change.json 2>/dev/null); rc3=$?
echo "$out3" | grep "one owner"
if [ $rc3 -ne 0 ] && echo "$out3" | grep -q "FAIL .*one owner O2"; then echo "REGRESSION OK: owner change during the fake rejected"; else echo "REGRESSION BROKEN: qc-handoff accepted an owner change in keep"; exit 1; fi
out4=$(node --experimental-strip-types scripts/qc-handoff.mts tactical/regress/regress-pfh-hand-in-ball.json 2>/dev/null); rc4=$?
echo "$out4" | grep "fingers inside"
if [ $rc4 -ne 0 ] && echo "$out4" | grep -q "FAIL .*no fingers inside"; then echo "REGRESSION OK: fingers inside the ball rejected"; else echo "REGRESSION BROKEN: qc-handoff accepted fingers inside the ball"; exit 1; fi
node --experimental-strip-types scripts/qc-handoff.mts tactical/plays/pfh-keep.json tactical/plays/pfh-give.json >/dev/null 2>&1 && echo "pfh plays still PASS (qc-handoff)" || { echo "pfh plays FAIL (qc-handoff)"; exit 1; }
