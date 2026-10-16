"""Egito, a Terra Negra (nível 50 a 70) · pedido do Jefin, 16/10/2026. Conceito: conceito.md desta pasta.

Gera no MESMO formato de game/data/mapas/*.json (classe Andar de design/mapas/cripta/gerar.py):
  egito.json                      o mapa aberto (200x200): Mênfis Reerguida, o Nilo, Gizé, o Faium, o Vale dos Reis
  hawara_1..3.json                O Labirinto de Hawara (dungeon nível 50 a 54, 3 chefes)
  coracao_1..6.json               O Coração Endurecido (raid nível 60, 6 chefes, um salão por chefe)
  planta_*.png                    plantas de conferência
Saída em entregas/egito/mapas/. Uso: python3 gerar.py [egito|hawara|raid]

Regras do projeto seguidas: spots estilo MU (12 mobs, 14 s), fogueira com a aguadeira Nefer perto de cada par,
"menos Diablo, mais WoW" (neutros; agressivos só nas tumbas), cada grupo com motivo, bordas disfarçadas (Mar de
Areia, penhascos, catarata, delta), praça do Primarca na cidade principal.
Tela: +X desce para a direita, +Y sobe para a direita; "frente" (perto da câmera) = +x -y.
"""
import json, math, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
SAIDA = os.path.join(RAIZ, "entregas", "egito", "mapas")
os.makedirs(SAIDA, exist_ok=True)
sys.path.insert(0, os.path.join(RAIZ, "design", "mapas", "cripta"))
import gerar as G          # noqa: E402  (Andar, porta_da_arena, planta)
G.AQUI = SAIDA
Andar, porta_da_arena = G.Andar, G.porta_da_arena
sys.path.insert(0, AQUI)
from dados_egito import MOBS  # noqa: E402

FOGO = [1, 0.5, 0.2]; OLEO = [1, 0.72, 0.38]; TURQ = [0.25, 0.85, 0.85]; SOL = [1, 0.62, 0.32]; LUA = [0.55, 0.62, 0.8]
ROXO = [0.62, 0.4, 1]
PISOS = {"a": "areia_calcario", "l": "lodo_negro", "j": "laje_tura", "h": "campo_cheia", "m": "margem_nilo",
         "e": "areia_escavacao", "w": "lodo_negro", "r": "margem_nilo", "k": "cascalho", "g": "granito_catarata",
         "u": "areia_calcario", "x": "laje_hawara", "o": "laje_duat", "n": "entulho"}
G.PISOS.update(PISOS)
G.COR_PISO.update({"a": (176, 156, 120), "l": (52, 46, 40), "j": (150, 138, 112), "h": (88, 96, 58), "m": (84, 84, 66),
                   "e": (150, 126, 92), "w": (40, 58, 56), "r": (70, 92, 84), "k": (100, 96, 90), "g": (120, 92, 86),
                   "u": (190, 170, 130), "x": (110, 98, 80), "o": (40, 44, 52), "n": (96, 86, 72)})


def ruido(x, y, s=0.0):
    return .5*math.sin(x*.37 + y*.21 + s) + .3*math.sin(x*.13 - y*.29 + 1.7 + s) + .2*math.sin(x*.71 + y*.53 + 2.9*s)


def dist_seg(px, py, a, b):
    ax, ay = a; bx, by = b; dx, dy = bx - ax, by - ay
    t = max(0, min(1, ((px - ax)*dx + (py - ay)*dy)/(dx*dx + dy*dy)))
    return math.hypot(px - ax - t*dx, py - ay - t*dy)


def dist_poli(px, py, pts):
    return min(dist_seg(px, py, pts[i], pts[i + 1]) for i in range(len(pts) - 1))


# ===================================================================================== zonas
ZONAS = [  # id, nome, seguro, nível, piso, neblina, música, ambiente
    ("menfis", "Mênfis Reerguida", True, None, "j", .14, "musica/egito_menfis", "ambiente/egito_cidade"),
    ("escavacao", "Acampamento da Escavação", True, None, "e", .2, "musica/egito_menfis", "ambiente/egito_escavacao"),
    ("margem_papiro", "Margem do Papiro", False, [50, 52], "m", .3, "musica/egito_nilo", "ambiente/egito_nilo"),
    ("campos_cheia", "Campos da Cheia", False, [51, 53], "h", .28, "musica/egito_nilo", "ambiente/egito_campos"),
    ("vila_artesaos", "Vila dos Artesãos", False, [52, 55], "a", .3, "musica/egito_nilo", "ambiente/egito_vento"),
    ("avenida_esfinges", "Avenida das Esfinges", False, [53, 56], "j", .3, "musica/egito_templo", "ambiente/egito_vento"),
    ("sacara", "Mastabas de Sacará", False, [55, 58], "a", .34, "musica/egito_templo", "ambiente/egito_vento"),
    ("karnak", "Ipet-Isut, o Templo de Amon", False, [56, 59], "j", .3, "musica/egito_templo", "ambiente/egito_templo"),
    ("lago_sagrado", "Lago Sagrado", False, [57, 60], "j", .32, "musica/egito_templo", "ambiente/egito_nilo"),
    ("gize", "Planalto de Gizé", False, [58, 63], "a", .32, "musica/egito_gize", "ambiente/egito_vento"),
    ("casa_vida", "Casa da Vida", False, [59, 62], "a", .36, "musica/egito_templo", "ambiente/egito_templo"),
    ("faium", "Oásis do Faium", False, [61, 65], "m", .3, "musica/egito_nilo", "ambiente/egito_oasis"),
    ("mar_areia", "Mar de Areia", False, [63, 66], "u", .7, None, "ambiente/egito_tempestade"),
    ("hatshepsut", "Terraços de Djeser-Djeseru", False, [64, 67], "a", .4, "musica/egito_gize", "ambiente/egito_vento"),
    ("catarata", "Primeira Catarata", False, [66, 69], "k", .36, "musica/egito_nilo", "ambiente/egito_catarata"),
    ("vale_reis", "Vale dos Reis", False, [67, 70], "a", .5, "musica/egito_vale", "ambiente/egito_vale"),
    ("necropole", "Necrópole Proibida", False, [68, 70], "a", .6, "musica/egito_vale", "ambiente/egito_vale"),
]
ZI = {z[0]: i for i, z in enumerate(ZONAS)}
LETRAS = "ABCDEFGHIJKLMNOPQ"

W = H = 200
# O Nilo corre de sul (y pequeno) para norte (y grande); oeste (x pequeno) = terra dos mortos.
NILO = [(118, -4), (116, 14), (112, 30), (106, 46), (104, 62), (108, 80), (111, 98), (108, 116), (102, 134), (99, 152),
        (101, 170), (106, 188), (108, 204)]
LAGO_MERIS = [(22, 50), (30, 46), (40, 48), (44, 54), (38, 60), (28, 60), (20, 56)]       # o lago do Faium (polígono)
LAGO_SAGRADO = (166, 44, 6.0, 4.0)                                                         # retângulo de pedra (cx, cy, meia-larg, meia-alt)

