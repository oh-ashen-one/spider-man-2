// OWNER: destruction (pinata-and-trees). What can break, and what happens when it does.
//  - street props (world/props.js instanced pools): hydrant, trash can, bench, mailbox, newsbox rack, bus-stop sign,
//    planter, cone, hot-dog cart: the instance is hidden, its collision solids switched off, the prop is split into its
//    parts and the solid parts Voronoi-fractured (pieces.js / fracture.js, pre-fractured at idle time), the pieces fly
//    (debris.js). A hydrant leaves a water jet. Everything respawns once the player is far away and not looking.
//  - glass: bus-shelter panes and newsstand windows shatter (2.5D Voronoi); the shelter / stand stays (swapped to a
//    glass-less copy of the model in a companion pool)
//  - cars: a heavy hit bursts a side window, tears a door / hood panel off, and the car stops on hazards
//  - combat throwables: crates splinter (stretched 3D Voronoi), litter bins burst open (hollow-shell shards + trash)
//   const B = createBreakables(ctx, debris);  B.breakAt(p, r, o);  B.sweep(p, r, vel);  B.hitCar(p, r, o);  B.update(dt)
import * as THREE from 'three';
import { PART } from '../../world/partmat.js';
import { Pool } from '../../world/pool.js';
import { planPieces, piecesNow, buildPieces } from './pieces.js';
import { MB } from '../../world/geom.js';
import { fracture, cached, prefetch } from './fracture.js';

const _m = new THREE.Matrix4(), _q = new THREE.Quaternion(), _e = new THREE.Euler(), _p = new THREE.Vector3(), _s = new THREE.Vector3();
const _v = new THREE.Vector3(), _v2 = new THREE.Vector3();
const rnd = (a, b) => a + Math.random() * (b - a);
const lin = (h) => [((h >> 16) & 255) / 255, ((h >> 8) & 255) / 255, (h & 255) / 255].map(c => Math.pow(c, 2.2));

// kind: radius (m, for hit tests), height, sound, whole (destroyed) or glass-only (pane swap), fx extras
export const BREAKABLE = {
  hydrant: { r: 0.3, h: 0.8, snd: 'metal', jet: true, power: 3 },
  trash: { r: 0.36, h: 0.95, snd: 'metal', spill: true },
  bench: { r: 1.05, h: 0.9, snd: 'wood' },
  mailbox: { r: 0.4, h: 1.2, snd: 'metal' },
  newsbox: { r: 0.9, h: 1.1, snd: 'metal', paper: true },
  busstop: { r: 0.25, h: 2.8, snd: 'metal' },
  planter: { r: 0.75, h: 0.8, snd: 'wood' },
  cone: { r: 0.25, h: 0.75, snd: 'wood' },
  cart: { r: 1.1, h: 2.2, snd: 'metal' },
  shelter: { r: 2.3, h: 2.6, glass: true },
  news: { r: 1.5, h: 2.5, glass: true, paper: true },
};

// combat crate: six plank panels (hollow, like the real thing) -> each splits into long board splinters
function crateGeo() {
  const b = new MB(), W = 0.35, H = 0.6, t = 0.03, e = 0.003; // e: panels never share a vertex (separate pieces)
  b.setPart(PART.WOOD).setColor(0x9a7248);
  b.box(-W, 0, -W, W, t, W); b.box(-W, H - t, -W, W, H, W);                                              // bottom / lid
  b.setColor(0x8d6740).box(-W, t + e, -W, W, H - t - e, -W + t); b.box(-W, t + e, W - t, W, H - t - e, W); // front / back
  b.setColor(0xa47b4f).box(-W, t + e, -W + t + e, -W + t, H - t - e, W - t - e); b.box(W - t, t + e, -W + t + e, W, H - t - e, W - t - e); // sides
  return b.build({ part: true });
}
function binShellSrc() {
  // closed hollow tub (outer 0.29 -> 0.25 m, 12 mm wall, bottom 16 mm): watertight lathe -> curved metal shards
  const t = 0.012, h = 0.86, pts = [[0.001, 0.02], [0.25, 0.02], [0.29, h], [0.29 - t, h], [0.25 - t, 0.02 + 0.016], [0.001, 0.036]].map(([r, y]) => new THREE.Vector2(r, y + 0.02));
  pts.push(pts[0].clone());
  const g = new THREE.LatheGeometry(pts, 18);
  g.deleteAttribute('uv');
  return { pos: g.attributes.position.array, nrm: g.attributes.normal.array, idx: Uint32Array.from(g.index.array) };
}

