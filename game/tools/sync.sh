#!/bin/bash
# Copia para dentro do projeto Godot os dados de design e os assets entregues pelas outras frentes.
# Rode sempre que chegar material novo:  bash tools/sync.sh
set -e
P=/mnt/project-files
G=$(cd "$(dirname "$0")/.." && pwd)
D=$G/data/design; E=$G/assets/ext
mkdir -p $D/combate $D/missoes $D/skills-itens $E
cp $P/design/combate/*.json $D/combate/
cp $P/design/missoes/dados/*.json $D/missoes/
cp $P/design/skills-itens/itens.json $P/design/skills-itens/skills.json $D/skills-itens/
# personagens: só as folhas e o manifesto
for c in $P/assets/personagens/*/; do n=$(basename $c); mkdir -p $E/personagens/$n
  cp $c/sprites.json $E/personagens/$n/
  for f in $(python3 -c "import json,sys;print(' '.join(v['file'] for v in json.load(open(sys.argv[1]))['anims'].values()))" $c/sprites.json); do cp $c/$f $E/personagens/$n/; done; done
# monstros: folhas + meta
for m in $P/assets/monstros/*/; do n=$(basename $m); [ -f $m/meta.json ] || continue; mkdir -p $E/monstros/$n
  cp $m/*.png $m/meta.json $E/monstros/$n/; done
# efeitos (sem prévias)
mkdir -p $E/efeitos; cp $P/assets/efeitos/efeitos.json $E/efeitos/
for d in $P/assets/efeitos/*/; do n=$(basename $d); [ "$n" = "_previa" ] && continue; mkdir -p $E/efeitos/$n; cp $d/*.png $E/efeitos/$n/ 2>/dev/null || true; done
# ícones: atlas 40/32 + arte da mochila
mkdir -p $E/icones/mochila; cp $P/assets/icones/atlas_*_40.* $P/assets/icones/atlas_*_64.* $E/icones/
cp $P/assets/icones/itens/mochila/*.png $E/icones/mochila/
# áudio (só ogg + manifesto)
mkdir -p $E/audio; cp $P/assets/audio/audio.json $E/audio/
(cd $P/assets/audio && find ambiente musica sfx -name '*.ogg' | tar cf - -T -) | (cd $E/audio && tar xf -)
# ambiente: kit renderizado (pisos, prédios, props, luzes)
# pisos do projeto têm prioridade; os que faltam vêm do kit renderizado por esta thread (fontes/ambiente_kit,
# gerado pelos scripts Blender em fontes/ambiente_kit/src; fica junto do projeto para o build ser reproduzível)
L=$G/fontes/ambiente_kit
mkdir -p $E/ambiente/tiles $E/ambiente/objetos $E/ambiente/luzes
for t in $L/tiles2_out/*.png $L/tiles_out/*.png; do case $(basename $t) in _*) ;; *) cp $t $E/ambiente/tiles/;; esac; done
for t in $P/assets/ambiente/tiles/*.png; do cp $t $E/ambiente/tiles/; done
cp $P/assets/ambiente/luzes/*.png $E/ambiente/luzes/
[ -d $L/assets_out ] && cp $L/assets_out/*.png $L/assets_out/*.json $E/ambiente/objetos/
for d in objetos assets; do [ -d $P/assets/ambiente/$d ] && cp $P/assets/ambiente/$d/*.{png,json} $E/ambiente/objetos/ 2>/dev/null || true; done
# interface (barra de HUD) e fontes
mkdir -p $E/ui $E/fontes; cp -r $P/assets/ui/hud/1x $P/assets/ui/hud/2x $P/assets/ui/hud/layout.json $E/ui/
cp $P/assets/ui/hud/fontes/*.woff2 $P/design/mapas/fontes/*.ttf $E/fontes/
# mapa aprovado
mkdir -p $D/mapas; cp $P/design/mapas/para_o_jogo/area_inicial.json $P/design/mapas/spots.json $D/mapas/
echo "sync ok"; du -sh $E/* $D
python3 $G/tools/pisos.py
python3 $G/tools/manifest.py
python3 $G/tools/mapa.py
