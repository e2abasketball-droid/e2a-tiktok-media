#!/usr/bin/env python3
"""Safety, duplicate, recovery and quality tests for tools/tactical_studio.py (owner brief Phase 15).
Local doubles only: no Metricool, ElevenLabs or GitHub calls.  Run: python3 tools/tests/test_tactical_studio.py"""
import datetime as dt
import json
import multiprocessing as mp
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import tactical_studio as ts  # noqa: E402

UTC = dt.timezone.utc
CID1 = "E2A-TACTICAL-2026-11-20-V01"
CID2 = "E2A-TACTICAL-2026-11-20-V02"


def walk(s, cid, upto, tmp):
    """Move a video through the flow up to `upto` (inclusive) with dummy artifacts."""
    for st in ts.FLOW[: ts.FLOW.index(upto) + 1]:
        if s.state(cid) is not None and ts.FLOW.index(s.state(cid)) >= ts.FLOW.index(st):
            continue
        if st == "authorised":
            s.authorise(cid, lambda scope: (True, "test delegation"), f"{cid}:{st}")
            continue
        art = {}
        if st == "audio_ready":
            p = os.path.join(tmp, f"{cid}-voice.mp3")
            open(p, "wb").write(b"ID3 fake narration")
            art = {"voice": p}
        s.advance(cid, st, f"{cid}:{st}", art, {"script_key": ts.Studio.voice_key("frozen script")} if st == "audio_ready" else None)


def _race(args):
    d, cid, net, op = args
    try:
        ts.Studio(d).reserve(cid, net, op)
        return "ok"
    except ts.StudioError:
        return "refused"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.s = ts.Studio(os.path.join(self.tmp, "state"))


class TestCalendar(Base):
    def test_J_dst_aedt_and_aest(self):
        # 20 Nov 2026 is AEDT (UTC+11); 20 May 2027 is AEST (UTC+10): same wall clock, different UTC
        self.assertEqual(ts.slot_instant("2026-11-20", 1).astimezone(UTC).hour, 23)   # 10:00 AEDT = 23:00Z day before
        self.assertEqual(ts.slot_instant("2027-05-20", 1).astimezone(UTC).hour, 0)    # 10:00 AEST = 00:00Z
        self.assertEqual(ts.slot_instant("2027-05-20", 2).astimezone(UTC).hour, 3)    # 13:00 AEST
        # DST change day (Sun 4 Apr 2027, 03:00 → 02:00): the slots still land on that local date
        self.assertEqual(ts.slot_instant("2027-04-04", 1).astimezone(ts.sydney()).date().isoformat(), "2027-04-04")

    def test_J_target_date_uses_sydney_not_utc(self):
        # 17:00 Sydney on 19 Nov = 06:00Z 19 Nov → produce for 20 Nov
        self.assertEqual(ts.target_date(dt.datetime(2026, 11, 19, 6, 0, tzinfo=UTC)).isoformat(), "2026-11-20")
        # 08:00 Sydney on 20 Nov = 21:00Z 19 Nov → still the same day (before the 09:00 cutoff)
        self.assertEqual(ts.target_date(dt.datetime(2026, 11, 19, 21, 0, tzinfo=UTC)).isoformat(), "2026-11-20")

    def test_content_ids(self):
        self.assertEqual(ts.content_id("2026-11-20", 1), CID1)
        self.assertEqual(ts.parse_cid(CID2), (dt.date(2026, 11, 20), 2))
        with self.assertRaises(ts.StudioError):
            ts.parse_cid("E2A-TT-0019")


