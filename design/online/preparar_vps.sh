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
