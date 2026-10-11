# O Agrak, o Grande Coliseu (evento PvP)

Pedido do Jefin (11/10/2026): evento de arena estilo coliseu, com plateia. Os jogadores se inscrevem, o
apresentador reúne os gladiadores no centro, soltam 3 leões nível 30 (chefes de verdade), os sobreviventes
enfrentam um mutante gigante com roupa de gladiador e bola de ferro na corrente (o especial é o Pião, um
twisted slash de 10 s que tira 20% do HP por segundo de quem estiver no meio), e a última luta é entre os
sobreviventes: só um sai vivo e ganha uma **Ficha de Sangue**. A ficha compra armadura PvP (4 por peça) e
arma PvP (10).

Números e dados prontos para o jogo: `dados.json` (o JSON vale mais que este texto).
Coliseu, plateia e narrador (Cenário e Level design): `coliseu_e_narrador.md`.
Código (Prévia): `plano_codigo.md`. Sprite do gigante: `tools/sprite-pipeline/monstros/golias.py`.

## Lore em uma linha

O Agrak é o antigo **Estádio Municipal de São Lázaro**, enterrado na areia até a marquise. Cavaram o gramado
de volta e as arquibancadas de cima viraram plateia. Quem apresenta as lutas é **Caim e Abel, o Ogro de Duas
Cabeças** (definido pelo Jefin), dono do Agrak, que vende ingresso para os dois lados. Quem vende o equipamento de PvP é **Pedro, o Penitente**
(definido pelo Jefin): um demônio da Legião Blasfema convertido à luz, de pele branca e aura divina, sereno como um
Buda (pense no Netero), mas ainda com o corpo de demônio. Foi o carrasco da Legião; hoje vive numa ermida debaixo
da arquibancada, troca Fichas de Sangue por armadura e arma, e a luz dele levanta os derrotados (por isso morrer
no evento não tem penalidade). No Agrak vale a **Trégua da Areia**: ninguém é Vigília nem Arauto, todo mundo é
carne. O nome veio do grito da plateia quando a primeira cabeça rolou ("A-GRAAAK!").

## Fluxo do evento

| Etapa | Duração | PvP | O que acontece |
|---|---|---|---|
| Inscrição | 10 min antes | | Cartaz do Agrak nas bases (Acampamento da Vela, Capela de São Lázaro) ou com o ogro Caim e Abel. Nível 25+, 100 de ouro. Aviso no chat do sistema aos 10, 5 e 1 min. |
| Chamada | 45 s | não | Inscritos são levados ao Agrak, no Círculo de Ferro do centro. O ogro apresenta cada gladiador (Caim berra, Abel debocha) pelo nome e classe (fala em balão + texto na tela). Ninguém se mexe para fora do círculo (grade invisível). |
| Luta 1: Os Leões | até 4 min | não | Abre o Portão dos Leões: 3 **Leões do Amargo** nível 30. Os jogadores lutam juntos. Quem morre é eliminado. |
| Respiro | 20 s | não | Sobreviventes recuperam 50% do HP e do recurso. Plateia joga coisas na areia (só efeito). |
| Luta 2: O Gigante | até 5 min | não | Abre o Portão do Gigante: **Golias, o Pião do Agrak** (nível 35). Quem morre é eliminado. |
| Respiro | 15 s | não | Igual ao anterior, mais a fala "Agora, um contra o outro." |
| Luta 3: Último de Pé | até 3 min | **sim** | Todos contra todos. Depois de 60 s o **Anel do Amargo** (névoa verde) fecha do muro até o centro. O último vivo vence. |
| Coroação | 15 s | | Vencedor no camarote, chuva de pétalas secas, **1 Ficha de Sangue**. Todos voltam para onde estavam. |

Casos de borda:
- Se ninguém sobreviver à luta 1 ou 2, não há vencedor ("O Agrak comeu todo mundo hoje").
- Se só um sobreviver à luta 1 ou 2, ele enfrenta a próxima luta sozinho; se vencer o Golias sozinho, ganha a ficha sem a luta 3.
- Se o tempo da luta 1 ou 2 acabar com o monstro vivo, os monstros recuam e **todos os vivos** passam (a plateia vaia; sem bônus).
- Se a luta 3 estourar o tempo, vence quem tiver mais % de HP.
- Desconectar = eliminado. Morrer no Agrak **não** tem penalidade (sem perda de XP, sem desgaste); o eliminado vira **espectador** no camarote dos derrotados até o fim.
- Mínimo 4 inscritos (senão o evento é cancelado e o ouro devolvido). Máximo 20 por Agrak; acima disso abre um segundo Agrak (outra instância do mesmo mapa).

Agenda padrão: às **20h e 22h** (horário de Brasília) todo dia, e também às **15h** no sábado e domingo. Fica no
`dados.json` (`agenda`) para o Jefin trocar.

## Regras de PvP do Agrak

