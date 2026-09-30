# P5 Combat: handoff after round 01

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See `DISCLAIMER.md`.

Branch `night1/combat`, worktree `~/sm2-n1/combat`. The UE MCP port is 8775 and the dev port is 5206; round 01 used neither editor nor MCP, and everything ran as headless commandlets plus `-game`. P5 owns `Source/WebHomage/Combat`,
`/Game/Combat`, `/Game/Tests/Combat`, `Scripts/build_combat.py` and `docs/night1/combat/`. Scratch: `/Users/midir/sm2-n1/_scratch/combat/`. Round evidence: `round-01/`
(`NOTES.md`, `COMPARE.md`, video, telemetry). No critic has scored it yet.

## Build and run (your editor closed)

```
python3 unreal/WebHomage/Scripts/build_combat.py                    # cpp, traversal (P3 script), characters (P2 script, staged P2 inputs), combat map; ~3 min
python3 unreal/WebHomage/Scripts/build_combat.py --steps combat     # only /Game/Combat + Combat_Street
docs/night1/combat/run_fight.sh logic  <out> docs/night1/combat/scripts/fight25.json          # -game -nullrhi, telemetry only (~40 s)
docs/night1/combat/run_fight.sh movie  <out> docs/night1/combat/scripts/fight25.json          # 1080p60 -dumpmovie, inside gpu_slot.sh capture
docs/night1/combat/run_fight.sh stills <out> docs/night1/combat/scripts/fight25.json 2.2,15.2 # native 4K stills, inside gpu_slot.sh capture
node docs/night1/combat/browser_fight.mjs docs/night1/combat/scripts/fight25.json <out>        # browser reference (port 5206, SwiftShader)
python3 docs/night1/combat/compare_logs.py <ue_out> <browser_out> COMPARE.md compare.json
python3 docs/night1/combat/freeze_script.py scripts/fight25_record.json <record_out>/fight_beats.jsonl scripts/fight25.json
```
Scripts: `fight25_record.json` contains reactive beats (`react: threat` = dodge when a threat is 0.08-0.25 s from contact, `react: free` = press once the hero is free).
`freeze_script.py` turns a record run into the fixed-time playback `fight25.json`. The replay is deterministic, and its event log is identical to the record run's.
Director flags: `-WHCmbScript= -WHCmbFight=mgb -WHCmbDist= -WHCmbOut= -WHCmbShots= -WHCmbShotName= -WHCmbQuit=`. All times are real seconds.
Live keys in `Combat_Street`: LMB attack (hold = launcher / air slam), F web shooter, E / MMB web strike, Q finisher, Z heal, R throw (not ported), C / Ctrl dodge.

## Code map (`Source/WebHomage/Combat`, port of `src/game/combat`)

| file | browser | what |
|---|---|---|
| `WHCombatDirector` | index.js + input.js | fight lifecycle, melee / gun tokens, slots, threats + spider-sense, hit-stop / slow-mo (global time dilation, real-time based), playerHit / enemyStrike / enemyShoot, web shots, combat camera layer + cinematic, script beats, telemetry |
| `WHCombatSpidey` | spidey.js | MOVES / POOLS / AIR / DASH_MAX 5.2 / NEAR 9, strike dash + flying kick, launcher, air combo, slam + ground pound, dive, web strike / yank, dodge (perfect = counter), web shooter, finisher, heal, hit / knockdown / get-up |
| `WHEnemy` | enemy.js | melee 50 / gunman 38 / brute 150 (scale 1.24), all 14 states, HIT_T / TELE, stumbles with hips root motion, yank, juggle, knock, wall / ground web pin, disarm (swap to the unarmed P2 mesh) |
| `WHClipStack` | poselayer.js | cross-fading clip stack (full-body cover pruning, upper-body mask) |
| `WHCombatAnim` | poselayer.js + enemy late() | `UWHCombatHeroAnim` (subclass of P3's `UWebTravAnimInstance`: combat stack over the traversal pose), `UWHEnemyAnim` (hips pinned, flinch / aim pitch) |
| `WHCombatFx` | fx.js | pooled basic-shape FX: flash / sparks / ring, dust, web strands, pellets, tracer / muzzle, splats, spider-sense streaks, heal |
| `WHCombatHero` | (C5 override) | `AWHCombatHero : AWebTravCharacter` (P3 file untouched) + `AWHCombatGameMode` |

Clips: hero `/Game/Traversal/HeroDev/<clip>` (P3's import of `spiderman.glb`), thugs `/Game/Characters/Thug/Anims/A_Thug_*`, loco `A_Street_walkStreet` + `A_Hero_jog/run`.
Meshes: P2 `SK_Street_{Thug_Bat,Tee_Bat,Beard_Pipe,Hood}` (melee), `SK_Street_{Thug,Hood}_Pistol` (gunmen), `SK_Street_Brute_Pipe` (brute).

## Integration with traversal (no P3 file edited): changes P3 should make

Currently the director ticks after the traversal pawn. While a combat move runs, it re-places the body every frame with `UWebTraversalComponent::Teleport`, and when a
move ends in the air it hands the fall back with `SetVelocityM`. It moves the P3 follow camera after the chase camera, and it binds its own keys. What P3 should add:
1. **Control-override hook** (browser `player.setControlOverride`): a delegate called before traversal integrates, returning the input and optionally an externally
   owned body (ground XY, or a kinematic air segment with collision). The per-frame `Teleport` now resets sub-state, ModeT, webs and velocity each frame.
2. **Public `ToAir(VelM)`** (browser `traversal.toAir`) and **`LaunchJump`**, for the Space jump-evade / jump-cancel. Also expose the sampled input (jumpPressed): the Space rules
   are not ported.
3. **Input swallowing**: combat must be able to consume E (strike vs zip), Q (finisher vs quick boost), C / Ctrl (dodge vs drop) and F (web shooter vs trick) on the frames it uses
   them. Now both fire in live play. Add an `I.combat` flag as well (fight-ready stance, no drop near enemies).
4. **Camera access**: a writable orbit yaw / pitch (`AddYaw`) plus `Shake` / `Impact`. Combat now keeps its own yaw offset and trauma on top of the chase camera.
5. Keep `UWebTravAnimInstance::CreateAnimInstanceProxy`, `FWebTravAnimProxy::Evaluate` / `PreUpdate` virtual, and keep `ClipRoot` public: combat subclasses them.
6. When P2's hero replaces HeroDev, the combat clip path follows `ClipRoot`. The `A_Hero_` prefix would need a name map.

## Manhattan (C)

The fight runs on the test street because the Manhattan build is about 12 minutes plus the city export. To add combat there, set `AWHCombatGameMode` as the map's game mode, or subclass
it in C's map. Start fights with `-WHCmbFight=` / a script, with the player start on the avenue. The director only needs P3's traversal world index (WHGround + building boxes).

## Known problems / next

- Visual: flat, hazy lighting on the test street; the camera sometimes gets too close to the hero; there is an abrupt cut into the finisher cinematic; the wall-pinned body reads poorly; the FX are basic shapes, not Niagara.
- Not ported: throwables, the Space jump-evade, the HUD, audio, the crime / reinforcement flow (fights come only from the script or the flag).
- The browser comparison diverges early (different world and RNG). A same-seed, same-layout comparison would need the browser fight moved onto a matching street.
- Round-01 gotchas: the module cannot use the `Json` module (Build.cs is integrator-owned; the Engine does not export it for linking), so there is a tiny JSON reader in the director.
  `build_editor.sh` sometimes leaves the manifest on a missing dylib (`ERROR ... missing`). Running it again fixes it.
