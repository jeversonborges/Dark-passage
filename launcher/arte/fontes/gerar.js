// Gera as peças do launcher: cada elemento [data-peca] de pecas.html vira arte/pecas/<nome>.png (transparente).
// Uso (na raiz do repositório): python3 -m http.server 8767 &  e depois  node launcher/arte/fontes/gerar.js
const path = require('path');
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const SAIDA = path.join(__dirname, '..', 'pecas');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1400, height: 900 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.log('erro:', e.message));
  await p.goto('http://localhost:8767/launcher/arte/fontes/pecas.html');
  await p.waitForFunction(() => document.title === 'ready', null, { timeout: 20000 });
  await p.waitForTimeout(500);
  for (const el of await p.$$('[data-peca]')) {
    const nome = await el.getAttribute('data-peca');
    // recorte em pixels inteiros com o tamanho declarado da peça (element.screenshot arredonda para fora)
    const r = await el.evaluate(e => { const b = e.getBoundingClientRect(); return { x: Math.round(b.x + scrollX), y: Math.round(b.y + scrollY), width: e.offsetWidth, height: e.offsetHeight }; });
    await p.screenshot({ path: path.join(SAIDA, nome + '.png'), omitBackground: true, clip: r, fullPage: true });
    console.log(nome);
  }
  await b.close();
})();
