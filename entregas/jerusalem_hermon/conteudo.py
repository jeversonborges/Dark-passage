"""Missões, NPCs, diálogos, itens, monstros, objetos e lojas de Jerusalém e Monte Hermon (Arautos).

REGRA DO ESPELHO: cada missão daqui é uma cópia estrutural de uma missão que a Vigília faz do nível 1 ao 12
(as dela e as "ambas" do deserto): mesmo nível, mesma XP, mesmo ouro, mesmos objetivos em número e tipo, mesmos
pré-requisitos e escolhas. O script copia a missão do deserto, troca os ids (NPC, mob, spot, item, objeto, subzona)
pelos espelhos e põe por cima o texto próprio daqui. Itens de recompensa são cópias dos do deserto (mesmos atributos).

Saída (formato de design/missoes/dados/*.json, só os acréscimos; ver INTEGRACAO.md):
  missoes_acrescimo.json, npcs_acrescimo.json, dialogos_acrescimo.json, itens_acrescimo.json, monstros_acrescimo.json,
  objetos_acrescimo.json, lojas_acrescimo.json, locais_acrescimo.json
Uso: python3 conteudo.py   (confere tudo com o validar.py da thread de Missões numa cópia temporária)
"""
import copy, json, os, shutil, subprocess, sys, tempfile
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
DADOS = os.path.join(RAIZ, "design", "missoes", "dados")
def load(n): return json.load(open(os.path.join(DADOS, n), encoding="utf-8"))
MISS = {q["id"]: q for q in load("missoes.json")["missoes"]}
ITENS = {i["id"]: i for i in load("itens.json")["itens"]}
MONS = {m["id"]: m for m in load("monstros.json")["monstros"]}
OBJS = {o["id"]: o for o in load("objetos.json")["objetos"]}
BAUS = {b["id"]: b for b in load("objetos.json")["baus"]}

# ============================================================================ trocas de ids
M_ID = {"v01": "j01", "v02": "j02", "v03": "j03", "v04": "j04", "v05": "j05", "s01": "js01", "s02": "js02", "s03": "js03", "s04": "js04",
        "s08": "js08", "s09": "js09", "r01": "jr01", "c01": "jc01", "c02": "jc02", "c03": "jc03", "c04": "jc04", "c05": "jc05", "c06": "jc06",
        "d01v": "jd01", "d02": "jd02", "d03": "jd03", "d04": "jd04", "d05": "jd05", "d06": "jd06", "e01v": "je01", "e02": "je02", "e03": "je03",
        "e04": "je04", "e05v": "je05", "f01v": "jf01", "f02": "jf02", "f03": "jf03", "f04": "jf04", "f05": "jf05", "f06": "jf06", "g01": "jg01"}
NPC = {"capita_odete": "sariel_porta", "doutor_anselmo": "hulda_escada", "mae_cardo": "zilpa_hissopo", "gaspar_bigorna": "tubal_malho",
       "tobias_pavio": "bartimeu_brasas", "simao_coveiro": "henoc_escriba", "frei_anacleto": "rispa_vigilia", "isaura_radialista": "jael_escuta",
       "corvina_atravessadora": "zaqueu_cobrador", "automatico": "automatico"}
MOB = {"carnical": "peregrino_ressecado", "corvo_de_cinza": "abutre_do_hermon", "cao_de_vala": "chacal_de_josafa", "nao_julgado": "levantado_das_oliveiras",
       "porco_pestilento": "porco_de_gadara", "acougueiro_oco": "fornalheiro_de_tofete", "capataz_gancho": "capataz_de_tofete",
       "filho_de_cardo": "filho_do_hissopo", "monge_emparedado": "escriba_emparedado", "eco_da_trombeta": "eco_do_juramento",
       "general_partido": "ohya_gigante", "irma_celeste": "naama_noiva", "zacarias_arauto": "semyaza_juramento", "ultimo_operador": "kokabiel_contador",
       "desertor_legiao": "sapador_herege", "sangrador_apostata": "sineiro_infiltrado", "sombra_gravada": "vigilante_acorrentado",
       "larva_de_carne": "verme_do_fosso", "gancheiro": "escravo_dos_gigantes", "soldado_caido": "soldado_de_pedra",
       "carpideira_de_ossos": "noiva_afogada", "fogo_de_vela": "brasa_de_azazel", "querubim_desfeito": "vigilante_desfeito"}
SPOT = {"covas_rasas": "getsemani", "telhados_dos_corvos": "escadas_de_siloe", "fosso_dos_caes": "covil_dos_chacais", "procissao_parada": "primeiros_a_levantar",
        "chiqueiro_do_carnica": "pocilga_de_gadara", "margem_das_viuvas": "cedros_partidos", "acampamento_desertores": "acampamento_sapadores",
        "marco_do_corte": "fenda_das_oliveiras", "patio_do_abatedouro": "fornalhas_de_tofete", "beira_da_tempestade": "neve_de_cinza"}
SUB = {"campos_cinza": "monte_oliveiras", "cemiterio_sao_lazaro": "necropole_oliveiras", "abatedouro_carnica": "vale_hinom", "bairro_afogado": "cidade_de_davi",
       "vala_comum": "vale_josafa", "rio_amargo": "fontes_jordao", "tempestade_areia": "cume_hermon", "bosque_viuvas": "encosta_cedros",
       "chiqueiros": "pocilgas_gadara", "mata_cardos": "bosque_hissopo", "acampamento_vela": "jerusalem", "porao_matadouro": "minas_dos_gigantes",
       "ossario_carpideiras": "salao_das_noivas", "camara_trombeta": "altar_do_juramento"}
OBJ = {"corpo_lacrado": "peregrino_de_joelhos", "escritorio_capataz": "mesa_do_capataz", "porta_ganchos": "porta_de_pa", "porta_camara": "porta_do_altar",
       "tumulo_cardo": "tumulo_de_joas", "covas_abertas": "tumulos_dos_profetas", "cela_monge": "nicho_da_noiva", "estandartes_caidos": "estandartes_da_legiao",
       "marco_do_corte": "trono_vazio", "rastro_arrasto": "rastro_de_brasas", "pocas_amargas": "fontes_secas", "escotilha_silo": "laje_do_juramento",
       "antena_radio": "antena_da_escuta", "andor_padroeiro": "pedra_da_ascensao", "sepulcro_primeiro": "tumulo_vazio_de_henoc",
       "bau_tobias_1": "bau_bartimeu_1", "bau_tobias_2": "bau_bartimeu_2", "bau_tobias_3": "bau_bartimeu_3",
       "bau_barraca_anselmo": "bau_escada_hulda", "bau_general": "bau_ohya", "bau_celeste": "bau_naama", "bau_zacarias": "bau_semyaza",
       "bau_amaldicoado_ossario": "bau_dote_naama"}
OBJ_POR_MISSAO = {("s03", "torre_sino"): "forja_de_tofete", ("f03", "torre_sino"): "rolos_da_escada"}

