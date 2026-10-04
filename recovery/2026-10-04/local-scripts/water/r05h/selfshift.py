"""Gate-2 proxy from ONE still: XOR/OR of the edge-aligned band mask (Y >= 180, 60 px window at 4K scale) between rows y and y + k. The dolly slides the
foam along the wall by tens of pixels between 4 fps samples; a solid band does not change under that slide (low), lace does (high).
usage: selfshift.py <frame.png> [k rows at 1080p, default 16]   (edge line from scratch r05g/crop_foam.jpg)"""
import sys, os, numpy as np, cv2
sys.path.insert(0, '/Users/midir/sm2-n1/water/tools/water')
import water_spec as ws
REF = os.environ.get('FOAM_REF', '/Users/midir/sm2-n1/_scratch/water/r05g/crop_foam.jpg')
A, _ = ws._wall_edge(cv2.imread(REF).astype(np.float32))
def measure(path, k=16):
    fr = cv2.imread(path); s = fr.shape[1] / 3840.0; y0 = int(ws.FOAMCROP[1] * s)
    Y = ws.luma(fr.astype(np.float32))[y0:fr.shape[0]]
    ex = (np.polyval(A, (np.arange(y0, fr.shape[0]) / s) - ws.FOAMCROP[1]) + ws.FOAMCROP[0]) * s
    win = int(60 * s); R = np.zeros((len(ex), win), bool)
    for i, e in enumerate(ex):
        x = int(round(e))
        for u in range(win):
            xx = x - 2 - u
            if 0 <= xx < Y.shape[1]: R[i, u] = Y[i, xx] >= 180
    a, b = R[:-k], R[k:]
    # only rows where either has foam
    u = (a | b).sum(); return round(float((a ^ b).sum() / u), 3) if u else 0.0, int(R.sum())
if __name__ == '__main__':
    k = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    for f in sys.argv[1:2]: print(f, measure(f, k))
