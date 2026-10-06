# DARK PASSAGE: Classes e Facções (v0.1)

> Rascunho de design. Engine ainda não definida; números são pontos de partida para balanceamento.

## 1. O conflito

Deus ordenou o fim do mundo e enviou suas forças numa **Guerra de Extermínio**. As trombetas soaram, o céu rachou e as pragas começaram.
Mas os homens resistiram. Contra toda expectativa, lutaram contra as forças do Apocalipse e conseguiram segurá-las, criando um **impasse**: o fim começou, mas não se completa.

O jogo se passa nesse impasse. O mundo está em ruínas, nenhum lado consegue vencer, e cada território, relíquia e trombeta selada pode desequilibrar a guerra.
Duas facções disputam o que resta da Terra:

| Facção | Objetivo | Símbolo | Cor dominante |
|---|---|---|---|
| **Arautos do Juízo** | Consumar o Apocalipse que Deus ordenou | Trombeta partida em chamas brancas | Branco osso, ouro sujo, vermelho sangue |
| **Vigília** (a Resistência) | Sobreviver no mundo apocalíptico e cancelar o fim | Vela acesa dentro de uma engrenagem | Azul aço, verde ácido, laranja brasa |

## 2. Divisão das classes (definida pelo Jefin)

Anjo, Demônio e Cultista estão juntos a favor do fim. Humano, Mutante e Tecnomancer lutam para sobreviver no mundo apocalíptico. Cada classe pertence a **uma** facção só, e cada lado tem um tanque, um dano e um suporte.

| Papel | Arautos do Juízo | Vigília |
|---|---|---|
| Tanque / corpo a corpo | **Demônio** | **Mutante** |
| Dano | **Cultista** (magia) | **Humano** (físico à distância) |
| Suporte / híbrido | **Anjo** | **Tecnomancer** |

**Por que essa divisão (lore):**
- **Anjo**: soldado direto de Deus, executa a ordem.
- **Cultista**: humanos fanáticos que veem no fim do mundo a salvação.
- **Demônio**: a reviravolta da história. Até o Inferno faz parte do plano: Deus prometeu aos demônios as ruínas da Terra depois do fim, então eles marcham ao lado dos anjos. Aliados por obediência e cobiça, nunca por amor; a desconfiança entre os dois é constante.
- **Humano**: o povo comum que se recusa a morrer.
- **Mutante**: humanos deformados pelas pragas do Apocalipse. Os Arautos os chamam de abominações; eles provam que a vida se adapta até ao fim do mundo.
- **Tecnomancer**: cientistas e hereges que fundiram tecnologia e ocultismo para sabotar as trombetas.

## 3. Atributos (estilo MU)

A cada nível o jogador ganha **5 pontos** para distribuir:

- **FOR** (Força): dano físico corpo a corpo, peso carregado.
- **AGI** (Agilidade): dano à distância, velocidade de ataque, esquiva.
- **VIT** (Vitalidade): HP e defesa.
- **ESP** (Espírito): mana/energia, dano mágico, cura.

Cada classe tem um **recurso próprio** além do HP:

| Classe | Recurso | Como funciona |
|---|---|---|
| Anjo | Graça | Regenera ao curar aliados e ao golpear inimigos |
| Cultista | Sangue | Gasta o próprio HP para lançar magias; regenera ao matar |
| Mutante | Fúria | Sobe ao receber dano; cai fora de combate |
| Demônio | Brasa Infernal | Sobe ao causar dano; queima o próprio HP se transbordar |
| Humano | Munição + Fôlego | Munição consumível (crafting/compra) e fôlego para habilidades |
| Tecnomancer | Carga | Bateria que recarrega devagar; módulos aumentam a capacidade |

## 4. Evolução de classe (3 estágios)

Missões de evolução no **nível 150** e no **nível 400** (estilo MU).

