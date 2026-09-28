# Citizens: Tripo guide and mix-and-match plan

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](../../DISCLAIMER.md).

These are ten original New York pedestrians, plus a kit of eight accessories any of them can wear. Together they replace the current crowd models. They were generated with Higgsfield Nano Banana Pro as four-view turnaround sheets, the same way as the hero suits. The prompts are in `prompts/`.

| Folder | Who |
|---|---|
| `01_retired_gent` | Original character: tall, slim man in his 70s, trench coat, flat cap, round glasses |
| `02_leather_jacket` | Leather bomber over a black hoodie, dark jeans, belt chain, boots |
| `03_white_tee` | Styled hair and beard, white tee, striped linen trousers, silver chain |
| `04_blue_sweatshirt` | Long dark hair, oversized blue sweatshirt, light jeans |
| `05_black_tee` | Dark wavy hair, black tee, black trousers and sneakers |
| `06_chrome_shades` | Curly bleached-tip hair, spiky chrome shades, black hoodie, cargo pants. Hair colour is split between views; re-roll with plain dark curls if Tripo struggles |
| `07_black_graphic_tee` | Full beard, black tee with a small chest print, layered chains |
| `08_black_suit` | Glasses, black suit and tie |
| `09_kurta_waistcoat` | Full beard, navy waistcoat over a blue kurta, tan trousers, brown boots |
| `10_silver_tie` | Glasses and beard, black suit, pale blue shirt, silver tie |
| `11_graphic_tee_bonnet` | Satin bonnet, beard, oversized graphic tee, joggers |

Citizens 02 to 11 are based on real people in the owner's life, who have given full permission to use their likeness in this game. Their source photos stay out of this public repo (`_photos/` is git-ignored). Prompts are in `prompts/real_people/`.

Each folder contains exactly the four images to upload: `front.png`, `left.png`, `back.png` and `right.png`. The combined turnaround sheets live in `_sheets_reference_only/`. **Never upload a combined sheet to Tripo.** It builds four separate people. In `left.png` the character faces left in the image, and in `right.png` they face right. That is Tripo's slot convention; the opposite naming gave the Qwen suit a face on the back of its head. `contact_sheet.jpg` shows all ten at once.


## Tripo: citizens

1. In **Generate Model**, click the **second icon** in the input row (the cube) for multi-view. Upload the four views from one folder into the matching slots. Tripo shows them as Front on top, then Left, Right and Back along the bottom, and leave **Generate Multi-Views** off. If there is no multiview option, use **Image to 3D** with `front.png`.
2. Settings: newest model, **HD PBR texture**, full detail, keep the A-pose.
3. **Skip auto-rig.** Claude moves each citizen onto the crowd's own 18-bone skeleton and bakes the 27 crowd animations for it.
4. Export GLB as `citizen_01.glb` through `citizen_11.glb`, into `concepts/citizens/tripo/`.

Don't worry about polygon count in Tripo. Hundreds of citizens are on screen at once, so Claude cuts every model down to three levels of detail in Blender: about 5,000 triangles up close, about 1,500 in the middle distance and about 400 far away.

## Tripo: accessories

In `accessories/` there is one image per item. The combined kit is in `_sheets_reference_only/accessory_kit.png`.

| Hats | Bags | Other |
|---|---|---|
| `baseball_cap`, `beanie`, `fedora`, `bucket_hat` | `backpack`, `messenger_bag` | `headphones`, `sunglasses` |

Use **Image to 3D** with one image each, HD texture. Export as `acc_baseball_cap.glb` and so on, into `concepts/citizens/tripo/`.

## How mix and match works in the game

Tripo gives each citizen one fused mesh, so shirts can't swap between different bodies. Variety comes from three layers stacked on top of the 10 bodies.

1. **Recolouring.** Claude paints a region mask for each body in Blender, marking top, bottom, shoes, hair and skin. The crowd shader then tints each region per person from curated palettes. The current game already does this with 15 material regions, so the pipeline exists.
2. **Accessories.** Each accessory is attached to a bone:
   - hats, sunglasses and headphones to the head
   - the backpack and messenger bag to the chest

   Each citizen randomly gets zero to two of them. Some combinations are ruled out:
   - no second hat on someone who already wears one (01, 03, 06, 08)
   - no backpack on the teen, who already has one
   - no hat over the hijab
3. **Scale and gait.** Each person gets a small random change in height and girth, plus their own walk speed and animation phase, as the current crowd does.

Put together, 10 bodies × 6 palettes × about 20 accessory combinations gives over a thousand distinct-looking people. The game already stops two people with the same outfit and hairstyle from appearing within 20 m of each other, and that rule carries over.

## Order after the models arrive

1. Fit the Tripo meshes onto the 18-bone crowd skeleton, make the three levels of detail, and bake the animation texture.
2. Paint the region masks and add the new palettes.
3. Attach the accessories to their bones and add the compatibility rules.
4. Check before and after in the street-level fixed screenshot shots, and check frame time with a full crowd.
