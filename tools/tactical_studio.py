#!/usr/bin/env python3
"""E2A Tactical Studio: resumable state for the two daily tactical videos (SHADOW until the owner activates it).

Two premium tactical videos per Sydney date, V01 at 10:00 and V02 at 13:00, each on Instagram Reels,
TikTok and YouTube Shorts (one MP4, three networks). This module is the single source of truth of the
production: every phase is an event in an APPEND-ONLY log, the current state is DERIVED from the log,
and every external step is idempotent. Nothing here calls a network: Metricool read-backs are files the
routine saved as they came.

States (owner brief 2026-11-12, Phase 12):
  candidate → researched → selected → scripted → storyboard_ready → audio_ready → rendered → qc_passed
  → asset_ready → authorised → scheduled_partial → scheduled_confirmed → published_confirmed
  → analytics_pending → analysed;  failed (with a reason) from anywhere.

Guarantees (each one has a test in tools/tests/test_tactical_studio.py):
  * Sydney time through zoneinfo (AEST/AEDT), never a fixed UTC offset.
  * Same operation id twice = no-op; a different target state with the same op id = error.
  * One reservation per `{content_id}:{network}:{date}:{slot}`; a second one is refused (no duplicates).
  * The narration is cached by the hash of the frozen script: a resumed run never pays for it again.
  * QC_PASS only when every mandatory check is present AND passed; any missing report = QC_FAIL.
  * Every audio/visual asset must have a known licence; an unknown origin fails QC.
  * `authorised` needs a delegation that the VERIFIER accepts. The default verifier is blocked: in shadow
    mode nothing can be authorised, so nothing can be scheduled.
  * `scheduled_confirmed` only with Metricool read-back evidence for all three networks at the right Sydney
    date and time; partial evidence = `scheduled_partial`, and confirmed networks are never redone.

CLI (all commands print JSON):
  plan [--now ISO] [--date YYYY-MM-DD]          target date, ids, slots in UTC, state and next phase per video
  advance CID STATE --op OP [--artifact k=path]… [--ref k=v]…
  fail CID --phase P --reason R [--op OP]
  voice-key SCRIPT_FILE | voice-lookup CID SCRIPT_FILE
  repeat-check --family F --variant V --concepts a,b [--date D] [--differential TEXT]
  register-play --play-id … --family … --variant … --concepts … --date … --cid … [--url …]
  qc CID --reports DIR --mp4 FILE
  reserve CID NETWORK --op OP
  package CID --mp4-url URL --caption FILE --titles FILE
  confirm CID --create FILE --readback FILE
  report DATE
"""
import argparse
import contextlib
import datetime as dt
import fcntl
import hashlib
import json
import os
import re
import sys
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CONFIG = os.path.join(ROOT, "config", "tactical_studio.json")
LICENCES = os.path.join(ROOT, "config", "asset_licences.json")
STATE = os.environ.get("E2A_STUDIO_STATE", os.path.join(ROOT, "state", "tactical"))
NETWORKS = ("instagram", "tiktok", "youtube")

FLOW = ["candidate", "researched", "selected", "scripted", "storyboard_ready", "audio_ready", "rendered",
        "qc_passed", "asset_ready", "authorised", "scheduled_partial", "scheduled_confirmed",
        "published_confirmed", "analytics_pending", "analysed"]
STATES = set(FLOW) | {"failed"}
# a state may also be re-entered after `failed` from the state before the failure (resume)
QC_REQUIRED = ("tactical", "engine", "audio", "technical", "frames", "licences")


class StudioError(ValueError):
    pass


def cfg():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def sydney(c=None):
    return ZoneInfo((c or cfg())["timezone"])


def now_utc():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def parse_ts(v):
    t = dt.datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise StudioError("timestamp without a time zone")
    return t


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ calendar
def target_date(now=None, c=None):
    """The routine runs the day before (17:00 Sydney). Before the cutoff (09:00) a run still targets today."""
    c = c or cfg()
    loc = (now or now_utc()).astimezone(sydney(c))
    hh, mm = map(int, c["production_cutoff_local"].split(":"))
    return loc.date() if (loc.hour, loc.minute) < (hh, mm) else loc.date() + dt.timedelta(days=1)


