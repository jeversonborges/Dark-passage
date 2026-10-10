# Consertar o download do site (para o Claude do PC do Jefin)

O site mostra "arquivo não está disponível" quando o nginx não acha o zip em `/var/www/darkpassage/downloads/`.
O GitHub está certo: o branch `downloads` tem `cliente/cliente.json` (versão 0.7.3), o jogo em 4 partes
(`DarkPassage-v0.7.3-windows.zip.parte00..03`) e `DarkPassage-Launcher.zip`. Falta a VPS montar e servir.

Antes de rodar: o Jefin precisa mergear o PR #4 no GitHub (ele traz o instalador novo e o site com o launcher).

## 1. Diagnóstico (só leitura, como root na VPS)

    ls -la /var/www/darkpassage/downloads/ 2>&1
    ls -la /home/dark/downloads/cliente/ 2>&1
    grep -n "downloads" /etc/nginx/sites-enabled/darkpassage
    grep -c "launcher" /usr/local/bin/darkpassage-atualizar
    systemctl status darkpassage-atualizar.timer --no-pager | head -5
    journalctl -u darkpassage-atualizar -n 30 --no-pager
    curl -sI https://darkpassage.com.br/downloads/cliente.json | head -1
    curl -sI https://darkpassage.com.br/downloads/DarkPassage-v0.7.3-windows.zip | head -1

O que cada resultado quer dizer:
- `/home/dark/downloads` não existe: a VPS nunca clonou o branch `downloads`.
- `grep downloads` no nginx vazio: o nginx não tem a rota `/downloads/`.
- `grep -c launcher` dá 0: o atualizador é o antigo (não publica o launcher).
- Pasta `/var/www/darkpassage/downloads` vazia ou com outra versão: o atualizador não rodou ou falhou (ver o journal).

## 2. Correção (depois do merge do PR #4)

    sudo -u dark git -C /opt/dark-passage pull --ff-only
    bash /opt/dark-passage/design/online/instalar_servidor.sh
    /usr/local/bin/darkpassage-atualizar
    ls -la /var/www/darkpassage/downloads/

O instalador pode rodar de novo sem perder nada: clona o branch `downloads`, põe a rota `/downloads/` no nginx,
troca o atualizador pelo novo e religa o HTTPS. Mostre ao Jefin o que vai rodar antes, como combinado.

## 3. Conferir

    curl -s https://darkpassage.com.br/downloads/cliente.json
    curl -sI https://darkpassage.com.br/downloads/DarkPassage-v0.7.3-windows.zip | head -1   # 200
    curl -sI https://darkpassage.com.br/downloads/DarkPassage-Launcher.zip | head -1          # 200

Se o `git clone` do branch `downloads` falhar com "Permission denied (publickey)", a deploy key do usuário `dark`
não está no GitHub: `cat /home/dark/.ssh/deploy.pub` e o Jefin cola em
GitHub > Dark-passage > Settings > Deploy keys (só leitura).
