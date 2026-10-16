"""Missões, NPCs, diálogos, itens, monstros, objetos, baús, lojas e locais do Egito (nível 50 a 70).
Formato: design/missoes/dados/*.json (só os acréscimos). Saída em entregas/egito/conteudo/.
Uso: python3 conteudo_egito.py   (confere com o validar.py da thread de Missões numa cópia temporária)

Linhas: K A Terra Negra (50-55) · H O Labirinto de Hawara (50-54) · L O Livro de Thoth (55-64) ·
V As Lâmpadas de Dendera (Vigília, 56-63) · A A Balança do Coro (Arautos, 56-63) · N O Coração Endurecido (60-66) ·
R diárias da escavação (50-70).
"""
import json, os, shutil, subprocess, sys, tempfile
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
SAIDA = os.path.join(AQUI, "conteudo")
sys.path.insert(0, os.path.join(RAIZ, "design", "mapas", "egito"))
from dados_egito import MOBS, MOBS_DUNGEON, CHEFES  # noqa: E402
import itens_egito as IE  # noqa: E402


def xp(n):   # ~10% de um nível (curva do jogo: 105n² + 525n)
    return int(round((105 * n * n + 525 * n) * 0.10, -2))


def ouro(n): return 30 * n


# ============================================================================ NPCs
NPCS = [
    dict(id="tuya_nomarca", nome="Tuya", titulo="Nomarca de Mênfis Reerguida", faccao=None, classe_visual="humano", local="menfis", ponto="praca",
         aparencia="Mulher de uns quarenta anos, alta, cabeça raspada sob um lenço de linho sujo de lodo, sobretudo de couro curtido sobre uma túnica plissada. No peito, um peitoral de contas de faiança remendado com arame; uma única conta turquesa ainda acende.",
         personalidade="Prática e cobradora. Fala como quem manda numa cidade que ela mesma desenterrou. Respeita quem cava e despreza quem só olha.",
         historia="A avó dela morava em Mit Rahina, em cima das ruínas de Mênfis. Quando o Nilo voltou e baixou, Tuya foi a primeira a cavar a casa da avó com as mãos e achou embaixo a casa de alguém de três mil anos atrás. Hoje toda Mênfis mora em dois andares: o de lama é de agora, o de pedra é de antes. Ela cobra dízimo de todo mundo que cava no planalto, porque 'a terra é preta e a terra é minha'.",
         falas_ambiente=["A rua de cima é nossa. A de baixo é dos avós.", "Quem cava paga. Quem não cava, carrega.", "O Nilo voltou. Agradeça a quem quiser, mas pague a mim."]),
    dict(id="hapu_mercador", nome="Hapu", titulo="Mercador das Docas", faccao=None, classe_visual="humano", local="menfis", ponto="mercado", servicos=["loja"], loja="loja_hapu",
         aparencia="Homem gordo de barba trançada, avental de couro cheio de bolsos, óculos de solda pendurados no pescoço. Vende de tudo numa banca coberta de papiro encerado.",
         personalidade="Simpático demais. Pechincha até com a própria sombra.",
         historia="Comprava e vendia antiguidade falsa para turista antes do Juízo. Agora vende antiguidade verdadeira para quem quiser e pão para quem precisa, e diz que o lucro é o mesmo.",
         falas_ambiente=["Escaravelho de verdade! Bom, quase.", "Pão de cevada, cerveja, mirra. O resto se discute."]),
    dict(id="nefer_aguadeira", nome="Nefer", titulo="a Aguadeira", faccao=None, classe_visual="humano", local="menfis", ponto="docas", servicos=["loja"], loja="loja_nefer",
         aparencia="Moça magra de uns vinte anos, cabelo trançado com fios de cobre, braços cobertos de cicatrizes de corda. Carrega dois potes de barro numa vara sobre os ombros.",
         personalidade="Rápida, desbocada, conhece cada fogueira da Terra Negra. Ri alto e conta o troco duas vezes.",
         historia="Filha de barqueiro. Quando a escavação cresceu, percebeu que ninguém levava água para quem fica o dia inteiro no spot. Hoje tem um carrinho em cada fogueira e um irmão diferente em cada um ('todos se chamam Nefer, é mais fácil').",
         falas_ambiente=["Água do Nilo fervida três vezes!", "Mirra boa fecha ferida e espanta mosca."]),
    dict(id="nefer_carrinho", nome="Nefer", titulo="Carrinho da Aguadeira", faccao=None, classe_visual="humano", local="escavacao", ponto="fogueiras", servicos=["loja"], loja="loja_carrinho_nefer",
         aparencia="Um dos 'irmãos' da Nefer, todos de trança com fio de cobre, empurrando um carrinho de potes de barro e unguentos.",
         personalidade="Rápido, cansado, sempre com troco.", historia="Leva água e mirra de fogueira em fogueira para quem caça nos spots.",
         falas_ambiente=["Água! Mirra! Cerveja ocre!"]),
    dict(id="besankh_ferreiro", nome="Besankh", titulo="Fundidor de Bronze", faccao=None, classe_visual="mutante", local="menfis", ponto="ferreiro", servicos=["ferreiro"],
         aparencia="Mutante enorme de pele cinza-esverdeada, um braço mais grosso que o outro, avental de couro queimado. Trabalha o bronze das estátuas derretidas num forno de tijolo de lama.",
         personalidade="Calado e caprichoso. Fala com o metal antes de bater.",
         historia="Era cantor de casamento em Gizé. O Amargo deixou o corpo dele largo e a voz rouca; ele trocou a música pelo martelo. Derrete estátuas sem cabeça, nunca as que ainda têm rosto.",
         falas_ambiente=["Bronze antigo é mole. Paciência.", "Esta tinha rosto. Esta eu não derreto."]),
    dict(id="ahmose_barqueiro", nome="Ahmose", titulo="Barqueiro das Docas de Mênfis", faccao=None, classe_visual="humano", local="menfis", ponto="docas",
         aparencia="Velho magro e queimado de sol, saiote de linho, chapéu de palha furado, remo comprido de madeira de acácia. Uma tatuagem do olho de Hórus no ombro.",
         personalidade="Fala devagar, como o rio. Sabe todas as histórias e não acredita em nenhuma.",
         historia="O avô dele dizia que crocodilo é o Nilo com fome. Ahmose atravessa a feluca da margem dos vivos para a margem dos mortos por três moedas e diz que é a mesma viagem que os faraós faziam, só que de volta.",
         falas_ambiente=["Três moedas para o outro lado.", "Do lado de lá enterram. Do lado de cá esquecem."]),
    dict(id="meritre_barqueira", nome="Meritre", titulo="Barqueira da Escavação", faccao=None, classe_visual="humano", local="escavacao", ponto="docas_escavacao",
         aparencia="Mulher forte de meia-idade, braços de remadora, véu de linho contra a areia, um amuleto de escaravelho no pescoço.",
         personalidade="Pouca conversa, muita pressa.", historia="Filha de Ahmose. Faz a volta da escavação para Mênfis e cobra o mesmo que o pai, mas rema mais rápido.",
         falas_ambiente=["Mênfis? Três moedas.", "Meu pai rema devagar porque gosta de falar."]),
    dict(id="reis_abdu", nome="Abdu", titulo="o Reis da Escavação", faccao=None, classe_visual="humano", local="escavacao", ponto="tenda_reis",
         aparencia="Homem baixo e largo, galabia listrada amarrada na cintura, bengala de capataz com ponta de latão, um caderno de contas preso no cinto por uma corrente.",
         personalidade="Capataz de escavação à moda antiga. Grita, conta, paga em dia. Leal a quem paga e só enquanto paga.",
         historia="A família dele foi 'reis' (capataz de escavação) por cinco gerações, desde os ingleses. Quando a areia desceu do planalto, ele já estava lá com cem homens e uma lista de preços. Vende braços para os quatro acampamentos e jura que não toma partido. Toma: o de quem paga mais.",
         falas_ambiente=["Quadrícula por quadrícula!", "Achou? Anota. Não achou? Cava.", "Os mortos trabalham de graça. Por isso estão me tirando os clientes."]),
    dict(id="djedi_mago", nome="Djedi", titulo="Mago da Casa de Hermes", faccao=None, classe_visual="cultista", local="escavacao", ponto="tenda_hermetista",
         aparencia="Velhíssimo, magro como um caniço, pele de papiro, barba branca até o cinto trançada com fios de ouro. Túnica de linho e um sobretudo de couro de hermetista coberto de símbolos costurados. Um olho de faiança no lugar do esquerdo, aceso em turquesa.",
         personalidade="Paciente, sorridente, infinitamente teimoso. Fala por enigmas e explica os enigmas. Come cem pães e bebe um jarro de cerveja por dia, como no papiro.",
         historia="O Papiro Westcar conta que o mago Djedi, de cento e dez anos, sabia o número das câmaras secretas do santuário de Thoth, que o rei Quéops procurava para a sua pirâmide. Este Djedi diz que é ele, e que tinha cento e dez anos quando o Juízo travou em 1962: não conseguiu fazer cento e onze. Procura o Salão dos Registros, onde Thoth guardou o que trouxe de Atlântida. (Segredo: ele sabe onde fica desde sempre. Espera alguém digno de entrar.)",
         falas_ambiente=["O que está embaixo é como o que está em cima.", "Cento e dez anos. Ainda.", "A Esfinge olha para o leste. O que ela guarda está a oeste."]),
    dict(id="diaprepes_atlante", nome="Diaprepes", titulo="Embaixador de Thotme", faccao=None, classe_visual="tecnomancer", local="escavacao", ponto="tenda_atlante",
         aparencia="Homem alto de pele cor de bronze e olhos verdes demais, túnica azul-mar sob uma armadura leve de oricalco riscada, um cristal esverdeado preso no peito que zune baixinho. Respira com uma máscara de filtro quando o vento traz areia.",
         personalidade="Educado, triste, deslocado. Pergunta tudo duas vezes, porque nada aqui funciona como em casa.",
         historia="Platão dá o nome Diaprepes a um dos dez reis de Atlântida. Este é descendente dele, embaixador da Redoma de Thotme, que atravessou a Fenda atrás do filho do seu guardião: Thoth, que fugiu para Khem há doze mil anos. Veio buscá-lo para segurar a Coluna do Ritmo, que trinca. Não sabe que Thoth subiu.",
         falas_ambiente=["Aqui o sol é preto. Lá embaixo nem sol temos.", "A Coluna trinca. Eu ouço daqui."]),
    dict(id="dalva_ferraz", nome="Dalva Ferraz", titulo="Engenheira Herege", faccao="vigilia", classe_visual="tecnomancer", local="escavacao", ponto="oficina_engenheiros",
         aparencia="Mulher de uns trinta e cinco anos, cabelo curto grisalho, macacão de lona cheio de bolsos, óculos de solda na testa, mãos pretas de graxa. Uma pilha de cobre e zinco presa no cinto, sempre faiscando.",
         personalidade="Rápida, entusiasmada, mal-educada sem querer. Desenha enquanto fala. Não acredita em deus nenhum e respeita todos os engenheiros, até os mortos.",
         historia="Engenheira Herege, discípula de Gustavo, o Primarca. Veio ao Egito atrás das Lâmpadas de Dendera: no templo de Hathor há um relevo com um bulbo, um filamento em forma de serpente e um pilar djed como isolador. 'Os antigos tinham luz sem fogo. Se eu achar a pilha, a Vela acende sem pavio.'",
         falas_ambiente=["Bulbo, filamento, isolador. Está desenhado na parede!", "Não é deus. É engenharia.", "Ninguém toca na minha pilha."]),
    dict(id="conego_barnabe", nome="Barnabé", titulo="Cônego do Coro", faccao="arautos", classe_visual="anjo", local="escavacao", ponto="tenda_coro",
         aparencia="Anjo de meia-idade, gordo, asas cinzentas cobertas de pó, batina roxa desbotada sob um sobretudo de couro com fivelas de latão. Carrega uma balança de bronze pequena presa ao cinto, que ele equilibra com os dedos quando pensa.",
         personalidade="Erudito, gentil, convicto até o fim. Fala baixo das coisas mais terríveis.",
         historia="O Coro o mandou ao Egito com uma tese: o Juízo travou porque alguém no mundo tem o coração endurecido contra Deus, como Faraó. Se o coração do Faraó Sem Nome for pesado na balança de Anúbis e cair, o Juízo destrava. Barnabé acredita nisso com o mesmo carinho com que acredita em tudo.",
         falas_ambiente=["Um coração, uma pena. É simples.", "Deus endureceu. Nós vamos amolecer.", "Tudo pesa. Até o que não deveria."]),
    dict(id="senebtisi_sacerdotisa", nome="Senebtisi", titulo="Sacerdotisa de Sobek", faccao=None, classe_visual="cultista", local="faium", ponto="crocodilopolis",
         aparencia="Mulher idosa de cabeça raspada, pele marcada de escamas desenhadas a carvão, manto de couro de crocodilo, braceletes de bronze com brincos de ouro pendurados.",
         personalidade="Serena e assustadora. Fala dos crocodilos como de filhos.",
         historia="Heródoto viu os sacerdotes de Crocodilópolis enfeitarem o crocodilo sagrado com brincos de ouro e pulseiras nas patas da frente. Senebtisi é a última dessa casa. Quando a cheia encheu o Labirinto de Hawara, Petsuchos ficou lá embaixo, e a fome dele cresceu com a água.",
         falas_ambiente=["Ele come. É isso que deuses fazem.", "Ouro na orelha, água na boca."]),
]

