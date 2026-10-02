# Request to traversal (P3 / B) from Tricks (C)

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Tricks owns `WebTravFlips.{h,cpp}`, the flip programs / clips (`docs/night1/traversal/blender/make_flip_shapes.py` keys) and the trick input
mapping, but the hooks that CALL them live in traversal-owned files. Round 1 needs these two one-line hooks (not done by C):

1. **Auto / player choice uses the new programs.** `UWebTraversalComponent::ChooseTrick` (WebTraversalComponent.cpp, the `!bLegacyTricks`
   branch) still cycles `SkyP = {backDouble, frontPikeSwan, corkscrew}` / `LowP`. Replace both lists with
   `WebFlips::ChooseForInput(InD0.Y_forward, S.TrickLat, S.AutoFlipK++, Air, S.LastTrickName)` (stick forward / lateral at the trick press;
   `Air` = `AirTimeToClear()` for a plain release, `<= 0` for flow / sky flips whose air is solved) and pass the result through `FitFlip`.
   Until then only scripts (`"flip": "a,b,..."`) reach the 8 new programs (frontSingle, frontDouble, backPike, backLayout, barani, fullTwist,
   rudi, backTripleChain).
2. **`FitFlip`'s fallback** returns `backSingle` when the wanted program does not fit; with 12 programs it should ask
   `WebFlips::ChooseForInput(0, 0, K, Air, Last)` for the longest one that fits instead.

Nothing else in traversal is needed: programs, shapes, tempo variation and the pose logger are inside WebTravFlips.cpp.
