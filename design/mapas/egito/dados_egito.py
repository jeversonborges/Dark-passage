"""Dados de combate do Egito (mobs, chefes, drops), usados por gerar.py e por exportar_dados().
Formatos: mobs = design/combate/mobs.json (entrada completa, entra por data/v06_extra.json -> mobs);
chefes = design/combate/chefes.json (fases e ataques que o chefe_ctl.gd já entende: os ids `lanca_do_juizo`, `pranto_que_cai`,
`vomito_de_brasa`, `banquete`, `marca_do_juizo` e invocação genérica dão o comportamento, `nome` dá o nome na tela) +
`mecanica_egito` (a ideia de cada luta, rodada por entregas/egito/codigo/chefe_egito.gd).
Uso: python3 dados_egito.py  -> entregas/egito/dados.json
"""
import json, os
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))


def mob(nome, niveis, arq, tags, motivo, ataques, ia, comportamento, drop, res=None, ajuste=None, alcance=1.2, grupo=(2, 2), lore=None, base=None):
    m = {"nome": nome, "area": "egito", "niveis": list(niveis), "arquetipo": arq, "tags": tags, "grupo": list(grupo), "res": res or {},
         "alcance": alcance, "ia": ia, "comportamento": comportamento, "ataques": ataques, "drop": drop, "renascimento_s": 14, "motivo": motivo}
    if ajuste: m["ajuste"] = ajuste
    if lore: m["registros"] = [{"fonte": f, "titulo": t, "texto": x} for f, t, x in lore]
    if base: m["base"] = base
    return m


VEN = lambda d, m: {"veneno": {"duracao": d, "dano_por_s_mult": m}}
SANG = lambda d, m: {"sangramento": {"duracao": d, "dano_por_s_mult": m}}

