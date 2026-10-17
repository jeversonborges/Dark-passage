# O Agrak: evento completo com a apresentação ao vivo (para a Prévia, 0.9.3)

Feito em 17/10/2026 pela thread "Apresentação ao vivo do Agrak". O `game/` compartilhado **não** foi mexido:
tudo entra pelo `aplicar.py` desta pasta. Roteiro seguido: `design/pvp/agrak/apresentacao.md`; números:
`design/pvp/agrak/dados.json` (o `sync.sh` já copia para `data/design/pvp/agrak.json`).

O evento inteiro ainda não existia no jogo (só o `lado_forcado` no `ent.gd` e o cartaz pedindo inscrição), então
a entrega cobre o evento todo, não só a apresentação: agenda e inscrição no servidor, as 7 etapas, as feras, o
PvP da luta final, os espectadores, a volta para casa e o prêmio.

## O que tem aqui

| Arquivo | Vai para | O quê |
|---|---|---|
| `scripts/sim/agrak_ctl.gd` | `game/scripts/sim/` | `AgrakCtl` (filho do `ChefeCtl`): Chamada de 45 s com o roteiro inteiro, leões, respiros, Golias com o Pião, Último de Pé com o Anel do Amargo, Coroação, espectadores, sem penalidade, volta para casa |
| `scripts/net/agrak.gd` | `game/scripts/net/` | servidor: agenda em horário de Brasília (20h e 22h; 15h no sábado e domingo), avisos no chat do sistema (10, 5, 1 min), inscrição (nível 25, 100 de ouro), cancela com menos de 4 e devolve o ouro, leva até 20 para o mapa `agrak` |
| `scripts/client/agrak_cena.gd` | `game/scripts/client/` | tela: falas de Caim e Abel em letra grande, cartão de cada gladiador, faixa da etapa com o tempo, barras dos 3 leões, plateia animada (0-1 a 4 fps; 2-3-3-2 nas mortes), portões subindo, Anel do Amargo, poeira do Pião, coisas jogadas na areia, chuva de pétalas, música e sons |
| `tools/teste_agrak.gd` | `game/tools/` | teste headless do evento inteiro com 4 gladiadores |
| `aplicar.py` | (roda daqui) | copia os 4 scripts e liga os ganchos em 6 arquivos do `game/`; pode rodar de novo, não duplica |

Sons novos (já gerados e no `assets/audio/` compartilhado, fonte `assets/audio/fontes/sfx_agrak.py`, registrado
no `build.py`): `agrak/plateia_urro` (3), `agrak/plateia_agrak` ("A-GRAAAK!"), `agrak/plateia_golias`,
`agrak/plateia_vaia`, `agrak/grade_sobe`, `agrak/guincho_corrente`, `agrak/corrente_girando`,
`agrak/rugido_dalila`, `agrak/rugido_nabucodonosor`, `agrak/rugido_sansao`, `agrak/rugido_morte`,
`agrak/golias_urro`, `agrak/megafone` (3, Caim), `agrak/abel_resmungo` (3), `ambiente/agrak_multidao` (loop) e
`musica/agrak_arena` (loop). O Saulo usa o `combate/sino_curto` que já existia.

## Ganchos que o `aplicar.py` liga (uma ou duas linhas cada)

- `sim/world_sim.gd` (`carregar_mapa`): mapa com bloco `agrak` cria `AgrakCtl` no lugar do `ChefeCtl`. Todos os
  outros ganchos do world_sim (`passo`, `ao_morrer_ent`, `ao_quebrar`, `jogador_morreu`, `porta_fechada`) já
  chegam no `AgrakCtl` sem mudar nada.
- `net/sincro.gd`: `lado_forcado` no `PUB` (o cliente precisa saber quem é inimigo na luta final: nome vermelho
  e clique ataca).
- `client/game.gd`: `preload` do `agrak_cena.gd`, cria o nó quando o mapa tem bloco `agrak`, limpa ao trocar de
  mapa e repassa cada evento (`agrak_cena.ev`).
- `sim/missoes.gd`: ação de diálogo `{"agrak": "inscrever" | "sair"}` (o diálogo do Caim e Abel já usa).
- `net/servidor.gd`: nó `agrak` (filho do servidor), o evento `agrak_pedido` vai para ele, e `agrak.saiu(peer)`
  antes de salvar quem desconecta no meio do evento (salva no mapa de onde ele veio).
- `defs.gd` (`_extras_v06`): carrega `pvp/agrak_npcs.json` (nome e diálogo de Caim e Abel e do Saulo, a loja e o
  objeto `cartaz_agrak`). Sem isso os dois NPCs apareciam com o id no lugar do nome.

## Passos

