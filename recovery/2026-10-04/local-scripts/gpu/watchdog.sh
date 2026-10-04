#!/bin/zsh
# Orchestrator watchdog: prints one line per NEW danger condition (stdout = events).
last=""; i=0; dead=""; ws_pid0=$(pgrep -x WindowServer | head -1); prev_e=""; seen_dlg="$(pgrep -x UserNotificationCenter | tr '\n' ' ')"
while true; do
  msgs=()
  now_e=$(ps -axo pid=,stat=,comm= | awk '/UnrealEditor\)?$/ && $2 ~ /[EZ]/ {print $1}' | tr '\n' ' ')
  stuck=""; for q in ${=now_e}; do [[ " $prev_e " == *" $q "* ]] && stuck="$stuck $q"; done; prev_e="$now_e"
  [ -n "$stuck" ] && msgs+="STUCK-EXITING UE (>=15 s):$stuck"
  ws=$(ps -axo %cpu=,comm= | awk '/WindowServer$/ {print int($1)}' | head -1)
  [ "${ws:-0}" -ge 60 ] && msgs+="WindowServer CPU ${ws}%"
  n=$(ps -axo command= | grep -E "^/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" | grep -vE -- "-nullrhi|-run=" | wc -l | tr -d ' ')
  s=$(cat /Users/midir/sm2-n1/_scratch/gpu/slots 2>/dev/null || echo 3)
  [ "$n" -gt $((s+2)) ] && msgs+="renderer UE count $n > slots $s + 2"
  g=$(tail -8 /Users/midir/sm2-n1/_scratch/gpu/health.log | awk '{split($2,a,"=");split($3,b,"="); if (a[2]+0>=98 && b[2]+0>=3) c++} END{print c+0}')
  [ "$g" -ge 6 ] && msgs+="GPU pinned >=98% with 3+ engines for ~2 min"
  wsp=$(pgrep -x WindowServer | head -1)
  if [ -n "$ws_pid0" ] && [ "$wsp" != "$ws_pid0" ]; then dead="WINDOWSERVER RESTARTED (pid $ws_pid0 -> ${wsp:-none}) - desktop session likely dead"; else dead=""; fi
  [ -n "$dead" ] && msgs+="$dead"
  dlg=$(pgrep -x UserNotificationCenter | grep -vxF -f <(printf '%s\n' ${=seen_dlg} 0) | tr '\n' ' ')
  [ -n "$dlg" ] && msgs+="SYSTEM DIALOG ON SCREEN: $(echo $dlg | tr '\n' ' ')"
  ld=$(sysctl -n vm.loadavg | awk '{print int($2)}')
  [ "${ld:-0}" -ge 80 ] && msgs+="CPU load5 ${ld} (32 cores)"
  sw=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}')
  [ "${sw:-0}" -ge 4096 ] && msgs+="SWAP ${sw} MB in use"
  pf=$(memory_pressure 2>/dev/null | awk '/free percentage/ {gsub("%","",$NF); print int($NF)}')
  [ -n "$pf" ] && [ "$pf" -le 10 ] && msgs+="MEMORY free ${pf}%"
  cur="${(j:; :)msgs}"
  if [ "$cur" != "$last" ]; then [ -n "$cur" ] && echo "$(date +%H:%M:%S) $cur" || echo "$(date +%H:%M:%S) clear"; last="$cur"; fi
  sleep 15
done
