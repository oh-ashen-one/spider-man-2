// OWNER: destruction (pinata-and-trees). Entry: initDestruction(ctx) — called from main.js after combat. Wires the
// debris renderer (debris.js) and the breakables (breakables.js) to the game's impacts:
//   - Spidey's hard landings / ground pounds break the street furniture (and dent cars) around him
//   - Spidey barrelling through at speed near the ground knocks props over / apart
//   - enemies sent flying by heavy hits smash the props, glass and cars they crash into
//   - thrown crates / bins shatter on their target; flying throwables break what they pass through
// ctx.destruction = { debris, breakables, breakAt(p, r, o), hitCar(p, r, o) }   (window.__destruct for dev / shots)
// Quality: getQuality().debris (live fragment cap; 0 = destruction off), ?qset=debris:0
import * as THREE from 'three';
import { getQuality } from '../../render/quality.js';
import { createDebris } from './debris.js';
import { createBreakables } from './breakables.js';

const _v = new THREE.Vector3(), _f = new THREE.Vector3();

export function initDestruction(ctx) {
  if (ctx.destruction) return ctx.destruction;
  const Q = getQuality();
  const debris = createDebris(ctx, { max: Q.debris ?? 300 });
  const B = createBreakables(ctx, debris);
  const D = ctx.destruction = {
    debris, breakables: B, enabled: (Q.debris ?? 300) > 0,
    breakAt: (p, r, o) => (D.enabled ? B.breakAt(p, r, o) : 0),
    hitCar: (p, r, o) => (D.enabled ? B.hitCar(p, r, o) : 0),
  };
  window.__destruct = D;
  if (!D.enabled) return D;

  // ground pounds (combat) break things too
  const hookCombat = () => {
    const c = ctx.combat; if (!c || c._destructHook) return;
    c._destructHook = true;
    const gp = c.groundPound;
    c.groundPound = (p) => { gp(p); B.breakAt(p, 3, { power: 7, up: 4 }); B.hitCar(p, 1.2, {}); debris.blast(p, 4, 6); };
  };

  let warmT = 1.5, sweepT = 0;
  ctx.systems.push({
    update(dt) {
      hookCombat();
      if (warmT > 0 && (warmT -= dt) <= 0) B.warm(); // idle-time pre-fracture once the game is running
      const P = ctx.player, W = ctx.world;
      // hard landings
      for (const e of P.traversal?.events ?? []) {
        if (e.type !== 'land' || !(e.severity > 0.4)) continue;
        const feet = _f.copy(P.position); feet.y = W.groundHeight(feet.x, feet.z, feet.y + 0.5);
        const s = e.severity;
        B.breakAt(feet, 1.1 + 2.4 * s, { power: 3 + 7 * s, up: 3 + 4 * s });
        B.hitCar(feet, 0.6 + s, { dir: _v.set(0, -4, 0) });
        debris.blast(feet, 2.5 + 3 * s, 3 + 6 * s);
      }
      // Spidey barrelling through low and fast (dive / low swing / sprint-zip): 20 Hz is plenty
      if ((sweepT -= dt) <= 0) {
        sweepT = 0.05;
        const v = P.velocity, sp = v.length();
        if (sp > 15) {
          const gy = W.groundHeight(P.position.x, P.position.z, P.position.y + 0.5);
          if (P.position.y - gy < 2.4) { _v.copy(P.position); _v.y = gy + 0.6; B.sweep(_v, 0.6, v, { minSpeed: 15 }); if (sp > 22) B.hitCar(P.position, 0.3, { dir: v }); }
        }
      }
      // combat: bodies and throwables in flight
      const c = ctx.combat;
      if (c) {
        for (const e of c.enemies) {
          if (!e.alive && e.state !== 'knock') continue;
          if (e.state !== 'knock' && e.state !== 'air') continue;
          const hs = Math.hypot(e.vel.x, e.vel.z);
          if (hs < 5) continue;
          _v.copy(e.pos); _v.y += 0.7;
          B.sweep(_v, 0.45, e.vel, { minSpeed: 5 });
          if (hs > 7) B.hitCar(_v, 0.35, { dir: e.vel });
        }
        for (const pr of c.props?.list ?? []) {
          if (pr.state !== 'flying') continue;
          B.sweep(pr.pos, 0.35, pr.vel, { minSpeed: 8 });
          B.hitCar(pr.pos, 0.2, { dir: pr.vel });
        }
      }
      debris.update(dt);
      B.update(dt, ctx.camera.position);
    },
  });
  return D;
}
