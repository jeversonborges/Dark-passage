# Evoluções de classe no nível 50 (rascunho para aprovação)

Estilo Ragnarok: no nível 50 cada classe escolhe um de dois caminhos, numa missão de evolução. A escolha é definitiva.

- `previa/arautos.png` e `previa/vigilia.png`: base e as duas evoluções de cada classe (close SE e tamanho real no jogo).
- `evolucoes.json`: bônus de atributos, passiva e 4 skills novas (níveis 50, 55, 60, 70) de cada evolução, no formato de
  `design/combate/classes_base.json`. Números são rascunho; a thread de Combate confere com `simular.py`.
- Código dos modelos: `tools/sprite-pipeline/personagens/evolucoes.py` (parte do modelo base e troca/soma peças, mesmo esqueleto
  e animações). Prévia rápida: `blender -b -P evo_previa.py -- <saida> <id...>`; prancha: `python3 evo_montar.py`.

Pendente após a aprovação do Jefin: folhas completas (idle/walk/attack, 8 direções) com `render.py` + `sheet.py`,
e entrega para a thread "Prévia jogável e área inicial" integrar.

Ids: arcanjo, serafim, lorde_das_trevas, ceifador, arquimago, profeta_do_amargo, pistoleiro, cacador_de_anjos,
gladiador, abominacao, mechanicus, engenheiro_herege.

## Folhas completas (aprovadas pelo Jefin em 16/10/2026)

`sprites/<id>/`: `idle.png`, `walk.png`, `attack.png` (linhas = 8 direções S, SE, E, NE, N, NW, W, SW; colunas = quadros),
GIF de prévia na direção SE e `sprites.json` (tamanho do quadro, âncora dos pés, fps). Mesmo formato de
`assets/personagens/<classe>/`. Gerado por `tools/sprite-pipeline/personagens/render.py` + `sheet.py`.

- Ids: arcanjo, serafim, lorde_das_trevas, ceifador, arquimago, profeta_do_amargo, pistoleiro, cacador_de_anjos,
  gladiador, abominacao, mechanicus, engenheiro_herege.
- `abominacao_colossal`: forma da skill Forma Colossal (nível 65); trocar o sprite da Abominação por este durante os 20 s.
- O quadro varia por personagem (192, 224 ou 352 px por causa das asas e da forma gigante): leia `frame_size` e `anchor` do `sprites.json`.
- Evoluções do Anjo e do Demônio voam (mesma altura de voo das classes base).
- `humano_sem_espada`: novo sprite do Humano base (Jefin, 16/10): besta pesada no ataque básico (`attack`), escopeta serrada
  no `shoot`, `dash` de esquiva; não existe mais `spin` (giro de espada). As skills de espada em
  `design/combate/classes_base.json` precisam ser trocadas pela thread de Combate antes de usar este sprite.
- Efeitos das skills de nível 65 em `assets/efeitos/` (ids no campo `vfx` de cada skill em `evolucoes.json`).
