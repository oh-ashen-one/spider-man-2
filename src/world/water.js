// OWNER: foundation agent (city remake); (water-effects) waves / shading / foam rewrite.
// River / harbour water around the island:
//   - SURFACE: a CDLOD quadtree grid (cdlod.js, adapted from dgreenheck/tidewater) displaced by the shared Gerstner
//     waves (waves.js) + the splash ripple sim (waterfx/ripples.js), out to ~300 km; per-pixel analytic wave normals,
//     filtered by the pixel footprint (resolved waves -> normals, unresolved slope variance -> roughness, Cox-Munk)
//   - SHADING (adapted from tidewater src/ocean/WaterMaterial.js, MIT): exact dielectric Fresnel, GGX sun glint with
//     that roughness, reflections = the planar mirror of the big stuff + the sky IBL with the reflection tilted toward
//     the darker upper sky on rough water, and the water body as an infinitely deep turbid medium (Beer-Lambert
//     absorption + single / multiple scattering of the refracted sun and sky light) instead of a painted colour;
//     crest translucency; the underside (camera below the surface): Snell's window + total internal reflection
//   - SEA DETAIL (tidewater src/ocean/SeaDetail.js): wind-aligned gusts, slicks and windrows modulate the short waves
//   - FOAM: contact foam where the water meets seawalls, pier edges, piles, bridge piers (a fine distance map baked from
//     the wet edges + the solids crossing the water line) and boat hulls (analytic, per boat), Kelvin wake arms + prop
//     wash behind moving boats, windrows, splash foam from the ripple sim
//   - opts out of the pipeline's SSR (the mirror replaces it; SSR's 220 m rays never reached the far shore)
// Plus: wet bands (dark, algae-stained tidal strip) along every bulkhead / seawall / pier edge, and a horizon skirt
// just inside the far plane.
import * as THREE from 'three';
import { G, distToShore, LAND_POLY } from './layout.js';
import { FAR_LANDS } from './farshore.js';
import { WAVES_GLSL, WIND_DIR, waveHeight } from './waves.js';
import { CDLOD } from './cdlod.js';
import { createRipples } from './waterfx/ripples.js';
import { createSpray, SPRAY, DROP } from './waterfx/spray.js';
import { createGulls } from './waterfx/gulls.js';
import { getQuality } from '../render/quality.js';

export const REFL_LAYER = 27;       // meshes the planar reflection renders besides the big shadow casters
const BIG_LAYER = 28;               // render/csm.js BIG_CASTER_LAYER (tagged large casters: towers, walls, bridges)
export const MAX_BOATS = 24;
const IOR = 1.333;

// turbid Hudson / East River water (per metre): absorption strongest in the blue (dissolved organics) and red, silt
// scattering nearly grey -> an olive-grey-green body; visibility ~1.5 m (the underwater view uses a clearer, stylised
// medium: render/pipeline.js composite)
export const WATER_OPTICS = { sigA: new THREE.Vector3(0.42, 0.29, 0.27), sigS: new THREE.Vector3(0.19, 0.2, 0.2) };

const f6 = (v) => (+v).toFixed(6);

