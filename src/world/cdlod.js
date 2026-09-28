// (water-effects) Continuous distance-dependent LOD quadtree grid (Strugar 2010) for the water surface.
// Adapted from dgreenheck/tidewater src/core/CDLOD.js (MIT, (c) 2026 DRG Software Solutions LLC): same selection and
// world-space geomorph, ported from WGSL to GLSL / three.js r186 WebGL.
//
// One G x G grid mesh is instanced for every selected node (instanced attribute `nodeData` = origin x, z, size, lod).
// Vertices near the outer edge of each LOD range morph toward the next coarser lattice: no cracks, no pops, and every
// vertex sits on a fixed world lattice (waves sampled at it never swim as the camera moves).
//
// GLSL (CDLOD_GLSL, vertex shader; needs `attribute vec4 nodeData;` and `uniform vec4 uCdlodMorph[levels];`):
//   vec4 cdlodMorph(vec4 node, vec2 grid, vec3 viewPos)  -> (world x, world z, spacing, morphK)
import * as THREE from 'three';

export class CDLOD {
  constructor({ gridSize = 32, leafSize = 8, levels = 15, rangeFactor = 2.5, morphStartRatio = 0.66, maxInstances = 1200,
    minY = -3, maxY = 1 } = {}) {
    this.G = gridSize; this.leafSize = leafSize; this.levels = levels; this.minY = minY; this.maxY = maxY;
    this.ranges = [];
    const morph = [];
    let prev = 0;
    for (let l = 0; l < levels; l++) {
      const r = leafSize * 2 ** l * rangeFactor;
      this.ranges.push(r);
      const start = prev + (r - prev) * morphStartRatio;
      morph.push(new THREE.Vector4(start, 1 / Math.max(1e-3, r - start), leafSize * 2 ** l / gridSize, 0));
      prev = r;
    }
    this.uMorph = { value: morph };
    this.glsl = /* glsl */`
vec4 cdlodMorph(vec4 node, vec2 grid, vec3 viewPos, float y0) {
  vec4 m = uCdlodMorph[int(node.w + 0.5)];
  float h = m.z;
  vec2 p = node.xy + grid * node.z;
  vec2 idx = floor(p / h + 1e-3);
  vec2 snapped = idx * h;
  float dist = length(viewPos - vec3(snapped.x, y0, snapped.y));
  float morphK = clamp((dist - m.x) * m.y, 0.0, 1.0);
  vec2 odd = fract(idx * 0.5) * 2.0;
  return vec4(snapped - odd * h * morphK, h * (morphK + 1.0), morphK);
}
`;
    // grid in [0,1]^2 on xz, quads in column strips (post-transform cache reuse), alternating diagonals
    const Gs = gridSize, verts = new Float32Array((Gs + 1) * (Gs + 1) * 3);
    let p = 0;
    for (let j = 0; j <= Gs; j++) for (let i = 0; i <= Gs; i++) { verts[p++] = i / Gs; verts[p++] = 0; verts[p++] = j / Gs; }
    const STRIP = 8, idx = new Uint32Array(Gs * Gs * 6);
    p = 0;
    for (let i0 = 0; i0 < Gs; i0 += STRIP) for (let j = 0; j < Gs; j++) for (let i = i0; i < Math.min(i0 + STRIP, Gs); i++) {
      const a = j * (Gs + 1) + i, b = a + 1, c = a + Gs + 1, d = c + 1;
      if ((i + j) % 2 === 0) { idx[p++] = a; idx[p++] = c; idx[p++] = b; idx[p++] = b; idx[p++] = c; idx[p++] = d; }
      else { idx[p++] = a; idx[p++] = c; idx[p++] = d; idx[p++] = a; idx[p++] = d; idx[p++] = b; }
    }
    const geo = new THREE.InstancedBufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(verts, 3));
    geo.setAttribute('normal', new THREE.BufferAttribute(new Float32Array((Gs + 1) * (Gs + 1) * 3).map((_, i) => (i % 3 === 1 ? 1 : 0)), 3));
    geo.setIndex(new THREE.BufferAttribute(idx, 1));
    this.nodeArray = new Float32Array(maxInstances * 4);
    this.nodeAttr = new THREE.InstancedBufferAttribute(this.nodeArray, 4);
    this.nodeAttr.setUsage(THREE.DynamicDrawUsage);
    geo.setAttribute('nodeData', this.nodeAttr);
    geo.instanceCount = 0;
    geo.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e7);
    geo.boundingBox = new THREE.Box3(new THREE.Vector3(-1e7, -1e7, -1e7), new THREE.Vector3(1e7, 1e7, 1e7));
    this.geometry = geo;
    this.maxInstances = maxInstances;
    this.count = 0;
    this._box = new THREE.Box3(); this._frustum = new THREE.Frustum(); this._mat = new THREE.Matrix4(); this._cam = new THREE.Vector3();
    this._order = [];
  }

  update(camera) {
    camera.updateMatrixWorld();
    this._mat.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
    this._frustum.setFromProjectionMatrix(this._mat, camera.coordinateSystem, camera.reversedDepth);
    camera.getWorldPosition(this._cam);
    this.count = 0;
    const top = this.levels - 1, rootSize = this.leafSize * 2 ** top;
    const cx = Math.floor(this._cam.x / rootSize), cz = Math.floor(this._cam.z / rootSize);
    for (let j = -1; j <= 1; j++) for (let i = -1; i <= 1; i++) this._select((cx + i) * rootSize, (cz + j) * rootSize, rootSize, top);
    // front to back: early depth rejects hidden wave faces
    const n = this.count, arr = this.nodeArray, c = this._cam, order = this._order;
    order.length = n;
    for (let i = 0; i < n; i++) {
      const s = arr[i * 4 + 2];
      const dx = Math.max(arr[i * 4] - c.x, 0, c.x - arr[i * 4] - s), dz = Math.max(arr[i * 4 + 1] - c.z, 0, c.z - arr[i * 4 + 1] - s);
      const o = order[i] || (order[i] = {});
      o.d = dx * dx + dz * dz; o.x = arr[i * 4]; o.z = arr[i * 4 + 1]; o.s = s; o.l = arr[i * 4 + 3];
    }
    order.sort((a, b) => a.d - b.d);
    for (let i = 0; i < n; i++) { const o = order[i]; arr[i * 4] = o.x; arr[i * 4 + 1] = o.z; arr[i * 4 + 2] = o.s; arr[i * 4 + 3] = o.l; }
    this.geometry.instanceCount = n;
    this.nodeAttr.clearUpdateRanges(); this.nodeAttr.addUpdateRange(0, n * 4); this.nodeAttr.needsUpdate = true;
  }
  _bounds(x, z, size) { this._box.min.set(x, this.minY, z); this._box.max.set(x + size, this.maxY, z + size); return this._box; }
  _inSphere(box, r) {
    const c = this._cam;
    const dx = Math.max(box.min.x - c.x, 0, c.x - box.max.x), dy = Math.max(box.min.y - c.y, 0, c.y - box.max.y), dz = Math.max(box.min.z - c.z, 0, c.z - box.max.z);
    return dx * dx + dy * dy + dz * dz <= r * r;
  }
  _add(x, z, size, lod) {
    if (this.count >= this.maxInstances) return;
    const o = this.count * 4;
    this.nodeArray[o] = x; this.nodeArray[o + 1] = z; this.nodeArray[o + 2] = size; this.nodeArray[o + 3] = lod;
    this.count++;
  }
  _select(x, z, size, lod) {
    const box = this._bounds(x, z, size);
    if (!this._inSphere(box, this.ranges[lod])) return false;
    if (!this._frustum.intersectsBox(box)) return true;
    if (lod === 0 || !this._inSphere(box, this.ranges[lod - 1])) { this._add(x, z, size, lod); return true; }
    const h = size * 0.5;
    for (const [cx, cz] of [[x, z], [x + h, z], [x, z + h], [x + h, z + h]]) {
      if (!this._select(cx, cz, h, lod - 1)) {
        const b = this._bounds(cx, cz, h);
        if (this._frustum.intersectsBox(b)) this._add(cx, cz, h, lod);
      }
    }
    return true;
  }
}
