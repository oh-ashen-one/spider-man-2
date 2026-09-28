// OWNER: destruction (pinata-and-trees). Off-thread Voronoi fracture with three-pinata: a 3D / 2.5D fracture of a
// 20-40 piece mesh costs 10-25 ms of synchronous CPU, so it never runs on the render thread (fracture.js).
// Message in:  { id, jobs: [{ pos, nrm, uv?, idx, opts }] }   typed arrays (transferred)
//   opts: { count, mode: '3D' | '2.5D', seed, impact?: [x,y,z], radius?, axis?: 'x'|'y'|'z'|'auto', normal?: [x,y,z],
//           stretch?: [sx,sy,sz] (fracture a scaled copy then scale back: elongated cells = wood splinters) }
// Message out: { id, out: [[{ pos, nrm, idx, n0, c: [x,y,z] }, ...] per job] }   n0 = index count of the outer faces
//   (the rest are the cut / interior faces); geometry is centred on c (model space of the input).
import * as THREE from 'three';
import { DestructibleMesh, FractureOptions } from '@dgreenheck/three-pinata';

const V = (a) => (a ? new THREE.Vector3(a[0], a[1], a[2]) : undefined);

export function fractureJob(j) {
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(j.pos, 3));
  g.setAttribute('normal', new THREE.BufferAttribute(j.nrm, 3));
  if (j.uv) g.setAttribute('uv', new THREE.BufferAttribute(j.uv, 2));
  g.setIndex(new THREE.BufferAttribute(j.idx, 1));
  const o = j.opts, st = o.stretch;
  if (st) g.scale(st[0], st[1], st[2]);
  const m = new DestructibleMesh(g);
  m.updateMatrixWorld(true);
  const scaleV = (v) => (v && st ? v.multiply(new THREE.Vector3(st[0], st[1], st[2])) : v);
  let frags = [];
  try {
    frags = m.fracture(new FractureOptions({
      fractureMethod: 'voronoi', fragmentCount: o.count, seed: o.seed,
      voronoiOptions: { mode: o.mode || '3D', impactPoint: scaleV(V(o.impact)), impactRadius: o.radius ? o.radius * (st ? Math.max(...st) : 1) : undefined,
        projectionAxis: o.axis || 'auto', projectionNormal: V(o.normal) },
    }));
  } catch (e) { return []; }
  const out = [];
  for (const f of frags) {
    const G = f.geometry;
    if (st) { G.scale(1 / st[0], 1 / st[1], 1 / st[2]); G.computeVertexNormals(); f.position.set(f.position.x / st[0], f.position.y / st[1], f.position.z / st[2]); }
    const idx = G.index.array, n0 = G.groups[0]?.count ?? idx.length;
    if (idx.length < 12) continue; // degenerate sliver
    out.push({ pos: G.attributes.position.array, nrm: G.attributes.normal.array, idx: idx instanceof Uint32Array ? idx : Uint32Array.from(idx), n0, c: [f.position.x, f.position.y, f.position.z] });
  }
  return out;
}

if (typeof self !== 'undefined' && typeof window === 'undefined') {
  self.onmessage = ({ data }) => {
    const out = [], transfer = [];
    for (const j of data.jobs) {
      const r = fractureJob(j);
      for (const f of r) transfer.push(f.pos.buffer, f.nrm.buffer, f.idx.buffer);
      out.push(r);
    }
    self.postMessage({ id: data.id, out }, transfer);
  };
}
