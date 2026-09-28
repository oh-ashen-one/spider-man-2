// OWNER: destruction (pinata-and-trees). Fracture service: Voronoi fractures (three-pinata) run in a Web Worker
// (fracture.worker.js) and are cached by key, so a crate / hydrant / glass pane is fractured once (at idle time after
// load, or on its first break) and every later break reuses the pieces. Falls back to the main thread when workers
// are unavailable (the same code, imported lazily).
//   fracture(key, src, opts) -> Promise<pieces>   src: { pos, nrm, idx } (model space), opts: see fracture.worker.js
//   cached(key) -> pieces | null                    pieces: [{ pos, nrm, idx, n0, c }]
//   prefetch(list)                                  [[key, src, opts], ...] queued at idle time
let worker = null, seq = 0, broken = false;
const pending = new Map(), cache = new Map(), inflight = new Map();

function getWorker() {
  if (worker || broken) return worker;
  try {
    worker = new Worker(new URL('./fracture.worker.js', import.meta.url), { type: 'module' });
    worker.onmessage = ({ data }) => { const p = pending.get(data.id); if (p) { pending.delete(data.id); p.resolve(data.out); } };
    worker.onerror = (e) => { console.warn('[destruction] fracture worker failed, using the main thread', e.message); broken = true; worker = null; for (const p of pending.values()) p.fallback(); pending.clear(); };
  } catch (e) { broken = true; worker = null; }
  return worker;
}

const copy = (src) => ({ pos: new Float32Array(src.pos), nrm: new Float32Array(src.nrm), idx: new Uint32Array(src.idx) });

async function runMain(jobs) { const m = await import('./fracture.worker.js'); return jobs.map(j => m.fractureJob(j)); }

function run(jobs) {
  const w = getWorker();
  if (!w) return runMain(jobs);
  return new Promise((resolve) => {
    const id = ++seq;
    const clones = jobs.map(j => ({ ...copy(j), opts: j.opts })); // keep the originals for a main-thread fallback
    pending.set(id, { resolve, fallback: () => runMain(jobs).then(resolve) });
    w.postMessage({ id, jobs: clones }, clones.flatMap(j => [j.pos.buffer, j.nrm.buffer, j.idx.buffer]));
  });
}

export function cached(key) { return cache.get(key) ?? null; }

export function fracture(key, src, opts) {
  if (cache.has(key)) return Promise.resolve(cache.get(key));
  if (inflight.has(key)) return inflight.get(key);
  const p = run([{ pos: src.pos, nrm: src.nrm, idx: src.idx, opts }]).then(([r]) => { cache.set(key, r); inflight.delete(key); return r; });
  inflight.set(key, p);
  return p;
}

// idle-time pre-fracture: one job at a time, only while the main thread has spare time
const queue = [];
let pumping = false;
export function prefetch(list) {
  for (const it of list) if (!cache.has(it[0])) queue.push(it);
  if (pumping) return;
  pumping = true;
  const idle = typeof requestIdleCallback === 'function' ? requestIdleCallback : (f) => setTimeout(f, 50);
  const step = () => {
    const it = queue.shift();
    if (!it) { pumping = false; return; }
    fracture(it[0], it[1], it[2]).then(() => idle(step, { timeout: 2000 }));
  };
  idle(step, { timeout: 2000 });
}
