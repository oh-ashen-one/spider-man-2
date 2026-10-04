# P3 driver: runs C's build_manhattan.py (unchanged) with a tighter slot wait: counts real UnrealEditor processes
# (pgrep -x; the -f pattern also matched python wrappers), polls every 5 s, still waits while 3+ run (RULES).
import sys, subprocess, time, runpy
sys.argv = ['build_manhattan.py', '--steps', sys.argv[1]]
g = runpy.run_path('/Users/midir/sm2-n1/traversal/unreal/WebHomage/Scripts/build_manhattan.py', run_name='bm')
def wait_slot():
    k = 0
    while True:
        n = len(subprocess.run(['pgrep', '-x', 'UnrealEditor'], capture_output=True, text=True).stdout.split())
        if n < 3: return
        if k % 12 == 0: g['log']('%d Unreal instances running, waiting' % n)
        k += 1; time.sleep(5)
g['wait_slot'] = wait_slot
g['main'].__globals__['wait_slot'] = wait_slot
g['main']()
