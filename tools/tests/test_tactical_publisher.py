"""E2A Tactical Publisher tests (V3, owner brief 2026-11-12 23:16Z): the delegation cannot be forged, extended or
used outside its scope; a create call happens at most once per proven-absent attempt; nothing is confirmed
without real Metricool evidence; write tools exist only in the publisher step.

  python3 -m unittest discover -s tools/tests -v
"""
import copy
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from test_tactical_studio import Base, CID, CID2  # noqa: E402  (also pops the real-state env vars)
import tactical_studio as ts  # noqa: E402
import tactical_publisher as tp  # noqa: E402

UTC = dt.timezone.utc
NOW = dt.datetime(2026, 11, 19, 6, 0, tzinfo=UTC)  # 17:00 Sydney the day before the posts
STATIC = "https://static.metricool.com/planner/202611/7681319-file-1.mp4"
TEMPLATE = json.load(open(os.path.join(ts.ROOT, "config", "delegation.tactical-studio.json")))


def granted(**over):
    d = copy.deepcopy(TEMPLATE)
    d.update({"status": "granted", "granted_by": "owner", "granted_at": "2026-11-13T09:00:00+11:00"})
    for k, v in over.items():
        if k.startswith("scope_"):
            d["scope"][k[6:]] = v
        else:
            d[k] = v
    return d


def raw(d):
    return json.dumps(d, indent=1).encode()


def loader_for(d):
    b = raw(d)
    return lambda: (json.loads(b), hashlib.sha256(b).hexdigest())


def sha_of(d):
    return hashlib.sha256(raw(d)).hexdigest()


REAL_CFG = ts.cfg


class PBase(Base):
    """Real gates; the studio runs in direct_delegated mode with a granted delegation pinned by sha."""

    def setUp(self):
        super().setUp()
        self.c = json.loads(json.dumps(REAL_CFG()))
        self.c["publishing"]["mode"] = "direct_delegated"
        p = mock.patch.object(ts, "cfg", side_effect=lambda: self.c)
        p.start()
        self.addCleanup(p.stop)
        self.deleg = granted()
        self.sha = sha_of(self.deleg)
        self.load = loader_for(self.deleg)
        self.creates = []

    def rb(self, posts=None, day="2026-11-20", fetched="2026-11-19T05:59:00+00:00"):
        return {"fetched_at": fetched, "from": f"{day}T00:00:00+11:00", "to": f"{day}T23:59:59+11:00", "data": posts or []}

    def to_authorised(self, cid=CID):
        self.drive(cid, "asset_ready")
        tp.authorise(self.st, cid, f"{cid}:authorised", self.sha, loader=self.load, now=NOW)

    def prepare(self, cid=CID, posts=None, **kw):
        a = dict(probe_url=STATIC, loader=self.load, fetch=self.fetch_good, now=NOW)
        a.update(kw)
        return tp.prepare(self.st, cid, self.p if cid == CID else self.pkg(cid), self.rb(posts), self.sha, **a)

    def post(self, pid=999, cid=CID, **over):
        n = ts.parse_cid(cid)[1]
        p = {"id": pid, "uuid": f"u-{pid}", "publicationDate": {"dateTime": f"2026-11-20T{self.c['slots'][str(n)]['time']}:00",
             "timezone": "Australia/Sydney"}, "text": "Caption #e2a", "draft": False, "media": [STATIC],
             "providers": [{"network": x, "status": "PENDING"} for x in ts.NETWORKS]}
        p.update(over)
        return p


