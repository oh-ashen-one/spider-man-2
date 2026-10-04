# water piece wrapper around the integrator's build_manhattan.py (not modified): private scratch, GPU-locked commandlets,
# pre-staged P2 inputs (cloned from the morning showcase stage) instead of rsyncing a running P2 round.
import os, sys
WT = '/Users/midir/sm2-n1/water'
S = '/Users/midir/sm2-n1/_scratch/water/manhattan'
os.environ['SM2_MANHATTAN_SCR'] = S
sys.path.insert(0, WT + '/unreal/WebHomage/Scripts'); os.chdir(WT)
import build_manhattan as b
b.SCR = S; b.EXPORT = os.path.join(S, 'export', 'midtown3x3'); b.TEX = os.path.join(S, 'tex'); b.CHAR_STAGE = os.path.join(S, 'chars')
b.UE = '/Users/midir/sm2-n1/_scratch/water/bin/ue_locked.sh'
b.stage_characters = lambda: b.log('using pre-staged P2 inputs', open(os.path.join(S, 'chars', 'STAGED.json')).read())
import subprocess, time
def _wait_slot():   # real UnrealEditor processes only (gpu_slot.py waiters carry the editor path in their argv)
    while int(subprocess.run('pgrep -x UnrealEditor | wc -l', shell=True, capture_output=True, text=True).stdout.strip() or 0) >= 3:
        b.log('3+ UnrealEditor processes running, waiting 10 s'); time.sleep(10)
b.wait_slot = _wait_slot
sys.argv = ['build_manhattan.py'] + sys.argv[1:]; b.main()
