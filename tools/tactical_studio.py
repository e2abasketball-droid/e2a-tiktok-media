#!/usr/bin/env python3
"""E2A Tactical Studio: resumable, gated production of the two daily tactical videos (SHADOW until activated).

Two premium tactical videos per Sydney date, V01 at 10:00 and V02 at 13:00, each on Instagram Reels,
TikTok and YouTube Shorts (one MP4, three networks). Every phase is an event in an APPEND-ONLY,
HASH-CHAINED log; the current state is DERIVED from the log.

v2 (owner review 2026-11-12 21:14Z) — the controls are in the production path, not in the prompt:
  * `advance` can only reach the FREE states (candidate, researched, analytics_*). Every other state is
    reachable only through its gate command, which runs the real check itself:
        selected          select       repeat check (45 days, concepts) + play registry
        scripted          script       structure HOOK/SETUP/CASE A/CASE B|COUNTER/TAKEAWAY/CTA, 30–40 s estimate
        storyboard_ready  storyboard   runs scripts/test-play.mts on the plays: 0 failures, ≥1 claim per play
        audio_ready       audio        voice permit (budget) or cached take; transcript matches the frozen script
        rendered          render       licence gate on every media file BEFORE rendering, render budget,
                                       runs Remotion + the social encode itself, hashes the MP4
        qc_passed         qc           measures the MP4 itself (ffprobe, EBU R128, blackdetect, silences,
                                       frames) + tactical and engine validators + licences; MP4 hash must
                                       be the rendered one
        asset_ready       asset        downloads the public URL and compares SHA-256 and size with the QC'd MP4
        authorised        authorise    the configured verifier (blocked in shadow)
        scheduled_*       confirm      read-back: same post, slot, caption, MEDIA BYTES, real status per network;
                                       a post waiting for approval is NOT scheduled
        published_confirmed published  every network PUBLISHED with a public URL on its own domain
  * `schedule-check` is mandatory before any create call: it re-runs the verifier live (the `authorised`
    event alone is never trusted), needs a fresh read-back of the WHOLE Sydney date and blocks on ANY
    existing post (static posts included) near the slot on our networks. `confirm` refuses without a
    valid ticket for the same package.
  * Budgets (voice takes and credits, renders) are enforced inside `voice-permit` and `render`.

What this module can NOT guarantee (see produccion/tactical/ACTIVACION.md): an agent with shell access
can edit any local file or call a connector directly. The log detects edits (hash chain) and the sync
refuses diverged histories, but the hard controls are outside the agent: the routine's permitted_tools
(only createScheduledPostForReview), the human approval in Metricool, and branch protection on the
state branch.
"""
import argparse
import contextlib
import datetime as dt
import difflib
import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE = os.path.join(ROOT, "template")
CONFIG = os.path.join(ROOT, "config", "tactical_studio.json")
LICENCES = os.path.join(ROOT, "config", "asset_licences.json")
STATE = os.environ.get("E2A_STUDIO_STATE", os.path.join(ROOT, "state", "tactical"))
NETWORKS = ("instagram", "tiktok", "youtube")
CHROME = "/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell"

FLOW = ["candidate", "researched", "selected", "scripted", "storyboard_ready", "audio_ready", "rendered",
        "qc_passed", "asset_ready", "authorised", "scheduled_partial", "scheduled_confirmed",
        "published_confirmed", "analytics_pending", "analysed"]
STATES = set(FLOW) | {"failed"}
FREE = {"candidate", "researched", "analytics_pending", "analysed"}
GATED = set(FLOW) - FREE
QC_REQUIRED = ("tactical", "engine", "audio", "technical", "frames", "licences")
SECTIONS = ("HOOK", "SETUP", "CASE A", "CASE B", "COUNTER", "TAKEAWAY", "CTA")
# Metricool provider statuses that mean "really scheduled" / "really published". Anything else (unknown,
# awaiting approval, draft, error) is never confirmed.
SCHEDULED_OK = {"PENDING"}
PUBLISHED_OK = {"PUBLISHED"}
PUBLIC_DOMAINS = {"instagram": ("instagram.com",), "tiktok": ("tiktok.com",), "youtube": ("youtube.com", "youtu.be")}
_GATE = object()  # only the gate functions of this module hold it


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


