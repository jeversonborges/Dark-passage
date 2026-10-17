#!/bin/bash
# Renderiza e monta as folhas de vários NPCs em sequência: bash lote.sh id1 id2 ...
# Brutos em /tmp/br/<id> (RESUME=1 retoma), saída em assets/personagens/npcs/<id>/. Log em /tmp/br/lote.log.
H=$(cd "$(dirname "$0")" && pwd); PY=${PY:-/opt/bpy42/bin/python}
OUT=${OUT:-$H/../../../assets/personagens/npcs}
for n in "$@"; do
  echo "== $n $(date +%H:%M:%S)" >> /tmp/br/lote.log
  RESUME=1 $PY "$H/render.py" -- $n /tmp/br/$n >> /tmp/br/$n.log 2>&1 || { echo "FALHOU render $n" >> /tmp/br/lote.log; continue; }
  CE=$(python3 -c "import sys;sys.path.insert(0,'$H');import ast,re;s=open('$H/$n.py').read();m=re.search(r'^CORES_EXTRA\s*=\s*\"([^\"]*)\"',s,re.M);print(m.group(1) if m else '')")
  CORES_EXTRA=$CE python3 "$H/folha.py" /tmp/br/$n "$OUT/$n" 64 >> /tmp/br/lote.log 2>&1 || echo "FALHOU folha $n" >> /tmp/br/lote.log
done
echo "== fim $(date +%H:%M:%S)" >> /tmp/br/lote.log
