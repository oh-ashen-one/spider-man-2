// OWNER: citylife engineer. Pedestrians + pigeons entry point used by city.js.
//   buildPeds({scene, blocks, parkPaths, props?, traffic?}) -> Promise<{update(dt, camera|cameraPos), crowd, pigeons}>
// The crowd itself lives in npc/crowd.js (Blender-modelled GPU-skinned people), birds in npc/pigeons.js.
import { createCrowd } from './npc/crowd.js';
import { createPigeons } from './npc/pigeons.js';
import { buildRoads } from './npc/roads.js';
import { createCritters } from './npc/fauna.js';
import { loadHQ } from './hqassets.js';

export async function buildPeds({ scene, blocks, parkPaths, props = null, traffic = null }) {
  const roads = traffic?.roads || buildRoads();
  const phase = props?.phase || (() => 2);
  const fauna = await loadHQ('/assets/city/npc/fauna'); // (3d-assets) textured animals: dogs, critters, pigeons, gulls
  let crowd = null;
  try {
    crowd = await createCrowd({ scene, blocks, parkPaths, props, roads, phase, fauna });
  } catch (e) {
    console.warn('[city] crowd assets missing (run tools/blender/city_npc.py)', e);
  }
  const pigeons = createPigeons({ scene, blocks, parkPaths, props, fauna });
  const critters = fauna ? createCritters({ scene, fauna, blocks, parkPaths, props }) : null;
  let cam = null;
  // debug: ?nocrowd / ?nopigeons disable the systems (bisecting perf)
  const q = typeof location !== 'undefined' ? new URLSearchParams(location.search) : new URLSearchParams();
  const noCrowd = q.has('nocrowd'), noPigeons = q.has('nopigeons'), noCritters = q.has('nocritters');
  return {
    crowd, pigeons, critters,
    update(dt, camOrPos) {
      if (camOrPos && camOrPos.isCamera) cam = camOrPos;
      else if (!cam) cam = (typeof window !== 'undefined' && window.__ctx?.camera) || null;
      if (!cam) return;
      if (!noCrowd) crowd?.update(dt, cam);
      if (!noPigeons) pigeons.update(dt, cam);
      if (!noCritters) critters?.update(dt, cam);
    },
  };
}
