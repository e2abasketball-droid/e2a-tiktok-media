"""FB-SETPIECE-001 V03 ("the short corner cutback") regression tests: 11 v 11, three passes and a legal goal,
the play file is the build of its spec, rules/physics validator and the engine motion QC pass, and the edit
keeps the owner's V03 rules (silent, no flashes, day look, clean grade, short labels, 25-31 s)."""
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
SPEC = os.path.join(SP, 'FB-SETPIECE-001-V03.spec.json')
PLAY = os.path.join(FOOTBALL, 'tactical-library', 'plays', 'FB-PLAY-SP001-V03-short-corner-cutback.json')
EP = os.path.join(FOOTBALL, 'remotion', 'src', 'episodes', 'shortCornerCutback.ts')


def jload(p):
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


class Play(unittest.TestCase):
    def test_play_is_the_build_of_its_spec(self):
        self.assertEqual(fb_motion.build(jload(SPEC)), jload(PLAY))

    def test_eleven_v_eleven_with_keepers(self):
        d = jload(PLAY)
        for team in ('attack', 'defence'):
            ps = [p for p in d['players'] if p['team'] == team]
            self.assertEqual(len(ps), 11)
            self.assertEqual(len([p for p in ps if p['role'] == 'GK']), 1)

    def test_three_passes_then_a_goal(self):
        ev = sorted(jload(PLAY)['ball']['events'], key=lambda e: e['t'])
        kinds = [(e['type'], e.get('by'), e.get('to')) for e in ev if e['type'] in ('pass', 'shot')]
        self.assertEqual(kinds, [('pass', 'A7', 'A10'), ('pass', 'A10', 'A7'), ('pass', 'A7', 'A9'), ('shot', 'A9', None)])

    def test_rules_and_physics_validator(self):
        res = fb_motion.validate(jload(PLAY))
        self.assertEqual([r for r in res if r['status'] != 'PASS'], [])
        names = ' '.join(r['check'] for r in res)
        for must in ('Law 17: ball inside the corner arc', '9.15 m from the corner arc', 'kicker does not touch', 'onside at pass A10->A7', 'onside at pass A7->A9',
                     'wholly crosses the goal line', 'between the posts', 'under the crossbar', 'shot lane', 'keeper D1 beaten', 'clear of team-mates'):
            self.assertIn(must, names)

    def test_motion_qc_on_engine_sampling(self):
        node = subprocess.run(['node', os.path.join(FOOTBALL, 'qa', 'qc_play_motion.mjs'), PLAY], capture_output=True, text=True)
        self.assertEqual(node.returncode, 0, node.stdout + node.stderr)
        self.assertIn('the ball wholly crosses the goal line', node.stdout)
        self.assertIn('never passes through a player', node.stdout)


class Edit(unittest.TestCase):
    src = open(EP, encoding='utf-8').read()

    def test_duration_and_script(self):
        dur = float(re.search(r'duration: ([\d.]+)', self.src).group(1))
        self.assertTrue(25 <= dur <= 31)
        lines = [(float(a), float(b)) for a, b in re.findall(r"\[([\d.]+), ([\d.]+), '", self.src)]
        self.assertTrue(lines)
        for (a, b), (c, _) in zip(lines, lines[1:]):
            self.assertLess(a, b)
            self.assertLessEqual(b, c)
        self.assertLessEqual(lines[-1][1], dur)

    def test_owner_v03_rules(self):
        self.assertNotIn('flash:', self.src)  # no white flash transitions
        for banned in ('ONSIDE', '9.15 M', 'ONE PASS'):
            self.assertNotIn(banned, self.src)
        for must in ("look: 'day'", "grade: 'clean'", 'graphicsV2: true', 'subtitles: false', "'3 PASSES.'", 'ATTACK THE SPACE.'):
            self.assertIn(must, self.src)
        for label in ('SHORT PASS', 'DEFENDER STEPS OUT', 'RETURN', 'CUTBACK', 'FINISH'):
            self.assertIn(f"text: '{label}'", self.src)
        self.assertLessEqual(len(re.findall(r'freeze: \[\[', self.src)), 2)

    def test_composition_registered(self):
        root = open(os.path.join(FOOTBALL, 'remotion', 'src', 'Root.tsx'), encoding='utf-8').read()
        self.assertIn('id="FBSetPiece001V03"', root)
        self.assertIn('id="FBSetPiece001"', root)  # V02 kept


if __name__ == '__main__':
    unittest.main()