# itens: id do deserto -> (id novo, nome, descrição, citação (texto, autor) | None). Atributos e efeitos são copiados.
IT = {
    "faixa_vigilia": "fita_juizo", "tonico_graxa": "hostia_negra",            # já existem para os Arautos
    "bobina_cobre": ("azeite_do_lagar", "Azeite do Lagar", "Azeite grosso das últimas oliveiras do Getsêmani, guardado em odre de couro. Os abutres furam os odres dos peregrinos mortos e levam para o ninho.", ("A Brasa come qualquer óleo. Este ela come com gosto.", "Hulda da Escada")),
    "vela_simao": ("vela_do_escriba", "Vela de Cera do Escriba", "Vela de cera escura que o Escriba enrola à mão, com uma linha escrita em volta do pavio. Enquanto ela queima, os Levantados das Oliveiras abaixam a cabeça e deixam você passar.", ("Os mortos respeitam quem sabe o nome deles.", "o Escriba")),
    "estilhaco_lacre": ("lasca_da_tabua", "Lasca da Tábua", "Uma lasca de pedra queimada com metade de uma letra que ninguém sabe ler. Esquenta quando alguém mente perto dela.", ("Queimamos o juramento. O fim deu um passo. Eu senti.", "Sariel, Guardiã da Porta")),
    "diapasao_reverso": ("selo_do_coro", "Selo do Coro", "O selo de chumbo que o Coro de Sião pôs na Tábua do Juramento antes de guardá-la. Pesa mais do que deveria.", ("Guardado não é perdoado. É guardado.", "Hulda da Escada")),
    "caldo_cardo_comum": ("cha_de_hissopo", "Chá de Hissopo", "O chá amargo do caldeirão da Zilpa. Purifica, ela diz. Ninguém sabe do quê, mas quem toma levanta mais forte.", ("Purifica-me com hissopo, e ficarei limpo. Ficar limpo dói.", "Zilpa, a Hissopeira")),
    "raiz_cova": ("raiz_de_hissopo", "Raiz de Hissopo", "Raiz branca de hissopo que só nasce onde enterraram alguém. Os Levantados carregam presa nas unhas.", None),
    "lenco_cardo": ("veu_de_zilpa", "Véu Bordado da Zilpa", "Véu de luto bordado com ramos de hissopo, o único que a Zilpa não vendeu. Era do filho dela antes de ser dela.", ("Ele usava para dormir. Agora você usa para não morrer.", "Zilpa, a Hissopeira")),
    "caldo_cardo": ("infusao_de_hissopo", "Infusão de Hissopo", "Uma tigela de barro com o chá mais forte que a Zilpa sabe fazer. Não é para beber.", None, {"uso": "Derramar no Túmulo de Joás, na necrópole do Monte das Oliveiras."}),
    "medalhinha_cardo": ("medalha_de_joas", "Medalha de Joás", "Medalha de latão com o nome JOÁS gravado a prego. Estava presa no pescoço de algo que respondia por esse nome.", None),
    "badalo_de_guerra": ("malho_de_tubal", "Malho de Tubal", "Martelo de forja da Legião, cabo de osso, cabeça feita de elos de corrente fundidos. Tubal martela o seu nome nele antes de entregar.", ("Ferro de Vigilante não enferruja. Só lembra.", "Tubal, o Malho")),
    "ferro_velho": ("elo_de_corrente", "Elo de Corrente", "Elo grosso de corrente antiga, das que prendiam algo grande no fundo da terra. Os fornalheiros levam no cinto como amuleto.", None),
    "mapa_rasgado": ("mapa_de_bartimeu", "Mapa de Bartimeu", "Um mapa desenhado por alguém que nunca viu nada. Os traços são em relevo, feitos com cera derretida. Funciona melhor de olhos fechados.", None),
    "caixinha_musica": ("flauta_de_osso", "Flauta de Osso", "Uma flauta de osso de abutre, rachada. Bartimeu tocava para a mãe quando ainda havia mãe.", None),
    "pa_simao": ("pa_do_escriba", "Pá do Escriba", "Pá curta de cabo gasto, com uma linha de escrita em volta do cabo. O Escriba empresta, mas conta.", None),
    "figo_anacleto": ("pao_de_rispa", "Pão de Rispa", "Pão de cevada assado na fogueira da Rispa, embrulhado em saco. Ela assa um para cada morto que guarda e não come nenhum.", ("Do começo da sega até a chuva. Eu fico.", "Rispa, a Que Vigia")),
    "sebo_rancoso": ("cinza_de_tofete", "Cinza de Tofete", "Cinza gordurosa das fornalhas da Geena. Os porcos de Gadara rolam nela para tirar os espíritos de cima. O Escriba faz velas com ela.", None),
    "chave_gancho": ("chave_de_pa", "Chave de Pã", "Chave de ferro em forma de chifre, presa a um cordão de couro com a palavra PANEAS gravada. Abre a gruta dos Portões do Hades.", ("PANEAS · PORTA DOS QUE DESCEM", "inscrição no cordão")),
    "livro_obitos": ("livro_de_contas_de_tofete", "Livro de Contas de Tofete", "Livro de capa de couro com tudo o que entrou nas fornalhas desde o primeiro dia. Na última página, uma encomenda paga em correntes: PARA O FUNDO DO MONTE.", None),
    "dragonas_general": ("manto_de_ohya", "Manto de Ohya", "Pele costurada de muitos escravos que o gigante usava como manto, cortada para caber num corpo de gente. Ainda está quente do fogo das minas.", ("Sonhei que vinha alguém pequeno. Sonhei errado no tamanho.", "Ohya, o Gigante que Sonhou")),
    "lacre_carne": ("selo_do_sonho", "Selo do Sonho", "O primeiro dos dois selos que trancam a porta do Altar. Estava enrolado no pulso de Ohya. Quem segura, sonha com água subindo.", ("Sonha com água. É o que eles todos sonham.", "Rispa, a Que Vigia")),
    "veu_carpideira": ("veu_de_naama", "Véu de Naamá", "O véu de noiva de Naamá, endurecido de sal e lágrima. Por baixo, o mundo fica sempre um pouco mais quieto.", ("Eles eram grandes. Eram meus.", "Naamá, a Noiva dos Vigilantes")),
    "lacre_lagrimas": ("selo_das_aguas", "Selo das Águas", "O segundo selo da porta do Altar, frio e molhado por dentro como uma concha. Estava debaixo do véu de Naamá.", None),
    "bocal_trombeta": ("tabua_do_juramento", "Tábua do Juramento", "Uma tábua de pedra negra com duzentos nomes e uma frase só, repetida até o fim da pedra. Semyaza a segurava contra o peito.", ("Que o fim fique onde está.", "a frase gravada duzentas vezes")),
    "valvula_radio": ("valvula_da_escuta", "Válvula da Escuta", "Válvula de vidro do posto de escuta, comida pelos chacais junto com o cabo. Ainda acende quando alguém reza perto.", None),
    "leitura_ordem_lancamento": ("leitura_decreto_sexta_hora", "O Decreto da Sexta Hora (cópia)", "Cópia em pergaminho de um decreto do Coro de Sião, com o selo raspado. Hulda diz que é falso. Jael diz que é a letra dela.", None, {"texto": "CORO DE SIÃO · DECRETO DA SEXTA HORA · PRIMEIRO DIA DO JUÍZO\nOs Vigiados resistem. A Cerca segura as cidades. O Juízo não avança.\nPelo bem do Fim, NA SEXTA HORA AFROUXEM-SE AS CORRENTES DOS DUZENTOS que jazem no Hermon.\nQue desçam outra vez sobre os homens, como desceram nos dias de Jarede.\nCopiado pela irmã Jael. Selado pelo Coro. (o selo foi raspado)"}),
    "pagina_ordem": ("pagina_do_decreto", "Página do Decreto", "Página arrancada de um decreto do Coro. Os Levantados dos cedros guardam no peito, como guardariam uma carta.", None),
    "contador_isaura": ("orelha_de_jael", "Orelha de Latão da Jael", "Um fone de latão do posto de escuta, preso num cordão. Estala quando um Vigilante acorda por perto.", ("Eles falam baixo. Quem não escuta acha que é vento.", "Jael, a Escuta")),
    "amostra_amarga": ("agua_de_degelo", "Água de Degelo", "Água cinzenta do degelo do Hermon. Os sapadores a represam para mandar ao deserto. No frasco, ela canta sozinha uma nota baixa.", None),
    "fragmento_clarao": ("elo_partido", "Elo Partido", "Elo de corrente partido de dentro para fora. Estava no pulso de um Vigilante Acorrentado.", None),
    "chave_lancamento": ("astrolabio_de_kokabiel", "Astrolábio de Kokabiel", "Instrumento de latão cheio de estrelas que não existem mais. Kokabiel contava com ele as noites até o fim.", None),
    "estilhaco_absinto": ("estrela_contada", "A Estrela Contada", "A última estrela do astrolábio, solta. Brilha fraco, sempre apontando para o fundo do Hermon.", ("Apaguei a conta. Agora ninguém sabe quantas noites faltam. Nem eles.", "Jael, a Escuta")),
    "chave_segunda_estrela": ("astrolabio_do_coro", "Astrolábio do Coro", "O astrolábio de Kokabiel com o selo do Coro de Sião. Quem o carrega sabe, mais ou menos, quantas noites faltam.", None),
    "insignia_arrancada": ("insignia_da_cerca", "Insígnia da Cerca", "Insígnia de latão da Vigília, com a vela dentro da engrenagem, arrancada de um sapador. Zaqueu paga bem por elas.", None),
    "carta_apostata": ("carta_do_sineiro", "Carta do Sineiro", "Carta da Vigília, cifrada. Zaqueu leu em dez minutos: fala de veneno, de um cálice e de um nome do Coro.", None),
    "divisa_legiao": ("divisa_da_geena", "Divisa da Geena", "A divisa da Legião Blasfema bordada com fio de brasa, como a usavam os que juraram ao general. Tubal tirou do trono vazio.", ("O trono está vazio. A divisa, não.", "Tubal, o Malho")),
    "meia_dragona": ("coroa_partida", "Coroa de Ferro Partida", "Metade de uma coroa de ferro presa nas correntes do Trono da Geena. A outra metade ninguém sabe onde está.", None),
    "placa_coveiro": ("tabuinha_de_argila", "Tabuinha de Argila", "Tabuinha de argila com escrita muito antiga. Três delas, juntas, dizem um nome: HNWK.", None),
    "leitura_livro_tombo": ("leitura_livro_de_henoc", "O Livro do Escriba (folha primeira)", "A primeira folha de um livro muito velho, copiada à mão muitas vezes. Fala de duzentos que desceram num monte e de um escriba que escreveu o pedido deles.", None, {"texto": "LIVRO DO ESCRIBA · FOLHA PRIMEIRA\nE aconteceu que nos dias de Jarede desceram duzentos sobre o cume do Hermon, e juraram, e se amarraram por maldição.\nE tomaram mulheres, e as mulheres pariram gigantes, e os gigantes comeram tudo, e depois comeram os homens.\nE os duzentos me pediram que eu escrevesse o pedido deles ao Altíssimo, porque eles já não podiam levantar os olhos.\nEu escrevi. Não foi atendido.\n(A mesma letra, em tinta mais nova, na margem:) Ainda não foi."}),
    "folha_tombo": ("folha_do_livro", "Folha do Livro", "Folha solta de um livro escrito por uma mão só, sempre a mesma, em séculos diferentes.", None),
    "ultimo_tijolo": ("ultima_linha", "A Última Linha", "Uma tira de couro com uma única linha escrita, arrancada de um Escriba Emparedado. É a mesma letra das tabuinhas.", None),
    "faixas_betania": ("pena_do_escriba", "Pena do Escriba", "Uma pena de escrever cinzenta, mais leve que deveria. O Escriba deu sem dizer de que ave era.", None),
    "elmo_rafael": ("diadema_do_escriba", "Diadema do Escriba", "Diadema de bronze escurecido com uma única linha gravada em volta, numa letra mais velha que o dilúvio. O Escriba usou quando andou com Deus. Quando voltou, guardou numa caixa.", ("Andou com Deus e já não era. Depois voltou, porque o fim travou.", "Livro do Escriba, última folha")),
    "eco_do_nome": ("nome_verdadeiro", "O Nome Verdadeiro", "Um som preso num frasco de barro: alguém dizendo um nome muito antigo. Os Ecos do Juramento repetem esse nome entre os duzentos.", None),
    "badalo_rachado": ("elo_de_vigilante", "Elo de Vigilante", "Um elo de corrente do tamanho de uma mão aberta, que Tubal tirou das fornalhas e não teve coragem de derreter. Pesa como uma criança dormindo.", None),
    "escopeta_badalada": ("lanca_da_porta", "Lança da Porta Dourada", "Lança de anjo com a ponta forjada de um elo de Vigilante. Cada golpe soa como uma corrente batendo em pedra.", ("Ferro que prendeu anjo serve na mão de anjo.", "Tubal, o Malho"), {"classe": ["anjo"]}),
    "machado_bonde": ("cutelo_de_tofete", "Cutelo de Tofete", "Cutelo largo de fornalheiro, cabo de corrente enrolada e lâmina feita de três elos batidos. Ainda cheira a Geena.", ("Corta como fornalha: devagar e de uma vez.", "Tubal, o Malho"), {"classe": ["demonio"]}),
    "cajado_lampiao": ("cetro_de_brasa", "Cetro de Brasa", "Cetro de ferro com uma brasa da fornalha de Tofete presa numa gaiola de elos. O cultista paga com o próprio sangue para ela não apagar.", ("Fogo da Geena na mão de quem reza. Que mal tem?", "Tubal, o Malho"), {"classe": ["cultista"]}),
    "leitura_mapa_tobias": ("leitura_mapa_bartimeu", "Mapa de Bartimeu", None, None, {"texto": "(em relevo de cera, para ler com o dedo)\nX 1: no olival, perto da pedra que sobe. Debaixo da pedra que balança.\nX 2: no bosque, no tronco oco perto da cabana do Escriba (ele finge que não ouve).\nX 3: na cidade de baixo, perto de Siloé. Trancado. Chama alguém forte.\nSe não achar, fecha o olho e tenta de novo. O que achar é seu, mas a flauta é MINHA. — B."}),
    "leitura_obitos": ("leitura_contas_de_tofete", "Contas de Tofete", None, None, {"texto": "Ano 1: 40 carroças de mortos, 3 de lenha.\nAno 9: 12 carroças de mortos. Pouca lenha. Os porcos comem o resto.\nAno 30: 2 carroças. O fogo não apaga mesmo assim.\nEncomenda paga em correntes, entregue na gruta de Pã: 600 elos.\nPARA O FUNDO DO MONTE. Quem paga não assina. Quem entrega não volta."}),
    "leitura_carta_apostata": ("leitura_carta_do_sineiro", "Carta do Sineiro (decifrada)", None, None, {"texto": "Irmão, o sino rachado avisa a hora.\nNa missa da sexta hora o Coro bebe do cálice de Sião.\nO veneno já está na adega, misturado ao vinho das oliveiras.\nQuem nos vende é do Coro e tem nome de anjo. Não confie no cobrador.\nEnquanto houver vela, não é noite. — S."}),
    "leitura_anselmo": ("leitura_hulda", "Diário da Hulda", None, None, {"texto": "Primeira noite. A Brasa ia apagar. Juntei o óleo de todas as lamparinas da cidade.\nSegunda noite. O Coro me mandou copiar um decreto. Copiei. Não li.\nTerceira noite. Li. NA SEXTA HORA, AFROUXEM-SE AS CORRENTES. Era a letra da Jael, não a minha. A ordem era do Coro.\nNão contei a ninguém. Se o fim travou, uma parte da trava fomos nós."}),
    "leitura_confissao_anacleto": ("leitura_juramento_noivas", "Votos na Parede", None, None, {"texto": "Riscado na pedra, com unha:\nEu, filha de homem, tomo por marido um dos duzentos.\nEle me ensinou as ervas e as raízes. Me ensinou a ler o céu.\nMeus filhos cresceram até o teto. Depois veio a água.\nNão me arrependo dele. Me arrependo de ter ensinado meus filhos a ter fome."}),
    "leitura_hino_carpideiras": ("leitura_canto_das_noivas", "Canto das Noivas", None, None, {"texto": "Grandes eram, grandes eram,\nos meninos que eu pari.\nA água subiu até a boca,\ne a boca deles não cabia aqui.\nCanta, irmã, o nome deles,\nque o céu não escreveu.\nCanta mais alto que a chuva:\no que é grande também morreu."}),
    "leitura_ordem_zacarias": ("leitura_juramento_duzentos", "O Juramento dos Duzentos (cópia)", None, None, {"texto": "Juramos no Hermon, nos dias de Jarede, e nos amarramos por maldição.\nJuramos de novo no dia do primeiro toque, com as correntes abertas pelo Coro:\nQUE O FIM FIQUE ONDE ESTÁ.\nSe o mundo acabar, voltamos ao fundo. Se o mundo não acabar, ficamos.\nAssinam: Semyaza e cento e noventa e nove."}),
}
GENERICOS = {"pao_duro", "agua_doce", "agua_benta_polvora", "livro_dos_vencidos"}

