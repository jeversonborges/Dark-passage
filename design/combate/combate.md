# DARK PASSAGE: Design do Combate (v0.1)

> Especificação da primeira entrega: área inicial (níveis 1 a 7) e a Cripta da Trombeta Calada (níveis 7 a 13, 3 chefes).
> Os números ficam nos JSON desta pasta; este texto explica o porquê e a ordem das coisas. Em caso de conflito, **o JSON vale**.

| Arquivo | O que tem |
|---|---|
| `formulas.json` | dano, defesa, acerto, crítico, golpe excelente, nível, velocidade, aggro, morte |
| `classes_base.json` | atributos iniciais, HP, recurso e números das 5 primeiras habilidades de cada classe |
| `sensacao.json` | hit-stop, flash, empurrão, tremor, números de dano, telegrafos, controles, ligação com os efeitos visuais prontos |
| `efeitos.json` | postura (quebra), efeitos de status, retornos decrescentes de controle |
| `mobs.json` | curva dos monstros, arquétipos, IA, os 15 monstros + elite + raro |
| `chefes.json` | os 3 chefes com fases, ataques e telegrafos |
| `progressao.json` | XP por nível (1 a 400), ritmo esperado, XP de monstro e de missão |
| `drops.json` | raridades, opções de item, tabelas de drop, baús, proteção contra azar |
| `simular.py` / `balanceamento.txt` | simulação que confere os números (rodar `python3 simular.py`) |

---

## 1. Os pilares

1. **Cada golpe tem peso.** O dano sai no frame de impacto, o alvo pisca, os dois congelam por uma fração de segundo, o número salta. Errar ou acertar tem que ser sentido sem olhar para a barra de HP.
2. **Clique e mata, como no MU, mas com leitura.** Andar e atacar com o mouse, habilidades no 1, 2, 3... (definido pelo Jefin). A profundidade vem de *quando* usar a habilidade e de *sair do chão vermelho*, não de combos de teclado.
3. **Todo golpe forte é avisado.** Ataque de monstro que tira muito HP sempre tem telegrafo no chão de pelo menos 0,6 s. Morrer tem que parecer culpa do jogador.
4. **Postura dá um segundo objetivo.** Além do HP, elites e chefes têm uma barra de postura. Quebrar abre uma janela de dano extra e é a forma de interromper os ataques mais perigosos dos chefes.
5. **O servidor manda.** Todo cálculo roda no servidor (hoje, a camada de "servidor" dentro do próprio jogo). O cliente só toca animação e sensação quando o evento chega. Isso deixa o multiplayer futuro sem retrabalho.

## 2. Sensação dos golpes (`sensacao.json`)

**Anatomia de um ataque.** Preparo (3 frames) → ativo (1 frame, o dano sai aqui) → recuperação (3 frames), a 15 fps escalando com a velocidade de ataque. A recuperação pode ser cancelada em habilidade, poção ou movimento, então o personagem nunca parece "preso". Comandos dados até 150 ms antes do fim entram no buffer.

**No frame de impacto, nesta ordem:**
1. O atacante avança 4 px na direção do golpe.
2. **Hit-stop local:** atacante e alvo congelam (45 ms golpe leve, 85 ms pesado, +40 ms crítico, 130 ms abate). O resto do mundo segue rodando.
3. **Flash:** o alvo fica branco osso por 60 a 90 ms (no jogador, vermelho sangue).
4. **Empurrão:** 0 a 24 px conforme o golpe, reduzido pela resistência do arquétipo (chefe só recua quando a postura quebra).
5. **Tremor de câmera** só em golpe pesado, crítico, abate e golpes de chefe (com opção no menu para desligar).
6. **Número de dano** com pop de escala 1,6 → 1,0 em 80 ms, sobe 26 px e some em 750 ms. Cores: branco osso normal, **laranja brasa com "!" no crítico**, **verde ácido no golpe excelente** (o verde do MU), vermelho no dano recebido, cinza para "ERROU".
7. Efeito visual e som do evento (já ligados aos efeitos prontos da thread Efeitos visuais, ver `vfx_ja_prontos`).