// opts: ssr (ponds keep the pipeline SSR), body (base colour tint reference), shore ({texture, box}: 8 m/px distance to
// the nearest shore), waves (CDLOD + Gerstner surface: the river; ponds stay flat), cdlod (CDLOD instance), contact
// ({texture, box, range}), boats (true: boat foam uniforms), rip (ripple sim {texture, box})
export function createRiverMaterial(T, refl = null, { ssr = false, body = [0.06, 0.082, 0.09], shore = null, waves = false, cdlod = null,
  contact = null, boats = false, rip = null } = {}) {
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.06, metalness: 0.0, side: waves ? THREE.DoubleSide : THREE.FrontSide });
  const defs = { NO_WET: '' };
  if (!ssr) defs.NO_SSR = '';
  if (shore) defs.HAS_SHORE = '';
  if (waves) defs.HAS_WAVES = '';
  if (contact) defs.HAS_CONTACT = '';
  if (boats) defs.HAS_BOATS = '';
  if (rip) defs.HAS_RIP = '';
  mat.defines = defs;
  const uni = { tWN: { value: T.waterNrm }, tWNoise: { value: T.noise }, uWTime: { value: 0 },
    tRefl: { value: refl?.texture ?? null }, uTexMat: { value: refl?.texMat ?? new THREE.Matrix4() }, uReflOn: { value: 0 },
    tShore: { value: shore?.texture ?? null }, uShoreBox: { value: shore?.box ?? new THREE.Vector4(0, 0, 1, 1) },
    uWaveT: { value: 0 }, uWaveAmp: { value: 1 }, uCdlodMorph: cdlod ? cdlod.uMorph : { value: [] },
    tContact: { value: contact?.texture ?? null }, uContactBox: { value: contact?.box ?? new THREE.Vector4(0, 0, 1, 1) },
    uBoatA: { value: Array.from({ length: MAX_BOATS }, () => new THREE.Vector4()) },
    uBoatB: { value: Array.from({ length: MAX_BOATS }, () => new THREE.Vector4()) }, uBoatN: { value: 0 },
    tRip: { value: rip?.texture ?? null }, uRipBox: { value: rip?.box ?? new THREE.Vector4(0, 0, 1, 0) },
    uSigA: { value: WATER_OPTICS.sigA }, uSigS: { value: WATER_OPTICS.sigS },
    uBodyRef: { value: new THREE.Vector3(...body) }, uCamBelow: { value: 0 } };
  mat.userData.uniforms = uni;
  const levels = cdlod ? cdlod.levels : 1;
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, uni);
    const vDecl = `#include <common>
      varying vec3 vWPw; varying vec2 vLag; uniform mat4 uTexMat; varying vec4 vRefl;
      uniform float uWaveT; uniform float uWaveAmp;
      #ifdef HAS_RIP
        uniform sampler2D tRip; uniform vec4 uRipBox;
      #endif
      #ifdef HAS_WAVES
        attribute vec4 nodeData; uniform vec4 uCdlodMorph[${levels}];
        ${WAVES_GLSL}
        ${cdlod ? cdlod.glsl : ''}
      #endif`;
    sh.vertexShader = sh.vertexShader.replace('#include <common>', vDecl)
      .replace('#include <begin_vertex>', `
      #ifdef HAS_WAVES
        vec4 cm = cdlodMorph(nodeData, position.xz, cameraPosition, ${f6(G.WATER_Y)});
        vec2 lag = cm.xy;
        vec3 wd = waveDisp(lag, cm.z) * uWaveAmp;
        #ifdef HAS_RIP
          if (uRipBox.w > 0.5) {
            vec2 ru = (lag - uRipBox.xy) / uRipBox.z;
            vec2 re = smoothstep(0.0, 0.08, ru) * smoothstep(1.0, 0.92, ru);
            wd.y += texture(tRip, ru).r * re.x * re.y;
          }
        #endif
        vec3 transformed = vec3(lag.x + wd.x, ${f6(G.WATER_Y)} + wd.y, lag.y + wd.z);
        vLag = lag;
      #else
        vec3 transformed = vec3(position);
        vLag = (modelMatrix * vec4(position, 1.0)).xz;
      #endif`)
      .replace('#include <fog_vertex>', `#include <fog_vertex>
        vWPw = (modelMatrix * vec4(transformed, 1.0)).xyz; vRefl = uTexMat * vec4(vWPw, 1.0);`);

    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      uniform sampler2D tWN; uniform sampler2D tWNoise; uniform float uWTime; varying vec3 vWPw; varying vec2 vLag;
      uniform sampler2D tRefl; uniform float uReflOn; varying vec4 vRefl;
      uniform sampler2D tShore; uniform vec4 uShoreBox;
      uniform float uWaveT; uniform float uWaveAmp;
      uniform vec3 uSigA; uniform vec3 uSigS; uniform vec3 uBodyRef;
      #ifdef HAS_WAVES
        ${WAVES_GLSL}
      #endif
      #ifdef HAS_CONTACT
        uniform sampler2D tContact; uniform vec4 uContactBox;
      #endif
      #ifdef HAS_BOATS
        uniform vec4 uBoatA[${MAX_BOATS}]; uniform vec4 uBoatB[${MAX_BOATS}]; uniform int uBoatN;
      #endif
      #ifdef HAS_RIP
        uniform sampler2D tRip; uniform vec4 uRipBox;
      #endif
      vec3 wN; float wR; float wA2; float wDist; float wSh = 1.0; vec2 wDisp; float wSlick; float wShore; float wNearS; float wStreak;
      float wGust; float wFoam; float wCrest; float wVarU; float wWake;
      vec3 wGlit = vec3(0.0); uniform float uCamBelow; bool wFront = true; vec3 wSunL = vec3(0.0); vec3 wLv = vec3(0.0, 1.0, 0.0); vec3 wRefl = vec3(0.0); vec3 wIrr = vec3(0.0); vec3 wTint = vec3(1.0);
      vec2 wn(vec2 uv) { return texture(tWN, uv).rg * 2.0 - 1.0; }
      float wSat(float x) { return clamp(x, 0.0, 1.0); }
      // exact unpolarised dielectric Fresnel (tidewater waterFresnelModule), eta = n2 / n1
      float fresnelDielectric(float cosI, float eta) {
        float c = clamp(cosI, 0.0, 1.0);
        float g2 = eta * eta - 1.0 + c * c;
        if (g2 < 0.0) return 1.0;
        float g = sqrt(g2);
        float a = (g - c) / (g + c);
        float b = (c * (g + c) - 1.0) / (c * (g - c) + 1.0);
        return 0.5 * a * a * (b * b + 1.0);
      }
      float waterPhaseHG(float cosT, float g) {
        float g2 = g * g;
        return ((1.0 - g2) / (4.0 * PI)) / pow(max(1.0 + g2 - cosT * 2.0 * g, 1e-4), 1.5);
      }
      // coverage-driven foam: bubbly cells that dissolve from the edges as the coverage drops
      float foamPattern(vec2 p, float cov) {
        float a = texture(tWNoise, p / 1.9 + vec2(uWTime * 0.004, 0.0)).r;
        float b = texture(tWNoise, p / 0.63 + vec2(0.0, uWTime * 0.006)).g;
        float pat = a * 0.62 + b * 0.5;
        return smoothstep(1.05 - cov, 1.3 - cov, pat) * smoothstep(0.0, 0.25, cov);
      }
      #ifdef HAS_BOATS
      // hull contact foam, bow wave, Kelvin wake arms (19.47 deg) and the turbulent prop wash of every boat near p
      vec2 boatFoam(vec2 p) {
        float foam = 0.0, wake = 0.0;
        for (int i = 0; i < ${MAX_BOATS}; i++) {
          if (i >= uBoatN) break;
          vec4 a = uBoatA[i], b = uBoatB[i];
          vec2 d = p - a.xy;
          float sh_ = sin(a.z), ch_ = cos(a.z);
          float v = d.x * sh_ + d.y * ch_;      // along the boat (+ = bow)
          float u = d.x * ch_ - d.y * sh_;      // across
          float hl = a.w * 0.5, hb = b.x * 0.5, spd = b.y, moving = b.z < 0.5 ? smoothstep(0.5, 3.0, spd) : 0.0;
          float wl = a.w * mix(1.0, 7.0, moving);
          if (v < -hl - wl || v > hl + 12.0 || abs(u) > hb + 12.0 + (hl - v) * 0.45) continue;
          // hull outline: a box with a pointed bow (the kits are boxes: close enough at water level)
          float bowK = smoothstep(hl * 0.35, hl, v);
          float halfB = hb * (1.0 - bowK * bowK * 0.8);
          vec2 q = vec2(abs(u) - halfB, abs(v) - hl);
          float dh = length(max(q, 0.0)) + min(max(q.x, q.y), 0.0);
          float spn = wSat(spd / 8.0);
          float contact = (1.0 - smoothstep(0.0, 0.9 + 2.2 * spn, dh)) * step(-0.3, dh);
          foam += contact * (0.45 + 0.55 * mix(0.3, 1.0, bowK) * (0.4 + spn));
          if (moving > 0.0) {
            float bb = hl - v; // behind the bow
            // Kelvin arms: thin foam ridges diverging from the bow, fading downstream
            float armD = abs(abs(u) - 0.3536 * bb - hb * 0.55);
            float arm = (1.0 - smoothstep(0.35, 1.2 + bb * 0.02, armD)) * step(0.0, bb) * exp(-bb / (a.w * 2.2));
            // prop wash: churned white water along the centre line, widening and decaying behind the stern
            float st = -(v + hl);
            float ww = hb * (0.75 + max(st, 0.0) * 0.045);
            float wash = step(0.0, st + 1.0) * exp(-max(st, 0.0) / (a.w * (0.9 + 1.2 * spn))) * (1.0 - smoothstep(0.35 * ww, ww, abs(u)));
            foam += (arm * 0.7 + wash * (0.55 + 0.45 * spn)) * moving;
            // disturbed (rougher, aerated) water inside the V
            float inV = step(0.0, bb) * (1.0 - smoothstep(0.3536 * bb + hb * 0.4, 0.3536 * bb + hb * 1.2, abs(u))) * exp(-bb / (a.w * 3.0));
            wake = max(wake, inV * moving);
          }
        }
        return vec2(foam, wake);
      }
      #endif
      vec3 river() {
        vec2 p = vWPw.xz;
        float dist = length(vWPw - cameraPosition); wDist = dist;
        float t = uWTime;
        float foot = max(length(fwidth(vLag)), 1e-4);
        // ---- sea detail (tidewater SeaDetail): wind-aligned, lightly domain-warped bands
        vec2 wdir = vec2(${f6(WIND_DIR[0])}, ${f6(WIND_DIR[1])});
        float g1 = texture(tWNoise, p / 620.0).r, g2 = texture(tWNoise, p / 230.0 + vec2(t * 0.0009, 0.37)).g;
        float gust = wSat((g1 * 0.62 + g2 * 0.38 - 0.5) * 2.4 + 0.5);
        float along = dot(p, wdir), across = dot(p, vec2(-wdir.y, wdir.x)) + (g2 - 0.5) * 26.0;
        float sl = texture(tWNoise, vec2(along / 1100.0, across / 70.0)).b;
        float slick = smoothstep(0.62, 0.76, sl) * (1.0 - gust * 0.8) * 0.9;
        float st = texture(tWNoise, vec2(along / 380.0, across / 11.0) + vec2(0.13, 0.71)).r;
        float brk = texture(tWNoise, vec2(along / 140.0, across / 40.0) + vec2(0.51, 0.29)).g;
        float streak = smoothstep(0.66, 0.82, st) * smoothstep(0.4, 0.62, brk) * 0.7;
        // current streaks along the rivers (z) (kept from the previous water: the refs' rivers are never one sheet)
        float s1 = texture(tWNoise, vec2(p.x / 34.0, p.y / 520.0) + vec2(t * 0.0008, t * 0.003)).g;
        streak = max(streak, smoothstep(0.6, 0.82, s1) * 0.45);
        // distance to the nearest shore (m, baked 8 m/px map): sheltered, silty water along the bulkheads
        wShore = 400.0;
        #ifdef HAS_SHORE
          wShore = texture(tShore, (p - uShoreBox.xy) / uShoreBox.zw).r * 400.0;
        #endif
        float nearS = 1.0 - smoothstep(6.0, 70.0, wShore);
        slick = wSat(slick + nearS * 0.3);
        wSlick = slick; wNearS = nearS; wStreak = streak; wGust = gust;
        float rough = mix(0.55, 1.45, gust) * (1.0 - slick * 0.7) * (1.0 - streak * 0.3);
        // ---- wave slopes: resolved Gerstner waves (analytic) + short detail normals (capillary chop)
        vec2 sl2 = vec2(0.0); float varU = 0.0; wCrest = 0.0;
        #ifdef HAS_WAVES
          vec4 ws = waveSlope(vLag, foot);
          float wk = uWaveAmp * mix(0.8, 1.15, gust) * (1.0 - 0.3 * slick);
          sl2 = ws.xy * wk; varU = ws.z * wk * wk; wCrest = ws.w;
        #endif
        vec2 pr1 = mat2(0.829, -0.559, 0.559, 0.829) * p;
        float fd1 = 1.0 - smoothstep(0.04, 0.35, foot), fd2 = 1.0 - smoothstep(0.15, 1.2, foot);
        vec2 dn = wn(p / 2.2 + vec2(t * 0.045, t * 0.031)) * 0.15 * fd1
                + wn(vec2(-p.y, p.x) / 3.6 + vec2(t * -0.03, t * 0.036)) * 0.12 * fd1
                + wn(pr1 / 9.0 + vec2(t * 0.012, -t * 0.009)) * 0.13 * fd2;
        dn *= rough;
        varU += (0.009 * (1.0 - fd1) + 0.004 * (1.0 - fd2)) * rough * rough;
        #ifndef HAS_WAVES
          // ponds: the previous normal-map water (no Gerstner waves)
          dn += (wn(p / 9.0 + vec2(t * 0.021, t * 0.013)) * 0.55 + wn(vec2(-p.y, p.x) / 14.0 + vec2(t * -0.012, t * 0.017)) * 0.45) * 0.12 * fd2;
        #endif
        vec2 slope = sl2 + dn;
        // ---- foam sources
        float foam = 0.0; wWake = 0.0;
        #ifdef HAS_RIP
          if (uRipBox.w > 0.5) {
            vec2 ru = (vLag - uRipBox.xy) / uRipBox.z;
            vec2 re = smoothstep(0.0, 0.08, ru) * smoothstep(1.0, 0.92, ru);
            float rk = re.x * re.y;
            float e = 1.0 / 256.0;
            float h0 = texture(tRip, ru).r;
            vec2 rs = vec2(texture(tRip, ru + vec2(e, 0.0)).r - texture(tRip, ru - vec2(e, 0.0)).r,
                           texture(tRip, ru + vec2(0.0, e)).r - texture(tRip, ru - vec2(0.0, e)).r) / (2.0 * e * uRipBox.z);
            slope += rs * rk;
            foam = max(foam, texture(tRip, ru).b * rk);
          }
        #endif
        #ifdef HAS_CONTACT
        {
          vec2 cu = (p - uContactBox.xy) / uContactBox.zw;
          if (cu.x > 0.0 && cu.y > 0.0 && cu.x < 1.0 && cu.y < 1.0) {
            float cd = texture(tContact, cu).r * 24.0;
            float fn = texture(tWNoise, p / 7.0 + vec2(t * 0.01, -t * 0.007)).b;
            // water sloshing against the wall: the band swells with the local crest and a slow lapping pulse
            float lap = 0.55 + 0.45 * sin(dot(p, vec2(0.11, -0.17)) + t * 1.1) * 0.5 + 0.35 * wCrest;
            float cf = (1.0 - smoothstep(0.1, 0.5 + 1.7 * fn + 0.9 * lap, cd));
            foam = max(foam, cf * (0.3 + 0.45 * lap) * smoothstep(0.25, 0.6, texture(tWNoise, p / 3.1 + vec2(-t * 0.02, t * 0.013)).r + 0.25 * lap));
            wShore = min(wShore, cd); // meniscus / wet contact line below
          }
        }
        #endif
        #ifdef HAS_BOATS
        {
          vec2 bf = boatFoam(p);
          foam = max(foam, bf.x); wWake = bf.y;
          rough *= 1.0 + 0.8 * wWake;
          varU += 0.02 * wWake;
        }
        #endif
        foam = max(foam, streak * 0.12 * smoothstep(0.4, 1.0, gust + 0.3));
        // whitecaps on the steepest crests in the gusts (sparse: a sheltered harbour, not the open sea)
        foam = max(foam, smoothstep(0.62, 0.95, wCrest) * gust * 0.35);
        wFoam = foamPattern(p, wSat(foam)) * (1.0 - smoothstep(600.0, 2500.0, dist)) + wSat(foam) * 0.35 * smoothstep(300.0, 2500.0, dist);
        wVarU = varU;
        wN = normalize(vec3(-slope.x, 1.0, -slope.y));
        // mirror distortion: waves smear the reflection vertically (screen space), less in the slicks; a mid-scale ripple
        // field that does not fade with distance, so far reflections break into wobbly bands
        vec2 rip = wn(vec2(p.x / 26.0, p.y / 7.0) + vec2(t * 0.011, -t * 0.019)) + 0.6 * wn(p / 61.0 + vec2(-t * 0.006, t * 0.009));
        wDisp = (sl2 * 0.55 + dn * 1.6) * (0.9 - 0.5 * slick) + rip * 0.09 * (1.0 - 0.5 * slick);
        // ---- roughness (GGX alpha^2): base + Cox-Munk unresolved capillaries + the variance of the filtered waves
        float mss = (0.003 + 0.0045 * rough);
        float unres = wSat(log2(max(foot, 1e-4) * 110.0 / 3.14159) / 9.0);
        wA2 = 0.028 * 0.028 + mss * 2.0 * unres + 2.0 * varU + wFoam * 0.2 + 0.03 * wWake;
        #ifndef NO_SSR
          wA2 += 0.004; // (ponds: wind-ruffled, the cloud reflection is never a crisp cubemap)
        #endif
        wR = clamp(pow(wA2, 0.25), 0.04, 0.7);
        // ---- body tint (turbidity varies): silty olive-brown along the shores, a little bluer mid-channel, current streaks
        vec3 c = uBodyRef;
        vec3 m1 = texture(tWNoise, p / 900.0 + vec2(0.0, t * 0.0015)).rgb;
        vec3 m2 = texture(tWNoise, vec2(p.x / 260.0, p.y / 1400.0) + vec2(0.31, t * 0.004)).rgb;
        c *= 0.85 + 0.3 * m1.r;
        c = mix(c, vec3(0.07, 0.085, 0.075), smoothstep(0.4, 0.8, m2.b) * 0.5);
        c = mix(c, vec3(0.06, 0.066, 0.055), nearS * 0.55);
        c = mix(c, c * vec3(0.8, 0.9, 1.05), smoothstep(150.0, 400.0, wShore));
        c *= 1.0 + 0.25 * streak;
        #ifdef HAS_SHORE
        {
          float fn = texture(tWNoise, p / 23.0 + vec2(t * 0.002, -t * 0.003)).g;
          float silt = (1.0 - smoothstep(10.0, 120.0, wShore)) * (0.55 + 0.45 * fn);
          c = mix(c, vec3(0.085, 0.08, 0.058), silt * 0.4);
        }
        #endif
        wTint = c / max(uBodyRef, vec3(1e-3));
        return c;
      }
      // Final radiance (tidewater WaterMaterial above / below water), view space N, V
      vec3 waterShade(vec3 N, vec3 V, bool front) {
        vec3 Nw = inverseTransformDirection(N, viewMatrix), Vw = inverseTransformDirection(V, viewMatrix);
        vec3 Lw = inverseTransformDirection(wLv, viewMatrix);
        vec3 sigA = uSigA, sigS = uSigS, sigT = sigA + sigS;
        vec3 bb = sigS * 0.035;
        vec3 albedoMS = bb * (0.33 * 4.0) / (sigA + bb);
        vec3 irr = wIrr / PI; // sky irradiance / PI (radiance of a white Lambertian)
        vec3 Ls = -refract(-Lw, vec3(0.0, 1.0, 0.0), ${f6(1 / IOR)}); // toward the sun, under water
        if (front) {
          float NdV = max(dot(N, V), 1e-4);
          float F = fresnelDielectric(NdV, ${f6(IOR)});
          // ---- sun glint (GGX, the roughness above), the sun light already includes the shadow
          vec3 H = normalize(wLv + V);
          float NdL = max(dot(N, wLv), 0.0), NdH = max(dot(N, H), 0.0), VdH = max(dot(V, H), 0.0);
          float a2 = wA2;
          float dd = NdH * NdH * (a2 - 1.0) + 1.0;
          float D = a2 / (dd * dd * PI);
          float gv = NdL * sqrt(NdV * NdV * (1.0 - a2) + a2), gl = NdV * sqrt(NdL * NdL * (1.0 - a2) + a2);
          float Vis = 0.5 / max(gv + gl, 1e-5);
          vec3 sunSpec = wSunL * min(D * Vis * fresnelDielectric(VdH, ${f6(IOR)}) * NdL, 400.0);
          // ---- the water body: refracted view ray into an infinitely deep turbid medium
          vec3 Tv = refract(-Vw, Nw, ${f6(1 / IOR)});
          Tv = normalize(vec3(Tv.x, min(Tv.y, -0.08), Tv.z));
          float muS = max(Ls.y, 0.1), muV = max(-Tv.y, 0.15);
          vec3 sunIn = wSunL * (1.0 - fresnelDielectric(max(Lw.y, 0.02), ${f6(IOR)}));
          vec3 kSun = sigT * (1.0 + muV / muS), kAmb = sigT * (1.0 + muV / 0.75);
          float phase = waterPhaseHG(dot(Tv, Ls), 0.86) * 0.7 + ${f6(0.3 / (4 * Math.PI))};
          vec3 inSun = sunIn * (sigS * phase + albedoMS * sigT / PI) / kSun;
          vec3 inAmb = irr * (sigS * 0.25 + albedoMS * sigT) / kAmb;
          // crest translucency: the sun through thin wave tips (green glow on the side-lit crests)
          vec2 vH = normalize(Vw.xz + 1e-5), lH = normalize(Lw.xz + 1e-5);
          float back = pow(wSat(dot(vH, -lH) * 0.6 + 0.4), 2.5);
          float crest = wSat(wCrest * 0.9 + 0.1) * (wSat((1.0 - Nw.y) * 4.0) + 0.25);
          vec3 sss = wSunL * vec3(0.12, 0.5, 0.4) * 0.05 * back * crest * smoothstep(0.0, 0.25, Lw.y);
          vec3 transmitted = (inSun + inAmb) * wTint + sss;
          // ---- foam: bright diffuse scatterer, wrapped sun + sky
          vec3 foamCol = (wSunL * (max(dot(Nw, Lw), 0.0) * 0.75 + 0.25) / PI + irr * 0.95) * 0.72;
          vec3 water = mix(transmitted, wRefl, F) + sunSpec + wGlit;
          // wet contact line: the meniscus darkens the last decimetres against walls / hulls
          water *= 1.0 - 0.35 * (1.0 - smoothstep(0.05, 0.5, wShore));
          return mix(water, foamCol + sunSpec * 0.05, wSat(wFoam));
        }
        // ---- seen from below: Snell's window (the sky through the surface) + total internal reflection of the body
        vec3 Nb = -N;
        float NdV = max(dot(Nb, V), 1e-4);
        float F = fresnelDielectric(NdV, ${f6(1 / IOR)});
        vec3 skyT = wRefl;
        vec3 Rr = reflect(-Vw, -Nw);
        float muU = max(Ls.y, 0.15);
        float phR = waterPhaseHG(dot(Rr, Ls), 0.86) * 0.7 + ${f6(0.3 / (4 * Math.PI))};
        vec3 kS = sigT * (1.0 - min(Rr.y, 0.0) / muU), kA = sigT * (1.0 - min(Rr.y, 0.0) / 0.8);
        vec3 eSun = wSunL * (1.0 - fresnelDielectric(max(Lw.y, 0.02), ${f6(IOR)}));
        vec3 deepCol = eSun * (sigS * phR + albedoMS * sigT / PI) / kS + irr * PI * (sigS * ${f6(1 / (4 * Math.PI))} + albedoMS * sigT / PI) / kA;
        vec3 foamUnder = (irr * PI + wSunL * 0.5) * 0.25 / PI;
        return mix(skyT * (1.0 - F) + deepCol * F, foamUnder, wSat(wFoam) * 0.7);
      }`)
      .replace('#include <map_fragment>', 'wFront = uCamBelow < 0.5; diffuseColor.rgb = river();')
      .replace('#include <roughnessmap_fragment>', 'float roughnessFactor = wR;')
      .replace('#include <normal_fragment_maps>', 'normal = normalize((viewMatrix * vec4(wN, 0.0)).xyz);')
      // the sun (first / only directional light) as the water sees it: colour x CSM shadow, view-space direction
      .replace('#include <lights_fragment_begin>', THREE.ShaderChunk.lights_fragment_begin
        .replace('directLight.color *= ( directLight.visible && receiveShadow ) ? csmShadow() : 1.0;',
          'wSh = ( directLight.visible && receiveShadow ) ? csmShadow() : 1.0; directLight.color *= wSh;')
        + `
        #if ( NUM_DIR_LIGHTS > 0 )
        {
          wSunL = directLight.color; wLv = directLight.direction;
          // (round 7) sun glitter: sparse sub-pixel facets on a finer, faster chop catch the sun (sparkling glint path)
          vec2 gp = vWPw.xz;
          vec2 gn = wn(gp / 2.3 + vec2(uWTime * 0.05, uWTime * 0.034)) + 0.8 * wn(vec2(-gp.y, gp.x) / 3.7 + vec2(-uWTime * 0.041, uWTime * 0.02));
          vec3 nG = normalize(wN + vec3(gn.x, 0.0, gn.y) * 0.22 * (1.0 - 0.6 * wSlick));
          vec3 nGv = normalize((viewMatrix * vec4(nG, 0.0)).xyz);
          vec3 Hh = normalize(directLight.direction + geometryViewDir);
          float gl = pow(clamp(dot(nGv, Hh), 0.0, 1.0), 700.0);
          float spark = smoothstep(0.62, 0.9, texture(tWNoise, gp / 5.0 + vec2(uWTime * 0.02, 0.0)).r);
          float gfade = 1.0 - smoothstep(900.0, 4000.0, wDist);
          wGlit = directLight.color * gl * spark * gfade * 18.0 * (1.0 - wSat(wFoam)); // on top of the GGX lobe
        }
        #endif`)
      .replace('#include <lights_fragment_maps>', `#include <lights_fragment_maps>
        wIrr = iblIrradiance;
        // sky reflection. The env map's lowest ~6 deg hold a generic city band (for the towers' IBL): open water at
        // grazing angles mirrors the horizon SKY instead, so the reflection is lifted above that band; unresolved
        // facets tilt the mean reflection toward the higher, darker sky (tidewater): gusts darken, slicks stay bright
        #if defined( USE_ENVMAP ) && defined( ENVMAP_TYPE_CUBE_UV )
        {
          vec3 nn = wFront ? normal : -normal;
          vec3 rvW = transformDirectionByInverseViewMatrix(reflect(-geometryViewDir, nn), viewMatrix);
          if (wFront) {
            float sigU = sqrt(max(wA2 - 0.0008, 0.0));
            float Rup = max(rvW.y, 0.004) + sigU * 1.3 * (1.0 - max(rvW.y, 0.0));
            rvW.y = max(Rup, 0.0) * 0.82 + 0.1;
          } else {
            // from below: the refracted ray into the air (Snell's window); total internal reflection -> the down direction
            vec3 Nw_ = transformDirectionByInverseViewMatrix(-nn, viewMatrix);
            vec3 Tt = refract(-transformDirectionByInverseViewMatrix(geometryViewDir, viewMatrix), -Nw_, ${f6(IOR)});
            rvW = dot(Tt, Tt) > 0.5 ? Tt : vec3(0.0, 1.0, 0.0);
          }
          radiance = textureCubeUV(envMap, envMapRotation * normalize(rvW), material.roughness).rgb * envMapIntensity;
        }
        #endif
        if (wFront && uReflOn > 0.5 && vRefl.w > 0.0) {
          vec2 ruv = vRefl.xy / vRefl.w;
          // ripple distortion that survives distance (sheared horizontally by the chop) + a vertical smear: real river
          // reflections are stretched / broken toward the viewer, never a crisp mirror
          vec2 d = vec2(wDisp.x * 0.7, wDisp.y * 1.6) * 0.22 / (1.0 + wDist * 0.00025);
          float spread = (0.004 + 0.034 * wR) * (1.0 - 0.5 * wSlick);
          float jit = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
          vec4 pr = vec4(0.0);
          for (int k = 0; k < 8; k++) {
            float o = (float(k) + jit) / 8.0 - 0.35;
            pr += texture(tRefl, ruv + d * (1.0 + 0.12 * float(k)) + vec2(o * spread * 0.25, o * spread));
          }
          pr /= 8.0;
          vec2 e = smoothstep(0.0, 0.03, ruv) * smoothstep(1.0, 0.97, ruv);
          // the mirror render has no aerial perspective: haze it toward the sky radiance with distance
          vec3 mir = mix(pr.rgb, radiance, 0.28 + 0.52 * smoothstep(200.0, 3500.0, wDist));
          float mw = mix(0.7, 0.9, wSlick) * mix(1.0, 0.5, smoothstep(0.2, 0.45, wR)) * (1.0 - 0.3 * wNearS);
          radiance = mix(radiance, mir, clamp(pr.a, 0.0, 1.0) * e.x * e.y * mw);
        }
        // wind fields modulate the sheen at every distance: glassy slicks mirror more of the bright sky, gust / ruffled
        // patches scatter it into a duller grey (large-scale mottling like the refs' Hudson / East River)
        radiance *= mix(0.9, 1.12, wSlick) * (1.0 + 0.1 * wStreak);
        wRefl = radiance;`)
      .replace('#include <opaque_fragment>', `outgoingLight = waterShade(normal, geometryViewDir, wFront);
        #include <opaque_fragment>`);
  };
  mat.customProgramCacheKey = () => 'city-river-v12' + (ssr ? '-ssr' : '') + (shore ? '-sh' : '') + (waves ? '-wv' : '') + (contact ? '-ct' : '')
    + (boats ? '-bt' : '') + (rip ? '-rp' : '') + body.join(',');
  return mat;
}

