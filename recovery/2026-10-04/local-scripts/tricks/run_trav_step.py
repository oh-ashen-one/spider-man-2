# tricks: run build_manhattan.py's 'traversal' step (flip clips) INSIDE a held gpu_slot capture slot: the lock governs the instance
# count, so build_manhattan's own 3-instance poll is replaced by a no-op (same pattern as traversal's run_rest.py)
import os, runpy, sys
os.environ['SM2_MANHATTAN_SCR'] = '/Users/midir/sm2-n1/_scratch/tricks/manhattan'
sys.argv = ['build_manhattan.py', '--steps', 'traversal']
g = runpy.run_path('/Users/midir/sm2-n1/tricks/unreal/WebHomage/Scripts/build_manhattan.py', run_name='bm')
g['main'].__globals__['wait_slot'] = lambda: None
g['main']()