**Abate:** o corpo voa 18 px, pisca 3 vezes e cai, com o efeito `morte_monstro`. **Chefe morto:** câmera lenta a 15% por 0,6 s, flash da tela e tremor forte.

**Controles (Jefin):** clique no chão anda (segurar segue o mouse), clique no inimigo anda até o alcance e ataca em loop, Shift ataca parado, **teclas 1 a 9 soltam a habilidade na hora** no inimigo sob o mouse (ou no alvo atual; área e mobilidade vão no ponto do mouse). Fora do alcance, o personagem anda até o alcance e solta. Q, W, E são poções. Clique a até 18 px de um inimigo conta como clique nele (alvo magnético, essencial em isométrico).

## 3. Atributos e fórmulas (`formulas.json`)

5 pontos por nível (6 depois da evolução no 150, 7 depois do 400).

| | O que faz |
|---|---|
| **FOR** | dano corpo a corpo (FOR/6 a FOR/4, como o Cavaleiro do MU) |
| **AGI** | dano à distância, velocidade de ataque (+0,4% por ponto), esquiva, crítico (+0,08% por ponto) |
| **VIT** | HP (3 a 4 por ponto, conforme a classe) e defesa |
| **ESP** | dano mágico (ESP/9 a ESP/4), cura, tamanho do recurso |

**Dano em uma linha:** rolagem entre mín e máx (atributo + arma) × multiplicador da habilidade → crítico (×1,5; Humano ×1,75) → excelente (×1,2 e ignora metade da defesa) → defesa → resistência elemental → diferença de nível → vantagem de facção → arredonda, mínimo 1.

**Defesa sem zerar dano.** No MU original a defesa era subtraída e monstro de nível alto ficava imune. Aqui a defesa vira porcentagem: `def / (def + 40 + 8 × nível do atacante)`, com teto de 70%. Defesa sempre ajuda e nunca anula.

**Acerto.** No mesmo nível o jogador acerta cerca de 9 em 10. Cada nível que o alvo tem a mais tira 3%. Habilidade em área nunca erra.

**Diferença de nível.** Bater em quem está acima: −4% de dano por nível (até −60%). Abaixo: +2% por nível (até +20%). Vale para os dois lados, então ir para a cripta cedo demais dói de verdade.

**Vantagens de facção** (classes.md, seção 6): +12% de dano (Tecnomancer +15% em invocações). Mutante resiste 30% a veneno, sangramento e maldição.

**Humano híbrido (Jefin).** O Humano luta com espada larga e escopeta. O ataque básico troca sozinho pela distância: até 1,8 tile é um golpe de espada larga em arco (FOR, acerta até 2 inimigos), mais longe é tiro (AGI, gasta munição). Shift força o tiro. Habilidades: Tiro Certeiro (1), Corte Giratório (3, slash da espada larga girando 360° em volta do corpo: acerta todos em volta e empurra para fora), Coquetel de Querosene (5, skill de área de farm), Arrancada (6, dash de 4 tiles com a espada larga estendida que corta todos no caminho, 2 cargas, recarga 5 s e 0,2 s de invulnerabilidade; o próximo ataque causa +30%), Rajada (9), Água Benta e Pólvora (12, vale para bala e lâmina). Armadilha de Prata passou para o 15. Na simulação ele fica no meio da tabela de dano e aguenta um pouco mais que antes.

**Recursos.** Cada classe joga diferente por causa do recurso: o Demônio fica mais forte com Brasa acima de 80, mas se queima se transbordar; o Cultista paga em HP e recupera matando; o Mutante ganha Fúria apanhando (+2% de dano a cada 10). Detalhes em `classes_base.json`.

## 4. Postura e controle (`efeitos.json`)

