// OWNER: 3d-assets. Textured Tripo animals (tools/critterfit -> /assets/city/npc/fauna.*): shared rigid-part vertex
// animation, the dog walkers' dogs (npc/crowd.js), and the street critters: rats by the trash piles, squirrels in the
// parks, alley cats on the sidewalks. Pigeons / gulls use the same pack from npc/pigeons.js.
//
// Rig: every vertex carries aRig = (part, weight) (critterfit.py PART: 0 body, 1 head, 2 tail, 3-6 legs FL FR BL BR,
// 7-8 wings L R) and every instance iA = (gait phase, gait amount 0..1, clock, head pitch). Legs swing in diagonal pairs
// about their hip / shoulder pivots, the paws lift, the body bobs, the tail wags, the head looks around or nods.
import * as THREE from 'three';
import { G, mulberry32, inPark } from '../layout.js';

const v3 = (a) => `vec3(${a.map((x) => x.toFixed(4)).join(',')})`;

export function quadGLSL(piv, { leg = 0.5, lift = 0.03, bob = 0.012, wag = 9.0, tail = 0.45, look = 0.3 } = {}) {
  return `
  attribute vec2 aRig; attribute vec4 iA;
  vec3 rigPose(vec3 p) {
    int part = int(aRig.x + 0.5); float w = aRig.y, ph = iA.x, amp = iA.y;
    bool isLeg = part >= 3 && part <= 6;
    if (isLeg) {
      vec3 pv = part == 3 ? ${v3(piv.legFL)} : part == 4 ? ${v3(piv.legFR)} : part == 5 ? ${v3(piv.legBL)} : ${v3(piv.legBR)};
      float o = (part == 3 || part == 6) ? 0.0 : 3.14159;
      float a = sin(ph + o) * ${leg.toFixed(3)} * amp * w;
      vec3 q = p - pv; float c = cos(a), s = sin(a);
      q = vec3(q.x, c * q.y - s * q.z, s * q.y + c * q.z);
      q.y += max(0.0, cos(ph + o)) * ${lift.toFixed(4)} * amp * w;
      p = pv + q;
    }
    p.y += sin(ph * 2.0) * ${bob.toFixed(4)} * amp * (isLeg ? 1.0 - w : 1.0);   // planted paws stay on the ground
    if (part == 2) {
      vec3 pv = ${v3(piv.tail)}; vec3 q = p - pv;
      float a = sin(iA.z * ${wag.toFixed(2)}) * ${tail.toFixed(3)} * w; float c = cos(a), s = sin(a);
      p = pv + vec3(c * q.x + s * q.z, q.y, -s * q.x + c * q.z);
    }
    if (part == 1) {
      vec3 pv = ${v3(piv.head)}; vec3 q = p - pv;
      float a = sin(iA.z * 0.7) * ${look.toFixed(3)} * (1.0 - amp) * w; float c = cos(a), s = sin(a);
      q = vec3(c * q.x + s * q.z, q.y, -s * q.x + c * q.z);
      float b = iA.w * w; c = cos(b); s = sin(b);
      p = pv + vec3(q.x, c * q.y - s * q.z, s * q.y + c * q.z);
    }
    return p;
  }`;
}

// material + shadow depth material running the same pose
export function rigMaterial(atlas, glsl, key, { roughness = 0.85, tint = false } = {}) {
  const mat = new THREE.MeshStandardMaterial({ map: atlas, roughness, metalness: 0 });
  mat.onBeforeCompile = (sh) => {
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>\n${glsl}\n${tint ? 'attribute vec3 iT; varying vec3 vT;' : ''}`)
      .replace('#include <begin_vertex>', `vec3 transformed = rigPose(position);${tint ? ' vT = iT;' : ''}`);
    if (tint) sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vT;')
      .replace('#include <map_fragment>', '#include <map_fragment>\n diffuseColor.rgb *= vT;');
  };
  mat.customProgramCacheKey = () => key;
  const depth = new THREE.MeshDepthMaterial({ depthPacking: THREE.RGBADepthPacking });
  depth.onBeforeCompile = (sh) => {
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>\n${glsl}`)
      .replace('#include <begin_vertex>', 'vec3 transformed = rigPose(position);');
  };
  depth.customProgramCacheKey = () => key + '-depth';
  return { mat, depth };
}

