# DARK PASSAGE · Guia de escrita da lore

Este guia vale para **todo texto que o jogador lê**: missões, diálogos, falas de ambiente, itens, bestiário,
chefes, lugares, livros, tela de carregamento, interface e site. Quem escreve qualquer um deles lê este arquivo
antes. O cânone (o que aconteceu) está em `design/missoes/historia.md`; este guia diz **como contar**.

Ordem de autoridade: o que o Jefin decidiu > `historia.md` > os JSON em `design/missoes/dados/` > este guia.
Se algo aqui contradiz o cânone, o cânone vence e este guia é corrigido.

---

## 1. O mundo em doze linhas

1. Em **1962 (Anno Domini)** Deus ordenou o fim do mundo. As sete trombetas foram entregues a sete anjos arautos
   (os anjos do Apocalipse de João; a facção **Arautos do Juízo** tomou o nome deles depois).
2. O homem disse não. Respondeu com chumbo, fé herege e uma estrela feita à mão: a ogiva **Absinto-1**.
3. A quinta trombeta, em **São Lázaro**, parou no meio do sopro: a **meia nota**. O fim começou e não termina.
4. Estamos no **Ano 31 do Impasse** (os Arautos dizem "do Juízo Adiado"). A Rádio conta noites.
5. O **Amargo** é a radiação: pó verde que ainda cai, amarga a água, deforma quem bebe muito tempo. A Vigília mede
   com contadores; a Comunhão bebe como sacramento.
6. Os mortos levantaram para o Juízo e o Juízo não veio: são os **Não-Julgados**, com o lacre de cera no peito.
7. **Arautos do Juízo** (Anjo, Demônio, Cultista) querem que a nota termine. São o Coro (anjos), a Legião Blasfema
   (demônios) e a Comunhão do Amargo (cultistas). Aliança podre com motivo concreto: na Grande Batalha o Coro recuou
   e deixou a Legião morrer no campo; o general Andras sumiu; o Coro precisa dos demônios para descer à cripta e
   esconde isso; os demônios escondem que não têm general.
8. **Vigília** (Humano, Mutante, Tecnomancer) quer cancelar o fim. É a Cerca, os Engenheiros Hereges e os Sineiros.
9. O **Warlord** é mercenário: veio do cerco, lutou pela Vela por carne e pela Capela por água, e parou de escolher.
   Os dois lados o contratam e nenhum confia nele. Seu recurso é o Ódio.
10. São Lázaro está enterrada na areia até o 4º andar. "A rua de hoje é o telhado de ontem."
11. A sabedoria hermética (Thoth, a Tábua de Esmeralda, Atlântida, Amenti) é **verdade** dentro do mundo, não
    superstição. Cada lado a lê a seu modo: a Vigília mede (Iolanda mede pirâmides e Colunas), o Coro chama de heresia
    (Versículo do Sino 7), a Legião aposta contra, os atlantes acreditam.
12. Lemas: **"O fim começou. O fim não termina."** · Arautos: "Que a nota termine." · Vigília: "Enquanto houver
    vela, não é noite."

---

## 2. A regra das vozes (a mais importante)

**Nenhum texto do jogo é narrado por ninguém.** Todo texto tem **autor, lugar e lado**, e pode estar errado.
A verdade aparece quando o jogador cruza duas fontes. Contradição entre fontes é proposital.

