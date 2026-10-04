# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.
# Tricks C r02: the catch-rotation line (tricks_check C) of two captures of the same route side by side, as a markdown table.
#   python3 tools/tricks/catch_table.py <a_telemetry.csv> <a_pose.csv> <b_telemetry.csv> <b_pose.csv> [<label a> <label b>]
# Per trick end: the largest 0.1 s chest rotation rate in the windows from 3 frames before the last trick row to + 0.4 s, the largest
# single-frame rate, what follows the trick (swing = web catch, air = the program ran out), and (b) the catch-lean state at the end.
import csv, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tricks_check as TC  # noqa: E402


def load(tel, pose):
    T = list(csv.DictReader(open(tel)))
    Pz = list(csv.DictReader(open(pose)))
    key = lambda r: (round(TC.f(r['x_m']), 2), round(TC.f(r['y_m']), 2), round(TC.f(r['z_m']), 2))
    PI = {}
    for r in Pz: PI.setdefault(key(r), r)
    J = [PI.get(key(r)) for r in T]
    t = [TC.f(r['t']) for r in T]
    out = []
    for c in TC.instances(T):
        e = c['rows'][-1][0]
        ws = [TC.rot_deg(TC.chest_frame(J[k]), TC.chest_frame(J[k + 6])) / (t[k + 6] - t[k])
              for k in range(e - 3, e + 25) if 0 <= k and k + 6 < len(T) and J[k] and J[k + 6] and t[k + 6] > t[k]]
        pf = [TC.rot_deg(TC.chest_frame(J[k]), TC.chest_frame(J[k + 1])) / (t[k + 1] - t[k])
              for k in range(e - 3, e + 30) if 0 <= k and k + 1 < len(T) and J[k] and J[k + 1] and t[k + 1] > t[k]]
        j = J[e] or {}
        out.append(dict(prog=c['prog'], end=t[e], win=max(ws) if ws else float('nan'), pf=max(pf) if pf else float('nan'),
                        nxt=T[e + 1]['mode'] if e + 1 < len(T) else '', shape=T[e].get('flip_shape', ''),
                        lean=j.get('catch_beta', ''), swing=j.get('catch_swing', ''), rho=j.get('catch_rho', '')))
    return out


def main():
    a = load(sys.argv[1], sys.argv[2]); b = load(sys.argv[3], sys.argv[4])
    la, lb = (sys.argv[5], sys.argv[6]) if len(sys.argv) > 6 else ('a', 'b')
    print('| # | program | end (s) | %s max 0.1 s (deg/s) | %s max 0.1 s (deg/s) | %s max frame | next | %s exit shape | %s predicted (lean pitch / sideways rest, deg) |' % (la, lb, lb, lb, lb))
    print('|---|---|---|---|---|---|---|---|---|')
    for i, (x, y) in enumerate(zip(a, b)):
        pred = ('%s %s / %s' % ('swing' if y['swing'] == '1' else 'air', y['lean'], y['rho'])) if y['lean'] else ''
        print('| %d | %s | %.2f | %.0f | %.0f%s | %.0f | %s | %s | %s |' % (i + 1, y['prog'], y['end'], x['win'], y['win'], ' (pass)' if y['win'] <= TC.CATCH_MAX else '',
                                                                       y['pf'], y['nxt'], y['shape'], pred))
    import statistics
    for lab, L in ((la, a), (lb, b)):
        v = [r['win'] for r in L if r['win'] == r['win']]
        print('\n%s: %d of %d measured trick ends <= %.0f deg/s; median of maxima %.0f, worst %.0f deg/s' % (lab, sum(1 for x in v if x <= TC.CATCH_MAX), len(v), TC.CATCH_MAX, statistics.median(v), max(v)), end='')
    print()


if __name__ == '__main__':
    main()
