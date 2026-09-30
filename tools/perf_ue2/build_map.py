#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Piece F: build /Game/Maps/Manhattan in THIS worktree with piece C's UNCHANGED Scripts/build_manhattan.py.
Differences from running build_manhattan.py directly (both are parameters, not code changes):
  * scratch = /Users/midir/sm2-n1/_scratch/perf (env SM2_MANHATTAN_SCR), so nothing of C's scratch is touched;
  * the browser export uses F's own Vite port 5209 (C's 5208 is C's), started from this worktree and stopped afterwards.
usage: python3 tools/perf_ue2/build_map.py [--steps cpp,city_export,city_prep,city,traversal,characters,look,map]   (editor closed)"""
import os, sys, subprocess
SCR = '/Users/midir/sm2-n1/_scratch/perf'
PORT = 5209
os.environ['SM2_MANHATTAN_SCR'] = SCR
HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(WT, 'unreal', 'WebHomage', 'Scripts'))
os.makedirs(os.path.join(SCR, 'logs'), exist_ok=True)
import build_manhattan as bm  # noqa: E402
bm.DEV_PORT = PORT


def _wait_slot():
    """same rule as bm.wait_slot (wait while 3+ Unreal run), but counts only real UnrealEditor processes: bm's
    `pgrep -f MacOS/UnrealEditor( |$)` also matches gpu_slot.py WAITERS (their argv holds the queued UnrealEditor command)"""
    import time
    while True:
        out = subprocess.run(['ps', '-axo', 'comm='], capture_output=True, text=True).stdout.splitlines()
        n = sum(1 for c in out if c.strip().endswith('MacOS/UnrealEditor'))
        if n < 3: return
        bm.log('3+ Unreal instances running (%d), waiting 60 s' % n); time.sleep(60)


bm.wait_slot = _wait_slot
try:
    bm.main()
finally:
    # stop F's own vite (only the process listening on F's port, started from this worktree)
    pids = subprocess.run(['lsof', '-t', '-nP', '-iTCP:%d' % PORT, '-sTCP:LISTEN'], capture_output=True, text=True).stdout.split()
    for p in pids:
        cmd = subprocess.run(['ps', '-o', 'command=', '-p', p], capture_output=True, text=True).stdout
        if 'vite' in cmd: subprocess.run(['kill', p])
