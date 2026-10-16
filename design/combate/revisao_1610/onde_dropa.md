# DARK PASSAGE · mapa consolidado "onde dropa o quê" (16/10/2026)

Levantamento feito só com leitura, nenhum arquivo do projeto foi alterado. Caminhos relativos a `/mnt/project-files`.

**Como o drop funciona hoje** (`game/scripts/sim/loot.gd` + `game/scripts/defs.gd`):

- O mob pega a tabela em `Defs.MOBS[kind].drop`; o chefe pega em `Defs.CHEFES[kind].drop`. A busca é sempre em
  `Defs.DROPS["tabelas"][id]` (`loot.gd`, `dropar_mob`).
- Se a tabela tem `rolagens_garantidas`, sorteia N vezes. Se não tem, faz 1 rolagem com chance `item_chance`. O sorteio
  é pelos `peso` das `rolagens`.
- `equip:faixaN` sorteia **qualquer** item com essa tag, sem olhar o nível do item. A preferência é 70% para a classe do
  jogador. O código usa `f := 1 if tag.ends_with("1") else 2`, então qualquer coisa que não seja faixa1 vira faixa 2.
- `lendario:X` sai de `itens.json → pools_lendarios`. `missao:X` cria o item `X` sem checar se ele existe.
- Ouro de mob: 55% de chance, `rand(2,6L; 6,5L) × arquetipo.xp × ouro_mult`. Ouro de chefe: `randi(2L, 5L) × ouro_mult`,
  e quando não há tabela o `ouro_mult` vale 20 por padrão.
- **Lágrimas** (`drops.json → lagrimas`): rolagem própria em qualquer mob. A Angélica segue a curva 0,08% (nv 1) → 0,8%
  (nv 50) → +0,004%/nível → teto 1,6%. A Sanguínea vale a metade. Multiplicadores: spot ×1,25, elite/raro ×3, chefe ×5.
  Isso **se soma** ao `joia:refino` das tabelas.
- Poções em spot: 10% de chance extra por abate.
- Mob 6 ou mais níveis abaixo do jogador não solta `equip`.
- Baús (`abrir_bau`): `faixa = 1 se nivel < 7, senão 2`. O `nivel` do baú vem de `aux.nivel`, e quando ele falta vale o
  **nível do jogador**.

---

## 1. Tabela por área (em ordem de nível)

Legenda de estado: **JOGO** = está em `game/data/`. **DESIGN** = está em `design/` e ainda não foi sincronizado.
**ENTREGA** = está em `entregas/` e ainda não foi integrado.

### Tabelas de drop referenciadas (pesos e chance)

| Tabela | Onde está | item_chance / rolagens | Tags (peso) | ouro_mult |
|---|---|---|---|---|
| inicial_animal | drops.json | 0,10 | pocao_vida_p 40, couro_podre 35, osso 15, **equip:faixa1 10** | – |
| inicial_humanoide | drops.json | 0,16 | pocao_vida_p 30, municao 15, sucata 20, **faixa1 35** | – |
| inicial_espectro | drops.json | 0,14 | pocao_recurso_p 35, cinza_de_alma 30, **faixa1 35** | – |
| elite_inicial | drops.json | 3 garantidas, mín. mágico | faixa1 70, **lendario:capataz 4**, chave:bau_de_ferro 26 | 3 |
| raro_missao_cardo | drops.json | 2 garantidas, mín. mágico, garantido `missao:coracao_de_cardo` | faixa1 85, **lendario:cardo 15** | – |
| cripta_carne | drops.json | 0,08 | pocao_vida_p 50, carne_estragada 50 (sem equip) | – |
| cripta_humanoide | drops.json | 0,16 | pocao_vida_m 25, municao 15, sucata 20, faixa2 40 | – |
| cripta_monge | drops.json | 0,22 | pedra_benta 40, faixa2 60 | – |
| cripta_espectro | drops.json | 0,15 | pocao_recurso_m 35, cera_de_vela 25, faixa2 40 | – |
| cripta_celestial | drops.json | 0,18 | pena_suja 30, faixa2 70 | – |
| chefe_general | drops.json | 4, mín. mágico, garantido `missao:estandarte_roido` | faixa2 80, joia:refino 12, lendario:general 8 | 25 |
| chefe_celeste | drops.json | 4, mín. mágico, garantido `missao:veu_da_carpideira` | faixa2 78, joia 14, lendario:celeste 8 | 25 |
| chefe_zacarias | drops.json | 5, mín. raro, garantido `missao:bocal_da_trombeta` | faixa2 72, joia 16, lendario:zacarias 12 | 30 |
| mata_animal | v06_extra.drops | 0,16 | pena_suja 35, faixa2 55, joia 10 | – |
| mata_arauto | v06_extra.drops | 0,20 | faixa2 80, joia 20 | – |
| elite_mata | v06_extra.drops | 2, mín. mágico | faixa2 80, joia 20 | 8 |
| torre_horda | v06_extra.drops (e dados_torre) | 0,22 | faixa2 78, joia 22 | – |
| torre_elite | design/mapas/a_torre/dados_torre.json | 1, | faixa2 76, joia 24 | 4 |
| chefe_torre_1..5 | v06_extra.drops (versão nova em dados_torre) | 3/3/4/4/5, mín. raro | faixa2 74→66, joia 18 (19→23 na nova); torre_4/5 antigas: **lendario:zacarias 12/14** | 20/25/30/35/40 |
| catacumba | v06_extra.drops | 0,22 | faixa2 78, joia 22 | – |
| chefe_catacumba | v06_extra.drops | 3, mín. raro | faixa2 80, joia 20 | 18 |
| atl_animal / atl_guardiao / atl_coro / atl_serpente | design/mapas/atlantida/dados.json | 0,18 / 0,22 / 0,24 / 0,26 | faixa2 60–78, joia 15–26 (atl_animal tem pena_suja 25) | – |
| elite_atl | atlantida/dados.json | 2, mín. mágico | faixa2 78, joia 22 | 10 |
| chefe_gadiro | atlantida/dados.json | 5, mín. raro | faixa2 70, joia 18, **lendario:zacarias 12** | 45 |
| egito_animal/inseto/mumia/guardiao/construto | entregas/egito/dados.json | 0,08–0,09 | **faixa3 52**, material novo 26, joia 8, pocao_vida_m 10, pocao_recurso_p 6 | – |
| egito_elite | entregas/egito/dados.json | 1, mín. mágico | faixa3 60, joia 15, chave 10, bronze_antigo 15 | 8 |
| hawara / raid_coracao | entregas/egito/dados.json | 0,10 / 0,12 | faixa3 52, ouro_de_sobek/fragmento_do_duat 18, joia 8, poções 16 | – |
| chefe_hawara_1..3 | entregas/egito/dados.json | 2, mín. mágico, garantidos brinco/glifo/ferrão | faixa3 62, joia 14, ouro_de_sobek 12, lendario:<chefe> 7, lendario:regalia_de_sobek 5 | 30/35/40 |
| chefe_coracao_1..6 | entregas/egito/dados.json | 2 (Faraó 3), mín. raro | faixa3 60, joia 14, fragmento_do_duat 12, lendario:<chefe> 7, lendario:regalia_do_farao 7 | 50→100 |

