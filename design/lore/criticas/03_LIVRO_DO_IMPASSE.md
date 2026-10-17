# Crítica nº 3 · `design/lore/LIVRO_DO_IMPASSE.md` (prefácio + 12 capítulos, 34 KB)

Crítico: a thread "Crítico de lore". Leitura integral. Cânone conferido em `historia.md` e `dados/npcs.json`.

## Veredito

Confesso, a contragosto: é o melhor texto do projeto. Quando os documentos falam, o livro é bom de verdade.
"Perdi o olho esquerdo e o Teodoro. Metade dos passageiros chegou. Anoto a metade que chegou." Isso é escrita.
Mas o narrador que costura os documentos tem **dois erros de cânone graves** e, nos fechos de capítulo,
volta a cair nos mesmos tiques que eu já tinha apontado no guia. Ele chega a colar no livro uma frase do
próprio guia. Nota 7,5. Com as correções abaixo, sobe para 9.

## 1. Erros de cânone (corrigir antes de qualquer coisa)

1. **Frei Anacleto não estava vivo em 1962.** `npcs.json` diz que ele "foi emparedado vivo por penitência... e
   morreu antes do Juízo", e `historia.md` l. 297 (missão f04) diz que **Simão assentou o último tijolo da cela
   em 1693**. O prefácio faz dele um monge vivo da era dos bondes: "Eu era monge do ossário... Eu gostava do
   som dos bondes", "Pela fresta do pão eu ouvi o fim do mundo começar", e no cap. IV, "Eu comi". Em 1693 não
   havia bonde, e um morto não come. Pior: a f04 depende desse tijolo de 1693; o livro desmonta uma missão.
   Correção de enredo, não de frase: ele é um emparedado de 1693 que **levantou** na meia nota, como os outros,
   dentro da cela. Isso é melhor do que o que está escrito: o cronista do Impasse é ele mesmo um Não-Julgado.
2. **Anselmo é o Doutor.** `npcs.json`: Anselmo Graxa, "Doutor e Guardião da Vela", pároco que "de manhã
   desmontou o motor de um bonde e **acendeu a primeira Vela**". O livro o divide em dois: no cap. II o padre
   Anselmo faz o lacre, e no cap. IV "O Doutor acendeu uma vela de arco com o motor do bonde 7", no "Mês 3 do
   cerco". O leitor entende que são duas pessoas, e a data contradiz o cânone ("de manhã", não no mês 3). No
   cap. V, "os Engenheiros Hereges, que são o Doutor e os seus", contradiz o próprio livro, que acabou de dizer
   que quem fundou os Hereges foi o Gustavo.
3. **Onde fica a parede?** A cela é no **Ossário das Carpideiras**, o andar 2 da Cripta, todo agressivo, com a
   Irmã Celeste cantando ao lado. O prefácio diz que passam por ela "soldados, cultistas, coveiros, crianças",
   e no fim "toda noite chega um recruta novo pela minha parede". Criança no andar 2 de uma cripta hostil? E o
   cronista nunca menciona a vizinha que canta do outro lado da pedra, que é a coisa mais óbvia que ele
   ouviria. Ou expliquem quem desce até ele e por quê, ou façam da canção da Celeste o som de fundo do livro
   inteiro.
4. **Monge Emparedado** é um mob da Cripta (`monstros.json`). O livro precisa de uma linha do Anacleto sobre os
   irmãos de ordem que não ficaram lúcidos como ele. Sem isso, o jogador mata "monges emparedados" sem saber
   que o cronista é um deles.

## 2. A frase do guia colada no livro

Cap. XII: "Nenhum lado é bom. A Vigília salva vidas e faz coisas horríveis para isso. Os Arautos são cruéis e
sinceros." É a regra 5 da §3 do `GUIA.md`, **palavra por palavra**. Uma instrução para redatores virou fala do
personagem no clímax do livro. É a marca mais clara de texto montado por máquina em todo o volume. Se a
mensagem tem que estar lá, o livro já a mostrou (a Ivone, o Gaspar derretendo o sino). Dizer depois é explicar
a piada.

## 3. Tiques que voltaram

**"Não é X. É pior: Y."** Cap. IV: "Não é uma mulher cruel. É pior: é uma mulher sincera." Construção de
contracapa. A Ivone é bem construída no parágrafo anterior (o alívio quando a trombeta soou); a frase de efeito
rebaixa o que veio antes.

**"Por isso é o mais perigoso."** Cap. VIII, Cultista: "É descartável, e sabe. Por isso é o mais perigoso dos
Arautos." É a frase de toda ficha de classe de todo RPG. Além disso, é um Versículo do Coro: o Coro não
chamaria um Arauto de descartável por escrito. A voz quebra.

**O Warlord inteiro** (cap. VIII). Repete "não reza em nenhuma", que eu já marquei no guia. "Nem Arauto. Nem
Vigília. Apenas ódio. É a única coisa que ele carrega que não enferruja." é anti-herói de capa de revista. "Os
dois lados o contratam. Os dois lados o odeiam. Os dois lados dormem melhor..." é anáfora tripla. É o trecho
mais fraco do livro, e é da Corvina, que no resto vende segredo com preço: aqui ela faz poesia de graça. O
início ("Lutou pela Vela por carne e pela Capela por água") é bom; cortem do "Nem Arauto" em diante.

**Contagem de anáforas e tríades**, só as mais visíveis:
- I: "sete trombetas, sete arautos, sete sopros"
- XI: "Três coisas aconteceram... A Fenda abriu. A mata... A areia..."
- XII: "Ainda no silo. Ainda inteira. Ainda minha." (esta funciona; é a única que funciona)
- XII: "Começa pela cerca. Começa pela Capela. Começa pelo cemitério."
- XII: "Não há salvação no Impasse. Há a Vigília, há o Juízo, e a noite comprida entre os dois."

