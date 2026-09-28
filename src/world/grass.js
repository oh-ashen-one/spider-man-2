// OWNER: city agent (pinata-and-trees). Real grass blades on the Central Park lawns near the camera.
// Adapted from dgreenheck/ez-tree src/app/grass.js (MIT, © Daniel Greenheck): instanced clumps of blades with
// patchy density and world-space simplex wind (position.y-weighted sway). Changes for the city:
//  - procedural clump (5 curved, tapered blades) instead of the demo's grass.glb
//  - GPU-anchored instancing: one fixed jittered grid of clumps over a square around the camera, wrapped
//    toroidally in the vertex shader, so every clump keeps its world position while the camera moves (no CPU repack,
//    no swimming); blades shrink to nothing toward the ring's edge, where the existing shader lawn (ground.js) remains
//  - a baked park mask (1 m texels): R = density (mowed meadows / rough meadow edges / woodland floor / nothing on
//    paths, water, rock outcrops and the museum lot), G = blade height
//  - lit like the lawn (normals bent up) so the blades melt into the ground at distance; receives CSM shadows
//   const g = buildGrass({ scene, parkPaths, density });  g.update(dt, camera)   (density: quality `grass`, 0 = off)
import * as THREE from 'three';
import { G, PARK_WATER } from './layout.js';
import { PARK_SITES, PARK_ROCKS } from './park.js';
import { meadowDist, PARK_MEADOWS } from './trees.js';
import { GY } from './ground.js';

const R = 32;            // blade ring radius (m)
const S = R * 2;          // wrapped square
const PER_M2 = 4.5;       // clumps per m^2 at density 1

function clumpGeometry() {
  const P = [], N = [], H = [], I = [];
  const blades = 7, segs = 2;
  let seed = 7; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let b = 0; b < blades; b++) {
    const a = rnd() * Math.PI * 2, r = 0.02 + rnd() * 0.12, lean = 0.12 + rnd() * 0.3, ha = rnd() * Math.PI * 2;
    const ox = Math.cos(a) * r, oz = Math.sin(a) * r, w = 0.006 + rnd() * 0.006, hk = 0.6 + rnd() * 0.55;
    const dx = Math.cos(ha), dz = Math.sin(ha), px = -dz, pz = dx; // lean direction, blade width direction
    const v0 = P.length / 3;
    for (let s = 0; s <= segs; s++) {
      const t = s / segs, y = t * hk, bend = lean * t * t, ww = w * (1 - t * 0.85);
      for (const side of [-1, 1]) {
        P.push(ox + dx * bend + px * ww * side, y, oz + dz * bend + pz * ww * side);
        N.push(dx * 0.3, 1, dz * 0.3); H.push(t);
      }
    }
    for (let s = 0; s < segs; s++) { const k = v0 + s * 2; I.push(k, k + 1, k + 3, k, k + 3, k + 2); }
  }
  const g = new THREE.InstancedBufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(N, 3));
  g.setAttribute('aH', new THREE.Float32BufferAttribute(H, 1));
  g.setIndex(I);
  return g;
}

