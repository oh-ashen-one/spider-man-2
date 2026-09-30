# P5 Combat: shot list (r02)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Map `/Game/Tests/Combat/Combat_Street` (procedural test street, dusk), the real game (`-game`, offscreen), scripted hero (`scripts/fight30.json`, frozen from the
reactive record run `fight30_record.json`), 60 fps fixed step, output 1920x1080 for the movie and 3840x2160 (native, `r.ScreenPercentage 100`) for stills. Internal
resolution is disclosed in `NOTES.md` for every run.

| id | what | how | matching reference |
|---|---|---|---|
| M1 | 32 s fight, 9 + 13 enemies, 3 launchers + air juggles, 2 finishers, web shots / strike / pin, dodges | `run_fight.sh movie` (1080p60 `-dumpmovie`), mp4 <= 15 MB | `street-combo__nm_0214-0224`, `street-fight-cars__nm_0500-0510`, `plaza-fight__dn_0818-0828`, `night-street-fight__nt_0755-0805` |
| S1 | group ring with telegraphs (hero + 5-7 enemies, mid-high camera) | 4K still at a ring moment | `group-fight-nm__nm_0223` |
| S2 | contact frame (hit-stop, small spark) | 4K still on a contact frame | `combo-hit-nm__nm_0217` |
| S3 | launcher / air juggle | 4K still while the victim is airborne | `air-combat-nm__nm_0248` |
| S4 | web strike / web shot line | 4K still with a strand out | `web-shooter-nm__nm_0244` |
| S5 | finisher beat (push-in) | 4K still at the cine peak | `symbiote-finisher__nm_0530-0538` (clip) |
| S6 | gunman aim line + brute silhouette | 4K stills | `street-fight-nm__nm_0501` |
| X1 | previous round vs this round | r01 `fight25_1080p60.mp4` vs r02 `fight30_1080p60.mp4` | - |
