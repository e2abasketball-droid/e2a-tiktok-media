"""E2A 3D lab — reader for the ara3d-data «.pack» files (MakeHuman base mesh, morph targets and proxies, CC0-1.0).

Format (verified 2026-11-18 on ara3d-data 1.1.0): gzip( b'MHP1' + uint32 header length + JSON header + binary arrays ).
Header: {"meta": {...}, "arrays": [{"name","type","offset","length"}]} with typed little-endian arrays.
  base.pack     positions (19158 verts, decimetres, y up), faceVerts/faceUVs (quads), uvs, skin weights (wOff/wBone/wVal,
                bone index into meta.bones), regions (per-vertex group), meta.joints (joint -> vertex list, head/tail)
  targets.pack  meta.targets[name] = [start, count, scale]; arrays idx (uint16, delta-encoded vertex index), x/y/z lo/hi bytes (int16, delta-encoded along idx, * scale)
  proxies/*.pack refs (3 base verts per proxy vertex), weights, offsets, meta.scale ([v1, v2, den] per axis), faces, uvs
Only numpy; no bpy.
"""
import gzip, json, struct
import numpy as np

DT = {'Uint32Array': '<u4', 'Uint16Array': '<u2', 'Uint8Array': 'u1', 'Float32Array': '<f4', 'Int16Array': '<i2'}


def read(path):
    d = gzip.decompress(open(path, 'rb').read())
    assert d[:4] == b'MHP1', path
    n = struct.unpack('<I', d[4:8])[0]
    h = json.loads(d[8:8 + n])
    body = d[8 + n:]
    arr = {}
    for a in h['arrays']:
        dt = np.dtype(DT[a['type']])
        arr[a['name']] = np.frombuffer(body, dt, a['length'], a['offset'])
    return h['meta'], arr


class Targets:
    def __init__(self, path):
        self.meta, a = read(path)
        self.a = a

    def names(self):
        return list(self.meta['targets'])

    def delta(self, name, nverts):
        s, c, sc = self.meta['targets'][name]
        a = self.a
        idx = np.cumsum(a['idx'][s:s + c].astype(np.int64))  # delta-encoded vertex indices
        def comp(lo, hi):
            v = (a[lo][s:s + c].astype(np.int32) | (a[hi][s:s + c].astype(np.int32) << 8)).astype(np.int16)
            return np.cumsum(v.astype(np.int64)).astype(np.float64) * sc  # values are delta-encoded too
        D = np.zeros((nverts, 3))
        D[idx, 0] = comp('xlo', 'xhi'); D[idx, 1] = comp('ylo', 'yhi'); D[idx, 2] = comp('zlo', 'zhi')
        return D


def base(path):
    m, a = read(path)
    P = a['positions'].reshape(-1, 3).astype(np.float64)
    F = a['faceVerts'].reshape(-1, 4).astype(np.int64)
    FU = a['faceUVs'].reshape(-1, 4).astype(np.int64)
    UV = a['uvs'].reshape(-1, 2).astype(np.float64)
    off = a['wOff'].astype(np.int64)
    W = [(a['wBone'][off[i]:off[i + 1]].astype(int), a['wVal'][off[i]:off[i + 1]].astype(float)) for i in range(len(P))]
    return {'meta': m, 'P': P, 'F': F, 'FU': FU, 'UV': UV, 'W': W, 'regions': a['regions'].astype(int)}


def joints(meta, P):
    return {k: P[v].mean(0) for k, v in meta['joints'].items()}


def proxy(path, P):
    """fit a proxy (clothes, hair, body proxy) to the current base positions P (MakeHuman proxy rule)."""
    m, a = read(path)
    n = m['vertexCount']
    refs = a['refs'].reshape(n, 3).astype(np.int64)
    w = a['weights'].reshape(n, 3).astype(np.float64)
    off = a['offsets'].reshape(n, 3).astype(np.float64)
    sc = np.ones(3)
    for ax, (v1, v2, den) in enumerate(m.get('scale') or []):
        sc[ax] = abs(P[v1, ax] - P[v2, ax]) / den
    V = (P[refs] * w[..., None]).sum(1) + off * sc
    sizes = a['faceSizes'].astype(int)
    fv = a['faceVerts'].astype(int)
    fu = a['faceUVs'].astype(int)
    faces, fuv, k = [], [], 0
    for s in sizes:
        faces.append(fv[k:k + s].tolist()); fuv.append(fu[k:k + s].tolist()); k += s
    uv = a['uvs'].reshape(-1, 2).astype(np.float64)
    return {'meta': m, 'V': V, 'faces': faces, 'fuv': fuv, 'uv': uv, 'refs': refs, 'w': w,
            'delete': a.get('deleteVerts', np.zeros(0)).astype(int)}