### Áreas

| # | Área / dungeon | Estado | Nível dos mobs (spawn real) | Mobs / chefes (id: nível) → tabela | Itens nomeados / lendários possíveis | Baús |
|---|---|---|---|---|---|---|
| 1 | **Paróquia de São Lázaro / Deserto de Absinto** (`game/data/mapas/area_inicial.json`, spots em `game/data/design/mapas/spots.json`, 10 spots) | JOGO | 1–12 | corvo_de_cinza 3–4 → inicial_animal; carnical 1–8 → inicial_humanoide; cao_de_vala 2–8 → inicial_animal; nao_julgado 3–10 → inicial_espectro; porco_pestilento 4–6 → inicial_animal; acougueiro_oco 5–9 → inicial_humanoide; sangrador_apostata 6–7 → inicial_humanoide (v06); desertor_legiao 6–9 → inicial_humanoide (v06); sombra_gravada 10–12 → inicial_espectro (v06); **capataz_gancho 9 (elite) → elite_inicial**; filho_de_cardo 6 (raro, missão) → raro_missao_cardo; ultimo_operador 12 (elite, escotilha do silo) → elite_inicial; nao_julgado_da_tempestade 9–11 e carnical_inchado 11–12 (v06, herdam a tabela da base) | gancho_capataz (nv 7, `lendario:capataz`, 11,5% por abate do Capataz, que renasce em 300 s); lenco_cardo (nv 5, `lendario:cardo`, 27,8% por abate do Filho de Cardo e também recompensa da s02); recompensas de missão: estilhaco_lacre, diapasao_reverso (v05), pena_zacarias, etiqueta_branca (a05), estilhaco_absinto, chave_segunda_estrela (d06), elmo_rafael (f06), faixas_betania (f05), dragonas_general (c04), faixa_de_linho_rafael nv 150 (g07), pena_que_ficou nv 400 (h01) | 16 caixote_podre, 7 bau_de_ferro (sem `nivel`: usam o nível do jogador) |
| 1b | **Cidade de São Lázaro** (`entregas/cidade_sao_lazaro/area_inicial.json`, 13 spots em `spots.json` = `design/mapas/spots.json`) | ENTREGA (substitui o mapa 1) | 1–12 | os mesmos de cima, mais **cao_de_vala_alfa 9** e **corvo_de_cinza_carnica 7** (não existem em mobs.json nem em v06_extra), mais carnical_inchado 8 | iguais ao mapa 1 | 10 baús com `tipo` comum/trancado/raro (não batem com as chaves de `drops.json → baus`) |
| 2 | **Jerusalém e Monte Hermon** (`entregas/jerusalem_hermon/jerusalem_hermon.json`) | ENTREGA | 1–12 (espelho do deserto) | peregrino_ressecado 1–8 → inicial_humanoide; abutre_do_hermon 3–4 e chacal_de_josafa 2–8 → inicial_animal; porco_de_gadara 4–6 → inicial_animal; **levantado_das_oliveiras 3–10 → inicial_humanoide** (o espelho nao_julgado usa inicial_espectro); sineiro_infiltrado 6–7 e sapador_herege 6–9 → inicial_humanoide; **vigilante_acorrentado 10–12 → inicial_humanoide** (o espelho sombra_gravada usa inicial_espectro); fornalheiro_de_tofete 5–9 → inicial_humanoide; **capataz_de_tofete 9 → inicial_humanoide** (o espelho capataz_gancho usa elite_inicial); filho_do_hissopo 5 → raro_missao_cardo; kokabiel_contador 12 → elite_inicial | só a `lendario:cardo` (lenco_cardo) via filho_do_hissopo; recompensas de missão: veu_de_zilpa, malho_de_tubal (nv 5), manto_de_ohya, veu_de_naama, orelha_de_jael, divisa_da_geena, pena_do_escriba, diadema_do_escriba, lasca_da_tabua, selo_do_coro, estrela_contada, astrolabio_do_coro (nv 12, "unico") | 16 caixote, 7 bau_de_ferro |
| 3 | **Cripta da Trombeta Calada** (porao_matadouro, ossario_carpideiras, camara_trombeta) | JOGO | 6–12 | Andar 1: larva_de_carne 6–7 → cripta_carne; acougueiro_oco 6–7 → inicial_humanoide; gancheiro 7 → cripta_humanoide; soldado_caido 8 → **sem tabela**; **general_partido 8 → chefe_general**. Andar 2: fogo_de_vela 8–9 e carpideira 9 → cripta_espectro; monge_emparedado 8–9 → cripta_monge; **irma_celeste 10 → chefe_celeste**. Andar 3: querubim_desfeito 10–11 e eco_da_trombeta 11 → cripta_celestial; **zacarias_arauto 12 → chefe_zacarias** | estandarte_legiao (nv 8, general); bacula_femur e veu_carpideira (nv 10, celeste); halo_incandescente (nv 12, zacarias; no Relicário também, com 20% por rolagem × 3) | andar 1: 2 ferro; andar 2: 1 caixote, 2 ferro; andar 3: 1 caixote, 1 ferro, 1 relicario_da_trombeta |
| 3b | **Fosso dos Vigilantes** (minas_dos_gigantes, salao_das_noivas, altar_do_juramento) | ENTREGA | 6–12 | verme_do_fosso 6–7 → cripta_carne; **nefilim_mirrado 6–7 → cripta_carne** (o espelho acougueiro_oco usa inicial_humanoide); escravo_dos_gigantes 7 → cripta_humanoide; soldado_de_pedra 8 → cripta_humanoide (o espelho soldado_caido não tem tabela); brasa_de_azazel 8–9 → cripta_espectro; **noiva_afogada 9 → cripta_monge** (o espelho carpideira usa cripta_espectro); escriba_emparedado 8–9 → cripta_monge; eco_do_juramento 11 e vigilante_desfeito 10–11 → cripta_celestial; chefes ohya_gigante 8 → `drop_ohya`, naama_noiva 10 → `drop_naama`, semyaza_juramento 12 → `drop_semyaza` (alias para chefe_general/celeste/zacarias em `dados.json → drops_alias`) | pelo alias, os mesmos relicários do deserto (estandarte_legiao, bacula_femur/veu_carpideira, halo_incandescente) e os itens de missão da Vigília | 2 / 3 / 3 (inclui um relicario_da_trombeta) |
| 4 | **Novo Éden / Mata do Granizo** (`game/data/mapas/mata_do_granizo.json`) | JOGO (a versão de `design/mapas/mata_do_granizo/` tem mais 4 mobs) | 12–30 | lobo_de_cinza 12–17, corvo_de_brasa 12–15, javali_brasa 13–15, enxerto_errado 18–21, sapo_sacristao 26–28 → mata_animal; enxame_de_fagulhas 15–17, legionario_desgarrado 16–25, incendiaria 16–17, cao_de_brasa 19–22, escudeiro_sem_hoste 18–22, vitral_andante 22–24, bombardeiro_legiao 28–30 → mata_arauto; querubim_queimado 25–27 e centuriao_sem_bandeira 28–30 → torre_horda; **ent_de_cinza 22 (elite) → elite_mata**. Só no design: cervo_de_lume 12–14 → mata_animal, querubim_da_espada 18–22 e serpente_do_eden 24–26 → mata_arauto, **a_serpente 27 (elite) → elite_mata** | nenhum lendário; equipamento só faixa2 (itens nv 7–15) | jogo: 1 caixote, 1 ferro (design: 2 e 2) |
| 5 | **A Torre** (`game/data/mapas/torre_1..5.json`) | JOGO (versão antiga: andares só com chefe) | chefes 15–30 | centuriao_ferrabras 15 → chefe_torre_1; madre_brasilia 19 → chefe_torre_2; o_telegrafista 23 → chefe_torre_3; malaquias_escudeiro_cego 27 → chefe_torre_4; baraquiel_arauto_do_granizo 30 → chefe_torre_5 | torre_4/5: lendario:zacarias (halo nv 12) | 1 bau_de_ferro por andar (abre com o chefe morto) |
| 5b | **A Torre, Repetidora do Granizo** (`design/mapas/a_torre/`) | DESIGN (não integrada) | 12–30 | sintonizado 12–17, sintonizado_locutor 16–21, receptaculo 20–25, eco_da_estatica 24–28 → torre_horda; guarda_fios, receptaculo_inchado 28, inaudivel (elite) → torre_elite; chefes ferrabras_guarda_linhas 15, madre_brasilia 19, o_telegrafista 23, malaquias_ouvinte_cego 27, baraquiel 30 → chefe_torre_1..5 (nova versão, sem lendário) | nenhum lendário | 1–2 caixote/ferro por andar |
| 6 | **Catacumba das Raízes** (`game/data/mapas/catacumba_das_raizes.json`) | JOGO | 18–21 | raiz_ossuda 18–21, enterrado_florido 19–20, envenenador_da_comunhao 21 → catacumba; **bento_fel 22 → chefe_catacumba** | nenhum lendário | 1 caixote, 2 ferro |
| 7 | **O Cume dos Vigilantes** (evento diário, `entregas/evento_hermon/`) | ENTREGA | jogadores 15–400; mobs 30/70/120/190/300 por faixa | vigilante_jurado, vigilante_ferreiro, vigilante_estrelado (elite) → `drop: null` | prêmio do vencedor: 30% de uma das 6 Armas de Azazel (nv 25, `lendario:hermon`); sobrevivente: 1 Lágrima Angélica, 15 de ouro × nível dos mobs, Fichas de Sangue | – |
| 8 | **Agrak** (`design/mapas/agrak/`, `design/pvp/agrak/dados.json`) | DESIGN | 25+ | leao_sansao, leao_dalila, leao_nabucodonosor 30; golias 35 → `drop: None` | prêmio: Ficha de Sangue; Couraça do Agrak (nv 25, raro) só na loja do Saulo | – |
| 9 | **Atlântida** (`design/mapas/atlantida/atlantida.json` + `dados.json`) | DESIGN (não integrada) | 30–45 | touro_de_poseidon 30–42, ibis_de_thoth 30–40, elefante_de_atlas 36–39 → atl_animal; vigia_de_oricalco 32–43, cinocefalo 34–40, hoplita_de_oricalco 40–43 → atl_guardiao; corista_do_cerco 38–40, sineiro_do_coro 39–41 → atl_coro; filho_da_serpente 42–45, sacerdote_da_serpente 43–44 → atl_serpente; **touro_do_pilar 42 (elite) → elite_atl**; **gadiro 45 → chefe_gadiro** | Gadiro: lendario:zacarias (halo nv 12); itens próprios só de missão (engrenagem_oricalco, pena_de_ibis, sino_rachado, livro_de_thoth) | 2 caixote, 3 ferro |
| 10 | **Egito, a Terra Negra** (`entregas/egito/mapas/egito.json`) | ENTREGA | 50–70 | 18 mobs: ibis 50–51, crocodilo_do_nilo 50–64, crocodilo_gigante 63–69, escorpiões e cria_de_apofis 58–68 → egito_animal; escaravelhos 51–58 → egito_inseto; múmias 52–70 → egito_mumia; anubis/sobekita/falcão/guardião_múmia 56–70 → egito_guardiao; esfinge_carneiro 53–56 → egito_construto; **escaravelho_rei 58–63 (elite) → egito_elite** | nenhum lendário em mob aberto | 10 caixote, 8 ferro |
| 10b | **Labirinto de Hawara** (hawara_1..3) | ENTREGA | 50–54 | 7 mobs de dungeon → hawara; **petsuchos 51, esfinge_de_hawara 53, serket 54** → chefe_hawara_1..3 | 4 relíquias por chefe (nv 51–54) + Regalia de Sobek (5 peças, nv 52) | 2 ferro por andar |
| 10c | **O Coração Endurecido** (raid, coracao_1..6) | ENTREGA | 60 | 9 mobs → raid_coracao; **jambres, hapi, duamutef, qebehsenuef, ammit (raro 60) → `drop: None`**; chefes sekhmet, janes, imseti, apofis, anubis_pesador, farao_sem_nome (60) → chefe_coracao_1..6 | 5 relíquias por chefe (nv 60–66) + Regalia do Faraó (8 peças, nv 62) | 1–2 ferro por salão |
| 11 | **Salões de Amenti** (`design/mapas/amenti/saloes_de_amenti.json`) | DESIGN | 150 | guardiao_da_aurora 150, guardiao_do_crepusculo 150 (**não definidos** em nenhum arquivo de mobs) | – (de propósito, a área não tem farm) | – |

