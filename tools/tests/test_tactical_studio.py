"""Tactical Studio tests (v2, owner review 2026-11-12 21:14Z): gates in the real path, adversarial attempts,
persistence between sessions, collisions with real Metricool data, media identity in the confirmation.

  python3 -m unittest discover -s tools/tests -v
"""
import copy
import datetime as dt
import hashlib
import json
import re
import multiprocessing as mp
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
for _v in ("E2A_STUDIO_STATE", "E2A_LICENCES"):  # tests never read the real registry or a licence override
    os.environ.pop(_v, None)
import studio_sync as ss  # noqa: E402
import tactical_studio as ts  # noqa: E402

UTC = dt.timezone.utc
CID = "E2A-TACTICAL-2026-11-20-V01"
CID2 = "E2A-TACTICAL-2026-11-20-V02"
REAL_RB = os.path.join(HERE, "fixtures", "metricool_readback_2026-11-13_20.json")
OK_LIC = {k: {"commercial_use": True} for k in ("voice/*", "music/*", "sfx/*", "3d/procedural", "anton.woff2", "inter.woff2", "e2a_logo_white.png")}
SCRIPT = """HOOK: Stop guarding the ball. Watch the corner.
SETUP: The pin-down starts with the shooter buried in the corner and his defender on his hip.
CASE A: If the defender trails the screen, the shooter curls to the rim before the help arrives.
CASE B: If the defender cheats under, the shooter pops to the wing for an open three.
TAKEAWAY: One screen, two reads. The defender chooses, the shooter takes it.
CTA: Which read would you take? Follow for the next play.
"""


def words_of(text):
    t, out = 0.2, []
    for w in ts.spoken_text(text).split():
        out.append({"text": w, "start": round(t, 3), "end": round(t + 0.3, 3)})
        t += 0.37
    return out


class Clock:
    def __init__(self, t="2026-11-19T06:00:00+00:00"):
        self.t = dt.datetime.fromisoformat(t)

    def __call__(self):
        return self.t


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.clock = Clock()
        self.st = ts.Studio(os.path.join(self.tmp, "state"), clock=self.clock)
        # a private template/public with provenance sidecars, so the licence gate runs on real files
        self.tpl = os.path.join(self.tmp, "template")
        os.makedirs(os.path.join(self.tpl, "public", "ep"))
        self.voice = self._media("ep/voice.wav", b"VOICE" * 100, "voice/elevenlabs/x")
        self._media("ep/music.mp3", b"MUSIC" * 100, "music/synth/x")
        p = mock.patch.object(ts, "TEMPLATE", self.tpl)
        p.start()
        self.addCleanup(p.stop)
        self.lic = mock.patch.object(ts, "load_licences", return_value=OK_LIC)
        self.lic.start()
        self.addCleanup(self.lic.stop)
        self.bounds = mock.patch.object(ts, "run_bounds_qc", return_value={"pass": True, "frames_checked": 1000, "violations": []})
        self.bounds.start()
        self.addCleanup(self.bounds.stop)
        self.calls = []

    def _media(self, rel, data, key):
        p = os.path.join(self.tpl, "public", rel)
        open(p, "wb").write(data)
        json.dump({"licence_key": key, "source": "test", "sha256": hashlib.sha256(data).hexdigest()}, open(p + ".provenance.json", "w"))
        return p

    def file(self, name, content):
        p = os.path.join(self.tmp, name)
        open(p, "w" if isinstance(content, str) else "wb").write(content)
        return p

    # fakes for the slow/real parts; the gate logic around them is the real one
    def validator_ok(self, plays):
        ids = [json.load(open(p))["id"] for p in plays]
        return {"passed": 10, "failed": 0, "results": [{"play": i, "check": "claim \"x\"", "ok": True} for i in ids]}

    def renderer(self, bundle, master, social, c):
        self.calls.append("render")
        open(master, "wb").write(b"MASTER")
        open(social, "wb").write(b"MP4-BYTES" * 10)

    def measure_ok(self, mp4, words, frames_dir, c):
        return ({"width": 1080, "height": 1920, "fps": 30, "vcodec": "h264", "acodec": "aac", "duration": 35.2, "social_mb": 9.1, "black_frames": 0},
                {"mix": {"I": -14.1, "TP": -1.5}, "silences_inside_narration": []},
                {"extracted_from_mp4": True, "count": 8, "issues": []})

    def engine_ok(self, ep):
        return {"passed": 20, "failed": 0}

    def fetch_good(self, url):
        b = b"MP4-BYTES" * 10
        return hashlib.sha256(b).hexdigest(), len(b)

    def drive(self, cid, upto, measure=None):
        """Run the REAL gates in order with fakes only for render/measure/network."""
        st = self.st
        order = ["candidate", "researched", "selected", "scripted", "storyboard_ready", "audio_ready", "rendered", "qc_passed",
                 "asset_ready", "authorised"]
        script = self.file(f"{cid}.script.txt", SCRIPT)
        play = self.file(f"{cid}.play.json", json.dumps({"id": f"play-{cid[-3:]}"}))
        words = self.file(f"{cid}.words.json", json.dumps(words_of(SCRIPT)))
        bundle = self.file(f"{cid}.bundle.json", json.dumps({"episode": {"voice": "ep/voice.wav", "music": {"src": "ep/music.mp3"}, "shots": [{"sfx": [{"name": "tick"}]}]}}))
        for s in order[: order.index(upto) + 1]:
            op = f"{cid}:{s}"
            if s in ("candidate", "researched"):
                st.advance(cid, s, op)
            elif s == "selected":
                ts.select(st, cid, op, f"pin-{cid[-3:]}", f"fam-{cid[13:]}", f"v-{cid[-3:]}", [f"c{cid[13:]}", "curl"])
            elif s == "scripted":
                ts.freeze_script(st, cid, op, script)
            elif s == "storyboard_ready":
                ts.storyboard(st, cid, op, [play], validator=self.validator_ok)
            elif s == "audio_ready":
                ts.voice_permit(st, cid, op + ":permit", 500)
                ts.audio(st, cid, op, self.voice, words)
            elif s == "rendered":
                ts.render(st, cid, op, bundle, os.path.join(self.tmp, "out"), renderer=self.renderer)
            elif s == "qc_passed":
                r = ts.qc(st, cid, op, "ep.json", os.path.join(self.tmp, f"qc-{cid}"), measure=measure or self.measure_ok,
                          plays_validator=self.validator_ok, engine=self.engine_ok)
                if r["result"] != "QC_PASS":
                    return r
            elif s == "asset_ready":
                ts.asset(st, cid, op, "https://raw.githubusercontent.com/x/y/abc/v.mp4", fetch=self.fetch_good)
            elif s == "authorised":
                ts.authorise(st, cid, op, verifier=lambda scope: (True, "test delegation"))
        return None

    def pkg(self, cid=CID):
        return ts.package(self.st, cid, "Caption #e2a", {"tiktok": "Pin-down", "youtube": "Pin-down: two reads #shorts"})


