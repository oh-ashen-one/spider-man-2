# Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation. See DISCLAIMER.md.
# Piece F (round 05, critic: "re-measure on the integrated map WITH traffic and crowd on"): a LOCAL copy of the integrated map with piece P6's
# city life (traffic + crowd + signals + probe = /Game/Tests/Life/Life_Actors, built by P6's UNCHANGED Scripts/build_life.py --steps content,map)
# streamed in as one more always-loaded sublevel. The shipped /Game/Maps/Manhattan is not modified.
#   /Game/PerfF/Life/Manhattan = /Game/Maps/Manhattan (+ its sublevels) + /Game/Tests/Life/Life_Actors   (perf_route.py spec: name@ini+variant:Life)
# Run in a headless commandlet of THIS worktree (editor + game closed, no GPU):
#   "<UnrealEditor>" <uproject> -run=pythonscript -script=<abs>/tools/perf_ue2/make_life_variant.py -unattended -nullrhi -RenderOffScreen -NoSound
import unreal, json, os

EAL = unreal.EditorAssetLibrary
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
SRC, DST, LIFE = '/Game/Maps/Manhattan', '/Game/PerfF/Life/Manhattan', '/Game/Tests/Life/Life_Actors'
LOG = os.environ.get('SM2_PERF_VAR_LOG', '/Users/midir/sm2-n1/_scratch/perf/life_variant.json')
for need in (SRC, LIFE):
    if not EAL.does_asset_exist(need): raise RuntimeError('missing ' + need)
# round 06: env SM2_PERF_LIFE_CROWD = 'prop=value;prop=value' (WHLifeCrowd UPROPERTYs in snake case, e.g. shadow_radius=3000;live_radius_high=14000, cm)
# and SM2_PERF_LIFE_TRAFFIC (WHLifeTraffic, same form): the variant streams F's COPY /Game/PerfF/Life/Life_Actors_F with those actor settings instead of
# P6's /Game/Tests/Life/Life_Actors (P6's level and C++ defaults are not modified; the settings are F's measured recommendation to P6).
OVR = {'WHLifeCrowd': os.environ.get('SM2_PERF_LIFE_CROWD', ''), 'WHLifeTraffic': os.environ.get('SM2_PERF_LIFE_TRAFFIC', '')}
applied = {}
if any(OVR.values()):
    COPY = '/Game/PerfF/Life/Life_Actors_F'
    if EAL.does_asset_exist(COPY): EAL.delete_asset(COPY)
    if not EAL.duplicate_asset(LIFE, COPY): raise RuntimeError('duplicate life level failed')
    unreal.EditorLoadingAndSavingUtils.load_map(COPY)
    for a in unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors():
        cls = a.get_class().get_name()
        for kv in [x for x in OVR.get(cls, '').split(';') if x]:
            k, v = kv.split('=', 1); cur = a.get_editor_property(k)
            nv = type(cur)(float(v)) if isinstance(cur, (int, float)) and not isinstance(cur, bool) else (v.lower() in ('1', 'true') if isinstance(cur, bool) else v)
            a.set_editor_property(k, nv); applied['%s.%s' % (cls, k)] = [cur, a.get_editor_property(k)]
    if not applied: raise RuntimeError('no life actor property applied: %s' % OVR)
    if not les.save_current_level(): raise RuntimeError('life copy not saved')
    LIFE = COPY
if EAL.does_asset_exist(DST): EAL.delete_asset(DST)
if not EAL.duplicate_asset(SRC, DST): raise RuntimeError('duplicate failed')
unreal.EditorLoadingAndSavingUtils.load_map(DST)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
have = [l.get_path_name() for l in unreal.EditorLevelUtils.get_levels(world)]
if not any(LIFE.split('/')[-1] + '.' in h or h.endswith(LIFE.split('/')[-1]) for h in have):
    unreal.EditorLevelUtils.add_level_to_world(world, LIFE, unreal.LevelStreamingAlwaysLoaded)
les.set_current_level_by_name(str(world.get_name()))
ok = unreal.EditorLoadingAndSavingUtils.save_map(world, DST)
levels = [l.get_path_name() for l in unreal.EditorLevelUtils.get_levels(world)]
json.dump({'map': DST, 'saved': bool(ok), 'levels': levels, 'life_level': LIFE, 'life_overrides': applied}, open(LOG, 'w'), indent=1)
print('[make_life_variant]', ok, levels, applied)
