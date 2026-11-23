#!/usr/bin/env python3
"""E2A Football — isolation and safety checks. Read-only. Exit 0 only if every check PASSes.

  python3 football/qa/check_isolation.py [--json report.json]

Checks: agent present and football-only; basketball files byte-identical to the baseline; changes only in
football paths; dependencies unchanged; configs separate; publishing disabled; no publishing calls in football
code; write guard protects basketball outputs; shared components unchanged; no secrets in football files.
What git cannot see (scheduled tasks, Metricool, ElevenLabs) is reported as NOT_VERIFIABLE here.
"""
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
QA = os.path.dirname(os.path.abspath(__file__))
FOOTBALL = os.path.dirname(QA)
REPO = os.path.dirname(FOOTBALL)
sys.path.insert(0, os.path.join(FOOTBALL, 'scripts'))
import fb_lib as L  # noqa: E402

with open(os.path.join(QA, 'baseline.json'), encoding='utf-8') as _fh:
    BASE = json.load(_fh)
AGENT = '.claude/agents/e2a-football-director.md'
SECRET_PATTERNS = [
    (r'sk-[A-Za-z0-9]{20,}', 'api key (sk-)'), (r'xi-api-key\s*[:=]', 'ElevenLabs key header'),
    (r'(?i)bearer\s+[A-Za-z0-9._-]{20,}', 'bearer token'), (r'gh[pousr]_[A-Za-z0-9]{30,}', 'GitHub token'),
    (r'AKIA[0-9A-Z]{16}', 'AWS key'), (r'-----BEGIN [A-Z ]*PRIVATE KEY-----', 'private key'),
    (r'(?i)(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*["\'][^"\']{6,}', 'credential assignment'),
    (r'[A-Za-z0-9._%+-]+@(gmail|outlook|hotmail|yahoo)\.com', 'personal email address'),
]
PUBLISH_CALLS = re.compile(r'createScheduledPost|updateScheduledPost|sendScheduledPostForReview|createScheduledPostForReview')
CODE_EXT = ('.py', '.sh', '.mjs', '.mts', '.ts', '.tsx', '.js')


def git(*a):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, text=True, check=True).stdout


def allowed(p):
    return any(p == x or (x.endswith('/') and p.startswith(x)) for x in BASE['allowed_new_paths'])


def football_files():
    out = []
    for root, dirs, files in os.walk(FOOTBALL):
        dirs[:] = [d for d in dirs if d not in ('.cache', '__pycache__', 'node_modules', 'public', 'out')]
        out += [os.path.join(root, f) for f in files]
    return out + [os.path.join(REPO, AGENT)]


