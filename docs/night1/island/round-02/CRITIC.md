# CRITIC: Island A r02
Homage fan game, not affiliated with Marvel/Sony/Insomniac. Same 7 axes as r01. Frames at 4 fps; t = clip time.

## Scores
1. **Facades 5.** Brick and fire-escape grating read up close (r3 t=2-8). Distant fire escapes are solid zigzag slabs (r2 still t12, left half). Glass reflects them as blocky "Z" shapes (r4 t=19.5).
2. **Street dressing 3.** On new tiles the road is a bare slab. Lane paint in the road band is 1.21 % at r2 t=12 and 0.00 % at t=26/28; luminance std drops from 39 to 13-17. There are no cars and no pedestrians (ref `swing-avenue-traffic-dn__dn_0952`).
3. **Rooftops/skyline 5.** The a1 stills give a dense tower field. The far shore (a1 north crop) is windowless pale extrusions. Roof props are bare slabs (r4 t=5-8).
4. **Composition 4.** From r2 t=25 to 30 s the "avenue" reads as an empty plaza.
5. **Image quality 5.** Y<25 averages 4-8 %. The camera is inside foliage at r1 t=17.25 (70 %) and t=23.25 (75 %), and r4 t=15.5 (60 %).
6. **Streaming coverage 4.** I saw no pop-in. The detailed street layer ends at y≈1010 (r2 t≈19.5), which matches the audit bound z1=1024. I3 (whole island) is unproven.
7. **Collision 3.**
   - **Fixed since r01:** the parapet clip (p1). Of the 9 web anchors I could see in frame, all 9 projected onto a facade.
   - **r2:** from t=23.72 to 30 s swing is held and nothing attaches (y>1228). The hero dives and runs the slab, so the new tiles cannot be swung.
   - **r3:** from t=2.38 to 8.93 s the hero is stuck under a fire-escape landing. He loops wallRun→topOut 5 times while z goes 32.2→36.2, and at t=7.75-8.0 the camera is inside the escape.
   - **r3 anchors:** 4 anchors in 0.12 s (t=16.28-16.40).
   - **r4:** from t=13.7 to 15.5 the hero slides down glass in air/dive with his body flush against it (wall-air look).
   - **Audit:** raw hollow is 16.72 % against 0.22 % after erosion. I5 passes only on the eroded figure.

**Content/:** 0 .uasset/.umap files on the branch and 0 in all history.

## A/B (decided before any identity guess)
- **v1: B.** It has traffic and pedestrians. A has an untextured grey sedan (t=1.5).
- **v2: B.** A's camera goes into the trees at t=4.75, 6.75 and 8.25.
- **v3: A.** It is a real canyon swing. B lies prone on a roof (t=3.5) and crawls sideways.
- **v4: B.** It has a continuous wall-run.
- **s1: A.** Its far band is continuous city with bridges.
- **s2: B.** It has material variety and depth.
- **s3: A.** It has haze and speed lines.
- **s4: B.** A is a soft glass under-view.
- **p1: B.** A hides the hero inside the parapet for t=0-2 s. B stays on the drawn surfaces.

## Single biggest gap
Give every tile past the merged region (y>1010) the merged-city street layer and facade anchors.
- **Test:** rerun r2 with swing held. A web must attach ≤0.5 s after every release through t=30 s, with 0 ground frames after t=1.
- **Test:** the road band at t=26/28 must have ≥1 % lane-paint pixels and luminance std ≥35, matching t=12.

## Secondary
1. Fire-escape collision must allow a top-out. On r3, wallRun→topOut cycles at one xy must be ≤1, and stuck time must be 0 s.
2. Replace the distant fire-escape zigzag LOD with see-through grating, or drop it.
3. Pull the camera out of foliage: 0 frames with >40 % foliage.
4. Remove the real brand **CHASE BANK** (r2 t=25.0-25.25). Also review CHOCO LOCO, TOKKA and the IRON GUARDIAN mural.

## Verdict: FAILS TARGET (lowest 3)
