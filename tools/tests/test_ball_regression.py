"""Regression (2026-11-15): ball jumps found by test-ball.mts in the V4 audit. The fix is in the shared sampler
(template/src/tactical/play.ts): the passer's square-up is eased in, the gather window never exceeds the hold, and a
dribble ends at the pick-up before a shot or layup. Published MP4s are not re-rendered or edited."""
import os
import shutil
import subprocess
import unittest

T = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "template")


def ball(play):
    r = subprocess.run(["node", "--experimental-strip-types", "scripts/test-ball.mts", f"tactical/plays/{play}.json"],
                       cwd=T, capture_output=True, text=True)
    return r.stdout


@unittest.skipUnless(shutil.which("node") and os.path.isdir(os.path.join(T, "node_modules")), "node + template deps")
class BallJumps(unittest.TestCase):
    def test_no_jump_at_contacts(self):
        for play in ("hammer-b-rim", "spain-a-roll", "elevator-a-chase", "example-pin-down"):
            out = ball(play)
            self.assertIn("PASS  [%s] ball path continuous" % play, out, play)

    def test_hammer_dribble_bounces_reach_the_floor(self):
        self.assertIn("PASS  [hammer-b-rim] dribble O1", ball("hammer-b-rim"))


if __name__ == "__main__":
    unittest.main()
