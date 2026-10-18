# Asas (sistema estilo MU) · para a versão depois da 0.9.3

Pedido do Jefin em 17/10/2026: ninguém nasce com asa feita. A partir do nível 10 qualquer classe pode fazer asa com o
**Pedro, o Exilado** (ilhota no Rio Amargo), como no MU: asa de nível 1 no 10, de nível 2 no 30, de nível 3 no 70.
Três tipos: **anjo** (penas que caem das aves), **demônio** (pele ressecada que cai dos demônios) e **mecânica**
(engrenagens, vários foguetes). Cada receita leva **20 joias** e tem que ser difícil. Alguns chefes soltam asa pronta.
O **Anjo e o Demônio** já nascem com uma asa básica equipada (as asas do próprio modelo); a asa feita entra no lugar dela.

## As asas

| Tipo | Nível 1 (nv 10) | Nível 2 (nv 30) | Nível 3 (nv 70) |
|---|---|---|---|
| Anjo (penas) | Asas do Penitente | Asas do Vigia Caído | Asas do Coro Partido (2 pares) |
| Demônio (couro) | Asas de Couro Seco | Asas do Carniceiro | Asas da Legião Blasfema (2 pares) |
| Mecânica (foguetes) | Mochila de Foguetes | Asas de Lata | Asas do Silo |

De chefe (desenho único, só por drop): **Asa Partida de Andras** (Andras, nível 2), **Véu da Carpideira** (Irmã
Celeste, nível 2) e **Asas da Trombeta Calada** (Zacarias, nível 3). Básicas: **Asas Caídas** (Anjo) e **Asas
Rasgadas** (Demônio), vinculadas.

Brilho: penas e couro usam brasa laranja; os foguetes queimam **Amargo** e a chama sai verde (a cor que brilha no deserto).

## Atributos (rascunho para a Revisão de balanceamento)

| | Dano | Reduz dano | HP | Extra do tipo |
|---|---|---|---|---|
| Básica | +3% | 3% | | |
| Nível 1 | +8% | 6% | | anjo +2% reduz · demônio +3% dano · mecânica +4% vel. ataque |
| Nível 2 | +16% | 12% | +150 | anjo +4% · demônio +6% · mecânica +8% |
| Nível 3 | +24% | 18% | +400 | anjo +6% · demônio +9% · mecânica +12% |

O "reduz dano" respeita o teto de 40% de `formulas.json`. Asas de chefe: um pouco acima do nível delas, com um extra
próprio (roubo de vida em Andras, resistência sagrada na Carpideira, crítico em Zacarias).

## Receitas (missões do Pedro)

Cada asa é uma missão do Pedro (`asa_<tipo>_<n>_receita`). Ele só faz depois de receber tudo. A de nível 2 e 3 pedem a
asa anterior do mesmo tipo (na mochila) e uma prova.

| | Material | Joias | Ouro | Prova |
|---|---|---|---|---|
| Nível 1 | 40 | 20 Lágrimas Angélicas | 10.000 | nenhuma (a dificuldade é juntar) |
| Nível 2 | 120 + asa nível 1 | 20 Lágrimas Sanguíneas | 80.000 | anjo: Baraquiel · demônio: 150 Centuriões + 150 Bombardeiros da Legião · mecânica: O Telegrafista + 100 Guarda-Fios |
| Nível 3 | 250 + asa nível 2 | 20 Lágrimas Sanguíneas | 400.000 | anjo: Anúbis, o Pesador + 200 Guardiões de Hórus · demônio: Apófis + 200 Crias de Apófis · mecânica: O Faraó Sem Nome + 200 Esfinges de Carneiro |

Quanto custa (média): só as 20 Angélicas da primeira asa são ~5.700 abates num spot de nível 15 (curva das lágrimas);
as 40 penas, ~1.600 abates de aves. A asa de nível 1 é coisa de vários dias de jogo, não de uma tarde.

## Drops

- **Materiais** (rolagem pessoal por abate, fora da tabela do mob, igual às lágrimas; pela tag do mob, então mob novo
  já entra sozinho): Pena Cinzenta = `voador` 2%, `celestial` 0,8% · Pele Ressecada = `demonio` 1,5% · Engrenagem
  Gasta = `construto` 2,5%, `cultista` e `inaudivel` (Torre) 1,2%, `humano` 0,5%. Spot ×1,25, elite ×3, chefe ×5.
  Mob 10+ níveis abaixo do jogador não solta.
- **Asa pronta de chefe**: Andras 0,4% (Asa Partida), Irmã Celeste 0,4% (Véu), Zacarias 0,25% (Trombeta Calada),
  Baraquiel 0,5% (anjo 2), O Telegrafista 0,5% (mecânica 2), Malaquias 0,5% (demônio 2), Anúbis 0,2% (anjo 3),
  Apófis 0,2% (demônio 3), Faraó Sem Nome 0,2% (mecânica 3).

## Visual

- A asa é uma **camada** que vale para qualquer classe: renderizada uma vez por asa (8 direções, `pairar` 12 quadros e
  `voar` 12 quadros), em duas folhas: a asa inteira, que vai **atrás** do corpo, e o pedaço que fica **na frente** do
  tronco quando as costas viram para a câmera (N, NE, NW, E, W).
- Com asa feita, **todo mundo voa** como o Anjo e o Demônio: o corpo das classes que andam (Humano, Cultista, Mutante,
  Tecnomancer, Warlord e as 12 evoluções) foi refeito pairando (pernas soltas, corpo na altura de voo, tronco inclinado
  ao andar). O Anjo, o Demônio e as evoluções deles ganharam um corpo **sem** as asas próprias, para a asa feita
  entrar no lugar. As armas visíveis continuam funcionando (camadas refeitas em voo).
- `assets/asas/ancoras.json` diz, quadro a quadro, onde fica o encaixe da asa nas costas de cada personagem.

## Molde para asas novas

Uma asa nova é uma entrada em `ASAS` de `tools/sprite-pipeline/personagens/asas.py` (tipo, tamanho, cores, brilho,
adornos) e `bash asas_lote.sh <id>`. Os campos estão no topo do arquivo; os adornos prontos são fivelas, placas,
brasas, correntes, auréola, trombetas, véu, lágrimas (penas), ganchos, espinhos, fissuras, farrapos (couro) e tanque,
rebites, radiação (mecânica). No jogo: um item com `"slot": "asa"` e `"visual": "<id>"`. Nada mais muda.

## Pendências

- Ícones: 17 (14 asas + 3 materiais) na lista do Jefin, `ICONES.md`. Até chegarem, o item aparece sem ícone próprio.
- Som: equipar asa usa o som de armadura. Som de batida de asa e de foguete fica para a thread de Som.
- Números de atributo, chance de drop e ouro: conferir com a Revisão de balanceamento.
