// OWNER: destruction (pinata-and-trees). Live debris: every fragment of every break (crate splinters, hydrant chunks,
// glass shards, car panels) is written into ONE dynamic, world-space vertex buffer and drawn in one call (+ one per
// shadow cascade) -- no per-fragment meshes / draw calls, no allocations per frame. Fragments get simple rigid-body
// motion (gravity, drag, tumbling, bounce + friction on world.groundHeight, deflection off walls via world.raycast),
// fall asleep when they come to rest (sleeping pieces are not rewritten), fade out by shrinking and are recycled.
// Hard cap on live fragments (quality `debris`, default 300): the oldest go first.
//   const D = createDebris(ctx, { max });  D.spawn(pieces, opts) -> n;  D.update(dt);  D.clear();  D.count
//   pieces: fracture.js output ({ pos, nrm, idx, n0, c }), model space;  opts: see spawn()
import * as THREE from 'three';
import { createPartMaterial, PART } from '../../world/partmat.js';

const MAXV = 1 << 18, MAXI = MAXV * 3;
const G = 21;
const _m = new THREE.Matrix4(), _p = new THREE.Vector3(), _q = new THREE.Quaternion(), _s = new THREE.Vector3(), _dq = new THREE.Quaternion();
const _v = new THREE.Vector3(), _v2 = new THREE.Vector3(), _n = new THREE.Vector3(), _ax = new THREE.Vector3();
const rnd = (a, b) => a + Math.random() * (b - a);
const jit = (c, k) => { const v = 1 + (Math.random() * 2 - 1) * k; return [c[0] * v, c[1] * v, c[2] * v]; }; // per-piece value variation