# ---------------------------------------------------------------- calendar
class TestCalendar(unittest.TestCase):
    def test_J_dst_aedt_and_aest(self):
        self.assertEqual(ts.slot_instant("2026-11-20", 1).astimezone(UTC).hour, 23)  # AEDT +11
        self.assertEqual(ts.slot_instant("2027-04-05", 1).astimezone(UTC).hour, 0)   # AEST +10

    def test_J_target_date_uses_sydney_not_utc(self):
        self.assertEqual(ts.target_date(dt.datetime(2026, 11, 19, 6, 0, tzinfo=UTC)).isoformat(), "2026-11-20")
        self.assertEqual(ts.target_date(dt.datetime(2026, 11, 19, 20, 0, tzinfo=UTC)).isoformat(), "2026-11-20")

    def test_content_ids(self):
        self.assertEqual(ts.content_id("2026-11-20", 2), CID2)
        with self.assertRaises(ts.StudioError):
            ts.parse_cid("E2A-TACTICAL-20-11-2026-V1")


# ---------------------------------------------------------------- 1. no shortcuts to sensitive states
class TestGatesCannotBeSkipped(Base):
    def test_advance_refuses_every_gated_state(self):
        self.st.advance(CID, "candidate", "op1")
        self.st.advance(CID, "researched", "op2")
        for s in sorted(ts.GATED):
            with self.assertRaises(ts.StudioError, msg=s):
                self.st.advance(CID, s, f"x:{s}")
        self.assertEqual(self.st.state(CID), "researched")

    def test_cli_advance_to_authorised_or_qc_passed_is_refused(self):
        env = dict(os.environ, E2A_STUDIO_STATE=os.path.join(self.tmp, "cli"))
        tool = os.path.join(os.path.dirname(HERE), "tactical_studio.py")
        for s in ("qc_passed", "authorised", "scheduled_confirmed", "published_confirmed"):
            p = subprocess.run([sys.executable, tool, "advance", CID, s, "--op", "evil"], env=env, capture_output=True, text=True)
            self.assertEqual(p.returncode, 2, s)
            self.assertIn("gate", p.stdout)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "cli", "events.jsonl")))

    def test_internal_transition_needs_the_gate_token(self):
        with self.assertRaises(ts.StudioError):
            self.st._advance(CID, "candidate", "op", _token=object())
        with self.assertRaises(ts.StudioError):
            self.st.spend(CID, "voice_credits", 1, "op")

    def test_gates_require_the_previous_gate(self):
        self.drive(CID, "researched")
        with self.assertRaises(ts.StudioError):
            ts.qc(self.st, CID, "q", "ep.json", self.tmp, measure=self.measure_ok, plays_validator=self.validator_ok, engine=self.engine_ok)
        with self.assertRaises(ts.StudioError):
            ts.authorise(self.st, CID, "a", verifier=lambda s: (True, ""))
        with self.assertRaises(ts.StudioError):
            ts.asset(self.st, CID, "a", "https://x/y.mp4", fetch=self.fetch_good)

    def test_full_path_reaches_authorised_only_through_gates(self):
        self.assertIsNone(self.drive(CID, "authorised"))
        self.assertEqual(self.st.state(CID), "authorised")
        self.assertTrue(self.st.verify_chain()["ok"])

    def test_default_verifier_is_blocked(self):
        self.drive(CID, "asset_ready")
        with self.assertRaises(ts.StudioError):
            ts.authorise(self.st, CID, "a")
        self.assertEqual(self.st.state(CID), "asset_ready")


class TestStateMachine(Base):
    def test_order_enforced_on_free_states(self):
        with self.assertRaises(ts.StudioError):
            self.st.advance(CID, "researched", "op")

    def test_idempotent_ops(self):
        a = self.st.advance(CID, "candidate", "op1")
        self.assertTrue(self.st.advance(CID, "candidate", "op1")["idempotent"])
        self.assertEqual(a["seq"], 0)
        with self.assertRaises(ts.StudioError):
            self.st.advance(CID, "researched", "op1")

    def test_resume_after_failure_and_no_loops(self):
        self.drive(CID, "researched")
        self.st.fail(CID, "selected", "x")
        self.assertEqual(self.st.next_phase(CID), {"action": "retry", "phase": "selected"})
        self.st.fail(CID, "selected", "x")
        self.assertEqual(self.st.next_phase(CID)["action"], "stop")

    def test_truncated_line_ignored(self):
        self.st.advance(CID, "candidate", "op1")
        open(self.st.log, "a").write('{"kind": "state", "cid": "E2A')
        self.assertEqual(self.st.state(CID), "candidate")

    def test_usage_limit_wait(self):
        self.st.advance(CID, "candidate", "op1")
        self.st.fail(CID, "researched", "usage limit", retry_after="2026-11-19T08:00:00+00:00")
        self.assertEqual(self.st.next_phase(CID)["action"], "wait")