LOJAS = [
    {"id": "loja_hapu", "npc": "hapu_mercador", "nome": "Banca do Hapu", "itens": ["pao_de_cevada", "cerveja_ocre", "unguento_de_mirra"], "fala_ao_abrir": "Tudo do Nilo. Quase tudo."},
    {"id": "loja_nefer", "npc": "nefer_aguadeira", "nome": "Potes da Nefer", "itens": ["agua_do_nilo", "unguento_de_mirra", "cerveja_ocre"], "fala_ao_abrir": "Fervida três vezes. Paga uma."},
    {"id": "loja_carrinho_nefer", "npc": "nefer_carrinho", "nome": "Carrinho da Aguadeira", "itens": ["agua_do_nilo", "unguento_de_mirra"], "fala_ao_abrir": "Água! Mirra! Rápido que tem fila."},
]

# ============================================================================ itens
def consumivel(i, nome, efeito, preco, desc, cit=None):
    x = {"id": i, "nome": nome, "tipo": "consumivel", "pilha": 20, "efeito": efeito, "preco": preco, "descricao": desc}
    if cit: x["citacao"] = {"texto": cit[0], "autor": cit[1]}
    return x


def missao_item(i, nome, desc, cit=None):
    x = {"id": i, "nome": nome, "tipo": "missao", "pilha": 10, "descricao": desc}
    if cit: x["citacao"] = {"texto": cit[0], "autor": cit[1]}
    return x


def equip(i, nome, slot, nivel, attrs, efeito, desc, classe=None, dano=None, cit=None):
    x = {"id": i, "nome": nome, "tipo": "equipamento", "slot": slot, "raridade": "unico", "classe": classe, "nivel": nivel, "atributos": attrs,
         "efeito": efeito, "descricao": desc}
    if dano: x["dano"] = dano; x["atributos"] = {"dano": dano, **attrs}
    if cit: x["citacao"] = {"texto": cit[0], "autor": cit[1]}
    return x


ITENS = [
    consumivel("pao_de_cevada", "Pão de Cevada", {"cura_hp_pct": 12, "duracao_s": 10}, 40, "Pão achatado de cevada do Campo da Cheia, assado na pedra. Os operários de Gizé comiam isso. Os de agora também."),
    consumivel("agua_do_nilo", "Água do Nilo Fervida", {"cura_hp_pct": 8, "remove": "veneno"}, 60, "Água verde-escura do Nilo, fervida três vezes no pote da Nefer. Tira o gosto de veneno da boca e quase todo o resto.", ("Fervida três vezes. A quarta é por sua conta.", "Nefer, a Aguadeira")),
    consumivel("unguento_de_mirra", "Unguento de Mirra", {"cura_hp_pct": 35}, 160, "Mirra, mel e gordura de ganso num pote de alabastro, como nas receitas do Papiro Ebers. Fecha ferida e espanta mosca."),
    consumivel("cerveja_ocre", "Cerveja Ocre", {"cura_hp_pct": 15, "buff": {"vit": 12, "duracao_s": 300}}, 90, "Cerveja grossa de cevada tingida com ocre vermelho, como as sete mil jarras que salvaram a humanidade. Tem gosto de pão e de sangue.", ("Bebe. Se ela achar que é sangue, melhor ainda.", "Hapu, Mercador das Docas")),
    missao_item("pena_de_ibis", "Pena de Íbis", "Pena branca de ponta preta. Os escribas molhavam no ocre e escreviam com ela, em honra de Thoth."),
    missao_item("ostraco_de_faltas", "Óstraco de Faltas", "Caco de calcário com a lista de faltas dos operários da Vila, escrita em hierático. 'Hay: ausente, morto.' Desde o Ano 31 ninguém mais falta."),
    missao_item("brinco_de_petsuchos", "Brinco de Petsuchos", "Argola de ouro do tamanho de uma mão, ainda molhada, que os sacerdotes de Sobek penduravam na orelha do crocodilo sagrado.", ("Ouro na orelha, água na boca.", "Senebtisi, Sacerdotisa de Sobek")),
    missao_item("glifo_da_resposta", "Glifo da Resposta", "Uma placa de faiança turquesa com um glifo que muda quando ninguém está olhando. Caiu do peito da Esfinge de Hawara."),
    missao_item("ferrao_de_serket", "Ferrão de Serket", "O ferrão da deusa escorpião, do tamanho de um punhal. Uma gota na ponta mata; duas, dizem os sacerdotes, curam."),
    missao_item("fragmento_de_esmeralda", "Fragmento de Esmeralda", "Lasca de pedra verde translúcida com sinais gravados que não são egípcios. Os escorpiões do planalto carregam no ninho como se fosse ovo."),
    missao_item("glandula_de_naja", "Glândula de Naja", "Bolsa de veneno de naja num frasco de vidro. Dalva diz que o veneno conduz. Ninguém sabe o quê."),
    missao_item("pilar_djed_de_bronze", "Pilar Djed de Bronze", "Um pilar djed de bronze maciço, com quatro discos no alto e um fio de cobre enrolado no meio. 'É um isolador', diz Dalva. 'É a coluna de Osíris', diz qualquer egípcio."),
    missao_item("lampada_de_dendera", "Lâmpada de Dendera", "Um bulbo de vidro do tamanho de um braço com uma serpente de metal dentro, encaixado numa flor de lótus de bronze. Acende quando alguém mente perto dela."),
    missao_item("pena_de_maat", "Pena de Maat", "Pena de avestruz branca, a medida da verdade. Os guardiões de Hórus a usavam na coroa. Pesa exatamente o que um coração justo pesa."),
    missao_item("vaso_canopico_lacrado", "Vaso Canópico Lacrado", "Vaso de alabastro com tampa em forma de cabeça, ainda lacrado com cera e linho. Dentro, algo de alguém."),
    missao_item("coracao_do_farao", "Coração do Faraó", "Um coração de granito do tamanho de um punho, pesado como uma pedra de moinho. Bate uma vez por minuto.", ("Dez vezes eu disse não.", "o Faraó Sem Nome")),
    {"id": "leitura_estela_herodoto", "nome": "Estela do Viajante (Heródoto)", "tipo": "leitura", "texto": "Vi este labirinto, e é maior do que as palavras. Se alguém juntar todas as muralhas e obras dos gregos, verá que custaram menos trabalho e dinheiro do que este labirinto. Tem doze pátios cobertos, seis para o norte e seis para o sul, e três mil salas, metade debaixo da terra. As de cima eu vi. As de baixo os guardas não me deixaram ver: disseram que ali estão as tumbas dos reis que o construíram e dos crocodilos sagrados.\n— Heródoto de Halicarnasso, Histórias, livro II"},
    {"id": "leitura_rolo_magos", "nome": "Rolo dos Magos", "tipo": "leitura", "texto": "E os magos fizeram também o mesmo com os seus encantamentos: lançaram cada um o seu bastão, e tornaram-se serpentes. Mas o bastão de Arão tragou os bastões deles.\nE os magos fizeram assim com os seus encantamentos, para tirar piolhos, mas não puderam. Então disseram os magos a Faraó: Isto é o dedo de Deus.\n(na margem, em hierático e com outra tinta): nós não dissemos isso."},
    {"id": "leitura_confissao", "nome": "A Confissão Negativa", "tipo": "leitura", "texto": "Salve, ó tu de grandes passos, que vens de Heliópolis: eu não cometi iniquidade.\nSalve, ó tu que abraças a chama: eu não roubei.\nSalve, ó nariz, que vens de Hermópolis: eu não fui violento.\n...\nSalve, ó tu de coração endurecido...\n(a linha 42 foi raspada da parede com uma lâmina)"},
    # recompensas únicas (níveis 50-66)
    equip("anel_da_nomarca", "Anel da Nomarca", "anel", 52, {"vit": 22, "for": 14, "hp": 260}, "Dízimo: +8% de ouro dos monstros.", "O anel de sinete de Tuya, com o escaravelho da cidade gravado. Quem usa, cobra.", cit=("A terra é preta e a terra é minha.", "Tuya, Nomarca de Mênfis")),
    equip("colar_de_ouro_de_sobek", "Colar de Ouro de Sobek", "amuleto", 54, {"vit": 26, "esp": 14, "hp": 320}, "Fome do Deus: cada abate cura 2% da vida máxima.", "Colar de contas de ouro e cornalina tirado do pescoço de Petsuchos. Pesa como o deus pesava."),
    equip("sandalias_do_escriba", "Sandálias do Escriba", "botas", 57, {"agi": 20, "esp": 16, "defesa": 34}, "Passo de Thoth: +8% de velocidade de movimento fora de combate.", "Sandálias de papiro trançado de um escriba da Casa da Vida. Não fazem barulho em biblioteca nenhuma."),
    equip("olho_de_horus", "Olho de Hórus (wedjat)", "amuleto", 60, {"esp": 24, "vit": 18, "hp": 300}, "Olho que Cura: +12% de cura recebida.", "Amuleto de faiança turquesa com o olho de Hórus, que Thoth remendou pedaço por pedaço depois da luta com Seth. É inteiro porque foi quebrado."),
    equip("luvas_de_dalva", "Luvas Isolantes de Dalva", "luvas", 62, {"esp": 22, "agi": 14, "defesa": 40}, "Isolador Djed: -15% de dano elétrico e de raio recebido; torretas causam +8% de dano.", "Luvas de couro de crocodilo forradas de borracha de acácia, com fios de cobre costurados nas pontas dos dedos.", classe=None),
    equip("balanca_de_barnabe", "Balança de Barnabé", "segunda_mao", 62, {"esp": 26, "vit": 16, "hp": 260}, "Pesagem: ataques contra alvos com mais vida que você causam +8% de dano.", "A balança de bronze pequena que o Cônego equilibra nos dedos. Num prato, uma pena de verdade. No outro, nada, por enquanto."),
    equip("khopesh_de_ramesses", "Khopesh de Ramessés", "arma", 64, {"for": 30, "agi": 14}, "Corte em Gancho: o 3º golpe seguido em um alvo puxa-o 1 m para perto e causa +30% de dano.", "Espada-foice de bronze com o cartucho de Ramessés II, achada no colosso tombado da praça. A lâmina é curva como o rio.", dano=[118, 196]),
    equip("cetro_was_do_pesador", "Cetro Was do Pesador", "arma", 66, {"esp": 34, "vit": 14}, "Domínio: +10% de dano mágico; inimigos abaixo de 30% de vida recebem +12% de dano.", "O cetro de cabeça de chacal e ponta bifurcada que Anúbis segurava no Salão das Duas Verdades. Quem segura sente o peso de quem está na frente.", dano=[104, 182]),
]

