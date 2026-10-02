# Round 13 SPEC CHECK (piece G, hero skins)

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. Numbers are read from `evidence/` by `tools/ue_char/suits/spec_check_r13.py`;
> the measures of the 4K chest stills run on the lossless PNG originals of the real game (UE 5.8.3 `-game`, offscreen, internal 3840x2160).

## Round target (critic round 12): sculpt the shared mask head

Measured by `tools/ue_char/suits/head_check_r13.py` on the lossless 4K PNG originals of the real game: `head` = 12 deg off the face axis (1.0 m), `head34` = the round-12 head framing (25 deg), `headside` = profile (1.25 m).
H1 nose-bridge luma profile (vertical, midline between the lenses, 11 px smoothing): extrema with prominence >= 20 luma, count >= 3 and swing >= 20. H2 silhouette nose bump >= 2 % of head height (profile still: front-most silhouette column above the line brow point -> chin point). H3 lens width >= 1.6x round 12 (lens px width / head silhouette width at the lens row; PASS = the near lens in the round-12 framing and the mean of both lenses in the 12 deg still; the far lens of a 25 deg view is foreshortened and partly behind the silhouette: reported, not gated). H4 rim: the contiguous band around each lens whose luma differs from the mask by >= 15 (of 255) is >= 6 px wide on >= 90 % of 48 angles. H5 face seam: lit / shadow pair >= 20 luma across the midline cord at 12 heights, no black run >= 12 px. H6 both lenses >= 3 px from the background in the 12 deg view (the lenses wrap the face and lie against its outline).

| suit | H1 extrema / swing (head, head34) | H2 nose bump % of head height | H3 lens / head width (r12 -> r13), ratio | H4 rim px median, closed (head / head34) | H5 seam pair, black run | H6 lens edge distance px | verdict |
|---|---|---|---|---|---|---|---|
| tessera | 4 / 140.7 ; 2 / 140.9 | **8.71** | 0.1888 -> 0.3323; near lens **1.952x**, far lens 1.556x, mean (12 deg still) **1.896x** | 21.5, 0.979 ; 13.8, 0.917 | 67.1, 0 | [270, 18] | PASS |
| verdant | 3 / 97.1 ; 3 / 151.4 | **8.74** | 0.2064 -> 0.3271; near lens **1.916x**, far lens 1.213x, mean (12 deg still) **1.764x** | 19.5, 0.854 ; 15.0, 0.729 | 82.4, 0 | [231, 39] | FAIL H4 |
| plum | 2 / 176.2 ; 5 / 174.4 | **8.64** | 0.2064 -> 0.3383; near lens **1.91x**, far lens 1.386x, mean (12 deg still) **1.754x** | 24.8, 0.979 ; 19.2, 0.896 | 49.0, 0 | [255, 23] | FAIL H4 |
| cinder | 2 / 91.0 ; 1 / 89.5 | **10.82** | 0.1975 -> 0.3373; near lens **1.93x**, far lens 1.519x, mean (12 deg still) **1.853x** | 25.5, 0.938 ; 23.2, 0.979 | 80.3, 0 | [119, 3] | FAIL H1 |
| glacier | 4 / 117.4 ; 5 / 107.7 | **9.44** | 0.2041 -> 0.3172; near lens **1.923x**, far lens 1.081x, mean (12 deg still) **1.791x** | 38.8, 0.938 ; 39.2, 0.938 | 78.3, 0 | [31, 42] | PASS |
| ash | 6 / 174.8 ; 6 / 174.8 | **9.09** | 0.189 -> 0.3334; near lens **1.961x**, far lens 1.561x, mean (12 deg still) **1.885x** | 18.2, 0.729 ; 18.5, 0.792 | 115.6, 0 | [190, 12] | FAIL H4 |
| saffron | 2 / 166.0 ; 2 / 187.7 | **10.72** | 0.2064 -> 0.3231; near lens **1.908x**, far lens 1.175x, mean (12 deg still) **1.748x** | 16.0, 0.729 ; 15.0, 0.792 | 146.9, 0 | [233, 45] | FAIL H1, H4 |
| sage | 5 / 137.7 ; 5 / 132.0 | **9.4** | 0.2072 -> 0.3158; near lens **1.964x**, far lens 1.067x, mean (12 deg still) **1.773x** | 38.0, 0.917 ; 38.8, 0.771 | 101.7, 0 | [221, 42] | FAIL H4 |

2 of 8 suits pass every gate H1 - H6 (`evidence/head_check.json`, overlays in `evidence/measures/head_overlays/`).

## Keep: the round-12 lines (raised piping, nothing under the sash, no fold)