---

## 2. Tags de drop: quantos itens existem e o intervalo de nível

Fonte do jogo: `game/data/design/skills-itens/itens.json` (195 itens, de 15/10 22:36). Fonte do design:
`design/skills-itens/itens.json` (243 itens, regerado em 16/10 13:48 e ainda **não sincronizado**).

| Tag | Jogo: itens (nível) | Design: itens (nível) | Quem sorteia |
|---|---|---|---|
| equip:faixa1 | 41 (1–6) | 56 (1–6) | inicial_*, elite_inicial, raro_missao_cardo, baús com nível < 7 |
| equip:faixa2 | 45 (7–15) | 80 (7–18) | tabelas da cripta, mata, torre, catacumba, Atlântida, chefes, baús com nível ≥ 7 |
| **equip:faixa3** | **0** | **0** | todas as 17 tabelas do Egito |
| lendario:capataz | 1 (gancho_capataz, nv 7) | 1 | elite_inicial |
| lendario:cardo | 1 (lenco_cardo, nv 5) | 1 | raro_missao_cardo |
| lendario:general | 1 (estandarte_legiao, nv 8) | 1 | chefe_general |
| lendario:celeste | 2 (bacula_femur, veu_carpideira, nv 10) | 2 | chefe_celeste |
| lendario:zacarias | 1 (halo_incandescente, nv 12) | 2 (+ decreto_vampirico, nv 12) | chefe_zacarias, Relicário, chefe_torre_4/5 (antigos), chefe_gadiro (nv 45) |
| lendario:hermon | 0 no jogo; 6 na entrega (nv 25) | – | prêmio do evento (não é tabela) |
| lendario:petsuchos … farao_sem_nome (9 pools) | 0; 4–5 cada na entrega (nv 51–66) | – | chefes do Egito |
| lendario:regalia_de_sobek / regalia_do_farao | 0; 5 (nv 52) / 8 (nv 62) na entrega | – | chefes de Hawara / da raid |
| joia:refino | 2 (lagrima_angelica, lagrima_sanguinea) | 2 (**lagrima_anjo, fragmento_alma**: ids antigos) | chefes, mata/torre/catacumba/Atlântida/Egito, baús de ferro (25%), curva |
| joia:extra | 2 (coagulo_caos, engrenagem_viva) | 2 | **nenhuma tabela** |
| chave:bau_de_ferro | 1 | 1 | elite_inicial, egito_elite |
| consumivel:pocao_vida_p / _m, pocao_recurso_p / _m | 1 cada (m = nv 8) | 1 cada | tabelas iniciais e da cripta, baús, spot |
| consumivel:municao | 3 | 3 | inicial_humanoide, cripta_humanoide, baús |
| consumivel:extra | 3 | 3 | baús (classe ≠ humano) |
| consumivel:gazua | 1 | 1 | nenhuma tabela (só loja, `jogador.gd:1145`) |
| material:couro_podre, osso, sucata, cinza_de_alma, carne_estragada, pedra_benta, cera_de_vela, pena_suja | 1 cada | 1 cada | tabelas iniciais, da cripta, mata_animal, atl_animal |
| material:couro_do_nilo, casca_de_escaravelho, linho_de_mumia, bronze_antigo, po_de_calcario, ouro_de_sobek, fragmento_do_duat | 0 (só na entrega do Egito, `skills_itens_acrescimo.json`) | 0 | tabelas do Egito |