ITENS += IE.todas_reliquias() + IE.itens_conjuntos()   # saque exclusivo dos chefes (lendario:<chefe>) e os dois conjuntos

# ============================================================================ objetos e baús (ids iguais aos que o gerar.py põe no mapa)
OBJETOS = [
    dict(id="marco_de_cheia", nome="Nilômetro de Mênfis", subzona="menfis", quantidade_no_mapa=1, texto_ao_usar="Uma escada de pedra que desce até a água, com marcas de cheia gravadas em cada degrau. A marca mais alta, de três mil anos, está seca. A de agora está dois degraus acima dela."),
    dict(id="selo_da_nomarca", nome="Estaca de Dízimo", subzona="campos_cheia", quantidade_no_mapa=3, texto_ao_usar="Uma estaca de acácia com uma placa de barro: o selo da Nomarca e o nome de quem cava este pedaço. Você aperta o selo novo no barro molhado.", visivel_se={"missao_ativa": ["k02"]}),
    dict(id="quadricula_da_escavacao", nome="Quadrícula da Escavação", subzona="gize", quantidade_no_mapa=3, texto_ao_usar="Um quadrado de cordas e estacas. Na peneira, cacos, ossos de peixe e uma conta de faiança turquesa que acende quando você sopra a areia.", visivel_se={"missao_ativa": ["k07"]}),
    dict(id="estela_do_sonho", nome="Estela do Sonho", subzona="gize", quantidade_no_mapa=1, texto_ao_usar="Entre as patas da Esfinge, a estela de granito de Tutmés IV: o príncipe dormiu à sombra da Esfinge, e ela prometeu que ele seria rei se tirasse a areia de cima dela. A areia saiu sozinha desta vez. Alguém riscou embaixo: 'E agora, quem vai ser rei?'"),
    dict(id="nicho_de_rolos", nome="Nicho de Rolos", subzona="casa_vida", quantidade_no_mapa=4, texto_ao_usar="Um nicho na parede com rolos de papiro em estojos de couro. A maioria virou pó. Um ainda abre: um catálogo da biblioteca, com uma linha riscada: 'Livro de Thoth: devolvido ao rio'.", visivel_se={"missao_ativa": ["l02"]}),
    dict(id="ka_de_setne", nome="O Ka de Setne Khamuas", subzona="casa_vida", quantidade_no_mapa=1, texto_ao_usar="Uma estátua de granito de um príncipe sentado com um rolo no colo. Quando você chega perto, os olhos de faiança acendem e uma voz cansada pergunta: 'Você também veio pelo Livro?'"),
    dict(id="camara_de_thoth", nome="A Pata da Esfinge", subzona="gize", quantidade_no_mapa=1, texto_ao_usar="Sob a pata direita da Esfinge, uma laje com um íbis gravado e uma ranhura do tamanho de uma lasca de esmeralda. A pedra está morna, como se alguém do outro lado tivesse acabado de encostar.", visivel_se={"missao_ativa": ["l05"]}),
    dict(id="coluna_do_ritmo_eco", nome="Cristal que Vibra", subzona="escavacao", quantidade_no_mapa=1, texto_ao_usar="Um cristal verde do tamanho de uma criança, preso num andaime atlante. Zune no ritmo de um coração. A cada três batidas, uma batida falha."),
    dict(id="relevo_de_dendera", nome="Relevo das Lâmpadas", subzona="karnak", quantidade_no_mapa=3, texto_ao_usar="Um relevo desbotado: um bulbo comprido saindo de uma flor de lótus, uma serpente ondulando dentro dele, e um pilar djed com braços segurando a ponta. Dalva ia gostar de ver isto.", visivel_se={"missao_ativa": ["v01"]}),
    dict(id="balanca_de_pedra", nome="Balança do Templo", subzona="karnak", quantidade_no_mapa=1, texto_ao_usar="Uma balança de granito do tamanho de um homem, com pratos de bronze verde. Num prato, uma pena de pedra. O outro está vazio e desce devagar quando você chega perto."),
    dict(id="oferenda_a_sobek", nome="Mesa de Oferenda de Sobek", subzona="faium", quantidade_no_mapa=1, texto_ao_usar="Uma mesa de pedra com marcas de dente na borda. Você deixa a carne que trouxe. Da água, algo grande sobe, olha e não come. Está esperando o deus comer primeiro."),
    dict(id="praga_de_sangue", nome="O Nilo Virando Sangue", subzona="margem_papiro", quantidade_no_mapa=3, texto_ao_usar="A água na margem está vermelha e grossa. Os peixes boiam de barriga para cima. Você enche o frasco de Djedi e a água continua vermelha dentro dele.", visivel_se={"missao_ativa": ["n01"]}),
    dict(id="porta_marcada", nome="Porta com Sangue no Lintel", subzona="menfis", quantidade_no_mapa=3, texto_ao_usar="Alguém passou sangue de cordeiro no lintel e nos dois umbrais desta porta, com um ramo de hissopo. A família lá dentro não abre. Você ouve alguém rezando em hebraico.", visivel_se={"missao_ativa": ["n02"]}),
    dict(id="cartucho_raspado", nome="Cartucho Raspado", subzona="vale_reis", quantidade_no_mapa=1, texto_ao_usar="Na porta da tumba, um cartucho real raspado a cinzel até a pedra ficar lisa. Os sacerdotes apagaram o nome. Mas a pedra lembra: quando você encosta a mão, ela bate, uma vez, como um coração."),
    dict(id="estela_herodoto", nome="Estela do Viajante", subzona="hawara_1", quantidade_no_mapa=1, texto_ao_usar="Uma estela grega no meio das egípcias, riscada por um viajante que esteve aqui há dois mil e quinhentos anos.", leitura="leitura_estela_herodoto"),
    dict(id="rolo_dos_magos", nome="Rolo dos Magos", subzona="coracao_2", quantidade_no_mapa=1, texto_ao_usar="Um rolo deixado aberto num banco de pedra, como se alguém tivesse parado de ler no meio.", leitura="leitura_rolo_magos"),
    dict(id="confissao_negativa", nome="A Confissão Negativa", subzona="coracao_5", quantidade_no_mapa=1, texto_ao_usar="Quarenta e dois juízes na parede, e embaixo de cada um a frase que o morto precisava dizer.", leitura="leitura_confissao"),
]
BAUS = [
    {"id": "bau_petsuchos", "nome": "Tesouro de Petsuchos", "subzona": "hawara_1", "tipo": "chefe", "tabela": "chefe_hawara_1", "texto_ao_abrir": "Brincos, pulseiras e ossos de cabra, tudo misturado no lodo."},
    {"id": "bau_esfinge", "nome": "Arca dos Doze Pátios", "subzona": "hawara_2", "tipo": "chefe", "tabela": "chefe_hawara_2", "texto_ao_abrir": "A tampa tem doze glifos. Abre com qualquer um."},
    {"id": "bau_serket", "nome": "Sarcófago de Amenemés", "subzona": "hawara_3", "tipo": "chefe", "tabela": "chefe_hawara_3", "texto_ao_abrir": "O rei não está aqui. O tesouro está."},
] + [{"id": f"bau_{c}", "nome": f"Oferendas de {CHEFES[c]['nome'].split(',')[0]}", "subzona": f"coracao_{n + 1}", "tipo": "chefe", "tabela": CHEFES[c]["drop"], "loot_de_grupo": True,
      "texto_ao_abrir": "Cada um do grupo acha a sua parte, como se a tumba soubesse quantos vieram."}
     for n, c in enumerate(("sekhmet", "janes", "imseti", "apofis", "anubis_pesador", "farao_sem_nome"))]

