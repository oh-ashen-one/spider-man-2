#!/usr/bin/env python3
# rewrites docs/night1/traversal/HANDOFF.md for round 16 (structural edits; texts come from files in _scratch/traversal/r16/h_*.md)
import re, sys, subprocess
H = '/Users/midir/sm2-n1/traversal/docs/night1/traversal/HANDOFF.md'
R = '/Users/midir/sm2-n1/_scratch/traversal/r16/'
s = open(H).read()
def rd(n): return open(R + n).read().rstrip('\n') + '\n'
# 1. header + status
a = s.index('# P3 Traversal + camera')
b = s.index('Owned paths:')
s = s[:a] + rd('h_status.md') + '\n' + s[b:]
# 2. section 3: round 16 bullet before "- Other: terrain boxes"
k = s.index('- Other: terrain boxes are always a floor')
s = s[:k] + rd('h_sec3.md') + s[k:]
# 2b. section 6 state
k = s.index('## 6. Known bugs / open issues\n') + len('## 6. Known bugs / open issues\n')
s = s[:k] + rd('h_sec6.md') + s[k:]
# 3. commands (section 4): replace trickcam / suncam / sky lines
def repl_line(prefix, new):
    global s
    m = re.search(r'^' + re.escape(prefix) + r'.*$', s, re.M)
    assert m, prefix
    s = s[:m.start()] + new + s[m.end():]
repl_line('python3 docs/night1/traversal/trickcam_check.py', 'python3 docs/night1/traversal/trickcam_check.py <telemetry.csv> <label> [--video <mp4>]   # round 16 v2: TRICK_CAMERA_SPEC tests TC-A..TC-K (WIN = program + 0.5 s, HOLD = program rows with flipcam_k >= .9; TC-C on the rendered hero mask, TC-H suit-mask luma from the video, TC2 fallbacks listed); `python3 docs/night1/traversal/tc_table.py <round dir>` = clip x test table')
repl_line('python3 docs/night1/traversal/sky_check.py', 'python3 docs/night1/traversal/sky_check.py <round dir> <clip> ...   # TC-I (round 16): POOLED over the clips, >= 35 % of 10 fps trick samples with ring >= 50 % sky (40 px ring around the hero mask bbox) AND hero h >= .15; (r12-r15: >= 70 % per clip)')
# 4. section 6l -> add 6m before "## 7."
k = s.index('## 7. Critic history')
s = s[:k] + rd('h_6m.md') + '\n' + s[k:]
# 5. critic history rows
old15 = re.search(r'^\| r15 \| not judged yet.*$', s, re.M)
assert old15
s = s[:old15.start()] + rd('h_rows.md').rstrip('\n') + s[old15.end():]
# 6. queue (section 8)
k = s.index('## 8. Queue for the next session')
s = s[:k] + rd('h_queue.md')
open(H, 'w').write(s)
print('HANDOFF rewritten', len(s))
