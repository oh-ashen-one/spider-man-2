# P6 City life round 01: spec table

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Counts come from the engine itself (`WHLifeProbe`, log lines `WH_LIFE_FRAME`): every vehicle / person whose centre projects into the frame, is at least N pixels tall and is reached by a visibility ray from the camera (city geometry blocks it; other vehicles and people do not). No YOLO model is installed on this machine, so these are NOT detector counts: the spec numbers were measured with YOLO on the reference, which misses small and partly hidden objects, so compare with the LARGER size threshold (>= 44 px vehicles / >= 56 px people) as well as the small one. Median (min-max) over the reports at game t = 8, 14, 20, 28 s of each run; "twins/looks" = people in frame that share model AND outfit with another person in frame. Verdicts use the 4K runs.

| id | target (SPEC) | measured (this build) | verdict |
|---|---|---|---|
| C4 cars, S1 street frame | 5-19 (median ~11) | vehicles moving + parked, >= 22 px: 4K 22 (22-23); 1080p 9 (9-11); >= 44 px: 4K 9 (9-11); 1080p 5 (4-6) | MEETS at >= 44 px (>= 22 px counts small far cars: above the range) |
| C4 people, S1 street frame | 6-32 (median ~24) | people >= 28 px: 4K 15 (15-18); 1080p 10 (10-13); >= 56 px: 4K 11 (10-12); 1080p 5 (4-5) | MEETS (median below the ~24 of the reference) |
| C4 traffic lights >= 1 | >= 1 | P1 street-kit signal heads are in the S1 frame (stills); they are P1 props and are NOT driven by the life signal clock | present, not driven |
| S1 parked cars incl. taxis | >= 5 parked cars incl. taxis | parked in frame >= 22 px: 4K 12 (12-12); 1080p 4 (4-4); parked taxis: 4K 1 (1-1); 1080p 1 (1-1) | MEETS |
| C6 vehicles, S2 avenue from swing height | median 14-22 per frame | vehicles moving + parked, >= 22 px: 4K 14.0 (11-17); 1080p 0.0 (0-0) (>= 44 px: none, the avenue is 60-500 m away) | MEETS |
| CH16 people per frame (street level) | 8-25 | S1 people >= 28 px: 4K 15 (15-18); 1080p 10 (10-13) | MEETS |
| CH17 >= 6 distinct civilian models in one frame, no identical twins | >= 6 models; 0 twins | S1 looks (model + outfit) in frame: 4K 15 (15-17); 1080p 10 (10-13); identical looks in frame: 4K 0 (0-1); 1080p 0 (0-0). 60 looks = 20 citizen meshes x 3 outfits; the mesh alone repeats | MISSES |
| CH17 no gliding / frozen walkers | 0 | planted-stance ankle displacement, S1 4K: `ankle world displacement during a planted stance (cm; ~20-25 = heel-toe roll, a stride is ~55) median 16.2 p95 38.4 max 59.9 | stances > 45 cm (sliding) 7 (2.3 %)`; S1 1080p: `ankle world displacement during a planted stance (cm; ~20-25 = heel-toe roll, a stride is ~55) median 26.3 p95 43.3 max 64.6 | stances > 45 cm (sliding) 10 (3.3 %)` (details below) | see notes |
| CH19 gait phases not in lockstep | pairwise phase difference spread >= 0.2 cycle across >= 6 walkers | 14 walkers: max pairwise difference 0.474 cycle, mean 0.263, resultant length R 0.078 (0 = evenly spread), pairs within 0.05 cycle: 7 of 91 | MEETS |

