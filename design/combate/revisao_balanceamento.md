# Revisão de balanceamento (15/10/2026)

Pedido do Jefin: XP 40% mais difícil, monstros comuns com 30% a mais de HP, revisão de chefes, spots de farm e itens
lendários com atributos absurdos. Conferido com `python3 simular.py` e `python3 farm.py` (saídas em
`balanceamento.txt` e `farm_resultado.txt`). As Lágrimas (refino) têm thread própria e não entram aqui.

## O que mudou nos dados

| Onde | Antes | Depois | Por quê |
|---|---|---|---|
| `progressao.json` XP para o próximo nível | `75L² + 375L` | `105L² + 525L` (×1,4; campo `multiplicador_dificuldade_xp`) | pedido do Jefin |
| `mobs.json` HP base do monstro | `32 + 7L` | `41,6 + 9,1L` (×1,3) | pedido do Jefin; vale para todo monstro de curva (comuns, elites, raros, variantes da Mata) |
| `mobs.json` ouro do monstro | `2L a 5L` | `2,6L a 6,5L` (×1,3) | com mais HP o abate demora mais; sem isso o gasto com poção subia de 25% para 33% do ouro |
| `mobs.json` arquétipo bruto, XP | 2,0 | 2,4 | o bruto (HP ×2,2, dano ×1,8) pagava menos XP por HP que o normal; o Chiqueiro do Carniça era o pior spot da faixa |
| `mobs.json` Cão de Vala, ajuste de HP | 1,3 | 1,1 | com o +30% o Fosso dos Cães rendia 19% menos que a Procissão Parada |
| Chefes da Torre e Catacumba (`mapas/mata_do_granizo/dados.json` e `gerar.py`) | HP `26 × L²` | HP `350 × L` (andar 5: `400 × L`) | o HP crescia ao quadrado e o dano do jogador em linha: Baraquiel levava 4 a 8 min solo e o Anjo batia na fúria (360 s) |
| Elmo de Rafael (`missoes/dados/itens.json`) | +5 em tudo, +200 de HP | +4 em tudo, +50 de HP | no nível 12 o jogador tem 200 a 400 de HP; o elmo quase dobrava a vida |
| Chave-Mestra do Primarca | nível 1 com dano 34-56, ESP 30, VIT 15, AGI 10, +400 HP | dano 15-28, ESP 8, VIT 4, AGI 3, +40 HP; efeitos um pouco menores (arco 50%, invocações +25% e +50% de duração, −10% de recarga, escudo 20%) | era um item de nível 1 mais forte que tudo do nível 12. Continua a melhor arma do Gustavo até o 15 e a única com 5 efeitos |

Chefes da cripta (Andras, Celeste, Zacarias) não mudaram: o Jefin pediu Andras mais forte em 11/10 e os três estão no
tempo-alvo (Andras 89 a 138 s, Celeste 85 a 135 s, Zacarias 118 a 190 s). Os adds deles (Soldado Caído etc.) ganham
os +30% junto com os outros monstros.

## Resultado

| | Antes | Depois |
|---|---|---|
| Golpes básicos para matar um monstro normal | 3,3 a 5,2 | 4,3 a 6,8 |
| Min por nível no spot, nível 5 (com poção) | 3,7 a 5,6 | 6,7 a 10,2 |
| Min por nível no spot, nível 7 | 4,7 a 7,1 | 8,6 a 13,0 |
| Min por nível no spot, nível 10 | 6,2 a 9,2 | 11,3 a 16,9 |
| Ouro por minuto e % gasto em poção | igual | igual (12% a 41%) |
| Torre, luta solo da classe do meio (Humano) | 167 s no andar 1, 316 s no andar 5 | 150 s no andar 1, 162 s no andar 5 |
| Torre, classe mais lenta (Anjo) no andar 5 | 467 s (passava da fúria) | 239 s |

Ao todo subir de nível fica cerca de 1,8× mais lento (1,4 da XP × 1,3 do HP). As missões dão a mesma XP de antes, então
pesam 40% menos por nível, como pedido.

## Para a Prévia jogável integrar (o jogo tem números escritos no código)

1. `game/scripts/defs.gd`, `xp_para_proximo`: multiplicar por 1,4 (`105n² + 525n`), ou ler `multiplicador_dificuldade_xp` de `progressao.json`.
2. `game/scripts/sim/loot.gd`, ouro do monstro (`randi_range(2 * nivel, 5 * nivel)` nas linhas do ouro de mob e de baú comum): passar a `2,6L a 6,5L` (ou ler `curva_base.ouro`). O ouro de chefe fica como está.
3. HP dos monstros já sai de `mobs.json` (`Regras.montar_mob`): basta rodar `tools/sync.sh`.
4. Chefes da Torre e Bento Fel: copiar os novos `hp` e `duracao_alvo_s` de `design/mapas/mata_do_granizo/dados.json` para `game/data/v06_extra.json` (Ferrabrás 5250, Madre Brasília 6650, Telegrafista 8050, Malaquias 9450, Baraquiel 12000, Bento Fel 7700).
5. A Chave-Mestra agora tem `dano` no topo do item: antes o jogo não achava o dano (estava só em `atributos`) e a arma batia 3-6.
6. Servidor e cliente mudam juntos (XP e HP são do servidor).

Observação para Skills, itens e ícones: `gerar_json.py` quebrava com a raridade `primordial`; agora pula esse item (o jogo
já o lê de Missões). Ao rodar de novo, entram 3 itens de Missões ainda sem ícone (`livro_dos_vencidos`,
`faixa_de_linho_rafael`, `pena_que_ficou`); por isso o `itens.json` desta revisão só trocou os números do Elmo.

## Refino com as Lágrimas (+15 = 2,2× o dano ou a defesa base)

Não quebra a curva, então os números ficam como a thread das Lágrimas entregou. Conta com o jogador Humano no nível 12:

| Refino da arma | Golpes para matar um monstro normal | Dano total do jogador | Redução de dano com o conjunto todo refinado |
|---|---|---|---|
| +0 | 5,3 | 1,0× | 15% a 17% |
| +6 (só Angélica, sempre dá certo) | 4,1 | cerca de 1,27× | 19% a 21% |
| +15 | 3,1 | cerca de 1,6× a 1,7× | 24% a 26% |

O dano do jogador não dobra porque o refino só multiplica o dano da arma, e uma parte do dano vem dos atributos. A
defesa tem retorno decrescente, então mesmo um conjunto +15 corta pouco mais de um quarto do dano.

- Um +6 devolve a velocidade de abate de antes do +30% de HP, mas custa umas 6 Angélicas por item (cerca de 2 h de spot
  no nível 10, com 0,26% por abate). É recompensa de quem farmou, não o ponto de partida.
- Com as falhas (perde 1 ou 2 níveis), levar um item do +6 ao +15 custa em média cerca de **550 Sanguíneas**. Do +6 ao +9
  são 6 e do +6 ao +12 são 36. No nível 20 o spot dá cerca de 2,7 Sanguíneas por hora, então o +15 fica para o fim de
  jogo, como no MU.
- Um chefe da cripta com arma +15 cai em uns 60% do tempo, o que é aceitável para quem gastou centenas de horas nisso.