export function createBreakables(ctx, debris) {
  const world = ctx.world;
  const plans = new Map();        // kind -> plan (pieces.js)
  const variants = new Map();     // glass kind -> companion Pool without the glass
  const broken = [];              // { kind, pool, it, solids, t, variantIt }
  let T = 0;
  const cratePlan = planPieces('crate', crateGeo(), { minPieces: 5, maxPieces: 7, splinter: true });

  const pool = (k) => world.propPool?.(k) ?? null;
  const fx = () => ctx.combat?.fx ?? null;
  const sfx = (k, ...a) => { try { ctx.sys?.audio?.sfx?.[k]?.(...a); } catch (e) { /* audio optional */ } };

  function planFor(kind) {
    if (plans.has(kind)) return plans.get(kind);
    const P = pool(kind); if (!P) { plans.set(kind, null); return null; }
    let geo = P.geo;
    if (BREAKABLE[kind].glass) geo = filterGeo(P.geo, (part) => part === PART.GLASS);
    const plan = planPieces('prop:' + kind, geo, { maxPieces: kind === 'bench' ? 3 : 6, drop: kind === 'news' ? 0.05 : 0.03 });
    plans.set(kind, plan);
    return plan;
  }
  // geometry restricted to (or without) one part id: glass panes / the glass-less shelter
  function filterGeo(src, keep) {
    const Pa = src.attributes.aPart, I = src.index.array, idx = [];
    for (let t = 0; t < I.length; t += 3) if (keep(Pa ? Math.round(Pa.getX(I[t])) : 0)) idx.push(I[t], I[t + 1], I[t + 2]);
    const g = new THREE.BufferGeometry();
    for (const k of ['position', 'normal', 'color', 'uv', 'aPart']) if (src.attributes[k]) g.setAttribute(k, src.attributes[k].clone());
    g.setIndex(idx); g.computeBoundingSphere(); g.computeBoundingBox();
    return g;
  }
  function variantPool(kind) {
    if (variants.has(kind)) return variants.get(kind);
    const P = pool(kind); if (!P) return null;
    const vp = new Pool(filterGeo(P.geo, (part) => part !== PART.GLASS), P.mat, { name: kind + '-broken', max: 64, far: P.far, castShadow: P.mesh.castShadow, extra: { aTint: 3, aState: 1 } });
    P.mesh.parent.add(vp.mesh);
    variants.set(kind, vp);
    return vp;
  }

  // spatial hash of the breakable instances (static street furniture; built on first use)
  let hash = null; const HC = 8;
  function buildHash() {
    hash = new Map();
    for (const kind of Object.keys(BREAKABLE)) {
      const P = pool(kind); if (!P) continue;
      for (const it of P.items) {
        if (it.y > 1.5) continue; // street level only (rooftop copies stay)
        const k = Math.floor(it.x / HC) * 100003 + Math.floor(it.z / HC);
        let a = hash.get(k); if (!a) hash.set(k, (a = [])); a.push({ kind, it, P });
      }
    }
  }
  function near(p, r, fn) {
    if (!hash) buildHash();
    for (let i = Math.floor((p.x - r - 2.5) / HC); i <= Math.floor((p.x + r + 2.5) / HC); i++)
      for (let j = Math.floor((p.z - r - 2.5) / HC); j <= Math.floor((p.z + r + 2.5) / HC); j++) {
        const a = hash.get(i * 100003 + j); if (!a) continue;
        for (const e of a) {
          if (e.it.hidden || e.it.broken) continue;
          const K = BREAKABLE[e.kind], d = Math.hypot(e.it.x - p.x, e.it.z - p.z);
          if (d > r + K.r) continue;
          if (p.y < e.it.y - 0.8 || p.y > e.it.y + K.h + 1.2) continue;
          fn(e, d);
        }
      }
  }
  const matrixOf = (it, out = _m) => {
    if (it.rx || it.rz) { _e.set(it.rx || 0, it.ry, it.rz || 0, 'YXZ'); _q.setFromEuler(_e); } else _q.setFromAxisAngle(THREE.Object3D.DEFAULT_UP, it.ry);
    if (it.scale3) _s.set(it.scale3[0] * it.s, it.scale3[1] * it.s, it.scale3[2] * it.s); else _s.setScalar(it.s ?? 1);
    return out.compose(_p.set(it.x, it.y, it.z), _q, _s);
  };
  // collision primitives belonging to a prop instance (solids whose footprint centre lies within its radius, base at
  // the prop's base): switched off while it is broken
  function solidsOf(it, K) {
    const g = world.collision; if (!g) return [];
    const out = [], r = K.r + 0.25;
    g.query(it.x - r, it.z - r, it.x + r, it.z + r, (i) => {
      const j = i * 6, b = g.bb;
      const cx = (b[j] + b[j + 3]) / 2, cz = (b[j + 2] + b[j + 5]) / 2;
      if (Math.hypot(cx - it.x, cz - it.z) > r || b[j + 1] < it.y - 0.3 || b[j + 1] > it.y + 0.6 || b[j + 4] > it.y + K.h + 0.6) return;
      if (b[j + 3] - b[j] > 2 * r + 0.6 || b[j + 5] - b[j + 2] > 2 * r + 0.6) return; // a sidewalk slab / wall, not the prop
      out.push(i);
    });
    for (const i of out) g.disable(i);
    return out;
  }

  function spawnKind(kind, plan, it, o) {
    const tint = it.extra?.aTint;
    const M = matrixOf(it).clone();
    const colorOf = (pc) => (pc.paint && tint ? pc.color.map((c, k) => c * tint[k]) : pc.color);
    const glass = BREAKABLE[kind].glass;
    // glass mostly drops out of the frame (a little outward push); solids get the full blast
    const opts = { matrix: M, colorOf, origin: o.origin, power: glass ? Math.min(1.6, (o.power ?? 4) * 0.4) : o.power ?? 4, dir: glass && o.dir ? o.dir.clone().multiplyScalar(0.6) : o.dir,
      up: glass ? 0.5 : o.up ?? 2.5, spin: glass ? 11 : 9, life: glass ? 6 : 8, bounce: glass ? 0.18 : 0.28,
      sfx: (sp, f) => { if (f.r > 0.2 && Math.random() < 0.3) sfx('crunch', Math.min(0.6, sp / 20), 0, BREAKABLE[kind].snd); } };
    const now = piecesNow(plan);
    debris.spawn(now, opts);
    // fractures still in flight (first break before the idle pre-fracture got to this kind): add them when ready
    if (!plan.jobs.every(j => cached(j.key))) {
      const have = new Set(plan.jobs.filter(j => cached(j.key)).map(j => j.key));
      Promise.all(plan.jobs.filter(j => !have.has(j.key)).map(j => fracture(j.key, j.src, j.opts).then(frs => frs.map(f => ({ ...f, ...j.meta })))))
        .then(list => debris.spawn(list.flat(), opts));
    }
  }

  const B = {
    kinds: BREAKABLE,
    // break one instance. o: { origin, power, dir, up, silent }
    breakItem(e, o = {}) {
      const { kind, it, P } = e, K = BREAKABLE[kind];
      const plan = planFor(kind); if (!plan) return false;
      const rec = { kind, P, it, t: T, solids: [] };
      it.broken = true;
      if (K.glass) {
        const vp = variantPool(kind); if (!vp) return false;
        P.hide(it);
        rec.variantIt = vp.add(it.x, it.y, it.z, it.ry, it.s, null, it.extra, it.scale3);
        vp.dirty = true; vp.last.set(1e9, 0, 0);
      } else {
        P.hide(it);
        rec.solids = solidsOf(it, K);
      }
      spawnKind(kind, plan, it, { ...o, origin: o.origin ?? _v.set(it.x, it.y + K.h * 0.4, it.z) });
      broken.push(rec);
      // fx + sound
      const F = fx(), c = _v2.set(it.x, it.y + K.h * 0.45, it.z);
      if (!o.silent) {
        const d = ctx.camera.position.distanceTo(c), g = Math.min(1.2, 12 / Math.max(4, d));
        if (K.glass) sfx('glass', g); else sfx('crunch', g, 0, K.snd);
      }
      if (F) {
        if (K.glass) B.glitter(c, K.r, 26);
        else F.dust(_v.set(it.x, it.y + 0.1, it.z), { amount: 0.7 });
        if (K.paper || K.spill) for (let i = 0; i < 16; i++) F.alpha.emit({ pos: _v.set(it.x + rnd(-0.4, 0.4), it.y + rnd(0.3, 1.2), it.z + rnd(-0.4, 0.4)), vel: _v2.set(rnd(-2.5, 2.5), rnd(1, 4), rnd(-2.5, 2.5)), life: rnd(1.4, 2.6), size: 0.07, size1: 0.07, color: K.spill ? [0.16, 0.15, 0.14] : [0.8, 0.78, 0.72], alpha: 1, tile: 0, grav: 2.2, drag: 1.8 });
      }
      if (K.jet) rec.jet = { t: 0, life: 14, x: it.x, y: it.y + 0.15, z: it.z };
      world.alarm?.(c, 14);
      return true;
    },
    // break everything breakable within r of p (explosions, hard landings, ground pounds, thrown props)
    breakAt(p, r, o = {}) {
      const hits = []; near(p, r, (e) => hits.push(e));
      for (const e of hits) B.breakItem(e, { origin: p, ...o, silent: hits.length > 2 && e !== hits[0] });
      return hits.length;
    },
    // a moving body (knocked enemy, thrown prop, Spidey at speed) at p with velocity vel: breaks what it runs into
    sweep(p, r, vel, o = {}) {
      const sp = vel.length(); if (sp < (o.minSpeed ?? 6)) return 0;
      const hits = []; near(p, r, (e) => hits.push(e));
      for (const e of hits) B.breakItem(e, { origin: p, dir: _v.copy(vel).multiplyScalar(0.35), power: 2 + sp * 0.12, ...o });
      return hits.length;
    },
    // glass glitter: bright additive sparkles + a few falling specks
    glitter(c, r, n = 20) {
      const F = fx(); if (!F) return;
      for (let i = 0; i < n; i++) {
        F.add.emit({ pos: _v.set(c.x + rnd(-r, r) * 0.7, c.y + rnd(-0.8, 0.8), c.z + rnd(-r, r) * 0.7), vel: _v2.set(rnd(-2.5, 2.5), rnd(0, 3.5), rnd(-2.5, 2.5)), life: rnd(0.5, 1.3), size: rnd(0.02, 0.045), size1: 0.01, color: [3.4, 3.6, 3.8], alpha: 0.9, tile: 0, grav: 12, drag: 0.8 });
      }
    },
    // cars: a hard hit near a car bursts its nearest side window and tears a panel off; the car stops on hazards
    hitCar(p, r, o = {}) {
      const cars = world.carsNear?.(p, r + 3) ?? []; let n = 0;
      for (const car of cars) {
        if ((car.dmg ?? 0) >= 3 || (car.hitT ?? -9) > T - 0.6) continue;
        // body contact: p within r of the car's box (local frame)
        const fx_ = Math.cos(car.ry), fz_ = -Math.sin(car.ry), dx = p.x - car.x, dz = p.z - car.z;
        const lx = dx * fx_ + dz * fz_, lz = -dx * fz_ + dz * fx_, base = car.parked ? 0 : (car.y ?? 0);
        if (Math.abs(lx) > car.len / 2 + r || Math.abs(lz) > car.wid / 2 + r || p.y > base + (car.h ?? 1.5) + r + 0.6 || p.y < base - 1) continue;
        car.hitT = T;
        car.dmg = (car.dmg ?? 0) + 1; n++;
        breakCar(car, p, o);
      }
      return n;
    },
    // combat throwables (game/combat/props.js)
    shatterCrate(g, origin, vel) {
      g.updateMatrixWorld(true);
      const opts = { matrix: g.matrixWorld.clone(), origin, dir: vel ? _v.copy(vel).multiplyScalar(0.25) : null, power: 5, up: 3, life: 7, spin: 12 };
      if (cratePlan.jobs.every(j => cached(j.key))) debris.spawn(piecesNow(cratePlan), opts); else buildPieces(cratePlan).then(p => debris.spawn(p, opts));
      sfx('crunch', 0.9, 0, 'wood');
    },
    burstBin(g, origin, vel) {
      g.updateMatrixWorld(true);
      const pieces = cached('bin');
      const opts = { matrix: g.matrixWorld.clone(), color: lin(0x2f5a37), colorIn: lin(0x6f7470), part: PART.METAL, partIn: PART.METAL, origin, dir: vel ? _v.copy(vel).multiplyScalar(0.3) : null, power: 4.5, up: 3, life: 7, spin: 10 };
      if (pieces) debris.spawn(pieces, opts); else fracture('bin', binShellSrc(), { count: 6, mode: '3D', seed: 9 }).then(p => debris.spawn(p, opts));
      const F = fx(); if (F) for (let i = 0; i < 18; i++) F.alpha.emit({ pos: _v.copy(origin).add(_v2.set(rnd(-0.3, 0.3), rnd(0, 0.5), rnd(-0.3, 0.3))), vel: _v2.set(rnd(-3, 3), rnd(1, 5), rnd(-3, 3)), life: rnd(1, 2), size: 0.08, size1: 0.07, color: [0.14, 0.13, 0.12], alpha: 1, tile: 0, grav: 9, drag: 1 });
      sfx('crunch', 0.8, 0, 'metal');
    },
    update(dt, camPos) {
      T += dt;
      const cam = camPos ?? ctx.camera.position;
      for (const vp of variants.values()) if (vp.due(cam)) vp.update(cam);
      const F = fx();
      for (let i = broken.length - 1; i >= 0; i--) {
        const b = broken[i];
        if (b.jet && F) { // hydrant geyser: a thick white column + spray, thinning out
          const J = b.jet; J.t += dt;
          if (J.t < J.life) {
            const k = 1 - J.t / J.life, n = Math.ceil(5 * k);
            for (let q = 0; q < n; q++) F.alpha.emit({ pos: _v.set(J.x + rnd(-0.06, 0.06), J.y, J.z + rnd(-0.06, 0.06)), vel: _v2.set(rnd(-0.7, 0.7), rnd(9, 13) * (0.6 + 0.4 * k), rnd(-0.7, 0.7)), life: rnd(0.9, 1.3), size: 0.2, size1: 0.9, color: [0.85, 0.9, 0.95], alpha: 0.35 * k + 0.1, tile: 3, grav: 12, drag: 0.6 });
            if (Math.random() < 0.6) F.add.emit({ pos: _v.set(J.x, J.y + rnd(0, 2), J.z), vel: _v2.set(rnd(-2, 2), rnd(2, 7), rnd(-2, 2)), life: 0.6, size: 0.03, size1: 0.01, color: [1.4, 1.5, 1.6], alpha: 0.6, tile: 0, grav: 14 });
            if ((J.snd = (J.snd ?? 0) - dt) <= 0) { J.snd = 0.8; if (ctx.camera.position.distanceTo(_v.set(J.x, J.y, J.z)) < 40) sfx('water', 0.6 * k); }
          } else b.jet = null;
        }
        // respawn: out of sight and far away, after a while
        if (T - b.t > 45 && Math.hypot(b.it.x - cam.x, b.it.z - cam.z) > 170) {
          b.it.broken = false; b.P.show(b.it);
          for (const s of b.solids) world.collision?.enable(s);
          if (b.variantIt) { const vp = variants.get(b.kind); const k = vp.items.indexOf(b.variantIt); if (k >= 0) vp.items.splice(k, 1); vp.dirty = true; vp.last.set(1e9, 0, 0); if (!vp.items.length) { vp.mesh.count = 0; vp.mesh.visible = false; } }
          broken.splice(i, 1);
        }
      }
    },
    // idle-time pre-fracture of every kind (after load)
    warm() {
      const list = [['bin', binShellSrc(), { count: 6, mode: '3D', seed: 9 }], ...cratePlan.jobs.map(j => [j.key, j.src, j.opts])];
      for (const kind of Object.keys(BREAKABLE)) { const pl = planFor(kind); if (pl) for (const j of pl.jobs) list.push([j.key, j.src, j.opts]); }
      prefetch(list);
    },
    brokenCount: () => broken.length,
    ready: () => cratePlan.jobs.every(j => cached(j.key)) && !!cached('bin') && Object.keys(BREAKABLE).every(k => { const pl = planFor(k); return !pl || pl.jobs.every(j => cached(j.key)); }),
    near,
  };

  // --- cars
  const GLASS = [0.03, 0.04, 0.042], GLASS_IN = [0.3, 0.42, 0.36];
  function breakCar(car, p, o) {
    const fx_ = Math.cos(car.ry), fz_ = -Math.sin(car.ry);          // nose direction (vehinst yaw convention)
    const lx = (p.x - car.x) * fx_ + (p.z - car.z) * fz_, lz = -(p.x - car.x) * fz_ + (p.z - car.z) * fx_;
    const side = lz >= 0 ? 1 : -1, base = car.parked ? 0 : (car.y ?? 0);
    const hl = car.len / 2, hw = car.wid / 2, h = car.h ?? 1.5;
    // side window: a pane along the cabin at the impact side, fractured 2.5D at the impact point
    const wl = Math.min(car.len * 0.42, 2.2), wh = Math.max(0.36, h * 0.28), wy = base + h * 0.72;
    const wx = Math.max(-hl * 0.35, Math.min(hl * 0.25, lx));
    const key = 'carwin:' + wl.toFixed(1) + ':' + wh.toFixed(2);
    const M = new THREE.Matrix4().compose(_p.set(car.x + fx_ * wx - fz_ * side * (hw - 0.04), wy, car.z + fz_ * wx + fx_ * side * (hw - 0.04)), _q.setFromAxisAngle(THREE.Object3D.DEFAULT_UP, car.ry), _s.set(1, 1, 1));
    const g = new THREE.BoxGeometry(wl, wh, 0.012);
    const win = { pos: g.attributes.position.array, nrm: g.attributes.normal.array, idx: Uint32Array.from(g.index.array) };
    // shards: burst out of the frame (radial from the cabin centre) and rain down the door; a few go in with the hit
    const cabin = new THREE.Vector3(car.x, wy, car.z);
    const optsW = { matrix: M, color: GLASS, colorIn: GLASS_IN, part: PART.SHARD, partIn: PART.SHARD, origin: cabin, power: 2.2, dir: o.dir ? o.dir.clone().multiplyScalar(0.12) : null, up: 0.6, life: 6, drag: 0.35, spin: 14 };
    const pw = cached(key);
    if (pw) debris.spawn(pw, optsW); else fracture(key, win, { count: 22, mode: '2.5D', axis: 'z', seed: 3, impact: [0, 0, 0], radius: 0.35 }).then(pcs => debris.spawn(pcs, optsW));
    B.glitter(_v2.set(M.elements[12], wy, M.elements[14]), 0.8, 18);
    // a torn-off panel: a door skin (impact at the side) or the hood (impact at the nose), in the car's paint
    const tint = Array.isArray(car.color) ? car.color : [0.3, 0.3, 0.3];
    const hood = Math.abs(lx) > hl * 0.55;
    const pw2 = hood ? hw * 1.7 : Math.min(1.2, car.len * 0.24), ph = hood ? 0.05 : h * 0.4, pd = hood ? hl * 0.45 : 0.05;
    const pg = new THREE.BoxGeometry(hood ? pd : pw2, hood ? ph : ph, hood ? pw2 : pd).translate(0, 0, 0);
    const pc = { pos: pg.attributes.position.array, nrm: pg.attributes.normal.array, idx: Uint32Array.from(pg.index.array), n0: pg.index.count, c: [0, 0, 0] };
    const pos = hood ? _v.set(car.x + fx_ * Math.sign(lx) * hl * 0.72, base + h * 0.62, car.z + fz_ * Math.sign(lx) * hl * 0.72)
      : _v.set(car.x + fx_ * wx - fz_ * side * (hw + 0.03), base + h * 0.42, car.z + fz_ * wx + fx_ * side * (hw + 0.03));
    const Mp = new THREE.Matrix4().compose(pos, _q.setFromAxisAngle(THREE.Object3D.DEFAULT_UP, car.ry), _s.set(1, 1, 1));
    // the panel is ripped off and thrown clear of the car (outward from the body centre), tumbling
    debris.spawn([pc], { matrix: Mp, color: tint, colorIn: [0.2, 0.2, 0.21], part: PART.PAINT, partIn: PART.METAL, origin: new THREE.Vector3(car.x, base + h * 0.4, car.z), power: 7, up: 3, life: 12, spin: 5, bounce: 0.2 });
    // the car stops, hazards on, alarm
    if (car.parked) car.haz = true; else car.v = 0; // moving cars: traffic.js keeps a smashed car (c.dmg) stopped on hazards
    world.alarm?.(p, 18);
    sfx('glass', 0.9); sfx('crunch', 1, 0, 'metal');
  }

  return B;
}
