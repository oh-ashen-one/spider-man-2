// node --test test/  — web-swing flight dynamics (src/player/traversal/webtension.js)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import { applyWebForces, enforceWeb, webTension, projectPerpendicular, WEB_MASS } from '../src/player/traversal/webtension.js';

const G = 25, m = WEB_MASS;

function simulate({ rope, v0, seconds, h = 1 / 120 }) {
  const anchor = new THREE.Vector3(0, 40, 0);
  const pos = new THREE.Vector3(0, 40 - rope, 0);   // bottom of the arc
  const vel = new THREE.Vector3(v0, 0, 0);
  const info = {}, log = [];
  const E0 = 0.5 * v0 * v0 + G * pos.y;
  for (let t = 0; t < seconds; t += h) {
    applyWebForces(pos, vel, anchor, m, G, h, info);
    pos.addScaledVector(vel, h);
    enforceWeb(pos, vel, anchor, rope);
    log.push({ t, x: pos.x, L: pos.distanceTo(anchor), vr: vel.dot(anchor.clone().sub(pos).normalize()), E: 0.5 * vel.lengthSq() + G * pos.y, T: info.tension });
  }
  return { log, E0 };
}

test('velocity projection strips pulling-away and pushing-in components', () => {
  const r = new THREE.Vector3(0, 1, 0);
  const away = new THREE.Vector3(5, -3, 0); assert.equal(projectPerpendicular(away, r), -3); assert.equal(away.y, 0);
  const into = new THREE.Vector3(5, 4, 0); assert.equal(projectPerpendicular(into, r), 4); assert.equal(into.y, 0);
});

test('tension formula: F = m g cos(theta) + m v^2 / |R|', () => {
  assert.equal(webTension(80, 25, 1, 100, 20), 80 * 25 + 80 * 100 / 20);   // bottom of the arc
  assert.equal(webTension(80, 25, 0, 100, 20), 80 * 100 / 20);             // web horizontal
  assert.ok(webTension(80, 25, -1, 16, 20) < 0);                           // over the top, slow: rigid web pushes
});

test('arc keeps its length and stays perpendicular to the web', () => {
  const { log } = simulate({ rope: 20, v0: 18, seconds: 12 });
  for (const s of log) {
    assert.ok(Math.abs(s.L - 20) < 1e-9, `|R| drifted to ${s.L}`);
    assert.ok(Math.abs(s.vr) < 1e-9, `radial speed ${s.vr}`);
  }
});

test('energy is (nearly) conserved: a smooth circular arc, no web jerks', () => {
  const { log, E0 } = simulate({ rope: 20, v0: 18, seconds: 12 });
  const worst = Math.max(...log.map(s => Math.abs(s.E - E0) / E0));
  assert.ok(worst < 0.02, `energy drift ${(worst * 100).toFixed(2)} %`);
});

test('tension at the bottom matches m g + m v^2 / R', () => {
  const { log } = simulate({ rope: 20, v0: 18, seconds: 0.02 });
  const want = m * G + m * 18 * 18 / 20;
  assert.ok(Math.abs(log[0].T - want) / want < 0.01, `T ${log[0].T} vs ${want}`);
});

test('small swings have the pendulum period 2 pi sqrt(R / g)', () => {
  const rope = 20, { log } = simulate({ rope, v0: 2, seconds: 20, h: 1 / 240 });
  const cross = []; for (let i = 1; i < log.length; i++) if (log[i - 1].x < 0 && log[i].x >= 0) cross.push(log[i].t);
  const period = (cross.at(-1) - cross[0]) / (cross.length - 1);
  const want = 2 * Math.PI * Math.sqrt(rope / G);
  assert.ok(Math.abs(period - want) / want < 0.01, `period ${period} vs ${want}`);
});

test('full loop over the top with a rigid web (never falls inside the circle)', () => {
  const rope = 12, v0 = Math.sqrt(5 * G * rope) * 0.8; // below the rope-loop speed: a real rope would go slack
  const { log } = simulate({ rope, v0, seconds: 4 });
  assert.ok(log.some(s => s.T < 0), 'expected the web to push near the top');
  for (const s of log) assert.ok(Math.abs(s.L - rope) < 1e-9);
});
