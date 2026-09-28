# Third-party code and techniques

## dgreenheck/tidewater — MIT License, © 2026 DRG Software Solutions LLC
https://github.com/dgreenheck/tidewater — techniques and shader math ported from WGSL (raw WebGPU) to GLSL / three.js r186 WebGL2
on the `water-effects` branch:

| Our file | Adapted from |
|---|---|
| `src/world/cdlod.js` | `src/core/CDLOD.js` (CDLOD quadtree selection + world-space geomorph) |
| `src/world/water.js` (shading, sea detail) | `src/ocean/WaterMaterial.js` (Fresnel, GGX glint, Cox-Munk roughness, turbid-medium body, underside), `src/ocean/SeaDetail.js` |
| `src/render/underwater.js` | `src/post/Underwater.js` (lens medium, in-scattering, shafts, meniscus), `src/ocean/Caustics.js` (photon-splat caustics) |
| `src/render/pipeline.js` (lens droplets in the final pass) | `src/post/LensDroplets.js` |
| `src/world/waterfx/spray.js` (sprite shading) | `src/fx/Spray.js` |
| `src/world/waterfx/gulls.js` | `src/world/Gulls.js` |

MIT License text: https://github.com/dgreenheck/tidewater/blob/main/LICENSE — "Permission is hereby granted, free of charge, to any person
obtaining a copy of this software ... The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software."

## Evan Wallace — "WebGL Water" (MIT)
The ripple heightfield (`src/world/waterfx/ripples.js`) and the caustic splatting idea follow https://madebyevan.com/webgl-water/.