export function createDebris(ctx, { max = 300 } = {}) {
  const geo = new THREE.BufferGeometry();
  const A = (name, n, T = Float32Array) => { const a = new THREE.BufferAttribute(new T(MAXV * n), n); a.setUsage(THREE.DynamicDrawUsage); geo.setAttribute(name, a); return a; };
  const aPos = A('position', 3), aNrm = A('normal', 3), aCol = A('color', 3), aPart = A('aPart', 1);
  const aIdx = new THREE.BufferAttribute(new Uint32Array(MAXI), 1); aIdx.setUsage(THREE.DynamicDrawUsage); geo.setIndex(aIdx);
  geo.setDrawRange(0, 0);
  geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e7);
  const mat = createPartMaterial({ name: 'debris', instTint: false });
  mat.side = THREE.DoubleSide; // thin shards / paper: both faces
  const mesh = new THREE.Mesh(geo, mat);
  mesh.name = 'debris'; mesh.frustumCulled = false; mesh.castShadow = true; mesh.receiveShadow = true; mesh.visible = false;
  ctx.scene.add(mesh);

  const live = [];
  let vTop = 0, iTop = 0, deadV = 0;
  let vMin = Infinity, vMax = -1, colDirty = false, idxDirty = false;

  function place(f) {
    f.vOff = vTop; f.iOff = iTop; vTop += f.nv; iTop += f.ni;
    const C = aCol.array, Pt = aPart.array, I = aIdx.array, o = f.vOff;
    // colours: outer faces / cut faces (the index ranges tell them apart: flag the vertices by the triangles using them)
    for (let k = 0; k < f.nv; k++) { C[(o + k) * 3] = f.colIn[0]; C[(o + k) * 3 + 1] = f.colIn[1]; C[(o + k) * 3 + 2] = f.colIn[2]; Pt[o + k] = f.partIn; }
    for (let k = 0; k < f.n0; k++) { const v = o + f.li[k]; C[v * 3] = f.col[0]; C[v * 3 + 1] = f.col[1]; C[v * 3 + 2] = f.col[2]; Pt[v] = f.part; }
    for (let k = 0; k < f.ni; k++) I[f.iOff + k] = o + f.li[k];
    f.dirty = true; colDirty = true; idxDirty = true;
  }
  function compact() {
    vTop = 0; iTop = 0; deadV = 0;
    for (const f of live) place(f);
    vMin = 0; vMax = vTop - 1;
  }
  function kill(i) {
    const f = live[i];
    aIdx.array.fill(f.vOff, f.iOff, f.iOff + f.ni); // degenerate until the next compaction
    deadV += f.nv; idxDirty = true;
    live.splice(i, 1);
  }

  const world = () => ctx.world;
  const D = {
    mesh,
    get count() { return live.length; },
    get max() { return max; }, set max(v) { max = v; },
    // opts: matrix (model -> world), color | colorOf(piece) -> [r,g,b] (linear), part, colorIn, partIn,
    //       origin (world impact point), power (m/s outward), dir (world push, m/s), up (m/s), spin (rad/s), life (s),
    //       drag (1/s; paper ~3, glass ~0.4), bounce (0..1), sfx(speed) on hard ground contacts
    spawn(pieces, o = {}) {
      if (!pieces?.length || max <= 0) return 0;
      const M = o.matrix ?? _m.identity();
      M.decompose(_p, _q, _s);
      const baseQ = _q.clone(), baseS = _s.clone();
      let n = 0;
      for (const pc of pieces) {
        const nv = pc.pos.length / 3, ni = pc.idx.length;
        if (nv + vTop > MAXV || ni + iTop > MAXI) { if (deadV > 0) compact(); if (nv + vTop > MAXV || ni + iTop > MAXI) break; }
        while (live.length >= max) { let k = live.findIndex(f => f.sleep); if (k < 0) k = 0; kill(k); }
        const c = _v.set(pc.c[0], pc.c[1], pc.c[2]).applyMatrix4(M);
        let r2 = 0; for (let k = 0; k < nv; k++) r2 = Math.max(r2, pc.pos[k * 3] ** 2 + pc.pos[k * 3 + 1] ** 2 + pc.pos[k * 3 + 2] ** 2);
        const r = Math.sqrt(r2) * Math.max(baseS.x, baseS.y, baseS.z);
        const f = {
          lp: pc.pos, ln: pc.nrm, li: pc.idx, n0: pc.n0 ?? ni, nv, ni,
          col: jit(o.colorOf ? o.colorOf(pc) : (pc.color ?? o.color ?? [0.5, 0.5, 0.5]), o.jitter ?? 0.08), part: pc.part ?? o.part ?? PART.BASE,
          colIn: pc.colorIn ?? o.colorIn ?? pc.color ?? o.color ?? [0.4, 0.4, 0.4], partIn: pc.partIn ?? o.partIn ?? pc.part ?? o.part ?? PART.BASE,
          p: c.clone(), q: baseQ.clone(), sc: baseS.clone(), v: new THREE.Vector3(), w: new THREE.Vector3(),
          r, low: r, age: 0, life: (o.life ?? 7) * rnd(0.8, 1.2), sleep: false, rest: 0, shrink: 1, dirty: true,
          drag: pc.drag ?? o.drag ?? 0.12, bounce: o.bounce ?? 0.3, sfx: o.sfx ?? null, sfxT: 0,
        };
        // launch: away from the impact point + a directed push + upward kick, heavier (bigger) pieces slower
        const heavy = Math.min(1, 0.25 / Math.max(0.05, r));
        const pw = (o.power ?? 4) * (0.45 + 0.55 * heavy) * rnd(0.6, 1.25);
        if (o.origin) { _v2.subVectors(f.p, o.origin); _v2.y = Math.max(_v2.y, 0.1); if (_v2.lengthSq() < 1e-6) _v2.set(rnd(-1, 1), 1, rnd(-1, 1)); f.v.addScaledVector(_v2.normalize(), pw); }
        else f.v.set(rnd(-1, 1), rnd(0.2, 1), rnd(-1, 1)).normalize().multiplyScalar(pw);
        if (o.dir) f.v.addScaledVector(o.dir, rnd(0.5, 1.1) * (0.5 + 0.5 * heavy));
        f.v.y += (o.up ?? 2) * rnd(0.5, 1.2);
        const sp = (o.spin ?? 8) * (0.4 + heavy);
        f.w.set(rnd(-sp, sp), rnd(-sp, sp), rnd(-sp, sp));
        if (pc.vel) f.v.add(pc.vel);
        live.push(f); place(f); n++;
      }
      mesh.visible = live.length > 0;
      return n;
    },
    update(dt) {
      if (!live.length) { if (mesh.visible) { mesh.visible = false; } return; }
      dt = Math.min(dt, 1 / 20);
      const W = world();
      for (let i = live.length - 1; i >= 0; i--) {
        const f = live[i];
        f.age += dt;
        if (f.age > f.life) { f.shrink = Math.max(0, f.shrink - dt / 0.5); f.dirty = true; if (f.shrink <= 0) { kill(i); continue; } }
        if (f.sleep) continue;
        const v = f.v;
        v.y -= G * dt;
        if (f.drag) { const k = Math.exp(-f.drag * dt); v.x *= k; v.z *= k; if (v.y > 0 || f.drag > 1) v.y *= k; if (f.drag > 1) v.y = Math.max(v.y, -3.2); } // paper flutters down
        const sp = v.length(), step = sp * dt;
        if (W?.raycast && step > 0.04 && (f.age < 3 || sp > 3)) {
          _v2.copy(v).divideScalar(sp);
          const hit = W.raycast(f.p, _v2, step + f.r * 0.5);
          if (hit && hit.normal && Math.abs(hit.normal.y) < 0.7) {
            _n.copy(hit.normal); const vn = v.dot(_n);
            if (vn < 0) { v.addScaledVector(_n, -(1 + f.bounce) * vn).multiplyScalar(0.6); f.w.multiplyScalar(0.7); }
            f.p.copy(hit.point).addScaledVector(_n, f.r * 0.5 + 0.01);
          }
        }
        f.p.addScaledVector(v, dt);
        const wl = f.w.length();
        if (wl > 1e-4) { _dq.setFromAxisAngle(_ax.copy(f.w).divideScalar(wl), wl * dt); f.q.premultiply(_dq).normalize(); }
        const gy = W?.groundHeight ? W.groundHeight(f.p.x, f.p.z, f.p.y - f.low + 0.25) : 0; // floors at / just under the piece's lowest point (never a roof above it)
        if (f.p.y - f.low <= gy) {
          f.p.y = gy + f.low;
          if (v.y < -2.2) {
            if (f.sfx && f.sfxT <= 0 && -v.y > 4) { f.sfx(-v.y, f); f.sfxT = 0.25; }
            v.y = -v.y * f.bounce; v.x *= 0.62; v.z *= 0.62;
            f.w.multiplyScalar(0.55).add(_v2.set(rnd(-2, 2), rnd(-2, 2), rnd(-2, 2)));
          } else {
            v.y = Math.max(0, v.y);
            const k = Math.exp(-7 * dt); v.x *= k; v.z *= k; f.w.multiplyScalar(Math.exp(-5 * dt));
            if (v.x * v.x + v.z * v.z < 0.05 && f.w.lengthSq() < 0.3) { f.rest += dt; if (f.rest > 0.25) { f.sleep = true; v.set(0, 0, 0); f.w.set(0, 0, 0); } }
          }
        } else f.rest = 0;
        f.sfxT -= dt;
        f.dirty = true;
      }
      // write the moved fragments (world space) into the shared buffer
      const P = aPos.array, N = aNrm.array;
      for (const f of live) {
        if (!f.dirty) continue;
        f.dirty = false;
        _s.copy(f.sc).multiplyScalar(f.shrink);
        _m.compose(f.p, f.q, _s);
        const e = _m.elements, o = f.vOff, lp = f.lp, ln = f.ln;
        let minY = Infinity;
        // rotation part for normals (uniform-ish scale: renormalise)
        for (let k = 0; k < f.nv; k++) {
          const x = lp[k * 3], y = lp[k * 3 + 1], z = lp[k * 3 + 2], j = (o + k) * 3;
          P[j] = e[0] * x + e[4] * y + e[8] * z + e[12];
          const wy = e[1] * x + e[5] * y + e[9] * z + e[13]; P[j + 1] = wy; if (wy < minY) minY = wy;
          P[j + 2] = e[2] * x + e[6] * y + e[10] * z + e[14];
          const nx = ln[k * 3], ny = ln[k * 3 + 1], nz = ln[k * 3 + 2];
          const a = e[0] * nx + e[4] * ny + e[8] * nz, b = e[1] * nx + e[5] * ny + e[9] * nz, c = e[2] * nx + e[6] * ny + e[10] * nz;
          const L = Math.hypot(a, b, c) || 1; N[j] = a / L; N[j + 1] = b / L; N[j + 2] = c / L;
        }
        f.low = Math.max(0.005, f.p.y - minY);
        if (o < vMin) vMin = o; if (o + f.nv - 1 > vMax) vMax = o + f.nv - 1;
      }
      if (deadV > vTop * 0.35 && deadV > 2000) compact();
      if (vMax >= vMin) {
        for (const a of [aPos, aNrm]) { a.clearUpdateRanges(); a.addUpdateRange(vMin * 3, (vMax - vMin + 1) * 3); a.needsUpdate = true; }
        vMin = Infinity; vMax = -1;
      }
      if (colDirty) { for (const [a, w] of [[aCol, 3], [aPart, 1]]) { a.clearUpdateRanges(); a.addUpdateRange(0, vTop * w); a.needsUpdate = true; } colDirty = false; }
      if (idxDirty) { aIdx.clearUpdateRanges(); aIdx.addUpdateRange(0, iTop); aIdx.needsUpdate = true; idxDirty = false; }
      geo.setDrawRange(0, iTop);
      if (!live.length) { vTop = iTop = deadV = 0; geo.setDrawRange(0, 0); }
      mesh.visible = live.length > 0;
    },
    // wake sleeping pieces near p (a new blast / a landing next to them) and push them away
    blast(p, radius, power) {
      for (const f of live) {
        const d = f.p.distanceTo(p); if (d > radius) continue;
        const k = 1 - d / radius;
        f.sleep = false; f.rest = 0;
        _v.subVectors(f.p, p).setY(0.6).normalize();
        f.v.addScaledVector(_v, power * k * rnd(0.6, 1.1));
        f.w.add(_v2.set(rnd(-6, 6), rnd(-6, 6), rnd(-6, 6)).multiplyScalar(k));
      }
    },
    clear() { while (live.length) kill(live.length - 1); vTop = iTop = deadV = 0; geo.setDrawRange(0, 0); mesh.visible = false; },
  };
  return D;
}
