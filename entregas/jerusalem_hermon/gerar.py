"""Jerusalém e Monte Hermon · área inicial dos Arautos do Juízo (pedido do Jefin, 16/10/2026).

"Base em Jerusalém, a cidade santa onde começou o apocalipse; área inicial no Monte Hermon. Diferente do mapa da
Vigília, mas com números equivalentes (XP, farm, spots, níveis e uma dungeon equivalente), para nenhuma facção ser
favorecida."

Gera no MESMO formato de game/data/mapas/*.json (classe Andar de design/mapas/cripta/gerar.py, como o Novo Éden):
  jerusalem_hermon.json                      o mapa aberto (160x160, nível 1 a 12), base dos Arautos
  minas_dos_gigantes.json                    Fosso dos Vigilantes, andar 1 (espelho do Porão do Matadouro)
  salao_das_noivas.json                      andar 2 (espelho do Ossário das Carpideiras)
  altar_do_juramento.json                    andar 3 (espelho da Câmara da Trombeta)
  dados.json                                 mobs (formato v06_extra), sprites (recolor), chefes, drops, nomes no HUD
  planta_*.png                               plantas de cima para conferir
  espelho.txt                                tabela Vigília x Arautos (spots, mobs, distâncias, dungeon)

REGRA DO ESPELHO: cada spot, grupo fora de spot, andar e chefe daqui copia um do deserto: mesmo nível, mesma
quantidade, mesmo temperamento, mesmo renascimento, e o mob usa como `base` o mesmo mob do deserto, sem `ajuste`
(mesmo HP, dano, XP e ouro). Muda o nome, a cor, o lugar e a história.
Uso: python3 gerar.py
"""
import json, math, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(RAIZ, "design", "mapas", "cripta"))
import gerar as G          # noqa: E402  (Andar, porta_da_arena, planta)
G.AQUI = AQUI
Andar, porta_da_arena = G.Andar, G.porta_da_arena

FOGO = [1, 0.45, 0.15]; BRASA = [1, 0.36, 0.1]; VELA = [1, 0.75, 0.4]; SANTO = [1, 0.9, 0.6]; FRIO = [0.6, 0.66, 0.82]
PISOS = {"a": "areia", "c": "calcamento", "e": "musgo", "f": "mata_morta", "g": "cemiterio", "k": "cascalho",
         "l": "laje_capela", "j": "laje_trombeta", "m": "chapa_matadouro", "n": "entulho", "p": "brejo", "q": "vidro",
         "r": "agua_toxica", "w": "lama", "s": "leito_rachado", "t": "terra", "z": "cinza", "y": "areia_vitrificada",
         "b": "barranca", "v": "vala", "i": "asfalto_rachado", "x": "cripta", "o": "ossario", "d": "duna"}
G.COR_PISO.update({"l": (150, 138, 116), "c": (112, 100, 84), "n": (96, 86, 72), "t": (92, 74, 56), "s": (104, 90, 70),
                   "f": (70, 60, 48), "g": (80, 76, 66), "z": (128, 126, 122), "k": (88, 84, 78), "p": (58, 56, 44),
                   "e": (60, 72, 60), "r": (70, 92, 104), "w": (40, 56, 66), "q": (170, 176, 184), "b": (98, 88, 70),
                   "m": (84, 58, 46)})


def ruido(x, y, s=0.0):
    return .5*math.sin(x*.37 + y*.21 + s) + .3*math.sin(x*.13 - y*.29 + 1.7 + s) + .2*math.sin(x*.71 + y*.53 + 2.9*s)


def dist_seg(px, py, a, b):
    ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax)*dx + (py - ay)*dy)/(dx*dx + dy*dy)))
    return math.hypot(px - ax - t*dx, py - ay - t*dy)