# ============================================================================ missões
MISSOES = []


def q(i, titulo, nivel, doador, objetivos, resumo, descricao, conclusao, oferta, fim, requer=(), faccao="ambas", itens=(), entrega=None, extra=None, mult=1.0):
    x = {"id": i, "titulo": titulo, "tipo": "principal" if i[0] in "kln" else ("faccao" if i[0] in "va" else ("dungeon" if i[0] == "h" else "repetivel")),
         "faccao": faccao, "nivel": nivel, "doador": doador, "entrega": entrega or doador, "requer": list(requer), "resumo": resumo,
         "descricao": descricao, "objetivos": objetivos, "recompensas": {"xp": int(xp(nivel) * mult), "ouro": int(ouro(nivel) * mult),
                                                                          "itens": [{"id": a, "qtd": b} for a, b in itens]},
         "texto_conclusao": conclusao, "_oferta": oferta, "_fim": fim}
    if extra: x.update(extra)
    MISSOES.append(x)


M = lambda alvo, n: {"tipo": "matar", "alvo": alvo, "qtd": n}
C = lambda item, n: {"tipo": "coletar", "item": item, "qtd": n}
I = lambda obj, sub, n=1: {"tipo": "interagir", "objeto": obj, "subzona": sub, "qtd": n}
E = lambda sub: {"tipo": "explorar", "subzona": sub}
F = lambda npc: {"tipo": "falar", "npc": npc}
S = lambda spot, n: {"tipo": "farmar_spot", "spot": spot, "qtd": n}

# ---- K: A Terra Negra
q("k01", "A Terra Negra", 50, "tuya_nomarca", [I("marco_de_cheia", "menfis"), F("ahmose_barqueiro")],
  "Veja o nilômetro e fale com o barqueiro Ahmose.",
  "SELO DA NOMARCA · MÊNFIS REERGUIDA · ANO 31\nForasteiro: aqui a terra é preta e a terra é minha.\nDesça o nilômetro nas docas e veja onde a água chegou. Depois fale com Ahmose, o barqueiro: quem quer cavar do lado dos mortos atravessa com ele.\n— Tuya, Nomarca",
  "O nilômetro mostrou dois degraus acima da cheia mais alta de três mil anos. Ahmose olhou a marca e cuspiu no rio, por respeito.",
  "Chegou pela Linha 7? Então chegou com fome e sem saber onde pisa. O Nilo voltou, forasteiro. Desça o nilômetro e veja até onde. Depois procure Ahmose nas docas.",
  "Viu a marca? Dois degraus acima dos avós. Bem-vindo à Terra Negra.", itens=[("pao_de_cevada", 10), ("agua_do_nilo", 5)])
q("k02", "O Dízimo da Nomarca", 51, "tuya_nomarca", [I("selo_da_nomarca", "campos_cheia", 3), M("crocodilo_do_nilo", 8)],
  "Sele as três estacas de dízimo e afaste os crocodilos dos campos.",
  "SELO DA NOMARCA · COBRANÇA\nTrês estacas nos Campos da Cheia estão sem o meu selo. Aperte o selo no barro de cada uma.\nE os crocodilos subiram do juncal para tomar sol na lavoura. Oito deles. Eles não pagam dízimo.\n— Tuya",
  "Tuya contou os selos duas vezes e as cabeças de crocodilo três. 'Agora sim. Terra paga, terra limpa.'",
  "Tem gente cavando nos meus campos sem selo. E tem crocodilo deitado no meu linho. Resolva os dois.", "Três selos. Oito crocodilos. Você sabe contar, gosto disso.",
  requer=["k01"], itens=[("unguento_de_mirra", 5)])
q("k03", "O Juncal do Papiro", 50, "nefer_aguadeira", [S("juncal_do_papiro", 12), C("pena_de_ibis", 6)],
  "Cace no Juncal do Papiro e traga penas de íbis.",
  "RECADO DA NEFER (riscado num caco)\nO juncal tá cheio de bicho e os escribas da Escavação pagam bem por pena de íbis. Seis penas. Cuidado que íbis bica e crocodilo morde.\n— N.",
  "Nefer cheirou as penas, separou a mais bonita para o cabelo e pagou o resto com água e uma piscadela.",
  "Pena de íbis vale mais que água, acredita? Os escribas molham no ocre e escrevem. Me traz seis.", "Seis penas! Uma é minha.", requer=["k01"], itens=[("agua_do_nilo", 8)])
q("k04", "Os Campos que Voltaram", 52, "tuya_nomarca", [S("campos_da_cheia", 12), M("escaravelho_sagrado", 10)],
  "Limpe os Campos da Cheia dos escaravelhos que rolam o lodo.",
  "SELO DA NOMARCA · LAVOURA\nOs escaravelhos estão rolando o meu lodo em bolas e levando para o deserto. Dizem que é sagrado. Eu digo que é meu.\nDez deles. E fique no campo até ele ficar quieto.\n— Tuya",
  "Os campos ficaram quietos. Um velho lavrador fez o sinal de Khepri e não olhou para você.",
  "Khepri rola o sol, eles dizem. Esses aí estão rolando a minha lavoura.", "Dez escaravelhos. Os velhos vão rezar por eles. Eu vou plantar.", requer=["k02"])
q("k05", "Do Outro Lado do Rio", 52, "ahmose_barqueiro", [E("escavacao"), F("reis_abdu")],
  "Atravesse para a Escavação e procure o Reis Abdu.",
  "Ahmose falou devagar, como o rio: 'Do lado de lá enterravam. Do lado de cá esqueciam. Atravesse e procure o Abdu, o reis da escavação. Ele vende braços para os quatro acampamentos e jura que não toma partido.'",
  "Abdu anotou o seu nome no caderno, embaixo de uma lista de mortos que voltaram ao trabalho.",
  "Quer cavar? Então vai para o lado dos mortos. Três moedas na feluca, ou vai a pé pela ponte. Procure o Abdu.", None, requer=["k01"], entrega="reis_abdu")
q("k06", "Os Quatro Acampamentos", 53, "reis_abdu", [F("djedi_mago"), F("diaprepes_atlante"), F("dalva_ferraz"), F("conego_barnabe")],
  "Apresente-se aos quatro acampamentos da Escavação.",
  "CADERNO DO REIS · FOLHA DO DIA\nQuatro acampamentos, um buraco. O velho Djedi, da Casa de Hermes. O atlante, que respira por máscara. A engenheira da Vigília. O cônego do Coro.\nVá dizer bom-dia a cada um. Depois volte e me diga quem paga mais.\n— Abdu",
  "Abdu ouviu os quatro nomes e escreveu um número ao lado de cada um. Não mostrou os números.",
  "Quatro acampamentos e todos querem o mesmo buraco. Vai conhecer os quatro. Quem sabe você descobre o que eles procuram, porque para mim não contam.", "E então? Quem paga mais? Não responda, eu já sei.", requer=["k05"])
q("k07", "A Quadrícula", 53, "reis_abdu", [I("quadricula_da_escavacao", "gize", 3), M("mumia_operaria", 8)],
  "Peneire as três quadrículas e afaste as múmias operárias.",
  "CADERNO DO REIS · TURNO\nTrês quadrículas no planalto para peneirar. E as múmias da Vila desceram de novo para 'trabalhar'. Elas cavam errado e não pagam.\nOito delas para o chão. As quadrículas para a peneira.\n— Abdu",
  "Na peneira, três contas de faiança acesas. Abdu guardou duas e deu uma para você 'pela sorte'.",
  "Os mortos estão me tirando os clientes. Cavam de graça, cavam errado. Me ajude a cavar direito.", "Três quadrículas, oito mortos. Isso sim é um turno.", requer=["k06"], itens=[("unguento_de_mirra", 5)])
q("k08", "Turno da Noite em Deir el-Medina", 54, "reis_abdu", [S("vila_dos_artesaos", 20), C("ostraco_de_faltas", 4)],
  "Cace na Vila dos Artesãos e traga os óstracos de faltas.",
  "CADERNO DO REIS · AVISO\nOs operários mortos da Vila ainda carregam as listas de faltas, escritas em caco. Quero ver. Se os mortos têm escala de turno, eu quero copiar.\n— Abdu",
  "Abdu leu os cacos com os óculos na ponta do nariz. 'Hay: ausente, morto. Ano 31: Hay voltou.' Ele riu, e depois não riu.",
  "Os mortos da Vila têm turno, acredita? Lista de faltas e tudo. Traga as listas.", "Quatro cacos. Olha isto: nenhum falta desde o Ano 31.", requer=["k07"], itens=[("anel_da_nomarca", 1)])
