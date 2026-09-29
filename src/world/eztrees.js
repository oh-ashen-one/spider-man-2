// OWNER: city agent (pinata-and-trees). Near-range trees from ez-tree (vendored v2, world/eztree/): per tree kind of
// trees.js (street / park / elm / small / conifer, + shrub-border bushes) a few seeded archetypes are grown at load,
// normalised to the kind's measured size (the placement / clearance logic of trees.js stays valid) and meshed at two
// detail levels. They draw through the same distance Pools (instancing, dithered LOD cross-fades, shadow prefix) as
// the existing trees, which keep everything beyond EZ.far (leaf-card canopies -> cauliflower crowns -> blobs), with
// their crown lobes re-fitted to the ez-tree canopies so the silhouettes agree across the hand-over.
//   const EZ = buildEzArchetypes();   EZ.lobes(kind) -> lobes | null;   EZ.attach({ scene, out, pools, kinds, uTime })
// Leaves: the ez-tree leaf-spray textures (MIT) turned into value maps and tinted per instance with trees.js' autumn
// palettes (aTintA / aTintB), crown self-occlusion from a per-leaf exposure, TAA-dithered alpha, sun translucency, wind
// (bark sways too, and the shadows follow: customDepthMaterial). Bark: the city's bark array (treetrunk.js, aBark).
// Quality: getQuality().eztree (false = the old trees everywhere), ?qset=eztree:0
import * as THREE from 'three';
import { Tree, TreePreset, applyEzWind, ezWindUniforms, EZ_LEAF_WEIGHT } from './eztree/index.js';
import { barkMaterial } from './treetrunk.js';
import { Pool } from './pool.js';
import { csmShared } from '../render/csm.js';
import { mulberry32 } from './layout.js';

export const EZ = { near: 20, far: 44 }; // L0 < near < L1 < far < trees.js LOD chain (dithered bands of 10 m)
const BARK_TILE = 0.85; // metres per bark repeat (treetrunk.js TILE)

// kind -> ez preset, target height (m, the kind's crown top at s = 1 in trees.js) and crown width, seeds, tuning
const KINDS = {
  street: { preset: 'Ash Medium', h: 9.6, w: 8.4, seeds: [7, 19, 31], leaf: 'ash', leafScale: 1.05 },
  park: { preset: 'Oak Medium', h: 14.2, w: 13.5, seeds: [3, 11, 29], leaf: 'oak', leafScale: 1.1 },
  elm: { preset: 'Ash Large', h: 17.2, w: 15.5, seeds: [5, 23], leaf: 'ash', tune: (o) => { o.branch.angle[1] = 38; o.branch.angle[2] = 42; o.branch.start[1] = 0.45; } }, // vase
  small: { preset: 'Oak Small', h: 6.8, w: 6.2, seeds: [2, 13], leaf: 'oak', leafScale: 1.2 },
  conifer: { preset: 'Pine Medium', h: 13.4, w: 7.2, seeds: [4, 17], leaf: 'pine', leafScale: 1.25 },
  hedge: { preset: 'Bush 2', h: 6.6, w: 6.2, seeds: [8, 21], leaf: 'aspen' }, // trees.js squashes the shrub border (scale3)
};
const LODS = [
  { sectionStride: 2, segmentFactor: 0.75, leafStride: 1 },
  { sectionStride: 6, segmentFactor: 0.4, leafStride: 2, leafScale: 1.3 },
];

