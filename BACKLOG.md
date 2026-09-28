# Backlog

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](DISCLAIMER.md).

## Suit selection page
- **Better animation on the suit page.** Today the hero holds one static idle frame on the preview stage. Ideas:
  - loop a proper idle or showcase animation
  - play a short pose flourish when a suit is equipped
  - smooth the camera move when switching cards
  - animate the transition between suits (fade or wipe) instead of an instant mesh swap

## Suit skins
- **Texture warning:** find and fix the `THREE.WebGLTextures: Trying to use 17 texture units while this GPU supports only 16` warning. It appears while an AI-logo skin is worn.
- **Back logos:** Gemini and Qwen have the chest logo copied onto the back, sculpted into the mesh by Tripo. Regenerate both in Tripo with only the Front and Back slots filled, then re-run `tools/skinfit/skinfit.py`.
- Add PBR maps (normal, roughness) to the skins; Tripo exported colour textures only.

## 3D assets pipeline
See `concepts/CREATURES.md` for the full plan and polygon budgets.
- [x] Hero suits: 5 AI-logo skins, wearable in game
- [ ] Citizens: 01 (retired gent) concept done; 02-11 made from photos of real people who gave permission (photos stay out of the repo); waiting on Tripo models; accessory kit done
- [ ] Animals: 8 animals. Concepts are done; waiting on Tripo models
- [ ] Props: 16 items (throwables and street dressing). Concepts are done; waiting on Tripo models
- [ ] Thugs and brute: concepts not made yet
