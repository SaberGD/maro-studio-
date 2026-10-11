// Drives the live HORIX app step by step over HTTP so each capture can be checked before the next.
import pw from '/opt/node22/lib/node_modules/playwright/index.js'; const { chromium } = pw;
import http from 'node:http';
const D = process.cwd() + '/cap/';
const b = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' });
const p = await ctx.newPage();
const log = [];
p.on('pageerror', (e) => log.push('ERR ' + e));
p.on('dialog', (d) => d.dismiss());
await p.goto('https://sabergroupacademy.com/horix/?webgl');
await p.waitForTimeout(10000);
let pendingFiles = null;
p.on('filechooser', async (fc) => { if (pendingFiles) { await fc.setFiles(pendingFiles); pendingFiles = null; } });
async function act(a) {
  const m = p.mouse, kb = p.keyboard;
  switch (a.t) {
    case 'key': await kb.press(a.k); break;
    case 'down': await kb.down(a.k); break;
    case 'up': await kb.up(a.k); break;
    case 'type': await kb.type(a.s, { delay: 30 }); break;
    case 'move': await m.move(a.x, a.y, { steps: a.steps || 1 }); break;
    case 'click': for (const k of a.mods || []) await kb.down(k); await m.click(a.x, a.y, { clickCount: a.n || 1 }); for (const k of a.mods || []) await kb.up(k); break;
    case 'drag': for (const k of a.mods || []) await kb.down(k); await m.move(a.x1, a.y1); await m.down(); await m.move(a.x2, a.y2, { steps: a.steps || 12 }); await m.up(); for (const k of a.mods || []) await kb.up(k); break;
    case 'files': pendingFiles = a.path; break;
    case 'wait': await p.waitForTimeout(a.ms); break;
    case 'shot': await p.waitForTimeout(a.ms ?? 400); await p.screenshot({ path: D + a.name + '.png' }); break;
    case 'reload': await p.reload(); await p.waitForTimeout(10000); break;
  }
}
http.createServer(async (req, res) => {
  let body = ''; req.on('data', (c) => body += c); req.on('end', async () => {
    try { for (const a of JSON.parse(body)) await act(a); res.end(JSON.stringify({ ok: true, log: log.splice(0) })); }
    catch (e) { res.end(JSON.stringify({ ok: false, err: String(e) })); }
  });
}).listen(9333, () => console.log('ready'));
