# Tarefa: colocar o DARK PASSAGE no ar (servidor do jogo + site + download)

> Jefin: abra o Claude (Claude Code ou o app Claude no modo Code) na pasta `E:\darkpassage\Dark-passage`, arraste este arquivo para a conversa e escreva "faça o que este arquivo pede".

## Para o Claude que está lendo isto

Você está no PC do Jefin (provavelmente Windows) e, ao contrário da nuvem onde este roteiro foi escrito, você consegue abrir SSH para a VPS. Fale com o Jefin em português, de forma simples, um passo de cada vez. Ele não é de infraestrutura.

**Regras**
- Nunca escreva, salve ou repita uma senha. Quando algo pedir senha, peça para o Jefin digitar ele mesmo no terminal dele.
- A VPS **já foi mexida antes** (o Jefin subiu uma versão do servidor com o Codex, que não está no GitHub). Primeiro inspecione. Não pare, apague nem sobrescreva nada que já esteja lá sem mostrar a ele o que é e ele dizer "pode".
- Mostre o que cada comando vai fazer antes de rodar algo que mude a VPS.

**Dados**
- VPS: MagnoHost, São Paulo, IP `213.109.169.186`, Ubuntu 26.04, usuário `root`.
- Domínio: `darkpassage.com.br` (registro.br). Não é `.com`.
- Repositório: https://github.com/jeversonborges/Dark-passage (privado).
  - branch `servidor`: o servidor do jogo v0.7 já exportado (`servidor/DarkPassage-servidor.pck`, sem sprites/sons, de propósito: o servidor só faz a lógica, quem desenha é o jogo no PC de cada jogador). Tem o deserto e a Cripta com os 3 chefes.
  - branch `downloads`: o cliente Windows em partes, para o botão "Baixar o jogo" do site.
  - PR #3: o site com o botão de download (já inclui o site do PR #2). PR #1: CLAUDE.md.
- Portas: 22/tcp (SSH), 80 e 443/tcp (site), 7777/udp (jogo, ENet).
- Como a VPS se atualiza: ela puxa o GitHub sozinha a cada 2 minutos com uma deploy key só-leitura (`darkpassage-atualizar.timer`), e reinicia o que mudou.

## Passos

**0. Gerar o zip do cliente (Jefin, no navegador).** No projeto DARK PASSAGE no claude.ai, na thread "Download do cliente no site", tocar "Pode criar". Isso cria o branch `downloads`. Confira com `git ls-remote --heads origin downloads`. Se ainda não existir, siga mesmo assim: a VPS pega o zip sozinha quando ele aparecer.

**1. Acesso por chave SSH.**
- Crie uma chave no PC, se não houver: `ssh-keygen -t ed25519 -f %USERPROFILE%\.ssh\darkpassage -N ""` (PowerShell: `$env:USERPROFILE\.ssh\darkpassage`).
- Peça para o Jefin rodar **no terminal dele**, digitando a senha quando pedir:
  `type $env:USERPROFILE\.ssh\darkpassage.pub | ssh root@213.109.169.186 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"`
- Teste: `ssh -i <chave> root@213.109.169.186 hostname`.
- Peça para ele **trocar a senha de root** (`passwd`, digitada por ele), porque a antiga apareceu em chat.

**2. Inspecionar o que já existe (só leitura).** Rode e mostre um resumo para o Jefin:
```
bash -c 'cat /etc/os-release | head -2; echo ---SERVICOS; systemctl list-units --type=service --state=running --no-pager --plain | grep -viE "systemd|dbus|cron|getty|rsyslog|polkit|udisks|multipath|snap|qemu|cloud|packagekit|fwupd|user@"; echo ---PORTAS; ss -tulpn; echo ---PASTAS; ls /opt /home /srv /var/www /root 2>/dev/null; echo ---FIREWALL; ufw status 2>/dev/null; echo ---PROGRAMAS; which godot node nginx docker pm2 git 2>/dev/null; find / -name "*.pck" -not -path "/proc/*" 2>/dev/null | head; ls /etc/systemd/system/*.service 2>/dev/null; echo ---DNS; getent hosts darkpassage.com.br www.darkpassage.com.br; echo ---CERT; ls /etc/letsencrypt/live 2>/dev/null'
```
Se o que o Codex deixou ocupar a porta 7777, 80 ou 443, ou tiver um serviço com nome parecido (`darkpassage*`), explique e pergunte se pode parar e desativar (`systemctl disable --now <nome>`). Não apague os arquivos dele; se precisar, mova para `/root/codex-antigo/`.

