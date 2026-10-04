#!/usr/bin/env python3
# fallback: run build_city.py's remaining steps (default proto,kit,fsky,map) through build_manhattan's commandlet runner (F scratch), when the
# one-pass city step was cut by the capture max hold. Steps from argv[1].
import os, sys
WT = '/Users/midir/sm2-n1/perf'
sys.argv = [sys.argv[0]] + sys.argv[1:]
steps = sys.argv[1] if len(sys.argv) > 1 else 'proto,kit,fsky,map'
os.environ['SM2_MANHATTAN_SCR'] = '/Users/midir/sm2-n1/_scratch/perf'
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
import build_manhattan as bm
env = {'SM2_CITY_EXPORT': bm.EXPORT, 'SM2_CITY_TEX': bm.TEX}
bc = os.path.join(bm.HERE, 'build_city.py')
bm.ue_python('city_rest', bm.exec_wrapper(bc, bm.LOAD_SME + 'JOB_ARGS = {"steps": "%s"}' % steps), env)
