#!/usr/bin/env python3
"""E2A Tactical Publisher — the ONLY component that may schedule Tactical Studio videos in Metricool.

It never calls Metricool itself: it decides whether a create call is allowed, writes a write-ahead
`intent` to the registry, and prints the EXACT arguments of ONE `createScheduledPost` call. The agent makes
that single call, hands the raw answer to `record`, reads the calendar back and runs `confirm`. Every step is
in the hash-chained registry (tools/tactical_studio.py), so a crash, a timeout or a second session can never
lead to a blind second create.

  delegation  --sha S                     check the owner's delegation (pinned sha) and print it
  preflight   --sha S --probe-url U       delegation + media-verification path (static.metricool.com) reachable
  authorise CID --sha S --op OP          gate `authorised` with the live delegation check
  prepare  CID --package P --readback R --sha S [--probe-url U]   → createScheduledPost arguments + intent
  record   CID --intent ID --response FILE|-                       → created / uncertain
  reconcile CID --readback R --package P                           → adopt the post, or prove it is absent
  confirm  CID --readback R --package P                            → per-network confirmation
  status   DATE                                                    → daily report rows

Delegation: config/delegation.tactical-studio.json, read from the git ref `origin/main` (never from the
working tree). The scheduled task's own prompt pins its sha256; the task's cron only fires inside the
delegation dates. Any edit of the file changes the sha and stops publishing. The agent cannot create, extend
or renew a delegation: that needs a merge to main by the owner AND an edit of the scheduled task by the owner.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tactical_studio as ts  # noqa: E402

DELEGATION_PATH = "config/delegation.tactical-studio.json"
DELEGATION_REF = "origin/main"  # fixed on purpose: no environment override (an agent could point it at its own branch)
BRAND = "7681319"
WRITE_TOOL = "createScheduledPost"
# the official accounts of brand 7681319 (getBrandSettings, 2026-11-12)
ACCOUNTS = {"instagram": "e2a_basketball", "tiktok": "e2a.basketball", "youtube": "UCdjEpbOnxtCaNn1m7YXyJqQ"}


class PublishError(ts.StudioError):
    pass


# ------------------------------------------------------------------ delegation
def load_delegation(ref=DELEGATION_REF, path=DELEGATION_PATH, git=None):
    """The delegation as committed on `ref` (default origin/main), never the working tree."""
    run = git or (lambda *a: subprocess.run(["git", *a], cwd=ts.ROOT, capture_output=True, check=False))
    run("fetch", "-q", "origin", "main")
    p = run("show", f"{ref}:{path}")
    if p.returncode:
        raise PublishError(f"no delegation on {ref}:{path}: publishing is not authorised")
    raw = p.stdout if isinstance(p.stdout, bytes) else p.stdout.encode()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def check_delegation(deleg, sha, pinned_sha, now, cid=None, c=None):
    """Raise unless the delegation is the pinned one, in force now, and its scope covers `cid`."""
    c = c or ts.cfg()
    if not pinned_sha or sha != pinned_sha:
        raise PublishError("delegation sha differs from the one pinned in the scheduled task: stop (changed, revoked or forged)")
    if deleg.get("status") != "granted" or deleg.get("revoked"):
        raise PublishError(f"delegation status {deleg.get('status')!r}, revoked={deleg.get('revoked')}")
    s = deleg.get("scope", {})
    frm, until = ts.parse_ts(deleg["valid_from"]), ts.parse_ts(deleg["valid_until"])
    if until - frm > dt.timedelta(days=c["delegation"]["max_days"]):
        raise PublishError(f"delegation longer than {c['delegation']['max_days']} days")
    if not frm <= now < until:
        raise PublishError(f"delegation not in force now ({frm} – {until})")
    want = {"brand": BRAND, "networks": sorted(ts.NETWORKS), "slots": sorted(c["slots"][k]["time"] for k in ("1", "2")),
            "timezone": c["timezone"], "max_videos_per_day": 2, "engine": "Tactical3DV2", "format": "tactical basketball",
            "duration_s": [c["duration_s"]["min"], c["duration_s"]["max"]], "write_tool": WRITE_TOOL,
            "accounts": ACCOUNTS, "qc_required": sorted(ts.QC_REQUIRED)}
    got = {"brand": str(s.get("brand")), "networks": sorted(s.get("networks", [])), "slots": sorted(s.get("slots", [])),
           "timezone": s.get("timezone"), "max_videos_per_day": s.get("max_videos_per_day"), "engine": s.get("engine"),
           "format": s.get("format"), "duration_s": s.get("duration_s"), "write_tool": s.get("write_tool"),
           "accounts": s.get("accounts"), "qc_required": sorted(s.get("qc_required") or [])}
    bad = {k: (got[k], want[k]) for k in want if got[k] != want[k]}
    if bad:
        raise PublishError(f"delegation scope does not match the studio: {bad}")
    for k, v in (s.get("budget_per_day") or {}).items():
        if c["budget_per_day"].get(k, 0) > v:
            raise PublishError(f"studio budget {k}={c['budget_per_day'][k]} exceeds the delegated {v}")
    if cid:
        d, n = ts.parse_cid(cid)
        if n not in (1, 2):
            raise PublishError(f"{cid}: only V01 (10:00) and V02 (13:00) exist; at most 2 videos a day")
        slot = ts.slot_instant(d, n, c)
        if not frm <= slot < until:
            raise PublishError(f"{cid} slot {slot} is outside the delegation")
    return {"ok": True, "valid_until": deleg["valid_until"], "sha": sha}


def delegation_verifier(pinned_sha, now=None, loader=None, cid=None):
    """Verifier for ts.authorise / ts.schedule_check: a live delegation check every time."""
    def v(scope):
        try:
            d, sha = (loader or load_delegation)()
            check_delegation(d, sha, pinned_sha, now or ts.now_utc(), scope.get("cid") or cid)
            return True, f"delegation {sha[:12]} in force"
        except (PublishError, KeyError, ValueError) as e:
            return False, str(e)
    return v


def authorise(st, cid, op, pinned_sha, loader=None, now=None):
    """GATE authorised for direct publishing: the owner's delegation, checked live (never a flag in the registry)."""
    if ts.cfg()["publishing"]["mode"] != "direct_delegated":
        raise PublishError(f"publishing mode is {ts.cfg()['publishing']['mode']!r}: direct scheduling is off")
    return ts.authorise(st, cid, op, verifier=delegation_verifier(pinned_sha, now or st.clock(), loader, cid))


