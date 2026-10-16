# Cidade de São Lázaro (Vigília) · entrega para a Prévia

Pedido do Jefin (15/10/2026): a área inicial passa a ser da Vigília. Ela vira a cidade da igreja de São Lázaro no deserto, com a rádio, o matadouro, a linha do bonde e o cemitério. O mapa é coeso e maior, com o dobro de props, nada empilhado, spots de farm bons, missões e mobs.

**Entra na versão depois da 0.9.2.** Não publique cliente só por causa disto.

## O que tem aqui

| Arquivo | O quê |
|---|---|
| `area_inicial.json` | O mapa novo, no **mesmo formato** de `design/mapas/area_inicial.json` (name, size, spawn, safe_zone, props, blocked, spawns, terreno, zonas, spots, descanso, npcs, baús, objetos, luzes...). |
| `spots.json` | Os 13 spots de farm e as 7 fogueiras (mesmo formato do `design/mapas/spots.json`). |
| `missoes/missoes_cidade.py` | Acrescenta as 5 missões novas, os diálogos, as subzonas novas, o objeto da matriz e os 3 spots novos aos dados de `design/missoes/`. Rode com `--teste` para validar numa cópia (o resultado dá OK no `validar.py`). |
| `imagens/` | Prévias montadas com a arte real do kit: `visao_geral.jpg`, `cidade.jpg`, `cemiterio.jpg`, `abatedouro_rio.jpg`, `campos_marco.jpg`, `patio_bondes.jpg`. Também tem `planta_tecnica.png`, a vista de cima com spots, NPCs e bloqueios (é só para conferência). |

As fontes ficam em `design/mapas/sao_lazaro/fontes/`:
- `layout.py` gera o mapa;
- `cena2d.py` monta as imagens com os pisos, objetos, luzes e sprites do kit;
- `overview.py` gera as prévias;
- `dbg.py` gera a planta técnica.

Para regerar: `cd design/mapas/sao_lazaro/fontes && python3 layout.py && python3 overview.py ../../../../entregas/cidade_sao_lazaro/imagens`.

## Números

- **Tamanho:** a área jogável tem 160x160 (antes eram 120x120). Com a moldura de 20 tiles, são 200x200.
- **Props:** 2.588 na área jogável (antes, 1.316 no mapa todo).
  - Cada objeto espalhado respeita o footprint real do kit no chão.
  - Também respeita a silhueta na tela: uma máscara de alpha de cada PNG impede que um objeto cubra mais de 10% de outro. Isso é o "nada empilhado".
- **Mobs:** 209 no total, 156 deles dentro dos 13 spots. São 133 neutros, 62 territoriais e 14 agressivos (só o Abatedouro, como manda a lore).
- **Bases:** uma só, a da Vigília. `safe_zones` tem só a cidade (raio 24) e `spawn_por_faccao` só tem `vigilia`.

## A cidade (id da zona continua `acampamento_vela`)

Mantive o id `acampamento_vela` para os diálogos, missões e pontos continuarem valendo. O nome mudou para "Cidade de São Lázaro".

- **Igreja Matriz** (`capela_enterrada`, ponto `matriz_sao_lazaro`): é a mesma arte da capela. A porta é o ponto `porta_matriz` e tem o objeto `matriz_sao_lazaro` (missão vc03).
- **Praça da Vela:**
  - a Vela (`a_vela`), com a Zulmira e o Pirralho;
  - a Arca do Gustavo;
  - o poço;
  - seis lampiões.
- **Estação da Linha 7:**
  - a cúpula (`portao_cupula`);
  - o bonde-veleiro atracado (`plataforma_bondes`, com o Bento);
  - o posto da Odete.
- **Rua do Mercado:** a forja do Gaspar, o caldeirão da Mãe Cardo, o carrinho do Tobias e o forno da Celina.
- **Enfermaria:** o Anselmo e a Lindalva.
- **Rádio São Lázaro:** fica no `predio_concreto` da beira do precipício, com a Isaura.
- **A Cerca:** a paliçada tem 7 portões e torres nos 3 principais. O Damião fica no portão leste (`costelas_cupula`).