# ---------------------------------------------------------------- 1. delegation
class TestDelegation(PBase):
    def check(self, d, pinned=None, now=NOW, cid=CID):
        return tp.check_delegation(d, sha_of(d), pinned or sha_of(d), now, cid, self.c)

    def test_granted_in_force_and_in_scope(self):
        self.assertTrue(self.check(granted())["ok"])

    def test_the_committed_template_is_not_a_grant(self):
        with self.assertRaises(tp.PublishError):
            self.check(TEMPLATE)

    def test_forged_or_changed_file_has_another_sha(self):
        for d in (granted(valid_until="2026-11-30T00:00:00+11:00"), granted(scope_max_videos_per_day=3), granted(revoked=False, note="x")):
            with self.assertRaises(tp.PublishError, msg=d):
                tp.check_delegation(d, sha_of(d), self.sha, NOW, CID, self.c)  # pinned = the owner's original

    def test_revoked_expired_too_long(self):
        for d, now in ((granted(revoked=True), NOW), (granted(status="revoked"), NOW), (granted(), dt.datetime(2026, 11, 21, 0, 0, tzinfo=UTC)),
                       (granted(valid_until="2026-11-22T00:00:00+11:00"), NOW)):
            with self.assertRaises(tp.PublishError, msg=d):
                self.check(d, now=now)

    def test_scope_must_match_the_studio(self):
        for over in ({"scope_networks": ["instagram", "tiktok", "youtube", "facebook"]}, {"scope_brand": "1"},
                     {"scope_slots": ["10:00", "18:00"]}, {"scope_engine": "Tactical2D"}, {"scope_duration_s": [20, 60]},
                     {"scope_write_tool": "updateScheduledPost"}, {"scope_accounts": {"instagram": "other"}},
                     {"scope_qc_required": ["tactical"]}):
            with self.assertRaises(tp.PublishError, msg=over):
                self.check(granted(**over))

    def test_studio_budget_cannot_exceed_the_delegated_one(self):
        d = granted()
        d["scope"]["budget_per_day"]["create_calls"] = 2
        with self.assertRaises(tp.PublishError):
            self.check(d)

    def test_only_two_videos_a_day_and_inside_the_window(self):
        with self.assertRaises(tp.PublishError):
            self.check(granted(), cid="E2A-TACTICAL-2026-11-20-V03")
        with self.assertRaises(tp.PublishError):
            self.check(granted(), cid="E2A-TACTICAL-2026-11-21-V01")

    def test_read_from_origin_main_never_from_the_working_tree(self):
        root = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, root, True)
        g = lambda *a, cwd: subprocess.run(["git", *a], cwd=cwd, check=True, capture_output=True)  # noqa: E731
        g("init", "-q", "--bare", "-b", "main", "origin.git", cwd=root)
        g("clone", "-q", "origin.git", "w", cwd=root)
        w = os.path.join(root, "w")
        os.makedirs(os.path.join(w, "config"))
        draft = copy.deepcopy(TEMPLATE)
        open(os.path.join(w, tp.DELEGATION_PATH), "wb").write(raw(draft))
        g("-c", "user.name=o", "-c", "user.email=o@x", "commit", "-qam", "x", "--allow-empty", cwd=w)
        g("add", ".", cwd=w)
        g("-c", "user.name=o", "-c", "user.email=o@x", "commit", "-qm", "draft", cwd=w)
        g("push", "-q", "origin", "HEAD:main", cwd=w)
        open(os.path.join(w, tp.DELEGATION_PATH), "wb").write(raw(granted()))  # agent edits its working tree
        g("-c", "user.name=a", "-c", "user.email=a@x", "commit", "-qam", "forge", cwd=w)  # and commits locally
        with mock.patch.object(ts, "ROOT", w):
            d, sha = tp.load_delegation()
        self.assertEqual(d["status"], "draft")
        self.assertEqual(sha, sha_of(draft))


# ---------------------------------------------------------------- 2. modes and gates
class TestModesAndGates(PBase):
    def test_shadow_mode_refuses(self):
        self.c["publishing"]["mode"] = "shadow"
        self.drive(CID, "asset_ready")
        with self.assertRaises(tp.PublishError):
            tp.authorise(self.st, CID, "a", self.sha, loader=self.load, now=NOW)

    def test_studio_authorise_stays_blocked_without_the_publisher(self):
        self.drive(CID, "asset_ready")
        self.c["delegation"]["verifier"] = "delegation"
        with self.assertRaises(ts.StudioError):
            ts.authorise(self.st, CID, "a")
        self.assertEqual(self.st.state(CID), "asset_ready")

    def test_qc_fail_is_never_schedulable(self):
        bad = lambda mp4, w, f, c: (lambda r: (r[0], {"mix": {"I": -19.0, "TP": -0.2}, "silences_inside_narration": []}, r[2]))(self.measure_ok(mp4, w, f, c))  # noqa: E731
        r = self.drive(CID, "qc_passed", measure=bad)
        self.assertEqual(r["result"], "QC_FAIL")
        for f in (lambda: tp.authorise(self.st, CID, "a", self.sha, loader=self.load, now=NOW),
                  lambda: tp.prepare(self.st, CID, {}, self.rb(), self.sha, STATIC, self.load, self.fetch_good, NOW)):
            with self.assertRaises(ts.StudioError):
                f()
        self.assertEqual(self.st.events(CID, "intent"), [])

    def test_bad_asset_url_never_reaches_authorised(self):
        self.drive(CID, "qc_passed")
        with self.assertRaises(ts.StudioError):
            ts.asset(self.st, CID, "a", "https://raw.githubusercontent.com/x/y/abc/v.mp4", fetch=lambda u: ("0" * 64, 5))
        with self.assertRaises(ts.StudioError):
            tp.authorise(self.st, CID, "b", self.sha, loader=self.load, now=NOW)


