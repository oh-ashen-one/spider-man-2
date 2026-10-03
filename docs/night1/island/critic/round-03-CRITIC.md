# CRITIC: Island A r03
Homage fan game, not affiliated with Marvel/Sony/Insomniac. Same 7 axes as r02. Frames are at 4 fps. Refs: `streets/street-midtown-high__og_0410.jpg` and `skyline-perch-dn__dn_1438.jpg`.

## Scores
1. **Facades 5.** Brick holds up. Far fire escapes are still solid zigzag slabs (r5 t=20, right facade).
2. **Street dressing 4.** The M2 street layer has paint, crosswalks, bike lanes, signals, kerbs, bollards and cars. But r5 has 0 pedestrians in any frame, about 6 cars against about 40 in og_0410, and toy-green trees.
3. **Rooftops/skyline 5.** a1 north and south are dense to the horizon. p3 towers have black glass cells.
4. **Composition 5.** r5 reads as an avenue canyon for all 30 s. The r02 empty plaza is gone.
5. **Image quality 4.** The camera is inside foliage at r5 t=6.75 (78 %), t=25.25 (68 %) and t=13.75 (47 %). The r1 t=17.25/23.25 (72 %) and r4 t=15.5 (62 %) frames are unchanged.
6. **Streaming 6.** r5 covers 1482 m to y=2285 with no bare mass and no pop-in. The audit region (x ±1024, y ±3584) has 0 facadeLod.
7. **Collision 4.**
   - r5 is clean.
   - r3 is still stuck under the fire escape from t=2.4 to 8.7. He does 6 topOut loops at x≈-235.5, the same as r02.
   - Raw hollow went from 16.72 % to 17.68 %.
   - The hero passes through a canopy (r5 t=10.2), and the rope runs through one (r5 t=26.8).

## Checks
- **a PASS.** 20/20 releases got a re-web. Max gap 0.30 s; 100 % of gaps ≤0.5 s.
- **b PASS.** 0 ground/land frames after 1 s. Min speed 32.6 m/s, 0 stalls. 24/26 anchors sit on a WHBox. Two re-anchors are 1.15 m (t=10.17) and 2.5 m (t=26.62) from a box; the second runs through a tree.
- **c PASS.** Lane paint is 3.0, 0.85\*, 1.4 and 1.1 % of the road. \*t=20 is a full crosswalk (5.4 % white). Std is 43.1, 44.1, 36.6 and 37.0.
- **d PASS.** Capsule-into-WHBox frames >0.6 m: 0 on every r02 and r03 route.
- **e** Dressed, but no people.
- **f** No regression. Frame diff vs r02 is 4.0 on r1 and 3.5 on r4. The first 10 s of r3 are identical to r02, including the stuck.
- **g** No real brand (tesseract at 2 fps on 5 clips, plus an eye scan). CHASE BANK is gone. CHOCO LOCO is still on the r3 billboard.
- **h** r2 has 187 wall frames, a max re-web gap of 2.65 s, stalls at t=18.5-20.5 and ends at z=95. Traversal owns this; not scored.

## A/B
- v1 A, v2 A, v3 B, v4 A
- s1 B, s2 A, s3 B, s4 B, s5 B, s6 A
- p1 B
- p2 tie (0.005 % of pixels differ)
- p3 B
- p4 A (a continuous chain vs a drop to a bare street)

## Single biggest gap
Make fire-escape collision match the drawn platforms and let the hero top out. On r3 crosstown-east, from t=2.4:
- Stuck time must be 0 s: no 1-s window moves <3 m.
- topOut loops must be ≤1.
- The hero must clear x=-235.5 by t=3.5.

## Secondary
1. Camera >40 % foliage must be 0 frames at 4 fps on r1-r5. Ropes must never cross a canopy.
2. Add ≥5 pedestrians per block and ≥15 cars per frame on r5 t=12-28.
3. Fire-escape LOD should be see-through grating, not zigzag slabs.
4. Review CHOCO LOCO, TOKKA and IRON GUARDIAN.

## Verdict: FAILS TARGET (lowest 4)
