# Studio continuation: hero animations

The owner cancelled crowd/animal animation work. Current scope is the main hero, manual plus automatic aerial tricks, and the suit-selection entrance.

## Ownership

- Studio checkout: /Users/midir/sm2-astra-anim, branch 3d-animations-astra.
- Direct remote: git@gh-sm2-astra-anim:oh-ashen-one/spider-man-2.git.
- Dedicated Blender MCP port 19891, scene owner sm2-astra-anim; editable art/anim/hero.blend.
- MCP bridge: blender-mcp 1.9.1 with its matching bundled addon, protocol 5; 28 tools verified. Blender 5.2.0 LTS. Shared addon/configuration untouched.
- Own Vite port 5193 (.scratch/vite.pid); own Chrome CDP 9334, profile .scratch/chrome-profile.
- Port 5192 and other Studio sessions are off limits. Revalidate live ownership before operating any process.
- Agent model/settings recorded from original thread context: gpt-6-astra, high.
- The requested chat migration failed. Work continued through this laptop-hosted chat, with all authoring/compute/testing on Studio. An unfinished agent turn still depends on the laptop connection; saved Studio assets and servers do not.

## Current implementation

Eight authored Blender Actions are baked at 120 Hz with stable unique IDs into an additive JSON library. Main runtime uses the new launch and trick clips, with original fallback. X/L3 is the manual trigger; automatic releases and double-Space remain. The suit preview owns its mixer and restores all saved transforms on close.

See [README.md](README.md), [PLAN.md](PLAN.md), [PERFORMANCE.md](PERFORMANCE.md) and the JSON checks. Preserve the original GLB and all five custom meshes. The old crowd handoff is superseded.

## Reproduce

Run commands from the Studio checkout:
- npm test; npm run build.
- uv run --with blender-mcp==1.9.1 python tools/heroanim/mcp_client.py catalog
- Use execute_blender_code with --script tools/heroanim/author_hero.py to rebuild Actions/export through the dedicated MCP connection.
- Run verify_export.py through MCP, then node tools/heroanim/verify_export.mjs for independent Blender-versus-Three sampling.
- Run render_review.py through MCP, then uv run --with pillow python tools/heroanim/contact_sheet.py.
- node tools/heroanim/runtime_checks.mjs and node tools/heroanim/extended_checks.mjs use only CDP 9334.
- node tools/heroanim/capture_motion.mjs records the two-angle review page on Studio.
- performance.mjs runs real visible desktop measurements; it moves only the task Chrome window onto the Studio 120 Hz display. Keep other rendering/encoding jobs idle during measurements.

Do not replace paid generation, hand off to another model, merge main, modify other sessions, or declare owner acceptance without new authorization/evidence. Push all subsequent authored changes to the branch in the same session.
