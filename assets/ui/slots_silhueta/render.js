// Renderiza as silhuetas dos slots: SVG 64x64 -> PNG 104 px (Chromium) -> 52 px (render.py).
// Uso: node render.js   (a partir desta pasta; precisa do playwright do /opt/node-tools)
const fs = require('fs');
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 104, height: 104 }, deviceScaleFactor: 1 });
  for (const f of fs.readdirSync('.').filter(n => n.endsWith('.svg'))) {
    const svg = fs.readFileSync(f, 'utf8').replace('<svg ', '<svg width="104" height="104" ');
    await p.setContent(`<html><body style="margin:0;background:transparent"><div style="opacity:0.5;width:104px;height:104px">${svg}</div></body></html>`);
    await p.screenshot({ path: f.replace('.svg', '_104.png'), omitBackground: true, clip: { x: 0, y: 0, width: 104, height: 104 } });
  }
  await b.close();
})();