# ------------------------------------------------------------------ media verification path
def preflight_media(probe_url, fetch=None):
    """Metricool re-hosts media on static.metricool.com. If that host cannot be read, `confirm` can never verify
    the file, so NOTHING may be created (an unverifiable post would still go out)."""
    if not probe_url or not probe_url.startswith("https://static.metricool.com/"):
        raise PublishError("a static.metricool.com probe URL from the calendar is required")
    try:
        (fetch or ts.fetch_sha)(probe_url)
    except ts.StudioError as e:
        raise PublishError(f"media verification path unavailable ({e}): nothing is created")
    return True


# ------------------------------------------------------------------ helpers
def _events(st, cid, kind):
    return st.events(cid, kind)


def _open_intent(st, cid):
    """An intent without `created` or `create_absent` = outcome unknown → reconcile first."""
    closed = {e["intent"] for e in _events(st, cid, "created")} | {e["intent"] for e in _events(st, cid, "create_absent")}
    return [e for e in _events(st, cid, "intent") if e["id"] not in closed]


def duplicates(readback, pkg, c=None):
    """Posts that already carry this video (same caption) anywhere in the read-back."""
    return [p.get("id") for p in readback.get("data", readback)
            if hashlib.sha256((p.get("text") or "").encode()).hexdigest() == pkg["text_sha256"]]


