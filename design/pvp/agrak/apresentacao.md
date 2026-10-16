# Apresentação do Agrak (ao vivo, dentro do jogo)

Pedido do Jefin (16/10/2026): a apresentação acontece dentro do jogo, com os jogadores já na arena, e não como
cinemática. A câmera continua do jogador e ninguém perde o controle da tela; durante a Chamada eles só ficam presos
no Círculo de Ferro (como já está em `dados.json`). Montagem: thread Prévia. Plateia e portões: thread Cenário.
Sprites: `assets/monstros/` (caim_abel, leao_*, golias, saulo).

## Chamada (45 s)

| t (s) | O que acontece | Sprite / animação | Som e efeito |
|---|---|---|---|
| 0 | Jogadores aparecem no Círculo de Ferro. Plateia já vibrando | plateia (4 quadros) | murmúrio da multidão em loop, braseiros acesos |
| 2 | Caim e Abel no camarote, em cima do placar | `caim_abel_anunciar` | voz de megafone; balão "SENHORAS, SENHORES E COISAS QUE UM DIA FORAM GENTE! BEM-VINDOS AO AGRAK!" |
| 6 | Abel debocha | `caim_abel_discutir` (1 vez) | balão de Abel "Ele ensaiou isso a semana toda." |
| 9 | Plateia em coro | plateia, braços para cima | "A-GRAAAK!" |
| 11 a 35 | Um gladiador por vez: Caim anuncia, Abel debocha (cerca de 3 s cada, no máximo 8; se houver mais, anuncia em grupos) | `anunciar` / `discutir` alternando | nome, facção e classe em texto grande na tela; urro curto da plateia a cada nome |
| 36 | As duas cabeças riem | `caim_abel_rir` | "Aposto dois dentes que não passa dos leões." |
| 38 | Caim: "SOLTEM OS LEÕES!" | `anunciar` | grade do Portão dos Leões sobe (`portao_grade` aberto), som de corrente |
| 39 a 42 | Os três leões saem da jaula correndo até perto do círculo, um de cada vez (Dalila, Nabucodonosor, Sansão por último) | `leao_*_run`, depois `leao_*_roar` parado | rugido (3 vozes), urro da plateia |
| 43 | Abel: "Eles não comem desde a última trombeta. Nem eu." | `discutir` | |
| 45 | Grade invisível cai, luta começa | leões passam para a IA de combate | tambores da música de arena entram |

## Entrada do Golias (início de `luta_gigante`)

1. Caim: "ELE GIRA, VOCÊS SANGRAM. GOOOLIAS!" (`anunciar`), e o Portão do Gigante sobe com o guincho.
2. Golias sai andando (`golias_walk`) até o meio, para e dá o `golias_roar` (é a `anim_entrada` dos dados). A plateia grita "GOLIAS! GOLIAS!".
3. Abel: "Já foi gente. Igual a nós. Mais ou menos." Depois disso a luta começa.

## Outros momentos com sprite

- Gladiador derrotado e levantado: Saulo faz `saulo_rezar` na ermida, com sino curto.
- Vencedor: Caim e Abel fazem `anunciar` e depois `rir`, com chuva de pétalas (efeito) e a plateia de braços para cima.
- Leão morto: Caim faz `anunciar` ("UM GATINHO A MENOS!"), Abel faz `discutir`.
