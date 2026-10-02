#!/bin/zsh
# P4 r05 follow-up in ONE gpu_slot hold: (1) 24 h lapse with eye adaptation matched to the 2 h/s time compression, (2) 22 h and 19.8 h re-captured with a longer settle
cd /Users/midir/sm2-n1/look
R=docs/night1/look/round-05; S=/Users/midir/sm2-n1/_scratch/look/r05
python3 tools/perf_ue/capture_tod_lapse.py --round $R --shot S4 --from 4.0 --hours 24 --seconds 12 --name tod_lapse_S4_fastadapt --cmds 'exec wh.ToDSet pp.AutoExposureSpeedUp 40;exec wh.ToDSet pp.AutoExposureSpeedDown 40'; echo "lapse2 rc=$?"
python3 tools/perf_ue/capture_tour.py --round $S/settle --tod 22,19.8 --res 1920x1080 --timeout 3000 --work $S/tour_settle --redo --settle 8 --first-settle 14; echo "settle rc=$?"
# (3) diagnostic: is the 20-21 h white wash the dense night fog lit by the sky ambient? (pin applies at every hour: diagnostic only, scratch)
python3 tools/perf_ue/capture_tod_lapse.py --round $S/diag --shot S4 --from 4.0 --hours 24 --seconds 12 --name tod_lapse_S4_noamb --cmds 'exec wh.ToDSet pp.AutoExposureSpeedUp 40;exec wh.ToDSet pp.AutoExposureSpeedDown 40;exec wh.ToDSet fog.SkyAtmosphereAmbientContributionColorScale 0 0 0 1'; echo "diag rc=$?"
