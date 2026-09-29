# Animals: Tripo guide

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](../../DISCLAIMER.md).

This folder holds eight city animals as four-view sheets, made with Higgsfield Nano Banana Pro. They replace the current box-shaped pigeons and dogs, and add wildlife the city doesn't have yet.

| Folder | Animal | Where it lives in the game |
|---|---|---|
| `pigeon` | Rock pigeon, standing | Sidewalks, plazas, rooftops; flocks burst up when Spider-Man lands |
| `pigeon_flight` | Rock pigeon, wings spread | The flying version of the same bird, for take-off and circling |
| `sewer_rat` | Big NYC sewer rat, on all fours | Alleys, subway entrances, trash piles; runs from the player |
| `squirrel` | Eastern grey squirrel | Central Park and street trees |
| `seagull` | Herring gull | Waterfront, piers, ferry terminals |
| `alley_cat` | Orange tabby | Alleys, fire escapes, stoops |
| `golden_retriever` | Golden retriever with a red collar | Walked by pedestrians (replaces the current rigid dog) |
| `french_bulldog` | Fawn French bulldog | Walked by pedestrians |

**Uploading:** each folder holds exactly the four images to upload. In Tripo's **Generate Model**, click the **second icon** (the cube) for multi-view. Put `front.png`, `left.png`, `right.png` and `back.png` into the matching slots, and leave **Generate Multi-Views** off. In `left.png` the animal faces left in the image, and in `right.png` it faces right. That is Tripo's slot convention. The combined sheets in `_sheets_reference_only/` are for reference only. **Never upload a combined sheet.** Tripo turns it into four animals.

**Settings:** HD texture, full detail, **no auto-rig**. Export as `animal_<folder>.glb`, for example `animal_sewer_rat.glb`, into `concepts/creatures/tripo/`.

## How they get into the game

The game animates these in the vertex shader, the same way it already moves the pigeons and dogs. That keeps hundreds on screen cheap.

- **Parts:** Claude splits each model in Blender into parts: body, head, legs, tail and wings. It gives each part a pivot for the shader to swing: leg pairs step with the gait, tails wag or trail, heads bob.
- **Levels of detail:**
  - Pigeons and gulls come down to about 200–300 triangles, because up to 700 pigeons are on screen.
  - Rats, squirrels and cats come down to about 800 triangles.
  - Dogs come down to about 2,500 triangles.
- **Pigeon pose switching:** the standing and flying pigeons swap mid-flight, so a flock can land, walk and take off.
- **New behaviour:**
  - Rats scatter from the player and from falling enemies.
  - Squirrels run up tree trunks in the park.
  - Gulls circle the piers.
  - Cats sit on stoops and fire escapes.
