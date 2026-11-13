#!/usr/bin/env python3
"""Export the engine's basketball one-shots as files for the editing templates (public/sfx/).
Generated here, so they are owned by E2A: no licence needed. Usage: python3 music/make_sfx.py template/public/sfx"""
import os, subprocess, sys, tempfile
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e2a_music import SR, Kit, reverb, pan2

out = sys.argv[1] if len(sys.argv) > 1 else 'template/public/sfx'
os.makedirs(out, exist_ok=True)
k = Kit(7, 'hype')
sounds = {
    'swish': k.swish, 'squeak': k.squeak, 'bounce': k.bounce, 'bass_hit': k.bass_hit,
    'impact_big': k.impact, 'crowd_cheer': k.crowd(3.0), 'riser_2s': k.riser(2.0), 'reverse_cymbal': k.revcym(1.2),
}
for name, x in sounds.items():
    st = x if x.ndim == 2 else pan2(x, 0.5) / np.sqrt(2)
    st = st + reverb(st, 0.9, seed=5) * 0.15
    st = st / (np.max(np.abs(st)) + 1e-9) * 0.89
    with tempfile.NamedTemporaryFile(suffix='.f32') as f:
        st.T.astype(np.float32).tofile(f.name)
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', f.name,
                        '-c:a', 'libmp3lame', '-b:a', '192k', os.path.join(out, name + '.mp3')], check=True)
    print('wrote', name)
