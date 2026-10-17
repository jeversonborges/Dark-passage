"""Atlântida, a Planície Sob a Redoma (nível 30 a 45). Pedido do Jefin, 15/10/2026: "uma grande planície verdejante,
protegida por um domo de energia, só se chega por um portal; a Atlântida de Thoth ou Hermes; fidelidade; um mapa grande,
obra-prima". Conceito e lore: conceito.md (mesma pasta).

Fiel ao Crítias de Platão: a cidade real de anéis de terra e água (ilha central, dois anéis de terra, três de água),
pontes sobre os anéis, muros revestidos de bronze, estanho e oricalco, o templo de Poseidon e Clito com o Pilar das Leis
e as fontes quente e fria, o hipódromo no anel de fora, o porto com trirremes e o canal até o mar; a grande planície
irrigada por canais retos em grade, com duas colheitas por ano; as montanhas ao norte. Fiel a Thoth/Hermes: a Redoma
(o reflexo do céu) presa por sete Colunas de Hermes, uma por princípio; o Salão dos Registros com a Tábua de Esmeralda;
o Portão de Amenti nas montanhas (trancado). Bússola do mapa: norte = alto da tela (-x, +y).

Gera no MESMO formato de game/data/mapas/*.json (classe Andar de design/mapas/cripta/gerar.py):
  atlantida.json        o mapa (160 x 160)
  dados.json            mobs (formato v06_extra), sprites, chefe Gadiro (formato chefes.json), drops, ligação com o Novo Éden
  planta_atlantida.png  planta de cima para conferir
Uso: python3 gerar.py
"""
import json, math, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "cripta"))
import gerar as G
G.AQUI = AQUI
Andar, planta, porta_da_arena = G.Andar, G.planta, G.porta_da_arena

W = H = 160
C = (80.0, 80.0)            # centro da Redoma
R_CHAO = 70.5               # raio andável; a Redoma (parede de luz) fica em 71-74
S2 = math.sqrt(.5)
NORTE, LESTE, SUL, OESTE = (-S2, S2), (S2, S2), (S2, -S2), (-S2, -S2)   # direções da TELA em coordenadas do mapa
def em(p, d, r, d2=None, r2=0.0):
    x, y = p[0] + d[0]*r, p[1] + d[1]*r
    if d2: x, y = x + d2[0]*r2, y + d2[1]*r2
    return (round(x, 1), round(y, 1))

def ruido(x, y, s=0.0):
    return (.5*math.sin(x*.37 + y*.21 + s) + .3*math.sin(x*.13 - y*.29 + 1.7 + s) + .2*math.sin(x*.71 + y*.53 + 2.9*s))

def dist_seg(px, py, a, b):
    ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax)*dx + (py - ay)*dy)/(dx*dx + dy*dy)))
    return math.hypot(px - ax - t*dx, py - ay - t*dy)

def norte_de(x, y):           # quanto o ponto está ao norte (alto da tela) do centro
    return ((x - C[0])*NORTE[0] + (y - C[1])*NORTE[1])

ESMERALDA = [.22, 1.0, .62]; FOGO = [1, .45, .15]; TARDE = [1, .78, .42]; PRIMARCA = [.62, .4, 1]; SINO = [1, .86, .55]
PISOS = {"e": "relva_atlante", "c": "campo_cevada", "l": "laje_tricolor", "m": "marmore_templo", "w": "agua_canal",
         "r": "agua_canal", "z": "terra_fenda", "t": "terra", "k": "cascalho"}
G.COR_PISO.update({"e": (62, 84, 36), "c": (128, 104, 52), "l": (110, 92, 84), "m": (150, 146, 136), "w": (24, 70, 76),
                   "r": (50, 104, 104), "z": (70, 70, 72), "t": (104, 82, 56), "k": (84, 78, 70)})

# ===================================================================================== a cidade dos anéis (Crítias 115c-117e)
CIDADE = em(C, SUL, 33)                                    # a metrópole fica ao sul, junto do mar (fora da Redoma)
ANEIS = [(0, 18, "ilha"), (18, 21, "agua"), (21, 25, "anel_meio"), (25, 28, "agua"), (28, 34, "anel_fora"), (34, 37, "agua")]
R_CIDADE = 37
TEMPLO = (CIDADE[0] - 2, CIDADE[1] + 2)                    # 20 x 14, no alto da ilha
PILAR = (CIDADE[0] + 9, CIDADE[1] - 10)                     # arena do Gadiro, na frente do templo
PORTA_Y = (CIDADE[0], CIDADE[1] + R_CIDADE + 1.5)           # avenida que sobe para a planície (eixo +y)
PORTA_X = (CIDADE[0] - R_CIDADE - 1.5, CIDADE[1])           # avenida para os prados (eixo -x)

def anel_de(x, y):
    d = math.hypot(x - CIDADE[0], y - CIDADE[1])
    for (r0, r1, k) in ANEIS:
        if r0 <= d < r1: return k, d
    return None, d

# ===================================================================================== zonas e spots
ZONAS = [  # id, nome, seguro, nível
    ("posto_da_fenda", "Posto da Fenda", True, None),
    ("campos_duas_colheitas", "Campos de Duas Colheitas", False, [30, 32]),
    ("canais_retos", "Os Canais Retos", False, [32, 35]),
    ("olival_dos_parados", "Olival dos Parados", False, [34, 37]),
    ("prados_dos_elefantes", "Prados dos Elefantes", False, [36, 39]),
    ("salao_dos_registros", "Salão dos Registros", False, [38, 40]),
    ("cerco_da_coluna", "Cerco da Coluna", False, [38, 41]),
    ("aneis_e_hipodromo", "Os Anéis e o Hipódromo", False, [40, 43]),
    ("ilha_do_templo", "Ilha do Templo", False, [42, 45]),
    ("tenda_do_diapasao", "Tenda do Diapasão", True, None),
]
FENDA = em(C, LESTE, 66.5)
POSTO = em(C, LESTE, 50)
SPAWN = (FENDA[0] + 1.0, FENDA[1] - 4.5)
SALAO = em(C, NORTE, 37, LESTE, 10)
AMENTI = em(C, NORTE, 51, OESTE, 4)
CERCO = em(C, OESTE, 30, NORTE, 18)
LAGOA = em(C, OESTE, 36, SUL, 8)
TENDA = em(CERCO, NORTE, 13)      # acampamento dos Arautos, fora do alcance do sino
# centro de cada zona (a zona de um tile é a do centro mais perto; a cidade é decidida pelos anéis)
SEMENTES = [(POSTO, 0), ((104, 104), 1), ((124, 94), 1), ((88, 96), 2), ((66, 86), 2), ((84, 110), 3), ((100, 124), 3),
            (LAGOA, 4), ((44, 42), 4), (SALAO, 5), (AMENTI, 5), (CERCO, 6), (TENDA, 9)]
# spot: (id, nome, nível, [(mob, qtd)], postura, centro, raio, marco)
SPOTS = [
    ("lavoura_do_touro", "Lavoura do Touro", [30, 31], [("touro_de_poseidon", 2), ("ibis_de_thoth_atl", 2)], "neutro", (104, 104), 7.5, "chifres_consagracao"),
    ("eira_das_duas_colheitas", "Eira das Duas Colheitas", [31, 32], [("touro_de_poseidon", 2), ("vigia_de_oricalco", 2)], "neutro", (124, 94), 7.0, "feixes_cevada"),
    ("eclusa_grande", "Eclusa Grande", [32, 34], [("ibis_de_thoth_atl", 2), ("vigia_de_oricalco", 2)], "neutro", (88, 97), 7.5, "obelisco_hermetico"),
    ("cais_das_barcas", "Cais das Barcas", [33, 35], [("vigia_de_oricalco", 2), ("ibis_de_thoth_atl", 2)], "neutro", (66, 86), 7.0, "anforas"),
    ("olival_dos_parados", "Olival dos Parados", [34, 36], [("vigia_de_oricalco", 2), ("cinocefalo", 2)], "neutro", (84, 110), 7.5, "oliveira_3"),
    ("bosque_sagrado", "Bosque Sagrado", [35, 37], [("cinocefalo", 2), ("touro_de_poseidon", 2)], "neutro", (100, 124), 7.0, "estatua_babuino"),
    ("lagoa_dos_elefantes", "Lagoa dos Elefantes", [36, 38], [("elefante_de_atlas", 2), ("touro_de_poseidon", 2)], "neutro", (LAGOA[0] + 4, LAGOA[1] + 9), 7.5, "tamareira_2"),
    ("prado_das_palmeiras", "Prado das Palmeiras", [37, 39], [("elefante_de_atlas", 2), ("ibis_de_thoth_atl", 2)], "neutro", (44, 42), 7.5, "tamareira"),
    ("escadaria_dos_escribas", "Escadaria dos Escribas", [38, 40], [("cinocefalo", 2), ("ibis_de_thoth_atl", 2)], "neutro", (SALAO[0] + 5, SALAO[1] - 8), 6.5, "estatua_thoth"),
    ("cerco_da_coluna", "Cerco da Coluna", [38, 41], [("corista_do_cerco", 3), ("sineiro_do_coro", 3)], "agressivo", (CERCO[0] + 4, CERCO[1] - 5), 7.0, None),
    ("hipodromo", "O Hipódromo", [40, 42], [("hoplita_de_oricalco", 2), ("touro_de_poseidon", 2)], "neutro", em(CIDADE, OESTE, 31), 4.6, None),
    ("porto_dos_aneis", "Porto dos Anéis", [41, 43], [("hoplita_de_oricalco", 2), ("vigia_de_oricalco", 2)], "neutro", em(CIDADE, LESTE, 31), 4.6, None),
    ("patio_dos_reis", "Pátio dos Dez Reis", [42, 44], [("filho_da_serpente", 3), ("sacerdote_da_serpente", 3)], "agressivo", em(CIDADE, NORTE, 23), 3.4, None),
    ("muralha_de_oricalco", "Muralha de Oricalco", [43, 45], [("filho_da_serpente", 3), ("sacerdote_da_serpente", 3)], "agressivo", em(CIDADE, SUL, 23), 3.4, None),
]
SPOT_ZONA = {"lavoura_do_touro": 1, "eira_das_duas_colheitas": 1, "eclusa_grande": 2, "cais_das_barcas": 2, "olival_dos_parados": 3,
             "bosque_sagrado": 3, "lagoa_dos_elefantes": 4, "prado_das_palmeiras": 4, "escadaria_dos_escribas": 5, "cerco_da_coluna": 6,
             "hipodromo": 7, "porto_dos_aneis": 7, "patio_dos_reis": 8, "muralha_de_oricalco": 8}
