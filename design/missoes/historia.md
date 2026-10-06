# DARK PASSAGE: História da Paróquia de São Lázaro (v0.3)

> Bíblia de lore da primeira área jogável e da dungeon **Cripta da Trombeta Calada**.
> Base: `design/classes.md` (facções e classes). Dados do jogo em `design/missoes/dados/`.

## 1. O que aconteceu aqui

Quando as sete trombetas começaram a soar, cada uma foi confiada a um anjo arauto e escondida num ponto da Terra.

A **terceira** soou primeiro, longe daqui. Caiu do céu a estrela que as Escrituras chamam de **Absinto**, ardendo como uma tocha, e um terço das águas ficou amargo. O que a estrela deixou não foi fogo: foi um pó fino, esverdeado, que cai até hoje como neve que não derrete. Os sobreviventes chamam esse pó de **Amargo**. Ele amarga a água, adoece o corpo, faz as pragas florescerem nos ossos e brilha fraco no escuro. Os Tecnomancers medem com contadores que estalam como contas de terço; os Arautos chamam de sacramento.

A **quinta trombeta** foi enterrada sob a Paróquia de São Lázaro, uma cidade de frigoríficos, bondes, sinos e cemitérios na beira da estrada do sul.

Na noite do Juízo, o arauto **Zacarias** desceu para tocá-la. Ele soprou, e a trombeta deu **meia nota**. Os túmulos se abriram. Os mortos de São Lázaro levantaram para serem julgados, como as Escrituras prometiam.

Foi aí que a Vigília chegou. Um grupo de engenheiros hereges e soldados velhos cravou um **lacre de chumbo** no bocal da trombeta e a calou no meio do sopro. Zacarias ficou preso lá embaixo com o instrumento mudo nas mãos. A nota nunca terminou.

E os mortos? Levantaram para o Juízo, mas o Juízo não veio. Hoje vagam pela paróquia com o **lacre de cera do julgamento ainda inteiro no peito**: são os **Não-Julgados**. Não estão vivos, não estão mortos, não estão salvos nem condenados. Esperam.

São Lázaro virou o retrato do impasse: o fim começou e não termina.

## 1.1 O Deserto de Absinto

Depois da Grande Batalha, o Amargo continuou caindo sobre a região, ano após ano, e o vento o juntou em dunas. O rio quase secou: do Jordão sobrou um fio de água verde e amarga correndo no leito rachado, o **Rio Amargo**, único oásis do deserto. A planície virou o **Deserto de Absinto**: areia cinza com veios verdes, vidro derretido onde a batalha queimou mais forte, e dunas que andam alguns metros por noite, como uma maré lenta.

A areia engoliu São Lázaro até o quarto andar. **A rua de hoje é o telhado de ontem.** Os sobreviventes moram nos andares de cima dos prédios tortos, entram nas casas pelas janelas e cavam escadas para baixo quando precisam de algo que ficou enterrado. Torres de igreja, chaminés de frigorífico e postes de bonde saem da areia como mastros de navio afundado.

O que torna o lugar diferente de qualquer outro deserto:
- **A maré de areia.** O que a duna cobre hoje, ela descobre amanhã. Baús, ruas inteiras e túmulos aparecem e somem. Por isso todo mundo aqui tem um mapa, e todos os mapas estão errados.
- **O Amargo é sagrado e venenoso ao mesmo tempo.** À noite a areia brilha verde e os Não-Julgados brilham mais forte que ela. Água doce é rara; a água comum tem gosto de remédio e cobra o preço no corpo, e é daí que vêm as mutações.
- **Os trilhos ainda servem.** Os bondes da linha 7 correm sobre os trilhos que a areia deixa à mostra, empurrados por velas de lona, como barcos de terra.
- **Nada de saqueadores motorizados.** Não há gasolina nem estrada. Aqui se anda a pé, de bonde-veleiro ou não se anda.

## 1.2 A estrela que nós soltamos (verdade revelada na linha D)

O que os Arautos pregam e o povo repete: a estrela Absinto caiu do céu na terceira trombeta. **Não é verdade.**

