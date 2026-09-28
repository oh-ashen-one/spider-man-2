# skinfit: Tripo mesh to in-game suit skin

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](../../DISCLAIMER.md).

`skinfit.py` turns an unrigged Tripo GLB into a suit skin that plays every existing hero animation. It works in four steps:

1. **Pose fit.** It poses the game's own skinned hero mesh until it overlaps the Tripo mesh. The pose covers arm angle, elbow bend, limb lengths, stance and torso and head proportions, mirrored left and right, and is solved with scipy Powell against a two-way nearest-point distance.
2. **Weight transfer.** Every Tripo vertex takes skin weights from the nearest posed game vertices whose surface faces the same way. The top 4 joints are kept, then smoothed over the Tripo mesh.
3. **Un-pose.** It applies the exact inverse of linear blend skinning, so the Tripo mesh lands in the rig's bind pose. The round-trip error is zero.
4. **Write.** It writes a GLB with the game's exact joint nodes and inverse bind matrices, plus the new mesh and a 4096² WebP texture.

```
python3 tools/skinfit/skinfit.py ~/Downloads/claude.glb public/assets/skins/claude.glb --name ClaudeSuit
python3 tools/skinfit/skinfit.py IN.glb test.glb --with-anims   # standalone test character: ?char=/assets/skins/test.glb
```

At runtime, `src/game/systems/skinswap.js` binds the skin to the live hero skeleton, after checking the joint names, and hides the original body and lenses. Suits with a `skin` field in `src/game/systems/suits.js` use this path.

Results for the five AI suits:

| Suit | Surface gap before fit | Surface gap after fit |
|---|---|---|
| Claude | 7.4 cm | 3.0 cm |
| Codex | 8.1 cm | 2.9 cm |
| Gemini | 4.5 cm | 3.1 cm |
| Kimi | 6.2 cm | 3.3 cm |
| Qwen | 6.2 cm | 3.1 cm |

`backlogo.py` is **experimental and not applied**. Tripo copied the front chest logo onto the back of the Gemini and Qwen models, sculpted into the mesh as well as painted, so repainting the texture alone doesn't remove it. The better fix is to regenerate those two in Tripo with only the Front and Back slots filled.
