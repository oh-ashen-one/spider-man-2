import json, statistics as st, sys
d = json.load(open(sys.argv[1])); c = d['crowns']
h = [x['hp_sd'] for x in c]; s = [x['mean_hsv_sat'] for x in c]
print(len(h), 'median', st.median(h), '>=9', sum(v >= 9 for v in h), 'min', min(h), 'sat median', st.median(s), 'sat>=0.65', sum(v >= 0.65 for v in s))
print(sorted([(round(x['hp_sd'], 2), x['box_xywh'][:2], x['mean_luma']) for x in c])[:6])
