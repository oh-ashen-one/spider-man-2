// node --test test/  — destruction (src/game/destruction): prop splitting + three-pinata fracture jobs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { MB } from '../src/world/geom.js';
import { PART } from '../src/world/partmat.js';
import { components, planPieces } from '../src/game/destruction/pieces.js';
import { fractureJob } from '../src/game/destruction/fracture.worker.js';

const src = (g) => ({ pos: g.attributes.position.array, nrm: g.attributes.normal.array, idx: Uint32Array.from(g.index.array) });
const bounds = (pieces) => {
  const b = new THREE.Box3(), v = new THREE.Vector3();
  for (const f of pieces) for (let i = 0; i < f.pos.length; i += 3) b.expandByPoint(v.set(f.pos[i] + f.c[0], f.pos[i + 1] + f.c[1], f.pos[i + 2] + f.c[2]));
  return b;
};

test('components: welded parts, colours, part ids and the watertight flag', () => {
  const b = new MB();
  b.setPart(PART.PAINT).setColor(0xff0000).box(0, 0, 0, 1, 1, 1);          // closed box (unwelded faces: welded by position)
  b.setPart(PART.GLASS).setColor(0).box(2, 0, 0, 3, 1, 0.01, 0b110000);   // two-faced pane: open
  b.setPart(PART.WOOD).setColor(0x00ff00).cyl(5, 0, 0, 0.2, 0.2, 1, 8, true);
  const c = components(b.build({ part: true }));
  assert.equal(c.length, 4, 'box, the pane\'s two faces, cylinder');
  const box = c.find(x => x.part === PART.PAINT), pane = c.find(x => x.part === PART.GLASS), cyl = c.find(x => x.part === PART.WOOD);
  assert.ok(box.watertight, 'closed box is watertight');
  assert.ok(!pane.watertight, 'a two-faced pane is open');
  assert.ok(cyl.watertight, 'capped cylinder is watertight');
  assert.ok(box.color[0] > 0.9 && box.color[1] < 0.01, 'vertex colour carried');
});

test('planPieces: solids -> 3D Voronoi, glass -> 2.5D slab, thin parts rigid', () => {
  const b = new MB();
  b.setPart(PART.CONCRETE).setColor(0x888888).box(-0.5, 0, -0.5, 0.5, 0.8, 0.5);
  b.setPart(PART.GLASS).setColor(0).box(1, 0.2, 0, 3, 2.2, 0.01, 0b110000);
  b.setPart(PART.METAL).setColor(0x444444).box(4, 0, 0, 4.02, 1, 0.02);      // a 2 cm bar: rigid chunk
  const plan = planPieces('t', b.build({ part: true }));
  assert.equal(plan.jobs.filter(j => j.meta.glass).length, 1, 'the two pane faces make one pane');
  const glass = plan.jobs.find(j => j.meta.glass), solid = plan.jobs.find(j => !j.meta.glass);
  assert.equal(glass.opts.mode, '2.5D');
  assert.equal(glass.opts.axis, 'z', 'projects through the thin axis');
  assert.equal(glass.meta.part, PART.SHARD);
  assert.equal(solid.opts.mode, '3D');
  assert.equal(plan.rigid.length, 1);
});

test('fractureJob: pieces tile the source (3D, stretched splinters, 2.5D glass)', () => {
  for (const [g, opts] of [
    [new THREE.BoxGeometry(0.7, 0.6, 0.7), { count: 12, mode: '3D', seed: 1 }],
    [new THREE.BoxGeometry(0.7, 0.6, 0.03), { count: 6, mode: '3D', seed: 2, stretch: [0.3, 1, 1] }],
    [new THREE.BoxGeometry(2, 1.2, 0.01), { count: 20, mode: '2.5D', axis: 'z', seed: 3, impact: [0, 0, 0], radius: 0.3 }],
  ]) {
    g.computeBoundingBox();
    const out = fractureJob({ ...src(g), opts });
    assert.ok(out.length >= Math.min(opts.count, 4), `${out.length} pieces`);
    const b = bounds(out);
    for (const k of ['x', 'y', 'z']) {
      assert.ok(Math.abs(b.min[k] - g.boundingBox.min[k]) < 1e-3 && Math.abs(b.max[k] - g.boundingBox.max[k]) < 1e-3, `bounds ${k}`);
    }
    for (const f of out) {
      assert.ok(f.n0 <= f.idx.length && f.idx.length % 3 === 0);
      const nv = f.pos.length / 3; for (const i of f.idx) assert.ok(i < nv);
    }
  }
});
