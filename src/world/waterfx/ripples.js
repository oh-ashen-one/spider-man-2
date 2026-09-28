// (water-effects) Interactive ripples: a 2D wave-equation heightfield (Evan Wallace, "WebGL Water" -- the same
// render-to-texture ping-pong idea tidewater uses for its caustics) in a 96 m window that follows the player, snapped to
// its texels so the simulation scrolls without smearing. Splashes, diving and swimming stamp drops into it; the water
// surface (water.js) displaces its near vertices by the height, bends its normals by the height gradient and shows
// the churned foam it carries.
//   texture (RGBA half float): r = height (m), g = vertical velocity, b = foam (0..1, decays over ~6 s)
//   ripples.drop(x, z, radius, strength, foam = 0)   queue a stamp (strength in m, negative = depression)
//   ripples.update(dt, focus)                          fixed 60 Hz steps (<= 3 per frame), window follows `focus`
import * as THREE from 'three';

const N = 256, SIZE = 96, MAXD = 12;

const VERT = /* glsl */`
precision highp float;
in vec3 position;
out vec2 vUv;
void main() { vUv = position.xy * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.0, 1.0); }`;

const FRAG = /* glsl */`
precision highp float;
in vec2 vUv; out vec4 fragColor;
uniform sampler2D tPrev; uniform vec2 uShift; uniform float uTexel;
uniform vec4 uDrops[${MAXD}]; uniform vec4 uDropF[${MAXD}]; uniform int uNDrops; uniform float uK; uniform float uDamp; uniform float uFoamDecay;
vec4 at(vec2 uv) {
  vec2 q = uv + uShift;
  if (q.x < 0.0 || q.y < 0.0 || q.x > 1.0 || q.y > 1.0) return vec4(0.0);
  return texture(tPrev, q);
}
void main() {
  vec4 c = at(vUv);
  float avg = (at(vUv + vec2(uTexel, 0.0)).r + at(vUv - vec2(uTexel, 0.0)).r + at(vUv + vec2(0.0, uTexel)).r + at(vUv - vec2(0.0, uTexel)).r) * 0.25;
  c.g += (avg - c.r) * uK;
  c.g *= uDamp;
  c.r += c.g;
  // churn: fast-moving water keeps / whips up foam, then it slowly dissolves
  c.b = max(c.b * uFoamDecay, min(abs(c.g) * 6.0, 0.6) * step(0.01, abs(c.g)));
  for (int i = 0; i < ${MAXD}; i++) {
    if (i >= uNDrops) break;
    vec4 d = uDrops[i];                     // uv x, uv y, radius (uv), strength (m)
    float x = max(0.0, 1.0 - length(vUv - d.xy) / d.z);
    float k = 0.5 - cos(x * 3.14159265) * 0.5;
    c.r += k * d.w;
    c.b = max(c.b, k * uDropF[i].x);
  }
  // absorbing border: waves leaving the window fade instead of reflecting back
  vec2 e = smoothstep(0.0, 0.06, vUv) * smoothstep(1.0, 0.94, vUv);
  float edge = e.x * e.y;
  c.rg *= mix(0.9, 1.0, edge);
  c.r = clamp(c.r, -1.5, 1.5);
  fragColor = c;
}`;

export function createRipples(renderer) {
  const mk = () => new THREE.WebGLRenderTarget(N, N, { type: THREE.HalfFloatType, format: THREE.RGBAFormat, depthBuffer: false,
    minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, wrapS: THREE.ClampToEdgeWrapping, wrapT: THREE.ClampToEdgeWrapping });
  const rt = [mk(), mk()];
  let cur = 0;
  const drops = Array.from({ length: MAXD }, () => new THREE.Vector4()), dropF = Array.from({ length: MAXD }, () => new THREE.Vector4());
  const mat = new THREE.RawShaderMaterial({
    glslVersion: THREE.GLSL3, vertexShader: VERT, fragmentShader: FRAG, depthTest: false, depthWrite: false,
    uniforms: { tPrev: { value: null }, uShift: { value: new THREE.Vector2() }, uTexel: { value: 1 / N }, uDrops: { value: drops },
      uDropF: { value: dropF }, uNDrops: { value: 0 }, uK: { value: 0.16 }, uDamp: { value: 0.988 }, uFoamDecay: { value: Math.exp(-1 / 60 / 5.5) } },
  });
  const quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), mat); quad.frustumCulled = false;
  const scene = new THREE.Scene(); scene.add(quad);
  const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const texel = SIZE / N;
  const box = new THREE.Vector4(0, 0, SIZE, 0); // x0, z0, size, on
  const queue = [];
  let acc = 0, idle = 1e9, inited = false;
  const clear = () => {
    const prev = renderer.getRenderTarget(), c = new THREE.Color(); renderer.getClearColor(c); const a = renderer.getClearAlpha();
    renderer.setClearColor(0x000000, 0);
    for (const r of rt) { renderer.setRenderTarget(r); renderer.clear(true, false, false); }
    renderer.setRenderTarget(prev); renderer.setClearColor(c, a);
  };
  const api = {
    texture: rt[0].texture, box, size: SIZE,
    get active() { return box.w > 0.5; },
    drop(x, z, radius, strength, foam = 0) { if (queue.length < 64) queue.push({ x, z, radius, strength, foam }); },
    update(dt, focus) {
      if (!inited) { clear(); inited = true; }
      // sleep when nothing happened for a while (the window stays where it is; the water shader skips it)
      if (queue.length) idle = 0; else idle += dt;
      if (idle > 14) { box.w = 0; return; }
      // window centre snapped to the texel grid (integer texel shifts: no resampling blur)
      const cx = Math.round(focus.x / texel) * texel - SIZE / 2, cz = Math.round(focus.z / texel) * texel - SIZE / 2;
      if (box.w < 0.5) { box.x = cx; box.y = cz; box.w = 1; }
      acc = Math.min(acc + dt, 3 / 60);
      const prevRT = renderer.getRenderTarget();
      while (acc >= 1 / 60) {
        acc -= 1 / 60;
        // shift: the new window's texel (0,0) reads the old window at +shift
        mat.uniforms.uShift.value.set((cx - box.x) / SIZE, (cz - box.y) / SIZE);
        box.x = cx; box.y = cz;
        let n = 0;
        while (queue.length && n < MAXD) {
          const d = queue.shift();
          drops[n].set((d.x - box.x) / SIZE, (d.z - box.y) / SIZE, d.radius / SIZE, d.strength);
          dropF[n].set(d.foam, 0, 0, 0); n++;
        }
        mat.uniforms.uNDrops.value = n;
        mat.uniforms.tPrev.value = rt[cur].texture;
        cur ^= 1;
        renderer.setRenderTarget(rt[cur]);
        renderer.render(scene, cam);
      }
      renderer.setRenderTarget(prevRT);
      api.texture = rt[cur].texture;
    },
  };
  return api;
}
