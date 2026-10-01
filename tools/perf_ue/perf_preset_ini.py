#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""(P4 round 04) Write the integration's perf preset (piece F, tools/perf_ue2/overrides/<stem>.cvars, default perf60_hwl2 at r.ScreenPercentage 50 = 3840x2160 output /
1920x1080 internal) into THIS worktree's Config/Mac/MacEngine.ini (generated, untracked, never `git add`), same block markers as tools/perf_ue2/build_map.py step perf_preset,
so every P4 launch (game, commandlet) runs the shipped render settings.  usage: perf_preset_ini.py [stem] [sp] | --off"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); WT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(WT, 'tools', 'perf_ue2'))
INI = os.path.join(WT, 'unreal', 'WebHomage', 'Config', 'Mac', 'MacEngine.ini')
BEGIN, END = '; >>> F perf preset (tools/perf_ue2/build_map.py step perf_preset) >>>', '; <<< F perf preset <<<'
def strip(txt):
    if BEGIN in txt:
        a, b = txt.index(BEGIN), txt.index(END) + len(END); txt = txt[:a].rstrip('\n') + '\n' + txt[b:].lstrip('\n')
    return txt.strip('\n')
txt = open(INI).read() if os.path.exists(INI) else ''
if '--off' in sys.argv:
    open(INI, 'w').write(strip(txt) + '\n'); print('preset removed from', INI); sys.exit(0)
stem = sys.argv[1] if len(sys.argv) > 1 else 'perf60_hwl2'; sp = sys.argv[2] if len(sys.argv) > 2 else '50'
from perf_route import read_set
d = dict(read_set(stem)); d['r.ScreenPercentage'] = sp
block = BEGIN + '\n; preset %s at r.ScreenPercentage %s, generated from tools/perf_ue2/overrides/%s.cvars by tools/perf_ue/perf_preset_ini.py (P4)\n[ConsoleVariables]\n' % (stem, sp, stem) + ''.join('%s=%s\n' % kv for kv in sorted(d.items())) + END + '\n'
os.makedirs(os.path.dirname(INI), exist_ok=True)
rest = strip(txt)
open(INI, 'w').write((rest + '\n\n' if rest else '') + block)
print('preset %s (%d cvars) written to %s' % (stem, len(d), INI))
