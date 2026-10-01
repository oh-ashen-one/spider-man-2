# F perf round 06: clips

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

| file | what | output / internal | settings | size |
|---|---|---|---|---|
| `route_30s.mp4` | R2: the 30 s swing route (P3 r14 camera), shipped preset, no traffic / crowd (`/Game/Maps/Manhattan`) | 1920x1080 / 1920x1080 (`r.ScreenPercentage 100`) | `route_30s_settings.json`: `perf60_hwl3`, Nanite error 4 (= the 8 px of the 4K run halved), fixed 1/60 s step | 14.6 MB, 30.0 s |
| `route_life_30s.mp4` | R2-L: the same route WITH P6's traffic + crowd (`/Game/PerfF/Life/Manhattan`) | 1920x1080 / 1920x1080 | `route_life_30s_settings.json`: same as R2 | 14.6 MB, 30.0 s |

Both are FOOTAGE only: a `-dumpmovie` run uses a fixed 1/60 s step and says nothing about real-time speed; the frame times are the 4K `perf/f1` runs. The 0.8 s pre-roll is trimmed. Hero spawned in both (no `Couldn't spawn Pawn` in the logs).