| Voz | Quem | Onde | Como soa |
|---|---|---|---|
| Despacho da Vela | a Capitã Odete Ferrolho (assina "C. O. Ferrolho"); Anselmo nos técnicos, Gaspar na forja | missões da Vigília | militar, numerado, frases de uma linha |
| Versículo do Coro | Abdiel; Madre Ivone pela Comunhão; Malfas zomba no rodapé. Livros: do Sopro, da Retirada, das Acusações, da Comunhão, das Patentes, do Chamado, do Sino (Sinésia) | missões dos Arautos | escritura, segunda pessoa solene |
| Rádio São Lázaro | Isaura Valente | linha D, carregamento | boletim noturno, contagem de noites, "ouvinte", estática |
| Caderno do Coveiro | Simão | bestiário, cemitério | seco, sem data, de quem enterrou tudo |
| Crônica do Emparedado | Frei Anacleto | história do mundo, site | erudito, ouve o mundo pela parede |
| Bilhete de Corvina | Corvina | linha E | segredo à venda, com preço anotado |
| Caderno do Escriba | o Escriba | Jerusalém e Hermon | anota os nomes dos mortos, frases de profeta |
| Inscrição | ninguém sabe | itens, paredes, baús | uma linha só |

Voz nova só entra com dono, formato e tom definidos, e registrada nesta tabela.

**Errado:** `Os mortos-vivos infestam o cemitério. Elimine 6 deles para proteger o acampamento.`
**Certo:**
```
DESPACHO DA VELA · Nº 4 · ANO 31 DO IMPASSE
6 Não-Julgados parados entre o poste 11 e o 12 da cerca sul, turno do Damião. Não avançam. Não recuam.
O Damião não dorme desde terça. Derrube os 6 antes da troca de guarda.
— C. O. Ferrolho, Capitã da Cerca
```
(Um despacho faz conta e dá ordem, com um detalhe que só quem está lá sabe. Não faz retórica.)

---

## 3. Dez regras de tom

1. **Frase curta, seca.** Ninguém faz discurso, exceto o fanático, e o discurso dele é o retrato dele.
   - Errado: "A escuridão que assola estas terras há tanto tempo parece cada vez mais forte."
   - Certo: "A Vela pisca desde terça. Ninguém fala disso."
2. **Concreto, nunca abstrato.** Nomeie a coisa: carne, sebo, sino derretido, chumbo, cera, pá. Corte "trevas",
   "mal ancestral", "poder sombrio", "forças obscuras".
   - Errado: "Um mal antigo desperta."
   - Certo: "O sino do cemitério tocou sozinho. Ele não tem badalo desde 1962."
3. **O horror vem do cotidiano.** Uma mãe que deixa caldo no portão para o filho que virou bicho assusta mais que
   qualquer demônio de três metros.
4. **Humor de forca.** Gente cansada ri do que dói. O humor é seco e da situação, nunca piada de internet.
   - Certo: Mãe Cardo: "Não pergunte para quem é o caldo." / Malfas, em liturgia de demônio (por isso a ênclise):
     "Prometeram-nos a Terra. Ninguém disse que viria cheia de gente."
5. **Nenhum lado é bom.** A Vigília salva vidas e faz coisas horríveis para isso. Os Arautos são cruéis e
   sinceros. Todo vilão tem uma razão que, dita por ele, quase convence.
6. **O mundo é maior que o jogador.** Cite outras trombetas, outras frentes, gente que não voltou, cidades que
   ninguém vê. O jogador chega no meio da história, não no começo dela.
7. **Mostre, não explique.** Nunca "Como você sabe, o Impasse começou em 1962...". O personagem fala do que
   importa para ele hoje, e a história vem de lado.
8. **O jogador não é o escolhido.** É mais um par de mãos. O respeito se ganha: os NPCs reagem ao que ele fez
   (flags), não a profecias.
9. **Beleza no fim do mundo.** Toda área tem um momento de beleza: o vitral que ainda pega luz, a flor da Rute,
   o rio verde à noite. "Mesmo que seja fim do mundo, pode ser belo."
10. **Silêncio é ferramenta.** Deixe lacunas. Uma frase que não se completa ("Antes de o Joaquim...") vale mais que
    um parágrafo de explicação. O jogador que cruza fontes deve ser recompensado com sentido.