MOBS = {
    # ------------------------------------------------------------------ bichos do Nilo
    "ibis_de_thoth": mob("Íbis de Thoth", (50, 52), "rasteiro", ["animal", "voador"],
        "as íbis de Thoth pescam no juncal desde antes das pirâmides; só bicam quem chega perto do ninho",
        [{"id": "bicada", "mult": 1.0, "preparo": 0.35}, {"id": "mergulho", "mult": 1.5, "preparo": 0.6, "salto": 2.5, "recarga": 7}],
        {"padrao": "enxame", "raio_aggro": 4, "aggro_social": 5}, "Circula a 2 tiles e mergulha. Neutra: só ataca quem bate.", "egito_animal",
        lore=[("caderno_tamit", "Íbis", "Thoth tinha cabeça de íbis porque a íbis anda com o bico no chão, como quem lê.")]),
    "crocodilo_do_nilo": mob("Crocodilo do Nilo", (50, 64), "bruto", ["animal", "anfibio"],
        "tomam sol no lodo da margem; o Nilo voltou e eles voltaram junto",
        [{"id": "mordida", "mult": 1.0, "preparo": 0.6}, {"id": "giro_da_morte", "mult": 1.3, "preparo": 0.9, "telegrafo": {"forma": "cone", "raio": 2.2, "angulo": 80},
          "efeito": SANG(4, .2), "recarga": 9}],
        {"padrao": "emboscada", "raio_aggro": 2.5, "raio_coleira": 12}, "Fica parado como tronco. Quando apanha, morde e prende (giro da morte).",
        "egito_animal", res={"veneno": .3}, ajuste={"mov": .8, "hp": .85},
        lore=[("diario_ahmose", "Margem", "Meu avô dizia que crocodilo é o Nilo com fome. Hoje o Nilo come de novo.")]),
    "crocodilo_gigante": mob("Crocodilo Gigante", (62, 69), "bruto", ["animal", "anfibio"],
        "os velhos machos da catarata e de Méris; defendem o pedaço de água que é deles",
        [{"id": "mordida", "mult": 1.15, "preparo": 0.65}, {"id": "rabada", "mult": 1.4, "preparo": 0.9, "telegrafo": {"forma": "circulo", "raio": 2.4},
          "empurrao_px": 18, "recarga": 8}, {"id": "giro_da_morte", "mult": 1.4, "preparo": 0.9, "telegrafo": {"forma": "cone", "raio": 2.4, "angulo": 80},
          "efeito": SANG(4, .25), "recarga": 10}],
        {"padrao": "emboscada", "raio_aggro": 3, "raio_coleira": 12}, "Rabada em círculo empurra. Territorial.", "egito_animal",
        res={"veneno": .4, "fisico": .1}, ajuste={"hp": 1.15, "mov": .8}),
    "escaravelho_sagrado": mob("Escaravelho Sagrado", (50, 56), "rasteiro", ["animal", "inseto"],
        "rolam bolas de lodo pelos campos como Khepri rola o sol; ninguém mexe com eles, por respeito e por medo",
        [{"id": "pinca", "mult": 1.0, "preparo": 0.35}, {"id": "bola_de_lodo", "mult": 1.2, "preparo": 0.7, "projetil_vel": 6, "efeito": {"lento": 2}, "recarga": 6}],
        {"padrao": "teimoso", "raio_aggro": 3, "raio_coleira": 12}, "Neutro. Joga a bola de lodo (lentidão) e foge para a bola.", "egito_inseto",
        res={"veneno": .4}, ajuste={"hp": 1.6, "dano": 1.4},
        lore=[("caderno_tamit", "Khepri", "Khepri, 'o que vem a ser'. O sol nasce porque um besouro o empurra. Neste ano 31 o besouro está cansado.")]),
    "escaravelho_carniceiro": mob("Escaravelho Carniceiro", (51, 58), "normal", ["animal", "inseto"],
        "os escaravelhos que os embalsamadores usavam para limpar os ossos; acharam as múmias de novo",
        [{"id": "mandibula", "mult": 1.0, "preparo": 0.45, "efeito": SANG(3, .15)}, {"id": "enxame", "mult": .4, "preparo": 1.0, "a_cada_s": 6,
          "area": {"raio": 1.6, "duracao": 3}}],
        {"padrao": "matilha", "raio_aggro": 4, "aggro_social": 6}, "Sangramento; deixa um enxame no chão a cada 6 s.", "egito_inseto",
        res={"veneno": .5, "fogo": -.3}),
    "escaravelho_rei": mob("Escaravelho-Rei", (58, 64), "elite", ["animal", "inseto", "sagrado"],
        "o escaravelho de lápis que guarda o ninho debaixo da escavação; os escavadores juram que ele tem nome",
        [{"id": "pinca", "mult": 1.0, "preparo": 0.5}, {"id": "disco_solar", "mult": 1.5, "preparo": 1.0, "telegrafo": {"forma": "circulo", "raio": 3},
          "efeito": {"queimadura": {"duracao": 3, "dano_por_s_mult": .3}}, "recarga": 10},
         {"id": "chamar_ninho", "em_hp": 0.5, "invoca": {"escaravelho_carniceiro": 2}}],
        {"padrao": "elite", "raio_aggro": 4, "raio_coleira": 14}, "Elite do spot. Disco solar em círculo; chama o ninho na metade da vida.",
        "egito_elite", res={"veneno": .5, "fogo": .3}),
    "esfinge_carneiro": mob("Esfinge de Carneiro", (53, 58), "bruto", ["construto", "pedra", "sagrado"],
        "as esfinges da avenida acordaram com a quarta trombeta e guardam a calçada de Amon; quem anda no meio é deixado em paz",
        [{"id": "chifrada", "mult": 1.0, "preparo": 0.7}, {"id": "investida", "mult": 1.6, "preparo": 1.0, "investida": True,
          "telegrafo": {"forma": "linha", "comprimento": 6, "largura": 1.4}, "empurrao_px": 22, "recarga": 9}],
        {"padrao": "guarda", "raio_aggro": 3, "raio_coleira": 10}, "Territorial e lenta; investida em linha que empurra. Resiste a físico.",
        "egito_construto", res={"fisico": .25, "veneno": 1.0, "sangue": 1.0, "raio": -.3}, ajuste={"mov": .75},
        lore=[("diario_dalva", "Avenida", "Duas fileiras de esfinges de carneiro, uma para cada lado, do templo de Ptah até Karnak. Vimos uma virar a cabeça. Ninguém mais anda fora da calçada.")]),
    # ------------------------------------------------------------------ múmias
    "mumia_operaria": mob("Múmia Operária", (52, 63), "normal", ["morto_vivo", "humano"],
        "os artesãos que cavaram as tumbas levantaram quando o coração do Faraó bateu; ainda tentam terminar o turno",
        [{"id": "enxo", "mult": 1.0, "preparo": 0.6}, {"id": "faixas", "mult": .6, "preparo": 0.8, "telegrafo": {"forma": "linha", "comprimento": 4, "largura": 1},
          "efeito": {"lento": 3}, "recarga": 8}],
        {"padrao": "teimoso", "raio_aggro": 4, "raio_coleira": 14}, "Lenta e teimosa; joga faixas de linho que deixam lento.", "egito_mumia",
        res={"fogo": -.5, "sagrado": -.3, "veneno": 1.0}, ajuste={"mov": .8, "hp": 1.15},
        lore=[("ostraco_vila", "Lista de faltas", "'Neferhotep: ausente, embalsamando o irmão. Hay: ausente, morto.' Ano 31: Hay voltou ao trabalho.")]),
    "sacerdote_mumia": mob("Sacerdote Mumificado", (56, 70), "conjurador", ["morto_vivo", "humano", "sacerdote"],
        "os sacerdotes do rito de abertura da boca ainda rezam pelos mortos; defendem os textos que leem",
        [{"id": "incenso", "mult": 1.0, "preparo": 0.8, "projetil_vel": 6}, {"id": "maldicao_de_seth", "mult": .8, "preparo": 1.1,
          "telegrafo": {"forma": "circulo", "raio": 2.2}, "efeito": {"silenciado": 2}, "recarga": 10},
         {"id": "abertura_da_boca", "cura_frac_hp_alvo": 0.25, "conjuracao": 1.4, "interrompivel": True, "recarga": 9}],
        {"padrao": "suporte", "distancia_ideal": 5, "distancia_minima": 3}, "Fica atrás e cura as múmias (interrompa). Silencia em área.",
        "egito_mumia", res={"fogo": -.5, "sagrado": -.2, "veneno": 1.0, "magico": .2}),
    "guardiao_mumia": mob("Guardião Mumificado", (60, 70), "bruto", ["morto_vivo", "humano", "guardiao"],
        "os guardas da necrópole juraram defender o sono do rei; o rei acordou e eles continuam de guarda",
        [{"id": "khopesh", "mult": 1.0, "preparo": 0.6}, {"id": "golpe_de_escudo", "mult": .8, "preparo": 0.7, "efeito": {"atordoado": 1.0}, "recarga": 10},
         {"id": "corte_em_arco", "mult": 1.4, "preparo": 0.9, "telegrafo": {"forma": "cone", "raio": 2.4, "angulo": 110}, "recarga": 8}],
        {"padrao": "guarda", "raio_aggro": 4, "raio_coleira": 12}, "Escudo atordoa; corte em arco. Agressivo nas tumbas.", "egito_guardiao",
        res={"fogo": -.4, "fisico": .15, "veneno": 1.0}),
    # ------------------------------------------------------------------ guardiões de cabeça de animal (netjer)
    "anubis_sentinela": mob("Anúbis Sentinela", (56, 70), "normal", ["guardiao", "sagrado", "chacal"],
        "os chacais de Anúbis voltaram às portas dos templos e das tumbas; só deixam passar quem não toca em nada",
        [{"id": "lanca", "mult": 1.0, "preparo": 0.55, "alcance": 1.8}, {"id": "estocada", "mult": 1.5, "preparo": 0.8,
          "telegrafo": {"forma": "linha", "comprimento": 4.5, "largura": .9}, "recarga": 7}],
        {"padrao": "guarda", "raio_aggro": 4, "raio_coleira": 12}, "Alcance de lança; estocada em linha.", "egito_guardiao",
        res={"sagrado": .3, "sombra": -.2}, alcance=1.8),
    "anubis_guardiao": mob("Anúbis Guardião", (64, 70), "bruto", ["guardiao", "sagrado", "chacal"],
        "a guarda de honra do Vale dos Reis; foram eles que deixaram os escavadores entrarem na tumba sem cartucho, e ninguém sabe por quê",
        [{"id": "khopesh", "mult": 1.0, "preparo": 0.55}, {"id": "julgamento", "mult": 1.8, "preparo": 1.2, "telegrafo": {"forma": "circulo", "raio": 2.6},
          "recarga": 11}, {"id": "uivo_de_anubis", "em_hp": 0.4, "buff": {"dano": .25, "duracao": 8}}],
        {"padrao": "guarda", "raio_aggro": 4.5, "raio_coleira": 12}, "Golpe de julgamento em círculo; com 40% de vida uiva e bate mais forte.",
        "egito_guardiao", res={"sagrado": .35, "fisico": .1}),
    "sobekita": mob("Sobekita", (57, 65), "normal", ["guardiao", "anfibio", "crocodilo"],
        "os guardiões de Sobek ainda vigiam as águas sagradas; atacam quem pisa no lodo deles",
        [{"id": "maca", "mult": 1.1, "preparo": 0.65}, {"id": "mergulho_de_lodo", "mult": 1.3, "preparo": 0.9, "salto": 3.5,
          "telegrafo": {"forma": "circulo", "raio": 1.8}, "efeito": {"lento": 2}, "recarga": 9}],
        {"padrao": "guarda", "raio_aggro": 4, "raio_coleira": 12}, "Salta no jogador e deixa o chão de lodo.", "egito_guardiao",
        res={"veneno": .3, "fogo": -.2}, ajuste={"hp": 1.2}),
    "guardiao_falcao": mob("Guardião de Hórus", (59, 67), "atirador", ["guardiao", "sagrado", "voador"],
        "os falcões de Hórus guardam do alto os terraços e a biblioteca; atiram em quem rouba rolo",
        [{"id": "flecha", "mult": 1.0, "preparo": 0.6, "projetil_vel": 11}, {"id": "chuva_de_flechas", "mult": .7, "preparo": 1.2,
          "telegrafo": {"forma": "circulo", "raio": 2.4}, "recarga": 10}],
        {"padrao": "atirador", "distancia_ideal": 6, "distancia_minima": 3}, "Fica longe e atira; chuva de flechas em círculo.", "egito_guardiao",
        res={"sagrado": .2, "raio": -.3}),
    # ------------------------------------------------------------------ escorpiões e serpentes
    "escorpiao_de_serket": mob("Escorpião de Serket", (58, 66), "normal", ["animal", "venenoso"],
        "a escavação rachou os ninhos de Serket debaixo das pirâmides; defendem o ninho e nada mais",
        [{"id": "pinca", "mult": 1.0, "preparo": 0.5}, {"id": "ferrao", "mult": 1.2, "preparo": 0.75, "efeito": VEN(6, .2), "recarga": 6}],
        {"padrao": "matilha", "raio_aggro": 3.5, "aggro_social": 5}, "Ferrão envenena (pilha).", "egito_animal", res={"veneno": .8, "fogo": -.2}),
    "escorpiao_negro": mob("Escorpião Negro", (62, 66), "bruto", ["animal", "venenoso"],
        "os escorpiões do Mar de Areia, pretos como a noite do Duat, caçam na tempestade",
        [{"id": "pinca_dupla", "mult": 1.1, "preparo": 0.55}, {"id": "ferrao_turquesa", "mult": 1.5, "preparo": 1.0, "telegrafo": {"forma": "linha", "comprimento": 3.5, "largura": .9},
          "efeito": VEN(8, .3), "recarga": 8}],
        {"padrao": "guarda", "raio_aggro": 3.5, "raio_coleira": 12}, "Ferrão em linha com veneno forte.", "egito_animal", res={"veneno": 1.0, "fisico": .1}),
    "naja": mob("Naja", (54, 68), "atirador", ["animal", "venenoso", "serpente"],
        "as najas da coroa do faraó; cospem nos olhos de quem chega perto do ovo",
        [{"id": "bote", "mult": 1.0, "preparo": 0.4}, {"id": "cuspe", "mult": .8, "preparo": 0.7, "projetil_vel": 8, "efeito": {"cegueira": 2, **VEN(4, .2)}, "recarga": 7}],
        {"padrao": "atirador", "distancia_ideal": 4, "distancia_minima": 2}, "Cospe veneno que cega (erra mais golpes).", "egito_animal",
        res={"veneno": 1.0}),
    "cria_de_apofis": mob("Cria de Apófis", (63, 69), "bruto", ["serpente", "caos"],
        "filhas da serpente do caos que saem da areia quando o sol escurece; mordem tudo o que brilha",
        [{"id": "bote", "mult": 1.1, "preparo": 0.55}, {"id": "constricao", "mult": .5, "preparo": 0.8, "efeito": {"atordoado": 1.5}, "recarga": 12},
         {"id": "veneno_do_caos", "mult": 1.2, "preparo": 1.0, "telegrafo": {"forma": "cone", "raio": 3, "angulo": 60}, "efeito": VEN(6, .3), "recarga": 9}],
        {"padrao": "guarda", "raio_aggro": 4, "raio_coleira": 12}, "Constrição atordoa; cone de veneno.", "egito_animal", res={"veneno": 1.0, "sombra": .3, "sagrado": -.3},
        ajuste={"hp": 1.1}),
}

