import sys, os, cv2, numpy as np
sys.path.insert(0,'/Users/midir/sm2-n1/water/tools/water'); sys.path.insert(0,'/Users/midir/sm2-n1/water/tools/water/r05')
import water_spec as ws, selfshift, farshore
D='/Users/midir/sm2-n1/_scratch/water/r05i/stills/'
for f in sorted(os.listdir(D)):
    if not f.endswith('.png'): continue
    p=D+f; im=cv2.imread(p); c=D+f[:-4]+'_crop.jpg'; cv2.imwrite(c, im[1250:2160,1500:2700], [cv2.IMWRITE_JPEG_QUALITY,95])
    g=ws.foam(c); n=ws.near(p); fs=farshore.score(p)
    print(f, 'gate1 px', g['band_px_mean'], 'rows>=12', g['rows_ge12px_pct'], 'Y', g['band_Y_mean'], '| selfshift32', selfshift.measure(p,32), '| hp', n['highpass_sd'], 'meanY', n['mean_Y'], 'bar', fs['bright_bar_pct'])