## Spots (ids das missões mantidos)

| Spot | Nível | Mobs | Novo? |
|---|---|---|---|
| Covas Rasas | 1-3 | 6 carnical, 6 corvo | |
| Cemitério de Bondes | 2-4 | 6 corvo (territorial no poste torto), 6 carnical | sim |
| Telhados dos Corvos | 3-5 | 6 cão de vala, 6 corvo | |
| Fosso dos Cães | 3-5 | 9 cão de vala, 3 carnical | |
| Procissão Parada | 4-6 | 12 não-julgado (+ 4 com o andor) | |
| Chiqueiro do Carniça | 4-6 | 12 porco | |
| Alameda dos Ciprestes | 5-7 | 9 não-julgado, 3 corvo-carniça | sim |
| Margem das Viúvas | 5-7 | 8 não-julgado, 4 sangrador | |
| Acampamento dos Desertores | 6-9 | 8 desertor, 4 cão | |
| Marco do Corte | 7-9 | 6 desertor, 6 carniçal inchado | |
| Pátio do Abatedouro | 7-9 | 11 açougueiro + Capataz (elite) | |
| Casas da Vila | 8-10 | 6 sangrador, 6 não-julgado | sim |
| Beira da Tempestade | 9-12 | 6 não-julgado da tempestade, 6 sombra gravada | |

Todos os spots usam `substituto` quando o mob ainda não está no jogo, igual ao mapa anterior. Usei também as variantes que já têm arte: `carnical_inchado`, `corvo_de_cinza_carnica`, `nao_julgado_da_tempestade` e `cao_de_vala_alfa`.

## Missões novas (Vigília)

| Id | Nível | Quem dá | O quê |
|---|---|---|---|
| vc01 Noite Nova na Cidade | 1 | Zulmira | Apresentar-se à Odete, ao Gaspar e à Isaura (tutorial da cidade). |
| vc02 Cobre dos Bondes | 3 | Odete | Farmar o Cemitério de Bondes e matar 6 corvos. |
| vc03 O Sino da Matriz | 5 | Gaspar | Tocar o sétimo sino pela rosácea, depois matar 8 Não-Julgados. |
| vc04 Os Nomes do Alto | 6 | Simão | Farmar a Alameda dos Ciprestes. |
| vc05 O Último Turno | 9 | Isaura | Farmar as Casas da Vila. |

## O que saiu do mapa (decisão minha; o Jefin pode mudar)

A Capela dos Arautos e os NPCs Madre Ivone, Abdiel, Malfas e Lúcio não estão neste mapa, nem as patrulhas de facção (`so_para`).

- As missões dos Arautos (a01–a05, s05–s07, d01a, e01a, e05a, f01a, r02) continuam nos JSON e ficam para a área inicial dos Arautos.
- As linhas D, E e F continuam funcionando pelo lado da Vigília.

## O que falta de arte (para o Cenário)

Estes props estão marcados `pendente`. Nas prévias aparece um parecido do kit no lugar:
- `antena_radio`: mastro de rádio com luz vermelha, no telhado da Rádio e no Bairro Afogado;
- `flor_absinto` e `flor_absinto_lata`: flores do oásis e flores plantadas em latas nas portas da cidade;
- `varal_lanternas`;
- `escotilha_silo`.

## Para a integração

1. Copie `area_inicial.json` sobre `design/mapas/area_inicial.json` e `spots.json` sobre `design/mapas/spots.json`, depois rode o `game/tools/sync.sh`. O `game/tools/mapa.py` lê o mesmo formato.
2. Rode `python3 missoes/missoes_cidade.py design/missoes` e depois `python3 design/missoes/validar.py`.
3. A câmera usa `camera_limite` (14 a 186). O mapa é maior, então o chão em blocos fica com mais pedaços.
4. Os terrenos usados são os mesmos códigos do mapa anterior, mais `n` (entulho) e `i` (asfalto). Os dois já existem no `PISOS` do `mapa.py`.
