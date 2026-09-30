#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# P6 City life: build round-NN/SPEC_TABLE.md (C4, C6, CH16, CH17, CH19) from the probe logs the capture script wrote (WH_LIFE_* lines).
#   python3 tools/life/spec_table.py docs/night1/life/round-01
import glob, json, os, re, statistics, sys
R = sys.argv[1]
FRAME = re.compile(r't=([\d.]+) res=(\d+)x(\d+).*?vehicles unoccluded >=(\d+)px: moving=(\d+) \(taxi (\d+)\) parked=(\d+) \(taxi (\d+)\) total=(\d+) \| >=(\d+)px: moving=(\d+) parked=(\d+) \(taxi (\d+)\) total=(\d+) \| '
                   r'people unoccluded >=(\d+)px: (\d+) \(models (\d+), identical (?:twins|looks) in frame (\d+)\) \| >=(\d+)px: (\d+) \(models (\d+)\) \| projected only.*?vehicles moving=(\d+) parked=(\d+) people=(\d+)')
def frames(f):
    out = []
    if not os.path.exists(f): return out
    for l in open(f):
        m = FRAME.search(l)
        if m:
            g = m.groups()
            out.append(dict(t=float(g[0]), w=int(g[1]), h=int(g[2]), cpx=int(g[3]), mov=int(g[4]), mtaxi=int(g[5]), par=int(g[6]), ptaxi=int(g[7]), tot=int(g[8]), cpx2=int(g[9]),
                            mov2=int(g[10]), par2=int(g[11]), ptaxi2=int(g[12]), tot2=int(g[13]), ppx=int(g[14]), ppl=int(g[15]), models=int(g[16]), twins=int(g[17]), ppx2=int(g[18]),
                            ppl2=int(g[19]), models2=int(g[20]), pmov=int(g[21]), ppar=int(g[22]), pppl=int(g[23])))
    return out
def med(v): return statistics.median(v) if v else None
def rng(v): return '%s-%s' % (min(v), max(v)) if v else 'n/a'
S = {}
for v in ('S1', 'S2'):
    for tag in ('1080p', '4k'):
        S[(v, tag)] = [f for f in frames(os.path.join(R, 'probe_%s_%s.txt' % (v, tag))) if f['t'] >= 8]
def vals(v, tag, key): return [f[key] for f in S[(v, tag)]]
def fmt(v, tag, key): x = vals(v, tag, key); return '%s (%s)' % (med(x), rng(x)) if x else 'n/a'
def both(v, key): return '4K %s; 1080p %s' % (fmt(v, '4k', key), fmt(v, '1080p', key))
def inr(x, lo, hi): return bool(x) and lo <= med(x) <= hi
def ok(c): return 'MEETS' if c else 'MISSES'
def foot(tag):
    fl = os.path.join(R, 'probe_S1_%s.txt' % tag)
    if os.path.exists(fl):
        for l in open(fl):
            if 'WH_LIFE_FOOT walkers=' in l: return l.strip()
    return 'n/a'
fj = os.path.join(R, 'feet_analysis.json')
gait = json.load(open(fj))['gait'] if os.path.exists(fj) else None
c4k, c4k2 = vals('S1', '4k', 'tot'), vals('S1', '4k', 'tot2')
out = []
out.append('# P6 City life round 01: spec table\n')
out.append('> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.\n')
out.append('Counts come from the engine itself (`WHLifeProbe`, log lines `WH_LIFE_FRAME`): every vehicle / person whose centre projects into the frame, is at least N pixels tall and is reached by a visibility ray from the camera (city geometry blocks it; other vehicles and people do not). No YOLO model is installed on this machine, so these are NOT detector counts: the spec numbers were measured with YOLO on the reference, which misses small and partly hidden objects, so compare with the LARGER size threshold (>= 44 px vehicles / >= 56 px people) as well as the small one. Median (min-max) over the reports at game t = 8, 14, 20, 28 s of each run; "twins/looks" = people in frame that share model AND outfit with another person in frame. Verdicts use the 4K runs.\n')
out.append('| id | target (SPEC) | measured (this build) | verdict |\n|---|---|---|---|')
out.append('| C4 cars, S1 street frame | 5-19 (median ~11) | vehicles moving + parked, >= 22 px: %s; >= 44 px: %s | %s at >= 44 px (>= 22 px counts small far cars: %s) |' % (both('S1', 'tot'), both('S1', 'tot2'), ok(inr(c4k2, 5, 19)), 'in range' if inr(c4k, 5, 19) else 'above the range'))
out.append('| C4 people, S1 street frame | 6-32 (median ~24) | people >= 28 px: %s; >= 56 px: %s | %s (median below the ~24 of the reference) |' % (both('S1', 'ppl'), both('S1', 'ppl2'), ok(inr(vals('S1', '4k', 'ppl'), 6, 32))))
out.append('| C4 traffic lights >= 1 | >= 1 | P1 street-kit signal heads are in the S1 frame (stills); they are P1 props and are NOT driven by the life signal clock | present, not driven |')
out.append('| S1 parked cars incl. taxis | >= 5 parked cars incl. taxis | parked in frame >= 22 px: %s; parked taxis: %s | %s |' % (both('S1', 'par'), both('S1', 'ptaxi'), ok(inr(vals('S1', '4k', 'par'), 5, 999) and vals('S1', '4k', 'ptaxi') and max(vals('S1', '4k', 'ptaxi')) >= 1)))
out.append('| C6 vehicles, S2 avenue from swing height | median 14-22 per frame | vehicles moving + parked, >= 22 px: %s (>= 44 px: none, the avenue is 60-500 m away) | %s |' % (both('S2', 'tot'), ok(inr(vals('S2', '4k', 'tot'), 14, 22))))
out.append('| CH16 people per frame (street level) | 8-25 | S1 people >= 28 px: %s | %s |' % (both('S1', 'ppl'), ok(inr(vals('S1', '4k', 'ppl'), 8, 25))))
out.append('| CH17 >= 6 distinct civilian models in one frame, no identical twins | >= 6 models; 0 twins | S1 looks (model + outfit) in frame: %s; identical looks in frame: %s. 60 looks = 20 citizen meshes x 3 outfits; the mesh alone repeats | %s |' % (both('S1', 'models'), both('S1', 'twins'), ok(vals('S1', '4k', 'models') and min(vals('S1', '4k', 'models')) >= 6 and max(vals('S1', '4k', 'twins')) == 0)))
out.append('| CH17 no gliding / frozen walkers | 0 | planted-stance ankle displacement, S1 4K: `%s`; S1 1080p: `%s` (details below) | see notes |' % (foot('4k').split('| ', 1)[-1], foot('1080p').split('| ', 1)[-1]))
if gait:
    g = gait
    out.append('| CH19 gait phases not in lockstep | pairwise phase difference spread >= 0.2 cycle across >= 6 walkers | %d walkers: max pairwise difference %.3f cycle, mean %.3f, resultant length R %.3f (0 = evenly spread), pairs within 0.05 cycle: %d of %d | %s |' % (
        g['walkers'], g['max_pairwise_diff_cycles'], g['mean_pairwise_diff_cycles'], g['resultant_length_R (0 = evenly spread, 1 = lockstep)'], g['pairs_within_0.05_cycle'], g['pairs'],
        ok(g['walkers'] >= 6 and g['mean_pairwise_diff_cycles'] >= 0.2)))
out.append('')
open(os.path.join(R, 'SPEC_TABLE.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
