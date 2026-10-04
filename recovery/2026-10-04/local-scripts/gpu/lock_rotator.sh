#!/bin/zsh
# transition helper (2026-10-02 12:22): waiters launched while the cap was 1 only try capture.0.lock. While fewer renderers run
# than the live cap and the queue is non-empty, swap a held capture.0.lock for a fresh file so the next 1-slot waiter can start.
# The holder keeps its flock on the old inode. Exits when no old-code waiter remains (all queued pids started after 12:22).
G=/Users/midir/sm2-n1/_scratch/gpu; L=$G/locks
while true; do
  cap=$(cat $G/slots); n=$(ps -axo command | grep -E "MacOS/UnrealEditor( |$)" | grep -v grep | grep -c -- "-game")
  q=$(ls $G/queue | wc -l | tr -d ' ')
  old=0; for f in $G/queue/*.json(N); do p=${${f:t:r}##*-}; st=$(ps -o lstart= -p $p 2>/dev/null); [ -n "$st" ] && [ $(date -j -f "%a %b %d %T %Y" "$st" +%s 2>/dev/null || echo 0) -lt 1790958120 ] && old=$((old+1)); done
  [ $old -eq 0 ] && { echo "$(date +%T) no old waiters left, exit"; exit 0; }
  if [ $q -gt 0 ] && [ $n -lt $cap ] && ! python3 -c "import fcntl,sys;f=open('$L/capture.0.lock','a');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)" 2>/dev/null; then
    mv $L/capture.0.lock $L/capture.0.lock.rot-$(date +%H%M%S) && : > $L/capture.0.lock && echo "$(date +%T) rotated capture.0 (renderers $n < cap $cap, queue $q, old waiters $old)"
    sleep 60
  fi
  sleep 15
done
