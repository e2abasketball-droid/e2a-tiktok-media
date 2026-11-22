#!/usr/bin/env python3
"""E2A Football command line (phase 1: infrastructure only; nothing here renders, publishes or spends credits).

  python3 football/scripts/fb.py paths
  python3 football/scripts/fb.py new-production <slug> [--date YYYY-MM-DD] [--root DIR]
  python3 football/scripts/fb.py shared list | verify | resolve <component-id>
  python3 football/scripts/fb.py check-play <FB-PLAY.json>
  python3 football/scripts/fb.py guard <path>          # may football write here?
"""
import argparse
import datetime as dt
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'engine'))
import fb_lib as L  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(prog='fb.py')
    sp = ap.add_subparsers(dest='cmd', required=True)
    sp.add_parser('paths')
    n = sp.add_parser('new-production'); n.add_argument('slug'); n.add_argument('--date'); n.add_argument('--root')
    s = sp.add_parser('shared'); s.add_argument('action', choices=['list', 'verify', 'resolve']); s.add_argument('id', nargs='?')
    c = sp.add_parser('check-play'); c.add_argument('file')
    g = sp.add_parser('guard'); g.add_argument('path')
    a = ap.parse_args(argv)

    if a.cmd == 'paths':
        cfg = L.division()
        print(json.dumps({'division': cfg['division'], 'phase': cfg['phase'], 'paths': cfg['paths'],
                          'publishing': L.load('publishing.json')['mode']}, indent=1, ensure_ascii=False))
    elif a.cmd == 'new-production':
        date = dt.date.fromisoformat(a.date) if a.date else None
        print(L.new_production(a.slug, date, a.root))
    elif a.cmd == 'shared':
        reg = L.registry()['components']
        if a.action == 'list':
            for comp in reg:
                print(f"{comp['category']}  {comp['id']:34s} {comp['ref_name']:30s} {comp['path']}")
        elif a.action == 'verify':
            res = [L.verify(comp) for comp in reg]
            for r in res:
                print(f"{r['status']:10s} {r['id']} {r.get('why', '')}")
            return 1 if any(r['status'] == 'FAIL' for r in res) else 0
        else:
            if not a.id:
                ap.error('resolve needs a component id')
            try:
                print(L.resolve(a.id))
            except (PermissionError, RuntimeError) as e:
                print('DENY ', e)
                return 1
    elif a.cmd == 'check-play':
        import playcheck
        err, warn = playcheck.check_file(a.file)
        for w in warn:
            print('WARN ', w)
        for e in err:
            print('ERROR', e)
        print('PASS' if not err else 'FAIL')
        return 1 if err else 0
    elif a.cmd == 'guard':
        try:
            print('ALLOW', L.check_write(a.path))
        except PermissionError as e:
            print('DENY ', e)
            return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
