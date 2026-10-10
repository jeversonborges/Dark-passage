# Servidor dedicado online — plano (para a thread "Prévia jogável")

VPS: MagnoHost São Paulo, 2 vCPU / 4 GB, Ubuntu 26.04, IP 213.109.169.186, domínio darkpassage.com.br.
Meta do Jefin: 40 jogadores ao mesmo tempo. Preparação da máquina: `preparar_vps.sh` (firewall 22/tcp, 80+443/tcp, 7777/udp, fail2ban, usuário `dark`, chave de deploy só leitura do GitHub).

## Como a VPS recebe o jogo
A nuvem do Claude não alcança SSH (só HTTPS). Então a VPS puxa sozinha:
- Branch `servidor` do repositório guarda só `servidor/DarkPassage-servidor.pck` (export "Servidor Linux", dedicated_server=true, texturas/áudio removidos) e `servidor/VERSAO`.
- `instalar_servidor.sh` (rodado na VPS, pode repetir) baixa o Godot 4.4.1 linux, clona o branch `servidor` em /home/dark/jogo e o `main` em /opt/dark-passage (site), instala nginx + certbot (HTTPS só quando o DNS já aponta), e liga `darkpassage` (jogo), `darkpassage-site` (Node, 127.0.0.1:8080) e `darkpassage-atualizar.timer` (a cada 2 min puxa as duas cópias, reinicia o que mudou e liga o serviço quando o arquivo dele aparecer) + backup diário de contas e personagens (14 dias).
- Publicar uma versão = exportar o .pck e dar push no branch `servidor`.

O modo sem tela já existe (`main.gd`: `-- servidor=1 porta=7777`), então o comando é
`godot --headless --main-pack DarkPassage-servidor.pck -- servidor=1`.

## Mudanças no código do jogo (dono: Prévia jogável)
1. `rede.gd:18` — `create_server(porta, 16)` → limite configurável, padrão 48 (`-- max=48`).
2. `export_presets.cfg` — preset novo "Servidor Linux" (Linux, x86_64, `dedicated_server=true`, embed_pck=false, export_path `build/servidor/DarkPassage-servidor.pck`).
3. Menu de abertura — botão "Jogar online" conectando em `darkpassage.com.br:7777`; o campo de IP continua para rede local.
4. Versão — cliente manda `"v"` no login; servidor recusa versão diferente com "Atualize o jogo".
5. Proteção de login — por peer e por IP: 5 erros → bloqueia 60 s; o hash de 4000 rodadas só roda depois desse filtro.
6. Limite de mensagens — mais de ~60 mensagens/s de um peer, ou pacote acima de 64 KB descomprimido (hoje aceita até 16 MB em `rede.gd` `_dec`), derruba a conexão.
7. Criptografia — hoje o sha256(usuário+senha) viaja aberto e vale como senha. Ligar DTLS no ENet: servidor `dtls_server_setup(TLSOptions.server(chave, cert))` com o certificado Let's Encrypt de darkpassage.com.br, que `instalar_servidor.sh` copia (e recopia a cada renovação) para `/home/dark/certs/darkpassage.crt` e `.key` (mesmo caminho que o servidor v0.7 procura; `certificado_tls.sh` fica redundante); cliente `dtls_client_setup("darkpassage.com.br")`. Rede local continua sem DTLS.
8. Contas pelo site — na VPS o processo do jogo recebe `CHAVE_INTERNA` no ambiente (systemd lê /etc/darkpassage/site.env); seguir a Parte 2 de `site-e-contas.md`.
9. Salvamento — `contas.json` com gravação atômica já existe e aguenta 40 pessoas; o backup diário fica na VPS. Banco de dados (SQLite/Postgres) só se passar de algumas centenas de contas.
10. Prévia no navegador — continua offline/LAN; jogar online pelo navegador exige WebSocket (wss) no servidor, fica para depois.

Já está bom e não precisa mexer: o servidor decide tudo (clientes só mandam comandos), senha com sal e 4000 rodadas, conta já logada em outro PC é recusada.
