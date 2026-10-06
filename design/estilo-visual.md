# DARK PASSAGE: Guia de Estilo Visual (v0.1)

> Nome do estilo: **Ferrugem Sagrada**. Gótico de fim do mundo + punk de rua + steampunk sujo, no espírito de Dark Eden.
> Imagens de referência: `design/estilo/` (cena.png, conceitos.png, sprites_3x.png, paleta.png). Fontes editáveis em `design/estilo/fontes/`.

## 1. A ideia em uma frase

Ninguém aqui é limpo nem brilhante. Anjos, demônios e sobreviventes **usam roupas**: sobretudos, couro, fivelas, correntes, máscaras de gás, latão e remendos. O sobrenatural aparece só em **pontos de luz** (halo, brasa, runa, olho) num mundo quase preto.

## 2. Os três pilares

| Pilar | O que entra | O que evita |
|---|---|---|
| **Gótico** (Dark Eden) | sobretudos longos, golas altas, catedrais, vitrais vermelhos, cruzes, velas, sangue | armaduras de placa brilhantes estilo fantasia medieval limpa |
| **Punk** | moicanos, coleiras de espinho, tachas, correntes, roupa rasgada, alfinetes, sucata como arma (placa de trânsito vira machado) | cores neon saturadas no corpo inteiro |
| **Steampunk sujo** | latão, cobre, caldeiras, bobinas, óculos de soldador, braços mecânicos, canos | engrenagens decorativas sem função, dourado novo |

## 3. Regras de personagem

1. **Proporção realista** (7 a 7,5 cabeças), nada de chibi. Dark Eden e Ultima eram "adultos".
2. **Silhueta primeiro:** cada classe precisa ser reconhecível só pela sombra (asas de penas, asas de morcego, capuz, chapéu de aba larga, corpo assimétrico, mochila com antenas).
3. **Roupa conta a facção:**
   - Arautos usam tecido de culto, batina, couro preto, ouro velho, vermelho sangue.
   - Vigília usa roupa de sobrevivência: couro gasto, azul aço, remendo, sucata e latão.
4. **Sujeira sempre:** barras rasgadas, manchas, desgaste. A textura escurece de cima para baixo (pés no escuro).
5. **No máximo 1 cor emissiva por personagem**, em pontos pequenos. É o que faz o sprite saltar na tela escura, como os itens brilhantes do MU.
6. **Rim light na cor da facção** do lado direito do corpo: laranja/vermelho para Arautos, laranja frio ou verde ácido para Vigília.

## 4. As seis classes

| Classe | Silhueta | Roupa e detalhes | Brilho |
|---|---|---|---|
| **Anjo** | asas de penas sujas presas por tiras de couro, halo de ferro quebrado | sobretudo-batina branco osso, gola alta, tiras vermelhas cruzadas, faixa vermelha, rosto de porcelana rachado com venda e olho dourado bordado | halo e espada (ouro claro) |
| **Demônio** | asas de morcego rasgadas, chifres com argolas de latão | sobretudo de couro preto sem mangas, peito nu, coleira de espinhos, ombreira espinhada, corrente no braço, calça rasgada, coturno, moicano vermelho | rachaduras de brasa no peito e olhos |
| **Cultista** | capuz pontudo, túnica larga até o chão | túnica vinho remendada, máscara de gás de osso, velas no ombro, contas de osso, mãos enfaixadas com sangue, grimório acorrentado, incensário | lentes vermelhas da máscara |
| **Humano** | chapéu de aba larga, sobretudo com capa curta | couro marrom gasto, lenço azul aço no rosto, óculos de aviador no chapéu, bandoleira de cartuchos, água benta, crucifixo, escopeta de cano duplo, besta nas costas | frascos de água benta (fraco) |
| **Mutante** | corpo assimétrico: um braço gigante deformado | colete de couro com tachas, pneu velho no ombro, braço de placas soldadas, respirador, moicano, tala de metal na perna, machado de placa de trânsito | veias e pústulas verde ácido |
| **Tecnomancer** | caldeira nas costas com bobinas de tesla | sobretudo azul aço com debrum de latão, avental de couro, braço mecânico, óculos de soldador, cajado com lanterna rúnica, sigilo oculto no peito | runas laranja + arco elétrico azul |

Evolução de classe (estágios 2 e 3): **a roupa cresce, não fica mais limpa**. Mais camadas, mais sucata, mais brilho nos pontos já definidos (o halo fecha, as rachaduras viram fendas, a mutação toma o corpo).

## 5. Paleta

Base do mundo: `#0e0c0d` noite, `#2a2626` pedra, `#46404a` névoa, `#6a3a22` ferrugem.

| Arautos do Juízo | Vigília |
|---|---|
| Branco osso `#d3cab7` | Azul aço `#3c5468` |
| Ouro sujo `#c99a3e` | Couro velho `#5a3a24` |
| Vermelho sangue `#7a1612` | Pele de praga `#6a7058` |
| Couro negro `#1d1a1c` | Latão/cobre `#b07a3a` |
| Carne demoníaca `#5a2622` | Verde ácido `#9cff3a` (emissivo) |
| Brasa `#ff7a1a` (emissivo) | Arco elétrico `#9fd8ff` (emissivo) |

Tudo fica dessaturado (~80%) e puxado para sépia frio, menos os emissivos.

## 6. Mundo e cenário

- Câmera isométrica 2:1 (tiles 48x24 na prévia), como Dark Eden e Ultima.
- Ruas de pedra rachada, muros de tijolo em ruínas, catedrais com vitral vermelho aceso, postes a gás quebrados, barris com fogo, poças de sangue.
- **Luz vem de fontes locais** (fogo, vitral, poste): poças de luz quente num chão quase preto, névoa baixa e vinheta forte nas bordas.
- Nomes de jogador acima da cabeça em fonte bitmap pequena com contorno preto: vermelho para Arautos, azul para Vigília.

## 7. Especificação técnica de sprite

- Altura do personagem: ~100 px em resolução 640x360 (ampliada 2x sem filtro para 1280x720).
- Paleta indexada de até 40 cores por sprite, **sem dither**.
- Contorno escuro de 1 px por fora (`#0a0808`), sombra "blob" elíptica no chão.
- 8 direções (padrão do pipeline em `tools/sprite-pipeline`).

## 8. Como gerar as imagens de novo

Fontes em `design/estilo/fontes/`: um SVG por classe (desenho de conceito), `render.js` (renderiza com o Chromium/Playwright do container) e `process.py` (aplica sujeira, converte em sprite e monta a cena).

    cd design/estilo/fontes
    python3 -m pip install --break-system-packages pillow numpy
    node render.js anjo demonio cultista humano mutante tecnomancer
    python3 process.py

Os desenhos atuais são de frente. Para o jogo, cada classe vira modelo 3D seguindo esta ficha e passa pelo pipeline de 8 direções.
