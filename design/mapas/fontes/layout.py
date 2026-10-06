# Level design da Paróquia de São Lázaro (área inicial, níveis 1 a 8), v0.3 · Deserto de Absinto.
# Mundo aberto: o mapa jogável (120x120) fica no meio de uma moldura de 20 tiles de cenário
# intransponível (tempestade de areia, precipício da Cidade Velha, mar de dunas), então a borda nunca aparece.
# Gera ../area_inicial.json no mesmo formato que o jogo já lê (name, size, spawn, safe_zone,
# props, blocked, spawns) mais as camadas novas (terreno, zonas, rio, trilhas, npcs, baús,
# objetos, luzes, ecossistemas). Também salva _cena.pkl para o render.py desenhar a visão geral.
# Uso: python3 layout.py            (precisa de numpy e scipy)
# Eixos iguais ao jogo: 1 tile = 1 m; +x desce para a direita na tela, +y sobe para a direita.
# (0,0) é o canto esquerdo do losango; (0,N) o topo; (N,N) a direita; (N,0) o canto de baixo.
import json, math, random, pickle, os
import numpy as np
from scipy import ndimage

AQUI = os.path.dirname(os.path.abspath(__file__))
N = 120
R = random.Random(1717)
NP = np.random.default_rng(1717)

# ------------------------------------------------------------------ ruído
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
XX, YY = np.meshgrid(np.arange(N) + .5, np.arange(N) + .5, indexing="ij")   # [x, y]

