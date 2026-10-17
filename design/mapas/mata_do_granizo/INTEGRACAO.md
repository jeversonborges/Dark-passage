# A Torre: como encaixar no jogo

**Atualização (Jefin, 11/10 09:29): agora só A Torre, para upar do 12 ao 30, com a entrada na área inicial. O pedaço de
floresta vem depois** (ela foi aprovada às 10:15 e está pronta: veja a Fase 2).

Para a thread "Prévia jogável e área inicial". Pedido do Jefin (11/10/2026): "faz um pedaço acima simples, e a torre
pra gente upar, coloca uns mobs 12+ lá até o 30". Versão simples: arte recolorida estilo MU, sem arte nova.
Tudo é gerado por `gerar.py` (não editar os JSON à mão). Plantas: `planta_*.png`.

## Arquivos

| Arquivo | O quê |
|---|---|
| `torre_1.json` ... `torre_5.json` | andares da Torre: patamar, arena (horda + chefe), elevador que sobe com `requer_flag: venceu_<chefe>` |
| `dados.json` | `mobs` (formato do `v06_extra.json`), `sprites` (formato do `sprites_substitutos.json`), `chefes` (formato do `chefes.json`), `drops` (tabelas), `ligacao_area_inicial`, `nomes_mapa_hud` |

Mesmo formato de `game/data/mapas/` (o da Cripta 0.7.8): grade, terreno, zona_grade, zonas, objetos, spawns, props,
luzes, camera, spawn, ceu, pisos.

## Entrada na área inicial

Acrescentar em `area_inicial.json` o que está em `dados.json > ligacao_area_inicial`: o portal em (87.5, 24.5), na
fresta aberta da borda norte do deserto (x 81 a 92), mais a `torre_vigia` e um braseiro com luz como marco. Todos os
andares têm saída de volta para (87.5, 27.5), logo abaixo da entrada.

## Faixas de nível

1º andar 12-15 (chefe nv 15), 2º 16-19 (19), 3º 20-23 (23), 4º 24-27 (27), 5º 28-30 (30). A horda nasce no nível do
andar (`horda.nivel`), não no nível padrão de cada mob.

## O que muda no código

1. **Dados.** Juntar `dados.json > mobs` às defs (como o `v06_extra`; a `base` é id de `design/combate/mobs.json`),
   `sprites` ao `sprites_substitutos.json`, `chefes` ao `Defs.CHEFES` e `drops` às tabelas. Os nomes do HUD estão em
   `nomes_mapa_hud`.
2. **Horda antes do chefe** (`chefe.horda` em cada andar):
   `{"ondas": [{mob: qtd}, ...], "nivel": [min, max], "pontos": [[x, y] x4], "pausa_s": 3, "chefe_depois": true}`.
   Ao entrar na arena a porta fecha (como hoje). As ondas nascem nos `pontos`, uma de cada vez: a próxima vem
   `pausa_s` depois da anterior morrer. Os mobs da horda não renascem e acordam já no jogador. Com a última onda
   morta, o chefe surge (no `pos`) e a luta segue como as da Cripta. Se o grupo morrer, reseta a horda junto.
3. **Invocação genérica.** Os chefes da Torre usam `"invoca"` com ids novos (`chamar_caes`, `chamar_incendiarias`...).
   No `chefe_ctl.gd`, `_usar` só invoca com os ids da Celeste e do Zacarias: basta tratar qualquer ataque com
   `a.has("invoca")` pelo `_invocar`.
4. **Nome do golpe.** Alguns ataques reaproveitam a mecânica de ids que já existem (`arrasto`, `vomito_de_brasa`,
   `lanca_do_juizo`, `pranto_que_cai`, `marca_do_juizo`) e trazem `"nome"` para o texto na tela ("Granizo e Fogo",
   "Olhar que Arde"...). Usar `a.get("nome", id)` onde o nome do golpe aparece.
5. **Elevador.** Os portais do elevador usam o visual `escada_subida` (não há arte de elevador ainda) e o adereço
   `gaiola_suspensa` ao lado. O andar 5 devolve à área inicial depois do chefe; todo patamar de chegada tem saída para a área inicial.

