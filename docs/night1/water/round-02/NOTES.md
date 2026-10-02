# River water, round 02 (Opus 5.5): capture notes

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Build: `night1/water` = integration 914de97 + round-02 water (`unreal/WebHomage/Scripts/build_water.py`, `tools/water/water_inputs.py`).
City: `build_manhattan.py` (unchanged) through the scratch wrapper (HANDOFF.md), export cloned from the integrator's morning showcase stage.
Every Unreal process (commandlets included) ran inside `gpu_slot.sh capture --label water` holds; perf under `gpu_slot.sh perf` (exclusive).
Numbers: `python3 tools/water/water_spec.py all docs/night1/water/round-02 --json docs/night1/water/round-02/spec.json`
(instrument calibrated on the round-01 critic numbers: see the docstring; reproduces build O's 90.6 / 4.4 / 117 and the 0.22 autocorrelation).

## What changed vs round 01
1. **Ring artifact / periodicity:** the 12 analytic capillary sinusoids summed into a lattice (top-down emulation shows a crystal pattern),
   and the warped wind-streak foam closed into loops. Replaced by 4 layers of a baked random-phase wind-sea slope spectrum
   (`T_WaterSlope`, k^-4, 3..24 cycles / tile, 2 realizations, tiles 21 / 6.7 / 2.2 / 0.73 m, scrolled at their phase speed, mip bias +1,
   unresolved variance -> roughness). Streaks no longer make foam and are straight (warp 26 -> 5 m), at half strength.
   Dolly autocorrelation at 80 px: round 01 **0.224** -> round 02 **see table** (target <= 0.10).
2. **Contact foam:** round 01's depth-based foam (SceneDepthWithoutWater) did not show. Added `T_WaterContact`: distance to the nearest
   place where the city export's geometry crosses the water plane (seawalls, bulkheads, pier piles, bridge piers; island shore box,
   0.89 m/px, 120 844 crossing segments from 54 GLBs, positions offset by each mesh's manifest tile centre). Foam band 0.1..~2.5 m,
   lapping, noise-broken; FoamK 1.8.
3. **Darker, choppier water:** ScatK 0.2 (body scattering x0.2), ChopK 2.6, BendK 0.3 (facets whose reflection would point below the
   horizon are bent up: Lumen would otherwise trace into the void). Picked from tuning variants (table below).
4. **New views:** `river_sun` (across the Hudson into the golden sun: glitter path) and `harbour_high` (coverage: harbour + both rivers);
   `harbour_high` shows the water wrapping the island (the grid follows the camera to 81 km; contact map covers the island's whole shore).
5. Build hygiene: /Game/Water is rebuilt from an empty folder (an in-place material rebuild failed to compile for Metal SM6 twice ->
   default material; the hold scripts now abort if the game log reports it).

## Look rig changed since round 01
The integrated golden rig (look piece, merged after round 01) is not the same: S4 far shore Y **150** (round 01: 171), cloudier sky.
Round-01 vs round-02 brightness comparisons are therefore not like for like; the previous-vs-this pair in the critic pack shows it.
