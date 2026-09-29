# P4 Look, lighting, post, perf: shot list (Night 1)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. Nothing here is meant to infringe.

Target: the look of Marvel's Spider-Man 2's Manhattan: warm physically plausible sun, deep blue skylight, aerial perspective and
haze layers, strong bounce light in the avenue canyons, glossy glass reflections, bloom / lens character, filmic tonemapping,
motion blur, and 60 fps at 3840x2160 output on the M3 Ultra with the internal resolution disclosed.

## Stills: the city views under each preset

The eight views of `unreal/WebHomage/Scripts/city_shots.json` (P1 SHOTLIST, `docs/night1/city/SHOTLIST.md`) are rebuilt as
`/Game/Tests/Look/Look_View_<preset>_<S#>` by `Scripts/build_look.py` for each preset, so a still differs from its P1 counterpart only by the
lighting rig. References: `~/spiderman-learnings/refs/streets/` (private repo, never committed here), the same files P1 lists.

| id | view | preset(s) | reference focus |
|---|---|---|---|
| S1_avenue_street | avenue canyon at street level looking north | midday, golden, night | canyon bounce light, sun shafts at the end of the avenue, street level exposure |
| S2_avenue_swing | 42 m swing view down the avenue | midday, golden, night | haze layers in depth, glass reflections of the sky |
| S3_rooftop_watertower | rooftop with a timber water tank, towers behind | midday, golden, night | sun colour and shadow softness on rooftop clutter |
| S4_perch_skyline | perch on a 300 m glass tower, skyline to the north-west | midday, golden, night | aerial perspective over kilometres, cloud layer, night city lights |
| S5_timessq_south | bowtie from the red steps looking south | midday, golden, night | billboard / neon emission at night, bloom |
| S6_timessq_street | bowtie at street level looking north | midday, golden, night | night street level, lens character |
| S7_sunset_crosstown | 30 m up looking west down a cross street into the sun | midday, golden, night | golden hour beams, volumetric fog, lens flare |
| S8_aerial_midtown | high aerial over midtown toward the park | midday, golden, night | distance haze, sun angle on roofs |

Each is captured at 3840x2160 and 1920x1080 (native internal resolution, `r.ScreenPercentage 100`) at game time 20 s
(`tools/perf_ue/capture_looks.py`), after the eye adaptation, Lumen scene and TSR history have settled.

## Clips: real gameplay per preset

`swing_<preset>.mp4`: 1920x1080, 60 fps (fixed 1/60 s step, every frame dumped), 12 s, <= 15 MB. The P3 traversal hero
(`Scripts/build_traversal.py` builds the hero; `-WHTravScript=tools/perf_ue/scripts/city_swing_clip.json`) starts 35 m over the avenue
at 22 m/s northward and web-swings with the deterministic autoChain rhythm through the real city (map `Look_Midtown[_golden|_night]`).

## Perf (real gameplay)

`tools/perf_ue/run_perf.py`: the same hero replays `tools/perf_ue/scripts/city_swing_avenue.json` (14 s standing warm-up, then a
sprint, jump and continuous swing chain up the avenue) at 3840x2160 output with `r.ScreenPercentage` 50 (TSR, 1920x1080 internal),
67 (2573x1447) and 100 (native). Numbers, GPU utilisation before each run and the top GPU passes: `round-NN/PERF.md`.
