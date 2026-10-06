# DARK PASSAGE · guia para o Claude

MMORPG old-school, escuro e retrô, no espírito de **Dark Eden**, **MU Online** e **Ultima Online**.
Dono: Jefin (GitHub `jeversonborges`). **Responda sempre em português.**

Este arquivo resume o que foi decidido até a prévia v0.6 (06/10/2026). Os detalhes ficam nos documentos de
`design/` e nos LEIAME/README de cada pasta: leia o documento da área antes de mexer nela, em vez de reinventar.

## Como o Jefin quer que se trabalhe

- **Tudo na nuvem.** Instalações, renders e builds rodam no container, nunca no PC dele. Não sugira instalar nada
  localmente. O container é temporário: as ferramentas precisam ser reinstaladas (cada README tem os comandos).
- **Sem serviços pagos de 3D ou arte** (Tripo, Meshy e afins foram recusados). Personagens e monstros são feitos no
  Blender por código; efeitos, ícones, UI e áudio também são gerados por código, sem samples nem bancos de imagem.
- **Nada com cara de protótipo.** Nunca mostre formas primitivas, cores chapadas, fonte padrão ou placeholder.
  Textura, luz, ornamento e tipografia final antes de qualquer prévia. Nível aprovado como referência: os sprites
  do Anjo e do Humano em `assets/personagens/` (`comparativo.png`): "nesse nível tá bacana demais".
- **Mostrar antes de mudar o que é grande.** Layout de mapa, direção de arte e monstros novos: primeiro uma imagem
  ou prévia para o Jefin aprovar (combinado dos monstros: 1 mob + 1 chefe antes do resto).
- Use os nomes canônicos da lore (abaixo e em `design/missoes/`). Não crie conteúdo paralelo: estenda os JSON existentes.

## Jogo e escopo

- Engine: **Godot 4.4.1**, cliente isométrico + simulação autoritativa (servidor) no mesmo projeto. Build Web para
  prévias e build Windows. Código em `game/` (o `game/README.md` tem todos os comandos).
- Escopo jogável atual: área inicial (Paróquia de São Lázaro, Deserto de Absinto), missões, NPCs com boas histórias,
  itens, drops e baús, mobs, uma dungeon completa (Cripta da Trombeta Calada, 3 andares e 3 chefes), combate caprichado,
  contas e rede local (LAN, porta 7777). Chat, PvP e multiplayer online vêm depois.
- **Controles:** clique para andar, clique no inimigo para ataque básico, skills nas teclas numéricas 1, 2, 3...
  (disparam na hora no alvo do mouse). Z liga o modo automático (luta perto do ponto de início, usa poção, para
  quando acabam as poções de HP ou aparece um chefe). M abre o mapa. Esc pausa.
- Pendências conhecidas da v0.6: 4 monstros novos usam arte recolorida, skills do nível 5 sem VFX e som próprios,
  2 spots pedidos pelas missões fora do mapa, arte própria para Mãe Cardo e Gaspar, dunas repetidas perto do
  acampamento, intros animadas dos chefes, animação de andar/atacar do Anjo ainda dura.

## Direção de arte: "Ferrugem Sagrada"

Guia completo: `design/estilo-visual.md` (imagens em `design/estilo/`).

- Estilo próprio: **gótico de fim do mundo + punk + steampunk sujo**, bem Dark Eden. Anjos e demônios **usam roupas**
  (sobretudos, couro, fivelas, correntes, máscaras de gás, latão, remendos). Nada de fantasia limpa e brilhante.
- Proporção realista (7 a 7,5 cabeças, nada de chibi); silhueta reconhecível por classe; roupa conta a facção;
  sujeira sempre; **no máximo 1 cor emissiva por personagem**, em pontos pequenos; rim light na cor da facção.
- Mundo quase preto, luz vinda de fontes locais (fogo, vitral, lampião), névoa baixa, vinheta. Paleta dessaturada
  puxada para sépia frio, menos os emissivos. No deserto a cor que brilha é o **verde do Amargo**.
- Técnica: sprites pré-renderizados em 3D, câmera isométrica 2:1 (elevação 30°, azimute 45°), 64 px por metro,
  tile 64x32, ~100 px de altura de personagem, 8 direções (S, SE, E, NE, N, NW, W, SW), paleta indexada sem dither,
  contorno escuro de 1 px. Variedade de monstros estilo MU: mesma base com variantes (cor, equipamento, escala).

## Lore e facções

Fontes: `design/classes.md` e `design/missoes/historia.md` (mais os JSON em `design/missoes/dados/`).

