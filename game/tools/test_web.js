// Teste de fumaça do build Web: abre o jogo no Chromium, entra na área inicial, anda, ataca e tira prints.
// Uso: NODE_PATH=$(npm root -g) node tools/test_web.js <url> <pasta_prints> [classe]
const { chromium } = require('playwright');
(async () => {
  const [url, out, classe] = [process.argv[2], process.argv[3], process.argv[4] || 'humano'];
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } });
  const logs = [];
  page.on('console', m => logs.push(m.type() + ': ' + m.text()));
  page.on('pageerror', e => logs.push('pageerror: ' + e.message));
  await page.goto(url);
  await page.waitForTimeout(9000);
  await page.screenshot({ path: `${out}/1_menu.png` });
  await page.mouse.click(640, 284);              // abertura: Jogar sozinho
  await page.waitForTimeout(1500);
  if (classe === 'anjo') { await page.mouse.click(475, 300); await page.waitForTimeout(300); }
  await page.keyboard.press('Enter');          // nome já preenchido: Enter entra
  await page.waitForTimeout(5000);
  await page.waitForTimeout(9000);
  await page.screenshot({ path: `${out}/2_ajuda.png` });
  await page.keyboard.press('h');
  await page.waitForTimeout(500);
  // anda para fora do acampamento em direção aos monstros
  for (let i = 0; i < 6; i++) { await page.mouse.click(900, 330); await page.waitForTimeout(900); }
  await page.screenshot({ path: `${out}/3_andando.png` });
  // procura monstros: clica em vários pontos e usa habilidades
  for (let i = 0; i < 25; i++) {
    await page.mouse.click(640 + Math.round(Math.sin(i) * 120), 330 + Math.round(Math.cos(i) * 60));
    await page.waitForTimeout(400);
    await page.keyboard.press(String(1 + (i % 2)));
    await page.waitForTimeout(400);
  }
  await page.screenshot({ path: `${out}/4_combate.png` });
  await page.keyboard.press('c');
  await page.waitForTimeout(400);
  await page.screenshot({ path: `${out}/5_atributos.png` });
  console.log(logs.filter(l => !l.includes('WebGL') ).slice(-40).join('\n'));
  await browser.close();
})();