def content_id(date, n, c=None):
    return (c or cfg())["content_id"].format(date=date.isoformat() if hasattr(date, "isoformat") else date, n=int(n))


def slot_instant(date, n, c=None):
    """Sydney wall-clock slot → aware datetime (zoneinfo resolves AEST/AEDT for that very date)."""
    c = c or cfg()
    d = date if isinstance(date, dt.date) else dt.date.fromisoformat(date)
    hh, mm = map(int, c["slots"][str(int(n))]["time"].split(":"))
    return dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=sydney(c))


def parse_cid(cid):
    m = re.fullmatch(r"E2A-TACTICAL-(\d{4}-\d{2}-\d{2})-V(\d{2})", cid)
    if not m:
        raise StudioError(f"bad content id {cid!r}")
    return dt.date.fromisoformat(m.group(1)), int(m.group(2))


# ------------------------------------------------------------------ append-only log
class Studio:
    def __init__(self, state_dir=None, clock=None):
        self.dir = state_dir or STATE
        os.makedirs(self.dir, exist_ok=True)
        self.log = os.path.join(self.dir, "events.jsonl")
        self.clock = clock or now_utc

    @contextlib.contextmanager
    def lock(self):
        with open(os.path.join(self.dir, ".lock"), "a") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)

    def events(self, cid=None, kind=None):
        out = []
        if not os.path.exists(self.log):
            return out
        with open(self.log, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue  # a truncated last line (cut mid-write) never invalidates the rest
                if (cid is None or e.get("cid") == cid) and (kind is None or e.get("kind") == kind):
                    out.append(e)
        return out

    def _append(self, e):
        e = {"at": self.clock().isoformat(), **e}
        with open(self.log, "a", encoding="utf-8") as f:
            f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return e

    # -------------------------------------------------------------- states
    def state(self, cid):
        st = [e for e in self.events(cid, "state")]
        return st[-1]["to"] if st else None

    def last_good(self, cid):
        for e in reversed(self.events(cid, "state")):
            if e["to"] != "failed":
                return e["to"]
        return None

    def _allowed(self, cid, to):
        cur = self.state(cid)
        if to == "failed":
            return True
        if to not in STATES:
            raise StudioError(f"unknown state {to!r}")
        base = self.last_good(cid) if cur == "failed" else cur
        if base is None:
            return to == "candidate"
        i, j = FLOW.index(base), FLOW.index(to)
        if to == "scheduled_confirmed" and base in ("authorised", "scheduled_partial"):
            return True
        if to == "analytics_pending" and base == "scheduled_confirmed":
            return False  # needs published_confirmed first
        return j == i + 1 or (cur == "failed" and j == i + 1)

    def advance(self, cid, to, op, artifacts=None, refs=None, _guard=None):
        parse_cid(cid)
        with self.lock():
            prev = [e for e in self.events(cid, "state") if e["op"] == op]
            if prev:
                if prev[-1]["to"] == to:
                    return {"idempotent": True, **prev[-1]}
                raise StudioError(f"operation {op!r} already moved {cid} to {prev[-1]['to']!r}")
            if _guard:
                _guard()
            if not self._allowed(cid, to):
                raise StudioError(f"{cid}: {self.state(cid)!r} → {to!r} is not allowed")
            arts = {}
            for k, p in (artifacts or {}).items():
                if not os.path.exists(p):
                    raise StudioError(f"artifact {k} missing: {p}")
                arts[k] = {"path": os.path.relpath(p, ROOT) if os.path.isabs(p) else p, "sha256": sha256(p)}
            return self._append({"kind": "state", "cid": cid, "to": to, "op": op, "artifacts": arts, "refs": refs or {}})

    def fail(self, cid, phase, reason, op=None, retry_after=None):
        with self.lock():
            n = len([e for e in self.events(cid, "state") if e["to"] == "failed" and e["refs"].get("phase") == phase])
            refs = {"phase": phase, "reason": reason, "attempt": n + 1}
            if retry_after:
                refs["retry_after"] = parse_ts(retry_after).isoformat()
            return self._append({"kind": "state", "cid": cid, "to": "failed", "op": op or f"{cid}:fail:{phase}:{n + 1}",
                                 "artifacts": {}, "refs": refs})

    def attempts(self, cid, phase):
        return len([e for e in self.events(cid, "state") if e["to"] == "failed" and e["refs"].get("phase") == phase])

    def artifacts(self, cid):
        out = {}
        for e in self.events(cid, "state"):
            out.update(e.get("artifacts") or {})
        return out

    def next_phase(self, cid, c=None):
        c = c or cfg()
        cur = self.state(cid)
        if cur == "failed":
            last = self.events(cid, "state")[-1]["refs"]
            if self.attempts(cid, last.get("phase")) > c["retries_per_phase"]:
                return {"action": "stop", "why": f"phase {last.get('phase')} failed {self.attempts(cid, last.get('phase'))} times: report, no loops"}
            ra = last.get("retry_after")
            if ra and self.clock() < parse_ts(ra):
                return {"action": "wait", "until": ra}
            base = self.last_good(cid)
            return {"action": "retry", "phase": FLOW[FLOW.index(base) + 1] if base else "candidate"}
        if cur is None:
            return {"action": "run", "phase": "candidate"}
        if cur in ("analysed",):
            return {"action": "done"}
        return {"action": "run", "phase": FLOW[FLOW.index(cur) + 1] if cur != "scheduled_partial" else "scheduled_confirmed"}

    # -------------------------------------------------------------- narration cache (never pay twice)
    @staticmethod
    def voice_key(script_text):
        norm = re.sub(r"\s+", " ", script_text.strip())
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:16]

    def voice_lookup(self, cid, script_text):
        """A valid narration for THIS frozen script, if one was already paid for (any earlier run)."""
        key = self.voice_key(script_text)
        for e in reversed(self.events(cid, "state")):
            a = (e.get("artifacts") or {}).get("voice")
            if e["to"] == "audio_ready" and a and e["refs"].get("script_key") == key:
                p = a["path"] if os.path.isabs(a["path"]) else os.path.join(ROOT, a["path"])
                if os.path.exists(p) and sha256(p) == a["sha256"]:
                    return {"reuse": True, "path": a["path"], "script_key": key}
        return {"reuse": False, "script_key": key}

    # -------------------------------------------------------------- reservations (no duplicates)
    @staticmethod
    def slot_key(cid, network):
        date, n = parse_cid(cid)
        return f"{cid}:{network}:{date.isoformat()}:{cfg()['slots'][str(n)]['time']}"

    def reserve(self, cid, network, op):
        if network not in NETWORKS:
            raise StudioError(f"unknown network {network!r}")
        key = self.slot_key(cid, network)
        with self.lock():
            for e in self.events(cid, "reservation"):
                if e["key"] == key:
                    if e["op"] == op:
                        return {"idempotent": True, **e}
                    raise StudioError(f"{key} is already reserved by {e['op']}: no second schedule")
            return self._append({"kind": "reservation", "cid": cid, "key": key, "network": network, "op": op})

    # -------------------------------------------------------------- budget (advisory counter, see config)
    def spend(self, cid, kind, amount, op):
        with self.lock():
            if any(e["op"] == op for e in self.events(kind="spend")):
                return {"idempotent": True}
            date, _ = parse_cid(cid)
            lim = cfg()["budget_per_day"].get(kind)
            used = sum(e["amount"] for e in self.events(kind="spend") if e["kind2"] == kind and e["date"] == date.isoformat())
            if lim is not None and used + amount > lim:
                raise StudioError(f"budget {kind}: {used}+{amount} > {lim} for {date}")
            return self._append({"kind": "spend", "cid": cid, "kind2": kind, "amount": amount, "date": date.isoformat(), "op": op})

    # -------------------------------------------------------------- delegation
    def authorise(self, cid, verifier, op):
        """`authorised` only if the verifier accepts a live delegation for this id, date, slot and networks."""
        date, n = parse_cid(cid)
        scope = {"cid": cid, "date": date.isoformat(), "slot": cfg()["slots"][str(n)]["time"], "networks": list(NETWORKS)}

        def guard():
            ok, why = verifier(scope)
            if not ok:
                raise StudioError(f"not authorised: {why}")
        return self.advance(cid, "authorised", op, refs={"scope": scope}, _guard=guard)


