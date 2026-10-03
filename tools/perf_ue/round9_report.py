#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
"""P4 round 09: writes <round>/TESTS_r09.md (+ TESTS_r09.json) from the round's committed stills.
  1 S4 lines of the round (city tools/export/s4_far_check.py on the 1080p frames of /Game/Maps/Manhattan_View_S4 and the S4 pose of the golden tour on
    /Game/Maps/Manhattan; the round-08 golden preset on the same city ('before'); the city round-11 frame for reference)
  2 golden S1-S8 on /Game/Maps/Manhattan: L1 / L5 (S7) per still, share of pixels below Y 25 (S3 / S7 / S8 against city r10 13.2 / 1.4 / 7.8 %)
  3 fixed midday / night preset maps: look_spec_check.py (L2 / L7, L3 / L8 / L13) next to the merged round-03 numbers
  4 time of day (round-08 table, round-09 city): tod_tests.py (golden 18.4 L1 / night 22 L3 / L8 / L13 / L22), twilight_check.py (L25a moon), dome_check.py (L27)
usage: round9_report.py --round docs/night1/look/round-09"""
import argparse, glob, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); WT = os.path.abspath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, os.path.join(HERE, 'sweeps', 'r09'))
import quick_s4, quick_all   # noqa: E402

def run(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=WT)
    return r.stdout + (('\n' + r.stderr[-400:]) if r.returncode else '')

