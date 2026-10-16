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
