#!/bin/zsh
# Owner rule 2026-09-29: never add an Unreal process while 3+ are already running; wait (poll every 60 s).
# Instances of THIS worktree do not count against the limit of others but count in the total, so call this BEFORE launching.
while [ "$(pgrep -f 'MacOS/UnrealEditor( |$)' | wc -l)" -ge 3 ]; do echo "wait_slot: 3+ Unreal instances running, waiting 60 s"; sleep 60; done
