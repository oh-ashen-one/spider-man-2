#!/bin/zsh
# GPU-slot governor for the Night-1 loop. Every 15 s: log GPU %, Unreal count, WindowServer CPU, free RAM, slots.
# 2026-10-01 02:02 WindowServer watchdog reset with only TWO 1080p -game renders: GPU sat at 100 % for ~2 min,
# then WindowServer CPU collapsed to ~1 % (main thread blocked in a Metal submit inside the AGX driver), 40 s later
# launchd killed it and the desktop session (and the orchestrator's terminal) died. Low WS CPU under a pinned GPU is
# STARVATION, not calm. Rules now:
#  - slots never auto-rise above 1 (owner may raise by hand).
#  - GPU >= 98 % for 6 consecutive samples (~90 s) with 2+ engines up: PAUSE launches (create PAUSED) and stop the
#    newest loop '-game' capture (SIGTERM, wait 60 s, SIGKILL only as a last resort).
#  - WindowServer starved = GPU >= 98 % AND ws_cpu <= 5 AND an 8x8 screencapture probe cannot finish in 6 s, twice in a
#    row (a single 4K perf engine pins the GPU legitimately; WS stays responsive then), or ws_cpu >= 70 twice: same, now.
G=/Users/midir/sm2-n1/_scratch/gpu; LOG=$G/health.log; S=$G/slots; P=$G/PAUSED
MAXSLOTS=2   # 2026-10-03 12:4x Devin (owner delegated 3-vs-2): 08:02 probe FAIL with 3 renders (GPU 100 %, WS 5 %) + 12:27 WS-HOT stops while the owner is active -> 2. Was 3 since 2026-10-02 20:35. Was 4 since 2026-10-02 11:50 owner: "max this out, don't crash" + capture renders at darwin background priority (gpu_slot taskpolicy -b); owner 2026-10-01 23:15: "do as much as you can without it crashing, if that's 2 or 3 go ahead" -> 2 with frame-capped captures
[ -f $G/DEMOTED ] && MAXSLOTS=2   # any starvation / pinned / WS-hot stop with 2 renders demotes to 1 for the rest of the session
pinned=0; starve=0; emerg=0; strain=0; swarn=0; calm=0
stop_newest() {  # $1 = reason
  echo "$(date +%H:%M) auto-pause by health_monitor: $1" > $P
  [ "$ue" -ge 2 ] && { echo "$(date +%H:%M) demoted to 2 slots: $1" > $G/DEMOTED; echo 2 > $S; note="$note DEMOTED->2"; }
  local newest=$(pgrep -nf "sm2-n1/.*WebHomage.uproject.* -game")
  [ -z "$newest" ] && return
  kill -TERM $newest 2>/dev/null
  ( for i in {1..60}; do kill -0 $newest 2>/dev/null || exit 0; sleep 1; done; kill -KILL $newest 2>/dev/null ) &
  note="$note STOP(TERM) newest -game pid=$newest"
}
while true; do
  slots=$(cat $S 2>/dev/null || echo 1)
  MAXNOW=$MAXSLOTS; [ -f $G/DEMOTED ] && MAXNOW=2
  [ "$slots" -gt $MAXNOW ] && { echo $MAXNOW > $S; slots=$MAXNOW; }
  u=$(ioreg -r -d 1 -c IOAccelerator | grep -o '"Device Utilization %"=[0-9]*' | head -1 | cut -d= -f2)
  ue=$(ps -Ao command | grep -E "MacOS/UnrealEditor( |$)" | grep -v grep | grep -vE -- "-nullrhi|-run=" | wc -l | tr -d " ")
  bl=$(pgrep -f "Blender.app/Contents/MacOS/Blender" | wc -l | tr -d ' ')
  ws=$(ps -Ao %cpu,comm | awk '/WindowServer/{print int($1); exit}')
  fr=$(vm_stat | awk '/Pages free/{gsub(/\./,"",$3); printf "%.0f", $3*16384/1e9}')
  note=""
  if [ "${u:-0}" -ge 98 ] && [ "$ue" -ge 2 ]; then pinned=$((pinned+1)); else pinned=0; fi
  # 2026-10-01 14:26: GTA alone (GPU 91-95 %, WindowServer 0-3 %) froze the desktop -> warn the orchestrator (who notifies the owner)
  if [ "${u:-0}" -ge 88 ] && [ "${ws:-99}" -le 3 ]; then swarn=$((swarn+1)); else swarn=0; fi
  [ ${swarn:-0} -ge 2 ] && note="$note WS-STARVE-WARN(gpu ${u}% ws ${ws}%)"
  probe=ok
  if [ "${u:-0}" -ge 98 ] && [ "${ws:-99}" -le 5 ]; then
    perl -e 'alarm 6; exec @ARGV' /usr/sbin/screencapture -x -t jpg -R0,0,8,8 $G/.probe.jpg 2>/dev/null && [ -s $G/.probe.jpg ] || probe=FAIL
    rm -f $G/.probe.jpg
  fi
  if [ $probe = FAIL ]; then starve=$((starve+1)); note="$note probe=FAIL"; else starve=0; fi
  if [ "${ws:-0}" -ge 70 ]; then emerg=$((emerg+1)); else emerg=0; fi
  if [ $starve -ge 2 ]; then stop_newest "WindowServer starved (gpu ${u}% ws_cpu ${ws})"; note="$note WS-STARVED"; starve=0; pinned=0
  elif [ $emerg -ge 2 ]; then stop_newest "WindowServer CPU ${ws}%"; note="$note WS-HOT"; emerg=0
  elif [ $pinned -ge 6 ]; then stop_newest "GPU pinned >=98% for 90 s with $ue engine(s)"; note="$note GPU-PINNED"; pinned=0
  fi
  # 2026-10-02 11:33: WindowServer CPU 40-50 % is normal with the owner using the desktop; HIGH WS CPU is not a strain signal
  # (starvation = LOW WS CPU, handled by the probe tripwire). Strain = more engines than slots only.
  if [ "$ue" -gt $((slots+1)) ]; then strain=$((strain+1)); else strain=0; fi
  if [ $strain -ge 2 ]; then echo 1 > $S; note="$note STRAIN slots->1"; strain=0; calm=0; fi
  # strain is a soft drop: after 20 calm min (ws_cpu < 35, no strain) return to the allowed max unless DEMOTED (the hard tripwire)
  if [ "${ws:-99}" -lt 35 ] && [ $strain -eq 0 ]; then calm=$((calm+15)); else calm=0; fi
  if [ $calm -ge 1200 ] && [ ! -f $G/DEMOTED ] && [ "$(cat $S)" -lt $MAXSLOTS ]; then echo $MAXSLOTS > $S; note="$note CALM20->slots $MAXSLOTS"; calm=0; fi
  # auto-lift (2026-10-01 22:40: a starvation pause at 20:43 stalled the loop 2 h): a PAUSED written by THIS monitor lifts after 10 calm
  # minutes with no loop -game render; a 3rd auto-pause inside 2 h stays paused for the orchestrator.
  if [ -f $P ] && grep -q "auto-pause by health_monitor" $P; then
    now=$(date +%s); pt=$(stat -f %m $P)
    trips=$(ls $G/PAUSED.autolift-* 2>/dev/null | while read f; do [ $(( now - $(stat -f %m $f) )) -lt 7200 ] && echo x; done | wc -l | tr -d ' ')
    need=600; [ "${trips:-0}" -ge 2 ] && need=3600   # repeated trips: longer cool-down instead of an indefinite stall
    if [ $(( now - pt )) -ge $need ] && [ "$ue" -eq 0 ] && [ "${u:-100}" -lt 50 ]; then
      mv $P $G/PAUSED.autolift-$(date +%H%M%S); note="$note AUTO-LIFT(after 10 min calm)"
    fi
  fi
  echo "$(date +%H:%M:%S) gpu=${u}% ue=$ue blender=$bl ws_cpu=$ws free_gb=$fr slots=$(cat $S)$note" >> $LOG
  sleep 15
done
