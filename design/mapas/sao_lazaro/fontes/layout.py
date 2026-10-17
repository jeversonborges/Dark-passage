# Cidade de São Lázaro (Vigília) · área inicial níveis 1 a 12 · v1.0 (16/10/2026)
# Pedido do Jefin (15/10): a área inicial vira da Vigília. A cidade da igreja de São Lázaro no deserto, com a
# rádio, o matadouro, a linha do bonde e o cemitério; mapa coeso, maior, com o dobro de props e nada empilhado;
# spots de farm bons; missões e mobs. Referência: Dark Souls 3 (gótico, bonito, soturno) + Ferrugem Sagrada.
#
# Mundo aberto: área jogável 160x160 no meio de uma moldura de 20 tiles de cenário (200x200 no total).
# Mesmo formato do mapa anterior (design/mapas/area_inicial.json), então o jogo lê sem mudar o leitor.
# Uso:  python3 layout.py   (numpy, scipy, pillow)  ->  ../area_inicial.json, ../spots.json
# Eixos iguais ao jogo: 1 tile = 1 m; +x desce para a direita na tela, +y sobe para a direita.
import json, math, random, os, glob
import numpy as np
from scipy import ndimage
from PIL import Image

AQUI = os.path.dirname(os.path.abspath(__file__))
PF = "/mnt/project-files"
OBJ = f"{PF}/assets/ambiente/objetos"
N = 160
R = random.Random(2026)
HW, HH = 45.255, 22.627

# ------------------------------------------------------------------ ruído e curvas
def fbm(seed, oct=5, base=6):
    rng = np.random.default_rng(seed); out = np.zeros((N, N)); amp = 1; tot = 0
    for o in range(oct):
        s = base * 2 ** o
        g = rng.random((s + 3, s + 3))
        z = ndimage.zoom(g, (N + 3 * N / s) / (s + 3), order=3)[:N, :N]
        out += z * amp; tot += amp; amp *= .5
    out /= tot
    return (out - out.min()) / (out.max() - out.min())
NZ = fbm(11); NZ2 = fbm(23, base=10); NZ3 = fbm(37, base=4)
XX, YY = np.meshgrid(np.arange(N) + .5, np.arange(N) + .5, indexing="ij")

