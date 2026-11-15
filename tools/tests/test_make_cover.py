import os, subprocess, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import make_cover as mc
from PIL import Image


class TestMakeCover(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.v = os.path.join(cls.tmp, "v.mp4")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "testsrc2=s=1080x1920:d=2:r=30", "-pix_fmt", "yuv420p", cls.v], check=True)

    def test_cover_passes_checks(self):
        out = os.path.join(self.tmp, "c.jpg")
        r = mc.make_cover(self.v, 1.0, "Catch or Backdoor?", out)
        self.assertTrue(r["ok"], r["checks"])
        im = Image.open(out)
        self.assertEqual((im.size, im.format, im.mode), ((1080, 1920), "JPEG", "RGB"))
        x0, y0, x1, y1 = r["title_box"]
        self.assertTrue(420 <= y0 and y1 <= 1500 and x0 >= 78 and x1 <= 1002)
        p = mc.previews(out, os.path.join(self.tmp, "prev"))
        self.assertEqual(Image.open(p["square_1x1"]).size, (360, 360))

    def test_title_words(self):
        for t in ["Backdoor", "One two three four five six"]:
            with self.assertRaises(mc.CoverError):
                mc.check_title(t)
        self.assertEqual(len(mc.check_title("Read the low defender")), 4)


if __name__ == "__main__":
    unittest.main()
