# Site darkpassage.com.br: o que a VPS precisa e como o jogo usa as contas

Escrito pela thread "Site do jogo" em 2026-10-06. O código está em `/mnt/project-files/site/`
(prévia publicada para o Jefin aprovar antes de ir ao ar).

Duas partes, para duas threads diferentes:

- **Parte 1** é para quem cuida da VPS (thread "Custo para colocar o jogo online").
- **Parte 2** é para quem cuida de `game/` (thread "Prévia jogável e área inicial").

---

## Parte 1 — Publicar o site na VPS

### O que é

Um servidor Node **sem nenhuma dependência externa** (`node:http`, `node:fs`, `node:crypto`).
Não tem `npm install`, não tem build. São três coisas:

| Caminho | O que é |
|---|---|
| `site/servidor.js` | servidor HTTP: páginas estáticas + API de contas |
| `site/lib/contas.js` | banco de contas (JSON gravado de forma atômica, senha em scrypt) |
| `site/publico/` | a página e as imagens |

### Requisitos

1. **Node 20 ou mais novo** (`apt install -y nodejs` no Ubuntu 24.04/26.04 já serve).
2. **Portas 80 e 443 liberadas no firewall.** Hoje só SSH e 7777 (jogo) estão abertas:

       ufw allow 80/tcp
       ufw allow 443/tcp

3. **DNS**: registro A de `darkpassage.com.br` e de `www` apontando para `213.109.169.186`.
4. **nginx + certbot** na frente, resolvendo HTTPS e repassando para `127.0.0.1:8080`.
   O HTTPS não é opcional: o navegador só deixa o site calcular o resumo da senha
   (`crypto.subtle`) em HTTPS ou em localhost. Sem certificado, o formulário de conta não funciona.

### Onde ficam os dados

**Fora do repositório**, em `/var/lib/darkpassage/`. Assim um `git pull` nunca encosta nas contas.
O repositório tem `site/.gitignore` ignorando `dados/`, mas o caminho de produção é definido pela
variável `DADOS` mesmo.

### Instalação sugerida

A VPS já puxa o repositório com deploy key só-leitura (a thread do servidor usa a branch
`servidor` para o .pck do jogo). O site pode vir do mesmo clone ou de um clone próprio; o que
importa é apontar o systemd para a pasta `site/` da cópia que a VPS tiver, e que a branch usada
contenha o commit do site (hoje na PR #2).

    git clone git@github.com:jeversonborges/Dark-passage.git /opt/dark-passage
    mkdir -p /var/lib/darkpassage /etc/darkpassage

    # chave que o servidor do jogo usa para conferir senhas (ver Parte 2)
    printf 'CHAVE_INTERNA=%s\n' "$(openssl rand -hex 32)" > /etc/darkpassage/site.env
    chmod 600 /etc/darkpassage/site.env

`/etc/systemd/system/darkpassage-site.service` (cópia pronta em `site/implantacao/darkpassage-site.service`):

    [Unit]
    Description=DARK PASSAGE - site e contas
    After=network.target

    [Service]
    Type=simple
    User=darkpassage
    WorkingDirectory=/opt/dark-passage/site
    EnvironmentFile=/etc/darkpassage/site.env
    Environment=PORTA=8080
    Environment=DADOS=/var/lib/darkpassage
    ExecStart=/usr/bin/node /opt/dark-passage/site/servidor.js
    Restart=always
    RestartSec=3
    NoNewPrivileges=true
    PrivateTmp=true
    ProtectSystem=strict
    ProtectHome=true
    ReadWritePaths=/var/lib/darkpassage

    [Install]
    WantedBy=multi-user.target

Depois: `useradd -r -s /usr/sbin/nologin darkpassage`, `chown -R darkpassage /var/lib/darkpassage`,
`systemctl enable --now darkpassage-site`.

nginx (cópia em `site/implantacao/nginx-darkpassage.conf`): server_name
`darkpassage.com.br www.darkpassage.com.br`, `proxy_pass http://127.0.0.1:8080`, e
`certbot --nginx -d darkpassage.com.br -d www.darkpassage.com.br` para o certificado.

### Atualizar o site depois

    cd /opt/dark-passage && git pull && systemctl restart darkpassage-site

Dá para conferir se está de pé com `curl -s localhost:8080/saude`, que responde
`{"ok":true,"contas":N}`.

---

## Parte 2 — Como o jogo usa a conta criada no site

### A regra que não pode mudar

O cliente do jogo já manda a senha resumida (`menu_rede.gd`):

    h = sha256("usuario:dark_passage:senha")

O site calcula **exatamente esse mesmo resumo** no navegador. Então a conta criada no site e a
conta criada no jogo são a mesma coisa, e **nada precisa mudar no cliente**.

O que o site faz a mais: antes de gravar, esse `h` passa por **scrypt** com um sal de 16 bytes por
conta (`N=16384, r=8, p=1`). O arquivo guarda só `{algo, sal, hash}`. Hoje `servidor.gd` usa
4000 voltas de sha256, que é bem mais fraco contra quem rouba o arquivo.

### O que muda em `game/scripts/net/servidor.gd`

Quando o jogo rodar na VPS (modo dedicado), **o site passa a ser o dono das contas** e o servidor
do jogo só confere a senha com ele. Em LAN, no PC de quem hospeda, nada muda: continua o
`contas.json` local de hoje.

Na mensagem `"login"`, trocar a conferência local por uma chamada HTTP local:

    POST http://127.0.0.1:8080/api/interno/autenticar
    X-Chave: <CHAVE_INTERNA>
    Content-Type: application/json

    {"u": "jefin", "h": "<os mesmos 64 hex que o cliente mandou>"}

Respostas:

    200  {"ok": true, "u": "jefin"}
    401  {"ok": false, "erro": "Usuário ou senha errados."}
    403  {"erro": "Acesso negado."}        // chave errada, ou veio de fora da máquina

A rota só aceita conexão de `127.0.0.1` **e** com a chave certa, então não precisa ficar exposta.

Em Godot:

    var req := HTTPRequest.new()
    add_child(req)
    req.request_completed.connect(_conta_conferida.bind(peer))
    req.request("http://127.0.0.1:8080/api/interno/autenticar",
        ["Content-Type: application/json", "X-Chave: " + OS.get_environment("CHAVE_INTERNA")],
        HTTPClient.METHOD_POST, JSON.stringify({"u": u, "h": h}))

Sugestão: uma constante `CONTAS_PELO_SITE := OS.has_environment("CHAVE_INTERNA")`. Com a variável
presente (só na VPS) usa o site; sem ela, usa o `contas.json` local de hoje. Assim a build de LAN
que o Jefin já tem continua funcionando igual.

A rota `"cadastro"` do servidor do jogo pode continuar existindo para LAN. Na VPS, o melhor é
recusar com "Crie sua conta em darkpassage.com.br", para ter um lugar só criando conta.

### Quem guarda os personagens

Os personagens continuam com o servidor do jogo, no `contas.json` dele, indexados pelo mesmo
nome de usuário. O site não mexe neles: ele tem um campo `personagens` vazio por conta, só para
mostrar a lista na página da conta mais tarde, se a thread do jogo quiser escrever ali.

**Nada combinado aqui exige mexer em `game/` agora.** Enquanto a Parte 2 não for feita, o site já
cria contas e o jogo em LAN segue como está.
