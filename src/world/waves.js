// (water-effects) Harbour / river waves: one set of Gerstner waves shared by the GPU (water surface displacement and
// normals, the underwater waterline, caustics) and the CPU (water height for the player, boats, splashes, the camera's
// medium). Short-fetch chop on the Hudson / East River: wavelengths 0.9-28 m, crests up to ~0.3 m, travelling
// down-wind (south-west wind toward the north-east) with a spread of directions, plus a slow harbour swell.
//
// GLSL (WAVES_GLSL, needs `uniform float uWaveT;` declared by the includer):
//   vec3 waveDisp(vec2 xz, float spacing)   Gerstner displacement at the undisplaced (Lagrangian) point xz; waves
//                                           shorter than ~4 grid spacings are faded (no aliasing on coarse LODs)
//   vec4 waveSlope(vec2 xz, float foot)     xy: height slopes dh/dx, dh/dz (fragment normal), z: unresolved slope
//                                           variance of the waves faded out by the pixel footprint `foot` (m) -> roughness,
//                                           w: normalised crest height (-1..1)
//   float waveHeightAt(vec2 xz)             surface height (relative to G.WATER_Y) above the EULERIAN point xz (two
//                                           fixed-point iterations inverting the horizontal displacement)
// CPU: waveHeight(x, z, t) / waveSlopeAt(x, z, t) mirror the GLSL (same constants).
import { G } from './layout.js';

const GRAV = 9.81;
// [wavelength m, amplitude m, direction deg (0 = +x, 90 = +z), steepness Q, phase]
// wind toward the north-east (+x, -z): -50 deg
const SPEC = [
  [31.0, 0.06, -38, 0.2, 0.0],     // harbour swell (long, low)
  [16.5, 0.055, -62, 0.35, 5.1],
  [11.2, 0.065, -24, 0.45, 1.7],
  [7.9, 0.05, -83, 0.5, 4.1],
  [5.6, 0.042, -47, 0.55, 2.3],
  [4.3, 0.03, -2, 0.5, 3.9],
  [3.3, 0.026, -71, 0.55, 5.6],
  [2.45, 0.019, -28, 0.5, 0.9],
  [1.8, 0.014, -104, 0.45, 3.3],
  [1.33, 0.01, -52, 0.4, 6.0],
  [0.97, 0.0072, 8, 0.35, 2.0],
  [0.71, 0.005, -66, 0.3, 4.6],
];
export const WAVES = SPEC.map(([L, A, dDeg, q, ph]) => {
  const k = 2 * Math.PI / L, d = dDeg * Math.PI / 180;
  return { L, A, k, w: Math.sqrt(GRAV * k), dx: Math.cos(d), dz: Math.sin(d), Q: q / (k * A * SPEC.length), ph };
});
export const WAVE_MAX = WAVES.reduce((a, w) => a + w.A, 0); // ~0.41 m (all crests aligned, never in practice)
export const WIND_DIR = [Math.cos(-50 * Math.PI / 180), Math.sin(-50 * Math.PI / 180)];

const f = (v) => { const s = (+v).toFixed(6); return s; };
const wavesConst = WAVES.map(w => `vec4(${f(w.dx)}, ${f(w.dz)}, ${f(w.k)}, ${f(w.A)}), vec4(${f(w.w)}, ${f(w.Q)}, ${f(w.ph)}, 0.0)`).join(',\n  ');

export const WAVES_GLSL = /* glsl */`
#define WAVE_N ${WAVES.length}
const vec4 WAVE_P[${WAVES.length * 2}] = vec4[${WAVES.length * 2}](
  ${wavesConst}
);
vec3 waveDisp(vec2 xz, float spacing) {
  vec3 o = vec3(0.0);
  for (int i = 0; i < WAVE_N; i++) {
    vec4 a = WAVE_P[i * 2], b = WAVE_P[i * 2 + 1];
    float L = 6.2831853 / a.z;
    float fade = 1.0 - smoothstep(0.18, 0.3, spacing / L);
    float th = a.z * dot(a.xy, xz) - b.x * uWaveT + b.z;
    float s = sin(th), c = cos(th);
    float A = a.w * fade;
    o.xz += b.y * A * a.xy * c;
    o.y += A * s;
  }
  return o;
}
vec4 waveSlope(vec2 xz, float foot) {
  vec2 sl = vec2(0.0); float varU = 0.0, h = 0.0;
  for (int i = 0; i < WAVE_N; i++) {
    vec4 a = WAVE_P[i * 2], b = WAVE_P[i * 2 + 1];
    float th = a.z * dot(a.xy, xz) - b.x * uWaveT + b.z;
    float kA = a.z * a.w;
    // resolved on screen while the wave spans several pixels; its slope variance ((kA)^2 / 2) moves into roughness
    float fade = 1.0 - smoothstep(0.12, 0.35, foot * a.z / 3.14159);
    float c = cos(th);
    // Gerstner slope (Lagrangian): dh/dx = kA d cos / (1 - Q kA sin) -- the denominator sharpens the crests
    float den = max(1.0 - b.y * kA * sin(th), 0.35);
    sl += a.xy * (kA * c / den) * fade;
    varU += 0.5 * kA * kA * (1.0 - fade);
    h += a.w * sin(th);
  }
  return vec4(sl, varU, h / ${f(WAVE_MAX * 0.5)});
}
float waveHeightAt(vec2 xz) {
  vec2 p = xz;
  for (int it = 0; it < 2; it++) { vec3 d = waveDisp(p, 0.0); p = xz - d.xz; }
  return waveDisp(p, 0.0).y;
}
`;

// ---- CPU mirror
export function waveDispCPU(x, z, t, out = { x: 0, y: 0, z: 0 }) {
  let ox = 0, oy = 0, oz = 0;
  for (const w of WAVES) {
    const th = w.k * (w.dx * x + w.dz * z) - w.w * t + w.ph, s = Math.sin(th), c = Math.cos(th);
    ox += w.Q * w.A * w.dx * c; oz += w.Q * w.A * w.dz * c; oy += w.A * s;
  }
  out.x = ox; out.y = oy; out.z = oz; return out;
}
const _d = { x: 0, y: 0, z: 0 };
// height of the surface above the world point (x, z), relative to G.WATER_Y
export function waveHeight(x, z, t) {
  let px = x, pz = z;
  for (let i = 0; i < 2; i++) { waveDispCPU(px, pz, t, _d); px = x - _d.x; pz = z - _d.z; }
  return waveDispCPU(px, pz, t, _d).y;
}
export const waterLevel = (x, z, t) => G.WATER_Y + waveHeight(x, z, t);
