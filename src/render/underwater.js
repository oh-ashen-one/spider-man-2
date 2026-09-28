// (water-effects) Everything that happens when the camera is (partly) under water, as a stage of the pipeline's
// composite pass. Adapted from dgreenheck/tidewater (MIT, (c) 2026 DRG Software Solutions LLC):
//   - src/post/Underwater.js: the medium at the lens per pixel (the lens is the near clip plane: where the wavy surface
//     crosses it the view splits into an above-water and an under-water part), a participating medium (Beer-Lambert
//     absorption + single scattering of the depth-attenuated, refracted sun and sky light, analytic along the view ray),
//     ray-marched caustic light shafts near the camera, and a dark meniscus line along the waterline on the lens
//   - src/ocean/Caustics.js: caustics by rasterised photon splatting (Evan Wallace's "WebGL Water"): a fine grid over one
//     tile of a periodic wave surface, each vertex refracts the sun ray down to a plane D metres below and lands there;
//     the fragment writes (surface area / floor area) with additive blending = the light concentration, so the focusing
//     folds form the bright caustic networks physically. Two focal planes (R shallow, G deep) blended by depth.
// Here the caustics light everything the composite finds below the surface (riverbed, seawall faces, piles, the player)
// and the shafts; the tile's waves are the shorter waves of waves.js snapped to the tile's lattice (so it tiles).
//
// createUnderwater(renderer) -> { uniforms, glsl, update(camera, water, sun), caustics }
//   glsl: uniforms + `vec4 uwComposite(vec2 uv, vec3 dir, float d, vec3 col, float dist, bool sky)` (rgb, a = 1 if the
//   pixel's medium is water) + `float uwMedium(...)`; the composite calls it before the air fog.
import * as THREE from 'three';
import { G } from '../world/layout.js';
import { WAVES_GLSL } from '../world/waves.js';
import { getQuality } from './quality.js';

const NOUW = typeof location !== 'undefined' && /[?&]nouw\b/.test(location.search);
const TILE = 12;          // caustic tile (m)
const CRES = 512;         // caustic texture resolution
const CGRID = 200;        // splat grid (quads per tile side, before the margin)
const MARGIN = 0.3;
// periodic waves on the tile: integer lattice wave vectors (n, m) -> k = 2 pi (n, m) / TILE, amplitude from its length
const CWAVES = [[3, -2, 0.03], [5, -4, 0.018], [2, -6, 0.016], [7, -3, 0.012], [9, -7, 0.008], [11, -2, 0.006], [4, 9, 0.006], [13, -9, 0.004]];

const f6 = (v) => (+v).toFixed(6);
const cw = CWAVES.map(([n, m, a], i) => `vec4(${f6(2 * Math.PI * n / TILE)}, ${f6(2 * Math.PI * m / TILE)}, ${f6(a)}, ${f6(Math.sqrt(9.81 * 2 * Math.PI * Math.hypot(n, m) / TILE))})`).join(',\n  ');
const CAUS_WAVES = `const vec4 CW[${CWAVES.length}] = vec4[${CWAVES.length}](\n  ${cw}\n);
vec2 causSlope(vec2 p, float t) {
  vec2 s = vec2(0.0);
  for (int i = 0; i < ${CWAVES.length}; i++) { vec4 w = CW[i]; float th = dot(w.xy, p) - w.w * t + float(i) * 1.7; s += w.xy * w.z * cos(th); }
  return s;
}`;

