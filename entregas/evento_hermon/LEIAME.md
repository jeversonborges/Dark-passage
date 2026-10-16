# O Cume dos Vigilantes · evento diário do Monte Hermon

Pedido do Jefin (16/10/2026): o Chaos Castle do MU, feito com o Monte Hermon e os Vigilantes. O `dados.json` desta
pasta vale mais que este texto.

## A lore em uma linha

No topo do Hermon os duzentos Vigilantes juraram descer juntos (Livro de Enoque). Eles continuam lá, ajoelhados
como estátuas de cinza. Toda noite às 19h o lacre do juramento estala, eles se levantam e o cume desmorona, anel por anel.

## Regras (como o Jefin pediu)

- **Convite dos Vigilantes**: compra-se por 300 de ouro com o Zaqueu (Vigília) ou a Corvina (Arautos). Clique nele
  na mochila **depois que o evento começou**. A entrada fica aberta por **5 minutos** (19:00 a 19:05, horário de
  Brasília). Antes ou depois disso o convite não é gasto e diz quando o Hermon chama de novo.
- **1 vez por dia, às 19:00.** Avisos para todo o servidor 10, 5 e 1 minuto antes.
- **15 minutos de sobrevivência** depois que a entrada fecha. A partir do nível 15, cume separado por faixa de nível
  (15-49, 50-99, 100-149, 150-249, 250-400), até 20 jogadores por cume. Com menos de 2 o cume é cancelado e o convite volta.
- **PvP ligado** (mesmos multiplicadores do Agrak), poções liberadas, voar não salva.
- **O chão cai**: 5 anéis desabam aos 3, 6, 9, 12 e 14 min (as fendas acendem 20 s antes). Quem estiver no anel cai
  no abismo e está fora. A Laje do Juramento, no centro, nunca cai. Empurrões perto da beira derrubam (MU puro).
- **Vigilantes**: 20 + 2 por jogador (máx. 50) e reforços do céu a cada queda. Três tipos: Jurado (comum),
  Ferreiro (bruto, o malho empurra) e Estrelado (elite, chama uma estrela no seu pé).
- **Pontos**: Vigilante 1, Estrelado 3, jogador 3. Morrer não tira nada: volta para casa sem perda.
- **Fim**: o último vivo sem Vigilantes no cume, ou os 15 min. Vence quem tem mais pontos entre os vivos.

## Prêmios

- **Vencedor (Testemunha do Juramento)**: **30% de chance de uma arma lendária** da própria classe, o título
  "Testemunha do Juramento" e **+2 Fichas de Sangue**.
- **Todo sobrevivente** (vencedor incluso): 1 Lágrima Angélica, 15 de ouro × nível dos mobs e **1 Ficha de Sangue**.
- **Abate PvP**: **+1 Ficha de Sangue** na hora, no máximo 3 por evento.
- As fichas são a mesma moeda PvP do Agrak (compram a Couraça do Agrak na banca do Saulo). Pedido do Jefin: "Coloca
  algumas fichas de pvp".

As Armas de Azazel (nível 25, brilho dourado `#ffd890`): Espada do Primeiro Juramento (Anjo), Cajado das Estrelas
Contadas (Cultista), Falx de Azazel (Demônio), Escopeta do Juramento Quebrado (Humano), Malho de Tubal (Mutante) e
Bobina de Baraquiel (Tecnomancer). Os efeitos especiais estão descritos no `dados.json`; ainda falta programá-los.

## Arquivos

| Arquivo | O quê |
|---|---|
| `dados.json` | evento, faixas, anéis, Vigilantes, pontos, prêmios, falas, mobs e itens (convite, 6 armas, ficha) |
| `mapa/gerar_mapa.py` | gera `cume_dos_vigilantes.json` (60x60) e a planta. Nunca edite o JSON à mão |
| `codigo/hermon_ctl.gd` | controle do evento no sim (anéis, quedas, pontos, fim, prêmios) |
| `codigo/evento_hermon.gd` | servidor: agenda das 19h, janela de 5 min, uso do convite, instâncias |
| `codigo/teste_hermon.gd` | 50 testes, todos passando (`saida_do_teste.txt`) |
| `codigo/jogo.patch` | tudo que muda em `game/` (sim, servidor e cliente), já testado contra o `game/` atual |
| `previa/jogo/` | fotos dentro do jogo: espera, juramento, luta, aviso, queda e o abismo |
| `assets/monstros/vigilante_*` | os 3 Vigilantes (8 direções; idle, walk, attack, hit, death, kneel, rise, land) |
| `tools/sprite-pipeline/monstros/vigilante.py` | o modelo no Blender, com as 3 variantes |

## Integração (thread "Prévia jogável e área inicial", depois da 0.9.2)

1. `cd /mnt/project-files && patch -p1 < entregas/evento_hermon/codigo/jogo.patch`.
2. Copie `dados.json` para `design/pvp/hermon/dados.json` (o `sync.sh` precisa copiar `design/pvp/`) e o mapa
   `mapa/cume_dos_vigilantes.json` para `game/data/mapas/`.
3. Junte os itens do `dados.json` ao `design/missoes/dados/itens.json` (convite, 6 armas; a Ficha de Sangue já vem
   do Agrak) e rode `design/skills-itens/fontes/gerar_json.py`. Ponha o convite à venda em `loja_zaqueu` e `loja_corvina`.
4. Ponha "O Cume dos Vigilantes" em `locais.json` (sem isso o minimapa mostra o id).
5. Rode `tools/sync.sh` (copia os Vigilantes) e `godot --headless --path . --script res://tools/teste_hermon.gd`.
6. A base de PvP (multiplicadores de `regras_pvp`) é a mesma do plano do Agrak (`design/pvp/agrak/plano_codigo.md`).

O que muda no cliente: o vazio do cume vira abismo com nevasca, as fendas acendem e tremem no aviso, as células do
anel viram abismo e os props caem com ele, e os Vigilantes ajoelhados aparecem como estátuas de cinza até levantarem
(`rise`) ou descerem do céu (`land`).

## Pendências para outras threads

- Ícones do convite, das 6 armas: entram no plano de arte de itens do próprio Jefin.
- Efeitos especiais das Armas de Azazel (Combate / Skills).
- Música própria do evento (hoje usa `musica/cripta`) e o som do desmoronamento (Som).