- Todo golpe tira postura. Monstros leves **recuam a cada golpe** e perdem o ataque em preparo, o que deixa o corpo a corpo satisfatório. Brutos, elites e chefes têm **super-armadura no preparo**: não adianta bater, tem que sair do telegrafo.
- Postura zerada: **QUEBRADO!** em dourado, o alvo fica atordoado (0,6 s em monstro leve, 4 s em chefe) e toma +30% de dano. Em chefe, a postura não quebra de novo por 12 s.
- Atordoar, derrubar, enraizar, cegar e silenciar o mesmo alvo várias vezes em 15 s rende 100%, 50%, 25% e depois imunidade. Chefe é imune a atordoar, derrubar e provocar.

## 5. Monstros e IA (`mobs.json`)

Curva do monstro "normal" no nível L: HP `32 + 7L`, dano `6,5 + 1,9L` em média, XP `10 + 5L`. Cada monstro aplica um arquétipo:

| Arquétipo | Papel | Exemplos |
|---|---|---|
| rasteiro | frágil, rápido, em bando | Corvo de Cinza, Cão de Vala, Larva de Carne, Fogo-de-Vela |
| normal | o padrão | Carniçal, Não-Julgado |
| bruto | lento, golpe telegrafado, super-armadura | Porco Pestilento, Açougueiro Oco, Monge Emparedado |
| atirador | mantém distância | Gancheiro, Querubim Desfeito |
| conjurador | cura, controla, invoca | Carpideira de Ossos, Eco da Trombeta |
| elite / raro | mini-chefe | Capataz Gancho, Filho de Cardo |

A IA é uma máquina de estados no servidor (ocioso → alerta com "!" → perseguir → atacar → voltar). Cada monstro tem um traço próprio para não serem todos iguais: o corvo circula e mergulha, os cães cercam por ângulos diferentes e fogem uivando, o Não-Julgado pisca para o seu lado, o porco investe em linha e fica tonto se bater na parede, o monge se esconde na parede, a carpideira cura os outros e precisa morrer primeiro, a larva estoura ao encostar, o Eco solta um anel com um vão para atravessar. Na cripta os grupos misturam papéis (bruto + conjurador, rasteiros + atirador) para o jogador ter que escolher o alvo.

## 6. Os três chefes (`chefes.json`)

Feitos para **um jogador sozinho** no nível do chefe, com equipamento comum ou mágico e 5 poções. Cada um ensina uma coisa e tem um momento de punição em que fica EXAUSTO.

### Andar 1: Andras, o General Partido (nível 8)
Demônio que foi general, partido ao meio na Grande Batalha, sobrevive comendo os guerreiros mortos (ideia do Jefin). Só o tronco, se arrasta com os braços e luta com o estandarte quebrado do próprio exército.
- **Mecânica central:** 6 Pilhas de Mortos na arena. Ele vai até uma e **devora** (4 s, barra visível): cura 8% e ganha *Fome Saciada* (+10% de dano e fica 6% maior, acumula). O jogador escolhe entre bater nele, **destruir as pilhas** (fogo e sagrado dão o dobro) ou **quebrar a postura dele enquanto come**, o que cancela a cura e o deixa exausto.
- **Fase 2 (60%):** "De pé, soldados!": ergue Soldados Caídos das pilhas, e cada soldado morto vira comida rápida para ele. Vomita brasa em cone.
- **Fase 3 (30%):** tenta agarrar e comer o jogador (*Banquete*): cone telegrafado; se pegar, drena HP e se cura; golpes contam em dobro para a postura para soltar. Depois fica exausto 3 s.
- Ensina: **negar recurso do chefe e usar a postura para interromper.**

### Andar 2: Irmã Celeste, a Carpideira (nível 10)
- **Fase 1:** Lamento em cone (silencia), Pranto que Cai (3 círculos nos pés do jogador em sequência, tem que continuar andando) e Regência (uma Corista de Osso canta e dá escudo nela se não for morta em 6 s).
- **Fase 2 (65%):** levita imune enquanto 4 coristas cantam; do centro saem ondas em anel com um vão que gira. Matar coristas encurta o coro. No fim ela cai exausta 5 s.
- **Fase 3 (30%):** apaga as velas. Só há luz em 3 pontos que mudam de lugar; fora da luz o jogador perde 2% do HP por segundo. Chama 2 carpideiras.
- Ensina: **trocar de alvo e posicionamento.**

