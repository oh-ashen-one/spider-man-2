#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# P6 City life: round-NN/SPEC_TABLE.md from (1) the SPEC DETECTOR numbers (tools/life/detect_counts.py = docs/night1/specs/tools/count_people_vehicles.py settings, YOLO11x-seg,
# conf 0.35, imgsz 1920: detector.json) and (2) the engine probe lines (WH_LIFE_SAMPLE in probe_*.txt: distinct looks, repeated looks, lane motion, queue, box stops).
# The verdict columns compare with the round-02 brief (task) and the SPEC lines (C4, C6, CH16, CH17, CH19). Numbers only; no quality judgement.
#   python3 tools/life/spec_table.py docs/night1/life/round-02
import glob, json, os, re, statistics, sys
R = sys.argv[1]
det = json.load(open(os.path.join(R, 'detector.json'))) if os.path.exists(os.path.join(R, 'detector.json')) else {}
def med(v): return statistics.median(v) if v else None
def rng(v): return '%s-%s' % (min(v), max(v)) if v else 'n/a'
def series(prefix):
    """detector counts of the still series S?_NN_tSSS.jpg of a view (scratch stills), keyed by time"""
    out = []
    for k, d in det.items():
        m = re.match(r'%s_\d+_t(\d+\.\d)\.jpg$' % prefix, k)
        if m and 'people' in d: out.append((float(m.group(1)), d))
    return sorted(out)
def clip(name): return det.get(name, {}).get('summary'), det.get(name, {}).get('rows', [])
def ok(c): return 'MEETS' if c else 'MISSES'
SAMPLE = re.compile(r'WH_LIFE_SAMPLE t=([\d.]+) .*?vehicles unoccluded >=(\d+)px: moving (\d+) \(>1 m/s (\d+), standing (\d+)\) parked (\d+) buses (\d+) \| nearest moving car ([-\d.]+) m \| lanes in view \(projected, >= size\) key:moving/standing([^|]*)\| '
                    r'people >=(\d+)px: (\d+) \(walking (\d+), looks (\d+), citizen meshes (\d+), nearest ([-\d.]+) m; within 60 m (\d+): repeated looks (\d+), within 30 m repeated looks (\d+) / repeated citizen meshes (\d+)\) \| signal av/st (-?\d+)/(-?\d+) \| junction-box stops now (-?\d+) worst (-?\d+)(.*)')
def samples(f):
    out = []
    p = os.path.join(R, f)
    if not os.path.exists(p): return out
    for l in open(p):
        m = SAMPLE.search(l)
        if not m: continue
        g = m.groups()
        lanes = {}
        for t in g[8].split():
            k, v = t.split(':'); mv, st = v.split('/'); lanes[int(k)] = (int(mv), int(st))
        out.append(dict(t=float(g[0]), veh_occ=int(g[2]), mov_fast=int(g[3]), standing=int(g[4]), parked=int(g[5]), buses=int(g[6]), nearest_car=float(g[7]), lanes=lanes,
                        people=int(g[10]), walking=int(g[11]), looks=int(g[12]), meshes=int(g[13]), nearest_p=float(g[14]), within60=int(g[15]), rep60=int(g[16]), rep30=int(g[17]),
                        repmesh30=int(g[18]), sig_av=int(g[19]), sig_st=int(g[20]), box_now=int(g[21]), box_worst=int(g[22]), tail=g[23]))
    return out
out = []
A = out.append
A('# P6 City life round 02: spec table\n')
A('> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.\n')
A('**Detector numbers are from `tools/life/detect_counts.py`**: the same model, classes (person, car, motorcycle, bus, truck), confidence 0.35 and image size 1920 as the spec instrument '
  '`docs/night1/specs/tools/count_people_vehicles.py` (YOLO11x-seg; this round run on the CPU device, the numbers do not depend on the device up to tie-breaks); stills are counted as they are, clips every 0.5 s like the spec tool. Round 01 was measured with the engine probe, which counted tiny distant '
  'figures that the detector does not; the probe is used below only for what the detector cannot see (distinct looks, lane motion, queue, box stops). Reference numbers: SPEC C4 / CH16 / C6.\n')