class TestLogIntegrity(Base):
    def test_edited_line_breaks_chain_and_blocks_writes(self):
        self.drive(CID, "asset_ready")
        lines = open(self.st.log).read().splitlines()
        lines[-1] = lines[-1].replace('"asset_ready"', '"authorised"')
        open(self.st.log, "w").write("\n".join(lines) + "\n")
        self.assertFalse(self.st.verify_chain()["ok"])
        with self.assertRaises(ts.StudioError):
            self.st.fail(CID, "x", "y")

    def test_deleted_line_breaks_chain(self):
        self.drive(CID, "scripted")
        lines = open(self.st.log).read().splitlines()
        del lines[1]
        open(self.st.log, "w").write("\n".join(lines) + "\n")
        self.assertFalse(self.st.verify_chain()["ok"])

    def test_forged_but_consistent_authorised_event_still_cannot_schedule(self):
        """An agent with shell access can append a well-formed `authorised` event. It gains nothing:
        schedule-check re-runs the verifier LIVE and the default verifier is blocked."""
        self.drive(CID, "asset_ready")
        ev = self.st.raw_events()
        forged = {"at": "2026-11-19T06:00:00+00:00", "seq": len(ev), "prev": ev[-1]["id"], "kind": "state", "cid": CID,
                  "to": "authorised", "op": "forged", "artifacts": {}, "refs": {}}
        forged["id"] = ts.Studio.event_id(forged)
        open(self.st.log, "a").write(json.dumps(forged) + "\n")
        self.assertTrue(self.st.verify_chain()["ok"])
        rb = json.load(open(REAL_RB))
        rb.update({"from": "2026-11-20T00:00:00+11:00", "to": "2026-11-21T00:00:00+11:00", "fetched_at": "2026-11-19T05:59:00+00:00"})
        with self.assertRaises(ts.StudioError) as e:
            ts.schedule_check(self.st, CID, "s", rb, self.pkg())
        self.assertIn("not authorised now", str(e.exception))
        self.assertEqual(self.st.events(CID, "reservation"), [])


# ---------------------------------------------------------------- 5. budget, licences, QC in the real path
class TestSelectionAndScript(Base):
    def test_repetition_blocked_in_the_select_gate(self):
        self.drive(CID, "selected")
        self.st.advance(CID2, "candidate", "c")
        self.st.advance(CID2, "researched", "r")
        with self.assertRaises(ts.StudioError):
            ts.select(self.st, CID2, "s", "pin-renamed", f"fam-{CID[13:]}", "v-V01", ["anything"])
        with self.assertRaises(ts.StudioError):
            ts.select(self.st, CID2, "s", "other", f"fam-{CID[13:]}", "other-variant", ["x"])  # same family, no differential
        ts.select(self.st, CID2, "s", "other", f"fam-{CID[13:]}", "other-variant", ["x"], differential="defence view")

    def test_script_structure_and_duration(self):
        self.drive(CID, "selected")
        bad = self.file("bad.txt", "HOOK: hi\nSETUP: short\nCTA: follow")
        with self.assertRaises(ts.StudioError):
            ts.freeze_script(self.st, CID, "s", bad)
        long = self.file("long.txt", SCRIPT.replace("TAKEAWAY:", "TAKEAWAY: " + "word " * 60))
        with self.assertRaises(ts.StudioError):
            ts.freeze_script(self.st, CID, "s2", long)
        self.assertTrue(ts.script_check(SCRIPT)["ok"], ts.script_check(SCRIPT))

    def test_script_changed_after_freeze_is_refused(self):
        self.drive(CID, "scripted")
        p = os.path.join(self.tmp, f"{CID}.script.txt")
        open(p, "a").write("CTA: a different call to action")
        with self.assertRaises(ts.StudioError):
            ts.storyboard(self.st, CID, "b", [self.file("p.json", '{"id":"p"}')], validator=self.validator_ok)

    def test_K_tactically_wrong_play_blocked(self):
        self.drive(CID, "scripted")
        play = self.file("p.json", '{"id":"p"}')
        with self.assertRaises(ts.StudioError):
            ts.storyboard(self.st, CID, "b", [play], validator=lambda p: {"passed": 30, "failed": 1, "results": []})
        with self.assertRaises(ts.StudioError):  # no narration claim
            ts.storyboard(self.st, CID, "b2", [play], validator=lambda p: {"passed": 30, "failed": 0, "results": []})


class TestD_Voice(Base):
    def test_permit_needed_and_transcript_must_match(self):
        self.drive(CID, "storyboard_ready")
        w = self.file("w.json", json.dumps(words_of(SCRIPT)))
        with self.assertRaises(ts.StudioError):
            ts.audio(self.st, CID, "a", self.voice, w)  # no permit
        ts.voice_permit(self.st, CID, "p", 500)
        other = self.file("w2.json", json.dumps(words_of("HOOK: Something else entirely was recorded here by mistake.")))
        with self.assertRaises(ts.StudioError):
            ts.audio(self.st, CID, "a", self.voice, other)
        ts.audio(self.st, CID, "a", self.voice, w)

    def test_resume_never_pays_twice(self):
        self.drive(CID, "audio_ready")
        self.st.fail(CID, "rendered", "container reclaimed")
        with self.assertRaises(ts.StudioError) as e:
            ts.voice_permit(self.st, CID, "p-again", 500)
        self.assertIn("reuse", str(e.exception))

    def test_M_voice_budget_enforced(self):
        self.drive(CID, "storyboard_ready")
        with self.assertRaises(ts.StudioError):
            ts.voice_permit(self.st, CID, "p", 5000)
        ts.voice_permit(self.st, CID, "p1", 600)
        self.drive(CID2, "storyboard_ready")
        with self.assertRaises(ts.StudioError):
            ts.voice_permit(self.st, CID2, "p2", 700)  # 600 + 700 > 1200 for the day


