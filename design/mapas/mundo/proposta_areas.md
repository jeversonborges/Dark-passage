# DARK PASSAGE: áreas coesas e mapa-múndi (proposta v0.1)

> Pedido do Jefin (05/10/2026): "áreas mais coesas, tipo MU, que tem Lorencia, mapas parecidos, ele todo parecido".
> Esta proposta não muda nenhum mapa ainda. Primeiro o Jefin aprova a direção; depois eu refaço o layout do deserto e desenho as áreas seguintes.

## 1. A regra Lorencia

Em MU, Lorencia é um lugar só: o mesmo gramado, o mesmo muro de pedra, a mesma luz, do portão da cidade até a última árvore. Devias é neve de ponta a ponta, e Noria é floresta de ponta a ponta. Você reconhece a área por um print de qualquer canto dela.

Daqui para a frente, toda área do DARK PASSAGE segue cinco regras:

1. **Um chão.** O piso-base cobre pelo menos 70% da área. Há no máximo dois pisos de destaque, e eles precisam ser o mesmo material em outro estado (areia → areia vitrificada; não "areia → laje de capela").
2. **Uma paleta.** São três cores de base e uma cor que brilha. A cor que brilha é a assinatura da área: no deserto é o verde do Amargo.
3. **Um vocabulário.** Cada área tem uns 20 props, as "palavras" dela, que aparecem em todas as zonas. Uma zona se diferencia da outra pela densidade e pela arrumação desses props, e por **um marco** visível de longe. Ela não ganha um kit próprio.
4. **Um céu.** A luz e o clima são os mesmos em toda a área. O que muda é a intensidade.
5. **Uma família de monstros.** Os mobs de uma área vêm da mesma origem na lore e têm um ar de parentesco, como as variantes do MU (mesma base, outra cor, outro equipamento).

## 2. O Deserto de Absinto hoje, e o que muda

**O problema.** O mapa aprovado tem 11 zonas e **21 tipos de chão**. A família da areia (areia, duna baixa, duna alta) cobre só 42% do mapa jogável. O resto é dividido entre laje de capela, chapa de matadouro, chão de cemitério, terra de vala, chão de mata, calçamento, cinza, brejo e musgo. Cada zona trouxe o seu próprio chão, e por isso o deserto parece 11 mapas colados.

**A identidade única do deserto.**

| | Regra |
|---|---|
| Chão-base (≥ 75%) | Areia cinza-ocre com veios verdes do Amargo, com dunas baixas |
| Destaques (máx. 2) | Areia vitrificada (onde a batalha queimou) e leito rachado (o rio seco) |
| Especial | A água amarga do rio, verde e brilhante, só no leito (escolha do Jefin em 06/10: "Oásis do rio amargo") |
| Paleta | Ocre-cinza, ferrugem, osso. A cor que brilha é o verde Amargo. A luz quente vem só dos lampiões dos sobreviventes |
| Céu | Noite de lua fria com o pó do Amargo caindo, igual em toda a área. Na borda, a tempestade só fica mais forte |
| Vocabulário (20 props) | prédio enterrado, chaminé enterrada, mastro de poste, trilho e bonde-veleiro, duna, lápide meio enterrada, árvore morta, arbusto seco, cardo, cacto seco, planta mutante, ossada, placa de radiação, tambor radioativo, tenda de lona, barraco de sucata, tonel de fogo, varal, sacos de areia, vidro estilhaçado |

**Como cada zona fica dentro dessa regra.** As zonas deixam de trazer chão próprio. Cada uma vira um arranjo diferente das mesmas palavras, com um marco.

| Zona | Antes | Depois (mesma areia) | Marco |
|---|---|---|---|
| Acampamento da Vela | terra batida + calçamento | areia pisada, tendas, sacos de areia | a lâmpada de arco |
| Capela de São Lázaro | laje de capela | areia; a capela enterrada até o coro | a rosácea virada em porta |
| Campos de Cinza | cinza + vidro | areia vitrificada (o destaque) com cinza salpicada | a cratera e o estandarte |
| A Vala | terra de vala | areia revolvida, covas abertas | a vala aberta |
| Bairro Afogado | calçamento + entulho | areia; telhados e janelas saindo da duna | a torre do relógio enterrada |
| Cemitério | chão de cemitério | areia; mar de lápides meio enterradas | a torre do sino |
| Mata dos Cardos | musgo + brejo | areia; moitas de cardo mais densas | o caldeirão da Mãe Cardo |
| Rio Amargo (oásis) | leito + lama + brejo | um fio de água amarga correndo no leito rachado (o outro destaque), a única água do deserto, com vida torta só nas margens: flor-de-absinto, juncos e planta mutante | a Ponte do Bonde |
| Bosque das Viúvas | chão de mata | areia; árvores mortas mais densas | a árvore dos enforcados |
| Abatedouro Carniça | chapa de matadouro | areia; o frigorífico enterrado | as chaminés |
| Borda (tempestade) | areia | areia, com a tempestade mais forte | ossadas de viajantes |

