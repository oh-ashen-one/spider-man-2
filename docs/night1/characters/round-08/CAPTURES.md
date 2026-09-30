# Round 08: captures of the running characters maps

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.

**Round target (critic r07, single biggest gap):** replace the copied suit layout with an original one (`SUIT_ORIGINALITY.md`), rebuild each eye lens as one closed rim sealed to a lens that sits inside the head silhouette, re-capture `hero_face_lens_4k` plus the hero turnaround and run clips, and check at 3x crops: 0 background pixels between rim and lens, no lens beyond the mask outline, no web-line stair step wider than 2 px. Secondary: the shoe shards, the thug collar shards, lips poking through the mask, the two fused heads in `crowd_tracking_4k`. Numbers: `SPEC_CHECK.md`.

**Source.** Real `-game` runs (UE 5.8.3, Metal, offscreen `-RenderOffScreen -NoSound`) through `unreal/WebHomage/Scripts/run_game.sh` (driver `tools/ue_char/run_r8_captures.sh`, groups `H X E F D C Q M S K`; crowd key movie `tools/ue_char/crowd/key_movie.sh`, colour movie `colour_movie.sh`, id movie `id_movie.sh`), 2026-09-30 16:46 onward. Content rebuilt from the committed scripts (`build_characters.py`, steps `clean,tex,mat,mesh,citizens,rename,abp,map,maps5,mapkey,mapavoid`; the hero maps are the 8192 Tessera maps of `hero_suit_r8.py`, the eyes come from `hero_lens_r8.py`); no `.uasset` / `.umap` is committed. Every Unreal launch (builds and captures) went through `gpu_slot.sh capture --label characters`, one engine of mine at a time (other agents held both slots for up to 25 min per launch; nothing was bypassed). Every release logged `contaminated=true reasons=no-exclusive-lock` (shared capture slot): **no frame time here is a performance result**.

**Resolution (disclosed).** Stills: native 3840x2160 output, internal 3840x2160 (`r.ScreenPercentage 100`, mode `manual`, in every `evidence/perf_*.json`). The hero key stills (`hero_key_*_4k.png`) and the two key stills `crowd_key_a_4k.png` / `crowd_key_c_4k.png` are lossless PNG (a 4:2:0 JPEG would bleed the key colour into edge pixels); the crowd stills picked by frame number come from fixed-step 4K movie runs (output = internal 3840x2160, 1/60 s steps, motion blur off). Movies: fixed-step `-movie` runs, 1920x1080 output = 1920x1080 internal, H.264, motion blur off, every clip <= 15 MB; `-movie` output says nothing about real-time speed. The hero maps are 8192 x 8192 (base colour, normal, ORM): BC compressed in the engine, a texel is 0.15 mm on the face (6,650 texels/m on the head, about 4,600 on the body) so a 4K close-up magnifies each texel 2x.

**Trimmed clips (texture-streaming warm-up).** The first ~0.4 s of every `-movie` run shows the lowest texture mips and the walkers in the rest pose. The first clip of each run (`hero_run_side`, `hero_run_chase`, `street_fight_wide`, `crowd_tracking`) therefore starts 0.6 s into the run (`tools/ue_char/trim_clips_r8.sh`, re-encoded crf 17); the untrimmed originals are in `untrimmed/` (scratch only).

## What changed in the content this round

- **Hero suit**: the original Tessera suit (procedural, 8192 maps), see `SUIT_ORIGINALITY.md`. Material: Cloth shading with a teal fuzz colour, tiled 2/2 twill detail normal (0.45 mm yarn), per-panel roughness.
- **Hero eyes**: one closed bezel ring per eye, sealed to a lens dome, both conformed to the mask surface; amber lens, graphite bezel (`hero_lens_r8.py`).
- **Street enemies**: tee mask hangs over the mouth (`mask.hang(uncover_mouth=True)`), thug collar (`mask.sink_neck`, softened neck atlas texels).
- **Citizens**: the triangles that float as detached polygons (`shards_r8.py`: skater 50, punk artist 2, chrome shades 1) are dropped; offline CH18 cracks did not rise (`evidence/offline_ch18_gate_round08_changed.json`).
- **New test map** `Char_HeroKey` (hero on the stencil key, flat class colours with `-WHFlatClasses`) and the tools that read it.

## Files

See the file table in `SPEC_CHECK.md` (every file named there is in `captures/`); `crops_3x/` holds the 3x Lanczos crops, round 07 (left) | round 08 (right).
