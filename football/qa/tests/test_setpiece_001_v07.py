"""FB-SETPIECE-001 V07 ("off-ball timing") regression tests: the play is the build of its spec, the master
timeline is complete and measured, every validator passes (rules/physics, tactics, NEW off-ball timing, engine
motion QC), the NEW edit QC passes (continuity across cuts, box-first framing, run visibility, short replay,
no static outro), the generator reproduces the spec, and the edit reads its play times from the timeline."""
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
import fb_timeline  # noqa: E402

SP = os.path.join(FOOTBALL, 'tactical-library', 'setpieces')
SPEC = os.path.join(SP, 'FB-SETPIECE-001-V07.spec.json')
GEN = os.path.join(SP, 'gen', 'FB-SETPIECE-001-V07.gen.py')
PLAY = os.path.join(FOOTBALL, 'tactical-library', 'plays', 'FB-PLAY-SP001-V07-off-ball-timing.json')
EP = os.path.join(FOOTBALL, 'remotion', 'src', 'episodes', 'offBallTiming.ts')
V05_PLAY = os.path.join(FOOTBALL, 'tactical-library', 'plays', 'FB-PLAY-SP001-V05-near-post-decoy-late-arrival.json')


def jload(p):
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


class Play(unittest.TestCase):
    def test_play_is_the_build_of_its_spec(self):
        self.assertEqual(fb_motion.build(jload(SPEC)), jload(PLAY))

    def test_same_ball_and_defence_design_as_v05(self):
        # V07 changes the off-ball timing and its presentation, not the routine: same ball script, same roles
        a, b = jload(PLAY), jload(V05_PLAY)
        self.assertEqual(a['ball'], b['ball'])
        self.assertEqual(sorted((p['id'], p['role']) for p in a['players']), sorted((p['id'], p['role']) for p in b['players']))

    def test_timeline_named_events(self):
        tl = jload(PLAY)['timeline']
        ids = [e['id'] for e in tl]
        for must in ('PLAYER_A_STARTS_APPROACH', 'CORNER_KICK_CONTACT', 'PLAYER_B_RECEIVES', 'DEFENDER_D_STEPS_OUT', 'DECOY_RUN_BEGINS',
                     'DEFENSIVE_LINE_ADJUSTS', 'LATE_RUNNER_ACCELERATES', 'FINAL_PASS_CONTACT', 'FINAL_RECEIVER_ARRIVES', 'SHOT_CONTACT',
                     'BALL_CROSSES_GOAL_LINE'):
            self.assertIn(must, ids)
        ts = [e['t'] for e in tl]
        self.assertTrue(all(t is not None for t in ts))
        self.assertEqual(ts, sorted(ts))

    def test_reactions_are_measured_not_authored(self):
        play = jload(PLAY)
        for e in play['timeline']:
            if e.get('measure'):
                self.assertAlmostEqual(e['t'], fb_timeline.onset(play, e['measure']['onset'], e['measure']['after']), places=2)

    def test_run_book(self):
        runs = jload(PLAY)['runs']
        self.assertEqual([r['runner'] for r in runs], ['A4', 'A9', 'A6'])
        for r in runs:
            for k in ('trigger', 'cue', 'reacts', 'arrive', 'intent', 'early', 'late'):
                self.assertTrue(r.get(k), (r['runner'], k))

    def test_rules_physics_tactics(self):
        play = jload(PLAY)
        self.assertEqual([r for r in fb_motion.validate(play) if r['status'] != 'PASS'], [])
        self.assertEqual([r for r in fb_tactics.validate(play) if r['status'] != 'PASS'], [])

    def test_offball_timing_validator(self):
        res = fb_timeline.validate(jload(PLAY))
        self.assertEqual([r for r in res if r['status'] == 'FAIL'], [])
        names = ' '.join(r['check'] for r in res)
        for must in ('run onset A4', 'trigger before run A6', 'arrives WITH the ball', 'before the lane is open', 'defender reaction D7',
                     'body prepared: shot A6', 'interpenetration', 'telepathic'):
            self.assertIn(must, names)
        # human judgements are never auto-passed
        self.assertTrue(all(r['status'] == 'NEEDS HUMAN REVIEW' for r in res if r['check'].startswith('visual:')))

    def test_timing_detects_a_late_runner(self):
        # mutation: the late runner starts 0.6 s later -> he can no longer arrive with the ball
        spec = jload(SPEC)
        spec['motion']['A6'] = [dict(w, t=w['t'] + 0.6) if w['t'] >= 4.4 else w for w in spec['motion']['A6']]
        play = fb_motion.build(spec)
        bad = [r['check'] for r in fb_timeline.validate(play) if r['status'] == 'FAIL']
        self.assertTrue(any('A6' in b for b in bad), bad)

    def test_motion_qc_on_engine_sampling(self):
        node = subprocess.run(['node', os.path.join(FOOTBALL, 'qa', 'qc_play_motion.mjs'), PLAY], capture_output=True, text=True)
        self.assertEqual(node.returncode, 0, node.stdout + node.stderr)


