# Personagens (sprites do jogo)

Gerados no Blender a partir de `tools/sprite-pipeline/personagens/` (estilo "Ferrugem Sagrada").

Cada classe tem uma pasta (`anjo/`, `demonio/`, `cultista/`, `humano/`, `mutante/`, `tecnomancer/`) com:

- `idle.png`, `walk.png`, `attack.png`: sprite sheets. **Linhas = 8 direções**, **colunas = quadros**.
  Ordem das linhas: `S, SE, E, NE, N, NW, W, SW` (para onde o personagem olha na tela; S = para baixo).
- `sprites.json`: tamanho do quadro (192x192), âncora dos pés (`anchor_feet`, onde o personagem pisa no tile),
  fps e se a animação repete. Parado 4 quadros a 4 fps, andar 8 a 10 fps, atacar 8 a 12 fps (não repete).
- `*_SE.gif`: prévia animada da direção SE.
- `<classe>.glb`: modelo 3D com esqueleto e as três animações. `<classe>.blend`: arquivo do Blender.

Detalhes técnicos: câmera isométrica 2:1 (elevação 30°, azimute 45°), 64 px por metro (personagem com ~100 px),
paleta de 64 cores por personagem sem dither (k-means com peso para cores saturadas; pontos emissivos mantêm a cor original e ganham brilho), contorno escuro de 1 px e sombra elíptica embutida.

`comparativo.png` e `preview_rua.png`: os personagens novos na rua da prévia Dark Eden.

`classes.png`: as seis classes lado a lado, paradas e atacando.
Efeitos de ataque: clarão da escopeta (Humano), rajada vermelha do incensário (Cultista) e raio da lanterna (Tecnomancer) aparecem nos quadros 4 e 5 do ataque.

## Humano (cowboy sombrio sobrevivente)
Animações: `idle` (4), `walk` (8), `attack` (8, espada larga), `shoot` (8, escopeta calibre 12 de cano serrado, clarão no quadro 4),
`spin` (8, corte giratório 360° com rastro), `dash` (12, arrancada cortando com a espada, linhas de velocidade e arco do corte).
Fps e repetição de cada uma em `humano/sprites.json`. `humano_antes_depois.png` compara com a versão antiga.
