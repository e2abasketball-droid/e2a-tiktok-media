"""E2A Football — shared helpers: division config, ids, write guard and read-only access to the shared engine.

Everything here is read-only towards basketball: shared components are executed from their own path when they
are on the checked-out commit, or extracted with `git show <ref>:<path>` into football/.cache/shared/<ref>/ when
they only exist on another branch. Nothing is ever written outside football/ or /mnt/project-files/football/.
"""
import datetime as _dt
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FOOTBALL = os.path.dirname(HERE)
REPO = os.path.dirname(FOOTBALL)


def load(name):
    with open(os.path.join(FOOTBALL, 'config', name), encoding='utf-8') as fh:
        return json.load(fh)


def division():
    return load('division.json')


def git(*args, check=True):
    r = subprocess.run(['git', '-C', REPO, *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


# ---------- ids ----------

def slugify(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')
    if not s:
        raise ValueError('empty slug')
    return s


def production_id(slug, date=None):
    date = date or _dt.date.today()
    pid = f"FB-{date:%Y%m%d}-{slugify(slug)}"
    assert re.match(division()['ids']['regex']['production'], pid), pid
    return pid


def content_id(date, n):
    cid = f"FB-TACTICAL-{date:%Y%m%d}-V{n:02d}"
    assert re.match(division()['ids']['regex']['content'], cid), cid
    return cid


def is_football_id(s):
    rx = division()['ids']['regex']
    return any(re.match(rx[k], s) for k in ('production', 'content', 'play', 'concept'))


# ---------- write guard ----------

def _abs(p):
    p = p if os.path.isabs(p) else os.path.join(REPO, p)
    return os.path.realpath(p)


def _roots(entries):
    out = []
    for e in entries:
        out.append(_abs(e).rstrip('/') + ('/' if e.endswith('/') else ''))
    return out


def check_write(path):
    """Return the absolute path if football may write it; raise PermissionError otherwise."""
    cfg = division()
    a = _abs(path)
    for root in _roots(cfg['write_deny']):
        r = root.rstrip('/')
        if a == r or a.startswith(r + '/'):
            raise PermissionError(f'{path}: protected basketball/shared path ({root})')
    for root in _roots(cfg['write_allow']):
        r = root.rstrip('/')
        if root.endswith('/') and (a == r or a.startswith(r + '/')):
            return a
        if not root.endswith('/') and a == r:
            return a
    raise PermissionError(f'{path}: outside the football write area')


def check_output_name(path):
    """Generated files (renders, covers, reports) must carry an FB- id in their file or folder name."""
    a = check_write(path)
    if not re.search(r'(^|/)FB-', a):
        raise PermissionError(f'{path}: generated football files must carry an FB- id')
    return a


def new_production(slug, date=None, root=None):
    cfg = division()
    pid = production_id(slug, date)
    base = os.path.join(root or cfg['paths']['productions_root'], pid)
    check_output_name(base)
    if os.path.exists(base):
        raise FileExistsError(f'{base} already exists (never overwritten)')
    for sub in cfg['paths']['production_subdirs']:
        os.makedirs(os.path.join(base, sub))
    meta = {'id': pid, 'division': 'football', 'created': _dt.datetime.now(_dt.timezone.utc).isoformat(timespec='seconds'),
            'status': 'planned', 'phase': cfg['phase']['current'], 'publishing': 'disabled',
            'versions': cfg['video']['versions'], 'credits': {'elevenlabs': 0}, 'log': []}
    with open(os.path.join(base, 'production.json'), 'x', encoding='utf-8') as fh:
        json.dump(meta, fh, indent=1)
    return base


# ---------- shared engine (read-only) ----------

def registry():
    return load('shared-engine.json')


def component(cid):
    for c in registry()['components']:
        if c['id'] == cid:
            return c
    raise KeyError(cid)


def blob_at(ref, path):
    out = git('ls-tree', ref, '--', path, check=False).split()
    return out[2] if len(out) >= 3 else None


def ref_available(ref):
    return subprocess.run(['git', '-C', REPO, 'cat-file', '-e', f'{ref}^{{commit}}'], capture_output=True).returncode == 0


def verify(c):
    """Check that the pinned component (and its deps) still has the same content at its ref."""
    if not ref_available(c['ref']):
        return {'id': c['id'], 'status': 'UNVERIFIED', 'why': f"commit {c['ref'][:7]} ({c['ref_name']}) not fetched"}
    bad = [d['path'] for d in [{'path': c['path'], 'blob': c['blob']}] + c['deps'] if blob_at(c['ref'], d['path']) != d['blob']]
    if bad:
        return {'id': c['id'], 'status': 'FAIL', 'why': 'content changed: ' + ', '.join(bad)}
    st = {'id': c['id'], 'status': 'PASS', 'category': c['category']}
    if c['on_main']:
        # the working copy must still hold that same content (basketball untouched)
        wt = git('hash-object', '--', c['path'], check=False).strip() if os.path.isfile(os.path.join(REPO, c['path'])) else None
        if wt and wt != c['blob']:
            st = {'id': c['id'], 'status': 'FAIL', 'why': 'working copy differs from the pinned blob'}
    return st


def resolve(cid, cache_root=None):
    """Executable path of a shared component. Category C is refused."""
    c = component(cid)
    if c['category'] == 'C':
        raise PermissionError(f'{cid} is basketball-specific (category C): football must not use it')
    v = verify(c)
    if v['status'] != 'PASS':
        raise RuntimeError(f"{cid}: {v['status']} {v.get('why', '')}")
    head = git('rev-parse', 'HEAD').strip()
    if c['on_main'] and blob_at(head, c['path']) == c['blob']:
        return os.path.join(REPO, c['path'])
    cache = cache_root or os.path.join(FOOTBALL, '.cache', 'shared', c['ref'][:12])
    if cache_root is None:
        check_write(cache)
    for p in [c['path']] + [d['path'] for d in c['deps']]:
        dst = os.path.join(cache, p)
        if os.path.exists(dst):
            continue
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        data = subprocess.run(['git', '-C', REPO, 'show', f"{c['ref']}:{p}"], capture_output=True, check=True).stdout
        with open(dst, 'wb') as fh:
            fh.write(data)
        if c.get('executable') and p == c['path']:
            os.chmod(dst, 0o755)
    return os.path.join(cache, c['path'])