Armas por classe dentro de cada faixa (jogo → design):

| Faixa | Anjo | Cultista | Demônio | Humano | Mutante | Tecnomancer |
|---|---|---|---|---|---|---|
| faixa1 | 2 (1–5) → 5 (1–6) | 2 (1–5) → 2 | 2 → 5 | 5 (1–6) → 8 | 2 → 2 | 2 → 2 |
| faixa2 | **1 (só nv 9)** → 8 (8–18) | **1 (só nv 11)** → 1 | 3 (8–11) → 10 (8–18) | 3 (9–11) → 10 (8–18) | 2 (8–11) → 2 | 2 (8–11) → 2 |

---

## 3. Problemas concretos (com evidência)

### A. Bugs que mudam o drop hoje (no jogo)

1. **Nenhuma tabela do `v06_extra.json` é encontrada.**
   - `defs.gd:137-138` faz `DROPS[k] = ex["drops"][k]` e grava no topo do dicionário. O `loot.gd` (`dropar_mob`) procura em
     `Defs.DROPS["tabelas"]`.
   - Ficam sem efeito: mata_animal, mata_arauto, elite_mata, torre_horda, chefe_torre_1..5, catacumba e chefe_catacumba.
   - Consequência: todo o Novo Éden (nv 12–30), a Catacumba e os 5 chefes da Torre não soltam nenhum item (nem
     equipamento, nem joia, nem lendário). Sobram ouro, lágrimas da curva e poção de spot.
   - Os chefes ficam com `ouro_mult` 20, o padrão.
   - O `INTEGRACAO.md` da Mata diz "drops às tabelas", e o código fez outra coisa.
