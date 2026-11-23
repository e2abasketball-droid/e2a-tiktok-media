"""E2A Football phase-1 tests: config, ids, guard, shared-engine access, play checker, agent, isolation.
Run: python3 -m unittest discover -s football/qa/tests   (no network, no credits, no publishing)."""
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
T = os.path.dirname(os.path.abspath(__file__))
FOOTBALL = os.path.dirname(os.path.dirname(T))
REPO = os.path.dirname(FOOTBALL)
sys.path[:0] = [os.path.join(FOOTBALL, 'scripts'), os.path.join(FOOTBALL, 'engine'), os.path.join(FOOTBALL, 'qa')]
import fb_lib as L  # noqa: E402
import pitch  # noqa: E402
import playcheck  # noqa: E402

FFMPEG = shutil.which('ffmpeg') and shutil.which('ffprobe')
def jload(p):
    with open(p, encoding='utf-8') as fh:
        return json.load(fh)


SAMPLE = os.path.join(FOOTBALL, 'tactical-library', 'plays', 'FB-PLAY-third-man-run.json')


class Config(unittest.TestCase):
    def test_configs_parse_and_are_football(self):
        d = L.division()
        self.assertEqual(d['id_prefix'], 'FB')
        self.assertIn(d['phase']['current'], (1, 2))  # phase 2 approved 2026-11-23 (local production only)
        self.assertTrue(d['phase']['next_requires_approval'])
        b = L.load('brand.json')
        self.assertEqual(b['palette'], {**b['palette'], 'navy': '#0B1C3D', 'gold': '#C9A24D', 'gold_deep': '#A9842F', 'white': '#FFFFFF'})
        self.assertFalse(b['audio_rules']['ball_bounce_sfx'])
        for k in ('white', 'navy'):
            self.assertTrue(os.path.isfile(os.path.join(REPO, b['logo'][k])), b['logo'][k])
            self.assertIn('2026', b['logo'][k])

    def test_publishing_disabled(self):
        p = L.load('publishing.json')
        self.assertEqual(p['mode'], 'disabled')
        self.assertTrue(all(not n['enabled'] for n in p['networks'].values()))
        self.assertFalse(p['metricool']['writes_allowed'])
        self.assertEqual(p['networks']['youtube']['catalogue'], 'FB')
        self.assertIsNone(p['delegation']['file'])


