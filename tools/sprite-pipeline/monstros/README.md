# Monstros e chefes do DARK PASSAGE

Pipeline de sprites dos monstros: modelo procedural no Blender, rig próprio,
animações por quadro e render isométrico em 8 direções, igual aos personagens
(mesma câmera 30°/45°, 64 px por metro, luz da lua + contraluz + preenchimento).

Dependências (container novo): ver `../README.md` (Blender, Pillow, NumPy).

## Arquivos

- `base_rig.py`: cópia congelada de `../personagens/rig.py` (materiais sujos, Skin modifier, saias).
- `mrig.py`: rig genérico. Esqueleto por dicionário (`humanoid(escala, largura)` ou ossos próprios),
  pesos automáticos, peças rígidas, poses por quadro com trava no chão, interpolação de poses
  (`keys_to_frames`) e material com manchas (`stained`).
- Um módulo por monstro com `build()` e `anims(R)`: `carnical.py`, `general.py`.
- `render.py`: quadros brutos em 2x. `process.py`: folhas finais. `contato.py`: folha de conferência.

## Uso

    blender -b -P render.py -- carnical /tmp/brutos/carnical                # tudo
    blender -b -P render.py -- carnical /tmp/brutos/c teste 1               # conferência rápida
    blender -b -P render.py -- general /tmp/brutos/g attack,roar 1,3        # só algumas animações/direções
    python3 process.py /tmp/brutos/carnical /mnt/project-files/assets/monstros/carnical 40 .6

## Saída (assets/monstros/<id>/)

- `<id>_<anim>.png`: folha com 8 linhas (direções S, SE, E, NE, N, NW, W, SW) e uma coluna por quadro.
- `meta.json`: tamanho do quadro, âncora (ponto no chão sob o monstro, em px dentro do quadro),
  fps e loop de cada animação. A sombra já vem desenhada no sprite.
- `previa/<anim>_SE.gif`: prévias animadas.

Animações: `idle`, `walk`, `attack`, `hit`, `death` (todas as criaturas); chefes ganham extras
(o General tem `roar`, para a troca de fase). `death` termina no corpo caído: segure o último quadro.

## Monstros (módulos e variantes)

- `carnical.py`: Carniçal; variantes `nao_julgado` (mortalha, mãos amarradas) e `carnical_inchado` (elite, pústulas).
- `general.py`: Andras, o General Partido (chefe do andar 1). Saída em `assets/monstros/andras/`.
- `acougueiro.py`: `acougueiro_oco` (barriga oca, capuz de saco, cutelo; extra `heavy`) e `capataz_gancho`
  (elite: braço de ferro com gancho, porrete, máscara de porco; extras `hook`, `spin`, `shout`).
  O gancho some durante o voo de `hook` (chave de pose `scale`).
- `soldado.py`: `soldado_caido` (luta do General) e `soldado_escudeiro` (escudo e elmo fechado); extra `rise`
  (levanta do chão a mando do General; começa no mesmo quadro final de `death`).
- `quad.py`: esqueleto quadrúpede compartilhado (`quad_bones`, patas `upper_arm/forearm/hand` e `thigh/shin/foot`,
  trava no chão por `PAWS`), corpo em anéis (`ring_path`/`loft`, com costelas e vértebras), tufos de pelo, ciclo de
  pata (`leg_cycle`) e `QRig` (chave de pose `bloat`: escala não uniforme por osso, ex. barriga inchando).
- `cao_de_vala.py`: Cão de Vala (matilha; extras `leap` bote no lugar, o jogo desloca, e `howl`); variante elite
  `cao_de_vala_alfa` (maior, quase preto, placas de sucata parafusadas, cicatrizes). Quadro 192 px.
- `porco_pestilento.py`: Porco Pestilento (placa-aríete na testa, arreio, pústulas verde-ácido; extras `scrape`,
  `charge`, `stun` em loop; `death` termina inchado no chão, a explosão fica com os efeitos). Quadro 256 px.
- `corvo_de_cinza.py`: Corvo de Cinza (esqueleto de ave: corpo, cauda, pescoço, cabeça, bico, asas em 3 ossos com
  penas planas por osso, pernas). Voa sempre a ~1,3 m (`"ground": None`); só `death` trava no chão (cai de asas
  abertas). Variante `corvo_de_cinza_carnica` (1,25x, quase preto, pescoço pelado, bico em gancho, carne pendurada;
  quadro 224 px). `safe_ground(R)` contorna a trava no chão de um quadro travado logo após quadros sem trava.
