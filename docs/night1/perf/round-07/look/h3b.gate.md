[ WARN:0@1.215] global loadsave.cpp:278 findDecoder imread_('/Users/midir/sm2-n1/_scratch/perf/r07/st/h3b/route_t20.png'): can't open/read file: check file path/integrity
[ WARN:0@1.357] global loadsave.cpp:278 findDecoder imread_('/Users/midir/sm2-n1/_scratch/perf/r07/st/h3b/route_t28.png'): can't open/read file: check file path/integrity
[ WARN:0@1.536] global loadsave.cpp:278 findDecoder imread_('/Users/midir/sm2-n1/_scratch/perf/r07/st/h3b/route_t42.png'): can't open/read file: check file path/integrity
look_gate.py (round 07 edition) test=/Users/midir/sm2-n1/_scratch/perf/r07/st/h3b
references: as found = /Users/midir/sm2-n1/_scratch/perf/r03/before ; r06 = /Users/midir/sm2-n1/_scratch/perf/r06/final

| id | still | ref | metric | crop (1920 space) | reference | test | ratio | line | class | result |
|---|---|---|---|---|---|---|---|---|---|---|
| S1_glass_spec | view_S1 | asfound | ssim_min | 485,0,710,490 | - | 0.9279 |  | >= 0.97 | SPEC | FAIL |
| S1_glass | view_S1 | asfound | ssim_min | 485,0,710,490 | - | 0.9279 |  | >= 0.90 | GATE | PASS |
| S1_canopy_fol | view_S1 | asfound | fol_2s | 480,180,720,360 | 80.542 | 46.125 | 0.573 | ratio 0.90-1.10 | GATE | FAIL |
| S1_canopy_Y | view_S1 | asfound | canopy_2s | 0,0,1920,1080 | 68.168 | 67.897 | 0.996 | ratio 0.90-1.10 | GATE | PASS |
| S1_recess_Y | view_S1 | asfound | luma_2s | 1700,540,1850,650 | 17.314 | 17.964 | 1.038 | ratio 0.90-1.10 | GATE | PASS |
| S1_sat | view_S1 | asfound | sat_2s | 0,0,1920,1080 | 121.786 | 122.692 | 1.007 | ratio 0.95-1.05 | GATE | PASS |
| S2_treeline_fol | view_S2 | asfound | fol_2s | 780,380,1180,1080 | 11.829 | 14.155 | 1.197 | ratio 0.90-1.10 | GATE | FAIL |
| S2_tile_fol | view_S2 | asfound | fol_2s | 960,540,1200,720 | 8.153 | 13.486 | 1.654 | ratio 0.90-1.10 | GATE | FAIL |
| S2_treeline | view_S2 | asfound | ssim_min | 780,380,1180,1080 | - | 0.9219 |  | >= 0.90 | GATE | PASS |
| S2_windows | view_S2 | asfound | ssim_min | 0,38,576,960 | - | 0.9945 |  | >= 0.97 | GATE | PASS |
| S2_gold | view_S2 | asfound | ssim_min | 1459,0,1920,1056 | - | 0.9842 |  | >= 0.97 | GATE | PASS |
| S2_canopy_Y | view_S2 | asfound | canopy_2s | 0,0,1920,1080 | 76.281 | 80.909 | 1.061 | ratio 0.90-1.10 | GATE | PASS |
| S2_sat | view_S2 | asfound | sat_2s | 0,0,1920,1080 | 130.487 | 132.498 | 1.015 | ratio 0.95-1.05 | GATE | PASS |
| S7_tile_fol | view_S7 | asfound | fol_2s | 0,720,240,900 | 4.981 | 0.076 | 0.015 | ratio 0.90-1.10 | GATE | FAIL |
| S7_refl | view_S7 | asfound | ssim_min | 0,560,720,1080 | - | 0.9743 |  | >= 0.97 | GATE | PASS |
| S7_sat | view_S7 | asfound | sat_2s | 0,0,1920,1080 | 117.812 | 118.44 | 1.005 | ratio 0.95-1.05 | GATE | PASS |
| t20_full | route_t20 | r06 | ssim_min | 0,0,1920,1080 | - |  |  |  | GATE | MISSING (missing test still) |
| t20_fol | route_t20 | r06 | fol_1s | 0,0,1920,1080 |  |  |  |  | GATE | MISSING (missing test still) |
| t20_canopy_Y | route_t20 | r06 | canopy_2s | 0,0,1920,1080 |  |  |  |  | GATE | MISSING (missing test still) |
| t20_sat | route_t20 | r06 | sat_2s | 0,0,1920,1080 |  |  |  |  | GATE | MISSING (missing test still) |
| t28_full | route_t28 | r06 | ssim_min | 0,0,1920,1080 | - |  |  |  | GATE | MISSING (missing test still) |
| t28_fol | route_t28 | r06 | fol_1s | 0,0,1920,1080 |  |  |  |  | GATE | MISSING (missing test still) |
| t28_sat | route_t28 | r06 | sat_2s | 0,0,1920,1080 |  |  |  |  | GATE | MISSING (missing test still) |
| t42_full | route_t42 | r06 | ssim_min | 0,0,1920,1080 | - |  |  |  | GATE | MISSING (missing test still) |
| t42_fol | route_t42 | r06 | fol_1s | 0,0,1920,1080 |  |  |  |  | GATE | MISSING (missing test still) |
| t42_sat | route_t42 | r06 | sat_2s | 0,0,1920,1080 |  |  |  |  | GATE | MISSING (missing test still) |

GATE VERDICT: **FAIL** (25 GATE rows, 14 not passing; SPEC rows reported, not gated)
