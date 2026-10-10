// Gera as peças da tela de abertura: cada [data-peca] de pecas.html vira game/assets/menu/<nome>.png (transparente).
// Uso, na raiz do repositório (game/, assets/, site/):  python3 -m http.server 8768 &  e  node game/fontes/menu/gerar.js
const path = require('path');
const { chromium } = require('playwright');
const SAIDA = path.join(__dirname, '..', '..', 'assets', 'menu');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2000, height: 1200 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.log('erro:', e.message));
  await p.goto('http://localhost:8768/game/fontes/menu/pecas.html');
  await p.waitForFunction(() => document.title === 'ready', null, { timeout: 30000 });
  await p.waitForTimeout(500);
  for (const el of await p.$$('[data-peca]')) {
    const nome = await el.getAttribute('data-peca');
    const r = await el.evaluate(e => { const b = e.getBoundingClientRect(); return { x: Math.round(b.x + scrollX), y: Math.round(b.y + scrollY), width: e.offsetWidth, height: e.offsetHeight }; });
    await p.screenshot({ path: path.join(SAIDA, nome + '.png'), omitBackground: true, clip: r, fullPage: true });
    console.log(nome);
  }
  await b.close();
})();
