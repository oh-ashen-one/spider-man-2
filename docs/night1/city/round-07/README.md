# P1 City round 07 — captures and camera parameters

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
| S1_avenue_street | 1920x1080 | 1399x787 | 35.846 | 55.617 | 30.835 | 41 % |
| S1_avenue_street | 3840x2160 | 1920x1080 | 56.878 | 74.314 | 50.76 | 100 % |
| S2_avenue_swing | 1920x1080 | 1399x787 | 28.654 | 41.353 | 24.945 | 0 % |
| S2_avenue_swing | 3840x2160 | 1920x1080 | 47.591 | 62.661 | 42.635 | 0 % |
| S3_rooftop_watertower | 1920x1080 | 1399x787 | 23.262 | 36.169 | 20.079 | 20 % |
| S3_rooftop_watertower | 3840x2160 | 1920x1080 | 21.538 | 44.358 | 19.545 | 70 % |
| S4_perch_skyline | 1920x1080 | 1399x787 | 24.971 | 33.754 | 23.645 | 99 % |
| S4_perch_skyline | 3840x2160 | 1920x1080 | 32.623 | 42.17 | 31.478 | 5 % |
| S5_timessq_south | 1920x1080 | 1399x787 | 20.863 | 30.771 | 18.775 | 0 % |
| S5_timessq_south | 3840x2160 | 1920x1080 | 39.358 | 49.896 | 36.491 | 0 % |
| S6_timessq_street | 1920x1080 | 1399x787 | 19.79 | 29.26 | 18.375 | 0 % |
| S6_timessq_street | 3840x2160 | 1920x1080 | 36.344 | 48.409 | 33.956 | 0 % |
| S7_sunset_crosstown | 1920x1080 | 1399x787 | 17.622 | 27.47 | 16.182 | 0 % |
| S7_sunset_crosstown | 3840x2160 | 1920x1080 | 23.52 | 33.165 | 22.067 | 0 % |
| S8_aerial_midtown | 1920x1080 | 1399x787 | 18.652 | 27.748 | 16.943 | 0 % |
| S8_aerial_midtown | 3840x2160 | 1920x1080 | 23.156 | 32.543 | 21.503 | 0 % |