class TestStateMachine(Base):
    def test_order_enforced(self):
        self.s.advance(CID1, "candidate", "op1")
        with self.assertRaises(ts.StudioError):
            self.s.advance(CID1, "rendered", "op2")  # cannot skip phases

    def test_idempotent_ops(self):
        self.s.advance(CID1, "candidate", "op1")
        self.assertTrue(self.s.advance(CID1, "candidate", "op1")["idempotent"])
        with self.assertRaises(ts.StudioError):
            self.s.advance(CID1, "researched", "op1")  # same op, other target

    def test_resume_after_failure_and_no_loops(self):
        walk(self.s, CID1, "audio_ready", self.tmp)
        self.s.fail(CID1, "rendered", "remotion crashed")
        self.assertEqual(self.s.next_phase(CID1), {"action": "retry", "phase": "rendered"})
        self.s.fail(CID1, "rendered", "remotion crashed again")
        self.assertEqual(self.s.next_phase(CID1)["action"], "stop")

    def test_truncated_line_ignored(self):
        self.s.advance(CID1, "candidate", "op1")
        with open(self.s.log, "a") as f:
            f.write('{"kind": "state", "cid": "E2A-TAC')  # cut mid-write
        self.assertEqual(self.s.state(CID1), "candidate")

    def test_usage_limit_wait(self):
        self.s.advance(CID1, "candidate", "op1")
        later = (dt.datetime.now(UTC) + dt.timedelta(hours=2)).isoformat()
        self.s.fail(CID1, "researched", "USAGE_LIMIT_REACHED", retry_after=later)
        self.assertEqual(self.s.next_phase(CID1)["action"], "wait")


class TestD_VoiceNeverPaidTwice(Base):
    def test_resume_reuses_narration(self):
        walk(self.s, CID1, "audio_ready", self.tmp)
        # the session dies here; a new run (new Studio object) resumes
        s2 = ts.Studio(self.s.dir)
        hit = s2.voice_lookup(CID1, "frozen   script\n")
        self.assertTrue(hit["reuse"], hit)
        self.assertEqual(s2.next_phase(CID1), {"action": "run", "phase": "rendered"})

    def test_changed_script_is_not_reused(self):
        walk(self.s, CID1, "audio_ready", self.tmp)
        self.assertFalse(self.s.voice_lookup(CID1, "a different script")["reuse"])

    def test_tampered_audio_is_not_reused(self):
        walk(self.s, CID1, "audio_ready", self.tmp)
        open(os.path.join(self.tmp, f"{CID1}-voice.mp3"), "ab").write(b"x")
        self.assertFalse(self.s.voice_lookup(CID1, "frozen script")["reuse"])


class TestC_Duplicates(Base):
    def test_second_reservation_refused(self):
        self.s.reserve(CID1, "tiktok", "run-A")
        self.assertTrue(self.s.reserve(CID1, "tiktok", "run-A")["idempotent"])
        with self.assertRaises(ts.StudioError):
            self.s.reserve(CID1, "tiktok", "run-B")

    def test_two_simultaneous_runs(self):
        with mp.Pool(8) as pool:
            res = pool.map(_race, [(self.s.dir, CID1, "instagram", f"run-{i}") for i in range(8)])
        self.assertEqual(res.count("ok"), 1, res)
        self.assertEqual(len(self.s.events(CID1, "reservation")), 1)

    def test_key_format(self):
        self.assertEqual(ts.Studio.slot_key(CID2, "youtube"), f"{CID2}:youtube:2026-11-20:13:00")


def good_reports(d):
    os.makedirs(d, exist_ok=True)
    rep = {
        "tactical": {"passed": 40, "failed": 0},
        "engine": {"passed": 9, "failed": 0},
        "audio": {"mix": {"I": -14.3, "TP": -2.2}, "worst_sfx_vs_word_db": -3.1, "silences_inside_narration": []},
        "technical": {"width": 1080, "height": 1920, "fps": 30, "vcodec": "h264", "acodec": "aac", "duration": 36.2,
                      "black_frames": 0, "social_mb": 9.3},
        "frames": {"extracted_from_mp4": True, "count": 12, "issues": []},
        "licences": {"pass": True, "failures": []},
    }
    for k, v in rep.items():
        json.dump(v, open(os.path.join(d, f"{k}.json"), "w"))
    return rep


