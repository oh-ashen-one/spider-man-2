# P2 hero skins, round 15: blind critic (Opus 5.5)
Homage fan game, not affiliated with Marvel, Sony or Insomniac. Coordinates are native 4K pixels unless marked.

## Scores
- **Hero model & suit: 6.** CH1 met (0.544–0.548H on all 8 front stills). CH2 met (chase median 0.451H, 22 samples).
  - Verdant profile: the lens rim now sits about 40 px *behind* the brow tip (2300 against 2342; it was 18 px proud in r14). The nose-bridge notch is 72 px (2342 to 2270, y 850 to 950).
  - Still flat lens fills, the suit is matte, and the cheek cords still read as tear-tracks.
- **Hero animation: 5.** The pawn's start is fixed: motion begins at frame 43 (0.717 s) and frame diffs ramp 1.0, 2.1, 2.3, 3.3 with no spike, so CH10 now passes.
  - The pawn's head bob is still **4.07 Hz** (peaks every 15 frames from f66), so CH6 fails.
  - The scripted side run is 3.48 steps/s (a stride repeats every 34.5 frames), which is OK.
- **Enemies: 5.** Unchanged from r14: the lineup differs from r14 on only 0.003% of pixels (>20 luma). The twin heads in slots 1/6 and 2/7 remain.
- **Civilians: 5.** The hard cut is still there at frame 449 (7.483 s, diff 55.7 against a median of 2.3).
- **Image quality: 5.** The Ash sash ends now have stitched cord borders. New defects:
  - a stair-stepped groove jog of about 20 px at the Verdant armpit (around 1300,1310 and 1430,1140);
  - a notch and shading smear at Ash (around 1480,1170);
  - the Cinder centre face seam zig-zags about 60 px sideways;
  - the front emblem and sash repeat on the Tessera and Plum backs (1080p backs), which looks like a decal projected through the torso.

## IP gate: PASS (8/8)
- No spider glyph, web lattice, teardrop lens, red/blue or black/red blocking, or text on any suit. The lenses are horizontal ovals.
- Watch: Verdant's green body with yellow limb bands and lenses drifts toward a known green/yellow vigilante costume (not Marvel/Sony).
- Watch: Cinder's black with cyan line work drifts toward a light-suit look.
- No copied brand marks: the Saffron ladder and Plum bars are abstract.

## A/B (decided before guessing identity)
- **progress-profile:** verdant A, tessera A and ash A win; the rim is behind the brow.
- **progress-head:** cinder B wins (straighter seam, deeper nose and cheeks). Tessera B wins marginally (seam has no kink). Sage A wins (clean trapezius).
- **progress-chest:**
  - ash A wins: grooves end on cords, though it has a notch at left;
  - verdant B wins: cleaner, and A has stair-step jogs;
  - cinder B wins: bordered panel, while A has stray groove stubs.
- **progress-swap-pawn:** A wins. B pops at f7 (diff 12.8 against 5.4/4.8) and jumps from 1.3 to 6.5.
- **progress-lineup:** tie (mean diff 0.68).
- **All ref-vs-ours pairs:** ref wins. The ref has gloss, micro-weave, raised web relief and a dressed street.

## Single biggest gap
Retime the playable pawn's run to 3.2–3.8 steps/s, which is a bob peak every 16–19 frames at 60 fps. Keep the current start ramp.

**Test:** in swap_pawn_T_key.mp4, the head-top FFT over 1.5–11 s gives 3.2–3.8 Hz, and no frame diff in 0–1.5 s exceeds 2× its neighbours.

## Secondary
1. Remove the stair-step jogs where groove cords cross panel borders (Verdant armpit, left chest on Ash and Cinder).
2. Straighten the face centre seam: no more than 10 px lateral deviation per 100 px of length.
3. Stop the front decals projecting onto the back: back stills must show no chest emblem.
4. Fix the enemies and civilians, untouched for several rounds: make the twin heads distinct and remove the crowd cut at 7.483 s.

## Verdict: **FAILS TARGET**
Lowest axis: 5.