def canon(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _abs(p):
    return p if os.path.isabs(p) else os.path.join(ROOT, p)


def _rel(p):
    a = os.path.abspath(p)
    return os.path.relpath(a, ROOT) if a.startswith(ROOT + os.sep) else a


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
    c = c or cfg()
    d = date if isinstance(date, dt.date) else dt.date.fromisoformat(date)
    hh, mm = map(int, c["slots"][str(int(n))]["time"].split(":"))
    return dt.datetime(d.year, d.month, d.day, hh, mm, tzinfo=sydney(c))


def parse_cid(cid):
    m = re.fullmatch(r"E2A-TACTICAL-(\d{4}-\d{2}-\d{2})-V(\d{2})", cid)
    if not m:
        raise StudioError(f"bad content id {cid!r}")
    return dt.date.fromisoformat(m.group(1)), int(m.group(2))


# ------------------------------------------------------------------ append-only, hash-chained log
class Studio:
    def __init__(self, state_dir=None, clock=None):
        self.dir = state_dir or STATE
        os.makedirs(self.dir, exist_ok=True)
        self.log = os.path.join(self.dir, "events.jsonl")
        self.plays = os.path.join(self.dir, "plays.jsonl")
        self.clock = clock or now_utc

    @contextlib.contextmanager
    def lock(self):
        with open(os.path.join(self.dir, ".lock"), "a") as fh:
            fcntl.flock(fh, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fh, fcntl.LOCK_UN)

    def raw_events(self):
        out = []
        if not os.path.exists(self.log):
            return out
        with open(self.log, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue  # a truncated last line (cut mid-write) never invalidates the rest
        return out

    def events(self, cid=None, kind=None):
        return [e for e in self.raw_events()
                if (cid is None or e.get("cid") == cid) and (kind is None or e.get("kind") == kind)]

    @staticmethod
    def event_id(e):
        return hashlib.sha256(canon({k: v for k, v in e.items() if k != "id"}).encode()).hexdigest()

    def verify_chain(self):
        """Every event carries the hash of the previous one and its own hash: an edited, removed or
        reordered line breaks the chain."""
        prev = None
        for i, e in enumerate(self.raw_events()):
            if e.get("prev") != prev:
                return {"ok": False, "at": i, "why": "prev hash does not match the previous event"}
            if e.get("id") != self.event_id(e):
                return {"ok": False, "at": i, "why": "event content was changed after it was written"}
            prev = e["id"]
        return {"ok": True, "events": len(self.raw_events()), "head": prev}

    def _append(self, e):
        ev = self.raw_events()
        chk = self.verify_chain()
        if not chk["ok"]:
            raise StudioError(f"log integrity broken ({chk['why']} at line {chk['at']}): stop, nothing written")
        e = {"at": self.clock().isoformat(), "seq": len(ev), "prev": ev[-1]["id"] if ev else None, **e}
        e["id"] = self.event_id(e)
        with open(self.log, "a", encoding="utf-8") as f:
            f.write(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n")
            f.flush()
            os.fsync(f.fileno())
        return e

    # -------------------------------------------------------------- states
    def state(self, cid):
        st = self.events(cid, "state")
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
        if to == "analytics_pending" and base != "published_confirmed":
            return False
        return j == i + 1

    def advance(self, cid, to, op, artifacts=None, refs=None):
        """Public entry: FREE states only. Sensitive states have their own gate command."""
        if to in GATED:
            raise StudioError(f"{to!r} can only be reached through its gate command, never with advance")
        return self._advance(cid, to, op, artifacts, refs, _token=_GATE)

    def _advance(self, cid, to, op, artifacts=None, refs=None, _token=None, _guard=None):
        if _token is not _GATE:
            raise StudioError("internal transition without a gate")
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
                if not os.path.exists(_abs(p)):
                    raise StudioError(f"artifact {k} missing: {p}")
                arts[k] = {"path": _rel(_abs(p)), "sha256": sha256(_abs(p)), "bytes": os.path.getsize(_abs(p))}
            return self._append({"kind": "state", "cid": cid, "to": to, "op": op, "artifacts": arts, "refs": refs or {}})

    def fail(self, cid, phase, reason, op=None, retry_after=None):
        with self.lock():
            n = self.attempts(cid, phase)
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

    def refs(self, cid, state):
        for e in reversed(self.events(cid, "state")):
            if e["to"] == state:
                return e["refs"]
        return None

    def require(self, cid, *states):
        cur = self.state(cid)
        base = self.last_good(cid) if cur == "failed" else cur
        if base not in states:
            raise StudioError(f"{cid} is {cur!r}; this step needs {' or '.join(states)}")
        return base

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
        if cur == "analysed":
            return {"action": "done"}
        return {"action": "run", "phase": FLOW[FLOW.index(cur) + 1] if cur != "scheduled_partial" else "scheduled_confirmed"}

    # -------------------------------------------------------------- narration cache (never pay twice)
    @staticmethod
    def voice_key(script_text):
        return hashlib.sha256(spoken_text(script_text).encode("utf-8")).hexdigest()[:16]

    def voice_lookup(self, cid, script_text):
        key = self.voice_key(script_text)
        for e in reversed(self.events(cid, "state")):
            a = (e.get("artifacts") or {}).get("voice")
            if e["to"] == "audio_ready" and a and e["refs"].get("script_key") == key:
                p = _abs(a["path"])
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

    # -------------------------------------------------------------- budget (ENFORCED: only gates call it)
    def spend(self, cid, kind, amount, op, _token=None):
        if _token is not _GATE:
            raise StudioError("spend is recorded by the gate that spends (voice-permit, render)")
        with self.lock():
            if any(e["op"] == op for e in self.events(kind="spend")):
                return {"idempotent": True}
            date, _ = parse_cid(cid)
            lim = cfg()["budget_per_day"].get(kind)
            if lim is None:
                raise StudioError(f"no budget defined for {kind!r}: refused")
            used = sum(e["amount"] for e in self.events(kind="spend") if e["kind2"] == kind and e["date"] == date.isoformat())
            if used + amount > lim:
                raise StudioError(f"budget {kind}: {used}+{amount} > {lim} for {date}")
            return self._append({"kind": "spend", "cid": cid, "kind2": kind, "amount": amount, "date": date.isoformat(), "op": op})


# ------------------------------------------------------------------ verifiers (authorisation)
def blocked_verifier(scope):
    return False, "no delegation mechanism outside the agent's reach is active (shadow mode)"


def metricool_review_verifier(scope):
    """Supervised / limited autonomy: the create call is only a REQUEST for review; the human approval
    happens in Metricool, outside the agent, and `confirm` only counts an approved, scheduled post."""
    mode = cfg()["publishing"]["mode"]
    if mode not in ("supervised", "limited_autonomy"):
        return False, f"publishing mode is {mode!r}"
    return True, "review request only: approval is given by a human in Metricool"


VERIFIERS = {"blocked": blocked_verifier, "metricool_review": metricool_review_verifier}


def configured_verifier():
    return VERIFIERS.get(cfg()["delegation"]["verifier"], blocked_verifier)


# ------------------------------------------------------------------ anti-repetition
def read_plays(path):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def repeat_check(family, variant, concepts, date, differential=None, plays=None, c=None):
    """Blocks a concept already used within the window. Compares meaning (family, variant, concept tags),
    not titles: renaming a play does not get it through."""
    c = c or cfg()
    d = date if isinstance(date, dt.date) else dt.date.fromisoformat(date)
    win = dt.timedelta(days=c["repeat_window_days"])
    cs = {x.strip().lower() for x in concepts if x.strip()}
    hits = []
    for p in plays or []:
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


def select(st, cid, op, play_id, family, variant, concepts, differential=None, sources=()):
    """GATE selected: the repetition check runs here, against the persistent play registry."""
    st.require(cid, "researched")
    date, _ = parse_cid(cid)
    plays = [p for p in read_plays(st.plays) if p.get("cid") != cid]  # a resumed selection is not its own repeat
    r = repeat_check(family, variant, concepts, date, differential, plays)
    if not r["ok"]:
        raise StudioError(f"repetition: {r}")
    entry = {"play_id": play_id, "family": family, "variant": variant, "concepts": sorted({x.strip().lower() for x in concepts}),
             "date": date.isoformat(), "cid": cid, "differential": differential, "sources": list(sources)}
    out = st._advance(cid, "selected", op, refs=entry, _token=_GATE)
    if not any(p.get("play_id") == play_id and p.get("cid") == cid for p in read_plays(st.plays)):
        with open(st.plays, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    return out


# ------------------------------------------------------------------ script
def parse_script(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"^\s*(HOOK|SETUP|CASE A|CASE B|COUNTER|TAKEAWAY|CTA)\s*:\s*(.*)$", line)
        if m:
            cur = m.group(1)
            out[cur] = m.group(2).strip()
        elif cur and line.strip() and not line.strip().startswith("#"):
            out[cur] = (out[cur] + " " + line.strip()).strip()
    return out


def spoken_text(text):
    s = parse_script(text)
    body = " ".join(s[k] for k in SECTIONS if k in s) if s else text
    return re.sub(r"\s+", " ", body.strip())


def script_check(text, c=None):
    c = c or cfg()
    s = parse_script(text)
    missing = [k for k in ("HOOK", "SETUP", "CASE A", "TAKEAWAY", "CTA") if not s.get(k)]
    if not (s.get("CASE B") or s.get("COUNTER")):
        missing.append("CASE B or COUNTER")
    words = len(spoken_text(text).split())
    est = words / c["speech"]["words_per_s"] + c["speech"]["designed_pauses_s"] + c["speech"]["tail_s"]
    ok = not missing and c["duration_s"]["min"] <= est <= c["duration_s"]["max"]
    return {"ok": ok, "missing": missing, "words": words, "estimated_s": round(est, 1)}


def freeze_script(st, cid, op, script_path):
    """GATE scripted: structure and duration checked here; the script hash freezes it."""
    st.require(cid, "selected")
    text = open(_abs(script_path), encoding="utf-8").read()
    r = script_check(text)
    if not r["ok"]:
        raise StudioError(f"script refused: {r}")
    return st._advance(cid, "scripted", op, artifacts={"script": script_path},
                       refs={"script_key": Studio.voice_key(text), **r}, _token=_GATE)


def _frozen_script(st, cid):
    a = st.artifacts(cid).get("script")
    if not a:
        raise StudioError("no frozen script")
    p = _abs(a["path"])
    if not os.path.exists(p) or sha256(p) != a["sha256"]:
        raise StudioError("the frozen script was changed after freezing: refused")
    return open(p, encoding="utf-8").read()


# ------------------------------------------------------------------ plays (storyboard)
def run_play_validator(play_paths):
    with tempfile.TemporaryDirectory() as td:
        rep = os.path.join(td, "r.json")
        p = subprocess.run(["node", "--experimental-strip-types", "scripts/test-play.mts", *[os.path.abspath(_abs(x)) for x in play_paths],
                            "--report", rep], cwd=TEMPLATE, capture_output=True, text=True)
        if not os.path.exists(rep):
            return {"passed": 0, "failed": 1, "error": (p.stderr or p.stdout)[-500:]}
        return json.load(open(rep))


def storyboard(st, cid, op, play_paths, validator=None):
    """GATE storyboard_ready: the generic tactical validator runs HERE (0 failures, ≥1 narration claim per play)."""
    st.require(cid, "scripted")
    _frozen_script(st, cid)
    rep = (validator or run_play_validator)(play_paths)
    claims = {}
    for r in rep.get("results", []):
        if r["check"].startswith("claim "):
            claims[r["play"]] = claims.get(r["play"], 0) + 1
    ids = [json.load(open(_abs(p)))["id"] for p in play_paths]
    if rep.get("failed", 1) != 0 or rep.get("passed", 0) == 0 or any(claims.get(i, 0) < 1 for i in ids):
        raise StudioError(f"plays refused: {rep.get('failed')} failed checks, claims {claims}")
    arts = {f"play_{i}": p for i, p in zip(ids, play_paths)}
    return st._advance(cid, "storyboard_ready", op, artifacts=arts, refs={"plays": ids, "checks": rep["passed"]}, _token=_GATE)


# ------------------------------------------------------------------ audio
def voice_permit(st, cid, op, credits):
    """Call BEFORE generating a narration. Refuses if a valid take for this frozen script exists (never pay
    twice) or the day's voice budget would be exceeded. The permit is what `audio` accepts."""
    text = _frozen_script(st, cid)
    hit = st.voice_lookup(cid, text)
    if hit["reuse"]:
        raise StudioError(f"a valid narration already exists for this script ({hit['path']}): reuse it, do not generate")
    if any(e["script_key"] == hit["script_key"] for e in st.events(cid, "voice_permit")):
        raise StudioError("this script already had a paid take (permit issued): recover that take; a new one needs the owner's approval")
    st.require(cid, "storyboard_ready")
    st.spend(cid, "voice_takes", 1, f"{op}:takes", _token=_GATE)
    st.spend(cid, "voice_credits", int(credits), f"{op}:credits", _token=_GATE)
    with st.lock():
        return st._append({"kind": "voice_permit", "cid": cid, "op": op, "script_key": hit["script_key"], "credits": int(credits)})


def transcript_match(script_text, words):
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    a = [norm(w) for w in spoken_text(script_text).split() if norm(w)]
    b = [norm(w["text"]) for w in words if norm(w["text"])]
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).ratio()


def audio(st, cid, op, voice_path, words_path):
    """GATE audio_ready: a voice permit (or a cached take) for THIS frozen script, and the real transcript
    must say the frozen script (≥ 0.9 word match)."""
    st.require(cid, "storyboard_ready")
    text = _frozen_script(st, cid)
    key = Studio.voice_key(text)
    permits = [e for e in st.events(cid, "voice_permit") if e["script_key"] == key]
    if not permits:
        raise StudioError("no voice permit for this script: run voice-permit before generating")
    words = json.load(open(_abs(words_path)))
    m = transcript_match(text, words)
    if m < 0.9:
        raise StudioError(f"the narration does not say the frozen script (match {m:.2f} < 0.90)")
    return st._advance(cid, "audio_ready", op, artifacts={"voice": voice_path, "words": words_path},
                       refs={"script_key": key, "transcript_match": round(m, 3)}, _token=_GATE)


# ------------------------------------------------------------------ licences
def load_licences():
    with open(LICENCES, encoding="utf-8") as f:
        return json.load(f)["assets"]


def licence_check(manifest, known=None):
    """Every asset must map to a known licence with commercial_use true. Unknown origin = fail."""
    known = load_licences() if known is None else known
    bad = []
    for a in manifest.get("assets", []):
        k = known.get(a["licence_key"]) or next((v for pat, v in known.items() if pat.endswith("*") and a["licence_key"].startswith(pat[:-1])), None)
        if not k or k.get("commercial_use") is not True:
            bad.append({"src": a["src"], "licence_key": a["licence_key"],
                        "why": "unknown origin" if not k else f"commercial use: {k.get('commercial_use')}"})
    return {"pass": not bad, "failures": bad, "checked": len(manifest.get("assets", []))}


def bundle_manifest(bundle):
    """Derive the asset list from the bundle itself (not from a hand-written list). Every media file under
    public/ needs a provenance sidecar `<file>.provenance.json` = {licence_key, source, sha256} whose hash
    matches the file; SFX are referenced by name and live in public/sfx (owned)."""
    ep = bundle["episode"]
    assets = [{"src": "3d/procedural", "licence_key": "3d/procedural"},
              {"src": "anton.woff2", "licence_key": "anton.woff2"}, {"src": "inter.woff2", "licence_key": "inter.woff2"},
              {"src": "e2a_logo_white.png", "licence_key": "e2a_logo_white.png"}]
    media = [ep.get("voice"), ep.get("voiceMix"), (ep.get("music") or {}).get("src")]
    for m in [x for x in media if x]:
        p = os.path.join(TEMPLATE, "public", m)
        side = p + ".provenance.json"
        if not os.path.exists(p):
            assets.append({"src": m, "licence_key": "missing-file"})
            continue
        if not os.path.exists(side):
            assets.append({"src": m, "licence_key": "no-provenance"})
            continue
        pv = json.load(open(side))
        assets.append({"src": m, "licence_key": pv["licence_key"] if pv.get("sha256") == sha256(p) else "provenance-hash-mismatch"})
    for s in ep.get("shots", []):
        for fx in s.get("sfx", []) or []:
            assets.append({"src": f"sfx/{fx['name']}", "licence_key": f"sfx/{fx['name']}"})
    uniq = {a["src"]: a for a in assets}
    return {"assets": list(uniq.values())}


# ------------------------------------------------------------------ render
def default_renderer(bundle_path, master, social, c):
    subprocess.run(["npx", "remotion", "render", "src/index.ts", "Tactical3DV2", master, f"--props={os.path.abspath(bundle_path)}",
                    "--gl=swangle", f"--browser-executable={CHROME}", "--concurrency=4"], cwd=TEMPLATE, check=True)
    social_encode(master, social, c)


def social_encode(master, social, c):
    """2-pass H.264 sized to the social limit; the audio stream is COPIED (no re-normalisation over SFX)."""
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", master],
                               capture_output=True, text=True, check=True).stdout)
    abr = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=bit_rate", "-of", "csv=p=0", master],
                             capture_output=True, text=True).stdout.strip() or 320000)
    target = c["video"]["social_max_mb"] * 0.92 * 8e6 / dur
    vbr = int(max(1.2e6, target - abr))
    with tempfile.TemporaryDirectory() as td:
        log = os.path.join(td, "pass")
        base = ["ffmpeg", "-v", "error", "-y", "-i", master, "-c:v", "libx264", "-preset", "slow", "-b:v", str(vbr),
                "-pix_fmt", "yuv420p", "-passlogfile", log]
        subprocess.run(base + ["-pass", "1", "-an", "-f", "mp4", os.devnull], check=True)
        subprocess.run(base + ["-pass", "2", "-c:a", "copy", "-movflags", "+faststart", social], check=True)