**3. Preparar a VPS.** Envie e rode o script `preparar_vps.sh` (abaixo): `ssh root@IP "bash -s" < preparar_vps.sh`. Ele liga firewall (22, 80, 443, 7777/udp), fail2ban, atualizações automáticas, cria o usuário `dark` e gera uma deploy key. No fim imprime uma linha `ssh-ed25519 ...`.

**4. Deploy key (Jefin, no navegador).** Adicionar essa linha em https://github.com/jeversonborges/Dark-passage/settings/keys/new, título "VPS", **sem** "Allow write access".

**5. DNS (Jefin, no navegador).** registro.br → darkpassage.com.br → DNS → "Configurar zona DNS": dois registros **A** para `213.109.169.186`, um com nome vazio e outro `www`. Confira depois com `nslookup darkpassage.com.br`.

**6. Merge dos PRs (Jefin ou você com `gh`, se ele autorizar).** Primeiro o PR #3 (site + download), depois o PR #1.

**7. Instalar jogo + site.** `ssh root@IP "bash -s" < instalar_servidor.sh` (abaixo). Ele instala nginx, certbot, Node, Godot 4.4.1, clona os branches, liga `darkpassage` (jogo), `darkpassage-site` (site em 127.0.0.1:8080) e o atualizador, e faz backup diário. Pode rodar de novo quantas vezes quiser.

**8. HTTPS.** Quando o `nslookup` do passo 5 já devolver o IP, rode o `instalar_servidor.sh` de novo: ele emite o certificado Let's Encrypt, liga o redirecionamento para https e copia o certificado para o jogo (`/home/dark/certs/`), o que liga a criptografia do login no jogo.

**9. Conferir e contar ao Jefin.**
- `https://darkpassage.com.br` abre a página do jogo com cadeado.
- O botão "Baixar o jogo" baixa o zip (`curl -sI https://darkpassage.com.br/downloads/cliente.json`).
- Na VPS: `systemctl is-active darkpassage darkpassage-site nginx darkpassage-atualizar.timer` (tudo `active`), `ss -ulpn | grep 7777`, `journalctl -u darkpassage -n 20 --no-pager` (deve aparecer "ouvindo na porta 7777" e "cifrado (DTLS)").
- No PC: abrir o jogo v0.7, "Jogar online", criar conta pelo site e entrar.
- Por último, se a chave SSH funcionou, ofereça desligar o login por senha (`PasswordAuthentication no` em `/etc/ssh/sshd_config.d/`, depois `systemctl reload ssh`), testando a chave em outra janela antes.

---

## preparar_vps.sh
```bash
bash <<'FIM'
# DARK PASSAGE - prepara a VPS (Ubuntu). Rodar uma vez, como root.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -y && apt-get upgrade -y
apt-get install -y ufw fail2ban unattended-upgrades git curl unzip

# usuário que vai rodar o jogo (sem senha, sem sudo)
id dark >/dev/null 2>&1 || useradd -m -s /bin/bash dark

# firewall: SSH, site (80/443) e a porta do jogo
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 7777/udp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# bloqueia quem erra a senha do SSH 5 vezes
printf '[sshd]\nenabled = true\nmaxretry = 5\nbantime = 1h\n' > /etc/fail2ban/jail.local
systemctl enable --now fail2ban
systemctl restart fail2ban

# atualizações de segurança automáticas
dpkg-reconfigure -f noninteractive unattended-upgrades

# chave para a VPS baixar o jogo do GitHub (só leitura)
sudo -u dark mkdir -p /home/dark/.ssh
sudo -u dark chmod 700 /home/dark/.ssh
[ -f /home/dark/.ssh/deploy ] || sudo -u dark ssh-keygen -q -t ed25519 -N "" -f /home/dark/.ssh/deploy -C vps-darkpassage
sudo -u dark bash -c 'printf "Host github.com\n  IdentityFile ~/.ssh/deploy\n  IdentitiesOnly yes\n  StrictHostKeyChecking accept-new\n" > ~/.ssh/config && chmod 600 ~/.ssh/config'

echo
echo "==== PRONTO. Copie a linha abaixo e mande no chat: ===="
cat /home/dark/.ssh/deploy.pub
ufw status | head -8
FIM
```

