# Paróquia de São Lázaro · level design v0.3 (Deserto de Absinto)

Proposta de mapa da área inicial (níveis 1 a 8) para o Jefin aprovar. Esta versão segue a lore nova: São Lázaro está enterrada na areia do Deserto de Absinto, e o mundo é aberto, sem parede marcando o limite.

- Visão geral: [visao_geral.png](visao_geral.png)
- Mapa tático com mobs, NPCs, baús e trilhas: [mapa_tatico.png](mapa_tatico.png)
- Dados no formato do jogo: [area_inicial.json](area_inicial.json)
- Fontes que geram tudo: `fontes/layout.py` (mapa) e `fontes/render.py` (imagens). Rode `python3 layout.py && python3 render.py` (precisa de numpy, scipy e pillow). Edite o `layout.py` e gere de novo em vez de mexer no JSON à mão.

As imagens são uma planta de level design. A arte final vem do kit de ambiente.

## O que mudou em relação à prévia

| Pedido | O que foi feito |
|---|---|
| Mob em excesso | 43 mobs em 48×48 viraram 76 mobs numa área jogável de 120×120, quase um quarto da densidade. Cada grupo tem de 1 a 4 monstros e um motivo ligado à lore, e fica longe das estradas principais. |
| Faltavam caminhos | São 14 trilhas com nome, duas estradas de pedra e os trilhos da Linha 7. O rio tem duas pontes e um vau, e sempre existe mais de um caminho até cada zona. |
| Faltavam vegetação, props e estruturas | São 1912 objetos. Há telhados e chaminés saindo da areia (o Bairro Afogado), a torre do relógio enterrada, a cúpula de vidro da estação, o bonde-veleiro, a torre do sino, o moinho parado e os chiqueiros. Não há nada verde e vivo: a vegetação é seca e mutante (árvores mortas, arbustos queimados, cardos roxos e plantas mutantes que brilham de verde porque bebem o Amargo). |
| Um rio | O Jordão secou. Sobrou o leito rachado com um canal de lama amarga no fundo, que abre em poças verdes que brilham à noite. Ele vem da tempestade e some no Sumidouro. A lama não se atravessa, então o leito continua dividindo o mapa, e o esgoto do abatedouro deixa a lama vermelha rio abaixo. |
| Ecossistemas imersivos | Cada zona tem piso, flora, fauna de ambiente, névoa, luz, som e um nível de Amargo próprios (detalhes abaixo). |
| Mundo aberto, sem parede | Não há muro em lugar nenhum. Cada lado do mapa termina num obstáculo natural, explicado abaixo. |

> **Coerência com a lore:** a `historia.md` diz que "o rio secou", e aqui ele secou mesmo. O que sobrou é lama com Amargo e o sebo do abatedouro, não água.

## Os limites do mapa (mundo aberto)

O mapa tem 160×160 tiles. A área jogável é o quadrado central de 120×120 (`jogavel` no JSON). Os 20 tiles em volta são uma moldura de cenário bloqueada, que continua o mesmo obstáculo de cada lado. Assim a câmera nunca mostra o fim do mundo: a moldura se dissolve em poeira.

| Lado | Disfarce | Como funciona |
|---|---|---|
| Fundo esquerdo | **Precipício da Cidade Velha** | O chão desabou sobre as ruas enterradas. A beira é recortada, com corda de guarda, guindaste de sucata, placas de aviso e uma ponte rompida. Os trilhos da Linha 7 terminam pendurados no abismo, e lá embaixo aparecem telhados e uma torre. |
| Fundo direito | **Tempestade de Areia e Amargo** | Dá para entrar uns 10 tiles. A visão cai, o contador de Amargo estala e, a partir do nível 7, o Amargo fere. Depois disso vem uma parede de areia. Lá dentro estão os restos da Linha do Impasse, ossadas de quem tentou passar e placas "VOLTE. A AREIA COME.". |
| Frente direita | **Mar de Dunas** | Dunas altas que andam com a maré de areia, com mastros de bonde naufragado e ossadas gigantes. |
| Frente esquerda | **Estrada do Sul engolida** | Dunas baixas, para não tapar a câmera. Uma fila de postes de telégrafo some debaixo da duna. |

Camadas do JSON para o jogo usar:
- `amargo`: um dígito de 0 a 9 por tile. 0 é o ar limpo da Vela, 2 é o deserto comum, a partir de 4 o contador estala e a partir de 7 o Amargo fere. Só a faixa da tempestade e a beira das bordas chegam a 7 ou mais.
- `camera_limite`: até onde a câmera pode ir, que é 6 tiles além da área jogável.
- A zona `tempestade_areia` em `zonas`, para o efeito de névoa e vento.