def blocked_verifier(scope):
    return False, "no delegation mechanism outside the agent's reach is active (shadow mode)"


# ------------------------------------------------------------------ anti-repetition
def plays_log():
    return os.path.join(STATE, "plays.jsonl")


def read_plays(path=None):
    p = path or plays_log()
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def repeat_check(family, variant, concepts, date, differential=None, plays=None, c=None):
    """Blocks a concept already used within the window. Compares meaning (family, variant, concept tags),
    not titles: renaming a play does not get it through."""
    c = c or cfg()
    d = date if isinstance(date, dt.date) else dt.date.fromisoformat(date)
    win = dt.timedelta(days=c["repeat_window_days"])
    cs = {x.strip().lower() for x in concepts if x.strip()}
    hits = []
    for p in plays if plays is not None else read_plays():
        used = dt.date.fromisoformat(p["date"])
        if not (d - win <= used <= d + win):
            continue
        pc = {x.lower() for x in p.get("concepts", [])}
        overlap = len(cs & pc) / max(1, len(cs | pc))
        same_family = p["family"].lower() == family.lower()
        same_variant = same_family and p["variant"].lower() == variant.lower()
        if same_variant or overlap >= c["concept_overlap_block"]:
            hits.append({"play_id": p["play_id"], "date": p["date"], "why": "same family and variant" if same_variant else f"concept overlap {overlap:.2f}"})
        elif same_family:
            hits.append({"play_id": p["play_id"], "date": p["date"], "why": "same family, different variant", "soft": True})
    hard = [h for h in hits if not h.get("soft")]
    soft = [h for h in hits if h.get("soft")]
    if hard:
        return {"ok": False, "blocked_by": hard}
    if soft and not differential:
        return {"ok": False, "blocked_by": soft, "fix": "explain the differential value of this variant (--differential)"}
    return {"ok": True, "related": soft, "differential": differential}


