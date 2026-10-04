import json, os, sys, re
sys.path.insert(0, '/Users/midir/sm2-n1/city/tools/export')
import cv2, numpy as np
import s4_far_check as S, city_spec_check as C
WT = '/Users/midir/sm2-n1/city/'
R = WT + 'docs/night1/city/round-11/'; P = WT + 'docs/night1/city/round-10/'
cfg = json.load(open(C.REGFILE))
def s4(path):
    r = S.analyse(path, cfg); L = {k: v['value'] for k, v in r['lines'].items()}; t4 = r['T4']
    return dict(T1=min(r['T1_std'].values()), T2=r['box_pct204'], T4a=t4['flat_of_all_pct'], T4b=t4['flat_of_bright_pct'], nb=t4['bright'], nf=t4['flat_bright'], C11=L['C11 lap/sky'], C11f=L['C11 flat8 %'], C12=L['C12 dBR'],
                C13=L['C13 far-sky Y'], C13c=r['C13_critic_box'], C14=L['C14 far-river Y'], C15=L['C15 rms far/near'])
def s8(path):
    im = cv2.imread(path); im = im if im.shape[1] == 1920 else cv2.resize(im, (1920, 1080), interpolation=cv2.INTER_AREA)
    Y = 0.2126 * im[:, :, 2] + 0.7152 * im[:, :, 1] + 0.0722 * im[:, :, 0]; return float((Y[0:300, 1270:1640] > 204).mean() * 100)
a = s4(P + 'S4_perch_skyline_1920x1080.jpg'); b = s4(R + 'S4_perch_skyline_1920x1080.jpg'); c = s4(R + 'S4_perch_skyline_3840x2160.jpg')
ga, gb, gc = s8(P + 'S8_aerial_midtown_1920x1080.jpg'), s8(R + 'S8_aerial_midtown_1920x1080.jpg'), s8(R + 'S8_aerial_midtown_3840x2160.jpg')
def row(name, k, fmt, tgt, extra=None):
    f = lambda d: fmt % d[k]
    return '| %s | %s | %s | %s | %s |' % (name, f(a), f(b), f(c), tgt)
rows = [
 row('T1 S4 silhouette-top std, x 0-1300 (px, min of 3 definitions)', 'T1', '%.1f', '>= 12'),
 row('T2 S4 box (0,150,1300,300) above Y 204 (%)', 'T2', '%.1f', '<= 10'),
 row('T4 flat bright 8x8 blocks in (540,110,900,260), share of ALL blocks (%)', 'T4a', '%.1f', '<= 10'),
 row('T4 same, share of the BRIGHT blocks (%)', 'T4b', '%.1f', '<= 10 (other reading)'),
 row('C11 far_shore lap / sky lap', 'C11', '%.1f', '>= 6'),
 row('C11 far_shore flat 8x8 (%)', 'C11f', '%.1f', '<= 40'),
 row('C12 far_shore (B-R) - sky (B-R)', 'C12', '%+.1f', '+-10'),
 row('C13 far_shore Y - sky Y (committed box)', 'C13', '%+.1f', '-35..-25'),
 row('C13 with the box (0,150,1300,215) the critic used in r10', 'C13c', '%+.1f', '-35..-25'),
 row('C14 far_shore Y - river Y', 'C14', '%+.1f', '5..35'),
 row('C15 rms far_shore / near_city', 'C15', '%.2f', '0.25..0.45'),
 '| T5 S8 glass box (1270,0,1640,300) above Y 204 (%%) | %.1f | %.2f | %.2f | <= 1.5 |' % (ga, gb, gc),
]
bright = '(%d of %d bright blocks are flat in r10; %d of %d in r11 1080p; %d of %d in r11 4K)' % (a['nf'], a['nb'], b['nf'], b['nb'], c['nf'], c['nb'])
table = '\n'.join(rows)
# extra lines from city_spec_check.json / shade_check.json
j10 = json.load(open(P + 'city_spec_check.json')) if os.path.exists(P + 'city_spec_check.json') else {}
print(table); print(bright)
open('/Users/midir/sm2-n1/_scratch/city/r11/table.md', 'w').write(table + '\n')
open('/Users/midir/sm2-n1/_scratch/city/r11/bright.txt', 'w').write(bright + '\n')
