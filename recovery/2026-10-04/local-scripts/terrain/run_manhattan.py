# terrain piece wrapper around the integrator's build_manhattan.py (not modified): private scratch, own dev port, GPU-locked commandlets,
# pre-staged P2 inputs (cloned from the morning showcase stage).
import os, sys
WT = '/Users/midir/sm2-n1/terrain'
S = '/Users/midir/sm2-n1/_scratch/terrain/manhattan'
os.environ['SM2_MANHATTAN_SCR'] = S
sys.path.insert(0, WT + '/unreal/WebHomage/Scripts'); os.chdir(WT)
import build_manhattan as b
b.SCR = S; b.EXPORT = os.path.join(S, 'export', 'midtown3x3'); b.TEX = os.path.join(S, 'tex'); b.CHAR_STAGE = os.path.join(S, 'chars')
b.DEV_PORT = 5209
b.UE = '/Users/midir/sm2-n1/_scratch/terrain/bin/ue_locked.sh'
b.stage_characters = lambda: b.log('using pre-staged P2 inputs', open(os.path.join(S, 'chars', 'STAGED.json')).read())
sys.argv = ['build_manhattan.py'] + sys.argv[1:]; b.main()