# ---------------------------------------------------------------- 3. create, record, reconcile
class TestCreateFlow(PBase):
    def setUp(self):
        super().setUp()
        self.to_authorised()
        self.p = self.pkg()

    def test_prepare_gives_exactly_one_call_with_sydney_offset(self):
        out = self.prepare()
        a = out["arguments"]
        self.assertEqual((out["tool"], a["blogId"], a["date"]), ("createScheduledPost", "7681319", "2026-11-20T10:00:00+11:00"))
        info = json.loads(a["info"])
        self.assertEqual(info["publicationDate"], {"dateTime": "2026-11-20T10:00:00", "timezone": "Australia/Sydney"})
        self.assertEqual([x["network"] for x in info["providers"]], ["instagram", "tiktok", "youtube"])
        self.assertEqual((info["instagramData"]["type"], info["youtubeData"]["type"], info["draft"]), ("REEL", "short", False))
        self.assertEqual(len(self.st.events(CID, "intent")), 1)
        self.assertEqual(sum(e["amount"] for e in self.st.events(kind="spend") if e["kind2"] == "create_calls"), 1)
        with self.assertRaises(tp.PublishError):  # open intent → never a second create
            self.prepare()

    def test_clear_answer_then_confirmed_with_media_identity(self):
        it = self.prepare()["intent"]
        resp = json.load(open(os.path.join(HERE, "fixtures", "metricool_create_response_426159230.json")))["response"]
        resp["data"]["id"], resp["data"]["uuid"] = 999, "u-999"
        self.assertTrue(tp.record(self.st, CID, it, json.dumps(resp))["created"])
        r = tp.confirm(self.st, CID, self.rb([self.post()]), self.p, fetch=self.fetch_good)
        self.assertEqual(r["state"], "scheduled_confirmed", r)
        with self.assertRaises(tp.PublishError):
            self.prepare()  # already created and confirmed: never again

    def test_connector_error_timeout_or_partial_answer_is_uncertain(self):
        for ans in ("Error: 500 internal", "", '{"data": {"id": 999}}', '{"status": "ok"}'):
            st = ts.Studio(os.path.join(self.tmp, "s" + hashlib.md5(ans.encode()).hexdigest()), clock=self.clock)
            self.st = st
            self.drive(CID, "asset_ready")
            tp.authorise(st, CID, "au", self.sha, loader=self.load, now=NOW)
            self.p = self.pkg()
            it = self.prepare()["intent"]
            self.assertEqual(tp.record(st, CID, it, ans)["created"], "unknown", ans)
            with self.assertRaises(tp.PublishError, msg=ans):
                self.prepare()  # blind retry refused

    def test_uncertain_then_found_is_adopted_not_recreated(self):
        it = self.prepare()["intent"]
        tp.record(self.st, CID, it, "timeout")
        self.assertEqual(tp.reconcile(self.st, CID, self.rb([self.post()]), self.p, now=NOW)["adopted"], 999)
        self.assertEqual(tp.confirm(self.st, CID, self.rb([self.post()]), self.p, fetch=self.fetch_good)["state"], "scheduled_confirmed")
        self.assertEqual(len(self.st.events(CID, "intent")), 1)

    def test_uncertain_then_absent_allows_one_more_attempt_only(self):
        it = self.prepare()["intent"]
        tp.record(self.st, CID, it, "timeout")
        self.assertTrue(tp.reconcile(self.st, CID, self.rb(), self.p, now=NOW)["absent"])
        it2 = self.prepare()["intent"]
        tp.record(self.st, CID, it2, "timeout")
        tp.reconcile(self.st, CID, self.rb(), self.p, now=NOW)
        with self.assertRaises(tp.PublishError):  # max_create_attempts = 2
            self.prepare()

    def test_reconcile_needs_a_fresh_full_day_readback(self):
        it = self.prepare()["intent"]
        tp.record(self.st, CID, it, "timeout")
        with self.assertRaises(tp.PublishError):
            tp.reconcile(self.st, CID, self.rb(fetched="2026-11-19T04:00:00+00:00"), self.p, now=NOW)
        self.assertEqual(len(tp._open_intent(self.st, CID)), 1)

    def test_duplicate_in_metricool_stops_and_deletes_nothing(self):
        it = self.prepare()["intent"]
        tp.record(self.st, CID, it, "timeout")
        with self.assertRaises(tp.PublishError):
            tp.reconcile(self.st, CID, self.rb([self.post(1), self.post(2, publicationDate={"dateTime": "2026-11-20T19:00:00", "timezone": "Australia/Sydney"})]), self.p, now=NOW)
        self.assertEqual(self.st.state(CID), "failed")

    def test_same_video_already_in_calendar_is_not_created(self):
        other_time = self.post(5, publicationDate={"dateTime": "2026-11-20T20:00:00", "timezone": "Australia/Sydney"})
        with self.assertRaises(tp.PublishError):
            self.prepare(posts=[other_time])
        self.assertEqual(self.st.events(CID, "intent"), [])

    def test_slot_taken_by_any_post_is_not_created(self):
        with self.assertRaises(ts.StudioError):
            self.prepare(posts=[self.post(7, text="a static carousel")])
        self.assertEqual(self.st.events(CID, "intent"), [])

    def test_media_verification_path_fails_closed(self):
        def blocked(u):
            raise ts.StudioError("CONNECT tunnel failed, response 403")
        for kw in ({"probe_url": None}, {"probe_url": "https://raw.githubusercontent.com/x.mp4"}, {"fetch": blocked}):
            with self.assertRaises(tp.PublishError, msg=kw):
                self.prepare(**kw)
        self.assertEqual(self.st.events(CID, "intent"), [])

    def test_revoked_between_authorise_and_create(self):
        self.load = loader_for(granted(revoked=True))
        with self.assertRaises(tp.PublishError):
            self.prepare()
        self.assertEqual(self.st.events(CID, "intent"), [])

    def test_no_confirmation_without_real_evidence(self):
        it = self.prepare()["intent"]
        tp.record(self.st, CID, it, {"data": {"id": 999, "uuid": "u-999"}})

        def blocked(u):
            raise ts.StudioError("403")
        for rb, f in ((self.rb(), self.fetch_good), (self.rb([self.post()]), blocked),
                      (self.rb([self.post(media=["https://static.metricool.com/other.mp4"])]), lambda u: ("0" * 64, 3)),
                      (self.rb([self.post(draft=True)]), self.fetch_good)):
            r = tp.confirm(self.st, CID, rb, self.p, fetch=f)
            self.assertEqual(r["confirmed"], [])
        self.assertEqual(self.st.state(CID), "authorised")

    def test_per_network_state(self):
        it = self.prepare()["intent"]
        tp.record(self.st, CID, it, {"data": {"id": 999, "uuid": "u-999"}})
        prov = [{"network": "instagram", "status": "PENDING"}, {"network": "tiktok", "status": "ERROR"}, {"network": "youtube", "status": "PENDING"}]
        r = tp.confirm(self.st, CID, self.rb([self.post(providers=prov)]), self.p, fetch=self.fetch_good)
        self.assertEqual((r["confirmed"], r["state"]), (["instagram", "youtube"], "scheduled_partial"))
        row = tp.status(self.st, "2026-11-20")[0]
        self.assertEqual((row["instagram"], row["tiktok"], row["youtube"], row["metricool_id"]), ("pending", "-", "pending", 999))
        with self.assertRaises(tp.PublishError):
            self.prepare()  # partially confirmed: never recreated


