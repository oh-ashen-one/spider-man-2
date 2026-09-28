// Frame cost of a ?shot= composition: loads it, lets it settle, then renders N more frames of the frozen composition
// (world + lighting + pipeline, like the shot harness), each followed by a 1-pixel readback that waits for the GPU, and
// reports the median / p95 frame time (CPU submit + GPU, serialised) and the CPU submit time.
//   node tools/perf.mjs riverHigh eastRiver underwater          -> table
//   URL=http://127.0.0.1:5198/ node tools/perf.mjs riverHigh    -> against another checkout's dev server (A/B)
// Headless numbers are for A/B comparison on the same machine only; the 60 fps target is measured on the Mac Studio.
import { chromium } from 'playwright-core';
import { createServer } from 'vite';

const names = process.argv.slice(2);
const N = +(process.env.N || 120);
let server = null, base = process.env.URL;
if (!base) {
  server = await createServer({ server: { port: +(process.env.PORT || 5192), strictPort: false, host: '127.0.0.1' }, logLevel: 'error' });
  await server.listen(); base = server.resolvedUrls.local[0];
}
const browser = await chromium.launch({ channel: 'chrome', headless: true, args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
try {
  for (const n of names) {
    const page = await browser.newPage({ viewport: { width: +(process.env.W || 1600), height: +(process.env.H || 900) } });
    await page.goto(new URL('?shot=' + n, base).href);
    await page.waitForFunction(() => window.__shotReady === true, null, { timeout: 240000 });
    const r = await page.evaluate(async (N) => {
      const ctx = window.__ctx, dt = 1 / 60;
      ctx.pipeline.timings?.(true);
      const gl = ctx.renderer.getContext(), px = new Uint8Array(4);
      const sync = () => { ctx.renderer.setRenderTarget(null); gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px); };
      let cpu = 0; const ft = [];
      sync();
      for (let i = 0; i < N; i++) {
        const t0 = performance.now();
        ctx.world.update(dt, ctx.camera); ctx.lighting.update(ctx.camera); ctx.pipeline.render(dt);
        const t1 = performance.now();
        sync(); // wait for the GPU: frame time = CPU submit + GPU work, serialised
        const t2 = performance.now();
        cpu += t1 - t0; ft.push(t2 - t0);
        await new Promise(r => requestAnimationFrame(r));
      }
      ft.sort((a, b) => a - b);
      return { cpu: cpu / N, med: ft[Math.floor(N / 2)], p95: ft[Math.floor(N * 0.95)], calls: ctx.renderer.info.render.calls, tris: ctx.renderer.info.render.triangles };
    }, N);
    console.log(`${n.padEnd(24)} frame median ${r.med.toFixed(2)} ms  p95 ${r.p95.toFixed(2)} ms  (cpu submit ${r.cpu.toFixed(2)} ms)`);
    await page.close();
  }
} finally { await browser.close(); await server?.close(); }
