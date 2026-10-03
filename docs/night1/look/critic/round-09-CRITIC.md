# P4 sky/ToD critic, round 09 (pixels only)
> Homage fan game, not official Marvel/Sony/Insomniac. Work: `_scratch/critic-P4-r09-work/`.

## Scores (r03 floor 6/4/4/4/5/5)
1. **Sun/sky/ToD 5:** golden L1 4/8 (S3 35.5, S7 42.2, S4 117.1, S5 Y<10 8.34 %); midday S7 71.1; L27 9/12.
2. **GI & shadows 4:** golden S3/S7 Y<10 27.9/29.5 %, crushed.
3. **Atmosphere 5:** S4 boxes pass, but far rank is a pale cut-out over a dark horizon band: strip rows 95-140 splits 34 Y (ref `skyline-perch-nm` 10).
4. **Reflections 4:** unchanged.
5. **Post 4:** S4 mean 117 (>100); S7 mean 42 after r09 (before 60.4).
6. **Night 5:** windows 3.14 % pass; L3 S3 33.2 and L13 S6 4 blobs fail; moon is a 78-px Y≥200 bloom.

## Checks
- **a** PASS: sky 183.1 view / 181.7 tour.
- **b** View −31.7 / −27.2 PASS. Pose = in-game tour (shift 0,0); tour −28.7 / **−24.7 FAIL**; ToD 18:24 −27.5 / **−23.5 FAIL**.
- **c** PASS: T2 2.0 %, T4 0/1 bright.
- **d** C12 +8.1, C11 10.2, C14 30.2, C15 0.26 PASS; T1 def-B 26.7 pass, def-C 0.6. ToD 18:24: C11 5.2, C12 14.9, C15 0.16 FAIL.
- **e FAIL:** S3 51.9 / S7 53.2 / S8 17.9 % vs 13.2 / 1.4 / 7.8.
- **f FAIL:** midday L2 7/8 (S7), L7 8/8; night L3 7/8, L8 8/8, L13 7/8; L25a 78 px/255 pass; golden L1 4/8 (r03 7/8); L22a 3.14 % pass; lapse L23b not supplied = unproven; L27 9/12 (S4 20:00 a +8.1, S4w 20:00 b 25.6, S4w 20:30 d −13.7).
- **g** Cut-out, not depth: far towers ~159 over horizon sky ~125.
- **h FAIL:** sky 5<6, post 4<5.

## A/B (decided first)
Refs: blue-hour B, dawn B, dusk A, aerial B, avenue B, perch A, perch-2 A, rooftop B, sunstreet A, swing B, moon A, night-skyline A, night-street B, overcast A. Ours lost all 14.
Progress: before-s3 A, before-s4 A, before-s7 A, city-r11-s4 A, r03-s1 A, r03-s3 A, r03-golden-s4 A, r03-golden-s7 A, midday-s4 B, midday-s7 B, night-s1 A, night-s4 B.

## Biggest gap
Remove the dark horizon band; let the far rank dissolve into haze. On 1080p S4 view, tour and ToD 18:24: Otsu split of rows 95-140 × x 0-1500 ≤ 12 Y; sky rows 100-130 at x 1300-1460 ≥ far-band mean (now 121-124 vs 151); L29a-d pass on all three.

## Secondary
1. Golden S3/S7/S8 Y<25 back to 13.2/1.4/7.8 %; L1 ≥ 7/8.
2. Put the r09 far-band look into ToD 18:24 (C11/C12/C15, box 2).
3. Night S3 mean ≥ 37, S6 ≥ 5 blobs; moon a disk, not a 78-px bloom.
4. Supply the L23b lapse; L27 12/12.

Brand: none flagged (rooftop board excluded by owner ruling).

## Verdict: FAILS TARGET (lowest 4)
