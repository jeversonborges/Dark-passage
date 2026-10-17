"""NPCs, diálogos, missões, itens, objetos, monstros e subzonas da Atlântida, no formato de design/missoes/dados/.
Pedido do Jefin (16/10/2026): "quero npcs novos para Atlântida". Os arquivos de design/missoes são da thread de Missões:
este script NÃO os edita. Gera entregas/atlantida/conteudo_missoes.json (blocos para acrescentar em cada arquivo) e
confere tudo com o validar.py da thread, numa cópia temporária.  Uso: python3 conteudo.py
"""
import json, os, shutil, subprocess, sys, tempfile
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SAIDA = os.path.join(RAIZ, "entregas", "atlantida", "conteudo_missoes.json")

def fala(*vs): return [dict(v) if isinstance(v, dict) else {"texto": v} for v in vs]
def op(texto, ir=None, se=None, acoes=None):
    o = {"texto": texto}
    if ir: o["ir"] = ir
    if se: o["se"] = se
    if acoes: o["acoes"] = acoes
    return o

# ============================================================================ subzonas (área nova)
AREA = {"id": "atlantida", "nome": "Atlântida", "tipo": "area", "nivel": [30, 45],
        "descricao": "A Grande Planície de Atlântida, dobrada para baixo do mundo por Thoth na noite em que a ilha afundou e guardada "
                     "numa redoma que é o reflexo do céu. Dentro dela o sol está se pondo há onze mil anos. Só se entra pela Fenda.",
        "musica_sugerida": "harpa e lira desafinadas pelo tempo, coro grave muito ao longe, água correndo nos canais, sino de bronze batendo fora do tom",
        "subzonas": [
            {"id": "posto_da_fenda", "nome": "Posto da Fenda", "tipo": "base", "faccao": "vigilia", "seguro": True,
             "descricao": "Acampamento da Vigília logo depois do rasgo de luz: tendas, guindaste, a Arca do Primarca e a Coluna do Ritmo trincada.",
             "pontos": ["bancada_iolanda", "guarita_fenda", "carrinho_tobias", "arca_primarca_atlantida", "coluna_do_ritmo"]},
            {"id": "tenda_do_diapasao", "nome": "Tenda do Diapasão", "tipo": "base", "faccao": "arautos", "seguro": True,
             "descricao": "Acampamento dos Arautos fora do alcance do sino: tenda do Coro, braseiros brancos e um demônio da Legião que aposta contra.",
             "pontos": ["tenda_sinesia", "caixote_belzarim"]},
            {"id": "campos_duas_colheitas", "nome": "Campos de Duas Colheitas", "tipo": "caca", "nivel": [30, 32]},
            {"id": "canais_retos", "nome": "Os Canais Retos", "tipo": "caca", "nivel": [32, 35]},
            {"id": "olival_dos_parados", "nome": "Olival dos Parados", "tipo": "caca", "nivel": [34, 37], "pontos": ["rei_parado"]},
            {"id": "prados_dos_elefantes", "nome": "Prados dos Elefantes", "tipo": "caca", "nivel": [36, 39]},
            {"id": "salao_dos_registros", "nome": "Salão dos Registros", "tipo": "caca", "nivel": [38, 40], "pontos": ["tabua_de_esmeralda", "nicho_thotme"]},
            {"id": "cerco_da_coluna", "nome": "Cerco da Coluna", "tipo": "caca", "nivel": [38, 41]},
            {"id": "aneis_e_hipodromo", "nome": "Os Anéis e o Hipódromo", "tipo": "caca", "nivel": [40, 43]},
            {"id": "ilha_do_templo", "nome": "Ilha do Templo", "tipo": "caca", "nivel": [42, 45], "pontos": ["pilar_das_leis"]},
        ]}