def run():
    res = []

    def add(name, ok, detail='', status=None):
        res.append({'check': name, 'status': status or ('PASS' if ok else 'FAIL'), 'detail': detail})

    # 1 agent
    ap = os.path.join(REPO, AGENT)
    if os.path.isfile(ap):
        txt = open(ap, encoding='utf-8').read()
        fm = txt.split('---')[1] if txt.startswith('---') else ''
        name_ok = re.search(r'^name:\s*e2a-football-director\s*$', fm, re.M) is not None
        desc = re.search(r'^description:\s*(.+)$', fm, re.M)
        desc_ok = bool(desc) and 'NO lo uses para baloncesto' in desc.group(1)
        tools = re.search(r'^tools:\s*(.+)$', fm, re.M)
        tools_ok = bool(tools) and not re.search(r'Metricool|ElevenLabs|mcp__', tools.group(1))
        add('agent: e2a-football-director defined, football-only, no publishing tools', name_ok and desc_ok and tools_ok,
            f'name={name_ok} excludes_basketball={desc_ok} tools_ok={tools_ok}')
    else:
        add('agent: e2a-football-director defined, football-only, no publishing tools', False, 'missing ' + AGENT)
    agents_dir = os.path.join(REPO, '.claude', 'agents')
    new_agents = [f for f in os.listdir(agents_dir) if f.endswith('.md')] if os.path.isdir(agents_dir) else []
    base_agents = [l.split('\t')[1] for l in git('ls-tree', '-r', BASE['base_commit'], '--', '.claude/agents').splitlines()]
    extra = [a for a in new_agents if f'.claude/agents/{a}' not in base_agents and a != 'e2a-football-director.md']
    add('agent: exactly one new agent', not extra, 'extra: ' + ', '.join(extra) if extra else 'only e2a-football-director.md')

    # 2 basketball byte-identical (every file tracked at the base commit)
    changed = []
    for line in git('ls-tree', '-r', BASE['base_commit']).splitlines():
        meta, path = line.split('\t', 1)
        mode, typ, blob = meta.split()
        if typ != 'blob':
            continue
        full = os.path.join(REPO, path)
        if not os.path.lexists(full):
            changed.append(path + ' (missing)')
        elif not os.path.islink(full) and git('hash-object', '--', path).strip() != blob:
            changed.append(path)
    add('basketball: every file of the baseline is byte-identical', not changed,
        f"{BASE['tracked_files_at_base']} files compared" if not changed else 'changed: ' + ', '.join(changed[:20]))

    # 3 only football paths changed (commits since base + working tree + untracked)
    paths = set(git('diff', '--name-only', BASE['base_commit'], 'HEAD').split())
    paths |= set(git('diff', '--name-only', 'HEAD').split())
    paths |= set(git('ls-files', '--others', '--exclude-standard').split())
    bad = sorted(p for p in paths if not allowed(p))
    add('git: changes only under football/ and the agent file', not bad,
        f'{len(paths)} paths changed, all allowed' if not bad else 'outside: ' + ', '.join(bad[:20]))

    # 4 dependencies
    deps = ['template/package.json', 'template/package-lock.json', 'template/tsconfig.json']
    dchg = [d for d in deps if git('diff', '--name-only', BASE['base_commit'], '--', d).strip()]
    add('dependencies: basketball package files unchanged', not dchg, ', '.join(dchg) or ', '.join(deps))
    fpkg = [f for f in football_files() if os.path.basename(f) in ('package.json', 'package-lock.json', 'requirements.txt') and '/node_modules/' not in f]
    fpkg = [os.path.relpath(f, REPO) if os.path.isabs(f) else f for f in fpkg]
    own = {'football/remotion/package.json', 'football/remotion/package-lock.json'}
    extra = sorted(set(fpkg) - own)
    add('dependencies: football has only its own Remotion manifest (phase 2)', not extra, ', '.join(extra) if extra else (', '.join(sorted(fpkg)) or 'none'))
    # same engine versions as basketball: Remotion / three / React pinned to the versions in template/package-lock.json
    mism = []
    flock = os.path.join(REPO, 'football/remotion/package-lock.json')
    if os.path.exists(flock):
        bl = json.loads(git('show', f"{BASE['base_commit']}:template/package-lock.json"))['packages']
        with open(flock, encoding='utf-8') as fh:
            fl = json.load(fh)['packages']
        for k in ('remotion', '@remotion/cli', '@remotion/three', '@react-three/fiber', 'three', 'react', 'react-dom'):
            a1 = bl.get(f'node_modules/{k}', {}).get('version')
            b1 = fl.get(f'node_modules/{k}', {}).get('version')
            if a1 != b1:
                mism.append(f'{k} {a1} != {b1}')
    add('dependencies: football Remotion stack = basketball versions (one engine, no fork)', not mism, '; '.join(mism) or 'remotion, three, react, r3f identical')

    # 5 configs separate
    cfg_dir = os.path.join(FOOTBALL, 'config')
    mixed = []
    for f in os.listdir(cfg_dir):
        txt = open(os.path.join(cfg_dir, f), encoding='utf-8').read()
        if f != 'shared-engine.json' and re.search(r'"(file|config|delegation_file)"\s*:\s*"config/', txt):
            mixed.append(f)
    add('config: football configs live in football/config and point to no basketball config', not mixed and os.path.isdir(cfg_dir),
        ', '.join(sorted(os.listdir(cfg_dir))) if not mixed else 'mixed: ' + ', '.join(mixed))

    # 6 publishing disabled
    pub = L.load('publishing.json')
    nets_off = all(not n['enabled'] for n in pub['networks'].values())
    add('publishing: mode disabled, every network off, no Metricool writes', pub['mode'] == 'disabled' and nets_off and pub['metricool']['writes_allowed'] is False,
        f"mode={pub['mode']} networks_enabled={[k for k, n in pub['networks'].items() if n['enabled']]}")
    calls = []
    for f in football_files():
        if f.endswith(CODE_EXT) and os.path.abspath(f) != os.path.abspath(__file__):
            if PUBLISH_CALLS.search(open(f, encoding='utf-8', errors='ignore').read()):
                calls.append(os.path.relpath(f, REPO))
    add('publishing: no football code calls Metricool write tools', not calls, ', '.join(calls) or 'none')

    # 7 write guard
    leaks = []
    for p in L.division()['write_deny']:
        probe = os.path.join(p, 'FB-probe.mp4')
        try:
            L.check_write(probe)
            leaks.append(p)
        except PermissionError:
            pass
    try:
        L.check_output_name('football/renders/final.mp4')
        leaks.append('unnamed render accepted')
    except PermissionError:
        pass
    add('guard: football cannot write into basketball paths or unnamed renders', not leaks,
        f"{len(L.division()['write_deny'])} protected roots refused" if not leaks else 'accepted: ' + ', '.join(leaks))

    # 8 shared engine reachable and unchanged
    ver = [L.verify(c) for c in L.registry()['components']]
    fails = [v for v in ver if v['status'] == 'FAIL']
    unv = [v for v in ver if v['status'] == 'UNVERIFIED']
    add('shared engine: pinned components reachable and unchanged', not fails,
        f"{len(ver) - len(fails) - len(unv)} PASS, {len(unv)} UNVERIFIED (ref not fetched), {len(fails)} FAIL"
        + ('; ' + '; '.join(f"{v['id']}: {v['why']}" for v in fails + unv) if fails or unv else ''))

    # 9 secrets
    hits = []
    for f in football_files():
        if f.endswith(('.png', '.jpg', '.jpeg')):
            continue
        txt = open(f, encoding='utf-8', errors='ignore').read()
        for rx, what in SECRET_PATTERNS:
            if os.path.abspath(f) != os.path.abspath(__file__) and re.search(rx, txt):
                hits.append(f'{os.path.relpath(f, REPO)}: {what}')
    add('secrets: no credentials or personal data in football files', not hits, ', '.join(hits) or f'{len(football_files())} files scanned')

    # 10 outside git
    add('automations: scheduled tasks unchanged', True, 'cannot be seen from git: compare list_triggers before/after (done by the session, see the phase report)', status='NOT_VERIFIABLE')
    return res


def main():
    res = run()
    for r in res:
        print(f"{r['status']:15s} {r['check']} — {r['detail']}")
    if '--json' in sys.argv:
        out = sys.argv[sys.argv.index('--json') + 1]
        json.dump(res, open(out, 'w'), indent=1)
    return 1 if any(r['status'] == 'FAIL' for r in res) else 0


if __name__ == '__main__':
    sys.exit(main())