q("k09", "A Avenida de Amon", 55, "tuya_nomarca", [E("avenida_esfinges"), M("esfinge_carneiro", 6)],
  "Abra caminho pela Avenida das Esfinges até Karnak.",
  "SELO DA NOMARCA · ESTRADA\nA avenida das esfinges de carneiro liga Mênfis ao templo de Amon. Elas acordaram com a trombeta e não deixam ninguém andar fora da calçada.\nSeis estão de cabeça virada para a estrada. Ponha-as de volta no lugar, ou no chão.\n— Tuya",
  "As esfinges que sobraram olham para a calçada de novo. Tuya mandou varrer as pegadas.",
  "Eu preciso da estrada para Karnak. As esfinges acham que ela é delas.", "A estrada é minha de novo. As esfinges vão se acostumar.", requer=["k04"])

# ---- H: O Labirinto de Hawara
q("h01", "Os Crocodilos de Ouro", 50, "senebtisi_sacerdotisa", [E("faium"), I("oferenda_a_sobek", "faium")],
  "Vá ao Faium e deixe uma oferenda na mesa de Sobek.",
  "Senebtisi falou sem abrir os olhos: 'Heródoto viu os crocodilos de ouro. Eu os alimentei. O maior está no Labirinto, embaixo da água. Leve carne à mesa de Sobek, no lago. Veja se ele ainda come.'",
  "Algo grande subiu da água, olhou a carne e afundou de novo. Senebtisi suspirou: 'Não come mais oferenda. Agora ele quer o que respira.'",
  "Você vai descer ao Labirinto? Então primeiro alimente o deus. Se ele comer, talvez não coma você.", "Ele não comeu. Então ele está com fome de outra coisa.", requer=["k01"])
q("h02", "O Deus que Come", 51, "senebtisi_sacerdotisa", [M("petsuchos", 1), C("brinco_de_petsuchos", 1)],
  "Desça às Galerias Alagadas e derrube Petsuchos.",
  "Senebtisi tirou um dos braceletes e pôs no seu pulso: 'Para ele reconhecer quem o manda descansar. Quando a água subir, suba nas ilhas. Quebre as mesas de oferenda, ou ele come e volta mais forte. Traga o brinco dele. Ele vai querer que alguém guarde.'",
  "Senebtisi lavou o brinco no lago e o pendurou na própria orelha. Chorou sem fazer barulho.",
  "Petsuchos ficou lá embaixo quando a cheia encheu o Labirinto. A fome cresceu com a água. Faça ele descansar.", "Você trouxe o brinco. Então ele dorme.", requer=["h01"], itens=[("colar_de_ouro_de_sobek", 1)], mult=1.5)
q("h03", "Os Doze Pátios", 53, "djedi_mago", [M("esfinge_de_hawara", 1), C("glifo_da_resposta", 1)],
  "Responda ao enigma da Esfinge de Hawara.",
  "Djedi riu baixinho: 'Doze pátios, seis para o norte, seis para o sul. A Esfinge de lá não fala, ela mostra. Quando ela sentar e acender três glifos no peito, procure o pedestal que completa a frase. Se errar, o teto responde por ela. Traga o glifo do peito dela: quero ler.'",
  "Djedi virou o glifo na mão e ele mudou de forma. 'Viu? A resposta muda quando ninguém pergunta.'",
  "Você vai passar pelos Doze Pátios? Então vai encontrar a Esfinge. Eu quero o glifo do peito dela.", "O glifo! Ele mudou de novo. Ótimo.", requer=["h02"], mult=1.5)
q("h04", "A Que Faz a Garganta Respirar", 54, "senebtisi_sacerdotisa", [M("serket", 1), C("ferrao_de_serket", 1)],
  "Desça à Câmara de Amenemés e enfrente Serket.",
  "Senebtisi desenhou um ankh no seu peito com carvão: 'Serket fecha a garganta e abre a garganta. O veneno dela se acumula. Os ankhs acesos da câmara tiram tudo: use-os, mas eles apagam. Quebre os ninhos. E traga o ferrão: uma gota mata, duas curam.'",
  "Senebtisi guardou o ferrão num pote de mel. 'Agora o rei pode dormir. E nós podemos curar picada.'",
  "No fundo do Labirinto, Serket guarda o rei que o construiu. Ninguém desce sem passar por ela.", "O ferrão. Cuidado com a ponta.", requer=["h03"], mult=1.5)

# ---- L: O Livro de Thoth
q("l01", "O Velho de Cento e Dez Anos", 55, "djedi_mago", [E("gize"), I("estela_do_sonho", "gize")],
  "Leia a Estela do Sonho entre as patas da Esfinge.",
  "Djedi: 'Quéops me perguntou o número das câmaras secretas de Thoth. Eu disse que não sabia. Menti. Vá ler a estela entre as patas da Esfinge. Ela prometeu um reino a quem tirasse a areia. A areia saiu. Quem vai ser rei?'",
  "Embaixo da estela, alguém riscou: 'E agora, quem vai ser rei?'. Djedi riu: 'Fui eu. Em 1962.'",
  "Quer saber o que procuramos aqui? Comece pela Esfinge. Leia o que está entre as patas dela.", "Leu? Agora você sabe tanto quanto Tutmés. Pouco, mas é um começo.", requer=["k06"])
q("l02", "Os Rolos da Casa da Vida", 57, "djedi_mago", [I("nicho_de_rolos", "casa_vida", 4), M("sacerdote_mumia", 8)],
  "Procure o catálogo da Casa da Vida e afaste os sacerdotes mumificados.",
  "Djedi: 'A Casa da Vida era a biblioteca do templo. Os sacerdotes mumificados ainda guardam os rolos. Procure nos nichos o catálogo: quero saber se o Livro de Thoth passou por lá.'",
  "No catálogo, uma linha riscada: 'Livro de Thoth: devolvido ao rio'. Djedi ficou um tempo quieto. 'Setne devolveu. Então Setne sabe.'",
  "Os rolos da Casa da Vida viraram pó, quase todos. O catálogo, não. Catálogo nunca vira pó.", "Devolvido ao rio... claro. Setne Khamuas.", requer=["l01"])
q("l03", "O Ka de Setne", 58, "djedi_mago", [I("ka_de_setne", "casa_vida"), M("guardiao_falcao", 6)],
  "Fale com o ka de Setne Khamuas na Casa da Vida.",
  "Djedi: 'Setne Khamuas, filho de Ramessés, tirou o Livro de Thoth da tumba de Neferkaptah e devolveu depois de perder tudo. O ka dele mora numa estátua na Casa da Vida. Os falcões de Hórus guardam a estátua. Pergunte a ele onde está o que o Livro descrevia.'",
  "O ka de Setne disse uma frase só: 'O Livro era o mapa. O lugar fica embaixo da pata direita.'",
  "Um príncipe morto vai te dar a resposta que eu procuro há cento e dez anos. Ou mais.", "Embaixo da pata direita. Eu sabia. Eu sempre soube.", requer=["l02"])
q("l04", "Embaixo da Pata", 60, "djedi_mago", [S("escavacao_de_queops", 24), C("fragmento_de_esmeralda", 5)],
  "Cace na escavação de Quéops e junte fragmentos de esmeralda dos ninhos de escorpião.",
  "Djedi: 'A laje da pata tem uma ranhura. Os escorpiões de Serket carregam no ninho umas lascas verdes que não são egípcias. São de Atlântida. Junte cinco: uma delas é a chave.'",
  "Djedi juntou as lascas na palma da mão. Uma delas se encaixou nas outras sozinha, e zuniu.",
  "Os escorpiões do planalto guardam lascas verdes como se fossem ovos. Eu preciso delas.", "Cinco. E uma delas canta. É essa.", requer=["l03"])
q("l05", "A Câmara de Thoth", 62, "djedi_mago", [I("camara_de_thoth", "gize"), I("coluna_do_ritmo_eco", "escavacao")],
  "Encaixe a lasca na pata da Esfinge e leve o eco ao cristal dos atlantes.",
  "Djedi pôs a lasca na sua mão: 'Encaixe na ranhura da pata direita. O que está embaixo é como o que está em cima. Depois leve o que você ouvir ao cristal do atlante: ele vai entender.'",
  "A laje não abriu. Mas a lasca bateu no ritmo do cristal atlante, e o cristal parou de falhar por três batidas. Diaprepes chorou.",
  "Chegou a hora. Embaixo da pata está o Salão dos Registros, onde Thoth guardou o que trouxe da Atlântida.", "Não abriu? Não precisava abrir. Precisava responder.", requer=["l04"])
q("l06", "O Atlante que Subiu", 64, "diaprepes_atlante", [F("djedi_mago"), M("cria_de_apofis", 10)],
  "Ouça de Djedi o destino de Thoth e proteja o caminho dos atlantes no Mar de Areia.",
  "Diaprepes: 'O cristal parou de falhar por três batidas. Eu preciso saber onde está Thoth. O velho sabe e não me diz. Pergunte você. E as crias da serpente estão comendo os meus batedores no Mar de Areia.'",
  "Djedi contou a verdade: Thoth subiu, há muito tempo, e deixou a chave para quem soubesse ouvir. Diaprepes ouviu calado e, no fim, agradeceu.",
  "Vim de tão longe buscar alguém que talvez não esteja mais aqui.", "Ele subiu. E deixou a chave para nós. Então a Coluna tem jeito.", requer=["l05"])

