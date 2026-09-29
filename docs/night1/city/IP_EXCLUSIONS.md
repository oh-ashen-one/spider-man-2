# P1 City: IP exclusions (Unreal port only)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Owner rule (2026-09-29): we copy nothing. The Times Square ad atlas `public/assets/city/tex/ts_ads.webp` and the storefront sign atlas
`ts_signs.webp` came from the upstream browser project and contain cells with Marvel-universe names and brands from the real game.
The browser atlas files are **not modified**. In the Unreal port `tools/export/prep_textures.py` calls `tools/export/ip_sanitize.py`,
which overwrites every excluded cell of the Unreal-side PNG copy with the pixels of another original-brand cell of the same
orientation (a UV-slot remap on the Unreal side). The table in `ip_sanitize.py` is the single source of truth; this page mirrors it.

Atlas layout (from `src/world/timessq.js`): `ts_ads.webp` 4096 x 4096, top half 64 landscape cells 512 x 256 (8 x 8, index = row * 8 + col),
bottom half 64 portrait cells 256 x 512 (16 x 4, index = row * 16 + col). `ts_signs.webp` 2048 x 2048, 64 signs 512 x 128 (4 x 16).

## ts_ads.webp: excluded cells and what replaces them

| kind / cell | content that is excluded | replaced by |
|---|---|---|
| L 0 | OSCORP, "Tomorrow, Engineered" | L 55 (Sonara headphones) |
| L 1 | RE-ELECT OSBORN, "Safe Streets. Strong City." | L 63 (Harborline insurance) |
| L 2 | THE DAILY BUGLE, cafe / newspaper | L 52 (Daybreak Roasters) |
| L 3 | ROXXON, "Powering New York" | L 53 (Volterra E7) |
| L 22 | EMPIRE STATE UNIVERSITY, "Enroll for Fall" | L 45 (Arcline Book) |
| L 26 | FROSTED HALOS, "Part of a Heavenly Breakfast" | L 43 (Citrus & Co) |
| L 33 | BOTANICA, "Now Playing, Majestic Theatre" | L 46 (Dinosaurs Alive) |
| L 34 | FROSTED HALOS, "Start Bright" | L 20 (Big Apple Burger) |
| L 39 | HELL'S KITCHEN BLUES, "New Season Streaming" | L 41 (Neon Racers) |
| L 60 | THE DAILY BUGLE, "New York's News" | L 59 (New York Knights) |
| L 27 | COLTEX SPORT (sneaker brand; round-04 critic: too close to the real game's COLEXCO) | L 4 (Lumen X5) |
| P 27 | COLTEX - "Own the Court" (same brand, portrait cell) | P 8 (Kinetix, "Rise Above") |
| P 38 | COLEXCO - "Run the City" (near-copy of the real game's brand) | P 15 (Skyward Air) |
| L 35 | COLEXCO SPORT (red-on-white sneaker ad; the "COLEX SPOR..." banner in S6, found after the round-04 critic note) | L 47 (Big Apple Tours) |
| P 6 | OSCORP, "A Healthier Tomorrow" | P 20 (Spark) |
| P 7 | DAILY BUGLE, "Read All About It" | P 22 (Ashby & Cole) |
| P 13 | ROXXON, "Fueling Tomorrow" | P 31 (Sol Airways) |
| P 39 | FROSTED HALOS | P 49 (Chasing Waves) |
| P 41 | HYDRA PRO | P 18 (Glacier Spring) |

Reasons: Oscorp, Osborn, Roxxon, Daily Bugle, Empire State University and Hydra are Marvel-universe names; Frosted Halos and Botanica are
brands from the real game (named by the critic, round 03); "Hell's Kitchen Blues" points at the Marvel / Netflix Hell's Kitchen material.

## ts_signs.webp

| cell | excluded | replaced by |
|---|---|---|
| S 48 | HOTEL MIRA (brand from the real game) | S 15 (HOTEL ASTORIA) |

## Reviewed, kept

All other cells were read (OCR of every cell plus a visual pass): fictional brands only (Kinetix, Coltex, Colexco, Nova, Zest, Fizzo,
Vantor, Sonara, Harborline, Meridian Trust, Skyward Air ...). Not excluded on purpose, owner may still veto: the "Majestic Theatre" show
ads (Gilded Fox, Queen of Hearts), "Iron Borough", "Nova" products (NOVA is also a Marvel name but a generic brand word here),
`city_signart.webp` (period ghost signs: Knickerbocker, Fulton Warehouse ...; no IP found) and `signs.png` (facade storefront signs:
generic trades plus a "CHASE BANK" cell, a real-world brand, not Marvel / game IP). The Times Square news ticker text
(`ts_ticker.webp`) mentions a "MASKED HERO" heist headline (generic).

Not used in the Unreal port but listed for whoever ports traffic (P6): `vehicles_atlas2.webp` carries "DAILY BUGLE - THE TRUTH, EVERY
MORNING" and "A HEALTHIER TOMORROW" (Oscorp) livery cells; exclude them the same way (`ip_sanitize.py` has the pattern).

## Round 05: original signage (nothing copied)

The street-level kit (`tools/export/street_kit.py`, `tools/export/gen_street_signs.py`) draws its own fascia boards and awning valances from
invented generic shop names with system fonts (Halvorsen & Daughters books, Silver Fern Cafe, Osteria Luna, Pine Street Pharmacy, Golden Lotus,
Kestrel Watch & Clock, Harbor Hardware, North Corner Deli, Sunrise Bagels, Velvet & Vine, Antonelli Pizza, Bluebird Laundry, Mercer Optical,
Copper Kettle Tea Room, Rosa's Flowers, Iron Gate Fitness, Lark & Finch, Harbor Light Photo, The Paper Mill, Dr. Amara Voss, Haley's Shoe Repair,
Orchard Street Bakery, First Harbor Credit Union, Lotus Nail & Spa, Anchor & Oak, Salt & Pepper Diner, Maple Leaf Fruit Market, Quill & Ink,
Cornerstone Medical, Neon Dragon Noodles, Sage Health Food; 48 generic valance lines such as "FRESH BAKED DAILY"). No logos, no marks of any
real or fictional franchise. If any of these turns out to collide with a real brand, edit the `FASCIA` list in `gen_street_signs.py`.

## Verification

`python3 tools/export/ip_sanitize.py` writes previews of both sanitised atlases to
`_scratch/city/r04/atlas/`. Rebuild in Unreal: `SKIP_EXPORT=1 STEPS=tex tools/export/build_city.sh` (re-imports the sanitised PNGs).
Round-04 captures of S5 / S6 show the replacement cells (billboards that read Roxxon / Frosted Halos / Botanica / Hotel Mira in round 03
now show Sol Airways / Chasing Waves / Dinosaurs Alive / Hotel Astoria).