// planar mirror at y = WATER_Y: mirrored camera renders layers BIG_LAYER + REFL_LAYER into a low-res HDR target
function createMirror(renderer) {
  const size = new THREE.Vector2();
  renderer.getDrawingBufferSize(size);
  const rt = new THREE.WebGLRenderTarget(Math.max(256, Math.round(size.x / 3)), Math.max(144, Math.round(size.y / 3)), { type: THREE.HalfFloatType });
  const texMat = new THREE.Matrix4();
  const vcam = new THREE.PerspectiveCamera();
  vcam.layers.set(BIG_LAYER); vcam.layers.enable(REFL_LAYER);
  const bias = new THREE.Matrix4().set(0.5, 0, 0, 0.5, 0, 0.5, 0, 0.5, 0, 0, 0.5, 0.5, 0, 0, 0, 1);
  const _p = new THREE.Vector3(), _d = new THREE.Vector3(), _t = new THREE.Vector3(), _c = new THREE.Color(), _u = new THREE.Vector3();
  const Y = G.WATER_Y;
  let frame = 0;
  return {
    texture: rt.texture, texMat,
    render(scene, camera, hide) {
      camera.updateMatrixWorld();
      _p.setFromMatrixPosition(camera.matrixWorld);
      if (_p.y < Y + 0.3) return false;
      // inland at street level the rivers are hidden behind the blocks: skip the mirror
      if (_p.y < 45 && distToShore(_p.x, _p.z) > 260) return false;
      camera.getWorldDirection(_d);
      _t.copy(_p).add(_d);
      vcam.position.set(_p.x, 2 * Y - _p.y, _p.z);
      _u.set(0, 1, 0).applyQuaternion(camera.quaternion); _u.y = -_u.y; vcam.up.copy(_u);
      vcam.lookAt(_t.x, 2 * Y - _t.y, _t.z);
      vcam.projectionMatrix.copy(camera.projectionMatrix);
      vcam.projectionMatrixInverse.copy(camera.projectionMatrixInverse);
      vcam.updateMatrixWorld();
      texMat.copy(bias).multiply(vcam.projectionMatrix).multiply(vcam.matrixWorldInverse);
      frame++;
      for (const h of hide) h.visible = false;
      const prevRT = renderer.getRenderTarget();
      const prevAlpha = renderer.getClearAlpha(); renderer.getClearColor(_c);
      const prevAuto = renderer.shadowMap.autoUpdate, prevOn = renderer.shadowMap.enabled;
      renderer.shadowMap.autoUpdate = false; renderer.shadowMap.enabled = false; // cascades are fitted to the main camera
      renderer.setClearColor(0x000000, 0);
      renderer.setRenderTarget(rt);
      renderer.clear();
      renderer.render(scene, vcam);
      renderer.setRenderTarget(prevRT);
      renderer.setClearColor(_c, prevAlpha);
      renderer.shadowMap.autoUpdate = prevAuto; renderer.shadowMap.enabled = prevOn;
      for (const h of hide) h.visible = true;
      return true;
    },
  };
}

