# Egito, a Terra Negra · guia de integração (para a thread "Prévia jogável e área inicial")

Área de nível 50 a 70, com o Labirinto de Hawara (dungeon de nível 50, 3 chefes) e o Coração Endurecido
(raid de nível 60, de 5 a 10 jogadores, 6 chefes). Nada disto mexe no cliente publicado: entra na próxima versão
que a Prévia montar, depois da 0.9.2. **Não publique o cliente por esta entrega** (a regra de lote continua valendo).

## O que tem aqui

| Arquivo | O quê | Gerado por |
|---|---|---|
| `mapas/egito.json` | área aberta 200x200: 17 zonas, 17 spots, 106 grupos, 49 objetos, 18 baús, 14 NPCs | `design/mapas/egito/gerar.py` |
| `mapas/hawara_1..3.json` | os 3 andares do Labirinto de Hawara | `design/mapas/egito/dungeons_egito.py` |
| `mapas/coracao_1..6.json` | os 6 salões da raid | idem |
| `mapas/planta_*.png` | plantas de conferência (não vão para o jogo) | idem |
| `dados.json` | mobs, chefes (com `escala_grupo` e `mecanica_egito`), tabelas de drop, sprites substitutos, nomes do HUD, ligação, dungeons | `design/mapas/egito/dados_egito.py` |
| `codigo/chefe_egito.gd` | as mecânicas das 9 lutas (classe `ChefeEgito`) | à mão |
| `codigo/chefe_ctl.patch` | 7 ganchos em `game/scripts/sim/chefe_ctl.gd` | `diff -u` |
| `codigo/teste_egito.gd` | teste headless das 9 lutas | à mão |
| `conteudo/*_acrescimo.json` | 43 missões, 13 NPCs, diálogos, 27 itens, bestiário, objetos, baús, lojas, locais | `conteudo_egito.py` |

Os geradores ficam no repositório; para refazer: `cd design/mapas/egito && python3 gerar.py && python3 dungeons_egito.py && python3 dados_egito.py`,
depois `python3 entregas/egito/conteudo_egito.py` (ele mesmo confere tudo com o `validar.py` de Missões numa cópia temporária;
a última rodada deu `OK: 99 missões, 33 NPCs, 33 diálogos, 109 itens, 73 monstros, 52 objetos/baús`).

## Passo a passo

1. **Mapas.** Copie `mapas/*.json` para onde o `sync.sh` leva os mapas (`game/data/mapas/`). O formato é o mesmo da Cripta
   (classe `Andar` de `design/mapas/cripta/gerar.py`), com `agua` (letras `w` funda e bloqueada, `r` rasa) igual ao Rio Amargo.
2. **Mobs, chefes e drops.** Junte `dados.json` em `game/data/v06_extra.json`: `mobs` → `mobs`, `chefes` → `chefes`,
   `drops` → `drops.tabelas`. O `Defs._extras_v06` já aceita ids novos. As entradas `base` das versões de dungeon são só referência:
   os números já vêm completos.
3. **Código dos chefes.** Copie `codigo/chefe_egito.gd` para `game/scripts/sim/` e aplique o patch:
   `cd game && patch -p1 < ../entregas/egito/codigo/chefe_ctl.patch` (são 7 linhas, todas protegidas por `if egito != null`;
   as lutas antigas não mudam). Rode `godot --headless --import` uma vez por causa do `class_name` novo.
4. **Teste.** Copie `codigo/teste_egito.gd` para `game/tools/` e rode
   `godot --headless --path game --script res://tools/teste_egito.gd`. Leva uns 100 s. Resultado esperado: os 9 chefes
   chegam à última fase e morrem, sem erro de script (o Faraó chega à fase 5, a décima praga).
5. **Conteúdo.** Acrescente cada `conteudo/*_acrescimo.json` ao arquivo de mesmo nome em `design/missoes/dados/`
   (as chaves batem: `missoes`, `npcs`, `dialogos`, `itens`, `monstros`, `objetos`+`baus`, `lojas`; em `locais.json`,
   `areas` e `dungeons` entram nas listas e `spots_pedidos` em `spots.pedidos`). Rode `python3 design/missoes/validar.py`,
   depois `python3 design/skills-itens/fontes/gerar_json.py` e `game/tools/sync.sh`. Os ids de missão têm prefixo `eg_`
   porque `k01`, `v01`, `a01`... já existem na área inicial.