| Classe | Estágio 1 | Estágio 2 | Estágio 3 |
|---|---|---|---|
| Anjo | Querubim Caído | Serafim | Arcanjo do Juízo |
| Cultista | Iniciado | Sacerdote de Sangue | Profeta do Fim |
| Mutante | Contaminado | Aberração | Besta do Apocalipse |
| Demônio | Diabrete | Senhor do Abismo | Arquidemônio |
| Humano | Sobrevivente | Caçador | Último Guardião |
| Tecnomancer | Engenheiro Herege | Tecnomante | Arquiteto do Amanhã |

## 5. As classes

### 5.1 Anjo (Arautos do Juízo)
**Papel:** suporte de cura e corpo a corpo leve. **Atributos principais:** ESP > FOR > VIT.
**Armas:** espada longa, lança, escudo sagrado. **Armadura:** placas brancas rachadas, asas de penas sujas.
**Fantasia:** um guerreiro celestial frio e implacável, que cura os seus enquanto julga os outros.

| Habilidade | Tipo | Efeito |
|---|---|---|
| Lâmina do Veredito | Ativa | Golpe corpo a corpo com dano sagrado; dano extra em Mutantes |
| Toque de Graça | Ativa | Cura um aliado |
| Asas da Ascensão | Ativa | Voo curto que atravessa obstáculos e inimigos |
| Halo Ardente | Área | Anel de luz que cega inimigos e cura aliados em volta |
| Sentença | Debuff | Marca um alvo; todo dano contra ele aumenta |
| Trombeta do Juízo (Estágio 3) | Suprema | Aliados ficam imunes a morte por alguns segundos |

### 5.2 Cultista (Arautos do Juízo)
**Papel:** mago de dano contínuo e invocador. **Atributos principais:** ESP > VIT.
**Armas:** adaga ritual, cajado de ossos, grimório. **Armadura:** túnicas e capuzes, quase nenhuma defesa.
**Fantasia:** paga com o próprio sangue por um poder enorme. Alto risco, alto dano.

| Habilidade | Tipo | Efeito |
|---|---|---|
| Sangria | Ativa | Projétil que causa sangramento contínuo |
| Pacto Rubro | Buff | Troca HP por dano mágico aumentado |
| Servo de Carne | Invocação | Invoca um zumbi que segura inimigos |
| Chuva de Cinzas | Área | Área amaldiçoada que reduz cura recebida |
| Profecia Sombria | Debuff | Inimigo morre se ficar abaixo de 10% de HP com a marca |
| Sétimo Selo (Estágio 3) | Suprema | Grande ritual em área; dano massivo após canalizar |

### 5.3 Mutante (Vigília)
**Papel:** tanque e berserker. **Atributos principais:** VIT > FOR.
**Armas:** garras orgânicas, machados pesados, punhos. **Armadura:** couro, carne endurecida, placas fundidas ao corpo.
**Fantasia:** quanto mais apanha, mais perigoso fica. O corpo muda visualmente com a evolução.

| Habilidade | Tipo | Efeito |
|---|---|---|
| Golpe Purulento | Ativa | Ataque pesado que envenena |
| Carapaça | Buff | Reduz o dano recebido; consome Fúria |
| Rugido da Praga | Área | Provoca inimigos próximos (taunt) |
| Regeneração Profana | Passiva | Recupera HP rapidamente fora de combate e ao matar |
| Investida Bestial | Ativa | Avança e derruba o alvo |
| Forma da Besta (Estágio 3) | Suprema | Vira uma criatura gigante por um tempo |

### 5.4 Demônio (Arautos do Juízo)
**Papel:** tanque ofensivo e assassino corpo a corpo. **Atributos principais:** FOR > AGI > VIT.
**Armas:** foices, espadas serrilhadas, correntes. **Armadura:** placas negras com brasas, chifres, asas de morcego rasgadas.
**Fantasia:** um predador que se alimenta do dano que causa e explode se não controlar a própria chama.

| Habilidade | Tipo | Efeito |
|---|---|---|
| Garra do Abismo | Ativa | Combo rápido que gera Brasa Infernal |
| Corrente de Danação | Ativa | Puxa um inimigo à distância para perto |
| Pele de Enxofre | Buff | Reflete parte do dano recebido como fogo |
| Passo Sombrio | Ativa | Teleporta para trás do alvo |
| Banquete | Passiva | Roubo de vida aumentado em alvos com pouco HP |
| Portão do Inferno (Estágio 3) | Suprema | Abre uma fenda que queima tudo em volta; dano extra em Humanos |