// distance-to-shore map (metres / 400 in R, 8 m/px) over the harbour: land polygons rasterised on a canvas, then a
// two-pass chamfer distance transform. Drives the silty near-shore tone / sheltered slicks of the river shader.
function shoreMap() {
  const X0 = -6400, Z0 = -8000, X1 = 6400, Z1 = 9600, PX = 8;
  const W = Math.round((X1 - X0) / PX), H = Math.round((Z1 - Z0) / PX);
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const g = cv.getContext('2d', { willReadFrequently: true });
  g.fillStyle = '#000'; g.fillRect(0, 0, W, H); g.fillStyle = '#fff';
  for (const pts of [LAND_POLY, ...FAR_LANDS.map(L => L.pts)]) {
    g.beginPath(); pts.forEach(([x, z], i) => { const u = (Math.max(-1e5, Math.min(1e5, x)) - X0) / PX, v = (Math.max(-1e5, Math.min(1e5, z)) - Z0) / PX; if (i) g.lineTo(u, v); else g.moveTo(u, v); });
    g.closePath(); g.fill();
  }
  const img = g.getImageData(0, 0, W, H).data;
  const D = new Float32Array(W * H);
  for (let i = 0; i < W * H; i++) D[i] = img[i * 4] > 127 ? 0 : 1e9;
  const a = PX, b = PX * Math.SQRT2;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const i = y * W + x; let d = D[i]; if (!d) continue;
    if (x > 0) d = Math.min(d, D[i - 1] + a); if (y > 0) { d = Math.min(d, D[i - W] + a); if (x > 0) d = Math.min(d, D[i - W - 1] + b); if (x < W - 1) d = Math.min(d, D[i - W + 1] + b); } D[i] = d; }
  for (let y = H - 1; y >= 0; y--) for (let x = W - 1; x >= 0; x--) { const i = y * W + x; let d = D[i]; if (!d) continue;
    if (x < W - 1) d = Math.min(d, D[i + 1] + a); if (y < H - 1) { d = Math.min(d, D[i + W] + a); if (x < W - 1) d = Math.min(d, D[i + W + 1] + b); if (x > 0) d = Math.min(d, D[i + W - 1] + b); } D[i] = d; }
  const out = new Uint8Array(W * H);
  for (let i = 0; i < W * H; i++) out[i] = Math.min(255, Math.round(D[i] / 400 * 255));
  const tex = new THREE.DataTexture(out, W, H, THREE.RedFormat, THREE.UnsignedByteType);
  tex.magFilter = THREE.LinearFilter; tex.minFilter = THREE.LinearFilter; tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping;
  tex.needsUpdate = true;
  return { texture: tex, box: new THREE.Vector4(X0, Z0, X1 - X0, Z1 - Z0) };
}