Quando a hoste celeste cobriu o céu da capital, o Comando Sul respondeu do único jeito que sabia. A **Ogiva Absinto-1** subiu do **Silo São Lázaro**, a poucos quilômetros da paróquia, e explodiu lá longe, no meio da formação alada. O clarão no céu foi o que os cultistas chamaram de estrela; a cratera onde ela "caiu" é a **Cratera de Absinto** (área 80-100 do mapa-múndi). O **Amargo** é a cinza radioativa dessa explosão, trazida pelo vento ano após ano. A terceira trombeta tocou, sim: fomos nós que tocamos.

- O projeto se chamava Absinto por piada de quartel. Eram duas ogivas. A **Absinto-2** nunca foi lançada e continua no silo, dentro da tempestade de areia.
- **Isaura Valente**, a radiotelegrafista que leu a ordem às 03h11, mora na torre enterrada da Rádio São Lázaro e lê toda noite a contagem da segunda ogiva.
- O clarão do lançamento gravou no muro da vila militar a sombra de quem olhava o céu: as **Sombras Gravadas**, que descolam à noite.
- O **Sargento Brandão**, último operador, ficou fundido à cadeira de comando esperando a segunda ordem.
- Os anjos sabem a verdade e escondem: um Apocalipse que os homens responderam com uma bomba é um Apocalipse que os homens podem cancelar. Por isso os Arautos chamam o Amargo de sacramento.
- No fim da linha, o jogador decide o destino da Absinto-2: **desarmar** (flag `ogiva_desarmada`) ou **entregar a chave à facção** (flag `ogiva_com_faccao`). Uma segunda estrela nas mãos de anjos, demônios ou da Vigília é gancho para o futuro.

## 1.3 A aliança podre e a Legião sem general (linha E)

Os Arautos não são um exército, são três inimigos que o Céu obrigou a marchar juntos: **anjos**, que desprezam os outros dois; **demônios** da **Legião Blasfema**, que obedecem porque o Inferno também quer o fim; e **cultistas**, humanos que traíram a própria espécie e sabem que são descartáveis.

Na Grande Batalha os anjos recuaram e deixaram a Legião segurando a linha. O general **Andras** sumiu. Desde então:
- Os demônios acham que os anjos o apunhalaram; os anjos acham que os cultistas o venderam; Malfas quer que ele continue sumido para assumir a Legião.
- Metade da Legião **desertou** e acampou no Rio Amargo, cobrando pedágio da água. Atrás das insígnias arrancadas, todos costuraram "A Andras, até o fim": desertaram da aliança, não do general.
- Uma célula de cultistas, os **Apóstatas**, escondida no Bosque das Viúvas, quer a Capela só para humanos de fé e planeja envenenar o Comandante Abdiel e culpar os demônios.
- **Corvina**, atravessadora no Bairro Afogado, vende a mesma verdade para a Vela e para a Capela.
- A investigação leva ao **Marco do Corte** (o bonde tombado de Odete), a uma meia dragona cortada reto e a um rastro de arrasto que some debaixo do abatedouro: o general está vivo, pela metade, no fosso (chefe 1 da cripta).
- Escolhas: a quem contar o plano dos Apóstatas (`avisou_anjos`, `avisou_demonios`, `calice_envenenado`); e, no fim, Arautos decidem com Malfas (`andras_revelado` ou `malfas_general`), Vigília decide com Odete (`vigilia_espalhou_andras` ou `vigilia_guardou_andras`).

## 2. A Grande Batalha, o cerco e o açougueiro

Na mesma noite da meia nota, os Arautos marcharam sobre São Lázaro para proteger a trombeta. À frente da **Legião Blasfema**, o exército do Inferno, vinha o general **Andras**. A Vigília e o povo da cidade os enfrentaram nos campos ao sul: a **Grande Batalha dos Campos de Cinza**. Os campos queimaram tão forte que a areia virou vidro, e nunca mais deram nada.

