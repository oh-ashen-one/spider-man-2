# AI-logo hero suits: Tripo guide

> A homage game. This is not an official Marvel game. The AI logos are a tribute, with no affiliation or endorsement. See [DISCLAIMER.md](../../DISCLAIMER.md).

There are five hero suits. Each is a fitted spandex-and-rubber superhero suit with a full fabric mask and an AI model's logo as the chest emblem. Every suit has a four-view character sheet plus the four views as separate images, ready for Tripo's multiview input.

| Folder | Look | Chest emblem |
|---|---|---|
| `claude/` | Matte black spandex, glossy terracotta-orange rubber side panels, orange lenses | Claude spark |
| `codex/` | White spandex with glossy black rubber panels and boots, silver lenses | OpenAI Codex knot |
| `gemini/` | Glossy red and deep blue with raised silver seams, silver lenses | Gemini sparkle star |
| `kimi/` | Crimson and navy with a carbon-weave texture, amber-gold lenses | Kimi "K" badge |
| `qwen/` | Bright red and royal blue with violet piping, violet lenses | Qwen pinwheel hexagon |

Each suit folder contains exactly the four images to upload: `front.png`, `left.png`, `back.png` and `right.png`. The combined turnaround sheets live in `_sheets_reference_only/`.

> **Never upload a combined sheet to Tripo.** It reads all four views as one scene and builds four separate people.

**Which side is which (Tripo's convention):** in `left.png` the character faces **left** in the image, and in `right.png` they face **right**. The first Qwen upload used the opposite naming and came out with a face on the back of its head, so every folder was swapped to match Tripo's slots. If a model still grows a second face or looks twisted, generate again with only the Front and Back slots filled. Kimi's side views are mirrors of each other, which is safe because the suit is symmetrical.

`contact_sheet.jpg` shows all five suits and all four views at once.

## What to do in Tripo (web app)

1. In **Generate Model**, click the **second icon** in the input row (the cube) to switch to multi-view. Upload `front.png`, `left.png`, `back.png` and `right.png` from one folder into the matching slots. Tripo shows them as Front on top, then Left, Right and Back along the bottom. Leave **Generate Multi-Views** off, because the views already exist.
   - If there is no multiview option, use **Image to 3D** with `front.png` only.
2. Use these settings. They are not checked against the current Tripo interface, so pick the closest match:
   - **Model:** the newest / highest-quality version.
   - **Texture:** on, **HD**, **PBR** on.
   - **Mesh:** full detail, about **50,000 triangles**, which matches the current hero's 56,000. Leave "smart low poly" off.
   - **Pose:** keep the input A-pose.
3. **Skip auto-rig.** Claude transfers the game's existing 58-bone skeleton and weights onto each mesh in Blender, so all 79 current animations work straight away.
4. **Export GLB** with embedded textures, named `skin_claude.glb`, `skin_codex.glb`, `skin_gemini.glb`, `skin_kimi.glb` and `skin_qwen.glb`. Drop them in `concepts/skins/tripo/` or send them to Claude.

**If Tripo asks for a text prompt**, paste the matching line:

```
claude:  superhero in a fitted matte black spandex suit with glossy terracotta-orange rubber side panels, full fabric mask with orange eye lenses, orange starburst chest emblem, A-pose, game-ready character
codex:   superhero in a fitted white spandex suit with glossy black rubber panels and black boots, full fabric mask with silver eye lenses, black knot chest emblem, A-pose, game-ready character
gemini:  superhero in a fitted glossy red and deep blue spandex suit with raised silver seams, full fabric mask with silver eye lenses, blue-purple four-point star chest emblem, A-pose, game-ready character
kimi:    superhero in a fitted crimson and navy spandex suit with carbon-weave texture, full fabric mask with amber-gold eye lenses, white K badge chest emblem, A-pose, game-ready character
qwen:    superhero in a fitted red and royal blue spandex suit with violet piping, full fabric mask with violet eye lenses, violet pinwheel hexagon chest emblem, A-pose, game-ready character
```

## How these were made

- **Model:** Higgsfield **Nano Banana Pro**, 21:9 at 4K. GPT Image 2 blocked every fitted-suit prompt.
- **Prompts:** in `prompts/`. `sheet_template.txt` is shared by all five, and `costumes.json` holds each suit's description.
- **What gets blocked:** image models refuse anything that reads as the licensed character. Three combinations trigger it:
  - red and blue with big white eye lenses in black frames
  - thick black trim or web lines
  - the words "Spider-Man" or "spider"

  Each suit gets its own lens colour and seam style instead.
- **Splitting:** `tools/split_sheet.py` cuts a sheet into the four views.

## Status: in the game

All five suits are fitted and wearable from the in-game suit menu:
- **Skin files:** `public/assets/skins/<id>.glb`
- **Runtime code:** `src/game/systems/skinswap.js`
- **Fitting tool:** `tools/skinfit/` (see its README)
- **Suit menu cards:** `public/assets/ui/suits/<id>.webp`

**Known issue:** the Gemini and Qwen models have their chest logo copied onto the back, sculpted into the mesh by Tripo. To fix it, regenerate those two in Tripo with only the **Front** and **Back** slots filled, then run `skinfit.py` on the new GLB.
