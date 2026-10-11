# O Agrak: coliseu, plateia e narrador

Plano para as threads **Cenário, prédios e dungeon** (arte), **Level design** (layout do mapa `agrak`),
**Personagens 3D / Monstros** (Pedro e os leões) e **Som e música**. Regras e números ficam em
`README.md` e `dados.json`. Pela regra da casa, layout e arte nova passam por uma imagem para o Jefin
aprovar antes de entrar no jogo.

## Ideia em uma frase

Um estádio de futebol enterrado na areia até a marquise, com o gramado escavado de volta e transformado em
fosso de arena: **o coliseu do fim do mundo é um estádio que a cidade esqueceu**. Coerente com São Lázaro
("a rua de hoje é o telhado de ontem") e sem clichê de coliseu romano de mármore.

## O mapa `agrak` (instância própria, como os andares da cripta)

- Gerado como os outros mapas (`design/mapas/fontes/`, nunca à mão). Sugestão de tamanho: 44 x 36 tiles.
- **Arena (o fosso)**: oval de 30 x 22 tiles, chão de areia batida escura com **linhas de cal do antigo campo**
  ainda aparecendo (meio-campo, grande área) e manchas de sangue velho. Sem obstáculo no meio: o Pião do Golias
  precisa de espaço. Quatro pilares baixos de entulho perto do muro dão cobertura contra o Bote dos leões.
- **Círculo de Ferro** no centro: anel de trilho de bonde cravado na areia (raio 3,5), onde a Chamada prende os
  gladiadores.
- **Muro do fosso** (3 m, a mureta da antiga arquibancada inferior) com borda de estacas e arame. É a borda
  do mapa: ninguém sai.
- **Três portões** no muro, com grade de ferro que sobe e desce (porta do mapa, `bloq` 2):
  - **Portão dos Gladiadores** (sul): por onde os jogadores entram; vira o túnel dos derrotados.
  - **Portão dos Leões** (norte): três jaulas de sucata visíveis atrás da grade.
  - **Portão do Gigante** (leste): o maior, com guincho de corrente e duas correntes grossas penduradas.
- **Camarote do Pedro** (oeste): em cima do **placar** enferrujado do estádio (letreiro "SÃO LÁZARO 0 x 0",
  números de lata), com o megafone e dois braseiros. Ao lado, o **Camarote dos Derrotados**, onde os espectadores
  esperam (zona segura, fora do fosso, vista para a luta).
- **Plateia** em volta, nas arquibancadas de cima: degraus de concreto rachado, faixas de pano rasgadas com nomes
  de campeões, gente amontoada. É cenário, não andável.

## Arte nova (Cenário)

Mesmo vocabulário do deserto (concreto enterrado, sucata, lona, latão, fogo), luz de braseiro, névoa baixa.
O verde do Amargo só aparece no Anel do Amargo da luta final.

| Peça | O que é |
|---|---|
| `piso_arena` | areia batida escura, variações com linha de cal, mancha de sangue, marca de arrasto |
| `arquibancada_a/b/c` | trechos de arquibancada curva (3 alturas de degrau), concreto rachado, ferragem exposta |
| `plateia_a/b/c` | multidão em silhueta para pôr nos degraus: sobreviventes de capuz, lampiões, braços erguidos; **4 quadros** de animação (vibrar, braços sobem quando alguém morre) |
| `portao_grade` | portão de grade com estado fechado/aberto (como a grade das arenas da cripta) |
| `jaula_leao` | jaula de sucata com palha e ossos |
| `guincho_corrente` | guincho do Portão do Gigante |
| `placar_camarote` | placar do estádio com camarote em cima (peça grande, como a `capela_enterrada`) |
| `circulo_ferro` | anel de trilho no chão |
| `faixa_campeao` | faixa de pano pendurada com nome pintado (3 variações) |
| `braseiro_holofote` | holofote de estádio morto virado braseiro (luz `luz_fogo`) |
| `pilar_entulho` | pilar baixo de entulho para cobertura |

Luzes: braseiros no muro a cada ~6 tiles e nos camarotes; nada de luz ambiente forte.

## Caim e Abel, o Ogro de Duas Cabeças (narrador e inscrição)

Definido pelo Jefin: **o narrador é um ogro de duas cabeças**. Os nomes são escolha minha (trocar é só mudar o
texto): as cabeças são irmãs e se odeiam, então a narração vira dupla de locutores.