2. **Os itens garantidos dos chefes da Cripta e do Filho de Cardo não existem.**
   - Em `drops.json → tabelas.*.garantido`: `missao:estandarte_roido`, `missao:veu_da_carpideira`,
     `missao:bocal_da_trombeta` e `missao:coracao_de_cardo`.
   - Nenhum desses ids está nos itens do jogo. Os que existem são `bocal_trombeta`, `veu_carpideira` (relíquia) e
     `estandarte_legiao` (relíquia).
   - O `Itens.novo()` (`itens.gd:18`) não confere o id. Resultado: a cada abate cai um item fantasma, sem definição, para
     qualquer jogador, tenha ou não a missão.
3. **Os baús usam o nível do jogador.**
   - Nenhum baú dos mapas do jogo tem `nivel`; `loot.gd`, em `abrir_bau`, faz `nivel = aux.nivel ou jog.nivel`.
   - Um jogador de nível 100 abrindo um caixote na área inicial recebe faixa2 e ouro de 520 a 1300 (2,6–6,5 × 100 × 2).
   - Um bau_de_ferro dá o mesmo × 5.
4. **O pity de relíquia não foi implementado.** `drops.json → pity.reliquia_chefe_garantida_apos_vitorias = 6` não é lido em
   nenhum `.gd`: só `pity_raro` existe (`ent.gd:107`).
