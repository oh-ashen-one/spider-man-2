// Studio-only inspection of this task's dedicated desktop Chrome, CDP port 9334.
import { chromium } from 'playwright-core';
import fs from 'node:fs';
const browser = await chromium.connectOverCDP('http://127.0.0.1:9334', { noDefaults: true });
const pages = browser.contexts().flatMap(c => c.pages());
const page = pages.find(p => p.url().startsWith('http://127.0.0.1:5193/'));
if (!page) throw new Error('Task-owned game tab missing');
await page.waitForFunction(() => !!window.__ctx?.player?.rig && !!window.__sys, null, { timeout: 120000, polling: 100 });
const [file, screenshot] = process.argv.slice(2);
if (file) console.log(JSON.stringify(await page.evaluate(fs.readFileSync(file, 'utf8')), null, 2));
if (screenshot) await page.screenshot({path:screenshot});
process.exit(0);