// (water-effects) fine contact map for the foam where the water touches something: distance (m / 24 in R, 2 m/px) to
// the nearest wet edge (seawalls, bulkheads, pier decks: water.js buildWetBands segments), land, or solid crossing the
// water line (piles, pier piers, bridge towers / anchorages, docked hulls) over the rivers around the island
function contactMap(segs, solids) {
  const X0 = -1800, Z0 = -4300, X1 = 2000, Z1 = 4500, PX = 2, CAP = 24;
  const W = Math.round((X1 - X0) / PX), H = Math.round((Z1 - Z0) / PX);
  const cv = document.createElement('canvas'); cv.width = W; cv.height = H;
  const g = cv.getContext('2d', { willReadFrequently: true });
  g.fillStyle = '#000'; g.fillRect(0, 0, W, H); g.fillStyle = '#fff'; g.strokeStyle = '#fff';
  const U = (x) => (Math.max(-1e5, Math.min(1e5, x)) - X0) / PX, V = (z) => (Math.max(-1e5, Math.min(1e5, z)) - Z0) / PX;
  for (const pts of [LAND_POLY, ...FAR_LANDS.map(L => L.pts)]) {
    g.beginPath(); pts.forEach(([x, z], i) => { if (i) g.lineTo(U(x), V(z)); else g.moveTo(U(x), V(z)); });
    g.closePath(); g.fill();
  }
  g.lineWidth = 1.2; g.beginPath();
  for (const s of segs ?? []) { g.moveTo(U(s.ax), V(s.az)); g.lineTo(U(s.bx), V(s.bz)); }
  g.stroke();
  let nS = 0;
  if (solids) {
    const b = solids.b, Y = G.WATER_Y;
    for (let i = 0; i < solids.count; i++) {
      const j = i * 6;
      if (b[j + 1] > Y + 0.8 || b[j + 4] < Y - 0.5) continue;
      const x0 = U(b[j]), z0 = V(b[j + 2]), x1 = U(b[j + 3]), z1 = V(b[j + 5]);
      if (x1 < 0 || z1 < 0 || x0 > W || z0 > H) continue;
      g.fillRect(x0, z0, Math.max(1, x1 - x0), Math.max(1, z1 - z0)); nS++;
    }
  }
  const img = g.getImageData(0, 0, W, H).data;
  const D = new Float32Array(W * H);
  for (let i = 0; i < W * H; i++) D[i] = img[i * 4] > 90 ? 0 : 1e9;
  const a = PX, bD = PX * Math.SQRT2;
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) { const i = y * W + x; let d = D[i]; if (!d) continue;
    if (x > 0) d = Math.min(d, D[i - 1] + a); if (y > 0) { d = Math.min(d, D[i - W] + a); if (x > 0) d = Math.min(d, D[i - W - 1] + bD); if (x < W - 1) d = Math.min(d, D[i - W + 1] + bD); } D[i] = d; }
  for (let y = H - 1; y >= 0; y--) for (let x = W - 1; x >= 0; x--) { const i = y * W + x; let d = D[i]; if (!d) continue;
    if (x < W - 1) d = Math.min(d, D[i + 1] + a); if (y < H - 1) { d = Math.min(d, D[i + W] + a); if (x < W - 1) d = Math.min(d, D[i + W + 1] + bD); if (x > 0) d = Math.min(d, D[i + W - 1] + bD); } D[i] = d; }
  const out = new Uint8Array(W * H);
  // the edge pixel itself sits ~half a pixel from the real edge
  for (let i = 0; i < W * H; i++) out[i] = Math.min(255, Math.round(Math.max(0, D[i] - PX * 0.5) / CAP * 255));
  return { data: out, W, H, box: new THREE.Vector4(X0, Z0, X1 - X0, Z1 - Z0), solids: nS };
}

