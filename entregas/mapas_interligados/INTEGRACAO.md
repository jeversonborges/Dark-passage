# Mapas interligados · integração (para a Prévia, 0.9.4)

Pedido do Jefin (17/10/2026): "os mapas precisa se interligar" e "tô em Jerusalém e não tem como ir para outro mapa".
Grafo do mundo: `grafo_mundo.png` (fonte `design/mapas/mundo/fontes/grafo_mundo.py`).

## O que muda

| Estrada | Ponta A | Ponta B | Mudança |
|---|---|---|---|
| Estrada dos Peregrinos | Jerusalém, saída norte da cidade (~101.5, 32.5), visual `torre_portao` | São Lázaro (~56.5, 126.5), visual `placa_rua_enterrada` | **sem a trava do nível 12** (era o que prendia o Jefin) |
| Linha de Cinza | São Lázaro (~87.5, 25.5), `placa_aviso` | Novo Éden (~74.5, 87.5), `pilar_portao` | só o visual |
| Estrada do Êxodo (nova) | Jerusalém, borda da Cidade de Davi (~131.5, 17.5), `placa_versiculo`, **nível 45** | Egito, borda leste de Mênfis (~153.5, 106.5), `obelisco` | o Egito não tinha nenhum acesso a pé |

Os portais de estrada levam `"estrada": true` e `"estrada_id"`. Masmorras, eventos e portas trancadas por missão ou mistério
não foram tocados. Atlântida continua entrando pela Fenda do Novo Éden. O `ligacoes.py` troca o `requer_nivel` da
Fenda por `nivel_minimo`, porque o servidor só lê `nivel_minimo`: sem isso, a Fenda abriria em qualquer nível quando a
Atlântida entrar.

**A grade não muda**: só `objetos`. Não é preciso subir `rede.VERSAO` por causa disto. O cliente precisa do patch abaixo
para desenhar o marco da estrada. Sem ele, a estrada continua funcionando, só que aparece como escada.

## Passos

1. Rodar o passo final nos mapas do jogo (é idempotente e pode rodar de novo depois de qualquer gerador, inclusive o
   do Novo Éden e o do layout novo de Jerusalém, que estão mudando agora):

       python3 design/mapas/mundo/fontes/ligacoes.py game/data/mapas
       python3 design/mapas/mundo/fontes/ligacoes.py --checar game/data/mapas   # só confere

   Ele procura a célula livre mais próxima do alvo e ligada ao spawn, e falha se não achar. `mapas/` tem os 4 mapas já
   processados a partir da cópia de 17/10 15:40, só para conferência. Prefira rodar o script nos mapas atuais.
2. Aplicar o patch do cliente: `git apply entregas/mapas_interligados/jogo.patch`. Ele muda `game/scripts/client/game.gd`
   (portal com visual de estrada usa o prop do kit; todos os 6 props já estão em `data/ext/ambiente.json`).
3. Menu de teleporte: o Egito e Mênfis ficam com a thread "Menu de teleporte", que já está mudando o gerador.
4. Teste rápido: nascer em Jerusalém com nível 1, andar até o portão ao norte do spawn e passar para São Lázaro. Com
   nível abaixo de 45, a Estrada do Êxodo deve responder "O deserto de Shur come quem atravessa fraco. Volte no nível 45."

## Não testado

Não rodei no Godot: o patch e os mapas foram conferidos só por script (grade igual, pontas ligadas ao spawn, patch aplica
no main).

## Gruta de Pã (Jerusalém)

A "pedra" que o Jefin viu é a fechadura da missão jc02, e não um bug. O texto de trancado agora diz onde está a chave
(`design/missoes/dados/objetos.json`, `porta_de_pa`). Ele entra pelo `sync.sh`, como os outros dados de missão.