class TestQuality(Base):
    def test_all_good_is_pass(self):
        d = os.path.join(self.tmp, "qc")
        good_reports(d)
        self.assertEqual(ts.qc_aggregate(d)["result"], "QC_PASS")

    def test_E_render_failure_blocks_publication(self):
        d = os.path.join(self.tmp, "qc")
        good_reports(d)
        os.remove(os.path.join(d, "technical.json"))  # the render crashed: no MP4, no technical report
        q = ts.qc_aggregate(d)
        self.assertEqual(q["result"], "QC_FAIL")
        walk(self.s, CID1, "rendered", self.tmp)
        with self.assertRaises(ts.StudioError):
            self.s.advance(CID1, "asset_ready", "skip-qc")  # cannot jump over qc_passed

    def test_K_tactically_wrong_play_blocked(self):
        d = os.path.join(self.tmp, "qc")
        good_reports(d)
        json.dump({"passed": 39, "failed": 1}, open(os.path.join(d, "tactical.json"), "w"))
        self.assertEqual(ts.qc_aggregate(d)["result"], "QC_FAIL")

    def test_audio_rules(self):
        d = os.path.join(self.tmp, "qc")
        good_reports(d)
        json.dump({"mix": {"I": -14.0, "TP": -0.5}, "worst_sfx_vs_word_db": -3}, open(os.path.join(d, "audio.json"), "w"))
        self.assertEqual(ts.qc_aggregate(d)["result"], "QC_FAIL")  # true peak above -1 dBTP
        json.dump({"mix": {"I": -14.0, "TP": -2}, "worst_sfx_vs_word_db": 1.0}, open(os.path.join(d, "audio.json"), "w"))
        self.assertEqual(ts.qc_aggregate(d)["result"], "QC_FAIL")  # an effect louder than a word

    def test_duration_window(self):
        d = os.path.join(self.tmp, "qc")
        r = good_reports(d)
        r["technical"]["duration"] = 44.0
        json.dump(r["technical"], open(os.path.join(d, "technical.json"), "w"))
        self.assertEqual(ts.qc_aggregate(d)["result"], "QC_FAIL")


class TestL_Licences(unittest.TestCase):
    def test_unknown_origin_fails(self):
        r = ts.licence_check({"assets": [{"src": "sfx/whoosh.mp3"}, {"src": "media/some-photo.jpg"}]})
        self.assertFalse(r["pass"])
        self.assertEqual(r["failures"][0]["src"], "media/some-photo.jpg")

    def test_owned_assets_pass(self):
        r = ts.licence_check({"assets": [{"src": "sfx/whoosh.mp3"}, {"src": "music/synth/drive_a.mp3"}, {"src": "anton.woff2"}]})
        self.assertTrue(r["pass"], r)

    def test_unconfirmed_elevenlabs_fails_until_owner_confirms(self):
        r = ts.licence_check({"assets": [{"src": "music/cinematic/cine-09.mp3"}]})
        self.assertFalse(r["pass"])


class TestG_H_Authorisation(Base):
    def test_G_blocked_verifier_cannot_authorise(self):
        walk(self.s, CID1, "asset_ready", self.tmp)
        with self.assertRaises(ts.StudioError):
            self.s.authorise(CID1, ts.blocked_verifier, "auth-1")
        self.assertEqual(self.s.state(CID1), "asset_ready")

    def test_G_revoked_delegation(self):
        walk(self.s, CID1, "asset_ready", self.tmp)
        revoked = lambda scope: (False, "delegation revoked by the owner")  # noqa: E731
        with self.assertRaises(ts.StudioError):
            self.s.authorise(CID1, revoked, "auth-1")

    def test_G_no_reservation_before_authorised_flow(self):
        # scheduling needs `authorised`: without it there is no path to scheduled_*
        walk(self.s, CID1, "asset_ready", self.tmp)
        with self.assertRaises(ts.StudioError):
            self.s.advance(CID1, "scheduled_partial", "x")

    def test_H_routine_has_no_direct_write_tool(self):
        cfg = json.load(open(os.path.join(ts.ROOT, "config", "routine.tactical-studio.json")))
        writes = set(cfg["metricool_write_tools"])
        for t in cfg["tasks"]:
            allowed = set(t["connectors"].get("Metricool-Social-Media-Management", {}).get("permitted_tools", []))
            self.assertTrue(allowed, f"{t['name']}: an empty list would mean ALL tools")
            self.assertLessEqual(allowed & writes, {cfg["allowed_write_tool"]}, t["name"])
            self.assertIn("Claude_Code_Remote", " ".join(t["never_attach"]))
        check = next(t for t in cfg["tasks"] if t["name"].endswith("CHECK"))
        self.assertFalse(set(check["connectors"]["Metricool-Social-Media-Management"]["permitted_tools"]) & writes)

    def test_H_config_shadow(self):
        c = ts.cfg()
        self.assertEqual(c["publishing"]["mode"], "shadow")
        self.assertIn("createScheduledPost", c["publishing"]["never"])
        self.assertEqual(c["delegation"]["verifier"], "blocked")


