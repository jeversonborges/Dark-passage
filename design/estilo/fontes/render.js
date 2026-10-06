const { chromium } = require('/opt/node-tools/node_modules/playwright');
const fs = require('fs');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ deviceScaleFactor: 2 });
  const defs = fs.readFileSync('defs.inc', 'utf8');
  for (const n of process.argv.slice(2)) {
    const svg = fs.readFileSync(n + '.svg', 'utf8').replace('@DEFS@', defs);
    fs.writeFileSync('full_' + n + '.svg', svg);
    await p.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await p.locator('svg').screenshot({ path: 'concept_' + n + '.png', omitBackground: true });
  }
  await b.close();
})();
