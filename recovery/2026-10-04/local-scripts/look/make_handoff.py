import json, os, sys
R = '/Users/midir/sm2-n1/look/docs/night1/look/round-03'
body = open('/Users/midir/sm2-n1/_scratch/look/HANDOFF_r3_body.md').read()
have = {p: os.path.exists('%s/swing_%s.mp4' % (R, p)) for p in ('midday', 'golden', 'night')}
parts = []
for p in ('midday', 'golden', 'night'):
    if not have[p]: continue
    h = json.load(open('%s/swing_%s_hero_luma.json' % (R, p)))
    parts.append('%s (%.1f MB): hero pixel-box luma min %.1f / p5 %.1f / mean %.1f (frames below 40: %d of %d)' % (p, os.path.getsize('%s/swing_%s.mp4' % (R, p)) / 1e6, h['bbox_mean_luma_min'], h['bbox_mean_luma_p5'], h['bbox_mean_luma_mean'], h['frames_below_threshold'], h['frames_measured']))
txt = '; '.join(parts) + '. Frame numbers of every clip (mean Y, B-R, near-black, clipped, L18): `round-03/TESTS.md`.'
missing = [p for p in have if not have[p]]
if missing: txt += ' **Not captured this round: %s** (the GPU slot lock refused every launch for over an hour behind two UnrealEditor processes of other agents stuck exiting in the driver, pids 17555 / 17831; nothing was launched around the lock). Run `capture_looks.py --clips --no-stills --no-warmup --presets %s` first thing next round.' % (', '.join(missing), ','.join(missing))
body = body.replace('CLIPS_PLACEHOLDER', txt)
body = body.replace("sky luminance factor .65 / .65 / .85 brought L10 B-R to +10 but reddened S4 past L6 (-58).", "sky luminance factor .65 / .65 / .65 brings L10 B-R to +11.8 but reddens S4 to -58 (past L6 -55); .65 / .70 / .85 gives +10.3 but S3 B-R -16.")
open('/Users/midir/sm2-n1/look/docs/night1/look/HANDOFF.md', 'w').write(body)
print('handoff written; clips:', have)