# ============================================================================ textos das missões
# id -> título, resumo, descrição (documento com cabeçalho e assinatura), texto de conclusão, fala da oferta, fala da entrega, [textos das escolhas]
T = {}
def m(i, titulo, resumo, desc, concl, oferta, fim, escolhas=None): T[i] = (titulo, resumo, desc, concl, oferta, fim, escolhas or [])

m("j01", "Os Que Ainda Rezam", "Derrube os Peregrinos Ressecados no Getsêmani.",
  "ORDEM DA PORTA DOURADA · Nº 1 · ANO 31 DO JUÍZO ADIADO\nAo irmão sem nome. Apresente-se à Porta Dourada.\nOs Peregrinos que vieram ver o fim ainda cavam o Getsêmani atrás de relíquias. Arranham as oliveiras, arranham a muralha. Seis deles. Derrube-os antes da sexta hora.\nNão reze por eles. Eles já rezaram demais.\n— Sariel, Guardiã da Porta",
  "Sariel amarrou a Fita do Juízo no seu pulso com um nó que ninguém sabe desfazer. \"Quem esquece, sangra\", disse. Depois escreveu o seu nome no batente da Porta Dourada, junto de muitos outros riscados.",
  "Escuta. Unha na pedra. São os Peregrinos do Getsêmani: vieram de todo canto para ver o fim e ficaram vendo. Seis deles abrem uma brecha no olival. Derrube os seis. Se voltar, eu escrevo o seu nome no batente.",
  "Seis. Vi da muralha. Você bate como quem pede desculpa, mas bate. Tome a fita. Agora vá à Hulda, perto da Brasa. Quando a Brasa baixa, eu não durmo.")
m("j02", "Azeite para a Brasa", "Traga azeite do lagar para a Brasa do Altar.",
  "ANOTAÇÃO DA ESCADA · FOLHA 3\nA Brasa do Altar comeu o último óleo da cisterna. Ela não apaga, mas baixa, e quando baixa os Levantados chegam mais perto da muralha. Os abutres do Hermon furam os odres dos peregrinos caídos e levam o azeite para os ninhos. Cinco odres.\n— Hulda da Escada",
  "Hulda despejou o azeite numa concha de bronze e a Brasa subiu meio palmo. \"Foi uma brasa como esta que tocou a boca do profeta\", disse. \"Ele parou de gaguejar. Você ainda gagueja.\"",
  "Cuidado com a Brasa, ela morde. Está baixa. Os abutres levam os odres de azeite dos peregrinos para os ninhos nas oliveiras. Cinco odres, e ela volta a subir.",
  "Cheiro de oliva. Bom. A Brasa vai comer tudo e pedir mais, como todo fogo santo. Volte à Sariel: ela tem serviço de dente e unha.")
m("j03", "Os Chacais de Josafá", "Mate os chacais que descem do Vale de Josafá.",
  "ORDEM DA PORTA DOURADA · Nº 3\nA matilha do Cedrom subiu de novo até a Porta do Esterco. Oito chacais. No vale onde todas as nações serão julgadas, quem come os ossos são eles. Por enquanto.\n— Sariel, Guardiã da Porta",
  "Sariel contou os dentes que você trouxe e jogou todos no fogo. \"No Juízo, até os chacais vão dar conta\", disse. \"Hoje, quem dá conta é você.\"",
  "O vale de Josafá é onde o Senhor vai julgar as nações. Enquanto Ele não vem, os chacais julgam primeiro. Oito deles rondam a Porta do Esterco. Desça ao Cedrom.",
  "O vale está mais quieto. Não confunda quieto com limpo. A Hulda quer falar com você, e o Escriba lá do bosque também anda perguntando por gente de pé.")
m("j04", "Os Que Levantaram Primeiro", "Abata Levantados das Oliveiras, examine os peregrinos ajoelhados e fale com o Escriba.",
  "ORDEM DA PORTA DOURADA · Nº 4\nOs mortos do Monte das Oliveiras levantaram primeiro, como a tradição prometia. Levantaram e ninguém os chamou. Abata seis. Veja três peregrinos ajoelhados na necrópole e me diga se ainda respiram. Depois procure o Escriba no Bosque do Hissopo: ele conta os mortos daqui desde antes de mim.\n— Sariel, Guardiã da Porta",
  "O Escriba anotou os seis num livro de folhas soltas e te deu uma vela de cera escura. \"Os mortos respeitam quem sabe o nome deles\", disse, e voltou a escrever antes que você perguntasse o dele.",
  "Os Levantados das Oliveiras são os mais velhos de todos. Estão na fila há trinta e um anos. Abata seis, veja os peregrinos ajoelhados e procure o Escriba. Ele sabe coisas que eu não quero saber.",
  "(o Escriba não levanta os olhos do livro) Seis. Escrevi. Quantos nomes você sabe dos que derrubou? Nenhum. Tome esta vela. Com ela acesa, eles abaixam a cabeça. Aprenda os nomes, e eles vão parar de levantar.")
m("j05", "O Destino da Tábua", "Decida o que fazer com a Tábua do Juramento.",
  "ORDEM DA PORTA DOURADA · SEM NÚMERO\nVocê desceu ao Fosso e trouxe a Tábua de Semyaza. Duzentos nomes e uma frase: que o fim fique onde está. Hulda quer selar a Tábua para o Coro. Eu quero queimá-la na Brasa. Você trouxe. Você escolhe.\n— Sariel, Guardiã da Porta",
  "A escolha foi registrada no batente da Porta Dourada, ao lado do seu nome.",
  "Você trouxe a Tábua. Eu não encosto nela. Leve à Hulda, perto da Brasa. Ela vai dizer o que o Coro quer. Eu vou dizer o que eu quero. Você decide.",
  "(Hulda segura a Tábua com um pano) Duzentos nomes jurando contra o fim. Queimar devolve um passo ao fim, a Sariel diz. Selar dá ao Coro uma corrente para puxar os Vigilantes de novo. Os dois são pecado. Escolha o seu.",
  ["Queimar a Tábua na Brasa do Altar (Sariel)", "Selar a Tábua para o Coro de Sião (Hulda)"])
m("js01", "Hissopo de Cova", "Traga raízes de hissopo para a Zilpa.",
  "RECEITA DA ZILPA (escrita no avesso de uma oração)\nHissopo de cova: só o que nasce em cima de enterro. Os Levantados das Oliveiras trazem preso nas unhas, de tanto cavar. Quatro raízes. Lavar em água de degelo. Não cheirar.",
  "Zilpa jogou as raízes no caldeirão e ficou um tempo olhando o vapor, como quem espera alguém aparecer nele.",
  "Purifica-me com hissopo, diz o salmo. Não diz que o hissopo bom nasce em cima de morto. Os Levantados trazem nas unhas. Quatro raízes, criança.",
  "Raiz boa. Branca. Cheira a chuva. Toma um chá. Não pergunta do que é.")
m("js02", "Chá para Joás", "Leve a infusão da Zilpa ao túmulo do filho dela.",
  "BILHETE DA ZILPA (dobrado em quatro)\nO meu Joás está enterrado na necrópole, debaixo da cruz celta torta. Ele levantou com os outros e não veio para casa. Leve o chá e derrame na pedra. Se ele vier, não deixe ele sofrer. Traga a medalha.",
  "Zilpa pegou a medalha, fechou a mão e não abriu mais naquela noite. De manhã te deu o véu bordado sem dizer nada.",
  "O meu menino está na necrópole. Levantou e não voltou. Esse chá ele tomava quando tinha febre. Derrama na pedra dele. O que vier... não deixa sofrer.",
  "(ela pega a medalha e aperta) Joás. Era ele? Não diz. Toma o véu. Era dele antes de ser meu.")
m("js03", "Correntes Viram Lâminas", "Traga elos de corrente para a forja do Tubal.",
  "ENCOMENDA DA FORJA DE TUBAL\nSeis elos das correntes antigas que os fornalheiros de Tofete usam no cinto. Ferro que prendeu Vigilante não quebra. Depois, aqueça os elos na fornalha de Tofete, a grande, e traga de volta.\n— Tubal, o Malho (assina com um X em brasa)",
  "Tubal bateu os elos até virarem cabeça de martelo. \"O ferro lembra o que prendeu\", disse, e gravou o seu nome no cabo.",
  "Quero ferro velho. Velho mesmo, do fundo do monte. Os fornalheiros da Geena usam os elos como amuleto. Seis. Depois esquenta na fornalha grande de Tofete. Fogo de casa, entende?",
  "(Tubal cheira o metal) Ferro de Vigilante. Ainda ouve. Toma o malho. E isto aqui, para quando a coisa piorar.")
m("js04", "Os Tesouros do Bartimeu", "Ache os três esconderijos do Bartimeu.",
  "MAPA DE BARTIMEU (em relevo de cera)\nTrês esconderijos. Um no olival, perto da pedra que sobe. Um no bosque do Escriba. Um na cidade de baixo, trancado. A flauta está num deles. Os outros são seus.",
  "Bartimeu passou o dedo na flauta, achou a rachadura e sorriu. \"Ainda toca torto. Como eu.\"",
  "Eu sou cego, não sou bobo. Escondi minhas coisas em três lugares e agora não acho nenhum, que ironia. Toma o mapa. É em relevo. Fecha o olho que fica mais fácil.",
  "A minha flauta! Rachada, mas minha. O resto é seu. Bartimeu paga bem quando ninguém está olhando, e ninguém está.")
m("jr01", "Ronda da Muralha", "Limpe o Getsêmani para a ronda da noite.",
  "ORDEM DA PORTA DOURADA · RONDA\nDez Peregrinos, cinco abutres. Toda noite. Até o fim terminar.\n— Sariel",
  "Sariel marcou mais um risco no batente. Os riscos já dão a volta na porta.",
  "Ronda de hoje. Dez Peregrinos, cinco abutres no olival. Amanhã de novo.",
  "Muralha limpa. Toma um chá da Zilpa e volte amanhã.")
m("js08", "Túmulos Abertos", "Feche os túmulos dos profetas que o vento descobriu.",
  "CADERNO DO ESCRIBA · FOLHA SOLTA\nO vento de cinza descobre os túmulos dos profetas toda noite. Quando um profeta fica à vista, os Levantados vêm ouvir. Cinco túmulos. A pá é minha. Devolva.",
  "O Escriba conferiu a pá, contou as pazadas pelo barro na lâmina e anotou.",
  "Os túmulos dos profetas estão abertos de novo. Feche cinco. Quando um profeta fica à vista, os mortos esperam que ele fale. Não fala mais.",
  "Cinco. Bom. Os profetas dormem. Os vivos não, mas isso não é comigo.")
m("js09", "As Noivas Emparedadas", "Leia os nichos das noivas no Salão.",
  "VIGÍLIA DE RISPA (riscado a carvão numa tábua)\nNo salão do fundo tem nichos com mulheres de pedra. Cada uma escreveu o nome do marido do céu. Leia cinco e me diga os nomes. Alguém tem que guardar.",
  "Rispa repetiu os nomes em voz baixa, um por um, e jogou uma pedra na fogueira para cada.",
  "Lá embaixo, onde a Naamá chorava, tem nichos com as outras noivas. Cada uma deixou escrito com quem casou. Leia cinco para mim. Eu guardo.",
  "Cinco nomes de anjo e cinco nomes de mulher. Ninguém mais lembra de nenhum. Eu lembro. Toma o pão.")