def dist_poli(px, py, pts):
    return min(dist_seg(px, py, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


# ===================================================================================== mobs (variantes estilo MU)
# espelho = id do mob do deserto: vira `base` (o jogo herda tudo dele, sem ajuste) e a folha recolorida até a arte própria.
MOBS = {
    # ---- mundo aberto (espelhos dos mobs do deserto)
    "peregrino_ressecado":   dict(nome="Peregrino Ressecado", espelho="carnical", tint="#b8ae9c", escala=1.0, tags=["morto_vivo"],
                                  motivo="vieram ver o fim do mundo e o fim não terminou; ainda cavam o Getsêmani atrás de relíquias"),
    "abutre_do_hermon":      dict(nome="Abutre do Hermon", espelho="corvo_de_cinza", tint="#cfc6b8", escala=1.25, tags=["animal", "voador"],
                                  motivo="descem do Hermon atrás dos peregrinos caídos; esperam a vez em cima das oliveiras mortas"),
    "chacal_de_josafa":      dict(nome="Chacal de Josafá", espelho="cao_de_vala", tint="#b08a5a", escala=1.05, tags=["animal"],
                                  motivo="a matilha mora no leito seco do Cedrom e defende a toca de quem desce ao vale"),
    "levantado_das_oliveiras": dict(nome="Levantado das Oliveiras", espelho="nao_julgado", tint="#c8c0b0", escala=1.0, tags=["morto_vivo"],
                                  motivo="os mortos do Monte das Oliveiras levantaram primeiro, como manda a tradição, e esperam na fila um Juízo que travou"),
    "porco_de_gadara":       dict(nome="Porco de Gadara", espelho="porco_pestilento", tint="#a0524a", escala=1.05, tags=["animal", "demonio"],
                                  motivo="a vara onde a Legião guarda os espíritos que sobram; ninguém lembra de mandar a vara para o mar"),
    "sineiro_infiltrado":    dict(nome="Sineiro Infiltrado", espelho="sangrador_apostata", tint="#6f86a8", escala=1.0, tags=["humano"],
                                  motivo="Sineiros da Vigília escondidos nos cedros: tocam sinos rachados para abafar o Coro e defendem o esconderijo"),
    "sapador_herege":        dict(nome="Sapador Herege", espelho="desertor_legiao", tint="#7a8a96", escala=1.0, tags=["humano"],
                                  motivo="Engenheiros Hereges represando as fontes do Jordão para mandar a água para o deserto; defendem o canteiro"),
    "vigilante_acorrentado": dict(nome="Vigilante Acorrentado", espelho="sombra_gravada", tint="#d8d4e8", escala=1.1, tags=["espectro", "celestial"],
                                  motivo="pedaços dos duzentos que desceram no Hermon; as correntes afrouxaram no Juízo e eles guardam as pegadas do juramento"),
    "fornalheiro_de_tofete": dict(nome="Fornalheiro de Tofete", espelho="acougueiro_oco", tint="#c0583a", escala=1.0, tags=["demonio"],
                                  motivo="demônios ocos que alimentam as fornalhas da Geena; atacam quem entra no pátio"),
    "capataz_de_tofete":     dict(nome="Capataz de Tofete", espelho="capataz_gancho", tint="#e06a3a", escala=1.1, tags=["demonio"],
                                  motivo="manda nas fornalhas desde que o general sumiu; guarda a chave da Porta de Pã"),
    "filho_do_hissopo":      dict(nome="Filho do Hissopo", espelho="filho_de_cardo", tint="#8a9a70", escala=1.0, tags=["planta"],
                                  motivo="o hissopo bebeu um morto e levantou com ele; só aparece para quem segue a receita da Zilpa"),
    # ---- Fosso dos Vigilantes (espelhos dos mobs da Cripta)
    "verme_do_fosso":        dict(nome="Verme do Fosso", espelho="larva_de_carne", tint="#b89a7a", escala=1.0, tags=["animal"],
                                  motivo="comem o que os gigantes deixam nas minas"),
    "escravo_dos_gigantes":  dict(nome="Escravo dos Gigantes", espelho="gancheiro", tint="#8c7c6a", escala=1.0, tags=["humano", "morto_vivo"],
                                  motivo="os homens que os Nefilins puseram para cavar; morreram de pé e continuam cavando"),
    "nefilim_mirrado":       dict(nome="Nefilim Mirrado", espelho="acougueiro_oco", tint="#a89070", escala=1.15, tags=["gigante"],
                                  motivo="filhos pequenos dos Vigilantes, grandes demais para gente e pequenos demais para o dilúvio levar"),
    "soldado_de_pedra":      dict(nome="Soldado de Pedra", espelho="soldado_caido", tint="#9a9890", escala=1.0, tags=["morto_vivo"],
                                  motivo="os gigantes comem os mortos; estes viraram pedra antes"),
    "noiva_afogada":         dict(nome="Noiva Afogada", espelho="carpideira_de_ossos", tint="#8aa0a8", escala=1.0, tags=["morto_vivo", "espectro"],
                                  motivo="as filhas dos homens que casaram com os Vigilantes; choram os filhos que o dilúvio levou"),
    "brasa_de_azazel":       dict(nome="Brasa de Azazel", espelho="fogo_de_vela", tint="#ff8a3a", escala=1.0, tags=["espectro"],
                                  motivo="o fogo que Azazel ensinou aos homens a fazer; ainda procura uma forja"),
    "escriba_emparedado":    dict(nome="Escriba Emparedado", espelho="monge_emparedado", tint="#b0a890", escala=1.0, tags=["humano", "morto_vivo"],
                                  motivo="copiavam os ensinamentos proibidos; foram emparedados com eles"),
    "kokabiel_contador":     dict(nome="Kokabiel, o Contador de Estrelas", espelho="ultimo_operador", tint="#c8c0ff", escala=1.15, tags=["celestial"],
                                  motivo="o Vigilante que ensinou os homens a ler as estrelas; guarda a laje do juramento e conta as noites que faltam"),
    "eco_do_juramento":      dict(nome="Eco do Juramento", espelho="eco_da_trombeta", tint="#e0d0ff", escala=1.0, tags=["celestial", "espectro"],
                                  motivo="a voz dos duzentos jurando, que ainda anda pelo salão"),
    "vigilante_desfeito":    dict(nome="Vigilante Desfeito", espelho="querubim_desfeito", tint="#c8b8e8", escala=1.05, tags=["celestial"],
                                  motivo="o que sobrou dos Vigilantes que o Juízo soltou pela metade"),
}
DROP_MOB = {"kokabiel_contador": "elite_inicial", "peregrino_ressecado": "inicial_humanoide", "abutre_do_hermon": "inicial_animal", "chacal_de_josafa": "inicial_animal",
            "levantado_das_oliveiras": "inicial_humanoide", "porco_de_gadara": "inicial_animal", "filho_do_hissopo": "raro_missao_cardo",
            "verme_do_fosso": "cripta_carne", "escravo_dos_gigantes": "cripta_humanoide", "nefilim_mirrado": "cripta_carne",
            "soldado_de_pedra": "cripta_humanoide", "noiva_afogada": "cripta_monge", "brasa_de_azazel": "cripta_espectro",
            "escriba_emparedado": "cripta_monge", "eco_do_juramento": "cripta_celestial", "vigilante_desfeito": "cripta_celestial"}

ZONAS = [  # id, nome, seguro, nível, piso, neblina, música, ambiente
    ("jerusalem", "Jerusalém, a Cidade Santa", True, None, "l", .12, "musica/capela", "ambiente/capela_coro"),
    ("cidade_de_davi", "Cidade de Davi", False, [1, 3], "n", .3, "musica/sao_lazaro", "ambiente/noite_vento"),
    ("monte_oliveiras", "Monte das Oliveiras", False, [1, 3], "t", .3, "musica/sao_lazaro", "ambiente/noite_vento"),
    ("vale_josafa", "Vale de Josafá", False, [2, 4], "s", .38, "musica/sao_lazaro", "ambiente/noite_vento"),
    ("bosque_hissopo", "Bosque do Hissopo", False, [2, 4], "f", .32, "musica/sao_lazaro", "ambiente/noite_vento"),
    ("necropole_oliveiras", "Necrópole das Oliveiras", False, [3, 5], "g", .42, "musica/sao_lazaro", "ambiente/cemiterio"),
    ("encosta_cedros", "Encosta dos Cedros", False, [4, 5], "f", .4, "musica/sao_lazaro", "ambiente/noite_vento"),
    ("vale_hinom", "Vale do Hinom (Geena)", False, [4, 7], "z", .45, "musica/sao_lazaro", "ambiente/abatedouro"),
    ("pocilgas_gadara", "Pocilgas de Gadara", False, [4, 6], "p", .4, "musica/sao_lazaro", "ambiente/noite_vento"),
    ("fontes_jordao", "Fontes do Jordão", False, [6, 8], "k", .35, "musica/sao_lazaro", "ambiente/rio"),
    ("cume_hermon", "Cume do Hermon", False, [9, 12], "z", .9, None, "ambiente/noite_vento"),
]
ZI = {z[0]: i for i, z in enumerate(ZONAS)}
LETRAS = "ABCDEFGHIJK"
ESPELHO_DE = {}   # mob do deserto -> mob do mundo daqui (o primeiro da lista; os da dungeon vêm depois e não entram)
for _k, _d in MOBS.items():
    if _k not in ("filho_do_hissopo", "kokabiel_contador"): ESPELHO_DE.setdefault(_d["espelho"], _k)
DESERTO_GAME = json.load(open(os.path.join(RAIZ, "game", "data", "mapas", "area_inicial.json")))

# ---- blobs: chave -> (x, y, raio, zona, spot | None). spot = (id, nome, nível, [(mob, qtd por grupo, nº de grupos)], temperamento por mob, espelho)
B = {
    "J":     (101, 46, 13, "jerusalem", None),
    "DAVI":  (122, 28, 9, "cidade_de_davi", None),
    "SILOE": (134, 24, 8, "cidade_de_davi", ("escadas_de_siloe", "Escadas de Siloé", [3, 5],
              [("chacal_de_josafa", 3, 2, "territorial"), ("abutre_do_hermon", 3, 2, "neutro")], "telhados_dos_corvos")),
    "GETS":  (120, 70, 10, "monte_oliveiras", ("getsemani", "Oliveiras do Getsêmani", [1, 3],
              [("peregrino_ressecado", 3, 2, "neutro"), ("abutre_do_hermon", 3, 1, "neutro")], "covas_rasas")),
    "FENDA": (104, 84, 9, "monte_oliveiras", ("fenda_das_oliveiras", "A Fenda das Oliveiras", [7, 9],
              [("sapador_herege", 3, 2, "territorial"), ("peregrino_ressecado", 3, 2, "neutro")], "marco_do_corte")),
    "JOS":   (134, 84, 10, "vale_josafa", ("covil_dos_chacais", "Covil dos Chacais", [3, 5],
              [("chacal_de_josafa", 3, 3, "territorial"), ("peregrino_ressecado", 3, 1, "neutro")], "fosso_dos_caes")),
    "JOS2":  (138, 102, 7, "vale_josafa", None),
    "HIS":   (86, 72, 8, "bosque_hissopo", None),
    "PRIM":  (100, 118, 10, "necropole_oliveiras", ("primeiros_a_levantar", "Os Primeiros a Levantar", [4, 6],
              [("levantado_das_oliveiras", 3, 4, "neutro")], "procissao_parada")),
    "NEC2":  (118, 104, 8, "necropole_oliveiras", None),
    "CED":   (44, 114, 9, "encosta_cedros", ("cedros_partidos", "Cedros Partidos", [5, 7],
              [("levantado_das_oliveiras", 2, 4, "neutro"), ("sineiro_infiltrado", 2, 2, "territorial")], "margem_das_viuvas")),
    "CED2":  (60, 96, 8, "encosta_cedros", None),
    "CED3":  (50, 76, 6, "encosta_cedros", None),
    "HIN":   (70, 32, 9, "vale_hinom", None),
    "TOF":   (32, 30, 10, "vale_hinom", ("fornalhas_de_tofete", "Fornalhas de Tofete", [7, 9],
              [("fornalheiro_de_tofete", 3, 3, "agressivo"), ("fornalheiro_de_tofete", 2, 1, "agressivo"), ("capataz_de_tofete", 1, 1, "agressivo")], "patio_do_abatedouro")),
    "POC":   (26, 68, 9, "pocilgas_gadara", ("pocilga_de_gadara", "Pocilga de Gadara", [4, 6],
              [("porco_de_gadara", 3, 4, "neutro")], "chiqueiro_do_carnica")),
    "POC2":  (44, 52, 7, "pocilgas_gadara", None),
    "SAP":   (76, 96, 9, "fontes_jordao", ("acampamento_sapadores", "Canteiro dos Sapadores", [6, 9],
              [("sapador_herege", 2, 4, "territorial"), ("chacal_de_josafa", 2, 2, "neutro")], "acampamento_desertores")),
    "FON2":  (88, 110, 8, "fontes_jordao", None),
    "NEVE":  (42, 136, 10, "cume_hermon", ("neve_de_cinza", "Neve de Cinza", [9, 12],
              [("levantado_das_oliveiras", 3, 2, "neutro"), ("vigilante_acorrentado", 3, 2, "territorial")], "beira_da_tempestade")),
    "CUM2":  (62, 126, 8, "cume_hermon", None),
    "JAEL":  (26, 122, 6, "cume_hermon", None),
}
ARESTAS = [("J", "DAVI"), ("DAVI", "SILOE"), ("J", "GETS"), ("GETS", "JOS"), ("GETS", "FENDA"), ("J", "HIS"), ("HIS", "FENDA"),
           ("JOS", "JOS2"), ("JOS2", "NEC2"), ("NEC2", "PRIM"), ("FENDA", "NEC2"), ("PRIM", "FON2"), ("HIS", "SAP"), ("SAP", "FON2"),
           ("SAP", "CED2"), ("J", "HIN"), ("HIN", "TOF"), ("HIN", "POC2"), ("TOF", "POC"), ("POC2", "POC"), ("POC2", "CED3"),
           ("CED3", "CED2"), ("CED3", "HIS"), ("CED2", "CED"), ("CED", "JAEL"), ("JAEL", "NEVE"), ("CED", "NEVE"), ("FON2", "CUM2"),
           ("CUM2", "NEVE"), ("CED2", "CUM2")]
ESTRADA = ["J", "HIS", "SAP", "FON2", "CUM2", "NEVE"]          # Estrada dos Peregrinos (calçamento), da Porta de Damasco ao cume

# ---- cidade murada (Jerusalém): retângulo alinhado aos eixos; portas = vãos de 3 tiles
CID = (90, 36, 112, 56)               # x0, y0, x1, y1 (piso por dentro)
PORTAS = {"dourada": ("y1", 103), "damasco": ("x0", 47), "esterco": ("y0", 99), "fonte": ("x1", 41)}
SPAWN = [101.5, 42.5]
PORTA_HADES = [92.5, 114.5]           # Portões do Hades (Banias): entrada do Fosso dos Vigilantes
CHEGADA_HADES = [92.5, 111.5]
FENDA = [(129, 76), (124, 80), (118, 82), (112, 86), (108, 92), (106, 99)]   # o Monte partido ao meio (Zc 14:4)
RIACHO = [(30, 146), (40, 132), (52, 122), (66, 116), (80, 112), (90, 108), (104, 108), (118, 112), (134, 112), (148, 108)]


def mapa():
    a = Andar("jerusalem_hermon", "Jerusalém e Monte Hermon", 160, 160, "t", None, {})
    W, H = a.w, a.h
    zona_de = [[None]*W for _ in range(H)]
    trilha = [[False]*W for _ in range(H)]
    estrada = [[False]*W for _ in range(H)]
    blobs = list(B.items())
    segs = [(B[i][:2], B[j][:2], (i in ESTRADA and j in ESTRADA and abs(ESTRADA.index(i) - ESTRADA.index(j)) == 1)) for i, j in ARESTAS]
    x0c, y0c, x1c, y1c = CID
    # ---- chão aberto: blobs + caminhos
    for y in range(3, H - 3):
        for x in range(3, W - 3):
            px, py = x + .5, y + .5
            best, bz = 1e9, None
            for k, (bx, by, r, z, sp) in blobs:
                d = math.hypot(px - bx, py - by)/(r*(1 + .16*ruido(x, y, bx)))
                if d < best: best, bz = d, z
            dc, de = 99, 99
            for p0, p1, e in segs:
                d = dist_seg(px, py, p0, p1); dc = min(dc, d)
                if e: de = min(de, d)
            na_cidade = x0c - 1 <= x <= x1c + 1 and y0c - 1 <= y <= y1c + 1
            if best < 1 or dc < 2.6 + .9*ruido(x, y, 3.1) or na_cidade:
                a.blk[y][x] = False
                zona_de[y][x] = bz if not (x0c <= x <= x1c and y0c <= y <= y1c) else "jerusalem"
                a.ter[y][x] = ZONAS[ZI[zona_de[y][x]]][4]
                if de < 1.25 and best > .4: a.ter[y][x] = "c"; trilha[y][x] = estrada[y][x] = True
                elif dc < 1.0 and best > .55: a.ter[y][x] = "t" if zona_de[y][x] not in ("cume_hermon",) else "k"; trilha[y][x] = True
    # ---- variação de piso por zona (um chão por área, manchas do mesmo vocabulário)
    for y in range(H):
        for x in range(W):
            if a.blk[y][x] or trilha[y][x]: continue
            z = zona_de[y][x]; n1 = ruido(x*1.6, y*1.6, 2); n2 = ruido(x*2.3, y*2.3, 7)
            if z == "jerusalem":
                if (x - x0c) % 7 in (3,) or (y - y0c) % 7 in (3,): a.ter[y][x] = "c"            # ruas da cidade velha
            elif z == "cidade_de_davi" and n1 > .35: a.ter[y][x] = "c"
            elif z == "monte_oliveiras" and n1 > .42: a.ter[y][x] = "z"                        # cinza da primeira trombeta
            elif z == "vale_josafa" and n2 > .45: a.ter[y][x] = "g"
            elif z == "bosque_hissopo" and n1 > .45: a.ter[y][x] = "t"
            elif z == "necropole_oliveiras" and n1 > .5: a.ter[y][x] = "t"
            elif z == "encosta_cedros" and n2 > .3: a.ter[y][x] = "k"
            elif z == "vale_hinom" and n1 > .3: a.ter[y][x] = "m" if n2 > .2 else "k"
            elif z == "pocilgas_gadara" and n1 > .25: a.ter[y][x] = "w"
            elif z == "fontes_jordao" and n2 > .38: a.ter[y][x] = "z"
            elif z == "cume_hermon" and n1 > .5: a.ter[y][x] = "q"                             # cinza vitrificada (gelo sujo)
    # ---- o Monte partido (Zc 14:4): fenda de abismo cortando o Monte das Oliveiras; caminhos atravessam por pontes
    fenda_pontes = []
    for y in range(H):
        for x in range(W):
            if a.blk[y][x]: continue
            d = dist_poli(x + .5, y + .5, FENDA)
            if d < .9 + .35*ruido(x*1.3, y*1.3, 4):
                if trilha[y][x]: fenda_pontes.append((x, y)); continue
                a.blk[y][x] = True; a.ter[y][x] = " "
            elif d < 2.0 and a.ter[y][x] not in "c": a.ter[y][x] = "z"
    # ---- as fontes do Jordão: o riacho de degelo que desce do Hermon, cinzento e frio
    fundo, raso = set(), set()
    rio_d = [[99.0]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if a.blk[y][x]: continue
            px, py = x + .5, y + .5
            d = dist_poli(px, py, RIACHO); rio_d[y][x] = d
            larg = 1.2 + 1.6*max(0, min(1, (px - 40)/60))                 # nasce fino no cume, engrossa nas fontes
            r_ = ruido(px*1.4, py*1.4, 9)*.4
            if d < larg/2 + r_:
                if trilha[y][x] or any(trilha[yy][xx] for xx in range(max(0, x - 1), min(W, x + 2)) for yy in range(max(0, y - 1), min(H, y + 2))):
                    raso.add((x, y))
                elif d < larg/2 - .9: fundo.add((x, y))
                else: raso.add((x, y))
            elif d < larg/2 + 1.3 and not trilha[y][x] and a.ter[y][x] not in "c": a.ter[y][x] = "b"
    for (x, y) in raso: a.ter[y][x] = "r"
    for (x, y) in fundo: a.ter[y][x] = "w"; a.blk[y][x] = True
    # a água rasa também bloqueia, menos nos vaus das trilhas (sem atalho por dentro do riacho)
    for (x, y) in raso:
        if not trilha[y][x]: a.extra_blk.add((x, y))

    rng = a.rng
    spots, descanso, lugares, pendentes = [], [], [], []
    area_spot = [(bx, by, r*.82) for k, (bx, by, r, z, sp) in blobs if sp]
    def em_spot(x, y, folga=0): return any(math.hypot(x - sx, y - sy) < sr + folga for sx, sy, sr in area_spot)
    def agua(x, y): return 0 <= x < W and 0 <= y < H and a.ter[y][x] in "rw"
    def livre3(x, y): return all(a.livre(x + dx, y + dy) and not agua(x + dx, y + dy) and (x + dx, y + dy) not in a.extra_blk
                                 for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    def perto_prop(x, y, d): return any(math.dist((x, y), (p["x"], p["y"])) < d for p in a.props if not p.get("chao"))
    def predio(k, x, y, fp, luz=None, **kw):
        """Prédio com pegada (fp em tiles, centrada na posição, como o add() do deserto)."""
        a.prop(k, x, y, luz=luz, **kw)
        for yy in range(int(y - fp[1]/2 + .5), int(y - fp[1]/2 + .5) + fp[1]):
            for xx in range(int(x - fp[0]/2 + .5), int(x - fp[0]/2 + .5) + fp[0]): a.extra_blk.add((xx, yy))

    # ================================================================ Jerusalém (base dos Arautos, zona segura)
    # muralha: alta atrás (topo da tela), meia-muralha na frente; pilares nos cantos; vãos nas quatro portas
    def porta_em(lado, i):
        if lado not in [l for l, c in PORTAS.values()]: return False
        return any(l == lado and abs(i - c) <= 1 for l, c in PORTAS.values())
    for y in range(y0c, y1c + 1):
        if not porta_em("x0", y): a.prop("parede_gotica_b" if (y % 3) else "parede_gotica_v2_b", x0c - .5, y + .5); a.extra_blk.add((x0c - 1, y))
        if not porta_em("x1", y): a.prop("parede_gotica_frente_b", x1c + 1.5, y + .5); a.extra_blk.add((x1c + 1, y))
    for x in range(x0c, x1c + 1):
        if not porta_em("y1", x): a.prop("parede_gotica_a" if (x % 3) else "parede_gotica_v2_a", x + .5, y1c + 1.5); a.extra_blk.add((x, y1c + 1))
        if not porta_em("y0", x): a.prop("parede_gotica_frente_a", x + .5, y0c - .5); a.extra_blk.add((x, y0c - 1))
    a.prop("parede_gotica_canto", x0c - .5, y1c + 1.5); a.extra_blk.add((x0c - 1, y1c + 1))
    for (cx_, cy_) in [(x1c + 1, y1c + 1), (x0c - 1, y0c - 1), (x1c + 1, y0c - 1)]:
        a.prop("parede_gotica_frente_canto", cx_ + .5, cy_ + .5); a.extra_blk.add((cx_, cy_))
    # portas: braseiros nos batentes (a Porta Dourada, fechada desde Ezequiel, foi aberta pelos Arautos no primeiro dia)
    for nome, (lado, c) in PORTAS.items():
        if lado == "y1": p0, p1, fx, fy = (c - 1.6, y1c + 2.2), (c + 2.6, y1c + 2.2), c + .5, y1c + 3.5
        elif lado == "y0": p0, p1, fx, fy = (c - 1.6, y0c - 1.2), (c + 2.6, y0c - 1.2), c + .5, y0c - 2.5
        elif lado == "x0": p0, p1, fx, fy = (x0c - 1.2, c - 1.6), (x0c - 1.2, c + 2.6), x0c - 2.5, c + .5
        else: p0, p1, fx, fy = (x1c + 2.2, c - 1.6), (x1c + 2.2, c + 2.6), x1c + 3.5, c + .5
        a.prop("braseiro_sagrado", *p0, bloqueia=.4, luz=BRASA + [6]); a.prop("braseiro_sagrado", *p1, bloqueia=.4, luz=BRASA + [6])
        a.prop("estandarte_rasgado", fx, fy, bloqueia=.3)
        lugares.append({"id": f"porta_{nome}", "nome": {"dourada": "Porta Dourada", "damasco": "Porta de Damasco", "esterco": "Porta do Esterco",
                                                         "fonte": "Porta da Fonte"}[nome], "pos": [fx, fy]})
    # a Cúpula sobre a Pedra e a Brasa do Altar (Is 6:6): o fogo que não apaga desde o primeiro toque
    predio("cupula_estacao", 98.5, 50.5, (5, 5), luz=SANTO + [9], marco="cupula_da_pedra", pendente="cupula_da_rocha")
    pendentes.append("cupula_da_rocha (cúpula de latão dourado sobre a Pedra; hoje usa cupula_estacao)")
    a.prop("braseiro_sagrado", 101.5, 46.0, bloqueia=.6, luz=BRASA + [11], marco="brasa_do_altar")
    for (dx, dy) in [(-2.5, -1.5), (2.5, -1.5), (-2.5, 2.0), (2.5, 2.0)]: a.prop("velas_chao", 101.5 + dx, 46 + dy, luz=VELA + [3])
    a.prop("pulpito_externo", 104.5, 49.5, bloqueia=.6)
    for (x, y) in [(95.5, 44.0), (95.5, 46.0), (95.5, 48.0)]: a.prop("banco_capela", x, y, bloqueia=.5)
    a.prop("tubos_orgao", 92.5, 54.0, bloqueia=1.0, luz=SANTO + [5])                    # o Coro de Sião
    predio("torre_sino", 92.0, 38.5, (3, 3), luz=FOGO + [6], marco="torre_de_davi")
    # Legião Blasfema: tendas e a forja de Tubal no canto da Porta da Fonte
    predio("tenda_demonio", 109.0, 52.0, (3, 3), luz=FOGO + [5])
    a.prop("bancada_ferreiro", 108.5, 39.5, bloqueia=.6); a.prop("braseiro_ferro", 110.5, 38.0, bloqueia=.4, luz=FOGO + [6])
    a.prop("tonel_fogo", 106.5, 37.5, bloqueia=.4, luz=FOGO + [5]); a.prop("pilha_carvao", 111.0, 40.5, bloqueia=.4)
    a.prop("caldeirao_cardo", 94.5, 40.0, bloqueia=.5, luz=FOGO + [4])                  # o caldeirão da Zilpa (hissopo)
    a.prop("carrinho_tobias", 106.0, 46.5, bloqueia=.5, ponto="carrinho_bartimeu")
    a.prop("arca_primarca", 96.0, 53.5, bloqueia=.5, luz=[.62, .4, 1] + [6])
    a.prop("trono_sucata", 110.5, 55.0, bloqueia=.6)                                       # a cadeira vazia do general, na tenda
    for (x, y) in [(91.5, 41.5), (91.5, 51.5), (110.5, 44.5), (110.5, 48.5), (100.5, 55.0), (100.5, 37.5)]:
        a.prop("lanterna_procissao", x, y, bloqueia=.2, luz=VELA + [5])
    for (x, y) in [(93.5, 49.0), (107.5, 43.5), (103.0, 38.5)]: a.prop("estatua_anjo_quebrada", x, y, bloqueia=.7)
    a.prop("caixas", 111.0, 45.0, bloqueia=.4); a.prop("barris", 111.2, 42.8, bloqueia=.4); a.prop("sacos_areia", 97.5, 37.5, bloqueia=.3)
    a.espalhar(["velas_chao", "folhas_papeis", "penas_espalhadas"], 18, (x0c + 1, y0c + 1, x1c - 1, y1c - 1))
    npcs = [("sariel_porta", 103.5, 54.5, [0, -1]), ("hulda_escada", 100.0, 44.0, [1, 0]), ("zilpa_hissopo", 94.5, 41.8, [1, 0]),
            ("tubal_malho", 108.8, 41.5, [-1, 0]), ("bartimeu_brasas", 106.0, 44.8, [-1, 0]), ("zaqueu_cobrador", 98.5, 38.4, [0, 1]),
            ("gustavo_primarca", 96.0, 52.2, [1, 0])]
    # ================================================================ fora da muralha
    # Cidade de Davi (1-3): a cidade de baixo, de antes dos muros; escadas de Siloé, o tanque seco
    dx_, dy_ = B["DAVI"][:2]
    predio("casa_ruina", dx_ - 4.0, dy_ + 3.5, (6, 6), luz=VELA + [4]); predio("barraco_sucata", dx_ + 4.5, dy_ + 1.0, (3, 3))
    a.prop("poco", B["SILOE"][0] - 4.5, B["SILOE"][1] + 4.0, bloqueia=.8, marco="tanque_de_siloe")
    npcs.append(("zaqueu_cobrador_casa", dx_ + 2.5, dy_ - 1.0, [1, 0]))
    lugares.append({"id": "tanque_de_siloe", "nome": "Tanque de Siloé", "pos": [B["SILOE"][0] - 4.5, B["SILOE"][1] + 4.0]})
    lugares.append({"id": "casa_do_cobrador", "nome": "Casa do Cobrador", "pos": [dx_ + 4.5, dy_ + 1.0]})
    # Monte das Oliveiras (1-3): oliveiras mortas, o Getsêmani, os túmulos dos profetas descendo a encosta
    gx, gy = B["GETS"][:2]
    a.prop("arvore_morta_grande", gx - 5.5, gy + 5.5, bloqueia=1.0, marco="oliveira_do_getsemani", pendente="oliveira_morta")
    pendentes.append("oliveira_morta / oliveira_morta_2 (oliveira retorcida milenar; hoje usa arvore_morta*)")
    lugares.append({"id": "getsemani", "nome": "Jardim do Getsêmani", "pos": [gx, gy]})
    # Vale de Josafá (2-4): o vale do julgamento, o leito seco do Cedrom, ossos de todas as nações (Jl 3:2)
    jx, jy = B["JOS"][:2]
    a.prop("toca_caes", jx + 4.0, jy + 3.5, bloqueia=1.0, marco="covil_dos_chacais")
    lugares.append({"id": "leito_do_cedrom", "nome": "Leito do Cedrom", "pos": [B["JOS2"][0], B["JOS2"][1]]})
    # Necrópole (3-5): os primeiros a levantar; Rispa guarda os que caem de novo
    nx, ny = B["NEC2"][:2]
    predio("mausoleu", nx + 3.5, ny + 3.0, (3, 3)); predio("casa_coveiro", nx - 4.5, ny + 2.5, (3, 3))
    npcs.append(("rispa_vigilia", nx - 2.0, ny - 1.5, [1, 0]))
    a.prop("fogueira", nx - .5, ny - 3.5, bloqueia=.5, luz=FOGO + [6])
    lugares.append({"id": "tumulos_dos_profetas", "nome": "Túmulos dos Profetas", "pos": [nx + 3.5, ny + 3.0]})
    # Bosque do Hissopo (2-4): a cabana do Escriba, entre a cidade e as fontes
    hx, hy = B["HIS"][:2]
    predio("casa_coveiro", hx - 3.5, hy + 3.0, (3, 3), marco="cabana_do_escriba")
    a.prop("lampiao_gas", hx - 1.0, hy + 1.0, bloqueia=.2, luz=VELA + [5]); a.prop("folhas_papeis", hx - 1.5, hy - .5, chao=True)
    npcs.append(("henoc_escriba", hx - 1.8, hy + .2, [1, 0]))
    lugares.append({"id": "cabana_do_escriba", "nome": "Cabana do Escriba", "pos": [hx - 3.5, hy + 3.0]})
    # Vale do Hinom (4-7): a Geena. Aceldama, o Campo de Sangue (a árvore do enforcado), as fornalhas de Tofete
    ix, iy = B["HIN"][:2]
    a.prop("arvore_enforcados", ix + 3.5, iy + 4.0, bloqueia=1.0, marco="aceldama")
    lugares.append({"id": "aceldama", "nome": "Aceldama, o Campo de Sangue", "pos": [ix + 3.5, iy + 4.0]})
    tx, ty = B["TOF"][:2]
    predio("caldeira_vapor", tx - 5.5, ty + 5.0, (2, 2), luz=FOGO + [8], marco="fornalha_de_tofete")
    predio("moedor_vapor", tx + 6.0, ty + 4.0, (4, 4), luz=FOGO + [8])
    a.prop("trono_sucata", tx - 6.5, ty - 3.5, bloqueia=.6, marco="trono_da_geena")
    lugares.append({"id": "trono_da_geena", "nome": "Trono da Geena", "pos": [tx - 6.5, ty - 3.5]})
    # Pocilgas de Gadara (4-6): a vara da Legião (Mc 5:9-13)
    px_, py_ = B["POC"][:2]
    for (dx, dy) in [(-6, -3), (-6, 0), (-6, 3), (6, -3), (6, 0), (6, 3)]: a.prop("cerca_chiqueiro_b", px_ + dx, py_ + dy, bloqueia=.3)
    a.prop("cocho", px_ - 3.5, py_ + 5.5, bloqueia=.4); a.prop("tanque_salmoura", px_ + 4.5, py_ + 6.0, bloqueia=.7)
    # Encosta dos Cedros (4-5): os cedros do Líbano partidos, ossadas de Nefilins no cascalho
    cx_, cy_ = B["CED"][:2]
    predio("ossada_gigante", cx_ - 7.0, cy_ + 6.5, (6, 4), marco="ossada_nefilim")
    lugares.append({"id": "ossada_nefilim", "nome": "Ossada do Nefilim", "pos": [cx_ - 7.0, cy_ + 6.5]})
    # posto de escuta da Jael (linha "O Juramento do Hermon"): torre, postes de telégrafo, a antena (pendente)
    c2x, c2y = B["CED2"][:2]
    predio("torre_vigia_enterrada", c2x - 3.5, c2y + 3.5, (4, 4), luz=FRIO + [6], marco="posto_de_escuta")
    a.prop("poste_telegrafo", c2x + 2.5, c2y + 3.5, bloqueia=.3); a.prop("poste_telegrafo", c2x + 5.5, c2y - 1.0, bloqueia=.3)
    npcs.append(("jael_escuta", c2x - .5, c2y + .8, [0, -1]))
    pendentes.append("antena_radio (antena da Escuta; mesmo pedido do deserto)")
    lugares.append({"id": "posto_de_escuta", "nome": "Posto de Escuta do Hermon", "pos": [c2x - 3.5, c2y + 3.5]})
    # Fontes do Jordão (6-8): Banias. A gruta de Pã, os Portões do Hades (Mt 16:18), o canteiro dos sapadores
    sx, sy = B["SAP"][:2]
    a.prop("roda_dagua_bomba", sx + 6.5, sy + 6.0, bloqueia=.9, luz=FRIO + [4])
    predio("tenda_vigilia", sx - 6.0, sy - 4.5, (3, 3)); a.prop("caldeira_vapor", sx - 7.5, sy + 2.5, bloqueia=1.0, luz=FOGO + [6])
    a.prop("barricada_sacos_a", sx + 5.0, sy - 5.0, bloqueia=.4); a.prop("barricada_sacos_b", sx - 3.0, sy - 7.0, bloqueia=.4)
    hx2, hy2 = PORTA_HADES
    predio("portal_dungeon", hx2, hy2 + .6, (3, 1), luz=BRASA + [7], marco="portoes_do_hades")
    for (dx, dy) in [(-3.5, 1.5), (3.5, 1.5)]: a.prop("pilar_porcelana", hx2 + dx, hy2 + dy, bloqueia=.7)
    a.prop("estatua_anjo_quebrada", hx2 - 5.5, hy2 + 3.5, bloqueia=.7)
    # a porta é um interativo como a Porta do Porão do deserto (requer a Chave de Pã; depois de aberta, leva direto)
    a.objetos.append({"kind": "interativo", "obj": "porta_de_pa", "pos": [hx2, hy2 - 1.0], "i": 0, "mapa": "minas_dos_gigantes", "chegada": [12.5, 50.5]})
    lugares.append({"id": "portoes_do_hades", "nome": "Portões do Hades", "pos": PORTA_HADES})
    # Cume do Hermon (9-12): neve de cinza, as pegadas dos duzentos, a laje do juramento; a nevasca é a borda do mundo
    ex, ey = B["NEVE"][:2]
    a.prop("cratera_corte", ex + 6.5, ey - 4.0, chao=True); a.prop("asa_anjo_caida", ex - 6.0, ey - 3.5, bloqueia=.6)
    a.prop("elmo_espada_fincada", ex + 5.5, ey + 4.5, bloqueia=.3)
    k2x, k2y = B["CUM2"][:2]
    a.prop("laje_rolada", k2x - 3.0, k2y + 3.5, bloqueia=.6, marco="laje_do_juramento")
    for i in range(7):
        t = i/7*math.tau; a.prop("pilar_porcelana", k2x - 3.0 + math.cos(t)*4.2, k2y + 3.5 + math.sin(t)*4.2, bloqueia=.6)
    lugares.append({"id": "laje_do_juramento", "nome": "Laje do Juramento", "pos": [k2x - 3.0, k2y + 3.5]})

    # ================================================================ borda: o mundo acaba em encosta, não em muro
    # vegetação/pedra alta só onde não há chão aberto na frente (câmera), baixa na frente
    alta = {"cidade_de_davi": ["casa_ruina", "ruina_concreto", "muro_tijolo_quebrado_a", "muro_tijolo_quebrado_b"],
            "monte_oliveiras": ["arvore_morta", "arvore_morta_2", "arvore_morta_grande", "arvore_morta"],
            "vale_josafa": ["arvore_morta_2", "ruina_concreto", "forca_ponte"],
            "bosque_hissopo": ["arvore_morta", "arvore_morta_2", "arvore_morta"],
            "necropole_oliveiras": ["mausoleu", "arvore_morta", "mar_de_lapides", "casa_coveiro"],
            "encosta_cedros": ["arvore_morta_grande", "arvore_morta", "arvore_morta_grande", "ossada_gigante"],
            "vale_hinom": ["chamine_enterrada", "guindaste_sucata", "arvore_morta_2", "ruina_concreto"],
            "pocilgas_gadara": ["arvore_morta_2", "barraco_sucata", "arvore_morta"],
            "fontes_jordao": ["arvore_morta_grande", "arvore_morta", "ruina_concreto"],
            "cume_hermon": ["ossada_gigante", "estatua_anjo_quebrada", "torre_tombada", "ossada_gigante"],
            "jerusalem": ["casa_ruina", "ruina_concreto"]}
    baixa = {"cidade_de_davi": ["entulho", "muro_tijolo_quebrado_b", "sacos_areia", "laje_rolada"],
             "monte_oliveiras": ["toco_arvore", "arbusto_seco", "mato_seco", "lapide", "arbusto_seco_2"],
             "vale_josafa": ["ossada_viajante", "mato_seco", "pedras_rio", "cruz_madeira"],
             "bosque_hissopo": ["moita_cardo", "arbusto_seco", "toco_arvore", "mato_seco_2"],
             "necropole_oliveiras": ["lapide", "lapide_obelisco", "lapide_cruz_celta", "tumulo_vitoriano", "lapide_vitoriana"],
             "encosta_cedros": ["toco_arvore", "mato_seco", "arbusto_seco_2", "laje_rolada"],
             "vale_hinom": ["pilha_carvao", "entulho", "tambores_radioativos", "mato_seco"],
             "pocilgas_gadara": ["estacas_cerca", "mato_seco", "arbusto_seco", "lama_porcos"],
             "fontes_jordao": ["juncos", "pedras_rio", "tronco_margem", "mato_seco"],
             "cume_hermon": ["laje_rolada", "ossada_animal", "cratera_cinza", "elmo_espada_fincada"],
             "jerusalem": ["entulho", "laje_rolada"]}
    feitas = []
    for y in range(H):
        for x in range(W):
            if not a.blk[y][x] or a.ter[y][x] == "w": continue
            if x0c - 2 <= x <= x1c + 2 and y0c - 2 <= y <= y1c + 2: continue
            if dist_poli(x + .5, y + .5, FENDA) < 2.2: continue                       # a fenda fica à vista
            if not any(0 <= x + dx < W and 0 <= y + dy < H and not a.blk[y + dy][x + dx] for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)): continue
            qx, qy = x + rng.uniform(.2, .8), y + rng.uniform(.2, .8)
            if any(math.dist((qx, qy), f) < 2.1 for f in feitas[-90:]): continue
            zv = [zona_de[y + dy][x + dx] for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)
                  if 0 <= x + dx < W and 0 <= y + dy < H and zona_de[y + dy][x + dx]]
            z = zv[0] if zv else "monte_oliveiras"
            frente = any(0 <= x + k + d < W and 0 <= y - k < H and not a.blk[y - k][x + k + d] for k in range(1, 9) for d in (-1, 0, 1))
            k = rng.choice(baixa[z] if frente else alta[z])
            feitas.append((qx, qy)); a.prop(k, qx, qy, decor_moldura=True)
            if z == "vale_hinom" and rng.random() < .12: a.luzes.append([round(qx, 2), round(qy, 2)] + BRASA + [5])

    # ================================================================ spots estilo MU (anel de grupos, fogueira na chegada, marco atrás)
    marcos = {"escadas_de_siloe": "muro_tijolo_quebrado_a", "getsemani": "arvore_morta_grande", "fenda_das_oliveiras": "cratera_corte",
              "covil_dos_chacais": "ossada_viajante", "primeiros_a_levantar": "mar_de_lapides", "cedros_partidos": "arvore_morta_grande",
              "fornalhas_de_tofete": "tonel_fogo", "pocilga_de_gadara": "barraco_sucata", "acampamento_sapadores": "guindaste_sucata",
              "neve_de_cinza": "torre_tombada"}
    for key, (bx, by, r, z, sp) in blobs:
        if not sp: continue
        sid, nome, niv, grupos, esp = sp
        resp = 18 if niv[0] == 1 else 14
        spots.append({"id": sid, "nome": nome, "nivel": niv, "pos": [bx, by], "raio": round(r*.85, 1), "respawn_s": resp, "espelho": esp,
                      "zona": z})
        # grupos = os do spot espelhado no jogo de hoje (game/data/mapas/area_inicial.json), com o mob trocado pelo espelho
        gd = [g for g in DESERTO_GAME["spawns"] if g.get("spot") == esp]
        listas = {}
        for g in gd: listas.setdefault(g["mob"], []).append((ESPELHO_DE[g["mob"]], g["qtd"], g["nivel"], g.get("temperamento", "neutro")))
        listas = list(listas.values())
        fila = [l.pop(0) for _ in range(max(len(l) for l in listas)) for l in listas if l]
        ng = len(fila)
        vx, vy = (B["J"][0] - bx, B["J"][1] - by); dn = math.hypot(vx, vy); vx, vy = vx/dn, vy/dn
        ang_cam = math.atan2(vy, vx)
        cands = []
        for ia in range(36):
            ang = ang_cam + math.pi + (ia - 18)/36*2*math.pi*.86
            for rr in (r*.36, r*.52, r*.66, r*.22, r*.76, r*.88):
                cands.append((abs(ia - 18) % 7, bx + math.cos(ang)*rr, by + math.sin(ang)*rr))
        cands.sort(key=lambda c: c[0])
        postos = []
        for (_, x, y) in cands:
            if len(postos) >= ng: break
            if not livre3(int(x), int(y)) or perto_prop(x, y, 1.6): continue
            mob, qtd, nv, temp = fila[len(postos)]
            if any(math.dist((x, y), p) < (4.6 if temp == "territorial" else 3.0) for p in postos): continue
            s_ = {"mob": mob, "pos": [round(x, 1), round(y, 1)], "raio": 1.5, "qtd": qtd, "nivel": nv, "temperamento": temp,
                  "spot": sid, "respawn_s": resp, "motivo": MOBS[mob]["motivo"]}
            if temp == "territorial": s_["raio_territorio"] = 4
            a.spawns.append(s_); postos.append((x, y))
        if len(postos) < ng: print("SPOT INCOMPLETO", sid, len(postos), "de", ng)
        mx, my = bx - r*.62, by + r*.62
        if a.livre(int(mx), int(my)) and not agua(int(mx), int(my)) and not perto_prop(mx, my, 2.0):
            a.prop(marcos[sid], mx, my, bloqueia=.8 if marcos[sid] not in ("cratera_corte",) else 0, chao=marcos[sid] == "cratera_corte")
    # ---- 6 pontos de descanso (fogueira + carrinho do Bartimeu), um para cada par de spots, como no deserto
    pares = [("getsemani", "escadas_de_siloe"), ("covil_dos_chacais", "fenda_das_oliveiras"), ("primeiros_a_levantar", "acampamento_sapadores"),
             ("fornalhas_de_tofete", "pocilga_de_gadara"), ("cedros_partidos", "neve_de_cinza"), ("acampamento_sapadores", "fenda_das_oliveiras")]
    nomes_desc = ["Fogueira do Lagar", "Fogueira do Cedrom", "Fogueira das Fontes", "Fogueira de Aceldama", "Fogueira dos Cedros", "Fogueira do Hissopo"]
    pos_sp = {s["id"]: s["pos"] for s in spots}
    for (s1, s2), nome in zip(pares, nomes_desc):
        (ax_, ay_), (bx_, by_) = pos_sp[s1], pos_sp[s2]
        alvo = ((ax_ + bx_)/2, (ay_ + by_)/2)
        melhor = None
        for y in range(H):
            for x in range(W):
                if not trilha[y][x]: continue
                for (ox, oy) in [(1.8, -1.8), (-1.8, 1.8), (2.2, 0), (0, 2.2)]:
                    qx, qy = x + .5 + ox, y + .5 + oy
                    if not livre3(int(qx), int(qy)) or trilha[int(qy)][int(qx)] or em_spot(qx, qy, 1.0): continue
                    d = math.dist((qx, qy), alvo)
                    if melhor is None or d < melhor[0]: melhor = (d, qx, qy)
        if not melhor: print("SEM DESCANSO", nome); continue
        _, qx, qy = melhor
        if any(math.dist((qx, qy), (d["x"], d["y"])) < 8 for d in descanso): continue
        a.prop("fogueira", qx, qy, bloqueia=.5, luz=FOGO + [6])
        a.prop("carrinho_tobias", qx + 1.8, qy + .8, bloqueia=.5, ponto="descanso")
        descanso.append({"nome": nome, "x": round(qx, 1), "y": round(qy, 1), "props": ["fogueira", "carrinho_tobias"],
                         "npc": "bartimeu_carrinho (vende poção)", "entre": [s1, s2]})
        npcs.append(("bartimeu_carrinho", round(qx + 2.6, 1), round(qy - .4, 1), [-1, 0]))

    # ================================================================ fora dos spots: poucos pares, com motivo e respiro (11 mobs, como no deserto)
    for (k1, k2, mob, niv, qtd, temp) in [("J", "GETS", "peregrino_ressecado", 2, 2, "neutro"), ("J", "DAVI", "chacal_de_josafa", 2, 3, "territorial"),
                                          ("HIS", "FENDA", "levantado_das_oliveiras", 3, 2, "neutro"), ("NEC2", "PRIM", "levantado_das_oliveiras", 5, 2, "neutro"),
                                          ("J", "HIN", "fornalheiro_de_tofete", 5, 1, "agressivo"), ("HIN", "TOF", "fornalheiro_de_tofete", 7, 1, "agressivo")]:
        (x0, y0), (x1, y1) = B[k1][:2], B[k2][:2]
        ok = False
        for t in (.5, .4, .6, .32, .68, .25, .75):
            for (ox, oy) in [(2.5, -2.5), (-2.5, 2.5), (3.5, 0), (0, 3.5), (0, 0), (-3.5, 0), (0, -3.5), (4.5, -4.5), (-4.5, 4.5)]:
                x, y = x0 + (x1 - x0)*t + ox, y0 + (y1 - y0)*t + oy
                if livre3(int(x), int(y)) and not trilha[int(y)][int(x)] and not em_spot(x, y, 2) and not perto_prop(x, y, 1.3): ok = True; break
            if ok: break
        if not ok: print("PAR SEM LUGAR", mob); continue
        s_ = {"mob": mob, "pos": [round(x, 1), round(y, 1)], "raio": 1.5, "qtd": qtd, "nivel": niv, "temperamento": temp, "respawn_s": 25,
              "motivo": MOBS[mob]["motivo"]}
        if temp == "territorial": s_["raio_territorio"] = 4
        a.spawns.append(s_)
    # filho do hissopo (só para a missão da Zilpa, como o Filho de Cardo)
    a.spawns.append({"mob": "filho_do_hissopo", "pos": [hx + 4.5, hy - 4.0], "raio": .5, "qtd": 1, "nivel": 5, "temperamento": "neutro",
                     "respawn_s": 60, "so_para": "missao_js02", "motivo": MOBS["filho_do_hissopo"]["motivo"]})

    # ================================================================ props soltos por zona (vocabulário de cada área)
    def solto(kinds, n, bloq, dist, zonas, spot_ok=False, chao=False, luz=None, pisos=None):
        f = t = 0
        while f < n and t < 9000:
            t += 1
            x, y = rng.uniform(4, W - 4), rng.uniform(4, H - 4); ix, iy = int(x), int(y)
            if a.blk[iy][ix] or trilha[iy][ix] or agua(ix, iy) or zona_de[iy][ix] not in zonas: continue
            if pisos and a.ter[iy][ix] not in pisos: continue
            if not spot_ok and em_spot(x, y, 1.5): continue
            if bloq and not livre3(ix, iy): continue
            if perto_prop(x, y, dist): continue
            if math.dist((x, y), PORTA_HADES) < 5 or (x0c - 3 <= x <= x1c + 3 and y0c - 3 <= y <= y1c + 3): continue
            a.prop(rng.choice(kinds), x, y, bloqueia=bloq, chao=chao); f += 1
            if luz and rng.random() < luz[0]: a.luzes.append([round(x, 2), round(y, 2)] + luz[1:])
    solto(["arvore_morta", "arvore_morta_2"], 26, .7, 4.5, ["monte_oliveiras", "bosque_hissopo"])                        # o olival morto
    solto(["toco_arvore", "arbusto_seco", "mato_seco", "arbusto_seco_2"], 50, 0, 2.2, ["monte_oliveiras", "bosque_hissopo", "encosta_cedros"], spot_ok=True)
    solto(["lapide", "lapide_obelisco", "lapide_cruz_celta", "tumulo_aberto", "lapide_vitoriana"], 60, .3, 2.0, ["necropole_oliveiras", "monte_oliveiras"], spot_ok=True)
    solto(["mar_de_lapides", "tumulo_vitoriano"], 10, .8, 5.0, ["necropole_oliveiras"])
    solto(["cova_aberta", "vala_aberta"], 8, .8, 5.0, ["vale_josafa"])
    solto(["ossada_viajante", "ossos_espalhados", "pilha_cranios", "cruz_madeira"], 34, 0, 2.2, ["vale_josafa", "necropole_oliveiras"], spot_ok=True)
    solto(["entulho", "laje_rolada", "muro_tijolo_quebrado_a", "muro_tijolo_quebrado_b", "placa_rua_enterrada"], 24, .4, 2.6, ["cidade_de_davi"], spot_ok=True)
    solto(["moita_cardo", "moita_cardo", "arbusto_seco_2", "cogumelos_palidos"], 30, 0, 1.8, ["bosque_hissopo"], spot_ok=True)
    solto(["arvore_morta_grande", "arvore_morta"], 14, 1.0, 6.0, ["encosta_cedros"])                                    # cedros partidos
    solto(["toco_arvore", "tronco_margem", "laje_rolada", "ossada_animal"], 26, 0, 2.4, ["encosta_cedros", "cume_hermon"], spot_ok=True)
    solto(["tonel_fogo", "braseiro_ferro"], 12, .4, 6.0, ["vale_hinom"], spot_ok=True, luz=[1.0] + FOGO + [5])
    solto(["pilha_carvao", "poca_sangue", "ganchos_carne", "carrinho_carne", "mesa_acougue_rua"], 26, .3, 2.6, ["vale_hinom"], spot_ok=True)
    solto(["estandarte_rasgado", "tenda_demonio"], 6, .8, 7.0, ["vale_hinom"])
    solto(["lama_porcos", "poca_agua"], 22, 0, 1.6, ["pocilgas_gadara"], spot_ok=True, chao=True)
    solto(["cerca_chiqueiro_a", "cerca_chiqueiro_b", "cocho", "sacos_sal", "barris"], 18, .3, 2.8, ["pocilgas_gadara"])
    solto(["juncos", "pedras_rio", "tronco_margem"], 34, 0, 1.8, ["fontes_jordao"], spot_ok=True, pisos="bkzt")
    solto(["canos_parede", "tanque_latao", "caixas", "barris", "sacos_areia"], 12, .5, 4.0, ["fontes_jordao"])
    solto(["asa_anjo_caida", "elmo_espada_fincada", "cratera_cinza", "penas_espalhadas", "laje_rolada"], 30, .3, 3.0, ["cume_hermon"], spot_ok=True)
    solto(["estatua_anjo_quebrada", "pilar_porcelana", "anjo_porcelana_caido"], 9, .7, 7.0, ["cume_hermon", "fontes_jordao"])
    # postes de gás ao longo da Estrada dos Peregrinos (metade apagados), a cada ~10 m
    ult = []
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            if not estrada[y][x] or any(math.dist((x, y), u) < 10 for u in ult): continue
            if x0c - 3 <= x <= x1c + 3 and y0c - 3 <= y <= y1c + 3: continue
            for (dx, dy) in [(-1.6, 1.6), (1.6, -1.6), (1.6, 1.6), (-1.6, -1.6)]:
                qx, qy = x + .5 + dx, y + .5 + dy
                if a.livre(int(qx), int(qy)) and not trilha[int(qy)][int(qx)] and not agua(int(qx), int(qy)) and not perto_prop(qx, qy, 1.5):
                    acesa = len(ult) % 2 == 0
                    a.prop("poste_gas" if acesa else "poste_gas_quebrado", qx, qy, bloqueia=.2, luz=(VELA + [5]) if acesa else None)
                    ult.append((x, y)); break
    # pontes: sobre a fenda e sobre o riacho onde a trilha cruza
    feitas_p = []
    for (x, y) in fenda_pontes:
        if not any(math.dist((x, y), p) < 3 for p in feitas_p): a.prop("ponte_madeira_a", x + .5, y + .5, chao=True); feitas_p.append((x, y))
    for y in range(H):
        for x in range(W):
            if a.ter[y][x] == "r" and trilha[y][x] and not any(math.dist((x, y), p) < 4 for p in feitas_p):
                a.prop("ponte_madeira_b", x + .5, y + .5, chao=True); feitas_p.append((x, y))

    # ================================================================ baús (20, como o deserto sem os 3 de missão do Tobias)
    BAUS = [(127.5, 33.5, "caixote_podre", "bau_comum", "jh_davi_porao", None), (139.0, 28.5, "caixote_podre", "bau_comum", "jh_siloe", None),
            (115.5, 75.5, "caixote_podre", "bau_comum", "jh_lagar", ("Lagar das Oliveiras", "No fundo do lagar seco, onde a última azeitona virou pedra, uma bolsa de couro com moedas de peregrino.")),
            (126.0, 63.0, "bau_de_ferro", "bau_raro", "jh_getsemani_gruta", ("Gruta do Getsêmani", "Na gruta onde Ele suou sangue, alguém deixou uma arca de ferro. Dentro, panos dobrados com cuidado e uma lâmina.")),
            (98.5, 90.5, "caixote_podre", "bau_comum", "jh_fenda", "mimico"), (140.5, 90.0, "bau_de_ferro", "bau_raro", "jh_cedrom", None),
            (142.5, 104.5, "caixote_podre", "bau_comum", "jh_josafa_vala", None), (92.0, 76.0, "caixote_podre", "bau_comum", "jh_hissopo", None),
            (107.5, 124.0, "bau_de_ferro", "bau_raro", "jh_profetas", ("Ossuário de Zacarias", "Um ossuário de pedra com o nome de um profeta raspado. Os ossos foram embora sozinhos; ficou o que estava embaixo deles.")),
            (122.0, 109.0, "caixote_podre", "bau_comum", "jh_rispa", None), (66.5, 27.5, "caixote_podre", "bau_comum", "jh_aceldama", ("Trinta Moedas", "Ao pé da árvore de Aceldama, uma bolsa rasgada. Trinta moedas de prata, escurecidas. Ninguém tem coragem de gastar todas.")),
            (26.0, 24.0, "bau_de_ferro", "bau_raro", "jh_tofete", "mimico"), (20.0, 70.0, "caixote_podre", "bau_comum", "jh_gadara", None),
            (46.5, 48.5, "caixote_podre", "bau_comum", "jh_cevada", None), (38.0, 120.0, "bau_de_ferro", "bau_raro", "jh_cedros", None),
            (56.0, 100.5, "caixote_podre", "bau_comum", "jh_escuta", "mimico"), (70.5, 100.0, "caixote_podre", "bau_comum", "jh_sapadores", ("Caixa de Ferramentas do Sapador", "Ferramentas de engenheiro com a vela da Vigília gravada no cabo. Embaixo, o pagamento da semana que ninguém veio buscar.")),
            (94.5, 106.0, "bau_de_ferro", "bau_raro", "jh_banias", None), (66.0, 130.5, "caixote_podre", "bau_comum", "jh_laje", None)]
    for (x, y, b, vis, idm, extra) in BAUS:
        q = None
        for r_ in range(0, 6):
            for dy in range(-r_, r_ + 1):
                for dx in range(-r_, r_ + 1):
                    if q is None and livre3(int(x + dx), int(y + dy)) and not trilha[int(y + dy)][int(x + dx)]: q = (x + dx, y + dy)
        if q is None: print("BAÚ SEM LUGAR", idm); continue
        o = {"kind": "bau", "pos": [round(q[0], 1), round(q[1], 1)], "bau": b, "visual": vis, "id_mapa": idm}
        if extra == "mimico": o["mimico"] = True
        elif extra: o["nome"], o["texto_ao_abrir"] = extra
        a.objetos.append(o)
    # baú trancado da Hulda (espelho do baú da barraca do Anselmo) e os 3 esconderijos do Bartimeu (espelho dos do Tobias)
    a.objetos.append({"kind": "bau", "pos": [99.5, 42.0], "bau": "caixote_podre", "visual": "bau_comum", "id_mapa": "bau_escada_hulda", "trancado": True,
                      "hist": "bau_escada_hulda", "visivel_se": {"missao_concluida": "jc01"}})

    # ================================================================ interativos das missões (ids em objetos_acrescimo.json)
    def inter(obj, pts, prop=None, **kw):
        for i, (x, y) in enumerate(pts):
            q = None
            for r_ in range(0, 6):
                for dy in range(-r_, r_ + 1):
                    for dx in range(-r_, r_ + 1):
                        if q is None and livre3(int(x + dx), int(y + dy)) and not perto_prop(x + dx, y + dy, 1.0): q = (x + dx + .0, y + dy + .0)
            if q is None: print("INTERATIVO SEM LUGAR", obj, i); continue
            o = {"kind": "interativo", "obj": obj, "pos": [round(q[0], 1), round(q[1], 1)], "i": i}; o.update(kw); a.objetos.append(o)
            if prop: a.prop(prop, q[0], q[1] + .6, bloqueia=0)
    inter("peregrino_de_joelhos", [(96, 114), (104, 122), (110, 112)], prop="corpo_lacrado")
    inter("tumulos_dos_profetas", [(112, 100), (120, 98), (124, 108), (96, 122), (106, 114)], prop="tumulo_aberto")
    for i, (x, y) in enumerate([(118.5, 64.5), (82.5, 66.5), (131.5, 31.5)]):
        o = {"kind": "bau", "pos": [x, y], "bau": "caixote_podre" if i < 2 else "bau_de_ferro", "visual": "bau_comum" if i < 2 else "bau_raro",
             "id_mapa": f"bau_bartimeu_{i + 1}", "hist": f"bau_bartimeu_{i + 1}", "visivel_se": {"missao_ativa": "js04"}}
        if i == 2: o["trancado"] = True
        a.objetos.append(o)
    inter("forja_de_tofete", [(B["TOF"][0] - 5.0, B["TOF"][1] + 2.5)])
    inter("mesa_do_capataz", [(B["TOF"][0] + 3.5, B["TOF"][1] - 6.5)], prop="mesa_acougue")
    inter("antena_da_escuta", [(c2x - 1.0, c2y + 5.5)], prop="poste_telegrafo")
    inter("fontes_secas", [(80, 104), (96, 106), (84, 112)], prop="poca_toxica")
    inter("laje_do_juramento", [(k2x - 3.0, k2y + 1.0)])
    inter("estandartes_da_legiao", [(76, 26), (60, 38), (50, 30)], prop="estandarte_rasgado")
    inter("trono_vazio", [(tx - 6.0, ty - 5.5)])
    inter("rastro_de_brasas", [(38, 58), (48, 64), (52, 72)], prop="rastro_arrasto")
    inter("rolos_da_escada", [(100.5, 52.5)])
    inter("pedra_da_ascensao", [(gx + 3.0, gy - 6.0)], prop="laje_rolada")
    inter("tumulo_de_joas", [(nx - 6.5, ny - 3.5)], prop="lapide_cruz_celta")
    inter("tumulo_vazio_de_henoc", [(nx - 8.0, ny + 1.0)], prop="sepulcro_primeiro")
    inter("ninhos_de_abutre", [(112, 62), (126, 74), (110, 70)], prop="poste_ninho")

    # ---- passada final: todo grupo em célula livre e longe de prop que bloqueia
    for sp in a.spawns:
        x, y = sp["pos"]
        if livre3(int(x), int(y)) and not perto_prop(x, y, 1.3): continue
        melhor = None
        for dy in range(-3, 4):
            for dx in range(-3, 4):
                qx, qy = x + dx, y + dy
                if livre3(int(qx), int(qy)) and not perto_prop(qx, qy, 1.3) and (melhor is None or math.hypot(dx, dy) < melhor[0]): melhor = (math.hypot(dx, dy), qx, qy)
        if melhor: sp["pos"] = [round(melhor[1], 1), round(melhor[2], 1)]
        else: print("SPAWN SEM LUGAR", sp["mob"], sp["pos"])
    # NPCs: uma célula livre perto do ponto
    for (nid, x, y, d) in npcs:
        if nid == "zaqueu_cobrador_casa": continue           # só o marco do lugar; o Zaqueu fica na cidade
        a.npcs.append({"id": nid, "pos": [x, y], "dir": d})
    m = a.exportar(spawn=SPAWN, ceu={"escuro": 0.22, "cor": [0.8, 0.8, 0.86], "neblina": [0.5, 0.5, 0.58]})
    m["pisos"] = PISOS
    m["spawn_por_faccao"] = {"arautos": SPAWN}
    m["faccao"] = "arautos"
    m["agua"] = {"fundo": [0.05, 0.07, 0.09], "raso": [0.22, 0.26, 0.3], "reflexo": [0.55, 0.58, 0.62], "brilho": [0.85, 0.88, 0.95],
                 "lume": [0.0, 0.0, 0.0], "espuma": [0.7, 0.72, 0.75]}
    m["rio"] = {"id": "fontes_do_jordao", "nome": "Fontes do Jordão", "nota": "degelo de cinza do Hermon; desce para o deserto e lá vira o Rio Amargo",
                "centro": [list(map(float, p)) for p in RIACHO]}
    m["zona_grade"] = ["".join("." if zona_de[y][x] is None else LETRAS[ZI[zona_de[y][x]]] for x in range(W)) for y in range(H)]
    m["zonas"] = [{"id": i, "nome": n, "seguro": s, "nivel": nv, "musica": mu, "ambiente": am, "faccao": "arautos" if s else None, "neblina": ne}
                  for (i, n, s, nv, _, ne, mu, am) in ZONAS]
    m["exterior"] = True
    m["spots"] = spots
    m["descanso"] = descanso
    m["lugares"] = lugares
    m["props_pendentes"] = pendentes
    m["sons"] = [{"som": "ambiente/pontual/coro_distante", "x": 101.0, "y": 46.0, "raio": 30, "intervalo_s": [30, 70]},
                 {"som": "ambiente/pontual/sino_distante", "x": 60.0, "y": 96.0, "raio": 26, "intervalo_s": [40, 90]},
                 {"som": "ambiente/pontual/corvo_distante", "x": 120.0, "y": 70.0, "raio": 24, "intervalo_s": [12, 30]},
                 {"som": "ambiente/pontual/uivo_distante", "x": 134.0, "y": 84.0, "raio": 34, "intervalo_s": [20, 50]},
                 {"som": "ambiente/pontual/porcos", "x": 26.0, "y": 68.0, "raio": 20, "intervalo_s": [8, 20]},
                 {"som": "ambiente/pontual/martelo_forja", "x": 32.0, "y": 30.0, "raio": 24, "intervalo_s": [4, 9]}]
    m["salas"] = [{"nome": (sp[1] if sp else ZONAS[ZI[z]][1]), "ret": [bx - 3, by - 2, bx + 3, by + 2]} for k, (bx, by, r, z, sp) in blobs
                  if sp or k in ("J", "DAVI", "HIS", "HIN", "JOS2", "NEC2", "FON2", "CUM2")]
    json.dump(m, open(f"{AQUI}/jerusalem_hermon.json", "w"), ensure_ascii=False, separators=(",", ":"))
    return m


# ===================================================================================== Fosso dos Vigilantes (3 andares)
# Espelho da Cripta da Trombeta Calada: mesmos tamanhos, mesmos grupos (9/8/5), mesmos níveis, mesmos chefes em número.
def minas_dos_gigantes():
    a = Andar("minas_dos_gigantes", "Minas dos Gigantes", 72, 64, "k", "parede_ossario",
              {"id": "minas_dos_gigantes", "nome": "Minas dos Gigantes", "seguro": False, "nivel": [6, 8],
               "musica": "musica/cripta", "ambiente": "ambiente/cripta_porao"})
    a.sala(8, 45, 17, 56, nome="Boca da Gruta de Pã")
    a.corredor(18, 49, 23, 52)
    a.sala(24, 40, 39, 58, nome="Galeria dos Escravos")
    a.corredor(30, 34, 33, 39)
    a.sala(22, 20, 38, 33, nome="Forja dos Ensinamentos")
    a.corredor(16, 25, 21, 28)
    a.sala(10, 21, 15, 31, nome="Depósito de Sal")
    a.corredor(40, 49, 45, 52)
    a.sala(46, 43, 57, 56, nome="Refeitório dos Gigantes")
    a.corredor(50, 38, 53, 42, piso="n")
    a.corredor(39, 26, 46, 29)
    a.sala(47, 19, 65, 37, piso="v", nome="Cova de Ohya")
    a.corredor(55, 17, 57, 18, piso="n")
    a.sala(52, 12, 60, 16, piso="n", nome="Poço que desce")
    for (x, y) in [(47, 19), (48, 19), (47, 20), (65, 19), (64, 19), (65, 20), (47, 37), (48, 37), (47, 36), (65, 37), (64, 37), (65, 36)]:
        a.fechar(x, y)
    a.pisar(47, 26, 49, 29, "n"); a.pisar(50, 37, 53, 37, "n")
    # boca da gruta
    a.portal(10.5, 48.5, "jerusalem_hermon", CHEGADA_HADES, "Subir para as Fontes do Jordão", visual="escada_subida")
    a.prop("estatua_anjo_quebrada", 15.3, 46.3, bloqueia=.6); a.prop("braseiro_sagrado", 13.5, 53.5, bloqueia=.4, luz=BRASA + [6])
    a.prop("ossada_animal", 15.0, 51.0); a.prop("rastro_arrasto", 19.5, 50.5, chao=True)
    a.luzes += [[13, 48, 0.8, 0.6, 0.4, 5]]
    # galeria dos escravos: correntes e gaiolas, picaretas largadas
    for gx in (27.5, 31.5, 35.5):
        for gy in (43.5, 47.5, 51.5, 55.5):
            if (gx, gy) not in [(31.5, 47.5), (31.5, 51.5)]: a.prop("gaiola_suspensa" if (gx + gy) % 2 else "ganchos_carne", gx, gy, bloqueia=0.4)
    a.prop("carroca_quebrada", 31.5, 49.5, bloqueia=0.7)
    for x, y in [(25.5, 41.5), (38, 41.5), (25.5, 57), (38, 57)]: a.luzes.append([x, y] + FOGO + [5])
    a.espalhar(["ossos_espalhados", "entulho", "poca_sangue"], 10, (24, 40, 39, 58))
    a.spawn("verme_do_fosso", 29.5, 45.5, 2, 1.5, 6); a.spawn("nefilim_mirrado", 33.5, 53.5, 1, 0.5, 6); a.spawn("verme_do_fosso", 37, 44, 2, 1.0, 6)
    # forja dos ensinamentos (Azazel ensinou o ferro): caldeiras, carvão
    a.prop("caldeira_vapor", 25.5, 22.5, bloqueia=1.2, luz=FOGO + [7]); a.prop("caldeira_vapor", 33.5, 22.5, bloqueia=1.2, luz=FOGO + [7])
    a.prop("bancada_ferreiro", 29.5, 21.0, bloqueia=0.6); a.prop("canos_parede", 22.5, 27.5, bloqueia=0.5)
    a.prop("pilha_carvao", 36.5, 25.0, bloqueia=0.6); a.prop("pilha_carvao", 23.5, 31.5, bloqueia=0.6)
    a.prop("tonel_fogo", 30.0, 30.5, bloqueia=0.4, luz=FOGO + [5])
    a.espalhar(["entulho", "pilha_carvao", "poca_agua"], 7, (22, 20, 38, 33))
    a.spawn("escravo_dos_gigantes", 31, 27, 2, 1.5, 7); a.spawn("nefilim_mirrado", 25, 31, 1, 0.5, 7)
    # depósito de sal (sala lateral com baú)
    a.prop("sacos_sal", 11.5, 23.5, bloqueia=0.6); a.prop("sacos_sal", 11.5, 28.0, bloqueia=0.6)
    a.prop("barris", 14.5, 30.5, bloqueia=0.4); a.prop("caixas", 14.5, 22.0, bloqueia=0.4)
    a.objetos.append({"kind": "bau", "pos": [13.5, 26.0], "bau": "bau_de_ferro", "visual": "bau_raro", "id_mapa": "deposito_sal"})
    a.luzes += [[13, 26, 1, 0.5, 0.2, 4]]
    a.spawn("escravo_dos_gigantes", 13, 29, 1, 0.5, 7)
    # refeitório dos gigantes: mesas, ossos roídos, o rastro de Ohya
    a.prop("mesa_acougue", 55.0, 50.0, bloqueia=0.7); a.prop("mesa_acougue", 49.5, 47.0, bloqueia=0.7)
    a.prop("pilha_mortos", 55.5, 54.5, bloqueia=0.8); a.prop("pilha_cranios", 48.5, 54.0, bloqueia=0.6)
    a.prop("tonel_fogo", 56.0, 46.5, bloqueia=0.4, luz=FOGO + [6]); a.prop("ossada_animal", 52.0, 45.0)
    a.espalhar(["poca_sangue", "ossos_espalhados"], 6, (46, 43, 57, 56))
    a.luzes += [[52, 52, 1, 0.4, 0.15, 5]]
    a.spawn("nefilim_mirrado", 52, 50, 1, 0.5, 7); a.spawn("verme_do_fosso", 49, 51, 2, 1.0, 7)
    a.prop("gaiola_suspensa", 42.5, 27.5); a.prop("rastro_arrasto", 51.5, 40.0, chao=True); a.prop("rastro_arrasto", 51.5, 36.0, chao=True)
    a.spawn("soldado_de_pedra", 43, 28, 2, 1.0, 8)
    a.luzes += [[42.5, 27.5, 1, 0.4, 0.12, 4], [51.5, 40, 1, 0.35, 0.12, 4]]
    # cova de Ohya: 6 pilhas de escravos mortos (a mesma mecânica do General Partido)
    cx, cy, r = 56.0, 27.5, 8.5
    a.prop("arena_vala", 61.5, 22.0, bloqueia=1.8, luz=[1, 0.3, 0.08, 9])
    for x, y in [(48.5, 20.5), (63.5, 20.5), (48.5, 35.5), (63.5, 35.5)]: a.prop("pilha_cranios", x, y, bloqueia=0.6)
    a.espalhar(["ossos_espalhados", "poca_sangue", "ossos_espalhados"], 16, (cx - 7, cy - 7, cx + 7, cy + 7))
    pilhas = [[round(cx + 6*math.cos(t), 1), round(cy + 6*math.sin(t), 1)] for t in [i*math.tau/6 + 0.4 for i in range(6)]]
    pilhas = [p for p in pilhas if a.livre(int(p[0]), int(p[1])) and (int(p[0]), int(p[1])) not in a.extra_blk]
    for ang in range(0, 360, 45):
        t = math.radians(ang); a.luzes.append([round(cx + 7.5*math.cos(t), 2), round(cy + 7.5*math.sin(t), 2), 1, 0.3, 0.12, 4])
    porta = porta_da_arena(a, cx, cy, r)
    a.prop("bau_chefe", 55.0, 13.5)
    a.objetos.append({"kind": "bau", "pos": [55.0, 13.5], "bau": "bau_de_ferro", "visual": "bau_chefe", "hist": "bau_ohya", "requer_chefe": "ohya_gigante", "id_mapa": "bau_ohya"})
    a.portal(57.5, 15.5, "salao_das_noivas", [12.5, 32.5], "Poço para o Salão das Noivas", requer_flag="venceu_ohya_gigante",
             texto_trancado="Ohya dorme sentado em cima do poço. Ainda está com fome.")
    a.luzes += [[56, 14, 0.9, 0.5, 0.25, 5]]
    a.paredes()
    return a.exportar(chefe={"id": "ohya_gigante", "pos": [cx + 1.5, cy - 2.5], "arena": {"centro": [cx, cy], "raio": r}, "porta": porta, "pilhas": pilhas},
                      ceu={"escuro": 0.86, "cor": [0.52, 0.44, 0.38], "neblina": [0.1, 0.07, 0.05]}, spawn=[12.5, 50.5])


def salao_das_noivas():
    a = Andar("salao_das_noivas", "Salão das Noivas", 72, 66, "o", "parede_gotica",
              {"id": "salao_das_noivas", "nome": "Salão das Noivas", "seguro": False, "nivel": [8, 10],
               "musica": "musica/cripta", "ambiente": "ambiente/cripta_ossario"})
    a.sala(8, 27, 17, 38, nome="Pé do poço")
    a.sala(18, 30, 50, 35, nome="Corredor dos Véus")
    a.corredor(25, 23, 28, 29)
    a.sala(20, 10, 36, 22, nome="Capela dos Casamentos")
    a.corredor(37, 14, 43, 17, piso="x")
    a.sala(44, 10, 57, 23, piso="x", nome="Cisterna do Dilúvio")
    a.corredor(24, 36, 27, 39)
    a.sala(18, 40, 36, 52, nome="Nichos das Noivas")
    a.corredor(37, 44, 43, 47, piso="x")
    a.corredor(47, 36, 50, 37, piso="x")
    a.sala(44, 38, 60, 53, piso="x", nome="Leito de Naamá")
    for (x, y) in [(44, 38), (45, 38), (44, 39), (60, 38), (59, 38), (60, 39), (44, 53), (45, 53), (44, 52), (60, 53), (59, 53), (60, 52)]:
        a.fechar(x, y)
    a.corredor(51, 54, 53, 56, piso="x")
    a.sala(48, 57, 57, 63, piso="x", nome="Antecâmara do Altar")
    a.portal(10.5, 30.5, "minas_dos_gigantes", [56.5, 18.5], "Subir para as Minas", visual="escada_subida")
    a.prop("candelabro_ossos", 15.5, 36.5, bloqueia=0.4, luz=VELA + [6]); a.prop("velas_chao", 9.5, 36.0, luz=VELA + [4])
    a.prop("asa_anjo_caida", 16.0, 28.5, bloqueia=0.5)
    a.espalhar(["penas_espalhadas"], 4, (8, 27, 17, 38))
    a.luzes += [[12, 32, 1, 0.75, 0.4, 5]]
    a.ao_longo("estante_ossos_a", 19.5, 35.5, 49.5, 35.5, 3.0)
    a.ao_longo("velas_chao", 20.5, 31.0, 48.5, 31.0, 7.0, luz=VELA + [4])
    a.espalhar(["penas_espalhadas", "folhas_papeis"], 7, (18, 30, 50, 35))
    a.spawn("brasa_de_azazel", 34, 33, 2, 1.0, 8); a.spawn("escriba_emparedado", 44, 32, 1, 0.5, 9)
    a.prop("anjo_porcelana_caido", 28.0, 11.5, bloqueia=0.8)
    a.prop("candelabro_ossos", 22.5, 12.5, bloqueia=0.4, luz=VELA + [7]); a.prop("candelabro_ossos", 34.5, 12.5, bloqueia=0.4, luz=VELA + [7])
    for x in (22.5, 25.5, 30.5, 33.5):
        for y in (16.5, 19.5): a.prop("banco_capela", x, y, bloqueia=0.5)
    a.ao_longo("velas_chao", 21.0, 21.5, 35.0, 21.5, 7.0, luz=VELA + [3])
    a.espalhar(["folhas_papeis", "penas_espalhadas"], 5, (20, 10, 36, 22))
    a.objetos.append({"kind": "bau", "pos": [35.0, 11.0], "bau": "caixote_podre", "visual": "bau_comum", "id_mapa": "capela_casamentos"})
    a.spawn("noiva_afogada", 28, 15, 2, 1.5, 9); a.spawn("brasa_de_azazel", 28, 20, 2, 1.0, 9)
    a.pisar(46, 12, 55, 21, "w")
    for x, y in [(47.5, 13.5), (53.5, 13.5), (47.5, 19.5), (53.5, 19.5)]: a.prop("sarcofago", x, y, bloqueia=0.8)
    a.espalhar(["poca_agua"], 8, (45, 11, 56, 22))
    a.luzes += [[50.5, 16.5] + FRIO + [6]]
    a.spawn("escriba_emparedado", 50, 16, 1, 0.5, 9); a.spawn("noiva_afogada", 52, 18, 1, 0.5, 9)
    nichos = [(20.0, 41.0), (24.0, 41.0), (28.0, 41.0), (32.0, 41.0), (21.0, 50.0), (26.0, 50.0), (31.0, 50.0)]
    for i, (x, y) in enumerate(nichos):
        a.prop("monge_emparedado", x + 0.5, y + 0.5, bloqueia=0.5)
        a.objetos.append({"kind": "interativo", "obj": "nicho_da_noiva", "pos": [x + 0.5, y + 1.5 if y < 45 else y - 0.5], "i": i})
    a.prop("sarcofago", 26.5, 46.0, bloqueia=0.8)
    a.objetos.append({"kind": "bau", "pos": [33.5, 46.0], "bau": "bau_de_ferro", "visual": "bau_raro", "hist": "bau_dote_naama", "id_mapa": "dote"})
    a.luzes += [[21, 46] + VELA + [5], [31, 46] + VELA + [5]]
    a.espalhar(["ossos_espalhados", "penas_espalhadas"], 5, (18, 43, 36, 48), chao=True)
    a.spawn("escriba_emparedado", 23, 46, 2, 1.5, 8); a.spawn("brasa_de_azazel", 30, 47, 2, 1.0, 8)
    cx, cy, r = 52.0, 45.5, 8.0
    a.prop("arena_carpideiras", 57.5, 40.5, bloqueia=1.5, luz=[0.8, 0.85, 1, 8])
    coristas = [[cx - 5.5, cy - 5.0], [cx + 5.0, cy - 5.0], [cx - 5.5, cy + 5.0], [cx + 5.0, cy + 5.0]]
    coristas = [[x, y] for x, y in coristas if a.livre(int(x), int(y))]
    a.espalhar(["penas_espalhadas", "poca_agua"], 8, (cx - 6, cy - 6, cx + 6, cy + 6))
    for ang in range(0, 360, 60):
        t = math.radians(ang); a.prop("velas_chao", round(cx + 7*math.cos(t), 2), round(cy + 7*math.sin(t), 2), luz=[0.8, 0.85, 1, 4])
    porta = porta_da_arena(a, cx, cy, r)
    a.prop("bau_chefe", 50.0, 59.5)
    a.objetos.append({"kind": "bau", "pos": [50.0, 59.5], "bau": "bau_de_ferro", "visual": "bau_chefe", "hist": "bau_naama", "requer_chefe": "naama_noiva", "id_mapa": "bau_naama"})
    a.prop("portao_ferro", 52.5, 62.5)
    a.objetos.append({"kind": "interativo", "obj": "porta_do_altar", "pos": [52.5, 61.0], "mapa": "altar_do_juramento", "chegada": [12.5, 34.5]})
    a.luzes += [[52, 60, 0.8, 0.85, 1, 5]]
    a.paredes()
    return a.exportar(chefe={"id": "naama_noiva", "pos": [cx + 3, cy - 3], "arena": {"centro": [cx, cy], "raio": r}, "porta": porta, "coristas": coristas},
                      ceu={"escuro": 0.9, "cor": [0.48, 0.52, 0.58], "neblina": [0.06, 0.07, 0.09]}, spawn=[12.5, 32.5])


def altar_do_juramento():
    a = Andar("altar_do_juramento", "Altar do Juramento", 70, 70, "j", "parede_trombeta",
              {"id": "altar_do_juramento", "nome": "Altar do Juramento", "seguro": False, "nivel": [10, 12],
               "musica": "musica/cripta", "ambiente": "ambiente/cripta_camara"})
    a.sala(8, 29, 17, 40, nome="Pé da escada")
    a.corredor(18, 32, 23, 37)
    a.sala(24, 24, 38, 45, nome="Nave dos Duzentos")
    a.corredor(29, 19, 32, 23)
    a.sala(23, 9, 38, 18, nome="Coro das Imprecações")
    a.corredor(29, 46, 32, 49)
    a.sala(25, 50, 36, 58, piso="x", nome="Arquivo de Penemue")
    a.corredor(39, 32, 41, 37)
    a.sala(42, 24, 62, 45, nome="Altar do Juramento")
    for (x, y) in [(42, 24), (43, 24), (42, 25), (62, 24), (61, 24), (62, 25), (42, 45), (43, 45), (42, 44), (62, 45), (61, 45), (62, 44)]:
        a.fechar(x, y)
    a.corredor(51, 46, 53, 47, piso="x")
    a.sala(48, 48, 56, 53, piso="x", nome="Relicário da Tábua")
    a.corredor(39, 12, 52, 15, piso="x"); a.sala(49, 16, 53, 23, piso="x", nome="Claustro das Correntes")
    a.portal(10.5, 32.5, "salao_das_noivas", [52.5, 59.5], "Voltar ao Salão das Noivas", visual="escada_subida")
    a.prop("braseiro_sagrado", 15.5, 38.5, bloqueia=0.4, luz=SANTO + [6])
    a.luzes += [[12, 34, 1, 0.9, 0.6, 5]]
    for y in (27.5, 33.0, 38.5, 43.0):
        for x in (26.5, 35.5): a.prop("pilar_porcelana", x, y, bloqueia=0.7)
    a.prop("asa_anjo_caida", 31.0, 29.5, bloqueia=0.6); a.prop("anjo_porcelana_caido", 30.5, 41.0, bloqueia=0.8)
    for y in (30.0, 36.0, 41.5): a.luzes.append([31, y] + SANTO + [5])
    a.espalhar(["folhas_papeis", "ossos_espalhados", "penas_espalhadas"], 8, (24, 24, 38, 45))
    a.spawn("vigilante_desfeito", 31, 34, 2, 1.5, 10); a.spawn("vigilante_desfeito", 30, 26, 1, 0.5, 11)
    a.prop("tubos_orgao", 30.5, 10.5, bloqueia=1.2, luz=SANTO + [6])
    a.prop("velas_chao", 25.0, 16.5, luz=SANTO + [4]); a.prop("velas_chao", 36.5, 16.5, luz=SANTO + [4])
    for x in (25.5, 28.5, 33.0, 36.0): a.prop("banco_capela", x, 13.5, bloqueia=0.5)
    a.espalhar(["folhas_papeis", "penas_espalhadas"], 5, (23, 9, 38, 18))
    a.spawn("eco_do_juramento", 30, 15, 2, 1.5, 11)
    a.ao_longo("velas_chao", 41.5, 13.5, 47.5, 13.5, 6.0, luz=SANTO + [3])
    a.prop("gaiola_suspensa", 51.0, 18.5); a.espalhar(["penas_espalhadas", "folhas_papeis"], 4, (39, 12, 53, 23))
    a.spawn("vigilante_desfeito", 46, 13.5, 1, 0.5, 11)
    a.prop("sarcofago", 27.5, 56.0, bloqueia=0.8); a.prop("estante_ossos_a", 33.5, 57.5); a.prop("folhas_papeis", 30.5, 54.0, chao=True)
    a.prop("candelabro_ossos", 34.5, 51.5, bloqueia=0.4, luz=SANTO + [5])
    a.objetos.append({"kind": "bau", "pos": [30.5, 56.5], "bau": "caixote_podre", "visual": "bau_comum", "id_mapa": "arquivo"})
    a.spawn("eco_do_juramento", 30, 53, 1, 0.5, 11)
    cx, cy, r = 52.0, 34.5, 10.0
    a.prop("arena_trombeta", 58.5, 29.5, bloqueia=1.8, luz=[0.85, 0.8, 1, 10])
    for x, y in [(cx - 4.5, cy - 4.5), (cx + 4.5, cy - 4.5), (cx - 4.5, cy + 4.5), (cx + 4.5, cy + 4.5)]: a.prop("pilar_porcelana", x, y, bloqueia=0.7)
    for ang in range(0, 360, 45):
        t = math.radians(ang); a.luzes.append([round(cx + 8.5*math.cos(t), 2), round(cy + 8.5*math.sin(t), 2), 0.85, 0.8, 1, 4])
    a.espalhar(["folhas_papeis", "ossos_espalhados", "penas_espalhadas"], 10, (cx - 8, cy - 8, cx + 8, cy + 8))
    porta = porta_da_arena(a, cx, cy, r)
    a.prop("bau_chefe", 50.0, 50.0)
    a.objetos.append({"kind": "bau", "pos": [50.0, 50.0], "bau": "bau_de_ferro", "visual": "bau_chefe", "hist": "bau_semyaza", "requer_chefe": "semyaza_juramento", "id_mapa": "bau_semyaza"})
    a.objetos.append({"kind": "bau", "pos": [54.0, 50.0], "bau": "relicario_da_trombeta", "visual": "bau_chefe", "requer_chefe": "semyaza_juramento", "id_mapa": "relicario_tabua"})
    a.portal(52.5, 51.5, "jerusalem_hermon", CHEGADA_HADES, "Subir às Fontes do Jordão", visual="escada_subida", requer_flag="venceu_semyaza_juramento",
             texto_trancado="A escada sobe para a neve, mas Semyaza ainda segura o juramento.")
    a.luzes += [[52, 50, 0.9, 0.9, 1, 5]]
    a.paredes()
    return a.exportar(chefe={"id": "semyaza_juramento", "pos": [cx + 3, cy - 3], "arena": {"centro": [cx, cy], "raio": r}, "porta": porta,
                             "trombeta": [cx + 5.5, cy - 5.0]},
                      ceu={"escuro": 0.84, "cor": [0.62, 0.6, 0.72], "neblina": [0.09, 0.09, 0.12]}, spawn=[12.5, 34.5])


# ===================================================================================== dados (mobs, sprites, chefes, drops)
def dados():
    v06 = json.load(open(os.path.join(RAIZ, "game", "data", "v06_extra.json")))["mobs"]
    base_mobs = json.load(open(os.path.join(RAIZ, "design", "combate", "mobs.json")))["arquetipos"]
    chefes_cripta = json.load(open(os.path.join(RAIZ, "design", "combate", "chefes.json")))["chefes"]
    mobs, sprites = {}, {}
    for mid, d in MOBS.items():
        esp = d["espelho"]
        niv = (v06.get(esp) or {}).get("niveis") or (base_mobs.get(esp) or {}).get("niveis") or [1, 1]
        mobs[mid] = {"nome": d["nome"], "base": esp, "niveis": niv, "ajuste": {}, "tags": d["tags"], "drop": DROP_MOB.get(mid, "inicial_humanoide"),
                     "renascimento_s": (v06.get(esp) or {}).get("renascimento_s", 14), "espelho_de": esp}
        if (v06.get(esp) or {}).get("arquetipo") in ("elite", "raro"): mobs[mid]["arquetipo"] = v06[esp]["arquetipo"]
        sprites[mid] = {"usa": esp, "escala": d["escala"], "tint": d["tint"]}
    # ---- chefes: cópia dos números da Cripta (hp, defesa, dano, fases, recargas); muda nome, história, falas e nome dos golpes
    REN = {
        "general_partido": ("ohya_gigante", "Ohya, o Gigante que Sonhou", "drop_ohya",
            "Filho de Semyaza com uma filha dos homens. Sonhou com o dilúvio antes de todos (Livro dos Gigantes) e se escondeu no fundo do Hermon para não morrer afogado. Sobreviveu comendo os escravos que cavavam para ele. Quando o Juízo começou, acordou com fome de novo.",
            "Os escravos acabaram. Mas você veio. O sonho dizia que viria alguém pequeno e quente.",
            "Ohya come as 6 Pilhas de Escravos Mortos para se curar (mesma mecânica do General Partido).",
            {"estandarte": "Clava de Cedro", "golpe_de_estandarte": "Varrida de Cedro", "arrasto": "Pisão do Gigante", "devorar": "Comer os Escravos",
             "ordem_de_levantar": "De Pé, Escravos!", "vomito_de_brasa": "Vômito de Brasa"}),
        "irma_celeste": ("naama_noiva", "Naamá, a Noiva dos Vigilantes", "drop_naama",
            "A filha dos homens que deu filhos gigantes a um Vigilante e viu o dilúvio levar todos. Ainda veste o véu. As noivas de pedra do salão são as outras esposas dos duzentos; ela as faz cantar o nome dos filhos.",
            "Shhh. Elas vão cantar o nome dos meus meninos. Você vai ouvir todos.",
            "As 4 Noivas de Pedra cantam como as Coristas de Osso (mesma mecânica da Irmã Celeste).",
            {"toque_de_luto": "Toque do Véu", "lamento": "Lamento das Águas", "pranto_que_cai": "Chuva do Dilúvio", "regencia": "O Nome dos Filhos",
             "onda_do_coro": "Onda do Dilúvio", "chamar_carpideiras": "Chamar as Noivas Afogadas", "escuridao": "Águas Escuras"}),
        "zacarias_arauto": ("semyaza_juramento", "Semyaza, o Primeiro Juramento", "drop_semyaza",
            "O chefe dos duzentos Vigilantes que desceram no Hermon e juraram com imprecações (Enoque 6). Preso no fundo da terra até o Dia do Juízo, quando será lançado no fogo. O Juízo começou e travou: as correntes afrouxaram, o fogo não veio. Agora ele jura de novo, e o novo juramento é um só: que o fim nunca termine.",
            "Duzentos juraram comigo. Você ouve? Eles juram de novo. Que o fim fique onde está. Para sempre.",
            "Semyaza canaliza O Juramento no Altar (mesma mecânica da Primeira Nota de Zacarias); os pilares dão cobertura.",
            {"espada_sagrada": "Espada do Vigilante", "lanca_do_juizo": "Lança do Juramento", "asas_cortantes": "Asas Acorrentadas",
             "marca_do_juizo": "Marca da Imprecação", "primeira_nota": "O Juramento", "chamar_ecos": "Chamar os Duzentos",
             "arena_encolhe": "As Correntes Fecham", "chamar_querubim": "Chamar um Vigilante Desfeito", "nota_final": "O Último Juramento"}),
    }
    INVOCA = {"soldado_caido": "soldado_de_pedra", "carpideira_de_ossos": "noiva_afogada", "eco_da_trombeta": "eco_do_juramento",
              "querubim_desfeito": "vigilante_desfeito"}
    chefes = {}
    for orig, (nid, nome, drop, conceito, fala, mec, golpes) in REN.items():
        c = json.loads(json.dumps(chefes_cripta[orig]))
        for k in ("conceito_jefin", "visual", "arena"): c.pop(k, None)
        c.update({"nome": nome, "conceito": conceito, "fala_entrada": fala, "mecanica_de": orig, "nota_mecanica": mec, "dungeon": "fosso_dos_vigilantes",
                  "drop": drop, "espelho_de": orig})
        for f in c.get("fases", []):
            f.pop("fala", None)
            for at in f.get("ataques", []):
                if at.get("id") in golpes: at["nome"] = golpes[at["id"]]
                if "invoca" in at: at["invoca"] = {INVOCA.get(k, k): v for k, v in at["invoca"].items()}
        chefes[nid] = c
    chefes["ohya_gigante"]["fases"][1]["fala"] = "DE PÉ, ESCRAVOS! O gigante tem fome!"
    chefes["naama_noiva"]["fases"][1]["fala"] = "Cantem! Cantem o nome deles!"
    chefes["naama_noiva"]["fases"][2]["fala"] = "Então afogue sozinho... no escuro."
    chefes["semyaza_juramento"]["fases"][1]["fala"] = "Duzentos! Jurem comigo! Que nunca termine!"
    chefes["semyaza_juramento"]["fases"][2]["fala"] = "Se o fim não vem para mim... eu sou a corrente."
    drops = {"drop_ohya": "chefe_general", "drop_naama": "chefe_celeste", "drop_semyaza": "chefe_zacarias"}
    nomes_hud = {"jerusalem_hermon": "Jerusalém e Monte Hermon (nv 1-12)", "minas_dos_gigantes": "Fosso dos Vigilantes · Minas dos Gigantes (chefe nv 8)",
                 "salao_das_noivas": "Fosso dos Vigilantes · Salão das Noivas (chefe nv 10)", "altar_do_juramento": "Fosso dos Vigilantes · Altar do Juramento (chefe nv 12)"}
    out = {"_doc": "Jerusalém e Monte Hermon (Arautos), pedido do Jefin 16/10/2026. mobs: formato de game/data/v06_extra.json (base = o mob do deserto que este espelha, sem ajuste). sprites: formato de game/data/sprites_substitutos.json (recolor estilo MU até a arte própria). chefes: formato de design/combate/chefes.json, cópia dos números da Cripta; `mecanica_de` diz qual controle de chefe usar. drops: cada tabela nova aponta para a tabela do chefe espelhado em design/combate/drops.json. Gerado por gerar.py.",
           "mobs": mobs, "sprites": sprites, "chefes": chefes, "drops_alias": drops, "nomes_mapa_hud": nomes_hud,
           "ligacao": {"_doc": "Arautos nascem em Jerusalém (spawn_por_faccao do mapa). Saída para o deserto e para o Novo Éden pela Estrada dos Peregrinos.",
                       "deserto": {"kind": "portal", "pos": [101.5, 32.0], "para": "area_inicial", "chegada": [44.0, 109.5],
                                   "nome": "Estrada do Sul · para o Deserto de Absinto (Capela de São Lázaro)", "visual": "escada_subida", "nivel_minimo": 12},
                       "deserto_volta": {"_doc": "acrescentar em area_inicial.json, perto da Capela de São Lázaro", "kind": "portal", "pos": [38.5, 116.0],
                                         "para": "jerusalem_hermon", "chegada": [101.5, 34.5], "nome": "Estrada dos Peregrinos · para Jerusalém", "visual": "escada_subida"}}}
    json.dump(out, open(f"{AQUI}/dados.json", "w"), ensure_ascii=False, indent=1)
    return out


DESERTO = {"covas_rasas": [77.0, 65.0], "telhados_dos_corvos": [29.0, 94.0], "fosso_dos_caes": [87.0, 32.0], "procissao_parada": [84.0, 115.0],
           "chiqueiro_do_carnica": [124.0, 78.0], "margem_das_viuvas": [114.0, 103.0], "acampamento_desertores": [98.0, 56.0],
           "marco_do_corte": [62.0, 82.0], "patio_do_abatedouro": [122.0, 44.0], "beira_da_tempestade": [109.0, 126.0]}


def espelho_txt(m):
    """Tabela para conferir o espelho: nível, mobs, temperamento e distância da base, lado a lado."""
    des = json.load(open(os.path.join(RAIZ, "game", "data", "mapas", "area_inicial.json")))
    sp_d = {s["id"]: s for s in json.load(open(os.path.join(RAIZ, "design", "mapas", "spots.json")))["spots"]}
    L = ["ESPELHO VIGÍLIA x ARAUTOS (gerado por gerar.py)", "", "spot do deserto (nível, mobs, dist. da Vela) -> spot daqui (nível, mobs, dist. de Jerusalém)", ""]
    vela, jer = [44.5, 44.0], SPAWN
    for s in m["spots"]:
        d = sp_d[s["espelho"]]
        agd = {}
        for g in des["spawns"]:
            if g.get("spot") == s["espelho"]: agd[(g["mob"], g.get("temperamento"))] = agd.get((g["mob"], g.get("temperamento")), 0) + g["qtd"]
        md = " + ".join(f"{q} {k} ({t})" for (k, t), q in agd.items())
        gs = [g for g in m["spawns"] if g.get("spot") == s["id"]]
        agg = {}
        for g in gs: agg[(g["mob"], g["temperamento"])] = agg.get((g["mob"], g["temperamento"]), 0) + g["qtd"]
        mh = " + ".join(f"{q} {k} ({t})" for (k, t), q in agg.items())
        L.append(f"{d['nome']:<24} {str(d['nivel']):<8} {md}  [{math.dist(vela, [d['x'], d['y']]):.0f} m]")
        L.append(f"  -> {s['nome']:<21} {str(s['nivel']):<8} {mh}  [{math.dist(jer, s['pos']):.0f} m]  respawn {s['respawn_s']} s")
    tot_d = sum(g["qtd"] for g in des["spawns"]); tot_h = sum(g["qtd"] for g in m["spawns"] if g["mob"] != "filho_do_hissopo")
    L += ["", f"mobs no mundo: deserto {tot_d} (em spots {sum(g['qtd'] for g in des['spawns'] if g.get('spot'))}) | aqui {tot_h} "
               f"(em spots {sum(g['qtd'] for g in m['spawns'] if g.get('spot'))})",
          f"baús no mundo: deserto {sum(1 for o in des['objetos'] if o['kind'] == 'bau')} | aqui {sum(1 for o in m['objetos'] if o['kind'] == 'bau')} "
          f"(+3 esconderijos do Bartimeu, interativos)",
          f"descansos: deserto 6 | aqui {len(m['descanso'])}", "",
          "dungeon: Cripta da Trombeta Calada -> Fosso dos Vigilantes (mesmos andares, grupos, níveis e números de chefe)",
          "  Porão do Matadouro (6-8, 9 grupos/14 mobs, Andras nv 8)   -> Minas dos Gigantes (6-8, 9/14, Ohya nv 8)",
          "  Ossário das Carpideiras (8-10, 8/13, Irmã Celeste nv 10) -> Salão das Noivas (8-10, 8/13, Naamá nv 10)",
          "  Câmara da Trombeta (10-12, 5/7, Zacarias nv 12)          -> Altar do Juramento (10-12, 5/7, Semyaza nv 12)"]
    open(f"{AQUI}/espelho.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    m = mapa()
    G.AQUI = os.path.join(RAIZ, "design", "mapas", "cripta")      # a planta acha as fontes IM Fell por aqui
    G.planta(m, f"{AQUI}/planta_jerusalem_hermon.png", "Jerusalém e Monte Hermon · área inicial dos Arautos (nv 1-12)")
    for fn, tit in [(minas_dos_gigantes, "Fosso dos Vigilantes · 1 · Minas dos Gigantes"), (salao_das_noivas, "Fosso dos Vigilantes · 2 · Salão das Noivas"),
                    (altar_do_juramento, "Fosso dos Vigilantes · 3 · Altar do Juramento")]:
        G.AQUI = AQUI; d = fn(); G.AQUI = os.path.join(RAIZ, "design", "mapas", "cripta"); G.planta(d, f"{AQUI}/planta_{d['id']}.png", tit)
    dados()
    espelho_txt(m)
