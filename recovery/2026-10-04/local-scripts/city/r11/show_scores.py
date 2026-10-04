import sys,json,glob
for fn in sys.argv[1:]:
    for l in open(fn):
        t,m,j=l.split(' ',2)
        try: d=json.loads(j)
        except Exception: continue
        print('%-4s %-18s score %5.1f T1 %4.1f T2 %5.2f T4b %5.1f T4a %4.1f far %5.1f river %5.1f C13 %6.1f C14 %5.1f C15 %.3f' % (t,m,d['score'],d['T1'],d['T2_pct'],d['T4_all'],d['T4_bright'],d['far'],d['river'],d['C13'],d['C14'],d['C15']))