# ---- versões da dungeon e da raid (mesma arte; números, nível e drop próprios). `base` = o mob do mundo.
def var(base, nome, niveis, motivo, drop, ajuste=None, arq=None, extra_tags=None):
    m = json.loads(json.dumps(MOBS[base])); m.update({"nome": nome, "niveis": list(niveis), "motivo": motivo, "drop": drop, "area": "dungeon"})
    if ajuste: m["ajuste"] = {**m.get("ajuste", {}), **ajuste}
    if arq: m["arquetipo"] = arq
    if extra_tags: m["tags"] = m["tags"] + extra_tags
    m["ia"] = {**m["ia"], "raio_aggro": max(5, m["ia"].get("raio_aggro", 5)), "raio_coleira": 18}
    m["sprite_de"] = base
    return m


MOBS_DUNGEON = {
    "crocodilo_sagrado": var("crocodilo_do_nilo", "Crocodilo Sagrado", (50, 51), "os crocodilos que os sacerdotes de Sobek criavam para o deus; a água do Labirinto subiu e eles voltaram a nadar", "hawara"),
    "sacerdote_de_sobek": var("sacerdote_mumia", "Sacerdote de Sobek", (50, 52), "os sacerdotes que enfeitavam Petsuchos de ouro; ainda cuidam dele", "hawara"),
    "escaravelho_do_labirinto": var("escaravelho_carniceiro", "Escaravelho do Labirinto", (50, 53), "limpam as três mil salas há três mil anos", "hawara"),
    "guarda_do_labirinto": var("guardiao_mumia", "Guarda do Labirinto", (52, 54), "Heródoto escreveu que os guardas não o deixaram descer; continuam não deixando", "hawara", ajuste={"hp": .9}),
    "esfinge_do_patio": var("esfinge_carneiro", "Esfinge do Pátio", (52, 53), "guardam os doze pátios; cada uma olha para uma porta", "hawara"),
    "filha_de_serket": var("escorpiao_de_serket", "Filha de Serket", (53, 54), "o ninho da deusa escorpião no fundo da tumba de Amenemés", "hawara"),
    "naja_do_labirinto": var("naja", "Naja do Labirinto", (53, 54), "as najas que os construtores puseram nas falsas portas", "hawara"),
    # raid (nível 60): grupos de 3, todos agressivos (dungeon). hp mais alto: é conteúdo de grupo.
    "leoa_de_sekhmet": var("crocodilo_do_nilo", "Leoa de Sekhmet", (60, 60), "as leoas que caçavam ao lado da deusa no dia da Destruição da Humanidade", "raid_coracao",
                           ajuste={"hp": 2.2, "dano": 1.3, "mov": 1.35}, extra_tags=["felino"]),
    "sacerdotisa_de_sekhmet": var("sacerdote_mumia", "Sacerdotisa de Sekhmet", (60, 60), "as sacerdotisas que acalmavam a leoa com cerveja e oração; agora a incitam", "raid_coracao", ajuste={"hp": 2.2}),
    "serpente_de_bastao": var("naja", "Serpente de Bastão", (60, 60), "o bastão dos magos que vira serpente (Êx 7:12); a de Arão engoliu as deles, mas Arão não está aqui", "raid_coracao", ajuste={"hp": 1.6}),
    "guardiao_do_duat": var("guardiao_mumia", "Guardião do Duat", (60, 60), "os porteiros das doze horas da noite", "raid_coracao", ajuste={"hp": 2.4, "dano": 1.2}),
    "anubita_do_duat": var("anubis_guardiao", "Anúbis do Duat", (60, 60), "a guarda dos vasos canópicos do rei", "raid_coracao", ajuste={"hp": 2.4, "dano": 1.2}),
    "falcao_do_duat": var("guardiao_falcao", "Falcão do Duat", (60, 60), "olhos de Hórus nas paredes da câmara canópica", "raid_coracao", ajuste={"hp": 2.2}),
    "cria_do_duat": var("cria_de_apofis", "Cria do Rio do Duat", (60, 60), "a cria de Apófis que sobe na barca da noite", "raid_coracao", ajuste={"hp": 2.0}),
    "escaravelho_do_coracao": var("escaravelho_rei", "Escaravelho do Coração", (60, 60), "os escaravelhos do coração que mentem pelo morto na pesagem (feitiço 30B)", "raid_coracao", ajuste={"hp": .5}),
    "primogenito_do_egito": var("mumia_operaria", "Primogênito do Egito", (60, 60), "os primogênitos que o Anjo Destruidor levou na décima praga; o Faraó os chama na fúria", "raid_coracao",
                                ajuste={"hp": 1.6, "mov": 1.1}),
}
MOBS_DUNGEON["leoa_de_sekhmet"]["sprite_de"] = "leoa_de_sekhmet"

# ---- adicionais de luta controlados pelo chefe_egito.gd (mobs com HP de chefe; a IA comum os move)
ADICIONAIS = {
    "jambres": dict(nome="Jambres, o Mago de Faraó", base="sacerdote_mumia", niveis=[60, 60], ajuste={"hp": 30.0, "dano": 1.9, "defesa": 1.3},
                    arquetipo="raro", ia={"padrao": "suporte", "distancia_ideal": 6, "distancia_minima": 3, "raio_aggro": 30, "raio_coleira": 40},
                    ataques=[{"id": "incenso", "mult": 1.0, "preparo": 0.8, "projetil_vel": 7}, {"id": "maldicao_de_seth", "mult": .9, "preparo": 1.1,
                             "telegrafo": {"forma": "circulo", "raio": 2.6}, "efeito": {"silenciado": 2}, "recarga": 9}],
                    tags=["morto_vivo", "humano", "sacerdote", "chefe_par"], drop=None, res={"fogo": -.3, "sagrado": -.2, "magico": .2}),
    "hapi": dict(nome="Hapi, o Babuíno do Norte", base="anubis_guardiao", niveis=[60, 60], ajuste={"hp": 22.0, "dano": 1.6, "defesa": 1.2}, arquetipo="raro",
                 ia={"padrao": "guarda", "raio_aggro": 30, "raio_coleira": 40}, tags=["guardiao", "sagrado", "chefe_par"], drop=None),
    "duamutef": dict(nome="Duamutef, o Chacal do Leste", base="anubis_guardiao", niveis=[60, 60], ajuste={"hp": 22.0, "dano": 1.6, "defesa": 1.2}, arquetipo="raro",
                     ia={"padrao": "guarda", "raio_aggro": 30, "raio_coleira": 40}, tags=["guardiao", "sagrado", "chefe_par"], drop=None),
    "qebehsenuef": dict(nome="Qebehsenuef, o Falcão do Oeste", base="guardiao_falcao", niveis=[60, 60], ajuste={"hp": 22.0, "dano": 1.6, "defesa": 1.2}, arquetipo="raro",
                        ia={"padrao": "atirador", "distancia_ideal": 6, "distancia_minima": 3, "raio_aggro": 30, "raio_coleira": 40}, tags=["guardiao", "sagrado", "chefe_par"], drop=None),
    "ammit": dict(nome="Ammit, a Devoradora", base="crocodilo_gigante", niveis=[60, 60], ajuste={"hp": 20.0, "dano": 2.0, "mov": 1.3}, arquetipo="raro",
                  ia={"padrao": "guarda", "raio_aggro": 30, "raio_coleira": 40}, tags=["monstro", "sagrado", "chefe_par"], drop=None),
}
for k, v in ADICIONAIS.items():
    m = json.loads(json.dumps(MOBS[v["base"]]))
    m.update({kk: vv for kk, vv in v.items() if kk != "base"}); m["area"] = "dungeon"; m["renascimento_s"] = 0
    m["motivo"] = "adicional de chefe (controlado pelo chefe_egito.gd)"; m["sprite_de"] = k
    if "ataques" not in v: m["ataques"] = MOBS[v["base"]]["ataques"]
    MOBS_DUNGEON[k] = m

TODOS_MOBS = {**MOBS, **MOBS_DUNGEON}

# ===================================================================================== chefes
def fase(n, hp, nome, ataques, fala=None, mudancas=None):
    f = {"n": n, "hp": hp, "nome": nome, "ataques": ataques}
    if fala: f["fala"] = fala
    if mudancas: f["mudancas"] = mudancas
    return f


