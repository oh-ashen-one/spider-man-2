# critterfit

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](../../DISCLAIMER.md).

This tool turns textured Tripo GLBs into the game's street props and animals. It runs on the Studio:

```
python3 tools/critterfit/critterfit.py tools/critterfit/manifest.json [--only props_hq|fauna]
```

It builds two packs. Each pack is one `.json` + `.bin` pair plus one texture atlas with a 1024 px tile per item:

| Pack | Output | Used by |
|---|---|---|
| `props_hq` | `public/assets/city/props/` | `src/world/props.js` (street furniture pools) and `src/game/combat/props.js` (fight throwables) |
| `fauna` | `public/assets/city/npc/` | `npc/crowd.js` (dogs), `npc/pigeons.js` (pigeons and gulls), `npc/fauna.js` (rats, squirrels, cats) |

`src/world/hqassets.js` loads the packs. If a pack is missing, or the URL has `?nohq`, every system falls back to its old procedural models.

## Manifest fields

| Field | Meaning |
|---|---|
| `glb` | The source model. Tripo's front is +X; the default `yaw: -90` turns it to face +Z in the game. |
| `yaw` | Add `:weld` (for example `"-90:weld"`) for fur-card meshes that stall decimation, such as the squirrel. The option welds uv seams and splits non-manifold edges. Don't use it on clean meshes: at low triangle counts it collapses them worse. |
| `size` | Real-world size in metres, one of: `h` (height), `l` (length along the facing), or `w` (width along x). |
| `lods` | Triangle targets. With two LODs, props cross-fade at 45 m. Thin props (the meter and the sawhorse) keep one LOD, because the pole vanishes when decimated. |
| `part` | Props only: the `partmat.js` material part, which sets roughness and metalness. |
| `rig` | Animals only. `quadruped` takes `leg_v`, `tail_u`, `head_u`, `head_v` and `mid_u`, in normalised coordinates: `u` runs from 0 at the rear to 1 at the nose, `v` from 0 to 1 of the height. `bird` takes `head_u` and `head_v`. `flight` takes `root`, the wing root as a fraction of the span. Each vertex gets a part id and a weight 0..1. The weight ramps across part boundaries, so the joints bend instead of tearing. |
| `paint` | For a GLB without a texture: a painted top-view tile (`pigeon` or `gull`) with planar uvs. The pigeon-in-flight model is the only one that needs it. |

## Checking the output

Render every item, with LOD1 and with the rig parts coloured, before shipping. Decimation can break a mesh without any error. See the `hqview` recipe in BACKLOG.md.