function placeholderTex(v = 255, format = THREE.RedFormat) {
  const n = format === THREE.RGBAFormat ? 4 : 1;
  const t = new THREE.DataTexture(new Uint8Array(n).fill(v), 1, 1, format, THREE.UnsignedByteType);
  t.needsUpdate = true; return t;
}

export function buildWater({ scene, T, renderer = null }) {
  const Q = getQuality();
  const mirror = renderer ? createMirror(renderer) : null;
  let shore = null; try { shore = shoreMap(); } catch (e) { console.warn('[water] shore map', e); }
  const cdlod = new CDLOD({ gridSize: Q.waterGrid ?? 32, leafSize: 8, levels: 15, minY: G.WATER_Y - 1.5, maxY: G.WATER_Y + 1.5 });
  const contact = { texture: placeholderTex(255), box: new THREE.Vector4(0, 0, 1, 1) };
  const ripples = renderer ? createRipples(renderer) : null;
  const rip = ripples ?? { texture: placeholderTex(0, THREE.RGBAFormat), box: new THREE.Vector4(0, 0, 1, 0) };
  const spray = createSpray({ scene, max: Q.waterSpray ?? 2400 });
  const gulls = createGulls({ scene, scale: Q.gulls ?? 1 });
  const mat = createRiverMaterial(T, mirror, { shore, waves: true, cdlod, contact, boats: true, rip });
  const U = mat.userData.uniforms;
  const mesh = new THREE.Mesh(cdlod.geometry, mat);
  mesh.name = 'water';
  mesh.receiveShadow = true; mesh.frustumCulled = false;
  scene.add(mesh);
  // horizon skirt: the flat world would end at the camera's far plane in a line below the true horizon. A ring wall
  // just inside the far plane, centred on the camera, rising from the water to the camera's height, fills the last
  // fraction of a degree down to the horizon with (fully aerial-perspective fogged) distant water / shore.
  const skirt = horizonSkirt();
  scene.add(skirt);
  // (water-effects) the river bed (only drawn while the camera is at / under the surface): dark silt, mottled
  const bed = riverBed(T);
  scene.add(bed);
  let t = 0, boats = null, camBelow = false;
  const root = () => { let o = mesh; while (o.parent) o = o.parent; return o; };
  const _c = new THREE.Vector3();
  const water = {
    mesh, material: mat, skirt, cdlod, uniforms: U, ripples, spray, gulls,
    get time() { return t; },
    // surface height at the world point (x, z) (waves only; the splash ripples are GPU-side)
    heightAt: (x, z) => G.WATER_Y + waveHeight(x, z, t),
    get cameraBelow() { return camBelow; },
    // (city.js, once everything is built) bake the contact foam map from the wet edges + the solids at the water line
    setContacts({ segs, solids }) {
      const t0 = performance.now();
      try {
        const c = contactMap(segs, solids);
        const tex = new THREE.DataTexture(c.data, c.W, c.H, THREE.RedFormat, THREE.UnsignedByteType);
        tex.magFilter = tex.minFilter = THREE.LinearFilter; tex.wrapS = tex.wrapT = THREE.ClampToEdgeWrapping; tex.needsUpdate = true;
        U.tContact.value = tex; U.uContactBox.value.copy(c.box);
        console.log(`[water] contact map ${c.W}x${c.H} (${c.solids} solids at the water line) ${(performance.now() - t0).toFixed(0)} ms`);
      } catch (e) { console.warn('[water] contact map', e); }
    },
    // boats.js: { boats: [{x, z, h, type, docked}], kit: {type: {len, beam, speed}} } -> hull / wake foam
    setBoats(b) { boats = b; },
    // a body hitting the water at (x, z): crater + rings in the ripple sim, foam, a crown of drops, spray column, mist
    splash(x, z, strength = 1, vx = 0, vz = 0) {
      const h = water.heightAt(x, z), s = Math.max(0.2, Math.min(strength, 1.5));
      ripples?.drop(x, z, 1.4 + 1.2 * s, -0.45 * s, 1);
      ripples?.drop(x, z, 3.2 + 2.5 * s, 0.12 * s, 0.6);
      spray.splash(x, h, z, s, vx, vz);
    },
    // something moving through the surface (a swimmer, a body dragged through the water): a travelling wake
    stir(x, z, strength = 0.3, foam = 0.4) { ripples?.drop(x, z, 0.9, -0.05 * strength, foam); },
    update(dt, camera) {
      t += dt; U.uWTime.value = t; U.uWaveT.value = t;
      if (camera) {
        cdlod.update(camera);
        camera.getWorldPosition(_c);
        if (ripples) { ripples.update(dt, _c); U.tRip.value = ripples.texture; }
        spray.update(dt, water);
        gulls.update(dt);
        // bow spray of the nearby moving boats
        if (boats) for (const b of boats.boats) {
          if (b.docked) continue;
          const k = boats.kit[b.type], dx = b.x - _c.x, dz = b.z - _c.z;
          if (dx * dx + dz * dz > 260 * 260 || Math.random() > dt * k.speed * 1.6) continue;
          const sx = Math.sin(b.h), cz = Math.cos(b.h), side = Math.random() < 0.5 ? -1 : 1, hl = k.len * 0.5, hb = k.beam * 0.3;
          const x = b.x + sx * hl * 0.92 + cz * hb * side, z = b.z + cz * hl * 0.92 - sx * hb * side, y = water.heightAt(x, z);
          const out = 1 + Math.random() * 1.5;
          spray.emit({ kind: SPRAY, x, y: y + 0.2, z, vx: sx * k.speed + cz * side * out, vy: 1.2 + Math.random() * 1.5, vz: cz * k.speed - sx * side * out, size: 0.4 + Math.random() * 0.3 * k.speed / 6, life: 0.9 });
          for (let i = 0; i < 4; i++) spray.emit({ kind: DROP, x, y: y + 0.2, z, vx: sx * k.speed + cz * side * (out + Math.random() * 2), vy: 1.5 + Math.random() * 2.5,
            vz: cz * k.speed - sx * side * (out + Math.random() * 2), size: 0.03 + Math.random() * 0.03, life: 2 });
        }
        camBelow = _c.y < water.heightAt(_c.x, _c.z);
        U.uCamBelow.value = camBelow ? 1 : 0;
        bed.visible = _c.y < water.heightAt(_c.x, _c.z) + 2.5;
        if (boats) {
          // the nearest MAX_BOATS boats (hull contact + wake foam)
          const list = boats.boats, kit = boats.kit;
          const near = list.map(b => ({ b, d: (b.x - _c.x) ** 2 + (b.z - _c.z) ** 2 })).filter(o => o.d < 700 * 700 + _c.y * _c.y * 4).sort((p, q) => p.d - q.d).slice(0, MAX_BOATS); // far foam is sub-pixel
          near.forEach(({ b }, i) => {
            const k = kit[b.type];
            U.uBoatA.value[i].set(b.x, b.z, b.h, k.len);
            U.uBoatB.value[i].set(k.beam, b.docked ? 0 : k.speed, b.docked ? 1 : 0, 0);
          });
          U.uBoatN.value = near.length;
        }
        const R = camera.far * 0.94;
        skirt.position.set(_c.x, G.WATER_Y, _c.z);
        skirt.scale.set(R, Math.max(2, _c.y - G.WATER_Y + 1), R);
        skirt.updateMatrixWorld();
        if (mirror) U.uReflOn.value = mirror.render(root(), camera, [mesh, skirt]) ? 1 : 0;
      }
    },
  };
  return water;
}