CHEFES = {
    # ------------------------------------------------------------------ O Labirinto de Hawara (grupo 1 a 5; hp para 1 jogador, +75% por jogador a mais)
    "petsuchos": {
        "nome": "Petsuchos, o Crocodilo Sagrado", "andar": 1, "dungeon": "labirinto_de_hawara", "nivel": 51, "tags": ["animal", "sagrado", "anfibio"],
        "hp": 26000, "escala_grupo": {"base": 1, "por_jogador": 0.75}, "defesa": 105, "dano_base": 125, "intervalo_ataque": 2.0, "velocidade_mov": 2.2,
        "postura_max": 900, "res": {"veneno": .5, "fogo": -.2, "sagrado": .2}, "duracao_alvo_s": 180, "furia_tempo_s": 420,
        "conceito": "O crocodilo-deus de Crocodilópolis (Heródoto e Estrabão: enfeitado de ouro, alimentado pelos sacerdotes). Ficou no Labirinto quando a cheia o encheu.",
        "fala_entrada": "(o salão inteiro range, e a água começa a subir)",
        "fases": [
            fase(1, [1.0, 0.6], "O Deus Come", [
                {"id": "mordida", "mult": 1.0, "preparo": 0.7, "alcance": 2.2},
                {"id": "lanca_do_juizo", "nome": "Investida do Lodo", "mult": 1.6, "preparo": 1.1, "telegrafo": {"forma": "linha", "comprimento": 9, "largura": 2.0},
                 "deslocamento": 8, "recarga": 10},
                {"id": "rabada", "nome": "Rabada", "mult": 1.3, "preparo": 1.0, "telegrafo": {"forma": "cone", "raio": 3.5, "angulo": 140}, "empurrao_px": 20, "recarga": 8}]),
            fase(2, [0.6, 0.25], "A Água Sobe", [
                {"id": "lanca_do_juizo", "encadeia": 2, "recarga": 9},
                {"id": "banquete", "nome": "Giro da Morte", "mult": .5, "preparo": 1.0, "telegrafo": {"forma": "cone", "raio": 2.5, "angulo": 70},
                 "mult_por_tick": .45, "depois": {"exausto": 2.5}, "recarga": 14},
                {"id": "chamar_sacerdotes", "nome": "Os Sacerdotes Trazem Comida", "invoca": {"sacerdote_de_sobek": 2}, "uma_vez": True}],
                fala="(ele afunda; as ilhas de pedra são o único chão seco)"),
            fase(3, [0.25, 0.0], "Fome de Deus", [
                {"id": "lanca_do_juizo", "encadeia": 3, "recarga": 8},
                {"id": "rabada", "recarga": 6}], fala="(as oferendas acabaram; ele vem por você)")],
        "mecanica_egito": {"tipo": "agua_que_sobe",
            "regra": "A cada 35 s (fase 2 em diante, a cada 25 s) a água do salão sobe por 8 s: o chão fora das 4 ilhas de pedra vira área de dano (3% do HP máx por s) e Petsuchos submerge (imune, some) e reaparece com uma Investida do Lodo telegrafada contra um jogador aleatório. Nas mesas de oferenda (4 objetos, 600 HP) ele se cura 6% do HP máximo por mesa inteira que alcançar enquanto está submerso; quebrar as mesas antes nega a cura.",
            "ciclo_s": [35, 25, 25], "duracao_s": 8, "dano_fora_ilha_frac": 0.03, "ilhas": "arena.ilhas", "oferendas": "arena.oferendas", "oferenda_hp": 600, "cura_por_oferenda": 0.06},
        "drop": "chefe_hawara_1", "morte": "(Petsuchos afunda devagar; o ouro dos brincos fica boiando)"},
    "esfinge_de_hawara": {
        "nome": "A Esfinge de Hawara", "andar": 2, "dungeon": "labirinto_de_hawara", "nivel": 53, "tags": ["construto", "pedra", "sagrado"],
        "hp": 29000, "escala_grupo": {"base": 1, "por_jogador": 0.75}, "defesa": 112, "dano_base": 132, "intervalo_ataque": 2.2, "velocidade_mov": 1.8,
        "postura_max": 1100, "res": {"fisico": .15, "veneno": 1.0, "sangue": 1.0, "raio": -.25}, "duracao_alvo_s": 190, "furia_tempo_s": 420,
        "conceito": "A guardiã dos doze pátios. Não pergunta em voz: mostra no peito a sequência dos glifos e espera a resposta nos pedestais.",
        "fala_entrada": "QUEM ANDA NO LABIRINTO SEM SABER O CAMINHO É O CAMINHO QUE ANDA NELE.",
        "fases": [
            fase(1, [1.0, 0.5], "Os Doze Pátios", [
                {"id": "patada", "mult": 1.0, "preparo": 0.8, "alcance": 2.4},
                {"id": "onda_de_pedra", "nome": "Onda de Pedra", "mult": 1.4, "preparo": 1.1, "telegrafo": {"forma": "cone", "raio": 6, "angulo": 50}, "recarga": 9},
                {"id": "pranto_que_cai", "nome": "Teto que Cai", "mult": 1.2, "quantidade": 4, "intervalo": .5, "preparo": .9, "telegrafo": {"forma": "circulo", "raio": 1.5}, "recarga": 12}]),
            fase(2, [0.5, 0.0], "A Resposta", [
                {"id": "onda_de_pedra", "recarga": 7},
                {"id": "pranto_que_cai", "quantidade": 6, "recarga": 10},
                {"id": "lanca_do_juizo", "nome": "Salto da Esfinge", "mult": 1.7, "preparo": 1.2, "telegrafo": {"forma": "linha", "comprimento": 8, "largura": 2.2},
                 "deslocamento": 7, "recarga": 11}], fala="ERRADO É SÓ OUTRO CAMINHO.")],
        "mecanica_egito": {"tipo": "enigma",
            "regra": "Em 80%, 55% e 30% de HP a Esfinge senta (imune) e acende três glifos no peito em sequência (escaravelho, olho, ankh, pena, djed, junco). Os 6 pedestais da sala têm um glifo cada; o certo é o que COMPLETA a sequência (a regra muda: repete o primeiro, o que falta da tríade, o oposto). Um jogador precisa ficar 3 s no pedestal certo em até 12 s: ela fica Quebrada (dano recebido +50% por 10 s). Pedestal errado ou tempo esgotado: Onda de Pedra na sala inteira (60% do HP máx; os pedestais protegem só quem está no certo).",
            "gatilhos_hp": [0.8, 0.55, 0.3], "glifos": ["escaravelho", "olho", "ankh", "pena", "djed", "junco"], "tempo_s": 12, "ficar_s": 3,
            "quebrada": {"dano_recebido": 0.5, "duracao": 10}, "erro_frac_hp_max": 0.6, "pedestais": "arena.pedestais"},
        "drop": "chefe_hawara_2", "morte": "A RESPOSTA... ERA VOCÊ."},
    "serket": {
        "nome": "Serket, a Que Faz a Garganta Respirar", "andar": 3, "dungeon": "labirinto_de_hawara", "nivel": 54, "tags": ["sagrado", "venenoso", "monstro"],
        "hp": 33000, "escala_grupo": {"base": 1, "por_jogador": 0.75}, "defesa": 110, "dano_base": 136, "intervalo_ataque": 1.6, "velocidade_mov": 2.6,
        "postura_max": 900, "res": {"veneno": 1.0, "fogo": -.2, "sagrado": .3}, "duracao_alvo_s": 200, "furia_tempo_s": 450,
        "conceito": "A deusa escorpião que protegia os vasos canópicos e curava picada, guardando a tumba de Amenemés III no fundo do Labirinto. O título dela é a cura; a picada é o preço.",
        "fala_entrada": "Eu fecho a garganta. Eu abro a garganta. Respire enquanto eu deixo.",
        "fases": [
            fase(1, [1.0, 0.6], "A Picada", [
                {"id": "pinca", "mult": 1.0, "preparo": 0.55, "alcance": 2.0, "efeito": VEN(8, .12)},
                {"id": "ferroada", "nome": "Ferroada Carregada", "mult": 1.8, "preparo": 1.3, "telegrafo": {"forma": "linha", "comprimento": 5, "largura": 1.2},
                 "efeito": VEN(10, .25), "recarga": 9},
                {"id": "vomito_de_brasa", "nome": "Névoa de Veneno", "mult": .6, "preparo": 1.0, "telegrafo": {"forma": "cone", "raio": 5, "angulo": 60}, "ticks": 4,
                 "efeito": VEN(6, .2), "recarga": 12}]),
            fase(2, [0.6, 0.3], "O Ninho", [
                {"id": "ferroada", "recarga": 8},
                {"id": "vomito_de_brasa", "recarga": 11}],
                fala="Filhas. A garganta deles."),
            fase(3, [0.3, 0.0], "Respire", [
                {"id": "ferroada", "recarga": 6},
                {"id": "vomito_de_brasa", "recarga": 9},
                {"id": "marca_do_juizo", "nome": "Selo de Serket", "mult": 2.0, "preparo": 3.0, "telegrafo": {"forma": "circulo_segue_jogador", "raio": 2.2}, "recarga": 14}],
                fala="Agora ninguém respira.")],
        "mecanica_egito": {"tipo": "veneno_e_ankh",
            "regra": "Os golpes empilham Veneno de Serket (até 10 pilhas; cada pilha tira 0,6% do HP máx por s e reduz a cura recebida em 4%). Os 4 ankhs acesos da sala tiram todas as pilhas de quem pisa neles e apagam por 25 s. Na fase 2 ela se enterra (imune) a cada 40 s, por 6 s, e reaparece embaixo do jogador com mais pilhas (círculo telegrafado). Os 3 ninhos (800 HP) chamam uma filha cada a cada 30 s na fase 2 em diante, enquanto estiverem de pé.",
            "pilha_max": 10, "dano_por_pilha_frac": 0.006, "cura_reduzida_por_pilha": 0.04, "ankhs": "arena.ankhs", "ankh_recarga_s": 25, "enterra": {"a_cada_s": 40, "dur_s": 6, "desde_fase": 2},
            "ninhos": "arena.ninhos", "ninho_hp": 800},
        "drop": "chefe_hawara_3", "morte": "Respire... agora... sozinho."},

    # ------------------------------------------------------------------ O Coração Endurecido (raid nível 60; hp para 5 jogadores, +20% por jogador a mais até 10)
    "sekhmet": {
        "nome": "Sekhmet, a Leoa Que Bebeu o Sangue", "andar": 1, "raid": "coracao_endurecido", "nivel": 60, "tags": ["sagrado", "felino", "deusa"],
        "hp": 240000, "escala_grupo": {"base": 5, "por_jogador": 0.2, "max": 10}, "defesa": 125, "dano_base": 165, "intervalo_ataque": 1.7, "velocidade_mov": 2.6,
        "postura_max": 1500, "res": {"fogo": .5, "sagrado": .3, "gelo": -.2}, "duracao_alvo_s": 300, "furia_tempo_s": 480,
        "conceito": "Rá mandou Sekhmet exterminar a humanidade e, arrependido, a deteve com sete mil jarras de cerveja tingida de ocre, que ela bebeu achando que era sangue. Foi o primeiro extermínio interrompido da história. O rito do Faraó a acordou para guardar o primeiro portão.",
        "fala_entrada": "Sete mil jarras. Eu bebi todas. Desta vez eu olho antes de beber.",
        "fases": [
            fase(1, [1.0, 0.6], "A Caçada", [
                {"id": "garras", "mult": 1.0, "preparo": 0.55, "alcance": 2.2},
                {"id": "vomito_de_brasa", "nome": "Sopro do Sol", "mult": 1.1, "preparo": 1.0, "telegrafo": {"forma": "cone", "raio": 6, "angulo": 70}, "ticks": 4, "recarga": 12},
                {"id": "lanca_do_juizo", "nome": "Salto da Leoa", "mult": 1.5, "preparo": 1.0, "telegrafo": {"forma": "linha", "comprimento": 10, "largura": 2.0},
                 "deslocamento": 9, "alvo": "mais_longe", "recarga": 11}]),
            fase(2, [0.6, 0.3], "O Massacre", [
                {"id": "chamar_leoas", "nome": "A Matilha do Sol", "invoca": {"leoa_de_sekhmet": 3}, "recarga": 40},
                {"id": "lanca_do_juizo", "encadeia": 2, "recarga": 10},
                {"id": "vomito_de_brasa", "recarga": 10}], fala="O GOSTO! EU LEMBRO DO GOSTO!"),
            fase(3, [0.3, 0.0], "Sete Mil Jarras", [
                {"id": "pranto_que_cai", "nome": "Chuva de Brasa", "mult": 1.2, "quantidade": 6, "intervalo": .4, "preparo": .9, "telegrafo": {"forma": "circulo", "raio": 1.6}, "recarga": 9},
                {"id": "lanca_do_juizo", "encadeia": 3, "recarga": 9}], fala="Não é sangue. NÃO É SANGUE.")],
        "mecanica_egito": {"tipo": "sede",
            "regra": "Sede: +6 por golpe dela que acerta um jogador, +2 por segundo na fase 2 em diante. Com 100 ela entra em Massacre por 8 s (dano +80%, velocidade +40%, ataques em cone sem pausa). As 8 jarras de cerveja ocre (objetos, 1 golpe) espalhadas pelo pátio: quebrar uma jarra a até 4 m dela tira 35 de Sede e a deixa Embriagada por 4 s (dano recebido +20%). Jarras renascem a cada 45 s. Longe dela a jarra só derrama no chão (desperdício).",
            "sede_por_golpe": 6, "sede_por_s": [0, 2, 3], "massacre": {"dano": 0.8, "vel": 0.4, "dur_s": 8}, "jarras": "arena.jarras", "jarra_raio": 4.0,
            "jarra_reduz": 35, "embriagada": {"dano_recebido": 0.2, "dur_s": 4}, "jarra_renasce_s": 45},
        "drop": "chefe_coracao_1", "morte": "Era... cerveja. Sempre foi cerveja."},
    "janes": {
        "nome": "Janes e Jambres, os Magos de Faraó", "andar": 2, "raid": "coracao_endurecido", "nivel": 60, "tags": ["morto_vivo", "humano", "sacerdote"],
        "hp": 130000, "escala_grupo": {"base": 5, "por_jogador": 0.2, "max": 10}, "defesa": 110, "dano_base": 150, "intervalo_ataque": 2.0, "velocidade_mov": 2.2,
        "postura_max": 1100, "res": {"fogo": -.3, "sagrado": -.2, "magico": .2}, "duracao_alvo_s": 300, "furia_tempo_s": 480,
        "conceito": "Os magos que imitaram Moisés diante de Faraó (Êx 7-8): também jogaram bastões que viraram serpentes, também tornaram a água em sangue, também fizeram subir rãs. Na terceira praga não conseguiram e disseram 'isto é o dedo de Deus'. O nome deles está em 2 Timóteo 3:8. Morreram juntos e foram enterrados de mãos dadas.",
        "fala_entrada": "Tudo o que ele fez, nós fizemos. Tudo o que vocês fizerem, nós faremos.",
        "fases": [
            fase(1, [1.0, 0.5], "O Bastão", [
                {"id": "golpe_de_bastao", "mult": 1.0, "preparo": 0.6, "alcance": 2.0},
                {"id": "chamar_serpentes", "nome": "Bastão que Vira Serpente", "invoca": {"serpente_de_bastao": 2}, "recarga": 25},
                {"id": "pranto_que_cai", "nome": "Chuva de Rãs", "mult": .9, "quantidade": 5, "intervalo": .4, "preparo": .9, "telegrafo": {"forma": "circulo", "raio": 1.4}, "recarga": 11}]),
            fase(2, [0.5, 0.0], "O Rio de Sangue", [
                {"id": "vomito_de_brasa", "nome": "Água em Sangue", "mult": .8, "preparo": 1.1, "telegrafo": {"forma": "cone", "raio": 6, "angulo": 60}, "ticks": 4, "recarga": 12},
                {"id": "marca_do_juizo", "nome": "O Dedo de Deus", "mult": 2.2, "preparo": 3.0, "telegrafo": {"forma": "circulo_segue_jogador", "raio": 2.4}, "recarga": 16}],
                fala="Isto... não é o dedo de Deus. É o nosso.")],
        "adicionais": {"jambres": {"_doc": "o segundo mago (mob com HP de chefe, ver dados.mobs.jambres); nasce no início da luta ao lado de Janes"}},
        "mecanica_egito": {"tipo": "imitacao",
            "regra": "Dois chefes (Janes é o principal; Jambres nasce junto). Imitação: a cada feitiço com telegrafo que um lança, o outro repete o mesmo 2 s depois, no seu próprio alvo. Vínculo: se um morrer, o outro tem 10 s; se não morrer também, ergue o irmão com 40% do HP (canal de 4 s, interrompível com postura). Rio de Sangue: na fase 2 uma poça de sangue cresce no centro (+0,5 m de raio a cada 10 s; dentro dela a cura recebida cai). Distância: se os dois ficarem a menos de 6 m um do outro por 3 s, ganham Pacto (dano +30%) até se separarem.",
            "segundo": "jambres", "eco_s": 2.0, "vinculo_s": 10, "ressuscita_frac": 0.4, "canal_s": 4.0, "rio": {"desde_fase": 2, "cresce_por_10s": 0.5, "cura_reduzida": 0.5},
            "pacto": {"dist": 6.0, "apos_s": 3.0, "dano": 0.3}},
        "drop": "chefe_coracao_2", "morte": "Juntos... como fomos enterrados."},
    "imseti": {
        "nome": "Os Quatro Filhos de Hórus", "andar": 3, "raid": "coracao_endurecido", "nivel": 60, "tags": ["guardiao", "sagrado"],
        "hp": 120000, "escala_grupo": {"base": 5, "por_jogador": 0.2, "max": 10}, "defesa": 120, "dano_base": 150, "intervalo_ataque": 1.8, "velocidade_mov": 2.2,
        "postura_max": 1200, "res": {"sagrado": .3}, "duracao_alvo_s": 330, "furia_tempo_s": 540,
        "conceito": "Imseti (homem, guarda o fígado, sul), Hapi (babuíno, os pulmões, norte), Duamutef (chacal, o estômago, leste) e Qebehsenuef (falcão, os intestinos, oeste), guardiões dos quatro vasos canópicos do rei. Imseti é o primogênito e o último a cair.",
        "fala_entrada": "IMSETI: Os quatro vasos estão cheios. O rei está inteiro. Vocês não.",
        "fases": [
            fase(1, [1.0, 0.0], "Os Quatro Vasos", [
                {"id": "golpe", "mult": 1.0, "preparo": 0.6, "alcance": 2.0},
                {"id": "lanca_do_juizo", "nome": "Corte do Sul", "mult": 1.4, "preparo": 1.0, "telegrafo": {"forma": "linha", "comprimento": 8, "largura": 1.6}, "recarga": 10},
                {"id": "pranto_que_cai", "nome": "Natrão", "mult": 1.0, "quantidade": 4, "intervalo": .5, "preparo": .9, "telegrafo": {"forma": "circulo", "raio": 1.6}, "recarga": 12}])],
        "adicionais": {"hapi": {}, "duamutef": {}, "qebehsenuef": {}},
        "mecanica_egito": {"tipo": "conselho",
            "regra": "Quatro guardiões, dois lutando por vez (os outros dois ficam nos pedestais dos vasos, imunes, e dão uma aura aos que lutam: Hapi +25% de dano, Duamutef cura 1% do HP máx por s, Qebehsenuef flechas em quem estiver longe, Imseti reduz dano recebido em 25%). A cada 30 s a dupla troca. Imseti é imune até os outros três caírem. Cada guardião que morre derrama o vaso: uma área permanente no lugar onde caiu (fígado: dano; pulmões: lentidão; estômago: tira cura; intestinos: veneno), por isso o grupo escolhe ONDE e EM QUE ORDEM derrubá-los.",
            "membros": ["imseti", "hapi", "duamutef", "qebehsenuef"], "troca_s": 30, "ultimo": "imseti",
            "auras": {"hapi": {"dano": 0.25}, "duamutef": {"cura_frac_s": 0.01}, "qebehsenuef": {"flechas_longe": 8.0}, "imseti": {"reducao_dano": 0.25}},
            "vasos": {"imseti": "figado_dano", "hapi": "pulmoes_lento", "duamutef": "estomago_sem_cura", "qebehsenuef": "intestinos_veneno"},
            "pedestais": "arena.pedestais"},
        "drop": "chefe_coracao_3", "morte": "IMSETI: O rei... está inteiro sem nós?"},
    "apofis": {
        "nome": "Apófis, a Serpente Sem Fim", "andar": 4, "raid": "coracao_endurecido", "nivel": 60, "tags": ["serpente", "caos"],
        "hp": 340000, "escala_grupo": {"base": 5, "por_jogador": 0.2, "max": 10}, "defesa": 120, "dano_base": 170, "intervalo_ataque": 2.2, "velocidade_mov": 0.0,
        "postura_max": 1800, "res": {"veneno": 1.0, "sombra": .4, "sagrado": -.3, "fogo": -.2}, "duracao_alvo_s": 360, "furia_tempo_s": 540,
        "conceito": "A serpente do caos que ataca a barca de Rá toda noite na sétima hora do Amduat. Toda noite perde. Desde que o Sol Terço ficou parado, a noite não acaba e a luta também não. O grupo luta em cima da barca da noite.",
        "fala_entrada": "(do rio escuro sobe uma cabeça do tamanho da barca, e ela não termina de subir)",
        "imovel": True,
        "fases": [
            fase(1, [1.0, 0.65], "A Sétima Hora", [
                {"id": "bote", "nome": "Bote", "mult": 1.0, "preparo": 0.9, "telegrafo": {"forma": "cone", "raio": 4, "angulo": 50}, "alcance": 4.0},
                {"id": "lanca_do_juizo", "nome": "Bote pela Lateral", "mult": 1.8, "preparo": 1.3, "telegrafo": {"forma": "linha", "comprimento": 14, "largura": 2.6}, "recarga": 9},
                {"id": "vomito_de_brasa", "nome": "Cuspe da Treva", "mult": .7, "preparo": 1.1, "telegrafo": {"forma": "cone", "raio": 7, "angulo": 40}, "ticks": 3, "recarga": 14}]),
            fase(2, [0.65, 0.3], "As Crias", [
                {"id": "chamar_crias", "nome": "As Crias Sobem na Barca", "invoca": {"cria_do_duat": 3}, "recarga": 35},
                {"id": "lanca_do_juizo", "dupla": True, "angulo_entre": 30, "recarga": 8},
                {"id": "vomito_de_brasa", "recarga": 11}], fala="(as escamas abrem e algo sobe pelos remos)"),
            fase(3, [0.3, 0.0], "O Olhar", [
                {"id": "lanca_do_juizo", "dupla": True, "angulo_entre": 30, "recarga": 7},
                {"id": "pranto_que_cai", "nome": "Escamas que Caem", "mult": 1.2, "quantidade": 6, "intervalo": .4, "preparo": .9, "telegrafo": {"forma": "circulo", "raio": 1.6}, "recarga": 10}],
                fala="(os olhos acendem; não olhe)")],
        "mecanica_egito": {"tipo": "lanterna_de_ra",
            "regra": "A Lanterna de Rá no meio da barca tem Luz (0 a 100), perde 3 por s e 25 a cada Cuspe da Treva que a atinge. Jogadores pegam Brasa nos 2 braseiros da proa (interagir: carrega 1 brasa, anda 30% mais devagar) e levam até a lanterna (+30 de Luz). Com Luz acima de 50 o grupo tem Sol de Rá (dano +15%); com 0 a barca escurece, Apófis Engole a Luz (dano em todos, 8% do HP máx por s, até alguém reacender). Fase 3: Olhar a cada 25 s (telegrafado 3 s, os olhos acendem): quem estiver de frente para ele no fim fica Petrificado 4 s; vire de costas.",
            "luz_max": 100, "perde_por_s": 3, "cuspe_tira": 25, "brasa": {"da": 30, "lento": 0.3}, "braseiros": "arena.braseiros", "lanterna": "arena.lanterna",
            "sol_de_ra": {"acima": 50, "dano": 0.15}, "escuro_frac_s": 0.08, "olhar": {"desde_fase": 3, "a_cada_s": 25, "aviso_s": 3, "petrifica_s": 4}},
        "drop": "chefe_coracao_4", "morte": "(a serpente afunda no rio escuro; a barca segue para a oitava hora)"},
    "anubis_pesador": {
        "nome": "Anúbis, o Pesador", "andar": 5, "raid": "coracao_endurecido", "nivel": 60, "tags": ["sagrado", "chacal", "deus"],
        "hp": 320000, "escala_grupo": {"base": 5, "por_jogador": 0.2, "max": 10}, "defesa": 130, "dano_base": 165, "intervalo_ataque": 1.9, "velocidade_mov": 2.3,
        "postura_max": 1700, "res": {"sagrado": .4, "sombra": .3}, "duracao_alvo_s": 360, "furia_tempo_s": 540,
        "conceito": "No Salão das Duas Verdades Anúbis põe o coração do morto num prato e a pena de Maat no outro; Thoth anota; Ammit espera o coração pesado. Há três mil e trezentos anos ele não consegue pesar o coração do Faraó. Vai pesar o seu.",
        "fala_entrada": "Coração de um lado. Pena do outro. Nenhum de vocês vai sair daqui sem ser pesado.",
        "fases": [
            fase(1, [1.0, 0.55], "A Pesagem", [
                {"id": "cetro_was", "mult": 1.0, "preparo": 0.6, "alcance": 2.2},
                {"id": "marca_do_juizo", "nome": "Marca do Pesador", "mult": 1.6, "preparo": 3.0, "telegrafo": {"forma": "circulo_segue_jogador", "raio": 2.2}, "recarga": 13},
                {"id": "pancada", "nome": "Pancada", "mult": 1.5, "preparo": 1.1, "telegrafo": {"forma": "circulo", "raio": 3.2}, "recarga": 9}]),
            fase(2, [0.55, 0.0], "A Devoradora", [
                {"id": "marca_do_juizo", "recarga": 10},
                {"id": "pancada", "recarga": 7},
                {"id": "lanca_do_juizo", "nome": "Avanço do Chacal", "mult": 1.6, "preparo": 1.0, "telegrafo": {"forma": "linha", "comprimento": 9, "largura": 1.8}, "deslocamento": 8, "recarga": 11}],
                fala="Ammit. Coma.")],
        "adicionais": {"ammit": {"_doc": "entra na fase 2 (mob com HP de chefe)"}},
        "mecanica_egito": {"tipo": "balanca",
            "regra": "A cada 30 s Anúbis divide o grupo: metade recebe Coração, metade Pena (sorteado, equilibrado). A Balança no centro tem dois pratos (áreas de 3 m): em 8 s, cada um precisa estar no prato da sua marca. Pesagem: se o número de jogadores em cada prato for igual (diferença de até 1), a balança fica equilibrada e todos ganham Maat (dano +20% por 15 s). Desequilibrada, o prato mais pesado afunda: quem está nele toma 50% do HP máx e Ammit pula nele. Quem ficou fora dos pratos toma 70%. Fase 2: Ammit (adicional) entra, pula no prato que pesou e precisa ser segurada por alguém resistente.",
            "a_cada_s": 30, "prazo_s": 8, "pratos": "arena.pratos", "raio_prato": 3.0, "tolerancia": 1, "maat": {"dano": 0.2, "dur_s": 15},
            "pesado_frac": 0.5, "fora_frac": 0.7, "ammit": {"desde_fase": 2, "kind": "ammit"}},
        "drop": "chefe_coracao_5", "morte": "A pena... pesou mais. Finalmente... alguma coisa pesou."},
    "farao_sem_nome": {
        "nome": "O Faraó Sem Nome", "andar": 6, "raid": "coracao_endurecido", "nivel": 60, "tags": ["morto_vivo", "rei", "nao_julgado"],
        "hp": 480000, "escala_grupo": {"base": 5, "por_jogador": 0.2, "max": 10}, "defesa": 135, "dano_base": 175, "intervalo_ataque": 1.8, "velocidade_mov": 2.0,
        "postura_max": 2200, "res": {"fogo": -.3, "sagrado": -.2, "veneno": 1.0, "sombra": .3}, "duracao_alvo_s": 480, "furia_tempo_s": 600,
        "conceito": "O faraó do Êxodo, apagado das paredes pelos próprios sacerdotes. Dez vezes disse não; na última Deus endureceu o coração dele. O coração não coube na balança: nem julgado nem devorado. Em 1962 o coração bateu. A luta é o Êxodo ao contrário: ele lança as pragas.",
        "fala_entrada": "Dez vezes ele pediu. Dez vezes eu disse não. Vocês acham que vieram me pedir alguma coisa?",
        "fases": [
            fase(1, [1.0, 0.8], "Sangue e Rãs", [
                {"id": "mangual", "mult": 1.0, "preparo": 0.6, "alcance": 2.2},
                {"id": "lanca_do_juizo", "nome": "Cajado do Rei", "mult": 1.5, "preparo": 1.0, "telegrafo": {"forma": "linha", "comprimento": 9, "largura": 1.6}, "recarga": 10},
                {"id": "pranto_que_cai", "nome": "Rãs", "mult": .8, "quantidade": 6, "intervalo": .35, "preparo": .9, "telegrafo": {"forma": "circulo", "raio": 1.3}, "recarga": 11}]),
            fase(2, [0.8, 0.6], "Piolhos, Moscas e Peste", [
                {"id": "vomito_de_brasa", "nome": "Enxame", "mult": .7, "preparo": 1.0, "telegrafo": {"forma": "cone", "raio": 6, "angulo": 70}, "ticks": 4, "efeito": {"cegueira": 3}, "recarga": 11},
                {"id": "chamar_escaravelhos", "nome": "Escaravelhos do Coração", "invoca": {"escaravelho_do_coracao": 4}, "recarga": 30}], fala="Piolho. Mosca. Peste. Eles também pediram que parasse."),
            fase(3, [0.6, 0.4], "Úlceras e Granizo", [
                {"id": "pranto_que_cai", "nome": "Granizo com Fogo", "mult": 1.3, "quantidade": 8, "intervalo": .3, "preparo": 1.0, "telegrafo": {"forma": "circulo", "raio": 1.8}, "recarga": 9},
                {"id": "marca_do_juizo", "nome": "Úlcera", "mult": 1.8, "preparo": 3.0, "telegrafo": {"forma": "circulo_segue_jogador", "raio": 2.4}, "recarga": 12}], fala="O granizo veio com fogo dentro. Eu fiquei olhando da janela."),
            fase(4, [0.4, 0.2], "Gafanhotos e Trevas", [
                {"id": "lanca_do_juizo", "nome": "Nuvem de Gafanhotos", "dupla": True, "angulo_entre": 25, "mult": 1.4, "recarga": 8},
                {"id": "vomito_de_brasa", "recarga": 9}], fala="Trevas que se podem apalpar. Apalpem."),
            fase(5, [0.2, 0.0], "A Décima", [
                {"id": "mangual", "mult": 1.3},
                {"id": "lanca_do_juizo", "encadeia": 2, "recarga": 8},
                {"id": "chamar_primogenitos", "nome": "Os Primogênitos", "invoca": {"primogenito_do_egito": 4}, "uma_vez": True}],
                fala="Falta uma. Quem vai passar esta noite por cima das portas de vocês?")],
        "mecanica_egito": {"tipo": "dez_pragas",
            "regra": "Cada fase traz duas pragas, na ordem do Êxodo, além dos ataques. 1) Sangue: o chão da arena vira sangue aos poucos (manchas que crescem; dentro, a cura recebida cai 50%). 2) Rãs: os círculos 'Rãs' deixam rãs (adicionais fracos). 3) Piolhos: cegueira (erra 30%) em 2 jogadores; só sai perto de um braseiro. 4) Moscas: o Enxame. 5) Peste: a cada 15 s um jogador adoece (2% do HP máx por s, 8 s) e passa a doença a quem chegar a 2 m dele (espalhar). 6) Úlceras: a Úlcera explode no alvo e espalha em quem estiver junto (espalhar). 7) Granizo. 8) Gafanhotos: linhas que cruzam a arena. 9) Trevas: a arena fica escura (só se enxerga a 3 m das 4 lamparinas, que se movem a cada 20 s; fora da luz o grupo perde 2% do HP máx por s). 10) A Décima (fúria em 20%): a cada 40 s o Anjo Destruidor passa: as 4 portas da arena acendem; quem não estiver sob uma porta com sangue no lintel (cada porta cabe até 3 jogadores; as portas se marcam com o sangue das manchas, interagindo nelas antes) morre. Ao morrer o Faraó deixa o Coração (objeto) para a escolha da linha N.",
            "pragas": ["sangue", "ras", "piolhos", "moscas", "peste", "ulceras", "granizo", "gafanhotos", "trevas", "decima"],
            "por_fase": [["sangue", "ras"], ["piolhos", "moscas", "peste"], ["ulceras", "granizo"], ["gafanhotos", "trevas"], ["decima"]],
            "sangue": {"cresce_s": 15, "cura_reduzida": 0.5}, "piolhos": {"alvos": 2, "erra": 0.3}, "peste": {"a_cada_s": 15, "dur_s": 8, "dano_frac_s": 0.02, "raio": 2.0},
            "trevas": {"raio_luz": 3.0, "lamparinas": "arena.lamparinas", "move_s": 20, "fora_frac_s": 0.02},
            "decima": {"a_cada_s": 40, "aviso_s": 6, "portas": "arena.portas", "por_porta": 3}, "coracao": "coracao_do_farao"},
        "drop": "chefe_coracao_6", "morte": "Eu disse não... e não... e... (o coração cai no chão do salão, inteiro, batendo)"},
}