Três no último capítulo. O fim do livro vira um sino batendo sempre no mesmo tempo. Fiquem com a da Isaura e
cortem as outras.

## 4. Explicar o que já foi mostrado

- **Cap. VI, quarta trombeta:** "por isso a paleta do mundo é sépia e cinza, por isso a única coisa que brilha é
  o Amargo." Um monge do século XVII falando de **paleta**. É direção de arte vazando para dentro do mundo, o
  mesmo erro que marquei no guia (§1.5), agora na boca do personagem. Cortar inteiro.
- **Cap. X:** "São o espelho dos nossos Não-Julgados: lá os vivos pararam esperando um Juízo que foi recusado;
  aqui os mortos levantaram para um Juízo que travou." É uma bela simetria, e é exatamente por isso que o
  leitor tem que descobri-la sozinho. Dita assim, vira nota de rodapé.
- **Cap. X, as sete Colunas:** "Mentalismo, Correspondência, Vibração, Polaridade, Ritmo, Causa e Efeito,
  Gênero." Sete nomes em fila com vírgula é verbete, não crônica. Não questiono o conteúdo hermético, que no
  mundo é verdade; questiono a forma. Nomeiem a que importa (a do Ritmo, que trincou) e deixem as outras seis
  para a inscrição de cada coluna, no jogo.
- **Cap. X:** "É o lugar mais bonito que já descreveram pela minha parede, e é uma prisão." É a gaiola de ouro,
  um clichê. A frase anterior, sobre os autômatos que cuidam da lavoura de uma tarde que não acaba, já dizia isso
  melhor.

## 5. O mesmo truque duas vezes

Cap. IX (Khem): o Céu "bateu nas faces polidas das pirâmides, e encontrou lá só o próprio rosto, e voltou".
Cap. X (Atlântida): o Juízo "encontrou lá só o próprio reflexo, e voltou". E o Despacho 231 repete: "As faces
refletem o que vem de cima". São três vezes em dois capítulos. Se é a mesma lei hermética operando nos dois
lugares (e tem tudo para ser), alguém dentro do livro tem que **notar** a repetição, e o Anacleto é o
candidato. Do jeito que está, parece que o autor esqueceu que já tinha usado a imagem.

## 6. Linguagem de jogo e repetição

- Cap. V, Tobias: "Quem está no **spot** precisa beber." "Spot" é termo de jogo e está proibido no mundo pela
  §8.2 do guia. "Quem está na fogueira" resolve.
- A Mãe Cardo aparece duas vezes com a mesma informação: no cap. V (braço, filho de quem não fala) e no cap.
  VIII (braço, filho levado inteiro, caldo no portão, "não me pergunte para quem"). A segunda vez, pelo Coveiro,
  é melhor. Cortem a do cap. V.
- "Versículo do Sino" é uma voz nova (Irmã Sinésia, cap. VII e X) que não está na tabela da §2 do guia. O guia
  diz que voz nova só entra registrada.

## 7. Segredos: insinuação demais

O guia diz que segredo com dono só se insinua. O livro insinua quem é o Ladrão em quatro lugares: cap. II ("o
coveiro muda mais rápido que os outros"), cap. VI (o Ladrão e a árvore), cap. XI ("Toda semente é roubada de
alguém... Não me pergunte da floresta") e na nota final, que lista as perguntas em aberto. Dois lugares são
uma pista; quatro são uma seta pintada no chão. Cortem a do cap. XI ou a da nota final. A nota final, aliás,
quebra a regra das vozes: "para quem lê de fora" é o autor falando, não o Anacleto.

## 8. O que está ótimo (não toquem)

- A Rádio da Noite 1 inteira: "Às 03h11 eu li uma ordem... Não vou repetir a ordem." E "Ainda no silo. Ainda
  inteira. Ainda minha."
- Os Despachos nº 1 e 2 da Ferrolho, a promoção de guarda-freios a Capitã ao longo dos capítulos e "O bonde não
  freia a tempo para general nenhum."
- "Que a Legião segure o campo." / "Guardei esta folha. Vou cobrar." Isso é o Malfas inteiro em duas linhas.
- Gaspar derretendo o sino: "cada tiro da Vigília é uma badalada. Ele diz isso sem rir."
- "A Andras, até o fim." costurado por dentro da roupa.
- Sariel riscando o batente e, no Nº 11.214, a soleira. Isso é a melhor imagem do livro.
- "Se a promessa é verdade, a resposta está atrás dele. Se não é, também."
- Joana: "Chorou. Eu também, mas sou lenhadora, não conto."

## Pedidos objetivos

1. Refazer o Anacleto como emparedado de 1693 que levantou na meia nota (prefácio, cap. I e cap. IV).
2. Unificar Anselmo e o Doutor e acertar quando a Vela foi acesa; tirar "o Doutor e os seus" dos Hereges.
3. Resolver quem passa pela parede no andar 2 e pôr a canção da Celeste no fundo do livro.
4. Apagar a frase do guia no cap. XII.
5. Cortar "É pior: é uma mulher sincera", "Por isso é o mais perigoso" e o Warlord do "Nem Arauto" em diante.
6. Cortar a "paleta", a explicação do espelho e a lista das sete Colunas.
7. Fazer o Anacleto notar o truque do reflexo, ou usá-lo uma vez só.
8. Trocar "spot", remover a Mãe Cardo duplicada e registrar o Versículo do Sino no guia.
9. Tirar uma das quatro pistas do Ladrão; reescrever a nota final na voz de alguém do mundo, ou cortá-la.