m("jc01", "Velas para os Mortos", "Traga cinza de Tofete para as velas do Escriba.",
  "CADERNO DO ESCRIBA · FOLHA 40\nPreciso de seis punhados de cinza gorda das fornalhas. Os porcos de Gadara rolam nela; quando morrem, ela fica no couro. Com cinza de Tofete a vela não apaga no fundo do monte.",
  "O Escriba enrolou seis velas na mesma noite e escreveu uma linha em volta de cada pavio. \"Para o que tem lá embaixo\", disse.",
  "Você vai descer ao fundo do Hermon. Todo mundo que fica aqui desce um dia. Lá embaixo vela comum apaga. Traga cinza de Tofete, a que os porcos de Gadara carregam no couro.",
  "Seis. Faço as velas hoje. Agora escute: debaixo das Fontes do Jordão tem uma gruta que os antigos chamavam de Portões do Hades. A chave está com o capataz das fornalhas.")
m("jc02", "O Livro de Contas", "Tome a chave do Capataz de Tofete e o livro da mesa dele.",
  "CADERNO DO ESCRIBA · FOLHA 41\nO Capataz de Tofete guarda a Chave de Pã desde que o general sumiu. Os fornalheiros não deixam ninguém chegar. Derrube oito, derrube o Capataz, pegue a chave e o livro de contas da mesa dele.",
  "O Escriba leu a última página do livro e fechou devagar. PARA O FUNDO DO MONTE. \"Alguém lá embaixo encomenda correntes\", disse.",
  "A chave dos Portões do Hades está no cinto do Capataz de Tofete. E na mesa dele tem um livro de contas. Eu quero o livro. Você fica com a chave.",
  "PARA O FUNDO DO MONTE, pago em correntes. A Legião vende ferro para alguém que está preso. Use a chave. Desça.")
m("jc03", "Os Portões do Hades", "Abra a gruta de Pã e desça ao Fosso dos Vigilantes.",
  "CADERNO DO ESCRIBA · FOLHA 42\nNa gruta de Pã, nas Fontes do Jordão, um homem disse uma vez que as portas do Hades não prevaleceriam. Não disse que não existiam. Abra. Desça.",
  "A porta de pedra se abriu para dentro e o ar que subiu era quente, como respiração de bicho grande dormindo.",
  "A gruta fica nas Fontes do Jordão, atrás das estátuas sem cabeça. A chave entra no chifre. Desça, e acenda a minha vela quando a escada acabar.",
  "")
m("jc04", "O Gigante que Sonhou", "Derrote Ohya nas Minas dos Gigantes.",
  "CADERNO DO ESCRIBA · FOLHA 43 (escrita depois)\nOhya, filho de Semyaza, sonhou com o dilúvio antes de todos e se escondeu no fundo do monte para não afogar. Comeu os escravos que cavavam para ele. Leva no pulso o primeiro selo do Altar.",
  "Ohya caiu sentado, como quem acorda de um sonho ruim. O Selo do Sonho estava enrolado no pulso dele, molhado.",
  "", "")
m("jc05", "Silêncio no Salão das Noivas", "Derrote Naamá, a Noiva dos Vigilantes.",
  "VIGÍLIA DE RISPA\nTem uma mulher lá embaixo que chora os filhos há mais tempo que eu. Ela se chama Naamá. Faz as outras cantarem o nome dos meninos. Faça ela parar. Debaixo do véu tem o segundo selo.",
  "Quando o canto parou, o salão inteiro ficou mais leve. O Selo das Águas estava debaixo do véu, frio como concha.",
  "Eu conheço choro de mãe. O dela já virou outra coisa. Desça ao Salão das Noivas e cale a Naamá. O segundo selo está com ela.",
  "Calou? Que ela descanse. Ninguém descansou por mim, mas que ela descanse. Toma o véu. Você vai precisar de silêncio lá no fundo.")
m("jc06", "O Primeiro Juramento", "Abra o Altar, derrote Semyaza e leve a Tábua ao Escriba.",
  "VIGÍLIA DE RISPA\nOs dois selos abrem o Altar do Juramento. Lá está Semyaza, o primeiro dos duzentos. Ele jurou no Hermon antes do dilúvio, e agora jura de novo: que o fim fique onde está. Derrube o juramento. Traga a Tábua ao Escriba.",
  "O Escriba passou a mão sobre os duzentos nomes sem encostar. \"Eu escrevi o pedido deles uma vez\", disse. \"Não foi atendido. Este também não vai ser.\"",
  "Os dois selos abrem a porta do Altar. Semyaza está lá, jurando de novo com os duzentos. Enquanto ele jurar, o fim não anda. Derrube ele e leve a Tábua ao Escriba.",
  "(o Escriba olha a Tábua um tempo longo) Duzentos nomes. Eu conheço a letra de todos. Leve à Sariel. Ela vai querer queimar. Eu não vou dizer o que eu faria.")
m("jd01", "Vozes na Estática", "Limpe as Escadas de Siloé e procure a Jael no Posto de Escuta.",
  "ANOTAÇÃO DA ESCADA · FOLHA 9\nO posto de escuta do Hermon voltou a falar. A voz é da Jael, uma irmã do Coro que subiu sozinha e não desceu. Ela diz ouvir nomes na estática. Limpe o caminho por Siloé e vá até ela.\n— Hulda da Escada",
  "Jael tirou o fone de latão do ouvido e te ofereceu, sem dizer nada. Na estática, alguém contava: um, dois, três... até duzentos, e começava de novo.",
  "Tem uma irmã no posto de escuta do Hermon, a Jael. Ela diz que ouve os Vigilantes contando. O Coro diz que ela enlouqueceu. Limpe as Escadas de Siloé e suba até ela.",
  "(Jael, sem tirar o fone) Duzentos. Eles contam até duzentos e começam de novo. Toda noite. Alguém ensinou a eles que o fim é uma conta. Fica. Preciso de mãos.")
m("jd02", "A Antena no Cedro", "Recupere válvulas dos chacais e conserte a antena da Escuta.",
  "BILHETE DA JAEL (caneta de pena, letra apertada)\nOs chacais roeram o cabo e levaram as válvulas para a toca. Cinco válvulas. Troque na antena, a do poste de telégrafo. Quero ouvir mais longe que o Hermon.",
  "A antena estalou e, por um instante, toda a encosta ouviu a contagem: duzentos, e de novo.",
  "Os chacais de Josafá levaram as minhas válvulas para o covil. Sem elas eu só escuto o Hermon. Com elas, escuto o que está debaixo dele.",
  "Agora sim. Escuta. Não é só contagem. Tem uma ordem. Alguém mandou soltar eles. Alguém do Coro.")
m("jd03", "O Decreto da Sexta Hora", "Recupere as páginas do decreto com os Levantados dos cedros.",
  "BILHETE DA JAEL\nOs Levantados dos cedros carregam papéis no peito. Quatro deles têm páginas de um decreto do Coro, o da Sexta Hora. Traga. Eu preciso saber se é a minha letra.",
  "Jael juntou as páginas e leu em voz alta: NA SEXTA HORA DO PRIMEIRO DIA, AFROUXEM-SE AS CORRENTES DOS DUZENTOS. Assinado pelo Coro de Sião. A letra era dela.",
  "Nos Cedros Partidos, os Levantados carregam papel no peito como quem carrega carta de amor. Quatro páginas de um decreto. Traga.",
  "(ela lê e fica branca) É a minha letra. Eu copiei este decreto no primeiro dia. O Coro mandou soltar os Vigilantes para ganhar a guerra. E eles juraram de novo.")
m("jd04", "O Que a Água Canta", "Colha água de degelo nas fontes que os sapadores secaram.",
  "BILHETE DA JAEL\nOs sapadores da Vigília represaram as Fontes do Jordão. Onde a água parou, ela canta uma nota baixa. Três frascos. Quero saber que nota é essa.",
  "No posto de escuta, os três frascos cantaram juntos. Era a mesma nota da contagem: os Vigilantes estavam debaixo da água também.",
  "Os sapadores secaram três fontes no canteiro deles. A água parada canta. Traga três frascos e o que os sapadores tiverem no bolso.",
  "A mesma nota. Eles estão debaixo de tudo, até da água. Tome o fone. Quando ele estalar, um deles acordou perto de você.")
m("jd05", "As Correntes Partidas", "Recolha elos partidos dos Vigilantes Acorrentados no cume.",
  "BILHETE DA JAEL\nNo cume, na Neve de Cinza, os Vigilantes Acorrentados guardam as pegadas do juramento. As correntes deles quebraram de dentro para fora. Traga cinco elos. Quero saber quem afrouxou.",
  "Todos os cinco elos tinham a mesma marca: o selo do Coro, batido a frio, por dentro.",
  "As correntes dos Vigilantes não quebraram. Foram abertas. Suba à Neve de Cinza e traga cinco elos. Se eu estiver certa, tem um selo dentro.",
  "O selo do Coro. Por dentro. Não foi o Juízo que soltou eles. Fomos nós. Falta uma coisa: a laje onde eles juraram.")
m("jd06", "A Conta das Noites", "Abra a Laje do Juramento, derrote Kokabiel e decida o destino do astrolábio.",
  "BILHETE DA JAEL (o último)\nNa Laje do Juramento, no cume, Kokabiel conta as noites que faltam para o fim terminar. Se ninguém contar, o fim não sabe quando chegar. Pegue o astrolábio dele. Depois decidimos.",
  "A escolha foi feita. No posto de escuta, a contagem continuou. Ou parou. Depende de quem escuta.",
  "Kokabiel ensinou os homens a ler as estrelas. Agora ele conta as noites até o fim, e o fim espera a conta acabar. Abra a laje. Pegue o astrolábio.",
  "(Jael segura o astrolábio) Se eu apago a conta, ninguém sabe quantas noites faltam. Nem eles, nem nós. Se o Coro fica com ela, o Coro decide quando o mundo acaba. O que eu faço?",
  ["Apagar a conta das noites para sempre", "Levar o astrolábio para o Coro de Sião"])
m("je01", "Os Estandartes da Geena", "Limpe o Getsêmani, examine os estandartes da Legião e procure o Zaqueu.",
  "RECADO DA FORJA DE TUBAL\nTrês estandartes da Legião caíram na Geena e ninguém levantou. Quando estandarte cai e ninguém levanta, é porque ninguém manda. Veja os três. Depois fale com o Zaqueu, o cobrador. Ele sabe quem deve o quê a quem.\n— Tubal",
  "Zaqueu ouviu tudo sentado num degrau, com o livro de dívidas no colo. \"Estandarte caído é dívida sem dono\", disse. \"Eu gosto de dívida sem dono.\"",
  "Na Geena, três estandartes da Legião estão no chão. Ninguém levanta. Vai ver, e passa no Zaqueu. Limpe o Getsêmani no caminho, que os peregrinos atrapalham.",
  "(Zaqueu, sem levantar do degrau) A Legião está sem general e o trono da Geena está vazio. Quem senta primeiro, manda. Quer saber quem está pagando para sentar?")
m("je02", "Insígnias da Cerca", "Arranque insígnias dos sapadores da Vigília.",
  "LIVRO DE DÍVIDAS DE ZAQUEU · PÁGINA 77\nOs sapadores da Cerca nas Fontes do Jordão estão sendo pagos com ferro da Legião. Cinco insígnias provam. Eu cobro de quem pagou.",
  "Zaqueu enfileirou as insígnias e anotou um nome ao lado de cada uma. Nenhum era da Vigília.",
  "Tem sapador da Vigília represando o Jordão com ferramenta da Geena. Alguém da Legião está vendendo para o inimigo. Cinco insígnias e eu te digo quem.",
  "Ferramenta da Geena, mão da Vigília, e um demônio no meio cobrando. Que bonito. Fica de olho nos Sineiros: eles carregam as cartas.")
