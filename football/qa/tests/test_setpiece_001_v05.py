"""FB-SETPIECE-001 V05 ("short corner: near-post decoy + late arrival") regression tests: the play is the build
of its spec (defenders driven by behaviours), the rules/physics validator, the NEW tactical validator and the
engine motion QC all pass, the generator reproduces the spec, and the edit keeps the owner's V05 rules
(25-32 s, hook matches the play, short replay, analytical graphics, no V04 composition touched)."""
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
import fb_tactics  # noqa: E402
import fb_defence  # noqa: E402

SP = os.path.join(FOOTBALL, 'tactical-library', 'setpieces')
SPEC = os.path.join(SP, 'FB-SETPIECE-001-V05.spec.json')
GEN = os.path.join(SP, 'gen', 'FB-SETPIECE-001-V05.gen.py')
PLAY = os.path.join(FOOTBALL, 'tactical-library', 'plays', 'FB-PLAY-SP001-V05-near-post-decoy-late-arrival.json')
EP = os.path.join(FOOTBALL, 'remotion', 'src', 'episodes', 'nearPostDecoy.ts')


def jload(p):
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


class Play(unittest.TestCase):
    def test_play_is_the_build_of_its_spec(self):
        self.assertEqual(fb_motion.build(jload(SPEC)), jload(PLAY))

    def test_mixed_defence_eleven_v_eleven(self):
        d = jload(PLAY)
        for team in ('attack', 'defence'):
            ps = [p for p in d['players'] if p['team'] == team]
            self.assertEqual(len(ps), 11)
            self.assertEqual(len([p for p in ps if p['role'] == 'GK']), 1)
        roles = sorted(p['role'] for p in d['players'] if p['team'] == 'defence')
        self.assertEqual(roles, sorted(['GK', 'POST', 'ZONE', 'ZONE', 'ZONE', 'MARK', 'MARK', 'MARK', 'SHORT', 'EDGE', 'OUTLET']))

    def test_every_outfield_defender_is_behaviour_driven(self):
        spec = jload(SPEC)
        outfield = [p['id'] for p in spec['players'] if p['team'] == 'defence' and p['role'] != 'GK']
        self.assertEqual(sorted(spec['behaviours']), sorted(outfield))
        self.assertFalse(any(d in spec['motion'] for d in outfield))

    def test_sequence(self):
        ev = sorted(jload(PLAY)['ball']['events'], key=lambda e: e['t'])
        kinds = [(e['type'], e.get('by'), e.get('to')) for e in ev if e['type'] in ('pass', 'shot')]
        self.assertEqual(kinds, [('pass', 'A7', 'A10'), ('pass', 'A10', 'A7'), ('pass', 'A7', 'A6'), ('shot', 'A6', None)])

    def test_rules_and_physics_validator(self):
        res = fb_motion.validate(jload(PLAY))
        self.assertEqual([r for r in res if r['status'] != 'PASS'], [])

    def test_tactical_validator(self):
        res = fb_tactics.validate(jload(PLAY))
        self.assertEqual([r for r in res if r['status'] != 'PASS'], [])
        names = ' '.join(r['check'] for r in res)
        for must in ('compact box', 'no attacker free', 'marking D7 on A4', 'delivery under pressure', 'defensive shift',
                     'not free in the box from the start', 'momentary advantage', 'orientation', 'bisector', 'keeper set',
                     'reacts after the strike', 'hard to stop', 'no contact'):
            self.assertIn(must, names)

    def test_motion_qc_on_engine_sampling(self):
        node = subprocess.run(['node', os.path.join(FOOTBALL, 'qa', 'qc_play_motion.mjs'), PLAY], capture_output=True, text=True)
        self.assertEqual(node.returncode, 0, node.stdout + node.stderr)

    def test_behaviour_follower_limits(self):
        # a marker following a sprinting attacker stays within the speed/acceleration limits it is given
        trk = {'A': {'track': [[0, 40, 0], [1, 40, 0], [3, 50, -4]]}}
        pos = lambda pid, t: fb_motion.track_pos(trk[pid]['track'], t)  # noqa: E731
        keys = fb_defence.simulate([{'t0': 0, 'type': 'mark', 'target': 'A', 'gap': 1.0, 'ball': 0}], 4.0, pos, lambda t: (52, -30))
        sp = [((b[1] - a[1]) ** 2 + (b[2] - a[2]) ** 2) ** 0.5 / 0.1 for a, b in zip(keys, keys[1:])]
        self.assertLessEqual(max(sp), 7.7)


class Edit(unittest.TestCase):
    src = open(EP, encoding='utf-8').read()

    def test_duration_and_script(self):
        dur = float(re.search(r'duration: ([\d.]+)', self.src).group(1))
        self.assertTrue(25 <= dur <= 32)
        lines = [(float(a), float(b)) for a, b in re.findall(r"\[([\d.]+), ([\d.]+), [\"']", self.src)]
        self.assertTrue(lines)
        for (a, b), (c, _) in zip(lines, lines[1:]):
            self.assertLess(a, b)
            self.assertLessEqual(b, c)

    def test_owner_v05_rules(self):
        self.assertNotIn('flash:', self.src)
        self.assertIn("UNTIL THEY CREATE IT.", self.src)
        for must in ("look: 'day'", "grade: 'clean'", 'graphicsV2: true', 'subtitles: false'):
            self.assertIn(must, self.src)
        for g in ("type: 'link'", "type: 'cone'", 'trail: true'):
            self.assertIn(g, self.src)
        # replay shorter than V04's 7.2 s, one pause at most
        rep = re.search(r"name: 'replay',\s+from: ([\d.]+)", self.src)
        nxt = re.search(r"name: 'payoff',\s+from: ([\d.]+)", self.src)
        self.assertLessEqual(float(nxt.group(1)) - float(rep.group(1)), 7.0)
        self.assertLessEqual(len(re.findall(r'freeze: \[\[', self.src)), 1)

    def test_compositions(self):
        root = open(os.path.join(FOOTBALL, 'remotion', 'src', 'Root.tsx'), encoding='utf-8').read()
        for cid in ('FBSetPiece001V05', 'FBSetPiece001V04', 'FBSetPiece001V03', 'FBSetPiece001'):
            self.assertIn(f'id="{cid}"', root)


class Generator(unittest.TestCase):
    def test_generator_reproduces_the_spec(self):
        before = open(SPEC, encoding='utf-8').read()
        r = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(open(SPEC, encoding='utf-8').read(), before)


if __name__ == '__main__':
    unittest.main()
