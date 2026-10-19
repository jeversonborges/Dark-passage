# Repositórios de referência (vendor)

Cópias dos repositórios públicos, sem o `.git`. Usados como referência de método, não como dependência de execução.
Para atualizar, clone de novo e atualize o commit abaixo.

| Pasta | Repo | Commit | Licença | Serve para |
|---|---|---|---|---|
| `blender-skills/` | github.com/kevinbadi/blender-skills | b2f0f81 | não encontrada no repo (confirmar com o autor) | bevel e subdivisão nas peças duras; checagem de normal e rugosidade. O resto é Meshy e Polyhaven, proibidos |
| `blender-skills-el4cteo/` | github.com/EL4CTEO/blender-skills | 71d031d | MIT | método de skinning (heat com fallback em proxy), peso rígido para props, teste de deformação, checagem de rig (`rig_check.py`). Rig é humanoide e pede Blender 5.2 |
| `blender-game-skills-majid/` | github.com/majidmanzarpour/blender-game-skills | f0ef293 | MIT | régua de anatomia de criaturas (quadrúpede, articulações do cavalo, locomoção) em `references/categories.md` e `rigging-animation.md` |
| `blender-lpm-ozanzeng/` | github.com/ozanzeng/blender-LPM-skill | 687d0a4 | MIT | disciplina low-poly: orçamento de triângulos por tipo, paleta única, checagem de silhueta (`compare_silhouette.py`). Estilo flat-shaded, diferente do nosso |
| `claude-design-skills-freshtechbro/` | github.com/freshtechbro/claudedesignskills | 1da73fe | MIT (LICENSE; o CLAUDE.md interno cita Apache-2.0) | só 1 skill de Blender (blender-web-pipeline, glTF para web). Sem anatomia, rig ou low-poly de jogo |
| `blender-skills-arjun988/` | github.com/arjun988/blender-skills | 8f778d2 | MIT | pacote com creature-artist (anatomia de quadrúpede, fluxo de criatura), animation (ciclos walk/run/idle, blocking→splining, NLA), rigging, retopology, export-pipeline. Skills em `.claude/skills/` e `.cursor/skills/` (cópia igual). Usado como referência de método; os alvos são MCP ao vivo |
| `godot-skills-divergent/` | github.com/thedivergentai/Game-Dev-Agentic-Skills | db004d7 |                    GNU LESSER GENERAL PUBLIC LICENSE | 17 skills de Godot (combate, partículas, tilemap, animação, câmera, navegação, física 2D, performance). Usadas pela Prévia e pelas threads que tocam game/ |