class TestM_Budget(Base):
    def test_over_limit_blocked(self):
        self.s.spend(CID1, "voice_credits", 500, "v1")
        self.s.spend(CID2, "voice_credits", 500, "v2")
        self.assertTrue(self.s.spend(CID2, "voice_credits", 500, "v2")["idempotent"])
        with self.assertRaises(ts.StudioError):
            self.s.spend(CID2, "voice_credits", 500, "v2-retake")  # 1,500 > 1,200

    def test_no_music_generation(self):
        with self.assertRaises(ts.StudioError):
            self.s.spend(CID1, "music_generations", 1, "m1")


def readback(posts):
    return {"data": posts}


def post(pid, nets, slot="2026-11-20T10:00:00", text="caption", status="PENDING"):
    return {"id": pid, "uuid": f"u{pid}", "publicationDate": {"dateTime": slot, "timezone": "Australia/Sydney"},
            "text": text, "providers": [{"network": n, "status": status} for n in nets], "instagramData": {"type": "REEL"}}


class TestF_N_Confirmation(Base):
    def setUp(self):
        super().setUp()
        walk(self.s, CID1, "authorised", self.tmp)
        self.pkg = ts.package(CID1, "https://raw.githubusercontent.com/x/y/abc/v.mp4", "caption",
                              {"tiktok": "t", "youtube": "The Spain PnR #shorts"})

    def test_N_only_with_three_networks(self):
        r = ts.confirm(self.s, CID1, {"data": {"id": 7, "uuid": "u7"}}, readback([post(7, ["instagram", "tiktok"])]), self.pkg)
        self.assertEqual(r["state"], "scheduled_partial")
        self.assertEqual(r["missing"], ["youtube"])
        r = ts.confirm(self.s, CID1, {"data": {"id": 7, "uuid": "u7"}}, readback([post(7, ["instagram", "tiktok", "youtube"])]), self.pkg)
        self.assertEqual(r["state"], "scheduled_confirmed")

    def test_F_one_network_fails_others_kept(self):
        p = post(7, ["instagram", "youtube"])
        p["providers"].append({"network": "tiktok", "status": "ERROR", "detailedStatus": "token expired"})
        r = ts.confirm(self.s, CID1, {"data": {"id": 7}}, readback([p]), self.pkg)
        self.assertEqual(r["confirmed"], ["instagram", "youtube"])
        self.assertTrue(any("tiktok" in x for x in r["problems"]))
        n = len(self.s.events(CID1, "confirmation"))
        ts.confirm(self.s, CID1, {"data": {"id": 7}}, readback([p]), self.pkg)
        self.assertEqual(len(self.s.events(CID1, "confirmation")), n)  # never re-recorded

    def test_invented_id_cannot_confirm(self):
        r = ts.confirm(self.s, CID1, {"data": {"id": 999}}, readback([post(7, ["instagram", "tiktok", "youtube"])]), self.pkg)
        self.assertEqual(r["confirmed"], [])
        self.assertEqual(self.s.state(CID1), "authorised")

    def test_wrong_slot_or_caption_rejected(self):
        r = ts.confirm(self.s, CID1, {"data": {"id": 7}}, readback([post(7, ["instagram"], slot="2026-11-20T12:00:00")]), self.pkg)
        self.assertEqual(r["confirmed"], [])
        r = ts.confirm(self.s, CID1, {"data": {"id": 7}}, readback([post(7, ["instagram"], text="other")]), self.pkg)
        self.assertEqual(r["confirmed"], [])

    def test_duplicate_in_readback_confirms_nothing(self):
        r = ts.confirm(self.s, CID1, {"data": {"id": 7, "uuid": "u8"}}, readback([post(7, ["instagram"]), post(8, ["instagram"])]), self.pkg)
        self.assertEqual(r["confirmed"], [])
        self.assertTrue(r["problems"])


