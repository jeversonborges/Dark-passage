# Novo Éden, revisão "Gênesis" (16/10/2026)

Pedido do Jefin (15/10): "revisando Novo Éden, deixando lindo, exuberante, com técnicas de criar cenários lindos e
referências bíblicas do Éden; melhores mobs lá; e a forma que o spot funciona bem feito".

O mapa continua com o id `mata_do_granizo` (nome no HUD: Novo Éden), mesmos níveis 12-30, mesma Torre no canto e a
mesma Catacumba sob a Árvore-Mãe. Tudo é gerado: `python3 gerar.py mata` chama `eden_mapa.py`.

## O jardim segundo o Gênesis

| Referência | No mapa |
|---|---|
| "Plantou um jardim no Éden, do lado do oriente" (Gn 2:8) | **Portão do Oriente** (66.5, 79): arco de pedra coberto de hera, dois pilares com querubins de pedra sem cabeça, a **espada flamejante** fincada num pedestal (Gn 3:24). É por onde se chega do deserto. |
| "Saía um rio do Éden para regar o jardim, e dali se dividia em quatro braços" (Gn 2:10) | **A Nascente dos Quatro Rios** (60, 71), fonte de pedra no Viveiro. Dela saem **Pisom**, **Giom**, **Hidéquel** e **Eufrates**, água limpa (não o verde do Amargo). |
| "Pisom rodeia a terra de Havilá, onde há ouro, bdélio e ônix" (Gn 2:11-12) | **Havilá** (89.5, 70.5): clareira de árvores de frutos dourados, lanternas de seiva âmbar, o spot dos Cervos de Lume. |
| Giom | **Lago de Giom** (68.5, 48.5): lago raso com nenúfares, salgueiros e ponte de tábuas. |
| "A árvore da vida no meio do jardim" (Gn 2:9) | **Árvore-Mãe** (55.5, 77), que já existia: segue sendo a entrada da Catacumba. |
| "A árvore do conhecimento do bem e do mal" (Gn 2:9) e a serpente (Gn 3:1) | **Clareira do Conhecimento** (53.5, 36): árvore pálida torcida com frutos acesos no verde do Amargo (a única cor "errada" do jardim), cercada de cordas e placas pela Enxertia. É o **Ninho da Serpente**, spot de elite. |
| "Pôs querubins ao oriente do jardim" (Gn 3:24) | **Querubins da Espada**: sentinelas que o Coro deixou e nunca chamou de volta, patrulham a Estrada da Torre e o Bosque dos Enxertos. |
| Placas de versículo | prop `placa_versiculo` junto das lanternas: a Enxertia escreveu o Gênesis nas tábuas. |

As zonas queimadas (entrada do deserto e Frente de Queimada) continuam cinza: o jardim é um lugar sendo restaurado,
não um paraíso pronto.

## Cenário: kit "Gênesis" (`assets/ambiente/fontes/eden.py`, 38 objetos + 4 pisos)

- Vegetação: `arvore_eden` (3 variantes, copa de folhas instanciadas, lanternas de seiva penduradas), `figueira` (2, copa
  baixa e larga), `arvore_frutos` (2, frutos dourados que acendem), `salgueiro` (2, ramos caídos), `samambaia` (3),
  `moita_florida` (3: branca, ouro, rosa), `tapete_flores` (3), `pedra_coberta` (3, musgo nas faces de cima),
  `tronco_caido_eden` (2, com cogumelos), `nenufares` (2), `cogumelos_eden`, `juncos_eden`.
- Marcos e props: `fonte_quatro_rios` (5x5, emite ciano), `arvore_conhecimento` (4x4), `espada_flamejante`,
  `pilar_portao`/`pilar_portao_2`, `arco_eden` (4x1), `ponte_tabuas` (3x1), `trelica_videira` (3x1), `colmeia`,
  `lanterna_eden`, `placa_versiculo`.
- Pisos: `relva_eden` (capim), `musgo_pedra` (lajes com musgo, nas ruínas e no Viveiro), `margem_rio` (barro úmido
  das margens), `terra_jardim` (canteiros). O mapa usa `pisos` = e relva, m musgo_pedra, g/w/r margem_rio, j terra_jardim,
  l musgo_lume, z cinza, f mata_morta, t terra, k cascalho.
- Luz: no máximo uma cor emissiva por objeto (âmbar nas lanternas e frutos, ciano na fonte, verde do Amargo só na
  Árvore do Conhecimento). O mapa traz `luzes` nessas cores.