- `filho_de_cardo.py`: Filho de Cardo (raro de missão): massa de carne com espinhos e cardos roxos, boca vertical,
  6 raízes de 2 ossos, cipós, lápide e cruz de ferro. Extras `burrow`/`emerge`: o root desce abaixo do chão e um
  disco Holdout preso ao osso `occ` esconde o que fica embaixo (fora dessas animações o disco fica 12 m abaixo,
  fora do quadro). Quadro 256 px.
- `monge_emparedado.py`: Monge Emparedado (cripta, andar 2): monge de 2,3 m de argamassa com hábito podre, pedaço de
  parede fundido nas costas, punhos de pedra com grilhões, correntes e rosário de ferro (olhos âmbar). Extras `ambush`
  (atrás de uma parede de tijolos; ~20 pedaços em ossos sem pai `wp*` voam em arco e ficam no chão; fora dela somem
  por escala), `pray` (ajoelha e a crosta de pedra dos ossos `crust.*` cresce; segure o último quadro) e `broken` (loop).
  Quadro 256 px.
- `carpideira_de_ossos.py`: Carpideira de Ossos (cripta, andar 2): ossada flutuante de luto, véu rasgado, máscara de
  ossos em leque, lágrimas negras, relicário-turíbulo na mão esquerda (brilho frio). Sem pernas: vestido em 6 painéis
  de 2 ossos (`sk*`) que arrastam e se abrem no chão na morte; `settle()` assenta a morte no chão sem a trava do mrig.
  Extras `lament`, `heal` (loop). Variante elite `carpideira_de_ossos_viuva` (véu vermelho-escuro, 1,12x, relicário e
  coroa maiores). Quadro 224 px.
- `larva_de_carne.py`: Larva de Carne (cripta, andar 1): verme segmentado de carne de defunto (loft com dobras), pregos de
  caixão, faixas de mortalha furadas, mão e costelas de quem ela comeu, boca de lampreia com 4 lábios (`lip_*`). Traz o
  `XRig` (reaproveitado pelos módulos da cripta): spec `inf`/`sx`/`sy`/`sz` (escala por osso), `vis` (esconde; ossos em
  `R.hidden` começam escondidos), `lx`/`ly`/`lz` (move ossos sem pai), pseudo-ossos `glow` (veias emissivas do material,
  keyframe por animação) e `lamp` (energia de luzes presas a ossos). `attack` = incha 0,8 s pulsando com as veias acesas;
  `death` = estoura (ossos-folha `s_*` murcham, 8 pedaços `k*` voam e caem, poça `pool`, rasgo `rip`). Variante elite
  `larva_de_carne_mae` (1,55x, mais roxa, 4 larvinhas `kid*` nas costas que se mexem; quadro 256 px). Quadro 192 px.
- `gancheiro.py`: Gancheiro (cripta, andar 1): ajudante do abatedouro magro e alto, capuz de carrasco de couro, óculos
  de soldador de latão (lentes acesas), avental curto (`apron_sheet` de `acougueiro.py`), bandoleira de corrente, ganchos no
  cinto e nas costas. `attack` arremessa (osso `hook` some em voo pela chave `scale`); extra `pull` (corrente esticada com o
  gancho na ponta no osso `line`, escondido fora dela; puxa duas vezes com o corpo todo). Quadro 224 px.
- `familiar.py`: familiar do Cultista (racial Pacto do Familiar), variantes `diabrete`, `algoz` e `tirano` (formas dos níveis 1, 6
  e 16; plano em `design/personagens/familiar_cultista.md`). Animações idle, walk, attack, hit, death; saída renomeada para `familiar_<forma>_<anim>.png`.
- `fogo_de_vela.py`: Fogo-de-Vela (cripta, andar 2): velas de igreja derretidas fundidas num corpinho flutuante (cera com
  subsurface, escorridos, rosto derretido, aro de lustre com corrente); chamas em ossos `fl*` tremulando por escala, luz
  pontual presa à cabeça (`lamp`). Extras `blink_out` (encolhe numa bola de cera, vira poça e some) e `blink_in`; `death`
  derrete numa poça (`pool`, com tocos e o rosto) e as chamas apagam uma a uma. Quadro 192 px.
