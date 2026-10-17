# Enfeites: props pequenos para as áreas carentes · guia de integração

Thread "Enfeites para as áreas carentes" (pedido do Jefin em 17/10/2026: "criar mais props, pequenos enfeites, para as
áreas mais carentes disso, que repetem muito; o matadouro só tem uma carne espetada" + "algo mais bonito").

**Não entra na 0.9.3** (o Jefin pediu só para adiantar). Integrar na versão seguinte.

Prévias em `entregas/enfeites/previa/` (maquete e folha de cada bioma). Fontes em `assets/ambiente/fontes/enfeites.py`.

## Passos

1. Copiar as 36 peças prontas para o kit e atualizar o manifesto:

       cp entregas/enfeites/objetos/*.png entregas/enfeites/objetos/*.json assets/ambiente/objetos/
       mkdir -p /tmp/claude-0/vazio && cd assets/ambiente/fontes && python3 publicar.py /tmp/claude-0/vazio

   (com uma pasta de brutos vazia, o `publicar.py` só reconstrói o `manifest.json` a partir de todos os `.json` de `objetos/`.)
2. `cd game && bash tools/sync.sh`.
3. Espalhar os enfeites nos mapas pelo gerador de cada área (nunca à mão): `design/mapas/cripta/gerar.py` (Porão,
   Câmara, Ossário, Catacumba), `design/mapas/egito/dungeons_egito.py` (Hawara, Coração) e o layout da área inicial
   (Abatedouro Carniça). Regra de ouro do Jefin: nada empilhado, cada sala com um motivo. Sugestão abaixo.
4. Os que têm `chao: true` são decalques (desenhar por baixo dos atores, sem bloqueio).
5. Fogo: os enfeites com vela, brasa ou lamparina trazem `"luz"` no json (`vela`, `fogo`): pôr uma luz pequena
   quente `[1, 0.55, 0.2]` com raio ~2 no mesmo ponto (o cliente já faz tremer a luz amarela).

## Onde usar (sugestão por sala, 2 a 4 enfeites por sala, longe das portas)

- **Porão do Matadouro:** açougue e câmara fria: `cepo_cutelo`, `bandeja_visceras`, `faqueiro_parede`, `balanca_gancho`,
  `cabide_avental` (perto da porta da câmara fria); salgadeira: `pernis_tripe`, `varal_linguica`, `balde_miudos`;
  depósito: `caixote_ossos`, `pedra_amolar`; chão do corredor e da Vala: `restos_carne_chao`, `caveira_boi`.
- **Abatedouro Carniça (área inicial):** `cepo_cutelo`, `varal_linguica` e `balde_miudos` no pátio dos ganchos.
- **Hawara e Coração:** salas de oferenda: `mesa_oferendas` + `lamparinas_chao` + `incensario_braco`; salas de enxoval:
  `cadeira_ebano`, `vasos_alabastro`, `ushabtis`, `modelo_barca`, `harpa_arco`, `cesto_papiros`; sala da Balança de
  Maat (Coração 5): `escaravelho_coracao`; corredores: `mumias_gato`, `cabeca_farao` (2x1).
- **Câmara da Trombeta:** `trombetas_caladas` (é o motivo do andar: as trombetas amordaçadas), `atril_partituras`,
  `candelabro_ferro`, `genuflexorio`, `sino_rachado`; chão: `lacres_cera_chao`.
- **Ossário das Carpideiras:** `ossuario_caixa`, `coroa_flores_secas`, `ex_votos`, `relicario`, `candelabro_ferro`.
- **Catacumba das Raízes:** `raizes_ossos` (2x1), `cruz_ferro_tombada`, `coroa_flores_secas`, `lacres_cera_chao`.

## As 36 peças

| id | bioma | tiles | chão | o que é |
|---|---|---|---|---|
| `cepo_cutelo` | matadouro | 1x1 |  | Cepo de tronco de casca rachada com aro de ferro, topo de lenho talhado e encharcado, cutelo cravado de fio,     um naco de costela e sangue escorrendo pela casca. |
| `balde_miudos` | matadouro | 1x1 |  | Dois baldes de chapa enferrujada: um cheio de miúdos até a borda, o outro tombado derramando tripa e sangue. |
| `varal_linguica` | matadouro | 2x1 |  | Varal de defumar: cavaletes de madeira com uma vara de ferro, gomos de linguiça em laço e mantas de charque     secando; pingos de gordura e serragem no chão. |
| `cabide_avental` | matadouro | 1x1 |  | Cabideiro de ferro do magarefe: avental de couro duro de sangue, luvas de borracha, chapéu de feltro e     as botas de cano alto largadas embaixo. |
| `bandeja_visceras` | matadouro | 1x1 |  | Caixote virado de banco com uma bandeja de zinco amassada: coração, fígado, rins e tripa limpos para a salmoura. |
| `caveira_boi` | matadouro | 1x1 |  | Cabeça de boi esfolada largada no chão: crânio com restos de carne, chifres longos, língua de fora e mandíbula solta. |
| `pedra_amolar` | matadouro | 1x1 |  | Esmeril de pedal: rebolo de arenito num cavalete de madeira, bacia de água ferruginosa embaixo, facas esperando a vez. |
| `balanca_gancho` | matadouro | 1x1 |  | Balança de gancho num tripé de vigas: mostrador de latão com ponteiro, pernil pendurado no prato e contrapeso de ferro. |
| `caixote_ossos` | matadouro | 1x1 |  | Caixote de ripas cheio de ossos de tutano para o caldo do cerco, uma caveira de chifres por cima e o carimbo do Carniça. |
| `faqueiro_parede` | matadouro | 1x1 |  | Quadro de ferramentas do magarefe em pé: tábua grossa num cavalete de ferro com facas, cutelos, serrote e chaira     pendurados, um amolador de couro e o rol de encomendas pregado. |
| `pernis_tripe` | matadouro | 1x1 |  | Tripé de ferro com corrente e três pernis curando no sal, um deles já cinzento de bolor; bacia de sal por baixo. |
| `restos_carne_chao` | matadouro | 1x1 | sim | Decalque de chão: aparas de carne, nacos de gordura, um osso de joelho e sangue pisado com marcas de bota. |
| `mesa_oferendas` | egito | 1x1 |  | Mesa de oferendas (hotep) de calcário com bica: pães cônicos e redondos, figos, um cacho de uva, um ganso     depenado, flores de lótus murchas e a jarra de cerveja, tudo que os vivos ainda deixam para os mortos do Faium. |
| `ushabtis` | egito | 1x1 |  | Caixa de ushabtis em forma de capela, pintada e de tampa caída: dezenas de servidores de faiança azul enfileirados     ("aqui estou") e alguns tombados no chão, um partido ao meio. |
| `cesto_papiros` | egito | 1x1 |  | Cesto de junco cheio de rolos de papiro atados com fita de linho, e um rolo aberto no chão com colunas de escrita     hierática e uma vinheta vermelha (o Livro dos Mortos de alguém que não chegou a ser enterrado). |
| `incensario_braco` | egito | 1x1 |  | Incensário em forma de braço, de bronze verde: cabo de papiro com cabeça de falcão numa ponta e a mão aberta na     outra segurando a taça com brasa; pousado num suporte de calcário, com as bolinhas de resina num prato. |
| `vasos_alabastro` | egito | 1x1 |  | Vasos de alabastro translúcido do enxoval: a taça em lótus, um vaso de unguento com tampa, uma jarra alta, e     os cacos de um que caiu. |
| `cabeca_farao` | egito | 2x1 |  | Cabeça de granito de um faraó caída da estátua: toucado nemes listrado com restos de azul e ouro, o nariz     quebrado, a barba postiça partida, meio afundada no lodo e no calcário que caiu junto. |
| `harpa_arco` | egito | 1x1 |  | Harpa de arco dos músicos do templo, de madeira com a cabeça de faraó entalhada no pé, cordas de tripa quase     todas arrebentadas, e um sistro de bronze de Hathor largado ao lado. |
| `cadeira_ebano` | egito | 1x1 |  | Cadeira de ébano do enxoval com pés de leão e encosto de folha de ouro gasta, o banquinho dos pés e o apoio de     cabeça de alabastro; o assento de junco trançado afundou. |
| `mumias_gato` | egito | 1x1 |  | Três múmias de gato de Bubástis em pé, enfaixadas em losango com a cara pintada e as orelhas de linho, e a     Bastet de bronze sentada com o filhote; uma caiu e abriu. |
| `lamparinas_chao` | egito | 1x1 |  | Lamparinas de barro acesas no chão diante de um nicho (o fogo dos que ainda rezam aqui), uma tigela de óleo,     pavios de linho e amuletos ankh e olho de Hórus deixados como ex-voto. |
| `escaravelho_coracao` | egito | 1x1 |  | Escaravelho do coração de pedra verde, do tamanho de um cão, num pedestal de calcário: as asas entalhadas e, na     base, o feitiço 30B ("ó meu coração, não te levantes como testemunha contra mim"). |
| `modelo_barca` | egito | 2x1 |  | Modelo de barca funerária de madeira pintada do enxoval: casco em lua, olho de Hórus na proa, remadores de     madeira sentados, o dono sob o dossel e a vela de linho enrolada; sobre um suporte baixo. |
| `trombetas_caladas` | cripta | 1x1 |  | Monte de trombetas de latão caladas: amassadas, as campanas entupidas de pano de luto, amarradas e lacradas     com cera vermelha, como os Arautos fizeram com todas as que acharam depois que a sétima não tocou. |
| `relicario` | cripta | 1x1 |  | Relicário gótico de latão sobre coluna de pedra: caixinha de vidro com pináculos, um osso de dedo num coxim de     veludo, ex-votos de fita amarrados na base e duas velas acesas. |
| `candelabro_ferro` | cripta | 1x1 |  | Candelabro de chão de ferro batido com três pés de garra, coroa de sete pontas e velas grossas derretendo,     a cera escorrida em estalactites pelos braços. |
| `ex_votos` | cripta | 1x1 |  | Sala dos milagres: tábua de promessas num cavalete com ex-votos de cera pendurados (cabeças, mãos, pernas, um     coração), fotografias desbotadas, muletas encostadas e as velas de quem ainda pede. |
| `coroa_flores_secas` | cripta | 1x1 |  | Coroa de flores de finados num tripé de arame: rosas e cravos secos quase pretos, folhagem de cipreste ressecada     e a faixa de luto escrita a tinta dourada desbotada. |
| `sino_rachado` | cripta | 1x1 |  | Sino de bronze caído da torre e rachado, de boca para o lado, com o badalo arrancado, a trave quebrada e a corda     podre; verdete por fora e cera pingada por cima (alguém acende velas para ele). |
| `atril_partituras` | cripta | 1x1 |  | Estante de coro de ferro batido com o hinário aberto na antífona do Juízo, partituras rasgadas no chão e uma     trombeta calada no banquinho do lado. |
| `genuflexorio` | cripta | 1x1 |  | Genuflexório de madeira escura com almofada de veludo puída, o terço de contas de osso pendendo e o missal     aberto; a cera de anos de velas forma um monte na frente. |
| `ossuario_caixa` | cripta | 1x1 |  | Caixas de ossuário empilhadas, com crânios pintados à moda velha (nome, data e uma coroa de folhas na testa),     uma tampa aberta mostrando os ossos longos arrumados. |
| `lacres_cera_chao` | cripta | 1x1 | sim | Decalque de chão: lacres de cera vermelha arrancados do peito dos Não-Julgados, tocos de vela, cera derramada e     fitas com o selo, onde um deles se levantou. |
| `raizes_ossos` | cripta | 2x1 |  | Raízes grossas que furaram o piso da catacumba e saíram arrastando ossos e uma caveira presa no meio; lajes     levantadas em volta e terra preta. |
| `cruz_ferro_tombada` | cripta | 1x1 |  | Cruz de túmulo de ferro batido com volutas e a plaquinha esmaltada do nome, tombada e meio torta sobre um monte de     terra, uma guirlanda de arame com flores secas ainda presa. |

## Regerar

    # bpy 4.2 (se /opt/bpy42 não existir: python3.11 -m pip install bpy==4.2.0 e troque por python3.11)
    cd assets/ambiente/fontes && /opt/bpy42/bin/python render_assets.py -- /tmp/claude-0/enfeites_brutos <ids...>
    python3 publicar.py /tmp/claude-0/enfeites_brutos

Novo enfeite: função com `@ef("id", "bioma")` em `enfeites.py` (biomas: matadouro, egito, cripta), usando os
materiais do kit da área. O `render_assets.py` já importa `enfeites`.