class TestRenderAndQC(Base):
    def test_L_licence_gate_runs_before_spending_a_render(self):
        self.drive(CID, "audio_ready")
        self.lic.stop()
        b = self.file("b.json", json.dumps({"episode": {"voice": "ep/voice.wav", "shots": []}}))
        with self.assertRaises(ts.StudioError) as e:
            ts.render(self.st, CID, "r", b, os.path.join(self.tmp, "out"), renderer=self.renderer)  # REAL licence file
        self.lic.start()
        self.assertIn("pending_owner_confirmation", str(e.exception))
        self.assertEqual(self.calls, [])
        self.assertEqual([x for x in self.st.events(kind="spend") if x["kind2"] == "final_renders"], [])

    def test_L_media_without_provenance_or_changed_after_it_fails(self):
        self.drive(CID, "audio_ready")
        open(os.path.join(self.tpl, "public", "ep", "music.mp3"), "ab").write(b"tampered")
        b = os.path.join(self.tmp, f"{CID}.bundle.json")
        with self.assertRaises(ts.StudioError) as e:
            ts.render(self.st, CID, "r", b, os.path.join(self.tmp, "out"), renderer=self.renderer)
        self.assertIn("provenance-hash-mismatch", str(e.exception))
        man = ts.bundle_manifest({"episode": {"voice": "nope.wav", "shots": []}})
        self.assertIn("missing-file", json.dumps(man))

    def test_bundle_must_use_the_approved_take(self):
        self.drive(CID, "audio_ready")
        self._media("ep/other.wav", b"OTHER", "voice/elevenlabs/y")
        b = self.file("b.json", json.dumps({"episode": {"voice": "ep/other.wav", "shots": []}}))
        with self.assertRaises(ts.StudioError):
            ts.render(self.st, CID, "r", b, os.path.join(self.tmp, "out"), renderer=self.renderer)

    def test_M_render_budget(self):
        self.drive(CID, "rendered")
        for i in range(3):
            self.st.fail(CID, "qc", "x", op=f"f{i}")
            self.st.spend(CID, "final_renders", 1, f"extra{i}", _token=ts._GATE) if i < 3 else None
        with self.assertRaises(ts.StudioError):
            self.st.spend(CID, "final_renders", 1, "one-too-many", _token=ts._GATE)

    def test_E_qc_measures_and_fails_closed(self):
        bads = {
            "loud": lambda *a: (self.measure_ok(*a)[0], {"mix": {"I": -11.0, "TP": -0.2}, "silences_inside_narration": []}, self.measure_ok(*a)[2]),
            "short": lambda *a: ({**self.measure_ok(*a)[0], "duration": 27.0}, *self.measure_ok(*a)[1:]),
            "heavy": lambda *a: ({**self.measure_ok(*a)[0], "social_mb": 14.0}, *self.measure_ok(*a)[1:]),
            "black": lambda *a: ({**self.measure_ok(*a)[0], "black_frames": 2}, *self.measure_ok(*a)[1:]),
            "frozen": lambda *a: (*self.measure_ok(*a)[:2], {"extracted_from_mp4": True, "count": 8, "issues": ["identical frames"]}),
            "silence": lambda *a: (self.measure_ok(*a)[0], {"mix": {"I": -14, "TP": -2}, "silences_inside_narration": [12.0]}, self.measure_ok(*a)[2]),
        }
        for i, (name, m) in enumerate(bads.items()):
            cid = f"E2A-TACTICAL-2026-11-{21 + i}-V01"
            r = self.drive(cid, "qc_passed", measure=m)
            self.assertEqual(r["result"], "QC_FAIL", name)
            self.assertEqual(self.st.state(cid), "failed", name)

    def test_qc_refuses_a_swapped_mp4(self):
        self.drive(CID, "rendered")
        open(os.path.join(self.tmp, "out", f"{CID}.mp4"), "wb").write(b"another video")
        with self.assertRaises(ts.StudioError):
            ts.qc(self.st, CID, "q", "ep.json", self.tmp, measure=self.measure_ok, plays_validator=self.validator_ok, engine=self.engine_ok)

    def test_qc_engine_or_tactical_failure(self):
        self.drive(CID, "rendered")
        r = ts.qc(self.st, CID, "q", "ep.json", os.path.join(self.tmp, "q"), measure=self.measure_ok,
                  plays_validator=self.validator_ok, engine=lambda e: {"passed": 19, "failed": 1})
        self.assertEqual(r["result"], "QC_FAIL")
        self.assertFalse(r["checks"]["engine"]["pass"])

    def test_test_licence_override_can_never_reach_asset(self):
        with mock.patch.object(ts, "LICENCES", self.file("test-lic.json", '{"assets": {}}')):
            self.drive(CID, "qc_passed")
        self.assertFalse(self.st.refs(CID, "rendered")["licences_official"])
        with self.assertRaises(ts.StudioError) as e:
            ts.asset(self.st, CID, "a", "https://x/y.mp4", fetch=self.fetch_good)
        self.assertIn("TEST licence override", str(e.exception))

    def test_asset_url_must_serve_the_qcd_bytes(self):
        self.drive(CID, "qc_passed")
        with self.assertRaises(ts.StudioError):
            ts.asset(self.st, CID, "a", "https://x/y.mp4", fetch=lambda u: (hashlib.sha256(b"x").hexdigest(), 1))
        with self.assertRaises(ts.StudioError):
            ts.asset(self.st, CID, "a2", "http://x/y.mp4", fetch=self.fetch_good)
        ts.asset(self.st, CID, "a3", "https://x/y.mp4", fetch=self.fetch_good)


class TestApprovalSystem(unittest.TestCase):
    def _cfg(self, mode, system):
        c = json.loads(json.dumps(ts.cfg()))
        c["publishing"]["mode"], c["publishing"]["approval_system"] = mode, system
        return c

    def test_only_supervised_with_explicit_approval(self):
        for mode, system, ok in [("supervised", "any", True), ("supervised", "optional", False), ("supervised", "all", False),
                                 ("limited_autonomy", "any", False), ("shadow", "any", False)]:
            with mock.patch.object(ts, "cfg", return_value=self._cfg(mode, system)):
                self.assertEqual(ts.metricool_review_verifier("x")[0], ok, (mode, system))

    def test_config_forbids_approval_by_silence(self):
        self.assertEqual(ts.cfg()["publishing"]["approval_system"], "any")