- `corista.py`: Corista de Osso (adicional da Irmã Celeste, andar 2): esqueleto de menino do coro (batina vermelha,
  sobrepeliz rasgada, gola de renda, cera escorrida, hinário aberto). Osso `voice` leva olhos, boca e auréola acesos e fica
  escondido (escala .001) fora de `sing`. `idle` = estátua apagada (2 quadros); `sing` canta e brilha; `death` desmorona
  (reaproveita painéis e `settle()` da Carpideira). Quadro 224 px.
- `celeste.py`: Irmã Celeste (chefe, andar 2): freira regente de hábito preto com cauda, sobretúnica rasgada, escapulário,
  rosto de porcelana com lágrimas de cera acesas, véu, coroa de 7 velas (chamas no osso `flames`), batuta de osso com sino
  e rosário de dentes. Reaproveita `tube`/`skirt_wave`/`settle` da Carpideira e `apron_sheet`. Extras `lament`, `weep`,
  `conduct` (rege os Coristas), `choir`, `exhausted` (loop caída no chão), `snuff`, `summon`; `death` apaga a coroa.
  Escala 1,45x, quadro 416 px.
- `zacarias.py`: Zacarias, o Arauto da Trombeta Calada (chefe do andar 3), visual 3 no padrão Egito/Amenti (usa `amenti.py`):
  armadura gótica de prata enegrecida em cascas com filigrana de ouro, corpo de luz astral por baixo (material `astral_mat`:
  núcleo azul, veios e bordas brancas), máscara de ouro sem boca com lacre de cera, cabelo de chamas astrais, auréola
  quebrada, trombeta calada nas costas (campânula lacrada com cera e pregos, corrente), tabardo de linho, asas de penas
  (`feather_wing`, ossos `wL1..3`/`wR1..3`), montante com runas (canal `glow`). Luz real na ponta da lâmina (chave `lamp`),
  aura no osso `aura` e onda de luz no chão no osso sem pai `onda` (ambos escondidos fora de charge/release, chave `vis`).
  Animações: idle (8), walk, attack, charge (laço de 4 s no jogo), release, hit, death. Escala 1,5x, quadro 512 px.
  Visuais anteriores: `zacarias_v1.py` (porcelana) e `zacarias_v2.py` (primeira armadura astral).
- `golias.py`: Golias, o Pião do Agrak (chefe da luta 2 do evento PvP do Agrak, `design/pvp/agrak/`): mutante gigante
  (3,2 m, `SCALE` 1,78) de gladiador de sucata, elmo de murmilão com grade e crista de arame, manica no braço esquerdo,
  galerus no direito, saiote de tiras, tumor com pústulas do Amargo (único emissivo). Bola cravejada numa corrente de
  6 elos-osso (`ch1..ch6` + `ball`, filhos de `hand.R`); `GRig.set_pose` aponta os elos depois da pose (chave `chain`:
  modos `drape` pendurada/arrastando, `fling` esticada pelo giro, `dir` direção dada), sem atravessar o chão. Extras
  `spin_start`, `spin` (loop de 12 quadros, uma volta), `spin_end` (tonto), `roar`. Quadro 512 px.
  `AMOSTRAS=32 blender -b -P render.py -- golias /tmp/brutos/golias` e
  `python3 process.py /tmp/brutos/golias /mnt/project-files/assets/monstros/golias 48 1.4`.

### Atlântida (Gadiro e guardiões)

- `atlante.py`: base comum dos módulos da Atlântida (não é monstro). `XRig` calcula a pose sem ação ligada e grava
  as chaves depois (chaves extras `glow` para força do emissivo, `follow` e `drop` para peças que caem e rolam);
  materiais `patina` (oricalco com azinhavre), `scales` (escamas Voronoi com ventre), `glow` (emissivo só na câmera);
  `tube()`/`bind_path()` para corpos de serpente ao longo de um caminho.
- `gadiro.py`: chefe **Gadiro, o Rei Que Abriu a Porta** (nível 45). Torso de rei atlante sobre corpo de serpente em
  espiral, coroa de oricalco que cai no `death`, tridente quebrado, olhos âmbar (único emissivo). Extras `roar`,
  `coil` (bote da espiral), `cast`. Quadro 512 px.
  `blender -b -P render.py -- gadiro /tmp/brutos/gadiro` e `python3 process.py /tmp/brutos/gadiro <dst> 48 2.2`.
