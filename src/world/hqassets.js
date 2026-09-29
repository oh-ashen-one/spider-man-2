// OWNER: 3d-assets. Loader for the textured Tripo asset packs built by tools/critterfit/critterfit.py:
//   /assets/city/props/props_hq.{json,bin} + props_hq_atlas.webp   street props + combat throwables
//   /assets/city/npc/fauna.{json,bin} + fauna_atlas.webp           dogs, cats, rats, squirrels, pigeons, gulls
// Every item: {name, size: [x, y, z] m, lods: [BufferGeometry], pivots?}. Geometry is in the item's local frame: y = 0
// on the ground, centred in x/z, facing +z. Attributes: position, normal, uv (into the shared atlas), plus
//   aPart (float): the partmat.js material part (props), or
//   aRig (vec2): rigid animation part id + weight 0..1 (fauna, see PART in critterfit.py).
// Returns null when the pack is not shipped (or ?nohq): callers keep their procedural fallbacks.
import * as THREE from 'three';
import { PART } from './partmat.js';

export const RIG = { body: 0, head: 1, tail: 2, legFL: 3, legFR: 4, legBL: 5, legBR: 6, wingL: 7, wingR: 8 };
const cache = new Map();

export function loadHQ(path) {
  if (/[?&]nohq/.test(typeof location !== 'undefined' ? location.search : '')) return Promise.resolve(null);
  if (!cache.has(path)) cache.set(path, load(path));
  return cache.get(path);
}

async function load(path) {
  try {
    const meta = await fetch(path + '.json').then(r => r.json());
    if (!meta?.items?.length) return null;
    const dir = path.slice(0, path.lastIndexOf('/') + 1);
    const [bin, atlas] = await Promise.all([
      fetch(path + '.bin').then(r => r.arrayBuffer()),
      new THREE.TextureLoader().loadAsync(dir + meta.atlas + '.webp'),
    ]);
    atlas.flipY = false; atlas.colorSpace = THREE.SRGBColorSpace; atlas.anisotropy = 8; atlas.needsUpdate = true;
    const items = {};
    for (const it of meta.items) {
      const part = PART[it.part] ?? PART.BASE;
      const lods = it.lods.map((L) => {
        const g = new THREE.BufferGeometry();
        g.setAttribute('position', new THREE.BufferAttribute(new Float32Array(bin, L.pos, L.nv * 3), 3));
        g.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(bin, L.nrm, L.nv * 3), 3));
        g.setAttribute('uv', new THREE.BufferAttribute(new Float32Array(bin, L.uv, L.nv * 2), 2));
        if (L.part != null) {
          const p = new Uint8Array(bin, L.part, L.nv), w = new Uint8Array(bin, L.pw, L.nv), rig = new Float32Array(L.nv * 2);
          for (let i = 0; i < L.nv; i++) { rig[i * 2] = p[i]; rig[i * 2 + 1] = w[i] / 255; }
          g.setAttribute('aRig', new THREE.BufferAttribute(rig, 2));
        } else g.setAttribute('aPart', new THREE.BufferAttribute(new Float32Array(L.nv).fill(part), 1));
        g.setIndex(new THREE.BufferAttribute(L.idx32 ? new Uint32Array(bin, L.idx, L.nt * 3) : new Uint16Array(bin, L.idx, L.nt * 3), 1));
        g.computeBoundingBox(); g.computeBoundingSphere();
        return g;
      });
      items[it.name] = { ...it, lods };
    }
    return { meta, atlas, items };
  } catch (e) {
    console.warn('[hq] ' + path + ' not available', e);
    return null;
  }
}

// A plain copy of an item geometry (position / normal / uv / index only): for ordinary meshes built from a geometry
// that an instanced Pool may also use (Pools attach their per-instance attributes to the geometry they draw).
export function bareGeometry(src) {
  const g = new THREE.BufferGeometry();
  for (const k of ['position', 'normal', 'uv']) g.setAttribute(k, src.attributes[k]);
  g.setIndex(src.index);
  g.boundingBox = src.boundingBox; g.boundingSphere = src.boundingSphere;
  return g;
}
