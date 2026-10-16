# Kit do Agrak (estádio de São Lázaro enterrado)

Publicado em `assets/ambiente/objetos` em 2026-10-16. Os construtores estão em `fontes/assets.py`, na seção AGRAK. A plateia é feita por `fontes/plateia_agrak.py`.

## Peças de parede (_a / _b, 1 tile, sobem para trás como as paredes da cripta)

- **Arquibancada**
  - `arquibancada_agrak`: 4 degraus de concreto (1,2 a 2,7 m).
  - `arquibancada_agrak_v2`: degrau quebrado e cadeiras derretidas.
  - `arquibancada_caida`: arquibancada desabada em rampa de areia até o fosso.
- **Muro do fosso**
  - `muro_fosso`: muro de 3 m com estacas e arame. Fica no fundo.
  - `muro_fosso_frente`: mureta baixa do lado da câmera, que não tampa a luta.
  - Cantos: `muro_fosso_canto` e `muro_fosso_frente_canto`.
- **Portões**
  - `portao_grade_agrak`: 2x1, fechado.
  - `portao_grade_agrak_aberto`: o mesmo portão com a grade erguida. Troca de sprite quando abre.
  - `portao_gigante`: 3x1, com correntes.
- **Faixas para o muro**: `faixa_campeao`, `faixa_campeao_2` e `faixa_campeao_3` (2x1). Ficam penduradas a 2 m, na face do muro.

## Props

- `jaula_leao` (2x2): os olhos verdes acendem.
- `guincho_corrente` (2x2).
- `placar_camarote` (6x3): placar "SÃO LÁZARO 0 x 0" com o camarote de Caim e Abel e braseiros.
- `ermida_saulo` (4x3): nicho debaixo da arquibancada, velas, a couraça nos ganchos, as 6 armas e luz dourada.
  - Sugestão de luz: [x, y-.8, 1, .78, .35, 4].
- `braseiro_holofote` (1x1): holofote morto virado braseiro.
  - Luz: [x, y, 1, .55, .22, 7], a cada ~6 tiles.
- `pilar_entulho` (2x2): cobertura contra o Bote dos leões.

## Chão (`chao: 1`)

- `circulo_ferro` (7x7): anel de trilho com raio de 3,5 tiles. Vai no centro.
- `linha_cal_a/_b`: 1 tile, linha do campo apagada.
- `linha_cal_meio` (2x2): pedaço do círculo central.

## Plateia animada (camada por cima da arquibancada)

- Nomes: `plateia_{a,b,c}_{0..3}_{a,b}`.
  - Variação a, b ou c.
  - Quadro: 0 parado, 1 balança, 2 braços pela metade, 3 braços no alto (quando alguém morre).
  - Orientação a ou b.
- Põe no mesmo tile da `arquibancada_agrak_{a,b}` correspondente. A âncora de todas é a origem do tile, então elas se alinham sozinhas.
- Não usar em cima de `arquibancada_caida`.
- Sugestão de animação: ciclo 0-1-0-1 a ~4 fps. No evento `morte_pvp` ou na morte de um chefe, 2-3-3-2 e volta.
- Cada tile começa num quadro diferente, para a plateia não balançar junta.

Prévia de um trecho montado: `agrak_kit_trecho.png`. Plateia animada: `plateia_animada.gif`.
