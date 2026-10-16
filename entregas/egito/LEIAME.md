# Egito, a Terra Negra (nível 50 a 70)

A terra da quarta trombeta, sob o Sol Terço. O Nilo voltou e cobriu de lodo preto a areia que tinha enterrado tudo:
Mênfis se reergueu em dois andares (o de lama é de agora, o de pedra é de antes). Do outro lado do rio, ao pé da Esfinge,
está a maior escavação do mundo, onde quatro acampamentos disputam o mesmo buraco: a Casa de Hermes (Djedi, o mago de
cento e dez anos do Papiro Westcar), os atlantes de Thotme (Diaprepes, atrás de Thoth), os Engenheiros Hereges da Vigília
(Dalva Ferraz, atrás das Lâmpadas de Dendera) e o Coro dos Arautos (Cônego Barnabé, que quer pesar o coração do Faraó).
No fundo do Vale dos Reis fica a tumba sem cartucho do Faraó do Êxodo, cujo coração Deus endureceu dez vezes.

Integração no jogo: [INTEGRACAO.md](INTEGRACAO.md).

## A área aberta (`mapas/egito.json`, 200x200)

Duas bases seguras: **Mênfis Reerguida** (praça do Gustavo, o Primarca, com o baú; docas, mercado, ferreiro, nilômetro) e
**a Escavação** (tendas dos quatro acampamentos, fogueiras com o carrinho da Nefer). Quinze zonas de caça em escada de nível,
de Mênfis para o sul e o oeste:

Margem do Papiro 50-52 · Campos da Cheia 51-53 · Vila dos Artesãos 52-55 · Avenida das Esfinges 53-56 · Sacara 55-58 ·
Karnak 56-59 · Lago Sagrado 57-60 · Gizé 58-63 · Casa da Vida 59-62 · Faium 61-65 · Mar de Areia 63-66 ·
Terraços de Hatshepsut 64-67 · Primeira Catarata 66-69 · Vale dos Reis 67-70 · Necrópole Proibida 68-70.

17 spots estilo MU (12 mobs, fogueira, respawn de 14 s), 9 pontos de descanso, 18 monstros com motivo e lore,
maioria neutra; agressivos só onde a lore pede (Calçada de Quéfren, Vale dos Reis, Necrópole).

## O Labirinto de Hawara (dungeon de nível 50, 1 a 5 jogadores, entrada no Faium)

| Andar | Chefe | A luta |
|---|---|---|
| Galerias Alagadas | **Petsuchos**, o crocodilo de ouro de Sobek | a água sobe e só as 4 ilhas de pedra ficam seguras; ele submerge e volta numa investida; as mesas de oferenda curam o deus se não forem quebradas antes |
| Os Doze Pátios | **A Esfinge de Hawara** | ela senta e acende 3 glifos no peito; o grupo tem de pisar no pedestal que completa a frase, senão o teto cai |
| Câmara de Amenemés | **Serket**, a deusa escorpião | o veneno se acumula em pilhas; os ankhs acesos limpam mas apagam; ninhos chocam filhas; ela se entoca |

## O Coração Endurecido (raid de nível 60, 5 a 10 jogadores, entrada no Vale dos Reis)

| Salão | Chefe | A luta |
|---|---|---|
| Pátio do Sol Terço | **Sekhmet** | barra de Sede; quebrar as jarras de cerveja ocre perto dela acalma a leoa |
| Salão dos Magos | **Janes e Jambres** | imitam um ao outro; quem cai primeiro é levantado pelo irmão: separar e derrubar juntos |
| Câmara Canópica | **Os Quatro Filhos de Hórus** | lutam dois de cada vez; cada um que cai derrama o seu vaso e muda a arena |
| O Rio do Duat | **Apófis** | na barca de Rá: manter a Lanterna acesa com as brasas da proa; virar de costas quando os olhos acendem |
| Salão das Duas Verdades | **Anúbis, o Pesador** | metade do grupo é Coração, metade é Pena; equilibrar a balança; segurar Ammit longe dos caídos |
| Câmara do Coração | **O Faraó Sem Nome** | as dez pragas na ordem do Êxodo, acumulando; na décima, só se salva quem está sob uma porta com sangue no lintel (3 por porta) |

As 9 lutas rodam no simulador e passam no teste headless (`codigo/teste_egito.gd`).

## Missões (`conteudo/`)

- **K · A Terra Negra** (9 missões, 50-55): Tuya, a Nomarca, o barqueiro Ahmose e Abdu, o reis da escavação.
- **H · O Labirinto de Hawara** (4, 50-54): Senebtisi, a última sacerdotisa de Sobek.
- **L · O Livro de Thoth** (6, 55-64): Djedi e Diaprepes, até a câmara sob a pata da Esfinge.
- **V · As Lâmpadas de Dendera** (Vigília, 4, 56-63) e **A · A Balança do Coro** (Arautos, 4, 56-63).
- **N · O Coração Endurecido** (10, 60-66): as pragas recomeçam, a sintonia da raid, os 6 chefes e a escolha final
  (pesar, quebrar ou devolver o coração ao Nilo), com flag para o mundo lembrar.
- **R · Turnos** (6 diárias, 51-68).
