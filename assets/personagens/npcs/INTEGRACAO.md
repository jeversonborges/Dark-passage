# NPCs com modelo próprio · guia de integração

**Não vai na 0.9.3** (pedido do Jefin em 17/10/2026: "não vamos enviar na 9.3, vamos só adiantar"). Fica pronto aqui
para a thread "Prévia jogável e área inicial" integrar numa versão seguinte.

## O que tem aqui
Uma pasta por NPC (`<id>/`) no formato de `assets/personagens/<classe>/`: `idle.png` e `walk.png` (linhas S, SE, E,
NE, N, NW, W, SW; colunas = quadros), `sprites.json` (frame_size, anchor_feet, anims), GIFs de conferência.
Pranchas de prévia em `_previa/`. Fontes: `tools/sprite-pipeline/npcs/` (um módulo por NPC, `kit.py` comum).

## NPCs prontos (38)
Vela: capita_odete, doutor_anselmo, mae_cardo, tobias_pavio, gaspar_bigorna, zaqueu_vendedor (Belmiro).
Cidade, cemitério e biblioteca: simao_coveiro, isaura_radialista, corvina_atravessadora, nina, eulalia_prado, frei_anacleto.
Capela: madre_ivone, comandante_abdiel, malfas, irmao_lucio.
Egito: tuya_nomarca, hapu_mercador, nefer_aguadeira, besankh_ferreiro, ahmose_barqueiro, meritre_barqueira, reis_abdu,
djedi_mago, diaprepes_atlante, dalva_ferraz, conego_barnabe, senebtisi_sacerdotisa.
Jerusalém, Hermon e Viveiro: sariel_porta, hulda_escada, henoc_escriba, rispa_vigilia, jael_escuta,
joana_enxertadeira, tadeu_vigia, rute_abelheira.
Tubal, Bartimeu, Zilpa e Zaqueu cobrador usam os modelos da Vela (tabela de réplicas abaixo).

## Como ligar no jogo
1. `game/tools/sync.sh` só copia o primeiro nível de `assets/personagens/`. Copie cada pasta para
   `assets/personagens/<id>/` (ou estenda o sync para ler `npcs/*`).
2. Em `game/data/sprites_substitutos.json`, troque a entrada do NPC por `"npc:<id>": {"usa": "<id>"}`.
   - `frei_anacleto`: manter `"fantasma": true` (é o espírito emparedado; o modelo já traz a parede).
   - Carrinhos que reaproveitam o mesmo vendedor: `tobias_carrinho` → `tobias_pavio`, `nefer_carrinho` →
     `nefer_aguadeira`, `bartimeu_carrinho` → `tobias_pavio` (ver réplicas abaixo).
   - `esfinge_amenti` não tem modelo: é uma voz que sai da pedra.

## Ferreiros: forja animada
Os ferreiros (`gaspar_bigorna` e `besankh_ferreiro`, no Egito) já trazem bigorna, fogareiro, balde de têmpera e as faíscas dentro do sprite.
Não anda: `walk` é igual ao `idle` (8 quadros a 8 fps, 1 golpe por segundo).
- Som: `assets/audio/ambiente/forja.ogg` (loop de 60 s, brasa + fole) como som posicional no ponto da forja, e
  `sfx/itens/forja_martelo` (3 variações) tocado no quadro 3 do idle (`GOLPE` no módulo), sorteando a variação.
- No mapa, o ponto do NPC precisa de ~1,5 m livre à esquerda dele (fogareiro) e à frente (bigorna).

## Réplicas nas 3 cidades iniciais (Jefin 17/10/2026)
Os NPCs básicos (ferreiro, poções e vendedores em geral) usam **o mesmo modelo** nas 3 cidades iniciais, cada um com
**nome próprio**, para não parecer a mesma pessoa em três lugares. Exceção: **Gustavo, o Primarca** (baú), que é o
mesmo em todas. Os NPCs de história (Odete, Anselmo, Malfas, Lúcio, Abdiel, Madre Ivone...) mantêm modelo próprio.

| Função | Acampamento da Vela | Capela de São Lázaro | Jerusalém | Modelo |
|---|---|---|---|---|
| Ferreiro | Gaspar Bigorna | Ezequias, o Fole (novo) | Tubal, o Malho | `gaspar_bigorna` |
| Poções (carrinho) | Tobias 'Pavio' | Matias Cera (novo) | Bartimeu, o Cego das Brasas | `tobias_pavio` |
| Comida / caldeirão | Mãe Cardo | Irmã Dorcas (nova) | Zilpa, a Hissopeira | `mae_cardo` |
| Convites | Belmiro (era "Zaqueu") | Nabal (novo) | Zaqueu, o Cobrador | `zaqueu_vendedor` |

- Renomear o `zaqueu_vendedor` da Vela para **Belmiro** em `design/missoes/dados/npcs.json` (e falas que citam o
  nome): o Zaqueu cobrador de Jerusalém é o da Bíblia e fica com o nome.
- Os novos da Capela precisam de entrada em `npcs.json`, loja em `lojas.json` e ponto no layout (thread de Missões e
  Level design); o visual é só `"npc:<id>": {"usa": "<modelo>"}`.
- Bartimeu é cego: se quiserem diferenciar, `"tint"` mais escuro basta; o modelo é o do Tobias.

## Regerar
Instalação (container novo): `apt-get install -y libegl1 libgl1-mesa-dri` e um venv com `pip install bpy==4.2.0
pillow numpy imageio` em `/opt/bpy42`. Depois, em `tools/sprite-pipeline/npcs/`:
`bash lote.sh <id> ...` (render + folha; `RESUME=1` retoma). Teste rápido:
`/opt/bpy42/bin/python render.py -- <id> /tmp/bt/<id> teste`.

## 18/10: Zaqueu do convite com o Zacarias antigo (para a 0.9.5)

Jefin pediu o modelo antigo do Zacarias (a armadura astral, `tools/sprite-pipeline/monstros/zacarias_v2.py`) como
modelo do NPC que vende item de evento. O modelo foi re-renderizado só em idle e walk, no formato de monstro,
em `assets/monstros/zacarias_antigo/` (folhas `zacarias_antigo_idle.png` / `_walk.png` + `meta.json`; prévia em
`previa/`). O chefe `zacarias` (visual 3, Egito) não mudou.

No branch `claude/npcs-cetro-094`:
- `game/assets/ext/monstros/zacarias_antigo/` + `data/ext/sprites.json` (manifest.py);
- `data/sprites_substitutos.json`: `"npc:zaqueu_vendedor": {"usa": "zacarias_antigo", "escala": 0.8}` (2,2 m);
- `data/mapas/area_inicial.json`: o Zaqueu do convite não estava em mapa nenhum; entrou na praça da Vela, entre as
  velas da matriz, em frente ao muro da capela (`pos [67.5, 105.5]`, olhando para a praça). Perto da lâmpada o
  `predio_enterrado` tapa qualquer NPC até o jogador chegar perto (a Zulmira sofre disso); ali ele fica visível de
  longe. A `loja_zaqueu` (Convite dos Irin, 300 de ouro) já existia. Foto: `assets/monstros/zacarias_antigo/previa/zaqueu_na_vela.png`.
O Zaqueu cobrador de Jerusalém continua com o modelo humano.
