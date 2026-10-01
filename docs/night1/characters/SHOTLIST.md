# CHARACTERS SHOTLIST, first-pass piece G (hero skins)

> Fan homage project. Not an official Marvel, Sony or Insomniac game. No affiliation. See `DISCLAIMER.md`.
> Scope since 2026-10-01 (director PLAN-firstpass.md, piece G): the HERO only; thugs / fight / crowd are paused. The older fight / crowd / lineup shots are in `HANDOFF.md` (rounds 05 - 10).

Every shot below is the REAL game (UE 5.8.3, `-game`, offscreen) through `gpu_slot.sh`, driven by `tools/ue_char/suits/chain_r11.sh`. Map `Char_Skins` = plain floor, key sun + four fills on the hero only;
`Char_SkinsPlay` = the same stage with the PLAYABLE pawn (`WebTravGameMode`, `AWebTravCharacter` wearing `/Game/Characters/Hero/SK_Hero` and the P2 hero clips). The suit is switched with the game's own code
(`UWHHeroSuitSubsystem`: director shots call `SetSuit` = `wh.Suit n`; the pawn movie injects real T key presses into the player controller).

| id | what | map / director shots | how | file (round-11/) |
|---|---|---|---|---|
| S1 | every suit, front, full body | `Char_Skins` shots 0, 4, 8 ... (suit i, view `front`), camera 5.6 m, FOV 40, aim 0.92 m | 4K real-time stills (`r.ScreenPercentage 100`, internal 3840x2160), stage-clock screenshot 2.2 s into the shot | `stills/skin_<suit>_front_4k.jpg` |
| S2 | every suit, back | views `back` (camera behind) | same | `stills/skin_<suit>_back_4k.jpg` |
| S3 | every suit, chest close-up (glyph, net, sash, stitching) | view `chest`, 1.5 m, FOV 30 (0.45 m of chest over 2160 px = 4800 px/m against 2330 texels/m) | same | `stills/skin_<suit>_chest_4k.jpg` |
| S4 | every suit, head close-up (hood, lens, vent) | view `head`, 1.0 m, FOV 26 | same | `stills/skin_<suit>_head_4k.jpg` |
| S5 | swatch sheet of all suits (front + back + chest) | composed from S1 - S3 | `tools/ue_char/suits/swatch_sheet.py` | `SWATCH_SHEET.jpg` |
| S6 | the playable hero cycling through all suits with the T key | `Char_SkinsPlay` pawn shot 0 (side tracking, 10 s) | 1080p `-movie` (fixed 1/60 s), 7 injected T presses at 1.5, 2.7 ... 8.7 s | `swap_pawn_T_key.mp4` |
| S7 | persistence: a second launch starts in the suit the first one ended in | `Char_SkinsPlay` | 960x540 still at 3 s, `-WHSuitPersist` | `persist_start.jpg`, `evidence/persist_*` |
| S8 | the stage hero in every suit, one continuous orbit, swap every 1.5 s | `Char_Skins` orbit shots (index 32 ...) | 1080p `-movie` | `orbit_all_suits.mp4` |
| M1 | swap latency, in the engine log and on the pixels of S6 | log lines `WH_SUIT set / swap_done`, `analyze_swap.py` | | `evidence/swap_latency.json` |

CPU-side checks (no engine): `suit_seams.py` (UV seams, spec CH18), `ip_guard.py palette` (colour blocking + structural uniqueness) and `ip_guard.py ocr` (OCR of the atlases and of every 4K still),
`swatch_cpu.py` (design-aid renders). Numbers: `round-11/SPEC_CHECK.md`.