def render(st, cid, op, bundle_path, out_dir, renderer=None):
    """GATE rendered: licences are checked on the bundle BEFORE spending a render; the render budget is
    charged here; the narration in the bundle must be the audio_ready take; the MP4 is hashed here."""
    st.require(cid, "audio_ready")
    c = cfg()
    bundle = json.load(open(_abs(bundle_path)))
    lic = licence_check(bundle_manifest(bundle))
    if not lic["pass"]:
        st.fail(cid, "render", f"licences: {lic['failures']}")
        raise StudioError(f"licence gate: {lic['failures']}")
    voice = st.artifacts(cid)["voice"]
    bv = os.path.join(TEMPLATE, "public", bundle["episode"]["voice"])
    if not os.path.exists(bv) or sha256(bv) != voice["sha256"]:
        raise StudioError("the bundle's narration is not the approved audio_ready take")
    st.spend(cid, "final_renders", 1, f"{op}:render", _token=_GATE)
    os.makedirs(_abs(out_dir), exist_ok=True)
    master, social = os.path.join(_abs(out_dir), f"{cid}.master.mp4"), os.path.join(_abs(out_dir), f"{cid}.mp4")
    (renderer or default_renderer)(_abs(bundle_path), master, social, c)
    return st._advance(cid, "rendered", op, artifacts={"bundle": bundle_path, "master": master, "mp4": social},
                       refs={"licences": lic}, _token=_GATE)