- **Quem é:** um sobrevivente que o Amargo inchou até virar ogro (3 m), com uma segunda cabeça que nasceu do
  ombro. **Caim** (a cabeça da direita, grande, testa baixa, dentes tortos) berra os anúncios; **Abel** (a da
  esquerda, menor, careca, olho leitoso, sorriso fino) comenta com deboche e corrige o irmão. Neutros: no Agrak
  qualquer facção paga ingresso. Criam os leões e mandam no portão do Golias.
- **Corpo e roupa:** barrigudo, braços longos, pele cinza-oliva cheia de verrugas e remendos. Casaca de domador
  vermelha desbotada que não fecha na barriga, dragonas de latão, gola dupla costurada para as duas cabeças. Caim
  usa um **megafone de latão** preso na mandíbula por correias; Abel usa uma **cartola amassada com uma vela** na
  fita (o único emissivo: a chama). Bengala-chicote do tamanho de uma lança, cinturão com as chaves das jaulas.
  Silhueta: duas cabeças de alturas diferentes + megafone + cartola, inconfundível de longe.
- **Sprite:** quadro grande como o Golias. Animações `idle` (as cabeças se olham e se ignoram), `anunciar` (Caim
  ergue o megafone, braço com a bengala no alto), `discutir` (as cabeças batem uma na outra), `rir` (os dois juntos,
  a barriga balança). Thread Personagens 3D faz; mostrar ao Jefin antes.
- Fica em dois lugares: na **Barraca do Ogro** (área inicial, perto da praça da Paróquia de São Lázaro, em zona
  segura; Level design escolhe o ponto), onde inscreve, e no **Camarote** do Agrak (em cima do placar) durante o
  evento.
- **Cartaz do Agrak**: objeto clicável (pôster colado em tapume, com o desenho do ogro) no Acampamento da Vela e na
  Capela de São Lázaro; inscreve no evento sem ir até o ogro e tem a opção "Ir ao Agrak" (leva à ermida do Pedro).

### Falas de Caim e Abel (para Missões, que cuida de `dialogos.json`)

- Chamada. Caim: "SENHORAS, SENHORES E COISAS QUE UM DIA FORAM GENTE! BEM-VINDOS AO AGRAK!" Abel: "Ele ensaiou isso a semana toda."
- Apresentando cada um. Caim: "DA {FACCAO}, UM {CLASSE}: {NOME}!" Abel: "Aposto dois dentes que não passa dos leões."
- Leões. Caim: "SOLTEM OS LEÕES!" Abel: "Eles não comem desde a última trombeta. Nem eu."
- Leão morto. Caim: "UM GATINHO A MENOS!" Abel: "Era o meu favorito. Anota o nome desse aí."
- Golias. Caim: "ELE GIRA, VOCÊS SANGRAM. GOOOLIAS!" Abel: "Já foi gente. Igual a nós. Mais ou menos."
- Pião. Caim: "OLHA O PIÃO!" Abel: "Quem ficar no meio vira farinha. Farinha boa, pelo menos."
- Golias morto. Caim: "DERRUBARAM O GIGANTE!" Abel: "Agora a parte que a plateia pagou pra ver: um contra o outro."
- Anel do Amargo. Caim: "O AMARGO TÁ ENTRANDO!" Abel: "Andem logo, que a plateia tem hora."
- Vencedor. Caim: "{NOME}! DO PÓ VIEMOS E VOCÊ FICOU DE PÉ!" Abel: "Uma Ficha de Sangue. Leve ao Pedro antes que alguém leve você."
- Sem vencedor. Caim: "O AGRAK COMEU TODO MUNDO!" Abel: "Voltem amanhã com mais carne."
- Na barraca. Abel: "Cem de ouro pra entrar na lista." Caim: "E A SUA VIDA!" Abel: "O ouro a gente devolve se não tiver luta. A vida, o Pedro."

## Pedro, o Penitente (loja de PvP)

Definido pelo Jefin: chama-se **Pedro**, é o NPC dos itens de PvP (troca Fichas de Sangue por armadura e arma), um
demônio convertido à luz, um penitente, com aura divina, pele branca, algo como um Buda ou o Netero, mas ainda
assim um ex-demônio.

- **História:** foi o carrasco da Legião Blasfema. Quando o general sumiu e o Juízo travou, negou o Inferno três
  vezes numa noite (daí o nome que tomou) e ficou de joelhos no gramado do estádio até a pele queimar de branco.
  Vive na **Ermida do Pedro**, um nicho de velas no corredor do Portão dos Gladiadores, debaixo da arquibancada
  (zona segura do Agrak, aberta o tempo todo). Vende a Couraça do Agrak e as armas por fichas, e é a luz dele que
  levanta os derrotados do evento. Fala manso e brinca como um velho mestre.
