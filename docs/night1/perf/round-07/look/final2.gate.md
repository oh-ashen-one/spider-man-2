look_gate.py (round 07 edition) test=/Users/midir/sm2-n1/_scratch/perf/r07/st/final2
references: as found = /Users/midir/sm2-n1/_scratch/perf/r03/before ; r06 = /Users/midir/sm2-n1/_scratch/perf/r06/final

| id | still | ref | metric | crop (1920 space) | reference | test | ratio | line | class | result |
|---|---|---|---|---|---|---|---|---|---|---|
| S1_glass_spec | view_S1 | asfound | ssim_min | 485,0,710,490 | - | 0.9268 |  | >= 0.97 | SPEC | FAIL |
| S1_glass | view_S1 | asfound | ssim_min | 485,0,710,490 | - | 0.9268 |  | >= 0.90 | GATE | PASS |
| S1_canopy_fol | view_S1 | asfound | fol_2s | 480,180,720,360 | 80.542 | 50.181 | 0.623 | ratio 0.90-1.10 | GATE | FAIL |
| S1_canopy_Y | view_S1 | asfound | canopy_2s | 0,0,1920,1080 | 68.168 | 68.739 | 1.008 | ratio 0.90-1.10 | GATE | PASS |
| S1_recess_Y | view_S1 | asfound | luma_2s | 1700,540,1850,650 | 17.314 | 18.067 | 1.044 | ratio 0.90-1.10 | GATE | PASS |
| S1_sat | view_S1 | asfound | sat_2s | 0,0,1920,1080 | 121.786 | 119.979 | 0.985 | ratio 0.95-1.05 | GATE | PASS |
| S2_treeline_fol | view_S2 | asfound | fol_2s | 780,380,1180,1080 | 11.829 | 13.093 | 1.107 | ratio 0.90-1.10 | GATE | FAIL |
| S2_tile_fol | view_S2 | asfound | fol_2s | 960,540,1200,720 | 8.153 | 9.38 | 1.15 | ratio 0.90-1.10 | GATE | FAIL |
| S2_treeline | view_S2 | asfound | ssim_min | 780,380,1180,1080 | - | 0.9238 |  | >= 0.90 | GATE | PASS |
| S2_windows | view_S2 | asfound | ssim_min | 0,38,576,960 | - | 0.9937 |  | >= 0.97 | GATE | PASS |
| S2_gold | view_S2 | asfound | ssim_min | 1459,0,1920,1056 | - | 0.9731 |  | >= 0.97 | GATE | PASS |
| S2_canopy_Y | view_S2 | asfound | canopy_2s | 0,0,1920,1080 | 76.281 | 79.669 | 1.044 | ratio 0.90-1.10 | GATE | PASS |
| S2_sat | view_S2 | asfound | sat_2s | 0,0,1920,1080 | 130.487 | 131.963 | 1.011 | ratio 0.95-1.05 | GATE | PASS |
| S7_tile_fol | view_S7 | asfound | fol_2s | 0,720,240,900 | 4.981 | 0.083 | 0.017 | ratio 0.90-1.10 | GATE | FAIL |
| S7_refl | view_S7 | asfound | ssim_min | 0,560,720,1080 | - | 0.9776 |  | >= 0.97 | GATE | PASS |
| S7_sat | view_S7 | asfound | sat_2s | 0,0,1920,1080 | 117.812 | 118.433 | 1.005 | ratio 0.95-1.05 | GATE | PASS |
| t20_full | route_t20 | r06 | ssim_min | 0,0,1920,1080 | - | 0.9879 |  | >= 0.95 | GATE | PASS |
| t20_fol | route_t20 | r06 | fol_1s | 0,0,1920,1080 | 9.956 | 9.916 | 0.996 | ratio >= 0.90 | GATE | PASS |
| t20_canopy_Y | route_t20 | r06 | canopy_2s | 0,0,1920,1080 | 84.239 | 81.386 | 0.966 | ratio 0.90-1.10 | GATE | PASS |
| t20_sat | route_t20 | r06 | sat_2s | 0,0,1920,1080 | 141.935 | 141.63 | 0.998 | ratio 0.95-1.05 | GATE | PASS |
| t28_full | route_t28 | r06 | ssim_min | 0,0,1920,1080 | - | 0.9911 |  | >= 0.95 | GATE | PASS |
| t28_fol | route_t28 | r06 | fol_1s | 0,0,1920,1080 | 5.362 | 4.646 | 0.866 | ratio >= 0.90 | GATE | FAIL |
| t28_sat | route_t28 | r06 | sat_2s | 0,0,1920,1080 | 136.254 | 136.277 | 1.0 | ratio 0.95-1.05 | GATE | PASS |
| t42_full | route_t42 | r06 | ssim_min | 0,0,1920,1080 | - | 0.9952 |  | >= 0.95 | GATE | PASS |
| t42_fol | route_t42 | r06 | fol_1s | 0,0,1920,1080 | 7.823 | 7.734 | 0.989 | ratio >= 0.90 | GATE | PASS |
| t42_sat | route_t42 | r06 | sat_2s | 0,0,1920,1080 | 124.197 | 124.009 | 0.998 | ratio 0.95-1.05 | GATE | PASS |

GATE VERDICT: **FAIL** (25 GATE rows, 5 not passing; SPEC rows reported, not gated)