# ------------------------------------------------------------------ prepare (the only path to a create call)
def prepare(st, cid, pkg, readback, pinned_sha, probe_url=None, loader=None, fetch=None, now=None):
    c = ts.cfg()
    if c["publishing"]["mode"] != "direct_delegated":
        raise PublishError(f"publishing mode is {c['publishing']['mode']!r}: direct scheduling is off")
    now = now or st.clock()
    d, sha = (loader or load_delegation)()
    check_delegation(d, sha, pinned_sha, now, cid, c)
    preflight_media(probe_url, fetch)
    if st.state(cid) not in ("authorised",):
        raise PublishError(f"{cid} is {st.state(cid)!r}: only an authorised video (QC_PASS, licences, verified URL) can be scheduled")
    if any(e["network"] for e in st.events(cid, "confirmation")):
        raise PublishError(f"{cid} already has confirmed networks: never create it again")
    if _events(st, cid, "created"):
        raise PublishError(f"{cid} was already created in Metricool: confirm or reconcile, never create twice")
    if _open_intent(st, cid):
        raise PublishError(f"{cid} has a create call with unknown outcome: run reconcile with a fresh read-back first")
    dup = duplicates(readback, pkg, c)
    if dup:
        raise PublishError(f"the calendar already has this video (posts {dup}): nothing created")
    attempts = len(_events(st, cid, "intent"))
    if attempts >= c["publishing"]["max_create_attempts"]:
        raise PublishError(f"{cid}: {attempts} create attempts already, limit reached")
    # one constant op: the three reservations belong to the video, so a retry after a PROVEN-absent create reuses them
    ticket = ts.schedule_check(st, cid, f"{cid}:publisher:schedule-check", readback, pkg,
                               verifier=delegation_verifier(pinned_sha, now, loader))
    st.spend(cid, "create_calls", 1, f"{cid}:create:{attempts + 1}", _token=ts._GATE)
    date, n = ts.parse_cid(cid)
    args = {"blogId": BRAND, "date": f"{date.isoformat()}T{c['slots'][str(n)]['time']}:00{_offset(date, n, c)}",
            "info": json.dumps(pkg["info"], ensure_ascii=False)}
    with st.lock():
        it = st._append({"kind": "intent", "cid": cid, "op": f"{cid}:intent:{attempts + 1}", "ticket": ticket["id"],
                         "tool": WRITE_TOOL, "args_sha256": hashlib.sha256(ts.canon(args).encode()).hexdigest(),
                         "delegation_sha": sha})
    return {"intent": it["id"], "tool": WRITE_TOOL, "arguments": args,
            "rule": "make exactly ONE call with these arguments; then `record` its raw answer, whatever it is"}


