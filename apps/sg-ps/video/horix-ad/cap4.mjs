import pw from '/opt/node22/lib/node_modules/playwright/index.js'; const { chromium } = pw;
const D = process.cwd() + '/hero', I = process.cwd() + '/img/';
const b = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 }, userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' });
const p = await ctx.newPage();
p.on('pageerror', (e) => console.log('ERR', String(e)));
await p.goto('https://sabergroupacademy.com/horix/?webgl');
await p.waitForTimeout(9000);
await p.mouse.click(1268*2-1920, 506*2); // close toast (approx)
await p.waitForTimeout(500);
const shot = async (n) => { await p.waitForTimeout(400); await p.screenshot({ path: `${D}/${n}.png` }); console.log('shot', n); };
const cmd = async (name, wait=1500) => { await p.keyboard.press('Control+K'); await p.waitForTimeout(500); await p.keyboard.type(name); await p.waitForTimeout(700); await p.keyboard.press('Enter'); await p.waitForTimeout(wait); };
const open = async (f) => { const ch = p.waitForEvent('filechooser', { timeout: 10000 }).catch(() => null); await p.keyboard.press('Control+O'); const fc = await ch; if (fc) await fc.setFiles(I + f); else console.log('no chooser'); await p.waitForTimeout(4500); };
await p.mouse.click(1300, 700);
await shot('10-home');
await open(process.argv[2] || '1500648767791-00dcc994a43e.jpg');
await shot('11-open');
await cmd('Select Subject', 6000);
await shot('12-subject');
await p.keyboard.press('Control+J'); await p.waitForTimeout(1500);
await shot('13-copy');
// hide background layer: alt-click? use command
await p.mouse.click(1610, 464); await p.waitForTimeout(1200);
await p.keyboard.press('Control+D'); await p.waitForTimeout(800);
await shot('14-cutout');
await p.mouse.click(1610, 464); await p.waitForTimeout(800);
await shot('15-both');
await p.mouse.click(1700, 464); await p.waitForTimeout(600);
await p.keyboard.press('Control+U'); await p.waitForTimeout(1500);
await shot('16-hs-open');
const box = await p.evaluate(() => null);
// hue field approx at (567,757)*2 offset quadrant: full coords
await p.mouse.dblclick(1134, 432); await p.waitForTimeout(300);
await p.keyboard.press('Control+A'); await p.keyboard.type('-150'); await p.keyboard.press('Tab'); await p.waitForTimeout(1500);
await shot('17-hs-hue');
await p.keyboard.press('Enter'); await p.waitForTimeout(1500);
await shot('18-final');
await b.close();