m("je03", "Veneno no Cálice", "Tome a carta do Sineiro e decida a quem avisar.",
  "LIVRO DE DÍVIDAS DE ZAQUEU · PÁGINA 78\nOs Sineiros dos cedros carregam uma carta cifrada. Fala de um cálice envenenado no altar do Coro. Traga a carta. A dívida é de quem souber primeiro.",
  "A escolha foi anotada no livro de Zaqueu, numa coluna que só ele entende.",
  "Os Sineiros dos Cedros Partidos carregam uma carta sobre um cálice. Traga. Depois a gente decide quem fica devendo a quem.",
  "Veneno no cálice do Coro, na missa da sexta hora. Quem fica devendo? Os anjos, se você avisar. Os demônios, se você mostrar ao Tubal. Ou ninguém, se ninguém souber.",
  ["Avisar a Sariel do veneno (os anjos ficam devendo)", "Mostrar a carta ao Tubal (os demônios ficam devendo)", "Deixar o veneno chegar ao cálice e ver o que acontece"])
m("je04", "O Trono Vazio", "Examine o Trono da Geena e traga a coroa partida.",
  "LIVRO DE DÍVIDAS DE ZAQUEU · PÁGINA 79\nNo Trono da Geena, nas Fornalhas de Tofete, alguém deixou metade de uma coroa presa nas correntes. Atravesse a Fenda das Oliveiras, onde os sapadores cavam, e traga a coroa.",
  "Tubal pegou a meia coroa, mediu na própria cabeça e devolveu. \"Não serve em mim. Serve em quem só tem meio corpo.\"",
  "O trono da Geena tem meia coroa presa nas correntes. Atravesse a Fenda, que está cheia de sapadores, e traga. Leve ao Tubal. Ele conhece ferro de general.",
  "Meia coroa. Do Andras. O general que o bonde partiu. Se a coroa está aqui partida, ele também está em algum lugar partido. E vivo. Toma a divisa. Era dele.")
m("je05", "Rastro de Brasa", "Siga o rastro de brasa até a Pocilga de Gadara e decida o que fazer com o segredo.",
  "RECADO DA FORJA DE TUBAL\nNa Pocilga de Gadara tem rastro de brasa, de alguém que se arrasta sem pernas. Os porcos estão inquietos. Siga o rastro. Depois me diga se eu conto para a Legião.",
  "A escolha foi feita. Na forja, Tubal martelou até o sol nascer.",
  "Os porcos de Gadara não dormem. Tem rastro de brasa entre eles, de alguém que se arrasta. Siga e volte. E não conte a ninguém antes de mim.",
  "(Tubal limpa as mãos) Arrasto de general. Vivo, debaixo da terra do deserto, no fosso do Carniça. A Legião está brigando por um trono que ainda tem dono. O que eu faço com isso?",
  ["Contar à Legião que o general está vivo", "Guardar o segredo para os Arautos usarem depois"])
m("jf01", "Tabuinhas de Argila", "Recolha tabuinhas de argila dos Peregrinos no Getsêmani.",
  "RECEITA DA ZILPA (verso)\nOs Peregrinos do Getsêmani carregam tabuinhas de argila que acham cavando. Três delas, juntas, dizem um nome. Eu quero saber que nome. Não conte ao Escriba.",
  "Zilpa juntou as três tabuinhas e leu devagar, letra por letra: H... N... W... K. \"É um nome sem vogal\", disse. \"Nome de quem não quer ser chamado.\"",
  "Os Peregrinos acham tabuinhas de argila no Getsêmani. Três juntas dizem um nome. Traga. E não conte ao Escriba.",
  "HNWK. Nome sem vogal. Eu já vi essa letra. No livro do Escriba, na cabana dele. Ele escreve com a mesma mão.")
m("jf02", "A Pedra que Sobe", "Abra caminho pela necrópole e examine a Pedra da Ascensão.",
  "LIVRO DE DÍVIDAS DE ZAQUEU · PÁGINA 12\nNo Monte das Oliveiras tem uma pedra com uma pegada. Dizem que alguém subiu dali para o céu. Eu digo que alguém deve explicações. Abra caminho pela necrópole e veja a pedra.",
  "Na pedra havia duas pegadas, não uma. A segunda era mais antiga, e alguém tinha escrito do lado, em argila: AQUI EU SUBI. AQUI EU VOLTEI.",
  "Tem uma pedra no olival com pegadas de quem subiu ao céu. Uma é famosa. A outra ninguém comenta. Vá ver, mas limpe a necrópole antes, que os Levantados estão na fila.",
  "Duas pegadas. Uma subiu e não voltou. A outra subiu e voltou. Eu cobro de quem volta. Procure as folhas do livro dessa pessoa.")
m("jf03", "As Folhas do Livro", "Leia os rolos da escada e recupere folhas do livro com os abutres.",
  "LIVRO DE DÍVIDAS DE ZAQUEU · PÁGINA 13\nNos rolos da Hulda, perto da Cúpula, tem um livro velho copiado mil vezes. A folha primeira está lá. As outras, os abutres levaram. Cinco folhas.",
  "As folhas eram todas da mesma mão. Não parecida: a mesma. Em pergaminho, em papiro, em papel de jornal.",
  "Leia os rolos da escada e cace cinco folhas com os abutres. Quero ver a mesma letra em séculos diferentes.",
  "Mesma letra. Em pergaminho e em papel de jornal. Alguém escreve este livro há tempo demais. Fale com a Rispa. Ela conhece quem não morre.")
m("jf04", "A Última Linha", "Derrube Escribas Emparedados e traga a última linha.",
  "VIGÍLIA DE RISPA\nNo Salão das Noivas tem escribas emparedados com os ensinamentos que copiavam. Um deles tem a última linha do livro. Derrube oito. Traga a linha.",
  "A linha dizia: E ELE ANDOU COM DEUS, E JÁ NÃO ERA. E DEPOIS VOLTOU, PORQUE O FIM TRAVOU. A letra era a das tabuinhas.",
  "Os Escribas Emparedados copiavam o que os Vigilantes ensinavam. Um deles guardou a última linha de um livro que não devia ter fim. Traga.",
  "Andou com Deus e já não era. Depois voltou. Eu sei de quem é. Vá ao Escriba. Leve a vela dele.")
m("jf05", "Ele Andou com Deus", "Acenda a vela no túmulo vazio e fale com o Escriba.",
  "VIGÍLIA DE RISPA\nNa necrópole tem um túmulo vazio, preparado há muito tempo para alguém que nunca morreu. Acenda a vela do Escriba lá. Depois vá até ele.",
  "A escolha foi feita. O Escriba voltou a escrever, um pouco mais devagar.",
  "Tem um túmulo vazio na necrópole. Ninguém nunca deitou nele. Acenda esta vela lá e depois fale com o Escriba. Ele vai saber que você sabe.",
  "(o Escriba larga a pena pela primeira vez) Eu escrevi o pedido dos duzentos ao Altíssimo, antes do dilúvio. Não foi atendido. Depois andei com Ele, e não fui mais. Quando o fim travou, me mandaram de volta para escrever a sentença deles. Ainda não terminei. O que você quer fazer com isso?",
  ["Guardar o segredo dele", "Perguntar o que ele vai escrever quando o fim terminar", "Contar ao Coro quem ele é"])
m("jf06", "O Nome Verdadeiro", "Recolha o nome que os Ecos do Juramento repetem e leve ao Escriba.",
  "VIGÍLIA DE RISPA\nNo Altar do Juramento, os Ecos repetem um nome entre os duzentos. Não é nome de Vigilante. É o nome de quem escreveu por eles. Traga o nome para o dono.",
  "O Escriba ouviu o próprio nome no frasco de barro e fechou os olhos. \"Henoc\", disse. \"Faz tempo que ninguém me chama. Toma o diadema. Eu não vou mais precisar de andar com ninguém.\"",
  "Os Ecos do Juramento repetem um nome no Altar. É o nome do Escriba. Traga, e devolva a ele.",
  "(ele segura o frasco) Henoc. É o meu nome. Eles lembram de mim, os duzentos. Fui o único que tentou ajudar. Toma o diadema. Usei quando subi. Agora fico.")
m("jg01", "O Livro dos Vencidos", "Vença os chefes até o nível 15 e volte ao Escriba.",
  "CADERNO DO ESCRIBA · FOLHA 44\nCada coisa que você derruba lá embaixo tem um nome, e cada nome entra no livro dos vencidos. Comece por eles. Quando a primeira página encher, volte.",
  "O Escriba leu a página cheia e virou para a seguinte, em branco. \"Ainda tem muito fim pela frente\", disse.",
  "Este é o livro dos vencidos. Cada chefe que você derrubar entra nele. Encha a primeira página e volte. Eu escrevo devagar, mas escrevo tudo.",
  "Página cheia. O livro é grande. Continue.")