# ---- V: As Lâmpadas de Dendera (Vigília)
q("v01", "O Relevo", 56, "dalva_ferraz", [I("relevo_de_dendera", "karnak", 3)], "Copie os três relevos das lâmpadas.",
  "DESPACHO DA OFICINA · ENGENHEIROS HEREGES\nTrês relevos em Karnak têm o mesmo desenho do templo de Hathor em Dendera: bulbo, filamento-serpente, pilar djed. Copie os três. Papel no meu bolso esquerdo, carvão no direito.\n— Dalva",
  "Dalva pôs as três cópias lado a lado e bateu na mesa: 'É um circuito! Está desenhado na parede há quatro mil anos!'",
  "Os antigos tinham luz sem fogo. Eu tenho certeza. Preciso das cópias dos relevos de Karnak.", "Bulbo, filamento, isolador. Não é deus. É engenharia.", requer=["k06"], faccao="vigilia")
q("v02", "O Filamento-Serpente", 58, "dalva_ferraz", [M("naja", 10), C("glandula_de_naja", 5)], "Traga glândulas de naja para a Dalva testar.",
  "DESPACHO DA OFICINA\nNo relevo, o filamento é uma serpente. Pode ser só desenho. Pode ser que o veneno de naja conduza. Quero testar. Cinco glândulas.\n— Dalva",
  "Dalva molhou um fio no veneno e encostou na pilha. Faiscou verde. Ela gritou de alegria e queimou a sobrancelha.",
  "Veneno de naja conduz? Só tem um jeito de saber.", "FAISCOU! Faiscou verde!", requer=["v01"], faccao="vigilia")
q("v03", "O Pilar Djed", 61, "dalva_ferraz", [S("calcada_de_quefren", 24), C("pilar_djed_de_bronze", 1)], "Tire um pilar djed de bronze dos guardiões da Calçada de Quéfren.",
  "DESPACHO DA OFICINA\nOs guardiões mumificados da Calçada de Quéfren carregam pilares djed de bronze na cintura. Um isolador perfeito. Traga um. Eles não vão dar de boa vontade.\n— Dalva",
  "Dalva enrolou fio no pilar e ligou na pilha. Pela primeira vez, o bulbo de vidro dela brilhou sozinho, fraco como vaga-lume.",
  "Preciso do isolador. Os guardiões da calçada têm. Eles são agressivos, vá com gente.", "É um isolador! Olha, olha!", requer=["v02"], faccao="vigilia")
q("v04", "Luz sem Fogo", 63, "dalva_ferraz", [E("hatshepsut"), C("lampada_de_dendera", 1)], "Encontre uma lâmpada inteira nos Terraços de Djeser-Djeseru.",
  "DESPACHO DA OFICINA\nOs escaravelhos-rei guardam o que brilha. Um deles foi visto nos terraços de Hatshepsut com um bulbo inteiro no ninho. Uma lâmpada de verdade, de quatro mil anos.\n— Dalva",
  "Dalva segurou a lâmpada como se fosse um filho. Ligou na pilha. A oficina inteira ficou branca por um segundo. 'A Vela vai acender sem pavio', ela disse, e mandou um bonde inteiro de cartas para o Acampamento da Vela.",
  "Uma lâmpada inteira. Se eu tiver uma, a Vigília nunca mais fica no escuro.", "Luz sem fogo. Gustavo ia chorar.", requer=["v03"], faccao="vigilia", itens=[("luvas_de_dalva", 1)], mult=1.3)

# ---- A: A Balança do Coro (Arautos)
q("a01", "A Balança do Templo", 56, "conego_barnabe", [I("balanca_de_pedra", "karnak")], "Veja a balança de granito de Karnak.",
  "CARTA DO CORO · AO IRMÃO QUE PESA\nEm Karnak há uma balança de granito do tamanho de um homem. Vá vê-la. Diga-me se o prato vazio desce quando você chega perto.\n— Barnabé, Cônego",
  "Barnabé ouviu e equilibrou a balancinha dele nos dedos. 'Desceu. Então ela ainda pesa. Então ainda há juízo, mesmo travado.'",
  "Uma balança que pesa sozinha, filho. Vá ver. Eu já sou velho para escada de templo.", "Desceu? Bendito seja. Ela ainda pesa.", requer=["k06"], faccao="arautos")
q("a02", "O Peso de uma Pena", 58, "conego_barnabe", [M("guardiao_falcao", 8), C("pena_de_maat", 4)], "Traga penas de Maat dos guardiões de Hórus.",
  "CARTA DO CORO\nO coração se pesa contra a pena de Maat. Os guardiões de cabeça de falcão as carregam na coroa. Precisamos de quatro: uma para a balança, três para errar.\n— Barnabé",
  "Barnabé pôs uma pena no prato da balancinha. O prato desceu, devagar, e parou no meio. 'Exata. Perfeita. Assustadora.'",
  "Para pesar um coração, filho, primeiro é preciso uma pena que não minta.", "Quatro penas. Uma delas pesa exatamente o que deveria.", requer=["a01"], faccao="arautos")
q("a03", "Os Corações nos Vasos", 61, "conego_barnabe", [M("anubis_sentinela", 10), C("vaso_canopico_lacrado", 4)], "Traga vasos canópicos lacrados para o Coro estudar.",
  "CARTA DO CORO\nOs egípcios tiravam tudo do morto e guardavam em quatro vasos, menos o coração. O coração ficava no peito, para ser pesado. Quero ver o que eles guardavam. Os anúbis não vão gostar.\n— Barnabé",
  "Barnabé abriu um vaso e fechou logo. 'Fígado. Três mil anos e ainda cheira a fígado.' Ele anotou alguma coisa e rezou baixinho.",
  "Quatro vasos, quatro filhos de Hórus. O coração fica fora. Quero entender por quê.", "Fígado. Pulmão. Estômago. Intestino. Nunca o coração.", requer=["a02"], faccao="arautos")
q("a04", "Coração de Granito", 63, "conego_barnabe", [S("vale_dos_reis", 24)], "Abra caminho pelo Vale dos Reis até a tumba sem cartucho.",
  "CARTA DO CORO\nA tumba sem cartucho está no fundo do Vale dos Reis, e os anúbis da guarda de honra deixaram os escavadores entrarem. Ninguém sabe por quê. Abra o caminho. O Coro vai pesar aquele coração, nem que seja com as mãos.\n— Barnabé",
  "Barnabé chegou à porta da tumba e pôs a mão no cartucho raspado. A pedra bateu uma vez. Ele tirou a mão e sorriu: 'Ele está lá. E está com medo.'",
  "Deus endureceu aquele coração. Nós vamos amolecer.", "Ele bateu, filho. O coração bateu na minha mão.", requer=["a03"], faccao="arautos", itens=[("balanca_de_barnabe", 1)], mult=1.3)

# ---- N: O Coração Endurecido
q("n01", "As Pragas Recomeçam", 60, "djedi_mago", [I("praga_de_sangue", "margem_papiro", 3)], "Colha a água do Nilo que virou sangue em três pontos.",
  "Djedi estava sério pela primeira vez: 'A Rádio do Cairo conta as pragas: sangue, rãs, piolhos, moscas, peste, úlceras, granizo, gafanhotos, trevas. Falta uma. O rio está virando sangue de novo nas margens. Colha em três lugares. Quero saber se é aviso ou é ordem.'",
  "O sangue nos frascos não coagulou. Djedi encostou o ouvido no vidro. 'Bate. Como um coração. É ordem.'",
  "As pragas recomeçaram, uma por mês, na ordem do Êxodo. A primeira voltou.", "Bate como um coração. Isto não é aviso.", requer=["l04"], extra={"requer_qualquer": ["v03", "a03", "l05"]})
q("n02", "As Portas Marcadas", 62, "djedi_mago", [I("porta_marcada", "menfis", 3)], "Veja as portas marcadas com sangue em Mênfis.",
  "Djedi: 'Em Mênfis algumas famílias passaram sangue de cordeiro nos lintéis, como na noite da Páscoa. Alguém lembrou o que vem depois das trevas. Vá ver as portas.'",
  "Três portas, três famílias rezando em línguas que ninguém fala mais. Djedi fechou o olho bom: 'Eles sabem que o Anjo Destruidor vai passar. Ninguém sabe a quem ele obedece desta vez.'",
  "Depois das trevas vem a décima. Mênfis já sabe.", "A décima praga é a morte dos primogênitos. Do mundo inteiro.", requer=["n01"])
q("n03", "A Tumba Sem Cartucho", 64, "djedi_mago", [I("cartucho_raspado", "vale_reis"), S("necropole_proibida", 24)], "Toque o cartucho raspado e abra a Necrópole Proibida.",
  "Djedi pôs a mão no seu ombro, e ela pesava como pedra: 'A tumba sem cartucho fica no fundo do Vale. Ponha a mão no nome raspado. Ele vai bater. Depois limpe a Necrópole, onde os sacerdotes enterraram o que tinham medo de pesar. Só entra no Coração Endurecido quem o coração reconheceu.'",
  "O cartucho bateu na sua mão. Desde então, uma vez por minuto, você sente uma segunda batida no peito que não é sua. A tumba sabe quem você é.",
  "Ninguém entra no Coração Endurecido sem que o coração saiba quem é. Leve gente. Leve muita gente.", "Bateu na sua mão? Então você pode entrar. Que Thoth anote.", requer=["n02"], mult=1.5)