# ============================================================================ NPCs
NPCS = [
    {"id": "iolanda_prumo", "nome": "Iolanda Prumo", "titulo": "Engenheira Herege, chefe do Posto da Fenda", "faccao": "vigilia",
     "classe_visual": "tecnomancer", "local": {"subzona": "posto_da_fenda", "ponto": "bancada_iolanda"}, "servicos": [], "dialogo": "dlg_iolanda",
     "aparencia": "Mulher de quarenta anos, alta e ossuda, avental de couro cheio de bolsos, óculos de solda com uma lente esmeralda que ela "
                  "mesma raspou de uma Coluna. Fio de prumo de latão no pescoço, no lugar de cruz. Giz nas unhas.",
     "personalidade": "Mede tudo antes de acreditar. Fala em números e em ferramentas, ri pouco e sempre na hora errada. Tem medo de uma coisa "
                      "só: de entender a Redoma e descobrir que não dá para copiar.",
     "historia": "Era desenhista de pontes da prefeitura de São Lázaro. Na noite da meia nota, a ponte que ela tinha calculado aguentou o "
                 "bonde da Odete e nenhuma outra aguentou. Anselmo a chamou para a Vela no dia seguinte. Foi a primeira dos Engenheiros "
                 "Hereges a passar a Fenda e a primeira a voltar. Escreveu na Coluna do Ritmo, a giz, a hora em que ela trincou. "
                 "Quer levar uma redoma para a Vela. Ainda não sabe o preço."},
    {"id": "cabo_nestor", "nome": "Nestor Calço", "titulo": "Cabo da Cerca, guarda da Fenda", "faccao": "vigilia",
     "classe_visual": "humano", "local": {"subzona": "posto_da_fenda", "ponto": "guarita_fenda"}, "servicos": [], "dialogo": "dlg_nestor",
     "aparencia": "Rapaz de vinte e poucos anos com sobretudo de cabo grande demais, escopeta de cano curto e um relógio de bolso parado "
                  "pendurado no peito como medalha. Queimadura de sol que não sai, num lugar onde o sol nunca se põe.",
     "personalidade": "Conversador, supersticioso, leal até a burrice. Conta histórias que ninguém pediu. Não dorme de costas para a Fenda.",
     "historia": "Era um dos catorze que passaram a Fenda com a Iolanda. Ficou de guarda na volta e nunca mais saiu. Diz que do lado de cá "
                 "o relógio parou às 17h40 e o coração dele também, e que é por isso que não envelhece. A Capitã Odete manda carta toda semana "
                 "mandando ele voltar. Ele responde que alguém tem de vigiar a porta dos dois lados."},
    {"id": "evemon_parado", "nome": "Evêmon, o Rei Parado", "titulo": "Um dos dez reis de Atlântida", "faccao": "neutro",
     "classe_visual": "humano", "visual_prop": "atlante_parado",
     "local": {"subzona": "olival_dos_parados", "ponto": "rei_parado"}, "servicos": [], "dialogo": "dlg_evemon",
     "aparencia": "Um dos Parados, mais alto que os outros, com o diadema de oricalco por baixo do pó. Os braços erguidos para o céu. "
                  "Quando alguém chega perto, os olhos se mexem; a boca, quase nada.",
     "personalidade": "Lento, solene, cansado de esperar. Fala uma frase por vez, como quem gasta um fôlego que precisa durar um século.",
     "historia": "Platão o lista entre os dez reis, filhos de Poseidon e de Clito (Crítias 114b). Estava no olival quando Thoth fechou a "
                 "Redoma e ficou parado no meio de uma oração. Viu o irmão Gadiro abrir a porta de baixo. Não contou a ninguém a tempo. "
                 "Respira uma vez por século e gasta o fôlego pedindo que alguém termine o que ele não terminou."},
    {"id": "thotme", "nome": "Thotme", "titulo": "Guardião do Grande Templo, pai de Thoth", "faccao": "neutro",
     "classe_visual": "humano", "local": {"subzona": "salao_dos_registros", "ponto": "nicho_thotme"}, "servicos": [], "dialogo": "dlg_thotme",
     "aparencia": "Velho sacerdote de linho branco e cabeça raspada, com o íbis bordado no peito. É transparente nas bordas, como uma figura "
                  "de vitral vista contra a luz, e a luz que passa por ele é verde. Não deixa sombra no chão.",
     "personalidade": "Gentil e terrível. Pergunta mais do que responde. Trata todo mundo como aluno e ninguém como filho.",
     "historia": "Na Tábua de Esmeralda, Thoth se diz filho de Thotme, guardião do grande templo. Quando Thoth fugiu para Khem levando os "
                 "registros, Thotme ficou para guardar as sete Colunas. Já não é bem um homem: é o que sobra de alguém que segura um céu de "
                 "pé por onze mil anos. Guarda o Livro do filho e só o entrega a quem terminar o que Gadiro começou."},
    {"id": "irma_sinesia", "nome": "Irmã Sinésia, a Afinadora", "titulo": "Corista do Coro, mestra do Diapasão", "faccao": "arautos",
     "classe_visual": "anjo", "local": {"subzona": "tenda_do_diapasao", "ponto": "tenda_sinesia"}, "servicos": [], "dialogo": "dlg_sinesia",
     "aparencia": "Anjo de asas cinzentas presas às costas com correias de couro para não abrirem. Sobretudo branco encardido, máscara de "
                  "gás de latão pendurada no pescoço e um diapasão de bronze do tamanho de um braço no cinto. Os ouvidos sangram um fio fino.",
     "personalidade": "Fanática, paciente, quase doce. Escuta antes de falar e fala como quem canta. Não perdoa nota errada.",
     "historia": "Cantou na quinta trombeta, em São Lázaro, e ouviu a nota parar no meio. Desde então ouve o resto da nota na cabeça, e "
                 "o resto não termina. Quando o Coro achou a ilha que disse não, Abdiel mandou o sino de bronze e mandou Sinésia junto. "
                 "Ela acredita que, quando a Coluna da Vibração cantar fora do tom, a nota de São Lázaro termina, e ela finalmente dorme."},
    {"id": "belzarim", "nome": "Belzarim, o Apostador", "titulo": "Tesoureiro da Legião Blasfema", "faccao": "arautos",
     "classe_visual": "demonio", "local": {"subzona": "tenda_do_diapasao", "ponto": "caixote_belzarim"}, "servicos": [], "dialogo": "dlg_belzarim",
     "aparencia": "Demônio baixo e gordo de chifres serrados, colete de veludo puído sobre a pele vermelha, óculos de um aro só e um "
                  "livro-caixa amarrado ao punho por uma corrente. Senta num caixote de munição como quem senta num trono.",
     "personalidade": "Simpático, venal, debochado. Zomba da liturgia do Coro na cara deles e anota tudo. Paga as dívidas, cobra em dobro.",
     "historia": "Contava as almas da Legião Blasfema antes de o general sumir. Sem general, contar almas virou contar apostas. Veio para "
                 "a Atlântida porque Malfas apostou que o sino não derruba a Coluna, e Belzarim é quem segura o dinheiro. Ajuda os Arautos "
                 "que pagam bem e ajuda o sino a falhar quando ninguém está olhando."},
]

# ============================================================================ itens
ITENS = [
    {"id": "engrenagem_oricalco", "nome": "Engrenagem de Oricalco", "tipo": "missao", "pilha": 20,
     "descricao": "Dente de engrenagem de um Vigia de Oricalco, ainda morno. Gira sozinho na palma da mão, devagar, para o mesmo lado.",
     "citacao": {"texto": "Isso não enferruja. Nada aqui enferruja. É isso que me dá medo.", "autor": "Iolanda Prumo"}},
    {"id": "pena_de_ibis_atl", "nome": "Pena de Íbis", "tipo": "missao", "pilha": 20,
     "descricao": "Pena branca de ponta preta. Escrevendo com ela, a tinta sai verde, e a letra sai certa mesmo de quem não sabe escrever.",
     "citacao": {"texto": "Os íbis são os escribas do meu filho. Cada pena é uma palavra que ele não teve tempo de dizer.", "autor": "Thotme"}},
    {"id": "sino_rachado", "nome": "Lasca do Diapasão", "tipo": "missao", "pilha": 10,
     "descricao": "Lasca de bronze de paróquia, do sino que o Coro bate contra a Coluna. Vibra quando alguém fala perto dela.",
     "citacao": {"texto": "Toda lasca que você me traz é uma nota que o sino não vai dar. Anote na minha conta.", "autor": "Belzarim"}},
    {"id": "livro_de_thoth", "nome": "O Livro de Thoth", "tipo": "missao", "pilha": 1, "chave": True,
     "descricao": "Um livro de lâminas finas de esmeralda presas por argolas de oricalco. As páginas estão em branco até alguém ler "
                  "em voz alta; aí a letra acende e diz outra coisa a cada vez. Thotme diz que é a chave de uma porta em Khem, "
                  "\"debaixo da casa que meu filho ergueu\".",
     "citacao": {"texto": "Quem lê isto não sai igual. Quem não lê não sai.", "autor": "Thotme"}},
]

