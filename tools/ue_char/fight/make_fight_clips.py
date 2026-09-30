#!/usr/bin/env python3
"""Round 09: in-place hit-reaction clips for the street enemies (numpy, no Blender, no engine).

Fan homage project; not an official Marvel, Sony or Insomniac game; no affiliation.

The browser game's thug clips carry their travel in the pelvis ('hips' translation x / z): thugStumbleBack ends 0.30 m behind the start,
thugKnockdown 0.53 m, the hero's getUp starts 0.53 m behind where it ends.  Played as they are, the actor stays where it is while the pose
walks away from it, and every hand-over to the guard idle snaps the pelvis back (a shuffling slide).  This tool writes the same clips
IN PLACE: the pelvis x / z is held at the guard value (0, -0.025 m) and the travel goes into clip_motion.json, which the choreography
(tools/ue_char/fight/choreo.py) turns into the actor's path, so the world-space motion is exactly the original clip's and the pose returns to
the guard without a pop.  Only the pelvis translation changes; every rotation, the pelvis height and every other bone are copied.

  python3 tools/ue_char/fight/make_fight_clips.py [--out <dir>]      (reads public/assets/thug.glb + spiderman.glb and $P2_SCRATCH/ueimport/SK_Thug.glb)
  writes  $P2_SCRATCH/ueimport/SK_Street_Fight.glb   (mesh of SK_Thug + the 5 clips below; the build imports the clips and deletes the mesh)
          tools/ue_char/fight/clip_motion.json        (per clip: duration, per-key hips travel relative to the clip start, m)
Clips: hitBack (thugStumbleBack), hitLeft (thugStumbleLeft), hitRight (thugStumbleRight), down (thugKnockdown), getUp (hero getUp).
"""
import os, sys, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, os.path.join(HERE, '..', 'heroanim'))
from p2paths import WT, SCRATCH  # noqa: E402
from ganim import Doc  # noqa: E402

GUARD_XZ = np.array([0.0, -0.025])       # pelvis x / z of the guard idle (thugIdle): every in-place clip holds it
SRC = [  # (new name, source file, source clip)
    ('hitBack', 'thug', 'thugStumbleBack'), ('hitLeft', 'thug', 'thugStumbleLeft'), ('hitRight', 'thug', 'thugStumbleRight'),
    ('down', 'thug', 'thugKnockdown'), ('getUp', 'hero', 'getUp')]


def main(out_dir=None):
    thug_src = Doc(os.path.join(WT, 'public/assets/thug.glb'))
    hero_src = Doc(os.path.join(WT, 'public/assets/spiderman.glb'))
    base = Doc(os.path.join(SCRATCH, 'ueimport', 'SK_Thug.glb'))      # stripped thug mesh + skeleton (prep_glbs.py)
    hips_base = base.idx['hips']
    by_name = {nm: i for i, nm in enumerate(base.names)}
    base.j['animations'] = []
    motion = {}
    for name, which, clip in SRC:
        d = thug_src if which == 'thug' else hero_src
        tr = d.tracks(clip)
        T = d.duration(clip)
        chans, samps = [], []
        times = None
        for node, chs in tr.items():
            nm = d.names[node]
            if nm not in by_name:
                continue
            for path, (t_, v_, interp) in chs.items():
                v = np.array(v_, float)
                if node == d.idx['hips'] and path == 'translation':
                    hips_t = t_.copy(); hips_raw = v.copy()
                    v = v.copy(); v[:, 0] = GUARD_XZ[0]; v[:, 2] = GUARD_XZ[1]
                ti = base._append(np.asarray(t_, np.float32).reshape(-1, 1), 'SCALAR')
                oi = base._append(v, {'translation': 'VEC3', 'rotation': 'VEC4', 'scale': 'VEC3'}[path])
                samps.append({'input': ti, 'output': oi, 'interpolation': 'LINEAR'})
                chans.append({'sampler': len(samps) - 1, 'target': {'node': by_name[nm], 'path': path}})
        base.j['animations'].append({'name': name, 'channels': chans, 'samplers': samps})
        rel = hips_raw[:, [0, 2]] - hips_raw[0, [0, 2]]          # travel relative to the clip start (m): x = the actor's LEFT, z = forward
        motion[name] = {'source': '%s:%s' % (which, clip), 'duration': float(T), 'times': [round(float(x), 5) for x in hips_t],
                        'dx_left': [round(float(x), 5) for x in rel[:, 0]], 'dz_fwd': [round(float(x), 5) for x in rel[:, 1]],
                        'hips_y': [round(float(x), 5) for x in hips_raw[:, 1]]}
        print('%-9s %-18s T=%.2f  K=%d  travel left %+.3f m, forward %+.3f m, hips y %.2f..%.2f' %
              (name, which + ':' + clip, T, len(hips_t), rel[-1, 0], rel[-1, 1], hips_raw[:, 1].min(), hips_raw[:, 1].max()))
    out = os.path.join(out_dir or os.path.join(SCRATCH, 'ueimport'), 'SK_Street_Fight.glb')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    base.write(out)
    json.dump(motion, open(os.path.join(HERE, 'clip_motion.json'), 'w'), indent=1)
    print('wrote', out, os.path.getsize(out) // 1024, 'KB and clip_motion.json')


if __name__ == '__main__':
    a = sys.argv[1:]
    main(a[a.index('--out') + 1] if '--out' in a else None)