// crown lobes (trees.js format {x, y, z, r, sy}) fitted to the leaf cloud: k-means on the leaf-quad centres
function fitLobes(pts, k, seed) {
  const rnd = mulberry32(seed), n = pts.length / 3;
  if (n < k) return null;
  const C = [];
  for (let i = 0; i < k; i++) { const j = Math.floor(rnd() * n) * 3; C.push([pts[j], pts[j + 1], pts[j + 2]]); }
  const asg = new Int32Array(n);
  for (let it = 0; it < 12; it++) {
    for (let i = 0; i < n; i++) {
      let bd = Infinity; for (let c = 0; c < k; c++) { const d = (pts[i * 3] - C[c][0]) ** 2 + (pts[i * 3 + 1] - C[c][1]) ** 2 + (pts[i * 3 + 2] - C[c][2]) ** 2; if (d < bd) { bd = d; asg[i] = c; } }
    }
    const S = C.map(() => [0, 0, 0, 0]);
    for (let i = 0; i < n; i++) { const s = S[asg[i]]; s[0] += pts[i * 3]; s[1] += pts[i * 3 + 1]; s[2] += pts[i * 3 + 2]; s[3]++; }
    S.forEach((s, c) => { if (s[3]) C[c] = [s[0] / s[3], s[1] / s[3], s[2] / s[3]]; });
  }
  const L = C.map(() => ({ rh: 0, rv: 0, m: 0 }));
  for (let i = 0; i < n; i++) {
    const c = asg[i], l = L[c];
    const dh = Math.hypot(pts[i * 3] - C[c][0], pts[i * 3 + 2] - C[c][2]), dv = Math.abs(pts[i * 3 + 1] - C[c][1]);
    l.rh += dh * dh; l.rv += dv * dv; l.m++;
  }
  return C.map((c, i) => {
    const l = L[i]; if (!l.m) return null;
    const rh = Math.sqrt(l.rh / l.m) * 1.55, rv = Math.sqrt(l.rv / l.m) * 1.55;
    return { x: c[0], y: c[1], z: c[2], r: Math.max(0.6, rh), sy: Math.max(0.45, Math.min(1.2, rv / Math.max(0.6, rh))) };
  }).filter(Boolean).sort((a, b) => b.r - a.r);
}

// per-leaf attributes for the shader: aLeafE = (exposure: 0 deep inside / underneath .. 1 outer sun-side shell,
// per-leaf random)
function leafAttrs(g) {
  const P = g.attributes.position, n = P.count;
  g.computeBoundingBox();
  const b = g.boundingBox, cx = (b.min.x + b.max.x) / 2, cz = (b.min.z + b.max.z) / 2, cy = b.min.y + (b.max.y - b.min.y) * 0.55;
  const R = Math.max(b.max.x - b.min.x, b.max.z - b.min.z) / 2 || 1, H = b.max.y - b.min.y || 1;
  const E = new Float32Array(n * 2);
  for (let q = 0; q + 3 < n; q += 4) {
    let x = 0, y = 0, z = 0; for (let k = 0; k < 4; k++) { x += P.getX(q + k); y += P.getY(q + k); z += P.getZ(q + k); }
    x /= 4; y /= 4; z /= 4;
    const rad = Math.min(1, Math.hypot((x - cx) / R, (y - cy) / (H * 0.55), (z - cz) / R));
    const hy = (y - b.min.y) / H;
    const ex = Math.min(1, Math.max(0, 0.06 + 0.52 * Math.pow(rad, 1.3) + 0.36 * hy));
    const r = Math.abs(Math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453) % 1;
    for (let k = 0; k < 4; k++) { E[(q + k) * 2] = ex; E[(q + k) * 2 + 1] = r; }
  }
  g.setAttribute('aLeafE', new THREE.BufferAttribute(E, 2));
  return g;
}

