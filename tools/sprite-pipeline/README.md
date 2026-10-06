# Pipeline de sprites isométricos (estilo Dark Eden / Ultima / MU)

Ideia: modelar ou importar em 3D, renderizar em 8 direções com câmera isométrica
ortográfica sem anti-aliasing, e reduzir a paleta para dar o visual retrô.
Era assim que muitos jogos da época geravam seus sprites.

Dependências (instalar em cada container novo):
    apt-get install -y blender libegl1 libgl1-mesa-dri python3-numpy   # numpy: importador glTF do Blender
    python3 -m pip install --break-system-packages pillow numpy imageio

Uso:
    blender -b -P render_iso.py -- out/frames 96     # 8 direções, 96px
    python3 make_sheet.py out/frames out/sheet.png 16  # sprite sheet com 16 cores

`render_iso.py` usa um boneco placeholder; troque pelo import de um .glb/.fbx.

## Estilo MMORPG anos 2000 (Dark Eden / MU / Lineage)

    blender -b -P render_2000s.py -- anjo out/anjo 128     # ou: demonio
    python3 make_sheet_2000s.py out/anjo out/anjo_8dir.png 64
    python3 preview_scene.py                                # out/preview_2000s.png

O que dá o visual da época:
- Sprite pré-renderizado em 3D (Cycles), câmera isométrica a ~35° de elevação.
- Luz principal fria do alto + contraluz (rim) na cor da facção + fill azulado fraco.
- Render em 2x e redução suave (os sprites da época tinham AA), paleta indexada
  de 64 cores sem dither, contorno escuro de 1px e sombra "blob" elíptica.
- Materiais emissivos em armas e detalhes (halo, brasas), como os itens +brilhantes do MU.
- Cores das facções vêm de /mnt/project-files/design/classes.md.

## Direção Dark Eden (punk/gótico) — pasta darkeden/

    cd darkeden
    blender -b -P dp_render.py -- scene out/cena.png              # cena isométrica (~2 min)
    python3 hud.py out/cena.png out/preview_darkeden.png "x,y,Nome,r,g,b" ...
    blender -b -P dp_render.py -- sprite anjo out/anjo 112        # ou: humano
    python3 ../make_sheet_2000s.py out/anjo out/anjo_8dir.png 96

- `dp_models.py`: personagens procedurais (corpo via Skin modifier). Anjo caído punk (Arautos)
  e Humano soldado de moicano (Vigília). Funções reutilizáveis: body, coat, wing, spikes, chain.
- Cena: rua em ruínas de cidade do Leste Europeu à noite (calçamento, tijolos, sacos de areia,
  arame farpado, cruzes, tonel com fogo, sangue, cadáver), luz da lua fria + fogo quente.
- Limite atual: modelos feitos de formas simples. Para qualidade final, trocar por modelos 3D
  esculpidos (import .glb/.fbx) mantendo a mesma câmera, luz e pós-processo.

## Modelos 3D prontos (.glb rigado com animações)

    blender -b -P darkeden/render_glb.py -- models/Soldier.glb out/soldado Walk_Character 10 112
    python3 make_sheet_2000s.py out/soldado out/soldado_8dir.png 96

Escala o modelo para 1,8 de altura, apoia no chão, escurece/dessatura os materiais e
renderiza 8 direções no frame pedido da animação. `models/Soldier.glb` é o modelo de
exemplo do three.js, usado só como teste.

## Personagens jogáveis com esqueleto e animação — pasta personagens/

    cd personagens
    blender -b -P render.py -- anjo /tmp/raw_anjo          # 8 direções × (parado 4, andar 8, atacar 8)
    python3 sheet.py /tmp/raw_anjo ../../../assets/personagens/anjo 64
    blender -b -P render.py -- humano /tmp/raw_humano teste # "teste": só alguns quadros
    blender -b -P cena.py -- /tmp/cena.png                  # rua da prévia com os novos personagens

- `rig.py`: esqueleto humanoide, corpo por Skin modifier, pesos automáticos por distância aos ossos,
  material sujo (manchas + escurece para os pés), poses por quadro.
- `classes.py`: Anjo e Humano seguindo design/estilo-visual.md. `anims.py`: parado, andar e atacar.
- Humano usa IK na mão esquerda (osso `grip.L` na telha da escopeta).
- Saída para o jogo em /mnt/project-files/assets/personagens (ver README lá).
