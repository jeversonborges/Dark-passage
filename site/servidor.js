'use strict';
// Site do DARK PASSAGE: páginas estáticas + API de contas. Sem nenhuma dependência externa.
//
//   node servidor.js                     porta 8080, dados em ./dados
//   PORTA=8080 DADOS=/var/lib/... node servidor.js
//
// Na VPS ele fica atrás do nginx, que resolve HTTPS e repassa para 127.0.0.1:8080.
// O servidor do jogo confere as senhas chamando /api/interno/autenticar com o
// cabeçalho X-Chave igual a CHAVE_INTERNA (só aceita chamada vinda do próprio servidor).

const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const { Contas } = require('./lib/contas.js');

const PORTA = Number(process.env.PORTA || 8080);
const RAIZ = path.join(__dirname, 'publico');
const DADOS = process.env.DADOS || path.join(__dirname, 'dados');
const CHAVE_INTERNA = process.env.CHAVE_INTERNA || '';

const contas = new Contas(path.join(DADOS, 'contas.json'));

// ------------------------------------------------------------------ limite de tentativas
// Janela de 15 min por IP, separada por rota. Segura força bruta sem atrapalhar quem erra a senha.
const tentativas = new Map();
const JANELA = 15 * 60 * 1000;

function demais(ip, rota, limite) {
  const chave = rota + '|' + ip;
  const agora = Date.now();
  const lista = (tentativas.get(chave) || []).filter(t => agora - t < JANELA);
  lista.push(agora);
  tentativas.set(chave, lista);
  return lista.length > limite;
}
setInterval(() => {
  const agora = Date.now();
  for (const [k, v] of tentativas) {
    const vivos = v.filter(t => agora - t < JANELA);
    if (vivos.length) tentativas.set(k, vivos); else tentativas.delete(k);
  }
}, 5 * 60 * 1000).unref();

// ------------------------------------------------------------------ utilidades
const TIPOS = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8',
  '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.webp': 'image/webp', '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
  '.woff2': 'font/woff2', '.zip': 'application/zip'
};

function responder(res, codigo, corpo, cabecalhos = {}) {
  res.writeHead(codigo, {
    'Content-Type': 'application/json; charset=utf-8',
    'X-Content-Type-Options': 'nosniff',
    ...cabecalhos
  });
  res.end(typeof corpo === 'string' ? corpo : JSON.stringify(corpo));
}

function ipDe(req) {
  const enc = req.headers['x-forwarded-for'];
  if (typeof enc === 'string' && enc) return enc.split(',')[0].trim();
  return req.socket.remoteAddress || '?';
}

function lerCorpo(req, limite = 4096) {
  return new Promise((ok, falha) => {
    let bruto = '';
    req.on('data', p => {
      bruto += p;
      if (bruto.length > limite) { falha(new Error('corpo grande demais')); req.destroy(); }
    });
    req.on('end', () => {
      try { ok(bruto ? JSON.parse(bruto) : {}); } catch (e) { falha(new Error('JSON inválido')); }
    });
    req.on('error', falha);
  });
}

// ------------------------------------------------------------------ arquivos estáticos
function servirArquivo(req, res, urlPath) {
  let rel = decodeURIComponent(urlPath.split('?')[0]);
  if (rel.endsWith('/')) rel += 'index.html';
  const destino = path.join(RAIZ, path.normalize(rel));
  if (!destino.startsWith(RAIZ)) return responder(res, 403, { erro: 'Caminho inválido.' });

  fs.stat(destino, (e, st) => {
    if (e || !st.isFile()) {
      // Página desconhecida volta para a home, que é onde está tudo.
      return fs.readFile(path.join(RAIZ, 'index.html'), (e2, html) => {
        if (e2) return responder(res, 404, { erro: 'Não encontrado.' });
        responder(res, 404, html, { 'Content-Type': TIPOS['.html'] });
      });
    }
    const ext = path.extname(destino).toLowerCase();
    const cache = ext === '.html' ? 'no-cache' : 'public, max-age=86400';
    res.writeHead(200, {
      'Content-Type': TIPOS[ext] || 'application/octet-stream',
      'Content-Length': st.size,
      'Cache-Control': cache,
      'X-Content-Type-Options': 'nosniff'
    });
    fs.createReadStream(destino).pipe(res);
  });
}

// ------------------------------------------------------------------ API
async function api(req, res, rota) {
  const ip = ipDe(req);

  if (req.method !== 'POST') return responder(res, 405, { erro: 'Método não permitido.' });

  let corpo;
  try { corpo = await lerCorpo(req); }
  catch { return responder(res, 400, { erro: 'Não consegui ler o pedido.' }); }

  const u = String(corpo.u || '').trim().toLowerCase();
  const h = String(corpo.h || '');

  if (rota === '/api/conta/criar') {
    if (demais(ip, 'criar', 5)) return responder(res, 429, { erro: 'Muitas contas criadas daqui. Tente de novo mais tarde.' });
    const email = corpo.email ? String(corpo.email).trim().slice(0, 120) : null;
    if (email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return responder(res, 400, { erro: 'Esse e-mail não parece válido.' });
    const r = await contas.criar(u, h, email);
    return responder(res, r.ok ? 201 : 400, r.ok ? { u: r.u } : { erro: r.erro });
  }

  if (rota === '/api/conta/entrar') {
    if (demais(ip, 'entrar', 20)) return responder(res, 429, { erro: 'Muitas tentativas. Espere alguns minutos.' });
    const r = await contas.autenticar(u, h);
    if (!r.ok) return responder(res, 401, { erro: r.erro });
    const info = contas.resumoDaConta(u);
    return responder(res, 200, { u: r.u, criada: info.criada, personagens: info.personagens });
  }

  // Só o servidor do jogo, rodando na mesma máquina, pode usar esta rota.
  if (rota === '/api/interno/autenticar') {
    const local = ['127.0.0.1', '::1', '::ffff:127.0.0.1'].includes(req.socket.remoteAddress);
    if (!local || !CHAVE_INTERNA || req.headers['x-chave'] !== CHAVE_INTERNA) {
      return responder(res, 403, { erro: 'Acesso negado.' });
    }
    const r = await contas.autenticar(u, h);
    return responder(res, r.ok ? 200 : 401, r.ok ? { ok: true, u: r.u } : { ok: false, erro: r.erro });
  }

  return responder(res, 404, { erro: 'Rota desconhecida.' });
}

// ------------------------------------------------------------------ servidor
const servidor = http.createServer((req, res) => {
  const rota = (req.url || '/').split('?')[0];
  if (rota === '/saude') return responder(res, 200, { ok: true, contas: contas.quantas() });
  if (rota.startsWith('/api/')) {
    return api(req, res, rota).catch(e => {
      console.error('erro na API', rota, e);
      responder(res, 500, { erro: 'Deu problema aqui no servidor. Tente de novo em instantes.' });
    });
  }
  if (req.method !== 'GET' && req.method !== 'HEAD') return responder(res, 405, { erro: 'Método não permitido.' });
  servirArquivo(req, res, rota);
});

servidor.listen(PORTA, () => {
  console.log('DARK PASSAGE · site em http://127.0.0.1:' + PORTA + ' · ' + contas.quantas() + ' conta(s)');
  if (!CHAVE_INTERNA) console.warn('aviso: CHAVE_INTERNA vazia, a rota /api/interno/autenticar fica desligada.');
});

for (const sinal of ['SIGINT', 'SIGTERM']) {
  process.on(sinal, () => servidor.close(() => process.exit(0)));
}
