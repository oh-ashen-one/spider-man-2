#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""Round 11 ORIGINAL hero suit generator (first-pass piece G).  Evaluates every style of tools/ue_char/suits/suits.json (an override of
tools/ue_char/suit8/design.py DEFAULT_STYLE = Tessera) on the hero UV atlas and writes, per suit,

  art/night1/characters/hero/suits/<id>_basecolor.png   <id>_normal.png (OpenGL)   <id>_orm.png   <id>.json (resolved style + palette stats)

No image generator and no reference image is involved: every texel is a function of the body's rest-pose 3D position (planes, helices, hexagon / arch / rhombus
distance fields), exactly like round 08's Tessera.  Tessera itself (texture_set 'hero') is made by hero_suit_r8.py at 8192 and is only re-evaluated here with --hero.

  python3 tools/ue_char/suits/gen_suits.py [--n 4096] [--only verdant,plum] [--out DIR] [--hero]
"""
import sys, os, json, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
UC = os.path.join(HERE, '..')
sys.path.insert(0, UC); sys.path.insert(0, os.path.join(UC, 'suit8'))
from p2paths import WT  # noqa: E402
import meshio, design  # noqa: E402
import hero_suit_r8 as hs  # noqa: E402

SUITS_JSON = os.path.join(HERE, 'suits.json')


def load_suits():
    d = json.load(open(SUITS_JSON))
    return d


def arg(k, dflt):
    return sys.argv[sys.argv.index(k) + 1] if k in sys.argv else dflt


def write_suit(entry, n, out, pre, log=print):
    """Evaluate one suit at n x n and write the three maps + json."""
    sid = entry['id']
    style = design.resolve(entry.get('style'))
    t0 = time.time()
    r = hs.build(n, log=log, style=style, pre=pre)
    cov = r['cov']
    col8 = (np.clip(r['col'], 0, 1) * 255 + 0.5).astype(np.uint8)
    col8, _ = hs.gutters(col8, cov, max(8, int(24 * n / 8192)))
    hh, _ = hs.gutters(r['h'], cov, 24); mp, _ = hs.gutters(r['mpt'], cov, 24)
    nn = hs.normal_from_height(hh, mp)
    ro, _ = hs.gutters(r['rough'], cov, 24); ao, _ = hs.gutters(r['ao'], cov, 24)
    os.makedirs(out, exist_ok=True)
    hs.save_png(col8, '%s/%s_basecolor.png' % (out, sid))
    hs.save_png(((nn * 0.5 + 0.5) * 255 + 0.5).astype(np.uint8), '%s/%s_normal.png' % (out, sid))
    orm = np.stack([ao, ro, np.zeros_like(ao)], -1)
    hs.save_png((np.clip(orm, 0, 1) * 255 + 0.5).astype(np.uint8), '%s/%s_orm.png' % (out, sid))
    json.dump(dict(id=sid, name=entry.get('name', sid), size=n, coverage=round(float(cov.mean()), 4), style=style, seconds=round(time.time() - t0, 1)),
              open('%s/%s.json' % (out, sid), 'w'), indent=1)
    log('suit %s %d px written (%.0f s)' % (sid, n, time.time() - t0))


def main():
    cfg = load_suits()
    n_def = int(arg('--n', cfg.get('size', 4096)))
    out = arg('--out', WT + '/art/night1/characters/hero/suits')
    only = arg('--only', '').split(',') if arg('--only', '') else None
    cache = {}
    for e in cfg['suits']:
        if only and e['id'] not in only: continue
        if e.get('texture_set') == 'hero' and '--hero' not in sys.argv and not only:
            print('skip %s (made by hero_suit_r8.py; --hero to re-evaluate it here)' % e['id']); continue
        n = n_def if (only is None and e.get('texture_set') != 'hero') or '--n' in sys.argv else int(e.get('size', n_def))
        if n not in cache:
            m = meshio.load_body(); t0 = time.time()
            cache[n] = (m, meshio.raster_tri(m['UV'], m['F'], n)); print('raster %d: %.1fs' % (n, time.time() - t0))
        write_suit(e, n, out, cache[n])


if __name__ == '__main__':
    main()
