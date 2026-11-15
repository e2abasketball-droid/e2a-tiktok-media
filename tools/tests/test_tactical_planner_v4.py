"""E2A Tactical Studio V4 shadow planner tests (owner brief 2026-11-14 16:28Z): 4 full slots, 12 destinations,
collision, repetition, 5th video rejected, budget limits, revocation, dry run, and the separation between the
live V3 scope (2 videos, publishable under the pinned delegation) and the V4 shadow production (4, never
publishable).

  python3 -m unittest discover -s tools/tests -v
"""
import copy
import datetime as dt
import hashlib
import json
import os
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import tactical_studio as ts  # noqa: E402
import tactical_publisher as tp  # noqa: E402
import tactical_planner_v4 as pl  # noqa: E402

UTC = dt.timezone.utc
DAY = "2026-12-02"  # outside the 45-day window of every published play
LIVE = json.load(open(ts.OFFICIAL_CONFIG))
V4 = json.load(open(pl.PROFILE))
CONCEPTS = json.load(open(pl.CONCEPTS))
NOFLAG = os.path.join(tempfile.gettempdir(), "e2a-v4-no-such-flag")


def post(pid, when, nets=("instagram", "tiktok", "youtube"), kind="REEL"):
    return {"id": pid, "publicationDate": {"dateTime": when, "timezone": "Australia/Sydney"},
            "providers": [{"network": n, "status": "PENDING"} for n in nets], "instagramData": {"type": kind}}


def plan(readback=None, **kw):
    kw.setdefault("flag", NOFLAG)
    return pl.plan_day(DAY, readback or {"data": []}, c=copy.deepcopy(V4), concepts=CONCEPTS, **kw)


class FourSlots(unittest.TestCase):
    def test_four_full_slots_distinct_ids_and_formats(self):
        p = plan()
        self.assertEqual([v["status"] for v in p["videos"]], ["planned"] * 4)
        self.assertEqual([v["cid"] for v in p["videos"]], [f"E2A-TACTICAL-{DAY}-S0{n}" for n in (1, 2, 3, 4)])
        self.assertEqual([v["format"] for v in p["videos"]], list(pl.FORMATS))
        self.assertEqual(len({v["family"] for v in p["videos"]}), 4)

    def test_twelve_destinations_four_grouped_calls(self):
        p = plan()
        self.assertEqual(p["n_destinations"], 12)
        self.assertEqual(len(set(p["destinations"])), 12)
        self.assertEqual(p["create_calls_planned"], 4)

    def test_initial_grid_collides_with_own_trial_reels(self):
        """10/13/16/19 + the +2 h trial rule: each trial is 60 min before the next reel, so slots move."""
        p = plan()
        self.assertEqual([v["time"] for v in p["videos"]], ["10:00", "13:30", "17:00", "20:30"])
        q = plan(trial_reels=False)
        self.assertEqual([v["time"] for v in q["videos"]], ["10:00", "13:00", "16:00", "19:00"])
        s = pl.best_schedule()
        self.assertFalse(s["initial_10_13_16_19"]["valid_with_trial_reels"])
        self.assertEqual(len(s["with_trial_reels"]["slots"]), 4)


class Collisions(unittest.TestCase):
    def test_calendar_post_moves_or_empties_the_slot(self):
        rb = {"data": [post(1, f"{DAY}T16:10:00")]}
        p = plan(rb)
        v3 = p["videos"][2]
        self.assertTrue(v3["moved"])
        self.assertEqual(v3["blocked_by"][0]["metricool_id"], 1)
        t = dt.datetime.fromisoformat(f"{DAY}T{v3['time']}")
        self.assertGreater(abs((t - dt.datetime.fromisoformat(f"{DAY}T16:10")).total_seconds()), 3600)

    def test_static_and_trial_posts_block_too(self):
        rb = {"data": [post(2, f"{DAY}T10:30:00", ("instagram",), "TRIAL_REEL")]}
        self.assertTrue(plan(rb)["videos"][0]["moved"])

    def test_full_calendar_leaves_slot_empty(self):
        rb = {"data": [post(100 + i, f"{DAY}T{h:02d}:{m:02d}:00") for i, (h, m) in
                       enumerate((h, m) for h in range(7, 22) for m in (0, 30))]}
        p = plan(rb)
        self.assertTrue(all(v["status"] == "empty" for v in p["videos"]))
        self.assertEqual(p["n_destinations"], 0)
        self.assertEqual(p["create_calls_planned"], 0)

    def test_live_v3_slot_is_kept_not_duplicated(self):
        rb = {"data": [post(427791842, f"{DAY}T10:00:00"), post(427792201, f"{DAY}T13:00:00")]}
        p = plan(rb, live={1: 427791842, 2: 427792201})
        self.assertEqual([v["status"] for v in p["videos"]][:2], ["live_v3", "live_v3"])
        self.assertEqual(p["create_calls_planned"], 2)
        self.assertEqual(p["n_destinations"], 6)

    def test_unknown_post_in_live_slot_still_blocks(self):
        rb = {"data": [post(5, f"{DAY}T10:00:00")]}
        p = plan(rb, live={1: 999})
        self.assertNotEqual(p["videos"][0]["status"], "live_v3")