// park density / height mask
function parkMask(parkPaths) {
  const P = G.PARK, x0 = Math.floor(P.x0) - 2, z0 = Math.floor(P.z0) - 2;
  const W = Math.ceil(P.x1 - P.x0) + 4, H = Math.ceil(P.z1 - P.z0) + 4;
  const D = new Uint8Array(W * H * 4);
  const t0 = performance.now();
  // water (+ a 2 m bank): scanline-filled pond polygons, dilated
  const wet = new Uint8Array(W * H);
  for (const w of PARK_WATER) {
    const pts = w.pts;
    for (let j = 0; j < H; j++) {
      const z = z0 + j + 0.5, xs = [];
      for (let a = 0, b = pts.length - 1; a < pts.length; b = a++) {
        const [xa, za] = pts[a], [xb, zb] = pts[b];
        if ((za > z) !== (zb > z)) xs.push(xa + (z - za) / (zb - za) * (xb - xa));
      }
      xs.sort((p, q) => p - q);
      for (let k = 0; k + 1 < xs.length; k += 2) for (let i = Math.max(0, Math.floor(xs[k] - x0)); i <= Math.min(W - 1, Math.ceil(xs[k + 1] - x0)); i++) wet[j * W + i] = 1;
    }
  }
  for (let pass = 0; pass < 2; pass++) { // 2 x 1-texel dilation
    const src = wet.slice();
    for (let j = 1; j < H - 1; j++) for (let i = 1; i < W - 1; i++) { const k = j * W + i; if (!src[k] && (src[k - 1] | src[k + 1] | src[k - W] | src[k + W])) wet[k] = 1; }
  }
  const ms = PARK_MEADOWS.map(m => ({ m, r: Math.max(m.rx, m.rz) * 1.45 }));
  for (let j = 0; j < H; j++) for (let i = 0; i < W; i++) {
    const x = x0 + i + 0.5, z = z0 + j + 0.5, k = (j * W + i) * 4;
    if (x < P.x0 + 1 || x > P.x1 - 1 || z < P.z0 + 1 || z > P.z1 - 1 || wet[j * W + i]) continue;
    const m = ms.some(q => Math.abs(x - q.m.x) < q.r && Math.abs(z - q.m.z) < q.r) ? meadowDist(x, z) : 9;
    let dens, hgt;
    if (m < 0.97) { dens = 1; hgt = 0.05; }                               // mowed lawn: short, dense
    else if (m < 1.3) { dens = 1; hgt = 0.35 + (m - 0.97) * 1.5; }         // rough, taller meadow edge
    else { dens = 0.5; hgt = 0.3; }                                       // woodland floor: sparse tufts in the leaf litter
    D[k] = dens * 255; D[k + 1] = Math.min(1, hgt) * 255; D[k + 3] = 255;
  }
  const clear = (xa, za, xb, zb, fn) => {
    for (let j = Math.max(0, Math.floor(za - z0)); j <= Math.min(H - 1, Math.ceil(zb - z0)); j++)
      for (let i = Math.max(0, Math.floor(xa - x0)); i <= Math.min(W - 1, Math.ceil(xb - x0)); i++) { if (fn(x0 + i + 0.5, z0 + j + 0.5)) D[(j * W + i) * 4] = 0; }
  };
  for (const p of parkPaths ?? []) for (let n = 1; n < p.pts.length; n++) {
    const a = p.pts[n - 1], b = p.pts[n], w = p.w / 2 + 0.35;
    const dx = b[0] - a[0], dz = b[1] - a[1], L2 = dx * dx + dz * dz || 1;
    clear(Math.min(a[0], b[0]) - w, Math.min(a[1], b[1]) - w, Math.max(a[0], b[0]) + w, Math.max(a[1], b[1]) + w, (x, z) => {
      const t = Math.max(0, Math.min(1, ((x - a[0]) * dx + (z - a[1]) * dz) / L2));
      return Math.hypot(x - a[0] - dx * t, z - a[1] - dz * t) < w;
    });
  }
  for (const r of Object.values(PARK_SITES)) clear(r.x0 - 1, r.z0 - 1, r.x1 + 1, r.z1 + 1, () => true);
  for (const [rx, rz, rr] of PARK_ROCKS) clear(rx - rr, rz - rr, rx + rr, rz + rr, (x, z) => Math.hypot(x - rx, z - rz) < rr * 0.8);
  const tex = new THREE.DataTexture(D, W, H, THREE.RGBAFormat);
  tex.magFilter = THREE.LinearFilter; tex.minFilter = THREE.LinearFilter; tex.needsUpdate = true;
  console.log(`[grass] park mask ${W}x${H} in ${(performance.now() - t0).toFixed(0)} ms`);
  return { tex, rect: new THREE.Vector4(x0, z0, W, H) };
}

