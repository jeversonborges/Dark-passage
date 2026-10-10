bash <<'FIM'
# DARK PASSAGE - liga o servidor do jogo ao certificado (DTLS) e às contas do site. Rodar como root na VPS,
# depois do instalar_servidor.sh e DEPOIS que darkpassage.com.br apontar para 213.109.169.186 (registro A no DNS).
# - O jogo procura o certificado em /home/dark/certs/darkpassage.crt e .key; achando, liga o DTLS sozinho.
#   Sem ele o servidor sobe sem criptografia e o botão "Jogar online" do jogo não consegue entrar.
# - Com CHAVE_INTERNA no ambiente (/etc/darkpassage/site.env, criado na instalação do site) o jogo confere as
#   senhas no site (127.0.0.1:8080) em vez do contas.json dele. Sem o arquivo, o jogo guarda as contas sozinho.
# Pode rodar de novo quantas vezes quiser.
set -euo pipefail
apt-get install -y certbot python3-certbot-nginx
ufw allow 80/tcp   # o Let's Encrypt confere o domínio por aqui (só durante a emissão e a renovação)

mkdir -p /etc/letsencrypt/renewal-hooks/deploy
cat > /etc/letsencrypt/renewal-hooks/deploy/darkpassage <<'H'
#!/bin/bash
install -d -o dark -g dark -m 700 /home/dark/certs
install -o dark -g dark -m 644 /etc/letsencrypt/live/darkpassage.com.br/fullchain.pem /home/dark/certs/darkpassage.crt
install -o dark -g dark -m 600 /etc/letsencrypt/live/darkpassage.com.br/privkey.pem /home/dark/certs/darkpassage.key
systemctl restart darkpassage || true
H
chmod +x /etc/letsencrypt/renewal-hooks/deploy/darkpassage

if systemctl is-active --quiet nginx; then   # o site já está no ar: o mesmo certificado serve o site e o jogo
  certbot --nginx -d darkpassage.com.br -d www.darkpassage.com.br --non-interactive --agree-tos --register-unsafely-without-email --keep-until-expiring
else
  certbot certonly --standalone -d darkpassage.com.br --non-interactive --agree-tos --register-unsafely-without-email --keep-until-expiring
fi

# o serviço do jogo lê a chave interna do site (o "-" deixa subir mesmo sem o arquivo)
grep -q site.env /etc/systemd/system/darkpassage.service || \
  sed -i '/^\[Service\]/a EnvironmentFile=-/etc/darkpassage/site.env' /etc/systemd/system/darkpassage.service
systemctl daemon-reload
/etc/letsencrypt/renewal-hooks/deploy/darkpassage
sleep 3
journalctl -u darkpassage -n 8 --no-pager | grep -i "ouvindo\|contas:" || true
echo "==== PRONTO: deve aparecer 'cifrado (DTLS)' acima (e 'contas: pelo site' se o site já estiver instalado) ===="
FIM
