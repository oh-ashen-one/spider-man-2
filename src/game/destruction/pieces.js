// OWNER: destruction (pinata-and-trees). Turns renderable geometry into breakable pieces:
//  - components(geo): splits a vertex-coloured, part-tagged prop geometry (world/geom.js MB output) into its
//    connected parts (welded by position), each with its colour, part id and a watertight flag
//  - planPieces(key, geo): per component -> a Voronoi fracture job (watertight solids big enough to break), a 2.5D
//    shatter job (glass parts, closed into a thin slab first) or a rigid chunk (thin / open parts: poles, slats, paper)
//  - buildPieces(plan): resolves the fracture jobs (fracture.js, cached) into a flat piece list for debris.spawn
// Pieces are model space (centre c), carry {color, colorIn, part, partIn, drag, paint}; paint parts take the
// instance tint at spawn time (props are tinted per instance).
import * as THREE from 'three';
import { PART } from '../../world/partmat.js';
import { fracture, cached } from './fracture.js';

export function components(geo) {
  const P = geo.attributes.position, Nn = geo.attributes.normal, C = geo.attributes.color, Pa = geo.attributes.aPart;
  const I = geo.index ? geo.index.array : Uint32Array.from({ length: P.count }, (_, i) => i);
  // weld by quantised position (1 mm)
  const weld = new Int32Array(P.count), keys = new Map();
  for (let i = 0; i < P.count; i++) {
    const k = Math.round(P.getX(i) * 1000) + ',' + Math.round(P.getY(i) * 1000) + ',' + Math.round(P.getZ(i) * 1000);
    let w = keys.get(k); if (w === undefined) { w = keys.size; keys.set(k, w); } weld[i] = w;
  }
  const par = new Int32Array(keys.size).map((_, i) => i);
  const find = (a) => { while (par[a] !== a) { par[a] = par[par[a]]; a = par[a]; } return a; };
  const uni = (a, b) => { a = find(a); b = find(b); if (a !== b) par[a] = b; };
  for (let t = 0; t < I.length; t += 3) { uni(weld[I[t]], weld[I[t + 1]]); uni(weld[I[t]], weld[I[t + 2]]); }
  const groups = new Map();
  for (let t = 0; t < I.length; t += 3) { const r = find(weld[I[t]]); let g = groups.get(r); if (!g) groups.set(r, (g = [])); g.push(t); }
  const out = [];
  for (const tris of groups.values()) {
    const remap = new Map(), pos = [], nrm = [], idx = [], col = [0, 0, 0], parts = new Map(), edges = new Map();
    const box = new THREE.Box3();
    for (const t of tris) {
      for (let v = 0; v < 3; v++) {
        const i = I[t + v];
        let k = remap.get(i);
        if (k === undefined) {
          k = remap.size; remap.set(i, k);
          pos.push(P.getX(i), P.getY(i), P.getZ(i)); nrm.push(Nn.getX(i), Nn.getY(i), Nn.getZ(i));
          box.expandByPoint(new THREE.Vector3(P.getX(i), P.getY(i), P.getZ(i)));
          if (C) { col[0] += C.getX(i); col[1] += C.getY(i); col[2] += C.getZ(i); }
          const pa = Pa ? Math.round(Pa.getX(i)) : 0; parts.set(pa, (parts.get(pa) || 0) + 1);
        }
        idx.push(k);
        const a = weld[i], b = weld[I[t + (v + 1) % 3]], ek = a < b ? a * 1e7 + b : b * 1e7 + a;
        edges.set(ek, (edges.get(ek) || 0) + 1);
      }
    }
    let watertight = true; for (const n of edges.values()) if (n % 2) { watertight = false; break; }
    const nv = remap.size;
    let part = 0, best = -1; for (const [k, n] of parts) if (n > best) { best = n; part = k; }
    const size = box.getSize(new THREE.Vector3());
    out.push({ pos: Float32Array.from(pos), nrm: Float32Array.from(nrm), idx: Uint32Array.from(idx), color: C ? col.map(c => c / nv) : [0.5, 0.5, 0.5], part, box, size, watertight });
  }
  return out;
}

// thin closed slab from a (possibly one- or two-faced) glass component's bounds
function slab(box, minT = 0.014) {
  const s = box.getSize(new THREE.Vector3()), c = box.getCenter(new THREE.Vector3());
  const ax = s.x <= s.y && s.x <= s.z ? 'x' : s.y <= s.z ? 'y' : 'z';
  s[ax] = Math.max(s[ax], minT);
  const g = new THREE.BoxGeometry(s.x, s.y, s.z).translate(c.x, c.y, c.z);
  return { src: { pos: g.attributes.position.array, nrm: g.attributes.normal.array, idx: Uint32Array.from(g.index.array) }, axis: ax, area: s.x * s.y * s.z / s[ax], c };
}