- `filho_da_serpente.py`: guerreiro-serpente com linotórax de escamas de bronze, khopesh e escudo; extra `hiss`.
  Variante `filho_da_serpente:sacerdote_da_serpente` (túnica, estola púrpura, caduceu) ganha `cast`. Emissivo âmbar.
  Quadro 224 px. `process.py ... 44 .7`.
- `vigia_de_oricalco.py`: autômato de placas de oricalco sem rosto, glifos verde-esmeralda (único emissivo), foice de
  lavoura; no `death` elmo e antebraço caem e o glifo apaga. Variante `vigia_de_oricalco:hoplita_de_oricalco`
  (elmo coríntio, hoplon com tridente, lança) ganha `block`. Quadro 256 px. `process.py ... 44 .8` (hoplita `.9`).
- `cinocefalo.py`: escriba cinocéfalo de quatro apoios (rig humanoide com braços longos e `plant`), juba prateada,
  disco lunar de oricalco com glifo esmeralda, paleta e juncos de escriba; extra `howl`. Quadro 192 px.
  `process.py ... 44 .8`.

### Egito (parte A)

Conceito em `design/mapas/egito/conceito.md` (§5 a §7). Emissivo da área: turquesa de faiança (`kemet.TURQ`), no máximo
um por criatura. Prévias em `entregas/egito/previa/monstros_A*.png`.

- `kemet.py`: base comum (não é monstro). `rest_uv`/`finalize` gravam a posição de repouso em UVs (`rxy`, `rz`) para os
  materiais não "nadarem" com a deformação; materiais `linho` (faixas cruzadas de múmia, costuras, resina preta em
  filetes, lodo), `listras` (pintura antiga gasta: nemes, colares, cajados), `manchas` (leopardo, couro de boi), `ouro`,
  `bronze`, `cobre`; `faixas_em` (voltas de faixa coladas num osso), `tira`, `hieroglifos`.
- `mumia.py` (rig humanoide + `XRig` de `atlante.py`, ossos `prop.R/L` de pegada no eixo -Y, `heart` sem pai que segue o
  peito, `beads` dos cordões do mangual): `mumia_operaria` (cesto e enxó de cobre; o idle ainda bate a enxó),
  `sacerdote_mumia` (pele de leopardo, incensário em forma de braço, cajado; `cast`), `guardiao_mumia` (elite 1,15x:
  máscara de madeira pintada, saiote plissado, escudo de couro de boi, khopesh; `shield`, segure o último quadro),
  `janes` / `jambres` (chefes da Raid, 2,4 m: máscara de íbis quebrada / pele de babuíno; bastão com serpente;
  `cast`, `staff_serpent` (o bastão some no voo), `resurrect` (canal: quadros 4 a 11 em loop)), `farao_sem_nome`
  (chefe final, 2,8 m: nemes, uraeus quebrado, barba postiça, colar largo, cartucho raspado, cajado e mangual na pose
  de Osíris, coração de granito com rachaduras turquesa na fenda do peito, que cai e fica no chão no `death`; `cast`,
  `plague`, `summon`, `roar`). Quadros 208/224/256/320/384 px.
- `escaravelho.py`: `escaravelho_sagrado` (bola de lodo no osso `ball`, sem pai, rola no `walk`), `escaravelho_carniceiro`
  (verde-cobre, mandíbulas em foice, fiapos de linho), `escaravelho_rei` (elite 1,6x, lápis-lazúli com veios de ouro,
  disco solar com olho turquesa). Extras `burrow`/`emerge` com o disco Holdout do osso `occ` (o último quadro de
  `burrow` é "enterrado"). Morte de costas com as patas encolhidas. Quadro 192 px (rei 256).
- `crocodilo.py`: corpo e cauda num `tube` com escamas por UV, osteodermos, lodo seco nas costas; `crocodilo_do_nilo`,
  `crocodilo_gigante` (1,5x, cicatrizes), `petsuchos` (chefe do andar 1 do Labirinto, 2,2x: brincos de ouro e cristal,
  braceletes, colar de faiança com pingente de escaravelho; `submerge`, `emerge`, `charge` em loop, `eat`).
  Quadros 224/320/448 px.
