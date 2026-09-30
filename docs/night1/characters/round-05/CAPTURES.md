# Round 05: captures of the running characters maps

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

**Source:** real `-game` runs (UE 5.8.3, Metal, offscreen `-RenderOffScreen -NoSound`) through F1's `unreal/WebHomage/Scripts/run_game.sh`, driven by `tools/ue_char/capture_r5.sh`. Content rebuilt headless (`tools/ue_char/build_characters_headless.sh`, `-nullrhi` commandlet, 45 s). Every Unreal launch (build, movie runs, still runs) ran inside `gpu_slot.sh capture --label characters` and waited for the loop's adaptive Unreal cap first; every release logged `contaminated=true reasons=no-exclusive-lock` (a shared capture slot, not an exclusive perf lock), so no frame time here is a performance result.

**Maps (all light: sun 8 lux + atmosphere, real-time sky light, height fog, auto exposure; 4 shadowless fills on lighting channel 1 for the characters in the fight; a test stage, not the city):**
- `Char_Hero`: hero only. The director hides every other actor per shot (`ManagedActors` / `ShowActors`): the turntable hero, the run lane hero and the jump lane hero are never in each other's frames.
- `Char_Fight`: hero (`ABP_Hero_Fight` sequence) in the middle of 6 enemies (bat, pipe, pistol carriers relaxed with the weapon hanging until they swing; three unarmed enemies in the boxing guard punching / kicking / reeling).
- `Char_Crowd`: 18 distinct citizens, two-way flow: mid lane 6 walking +X and 6 walking -X, near lane (4.5 m from the tracking camera) 3 + 3; gait phases spread by the golden ratio.
- `Char_Lineup`: standing enemies, used for the five face close-ups only.

**Movies (1080p60, fixed-step `-movie` runs: 1/60 s step, H.264 crf 20, motion blur on):** `H` = `Char_Hero` shots 1-3, `F` = `Char_Fight` shots 0-2, `C` = `Char_Crowd` shots 0-1. Frames before the director's first cut are the default camera (measured in round 04), so clips are cut at +0.05 s. `-movie` output says nothing about real-time speed.

**Stills (native 3840x2160):** real-time runs with `-exec "r.ScreenPercentage 100,r.MotionBlurQuality 0"`; every group's perf json reports internal 3840x2160, manual screen percentage (`evidence/perf_4k_groups_contaminated.json`). The director clock runs behind the automation clock, so shots are 6-8 s long and several stills share one run. The leap still comes from a fixed-step 4K `-movie` run (`hero_jump_4k`: frame at the apex).

| File | Shot | Content |
|---|---|---|
| `hero_run_side.mp4` (6 s), `hero_run_34.mp4` (5 s) | side 5.6 m / 3/4 4.8 m, FOV 40 | Hero running +X on an empty street |
| `hero_run_leap_side.mp4` (6.5 s) | side 8.2 m, FOV 42 | Run, takeoff crouch (1.3 s), `runLeap`, landing, run, second jump (`runLeapB`) |
| `street_fight_wide.mp4`, `street_fight_34.mp4`, `street_fight_orbit.mp4` (8 s each) | static wide 10 m / static 3/4 / orbit 9.5 m | The staged fight |
| `crowd_tracking.mp4` (8 s), `crowd_wide.mp4` (6 s) | side tracking 11.5 m, FOV 64 / wide | Two-way flow, near lane walkers |
| `*_1080.jpg` | | 1080p frames of the movies |
| `hero_turntable_4k`, `hero_run_side_4k`, `hero_jump_4k`, `suit_closeup_4k`, `hero_face_lens_4k` | | Hero: moving turntable, run side, the leap at its apex, chest close-up (weave, thread relief), face + lens close-up |
| `street_fight_wide_4k`, `street_fight_34_4k`, `street_fight_orbit_4k` | | The fight |
| `crowd_tracking_4k`, `crowd_wide_4k` | | The crowd (CH18 test image) |
| `thug_face_4k`, `brute_face_4k`, `hood_face_4k`, `tee_face_4k`, `beard_face_4k` | | Masks and faces of the five enemies |

**Evidence (`evidence/`):** `cracks_stills.txt` (critic's `cracks.py` on the crowd stills), `count_videos.txt` (critic's `count.py`), `yolo_*.json`, `head_pitch_clips.json`, `video_hero_run_side_*.json`, `hero_leap_takeoff.json`, `hull_stats.json`, `crack_proxy_*.txt` (offline proxy), `perf_4k_groups_contaminated.json`, `gpu_util_before_4k.txt`, `suit_r5.json`.