def register_play(entry, path=None):
    need = ["play_id", "canonical", "family", "variant", "concepts", "date", "cid"]
    miss = [k for k in need if not entry.get(k)]
    if miss:
        raise StudioError(f"play entry missing {miss}")
    p = path or plays_log()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if any(x["play_id"] == entry["play_id"] and x["cid"] == entry["cid"] for x in read_plays(p)):
        return {"idempotent": True}
    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return entry


# ------------------------------------------------------------------ QC aggregate
def _load(d, name):
    p = os.path.join(d, f"{name}.json")
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def licence_check(manifest, known=None):
    """Every asset in the episode manifest must map to a known licence (owned, generated on E2A's account,
    or a licence file). Unknown origin = fail; never inferred."""
    if known is None:
        with open(LICENCES, encoding="utf-8") as f:
            known = json.load(f)["assets"]
    bad = []
    for a in manifest.get("assets", []):
        k = known.get(a["src"]) or next((v for pat, v in known.items() if pat.endswith("*") and a["src"].startswith(pat[:-1])), None)
        if not k or k.get("commercial_use") is not True:
            bad.append({"src": a["src"], "why": "unknown origin" if not k else f"commercial use: {k.get('commercial_use')}"})
    return {"pass": not bad, "failures": bad, "checked": len(manifest.get("assets", []))}


