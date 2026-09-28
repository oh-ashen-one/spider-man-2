// (water-effects) Seagulls soaring over the rivers and the harbour. Adapted from dgreenheck/tidewater
// src/world/Gulls.js (MIT, (c) 2026 DRG Software Solutions LLC): each bird circles its own thermal, banking into the
// turn, with occasional flapping bursts and the bent ("M") wing; everything is animated in the vertex shader from time
// and per-instance parameters (no CPU work per frame, one draw call). Ported from WGSL to a three.js r186
// MeshStandardMaterial vertex stage, so the birds are lit / shadowed / fogged like the rest of the city.
import * as THREE from 'three';

// ~1.3 m wingspan gull: slim body, bent wings with grey mantle and black tips, white underside
function gullGeometry() {
  const pos = [], col = [], side = [], span = [], idx = [];
  const white = [0.92, 0.92, 0.9], grey = [0.55, 0.58, 0.62], black = [0.06, 0.06, 0.07], bill = [0.85, 0.7, 0.2];
  const v = (x, y, z, c, s, sp) => { pos.push(x, y, z); col.push(...c); side.push(s); span.push(sp); return pos.length / 3 - 1; };
  const nose = v(0, 0.01, 0.26, bill, 0, 0), tail = v(0, 0.0, -0.24, white, 0, 0);
  const lt = v(-0.045, 0.03, 0.02, white, 0, 0), rt = v(0.045, 0.03, 0.02, white, 0, 0);
  const lb = v(-0.04, -0.03, 0.02, white, 0, 0), rb = v(0.04, -0.03, 0.02, white, 0, 0);
  idx.push(nose, rt, lt, nose, lb, rb, nose, lt, lb, nose, rb, rt, tail, lt, rt, tail, rb, lb, tail, lb, lt, tail, rt, rb);
  for (const s of [-1, 1]) {
    const ls = v(s * 0.04, 0.02, 0.07, grey, s, 0), ts = v(s * 0.04, 0.02, -0.08, grey, s, 0);
    const le = v(s * 0.32, 0.05, 0.05, grey, s, 0.5), te = v(s * 0.32, 0.05, -0.09, grey, s, 0.5);
    const tip = v(s * 0.66, 0.0, -0.06, black, s, 1), tt = v(s * 0.55, 0.01, -0.1, black, s, 0.85);
    if (s > 0) idx.push(ls, le, ts, ts, le, te, le, tip, te, te, tip, tt);
    else idx.push(ls, ts, le, ts, te, le, le, te, tip, te, tt, tip);
  }
  const g = new THREE.InstancedBufferGeometry();
  g.setIndex(idx);
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
  g.setAttribute('color', new THREE.Float32BufferAttribute(col, 3));
  g.setAttribute('gSide', new THREE.Float32BufferAttribute(side, 1));
  g.setAttribute('gSpan', new THREE.Float32BufferAttribute(span, 1));
  g.computeVertexNormals();
  return g;
}

// flocks: [x, z, spread, count] over the Hudson, the East River and the harbour
const FLOCKS = [[-920, -1400, 260, 10], [-930, -200, 240, 12], [-960, 900, 260, 10], [960, -900, 220, 8], [940, 700, 240, 10],
  [700, 2500, 300, 12], [-500, 3700, 420, 14], [300, 4300, 500, 12]];

export function createGulls({ scene, seed = 7, scale = 1 }) {
  let s = seed >>> 0;
  const rand = () => ((s = Math.imul(s ^ (s >>> 15), 2246822519) + 0x6D2B79F5 >>> 0) / 4294967296);
  const geo = gullGeometry();
  const count = FLOCKS.reduce((a, f) => a + Math.round(f[3] * scale), 0);
  const a = new Float32Array(count * 4), b = new Float32Array(count * 4);
  let i = 0;
  for (const [cx, cz, spread, n] of FLOCKS) for (let k = 0; k < Math.round(n * scale); k++, i++) {
    a.set([cx + (rand() - 0.5) * spread, cz + (rand() - 0.5) * spread * 0.8, 14 + rand() * 40, 8 + rand() * 30], i * 4); // centre x, z, radius, height
    b.set([rand() * Math.PI * 2, 8 + rand() * 4, rand() * 100, rand() < 0.5 ? -1 : 1], i * 4);                     // phase, speed, flap seed, dir
  }
  geo.setAttribute('gA', new THREE.InstancedBufferAttribute(a, 4));
  geo.setAttribute('gB', new THREE.InstancedBufferAttribute(b, 4));
  geo.instanceCount = count;
  geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e7);
  const uT = { value: 0 };
  const mat = new THREE.MeshStandardMaterial({ vertexColors: true, roughness: 0.75, metalness: 0, side: THREE.DoubleSide });
  mat.defines = { NO_WET: '', NO_SSR: '' };
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uGullT = uT;
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>
      attribute vec4 gA; attribute vec4 gB; attribute float gSide; attribute float gSpan; uniform float uGullT;
      vec3 gFwd; vec3 gRight; float gBank;`)
      .replace('#include <beginnormal_vertex>', `
        float t = uGullT;
        float R = gA.z, dir = gB.w;
        float th = gB.x + t * gB.y / R * dir;
        gFwd = vec3(-sin(th) * dir, 0.0, cos(th) * dir);
        gRight = vec3(gFwd.z, 0.0, -gFwd.x);
        gBank = dir * -0.45;
        vec3 objectNormal = vec3(normal);
        { float cb = cos(gBank), sb = sin(gBank); vec3 n = vec3(objectNormal.x * cb - objectNormal.y * sb, objectNormal.x * sb + objectNormal.y * cb, objectNormal.z);
          objectNormal = gRight * n.x + vec3(0.0, n.y, 0.0) + gFwd * n.z; }`)
      .replace('#include <begin_vertex>', `
        vec3 stP = vec3(gA.x + cos(th) * R, gA.w + sin(th * 2.0 + gB.z) * 3.0, gA.y + sin(th) * R);
        // flapping bursts: a slow gate turns wing beats (3 Hz) on and off; gliding otherwise
        float gate = smoothstep(0.55, 0.8, sin(t * 0.23 + gB.z) * 0.5 + 0.5);
        float beat = sin(t * ${(3.1 * 2 * Math.PI).toFixed(6)} + gB.z * 7.0);
        float lift = gate * beat * 0.55 + 0.08;
        vec3 p = position;
        float ang = lift * (gSpan * 0.6 + 0.4) + gSpan * gSpan * ((1.0 - gate) * -0.18);
        float ax = abs(p.x);
        if (gSide != 0.0) p = vec3(p.x * cos(ang), p.y + ax * sin(ang), p.z);
        float cb = cos(gBank), sb = sin(gBank);
        vec3 rolled = vec3(p.x * cb - p.y * sb, p.x * sb + p.y * cb, p.z);
        vec3 transformed = stP + gRight * rolled.x + vec3(0.0, rolled.y, 0.0) + gFwd * rolled.z;`);
    // scene alpha < 0.5 flags a fast-moving object for the TAA (render/pipeline.js): trust the current frame there
    sh.fragmentShader = sh.fragmentShader.replace('#include <opaque_fragment>', '#include <opaque_fragment>\n gl_FragColor.a = 0.25;');
  };
  mat.customProgramCacheKey = () => 'gulls-v1';
  const mesh = new THREE.Mesh(geo, mat);
  mesh.name = 'gulls'; mesh.frustumCulled = false; mesh.castShadow = false;
  scene.add(mesh);
  return { mesh, count, update(dt) { uT.value += dt; } };
}