## Fase 2: Novo Éden, a floresta (id `mata_do_granizo`; aprovada pelo Jefin em 11/10 10:15, entra na 0.8.3)

O mapa está pronto em `mata_do_granizo.json` (planta: `planta_mata_do_granizo.png`). Ele é exterior, nível 12 a 30,
com 8 zonas (o Viveiro é zona segura), 10 spots estilo MU (12 mobs, renascimento de 14 s; só a Frente de Queimada é
agressiva, em grupos de 3; os 3 do Coração da Mata, do 22 ao 30, entraram na 0.8.3), 4 fogueiras de descanso com `carrinho_tobias` (`ponto: descanso`), 1 elite (Ent-de-Cinza,
nível 22) e a entrada da Torre no topo. Os spawns trazem `temperamento`, `respawn_s`, `spot`, `motivo` e, nos
territoriais, `ancora`/`raio_territorio`, como os spots do deserto. Props de borda têm `decor_moldura`.

**0.8.3 (decisão do Jefin): entra só a mata, nível 12 a 30. A Torre fica para a próxima versão:** a porta dela na mata
tem `requer_flag: "torre_aberta"` e fica trancada; não é preciso integrar os andares nem o código de horda agora.
O `dados.json` desta pasta já está no modo fase 2 (o portal do deserto leva à mata). Os mobs da mata estão em
`dados.json > mobs` e `sprites` (os chefes e drops de chefe são da Torre e podem esperar).

Quando a Torre entrar (rode de novo `python3 gerar.py fase2` e `python3 gerar.py mata`):
- o portal do deserto em (87.5, 24.5) passa a levar à mata (`dados.json > ligacao_area_inicial`); tire do deserto a
  `torre_vigia` e o braseiro da fase 1;
- as saídas dos andares da Torre passam a devolver o jogador à mata, ao lado da porta da Torre (16.5, 15.5);
- a mata já tem o portal de volta ao deserto (chega em 87.5, 27.5) e a porta da Torre (leva ao 1º andar).

## 0.8.4: visual do Novo Éden, Catacumba das Raízes e portal de dungeon (adiados da 0.8.3)

Pedido do Jefin: "existe uma catacumba abaixo da árvore; já na 8.3 toda entrada de Dungeon faça um portal para deixar
claro que é uma dungeon".

- **`catacumba_das_raizes.json`** (planta `planta_catacumba_das_raizes.png`): 1 andar feito com o gerador da Cripta,
  nível 18 a 22, toda agressiva. Escada de chegada, Ossário das Raízes (com 2 nichos e baús), Poço do Amargo
  (acampamento dos envenenadores) e a arena A Raiz-Mestra. O chefe é **Bento Fel, o Coveiro do Amargo** (`bento_fel`,
  nível 22, em `dados.json > chefes`): ele só usa mecânicas que já existem (`arrasto`, `vomito_de_brasa`,
  `pranto_que_cai`, com `"nome"` próprio) e um `invoca` (`chamar_raizes`), então precisa só dos itens 3 e 4 acima.
  Não tem horda: é uma luta de chefe igual às da Cripta. A saída pela raiz abre com `venceu_bento_fel`.
- Mobs novos em `dados.json > mobs/sprites` (recolor): `raiz_ossuda`, `enterrado_florido`, `envenenador_da_comunhao`.
  Drops: `catacumba` e `chefe_catacumba`. Nome no HUD em `nomes_mapa_hud`.
- **Na mata:** a Árvore-Mãe (`arvore_morta_grande` com `escala: 1.8` e `marco: "arvore_mae"`, até ter arte própria)
  em (66.5, 63.5), na borda norte do Viveiro, e o portal da catacumba em (66.5, 66.5). A volta chega em (66.5, 68.5).
