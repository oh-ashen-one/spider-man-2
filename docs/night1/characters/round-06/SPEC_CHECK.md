# Round 06: SPEC check (CH1-CH19)

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation.

**No engine capture was possible this round (see `CAPTURES.md`), so no row is re-measured in the engine.** Rows other than CH18 are unchanged content: the last measured values are in `../round-05/SPEC_CHECK.md` and are not repeated as round-06 results.

| id | target | round 06 |
|---|---|---|
| CH1-CH15, CH16, CH17, CH19 | see SPEC.md | unchanged in code and content since round 05 (hero, enemies, crowd layout, gait phases); not re-measured |
| CH18 | zero seam / sparkle pixels at native 4K | **root cause fixed in the content pipeline; engine verification pending.** Offline gate (`eval_r6.py`, proxy of the engine's skinning on the crowd's own clips, 18 citizens x 72 views at 700 px/m): cracks 1035 comp / 42551 px (round-05 geometry) -> **244 / 13362** (refit; the rest are silhouette-edge slivers and 1-3 px ankle rings); triangles whose edges grow > 5 cm in a walk 2134 -> **13**, > 10 cm 915 -> **0**, worst 51.5 -> **5.6 cm**; the coat flap, the sleeve / armpit hole and the stretched fingers of round 05 are gone in the same-pose proxy (`evidence/offline_before_after_proxy.jpg`). Engine baseline to beat: round-05 key stills, interior hole components 47 / 31 / 47 / 31 (`evidence/keyreport_round05/`). |
| CH3 (texel density) | >= 680 texels/m (hero) | hero unchanged (2331 texels/m). Citizens: 2048 px raw-Tripo texture (was a 1024 px atlas tile): ~2x the linear density |

## What the round-05 critic asked for, and the state

1. Zero enclosed key pixels inside any torso or sleeve silhouette: offline no torso / sleeve crack remains except silhouette-edge slivers; **engine rerun of `crowd_key_*_4k` pending**.
2. No vertex spike > 5 px outside the cloth hull on the olive coat, trousers, hoodie collar: coat and trousers: geometry fixed offline (no edge grows more than 5.6 cm in any crowd clip; the round-05 flap grew 34 cm); **hoodie collar (thug): measured 0.9 cm edge growth in its walk, not a stretch defect; the dark shapes are shadow / neck skin under the mask hem; unchanged**.
3. No stretched fingers: hands are the raw Tripo hands (five wedges, single-piece, 100 % on the hand bone, no seam tears); 3x engine crop pending.