for i, (c, nivel) in enumerate([("sekhmet", 60), ("janes", 61), ("imseti", 62), ("apofis", 63), ("anubis_pesador", 64), ("farao_sem_nome", 65)]):
    nome = CHEFES[c]["nome"]
    txt = {
        "sekhmet": ("A Leoa que Bebeu o Sangue", "Rá mandou Sekhmet acabar com a humanidade e a deteve com sete mil jarras de cerveja ocre. O rito do Faraó a acordou no primeiro portão. Quebre as jarras perto dela quando a Sede subir.", "Sekhmet deitou no pátio e dormiu, como depois da cerveja, há cinco mil anos."),
        "janes": ("Os Magos de Faraó", "Janes e Jambres imitaram Moisés até a terceira praga. Eles imitam um ao outro: derrube os dois juntos, ou um levanta o outro. Separe-os.", "Os magos caíram de mãos dadas, como foram enterrados. No chão, dois bastões que não viraram serpente."),
        "imseti": ("Os Quatro Filhos de Hórus", "Os quatro guardiões dos vasos canópicos lutam dois de cada vez. Cada um que cai derrama o vaso dele no chão: escolha onde e em que ordem.", "Os quatro vasos se quebraram. Imseti olhou o rei por cima do ombro, como quem pede desculpas."),
        "apofis": ("A Serpente Sem Fim", "Na sétima hora da noite, Apófis ataca a barca de Rá. Mantenha a Lanterna de Rá acesa com as brasas da proa e, quando os olhos acenderem, vire de costas.", "A serpente afundou no rio escuro. A barca seguiu para a oitava hora, e um pouco de luz passou pela fresta do Sol Terço."),
        "anubis_pesador": ("O Pesador", "Anúbis vai pesar vocês: metade Coração, metade Pena, cada um no seu prato. Equilibrem a balança. Segurem Ammit longe dos caídos.", "Anúbis baixou o cetro. 'A pena pesou. Agora vocês sabem o que eu sinto há três mil anos.'"),
        "farao_sem_nome": ("O Faraó Sem Nome", "O Faraó lança as pragas na ordem do Êxodo. Na décima, o Anjo Destruidor passa: fiquem sob as portas com sangue no lintel, até três por porta.", "O Faraó caiu dizendo não. O coração dele rolou pelo chão do salão, inteiro, batendo."),
    }[c]
    q(f"n{4 + i:02d}", txt[0], nivel, "djedi_mago", [M(c, 1)], f"Derrote {nome} no Coração Endurecido.",
      "Djedi, diante da tumba sem cartucho: '" + txt[1] + "'", txt[2], txt[1], "Voltou. Nem todo mundo volta.",
      requer=["n03"] if i == 0 else [f"n{3 + i:02d}"], mult=2.0,
      itens=([("olho_de_horus", 1)] if c == "imseti" else [("khopesh_de_ramesses", 1)] if c == "apofis" else [("cetro_was_do_pesador", 1)] if c == "anubis_pesador" else []) )
q("n10", "O Que Fazer com um Coração", 66, "djedi_mago", [C("coracao_do_farao", 1), {"tipo": "decidir", "npc": "djedi_mago"}],
  "Decida o destino do Coração do Faraó.",
  "Os quatro acampamentos esperam na tenda de Djedi. O Coração está na sua mão, batendo uma vez por minuto.\nBarnabé quer pesá-lo na balança: se cair, o Juízo destrava.\nDalva quer quebrá-lo: sem coração não há décima praga.\nDjedi quer devolvê-lo ao Nilo, como Setne devolveu o Livro: 'o que não se pode pesar nem destruir, se devolve'.",
  "O que você escolheu correu a Terra Negra antes do pôr do Sol Terço.",
  "Chegou a hora, e ela é sua. Eu sou velho demais para escolher pelo mundo.", "Escolha. O coração está batendo mais rápido.",
  requer=["n09"], mult=2.0, extra={"escolhas": [
      {"id": "pesar", "texto": "Entregar o coração ao Coro para ser pesado.", "flags": ["coracao_pesado"], "recompensas": {"xp": xp(66) * 2, "ouro": ouro(66) * 2, "itens": [{"id": "balanca_de_barnabe", "qtd": 1}]},
       "texto_conclusao": "Barnabé pôs o coração no prato. A pena subiu. O coração não desceu nem subiu: ficou no meio, para sempre. Barnabé chorou de alegria, ou de outra coisa."},
      {"id": "quebrar", "texto": "Entregar o coração à Dalva para ser quebrado.", "flags": ["coracao_quebrado"], "recompensas": {"xp": xp(66) * 2, "ouro": ouro(66) * 2, "itens": [{"id": "luvas_de_dalva", "qtd": 1}]},
       "texto_conclusao": "Dalva bateu com o martelo três vezes. Na terceira o coração rachou e saiu de dentro um som de mar fechando. As portas marcadas de Mênfis foram lavadas no dia seguinte."},
      {"id": "devolver", "texto": "Devolver o coração ao Nilo, com Djedi.", "flags": ["coracao_devolvido"], "recompensas": {"xp": xp(66) * 2, "ouro": ouro(66) * 2, "itens": [{"id": "olho_de_horus", "qtd": 1}]},
       "texto_conclusao": "Djedi e você soltaram o coração no meio do rio, de cima da feluca de Ahmose. Ele afundou batendo. Djedi fez cento e onze anos naquela noite."}]})

# ---- R: diárias
for i, (rid, titulo, nivel, spot, npc, fala) in enumerate([
        ("r01", "Turno no Juncal", 51, "juncal_do_papiro", "nefer_aguadeira", "Juncal cheio de novo. Limpa um pouco, que eu levo água para quem fica."),
        ("r02", "Turno na Vila", 54, "vila_dos_artesaos", "reis_abdu", "Os mortos da Vila voltaram ao turno. Você também."),
        ("r03", "Turno em Karnak", 58, "salao_hipostilo", "tuya_nomarca", "O salão hipostilo tem guarda nova. Morta. Tire."),
        ("r04", "Turno em Gizé", 61, "escavacao_de_queops", "reis_abdu", "Quadrícula por quadrícula, escorpião por escorpião."),
        ("r05", "Turno no Faium", 64, "lago_meris", "senebtisi_sacerdotisa", "O lago tem filhos demais. Alguns precisam descansar."),
        ("r06", "Turno no Vale", 68, "vale_dos_reis", "reis_abdu", "O Vale paga em dobro. Porque morre em dobro.")]):
    q(rid, titulo, nivel, npc, [S(spot, 30)], f"Cace 30 no spot ({spot.replace('_', ' ')}).",
      f"CADERNO DO REIS · DIÁRIA\n{fala}", "Diária feita. Volte amanhã.", fala, "Diária feita. Volte amanhã.", requer=["k06"] if i > 0 else ["k03"],
      extra={"repete": "diaria"}, mult=0.6)


# ---- ids com prefixo (k01 etc. já existem na área inicial)
PFX = "eg_"
for q_ in MISSOES:
    q_["id"] = PFX + q_["id"]
    q_["requer"] = [PFX + r for r in q_["requer"]]
    if "requer_qualquer" in q_: q_["requer_qualquer"] = [PFX + r for r in q_["requer_qualquer"]]
for o in OBJETOS:
    if "visivel_se" in o: o["visivel_se"] = {"missao_ativa": [PFX + r for r in o["visivel_se"]["missao_ativa"]]}


# ============================================================================ monstros (bestiário)
def monstros():
    out = []
    drops = {"ibis_de_thoth": [("pena_de_ibis", .4, "k03")], "mumia_operaria": [("ostraco_de_faltas", .3, "k08")], "escorpiao_de_serket": [("fragmento_de_esmeralda", .3, "l04")],
             "naja": [("glandula_de_naja", .4, "v02")], "guardiao_mumia": [("pilar_djed_de_bronze", .25, "v03")], "escaravelho_rei": [("lampada_de_dendera", .5, "v04")],
             "guardiao_falcao": [("pena_de_maat", .4, "a02")], "sacerdote_mumia": [("vaso_canopico_lacrado", .3, "a03")]}
    drops.update({"petsuchos": [("brinco_de_petsuchos", 1.0, "h02")], "esfinge_de_hawara": [("glifo_da_resposta", 1.0, "h03")],
                  "serket": [("ferrao_de_serket", 1.0, "h04")], "farao_sem_nome": [("coracao_do_farao", 1.0, "n10")]})
    drops = {k: [(a, b, PFX + c) for a, b, c in v] for k, v in drops.items()}
    locais = {}
    mp = json.load(open(os.path.join(AQUI, "mapas", "egito.json")))
    for g in mp["spawns"]:
        x, y = int(g["pos"][0]), int(g["pos"][1]); ch = mp["zona_grade"][y][x]
        if ch != ".": locais.setdefault(g["mob"], set()).add(mp["zonas"][ord(ch) - 65]["id"])
    for f in ["hawara_1", "hawara_2", "hawara_3"] + [f"coracao_{i}" for i in range(1, 7)]:
        dm = json.load(open(os.path.join(AQUI, "mapas", f + ".json")))
        for g in dm["spawns"]: locais.setdefault(g["mob"], set()).add(f)
        for a in dm.get("chefe", {}).get("adicionais", []):
            if isinstance(a, dict) and a.get("mob"): locais.setdefault(a["mob"], set()).add(f)
            elif isinstance(a, str): locais.setdefault(a, set()).add(f)
        if dm.get("chefe"): locais.setdefault(dm["chefe"]["id"], set()).add(f)
    for k, m in {**MOBS, **MOBS_DUNGEON}.items():
        out.append({"id": k, "nome": m["nome"], "tipo": "elite" if m["arquetipo"] == "elite" else ("chefe" if "chefe_par" in m.get("tags", []) else "normal"),
                    "locais": sorted(locais.get(k) or {"necropole" if m.get("area") == "egito" else "coracao_1"}), "descricao": m["motivo"][0].upper() + m["motivo"][1:] + ".", "aparencia": m.get("comportamento", ""),
                    "drops_missao": [{"item": a, "chance": b, "missao": c} for a, b, c in drops.get(k, [])],
                    "registros": m.get("registros", [{"fonte": "caderno_tamit", "titulo": m["nome"], "texto": m["motivo"][0].upper() + m["motivo"][1:] + "."}]),
                    "nivel": m["niveis"]})
    for k, c in CHEFES.items():
        out.append({"id": k, "nome": c["nome"], "tipo": "chefe", "locais": sorted(locais.get(k, {"coracao_1"})), "descricao": c["conceito"], "aparencia": "",
                    "drops_missao": [{"item": a, "chance": b, "missao": c_} for a, b, c_ in drops.get(k, [])], "registros": [{"fonte": "caderno_tamit", "titulo": c["nome"], "texto": c["conceito"]}], "nivel": [c["nivel"], c["nivel"]]})
    return out