function riverBed(T) {
  const g = new THREE.PlaneGeometry(16000, 16000, 1, 1).rotateX(-Math.PI / 2).translate(0, G.WATER_Y - 9, 0);
  const m = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.95, metalness: 0 });
  m.defines = { NO_WET: '', NO_SSR: '' };
  m.onBeforeCompile = (sh) => {
    sh.uniforms.tBedN = { value: T.noise };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vBedP;')
      .replace('#include <fog_vertex>', '#include <fog_vertex>\nvBedP = (modelMatrix * vec4(transformed, 1.0)).xz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nuniform sampler2D tBedN; varying vec2 vBedP;')
      .replace('#include <map_fragment>', `{
        vec3 a = texture(tBedN, vBedP / 37.0).rgb, b = texture(tBedN, vBedP / 5.3).rgb, c = texture(tBedN, vBedP / 1.1).rgb;
        vec3 silt = vec3(0.16, 0.14, 0.1) * (0.7 + 0.5 * a.r) * (0.85 + 0.3 * b.g);
        silt = mix(silt, vec3(0.08, 0.1, 0.06), smoothstep(0.55, 0.8, a.g) * 0.6); // algae / weed patches
        silt = mix(silt, vec3(0.22, 0.21, 0.19), smoothstep(0.7, 0.9, c.b) * 0.5);  // pebbles / shell grit
        diffuseColor.rgb = silt;
      }`);
  };
  m.customProgramCacheKey = () => 'river-bed-v1';
  const mesh = new THREE.Mesh(g, m);
  mesh.name = 'riverBed'; mesh.receiveShadow = true; mesh.visible = false;
  return mesh;
}

