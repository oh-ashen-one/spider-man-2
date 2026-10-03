# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# Piece F (round 07): committed copy of the integrator's morning-build step `add_life.py` (_scratch/showcase/add_life.py, 2026-10-01),
# so F's rebuild of the integrated map follows the same recipe from committed files. Adds P6's /Game/Tests/Life/Life_Actors (traffic +
# crowd) as an always-loaded sublevel of /Game/Maps/Manhattan(_Midday|_Night). Idempotent. Headless commandlet of THIS worktree:
#   "<UnrealEditor>" <uproject> -run=pythonscript -script=<abs>/tools/perf_ue2/add_life.py -unattended -nullrhi -RenderOffScreen -NoSound
import unreal
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
for m in ('/Game/Maps/Manhattan', '/Game/Maps/Manhattan_Midday', '/Game/Maps/Manhattan_Night'):
    les.load_level(m)
    w = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    have = [l.get_path_name() for l in unreal.EditorLevelUtils.get_levels(w)]
    if not any('Life_Actors' in h for h in have):
        unreal.EditorLevelUtils.add_level_to_world(w, '/Game/Tests/Life/Life_Actors', unreal.LevelStreamingAlwaysLoaded)
    les.set_current_level_by_name(str(w.get_name()))
    ok = unreal.EditorLoadingAndSavingUtils.save_map(w, m)
    unreal.log('[showcase] %s life added saved=%s levels=%d' % (m, ok, len(unreal.EditorLevelUtils.get_levels(w))))
