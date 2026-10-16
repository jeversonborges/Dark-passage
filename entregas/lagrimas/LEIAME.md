# Lágrimas de refino (Bless e Soul do DARK PASSAGE)

## v2 (16/10/2026): arte nova, e por que não apareceu na 0.9.1

**Por que não apareceu:** o jogo pega os ícones do atlas (`atlas_itens_40/64`) e da lista da mochila em `data/ext/icones.json`.
O atlas não foi refeito porque o `folha.py itens` quebrava em 3 itens de missão sem ícone (`livro_dos_vencidos`,
`faixa_de_linho_rafael` e `pena_que_ficou`). Além disso, o `sync.sh` não rodou depois da entrega, então a
`game/assets/ext` ficou sem os ícones e sem os efeitos das lágrimas. O código do patch entrou, mas os arquivos não.

**O que mudou:** agora a pedra tem lapidação de gota de verdade, com casca de vidro refratando um núcleo que brilha.
A Angélica tem engaste de prata velha com filete de ouro, seis garras com contas, um par de asas de penas e auréola.
A Sanguínea tem ferro enegrecido, coroa de espinhos, um ramo de espinhos enrolado na pedra e uma gota de sangue pingando.
O `folha.py` agora pula os itens sem ícone, com aviso, e o atlas foi refeito com as duas lágrimas. Os efeitos e o código não mudaram.

**Para a Prévia, na 0.9.2:** rode `bash tools/sync.sh` (ele já roda o `manifest.py`) e confira se existem
`game/assets/ext/icones/mochila/lagrima_angelica.png` e `game/assets/ext/efeitos/itens/lagrima_angelica_brilho.png`.
O patch de código já está no jogo, não aplique de novo.

Pedido do Jefin em 15/10/2026. A **Lágrima Angélica** (azul-claro) leva o item do +0 ao +6 e a **Lágrima Sanguínea** (vermelho-sangue)
leva do +6 ao +15. Qualquer mob pode soltar as duas. No chão elas brilham como joia. Elas substituem a Lágrima de Anjo e o
Fragmento de Alma.

Prévia: `previa.png` (render, ícones 64/40/32 e o efeito no chão: queda + loop).

## O que já está nas pastas de origem

| Onde | O quê |
|---|---|
| `design/skills-itens/fontes/itens_data.py`, `itens.json` | `lagrima_angelica` e `lagrima_sanguinea` (categoria joia, tag `joia:refino`, pilha 20), com `brilho_chao` (cor, efeitos e som) e `substitui` |
| `design/combate/drops.json` | `lagrimas`: curva de drop e multiplicadores. `refino_com_lagrimas`: máximo +15, chances e regra de falha. Baús: `joia_sanguinea_fracao`. `cripta_monge` e `cripta_celestial` não soltam mais joia pela tabela (o peso foi para equipamento), porque agora quem cuida disso é a curva |
| `assets/icones/fontes/lagrimas.png` | folha 4x2 (índices 0 e 1), renderizada no Blender |
| `assets/icones/itens/{64,40,32,mochila,mochila_2x}/lagrima_*.png` | ícones finais |
| `assets/efeitos/itens/lagrima_{angelica,sanguinea}_{queda,brilho}` | queda (one-shot, 14 quadros) e brilho no chão (loop, 16 quadros) |

## Números

- **Chance por abate:** Angélica = curva(nível do mob), Sanguínea = metade da curva. A curva vale 0,08% no nível 1 e sobe em
  linha reta até 0,8% no nível 50. Depois ganha +0,004% por nível, até o teto de 1,6%.
  Exemplos para a Angélica: nível 10 dá 0,21%, nível 25 dá 0,43%, nível 50 dá 0,80% e nível 100 dá 1,0%.
- **Multiplicadores:** spot de farm ×1,25, elite/raro ×3, chefe ×5. Na `cripta_celestial`, a Angélica sai ×2. O loot é pessoal e a
  rolagem fica fora da tabela do mob. Chefes e baús continuam com a tag `joia:refino` e somam essa chance à da curva.
- **Refino:** a Angélica leva do +0 ao +6 e sempre dá certo. Com a Sanguínea, a chance de chegar a cada nível é:

  | +7 | +8 | +9 | +10 | +11 | +12 | +13 | +14 | +15 |
  |---|---|---|---|---|---|---|---|---|
  | 75% | 70% | 65% | 55% | 50% | 45% | 40% | 35% | 30% |

  Se falhar ao tentar do +7 ao +10, o item perde 1 nível. Do +11 ao +15, perde 2. Nunca fica abaixo de +6 e nunca quebra.
  O ouro do ferreiro continua sendo 50 × nível alvo. Cada + ainda soma 8% no dano e na defesa base, então um +15 fica com 2,2×.
  Esse valor fica com a thread Revisão de balanceamento.

## Para a Prévia jogável (dona do código)

1. Rode `bash tools/sync.sh`, que copia o `itens.json`, o `drops.json`, os ícones e os efeitos.
2. Aplique o patch: `cd /mnt/project-files && patch -p1 < entregas/lagrimas/jogo.patch`. Ele mexe em 4 arquivos:
   - `loot.gd`: `chance_lagrima()` e `_rolar_lagrimas()`, chamada em todo `dropar_mob`. O baú sorteia Angélica ou Sanguínea.
   - `jogador.gd`: `refinar()` lê `refino_com_lagrimas` (até +15) e ganhou `chance_refino()`. O `carregar()` converte saves
     antigos (`lagrima_anjo` vira `lagrima_angelica` e `fragmento_alma` vira `lagrima_sanguinea`).
   - `janelas.gd`: o texto do ferreiro mostra a chance de cada nível e o máximo passa a ser +15.
   - `game.gd`: quando o item tem `brilho_chao`, o chão usa a cor da joia e toca a queda, o brilho em loop e o som
     `itens/joia_aplicar`, no lugar do feixe de raridade.
3. Testado no Godot 4.4.1 headless: o `tools/parse_test.gd` passa, `game.gd` e `janelas.gd` compilam, e a curva e as chances
   batem com a tabela acima. Não abri o jogo com tela.
4. Não publiquei cliente.

Se o `jogador.gd` tiver mudado e o patch não entrar, o bloco que importa é a função `refinar` inteira e a linha de migração
dentro de `carregar`.

## Regerar

    blender -b -P tools/icones/lagrimas_blender.py -- /tmp/lag
    python3 tools/icones/lagrimas_folha.py /tmp/lag          # precisa de scipy
    cd tools/icones && python3 arte_pronta.py lagrima_angelica lagrima_sanguinea
    cd tools/vfx && python3 build.py lagrima_

O `arte_pronta.py` agora usa `cor_brilho` do item (se existir) e ganhou 1 px de margem antes do contorno. Antes, o `np.roll`
vazava pontinhos para a borda oposta do ícone. Os anéis e túnicas ficam sem esses pontinhos quando forem regerados.