- **Portal de dungeon** (kit de cenário, `assets/ambiente/objetos/`): `portal_dungeon` (véu rubro) e
  `portal_dungeon_lume` (véu ciano). Arco gótico de pedra com véu de luz. Prévia: `previa_portal_dungeon.png`.
  Usar como visual de toda entrada de dungeon: a **Cripta** (porão do Abatedouro, trocar o visual da entrada por
  `portal_dungeon`), a **Torre** (a porta na mata já usa `visual: "portal_dungeon"`, segue trancada) e a **Catacumba**
  (`portal_dungeon_lume`, já no mapa como prop e como `visual` do portal). Se o cliente não tiver o visual `portal_*`
  mapeado, basta desenhar o prop de mesmo nome no lugar do sprite de escada. Rode `game/tools/sync.sh` para levar os
  objetos novos.

**Visual do Novo Éden** (aprovado pelo Jefin em 11/10, prévia `previa_novo_eden.png`): o miolo da mata (Viveiro, Lago,
Fundo e Coração) está vivo e acende em ciano; as bordas queimadas (Linha de Cinza, Bordas, Frente, Estrada) continuam
cinza. O `mata_do_granizo.json` já foi regerado com isso:
- piso novo `musgo_lume` (`tiles/musgo_lume.png` + bordas); o mapa traz `pisos.e = "musgo_lume"`;
- objetos novos do kit: `arvore_lume`, `arvore_lume_2`, `arvore_mae` (marco, 13 m), `arvore_jovem_lume`, `palmeira_lume`,
  `palmeira_lume_2`, `folha_larga`, `flor_lume`, `flor_lume_2`, `moita_lume`, `cipo_lume`, `campanula`, `tanque_latao`;
- `ceu` noturno azul-esverdeado e luzes ciano (`luzes`) espalhadas no miolo. As copas são altas: se esconderem o
  jogador, use o mesmo esmaecimento por proximidade das árvores grandes do deserto.

## O que fica para depois (não bloqueia)

- Arte própria dos mobs e chefes (hoje recolor de folhas existentes) e da Torre (hoje `torre_vigia` do kit).
- Drops: usam `equip:faixa2` até a thread de Combate criar a faixa dos níveis 20-30; números de chefe são a fórmula
  `hp = 26 × nível²`, para a thread de Combate afinar.
- Missões da mata (continuação da linha F, Simão como restaurador), NPCs da Enxertia no Viveiro e a arte viva do `conceito.md`.

## Revisão "Gênesis" do Novo Éden (16/10/2026, depois da 0.9.2)

Detalhes em `eden.md`. Para o jogo:

1. `bash game/tools/sync.sh` e `python3 game/tools/pisos.py` (objetos e pisos novos do kit "Gênesis", folhas de
   `cervo_de_lume`, `querubim_da_espada`, `serpente_do_eden`), depois `python3 game/tools/manifest.py`.
2. Copiar `mata_do_granizo.json` (regerado por `gerar.py mata`) para `game/data/mapas/`. Mesmo id, mesmos portais
   (Torre, Catacumba, volta ao deserto) e mesmo formato; campos novos: `agua` (cores da água) e `lugares` (marcos).
3. Mobs: juntar `dados.json > mobs` em `v06_extra.json` (entram `cervo_de_lume`, `querubim_da_espada`,
   `serpente_do_eden`, `a_serpente`; os antigos continuam) e `dados.json > sprites` em `sprites_substitutos.json`
   (só `a_serpente` precisa de entrada: `usa serpente_do_eden`, `escala 1.6`, `tint #c8ffb0`; os outros têm folha própria).
4. Aplicar `patches/chao_agua.diff` em `game/scripts/client/chao.gd`: uniforms de cor da água lidos do campo `agua`
   do mapa, padrão igual ao Rio Amargo (nada muda no deserto). Sem o patch o mapa funciona, mas a água dos quatro rios
   sai verde-amarga.
5. Nada muda na sim: spots, grupos, `temperamento`, `ancora` e `raio_territorio` seguem o formato de hoje.
6. A Torre no mapa agora é o prop `torre_radio` (thread da Torre de rádio, já em `assets/ambiente`), centro (11.5, 9.0),
   porta do portal em (16.1, 9.0) e chegada ao sair em (17.3, 10.0) (`PORTA_TORRE`/`CHEGADA_TORRE` em `gerar.py`; os
   `torre_*.json` desta pasta foram regerados com a nova chegada).
