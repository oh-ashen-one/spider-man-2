# Tricks (C) — handoff (round 1 IN PROGRESS)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Branch `night1/tricks`, worktree `~/sm2-n1/tricks`, scratch `/Users/midir/sm2-n1/_scratch/tricks`. Owned: `Source/WebHomage/Traversal/WebTravFlips.{h,cpp}`,
flip programs / clips (`docs/night1/traversal/blender/make_flip_shapes.py` keys), trick input mapping (`WebFlips::ChooseForInput`), `docs/night1/tricks/`,
`tools/tricks/`. NOT owned: WebTravAnimInstance.cpp, WebTravCamera.*, WebTraversalComponent.*, wall-run code (requests: `REQUEST-traversal.md`).

State (WIP): 8 new programs (13 total) + per-instance tempo + `-WHTrickPose` rendered-bone logger in WebTravFlips.cpp; keyed squeezing tuck,
head-spot keys in the kick-out, straighter layout scissor in make_flip_shapes.py; checkers in tools/tricks. Content build of this worktree:
`SM2_MANHATTAN_SCR=/Users/midir/sm2-n1/_scratch/tricks/manhattan python3 unreal/WebHomage/Scripts/build_manhattan.py --steps cpp,city_prep,city_extra,city,traversal,characters,look,map`
(city export cloned from traversal's scratch with `cp -cR`). Next: compile, probe the 60 s reel route (-nullrhi), capture, measure, critic pack.