for _c in CHEFES.values():   # Jefin 16/10: cada chefe de dungeon 1x por dia, de raid 1x por semana (ChefeEgito.vigiar)
    _c["trava"] = "semanal" if "raid" in _c else "diaria"

# ===================================================================================== drops
# Jefin 16/10: chance menor e variedade maior. Mob: ~1 item a cada 12 abates (antes 1 a cada 5). Chefe: 2 rolagens
# (antes 3 a 6), com a lista exclusiva do chefe (lendario:<chefe>, 4 ou 5 relíquias) e o conjunto da masmorra
# (lendario:regalia_*) em peso baixo; o resto é faixa 3 comum, joias, materiais e consumíveis.
from itens_egito import POR_CHEFE  # noqa: E402

def _mob(chance, material, mat_peso=26):
    return {"item_chance": chance, "rolagens": [{"tag": "equip:faixa3", "peso": 52}, {"tag": material, "peso": mat_peso}, {"tag": "joia:refino", "peso": 8},
                                                 {"tag": "consumivel:pocao_vida_m", "peso": 10}, {"tag": "consumivel:pocao_recurso_p", "peso": 6}]}

DROPS = {
    "egito_animal": _mob(0.08, "material:couro_do_nilo"),
    "egito_inseto": _mob(0.08, "material:casca_de_escaravelho"),
    "egito_mumia": _mob(0.085, "material:linho_de_mumia"),
    "egito_guardiao": _mob(0.09, "material:bronze_antigo"),
    "egito_construto": _mob(0.09, "material:po_de_calcario"),
    "egito_elite": {"rolagens_garantidas": 1, "raridade_minima": "magico", "ouro_mult": 8,
                    "rolagens": [{"tag": "equip:faixa3", "peso": 60}, {"tag": "joia:refino", "peso": 15}, {"tag": "chave:bau_de_ferro", "peso": 10},
                                 {"tag": "material:bronze_antigo", "peso": 15}]},
    "hawara": _mob(0.10, "material:ouro_de_sobek", 18),
    "raid_coracao": _mob(0.12, "material:fragmento_do_duat", 18),
}
for i, c in enumerate(["petsuchos", "esfinge_de_hawara", "serket"]):
    DROPS[f"chefe_hawara_{i + 1}"] = {"rolagens_garantidas": 2, "raridade_minima": "magico", "ouro_mult": 30 + 5 * i,
        "garantido": [["missao:brinco_de_petsuchos"], ["missao:glifo_da_resposta"], ["missao:ferrao_de_serket"]][i],
        "rolagens": [{"tag": "equip:faixa3", "peso": 62}, {"tag": "joia:refino", "peso": 14}, {"tag": "material:ouro_de_sobek", "peso": 12},
                     {"tag": f"lendario:{c}", "peso": 7}, {"tag": "lendario:regalia_de_sobek", "peso": 5}],
        "_doc": f"chance de relíquia por morte ~13%; {len(POR_CHEFE[c])} relíquias exclusivas + 5 peças da Regalia de Sobek; trava diária"}
