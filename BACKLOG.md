# Backlog

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](DISCLAIMER.md).

## Suit selection page
- **Better animation on the suit page.** Today the hero holds one static idle frame on the preview stage. Ideas:
  - loop a proper idle or showcase animation
  - play a short pose flourish when a suit is equipped
  - smooth the camera move when switching cards
  - animate the transition between suits (fade or wipe) instead of an instant mesh swap

## Suit skins
- **Texture warning:** fix the `THREE.WebGLTextures: Trying to use 17 texture units while this GPU supports only 16` warning. The cause is the **original hero suit material** (`SpiderSuit`), not the skins. It samples boneTexture, uSymMask, uFabHex, uFabKnit, map, aoMap, envMap, dfgLUT, 6 shadow maps, normalMap, roughnessMap and metalnessMap, which is 17. The symbiote mask (`suits.js`) is the one that tips it over. Fix it by packing the fabric hex and knit detail into one texture, or by binding `uSymMask` only while the symbiote suit is worn.
- **Back logos:** Gemini and Qwen have the chest logo copied onto the back, sculpted into the mesh by Tripo. Regenerate both in Tripo with only the Front and Back slots filled, then re-run `tools/skinfit/skinfit.py`.
- Add PBR maps (normal, roughness) to the skins; Tripo exported colour textures only.

## 3D assets pipeline
See `concepts/CREATURES.md` for the full plan and polygon budgets.
- [x] Hero suits: 5 AI-logo skins, wearable in game
- [x] Citizens: 20 citizens plus 8 accessories are in the game and replace the painted crowd (concepts: 01 and 12-20 original, 02-11 from photos of real people who gave permission (photos stay out of the repo); waiting on Tripo models; accessory kit done
- [ ] Animals: 8 animals. Concepts are done; waiting on Tripo models
- [ ] Props: 16 items (throwables and street dressing). Concepts are done; waiting on Tripo models
- [ ] Thugs and brute: concepts not made yet

## Citizens (next)
- **Citizen animation pass** (owner: "we'll work on the animations for them later"). They use the crowd's 27 existing clips on the fitted meshes. Things to improve:
  - joint deformation at the armpits and crotch, where the A-pose to arms-down un-pose is large
  - per-citizen gait
  - accessory sway
- **Frame time with the full citizen crowd:** measure it in a real desktop session on the Studio. The atlas is 6144 by 4096.
- Tune accessory probabilities and placement per citizen if anything clips (big hair under hats, and so on).

## Street props and animals (Tripo pack 2, done 2026-09-28)

- Integrated 23 textured Tripo models plus 1 untextured (pigeon in flight, painted in code) through `tools/critterfit`.
- **Street:** hydrant, litter basket, bench, hot-dog cart, halal cart (about 40% of the cart spots), planter, mailbox, parking meter, a newsbox row (3 cabinets), trash-bag piles and the traffic drum. New: acorn lamps on the park paths and the promenade (they glow at night), sawhorses at the steam work zones, and shopping carts beside about 12% of the trash piles.
- **Fights:** the throwables are now the trash can, wooden crate, blue oil drum and traffic barrel.
- **Animals:**
  - Dog walkers walk a golden retriever or a French bulldog.
  - Pigeons use a standing model that pecks, and a flying model that flaps.
  - The waterfront flocks are now gulls.
  - New (`npc/fauna.js`): rats at the trash piles and dumpsters (they bolt and hide), squirrels on the park paths, and alley cats on the sidewalks. They react to Spider-Man and to `world.alarm`.
- **Debug switches:** `?nohq` (old models), `?nocritters`.
- **To do:**
  - Measure frame time in a real desktop session on the Studio (not over SSH).
  - Tune the critter density.
  - The pigeon-in-flight Tripo export has no texture; a textured re-export would replace the painted tile.
  - The streets still use the old procedural lamp, busstop, kiosk and bike rack.
  - A jaywalking-rat moment would be fun.
  - Verification render recipe: export each pack item to PLY with atlas or part colours and render it in Blender workbench (see the session's `/tmp/hqview.py` pattern).