# ============================================================================ NPCs novos
NPCS = [
    dict(id="sariel_porta", nome="Sariel", titulo="Guardiã da Porta Dourada", faccao="arautos", classe_visual="anjo", local="jerusalem", ponto="porta_dourada",
         aparencia="Anjo alta e magra, sobretudo de couro preto com fivelas de ouro velho, uma asa inteira e a outra substituída por uma armação de latão e lona. Máscara de gás pendurada no pescoço. Uma brasa pequena acesa no olho esquerdo, o único ponto que brilha.",
         personalidade="Seca, leal ao Coro até onde o Coro é leal ao fim. Conta tudo: dentes, riscos, mortos. Não gosta de rezar em voz alta.",
         historia="Guardava a Porta Dourada quando o primeiro toque soou em Jerusalém. A porta estava selada desde Ezequiel: ninguém entraria por ela até o fim. Sariel abriu. Desde então risca o batente a cada noite em que o fim não termina. Os riscos já dão a volta na porta.",
         falas_ambiente=["Mais um risco no batente.", "A porta está aberta. O fim é que não entra.", "Conte seus mortos. Ninguém vai contar por você."]),
    dict(id="hulda_escada", nome="Hulda", titulo="Profetisa da Escada", faccao="arautos", classe_visual="cultista", local="jerusalem", ponto="brasa_do_altar",
         aparencia="Mulher de uns sessenta anos, batina vermelha desbotada, mãos enfaixadas de tanto mexer na Brasa, óculos de lente rachada. Carrega rolos amarrados nas costas.",
         personalidade="Erudita, irônica, desconfia de quem acredita fácil. Fala citando e corrige a citação.",
         historia="Lia os rolos do Coro na escada do Templo quando o Juízo começou. Foi quem manteve a Brasa do Altar acesa na primeira noite, com o óleo das lamparinas de toda a cidade. Sabe mais do que o Coro gostaria e menos do que ela mesma gostaria.",
         falas_ambiente=["A Brasa baixa à noite. Como todo mundo.", "Isso não está escrito. Ainda."], servicos=["loja"], loja="loja_hulda"),
    dict(id="zilpa_hissopo", nome="Zilpa", titulo="a Hissopeira", faccao="arautos", classe_visual="cultista", local="jerusalem", ponto="caldeirao_zilpa",
         aparencia="Velha baixa e forte, xale de luto bordado com ramos de hissopo, braços cobertos de cicatrizes de queimadura. Mexe o caldeirão com um osso comprido.",
         personalidade="Mandona, carinhosa, faz todo mundo comer. Nunca fala do filho, e fala dele o tempo todo.",
         historia="Cultista da Comunhão do Amargo, curandeira da cidade baixa. O filho, Joás, morreu na primeira semana e levantou com os outros na necrópole. Ela nunca foi ver.",
         falas_ambiente=["Come. Depois morre, se quiser.", "Hissopo bom nasce em cima de morto."], servicos=["loja"], loja="loja_zilpa"),
    dict(id="tubal_malho", nome="Tubal", titulo="o Malho, Ferreiro da Legião", faccao="arautos", classe_visual="demonio", local="jerusalem", ponto="forja_tubal",
         aparencia="Demônio enorme de pele cor de carne queimada, avental de couro cheio de furos de faísca, chifres serrados para caber na tenda. Um elo de corrente pendurado na orelha.",
         personalidade="Fala pouco e baixo, ri alto. Respeita ferro e quem sabe bater nele.",
         historia="Forjava armas da Legião Blasfema nas fornalhas de Tofete até o general sumir. Subiu para Jerusalém com a bigorna nas costas e montou a forja ao lado dos anjos, que não gostam dele. Ele não gosta dos anjos. Os dois precisam de lâminas.",
         falas_ambiente=["Ferro lembra.", "Não toque na bigorna. Ela morde."], servicos=["ferreiro"]),
    dict(id="bartimeu_brasas", nome="Bartimeu", titulo="o Cego das Brasas", faccao="arautos", classe_visual="humano", local="jerusalem", ponto="carrinho_bartimeu",
         aparencia="Rapaz magro de uns dezesseis anos, olhos brancos, faixa vermelha na testa, carrinho de mão cheio de frascos que ele reconhece pelo som.",
         personalidade="Rápido, debochado, cobra caro de quem enxerga. Diz que vê melhor no escuro, e no fim do mundo é sempre escuro.",
         historia="Mendigava na Porta de Damasco antes do Juízo. Quando a cidade escureceu, foi o único que não se perdeu nas ruas. Hoje empurra o carrinho de fogueira em fogueira vendendo poção para quem fica no spot.",
         falas_ambiente=["Frasco fresco! Eu sei porque está frio.", "Paga primeiro. Eu conto as moedas pelo barulho."], servicos=["loja"], loja="loja_bartimeu"),
    dict(id="bartimeu_carrinho", nome="Bartimeu", titulo="Carrinho de Poções", faccao="neutro", classe_visual="humano", local="jerusalem", ponto="descanso",
         aparencia="O mesmo Bartimeu, de faixa vermelha, empurrando o carrinho até a fogueira.", personalidade="Igual na fogueira e na cidade.",
         historia="Leva poção às fogueiras dos spots.", servicos=["loja"], loja="loja_carrinho_bartimeu"),
    dict(id="zaqueu_cobrador", nome="Zaqueu", titulo="o Cobrador", faccao="neutro", classe_visual="cultista", local="jerusalem", ponto="porta_do_esterco",
         aparencia="Homem baixinho, casaca de cobrador de impostos com botões de ossos, livro de dívidas preso por corrente ao cinto. Senta sempre em lugar alto.",
         personalidade="Amável, ganancioso, honesto do jeito dele: cobra todo mundo pelo mesmo preço.",
         historia="Cobrava impostos para quem estivesse mandando em Jerusalém. Quando o Juízo começou, continuou cobrando: dos anjos, dos demônios, da Vigília. Sabe quem deve o quê a quem, e isso vale mais que ouro.",
         falas_ambiente=["Todo mundo deve. Eu só anoto.", "Desce daí? Eu? Nunca."], servicos=["loja"], loja="loja_zaqueu"),
    dict(id="henoc_escriba", nome="O Escriba", titulo="Escriba do Bosque", faccao="neutro", classe_visual="humano", local="bosque_hissopo", ponto="cabana_do_escriba",
         aparencia="Homem muito velho sem idade certa, batina cinza de lã grossa, dedos pretos de tinta, um diadema de bronze guardado numa caixa ao lado. Escreve o tempo todo.",
         personalidade="Calmo, preciso, gentil de um jeito distante. Responde pergunta com outra pergunta. Nunca diz o próprio nome.",
         historia="Ninguém sabe quando chegou. Mora na cabana do Bosque do Hissopo e anota o nome de cada morto que levanta no Monte das Oliveiras. (Segredo da linha \"O Escriba Que Não Morreu\": é Henoc, que andou com Deus e já não era; escreveu o pedido dos duzentos Vigilantes antes do dilúvio e foi mandado de volta quando o fim travou, para escrever a sentença deles.)",
         falas_ambiente=["Nome?", "Escrevo devagar. Mas escrevo tudo."]),
    dict(id="rispa_vigilia", nome="Rispa", titulo="a Que Vigia", faccao="neutro", classe_visual="humano", local="necropole_oliveiras", ponto="fogueira_rispa",
         aparencia="Mulher de meia-idade, saco de pano como manto, cabelo raspado, um cajado com trapos pendurados para espantar abutres. Senta numa rocha ao lado de uma fogueira que nunca apaga.",
         personalidade="Teimosa, mansa, dura como pedra. Guarda tudo o que os outros esquecem.",
         historia="Como a Rispa das Escrituras, que guardou os corpos dos filhos dos abutres do começo da sega até a chuva, ela guarda os mortos da necrópole dos abutres do Hermon. Desde o primeiro dia. A chuva não veio.",
         falas_ambiente=["Xô. Xô.", "Até a chuva. Eu fico."], servicos=[]),
    dict(id="jael_escuta", nome="Jael", titulo="a Escuta", faccao="neutro", classe_visual="cultista", local="encosta_cedros", ponto="posto_de_escuta",
         aparencia="Mulher jovem de batina do Coro rasgada nas mangas, fone de latão sempre num ouvido, cabos enrolados nos braços como terço.",
         personalidade="Ansiosa, brilhante, fala baixo como se alguém pudesse ouvir. Alguém pode.",
         historia="Copista do Coro de Sião, subiu ao posto de escuta abandonado do Hermon para provar que a estática era só estática. Não era. Ficou.",
         falas_ambiente=["Psiu. Eles estão contando.", "Cento e noventa e oito... cento e noventa e nove..."]),
]
LOJAS = [
    {"id": "loja_hulda", "npc": "hulda_escada", "nome": "Rolos e Remédios da Escada", "itens": ["hostia_negra", "pao_duro"], "fala_ao_abrir": "Tudo abençoado. Por mim. Serve?"},
    {"id": "loja_zilpa", "npc": "zilpa_hissopo", "nome": "Caldeirão da Zilpa", "itens": ["cha_de_hissopo", "pao_duro", "agua_doce"], "fala_ao_abrir": "Come. Paga depois. Mas paga."},
    {"id": "loja_bartimeu", "npc": "bartimeu_brasas", "nome": "Carrinho do Cego", "itens": ["vela_do_escriba", "agua_benta_polvora", "pao_duro", "agua_doce"], "compra_sucata": True, "fala_ao_abrir": "Escolhe. Eu sei o que você pegou pelo barulho."},
    {"id": "loja_carrinho_bartimeu", "npc": "bartimeu_carrinho", "nome": "Carrinho de Poções do Bartimeu", "fala_ao_abrir": "Vida, éter, antídoto. O resto ficou na cidade.",
     "itens": ["agua_benta_polvora", "pao_duro", "agua_doce"], "_nota": "poções, munição e armas da faixa 1 entram pelo jogador.gd estoque() (ver INTEGRACAO.md)"},
    {"id": "loja_zaqueu", "npc": "zaqueu_cobrador", "nome": "Degrau do Cobrador", "itens": ["agua_doce", "vela_do_escriba", "tonico_graxa", "hostia_negra"], "fala_ao_abrir": "Vendo para os dois lados. Pelo mesmo preço. Anoto tudo."},
]

# ============================================================================ objetos (cópia do deserto + texto próprio)
OB_TXT = {
    "peregrino_de_joelhos": ("Peregrino de Joelhos", "Ele está ajoelhado de frente para a Porta Dourada, mãos juntas, coberto de cinza. Não respira. Não caiu. Ainda espera alguém passar pela porta."),
    "mesa_do_capataz": ("Mesa do Capataz", "Entre correntes e recibos chamuscados, um livro de couro: CONTAS DE TOFETE. A última página está dobrada."),
    "porta_de_pa": ("Gruta de Pã", "A chave entra no chifre e gira sozinha o resto do caminho. A pedra se afasta e um bafo quente sobe das Fontes do Jordão para o fundo do monte."),
    "porta_do_altar": ("Porta do Altar", "Os selos se encaixam e a pedra se abre para dentro. Lá no fundo, duzentas vozes falam a mesma frase."),
    "tumulo_de_joas": ("Túmulo de Joás", "Você derrama a infusão na pedra. O cheiro amargo sobe. Entre os túmulos, algo grande e verde se levanta e pergunta, rouco: ...mãe?"),
    "forja_de_tofete": ("Fornalha de Tofete", "A fornalha grande ainda ruge. Os elos ficam brancos e, por um segundo, você ouve alguém puxando uma corrente lá embaixo."),
    "rolos_da_escada": ("Rolos da Escada", "Rolos de couro amarrados com fita vermelha. No de cima, a folha primeira de um livro: duzentos que desceram num monte e um escriba que escreveu por eles."),
    "tumulos_dos_profetas": ("Túmulo de Profeta", "Você joga cinza sobre a laje até o nome sumir de novo. Um Levantado na fila próxima abaixa a cabeça. Amanhã o vento descobre outro."),
    "nicho_da_noiva": ("Nicho da Noiva", "Uma mulher de pedra com véu. Na base, dois nomes riscados: o dela, de mulher, e o dele, de anjo."),
    "estandartes_da_legiao": ("Estandarte da Legião", "Um estandarte da Legião Blasfema caído na cinza da Geena. Em volta, pegadas de muitos demônios. Nenhum o levantou."),
    "trono_vazio": ("Trono da Geena", "Um trono de ferro e osso no meio das fornalhas, preso por correntes. No braço, metade de uma coroa. O assento está frio."),
    "rastro_de_brasas": ("Rastro de Brasa", "Dois sulcos de mão gigante na lama, com um risco de brasa no meio, como de algo que se arrasta sem pernas. O rastro vai para o sul, na direção do deserto."),
    "fontes_secas": ("Fonte Represada", "Você enche o frasco. A água cinzenta canta uma nota baixa dentro do vidro, sem parar."),
    "laje_do_juramento": ("Laje do Juramento", "Uma laje de pedra negra rachada no meio de sete pilares. Quando você encosta, as estrelas do céu escuro parecem piscar na mesma hora. Alguém se levanta do outro lado."),
    "antena_da_escuta": ("Antena da Escuta", "Você troca as válvulas. A antena estala, e por toda a encosta se ouve a contagem: cento e noventa e nove, duzentos, um..."),
    "pedra_da_ascensao": ("Pedra da Ascensão", "Na pedra, duas pegadas. Uma é famosa. A outra, mais antiga, tem do lado, em argila: AQUI EU SUBI. AQUI EU VOLTEI."),
    "tumulo_vazio_de_henoc": ("Túmulo Vazio", "A vela acende sozinha. O túmulo está pronto há séculos e nunca foi usado. Na parede, gravado em letras antigas: ELE ANDOU COM DEUS, E JÁ NÃO ERA."),
}
BAU_TXT = {
    "bau_bartimeu_1": ("Esconderijo da Pedra que Sobe", "Debaixo de uma pedra solta, uma lata com moedas de peregrino e um pedaço de cera com o desenho de um olho."),
    "bau_bartimeu_2": ("Esconderijo do Bosque", "Dentro de um tronco oco, perto da cabana do Escriba, um embrulho de couro amarrado com três nós de cego."),
    "bau_bartimeu_3": ("Esconderijo da Cidade de Baixo", "Um baú de ferro trancado, com uma flauta de osso rachada por cima do resto."),
    "bau_escada_hulda": ("Baú da Escada", "O baú da Hulda, cheio de rolos e um frasco de óleo da primeira noite."),
    "bau_ohya": ("Baú de Ohya", "O tesouro do gigante: o que sobrou dos escravos que tinham alguma coisa."),
    "bau_naama": ("Arca do Enxoval", "O enxoval de Naamá: panos de linho, sal e brinquedos grandes demais para criança de gente."),
    "bau_semyaza": ("Cofre do Juramento", "O que os duzentos trouxeram do céu e não puderam usar."),
    "bau_dote_naama": ("Dote das Noivas", "O dote que os Vigilantes pagaram pelas filhas dos homens. Ainda brilha. Ainda pesa na consciência de alguém."),
}