def _offset(date, n, c):
    o = ts.slot_instant(date, n, c).utcoffset()
    m = int(o.total_seconds() // 60)
    return f"{'+' if m >= 0 else '-'}{abs(m) // 60:02d}:{abs(m) % 60:02d}"


# ------------------------------------------------------------------ record / reconcile / confirm
def record(st, cid, intent, response):
    """Store what Metricool answered. Anything without a clear id+uuid is UNCERTAIN (maybe created)."""
    if intent not in {e["id"] for e in _open_intent(st, cid)}:
        raise PublishError("unknown or already closed intent")
    data = None
    if isinstance(response, str):
        try:
            response = json.loads(response)
        except ValueError:
            response = {"raw": response[:500]}
    if isinstance(response, dict):
        data = response.get("data", response)
    if isinstance(data, dict) and data.get("id") and data.get("uuid"):
        with st.lock():
            e = st._append({"kind": "created", "cid": cid, "intent": intent, "metricool_id": data["id"], "uuid": str(data["uuid"]),
                            "planner_url": data.get("plannerUrl")})
        return {"created": True, "metricool_id": data["id"], "uuid": str(data["uuid"]), "event": e["id"]}
    with st.lock():
        st._append({"kind": "create_uncertain", "cid": cid, "intent": intent, "answer": str(response)[:300]})
    return {"created": "unknown", "next": "read the calendar back and run reconcile; NEVER call create again before that"}


def reconcile(st, cid, readback, pkg, now=None):
    """Resolve an intent whose outcome is unknown, from a fresh full-day read-back."""
    c = ts.cfg()
    opened = _open_intent(st, cid)
    if not opened:
        return {"open_intents": 0}
    date, _ = ts.parse_cid(cid)
    good, why = ts.readback_covers(readback, date, now or st.clock(), c)
    if not good:
        raise PublishError(f"read-back refused: {why}")
    found = [p for p in readback.get("data", readback)
             if hashlib.sha256((p.get("text") or "").encode()).hexdigest() == pkg["text_sha256"]]
    it = opened[-1]["id"]
    if len(found) == 1:
        p = found[0]
        with st.lock():
            st._append({"kind": "created", "cid": cid, "intent": it, "metricool_id": p.get("id"), "uuid": str(p.get("uuid")),
                        "adopted": True})
        return {"adopted": p.get("id")}
    if len(found) > 1:
        st.fail(cid, "publish", f"duplicate posts for one video: {[p.get('id') for p in found]}")
        raise PublishError(f"DUPLICATE in Metricool for {cid}: {[p.get('id') for p in found]} — stop and report, nothing deleted")
    with st.lock():
        st._append({"kind": "create_absent", "cid": cid, "intent": it})
    return {"absent": True, "next": "a new prepare is allowed (attempt limit applies)"}


def confirm(st, cid, readback, pkg, fetch=None):
    created = _events(st, cid, "created")
    if not created:
        raise PublishError("nothing created for this video")
    cr = created[-1]
    return ts.confirm(st, cid, {"id": cr["metricool_id"], "uuid": cr["uuid"]}, readback, pkg, fetch=fetch,
                      op_prefix=f"{cid}:publisher")


# ------------------------------------------------------------------ daily report
def status(st, date):
    rows = []
    for n in (1, 2):
        cid = ts.content_id(dt.date.fromisoformat(date), n)
        conf = {e["network"]: e for e in st.events(cid, "confirmation")}
        cr = (_events(st, cid, "created") or [{}])[-1]
        arts = st.artifacts(cid)
        sel = st.refs(cid, "selected") or {}
        qc = "QC_PASS" if st.refs(cid, "qc_passed") is not None else ("QC_FAIL" if any(
            e["refs"].get("phase") == "qc" for e in st.events(cid, "state") if e["to"] == "failed") else "-")
        spend = sum(e["amount"] for e in st.events(cid, "spend") if e.get("kind2") == "voice_credits")
        fails = [e["refs"] for e in st.events(cid, "state") if e["to"] == "failed"]
        rows.append({"cid": cid, "play": sel.get("play_id"), "duration_s": (st.refs(cid, "qc_passed") or {}).get("duration"),
                     "qc": qc, "mp4_url": (st.refs(cid, "asset_ready") or {}).get("url"),
                     **{net: (conf[net]["status"].lower() if net in conf else ("error" if fails else "-")) for net in ts.NETWORKS},
                     "metricool_id": cr.get("metricool_id"), "slot": f"{date} {ts.cfg()['slots'][str(n)]['time']} Sydney",
                     "voice_credits": spend, "state": st.state(cid), "incidents": fails[-3:], "mp4": arts.get("mp4", {}).get("path")})
    return rows


# ------------------------------------------------------------------ CLI
def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("delegation"); p.add_argument("--sha", required=True)
    p = sp.add_parser("preflight"); p.add_argument("--sha", required=True); p.add_argument("--probe-url", required=True)
    p = sp.add_parser("authorise"); p.add_argument("cid"); p.add_argument("--sha", required=True); p.add_argument("--op", required=True)
    p = sp.add_parser("prepare"); p.add_argument("cid"); p.add_argument("--package", required=True); p.add_argument("--readback", required=True)
    p.add_argument("--sha", required=True); p.add_argument("--probe-url", required=True)
    p = sp.add_parser("record"); p.add_argument("cid"); p.add_argument("--intent", required=True); p.add_argument("--response", required=True)
    p = sp.add_parser("reconcile"); p.add_argument("cid"); p.add_argument("--readback", required=True); p.add_argument("--package", required=True)
    p = sp.add_parser("confirm"); p.add_argument("cid"); p.add_argument("--readback", required=True); p.add_argument("--package", required=True)
    p = sp.add_parser("status"); p.add_argument("date")
    a = ap.parse_args(argv)
    st = ts.Studio()
    j = lambda f: json.load(sys.stdin if f == "-" else open(f, encoding="utf-8"))  # noqa: E731
    try:
        if a.cmd == "delegation":
            d, sha = load_delegation()
            out = {**check_delegation(d, sha, a.sha, ts.now_utc()), "delegation": d}
        elif a.cmd == "preflight":
            d, sha = load_delegation()
            out = {**check_delegation(d, sha, a.sha, ts.now_utc()), "media_path": preflight_media(a.probe_url)}
        elif a.cmd == "authorise":
            out = authorise(st, a.cid, a.op, a.sha)
        elif a.cmd == "prepare":
            out = prepare(st, a.cid, j(a.package), j(a.readback), a.sha, a.probe_url)
        elif a.cmd == "record":
            raw = sys.stdin.read() if a.response == "-" else open(a.response, encoding="utf-8").read()
            out = record(st, a.cid, a.intent, raw)
        elif a.cmd == "reconcile":
            out = reconcile(st, a.cid, j(a.readback), j(a.package))
        elif a.cmd == "confirm":
            out = confirm(st, a.cid, j(a.readback), j(a.package))
        else:
            out = status(st, a.date)
        print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    except ts.StudioError as e:
        print(json.dumps({"error": str(e), "stop": True}, ensure_ascii=False))
        sys.exit(2)


if __name__ == "__main__":
    main()
