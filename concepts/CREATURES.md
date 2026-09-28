# Living creatures: upgrade plan

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](../DISCLAIMER.md).

**Goal:** make custom, higher-quality 3D models for every living creature in the game, and keep the buildings as they are. The pipeline is the same for each one:

1. Claude generates a concept image with Higgsfield: front view, neutral pose, flat grey background.
2. The owner turns it into a model in the Tripo web app.
3. Claude fits the model into the game in Blender on the Studio. That means scaling it, transferring weights onto the game's existing skeleton, making levels of detail, and exporting a GLB.
4. Claude checks it in the fixed screenshot shots.

## Inventory

| Creature | Now | How it animates | Budget for the new model | Concepts needed |
|---|---|---|---|---|
| **Hero** | `spiderman.glb`: 27k verts, 50k tris, 4096² textures | 58-bone skeleton, 79 baked clips, about 15 procedural layers | About 50k tris, 4096² PBR textures | **5 done**, four-view sheets in `skins/<name>/` |
| **Thugs** (melee, gunman) | `thug.glb`: 30k verts, 56k tris, same 58-bone skeleton, 3 recoloured textures | 13 thug clips plus the hero's walk, jog and run | About 30–40k tris, 2048² textures | 3 to 4 street-thug looks |
| **Brute** | Same thug mesh scaled ×1.24, with its own texture | Same as thugs | Its own heavier body, about 40k tris | 1 |
| **Pedestrians** | `people.json/.bin`: 24 outfits × 3 LODs, faces from a 32-face atlas | 18-bone skeleton, 27 clips baked into a texture and skinned on the GPU, hundreds on screen | **Near LOD about 4–6k tris**, mid about 1.5k, far about 400; one shared texture atlas | **10 done**, four-view sheets plus an 8-item accessory kit in `citizens/` |
| **Dogs** | Rigid-part mesh with 3 LODs | Legs, tail and head moved in the vertex shader | About 2–3k tris, split into body, legs, tail and head | 2 to 3 breeds |
| **Pigeons** | Instanced, up to 700 on screen | Wing flap in the vertex shader | **About 150–300 tris** | 1 |

**Tripo settings by group:**
- **Hero, thugs, brute:** export at full detail and skip auto-rig. We reuse the existing 58-bone skeleton, so all current animations keep working.
- **Pedestrians:** export full detail. Claude decimates each model into 3 LODs and moves it onto the 18-bone crowd skeleton, which is re-baked into the animation texture. With hundreds on screen, polygon budget matters more than detail.
- **Dogs and pigeons:** export full detail. Claude splits the parts and decimates hard, because the shaders animate them.

## Order

1. **Hero skins.** Concepts are done; waiting on the Tripo models.
2. **Thugs and brute.** Same skeleton as the hero, so the fit is the easiest.
3. **Pedestrians.** The biggest visual impact at street level, and the hardest to fit because of the performance budget.
4. **Dogs and pigeons.**

Each step ends with before and after renders in the fixed screenshot shots, plus a frame-time check. 60 fps stays part of the brief.