Andras ficou de pé nos trilhos para segurar a linha. O bonde da linha 7, dirigido por **Odete Ferrolho**, passou por cima dele e o partiu ao meio. Quando a trombeta calou, os anjos receberam ordem de recuar e voaram embora. A Legião não tinha asas e morreu no campo.

Depois disso, a cidade ficou cercada pelos mortos por meses. Quem sobreviveu comeu o que o **Abatedouro Carniça** fornecia. O dono, **Benedito Carniça**, nunca deixou faltar carne.

Ninguém perguntou de onde vinha. O Livro de Óbitos do coveiro tem a resposta: Benedito comprava corpos frescos do cemitério à noite. Depois recolheu os mortos da Grande Batalha e jogou o que não cabia nas câmaras num fosso do porão. A metade de cima de Andras estava na pilha. Ele acordou no escuro e começou a comer. Benedito desceu para ver quem pedia mais carne lá embaixo e nunca subiu. O fosso fica em cima das catacumbas antigas da paróquia, e mais fundo ainda está a câmara da trombeta.

## 3. As duas bases

### Acampamento da Vela (Vigília)
Montado no teto de vidro da antiga estação de bondes, a única cúpula que a areia não quebrou. Os bondes-veleiros atracam nos trilhos que saem da duna. No centro, a **Vela**: uma lâmpada de arco gigante que o Doutor Anselmo construiu com bobinas de bonde e fé herege. A luz dela queima os Não-Julgados e, por algum motivo que nem ele entende, faz o Amargo assentar no chão em volta, deixando o ar limpo. Por isso o acampamento ainda existe. A Vela come óleo, cobre e paciência.

### Capela de São Lázaro (Arautos)
A igreja da paróquia, enterrada até as janelas do coro. Só a torre e o telhado saem da duna, e os Arautos entram pela rosácea quebrada e descem por escadas de corda até a nave, onde a luz entra verde pelos vitrais cobertos de areia. A cruz da torre foi trocada por uma **trombeta partida em chamas brancas**. Os cultistas bebem água com Amargo de propósito, como comunhão. Anjos e cultistas rezam no altar; os demônios ficam do lado de fora, no cemitério de trás, porque o Comandante Abdiel não os deixa entrar. Eles querem a mesma coisa que a Vigília quer impedir: descer à cripta, arrancar o lacre de chumbo e deixar a quinta trombeta terminar a nota.

## 4. O coveiro

**Simão** cuida do Cemitério de São Lázaro desde que alguém se lembra. No deserto, o trabalho do coveiro virou o contrário: a maré de areia desenterra os túmulos toda noite, e ele passa os dias cobrindo de novo. Ele é o único que anda entre os Não-Julgados sem ser atacado. Não serve nenhuma facção. Atende quem trouxer velas.

O segredo dele (nunca dito em voz alta, só insinuado): Simão é **Lázaro**, o homem que foi chamado de volta da morte há dois mil anos. Morreu duas vezes e não conseguiu ficar morto nenhuma. A cidade tem o nome dele. Quando a trombeta der a nota inteira, ele finalmente será julgado, e ele ainda não decidiu se quer isso.

## 5. A dungeon: Cripta da Trombeta Calada

Entrada pelo porão do Abatedouro Carniça, atrás de uma porta de ganchos. Três andares, cada um mais antigo que o anterior.

| Andar | Nome | O que é | Chefe |
|---|---|---|---|
| 1 | **Porão do Matadouro** | Câmaras frias, trilhos de ganchos e, no fundo, a Vala da Grande Batalha, o fosso onde Benedito jogou os mortos do campo | **Andras, o General Partido** |
| 2 | **Ossário das Carpideiras** | Catacumbas medievais, paredes de crânios, celas de monges emparedados vivos | **Irmã Celeste, a Carpideira** |
| 3 | **Câmara da Trombeta** | Uma catedral subterrânea de antes da paróquia; no altar, a quinta trombeta lacrada | **Zacarias, o Arauto da Trombeta Calada** |

