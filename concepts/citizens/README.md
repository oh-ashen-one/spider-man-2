# Citizens: Tripo guide and mix-and-match plan

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](../../DISCLAIMER.md).

These are ten original New York pedestrians, plus a kit of eight accessories any of them can wear. Together they replace the current crowd models. They were generated with Higgsfield Nano Banana Pro as four-view turnaround sheets, the same way as the hero suits. The prompts are in `prompts/`.

| Folder | Who |
|---|---|
| `01_retired_gent` | Tall, slim East Asian man in his 70s: trench coat, flat cap, round glasses |
| `02_sundress_mom` | Plus-size Black woman in her 30s: afro puff, yellow floral sundress, denim jacket |
| `03_construction_worker` | Short, stocky Latino man in his 40s: hard hat, hi-vis vest, flannel shirt, work boots |
| `04_teen_skater` | Lanky South Asian teen: purple hoodie, cargo shorts, backpack, headphones |
| `05_executive` | Athletic white woman in her 40s: platinum bob, navy pantsuit, heels, laptop bag |
| `06_lumberjack_hipster` | Heavyset ginger-bearded man in his 30s: beanie, flannel shirt, puffer vest |
| `07_hijabi_student` | Young Middle Eastern woman: pink hijab, sunglasses, olive trench coat, wide jeans |
| `08_dapper_elder` | Elderly Black man with a round face and pencil moustache: tweed three-piece suit, fedora, bow tie |
| `09_marathon_runner` | Tall, muscular Pacific Islander man: running tank top, shorts, neon shoes |
| `10_punk_artist` | Petite Southeast Asian woman: pink bob, studded leather jacket, tartan skirt, combat boots |

Each folder contains `sheet.png` (the full turnaround) and `front.png`, `left.png`, `back.png` and `right.png`. The left image shows the character's left side, so they face right. `contact_sheet.jpg` shows all ten at once.

The first draft of the dapper elder looked like a real famous actor, so he was regenerated with an explicitly original face. Every character is original.

## Tripo: citizens

1. Use **Multiview to 3D** with the four views from one folder. If there is no multiview option, use **Image to 3D** with `front.png`.
2. Settings: newest model, **HD PBR texture**, full detail, keep the A-pose.
3. **Skip auto-rig.** Claude moves each citizen onto the crowd's own 18-bone skeleton and bakes the 27 crowd animations for it.
4. Export GLB as `citizen_01.glb` through `citizen_10.glb`, into `concepts/citizens/tripo/`.

Don't worry about polygon count in Tripo. Hundreds of citizens are on screen at once, so Claude cuts every model down to three levels of detail in Blender: about 5,000 triangles up close, about 1,500 in the middle distance and about 400 far away.

## Tripo: accessories

In `accessories/` there is one image per item, plus `kit_sheet.png` with all eight:

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
