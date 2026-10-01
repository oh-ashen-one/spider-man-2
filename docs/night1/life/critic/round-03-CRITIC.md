# P6 City Life, critic r03 (blind, pixels only)
Homage fan game, not an official Marvel, Sony or Insomniac game.
YOLO11x-seg (conf .35, 1920 px, CPU, video frames every 0.5 s) matches detector.txt exactly. Foot data comes from feet_clip.csv. Work dir: `_scratch/critic-P6-r03-work/`.

| Axis | r2 | r3 | Evidence |
|---|---|---|---|
| 1 Traffic density/variety | 5 | **5** | S1 9/8 vehicles (C4 5–19, median 11). S2 14/15, still the low edge of C6. Swing median 24, but car boxes are 30 px vs 47 px in the ref, so the camera is still too far. At swing@0.5 s the nearest block has 5 cars in 4 lanes. |
| 2 Traffic motion | 5 | **5** | Heads lit red. A queue of 2 taxis, a van and a bus holds while a box truck crosses, then pulls away by 12.25 s. The pickup-bed fault is fixed in S2. Near lanes at swing height are still thin. |
| 3 Ped density/variety | 5 | **6** | S1 51 people (30 L / 21 R, 41 % right), street median 28, signal 48. Hand count at swing@5 s is ≥15 per near sidewalk, which closes the r2 gap. Faults: the hard-hat + hi-vis look appears 4× in S1-left. Outfits are candy-saturated. Crowds move as single-file conga lines. Pink twins at swing@8 s. |
| 4 Ped motion | 4 | **4** | CH19 now proven: median pairwise phase 0.26. But during stance the foot slides 47–54 cm/s (about 40 % of the 1.2 m/s walk, ≈20 cm per step). Ankle lift reaches 31 cm, a visible back-kick at street@9.6–10.1 s. Every walker's period is 1.00–1.10 s. Legs poke through long coats. A group walks mid-roadway, off any crosswalk, at swing@7.75–8.5 s. |
| 5 Believability + IQ | 4 | **4** | A haze column sits on the road centre in every S1 view: asphalt luma 183/164 vs 100–131 at either side (4K y=1450/1600). The bus rear is a hollow, smeared white box (street@0.75 s). White untextured plaza at swing@8 s. People are flat and plastic-lit. |

**A/B (merit first)**: avenue-street **A** (photoreal; B is sparse in the near lanes and shows the haze column). Sidewalk **A**. Avenue-traffic **A** (28 vs 13 vehicles, closer camera). Swing-avenue **A** on fidelity, though B is denser (21 vehicles, 12 people). Progress-street **A** (42 vs 26 people, right sidewalk 17 vs 3), with flatter shading. Progress-avenue **B**, because A has people standing in a pickup bed on a crosswalk. Progress-swing **A** (12/21 vs 0/9). Guesses: ref = A in avenue-street, sidewalk, avenue-traffic and swing-avenue. Newest build = progress-street A, progress-avenue B, progress-swing A.

**Biggest gap**: plant the feet. In feet_clip.csv (≥14 walkers), stance ankle speed (foot within 1 cm of its minimum height) must have a median ≤10 cm/s (now 47–54). Peak ankle lift must be ≤20 cm (now 31). Gait periods must span ≥0.25 s (now 0.10 s), via stride or speed variants.

**Secondary**
1. Remove the centre haze column: in S1_4k, asphalt luma at x1880–1960 must be within ±10 of x1600–1700 and x2150–2250 at y=1450 and y=1600.
2. Crowd composition: within 30 m in S1, no look appears more than twice and no twins. Desaturate outfits. Break the single-file streams into mixed-direction, staggered flow.
3. Swing: median car box ≥45 px at 1080p and ≥8 moving vehicles on the nearest block. Zero pedestrians in the roadway outside crosswalks.
4. LOD0 bus rear and van must be closed, textured geometry. Flag the untextured white plaza to the city owner.

Brands: none copied. METRO LOCAL SHIPPING, SALT & PEPPER DINER, HARBOR LIGHT PHOTO, HALEY'S SHOE REPAIR, SUNRISE BAGELS, THE PAPER MILL and VELVET & VINE are invented. The crossing taxi carries only a checker stripe; no "NYC TAXI" text was seen.

**Verdict: FAILS TARGET** (lowest score is 4; MEETS needs ≥8 on every axis).
