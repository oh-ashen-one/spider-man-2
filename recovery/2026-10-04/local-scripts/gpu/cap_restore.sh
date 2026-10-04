#!/bin/zsh
# Restore the loop engine cap to 2 once the owner's GPU apps (Steam / CrossOver / wine) have been gone 15 min.
G=/Users/midir/sm2-n1/_scratch/gpu; quiet=0
while true; do
  if pgrep -f "[s]team_osx|[C]rossOver|[w]ine64|[w]ineserver|steamwebhelper" >/dev/null; then quiet=0; else quiet=$((quiet+60)); fi
  if [ $quiet -ge 900 ]; then
    pkill -f "[h]ealth_monitor.sh"; sleep 1
    sed -i '' 's/\[ \$slots -lt 1 \]/[ $slots -lt 2 ]/' $G/health_monitor.sh; echo 2 > $G/slots
    (cd $G && nohup ./health_monitor.sh >/dev/null 2>&1 &)
    echo "$(date +%H:%M) owner GPU apps gone 15 min — loop cap back to 2"; exit 0
  fi
  sleep 60
done
