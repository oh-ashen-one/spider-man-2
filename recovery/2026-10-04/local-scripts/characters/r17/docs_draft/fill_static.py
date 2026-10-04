import sys, os, re
d = '/Users/midir/sm2-n1/characters/docs/night1/characters/round-17'
cap = open(os.path.join(d, 'CAPTURES.md')).read()
src = open('/Users/midir/sm2-n1/_scratch/characters/r17/docs_draft/captures_static.md').read()
src += '''
| hold | when (EDT) | what it gave | used |
|---|---|---|---|
| A (previous session) | 15:40 - 16:20 | build + the first settle-protocol lineup, which never settled (the player pawn and 31 lane walkers moved: 25 min, max hold 2400 s exceeded, crash count 1 from the missing WH_QUIT) | diagnosis only |
| B | 20:42 | E0 (the r16 command, probe) + E1 (settle) which spun on the falling pawn; stopped by me with `stop_ue.sh` ("stopped cleanly") | E0 |
| C | 20:46 - 20:51 (316 s) | lineup, lineup34 (settle), E1 (settle + streaming + convergence dump), E2 (settle + `-NoTextureStreaming`), 0 crashes | E1, E2 |
| mini | 20:56 - 20:59 (170 s) | 8 settled stills of Tessera on `Char_Skins` (the protocol on the stills map and the head-lock shot) | test only |
| **D** | 21:00 - 21:23 (1367 s) | **content build + `enemy_lineup_4k` + `enemy_lineup_34_4k` + all 56 stills** (every one `settle_frames=34`, 0 resets, 0 timeouts, wall 5.5 - 7.2 s each; the first lineup waited 64.6 s for 23 compiling assets after the clean build), 0 crashes | **every still, both lineups, the swatch sheet** |
| **E** | 21:23 - 21:48 (1485 s) | pawn swap movie (`-WHPreload`), orbit movie, 0 crashes (its `lineupx0` step was a `-shots` time list: all shots fired in frames 1 - 3, discarded) | **pawn, orbit** |
| **F** | @@F@@ | crowd tracking movie | **crowd** |
| **H** | @@H@@ | dose-response of the r16 protocol (`-WHShotFrames`) | cause table |

- **4K stills:** output 3840x2160 = internal 3840x2160 (`r.ScreenPercentage 100`), committed as 4K JPEG (q2) for EVERY view (`stills/skin_<suit>_<view>_4k.jpg`, 56 files); every measure ran on the lossless PNG originals (`$P2_SCRATCH/r17/chainD/run/stills`). The lineups are the PNG originals re-encoded to 4K JPEG (q2).
- **Movies:** 1920x1080 output = internal, `-movie` = every frame at a fixed 1/60 s step, H.264 crf 18 - 20 (`swap_pawn_T_key.mp4`, `orbit_all_suits.mp4`, `crowd_tracking.mp4`; sizes in the Files list, all <= 15 MB). The first 0.1 s of camera binding are trimmed as in r14 - r16.
- **Not re-shot this round** (content unchanged except the r17 skin weights; the lock ran movies at 0.5 - 1.4 fps): the stage-hero run / chase clips and the fight clip. The critic pack uses the round-16 / round-15 files for them (`make_pairs_r17.py` falls back); `evidence/fight_unchanged_since_r10.txt` holds.
- GPU load: every hold shared the lock with 2 other holders (cap 3, `contaminated=true`), so **no frame time here is a performance number**.
'''
cap = cap.replace('@@SOURCE@@', src)
open(os.path.join(d, 'CAPTURES.md'), 'w').write(cap)
print('ok')