export function buildEzArchetypes() {
  const t0 = performance.now();
  const arch = {};
  let tris = [0, 0];
  for (const [kind, K] of Object.entries(KINDS)) {
    arch[kind] = [];
    for (const seed of K.seeds) {
      const tree = new Tree();
      tree.options.copy(structuredClone(TreePreset[K.preset]));
      tree.options.seed = seed;
      if (K.leafScale) tree.options.leaves.size *= K.leafScale;
      K.tune?.(tree.options);
      // measure the skeleton (cheap low-detail mesh), then scale to the kind's size: height, and width within reason
      const probe = tree.createGeometry({ sectionStride: 8, segmentFactor: 0.4, leafStride: 4 });
      const bb = new THREE.Box3(); probe.branches.computeBoundingBox(); probe.leaves.computeBoundingBox();
      bb.copy(probe.branches.boundingBox).union(probe.leaves.boundingBox);
      const hgt = bb.max.y - Math.min(0, bb.min.y), wid = Math.max(bb.max.x - bb.min.x, bb.max.z - bb.min.z);
      const sH = K.h / hgt, sW = K.w / wid;
      const s = Math.min(sH * 1.1, Math.max(sH * 0.8, sW)); // favour the crown width, height within +-15 %
      probe.branches.dispose(); probe.leaves.dispose();
      const lods = LODS.map((d) => {
        const g = tree.createGeometry({ ...d, metricUV: BARK_TILE / s });
        for (const x of [g.branches, g.leaves]) { x.scale(s, s, s); x.computeBoundingSphere(); x.computeBoundingBox(); }
        // barkMaterial() multiplies vertex colours: thin twigs (high wind weight) darker, as in shade / against the sky
        const nb = g.branches.attributes.position.count, col = new Float32Array(nb * 3), aw = g.branches.attributes.aWind;
        for (let i = 0; i < nb; i++) col.fill(0.9 - 0.45 * Math.min(1, aw.getX(i) * 1.4), i * 3, i * 3 + 3);
        g.branches.setAttribute('color', new THREE.BufferAttribute(col, 3));
        leafAttrs(g.leaves);
        return g;
      });
      tris[0] += lods[0].branches.index.count / 3 + lods[0].leaves.index.count / 3; tris[1] += lods[1].branches.index.count / 3 + lods[1].leaves.index.count / 3;
      // leaf-cloud lobes (for the far LODs of this kind): from the full-detail leaf quads
      const L = lods[0].leaves.attributes.position, pts = [];
      for (let q = 0; q + 3 < L.count; q += 4) pts.push((L.getX(q) + L.getX(q + 2)) / 2, (L.getY(q) + L.getY(q + 2)) / 2, (L.getZ(q) + L.getZ(q + 2)) / 2);
      arch[kind].push({ seed, scale: s, lods, lobes: fitLobes(pts, kind === 'conifer' ? 5 : kind === 'small' || kind === 'hedge' ? 3 : 5, seed), leaf: K.leaf, height: hgt * s });
    }
  }
  const n = Object.values(arch).reduce((a, v) => a + v.length, 0);
  console.log(`[eztree] ${n} archetypes in ${(performance.now() - t0).toFixed(0)} ms; avg tris L0 ${Math.round(tris[0] / n)}, L1 ${Math.round(tris[1] / n)}`);
  return {
    arch,
    lobes: (kind) => arch[kind]?.[0]?.lobes ?? null,
    attach: (o) => attachEz(arch, o),
  };
}

// ---- materials
let LEAF_TEX = null;
function leafTex(name) {
  LEAF_TEX ??= {};
  if (LEAF_TEX[name]) return LEAF_TEX[name];
  const t = new THREE.TextureLoader().load('/assets/eztree/leaves/' + name + '.png');
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4;
  return (LEAF_TEX[name] = t);
}

function ezLeafMaterial(name, wind) {
  const mat = new THREE.MeshStandardMaterial({ map: leafTex(name), alphaTest: 0.5, side: THREE.DoubleSide, roughness: 0.78 });
  mat.onBeforeCompile = (sh) => {
    sh.uniforms.uLeafFrame = { value: csmShared.params };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>
      attribute vec2 aLeafE; attribute vec3 aTintA; attribute vec3 aTintB; varying vec2 vLeafE; varying vec3 vTA; varying vec3 vTB;`)
      .replace('#include <begin_vertex>', `#include <begin_vertex>
      vLeafE = aLeafE; vTA = aTintA; vTB = aTintB;`);
    // capture the (CSM-shadowed) sun radiance + direction right after the key light (leaf translucency, as trees.js)
    let lf = THREE.ShaderChunk.lights_fragment_begin;
    const k = lf.indexOf('csmShadow()');
    const e = k >= 0 ? lf.indexOf('#endif', k) + 6 : lf.indexOf('getDirectionalLightInfo( directionalLight, directLight );') + 57;
    lf = e > 60 ? lf.slice(0, e) + '\n\tleafSun = directLight.color; leafSunDir = directLight.direction;\n' + lf.slice(e) : lf;
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      varying vec2 vLeafE; varying vec3 vTA; varying vec3 vTB; uniform vec4 uLeafFrame;
      float ezIGN(vec2 p) { return fract(52.9829189 * fract(dot(p, vec2(0.06711056, 0.00583715)))); }`)
      .replace('#include <map_fragment>', `
        vec4 tx = texture2D(map, vMapUv);
        // photo spray -> value + twig mask; recoloured with the instance's autumn tints (trees.js palettes)
        float lum = dot(tx.rgb, vec3(0.3, 0.59, 0.11));
        float twig = 1.0 - smoothstep(-0.03, 0.02, tx.g - max(tx.r, tx.b) - 0.015); // brown stems (not green-dominant)
        float hsel = vLeafE.y * 0.7 + lum * 0.6 - 0.2;
        vec3 leaf = mix(vTA, vTB, smoothstep(0.15, 0.85, hsel));
        float odd = fract(vLeafE.y * 13.7);
        leaf = odd > 0.95 ? vec3(0.13, 0.06, 0.025) : leaf;          // the odd dry brown spray
        leaf *= 0.5 + 1.25 * lum;
        float expo = clamp(vLeafE.x, 0.0, 1.0);
        float occ = mix(0.36, 1.05, pow(expo, 1.3));
        vec3 c = mix(leaf, vec3(0.085, 0.06, 0.042), twig) * occ;
        diffuseColor.rgb *= c;
        diffuseColor.a *= tx.a;
        float leafExpo = expo * (1.0 - twig);`)
      .replace('#include <alphatest_fragment>', `
        { float n = fract(ezIGN(gl_FragCoord.xy + 23.0) + uLeafFrame.x * 2.618034);
          if (diffuseColor.a < mix(0.25, 0.7, n)) discard; diffuseColor.a = 1.0; }`)
      .replace('#include <lights_fragment_begin>', 'vec3 leafSun = vec3(0.0); vec3 leafSunDir = vec3(0.0, 1.0, 0.0);\n' + lf)
      .replace('#include <lights_fragment_end>', `#include <lights_fragment_end>
        { vec3 V = normalize(vViewPosition);
          float thr = pow(clamp(dot(-V, leafSunDir), 0.0, 1.0), 4.0);
          float back = clamp(dot(-normal, leafSunDir), 0.0, 1.0);
          reflectedLight.directDiffuse += diffuseColor.rgb * leafSun * RECIPROCAL_PI * leafExpo * leafExpo * (thr * 2.2 + back * 0.6); }`)
      .replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\ntotalEmissiveRadiance += diffuseColor.rgb * vec3(0.13, 0.1, 0.06) * ambData.vert.x * ambData.bounce.w * leafExpo;');
  };
  mat.customProgramCacheKey = () => 'ez-leaf-v1';
  return applyEzWind(mat, wind, EZ_LEAF_WEIGHT);
}
function ezLeafDepth(name, wind) {
  return applyEzWind(new THREE.MeshDepthMaterial({ map: leafTex(name), alphaTest: 0.5, side: THREE.DoubleSide }), wind, EZ_LEAF_WEIGHT);
}