class TestBoundsQC(Base):
    """Screen elements must stay in the frame/safe area during the whole animation, judged on the engine
    code that actually rendered the MP4."""

    def test_bounds_violation_fails_qc(self):
        self.drive(CID, "rendered")
        bad = {"pass": False, "violations": [{"kind": "pin", "text": "HAMMER", "area": "frame", "side": "right", "worst_px": 130}]}
        with mock.patch.object(ts, "run_bounds_qc", return_value=bad):
            r = ts.qc(self.st, CID, "q", "ep.json", os.path.join(self.tmp, "q"), measure=self.measure_ok,
                      plays_validator=self.validator_ok, engine=self.engine_ok)
        self.assertEqual(r["result"], "QC_FAIL")
        self.assertFalse(r["checks"]["bounds"]["pass"])

    def test_engine_changed_after_render_fails_qc(self):
        self.drive(CID, "rendered")
        with mock.patch.object(ts, "engine_hash", return_value="0" * 64):
            r = ts.qc(self.st, CID, "q", "ep.json", os.path.join(self.tmp, "q"), measure=self.measure_ok,
                      plays_validator=self.validator_ok, engine=self.engine_ok)
        self.assertEqual(r["result"], "QC_FAIL")
        self.assertIn("engine changed", r["measured"]["bounds"]["why"])

    def test_render_records_engine_hash(self):
        self.drive(CID, "rendered")
        self.assertEqual(self.st.refs(CID, "rendered")["engine_sha256"], ts.engine_hash())


class TestLoudnessInProductionPath(Base):
    """The audio level is fixed in the render/encode path itself (not by a prompt): one fixed gain, capped."""

    def test_master_gain_is_fixed_and_capped(self):
        c = ts.cfg()
        self.assertEqual(ts.master_gain(-16.6, -4.1, c), 2.6)          # plain lift to -14
        self.assertEqual(ts.master_gain(-16.0, -2.0, c), 0.8)          # capped by true peak (-1.0 - 0.2)
        self.assertEqual(ts.master_gain(-30.0, -20.0, c), 6.0)         # capped by max_master_gain_db
        self.assertEqual(ts.master_gain(-12.0, -1.5, c), -2.0)         # too loud: fixed attenuation

    def test_real_encoder_applies_one_gain_without_dynamics(self):
        """Real ffmpeg on a synthetic master: a loud 'SFX' burst over a quiet bed must keep its ratio to the bed
        (a loudnorm/limiter would squash it)."""
        m = os.path.join(self.tmp, "m.mp4")
        sub = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=108x192:d=6:r=30",
                              "-f", "lavfi", "-i", "sine=f=220:d=6", "-filter_complex",
                              "[1]volume=-26dB,volume='if(between(t,3,3.5),15,1)':eval=frame[a]",
                              "-map", "0", "-map", "[a]", "-c:v", "libx264", "-c:a", "aac", "-b:a", "320k", m])
        self.assertEqual(sub.returncode, 0)
        out = os.path.join(self.tmp, "s.mp4")
        c = json.loads(json.dumps(ts.cfg()))
        c["video"]["social_max_mb"] = 1
        enc = ts.social_encode(m, out, c)
        def rms(path, a, b):
            e = ts._run(["ffmpeg", "-nostats", "-ss", str(a), "-t", str(b - a), "-i", path, "-vn", "-af", "astats", "-f", "null", "-"]).stderr
            return float(re.findall(r"RMS level dB: (-?[\d.]+)", e)[-1])
        d_in = rms(m, 3.05, 3.45) - rms(m, 1.0, 2.5)
        d_out = rms(out, 3.05, 3.45) - rms(out, 1.0, 2.5)
        self.assertAlmostEqual(d_in, d_out, delta=0.3)                  # burst-to-bed ratio unchanged
        self.assertAlmostEqual(rms(out, 1.0, 2.5) - rms(m, 1.0, 2.5), enc["gain_db"], delta=0.3)
        I, TP = ts.ebur128(out)
        self.assertLessEqual(TP, ts.cfg()["audio"]["true_peak_max"] + 0.3)

    def _audio_fail(self, cid):
        quiet = lambda *a: (self.measure_ok(*a)[0], {"mix": {"I": -16.6, "TP": -4.1}, "silences_inside_narration": []}, self.measure_ok(*a)[2])
        r = self.drive(cid, "qc_passed", measure=quiet)
        self.assertEqual(r["result"], "QC_FAIL")

    def test_remaster_reencodes_the_same_master_once_and_spends_no_render(self):
        self._audio_fail(CID)
        spent = self.st.events(CID, "spend")
        enc = lambda master, social, c: (open(social, "wb").write(b"REMASTERED") and {"gain_db": 2.6})
        ts.remaster(self.st, CID, "rm", encoder=enc)
        self.assertEqual(self.st.state(CID), "rendered")
        self.assertEqual(self.st.events(CID, "spend"), spent)
        self.assertEqual(self.st.refs(CID, "rendered")["encode"]["gain_db"], 2.6)
        self.assertIn("licences_official", self.st.refs(CID, "rendered"))
        r = ts.qc(self.st, CID, "q2", "ep.json", os.path.join(self.tmp, "q2"), measure=self.measure_ok,
                  plays_validator=self.validator_ok, engine=self.engine_ok)
        self.assertEqual(r["result"], "QC_PASS")
        self.assertEqual(r["mp4_sha256"], hashlib.sha256(b"REMASTERED").hexdigest())

    def test_remaster_refusals(self):
        self.drive(CID, "rendered")
        enc = lambda master, social, c: {"gain_db": 0}
        with self.assertRaises(ts.StudioError):                       # not failed
            ts.remaster(self.st, CID, "rm0", encoder=enc)
        ts.qc(self.st, CID, "q", "ep.json", os.path.join(self.tmp, "q"), measure=self.measure_ok,
              plays_validator=self.validator_ok, engine=lambda e: {"passed": 1, "failed": 1})
        with self.assertRaises(ts.StudioError):                       # engine failure is not an audio fix
            ts.remaster(self.st, CID, "rm1", encoder=enc)
        cid2 = "E2A-TACTICAL-2026-11-29-V02"
        self._audio_fail(cid2)
        open(os.path.join(self.tmp, "out", f"{cid2}.master.mp4"), "wb").write(b"other master")
        with self.assertRaises(ts.StudioError):                       # master swapped
            ts.remaster(self.st, cid2, "rm2", encoder=enc)
        cid3 = "E2A-TACTICAL-2026-11-30-V01"
        self._audio_fail(cid3)
        ts.remaster(self.st, cid3, "rm3", encoder=enc)
        quiet = lambda *a: (self.measure_ok(*a)[0], {"mix": {"I": -16.6, "TP": -4.1}, "silences_inside_narration": []}, self.measure_ok(*a)[2])
        ts.qc(self.st, cid3, "q3", "ep.json", os.path.join(self.tmp, "q3"), measure=quiet,
              plays_validator=self.validator_ok, engine=self.engine_ok)
        with self.assertRaises(ts.StudioError):                       # limit: one remaster
            ts.remaster(self.st, cid3, "rm4", encoder=enc)