def qc_aggregate(reports_dir, mp4=None, c=None):
    """QC_PASS only if every mandatory report exists and passes. Missing report = QC_FAIL (never skipped)."""
    c = c or cfg()
    out = {"checks": {}, "mp4_sha256": sha256(mp4) if mp4 and os.path.exists(mp4) else None}
    for name in QC_REQUIRED:
        r = _load(reports_dir, name)
        if r is None:
            out["checks"][name] = {"pass": False, "why": "report missing"}
            continue
        if name == "tactical":
            ok = r.get("failed", 1) == 0 and r.get("passed", 0) > 0
        elif name == "engine":
            ok = r.get("failed", 1) == 0 and r.get("passed", 0) > 0
        elif name == "audio":
            mix = r.get("mix", {})
            ok = (abs(mix.get("I", 0) - c["audio"]["lufs_target"]) <= c["audio"]["lufs_tolerance"]
                  and mix.get("TP", 0) <= c["audio"]["true_peak_max"]
                  and r.get("worst_sfx_vs_word_db", 99) < 0
                  and not r.get("silences_inside_narration"))
        elif name == "technical":
            v = c["video"]
            ok = (r.get("width") == v["width"] and r.get("height") == v["height"] and r.get("fps", 0) >= v["fps_min"]
                  and r.get("vcodec") == v["vcodec"] and r.get("acodec") == v["acodec"]
                  and c["duration_s"]["min"] <= r.get("duration", 0) <= c["duration_s"]["max"]
                  and r.get("black_frames", 1) == 0 and r.get("social_mb", 99) <= v["social_max_mb"])
        elif name == "frames":
            ok = r.get("extracted_from_mp4") is True and r.get("count", 0) >= 6 and not r.get("issues")
        elif name == "licences":
            ok = r.get("pass") is True
        out["checks"][name] = {"pass": bool(ok)}
    out["result"] = "QC_PASS" if all(v["pass"] for v in out["checks"].values()) else "QC_FAIL"
    return out


# ------------------------------------------------------------------ publication package + confirmation
def package(cid, mp4_url, caption, titles, c=None):
    """ONE Metricool post per video with the three networks (same MP4, metadata per network).
    In shadow mode this is only written to disk; the routine never calls a write tool."""
    c = c or cfg()
    date, n = parse_cid(cid)
    lab = c["ai_labels"]
    info = {
        "autoPublish": True, "draft": False, "descendants": [], "firstCommentText": "", "hasNotReadNotes": False,
        "media": [mp4_url], "mediaAltText": [], "shortener": False, "smartLinkData": {"ids": []},
        "providers": [{"network": x} for x in NETWORKS],
        "publicationDate": {"dateTime": f"{date.isoformat()}T{c['slots'][str(n)]['time']}:00", "timezone": c["timezone"]},
        "text": caption,
        "instagramData": {"type": "REEL", "showReelOnFeed": True, "isAiGenerated": lab["instagram_isAiGenerated"]},
        "tiktokData": {"privacyOption": "PUBLIC_TO_EVERYONE", "title": titles["tiktok"], "isAigc": lab["tiktok_isAigc"]},
        "youtubeData": {"title": titles["youtube"], "type": "short", "privacy": "public", "category": "SPORTS",
                        "madeForKids": False, "isAiGeneratedContent": lab["youtube_isAiGeneratedContent"],
                        "tags": titles.get("tags", [])},
    }
    if not titles["youtube"].endswith("#shorts") or len(titles["youtube"]) > 100:
        raise StudioError("YouTube title must end with #shorts and be ≤ 100 characters")
    if info["instagramData"]["type"] != "REEL":
        raise StudioError("Instagram must be a Reel (no Trial Reels)")
    return {"cid": cid, "mode": c["publishing"]["mode"], "date": date.isoformat(), "info": info,
            "text_sha256": hashlib.sha256(caption.encode()).hexdigest(),
            "keys": [f"{cid}:{x}:{date.isoformat()}:{c['slots'][str(n)]['time']}" for x in NETWORKS]}