def dialogos():
    por = {}
    for q_ in MISSOES:
        por.setdefault(q_["doador"], []).append(("oferta", q_)); por.setdefault(q_["entrega"], []).append(("fim", q_))
    out = []
    for n in NPCS:
        nid = n["id"]
        if nid == "nefer_carrinho":
            out.append({"id": "dlg_nefer_carrinho", "npc": nid, "inicio": "raiz", "nos": {"raiz": {"fala": "Água! Mirra! Pra quem fica no spot o dia inteiro, eu trago o carrinho até a fogueira.",
                        "opcoes": [{"texto": "Mostra o que tem.", "acoes": [{"abrir_loja": "loja_carrinho_nefer"}]}, {"texto": "Até mais."}]}}})
            continue
        nos = {"raiz": {"fala": n["falas_ambiente"][0] + " " + n["personalidade"].split(".")[0] + ".", "opcoes": []}}
        op = nos["raiz"]["opcoes"]
        for tipo, q_ in por.get(nid, []):
            qid = q_["id"]
            if tipo == "oferta":
                nos[qid + "_oferta"] = {"fala": q_["_oferta"] or q_["resumo"], "opcoes": [{"texto": "Deixa comigo.", "acoes": [{"aceitar_missao": qid}]}, {"texto": "Agora não."}]}
                op.append({"texto": q_["titulo"] + "?", "ir": qid + "_oferta", "se": {"missao_disponivel": qid}})
            if tipo == "fim":
                fim = q_["_fim"] or q_["texto_conclusao"]
                if q_.get("escolhas"):
                    nos[qid + "_fim"] = {"fala": fim, "opcoes": [{"texto": e["texto"], "acoes": [{"concluir_missao": qid, "escolha": e["id"]}]} for e in q_["escolhas"]] + [{"texto": "Preciso pensar."}]}
                else:
                    ac = [{"concluir_missao": qid}]
                    if qid == PFX + "n03": ac.append({"definir_flag": "sintonia_coracao"})
                    nos[qid + "_fim"] = {"fala": fim, "opcoes": [{"texto": "Feito.", "acoes": ac}]}
                op.append({"texto": "Sobre " + q_["titulo"].lower() + ".", "ir": qid + "_fim", "se": {"missao_pronta": qid}})
        if n.get("loja"): op.append({"texto": "Quero ver o que você tem.", "acoes": [{"abrir_loja": n["loja"]}]})
        nos["historia"] = {"fala": n["historia"].split(" (Segredo")[0], "opcoes": [{"texto": "Voltar.", "ir": "raiz"}]}
        op.append({"texto": "Quem é você?", "ir": "historia"}); op.append({"texto": "Até mais."})
        out.append({"id": "dlg_" + nid, "npc": nid, "inicio": "raiz", "nos": nos})
    return out


def main():
    os.makedirs(SAIDA, exist_ok=True)
    ms = [{k: v for k, v in q_.items() if not k.startswith("_")} for q_ in MISSOES]
    npcs = [{"id": n["id"], "nome": n["nome"], "titulo": n["titulo"], "faccao": n["faccao"], "classe_visual": n["classe_visual"],
             "local": {"subzona": n["local"], "ponto": n["ponto"]}, "servicos": n.get("servicos", []), **({"loja": n["loja"]} if n.get("loja") else {}),
             "dialogo": "dlg_" + n["id"], "aparencia": n["aparencia"], "personalidade": n["personalidade"], "historia": n["historia"],
             "falas_ambiente": n.get("falas_ambiente", [])} for n in NPCS]
    dl = dialogos(); mons = monstros()
    mapa = json.load(open(os.path.join(AQUI, "mapas", "egito.json")))
    area = {"id": "egito", "nome": "Egito, a Terra Negra", "tipo": "campo", "faccao": None, "nivel": [50, 70],
            "descricao": "A terra da quarta trombeta, sob o Sol Terço. O Nilo voltou e cobriu de lodo preto a areia que tinha enterrado tudo: Mênfis se reergueu em dois andares, o de lama é de agora e o de pedra é de antes. Do lado dos mortos, a maior escavação do mundo ao pé da Esfinge; no fundo do Vale dos Reis, a tumba sem cartucho do Faraó do Êxodo.",
            "musica_sugerida": "harpa angular e alaúde de cordas de tripa, sistro de bronze, tambor de moldura grave, vento de areia, coro masculino distante em uníssono",
            "subzonas": [{"id": z["id"], "nome": z["nome"], "tipo": "base" if z["seguro"] else "campo", "faccao": None, "seguro": z["seguro"], "nivel": z["nivel"]} for z in mapa["zonas"]]}
    dungs = [{"id": "labirinto_de_hawara", "nome": "O Labirinto de Hawara", "faccao": None, "nivel": [50, 54], "entrada": "faium",
              "descricao": "O Labirinto que Heródoto viu 'acima das pirâmides': doze pátios e três mil salas, metade debaixo da terra. A cheia encheu as galerias de baixo; Petsuchos, a Esfinge e Serket guardam o rei que o construiu.",
              "andares": [{"id": "hawara_1", "nome": "Galerias Alagadas", "nivel": [50, 51], "chefe": "petsuchos"},
                          {"id": "hawara_2", "nome": "Os Doze Pátios", "nivel": [52, 53], "chefe": "esfinge_de_hawara"},
                          {"id": "hawara_3", "nome": "Câmara de Amenemés", "nivel": [53, 54], "chefe": "serket"}]},
             {"id": "coracao_endurecido", "nome": "O Coração Endurecido", "faccao": None, "nivel": [60, 60], "entrada": "vale_reis", "raid": True, "grupo": [5, 10],
              "descricao": "A tumba sem cartucho do Faraó do Êxodo: seis salões, do pátio de Sekhmet à câmara onde o coração que não coube na balança ainda bate.",
              "andares": [{"id": f"coracao_{i + 1}", "nome": nm, "nivel": [60, 60], "chefe": c} for i, (nm, c) in enumerate([
                  ("Pátio do Sol Terço", "sekhmet"), ("Salão dos Magos", "janes"), ("Câmara Canópica", "imseti"), ("O Rio do Duat", "apofis"),
                  ("Salão das Duas Verdades", "anubis_pesador"), ("Câmara do Coração", "farao_sem_nome")])]}]
    spots_ped = [{"id": s["id"], "nome": s["nome"], "nivel": s["nivel"], "subzona": s["zona"],
                  "monstros": sorted({g["mob"] for g in mapa["spawns"] if g.get("spot") == s["id"]})} for s in mapa["spots"]]
    W = lambda nome, obj: json.dump(obj, open(os.path.join(SAIDA, nome), "w"), ensure_ascii=False, indent=1)
    W("missoes_acrescimo.json", {"_doc": "Acrescentar a design/missoes/dados/missoes.json (Egito, nível 50 a 70).", "missoes": ms})
    W("npcs_acrescimo.json", {"npcs": npcs}); W("dialogos_acrescimo.json", {"dialogos": dl})
    W("itens_acrescimo.json", {"_doc": "Consumíveis, itens de missão, leituras e recompensas únicas do Egito.", "itens": ITENS})
    W("skills_itens_acrescimo.json", {"_doc": "Para design/skills-itens/fontes/itens_data.py: POOLS_LENDARIOS recebe 'pools' (cada chefe do Egito tem a sua lista; as peças dos conjuntos também caem por lendario:regalia_*), MATERIAIS recebe 'materiais', CONJUNTOS recebe 'conjuntos'. Os itens em si estão em itens_acrescimo.json (thread Missões).",
                                      "pools": IE.pools(), "materiais": IE.MATERIAIS,
                                      "conjuntos": [{"id": c["id"], "nome": c["nome"], "nivel": c["nivel"], "pecas_ids": [i for i, *_ in c["pecas"]], "bonus": c["bonus"], "lore": c["lore"]} for c in IE.CONJUNTOS]})
    W("monstros_acrescimo.json", {"monstros": mons}); W("objetos_acrescimo.json", {"objetos": OBJETOS, "baus": BAUS}); W("lojas_acrescimo.json", {"lojas": LOJAS})
    W("locais_acrescimo.json", {"areas": [area], "dungeons": dungs, "spots_pedidos": spots_ped})
    # ---- confere com o validar.py da thread de Missões numa cópia temporária
    tmp = tempfile.mkdtemp()
    shutil.copytree(os.path.join(RAIZ, "design", "missoes"), os.path.join(tmp, "missoes"), ignore=shutil.ignore_patterns("__pycache__"))
    os.makedirs(os.path.join(tmp, "mapas", "mata_do_granizo"))
    shutil.copy(os.path.join(RAIZ, "design", "mapas", "spots.json"), os.path.join(tmp, "mapas"))
    shutil.copy(os.path.join(RAIZ, "design", "mapas", "mata_do_granizo", "dados.json"), os.path.join(tmp, "mapas", "mata_do_granizo"))
    d = os.path.join(tmp, "missoes", "dados")
    def junta(nome, chave, novos):
        j = json.load(open(os.path.join(d, nome))); j[chave] += novos; json.dump(j, open(os.path.join(d, nome), "w"), ensure_ascii=False)
    junta("missoes.json", "missoes", ms); junta("npcs.json", "npcs", npcs); junta("dialogos.json", "dialogos", dl)
    junta("itens.json", "itens", ITENS); junta("monstros.json", "monstros", mons); junta("lojas.json", "lojas", LOJAS)
    junta("objetos.json", "objetos", OBJETOS); junta("objetos.json", "baus", BAUS)
    L = json.load(open(os.path.join(d, "locais.json")))
    L["areas"].append(area); L["dungeons"] += dungs
    L.setdefault("spots", {}).setdefault("pedidos", []).extend(spots_ped)
    json.dump(L, open(os.path.join(d, "locais.json"), "w"), ensure_ascii=False)
    r = subprocess.run([sys.executable, os.path.join(tmp, "missoes", "validar.py")], capture_output=True, text=True)
    print(r.stdout[-4000:], r.stderr[-2000:])
    print(f"missões {len(ms)} | NPCs {len(npcs)} | itens {len(ITENS)} | monstros {len(mons)} | objetos {len(OBJETOS)} | XP total {sum(m['recompensas']['xp'] for m in ms if m['tipo'] != 'repetivel')}")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
