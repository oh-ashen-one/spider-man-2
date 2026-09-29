// Night 1 / F3 browser baseline: scripted playtests driven by REAL input events (CDP Input.dispatchKeyEvent /
// dispatchMouseEvent via Playwright keyboard + mouse) in a headless Chrome (new headless, Metal ANGLE, GPU on).
//
//   MODE=film node docs/night1/baseline/tools/playtest.mjs swingChain fight ...   -> clips (frame-stepped, 60 fps game time)
//   MODE=perf W=3840 H=2160 node docs/night1/baseline/tools/playtest.mjs swingChain street   -> real-time frame times
//
// film: ctx.manualStep = true; every frame = input events for that frame -> ctx.stepFrame(1/60) -> CDP JPEG capture piped
//       to ffmpeg. The video therefore plays back at exactly 60 fps of game time regardless of how long each frame took
//       to render and capture (capture is offline, not real time).
// perf: the normal real-time loop (renderer.setAnimationLoop); the same scripts run on wall-clock time while an in-page
//       rAF logger records every frame delta. Chrome is launched with vsync / frame-rate limit off so frames are not
//       quantised to the display.
// Camera turning uses ctx.input.mouse.dx/dy (the pointer-lock path cannot be entered in headless Chrome); every
// other control is a real key / mouse event.
// Needs a Vite dev server of this worktree (URL, default http://127.0.0.1:5201/). Scratch output: SCRATCH dir.
import { chromium } from 'playwright-core';
import { spawn } from 'node:child_process';
import { once } from 'node:events';
import fs from 'node:fs';
import path from 'node:path';

const MODE = process.env.MODE || 'film';
const W = +(process.env.W || 1920), H = +(process.env.H || 1080);
const BASE = process.env.URL || 'http://127.0.0.1:5201/';
const SCRATCH = process.env.SCRATCH || '/Users/midir/sm2-n1/_scratch/baseline';
const OUTDIR = process.env.OUT || 'docs/night1/baseline';
const Q = process.env.Q ? '&q=' + process.env.Q : '';
const names = process.argv.slice(2);
fs.mkdirSync(path.join(SCRATCH, 'raw'), { recursive: true });
fs.mkdirSync(path.join(OUTDIR, 'clips'), { recursive: true });
fs.mkdirSync(path.join(OUTDIR, 'logs'), { recursive: true });
fs.mkdirSync(path.join(OUTDIR, 'perf'), { recursive: true });

const profile = path.join(SCRATCH, `chrome-profile-${process.pid}`);
const browser = await chromium.launchPersistentContext(profile, {
  channel: 'chrome', headless: true, viewport: { width: W, height: H }, deviceScaleFactor: 1,
  args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist', '--disable-frame-rate-limit', '--disable-gpu-vsync',
    '--disable-background-timer-throttling', '--disable-renderer-backgrounding', '--disable-backgrounding-occluded-windows'],
});
const page = browser.pages()[0] || await browser.newPage();
const consoleLog = [];
page.on('console', m => consoleLog.push({ t: Date.now(), type: m.type(), text: m.text().slice(0, 400) }));
page.on('pageerror', e => consoleLog.push({ t: Date.now(), type: 'pageerror', text: String(e.message).slice(0, 400) }));
const cdp = await page.context().newCDPSession(page);

const t0 = Date.now();
await page.goto(BASE + '?playtest=1' + Q + (process.env.EXTRA || ''));
await page.waitForFunction(() => window.__cmb && window.__sys && window.__ctx?.player && window.__ctx.stepFrame, null, { timeout: 300000 });
await page.waitForTimeout(6000); // loading screen out, warmup trickle, streaming settle
console.log(`[pt] game ready in ${((Date.now() - t0) / 1000).toFixed(1)} s (${W}x${H}, mode ${MODE})`);
// hide the controls help (H) for clean footage
const helpVisible = await page.evaluate(() => [...document.querySelectorAll('div')].some(d => d.offsetParent && /^CONTROLS/i.test(d.textContent.trim()) && d.textContent.length < 2000));
if (helpVisible) { await page.keyboard.press('KeyH'); }
await page.mouse.move(W / 2, H / 2);
const renderInfo = await page.evaluate(() => { const C = __ctx, gl = C.renderer.getContext(), e = gl.getExtension('WEBGL_debug_renderer_info');
  return { pixelRatio: C.renderer.getPixelRatio(), drawingBuffer: C.renderer.getDrawingBufferSize(new C.THREE.Vector2()).toArray(), css: [innerWidth, innerHeight],
    gpu: e ? gl.getParameter(e.UNMASKED_RENDERER_WEBGL) : '?', quality: C.lighting.quality?.name, maxTexUnits: gl.getParameter(gl.MAX_TEXTURE_IMAGE_UNITS) }; });