## Como o jogador anda pelo mapa

```
VIGÍLIA: Acampamento da Vela ─┐                 ┌─ Capela de São Lázaro :ARAUTOS
         (cúpula de vidro)    ▼                 ▼    (enterrada até o coro)
                     Campos de Cinza (1-3) ── Bairro Afogado (1-3, exploração)
                       │                     │
              Trilha da Vala           Rua do Sino / Trilha das Procissões
                       ▼                     ▼
                A Vala (2-4)        Cemitério no Morro do Coveiro (3-5)
                       │                     │
               Vau do Sebo          Ponte dos Enforcados
                       │                     ▼
                       │            Bosque das Viúvas (4-5, mata morta)
                       │                     │ Trilha dos Chiqueiros
                       ▼                     ▼
            Abatedouro Carniça (5-7) ◄── Chiqueiros (4-6)
                       │      ▲
             porta do porão   └── Ponte do Bonde (atalho pelos trilhos da Linha 7)
                       ▼
          Cripta da Trombeta Calada
```

- Os dois spawns ficam em lados opostos dos Campos de Cinza: a Vigília no Acampamento, os Arautos na Capela. Cada base tem os primeiros mobs de nível 1 a poucos passos do portão.
- A Linha 7 é o fio da história. Os trilhos saem do precipício, passam pela estação do acampamento e atravessam o campo da Grande Batalha. No meio fica o bonde tombado, o Marco do Corte, onde Odete partiu o General ao meio. Depois os trilhos cruzam o rio pela Ponte do Bonde e terminam no abatedouro.
- O rio só se atravessa em três pontos. Isso cria gargalos e encontros naturais para o PvP que vem depois.

## Zonas e ecossistemas

| Zona | Nível | Piso | Clima e luz | Vida |
|---|---|---|---|---|
| Acampamento da Vela | seguro | cúpula de vidro da estação, cascalho | ar limpo em volta da Vela (Amargo 0), faíscas, luz azul elétrica | ratos e mariposas |
| Capela de São Lázaro | seguro | adro escavado em volta da igreja enterrada, paredes de saco e tábua | areia escorrendo, chama branca, vitral verde de areia | pombos brancos; cardos em latas; demônios no telhado dos fundos |
| Campos de Cinza | 1 a 3 | cinza e vidro derretido | Amargo caindo como neve verde, vidro estalando | corvos nos postes, ratos entre os soldados mortos |
| Bairro Afogado | 1 a 3 | areia entre telhados | vento nas chaminés, janelas que levam para baixo | ratos, corvos, cães da matilha nos becos |
| A Vala | 2 a 4 | crateras e brejo | maré de areia desenterrando as valas, névoa do brejo | sapos, moscas, uivos |
| Mata dos Cardos | transição | chão de mata | sementes voando | cardos roxos, a única planta que gosta do Amargo |
| Cemitério | 3 a 5 | mar de lápides meio enterradas, com dunas passando por cima | velas, sino rachado; à noite os Não-Julgados brilham verde | corvos nas árvores mortas |
| Rio Amargo | — | leito seco rachado e canal de lama amarga | poças verdes que brilham; lama vermelha abaixo do esgoto | esqueletos de peixe, moscas, juncos secos, plantas mutantes |
| Bosque das Viúvas | 4 a 5 | mata morta na curva do leito | troncos secos de pé, cogumelos e plantas mutantes acesos de verde, poças tóxicas | corujas, mariposas verdes |
| Chiqueiros e Abatedouro | 4 a 7 | chapa e lama; frigorífico enterrado até o 2º andar | fumaça das chaminés, luz de fornalha | moscas, ratos gordos, porcos |

## Monstros: cada grupo no lugar certo

São 76 mobs em 36 grupos, mais o Filho de Cardo, que só aparece na missão. Os níveis seguem as faixas de `design/combate/mobs.json`. As regras:

1. **Nenhum mob sem motivo.** Cada grupo tem um `motivo` no JSON, o mesmo da tabela abaixo.
2. **Espécie certa no ecossistema certo**, conforme `locais.json`. Os Carniçais reviram os mortos dos Campos e cavam a Vala. Os corvos só existem em volta dos ninhos. A matilha mora na Vala e anda pelos becos do Bairro Afogado e pelo bosque. Os Não-Julgados esperam no cemitério e as viúvas no bosque. Os porcos ficam nos chiqueiros e os Açougueiros no abatedouro.
3. **Estradas limpas.** Nenhum grupo comum fica a menos de 4,5 tiles da estrada de pedra ou dos trilhos. As exceções são de propósito: o bonde tombado, o portão do cemitério e o abatedouro, que é fechado.
4. **Respiro.** Grupos vizinhos ficam mais longe um do outro que o raio de aggro, então puxar um não puxa o outro.
5. **Patrulhas de facção** andam por rotas (tracejado roxo no mapa tático). Cada uma só existe para a facção inimiga.

As coordenadas estão na grade de 160×160. A área jogável vai de 20 a 140.

| Zona | Monstro | Nv | Qtd | x, y | Motivo |
|---|---|---|---|---|---|
| Campos de Cinza | Carniçal | 1 | 2 | 58, 55 | Primeiro mob da Vigília. Dois Carniçais cavando a cova rasa de um soldado na beira do campo, à vista do portão leste do acampamento. |
| — | Carniçal | 1 | 2 | 52, 103 | Primeiro mob dos Arautos. Reviram as armaduras caídas no fim do campo, logo abaixo do adro da capela. |
| Campos de Cinza | Corvo de Cinza | 1 | 2 | 48, 67 | Defendem o ninho do poste torto mais perto do acampamento. |
| Campos de Cinza | Corvo de Cinza | 1 | 2 | 48, 98 | Defendem o ninho mais perto da capela. |
| Campos de Cinza | Carniçal | 2 | 3 | 62, 57 | Comendo os mortos que restam no Campo das Penas, onde caíram os anjos. |
| Campos de Cinza | Carniçal | 2 | 2 | 46, 80 | Rondam o poço seco, onde jogaram corpos na noite da batalha. |
| Campos de Cinza | Corvo de Cinza | 2 | 3 | 60, 84 | Ninho do meio do campo, o mais disputado. |
| Campos de Cinza | Carniçal | 3 | 3 | 69, 82 | Bando maior em volta do bonde tombado e do Marco do Corte: ali morreu mais gente e há mais o que comer. |
| Campos de Cinza | Corvo de Cinza | 3 | 3 | 71, 69 | Ninho perto do esconderijo do Tobias (o ninho gigante). Os corvos roubaram as coisas brilhantes que estão no baú. |
| Campos de Cinza | Cão de Vala | 2 | 2 | 37, 69 | Dois cães da matilha que sobem da Vala pelos becos entre os telhados enterrados atrás de ratos. O primeiro Cão de Vala que a Vigília encontra. |
| A Vala | Cão de Vala | 2 | 3 | 74, 42 | Batedores da matilha na entrada da Vala, perto da trilha que vem do acampamento. |
| A Vala | Cão de Vala | 3 | 3 | 81, 53 | Disputam ossos na vala aberta do norte. |
| A Vala | Carniçal | 3 | 2 | 80, 45 | Carniçais cavando a vala do meio; os cães toleram porque eles desenterram comida. |
| A Vala | Cão de Vala | 4 | 4 | 87, 38 | A toca da matilha no bueiro desabado. O maior grupo da Vala; o uivo de fuga chama os outros. |
| Cemitério de São Lázaro | Não-Julgado | 3 | 2 | 73, 102 | Esperando no portão da Rua do Sino, os primeiros que o jogador encontra. |
| Cemitério de São Lázaro | Não-Julgado | 4 | 3 | 82, 116 | A fila dos Não-Julgados, parada de frente para a torre do sino, esperando o Juízo que não veio. |
| Cemitério de São Lázaro | Não-Julgado | 4 | 2 | 86, 102 | Junto às covas abertas de dentro para fora, de onde acabaram de sair. |
| Cemitério de São Lázaro | Não-Julgado | 5 | 2 | 70, 115 | Em volta da Subida da Torre, os mais antigos do cemitério. |
| Cemitério de São Lázaro | Corvo de Cinza | 3 | 2 | 82, 110 | Corvos pousados nas árvores mortas do centro do cemitério. |
| Bosque das Viúvas | Não-Julgado | 4 | 2 | 110, 116 | Viúvas da Grande Batalha que atravessaram a Ponte dos Enforcados e ficaram no bosque. |
| — | Cão de Vala | 4 | 3 | 126, 108 | Matilha que desce o rio comendo o que os porcos deixam; liga a Vala ao abatedouro. |
| — | Corvo de Cinza | 3 | 3 | 116, 104 | Ninho na copa das árvores na saída da ponte. |
| — | Não-Julgado | 5 | 2 | 123, 120 | Guardam a Árvore dos Enforcados e o baú de oferendas aos pés dela. |
| Abatedouro Carniça | Porco Pestilento | 4 | 2 | 116, 81 | Dentro do chiqueiro oeste, o mais perto da trilha. As cercas dão parede para a investida bater e o porco ficar tonto. |
| Abatedouro Carniça | Porco Pestilento | 5 | 2 | 124, 78 | Chiqueiro leste. |
| Abatedouro Carniça | Porco Pestilento | 6 | 2 | 120, 88 | Chiqueiro dos fundos, os porcos mais gordos. |
| Abatedouro Carniça | Açougueiro Oco | 5 | 1 | 112, 62 | Trabalhando no varal de ganchos da fachada oeste, perto da Ponte do Bonde. |
| Rio Amargo | Açougueiro Oco | 6 | 1 | 115, 47 | Carneando no pátio sul, onde chega o Vau do Sebo. |
| Abatedouro Carniça | Porco Pestilento | 6 | 1 | 126, 50 | Porco que escapou do chiqueiro e fuça os restos atrás do galpão. |
| Abatedouro Carniça | Açougueiro Oco | 7 | 1 | 128, 60 | Guarda os tanques de sebo, onde está o baú do Tobias. |
| Abatedouro Carniça | Capataz Gancho (elite) | 7 | 1 | 124, 52 | Elite de fim de área, no pátio do escritório. Fica com a chave do porão da cripta. Renasce em 300 s. |
| Campos de Cinza | Saqueador da Vigília | 4 | 2 | 44, 96 | Saqueadores da Vigília catando sucata no lado da capela. |
| Campos de Cinza | Fanático da Capela | 4 | 2 | 50, 62 | Fanáticos da Capela rondando o lado do acampamento. |
| — | Fanático da Capela | 6 | 2 | 86, 72 | Fanáticos vigiando a cabeceira oeste da Ponte do Bonde. |
| Cemitério de São Lázaro | Saqueador da Vigília | 6 | 2 | 84, 100 | Saqueadores na cabeceira oeste da Ponte dos Enforcados. |
| Cemitério de São Lázaro | Filho de Cardo (raro) | 6 | 1 | 69, 106 | Só aparece na missão s02, quando o caldo é derramado no túmulo de Firmino Cardo. |

