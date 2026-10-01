// In-page collector for the TERRAIN kinds (piece E): park ground, lawns, paths, ponds / Reservoir, park furniture, shoreline pieces that the
// city export (collect_page.js, piece A) does not carry. Installed by tools/export/export_terrain.mjs via page.addScriptTag; exposes
// window.__terrainExport(opts). Everything stays in browser units (metres, +x east, +y up, -z north); meshes are baked to WORLD space, whole (no tiling,
// no region clip: island-wide by construction). Parts are POSTed as binary blobs to the node receiver: [u32 headerLen][header JSON][attr buffers...][index u32].
(() => {
  // ---- which scene meshes are terrain pieces (name -> group). Everything else in the scene is the city / water / far field and stays out.
  const MESHES = [
    // ground surfaces
    [/^park$/, 'ground'], [/^mapLawns$/, 'ground'], [/^coastLawn-/, 'ground'], [/^parkPaths$/, 'ground'], [/^park-drives$/, 'ground'], [/^park-hexpavers$/, 'ground'],
    [/^plazaPaving$/, 'ground'],
    // water bodies (ponds, lake, Reservoir) + their edges
    [/^parkWater$/, 'water'], [/^park-water-shallows$/, 'water'], [/^reservoir-coping$/, 'edge'], [/^reservoir-fence$/, 'furniture'],
    // park furniture / set dressing (vertex coloured)
    [/^park-path-furniture$/, 'furniture'], [/^park-lamps$/, 'furniture'], [/^park-lamp-globes$/, 'furniture'], [/^park-path-globes$/, 'furniture'],
    [/^park-wall-benches$/, 'furniture'], [/^park-ballfield-fences$/, 'furniture'], [/^park-ballfield-posts$/, 'furniture'], [/^park-reeds$/, 'furniture'],
    // shoreline details that are not in the city's far export
    [/^coastPickets-/, 'shore'], [/^wetBands$/, 'shore'],
    // Met-like museum + schist outcrops share one facade-builder mesh: exported whole, the museum triangles are dropped by tools/terrain/prep_terrain.py (rocks only)
    [/^park-setpieces$/, 'setpieces'],
  ];
  // plain InstancedMesh / Pool props that belong to the terrain (positions are the full island list, not the view-dependent near set)
  const INST = /^(parkReeds|park-blankets|parklamp|parklampFar|parkLampPool|ez-(park|elm|conifer)\d-l[01]-(leaves|bark))$/;   // + the park woodland's ez-trees (per-instance autumn tints aTintA / aTintB, LOD0 + LOD1)

  function attrArray(a) {
    const n = a.count, k = a.itemSize, out = new Float32Array(n * k);
    if (!a.isInterleavedBufferAttribute && a.array instanceof Float32Array && !a.normalized) { out.set(a.array.subarray(0, n * k)); return out; }
    for (let i = 0; i < n; i++) for (let j = 0; j < k; j++) out[i * k + j] = a.getComponent ? a.getComponent(i, j) : [a.getX(i), a.getY(i), a.getZ(i), a.getW(i)][j];
    return out;
  }

  // bake a mesh to world space: positions, rotated normals, every other attribute copied; index respects the draw range
  function bake(m) {
    const g = m.geometry, pos = g.attributes.position; if (!pos || pos.count === 0) return null;
    m.updateMatrixWorld(true);
    const M = m.matrixWorld.elements;
    const idxA = g.index ? g.index.array : null, start = g.drawRange.start, cnt = Math.min(g.drawRange.count, (idxA ? idxA.length : pos.count) - start);
    const index = new Uint32Array(cnt);
    for (let i = 0; i < cnt; i++) index[i] = idxA ? idxA[start + i] : start + i;
    const P = attrArray(pos), n = pos.count, W = new Float32Array(n * 3);
    for (let i = 0; i < n; i++) {
      const x = P[i * 3], y = P[i * 3 + 1], z = P[i * 3 + 2];
      W[i * 3] = M[0] * x + M[4] * y + M[8] * z + M[12]; W[i * 3 + 1] = M[1] * x + M[5] * y + M[9] * z + M[13]; W[i * 3 + 2] = M[2] * x + M[6] * y + M[10] * z + M[14];
    }
    const attrs = { position: { k: 3, data: W } };
    for (const [k, a] of Object.entries(g.attributes)) {
      if (k === 'position' || a.isInstancedBufferAttribute) continue;
      const d = attrArray(a);
      if (k === 'normal') for (let i = 0; i < n; i++) {
        const x = d[i * 3], y = d[i * 3 + 1], z = d[i * 3 + 2];
        const X = M[0] * x + M[4] * y + M[8] * z, Y = M[1] * x + M[5] * y + M[9] * z, Z = M[2] * x + M[6] * y + M[10] * z, L = Math.hypot(X, Y, Z) || 1;
        d[i * 3] = X / L; d[i * 3 + 1] = Y / L; d[i * 3 + 2] = Z / L;
      }
      attrs[k] = { k: a.itemSize, data: d };
    }
    return { attrs, index };
  }

  const matInfo = (m) => { const x = Array.isArray(m) ? m[0] : m; return { type: x?.type, color: x?.color?.toArray?.(), roughness: x?.roughness, metalness: x?.metalness, transparent: !!x?.transparent,
    vertexColors: !!x?.vertexColors, map: x?.map?.image?.src ?? null, alphaTest: x?.alphaTest, side: x?.side, emissive: x?.emissive?.toArray?.(), emissiveIntensity: x?.emissiveIntensity }; };

  async function post(url, header, buffers) {
    const hj = new TextEncoder().encode(JSON.stringify(header));
    const pad = (4 - (hj.length % 4)) % 4;
    let total = 4 + hj.length + pad; for (const b of buffers) total += b.byteLength;
    const out = new Uint8Array(total), dv = new DataView(out.buffer);
    dv.setUint32(0, hj.length + pad, true); out.set(hj, 4); out.fill(32, 4 + hj.length, 4 + hj.length + pad);
    let o = 4 + hj.length + pad; for (const b of buffers) { out.set(new Uint8Array(b.buffer, b.byteOffset, b.byteLength), o); o += b.byteLength; }
    const r = await fetch(url, { method: 'POST', body: out.buffer });
    if (!r.ok) throw new Error('post failed ' + r.status);
  }
  async function postMesh(url, name, group, p, extra = {}) {
    const header = { type: 'mesh', name, kind: group, tile: [0, 0], center: [0, 0, 0], attrs: {}, nIndex: p.index.length, ...extra };
    const bufs = [];
    for (const [k, a] of Object.entries(p.attrs)) { header.attrs[k] = { k: a.k, n: a.data.length / a.k }; bufs.push(a.data); }
    bufs.push(p.index);
    await post(url, header, bufs);
  }
  const postJSON = (url, file, data) => post(url + '&file=' + file, { type: 'json', file, data }, []);

  // plain InstancedMesh -> records [x,y,z, ry, sx,sy,sz, r,g,b] (rotation about +y only: CanopyBatch / park blankets)
  function instRecords(m) {
    const a = m.instanceMatrix.array, out = [], col = m.instanceColor?.array;
    for (let i = 0; i < m.count; i++) {
      const e = a.subarray(i * 16, i * 16 + 16);
      const sx = Math.hypot(e[0], e[1], e[2]), sy = Math.hypot(e[4], e[5], e[6]), sz = Math.hypot(e[8], e[9], e[10]);
      const r = [e[12], e[13], e[14], Math.atan2(-e[2] / sx, e[0] / sx), sx, sy, sz];
      if (col) r.push(col[i * 3], col[i * 3 + 1], col[i * 3 + 2]);
      out.push(r.map(v => +v.toFixed(4)));
    }
    return out;
  }

  window.__terrainExport = async (opts) => {
    const { url } = opts, ctx = window.__ctx, scene = ctx.scene, world = ctx.world;
    const log = [], stats = {};
    const L = await import('/src/world/layout.js'), GR = await import('/src/world/ground.js'), TR = await import('/src/world/trees.js'), PK = await import('/src/world/park.js');
    const WF = await import('/src/world/waterfront.js'), GRS = await import('/src/world/grass.js');
    const { G } = L;
    // ---- 1. static meshes
    const used = new Map();
    const all = []; scene.traverse(o => { if (o.isMesh && !o.isInstancedMesh && !o.isSkinnedMesh && o.geometry?.attributes?.position && o.name) all.push(o); });
    for (const m of all) {
      const hit = MESHES.find(([re]) => re.test(m.name)); if (!hit) continue;
      const b = bake(m); if (!b) continue;
      const safe = m.name.replace(/-(?=\d)/g, 'n').replace(/[^A-Za-z0-9_]+/g, '_'), k = (used.get(safe) ?? 0) + 1; used.set(safe, k);
      const name = k > 1 ? safe + '_n' + k : safe;
      await postMesh(url, name, hit[1], b, { src: m.name, mat: matInfo(m.material), lod: false });
      const s = (stats[hit[1]] ||= { meshes: 0, verts: 0, tris: 0 }); s.meshes++; s.verts += b.attrs.position.data.length / 3; s.tris += b.index.length / 3;
    }
    log.push('meshes ' + [...used.keys()].length);
    // ---- 2. instanced props (full island lists). Pools are hooked by the driver (window.__pools); plain InstancedMeshes are read from the scene.
    const instances = {};
    const protoDone = new Set();
    const sendProto = async (name, geo, mat) => {
      if (protoDone.has(name)) return; protoDone.add(name);
      const fake = { geometry: geo, matrixWorld: new ctx.camera.matrixWorld.constructor(), updateMatrixWorld() {} };
      fake.matrixWorld.identity();
      const b = bake(fake); if (!b) return;
      await postMesh(url, name.replace(/-(?=\d)/g, 'n').replace(/[^A-Za-z0-9_]+/g, '_'), 'proto', b, { src: name, proto: true, mat: matInfo(mat) });
    };
    scene.traverse(o => { if (o.isInstancedMesh && INST.test(o.name || '')) (window.__plainInst ||= []).push(o); });
    for (const m of window.__plainInst ?? []) {
      if (instances[m.name]) continue;
      instances[m.name] = { n: m.count, kind: 'matrix', items: instRecords(m) };
      await sendProto(m.name, m.geometry, m.material);
    }
    for (const P of [...(window.__pools ?? [])]) {
      const name = P.mesh?.name || ''; if (!INST.test(name)) continue;
      instances[name] = { near: P.near, far: P.far, n: P.items.length, kind: 'pool', items: P.items.filter(it => !it.hidden).map(it => {
        const o = { x: +it.x.toFixed(3), y: +it.y.toFixed(3), z: +it.z.toFixed(3), ry: +(it.ry || 0).toFixed(4), s: +(it.s ?? 1).toFixed(4) };
        if (it.rx) o.rx = +it.rx.toFixed(4); if (it.rz) o.rz = +it.rz.toFixed(4); if (it.scale3) o.s3 = it.scale3.map(v => +v.toFixed(4));
        if (it.color) o.c = Array.from(it.color).map(v => +v.toFixed(4));
        if (it.extra) { o.e = {}; for (const k in it.extra) o.e[k] = typeof it.extra[k] === 'number' ? it.extra[k] : Array.from(it.extra[k]); }
        return o; }) };
      await sendProto(name, P.geo, P.mat);
    }
    log.push('instances ' + Object.keys(instances).join(','));
    // ---- 3. park grass mask (grass.js parkMask: 1 m texels, R = blade density, G = blade height, 0 on paths / water / rocks / museum lot)
    let mask = null;
    try {
      const gm = scene.getObjectByName('park-grass');
      if (gm) {
        const sh = { uniforms: {}, vertexShader: '#include <common>\n#include <beginnormal_vertex>\n#include <begin_vertex>', fragmentShader: '#include <common>\n#include <color_fragment>\n#include <normal_fragment_begin>' };
        gm.material.onBeforeCompile(sh);
        const tex = sh.uniforms.tMask.value, rect = sh.uniforms.uMask.value;
        const D = tex.image.data;
        await post(url + '&file=parkmask.rgba', { type: 'bin', file: 'parkmask.rgba' }, [new Uint8Array(D.buffer, D.byteOffset, D.byteLength)]);
        mask = { file: 'parkmask.rgba', w: tex.image.width, h: tex.image.height, x0: rect.x, z0: rect.y, texel: 1 };
      }
    } catch (e) { log.push('park mask FAILED ' + e.message); }
    // ---- 4. layout / parameters of the park shaders + checkers
    const pw = L.PARK_WATER.map(w => ({ name: w.name, y: w.y, cx: w.cx, cz: w.cz, rx: w.rx, rz: w.rz, a: w.a, h: w.h ?? [0, 0, 0, 0], q: w.q ?? 0, pts: w.pts }));
    const F = world.getMapFeatures?.() ?? {};
    const data = {
      units: 'metres, browser frame (+x east, +y up, -z north); UE = (x, z, y) * 100',
      G: { PARK: G.PARK, CURB_H: G.CURB_H, WATER_Y: G.WATER_Y, X_MIN: G.X_MIN, X_MAX: G.X_MAX, Z_MIN: G.Z_MIN, Z_MAX: G.Z_MAX },
      GY: GR.GY,
      meadows: TR.PARK_MEADOWS, water: pw, sites: PK.PARK_SITES, rocks: PK.PARK_ROCKS,
      landPoly: L.LAND_POLY, shoreZ: L.SHORE_Z,
      piers: (GR.PIERS || []).map(p => JSON.parse(JSON.stringify(p))), pileFields: GR.PILE_FIELDS,
      coast: { lamps: WF.COAST.lamps?.length ?? 0, benches: WF.COAST.benches?.length ?? 0, trees: WF.COAST.trees?.length ?? 0, stats: WF.COAST.stats ?? null },
      mask, stats, instances,
    };
    await postJSON(url, 'terrain.json', data);
    // paths straight from the ribbon mesh are in parkPaths.glb; the polylines are not exposed by the world object
    log.push('terrain.json');
    return { log, stats, instances: Object.fromEntries(Object.entries(instances).map(([k, v]) => [k, v.n])) };
  };
})();