O chão de matadouro, de capela e de cripta continua existindo, só que **dentro** dos prédios e na dungeon, onde faz sentido. O resultado são 4 pisos ao ar livre em vez de 21.

**Mobs: menos Diablo, mais WoW** (regra do Jefin de 05/10). Cada grupo do mapa ganha um campo `temperamento`:

- **neutro**: cuida da própria vida e só reage se apanhar. Exemplos: porcos fuçando, Não-Julgados esperando o Juízo, corvos comendo.
- **territorial**: só ataca quem chega perto do ninho, da toca ou do cadáver que está guardando, num raio curto (3 a 4 m).
- **agressivo**: só onde a lore manda, como os açougueiros do Abatedouro e a matilha da Vala à noite.

As metas para o deserto revisado são:
- pelo menos 50% dos mobs neutros;
- grupos de 1 a 3;
- nenhum mob a menos de 15 m de uma zona segura;
- nenhum grupo a menos de 8 m de outro (sem puxar em cadeia);
- os primeiros 5 minutos fora do acampamento só com neutros.

Os números de aggro continuam com a thread de Combate. O mapa diz quem é neutro e onde.

**Beleza no fim do mundo.** O Jefin pediu isso em 05/10: "mesmo que seja fim do mundo, pode ser belo". A beleza do deserto vem do mesmo Amargo que o envenena e do cuidado dos sobreviventes. Ela não é decoração solta: cada elemento tem um motivo na lore.

- **Flor-de-absinto.** É uma flor que come o Amargo. Ela brota em touceiras na beira do leito e das poças, e à noite as pétalas brilham verde-água. É a única coisa viva e bonita do lugar, e por isso os sobreviventes a plantam em latas na porta de casa. No jogo, onde ela floresce o contador estala menos.
- **Varais de lanternas.** Os sobreviventes penduram lanternas de lata entre os mastros e as janelas dos prédios enterrados. Visto de longe, o acampamento é um cordão de luz quente no meio do azul da lua.
- **Os campos de vidro.** Onde a batalha queimou, a areia virou vidro, e ele reflete a lua e o brilho verde. Andar ali à noite é como andar sobre um lago parado.
- **Sinos de vidro.** São mensageiros do vento feitos com o vidro derretido, pendurados nos mastros e nas árvores mortas. O som entra no ambiente do mapa.
- **As velas do bonde.** As velas de lona são remendadas com retalhos de cores diferentes, e cada remendo foi doado por uma família.
- **O céu.** É uma noite limpa e estrelada, e de vez em quando passa uma aurora verde do Amargo. A noite fria e o verde no alto são a assinatura do Deserto.

**Pedido para a thread "Cenário, prédios e dungeon"** (é tudo novo, nada existe no kit):

| Prop | Uso |
|---|---|
| `flor_absinto` (3 variantes) | Touceiras luminosas na beira do leito, das poças e nas latas da porta |
| `flor_absinto_lata` | Flor plantada em lata ou bota velha, na porta das casas e do acampamento |
| `varal_lanternas` (2 tamanhos) | Cordão de lanternas de lata entre mastros e janelas |
| `sinos_de_vidro` | Mensageiro de vento de vidro derretido, nos mastros e nas árvores |
| `bonde_veleiro_remendado` | Variante do bonde com a vela de retalhos coloridos |
| `espelho_de_vidro` (piso de destaque) | Vidro liso e espelhado dentro dos Campos de Cinza |

Para a thread de efeitos visuais: a aurora verde no céu, o pólen luminoso das flores e o brilho que treme no vidro.

**Imagem:** `imagens/01_deserto_de_absinto.png`. A imagem já mostra as flores e os varais de lanternas.

## 3. O mapa-múndi: uma área por trombeta