# ============================================================================ objetos interativos
OBJETOS = [
    {"id": "coluna_do_ritmo", "nome": "Coluna do Ritmo (trincada)", "subzona": "posto_da_fenda", "quantidade_no_mapa": 1,
     "texto_ao_usar": "Você encosta o prumo de latão na trinca. O fio não para quieto: balança para fora e para dentro, sempre na mesma medida. "
                      "Do outro lado da trinca, bem longe, alguém responde com o mesmo balanço.",
     "visivel_se": {"missao_ativa": "at_v03"}},
    {"id": "tabua_de_esmeralda_obj", "nome": "A Tábua de Esmeralda", "subzona": "salao_dos_registros", "quantidade_no_mapa": 1,
     "texto_ao_usar": "Você passa a pena de íbis por cima das letras. Elas acendem uma por uma e uma voz de dentro da pedra lê junto com você: "
                      "\"o que está embaixo é como o que está em cima\". A última linha não acende. Embaixo dela, alguém raspou o nome de Gadiro.",
     "visivel_se": {"missao_ativa": "at_c02"}},
]

# ============================================================================ monstros (lore e drops de missão; números em atlantida/dados.json)
def mon(i, nome, tipo, niv, locais, desc, apar, comp, drops=(), regs=()):
    d = {"id": i, "nome": nome, "tipo": tipo, "nivel": niv, "locais": locais, "descricao": desc, "aparencia": apar, "comportamento": comp}
    if drops: d["drops_missao"] = [{"item": it, "chance": ch, "missao": ms} for (it, ch, ms) in drops]
    if regs: d["registros"] = [{"fonte": f, "titulo": t, "texto": x} for (f, t, x) in regs]
    return d
MONSTROS = [
    mon("touro_de_poseidon", "Touro de Poseidon", "normal", [30, 37], ["campos_duas_colheitas", "prados_dos_elefantes"],
        "Os touros soltos no santuário de Poseidon (Crítias 119d). Os reis os caçavam sem ferro, só com laço e bastão, para o sacrifício das leis.",
        "Touro enorme de pelo ruivo, chifres largos com pontas de oricalco, guirlanda seca no pescoço.", "Neutro. Pasta em dupla; investe se apanhar.",
        regs=[("despacho_vela", "Despacho nº 214", "Carne limpa. Repito: limpa. Primeira em 31 anos. Não matem mais do que a panela pede."),
              ("caderno_coveiro", "Página sem data", "Ninguém aqui é sacrificado faz onze mil anos. Os touros ainda esperam o laço.")]),
    mon("ibis_de_thoth_atl", "Íbis de Thoth", "normal", [30, 40], ["campos_duas_colheitas", "canais_retos", "salao_dos_registros"],
        "As aves sagradas de Thoth, o escriba dos deuses. Pescam nos canais e contam os passos de quem passa.",
        "Íbis branco de cabeça e pescoço pretos, bico longo e curvo, olho verde que acende quando encara.", "Neutro. Bando de dois; bica quem espanta.",
        drops=[("pena_de_ibis_atl", .6, "at_c02")]),
    mon("vigia_de_oricalco", "Vigia de Oricalco", "normal", [31, 43], ["canais_retos", "olival_dos_parados", "aneis_e_hipodromo"],
        "Autômatos que Thotme forjou para cuidar dos canais, das eclusas e dos rebanhos. Defendem-se e voltam ao trabalho.",
        "Figura de oricalco avermelhado e azinhavre, máscara de rosto sereno, engrenagens à mostra na cintura, ferramenta de canal na mão.",
        "Neutro. Trabalha em dupla; ignora quem não atrapalha.",
        drops=[("engrenagem_oricalco", .55, "at_v02")],
        regs=[("despacho_vela", "Despacho nº 213", "Não enferruja. Não cansa. Não responde. Anselmo quer um. Eu quero dez."),
              ("versiculo_coro", "Livro do Sino · 5", "E a ilha fez servos de metal para não precisar de anjos. E o metal obedeceu melhor.")]),
    mon("cinocefalo", "Cinocéfalo", "normal", [34, 40], ["olival_dos_parados", "salao_dos_registros"],
        "Os babuínos sagrados de Thoth, escribas e guardas do Salão dos Registros. Atiram pedras gravadas com sinais.",
        "Babuíno grande de juba prateada, focinho de cão, colar de contas de lápis-lazúli e uma tábua de escriba presa ao quadril.",
        "Neutro. Ataca de longe com pedras; foge para perto do Salão quando ferido."),
    mon("elefante_de_atlas", "Elefante de Atlas", "normal", [36, 39], ["prados_dos_elefantes"],
        "\"Havia na ilha grande número de elefantes\" (Crítias 114e). Bebem na lagoa e não gostam de susto.",
        "Elefante de presas curtas revestidas de bronze, manta de linho bordada já desbotada, poeira de oricalco nas rugas.",
        "Neutro. Lento; quando apanha, pisoteia em área."),
    mon("corista_do_cerco", "Corista do Cerco", "normal", [38, 41], ["cerco_da_coluna"],
        "Coristas do Coro trazidos para desafinar a Coluna da Vibração. Cantam a mesma nota até sangrar pelos ouvidos.",
        "Anjo magro de sobretudo branco encardido, boca costurada por cima da máscara, partitura amarrada no braço.", "Agressivo. Grupo de três.",
        drops=[("sino_rachado", .5, "at_a02")]),
    mon("sineiro_do_coro", "Sineiro do Coro", "normal", [38, 41], ["cerco_da_coluna"],
        "Querubins postos para tocar o Diapasão do Coro dia e noite contra a Coluna.",
        "Querubim de couro e latão com o martelo do sino nas costas, protetor de ouvido de ferro.", "Agressivo. Grupo de três.",
        drops=[("sino_rachado", .5, "at_a02")]),
    mon("hoplita_de_oricalco", "Hoplita de Oricalco", "normal", [40, 43], ["aneis_e_hipodromo"],
        "A guarda dos anéis que Thotme forjou; patrulha o hipódromo e o porto como se a ilha ainda tivesse rei.",
        "Vigia de oricalco com elmo de crista, escudo redondo com o tridente gravado e lança de bronze.", "Neutro. Dupla; firme e lento.",
        drops=[("engrenagem_oricalco", .55, "at_v02")]),
    mon("filho_da_serpente", "Filho da Serpente", "normal", [42, 45], ["ilha_do_templo"],
        "Os Irmãos da Escuridão que Gadiro chamou (Tábuas de Esmeralda): vestem forma de homem e só se mostram com cabeça de serpente.",
        "Homem alto de armadura de escamas negras e cabeça de serpente, olhos sem pálpebra, khopesh de bronze.", "Agressivo. Grupo de três.",
        regs=[("caderno_coveiro", "Página sem data", "Esses não são mortos nem vivos. São de baixo. Não cavo para eles.")]),
    mon("sacerdote_da_serpente", "Sacerdote da Serpente", "normal", [42, 45], ["ilha_do_templo"],
        "Rezam para alargar a Fenda e sair da Redoma. Guardam o caminho do Pilar das Leis.",
        "Irmão da Escuridão de manto de linho preto, máscara de rosto humano sobre a cabeça de serpente, cajado de serpente enrolada.",
        "Agressivo. Conjura de longe; grupo de três."),
    mon("touro_do_pilar", "O Touro do Pilar", "elite", [42, 42], ["aneis_e_hipodromo"],
        "O touro que os reis laçavam para o sacrifício das leis. Nunca foi caçado. Ainda corre o hipódromo, volta após volta.",
        "Touro branco imenso com os chifres dourados e as costas riscadas pelas leis do Pilar, escritas a sangue seco.",
        "Neutro. Corre a pista; quando apanha, carrega em linha reta."),
    dict(mon("gadiro", "Gadiro, o Rei Que Abriu a Porta", "chefe", [45, 45], ["ilha_do_templo"],
             "Gêmeo de Atlas e rei da ponta da ilha voltada para Gades (Crítias 114b). Abriu os portões de baixo e chamou os Irmãos da "
             "Escuridão. A Serpente que ele chamou se fundiu a ele, e ele está enrolado no Pilar das Leis há onze mil anos.",
             "Metade de cima um rei de barba trançada e coroa de oricalco; da cintura para baixo, uma serpente negra que dá três voltas no Pilar.",
             "Chefe de campo no Pilar das Leis. Fase 1 tridente e cauda; fase 2 chama os Irmãos; fase 3 o mar cai do céu."),
         conceito="Pedido do Jefin (15/10): Atlântida fiel a Platão e a Thoth; o rei que traiu a lei e chamou os de baixo."),
]

