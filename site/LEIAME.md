# Site do DARK PASSAGE

Site do jogo: a lore do mundo e a criação de conta. A conta criada aqui é a mesma que entra no
jogo. Sem framework e sem dependências: só Node e arquivos.

## Rodar aqui

    cd site
    node servidor.js            # http://127.0.0.1:8080

Variáveis: `PORTA` (padrão 8080), `DADOS` (pasta das contas, padrão `./dados`),
`CHAVE_INTERNA` (segredo que o servidor do jogo usa para conferir senhas; sem ela essa rota
fica desligada).

## Arquivos

| Caminho | O que é |
|---|---|
| `publico/index.html` | o site inteiro: HTML, CSS e JS num arquivo só |
| `publico/img/` | recortes das artes do jogo (`assets/personagens`, `assets/ambiente`, `assets/monstros`) |
| `servidor.js` | rotas estáticas, API de contas, limite de tentativas por IP |
| `lib/contas.js` | banco de contas em JSON, senha em scrypt |
| `tools/gerar_previa.py` | gera a versão publicada como Artifact (modo prévia, não grava conta) |
| `implantacao/` | unit do systemd e configuração do nginx para a VPS |

## Senhas

A senha nunca chega ao servidor. O navegador manda
`h = sha256("usuario:dark_passage:senha")` — o mesmo resumo que o cliente do jogo já calcula em
`game/scripts/net/menu_rede.gd`. O servidor grava `scrypt(h, sal)` com um sal de 16 bytes por conta.
Quem copiar o arquivo de contas não volta à senha.

Regras do usuário são as mesmas do servidor do jogo: de 3 a 16 caracteres, só `a-z`, `0-9` e `_`.

## API

| Rota | Corpo | Resposta |
|---|---|---|
| `POST /api/conta/criar` | `{u, h, email?}` | `201 {u}` ou `400 {erro}` |
| `POST /api/conta/entrar` | `{u, h}` | `200 {u, criada, personagens}` ou `401 {erro}` |
| `POST /api/interno/autenticar` | `{u, h}` + cabeçalho `X-Chave` | `200 {ok:true,u}` / `401` / `403` |
| `GET /saude` | — | `200 {ok:true, contas:N}` |

A rota `interno` é para o servidor do jogo e só responde a quem chama de `127.0.0.1` com a chave
certa. O nginx de produção também bloqueia `/api/interno/` vindo de fora.

## Publicar

Como colocar no ar na VPS, abrir as portas e ligar com o servidor do jogo:
`design/online/site-e-contas.md`.