6. **Ligação.** Linha 7 do bonde-veleiro: a estação de Mênfis está em (151.5, 106.5) no `egito.json`. Ponha a ponta de lá
   na estação de São Lázaro (`dados.json` → `ligacao.estacao_sao_lazaro`, nível mínimo 50) e, depois, em Jerusalém.
7. **Faixa de itens 3 (nível 50 a 70).** As tabelas de drop do Egito usam `equip:faixa3`, que ainda não existe:
   - em `game/scripts/sim/loot.gd`, troque `var f := 1 if tag.ends_with("1") else 2` por
     `var f := int(tag.right(1))` e, nos baús, `var f := 1 if nivel < 7 else 2` por `var f := 1 if nivel < 7 else (2 if nivel < 50 else 3)`;
   - em `Itens.gerar_equip`, trate a faixa 3 como a 2 com os valores escalados até a thread de Skills/itens fechar os números;
   - em `design/skills-itens/fontes/gerar_json.py`, `faixa(n)` passa a devolver `faixa3` para `n >= 50`. Os itens de nível 50+
     ficam com a thread de Skills/itens (as recompensas únicas com nome já estão em `itens_acrescimo.json`).
   Enquanto a faixa 3 não existir, `item_da_tag` devolve `{}` e os chefes só deixam ouro, consumíveis e as recompensas fixas: nada quebra.
8. **Sintonia da raid.** O portal da raid (12.5, 192) pede a flag `sintonia_coracao` e nível 60. Quem dá a flag é o diálogo
   que conclui a missão `eg_n03` (ação `definir_flag`). O portal do Labirinto (60.5, 31) pede nível 50.
9. **Trava.** Labirinto: um baú por chefe por dia. Raid: um baú por chefe por semana, `loot_de_grupo: true` (cada jogador
   rola a sua parte). O HP dos chefes escala pelo tamanho do grupo (`escala_grupo`): na dungeon 1 + 0,75 por jogador extra;
   na raid 5 de base + 0,2 por jogador, até 10.

## Eventos novos para o cliente

O `ChefeEgito` emite eventos que o cliente ainda não desenha. Até ganharem arte própria, mostrar como `aviso` já basta:

| Evento | Dados | Mostrar |
|---|---|---|
| `chefe_barra` | `{id, nome, valor, max}` | segunda barra no HUD do chefe (Sede de Sekhmet, Luz da Lanterna de Rá, Balança de Anúbis) |
| `enigma` | `{id, glifos:[3], dica, t}` | os 3 glifos no peito da Esfinge, grandes no centro da tela |
| `marca_egito` | `{id, marca, pilhas}` | ícone em cima do jogador (veneno de Serket, Coração/Pena, doença da Peste) |
| `portas_marcadas` | `{pos:[...], t, por_porta}` | brilho vermelho nos lintéis da décima praga |
| `agua_arena` | `{sobe}` | sobe a água da arena de Petsuchos |
| `chefe_some` | `{id, some}` | chefe some (Serket entocada, Janes no vínculo) |
| `ankh` | `{i, aceso}` | acende/apaga os ankhs da câmara de Serket |
| `canal` / `canal_fim` | `{id, t, nome}` / `{id, ok}` | barra de conjuração em cima do mob (Jambres levantando o irmão) |

## Arte que ainda falta

- **Monstros:** sendo feitos no Blender pelos ajudantes desta thread (`tools/sprite-pipeline/monstros/`, saída em
  `assets/monstros/`). Quem não tiver folha usa o substituto de `dados.json` → `sprites` (base recolorida).
- **Cenário da área aberta:** kit do Egito em `assets/ambiente/` (templos, pirâmides, colossos, casas de lama, papiro,
  palmeiras, feluca...). Os props que o `egito.json` pede e ainda não têm arte aparecem na lista do `render.py`.
- **Interiores da dungeon e da raid** (próximo lote): paredes `parede_hawara*`/`parede_duat*`, pisos `laje_hawara`, `laje_duat`,
  `laje_tura`, `laje_ocre`, `entulho`, `areia_calcario`, `quartzito`, `convés_barca`, e os props das arenas (barca de Rá,
  balança de Maat, sarcófago sem nome, portas falsas, ninhos de Serket, ankhs, jarras de cerveja ocre, vasos canópicos etc.).
  A lista completa sai de `grep -o '"kind": "[a-z_]*"' mapas/hawara_*.json mapas/coracao_*.json | sort -u`.
