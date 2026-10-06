const { chromium } = require('/opt/node-tools/node_modules/playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport:{width:1280,height:720}, deviceScaleFactor: +(process.argv[4]||1) });
  p.on('console', m => console.log('console:', m.text())); p.on('pageerror', e => console.log('err:', e.message));
  await p.goto('http://localhost:8765/' + process.argv[2]);
  await p.waitForFunction(() => document.title === 'ready', null, {timeout: 10000});
  await p.waitForTimeout(400);
  await p.screenshot({ path: process.argv[3] });
  await b.close();
})();