# as estradas de laje (Crítias: "caminhos e pontes por toda a planície")
LUGARES = {"posto": POSTO, "lavoura": (104, 104), "eira": (124, 94), "eclusa": (88, 97), "cais": (66, 86), "olival": (84, 110),
           "bosque": (100, 124), "lagoa": (LAGOA[0] + 4, LAGOA[1] + 9), "palmeiras": (44, 42), "salao": SALAO, "cerco": CERCO,
           "amenti": AMENTI, "porta_y": PORTA_Y, "porta_x": PORTA_X, "fenda": FENDA}
ESTRADAS = [("fenda", "posto", 3), ("posto", "lavoura", 3), ("posto", "eira", 2), ("lavoura", "eira", 2), ("lavoura", "eclusa", 3),
            ("eclusa", "porta_y", 3), ("eclusa", "cais", 2), ("eclusa", "olival", 2), ("olival", "bosque", 2), ("olival", "salao", 2),
            ("salao", "amenti", 2), ("cais", "lagoa", 2), ("lagoa", "cerco", 2), ("lagoa", "palmeiras", 2), ("palmeiras", "porta_x", 3),
            ("cais", "cerco", 2), ("salao", "cerco", 2), ("lavoura", "bosque", 2), ("bosque", "posto", 2)]

# a grade de canais da planície (Crítias 118c-e): canais retos a cada 16 tiles, nos dois sentidos
CANAIS_X = [56, 72, 88, 104, 120]          # canais ao longo do eixo Y (x constante)
CANAIS_Y = [72, 88, 104, 120]              # canais ao longo do eixo X (y constante)
LARG_CANAL = 2

# as sete Colunas de Hermes (uma por princípio) seguram a Redoma; a do Ritmo trincou com a meia nota (a Fenda)
COLUNAS = [
    ("ritmo", "Coluna do Ritmo", em(C, LESTE, 60, NORTE, -6), True),
    ("mentalismo", "Coluna do Mentalismo", em(SALAO, NORTE, 6, OESTE, 4), False),
    ("correspondencia", "Coluna da Correspondência", (80.5, 96.5), False),
    ("vibracao", "Coluna da Vibração", CERCO, False),
    ("polaridade", "Coluna da Polaridade", em(LAGOA, SUL, 14, OESTE, 6), False),
    ("causa_e_efeito", "Coluna de Causa e Efeito", (131, 101), False),
    ("genero", "Coluna do Gênero", (108, 133), False),
]

# ===================================================================================== mobs
MOBS = {
    "touro_de_poseidon":     dict(nome="Touro de Poseidon", base="porco_pestilento", niveis=[30, 37], ajuste={"hp": 1.3, "dano": 1.1}, tags=["animal"],
                                  res={"fisico": 0.1}, usa="touro_de_poseidon", tint=None, escala=1.0, drop="atl_animal"),
    "ibis_de_thoth_atl":         dict(nome="Íbis de Thoth", base="corvo_de_cinza", niveis=[30, 40], ajuste={"hp": 1.1}, tags=["animal", "voador"],
                                  res={"sagrado": 0.3}, usa="ibis_de_thoth_atl", tint=None, escala=1.0, drop="atl_animal"),
    "vigia_de_oricalco":     dict(nome="Vigia de Oricalco", base="soldado_caido", niveis=[31, 43], ajuste={"hp": 1.35}, tags=["constructo"],
                                  res={"fisico": 0.25, "eletrico": -0.4}, usa="vigia_de_oricalco", tint=None, escala=1.0, drop="atl_guardiao"),
    "cinocefalo":            dict(nome="Cinocéfalo", base="gancheiro", niveis=[34, 40], ajuste={"dano": 1.15}, tags=["animal"],
                                  res={"sagrado": 0.3}, usa="cinocefalo", tint=None, escala=1.0, drop="atl_guardiao"),
    "elefante_de_atlas":     dict(nome="Elefante de Atlas", base="porco_pestilento", niveis=[36, 39], ajuste={"hp": 1.9, "dano": 1.2, "mov": 0.85},
                                  tags=["animal"], res={"fisico": 0.2}, usa="elefante_de_atlas", tint=None, escala=1.0, drop="atl_animal"),
    "corista_do_cerco":      dict(nome="Corista do Cerco", base="eco_da_trombeta", niveis=[38, 41], ajuste={"hp": 1.25}, tags=["celestial"],
                                  res={"sagrado": 0.5, "trevas": -0.3}, usa="corista_de_osso", tint="#e0c27a", escala=1.05, drop="atl_coro"),
    "sineiro_do_coro":       dict(nome="Sineiro do Coro", base="soldado_caido", niveis=[38, 41], ajuste={"hp": 1.4, "dano": 1.2}, tags=["celestial"],
                                  res={"sagrado": 0.5, "trevas": -0.3}, usa="querubim_da_espada", tint="#c89a5a", escala=1.08, drop="atl_coro"),
    "hoplita_de_oricalco":   dict(nome="Hoplita de Oricalco", base="soldado_caido", niveis=[40, 43], ajuste={"hp": 1.55, "dano": 1.2}, tags=["constructo"],
                                  res={"fisico": 0.3, "eletrico": -0.4}, usa="hoplita_de_oricalco", tint=None, escala=1.0, drop="atl_guardiao"),
    "filho_da_serpente":     dict(nome="Filho da Serpente", base="soldado_caido", niveis=[42, 45], ajuste={"hp": 1.45, "dano": 1.3}, tags=["demonio"],
                                  res={"veneno": 0.6, "sagrado": -0.3}, usa="filho_da_serpente", tint=None, escala=1.0, drop="atl_serpente"),
    "sacerdote_da_serpente": dict(nome="Sacerdote da Serpente", base="carpideira_de_ossos", niveis=[42, 45], ajuste={"hp": 1.2, "dano": 1.35}, tags=["demonio"],
                                  res={"veneno": 0.6, "sagrado": -0.3}, usa="sacerdote_da_serpente", tint=None, escala=1.0, drop="atl_serpente"),
    "touro_do_pilar":        dict(nome="O Touro do Pilar", base="porco_pestilento", niveis=[42, 42], ajuste={"hp": 3.0, "dano": 1.5}, tags=["animal"],
                                  res={"fisico": 0.2}, usa="touro_do_pilar", tint=None, escala=1.0, drop="elite_atl"),
}
MOTIVO = {
    "touro_de_poseidon": "os touros soltos do santuário de Poseidon; pastam a cevada e só investem se alguém mete a mão",
    "ibis_de_thoth_atl": "as aves de Thoth pescam nos canais e contam os passos de quem passa; bicam quem espanta o bando",
    "vigia_de_oricalco": "autômatos de Thotme que ainda cuidam dos canais e das eclusas; defendem-se e voltam ao trabalho",
    "cinocefalo": "os babuínos escribas de Thoth guardam as oliveiras dos Parados e o caminho do Salão",
    "elefante_de_atlas": "Crítias 114e: 'havia na ilha grande número de elefantes'; bebem na lagoa e não gostam de susto",
    "corista_do_cerco": "o Coro quer desafinar a Coluna da Vibração e terminar o Juízo que ficou pela metade",
    "sineiro_do_coro": "tocam o Diapasão do Coro dia e noite contra a Coluna; atacam quem chega perto do sino",
    "hoplita_de_oricalco": "a guarda dos anéis que Thotme forjou; patrulha o hipódromo e o porto como se a ilha ainda tivesse rei",
    "filho_da_serpente": "os Irmãos da Escuridão que Gadiro chamou; tomaram a ilha do templo e matam quem atravessa a ponte",
    "sacerdote_da_serpente": "rezam para alargar a Fenda e sair da Redoma; guardam o caminho do Pilar das Leis",
    "touro_do_pilar": "o touro que os reis laçavam para o sacrifício das leis; nunca foi caçado e ainda corre o hipódromo",
}

def chefe(nome, nivel, tags, res, fases, fala, conceito, drop):
    return {"nome": nome, "andar": 1, "nivel": nivel, "tags": tags, "hp": 400*nivel, "defesa": 2*nivel + 4,
            "dano_base": 2*nivel + 12, "intervalo_ataque": 1.8, "velocidade_mov": 2.2, "postura_max": 300 + 10*nivel, "res": res,
            "duracao_alvo_s": 170, "furia_tempo_s": 360, "dungeon": "atlantida", "conceito": conceito, "fala_entrada": fala,
            "fases": fases, "drop": drop}
def F(nn, hp, nome, ataques): return {"n": nn, "hp": hp, "nome": nome, "ataques": ataques}

