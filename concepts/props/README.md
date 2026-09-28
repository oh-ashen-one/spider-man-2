# Props: Tripo guide

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](../../DISCLAIMER.md).

This folder holds sixteen New York street objects, one image each, made with Higgsfield Nano Banana Pro. Upload each image on its own with Tripo's **Image to 3D** (the first icon), with HD texture. Export as `prop_<name>.glb`, for example `prop_fire_hydrant.glb`, into `concepts/props/tripo/`.

## `throwables/`: objects Spider-Man can web up and throw

The first three replace the box-and-canvas versions the combat system spawns today (`src/game/combat/props.js`). The rest are new throwables.

| File | Object |
|---|---|
| `litter_basket.png` | Green wire-mesh public litter basket |
| `wooden_crate.png` | Weathered shipping crate |
| `oil_drum.png` | Dented blue oil drum |
| `trash_bags.png` | Pile of black garbage bags |
| `traffic_barrel.png` | Orange and white construction barrel |
| `newspaper_box.png` | Red newspaper vending box, no brand |
| `fire_hydrant.png` | Red cast-iron fire hydrant |
| `parking_meter.png` | Single-head parking meter |

## `street/`: street dressing

| File | Object |
|---|---|
| `hot_dog_cart.png` | Hot dog cart with a striped umbrella |
| `halal_cart.png` | Halal food cart. It has some garbled sign text; Claude can repaint the texture |
| `park_bench.png` | Green slatted bench with cast-iron legs |
| `police_barricade.png` | Blue sawhorse barricade, no text |
| `mailbox.png` | Blue curbside mailbox, no logos |
| `concrete_planter.png` | Round planter with a shrub |
| `shopping_cart.png` | Metal shopping cart |
| `street_lamp.png` | Cast-iron lamp post |

**How they get into the game:** Claude scales each model to real size and makes a far LOD, with a dithered cross-fade as the current props use. Collision is emitted by the same call that places the prop. Street props are placed through the existing instancing pool, so hundreds of benches, hydrants and meters cost a few draw calls. Throwables also get a simple collision box and mass for the throw arc.

The combined kit images are in `_sheets_reference_only/`, for reference only.