# ============================================================================ missões
def ms(i, titulo, tipo, faccao, nivel, doador, entrega, requer, resumo, descricao, objetivos, recomp, conclusao, **kw):
    d = {"id": i, "titulo": titulo, "tipo": tipo, "faccao": faccao, "nivel": nivel, "doador": doador, "entrega": entrega,
         "requer": requer, "resumo": resumo, "descricao": descricao.strip(), "objetivos": objetivos, "recompensas": recomp,
         "texto_conclusao": conclusao}
    d.update(kw); return d
def matar(a, q): return {"tipo": "matar", "alvo": a, "qtd": q}
def coletar(i, q): return {"tipo": "coletar", "item": i, "qtd": q}
def xp(n, ouro, **kw): return {"xp": n, "ouro": ouro, **kw}

MISSOES = [
    ms("at_v01", "Catorze Que Voltaram", "principal", "vigilia", 30, "iolanda_prumo", "iolanda_prumo", [],
       "Abasteça o Posto com carne dos Campos de Duas Colheitas e conte o que viu lá.",
       """DESPACHO DA VELA · Nº 213 · ANO 31 DO IMPASSE · POSTO DA FENDA
Passamos catorze. Voltaram catorze. Quero que continue assim.
O Posto come conserva de cão desde o deserto. Nos campos tem touro e tem íbis, e a carne é limpa.
Seis touros, seis íbis. Não mate os que não reagem: ainda não sabemos quem é dono deles.
— I. Prumo, Engenheiros Hereges""",
       [matar("touro_de_poseidon", 6), matar("ibis_de_thoth_atl", 6)], xp(52000, 900),
       "A primeira panela de carne limpa em trinta e um anos. O Posto comeu calado. O Nestor chorou e disse que foi a cebola. Não tinha cebola."),
    ms("at_v02", "Engrenagem Que Gira Sozinha", "principal", "vigilia", 33, "iolanda_prumo", "iolanda_prumo", ["at_v01"],
       "Traga engrenagens de oricalco dos Vigias e dos Hoplitas para a Iolanda estudar.",
       """DESPACHO DA VELA · Nº 216 · ANO 31 DO IMPASSE
Os de metal cuidam dos canais sem ninguém mandar. Quero saber o que manda neles.
Oito engrenagens. Os Vigias se defendem e voltam ao trabalho; não são inimigos. São fornecedores que ainda não sabem.
— I. Prumo""",
       [matar("vigia_de_oricalco", 8), coletar("engrenagem_oricalco", 8)], xp(68000, 1100),
       "Iolanda montou as oito engrenagens na bancada. Elas giraram sozinhas, devagar, todas para o mesmo lado: o lado da Coluna do Ritmo."),
    ms("at_v03", "A Medida da Trinca", "principal", "vigilia", 35, "iolanda_prumo", "iolanda_prumo", ["at_v02"],
       "Meça o balanço da Coluna do Ritmo com o prumo da Iolanda e veja o que o Coro está fazendo com a Coluna da Vibração.",
       """DESPACHO DA VELA · Nº 219 · ANO 31 DO IMPASSE
O fio de prumo não para quieto perto da trinca. Leve o meu e me diga a medida.
Depois vá olhar o Cerco. O Coro trouxe um sino de paróquia. Sino de paróquia derrubou a minha ponte uma vez. Não vai derrubar um céu.
— I. Prumo""",
       [{"tipo": "interagir", "objeto": "coluna_do_ritmo", "subzona": "posto_da_fenda", "qtd": 1},
        {"tipo": "explorar", "subzona": "cerco_da_coluna"}, matar("corista_do_cerco", 6)], xp(80000, 1300),
       "\"Para fora e para dentro, na mesma medida. Igual respiração.\" Iolanda escreveu a medida na Coluna, a giz, embaixo da hora "
       "em que ela trincou. Depois ficou um tempo calada e mandou você falar com o rei parado do olival."),
    ms("at_r01", "Ronda da Fenda", "repetivel", "vigilia", 31, "cabo_nestor", "cabo_nestor", ["at_v01"],
       "Limpe os arredores da Fenda para os que chegam do Éden.",
       """DESPACHO DA VELA · RONDA DA FENDA
Todo dia alguém atravessa achando que é o paraíso. Todo dia um touro discorda.
— Cabo N. Calço""",
       [matar("touro_de_poseidon", 8), matar("ibis_de_thoth_atl", 8)], xp(16000, 300),
       "Nestor riscou mais um dia num poste. Como aqui o dia não acaba, ele risca quando cansa.", repete="diaria"),
    ms("at_a01", "O Sino Não Desafina Sozinho", "principal", "arautos", 38, "irma_sinesia", "irma_sinesia", [],
       "Afaste os servos de metal da Coluna da Vibração para o Coro tocar em paz.",
       """VERSÍCULO DO CORO · LIVRO DO SINO · 3 · ANO 31 DO JUÍZO ADIADO
E os servos de metal vieram tirar o sino, e o sino não pôde cantar.
Vai tu, irmão, e cala o metal, para que a nota de São Lázaro encontre o seu fim.
— Sinésia, pelo Coro""",
       [matar("vigia_de_oricalco", 10), matar("cinocefalo", 6)], xp(90000, 1400),
       "Sinésia bateu o diapasão na palma da mão e escutou com os olhos fechados. \"Mais perto\", disse. \"Quase. Quase.\" O fio de sangue do ouvido dela engrossou."),
    ms("at_a02", "Aposta no Céu", "secundaria", "arautos", 40, "belzarim", "belzarim", ["at_a01"],
       "Belzarim quer lascas do Diapasão. Para quê, ele não diz.",
       """LIVRO-CAIXA DA LEGIÃO BLASFEMA · FOLHA 7
Malfas apostou que o sino não derruba a Coluna. Eu seguro o dinheiro. Quem segura o dinheiro decide o resultado.
Seis lascas do sino. Os coristas não vão gostar. Os coristas não precisam saber.
— Belzarim, tesoureiro""",
       [matar("sineiro_do_coro", 6), coletar("sino_rachado", 6)],
       xp(96000, 2400),
       "Belzarim pesou as lascas, anotou e guardou no colete. \"O sino agora soa meio tom abaixo. Ninguém no Coro tem ouvido para isso. "
       "Menos a Sinésia. Coitada.\""),
    ms("at_c01", "O Rei Que Respira", "principal", "ambas", 36, "evemon_parado", "thotme", [],
       "O Rei Parado gastou o fôlego de um século para mandar você ao Salão dos Registros.",
       """INSCRIÇÃO NO PEDESTAL DO REI PARADO · letra de antes de Atenas
Evêmon, filho de Poseidon e de Clito, quarto dos dez.
(embaixo, riscado com a unha, recente)
VÁ AO VELHO. ELE SABE O RESTO.""",
       [{"tipo": "falar", "npc": "thotme"}], xp(40000, 600), "Thotme olhou para você como se esperasse outra pessoa. \"Ele ainda respira? Então ainda dá tempo.\"",
       requer_qualquer=["at_v03", "at_a01"]),
    ms("at_c02", "Os Registros", "principal", "ambas", 39, "thotme", "thotme", ["at_c01"],
       "Junte penas de íbis e leia a Tábua de Esmeralda com elas, como Thotme mandou.",
       """DITO DE THOTME, GUARDIÃO DO GRANDE TEMPLO
A Tábua não se lê com os olhos. Lê-se com a pena do escriba.
Traz-me oito penas dos meus íbis, e passa uma delas por cima das letras.
O que acender, é teu. O que não acender, é de Gadiro.""",
       [coletar("pena_de_ibis_atl", 8), {"tipo": "interagir", "objeto": "tabua_de_esmeralda_obj", "subzona": "salao_dos_registros", "qtd": 1}],
       xp(110000, 1600),
       "A última linha da Tábua não acendeu. Thotme passou a mão transparente por cima do nome raspado. \"Meu filho escreveu tudo. "
       "Quem apagou o fim foi o rei que abriu a porta.\""),
    ms("at_c03", "O Que Estava Escrito Embaixo", "principal", "ambas", 43, "thotme", "thotme", ["at_c02"],
       "Abra caminho pela Ilha do Templo até o Pilar das Leis.",
       """DITO DE THOTME
Os Irmãos da Escuridão vestem forma de homem. Só se mostram com a cabeça de serpente quando acham que ninguém vê.
Eles tomaram o templo da minha ilha. Atravessa a ponte e não olhes para trás: atrás de ti, a ponte também é deles.""",
       [matar("filho_da_serpente", 12), matar("sacerdote_da_serpente", 8)], xp(150000, 2200),
       "No pé do Pilar das Leis, o sangue seco de onze mil anos formava uma letra só. G. Thotme fechou os olhos. \"Agora ele sabe que você vem.\""),
    ms("at_c04", "Num Só Dia e Numa Noite", "principal", "ambas", 45, "thotme", "thotme", ["at_c03"],
       "Derrote Gadiro, o Rei Que Abriu a Porta, no Pilar das Leis.",
       """DITO DE THOTME
Platão diz que a ilha afundou num só dia e numa noite terrível. Não diz por quê.
Foi por isto: um rei leu o que estava escrito embaixo da lei, e a lei não bastou.
Termina o que meu filho não pôde. Depois eu te dou o Livro, e tu saberás o que fazer com ele, ou não.""",
       [matar("gadiro", 1)], xp(240000, 6000, itens=[{"id": "livro_de_thoth", "qtd": 1}]),
       "Thotme pôs o Livro de Thoth nas suas mãos. As páginas estavam em branco. \"Leia em voz alta, um dia, debaixo da casa que meu "
       "filho ergueu em Khem. Não hoje.\" Pela primeira vez em onze mil anos, a Coluna do Ritmo parou de balançar por um instante.",
       ao_concluir_flag="tem_livro_de_thoth"),
]