for i, c in enumerate(["sekhmet", "janes", "imseti", "apofis", "anubis_pesador", "farao_sem_nome"], 1):
    DROPS[f"chefe_coracao_{i}"] = {"rolagens_garantidas": 2 if i < 6 else 3, "raridade_minima": "raro", "ouro_mult": 40 + 10 * i,
        "rolagens": [{"tag": "equip:faixa3", "peso": 60}, {"tag": "joia:refino", "peso": 14}, {"tag": "material:fragmento_do_duat", "peso": 12},
                     {"tag": f"lendario:{c}", "peso": 7}, {"tag": "lendario:regalia_do_farao", "peso": 7}],
        "loot_de_grupo": True,
        "_doc": f"loot pessoal (cada um rola o seu); {len(POR_CHEFE[c])} relíquias exclusivas + 8 peças da Regalia do Faraó; trava semanal"}
DROPS["chefe_coracao_6"]["garantido"] = ["missao:coracao_do_farao"]

SPRITES = {  # quando a arte própria ainda não estiver em assets/monstros/<id>/ (formato sprites_substitutos.json)
    "ibis_de_thoth": {"usa": "corvo_de_cinza", "escala": 1.2, "tint": "#d8d2c4"},
    "leoa_de_sekhmet": {"usa": "cao_de_vala_alfa", "escala": 1.4, "tint": "#c49a5a"},
}
for k, m in MOBS_DUNGEON.items():
    if m.get("sprite_de") and m["sprite_de"] != k: SPRITES[k] = {"usa": m["sprite_de"], "escala": 1.0, "tint": "#ffffff"}