- Dano entre jogadores x0,6 (dano de jogador em monstro não muda). Cura em jogadores x0,7 na luta 3.
- Controles (atordoar, derrubar, puxar) duram metade em jogadores, e cada um dá 4 s de imunidade ao mesmo efeito.
- Poções: liberadas nas lutas 1 e 2 (recarga de 8 s, como fora). **Proibidas na luta 3.**
- Invocações (torretas do Tecnomancer) contam como do dono e somem quando ele é eliminado.
- Sem normalização de nível nesta primeira versão: faixa única 25+. Se a diferença ficar injusta, a próxima
  versão abre faixas (25-49, 50+), já previstas em `dados.json` (`faixas`, desligado).

## Os Leões do Amargo (luta 1)

Leões do velho zoológico da cidade, que o Amargo deixou maiores, carecas em placas e com a juba endurecida em
cerdas de crosta. O ogro os cria a carne de Não-Julgado. Os três têm nome na barra: **Sansão** (o maior, tanque),
**Dalila** (a mais rápida) e **Nabucodonosor** (o velho, que ruge).

- Nível 30, chefes (imunes a atordoar/derrubar, barra de postura). HP cresce com o número de gladiadores.
- **Mordida** (básico), **Bote** (salta numa linha de 6 tiles em quem estiver mais longe, derruba), **Dilacerar**
  (sangramento 6 s), **Rugido** (só Nabucodonosor: medo 1,5 s em raio 4).
- **O bando se vinga:** quando um leão morre, os outros ganham +15% de dano e +10% de velocidade (acumula).
- Cada leão persegue um alvo diferente quando possível (a ameaça de um alvo já caçado conta menos), para a luta
  espalhar pela arena.

## Golias, o Pião do Agrak (luta 2)

Mutante de 3,2 m, ex-escravo de arena: elmo de murmilão de sucata com grade, crista de arame, colar de escravo,
manica de placas no braço esquerdo, ombreira alta no direito, saiote de tiras de couro, tumor no ombro com
pústulas do Amargo (a única cor que brilha). Luta com uma bola de ferro cravejada numa corrente de 2,5 m.
Nível 35, chefe, HP cresce com os sobreviventes.

- **Bolada** (básico): arco curto à frente.
- **Esmagar**: ergue a bola por cima da cabeça e crava no chão à frente (círculo de 2 tiles a 3 tiles dele,
  preparo 1 s, atordoa 1 s).
- **O Pião (twisted slash)**: o telegrafo é um anel vermelho de 3,5 tiles em volta dele por 0,7 s (animação
  `spin_start`); depois gira por **10 s** (`spin`, em loop), andando devagar (1,2 tile/s) atrás de quem tem mais
  ameaça. Quem estiver dentro do anel perde **20% do HP máximo por segundo** (5% a cada 0,25 s), ignorando
  defesa. Escudos absorvem normalmente. Não dá para interromper. Ao fim, fica **Tonto 4 s** (`spin_end`): recebe
  +50% de dano. Primeiro Pião aos 15 s de luta, depois a cada 30 s.
- **Fase 2 (40% do HP)**: ruge (`roar`), o Pião passa a cada 20 s, raio 4 tiles e anda a 1,6 tile/s.
- Fúria aos 5 min (a luta acaba antes por tempo, então na prática não aparece).

## Ficha de Sangue e a loja do Agrak

- **Ficha de Sangue**: moeda do evento, pilha 99, vinculada à conta (não troca, não vende, não cai no chão).
- Loja: **Pedro, o Penitente**, na Ermida do Pedro, no corredor do Portão dos Gladiadores (zona segura do Agrak, aberta o tempo todo; o Cartaz do Agrak nas bases tem a opção "Ir ao Agrak"). Conjunto **Couraça do Agrak**, nível 25, 5 peças a **4 fichas**
  cada (cabeça, peito, luvas, calças, botas) e uma **arma do Agrak por classe a 10 fichas**. Conjunto completo +
  arma = 30 fichas.
- Atributo próprio de PvP: **Couro Curtido** (cada peça: dano recebido de jogadores -4%) e **Sede da Arena** (a
  arma: dano em jogadores +8%). Bônus de conjunto: 3 peças = +150 HP; 5 peças = mais -5% de dano de jogadores e o
  título "Gladiador do Agrak". Fora do PvP as peças valem como um raro do nível 25.
- Nomes, textos e atributos de cada peça em `dados.json` (`itens`), no mesmo formato de
  `design/missoes/dados/itens.json` para a thread de Missões copiar.

## Pontos em aberto para o Jefin

1. Pedro, o Penitente, é o NPC da loja de PvP (definido pelo Jefin); o narrador é o ogro de duas cabeças (também do Jefin); os nomes Caim e Abel são escolha minha. Nome do gigante: escolhi **Golias, o Pião do Agrak**. Trocar é só mudar `nome` no JSON.
2. Agenda (20h e 22h, mais 15h no fim de semana) e nível mínimo 25.
3. Só o vencedor ganha ficha, como pedido. Se quiser um prêmio de consolação (por exemplo ouro para quem
   passar da luta 1), está pronto para ligar em `dados.json` (`consolacao`, desligado).