CHEFES = {"gadiro": chefe("Gadiro, o Rei Que Abriu a Porta", 45, ["demonio", "humano"], {"veneno": 0.6, "sagrado": -0.3, "fisico": 0.1}, [
    F(1, [1.0, 0.65], "O Gêmeo de Atlas", [{"id": "golpe_de_tridente", "nome": "Tridente Partido", "mult": 1.0, "preparo": 0.6, "alcance": 2.0},
                                            {"id": "arrasto", "nome": "Laço da Cauda", "mult": 1.4, "preparo": 0.9, "telegrafo": {"forma": "linha", "comprimento": 7, "largura": 1.2}, "deslocamento": 5, "recarga": 9},
                                            {"id": "giro_da_serpente", "nome": "Abraço da Serpente", "mult": 1.5, "preparo": 1.0, "telegrafo": {"forma": "circulo", "raio": 3.4}, "recarga": 8}]),
    F(2, [0.65, 0.3], "A Porta de Baixo", [{"id": "vomito_de_brasa", "nome": "Peçonha", "mult": 1.2, "preparo": 0.9, "telegrafo": {"forma": "cone", "raio": 5, "angulo": 60}, "ticks": 3, "intervalo_tick": 0.4, "recarga": 8},
                                           {"id": "chamar_irmaos", "invoca": {"filho_da_serpente": 2}, "uma_vez": True},
                                           {"id": "arrasto", "recarga": 7}]),
    F(3, [0.3, 0.0], "Num Só Dia e Numa Noite", [{"id": "pranto_que_cai", "nome": "O Mar Que Cai", "mult": 1.3, "quantidade": 7, "intervalo": 0.45, "preparo": 0.8, "telegrafo": {"forma": "circulo", "raio": 1.6}, "recarga": 7},
                                                 {"id": "marca_do_juizo", "nome": "A Lei Quebrada", "mult": 2.0, "preparo": 1.8, "telegrafo": {"forma": "circulo", "raio": 2.4}, "recarga": 9}])],
    "Meu irmão escreveu as leis no pilar. Eu li o que estava escrito embaixo.",
    "Gêmeo de Atlas e rei da ponta da ilha voltada para Gades (Crítias 114b). Abriu os portões de baixo e chamou os Irmãos da "
    "Escuridão; a Serpente que ele chamou se fundiu a ele, e ele está enrolado no Pilar das Leis há onze mil anos.", "chefe_gadiro")}
SPR_CHEFES = {"gadiro": {"usa": "gadiro", "escala": 1.0}}
DROPS = {
    "atl_animal": {"item_chance": 0.18, "rolagens": [{"tag": "material:pena_suja", "peso": 25}, {"tag": "equip:faixa2", "peso": 60}, {"tag": "joia:refino", "peso": 15}]},
    "atl_guardiao": {"item_chance": 0.22, "rolagens": [{"tag": "equip:faixa2", "peso": 78}, {"tag": "joia:refino", "peso": 22}]},
    "atl_coro": {"item_chance": 0.24, "rolagens": [{"tag": "equip:faixa2", "peso": 76}, {"tag": "joia:refino", "peso": 24}]},
    "atl_serpente": {"item_chance": 0.26, "rolagens": [{"tag": "equip:faixa2", "peso": 74}, {"tag": "joia:refino", "peso": 26}]},
    "elite_atl": {"rolagens_garantidas": 2, "raridade_minima": "magico", "ouro_mult": 10, "rolagens": [{"tag": "equip:faixa2", "peso": 78}, {"tag": "joia:refino", "peso": 22}]},
    "chefe_gadiro": {"rolagens_garantidas": 5, "raridade_minima": "raro", "ouro_mult": 45,
                     "rolagens": [{"tag": "equip:faixa2", "peso": 70}, {"tag": "joia:refino", "peso": 18}, {"tag": "lendario:zacarias", "peso": 12}]},
}

# ===================================================================================== textos no mundo (objetos "leitura")
from textos import TEXTOS     # noqa: E402  (textos.py, mesma pasta)


