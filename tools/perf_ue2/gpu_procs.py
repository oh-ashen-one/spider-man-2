#!/usr/bin/env python3
# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
"""Piece F (round 07): per-process GPU time of EVERY process on this Mac, read without sudo from the IOAccelerator user clients
(`ioreg -r -c IOAccelerator -l`: each Metal client carries AppUsage.accumulatedGPUTime in ns and IOUserClientCreator "pid N, name").
The GPU lock only sees Unreal processes; another session's local model (EXO / MLX) can use the GPU invisibly. perf_route.py takes a
snapshot before and after every config and stores the difference in result.json ('other_gpu'); a run is VOID when any process other
than the game itself used the GPU for more than VOID_PCT of the run's wall time (WindowServer: VOID_PCT_WS, it composites the desktop).
usage: gpu_procs.py snap <out.json> | gpu_procs.py diff <a.json> <b.json> [--exclude-pid N] | gpu_procs.py watch <seconds>"""
import json, re, subprocess, sys, time

VOID_PCT = 2.0      # % of wall time on the GPU by any non-game, non-WindowServer process
VOID_PCT_WS = 8.0   # WindowServer


def snap():
    out = subprocess.run(['ioreg', '-r', '-c', 'IOAccelerator', '-l', '-d', '3'], capture_output=True, text=True).stdout
    procs = {}
    for blk in re.split(r'\+-o ', out)[1:]:   # one IORegistry entry per block; keys inside a block are sorted (AppUsage before IOUserClientCreator)
        m = re.search(r'"IOUserClientCreator" = "pid (\d+), ([^"]*)"', blk)
        if not m: continue
        ns = sum(int(x) for x in re.findall(r'"accumulatedGPUTime"=(\d+)', blk))
        p = procs.setdefault(m.group(1), {'name': m.group(2), 'gpu_ns': 0})
        p['gpu_ns'] += ns
    return {'t': time.time(), 'procs': procs}


def diff(a, b, exclude=()):
    dt = b['t'] - a['t']; rows = []
    for pid, p in b['procs'].items():
        if int(pid) in exclude: continue
        d = p['gpu_ns'] - a['procs'].get(pid, {}).get('gpu_ns', 0)
        if d > 0: rows.append({'pid': int(pid), 'name': p['name'], 'gpu_ms': round(d / 1e6, 1), 'pct': round(100.0 * d / 1e9 / dt, 2) if dt > 0 else None})
    rows.sort(key=lambda r: -r['gpu_ms'])
    void = [r for r in rows if r['pct'] is not None and (r['pct'] > (VOID_PCT_WS if r['name'] == 'WindowServer' else VOID_PCT))
            and not r['name'].startswith('UnrealEditor')]
    return {'wall_s': round(dt, 1), 'top': rows[:8], 'void': bool(void), 'void_by': void}


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == 'snap': json.dump(snap(), open(sys.argv[2], 'w')); return
    if len(sys.argv) >= 4 and sys.argv[1] == 'diff':
        ex = [int(sys.argv[i + 1]) for i, x in enumerate(sys.argv) if x == '--exclude-pid']
        print(json.dumps(diff(json.load(open(sys.argv[2])), json.load(open(sys.argv[3])), ex), indent=1)); return
    if len(sys.argv) >= 3 and sys.argv[1] == 'watch':
        a = snap(); time.sleep(float(sys.argv[2])); print(json.dumps(diff(a, snap()), indent=1)); return
    print(__doc__); sys.exit(2)


if __name__ == '__main__':
    main()