5. **As tabelas fixam a faixa, não o nível do mob.**
   - `regras.item_faixa` diz "faixa2 se L_mob ≥ 7", mas `Loot.tabela_por_nivel` não é chamado em lugar nenhum.
   - Por isso mobs de nível 9–12 soltam faixa1 (itens nv 1–6): sombra_gravada 10–12, nao_julgado 9–10,
     nao_julgado_da_tempestade 9–11, carnical_inchado 11–12, desertor 8–9, Capataz 9 e ultimo_operador 12 (elite_inicial).
6. **O item sorteado ignora o nível.**
   - `equip:faixa2` sai com o mesmo peso do nv 7 ao 15 (no design, até o 18). Um mob de nível 7 solta item de nível 15,
     que o jogador não consegue usar.
   - Um mob de nível 30 (Mata/Torre) solta no máximo item de nível 15.

### B. Regressão pronta para acontecer no próximo `sync.sh`

7. **`design/skills-itens/itens.json` foi regerado em 16/10 13:48 e perdeu a revisão de balanceamento que está no jogo.**
   - Não tem `lagrima_angelica` / `lagrima_sanguinea`. Tem `lagrima_anjo` / `fragmento_alma`, e nem
     `fontes/itens_data.py` tem `lagrima_angelica`.
   - Não tem `pena_que_ficou`, `faixa_de_linho_rafael` nem `livro_dos_vencidos`.
   - O `elmo_rafael` voltou para FOR/AGI/VIT/ESP +5 e +200 HP. No jogo ele é +4 e +50.
   - Se o `sync.sh` rodar, `_rolar_lagrimas` deixa de soltar lágrimas, porque checa `Defs.ITENS.has(id)`, e o refino até
     +15 fica sem item.
   - Ao mesmo tempo, essa cópia de design traz 53 itens novos (conjuntos peregrino → regente_anil, amuletos, 10 espadas
     nv 2–18 e `decreto_vampirico`) que o jogo não tem.

### C. Tags e tabelas inexistentes nas entregas

8. **`equip:faixa3` não tem nenhum item.**
   - 17 tabelas do Egito usam essa tag (`entregas/egito/dados.json → drops`), com 52–62% do peso.
   - Hoje o `loot.gd` trata faixa3 como f = 2, e `POR_TAG["equip:faixa3"]` está vazio, então volta `{}`. Os mobs do Egito
     soltam item em só ~4% dos abates, e os chefes perdem cerca de 60% das rolagens.
   - O ajuste que o `INTEGRACAO.md` (passo 8) sugere, `int(tag.right(1))`, quebraria `Itens._opcao`:
     `drops.json → opcoes_de_item` só tem `faixa1`/`faixa2`, e um item mágico ou melhor de faixa 3 daria erro de índice.
9. **Os chefes do Fosso dos Vigilantes não têm tabela.**
   - `ohya_gigante`, `naama_noiva` e `semyaza_juramento` apontam para `drop_ohya`, `drop_naama` e `drop_semyaza`, que só
     existem como alias de texto (`entregas/jerusalem_hermon/dados.json → drops_alias`). O `loot.gd` não resolve alias.
   - Mesmo resolvidos, eles soltariam os itens de missão da Vigília (e inexistentes) do item 2 e as relíquias do deserto.
10. **Os 7 materiais do Egito, os 11 pools `lendario:*` do Egito e o `lendario:hermon`** só existem nas entregas
    (`entregas/egito/conteudo/skills_itens_acrescimo.json`, `entregas/evento_hermon/dados.json → pools_lendarios`).
11. **A Torre nova reaproveita as chaves `torre_horda` e `chefe_torre_1..5`**, que já estão no `v06_extra.json`.
    - Pela regra do `_extras_v06` ("só entra se não existir"), os números novos de `dados_torre.json` não entrariam.
    - O `torre_elite` é novo.
    - Os chefes antigos (`chefes_removidos`: centuriao_ferrabras, malaquias_escudeiro_cego, baraquiel_arauto_do_granizo)
      continuam no jogo.

### D. Mobs e chefes sem tabela ou indefinidos

12. **Mobs sem tabela:**
    - soldado_caido (Cripta 1, nv 8, `mobs.json`, `drop: null`).
    - jambres, hapi, duamutef, qebehsenuef e ammit: 5 "raro" nv 60 da raid, com `drop` ausente.
    - Vigilantes do evento (`drop: null`, de propósito).
    - Leões e Golias do Agrak (`drop: None`, de propósito).
