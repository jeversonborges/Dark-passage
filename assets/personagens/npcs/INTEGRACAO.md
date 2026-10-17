# NPCs com modelo próprio · guia de integração

**Não foi na 0.9.3** (pedido do Jefin em 17/10/2026: "não vamos enviar na 9.3, vamos só adiantar"); ligado no jogo na
0.9.4 (seção "Como foi ligado" abaixo).

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

## Como foi ligado (0.9.4)
- `game/tools/sync.sh` copia também `assets/personagens/npcs/*/` (sprites.json + PNGs das anims, sem GIF) para
  `game/assets/ext/personagens/<id>/`; `game/tools/manifest.py` gera a chave `<id>` em `game/data/ext/sprites.json`.
- `game/data/sprites_substitutos.json`: `"npc:<id>": {"usa": "<id>"}` para os 36 (`frei_anacleto` com `"fantasma": true`).
  Sem entrada, `game/scripts/client/unidade.gd` usa a pasta com o id do NPC quando ela existe (senão, `classe_visual`).
- Carrinhos: `tobias_carrinho` → `tobias_pavio`, `nefer_carrinho` → `nefer_aguadeira`, `bartimeu_carrinho` → `tobias_pavio`.
- Forja: `"sons": {"loop": "ambiente/forja", "quadros": {"idle": {"3": "itens/forja_martelo"}}}` nas entradas de
  `gaspar_bigorna`, `besankh_ferreiro` e `tubal_malho`. `unidade.gd` toca a martelada quando a animação cruza o quadro
  (uma por golpe) e pede o loop posicional todo quadro (`Audio.loop_em`, -6 dB); o loop para sozinho quando o NPC sai.
- Réplicas (ids reais de `npcs.json`): Jerusalém `tubal_malho` → `gaspar_bigorna`, `bartimeu_brasas` e
  `bartimeu_carrinho` → `tobias_pavio` (tint um pouco mais escuro), `zilpa_hissopo` → `mae_cardo`,
  `zaqueu_cobrador` → `zaqueu_vendedor`. Na Capela só existem Malfas (ferreiro + loja) e Lúcio (loja), com modelo
  próprio: Ezequias, Matias Cera, Irmã Dorcas e Nabal não estão em `npcs.json`, e nenhum NPC da Capela tem ponto em
  `game/data/mapas/area_inicial.json` (Missões e Level design). Zaqueu da Vela ainda se chama "Zaqueu" (renomear para
  Belmiro é da thread de Missões).
- `esfinge_amenti` não tem modelo (voz na pedra). Gustavo já tinha o dele (`classe_visual: gustavo_primarca`) e é o
  mesmo em todo lugar.

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