### 5.5 Humano (Vigília)
**Papel:** dano físico à distância e versatilidade. **Atributos principais:** AGI > FOR > VIT.
**Armas:** bestas, mosquetes, escopetas, espada curta de apoio. **Armadura:** couro, cotas de malha, sobretudos.
**Fantasia:** não tem poderes, só coragem, armas e engenho. A classe com mais variedade de equipamento.

| Habilidade | Tipo | Efeito |
|---|---|---|
| Tiro Certeiro | Ativa | Disparo de alto dano crítico |
| Rajada | Área | Leque de projéteis em cone |
| Armadilha de Prata | Ativa | Prende e causa dano extra em Anjos e Demônios |
| Água Benta e Pólvora | Buff | Munição especial com dano sagrado ou de fogo |
| Rolamento | Ativa | Esquiva rápida |
| Último Suspiro (Estágio 3) | Suprema | Uma vez por combate, sobrevive a um golpe fatal e ganha dano dobrado |

### 5.6 Tecnomancer (Vigília)
**Papel:** suporte, controle e invocações mecânicas. **Atributos principais:** ESP > AGI.
**Armas:** cajado-antena, luvas elétricas, pistola de raios. **Armadura:** trajes de couro com tubos, óculos, mochila gerador.
**Fantasia:** mistura ciência proibida e ocultismo. Cura com nanomáquinas, protege com escudos e coloca torretas no campo.

| Habilidade | Tipo | Efeito |
|---|---|---|
| Arco Voltaico | Ativa | Raio que salta entre vários inimigos |
| Nanoreparo | Ativa | Cura contínua em um aliado |
| Torreta Sentinela | Invocação | Torreta fixa que atira automaticamente |
| Campo de Força | Área | Escudo que absorve dano para aliados na área |
| Pulso Anti-Divino | Debuff | Silencia magias e buffs inimigos numa área |
| Máquina do Juízo Reverso (Estágio 3) | Suprema | Constrói um artefato que anula as supremas inimigas numa área |

## 6. Vantagens cruzadas

Pequenos bônus para criar rivalidades naturais, sem pedra-papel-tesoura rígido (+10% a +15% de dano):

- Humano: dano extra em Anjos e Demônios (armas de prata e água benta).
- Anjo: dano extra em Mutantes (purificação das abominações).
- Demônio: dano extra em Humanos (almas para colher).
- Tecnomancer: dano extra em invocações (servos do Cultista) e escudos sagrados.
- Cultista: dano extra em Tecnomancers (a fé corrompe as máquinas).
- Mutante: resiste a venenos, sangramento e maldições do Cultista.
- Dentro dos Arautos, Anjos e Demônios não podem formar grupo com bônus de sinergia (desconfiança), mas podem lutar lado a lado.

## 7. Notas de arte para o pipeline de sprites

- Sprites isométricos de **8 direções** com paleta de 16 cores (ver `tools/sprite-pipeline`).
- Cada facção tem uma sub-paleta para que o jogador identifique amigo ou inimigo de longe:
  Arautos com tons de osso, ouro e vermelho (Demônios puxando para o preto e brasa); Vigília com aço, verde ácido e laranja.
- Silhuetas precisam ser distintas mesmo pequenas: asas (Anjo), capuz e cajado (Cultista), corpo largo e assimétrico (Mutante), chifres (Demônio), sobretudo e arma longa (Humano), mochila com antenas (Tecnomancer).
- Equipamento troca o visual (estilo MU), e o estágio 3 de cada classe tem silhueta própria.

## 8. Pontos em aberto

1. Gênero do personagem: livre para todas as classes ou fixo por classe (como no MU)?
2. Nível máximo e curva de experiência.
3. PvP: guerra de facções aberta no mapa (estilo Dark Eden) ou em zonas/horários definidos?
