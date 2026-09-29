# Performance ledger

Target: Mac Studio M3 Ultra, 1920x1080, High, render scale 1. Day lighting, puddles on, existing motion blur/DOF enabled. Real visible desktop Chrome, ANGLE Metal; no headless rendering. The actual drawing buffer was asserted at 1920x1080 for every final measurement.

**60 FPS is not verified.** The reliable final run was on the main LG display at 50 Hz. Its stable frame cadence is about 20 ms. A second display reports 120 Hz, but attempts to use it suffered window movement, resolution changes and a window closure; those mixed-resolution attempts were discarded. No shared display setting was changed.

| View | Mean ms | Average FPS | 1% low FPS | P99 ms | Worst ms | >33.34 ms | Mean animator CPU ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| street | 20.02 | 49.95 | 47.56 | 21.00 | 21.10 | 0 | 0.149 |
| park | 20.27 | 49.34 | 23.12 | 21.00 | 120.20 | 3 | 0.143 |
| traversal | 20.02 | 49.95 | 47.56 | 21.00 | 21.10 | 0 | 0.204 |

Each final view records 719 intervals after warm-up. The traversal run observed actual authored tricks alongside swing, wall and landing transitions. The park run had three hitches, including a 120 ms maximum; their cause is unresolved. This is not a claim of hitch-free gameplay or a locked 60 FPS result.

The initial untouched baseline at the same 1080p/High settings and main 50 Hz display averaged 20.02 ms in street and park views, with approximately 45.5 / 46.0 FPS 1% lows and no >33 ms hitches in its shorter 359-interval samples. Dynamic city populations and sample lengths differ, so these runs are descriptive evidence rather than a controlled regression percentage.

Evidence: [initial baseline](baseline-performance.json), [final desktop run](final-desktop-performance.json), corresponding street/park/traversal captures, and [reproduction script](../../../tools/heroanim/performance.mjs). Original source snapshot used for attempted before/after checks: 1ead02a; it added no hero clips. The final source retains identical original hero/skin geometry.