console.log('[pt] render', JSON.stringify(renderInfo));

// ------------------------------------------------------------------------------------------------ scenario API
function makeApi(name) {
  const st = { frame: 0, log: [], marks: [], ff: null, done: null, rawPath: null, perFrame: null };
  const api = {
    name, W, H, MODE,
    ev: (fn, arg) => page.evaluate(fn, arg),
    down: k => page.keyboard.down(k), up: k => page.keyboard.up(k),
    tap: async k => { await page.keyboard.down(k); await api.sec(1 / 30); await page.keyboard.up(k); },
    mdown: (b = 'right') => page.mouse.down({ button: b }), mup: (b = 'right') => page.mouse.up({ button: b }),
    click: async (b = 'left') => { await page.mouse.down({ button: b }); await api.sec(1 / 20); await page.mouse.up({ button: b }); },
    look: (dx, dy = 0) => page.evaluate(([dx, dy]) => { __ctx.input.mouse.dx += dx; __ctx.input.mouse.dy += dy; }, [dx, dy]),
    mark: label => { st.marks.push({ t: +(st.frame / 60).toFixed(2), label }); console.log(`  [${name} ${(st.frame / 60).toFixed(2)}s] ${label}`); },
    get t() { return st.frame / 60; },
    state: () => page.evaluate(() => { const C = __ctx, p = C.player, v = p.velocity; const pt = window.__ptState?.() || {};
      return { pos: p.position.toArray().map(x => +x.toFixed(1)), spd: +v.length().toFixed(1), mode: p.mode, sub: pt.sub, trick: pt.trick, node: pt.node, clip: pt.aClip, cmb: pt.cmb ? `${pt.cmb.move} hp${pt.cmb.hp} c${pt.cmb.combo} ${pt.cmb.enemies}` : '', suit: pt.sys?.suit }; }),
    // advance t seconds of game time; fn(i) runs before each frame (film) / each ~16 ms (perf)
    async sec(t, fn = null) {
      const n = Math.max(1, Math.round(t * 60));
      for (let i = 0; i < n; i++) {
        if (fn) await fn(i);
        if (st.perFrame) await st.perFrame(st.frame);
        if (MODE === 'film') {
          await page.evaluate(() => __ctx.stepFrame(1 / 60));
          if (st.ff) {
            const f = await cdp.send('Page.captureScreenshot', { format: 'jpeg', quality: 92 });
            if (!st.ff.stdin.write(Buffer.from(f.data, 'base64'))) await once(st.ff.stdin, 'drain');
          }
        } else await page.waitForTimeout(1000 / 60);
        if (st.frame % 15 === 0) st.log.push({ t: +(st.frame / 60).toFixed(2), ...(await api.state()) });
        st.frame++;
      }
    },
    everyFrame(fn) { st.perFrame = fn; },
    async until(pred, max = 5, fn = null) { const end = st.frame + max * 60; while (st.frame < end) { await api.sec(1 / 60, fn); if (await page.evaluate(pred)) return true; } return false; },
    teleport: (x, z, y = null, yaw = Math.PI) => page.evaluate(([x, z, y, yaw]) => { const C = __ctx; const gy = C.world.groundHeight(x, z, y ?? 999);
      C.player.teleport(new C.THREE.Vector3(x, y ?? gy + 1.0, z), yaw); }, [x, z, y, yaw]),
  };
  return { api, st };
}

// ------------------------------------------------------------------------------------------------ scenarios
const SPAWN = [250, 167.3];
const S = {};
async function reset(a, x = SPAWN[0], z = SPAWN[1], yaw = Math.PI) {
  await page.keyboard.up('KeyW'); await page.mouse.up({ button: 'right' });
  await a.ev(() => { __cmb.debug.end?.(); __ctx.input.releaseAll(); });
  await a.teleport(x, z, null, yaw); await a.sec(1.0);
}
async function swingChain(a, n, { hold = 1.25, gap = 0.3, spaceRel = false, yawFn = null } = {}) {
  for (let k = 0; k < n; k++) {
    await a.mdown('right'); await a.sec(hold, yawFn);
    if (spaceRel) await a.down('Space');
    await a.mup('right'); await a.sec(gap, yawFn);
    if (spaceRel) await a.up('Space');
  }
}

