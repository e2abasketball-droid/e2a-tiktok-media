"""E2A 3D lab — local pose tracking of a reference take (MediaPipe PoseLandmarker heavy, world landmarks 3D).

Runs on the frames extracted (tonemapped) from the owner's MOV; nothing leaves the machine.
Each frame is cropped around the previous detection (square, 2.3x the body height, resized to 640 px) so the
player keeps enough pixels when he runs away from the camera; IMAGE mode per frame (no hidden tracker state).

  python -I tools/blender/pose_track.py --frames DIR --model pose_landmarker_heavy.task --fps 29.97 --out raw.json
Output: {fps, w, h, frames:[{i, t, ok, img:[[x,y,z,vis]*33] (pixels), world:[[x,y,z]*33] (m, hip centred)}]}
"""
import argparse, glob, json, os
import cv2
import numpy as np
import mediapipe as mp

ap = argparse.ArgumentParser()
ap.add_argument('--frames', required=True)
ap.add_argument('--model', required=True)
ap.add_argument('--fps', type=float, default=30000 / 1001)
ap.add_argument('--out', required=True)
ap.add_argument('--first', type=int, default=1)
ap.add_argument('--last', type=int, default=10**9)
a = ap.parse_args()

BaseOptions = mp.tasks.BaseOptions
PL = mp.tasks.vision.PoseLandmarker
opts = mp.tasks.vision.PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=a.model),
                                             running_mode=mp.tasks.vision.RunningMode.IMAGE, num_poses=1,
                                             min_pose_detection_confidence=0.3, min_pose_presence_confidence=0.3)
files = sorted(glob.glob(os.path.join(a.frames, 'f*.jpg')))
out = {'fps': a.fps, 'frames': []}
box = None
with PL.create_from_options(opts) as det:
    for f in files:
        i = int(os.path.basename(f)[1:5])
        if i < a.first or i > a.last:
            continue
        im = cv2.imread(f)
        H, W = im.shape[:2]
        out['w'], out['h'] = W, H
        res = None
        for attempt in (0, 1):
            if box is not None and attempt == 0:
                cx, cy, s = box
                x0, y0 = int(cx - s / 2), int(cy - s / 2)
                crop = np.zeros((int(s), int(s), 3), np.uint8)
                sx0, sy0, sx1, sy1 = max(0, x0), max(0, y0), min(W, x0 + int(s)), min(H, y0 + int(s))
                crop[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = im[sy0:sy1, sx0:sx1]
                crop = cv2.resize(crop, (640, 640), interpolation=cv2.INTER_CUBIC)
                tr = (x0, y0, s / 640)
            else:
                crop, tr = im, (0, 0, 1)
            r = det.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)))
            if r.pose_landmarks:
                res, T = r, tr
                break
        rec = {'i': i, 't': round((i - 1) / a.fps, 4), 'ok': res is not None}
        if res is not None:
            cw = crop.shape[1]
            ch = crop.shape[0]
            img = [[T[0] + l.x * cw * T[2], T[1] + l.y * ch * T[2], l.z * cw * T[2], l.visibility] for l in res.pose_landmarks[0]]
            wl = [[l.x, l.y, l.z] for l in res.pose_world_landmarks[0]]
            rec['img'] = [[round(v, 2) if k < 3 else round(v, 3) for k, v in enumerate(p)] for p in img]
            rec['world'] = [[round(v, 4) for v in p] for p in wl]
            xs = [p[0] for p in img]
            ys = [p[1] for p in img]
            hgt = max(ys) - min(ys)
            box = ((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, max(260, hgt * 1.5))
        else:
            box = None
        out['frames'].append(rec)
        print(i, rec['ok'], end='; ', flush=True)
json.dump(out, open(a.out, 'w'))
print('\nwrote', a.out, sum(r['ok'] for r in out['frames']), '/', len(out['frames']))
