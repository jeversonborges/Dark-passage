# Brief comum: vinheta de área (proposta de mundo do DARK PASSAGE)

Objetivo: UMA imagem 1920x1080 por área, em câmera isométrica igual à do jogo, que faça o Jefin (dono do jogo)
entender e se empolgar com a identidade da área. Barra de qualidade do Jefin: nada com cara de protótipo ou de
formas primitivas cruas; tem que ser detalhado, sujo, com atmosfera (estilo "Ferrugem Sagrada": gótico + punk +
steampunk sujo, Dark Eden, MU Online). Referência do nível aceito: /mnt/project-files/assets/ambiente/previa/cena_deserto.png
e out/deserto_raw.png (vinheta do deserto feita com este mesmo harness).

Ferramentas (já instaladas): `blender42` (Blender 4.2 LTS, Cycles CPU, 4 núcleos compartilhados com outras renders).
Harness: /mnt/project-files/design/mapas/mundo/fontes/cena.py  (LEIA antes) e pos.py (pós-processo + título).
Kit do jogo: /mnt/project-files/assets/ambiente/fontes/kit.py (materiais com nós: mat_stone, mat_brick, mat_wood,
mat_metal, mat_cloth, mat_bone, mat_emit, mat_ground..., e helpers de geometria box, cyl, along, sphere, torus,
displace, crumble, flame, candle, chain, prism) e assets.py (170 modelos prontos em REG; olhe como são feitos e
reaproveite os que servem, ex.: arvore_morta, barraco_sucata, tonel_fogo, poste_gas, ossada_gigante, trilho_bonde,
bonde_veleiro, caixas, barris, estandarte_rasgado, guindaste_sucata, carroca_quebrada...).

Como montar (exemplo completo: area_deserto.py):
- `C.iniciar(ceu=..., poeira=..., luzes=False)` e suas próprias luzes com `C.sol(...)`/`C.ponto(...)` para a paleta da área.
- Chão: `C.chao(material_ou_nome, 160, ondula=..)` POR ÚLTIMO (subsurf pesado deixa tudo lento se vier antes);
  `C.faixa`, `C.mancha` para destaques. Materiais novos de chão: escreva no seu script com os helpers do kit (K.noise, K.voronoi, K.ramp, K.mix, K.bump...).
- Modelos novos: escreva funções `def meu_modelo(m): ...` que montam em volta da origem (base no chão, metros, personagem = 1,8 m)
  e coloque com `C.grupo(meu_modelo, x, y, rot, s, chave="meu_modelo")` (chave = instancia, rápido). Kit: `C.por("nome_do_REG", x, y, rot, s)`.
- Variação: para ter variantes, use chaves diferentes (ex.: chave=f"tronco{i}" com seed diferente), 3 a 5 variantes bastam.
- Câmera: `C.render(OUT, centro=(x,y), largura=~46-58)`. Mundo: +X vai para baixo-direita da tela, +Y para cima-direita.
- Teste rápido: `Q=1 blender42 -b -P area_X.py` (960x540, 16 amostras). Olhe o PNG com a ferramenta Read e itere
  (composição, luz, densidade) até ficar bom. Final: sem Q (1920x1080, 96 amostras).
- Pós: `python3 pos.py out/<id> '<json>'` com nevoa_cor, nevoa, particulas (lista de {cor, n, r, a, rastro, dx}), grade, contraste,
  titulo, sub (ex.: "Nível 15 a 30 · 1ª trombeta"), frase (uma linha de lore), acento (RGB do título), saida.
  Saída final: /mnt/project-files/design/mapas/mundo/imagens/<NN>_<id>.png

Regras de conteúdo (a "regra Lorencia" da proposta, leia /mnt/project-files/design/mapas/mundo/proposta_areas.md):
um chão-base cobrindo a maior parte da imagem, no máximo 2 destaques do mesmo material em outro estado, paleta de
3 cores + 1 cor que brilha, ~10-20 props que se repetem (o "vocabulário") e UM marco forte na composição.
Mostre sobreviventes (uma pequena área habitada: barracas, luz quente) e o marco; sem personagens/monstros.
Sem carros nem veículos a motor. Composição legível: primeiro plano, plano médio com o marco, fundo que some na névoa.

Restrições: escreva só em /mnt/project-files/design/mapas/mundo/fontes/area_<id>.py, fontes/out/<id>* e no PNG final
em mundo/imagens/. NÃO edite cena.py, pos.py, kit.py, assets.py nem nada fora disso (se precisar de um helper,
coloque no seu script). Não instale pacotes. Temp files no próprio out/.
Ao terminar, responda com: caminho do PNG final, o que tem na cena (marco, vocabulário) e o que ficou fraco.