def atlantida():
    a = Andar("atlantida", "Atlântida", W, H, "e", None, {})
    rng = a.rng
    zona = [[None]*W for _ in range(H)]
    estrada = [[0]*W for _ in range(H)]
    canal = [[False]*W for _ in range(H)]
    serra = [[False]*W for _ in range(H)]

    # ---- o chão dentro da Redoma
    for y in range(H):
        for x in range(W):
            px, py = x + .5, y + .5
            d = math.hypot(px - C[0], py - C[1])
            if d > R_CHAO + .8*ruido(px, py, 4): continue
            a.blk[y][x] = False; a.ter[y][x] = "e"
            k, dc = anel_de(px, py)
            if k is not None or dc < R_CIDADE + 1.5:
                zona[y][x] = 8 if (k in ("ilha", "anel_meio") or dc < 25) else 7
            else:
                zona[y][x] = min(SEMENTES, key=lambda s: math.hypot(px - s[0][0], py - s[0][1])*(1 + .08*ruido(px, py, s[1])))[1]
            # as montanhas ao norte (Crítias 118a-b), com a garganta que sobe ao Portão de Amenti
            n = norte_de(px, py)
            garganta = dist_seg(px, py, SALAO, AMENTI) < 3.2 or math.hypot(px - AMENTI[0], py - AMENTI[1]) < 6
            if n > 47 + 3.5*ruido(px*.8, py*.8, 7) and not garganta:
                serra[y][x] = True; a.blk[y][x] = True; a.ter[y][x] = "k"
            elif n > 42 + 3*ruido(px, py, 9): a.ter[y][x] = "k"

    # ---- a cidade dos anéis
    for y in range(H):
        for x in range(W):
            if a.ter[y][x] == " ": continue
            px, py = x + .5, y + .5
            k, dc = anel_de(px, py)
            if k == "ilha": a.ter[y][x] = "m"
            elif k == "agua": a.ter[y][x] = "w"; a.blk[y][x] = True
            elif k == "anel_meio": a.ter[y][x] = "l"
            elif k == "anel_fora": a.ter[y][x] = "t" if 30 <= dc < 32.6 else "l"     # a pista do hipódromo no meio do anel
            elif dc < R_CIDADE + 2.2: a.ter[y][x] = "l"                              # o cais de fora
    # o canal do mar (Crítias 115d: 50 estádios até o mar) e o porto com as trirremes
    for y in range(H):
        for x in range(W):
            if a.ter[y][x] == " ": continue
            px, py = x + .5, y + .5
            if py < CIDADE[1] - 34 and abs(px - CIDADE[0]) < 2.6: a.ter[y][x] = "w"; a.blk[y][x] = True
            if CIDADE[1] - 46 < py < CIDADE[1] - 39.5 and abs(px - (CIDADE[0] - 9)) < 9.5: a.ter[y][x] = "w"; a.blk[y][x] = True
            if (CIDADE[1] - 47.5 < py <= CIDADE[1] - 46 or CIDADE[1] - 39.5 <= py < CIDADE[1] - 38) and abs(px - (CIDADE[0] - 9)) < 10.5 and a.ter[y][x] != "w":
                a.ter[y][x] = "l"

    # ---- a grade de canais da planície (só na planície: fora da cidade, do Posto, da serra, do Salão e do Cerco)
    def planicie(px, py, folga=0):
        return (math.hypot(px - CIDADE[0], py - CIDADE[1]) > R_CIDADE + 3 + folga and math.hypot(px - POSTO[0], py - POSTO[1]) > 11 + folga
                and norte_de(px, py) < 38 - folga and math.hypot(px - CERCO[0], py - CERCO[1]) > 12 + folga
                and math.hypot(px - SALAO[0], py - SALAO[1]) > 10 + folga and math.hypot(px - C[0], py - C[1]) < 62 - folga
                and math.hypot(px - LAGOA[0], py - LAGOA[1]) > 9 + folga and math.hypot(px - TENDA[0], py - TENDA[1]) > 8 + folga)
    for y in range(H):
        for x in range(W):
            if a.blk[y][x]: continue
            px, py = x + .5, y + .5
            if not planicie(px, py) or (px < 84 and py < 50): continue
            if any(cx <= x < cx + LARG_CANAL for cx in CANAIS_X) or any(cy <= y < cy + LARG_CANAL for cy in CANAIS_Y):
                a.ter[y][x] = "w"; a.blk[y][x] = True; canal[y][x] = True
    # a lagoa dos elefantes
    for y in range(H):
        for x in range(W):
            if a.ter[y][x] == " ": continue
            d = math.hypot(x + .5 - LAGOA[0], y + .5 - LAGOA[1]) - 5.2 - .9*ruido(x*1.3, y*1.3, 3)
            if d < -1.2: a.ter[y][x] = "w"; a.blk[y][x] = True
            elif d < 0: a.ter[y][x] = "r"; a.blk[y][x] = False

    # ---- estradas de laje entre os lugares
    for (u, v, larg) in ESTRADAS:
        p0, p1 = LUGARES[u], LUGARES[v]
        for y in range(H):
            for x in range(W):
                if a.ter[y][x] == " " or serra[y][x]: continue
                if dist_seg(x + .5, y + .5, p0, p1) < larg/2 + .15*ruido(x, y, 2):
                    estrada[y][x] = max(estrada[y][x], larg)
    # avenidas da cidade: atravessam os anéis em linha reta até a ilha
    for y in range(H):
        for x in range(W):
            if a.ter[y][x] == " ": continue
            px, py = x + .5, y + .5
            if abs(px - CIDADE[0]) < 1.6 and CIDADE[1] < py < PORTA_Y[1] + 1: estrada[y][x] = 3
            if abs(py - CIDADE[1]) < 1.6 and PORTA_X[0] - 1 < px < CIDADE[0]: estrada[y][x] = 3
    pontes = []
    for y in range(H):
        for x in range(W):
            if not estrada[y][x]: continue
            if a.ter[y][x] in "wr":
                a.ter[y][x] = "r"; a.blk[y][x] = False     # sob a ponte: água rasa andável (a ponte cobre)
            elif a.ter[y][x] not in "m": a.ter[y][x] = "l"
    # uma ponte (prop de chão) em cada travessia: agrupa os tiles de água rasa das estradas
    vistos = set()
    for y in range(H):
        for x in range(W):
            if a.ter[y][x] != "r" or not estrada[y][x] or (x, y) in vistos: continue
            pilha, grupo = [(x, y)], []
            vistos.add((x, y))
            while pilha:
                cx_, cy_ = pilha.pop(); grupo.append((cx_, cy_))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    q = (cx_ + dx, cy_ + dy)
                    if 0 <= q[0] < W and 0 <= q[1] < H and q not in vistos and a.ter[q[1]][q[0]] == "r" and estrada[q[1]][q[0]]:
                        vistos.add(q); pilha.append(q)
            gx = sum(p[0] for p in grupo)/len(grupo) + .5; gy = sum(p[1] for p in grupo)/len(grupo) + .5
            # sentido: a água corre ao longo de x (canal em y constante) -> a ponte vai ao longo de y
            def eh_agua(qx, qy): return 0 <= qx < W and 0 <= qy < H and a.ter[qy][qx] == "w"
            agua_x = sum(eh_agua(p[0] - 1, p[1]) + eh_agua(p[0] + 1, p[1]) for p in grupo)   # água dos lados em x: o caminho corre em y
            agua_y = sum(eh_agua(p[0], p[1] - 1) + eh_agua(p[0], p[1] + 1) for p in grupo)
            k = "ponte_laje_y" if agua_x > agua_y else "ponte_laje"
            pontes.append((gx, gy)); a.prop(k, round(gx, 1), round(gy, 1), chao=True)
    # cais de laje ao longo dos canais (uma fiada de cada lado)
    for y in range(H):
        for x in range(W):
            if a.blk[y][x] or a.ter[y][x] not in "e": continue
            if any(0 <= x + dx < W and 0 <= y + dy < H and canal[y + dy][x + dx] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                a.ter[y][x] = "l"

    # ---- os Campos de Duas Colheitas: lotes de cevada entre os canais, com uma faixa de relva na beira
    for y in range(H):
        for x in range(W):
            if a.ter[y][x] != "e" or zona[y][x] not in (1, 2): continue
            cx_ = max([c for c in CANAIS_X if c <= x] or [0]); cy_ = max([c for c in CANAIS_Y if c <= y] or [0])
            lote = (cx_*31 + cy_*17) % 7
            ix, iy = x - cx_, y - cy_
            if lote < (5 if zona[y][x] == 1 else 2) and 3 <= ix <= 13 and 3 <= iy <= 13: a.ter[y][x] = "c"
    # a língua de cinza que entra pela Fenda (o único cinza da área)
    for y in range(H):
        for x in range(W):
            if a.blk[y][x] or a.ter[y][x] == " ": continue
            d = dist_seg(x + .5, y + .5, FENDA, POSTO) + 2.5*ruido(x*1.4, y*1.4, 6)
            if math.hypot(x + .5 - FENDA[0], y + .5 - FENDA[1]) < 7 + 1.5*ruido(x, y, 8) or d < 2.2: a.ter[y][x] = "z"

    # ---- zonas de nível dentro da cidade e conferência das zonas
    for y in range(H):
        for x in range(W):
            if a.ter[y][x] == " ": zona[y][x] = None

    # ---- utilitários de colocação
    area_spot = [(sp[5][0], sp[5][1], sp[6]) for sp in SPOTS]
    def em_spot(x, y, folga=0): return any(math.hypot(x - sx, y - sy) < sr + folga for sx, sy, sr in area_spot)
    def agua(x, y): return not (0 <= x < W and 0 <= y < H) or a.ter[int(y)][int(x)] in "rw"
    def livre3(x, y): return all(a.livre(int(x) + dx, int(y) + dy) and not agua(int(x) + dx, int(y) + dy) and (int(x) + dx, int(y) + dy) not in a.extra_blk for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    def perto_prop(x, y, d): return any(math.dist((x, y), (p["x"], p["y"])) < d for p in a.props if not p.get("chao"))
    def na_estrada(x, y, f=0): return any(0 <= int(x) + dx < W and 0 <= int(y) + dy < H and estrada[int(y) + dy][int(x) + dx] for dx in range(-f, f + 1) for dy in range(-f, f + 1))
    reservado = []          # (x, y, r): praças e marcos que nada pode cobrir
    def livre_de_reserva(x, y, d=0): return all(math.hypot(x - rx, y - ry) > rr + d for rx, ry, rr in reservado)

    # ---- a Redoma: parede de luz esmeralda ao redor de tudo (alta atrás, baixa na frente para não tapar a vista)
    n_b = int(2*math.pi*72.5/2.1)
    for i in range(n_b):
        ang = i/n_b*2*math.pi
        x, y = C[0] + math.cos(ang)*72.4, C[1] + math.sin(ang)*72.4
        if not (1 < x < W - 1 and 1 < y < H - 1): continue
        frente = (math.cos(ang)*SUL[0] + math.sin(ang)*SUL[1]) > .25        # metade de baixo da tela
        if norte_de(x, y) > 45 and not frente: continue                      # atrás da serra a Redoma some nos picos
        a.prop("borda_domo_baixa" if frente else "borda_domo", round(x, 2), round(y, 2), decor_moldura=True)
        if i % 9 == 0: a.luzes.append([round(x, 2), round(y, 2)] + ESMERALDA + [5])
    # a serra: rochedos na borda da área bloqueada (os de trás maiores)
    feitos = []
    for y in range(H):
        for x in range(W):
            if not serra[y][x]: continue
            viz = any(0 <= x + dx < W and 0 <= y + dy < H and not a.blk[y + dy][x + dx] for dx in range(-3, 4) for dy in range(-3, 4))
            if not viz or rng.random() < .55: continue
            px, py = x + rng.uniform(.2, .8), y + rng.uniform(.2, .8)
            if any(math.dist((px, py), f) < 4.2 for f in feitos): continue
            feitos.append((px, py)); a.prop(rng.choice(["rochedo", "rochedo_2", "rochedo"]), px, py, decor_moldura=True)
    for y in range(0, H, 3):              # ciprestes e oliveiras ao pé da serra
        for x in range(0, W, 3):
            if a.blk[y][x] or a.ter[y][x] != "k" or rng.random() < .55: continue
            px, py = x + rng.uniform(0, 2), y + rng.uniform(0, 2)
            if not a.livre(int(px), int(py)) or perto_prop(px, py, 2.6) or na_estrada(px, py, 1): continue
            if math.hypot(px - AMENTI[0], py - AMENTI[1]) < 8 or math.hypot(px - SALAO[0], py - SALAO[1]) < 9: continue
            a.prop(rng.choice(["cipreste", "cipreste_2", "oliveira_2", "rochedo_2" if rng.random() < .1 else "mirto"]), px, py, bloqueia=.6)

    # ---- A FENDA e o Posto da Fenda (Vigília, zona segura)
    fx, fy = FENDA
    a.prop("fenda", fx, fy, bloqueia=1.6, luz=ESMERALDA + [10], marco="a_fenda")
    reservado.append((fx, fy, 3.5))
    a.portal(fx - .5, fy - 2.6, "mata_do_granizo", [52.0, 9.0], "A Fenda · de volta ao Novo Éden", visual="portal_dungeon_lume")
    px_, py_ = POSTO
    reservado.append((px_, py_, 7.5))
    a.prop("tenda_vigilia", px_ - 4.5, py_ + 3.0, bloqueia=1.4); a.prop("tenda_vigilia", px_ + 2.5, py_ + 5.5, bloqueia=1.4)
    a.prop("tenda_vigilia", px_ - 6.5, py_ - 2.5, bloqueia=1.4)
    a.prop("fogueira", px_ + 1.0, py_ - 1.0, bloqueia=.5, luz=FOGO + [7])
    a.prop("carrinho_tobias", px_ + 3.0, py_ - .2, bloqueia=.5, ponto="descanso")
    a.prop("bancada_ferreiro", px_ - 3.5, py_ + 6.5, bloqueia=.6); a.prop("caixas", px_ - 7.0, py_ + 1.0, bloqueia=.5)
    a.prop("barris", px_ - 6.0, py_ + 5.0, bloqueia=.5); a.prop("tanque_latao", px_ + 5.5, py_ + 3.0, bloqueia=1.0)
    a.prop("guindaste_sucata", px_ - 1.0, py_ + 8.5, bloqueia=1.2)
    for (dx, dy) in [(-2.5, -4.5), (4.5, -3.5), (6.5, 6.5), (-8.5, -.5)]: a.prop("lampiao_gas", px_ + dx, py_ + dy, bloqueia=.2, luz=FOGO + [5])
    # a praça do Primarca (pedido da thread "Gustavo o Primarca"): Arca no meio do Posto, de frente para quem chega da Fenda
    ax, ay = px_ + 2.5, py_ - 5.0
    a.prop("marcador_npc", ax + 1.6, ay - 1.6, invisivel=True, nota="praça do Primarca (livre)")
    a.prop("arca_primarca", ax, ay, bloqueia=.9, ponto="arca_primarca_atlantida", objeto="arca_primarca", luz=PRIMARCA + [6])
    a.prop("caldeira_vapor", ax - 1.5, ay + 1.5, bloqueia=.9, luz=FOGO + [3])
    for (dx, dy) in [(-1.6, -1.2), (1.2, 1.6)]: a.prop("poste_gas", ax + dx, ay + dy, bloqueia=.2, luz=[1, .8, .5, 4])
    for (dx, dy) in [(.4, -1.3), (-.9, -1.6), (1.5, .2)]: a.prop("velas_chao", ax + dx, ay + dy, chao=True, luz=[1, .7, .35, 1.5])
    for (dx, dy) in [(-2.8, .4), (.3, 2.9)]: a.prop("obelisco_hermetico", ax + dx, ay + dy, bloqueia=.4, luz=ESMERALDA + [2])
    reservado.append((ax + 1.6, ay - 1.6, 2.6))
    a.npcs.append({"id": "gustavo_primarca", "ponto": "arca_primarca_atlantida", "x": round(ax + 1.5, 2), "y": round(ay + .5, 2)})
    a.objetos.append({"kind": "leitura", "pos": [px_ - 2.0, py_ - 3.0], "nome": TEXTOS["despacho_da_vela"]["nome"], "texto": TEXTOS["despacho_da_vela"]["texto"], "visual": "placa_versiculo"})
    a.prop("placa_versiculo", px_ - 2.0, py_ - 3.0, bloqueia=.3)
    a.objetos.append({"kind": "leitura", "pos": [px_ + 6.0, py_ + 6.0], "nome": TEXTOS["radio_sao_lazaro"]["nome"], "texto": TEXTOS["radio_sao_lazaro"]["texto"], "visual": "poste_telegrafo"})
    a.prop("poste_telegrafo", px_ + 6.5, py_ + 7.0, bloqueia=.3)
    # a volta de Thoth (lore do Jefin, 16/10): o despacho da Iolanda pregado na bancada
    a.objetos.append({"kind": "leitura", "pos": [round(px_ - 4.6, 1), round(py_ + 5.0, 1)], "nome": TEXTOS["despacho_da_volta"]["nome"], "texto": TEXTOS["despacho_da_volta"]["texto"], "visual": "placa_versiculo"})
    a.prop("placa_versiculo", round(px_ - 4.6, 1), round(py_ + 5.0, 1), bloqueia=.3)
    # NPCs do Posto (design/missoes: conteudo.py): Iolanda na bancada, o cabo Nestor de guarda virado para a Fenda
    a.npcs.append({"id": "iolanda_prumo", "ponto": "bancada_iolanda", "x": round(px_ - 2.5, 2), "y": round(py_ + 5.3, 2)})
    a.npcs.append({"id": "cabo_nestor", "ponto": "guarita_fenda", "x": round(px_ + 7.5, 2), "y": round(py_ + .5, 2)})

    # ---- Tenda do Diapasão: acampamento dos Arautos (Sinésia e Belzarim), seguro
    tx_, ty_ = TENDA
    reservado.append((tx_, ty_, 6.5))
    a.prop("tenda_demonio", tx_ - 3.0, ty_ + 2.0, bloqueia=1.4); a.prop("tenda_demonio", tx_ + 2.5, ty_ + 3.5, bloqueia=1.4)
    a.prop("braseiro_sagrado", tx_, ty_ - .5, bloqueia=.5, luz=[1, .95, .85, 6])
    for (dx, dy) in [(-3.5, -2.5), (3.5, -1.5)]: a.prop("braseiro_ferro", tx_ + dx, ty_ + dy, bloqueia=.4, luz=FOGO + [4])
    a.prop("estandarte_rasgado", tx_ - 1.0, ty_ + 4.5, bloqueia=.3); a.prop("estandarte_portadora", tx_ + 4.5, ty_ + .5, bloqueia=.3)
    a.prop("caixas", tx_ + 2.0, ty_ - 2.5, bloqueia=.5); a.prop("barris", tx_ - 4.5, ty_ + .5, bloqueia=.5)
    a.npcs.append({"id": "irma_sinesia", "ponto": "tenda_sinesia", "x": round(tx_ - 1.5, 2), "y": round(ty_ + .8, 2)})
    a.npcs.append({"id": "belzarim", "ponto": "caixote_belzarim", "x": round(tx_ + 1.6, 2), "y": round(ty_ - 1.6, 2)})
    a.objetos.append({"kind": "leitura", "pos": [tx_ + .5, ty_ + 2.5], "nome": TEXTOS["versiculo_do_coro"]["nome"], "texto": TEXTOS["versiculo_do_coro"]["texto"], "visual": "placa_versiculo"})
    a.prop("placa_versiculo", tx_ + .5, ty_ + 2.5, bloqueia=.3)
    a.objetos.append({"kind": "leitura", "pos": [round(tx_ - 3.5, 1), round(ty_ + 3.6, 1)], "nome": TEXTOS["versiculo_da_heresia"]["nome"], "texto": TEXTOS["versiculo_da_heresia"]["texto"], "visual": "placa_versiculo"})
    a.prop("placa_versiculo", round(tx_ - 3.5, 1), round(ty_ + 3.6, 1), bloqueia=.3)

    # ---- as sete Colunas de Hermes
    for (cid, nome, (cx_, cy_), trinc) in COLUNAS:
        a.prop("coluna_hermes_trincada" if trinc else "coluna_hermes", cx_, cy_, bloqueia=1.4, marco=f"coluna_{cid}", luz=ESMERALDA + [8 if not trinc else 6])
        reservado.append((cx_, cy_, 3.2))
        t = TEXTOS[f"coluna_{cid}"]
        a.objetos.append({"kind": "leitura", "pos": [round(cx_ + 2.2, 1), round(cy_ - 2.2, 1)], "nome": t["nome"], "texto": t["texto"], "visual": "coluna_hermes"})
        if cid == "ritmo": a.objetos.append({"kind": "interativo", "obj": "coluna_do_ritmo", "pos": [round(cx_ - 2.2, 1), round(cy_ + 2.2, 1)]})

    # ---- o Salão dos Registros (Thoth) e a Tábua de Esmeralda
    sx, sy = SALAO
    a.prop("tabua_esmeralda", sx, sy, bloqueia=1.6, marco="tabua_de_esmeralda", luz=ESMERALDA + [9])
    reservado.append((sx, sy, 5))
    t = TEXTOS["tabua_de_esmeralda"]
    a.objetos.append({"kind": "leitura", "pos": [sx + 2.5, sy - 2.5], "nome": t["nome"], "texto": t["texto"], "visual": "tabua_esmeralda"})
    a.npcs.append({"id": "thotme", "ponto": "nicho_thotme", "x": round(sx - 3.0, 2), "y": round(sy + .2, 2)})
    a.objetos.append({"kind": "interativo", "obj": "tabua_de_esmeralda_obj", "pos": [sx + 1.6, sy - 1.6]})
    a.prop("estatua_thoth", sx - 4.5, sy + 1.5, bloqueia=1.0); a.prop("estatua_babuino", sx + 1.5, sy + 4.5, bloqueia=1.0)
    a.prop("estatua_babuino", sx - 3.0, sy - 3.5, bloqueia=1.0)
    for k in range(6):
        ang = math.radians(200 + k*28)
        a.prop("colunata_a" if k % 2 else "colunata_b", round(sx + math.cos(ang)*7.5, 1), round(sy + math.sin(ang)*7.5, 1), bloqueia=.7)
    for (dx, dy) in [(3.5, -1.0), (-1.0, -5.5)]: a.prop("tripode", sx + dx, sy + dy, bloqueia=.4, luz=FOGO + [4])
    # peças da thread "Biblioteca e mistérios" (texto vem do servidor): pedra gravada no chão entre as colunatas k=2 e k=3,
    # e um degrau entalhado que não leva a lugar nenhum na entrada do Salão (do lado de quem chega da planície)
    c2 = [sx + math.cos(math.radians(200 + k*28))*7.5 for k in (2, 3)], [sy + math.sin(math.radians(200 + k*28))*7.5 for k in (2, 3)]
    ix_, iy_ = round(sum(c2[0])/2, 1), round(sum(c2[1])/2, 1)
    a.prop("laje_rolada", ix_, iy_, chao=True)
    a.objetos.append({"kind": "interativo", "obj": "inscricao_05", "pos": [ix_, iy_]})
    a.prop("velas_chao", ix_ + .4, iy_ - .3, chao=True, luz=[1, .7, .35, 1.0])
    dx_, dy_ = em(SALAO, SUL, 8.5)
    a.prop("pedra_coberta", round(dx_, 1), round(dy_, 1), bloqueia=.4)
    a.objetos.append({"kind": "interativo", "obj": "pedra_entalhada_b", "pos": [round(dx_, 1), round(dy_, 1)]})
    t = TEXTOS["cronica_do_emparedado"]
    a.objetos.append({"kind": "leitura", "pos": [sx - 6.0, sy - 2.0], "nome": t["nome"], "texto": t["texto"], "visual": "obelisco_hermetico"})
    a.prop("obelisco_hermetico", sx - 6.0, sy - 2.0, bloqueia=.4)
    # o Portão de Amenti (Tábua II: os Salões de Amenti, embaixo da terra), trancado
    mx, my = AMENTI
    a.prop("portao_amenti", mx, my, bloqueia=2.2, marco="portao_de_amenti", luz=ESMERALDA + [7])
    reservado.append((mx, my, 4))
    a.portal(mx + 1.5, my - 3.0, "saloes_de_amenti", [60.0, 8.5], "Os Salões de Amenti", visual="portal_dungeon_lume",
             requer_flag="amenti_aberto", texto_trancado="A pedra não tem fechadura. Tem uma pergunta escrita, e você ainda não sabe a resposta.")

    # ---- o Cerco da Coluna (Coro, agressivo): o sino de bronze contra a Coluna da Vibração
    cx_, cy_ = CERCO
    a.prop("diapasao_coro", cx_ + 4.5, cy_ - 1.5, bloqueia=1.2, marco="diapasao_do_coro", luz=SINO + [6])
    for (dx, dy) in [(-5, -4), (6, 4), (0, -7)]: a.prop("braseiro_sagrado", cx_ + dx, cy_ + dy, bloqueia=.4, luz=SINO + [5])
    for (dx, dy) in [(-7, 2), (2, 7.5)]: a.prop("lanterna_procissao", cx_ + dx, cy_ + dy, bloqueia=.3, luz=SINO + [4])
    a.prop("pilar_porcelana", cx_ - 6.5, cy_ + 6.0, bloqueia=.7); a.prop("anjo_porcelana_caido", cx_ + 8.0, cy_ - 6.0, bloqueia=.8)
    t = TEXTOS["versiculo_do_coro"]
    a.objetos.append({"kind": "leitura", "pos": [cx_ + 7.0, cy_ + 1.0], "nome": t["nome"], "texto": t["texto"], "visual": "placa_versiculo"})
    a.prop("placa_versiculo", cx_ + 7.0, cy_ + 1.0, bloqueia=.3)

    # ---- a Ilha do Templo
    tx, ty = TEMPLO
    a.prop("templo_poseidon", tx, ty, bloqueia=0, marco="templo_de_poseidon", luz=TARDE + [10])
    for yy in range(int(ty - 6.5), int(ty + 7.5)):
        for xx in range(int(tx - 9.5), int(tx + 10.5)): a.extra_blk.add((xx, yy))
    reservado.append((tx, ty, 10.5))
    plx, ply = PILAR
    a.prop("pilar_leis", plx, ply, bloqueia=1.2, marco="pilar_das_leis", luz=TARDE + [7])
    reservado.append((plx, ply, 5.5))
    t = TEXTOS["pilar_das_leis"]
    a.objetos.append({"kind": "leitura", "pos": [plx - 2.5, ply + 2.5], "nome": t["nome"], "texto": t["texto"], "visual": "pilar_leis"})
    a.prop("fontes_gemeas", CIDADE[0] - 10, CIDADE[1] - 8, bloqueia=1.6, marco="fontes_quente_e_fria", luz=[.6, .85, 1, 5])
    a.prop("estatua_poseidon", CIDADE[0] - 1, CIDADE[1] - 13, bloqueia=1.6, marco="estatua_de_poseidon")
    for (dx, dy) in [(-6, -5), (6, -4.5), (3, -12), (-12, -1)]: a.prop("tripode", CIDADE[0] + dx, CIDADE[1] + dy, bloqueia=.4, luz=FOGO + [5])
    a.prop("chifres_consagracao", CIDADE[0] + 14, CIDADE[1] - 3, bloqueia=.8)
    # muros dos anéis junto das portas (bronze no de fora, estanho no do meio, oricalco na cidadela) e torres de portão
    for (r_muro, metal, torre) in [(36.6, "muralha_bronze", True), (27.6, "muralha_estanho", True), (20.6, "muralha_oricalco", False)]:
        for k in range(-7, 8):
            if abs(k) <= 2: continue
            # avenida +y: tangente ao longo de x
            a.prop(metal + "_a", CIDADE[0] + k*.707*1.0 + .0, round(CIDADE[1] + r_muro - .3, 2), bloqueia=0)
            a.extra_blk.add((int(CIDADE[0] + k*.707), int(CIDADE[1] + r_muro - .3)))
            # avenida -x: tangente ao longo de y
            a.prop(metal + "_b", round(CIDADE[0] - r_muro + .3, 2), CIDADE[1] + k*.707, bloqueia=0)
            a.extra_blk.add((int(CIDADE[0] - r_muro + .3), int(CIDADE[1] + k*.707)))
        if torre:
            for s_ in (-1, 1):
                a.prop("torre_portao", CIDADE[0] + s_*3.2, CIDADE[1] + r_muro + .8, bloqueia=1.2, luz=FOGO + [5])
                a.prop("torre_portao", CIDADE[0] - r_muro - .8, CIDADE[1] + s_*3.2, bloqueia=1.2, luz=FOGO + [5])
    # o colosso de Atlas guarda a avenida que sobe para a planície
    a.prop("estatua_atlas", PORTA_Y[0] + 6.5, PORTA_Y[1] + 4.5, bloqueia=2.2, marco="colosso_de_atlas")
    reservado.append((PORTA_Y[0] + 6.5, PORTA_Y[1] + 4.5, 3.5))
    # casas de pedra tricolor no anel do meio e no cais de fora
    for k in range(10):
        ang = math.radians(15 + k*36)
        for (rr_, kk) in [(21.9, "casa_atlante"), (35.9, None)]:   # coladas na borda de dentro: o anel fica andável em volta
            x, y = CIDADE[0] + math.cos(ang)*rr_, CIDADE[1] + math.sin(ang)*rr_
            if kk and not na_estrada(x, y, 4) and livre_de_reserva(x, y, 3) and not em_spot(x, y, 1):
                a.prop(rng.choice(["casa_atlante", "casa_atlante_2"]), round(x, 1), round(y, 1), bloqueia=1.0)
    # o hipódromo: estátuas e chifres na beira da pista; o porto com as trirremes
    for k in range(16):
        ang = math.radians(k*22.5 + 11)
        x, y = CIDADE[0] + math.cos(ang)*29.0, CIDADE[1] + math.sin(ang)*29.0
        if na_estrada(x, y, 2) or not a.livre(int(x), int(y)) or em_spot(x, y, -1): continue
        a.prop(["obelisco_hermetico", "chifres_consagracao", "cipreste", "tripode"][k % 4], round(x, 1), round(y, 1), bloqueia=.5,
               luz=FOGO + [4] if k % 4 == 3 else None)
    for (bx, by) in [(CIDADE[0] - 13, CIDADE[1] - 42.6), (CIDADE[0] - 3.5, CIDADE[1] - 42.9)]:
        a.prop("trirreme", round(bx, 1), round(by, 1), chao=False, bloqueia=0)
    t = TEXTOS["caderno_do_coveiro"]
    a.objetos.append({"kind": "leitura", "pos": [CIDADE[0] - 17.5, CIDADE[1] - 38.0], "nome": t["nome"], "texto": t["texto"], "visual": "anforas"})
    a.prop("anforas", CIDADE[0] - 18.0, CIDADE[1] - 37.0, bloqueia=.6)

    # ---- canais: eclusas nos cruzamentos, ciprestes em fila ao longo das margens, papiro e lótus na água
    for cxx in CANAIS_X:
        for cyy in CANAIS_Y:
            x, y = cxx + 1.0, cyy + 1.0
            if a.ter[int(y)][int(x)] == "w" and canal[int(y)][int(x)] and rng.random() < .6:
                a.prop("eclusa" if rng.random() < .5 else "eclusa_y", x, y, chao=False, bloqueia=0)
    for y in range(H):
        for x in range(W):
            if a.ter[y][x] != "l" or estrada[y][x] or a.blk[y][x]: continue
            viz_canal = [(dx, dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= x + dx < W and 0 <= y + dy < H and canal[y + dy][x + dx]]
            if not viz_canal: continue
            # o cipreste fica um tile para fora do cais, a cada 3 tiles (as filas dos canais)
            dx, dy = viz_canal[0]
            ox, oy = x - dx*1.0, y - dy*1.0
            passo = (x if dy else y) % 4
            if passo == 0 and a.livre(int(ox), int(oy)) and not agua(ox, oy) and not na_estrada(ox, oy, 1) and not em_spot(ox + .5, oy + .5, 1) \
                    and livre_de_reserva(ox, oy, 1) and not perto_prop(ox + .5, oy + .5, 1.8) and zona[y][x] in (1, 2, 3, 4):
                a.prop("cipreste" if rng.random() < .7 else "cipreste_2", ox + .5, oy + .5, bloqueia=.4)
    for y in range(H):
        for x in range(W):
            if not canal[y][x] or rng.random() > .05: continue
            a.prop(rng.choice(["lotus", "papiro", "lotus"]), x + .5, y + .5, chao=True)

    # ---- spots estilo MU: anel de grupos em célula livre, fogueira do Tobias na beira do caminho, marco atrás
    spots, descanso = [], [[POSTO[0] + 1.0, POSTO[1] - 1.0]]
    for (sid, nome, niv, mobs, postura, (bx, by), r, marco) in SPOTS:
        spots.append({"id": sid, "nome": nome, "nivel": niv, "pos": [bx, by], "raio": round(r*.8, 1), "respawn_s": 14})
        q = mobs[0][1]; ng = 12 // q
        cidade = math.hypot(bx - CIDADE[0], by - CIDADE[1]) < R_CIDADE + 1
        dv = (C[0] - bx, C[1] - by) if not cidade else (bx - CIDADE[0], by - CIDADE[1])
        dn = math.hypot(*dv) or 1; dv = (dv[0]/dn, dv[1]/dn)
        ang_cam = math.atan2(dv[1], dv[0])
        cands = []
        if cidade:       # nos anéis: os grupos seguem o arco do anel
            rc = math.hypot(bx - CIDADE[0], by - CIDADE[1]); a0 = math.atan2(by - CIDADE[1], bx - CIDADE[0])
            for ia in range(-30, 31):
                ang = a0 + ia/30*(r*2.4/rc)
                for dr in (0, -1.2, 1.2, -2.2, 2.2):
                    cands.append((abs(ia) % 5, CIDADE[0] + math.cos(ang)*(rc + dr), CIDADE[1] + math.sin(ang)*(rc + dr)))
        else:
            for ia in range(36):
                ang = ang_cam + math.pi + (ia - 18)/36*2*math.pi*.86
                for rr in (r*.36, r*.52, r*.66, r*.22, r*.76, r*.88):
                    cands.append((abs(ia - 18) % 7, bx + math.cos(ang)*rr, by + math.sin(ang)*rr))
        cands.sort(key=lambda c: c[0])
        postos = []
        # segunda e terceira passada só se faltar lugar: aproxima um pouco os grupos e os props (spot sempre com 12)
        for (_, x, y, dmin, dprop) in [c + (2.7 if not cidade else 2.4, 1.6) for c in cands] + \
                                       [c + (2.2, 1.2) for c in cands] + [c + (1.9, .9) for c in cands]:
            if len(postos) >= ng: break
            if not livre3(x, y) or perto_prop(x, y, dprop) or not livre_de_reserva(x, y, .5): continue
            if any(math.dist((x, y), p) < dmin for p in postos): continue
            g = len(postos); mob, qtd = mobs[g % len(mobs)]
            s_ = {"mob": mob, "pos": [round(x, 1), round(y, 1)], "raio": 1.2, "qtd": qtd, "nivel": niv[0] + g % (niv[1] - niv[0] + 1),
                  "spot": sid, "postura": postura, "temperamento": postura, "respawn_s": 14, "motivo": MOTIVO[mob]}
            if postura == "agressivo": s_.update({"territorio": 3.5})
            a.spawns.append(s_); postos.append((x, y))
        if len(postos) < ng: print("SPOT INCOMPLETO", sid, len(postos), "de", ng)
        # fogueira + carrinho do Tobias do lado de quem chega (fora do anel de grupos), se não há descanso perto
        fx_, fy_ = bx + dv[0]*r*.95, by + dv[1]*r*.95
        if not any(math.dist((fx_, fy_), d) < 16 for d in descanso):
            for k in range(30):
                qx_, qy_ = fx_ + rng.uniform(-2.5, 2.5), fy_ + rng.uniform(-2.5, 2.5)
                if livre3(qx_, qy_) and livre3(qx_ + 1.8, qy_ + .8) and not na_estrada(qx_, qy_) and not perto_prop(qx_, qy_, 2.2) and livre_de_reserva(qx_, qy_):
                    a.prop("fogueira", round(qx_, 1), round(qy_, 1), bloqueia=.5, luz=FOGO + [6])
                    a.prop("carrinho_tobias", round(qx_ + 1.8, 1), round(qy_ + .8, 1), bloqueia=.5, ponto="descanso"); descanso.append([qx_, qy_]); break
        if marco:
            mx_, my_ = bx - r*.55, by + r*.55
            for k in range(12):
                if livre3(mx_, my_) and not perto_prop(mx_, my_, 2.0) and livre_de_reserva(mx_, my_): a.prop(marco, round(mx_, 1), round(my_, 1), bloqueia=.8); break
                mx_ += rng.uniform(-1.5, 1.5); my_ += rng.uniform(-1.5, 1.5)
        reservado.append((bx, by, r*.8))

    # ---- vegetação e vida da planície (tudo fora dos spots, das estradas e das praças)
    def solto(kinds, n, bloq, dist, zonas=None, spot_ok=False, chao=False, pisos="e", luz=None, perto_de=None):
        f = t_ = 0
        while f < n and t_ < 12000:
            t_ += 1
            if perto_de:
                (qx, qy, qr) = perto_de; ang = rng.uniform(0, 2*math.pi); rr = qr*math.sqrt(rng.random())
                x, y = qx + math.cos(ang)*rr, qy + math.sin(ang)*rr
            else:
                x, y = rng.uniform(4, W - 4), rng.uniform(4, H - 4)
            ix, iy = int(x), int(y)
            if not (0 <= ix < W and 0 <= iy < H) or a.blk[iy][ix] or estrada[iy][ix] or a.ter[iy][ix] not in pisos: continue
            if zonas is not None and zona[iy][ix] not in zonas: continue
            if not spot_ok and em_spot(x, y, 1.5): continue
            if bloq and not livre3(x, y): continue
            if perto_prop(x, y, dist) or not livre_de_reserva(x, y, 1 if not chao else 0): continue
            if math.dist((x, y), SPAWN) < 4 or na_estrada(x, y, 1) and bloq: continue
            a.prop(rng.choice(kinds), round(x, 2), round(y, 2), bloqueia=bloq, chao=chao); f += 1
            if luz and rng.random() < luz[0]: a.luzes.append([round(x, 2), round(y, 2)] + luz[1:])
    # o Olival dos Parados: oliveiras velhas com os atlantes parados entre elas, olhando para cima
    ex_, ey_ = em((84, 110), NORTE, 10.5)
    reservado.append((ex_, ey_, 2.5))
    a.npcs.append({"id": "evemon_parado", "ponto": "rei_parado", "x": round(ex_, 2), "y": round(ey_, 2), "visual": "atlante_parado"})
    a.prop("velas_chao", ex_ + .9, ey_ - .9, chao=True, luz=[1, .7, .35, 1.5])
    solto(["oliveira", "oliveira_2", "oliveira_3", "oliveira"], 70, .9, 3.4, zonas=[3])
    solto(["atlante_parado", "atlante_parado_2"], 26, .4, 2.6, zonas=[3], pisos="el")
    solto(["atlante_parado", "atlante_parado_2"], 14, .4, 6.0, zonas=[1, 2, 4, 5], pisos="elc")
    # campos: cevada em pé nos lotes, feixes e ânforas nas eiras
    solto(["cevada", "cevada_2", "cevada"], 150, 0, 1.7, zonas=[1, 2], pisos="c", spot_ok=True)
    solto(["feixes_cevada", "anforas"], 18, .6, 5.0, zonas=[1, 2], pisos="ec")
    solto(["casa_atlante", "casa_atlante_2"], 7, 1.6, 12.0, zonas=[1, 2, 4], pisos="e")
    # prados: tamareiras, mirtos, juncos em volta da lagoa
    solto(["tamareira", "tamareira_2"], 80, .5, 3.4, zonas=[4])
    solto(["mirto", "papiro", "rochedo_2"], 30, .4, 4.0, zonas=[4])
    solto(["tamareira", "tamareira_2", "papiro"], 18, .4, 2.0, perto_de=(LAGOA[0], LAGOA[1], 10), pisos="e")
    solto(["lotus", "lotus"], 10, 0, 1.5, perto_de=(LAGOA[0], LAGOA[1], 6), pisos="wr", chao=True, spot_ok=True)
    solto(["mirto"], 70, .3, 2.6, zonas=[1, 2, 3, 4, 5, 6])
    solto(["oliveira_2", "oliveira_3"], 26, .9, 6.0, zonas=[1, 2, 4, 6])
    solto(["cipreste", "cipreste_2"], 20, .4, 4.0, zonas=[5, 6, 3])
    solto(["obelisco_hermetico"], 10, .4, 14.0, zonas=[1, 2, 3, 4], luz=[1.0] + ESMERALDA + [2])
    solto(["rochedo_2"], 4, 1.8, 18.0, zonas=[4, 6])
    # estelas e tripés ao longo das estradas, a cada ~11 tiles
    ult = []
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            if estrada[y][x] < 2 or zona[y][x] in (None, 7, 8) or a.ter[y][x] == "r": continue
            if any(math.dist((x, y), u) < 11 for u in ult): continue
            for (dx, dy) in [(-2.2, 2.2), (2.2, -2.2), (2.2, 2.2), (-2.2, -2.2)]:
                qx, qy = x + .5 + dx, y + .5 + dy
                if a.livre(int(qx), int(qy)) and not estrada[int(qy)][int(qx)] and not agua(qx, qy) and not perto_prop(qx, qy, 1.6) and livre_de_reserva(qx, qy):
                    a.prop("tripode", round(qx, 1), round(qy, 1), bloqueia=.3, luz=FOGO + [4]); ult.append((x, y)); break

    # ---- fora dos spots: poucos pares neutros nos caminhos, com espaço para respirar
    for (u, v, mob, niv) in [("posto", "lavoura", "ibis_de_thoth_atl", 30), ("lavoura", "eclusa", "touro_de_poseidon", 32),
                             ("eclusa", "olival", "vigia_de_oricalco", 34), ("cais", "lagoa", "ibis_de_thoth_atl", 35),
                             ("olival", "salao", "cinocefalo", 37), ("lagoa", "palmeiras", "elefante_de_atlas", 37)]:
        (x0, y0), (x1, y1) = LUGARES[u], LUGARES[v]
        ok = False
        for t_ in (.5, .4, .6, .32, .68):
            for (ox, oy) in [(2.5, -2.5), (-2.5, 2.5), (3.5, 0), (0, 3.5), (-3.5, 0)]:
                x, y = x0 + (x1 - x0)*t_ + ox, y0 + (y1 - y0)*t_ + oy
                if livre3(x, y) and not na_estrada(x, y) and not perto_prop(x, y, 1.6) and not em_spot(x, y, 3): ok = True; break
            if ok: break
        if not ok: print("PAR SEM LUGAR", u, v); continue
        a.spawns.append({"mob": mob, "pos": [round(x, 1), round(y, 1)], "raio": 1.0, "qtd": 2, "nivel": niv, "postura": "neutro",
                         "temperamento": "neutro", "respawn_s": 30, "motivo": MOTIVO[mob]})
    # ---- elite: o Touro do Pilar corre o hipódromo
    ex, ey = em(CIDADE, SUL, 31)
    a.spawns.append({"mob": "touro_do_pilar", "pos": [ex, ey], "raio": .5, "qtd": 1, "nivel": 42, "elite": True, "postura": "neutro",
                     "temperamento": "neutro", "respawn_s": 300, "patrulha": [list(em(CIDADE, SUL, 31, LESTE, 6)), [ex, ey], list(em(CIDADE, SUL, 31, OESTE, 6))],
                     "motivo": MOTIVO["touro_do_pilar"]})
    # ---- guarda da ponte da ilha (a Serpente não deixa ninguém passar)
    for (x, y) in [(CIDADE[0] + 3.2, CIDADE[1] + 16.0), (CIDADE[0] - 16.0, CIDADE[1] - 3.2)]:
        a.spawns.append({"mob": "filho_da_serpente", "pos": [round(x, 1), round(y, 1)], "raio": 1.0, "qtd": 2, "nivel": 44, "postura": "agressivo",
                         "temperamento": "agressivo", "territorio": 3.0, "respawn_s": 30, "motivo": MOTIVO["filho_da_serpente"]})
    # ---- baús
    for (x, y, b, vis, idm) in [(SALAO[0] - 2.5, SALAO[1] + 5.0, "bau_de_ferro", "bau_raro", "atl_registros"),
                                (LAGOA[0] - 3.0, LAGOA[1] - 8.0, "caixote_podre", "bau_comum", "atl_lagoa"),
                                (CERCO[0] - 3.0, CERCO[1] + 7.5, "bau_de_ferro", "bau_raro", "atl_cerco"),
                                (130.5, 92.0, "caixote_podre", "bau_comum", "atl_eira"),
                                (TEMPLO[0] + 3.0, TEMPLO[1] - 8.5, "bau_de_ferro", "bau_raro", "atl_templo")]:
        if not (a.livre(int(x), int(y)) and not agua(x, y)):
            print("BAU SEM LUGAR", idm); continue
        a.objetos.append({"kind": "bau", "pos": [round(x, 1), round(y, 1)], "bau": b, "visual": vis, "id_mapa": idm})

    # ---- passada final: todo grupo em célula livre (3x3) e longe de prop que bloqueia; senão desloca até 3 tiles
    for sp in a.spawns:
        x, y = sp["pos"]
        if livre3(x, y) and not perto_prop(x, y, 1.3): continue
        melhor = None
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                qx, qy = x + dx, y + dy
                if livre3(qx, qy) and not perto_prop(qx, qy, 1.3) and (melhor is None or math.hypot(dx, dy) < melhor[0]): melhor = (math.hypot(dx, dy), qx, qy)
        if melhor: sp["pos"] = [round(melhor[1], 1), round(melhor[2], 1)]
        else: print("SPAWN SEM LUGAR (removido)", sp["mob"], sp["pos"]); sp["_fora"] = True
    a.spawns[:] = [sp for sp in a.spawns if not sp.get("_fora")]

    chefe_ = {"id": "gadiro", "pos": [round(PILAR[0] + 1.5, 1), round(PILAR[1] - 1.5, 1)], "arena": {"centro": list(PILAR), "raio": 5.0},
              "porta": porta_da_arena(a, PILAR[0], PILAR[1], 5.0)}
    m = a.exportar(chefe=chefe_, spawn=list(SPAWN), ceu={"escuro": 0.42, "cor": [0.95, 0.8, 0.58], "neblina": [0.1, 0.13, 0.09]})
    m["pisos"] = dict(PISOS)
    m["exterior"] = True
    # água limpa dos canais (o shader do chão usa estas cores no lugar das do Rio Amargo quando o mapa traz `agua`)
    m["agua"] = {"fundo": [0.02, 0.08, 0.1], "raso": [0.08, 0.24, 0.24], "reflexo": [0.62, 0.55, 0.38], "brilho": [1.0, 0.85, 0.55],
                 "lume": [0.0, 0.04, 0.03], "espuma": [0.7, 0.7, 0.62]}
    centro = []
    for cxx in CANAIS_X: centro += [[cxx + 1.0, 16.0], [cxx + 1.0, 144.0], [cxx + 1.0, 16.0]]
    for cyy in CANAIS_Y: centro += [[16.0, cyy + 1.0], [144.0, cyy + 1.0], [16.0, cyy + 1.0]]
    m["rio"] = {"id": "canais_retos", "nome": "Os Canais Retos", "nota": "Crítias 118c-e: a planície cortada por canais retos",
                "centro": centro, "nascente": list(C)}
    letras = "ABCDEFGHIJ"
    m["zona_grade"] = ["".join("." if zona[y][x] is None else letras[zona[y][x]] for x in range(W)) for y in range(H)]
    m["zonas"] = [{"id": i, "nome": n, "seguro": s, "nivel": nv, "musica": "musica/sao_lazaro", "ambiente": "ambiente/noite_vento",
                   "faccao": None, "neblina": .18 if i != "cerco_da_coluna" else .26} for (i, n, s, nv) in ZONAS]
    m["spots"] = spots
    m["descanso"] = [[round(d[0], 1), round(d[1], 1)] for d in descanso]
    m["salas"] = [{"nome": sp[1], "ret": [sp[5][0] - 3, sp[5][1] - 2, sp[5][0] + 3, sp[5][1] + 2]} for sp in SPOTS] + \
                 [{"nome": "Posto da Fenda", "ret": [POSTO[0] - 3, POSTO[1] - 2, POSTO[0] + 3, POSTO[1] + 2]},
                  {"nome": "Templo de Poseidon", "ret": [TEMPLO[0] - 3, TEMPLO[1] - 2, TEMPLO[0] + 3, TEMPLO[1] + 2]}]
    m["lugares"] = [{"id": "a_fenda", "nome": "A Fenda", "pos": list(FENDA)}, {"id": "posto_da_fenda", "nome": "Posto da Fenda", "pos": list(POSTO)},
                    {"id": "tabua_de_esmeralda", "nome": "A Tábua de Esmeralda", "pos": list(SALAO)},
                    {"id": "portao_de_amenti", "nome": "Portão de Amenti", "pos": list(AMENTI)},
                    {"id": "templo_de_poseidon", "nome": "Templo de Poseidon e Clito", "pos": list(TEMPLO)},
                    {"id": "pilar_das_leis", "nome": "Pilar das Leis", "pos": list(PILAR)},
                    {"id": "colosso_de_atlas", "nome": "Colosso de Atlas", "pos": [PORTA_Y[0] + 6.5, PORTA_Y[1] + 4.5]}] + \
                   [{"id": f"coluna_{cid}", "nome": nome, "pos": list(p)} for (cid, nome, p, _) in COLUNAS]
    json.dump(m, open(f"{AQUI}/atlantida.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print("atlantida", W, "x", H, "props", len(m["props"]), "spawns", len(m["spawns"]), "objetos", len(m["objetos"]), "pontes", len(pontes))
    return m


def ligacao_eden():
    """Onde a Fenda abre do lado do Novo Éden: tile livre (5x5) no Coração do Éden, longe dos grupos (o mapa é da outra thread)."""
    p = os.path.join(AQUI, "..", "mata_do_granizo", "mata_do_granizo.json")
    try: e = json.load(open(p))
    except OSError: return [52.0, 9.0]
    for o in e["objetos"]:   # a Fenda já está no Novo Éden (eden_mapa.py, FENDA_ATLANTIDA): usa a posição de lá
        if o.get("para") == "atlantida": return list(o["pos"])
    return [83.5, 34.5]   # FENDA_ATLANTIDA em eden_mapa.py (0.9.4)
    g = e["grade"]; spw = [s["pos"] for s in e["spawns"]]
    melhor = None
    for y in range(3, e["h"] - 3):
        for x in range(3, e["w"] - 3):
            if not all(g[y + dy][x + dx] == "." for dx in range(-2, 3) for dy in range(-2, 3)): continue
            if any(math.dist((x, y), s) < 7 for s in spw) or any(math.dist((x, y), (p_["x"], p_["y"])) < 2.5 for p_ in e["props"] if not p_.get("chao")): continue
            d = math.dist((x, y), (52, 12))
            if melhor is None or d < melhor[0]: melhor = (d, x + .5, y + .5)
    return [melhor[1], melhor[2]] if melhor else [52.0, 9.0]


def dados(eden):
    mobs, spr = {}, {}
    for k, v in MOBS.items():
        d = {x: v[x] for x in ("nome", "base", "niveis", "ajuste", "tags", "drop")}
        if "res" in v: d["res"] = v["res"]
        d["renascimento_s"] = 14
        if k == "touro_do_pilar": d.update({"arquetipo": "elite", "renascimento_s": 300})
        mobs[k] = d
        spr[k] = {"usa": v["usa"], "escala": v["escala"], **({"tint": v["tint"]} if v["tint"] else {})}
    spr.update(SPR_CHEFES)
    out = {
        "_doc": "Atlântida (pedido do Jefin 15/10/2026). mobs: formato de game/data/v06_extra.json (base = id de design/combate/mobs.json). "
                "sprites: formato de game/data/sprites_substitutos.json (sem tint = folha própria em assets/monstros/<id>). chefes: formato de "
                "design/combate/chefes.json. drops: formato de design/combate/drops.json (faixa2 até existir faixa3). Gerado por gerar.py.",
        "mobs": mobs, "sprites": spr, "chefes": CHEFES, "drops": DROPS,
        "ligacao_novo_eden": {"_doc": "Objeto a acrescentar em mata_do_granizo.json (Coração do Éden): a Fenda vista do lado de fora. "
                                      "A posição foi escolhida num 5x5 livre longe dos grupos; o prop 'fenda' (4x3) fica 2 tiles atrás.",
                              "objeto": {"kind": "portal", "pos": eden, "para": "atlantida", "chegada": list(SPAWN),
                                         "nome": "A Fenda · Atlântida (nv 30-45)", "visual": "portal_dungeon_lume", "requer_nivel": 30},
                              "props": [{"k": "fenda", "x": round(eden[0] - 1.5, 1), "y": round(eden[1] + 1.5, 1), "decor_moldura": True}],
                              "luzes": [[round(eden[0] - 1.5, 1), round(eden[1] + 1.5, 1)] + ESMERALDA + [9]]},
        "nomes_mapa_hud": {"atlantida": "Atlântida (nv 30-45)"},
    }
    json.dump(out, open(f"{AQUI}/dados.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    m = atlantida()
    eden = ligacao_eden()
    for o in m["objetos"]:
        if o["kind"] == "portal" and o["para"] == "mata_do_granizo": o["chegada"] = [eden[0], eden[1] + 2.0]
    json.dump(m, open(f"{AQUI}/atlantida.json", "w"), ensure_ascii=False, separators=(",", ":"))
    dados(eden)
    planta(m, f"{AQUI}/planta_atlantida.png", "Atlântida · a Planície Sob a Redoma · nível 30 a 45")
    g = m["grade"]
    livre = lambda p: g[int(p[1])][int(p[0])] == "."
    ruins = [("spawn", m["spawn"])] if not livre(m["spawn"]) else []
    ruins += [(o["nome"], o["pos"]) for o in m["objetos"] if o["kind"] == "portal" and not livre(o["pos"])]
    ruins += [(s["mob"], s["pos"]) for s in m["spawns"] if not livre(s["pos"])]
    print("atlantida", "OK" if not ruins else f"FORA DO CHÃO: {ruins}")
