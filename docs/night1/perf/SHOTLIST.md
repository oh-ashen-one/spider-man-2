# F perf: shot list (Night 1)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Reference stills live in the private repo
> `~/spiderman-learnings/refs` and are never committed here.

Every capture is the RUNNING game (`Scripts/run_game.sh`, offscreen `-game`, true 3840x2160 back buffer) on the integrated Manhattan map (piece C's
`/Game/Maps/Manhattan`, golden rig), inside `gpu_slot.sh capture` (stills / clips) or `gpu_slot.sh perf` (frame times). "Before" = the build as
found (all Epic-tier defaults, HWRT Lumen, `r.Nanite.MaxPixelsPerEdge 1`), "after" = `overrides/perf60.cvars` + the content transformations kept in the round.
Internal resolution is `r.ScreenPercentage 50` = 1920x1080 unless a row says otherwise; TSR upscales to the output.

**Round 02 update:** "after" = `overrides/perf60_hwrefl.cvars` (hardware-RT reflections, software GI, Nanite error 6) on the RT-lite map copy with the 4 km cloud (`/Game/PerfF/Cl4RT/`) at `r.ScreenPercentage 46` = 1766x994 internal (`stills/after_settings.json`);
"before" = as found (TSR 50 % = 1920x1080 internal). Extra route stills at game t = 38 / 42 s (late route, horizon). The R2 clip is a 1080p60 fixed-step movie at native 1080p internal with the Nanite error halved (footage only).
P-R = route frame times at TSR 44 / 46 / 50 (hardware-RT) and 50 / 58 (software), `round-02/perf/s4_official`; P-S2 = static S2 at TSR 46.

| id | view / movement | camera | before / after | reference (private) |
|---|---|---|---|---|
| S1 | avenue canyon at street level, looking north (`/Game/Maps/Manhattan_View_S1`) | P1 shot S1_avenue_street | 4K still x2 | `streets/street-avenue-hero-taxis__og_0000` |
| S2 | 42 m over the avenue, mid-swing height (`Manhattan_View_S2`); also the heavy-view perf line P3 | P1 shot S2_avenue_swing | 4K still x2 + static-view perf | `streets/street-midtown-high__og_0410` |
| S7 | sunset cross street, 30 m up, looking west into the sun (F's local `/Game/PerfF/View_S7`, `tools/perf_ue2/make_views.py`) | P1 shot S7_sunset_crosstown | 4K still x2 | `streets/sunset-swing-trailer__eny_0142` |
| R1 | 30 s scripted swing route (C `route_30s_warmup15.json`), stills at route t = 5 s and 13 s (game 20 s / 28 s) | P3 chase camera | 4K still x2 | `traversal/swing-avenue-canyon-above__nm_0557` |
| R2 | the same route as a clip: 1920x1080 output at native internal resolution, `r.Nanite.MaxPixelsPerEdge 2` (= the 4 px of the 4K run), fixed 1/60 s step. Footage only: it says nothing about real-time speed | P3 chase camera | mp4 (after) | - |
| P-R | frame times of R1 for 30 s, 3840x2160 output at TSR 50 / 58 / 67 % | - | perf tables | - |
| P-S2 | frame times of S2 (static camera, 30 s) at TSR 50 % | - | perf table | - |