| suit | relief: 64 px cells with a lit / shadow pair >= 20 luma (r12 -> r13) | median cell delta (r12 -> r13) | sash: longest dark run px, target <= 10 (r12 -> r13) | sash verdict |
|---|---|---|---|---|
| tessera | 0.592 -> **0.515** (206 of 400 cells) | 23.4 -> **20.6** | 11 -> **9** | PASS |
| verdant | 0.339 -> **0.367** (88 of 240 cells) | 13.6 -> **13.5** | 8 -> **8** | PASS |
| plum | 0.605 -> **0.579** (194 of 335 cells) | 25.4 -> **25.1** | None -> **9** | PASS |
| cinder | 0.598 -> **0.58** (145 of 250 cells) | 25.6 -> **26.1** | 10 -> **6** | PASS |
| glacier | 0.602 -> **0.636** (175 of 275 cells) | 25.4 -> **29.3** | None -> **None** | n/a |
| ash | 0.575 -> **0.556** (194 of 349 cells) | 25.0 -> **23.4** | 3 -> **4** | PASS |
| saffron | 0.52 -> **0.526** (122 of 232 cells) | 21.8 -> **21.5** | 6 -> **5** | PASS |
| sage | 0.6 -> **0.623** (185 of 297 cells) | 25.7 -> **25.8** | None -> **None** | n/a |

| Verdant chevron edge at the critic's columns x 1320-1400 | target | round 12 | round 13 | verdict |
|---|---|---|---|---|
| largest column-to-column jump beyond its slope | <= 2 px | 1.24 px | **6.25 px** | FAIL |

## Keep-passing lines

| line | target | measured | verdict |
|---|---|---|---|
| CH1 front stills (hero height / frame height, all 8 suits) | 0.48 - 0.62 | 0.542 - 0.544 | PASS |
| IP guard palette P1 - P7 (Verdant / Saffron re-blocked, Plum recoloured) | 0 failures | min palette distance 45.0 over 28 pairs, fails: none | PASS |
| UV seam runs at 4K (texture level) | <= 40 px | worst 4.3 px, runs > 40 px: 0 | PASS |
| OCR of every 4K still | 0 hits | 0 hits over 48 images | PASS |
| Tessera stays the default; generator regression (r8 legacy texel for texel + r13 default) | PASS | REGRESSION PASS | PASS |
| swap on the pixels (playable pawn, real T presses) | <= 500 ms | 7 of 7 presses found, worst 33.3 ms | PASS |

## Hero animation (stage hero, Char_Hero, 1080p60 fixed step) and the playable pawn

| line | target | measured | verdict |
|---|---|---|---|
| CH10 stage-hero blends | >= 0.15 s | the stage clips use the round-08 animation set unchanged (same ABP_Hero_Lineup / ABP_Hero_Leap); `video_checks.py takeoff` reads 1 - 2 frames on BOTH the round-08 and the round-13 leap clips (its ground line is set from the bobbing run, not a usable instrument) | not re-measured |
| playable pawn (P3 `WebTravAnimInstance`, NOT P2) run cadence | (P3) 3.2 - 3.8 | 4.0 steps/s (FFT 4.133 Hz, bob period 15.0 frames) | logged for the traversal brief |
| playable pawn idle -> run start | (P3) blend >= 0.15 s | largest one-frame change of the silhouette: height 0.089, width 0.769 at t = 0.183 s | logged for the traversal brief |
| playable pawn start, from its own telemetry | (P3) | clip switches A_Hero_idle -> A_Hero_walk @0.817 s -> A_Hero_jog @0.867 s -> A_Hero_run @0.983 s, all at blend weight 1.0; the 10-number pose signature then needs 28 frames (0.467 s) for 90 % of its change (largest single frame 5.8 %) | logged for the traversal brief |

## Enemy pack (restored to the round-10 content; round-13 lineup)

| line | measured |
|---|---|
| lineup 4K still, wall / floor mean RGB (round 04 -> round 12 -> round 13) | {'wall': [208.3, 208.7, 212.9], 'floor': [165.2, 182.8, 201.4], 'brick': [165.7, 132.3, 132.0]} -> {'wall': [207.5, 208.1, 212.4], 'floor': [164.7, 183.0, 202.3], 'brick': [163.3, 126.4, 126.3]} -> **{'wall': [140.9, 140.8, 149.0], 'floor': [87.0, 103.8, 128.7], 'brick': [87.8, 65.7, 65.8]}** |
| the skins-stage EV (+10) leaking into Char_Lineup | NO: the r04 and r12 lineups have the same exposure (wall 208 / 207 of 255); the washed-out look is the pale sunlit wall, fixed this round with a -0.6 EV bias and a weaker fill |
| fight script / choreography / weapon fit vs the round-10 commit | IDENTICAL (git diff --stat empty) |

Resolution: stills output 3840x2160, internal 3840x2160 (`r.ScreenPercentage 100`). Movies 1920x1080, fixed 1/60 s step.