def confirm(studio, cid, create_resp, readback, pkg, op_prefix=None):
    """Read-back confirmation. A network counts only if the read-back shows the SAME Metricool post (id or uuid
    from the create answer), that network, the slot's Sydney date and time, the same caption and a non-error
    status. Confirmed networks are kept; nothing is ever redone."""
    date, n = parse_cid(cid)
    slot = f"{date.isoformat()}T{cfg()['slots'][str(n)]['time']}:00"
    cr = create_resp.get("data", create_resp)
    want_ids = {str(cr.get("id")), str(cr.get("uuid"))} - {"None"}
    posts = readback.get("data", readback)
    mine = [p for p in posts if {str(p.get("id")), str(p.get("uuid"))} & want_ids]
    already = {e["network"] for e in studio.events(cid, "confirmation")}
    got, problems = set(already), []
    if len(mine) > 1:
        problems.append("the read-back shows the post twice: duplicate, confirm nothing and report")
        mine = []
    for p in mine:
        pd = p.get("publicationDate", {})
        if pd.get("dateTime") != slot or pd.get("timezone") != cfg()["timezone"]:
            problems.append(f"wrong slot {pd}")
            continue
        if hashlib.sha256(p.get("text", "").encode()).hexdigest() != pkg["text_sha256"]:
            problems.append("caption differs from the package")
            continue
        for prov in p.get("providers", []):
            net = prov.get("network")
            if net not in NETWORKS or net in got:
                continue
            if str(prov.get("status", "")).upper() in ("ERROR", "FAILED", "REJECTED"):
                problems.append(f"{net}: {prov.get('status')} {prov.get('detailedStatus', '')}")
                continue
            with studio.lock():
                studio._append({"kind": "confirmation", "cid": cid, "network": net, "metricool_id": p.get("id"),
                                "uuid": p.get("uuid"), "status": prov.get("status"), "public_url": prov.get("publicUrl")})
            got.add(net)
    st = studio.state(cid)
    target = "scheduled_confirmed" if got >= set(NETWORKS) else ("scheduled_partial" if got else None)
    if target and st != target and studio._allowed(cid, target):
        studio.advance(cid, target, f"{op_prefix or cid}:{target}", refs={"networks": sorted(got)})
    return {"confirmed": sorted(got), "missing": sorted(set(NETWORKS) - got), "problems": problems, "state": studio.state(cid)}


def collisions(readback, date, c=None):
    """Existing Metricool posts on the target Sydney date at our slots (or within 60 min of them).
    They are reported and kept: the studio never cancels or moves a post; a taken slot blocks that video."""
    c = c or cfg()
    d = date if isinstance(date, dt.date) else dt.date.fromisoformat(date)
    out = []
    for p in readback.get("data", readback):
        pd = p.get("publicationDate", {})
        try:
            t = dt.datetime.fromisoformat(pd["dateTime"]).replace(tzinfo=ZoneInfo(pd.get("timezone") or c["timezone"]))
        except (KeyError, ValueError):
            continue
        for n in (1, 2):
            s = slot_instant(d, n, c)
            if abs((t - s).total_seconds()) <= 3600:
                nets = sorted(x.get("network") for x in p.get("providers", []))
                video = (p.get("instagramData") or {}).get("type") in ("REEL", "TRIAL_REEL") or "tiktok" in nets or "youtube" in nets
                out.append({"slot": n, "metricool_id": p.get("id"), "at": pd, "networks": nets, "video": video,
                            "blocks": video})
    return out


