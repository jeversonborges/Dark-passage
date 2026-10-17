#!/bin/bash
# Publica cliente e servidor, NESTA ordem (servidor antes do cliente tranca quem já atualizou fora do jogo).
#   bash tools/release/publicar.sh VERSAO teste|producao [tudo|cliente]
# producao: branches downloads e servidor (a VPS puxa sozinha). teste: downloads-teste e servidor-teste.
# downloads é recriado órfão a cada versão (force-push): o repositório não acumula 190 MB por versão.
# servidor ganha um commit novo por cima do anterior (8 MB, histórico mantido).
set -euo pipefail
V=$1; DEST=$2; PARTES=${3:-tudo}
R=$(cd "$(dirname "$0")/../.." && pwd)
case $DEST in producao) DL=downloads; SV=servidor;; teste) DL=downloads-teste; SV=servidor-teste;; *) echo "destino: teste|producao"; exit 1;; esac
URL="https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
W=$(mktemp -d); cd "$W"
git init -q . && git config user.name "DARK PASSAGE release" && git config user.email "release@darkpassage.com.br"
git remote add origin "$URL"
# launcher atual sempre vem do downloads de produção
git fetch -q --depth 1 origin downloads
git show FETCH_HEAD:cliente/cliente.json > launcher_atual.json
mkdir -p pub/cliente
git show FETCH_HEAD:cliente/DarkPassage-Launcher.zip > pub/cliente/DarkPassage-Launcher.zip
bash "$R/tools/release/empacotar.sh" "$V" "$W/pub" "$W/launcher_atual.json"
# 1) cliente
git checkout -q --orphan dl && git --work-tree=pub add -A . && git --work-tree=pub commit -q -m "Cliente Windows v$V"
git push -f origin "dl:refs/heads/$DL"
echo "cliente publicado em $DL: $(git rev-parse --short HEAD)"
# 2) servidor (só no teste; em produção o servidor é da Prévia)
[ "$PARTES" = cliente ] && { echo "servidor não publicado (só cliente)"; exit 0; }
NOVO=$(sha256sum "$R/game/build/servidor/DarkPassage-servidor.pck" | cut -c1-16)
git fetch -q --depth 1 origin servidor && echo "pck novo $NOVO | pck em produção $(git show FETCH_HEAD:servidor/DarkPassage-servidor.pck | sha256sum | cut -c1-16)"
if git fetch -q --depth 1 origin "$SV" 2>/dev/null; then BASE=FETCH_HEAD; else git fetch -q --depth 1 origin servidor; BASE=FETCH_HEAD; fi
git checkout -q -B sv "$BASE"
cp "$R/game/build/servidor/DarkPassage-servidor.pck" servidor/DarkPassage-servidor.pck
printf '%s\n' "$V" > servidor/VERSAO
git add servidor && git commit -q -m "Servidor $V: pacote do servidor e VERSAO $V" || echo "servidor sem mudança"
git push origin "sv:refs/heads/$SV"
echo "servidor publicado em $SV: $(git rev-parse --short HEAD)"