export function buildGrass({ scene, parkPaths, density = 1 }) {
  if (!(density > 0)) return { update() {} };
  const geo = clumpGeometry();
  const n = Math.round(S * S * PER_M2 * density), side = Math.ceil(Math.sqrt(n)), step = S / side;
  const off = new Float32Array(side * side * 4);
  let seed = 12345; const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  for (let j = 0, k = 0; j < side; j++) for (let i = 0; i < side; i++, k++) off.set([(i + rnd()) * step, (j + rnd()) * step, rnd(), rnd() * Math.PI * 2], k * 4);
  geo.setAttribute('aOff', new THREE.InstancedBufferAttribute(off, 4));
  geo.instanceCount = side * side;
  const mask = parkMask(parkPaths);
  const uni = {
    tMask: { value: mask.tex }, uMask: { value: mask.rect }, uCam: { value: new THREE.Vector3() }, uTime: { value: 0 },
    uY: { value: GY.GRASS }, uR: { value: R }, uS: { value: S },
  };
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.92, side: THREE.DoubleSide });
  mat.onBeforeCompile = (sh) => {
    Object.assign(sh.uniforms, uni);
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>
      attribute vec4 aOff; attribute float aH; uniform sampler2D tMask; uniform vec4 uMask; uniform vec3 uCam; uniform float uTime;
      uniform float uY; uniform float uR; uniform float uS; varying float vGH; varying vec3 vGC;
      vec3 gMod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec2 gMod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec3 gPermute(vec3 x) { return gMod289(((x * 34.0) + 1.0) * x); }
      float gSimplex2d(vec2 v) { // (ez-tree grass.js, MIT)
        const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
        vec2 i = floor(v + dot(v, C.yy)); vec2 x0 = v - i + dot(i, C.xx);
        vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
        vec4 x12 = x0.xyxy + C.xxzz; x12.xy -= i1;
        i = gMod289(i);
        vec3 p = gPermute(gPermute(i.y + vec3(0.0, i1.y, 1.0)) + i.x + vec3(0.0, i1.x, 1.0));
        vec3 m = max(0.5 - vec3(dot(x0, x0), dot(x12.xy, x12.xy), dot(x12.zw, x12.zw)), 0.0); m = m * m; m = m * m;
        vec3 x = 2.0 * fract(p * C.www) - 1.0; vec3 h = abs(x) - 0.5; vec3 ox = floor(x + 0.5); vec3 a0 = x - ox;
        m *= 1.79284291400159 - 0.85373472095314 * (a0 * a0 + h * h);
        vec3 g; g.x = a0.x * x0.x + h.x * x0.y; g.yz = a0.yz * x12.xz + h.yz * x12.yw;
        return 130.0 * dot(m, g);
      }`)
      .replace('#include <beginnormal_vertex>', `#include <beginnormal_vertex>
      objectNormal = normalize(objectNormal * vec3(0.35, 3.0, 0.35));`) // bent up: shaded like the lawn under it
      .replace('#include <begin_vertex>', `
      // world-anchored toroidal wrap around the camera
      vec2 gw = uCam.xz + mod(aOff.xy - uCam.xz + 0.5 * uS, uS) - 0.5 * uS;
      float gd = length(gw - uCam.xz);
      vec4 gm = textureLod(tMask, (gw - uMask.xy) / uMask.zw, 0.0);
      float gk = step(aOff.z, gm.r) * (1.0 - smoothstep(uR * 0.62, uR, gd));
      float gh = gk * (0.06 + 0.4 * gm.g) * (0.7 + 0.6 * fract(aOff.z * 7.31));
      float cs = cos(aOff.w), sn = sin(aOff.w);
      vec3 transformed = vec3(position.x * cs - position.z * sn, position.y * gh, position.x * sn + position.z * cs) * vec3(gk, 1.0, gk);
      // wind (ez-tree grass: position.y-weighted, world-space simplex offset) + a slow gust field
      float wo = 6.2831 * gSimplex2d(gw / 18.0);
      float gust = 0.5 + 0.5 * gSimplex2d(gw / 60.0 - uTime * 0.08);
      vec2 sway = vec2(0.32, 0.24) * aH * aH * gh * (0.4 + 0.9 * gust) * sin(uTime * 1.6 + wo) * cos(uTime * 1.1 + wo);
      transformed.xz += sway;
      transformed += vec3(gw.x, uY - 0.01, gw.y);
      vGH = aH;
      float ph = gSimplex2d(gw / 7.0) * 0.5 + 0.5;
      vGC = mix(vec3(0.17, 0.2, 0.045), vec3(0.23, 0.26, 0.06), ph) * mix(0.85, 1.12, fract(aOff.z * 3.7));
      vGC = mix(vGC, vec3(0.34, 0.27, 0.1), step(0.92, fract(aOff.z * 11.3)) * 0.8); // the odd dry, straw blade`);
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      varying float vGH; varying vec3 vGC;`)
      .replace('#include <color_fragment>', `#include <color_fragment>
      diffuseColor.rgb = vGC * mix(0.8, 1.04, vGH);`) // a little darker at the root, sunlit tips
      .replace('#include <normal_fragment_begin>', THREE.ShaderChunk.normal_fragment_begin.replace('normal *= faceDirection;', '')); // both faces lit as the lawn
  };
  mat.customProgramCacheKey = () => 'park-grass-v2';
  const mesh = new THREE.Mesh(geo, mat);
  mesh.name = 'park-grass'; mesh.frustumCulled = false; mesh.castShadow = false; mesh.receiveShadow = true; mesh.visible = false;
  scene.add(mesh);
  console.log(`[grass] ${geo.instanceCount} clumps (${(geo.instanceCount * geo.index.count / 3 / 1e3).toFixed(0)}k tris max)`);
  const P = G.PARK;
  let t = 0;
  return {
    mesh,
    update(dt, camera) {
      t += dt; uni.uTime.value = t;
      const c = camera.position;
      // only near the park and close to the ground (blades are invisible from swing height beyond ~45 m anyway)
      const dx = Math.max(P.x0 - c.x, 0, c.x - P.x1), dz = Math.max(P.z0 - c.z, 0, c.z - P.z1);
      mesh.visible = Math.hypot(dx, dz) < R && c.y < GY.GRASS + R * 0.9;
      uni.uCam.value.copy(c);
    },
  };
}