function createCaustics(renderer) {
  const rt = new THREE.WebGLRenderTarget(CRES, CRES, { type: THREE.HalfFloatType, format: THREE.RGBAFormat, depthBuffer: false,
    generateMipmaps: true, minFilter: THREE.LinearMipmapLinearFilter, magFilter: THREE.LinearFilter, wrapS: THREE.RepeatWrapping, wrapT: THREE.RepeatWrapping });
  const g = Math.ceil(CGRID * (1 + 2 * MARGIN));
  const geo = new THREE.PlaneGeometry(1, 1, g, g); // positions -0.5..0.5 -> grid uv
  const mat = new THREE.RawShaderMaterial({
    glslVersion: THREE.GLSL3, depthTest: false, depthWrite: false, transparent: true,
    blending: THREE.CustomBlending, blendSrc: THREE.OneFactor, blendDst: THREE.OneFactor, blendEquation: THREE.AddEquation,
    uniforms: { uT: { value: 0 }, uSun: { value: new THREE.Vector3(0, 1, 0) }, uD: { value: 2 }, uMask: { value: new THREE.Vector4(1, 0, 0, 0) } },
    vertexShader: /* glsl */`
precision highp float;
in vec3 position;
uniform float uT; uniform vec3 uSun; uniform float uD;
out vec2 vOld; out vec2 vNew;
${CAUS_WAVES}
void main() {
  vec2 uv = (position.xy + 0.5) * ${f6(1 + 2 * MARGIN)} - ${f6(MARGIN)};
  vec2 p = uv * ${f6(TILE)};
  vec2 s = causSlope(p, uT);
  vec3 n = normalize(vec3(-s.x, 1.0, -s.y));
  vec3 T = refract(-uSun, n, ${f6(1 / 1.333)});
  vec3 T0 = refract(-uSun, vec3(0.0, 1.0, 0.0), ${f6(1 / 1.333)});
  float tDown = max(-T.y, 0.15);
  // flat-surface offset removed: the pattern stays registered with its entry point (the lookup re-applies it)
  vec2 off = (T.xz / tDown - T0.xz / max(-T0.y, 0.15)) * uD;
  vOld = p; vNew = p + off;
  vec2 ndc = vNew / ${f6(TILE)} * 2.0 - 1.0;
  gl_Position = vec4(ndc, 0.0, 1.0);
}`,
    fragmentShader: /* glsl */`
precision highp float;
in vec2 vOld; in vec2 vNew; out vec4 fragColor;
uniform vec4 uMask;
void main() {
  float ao = abs(dFdx(vOld).x * dFdy(vOld).y - dFdx(vOld).y * dFdy(vOld).x);
  float an = abs(dFdx(vNew).x * dFdy(vNew).y - dFdx(vNew).y * dFdy(vNew).x);
  float I = ao / max(an + ao * 0.125, 1e-9);
  fragColor = uMask * I;
}`,
  });
  mat.side = THREE.DoubleSide;
  const mesh = new THREE.Mesh(geo, mat); mesh.frustumCulled = false;
  const scene = new THREE.Scene(); scene.add(mesh);
  const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const c0 = new THREE.Color();
  return {
    texture: rt.texture, tile: TILE,
    render(t, sunDir) {
      const prev = renderer.getRenderTarget(), a = renderer.getClearAlpha(); renderer.getClearColor(c0);
      renderer.setRenderTarget(rt); renderer.setClearColor(0x000000, 0); renderer.clear(true, false, false);
      mat.uniforms.uT.value = t; mat.uniforms.uSun.value.copy(sunDir);
      renderer.autoClear = false;
      for (const [D, m] of [[1.6, [1, 0, 0, 0]], [4.5, [0, 1, 0, 0]]]) { mat.uniforms.uD.value = D; mat.uniforms.uMask.value.set(...m); renderer.render(scene, cam); }
      renderer.autoClear = true;
      renderer.setRenderTarget(prev); renderer.setClearColor(c0, a);
    },
  };
}

