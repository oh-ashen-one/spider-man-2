// OWNER: traversal engineer. Web-swing flight dynamics: rigid-web velocity projection + artificial tension.
//
// R  = anchor - body            the web vector, from his centre of mass to the anchor on the model (distance + direction)
// R^ = R / |R|                  unit vector along the web, pointing at the anchor
// theta                         angle between the web and straight down (0 at the bottom of the arc):
//                               cos(theta) = (-R^) . (0,-1,0) = R^.y
//
// 1. Velocity projection:  v <- v - (v . R^) R^
//    Removes every radial component: pulling away from the web (v . R^ < 0) or pushing into it (v . R^ > 0). What is
//    left is always perpendicular to the web, so he moves on the circle (a smooth arc) around the anchor.
// 2. Artificial tension:   F_T = m g cos(theta) + m v^2 / |R|     (applied along R^, toward the anchor)
//    m g cos(theta) cancels the part of gravity that pulls along the web, m v^2 / |R| is the centripetal force that
//    bends the path into the circle. The web is rigid: F_T < 0 (above the anchor and slow) pushes him out, so he never
//    falls inside the circle.
//    With gravity added, the net radial acceleration is exactly v^2 / |R| toward the anchor, and the tangential part is
//    gravity's own: a pendulum that keeps its length.
// 3. Constraint: after the position update the body is put back at |R| = rope and the velocity is projected again
//    (removes the small numerical drift of a finite step).
import * as THREE from 'three';

export const WEB_MASS = 80; // kg (cancels out of the motion; only the reported tension in newtons depends on it)

const _r = new THREE.Vector3();

// R^ (unit, body -> anchor) into out; returns |R|
export function webVector(pos, anchor, out) {
  out.copy(anchor).sub(pos);
  const L = out.length();
  if (L > 1e-6) out.divideScalar(L); else out.set(0, 1, 0);
  return L;
}

// v <- v - (v . R^) R^ ; returns the removed radial speed (> 0 pushing into the web, < 0 pulling away from it)
export function projectPerpendicular(vel, rHat) {
  const vr = vel.dot(rHat);
  vel.addScaledVector(rHat, -vr);
  return vr;
}

// F_T = m g cos(theta) + m v^2 / |R|   (newtons; negative = the rigid web pushes)
export function webTension(m, g, cosTheta, v2, Rlen) {
  return m * g * cosTheta + m * v2 / Math.max(Rlen, 1e-3);
}

// Force step for one frame (before the position update): project the velocity perpendicular to the web, then apply
// gravity plus the artificial tension. Mutates vel. Writes {Rlen, cosTheta, tension, radial} into info.
export function applyWebForces(pos, vel, anchor, m, g, h, info) {
  const Rlen = webVector(pos, anchor, _r);
  const radial = projectPerpendicular(vel, _r);
  const cosTheta = _r.y;
  const T = webTension(m, g, cosTheta, vel.lengthSq(), Rlen);
  vel.y -= g * h;
  vel.addScaledVector(_r, (T / m) * h);
  info.Rlen = Rlen; info.cosTheta = cosTheta; info.tension = T; info.radial = radial;
  return info;
}

// Constraint step (after the position update): body back on the sphere of radius `rope` around the anchor, velocity
// projected perpendicular to the new web vector. Mutates pos / vel; returns the radial speed removed.
export function enforceWeb(pos, vel, anchor, rope) {
  _r.copy(pos).sub(anchor);
  const L = _r.length();
  if (L > 1e-6) _r.divideScalar(L); else _r.set(0, -1, 0);
  pos.copy(anchor).addScaledVector(_r, rope);
  return -projectPerpendicular(vel, _r); // _r points away from the anchor here: flip so > 0 = pushing into the web
}