def yn(b): return 'pass' if b else 'FAIL'

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--round', required=True); a = ap.parse_args(); R = os.path.abspath(a.round); S = R + '/stills'
    LOOK = os.path.dirname(R); CITY = os.path.join(os.path.dirname(LOOK), 'city')
    out = {}
    L = ['# Round 09: S4 golden sky / aerial perspective numbers', '', '> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.', '',
         'All frames from the real game (`Scripts/run_game.sh -game`, offscreen, inside `gpu_slot.sh capture`), 1920x1080 output, internal 1920x1080 (`r.ScreenPercentage 100`, TSR as anti-aliasing only). '
         'Measured on the lossless PNG of each frame where it is kept (`diag/png/`), else on the committed JPEG (q90); JPEG numbers are listed too. Instruments: `tools/export/s4_far_check.py` (city), '
         '`tools/perf_ue/sweeps/r09/quick_s4.py` / `quick_all.py` (wrappers), `look_spec_check.py`, `tod_tests.py`, `twilight_check.py`, `dome_check.py`.', '']
    # ---- 1 S4
    frames = [('Manhattan_View_S4 session 1 t=38 s (round frame)', R + '/diag/png/view_s4_1_t038.png'), 
                            ('golden tour S4 on /Game/Maps/Manhattan', R + '/diag/png/tour_S4.png'),
              ('Manhattan_View_S4 JPEG (committed still)', S + '/golden_S4_1920x1080_manhattan_view.jpg'), ('golden tour S4 JPEG (committed still)', S + '/golden_S4_1920x1080_manhattan.jpg'),
              ('BEFORE: round-08 golden preset, same city build (sweep 15 base, tour S4)', R + '/diag/png/before_tour_S4.png'),
              ('city round-11 frame (city test map + city S4 lighting; reference)', CITY + '/round-11/S4_perch_skyline_1920x1080.jpg')]
    frames = [(n, p) for n, p in frames if os.path.exists(p)]
    rows = quick_s4.rows([p for _, p in frames])
    L += ['## 1. S4 perch: the round lines (1080p)', '',
          'Targets: sky (0,0,1650,80) mean Y <= 205; far band 25-32 Y under the sky on BOTH (450,192,1350,236) and (0,150,1300,215); T2 <= 10 % of (0,150,1300,300) above Y 204; '
          'T4 <= 10 % of the bright 8x8 blocks of (540,110,900,260) flat (and <= 10 % of all blocks); C12 far - sky B-R within +-10; T1 silhouette-top std >= 12 px '
          '(three definitions of s4_far_check.py: A first Y < 215, B first |dY| > 4, C first Y < column sky - 12); C11 far / sky Laplacian >= 6 and flat 8x8 <= 40 %; C14 far - river 5..35; C15 rms far / near 0.25..0.45.', '',
          '| frame | sky Y | far - sky | (0,150,1300,215) - sky | T2 % | T4 flat / bright (bright n) | T4 flat / all % | C12 | T1 A / B / C | C11 lap / flat % | C14 | C15 | frame mean | failing |', '|' + '---|' * 14]
    for (n, p), d in zip(frames, rows):
        f = [k for k, v in d['pass'].items() if not v and k != 'T1BC']
        L.append('| %s | %.1f | %.1f | %.1f | %.1f | %.1f (%d) | %.1f | %+.1f | %.1f / %.1f / %.1f | %.1f / %.1f | %.1f | %.2f | %.1f | %s |' % (
            n, d['sky'], d['far_m_sky'], d['crit_m_sky'], d['T2'], d['T4b'], d['nbright'], d['T4a'], d['C12'], d['T1A'], d['T1B'], d['T1C'], d['C11'], d['C11f'], d['C14'], d['C15'], d['mean'], ', '.join(f) or 'none'))
    out['S4'] = [dict(frame=n, **d) for (n, _), d in zip(frames, rows)]
    L += ['', 'T1 definition A is 0 on every frame whose sky is below Y 215 (the first row of every column is already "below 215"); the round asks for sky <= 205, so A cannot pass together with the sky line.', '']
    # ---- 2 golden S1-S8
    L += ['## 2. Golden preset S1-S8 on /Game/Maps/Manhattan (L1 61..100 mean, Y<10 <= 8 %, clipped <= 1.8 %, B-R -55..-20; S7 L5 59..118 / 8.8 % / 0.7 %)', '']
    sets = [('round 09 (final)', S, 'golden_S?_1920x1080_manhattan.jpg'), ('before (round-08 golden preset, same city)', S, 'before_golden_S?_1920x1080.jpg'),
            ('merged look round 03 (round-03 city)', LOOK + '/round-03/stills', 'golden_S?_1920x1080.jpg')]
    L += ['| set | L1 / L5 pass | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | Y<25 S3 / S7 / S8 % |', '|' + '---|' * 11]
    out['golden'] = {}
    for name, d, pat in sets:
        fs = sorted(glob.glob(os.path.join(d, pat)))
        if not fs: continue
        r = {}
        for f in fs:
            s = 'S' + os.path.basename(f).split('_S')[1][0]
            st = quick_all.stats(f); sp = quick_all.SPEC_S7 if s == 'S7' else quick_all.SPEC
            st['pass'] = bool(sp[1] <= st['mean'] <= sp[2] and st['nb10'] <= sp[3] and st['clip'] <= sp[4] and sp[5] <= st['BR'] <= sp[6]); r[s] = st
        out['golden'][name] = r
        cell = lambda x: '%.0f / %.1f / %.2f / %+.0f%s' % (x['mean'], x['nb10'], x['clip'], x['BR'], '' if x['pass'] else ' x')
        L.append('| %s | %d / %d | %s | %s |' % (name, sum(x['pass'] for x in r.values()), len(r), ' | '.join(cell(r[s]) if s in r else '-' for s in ['S%d' % i for i in range(1, 9)]),
                                              ' / '.join('%.1f' % r[s]['nb25'] if s in r else '-' for s in ('S3', 'S7', 'S8'))))
    L += ['', 'Cells: mean / Y<10 % / clipped % / B-R (x = outside the band). City round-10 Y<25 limits of the round: S3 13.2, S7 1.4, S8 7.8 %.', '']
    # ---- 3 fixed midday / night
    L += ['## 3. Fixed midday / night preset maps (round-03 floors)', '']
    tmp = os.path.join(R, 'diag', 'fixed_spec.md')
    run([os.path.join(HERE, 'look_spec_check.py'), *sorted(glob.glob(S + '/midday_S?_1920x1080.jpg') + glob.glob(S + '/night_S?_1920x1080.jpg')), '--md', tmp, '--json', tmp[:-3] + '.json'])
    if os.path.exists(tmp): L += [open(tmp).read(), '']
    # ---- 4 time of day
    L += ['## 4. Time of day (round-08 key table, unchanged; round-09 city)', '']
    tt = os.path.join(R, 'TESTS_tod')
    if glob.glob(S + '/tod_*'):
        run([os.path.join(HERE, 'tod_tests.py'), '--dir', S, '--out', tt])
        if os.path.exists(tt + '.md'): L += ['See `TESTS_tod.md` (tod_tests.py). Summary:', ''] + [l for l in open(tt + '.md').read().splitlines() if l.startswith('|')][:12] + ['']
        tw = run([os.path.join(HERE, 'twilight_check.py'), '--dir', S, '--out', os.path.join(R, 'TWILIGHT_r09')])
        if os.path.exists(os.path.join(R, 'TWILIGHT_r09.md')): L += ['L25 / L24 / L26: `TWILIGHT_r09.md`.', '']
        run([os.path.join(HERE, 'dome_check.py'), '--dir', S, '--out', os.path.join(R, 'DOME_r09')])
        if os.path.exists(os.path.join(R, 'DOME_r09.md')): L += ['L27: `DOME_r09.md`:', ''] + open(os.path.join(R, 'DOME_r09.md')).read().splitlines()[:40] + ['']
    else:
        L += ['No time-of-day stills in this round folder.', '']
    open(os.path.join(R, 'TESTS_r09.md'), 'w').write('\n'.join(L) + '\n'); json.dump(out, open(os.path.join(R, 'TESTS_r09.json'), 'w'), indent=1)
    print('wrote', os.path.join(R, 'TESTS_r09.md'))

if __name__ == '__main__':
    main()