# ---------------------------------------------------------------- 3. collisions (real Metricool data)
class TestI_Collisions(Base):
    def rb(self, day="2026-11-20", posts=None, fetched="2026-11-19T05:59:00+00:00"):
        return {"fetched_at": fetched, "from": f"{day}T00:00:00+11:00", "to": f"{day}T23:59:59+11:00",
                "data": posts if posts is not None else []}

    def test_real_calendar_13_nov_blocks_both_slots_static_included(self):
        rb = json.load(open(REAL_RB))
        hits = ts.collisions(rb, "2026-11-13")
        s1 = {h["metricool_id"] for h in hits if h["slot"] == 1}
        s2 = {h["metricool_id"] for h in hits if h["slot"] == 2}
        self.assertEqual(s1, {407520370, 426159230})  # static carousel + Stagger reel at 10:00
        self.assertEqual(s2, {426159411})              # trial reel at 13:00
        self.assertEqual({h["type"] for h in hits if h["metricool_id"] == 407520370}, {"POST"})

    def test_real_calendar_14_nov_static_blocks_10_only(self):
        hits = ts.collisions(json.load(open(REAL_RB)), "2026-11-14")
        self.assertEqual([(h["slot"], h["metricool_id"]) for h in hits], [(1, 407520558)])
        self.assertEqual(ts.collisions(json.load(open(REAL_RB)), "2026-11-15"), [])

    def test_schedule_check_is_mandatory_and_blocks_a_static_post(self):
        self.drive(CID, "authorised")
        static = copy.deepcopy(json.load(open(REAL_RB))["data"][0])
        static["publicationDate"]["dateTime"] = "2026-11-20T10:30:00"
        ok = lambda s: (True, "")
        with self.assertRaises(ts.StudioError):
            ts.schedule_check(self.st, CID, "s", self.rb(posts=[static]), self.pkg(), verifier=ok)
        self.assertEqual(self.st.events(CID, "reservation"), [])
        self.assertEqual(self.st.state(CID), "failed")

    def test_readback_must_be_fresh_and_cover_the_whole_day(self):
        self.drive(CID, "authorised")
        ok = lambda s: (True, "")
        with self.assertRaises(ts.StudioError):
            ts.schedule_check(self.st, CID, "s", self.rb(fetched="2026-11-19T05:00:00+00:00"), self.pkg(), verifier=ok)
        partial = self.rb()
        partial["from"] = "2026-11-20T09:00:00+11:00"
        with self.assertRaises(ts.StudioError):
            ts.schedule_check(self.st, CID, "s", partial, self.pkg(), verifier=ok)
        with self.assertRaises(ts.StudioError):
            ts.schedule_check(self.st, CID, "s", {"data": []}, self.pkg(), verifier=ok)

    def test_post_with_unreadable_date_blocks(self):
        self.assertTrue(ts.collisions({"data": [{"id": 1, "providers": [{"network": "instagram"}]}]}, "2026-11-20")[0]["blocks"])

    def test_edited_package_or_foreign_media_refused(self):
        self.drive(CID, "authorised")
        ok = lambda s: (True, "")
        p = self.pkg()
        p["info"]["text"] = "changed after build"
        with self.assertRaises(ts.StudioError):
            ts.schedule_check(self.st, CID, "s", self.rb(), p, verifier=ok)
        p = self.pkg()
        p["info"]["media"] = ["https://evil/x.mp4"]
        p["package_sha256"] = ts._pkg_hash(p)
        with self.assertRaises(ts.StudioError):
            ts.schedule_check(self.st, CID, "s", self.rb(), p, verifier=ok)

    def test_C_free_day_reserves_three_networks_once(self):
        self.drive(CID, "authorised")
        ok = lambda s: (True, "")
        t = ts.schedule_check(self.st, CID, "s", self.rb(), self.pkg(), verifier=ok)
        self.assertEqual(len(self.st.events(CID, "reservation")), 3)
        self.assertIn("expires", t)
        with self.assertRaises(ts.StudioError):
            ts.schedule_check(self.st, CID, "s-again", self.rb(), self.pkg(), verifier=ok)  # second schedule refused


def _race(args):
    d, i = args
    st = ts.Studio(d)
    try:
        st.reserve(CID, "instagram", f"op{i}")
        return 1
    except ts.StudioError:
        return 0


