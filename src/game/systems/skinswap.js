// OWNER: systems engineer (3d-assets). Whole-mesh suit skins (AI-logo suits, public/assets/skins/*.glb).
// Each skin GLB is written by tools/skinfit/skinfit.py: a Tripo mesh fitted onto the hero's own 58-joint skeleton,
// with the game's joint order and inverse bind matrices copied verbatim. So the skin mesh is bound straight to the
// live `SpiderMan` SkinnedMesh's skeleton: every clip, IK layer and procedural pose drives it unchanged, and the
// original body + lenses are simply hidden while a skin is worn.
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const cache = new Map(); // url -> Promise<{geometry, material}>

function loadSkin(url) {
  if (!cache.has(url)) {
    cache.set(url, new GLTFLoader().loadAsync(url).then(gltf => {
      let src = null;
      gltf.scene.traverse(o => { if (!src && o.isSkinnedMesh) src = o; });
      if (!src) throw new Error('no skinned mesh in ' + url);
      return { geometry: src.geometry, material: src.material, jointNames: src.skeleton.bones.map(b => b.name) };
    }));
  }
  return cache.get(url);
}

export function createSkinSwap(ctx) {
  let worn = null;     // { url, mesh }
  let token = 0;

  function original() {
    const obj = ctx.player?.object; if (!obj) return {};
    let body = null; const lenses = [];
    obj.traverse(o => {
      if (!o.isSkinnedMesh || o.userData.isSuitSkin) return;
      if (o.name === 'SpiderMan' || [].concat(o.material).some(m => m?.name === 'SpiderSuit')) body = o;
      else if (/lens/i.test(o.name) || [].concat(o.material).some(m => /lens/i.test(m?.name || ''))) lenses.push(o);
    });
    return { body, lenses };
  }

  function showOriginal(on) {
    const { body, lenses } = original();
    if (body) body.visible = on;
    for (const l of lenses) l.visible = on;
  }

  function remove() {
    if (worn) { worn.mesh.removeFromParent(); worn = null; }
    showOriginal(true);
  }

  async function wear(url) {
    const my = ++token;
    if (!url) { remove(); return null; }
    if (worn?.url === url) return worn.mesh;
    let data;
    try { data = await loadSkin(url); } catch (e) { console.warn('[skins] failed to load', url, e); return null; }
    if (my !== token) return null;                       // another suit was chosen while this one loaded
    const { body } = original();
    if (!body) { console.warn('[skins] no hero body to bind to'); return null; }
    // same joint order as the hero skeleton (skinfit.py copies it); check by name so a mismatch never mis-skins
    const names = body.skeleton.bones.map(b => b.name);
    if (data.jointNames.length !== names.length || data.jointNames.some((n, i) => n !== names[i])) {
      console.warn('[skins] joint order mismatch, refusing', url); return null;
    }
    if (worn) worn.mesh.removeFromParent();
    const mat = data.material;
    mat.envMapIntensity = [].concat(body.material)[0]?.envMapIntensity ?? mat.envMapIntensity;
    const mesh = new THREE.SkinnedMesh(data.geometry, mat);
    mesh.name = 'SuitSkin'; mesh.userData.isSuitSkin = true;
    mesh.position.copy(body.position); mesh.quaternion.copy(body.quaternion); mesh.scale.copy(body.scale);
    mesh.castShadow = body.castShadow; mesh.receiveShadow = body.receiveShadow;
    mesh.frustumCulled = false; mesh.layers.mask = body.layers.mask; mesh.renderOrder = body.renderOrder;
    mesh.bindMode = body.bindMode;
    mesh.bind(body.skeleton, body.bindMatrix);
    body.parent.add(mesh);
    worn = { url, mesh };
    showOriginal(false);
    try { ctx.renderer?.compileAsync?.(mesh, ctx.camera, ctx.scene); } catch (e) { /* first-frame compile instead */ }
    return mesh;
  }

  return { wear, remove, get worn() { return worn?.url || null; }, preload: url => loadSkin(url).catch(() => null) };
}
