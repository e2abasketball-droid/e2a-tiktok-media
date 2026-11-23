#!/usr/bin/env python3
"""Stage the Remotion public/ folder of the football entry (football/remotion/public/, gitignored).

Fonts come from the shared engine (branding.fonts, category A) through fb_lib.resolve: read in place,
copied only into the ignored staging folder that Remotion serves. The 2026 logo comes from
football/assets/brand/. Optional audio (--audio src:dst) is copied in for a render. Nothing is written
outside football/.
"""
import argparse
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fb_lib as L  # noqa: E402

PUBLIC = os.path.join(L.FOOTBALL, 'remotion', 'public')


def stage(audio=()):
    L.check_write(PUBLIC + '/')
    os.makedirs(PUBLIC, exist_ok=True)
    anton = L.resolve('branding.fonts')
    inter = os.path.join(os.path.dirname(anton), 'inter.woff2')
    c = L.component('branding.fonts')
    if L.git('hash-object', '--', inter).strip() != c['deps'][0]['blob']:
        raise RuntimeError('inter.woff2 differs from the pinned blob')
    out = []
    for src, name in [(anton, 'anton.woff2'), (inter, 'inter.woff2'),
                      (os.path.join(L.FOOTBALL, 'assets', 'brand', 'e2a_logo_2026_white.png'), 'e2a_logo_2026_white.png')]:
        dst = L.check_write(os.path.join(PUBLIC, name))
        shutil.copyfile(src, dst)
        out.append(name)
    for spec in audio:
        src, name = spec.split(':', 1)
        dst = L.check_write(os.path.join(PUBLIC, name))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
        out.append(name)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--audio', action='append', default=[], help='src_path:public_name')
    a = ap.parse_args()
    for n in stage(a.audio):
        print('staged', n)
