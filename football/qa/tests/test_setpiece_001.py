"""FB-SETPIECE-001 regression tests: the short-corner play stays legal and physically plausible, the play
file is the build of its spec, the motion QC on the real engine sampling passes, and the roadmap holds."""
import json
import os
import re
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FOOTBALL = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(FOOTBALL, 'scripts'))
sys.dont_write_bytecode = True

import fb_motion  # noqa: E402

SP = os.path.join(FOOTBALL, 'tactical-library', 'setpieces')
SPEC = os.path.join(SP, 'FB-SETPIECE-001.spec.json')
PLAY = os.path.join(FOOTBALL, 'tactical-library', 'plays', 'FB-PLAY-SP001-simple-short-corner.json')
EP = os.path.join(FOOTBALL, 'remotion', 'src', 'episodes', 'simpleShortCorner.ts')


def jload(p):
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


class ShortCorner(unittest.TestCase):
    def test_play_is_the_build_of_its_spec(self):
        self.assertEqual(fb_motion.build(jload(SPEC)), jload(PLAY))

    def test_rules_and_physics_validator(self):
        res = fb_motion.validate(jload(PLAY))
        bad = [r for r in res if r['status'] != 'PASS']
        self.assertEqual(bad, [])
        names = ' '.join(r['check'] for r in res)
        for must in ('Law 17: ball inside the corner arc', '9.15 m from the corner arc', 'kicker does not touch', 'onside at pass', 'pass lane', 'corner flagposts'):
            self.assertIn(must, names)

    def test_motion_qc_on_engine_sampling(self):
        node = subprocess.run(['node', os.path.join(FOOTBALL, 'qa', 'qc_play_motion.mjs'), PLAY], capture_output=True, text=True)
        self.assertEqual(node.returncode, 0, node.stdout + node.stderr)
        self.assertIn('PASS', node.stdout)

    def test_ground_pass_physics_v2(self):
        d = jload(PLAY)
        passes = [e for e in d['ball']['events'] if e['type'] == 'pass']
        self.assertTrue(passes)
        for e in passes:
            self.assertEqual(e.get('height'), 'ground')
            self.assertGreaterEqual(e['decel'], 0.8)
            self.assertLessEqual(e['decel'], 3.0)


class Edit(unittest.TestCase):
    def test_script_inside_duration_and_ordered(self):
        src = open(EP, encoding='utf-8').read()
        dur = float(re.search(r'duration: ([\d.]+)', src).group(1))
        lines = [(float(a), float(b)) for a, b in re.findall(r"\[([\d.]+), ([\d.]+), '", src)]
        self.assertTrue(20 <= dur <= 25.5)
        self.assertTrue(lines)
        for (a, b), (c, _) in zip(lines, lines[1:]):
            self.assertLess(a, b)
            self.assertLessEqual(b, c)
        self.assertLessEqual(lines[-1][1], dur)

    def test_composition_registered_with_fb_id(self):
        root = open(os.path.join(FOOTBALL, 'remotion', 'src', 'Root.tsx'), encoding='utf-8').read()
        self.assertIn('id="FBSetPiece001"', root)

    def test_no_aerial_ball_no_shot_in_level_1(self):
        d = jload(PLAY)
        self.assertFalse([e for e in d['ball']['events'] if e['type'] in ('shot', 'cross') or e.get('height') in ('low', 'lofted')])
        self.assertFalse([p for p in d['players'] if p.get('actions')])  # no animated goalkeeper


class Roadmap(unittest.TestCase):
    def test_eight_videos_in_order_and_only_001_started(self):
        r = jload(os.path.join(SP, 'roadmap.json'))
        ids = [v['id'] for v in r['videos']]
        self.assertEqual(ids, [f'FB-SETPIECE-{i:03d}' for i in range(1, 9)])
        self.assertTrue(all(v['status'] == 'planned' for v in r['videos'][1:]))


if __name__ == '__main__':
    unittest.main()
