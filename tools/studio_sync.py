#!/usr/bin/env python3
"""Persist the Tactical Studio registry between Claude Cloud sessions (each session starts in a fresh
container; `state/` is git-ignored and would be lost).

The registry lives on a dedicated git branch (config `state_sync.branch`) under `studio-state/`:
events.jsonl (hash-chained), plays.jsonl and lease.json. Git itself is the concurrency control:
a push is accepted only if it is a fast-forward of what the session last fetched, so two sessions
can never both write on top of the same head (compare-and-swap on the branch ref).

  lease  RUN   take the writer lease (refused while another unexpired lease exists)
  pull         bring the remote registry into state/ (refuses a broken chain or a diverged history)
  push   RUN   publish local events (needs our lease; remote must be a prefix of local; never force)
  release RUN  give the lease back

Rules: never `--force`; a rejected push re-fetches and re-checks instead of overwriting. The branch
should be protected on GitHub (no force-push, no deletion) so history can only grow.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tactical_studio as ts  # noqa: E402

FILES = ("events.jsonl", "plays.jsonl")


class SyncError(RuntimeError):
    pass


class Sync:
    def __init__(self, remote, branch, state_dir, cache_dir, subdir="studio-state", clock=None, lease_ttl_min=240):
        self.remote, self.branch, self.state, self.cache, self.sub = remote, branch, state_dir, cache_dir, subdir
        self.clock = clock or ts.now_utc
        self.ttl = dt.timedelta(minutes=lease_ttl_min)
        os.makedirs(state_dir, exist_ok=True)

    def git(self, *a, check=True):
        p = subprocess.run(["git", *a], cwd=self.cache, capture_output=True, text=True)
        if check and p.returncode:
            raise SyncError(f"git {' '.join(a)}: {p.stderr.strip()[-300:]}")
        return p

    def fresh(self):
        """Exactly the remote branch head (or an empty orphan if the branch does not exist yet)."""
        if not os.path.isdir(os.path.join(self.cache, ".git")):
            os.makedirs(self.cache, exist_ok=True)
            self.git("init", "-q")
            self.git("remote", "add", "origin", self.remote)
            self.git("config", "user.name", "E2A Tactical Studio")
            self.git("config", "user.email", "studio@e2a.invalid")
        f = self.git("fetch", "-q", "origin", f"+refs/heads/{self.branch}:refs/remotes/origin/{self.branch}", check=False)
        if f.returncode == 0:
            self.git("checkout", "-q", "-B", "work", f"origin/{self.branch}")
            self.git("reset", "-q", "--hard", f"origin/{self.branch}")
            self.git("clean", "-qfd")
            self.base = self.git("rev-parse", "HEAD").stdout.strip()
        else:
            self.git("checkout", "-q", "--orphan", "work", check=False)
            self.git("rm", "-rqf", "--ignore-unmatch", ".", check=False)
            self.base = None
        os.makedirs(os.path.join(self.cache, self.sub), exist_ok=True)

    def _p(self, name):
        return os.path.join(self.cache, self.sub, name)

    def lease_info(self):
        p = self._p("lease.json")
        return json.load(open(p)) if os.path.exists(p) else None

    def _commit_push(self, msg):
        self.git("add", "-A", self.sub)
        if not self.git("status", "--porcelain").stdout.strip():
            return True
        self.git("commit", "-qm", msg)
        p = self.git("push", "-q", "origin", f"HEAD:refs/heads/{self.branch}", check=False)  # never --force
        return p.returncode == 0

    @staticmethod
    def _ids(path):
        if not os.path.exists(path):
            return []
        return [json.loads(l)["id"] for l in open(path, encoding="utf-8") if l.strip()]

    @staticmethod
    def _chain_ok(path):
        with tempfile.TemporaryDirectory() as td:
            if os.path.exists(path):
                shutil.copy(path, os.path.join(td, "events.jsonl"))
            return ts.Studio(td).verify_chain()

    # ---------------------------------------------------------------- commands
    def lease(self, run):
        for _ in range(5):
            self.fresh()
            cur = self.lease_info()
            if cur and cur["run"] != run and ts.parse_ts(cur["expires"]) > self.clock():
                raise SyncError(f"lease held by {cur['run']} until {cur['expires']}: another run is writing")
            info = {"run": run, "taken": self.clock().isoformat(), "expires": (self.clock() + self.ttl).isoformat()}
            json.dump(info, open(self._p("lease.json"), "w"), indent=1)
            if self._commit_push(f"studio: lease {run}"):
                return info
        raise SyncError("could not take the lease (the branch kept moving)")

    def pull(self):
        self.fresh()
        chk = self._chain_ok(self._p("events.jsonl"))
        if not chk["ok"]:
            raise SyncError(f"remote registry chain is broken ({chk['why']} at {chk['at']}): refusing it, report")
        r, l = self._ids(self._p("events.jsonl")), self._ids(os.path.join(self.state, "events.jsonl"))
        if l[:len(r)] == r:
            return {"action": "local is up to date or ahead", "remote": len(r), "local": len(l)}
        if r[:len(l)] == l:
            for f in FILES:
                if os.path.exists(self._p(f)):
                    shutil.copy(self._p(f), os.path.join(self.state, f))
            return {"action": "pulled", "remote": len(r), "local_before": len(l)}
        raise SyncError("local and remote histories diverged: refusing to merge, report")

    def push(self, run):
        for _ in range(5):
            self.fresh()
            cur = self.lease_info()
            if not cur or cur["run"] != run or ts.parse_ts(cur["expires"]) <= self.clock():
                raise SyncError(f"no valid lease for {run} (lease: {cur}): nothing pushed")
            chk = self._chain_ok(os.path.join(self.state, "events.jsonl"))
            if not chk["ok"]:
                raise SyncError(f"local registry chain is broken ({chk['why']} at {chk['at']}): nothing pushed")
            r, l = self._ids(self._p("events.jsonl")), self._ids(os.path.join(self.state, "events.jsonl"))
            if l[:len(r)] != r:
                raise SyncError("remote has events this session does not have: pull first (diverged)")
            for f in FILES:
                if os.path.exists(os.path.join(self.state, f)):
                    shutil.copy(os.path.join(self.state, f), self._p(f))
            if self._commit_push(f"studio: {len(l) - len(r)} events by {run}"):
                return {"pushed": len(l) - len(r), "total": len(l)}
        raise SyncError("push kept being rejected")

    def release(self, run):
        for _ in range(5):
            self.fresh()
            cur = self.lease_info()
            if not cur or cur["run"] != run:
                return {"released": False, "lease": cur}
            os.remove(self._p("lease.json"))
            if self._commit_push(f"studio: release {run}"):
                return {"released": True}
        raise SyncError("could not release")


def from_config(state_dir=None, cache_dir=None):
    c = ts.cfg()["state_sync"]
    if c["branch"].startswith("PENDING"):
        raise SyncError("state branch not approved yet (config state_sync.branch)")
    root = ts.ROOT
    remote = subprocess.run(["git", "remote", "get-url", c["remote"]], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
    return Sync(remote, c["branch"], state_dir or ts.STATE, cache_dir or os.path.join(root, ".studio-sync"), c["dir"],
                lease_ttl_min=c["lease_ttl_min"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["lease", "pull", "push", "release"])
    ap.add_argument("run", nargs="?")
    ap.add_argument("--remote"); ap.add_argument("--branch"); ap.add_argument("--cache")
    a = ap.parse_args()
    try:
        s = Sync(a.remote, a.branch, ts.STATE, a.cache or os.path.join(ts.ROOT, ".studio-sync")) if a.remote else from_config(cache_dir=a.cache)
        out = s.pull() if a.cmd == "pull" else getattr(s, a.cmd)(a.run)
        print(json.dumps(out, indent=1))
    except (SyncError, ts.StudioError) as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(2)
