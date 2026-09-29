# Hero animation scope and verification ledger

> A homage game. This is not an official Marvel game. See [DISCLAIMER.md](../../../DISCLAIMER.md).

## Owner direction (2026-09-28)

This replaces the former crowd/animal task. Leave existing bystanders and animals alone.
Build high-quality main-character jumping, airborne flips, spins, and a skin-selection entrance:
jump in from the side, flip, land with weight, settle into a suit showcase pose.
Support BOTH automatic context-sensitive traversal tricks and an explicit trick button.
Use the existing hero and compatible suits; improve geometry only if the motion exposes a concrete need.
No new paid generation, mocap packs, or hero redesign is authorized.

## Working environment

- Branch: `3d-animations-astra`; Studio checkout: `/Users/midir/sm2-astra-anim`.
- Model: `gpt-6-astra`, effort `high`, verified from this Codex thread's turn-context record.
- Dedicated Blender port: 19891; stdio MCP: blender-mcp 1.9.1, started on Studio.
- All Blender, Vite, browser QA, rendering and encoding run on Studio.
- Output target: 1920x1080, 60 FPS; record actual quality settings with measurements.
- Existing shared Studio sessions and other working checkouts are off-limits.

## Implementation and acceptance

1. [x] Prove dedicated MCP catalog/status/scene/execute round trip; save evidence.
2. [x] Import original hero GLB, inspect rig and all clip names, establish reproducible action export.
3. [x] Capture untouched baseline and verify skeletal import/export compatibility before replacing clips.
4. [x] Author front/back layout flips, corkscrew, controlled tuck flip and expressive split/scissor spin as editable Blender Actions. Build readable anticipation, rotation and recovery poses.
5. [x] Improve launch/rise/apex/landing transitions where needed for connected movement.
6. [x] Integrate automatic context-sensitive tricks and manual directional trick control; preserve existing shortcuts, combat and traversal responsiveness. Web attach, landing and obstacle contact must interrupt safely.
7. [x] Author side-entry flip, weighted landing, and breathing showcase idle for skin selection. Preserve equipment behavior and restore exact paused gameplay state on menu close.
8. [x] Check original hero and all five custom meshes, including fast menu changes and opening while airborne.
9. [x] Inspect side and three-quarter motion sequences in Blender and comparable in-game sequences. Fix visible defects, record residual issues.
10. [x] Run regression/build checks and representative real desktop performance at 1080p; report average frame time, 1% lows, hitches and before/after.
11. [ ] Push sources, scripts, clips, captures and evidence to the branch; verify remote SHA. Owner acceptance remains distinct.

## Initial source audit

Automatic release and double-tap-jump tricks already exist. The active layout/corkscrew/tuckFlip/scissor routes use procedural poses and visual-root spin in `src/player/anim/animator.js`.
The suit menu manually applies one idle frame and restores saved bone transforms. An animated preview must preserve that restoration contract and prevent the normal animator from overwriting it.

## Current status

Eight Actions implemented and visually sampled in Blender and Three.js. Manual/automatic runtime checks, all five skins, and menu state restoration pass. Export comparison passes at nonuniform times between new 120 Hz baked keys (maximum joint-position difference 3.8 mm). See README.md for evidence and honest limits. Original legacy clips are untouched; their import-only between-key discrepancy remains documented. Performance and remote publication are tracked separately.

Final desktop performance was measured at 1080p/High on the 50 Hz main display. Street and traversal averaged about 49.95 FPS; park about 49.34 FPS with three hitches. The 60 FPS target remains unverified; see PERFORMANCE.md. Implementation checks pass; owner feel/quality acceptance remains separate.
