#!/usr/bin/env python3
"""Football adapter for the shared cover tool (category B): same tool, called with the 2026 E2A logo.
The basketball tool keeps its own default (old logo) untouched.

  python3 football/scripts/fb_cover.py VIDEO.mp4 --at 2.5 --title "Who Is Free?" --out <.../FB-.../thumbnails/FB-...-cover.jpg>
"""
import argparse
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fb_lib as L  # noqa: E402


def load_cover_module():
    path = L.resolve('thumbnails.cover')
    spec = importlib.util.spec_from_file_location('e2a_shared_make_cover', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('video'); ap.add_argument('--at', type=float, required=True)
    ap.add_argument('--title', required=True); ap.add_argument('--out', required=True)
    ap.add_argument('--report')
    a = ap.parse_args(argv)
    out = L.check_output_name(a.out)
    if a.report:
        L.check_output_name(a.report)
    logo = os.path.join(L.REPO, L.load('brand.json')['logo']['white'])
    mod = load_cover_module()
    rep = mod.make_cover(a.video, a.at, a.title, out, logo=logo)
    if a.report:
        with open(a.report, 'w', encoding='utf-8') as fh:
            json.dump(rep, fh, indent=1, default=str)
    print(json.dumps({'out': out, 'logo': os.path.relpath(logo, L.REPO)}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
