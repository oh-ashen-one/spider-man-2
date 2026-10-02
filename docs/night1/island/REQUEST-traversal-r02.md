# Request to traversal (piece P3) from the Island (piece A), round 02

> Homage fan game. Not an official Marvel, Sony or Insomniac game; no affiliation.

Filed 2026-10-01 by the island builder. The island never edits `Source/WebHomage/Traversal`; these are asks, with the island-side facts.

## 1. Index WHBox cube ISM instances per instance in SolidMode 2

**Why:** the island's `SM2_WHBOX_MODE=ism` build puts the ~57 k WHBox cubes in 58 always-loaded actors (one invisible
`InstancedStaticMeshComponent` of `/Engine/BasicShapes/Cube` per 256 m tile). It builds the WP map in ~20 s instead of 1,077-2,203 s
(actor mode), and it is the only way the whole island (~140 k boxes, M2) can be built at all.

**What breaks today (WebTravWorld.cpp, round 20, `Init`):** in `SolidMode == 2` the `IsTravCube(P)` branch runs before the ISM branch and
calls `AddBox(P->Bounds.GetBox())` once per *component*. An ISM cube component is accepted by `IsTravCube` (it is a
`UStaticMeshComponent`, invisible, mesh `Cube`), so each tile's ~1,000 boxes collapse into ONE 256 m index box. The anchor / canyon /
zip-point / perch logic would then see a 256 m block per tile.

**Ask:** in the SolidMode-2 cube branch, when `P` is an `UInstancedStaticMeshComponent`, add one box per instance (as the old SolidMode-0
ISM branch does: `GetInstanceTransform(I, T, true)`, `AddBox(MeshBounds.TransformBy(T))`, fill `InstToBox`) and keep the component
de-collided (index only). The `bHasBoxes` probe at the top of `Init` already accepts ISM cubes.

**Until then:** the island keeps actor-mode WHBox cubes as the default (`SM2_WHBOX_MODE=actor`); `Manhattan_WP` is built that way.

## 2. Default for instanced props / trees (`-WHTravIsmSolid`)

r02 makes the A/B meaningful: every instanced prop that is not on the r20 exclusion list (benches, pit fences, planters, kiosks,
bus shelters, dumpsters, parked cars, tree barks ...) now carries cooked triangle collision with its collision **off** and BlockAll
responses (`build_city.py proto_ab()`). r20's default (`-WHTravIsmSolid=0`) is unchanged; with `=1` the traversal re-enables them
(QueryOnly). Sheds, shed tops and subway entrances are solids in both modes. The measured A/B (stuck frames, trunk-overlap frames, same
r1 route, fixed 1/60 s step) is in `docs/night1/island/round-02/README.md` ("IsmSolid A/B"); the default decision is traversal's.
