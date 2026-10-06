// uso: node shot.js pagina.html saida.png [escala]  -> página inteira
//      node shot.js pagina.html --pecas dir [escala]  -> cada .peca vira dir/<id>.png (fundo transparente)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const [pg, out, a3, a4] = process.argv.slice(2);
  const pecas = out === '--pecas';
  const scale = +(pecas ? a4 : a3) || 1;
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const vp = pecas ? {width:1400,height:900} : {width:1280,height:720};
  const p = await b.newPage({ viewport:vp, deviceScaleFactor: scale });
  p.on('pageerror', e => console.log('err:', e.message));
  p.on('console', m => { if (m.type()==='error') console.log('console:', m.text()); });
  await p.goto('http://localhost:8766/' + pg);
  await p.waitForFunction(() => document.title === 'ready', null, {timeout: 20000});
  await p.waitForFunction(() => [...document.images].every(i => i.complete), null, {timeout: 20000});
  await p.waitForTimeout(500);
  if (pecas) {
    const fs = require('fs'); fs.mkdirSync(a3, {recursive:true});
    const ids = await p.$$eval('.peca', els => els.map(e => e.id));
    for (const id of ids) await p.locator('#' + id).screenshot({ path: `${a3}/${id}.png`, omitBackground: true });
    console.log(ids.length, 'pecas');
  } else await p.screenshot({ path: out, fullPage: true });
  await b.close();
})();