// (a) 20 s street-canyon swing chain at speed down the avenue from the spawn
S.swingChain = async a => {
  await reset(a);
  await a.mark('start: W held, jump, then RMB swing chain down the avenue');
  await a.down('KeyW'); await a.tap('Space'); await a.sec(0.35);
  await swingChain(a, 12, { hold: 1.2, gap: 0.35 });
  await a.mark('chain end');
  await a.sec(1.0); await a.up('KeyW'); await a.sec(1.0);
};
// (b) swing, Space-release (trick), dive (C held), web-zip (E) to a targeted rooftop point
S.trickZip = async a => {
  await reset(a);
  await a.down('KeyW'); await a.tap('Space'); await a.sec(0.35);
  await swingChain(a, 3, { hold: 1.2, gap: 0.35 });
  await a.mark('swing then Space-release');
  await a.mdown('right'); await a.sec(1.2); await a.down('Space'); await a.mup('right'); await a.sec(0.3); await a.up('Space');
  await a.sec(0.9);
  await a.mark('dive (C held)'); await a.down('KeyC'); await a.sec(1.0); await a.up('KeyC');
  await a.mark('look up + E web-zip to a point');
  await a.sec(0.5, () => a.look(0, -18));
  await a.tap('KeyE'); await a.sec(2.5);
  await a.up('KeyW');
  await a.mark('after zip (expect perch)'); await a.sec(2.0);
};
// (c) wall-run up a skyscraper (Shift + W into the facade), wall zips (E), top-out and perch
S.wallRun = async a => {
  await reset(a);
  // (__cmb.debug.nearWall picked a parked vehicle / low obstacle in the first take) -> find a real tower facade: ray at
  // 30 m height from the avenue, facade whose roof is > 90 m, stand 6 m in front of it facing it
  const w = await a.ev(() => {
    const C = __ctx, V = (x, y, z) => new C.THREE.Vector3(x, y, z); let best = null;
    for (const [ox, oz] of [[250, 120], [250, 60], [250, 0], [250, -60], [250, 200]]) for (let i = 0; i < 16; i++) {
      const a = i / 16 * Math.PI * 2, d = V(Math.sin(a), 0, Math.cos(a)); const h = C.world.raycast(V(ox, 30, oz), d, 60);
      if (!h || Math.abs(h.normal.y) > 0.2) continue;
      const top = C.world.raycast(V(h.point.x - h.normal.x, 900, h.point.z - h.normal.z), V(0, -1, 0), 900); const roof = top ? top.point.y : 0;
      if (roof > 90 && (!best || roof > best.roof)) best = { p: h.point.clone(), n: h.normal.clone().setY(0).normalize(), roof };
    }
    if (!best) return null;
    const q = best.p.clone().addScaledVector(best.n, 6); q.y = C.world.groundHeight(q.x, q.z, 5) + 1.0;
    C.player.teleport(q, Math.atan2(-best.n.x, -best.n.z)); return { at: [+q.x.toFixed(1), +q.z.toFixed(1)], roof: Math.round(best.roof) };
  });
  a.mark('tower facade ' + JSON.stringify(w));
  await a.sec(0.8);
  await a.mark('Shift+W into the facade'); await a.down('ShiftLeft'); await a.down('KeyW');
  await a.sec(4.0);
  await a.mark('E: wall zip up'); await a.tap('KeyE'); await a.sec(2.0); await a.tap('KeyE'); await a.sec(2.0); await a.tap('KeyE'); await a.sec(3.0);
  await a.up('ShiftLeft'); await a.up('KeyW');
  await a.mark('released: expect perch / top'); await a.sec(3.0);
};
// (d) ground run through a street with crowd / traffic
S.street = async a => {
  await reset(a, 262, 150, Math.PI);
  await a.mark('run W down the east sidewalk'); await a.down('KeyW');
  await a.sec(5.0);
  await a.mark('Shift parkour run'); await a.down('ShiftLeft'); await a.sec(5.0, i => i % 2 ? null : a.look(i < 60 ? 3 : -3, 0));
  await a.up('ShiftLeft'); await a.sec(3.0); await a.up('KeyW'); await a.sec(1.0);
};
// (e) street fight: spawned thugs, combos, dodge, web shooter, web strike, finisher
S.fight = async a => {
  await reset(a, 250, 120, Math.PI);
  const r = await a.ev(() => __cmb.debug.fight('mmgb', 8)); a.mark('fight spawned: ' + r);
  await a.sec(1.0);
  for (let round = 0; round < 3; round++) {
    await a.mark(`round ${round}: approach + 4-hit combo`);
    await a.down('KeyW'); await a.sec(0.4); await a.up('KeyW');
    for (let k = 0; k < 4; k++) { await a.click('left'); await a.sec(0.28); }
    await a.mark('dodge (Space)'); await a.tap('Space'); await a.sec(0.6);
    await a.mark('web shooter (F) x2'); await a.tap('KeyF'); await a.sec(0.4); await a.tap('KeyF'); await a.sec(0.5);
    await a.mark('launcher (LMB held)'); await a.mdown('left'); await a.sec(0.45); await a.mup('left'); await a.sec(0.4);
    for (let k = 0; k < 3; k++) { await a.click('left'); await a.sec(0.28); }
    await a.mark('web strike (E)'); await a.tap('KeyE'); await a.sec(0.8);
    await a.mark('finisher (Q)'); await a.tap('KeyQ'); await a.sec(1.2);
  }
  await a.sec(2.0);
};
// (f) water: swing out along the Hudson seawall, drop toward / into the river
S.water = async a => {
  const p = await a.ev(() => { const C = __ctx; return null; });
  // Hudson promenade near z = -440 (splash shot), facing south along the shore
  await reset(a, -1, -440, 0);
  const pos = await a.ev(() => { const C = __ctx; let x = -700; for (let xx = -900; xx < 200; xx += 2) if (C.world.groundHeight(xx, -440, 5) > -0.5) { x = xx; break; } return x; });
  await a.teleport(pos + 6, -440, null, -Math.PI / 2); await a.sec(1.0);
  await a.mark(`seawall at x=${pos}: run W west into the river`);
  await a.down('KeyW'); await a.sec(3.5);
  await a.mark('in / over water'); await a.sec(3.0);
  await a.mark('jump + swing attempt over the river'); await a.tap('Space'); await a.mdown('right'); await a.sec(1.5); await a.mup('right'); await a.sec(3.0);
  await a.up('KeyW'); await a.sec(1.0);
};
// (g) each suit worn while swinging (3 s each)
S.skins = async a => {
  await reset(a);
  await a.down('KeyW'); await a.tap('Space'); await a.sec(0.35);
  for (const id of ['advanced', 'iron', 'symbiote', 'claude', 'codex', 'gemini', 'kimi', 'qwen']) {
    await a.ev(id => __sys.debug.suit(id), id); a.mark('suit ' + id);
    await swingChain(a, 2, { hold: 1.15, gap: 0.35 });
  }
  await a.up('KeyW'); await a.sec(1.0);
};
// (h) citizens + animals up close: walk the busy sidewalk near the spawn, orbit the camera slowly
S.crowd = async a => {
  await reset(a, 262.5, 172, Math.PI);
  await a.mark('slow sidewalk run past citizens / dog walkers, camera swinging side to side');
  await a.down('KeyW');
  await a.sec(9.0, i => a.look(Math.sin(i / 40) * 6, 0));
  await a.up('KeyW'); await a.mark('stand + orbit'); await a.sec(4.0, () => a.look(8, 0));
};

