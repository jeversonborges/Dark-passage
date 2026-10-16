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
| `codigo/chefe_ctl.patch` | 9 ganchos em `game/scripts/sim/chefe_ctl.gd` (mecânicas + trava) | `diff -u` |
| `codigo/jogador.patch` | 3 linhas em `game/scripts/sim/jogador.gd`: baú de chefe com a parte de cada um | `diff -u` |
| `codigo/teste_egito.gd` | teste headless das 9 lutas | à mão |
| `codigo/teste_trava.gd` | teste da trava diária/semanal e do baú por jogador | à mão |
| `conteudo/*_acrescimo.json` | 43 missões, 13 NPCs, diálogos, 82 itens (43 relíquias de chefe e 13 peças de conjunto), bestiário, objetos, baús, lojas, locais, e `skills_itens_acrescimo.json` (listas de saque, materiais, conjuntos) | `conteudo_egito.py` + `design/mapas/egito/itens_egito.py` |

Os geradores ficam no repositório; para refazer: `cd design/mapas/egito && python3 gerar.py && python3 dungeons_egito.py && python3 dados_egito.py`,
depois `python3 entregas/egito/conteudo_egito.py` (ele mesmo confere tudo com o `validar.py` de Missões numa cópia temporária;
a última rodada deu `OK: 99 missões, 33 NPCs, 33 diálogos, 164 itens, 73 monstros, 52 objetos/baús`).

## Passo a passo

1. **Mapas.** Copie `mapas/*.json` para onde o `sync.sh` leva os mapas (`game/data/mapas/`). O formato é o mesmo da Cripta
   (classe `Andar` de `design/mapas/cripta/gerar.py`), com `agua` (letras `w` funda e bloqueada, `r` rasa) igual ao Rio Amargo.
2. **Mobs, chefes e drops.** Junte `dados.json` em `game/data/v06_extra.json`: `mobs` → `mobs`, `chefes` → `chefes`,
   `drops` → `drops.tabelas`. O `Defs._extras_v06` já aceita ids novos. As entradas `base` das versões de dungeon são só referência:
   os números já vêm completos.
3. **Código dos chefes.** Copie `codigo/chefe_egito.gd` para `game/scripts/sim/` e aplique os patches da raiz do repositório:
   `patch -p1 < entregas/egito/codigo/chefe_ctl.patch && patch -p1 < entregas/egito/codigo/jogador.patch`
   (no ChefeCtl tudo fica protegido por `if egito != null`, e no baú só vale para `loot_de_grupo`: as lutas antigas não mudam). Rode `godot --headless --import` uma vez por causa do `class_name` novo.
4. **Teste.** Copie `codigo/teste_egito.gd` e `codigo/teste_trava.gd` para `game/tools/` e rode
   `godot --headless --path game --script res://tools/teste_egito.gd` (uns 100 s: os 9 chefes chegam à última fase e morrem,
   sem erro de script; o Faraó chega à fase 5) e `.../teste_trava.gd` (o travado fica fora da arena, o baú abre uma vez).
5. **Conteúdo.** Acrescente cada `conteudo/*_acrescimo.json` (menos o `skills_itens_acrescimo.json`, ver passo 7) ao arquivo de mesmo nome em `design/missoes/dados/`
   (as chaves batem: `missoes`, `npcs`, `dialogos`, `itens`, `monstros`, `objetos`+`baus`, `lojas`; em `locais.json`,
   `areas` e `dungeons` entram nas listas e `spots_pedidos` em `spots.pedidos`). Rode `python3 design/missoes/validar.py`,
   depois `python3 design/skills-itens/fontes/gerar_json.py` e `game/tools/sync.sh`. Os ids de missão têm prefixo `eg_`
   porque `k01`, `v01`, `a01`... já existem na área inicial.
6. **Ligação.** Linha 7 do bonde-veleiro: a estação de Mênfis está em (151.5, 106.5) no `egito.json`. Ponha a ponta de lá
   na estação de São Lázaro (`dados.json` → `ligacao.estacao_sao_lazaro`, nível mínimo 50) e, depois, em Jerusalém.
7. **Saque (Jefin, 16/10: menos chance, mais variedade).** Mobs: 8 a 12% de chance de item por abate (antes 20 a 32%).
   Chefes: 2 rolagens (Faraó 3), antes 3 a 6. Cada chefe tem a sua lista de 4 ou 5 relíquias (`lendario:<chefe>`, peso 7) e a masmorra
   tem um conjunto (`lendario:regalia_de_sobek`, 5 peças; `lendario:regalia_do_farao`, 8 peças). Os itens estão em `itens_acrescimo.json`;
   as listas, os 7 materiais e os conjuntos vão para `design/skills-itens/fontes/itens_data.py` (`skills_itens_acrescimo.json`), e o
   `gerar_json.py` já põe a tag nos itens que estão numa lista. Nenhum código novo de saque é preciso para isso.
8. **Faixa de itens 3 (nível 50 a 70).** As tabelas de drop do Egito usam `equip:faixa3`, que ainda não existe:
   - em `game/scripts/sim/loot.gd`, troque `var f := 1 if tag.ends_with("1") else 2` por
     `var f := int(tag.right(1))` e, nos baús, `var f := 1 if nivel < 7 else 2` por `var f := 1 if nivel < 7 else (2 if nivel < 50 else 3)`;
   - em `Itens.gerar_equip`, trate a faixa 3 como a 2 com os valores escalados até a thread de Skills/itens fechar os números;
   - em `design/skills-itens/fontes/gerar_json.py`, `faixa(n)` passa a devolver `faixa3` para `n >= 50`. Os itens de nível 50+
     ficam com a thread de Skills/itens (as recompensas únicas com nome já estão em `itens_acrescimo.json`).
   Enquanto a faixa 3 não existir, `item_da_tag` devolve `{}` e os chefes deixam ouro, consumíveis, materiais e as relíquias com nome: nada quebra.
9. **Sintonia da raid.** O portal da raid (12.5, 192) pede a flag `sintonia_coracao` e nível 60. Quem dá a flag é o diálogo
   que conclui a missão `eg_n03` (ação `definir_flag`). O portal do Labirinto (60.5, 31) pede nível 50.
10. **Trava (Jefin, 16/10).** Cada chefe do Labirinto pode ser morto 1 vez por dia; cada chefe da raid, 1 vez por semana.
   Reset às 6h de Brasília (09:00 UTC); o semanal na quarta. Fica em `flags["trava_<chefe>"]` (horário Unix do reset), que já é salvo
   com a conta. Quem está travado não acorda o chefe nem é alvo dele; se há alguém sem trava no mapa, o travado é empurrado para fora
   da arena com um aviso; se todos estão travados, o chefe dorme e não é alvejável, e eles atravessam. O saque do chefe já é pessoal
   (`participantes` do WorldSim); o baú do chefe (`loot_de_grupo`) abre uma vez por pessoa por trava. O HP dos chefes escala pelo tamanho do grupo (`escala_grupo`): na dungeon 1 + 0,75 por jogador extra;
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