# ============================================================================ monstros (texto do bestiário; números ficam em dados.json do gerar.py)
MON_TXT = {
    "peregrino_ressecado": ("Peregrinos que vieram de todo canto ver o fim do mundo em Jerusalém e foram pegos pelo primeiro toque. Secaram de joelhos. Levantam para cavar o Getsêmani atrás de relíquias.", "Pele de couro seco, roupas de romaria, terço nas mãos, joelhos em carne viva.", ["monte_oliveiras"]),
    "abutre_do_hermon": ("Abutres grandes que descem do Hermon atrás dos mortos. Furam odres, levam papel, levam azeite.", "Abutre do tamanho de um homem curvado, cabeça pelada cinza, penas sujas de cinza.", ["monte_oliveiras", "cidade_de_davi"]),
    "chacal_de_josafa": ("Matilhas do leito seco do Cedrom, no Vale de Josafá, onde as nações serão julgadas. Defendem a toca.", "Chacal magro e alto, pelo ruivo queimado, dentes à mostra.", ["vale_josafa", "cidade_de_davi", "fontes_jordao"]),
    "levantado_das_oliveiras": ("Os mortos do Monte das Oliveiras, os primeiros a levantar no Juízo, como a tradição prometia. Esperam na fila ser chamados.", "Mortos antigos de mortalha de linho cinzento, de pé em fila, olhando a Porta Dourada.", ["necropole_oliveiras", "encosta_cedros", "cume_hermon"]),
    "porco_de_gadara": ("A vara onde a Legião guarda os espíritos que sobram, como em Gadara. Ninguém lembra de mandar a vara para o mar.", "Porco grande de couro avermelhado, olhos humanos, fala sozinho baixinho.", ["pocilgas_gadara"]),
    "sineiro_infiltrado": ("Sineiros da Vigília escondidos nos cedros: tocam sinos rachados para abafar o Coro e carregam cartas cifradas.", "Homem de capa azul suja, sino de bronze rachado no cinto, rosto coberto.", ["encosta_cedros"]),
    "sapador_herege": ("Engenheiros Hereges da Vigília represando as Fontes do Jordão para mandar água ao deserto. Cavam também a Fenda das Oliveiras.", "Engenheiro de macacão de lona, óculos de solda, picareta e lanterna de arco.", ["fontes_jordao", "monte_oliveiras", "encosta_cedros"]),
    "vigilante_acorrentado": ("Pedaços dos duzentos Vigilantes que desceram no Hermon. As correntes afrouxaram no Juízo; eles guardam as pegadas do juramento.", "Figura alta e translúcida, asas de fumaça, correntes partidas nos pulsos.", ["cume_hermon"]),
    "fornalheiro_de_tofete": ("Demônios ocos que alimentam as fornalhas da Geena. Atacam quem entra no pátio de Tofete.", "Demônio oco de couro rachado, brasa no peito aberto, pá de carvão.", ["vale_hinom"]),
    "capataz_de_tofete": ("Manda nas fornalhas desde que o general sumiu. Guarda a Chave de Pã no cinto.", "Demônio grande de avental de ferro, corrente no ombro, chave de chifre no cinto.", ["vale_hinom"]),
    "filho_do_hissopo": ("O hissopo bebeu um morto e levantou com ele. Responde por um nome.", "Criatura de raízes e mortalha, flores de hissopo nos ombros, medalha no pescoço.", ["necropole_oliveiras"]),
    "kokabiel_contador": ("O Vigilante que ensinou os homens a ler as estrelas. Conta as noites que faltam para o fim terminar.", "Anjo alto de manto de estrelas apagadas, astrolábio de latão no peito.", ["cume_hermon"]),
    "verme_do_fosso": ("Comem o que os gigantes deixam nas minas.", "Verme branco do tamanho de um cão.", ["minas_dos_gigantes"]),
    "escravo_dos_gigantes": ("Os homens que os Nefilins puseram para cavar. Morreram de pé e continuam cavando.", "Morto de tanga e corrente, gancho de minério na mão.", ["minas_dos_gigantes"]),
    "nefilim_mirrado": ("Filhos pequenos dos Vigilantes, grandes demais para gente e pequenos demais para o dilúvio levar.", "Gigante de três metros, curvado, cabeça grande demais.", ["minas_dos_gigantes"]),
    "soldado_de_pedra": ("Mortos que viraram pedra antes que os gigantes os comessem.", "Soldado de armadura antiga, pele de pedra rachada.", ["minas_dos_gigantes"]),
    "noiva_afogada": ("As filhas dos homens que casaram com os Vigilantes; choram os filhos que o dilúvio levou.", "Mulher de véu encharcado, pele azulada, voz de água.", ["salao_das_noivas"]),
    "brasa_de_azazel": ("O fogo que Azazel ensinou aos homens; ainda procura uma forja.", "Chama viva do tamanho de uma criança, com cara.", ["salao_das_noivas"]),
    "escriba_emparedado": ("Copiavam os ensinamentos proibidos dos Vigilantes e foram emparedados com eles.", "Homem magro meio saído da parede, pena na mão, olhos costurados.", ["salao_das_noivas"]),
    "eco_do_juramento": ("A voz dos duzentos jurando, que ainda anda pelo salão.", "Boca de luz pálida flutuando, repetindo palavras.", ["altar_do_juramento"]),
    "vigilante_desfeito": ("O que sobrou dos Vigilantes que o Juízo soltou pela metade.", "Anjo de asas quebradas, corpo de fumaça e corrente.", ["altar_do_juramento"]),
    "ohya_gigante": ("Filho de Semyaza. Sonhou com o dilúvio antes de todos e se escondeu no fundo do Hermon.", "Gigante de cinco metros, manto de peles costuradas, clava de tronco de cedro.", ["minas_dos_gigantes"]),
    "naama_noiva": ("A Noiva dos Vigilantes, que chora os filhos gigantes afogados.", "Mulher altíssima de véu de sal, flutuando, lágrimas que caem como chuva.", ["salao_das_noivas"]),
    "semyaza_juramento": ("O chefe dos duzentos que desceram no Hermon. Jura de novo: que o fim fique onde está.", "Anjo imenso acorrentado ao Altar, asas negras de fuligem, Tábua de pedra no peito.", ["altar_do_juramento"]),
}
REGISTRO = {"fonte": "caderno_escriba", "titulo": "Folha solta"}


def troca(v, ctx):
    """Troca ids em qualquer valor de missão (recursivo)."""
    if isinstance(v, list): return [troca(x, ctx) for x in v]
    if isinstance(v, dict):
        out = {}
        for k, x in v.items():
            if k in ("alvo",): out[k] = MOB.get(x, x)
            elif k in ("npc", "doador", "entrega"): out[k] = [NPC[y] for y in x] if isinstance(x, list) else NPC[x]
            elif k == "spot": out[k] = SPOT[x]
            elif k == "subzona": out[k] = SUB[x]
            elif k == "objeto": out[k] = OBJ_POR_MISSAO.get((ctx, x)) or OBJ[x]
            elif k in ("item",) or (k == "id" and isinstance(x, str) and (x in ITENS)): out[k] = item_novo(x)
            elif k in ("requer", "requer_qualquer", "missao_concluida", "missao_ativa", "missao_disponivel"):
                out[k] = [M_ID[y] for y in x if y in M_ID] if isinstance(x, list) else M_ID.get(x, x)
            elif k == "ao_concluir_inicia": out[k] = M_ID[x]
            elif k == "flags": out[k] = ["jh_" + f for f in x]
            else: out[k] = troca(x, ctx)
        return out
    return v


NOVOS_ITENS = {}
def item_novo(i):
    if i in GENERICOS: return i
    if i not in IT: raise SystemExit(f"item sem espelho: {i}")
    e = IT[i]
    if isinstance(e, str): return e
    nid, nome, desc, cit = e[:4]
    if nid not in NOVOS_ITENS:
        x = copy.deepcopy(ITENS[i]); x["id"] = nid; x["nome"] = nome; x["espelho_de"] = i
        if desc: x["descricao"] = desc
        if len(e) > 4: x.update(e[4])
        x.pop("origem", None)
        if x.get("faccao") == "vigilia": x["faccao"] = "arautos"
        x.pop("citacao", None); x.pop("_balanceamento", None)
        if cit: x["citacao"] = {"texto": cit[0], "autor": cit[1]}
        if "leitura" in x: x["leitura"] = item_novo(x["leitura"])
        if isinstance(x.get("efeito"), dict) and x["efeito"].get("repele"): x["efeito"]["repele"] = MOB.get(x["efeito"]["repele"], x["efeito"]["repele"])
        NOVOS_ITENS[nid] = x
    return nid


def missoes():
    out = []
    for orig, nid in M_ID.items():
        q = copy.deepcopy(MISS[orig])
        n = troca(q, orig)
        n["id"] = nid; n["faccao"] = "arautos"; n["espelho_de"] = orig
        if "linha" in n:
            n["linha"] = {"A Estrela Que Nós Soltamos": "O Juramento do Hermon", "A Legião Sem General": "O Trono da Geena",
                          "Vem Para Fora": "O Escriba Que Não Morreu", "O Livro dos Vencidos": "O Livro dos Vencidos"}[n["linha"]]
        titulo, resumo, desc, concl, *_r = T[nid]
        n["titulo"], n["resumo"], n["descricao"], n["texto_conclusao"] = titulo, resumo, desc, concl
        esc = T[nid][6]
        if n.get("escolhas"):
            assert len(esc) == len(n["escolhas"]), (nid, len(esc), len(n["escolhas"]))
            for e, t in zip(n["escolhas"], esc): e["texto"] = t
        if orig == "v05": n["entrega"] = "hulda_escada"
        if orig in ("d01v",): n["doador"] = "hulda_escada"
        if orig in ("e01v",): n["doador"] = "tubal_malho"
        if orig in ("f01v",): n["doador"] = "zilpa_hissopo"; n["entrega"] = "zilpa_hissopo"
        if orig in ("f02", "f03"): n["doador"] = n["entrega"] = "zaqueu_cobrador"
        if orig in ("e04",): n["entrega"] = "tubal_malho"
        if orig in ("e05v",): n["doador"] = n["entrega"] = "tubal_malho"
        out.append(n)
    return out


