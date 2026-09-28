# crowdfit: Tripo citizens to crowd variants

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](../../DISCLAIMER.md).

`crowdfit.py` turns unrigged Tripo citizen GLBs into GPU-skinned crowd variants that walk, idle, film and react with the existing 27 crowd animations. Run it on the Studio, where Blender is installed.

```
python3 tools/crowdfit/crowdfit.py manifest.json --out public/assets/city/npc
```

`manifest.json` lists each citizen:

```
[{"glb": "~/Downloads/citizen_02.glb", "name": "02_leather_jacket", "female": false}, ...]
```

For each citizen it runs these steps:
1. **Decimate:** Blender (`decimate_lods.py`) cuts three detail levels: 5,000, 1,500 and 400 triangles.
2. **Pose fit:** it poses an existing crowd body onto the citizen (`m_tee` for men, `f_casual` for women), covering arm angle, limb lengths, stance, torso and head.
3. **Transfer:** it copies skin weights onto the citizen and un-poses the mesh into the crowd's rest pose (arms down, 1.70 m, facing +Z).
4. **Pack:** it writes `citizens.json`, `citizens.bin` and `citizens_atlas.webp`, with a 1024 px tile per citizen, 5 per row.

**At runtime:** `src/world/npc/crowd.js` loads the citizens if those files exist and adds them as extra textured crowd variants. They share the same skinning, clip blending, look-at, body-shape girth and instanced pools as the painted pedestrians. `?nocitizens` turns them off for A/B comparison.

**Test result:** two stand-in meshes each took about 50 seconds and fit to within about 4 cm.
