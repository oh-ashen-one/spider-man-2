# P2 hero skins, round 12: blind critic (Opus 5.5)

Homage fan game, not affiliated with Marvel, Sony or Insomniac. Stills are 3840×2160 unless marked; clips are 1080p60. Coordinates are in native pixels.

## Scores
- **Hero model & suit: 5.**
  - Met: CH1, head 512 → feet 1689 = **0.545H** (all eight front stills fall in 0.544–0.547). CH2, chase median **0.46** (22 frames).
  - Met: the lines are now real grooves. Across Tessera chest y=700 the line minimum is 17–43 against a lip of 65–74, a difference of at least 20.
  - Failed: the heads are still unsculpted socks with small almond lenses and no rim. Ref: suits-duo-closeup.
- **Hero animation: 5.**
  - Met: CH7 lean is about 21° (hip (1190,620) → neck (1300,330), hero_run_side @2.0 s). Ref ≈30°.
  - Met: CH10, idle→run blends over frames 45–60 with no pop.
  - Failed: CH6 on the **playable pawn**. Head-bob minima in swap_pawn_T_key fall at frames 87, 101, 117, 131, 146 (FFT **4.08 steps/s** at 9.8 m/s). The scripted runs pass: hero_run_toward has a minimum every 17 frames, which is 3.5 steps/s.
- **Enemies: 4.**
  - Met: weapons are pistol, crowbar and bat. Silhouettes include a bomber jacket, puffer vest, hoodie and leather jacket.
  - Failed: the lineup has only 6 men (7 needed). The crowbar passes through the fingers at (2000,1440), and the lighting is washed out.
  - In street_fight_wide, 7 enemies clump within about 1 m and attack all at once, with no hit FX.
- **Civilians: 5.** Frame crowd_tracking @3.25 s shows 13 people from at least 9 distinct models, and their legs animate.
  - Failed: the robe and long coat are rigid shells that legs poke through.
  - Failed: there is a hard camera cut at 7.5 s.
- **Image quality: 5.**
  - Fixed: lines no longer show through the sash, and the Verdant chevron apex is clean.
  - New defects:
    - Sash ends are unfinished: Ash's ragged upper end (1410–1440, 700–1050) and Tessera's straight cut have no piping.
    - Ash's armpit stitches smear and double at (1150–1200, 1530–1600).
    - There is a 12 px black kinked neck/face seam on every suit.
    - Cinder's emblem is cyan on a cyan sash and is crossed by its stitches.

## IP gate: PASS
- No suit has a spider glyph, a radial web, rimmed teardrop lenses, red/blue or black/white blocking, or any brand text.
- Tessera, Cinder, Glacier, Ash, Sage: no resemblance.
- Verdant: the ring is gone, so it is now a generic green/yellow chevron. Pass.
- Saffron: the brown raglans are gone and there is no dark cowl/yellow blocking. Pass.
- Watch Plum: its purple+mint palette is loosely villain-coded, but no blocking or emblem matches.

## A/B decisions
- **Ref vs ours (all 20 ref pairs): the ref wins.** The ref has glossy micro-weave, sculpted lenses, a dressed street and impact FX. Ours has blank planes, matte suits and no FX.
- **progress-tessera: A.** In B, net lines show through the sash and the sash's left end is smeared. Identity guess: A is round 12.

## Single biggest gap
Sculpt the mask head and lenses. Replace the egg with:
- brow ridge, nose bridge, cheekbones and chin relief;
- lenses at least 1.6× their current width, with a raised dark rim at least 6 px wide at 4K;
- the face seam as raised piping, not ink.

**Test:** in the 4K head still, a horizontal luma profile through the nose bridge shows at least 3 extrema with at least 20 luma swing. The profile silhouette shows a nose bump of at least 2 % of head height.

## Secondary issues
1. Bring the playable pawn to 3.2–3.8 steps/s (CH6).
2. Finish every sash end with piping. Fix the Ash armpit stitch smear and Cinder's same-colour emblem.
3. Lineup of at least 7 enemies with gripped weapons. Fight enemies spaced at least 1.5 m apart and attacking in turns.
4. Fake cloth motion for long coats and robes. Remove the 7.5 s crowd cut.

## Verdict: **FAILS TARGET**
Lowest axis: 4 (enemies).