class TestC_Concurrency(unittest.TestCase):
    def test_two_simultaneous_runs(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        with mp.Pool(8) as p:
            self.assertEqual(sum(p.map(_race, [(d, i) for i in range(8)])), 1)
        self.assertTrue(ts.Studio(d).verify_chain()["ok"])


# ---------------------------------------------------------------- 4. confirmation
class TestF_N_Confirmation(Base):
    def setUp(self):
        super().setUp()
        self.drive(CID, "authorised")
        self.p = self.pkg()
        rb = {"fetched_at": "2026-11-19T05:59:00+00:00", "from": "2026-11-20T00:00:00+11:00", "to": "2026-11-21T00:00:00+11:00", "data": []}
        ts.schedule_check(self.st, CID, "s", rb, self.p, verifier=lambda s: (True, ""))
        self.create = {"data": {"id": 999, "uuid": "u-999"}}

    def post(self, **over):
        p = {"id": 999, "uuid": "u-999", "publicationDate": {"dateTime": "2026-11-20T10:00:00", "timezone": "Australia/Sydney"},
             "text": "Caption #e2a", "draft": False, "media": ["https://static.metricool.com/planner/x.mp4"],
             "providers": [{"network": n, "status": "PENDING"} for n in ts.NETWORKS]}
        p.update(over)
        return p

    def test_N_all_three_with_media_identity(self):
        r = ts.confirm(self.st, CID, self.create, {"data": [self.post()]}, self.p, fetch=self.fetch_good)
        self.assertEqual(r["state"], "scheduled_confirmed", r)

    def test_media_bytes_differ_or_unverifiable(self):
        r = ts.confirm(self.st, CID, self.create, {"data": [self.post()]}, self.p, fetch=lambda u: (hashlib.sha256(b"x").hexdigest(), 1))
        self.assertEqual(r["confirmed"], [])
        self.assertIn("media bytes differ", r["problems"][0])

        def blocked(u):
            raise ts.StudioError("CONNECT 403")
        r = ts.confirm(self.st, CID, self.create, {"data": [self.post()]}, self.p, fetch=blocked)
        self.assertEqual((r["confirmed"], r["state"]), ([], "authorised"))
        self.assertIn("not verifiable", r["problems"][0])

    def test_two_media_items_refused(self):
        r = ts.confirm(self.st, CID, self.create, {"data": [self.post(media=["a.mp4", "b.mp4"])]}, self.p, fetch=self.fetch_good)
        self.assertEqual(r["confirmed"], [])

    def test_pending_approval_is_not_confirmed(self):
        for p in (self.post(draft=True), self.post(draft=None), self.post(reviewStatus="PENDING_REVIEW"),
                  self.post(providers=[{"network": n, "status": "PENDING_APPROVAL"} for n in ts.NETWORKS])):
            r = ts.confirm(self.st, CID, self.create, {"data": [p]}, self.p, fetch=self.fetch_good)
            self.assertEqual(r["confirmed"], [], p)
            self.assertTrue(r["awaiting_approval"], p)
        self.assertEqual(self.st.state(CID), "authorised")

    def test_unknown_status_is_not_confirmed(self):
        r = ts.confirm(self.st, CID, self.create, {"data": [self.post(providers=[{"network": "instagram", "status": "QUEUED"}])]}, self.p, fetch=self.fetch_good)
        self.assertEqual(r["confirmed"], [])

    def test_F_one_network_fails_others_kept(self):
        prov = [{"network": "instagram", "status": "PENDING"}, {"network": "tiktok", "status": "ERROR"}, {"network": "youtube", "status": "PENDING"}]
        r = ts.confirm(self.st, CID, self.create, {"data": [self.post(providers=prov)]}, self.p, fetch=self.fetch_good)
        self.assertEqual((r["confirmed"], r["state"]), (["instagram", "youtube"], "scheduled_partial"))
        r = ts.confirm(self.st, CID, self.create, {"data": [self.post()]}, self.p, fetch=self.fetch_good)
        self.assertEqual(r["state"], "scheduled_confirmed")
        self.assertEqual(len(self.st.events(CID, "confirmation")), 3)

    def test_no_ticket_no_confirmation(self):
        p = dict(self.p)
        p["text_sha256"] = "0"
        p["package_sha256"] = ts._pkg_hash(p)
        with self.assertRaises(ts.StudioError):
            ts.confirm(self.st, CID, self.create, {"data": [self.post()]}, p, fetch=self.fetch_good)

    def test_invented_id_duplicate_wrong_slot_caption(self):
        self.assertEqual(ts.confirm(self.st, CID, {"id": 1}, {"data": [self.post()]}, self.p, fetch=self.fetch_good)["confirmed"], [])
        self.assertEqual(ts.confirm(self.st, CID, self.create, {"data": [self.post(), self.post()]}, self.p, fetch=self.fetch_good)["confirmed"], [])
        self.assertEqual(ts.confirm(self.st, CID, self.create, {"data": [self.post(publicationDate={"dateTime": "2026-11-20T13:00:00", "timezone": "Australia/Sydney"})]}, self.p, fetch=self.fetch_good)["confirmed"], [])
        self.assertEqual(ts.confirm(self.st, CID, self.create, {"data": [self.post(text="other")]}, self.p, fetch=self.fetch_good)["confirmed"], [])

    def test_published_needs_status_and_real_domain(self):
        ts.confirm(self.st, CID, self.create, {"data": [self.post()]}, self.p, fetch=self.fetch_good)
        urls = {"instagram": "https://www.instagram.com/reel/abc/", "tiktok": "https://www.tiktok.com/@e2a.basketball/video/1",
                "youtube": "https://youtube.com/shorts/xyz"}
        fake = self.post(providers=[{"network": n, "status": "PUBLISHED", "publicUrl": u.replace(".com", ".com.evil.io")} for n, u in urls.items()])
        with self.assertRaises(ts.StudioError):
            ts.published(self.st, CID, "p", {"data": [fake]})
        pending = self.post(providers=[{"network": n, "status": "PENDING", "publicUrl": u} for n, u in urls.items()])
        with self.assertRaises(ts.StudioError):
            ts.published(self.st, CID, "p", {"data": [pending]})
        ok = self.post(providers=[{"network": n, "status": "PUBLISHED", "publicUrl": u} for n, u in urls.items()])
        ts.published(self.st, CID, "p", {"data": [ok]})
        self.assertEqual(self.st.state(CID), "published_confirmed")


# ---------------------------------------------------------------- configuration (H)
class TestH_Config(unittest.TestCase):
    def test_routine_write_tools(self):
        r = json.load(open(os.path.join(ts.ROOT, "config", "routine.tactical-studio.json")))
        for t in r["tasks"]:
            tools = t["connectors"].get("Metricool-Social-Media-Management", {}).get("permitted_tools", [])
            self.assertTrue(tools, "empty permitted_tools = all tools")
            for w in ("updateScheduledPost", "sendScheduledPostForReview", "createScheduledPostForReview"):
                self.assertNotIn(w, tools)
            self.assertEqual("createScheduledPost" in tools, t["name"] == "E2A — TACTICAL STUDIO")
            self.assertIn("Claude_Code_Remote", t["never_attach"])

    def test_shadow_and_blocked_by_default(self):
        c = ts.cfg()
        self.assertIn(c["publishing"]["mode"], ("shadow", "direct_delegated"))
        self.assertEqual(c["delegation"]["verifier"], "blocked")  # tactical_studio.py authorise never opens publishing
        self.assertFalse(ts.metricool_review_verifier({})[0])

    def test_real_licences_block_unconfirmed_elevenlabs(self):
        r = ts.licence_check({"assets": [{"src": "v.wav", "licence_key": "voice/elevenlabs/x"}, {"src": "s", "licence_key": "sfx/tick"}]})
        self.assertFalse(r["pass"])
        self.assertEqual([f["src"] for f in r["failures"]], ["v.wav"])


class TestPackageAndRepetition(Base):
    def test_package_rules(self):
        self.drive(CID, "asset_ready")
        p = self.pkg()
        self.assertEqual(p["info"]["instagramData"]["type"], "REEL")
        self.assertEqual(p["info"]["media"], ["https://raw.githubusercontent.com/x/y/abc/v.mp4"])
        self.assertEqual(p["package_sha256"], ts._pkg_hash(p))
        with self.assertRaises(ts.StudioError):
            ts.package(self.st, CID, "c", {"tiktok": "t", "youtube": "no hashtag"})

    def test_repeat_window(self):
        plays = [{"play_id": "a", "family": "pin-down", "variant": "curl", "concepts": ["curl", "pin-down"], "date": "2026-11-01"}]
        self.assertFalse(ts.repeat_check("pin-down", "curl", ["x"], "2026-11-20", plays=plays)["ok"])
        self.assertTrue(ts.repeat_check("pin-down", "curl", ["x"], "2027-01-20", plays=plays)["ok"])


# ---------------------------------------------------------------- 2. persistence between sessions
def _lease_race(args):
    remote, cache, state, run = args
    try:
        ss.Sync(remote, "studio-state", state, cache).lease(run)
        return 1
    except ss.SyncError:
        return 0


class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.remote = os.path.join(self.tmp, "remote.git")
        subprocess.run(["git", "init", "-q", "--bare", self.remote], check=True)
        self.clock = Clock()

    def session(self, name):
        """A brand-new session: empty state dir and empty git cache (as in a fresh cloud container)."""
        return ss.Sync(self.remote, "studio-state", os.path.join(self.tmp, name, "state"), os.path.join(self.tmp, name, "cache"),
                       clock=self.clock), ts.Studio(os.path.join(self.tmp, name, "state"), clock=self.clock)

    def test_state_survives_into_a_new_session(self):
        a, sa = self.session("A")
        a.lease("run-A")
        sa.advance(CID, "candidate", "c")
        sa.advance(CID, "researched", "r")
        a.push("run-A")
        a.release("run-A")
        b, sb = self.session("B")
        self.assertEqual(b.pull()["action"], "pulled")
        self.assertEqual(sb.state(CID), "researched")
        self.assertTrue(sb.verify_chain()["ok"])

    def test_lease_blocks_a_second_writer(self):
        a, sa = self.session("A")
        b, sb = self.session("B")
        a.lease("run-A")
        with self.assertRaises(ss.SyncError):
            b.lease("run-B")
        sb.advance(CID, "candidate", "c")
        with self.assertRaises(ss.SyncError):
            b.push("run-B")

    def test_expired_lease_can_be_taken(self):
        a, _ = self.session("A")
        b, _ = self.session("B")
        a.lease("run-A")
        self.clock.t += dt.timedelta(hours=5)
        b.lease("run-B")
        with self.assertRaises(ss.SyncError):
            a.push("run-A")

    def test_lease_race_one_winner(self):
        args = [(self.remote, os.path.join(self.tmp, f"c{i}"), os.path.join(self.tmp, f"s{i}"), f"run-{i}") for i in range(6)]
        with mp.Pool(6) as p:
            self.assertEqual(sum(p.map(_lease_race, args)), 1)

    def test_diverged_histories_refused(self):
        a, sa = self.session("A")
        a.lease("run-A")
        sa.advance(CID, "candidate", "c")
        a.push("run-A")
        b, sb = self.session("B")
        sb.advance(CID, "candidate", "other-op")  # B wrote without pulling
        with self.assertRaises(ss.SyncError):
            b.pull()

    def test_tampered_remote_history_refused(self):
        a, sa = self.session("A")
        a.lease("run-A")
        sa.advance(CID, "candidate", "c")
        sa.advance(CID, "researched", "r")
        a.push("run-A")
        # someone rewrites the remote file in a normal commit (no force needed)
        a.fresh()
        p = os.path.join(a.cache, "studio-state", "events.jsonl")
        txt = open(p).read()
        open(p, "w").write(txt.replace('"researched"', '"authorised"'))
        a.git("commit", "-qam", "tamper")
        a.git("push", "-q", "origin", "HEAD:refs/heads/studio-state")
        b, _ = self.session("B")
        with self.assertRaises(ss.SyncError) as e:
            b.pull()
        self.assertIn("chain is broken", str(e.exception))

    def test_push_never_forces(self):
        src = open(ss.__file__).read()
        self.assertNotIn("--force", src.replace("never --force", "").replace("never `--force`", ""))


if __name__ == "__main__":
    unittest.main()