// one instanced draw of a rigged mesh: begin() / push(...) / end() every frame
export class RigPool {
  constructor(scene, geo, { mat, depth }, max, name, castShadow = true, tint = false) {
    const g = geo.clone();
    this.iA = new THREE.InstancedBufferAttribute(new Float32Array(max * 4), 4).setUsage(THREE.DynamicDrawUsage);
    g.setAttribute('iA', this.iA);
    if (tint) { this.iT = new THREE.InstancedBufferAttribute(new Float32Array(max * 3).fill(1), 3).setUsage(THREE.DynamicDrawUsage); g.setAttribute('iT', this.iT); }
    const m = new THREE.InstancedMesh(g, mat, max);
    m.customDepthMaterial = depth; m.name = name; m.count = 0; m.frustumCulled = false; m.castShadow = castShadow; m.receiveShadow = true;
    m.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
    scene.add(m);
    Object.assign(this, { m, max, n: 0 });
  }
  begin() { this.n = 0; }
  push(x, y, z, ry, s, a0, a1, a2, a3, tint = null) {
    if (this.n >= this.max) return -1;
    const k = this.n++, e = this.m.instanceMatrix.array, o = k * 16, c = Math.cos(ry) * s, sn = Math.sin(ry) * s;
    e[o] = c; e[o + 1] = 0; e[o + 2] = -sn; e[o + 3] = 0; e[o + 4] = 0; e[o + 5] = s; e[o + 6] = 0; e[o + 7] = 0;
    e[o + 8] = sn; e[o + 9] = 0; e[o + 10] = c; e[o + 11] = 0; e[o + 12] = x; e[o + 13] = y; e[o + 14] = z; e[o + 15] = 1;
    const A = this.iA.array; A[k * 4] = a0; A[k * 4 + 1] = a1; A[k * 4 + 2] = a2; A[k * 4 + 3] = a3;
    if (tint && this.iT) this.iT.array.set(tint, k * 3);
    return k;
  }
  end() {
    const m = this.m; m.count = this.n; m.visible = this.n > 0;
    if (!this.n) return;
    for (const [a, w] of [[m.instanceMatrix, 16], [this.iA, 4], [this.iT, 3]]) { if (!a) continue; a.clearUpdateRanges(); a.addUpdateRange(0, this.n * w); a.needsUpdate = true; }
  }
}