## NPCs, baús e objetos

- **Acampamento da Vela:** Odete no posto de comando, Anselmo na tenda (com o baú trancado), Mãe Cardo no caldeirão, Tobias no carrinho e Gaspar na forja.
- **Capela:** Madre Ivone prega num púlpito no adro escavado. Abdiel treina os Arautos em frente à rosácea. Lúcio fica na porta lateral da sacristia. Malfas fica com os demônios no telhado dos fundos.
- **Cemitério:** Simão na porta do mausoléu que serve de casa.
- **Baús de história**, nos pontos que `objetos.json` descreve: o Poste Torto, o anjo sem cabeça, o tanque de sebo (com o som da caixinha de música como pista) e o baú do Anselmo.
- **Baús de mundo**, de recompensa para quem explora: o Barco Afundado do Balseiro, a Arca do Moinho Parado, a Oferenda das Viúvas, a Caixa do Tratador e o Sótão Afogado (entra-se por uma janela na areia). Se a thread de missões quiser, pode passá-los para `objetos.json`.
- **Objetos de missão** nas quantidades certas: 5 ninhos de corvo, 6 Não-Julgados caídos, 8 covas abertas, o túmulo de Firmino Cardo, a torre do sino, o poço seco, a escrivaninha do capataz e a porta do porão.

## Para a thread do jogo (integração)

O mapa foi aprovado pelo Jefin em 2026-10-04. O passo a passo está em `para_o_jogo/INTEGRACAO.md`, e `para_o_jogo/area_inicial.json` já roda no jogo atual.