13. **Mobs que aparecem em mapa sem estar definidos:**
    - `cao_de_vala_alfa` e `corvo_de_cinza_carnica` (`entregas/cidade_sao_lazaro/area_inicial.json`).
    - `cervo_de_lume`, `querubim_da_espada`, `serpente_do_eden` e `a_serpente`
      (`design/mapas/mata_do_granizo/mata_do_granizo.json`; estão em `dados.json` da Mata, mas não no `v06_extra.json`).
    - `guardiao_da_aurora` e `guardiao_do_crepusculo` (Amenti).
14. **O espelho de Jerusalém não usa as mesmas tabelas**, ao contrário do que diz o `INTEGRACAO.md` ("Mesmas tabelas de
    drop"):
    - levantado_das_oliveiras e vigilante_acorrentado usam inicial_humanoide; o deserto usa inicial_espectro.
    - **capataz_de_tofete usa inicial_humanoide**; o Capataz do deserto usa elite_inicial. Com isso os Arautos ficam sem
      `lendario:capataz` e **sem nenhuma fonte de `chave:bau_de_ferro`** para os 7 baús de ferro (sobra a gazua, 60%).
    - nefilim_mirrado usa cripta_carne (o espelho usa inicial_humanoide).
    - noiva_afogada usa cripta_monge (o espelho usa cripta_espectro).
15. **Ids repetidos entre entregas** (um sobrescreve o outro ao integrar):
    - mob `ibis_de_thoth`: Atlântida nv 30–40, tabela atl_animal × Egito nv 50–52, tabela egito_animal.
    - item `malho_de_tubal`: Jerusalém (acessório raro nv 5) × evento (arma lendária nv 25 do Mutante).
    - item `pena_de_ibis`: Atlântida × Egito.

### E. Lendários e itens sem fonte

16. **Lendários sem drop** (só recompensa de missão; não é erro, mas não estão no loot):
    - estilhaco_lacre e diapasao_reverso (v05); pena_zacarias e etiqueta_branca (a05); estilhaco_absinto e
      chave_segunda_estrela (d06), todos nv 12.
    - elmo_rafael (f06), faixa_de_linho_rafael nv 150 (g07), pena_que_ficou nv 400 com +30 em tudo (h01).
    - `decreto_vampirico` (nv 12, `lendario:zacarias`) só existe no design.
17. **Relíquias "sugeridas" que não existem como item** (`drops.json → tabelas.chefe_*.reliquias_sugeridas`): veu_de_luto,
    rosario_do_coro, lanca_do_arauto, asa_partida, bocal_calado, dragona_do_general e estandarte_partido.
18. **Itens que não caem em lugar nenhum:**
    - `coagulo_caos` e `engrenagem_viva` (tag `joia:extra`, que nenhuma tabela sorteia).
    - `gazua` (só loja).
    - Atlântida (30–45) não tem nenhum equipamento próprio. O Egito tem só relíquias/únicos de chefe (nv 51–66) e nenhum
      item rolado.
19. **O `lendario:zacarias` (1 item, nv 12) é reaproveitado por 4 fontes:** chefe_zacarias (47% por abate), Relicário
    (~49% por dia), chefe_torre_4/5 (nv 27–30, 41–54%) e Gadiro (nv 45, 47%). Um chefe de nível 45 solta relíquia de
    nível 12, e a relíquia "única" cai toda hora: numa ida diária à Cripta, cerca de 73% de chance.

### F. Faixas de nível: buracos e sobreposição

20. **Áreas:**
    - Sobreposição: Paróquia 1–12, Jerusalém 1–12 (espelho) e Cripta 6–12; Mata 12–30, Torre 12–30 e Catacumba 18–22.
    - Buracos: **45–50** sem área; **70–150** sem nada; Amenti 150 sem farm; **150–400 sem nada** (o nível máximo é 400).
21. **Equipamento:**
    - Faixa1 nv 1–6, faixa2 nv 7–15 (design: 7–18). Não existe item rolado acima do nv 18.
    - Mata, Torre e Atlântida (12–45) soltam no máximo item nv 15.
    - `drops.json → opcoes_de_item._doc` define a faixa 2 como "nível 7–13", e os itens vão até 15/18.
22. **Armas da faixa 2 por classe:**
    - Anjo: 1 arma (nv 9). Cultista: 1 (nv 11). Mutante e Tecnomancer: 2 (até nv 11).
    - As 10 espadas novas do design (nv 8–18) vão só para Anjo, Demônio e Humano.
    - Na prática, Cultista, Mutante e Tecnomancer ficam sem arma nova do nível 11 em diante. Isso vai contra o "DPS
      parecido".

### G. Ouro e chances fora de escala

23. **Elite paga mais ouro que chefe**, porque a fórmula de mob multiplica `arquetipo.xp` (elite = 8) por `ouro_mult`:

    | Mob | Ouro por abate | Chefe de referência | Ouro do chefe |
    |---|---|---|---|
    | Capataz (nv 9, ×3) | 562–1404 | Zacarias (nv 12, ×30) | 720–1800 |
    | ultimo_operador (nv 12) | 749–1872 | Zacarias | 720–1800 |
    | ent_de_cinza (nv 22, ×8, se a tabela for consertada) | 3661–9152 | Torre (nv 15–30) | 600–6000 |
    | touro_do_pilar (nv 42, ×10) | 8736–21840 | Gadiro (nv 45, ×45) | 4050–10125 |
    | escaravelho_rei (nv 58–63, ×8) | 9651–26208 | Hawara (nv 51–54) | 3060–10800 |

    - Raid: o Faraó (nv 60, ×100) dá 12 000–30 000 por jogador (o loot é pessoal).
24. **A joia de refino pela tabela passa muito a curva, e as duas se somam:**

    | Fonte | Joia por abate | Curva no mesmo nível |
    |---|---|---|
    | mata_arauto | 4,0% | nv 20: ~0,37% |
    | torre_horda / catacumba | 4,8% | nv 20: ~0,37% |
    | atl_serpente | 6,8% | nv 45: ~0,73% |
    | atl_coro | 5,8% | nv 45: ~0,73% |
    | elite_mata / elite_atl | 36–39% | – |
    | chefes | 40–76% | – |
    | bau_de_ferro | 25% | – |

    - Entre 10 e 18 vezes a curva de 0,08–0,8% pedida pelo Jefin.
    - `joia:refino` sorteia Angélica e Sanguínea meio a meio, então pela tabela a Sanguínea (+6 → +15) sai tanto quanto a
      Angélica. Na curva ela é a metade.
    - O `LEIAME` das lágrimas diz que tirou a joia da cripta_monge e da cripta_celestial "porque agora quem cuida é a
      curva", mas as tabelas da Mata, Torre, Catacumba, Atlântida e Egito continuam com joia.
25. **Lendário de elite e de raro, alto demais:**
    - lendario:capataz: 11,5% por abate do Capataz, que renasce em 300 s. Dá cerca de 1 relíquia a cada 45 min de farm.
    - lendario:cardo: 27,8% por abate.
26. **Os itens de missão garantidos** (`garantido: missao:*`) caem para todo mundo, a cada abate, tenha ou não a missão.
    Isso vale nos chefes da Cripta, do Egito e do Filho de Cardo; o `loot.gd` não checa `Missoes.precisa_item` para
    `garantido`.

---

## Resumo (15 linhas)

1. Bug grave: as tabelas do `v06_extra` caem em `DROPS[k]`, e o `loot.gd` lê `DROPS["tabelas"]` (`defs.gd:138`). Por isso Mata/Novo Éden, Catacumba e os 5 chefes da Torre (nv 12–30) não soltam nenhum item.
2. Regressão pronta: `design/skills-itens/itens.json` (16/10 13:48) não tem `lagrima_angelica`/`sanguinea` e tem o Elmo de Rafael antigo (+5 em tudo, +200 HP). O próximo `sync.sh` apaga as lágrimas do jogo.
3. Os garantidos dos chefes da Cripta e do Cardo (`estandarte_roido`, `veu_da_carpideira`, `bocal_da_trombeta`, `coracao_de_cardo`) não existem: cai item fantasma a cada abate.
4. `equip:faixa3` tem 0 itens, e o Egito inteiro (nv 50–70) depende dela. O conserto sugerido quebra `opcoes_de_item`, que não tem faixa3.
5. Não existe item rolado acima do nv 15 no jogo (18 no design). Áreas de nível 12–45 soltam só faixa2 (7–15), e os mobs de nível 9–12 do deserto ainda soltam faixa1.
6. O item sorteado ignora o nível do mob: um mob nv 7 solta item nv 15.
7. Os baús não têm `nivel` e usam o do jogador: nível alto farma caixote inicial com ouro e faixa2.
8. Elite paga mais ouro que chefe (Capataz ≈ Zacarias; touro_do_pilar 2× Gadiro; escaravelho_rei > chefes de Hawara).
9. A joia pela tabela dá 4–7% por abate na Mata/Torre/Atlântida, 10 a 18 vezes a curva pedida, e soma com a curva. A Sanguínea sai meio a meio.
10. `lendario:zacarias` (1 item nv 12) sai de Zacarias, do Relicário, da Torre 4/5 e de Gadiro (nv 45). Capataz 11,5% e Cardo 27,8% de relíquia por abate.
11. Jerusalém não espelha as tabelas: o Capataz de Tofete não é elite_inicial, então os Arautos ficam sem chave de baú de ferro e sem relíquia; os 3 chefes do Fosso apontam para alias não resolvidos.
12. Mobs sem definição em mapas (cao_de_vala_alfa, corvo_de_cinza_carnica, cervo_de_lume, querubim_da_espada, serpente_do_eden, a_serpente, guardiões de Amenti) e mobs sem tabela (soldado_caido, 5 raros da raid).
13. Ids repetidos entre entregas: `ibis_de_thoth` (Atlântida × Egito), `malho_de_tubal` (Jerusalém × evento), `pena_de_ibis`.
14. Buracos de nível: 45–50, 70–150 e 150–400 sem conteúdo. Sobreposição: 1–12 (deserto, Jerusalém, Cripta) e 12–30 (Mata, Torre, Catacumba).
15. Armas da faixa 2: Anjo e Cultista com 1 arma cada, Mutante e Tecnomancer com 2 (até nv 11). As espadas novas do design vão só para Anjo, Demônio e Humano, o que fere o "DPS parecido". `joia:extra` e o pity de relíquia (6 vitórias) não têm efeito.