class TestBudget(PBase):
    def test_create_calls_budget_per_day(self):
        self.c["budget_per_day"]["create_calls"] = 1
        d = granted()
        d["scope"]["budget_per_day"]["create_calls"] = 1
        self.deleg, self.sha, self.load = d, sha_of(d), loader_for(d)
        self.to_authorised(CID)
        self.p = self.pkg()
        self.prepare()
        self.to_authorised(CID2)
        with self.assertRaises(ts.StudioError):
            self.prepare(CID2)
        self.assertEqual(self.st.events(CID2, "intent"), [])


class TestConcurrency(PBase):
    def test_two_sessions_cannot_both_create(self):
        self.to_authorised()
        self.p = self.pkg()
        other = ts.Studio(self.st.dir, clock=self.clock)  # a second session on the same synced registry
        self.prepare()
        with self.assertRaises(ts.StudioError):
            tp.prepare(other, CID, self.p, self.rb(), self.sha, STATIC, self.load, self.fetch_good, NOW)
        self.assertEqual(len(self.st.events(CID, "intent")), 1)
        self.assertTrue(self.st.verify_chain()["ok"])


# ---------------------------------------------------------------- 4. static scan: where write tools may appear
class TestWriteToolsOnlyInThePublisherStep(unittest.TestCase):
    WRITE = ("createScheduledPost", "updateScheduledPost", "sendScheduledPostForReview", "createScheduledPostForReview")

    def test_routine_permissions(self):
        r = json.load(open(os.path.join(ts.ROOT, "config", "routine.tactical-studio.json")))
        tasks = {t["name"]: t for t in r["tasks"]}
        studio = tasks["E2A — TACTICAL STUDIO"]["connectors"]["Metricool-Social-Media-Management"]["permitted_tools"]
        check = tasks["E2A — TACTICAL CHECK"]["connectors"]["Metricool-Social-Media-Management"]["permitted_tools"]
        self.assertEqual([t for t in studio if t in self.WRITE], ["createScheduledPost"])
        self.assertEqual([t for t in check if t in self.WRITE], [])
        for t in r["tasks"]:
            self.assertIn("Claude_Code_Remote", t["never_attach"])
            self.assertTrue(re.search(r" \d+-\d+ \d+ \*$", t["cron"]), "cron must be limited to the delegation dates")

    def test_prompts(self):
        d = os.path.join(ts.ROOT, "produccion", "tactical")
        check = open(os.path.join(d, "PROMPT-CHECK.md")).read()
        for w in self.WRITE:
            self.assertNotIn(w, check)
        daily = open(os.path.join(d, "PROMPT-DIARIO.md")).read().split("\n")
        for i, line in enumerate(daily):
            for w in ("updateScheduledPost", "createScheduledPostForReview", "sendScheduledPostForReview"):
                if w in line:
                    self.assertRegex(line, r"Nunca|nunca", line)
        calls = [l for l in daily if re.search(r"\bcreateScheduledPost\b", l) and "Nunca" not in l]
        self.assertTrue(all(re.match(r"\s*(4\.|`getScheduledPosts|`createScheduledPost|--sha|6\.)", l) for l in calls), calls)
        for f in ("ACTIVACION.md", "PROCEDIMIENTO.md", "PROMPT-DIARIO.md", "PROMPT-CHECK.md"):
            txt = open(os.path.join(d, f)).read()
            self.assertNotRegex(txt, r"12:00|18:00 Sydney|mode: supervised|`limited`", f)

    def test_code(self):
        tools = os.path.join(ts.ROOT, "tools")
        for f in os.listdir(tools):
            if f.endswith(".py") and f != "tactical_publisher.py":
                src = open(os.path.join(tools, f)).read()
                self.assertNotRegex(src, r"WRITE_TOOL|tool\s*=\s*\"createScheduledPost\"", f)
        self.assertEqual(ts.cfg()["publishing"]["create_tool"], "createScheduledPost")
        self.assertEqual(ts.cfg()["publishing"]["mode"], "shadow")  # this PR does not activate anything
        self.assertEqual(TEMPLATE["status"], "draft")


