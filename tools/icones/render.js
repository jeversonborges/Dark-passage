// Renderiza todos os .svg de uma pasta em PNG 4x (transparente). Uso: node render.js <pasta_svg> <pasta_png> [tamanho_svg=64]
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [src, dst, tam] = process.argv.slice(2); const T = parseInt(tam || '64');
  fs.mkdirSync(dst, { recursive: true });
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ deviceScaleFactor: 4, viewport: { width: T, height: T } });
  for (const f of fs.readdirSync(src).filter(f => f.endsWith('.svg'))) {
    await p.setContent(`<html><body style="margin:0;background:transparent">${fs.readFileSync(path.join(src, f), 'utf8')}</body></html>`);
    await p.locator('svg').screenshot({ path: path.join(dst, f.replace('.svg', '.png')), omitBackground: true });
  }
  await b.close();
})();
