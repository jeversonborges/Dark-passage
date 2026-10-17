#!/bin/bash
# Fila de renders: espera qualquer lote.sh em andamento terminar e roda o próximo. bash fila.sh id1 id2 ...
H=$(cd "$(dirname "$0")" && pwd)
while pgrep -f "bash $H/lote.sh|bash lote.sh" > /dev/null; do sleep 15; done
bash "$H/lote.sh" "$@"