rows = []
# ---- S1 people / vehicles
s1 = series('S1'); pub = {k: v for k, v in det.items() if k.startswith('S1_street_')}
if s1:
    P = [d['people'] for t, d in s1]; V = [d['vehicles'] for t, d in s1]
    pk = '; '.join('%s: %d people / %d vehicles' % (k.replace('S1_street_', '').replace('.jpg', ''), v['people'], v['vehicles']) for k, v in sorted(pub.items()))
    rows.append(('C4 / CH16 people, S1 street view (still)', '>= 16 median (brief); SPEC 6-32, median ~24; reference sidewalk shot 30', 'detector, 1080p, game t = %s s: %s; **median %g** (min-max %s); published stills: %s' % (
        '/'.join('%g' % t for t, d in s1), ', '.join(str(x) for x in P), med(P), rng(P), pk), ok(med(P) >= 16)))
    rows.append(('C4 cars, S1 street view', '5-19, median ~11', 'detector vehicles (moving + parked + buses): %s; median %g (min-max %s)' % (', '.join(str(x) for x in V), med(V), rng(V)), ok(5 <= med(V) <= 19)))
st, strows = clip('street_clip_1080p60.mp4')
if st:
    rows.append(('CH16 people, street clip (18 s, 0.5 s sampling)', '>= 16 median (brief); SPEC 8-25', 'detector: p10 %g / **median %g** / p90 %g people (>= 3 %% height: median %g); n = %d frames' % (st['people_p10'], st['people_med'], st['people_p90'], st['people_h3_med'], st['n']), ok(st['people_med'] >= 16)))
sw, swrows = clip('swing_clip_1080p60.mp4')
if sw:
    rows.append(('C6 vehicles at swing height (10 s clip, 30 m over the avenue, 25 m/s)', '>= 14 median (brief); SPEC 14-22 (ref swing-avenue-traffic 14, p90 24)', 'detector: p10 %g / **median %g** / p90 %g / max %d vehicles; n = %d' % (sw['veh_p10'], sw['veh_med'], sw['veh_p90'], sw['veh_max'], sw['n']), ok(sw['veh_med'] >= 14)))
s2 = series('S2'); pub2 = {k: v for k, v in det.items() if k.startswith('S2_avenue_')}
if s2:
    V2 = [d['vehicles'] for t, d in s2]
    rows.append(('C6 vehicles, S2 avenue view (still, swing height)', 'median 14-22', 'detector, 1080p, game t = %s s: %s; **median %g** (min-max %s); published stills: %s' % (
        '/'.join('%g' % t for t, d in s2), ', '.join(str(x) for x in V2), med(V2), rng(V2), '; '.join('%s: %d vehicles' % (k.replace('S2_avenue_', '').replace('.jpg', ''), v['vehicles']) for k, v in sorted(pub2.items()))),
        ok(med(V2) >= 14) + ' (still series; the swing clip above is the fuller C6 test)'))
sg, sgrows = clip('signal_clip_1080p60.mp4')
if sg:
    rows.append(('vehicles, signal clip (fixed camera, 10 s)', 'context', 'detector: p10 %g / median %g / p90 %g vehicles; people median %g' % (sg['veh_p10'], sg['veh_med'], sg['veh_p90'], sg['people_med']), ''))
# ---- probe: distinct looks, repeats, nearest
for name, f in (('S1 stills (1080p series + 4K)', None), ('street clip', 'probe_street.txt'), ('signal clip', 'probe_signal.txt')):
    if f is None:
        sm = [x for tag in ('1080p', '4k') for x in samples('probe_S1_%s.txt' % tag) if x['t'] >= 8]
    else:
        sm = [x for x in samples(f) if x['t'] >= 2.5]
    if not sm: continue
    tw = sum(1 for x in sm if x['rep30'] > 0)
    rows.append(('CH17 distinct looks per frame, ' + name, '>= 6 distinct; no repeated head in one frame', 'engine probe (people >= 28 px, unoccluded): looks in frame median %g (min-max %s), of them citizen meshes %g; within 60 m repeated LOOKS median %g (max %d; more than 100 people within 60 m cannot all differ with 100 looks), '
                 '**within 30 m repeated looks: at least one pair in %d of %d samples (max %d pairs)**, repeated citizen meshes within 30 m max %d (100 looks = 20 citizens x 5 outfit / hair / skin / head-cover variants)' % (
        med([x['looks'] for x in sm]), rng([x['looks'] for x in sm]), med([x['meshes'] for x in sm]), med([x['rep60'] for x in sm]), max(x['rep60'] for x in sm), tw, len(sm), max(x['rep30'] for x in sm), max(x['repmesh30'] for x in sm)),
        ('MEETS >= 6 looks; ' + ('NO twin within 30 m' if tw == 0 else 'PARTIAL: a twin pair within 30 m in %d %% of the samples' % round(100 * tw / len(sm))) if min(x['looks'] for x in sm) >= 6 else 'MISSES')))
