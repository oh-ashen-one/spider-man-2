# P1 City round 10 — captures and camera parameters

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Running game: `Scripts/run_game.sh` (`-game`, offscreen, map `/Game/Tests/City/City_View_<id>`, auto-activated CameraActor), screenshot at t = 28 s.
Frame times: game seconds 18-28, `t.MaxFPS 0`, no VSync, TSR with automatic screen percentage. GPU utilization read with ioreg before each run
(GPU shared with other sessions; the P1 editor was closed during the runs). Positions in browser metres (x east, y up, z south); UE = (100x, 100z, 100y) cm.

| id | camera pos | target | fov | sun (pitch, yaw) |
|---|---|---|---|---|
| S1_avenue_street | [246, 2.0, 150] | [251, 16, -300] | 75 | [-40, -45] |
| S2_avenue_swing | [243, 42, 185] | [252, 18, -350] | 80 | [-40, -45] |
| S3_rooftop_watertower | [166, 48.5, -122] | [158, 51, -150] | 75 | [-40, -45] |
| S4_perch_skyline | [182, 306, -92] | [-120, 150, -470] | 75 | [-40, -45] |
| S5_timessq_south | [-12, 6, -255] | [0, 48, -40] | 80 | [-40, -45] |
| S6_timessq_street | [8, 1.8, -110] | [-4, 26, -330] | 80 | [-40, -45] |
| S7_sunset_crosstown | [300, 30, -160] | [-300, 22, -160] | 75 | [-7, 0] |
| S8_aerial_midtown | [420, 160, 220] | [0, 20, -320] | 75 | [-40, -45] |

| id | output | internal | avg ms | p95 ms | GPU ms | GPU util before |
|---|---|---|---|---|---|---|
| S1_avenue_street | 1920x1080 | 1399x787 | 20.561 | 34.632 | 18.455 | 0 % |
| S1_avenue_street | 3840x2160 | NonexNone | None | None | None | None % |
| S2_avenue_swing | 1920x1080 | 1399x787 | 20.125 | 30.625 | 17.47 | 69 % |
| S2_avenue_swing | 3840x2160 | NonexNone | None | None | None | None % |
| S3_rooftop_watertower | 1920x1080 | 1399x787 | 23.244 | 75.732 | 15.936 | 71 % |
| S3_rooftop_watertower | 3840x2160 | NonexNone | None | None | None | None % |
| S4_perch_skyline | 1920x1080 | 1399x787 | 28.844 | 64.944 | 27.142 | 13 % |
| S4_perch_skyline | 3840x2160 | NonexNone | None | None | None | None % |
| S5_timessq_south | 1920x1080 | 1399x787 | 19.767 | 30.778 | 17.854 | 82 % |
| S5_timessq_south | 3840x2160 | NonexNone | None | None | None | None % |
| S6_timessq_street | 1920x1080 | 1399x787 | 20.897 | 30.981 | 18.972 | 68 % |
| S6_timessq_street | 3840x2160 | NonexNone | None | None | None | None % |
| S7_sunset_crosstown | 1920x1080 | 1399x787 | 18.438 | 29.329 | 16.661 | 68 % |
| S7_sunset_crosstown | 3840x2160 | NonexNone | None | None | None | None % |
| S8_aerial_midtown | 1920x1080 | 1399x787 | 21.268 | 32.038 | 18.835 | 78 % |
| S8_aerial_midtown | 3840x2160 | NonexNone | None | None | None | None % |
