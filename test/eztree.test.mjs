// node --test test/  — vendored ez-tree (src/world/eztree): the (pat) fixes
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { Tree, TreePreset, applyEzWind, ezWindUniforms, EZ_LEAF_WEIGHT } from '../src/world/eztree/index.js';

const oak = (seed = 3) => { const t = new Tree(); t.options.copy(structuredClone(TreePreset['Oak Medium'])); t.options.seed = seed; return t; };

test('same seed -> identical skeleton at every detail level (LOD silhouettes agree)', () => {
  const a = oak().createGeometry({}), a2 = oak().createGeometry({}), b = oak().createGeometry({ sectionStride: 4, segmentFactor: 0.5 });
  for (const g of [a, a2, b]) { g.leaves.computeBoundingBox(); g.branches.computeBoundingBox(); }
  assert.deepEqual(a.leaves.boundingBox.max.toArray(), a2.leaves.boundingBox.max.toArray(), 'deterministic');
  assert.deepEqual(a.leaves.boundingBox.max.toArray(), b.leaves.boundingBox.max.toArray(), 'same leaves at a coarser branch level');
  assert.ok(b.branches.index.count < a.branches.index.count / 2, 'coarser level has far fewer triangles');
});

test('bark carries a wind weight: 0 at the trunk base, rising to the twig tips', () => {
  const g = oak().createGeometry({});
  const w = g.branches.attributes.aWind; assert.ok(w, 'aWind attribute');
  assert.equal(w.count, g.branches.attributes.position.count);
  let min = Infinity, max = -Infinity; for (let i = 0; i < w.count; i++) { min = Math.min(min, w.getX(i)); max = Math.max(max, w.getX(i)); }
  assert.equal(min, 0); assert.ok(max > 0.7 && max <= 1);
});

test('metric bark UVs run along the branch', () => {
  const g = oak().createGeometry({ metricUV: 2 });
  const uv = g.branches.attributes.uv; let maxV = 0; for (let i = 0; i < uv.count; i++) maxV = Math.max(maxV, uv.getY(i));
  assert.ok(maxV > 3, `v spans the trunk length (max ${maxV.toFixed(1)})`);
});

test('wind patch keeps the instancing path (fix 1) and samples world space + instance phase (fix 2)', () => {
  const mat = applyEzWind(new THREE.MeshStandardMaterial(), ezWindUniforms(), EZ_LEAF_WEIGHT);
  const sh = { uniforms: {}, vertexShader: THREE.ShaderLib.standard.vertexShader, fragmentShader: '' };
  mat.onBeforeCompile(sh);
  assert.ok(sh.vertexShader.includes('#include <project_vertex>'), 'stock project_vertex (instanceMatrix) untouched');
  const i = sh.vertexShader.indexOf('#include <begin_vertex>'), j = sh.vertexShader.indexOf('#include <project_vertex>');
  const patch = sh.vertexShader.slice(i, j);
  assert.ok(patch.includes('instanceMatrix * ezW') && patch.includes('modelMatrix * ezW'), 'noise in world space');
  assert.ok(patch.includes('ezPhase'), 'per-instance phase');
  assert.ok(sh.uniforms.uTime && sh.uniforms.uWindStrength, 'shared uniforms bound');
});

test('shadow pass sways too: createDepthMaterial applies the same wind (fix 3)', () => {
  const t = oak(); t.generate();
  const d = t.leavesMesh.customDepthMaterial;
  assert.ok(d?.isMeshDepthMaterial, 'leaves have a custom depth material');
  const sh = { uniforms: {}, vertexShader: THREE.ShaderLib.depth.vertexShader, fragmentShader: '' };
  d.onBeforeCompile(sh);
  assert.ok(sh.vertexShader.includes('ezSimplex3'));
  assert.strictEqual(sh.uniforms.uTime, t.wind.uTime, 'same time uniform as the leaves');
});