A lore já entrega a estrutura. As sete trombetas foram escondidas em sete pontos da Terra, e cada uma deixou uma praga diferente. **Cada área do jogo é a terra de uma trombeta**, e por isso cada uma tem uma cara só, como as áreas do MU. A Linha 7 do bonde-veleiro liga as áreas: é o "teleporte" do jogo, com uma estação em cada cidade.

| # | Área | Nível | Trombeta | Em uma frase | Cor que brilha | Cidade (zona segura) | Dungeon |
|---|---|---|---|---|---|---|---|
| 1 | **Deserto de Absinto** | 1 a 15 | 3ª (o pó) e 5ª (enterrada) | Cidade enterrada na areia até o 4º andar | verde Amargo | Acampamento da Vela / Capela | Cripta da Trombeta Calada |
| 2 | **Mata do Granizo** | 15 a 30 | 1ª | Floresta de troncos carbonizados de pé, com granizo de sangue que nunca derrete | vermelho brasa | Carvoaria (vila de carvoeiros sobre palafitas) | Forno das Raízes |
| 3 | **Costa Rubra** | 30 a 45 | 2ª | Mar que virou sangue e coalhou; navios encalhados; a montanha em chamas no horizonte | laranja de enxofre | Porto dos Cascos (cidade dentro de cascos virados) | Ventre da Montanha |
| 4 | **Candelária, a Cidade sem Sol** | 45 a 60 | 4ª | Cidade gótica em noite eterna e geada, onde a luz é moeda | amarelo de lampião | Candelária (a parte acesa) | Gasômetro dos Acendedores |
| 5 | **Planície dos Cavaleiros** | 60 a 80 | 6ª | A carga de duzentos milhões de cavaleiros, petrificada no meio do galope, em chão de enxofre | amarelo enxofre | Acampamento da Ponte Partida | As Correntes do Rio |
| 6 | **Cratera de Absinto** | 80 a 100 | 3ª (a estrela) | A própria estrela caída: cristal verde vivo, a fonte de todo o Amargo | verde vivo | Posto Avançado da Vigília | O Coração da Estrela |

A 7ª trombeta fica de fora de propósito. O Apocalipse diz que, quando ela vai soar, "houve silêncio no céu por meia hora". O conteúdo final, depois do nível 100, guarda esse silêncio para depois.

**Por que essas e não outras.** Cada área sai do texto do Apocalipse, então nenhuma é "a floresta genérica" ou "a neve genérica":

- a 1ª trombeta queima árvores com granizo e fogo misturados com sangue;
- a 2ª joga uma montanha ardendo no mar e o mar vira sangue;
- a 4ª apaga um terço do sol;
- a 6ª solta os quatro anjos do rio e um exército de cavaleiros com cabeça de leão que soltam fogo e enxofre.

O tom continua o nosso: sobreviventes que se viram no meio da praga. Ninguém é herói de cartaz.

### 3.1 Mata do Granizo (nível 15 a 30)

- **Lore:** a primeira trombeta. Granizo e fogo misturados com sangue caíram sobre a floresta, e um terço das árvores queimou de pé. O granizo de sangue não derrete: são pedras de gelo vermelho que ficam no chão como frutas podres. Os sobreviventes viraram **carvoeiros**. Vendem o carvão das árvores mortas e moram em palafitas para fugir das brasas que ainda correm sob a cinza.
- **Chão:** cinza preta fofa (base). Destaques: brasa exposta (rachaduras laranja) e crosta de granizo vermelho.
- **Paleta:** carvão, cinza clara, vermelho sangue. Brilha: laranja brasa.
- **Vocabulário:** tronco carbonizado de pé, tronco tombado, toco em brasa, pedra de granizo rubro, palafita, forno de carvão (meda de barro), carroça de carvão, trilha de tábuas, cerca de galhos queimados, ninho de corvo no tronco, cogumelo de cinza.
- **Marcos:** a Árvore-Mãe (uma sequoia carbonizada oca, com a vila dentro), o Forno das Raízes (dungeon) e o lago de granizo.
- **Mobs (família "o que comeu a floresta"):** cervo de carvão (neutro), javali-brasa (territorial), carvoeiro enlouquecido (agressivo, perto dos fornos abandonados), enxame de fagulhas (neutro até ser tocado), ent-de-cinza (elite, neutro: só acorda se você corta a árvore dele).

### 3.2 Costa Rubra (nível 30 a 45)