- `serpente.py`: `naja` (capelo com as faixas da garganta; `spit`), `cria_de_apofis` (elite, ~6 m, escamas pretas com
  veios turquesa, crista de espinhos), `apofis` (chefe 4 da Raid: só a coluna que sai da água, com um arco do corpo
  atrás; disco Holdout fixo na linha d'água; olhos acendem pela chave `glow`; `rise`, `bite`, `gaze`, `spit`,
  `submerge`). Quadros 192/384/512 px.

Render (um processo por vez; `AMOSTRAS=n` troca as amostras):

    cd tools/sprite-pipeline/monstros
    /opt/bpy42/bin/python render.py -- mumia:farao_sem_nome /tmp/brutos/farao_sem_nome
    python3 process.py /tmp/brutos/farao_sem_nome /mnt/project-files/assets/monstros/farao_sem_nome 64 .85

Cores e sombra usadas: operária/sacerdote 48 .6, guardião 48 .7, janes/jambres 64 .75, faraó 64 .85; escaravelhos
48 .7 / 48 .65 / 56 1.0; crocodilos 48 .9 / 48 1.35, petsuchos 64 2.0; naja 48 .5, cria 56 1.4, apofis 64 2.2.

Com ouro ou cores saturadas no quadro, a reserva de brilho da paleta perde o turquesa (olhos e veios saem brancos ou
somem). Para isso o `process.py` aceita `CORES_EXTRA` (hex separados por vírgula, somados à paleta). Todas as variantes
da parte A foram processadas com `CORES_EXTRA="78f4f0,50c8b4,2e7c74"`.

## Egito (parte B)

Guardiões de cabeça de animal, esfinges, escorpiões e Ammit (conceito em `design/mapas/egito/conceito.md`, §5 a §7).
Emissivo único: turquesa de faiança (olhos, rachaduras, glifos, ferrão).

- `netjer.py`: humanoide de 2,3 m (pele cinza-escura, saiote plissado com avental, colar largo de faiança rachado,
  braceletes de bronze verde, sandálias de papiro), cabeça trocável por variante. Ossos extras `jaw`, `wpn` (arma da mão
  direita; a pose aponta a arma com a chave `aim`) e `arrow` (some pela chave `scale`). `pose_basis()` orienta peças
  pela pose base (o escudo). Variantes: `anubis_sentinela` (lança), `anubis_guardiao` (elite 1,15x, nemes, khopesh e
  escudo; `shield`), `sobekita` (crocodilo, maça de granito), `guardiao_falcao` (arco, aljava, asas de bronze dobradas;
  o `attack` é o disparo), os Filhos de Hórus `imseti` / `hapi` / `duamutef` / `qebehsenuef` (2,6 m, vaso canópico no
  cinto, saiote de cor própria, cetro was; `cast`, `aura` em loop), `sekhmet` (2,8 m, disco solar com uraeus, peruca
  tripartida, vestido vermelho-ocre; `roar`, `leap` (o jogo desloca), `breath`, `frenzy` em loop) e `anubis_pesador`
  (3,0 m, colar de ouro, balança e cetro was; `mark`, `slam`, `cast`). Quadros 288/320/384 px.
- `esfinge_carneiro.py` (`quad.py` + `XRig`): `esfinge_carneiro` (criosfinge de calcário, chifres de Amon, estatueta do
  rei entre as patas, lascas e rachaduras com brilho) e `esfinge_de_hawara` (chefe, 2x: androsfinge de nemes, nariz
  quebrado, três glifos no peito que acendem pela chave `glow`; `riddle` em loop, `slam`, `wave`). Quadros 384/640 px.
- `escorpiao.py` (`XRig`, ossos próprios: corpo, 2 do mesossoma, 5 da cauda + `sting`, pedipalpos com `claw`/`finger`,
  8 patas de 3 ossos): `escorpiao_de_serket` (marrom-areia, pinças de arenito), `escorpiao_negro` (elite 1,2x, preto,
  ferrão turquesa), `serket` (chefe 1,75x: torso de mulher com peruca de tranças e coroa de escorpião de ouro; `sting`,
  `burrow`/`emerge` com o disco Holdout do osso `occ`, `cast`). Quadros 320/352/576 px.
- `ammit.py` (`quad.py`): Ammit, a Devoradora (cabeça de crocodilo, frente de leão com juba listrada, traseiro de
  hipopótamo; `devour`, `roar`, `charge` em loop). Quadro 448 px.

