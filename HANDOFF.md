# M5 Spider-Man migration — 2026-10-06

The owner authorized copying everything needed to develop, run and test Spider-Man from the M3 to the M5. Migration and offline preparation completed; no game/editor/commandlet launched. Owner playtest remains pending.

## Canonical M5 project
- ~/spider-man-2, branch codex/m5-migration-20261006, based on codex/owner-playtest-20261004 at 3ee7a938cfd330aa0c8de19c0f0123dc970933fe.
- Full remote game history/branches fetched. Base accepted integration is 7094940146da974955a6daed8b4d9ce3ea16cc26.
- Accepted generated Content: integrated city/water/look/life/traversal, complete characters r17, preserved TerrainR5b checkpoint. Original donor provenance remains in docs/migration/source-preview-handoff.txt and prepare.py.
- Prepared map: /Game/TerrainR5b/Maps/Manhattan_Terrain. Requested output 3840x2160, Cinematic, 100% scale, 30 FPS cap. These are settings, not measured runtime output or performance.
- Current R5b map composition predates city r11; current city asset files are present. Inspect the combination during the owner's first playtest.

## Supporting data now on M5
- ~/sm2-assets: raw GLBs and source textures.
- ~/spider-man-2/art/night1/characters: complete generated character sources.
- ~/sm2-n1/_scratch: character import inputs, terrain export/prep, showcase city export/textures, life vehicle/citizen imports, water inputs, reference clip, full-island export/textures.
- ~/sm2-n1/island: separate unfinished island worktree, codex/m5-island-20261006 at 9e3cfb0d; partial generated Content retained. Not merged or gameplay-ready.
- ~/spiderman-learnings: private reference repository on night1/refs plus full local refs library.
- ~/spiderbench: original author's newer browser version, detached at 64d957f92f005a1c1870070079351e30b2395661. Dependencies installed and browser build passed. Its night mode is NOT yet ported into Unreal.
- docs/migration/perf-working-tree.patch preserves the M3 perf checkout's uncommitted config deletion; not applied here.
- Claude continuation prompt and private policy cache: ~/Documents/Codex/m5-unreal-setup-20261006. Claude and GitHub auth were verified in the owner's GUI session; SSH Keychain isolation can falsely report unauthenticated. Do not export credentials or ask for sign-in solely from SSH auth output.

## Verification
10,473 transferred asset/reference/input files totaling 14,157,211,969 bytes match M3 SHA-256 checksums. The only source-side inventory extra is an intentionally excluded water stdout log. Git repository files and installed tools are additional to that count. No source assets are linked back to the M3 or external SD card.

Unreal 5.8.3 native WebHomageEditor build succeeded on M5 with Xcode 27. Manifest points to existing libUnrealEditor-WebHomage.dylib. -NoHotReload prevents unrelated open editors from causing a stale suffixed module manifest. prepare.py reports prepared_on_disk, missing=[], 25 suit references checked. Browser production builds passed for our project and upstream. npm reports one pre-existing high-severity advisory; dependencies were preserved, not upgraded in this migration.

No runtime, visual, controller, audio, FPS or owner-play acceptance is claimed. First authorized launch can still compile shaders. Existing M5 Blender/Unreal/model jobs were not touched; manual preview correctly refuses competing renderers.

## Commands (M5 only)
Check without opening:
```sh
cd ~/spider-man-2
source tools/m5/env.sh
python3 tools/owner_preview/prepare.py
python3 tools/owner_preview/play.py
```
Build without opening:
```sh
bash unreal/WebHomage/Scripts/build_editor.sh -MaxParallelActions=4 -NoUBA
```
After a new explicit owner request and live renderer/health/ownership review, the manual preview command is `python3 tools/owner_preview/play.py --launch`. Do not run it just because it appears here. It refuses other renderers/holders and honors shared PAUSED.

Next development job: use the provided Claude showcase brief; port upstream night while retaining accepted work, then improve sky/water/buildings/traversal within that scope. Do not restart the old many-branch loop. Legacy export scripts need shared GPU-admission review before any commandlet/render stage. Do not remove this prepared project or data while waiting for the owner's test.