# ------------------------------------------------------------------ QC (measured here, from the MP4)
def _run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def measure_mp4(mp4, words, frames_dir, c):
    pr = json.loads(_run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", mp4]).stdout)
    v = next(s for s in pr["streams"] if s["codec_type"] == "video")
    a = next((s for s in pr["streams"] if s["codec_type"] == "audio"), {})
    num, den = map(int, v["r_frame_rate"].split("/"))
    dur = float(pr["format"]["duration"])
    technical = {"width": v["width"], "height": v["height"], "fps": num / den, "vcodec": v["codec_name"],
                 "acodec": a.get("codec_name"), "duration": dur, "social_mb": int(pr["format"]["size"]) / 1e6}
    err = _run(["ffmpeg", "-v", "info", "-nostats", "-i", mp4, "-vf", "blackdetect=d=0.1:pix_th=0.06", "-an", "-f", "null", "-"]).stderr
    technical["black_frames"] = len(re.findall(r"black_start", err))
    e = _run(["ffmpeg", "-nostats", "-i", mp4, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
    summ = e[e.rfind("Summary:"):]
    I = float(re.search(r"I:\s*(-?[\d.]+) LUFS", summ).group(1))
    TP = float(re.search(r"Peak:\s*(-?[\d.]+) dBFS", summ).group(1))
    sd = _run(["ffmpeg", "-nostats", "-i", mp4, "-vn", "-af", "silencedetect=n=-55dB:d=0.5", "-f", "null", "-"]).stderr
    t0, t1 = words[0]["start"], words[-1]["end"]
    sil = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", sd)]
    inside = [s for s in sil if t0 < s < t1]
    audio = {"mix": {"I": I, "TP": TP}, "silences_inside_narration": inside}
    os.makedirs(frames_dir, exist_ok=True)
    n = 8
    shots = []
    for i in range(n):
        t = dur * (i + 0.5) / n
        out = os.path.join(frames_dir, f"frame_{i + 1:02d}.png")
        _run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", mp4, "-frames:v", "1", out])
        st_ = _run(["ffmpeg", "-v", "info", "-i", out, "-vf", "signalstats,metadata=print", "-f", "null", "-"]).stderr
        ymin = re.search(r"YMIN=(\d+)", st_)
        ymax = re.search(r"YMAX=(\d+)", st_)
        shots.append({"t": round(t, 2), "file": out, "exists": os.path.exists(out),
                      "contrast": int(ymax.group(1)) - int(ymin.group(1)) if ymin and ymax else 0,
                      "sha": sha256(out) if os.path.exists(out) else None})
    issues = [s["t"] for s in shots if not s["exists"] or s["contrast"] < 60]
    if len({s["sha"] for s in shots}) < n:
        issues.append("identical frames (frozen video)")
    frames = {"extracted_from_mp4": True, "count": sum(s["exists"] for s in shots), "issues": issues, "frames": shots}
    return technical, audio, frames


def run_engine_qc(episode_path):
    with tempfile.TemporaryDirectory() as td:
        rep = os.path.join(td, "e.json")
        p = _run(["node", "--experimental-strip-types", "scripts/qc-tactical3d.mts", os.path.abspath(_abs(episode_path)), rep], cwd=TEMPLATE)
        res = [l for l in p.stdout.splitlines() if l.startswith(("PASS", "FAIL"))]
        return {"passed": sum(l.startswith("PASS") for l in res), "failed": sum(l.startswith("FAIL") for l in res),
                "fails": [l for l in res if l.startswith("FAIL")], "exit": p.returncode}


def qc_evaluate(r, c=None):
    c = c or cfg()
    out = {}
    for name in QC_REQUIRED:
        x = r.get(name)
        if x is None:
            out[name] = {"pass": False, "why": "report missing"}
            continue
        if name in ("tactical", "engine"):
            ok = x.get("failed", 1) == 0 and x.get("passed", 0) > 0
        elif name == "audio":
            mix = x.get("mix", {})
            ok = (abs(mix.get("I", 0) - c["audio"]["lufs_target"]) <= c["audio"]["lufs_tolerance"]
                  and mix.get("TP", 0) <= c["audio"]["true_peak_max"] and not x.get("silences_inside_narration"))
        elif name == "technical":
            v = c["video"]
            ok = (x.get("width") == v["width"] and x.get("height") == v["height"] and x.get("fps", 0) >= v["fps_min"]
                  and x.get("vcodec") == v["vcodec"] and x.get("acodec") == v["acodec"]
                  and c["duration_s"]["min"] <= x.get("duration", 0) <= c["duration_s"]["max"]
                  and x.get("black_frames", 1) == 0 and x.get("social_mb", 99) <= v["social_max_mb"])
        elif name == "frames":
            ok = x.get("extracted_from_mp4") is True and x.get("count", 0) >= 6 and not x.get("issues")
        else:
            ok = x.get("pass") is True
        out[name] = {"pass": bool(ok)}
    return out


def qc(st, cid, op, episode_path, reports_dir, measure=None, plays_validator=None, engine=None):
    """GATE qc_passed: every measurement is taken HERE from the rendered MP4 (hash = the `rendered` one)."""
    st.require(cid, "rendered")
    arts = st.artifacts(cid)
    mp4 = _abs(arts["mp4"]["path"])
    if not os.path.exists(mp4) or sha256(mp4) != arts["mp4"]["sha256"]:
        raise StudioError("the MP4 is not the rendered one (missing or changed)")
    bundle = json.load(open(_abs(arts["bundle"]["path"])))
    words = json.load(open(_abs(arts["words"]["path"])))
    os.makedirs(_abs(reports_dir), exist_ok=True)
    technical, aud, frames = (measure or measure_mp4)(mp4, words, os.path.join(_abs(reports_dir), "frames"), cfg())
    plays = [a["path"] for k, a in arts.items() if k.startswith("play_")]
    r = {"technical": technical, "audio": aud, "frames": frames,
         "tactical": (plays_validator or run_play_validator)(plays),
         "engine": (engine or run_engine_qc)(episode_path),
         "licences": licence_check(bundle_manifest(bundle))}
    checks = qc_evaluate(r)
    result = "QC_PASS" if all(v["pass"] for v in checks.values()) else "QC_FAIL"
    rep = {"cid": cid, "mp4": _rel(mp4), "mp4_sha256": arts["mp4"]["sha256"], "result": result, "checks": checks,
           "measured": {k: v for k, v in r.items() if k != "tactical"},
           "tactical": {"passed": r["tactical"].get("passed"), "failed": r["tactical"].get("failed")}}
    path = os.path.join(_abs(reports_dir), "qc.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1, ensure_ascii=False, default=str)
    if result != "QC_PASS":
        st.fail(cid, "qc", "QC_FAIL: " + ",".join(k for k, v in checks.items() if not v["pass"]), op=f"{op}:fail")
        return rep
    st._advance(cid, "qc_passed", op, artifacts={"qc": path}, refs={"mp4_sha256": arts["mp4"]["sha256"]}, _token=_GATE)
    return rep


# ------------------------------------------------------------------ public asset
def fetch_sha(url):
    """Download through the session proxy (curl) and hash the bytes. Returns (sha256, bytes)."""
    p = subprocess.Popen(["curl", "-sSfL", "--max-time", "120", url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    h, n = hashlib.sha256(), 0
    for b in iter(lambda: p.stdout.read(1 << 20), b""):
        h.update(b)
        n += len(b)
    if p.wait() != 0:
        raise StudioError(f"cannot download {url}: {p.stderr.read().decode()[-200:]}")
    return h.hexdigest(), n


def asset(st, cid, op, url, fetch=None):
    """GATE asset_ready: the public URL must serve EXACTLY the QC'd bytes."""
    st.require(cid, "qc_passed")
    if not url.startswith("https://"):
        raise StudioError("the asset URL must be https")
    want = st.artifacts(cid)["mp4"]
    got, n = (fetch or fetch_sha)(url)
    if got != want["sha256"] or n != want["bytes"]:
        raise StudioError(f"URL serves different bytes ({n} B, {got[:12]}) than the QC'd MP4 ({want['bytes']} B, {want['sha256'][:12]})")
    return st._advance(cid, "asset_ready", op, refs={"url": url, "sha256": got, "bytes": n}, _token=_GATE)


# ------------------------------------------------------------------ authorisation
def scope_of(cid):
    date, n = parse_cid(cid)
    return {"cid": cid, "date": date.isoformat(), "slot": cfg()["slots"][str(n)]["time"], "networks": list(NETWORKS)}


def authorise(st, cid, op, verifier=None):
    st.require(cid, "asset_ready")
    verifier = verifier or configured_verifier()
    scope = scope_of(cid)

    def guard():
        ok, why = verifier(scope)
        if not ok:
            raise StudioError(f"not authorised: {why}")
    return st._advance(cid, "authorised", op, refs={"scope": scope}, _token=_GATE, _guard=guard)


# ------------------------------------------------------------------ package
def package(st, cid, caption, titles, c=None):
    """ONE Metricool post per video, three networks; media = the verified asset URL and its hash."""
    c = c or cfg()
    st.require(cid, "asset_ready", "authorised", "scheduled_partial")
    date, n = parse_cid(cid)
    ar = st.refs(cid, "asset_ready")
    lab = c["ai_labels"]
    if not titles["youtube"].endswith("#shorts") or len(titles["youtube"]) > 100:
        raise StudioError("YouTube title must end with #shorts and be ≤ 100 characters")
    info = {
        "autoPublish": True, "draft": False, "descendants": [], "firstCommentText": "", "hasNotReadNotes": False,
        "media": [ar["url"]], "mediaAltText": [], "shortener": False, "smartLinkData": {"ids": []},
        "providers": [{"network": x} for x in NETWORKS],
        "publicationDate": {"dateTime": f"{date.isoformat()}T{c['slots'][str(n)]['time']}:00", "timezone": c["timezone"]},
        "text": caption,
        "instagramData": {"type": "REEL", "showReelOnFeed": True, "isAiGenerated": lab["instagram_isAiGenerated"]},
        "tiktokData": {"privacyOption": "PUBLIC_TO_EVERYONE", "title": titles["tiktok"], "isAigc": lab["tiktok_isAigc"]},
        "youtubeData": {"title": titles["youtube"], "type": "short", "privacy": "public", "category": "SPORTS",
                        "madeForKids": False, "isAiGeneratedContent": lab["youtube_isAiGeneratedContent"],
                        "tags": titles.get("tags", [])},
    }
    pkg = {"cid": cid, "mode": c["publishing"]["mode"], "date": date.isoformat(), "info": info,
           "media_sha256": ar["sha256"], "media_bytes": ar["bytes"],
           "text_sha256": hashlib.sha256(caption.encode()).hexdigest(),
           "keys": [f"{cid}:{x}:{date.isoformat()}:{c['slots'][str(n)]['time']}" for x in NETWORKS]}
    pkg["package_sha256"] = hashlib.sha256(canon(pkg).encode()).hexdigest()
    return pkg


def _pkg_hash(pkg):
    return hashlib.sha256(canon({k: v for k, v in pkg.items() if k != "package_sha256"}).encode()).hexdigest()


# ------------------------------------------------------------------ collisions + schedule ticket
def _post_time(p, c):
    pd = p.get("publicationDate", {})
    return dt.datetime.fromisoformat(pd["dateTime"]).replace(tzinfo=ZoneInfo(pd.get("timezone") or c["timezone"]))


def collisions(readback, date, c=None, ignore_ids=()):
    """ANY existing post (video, carousel, image, story) on one of our networks within the window of a slot
    blocks that slot. Posts are reported and kept: the studio never cancels or moves a post."""
    c = c or cfg()
    d = date if isinstance(date, dt.date) else dt.date.fromisoformat(date)
    win = c["collision_window_min"] * 60
    out = []
    for p in readback.get("data", readback):
        if str(p.get("id")) in {str(x) for x in ignore_ids}:
            continue
        try:
            t = _post_time(p, c)
        except (KeyError, ValueError):
            out.append({"slot": "?", "metricool_id": p.get("id"), "why": "post without a readable date: blocks (uncertain)", "blocks": True})
            continue
        nets = sorted(x.get("network") for x in p.get("providers", []))
        for n in (1, 2):
            s = slot_instant(d, n, c)
            if abs((t - s).total_seconds()) <= win and set(nets) & set(NETWORKS):
                kind = (p.get("instagramData") or {}).get("type") or ("VIDEO" if {"tiktok", "youtube"} & set(nets) else "POST")
                out.append({"slot": n, "metricool_id": p.get("id"), "at": p.get("publicationDate"), "networks": nets,
                            "type": kind, "blocks": True})
    return out


def readback_covers(rb, date, now, c):
    """The read-back must be fresh and cover the whole Sydney date of the slot (± the window)."""
    tz = sydney(c)
    d = date if isinstance(date, dt.date) else dt.date.fromisoformat(date)
    start = dt.datetime(d.year, d.month, d.day, tzinfo=tz)
    end = start + dt.timedelta(days=1)
    try:
        f, t, at = parse_ts(rb["from"]), parse_ts(rb["to"]), parse_ts(rb["fetched_at"])
    except (KeyError, StudioError, ValueError):
        return False, "read-back without from/to/fetched_at (with time zones)"
    if f > start or t < end - dt.timedelta(seconds=1):
        return False, f"read-back covers {f}–{t}, not the whole {d} Sydney"
    age = (now - at).total_seconds()
    if age < -60 or age > c["readback_max_age_min"] * 60:
        return False, f"read-back is {age / 60:.0f} min old (max {c['readback_max_age_min']})"
    return True, "ok"


def schedule_check(st, cid, op, readback, pkg, verifier=None):
    """MANDATORY before any create call. Re-checks authorisation LIVE, the package against the verified asset,
    a fresh full-day read-back and collisions; then reserves the three networks and issues a ticket."""
    c = cfg()
    st.require(cid, "authorised", "scheduled_partial")
    ok, why = (verifier or configured_verifier())(scope_of(cid))
    if not ok:
        raise StudioError(f"not authorised now: {why}")
    if pkg.get("package_sha256") != _pkg_hash(pkg) or pkg["cid"] != cid:
        raise StudioError("package was edited after it was built")
    ar = st.refs(cid, "asset_ready")
    if pkg["info"]["media"] != [ar["url"]] or pkg["media_sha256"] != ar["sha256"]:
        raise StudioError("package media is not the verified asset")
    date, _ = parse_cid(cid)
    good, why = readback_covers(readback, date, st.clock(), c)
    if not good:
        raise StudioError(f"read-back refused: {why}")
    mine = [e.get("metricool_id") for e in st.events(cid, "confirmation")]
    hits = collisions(readback, date, c, ignore_ids=mine)
    n = parse_cid(cid)[1]
    hits = [h for h in hits if h["slot"] in (n, "?")]
    if hits:
        st.fail(cid, "schedule", f"slot taken: {hits}", op=f"{op}:collision")
        raise StudioError(f"slot collision, nothing scheduled: {hits}")
    for net in NETWORKS:
        st.reserve(cid, net, f"{op}:{net}")
    with st.lock():
        exp = st.clock() + dt.timedelta(minutes=c["ticket_ttl_min"])
        return st._append({"kind": "ticket", "cid": cid, "op": op, "package_sha256": pkg["package_sha256"],
                           "expires": exp.isoformat()})


# ------------------------------------------------------------------ confirmation
def _approval_pending(p):
    if p.get("draft") is not False:
        return "draft or unknown draft flag"
    for k, v in p.items():
        if re.search(r"approv|review", k, re.I) and v not in (None, False, "", "APPROVED", "approved", []):
            return f"{k}={v}"
    return None


def confirm(st, cid, create_resp, readback, pkg, fetch=None, op_prefix=None):
    """Read-back confirmation. A network counts only if: a valid schedule ticket exists for this exact package;
    the read-back shows the SAME post (id/uuid from the create answer) exactly once; slot, time zone and caption
    match; the post has exactly one media item whose BYTES are the QC'd MP4; it is not a draft nor waiting for
    approval; and the provider status is a real scheduled/published status. Confirmed networks are kept."""
    c = cfg()
    date, n = parse_cid(cid)
    tickets = [e for e in st.events(cid, "ticket") if e["package_sha256"] == pkg.get("package_sha256")]
    if not tickets or pkg.get("package_sha256") != _pkg_hash(pkg):
        raise StudioError("no schedule ticket for this package: schedule-check is mandatory before creating")
    slot = f"{date.isoformat()}T{c['slots'][str(n)]['time']}:00"
    cr = create_resp.get("data", create_resp)
    want_ids = {str(cr.get("id")), str(cr.get("uuid"))} - {"None"}
    posts = readback.get("data", readback)
    mine = [p for p in posts if {str(p.get("id")), str(p.get("uuid"))} & want_ids]
    already = {e["network"] for e in st.events(cid, "confirmation")}
    got, problems, waiting = set(already), [], []
    if len(mine) > 1:
        problems.append("the read-back shows the post twice: duplicate, confirm nothing and report")
        mine = []
    if not mine and not already:
        problems.append("post not found in the read-back")
    for p in mine:
        pd = p.get("publicationDate", {})
        if pd.get("dateTime") != slot or pd.get("timezone") != c["timezone"]:
            problems.append(f"wrong slot {pd}")
            continue
        if hashlib.sha256(p.get("text", "").encode()).hexdigest() != pkg["text_sha256"]:
            problems.append("caption differs from the package")
            continue
        media = p.get("media") or []
        if len(media) != 1:
            problems.append(f"expected one media item, found {len(media)}")
            continue
        try:
            sh, nb = (fetch or fetch_sha)(media[0])
        except StudioError as e:
            problems.append(f"media identity not verifiable: {e}")
            continue
        if sh != pkg["media_sha256"] or nb != pkg["media_bytes"]:
            problems.append(f"media bytes differ from the QC'd MP4 ({nb} B {sh[:12]})")
            continue
        pend = _approval_pending(p)
        if pend:
            waiting.append(pend)
            continue
        for prov in p.get("providers", []):
            net = prov.get("network")
            if net not in NETWORKS or net in got:
                continue
            status = str(prov.get("status", "")).upper()
            if status not in SCHEDULED_OK | PUBLISHED_OK:
                (waiting if "APPROV" in status or "REVIEW" in status else problems).append(f"{net}: {status} {prov.get('detailedStatus', '')}".strip())
                continue
            with st.lock():
                st._append({"kind": "confirmation", "cid": cid, "network": net, "metricool_id": p.get("id"),
                            "uuid": p.get("uuid"), "status": status, "public_url": prov.get("publicUrl"),
                            "media_sha256": sh})
            got.add(net)
    cur = st.state(cid)
    target = "scheduled_confirmed" if got >= set(NETWORKS) else ("scheduled_partial" if got else None)
    if target and cur != target and st._allowed(cid, target):
        st._advance(cid, target, f"{op_prefix or cid}:{target}", refs={"networks": sorted(got)}, _token=_GATE)
    return {"confirmed": sorted(got), "missing": sorted(set(NETWORKS) - got), "awaiting_approval": waiting,
            "problems": problems, "state": st.state(cid)}


def published(st, cid, op, readback):
    """GATE published_confirmed: every network PUBLISHED with a public URL on its own domain, same Metricool post."""
    st.require(cid, "scheduled_confirmed")
    ids = {str(e["metricool_id"]) for e in st.events(cid, "confirmation")}
    ok = {}
    for p in readback.get("data", readback):
        if str(p.get("id")) not in ids:
            continue
        for prov in p.get("providers", []):
            net, url = prov.get("network"), prov.get("publicUrl") or ""
            host = re.sub(r"^https://(www\.|m\.)?", "", url).split("/")[0]
            if net in NETWORKS and str(prov.get("status", "")).upper() in PUBLISHED_OK and any(host == d or host.endswith("." + d) for d in PUBLIC_DOMAINS[net]):
                ok[net] = url
    if set(ok) != set(NETWORKS):
        raise StudioError(f"not published everywhere: {sorted(set(NETWORKS) - set(ok))}")
    return st._advance(cid, "published_confirmed", op, refs={"urls": ok}, _token=_GATE)


# ------------------------------------------------------------------ CLI
def _kv(items):
    out = {}
    for it in items or []:
        k, _, v = it.partition("=")
        out[k] = v
    return out


def _j(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main(argv=None):
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("plan"); p.add_argument("--now"); p.add_argument("--date")
    p = sp.add_parser("advance", help="free states only (candidate, researched, analytics_*)")
    p.add_argument("cid"); p.add_argument("state"); p.add_argument("--op", required=True); p.add_argument("--ref", action="append")
    p = sp.add_parser("fail"); p.add_argument("cid"); p.add_argument("--phase", required=True); p.add_argument("--reason", required=True)
    p.add_argument("--op"); p.add_argument("--retry-after")
    p = sp.add_parser("select"); p.add_argument("cid"); p.add_argument("--op", required=True)
    for k in ("play-id", "family", "variant", "concepts"):
        p.add_argument(f"--{k}", required=True)
    p.add_argument("--differential"); p.add_argument("--sources", default="")
    p = sp.add_parser("script"); p.add_argument("cid"); p.add_argument("file"); p.add_argument("--op", required=True)
    p = sp.add_parser("script-check"); p.add_argument("file")
    p = sp.add_parser("storyboard"); p.add_argument("cid"); p.add_argument("plays", nargs="+"); p.add_argument("--op", required=True)
    p = sp.add_parser("voice-lookup"); p.add_argument("cid")
    p = sp.add_parser("voice-permit"); p.add_argument("cid"); p.add_argument("--credits", type=int, required=True); p.add_argument("--op", required=True)
    p = sp.add_parser("audio"); p.add_argument("cid"); p.add_argument("--voice", required=True); p.add_argument("--words", required=True)
    p.add_argument("--op", required=True)
    p = sp.add_parser("licences"); p.add_argument("bundle")
    p = sp.add_parser("render"); p.add_argument("cid"); p.add_argument("bundle"); p.add_argument("--out", required=True); p.add_argument("--op", required=True)
    p = sp.add_parser("qc"); p.add_argument("cid"); p.add_argument("--episode", required=True); p.add_argument("--reports", required=True)
    p.add_argument("--op", required=True)
    p = sp.add_parser("asset"); p.add_argument("cid"); p.add_argument("url"); p.add_argument("--op", required=True)
    p = sp.add_parser("authorise"); p.add_argument("cid"); p.add_argument("--op", required=True)
    p = sp.add_parser("package"); p.add_argument("cid"); p.add_argument("--caption", required=True); p.add_argument("--titles", required=True)
    p.add_argument("--out", required=True)
    p = sp.add_parser("schedule-check"); p.add_argument("cid"); p.add_argument("--readback", required=True); p.add_argument("--package", required=True)
    p.add_argument("--op", required=True)
    p = sp.add_parser("confirm"); p.add_argument("cid"); p.add_argument("--create", required=True)
    p.add_argument("--readback", required=True); p.add_argument("--package", required=True)
    p = sp.add_parser("published"); p.add_argument("cid"); p.add_argument("--readback", required=True); p.add_argument("--op", required=True)
    p = sp.add_parser("collisions"); p.add_argument("date"); p.add_argument("--readback", required=True)
    p = sp.add_parser("verify")
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
        out = {"target_date": d.isoformat(), "mode": c["publishing"]["mode"], "log": s.verify_chain(), "videos": vids}
    elif a.cmd == "advance":
        out = s.advance(a.cid, a.state, a.op, None, _kv(a.ref))
    elif a.cmd == "fail":
        out = s.fail(a.cid, a.phase, a.reason, a.op, a.retry_after)
    elif a.cmd == "select":
        out = select(s, a.cid, a.op, a.play_id, a.family, a.variant, a.concepts.split(","), a.differential,
                     [x for x in a.sources.split(",") if x])
    elif a.cmd == "script":
        out = freeze_script(s, a.cid, a.op, a.file)
    elif a.cmd == "script-check":
        out = script_check(open(a.file, encoding="utf-8").read())
    elif a.cmd == "storyboard":
        out = storyboard(s, a.cid, a.op, a.plays)
    elif a.cmd == "voice-lookup":
        out = s.voice_lookup(a.cid, _frozen_script(s, a.cid))
    elif a.cmd == "voice-permit":
        out = voice_permit(s, a.cid, a.op, a.credits)
    elif a.cmd == "audio":
        out = audio(s, a.cid, a.op, a.voice, a.words)
    elif a.cmd == "licences":
        out = licence_check(bundle_manifest(_j(a.bundle)))
    elif a.cmd == "render":
        out = render(s, a.cid, a.op, a.bundle, a.out)
    elif a.cmd == "qc":
        out = qc(s, a.cid, a.op, a.episode, a.reports)
    elif a.cmd == "asset":
        out = asset(s, a.cid, a.op, a.url)
    elif a.cmd == "authorise":
        out = authorise(s, a.cid, a.op)
    elif a.cmd == "package":
        out = package(s, a.cid, open(a.caption, encoding="utf-8").read().strip(), _j(a.titles), c)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, ensure_ascii=False)
    elif a.cmd == "schedule-check":
        out = schedule_check(s, a.cid, a.op, _j(a.readback), _j(a.package))
    elif a.cmd == "confirm":
        out = confirm(s, a.cid, _j(a.create), _j(a.readback), _j(a.package))
    elif a.cmd == "published":
        out = published(s, a.cid, a.op, _j(a.readback))
    elif a.cmd == "collisions":
        out = collisions(_j(a.readback), a.date, c)
    elif a.cmd == "verify":
        out = s.verify_chain()
    elif a.cmd == "report":
        out = {"date": a.date, "log": s.verify_chain(), "videos": []}
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
    except (StudioError, subprocess.CalledProcessError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(2)