### Andar 3: Zacarias, o Arauto da Trombeta Calada (nível 12)
- **Fase 1:** Lança do Juízo em linha, Asas Cortantes em círculo com empurrão e Marca do Juízo (círculo que segue o jogador e trava 0,6 s antes da coluna de luz cair).
- **Fase 2 (70%):** voa até a trombeta e canaliza a Primeira Nota por 10 s com 3 Ecos em volta. **Quebrar a postura interrompe.** Se a nota sair, tira 60% do HP de quem não estiver atrás de um pilar.
- **Fase 3 (40%):** asas em chamas, a arena encolhe com um anel de fogo, lança dupla e nova tentativa de nota a cada 45 s.
- Ensina: **tudo junto**: postura, cobertura, adds e espaço.

**Tempo de luta na simulação** (solo, nível do chefe): General 63 a 99 s (mais com as curas), Celeste 84 a 132 s, Zacarias 120 a 189 s. Golpe básico de chefe tira 7% a 15% do HP; golpe grande telegrafado, 15% a 34%. Ver `balanceamento.txt`.

## 7. Progressão (`progressao.json`)

- Nível máximo **400** (responde o ponto em aberto 2 de classes.md). XP para o próximo nível: `75L² + 375L` (v0.2, 3x a primeira versão por causa dos spots; nível 1→2: 450 XP; 7→8: 6.300; 12→13: 15.300), mais íngreme depois do 100.
- Ritmo (v0.2): farmando no spot do próprio nível com poções, **4 a 9 min por nível entre o 5 e o 10**. Nível 7 em 50 a 70 min, nível 12 a 13 em mais umas 2 h. Cerca de 30% da XP vem de missões (sugestão para a thread de missões: missão comum = 40% do nível, história = 70%).
- Monstro 5+ níveis acima dá +20% de XP; 4+ abaixo cai rápido até 10%.
- Morte: renasce no acampamento, sem perder item; a partir do nível 10 perde 2% da XP do nível (nunca perde nível).

## 8. Drops e baús (`drops.json`)

- **Raridades:** Comum (cinza), Mágico (azul aço, 1 a 2 opções), Raro (ouro sujo, feixe de luz), **Excelente (verde ácido, sempre com uma opção excelente, como o MU)** e Lendário/Relíquia (vermelho, únicos com nome). Os brilhos já existem na thread Efeitos visuais.
- Itens podem cair com **+1, +2 ou +3** (19%, 7%, 2%), cada + soma 8% no atributo base.
- O drop salta do corpo em arco e se espalha; Alt mostra os nomes no chão; ouro é pego passando por cima. Loot é pessoal (pronto para o multiplayer).
- **Proteção contra azar:** Raro garantido depois de 250 abates sem Raro; Relíquia de chefe garantida na 6ª vitória sem uma.
- **Baús:** Caixote Podre (comum, 10% de chance de armadilha de veneno), Baú de Ferro (trancado, chave do elite ou gazua), **Baú Faminto** (1 em 12 caixotes da cripta é um mímico elite) e o **Relicário da Trombeta** atrás do Zacarias (1 vez por dia, mínimo Raro, a sala acende vela por vela antes de abrir).
- Cada chefe tem relíquias sugeridas com efeito próprio (por exemplo, a Dragona do General: abates curam 3% e dão dano acumulativo). Os itens em si são da thread Skills, itens e ícones; as tabelas usam tags (`equip:faixa2`, `lendario:general`).

## 9. Skill em leque, modo automático, poções e spots (`farm_auto.json`, `farm.py`)

Pedido do Jefin: spots estilo MU para farmar nível, uma skill em área no nível 5 e um modo automático que usa essa skill sozinho, com a mana acabando se o jogador abusar.

