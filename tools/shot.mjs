// Deterministic screenshot capture for the ?shot= harness (src/shots.js).
//   node tools/shot.mjs riverHigh 'riverHigh&tod=sunset' riverLow eastRiver    -> shots/<name>.png
//   OUT=shots/before node tools/shot.mjs riverHigh                             -> shots/before/riverHigh.png
// Starts its own Vite dev server on a free port (never 5173/5191, used by other sessions) unless URL= is given.
// Uses the installed Google Chrome (playwright-core, no browser download), headless with the GPU on (Metal ANGLE).
import { chromium } from 'playwright-core';
import { createServer } from 'vite';
import fs from 'node:fs';
import path from 'node:path';

const names = process.argv.slice(2);
if (!names.length) { console.error('usage: node tools/shot.mjs <shot[&query]> ...'); process.exit(1); }
const OUT = process.env.OUT || 'shots';
const W = +(process.env.W || 1600), H = +(process.env.H || 900);
fs.mkdirSync(OUT, { recursive: true });

let server = null, base = process.env.URL;
if (!base) {
  server = await createServer({ server: { port: +(process.env.PORT || 5192), strictPort: false, host: '127.0.0.1' }, logLevel: 'error' });
  await server.listen();
  base = server.resolvedUrls.local[0];
}
const browser = await chromium.launch({ channel: 'chrome', headless: true,
  args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--enable-unsafe-swiftshader'] });
try {
  for (const n of names) {
    const page = await browser.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1 });
    const errs = [];
    page.on('pageerror', e => errs.push(e.message));
    page.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
    const t0 = Date.now();
    await page.goto(new URL('?shot=' + n, base).href);
    await page.waitForFunction(() => window.__shotReady === true, null, { timeout: 240000 });
    const file = path.join(OUT, n.replace(/[&=]/g, '_') + '.png');
    await page.screenshot({ path: file });
    const info = await page.evaluate(() => window.__shotInfo);
    console.log(`${file}  ${((Date.now() - t0) / 1000).toFixed(1)}s  ${info}${errs.length ? '  ERRORS: ' + errs.slice(0, 3).join(' | ') : ''}`);
    await page.close();
  }
} finally {
  await browser.close();
  await server?.close();
}