function horizonSkirt(n = 180) {
  const P = [], N = [], C = [], I = [];
  const land = [0.3, 0.3, 0.29], water = [0.14, 0.17, 0.19];
  // direction classes (from the island): west (New Jersey), east (Long Island), north (Bronx / Westchester);
  // south: open ocean past the Narrows
  const colAt = (a) => { const z = Math.sin(a); return z > 0.3 ? water : land; };
  for (let i = 0; i <= n; i++) {
    const a = i / n * Math.PI * 2, x = Math.cos(a), z = Math.sin(a), c = colAt(a);
    P.push(x, 0, z, x, 1, z); N.push(0, 1, 0, 0, 1, 0); C.push(...c, ...c);
    if (i < n) { const b = i * 2; I.push(b, b + 1, b + 2, b + 1, b + 3, b + 2); }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(N, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(C, 3));
  g.setIndex(I);
  const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 1, side: THREE.DoubleSide }));
  m.name = 'horizonSkirt'; m.frustumCulled = false; m.matrixAutoUpdate = false;
  return m;
}

// Wet tidal band along vertical water edges (seawalls, bulkheads, pier decks, piles, anchorages): a dark, algae-stained
// strip from just below the water line up ~1.1 m, fading out with a ragged top edge. segs: [{ax, az, bx, bz, nx, nz}]
// (outward normal toward the water). One transparent mesh, 2 cm proud of the wall (no z-fight, no collision change).
export function buildWetBands({ scene, T, segs, y0 = G.WATER_Y - 0.25, h = 1.35 }) {
  const P = [], N = [], UV = [], I = [];
  let v = 0;
  for (const s of segs) {
    const L = Math.hypot(s.bx - s.ax, s.bz - s.az); if (L < 0.05) continue;
    const o = 0.02;
    const ax = s.ax + s.nx * o, az = s.az + s.nz * o, bx = s.bx + s.nx * o, bz = s.bz + s.nz * o;
    P.push(ax, y0, az, bx, y0, bz, bx, y0 + h, bz, ax, y0 + h, az);
    for (let k = 0; k < 4; k++) N.push(s.nx, 0, s.nz);
    const u0 = (s.ax * 0.7 + s.az * 0.3), u1 = u0 + L;
    UV.push(u0, 0, u1, 0, u1, 1, u0, 1);
    // wind so the face points along the normal
    const cx = (bz - az) * h, cz = -(bx - ax) * h; // (b-a) x up
    if (cx * s.nx + cz * s.nz <= 0) I.push(v, v + 1, v + 2, v, v + 2, v + 3); else I.push(v, v + 2, v + 1, v, v + 3, v + 2);
    v += 4;
  }
  if (!v) return null;
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(N, 3));
  g.setAttribute('uv', new THREE.Float32BufferAttribute(UV, 2));
  g.setIndex(new THREE.Uint32BufferAttribute(I, 1));
  g.computeBoundingSphere();
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.35, transparent: true, depthWrite: false,
    polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -2 });
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.tWetN = { value: T.noise };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec2 vWetUv;')
      .replace('#include <uv_vertex>', '#include <uv_vertex>\nvWetUv = uv;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nuniform sampler2D tWetN; varying vec2 vWetUv;')
      .replace('#include <map_fragment>', `{
        float u = vWetUv.x, y = vWetUv.y;
        vec3 nz = texture(tWetN, vec2(u / 9.0, 0.37)).rgb, nz2 = texture(tWetN, vec2(u / 2.1, y * 0.4 + 0.1)).rgb;
        float top = 0.45 + 0.35 * nz.r + 0.15 * nz2.g;            // ragged high-water line
        float a = 1.0 - smoothstep(top - 0.12, top + 0.04, y);
        float algae = 1.0 - smoothstep(0.1, 0.35, y);              // green-black slime right at the water line
        vec3 c = mix(vec3(0.07, 0.065, 0.055), vec3(0.04, 0.06, 0.035), algae);
        c *= 0.8 + 0.4 * nz2.b;
        // streaks running down from the high-water line
        a = max(a, (1.0 - smoothstep(0.0, 0.9, y)) * smoothstep(0.62, 0.8, texture(tWetN, vec2(u / 0.9, 0.71)).r) * 0.6);
        diffuseColor = vec4(c, a * 0.88);
      }`);
  };
  mat.customProgramCacheKey = () => 'wet-band-v1';
  const m = new THREE.Mesh(g, mat);
  m.name = 'wetBands'; m.receiveShadow = true; m.renderOrder = 1;
  scene.add(m);
  return m;
}