class Edit(unittest.TestCase):
    src = open(EP, encoding='utf-8').read()

    def test_edit_qc(self):
        node = subprocess.run(['node', os.path.join(FOOTBALL, 'qa', 'qc_edit.mjs'), EP, 'offBallTimingV07'], capture_output=True, text=True)
        self.assertEqual(node.returncode, 0, node.stdout + node.stderr)
        m = json.loads(node.stdout.split('METRICS ')[1].splitlines()[0])
        self.assertTrue(23 <= m['duration'] <= 29)
        self.assertLessEqual(m['replay_s'], 5.0)
        self.assertEqual(m['static_end_s'], 0)
        self.assertEqual(m['corner_phase_corner_only_s'], 0)

    def test_v06_edit_qc_documents_the_audit(self):
        # the same QC on V06 shows the problems the owner listed (cut rewinds the play, corner-only framing, long replay)
        node = subprocess.run(['node', os.path.join(FOOTBALL, 'qa', 'qc_edit.mjs'), os.path.join(FOOTBALL, 'remotion', 'src', 'episodes', 'nearPostDecoy.ts'),
                               'nearPostDecoyV06'], capture_output=True, text=True)
        self.assertNotEqual(node.returncode, 0)
        self.assertIn('FAIL  [edit] continuity', node.stdout)
        self.assertIn('FAIL  [edit] structure: replay', node.stdout)

    def test_play_times_come_from_the_timeline(self):
        self.assertIn("ev(play, id)", self.src)
        for name in ('CORNER_KICK_CONTACT', 'DECOY_RUN_BEGINS', 'LATE_RUNNER_STARTS', 'FINAL_PASS_CONTACT', 'SHOT_CONTACT'):
            self.assertIn(f"E('{name}')", self.src)

    def test_owner_v07_rules(self):
        self.assertIn("'THE GOAL STARTS', 'OFF THE BALL.'", self.src)
        self.assertIn("'CREATE THE SPACE.', 'TIME THE RUN.'", self.src)
        self.assertIn("type: 'steps'", self.src)
        self.assertIn("type: 'halo'", self.src)
        self.assertIn("type: 'ghost'", self.src)
        self.assertIn("type: 'cue'", self.src)
        self.assertIn('pip:', self.src)
        self.assertIn("role: 'decisive'", self.src)
        self.assertNotIn("type: 'end'", self.src)  # no static end card: discreet signature over the moving picture
        self.assertLessEqual(len(re.findall(r'freeze: \[\[', self.src)), 1)

    def test_compositions_kept(self):
        root = open(os.path.join(FOOTBALL, 'remotion', 'src', 'Root.tsx'), encoding='utf-8').read()
        for cid in ('FBSetPiece001V07', 'FBSetPiece001V06', 'FBSetPiece001V05', 'FBSetPiece001V04', 'FBSetPiece001V03', 'FBSetPiece001'):
            self.assertIn(f'id="{cid}"', root)


class Generator(unittest.TestCase):
    def test_generator_reproduces_the_spec(self):
        before = open(SPEC, encoding='utf-8').read()
        r = subprocess.run([sys.executable, GEN], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(open(SPEC, encoding='utf-8').read(), before)


if __name__ == '__main__':
    unittest.main()