- **Lore:** a segunda trombeta. Uma montanha ardendo foi atirada no mar, e um terço do mar virou sangue. Aqui o sangue coalhou numa crosta escura onde dá para andar, com rachaduras de onde sobe vapor. Um terço dos navios naufragou, e o mar seco os deixou encalhados de quilha para cima. A montanha ainda arde no horizonte, sempre visível. Os sobreviventes moram dentro dos cascos virados.
- **Chão:** crosta de sangue coalhado (base). Destaques: sal ferruginoso e poça viva de sangue.
- **Paleta:** ferrugem escura, osso, sal. Brilha: laranja de enxofre (a montanha e o vapor).
- **Vocabulário:** casco virado, mastro tombado, âncora, corrente, rede de pesca, costela de baleia, farol apagado, cais de madeira, barril, boia, guindaste de porto, ossada de peixe gigante.
- **Marcos:** o Farol Cego, o Cemitério de Quilhas e a montanha em chamas no horizonte.
- **Mobs (família "o que o mar devolveu"):** caranguejo de coágulo (neutro), afogado de sal (neutro, de dia), gaivota-carniça (territorial no ninho), pescador de anzol (agressivo), leviatã de crosta (elite, territorial).

### 3.3 Candelária, a Cidade sem Sol (nível 45 a 60)

- **Lore:** a quarta trombeta apagou um terço do sol, e sobre Candelária nunca mais amanheceu. Sem sol, caiu o frio: geada eterna e neve de fuligem. A luz virou moeda. Os **acendedores** mantêm as ruas acesas a gás, e quem não paga o lampião vive no escuro, onde as coisas da noite caçam. É a Devias do nosso jogo, só que gótica e steampunk.
- **Chão:** paralelepípedo com geada (base). Destaques: neve de fuligem e gelo negro.
- **Paleta:** azul-noite, ferro, branco de geada. Brilha: amarelo de lampião a gás.
- **Vocabulário:** poste de gás, sobrado gótico de 3 andares, chaminé, cano de gás, grade de ferro, gasômetro, relógio de rua, carrinho de acendedor, banco congelado, estátua coberta de gelo, escada de incêndio.
- **Marcos:** a Catedral Apagada (o único prédio sem nenhuma luz), o Gasômetro e a Praça dos Mil Lampiões.
- **Mobs (família "o que vive no escuro"):** mariposa de lampião (neutra, atraída pela luz), mendigo de geada (neutro), sombra roubada (agressiva só fora da luz: a luz dos postes é zona segura de verdade), cão de fuligem (territorial), acendedor caído (elite).

### 3.4 Planície dos Cavaleiros (nível 60 a 80)

- **Lore:** a sexta trombeta soltou os quatro anjos presos no grande rio, e com eles um exército de duzentos milhões de cavaleiros. Os cavalos têm cabeça de leão e soltam fogo, fumaça e enxofre. A Vigília calou essa trombeta no meio da carga, e a cavalaria petrificou no galope. É uma planície inteira de estátuas em formação de batalha, que de vez em quando racham e soltam um cavaleiro vivo.
- **Chão:** enxofre amarelo (base). Destaques: basalto preto e rachadura de fumaça.
- **Paleta:** amarelo enxofre, basalto, cinza de fumaça. Brilha: amarelo-fogo das bocas de leão.
- **Vocabulário:** cavaleiro petrificado (em fileiras), lança quebrada, estandarte de pedra, fumarola de enxofre, cratera de fogo, carroça de guerra, corrente gigante, pilar de basalto, tenda rasgada.
- **Marcos:** a Ponte Partida sobre o rio, as Quatro Correntes (onde os anjos estavam presos) e o General de Pedra.
- **Mobs (família "a carga parada"):** cavaleiro desperto (neutro até você tocar uma estátua), leão de enxofre (territorial), mosca de fumaça (neutra), arauto da carga (agressivo), anjo acorrentado (elite).

### 3.5 Cratera de Absinto (nível 80 a 100)

- **Lore:** a terceira trombeta soou "longe daqui". Este é o lugar onde a estrela Absinto caiu. A cratera é um anfiteatro de vidro verde, e no centro a estrela ainda pulsa, viva, como um coração de cristal. Todo o Amargo do mundo sai daqui. A Vigília tem um posto avançado na borda, e os Arautos têm uma romaria até o centro.
- **Chão:** vidro verde-escuro rachado (base). Destaques: cristal vivo e pó de Amargo puro.
- **Paleta:** preto vítreo, verde, prata. Brilha: verde vivo (no máximo de toda a jornada).
- **Vocabulário:** cristal de Absinto, rocha vitrificada, andaime da Vigília, guindaste de mineração, contador de radiação, ossadas de peregrino, altar de romaria, trilhos de mina, barraca de chumbo.
- **Marcos:** o Coração da Estrela, a Estrada dos Peregrinos e a Escavação da Vigília.
- **Mobs (família "o que o Amargo criou"):** peregrino de cristal (neutro, em romaria), cão de vidro (territorial), mutante do Amargo (agressivo), larva de estrela (neutra), Absinto Encarnado (chefe de mundo).