# ============================================================================ diálogos
def dlg(i, npc, nos): return {"id": i, "npc": npc, "inicio": "raiz", "nos": nos}
DIALOGOS = [
    dlg("dlg_iolanda", "iolanda_prumo", {
        "raiz": {"fala": fala({"se": {"missao_concluida": "at_v03"}, "texto": "Medida anotada. Agora só falta entender. Isso costuma levar uma vida. A minha está acabando de tanto olhar para esta trinca."},
                              {"se": {"missao_disponivel": "at_v01"}, "texto": "Recruta da Fenda. Bem-vindo à única tarde de onze mil anos. Não toque nos parados, não beba água de fonte quente e não confie em nada que não enferruja."},
                              "Fala. Estou medindo."),
                 "opcoes": [op("Do que o Posto precisa?", "v01_oferta", {"missao_disponivel": "at_v01"}),
                            op("A carne chegou.", "v01_fim", {"missao_pronta": "at_v01"}),
                            op("Mais serviço?", "v02_oferta", {"missao_disponivel": "at_v02"}),
                            op("As engrenagens estão aqui.", "v02_fim", {"missao_pronta": "at_v02"}),
                            op("O que mais precisa medir?", "v03_oferta", {"missao_disponivel": "at_v03"}),
                            op("Medi a trinca e vi o sino.", "v03_fim", {"missao_pronta": "at_v03"}),
                            op("O que é este lugar?", "historia"), op("Até depois.")]},
        "v01_oferta": {"fala": "Seis touros, seis íbis. Carne para o Posto. Escolha os que estão longe da Fenda: os que estão perto já aprenderam a nossa cara.",
                       "opcoes": [op("Vou caçar.", acoes=[{"aceitar_missao": "at_v01"}]), op("Depois.")]},
        "v01_fim": {"fala": "Carne limpa. Vou escrever isso três vezes no despacho para a Odete acreditar.", "opcoes": [op("Bom apetite.", acoes=[{"concluir_missao": "at_v01"}])]},
        "v02_oferta": {"fala": "Os Vigias cuidam dos canais sem ninguém mandar. Quero uma engrenagem de cada. Oito. Eles se defendem, então leve curativo.",
                       "opcoes": [op("Trago as oito.", acoes=[{"aceitar_missao": "at_v02"}]), op("Depois.")]},
        "v02_fim": {"fala": "Olhe isso. Giram sozinhas. Todas para o mesmo lado. Para o lado da trinca.", "opcoes": [op("Isso é bom ou ruim?", acoes=[{"concluir_missao": "at_v02"}])]},
        "v03_oferta": {"fala": "Leve o meu prumo até a Coluna do Ritmo e me diga como ele balança. Depois vá ao Cerco ver o sino do Coro. Se der, faça os coristas cantarem mais baixo.",
                       "opcoes": [op("Vou medir.", acoes=[{"aceitar_missao": "at_v03"}]), op("Depois.")]},
        "v03_fim": {"fala": "Para fora e para dentro, na mesma medida. Respiração. Esta coluna respira, e a trinca é por onde ela tosse. Vá ver o rei parado no olival. Ele mexeu os olhos quando você passou ontem.",
                    "opcoes": [op("Vou.", acoes=[{"concluir_missao": "at_v03"}])]},
        "historia": {"fala": "Uma redoma que é o céu de cabeça para baixo. O Juízo desce, dá de cara com o próprio reflexo e volta. Thoth fez isso com sete colunas e uma frase. Eu tenho giz, cobre e o Anselmo. Me dá uns cem anos.",
                     "opcoes": [op("E se a gente fizer uma sobre a Vela?", "historia_2"), op("Voltar.", "raiz")]},
        "historia_2": {"fala": "Aí o Juízo desce na Vela, vê o próprio rosto e volta para cima de outro lugar. Alguém sempre paga a redoma. Até hoje ninguém me disse quem pagou esta.",
                       "opcoes": [op("Voltar.", "raiz")]},
    }),
    dlg("dlg_nestor", "cabo_nestor", {
        "raiz": {"fala": fala("Parado aí. Ah, é da Vigília. Desculpa. Aqui tudo que chega parece com alguma coisa que não é."),
                 "opcoes": [op("Ronda de hoje?", "r01_oferta", {"missao_disponivel": "at_r01"}),
                            op("Ronda feita.", "r01_fim", {"missao_pronta": "at_r01"}),
                            op("Por que seu relógio está parado?", "relogio"), op("Até mais, cabo.")]},
        "r01_oferta": {"fala": "Oito touros, oito íbis, perto da Fenda. Todo dia alguém atravessa achando que é o paraíso e todo dia um touro discorda.",
                       "opcoes": [op("Eu faço a ronda.", acoes=[{"aceitar_missao": "at_r01"}]), op("Hoje não.")]},
        "r01_fim": {"fala": "Fenda limpa. Vou riscar no poste. Aqui o dia não acaba, então eu risco quando canso.", "opcoes": [op("Descansa, cabo.", acoes=[{"concluir_missao": "at_r01"}])]},
        "relogio": {"fala": "Parou às 17h40 quando eu passei. O de todo mundo parou. O meu coração parou junto, eu acho, porque eu não envelheço. A Capitã manda carta mandando eu voltar. Eu volto quando a porta tiver alguém do outro lado também.",
                    "opcoes": [op("Voltar.", "raiz")]},
    }),
    dlg("dlg_evemon", "evemon_parado", {
        "raiz": {"fala": fala({"se": {"missao_concluida": "at_c04"}, "texto": "...meu irmão... calou?... então... posso... descer os braços..."},
                              "...você... respira... depressa..."),
                 "opcoes": [op("Quem é você?", "quem"),
                            op("Você me chamou?", "c01_oferta", {"missao_nao_iniciada": "at_c01"}),
                            op("(Esperar em silêncio.)")]},
        "quem": {"fala": "...Evêmon... quarto dos dez... filho de Clito... eu vi Gadiro... abrir a porta de baixo... não contei a tempo...",
                 "opcoes": [op("Voltar.", "raiz")]},
        "c01_oferta": {"fala": "...o velho... no salão dos registros... ele sabe o resto... vá... eu gastei o fôlego... do século...",
                       "opcoes": [op("Eu vou falar com ele.", acoes=[{"aceitar_missao": "at_c01"}]), op("Mais tarde.")]},
    }),
    dlg("dlg_thotme", "thotme", {
        "raiz": {"fala": fala({"se": {"missao_concluida": "at_c04"}, "texto": "O Livro está contigo. Não me perguntes o que há debaixo da casa do meu filho. Eu guardei a porta de cima. A de baixo nunca me deixaram ver."},
                              {"se": {"missao_pronta": "at_c01"}, "texto": "O rei parado mandou-te? Ele ainda respira? Então ainda dá tempo."},
                              "Aluno. Senta. Não, não há onde sentar. Fica de pé, então, e escuta."),
                 "opcoes": [op("O rei parado me mandou.", "c01_fim", {"missao_pronta": "at_c01"}),
                            op("O que eu preciso aprender?", "c02_oferta", {"missao_disponivel": "at_c02"}),
                            op("Li a Tábua com a pena.", "c02_fim", {"missao_pronta": "at_c02"}),
                            op("E agora?", "c03_oferta", {"missao_disponivel": "at_c03"}),
                            op("Cheguei ao Pilar.", "c03_fim", {"missao_pronta": "at_c03"}),
                            op("Estou pronto para Gadiro.", "c04_oferta", {"missao_disponivel": "at_c04"}),
                            op("Gadiro caiu.", "c04_fim", {"missao_pronta": "at_c04"}),
                            op("Seu filho vai voltar?", "volta", {"missao_concluida": "at_c04"}),
                            op("O que é Khem para Atlântida?", "khem", {"missao_concluida": "at_c02"}),
                            op("Quem é você?", "quem"), op("O que é a Redoma?", "redoma"), op("Adeus, mestre.")]},
        "c01_fim": {"fala": "Evêmon gastou um século para te mandar aqui. Não desperdices.", "opcoes": [op("Não vou.", acoes=[{"concluir_missao": "at_c01"}])]},
        "c02_oferta": {"fala": "A Tábua não se lê com os olhos. Traz-me oito penas dos meus íbis e passa uma delas sobre as letras. O que acender é teu.",
                       "opcoes": [op("Trarei as penas.", acoes=[{"aceitar_missao": "at_c02"}]), op("Depois.")]},
        "c02_fim": {"fala": "A última linha não acendeu. Meu filho escreveu o fim. Quem raspou foi o rei que abriu a porta.", "opcoes": [op("Gadiro.", acoes=[{"concluir_missao": "at_c02"}])]},
        "c03_oferta": {"fala": "Os Irmãos da Escuridão tomaram o templo. Atravessa a ponte e não olhes para trás: atrás de ti, a ponte também é deles.",
                       "opcoes": [op("Eu atravesso.", acoes=[{"aceitar_missao": "at_c03"}]), op("Depois.")]},
        "c03_fim": {"fala": "Uma letra no pé do Pilar. Agora ele sabe que vens.", "opcoes": [op("Que saiba.", acoes=[{"concluir_missao": "at_c03"}])]},
        "c04_oferta": {"fala": "Termina o que meu filho não pôde. Depois eu te dou o Livro. Saberás o que fazer com ele, ou não.",
                       "opcoes": [op("Vou ao Pilar.", acoes=[{"aceitar_missao": "at_c04"}]), op("Ainda não.")]},
        "c04_fim": {"fala": "Toma. O Livro de Thoth. Páginas em branco até alguém ler em voz alta debaixo da casa que meu filho ergueu em Khem. Não hoje.",
                    "opcoes": [op("Obrigado, mestre.", acoes=[{"concluir_missao": "at_c04"}, {"definir_flag": "tem_livro_de_thoth"}])]},
        "khem": {"fala": "Khem era a nossa colônia, a terra negra do outro lado do mar. Meu filho levou para lá os registros, os escribas e a ciência das colunas. "
                         "As pirâmides são redomas de pedra: pequenas, mas do mesmo princípio. Quando o vosso céu caiu e o vosso fogo subiu, "
                         "o Juízo bateu nas faces delas e encontrou só o próprio rosto. O fogo também. Khem dormiu debaixo da areia, mas não morreu.",
                 "opcoes": [op("Então o Egito foi salvo como Atlântida.", "khem_2"), op("Voltar.", "raiz")]},
        "khem_2": {"fala": "Salvo, não. Guardado. Salvo é quando acorda.", "opcoes": [op("Voltar.", "raiz")]},
        "volta": {"fala": "Ele já voltou. Pelas areias do tempo, pelo caminho de baixo de Khem, pelos salões onde não entra morto. "
                          "Por que achas que a Fenda abriu, que o vosso Éden floresceu, que a areia de Khem devolveu os templos? Não foi acaso. "
                          "O acaso é o nome da lei que não se conhece.",
                  "opcoes": [op("E o que ele quer?", "volta_2"), op("Voltar.", "raiz")]},
        "volta_2": {"fala": "O que quis da primeira vez: que o Juízo encontre só o próprio rosto e volte. Ele diz que pelo éter e pela luz tudo vai se "
                            "reconciliar, anjo com homem, demônio com anjo, e que não haverá mais guerra. Eu sou pai dele. Acredito. "
                            "Os do sino não acreditam. Os do caixote apostam contra. Desce e pergunta a ele tu mesmo.",
                    "opcoes": [op("Descer onde?", "volta_3"), op("Voltar.", "raiz")]},
        "volta_3": {"fala": "Debaixo da casa que ele ergueu em Khem. Entre as patas de quem pergunta. Leva o Livro. Responde certo.",
                    "opcoes": [op("Voltar.", "raiz")]},
        "quem": {"fala": "Thotme, guardião do grande templo. Meu filho chamou-se Thoth. Os gregos chamaram-no Hermes, o Três Vezes Grande. Ele foi para Khem com os registros. Eu fiquei com as colunas. Um de nós tinha de segurar o céu.",
                 "opcoes": [op("Voltar.", "raiz")]},
        "redoma": {"fala": "O que está embaixo é como o que está em cima. Meu filho dobrou a planície para baixo do mundo e pôs sobre ela o reflexo do céu. O Juízo desceu, encontrou só o próprio rosto e voltou. Isso foi o primeiro não. O vosso é o segundo.",
                   "opcoes": [op("Voltar.", "raiz")]},
    }),
    dlg("dlg_sinesia", "irma_sinesia", {
        "raiz": {"fala": fala({"se": {"faccao": "vigilia"}, "texto": "Uma vela. Que bonito. Apague-se longe do meu sino."},
                              "Irmão. Escuta. Não, não a mim. O sino. Escuta o que ele quase diz."),
                 "opcoes": [op("Como posso servir ao Coro?", "a01_oferta", {"missao_disponivel": "at_a01"}),
                            op("O metal está calado.", "a01_fim", {"missao_pronta": "at_a01"}),
                            op("Por que seus ouvidos sangram?", "ouvido"), op("Que a nota termine.")]},
        "a01_oferta": {"fala": "Os servos de metal vêm tirar o sino da Coluna. Os babuínos do escriba atiram pedras nos sineiros. Cala-os, irmão, para que a nota de São Lázaro encontre o fim.",
                       "opcoes": [op("Eu calo o metal.", acoes=[{"aceitar_missao": "at_a01"}]), op("Depois.")]},
        "a01_fim": {"fala": "Mais perto. Quase. Quase. Ouviste? Não? Tu não estavas lá na noite em que ela parou.", "opcoes": [op("Que a nota termine.", acoes=[{"concluir_missao": "at_a01"}])]},
        "ouvido": {"fala": "Eu cantei na quinta trombeta. A nota parou no meio, e o resto da nota ficou aqui dentro. Ela não termina. Quando a Coluna desafinar, a nota termina, e eu durmo.",
                   "opcoes": [op("Voltar.", "raiz")]},
    }),
    dlg("dlg_belzarim", "belzarim", {
        "raiz": {"fala": fala("Freguês! Senta. Não no caixote, que é meu. Quer apostar? Todo mundo aqui aposta, só que alguns apostam a alma."),
                 "opcoes": [op("Trabalho para a Legião?", "a02_oferta", {"missao_disponivel": "at_a02"}),
                            op("Trouxe as lascas do sino.", "a02_fim", {"missao_pronta": "at_a02"}),
                            op("Thoth diz que não haverá mais guerra.", "paz", {"missao_concluida": "at_c04"}),
                            op("Que aposta é essa?", "aposta"), op("Até mais, tesoureiro.")]},
        "paz": {"fala": "Paz! Que palavra cara. Anotei. Aposta aberta: dez mil almas que dura menos que a última. Quer entrar? Não? Pena. Você parece de quem acredita.",
                "opcoes": [op("Voltar.", "raiz")]},
        "a02_oferta": {"fala": "Seis lascas daquele sino. Os coristas não vão gostar. Os coristas não precisam saber. Eu pago em ouro, e ouro aqui dentro brilha mais, você reparou?",
                       "opcoes": [op("Fechado.", acoes=[{"aceitar_missao": "at_a02"}]), op("Não traio o Coro.")]},
        "a02_fim": {"fala": "Seis. Anotado. O sino agora soa meio tom abaixo. Ninguém no Coro tem ouvido para isso. Menos a Sinésia. Coitada.", "opcoes": [op("Pague.", acoes=[{"concluir_missao": "at_a02"}])]},
        "aposta": {"fala": "Malfas apostou que o sino não derruba a Coluna. O Abdiel apostou que derruba, só que ele não sabe que apostou. Eu seguro o dinheiro. Quem segura o dinheiro decide o resultado. Isso é teologia, freguês.",
                   "opcoes": [op("Voltar.", "raiz")]},
    }),
]