# ------------------------------------------------------------------ CLI
def _kv(items):
    out = {}
    for it in items or []:
        k, _, v = it.partition("=")
        out[k] = v
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("plan"); p.add_argument("--now"); p.add_argument("--date")
    p = sp.add_parser("advance"); p.add_argument("cid"); p.add_argument("state"); p.add_argument("--op", required=True)
    p.add_argument("--artifact", action="append"); p.add_argument("--ref", action="append")
    p = sp.add_parser("fail"); p.add_argument("cid"); p.add_argument("--phase", required=True); p.add_argument("--reason", required=True)
    p.add_argument("--op"); p.add_argument("--retry-after")
    p = sp.add_parser("voice-key"); p.add_argument("script")
    p = sp.add_parser("voice-lookup"); p.add_argument("cid"); p.add_argument("script")
    p = sp.add_parser("repeat-check"); p.add_argument("--family", required=True); p.add_argument("--variant", required=True)
    p.add_argument("--concepts", required=True); p.add_argument("--date"); p.add_argument("--differential")
    p = sp.add_parser("register-play")
    for k in ("play-id", "canonical", "family", "variant", "concepts", "date", "cid"):
        p.add_argument(f"--{k}", required=True)
    p.add_argument("--url"); p.add_argument("--sources", default="")
    p = sp.add_parser("qc"); p.add_argument("cid"); p.add_argument("--reports", required=True); p.add_argument("--mp4")
    p = sp.add_parser("licences"); p.add_argument("manifest")
    p = sp.add_parser("reserve"); p.add_argument("cid"); p.add_argument("network"); p.add_argument("--op", required=True)
    p = sp.add_parser("package"); p.add_argument("cid"); p.add_argument("--mp4-url", required=True)
    p.add_argument("--caption", required=True); p.add_argument("--titles", required=True); p.add_argument("--out")
    p = sp.add_parser("confirm"); p.add_argument("cid"); p.add_argument("--create", required=True)
    p.add_argument("--readback", required=True); p.add_argument("--package", required=True)
    p = sp.add_parser("report"); p.add_argument("date")
    a = ap.parse_args(argv)
    s = Studio()
    c = cfg()
    if a.cmd == "plan":
        d = dt.date.fromisoformat(a.date) if a.date else target_date(parse_ts(a.now) if a.now else None, c)
        vids = []
        for n in (1, 2):
            cid = content_id(d, n, c)
            vids.append({"cid": cid, "slot_sydney": c["slots"][str(n)]["time"], "slot_utc": slot_instant(d, n, c).astimezone(dt.timezone.utc).isoformat(),
                         "label": c["slots"][str(n)]["label"], "state": s.state(cid), "next": s.next_phase(cid, c),
                         "artifacts": sorted(s.artifacts(cid))})
        out = {"target_date": d.isoformat(), "mode": c["publishing"]["mode"], "videos": vids}
    elif a.cmd == "advance":
        out = s.advance(a.cid, a.state, a.op, _kv(a.artifact), _kv(a.ref))
    elif a.cmd == "fail":
        out = s.fail(a.cid, a.phase, a.reason, a.op, a.retry_after)
    elif a.cmd == "voice-key":
        out = {"script_key": Studio.voice_key(open(a.script, encoding="utf-8").read())}
    elif a.cmd == "voice-lookup":
        out = s.voice_lookup(a.cid, open(a.script, encoding="utf-8").read())
    elif a.cmd == "repeat-check":
        out = repeat_check(a.family, a.variant, a.concepts.split(","), a.date or target_date().isoformat(), a.differential)
    elif a.cmd == "register-play":
        out = register_play({"play_id": a.play_id, "canonical": a.canonical, "family": a.family, "variant": a.variant,
                             "concepts": [x.strip() for x in a.concepts.split(",") if x.strip()], "date": a.date, "cid": a.cid,
                             "url": a.url, "sources": [x for x in a.sources.split(",") if x]})
    elif a.cmd == "qc":
        out = qc_aggregate(a.reports, a.mp4, c)
        with open(os.path.join(a.reports, "qc.json"), "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
    elif a.cmd == "licences":
        out = licence_check(json.load(open(a.manifest, encoding="utf-8")))
    elif a.cmd == "reserve":
        out = s.reserve(a.cid, a.network, a.op)
    elif a.cmd == "package":
        out = package(a.cid, a.mp4_url, open(a.caption, encoding="utf-8").read().strip(), json.load(open(a.titles, encoding="utf-8")), c)
        if a.out:
            json.dump(out, open(a.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    elif a.cmd == "confirm":
        out = confirm(s, a.cid, json.load(open(a.create)), json.load(open(a.readback)), json.load(open(a.package)))
    elif a.cmd == "report":
        out = {"date": a.date, "videos": []}
        for n in (1, 2):
            cid = content_id(a.date, n, c)
            out["videos"].append({"cid": cid, "slot": c["slots"][str(n)]["time"], "state": s.state(cid),
                                  "confirmations": [{k: e.get(k) for k in ("network", "metricool_id", "status", "public_url")} for e in s.events(cid, "confirmation")],
                                  "failures": [e["refs"] for e in s.events(cid, "state") if e["to"] == "failed"]})
        out["spend"] = [e for e in s.events(kind="spend") if e["date"] == a.date]
    print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except StudioError as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(2)