## 4. Assets de cenário por área

O kit do deserto já tem 170 objetos e 18 pisos. As áreas novas reaproveitam a base do kit (ferro, madeira, lona, osso, tijolo) e só criam o que dá identidade. A quantidade é uma estimativa.

| Área | Pisos novos | Props novos | Marcos | Céu e efeitos |
|---|---|---|---|---|
| Deserto (revisão) | nenhum (aposenta 17 pisos ao ar livre) | nenhum; só rearranjo | já existem | já existem |
| Mata do Granizo | 3 (cinza preta, brasa, crosta de granizo) | ~18 | 3 | fagulhas, fumaça baixa, granizo caindo |
| Costa Rubra | 3 (crosta de sangue, sal, poça de sangue) | ~18 | 3 | vapor das rachaduras, brilho da montanha |
| Candelária | 3 (paralelepípedo com geada, neve de fuligem, gelo) | ~22 | 3 | neve de fuligem, halo dos lampiões |
| Planície | 3 (enxofre, basalto, fumarola) | ~16 | 3 | fumaça amarela, brasas |
| Cratera | 3 (vidro verde, cristal, pó) | ~16 | 3 | pó verde subindo, pulsação |

**Imagens:** `imagens/02_mata_do_granizo.png` até `imagens/06_cratera_de_absinto.png`, mais `imagens/00_mapa_mundi.png`.

## 5. Spots de farm do deserto (estilo MU)

Pedido do Jefin (05/10): spots no estilo MU, onde se sobe de nível com missões e farm, pensados para a skill em leque do nível 5 com modo automático. Os spots seguem o ritmo "mais WoW":

- Cada spot é uma clareira de 8 a 11 m sem objetos altos, onde cabe o leque.
- Os mobs ficam em grupos de 2 ou 3, espaçados, e um grupo não puxa o outro.
- O respawn é de 15 a 25 s, rápido o bastante para farmar.
- Os spots ficam longe das zonas seguras e fora das estradas principais. Quem só passa por ali não puxa nada.
- Só o Pátio do Abatedouro é agressivo, porque a história pede.
- Perto de cada par de spots há uma fogueira de descanso com o carrinho do Tobias vendendo poção, para a mana acabar no auto sem a poção ficar longe.

| Spot | Nível | Monstros | Temperamento |
|---|---|---|---|
| Covas Rasas | 1 a 3 | 8 carniçais | neutros |
| Telhados dos Corvos | 1 a 3 | 9 corvos | neutros |
| Fosso dos Cães | 2 a 4 | 9 cães e 3 carniçais | cães territoriais (agressivos à noite) |
| Procissão Parada | 3 a 5 | 12 Não-Julgados | neutros (o primeiro spot de leque) |
| Margem das Viúvas | 5 a 7 | 7 Não-Julgados e 5 cães | neutros e territoriais |
| Chiqueiro do Carniça | 5 a 7 | 12 porcos | neutros |
| Pátio do Abatedouro | 7 a 9 | 11 açougueiros e o Capataz | agressivos (a porta da Cripta) |
| Beira da Tempestade | 9 a 12 | 8 Não-Julgados da tempestade e 4 carniçais inchados | neutros e territoriais |

Do nível 3 em diante, os spots seguem o padrão da thread de Combate (`combate.md`, seção 9): 12 monstros, renascimento de 14 s, e as faixas 3 a 5, 5 a 7, 7 a 9 na entrada da Cripta e 9 a 12 no deserto. Os dois spots de nível 1 a 3 são menores, porque o leque só chega no nível 5.

Os dados estão em `design/mapas/spots.json` (nome, nível, monstros, posição, raio, respawn, lore e missão sugerida), para a thread de Missões. A imagem é `design/mapas/spots.png`. O gerador é `fontes/spots.py`. As posições usam o mapa atual; na revisão do layout, os spots com `abrir_clareira` ganham a clareira limpa.