# ---- blobs: chave -> (x, y, raio, zona, spot | None).
# spot = (id, nome, [nível], [(mob, qtd por grupo, nº de grupos, temperamento)])  -> 12 mobs, 14 s
B = {
    # margem leste (vivos)
    "MEN":   (138, 100, 16, "menfis", None),
    "PAP":   (124, 138, 10, "margem_papiro", ("juncal_do_papiro", "Juncal do Papiro", [50, 52],
              [("crocodilo_do_nilo", 2, 4, "neutro"), ("ibis_de_thoth", 2, 2, "neutro")])),
    "PAP2":  (128, 156, 8, "margem_papiro", None),
    "CAM":   (154, 136, 11, "campos_cheia", ("campos_da_cheia", "Campos da Cheia", [51, 53],
              [("escaravelho_sagrado", 2, 5, "neutro"), ("escaravelho_carniceiro", 2, 1, "neutro")])),
    "CAM2":  (164, 158, 9, "campos_cheia", None),
    "AVE":   (162, 82, 10, "avenida_esfinges", ("avenida_das_esfinges", "Avenida das Esfinges", [53, 56],
              [("esfinge_carneiro", 2, 4, "territorial"), ("escaravelho_sagrado", 2, 2, "neutro")])),
    "KAR":   (178, 58, 13, "karnak", ("salao_hipostilo", "Salão Hipostilo", [56, 59],
              [("anubis_sentinela", 2, 3, "territorial"), ("sacerdote_mumia", 2, 3, "neutro")])),
    "LAG":   (158, 40, 9, "lago_sagrado", ("lago_sagrado", "Margens do Lago Sagrado", [57, 60],
              [("sobekita", 2, 4, "territorial"), ("naja", 2, 2, "neutro")])),
    "SUL":   (150, 22, 9, "catarata", None),
    "CAT":   (132, 16, 10, "catarata", ("primeira_catarata", "Pedreira da Catarata", [66, 69],
              [("crocodilo_gigante", 2, 3, "territorial"), ("naja", 2, 2, "neutro"), ("cria_de_apofis", 1, 2, "territorial")])),
    # margem oeste (mortos)
    "ESC":   (82, 116, 8, "escavacao", None),
    "VIL":   (84, 90, 10, "vila_artesaos", ("vila_dos_artesaos", "Vila dos Artesãos", [52, 55],
              [("mumia_operaria", 2, 6, "neutro")])),
    "SAQ":   (60, 98, 10, "sacara", ("mastabas_de_sacara", "Mastabas de Sacará", [55, 58],
              [("mumia_operaria", 2, 3, "neutro"), ("escaravelho_carniceiro", 2, 3, "neutro")])),
    "SAQ2":  (46, 82, 8, "sacara", None),
    "GIZ":   (78, 152, 9, "gize", ("escavacao_de_queops", "Escavação de Quéops", [58, 61],
              [("escorpiao_de_serket", 2, 5, "territorial"), ("escaravelho_rei", 1, 2, "neutro")])),
    "QUE":   (58, 128, 8, "gize", ("calcada_de_quefren", "Calçada de Quéfren", [60, 63],
              [("guardiao_mumia", 3, 2, "agressivo"), ("mumia_operaria", 3, 2, "agressivo")])),
    "GIZ2":  (40, 150, 9, "gize", None),
    "VID":   (78, 66, 9, "casa_vida", ("casa_da_vida", "Casa da Vida", [59, 62],
              [("sacerdote_mumia", 2, 4, "neutro"), ("guardiao_falcao", 2, 2, "territorial")])),
    "FAI":   (52, 58, 9, "faium", ("crocodilopolis", "Crocodilópolis", [61, 64],
              [("sobekita", 2, 3, "territorial"), ("crocodilo_do_nilo", 2, 3, "neutro")])),
    "FAI2":  (34, 34, 9, "faium", ("lago_meris", "Margem do Lago Méris", [62, 65],
              [("naja", 2, 3, "neutro"), ("crocodilo_gigante", 2, 3, "territorial")])),
    "HAW":   (60, 34, 7, "faium", None),
    "MAR":   (20, 96, 10, "mar_areia", ("mar_de_areia", "Mar de Areia", [63, 66],
              [("escorpiao_negro", 2, 3, "territorial"), ("cria_de_apofis", 2, 3, "territorial")])),
    "MAR2":  (22, 122, 8, "mar_areia", None),
    "HAT":   (52, 174, 10, "hatshepsut", ("terracos_de_hatshepsut", "Terraços de Djeser-Djeseru", [64, 67],
              [("guardiao_falcao", 2, 4, "territorial"), ("anubis_sentinela", 2, 2, "territorial")])),
    "VAL":   (24, 172, 10, "vale_reis", ("vale_dos_reis", "Vale dos Reis", [67, 70],
              [("anubis_guardiao", 3, 2, "agressivo"), ("anubis_sentinela", 3, 2, "agressivo")])),
    "NEC":   (28, 146, 8, "necropole", ("necropole_proibida", "Necrópole Proibida", [68, 70],
              [("guardiao_mumia", 3, 2, "agressivo"), ("sacerdote_mumia", 3, 2, "agressivo")])),
    "VAL2":  (14, 188, 6, "vale_reis", None),
}
ARESTAS = [("MEN", "PAP"), ("PAP", "PAP2"), ("MEN", "CAM"), ("CAM", "CAM2"), ("PAP2", "CAM2"), ("MEN", "AVE"), ("AVE", "KAR"),
           ("KAR", "LAG"), ("LAG", "SUL"), ("MEN", "LAG"), ("SUL", "CAT"),
           ("ESC", "VIL"), ("VIL", "SAQ"), ("SAQ", "SAQ2"), ("ESC", "QUE"), ("ESC", "GIZ"), ("QUE", "GIZ2"), ("GIZ", "GIZ2"),
           ("VIL", "VID"), ("SAQ2", "VID"), ("VID", "FAI"), ("FAI", "HAW"), ("FAI", "FAI2"), ("SAQ2", "MAR"), ("MAR", "MAR2"),
           ("MAR2", "NEC"), ("GIZ2", "NEC"), ("GIZ2", "HAT"), ("HAT", "VAL"), ("NEC", "VAL"), ("VAL", "VAL2"), ("SAQ", "QUE")]
# travessias do Nilo: (ponto oeste, ponto leste, tipo)
TRAVESSIAS = [((92, 104), (124, 100), "ponte_barcas"),            # Ponte de Barcas: Mênfis -> Escavação
              ((90, 146), (118, 144), "dique"),                   # Dique Velho: Gizé -> Margem do Papiro
              ((100, 22), (126, 18), "vau")]                      # o vau de granito da Primeira Catarata
ESTRADA = [("MEN", "AVE"), ("AVE", "KAR"), ("ESC", "QUE"), ("ESC", "VIL"), ("VIL", "VID")]   # calçadas de laje

CID = (124, 88, 152, 112)            # Mênfis: x0, y0, x1, y1
SPAWN = [140.5, 99.5]
ACAMP = (74, 108, 90, 122)           # Acampamento da Escavação (zona segura)
PORTA_HAWARA = [60.5, 31.0]          # na base da pirâmide de tijolo de Amenemés III
PORTA_RAID = [12.5, 192.0]           # a tumba sem cartucho, no fundo do Vale dos Reis
ESTACAO = [151.5, 106.5]             # estação da Linha 7 (bonde-veleiro)