def dialogos(ms):
    """Um diálogo por NPC: abertura, uma opção por missão (oferta / entrega) e a história do NPC."""
    por = {}
    for q in ms:
        d = q["doador"] if isinstance(q["doador"], str) else q["doador"][0]
        e = q["entrega"] if isinstance(q["entrega"], str) else q["entrega"][0]
        por.setdefault(d, []).append(("oferta", q)); por.setdefault(e, []).append(("fim", q))
    out = []
    for n in NPCS:
        nid = n["id"]
        if nid == "bartimeu_carrinho":
            out.append({"id": "dlg_bartimeu_carrinho", "npc": nid, "inicio": "raiz", "nos": {"raiz": {"fala": "Frasco fresco! Pra quem fica no spot o dia inteiro, eu trago o carrinho até a fogueira. Eu sei o caminho pelo calor.",
                        "opcoes": [{"texto": "Mostra as poções.", "acoes": [{"abrir_loja": "loja_carrinho_bartimeu"}]}, {"texto": "Até mais."}]}}})
            continue
        nos = {"raiz": {"fala": n["falas_ambiente"][0] + " " + n["personalidade"].split(".")[0] + ".", "opcoes": []}}
        op = nos["raiz"]["opcoes"]
        for tipo, q in por.get(nid, []):
            qid = q["id"]; titulo, resumo, desc, concl, oferta, fim, esc = T[qid]
            if tipo == "oferta" and q["doador"] != "automatico":
                nos[qid + "_oferta"] = {"fala": oferta or resumo, "opcoes": [{"texto": "Deixa comigo.", "acoes": [{"aceitar_missao": qid}]}, {"texto": "Agora não."}]}
                op.append({"texto": titulo + "?", "ir": qid + "_oferta", "se": {"missao_disponivel": qid}})
            if tipo == "fim" and q["entrega"] != "automatico" and fim:
                if q.get("escolhas"):
                    nos[qid + "_fim"] = {"fala": fim, "opcoes": [{"texto": e["texto"], "acoes": [{"concluir_missao": qid, "escolha": e["id"]}]} for e in q["escolhas"]] + [{"texto": "Preciso pensar."}]}
                else:
                    nos[qid + "_fim"] = {"fala": fim, "opcoes": [{"texto": "Feito.", "acoes": [{"concluir_missao": qid}]}]}
                op.append({"texto": "Sobre " + titulo.lower() + ".", "ir": qid + "_fim", "se": {"missao_pronta": qid}})
        if n.get("loja"): op.append({"texto": "Quero ver o que você tem.", "acoes": [{"abrir_loja": n["loja"]}]})
        nos["historia"] = {"fala": n["historia"].split(" (Segredo")[0], "opcoes": [{"texto": "Voltar.", "ir": "raiz"}]}
        op.append({"texto": "Quem é você?", "ir": "historia"}); op.append({"texto": "Até mais."})
        out.append({"id": "dlg_" + nid, "npc": nid, "inicio": "raiz", "nos": nos})
    return out


def main():
    ms = missoes()
    npcs = [{"id": n["id"], "nome": n["nome"], "titulo": n["titulo"], "faccao": n["faccao"], "classe_visual": n["classe_visual"],
             "local": {"subzona": n["local"], "ponto": n["ponto"]}, "servicos": n.get("servicos", []), **({"loja": n["loja"]} if n.get("loja") else {}),
             "dialogo": "dlg_" + n["id"], "aparencia": n["aparencia"], "personalidade": n["personalidade"], "historia": n["historia"],
             "falas_ambiente": n.get("falas_ambiente", [])} for n in NPCS]
    dl = dialogos(ms)
    # monstros: drops de missão espelhados
    mons = []
    for mid, (desc, apar, locs) in MON_TXT.items():
        orig = next((k for k, v in MOB.items() if v == mid), None)
        drops = []
        for d in (MONS.get(orig, {}).get("drops_missao", []) if orig else []):
            if d["missao"] in M_ID: drops.append({"item": item_novo(d["item"]), "chance": d["chance"], "missao": M_ID[d["missao"]]})
        # o chefe espelho do General solta o selo; Kokabiel o astrolábio (como no deserto)
        x = {"id": mid, "nome": None, "tipo": "chefe" if mid in ("ohya_gigante", "naama_noiva", "semyaza_juramento") else ("elite" if mid == "kokabiel_contador" else "normal"),
             "locais": locs, "descricao": desc, "aparencia": apar, "espelho_de": orig, "drops_missao": drops,
             "registros": [dict(REGISTRO, texto=desc.split(".")[0] + ".")]}
        mons.append(x)
    nomes = json.load(open(os.path.join(AQUI, "dados.json")))
    for x in mons:
        x["nome"] = (nomes["mobs"].get(x["id"]) or nomes["chefes"].get(x["id"]) or {}).get("nome", x["id"])
        x["nivel"] = (nomes["mobs"].get(x["id"]) or {}).get("niveis") or [nomes["chefes"].get(x["id"], {}).get("nivel", 1)] * 2
    # objetos e baús
    objs, baus = [], []
    for o_orig, o_novo in OBJ.items():
        if o_orig in OBJS:
            x = troca(copy.deepcopy(OBJS[o_orig]), None); x["id"] = o_novo
            x.pop("pendente", None); x.pop("posicao_sugerida", None); x.pop("textos_variados", None)
            if "leitura" in x: x["leitura"] = item_novo(x["leitura"])
            if o_novo in OB_TXT: x["nome"], x["texto_ao_usar"] = OB_TXT[o_novo]
            if "invoca" in x: x["invoca"] = MOB.get(x["invoca"], x["invoca"])
            if "requer_item" in x: x["requer_item"] = item_novo(x["requer_item"])
            if "requer_itens" in x: x["requer_itens"] = [item_novo(i) for i in x["requer_itens"]]
            if "leva_para" in x: x["leva_para"] = SUB.get(x["leva_para"], x["leva_para"])
            if "texto_trancado" in x:
                x["texto_trancado"] = {"porta_de_pa": "A gruta de Pã está fechada por uma pedra com um buraco em forma de chifre. Do outro lado, algo respira devagar e quente.",
                                       "porta_do_altar": "Uma porta de pedra negra com dois buracos: um em forma de olho fechado, outro em forma de onda.",
                                       "laje_do_juramento": "Uma laje negra rachada no meio de sete pilares. Ela não se mexe para quem não foi chamado."}.get(o_novo, x["texto_trancado"])
            x["espelho_de"] = o_orig
            objs.append(x)
        elif o_orig in BAUS:
            x = troca(copy.deepcopy(BAUS[o_orig]), None); x["id"] = o_novo; x["espelho_de"] = o_orig
            if o_novo in BAU_TXT: x["nome"], x["texto_ao_abrir"] = BAU_TXT[o_novo]
            for f in x.get("fixo", []): f["id"] = item_novo(f["id"]) if f["id"] in ITENS else f["id"]
            baus.append(x)
    x = troca(copy.deepcopy(OBJS["torre_sino"]), None); x.update({"id": "forja_de_tofete", "subzona": "vale_hinom", "visivel_se": {"missao_ativa": "js03"}, "espelho_de": "torre_sino"})
    x["nome"], x["texto_ao_usar"] = OB_TXT["forja_de_tofete"]; objs.append(x)
    x = troca(copy.deepcopy(OBJS["torre_sino"]), None); x.update({"id": "rolos_da_escada", "subzona": "jerusalem", "visivel_se": {"missao_ativa": "jf03"}, "espelho_de": "torre_sino"})
    x["nome"], x["texto_ao_usar"] = OB_TXT["rolos_da_escada"]; objs.append(x)
    objs.append({"id": "ninhos_de_abutre", "nome": "Ninho de Abutre", "subzona": "monte_oliveiras", "quantidade_no_mapa": 3, "tabela": "ninho_corvo",
                 "texto_ao_usar": "Um ninho de galhos, pano de mortalha e coisas brilhantes no alto de um poste. Os abutres não vão gostar disso.", "invoca": "abutre_do_hermon", "espelho_de": "ninhos_corvo"})
    for o in objs:   # quantidades no mapa iguais às que o gerar.py coloca
        o["quantidade_no_mapa"] = {"peregrino_de_joelhos": 3, "tumulos_dos_profetas": 5, "fontes_secas": 3, "estandartes_da_legiao": 3, "rastro_de_brasas": 3,
                                   "nicho_da_noiva": 7, "ninhos_de_abutre": 3}.get(o["id"], o.get("quantidade_no_mapa", 1))
    # locais: a área e a dungeon
    mapa = json.load(open(os.path.join(AQUI, "jerusalem_hermon.json")))
    area = {"id": "jerusalem_hermon", "nome": "Jerusalém e Monte Hermon", "tipo": "area_inicial", "faccao": "arautos", "nivel": [1, 12],
            "descricao": "A cidade santa onde o Juízo começou, aberta pela Porta Dourada no primeiro toque, e as encostas do Hermon, onde os duzentos Vigilantes juraram antes do dilúvio. Pedra branca suja de cinza, oliveiras mortas, a Geena ardendo no vale e neve de cinza no cume.",
            "musica_sugerida": "coro distante de vozes graves, sinos de bronze abafados, vento de montanha, estalo de brasa",
            "subzonas": [{"id": z["id"], "nome": z["nome"], "tipo": "base" if z["seguro"] else "campo", "faccao": z["faccao"], "seguro": z["seguro"],
                          "nivel": z["nivel"]} for z in mapa["zonas"]]}
    dung = {"id": "fosso_dos_vigilantes", "nome": "Fosso dos Vigilantes", "faccao": "arautos", "nivel": [6, 12], "entrada": "fontes_jordao",
            "descricao": "Debaixo do Hermon, atrás dos Portões do Hades na gruta de Pã: as minas dos gigantes, o salão das noivas e o altar onde Semyaza jura de novo que o fim nunca termine.",
            "andares": [{"id": "minas_dos_gigantes", "nome": "Minas dos Gigantes", "nivel": [6, 8], "chefe": "ohya_gigante"},
                        {"id": "salao_das_noivas", "nome": "Salão das Noivas", "nivel": [8, 10], "chefe": "naama_noiva"},
                        {"id": "altar_do_juramento", "nome": "Altar do Juramento", "nivel": [10, 12], "chefe": "semyaza_juramento"}]}
    spots_ped = [{"id": s["id"], "nome": s["nome"], "nivel": s["nivel"], "subzona": s["zona"],
                  "monstros": sorted({g["mob"] for g in mapa["spawns"] if g.get("spot") == s["id"]}), "espelho_de": s["espelho"]} for s in mapa["spots"]]
    W = lambda nome, obj: json.dump(obj, open(os.path.join(AQUI, nome), "w"), ensure_ascii=False, indent=1)
    W("missoes_acrescimo.json", {"_doc": "Acrescentar a design/missoes/dados/missoes.json. Espelho das missões da Vigília do 1 ao 12 (campo espelho_de).", "missoes": ms})
    W("npcs_acrescimo.json", {"npcs": npcs}); W("dialogos_acrescimo.json", {"dialogos": dl})
    W("itens_acrescimo.json", {"_doc": "Cópias dos itens do deserto (mesmos atributos e efeitos), com nome e texto daqui.", "itens": list(NOVOS_ITENS.values())})
    W("monstros_acrescimo.json", {"monstros": mons}); W("objetos_acrescimo.json", {"objetos": objs, "baus": baus}); W("lojas_acrescimo.json", {"lojas": LOJAS})
    W("locais_acrescimo.json", {"areas": [area], "dungeons": [dung], "spots_pedidos": spots_ped})
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
    junta("itens.json", "itens", list(NOVOS_ITENS.values())); junta("monstros.json", "monstros", mons); junta("lojas.json", "lojas", LOJAS)
    junta("objetos.json", "objetos", objs); junta("objetos.json", "baus", baus)
    L = json.load(open(os.path.join(d, "locais.json")))
    L["areas"].append(area); dd = dict(dung); dd["andares"] = [dict(a) for a in dung["andares"]]; L["dungeons"].append(dd)
    L.setdefault("spots", {}).setdefault("pedidos", []).extend(spots_ped)
    json.dump(L, open(os.path.join(d, "locais.json"), "w"), ensure_ascii=False)
    r = subprocess.run([sys.executable, os.path.join(tmp, "missoes", "validar.py")], capture_output=True, text=True)
    print(r.stdout[-3000:], r.stderr[-2000:])
    xv = sum((q.get("recompensas") or {}).get("xp", 0) for q in MISS.values() if q["faccao"] in ("vigilia", "ambas") and q["nivel"] <= 12)
    xa = sum((q.get("recompensas") or {}).get("xp", 0) for q in ms)
    print(f"XP de missão até o 12: Vigília {xv} | Arautos (Jerusalém) {xa} | missões {len(ms)} | itens novos {len(NOVOS_ITENS)} | NPCs {len(npcs)}")
    shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
