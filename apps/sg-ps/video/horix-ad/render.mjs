// Usage: node render.mjs page.html out.mp4 [fps] | node render.mjs page.html --stills t1,t2,...
import pw from '/opt/node22/lib/node_modules/playwright/index.js'; const { chromium } = pw;
import { spawn } from 'node:child_process';
const [page, out, fpsArg, warpFile] = process.argv.slice(2);
const fs = await import('node:fs');
const WARP = warpFile ? JSON.parse(fs.readFileSync(warpFile, 'utf8')) : null;
const b = await chromium.launch({ args: ['--allow-file-access-from-files', '--font-render-hinting=none'] });
const p = await b.newPage({ viewport: { width: +(process.env.VW || 1920), height: +(process.env.VH || 1080) }, deviceScaleFactor: 1 });
p.on('pageerror', e => console.error('pageerror', e));
await p.goto('file://' + process.cwd() + '/' + page);
await p.waitForFunction(() => window.READY === true);
await p.waitForTimeout(500);
if (out === '--stills') {
  for (const t of fpsArg.split(',').map(Number)) {
    await p.evaluate(t => render(t), t);
    await p.screenshot({ path: process.cwd() + '/stills/' + page.replace('.html','') + '-' + t.toFixed(1) + '.png' });
  }
} else {
  const fps = Number(fpsArg || 30);
  if (WARP) await p.evaluate((w) => { window.__warp = (t) => { for (let i = 1; i < w.length; i++) if (t <= w[i][0]) { const a = w[i - 1], b = w[i]; return a[1] + (b[1] - a[1]) * (t - a[0]) / (b[0] - a[0]); } return w[w.length - 1][1]; }; }, WARP);
  const dur = WARP ? WARP[WARP.length - 1][0] : await p.evaluate(() => window.DURATION);
  const n = Math.round(dur * fps);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', process.env.CRF || '18', '-preset', process.env.PRESET || 'medium', '-profile:v', 'high', '-tune', 'film', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => render(window.__warp ? window.__warp(t) : t), i / fps);
    const buf = await p.screenshot(process.env.PNG ? { type: 'png' } : { type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log('frame', i, '/', n);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await b.close();