- Os campos do mapa atual continuam iguais (`name`, `size`, `spawn`, `safe_zone`, `props`, `blocked` e `spawns`), então o jogo já lê o arquivo. As camadas novas são opcionais: `jogavel`, `camera_limite`, `terreno`, `amargo`, `zonas`, `zonas_grid`, `rio`, `trilhas`, `npcs`, `baus`, `objetos`, `luzes`, `sons_pontuais`, `safe_zones` e `spawn_por_faccao`.
- Os `kind` dos props usam os nomes do kit de ambiente quando o objeto já existe lá (`predio_enterrado`, `bonde_veleiro`, `poste_mastro`, `juncos`, `pedras_rio`…). Props com `"camada": "chao"` são decalques e vão por baixo dos personagens. Props com `"pendente": true` ainda não têm arte. Props com `"decor_moldura": true` são só cenário da moldura.
- Os `kind` dos spawns usam os ids de `design/combate/mobs.json`. O jogo ainda usa os nomes antigos (`cao_praga`, `flagelado`, `automato`, `acougueiro`).
- Campos novos nos spawns: `motivo`, `ancora`, `formacao: "fila"`, `patrulha`, `so_para` e `so_por_missao`.
- Com 160 tiles, um chão pré-renderizado numa imagem só ficaria grande demais. Vale montar o chão com os pisos em blocos 4×4 do kit ou dividir em pedaços.
- O jogo usa 44,8 px/m e 35°, e o kit usa 64×32 por tile e 30°. Essa diferença precisa ser resolvida na integração.

## Arte que falta (lista para a thread de cenário)

São 62 kinds marcados como `pendente`. Os mais importantes para o mapa funcionar:

1. **Pisos:** areia com veios verdes, duna baixa, vidro derretido, leito seco rachado, lama amarga e poça verde, barranca de lama seca, musgo amargo, brejo tóxico, chão de mata morta e cascalho com trilhos. A cinza dos Campos já está a caminho.
2. **Limites:** a beira do precipício com `corda_guarda`, `guindaste_sucata`, `ponte_rompida`, `trilhos_no_abismo`, `telhado_no_abismo` e `torre_no_abismo`; e a tempestade com `torre_vigia_enterrada`, `ossada_viajante`, `ossada_gigante` e `poste_telegrafo`.
3. **Estruturas:** `ponte_ferro_bonde`, `torre_sino`, `casa_coveiro` (mausoléu), `torre_relogio_enterrada`, `moinho_ruina` e `roda_dagua`, `tanque_sebo`, `cerca_chiqueiro`, `toca_caes`, `vala_aberta`, `muro_contencao_areia`, `tenda_demonio`, `trono_sucata`, `pulpito_externo` e `posto_odete`.
4. **Vegetação seca e mutante:** `moita_cardo`, `cogumelos_palidos` e `arvore_enforcados`. O resto já vem do kit: `arvore_morta`, `arvore_morta_grande`, `arbusto_seco`, `mato_seco`, `juncos`, `planta_mutante` e `poca_toxica`. Não há carros em lugar nenhum do mapa.

Lista completa, igual à do JSON: `arvore_enforcados`, `asa_anjo_caida`, `braseiro_sagrado`, `caldeirao_cardo`, `cano_esgoto`, `capelinha_beira`, `carrinho_tobias`, `casa_coveiro`, `cerca_arame_torta`, `cerca_chiqueiro`, `cocho`, `cogumelos_palidos`, `corda_guarda`, `corpo_lacrado`, `cova_aberta`, `cratera_corte`, `duna_ondulacao`, `elmo_espada_fincada`, `espantalho_arame`, `estacas_cerca`, `estandarte_rasgado`, `forca_ponte`, `guindaste_sucata`, `janela_na_areia`, `lama_porcos`, `lanterna_procissao`, `mesa_acougue_rua`, `moinho_ruina`, `moita_cardo`, `muro_contencao_areia`, `ossada_animal`, `ossada_gigante`, `ossada_viajante`, `penas_espalhadas`, `placa_rua_enterrada`, `ponte_ferro_bonde`, `ponte_rompida`, `poste_ninho`, `poste_ninho_gigante`, `poste_telegrafo`, `posto_odete`, `pulpito_externo`, `ralo_ferro_chao`, `roda_dagua`, `roda_dagua_bomba`, `sumidouro`, `tanque_sebo`, `telhado_no_abismo`, `tenda_demonio`, `toca_caes`, `torre_no_abismo`, `torre_relogio_enterrada`, `torre_sino`, `torre_vigia_enterrada`, `trilho_retorcido`, `trilhos_no_abismo`, `trono_sucata`, `tumulo_aberto`, `vala_aberta`, `varal_roupas`, `vela_tumulo`, `vidro_estilhacos`

Para a thread de efeitos visuais: o brilho das poças e da lama amarga, a parede da tempestade com rajadas de areia, a poeira em que a moldura se dissolve, o Amargo caindo nos Campos, a névoa sobre o rio e a Vala, a fumaça das chaminés, as sementes de cardo, os vaga-lumes do bosque e os corvos que levantam voo quando o jogador passa.
