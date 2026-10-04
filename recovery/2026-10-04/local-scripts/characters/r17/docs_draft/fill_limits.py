import os, glob, json
d = '/Users/midir/sm2-n1/characters/docs/night1/characters/round-17'
ev = d + '/evidence'
def J(p, default=None):
    try: return json.load(open(os.path.join(ev, p)))
    except Exception: return default
cap = open(d + '/CAPTURES.md').read()
st = J('seam_track.json') or {}; cj = J('cord_jog.json') or {}
lim = '''- **Sash / groove edge steps NOT fully met**: the colour-region instrument (`line_step_r17.py`) still finds long-edge jogs of 4.5 - 10 px (see the table row): the named r16 defects are gone (Ash sash shelf 26.9 px, Verdant groove step 13.7 px) but the yoke-seam cord still steps ~8 px where it crosses the Tessera sash's top-left corner, the Verdant ring-net line wobbles ~10 px at the image-right armpit, and Saffron / Sage keep 5 - 7 px steps on the collar line. These sit in the trapezius / collar band (y > 1.38) and the pec <-> arm boundary, outside the sternum strip this round smoothed.
- **Cord jog 7 / 8 by the instrument**: Ash reads %s px at x %s = the cord's thicker end cap meeting the sash border (the tracker is pulled up by the border cord); the under-arm run, where the r15 stair-steps were, reads %s px. Overlay `evidence/measures/cord_jog/cordjog_ash.jpg`.
- **Face seam dev100 7 / 8**: Glacier reads %s px; `evidence/seam_instrument_note.txt` + `evidence/measures/glacier_seam_glabella_1p6x.jpg`: the tracker follows the bright centroid, which moves 12 px where the dark crown meets the pale face; the cord itself is straight. Cinder (r16 10.9) is %s, Verdant is tracked now (%s), the chin steps are %s px (Cinder) / %s px (Ash) at the last 350 tracked rows.
- **Q6 Verdant armpit pinch ratio 0.27 (own gate 0.5)**: the copper cord is intact and tapers into the armpit crease like the brass one did (`evidence/measures/q6_pair.jpg`, r16 | r17); the instrument's colour thresholds were tuned on brass. H3 (lens >= 1.6x the r12 lens) is not computed for Verdant after the re-block (the r12 baseline segmentation expects the old lens colour); its lens widths are unchanged (594 / 389 px vs 575 / 419 px at another idle phase). H4 (own, ONE closed raised rim) %s / 8 (r16 3 / 8).
- **Dose-response limit**: `Char_Lineup` shot 5 lasts 6 s of world time, so only frames <= 20 of the r16-protocol run are comparable; the residual > 20 luma share of the frame-20 shot (1.53 %% whole / 5.07 %% band, 0 assets compiling) is the running animation (E1 after 1 static frame: 0.06 %%).
- **Not re-shot**: the stage-hero run / chase clips and the fight clip (lock at 0.5 - 1.4 fps for movies; content unchanged except the r17 weights); the Tessera back changed in r16, so the r15 / r16 chase clips in the pack still show the old back.
- The lock ran with 2 other holders for every hold (`contaminated=true`): no frame time is a performance number.
- The Verdant accent is copper (#c4703a) next to Tessera's amber (#e0780c): IP guard PASS (palette distance %s to Tessera, %s to Ash) but five of the eight suits now carry an orange-family accent (Tessera amber, Verdant copper, Plum apricot, Glacier coral, Sage clay): variety is the owner's call on `VERDANT_BEFORE_AFTER.jpg` / `SWATCH_SHEET.jpg` (a cool accent - mint, ice - is the alternative).
''' % (cj.get('ash', {}).get('max_jump_px'), (cj.get('ash', {}).get('jump_at') or [None])[0], cj.get('ash', {}).get('max_jump_under_arm_px'),
       st.get('glacier', {}).get('dev100'), st.get('cinder', {}).get('dev100'), st.get('verdant', {}).get('dev100'), st.get('cinder', {}).get('step20_chin'), st.get('ash', {}).get('step20_chin'),
       sum(1 for s_ in ('tessera','verdant','plum','cinder','glacier','ash','saffron','sage') if ((J('head_check.json') or {}).get(s_) or {}).get('verdict', {}).get('H4_rim_ge_6px_closed')),
       round((J('ipguard.json') or {}).get('palette_distance', {}).get('tessera|verdant', 0), 1), round((J('ipguard.json') or {}).get('palette_distance', {}).get('verdant|ash', 0), 1))
cap = cap.replace('@@LIMITS@@', lim)
files = '''- Stills: `stills/skin_<suit>_<view>_4k.jpg` (56: front, back, chest, head, head34, headside, headfront x 8 suits), `SWATCH_SHEET.jpg` (owner sheet, all 8 suits, front + back + chest + head), `VERDANT_BEFORE_AFTER.jpg` (r16 | r17).
- Lineups: `enemy_lineup_4k.jpg`, `enemy_lineup_34_4k.jpg` (settled); `evidence/measures/lineup/` (diff maps vs r14 / r15 / r16, `weapons_crops.jpg`: r14 | r16 | r17 crops of the bat, the pistols, the garments).
- Clips (1920x1080 internal = output): %s
- Evidence: `evidence/lineup_cause.json` + `.md`, `evidence/lineup_experiment/*.txt` (the probe / settle / shot lines of E0, E1, E2 and the frame run), `evidence/lineup_diff_*.json`, `evidence/cut_check_*.json`, `evidence/line_step_*.json` (+ `_r16_`), `evidence/cord_jog*.json`, `evidence/seam_track*.json`, `evidence/back_bleed*.json`, `evidence/net_end*.json`, `evidence/head_check.json`, `evidence/rim_depth*.json`, `evidence/iq_check.json`, `evidence/ipguard.json`, `evidence/ocr_stills.json` (+ `ocr_review.txt`), `evidence/swap_latency.json`, `evidence/pawn_check.json`, `evidence/measures/` (overlays, crop sheets, `chin_crops.jpg`, `cuts/r16_director_cuts.jpg`), `SPEC_CHECK.md`, `critic_pairs.json`.
''' % ', '.join('`%s` %.1f MB' % (os.path.basename(p), os.path.getsize(p) / 1e6) for p in sorted(glob.glob(d + '/*.mp4')))
cap = cap.replace('@@FILES@@', files)
open(d + '/CAPTURES.md', 'w').write(cap)
print('ok', '@@' in cap)
