// (water-effects) Water spray: splash drops, dense spray and mist as lit, camera-facing sprites.
// Shading follows dgreenheck/tidewater src/fx/Spray.js (MIT): drops are clear water (motion-blurred streaks whose
// opacity keeps their visual weight small), dense spray is white from every side (multiple scattering), mist is a thin
// veil; all of it glows when back-lit by the sun (forward-scattering lobe) and is lit / shadowed by the scene's real sun,
// sky IBL and cascaded shadows (a MeshStandardMaterial with a billboard vertex stage). CPU simulation (a few hundred
// live particles at most): gravity, drag toward still air, growth of spray / mist; drops die in the water and leave a
// little ripple + foam there.
//   spray.emit({kind, x, y, z, vx, vy, vz, size, life})   kind: 0 drop, 1 spray, 2 mist
//   spray.splash(x, y, z, strength, vx, vz)             a body hitting the water (crown of drops, column, mist)
//   spray.update(dt, water)
import * as THREE from 'three';

export const DROP = 0, SPRAY = 1, MIST = 2;
const KIND = {
  drag: [0.25, 1.6, 3.2], grav: [9.81, 7.5, 0.35], grow: [0, 0.55, 0.45], alpha: [0.75, 0.42, 0.2], albedo: [0.62, 0.9, 0.8],
  stretch: [0.045, 0.05, 0],
};