for k in ("hapi", "duamutef", "qebehsenuef", "imseti", "jambres", "ammit"):
    SPRITES.pop(k, None)

NOMES_HUD = {"egito": "Egito, a Terra Negra (nv 50-70)",
             "hawara_1": "Labirinto de Hawara · Galerias Alagadas (chefe nv 51)", "hawara_2": "Labirinto de Hawara · Os Doze Pátios (chefe nv 53)",
             "hawara_3": "Labirinto de Hawara · Câmara de Amenemés (chefe nv 54)",
             "coracao_1": "O Coração Endurecido · Pátio do Sol Terço (Raid nv 60)", "coracao_2": "O Coração Endurecido · Salão dos Magos (Raid nv 60)",
             "coracao_3": "O Coração Endurecido · Câmara Canópica (Raid nv 60)", "coracao_4": "O Coração Endurecido · O Rio do Duat (Raid nv 60)",
             "coracao_5": "O Coração Endurecido · Salão das Duas Verdades (Raid nv 60)", "coracao_6": "O Coração Endurecido · Câmara do Coração (Raid nv 60)"}

LIGACAO = {"_doc": "Como chegar: Linha 7 do bonde-veleiro (estação em cada cidade). A estação de Mênfis fica na saída leste (151.5, 106.5). Ponha a ponta de lá na estação de São Lázaro (layout.py do deserto) e, quando existir, em Jerusalém.",
           "estacao_menfis": {"kind": "portal", "pos": [151.5, 106.5], "para": "area_inicial", "chegada": "estação da Linha 7 em São Lázaro", "nome": "Linha 7 · para São Lázaro", "visual": "invisivel"},
           "estacao_sao_lazaro": {"kind": "portal", "para": "egito", "chegada": [149.5, 105.0], "nome": "Linha 7 · para Mênfis (Egito, nível 50)", "nivel_minimo": 50, "visual": "invisivel"}}

