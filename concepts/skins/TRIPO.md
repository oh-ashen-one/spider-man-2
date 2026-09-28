# AI-logo suits: Tripo guide

> A homage game. This is not an official Marvel game. The AI logos are a tribute, with no affiliation or endorsement. See [DISCLAIMER.md](../../DISCLAIMER.md).

Five hero suit concepts, generated with Higgsfield (GPT Image 2, 1744×2336). Each has a different colour scheme and helmet, and an AI model's logo as the chest emblem.

| File | Colours | Helmet | Chest emblem |
|---|---|---|---|
| `suit_claude.png` | Matte black, terracotta-orange armour accents | Wide glowing orange visor band | Claude spark |
| `suit_codex.png` | Pure black and white | White helmet, black glass faceplate | OpenAI Codex knot |
| `suit_gemini.png` | Bright red and deep blue, silver trim | Silver mirrored wraparound visor | Gemini sparkle star |
| `suit_kimi.png` | Dark crimson and navy, armoured knees and shoulders | Amber-gold mirrored visor | Kimi "K" badge |
| `suit_qwen.png` | Bright red and royal blue, black trim | Black faceplate, white glowing slit | Qwen hex star |

Every image uses the same framing on purpose: front view, the game rig's A-pose, flat grey background, even light. That keeps all five Tripo models at the same proportions, so they swap onto one skeleton. The exact prompts are in `prompts.json`.

## What to do in Tripo (web app)

For each image:

1. Choose **Image to 3D** and upload one `suit_*.png`.
2. Use these settings. They are not checked against the current Tripo interface, so pick the closest match:
   - **Model:** the newest / highest-quality version.
   - **Texture:** on, **HD** texture, **PBR** on.
   - **Mesh:** keep full detail. A target of about **50,000 triangles** matches the current hero, which has 56,000. Leave "smart low poly" off; we decimate later if needed.
   - **Pose:** A-pose / keep the input pose. Don't let Tripo re-pose the character.
3. **Skip auto-rig.** The game already has a 58-bone skeleton and 79 animations. We will transfer the existing skin weights onto the new mesh in Blender, so every animation works straight away. A Tripo rig would be thrown away.
4. **Export GLB** with embedded textures.
5. Name the files `skin_claude.glb`, `skin_codex.glb`, `skin_gemini.glb`, `skin_kimi.glb` and `skin_qwen.glb`. Drop them in `concepts/skins/tripo/` in this repo, or send them to Claude.

**If Tripo shows a text prompt box** (image + prompt mode, or retexture), paste the matching line:

```
claude:  full-body superhero in a matte black suit with terracotta-orange armor panels, glowing orange visor helmet, orange starburst chest emblem, A-pose, game-ready character
codex:   full-body superhero in a black and white suit, white helmet with black glass faceplate, black interlocking knot chest emblem, A-pose, game-ready character
gemini:  full-body superhero in a glossy red and deep blue suit with silver trim, silver mirrored visor helmet, blue-purple four-point star chest emblem, A-pose, game-ready character
kimi:    full-body superhero in a crimson and navy armored suit, amber-gold visor helmet, white K badge chest emblem, A-pose, game-ready character
qwen:    full-body superhero in a red and royal blue suit with black trim, black faceplate helmet with white glowing slit, violet hexagon star chest emblem, A-pose, game-ready character
```

**If the back comes out bad:** Tripo guesses the back from a single front image. A multiview option (front, side, back) would give a better back. Ask Claude to generate matching back and side views of any suit from the same prompt.

## What happens after (Claude, in Blender on the Studio)

1. Import each GLB, scale it to the game rig's 1.79 m height, and line it up with the rig's A-pose.
2. Transfer the skin weights from the existing hero mesh onto the new mesh, then fix the shoulders, hips and fingers by hand where needed.
3. Re-export with the same 58-bone armature and all 79 clips, one GLB per skin.
4. Add the skins to the in-game suit menu (`src/game/systems/suits.js`). Check them in the fixed screenshot shots under each time-of-day preset.
