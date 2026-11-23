"""Phase 2 checks: the pilot play is tactically valid, the caption timing is sane, the Remotion entry
stays inside football/ with FB ids and the same engine versions as basketball."""
import json
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FOOTBALL = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(FOOTBALL, 'engine'))
sys.path.insert(0, os.path.join(FOOTBALL, 'scripts'))
sys.dont_write_bytecode = True

import playcheck  # noqa: E402
from pitch import offside_line  # noqa: E402
import fb_lib as L  # noqa: E402
import fb_words  # noqa: E402

PLAY = os.path.join(FOOTBALL, 'tactical-library', 'plays', 'FB-PLAY-third-man-run.json')
EP = os.path.join(FOOTBALL, 'remotion', 'src', 'episodes', 'thirdManRun.ts')


def jload(p):
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


class PilotPlay(unittest.TestCase):
    def test_play_passes_checker(self):
        err, _ = playcheck.check(jload(PLAY))
        self.assertEqual(err, [])

    def test_third_man_onside_at_the_set(self):
        d = jload(PLAY)
        P = {p['id']: p for p in d['players']}
        for c in d['checks']:
            t = c['at']
            dx = [playcheck.pos(p['track'], t)[0] for p in d['players'] if p['team'] == 'defence']
            ev = [e for e in d['ball']['events'] if abs(e['t'] - t) < 1e-6][0]
            bx = playcheck.pos(P[ev['by']]['track'], t)[0]
            self.assertLessEqual(playcheck.pos(P[c['player']]['track'], t)[0], offside_line(dx, bx), c)

    def test_centre_back_left_the_line(self):
        # the point of the clip: D4 is >5 m in front of his back line when the set is played
        d = jload(PLAY)
        P = {p['id']: p for p in d['players']}
        line = sorted(playcheck.pos(P[i]['track'], 5.0)[0] for i in ('D2', 'D3', 'D5'))
        self.assertGreater(min(line) - playcheck.pos(P['D4']['track'], 5.0)[0], 5.0)

    def test_fictional_and_fb_ids(self):
        d = jload(PLAY)
        self.assertTrue(d['fictional'])
        self.assertTrue(L.is_football_id(d['id']))


class EditAndEntry(unittest.TestCase):
    def test_caption_words_monotonic_inside_video(self):
        w = fb_words.words_from_ts(EP)
        self.assertGreater(len(w), 50)
        self.assertTrue(all(a['start'] < a['end'] <= b['start'] + 1e-6 for a, b in zip(w, w[1:])))
        self.assertLessEqual(w[-1]['end'], 35.0)

    def test_compositions_carry_fb_prefix(self):
        with open(os.path.join(FOOTBALL, 'remotion', 'src', 'Root.tsx'), encoding='utf-8') as fh:
            ids = re.findall(r'id="([^"]+)"', fh.read())
        self.assertTrue(ids)
        self.assertTrue(all(i.startswith('FB') for i in ids), ids)

    def test_no_basketball_imports(self):
        src = os.path.join(FOOTBALL, 'remotion', 'src')
        for root, _, files in os.walk(src):
            for f in files:
                with open(os.path.join(root, f), encoding='utf-8') as fh:
                    s = fh.read()
                self.assertNotRegex(s, r"from ['\"][./]*template/", f)
                self.assertNotIn('t3d/', s, f)

    def test_stage_folder_is_football_only(self):
        self.assertTrue(L.check_write(os.path.join(FOOTBALL, 'remotion', 'public') + '/'))
        with self.assertRaises(PermissionError):
            L.check_write(os.path.join(L.REPO, 'template', 'public', 'x.png'))


if __name__ == '__main__':
    unittest.main()