class TestI_Collisions(unittest.TestCase):
    def test_existing_post_at_slot_is_reported_not_touched(self):
        rb = readback([post(1, ["instagram", "tiktok", "youtube"], slot="2026-11-20T10:00:00"),
                       {**post(2, ["instagram"], slot="2026-11-20T18:00:00"), "instagramData": {"type": "POST"}}])
        col = ts.collisions(rb, "2026-11-20")
        self.assertEqual([(c["slot"], c["blocks"]) for c in col], [(1, True)])

    def test_static_post_near_slot_does_not_block(self):
        rb = readback([{**post(3, ["instagram"], slot="2026-11-20T10:00:00"), "instagramData": {"type": "POST"}}])
        col = ts.collisions(rb, "2026-11-20")
        self.assertEqual(len(col), 1)
        self.assertFalse(col[0]["blocks"])


class TestPackage(unittest.TestCase):
    def test_one_post_three_networks_reel_no_trial(self):
        p = ts.package(CID2, "https://x/v.mp4", "cap", {"tiktok": "t", "youtube": "Title #shorts"})
        self.assertEqual([x["network"] for x in p["info"]["providers"]], ["instagram", "tiktok", "youtube"])
        self.assertEqual(p["info"]["instagramData"]["type"], "REEL")
        self.assertEqual(p["info"]["publicationDate"], {"dateTime": "2026-11-20T13:00:00", "timezone": "Australia/Sydney"})
        self.assertEqual(len(p["keys"]), 3)

    def test_youtube_title_rules(self):
        with self.assertRaises(ts.StudioError):
            ts.package(CID2, "u", "c", {"tiktok": "t", "youtube": "no hashtag"})


class TestRepetition(unittest.TestCase):
    PLAYS = [{"play_id": "stagger-screen", "family": "off-ball screens", "variant": "stagger", "date": "2026-11-13",
              "concepts": ["stagger", "trail", "top-lock", "backdoor", "shooter"]},
             {"play_id": "elevator-screen", "family": "off-ball screens", "variant": "elevator", "date": "2026-11-12",
              "concepts": ["elevator doors", "chase", "early switch", "slip"]}]

    def test_same_play_renamed_is_blocked(self):
        r = ts.repeat_check("Off-ball screens", "Stagger", ["Stagger", "trail", "top-lock", "backdoor"], "2026-11-30", plays=self.PLAYS)
        self.assertFalse(r["ok"])

    def test_concept_overlap_blocks_new_name(self):
        r = ts.repeat_check("shooting actions", "double screen", ["stagger", "trail", "top-lock", "backdoor", "shooter"], "2026-11-30", plays=self.PLAYS)
        self.assertFalse(r["ok"])

    def test_same_family_needs_differential(self):
        r = ts.repeat_check("off-ball screens", "flare", ["flare", "skip pass"], "2026-11-30", plays=self.PLAYS)
        self.assertFalse(r["ok"])
        r = ts.repeat_check("off-ball screens", "flare", ["flare", "skip pass"], "2026-11-30", "away-from-ball screen, skip read", plays=self.PLAYS)
        self.assertTrue(r["ok"])

    def test_outside_window_ok(self):
        r = ts.repeat_check("off-ball screens", "stagger", ["stagger"], "2027-02-01", plays=self.PLAYS)
        self.assertTrue(r["ok"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