- **Corpo:** demônio alto (2,4 m) e pesado, mas sereno: careca, pele **branca de giz** com as marcas e runas
  demoníacas antigas cicatrizadas em relevo, orelhas compridas de Buda, sobrancelhas e **bigode brancos e longos**
  caindo até o peito (o toque Netero), olhos fechados ou semicerrados. O que sobrou do demônio: **chifres serrados**
  com tampas de ouro velho, cauda enrolada na cintura servindo de cinto, tocos de asa queimados nas costas, unhas
  pretas, pés com casco.
- **Roupa:** túnica de penitente de pano de saco amarrada com corda, um ombro de fora, manto rasgado; rosário
  grande feito de pedaços dos próprios chifres e da corrente que usava como carrasco; descalço nos cascos. Sem armadura.
- **Aura:** a única cor que brilha nele é o **dourado** (pontos pequenos: um halo fino e quebrado atrás da cabeça,
  as runas cicatrizadas acendendo de leve quando ele fala). Rim light dourado.
- **Sprite:** NPC na escala do Golias (quadro grande), animações `idle` (respira, contas do rosário passando nos
  dedos), `abencoar` (abre os braços sobre o comprador, o halo acende), `rezar` (mãos juntas, para quando um gladiador cai e é
  levantado) e `rir` (ri com a barriga, bem Netero). Thread Personagens 3D faz; mostrar ao Jefin antes.
- **Ermida** (Cenário): nicho baixo de concreto com velas derretidas, esteira de palha, as peças da Couraça do
  Agrak penduradas em ganchos e as seis armas encostadas; a luz dourada dele é o que ilumina o corredor.

### Falas do Pedro

- Saudação: "Sente, filho. Eu já matei mais gente do que esse estádio comporta. Hoje só vendo couro e reza."
- Loja: "Quatro fichas por peça, dez pela arma. Sangue por ferro: é a única troca honesta que sobrou."
- Sem fichas: "Volte com sangue na mão, não no rosto."
- Ao comprar: "Ho ho! Couro de leão fica melhor em você do que no leão."
- Gladiador levantado no evento: "Levanta, filho. Aqui ninguém morre. Só perde."
- Sobre o passado: "Neguei o Inferno três vezes numa noite. Ele não respondeu nenhuma. Foi assim que eu soube."

## Monstros (thread Monstros e chefes)

- **Golias**: módulo `tools/sprite-pipeline/monstros/golias.py` feito nesta thread (prévia mostrada ao Jefin).
  Animações: `idle`, `walk`, `attack`, `spin_start`, `spin` (loop), `spin_end`, `roar`, `hit`, `death`.
  Quadro 512 px (a corrente esticada no Pião tem ~3,7 m de raio). Render final em 8 direções depois da aprovação:
  `blender -b -P render.py -- golias /tmp/brutos/golias` e `python3 process.py /tmp/brutos/golias
  /mnt/project-files/assets/monstros/golias 48 1.4`.
- **Leão do Amargo**: módulo novo sobre `quad.py` (mesma base do Cão de Vala), com 3 variantes estilo MU:
  `maior` (Sansão, 1,3x, juba de cerdas de crosta), `leoa` (Dalila, sem juba, mais esguia, cicatrizes) e `velho`
  (Nabucodonosor, juba grisalha, um olho leitoso, placas de sucata parafusadas). Pele careca em placas, olhos
  verde-Amargo pequenos. Animações: `idle`, `walk`, `run`, `attack`, `leap` (como o `leap` do cão, o jogo
  desloca), `roar`, `hit`, `death`. Pela regra dos monstros, mostrar 1 leão antes das variantes.

## Efeitos e som

- Efeitos (thread Efeitos visuais): `piao_poeira` (anel de poeira e faíscas em volta do Golias, loop, por cima
  do sprite), `piao_telegrafo` (anel vermelho que segue o chefe), `anel_amargo` (parede de névoa verde que
  fecha), `chuva_petalas` (coroação), `coisas_na_areia` (plateia jogando lixo no respiro).
- Som (thread Som e música): multidão em loop (murmúrio), urro da plateia (morte, chefe solto, vitória),
  "A-GRAAAK!" em coro, grade do portão, guincho de corrente, corrente girando em loop para o Pião, rugido de leão
  (3 vozes), duas vozes para o ogro, uma metálica de megafone (Caim) e uma rouca e baixa (Abel), só o timbre (as falas são texto), voz grave e mansa com eco para o Pedro e sino curto quando ele levanta um derrotado, música de arena
  (tambores e metal batido).