export function createUnderwater(renderer) {
  const Q = getQuality(), CAUS = Q.waterCaustics !== false, SHAFTS = CAUS ? (Q.waterShafts ?? 12) : 0;
  const caustics = createCaustics(renderer);
  const uniforms = {
    uUwOn: { value: 0 },                        // any pixel can be under water this frame
    uUwCam: { value: new THREE.Vector4() },     // x: camera height above the water surface below it, y: near plane, z: time, w: caustic strength
    uUwFwd: { value: new THREE.Vector3(0, 0, -1) },
    uUwSigA: { value: new THREE.Vector3(0.13, 0.058, 0.062) }, // stylised, clearer than the real Hudson (gameplay: ~12 m visibility)
    uUwSigS: { value: new THREE.Vector3(0.05, 0.056, 0.058) },
    uUwSky: { value: new THREE.Vector3(0.3, 0.4, 0.5) },     // sky irradiance / PI at the surface
    tCaus: { value: caustics.texture },
    uWaveT: { value: 0 },
  };
  const glsl = /* glsl */`
#ifndef PI
#define PI 3.14159265359
#endif
uniform float uUwOn; uniform vec4 uUwCam; uniform vec3 uUwFwd; uniform vec3 uUwSigA, uUwSigS, uUwSky; uniform sampler2D tCaus;
uniform float uWaveT;
${WAVES_GLSL}
const float UW_WY = ${f6(G.WATER_Y)};
// medium at the near clip plane for this view direction: 1 water, 0 air (the lens straddles the surface within ~0.4 m)
float uwMedium(vec3 dir) {
  if (abs(uUwCam.x) > 0.45) return uUwCam.x < 0.0 ? 1.0 : 0.0;
  vec3 pn = uCamPos + dir * (uUwCam.y / max(dot(dir, uUwFwd), 0.05));
  return pn.y < UW_WY + waveHeightAt(pn.xz) ? 1.0 : 0.0;
}
// caustic light factor (mean ~1) at a world point depth z below the surface
vec3 uwCaustics(vec3 P, float z, float lod) {
  vec3 Ls = -refract(-uSunDir, vec3(0.0, 1.0, 0.0), ${f6(1 / 1.333)});
  float tDown = max(Ls.y, 0.15);
  vec2 entry = P.xz - Ls.xz * (z / tDown);
  vec2 uv = entry / ${f6(TILE)};
  float blur = clamp(z * 0.35 - 0.3, 0.0, 3.0) + lod;
  vec4 c = textureLod(tCaus, uv, blur);
  float g = mix(c.r, c.g, clamp((z - 1.6) / 2.9, 0.0, 1.0));
  // chromatic dispersion: a hint of colour fringes on the bright lines
  float gr = mix(textureLod(tCaus, uv + vec2(0.0015, 0.0), blur).r, textureLod(tCaus, uv + vec2(0.0015, 0.0), blur).g, clamp((z - 1.6) / 2.9, 0.0, 1.0));
  vec3 cc = vec3(gr, g, g * 0.97 + 0.03 * gr);
  return mix(vec3(1.0), cc, smoothstep(0.0, 0.4, z) * (1.0 - smoothstep(9.0, 16.0, z)));
}
float uwIgn(vec2 px) { return fract(fract(dot(px, vec2(0.06711056, 0.00583715))) * 52.9829189); }
// in-scattered light along a ray from the camera (depth zc below the surface) for distance dist (tidewater _uwLit)
vec3 uwLit(float m, vec3 sigT, float zc, float dirY, float dist) {
  vec3 a = sigT * zc / m;
  vec3 kk = sigT * (1.0 - dirY / m);
  vec3 e0 = exp(-a), e1 = exp(-max(a + kk * dist, vec3(0.0)));
  vec3 r;
  for (int i = 0; i < 3; i++) r[i] = abs(kk[i]) < 1e-4 ? e0[i] * dist : (e0[i] - e1[i]) / kk[i];
  return r;
}
// pixel colour when its lens medium is water: light on submerged surfaces (depth-attenuated sun + caustics), the
// medium's absorption and in-scattering along the view ray, caustic shafts near the camera
vec3 uwComposite(vec3 dir, vec3 col, float dist, bool sky) {
  vec3 sigA = uUwSigA, sigS = uUwSigS, sigT = sigA + sigS;
  float camSurf = uCamPos.y - uUwCam.x; // (uUwCam.x: camera height above the surface, from the CPU wave model)
  float zc = max(camSurf - uCamPos.y, 0.0);
  float maxD = sky ? 400.0 : dist;
  vec3 Ls = -refract(-uSunDir, vec3(0.0, 1.0, 0.0), ${f6(1 / 1.333)});
  float mu = max(Ls.y, 0.15);
  vec3 sunE = uSunColor * 0.96 * smoothstep(-0.02, 0.1, uSunDir.y);
  if (!sky) {
    vec3 P = uCamPos + dir * dist;
    float surfP = UW_WY + waveDisp(P.xz, 0.0).y; // (Lagrangian height: close enough for the light path)
    float z = surfP - P.y;
    if (z > 0.02) {
      // the scene lit it with the full sun: the water on the way down absorbs it (sun share ~60 % of the light in daylight),
      // the surface waves focus it into caustics
      vec3 att = exp(-sigT * z / mu);
      float sunShare = 0.6 * smoothstep(-0.02, 0.1, uSunDir.y);
      vec3 caus = uwCaustics(P, z, 0.0);
      col *= mix(exp(-sigT * z * 0.55), att * caus * uUwCam.w + att * (1.0 - uUwCam.w), sunShare);
    }
  }
  vec3 Tr = exp(-sigT * maxD);
  float cosPh = dot(dir, Ls);
  float g = 0.85;
  float phase = (1.0 - g * g) / (4.0 * PI) / pow(max(1.0 + g * g - cosPh * 2.0 * g, 1e-4), 1.5) * 0.75 + 0.25 / (4.0 * PI);
  vec3 bb = sigS * 0.035, albedoMS = bb * 1.32 / (sigA + bb);
  vec3 lit = uwLit(mu, sigT, zc, dir.y, maxD);
  vec3 inS = sunE * (sigS * phase + albedoMS * sigT / PI) * lit + skyLUT(vec3(0.0, 1.0, 0.0)) * PI * (sigS * 0.25 / PI + albedoMS * sigT / PI) * uwLit(0.75, sigT, zc, dir.y, maxD);
  // caustic shafts: sunlight focused by the waves streaming down through the water near the camera (12 jittered steps)
  vec3 shafts = vec3(0.0);
  {
    float md = min(maxD, 22.0), ds = md / ${Math.max(1, SHAFTS)}.0;
    float jit = uwIgn(gl_FragCoord.xy + fract(uUwCam.z * 7.3) * 64.0);
    for (int i = 0; i < ${SHAFTS}; i++) {
      float s = (float(i) + jit) * ds;
      vec3 p = uCamPos + dir * s;
      float z = max(camSurf - p.y, 0.02);
      vec3 caus = uwCaustics(p, z, 1.5);
      shafts += (caus - 1.0) * exp(-sigT * (s + z / mu)) * ds;
    }
    shafts *= sunE * sigS * phase * 2.5 * uUwCam.w;
  }
  return col * Tr + inS + max(shafts, vec3(0.0));
}
`;
  const _p = new THREE.Vector3(), _f = new THREE.Vector3();
  let t = 0, frame = 0;
  return {
    uniforms, glsl, caustics,
    // camera, water (world.water: heightAt, time), sunDir (world, toward the sun), skyIrr (vec3, sky radiance ~ zenith)
    update(camera, water, sunDir, skyRad) {
      if (!water) { uniforms.uUwOn.value = 0; return false; }
      camera.getWorldPosition(_p);
      const h = _p.y - water.heightAt(_p.x, _p.z);
      camera.getWorldDirection(_f);
      uniforms.uUwCam.value.set(h, camera.near, water.time, CAUS ? 1.7 : 0);
      uniforms.uUwFwd.value.copy(_f);
      uniforms.uWaveT.value = water.time;
      const on = h < 0.5 && !NOUW; // ?nouw: raw scene colour under water (debug)
      uniforms.uUwOn.value = on ? 1 : 0;
      if (skyRad) uniforms.uUwSky.value.copy(skyRad);
      if (on && CAUS && (frame++ & 1) === 0) caustics.render(water.time, sunDir);
      return on;
    },
  };
}
