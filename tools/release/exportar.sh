#!/bin/bash
# Exporta cliente Windows e servidor Linux do projeto game/ numa máquina limpa.
#   bash tools/release/exportar.sh VERSAO      (GODOT=/opt/godot/godot por padrão)
set -euo pipefail
V=$1
R=$(cd "$(dirname "$0")/../.." && pwd); G=$R/game
GODOT=${GODOT:-/opt/godot/godot}
# a versão do código precisa bater com a pedida (cliente e servidor recusam versões diferentes)
VC=$(sed -n 's/^const VERSAO := "\([^"]*\)".*/\1/p' "$G/scripts/net/rede.gd")
[ "$VC" = "$V" ] || { echo "ERRO: scripts/net/rede.gd diz VERSAO $VC, mas foi pedida a $V"; exit 1; }
cd "$G"
t0=$SECONDS
"$GODOT" --headless --path . --import > "$R/import.log" 2>&1 || true
echo "import: $((SECONDS-t0)) s ($(grep -c ERROR "$R/import.log" || true) linhas com ERROR)"
mkdir -p build/windows build/servidor
t0=$SECONDS
"$GODOT" --headless --path . --export-release "Windows" build/windows/DarkPassage.exe
echo "export Windows: $((SECONDS-t0)) s"
t0=$SECONDS
"$GODOT" --headless --path . --export-pack "Servidor Linux" build/servidor/DarkPassage-servidor.pck
echo "export servidor: $((SECONDS-t0)) s"
ls -la build/windows build/servidor
[ "$(stat -c %s build/windows/DarkPassage.exe)" -gt 50000000 ] || { echo "ERRO: exe pequeno demais"; exit 1; }
[ -s build/servidor/DarkPassage-servidor.pck ] || { echo "ERRO: pck do servidor vazio"; exit 1; }
python3 "$R/tools/release/conferir_icone.py" build/windows/DarkPassage.exe assets/icone.ico || true