### Andras, o General Partido
*(chefe criado pelo Jefin)* General do Inferno, comandante da Legião Blasfema, partido ao meio pelo bonde de Odete na Grande Batalha. Sobreviveu no fosso do porão comendo os guerreiros mortos, dos dois lados, e por último o próprio Benedito. Quer subir e se vingar da humanidade por cada soldado que perdeu, e não perdoa os anjos que largaram a Legião no campo. Por isso odeia os dois lados.
Só o tronco: se arrasta com braços gigantes, o toco da cintura ainda em brasa, dragonas de general podres, e luta com o estandarte partido da Legião. Quanto mais come das Pilhas de Mortos, maior e mais forte fica.

### Irmã Celeste, a Carpideira
Freira das carpideiras de São Lázaro, as mulheres pagas para chorar nos enterros. Quando os mortos levantaram, ela desceu ao ossário para cantar para eles até dormirem de novo. Cantou por anos. Os ossos aprenderam a cantar junto. Hoje ela rege um coro de esqueletos e chora lágrimas de cera, e acredita que quem descer vai acordar seus filhos.

### Zacarias, o Arauto da Trombeta Calada
O anjo que deu a meia nota. Ficou anos no escuro, segurando uma trombeta que não soa. Enlouqueceu com uma ideia limpa: os Arautos o abandonaram, se misturaram com demônios e cultistas imundos, e portanto também merecem ser julgados. Quando tocar a nota inteira, vai julgar **todos**, Vigília e Arautos. Por isso os dois lados precisam derrubá-lo.
Asas acorrentadas ao teto por correntes que ele mesmo prendeu para não fugir do posto. Rosto de porcelana com a boca costurada em volta do bocal.

## 6. O arco do jogador

1. **Chegada (por facção).** O jogador entra pela sua base, ajuda com o básico (Carniçais, Corvos, Cães de Vala) e é mandado investigar o cemitério, onde os lacres dos Não-Julgados estão inteiros.
2. **O coveiro (comum).** No cemitério as duas histórias se encontram em Simão. Ele explica a meia nota, pede velas e o Livro de Óbitos, que revela o crime de Benedito, o fosso dos mortos da Grande Batalha e o caminho para a cripta.
3. **A cripta (comum).** Três chefes, três andares. Cada chefe derrubado entrega um pedaço da verdade.
4. **O bocal (por facção).** Com o Bocal da Trombeta na mão, o jogador volta à base e escolhe o destino dele. A escolha vira flag para o futuro.
   - Vigília: **destruir** o bocal (Capitã Odete) ou **entregar para estudo** (Doutor Anselmo, que acha que pode fazer uma "trombeta reversa").
   - Arautos: **entregar ao Comandante Abdiel** (os anjos guardam) ou **vender a Malfas** (os demônios guardam, em troca de favores). A desconfiança entre os dois aparece na cara.

5. **O deserto (níveis 5 a 12, as duas facções).** Depois da arma (v03/a03), duas linhas correm em paralelo e mandam o jogador para os spots de farm:
   - **Linha D, A Estrela Que Nós Soltamos** (Isaura): a estrela Absinto foi uma bomba humana. Termina no silo, com a Absinto-2.
   - **Linha E, A Legião Sem General** (Corvina): traições dentro dos Arautos e o sumiço de Andras. O último passo exige c02, porque o rastro desce para o porão do abatedouro.

## 7. Tom de escrita

- Frases curtas, secas, com humor de forca. Ninguém faz discurso longo, exceto quem é fanático.
- A Vigília fala como gente cansada: gíria, ironia, nomes de ferramenta.
- Os Arautos falam com liturgia: "irmão", "Juízo", "pureza". Os demônios zombam da liturgia.
- Nenhum lado é bom. A Vigília salva vidas e faz coisas horríveis para isso; os Arautos são cruéis e sinceros.
- O horror vem do cotidiano: carne, velas, sinos derretidos, crianças fazendo comércio de sucata, água que amarga a boca.
- Evitar o deserto genérico de filme: sem carros, sem gasolina, sem gangues motorizadas. O punk está na roupa das pessoas, não em veículos. O deserto daqui é uma cidade afogada em areia sagrada.