def gerar():
    out = {"_doc": "Conteúdo da Atlântida no formato de design/missoes/dados (thread de Missões é a dona desses arquivos). Cada bloco vai "
                   "acrescentado no arquivo de mesmo nome. Gerado e validado por design/mapas/atlantida/conteudo.py.",
           "locais.areas": [AREA], "npcs.npcs": NPCS, "dialogos.dialogos": DIALOGOS, "missoes.missoes": MISSOES, "itens.itens": ITENS,
           "objetos.objetos": OBJETOS, "monstros.monstros": MONSTROS}
    os.makedirs(os.path.dirname(SAIDA), exist_ok=True)
    json.dump(out, open(SAIDA, "w"), ensure_ascii=False, indent=1)
    # confere com o validar.py da thread de Missões numa cópia (nada em design/missoes é alterado)
    tmp = tempfile.mkdtemp()
    shutil.copytree(os.path.join(RAIZ, "design", "missoes"), os.path.join(tmp, "missoes"))
    os.makedirs(os.path.join(tmp, "mapas"), exist_ok=True)
    shutil.copy(os.path.join(RAIZ, "design", "mapas", "spots.json"), os.path.join(tmp, "mapas", "spots.json"))
    shutil.copytree(os.path.join(RAIZ, "design", "mapas", "mata_do_granizo"), os.path.join(tmp, "mapas", "mata_do_granizo"))
    D = os.path.join(tmp, "missoes", "dados")
    for chave, bloco in out.items():
        if chave.startswith("_"): continue
        arq, campo = chave.split(".")
        p = os.path.join(D, f"{arq}.json"); d = json.load(open(p, encoding="utf-8"))
        d[campo] = d[campo] + bloco
        json.dump(d, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    r = subprocess.run([sys.executable, os.path.join(tmp, "missoes", "validar.py")], capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-2000:])
    shutil.rmtree(tmp)
    print(len(NPCS), "NPCs,", len(MISSOES), "missões,", len(ITENS), "itens,", len(MONSTROS), "monstros")


if __name__ == "__main__":
    gerar()