class Repetition(unittest.TestCase):
    def test_used_family_variant_is_skipped(self):
        first = next(k for k in CONCEPTS["concepts"] if k["format"] == "execution")
        used = [{"cid": "x", "date": "2026-11-30", "family": first["family"], "variant": first["variant"],
                 "concepts": first["concepts"], "play_id": first["id"]}]
        v = plan(used=used)["videos"][0]
        self.assertNotEqual(v["concept"], first["id"])
        self.assertEqual(v["skipped"][0]["id"], first["id"])

    def test_consecutive_days_never_repeat(self):
        days = pl.plan_range(DAY, 5, {"data": []}, c=copy.deepcopy(V4), concepts=CONCEPTS, flag=NOFLAG)
        ids = [v["concept"] for p in days for v in p["videos"] if v["status"] == "planned"]
        self.assertEqual(len(ids), 20)
        self.assertEqual(len(ids), len(set(ids)))

    def test_exhausted_format_leaves_slot_empty(self):
        days = pl.plan_range(DAY, 7, {"data": []}, c=copy.deepcopy(V4), concepts=CONCEPTS, flag=NOFLAG)
        self.assertTrue(all(v["status"] == "empty" for v in days[6]["videos"]))  # 6 concepts per format

    def test_published_history_blocks(self):
        used = [{"cid": "E2A-TACTICAL-2026-11-15-V02", "date": "2026-11-15", "family": "ICE coverage",
                 "variant": "ice the side ball screen to the baseline", "concepts": ["ice"], "play_id": "x"}]
        p = pl.plan_day("2026-11-20", {"data": []}, used, c=copy.deepcopy(V4), concepts=CONCEPTS, flag=NOFLAG)
        self.assertNotEqual(p["videos"][1]["concept"], "ice-side-pnr")


class Limits(unittest.TestCase):
    def test_fifth_video_is_rejected(self):
        p = plan(requested=5)
        self.assertEqual(len(p["videos"]), 4)
        self.assertEqual([r["n"] for r in p["rejected"]], [5])

    def test_fewer_requested(self):
        p = plan(requested=2)
        self.assertEqual(len(p["videos"]), 2)
        self.assertEqual(p["rejected"], [])

    def test_budget_fits_four_measured_videos(self):
        b = plan()["budget"]
        self.assertTrue(b["ok"], b["over"])
        self.assertEqual(b["need"]["voice_credits"], 4 * 508)
        self.assertEqual(b["need"]["scribe_credits"], 4 * 166)

    def test_budget_reports_exact_shortfall(self):
        c = copy.deepcopy(V4)
        c["budget_per_day"]["voice_credits"] = 1200  # the live V3 day budget
        b = pl.budget(4, c)
        self.assertFalse(b["ok"])
        self.assertEqual(b["over"]["voice_credits"]["missing"], 4 * 508 - 1200)

    def test_spend_guard_refuses_past_limit(self):
        spent = {}
        for _ in range(6):
            pl.spend_guard(spent, "create_calls", 1, V4)
        with self.assertRaises(pl.PlanError):
            pl.spend_guard(spent, "create_calls", 1, V4)
        with self.assertRaises(pl.PlanError):
            pl.spend_guard({}, "unknown_kind", 1, V4)


class Revocation(unittest.TestCase):
    def test_revocation_flag_stops_planning(self):
        with tempfile.TemporaryDirectory() as td:
            flag = os.path.join(td, "REVOKED")
            open(flag, "w").close()
            with self.assertRaises(pl.PlanError):
                plan(flag=flag)

    def test_revoked_status_stops_planning(self):
        c = copy.deepcopy(V4)
        c["status"] = "REVOKED by the owner"
        with self.assertRaises(pl.PlanError):
            pl.plan_day(DAY, {"data": []}, c=c, concepts=CONCEPTS, flag=NOFLAG)

    def test_publishing_profile_is_refused(self):
        for mut in (lambda c: c["publishing"].update(mode="direct_delegated"),
                    lambda c: c["delegation"].update(verifier="delegation"),
                    lambda c: c.update(content_id="E2A-TACTICAL-{date}-V{n:02d}")):
            c = copy.deepcopy(V4)
            mut(c)
            with self.assertRaises(pl.PlanError):
                pl.plan_day(DAY, {"data": []}, c=c, concepts=CONCEPTS, flag=NOFLAG)