# ---------------------------------------------------------------- 5. integral (production → publication prep, dry run)
class TestIntegralDryRun(PBase):
    def test_two_videos_end_to_end_with_fake_metricool(self):
        ids = iter((426200001, 426200002))
        cal = []
        for cid, n in ((CID, 1), (CID2, 2)):
            self.to_authorised(cid)
            pkg = ts.package(self.st, cid, f"Caption {cid}", {"tiktok": "Play", "youtube": "Play #shorts"})
            out = tp.prepare(self.st, cid, pkg, self.rb(cal), self.sha, STATIC, self.load, self.fetch_good, NOW)
            info = json.loads(out["arguments"]["info"])
            pid = next(ids)  # the fake createScheduledPost
            cal.append({"id": pid, "uuid": f"u{pid}", "publicationDate": info["publicationDate"], "text": info["text"],
                        "draft": False, "media": [STATIC], "providers": [{"network": x["network"], "status": "PENDING"} for x in info["providers"]]})
            tp.record(self.st, cid, out["intent"], {"data": {"id": pid, "uuid": f"u{pid}", "plannerUrl": "https://app.metricool.com/x"}})
            r = tp.confirm(self.st, cid, self.rb(cal), pkg, fetch=self.fetch_good)
            self.assertEqual(r["state"], "scheduled_confirmed", r)
        rows = tp.status(self.st, "2026-11-20")
        self.assertEqual([(r["state"], r["qc"], r["metricool_id"]) for r in rows],
                         [("scheduled_confirmed", "QC_PASS", 426200001), ("scheduled_confirmed", "QC_PASS", 426200002)])
        self.assertTrue(all(r[n] == "pending" for r in rows for n in ts.NETWORKS))
        self.assertTrue(self.st.verify_chain()["ok"])


if __name__ == "__main__":
    unittest.main()
