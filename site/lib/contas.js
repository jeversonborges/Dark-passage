'use strict';
// Banco de contas do DARK PASSAGE.
//
// A senha NUNCA chega aqui em texto puro. O navegador (e o cliente do jogo) mandam
// h = sha256("usuario:dark_passage:senha"); aqui esse resumo ganha um sal próprio e passa
// por scrypt antes de ser gravado. Quem roubar o arquivo não consegue voltar à senha.
//
// Guarda tudo num JSON escrito de forma atômica (grava .tmp e renomeia), igual ao servidor
// do jogo faz com o contas.json dele. Para 40 jogadores isso sobra; se um dia crescer,
// trocar este módulo por SQLite não muda a API usada pelo servidor.

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const SCRYPT = { N: 16384, r: 8, p: 1, maxmem: 64 * 1024 * 1024 };
const TAM_CHAVE = 64;
const MAX_PERSONAGENS = 6;

class Contas {
  constructor(arquivo) {
    this.arquivo = arquivo;
    this.dados = { versao: 1, contas: {} };
    this._gravando = null;
    this._sujo = false;
    this._carregar();
  }

  _carregar() {
    fs.mkdirSync(path.dirname(this.arquivo), { recursive: true });
    if (!fs.existsSync(this.arquivo)) return;
    try {
      const d = JSON.parse(fs.readFileSync(this.arquivo, 'utf8'));
      if (d && typeof d === 'object' && d.contas) this.dados = d;
    } catch (e) {
      // Nunca apaga um arquivo que não deu para ler: guarda de lado e começa vazio.
      const backup = this.arquivo + '.ilegivel.' + Date.now();
      fs.renameSync(this.arquivo, backup);
      console.error('contas.json ilegível, guardado em', backup, e.message);
    }
  }

  async _gravar() {
    if (this._gravando) { this._sujo = true; return this._gravando; }
    this._gravando = (async () => {
      do {
        this._sujo = false;
        const tmp = this.arquivo + '.tmp';
        await fs.promises.writeFile(tmp, JSON.stringify(this.dados), { mode: 0o600 });
        await fs.promises.rename(tmp, this.arquivo);
      } while (this._sujo);
      this._gravando = null;
    })();
    return this._gravando;
  }

  static usuarioOk(u) { return typeof u === 'string' && /^[a-z0-9_]{3,16}$/.test(u); }
  static resumoOk(h) { return typeof h === 'string' && /^[0-9a-f]{64}$/.test(h); }

  static _scrypt(h, sal) {
    return new Promise((ok, falha) => {
      crypto.scrypt(h, sal, TAM_CHAVE, SCRYPT, (e, chave) => e ? falha(e) : ok(chave.toString('hex')));
    });
  }

  existe(u) { return Object.prototype.hasOwnProperty.call(this.dados.contas, u); }

  /** Cria a conta. Devolve {ok:false, erro} com texto já pronto para o jogador ler. */
  async criar(u, h, email) {
    if (!Contas.usuarioOk(u)) return { ok: false, erro: 'O usuário precisa ter de 3 a 16 caracteres, usando só letras, números e _.' };
    if (!Contas.resumoOk(h)) return { ok: false, erro: 'Senha inválida.' };
    if (this.existe(u)) return { ok: false, erro: 'Esse usuário já existe. Use Entrar.' };

    const sal = crypto.randomBytes(16).toString('hex');
    this.dados.contas[u] = {
      algo: 'scrypt-16384-8-1',
      sal,
      hash: await Contas._scrypt(h, sal),
      email: email || null,
      criada: new Date().toISOString(),
      ultimo_login: null,
      personagens: []
    };
    await this._gravar();
    return { ok: true, u };
  }

  /** Confere a senha. Leva o mesmo tempo com usuário inexistente, para não entregar quem existe. */
  async autenticar(u, h) {
    if (!Contas.usuarioOk(u) || !Contas.resumoOk(h)) return { ok: false, erro: 'Usuário ou senha errados.' };
    const c = this.dados.contas[u];
    const sal = c ? c.sal : 'isca000000000000isca000000000000';
    const alvo = c ? c.hash : '0'.repeat(TAM_CHAVE * 2);
    const chave = await Contas._scrypt(h, sal);
    const a = Buffer.from(chave, 'hex');
    const b = Buffer.from(alvo, 'hex');
    const bate = a.length === b.length && crypto.timingSafeEqual(a, b);
    if (!c || !bate) return { ok: false, erro: 'Usuário ou senha errados.' };
    c.ultimo_login = new Date().toISOString();
    this._gravar();
    return { ok: true, u, personagens: (c.personagens || []).slice(0, MAX_PERSONAGENS) };
  }

  /** Lista simples para a página da conta (o jogo é quem cria e atualiza os personagens). */
  resumoDaConta(u) {
    const c = this.dados.contas[u];
    if (!c) return null;
    return {
      u,
      criada: c.criada,
      personagens: (c.personagens || []).map(p => ({
        nome: p.nome || '?', classe: p.classe || '', nivel: Number(p.nivel || 1)
      }))
    };
  }

  quantas() { return Object.keys(this.dados.contas).length; }
}

module.exports = { Contas, MAX_PERSONAGENS };
