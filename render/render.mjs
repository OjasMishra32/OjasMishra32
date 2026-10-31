// Usage: node render.mjs <scene> <theme> <width> <height> <frames> <outdir> [data.json]
// Serves this folder over a local HTTP server, opens scenes/<scene>.html in
// headless Chrome, and screenshots one PNG per frame after calling draw(t).
import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import puppeteer from 'puppeteer-core';

const [scene, theme, W, H, N, outdir, dataFile] = process.argv.slice(2);
const root = path.dirname(new URL(import.meta.url).pathname);
const types = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.json': 'application/json', '.jpg': 'image/jpeg', '.png': 'image/png' };
const server = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  if (!p.startsWith(root) || !fs.existsSync(p)) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { 'content-type': types[path.extname(p)] || 'application/octet-stream' });
  fs.createReadStream(p).pipe(res);
}).listen(0);
const port = server.address().port;

fs.mkdirSync(outdir, { recursive: true });
const browser = await puppeteer.launch({
  executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  headless: 'new',
  args: process.platform === 'darwin' ? ['--use-angle=metal', '--ignore-gpu-blocklist'] : ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'],
});
const page = await browser.newPage();
await page.setViewport({ width: +W, height: +H, deviceScaleFactor: 1 });
page.on('console', m => console.log('[page]', m.text()));
page.on('pageerror', e => console.log('[err]', e.message));
await page.goto(`http://127.0.0.1:${port}/scenes/${scene}.html?theme=${theme}&w=${W}&h=${H}`, { waitUntil: 'networkidle0' });
const data = dataFile ? JSON.parse(fs.readFileSync(dataFile, 'utf8')) : null;
await page.evaluate(async (d) => { await window.ready; if (window.setData) await window.setData(d); }, data);
await page.evaluate(() => document.fonts.ready);
for (let i = 0; i < +N; i++) {
  await page.evaluate((t) => window.draw(t), i / +N);
  await page.screenshot({ path: path.join(outdir, `f${String(i).padStart(4, '0')}.png`) });
}
await browser.close();
server.close();
console.log('rendered', N, 'frames to', outdir);
