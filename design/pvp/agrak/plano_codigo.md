# O Agrak: plano de código (thread Prévia)

O jogo ainda não tem PvP; o Agrak é o primeiro. Tudo roda no servidor (simulação autoritativa) e o cliente só
mostra. Números em `dados.json`; o `tools/sync.sh` precisa copiar `design/pvp/` para `data/design/pvp/`.

## 1. Base de PvP (serve para o Agrak e para o PvP de mundo depois)

- `sim/ent.gd`: `lado()` hoje separa jogadores de monstros. Adicionar `lado_forcado: String` (vazio = normal).
  O Agrak define `"agrak"` para todos nas lutas 1 e 2 e `"g_<id>"` (um lado por jogador) na luta 3, então
  `eh_inimigo_de` e `inimigos_de` passam a valer entre jogadores sem mexer em cada habilidade.
- `sim/regras.gd`: multiplicadores quando atacante e alvo são jogadores: `regras_pvp.dano_jogador_em_jogador`,
  `cura_em_jogador_luta_final`, novos atributos de item `dano_em_jogadores` e `dano_recebido_jogadores` (o
  Elmo de Rafael já tem esse efeito em texto; ligar os dois pelo mesmo atributo).
- `sim/world_sim.gd` (`aplicar_status`): em alvo jogador, duração de controle x0,5 e imunidade de 4 s ao mesmo
  efeito.
- Morte de jogador por jogador: evento `morte_pvp` (killer, vítima) para o narrador e o placar. Sem perda de
  XP nem drop quando o mapa tem `sem_penalidade`.
- Cliente: nome de outro jogador em vermelho quando ele é inimigo (mesmo esquema de nome amarelo/vermelho dos
  mobs), clique em jogador inimigo = ataque básico.

## 2. Agendador e inscrição (servidor)

- `net/servidor.gd`: novo `agrak.gd` (nó do servidor, não do sim) com a agenda de `dados.json`, a lista de
  inscritos por conta/personagem e os avisos no chat do sistema (10, 5, 1 min). Sem chat ainda: usar o mesmo
  canal das mensagens do sistema (`emitir_a(e, "aviso", ...)`) para todos os jogadores online.
- Inscrição: comando novo em `sim/comandos.gd` (`agrak_inscrever`), disparado pelo diálogo do ogro ou pelo
  objeto `cartaz_agrak`. Confere nível 25+, cobra 100 de ouro, guarda o mapa e a posição de volta.
- Na hora: se houver menos de 4, devolve o ouro. Senão divide em grupos de até 20 e cria uma instância do
  mapa `agrak` para cada (`_mundo("agrak#1")`, mesmo caminho dos mapas por instância) e move os inscritos online.
- Fim: devolve cada um ao mapa e à posição de antes (HP cheio), entrega a ficha ao vencedor, libera a instância.
- Modo LAN/offline: o anfitrião pode iniciar o Agrak pelo menu de depuração (`agrak=agora` na linha de comando),
  para teste.

## 3. Controlador da arena (sim)

`sim/agrak_ctl.gd`, irmão do `chefe_ctl.gd`, criado pelo `world_sim` quando o mapa é `agrak`:

- Máquina de etapas de `dados.json` (`chamada`, `luta_leoes`, `respiro`, `luta_gigante`, `respiro`,
  `ultimo_de_pe`, `coroacao`), com tempo restante enviado ao HUD.
- Chamada: prende os jogadores no Círculo de Ferro (área `prender`), dispara as falas do ogro (Caim e Abel, uma linha de cada cabeça) com nome e
  classe de cada um (evento `fala` com `quem: "caim"` ou `"abel"`).
- Lutas 1 e 2: abre a porta do portão (`definir_bloqueio`), cria os chefes com `ChefeCtl` (vários ao mesmo tempo:
  hoje o `world_sim` tem um `chefe` só; trocar por uma lista `chefes`). HP = `hp + hp_por_jogador * vivos`.
- Morte de jogador: vira espectador (teleporte para o Camarote dos Derrotados, sem ação de combate, câmera
  livre na arena). Desconectar = eliminado.
- Luta 3: troca `lado_forcado`, bloqueia poções (`pocoes: false`), liga o Anel do Amargo: área circular que
  encolhe e dá 8% do HP máximo por segundo fora dela.
- Tempo esgotado e casos de borda conforme `tempo_esgotado` e `README.md`.

## 4. Chefes novos no `chefe_ctl.gd`

- Os leões: alvo `mais_longe` no Bote, alvos espalhados (ameaça x0,5 para quem já é perseguido por outro leão),
  buff do `_bando` quando um morre. O resto (mordida, sangramento, medo) já existe nos mobs.
- Golias, ataque `piao`: telegrafo `anel_que_segue` (preso ao chefe), estado `girando` por 10 s com
  `velocidade_mov_girando`, a cada 0,25 s tira 5% do HP máximo de quem estiver no raio, ignorando defesa
  (escudo absorve). Anim `spin_start` no preparo, `spin` em loop, `spin_end` + status `tonto` (+50% de dano
  recebido) por 4 s. Fase 2 aos 40%: anim `roar` e as `mudancas`.
- `_jog()` hoje escolhe o jogador de maior ameaça dentro da arena; já serve para vários jogadores.

## 5. Itens, loja e moeda

- `ficha_sangue`: tipo `moeda`, vinculada (não pode largar, trocar nem vender).
- Loja do Pedro (NPC `pedro`, na ermida do Agrak, zona segura aberta o tempo todo; o Cartaz do Agrak ganha a opção "Ir ao Agrak"). Loja com moeda que não é ouro: `lojas.json` ganha `moeda` por loja; a janela de loja mostra o ícone da ficha.
- Conjunto `couraca_do_agrak` com bônus por número de peças (primeiro conjunto do jogo; conferir em `itens.gd`
  ao recalcular atributos).
- Os itens entram por `design/missoes/dados/itens.json` (thread Missões copia de `dados.json`) e depois
  `python3 design/skills-itens/fontes/gerar_json.py`.

## 6. Cliente

- HUD do evento: faixa no topo com a etapa e o tempo, e quantos gladiadores restam.
- Barras de chefe para até 3 chefes ao mesmo tempo (leões).
- Plateia: props animados `plateia_*` com reação ao evento `morte_pvp`/morte de chefe (troca para o quadro de
  braços erguidos por 1 s) e o som de urro.
- Falas do ogro em texto grande no centro da tela por 3 s (ele está longe no camarote).
- Espectador: câmera presa no centro da arena, sem HUD de habilidades.

## 7. Rede e versão

- Mapa novo e mensagens novas: subir `rede.VERSAO` e publicar servidor e cliente juntos (regra da 0.8.0).
- Teste: `xvfb-run godot ... -- roteiro=agrak` com 4 jogadores simulados (bots que andam e atacam) para conferir
  as etapas, o Pião e a luta final.