def spline(pts, step=.25):
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = map(np.array, P[i - 1:i + 3])
        L = max(2, int(np.linalg.norm(p2 - p1) / step))
        for k in range(L):
            t = k / L
            out.append(tuple(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(pts[-1])); return out
def poli(pts, step=.25):
    out = []
    for a, b in zip(pts, pts[1:]):
        L = max(1, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
        out += [(a[0] + (b[0] - a[0]) * k / L, a[1] + (b[1] - a[1]) * k / L) for k in range(L)]
    return out + [tuple(pts[-1])]
def dist_to(curve):
    m = np.ones((N, N), bool)
    for x, y in curve:
        xi, yi = int(x), int(y)
        if 0 <= xi < N and 0 <= yi < N: m[xi, yi] = False
    return ndimage.distance_transform_edt(m)
def circ(c, r, jitter=0.0, nz=NZ): return np.hypot(XX - c[0], YY - c[1]) < r + (nz - .5) * jitter
def ellip(c, rx, ry, jitter=0.0): return ((XX - c[0]) / rx) ** 2 + ((YY - c[1]) / ry) ** 2 < 1 + (NZ - .5) * jitter

# ------------------------------------------------------------------ arte do kit: footprint e silhueta na tela
KFP, BOX, MASK = {}, {}, {}
DS = 8                                       # resolução da máscara de silhueta (px de tela por célula)
# o kit do Cenário primeiro; o que só existe no jogo (ex.: capela_sao_lazaro, do kit antigo) vem de game/assets/ext
OBJ_JOGO = f"{PF}/game/assets/ext/ambiente/objetos"
_kit = {os.path.basename(f)[:-5]: f for f in glob.glob(f"{OBJ_JOGO}/*.json")}
_kit.update({os.path.basename(f)[:-5]: f for f in glob.glob(f"{OBJ}/*.json")})
for f in _kit.values():
    m = json.load(open(f)); k = m.get("kind") or os.path.basename(f)[:-5]
    fp = m.get("footprint_tiles", [1, 1])
    KFP[k] = (max(1, round(fp[0] * .7071)), max(1, round(fp[1] * .7071)))
    try:
        im = Image.open(f[:-5] + ".png").getchannel("A")
        ax, ay = m["anchor"]
        a = np.asarray(im) > 90
        ys, xs = np.nonzero(a)
        BOX[k] = (xs.min() - ax, ys.min() - ay, xs.max() - ax, ys.max() - ay) if len(xs) else (0, 0, 1, 1)
        # máscara reduzida, alinhada à grade global de DS px (origem na âncora arredondada)
        sm = np.asarray(im.resize((max(1, im.width // DS), max(1, im.height // DS)), Image.BOX)) > 110
        MASK[k] = (sm, int(round(ax / DS)), int(round(ay / DS)))
    except Exception: pass
def arte(kind, orient=None):
    if kind in BOX: return kind
    for s in (("_b", "_a") if orient == "y" else ("_a", "_b")):
        if kind + s in BOX: return kind + s
    return None

# ------------------------------------------------------------------ pontos-chave
CITY = (50, 80); CITY_R = 24                  # Cidade de São Lázaro (zona segura da Vigília)
PRACA = (48, 78)                              # Praça da Vela, em frente à porta da matriz
MATRIZ = (48, 92)                             # Igreja Matriz de São Lázaro (nave ao longo de y, porta no sul)
RADIO = (35, 92)                              # Rádio São Lázaro (prédio de concreto na beira do precipício)
ESTACAO = (64, 76)                            # Estação da Linha 7 (cúpula de vidro)
CEM = (78, 128)                               # Cemitério no Morro do Coveiro
ABAT = (140, 50)                              # Abatedouro Carniça
PATIO = (26, 40)                              # Pátio dos Bondes (cemitério de bondes)
VALA = (102, 28)
BAIRRO = (20, 127)
WOOD = (128, 121)
PIG = (142, 84)
VILA = (148, 138)
TRAM = (92, 58)                               # Marco do Corte (o bonde tombado)
LY = 70                                       # y dos trilhos da Linha 7

# ------------------------------------------------------------------ Rio Amargo
RIO = spline([(97, 163), (100, 150), (108, 138), (112, 124), (107, 112), (104, 100), (108, 88), (115, 77),
              (117, 64), (116, 52), (120, 41), (128, 31), (138, 22), (148, 14), (153, 9)])
largura = [2.2 + 2.6 * max(0.0, math.sin(i / len(RIO) * 25.0)) ** 2 + .5 * i / len(RIO) for i in range(len(RIO))]
m_ = np.ones((N, N), bool); lab = -np.ones((N, N), int)
for i, (x, y) in enumerate(RIO):
    xi, yi = int(x), int(y)
    if 0 <= xi < N and 0 <= yi < N: m_[xi, yi] = False; lab[xi, yi] = i
D_RIO, (IX, IY) = ndimage.distance_transform_edt(m_, return_indices=True)
IDX = lab[IX, IY]
HALF = np.array(largura)[IDX] / 2 + (NZ2 - .5) * .9
AGUA = D_RIO < HALF
FUNDA = D_RIO < HALF - .8
MARGEM = (D_RIO < HALF + 1.2 + NZ * 1.0) & ~AGUA
LEITO = (D_RIO < HALF + 4.0 + NZ2 * 3.0) & ~AGUA & ~MARGEM
OASIS = D_RIO < HALF + 6 + NZ * 7
# Ilha do Exilado (0.9.3): o rio abre num remanso em volta de uma ilhota onde o Pedro ergueu a oficina
ILHA_C = (107.6, 88.0)
ILHA = circ(ILHA_C, 3.8, 1.0)
LAGO = circ(ILHA_C, 7.0, 1.6) & ~ILHA
AGUA = (AGUA | LAGO) & ~ILHA
FUNDA = (FUNDA | (LAGO & ~circ(ILHA_C, 4.6))) & ~ILHA
MARGEM = ((MARGEM | circ(ILHA_C, 8.2, 1.0)) & ~AGUA) | ILHA
LEITO = LEITO & ~MARGEM & ~AGUA
dRIO = np.gradient(np.array(RIO), axis=0)
FLUXO = dRIO[IDX] / (np.linalg.norm(dRIO[IDX], axis=-1, keepdims=True) + 1e-6)

# ------------------------------------------------------------------ terreno
# a areia, u duna baixa, d duna alta (bloqueia), h abismo, y vidro derretido, s leito seco, t terra batida,
# z cinza, c calçamento, g cemitério, l laje (adro), m chapa do matadouro, w lama funda, r água rasa, b barranca,
# e musgo amargo, p brejo, f chão de mata morta, v terra de vala, k cascalho dos trilhos, n entulho, i asfalto
T = np.full((N, N), "a", dtype="<U1")
T[NZ3 > .64] = "u"
ZCITY = circ(CITY, CITY_R)
ZCAMPOS = ellip((90, 76), 16, 27, 1.0) & ~ZCITY & (D_RIO > HALF + 5)
ZPATIO = ellip(PATIO, 15, 13, .8) & ~ZCITY
ZVALA = ellip(VALA, 15, 13, .9)
BREJO = ZVALA & (D_RIO < HALF + 5 + NZ2 * 3)
ZBAIRRO = ellip(BAIRRO, 15, 23, .8)
ZCEM = ellip(CEM, 22, 16, .5) & (D_RIO > HALF + 3)
ZCARDOS = ellip((63, 108), 8, 6, 1.0) & ~ZCITY
ZWOOD = ellip(WOOD, 16, 15, 1.0) & ~AGUA & (D_RIO > HALF + 1.5)
ZPIG = ellip(PIG, 11, 9, .5)
ZDES = ellip((118, 100), 9, 8, .6) & (D_RIO > HALF + 1)
ZABAT = ellip(ABAT, 15, 13, .4) & (D_RIO > HALF + 3)
ZVILA = ellip(VILA, 10, 8, .6)

T[ZCAMPOS] = "z"; T[ZCAMPOS & (NZ2 > .55)] = "y"
T[ZPATIO] = "k"; T[ZPATIO & (NZ > .55)] = "a"
T[ZVALA] = "v"; T[BREJO] = "p"
T[ZBAIRRO & (NZ2 > .5)] = "n"
T[ZCEM] = "g"; T[ZCEM & (NZ3 > .62)] = "a"
T[ZCARDOS] = "f"
T[ZWOOD] = "f"
T[ZPIG] = "t"
T[ZDES] = "t"
T[ZABAT] = "m"; T[ZABAT & ~ellip(ABAT, 9, 8)] = "t"
T[ZVILA] = "i"; T[ZVILA & (NZ > .55)] = "a"
T[OASIS & np.isin(T, ["a", "u"])] = "e"
T[ZCITY] = "t"; T[ZCITY & (NZ2 > .6)] = "n"

# ------------------------------------------------------------------ trilhas e estradas
TRILHAS = [
    # id, nome, piso, largura, pontos
    ("estrada_sul", "Estrada do Sul", "c", 3.0, [(50, 57), (52, 46), (56, 34), (60, 20), (63, 6), (64, -2)]),
    ("avenida_matriz", "Avenida da Matriz", "c", 3.2, [(50, 56), (50, 64), (49, 72), (48, 80)]),
    ("rua_mercado", "Rua do Mercado", "c", 2.8, [(48, 80), (56, 80), (64, 80.5), (72, 80), (78, 79)]),
    ("estrada_leste", "Estrada do Leste", "c", 2.6, [(78, 79), (86, 78), (96, 75), (104, 71)]),
    ("rua_sino", "Rua do Sino", "c", 2.4, [(54, 98), (58, 102), (63, 106), (69, 111), (74, 115)]),
    ("beco_radio", "Beco da Rádio", "c", 2.2, [(44, 81), (40, 85), (37, 89)]),
    ("trilha_telhados", "Trilha dos Telhados", "t", 1.8, [(36, 98), (31, 104), (27, 112), (22, 119)]),
    ("trilha_patio", "Trilha do Pátio", "t", 2.0, [(34, 64), (31, 56), (29, 50)]),
    ("trilha_vala", "Trilha da Vala", "t", 1.8, [(56, 34), (68, 32), (80, 31), (90, 29)]),
    ("caminho_margem", "Caminho da Margem", "t", 1.6, [(104, 69), (107, 60), (109, 50), (110, 42), (113, 36)]),
    ("vau_do_sebo", "Vau do Sebo", "t", 1.6, [(113, 36), (119, 36), (125, 36), (130, 39)]),
    ("estrada_gado", "Estrada do Gado", "c", 2.4, [(126, 68), (130, 62), (133, 57), (135, 54)]),
    ("trilha_chiqueiros", "Trilha dos Chiqueiros", "t", 1.8, [(126, 70), (132, 75), (137, 80)]),
    ("trilha_procissao", "Trilha das Procissões", "t", 1.8, [(74, 115), (80, 118), (86, 120)]),
    ("cemiterio_alameda", "Alameda dos Ciprestes", "t", 1.5, [(74, 115), (72, 122), (70, 130), (72, 137)]),
    ("trilha_enforcados", "Trilha dos Enforcados", "t", 1.6, [(86, 120), (92, 117), (98, 114)]),
    ("trilha_viuvas", "Trilha das Viúvas", "t", 1.5, [(115, 113), (121, 116), (126, 113), (134, 112), (140, 120), (144, 130)]),
    ("trilha_desertor", "Caminho do Desertor", "t", 1.4, [(115, 113), (116, 108)]),
    ("trilha_tempestade", "Trilha da Tempestade", "t", 1.4, [(140, 120), (136, 132), (132, 140)]),
    ("trilha_cardos", "Trilha dos Cardos", "t", 1.3, [(58, 102), (62, 108), (66, 112)]),
    ("trilha_campos", "Trilha dos Espantalhos", "t", 1.4, [(78, 79), (82, 86), (84, 96), (80, 104)]),
]
D_TRILHA = np.full((N, N), 99.0); ROAD = np.zeros((N, N), bool); MAIN = np.zeros((N, N), bool)
trilhas_json = []
for tid, nome, piso, w, pts in TRILHAS:
    cur = spline(pts); d = dist_to(cur)
    mask = d < w / 2 + (NZ2 - .5) * .9
    T[mask & ~AGUA] = piso
    ROAD |= d < w / 2 + (1.0 if piso == "c" else .6)
    if piso == "c": MAIN |= d < w / 2 + 1
    D_TRILHA = np.minimum(D_TRILHA, d)
    trilhas_json.append({"id": tid, "nome": nome, "piso": {"c": "calcamento", "t": "terra"}[piso], "largura": w,
                         "pontos": [[round(a, 1), round(b, 1)] for a, b in pts]})
# Linha 7: reta ao longo de x (os trilhos do kit são em X ou em Y), da beira do precipício ao matadouro
LINHA7 = poli([(-2, LY), (124, LY), (124, 58), (133, 58)])
RAMAL = poli([(40, LY), (40, 46), (12, 46)])                 # ramal morto para o Pátio dos Bondes
D_L7 = np.minimum(dist_to(LINHA7), dist_to(RAMAL))
T[(D_L7 < 1.4) & ~AGUA] = "k"
ROAD |= D_L7 < 2.2; MAIN |= D_L7 < 2
trilhas_json.append({"id": "linha_7", "nome": "Trilhos da Linha 7", "piso": "trilho", "largura": 2.0,
                     "pontos": [[-2, LY], [124, LY], [124, 58], [133, 58]]})
trilhas_json.append({"id": "ramal_patio", "nome": "Ramal do Pátio", "piso": "trilho", "largura": 2.0, "pontos": [[40, LY], [40, 46], [12, 46]]})
# praça e adro da matriz
T[circ(PRACA, 6.5)] = "l"
# adro da matriz: laje em volta da nave, caminho até a praça e os canteiros do Jardim de São Lázaro (terra regada)
_mx, _my = MATRIZ
ADRO = (np.abs(XX - _mx) < 9.5) & (YY > _my - 13) & (YY < _my + 9.5)
T[ADRO] = "l"
CANTEIROS = []
for (bx0, by0, bx1, by1) in [(40.6, 80.4, 45.8, 85.0), (50.2, 80.4, 55.4, 85.0),      # na frente, dos dois lados do caminho
                             (53.4, 86.6, 56.6, 99.0), (39.4, 86.6, 42.6, 99.0),      # ao longo da nave (lado dos vitrais e lado da torre)
                             (44.2, 99.0, 51.8, 101.0)]:                              # atrás da cabeceira
    CANTEIROS.append((bx0, by0, bx1, by1))
    T[(XX > bx0) & (XX < bx1) & (YY > by0) & (YY < by1)] = "t"

# ------------------------------------------------------------------ água e pontes
T[LEITO & np.isin(T, ["a", "u", "e", "z", "y", "v", "f", "t", "g", "n", "i"])] = "s"
T[MARGEM] = "b"; T[AGUA] = "r"; T[FUNDA] = "w"; T[ILHA & ~circ(ILHA_C, 3.0)] = "b"; T[circ(ILHA_C, 3.0)] = "e"
PONTES = []
def ponte(pid, nome, a, b, w, kind):
    d = dist_to(poli([a, b])); m = d < w / 2
    PONTES.append(dict(id=pid, nome=nome, de=list(a), ate=list(b), largura=w, kind=kind, mask=m)); return m
P1 = ponte("ponte_bonde", "Ponte do Bonde", (106, LY), (126, LY), 3.4, "ponte_ferro_bonde")
P2 = ponte("ponte_enforcados", "Ponte dos Enforcados", (99, 113), (116, 113), 3.0, "ponte_pedra")
VAU = circ((122.5, 36), 4.4, 1.5) & AGUA
# pontes de corda da ilha: ao longo de X (o jogo cobre de tábuas o trecho de água); só baixam para quem traz a carta do Simão
P3 = ponte("ponte_corda_oeste", "Ponte de Corda (oeste)", (ILHA_C[0] - 8.8, ILHA_C[1]), (ILHA_C[0] - 2.8, ILHA_C[1]), 2.2, "ponte_corda")
P4 = ponte("ponte_corda_leste", "Ponte de Corda (leste)", (ILHA_C[0] + 2.8, ILHA_C[1]), (ILHA_C[0] + 8.8, ILHA_C[1]), 2.2, "ponte_corda")
for p_ in PONTES[-2:]: p_.update(trava="missao:a01", nota="a ponte só baixa para quem traz a palavra do coveiro (carta do Simão, missão A Carta do Coveiro)")
ROAD |= P1 | P2 | P3 | P4

# ------------------------------------------------------------------ limites disfarçados (mundo aberto)
PRECIPICIO = XX < np.maximum(1.5, 3.0 + NZ * 4 + (NZ2 - .5) * 9 + NZ3 * 2)
TEMP_BLOQ = YY > N - 2.5 - NZ2 * 2
TEMPESTADE = (YY > N - 14 - NZ2 * 5) & ~TEMP_BLOQ
DUNAS = XX > N - 5 - NZ * 5
DUNAS_SUL = YY < 2.5 + NZ2 * 3
SUMIDOURO = circ((153, 8.5), 2.6)
BORDA = PRECIPICIO | TEMP_BLOQ | DUNAS | DUNAS_SUL | SUMIDOURO
T[BORDA & ~AGUA] = "d"
T[PRECIPICIO | SUMIDOURO] = "h"
T[TEMPESTADE & np.isin(T, ["a", "e", "s"])] = "u"
LY_OK = ~PRECIPICIO

# ------------------------------------------------------------------ objetos
props = []; blocked = np.zeros((N, N), bool); ocup = np.zeros((N, N), bool)
# raster global de silhuetas na tela (anti-empilhamento): cada célula guarda o id do objeto que a ocupa
SW, SH_ = int(2 * N * HW / DS) + 200, int(2 * N * HH / DS) + 200
OCC = np.zeros((SH_, SW), np.int32); AREA = [0]
def _sil(kind, x, y):
    if kind not in MASK: return None
    sm, ax, ay = MASK[kind]
    u = int(round((x + y) * HW / DS)) - ax + 50; v = int(round((x - y) * HH / DS + N * HH / DS)) - ay + 100
    if u < 0 or v < 0 or u + sm.shape[1] > SW or v + sm.shape[0] > SH_: return None
    return sm, u, v
def _rect(kind, x, y): return _sil(kind, x, y)
def _overlap(r, lim):
    sm, u, v = r
    sub = OCC[v:v + sm.shape[0], u:u + sm.shape[1]][sm]
    a = max(1, int(sm.sum()))
    hit = sub[sub > 0]
    if len(hit) > lim * a: return True
    if len(hit):
        ids, cnt = np.unique(hit, return_counts=True)
        if any(c > lim * AREA[i] for i, c in zip(ids, cnt)): return True
    return False
def _reg(r):
    sm, u, v = r
    AREA.append(max(1, int(sm.sum()))); i = len(AREA) - 1
    blk = OCC[v:v + sm.shape[0], u:u + sm.shape[1]]
    blk[sm & (blk == 0)] = i
def fp_de(kind, orient=None):
    k = arte(kind, orient)
    return KFP.get(k, (1, 1)) if k else (1, 1)
def add(kind, x, y, block=True, camada=None, fp=None, silhueta=True, **kw):
    p = {"kind": kind, "x": round(float(x), 2), "y": round(float(y), 2)}
    if camada: p["camada"] = camada
    p.update({k: v for k, v in kw.items() if v is not None}); props.append(p)
    f = fp or (None if camada == "chao" else fp_de(kind, kw.get("orient")))
    if f and (f[0] > 1 or f[1] > 1):
        x0, y0 = int(x - f[0] / 2 + .5), int(y - f[1] / 2 + .5)
        sl = (slice(max(0, x0), max(0, x0 + f[0])), slice(max(0, y0), max(0, y0 + f[1])))
        ocup[sl] = True
        if block: blocked[sl] = True
    else:
        xi, yi = int(x), int(y)
        if 0 <= xi < N and 0 <= yi < N:
            ocup[xi, yi] = True
            if block and camada != "chao": blocked[xi, yi] = True
    if silhueta and camada != "chao":
        r = _rect(arte(kind, kw.get("orient")) or "", x, y)
        if r: _reg(r)
    return p

def livre(x, y, r=1.0, road_ok=False, water_ok=False, fp=(1, 1)):
    xi, yi = int(x), int(y)
    if not (1 <= xi < N - 1 and 1 <= yi < N - 1): return False
    rx, ry = r + fp[0] / 2 - .5, r + fp[1] / 2 - .5
    a, b = max(0, int(x - rx)), max(0, int(y - ry))
    if ocup[a:int(x + rx) + 1, b:int(y + ry) + 1].any(): return False
    if not road_ok and ROAD[a:int(x + rx) + 1, b:int(y + ry) + 1].any(): return False
    if not water_ok and AGUA[xi, yi]: return False
    if BORDA[xi, yi]: return False
    return True

BEIRA_OK = {"juncos", "mato_seco"}
_DAGUA = ndimage.distance_transform_edt(~AGUA)
RESERVA = np.zeros((N, N), bool)            # clareiras dos spots, praças e portões: o espalhamento não entra
def espalhar(mask, kinds, n, sep=1.5, block=True, road_ok=False, water_ok=False, camada=None, dens=None, tries=60,
             lim=.10, veg=False, **kw):
    """Espalha sem empilhar: respeita o footprint real do kit (chão) e a silhueta na tela (lim = sobreposição máxima)."""
    cand = np.argwhere(mask & ~RESERVA)
    if len(cand) == 0: return 0
    feitos = 0
    for _ in range(n * tries):
        if feitos >= n: break
        cx, cy = cand[R.randrange(len(cand))]
        x, y = cx + R.random(), cy + R.random()
        if dens is not None and R.random() > dens[cx, cy]: continue
        k = R.choice(kinds) if isinstance(kinds, list) else kinds
        f = (1, 1) if camada == "chao" else fp_de(k)
        if not livre(x, y, sep, road_ok, water_ok, f): continue
        if not water_ok and k not in BEIRA_OK and _DAGUA[cx, cy] < (5.5 if "arvore" in k else 3.0): continue
        if camada != "chao":
            r = _rect(arte(k) or "", x, y)
            if r and _overlap(r, lim): continue
        # vegetação bloqueia só o tronco; o resto do footprint fica livre para andar
        add(k, x, y, block=block, camada=camada, fp=(1, 1) if veg else None, **kw); feitos += 1
    return feitos

def touceiras(mask, k, raio, sep=None):
    cand = np.argwhere(mask)
    if len(cand) == 0: return mask
    sep = sep or raio * 2.5; cs = []
    for _ in range(k * 80):
        if len(cs) >= k: break
        cx, cy = cand[R.randrange(len(cand))]
        if all(math.hypot(cx - a, cy - b) >= sep for a, b in cs): cs.append((cx, cy))
    out = np.zeros_like(mask)
    for c in cs: out |= circ(c, raio)
    return mask & out

LUZ = {"fogo": [1, .5, .15], "tonel": [1, .45, .12], "gas": [.95, .75, .4], "arco": [.75, .85, 1],
       "vitral": [.55, 1, .45], "vela": [1, .75, .35], "sagrada": [1, .95, .7], "fornalha": [1, .3, .08],
       "podre": [.5, 1, .25], "lua": [.55, .65, .9], "valvula": [.62, .4, 1], "radio": [1, .22, .12]}
def L(tipo, raio): return LUZ[tipo] + [raio]

def linha_de(kind, a, b, passo, orient=None, pula=(), **kw):
    """Fileira de peças de cerca/muro de a até b (passo em m), pulando trechos (portões) e o que já está ocupado."""
    L_ = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L_ / passo))
    for i in range(n + 1):
        x = a[0] + (b[0] - a[0]) * i / n; y = a[1] + (b[1] - a[1]) * i / n
        if any(math.hypot(x - px, y - py) < pr for px, py, pr in pula): continue
        xi, yi = int(x), int(y)
        if not (0 <= xi < N and 0 <= yi < N) or AGUA[xi, yi] or ocup[xi, yi] or BORDA[xi, yi]: continue
        add(kind, x, y, orient=orient, **kw)

# =================================================================== A CIDADE DE SÃO LÁZARO
# A Vigília vive em cima da cidade afogada: a rua de hoje é o telhado de ontem. No meio, a Igreja Matriz,
# enterrada até o coro, com a Praça da Vela na porta. A Linha 7 corta a cidade (Rua dos Trilhos) e para na
# Estação de cúpula de vidro. A Rádio São Lázaro fica no prédio de concreto da beira do precipício.
cx_, cy_ = CITY
# portões da Cerca (onde as estradas saem) e reserva das praças: nada de entulho no meio do caminho
PORTOES = []
for (tx, ty) in [(50, 56), (74, 80), (60, 102), (36, 98), (33, 63), (27, LY), (73, LY)]:
    a = math.atan2(ty - cy_, tx - cx_); PORTOES.append(a)
# a vista da matriz: o que fica na frente dela na tela (câmera 2:1, frente = x - y maior) não pode ser alto
VISTA = (np.abs((XX + YY) - (MATRIZ[0] + MATRIZ[1])) < 12.5) & ((XX - YY) - (MATRIZ[0] - MATRIZ[1]) > -2) & \
        ((XX - YY) - (MATRIZ[0] - MATRIZ[1]) < 26)
RESERVA |= circ(PRACA, 7.5) | ADRO | VISTA
# ---- a matriz: a nave gótica inteira de pé, com os vitrais vermelhos acesos, em evidência no meio da cidade
qx, qy = MATRIZ
LUZ["vitral_rubro"] = [1, .15, .08]
add("capela_sao_lazaro", qx, qy, fp=(8, 12), light=L("vitral_rubro", 9), ponto="matriz_sao_lazaro",
    luzes_extra=[[qx + 4.5, qy - 2] + L("vitral_rubro", 5), [qx + 4.5, qy + 3] + L("vitral_rubro", 5), [qx - 1.5, qy - 6.5] + L("vitral_rubro", 4),
                 [qx - 1, qy - 9.5] + L("sagrada", 8)],
    nota="Igreja Matriz de São Lázaro: a nave que a areia não engoliu; os Sineiros da Vigília tocam o sino e fundem os outros em bala")
add("marcador_npc", qx, qy - 7.4, block=False, invisivel=True, ponto="porta_matriz", objeto="matriz_sao_lazaro", silhueta=False, nota="porta da matriz")
for (dx, dy) in [(-2.4, -6.8), (2.4, -6.8)]:                       # braseiros colados ao portal
    add("braseiro_sagrado", qx + dx, qy + dy, light=L("sagrada", 4.5))
for (dx, dy) in [(-1.6, -7.6), (1.3, -7.9), (2.0, -7.3), (-.8, -8.2), (.4, -7.5)]:
    add("velas_chao", qx + dx, qy + dy, block=False, light=L("vela", 1.6), silhueta=False)
# luz de destaque: dois holofotes de estádio virados braseiro, de fora da vista, apontados para a fachada e os vitrais
add("braseiro_holofote", qx + 14.5, qy - 1.5, light=L("sagrada", 10), nota="holofote da matriz (lado dos vitrais)")
add("braseiro_holofote", qx - 10.5, qy - 13.5, light=L("sagrada", 9), nota="holofote da matriz (lado da praça)")
# o caminho de laje da porta até a Praça da Vela, com lampiões só nas pontas
for (dx, dy) in [(-1.9, -11.6), (1.9, -11.6)]:
    add("lampiao_gas", qx + dx, qy + dy, light=L("gas", 3.5))
# Jardim de São Lázaro: o último jardim do deserto, regado com a água do poço pelos Sineiros. Canteiros cercados de ferro batido;
# baixo na frente e do lado dos vitrais (nada tampa a igreja), ciprestes e oliveira só atrás e do lado da torre
JR = random.Random(77)
def canteiro(b, kinds, passo, grade_lados):
    bx0, by0, bx1, by1 = b
    for lado in grade_lados:                                       # grade de ferro batido na borda do canteiro
        if lado in "nN":
            for x in np.arange(bx0 + .35, bx1, .7): add("grade_ferro_batido", x, by0 + .1 if lado == "n" else by1 - .1, orient="x", block=False, silhueta=False)
        else:
            for y in np.arange(by0 + .35, by1, .7): add("grade_ferro_batido", bx0 + .1 if lado == "w" else bx1 - .1, y, orient="y", block=False, silhueta=False)
    for x in np.arange(bx0 + .9, bx1 - .5, passo):
        for y in np.arange(by0 + .9, by1 - .5, passo):
            add(JR.choice(kinds), x + JR.uniform(-.25, .25), y + JR.uniform(-.25, .25), block=False, silhueta=False)
BAIXAS = ["tapete_flores", "tapete_flores_2", "tapete_flores_3", "moita_florida_3", "moita_florida_3", "planta_mutante"]
canteiro(CANTEIROS[0], BAIXAS, 1.3, "nw")
canteiro(CANTEIROS[1], BAIXAS, 1.3, "ne")
canteiro(CANTEIROS[2], BAIXAS + ["campanula"], 1.55, "e")
canteiro(CANTEIROS[3], ["mirto", "moita_florida", "moita_florida_2", "tapete_flores"], 1.6, "w")
canteiro(CANTEIROS[4], ["mirto", "moita_florida", "tapete_flores_2"], 1.6, "N")
for y in np.arange(88.0, 100.5, 3.0):                               # alameda de ciprestes do lado da torre (atrás na tela)
    add("cipreste" if int(y) % 2 else "cipreste_2", 38.4, y)
for x in (41.5, 46.0, 50.5, 55.0):                                  # e atrás da cabeceira
    add("cipreste_2" if x in (46.0,) else "cipreste", x, 102.2)
add("oliveira", 41.0, 103.5, nota="a oliveira de São Lázaro, plantada no dia em que a areia parou no 4º andar")
add("trelica_videira", 56.4, 101.6, block=False)
add("banco_capela", 44.3, 84.0); add("banco_capela", 52.0, 84.0)
add("poco", 39.0, 84.4, objeto="poco_jardim", nota="poço que rega o jardim")
add("vela_tumulo", 41.8, 101.4, block=False, silhueta=False); add("cruz_madeira", 57.2, 98.5)
add("lapide_cruz_vitoriana", 56.0, 88.0); add("tumulo_vitoriano", 39.6, 100.6)
def por_predio(k, x, y, busca=5, **kw):
    """Põe um prédio o mais perto possível de (x, y) sem invadir rua, praça nem outro prédio."""
    f = fp_de(k)
    for r_ in range(busca + 1):
        cand = sorted({(x + a * .5, y + b * .5) for a in range(-2 * r_, 2 * r_ + 1) for b in range(-2 * r_, 2 * r_ + 1)
                       if max(abs(a), abs(b)) == 2 * r_}, key=lambda c: (c[0] - x) ** 2 + (c[1] - y) ** 2)
        for cx2, cy2 in cand:
            if livre(cx2, cy2, .4, fp=f) and not RESERVA[int(cx2), int(cy2)] and np.hypot(cx2 - cx_, cy2 - cy_) + max(f) / 2 < 20.5:
                r = _rect(arte(k), cx2, cy2)
                if r and _overlap(r, .3): continue
                return add(k, cx2, cy2, **kw)
    print("prédio não coube:", k, x, y); return None
# quadras da cidade: os prédios enterrados dão a silhueta; os barracos de sucata ocupam os telhados entre eles
for k, x, y in [("predio_enterrado", 58, 95), ("casa_ruina", 67, 91), ("predio_enterrado", 31, 84), ("casa_ruina", 40, 62),
                ("predio_enterrado", 62, 62), ("ruina_concreto", 55, 63), ("chamine_enterrada", 69, 65), ("casa_ruina", 37, 100),
                ("torre_relogio_enterrada", 52, 100), ("caixa_dagua_sucata", 30, 76), ("ruina_concreto", 70, 86),
                ("barraco_sucata", 44, 64), ("barraco_sucata", 33, 71), ("barraco_sucata", 41, 89), ("barraco_sucata", 63, 88),
                ("barraco_sucata", 57, 74.5), ("tenda_vigilia", 70, 75), ("chamine_enterrada", 29, 91), ("barraco_sucata", 64, 98),
                ("caixa_dagua_sucata", 46, 66), ("barraco_sucata", 35, 66), ("ruina_concreto", 66, 69)]:
    por_predio(k, x, y, light=L("gas", 4) if k in ("predio_enterrado", "casa_ruina", "barraco_sucata") else None)
# ---- Praça da Vela
px_, py_ = PRACA
add("lampada_arco", px_, py_, light=L("arco", 11), ponto="a_vela")
for a in range(0, 360, 60):                                  # anel de velas e postes em volta da Vela
    ar = math.radians(a + 30)
    lx_, ly_ = px_ + 5.6 * math.cos(ar), py_ + 5.6 * math.sin(ar)
    if VISTA[int(lx_), int(ly_)]: continue                      # o anel abre para a vista da matriz
    add("lampiao_gas", lx_, ly_, light=L("gas", 3.5))
add("poco", px_ - 3.0, py_ - 3.6, objeto="poco_praca")
def praca_primarca(ax, ay, ponto):
    """Gustavo, o Primarca (armazém), em evidência na praça: Arca com as válvulas roxas, caldeira atrás, velas na frente."""
    add("marcador_npc", ax + 1.6, ay - 1.6, block=False, fp=(4, 4), invisivel=True, nota="praça do Primarca (livre)", silhueta=False)
    add("arca_primarca", ax, ay, fp=(2, 1), ponto=ponto, objeto="arca_primarca", light=L("valvula", 6))
    add("caldeira_vapor", ax - 1.6, ay + 1.6, light=L("fornalha", 3))
    for (dx, dy) in [(.4, -1.3), (-.9, -1.6), (1.5, .2)]:
        add("velas_chao", ax + dx, ay + dy, block=False, light=L("vela", 1.5), silhueta=False)
praca_primarca(px_ - 6.0, py_ + 1.0, "arca_primarca")
add("placa_aviso", px_ + 4.4, py_ - 5.2, texto="ENQUANTO HOUVER VELA, NÃO É NOITE.")
# ---- Estação da Linha 7 e o posto da Odete (capitã do bonde)
ex, ey = ESTACAO
add("cupula_estacao", ex, ey + 1, ponto="portao_cupula", light=L("arco", 5))
add("bonde_veleiro", ex - 3, LY + .1, fp=(7, 3), block=True, ponto="plataforma_bondes", light=L("gas", 4))
add("posto_odete", ex + 5.5, ey - .5, ponto="posto_odete", light=L("gas", 4))
add("caixas", ex - 6.5, ey - 2.2); add("barris", ex + 2.6, ey - 3.2); add("sacos_sal", ex - 4.6, ey - 3.0)
add("caixa_dagua_sucata", ex + 6.5, ey + 5.5)
add("guindaste_sucata", ex - 9.5, LY + 3.2, light=L("tonel", 3))
# ---- Rua do Mercado: forja, caldeirão, carrinho e vidraria
add("bancada_ferreiro", 64.6, 87.4, light=L("fornalha", 5), ponto="forja_bigorna"); add("pilha_carvao", 63.0, 88.4); add("tonel_fogo", 66.6, 88.8, light=L("tonel", 4))
add("caldeirao_cardo", 61.2, 83.4, light=L("fogo", 4), ponto="caldeirao_cardo"); add("moita_cardo", 60.0, 84.8, block=False)
add("carrinho_tobias", 66.5, 83.6, ponto="carrinho_tobias", light=L("vela", 2.5))
add("caldeira_vapor", 70.4, 84.4, ponto="forno_vidro", light=L("fornalha", 4))
add("tanque_latao", 72.0, 76.0); add("varal_roupas", 68.6, 86.8)
for x in (63, 71):
    add("lampiao_gas", x, 82.3, light=L("gas", 3.5))
    add("lampiao_gas", x + 3, 78.0, light=L("gas", 3.5))
# ---- enfermaria (Anselmo e Lindalva) e dormitórios
add("tenda_vigilia", 38.5, 76, ponto="barraca_anselmo", light=L("vela", 3))
add("bau_comum", 36.6, 73.6, bau="bau_barraca_anselmo", tipo_bau="trancado")
add("tenda_vigilia", 39.5, 82.5, ponto="enfermaria_lindalva", light=L("vela", 3))
add("varal_roupas", 35, 80); add("tonel_fogo", 42.5, 74, light=L("tonel", 4))
# ---- Rádio São Lázaro (Isaura): o prédio de concreto na beira do precipício, antena no telhado
rx_, ry_ = RADIO
add("predio_concreto", rx_, ry_ + 1, ponto="radio_sao_lazaro", light=L("gas", 5),
    luzes_extra=[[rx_ + 2, ry_ + 4] + L("radio", 3)], nota="Rádio São Lázaro: Isaura transmite do 5º andar, que hoje é o térreo")
add("antena_radio", rx_ - 1.5, ry_ + 5.5, pendente=True, light=L("radio", 2.5), nota="mastro de rádio com luz vermelha (arte nova)")
add("tambores_radioativos", rx_ + 4.6, ry_ - 2.2); add("lampiao_gas", rx_ + 4.2, ry_ - 3.6, light=L("gas", 3.5))
# ---- a Cerca (paliçada) com torres nos portões
for k in range(int(2 * math.pi * 23 / 1.0)):
    a = k / (2 * math.pi * 23 / 1.0) * 2 * math.pi
    if any(abs(math.atan2(math.sin(a - g), math.cos(a - g))) < (.075 if g in PORTOES[5:] else .09) for g in PORTOES): continue
    x, y = cx_ + 23 * math.cos(a), cy_ + 23 * math.sin(a)
    xi, yi = int(x), int(y)
    if PRECIPICIO[max(0, xi - 1):xi + 2, yi].any(): continue
    add("palicada", x, y, orient="y" if abs(math.cos(a)) > .7 else "x", silhueta=False)
for g in PORTOES[:3]:
    for s_ in (-.16, .16):
        x, y = cx_ + 24.2 * math.cos(g + s_), cy_ + 24.2 * math.sin(g + s_)
        if not PRECIPICIO[int(x), int(y)]: add("torre_vigia", x, y, light=L("arco", 6))
add("marcador_npc", cx_ + 24.6 * math.cos(PORTOES[1]), cy_ + 24.6 * math.sin(PORTOES[1]) - 2, block=False, invisivel=True,
    ponto="costelas_cupula", nota="Damião vigia o portão leste", silhueta=False)
# ---- a cidade afogada: prédios enterrados formando as quadras (o que dá a silhueta da cidade)
CID = ZCITY & ~ROAD & ~circ(PRACA, 7.5) & ~ADRO & ~VISTA & (np.hypot(XX - cx_, YY - cy_) < 21.5)
espalhar(CID, ["caixas", "barris", "sacos_areia", "sacos_sal", "carroca_quebrada", "tonel_fogo"], 38, sep=1.0, light=None)
espalhar(CID, ["varal_roupas"], 6, sep=2.5)
espalhar(CID, ["lampiao_gas", "poste_gas"], 12, sep=3.5, light=L("gas", 3.5))
espalhar(CID, ["flor_absinto_lata"], 18, sep=1.2, block=False, pendente=True, luz_fraca=[.45, 1, .75, 1.2])
espalhar(CID, ["janela_na_areia", "placa_rua_enterrada", "chamine_enterrada"], 8, sep=2)
espalhar(CID & (NZ > .5), ["entulho", "folhas_papeis"], 30, sep=.8, block=False, camada="chao")
for x in (30, 40, 50, 60, 70):                                # postes da Rua dos Trilhos
    add("poste_gas", x + .5, LY - 2.2, light=L("gas", 3.5))
# ---- trilhos (peças do kit a cada 0,707 m) e o bonde
def trilhos(curva, passo=.707):
    ult = None
    for i, (x, y) in enumerate(curva[::max(1, int(passo / .25))]):
        xi, yi = int(x), int(y)
        if not (0 <= xi < N and 0 <= yi < N) or PRECIPICIO[xi, yi]: continue
        if P1[xi, yi]: continue
        o = "x" if ult is None or abs(x - ult[0]) >= abs(y - ult[1]) else "y"
        if ult is not None: add("trilho_bonde", x, y, block=False, camada="chao", orient=o, silhueta=False)
        ult = (x, y)
trilhos(LINHA7); trilhos(RAMAL)

# =================================================================== PÁTIO DOS BONDES (2-4)
# Onde a companhia largava os bondes quebrados. A maré de areia cobriu metade; os corvos fazem ninho nos mastros.
PAT_OK = ZPATIO & ~ROAD & ~AGUA
for (x, y) in [(20, 36), (31, 33), (16, 50), (34, 50), (24, 30)]:
    if livre(x, y, .3, fp=(6, 3)): add("bonde_queimado", x, y, ponto="bonde_patio")
add("bonde_veleiro", 22.5, 46.2, fp=(7, 3), nota="bonde-veleiro abandonado no ramal, vela rasgada")
add("poste_ninho_gigante", 30, 42, ponto="poste_torto", objeto="ninhos_corvo")
add("bau_comum", 31.0, 41.0, bau="bau_tobias_1", block=False)
espalhar(PAT_OK, ["poste_mastro", "poste_tombado", "poste_ninho"], 9, sep=3)
espalhar(PAT_OK, ["trilho_retorcido", "carroca_quebrada", "caixas", "barris", "entulho"], 22, sep=1.6)
espalhar(PAT_OK, ["mato_seco", "mato_seco_2", "arbusto_seco"], 26, sep=1.2, block=False)
espalhar(PAT_OK, ["duna_areia", "duna_areia_2"], 7, sep=2.5, block=False)

# =================================================================== CAMPOS DE CINZA (1-3; Marco do Corte 7-9)
CAMPO_OK = ZCAMPOS & ~ROAD
add("bonde_queimado", TRAM[0], TRAM[1], ponto="marco_do_corte", objeto="marco_do_corte", light=L("fogo", 3))
add("cratera_corte", TRAM[0] + 3, TRAM[1] - 3.5, camada="chao", block=False)
add("pilha_mortos", TRAM[0] - 3.5, TRAM[1] + 2.5); add("rastro_arrasto", TRAM[0] + 4.5, TRAM[1] - 5, camada="chao", block=False)
add("trilho_retorcido", TRAM[0] - 4, TRAM[1] - 3)
for i in range(4):                                        # estandartes caídos em volta do marco (linha E)
    a = i / 4 * 2 * math.pi + .4
    add("estandarte_rasgado", TRAM[0] + math.cos(a) * 7.5, TRAM[1] + math.sin(a) * 7.5, ponto="estandartes_caidos", objeto="estandartes_caidos")
add("poco", 82, 98, ponto="poco_seco", objeto="poco_seco")
CAMPO_PENAS = (96, 90)
add("asa_anjo_caida", *CAMPO_PENAS, ponto="campo_penas")
espalhar(circ(CAMPO_PENAS, 4) & CAMPO_OK, ["penas_espalhadas"], 10, sep=.8, block=False, camada="chao")
NINHOS = [(84, 66), (98, 82), (80, 92), (100, 96), (86, 104)]
for (x, y) in NINHOS:
    add("poste_ninho", x, y, objeto="ninhos_corvo")
for (x, y) in [(80, 72), (83, 75), (87, 85), (82, 88), (95, 70), (99, 66), (79, 100), (90, 100)]:
    if livre(x, y, .6): add("espantalho_arame", x, y)
BATALHA = touceiras(CAMPO_OK, 7, 3.5, sep=11)
espalhar(BATALHA, ["cratera_cinza"], 8, sep=3, block=False)
espalhar(BATALHA, ["soldado_morto", "soldado_morto", "elmo_espada_fincada"], 30, sep=1.2, block=False, lim=.25)
espalhar(BATALHA, ["estandarte_rasgado"], 5, sep=6)
espalhar(CAMPO_OK, ["carroca_quebrada", "cerca_arame_torta"], 10, sep=4)
espalhar(CAMPO_OK, ["vidro_estilhacos"], 60, sep=.9, block=False, camada="chao", dens=NZ ** 1.5 * 1.6)
espalhar(CAMPO_OK, ["arvore_morta", "arvore_morta_2"], 14, sep=4, dens=NZ3, veg=True)
espalhar(CAMPO_OK, ["mato_seco", "mato_seco_2"], 50, sep=1.2, block=False, dens=NZ2)
espalhar(CAMPO_OK, ["ossos_espalhados", "poca_sangue"], 18, sep=1.2, block=False, camada="chao")
espalhar(CAMPO_OK, ["poste_mastro", "poste_telegrafo"], 6, sep=9)

# =================================================================== A VALA (3-5)
VALA_OK = ZVALA & ~ROAD & ~AGUA
for (x, y) in [(96, 22), (103, 20), (94, 33), (106, 33), (100, 28)]:
    add("vala_aberta", x, y, objeto="vala_aberta")
add("toca_caes", 99, 15.5, ponto="toca_matilha")
espalhar(touceiras(VALA_OK & ~BREJO, 4, 2.5), ["estacas_cerca", "cruz_madeira"], 12, sep=1.4)
espalhar(BREJO & ~ROAD & ~AGUA, ["juncos", "mato_seco"], 50, sep=.8, block=False, water_ok=True)
espalhar(BREJO & ~ROAD & ~AGUA, ["poca_toxica"], 8, sep=3, block=False, camada="chao", light=[.4, 1, .3, 1.6])
espalhar(VALA_OK, ["carroca_quebrada", "entulho", "ossada_animal"], 10, sep=3)
espalhar(VALA_OK, ["ossos_espalhados", "poca_sangue"], 14, sep=1, block=False, camada="chao")
add("gaiola_suspensa", 90, 26, light=L("podre", 3))
add("barco_afundado", 117, 26, water_ok=True)
add("bau_comum", 116, 24.6, bau="bau_mundo_barco", tipo_bau="comum", block=False)
add("tonel_fogo", 88, 30, light=L("tonel", 4))

# =================================================================== BAIRRO AFOGADO (3-5)
# Os telhados da cidade velha saindo da duna; o relógio da prefeitura; a antena de repetição da Rádio.
BAI_OK = ZBAIRRO & ~ROAD & ~PRECIPICIO
for (k, x, y) in [("predio_enterrado", 14, 112), ("casa_ruina", 26, 140), ("predio_enterrado", 12, 140), ("casa_ruina", 30, 118),
                  ("ruina_concreto", 10, 125), ("chamine_enterrada", 28, 132), ("torre_tombada", 16, 148)]:
    if livre(x, y, .2, fp=fp_de(k)): add(k, x, y, light=L("vela", 3) if k == "predio_enterrado" else None)
    else: print("não coube no bairro:", k, x, y)
add("torre_relogio_enterrada", 22, 120, ponto="relogio_afogado", light=L("vela", 3))
add("janela_na_areia", 24.5, 117.5, block=False, ponto="sotao_afogado", leva_para="sotao (interior opcional)")
add("bau_comum", 25.5, 116.8, bau="bau_mundo_sotao", tipo_bau="comum", block=False)
add("antena_radio", 13, 132, pendente=True, ponto="antena_radio", objeto="antena_radio", light=L("radio", 2.5), nota="antena de repetição da Rádio (linha D)")
add("barraco_sucata", 32, 110, ponto="loja_corvina", light=L("gas", 3)); add("varal_lanternas", 33.5, 107.6, pendente=True, light=L("vela", 2.5))
espalhar(BAI_OK, ["predio_enterrado", "casa_ruina"], 3, sep=2)
espalhar(BAI_OK, ["chamine_enterrada", "janela_na_areia", "placa_rua_enterrada", "ruina_concreto"], 18, sep=1.8)
espalhar(BAI_OK, ["entulho", "caixas", "carroca_quebrada"], 18, sep=1.4)
espalhar(BAI_OK, ["duna_ondulacao", "duna_areia"], 10, sep=2.5, block=False)
espalhar(BAI_OK, ["mato_seco", "arbusto_seco"], 22, sep=1.2, block=False)

# =================================================================== CEMITÉRIO DE SÃO LÁZARO (4-7)
CEM_OK = ZCEM & ~ROAD
ex, ey = CEM
for k in range(int(2 * math.pi * 19 / 1.0)):                    # gradil de ferro batido, portões nas trilhas
    a = k / (2 * math.pi * 19) * 2 * math.pi
    x, y = ex + 21.2 * math.cos(a), ey + 15.2 * math.sin(a)
    xi, yi = int(x), int(y)
    if not (0 <= xi < N and 0 <= yi < N) or AGUA[xi, yi] or MARGEM[xi, yi] or D_TRILHA[xi, yi] < 1.8: continue
    add("grade_ferro_batido", x, y, orient="x" if abs(math.sin(a)) > .7 else "y", silhueta=False)
add("casa_coveiro", ex - 6.5, ey - 3.5, ponto="casa_simao", light=L("vela", 4))
add("torre_sino", ex - 1.5, ey + 9.5, ponto="torre_sino", objeto="torre_sino")
add("estatua_anjo_quebrada", ex + 9, ey + 6, ponto="anjo_sem_cabeca")
add("bau_comum", ex + 9.8, ey + 4.6, bau="bau_tobias_2", block=False)
add("mausoleu", ex - 12, ey + 4, light=L("vela", 2.5)); add("mausoleu", ex + 6, ey - 8); add("mausoleu", ex - 4, ey + 11.5)
add("lapide_cruz_celta", ex - 13, ey - 4, ponto="tumulo_cardo", objeto="tumulo_cardo")
espalhar(ellip((ex - 13, ey - 4.5), 3.5, 3) & ~ROAD, ["moita_cardo"], 9, sep=.8, block=False)
add("sepulcro_primeiro", ex - 9.5, ey - 7.5, ponto="sepulcro_primeiro", objeto="sepulcro_primeiro", light=L("vela", 2))
add("laje_rolada", ex - 7.8, ey - 8.6)
espalhar(CEM_OK, ["cova_aberta"], 8, sep=1.2, tries=400, block=False, objeto="covas_abertas")
espalhar(CEM_OK, ["corpo_lacrado"], 6, sep=1, tries=400, block=False, objeto="corpo_lacrado")
SPOTS_PRE = [(88, 124, 10), (66, 134, 9)]                       # clareiras dos spots do cemitério (reservadas)
for sx, sy, sr in SPOTS_PRE: RESERVA |= circ((sx, sy), sr * .8)
for row in range(-7, 8):                                        # fileiras de túmulos com falhas
    for col in range(-9, 10):
        x = ex + col * 1.7 + R.uniform(-.25, .25); y = ey + row * 1.9 + R.uniform(-.2, .2)
        xi, yi = int(x), int(y)
        if not (0 <= xi < N and 0 <= yi < N) or not ZCEM[xi, yi] or R.random() < (.45 if RESERVA[xi, yi] else .2): continue
        if livre(x, y, .3):
            k = R.choice(["lapide", "lapide_vitoriana", "cruz_madeira", "lapide_cruz_celta", "lapide_cruz_vitoriana", "tumulo_aberto", "lapide_obelisco"])
            r = _rect(arte(k), x, y)
            if r and _overlap(r, .35): continue
            add(k, x, y, block=k in ("lapide_obelisco", "tumulo_aberto"))
espalhar(CEM_OK, ["arvore_morta", "arvore_morta_2"], 8, sep=3, veg=True)
espalhar(CEM_OK, ["vela_tumulo"], 26, sep=.4, block=False, light=L("vela", 1.2), lim=.4)
espalhar(CEM_OK, ["mar_de_lapides"], 12, sep=.5, block=False, lim=.2)
espalhar(CEM_OK, ["folhas_papeis", "ossos_espalhados"], 10, sep=1.5, block=False, camada="chao")
for (x, y) in spline([(74, 115), (72, 122), (70, 130), (72, 137)])[::14]:
    add("lanterna_procissao", x + 1.4, y, light=L("vela", 2.5))

# =================================================================== MATA DOS CARDOS (transição)
CARD_OK = ZCARDOS & ~ROAD & ~AGUA
espalhar(CARD_OK, ["moita_cardo", "moita_cardo", "arbusto_seco"], 60, sep=.7, block=False, lim=.3)
espalhar(CARD_OK, ["arvore_morta", "arvore_morta_2"], 6, sep=2.6, veg=True)

# =================================================================== RIO AMARGO (o oásis)
MARG_OK = MARGEM & ~ROAD & ~BORDA
espalhar(touceiras(MARG_OK, 9, 2.6, sep=16), ["juncos", "mato_seco", "juncos"], 60, sep=.8, block=False, water_ok=True, lim=.3)
for (x, y) in [(121.5, 34.5), (123, 36.5), (122, 38), (124, 35), (121, 37)]:
    add("pedras_rio", x, y, block=False, camada="chao")
# oásis (escolha do Jefin): canteiros de flor-de-absinto nos remansos, a única coisa viva e bonita do deserto
espalhar(touceiras(MARG_OK | (LEITO & (D_RIO < HALF + 2.5)), 12, 2.2, sep=13), ["flor_absinto"], 90, sep=.5, block=False, water_ok=True, lim=.4,
         pendente=True, luz_fraca=[.45, 1, .75, 1.3])
add("ponte_ferro_bonde", 116, LY, block=False, ponto="ponte_bonde", comprimento=20, silhueta=False)
add("ponte_madeira", 107.5, 113, block=False, ponto="ponte_enforcados", comprimento=17, orient="x", silhueta=False)
for x in (102, 106, 110, 114):
    add("forca_ponte", x, 115, light=L("podre", 1.5) if x == 110 else None)
add("moinho_ruina", 96, 126, ponto="moinho")
add("roda_dagua", 101.2, 124.6, water_ok=True)
add("bau_raro", 94.6, 122.8, bau="bau_mundo_moinho", tipo_bau="raro")
add("cano_esgoto", 128.5, 44.5, ponto="esgoto_abatedouro", vaza="sebo_sangue")
add("cano_esgoto", 127.5, 49.0, vaza="sebo_sangue")
add("sumidouro", 153, 8.5, block=False, ponto="sumidouro", nota="o rio some girando na areia")

# =================================================================== ACAMPAMENTO DOS DESERTORES (6-9)
dx_, dy_ = 118, 100
for (ox, oy, k) in [(0, 0, "tenda_demonio"), (3, -2, "braseiro_ferro"), (-3, 2, "estandarte_rasgado"), (2, 3, "trono_sucata"), (-2.5, -3, "caixas"), (4, 2.5, "gaiola_suspensa")]:
    add(k, dx_ + ox, dy_ + oy, ponto="acampamento_desertores" if k == "tenda_demonio" else None, light=L("fornalha", 5) if k == "braseiro_ferro" else None)
for i, (x, y) in enumerate([(110, 104), (111, 96), (112, 90), (109, 108), (111.5, 100)]):
    add("poca_toxica", x, y, ponto="pocas_amargas", camada="chao", light=[.4, 1, .3, 2], objeto="pocas_amargas")

# =================================================================== BOSQUE DAS VIÚVAS (5-7) e VILA MILITAR (8-10)
WOOD_OK = ZWOOD & ~ROAD & ~AGUA & ~BORDA
RESERVA |= circ((128, 122), 8) | circ((148, 138), 7.5)
DENS_W = np.clip(NZ * 1.3 - .1, 0, 1)
espalhar(WOOD_OK, ["arvore_morta", "arvore_morta_2", "arvore_morta_grande", "planta_mutante"], 120, sep=1.5, dens=DENS_W, veg=True, lim=.16)
espalhar(WOOD_OK, ["arbusto_seco", "arbusto_seco_2", "mato_seco"], 110, sep=.9, block=False, lim=.25)
espalhar(WOOD_OK, ["poca_toxica"], 14, sep=.3, tries=200, block=False, camada="chao", light=[.4, 1, .3, 1.6])
espalhar(WOOD_OK, ["cogumelos_palidos"], 30, sep=.3, tries=200, block=False, light=[.55, .8, .6, 1.0], lim=.3)
espalhar(WOOD_OK, ["tronco_margem", "toco_arvore"], 18, sep=2)
add("arvore_enforcados", 136, 128, ponto="arvore_viuvas", light=L("podre", 3))
add("bau_raro", 138.6, 126.6, bau="bau_mundo_viuvas", tipo_bau="raro")
add("capelinha_beira", 124, 112.5, light=L("vela", 3))
VIL_OK = ZVILA & ~ROAD
for (k, x, y) in [("casa_ruina", 140, 144), ("casa_ruina", 154, 132), ("ruina_concreto", 140, 132), ("predio_concreto", 152, 146)]:
    if livre(x, y, .1, fp=fp_de(k)): add(k, x, y, ponto="vila_militar", light=L("vela", 2.5))
    else: print("vila não coube:", k, x, y)
add("varal_roupas", 147, 131); add("placa_radiacao", 141, 138); add("tambores_radioativos", 144, 129)
espalhar(VIL_OK, ["cerca_arame_torta", "barricada_sacos", "entulho", "carroca_quebrada"], 14, sep=1.5)
espalhar(VIL_OK, ["mato_seco", "arbusto_seco"], 18, sep=1, block=False)

# =================================================================== CHIQUEIROS (4-6)
ch_x, ch_y = PIG
for (ox, oy, w, h) in [(-6, -4, 6, 5), (2, -5, 6, 5), (-2, 3, 7, 4)]:
    x0, y0 = ch_x + ox, ch_y + oy
    linha_de("cerca_chiqueiro", (x0, y0), (x0 + w, y0), 1.0, orient="x", pula=[(x0 + w / 2, y0, 1.1)], silhueta=False)
    linha_de("cerca_chiqueiro", (x0, y0 + h), (x0 + w, y0 + h), 1.0, orient="x", silhueta=False)
    linha_de("cerca_chiqueiro", (x0, y0 + 1), (x0, y0 + h - 1), 1.0, orient="y", silhueta=False)
    linha_de("cerca_chiqueiro", (x0 + w, y0 + 1), (x0 + w, y0 + h - 1), 1.0, orient="y", silhueta=False)
espalhar(ZPIG & ~ROAD, ["cocho", "lama_porcos"], 14, sep=1.2, block=False)
espalhar(ZPIG & ~ROAD, ["poca_sangue", "ossos_espalhados"], 10, sep=1.2, block=False, camada="chao")
add("barraco_sucata", ch_x + 8, ch_y - 7)
add("bau_comum", ch_x + 9.8, ch_y - 4.8, bau="bau_mundo_chiqueiro", tipo_bau="comum")

# =================================================================== ABATEDOURO CARNIÇA (7-9) e a porta da Cripta
ax_, ay_ = ABAT
add("frigorifico_enterrado", ax_ + 3, ay_ + 3, ponto="escritorio_capataz", light=L("fornalha", 8),
    luzes_extra=[[ax_ - 2, ay_ + 7] + L("fornalha", 5), [ax_ + 7, ay_ - 2] + L("fogo", 4)], nota="Abatedouro Carniça, enterrado até o 2º andar")
add("entrada_cripta", ax_ - 4, ay_ - 4.5, ponto="porta_ganchos", objeto="porta_ganchos", light=L("fornalha", 4))
add("tanque_sebo", ax_ + 10, ay_ - 4, ponto="tanque_sebo"); add("bau_raro", ax_ + 11.6, ay_ - 2.6, bau="bau_tobias_3", tipo_bau="trancado", block=False)
add("tanque_sebo", ax_ + 11, ay_ + 1.5)
for i in range(6): add("ganchos_carne", ax_ - 9, ay_ - 7 + i * 2)
for (x, y) in [(ax_ - 8, ay_ - 9), (ax_ + 4, ay_ - 9), (ax_ + 12, ay_ + 8), (ax_ - 11, ay_ + 6)]:
    add("tonel_fogo", x, y, light=L("tonel", 4.5))
add("carrinho_carne", ax_ - 6, ay_ - 2); add("mesa_acougue_rua", ax_ - 1, ay_ - 8); add("moedor_vapor", ax_ + 6, ay_ - 9.5, light=L("fornalha", 3))
espalhar(ZABAT & ~ROAD, ["poca_sangue", "poca_sangue_rastro", "ralo_ferro_chao"], 14, sep=1.4, block=False, camada="chao")
espalhar(ZABAT & ~ROAD, ["barris", "caixas", "carroca_quebrada", "sacos_sal"], 10, sep=2)
linha_de("muro_tijolo", (ax_ - 14, ay_ + 13), (ax_ + 12, ay_ + 13), 1.0, orient="x", pula=[(ax_ - 3, ay_ + 13, 2)], silhueta=False)
add("placa_aviso", 131, 56, texto="CARNIÇA & FILHOS · CARNE PARA A PARÓQUIA")
add("gaiola_suspensa", 129, 52, light=L("podre", 2.5))

# =================================================================== DESERTO ABERTO ENTRE AS ZONAS
OCUPADAS = ZCITY | ZCAMPOS | ZPATIO | ZVALA | ZBAIRRO | ZCEM | ZCARDOS | ZWOOD | ZPIG | ZABAT | ZVILA | ZDES
GERAL = np.isin(T, ["a", "u", "e", "s"]) & ~ROAD & ~BORDA & ~OCUPADAS & ~TEMPESTADE
VERDE = GERAL & OASIS
SECO = GERAL & ~OASIS
espalhar(VERDE, ["arvore_morta", "arvore_morta_grande", "planta_mutante"], 50, sep=2.4, dens=np.clip(NZ3 * 1.4 - .1, 0, 1), veg=True)
espalhar(VERDE, ["arbusto_seco", "mato_seco", "moita_cardo", "planta_mutante"], 240, sep=.9, block=False, dens=NZ2, lim=.25)
espalhar(SECO, ["arvore_morta", "arvore_morta_2"], 44, sep=5, dens=NZ3, veg=True)
espalhar(SECO, ["duna_ondulacao", "duna_ondulacao_2", "duna_ondulacao_3", "duna_areia", "duna_areia_2"], 130, sep=3, block=False)
espalhar(SECO, ["mato_seco", "mato_seco_2", "arbusto_seco", "arbusto_seco_2", "cacto_seco"], 260, sep=1.3, block=False, dens=NZ2)
espalhar(SECO, ["predio_enterrado", "casa_ruina"], 6, sep=5)
espalhar(touceiras(SECO, 9, 3, sep=14), ["chamine_enterrada", "carroca_quebrada", "ossada_animal", "placa_rua_enterrada"], 22, sep=2)
espalhar(SECO, ["ossada_animal", "tambores_radioativos", "placa_radiacao", "vidro_estilhacos"], 30, sep=3)
espalhar((T == "s") & ~ROAD, ["ossada_animal", "pedras_rio", "barco_afundado"], 10, sep=6)
# pontos de interesse no deserto aberto (exploração, baús de mundo, histórias sem mob)
def poi(lista):
    for k, x, y, *kw in lista:
        kw = kw[0] if kw else {}
        if livre(x, y, .2, fp=fp_de(k)): add(k, x, y, **kw)
        else:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1.5, 1.5), (-1.5, -1.5)):
                if livre(x + dx, y + dy, .2, fp=fp_de(k)): add(k, x + dx, y + dy, **kw); break
# Caravana Soterrada: os romeiros que vinham para a festa do padroeiro na noite da 3ª trombeta
poi([("carroca_quebrada", 38, 17), ("carroca_quebrada", 42, 15), ("carroca_quebrada", 34, 20), ("ossada_animal", 40, 19), ("ossada_viajante", 44, 18),
     ("estandarte_rasgado", 37, 14), ("andor_padroeiro", 46, 14, {"nota": "andor de romaria quebrado"}), ("duna_areia", 32, 15), ("fogueira", 41, 21, {"light": L("fogo", 3)})])
add("bau_comum", 43.2, 16.4, bau="bau_mundo_caravana", tipo_bau="comum", block=False)
# Escola Afogada: o grupo escolar de São Lázaro, só o 2º andar fora da areia
poi([("casa_ruina", 78, 42, {"ponto": "escola_afogada", "light": L("vela", 2)}), ("ruina_concreto", 70, 45), ("placa_rua_enterrada", 74, 39), ("espantalho_arame", 82, 47),
     ("carroca_quebrada", 84, 40), ("poste_tombado", 72, 38)])
# Capela dos Romeiros: oratório no caminho do bairro, cheio de ex-votos
poi([("capelinha_beira", 44, 130, {"light": L("vela", 3), "ponto": "capela_romeiros"}), ("cruz_madeira", 41, 128), ("cruz_madeira", 46, 133), ("velas_chao", 43, 127.5, {"block": False, "light": L("vela", 1.5)}),
     ("arvore_morta_grande", 49, 128), ("lapide", 40, 131)])
# Barcos do Sumidouro: barcos que desceram o rio e encalharam onde a água some
poi([("barco_afundado", 146, 18), ("barco_afundado", 150, 22), ("ossada_gigante", 140, 12), ("poste_mastro", 144, 24)])
# Torre caída da Linha do Impasse, no meio do mar de dunas
poi([("torre_tombada", 152, 60), ("ossada_viajante", 147, 63), ("estandarte_rasgado", 149, 57)])
# postes de telégrafo ao longo da Estrada do Sul e da Estrada do Leste
for (x, y) in spline([(50, 57), (52, 46), (56, 34), (60, 20), (63, 6)])[::40][1:]:
    add("poste_telegrafo", x + 2.6, y)
for (x, y) in spline([(78, 79), (86, 78), (96, 75), (104, 71)])[::36][1:]:
    add("poste_gas", x, y + 2.2, light=L("gas", 3.5))

# =================================================================== LIMITES
BEIRA = ndimage.binary_dilation(PRECIPICIO, iterations=2) & ~PRECIPICIO
for (x, y) in np.argwhere(BEIRA)[::3]:
    if livre(x + .5, y + .5, .3, road_ok=True) and R.random() < .45:
        add("corda_guarda", x + .5, y + .5, orient="y", silhueta=False)
add("trilhos_no_abismo", 4.5, LY, ponto="fim_da_linha7", block=False)
add("ponte_rompida", 6, 104, block=False)
for (x, y, t) in [(9, 60, "A CIDADE VELHA CAIU AQUI"), (10, 96, "NÃO DESÇA. ELES AINDA CHAMAM.")]:
    add("placa_aviso", x, y, texto=t)
for x in range(6, N - 8, 3):
    yy = N - 13 + NZ2[min(x, N - 1), N - 13] * 4
    if livre(x, yy, .5, road_ok=True) and R.random() < .55:
        add(R.choice(["cerca_arame_torta", "barricada_sacos", "estacas_cerca"]), x, yy, orient="x", silhueta=False)
for x in (24, 60, 96, 132):
    if livre(x, N - 7.5, .2, road_ok=True, fp=(3, 3)): add("torre_vigia_enterrada", x, N - 7.5, light=L("arco", 3))
espalhar(TEMPESTADE & ~AGUA, ["ossada_animal", "ossada_viajante", "estandarte_rasgado"], 16, sep=4, block=False, road_ok=True)
for (x, y) in [(36, N - 15), (76, N - 16), (106, N - 15)]:
    add("placa_aviso", x, y, texto="VOLTE. A AREIA COME.")
espalhar(DUNAS | DUNAS_SUL, ["poste_mastro", "ossada_gigante", "poste_telegrafo"], 22, sep=6, block=False, road_ok=True, water_ok=True)
add("placa_aviso", 66, 5.5, texto="ESTRADA DO SUL")

# =================================================================== SPOTS DE FARM (estilo MU: 12 mobs, respawn 14 s)
# Ids das missões (farmar_spot) mantidos; 3 spots novos (cemiterio_bondes, alameda_ciprestes, casas_da_vila).
SPOTS = [
 dict(id="covas_rasas", nome="Covas Rasas", nivel=[1, 3], zona="campos_cinza", x=88, y=92, raio=10, respawn_s=14,
      mobs=[{"kind": "carnical", "nivel": [1, 2], "qtd": 6, "temperamento": "neutro"}, {"kind": "corvo_de_cinza", "nivel": [2, 3], "qtd": 6, "temperamento": "neutro"}],
      lore="Carniçais revirando os mortos da Grande Batalha no vidro derretido; os corvos esperam a vez. Ninguém aqui ataca primeiro.",
      missao="v01 Pavio Curto, v02 (Odete): primeiros abates"),
 dict(id="cemiterio_bondes", nome="Cemitério de Bondes", nivel=[2, 4], zona="patio_bondes", x=26, y=40, raio=10, respawn_s=14, novo=True,
      mobs=[{"kind": "corvo_de_cinza", "nivel": [2, 3], "qtd": 6, "temperamento": "territorial", "ancora": "poste_torto", "raio_territorio": 4},
            {"kind": "carnical", "nivel": [3, 4], "qtd": 6, "temperamento": "neutro"}],
      lore="Os bondes que a companhia largou no ramal morto. Os corvos fazem ninho nos mastros e defendem o poste torto; os Carniçais dormem dentro dos vagões.",
      missao="vc02 Cobre dos Bondes (Odete)"),
 dict(id="telhados_dos_corvos", nome="Telhados dos Corvos", nivel=[3, 5], zona="bairro_afogado", x=20, y=128, raio=9,
      mobs=[{"kind": "cao_de_vala", "nivel": [3, 5], "qtd": 6, "temperamento": "territorial", "ancora": "toca_caes", "raio_territorio": 4},
            {"kind": "corvo_de_cinza", "nivel": [3, 4], "qtd": 6, "temperamento": "neutro"}],
      lore="A matilha caça ratos entre os telhados enterrados, perto da antena de repetição da Rádio; os corvos ficam nas chaminés.",
      missao="linha D: d02 Antena no Telhado"),
 dict(id="fosso_dos_caes", nome="Fosso dos Cães", nivel=[3, 5], zona="vala_comum", x=100, y=26, raio=10,
      mobs=[{"kind": "cao_de_vala", "nivel": [3, 5], "qtd": 9, "temperamento": "territorial", "ancora": "toca_caes", "raio_territorio": 4},
            {"kind": "carnical", "nivel": [3, 4], "qtd": 3, "temperamento": "neutro"}],
      lore="O bueiro desabado onde a matilha dorme. De dia ela defende a toca; à noite caça.",
      missao="v03 Os Cães da Vala"),
 dict(id="procissao_parada", nome="Procissão Parada", nivel=[4, 6], zona="cemiterio_sao_lazaro", x=88, y=124, raio=10,
      mobs=[{"kind": "nao_julgado", "nivel": [4, 6], "qtd": 12, "temperamento": "neutro"}],
      lore="A fila de Não-Julgados parada diante da torre do sino, com o andor no meio, esperando o Juízo. Só revidam: o spot feito para o leque.",
      missao="v04 Lacres Inteiros, f02 O Rosto do Padroeiro"),
 dict(id="chiqueiro_do_carnica", nome="Chiqueiro do Carniça", nivel=[4, 6], zona="chiqueiros", x=142, y=84, raio=9,
      mobs=[{"kind": "porco_pestilento", "nivel": [4, 6], "qtd": 12, "temperamento": "neutro"}],
      lore="Os porcos gordos fuçam a lama atrás das cercas de chapa; o rastro de arrasto passa por aqui.",
      missao="linha E: o rastro de arrasto"),
 dict(id="alameda_ciprestes", nome="Alameda dos Ciprestes", nivel=[5, 7], zona="cemiterio_sao_lazaro", x=66, y=134, raio=9, novo=True,
      mobs=[{"kind": "nao_julgado", "nivel": [5, 7], "qtd": 9, "temperamento": "neutro"}, {"kind": "corvo_de_cinza_carnica", "substituto": "corvo_de_cinza", "nivel": [6, 7], "qtd": 3, "temperamento": "territorial", "ancora": "mausoleu", "raio_territorio": 4}],
      lore="Os mortos mais antigos da paróquia, nas covas de família do alto do morro. Os corvos-carniça guardam o mausoléu onde fazem ninho.",
      missao="vc04 Os Nomes do Alto (Simão)"),
 dict(id="margem_das_viuvas", nome="Margem das Viúvas", nivel=[5, 7], zona="bosque_viuvas", x=128, y=122, raio=9,
      mobs=[{"kind": "nao_julgado", "nivel": [5, 6], "qtd": 8, "temperamento": "neutro"},
            {"kind": "sangrador_apostata", "substituto": "nao_julgado", "nivel": [6, 7], "qtd": 4, "temperamento": "territorial", "ancora": "arvore_viuvas", "raio_territorio": 5}],
      lore="As viúvas da Grande Batalha andam entre as árvores mortas; uma célula de cultistas apóstatas se esconde na Árvore dos Enforcados.",
      missao="linha D: a vila militar do silo"),
 dict(id="acampamento_desertores", nome="Acampamento dos Desertores", nivel=[6, 9], zona="rio_amargo", x=118, y=100, raio=9,
      mobs=[{"kind": "desertor_legiao", "substituto": "acougueiro_oco", "nivel": [6, 9], "qtd": 8, "temperamento": "territorial", "ancora": "tenda_demonio", "raio_territorio": 5},
            {"kind": "cao_de_vala", "nivel": [6, 8], "qtd": 4, "temperamento": "neutro"}],
      lore="Demônios da Legião Blasfema que largaram a bandeira quando o general sumiu, acampados na margem do oásis, cobrando pedágio da água.",
      missao="e02 Desertores, d04 O Que a Água Lembra"),
 dict(id="marco_do_corte", nome="Marco do Corte", nivel=[7, 9], zona="campos_cinza", x=92, y=58, raio=9,
      mobs=[{"kind": "desertor_legiao", "substituto": "acougueiro_oco", "nivel": [7, 9], "qtd": 6, "temperamento": "territorial", "ancora": "marco_do_corte", "raio_territorio": 5},
            {"kind": "carnical_inchado", "substituto": "carnical", "nivel": [7, 8], "qtd": 6, "temperamento": "neutro"}],
      lore="O bonde tombado onde Andras foi partido. Desertores vêm procurar o corpo do general e guardam o lugar; os Carniçais incharam de tanto comer ali.",
      missao="e04 O Marco do Corte"),
 dict(id="patio_do_abatedouro", nome="Pátio do Abatedouro", nivel=[7, 9], zona="abatedouro_carnica", x=134, y=38, raio=10,
      mobs=[{"kind": "acougueiro_oco", "nivel": [7, 9], "qtd": 11, "temperamento": "agressivo"},
            {"kind": "capataz_gancho", "nivel": [9, 9], "qtd": 1, "temperamento": "agressivo", "elite": True, "respawn_s": 300}],
      lore="Os açougueiros ainda trabalham para o patrão morto e atacam quem entra no pátio. O único spot agressivo de verdade, e a porta da Cripta.",
      missao="c02 O Livro de Óbitos, c03 A Porta Debaixo da Carne"),
 dict(id="casas_da_vila", nome="Casas da Vila", nivel=[8, 10], zona="vila_militar", x=148, y=138, raio=8, novo=True,
      mobs=[{"kind": "sangrador_apostata", "substituto": "nao_julgado", "nivel": [8, 10], "qtd": 6, "temperamento": "territorial", "ancora": "vila_militar", "raio_territorio": 4},
            {"kind": "nao_julgado", "nivel": [8, 9], "qtd": 6, "temperamento": "neutro"}],
      lore="A vila dos oficiais do silo. Os apóstatas fizeram das casas um altar e sangram os Não-Julgados que ainda batem às portas.",
      missao="vc05 O Último Turno (Isaura)"),
 dict(id="beira_da_tempestade", nome="Beira da Tempestade", nivel=[9, 12], zona="tempestade_areia", x=120, y=148, raio=10,
      mobs=[{"kind": "nao_julgado_da_tempestade", "substituto": "nao_julgado", "nivel": [9, 11], "qtd": 6, "temperamento": "neutro"},
            {"kind": "sombra_gravada", "substituto": "nao_julgado", "nivel": [10, 12], "qtd": 6, "temperamento": "territorial", "ancora": "muro_sombras", "raio_territorio": 4}],
      lore="As sombras que o clarão da bomba gravou no muro da vila descolam à noite e defendem o muro. Na borda da tempestade o contador não para de estalar.",
      missao="d05 O Muro das Sombras, d06 Absinto-2"),
]
for s in SPOTS: RESERVA |= circ((s["x"], s["y"]), s["raio"] * .85)
# âncoras que faltam (o muro das sombras, a escotilha do silo, o andor)
ms = next(s for s in SPOTS if s["id"] == "beira_da_tempestade")
linha_de("muro_tijolo", (ms["x"] - 5, ms["y"] + 7.5), (ms["x"] + 5, ms["y"] + 7.5), 1.0, orient="x", ponto="muro_sombras", silhueta=False)
add("escotilha_silo", 146, 150, pendente=True, fp=(3, 3), ponto="escotilha_silo", objeto="escotilha_silo", light=L("radio", 2))
add("placa_aviso", 143.5, 148, texto="PROPRIEDADE DO EXÉRCITO · SILO SÃO LÁZARO")
pp = next(s for s in SPOTS if s["id"] == "procissao_parada")
add("andor_padroeiro", pp["x"] + 1.5, pp["y"] + .5, ponto="andor_padroeiro", objeto="andor_padroeiro", light=L("vela", 2.5))

# descanso: fogueira + carrinho do Tobias (poção) perto de cada par de spots
DESCANSO = [("Fogueira do Espantalho", 82, 78, ["covas_rasas", "marco_do_corte"]),
            ("Fogueira do Pátio", 40, 52, ["cemiterio_bondes"]),
            ("Fogueira dos Telhados", 31, 124, ["telhados_dos_corvos"]),
            ("Fogueira da Vala", 112, 42, ["fosso_dos_caes", "patio_do_abatedouro"]),
            ("Fogueira das Lápides", 90, 140, ["procissao_parada", "alameda_ciprestes"]),
            ("Fogueira do Vau", 131, 94, ["chiqueiro_do_carnica", "acampamento_desertores"]),
            ("Fogueira da Tempestade", 134, 142, ["beira_da_tempestade", "margem_das_viuvas", "casas_da_vila"])]
desc_json = []
for nome, x, y, entre in DESCANSO:
    for r_ in range(0, 6):
        cand = [(x + a, y + b) for a in range(-r_, r_ + 1) for b in range(-r_, r_ + 1)]
        cand = [(a, b) for a, b in cand if livre(a, b, .3, road_ok=False, fp=(3, 2)) and not RESERVA[int(a), int(b)]]
        if cand: x, y = cand[0]; break
    add("fogueira", x, y + 1, light=L("fogo", 6), ponto="descanso")
    add("carrinho_tobias", x + 1.6, y - .6, ponto="descanso")
    add("sacos_areia", x - 1.4, y + .2); add("tonel_fogo", x + .4, y - 1.8, light=L("tonel", 3))
    desc_json.append({"nome": nome, "x": x, "y": y, "props": ["fogueira", "carrinho_tobias"], "npc": "tobias (vende poção)", "entre": entre})

# Cartaz do Agrak (inscrição no evento PvP, 16/10; Level design): na praça da Vela, posto no fim para não mexer no sorteio do resto
add("placa_aviso", PRACA[0] - 4.4, PRACA[1] - 5.2, objeto="cartaz_agrak", ponto="cartaz_agrak_vela", silhueta=False,
    texto="O AGRAK CHAMA · INSCRIÇÃO 100 OURO · NV 25+")

# Ilha do Exilado: a oficina do Pedro, o Exilado (ascensão de classe no nível 50); nada do espalhamento fica na ilha
_na_ilha = lambda p: ILHA[min(N - 1, int(p["x"])), min(N - 1, int(p["y"]))] and not p.get("ponto")
props[:] = [p for p in props if not _na_ilha(p)]
ocup[ILHA] = False; blocked[ILHA] = False
ix, iy = ILHA_C
# kit da ilha (assets/ambiente/fontes/exilado.py, 17/10): oficina de lona azul-noite + rubro-negra, manequins das
# evoluções, pontes de corda inteiras (decalque), sino de chamar a ponte e trapiche; a fileira y=87 fica livre das
# pontes até o Pedro
add("oficina_exilado", ix + .2, iy + 1.4, ponto="oficina_do_exilado", light=L("gas", 3.5), nota="oficina do Pedro, o Exilado")
add("manequim_evolucao_a", ix - 1.3, iy - 1.6, nota="manequim dos Arautos: o que você pode virar")
add("manequim_evolucao_b", ix + 2.3, iy - 1.4, nota="manequim da Vigília: o que você pode virar")
add("fogueira", ix - .3, iy - 2.4, block=False, light=L("fogo", 5))
add("estandarte_rasgado", ix - 1.9, iy + 2.9, nota="Vigília, riscado a faca")
add("estandarte_rasgado", ix + 1.6, iy + 3.2, nota="Coro, riscado a faca")
add("sino_ponte", ix - 3.0, iy + 1.7, nota="sino de chamar a ponte (oeste)")
add("sino_ponte", ix + 2.9, iy + 1.9, nota="sino de chamar a ponte (leste)")
add("trapiche_exilado", ix + .9, iy - 4.6, block=False, silhueta=False)
for a in (40, 70, 120, 150, 215, 245, 300, 330):
    add("juncos", ix + math.cos(math.radians(a)) * 3.7, iy + math.sin(math.radians(a)) * 3.7, block=False, silhueta=False)
for (pid, cx) in (("ponte_corda_oeste", ix - 5.8), ("ponte_corda_leste", ix + 5.8)):
    add("ponte_corda", cx, iy, block=False, camada="chao", silhueta=False, comprimento=6.4, orient="x", nota=pid)

# ------------------------------------------------------------------ colisão
blocked |= AGUA & ~VAU & ~P1 & ~P2 & ~P3 & ~P4
blocked |= BORDA
blocked &= ~(P1 | P2 | P3 | P4)
# estradas sempre livres (menos prédios que ocupam o chão de propósito)
blocked &= ~(ROAD & ~ocup)

# ------------------------------------------------------------------ zonas
def Z(id, nome, tipo, mask, nivel=None, **kw): return dict(id=id, nome=nome, tipo=tipo, nivel=nivel, mask=mask, **kw)
ZONAS = [
    Z("acampamento_vela", "Cidade de São Lázaro", "base", ZCITY, faccao="vigilia", seguro=True, musica="musica/acampamento_vela", ambiente="ambiente/acampamento_vela",
      eco=dict(clima="a cidade da Vigília em cima da cidade afogada: a Vela acesa na praça da matriz, o sino dos Sineiros, fumaça das forjas e o apito do bonde", neblina=.1,
               fauna=["ratos nos caixotes", "mariposas na Vela", "cachorro magro dormindo (decorativo)"], flora=["flor-de-absinto plantada em latas nas portas"],
               cor="âmbar das lanternas contra o azul elétrico da Vela e o verde dos vitrais")),
    Z("campos_cinza", "Campos de Cinza", "caca", ZCAMPOS, [1, 9], musica="musica/sao_lazaro", ambiente="ambiente/campos_cinza",
      eco=dict(clima="Amargo caindo como neve verde, vidro estalando sob os pés", neblina=.25, fauna=["corvos nos postes"], flora=["capim seco raro"], cor="cinza com veios verdes")),
    Z("patio_bondes", "Pátio dos Bondes", "caca", ZPATIO, [2, 4], musica="musica/sao_lazaro", ambiente="ambiente/noite_vento",
      eco=dict(clima="bondes mortos meio enterrados no ramal; o vento bate nas velas rasgadas", neblina=.25, fauna=["corvos nos mastros"], flora=["mato seco"], cor="ferrugem e lona")),
    Z("vala_comum", "A Vala", "caca", ZVALA, [3, 5], musica="musica/sao_lazaro", ambiente="ambiente/vala_comum",
      eco=dict(clima="valas que a maré de areia desenterra, névoa baixa do brejo", neblina=.4, fauna=["moscas", "uivos"], flora=["juncos na beira do rio"], cor="verde podre e lama")),
    Z("bairro_afogado", "Bairro Afogado", "caca", ZBAIRRO, [3, 5], musica="musica/sao_lazaro", ambiente="ambiente/noite_vento",
      eco=dict(clima="telhados saindo da areia, vento nas chaminés, a cidade velha caída no abismo ao lado", neblina=.3, fauna=["ratos", "corvos"], flora=["nenhuma"], cor="telha queimada")),
    Z("cemiterio_sao_lazaro", "Cemitério de São Lázaro", "caca", ZCEM, [4, 7], musica="musica/sao_lazaro", ambiente="ambiente/cemiterio",
      eco=dict(clima="lápides que a duna cobre e descobre, velas que não apagam, o sino rachado batendo sozinho", neblina=.45, fauna=["corvos"], flora=["árvores mortas", "cardos no túmulo do Firmino"], cor="azul frio, verde e pontos de vela")),
    Z("mata_cardos", "Mata dos Cardos", "transicao", ZCARDOS, [2, 4], musica="musica/sao_lazaro", ambiente="ambiente/noite_vento",
      eco=dict(clima="vento nos espinhos, sementes de cardo voando", neblina=.3, fauna=["mariposas"], flora=["cardos roxos"], cor="roxo apagado")),
    Z("rio_amargo", "Rio Amargo", "caca", AGUA | MARGEM | LEITO | ZDES, [6, 9], ambiente="ambiente/noite_vento",
      eco=dict(clima="o oásis: um fio de água verde e amarga no leito rachado, a única água do deserto", neblina=.45, fauna=["sapos (som)"], flora=["juncos", "flor-de-absinto"], cor="verde tóxico")),
    Z("bosque_viuvas", "Bosque das Viúvas", "caca", ZWOOD, [5, 7], musica="musica/sao_lazaro", ambiente="ambiente/noite_vento",
      eco=dict(clima="mata morta na curva do leito, cogumelos e plantas mutantes acesos de verde", neblina=.4, fauna=["corujas (som)"], flora=["árvores mortas", "cogumelos pálidos"], cor="cinza-osso e verde")),
    Z("vila_militar", "Vila Militar do Silo", "caca", ZVILA, [8, 10], musica="musica/sao_lazaro", ambiente="ambiente/noite_vento",
      eco=dict(clima="casas de oficiais com as sombras do clarão gravadas nas paredes", neblina=.5, fauna=[], flora=["mato seco"], cor="cal e fuligem")),
    Z("chiqueiros", "Chiqueiros", "caca", ZPIG, [4, 6], musica="musica/sao_lazaro", ambiente="ambiente/abatedouro",
      eco=dict(clima="cercas de chapa e lama na frente do abatedouro", neblina=.3, fauna=["porcos"], flora=[], cor="lama e ferrugem")),
    Z("abatedouro_carnica", "Abatedouro Carniça", "caca", ZABAT, [7, 9], musica="musica/sao_lazaro", ambiente="ambiente/abatedouro",
      eco=dict(clima="frigorífico enterrado até o 2º andar, fumaça das chaminés, chão grudento", neblina=.35, fauna=["moscas", "ratos gordos"], flora=[], cor="vermelho de fornalha")),
    Z("tempestade_areia", "Beira da Tempestade", "caca", TEMPESTADE, [9, 12], ambiente="ambiente/noite_vento",
      eco=dict(clima="parede de areia e Amargo que nunca baixa; a visão cai e o contador estala", neblina=.95, fauna=[], flora=[], cor="verde-acinzentado opaco")),
    Z("ilha_do_exilado", "Ilha do Exilado", "base", ILHA, faccao="neutro", seguro=True, ambiente="ambiente/noite_vento",
      eco=dict(clima="remanso do Rio Amargo; a fogueira do Pedro e o único riso que se ouve no rio", neblina=.3, fauna=["sapos (som)"], flora=["juncos"], cor="fogo contra o verde da água")),
]
LETRAS = "abcdefghijklmnop"
ZID = np.full((N, N), ".", dtype="<U1"); COD = {}
for i, z in reversed(list(enumerate(ZONAS))):
    COD[LETRAS[i]] = z["id"]; ZID[z["mask"]] = LETRAS[i]
ZID[ZCITY] = LETRAS[0]
ZID[ILHA] = LETRAS[len(ZONAS) - 1]

# ------------------------------------------------------------------ mobs fora dos spots (grupos pequenos, com motivo)
SP = []
def mob(kind, nivel, x, y, count, raio=2.0, temperamento="neutro", **kw):
    SP.append({"kind": kind, "level": nivel, "x": x, "y": y, "count": count, "radius": raio, "temperamento": temperamento, **kw})
mob("carnical", 1, 80, 64, 2, motivo="Primeiro mob da Vigília: dois Carniçais cavando a cova rasa de um soldado, à vista do portão leste.")
mob("carnical", 1, 76, 96, 2, motivo="Reviram as armaduras caídas na beira do campo, perto do poço seco.")
mob("corvo_de_cinza", 1, 85, 67, 2, ancora="ninhos_corvo", temperamento="territorial", raio_territorio=3, motivo="Defendem o ninho do poste torto mais perto da cidade.")
mob("corvo_de_cinza", 2, 99, 81, 2, ancora="ninhos_corvo", temperamento="territorial", raio_territorio=3, motivo="Ninho do meio do campo, o mais disputado.")
mob("carnical", 2, 100, 92, 3, motivo="Comendo os mortos que restam no Campo das Penas, onde caíram os anjos.")
mob("carnical", 2, 46, 30, 2, motivo="Seguem os trilhos do ramal atrás do cheiro dos vagões; os primeiros que quem sai pelo portão sul encontra.")
mob("corvo_de_cinza", 2, 36, 28, 2, motivo="Corvos que brigam com os do pátio pelos restos da estrada.")
mob("cao_de_vala", 3, 70, 26, 2, motivo="Batedores da matilha na Trilha da Vala.")
mob("cao_de_vala", 3, 110, 18, 3, temperamento="territorial", raio_territorio=3, ancora="toca_matilha", motivo="A ninhada da toca: só morde quem chega perto.")
mob("carnical", 3, 88, 18, 2, motivo="Cavando a vala mais nova; os cães toleram porque eles desenterram comida.")
mob("cao_de_vala", 3, 26, 104, 2, motivo="Dois cães que sobem do bairro pelos becos atrás de ratos.")
mob("corvo_de_cinza", 3, 12, 118, 2, motivo="Pousados na antena de repetição, gritam para a Rádio.")
mob("nao_julgado", 4, 72, 118, 2, motivo="Esperando no portão do cemitério, os primeiros que o jogador encontra.")
mob("nao_julgado", 4, 92, 132, 2, motivo="Junto às covas abertas de dentro para fora, de onde acabaram de sair.")
mob("nao_julgado", 5, 64, 126, 2, motivo="Em volta do túmulo do Firmino Cardo, atraídos pelo cheiro do caldo.")
mob("porco_pestilento", 4, 132, 80, 2, motivo="Porcos que escaparam do chiqueiro e fuçam a beira da trilha.")
mob("porco_pestilento", 5, 150, 92, 2, motivo="Os mais gordos, atrás do barraco do tratador.")
mob("acougueiro_oco", 6, 148, 60, 1, temperamento="agressivo", motivo="Guarda os tanques de sebo, onde está o baú do Tobias.")
mob("acougueiro_oco", 6, 128, 48, 1, temperamento="agressivo", motivo="Carneando no pátio sul, onde chega o Vau do Sebo.")
mob("nao_julgado", 5, 120, 128, 2, motivo="Viúvas que atravessaram a Ponte dos Enforcados e ficaram no bosque.")
mob("cao_de_vala", 6, 140, 108, 3, motivo="Matilha que desce o rio comendo o que os porcos deixam; liga a vila ao abatedouro.")
mob("corvo_de_cinza", 5, 134, 114, 2, motivo="Ninho na copa das árvores na saída da ponte.")
mob("nao_julgado", 8, 150, 124, 2, motivo="Moradores da vila que levantaram e voltam para casa todo fim de tarde.")
mob("cao_de_vala_alfa", 9, 106, 140, 1, temperamento="territorial", raio_territorio=4, substituto="cao_de_vala", motivo="O alfa da matilha caça sozinho na beira da tempestade.")
mob("filho_de_cardo", 6, 66, 124, 1, raio=0, so_por_missao="s02", motivo="Só aparece na missão s02, quando o caldo é derramado no túmulo de Firmino Cardo.")
# andor da procissão: 4 Não-Julgados parados carregando o andor (não contam no spot)
mob("nao_julgado", 5, pp["x"] + 1.5, pp["y"] + .5, 4, raio=1.2, formacao="andor", andor=True, temperamento="neutro", motivo="Carregam o andor do padroeiro e nunca o largam.")

# spots -> subgrupos de 2 ou 3, em anel, a 5 m um do outro
RND = random.Random(6)
for s in SPOTS:
    todos = [(m, 1) for m in s["mobs"] if m.get("elite")] + \
            [(m, k) for m in s["mobs"] if not m.get("elite") for k in ([3] * (m["qtd"] // 3) + ([m["qtd"] % 3] if m["qtd"] % 3 else []))]
    for m in s["mobs"]: m["subgrupos"] = sum(1 for mm, _ in todos if mm is m)
    n = len(todos); a0 = RND.uniform(0, 6.28)
    for i, (m, k) in enumerate(todos):
        if m.get("elite"): px, py = s["x"], s["y"]
        else:
            rr = s["raio"] * (.66 if i % 2 else .36) if n > 5 else s["raio"] * .5
            a = a0 + i / n * 2 * math.pi
            px, py = s["x"] + math.cos(a) * rr, s["y"] + math.sin(a) * rr
        lv = m["nivel"]; nivel = lv[0] + round((lv[1] - lv[0]) * i / max(1, n - 1))
        g = {"kind": m["kind"], "level": int(nivel), "x": round(px, 1), "y": round(py, 1), "count": k, "radius": 1.5,
             "temperamento": m["temperamento"], "spot": s["id"], "respawn_s": m.get("respawn_s", s.get("respawn_s", 14)), "motivo": s["lore"]}
        for kk in ("substituto", "ancora", "raio_territorio", "elite", "variante"):
            if m.get(kk): g[kk] = m[kk]
        SP.append(g)

# ------------------------------------------------------------------ NPCs (todos da Vigília e neutros)
PT = {}
for p in props:
    if p.get("ponto"): PT.setdefault(p["ponto"], (p["x"], p["y"]))
npcs = []
def npc(i, ponto, dx=0, dy=-1.8, **kw):
    x, y = PT[ponto]; npcs.append({"id": i, "ponto": ponto, "x": round(x + dx, 2), "y": round(y + dy, 2), **kw})
npc("capita_odete", "posto_odete", -2.6, -.6)
npc("doutor_anselmo", "barraca_anselmo", 2.6, -.6)
npc("mae_cardo", "caldeirao_cardo", .2, -1.4)
npc("tobias_pavio", "carrinho_tobias", -1.4, -1.2)
npc("gaspar_bigorna", "forja_bigorna", 0, -1.6)
npc("gustavo_primarca", "arca_primarca", 1.5, -.6)
npc("isaura_radialista", "radio_sao_lazaro", 4.6, -.8)
npc("zulmira_faroleira", "a_vela", 1.6, -1.6)
npc("bento_atracador", "plataforma_bondes", 1.0, -2.4)
npc("celina_vidraceira", "forno_vidro", -1.4, -1.2)
npc("damiao_sentinela", "costelas_cupula", 0, 0)
npc("lindalva_parteira", "enfermaria_lindalva", 2.6, -.6)
npc("pirralho_ferrolho", "a_vela", -2.6, -2.8)
npc("corvina_atravessadora", "loja_corvina", -1.6, -2.6)
npc("simao_coveiro", "casa_simao", 1.0, -2.6)
npc("pedro_exilado", "oficina_do_exilado", .4, -1.6, subzona="ilha_do_exilado")

# ------------------------------------------------------------------ baús, objetos, luzes, sons, lugares
baus = [{"id": p["bau"], "x": p["x"], "y": p["y"], "kind": p["kind"], **({"tipo": p["tipo_bau"]} if p.get("tipo_bau") else {})} for p in props if p.get("bau")]
MUNDO = {"bau_mundo_barco": ("Barco Afundado do Balseiro", "comum", "Debaixo do banco do barco, uma lata de querosene cheia de moedas e um terço de dente de cão."),
         "bau_mundo_moinho": ("Arca do Moinho Parado", "raro", "O rio secou e a roda parou com a arca presa entre as pás. Dentro, farinha preta e um embrulho de oleado."),
         "bau_mundo_viuvas": ("Oferenda das Viúvas", "raro", "Ao pé da árvore, um baú cheio de alianças, lenços e cartas que nunca foram mandadas."),
         "bau_mundo_sotao": ("Sótão Afogado", "comum", "Pela janela, um sótão cheio de areia até o teto. No canto que a areia não pegou, uma mala de viagem fechada com cinto."),
         "bau_mundo_caravana": ("Bagagem dos Romeiros", "comum", "Debaixo da carroça, uma mala de romeiro com terços, uma vela de promessa nunca acesa e moedas embrulhadas num lenço."),
         "bau_mundo_chiqueiro": ("Caixa do Tratador", "comum", "Atrás do barraco, a caixa de ferramentas do tratador. Ele não volta para buscar.")}
for b in baus:
    if b["id"] in MUNDO:
        n_, t_, txt = MUNDO[b["id"]]; b.update(nome=n_, tipo=t_, tabela="bau_area_inicial_" + t_, texto_ao_abrir=txt)
objetos = [{"id": p["objeto"], "x": p["x"], "y": p["y"]} for p in props if p.get("objeto")]
luzes = []
for p in props:
    if p.get("light"): luzes.append([p["x"], p["y"]] + p["light"])
    for e in p.get("luzes_extra", []): luzes.append(e)
    if p.get("luz_fraca"): luzes.append([p["x"], p["y"]] + p["luz_fraca"])
sons = [
    {"som": "ambiente/pontual/sino_distante", "x": MATRIZ[0], "y": MATRIZ[1], "raio": 40, "intervalo_s": [40, 90], "nota": "o sino dos Sineiros na matriz"},
    {"som": "ambiente/pontual/sino_distante", "x": CEM[0] - 1.5, "y": CEM[1] + 9.5, "raio": 26, "intervalo_s": [60, 120], "nota": "o sino rachado do cemitério"},
    {"som": "ambiente/pontual/corvo_distante", "x": 90, "y": 80, "raio": 26, "intervalo_s": [12, 30]},
    {"som": "ambiente/pontual/corvo_distante", "x": PATIO[0], "y": PATIO[1], "raio": 22, "intervalo_s": [14, 34]},
    {"som": "ambiente/pontual/uivo_distante", "x": 99, "y": 16, "raio": 34, "intervalo_s": [25, 60]},
    {"som": "ambiente/pontual/porta_distante", "x": ABAT[0], "y": ABAT[1], "raio": 22, "intervalo_s": [20, 50]},
    {"som": "ambiente/pontual/trovao_distante", "x": 80, "y": 158, "raio": 220, "intervalo_s": [60, 160]},
    {"som": "ambiente/pontual/caixinha_distante", "x": ABAT[0] + 10, "y": ABAT[1] - 4, "raio": 8, "intervalo_s": [45, 90], "nota": "dica do baú do Tobias no tanque de sebo"},
    {"som": "radio_chiado (pendente)", "x": RADIO[0], "y": RADIO[1], "raio": 14, "intervalo_s": [8, 20], "nota": "a Rádio da Isaura"},
]
LUGARES = [{"id": "radio_sao_lazaro", "nome": "Rádio São Lázaro", "x": RADIO[0], "y": RADIO[1], "zona": "acampamento_vela"},
           {"id": "matriz_sao_lazaro", "nome": "Igreja Matriz de São Lázaro", "x": MATRIZ[0], "y": MATRIZ[1], "zona": "acampamento_vela"},
           {"id": "estacao_linha7", "nome": "Estação da Linha 7", "x": ESTACAO[0], "y": ESTACAO[1], "zona": "acampamento_vela"},
           {"id": "loja_corvina", "nome": "Loja da Corvina", "x": 32, "y": 110, "zona": "bairro_afogado"},
           {"id": "marco_do_corte", "nome": "Marco do Corte", "x": TRAM[0], "y": TRAM[1], "zona": "campos_cinza"},
           {"id": "acampamento_desertores", "nome": "Acampamento dos Desertores", "x": 118, "y": 100, "zona": "rio_amargo"},
           {"id": "vila_militar", "nome": "Vila militar do silo", "x": VILA[0], "y": VILA[1], "zona": "vila_militar"},
           {"id": "silo_sao_lazaro", "nome": "Silo São Lázaro (escotilha)", "x": 146, "y": 150, "zona": "tempestade_areia"},
           {"id": "patio_bondes", "nome": "Pátio dos Bondes", "x": PATIO[0], "y": PATIO[1], "zona": "patio_bondes"}]

# ------------------------------------------------------------------ validação: tudo alcançável, nada em cima de nada
SPAWN = (PRACA[0] + 2, PRACA[1] - 4)
def alcancavel(a):
    seen = np.zeros((N, N), bool); q = [a]; seen[a] = True
    while q:
        x, y = q.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            u, v = x + dx, y + dy
            if 0 <= u < N and 0 <= v < N and not seen[u, v] and not blocked[u, v]: seen[u, v] = True; q.append((u, v))
    return seen
ok = alcancavel((int(SPAWN[0]), int(SPAWN[1])))
def encaixa(x, y, rmax=6):
    if ok[int(x), int(y)]: return x, y
    best = None
    for dx in range(-rmax, rmax + 1):
        for dy in range(-rmax, rmax + 1):
            u, v = int(x) + dx, int(y) + dy
            if 0 <= u < N and 0 <= v < N and ok[u, v] and (best is None or dx * dx + dy * dy < best[0]): best = (dx * dx + dy * dy, u + .5, v + .5)
    return (best[1], best[2]) if best else (x, y)
problemas = []
for s in SP:
    s["x"], s["y"] = encaixa(s["x"], s["y"])
    if not ok[int(s["x"]), int(s["y"])]: problemas.append(("mob inalcançável", s["kind"], s["x"], s["y"]))
for n_ in npcs:
    n_["x"], n_["y"] = encaixa(n_["x"], n_["y"], 3)
    if not ok[int(n_["x"]), int(n_["y"])]: problemas.append(("npc inalcançável", n_["id"]))
for b in baus:
    if not ok[max(0, int(b["x"]) - 1):int(b["x"]) + 2, max(0, int(b["y"]) - 1):int(b["y"]) + 2].any(): problemas.append(("baú inalcançável", b["id"]))
for o in objetos:
    if not ok[max(0, int(o["x"]) - 2):int(o["x"]) + 3, max(0, int(o["y"]) - 2):int(o["y"]) + 3].any(): problemas.append(("objeto inalcançável", o["id"]))
for s in SPOTS:
    if not ok[int(s["x"]) - 2:int(s["x"]) + 3, int(s["y"]) - 2:int(s["y"]) + 3].any(): problemas.append(("spot inalcançável", s["id"]))
    livre_ = ok[int(s["x"] - s["raio"]):int(s["x"] + s["raio"]), int(s["y"] - s["raio"]):int(s["y"] + s["raio"])].mean()
    s["livre"] = round(float(livre_), 2); s["dist_trilha"] = round(float(D_TRILHA[int(s["x"]), int(s["y"])]), 1)
    d_seg = math.hypot(s["x"] - CITY[0], s["y"] - CITY[1]) - CITY_R
    if d_seg < 14: problemas.append(("spot perto da cidade", s["id"], round(d_seg, 1)))
for a in SPOTS:
    for b in SPOTS:
        if a["id"] < b["id"] and math.hypot(a["x"] - b["x"], a["y"] - b["y"]) < a["raio"] + b["raio"] + 3: problemas.append(("spots colados", a["id"], b["id"]))
from collections import Counter
q_ = Counter(o["id"] for o in objetos)
for oid, qtd in {"corpo_lacrado": 6, "covas_abertas": 8, "ninhos_corvo": 6}.items():
    if q_[oid] != qtd: problemas.append(("quantidade", oid, q_[oid], qtd))
print("problemas:", problemas or "nenhum")

# ------------------------------------------------------------------ Amargo (0 a 9)
AM = np.full((N, N), 2.0)
AM += (ZVALA | AGUA | MARGEM).astype(float) + ZCEM * 1 + ZCAMPOS * .5 + ZVILA * 1.5
dt = ndimage.distance_transform_edt(~TEMP_BLOQ)
AM = np.maximum(AM, np.where(TEMPESTADE, 9 - np.clip(dt, 0, 10) * .55, 0))
db = ndimage.distance_transform_edt(~(PRECIPICIO | DUNAS | DUNAS_SUL))
AM += np.clip(3 - db, 0, 3)
AM[np.hypot(XX - CITY[0], YY - CITY[1]) < CITY_R + 1] = 0
AM = np.clip(np.round(AM), 0, 9).astype(int)

# ------------------------------------------------------------------ moldura e saída (mesmo formato do mapa anterior)
M = 20; NT = N + 2 * M
XT, YT = np.meshgrid(np.arange(NT) + .5 - M, np.arange(NT) + .5 - M, indexing="ij")
def pad(a, v): return np.pad(a, M, mode="constant", constant_values=v)
TT = pad(T, "d")
fora = np.ones((NT, NT), bool); fora[M:M + N, M:M + N] = False
NZ2T = np.pad(NZ2, M, mode="reflect"); NZT = np.pad(NZ, M, mode="reflect")
TT[fora & (XT < (NZ2T - .5) * 10 + 2) & (YT < N + (NZT - .5) * 14)] = "h"
BT = pad(blocked, True)
SH = lambda v: round(float(v) + M, 2)
def shp(p): return [SH(p[0]), SH(p[1])] + list(p[2:])
extra = []
for _ in range(110):
    x, y = R.uniform(-M + 2, N + M - 2), R.uniform(-M + 2, N + M - 2)
    if 0 <= x < N and 0 <= y < N: continue
    if x < 0 and y <= N: k = R.choice(["telhado_no_abismo", "torre_no_abismo", "telhado_no_abismo"])
    elif y > N: k = R.choice(["ossada_gigante", "torre_vigia_enterrada", "poste_mastro"])
    else: k = R.choice(["poste_mastro", "ossada_gigante", "poste_telegrafo", "arvore_morta", "duna_ondulacao"])
    extra.append({"kind": k, "x": round(x, 2), "y": round(y, 2), "decor_moldura": True})
KIT = set(BOX) | {k[:-2] for k in BOX if k.endswith(("_a", "_b"))}
for p in props + extra:
    if p["kind"] == "marcador_npc": p.pop("pendente", None); continue
    if p["kind"] in KIT: p.pop("pendente", None)
    else: p["pendente"] = True
pend = sorted({p["kind"] for p in props + extra if p.get("pendente")})
props_out = []
for p in props:
    q = {k: v for k, v in p.items() if v is not None}
    q["x"], q["y"] = SH(p["x"]), SH(p["y"])
    if "luzes_extra" in q: q["luzes_extra"] = [shp(e) for e in q["luzes_extra"]]
    props_out.append(q)
for p in extra: p["x"], p["y"] = SH(p["x"]), SH(p["y"]); props_out.append(p)
for s_ in SP: s_["x"], s_["y"] = SH(s_["x"]), SH(s_["y"])
for lst in (npcs, baus, objetos, LUGARES, desc_json):
    for o_ in lst: o_["x"], o_["y"] = SH(o_["x"]), SH(o_["y"])
for t_ in trilhas_json: t_["pontos"] = [shp(p) for p in t_["pontos"]]
for so in sons:
    if "x" in so: so["x"], so["y"] = SH(so["x"]), SH(so["y"])
spots_out = []
for s in SPOTS:
    s2 = dict(s); s2["x"], s2["y"] = SH(s["x"]), SH(s["y"]); spots_out.append(s2)
REGRAS = {"respawn_s": "14 por mob nos spots de farm (padrão do Combate); 25 fora dos spots",
          "subgrupos": "2 ou 3 mobs, a pelo menos 5 m um do outro; aggro_social 0 entre subgrupos",
          "afastamento": "spot a mais de 14 m da Cerca da cidade e fora das estradas principais; quem só passa não puxa nada",
          "skill_em_area": "clareira de 8 a 10 m de raio sem objetos altos, para o leque do nível 5 e o modo automático",
          "descanso": "fogueira + carrinho do Tobias (poção) perto de cada par de spots"}
data = {
    "name": "Cidade de São Lázaro", "versao": "1.0 (cidade da Vigília)", "size": NT,
    "_doc": "Área inicial da Vigília. Mesmo formato do mapa anterior. 200x200 tiles: a área jogável é 'jogavel' (160x160), o resto é moldura bloqueada. "
            "terreno/zonas_grid/amargo: uma string por x (índice = y). props com 'camada':'chao' são decalques; 'pendente': true = arte ainda não existe no kit.",
    "jogavel": {"x0": M, "y0": M, "x1": M + N, "y1": M + N},
    "camera_limite": {"x0": M - 6, "y0": M - 6, "x1": M + N + 6, "y1": M + N + 6},
    "spawn": [SH(SPAWN[0]), SH(SPAWN[1])],
    "spawn_por_faccao": {"vigilia": [SH(SPAWN[0]), SH(SPAWN[1])]},
    "safe_zone": {"x": SH(CITY[0]), "y": SH(CITY[1]), "radius": CITY_R},
    "safe_zones": [{"id": "acampamento_vela", "nome": "Cidade de São Lázaro", "x": SH(CITY[0]), "y": SH(CITY[1]), "radius": CITY_R, "faccao": "vigilia"}],
    "terreno_legenda": {"a": "areia", "u": "duna baixa (andável)", "d": "duna alta (bloqueia)", "h": "precipício/abismo (bloqueia)", "y": "vidro derretido",
                        "s": "leito seco rachado", "t": "terra batida", "z": "cinza (Campos)", "c": "calcamento", "g": "cemiterio", "l": "laje (praça e adro)",
                        "m": "chapa_matadouro", "w": "lama amarga funda (bloqueia)", "r": "água rasa (bloqueia, menos o vau)", "b": "barranca", "e": "musgo amargo",
                        "p": "brejo", "f": "chao de mata", "v": "terra de vala", "k": "cascalho dos trilhos", "n": "entulho", "i": "asfalto rachado"},
    "terreno": ["".join(TT[x]) for x in range(NT)],
    "amargo": ["".join(str(v) for v in pad(AM, 9)[x]) for x in range(NT)],
    "amargo_regras": {"0": "ar limpo (Vela)", "4": "contador começa a estalar", "7": "o Amargo fere"},
    "zonas_legenda": dict(COD, **{"#": "moldura (cenário)"}),
    "zonas": [{k: v for k, v in z.items() if k != "mask"} for z in ZONAS],
    "zonas_grid": ["".join(pad(ZID, "#")[x]) for x in range(NT)],
    "rio": {"id": "rio_amargo", "nome": "Rio Amargo", "centro": [[SH(a), SH(b)] for a, b in RIO[::12]],
            "largura": [round(largura[i], 1) for i in range(0, len(RIO), 12)], "agua_suja_a_partir_de": [SH(128), SH(46)],
            "vaus": [{"id": "vau_do_sebo", "x": SH(122.5), "y": SH(36), "raio": 4}],
            "pontes": [dict({k: v for k, v in p.items() if k not in ("mask", "de", "ate")}, de=shp(p["de"]), ate=shp(p["ate"])) for p in PONTES]},
    "trilhas": trilhas_json, "props": props_out, "blocked": [[int(a), int(b)] for a, b in np.argwhere(BT)],
    "spawns": SP, "npcs": npcs, "baus": baus, "objetos": objetos, "luzes": [shp(l) for l in luzes], "sons_pontuais": sons,
    "props_pendentes": pend, "lugares": LUGARES, "spots": spots_out, "descanso": desc_json, "spots_regras": REGRAS,
}
SAIDA = os.path.join(AQUI, "..")
json.dump(data, open(f"{SAIDA}/area_inicial.json", "w"), ensure_ascii=False, separators=(",", ":"))
json.dump({"_doc": "Spots de farm da Cidade de São Lázaro (grade 200x200 de area_inicial.json).", "regras": REGRAS, "spots": spots_out, "descanso": desc_json},
          open(f"{SAIDA}/spots.json", "w"), ensure_ascii=False, indent=1)
dentro = [p for p in props if 0 <= p["x"] < N and 0 <= p["y"] < N]
tot = sum(s_["count"] for s_ in SP if not s_.get("so_por_missao"))
print(f"{len(props_out)} props ({len(dentro)} na área jogável, {sum(1 for p in dentro if p.get('camada') != 'chao')} de pé) | "
      f"{int(BT.sum())} tiles bloqueados | {len(SP)} grupos / {tot} mobs | {len(SPOTS)} spots | pendentes: {pend}")