- **Skill em leque no nível 5 para todas as classes** (cone de 75°, 3 tiles, recarga de 2 a 2,4 s, nunca erra): com nomes e formas da thread de skills: Leque do Juízo (Anjo), Espinhos de Sangue (Cultista, não usa abaixo de 25% de HP), Terremoto Pútrido (Mutante), Ceifa Infernal (Demônio), Coquetel de Querosene (Humano) e Tempestade de Bobina (Tecnomancer). **Custo, recarga e dano que valem são os de `farm_auto.json`/`classes_base.json`** (recarga de 2 a 2,4 s, mais lenta que a provisória de skills.json).
- **A "mana" de cada classe é o próprio recurso** (Graça, Carga, Fôlego, Fúria, Brasa; o Cultista paga em HP). Spammar o leque gasta de 2 a 4 vezes mais rápido do que o recurso volta, então a barra seca em 15 a 40 s. Skill em área só gera Graça, Fúria ou Brasa pelo primeiro alvo, para o leque não se pagar sozinho num grupo grande.
- **Modo automático (tecla Z):** ataca o mais próximo dentro de um raio (6 tiles por padrão) em volta de onde foi ligado. Usa o leque quando há 2 ou mais monstros no cone e ataque básico com um só. Bebe poção sozinho (vida abaixo de 50%, recurso abaixo de 25%, ajustável). Sem poção, luta no básico até o recurso voltar a 50% e retoma o leque. Desliga sozinho sem poção de vida com HP baixo, quando aparece chefe ou elite, quando o jogador clica para andar e na morte. Não anda até outro spot nem foge: é ajudante de farm, não bot.
- **Poções acessíveis:** Frasco de Sangue P (120 HP) por 6 moedas, Elixir de Éter P (40% do recurso) por 8 (vale este preço, não os 15 de itens.json), versões médias a partir do nível 8 (18 e 22), pilha de 100, recarga de 1 s. Começa com 20 de vida e 10 de recurso. Monstro de spot tem 10% de chance extra de soltar poção.
- **Spot padrão:** 12 monstros, renascimento de 14 s, mistura de normais, rasteiros e alguns brutos. Faixas sugeridas: 3 a 5 e 5 a 7 na área inicial, 7 a 9 na entrada da cripta, 9 a 12 no deserto (os lugares ficam com a thread de mapas).

**Conta de farm** (jogador no nível do spot, ver `farm_resultado.txt`):

| Spot | Abates/min com elixir | Abates/min sem elixir | Ouro/min | Gasto em poções | Min por nível com elixir |
|---|---|---|---|---|---|
| nível 5 | 20 a 32 | 12 a 24 | 190 a 310 | 15% a 38% do ouro | 3,3 a 5,4 |
| nível 7 | 20 a 31 | 12 a 23 | 270 a 420 | 13% a 30% | 4,5 a 7,1 |
| nível 10 | 19 a 30 | 12 a 23 | 370 a 580 | 12% a 24% | 6,2 a 9,6 |

Usar elixir rende de 30% a 60% mais abates e custa de um quarto a um terço do ouro do próprio spot: compensa, mas o jogador não fica preso pagando para jogar. O Demônio farma mais rápido e o Mutante mais devagar, porque é tanque e quase não precisa de poção de vida.

## 10. Pendências e combinações com outras threads

- **Missões, NPCs e história:** adotou o nome Andras, os ids, os níveis e o XP de missão; falas de combate em `design/missoes/dados/monstros.json`. Os níveis da cripta (andar 1: 6 a 8, andar 2: 8 a 10, andar 3: 10 a 12) são proposta minha.
- **Skills, itens e ícones:** itens com as tags de `drops.json`; os números de habilidade em `classes_base.json` são os de balanceamento.
- **Prévia jogável:** implementa a partir dos JSON; o `simular.py` deve continuar batendo com o jogo se as fórmulas forem trocadas.