// ---- pools: per archetype x (bark, leaves) x (L0, L1); items = the kind's items assigned to that archetype
function attachEz(arch, { scene, out, pools, time }) {
  const wind = ezWindUniforms();
  wind.uWindStrength.value.set(0.1, 0, 0.08); // metres at the twig tips (geometry is in metres)
  wind.uWindFrequency.value = 0.9; wind.uWindScale.value = 45;
  const bark = applyEzWind(barkMaterial(), wind, 'aWind');
  const barkDepth = applyEzWind(new THREE.MeshDepthMaterial(), wind, 'aWind');
  const leafMats = {}, leafDepths = {};
  const ezPools = [];
  const hash = (x, z) => Math.abs(Math.sin(x * 12.9898 + z * 78.233) * 43758.5453) % 1;
  for (const [kind, A] of Object.entries(arch)) {
    const src = kind === 'hedge' ? (out.small ?? []).filter(it => it.hedge) : (out[kind] ?? []).filter(it => !it.hedge);
    if (!src.length) continue;
    const groups = A.map(() => []);
    for (const it of src) groups[Math.min(A.length - 1, Math.floor(hash(it.x, it.z) * A.length))].push(it);
    A.forEach((a, v) => {
      const items = groups[v]; if (!items.length) return;
      leafMats[a.leaf] ??= ezLeafMaterial(a.leaf, wind);
      leafDepths[a.leaf] ??= ezLeafDepth(a.leaf, wind);
      const n = items.length;
      a.lods.forEach((g, l) => {
        const range = l === 0 ? { far: EZ.near, shadowFar: EZ.near } : { near: EZ.near, far: EZ.far, shadowFar: EZ.far };
        const cap = Math.min(n, l === 0 ? 160 : 700);
        const pl = new Pool(g.leaves, leafMats[a.leaf], { max: cap, ...range, extra: { aTintA: 3, aTintB: 3 }, name: `ez-${kind}${v}-l${l}-leaves` });
        const pb = new Pool(g.branches, bark, { max: cap, ...range, extra: { aBark: 4 }, name: `ez-${kind}${v}-l${l}-bark` });
        pl.mesh.customDepthMaterial = leafDepths[a.leaf]; pb.mesh.customDepthMaterial = barkDepth;
        for (const p of [pl, pb]) { p.items = items; scene.add(p.mesh); pools.push(p); ezPools.push(p); }
      });
    });
  }
  return { wind, pools: ezPools, update(t) { wind.uTime.value = t; } };
}