def mapa():
    a = Andar("egito", "Egito, a Terra Negra", W, H, "a", None, {})
    zona_de = [[None]*W for _ in range(H)]
    trilha = [[False]*W for _ in range(H)]
    estrada = [[False]*W for _ in range(H)]
    blobs = list(B.items())
    segs = [(B[i][:2], B[j][:2], (i, j) in ESTRADA or (j, i) in ESTRADA) for i, j in ARESTAS]
    segs += [(p0, p1, False) for p0, p1, _ in TRAVESSIAS]
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
            na_cidade = x0c - 2 <= x <= x1c + 2 and y0c - 2 <= y <= y1c + 2
            no_acamp = ACAMP[0] - 1 <= x <= ACAMP[2] + 1 and ACAMP[1] - 1 <= y <= ACAMP[3] + 1
            if best < 1 or dc < 2.8 + .9*ruido(x, y, 3.1) or na_cidade or no_acamp:
                a.blk[y][x] = False
                zz = bz
                if x0c <= x <= x1c and y0c <= y <= y1c: zz = "menfis"
                elif ACAMP[0] <= x <= ACAMP[2] and ACAMP[1] <= y <= ACAMP[3]: zz = "escavacao"
                zona_de[y][x] = zz
                a.ter[y][x] = ZONAS[ZI[zz]][4]
                if de < 1.3 and best > .35: a.ter[y][x] = "j"; trilha[y][x] = estrada[y][x] = True
                elif dc < 1.0 and best > .55: a.ter[y][x] = "l" if x > 100 else "e"; trilha[y][x] = True
    # ---- o Nilo e as margens de lodo (a Terra Negra), antes das manchas de piso
    nilo_d = [[99.0]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            nilo_d[y][x] = dist_poli(x + .5, y + .5, NILO)
    trav_cel = set()
    for p0, p1, tipo in TRAVESSIAS:
        for y in range(H):
            for x in range(W):
                if dist_seg(x + .5, y + .5, p0, p1) < (1.6 if tipo != "vau" else 2.0): trav_cel.add((x, y))
    fundo, raso = set(), set()
    for y in range(H):
        for x in range(W):
            d = nilo_d[y][x]
            larg = 6.5 + 1.6*ruido(x*.4, y*.4, 5)
            if y < 34: larg -= 1.2                                   # estreita na catarata
            if d < larg/2:
                a.blk[y][x] = False
                zona_de[y][x] = zona_de[y][x] or ("margem_papiro" if y > 120 else ("catarata" if y < 40 else "menfis"))
                if (x, y) in trav_cel: raso.add((x, y)); trilha[y][x] = True
                elif d < larg/2 - 1.1: fundo.add((x, y))
                else: raso.add((x, y))
            elif d < larg/2 + 3.2 and not a.blk[y][x] and not estrada[y][x]:
                a.ter[y][x] = "m" if d < larg/2 + 1.6 else "l"      # margem úmida e a faixa de lodo preto
    for (x, y) in raso: a.ter[y][x] = "r"
    for (x, y) in fundo: a.ter[y][x] = "w"; a.blk[y][x] = True
    for (x, y) in raso:
        if (x, y) not in trav_cel: a.extra_blk.add((x, y))
    # ---- o lago Méris (Faium) e o Lago Sagrado de Karnak
    for y in range(H):
        for x in range(W):
            px, py = x + .5, y + .5
            ins = _dentro(px, py, LAGO_MERIS)
            dd = dist_poli(px, py, LAGO_MERIS + [LAGO_MERIS[0]])
            if ins and dd > 1.6: a.ter[y][x] = "w"; a.blk[y][x] = True
            elif ins or dd < 1.0:
                if not a.blk[y][x] or ins: a.blk[y][x] = False; a.ter[y][x] = "r"; a.extra_blk.add((x, y)); zona_de[y][x] = zona_de[y][x] or "faium"
            elif dd < 3.0 and not a.blk[y][x] and not trilha[y][x]: a.ter[y][x] = "m"
    cxl, cyl, hw, hh = LAGO_SAGRADO
    for y in range(int(cyl - hh - 2), int(cyl + hh + 3)):
        for x in range(int(cxl - hw - 2), int(cxl + hw + 3)):
            a.blk[y][x] = False; zona_de[y][x] = "lago_sagrado"
            if abs(x + .5 - cxl) < hw and abs(y + .5 - cyl) < hh: a.ter[y][x] = "w"; a.blk[y][x] = True
            else: a.ter[y][x] = "j"
    # ---- variação de piso por zona (um chão por área, manchas do mesmo vocabulário)
    for y in range(H):
        for x in range(W):
            if a.blk[y][x] or trilha[y][x] or a.ter[y][x] in "wrml": continue
            z = zona_de[y][x]; n1 = ruido(x*1.6, y*1.6, 2); n2 = ruido(x*2.3, y*2.3, 7)
            if z == "menfis":
                if (x - x0c) % 7 in (3,) or (y - y0c) % 7 in (3,): a.ter[y][x] = "j"
                elif n1 > .2: a.ter[y][x] = "l"
                else: a.ter[y][x] = "a"
            elif z == "escavacao": a.ter[y][x] = "e" if n1 > -.3 else "a"
            elif z == "campos_cheia": a.ter[y][x] = "h" if n2 > -.35 else "l"
            elif z == "margem_papiro": a.ter[y][x] = "m" if n1 > -.1 else "l"
            elif z in ("avenida_esfinges", "karnak", "lago_sagrado"): a.ter[y][x] = "j" if n1 > -.15 else "a"
            elif z == "gize": a.ter[y][x] = "e" if n2 > .35 else "a"
            elif z == "sacara" and n1 > .4: a.ter[y][x] = "e"
            elif z == "vila_artesaos" and n1 > .3: a.ter[y][x] = "j"
            elif z == "casa_vida" and n1 > .1: a.ter[y][x] = "j"
            elif z == "faium": a.ter[y][x] = "m" if n2 > .1 else ("h" if n1 > .3 else "a")
            elif z == "mar_areia": a.ter[y][x] = "u"
            elif z == "catarata": a.ter[y][x] = "g" if n1 > .1 else "k"
            elif z in ("vale_reis", "necropole") and n2 > .4: a.ter[y][x] = "k"
            elif z == "hatshepsut" and n1 > .2: a.ter[y][x] = "j"

    rng = a.rng
    spots, descanso, lugares, npcs = [], [], [], []
    area_spot = [(bx, by, r*.82) for k, (bx, by, r, z, sp) in blobs if sp]
    def em_spot(x, y, folga=0): return any(math.hypot(x - sx, y - sy) < sr + folga for sx, sy, sr in area_spot)
    def agua(x, y): return 0 <= x < W and 0 <= y < H and a.ter[y][x] in "rw"
    def livre3(x, y): return all(a.livre(x + dx, y + dy) and not agua(x + dx, y + dy) and (x + dx, y + dy) not in a.extra_blk
                                 for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    def perto_prop(x, y, d): return any(math.dist((x, y), (p["x"], p["y"])) < d for p in a.props if not p.get("chao"))
    def predio(k, x, y, fp, luz=None, **kw):
        """Prédio com pegada (fp em tiles, centrada na posição)."""
        a.prop(k, x, y, luz=luz, **kw)
        for yy in range(int(y - fp[1]/2 + .5), int(y - fp[1]/2 + .5) + fp[1]):
            for xx in range(int(x - fp[0]/2 + .5), int(x - fp[0]/2 + .5) + fp[0]): a.extra_blk.add((xx, yy))
    def lugar(id_, nome, pos): lugares.append({"id": id_, "nome": nome, "pos": [round(pos[0], 1), round(pos[1], 1)]})

    # ================================================================ Mênfis Reerguida (cidade-base, zona segura)
    # "A rua de hoje é o terraço de ontem": casas novas de tijolo de lama sobre o térreo de pedra desenterrado.
    # Quarteirões 7x7 entre as ruas de laje; casas soterradas nas bordas (onde a areia ainda não desceu).
    reservado = []                   # retângulos livres (praças)
    PRACA = (134, 95, 144, 105)      # praça central: Primarca, mercado, a Esfinge de Alabastro de Mênfis
    DOCAS = (124, 92, 128, 108)      # a beira do Nilo
    reservado += [PRACA, DOCAS]
    def em_res(x, y, f=0): return any(r[0] - f <= x <= r[2] + f and r[1] - f <= y <= r[3] + f for r in reservado)
    casas = []
    for qy in range(y0c + 4, y1c - 1, 7):
        for qx in range(x0c + 4, x1c - 1, 7):
            cx_, cy_ = qx + 3.0, qy + 3.0
            if em_res(cx_, cy_, 3): continue
            borda = qx < x0c + 6 or qx > x1c - 9 or qy < y0c + 6 or qy > y1c - 9
            k = ("casa_soterrada" if borda and rng.random() < .45 else rng.choice(["casa_reerguida", "casa_reerguida_2", "casa_reerguida"]))
            fp = (4, 4) if k == "casa_soterrada" else (5, 5)
            predio(k, cx_, cy_, fp, luz=(OLEO + [4]) if k != "casa_soterrada" and rng.random() < .6 else None)
            casas.append((cx_, cy_))
    # praça central
    px0, py0, px1, py1 = PRACA
    a.prop("esfinge_carneiro_estatua", 139.0, 103.5, bloqueia=1.2, marco="esfinge_de_alabastro", pendente="esfinge_alabastro")
    lugar("praca_de_ptah", "Praça de Ptah", (139.0, 100.0))
    # praça do Primarca (Gustavo, armazém): em lugar central e visível, frente livre (+x -y)
    gx_, gy_ = 136.0, 102.5
    a.prop("arca_primarca", gx_, gy_, bloqueia=.5, luz=ROXO + [6], ponto="arca_primarca_menfis")
    a.prop("lampiao_oleo", gx_ - 1.6, gy_ - 1.2, bloqueia=.2, luz=OLEO + [4]); a.prop("lampiao_oleo", gx_ + 1.2, gy_ + 1.6, bloqueia=.2, luz=OLEO + [4])
    a.prop("jarros", gx_ - 1.4, gy_ + 1.4, bloqueia=.3)
    npcs.append(("gustavo_primarca", gx_ + .2, gy_ - 1.2, [1, -1]))
    # mercado (bancas sob toldo)
    for (x, y) in [(141.5, 97.0), (143.5, 99.5), (141.5, 96.0 + 6.5)]:
        a.prop("banca_mercado", x, y, bloqueia=.7, luz=OLEO + [3])
    a.prop("cestos_graos", 143.0, 96.0, bloqueia=.3); a.prop("jarros", 144.0, 101.5, bloqueia=.3)
    npcs += [("tuya_nomarca", 138.5, 98.0, [1, -1]), ("hapu_mercador", 142.5, 98.2, [-1, 0]), ("nefer_aguadeira", 140.5, 104.2, [0, -1])]
    # o templo de Ptah em ruínas e o colosso caído de Ramessés (fiel: o colosso deitado de Mit Rahina)
    predio("pilono_ruina", 146.5, 92.5, (12, 3), luz=OLEO + [4], marco="templo_de_ptah")
    predio("colosso_tombado", 147.0, 97.5, (6, 3), marco="colosso_de_ramesses")
    lugar("templo_de_ptah", "Templo de Ptah", (146.5, 92.5)); lugar("colosso_de_ramesses", "Colosso de Ramessés", (147.0, 97.5))
    # o ferreiro de bronze
    a.prop("bancada_ferreiro", 131.5, 109.0, bloqueia=.6); a.prop("braseiro_ferro", 130.0, 110.5, bloqueia=.4, luz=FOGO + [6])
    a.prop("pilha_carvao", 132.8, 110.6, bloqueia=.3)
    npcs.append(("besankh_ferreiro", 131.5, 107.6, [1, 0]))
    # docas no Nilo: o nilômetro, o cais, felucas, o barqueiro
    predio("poco_nilometro", 127.0, 104.5, (3, 3), marco="nilometro")
    lugar("nilometro", "Nilômetro de Mênfis", (127.0, 104.5))
    a.prop("cais", 125.5, 97.0, chao=True); a.prop("cais", 125.5, 100.5, chao=True)
    for (x, y) in [(121.5, 95.5), (121.0, 106.0)]:
        if agua(int(x), int(y)): a.prop("feluca", x, y, chao=True)
    a.prop("barca_junco", 122.5, 109.5, chao=True)
    npcs.append(("ahmose_barqueiro", 126.5, 95.0, [1, -1]))
    a.objetos.append({"kind": "portal", "pos": [125.0, 95.6], "para": "egito", "chegada": [92.0, 119.5], "nome": "Feluca de Ahmose · para a Escavação (3 de ouro)",
                      "visual": "invisivel", "custo_ouro": 3, "npc": "ahmose_barqueiro"})
    lugar("docas_de_menfis", "Docas de Mênfis", (126.0, 99.0))
    # estação da Linha 7 (bonde-veleiro) na saída leste
    predio("bonde_veleiro", ESTACAO[0] + 3.0, ESTACAO[1] + 2.5, (6, 3), luz=OLEO + [4], marco="estacao_linha7")
    lugar("estacao_de_menfis", "Estação de Mênfis (Linha 7)", ESTACAO)
    # pombais, celeiros e lampiões de rua
    for (x, y) in [(150.5, 111.0), (125.5, 89.5)]: a.prop("pombal", x, y, bloqueia=.9)
    for (x, y) in [(151.0, 89.5), (149.5, 113.0)]: a.prop("celeiro", x, y, bloqueia=1.2)
    for qy in range(y0c + 3, y1c, 7):
        for qx in range(x0c + 3, x1c, 7):
            if (qx + qy) % 2 == 0 and a.livre(qx, qy) and not perto_prop(qx + .5, qy + .5, 1.5):
                a.prop("lampiao_oleo", qx + .5, qy + .5, bloqueia=.2, luz=OLEO + [4])
    a.espalhar(["jarros", "cestos_graos", "entulho"], 22, (x0c + 1, y0c + 1, x1c - 1, y1c - 1), chao=False, bloq=.3, dist=3.5)

    # ================================================================ Acampamento da Escavação (zona segura, ao pé da Esfinge)
    ax0, ay0, ax1, ay1 = ACAMP
    predio("tenda_escavacao", 78.0, 112.0, (4, 3), luz=OLEO + [4]); npcs.append(("reis_abdu", 80.4, 111.2, [1, 0]))
    predio("tenda_hermetista", 77.5, 118.5, (4, 3), luz=OLEO + [4]); npcs.append(("djedi_mago", 79.8, 117.6, [1, -1]))
    predio("tenda_atlante", 86.5, 120.0, (4, 3), luz=OLEO + [4]); npcs.append(("diaprepes_atlante", 86.0, 118.0, [0, -1]))
    predio("oficina_engenheiros", 87.0, 111.0, (4, 3), luz=TURQ + [5]); npcs.append(("dalva_ferraz", 85.0, 112.6, [-1, 0]))
    predio("tenda_coro", 83.0, 121.0, (4, 3), luz=FOGO + [4]); npcs.append(("conego_barnabe", 82.0, 119.2, [0, -1]))
    a.prop("fogueira", 82.5, 115.5, bloqueia=.5, luz=FOGO + [7])
    a.prop("carrinho_nefer", 84.6, 116.4, bloqueia=.6); npcs.append(("nefer_carrinho", 85.2, 115.2, [-1, 0]))
    a.prop("mesa_topografo", 76.0, 115.0, bloqueia=.4); a.prop("caixotes_achados", 89.0, 114.5, bloqueia=.4)
    a.prop("mesa_mumia", 89.5, 117.5, bloqueia=.5); a.prop("peneira_escavacao", 80.0, 109.5, bloqueia=.3)
    a.prop("vasos_canopicos", 88.5, 109.5, bloqueia=.3)
    for (x, y) in [(75.5, 110.0), (90.0, 121.5), (75.5, 121.5), (90.5, 108.5)]: a.prop("lampiao_oleo", x, y, bloqueia=.2, luz=OLEO + [4])
    a.prop("cais", 92.5, 118.0, chao=True); npcs.append(("meritre_barqueira", 91.5, 116.6, [1, 0]))
    a.objetos.append({"kind": "portal", "pos": [92.0, 117.5], "para": "egito", "chegada": [126.5, 97.5], "nome": "Feluca de Meritre · para Mênfis (3 de ouro)",
                      "visual": "invisivel", "custo_ouro": 3, "npc": "meritre_barqueira"})
    lugar("acampamento_escavacao", "Acampamento da Escavação", (82.0, 115.0))
    # ---- Gizé: a Esfinge olha para o leste (para o Nilo); atrás, a calçada sobe até Quéfren; Quéops ao norte, Miquerinos ao sul
    predio("esfinge", 70.0, 130.0, (14, 6), luz=TURQ + [4], marco="esfinge")
    a.prop("andaime", 74.0, 126.5, bloqueia=.8); a.prop("guincho", 76.5, 133.5, bloqueia=.8)
    lugar("esfinge", "A Esfinge", (70.0, 130.0))
    predio("piramide_quefren", 40.0, 134.0, (16, 16), marco="piramide_de_quefren"); lugar("piramide_de_quefren", "Pirâmide de Quéfren", (40.0, 134.0))
    predio("piramide_queops", 58.0, 160.0, (18, 18), marco="piramide_de_queops"); lugar("piramide_de_queops", "Grande Pirâmide de Quéops", (58.0, 160.0))
    predio("piramide_miquerinos", 30.0, 114.0, (10, 10), marco="piramide_de_miquerinos"); lugar("piramide_de_miquerinos", "Pirâmide de Miquerinos", (30.0, 114.0))
    for (x, y) in [(66.0, 150.0), (70.0, 156.5), (68.0, 145.0)]: a.prop(rng.choice(["andaime", "guincho", "tenda_escavacao"]), x, y, bloqueia=.9)
    a.prop("trilho_vagonete", 72.5, 146.0, chao=True); a.prop("trilho_vagonete", 75.0, 143.0, chao=True); a.prop("vagonete", 74.0, 144.6, bloqueia=.4)
    for (x, y) in [(48.0, 144.0), (34.0, 148.0), (46.0, 120.0)]: predio("mastaba", x, y, (6, 4))
    # ---- Sacará: a pirâmide de degraus de Djoser (Imhotep) e as mastabas
    predio("piramide_degraus", 42.0, 100.0, (14, 12), marco="piramide_de_djoser"); lugar("piramide_de_djoser", "Pirâmide de Degraus de Djoser", (42.0, 100.0))
    for (x, y) in [(56.0, 88.0), (66.0, 106.0), (52.0, 108.0)]: predio("mastaba", x, y, (6, 4))
    # ---- Vila dos Artesãos (Deir el-Medina): casinhas caiadas em fila, tumbas-capela atrás
    vx, vy = B["VIL"][:2]
    for i, (dx, dy) in enumerate([(-7, 4), (-3.5, 6.5), (0, 8), (4, 7), (-8, -1), (7, 3)]):
        predio("casa_artesao" if i % 2 else "casa_artesao_2", vx + dx, vy + dy, (3, 4))
    lugar("vila_dos_artesaos", "Vila dos Artesãos", (vx, vy + 6))
    # ---- Casa da Vida: a biblioteca do templo, meio enterrada
    hx, hy = B["VID"][:2]
    predio("casa_da_vida", hx - 2.0, hy + 7.0, (12, 8), luz=OLEO + [5], marco="casa_da_vida")
    a.prop("estante_rolos", hx + 5.0, hy + 3.0, bloqueia=.5); a.prop("mesa_escriba", hx + 3.0, hy + 1.0, bloqueia=.4)
    lugar("casa_da_vida", "Casa da Vida", (hx - 2.0, hy + 7.0))
    # ---- Faium: o lago Méris, palmeiras, Crocodilópolis, a pirâmide de tijolo de Hawara (porta do Labirinto)
    predio("piramide_tijolo", PORTA_HAWARA[0], PORTA_HAWARA[1] - 7.0, (12, 12), marco="piramide_de_hawara")
    predio("portal_dungeon", PORTA_HAWARA[0], PORTA_HAWARA[1] + .6, (3, 1), luz=TURQ + [7], marco="porta_do_labirinto")
    a.objetos.append({"kind": "portal", "pos": PORTA_HAWARA, "para": "hawara_1", "chegada": [12.5, 40.5], "nome": "O Labirinto de Hawara (nível 50)",
                      "visual": "invisivel", "nivel_minimo": 50, "dungeon": "labirinto_de_hawara"})
    lugar("labirinto_de_hawara", "Porta do Labirinto de Hawara", PORTA_HAWARA)
    fx, fy = B["FAI"][:2]
    a.prop("pilono_ruina", fx - 4.0, fy + 7.0, bloqueia=1.5, marco="templo_de_sobek")
    npcs.append(("senebtisi_sacerdotisa", fx + 1.0, fy + 4.0, [0, -1]))
    lugar("templo_de_sobek", "Templo de Sobek (Crocodilópolis)", (fx - 4.0, fy + 7.0))
    # ---- Karnak: pilono, salão hipostilo (fileiras de colunas papiriformes), obeliscos, colossos
    kx, ky = B["KAR"][:2]
    predio("pilono", kx - 9.0, ky + 1.0, (3, 12), marco="primeiro_pilono")
    for i in range(4):
        for j in range(4):
            x, y = kx - 4.0 + i*3.0, ky - 4.5 + j*3.0
            k = "coluna_papiro" if (i + j*3) % 5 else "coluna_papiro_quebrada"
            a.prop(k, x, y, bloqueia=.7)
    a.prop("coluna_tombada", kx + 9.0, ky - 6.0, chao=True)
    for (x, y) in [(kx - 11.5, ky - 4.0), (kx - 11.5, ky + 6.0)]: a.prop("obelisco", x, y, bloqueia=.6)
    a.prop("obelisco_tombado", kx + 6.0, ky + 9.0, chao=True)
    for (x, y) in [(kx - 12.0, ky - 1.0), (kx - 12.0, ky + 3.5)]: a.prop("colosso_sentado", x, y, bloqueia=1.6)
    for k_ in range(6): a.prop("estatua_sekhmet", kx + 9.5, ky - 2.0 + k_*1.6, bloqueia=.4)    # a fila de Sekhmets de Mut
    lugar("salao_hipostilo", "Salão Hipostilo de Ipet-Isut", (kx, ky))
    # ---- a Avenida das Esfinges (esfinges de carneiro em fila dos dois lados da calçada)
    (ax_, ay_), (bx_, by_) = B["MEN"][:2], B["AVE"][:2]
    p0, p1 = (CID[2] + 1.0, 97.0), (B["KAR"][0] - 11.0, B["KAR"][1] + 1.0)
    n_ = int(math.dist(p0, p1)/3.2)
    ux, uy = (p1[0] - p0[0])/math.dist(p0, p1), (p1[1] - p0[1])/math.dist(p0, p1)
    for i in range(1, n_):
        cx_, cy_ = p0[0] + (p1[0] - p0[0])*i/n_, p0[1] + (p1[1] - p0[1])*i/n_
        for s in (-1, 1):
            x, y = cx_ - uy*3.0*s, cy_ + ux*3.0*s
            if a.livre(int(x), int(y)) and not em_spot(x, y, -2) and not perto_prop(x, y, 2.0):
                a.prop("esfinge_carneiro_estatua", x, y, bloqueia=.7)
    for y in range(H):
        for x in range(W):
            if dist_seg(x + .5, y + .5, p0, p1) < 1.4 and a.livre(x, y) and not agua(x, y): a.ter[y][x] = "j"; trilha[y][x] = estrada[y][x] = True
    lugar("avenida_das_esfinges", "Avenida das Esfinges", ((p0[0] + p1[0])/2, (p0[1] + p1[1])/2))
    # ---- o Lago Sagrado
    lugar("lago_sagrado", "Lago Sagrado", LAGO_SAGRADO[:2])
    a.prop("colosso_sentado", LAGO_SAGRADO[0] - 9.0, LAGO_SAGRADO[1] + 2.0, bloqueia=1.6)
    # ---- Terraços de Hatshepsut (Djeser-Djeseru, "o sagrado dos sagrados") ao pé do penhasco
    tx, ty = B["HAT"][:2]
    predio("terracos_templo", tx - 6.0, ty + 8.0, (18, 10), luz=OLEO + [4], marco="djeser_djeseru")
    lugar("djeser_djeseru", "Djeser-Djeseru", (tx - 6.0, ty + 8.0))
    # ---- Vale dos Reis: tumbas no paredão; a tumba sem cartucho no fundo (porta da Raid)
    for (x, y, k) in [(22.0, 182.5, "entrada_tumba"), (32.0, 180.5, "entrada_tumba_2"), (36.0, 166.0, "entrada_tumba")]:
        a.prop(k, x, y, bloqueia=1.0)
    predio("tumba_sem_cartucho", PORTA_RAID[0], PORTA_RAID[1] + 1.0, (5, 2), luz=TURQ + [6], marco="tumba_sem_cartucho")
    a.objetos.append({"kind": "portal", "pos": PORTA_RAID, "para": "coracao_1", "chegada": [12.5, 40.5], "nome": "A Tumba Sem Cartucho · O Coração Endurecido (Raid nível 60)",
                      "visual": "invisivel", "nivel_minimo": 60, "requer_flag": "sintonia_coracao", "raid": "coracao_endurecido",
                      "texto_trancado": "O selo de barro está quebrado, mas a porta não abre para quem não carrega o nome dele. Fale com Djedi."})
    lugar("tumba_sem_cartucho", "A Tumba Sem Cartucho", PORTA_RAID)
    # ---- Primeira Catarata: a pedreira de granito e o obelisco inacabado
    cx2, cy2 = B["SUL"][:2]
    a.prop("obelisco_inacabado", cx2 + 2.0, cy2 - 3.0, chao=True, marco="obelisco_inacabado")
    lugar("obelisco_inacabado", "O Obelisco Inacabado", (cx2 + 2.0, cy2 - 3.0))
    for y in range(4, 36):                                     # rochedos de granito dentro do rio (as corredeiras)
        for x in range(96, 130):
            if a.ter[y][x] in "rw" and (x, y) not in trav_cel and rng.random() < .05:
                a.prop(rng.choice(["rocha_granito", "rocha_granito_2"]), x + .5, y + .5, chao=False)
    # ---- Nilo: papiro, lótus, barcas, shaduf e saqia nas margens
    for (x, y) in [(116.0, 128.0), (113.5, 150.0), (96.5, 62.0), (112.0, 70.0)]:
        if agua(int(x), int(y)): a.prop("feluca", x, y, chao=True)
    for p0_, p1_, tipo in TRAVESSIAS:
        L_ = math.dist(p0_, p1_); n2 = int(L_/2.6)
        for i in range(n2 + 1):
            x, y = p0_[0] + (p1_[0] - p0_[0])*i/n2, p0_[1] + (p1_[1] - p0_[1])*i/n2
            if agua(int(x), int(y)):
                a.prop("ponte_barcas" if tipo == "ponte_barcas" else ("laje_rolada" if tipo == "dique" else "rocha_granito_2"), x, y, chao=True)
    lugar("ponte_de_barcas", "Ponte de Barcas", ((TRAVESSIAS[0][0][0] + TRAVESSIAS[0][1][0])/2, (TRAVESSIAS[0][0][1] + TRAVESSIAS[0][1][1])/2))
    lugar("dique_velho", "Dique Velho", ((TRAVESSIAS[1][0][0] + TRAVESSIAS[1][1][0])/2, (TRAVESSIAS[1][0][1] + TRAVESSIAS[1][1][1])/2))
    lugar("vau_da_catarata", "Vau da Catarata", ((TRAVESSIAS[2][0][0] + TRAVESSIAS[2][1][0])/2, (TRAVESSIAS[2][0][1] + TRAVESSIAS[2][1][1])/2))

    # ================================================================ spots estilo MU (anel de grupos, fogueira na chegada, marco atrás)
    marcos = {"juncal_do_papiro": "barca_junco", "campos_da_cheia": "shaduf", "avenida_das_esfinges": "estela",
              "salao_hipostilo": "coluna_tombada", "lago_sagrado": "estatua_sekhmet", "primeira_catarata": "rocha_granito",
              "vila_dos_artesaos": "celeiro", "mastabas_de_sacara": "estela", "escavacao_de_queops": "sarcofago_aberto",
              "calcada_de_quefren": "estatua_anubis", "casa_da_vida": "estante_rolos", "crocodilopolis": "estela",
              "lago_meris": "palmeira_dum", "mar_de_areia": "duna_alta", "terracos_de_hatshepsut": "estatua_anubis",
              "vale_dos_reis": "estela", "necropole_proibida": "sarcofago_aberto"}
    centro_menfis, centro_esc = B["MEN"][:2], B["ESC"][:2]
    for key, (bx, by, r, z, sp) in blobs:
        if not sp: continue
        sid, nome, niv, grupos = sp
        assert sum(q*n for _, q, n, _ in grupos) == 12, sid
        spots.append({"id": sid, "nome": nome, "nivel": niv, "pos": [bx, by], "raio": round(r*.85, 1), "respawn_s": 14, "zona": z,
                      "mobs": 12})
        fila = []
        restos = [[(m, q, t)]*n for m, q, n, t in grupos]
        while any(restos):
            for l in restos:
                if l: fila.append(l.pop(0))
        base = centro_menfis if bx > 100 else centro_esc
        vx, vy = (base[0] - bx, base[1] - by); dn = math.hypot(vx, vy) or 1; vx, vy = vx/dn, vy/dn
        ang_cam = math.atan2(vy, vx)
        cands = []
        for ia in range(36):
            ang = ang_cam + math.pi + (ia - 18)/36*2*math.pi*.86
            for rr in (r*.36, r*.52, r*.66, r*.22, r*.76, r*.88, r*.44, r*.6, r*.95):
                cands.append((abs(ia - 18) % 7, bx + math.cos(ang)*rr, by + math.sin(ang)*rr))
        cands.sort(key=lambda c: c[0])
        postos = []
        for (_, x, y) in cands:
            if len(postos) >= len(fila): break
            if not livre3(int(x), int(y)) or perto_prop(x, y, 1.6): continue
            mob, qtd, temp = fila[len(postos)]
            if any(math.dist((x, y), p) < (4.8 if temp != "neutro" else 3.2) for p in postos): continue
            nv = niv[0] + round((niv[1] - niv[0])*len(postos)/max(1, len(fila) - 1))
            s_ = {"mob": mob, "pos": [round(x, 1), round(y, 1)], "raio": 1.5, "qtd": qtd, "nivel": nv, "temperamento": temp,
                  "spot": sid, "respawn_s": 14, "motivo": MOBS[mob]["motivo"]}
            if temp == "territorial": s_["raio_territorio"] = 4
            a.spawns.append(s_); postos.append((x, y))
        if len(postos) < len(fila): print("SPOT INCOMPLETO", sid, len(postos), "de", len(fila))
        mx, my = bx - r*.62, by + r*.62
        if a.livre(int(mx), int(my)) and not agua(int(mx), int(my)) and not perto_prop(mx, my, 2.0):
            a.prop(marcos[sid], mx, my, bloqueia=.8)
    # ---- pontos de descanso (fogueira + carrinho da Nefer), um para cada par de spots
    pares = [("juncal_do_papiro", "campos_da_cheia"), ("avenida_das_esfinges", "salao_hipostilo"), ("lago_sagrado", "primeira_catarata"),
             ("vila_dos_artesaos", "mastabas_de_sacara"), ("escavacao_de_queops", "calcada_de_quefren"), ("casa_da_vida", "crocodilopolis"),
             ("lago_meris", "mar_de_areia"), ("terracos_de_hatshepsut", "vale_dos_reis"), ("necropole_proibida", "vale_dos_reis")]
    nomes_desc = ["Fogueira do Papiro", "Fogueira da Avenida", "Fogueira da Pedreira", "Fogueira dos Artesãos", "Fogueira da Calçada",
                  "Fogueira dos Escribas", "Fogueira de Méris", "Fogueira do Penhasco", "Fogueira dos Embalsamadores"]
    pos_sp = {s["id"]: s["pos"] for s in spots}
    for (s1, s2), nome in zip(pares, nomes_desc):
        (ax_, ay_), (bx_, by_) = pos_sp[s1], pos_sp[s2]
        alvo = ((ax_ + bx_)/2, (ay_ + by_)/2)
        melhor = None
        for y in range(H):
            for x in range(W):
                if not trilha[y][x] or agua(x, y): continue
                for (ox, oy) in [(1.8, -1.8), (-1.8, 1.8), (2.2, 0), (0, 2.2)]:
                    qx, qy = x + .5 + ox, y + .5 + oy
                    if not livre3(int(qx), int(qy)) or trilha[int(qy)][int(qx)] or em_spot(qx, qy, 1.0) or perto_prop(qx, qy, 2.5): continue
                    d = math.dist((qx, qy), alvo)
                    if melhor is None or d < melhor[0]: melhor = (d, qx, qy)
        if not melhor: print("SEM DESCANSO", nome); continue
        _, qx, qy = melhor
        if any(math.dist((qx, qy), (d["x"], d["y"])) < 8 for d in descanso): continue
        a.prop("fogueira", qx, qy, bloqueia=.5, luz=FOGO + [6])
        a.prop("carrinho_nefer", qx + 1.8, qy + .8, bloqueia=.6, ponto="descanso")
        descanso.append({"nome": nome, "x": round(qx, 1), "y": round(qy, 1), "props": ["fogueira", "carrinho_nefer"],
                         "npc": "nefer_carrinho (vende poção)", "entre": [s1, s2]})
        npcs.append(("nefer_carrinho", round(qx + 2.6, 1), round(qy - .4, 1), [-1, 0]))
    # ---- fora dos spots: poucos pares com motivo e respiro
    for (k1, k2, mob, niv, qtd, temp) in [("MEN", "PAP", "ibis_de_thoth", 50, 2, "neutro"), ("ESC", "VIL", "escaravelho_sagrado", 52, 2, "neutro"),
                                          ("VIL", "VID", "mumia_operaria", 56, 2, "neutro"), ("SAQ2", "MAR", "escorpiao_de_serket", 62, 2, "territorial"),
                                          ("KAR", "LAG", "naja", 58, 2, "neutro"), ("GIZ2", "HAT", "escaravelho_rei", 63, 1, "neutro"),
                                          ("FAI", "FAI2", "crocodilo_do_nilo", 62, 2, "neutro"), ("NEC", "VAL", "anubis_sentinela", 68, 2, "territorial")]:
        (x0, y0), (x1, y1) = B[k1][:2], B[k2][:2]
        ok = False
        for t in (.5, .4, .6, .32, .68, .25, .75, .2, .8, .15, .85):
            for (ox, oy) in [(2.5, -2.5), (-2.5, 2.5), (3.5, 0), (0, 3.5), (0, 0), (-3.5, 0), (0, -3.5), (4.5, -4.5), (-4.5, 4.5)]:
                x, y = x0 + (x1 - x0)*t + ox, y0 + (y1 - y0)*t + oy
                if livre3(int(x), int(y)) and not trilha[int(y)][int(x)] and not em_spot(x, y, 2) and not perto_prop(x, y, 1.3) \
                        and zona_de[int(y)][int(x)] not in ("menfis", "escavacao"): ok = True; break
            if ok: break
        if not ok:   # na borda do blob de destino, fora do spot
            bx2, by2, br2 = B[k2][:3]
            for ia in range(48):
                for rr in (br2 + 2, br2 + 4, br2 + 6, br2 - 1):
                    x, y = bx2 + math.cos(ia/48*6.283)*rr, by2 + math.sin(ia/48*6.283)*rr
                    if 0 < x < W - 1 and 0 < y < H - 1 and livre3(int(x), int(y)) and not trilha[int(y)][int(x)] and not em_spot(x, y, 2) \
                            and not perto_prop(x, y, 1.3) and zona_de[int(y)][int(x)] not in ("menfis", "escavacao"): ok = True; break
                if ok: break
        if not ok: print("PAR SEM LUGAR", mob); continue
        s_ = {"mob": mob, "pos": [round(x, 1), round(y, 1)], "raio": 1.5, "qtd": qtd, "nivel": niv, "temperamento": temp, "respawn_s": 25,
              "motivo": MOBS[mob]["motivo"]}
        if temp == "territorial": s_["raio_territorio"] = 4
        a.spawns.append(s_)

    # ================================================================ props soltos por zona (vocabulário de cada área)
    def solto(kinds, n, bloq, dist, zonas, spot_ok=False, chao=False, luz=None, pisos=None, agua_ok=False):
        f = t = 0
        while f < n and t < 12000:
            t += 1
            x, y = rng.uniform(4, W - 4), rng.uniform(4, H - 4); ix, iy = int(x), int(y)
            if zona_de[iy][ix] not in zonas: continue
            if agua_ok:
                if a.ter[iy][ix] not in "rw": continue
            elif a.blk[iy][ix] or trilha[iy][ix] or agua(ix, iy): continue
            if pisos and a.ter[iy][ix] not in pisos: continue
            if not spot_ok and em_spot(x, y, 1.5): continue
            if bloq and not livre3(ix, iy): continue
            if perto_prop(x, y, dist): continue
            if x0c - 2 <= x <= x1c + 2 and y0c - 2 <= y <= y1c + 2: continue
            if ACAMP[0] - 1 <= x <= ACAMP[2] + 1 and ACAMP[1] - 1 <= y <= ACAMP[3] + 1: continue
            if math.dist((x, y), PORTA_HAWARA) < 5 or math.dist((x, y), PORTA_RAID) < 5: continue
            a.prop(rng.choice(kinds), x, y, bloqueia=bloq, chao=chao); f += 1
            if luz and rng.random() < luz[0]: a.luzes.append([round(x, 2), round(y, 2)] + luz[1:])
    VIVOS = ["margem_papiro", "campos_cheia", "faium", "lago_sagrado"]
    solto(["tamareira_nilo", "tamareira_nilo_2", "tamareira_nilo_3", "palmeira_dum"], 70, .5, 4.0, VIVOS + ["vila_artesaos", "menfis"])
    solto(["moita_papiro", "moita_papiro_2", "juncos_nilo"], 80, 0, 1.8, ["margem_papiro", "faium", "catarata", "campos_cheia"], spot_ok=True, pisos="ml")
    solto(["lotus_azul", "moita_papiro"], 40, 0, 2.6, ["margem_papiro", "faium", "menfis", "catarata"], spot_ok=True, chao=True, agua_ok=True)
    solto(["campo_linho", "feixes_cevada_egito"], 30, 0, 3.0, ["campos_cheia", "faium"], spot_ok=True, chao=False, pisos="h")
    solto(["shaduf", "saqia"], 10, .7, 8.0, ["campos_cheia", "margem_papiro", "faium"])
    solto(["acacia"], 16, .5, 5.0, ["sacara", "vila_artesaos", "faium", "casa_vida", "campos_cheia"])
    solto(["jarros", "cestos_graos", "estela"], 26, .3, 3.0, ["vila_artesaos", "campos_cheia", "casa_vida", "sacara"], spot_ok=True)
    solto(["coluna_papiro_quebrada", "coluna_tombada", "estela", "obelisco_tombado"], 22, .6, 5.0, ["karnak", "avenida_esfinges", "lago_sagrado", "casa_vida"])
    solto(["sarcofago_aberto", "vasos_canopicos", "estela", "entulho"], 34, .3, 3.0, ["sacara", "gize", "necropole", "vale_reis"], spot_ok=True)
    solto(["andaime", "guincho", "caixotes_achados", "peneira_escavacao"], 14, .6, 5.0, ["gize", "sacara"])
    solto(["duna_alta", "duna_alta_2"], 22, 1.2, 7.0, ["mar_areia"])
    solto(["rocha_granito", "rocha_granito_2"], 30, 1.0, 4.0, ["catarata"], spot_ok=True)
    solto(["paredao_arenito", "paredao_arenito_2"], 10, 1.4, 7.0, ["vale_reis", "hatshepsut", "necropole"])
    solto(["estatua_anubis", "estela"], 10, .6, 6.0, ["necropole", "vale_reis", "hatshepsut"], luz=[.5] + TURQ + [3])
    # lampiões a óleo ao longo das calçadas de laje (metade apagados)
    ult = []
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            if not estrada[y][x] or any(math.dist((x, y), u) < 10 for u in ult): continue
            if x0c - 3 <= x <= x1c + 3 and y0c - 3 <= y <= y1c + 3: continue
            for (dx, dy) in [(-1.6, 1.6), (1.6, -1.6), (1.6, 1.6), (-1.6, -1.6)]:
                qx, qy = x + .5 + dx, y + .5 + dy
                if a.livre(int(qx), int(qy)) and not trilha[int(qy)][int(qx)] and not agua(int(qx), int(qy)) and not perto_prop(qx, qy, 1.5):
                    acesa = len(ult) % 2 == 0
                    a.prop("lampiao_oleo", qx, qy, bloqueia=.2, luz=(OLEO + [4]) if acesa else None)
                    ult.append((x, y)); break

    # ================================================================ borda: o mundo acaba em duna, penhasco, catarata e delta
    alta = {"mar_areia": ["tempestade_areia", "duna_alta", "duna_alta_2"], "vale_reis": ["paredao_arenito", "paredao_arenito_2"],
            "necropole": ["paredao_arenito", "duna_alta"], "hatshepsut": ["paredao_arenito", "paredao_arenito_2"],
            "gize": ["duna_alta", "duna_alta_2", "mastaba"], "sacara": ["duna_alta", "mastaba", "duna_alta_2"],
            "faium": ["tamareira_nilo", "palmeira_dum", "duna_alta"], "casa_vida": ["duna_alta", "casa_soterrada"],
            "vila_artesaos": ["duna_alta", "casa_soterrada"], "catarata": ["rocha_granito", "rocha_granito_2", "paredao_arenito"],
            "margem_papiro": ["moita_papiro", "tamareira_nilo_2", "moita_papiro_2"], "campos_cheia": ["tamareira_nilo", "palmeira_dum", "acacia"],
            "avenida_esfinges": ["casa_soterrada", "tamareira_nilo"], "karnak": ["pilono_ruina", "coluna_papiro_quebrada", "duna_alta"],
            "lago_sagrado": ["tamareira_nilo_3", "coluna_papiro_quebrada"], "menfis": ["casa_soterrada", "tamareira_nilo"],
            "escavacao": ["duna_alta", "tenda_escavacao"]}
    baixa = {"mar_areia": ["duna_alta_2", "estela"], "vale_reis": ["rocha_granito_2", "estela", "entulho"], "necropole": ["estela", "sarcofago_aberto", "entulho"],
             "hatshepsut": ["entulho", "estela"], "gize": ["entulho", "estela", "laje_rolada"], "sacara": ["entulho", "estela", "jarros"],
             "faium": ["moita_papiro", "juncos_nilo", "acacia"], "casa_vida": ["entulho", "jarros"], "vila_artesaos": ["jarros", "entulho"],
             "catarata": ["rocha_granito_2", "juncos_nilo"], "margem_papiro": ["juncos_nilo", "moita_papiro"], "campos_cheia": ["feixes_cevada_egito", "juncos_nilo"],
             "avenida_esfinges": ["entulho", "estela"], "karnak": ["coluna_tombada", "entulho"], "lago_sagrado": ["entulho", "juncos_nilo"],
             "menfis": ["entulho", "jarros"], "escavacao": ["caixotes_achados", "entulho"]}
    feitas = []
    for y in range(H):
        for x in range(W):
            if not a.blk[y][x] or a.ter[y][x] == "w": continue
            if not any(0 <= x + dx < W and 0 <= y + dy < H and not a.blk[y + dy][x + dx] and a.ter[y + dy][x + dx] not in "w"
                       for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)): continue
            qx, qy = x + rng.uniform(.2, .8), y + rng.uniform(.2, .8)
            if any(math.dist((qx, qy), f) < 2.3 for f in feitas[-100:]): continue
            zv = [zona_de[y + dy][x + dx] for dx in (-2, -1, 0, 1, 2) for dy in (-2, -1, 0, 1, 2)
                  if 0 <= x + dx < W and 0 <= y + dy < H and zona_de[y + dy][x + dx]]
            z = zv[0] if zv else "mar_areia"
            frente = any(0 <= x + k + d < W and 0 <= y - k < H and not a.blk[y - k][x + k + d] for k in range(1, 9) for d in (-1, 0, 1))
            k = rng.choice(baixa[z] if frente else alta[z])
            feitas.append((qx, qy)); a.prop(k, qx, qy, decor_moldura=True)

    # ================================================================ baús
    BAUS = [(132.0, 140.5, "caixote_podre", "bau_comum", "eg_juncal", None), (160.0, 144.0, "caixote_podre", "bau_comum", "eg_celeiro", None),
            (168.5, 86.0, "caixote_podre", "bau_comum", "eg_avenida", "mimico"),
            (184.0, 64.0, "bau_de_ferro", "bau_raro", "eg_karnak", ("Cofre dos Sacerdotes de Amon", "Um cofre de cedro forrado de bronze, atrás da última coluna. Dentro, a parte do templo que nunca foi para o templo.")),
            (162.0, 34.5, "caixote_podre", "bau_comum", "eg_lago", None), (140.0, 12.0, "bau_de_ferro", "bau_raro", "eg_catarata", None),
            (90.0, 84.0, "caixote_podre", "bau_comum", "eg_vila", ("Óstraco do Capataz", "Um caco de cerâmica com a lista de faltas da equipe de Sennedjem: 'Penebuy faltou: bebedeira. Paneb faltou: picado por escorpião.' Embaixo, o salário de um mês em cevada e cobre.")),
            (54.0, 92.0, "caixote_podre", "bau_comum", "eg_mastaba", None), (66.0, 104.5, "bau_de_ferro", "bau_raro", "eg_serapeu", ("Câmara do Serapeu", "Um sarcófago de touro Ápis, de granito, empurrado de lado. Os ladrões de três mil anos atrás não acharam o fundo falso.")),
            (82.0, 158.0, "caixote_podre", "bau_comum", "eg_escavacao_q", "mimico"), (52.0, 124.0, "bau_de_ferro", "bau_raro", "eg_calcada", None),
            (84.5, 72.0, "caixote_podre", "bau_comum", "eg_biblioteca", None), (46.0, 52.0, "caixote_podre", "bau_comum", "eg_crocodilopolis", None),
            (28.0, 30.0, "bau_de_ferro", "bau_raro", "eg_meris", None), (14.0, 92.0, "caixote_podre", "bau_comum", "eg_mar", "mimico"),
            (58.0, 178.0, "bau_de_ferro", "bau_raro", "eg_hatshepsut", ("Expedição a Punt", "Um baú de ébano com incenso de Punt ainda cheiroso. A rainha mandou buscar árvores vivas do outro lado do mar; isto é o que sobrou da viagem.")),
            (20.0, 168.0, "bau_de_ferro", "bau_raro", "eg_vale", None), (32.0, 142.0, "bau_de_ferro", "bau_raro", "eg_necropole", "mimico")]
    for (x, y, b, vis, idm, extra) in BAUS:
        q = None
        for r_ in range(0, 13):
            for dy in range(-r_, r_ + 1):
                for dx in range(-r_, r_ + 1):
                    if q is None and livre3(int(x + dx), int(y + dy)) and not trilha[int(y + dy)][int(x + dx)] and not perto_prop(x + dx, y + dy, 1.0): q = (x + dx, y + dy)
        if q is None: print("BAÚ SEM LUGAR", idm); continue
        o = {"kind": "bau", "pos": [round(q[0], 1), round(q[1], 1)], "bau": b, "visual": vis, "id_mapa": idm}
        if extra == "mimico": o["mimico"] = True
        elif extra: o["nome"], o["texto_ao_abrir"] = extra
        a.objetos.append(o)

    # ================================================================ interativos das missões (ids em objetos do conteúdo)
    def inter(obj, pts, prop=None, **kw):
        for i, (x, y) in enumerate(pts):
            q = None
            for r_ in range(0, 13):
                for dy in range(-r_, r_ + 1):
                    for dx in range(-r_, r_ + 1):
                        if q is None and livre3(int(x + dx), int(y + dy)) and not perto_prop(x + dx, y + dy, 1.0): q = (x + dx + .0, y + dy + .0)
            if q is None: print("INTERATIVO SEM LUGAR", obj, i); continue
            o = {"kind": "interativo", "obj": obj, "pos": [round(q[0], 1), round(q[1], 1)], "i": i}; o.update(kw); a.objetos.append(o)
            if prop: a.prop(prop, q[0], q[1] + .6, bloqueia=0)
    inter("marco_de_cheia", [(127.0, 107.0)])                                                   # K: o nilômetro
    inter("selo_da_nomarca", [(118.0, 132.0), (150.0, 128.0), (156.0, 150.0)], prop="estela")    # K: estacas de dízimo
    inter("quadricula_da_escavacao", [(72.0, 142.0), (80.0, 148.0), (68.0, 136.0)], prop="peneira_escavacao")
    inter("estela_do_sonho", [(76.5, 130.0)])                                                   # L: entre as patas da Esfinge
    inter("nicho_de_rolos", [(76.0, 72.0), (80.0, 70.0), (74.0, 64.0), (82.0, 62.0)], prop="estante_rolos")
    inter("ka_de_setne", [(hx - 2.0, hy + 2.5)])
    inter("camara_de_thoth", [(70.5, 126.0)])                                                   # L: a pata da Esfinge (Salão dos Registros)
    inter("relevo_de_dendera", [(kx + 2.0, ky - 7.0), (tx - 2.0, ty + 2.0), (fx + 4.0, fy + 2.0)])   # V: os três relevos
    inter("balanca_de_pedra", [(kx - 1.0, ky + 6.0)])                                           # A: a balança do templo
    inter("oferenda_a_sobek", [(fx - 2.0, fy - 2.0)], prop="jarros")                            # H
    inter("praga_de_sangue", [(110.5, 86.0), (106.0, 128.0), (92.0, 146.0)])                    # N: o Nilo virando sangue
    inter("porta_marcada", [(132.0, 92.5), (146.0, 108.5), (128.5, 110.0)])                     # N: as portas com sangue no lintel
    inter("cartucho_raspado", [(PORTA_RAID[0] + 3.0, PORTA_RAID[1] - 2.0)])
    inter("coluna_do_ritmo_eco", [(84.0, 123.0)])                                               # atlante: o cristal que vibra

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
    for (nid, x, y, d) in npcs:
        a.npcs.append({"id": nid, "pos": [x, y], "dir": d})
    m = a.exportar(spawn=SPAWN, ceu={"escuro": 0.3, "cor": [1.0, 0.78, 0.58], "neblina": [0.55, 0.46, 0.34], "sol": "sol_terco"})
    m["pisos"] = PISOS
    m["agua"] = {"fundo": [0.03, 0.06, 0.05], "raso": [0.16, 0.22, 0.17], "reflexo": [0.62, 0.5, 0.36], "brilho": [1.0, 0.78, 0.5],
                 "lume": [0.0, 0.0, 0.0], "espuma": [0.62, 0.58, 0.48]}
    m["rio"] = {"id": "nilo", "nome": "O Nilo", "nota": "a única água grande que sobrou no mundo; transbordou uma vez sem estação e deixou a lama preta", "centro": [list(map(float, p)) for p in NILO]}
    m["zona_grade"] = ["".join("." if zona_de[y][x] is None else LETRAS[ZI[zona_de[y][x]]] for x in range(W)) for y in range(H)]
    m["zonas"] = [{"id": i, "nome": n, "seguro": s, "nivel": nv, "musica": mu, "ambiente": am, "faccao": None, "neblina": ne}
                  for (i, n, s, nv, _, ne, mu, am) in ZONAS]
    m["exterior"] = True
    m["spots"] = spots
    m["descanso"] = descanso
    m["lugares"] = lugares
    m["sons"] = [{"som": "ambiente/pontual/egito_chamado", "x": 139.0, "y": 100.0, "raio": 30, "intervalo_s": [40, 90]},
                 {"som": "ambiente/pontual/egito_picareta", "x": 74.0, "y": 140.0, "raio": 28, "intervalo_s": [3, 8]},
                 {"som": "ambiente/pontual/egito_sistro", "x": 178.0, "y": 58.0, "raio": 26, "intervalo_s": [25, 60]},
                 {"som": "ambiente/pontual/egito_corredeira", "x": 116.0, "y": 18.0, "raio": 30, "intervalo_s": [6, 12]},
                 {"som": "ambiente/pontual/egito_ra_tempestade", "x": 18.0, "y": 100.0, "raio": 34, "intervalo_s": [12, 30]},
                 {"som": "ambiente/pontual/egito_lamento", "x": 22.0, "y": 176.0, "raio": 30, "intervalo_s": [20, 50]}]
    m["salas"] = [{"nome": (sp[1] if sp else ZONAS[ZI[z]][1]), "ret": [bx - 3, by - 2, bx + 3, by + 2]} for k, (bx, by, r, z, sp) in blobs
                  if sp or k in ("MEN", "ESC", "HAW")]
    json.dump(m, open(f"{SAIDA}/egito.json", "w"), ensure_ascii=False, separators=(",", ":"))
    print("egito", W, "x", H, "props", len(m["props"]), "spawns", len(m["spawns"]), "objetos", len(m["objetos"]), "spots", len(spots), "descanso", len(descanso))
    return m


def _dentro(px, py, poli):
    c = False; n = len(poli)
    for i in range(n):
        (x1, y1), (x2, y2) = poli[i], poli[(i + 1) % n]
        if (y1 > py) != (y2 > py) and px < (x2 - x1)*(py - y1)/(y2 - y1) + x1: c = not c
    return c


if __name__ == "__main__":
    qual = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    if qual in ("egito", "tudo"):
        m = mapa(); G.planta(m, f"{SAIDA}/planta_egito.png", "Egito, a Terra Negra (nível 50 a 70)")
    if qual in ("hawara", "tudo"):
        import dungeons_egito as D
        for fn, tit in D.HAWARA:
            m = fn(); G.planta(m, f"{SAIDA}/planta_{m['id']}.png", tit)
    if qual in ("raid", "tudo"):
        import dungeons_egito as D
        for fn, tit in D.RAID:
            m = fn(); G.planta(m, f"{SAIDA}/planta_{m['id']}.png", tit)