class Ids(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(L.production_id('Third Man Run!', dt.date(2026, 11, 23)), 'FB-20261123-third-man-run')
        self.assertEqual(L.content_id(dt.date(2026, 11, 23), 1), 'FB-TACTICAL-20261123-V01')
        self.assertTrue(L.is_football_id('FB-PLAY-third-man-run'))
        self.assertFalse(L.is_football_id('E2A-TACTICAL-20261117-V01'))
        self.assertFalse(L.is_football_id('BB-20261123-x'))
        with self.assertRaises(ValueError):
            L.slugify('!!!')


class Guard(unittest.TestCase):
    def test_basketball_paths_refused(self):
        for p in ['template/src/Root.tsx', 'tools/tactical_publisher.py', 'config/tactical_studio.json', 'produccion/tactical/x',
                  'music/history.json', 'videos/x.mp4', 'editing-library/index.json', '.claude/skills/x', '/mnt/project-files/tactical-studio/FB-x.mp4',
                  'football/../template/x', '/etc/passwd', '.claude/agents/e2a-3d-animation.md']:
            with self.assertRaises(PermissionError, msg=p):
                L.check_write(p)

    def test_football_paths_allowed(self):
        self.assertTrue(L.check_write('football/x.json').endswith('football/x.json'))
        L.check_write('/mnt/project-files/football/productions/FB-20261123-a/renders/FB-20261123-a-main.mp4')
        L.check_write('.claude/agents/e2a-football-director.md')

    def test_generated_names_need_fb_id(self):
        with self.assertRaises(PermissionError):
            L.check_output_name('/mnt/project-files/football/final.mp4')
        L.check_output_name('/mnt/project-files/football/productions/FB-20261123-a/renders/main.mp4')

    def test_new_production_never_overwrites(self):
        with tempfile.TemporaryDirectory() as td:
            root = os.path.join(FOOTBALL, '.cache', 'test-prod-' + os.path.basename(td))
            try:
                base = L.new_production('Pilot one', dt.date(2026, 11, 23), root=root)
                self.assertTrue(os.path.basename(base).startswith('FB-20261123-pilot-one'))
                meta = jload((os.path.join(base, 'production.json')))
                self.assertEqual(meta['publishing'], 'disabled')
                self.assertEqual(sorted(os.listdir(base)), sorted(L.division()['paths']['production_subdirs'] + ['production.json']))
                with self.assertRaises(FileExistsError):
                    L.new_production('Pilot one', dt.date(2026, 11, 23), root=root)
            finally:
                shutil.rmtree(root, ignore_errors=True)


class SharedEngine(unittest.TestCase):
    def test_registry_categories(self):
        comps = L.registry()['components']
        ids = [c['id'] for c in comps]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue({c['category'] for c in comps} <= {'A', 'B', 'C'})
        for c in comps:
            self.assertEqual(L.verify(c)['status'], 'PASS', c['id'])

    def test_category_c_refused(self):
        for c in L.registry()['components']:
            if c['category'] == 'C':
                with self.assertRaises(PermissionError):
                    L.resolve(c['id'])

    def test_resolve_main_component_in_place(self):
        p = L.resolve('narration.voice-splice')
        self.assertEqual(p, os.path.join(REPO, 'template/scripts/tactical-voice.py'))

    def test_resolve_branch_component_into_cache(self):
        p = L.resolve('trial.variant')
        self.assertIn(os.path.join('football', '.cache', 'shared'), p)
        self.assertEqual(subprocess.run(['git', 'hash-object', p], capture_output=True, text=True).stdout.strip(), L.component('trial.variant')['blob'])

    @unittest.skipUnless(FFMPEG, 'ffmpeg not installed')
    def test_shared_trial_variant_and_cover_on_synthetic_fb_clip(self):
        """End-to-end on a 4 s synthetic clip (lavfi test pattern + tone): no credits, no network, FB paths only."""
        root = os.path.join(FOOTBALL, '.cache', 'it')
        prod = os.path.join(root, 'FB-20261123-synthetic')
        os.makedirs(os.path.join(prod, 'renders'), exist_ok=True)
        os.makedirs(os.path.join(prod, 'thumbnails'), exist_ok=True)
        try:
            src = os.path.join(prod, 'renders', 'FB-20261123-synthetic-main.mp4')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=1080x1920:rate=30:duration=4',
                            '-f', 'lavfi', '-i', 'sine=frequency=220:duration=4', '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
                            '-c:a', 'aac', src], check=True)
            trial = os.path.join(prod, 'renders', 'FB-20261123-synthetic-trial.mp4')
            L.check_output_name(trial)
            r = subprocess.run(['bash', L.resolve('trial.variant'), src, trial], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            ssim = float(r.stdout.split('All:')[1].split()[0])
            self.assertLess(ssim, 0.99)  # a different file, as the trial-reel rule requires
            try:
                import PIL  # noqa: F401
            except ImportError:
                self.skipTest('Pillow missing')
            cover = os.path.join(prod, 'thumbnails', 'FB-20261123-synthetic-cover.jpg')
            r = subprocess.run([sys.executable, os.path.join(FOOTBALL, 'scripts', 'fb_cover.py'), src, '--at', '1.0',
                                '--title', 'Who Is Free?', '--out', cover], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn('e2a_logo_2026_white.png', r.stdout)
            self.assertTrue(os.path.getsize(cover) > 0)
        finally:
            shutil.rmtree(root, ignore_errors=True)


class Plays(unittest.TestCase):
    def test_sample_play_passes(self):
        self.assertEqual(playcheck.check_file(SAMPLE), ([], []))

    def test_offside_detected(self):
        play = jload((SAMPLE))
        for p in play['players']:
            if p['id'] == 'A8':
                p['track'] = [[0, 20, -4], [6, 24, -2]]  # beyond the second-last defender at the pass
        err, _ = playcheck.check(play)
        self.assertTrue(any('offside' in e for e in err), err)

    def test_rules(self):
        play = jload((SAMPLE))
        play['fictional'] = False
        play['players'][0]['track'] = [[0, -22, 0], [0.5, 10, 0]]  # 64 m/s
        play['players'][1]['track'] = [[0, 80, 0]]  # off the pitch
        play['ball']['events'].append({'t': 2, 'type': 'pass', 'by': 'A6', 'to': 'ZZ'})
        err, _ = playcheck.check(play)
        for needle in ('fictional', 'speed', 'off the pitch', 'unknown player'):
            self.assertTrue(any(needle in e for e in err), needle)

    def test_offside_line_rules(self):
        self.assertEqual(pitch.offside_line([50, 10, 5], ball_x=0), 10)
        self.assertEqual(pitch.offside_line([50, -10, -20], ball_x=-5), 0)  # never in the attacker's own half
        self.assertEqual(pitch.offside_line([50, 10], ball_x=30), 30)        # ball nearer the goal line
        self.assertTrue(pitch.Pitch().in_penalty_area(45, 0))

    def test_library(self):
        lib = jload((os.path.join(FOOTBALL, 'tactical-library', 'concepts.json')))
        for c in lib['concepts']:
            self.assertTrue(L.is_football_id(c['id']), c['id'])
        forms = jload((os.path.join(FOOTBALL, 'tactical-library', 'formations.json')))['formations']
        P = pitch.Pitch()
        for name, f in forms.items():
            self.assertEqual(len(f), 11, name)
            self.assertTrue(all(P.inside(x, y) for x, y in f.values()), name)


class Isolation(unittest.TestCase):
    def test_isolation_checks_pass(self):
        import check_isolation
        res = check_isolation.run()
        fails = [r for r in res if r['status'] == 'FAIL']
        self.assertFalse(fails, fails)


if __name__ == '__main__':
    unittest.main()