const GLASS_FACE = [0.03, 0.04, 0.042];
const centred = (cp) => {
  const c = cp.box.getCenter(new THREE.Vector3()), pos = cp.pos.slice();
  for (let i = 0; i < pos.length; i += 3) { pos[i] -= c.x; pos[i + 1] -= c.y; pos[i + 2] -= c.z; }
  return { pos, nrm: cp.nrm, idx: cp.idx, n0: cp.idx.length, c: [c.x, c.y, c.z] };
};

// inner (cut-face) colour: raw material colour of the part (wood lighter / fibrous, paint -> bare metal, stone paler)
function innerOf(part, color) {
  if (part === PART.GLASS) return [0.3, 0.42, 0.36];
  if (part === PART.WOOD) return color.map((c, k) => c * 1.25 + [0.06, 0.04, 0.02][k]);
  if (part === PART.PAINT || part === PART.METAL) return [0.22, 0.21, 0.2];
  if (part === PART.CONCRETE) return color.map(c => c * 1.15 + 0.03);
  return color.map(c => c * 0.8);
}

// plan: { key, jobs: [{ key, src, opts, meta }], rigid: [piece] }
//   opts: { maxPieces (per solid, default 7), glassDensity (shards per m^2, default 14), drop (m: smaller parts are
//   discarded), splinter: stretch for wood }
export function planPieces(key, geo, o = {}) {
  const comps = components(geo);
  // one- / two-faced glass panes come apart into one component per face: merge overlapping glass into one pane
  for (let i = 0; i < comps.length; i++) {
    const a = comps[i]; if (a.part !== PART.GLASS || a.merged) continue;
    const ex = a.box.clone().expandByScalar(0.03);
    for (let j = i + 1; j < comps.length; j++) {
      const b = comps[j]; if (b.part !== PART.GLASS || b.merged || !ex.intersectsBox(b.box)) continue;
      const u = a.box.clone().union(b.box), us = u.getSize(new THREE.Vector3());
      if (Math.min(us.x, us.y, us.z) > 0.05) continue; // a neighbouring pane at an angle, not the other face of this one
      a.box.copy(u); ex.copy(a.box).expandByScalar(0.03); b.merged = true;
    }
    a.size = a.box.getSize(new THREE.Vector3());
  }
  const jobs = [], rigid = [];
  let seed = 11;
  comps.forEach((cp, i) => {
    if (cp.merged) return;
    const s = cp.size, big = Math.max(s.x, s.y, s.z), small = Math.min(s.x, s.y, s.z);
    if (big < (o.drop ?? 0.03)) return;
    const meta = { color: cp.color, part: cp.part, colorIn: innerOf(cp.part, cp.color), partIn: cp.part === PART.GLASS ? PART.SHARD : cp.part === PART.PAINT ? PART.METAL : cp.part, paint: cp.part === PART.PAINT };
    if (cp.part === PART.GLASS && big > 0.3) {
      const sl = slab(cp.box, 0.01);
      const n = Math.max(12, Math.min(56, Math.round(sl.area * (o.glassDensity ?? 26))));
      jobs.push({ key: `${key}#${i}`, src: sl.src, opts: { count: n, mode: '2.5D', axis: sl.axis, seed: seed++, impact: [sl.c.x, sl.c.y, sl.c.z], radius: Math.sqrt(sl.area) * 0.22 }, meta: { ...meta, color: GLASS_FACE, part: PART.SHARD, drag: 0.35, glass: true } });
      return;
    }
    const vol = s.x * s.y * s.z;
    if (cp.watertight && big > 0.16 && small > 0.025 && vol > 0.0015) {
      const n = Math.max(o.minPieces ?? 2, Math.min(o.maxPieces ?? 7, Math.round(Math.cbrt(vol) * 14)));
      const wood = cp.part === PART.WOOD || o.splinter;
      const st = wood ? (s.x >= s.y && s.x >= s.z ? [0.3, 1, 1] : s.y >= s.z ? [1, 0.3, 1] : [1, 1, 0.3]) : null;
      jobs.push({ key: `${key}#${i}`, src: { pos: cp.pos, nrm: cp.nrm, idx: cp.idx }, opts: { count: n, mode: '3D', seed: seed++, stretch: st }, meta });
      return;
    }
    rigid.push({ ...centred(cp), ...meta, drag: small < 0.012 && big > 0.08 ? 3.2 : 0.15 });
  });
  return { key, jobs, rigid };
}

// -> Promise<pieces>; pieces of fracture jobs inherit the job's meta
export async function buildPieces(plan) {
  const res = await Promise.all(plan.jobs.map(j => fracture(j.key, j.src, j.opts)));
  const out = [...plan.rigid];
  res.forEach((frs, k) => { const m = plan.jobs[k].meta; for (const f of frs) out.push({ ...f, ...m }); });
  return out;
}
export function piecesReady(plan) { return plan.jobs.every(j => cached(j.key)); }
export function piecesNow(plan) {
  const out = [...plan.rigid];
  for (const j of plan.jobs) { const frs = cached(j.key); if (!frs) continue; for (const f of frs) out.push({ ...f, ...j.meta }); }
  return out;
}
