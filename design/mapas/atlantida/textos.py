"""Textos do mundo da Atlântida (objetos "leitura" do mapa). Regra das vozes (design/missoes/historia.md §7): todo texto
tem autor, data e lado; as fontes se contradizem de propósito. As frases da Tábua de Esmeralda são tradução livre do texto
tradicional; os sete princípios seguem a tradição hermética, em palavras próprias."""

def _t(nome, texto): return {"nome": nome, "texto": texto.strip()}

TEXTOS = {
    "despacho_da_vela": _t("Despacho da Vela nº 212", """
DESPACHO DA VELA Nº 212 · ANO 31 DO IMPASSE · POSTO DA FENDA

Passamos a Fenda com catorze. Voltaram catorze. Primeira vez que escrevo isso.
Aqui dentro o sol não termina de se pôr. Todos os relógios pararam às 17h40.
Água dos canais: limpa. Repito: limpa. Anselmo bebeu antes, como manda o regulamento dele.
Os bichos só atacam se apanharem. Os de metal também. Os de cabeça de cobra, não: esses atacam.
Os parados entre as oliveiras: não tocar, não raspar, não vender o pó. Um recruta raspou um. O parado piscou. O recruta pediu transferência.
Ninguém dorme perto da Coluna trincada.
Ordem: estudar as sete Colunas. Se isto segura um Juízo há onze mil anos, segura o nosso.

— Capitã Odete, pela Cerca.
(rodapé, letra do Anselmo) Quero uma dessas em cima da Vela. Mandem cobre.
"""),
    "radio_sao_lazaro": _t("Rádio São Lázaro · noite 11.229", """
TRANSMISSÃO DA RÁDIO SÃO LÁZARO · NOITE ONZE MIL DUZENTOS E VINTE E NOVE

Boa noite, ouvinte. A segunda estrela continua no silo. Contagem sem mudança.
Tem ouvinte pedindo para eu falar da luz verde da mata. Não é o Amargo, ouvinte. O Amargo é verde de doença. Essa é verde de vitral.
Do outro lado alguém transmite na mesma frequência que eu. Não é voz. É uma nota só, que sobe e desce a cada dezessete segundos, feito respiração.
Gravei. Toquei de trás para frente. É igual. O Frei Anacleto diz que o que está embaixo é como o que está em cima. Eu digo que é eco.
Ouvinte da Vigília que estiver lá dentro: se o sol de vocês não se põe, me mandem um pouco. Aqui faz frio.

Boa noite, ouvinte. Durma de bota.
— Isaura Valente, Rádio São Lázaro
"""),
    "tabua_de_esmeralda": _t("A Tábua de Esmeralda", """
A TÁBUA DE ESMERALDA · a letra acende quando alguém lê

É verdade, sem mentira, certo e muito verdadeiro:
o que está embaixo é como o que está em cima, e o que está em cima é como o que está embaixo, para fazer o milagre de uma coisa só.
E assim como todas as coisas vieram do Um, pela meditação do Um, todas nasceram dessa coisa única, por adaptação.
O Sol é o pai, a Lua é a mãe, o vento a carregou no ventre, a terra é a sua ama.
Separarás a terra do fogo, o sutil do espesso, docemente, com grande engenho.
Sobe da terra ao céu, desce de novo à terra, e recebe a força das coisas de cima e das de baixo.
Por isso fui chamado Três Vezes Grande.

(mais embaixo, outra mão, no mesmo verde)
Eu, Thoth, o Atlante, filho de Thotme, dobrei a planície para baixo do mundo. O Juízo desce; aqui encontra só o próprio rosto, e volta.
Guardem as sete. Se uma cantar fora do tom, a porta abre para os dois lados.
"""),
    "pilar_das_leis": _t("O Pilar das Leis", """
O PILAR DAS LEIS · oricalco, letra de antes de Atenas

Que nenhum rei pegue em armas contra outro rei.
Que, se um tentar derrubar a casa real, os outros nove se levantem.
Que os dez se reúnam a cada cinco anos e a cada seis, honrando o par e o ímpar.
Que o touro seja caçado sem ferro, só com laço e bastão, e que o seu sangue escorra sobre estas letras.
Que quem quebrar a lei beba desse sangue e se cale.

(embaixo, raspado com unha de escama)
EU LI O QUE ESTAVA ESCRITO EMBAIXO. — G.
"""),
    "versiculo_do_coro": _t("Versículo do Coro · Livro do Sino", """
VERSÍCULO DO CORO · LIVRO DO SINO · 2 · ANO 31 DO JUÍZO ADIADO

E acharam os servos uma ilha que disse não ao Senhor. E o Senhor desceu sobre ela, e ela se escondeu dentro do próprio reflexo.
E disse o Comandante: a nota que não terminou em São Lázaro terminará aqui.
Tocai o sino contra a coluna até que ela cante fora do tom. Quando a coluna cair, o Juízo entrará, e não haverá reflexo onde se esconder.
Que a nota termine.

(rodapé, letra de Malfas) Trouxeram um sino de paróquia para derrubar um céu. A Legião manda lembranças, e aposta no céu.
"""),
    "cronica_do_emparedado": _t("Crônica do Emparedado · cópia", """
DA CRÔNICA DO EMPAREDADO · cópia que a Vigília pregou no obelisco

Platão escreveu que Sólon ouviu dos sacerdotes de Saís: houve uma ilha além das Colunas de Hércules, maior que a Líbia e a Ásia juntas, e ela afundou num só dia e numa noite terrível.
Platão não sabia o resto. Houve um Juízo antes do nosso, pequeno, sobre uma ilha só. E alguém disse não.
Quem riscou a ilha dos livros foi o Coro. Quem a guardou foi um sacerdote que o Egito chamou de Thoth e os gregos de Hermes.
Se um Juízo foi recusado uma vez, pode ser recusado duas. É por isso que me emparedaram, e é por isso que escrevo com a unha.

— Frei Anacleto
"""),
    "caderno_do_coveiro": _t("Caderno do Coveiro · página solta", """
CADERNO DO COVEIRO · página sem data, achada numa ânfora do porto

Aqui ninguém morre, então ninguém me chama. Vim assim mesmo.
Os parados não precisam de cova. Precisam de alguém que espere com eles. Fiquei uma tarde. Aqui toda tarde é a mesma.
Já vi esta ilha de cima, antes. Não me pergunte quando.
"""),
    "despacho_da_volta": _t("Despacho da Vela nº 231", """
DESPACHO DA VELA Nº 231 · ANO 31 DO IMPASSE · POSTO DA FENDA

O velho do Salão diz que o filho voltou. Que o Egito era colônia daqui e que as pirâmides são redomas de pedra.
Que foi por isso que Khem não queimou: nem o Juízo de cima nem a nossa bomba de baixo acharam onde morder.
Que a Fenda, o Éden florescendo e os templos saindo da areia são a mesma coisa: ele voltando, pelo éter e pela luz.
Que no fim tudo se reconcilia e não haverá mais guerra.
Anotei tudo. Não acredito em metade. A outra metade explica coisas que eu não consigo explicar.
Ordem: mandar um engenheiro a Khem medir uma pirâmide. Se for redoma, quero a conta.

— I. Prumo, Engenheiros Hereges
(rodapé, letra da Capitã Odete) Reconciliar com quem? Com quem soltou a estrela? Com quem tocou a trombeta? Mantenham as escopetas carregadas.
"""),
    "versiculo_da_heresia": _t("Versículo do Coro · Livro do Sino · 7", """
VERSÍCULO DO CORO · LIVRO DO SINO · 7 · ANO 31 DO JUÍZO ADIADO

E levantou-se um escriba de antes do Dilúvio dizendo: eu voltei, e a minha ilha voltou, e a terra negra voltou, e o jardim voltou.
E disse: pelo éter e pela luz tudo será reconciliado, e não haverá mais guerra.
Ai de quem crê. A paz sem Juízo é o mesmo Impasse com outro nome.
Tocai o sino.

— Abdiel, pelo Coro
(rodapé, letra de Sinésia, tremida) E se ele estiver certo, a nota termina sem precisar cair a coluna?
"""),
}