1. Na raiz do repositório: `python3 entregas/agrak/aplicar.py` (ou `python3 entregas/agrak/aplicar.py <pasta do game>`).
   Esperado: 4 "copiado", 13 "ligado" e `OK`. Rodar de novo mostra "já tinha" e `OK`.
2. `cd game && bash tools/sync.sh` (traz os sons novos para `assets/ext/audio/` e o `audio.json`).
3. `godot --headless --path . --import`.
4. Testes:
   - `godot --headless --path . --script res://tools/teste_agrak.gd` → `RESULTADO: OK` (24 conferências: a grade
     do círculo segura, 4 apresentados, 3 leões correm até o círculo, derrotado levantado pelo Saulo no camarote,
     Golias entra, gira o Pião e cai, PvP só entre os vivos, Anel fecha, coroação, 1 Ficha de Sangue, todos voltam).
   - `godot --headless --path . -s tools/check.gd` → todos "ok" (compila o cliente com o `agrak_cena.gd`).
5. Ver no jogo, sozinho: `godot --path . -- classe=mutante mapa=agrak agrak=agora`. Com `agrak=agora` o
   controlador começa assim que o jogador entra e roda o evento inteiro com ele só.
6. Ver em rede (LAN): servidor com `servidor=1 agrak=agora agrak_min=1`, entrar com 1 ou 2 personagens de nível
   25+ e usar o Cartaz do Agrak (área inicial) ou falar com Caim e Abel: a inscrição abre na hora e a luta começa
   em 60 s. Sem os dois argumentos vale a agenda do `dados.json`.
7. Mapa e protocolo novos: subir `rede.VERSAO` e publicar servidor e cliente juntos (regra da 0.8.0).

## Como a apresentação funciona (para quem for mexer)

- Tudo roda no servidor e sai em eventos; ninguém perde o controle nem a câmera. Na Chamada a grade invisível
  só puxa de volta para a borda do Círculo de Ferro quem tentar sair (raio 3,5 do bloco `agrak` do mapa).
- Eventos novos: `agrak_etapa` (etapa, tempo, quantos de pé), `agrak_fala` (quem: `caim` ou `abel`),
  `agrak_gladiador` (cartões), `agrak_plateia` (`vibrar`, `urro`, `coro`, `golias`, `vaia`, `bracos`),
  `agrak_portao`, `agrak_som`, `agrak_musica`, `agrak_fera` (barras dos leões), `agrak_anel`, `agrak_fx`
  (`piao`, `coisas_na_areia`), `agrak_coroacao`, `agrak_espectador`, `agrak_fim`, `morte_pvp`. O balão e a
  animação do ogro usam os eventos que já existiam (`fala` e `anim` no NPC `caim_abel`: `anunciar`, `discutir`,
  `rir`); o Saulo faz `rezar` quando levanta alguém.
- As falas são as de `coliseu_e_narrador.md`; o Abel tem dois deboches por classe (`DEBOCHE` no topo do
  `agrak_ctl.gd`). Mais de 8 gladiadores: o Caim anuncia em grupos, como o roteiro pede.
- Leões: cada um é um `ChefeCtl` (classe interna `Fera`), com o Bote no mais longe, alvos espalhados e o bando se
  vingando (+15% de dano e +10% de velocidade por leão morto). Golias: Pião de 10 s que segue a maior ameaça,
  5% do HP máximo a cada 0,25 s no raio, ignora defesa (escudo absorve), e depois fica tonto 4 s com +50% de dano
  recebido. A fase 2 aos 40% usa as `mudancas` do `dados.json`.
- Luta final: cada vivo vira o próprio lado (`g_<id>`), dano entre jogadores x0,6 (buff `dano_recebido`), sem
  poções, torretas contam como do dono e somem com ele. Anel do Amargo aos 60 s, do raio 13 ao 4 em 90 s, 8% do
  HP por segundo fora dele.
- Morrer no Agrak não custa nada: a XP volta e, 3 s depois, o Saulo levanta o derrotado no Camarote dos
  Derrotados como espectador (lado `neutro`, não acerta nem é acertado). Desconectar = eliminado.
- No fim, cada um volta para o mapa e o lugar de antes (`aux.agrak_volta`, que o servidor grava ao levar), com
  HP cheio.

## O que fica de fora desta entrega

- A Banca de Sangue do Saulo (loja com Ficha de Sangue em vez de ouro) e as peças PvP do Agrak: os itens
  `agrak_*` de `design/pvp/agrak/itens_agrak.json` ainda não estão no `itens.json` gerado. A ficha já existe e é
  entregue ao vencedor.
- Uma arena por vez: acima de 20 inscritos o resto recebe o ouro de volta (o plano previa uma segunda instância).
- Os leões ainda não têm o efeito de VFX próprio do Pião nem da névoa: a poeira do Pião, o Anel, as pétalas e o
  lixo da plateia são desenhados pelo `agrak_cena.gd`.
