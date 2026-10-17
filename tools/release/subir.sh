#!/bin/bash
# Leva a game/ da montagem compartilhada para o main do GitHub e, com VERSAO, dispara a publicação.
#   bash tools/release/subir.sh            só sincroniza a game/ (commit no main)
#   bash tools/release/subir.sh 0.9.4      sincroniza e empurra a tag v0.9.4 -> Actions publica em produção
# Rode de um clone do repositório. Fonte: /mnt/project-files/game (sem .godot, build, builds, dist, server_data).
set -euo pipefail
V=${1:-}
R=$(cd "$(dirname "$0")/../.." && pwd); cd "$R"
[ -z "$(git status --porcelain)" ] || { echo "ERRO: clone com mudanças locais"; exit 1; }
git fetch -q origin main && git checkout -q -B main origin/main
python3 - /mnt/project-files/game "$R/game" <<'PY'
import os, sys, shutil
from concurrent.futures import ThreadPoolExecutor
src, dst = sys.argv[1:]
FORA = {".godot", "build", "builds", "dist", "server_data", "__pycache__"}
def lista(base):
    out = {}
    for d, dirs, files in os.walk(base):
        rel = os.path.relpath(d, base)
        dirs[:] = [x for x in dirs if x not in FORA] if rel == "." else [x for x in dirs if x != "__pycache__"]
        for f in files:
            if f.endswith((".pyc", ".zip")): continue
            p = os.path.normpath(os.path.join(rel, f)); st = os.stat(os.path.join(d, f))
            out[p] = (st.st_size, int(st.st_mtime))
    return out
# o clone tem mtime de checkout, então vale a hora da última sincronização (game/.sincronizado)
marca = os.path.join(dst, ".sincronizado")
ultima = int(open(marca).read().split()[0]) if os.path.exists(marca) else 0
agora = int(__import__("time").time())
a, b = lista(src), lista(dst)
b.pop(".sincronizado", None)
novos = [p for p in a if p not in b or b[p][0] != a[p][0] or a[p][1] >= ultima - 120]
velhos = [p for p in b if p not in a]
def cp(p):
    t = os.path.join(dst, p); os.makedirs(os.path.dirname(t), exist_ok=True); shutil.copy2(os.path.join(src, p), t)
with ThreadPoolExecutor(64) as ex: list(ex.map(cp, novos))
for p in velhos: os.remove(os.path.join(dst, p))
open(marca, "w").write(f"{agora}\n")
print(f"game/: {len(novos)} copiados, {len(velhos)} apagados")
PY
git add -A game
if ! git diff --cached --quiet; then
  git commit -qm "game/: sincronizada da montagem da Prévia${V:+ para a $V}"
  for i in 1 2 3 4; do git push -q origin main && break; sleep $((2**i)); done
fi
echo "main: $(git rev-parse --short HEAD)"
[ -z "$V" ] && exit 0
VC=$(sed -n 's/^const VERSAO := "\([^"]*\)".*/\1/p' game/scripts/net/rede.gd)
[ "$VC" = "$V" ] || { echo "ERRO: rede.gd diz $VC, pedida $V"; exit 1; }
git tag -a "v$V" -m "DARK PASSAGE $V" && git push -q origin "v$V"
echo "tag v$V empurrada: acompanhe em https://github.com/jeversonborges/Dark-passage/actions"
