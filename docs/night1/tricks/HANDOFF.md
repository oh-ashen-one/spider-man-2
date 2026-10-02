# Tricks (C) — handoff (round 1 IN PROGRESS)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Branch `night1/tricks`, worktree `~/sm2-n1/tricks`, scratch `/Users/midir/sm2-n1/_scratch/tricks`. Owned: `Source/WebHomage/Traversal/WebTravFlips.{h,cpp}`,
flip programs / clips (`docs/night1/traversal/blender/make_flip_shapes.py` keys), trick input mapping (`WebFlips::ChooseForInput`), `docs/night1/tricks/`,
`tools/tricks/`. NOT owned: WebTravAnimInstance.cpp, WebTravCamera.*, WebTraversalComponent.*, wall-run code (requests: `REQUEST-traversal.md`).

State (WIP): 8 new programs (13 total) + per-instance tempo + `-WHTrickPose` rendered-bone logger in WebTravFlips.cpp; keyed squeezing tuck,
head-spot keys in the kick-out, straighter layout scissor in make_flip_shapes.py; checkers in tools/tricks. Content build of this worktree:
`SM2_MANHATTAN_SCR=/Users/midir/sm2-n1/_scratch/tricks/manhattan python3 unreal/WebHomage/Scripts/build_manhattan.py --steps cpp,city_prep,city_extra,city,traversal,characters,look,map`
(city export cloned from traversal's scratch with `cp -cR`; ~15 min). Flip-clip rebuild only: `python3 /Users/midir/sm2-n1/_scratch/tricks/run_trav_step.py`
INSIDE a gpu_slot hold (build_manhattan's own 3-instance poll starves while 4 capture slots are busy).
Round-1 hold script: `/Users/midir/sm2-n1/_scratch/tricks/hold_r01.sh` (clip step -> `tools/tricks/auto_route.py` fits the reel's turn keys with
-nullrhi probes -> `tools/tricks/capture.sh docs/night1/tricks/round-01 t60_trick_reel`). Queue it with
`/Users/midir/sm2-n1/_scratch/gpu/bin/gpu_slot.sh capture --label tricks -- /Users/midir/sm2-n1/_scratch/tricks/hold_r01.sh`.
Probe p1 (first draft, -nullrhi): 13 programs in 61 s, V2 PASS, K PASS, G1/G2 PASS; fails fixed since: 6 slow-limb samples (static reach / pencil /
end of tuck -> keyed), G3 head spot 8/13 (-> reach spot keys), G4 open-out 8/13 (-> final reach >= 0.36 s), route broke at the 5th Av corner
(-> auto_route). Gotcha: pollers must not `pgrep -f` a string their own command line contains (use [x]yz).
