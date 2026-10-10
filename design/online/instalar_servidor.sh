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