11. **Sem retórica automática.** Lista de três só quando a coisa tem três partes de verdade. Nada de anadiplose em
    cadeia ("X abre uma brecha. Uma brecha apaga a Vela."). Nada de aforismo de contracapa ("ninguém é bom", "o
    mundo é maior que você"): troque por um fato que mostre a mesma coisa.

---

## 4. Língua e forma

- **Português do Brasil**, culto mas falado. Tratamento padrão: "você". Os Arautos usam o solene ("tu", "vós",
  "irmão") quando liturgia; demônios zombam desse registro.
- **Cada voz tem vocabulário.** Vigília: ferramenta, número, ofício ("bobina", "cerca", "turno"). Arautos:
  liturgia ("Juízo", "pureza", "irmão", "nota"). Neutros: ofício próprio (coveiro fala de terra; Isaura de rádio).
- **Regionalismo com medida.** Um "Nhá", um "menino", um "freguês" dão lugar. Caipira de novela, não.
- **Travessão (—) só na assinatura** de documentos e citações. No resto, ponto e vírgula, ponto, vírgula.
- **Exclamação é rara.** Uma por fala no máximo, e só de quem grita de verdade (Irmã Sinésia, a Afinadora; o
  Ferrolhinho, moleque de recados da Vela; não a Capitã Odete Ferrolho, que nunca grita).
- **Rubrica de ação** em diálogo vai entre parênteses, curta, no presente: `(ele se senta na beira da cova)`.
- **Maiúsculas** só no cabeçalho do documento: `DESPACHO DA VELA · Nº 1 · ANO 31 DO IMPASSE`.
- **Números**: por extenso até dez em fala ("seis carniçais"); algarismo em documento militar ("Nº 4", "11.214 noites").
- **Nomes canônicos sempre** (seção 11). Nome novo: pronunciável em português, com eco bíblico, hermético ou de ofício.
- **Regras de nome.** Uma palavra descritiva ("de Cinza", "Brasa", "Filho de") em no máximo dois nomes por área.
  Nenhum nome que colida com facção ou instituição (Vigília, Coro, Sineiros, Cerca, Legião). Apelido de ofício
  (Graxa, Bigorna) só para quem já tem; gente nova recebe sobrenome de família (Ferraz, Prado, Valente). Chefe sem
  "X, o Y" de vez em quando, para os outros se destacarem. Nunca nome de criatura de obra alheia (Ent, orc, etc.).

---

## 5. Como escrever cada tipo de texto

### 5.1 Missão (`missoes.json`)
Cada missão é **um documento do mundo**, sem mudar objetivo, recompensa nem número.
1. **Papel** (1ª linha da `descricao`, maiúsculas): formato, número, data.
2. **O porquê grande**: ligue a tarefa pequena à guerra.
3. **A ordem**: curta, imperativa.
4. **Assinatura**: `— Nome, cargo`.
5. **`texto_conclusao`**: uma consequência e um fragmento de verdade; se der, algo que contradiz o NPC.
6. **`resumo`**: uma linha prática para o rastreador ("Mate 6 Não-Julgados na cerca sul"). Só aqui a linguagem
   de jogo é permitida.

Regra de ouro: **o objetivo de jogo é o pretexto, a razão no mundo é a missão.** "Colete 8 ossos" vira "Simão
precisa de oito fêmures para fechar a cova coletiva antes da maré de areia".

### 5.2 Diálogo de NPC (`dialogos.json`)
- **Primeira fala define a pessoa.** Ela está no meio de algo quando o jogador chega.
  - Certo: "Meio tom abaixo! Se eu afinar meio tom abaixo, a nota volta para dentro! Ah, é você."
- **Máximo de três frases por balão.** Se precisa de mais, é outro balão ou outra conversa.
- **Respostas do jogador** são curtas e são escolhas reais (de tom ou de lado), não "Entendi." / "Continue."
- **O NPC quer algo** em toda conversa, mesmo que seja só que o jogador vá embora.
- **Lembra do que o jogador fez.** Use flags: o NPC que viu o jogador matar Andras não fala igual ao que não viu.

### 5.3 Falas de ambiente (`falas_ambiente`)
Uma linha, ouvida de passagem. Mostra a rotina, não a trama. Pelo menos uma por NPC fala de outro NPC.
- Certo: "Se a Celina perguntar, eu não peguei vidro nenhum." (Ferrolho)

### 5.4 Item (`itens.json`)
- **Descrição técnica** (o que faz) fica separada da **`citacao`** (quem falou dele).
- A citação é **uma linha, assinada**, e conta de onde a coisa veio ou o que custou.
  - Errado: "Uma espada poderosa forjada com magia antiga."
  - Certo: `"Bala do sino grande da matriz. Trinta anos chamando para a missa; agora chama uma vez só." — Gaspar Bigorna`
- Item comum (poção, sucata) pode ter citação de humor; item de chefe tem citação de luto.
- Estilo FromSoftware: o item é um fragmento de história. Três itens do mesmo lugar contam juntos o que nenhum
  conta sozinho.

### 5.5 Bestiário (`registros` dos monstros)
Duas ou três entradas curtas, **cada uma de uma fonte** (Despacho, Versículo, Caderno do Coveiro, Escriba...).
As fontes discordam. O Caderno do Coveiro todos veem; o resto, cada facção vê a sua.
- Todo monstro tem **motivo** de estar ali (ecologia, ordem, maldição, fome). Nenhum é "inimigo genérico".

### 5.6 Chefe
Escreva o chefe como pessoa antes de escrever a luta. Ficha mínima, toda preenchida antes da primeira fala:
- **Quem era** antes do Juízo (ofício, nome, uma pessoa que amava).
- **O que quebrou** (o momento exato).
- **O que quer agora** (e por que, dito por ele, faz sentido).
- **O que deixa** ao morrer: a última fala, um item com citação, uma consequência no mundo (flag, NPC que reage).
- Andras, Irmã Celeste e Zacarias são o padrão. Andras: quem era (general da Legião), o que quebrou (o bonde o partiu
  ao meio e o Coro o deixou no campo), o que quer (cobrar da humanidade e dos anjos cada soldado), o que deixa (a
  dragona, a verdade de que o general vive). Celeste: desceu para cantar os mortos de volta ao sono, não parou, e os
  ossos repetem a canção; acha que todo vivo que desce veio acordar os filhos dela. Zacarias: trinta e um anos no
  escuro com a trombeta muda; concluiu que foi abandonado e quer julgar os dois lados.

### 5.7 Lugar (`locais.json`, áreas e subzonas)
Todo lugar responde a cinco perguntas: **o que era**, **o que aconteceu aqui**, **quem vive aqui agora**,
**o que se ouve e se cheira**, **qual o momento de beleza**. A descrição é escrita por uma voz (não pelo narrador).
Um lugar coeso tem um chão, uma paleta, um vocabulário de props, um céu e uma família de monstros.

### 5.8 Livro, diário, inscrição
- Livro tem autor, ano e motivo de ter sido escrito. Diário tem data e mão (letra tremida, manchas, páginas
  arrancadas: descreva entre colchetes `[página arrancada]`).
- Material hermético (Tábua de Esmeralda, Thoth, Amenti) é tratado como verdade antiga: tom grave, frases que
  parecem paradoxo e se revelam precisas. "O que está embaixo é como o que está em cima." Nunca ironize.
- Inscrição: uma linha. Se precisa de duas, é um livro.

### 5.9 Tela de carregamento (`citacoes.json`)
Uma ou duas frases, assinadas, com `faccao`. Devem funcionar sozinhas, sem contexto, e deixar uma pergunta.

### 5.10 Interface e sistema
Aqui a clareza vence a lore. Botões, erros e tutoriais falam a língua do jogo de forma direta e curta
("Inventário cheio.", "Pressione Z para o modo automático."). Dá para vestir com o mundo onde não atrapalha
("A Vela te espera." na tela de morte), nunca onde o jogador precisa entender uma regra.

### 5.11 Site e notícias
O site fala com quem **ainda não joga**. A abertura é a Crônica do Emparedado (`historia.md` §7.5). Notícias de
versão podem ser escritas como Despacho da Vela ou Boletim da Rádio, mas a lista de mudanças é sempre clara e
literal embaixo. Nunca prometa no site o que não está no jogo.

---

## 6. Como construir um NPC

Ficha de oito linhas (preencha antes de escrever uma fala):

| Campo | Pergunta |
|---|---|
| Ofício | O que fazia antes do Juízo? O ofício molda o vocabulário. |
| Ferida | O que o Impasse tirou dele? |
| Desejo | O que quer hoje, concreto? |
| Mentira | O que conta para si mesmo para continuar? |
| Segredo | O que esconde dos outros (e quem sabe)? |
| Laço | Com que outro NPC se liga (amor, dívida, ódio)? Ninguém vive sozinho. |
| Tique | Um jeito de falar ou um gesto que se repete ("menino", juros sobre conselho). |
| Lugar | Onde fica, o que faz ali quando ninguém olha, e por que não vai embora. |

Exemplo (existente, aprovado): **Mãe Cardo**. Ofício: cozinheira. Ferida: o Amargo levou o braço dela e o
filho inteiro. Desejo: alimentar todo mundo. Mentira: que o caldo do portão é para "os cães da rua". Segredo:
quem come é o Joaquim, que virou o Cão de Vala. Laço: o acampamento todo, que finge não saber. Tique: "menino".
Lugar: o caldeirão do tamanho de uma banheira.

**Mascote proibido.** Nenhum NPC existe só para dar serviço. O vendedor de poção tem uma história (Tobias é
órfão do cerco e acendia as velas da Vela).

---

## 7. Grandes obras e o que aprender de cada uma

Poucas, e cada uma com o lugar onde aparece no jogo. Roube a técnica, nunca nomes nem frases.

**Apocalipse de João e os livros sapienciais (Eclesiastes, Jó).** Paralelismo, imagem crua, pergunta sem resposta.
"E vi, e eis..." é a sintaxe dos Versículos do Coro. Onde: toda missão dos Arautos, o Livro das Acusações, os
Versículos do Sino em Atlântida.
- Como usar: duas orações coordenadas por "e", uma imagem física, nenhuma explicação. "E a árvore do furto ardeu por
  fora, e não morreu por dentro."

**Um Cântico para Leibowitz (Walter M. Miller Jr.).** Monges guardando ciência depois da bomba sem saber o que
guardam; o sagrado e o técnico misturados sem ironia. É o parente mais próximo do Impasse. Onde: Anselmo (padre que
vira engenheiro), os Engenheiros Hereges, a Biblioteca Soterrada, a Crônica do Emparedado.
- Como usar: um objeto técnico tratado com liturgia ("os contadores estalam como contas de terço").

**Os Sertões (Euclides da Cunha) e Vidas Secas (Graciliano Ramos).** O deserto brasileiro, o messianismo de Canudos,
a frase que economiza até doer. Onde: a Vigília inteira, a Mãe Cardo, Odete, o Deserto de Absinto.
- Como usar (Graciliano): corte o verbo de dizer e o adjetivo. "Fabiano, você é um homem" vira, aqui, "Perdi o olho
  esquerdo e o Teodoro. Anoto a metade que chegou."

**Trench Crusade e Warhammer 40.000.** Documento do mundo no lugar de narrador; instituições que falam; guerra sem
heróis. Onde: a regra das vozes (§2), os Despachos, os registros do bestiário.
- Como usar: antes de escrever, decida o papel (despacho, sermão, bilhete) e quem assina.

**Dark Souls e Bloodborne (FromSoftware).** O item conta a história; a arquitetura conta o resto; ninguém explica.
Onde: toda `citacao` de item, inscrições, a Cripta, Amenti.
- Como usar: três itens do mesmo lugar contam juntos o que nenhum conta sozinho.

**Tábua de Esmeralda e Corpus Hermeticum.** Sentença curta, correspondência ("como em cima, embaixo"), segredo que
se revela a quem está pronto. Onde: Thotme, as Colunas, a Esfinge, os Salões de Amenti.
- Como usar: tom grave, sem ironia, frase que parece paradoxo e se revela medida.

Leituras de apoio, só para quem já domina as de cima: Paraíso Perdido (o rebelde com argumentos melhores que o
trono, para escrever demônios), a Divina Comédia (cada círculo com sua lógica, para dungeons), Ficções de Borges
(livros apócrifos, para a Biblioteca), Auto da Compadecida (fé e riso juntos). De Planescape: Torment e Disco
Elysium rouba-se só a escolha de diálogo como posição moral, nunca a prosa longa.

---

## 8. O que não escrever

### 8.1 Proibido sempre
- **Violência sexual**, de qualquer forma, insinuada ou descrita.
- **Sofrimento infantil gráfico.** Crianças existem e sofrem no mundo (Nina, Ferrolho), mas o horror fica fora de
  cena e elas têm dignidade e agência.
- **Ódio a grupos reais**: nenhuma raça, etnia, nacionalidade, deficiência, gênero ou orientação é inferior,
  monstruosa ou piada. O Amargo deforma corpos; isso é tragédia, nunca deboche de quem é diferente.
- **Religiões reais como alvo.** O jogo usa mitologia cristã, judaica e egípcia como matéria épica. Os personagens
  fanáticos são do mundo do jogo; nunca caricaturar fiéis de hoje, denominações reais ou figuras sagradas para riso.
  Jerusalém e Egito: sem estereótipo de povo, sem orientalismo (exotismo, "nativos misteriosos"); os moradores
  têm ofício, família e humor como em São Lázaro.
- **Tragédias reais exploradas**: nada de Hiroshima, Holocausto ou atentados reais como piada, cenário ou
  referência. A bomba do jogo é a Absinto-1, ficcional.
- **Glorificar a bomba ou o suicídio.** A arma atômica é o pecado da Vigília, não o triunfo dela. Morte voluntária
  nunca aparece como solução bonita.
- **Política partidária, pessoas reais vivas, marcas, celebridades, memes, cultura pop.**
- **Conteúdo dos mistérios.** Soluções, pistas e recompensas dos mistérios são da thread "Biblioteca e mistérios"
  e não aparecem em nenhum outro texto, documento, commit ou conversa.

### 8.2 Fora do tom (cortar na revisão)
- **Linguagem de jogo dentro do mundo**: XP, quest, level, farmar, buff, drop, NPC, "clique". (Só no `resumo` e
  na interface.)
- **Gíria de hoje**: "tá ligado", "mano", "top", "de boa", "véi", "parça", "cringe".
- **Anacronismo**: celular, internet, carro, gasolina, gangue motorizada, "drone". O mundo parou em 1962 e
  enferrujou; a tecnologia é válvula, telégrafo, rádio, latão, vapor, bonde-veleiro.
- **Clichê de fantasia**: "escolhido", "profecia antiga", "mal ancestral", "trevas que assolam", "herói",
  "aventureiro", "reino", "taverna", "elfo", "masmorra" (diga cripta, catacumba, porão).
- **Exposição**: personagem que explica o que os dois já sabem; parágrafo de história no primeiro balão.
- **Narrador onisciente**: "Neste lugar sombrio, os mortos...". Sempre uma voz.
- **Maniqueísmo**: o lado do jogador sempre certo, o outro sempre burro.
- **Melodrama**: cascata de adjetivos, exclamações, "NÃÃÃO!", reticências em toda frase.
- **Humor de sitcom**: quebra da quarta parede, piada que pisca para o jogador.
- **Palavrão gratuito.** Pode haver um, de quem perdeu tudo, no momento certo. Nunca como tempero.
- **Tríade e anadiplose automáticas**: três itens por frase quando a coisa não tem três partes; frase que começa com
  o fim da anterior em cadeia. É a impressão digital de texto gerado.
- **Aforismo de contracapa**: frase bonita que serve para qualquer jogo ("o horror mora no cotidiano"). Troque pelo
  fato.
- **Inglês** onde existe palavra em português (exceto termos já canônicos, como Tecnomancer e Warlord).

### 8.3 Comunicação com o jogador fora do jogo
Notícias, changelog, avisos de manutenção e mensagens de suporte: claras, respeitosas, sem promessa de data que
não se controla, sem culpar o jogador, sem pressionar compra. O tom do mundo pode vestir o título, nunca esconder
a informação.

---

## 9. Coesão: como não contradizer o mundo

- **Antes de escrever, procure o nome** em `design/missoes/dados/*.json` e `historia.md` (`rg -n "Nome"`).
  Se já existe, use o que existe. Não crie conteúdo paralelo: estenda o JSON.
- **Datas e números fixos**: Juízo em 1962; Ano 31 do Impasse; 11.214 noites no início (a Rádio soma);
  trombetas 1-2 tocadas, 3ª = Absinto, 4ª escureceu um terço do sol, 5ª calada em São Lázaro, 6ª boato do Eufrates,
  7ª perdida.
- **Segredos têm dono.** Revelações (quem é Simão, de onde veio a Árvore-Mãe) só acontecem na missão que as
  revela. Antes disso, os textos podem insinuar, nunca contar.
- **Cada facção mente de um jeito.** A Vigília esconde a bomba. Os Arautos escondem que precisam dos demônios.
  Os demônios escondem que o general sumiu. Escreva cada fonte sabendo o que ela esconde.
- **Toda área nova** se liga a pelo menos uma trombeta, uma facção e um NPC de outra área.
- Depois de editar dados: `python3 design/missoes/validar.py`.

---

## 10. Checklist antes de entregar

- [ ] Quem está falando? Tem autor, lugar e lado?
- [ ] Algum nome está fora do cânone (seção 11)?
- [ ] Alguma frase passa de duas linhas sem motivo? Corte.
- [ ] Algum adjetivo abstrato ("sombrio", "antigo", "poderoso") pode virar uma coisa concreta?
- [ ] Algum termo de jogo, gíria ou anacronismo dentro do mundo?
- [ ] O texto explica o que devia mostrar?
- [ ] O NPC ou chefe quer algo? Tem uma razão que convence?
- [ ] Há uma lacuna para o jogador preencher e um fragmento de beleza ou de humor?
- [ ] Nada da seção 8.1?
- [ ] `validar.py` passou?

---

## 11. Nomes canônicos e erros comuns

| Certo | Errado |
|---|---|
| Legião Blasfema | Legião Rubra |
| Amargo (a radiação), Rio Amargo | radiação, veneno verde |
| Ano 31 do Impasse / do Juízo Adiado | ano 31, pós-apocalipse |
| a meia nota (a quinta trombeta calada) | a explosão, o evento |
| Não-Julgados | zumbis, mortos-vivos |
| Arautos do Juízo; Vigília | Luz/Trevas, bons/maus |
| Deserto de Absinto, Paróquia de São Lázaro | deserto radioativo genérico |
| Cripta da Trombeta Calada | masmorra |
| Acampamento da Vela; Capela de São Lázaro | base, cidade |
| bonde-veleiro | carro, moto, veículo |
| Andras, o General Partido; Irmã Celeste, a Carpideira; Zacarias, o Arauto da Trombeta Calada | nomes inventados para os chefes |
| Tecnomancer (a classe) | Tecnomante |
| Capitã Odete Ferrolho (assina C. O. Ferrolho) · Ferrolhinho (o moleque) | "Ferrolho" solto |
| Abatedouro Carniça; Porão do Abatedouro | Matadouro |
| Tronco Penitente; Badaleiro do Coro; Crispim Fel | Ent-de-Cinza; Sineiro do Coro; Bento Fel |

Mais nomes: `design/missoes/dados/npcs.json`, `locais.json`, `monstros.json`.
