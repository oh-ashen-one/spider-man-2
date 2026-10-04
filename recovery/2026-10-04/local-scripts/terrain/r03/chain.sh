#!/bin/bash
# wait for the terrain build (run_build.sh writes build.rc at the end), then build the r02 copy, then release the chain sentinel
S=/Users/midir/sm2-n1/_scratch/terrain
until [ -e $S/build.rc ] && [ ! -e $S/BUILDING ]; do sleep 10; done
echo "terrain build: $(cat $S/build.rc) $(date)"
if pgrep -f "sm2-n1/terrain/unreal/WebHomage/WebHomage.uproject" >/dev/null; then echo "an engine of this worktree is running: r02 copy skipped"; else
  $S/r03/run_r02copy.sh; fi
rm -f $S/BUILDING_CHAIN; echo "chain done $(date)"