export function createSpray({ scene, max = 2400 }) {
  const g = new THREE.InstancedBufferGeometry();
  const base = new THREE.PlaneGeometry(1, 1);
  g.index = base.index; g.setAttribute('position', base.attributes.position); g.setAttribute('uv', base.attributes.uv);
  g.setAttribute('normal', base.attributes.normal);
  const A = (n, k) => { const a = new THREE.InstancedBufferAttribute(new Float32Array(max * k), k); a.setUsage(THREE.DynamicDrawUsage); g.setAttribute(n, a); return a; };
  const aPos = A('iPos', 3), aVel = A('iVel', 3), aP = A('iP', 4), aS = A('iS', 1); // iP: size, kind, age01, alpha; iS: seed
  g.instanceCount = 0;
  g.boundingSphere = new THREE.Sphere(new THREE.Vector3(), 1e7);
  const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.85, metalness: 0, transparent: true, depthWrite: false });
  mat.defines = { NO_WET: '', NO_SSR: '' };
  mat.onBeforeCompile = (sh) => {
    sh.vertexShader = sh.vertexShader.replace('#include <common>', `#include <common>
      attribute vec3 iPos; attribute vec3 iVel; attribute vec4 iP; attribute float iS; varying vec2 vC; varying vec4 vP; varying float vS;`)
      .replace('#include <begin_vertex>', `
        vec3 camR = vec3(viewMatrix[0][0], viewMatrix[1][0], viewMatrix[2][0]);
        vec3 camU = vec3(viewMatrix[0][1], viewMatrix[1][1], viewMatrix[2][1]);
        // stretch along the screen-space motion (drops read as short streaks, like a real shutter)
        vec3 dv = (viewMatrix * vec4(iVel, 0.0)).xyz;
        float L = length(dv.xy);
        vec2 ax = L > 1e-4 ? dv.xy / L : vec2(1.0, 0.0);
        vec2 ay = vec2(-ax.y, ax.x);
        int kind = int(iP.y + 0.5);
        float st = kind == 0 ? ${KIND.stretch[0]} : (kind == 1 ? ${KIND.stretch[1]} : 0.0);
        float len = iP.x * (1.0 + L * st / max(iP.x, 1e-3));
        vec3 axW = camR * ax.x + camU * ax.y, ayW = camR * ay.x + camU * ay.y;
        vec3 transformed = iPos + axW * position.x * len + ayW * position.y * iP.x;
        vC = uv * 2.0 - 1.0; vP = iP; vS = iS;`)
      .replace('#include <defaultnormal_vertex>', 'vec3 transformedNormal = vec3(0.0, 0.0, 1.0);');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      varying vec2 vC; varying vec4 vP; varying float vS;
      float sHash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float sNoise(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
        return mix(mix(sHash(i), sHash(i + vec2(1, 0)), f.x), mix(sHash(i + vec2(0, 1)), sHash(i + vec2(1, 1)), f.x), f.y); }
      float sprayA; float sprayFwd;`)
      .replace('#include <map_fragment>', `{
        int kind = int(vP.y + 0.5);
        float r = length(vC), age = vP.z;
        float a;
        if (kind == 0) { a = smoothstep(1.0, 0.35, r); diffuseColor.rgb = vec3(${KIND.albedo[0]}); sprayFwd = 1.4; }
        else if (kind == 1) {
          // dense spray: a clump of drops, eroded into strands from the edges as it ages (never cotton wool)
          vec2 q = vC * 2.3 + vec2(vS * 71.0, vS * 13.0);
          float n = sNoise(q) * 0.6 + sNoise(q * 2.7 + 3.1) * 0.4;
          a = smoothstep(1.0, 0.25, r) * smoothstep(0.35 + age * 0.4, 0.62 + age * 0.3, n + (1.0 - r) * 0.3);
          diffuseColor.rgb = vec3(${KIND.albedo[1]}); sprayFwd = 0.6;
        } else {
          vec2 q = vC * 1.6 + vec2(vS * 33.0, vS * 5.0);
          a = exp(-r * r * 2.2) * (0.55 + 0.45 * sNoise(q + age * 0.6));
          diffuseColor.rgb = vec3(${KIND.albedo[2]}); sprayFwd = 1.0;
        }
        a *= vP.w;
        if (a < 0.004) discard;
        sprayA = a;
      }`)
      .replace('#include <normal_fragment_begin>', `#include <normal_fragment_begin>
        normal = normalize(vec3(vC * 0.75, 1.0)); // a rounded clump, lit like a volume`)
      .replace('#include <lights_fragment_begin>', THREE.ShaderChunk.lights_fragment_begin + `
        #if ( NUM_DIR_LIGHTS > 0 )
        {
          // forward scattering: back-lit spray and drops glow (Henyey-Greenstein, g = 0.7)
          float ct = -dot(directLight.direction, geometryViewDir);
          float ph = (1.0 - 0.49) / (4.0 * PI) / pow(max(1.0 + 0.49 - 1.4 * ct, 1e-3), 1.5);
          reflectedLight.directDiffuse += directLight.color * ph * sprayFwd * diffuseColor.rgb * 2.0;
        }
        #endif`)
      .replace('#include <opaque_fragment>', `#include <opaque_fragment>
        gl_FragColor.a = sprayA;`);
  };
  mat.customProgramCacheKey = () => 'water-spray-v1';
  const mesh = new THREE.Mesh(g, mat);
  mesh.name = 'waterSpray'; mesh.frustumCulled = false; mesh.renderOrder = 18; mesh.receiveShadow = true;
  scene.add(mesh);

  const P = []; // {x,y,z,vx,vy,vz,size,kind,age,life,seed}
  const rnd = Math.random;
  const api = {
    mesh, get count() { return P.length; },
    emit(o) { if (P.length >= max) P.shift(); P.push({ age: 0, seed: rnd(), ...o }); },
    splash(x, y, z, strength = 1, vx = 0, vz = 0) {
      const s = Math.max(0.15, Math.min(strength, 1.5));
      // crown: a ring of drops thrown up and out
      const nd = Math.round(90 * s);
      for (let i = 0; i < nd; i++) {
        const a = rnd() * Math.PI * 2, out = 1.5 + rnd() * 4.5 * s, up = 2.5 + rnd() * 7 * s;
        const r0 = 0.3 + rnd() * 0.5;
        api.emit({ kind: DROP, x: x + Math.cos(a) * r0, y: y + 0.05, z: z + Math.sin(a) * r0, vx: Math.cos(a) * out + vx * 0.3, vy: up, vz: Math.sin(a) * out + vz * 0.3,
          size: 0.025 + rnd() * 0.05, life: 3 });
      }
      // the column: dense white spray blooming up out of the hole, and a veil of mist drifting off it
      const ns = Math.round(46 * s);
      for (let i = 0; i < ns; i++) {
        // a column (fast, narrow) and a lower, wider skirt of torn spray
        const col = i % 3 !== 0, a = rnd() * Math.PI * 2, out = col ? rnd() * 1.2 * s : 1.5 + rnd() * 3 * s;
        const r0 = col ? rnd() * 0.5 : 0.6 + rnd() * 0.6;
        api.emit({ kind: SPRAY, x: x + Math.cos(a) * r0, y: y + 0.1, z: z + Math.sin(a) * r0, vx: Math.cos(a) * out + vx * 0.15,
          vy: col ? 5 + rnd() * 9 * s : 2 + rnd() * 4 * s, vz: Math.sin(a) * out + vz * 0.15,
          size: col ? 0.16 + rnd() * 0.3 * s : 0.22 + rnd() * 0.35 * s, life: 0.9 + rnd() * 0.9 });
      }
      for (let i = 0; i < Math.round(8 * s); i++) {
        const a = rnd() * Math.PI * 2;
        api.emit({ kind: MIST, x: x + Math.cos(a) * 0.8, y: y + 0.4 + rnd() * 1.5, z: z + Math.sin(a) * 0.8, vx: Math.cos(a) * 1.2, vy: 0.8 + rnd() * 1.5, vz: Math.sin(a) * 1.2,
          size: 1.2 + rnd() * 1.4 * s, life: 2.2 + rnd() * 1.6 });
      }
    },
    update(dt, water) {
      let n = 0;
      for (let i = 0; i < P.length; i++) {
        const p = P[i];
        p.age += dt;
        if (p.age >= p.life) continue;
        const k = p.kind;
        p.vy -= KIND.grav[k] * dt;
        const d = Math.exp(-KIND.drag[k] * dt); p.vx *= d; p.vz *= d; if (k !== DROP) p.vy *= d;
        p.x += p.vx * dt; p.y += p.vy * dt; p.z += p.vz * dt;
        p.size *= 1 + KIND.grow[k] * dt;
        if (k !== MIST && p.vy < 0 && water) {
          const h = water.heightAt(p.x, p.z);
          if (p.y < h) {
            // back into the water: a tiny ring + a speck of foam where the heavier ones land
            if (water.ripples && (k === SPRAY || rnd() < 0.08)) water.ripples.drop(p.x, p.z, k === SPRAY ? 0.8 : 0.35, k === SPRAY ? -0.03 : -0.012, k === SPRAY ? 0.5 : 0.2);
            continue;
          }
        }
        P[n++] = p;
      }
      P.length = n;
      const pos = aPos.array, vel = aVel.array, pr = aP.array;
      for (let i = 0; i < n; i++) {
        const p = P[i], u = p.age / p.life, k = p.kind;
        pos[i * 3] = p.x; pos[i * 3 + 1] = p.y; pos[i * 3 + 2] = p.z;
        vel[i * 3] = p.vx; vel[i * 3 + 1] = p.vy; vel[i * 3 + 2] = p.vz;
        const fadeIn = k === DROP ? 1 : Math.min(1, p.age / 0.12);
        const fadeOut = 1 - Math.max(0, (u - 0.6) / 0.4);
        aS.array[i] = p.seed;
        pr[i * 4] = p.size; pr[i * 4 + 1] = k; pr[i * 4 + 2] = u; pr[i * 4 + 3] = KIND.alpha[k] * fadeIn * fadeOut * (0.85 + 0.3 * p.seed);
      }
      g.instanceCount = n;
      for (const a of [aPos, aVel, aP, aS]) { a.clearUpdateRanges(); a.addUpdateRange(0, n * a.itemSize); a.needsUpdate = true; }
    },
  };
  return api;
}