Cores e sombra: sentinela/sobekita/falcão 46 .7, guardião 46 .8, filhos 46 .8, sekhmet 48 .9, pesador 48 1.0;
esfinge 44 1.3, hawara 48 2.6; escorpiões 44 1.2 / 44 1.4, serket 48 2.2; ammit 46 1.9. Os quadros grandes (> 500 px)
usam 20 amostras.

### Atlântida (animais de Poseidon e de Thoth)

- `touro_de_poseidon.py`: Touro de Poseidon (nível 30-33, neutro): touro de 1,7 m na cernelha, pelo preto-avermelhado
  empoeirado, cupim e barbela, chifres em lira com anéis e ponteiras de oricalco (azinhavre), guirlanda de oliveira seca
  com fitas de linho, marcas de laço e cicatrizes; sem emissivo. Extras `scrape` e `charge` (loops; o jogo desloca).
  Variante elite `touro_do_pilar` (1,25x, quase preto, chifres revestidos de oricalco, placa na testa com glifos
  herméticos acesos em verde-esmeralda, correntes partidas; quadro 384 px). Quadro 320 px. Pós: `40 1.4` / `40 1.75`.
- `ibis_de_thoth.py`: Íbis de Thoth (nível 30-34, neutro): pernalta de 1,1 m, branco sujo de lama e limo, cabeça e
  pescoço pelados pretos, bico curvo, plumas pretas sobre a garupa, argola de oricalco na perna. Asas em dois estados
  (ossos `fold.*` fechadas; `wing1..3` abertas), o que não aparece fica escondido pela chave `scale`. Extra `flap`
  (abre as asas e dá saltos curtos, loop); `death` cai de asas abertas. Quadro 224 px. Pós: `40 .55`.
- `elefante_de_atlas.py`: Elefante de Atlas (nível 36-39, neutro): 3,2 m na cernelha, pele enrugada (ondas no relevo)
  com lama seca e musgo, presas com anéis de oricalco, pintura ritual desbotada, orelhas rasgadas (`ear.*`), tromba em
  4 ossos, manta de linho rasgada com franjas de contas das três pedras, cintas de couro e sino de bronze. Extra
  `trumpet`. Quadro 512 px, 32 amostras. Pós: `40 2.6`.

### Lordes dos Salões de Amenti (não atacáveis)

- `amenti.py`: base comum (não é monstro). Materiais lidos na posição de repouso (`rest_uv` próprio, seguro com malhas
  que já têm UV): `marfim` (placa esmaltada com filigrana de ouro em arabescos), `ouro`, `pano`, `couro`, `aco`,
  `lava` (ferro negro ou carne com rachaduras de lava; devolve o socket da emissão para pulsar pela chave `glow`),
  `chifre`, `membrana`. Malhas: `shell`/`shell_edge` (cascas de elipsoide e filetes na borda), `ttube`, `trim`,
  `rings_loft`, `annulus`, `blade`, `flame_spike`, `sheet`, `skirt_folds`, `limb`; `feather_wing` (asa de penas em
  3 ossos) e `bat_wing` (membrana rasgada); partículas em ossos sem pai (`mote_bones`, `motes`, `mote_pose`).
- `lider_dos_anjos.py`: o Líder dos Anjos, "o Perfeito" (4,9 m): marfim e ouro, elmo com coroa de pontas, halo em roda,
  seis asas, saia, tabardo e manto, espada com sol na guarda apoiada no chão. Emissivo ouro-branco.
- `lider_dos_demonios.py`: o Líder dos Demônios (5,1 m): carne e ferro negro com rachaduras de lava, chifres enormes,
  asas de morcego rasgadas, garras, queixo erguido. Emissivo vermelho-lava.
- Só `idle` (laço: respiração, asas, pano, brilho pulsando, centelhas/brasas subindo), `talk` (fala com a mão aberta)
  e `point` (aponta para o jogador). Sem andar, ataque, dano ou morte. Quadro 640 px.
- Quadros grandes: `BRUTO=1` faz o `render.py` gravar os brutos em 1x (o `process.py` aceita igual).

      BRUTO=1 AMOSTRAS=20 /opt/bpy42/bin/python render.py -- lider_dos_anjos /tmp/brutos/lider_dos_anjos
      python3 process.py /tmp/brutos/lider_dos_anjos /mnt/project-files/assets/monstros/lider_dos_anjos 56 2.2
      (demônio: sombra 2.4)
      /opt/bpy42/bin/python retrato_lorde.py -- lider_dos_anjos /mnt/project-files/entregas/warlord/lordes/lider_dos_anjos_retrato.png 1200 64