sm = [x for x in samples('probe_street.txt') if x['t'] >= 2.5]
if sm:
    rows.append(('walkers within ~10 m of the camera, street clip', 'some walkers within ~10 m', 'engine probe: nearest visible walker median %.1f m (min %.1f m); two-way flow by construction (each walker picks its direction 50/50 at spawn)' % (med([x['nearest_p'] for x in sm if x['nearest_p'] > 0]), min([x['nearest_p'] for x in sm if x['nearest_p'] > 0])), ok(min([x['nearest_p'] for x in sm if x['nearest_p'] > 0]) <= 10)))
# ---- swing lanes
sm = [x for x in samples('probe_swing.txt') if x['t'] >= 2.5]
if sm:
    keys = sorted({k for x in sm for k in x['lanes']})
    def moving(k): return sum(1 for x in sm if x['lanes'].get(k, (0, 0))[0] > 0)
    rows.append(('traffic moves in every through-lane (swing clip)', 'C6: moving flow in every through-lane', 'engine probe, samples (of %d) with >= 1 car moving > 1 m/s in view per lane (key = kind*100 + lane*10 + direction 1 N / 2 S; kind 0 = avenue): %s; buses in view (occlusion-tested, >= 22 px) max %d' % (
        len(sm), ', '.join('%d: %d' % (k, moving(k)) for k in keys), max(x['buses'] for x in sm)), ok(all(moving(k) > 0 for k in (1, 2, 11, 12)))))
# ---- signals / queue
sm = [x for x in samples('probe_signal.txt') if x['t'] >= 2.5]
if sm:
    qs = []
    for x in sm:
        m = re.search(r'link 1201 cars (\d+) stopped (\d+) front ([-\d.]+) m', x['tail'])
        if m: qs.append((x['t'], x['sig_av'], int(m.group(1)), int(m.group(2)), float(m.group(3))))
    if qs:
        maxq = max(q[3] for q in qs); red = [q for q in qs if q[1] == 0]; grn = [q for q in qs if q[1] == 2]
        rows.append(('signal queue: >= 3 cars stop at red and pull away on green (fixed camera)', '>= 1 queue of 3+ cars stops at red, pulls away on green; none stops inside the box', 'engine probe, link 1201 (southbound inner lane, stop line 5 m before the street-160 box), 0.5 s samples: cars stopped at the line during red max %d (cars on link %s); after green: stopped %s (front car %s m from the line); avenue signal red at %d of %d samples, green at %d; junction-box stops (car standing < 0.3 m/s with the body in a box > 0.8 s) worst %d' % (
            maxq, '/'.join(str(q[2]) for q in red[:1] + red[-1:]), '/'.join(str(q[3]) for q in grn[:1] + grn[-1:]) if grn else 'n/a', '/'.join('%.1f' % q[4] for q in grn[:1] + grn[-1:]) if grn else 'n/a', len(red), len(qs), len(grn), max(x['box_worst'] for x in sm)),
            ok(maxq >= 3 and grn and max(x['box_worst'] for x in sm) == 0)))
rows.append(('C4 traffic lights >= 1, lit', '>= 1 lit signal head', 'the lens overlay (`AWHLifeTraffic::BuildSignals`, %s lens instances on the P1 masts / posts) lights red / amber / green from the shared 40 s clock; see `signal_clip_1080p60.mp4` and the S1 / S2 stills' % ('246'), 'see stills'))
fj = os.path.join(R, 'feet_analysis.json')
if os.path.exists(fj):
    g = json.load(open(fj))['gait']
    rows.append(('CH19 gait phases not in lockstep', 'pairwise phase difference spread >= 0.2 cycle across >= 6 walkers', '%d walkers: max pairwise difference %.3f cycle, mean %.3f, resultant length R %.3f (0 = evenly spread), pairs within 0.05 cycle: %d of %d' % (
        g['walkers'], g['max_pairwise_diff_cycles'], g['mean_pairwise_diff_cycles'], g['resultant_length_R (0 = evenly spread, 1 = lockstep)'], g['pairs_within_0.05_cycle'], g['pairs']), ok(g['walkers'] >= 6 and g['mean_pairwise_diff_cycles'] >= 0.2)))
A('| id | target | measured | verdict |\n|---|---|---|---|')
for r in rows: A('| %s | %s | %s | %s |' % r)
A('')
open(os.path.join(R, 'SPEC_TABLE.md'), 'w').write('\n'.join(out) + '\n')
print('\n'.join(out))
