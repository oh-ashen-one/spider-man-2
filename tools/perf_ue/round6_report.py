#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 06: writes <round>/TESTS_r06.md from the final captures of tools/perf_ue/sweeps/r06/final_r06.sh:
  1 L23b   <round>/tod_lapse_S4.json (checks, instrument condition, the biggest jumps)
  2 L24    twilight stills (twilight_check.py on <round>/stills): sky band vs far band, sun-facing B-R, L25 moon / sky high-pass, L26 dawn correlation
  3 golden 18.4 and night 22 spec tables (tod_tests.py: L1 / L5 / L6 / L21 and L3 / L8 / L13 / L14 / L22, S4 <= 100, Y<10 <= 8 %)
  4 clips  hero box numbers (swing_tod_22_hero_luma.json: L15 / L15b) and clip_check.py numbers of the swing clips
usage: round6_report.py --round docs/night1/look/round-06"""
import argparse, glob, json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, '..', '..'))


def run(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=WT)
    return r.stdout + (('\n' + r.stderr[-400:]) if r.returncode else '')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--round', required=True)
    a = ap.parse_args(); R = os.path.abspath(a.round)
    L = ['# Round 06: sky / time-of-day numbers', '', '> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.', '',
         'All numbers from the real game (`Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`); stills 1920x1080 internal 100 % of output; the lapse 1920x1080 at a fixed 1/60 s step. Instruments: `tools/perf_ue/{capture_tod_lapse,twilight_check,tod_tests,night_tests,clip_check}.py`.', '']
    lp = os.path.join(R, 'tod_lapse_S4.json')
    if os.path.exists(lp):
        d = json.load(open(lp)); c = d['checks_L23b']
        L += ['## L23b time-lapse (S4 perch, 04:00 start, 2 h/s, %d frames)' % d['frames'], '', 'Instrument condition: %s.' % d.get('instrument_condition'), '',
              'Render settings while the clock runs fast (wh.ToDLapseCvars): see `live_cmds` / HANDOFF.' , '',
              '| max jump | p99 | median | frames > 3 | frames > 1.5 | 05:00-21:30 max mean | at h | max clipped % | at h | verdict |', '|---|---|---|---|---|---|---|---|---|---|',
              '| %.2f | %.2f | %.2f | %d | %d | %.1f | %.2f | %.2f | %.2f | %s |' % (c['max_jump'], c['p99_jump'], c['median_jump'], c['frames_over_3'], c['frames_over_1.5'], c['window_05_2130']['max_mean_y'],
                                                                                         c['window_05_2130']['hour_of_max_mean'], c['window_05_2130']['max_clipped_pct'], c['window_05_2130']['hour_of_max_clipped'], 'PASS' if c['pass'] else 'FAIL'),
              '', 'Biggest jumps: ' + ', '.join('%.2f h %+.1f (%.0f -> %.0f)' % (j['hour'], j['jump'], j['from'], j['to']) for j in c['biggest_jumps'][:6]), '']
    st = os.path.join(R, 'stills')
    if os.path.isdir(st):
        L += ['## L24 / L25 / L26 sky stills', '', '```', run(['tools/perf_ue/twilight_check.py', '--dir', st, '--out', os.path.join(R, 'TWILIGHT_r06')]).strip(), '```', '']
        L += ['## Golden 18.4 and night 22 spec numbers (tod_tests.py)', '', '```', run(['tools/perf_ue/tod_tests.py', '--dir', st, '--out', os.path.join(R, 'TESTS_tod'), '--map', 'h18.4=golden,h22=night,h7.6=golden,h13=midday,h13w1=midday']).strip(), '```', '',
              'Per-still tables: `TESTS_tod.md`.', '']
    for hp in sorted(glob.glob(os.path.join(R, 'swing_tod_*_hero_luma.json'))):
        h = json.load(open(hp)); keep = ('frames_measured', 'bbox_mean_luma_min', 'bbox_mean_luma_p5', 'bbox_mean_luma_mean', 'bbox_mean_luma_max', 'frames_below_threshold', 'L15b_frames_with_clipped_px', 'L15b_max_clipped_px_in_box')
        L += ['## Hero box (%s)' % os.path.basename(hp), '', '| ' + ' | '.join(keep) + ' |', '|' + '---|' * len(keep), '| ' + ' | '.join(str(h.get(k)) for k in keep) + ' |', '']
    for cp in sorted(glob.glob(os.path.join(R, 'swing_tod_*.mp4'))):
        j = cp[:-4] + '.check.json'
        run(['tools/perf_ue/clip_check.py', cp, '--json', j])
        if os.path.exists(j):
            c = json.load(open(j))
            L += ['## %s' % os.path.basename(cp), '', 'mean Y %.1f (min %.1f max %.1f), B-R mean %+.1f, clipped mean %.2f %%, L18 edge/centre p50 %.2f' % (c['mean_Y']['mean'], c['mean_Y']['min'], c['mean_Y']['max'], c['B_minus_R']['mean'], c['clipped_pct_mean'],
                  c['L18_edge_over_centre_sharpness']['p50']), '']
    open(os.path.join(R, 'TESTS_r06.md'), 'w').write('\n'.join(L) + '\n')
    print('wrote', os.path.join(R, 'TESTS_r06.md'))


if __name__ == '__main__':
    main()