// ------------------------------------------------------------------------------------------------ run
const summary = [];
for (const name of names) {
  const fn = S[name]; if (!fn) { console.error('unknown scenario', name); continue; }
  const { api, st } = makeApi(name);
  const tag = `${name}_${W}x${H}`;
  let perfHandle = null;
  if (MODE === 'film') {
    await page.evaluate(() => { __ctx.manualStep = true; });
    st.rawPath = path.join(SCRATCH, 'raw', `${tag}.mp4`);
    st.ff = spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-framerate', '60', '-i', 'pipe:0',
      '-an', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', st.rawPath], { stdio: ['pipe', 'ignore', 'inherit'] });
    st.done = once(st.ff, 'close');
  } else {
    await page.evaluate(() => { __ctx.manualStep = false; window.__ft = []; let last = performance.now();
      const f = now => { window.__ft.push(now - last); last = now; if (!window.__ftStop) requestAnimationFrame(f); }; window.__ftStop = false; requestAnimationFrame(f); });
  }
  const c0 = consoleLog.length, w0 = Date.now();
  try { await fn(api); } catch (e) { console.error(`[pt] ${name} failed:`, e.message); api.mark('SCRIPT ERROR ' + e.message); }
  const wall = (Date.now() - w0) / 1000;
  const errs = consoleLog.slice(c0).filter(m => m.type === 'error' || m.type === 'pageerror' || m.type === 'warning');
  const counts = {}; for (const m of errs) { const k = m.type + ': ' + m.text.slice(0, 160); counts[k] = (counts[k] || 0) + 1; }
  const rec = { name, mode: MODE, W, H, render: renderInfo, gameSeconds: +(st.frame / 60).toFixed(2), wallSeconds: +wall.toFixed(1), marks: st.marks, console: counts, log: st.log };
  if (MODE === 'film') {
    st.ff.stdin.end(); await st.done;
    // committed copy: h264, <= ~14 MB (CRF 21 capped by a bitrate that fits the clip length)
    const dur = st.frame / 60, kbps = Math.floor(Math.min(12000, (13.5 * 8 * 1024) / Math.max(dur, 1)));
    const out = path.join(OUTDIR, 'clips', `${name}.mp4`);
    await once(spawn('ffmpeg', ['-hide_banner', '-loglevel', 'error', '-y', '-i', st.rawPath, '-c:v', 'libx264', '-preset', 'slow', '-crf', '21',
      '-maxrate', `${kbps}k`, '-bufsize', `${kbps}k`, '-pix_fmt', 'yuv420p', '-movflags', '+faststart', out], { stdio: 'inherit' }), 'close');
    rec.clip = out; rec.clipMB = +(fs.statSync(out).size / 1048576).toFixed(2); rec.captureFps = '60 (frame-stepped game time, 1/60 s per frame)';
    await page.evaluate(() => { __ctx.manualStep = false; });
    fs.writeFileSync(path.join(OUTDIR, 'logs', `${name}.json`), JSON.stringify(rec, null, 1));
  } else {
    const ft = await page.evaluate(() => { window.__ftStop = true; return window.__ft; });
    ft.shift(); const s = [...ft].sort((x, y) => x - y), pc = p => s[Math.min(s.length - 1, Math.floor(s.length * p))];
    const stats = { frames: ft.length, avg: +(ft.reduce((x, y) => x + y, 0) / ft.length).toFixed(2), median: +pc(0.5).toFixed(2), p95: +pc(0.95).toFixed(2), p99: +pc(0.99).toFixed(2), max: +s[s.length - 1].toFixed(1),
      hitches33: ft.filter(x => x > 33.4).length, hitches50: ft.filter(x => x > 50).length, fps: +(1000 / (ft.reduce((x, y) => x + y, 0) / ft.length)).toFixed(1) };
    rec.frameTimes = stats; rec.gpu = await page.evaluate(() => { const i = __ctx.renderer.info.render; return { calls: i.calls, tris: i.triangles }; });
    fs.writeFileSync(path.join(OUTDIR, 'perf', `${tag}.json`), JSON.stringify({ ...rec, log: undefined, rawFrameTimes: ft.map(x => +x.toFixed(2)) }));
    console.log(`[perf] ${tag}: ${JSON.stringify(stats)}`);
  }
  summary.push({ name, clipMB: rec.clipMB, game: rec.gameSeconds, wall: rec.wallSeconds, errs: Object.keys(counts).length, ...(rec.frameTimes || {}) });
  console.log(`[pt] ${name} done: ${rec.gameSeconds}s game / ${rec.wallSeconds}s wall`, Object.keys(counts).length ? 'console: ' + JSON.stringify(counts).slice(0, 600) : '');
}
console.table(summary);
fs.writeFileSync(path.join(SCRATCH, `console_${MODE}_${W}x${H}_${process.pid}.json`), JSON.stringify(consoleLog, null, 0));
await browser.close();
fs.rmSync(profile, { recursive: true, force: true });
