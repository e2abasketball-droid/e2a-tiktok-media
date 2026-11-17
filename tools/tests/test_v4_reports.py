"""V4 retention report and common-master sheet tests."""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import retention_report as rr  # noqa: E402
import master_sheet as ms  # noqa: E402
import tactical_studio as ts  # noqa: E402

SNAP = os.path.join(ts.ROOT, "produccion", "tactical", "v4", "retencion", "snapshot-2026-11-14T1655Z.json")


class Retention(unittest.TestCase):
    def test_ratios_use_reach_and_duration_never_views(self):
        rows = {r["key"]: r for r in rr.instagram_rows(json.load(open(SNAP)))}
        s = rows["stagger-v2"]
        self.assertEqual(s["avg_watch_pct"], round(100 * 17.744 / 33.344, 1))
        self.assertIn("reach=46359", s["denominator"])
        self.assertNotIn("views", json.dumps(s))

    def test_missing_metrics_are_labelled(self):
        snap = json.load(open(SNAP))
        snap["registry"][2]["duration_s"] = None
        rows = {r["key"]: r for r in rr.instagram_rows(snap)}
        self.assertTrue(str(rows["stagger-v2"]["avg_watch_pct"]).startswith("MISSING"))
        self.assertEqual(rows["stagger-v2"]["retention_IGRE27"], "MISSING")
        rep = rr.report([SNAP])
        self.assertTrue(any("tiktok" in m for m in rep["missing"]))

    def test_windows_and_no_winner(self):
        self.assertEqual(rr.window_of(25), "24h")
        self.assertEqual(rr.window_of(70), "72h")
        self.assertEqual(rr.window_of(170), "7d")
        self.assertTrue(rr.window_of(40).startswith("other"))
        self.assertTrue(rr.report([SNAP])["verdict"].startswith("no winner"))


@unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg needed")
class Sheet(unittest.TestCase):
    def test_sheet_binds_play_and_media_and_detects_changes(self):
        with tempfile.TemporaryDirectory() as td:
            soc, crs = os.path.join(td, "s.mp4"), os.path.join(td, "c.mp4")
            for p, size in ((soc, "1080x1920"), (crs, "1280x720")):
                subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", f"color=c=black:s={size}:d=0.2:r=30", p], check=True)
            path, s = ms.make("ram-v2-a-drop", soc, None, crs, {"from": 0, "to": 6.6}, out=td)
            self.assertTrue(path.endswith("ram-v2-a-drop@" + s["play_sha256"][:8] + ".json"))
            self.assertTrue(s["outputs"]["social_9x16"]["profile_ok"] and s["outputs"]["course_16x9"]["profile_ok"])
            self.assertTrue(ms.check(path, td)["ok"])
            open(crs, "ab").write(b"x")
            self.assertFalse(ms.check(path, td)["ok"])


if __name__ == "__main__":
    unittest.main()
