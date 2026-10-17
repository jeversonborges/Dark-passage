#!/bin/bash
# Monta o zip do cliente, divide em partes de 45 MiB (limite de 100 MB por arquivo do GitHub) e gera o cliente.json.
#   bash tools/release/empacotar.sh VERSAO SAIDA LAUNCHER_JSON
# LAUNCHER_JSON: cliente.json atual do branch downloads (o bloco "launcher" é mantido).
set -euo pipefail
V=$1; OUT=$2; LJ=$3
R=$(cd "$(dirname "$0")/../.." && pwd); B=$R/game/build/windows
Z=DarkPassage-v$V-windows.zip
mkdir -p "$OUT/cliente"
sed "s/{VERSAO}/$V/" "$R/tools/release/LEIA-ME.txt.modelo" > "$B/LEIA-ME.txt"
rm -f "/tmp/$Z"
(cd "$B" && zip -X -9 -q "/tmp/$Z" DarkPassage.exe LEIA-ME.txt)
(cd "$OUT/cliente" && split -b 47185920 -d -a 2 "/tmp/$Z" "$Z.parte")
python3 - "$V" "/tmp/$Z" "$LJ" "$OUT/cliente/cliente.json" <<'PY'
import hashlib, json, os, sys, datetime
v, z, lj, out = sys.argv[1:]
h = hashlib.sha256()
with open(z, "rb") as f:
    for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
atual = json.load(open(lj)) if os.path.exists(lj) else {}
d = {"versao": v, "arquivo": os.path.basename(z), "tamanho": os.path.getsize(z), "sha256": h.hexdigest(),
     "sistema": "Windows 10/11 64 bits",
     "data": (datetime.datetime.utcnow() - datetime.timedelta(hours=3)).strftime("%Y-%m-%d")}
if "launcher" in atual: d["launcher"] = atual["launcher"]
json.dump(d, open(out, "w"), indent=2, ensure_ascii=False); open(out, "a").write("\n")
print(json.dumps(d, indent=2, ensure_ascii=False))
PY
# confere: as partes juntas dão o mesmo sha256
cat "$OUT/cliente/$Z".parte* | sha256sum | cut -d' ' -f1 | grep -qx "$(python3 -c "import json;print(json.load(open('$OUT/cliente/cliente.json'))['sha256'])")" \
  && echo "partes conferidas: sha256 ok" || { echo "ERRO: partes não batem com o sha256"; exit 1; }
rm -f "/tmp/$Z"
ls -la "$OUT/cliente"