def spline(pts, step=.25):
    """Catmull-Rom pelos pontos; devolve lista densa de (x, y)."""
    P = [pts[0]] + list(pts) + [pts[-1]]; out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = map(np.array, P[i - 1:i + 3])
        L = max(2, int(np.linalg.norm(p2 - p1) / step))
        for k in range(L):
            t = k / L
            out.append(tuple(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(pts[-1])); return out

def dist_to(curve):
    """Distância de cada tile até a curva (campo N x N) e índice do ponto mais próximo."""
    m = np.ones((N, N), bool); idx = {}
    for i, (x, y) in enumerate(curve):
        xi, yi = int(x), int(y)
        if 0 <= xi < N and 0 <= yi < N: m[xi, yi] = False; idx[(xi, yi)] = i
    d, inds = ndimage.distance_transform_edt(m, return_indices=True)
    return d

# ------------------------------------------------------------------ pontos-chave
CAMP = (22, 26)          # Acampamento da Vela (Vigília) - pátio da antiga estação de bondes
CHAPEL = (24, 99)        # Capela de São Lázaro (Arautos) - nave ao longo de y, porta no sul (y menor)
CEM = (55, 89)           # Cemitério no Morro do Coveiro, rio passando ao norte e a leste
VALA = (58, 26)          # A Vala, várzea alagada ao lado do rio
ABAT = (101, 37)         # Abatedouro Carniça, margem leste, rio abaixo
PIG = (99, 63)           # Chiqueiros do Carniça
WOOD = (97, 92)          # Bosque das Viúvas
TRAM = (45, 57)          # o bonde da linha 7 descarrilado, Marco do Corte

# ------------------------------------------------------------------ Rio Amargo (o que sobrou do Jordão)
# O Jordão secou. No fundo do leito rachado sobrou um canal de lama amarga (Amargo + sebo do abatedouro)
# que abre em poças verdes e brilha à noite. Não dá para atravessar a lama: só pelas pontes ou pelo Vau do Sebo.
RIO = spline([(46, 124), (50, 113), (60, 106), (71, 100), (76, 91), (73, 81), (75, 71), (81, 62),
              (82, 52), (80, 43), (83, 33), (89, 24), (97, 16), (105, 11), (110, 8.5)])
largura = []
for i, (x, y) in enumerate(RIO):
    t = i / len(RIO); largura.append(2.0 + 3.4 * max(0.0, math.sin(t * 23.0)) ** 2 + .6 * t)   # canal fino de lama que abre em poças
# meia-largura por tile = a do ponto mais próximo
m = np.ones((N, N), bool); lab = -np.ones((N, N), int)
for i, (x, y) in enumerate(RIO):
    xi, yi = int(x), int(y)
    if 0 <= xi < N and 0 <= yi < N: m[xi, yi] = False; lab[xi, yi] = i
D_RIO, (IX, IY) = ndimage.distance_transform_edt(m, return_indices=True)
IDX = lab[IX, IY]
HALF = np.array(largura)[IDX] / 2 + (NZ2 - .5) * .9
AGUA = D_RIO < HALF
FUNDA = D_RIO < HALF - .8
MARGEM = (D_RIO < HALF + 1.2 + NZ * 1.0) & ~AGUA
LEITO = (D_RIO < HALF + 4.0 + NZ2 * 3.0) & ~AGUA & ~MARGEM      # leito seco rachado do rio antigo
OASIS = D_RIO < HALF + 6 + NZ * 7                                 # só perto da água ainda cresce alguma coisa
# direção do fluxo por tile (para o shader da água)
dRIO = np.gradient(np.array(RIO), axis=0)
FLUXO = dRIO[IDX] / (np.linalg.norm(dRIO[IDX], axis=-1, keepdims=True) + 1e-6)

def rio_em(y=None, x=None):
    """Ponto do rio mais próximo de uma linha horizontal/vertical (ajuda a posicionar pontes)."""
    best = min(RIO, key=lambda p: abs(p[1] - y) if y is not None else abs(p[0] - x)); return best

# ------------------------------------------------------------------ terreno base
# códigos: a areia, u duna baixa (andável), d duna alta (bloqueia), h precipício/abismo, y vidro derretido,
# q cúpula de vidro, s leito seco, t terra batida, z cinza, c calçamento, g cemitério, l laje da capela,
# m chapa do matadouro, w água funda, r água rasa, b margem/lama, e relva amarga (oásis), p brejo,
# f chão de mata, v terra de vala, k trilho (cascalho)
T = np.full((N, N), "a", dtype="<U1")
T[NZ3 > .62] = "u"
def circ(c, r, jitter=0.0, nz=NZ):
    return np.hypot(XX - c[0], YY - c[1]) < r + (nz - .5) * jitter
def ellip(c, rx, ry, jitter=0.0):
    return ((XX - c[0]) / rx) ** 2 + ((YY - c[1]) / ry) ** 2 < 1 + (NZ - .5) * jitter

ZCAMPOS = ellip((36, 57), 25, 24, 1.0) & (XX > 8) & ~circ(CAMP, 11) & (YY < 84)
T[ZCAMPOS] = "z"
T[ZCAMPOS & (NZ2 > .6)] = "y"                         # onde a batalha queimou mais forte a areia virou vidro
ZVALA = ellip((62, 25), 17, 13, .9)
T[ZVALA] = "v"
BREJO = ZVALA & (D_RIO < HALF + 5 + NZ2 * 3)
T[BREJO] = "p"
ZCEM = ellip(CEM, 15.5, 13, .5) & (D_RIO > HALF + 2.0)
T[ZCEM] = "g"
ZWOOD = (ellip(WOOD, 20, 17, 1.0) | ellip((108, 78), 9, 14, .8)) & ~AGUA & (D_RIO < HALF + 15 + NZ * 6)
T[ZWOOD] = "f"
ZCARDOS = ellip((50, 74), 9, 5.5, 1.0)                 # Mata dos Cardos
T[ZCARDOS & (T != "z")] = "f"
ZABAT = ellip(ABAT, 15, 13, .4) & (XX > 86)
T[ZABAT] = "m"
ZPIG = ellip(PIG, 10, 8, .5) & ~ZABAT
T[ZPIG] = "t"
ZCAMP = circ(CAMP, 10.5)
T[ZCAMP] = "t"
T[circ(CAMP, 6.5)] = "q"                              # o acampamento pisa na cúpula de vidro da estação
ZCHAPEL = ellip(CHAPEL, 12, 15)
T[ZCHAPEL] = "l"
T[OASIS & np.isin(T, ["a", "u"])] = "e"                # relva amarga só onde ainda chega água

# ------------------------------------------------------------------ trilhas e estradas
TRILHAS = [
    # id, nome, piso, largura, pontos
    ("estrada_paroquia", "Estrada da Paróquia", "c", 3.0,
     [(26, 35), (21, 42), (17, 52), (16, 63), (19, 74), (23, 83), (24, 89)]),
    ("rua_do_sino", "Rua do Sino", "c", 2.2,
     [(17, 64), (26, 68), (36, 72), (44, 79), (50, 85), (52, 87)]),
    ("trilha_procissao", "Trilha das Procissões", "t", 1.7,
     [(30, 95), (38, 96), (46, 95), (51, 93)]),
    ("trilha_vala", "Trilha da Vala", "t", 1.8,
     [(31, 22), (39, 20), (47, 22), (54, 25)]),
    ("caminho_margem", "Caminho da Margem", "t", 1.6,
     [(66, 30), (71, 38), (73, 46), (72, 55), (69, 63), (66, 71), (66, 77)]),
    ("vau_do_sebo", "Vau do Sebo", "t", 1.6,
     [(70, 29), (78, 30), (86, 30), (93, 30)]),
    ("estrada_gado", "Estrada do Gado", "c", 2.4,
     [(88, 52), (93, 49), (96, 46), (99, 44)]),
    ("trilha_chiqueiros", "Trilha dos Chiqueiros", "t", 1.8,
     [(91, 51), (93, 57), (95, 63), (93, 71), (89, 78), (85, 83), (82, 86)]),
    ("trilha_viuvas", "Trilha das Viúvas", "t", 1.4,
     [(84, 87), (91, 91), (98, 96), (104, 102), (107, 106)]),
    ("trilha_campos", "Trilha dos Espantalhos", "t", 1.4,
     [(21, 44), (28, 51), (35, 58), (32, 66), (24, 70)]),
    ("trilha_cardos", "Trilha dos Cardos", "t", 1.3,
     [(41, 66), (47, 70), (55, 72), (63, 73)]),
    ("cemiterio_alamedas", "Alameda dos Ciprestes", "t", 1.5,
     [(52, 87), (57, 88), (62, 88), (66, 87), (69, 87)]),
    ("cemiterio_norte", "Subida da Torre", "t", 1.3,
     [(51, 93), (55, 92), (58, 94), (56, 98)]),
]
D_TRILHA = np.full((N, N), 99.0); ROAD = np.zeros((N, N), bool); MAIN = np.zeros((N, N), bool)
trilhas_json = []
for tid, nome, piso, w, pts in TRILHAS:
    cur = spline(pts)
    d = dist_to(cur)
    mask = d < w / 2 + (NZ2 - .5) * .9
    T[mask & ~AGUA] = piso
    ROAD |= d < w / 2 + (1.0 if piso == "c" else .6)
    if piso == "c": MAIN |= d < w / 2 + 1
    D_TRILHA = np.minimum(D_TRILHA, d)
    trilhas_json.append({"id": tid, "nome": nome, "piso": {"c": "calcamento", "t": "terra"}[piso],
                         "largura": w, "pontos": [[round(a, 1), round(b, 1)] for a, b in pts]})

# trilhos do bonde da linha 7 (cascalho + trilhos), da estação ao abatedouro, e o ramal morto para a cidade
LINHA7 = spline([(-2, 30), (8, 29), (17, 28), (25, 30), (31, 37), (37, 46), (42, 53), (46, 57), (54, 58),
                 (64, 55), (72, 52), (80, 51), (88, 51), (94, 48), (98, 45)])
D_L7 = dist_to(LINHA7)
T[(D_L7 < 1.3) & ~AGUA] = "k"
ROAD |= D_L7 < 2.2; MAIN |= D_L7 < 2
trilhas_json.append({"id": "linha_7", "nome": "Trilhos da Linha 7", "piso": "trilho", "largura": 2.0,
                     "pontos": [[round(a, 1), round(b, 1)] for a, b in LINHA7[::16]] + [[98, 45]]})

# ------------------------------------------------------------------ água e pontes
T[LEITO & np.isin(T, ["a", "u", "e", "z", "y", "v", "f", "t"])] = "s"
T[MARGEM] = "b"
T[AGUA] = "r"; T[FUNDA] = "w"
PONTES = []
def ponte(pid, nome, a, b, w, kind):
    cur = spline([a, b]); d = dist_to(cur); m = (d < w / 2)
    PONTES.append(dict(id=pid, nome=nome, de=list(a), ate=list(b), largura=w, kind=kind, mask=m))
    return m
P1 = ponte("ponte_bonde", "Ponte do Bonde", (73, 51.5), (89, 51.5), 3.2, "ponte_ferro_bonde")
P2 = ponte("ponte_enforcados", "Ponte dos Enforcados", (68, 86.5), (83, 86.5), 3.0, "ponte_pedra")
VAU = circ((80, 30), 4.2, 1.5) & AGUA
T[VAU] = "r"
FUNDA_BLOQ = AGUA & ~VAU & ~P1 & ~P2
# a água rasa da beira também bloqueia (só o vau é atravessável), para não abrir atalhos sem querer
ROAD |= P1 | P2

# ------------------------------------------------------------------ limites disfarçados (mundo aberto)
# Nada de muro. Cada lado acaba de um jeito que a lore explica, e a moldura de 20 tiles de cenário fora do
# mapa continua o mesmo efeito, então a câmera nunca mostra o fim do mundo.
#   x=0  (fundo esquerdo) : PRECIPÍCIO da Cidade Velha, onde a areia engoliu as ruas e o chão desabou.
#   y=N  (fundo direito)  : TEMPESTADE DE AREIA E AMARGO permanente. Dá para entrar um pouco; o Amargo
#                           sobe, o contador estala e a tempestade fere quem insiste. Depois, parede de areia.
#   x=N  (frente direita) : MAR DE DUNAS altas que andam com a maré de areia.
#   y=0  (frente esquerda): dunas baixas engolindo a Estrada do Sul (baixas para não tapar a câmera).
PRECIPICIO = XX < np.maximum(1.5, 3.0 + NZ * 4 + (NZ2 - .5) * 9 + NZ3 * 2)
TEMP_BLOQ = YY > N - 2.5 - NZ2 * 2
TEMPESTADE = (YY > N - 13 - NZ2 * 5) & ~TEMP_BLOQ
DUNAS = XX > N - 5 - NZ * 5
DUNAS_SUL = YY < 2.5 + NZ2 * 3
SUMIDOURO = circ((111, 7.5), 2.6)
BORDA = PRECIPICIO | TEMP_BLOQ | DUNAS | DUNAS_SUL | SUMIDOURO
T[(BORDA & ~AGUA)] = "d"
T[PRECIPICIO | SUMIDOURO] = "h"
T[TEMPESTADE & np.isin(T, ["a", "e", "s"])] = "u"

# ------------------------------------------------------------------ objetos
props = []; blocked = np.zeros((N, N), bool); ocup = np.zeros((N, N), bool)
def add(kind, x, y, block=True, camada=None, fp=None, **kw):
    p = {"kind": kind, "x": round(float(x), 2), "y": round(float(y), 2)}
    if camada: p["camada"] = camada
    p.update(kw); props.append(p)
    if fp:
        x0, y0 = int(x - fp[0] / 2 + .5), int(y - fp[1] / 2 + .5)
        ocup[max(0, x0):x0 + fp[0], max(0, y0):y0 + fp[1]] = True
        if block: blocked[max(0, x0):x0 + fp[0], max(0, y0):y0 + fp[1]] = True
    else:
        xi, yi = int(x), int(y)
        if 0 <= xi < N and 0 <= yi < N:
            ocup[xi, yi] = True
            if block: blocked[xi, yi] = True
    return p

def livre(x, y, r=1.0, road_ok=False, water_ok=False):
    xi, yi = int(x), int(y)
    if not (1 <= xi < N - 1 and 1 <= yi < N - 1): return False
    a, b = max(0, int(x - r)), max(0, int(y - r))
    if ocup[a:int(x + r) + 1, b:int(y + r) + 1].any(): return False
    if not road_ok and ROAD[xi, yi]: return False
    if not water_ok and AGUA[xi, yi]: return False
    return True

def espalhar(mask, kinds, n, sep=1.5, block=True, road_ok=False, water_ok=False, camada=None, dens=None, tries=40, **kw):
    """Poisson simples dentro da máscara; 'dens' (N x N, 0..1) agrupa em bosques/manchas."""
    cand = np.argwhere(mask)
    if len(cand) == 0: return 0
    feitos = 0
    for _ in range(n * tries):
        if feitos >= n: break
        cx, cy = cand[R.randrange(len(cand))]
        x, y = cx + R.random(), cy + R.random()
        if dens is not None and R.random() > dens[cx, cy]: continue
        if not livre(x, y, sep, road_ok, water_ok): continue
        k = R.choice(kinds) if isinstance(kinds, list) else kinds
        add(k, x, y, block=block, camada=camada, **kw); feitos += 1
    return feitos

LUZ = {"fogo": [1, .5, .15], "tonel": [1, .45, .12], "gas": [.95, .75, .4], "arco": [.75, .85, 1],
       "vitral": [1, .15, .08], "vela": [1, .75, .35], "sagrada": [1, .95, .7], "fornalha": [1, .3, .08],
       "podre": [.5, 1, .25], "lua": [.55, .65, .9]}
def L(tipo, raio): return LUZ[tipo] + [raio]

# ---------- Acampamento da Vela (base da Vigília, zona segura) ----------
cx, cy = CAMP
add("lampada_arco", cx, cy, fp=(2, 2), light=L("arco", 10), ponto="a_vela")
for a in range(0, 360, 9):                                 # paliçada com 3 portões
    if 30 < a < 62 or 95 < a < 118 or 196 < a < 222: continue
    r = 10.2; x, y = cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
    if AGUA[int(x), int(y)]: continue
    add("palicada", x, y, orient="y" if abs(math.cos(math.radians(a))) > .7 else "x")
for (x, y, ang) in [(cx + 9.6, cy + 6.8, 46), (cx - 4.2, cy + 10.2, 106), (cx - 9.6, cy - 3.6, 209)]:
    add("torre_vigia", x + 1.2 * math.cos(math.radians(ang)), y + 1.2 * math.sin(math.radians(ang)), fp=(2, 2), light=L("arco", 6))
# a cúpula de vidro da estação (o piso "q"), claraboias quebradas e o bonde-veleiro atracado nos trilhos
for (x, y) in [(cx - 4.5, cy + 3.0), (cx + 3.0, cy - 3.5), (cx - 2.0, cy + 5.0)]:
    add("claraboia_quebrada", x, y, block=False, camada="chao", pendente=True)
add("bonde_veleiro_atracado", cx + 1.5, cy + 3.8, fp=(5, 2), pendente=True, block=True)
add("tenda_vigilia", cx - 5.5, cy - 4.5, fp=(3, 3), ponto="barraca_anselmo")
add("bau_comum", cx - 4.2, cy - 6.0, bau="bau_barraca_anselmo", tipo_bau="trancado")
add("bancada_ferreiro", cx + 5.0, cy - 3.0, fp=(2, 1), light=L("fornalha", 5), ponto="forja_bigorna")
add("caldeirao_cardo", cx - 2.5, cy - 6.5, light=L("fogo", 4), ponto="caldeirao_cardo", pendente=True)
add("carrinho_tobias", cx + 6.0, cy + 1.5, ponto="carrinho_tobias", pendente=True)
add("posto_odete", cx + 2.5, cy - 5.5, fp=(2, 2), ponto="posto_odete", pendente=True)
add("tenda_vigilia", cx + 6.5, cy - 7.0, fp=(3, 3))
add("tenda_vigilia", cx - 7.0, cy + 0.5, fp=(3, 3))
for (x, y) in [(cx - 1.5, cy - 2.5), (cx + 3.0, cy + 1.0), (cx - 3.2, cy + 0.8), (cx + 7.5, cy - 1.8)]:
    add("tonel_fogo", x, y, light=L("tonel", 4.5))
for (x, y) in [(cx + 4.2, cy - 4.8), (cx + 4.8, cy - 1.0), (cx - 6.5, cy - 2.4), (cx + 1.0, cy + 7.3), (cx - 1.0, cy - 8.0)]:
    add(R.choice(["caixas", "barris", "caixas"]), x, y)
add("sacos_areia", cx + 8.4, cy + 3.9); add("sacos_areia", cx + 8.0, cy + 5.2)
add("placa_aviso", cx + 11.5, cy + 6.2, texto="CAMPOS DE CINZA — NÃO SAIA DOS TRILHOS")
add("varal_roupas", cx - 3.5, cy - 8.5, pendente=True, block=False)
add("roda_dagua_bomba", cx + 9.5, cy - 7.5, pendente=True)  # bomba manual puxando água de um poço artesiano
add("poco", cx + 9.0, cy - 6.0)

# ---------- Capela de São Lázaro (base dos Arautos, zona segura) ----------
qx, qy = CHAPEL
add("capela_sao_lazaro", qx, qy, fp=(8, 12), light=L("vitral", 9), ponto="altar_trombeta", variante="enterrada_ate_o_coro",
    luzes_extra=[[qx - 3, qy - 2] + L("vitral", 5), [qx + 3, qy + 2] + L("vitral", 5), [qx, qy + 6] + L("sagrada", 7)])
add("pulpito_externo", qx + 1.8, qy - 11.0, pendente=True, block=False, ponto="pulpito_ivone")
add("marcador_npc", qx - 2.5, qy - 8.5, block=False, ponto="nave_abdiel", invisivel=True, nota="Abdiel treina os Arautos no adro, em frente à porta da nave")
add("marcador_npc", qx + 6.0, qy + 1.5, block=False, ponto="sacristia_lucio", invisivel=True, nota="porta lateral da sacristia")
# adro escavado: os Arautos cavaram a areia em volta da igreja e seguram as paredes com sacos e tábuas
for i in range(-9, 10):
    for (x, y) in [(qx + i, qy - 13.5), (qx + i, qy + 13.5)]:
        if abs(i) <= 1 and y < qy: continue                          # portão principal
        add("muro_contencao_areia" if R.random() < .7 else "barricada_sacos", x, y, orient="x", pendente=True)
for j in range(-13, 14):
    for x in (qx - 9.5, qx + 9.5):
        if abs(j) <= 1 and x > qx: continue                          # portão lateral para a procissão
        add("muro_contencao_areia" if R.random() < .7 else "barricada_sacos", x, qy + j, orient="y", pendente=True)
for (x, y) in [(qx - 2.2, qy - 11.5), (qx + 2.2, qy - 11.5), (qx + 7.5, qy - 2.2), (qx + 7.5, qy + 2.2)]:
    add("braseiro_sagrado", x, y, light=L("sagrada", 5), pendente=True)
for (x, y) in [(qx - 7, qy - 10), (qx + 7, qy - 10), (qx - 7.5, qy - 5), (qx + 7.5, qy - 7)]:
    add("cipreste", x, y, pendente=True)
add("estatua_anjo_quebrada", qx - 5.5, qy - 9, fp=(2, 2))
add("estatua_anjo_quebrada", qx + 5.5, qy - 9, fp=(2, 2))
# telhado dos fundos: acampamento dos demônios (Malfas), que não entram na igreja
add("fogueira", qx, qy + 10, fp=(2, 2), light=L("fogo", 6), ponto="patio_malfas")
add("trono_sucata", qx + 2.5, qy + 11, pendente=True)
for (x, y) in [(qx - 4, qy + 9), (qx + 5, qy + 8.5), (qx - 6, qy + 11.5)]:
    add("tenda_demonio", x, y, fp=(2, 2), pendente=True)
add("gaiola_suspensa", qx - 2.5, qy + 12)
for (x, y) in [(qx - 6.5, qy - 1), (qx + 6.5, qy + 4), (qx - 6.5, qy + 5)]:
    add(R.choice(["caixas", "barris"]), x, y)
add("placa_aviso", qx + 1.8, qy - 15.0, texto="SÓ ENTRA QUEM ESPERA A NOTA")

# ---------- Campos de Cinza (1-3) ----------
CAMPO_OK = (T == "z") & ~ROAD
# o bonde descarrilado e o Marco do Corte (onde Odete partiu o General ao meio)
add("bonde_linha7_tombado", TRAM[0], TRAM[1], fp=(5, 3), pendente=True, ponto="marco_do_corte")
add("cratera_corte", TRAM[0] + 2.5, TRAM[1] - 3.0, camada="chao", block=False, pendente=True)
add("poca_sangue_rastro", TRAM[0] + 4, TRAM[1] - 4.5, camada="chao", block=False)
add("trilho_retorcido", TRAM[0] - 3, TRAM[1] - 2, pendente=True)
add("estandarte_rasgado", TRAM[0] + 3.5, TRAM[1] + 3, pendente=True, faccao_estandarte="legiao_rubra")
# poço seco e campo das penas
add("poco", 29, 64, ponto="poco_seco", objeto="poco_seco")
CAMPO_PENAS = (43, 40)
add("asa_anjo_caida", CAMPO_PENAS[0], CAMPO_PENAS[1], fp=(3, 2), pendente=True, ponto="campo_penas")
espalhar(circ(CAMPO_PENAS, 4) & CAMPO_OK, ["penas_espalhadas"], 10, sep=.8, block=False, camada="chao", pendente=True)
# ninhos de corvo em postes tortos (5) e o esconderijo do Tobias num ninho gigante
NINHOS = [(27, 45), (40, 66), (52, 50), (24, 58), (29, 77)]
for (x, y) in NINHOS:
    add("poste_ninho", x, y, objeto="ninhos_corvo", pendente=True)
add("poste_ninho_gigante", 47, 43, pendente=True, ponto="poste_torto")
add("bau_comum", 47.8, 42.2, bau="bau_tobias_1", block=False)
# espantalhos de arame em fileiras quebradas pela trilha
for (x, y) in [(23, 49), (26, 52), (30, 55), (33, 61), (30, 68), (37, 70), (19, 56), (44, 61), (49, 63), (40, 41)]:
    if livre(x, y, .8): add("espantalho_arame", x, y, pendente=True)
# restos da Grande Batalha: armaduras, crateras, estandartes, cercas de arame, carroças
espalhar(CAMPO_OK, ["armadura_enferrujada", "armadura_enferrujada", "elmo_espada_fincada"], 46, sep=1.6, block=False, pendente=True)
espalhar(CAMPO_OK, ["cratera"], 14, sep=3.5, block=False, camada="chao", pendente=True)
espalhar(CAMPO_OK, ["estandarte_rasgado"], 6, sep=6, pendente=True)
espalhar(CAMPO_OK, ["carroca_quebrada"], 4, sep=5, fp=None)
espalhar(CAMPO_OK, ["cerca_arame_torta"], 14, sep=2, pendente=True)
espalhar(CAMPO_OK | ((T == "y") & ~ROAD), ["vidro_estilhacos"], 140, sep=.9, block=False, camada="chao", pendente=True, dens=NZ ** 1.5 * 1.6)
espalhar(CAMPO_OK, ["duna_ondulacao"], 40, sep=2.5, block=False, camada="chao", pendente=True)
espalhar(CAMPO_OK, ["ossos_espalhados", "poca_sangue"], 30, sep=1.5, block=False, camada="chao")
espalhar(CAMPO_OK, ["arvore_morta"], 12, sep=4, dens=NZ3)
espalhar(CAMPO_OK, ["capim_seco"], 30, sep=1.2, block=False, pendente=True, dens=NZ2)
espalhar(CAMPO_OK, ["poste_bonde_mastro"], 6, sep=6, pendente=True)
# postes de gás na estrada principal (metade apagados)
for i, (x, y) in enumerate(spline([(26, 35), (21, 42), (17, 52), (16, 63), (19, 74), (23, 83), (24, 89)])[::28]):
    if i == 0: continue
    if i % 3 == 2: add("poste_gas_quebrado", x + 2.2, y)
    else: add("poste_gas", x + 2.2, y, light=L("gas", 4))
for (x, y) in spline([(17, 64), (26, 68), (36, 72), (44, 79), (50, 85)])[::30][1:]:
    add("poste_gas", x + .3, y + 1.8, light=L("gas", 3.5))

# ---------- A Vala (2-4): valas abertas na várzea alagada ----------
VALA_OK = ZVALA & ~ROAD & ~AGUA
for (x, y, w, h) in [(56, 20, 7, 2), (62, 22, 6, 2), (54, 31, 6, 2), (65, 31, 5, 2), (60, 27, 4, 2)]:
    add("vala_aberta", x, y, fp=(w, h), pendente=True)
    espalhar(ellip((x, y), w / 2 + 1, h / 2 + 1) & VALA_OK, ["ossos_espalhados", "poca_sangue"], 4, sep=.8, block=False, camada="chao")
add("toca_caes", 67, 17, fp=(3, 2), pendente=True, ponto="toca_matilha")       # bueiro desabado onde a matilha dorme
espalhar(VALA_OK & ~BREJO, ["estacas_cerca", "cruz_madeira"], 18, sep=2)
espalhar(BREJO & ~ROAD & ~AGUA, ["juncos", "juncos", "taboa"], 120, sep=.7, block=False, pendente=True)
espalhar(BREJO & ~ROAD & ~AGUA, ["poca_toxica"], 18, sep=2, block=False, camada="chao")
espalhar(VALA_OK & OASIS, ["salgueiro_chorao"], 4, sep=5, fp=None, pendente=True)
espalhar(VALA_OK, ["carroca_quebrada", "entulho"], 4, sep=4)
add("gaiola_suspensa", 52, 28, light=L("podre", 3))
add("barco_afundado", 74, 22, fp=(3, 2), pendente=True, water_ok=True)
add("bau_comum", 74.5, 20.5, bau="bau_mundo_barco", tipo_bau="comum", block=False)
add("tonel_fogo", 47, 23, light=L("tonel", 4))                             # fogueira de saqueadores, entrada da vala

# ---------- Cemitério de São Lázaro (3-5), Morro do Coveiro ----------
CEM_OK = ZCEM & ~ROAD
ex, ey = CEM
for k in range(int(2 * math.pi * 14.4 / 1.0)):                             # gradil de ferro com 3 portões
    a = k / (2 * math.pi * 14.4 / 1.0) * 360
    x, y = ex + 14.6 * math.cos(math.radians(a)), ey + 12.4 * math.sin(math.radians(a))
    if AGUA[int(x), int(y)] or MARGEM[int(x), int(y)]: continue
    if D_TRILHA[int(x), int(y)] < 1.6: continue
    add("cerca_ferro", x, y, orient="x" if abs(math.sin(math.radians(a))) > .7 else "y")
add("casa_coveiro", ex + .5, ey - 1.5, fp=(5, 4), pendente=True, ponto="casa_simao", light=L("vela", 4))
add("torre_sino", ex - 2, ey + 9, fp=(3, 3), pendente=True, ponto="torre_sino", objeto="torre_sino")
add("estatua_anjo_quebrada", ex + 7, ey + 5, fp=(2, 2), ponto="anjo_sem_cabeca")
add("bau_comum", ex + 7.8, ey + 4.0, bau="bau_tobias_2", block=False)
add("mausoleu", ex - 7, ey + 3, fp=(3, 3), light=L("vela", 2.5))
add("mausoleu", ex + 4.5, ey + 8.5, fp=(3, 3))
add("mausoleu", ex - 5, ey - 6.5, fp=(3, 3))
add("lapide_cruz_celta", ex - 9, ey - 2, ponto="tumulo_cardo", objeto="tumulo_cardo")
espalhar(ellip((ex - 9.5, ey - 2.5), 3.5, 3) & ~ROAD, ["moita_cardo"], 9, sep=.8, block=False, pendente=True)
COVAS = []
espalhar(CEM_OK, ["cova_aberta"], 8, sep=1.2, tries=400, block=False, camada="chao", pendente=True, objeto="covas_abertas")
espalhar(CEM_OK, ["corpo_lacrado"], 6, sep=1, tries=400, block=False, objeto="corpo_lacrado", pendente=True)
# fileiras de túmulos (com falhas), túmulos abertos de dentro para fora
for row in range(-6, 7):
    for col in range(-8, 9):
        x = ex + col * 1.7 + R.uniform(-.25, .25); y = ey + row * 1.9 + R.uniform(-.2, .2)
        if not ZCEM[int(x), int(y)] or R.random() < .22: continue
        if livre(x, y, .3):
            k = R.choice(["lapide", "lapide", "cruz_madeira", "lapide_cruz_celta", "tumulo_aberto"])
            add(k, x, y, pendente=(k == "tumulo_aberto"))
espalhar(CEM_OK, ["cipreste"], 14, sep=1, tries=200, pendente=True)
espalhar(CEM_OK, ["arvore_morta"], 6, sep=4)
espalhar(CEM_OK, ["vela_tumulo"], 22, sep=.3, block=False, pendente=True, light=L("vela", 1.2))
espalhar(CEM_OK, ["folhas_papeis", "ossos_espalhados"], 20, sep=1.2, block=False, camada="chao")
espalhar(CEM_OK, ["mar_de_lapides"], 16, sep=.3, block=False, tries=200)              # lápides que a duna cobre e descobre
espalhar(CEM_OK, ["duna_areia"], 10, sep=.3, block=False, camada="chao", tries=200)
for (x, y) in spline([(52, 87), (57, 88), (62, 88), (66, 87), (69, 87)])[::14]:
    add("lanterna_procissao", x, y + 1.6, light=L("vela", 2.5), pendente=True)

# ---------- Mata dos Cardos (transição campos -> cemitério) ----------
CARD_OK = ZCARDOS & ~ROAD & ~AGUA
espalhar(CARD_OK, ["moita_cardo", "moita_cardo", "arbusto_espinhos"], 70, sep=.8, block=False, pendente=True)
espalhar(CARD_OK, ["arvore_retorcida", "arvore_morta"], 9, sep=2.6)
espalhar(CARD_OK, ["tronco_caido"], 3, sep=3, pendente=True)

# ---------- Rio: margens vivas ----------
MARG_OK = MARGEM & ~ROAD & ~BORDA
espalhar(MARG_OK, ["juncos", "taboa", "juncos"], 360, sep=.65, block=False, pendente=True, dens=.35 + .65 * NZ2)
espalhar(MARG_OK, ["salgueiro_chorao"], 22, sep=4.5, pendente=True)
espalhar(MARG_OK, ["pedras_margem"], 40, sep=1.6, block=False, pendente=True)
espalhar(MARG_OK, ["tronco_caido"], 6, sep=4, pendente=True)
espalhar(AGUA & ~FUNDA & ~VAU & ~P1 & ~P2, ["peixes_mortos", "lirio_negro"], 30, sep=1.5, block=False, water_ok=True, camada="agua", pendente=True)
for (x, y) in [(79, 28.5), (80.5, 30.5), (79.5, 32), (81.5, 29), (78.5, 31)]:
    add("pedra_vau", x, y, block=False, camada="chao", pendente=True)
add("ponte_ferro_bonde", 81, 51.5, block=False, pendente=True, ponto="ponte_bonde", comprimento=16)
add("ponte_pedra", 75.5, 86.5, block=False, pendente=True, ponto="ponte_enforcados", comprimento=15)
for x in (70, 74, 78, 82):
    add("forca_ponte", x, 88.2, pendente=True, light=L("podre", 1.5) if x == 78 else None)
add("moinho_ruina", 63.5, 104.5, fp=(4, 4), pendente=True, ponto="moinho")   # moinho afogado perto da capela
add("roda_dagua", 66.2, 103.0, pendente=True, water_ok=True)
add("bau_raro", 61.0, 101.5, bau="bau_mundo_moinho", tipo_bau="raro")
# esgoto do abatedouro sujando o rio: daqui pra baixo a água é vermelha e oleosa
add("cano_esgoto", 87.0, 36.5, pendente=True, ponto="esgoto_abatedouro", vaza="sebo_sangue")
add("cano_esgoto", 86.0, 41.5, pendente=True, vaza="sebo_sangue")

# ---------- Margem leste: Bosque das Viúvas (4-5) ----------
WOOD_OK = ZWOOD & ~ROAD & ~AGUA & ~BORDA
DENS_W = np.clip(NZ * 1.3 - .1, 0, 1)
espalhar(WOOD_OK, ["arvore_retorcida", "arvore_retorcida", "arvore_retorcida", "arvore_morta", "salgueiro_chorao"], 260, sep=1.2, dens=DENS_W)
espalhar(WOOD_OK, ["arbusto_espinhos", "samambaia_seca"], 140, sep=.9, block=False, pendente=True)
espalhar(WOOD_OK, ["poca_toxica"], 14, sep=.3, tries=200, block=False, camada="chao", light=[.4, 1, .3, 1.6])
espalhar(WOOD_OK, ["cogumelos_palidos"], 28, sep=.3, tries=200, block=False, pendente=True, light=[.55, .8, .6, 1.0])
espalhar(WOOD_OK, ["tronco_caido", "toco"], 22, sep=2.5, pendente=True)
espalhar(WOOD_OK, ["folhas_papeis"], 30, sep=1.5, block=False, camada="chao")
add("arvore_enforcados", 101, 98, fp=(3, 3), pendente=True, ponto="arvore_viuvas", light=L("podre", 3))
add("bau_raro", 103.2, 96.6, bau="bau_mundo_viuvas", tipo_bau="raro")
add("capelinha_beira", 108, 106, fp=(3, 3), pendente=True, light=L("vela", 3))   # oratório no fim da trilha

# ---------- Chiqueiros do Carniça (4-6) ----------
px_, py_ = PIG
for (ox, oy, w, h) in [(-5, -3, 6, 5), (3, -4, 6, 5), (-1, 4, 7, 4)]:
    x0, y0 = px_ + ox, py_ + oy
    for i in range(w + 1):
        for (x, y) in [(x0 + i, y0), (x0 + i, y0 + h)]:
            if i == w // 2 and y == y0: continue
            add("cerca_chiqueiro", x, y, orient="x", pendente=True)
    for j in range(1, h):
        for x in (x0, x0 + w): add("cerca_chiqueiro", x, y0 + j, orient="y", pendente=True)
espalhar(ZPIG & ~ROAD, ["cocho", "lama_porcos"], 12, sep=1.4, block=False, pendente=True)
espalhar(ZPIG & ~ROAD, ["poca_sangue", "ossos_espalhados"], 10, sep=1.2, block=False, camada="chao")
add("barraco_sucata", px_ + 7, py_ - 6, fp=(3, 3))
add("bau_comum", px_ + 8.7, py_ - 4.3, bau="bau_mundo_chiqueiro", tipo_bau="comum")

# ---------- Abatedouro Carniça (4-7) ----------
ax, ay = ABAT
add("abatedouro_carnica", ax, ay, fp=(10, 8), light=L("fornalha", 8), ponto="escritorio_capataz",
    luzes_extra=[[ax - 3, ay + 4] + L("fornalha", 5), [ax + 4, ay - 4] + L("fogo", 4)])
add("entrada_cripta", ax - 1, ay - 7, fp=(3, 3), ponto="porta_ganchos", objeto="porta_ganchos", light=L("fornalha", 4))
add("tanque_sebo", ax + 8, ay - 5, fp=(2, 2), pendente=True, ponto="tanque_sebo")
add("bau_raro", ax + 8.6, ay - 3.2, bau="bau_tobias_3", tipo_bau="trancado", block=False)
add("tanque_sebo", ax + 8, ay + 1, fp=(2, 2), pendente=True)
for i in range(7):
    add("ganchos_carne", ax - 9, ay - 6 + i * 2, fp=(1, 1))
for i in range(5):
    add("ganchos_carne", ax - 4 + i * 2, ay + 7.5)
for (x, y) in [(ax - 6, ay - 8), (ax + 5, ay - 8), (ax + 10, ay + 6), (ax - 10, ay + 7)]:
    add("tonel_fogo", x, y, light=L("tonel", 4.5))
espalhar(ZABAT & ~ROAD & ~ocup, ["poca_sangue", "poca_sangue_rastro", "ralo_ferro_chao"], 26, sep=1.2, block=False, camada="chao")
espalhar(ZABAT & ~ROAD, ["barris", "caixas", "mesa_acougue_rua", "carroca_quebrada"], 16, sep=1.8)
for x in range(int(ax - 13), int(ax + 13)):
    if livre(x, ay + 12.5, .4, road_ok=True) and not ROAD[x, int(ay + 12.5)]:
        add("muro_tijolo" if R.random() < .7 else "muro_tijolo_quebrado", x, ay + 12.5, orient="x")
add("placa_aviso", 96, 49.5, texto="CARNIÇA & FILHOS — CARNE PARA A PARÓQUIA")
add("gaiola_suspensa", 92.5, 45, light=L("podre", 2.5))

# ---------- Bairro Afogado: a rua de hoje é o telhado de ontem ----------
ZBAIRRO = ellip((13, 60), 7, 22, .8) & ~PRECIPICIO & ~ROAD
for (x, y) in [(10, 42), (15, 45), (9, 50), (14, 53), (10, 70), (15, 72), (9, 77), (13, 81), (16, 66), (8, 61)]:
    if livre(x, y, 1.5, road_ok=True): add("telhado_enterrado", x, y, fp=(4, 3), pendente=True)
add("torre_relogio_enterrada", 12, 58, fp=(3, 3), pendente=True, ponto="relogio_afogado", light=L("vela", 3))
add("janela_na_areia", 13.5, 56.0, block=False, pendente=True, ponto="sotao_afogado", leva_para="sotao (interior opcional)")
add("bau_comum", 14.6, 55.5, bau="bau_mundo_sotao", tipo_bau="comum", block=False)
espalhar(ZBAIRRO, ["chamine_enterrada", "janela_na_areia", "placa_rua_enterrada"], 12, sep=2.2, pendente=True)
espalhar(ZBAIRRO, ["entulho", "duna_ondulacao"], 16, sep=1.6, block=False, pendente=True)

# ---------- deserto aberto entre as zonas ----------
GERAL = np.isin(T, ["a", "u", "e", "s"]) & ~ROAD & ~BORDA & ~ZCAMP & ~ZCHAPEL & ~ZABAT & ~ZBAIRRO & ~TEMPESTADE
VERDE = GERAL & OASIS
espalhar(VERDE, ["arvore_retorcida", "arvore_morta", "salgueiro_chorao"], 40, sep=2.4, dens=np.clip(NZ3 * 1.4 - .1, 0, 1))
espalhar(VERDE, ["arbusto_espinhos", "capim_seco", "moita_cardo"], 160, sep=.9, block=False, pendente=True, dens=NZ2)
SECO = GERAL & ~OASIS
espalhar(SECO, ["arvore_morta"], 22, sep=5, dens=NZ3)
espalhar(SECO, ["duna_ondulacao"], 120, sep=2.0, block=False, camada="chao", pendente=True)
espalhar(SECO, ["capim_seco", "arbusto_espinhos"], 60, sep=1.5, block=False, pendente=True, dens=NZ2)
espalhar(SECO, ["telhado_enterrado"], 9, sep=6, fp=None, pendente=True)
espalhar(SECO, ["chamine_enterrada", "poste_bonde_mastro", "ossada_animal", "carroca_quebrada"], 26, sep=4, pendente=True)
espalhar((T == "s") & ~ROAD, ["barco_encalhado", "ossada_animal", "pedras_margem"], 14, sep=4, pendente=True)

# ---------- limites ----------
# precipício da Cidade Velha: corda de guarda, guindaste de sucata, telhados na beira e os trilhos da Linha 7 caindo no abismo
BEIRA = ndimage.binary_dilation(PRECIPICIO, iterations=2) & ~PRECIPICIO
for (x, y) in np.argwhere(BEIRA)[::3]:
    if livre(x + .5, y + .5, .3, road_ok=True) and R.random() < .45:
        add("corda_guarda", x + .5, y + .5, orient="y", pendente=True)
add("trilhos_no_abismo", 6, 29.5, pendente=True, ponto="fim_da_linha7", block=False)
add("guindaste_sucata", 9, 88, fp=(2, 2), pendente=True, light=L("tonel", 3), ponto="guindaste_cidade_velha")
add("ponte_rompida", 6.5, 72, pendente=True, block=False)
for (x, y, t) in [(9, 36, "A CIDADE VELHA CAIU AQUI"), (9, 64, "NÃO DESÇA. ELES AINDA CHAMAM.")]:
    add("placa_aviso", x, y, texto=t)
# tempestade: o que sobrou da Linha do Impasse sendo engolido, e o aviso de quem voltou
for x in range(6, N - 8, 3):
    yy = N - 12 + NZ2[min(x, N - 1), N - 12] * 4
    if livre(x, yy, .5, road_ok=True) and R.random() < .6:
        add(R.choice(["cerca_arame_torta", "barricada_sacos", "estacas_cerca"]), x, yy, orient="x", pendente=True)
for x in (20, 46, 74, 100):
    add("torre_vigia_enterrada", x, N - 7.5, fp=(2, 2), pendente=True, light=L("arco", 3))
espalhar(TEMPESTADE & ~AGUA, ["ossada_animal", "ossada_viajante", "estandarte_rasgado"], 26, sep=3, block=False, road_ok=True, pendente=True)
for (x, y) in [(28, N - 14), (56, N - 15), (88, N - 14)]:
    add("placa_aviso", x, y, texto="VOLTE. A AREIA COME.")
# mar de dunas e estrada do sul engolida
espalhar(DUNAS | DUNAS_SUL, ["mastro_bonde_naufragado", "ossada_gigante", "poste_telegrafo"], 18, sep=6, block=False, road_ok=True, water_ok=True, pendente=True)
for x in range(26, 74, 4):
    add("poste_telegrafo", x, 4.2 - (x - 26) / 24, pendente=True)      # a linha de postes sumindo debaixo da duna
add("placa_aviso", 30, 5.5, texto="ESTRADA DO SUL")
add("sumidouro", 111, 7.5, block=False, pendente=True, ponto="sumidouro", nota="o rio some girando na areia")

# ------------------------------------------------------------------ colisão
blocked |= FUNDA_BLOQ | (AGUA & ~VAU & ~P1 & ~P2)
blocked |= BORDA
blocked &= ~(P1 | P2)
# garante que trilhas e estradas fiquem sempre abertas (exceto prédios)
for p in props:
    pass
# ------------------------------------------------------------------ zonas por tile
ZONAS = [
    dict(id="acampamento_vela", nome="Acampamento da Vela", tipo="base", faccao="vigilia", seguro=True, nivel=None,
         mask=ZCAMP, musica="musica/acampamento_vela", ambiente="ambiente/acampamento_vela",
         eco=dict(clima="ar limpo em volta da Vela (o Amargo assenta no chão), faíscas da lâmpada de arco, fumaça de carvão", neblina=.1,
                  fauna=["ratos nos caixotes", "mariposas na lâmpada", "cachorro magro dormindo (decorativo)"],
                  flora=["nada: vidro da cúpula e cascalho dos trilhos"], cor="âmbar quente contra o azul elétrico da Vela")),
    dict(id="capela_sao_lazaro", nome="Capela de São Lázaro", tipo="base", faccao="arautos", seguro=True, nivel=None,
         mask=ZCHAPEL, musica="musica/capela", ambiente="ambiente/capela_sao_lazaro",
         eco=dict(clima="areia escorrendo das paredes do adro escavado, chama branca nos braseiros, coro abafado debaixo da duna", neblina=.2,
                  fauna=["pombos brancos na torre", "moscas no telhado dos demônios"],
                  flora=["cardos em latas de óleo"], cor="branco frio e vitral verde de areia")),
    dict(id="campos_cinza", nome="Campos de Cinza", tipo="caca", nivel=[1, 3], mask=ZCAMPOS,
         musica="musica/sao_lazaro", ambiente="ambiente/campos_cinza",
         eco=dict(clima="Amargo caindo como neve verde, vento rasteiro levantando cinza, vidro estalando sob os pés", neblina=.25,
                  fauna=["corvos nos postes (voam quando o jogador passa)", "ratos entre as armaduras"],
                  flora=["capim seco raro", "árvores mortas isoladas"], cor="cinza com veios verdes e vidro refletindo")),
    dict(id="vala_comum", nome="A Vala", tipo="caca", nivel=[2, 4], mask=ZVALA,
         musica="musica/sao_lazaro", ambiente="ambiente/vala_comum",
         eco=dict(clima="crateras que a maré de areia desenterra, névoa baixa do brejo amargo", neblina=.4,
                  fauna=["sapos (só som)", "moscas sobre as valas", "uivos da matilha"],
                  flora=["juncos e taboas só na beira do rio"], cor="verde podre e lama")),
    dict(id="bairro_afogado", nome="Bairro Afogado", tipo="exploracao", nivel=[1, 3], mask=ZBAIRRO,
         musica="musica/sao_lazaro", ambiente="ambiente/noite_vento",
         eco=dict(clima="telhados saindo da areia, vento assobiando nas chaminés, janelas que levam para baixo", neblina=.3,
                  fauna=["ratos", "corvos nas chaminés"], flora=["nenhuma"], cor="telha queimada e areia cinza")),
    dict(id="cemiterio_sao_lazaro", nome="Cemitério de São Lázaro", tipo="caca", nivel=[3, 5], mask=ZCEM,
         musica="musica/sao_lazaro", ambiente="ambiente/cemiterio",
         eco=dict(clima="lápides que a duna cobre e descobre, velas que não apagam, sino rachado batendo sozinho; à noite os Não-Julgados brilham verde", neblina=.45,
                  fauna=["corvos nos ciprestes", "gato preto que some (easter egg)"],
                  flora=["árvores mortas", "cardos roxos no túmulo do Firmino"], cor="azul frio, brilho verde e pontos de vela")),
    dict(id="mata_cardos", nome="Mata dos Cardos", tipo="transicao", nivel=[2, 4], mask=ZCARDOS,
         musica="musica/sao_lazaro", ambiente="ambiente/noite_vento",
         eco=dict(clima="vento nos espinhos, sementes de cardo voando", neblina=.3,
                  fauna=["mariposas", "corvos"], flora=["cardos roxos (a única planta que gosta do Amargo)", "arbustos de espinho"],
                  cor="roxo apagado")),
    dict(id="rio_amargo", nome="Rio Amargo", tipo="rio", nivel=None, mask=AGUA | MARGEM | LEITO,
         musica=None, ambiente="ambiente/noite_vento",
         eco=dict(clima="o Jordão secou: leito rachado com um canal de lama amarga que abre em poças verdes e brilha à noite; abaixo do esgoto do abatedouro a lama fica vermelha", neblina=.45,
                  fauna=["esqueletos de peixe no barro", "moscas", "sapos mutantes (só som)"],
                  flora=["juncos secos", "plantas mutantes que bebem o Amargo", "árvores mortas na barranca"], cor="verde tóxico; vermelho rio abaixo")),
    dict(id="bosque_viuvas", nome="Bosque das Viúvas", tipo="caca", nivel=[4, 5], mask=ZWOOD,
         musica="musica/sao_lazaro", ambiente="ambiente/noite_vento",
         eco=dict(clima="mata morta na curva do leito: troncos secos de pé, galhos rangendo, cogumelos e plantas mutantes acesos de verde", neblina=.4,
                  fauna=["corvos", "corujas (som)", "mariposas verdes"],
                  flora=["árvores mortas", "plantas mutantes", "arbustos queimados", "cogumelos pálidos"], cor="cinza-osso com brilho verde")),
    dict(id="abatedouro_carnica", nome="Abatedouro Carniça", tipo="caca", nivel=[4, 7], mask=ZABAT | ZPIG,
         musica="musica/sao_lazaro", ambiente="ambiente/abatedouro",
         eco=dict(clima="frigorífico enterrado até o 2º andar, fumaça das chaminés que ninguém alimenta, chão grudento", neblina=.35,
                  fauna=["moscas em nuvem", "ratos gordos", "porcos grunhindo nos chiqueiros"],
                  flora=["nenhuma: lama e sebo"], cor="vermelho de fornalha e ferrugem")),
    dict(id="tempestade_areia", nome="Tempestade de Areia", tipo="limite", nivel=None, mask=TEMPESTADE,
         musica=None, ambiente="ambiente/noite_vento",
         eco=dict(clima="parede de areia e Amargo que nunca baixa; visão cai, o contador estala e o Amargo fere quem continua", neblina=.95,
                  fauna=[], flora=[], cor="verde-acinzentado opaco")),
]
ZID = np.full((N, N), ".", dtype="<U1")
COD = {}
for i, z in enumerate(reversed(ZONAS)):
    c = "abcdefghijk"[len(ZONAS) - 1 - i]; COD[c] = z["id"]; ZID[z["mask"]] = c
# rio por cima de tudo que é água
ZID[AGUA] = "abcdefghijk"[[z["id"] for z in ZONAS].index("rio_amargo")]

# ------------------------------------------------------------------ mobs (bem menos e com respiro)
SP = []
def mob(kind, nivel, x, y, count, raio, **kw):
    SP.append({"kind": kind, "level": nivel, "x": x, "y": y, "count": count, "radius": raio, **kw})
# Cada grupo tem um motivo (lore + ecossistema). Níveis dentro da faixa de design/combate/mobs.json.
# Campos de Cinza (carnical 1-3, corvo 1-3): os Carniçais reviram a terra atrás dos mortos da Grande Batalha;
# os corvos só existem onde há ninho (postes tortos) e voam em volta dele.
mob("carnical", 1, 38, 35, 2, 2.5, motivo="Primeiro mob da Vigília. Dois Carniçais cavando a cova rasa de um soldado na beira do campo, à vista do portão leste do acampamento.")
mob("carnical", 1, 32, 83, 2, 2.5, motivo="Primeiro mob dos Arautos. Reviram as armaduras caídas no fim do campo, logo abaixo do adro da capela.")
mob("corvo_de_cinza", 1, 28, 47, 2, 2, ancora="ninhos_corvo", motivo="Defendem o ninho do poste torto mais perto do acampamento.")
mob("corvo_de_cinza", 1, 29, 77, 2, 2, ancora="ninhos_corvo", motivo="Defendem o ninho mais perto da capela.")
mob("carnical", 2, 42, 37, 3, 3, motivo="Comendo os mortos que restam no Campo das Penas, onde caíram os anjos.")
mob("carnical", 2, 26, 60, 2, 3, motivo="Rondam o poço seco, onde jogaram corpos na noite da batalha.")
mob("corvo_de_cinza", 2, 40, 64, 3, 2, ancora="ninhos_corvo", motivo="Ninho do meio do campo, o mais disputado.")
mob("carnical", 3, 49, 62, 3, 3, motivo="Bando maior em volta do bonde tombado e do Marco do Corte: ali morreu mais gente e há mais o que comer.")
mob("corvo_de_cinza", 3, 51, 49, 3, 2, ancora="ninhos_corvo", motivo="Ninho perto do esconderijo do Tobias (o ninho gigante). Os corvos roubaram as coisas brilhantes que estão no baú.")
mob("cao_de_vala", 2, 17, 49, 2, 2, motivo="Dois cães da matilha que sobem da Vala pelos becos entre os telhados enterrados atrás de ratos. O primeiro Cão de Vala que a Vigília encontra.")
# A Vala (cao_de_vala 2-4): valas de enterro em massa na várzea; a matilha mora no bueiro desabado.
mob("cao_de_vala", 2, 54, 20, 3, 2.5, motivo="Batedores da matilha na entrada da Vala, perto da trilha que vem do acampamento.")
mob("cao_de_vala", 3, 61, 33, 3, 2.5, motivo="Disputam ossos na vala aberta do norte.")
mob("carnical", 3, 60, 25, 2, 3, motivo="Carniçais cavando a vala do meio; os cães toleram porque eles desenterram comida.")
mob("cao_de_vala", 4, 67, 18, 4, 3, motivo="A toca da matilha no bueiro desabado. O maior grupo da Vala; o uivo de fuga chama os outros.")
# Cemitério (nao_julgado 3-5): os mortos que levantaram para o Juízo e esperam em fila entre as lápides.
mob("nao_julgado", 3, 53, 82, 2, 2, motivo="Esperando no portão da Rua do Sino, os primeiros que o jogador encontra.")
mob("nao_julgado", 4, 61, 94, 3, 0.5, formacao="fila", direcao=[1, 0], motivo="A fila dos Não-Julgados, parada de frente para a torre do sino, esperando o Juízo que não veio.")
mob("nao_julgado", 4, 66, 82, 2, 2.5, motivo="Junto às covas abertas de dentro para fora, de onde acabaram de sair.")
mob("nao_julgado", 5, 50, 95, 2, 2, motivo="Em volta da Subida da Torre, os mais antigos do cemitério.")
mob("corvo_de_cinza", 3, 63, 90, 2, 2, motivo="Corvos pousados nas árvores mortas do centro do cemitério.")
# Bosque das Viúvas (margem leste, 4-5): onde as viúvas da batalha se enforcaram; ponte para o abatedouro.
mob("nao_julgado", 4, 90, 95, 2, 3, motivo="Viúvas da Grande Batalha que atravessaram a Ponte dos Enforcados e ficaram no bosque.")
mob("cao_de_vala", 4, 106, 88, 3, 3, motivo="Matilha que desce o rio comendo o que os porcos deixam; liga a Vala ao abatedouro.")
mob("corvo_de_cinza", 3, 96, 84, 3, 2.5, motivo="Ninho na copa das árvores na saída da ponte.")
mob("nao_julgado", 5, 103, 100, 2, 2, motivo="Guardam a Árvore dos Enforcados e o baú de oferendas aos pés dela.")
# Chiqueiros e Abatedouro (porco 4-6, acougueiro 5-8, capataz 7)
mob("porco_pestilento", 4, 96, 61, 2, 2, motivo="Dentro do chiqueiro oeste, o mais perto da trilha. As cercas dão parede para a investida bater e o porco ficar tonto.")
mob("porco_pestilento", 5, 103, 59, 2, 2, motivo="Chiqueiro leste.")
mob("porco_pestilento", 6, 100, 68, 2, 2, motivo="Chiqueiro dos fundos, os porcos mais gordos.")
mob("acougueiro_oco", 5, 92, 42, 1, 1, motivo="Trabalhando no varal de ganchos da fachada oeste, perto da Ponte do Bonde.")
mob("acougueiro_oco", 6, 95, 27, 1, 1, motivo="Carneando no pátio sul, onde chega o Vau do Sebo.")
mob("porco_pestilento", 6, 106, 30, 1, 2, motivo="Porco que escapou do chiqueiro e fuça os restos atrás do galpão.")
mob("acougueiro_oco", 7, 108, 40, 1, 1, motivo="Guarda os tanques de sebo, onde está o baú do Tobias.")
mob("capataz_gancho", 7, 103, 33, 1, 0, elite=True, motivo="Elite de fim de área, no pátio do escritório. Fica com a chave do porão da cripta. Renasce em 300 s.")
# Patrulhas de facção (cada uma só existe para a facção inimiga): andam pela trilha entre os pontos.
mob("patrulha_vigilia", 4, 24, 76, 2, 0, patrulha=[[24, 76], [20, 66], [30, 66], [36, 72]], so_para="arautos", motivo="Saqueadores da Vigília catando sucata no lado da capela.")
mob("patrulha_arauto", 4, 30, 42, 2, 0, patrulha=[[30, 42], [22, 48], [34, 52], [40, 44]], so_para="vigilia", motivo="Fanáticos da Capela rondando o lado do acampamento.")
mob("patrulha_arauto", 6, 66, 52, 2, 0, patrulha=[[66, 52], [70, 60], [72, 46]], so_para="vigilia", motivo="Fanáticos vigiando a cabeceira oeste da Ponte do Bonde.")
mob("patrulha_vigilia", 6, 64, 80, 2, 0, patrulha=[[64, 80], [68, 74], [72, 84]], so_para="arautos", motivo="Saqueadores na cabeceira oeste da Ponte dos Enforcados.")
# raro de missão
mob("filho_de_cardo", 6, 49, 86, 1, 0, so_por_missao="s02", motivo="Só aparece na missão s02, quando o caldo é derramado no túmulo de Firmino Cardo.")

# ------------------------------------------------------------------ NPCs
npcs = []
PT = {p.get("ponto"): (p["x"], p["y"]) for p in props if p.get("ponto")}
def npc(i, ponto, dx=0, dy=-1.6, olha=None):
    x, y = PT[ponto]; npcs.append({"id": i, "ponto": ponto, "x": round(x + dx, 2), "y": round(y + dy, 2), **({"olha": olha} if olha else {})})
npc("capita_odete", "posto_odete", 0, -1.6)
npc("doutor_anselmo", "barraca_anselmo", 1.8, 0)
npc("mae_cardo", "caldeirao_cardo", 0, 1.2)
npc("tobias_pavio", "carrinho_tobias", -1.2, 0)
npc("gaspar_bigorna", "forja_bigorna", -1.4, 0)
npc("madre_ivone", "pulpito_ivone", 0, 0)
npc("comandante_abdiel", "nave_abdiel", 0, 0)
npc("malfas", "patio_malfas", 1.6, 0)
npc("irmao_lucio", "sacristia_lucio", 0, 0)
npc("simao_coveiro", "casa_simao", 0, -2.8)

# ------------------------------------------------------------------ baús e objetos
baus = [{"id": p["bau"], "x": p["x"], "y": p["y"], "kind": p["kind"], **({"tipo": p["tipo_bau"]} if p.get("tipo_bau") else {})}
        for p in props if p.get("bau")]
mundo_baus = {"bau_mundo_barco": ("Barco Afundado do Balseiro", "comum", "Debaixo do banco do barco, uma lata de querosene cheia de moedas e um terço de dente de cão."),
              "bau_mundo_moinho": ("Arca do Moinho Parado", "raro", "O rio secou e a roda parou com a arca presa entre as pás. Dentro, farinha preta e um embrulho de oleado."),
              "bau_mundo_viuvas": ("Oferenda das Viúvas", "raro", "Ao pé da árvore, um baú cheio de alianças, lenços e cartas que nunca foram mandadas."),
              "bau_mundo_sotao": ("Sótão Afogado", "comum", "Pela janela, um sótão cheio de areia até o teto. No canto que a areia não pegou, uma mala de viagem fechada com cinto."),
              "bau_mundo_chiqueiro": ("Caixa do Tratador", "comum", "Atrás do barraco, a caixa de ferramentas do tratador. Ele não volta para buscar.")}
for b in baus:
    if b["id"] in mundo_baus:
        n, t, txt = mundo_baus[b["id"]]; b.update(nome=n, tipo=t, tabela="bau_area_inicial_" + t, texto_ao_abrir=txt, novo=True)
objetos = [{"id": p["objeto"], "x": p["x"], "y": p["y"]} for p in props if p.get("objeto")]

# ------------------------------------------------------------------ luzes
luzes = []
for p in props:
    if p.get("light"):
        luzes.append([p["x"], p["y"]] + p["light"])
    for e in p.get("luzes_extra", []): luzes.append(e)

# ------------------------------------------------------------------ sons pontuais do mundo
sons = [
    {"som": "ambiente/pontual/sino_distante", "x": CEM[0] - 2, "y": CEM[1] + 9, "raio": 30, "intervalo_s": [40, 90]},
    {"som": "ambiente/pontual/coro_distante", "x": CHAPEL[0], "y": CHAPEL[1], "raio": 26, "intervalo_s": [30, 70]},
    {"som": "ambiente/pontual/corvo_distante", "x": 38, "y": 56, "raio": 24, "intervalo_s": [12, 30]},
    {"som": "ambiente/pontual/uivo_distante", "x": 67, "y": 18, "raio": 34, "intervalo_s": [25, 60]},
    {"som": "ambiente/pontual/porta_distante", "x": ABAT[0], "y": ABAT[1], "raio": 22, "intervalo_s": [20, 50]},
    {"som": "ambiente/pontual/trovao_distante", "x": 60, "y": 118, "raio": 200, "intervalo_s": [60, 160]},
    {"som": "ambiente/pontual/caixinha_distante", "x": ABAT[0] + 8, "y": ABAT[1] - 5, "raio": 8, "intervalo_s": [45, 90], "nota": "dica do baú do Tobias no tanque de sebo"},
    {"som": "rio_correnteza (pendente)", "linha": "rio", "raio": 10},
]

# ------------------------------------------------------------------ validações
proibido = []
for s in SP:
    if s.get("patrulha") or s["kind"] == "filho_de_cardo": continue
    d = D_TRILHA[int(s["x"]), int(s["y"])]; d7 = D_L7[int(s["x"]), int(s["y"])]
    if blocked[int(s["x"]), int(s["y"])]: proibido.append(("spawn bloqueado", s))
    s["_dist_trilha"] = round(float(min(d, d7)), 1)
# caminho entre todos os pontos importantes (BFS no grid de colisão)
def alcancavel(a):
    seen = np.zeros((N, N), bool); q = [a]; seen[a] = True
    while q:
        x, y = q.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            u, v = x + dx, y + dy
            if 0 <= u < N and 0 <= v < N and not seen[u, v] and not blocked[u, v]:
                seen[u, v] = True; q.append((u, v))
    return seen
SPAWN = (CAMP[0] + 2.5, CAMP[1] - 2.0)
ok = alcancavel((int(SPAWN[0]), int(SPAWN[1])))
for nome, (x, y) in [("capela", (CHAPEL[0], CHAPEL[1] - 9)), ("cemiterio", (CEM[0], CEM[1] - 5)), ("vala", (58, 24)),
                     ("abatedouro", (ABAT[0] - 1, ABAT[1] - 10)), ("bosque", (95, 92)), ("chiqueiro", (95, 57)),
                     ("bonde", (TRAM[0], TRAM[1] - 3)), ("moinho", (58, 103)), ("vau", (80, 30))]:
    if not ok[int(x), int(y)]: proibido.append(("inalcançável", nome, x, y))
def encaixa(x, y, rmax=6):
    """Ponto livre e alcançável mais perto de (x, y)."""
    if ok[int(x), int(y)]: return x, y
    best = None
    for dx in range(-rmax, rmax + 1):
        for dy in range(-rmax, rmax + 1):
            u, v = int(x) + dx, int(y) + dy
            if 0 <= u < N and 0 <= v < N and ok[u, v] and (best is None or dx * dx + dy * dy < best[0]):
                best = (dx * dx + dy * dy, u + .5, v + .5)
    return (best[1], best[2]) if best else (x, y)
proibido = [p for p in proibido if p[0] != "spawn bloqueado"]
for s in SP:
    s["x"], s["y"] = encaixa(s["x"], s["y"])
    if "patrulha" in s: s["patrulha"] = [list(encaixa(*p)) for p in s["patrulha"]]
    if not ok[int(s["x"]), int(s["y"])]: proibido.append(("spawn inalcançável", s["kind"], s["x"], s["y"]))
    s["_dist_trilha"] = round(float(min(D_TRILHA[int(s["x"]), int(s["y"])], D_L7[int(s["x"]), int(s["y"])])), 1)
for n_ in npcs:
    n_["x"], n_["y"] = encaixa(n_["x"], n_["y"], 3)
for b in baus:
    near = ok[max(0, int(b["x"]) - 1):int(b["x"]) + 2, max(0, int(b["y"]) - 1):int(b["y"]) + 2].any()
    if not near: proibido.append(("baú inalcançável", b["id"]))
for n_ in npcs:
    if not ok[int(n_["x"]), int(n_["y"])]: proibido.append(("npc inalcançável", n_["id"]))
from collections import Counter
_q = Counter(o["id"] for o in [{"id": p["objeto"]} for p in props if p.get("objeto")])
for oid, qtd in {"corpo_lacrado": 6, "covas_abertas": 8, "ninhos_corvo": 5}.items():
    if _q[oid] != qtd: proibido.append(("quantidade errada", oid, _q[oid], qtd))
print("problemas:", proibido if proibido else "nenhum")

# ------------------------------------------------------------------ Amargo (radiação) por tile, 0 a 9
# 0 = ar limpo da Vela; 2 = deserto comum; contador começa a estalar em 4; a partir de 7 o Amargo fere.
AM = np.full((N, N), 2.0)
AM += (ZVALA | AGUA | MARGEM).astype(float) * 1 + ZCEM * 1 + ZCAMPOS * .5
dt = ndimage.distance_transform_edt(~TEMP_BLOQ)
AM = np.maximum(AM, np.where(TEMPESTADE, 9 - np.clip(dt, 0, 10) * .55, 0))
db = ndimage.distance_transform_edt(~(PRECIPICIO | DUNAS | DUNAS_SUL))
AM += np.clip(3 - db, 0, 3)
AM[np.hypot(XX - CAMP[0], YY - CAMP[1]) < 12] = 0
AM[ZCHAPEL] = np.minimum(AM[ZCHAPEL], 1)
AM = np.clip(np.round(AM), 0, 9).astype(int)

# ------------------------------------------------------------------ moldura de cenário (mundo aberto)
M = 20; NT = N + 2 * M
XT, YT = np.meshgrid(np.arange(NT) + .5 - M, np.arange(NT) + .5 - M, indexing="ij")    # coordenadas antigas
def pad(a, v): return np.pad(a, M, mode="constant", constant_values=v)
def padr(a): return np.pad(a, M, mode="reflect")
TT = pad(T, "d")
fora = np.ones((NT, NT), bool); fora[M:M + N, M:M + N] = False
NZ2T_ = np.pad(NZ2, M, mode="reflect"); NZT_ = np.pad(NZ, M, mode="reflect")
TT[fora & (XT < (NZ2T_ - .5) * 10 + 2) & (YT < N + (NZT_ - .5) * 14)] = "h"     # o precipício continua, recortado
BT = pad(blocked, True)
# altura para o render: dunas sobem para fora, o precipício despenca
NZT = padr(NZ); NZ2T = padr(NZ2); NZ3T = padr(NZ3)
dentro = np.zeros((NT, NT), bool); dentro[M:M + N, M:M + N] = ~BORDA
dist_out = ndimage.distance_transform_edt(~dentro)
ALT = np.clip(dist_out, 0, 14) * (.55 + .5 * NZ3T) + np.sin((XT * .7 + YT * .45) + NZ2T * 6) * .9 * (dist_out > 1)
ALT[TT == "h"] = -np.clip(dist_out[TT == "h"], 0, 12) * .9 - 2
ALT += (TT == "u") * (np.sin(XT * .5 + YT * .9 + NZ2T * 5) * .6)
SH = lambda v: round(float(v) + M, 2)
def shp(p): return [SH(p[0]), SH(p[1])] + list(p[2:])

# decoração da moldura (só cenário, tudo intransponível)
extra = []
for _ in range(80):
    x, y = R.uniform(-M + 2, N + M - 2), R.uniform(-M + 2, N + M - 2)
    if 0 <= x < N and 0 <= y < N: continue
    if x < 0 and y <= N: k = R.choice(["telhado_no_abismo", "torre_no_abismo", "telhado_no_abismo"])
    elif y > N: k = R.choice(["ossada_gigante", "torre_vigia_enterrada", "mastro_bonde_naufragado"])
    else: k = R.choice(["mastro_bonde_naufragado", "ossada_gigante", "poste_telegrafo", "arvore_morta"])
    extra.append({"kind": k, "x": round(x, 2), "y": round(y, 2), "pendente": k != "arvore_morta", "decor_moldura": True})

import re as _re
_src = open(os.path.join(AQUI, "..", "..", "..", "assets", "ambiente", "fontes", "assets.py")).read()
KIT = set(_re.findall(r"@asset\([^\n]*\)\s*\ndef (\w+)", _src))
# nomes do kit de ambiente para o que já existe lá (o render volta para os nomes internos)
RENOMEIA = {"salgueiro_chorao": "arvore_morta_grande", "cipreste": "arvore_morta", "taboa": "mato_seco",
            "samambaia_seca": "arbusto_seco", "lirio_negro": "poca_toxica", "peixes_mortos": "ossos_espalhados",
            "telhado_enterrado": "predio_enterrado", "bonde_veleiro_atracado": "bonde_veleiro", "bonde_linha7_tombado": "bonde_queimado",
            "poste_bonde_mastro": "poste_mastro", "mastro_bonde_naufragado": "poste_mastro", "ponte_pedra": "ponte_pedra_ruina",
            "pedras_margem": "pedras_rio", "pedra_vau": "pedras_rio", "tronco_caido": "tronco_margem", "capim_seco": "mato_seco",
            "arbusto_espinhos": "arbusto_seco", "toco": "toco_arvore", "cratera": "cratera_cinza", "armadura_enferrujada": "soldado_morto",
            "claraboia_quebrada": "cupula_estacao"}
for p in props + extra:
    if p["kind"] in RENOMEIA: p["kind"] = RENOMEIA[p["kind"]]
    if p["kind"] == "arvore_retorcida":      # nada vivo e verde: árvore morta, morta grande ou planta mutante do Amargo
        p["kind"] = R.choice(["arvore_morta", "arvore_morta_grande", "arvore_morta", "planta_mutante"])
        if p["kind"] == "planta_mutante": p["light"] = [.45, 1, .35, 1.4]
for p in props + extra:                      # pendente = ainda não existe no kit de ambiente
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
for s_ in SP:
    s_["x"], s_["y"] = SH(s_["x"]), SH(s_["y"])
    if "patrulha" in s_: s_["patrulha"] = [shp(p) for p in s_["patrulha"]]
for n_ in npcs: n_["x"], n_["y"] = SH(n_["x"]), SH(n_["y"])
for b_ in baus: b_["x"], b_["y"] = SH(b_["x"]), SH(b_["y"])
for o_ in objetos: o_["x"], o_["y"] = SH(o_["x"]), SH(o_["y"])
for t_ in trilhas_json: t_["pontos"] = [shp(p) for p in t_["pontos"]]
for so in sons:
    if "x" in so: so["x"], so["y"] = SH(so["x"]), SH(so["y"])
ZIDT = pad(ZID, "#")
AMT = pad(AM, 9)
data = {
    "name": "Paróquia de São Lázaro", "versao": "0.3", "size": NT,
    "_doc": "Mesmo formato do mapa v0.1 (name, size, spawn, safe_zone, props, blocked, spawns) mais camadas novas. "
            "O mapa tem 160x160 tiles: a área jogável é o quadrado 'jogavel' (120x120) e o resto é moldura de cenário bloqueada, "
            "para a câmera nunca mostrar o fim do mundo. "
            "terreno/zonas_grid/amargo: uma string por x (índice = y), um caractere por tile; legendas em terreno_legenda/zonas_legenda. "
            "props com 'camada':'chao' são decalques (desenhar sob personagens); 'pendente': true = arte ainda não existe no kit de ambiente. "
            "Kinds dos props usam os nomes do kit em assets/ambiente/fontes/assets.py.",
    "jogavel": {"x0": M, "y0": M, "x1": M + N, "y1": M + N},
    "camera_limite": {"x0": M - 6, "y0": M - 6, "x1": M + N + 6, "y1": M + N + 6,
                      "nota": "a câmera para antes de chegar no fim da moldura; o que sobra além disso some na névoa da tempestade"},
    "spawn": [SH(SPAWN[0]), SH(SPAWN[1])],
    "spawn_por_faccao": {"vigilia": [SH(SPAWN[0]), SH(SPAWN[1])], "arautos": [SH(CHAPEL[0]), SH(CHAPEL[1] - 9.5)]},
    "safe_zone": {"x": SH(CAMP[0]), "y": SH(CAMP[1]), "radius": 10.5},
    "safe_zones": [{"id": "acampamento_vela", "x": SH(CAMP[0]), "y": SH(CAMP[1]), "radius": 10.5, "faccao": "vigilia"},
                   {"id": "capela_sao_lazaro", "x": SH(CHAPEL[0]), "y": SH(CHAPEL[1]), "radius": 14, "faccao": "arautos"}],
    "terreno_legenda": {"a": "areia", "u": "duna baixa (andável)", "d": "duna alta (bloqueia)", "h": "precipício/abismo (bloqueia)",
                        "y": "vidro derretido", "q": "cúpula de vidro da estação", "s": "leito seco rachado", "t": "terra batida",
                        "z": "cinza (Campos)", "c": "calcamento", "g": "cemiterio", "l": "laje_capela", "m": "chapa_matadouro",
                        "w": "lama amarga funda (bloqueia)", "r": "poça rasa / vau (bloqueia, menos o vau)", "b": "barranca de lama seca", "e": "musgo amargo (seco, mutante)", "p": "brejo",
                        "f": "chao de mata", "v": "terra de vala", "k": "cascalho dos trilhos"},
    "terreno": ["".join(TT[x]) for x in range(NT)],
    "amargo": ["".join(str(v) for v in AMT[x]) for x in range(NT)],
    "amargo_regras": {"0": "ar limpo (Vela)", "4": "contador começa a estalar", "7": "o Amargo fere (dano leve por segundo, sobe até 9)",
                      "tempestade": "na faixa da tempestade a visão cai e o vento empurra de volta"},
    "zonas_legenda": dict({c: z for c, z in COD.items()}, **{"#": "moldura (cenário)"}),
    "zonas": [{k: v for k, v in z.items() if k != "mask"} for z in ZONAS],
    "zonas_grid": ["".join(ZIDT[x]) for x in range(NT)],
    "rio": {"id": "rio_amargo", "nome": "Rio Amargo", "nota": "o Jordão secou; sobrou um canal de lama amarga com poças verdes que vem da tempestade e some no Sumidouro",
            "centro": [[SH(a), SH(b)] for a, b in RIO[::12]],
            "largura": [round(largura[i], 1) for i in range(0, len(RIO), 12)],
            "agua_suja_a_partir_de": [SH(87), SH(36)], "vaus": [{"id": "vau_do_sebo", "x": SH(80), "y": SH(30), "raio": 4}],
            "pontes": [dict({k: v for k, v in p.items() if k not in ("mask", "de", "ate")}, de=shp(p["de"]), ate=shp(p["ate"])) for p in PONTES]},
    "trilhas": trilhas_json,
    "props": props_out,
    "blocked": [[int(a), int(b)] for a, b in np.argwhere(BT)],
    "spawns": SP,
    "npcs": npcs,
    "baus": baus,
    "objetos": objetos,
    "luzes": [shp(l) for l in luzes],
    "sons_pontuais": sons,
    "props_pendentes": pend,
}
json.dump(data, open(os.path.join(AQUI, "..", "area_inicial.json"), "w"), ensure_ascii=False)
FL = np.pad(FLUXO, ((M, M), (M, M), (0, 0)))
pickle.dump(dict(T=TT, AGUA=pad(AGUA, False), FUNDA=pad(FUNDA, False), MARGEM=pad(MARGEM, False), VAU=pad(VAU, False),
                 P1=pad(P1, False), P2=pad(P2, False), FLUXO=FL, D_RIO=pad(D_RIO, 99.0), HALF=np.pad(HALF, M, mode="edge"),
                 ZCEM=pad(ZCEM, False), ZCHAPEL=pad(ZCHAPEL, False), ZWOOD=pad(ZWOOD, False), NZ=NZT, NZ2=NZ2T, NZ3=NZ3T,
                 LINHA7=[(a + M, b + M) for a, b in LINHA7], BORDA=pad(BORDA, True), ALT=ALT, AM=AMT, M=M, N_IN=N,
                 TEMP=pad(TEMPESTADE, False) | (fora & (YT > N)), blocked=BT, data=data, ZID=ZIDT,
                 CENTROS={k: (v[0] + M, v[1] + M) for k, v in dict(acampamento_vela=CAMP, capela_sao_lazaro=CHAPEL, campos_cinza=(34, 58),
                          vala_comum=VALA, cemiterio_sao_lazaro=CEM, abatedouro_carnica=ABAT, bosque_viuvas=WOOD,
                          mata_cardos=(50, 74), chiqueiros=PIG, bairro_afogado=(13, 60)).items()}),
            open(os.path.join(AQUI, "_cena.pkl"), "wb"))
tot = sum(s_["count"] for s_ in SP if not s_.get("so_por_missao"))
print(len(props_out), "props |", int(BT.sum()), "tiles bloqueados |", len(SP), "grupos /", tot, "mobs |", len(pend), "props pendentes")