- Deus ordenou uma **Guerra de Extermínio**. Os humanos resistiram e forçaram um **impasse**: o fim começou e não
  se completa. Os humanos usaram armas atômicas, e a radiação (o **Amargo**) cobre o mundo.
- **Arautos do Juízo** (a favor do Apocalipse): **Anjo** (suporte), **Cultista** (dano mágico, gasta o próprio HP),
  **Demônio** (tanque/assassino). Aliança cheia de traição; o exército demoníaco é a **Legião Blasfema** (nunca
  "Legião Rubra"), cujo general sumiu.
- **Vigília** (resistência, quer cancelar o fim): **Humano** (dano físico à distância; cowboy com espada larga e
  escopeta serrada), **Mutante** (tanque), **Tecnomancer** (suporte/torretas). Classes exclusivas, 3 por facção:
  essa divisão está decidida, não proponha outra.
- Atributos estilo MU (FOR, AGI, VIT, ESP), 5 pontos por nível, 3 estágios de classe (nível 150 e 400). Nível máximo 400.
- Primeiro mapa: **Deserto de Absinto**, um deserto radioativo. O povo acredita que a estrela Absinto caiu na 3ª
  trombeta; a verdade (linha de missões D) é que os humanos lançaram a ogiva Absinto-1 do Silo São Lázaro, e a
  Absinto-2 ainda está lá. A cidade de São Lázaro está enterrada na areia até o 4º andar ("a rua de hoje é o telhado
  de ontem"). Bondes-veleiros navegam nos trilhos expostos. **Sem carros e sem gangues motorizadas** (nada de clichê).
- O **Rio Amargo** é o oásis do deserto: a única água corrente, amarga e verde, com vida retorcida só nas margens
  ("o rio quase secou").
- Área inicial: Paróquia de São Lázaro. Bases: Acampamento da Vela (Vigília) e Capela de São Lázaro (Arautos).
  Inimigo neutro: os Não-Julgados (mortos que se levantaram para um Juízo que travou; lacre de cera no peito).
- Dungeon: **Cripta da Trombeta Calada** (entrada no porão do Abatedouro). Chefes: andar 1 **Andras, o General
  Partido** (id `general_partido`; ideia do Jefin: general demônio cortado ao meio pelo bonde da Odete, se arrasta e
  come os mortos do campo de batalha), andar 2 **Irmã Celeste, a Carpideira**, andar 3 **Zacarias, o Arauto da
  Trombeta Calada**. Benedito é só lore.
- NPCs principais: Odete, Anselmo, Mãe Cardo, Tobias (carrinho de poções nas fogueiras), Gaspar (Vigília); Madre
  Ivone, Abdiel, Malfas, Lúcio (Arautos); Simão, o coveiro, e Frei Anacleto (neutros); Isaura Valente (linha D,
  "A Estrela Que Nós Soltamos") e Corvina (linha E, "A Legião Sem General").

## Mapas e ritmo dos mobs

Fontes: `design/mapas/level_design.md`, `design/mapas/mundo/proposta_areas.md`, `design/combate/combate.md`.

- **Coerência e beleza.** Nada de clichê. Cada área é coesa como a Lorencia do MU: um chão, uma paleta, um
  vocabulário de props, um céu e uma família de monstros, de ponta a ponta (não uma colcha de temas). "Mesmo que
  seja fim do mundo, pode ser belo."
- Mundo aberto, sem paredes: bordas disfarçadas (tempestade de areia, precipício, dunas). Menos mobs, mais caminhos,
  vegetação, props e estruturas, ecossistemas imersivos. **Nenhum mob sem motivo**: cada grupo tem um `motivo`.
- Evolução de nível principalmente por **missões + spots de farm estilo MU** (12 mobs, respawn de 14 s, fogueira com
  o Tobias).
- **"Menos Diablo, mais WoW."** A maioria dos mobs é **neutra** (nome amarelo, só ataca se apanhar); agressivos
  (nome vermelho) só onde a lore pede (no deserto: Vala dos Cães e Abatedouro Carniça; a cripta é toda agressiva).
  Grupos pequenos (2, ou 3 nos agressivos), raio de aggro pequeno, sem puxadas em cadeia (só o mesmo grupo vem),
  espaço para respirar entre grupos. Todo mob ou área nova segue essa regra.
- Mapas são gerados, nunca editados à mão: altere `design/mapas/fontes/layout.py` e rode
  `layout.py && spots.py && render.py && exportar_jogo.py`. A entrega para o jogo fica em `design/mapas/para_o_jogo/`.

## Onde fica cada coisa

| Pasta | O quê | Documento |
|---|---|---|
| `game/` | projeto Godot (sim em `scripts/sim/`, cliente em `scripts/client/`, rede em `scripts/net/`) | `game/README.md` |
| `design/classes.md` | facções, classes, atributos, recursos | |
| `design/estilo-visual.md`, `design/estilo/` | guia de arte "Ferrugem Sagrada" | |
| `design/combate/` | fórmulas, classes, mobs, chefes, drops, progressão (o JSON vale mais que o .md) | `combate.md`; rode `simular.py` e `farm.py` |
| `design/missoes/` | lore, NPCs, diálogos, missões, itens com nome | `README.md`; rode `validar.py` após editar |
| `design/skills-itens/` | `skills.json` e `itens.json` gerados | `README.md` (`fontes/gerar_json.py`) |
| `design/mapas/` | mapa da área inicial, spots, proposta de mundo | `level_design.md` |
| `assets/personagens/` | 6 classes, folhas idle/walk/attack + `sprites.json` | `README.md` |
| `assets/monstros/` | folhas por animação + `meta.json` | `tools/sprite-pipeline/monstros/README.md` |
| `assets/ambiente/` | pisos, objetos, luzes, `manifest.json` | fontes em `assets/ambiente/fontes/` |
| `assets/efeitos/` | sprite sheets de VFX + `efeitos.json` | `LEIAME.md` |
| `assets/icones/` | ícones de skills e itens, atlas, mochila | `design/skills-itens/README.md` |
| `assets/ui/` | HUD (barra, orbes Vida/Fôlego), mockups, fontes | `assets/ui/hud/README.md` |
| `assets/audio/` | música, ambientes, sfx (OGG) + `audio.json` | `LEIAME.md` |
| `tools/` | pipelines de sprites, efeitos e ícones | README de cada pasta |

O jogo **não** lê `assets/` e `design/` direto: `game/tools/sync.sh` copia tudo para `game/assets/ext/` e
`game/data/design/`. Rode-o sempre que mudar algo nessas pastas. Ele procura os arquivos em `/mnt/project-files`;
numa sessão nova, antes de rodar, aponte esse caminho para a raiz do repositório:

    [ -e /mnt/project-files ] || ln -s "$(git rev-parse --show-toplevel)" /mnt/project-files

(O mesmo vale para alguns scripts de `design/mapas/fontes/` e `game/tools/art/`, que usam esse caminho.)

## Como regerar

- **Jogo (Godot):** `cd game && bash tools/instalar_godot.sh && bash tools/sync.sh`, depois
  `GODOT=/opt/godot/godot bash tools/build_web.sh`. Teste visual:
  `xvfb-run godot --rendering-driver opengl3 -- classe=X fotos=DIR` (ver `game/README.md`).
- **Personagens e monstros (Blender):** `tools/sprite-pipeline/README.md` (instalação: `apt-get install -y blender
  libegl1 libgl1-mesa-dri python3-numpy` + `pip install pillow numpy imageio`). Classes em
  `tools/sprite-pipeline/personagens/` (rig.py, classes.py, anims.py, render.py, sheet.py); monstros em
  `tools/sprite-pipeline/monstros/` (um módulo por monstro com `build()` e `anims()`, variantes estilo MU como
  `carnical:nao_julgado`). Saída no mesmo formato de folha que o jogo já lê.
- **Cenário:** fontes em `assets/ambiente/fontes/`; use o Blender 4.2 LTS oficial (download.blender.org, tem
  denoiser): `blender42 -b -P render_assets.py -- <brutos> [kinds]` e `python3 publicar.py <brutos>`.
- **Efeitos:** `cd tools/vfx && python3 build.py [filtro]` (pillow, numpy). Efeito novo = função `@effect` em
  `efeitos_*.py`, usando as rampas de cor fixas.
- **Ícones:** edite o motivo em `tools/icones/motivos_*.py` e regenere (`design/skills-itens/README.md`).
- **Áudio:** `pip install numpy scipy numba soundfile pyloudnorm`, depois `cd assets/audio/fontes && python3 build.py
  [prefixos]`. Som novo = função `@som(...)`; semente fixa por id.
- **Skills e itens:** `python3 design/skills-itens/fontes/gerar_json.py` quando mudar `design/combate/classes_base.json`
  ou `design/missoes/dados/itens.json`.

Os builds (zip do Windows, `dist/`) e caches (`.godot/`, `__pycache__`) não vão para o repositório.
