# Asas: integração no jogo (para a thread "Prévia jogável", dona de `game/`)

**Não entra na 0.9.3.** Vai na versão seguinte. Tudo foi testado numa cópia do jogo (Godot 4.4.1): simulação
(`teste_asas.gd`, 28 de 28), `tools/check.gd` (todos os scripts do cliente compilam) e `tools/sim_test.gd` sem erro.

## O que tem aqui

| Onde | O quê |
|---|---|
| `entregas/asas/LEIAME.md` | design: tipos, níveis, atributos, receitas, drops, visual, molde |
| `entregas/asas/dados/` | `asas_itens.json` (14 asas + 3 materiais), `asas_missoes.json` (9 receitas do Pedro), `asas_dialogo.json` (ramo "Ouvi dizer que você faz asas"), `asas_drops.json` |
| `entregas/asas/aplicar_dados.py` | junta os 4 arquivos em `design/` (pode rodar de novo, não duplica) |
| `game/scripts/...`, `game/tools/sync.sh` | código já aplicado neste ramo (slot asa, voo, drops, ouro, visual) |
| `game/tools/teste_asas.gd` | teste headless da simulação |
| `entregas/asas/ICONES.md` | 17 ícones para o Jefin pintar (regra de ícone único) |
| `assets/asas/<asa>/` | `pairar.png`, `voar.png` (asa inteira, atrás do corpo), `*_frente.png` (pedaço na frente do tronco), `asa.json` |
| `assets/asas/corpos/<classe>/` | corpo em voo (classes que andam) ou sem as asas próprias (Anjo, Demônio e evoluções), no MESMO formato de `assets/armas/<classe>/` (corpo + camadas de arma) |
| `assets/asas/ancoras.json` | encaixe da asa nas costas, por classe, animação, direção e quadro |
| `entregas/asas/previa/` | pranchas e GIFs |

## Passos (já feitos neste ramo)

O código já está em `game/` (ramo sobre a main 596c767, 0.9.5). Os dados de jogo (`game/data/design/`) já têm as
receitas, os itens, o diálogo do Pedro e os drops. Os arquivos de asa (`assets/asas/`) foram copiados para
`assets/` e para `game/assets/ext/asas/` (o mesmo que `tools/sync.sh` faz). Para refazer:

1. `python3 entregas/asas/aplicar_dados.py --jogo game/data/design` (idempotente).
2. `bash game/tools/sync.sh` (copia `assets/asas/` para `game/assets/ext/asas/`).
3. Teste: `cd game && godot --headless --path . --script res://tools/teste_asas.gd`.

O `jogo.patch` que existia antes foi removido: as mudanças já estão no ramo.

## O que o patch muda

- `sim/itens.gd`: slot `asa` (nome "Asa"); bônus `dano_pct`.
- `sim/regras.gd`: `dano_pct` multiplica o dano; `visual_armas` publica `vis.asa = {id}`.
- `sim/jogador.gd`: Anjo e Demônio nascem com a asa básica no slot; personagem salvo antes das asas recebe a básica ao carregar.
- `sim/missoes.gd`: objetivo novo `{"tipo": "ouro", "qtd": N}` (confere, cobra na entrega, texto "Traga N de ouro"); "Consiga N × item".
- `sim/loot.gd`: `_rolar_materiais_asa` (pela tag do mob, rolagem pessoal) e asa pronta de chefe.
- `net/sincro.gd`: a main já publica `vis` (nada a mudar).
- `client/janelas.gd`: casa da asa no equipamento (`Rect2(146, 182, 88, 52)`, embaixo do retrato). Confira se não
  cobre o retrato; se cobrir, mude só esse retângulo.
- `client/unidade.gd`: com asa feita, o corpo vira `assets/ext/asas/corpos/<classe>` (voo) e a asa entra em duas
  camadas (`asa_tras` antes do corpo, `asa_frente` depois das armas). A asa anima no próprio relógio (`pairar`
  parado, `voar` andando) e acompanha o encaixe do quadro atual do corpo. Equipar ou tirar troca na hora, também nos
  outros jogadores. Asa básica (`"visual": null`) não usa camada: fica o corpo de sempre, com as asas do modelo.
  `_montar_armas` ficou idempotente (`iniciar` de novo na evolução não duplica sprites).
- `tools/sync.sh`: bloco das asas.

## Regerar ou criar asa nova

`tools/sprite-pipeline/personagens/`: `asas.py` (molde e as 12 asas), `asas_render.py`, `asas_compor.py`,
`bash asas_lote.sh [id...]` (uma asa leva ~4 min). Corpos em voo: `voo.py` + `bash asas_corpos_lote.sh [classe...]`
(retoma de onde parou; ~20 min por personagem). Prévia: `python3 asas_previa.py saida.png classes=humano,anjo asas=asa_anjo_3`.
Asa nova no jogo: entrada em `ASAS`, `asas_lote.sh <id>`, item com `"slot": "asa"` e `"visual": "<id>"`, `sync.sh`.