- Árvores com 4,6 a 5,8 m (as de 8-9 m cobriam a tela, como aconteceu em 11/10): copas altas só na moldura, atrás das
  clareiras (o gerador confere 11 tiles "para baixo na tela" antes de pôr uma árvore alta); na frente só vegetação baixa.
- Regerar: `cd assets/ambiente/fontes && /opt/bpyenv/bin/python render_assets.py -- <brutos> [nomes]` e
  `python3 publicar.py <brutos>`; pisos: `/opt/bpyenv/bin/python eden_tiles.py -- <brutos>` e
  `python3 post.py tiles <brutos> ../tiles`. Com o bpy 5.2 (pip) o `kit.py` precisou de
  `transform_apply(location=False, rotation=False, scale=True)` e o `mrig.py` passou a ler as ações em camadas.

## Água limpa: campo `agua` no JSON

O shader do chão (`game/scripts/client/chao.gd`) tem as cores do Rio Amargo fixas. O mapa novo traz
`"agua": {fundo, raso, reflexo, brilho, lume, espuma}` (RGB 0-1) e o diff `patches/chao_agua.diff` transforma essas
cores em uniforms com o padrão igual ao de hoje (o deserto não muda). O `rio.centro` traz os quatro rios como ida e
volta, para a correnteza correr da nascente para fora em cada braço.

## Spots bem feitos (11, todos completos)

Cada spot é um anel de grupos aberto do lado por onde o jogador chega, com a fogueira do Tobias nessa abertura, um
marco atrás (árvore de frutos, salgueiro, pilar) e 12 mobs em grupos de 2 (3 nos agressivos), respawn 14 s.

| Spot | Nível | Mobs | Temperamento |
|---|---|---|---|
| Havilá | 12-14 | Cervo de Lume, Corvo de Brasa | neutro |
| Toca dos Javalis | 13-15 | Javali-Brasa, Lobo de Cinza | territorial |
| Lago de Giom | 15-17 | Enxame de Fagulhas, Lobo de Cinza | neutro |
| Frente de Queimada | 16-18 | Legionário Desgarrado, Incendiária da Comunhão | agressivo (grupos de 3) |
| Bosque dos Enxertos | 18-20 | Enxerto Errado, Querubim da Espada | neutro |
| Clareira do Ent | 19-21 | Enxerto Errado, Cão de Brasa + Ent de Cinza (elite, fora do anel) | neutro |
| Estrada da Torre | 20-22 | Querubim da Espada, Cão de Brasa | neutro |
| Ruínas do Coro | 22-25 | Vitral Andante, Legionário Desgarrado | neutro |
| Charco dos Querubins | 25-28 | Querubim Queimado, Sapo-Sacristão | neutro |
| Acampamento da Legião | 28-30 | Centurião sem Bandeira, Bombardeiro da Legião | territorial |
| Ninho da Serpente | 24-27 | Serpente do Éden, Vitral Andante + **A Serpente** (elite, 27, renasce em 300 s) | neutro |

## Mobs novos com arte própria (`assets/monstros/`, módulos em `tools/sprite-pipeline/monstros/`)

- **Cervo de Lume** (`cervo_de_lume`, 12-14): o bicho que o Éden devolveu. Cervo magro com galhada de seiva viva (pontas
  acesas em âmbar), sininho da Enxertia na cernelha. Pasta; só ataca se apanhar (coice e galhada). Anims: idle, walk,
  attack, alert, hit, death.
- **Querubim da Espada** (`querubim_da_espada`, 18-22): sentinela do Portão. Anjo alto de sobretudo de couro e
  sobrepeliz, peitoral de bronze com rosto de leão, máscara de bronze cheia de olhos (Ez 10:12), quatro asas (duas
  grandes abertas, duas cruzadas sobre o peito, Is 6:2), espada de bronze que queima sem se consumir. Anims: idle,
  walk, attack, hit, death (a chama apaga).
- **Serpente do Éden** (`serpente_do_eden`, 24-27): cobra de 4 m enrolada, terço da frente erguido, capelo de naja com
  "olhos", escamas acesas no verde do Amargo ao longo da espinha. **A Serpente** (`a_serpente`) usa a mesma folha com
  `escala 1.6` e tinta clara (em `dados.json > sprites`). Anims: idle, walk, attack (bote), hit, death.
- `dados.json` (regerado por `gerar.py`) traz os quatro em `mobs` (base + ajuste, estilo v06_extra) e em `sprites`.

## Prévia

Fotos em `previa_eden/` (Viveiro com a Nascente, Portão do Oriente, Havilá, Lago de Giom, Clareira do Conhecimento).
