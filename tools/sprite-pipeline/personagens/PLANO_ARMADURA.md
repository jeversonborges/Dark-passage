# Corpo padronizado para troca de armadura (plano, 0.9.8)

Pedido do Jefin: os personagens jogáveis precisam trocar a aparência da armadura, então o corpo
é padronizado. Diferenças pequenas por classe, uma roupa básica por baixo, e as peças se
comportam como um boneco modular (cada parte do corpo pode ser trocada).

## Decisão: boneco modular, com a roupa básica como a própria peça de base

Duas opções foram avaliadas:

- A. Roupa básica por baixo, um bloco único de corpo mais uma camada de roupa.
- B. Boneco modular: cada parte do corpo é um slot próprio e trocável.

**Recomendação: B.** A roupa básica entra como a peça de base de cada slot (camisa, calça,
bota, luva). Assim a "roupa por baixo" existe sem camada extra, e a armadura substitui ou cobre
o slot. A opção A obriga a renderizar combinações, a B renderiza uma camada por peça.

## Esqueleto e slots comuns

Todas as classes usam o mesmo esqueleto (`rig.py`, `BONES`) e o mesmo conjunto de slots:

| Slot | Ossos | Peça de base (roupa básica) |
|---|---|---|
| cabeça | head, neck | cabeça + cabelo |
| tronco | chest, spine, hips | camisa |
| braços | upper_arm, forearm | camisa de manga |
| mãos | hand | luva básica |
| pernas | thigh, shin | calça |
| pés | foot | bota básica |

Diferenças por classe ficam só nas proporções e no material da peça de base (escala de ombro,
largura do quadril, cor). O esqueleto e os pontos de encaixe são iguais para todas.

## Ordem de camadas e oclusão (regra do Jefin)

Cada slot tem uma ordem de desenho e uma lista do que ele cobre:

- Ordem de desenho: base (roupa básica) -> armadura de corpo -> manto/vestido -> acessórios
  (cinto, ombreira, colar).
- O que cobre: vestido cobre calça e bota de base; manto cobre tronco e braços de base;
  manga longa cobre a camisa de manga e a luva; luva cobre a mão.
- Peças de armadura são um pouco maiores que a base (casca de ~1 cm em `skin_mesh`), então a
  base não aparece por dentro da armadura. Quando uma peça cobre um slot, a base desse slot
  fica escondida pela ordem de desenho e não precisa de render separado.

A tabela de cobertura e a ordem vão para `sprites.json` (campo `slots`), para o cliente saber
quais camadas desenhar e em que ordem.

## Pontos de encaixe (compatíveis com as threads de armas, escudos e asas)

- Armas: `hand.R` (arma principal), `hand.L`. Escudos: `forearm.L`.
- Asas: `wing.L`, `wing.R` (`assets/asas/ancoras.json` já usa estes ossos).
- Grimório: `forearm.L` (o do cultista já está assim, commit a90481d7).
- Armadura de corpo e ombreiras: `chest` e `upper_arm.L/R` (já usado por `pauldron()` no Anjo).

Nenhum ponto novo é criado; quem encaixa algo no corpo continua usando os mesmos ossos.

## Prova: Anjo primeiro, depois as outras

1. Separar o corpo do Anjo em slots (base + armadura), sem mudar a aparência final.
2. Renderizar idle, walk e attack com o layout de camadas, e conferir se o corpo base não vaza.
3. Gerar `sprites.json` com `slots` (ordem e cobertura).
4. Estender para Demônio, Cultista, Humano, Mutante, Tecnomancer e Warlord, e depois para as 12
   evoluções do nível 30 (cada uma troca só o material e a silhueta da armadura).

## Fora desta versão

- Armadura visível no corpo continua desligada na 0.9.7 (decisão do Jefin). Este trabalho é a
  base para isso na 0.9.8.
- Sem serviços pagos de 3D. Estilo "Ferrugem Sagrada" (`design/estilo-visual.md`).
- Arte antiga vai para `arquivo/`, nunca é apagada.