class DryRun(unittest.TestCase):
    def test_plan_is_dry_and_writes_nothing(self):
        p = plan()
        self.assertTrue(p["dry_run"])
        self.assertEqual(p["writes"], [])
        self.assertEqual(p["mode"], "shadow")

    def test_planner_has_no_metricool_write_path(self):
        src = open(pl.__file__).read()
        for w in ("createScheduledPost", "updateScheduledPost", "metricool_create", "import tactical_publisher"):
            self.assertNotIn(w, src)

    def test_cli_dry_run(self):
        with tempfile.TemporaryDirectory() as td:
            rb = os.path.join(td, "rb.json")
            json.dump({"data": []}, open(rb, "w"))
            out = os.path.join(td, "plan.json")
            with mock.patch.object(pl, "REVOKED_FLAG", NOFLAG), mock.patch("sys.stdout"):
                pl.main(["plan", DAY, "--readback", rb, "--out", out])
            self.assertEqual(json.load(open(out))[0]["n_destinations"], 12)


class LiveScopeUnchanged(unittest.TestCase):
    """The V3 publisher keeps exactly its 2-video scope; nothing in V4 can widen it."""

    def test_live_config_is_still_two_slots(self):
        self.assertEqual(ts.slot_numbers(LIVE), (1, 2))
        self.assertEqual([LIVE["slots"][k]["time"] for k in ("1", "2")], ["10:00", "13:00"])
        self.assertEqual(LIVE["content_id"], "E2A-TACTICAL-{date}-V{n:02d}")

    def test_committed_delegation_untouched(self):
        raw = open(os.path.join(ts.ROOT, "config", "delegation.tactical-studio.json"), "rb").read()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), "d5be6cd2da285097cf90bf9e1ed9b88856a63202631416422b34b7ffdedb1a27")

    def _deleg(self):
        d = json.load(open(os.path.join(ts.ROOT, "config", "delegation.tactical-studio.json")))
        b = json.dumps(d).encode()
        return d, hashlib.sha256(b).hexdigest()

    def test_publisher_rejects_shadow_profile_scope(self):
        d, sha = self._deleg()
        now = dt.datetime(2026, 11, 16, 6, 0, tzinfo=UTC)
        tp.check_delegation(d, sha, sha, now, c=copy.deepcopy(LIVE), cid="E2A-TACTICAL-2026-11-17-V02")  # live: ok
        with self.assertRaises(tp.PublishError):
            tp.check_delegation(d, sha, sha, now, c=copy.deepcopy(V4))

    def test_publisher_rejects_shadow_ids_and_third_video(self):
        d, sha = self._deleg()
        now = dt.datetime(2026, 11, 16, 6, 0, tzinfo=UTC)
        for cid in ("E2A-TACTICAL-2026-11-17-S01", "E2A-TACTICAL-2026-11-17-V03", "E2A-TACTICAL-2026-11-17-V00"):
            with self.assertRaises(tp.PublishError, msg=cid):
                tp.check_delegation(d, sha, sha, now, c=copy.deepcopy(LIVE), cid=cid)

    def test_four_slot_live_config_needs_a_new_delegation(self):
        """Even if someone puts 4 slots in the LIVE config, the granted 2-slot delegation refuses it."""
        d, sha = self._deleg()
        c = copy.deepcopy(LIVE)
        c["slots"].update({"3": {"time": "16:00"}, "4": {"time": "19:00"}})
        with self.assertRaises(tp.PublishError):
            tp.check_delegation(d, sha, sha, dt.datetime(2026, 11, 16, 6, 0, tzinfo=UTC), c=c, cid="E2A-TACTICAL-2026-11-17-V01")

    def test_cid_parser(self):
        self.assertEqual(ts.parse_cid("E2A-TACTICAL-2026-11-17-V02"), (dt.date(2026, 11, 17), 2))
        self.assertEqual(ts.parse_cid("E2A-TACTICAL-2026-11-17-S04", V4), (dt.date(2026, 11, 17), 4))
        for bad in ("E2A-TACTICAL-2026-11-17-V2", "E2A-TACTICAL-2026-11-17-X01", "E2A-TACTICAL-2026-11-17-V00", None):
            with self.assertRaises(ts.StudioError):
                ts.parse_cid(bad)
        with self.assertRaises(ts.StudioError):
            ts.parse_cid("E2A-TACTICAL-2026-11-17-S01", LIVE)  # shadow id against live config
        with self.assertRaises(ts.StudioError):
            ts.parse_cid("E2A-TACTICAL-2026-11-17-V03", LIVE)  # third slot does not exist live
        with self.assertRaises(ts.StudioError):
            ts.parse_cid("E2A-TACTICAL-2026-11-17-S05", V4)  # fifth slot does not exist in V4


if __name__ == "__main__":
    unittest.main()