## instalar_servidor.sh
```bash
bash <<'FIM'
# DARK PASSAGE - instala jogo + site na VPS. Rodar como root, depois do preparar_vps.sh
# e da deploy key no GitHub. Pode rodar de novo quantas vezes quiser.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
REPO=git@github.com:jeversonborges/Dark-passage.git
IP=213.109.169.186
DOM=darkpassage.com.br
apt-get install -y nginx certbot python3-certbot-nginx nodejs openssl dnsutils
ufw allow 80/tcp; ufw allow 443/tcp

# ---- Godot (servidor do jogo)
V=4.4.1-stable
mkdir -p /opt/godot
if [ ! -x /opt/godot/godot ]; then
  cd /tmp && curl -sSLO https://github.com/godotengine/godot/releases/download/$V/Godot_v${V}_linux.x86_64.zip
  unzip -o -q Godot_v${V}_linux.x86_64.zip && mv -f Godot_v${V}_linux.x86_64 /opt/godot/godot && chmod +x /opt/godot/godot
fi

# ---- cópias do repositório: branch servidor (.pck do jogo) e main (site)
install -d -o dark -g dark /opt/dark-passage
[ -d /home/dark/jogo/.git ] || sudo -u dark git clone -q --depth 1 -b servidor $REPO /home/dark/jogo || echo "(branch servidor ainda não existe, o jogo entra sozinho quando existir)"
[ -d /opt/dark-passage/.git ] || sudo -u dark git clone -q --depth 1 $REPO /opt/dark-passage
# branch downloads: o cliente Windows em partes; o atualizador junta em /var/www/darkpassage/downloads
[ -d /home/dark/downloads/.git ] || sudo -u dark git clone -q --depth 1 -b downloads $REPO /home/dark/downloads || echo "(branch downloads ainda não existe)"
install -d -o dark -g dark /var/www/darkpassage/downloads

# ---- chave interna site <-> jogo
mkdir -p /etc/darkpassage /var/lib/darkpassage
[ -f /etc/darkpassage/site.env ] || { printf 'CHAVE_INTERNA=%s\n' "$(openssl rand -hex 32)" > /etc/darkpassage/site.env; chmod 600 /etc/darkpassage/site.env; }
id darkpassage >/dev/null 2>&1 || useradd -r -s /usr/sbin/nologin darkpassage
chown -R darkpassage /var/lib/darkpassage

# ---- serviço do jogo
cat > /etc/systemd/system/darkpassage.service <<'U'
[Unit]
Description=DARK PASSAGE servidor do jogo
After=network-online.target darkpassage-site.service
[Service]
User=dark
WorkingDirectory=/home/dark/jogo
EnvironmentFile=-/etc/darkpassage/site.env
ExecStart=/opt/godot/godot --headless --main-pack /home/dark/jogo/servidor/DarkPassage-servidor.pck -- servidor=1 max=48
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
U

# ---- serviço do site (unit fixa aqui; igual a site/implantacao/darkpassage-site.service)
cat > /etc/systemd/system/darkpassage-site.service <<'U'
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
U

# ---- nginx na frente do site
cat > /etc/nginx/sites-available/darkpassage <<'U'
server {
    listen 80;
    listen [::]:80;
    server_name darkpassage.com.br www.darkpassage.com.br;
    client_max_body_size 1m;
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host              $host;
        proxy_set_header X-Real-IP         $remote_addr;
        proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /api/interno/ { return 404; }
    location /downloads/ {
        alias /var/www/darkpassage/downloads/;
        autoindex off;
        default_type application/octet-stream;
    }
    location = /downloads/cliente.json {
        alias /var/www/darkpassage/downloads/cliente.json;
        default_type application/json;
        add_header Cache-Control "no-cache";
    }
}
U
[ -L /etc/nginx/sites-enabled/darkpassage ] || ln -s /etc/nginx/sites-available/darkpassage /etc/nginx/sites-enabled/darkpassage
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

# ---- o certificado também vai para o jogo (DTLS), legível pelo usuário dark
mkdir -p /etc/letsencrypt/renewal-hooks/deploy
cat > /etc/letsencrypt/renewal-hooks/deploy/darkpassage.sh <<'U'
#!/bin/bash
install -d -o dark -g dark -m 700 /home/dark/certs
install -o dark -g dark -m 644 /etc/letsencrypt/live/darkpassage.com.br/fullchain.pem /home/dark/certs/darkpassage.crt
install -o dark -g dark -m 600 /etc/letsencrypt/live/darkpassage.com.br/privkey.pem /home/dark/certs/darkpassage.key
systemctl try-restart darkpassage
U
chmod +x /etc/letsencrypt/renewal-hooks/deploy/darkpassage.sh

# ---- atualizador: puxa as duas cópias a cada 2 min e liga o que já estiver pronto
cat > /usr/local/bin/darkpassage-atualizar <<'U'
#!/bin/bash
puxar() {  # $1 pasta, $2 serviço; reinicia se mudou
  [ -d "$1/.git" ] || return 0
  a=$(sudo -u dark git -C "$1" rev-parse HEAD)
  sudo -u dark git -C "$1" pull -q --ff-only || return 0
  [ "$a" != "$(sudo -u dark git -C "$1" rev-parse HEAD)" ] && systemctl try-restart "$2"
  return 0
}
[ -d /home/dark/jogo/.git ] || sudo -u dark git clone -q --depth 1 -b servidor git@github.com:jeversonborges/Dark-passage.git /home/dark/jogo 2>/dev/null
puxar /home/dark/jogo darkpassage
puxar /opt/dark-passage darkpassage-site
# cliente para download: o branch downloads é trocado a cada versão (push --force), então fetch + reset
D=/home/dark/downloads; W=/var/www/darkpassage/downloads
[ -d $D/.git ] || sudo -u dark git clone -q --depth 1 -b downloads git@github.com:jeversonborges/Dark-passage.git $D 2>/dev/null
if [ -e $D/.git ]; then
  sudo -u dark git -C $D fetch -q --depth 1 origin downloads && sudo -u dark git -C $D reset -q --hard origin/downloads
  J=$D/cliente/cliente.json
  if [ -f $J ]; then
    A=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["arquivo"])' $J)
    H=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["sha256"])' $J)
    if [ "$(sha256sum "$W/$A" 2>/dev/null | cut -d' ' -f1)" != "$H" ]; then
      cat "$D/cliente/$A".parte* > "$W/.$A.tmp"
      if [ "$(sha256sum "$W/.$A.tmp" | cut -d' ' -f1)" = "$H" ]; then
        chmod 644 "$W/.$A.tmp"; mv -f "$W/.$A.tmp" "$W/$A"
        install -m 644 $J $W/cliente.json
        find $W -maxdepth 1 -name 'DarkPassage-*.zip' ! -name "$A" -delete
      else
        rm -f "$W/.$A.tmp"; echo "darkpassage: partes do cliente com sha256 errado" >&2
      fi
    fi
  fi
fi
[ -f /opt/dark-passage/site/servidor.js ] && ! systemctl is-enabled -q darkpassage-site && systemctl enable --now darkpassage-site
[ -f /home/dark/jogo/servidor/DarkPassage-servidor.pck ] && ! systemctl is-enabled -q darkpassage && systemctl enable --now darkpassage
exit 0
U
chmod +x /usr/local/bin/darkpassage-atualizar
printf '[Unit]\nDescription=Atualiza o DARK PASSAGE\n[Service]\nType=oneshot\nExecStart=/usr/local/bin/darkpassage-atualizar\n' > /etc/systemd/system/darkpassage-atualizar.service
printf '[Unit]\nDescription=Atualiza o DARK PASSAGE a cada 2 min\n[Timer]\nOnBootSec=1min\nOnUnitActiveSec=2min\n[Install]\nWantedBy=timers.target\n' > /etc/systemd/system/darkpassage-atualizar.timer

# ---- backup diário: contas do site e personagens do jogo, guarda 14 dias
printf '#!/bin/bash\nD=/root/backups; mkdir -p $D\ntar czf $D/darkpassage-$(date +%%F).tgz /var/lib/darkpassage /home/dark/.local/share/godot/app_userdata 2>/dev/null\nfind $D -name "darkpassage-*.tgz" -mtime +14 -delete\n' > /etc/cron.daily/darkpassage-backup
chmod +x /etc/cron.daily/darkpassage-backup

systemctl daemon-reload
systemctl enable --now darkpassage-atualizar.timer
/usr/local/bin/darkpassage-atualizar

# ---- HTTPS: só dá certo quando o domínio já aponta para esta VPS
if [ "$(dig +short $DOM A | tail -1)" = "$IP" ]; then
  certbot --nginx -n --agree-tos --register-unsafely-without-email --redirect -d $DOM -d www.$DOM
  bash /etc/letsencrypt/renewal-hooks/deploy/darkpassage.sh
  echo "HTTPS ligado: https://$DOM"
else
  echo "!! O domínio ainda não aponta para $IP. Depois que apontar, rode este script de novo para ligar o HTTPS."
fi
echo "==== PRONTO ===="
node -v
systemctl is-active darkpassage-site darkpassage || true
FIM
```