# as sete Colunas de Hermes: o princípio gravado e o que cada lado escreveu embaixo
_COLUNAS = [
    ("mentalismo", "Coluna do Mentalismo", "O TODO é mente. O mundo é um pensamento dele.",
     "(giz da Vigília) Coluna mais firme das sete. Não vibra, não esquenta, não responde a nada. Responde a quem pensa nela. Não pensem nela. — Engenheiros Hereges, turma da Fenda"),
    ("correspondencia", "Coluna da Correspondência", "O que está embaixo é como o que está em cima; o que está em cima é como o que está embaixo.",
     "(giz da Vigília) A Redoma é o céu de cabeça para baixo. O Juízo desce e dá de cara com ele mesmo. Simples. Agora façam uma. — Anselmo"),
    ("vibracao", "Coluna da Vibração", "Nada está parado. Tudo se move. Tudo vibra.",
     "(cera de vela do Coro, por cima do giz) Tudo vibra. Inclusive o que cai."),
    ("polaridade", "Coluna da Polaridade", "Tudo é duplo. Os opostos são a mesma coisa em graus diferentes.",
     "(giz da Vigília) Calor e frio, sim e não, Juízo e Impasse: mesma régua. Isso explica as duas fontes da ilha. Não explica o resto. — Engenheiros Hereges"),
    ("ritmo", "Coluna do Ritmo (trincada)", "Tudo flui, para fora e para dentro. A medida da ida é a medida da volta.",
     "(giz da Vigília, ao longo da trinca) Trincou de alto a baixo na noite de 1962. Mesma hora em que calaram a quinta trombeta. A nota que não terminou lá terminou aqui, rachando isto. Por esta trinca é que entramos. Por ela é que alguma coisa vai sair."),
    ("causa_e_efeito", "Coluna de Causa e Efeito", "Toda causa tem seu efeito. O acaso é o nome que se dá à lei que não se conhece.",
     "(giz da Vigília) Ninguém aqui acredita em acaso desde que a Fenda abriu do lado da árvore que não morre."),
    ("genero", "Coluna do Gênero", "O gênero está em tudo. Tudo tem o princípio que gera e o que concebe.",
     "(riscado a faca) Os parados olham todos para esta. Não sei por quê. Não gosto."),
]
for cid, nome, principio, nota in _COLUNAS:
    TEXTOS[f"coluna_{cid}"] = _t(nome, f"{nome.upper()} · uma das sete que seguram a Redoma\n\n{principio}\n\n{nota}")
