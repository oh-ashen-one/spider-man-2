#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# P6 City life: PERF_TABLE.md from the run_game perf JSONs + the gpu_slot.sh perf sidecars in a round directory.
#   python3 tools/life/perf_table.py docs/night1/life/round-01
import json, os, sys
R = sys.argv[1]
def load(n):
    p = os.path.join(R, n)
    return json.load(open(p)) if os.path.exists(p) else None
ROWS = {
 '1920x1080': [('life off (`-WHLifeOff`: no traffic, no crowd), run 1', '1080p_off'),
               ('life ON, ray-tracing visible (first build: `-WHLifeRT`)', '1080p_on'),
               ('life ON (default now: instances invisible to ray tracing)', '1080p_rtoff'),
               ('life ON, no shadows from life actors (`-WHLifeNoShadow`)', '1080p_rtoff_noshadow'),
               ('traffic only (`-WHCrowdOff`)', '1080p_traffic_only'),
               ('crowd only (`-WHTrafficOff`)', '1080p_crowd_only')],
 '3840x2160': [('life off, run 1', '4k_off'), ('life off, run 2 (repeat: run 1 is a slow outlier)', '4k_off2'),
               ('life ON, ray-tracing visible (first build)', '4k_on'), ('life ON (default now)', '4k_rtoff')]}
out = ['# P6 City life round 01: GPU-locked perf (S1 street view, Life_View_S1, game t = 22-52 s)\n',
       '> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.\n',
       'Every run: `gpu_slot.sh perf` (exclusive, waited for GPU < 15 % for 10 s, `contaminated=false`), Mac Studio M3 Ultra, Metal SM6, golden-hour rig, `r.ScreenPercentage 100` (NATIVE internal resolution = output resolution, so 1080p is 1920x1080 internal and 4K is 3840x2160 internal; the project default would render 4K at 67 % / 50 %). '
       'Frame times include everything else in the P1 / P4 scene (Lumen, VSM, ...), which alone is ~21 ms GPU at native 1080p; read the DIFFERENCE between rows. Run-to-run spread is a few ms (the two 4K "life off" runs differ by 9 ms).\n']
for res, rows in ROWS.items():
    out.append('## %s\n' % res)
    out.append('| variant | frames | avg ms | p95 | p99 | GPU avg ms | GPU util before / during avg | valid |\n|---|---|---|---|---|---|---|---|')
    for label, key in rows:
        p = load('perf_%s.json' % key); g = load('perf_gpu_%s.json' % key)
        if not p: out.append('| %s | not run | | | | | | |' % label); continue
        out.append('| %s | %d | %.2f | %.2f | %.2f | %.2f | %s / %s | %s |' % (label, p['frames'], p['avg_ms'], p['p95_ms'], p['p99_ms'], p['gpu_avg_ms'],
                   '%.0f %%' % g['util_before'] if g else 'n/a', '%.0f %%' % g['util_during']['avg'] if g else 'n/a', 'perf_valid' if g and g.get('perf_valid') else 'CONTAMINATED'))
    out.append('')
open(os.path.join(R, 'PERF_TABLE.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
