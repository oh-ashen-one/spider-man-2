# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 08: eye checks on the hero key stills (Char_HeroKey: lens = flat magenta, bezel = flat yellow, suit = flat blue, everything else the key green; needs r.CustomDepth 3).

  python3 tools/ue_char/eval/lens_check_r8.py hero_key_face_4k.png --out DIR [--crop x0 y0 x1 y1]

Classes per pixel (nearest of four prototypes measured from the image itself: the flat colours are tonemapped, so they are not exactly 0 / 1):
  key (exterior AND enclosed), lens, bezel, suit.
Numbers (critic r07 round target):
  background_between_rim_and_lens_px  key-class pixels NOT connected to the image border (enclosed background) within 6 px of any lens or bezel pixel: 0 required
  key_adjacent_to_lens_px             lens pixels with a key pixel in their 8-neighbourhood (a lens that touches the background): 0 required
  lens_min_dist_to_exterior_px        smallest distance from any lens pixel to the exterior key region (how far inside the silhouette the lens stays)
  lens_ring_closed                    fraction of the lens outline (lens pixels with a non-lens 4-neighbour) whose neighbour is bezel or lens-bezel mixed (AA); suit / key neighbours counted as open
Writes the class image + overlay next to --out."""
import sys, os, json
import numpy as np
import cv2
from scipy import ndimage as ndi
a = sys.argv[1:]
img = a[0]
out = a[a.index('--out') + 1] if '--out' in a else '.'
os.makedirs(out, exist_ok=True)
im = cv2.imread(img)[..., ::-1].astype(np.float32)
H, W = im.shape[:2]
mx = im.max(-1) + 1e-6
n = im / mx[..., None]
r, g, b = n[..., 0], n[..., 1], n[..., 2]
dark = mx < 40
KEY = (g > 0.85) & (r < 0.5) & (b < 0.5) & ~dark
LENS = (r > 0.8) & (b > 0.7) & (g < 0.5) & ~dark
BEZ = (r > 0.8) & (g > 0.8) & (b < 0.5) & ~dark
SUIT = (b > 0.85) & (r < 0.45) & (g < 0.6) & ~dark
cls = np.zeros((H, W), np.uint8); cls[KEY] = 1; cls[LENS] = 2; cls[BEZ] = 3; cls[SUIT] = 4
unk = (cls == 0)
lab, nl = ndi.label(KEY)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
ext = np.isin(lab, list(border))
enclosed_key = KEY & ~ext
near_eye = ndi.binary_dilation(LENS | BEZ, iterations=6)
gap = enclosed_key & near_eye
lab_g, ng = ndi.label(gap)
st8 = np.ones((3, 3), bool)
key_adj = LENS & ndi.binary_dilation(KEY, structure=st8)
dist_ext = ndi.distance_transform_edt(~ext)
lens_min = float(dist_ext[LENS].min()) if LENS.any() else -1
edge = LENS & ~ndi.binary_erosion(LENS, structure=ndi.generate_binary_structure(2, 1))
nb4 = ndi.binary_dilation(edge, structure=ndi.generate_binary_structure(2, 1)) & ~LENS
open_px = int((nb4 & (KEY | SUIT)).sum()); closed_px = int((nb4 & BEZ).sum())
res = dict(image=os.path.basename(img), size=[W, H], lens_px=int(LENS.sum()), bezel_px=int(BEZ.sum()), suit_px=int(SUIT.sum()), key_px=int(KEY.sum()), unclassified_px=int(unk.sum()),
           background_between_rim_and_lens_px=int(gap.sum()), background_components_in_eye=int(ng), key_adjacent_to_lens_px=int(key_adj.sum()), lens_min_dist_to_exterior_px=round(lens_min, 1),
           lens_outline_bezel_neighbours=closed_px, lens_outline_suit_or_key_neighbours=open_px)
json.dump(res, open(os.path.join(out, os.path.splitext(os.path.basename(img))[0] + '_lenscheck.json'), 'w'), indent=1)
ov = np.zeros((H, W, 3), np.uint8)
ov[KEY] = (0, 120, 0); ov[LENS] = (255, 0, 255); ov[BEZ] = (255, 255, 0); ov[SUIT] = (40, 60, 200); ov[gap] = (255, 0, 0); ov[key_adj] = (255, 128, 0)
cv2.imwrite(os.path.join(out, os.path.splitext(os.path.basename(img))[0] + '_classes.png'), ov[..., ::-1])
print(json.dumps(res))