- `retrato_lorde.py`: retrato de corpo inteiro para a tela de carregamento (perspectiva de baixo, 3/4, fundo
  transparente, recortado com a altura pedida).

### A Torre (Repetidora do Granizo, Congregação da Portadora)

Lore e lista em `design/mapas/a_torre/conceito.md`.

- `sintonizado.py`: Sintonizado (A Torre, Congregação da Portadora): acólito curvado de cabeça inclinada "escutando", casaco longo de borracha preta rachada com remendos e fita isolante, crânio raspado com fones de baquelite aparafusados, boca trocada por grade redonda de alto-falante presa em tiras de couro, antenas de arame saindo da gola, 3 válvulas acesas no peitoral de couro (laranja de válvula, o único brilho), luvas de borracha e chave inglesa isolada. Idle com o tique de escuta (mão ao fone); na morte leva as mãos aos fones, cai de joelhos e tomba. Quadro 192 px, âncora (96, 145.9). Variantes:
  - `sintonizado_locutor` (1,03x, quadro 208 px): corneta de latão amassado nas costas num arnês, sobretudo-batina, estola de fita de rolo, microfone de mão. `attack` = grita a estática no microfone (cone).
  - `guarda_fios` (elite, 1,1x e mais largo, quadro 224 px): capacete de linha com lanterna, macacão de lona, luvas de eletricista, cinto de ferramentas, esporas de poste, escudo de chapa de transformador com isoladores e a senoide, chicote de cabo de alta tensão (ossos `w1..w5` por `aim`). `attack` = chicotada por cima do ombro.
  Regerar: `blender -b -P render.py -- sintonizado[:variante] /tmp/brutos/X` e `python3 process.py /tmp/brutos/X ../../../assets/monstros/X 42 .6` (locutor 42 .65, guarda_fios 44 .75). `RESUME=1` retoma render interrompido.