// ------------------------------------------------------------------ dogs (the crowd's dog walkers)
// Same interface as crowd.js createDogs (begin / push(agent, y, lod, time) / end): a golden retriever or a French
// bulldog per walker, on the owner's left, a leash from the owner's left hand to the collar.
const BREED = { golden: { stride: 0.62, leg: 0.5 }, bulldog: { stride: 0.34, leg: 0.6 } };
export function createDogsHQ(scene, fauna) {
  const B = Object.keys(BREED).map((k) => fauna.items[k]).filter(Boolean).map((it) => {
    const m = rigMaterial(fauna.atlas, quadGLSL(it.pivots, { leg: BREED[it.name].leg }), 'dog-hq-' + it.name);
    return { it, ...BREED[it.name], collar: [0, it.pivots.head[1] * 0.95, it.pivots.head[2] - 0.02], pools: it.lods.map((g, li) => new RigPool(scene, g, m, [40, 120][li], `dogs-${it.name}-L${li}`, li === 0)) };
  });
  if (!B.length) return null;
  const lg = new THREE.CylinderGeometry(0.006, 0.006, 1, 4, 1, true); lg.translate(0, 0.5, 0);
  const leash = new THREE.InstancedMesh(lg, new THREE.MeshStandardMaterial({ color: 0x151515, roughness: 0.6 }), 60);
  leash.name = 'dog-leash'; leash.count = 0; leash.frustumCulled = false; leash.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  scene.add(leash);
  let nl = 0;
  const M4 = new THREE.Matrix4(), Q = new THREE.Quaternion(), V0 = new THREE.Vector3(), V1 = new THREE.Vector3(), UP = new THREE.Vector3(0, 1, 0), SC = new THREE.Vector3();
  return {
    begin() { for (const b of B) for (const p of b.pools) p.begin(); nl = 0; },
    push(a, y, lod, time) {
      const d = a.dog;
      d.breed ??= Math.floor(d.ph * 1000) % B.length;
      const b = B[d.breed], P = b.pools[Math.min(lod, b.pools.length - 1)];
      const moving = a.clip.startsWith('walk') || a.clip === 'run' || a.clip === 'flee';
      const dt = d.t < 0 ? 0 : Math.min(0.25, time - d.t); d.t = time;
      const sp = moving ? a.speed : 0;
      const ds = 0.92 + (d.s - 0.72) * 0.35;               // breeds come in real sizes: a small spread only
      d.amp = (d.amp ?? 0) + ((moving ? 1 : 0) - (d.amp ?? 0)) * Math.min(1, dt * 4);
      d.ph += dt * (sp / (b.stride * ds)) * 6.2832;
      const c = Math.cos(a.ry), s = Math.sin(a.ry);
      const lx = 0.5, lz = 0.95 + 0.1 * Math.sin(time * 0.6 + d.col);
      const x = a.x + lx * c + lz * s, z = a.z - lx * s + lz * c;
      if (P.push(x, y, z, a.ry, ds, d.ph, d.amp, time + d.col * 1e-7, 0) < 0) return;
      if (nl < 60) { // hand (owner-local 0.25, 0.81, 0.12) -> collar
        const hx = 0.25 * a.scale, hz = 0.12 * a.scale, [cx, cy, cz] = b.collar;
        V0.set(a.x + hx * c + hz * s, y + 0.81 * a.scale, a.z - hx * s + hz * c);
        V1.set(x + cz * ds * s + cx * ds * c, y + cy * ds, z + cz * ds * c - cx * ds * s);
        V1.sub(V0); const len = V1.length(); V1.divideScalar(len || 1);
        Q.setFromUnitVectors(UP, V1); SC.set(1, len, 1); M4.compose(V0, Q, SC); M4.toArray(leash.instanceMatrix.array, nl * 16); nl++;
      }
    },
    end() {
      for (const b of B) for (const p of b.pools) p.end();
      leash.count = nl; leash.visible = nl > 0;
      if (nl) { leash.instanceMatrix.clearUpdateRanges(); leash.instanceMatrix.addUpdateRange(0, nl * 16); leash.instanceMatrix.needsUpdate = true; }
    },
  };
}

// ------------------------------------------------------------------ street critters
// Deterministic sites (like the pigeon flocks), simulated only near the camera:
//   rats      at curbside trash piles and dumpsters: scurry and sniff around the pile, bolt and vanish when approached
//   squirrels along the park paths: hop about, freeze, sprint off (up a tree) when approached
//   cats      on sidewalk frontages: stroll, sit, walk briskly away from Spider-Man (they never run from anyone else)
const R_SIM = 90, LOD_D = 22;
const SPEC = {
  rat:      { key: 'rat',      max: 90, stride: 0.1,  walk: 0.9, run: 4.2, fear: 7,  roam: 2.6, vanish: true,  leg: 0.8, lift: 0.015, bob: 0.006, tail: 0.35, wag: 5, look: 0.5, sniff: 0.25 },
  squirrel: { key: 'squirrel', max: 70, stride: 0.22, walk: 1.4, run: 5.5, fear: 8,  roam: 4.5, vanish: true,  leg: 0.9, lift: 0.04,  bob: 0.03,  tail: 0.25, wag: 3, look: 0.6, sniff: 0.3 },
  cat:      { key: 'cat',      max: 24, stride: 0.34, walk: 0.7, run: 2.6, fear: 5,  roam: 9,   vanish: false, leg: 0.5, lift: 0.02,  bob: 0.008, tail: 0.3,  wag: 1.3, look: 0.4, sniff: 0 },
};