DUNGEONS = {
    "labirinto_de_hawara": {"nome": "O Labirinto de Hawara", "nivel": [50, 54], "grupo": [1, 5], "andares": ["hawara_1", "hawara_2", "hawara_3"],
                            "chefes": ["petsuchos", "esfinge_de_hawara", "serket"], "trava": "diaria_por_chefe", "entrada": "egito (60.5, 31.0)"},
    "coracao_endurecido": {"nome": "O Coração Endurecido", "tipo": "raid", "nivel": 60, "grupo": [5, 10], "andares": [f"coracao_{i}" for i in range(1, 7)],
                           "chefes": ["sekhmet", "janes", "imseti", "apofis", "anubis_pesador", "farao_sem_nome"], "trava": "semanal_por_chefe",
                           "sintonia": "flag sintonia_coracao (missão n03)", "entrada": "egito (12.5, 192.0)"},
}


def exportar_dados():
    mobs = {k: {kk: vv for kk, vv in v.items() if kk not in ("sprite_de",)} for k, v in TODOS_MOBS.items()}
    out = {"_doc": "Egito, a Terra Negra (Jefin 16/10/2026). mobs: entrada completa no formato de design/combate/mobs.json (entra por data/v06_extra.json -> mobs; "
                   "`base` nas versões de dungeon/raid é só referência, os números já vêm completos). chefes: formato de design/combate/chefes.json + `escala_grupo` e "
                   "`mecanica_egito` (rodada por codigo/chefe_egito.gd). drops: tabelas novas para design/combate/drops.json -> tabelas (usam a tag nova equip:faixa3, ver INTEGRACAO.md). "
                   "sprites: substitutos só para quem ainda não tem arte. Gerado por design/mapas/egito/dados_egito.py.",
           "mobs": mobs, "chefes": CHEFES, "drops": DROPS, "sprites": SPRITES, "nomes_mapa_hud": NOMES_HUD, "ligacao": LIGACAO, "dungeons": DUNGEONS}
    os.makedirs(os.path.join(RAIZ, "entregas", "egito"), exist_ok=True)
    json.dump(out, open(os.path.join(RAIZ, "entregas", "egito", "dados.json"), "w"), ensure_ascii=False, indent=1)
    print("dados.json:", len(mobs), "mobs,", len(CHEFES), "chefes,", len(DROPS), "tabelas de drop")


if __name__ == "__main__":
    exportar_dados()