- `receptaculo.py`: Receptáculo (A Torre, andares 3 e 4): um Sintonizado que recebeu um Inaudível. Anda de quatro de barriga para cima, cotovelos e joelhos para o alto, cabeça pendurada e virada (`ROLL`); pele cinza com fios de cobre costurados, fones aparafusados, restos do casaco de borracha, costelas abertas como varetas de antena (`rib.L`/`rib.R`) e estática violeta no peito (único emissivo). Quadro 224 px. Variante elite `receptaculo_inchado` (Receptáculo Saturado, 1,35x, quadro 256): pele translúcida com veias de estática, bolhas, válvulas quebradas; a morte incha e estoura como a da `larva_de_carne`. Usa o `SRig` de `inaudivel.py`.
- `inaudivel.py`: os Inaudíveis (andares 4 e 5). Material `static_mat` (núcleo quase preto, bordas acesas, linhas de varredura, chuvisco e faixas vazadas em violeta #b46cff); `SRig` anima `scan`, `flick` e `cut` por quadro. Padrão = `inaudivel` (elite, ~3 m, quadro 320: corcunda, três pares de braços, cantoneiras da torre como costelas, cabeça de molduras concêntricas girando no vazio). Variante `eco_da_estatica` (~1,7 m, quadro 224: braços longos, cabeça de aro de alto-falante arrancado, corpo que se desfaz em fiapos). Morte "perde o sinal": treme, perde faixas, vira um ponto e some; a cabeça física fica no chão.
- Regerar: `blender -b -P render.py -- receptaculo[:receptaculo_inchado] /tmp/brutos/X`, `blender -b -P render.py -- inaudivel[:eco_da_estatica] /tmp/brutos/X`; process com 44 .9 (receptaculo), 44 1.1 (inchado), 44 .6 (eco), 48 .9 (inaudivel).
- `ferrabras.py`: Ferrabrás, o Guarda-Linhas (A Torre, chefe do andar 1, saída `ferrabras_guarda_linhas`): gigante de 3,0 m (`SCALE` 1,68), macacão de lona remendado, capacete de linha com lanterna morta, luvas de borracha até o cotovelo, esporas de poste, cinto de ferramentas e um transformador de poste nas costas. Dois cabos de alta tensão saem dele e viram correntes de 8 elos-osso por lado (`cL1..cL8`+`tipL`, `cR1..cR8`+`tipR`), apontados pelo `CRig` com os modos `drape`, `fling` e `dir`. Único brilho: laranja de válvula nas pontas de cobre e no núcleo da bobina (`tipL`/`tipR`/`coil`). Extras: spin, lunge, cast, summon, roar. Quadro 512 px. `AMOSTRAS=24 blender -b -P render.py -- ferrabras:ferrabras_guarda_linhas /tmp/brutos/X` e `python3 process.py /tmp/brutos/X <saida> 48 1.3`.
- `brasilia.py`: Madre Brasília, a Voz da Portadora (chefe do andar 2, saída `madre_brasilia`): locutora de 2,3 m (`SCALE` 1,17), vestido de luto com saia plissada (painéis `sk*` + `settle()` da carpideira), ombreiras de baquelite, corneta no peito, véu-gaiola de malha de alto-falante (osso `grille`), colar de 7 válvulas (osso `valves`, o único brilho) e microfone de pedestal de latão como cajado (osso `stand`). Extras: spin, lunge, cast, summon, roar. Quadro 416 px. `AMOSTRAS=24 blender -b -P render.py -- brasilia:madre_brasilia /tmp/brutos/X` e `python3 process.py /tmp/brutos/X <saida> 48 1.0`.
- O sufixo `:variante` é obrigatório nos chefes (dá o nome das folhas e do meta.json). `RESUME=1` retoma; `teste` como 3º argumento faz conferência rápida.
- `telegrafista.py`: O Telegrafista (`o_telegrafista`, andar 3): operador de colete vinho e viseira verde fundido à cadeira giratória e à mesa de telégrafo (4 manipuladores, receptor de 6 válvulas acesas: único emissivo), que anda sobre 6 pernas de aranha de viga rebitada vermelha e branca; dois braços de latão, antena dipolo e fita perfurada saindo da boca. Rig `TRig` (chave `lift`): `hips` chassi, `swivel` cadeira, pernas `leg{FL,ML,BL,FR,MR,BR}.{1,2,3}`, fita `t1..t5`, `coil`, `spark`, `lever`. Quadro 512 px. Também guarda os utilitários `bx`, `cyl`, `ball`, `ring`, `sag`, `strip`, `glow` (usados pelo `malaquias.py`).
- `malaquias.py`: Malaquias, o Ouvinte Cego (`malaquias_ouvinte_cego`, andar 4): ~2,7 m, sobretudo de borracha rachada, faixa ensanguentada nos olhos, cornetas acústicas costuradas nas orelhas (`horn.L/R`), parabólica enferrujada nas costas que gira sobre a cabeça no lunge (`dish`), cajado-antena telescópico com a válvula no topo (`staff`, único emissivo). Quadro 448 px.
- Regerar os chefes da Torre: `blender -b -P render.py -- <modulo>:<id> /tmp/brutos/<id>` (o `:id` é obrigatório) e `python3 process.py /tmp/brutos/<id> ../../../assets/monstros/<id> 48 <sombra>` (Telegrafista 2.2, Malaquias 1.0). `RESUME=1` retoma; `teste` como 3º argumento faz conferência rápida.
- `baraquiel.py`: Baraquiel, o Que Respondeu (chefe final da raid "A Torre", nv 30): um Inaudível de ~4 m dentro da carcaça rachada do anjo do relâmpago. Armadura de ouro velho com fissuras de Voronoi acesas em violeta; por dentro, estática `static_mat` (grão 4D por quadro, faixa de varredura). Meia máscara partida (osso `mask`, abre no roar), auréola-antena de cobre com isoladores (`halo_fx`), asas de treliça com penas de estática, sem pernas (fiapos `tr1..tr3`), lança-para-raios (`spear`, `bolt`), raios da Chuva de Estática (`rain0..5`) e fenda (`rift`). Rig `BRig` com canais de material na chave `fx` (`amp`, `dis`, `band`, `hot`). Extras: spin, lunge, cast, summon, roar; na death a armadura vazia desaba. Variante `baraquiel_sinal_pleno` (fase 3): mais estática, asas mais acesas, três antenas girando (`halo2`, `halo3`). Quadro 576 px, render em 1x (`RES=100` volta ao 2x). `AMOSTRAS=24 blender -b -P render.py -- baraquiel[:baraquiel_sinal_pleno] /tmp/brutos/X` e `python3 process.py /tmp/brutos/X <saida> 64 1.6`.