export function createCritters({ scene, fauna, blocks, parkPaths, props }) {
  const S = {};
  for (const [name, sp] of Object.entries(SPEC)) {
    const it = fauna.items[sp.key]; if (!it) continue;
    const m = rigMaterial(fauna.atlas, quadGLSL(it.pivots, sp), 'critter-' + name);
    S[name] = { ...sp, it, pools: it.lods.map((g, li) => new RigPool(scene, g, m, li ? sp.max : Math.ceil(sp.max / 2), `${name}s-L${li}`, li === 0)) };
  }
  // ---- sites
  const rnd = mulberry32(0xc1a77e);
  const sites = [];
  const add = (kind, x, y, z, n, extra = {}) => { if (S[kind]) sites.push({ kind, x, y, z, n, a: null, seed: sites.length * 7919 + 11, ...extra }); };
  const piles = [...(props?.bags?.() || []), ...(props?.dumpsters?.() || [])];
  for (const p of piles) if (rnd() < 0.45) add('rat', p.x, p.y ?? G.CURB_H, p.z, 1 + Math.floor(rnd() * 3));
  for (const p of parkPaths || []) {
    if (p.drive) continue;
    for (let i = 7; i < p.pts.length; i += 16) if (rnd() < 0.5) {
      const [x, z] = p.pts[i], a = rnd() * 6.28, d = 3 + rnd() * 4;
      if (inPark(x + Math.cos(a) * d, z + Math.sin(a) * d)) add('squirrel', x + Math.cos(a) * d, G.CURB_H + 0.02, z + Math.sin(a) * d, 1 + Math.floor(rnd() * 2));
    }
  }
  for (const b of blocks) {
    if (rnd() > 0.1) continue;
    // a stretch of sidewalk along one frontage (same offsets as the pigeon flocks)
    const side = Math.floor(rnd() * 4), u = 0.2 + rnd() * 0.6;
    const alongX = side === 0 || side === 2;
    const x = alongX ? b.x0 + (b.x1 - b.x0) * u : side === 1 ? b.x1 - 2.8 : b.x0 + 2.8;
    const z = alongX ? (side === 0 ? b.z0 + 2.5 : b.z1 - 2.5) : b.z0 + (b.z1 - b.z0) * u;
    add('cat', x, G.CURB_H, z, 1, { ax: alongX ? 1 : 0, az: alongX ? 0 : 1 });
  }

  const player = { pos: new THREE.Vector3(1e9, 0, 0) };
  const alarms = [];
  let time = 0;
  const spawn = (st) => {
    const r = mulberry32(st.seed), sp = S[st.kind];
    st.a = [];
    for (let i = 0; i < st.n; i++) {
      const a = r() * 6.28, d = r() * sp.roam * 0.6;
      st.a.push({ x: st.x + (st.ax ?? Math.cos(a)) * d, z: st.z + (st.az ?? Math.sin(a)) * d, ry: r() * 6.28, tx: null, tz: 0, wait: r() * 2, mode: 'idle',
        ph: r() * 6.28, amp: 0, clock: r() * 100, s: 0.9 + r() * 0.2, gone: 0, sniff: 0 });
    }
  };
  const wander = (st, c, sp, r) => {
    if (st.ax != null) { const d = (r() - 0.5) * 2 * sp.roam; c.tx = st.x + st.ax * d; c.tz = st.z + st.az * d; }
    else { const a = r() * 6.28, d = Math.sqrt(r()) * sp.roam; c.tx = st.x + Math.cos(a) * d; c.tz = st.z + Math.sin(a) * d; }
  };
  return {
    sites,
    setPlayer(st) { player.pos.copy(st.pos); },
    alarm(pos, r = 25) { alarms.push({ x: pos.x, z: pos.z, r, t: time }); },
    update(dt, camera) {
      time += dt;
      while (alarms.length && time - alarms[0].t > 0.5) alarms.shift();
      const cp = camera.position;
      for (const k in S) for (const p of S[k].pools) p.begin();
      for (const st of sites) {
        const dc = Math.hypot(st.x - cp.x, st.z - cp.z);
        if (dc > R_SIM) { st.a = null; continue; }
        if (!st.a) spawn(st);
        const sp = S[st.kind];
        for (const c of st.a) {
          const pd = Math.hypot(player.pos.x - c.x, player.pos.z - c.z), ph = player.pos.y - st.y;
          const scared = (pd < sp.fear && ph < 4) || alarms.some((al) => Math.hypot(al.x - c.x, al.z - c.z) < al.r);
          if (c.mode === 'gone') { // hiding (in the pile / up a tree) until Spider-Man has left
            if (pd > 25 && (c.gone -= dt) < 0) { c.mode = 'idle'; c.x = st.x; c.z = st.z; c.wait = 1 + Math.random() * 3; }
            continue;
          }
          if (scared && c.mode !== 'flee') {
            c.mode = 'flee'; c.t = 0;
            let fx = c.x - player.pos.x, fz = c.z - player.pos.z;
            if (st.ax != null) { const u = fx * st.ax + fz * st.az; fx = st.ax * Math.sign(u || 1); fz = st.az * Math.sign(u || 1); }
            const l = Math.hypot(fx, fz) || 1; c.fx = fx / l; c.fz = fz / l;
          }
          let speed = 0;
          if (c.mode === 'flee') {
            c.t += dt; speed = sp.run;
            c.x += c.fx * speed * dt; c.z += c.fz * speed * dt; c.ry = Math.atan2(c.fx, c.fz);
            if (sp.vanish && c.t > 1.4) { c.mode = 'gone'; c.gone = 4 + Math.random() * 6; continue; }
            if (!sp.vanish && (c.t > 2.5 || Math.hypot(c.x - st.x, c.z - st.z) > sp.roam * 1.6)) { c.mode = 'idle'; c.wait = 2 + Math.random() * 3; }
          } else if (c.mode === 'idle') {
            c.wait -= dt;
            c.sniff = sp.sniff * Math.max(0, Math.sin(time * 5 + c.clock));
            if (c.wait <= 0) { wander(st, c, sp, Math.random); c.mode = 'move'; }
          } else { // move to the wander target
            const dx = c.tx - c.x, dz = c.tz - c.z, l = Math.hypot(dx, dz);
            speed = sp.walk * (st.kind === 'rat' ? 1 + 0.8 * Math.max(0, Math.sin(time * 3 + c.clock)) : 1);   // rats go in bursts
            if (l < 0.08) { c.mode = 'idle'; c.wait = st.kind === 'cat' ? 3 + Math.random() * 8 : 0.5 + Math.random() * 2.5; speed = 0; }
            else {
              const s = Math.min(l, speed * dt); c.x += dx / l * s; c.z += dz / l * s;
              const want = Math.atan2(dx, dz); c.ry += Math.atan2(Math.sin(want - c.ry), Math.cos(want - c.ry)) * Math.min(1, dt * 8);
            }
            c.sniff = 0;
          }
          c.amp += ((speed > 0 ? 1 : 0) - c.amp) * Math.min(1, dt * 8);
          c.ph += dt * (speed / (sp.stride * c.s)) * 6.2832;
          c.clock += dt;
          const pool = sp.pools[dc < LOD_D || sp.pools.length < 2 ? 0 : 1];
          pool.push(c.x, st.y, c.z, c.ry, c.s, c.ph, c.amp, c.clock, c.sniff);
        }
      }
      for (const k in S) for (const p of S[k].pools) p.end();
    },
    stats() { let n = 0; for (const st of sites) if (st.a) n += st.a.length; return { critters: n, critterSites: sites.length }; },
  };
}
