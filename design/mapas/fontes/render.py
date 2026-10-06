# Visão geral pintada da Paróquia de São Lázaro (isométrica, mesma orientação do jogo) e o mapa tático.
# Uso: python3 layout.py && python3 render.py      (numpy, scipy, pillow)
# Saída: ../visao_geral.png e ../mapa_tatico.png
import pickle, math, random, os
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

AQUI = os.path.dirname(os.path.abspath(__file__))
C = pickle.load(open(os.path.join(AQUI, "_cena.pkl"), "rb"))
D = C["data"]; N = D["size"]; T = C["T"]
R = random.Random(5)
S = 12                       # px por tile no raster de chão (vista de cima)
k = 12                       # px de meio-tile na tela isométrica
SE = 0.57357644              # sen 35°
PXM = k / 0.70710678         # px por metro
ZV = PXM * 0.81915204        # px por metro de altura
PAD_T, PAD_B, PAD_X = 150, 60, 30
M = C["M"]; NI = C["N_IN"]; MG = 7                    # moldura de cenário e quanto dela entra no quadro
OX = PAD_X + k * 2 * (M - MG); OY = PAD_T + k * SE * 2 * (M - MG) - 130
W = int(k * 2 * (NI + 2 * MG)); H = int(k * SE * 2 * (NI + 2 * MG)) + 150

def iso(x, y, z=0.0):
    return (PAD_X + k * (x + y) - OX, PAD_T + k * SE * (x - y) + N * k * SE - ZV * z - OY)

# ------------------------------------------------------------------ chão (vista de cima, em pixels [x, y])
def up(a, order=1):
    return ndimage.zoom(a.astype(float), S, order=order)
def noise_px(seed, scale, oct=4):
    rng = np.random.default_rng(seed); out = np.zeros((N * S, N * S)); amp = 1; tot = 0
    for o in range(oct):
        s = max(2, int(N * S / scale * 2 ** o))
        g = rng.random((s + 2, s + 2))
        out += ndimage.zoom(g, (N * S) / s, order=3)[:N * S, :N * S] * amp; tot += amp; amp *= .55
    out /= tot; return (out - out.min()) / (out.max() - out.min())
n1 = noise_px(1, 60); n2 = noise_px(2, 14); n3 = noise_px(3, 4, 2)

PAL = {"a": (92, 89, 78), "u": (100, 96, 82), "d": (112, 106, 90), "h": (10, 10, 12), "y": (74, 82, 76),
       "q": (66, 92, 100), "s": (82, 70, 56), "x": (30, 27, 26), "t": (66, 54, 44), "z": (74, 70, 66), "c": (88, 82, 76), "g": (52, 56, 44), "l": (96, 90, 82),
       "m": (78, 56, 50), "w": (24, 44, 22), "r": (40, 60, 34), "b": (70, 60, 48), "e": (84, 80, 58), "p": (42, 50, 36),
       "f": (40, 46, 32), "v": (60, 46, 38), "k": (70, 64, 60)}
col = np.zeros((N, N, 3))
for c, rgb in PAL.items(): col[T == c] = rgb
G = np.stack([ndimage.gaussian_filter(up(col[..., i], 0), 3.2) for i in range(3)], -1)
# textura: manchas grandes + granulado
G *= (0.78 + 0.38 * n1)[..., None]
G *= (0.86 + 0.24 * n2)[..., None]
G += ((n3 - .5) * 16)[..., None]
Tpx = np.repeat(np.repeat(T, S, 0), S, 1)
# calçamento: pedrinhas
yy, xx = np.mgrid[0:N * S, 0:N * S]
cob = ((np.sin(xx * 1.3 + np.sin(yy * .4) * 2) * np.sin(yy * 1.3 + np.sin(xx * .4) * 2)) > .15)
G[(Tpx == "c") & cob] *= .82
G[(Tpx == "l") & ((xx % 18 < 1) | (yy % 18 < 1))] *= .7
G[(Tpx == "m") & ((xx % 14 < 1) | (yy % 24 < 1))] *= .75
# cinza: manchas pretas de queimado e brasas
burn = (n2 > .62) & (Tpx == "z"); G[burn] *= .55
ember = (n3 > .985) & (Tpx == "z"); G[ember] = (150, 60, 25)
# veios verdes do Amargo na areia (brilham à noite)
areia = np.isin(Tpx, ["a", "u", "d", "z"])
veio = areia & (np.abs(n2 - .5) < .012)
G[veio] = G[veio] * .6 + np.array([90, 150, 90]) * .4
# leito seco rachado
crk = (np.abs(np.sin(xx * .35 + n2 * 14) * np.sin(yy * .33 + n1 * 11)) < .07)
G[(Tpx == "s") & crk] *= .55
# vidro derretido: brilho e lascas
G[(Tpx == "y") & (n3 > .86)] = G[(Tpx == "y") & (n3 > .86)] * .5 + np.array([160, 196, 184]) * .5
G[(Tpx == "y") & (n2 < .3)] *= .75
# cúpula de vidro da estação: nervuras de ferro
cup = Tpx == "q"
G[cup & ((xx % 22 < 2) | (yy % 22 < 2))] = (40, 40, 44)
G[cup & (n3 > .7)] = G[cup & (n3 > .7)] * .6 + np.array([140, 180, 190]) * .4
# relvado: tufos
G[(Tpx == "e") & (n3 > .7)] *= np.array([.9, 1.08, .85])
G[(Tpx == "f") & (n2 > .55)] *= np.array([.8, 1.0, .75])
# relevo: morro do cemitério, capela no alto, vale do rio, borda
Hm = C["ALT"].astype(float) * 1.0
Hm += ndimage.gaussian_filter(C["ZCEM"].astype(float), 6) * 3.0
Hm += ndimage.gaussian_filter(C["ZCHAPEL"].astype(float), 6) * 2.0
Hm -= np.clip(1 - C["D_RIO"] / (C["HALF"] + 6), 0, 1) * 2.2
Hm += C["NZ"] * 1.6
Hp = ndimage.gaussian_filter(up(Hm, 1), 6)
gx, gy = np.gradient(Hp)
# luz vindo do fundo-esquerdo da tela (lua): direção (-x, +y)
shade = np.clip(1 + (-gx * 1 + gy * 1) * 7.5, .55, 1.35)
G *= shade[..., None]
# abismo: escurece com a profundidade, beira clara
abis = Tpx == "h"
prof = np.clip(-up(C["ALT"], 1) / 12, 0, 1)
G[abis] = (np.array([34, 32, 30]) * (1 - prof[abis][:, None]) + np.array([4, 4, 6]) * prof[abis][:, None])
beira = abis & ~ndimage.binary_erosion(abis, iterations=4)
G[beira] = G[beira] * .4 + np.array([120, 110, 92]) * .6
# água
AG = up(C["AGUA"], 0) > .5
dep = np.clip(1 - up(C["D_RIO"], 1) / np.maximum(up(C["HALF"], 1), .1), 0, 1)
wcol = np.array([46, 62, 34]) * (1 - dep[..., None]) + np.array([30, 70, 26]) * dep[..., None]      # lama amarga, mais verde onde é poça
FL = C["FLUXO"]
fx = up(FL[..., 0], 1); fy = up(FL[..., 1], 1)
streak = np.sin((xx * fy - yy * fx) * .9 + n2 * 9) * .5 + .5
wcol = wcol + (streak > .95)[..., None] * 10 + (n1[..., None] - .5) * 14 + ((n3 > .9) & (dep > .5))[..., None] * np.array([40, 90, 30])
# sujeira do abatedouro rio abaixo (vermelho oleoso)
suja = np.clip((xx / S - 82 - M) / 6, 0, 1) * np.clip((40 + M - yy / S) / 6, 0, 1)
wcol = wcol * (1 - .55 * suja[..., None]) + np.array([70, 18, 14]) * .55 * suja[..., None]
G[AG] = wcol[AG]
# espuma/beira
edge = AG & ~ndimage.binary_erosion(AG, iterations=3)
G[edge] = G[edge] * .7 + np.array([96, 86, 60]) * .3
# pontes (tábuas / pedra) no raster
for pmask, base in ((C["P1"], (60, 52, 48)), (C["P2"], (86, 84, 80))):
    pm = up(pmask, 0) > .5
    G[pm] = base
    G[pm & (xx % 10 < 2)] *= .7
    G[pm & ~ndimage.binary_erosion(pm, iterations=3)] *= .55
# trilhos da linha 7
im_tmp = Image.new("L", (N * S, N * S)); dt = ImageDraw.Draw(im_tmp)
L7 = C["LINHA7"]
for i in range(0, len(L7) - 1):
    (x0, y0), (x1, y1) = L7[i], L7[i + 1]
    dx, dy = x1 - x0, y1 - y0; l = math.hypot(dx, dy) or 1; nx, ny = -dy / l, dx / l
    for o in (-.45, .45):
        dt.line([((y0 + ny * o) * S, (x0 + nx * o) * S), ((y1 + ny * o) * S, (x1 + nx * o) * S)], fill=255, width=2)
    if i % 3 == 0:
        dt.line([((y0 - ny * .8) * S, (x0 - nx * .8) * S), ((y0 + ny * .8) * S, (x0 + nx * .8) * S)], fill=140, width=3)
rail = np.array(im_tmp).T / 255.0       # PIL guarda [linha=y?] -> desenhamos (col=y, lin=x), transposto para [x, y]
rail = np.array(im_tmp) / 255.0
# im_tmp foi desenhado com coordenadas (col=y*S, lin=x*S) => array [lin, col] = [x, y]
G = G * (1 - rail[..., None] * .55) + np.array([120, 100, 88]) * (rail[..., None] * .45) * (rail[..., None] > .8)
G = np.clip(G, 0, 255)

# ------------------------------------------------------------------ projeção isométrica do chão
ground = Image.fromarray(G.astype(np.uint8))          # array [x, y] -> imagem (lin=x, col=y)
a = S / (2 * k); b = S / (2 * k * SE)
X0, Y0 = PAD_X - OX, PAD_T + N * k * SE - OY
# col = y*S, lin = x*S ;  x = ((X-X0)/k + (Y-Y0)/(k SE))/2 ; y = ((X-X0)/k - (Y-Y0)/(k SE))/2
coef = (a, -b, -a * X0 + b * Y0, a, b, -a * X0 - b * Y0)
img = ground.transform((W, H), Image.AFFINE, coef, resample=Image.BICUBIC, fillcolor=(70, 68, 60))
img = img.convert("RGBA")

# ------------------------------------------------------------------ objetos
props = sorted(D["props"], key=lambda p: (p["x"] - p["y"]))
FP = {"capela_sao_lazaro": (8, 12, 7), "abatedouro_carnica": (10, 8, 5.5), "casa_ruina": (3, 4, 4), "muro_reboco_janela": (3, 4, 3.2),
      "tenda_vigilia": (3, 3, 2.2), "estacao_bonde": (6, 4, 3.5), "casa_coveiro": (5, 4, 3.4), "torre_sino": (3, 3, 10),
      "mausoleu": (3, 3, 2.6), "moinho_ruina": (4, 4, 4.5), "barraco_sucata": (3, 3, 2.4), "entrada_cripta": (3, 3, 1.6),
      "tenda_demonio": (2, 2, 1.8), "tunel_desabado": (3, 4, 2.5), "capelinha_beira": (3, 3, 3.2), "toca_caes": (3, 2, .8),
      "posto_odete": (2, 2, 2.2), "bonde_linha7_parado": (5, 2, 2.4), "bonde_linha7_tombado": (5, 3, 1.8),
      "tanque_sebo": (2, 2, 2.2), "bonde_veleiro_atracado": (5, 2, 2.2), "asa_anjo_caida": (3, 2, .6), "vala_aberta": (6, 2, 0)}
layer = Image.new("RGBA", (W, H)); d = ImageDraw.Draw(layer)
glow = []

def sh(c, f): return tuple(int(max(0, min(255, v * f))) for v in c[:3]) + ((c[3],) if len(c) > 3 else (255,))
def box(x0, y0, x1, y1, h, cor, telhado=None, rh=0, z0=0.0, eixo=None):
    A, B, Cc, Dd = (x0, y0), (x1, y0), (x1, y1), (x0, y1)
    # sombra no chão
    s = [iso(*p) for p in (A, B, Cc, Dd)]
    d.polygon([(px + 6, py + 3) for px, py in s], fill=(0, 0, 0, 90))
    fl = [iso(*A, z0), iso(*B, z0), iso(*B, z0 + h), iso(*A, z0 + h)]           # face y=y0 (esquerda, iluminada)
    fr = [iso(*B, z0), iso(*Cc, z0), iso(*Cc, z0 + h), iso(*B, z0 + h)]          # face x=x1 (direita, sombra)
    d.polygon(fl, fill=sh(cor, 1.0), outline=sh(cor, .45))
    d.polygon(fr, fill=sh(cor, .62), outline=sh(cor, .35))
    top = [iso(*p, z0 + h) for p in (A, B, Cc, Dd)]
    if telhado is None:
        d.polygon(top, fill=sh(cor, .8), outline=sh(cor, .4)); return
    if eixo is None: eixo = "y" if (y1 - y0) >= (x1 - x0) else "x"
    if eixo == "y":
        xm = (x0 + x1) / 2
        r1, r2 = iso(xm, y0, z0 + h + rh), iso(xm, y1, z0 + h + rh)
        d.polygon([iso(x0, y1, z0 + h), iso(x0, y0, z0 + h), r1, r2], fill=sh(telhado, .85), outline=sh(telhado, .4))
        d.polygon([iso(x1, y0, z0 + h), iso(x1, y1, z0 + h), r2, r1], fill=sh(telhado, .55), outline=sh(telhado, .35))
        d.polygon([iso(x0, y0, z0 + h), iso(x1, y0, z0 + h), r1], fill=sh(cor, .92), outline=sh(cor, .4))
    else:
        ym = (y0 + y1) / 2
        r1, r2 = iso(x0, ym, z0 + h + rh), iso(x1, ym, z0 + h + rh)
        d.polygon([iso(x0, y0, z0 + h), iso(x1, y0, z0 + h), r2, r1], fill=sh(telhado, 1.0), outline=sh(telhado, .4))
        d.polygon([iso(x1, y0, z0 + h), iso(x1, y1, z0 + h), r2], fill=sh(cor, .62), outline=sh(cor, .35))
        d.polygon([iso(x0, y1, z0 + h), iso(x1, y1, z0 + h), r2, r1], fill=sh(telhado, .7), outline=sh(telhado, .35))

def janela(x, y, z, cor=(255, 170, 70), r=2):
    px, py = iso(x, y, z); d.rectangle([px - 1, py - r, px + 1, py + r], fill=cor + (255,)); glow.append((px, py, cor, 18))

def arvore_morta(px, py, h=58, cor=(26, 22, 20)):
    def galho(x, y, ang, L, w, nv):
        if nv == 0 or L < 3: return
        x2, y2 = x + math.cos(ang) * L, y - math.sin(ang) * L
        d.line([(x, y), (x2, y2)], fill=cor + (255,), width=max(1, int(w)))
        for da in (-.5 - R.random() * .3, .45 + R.random() * .3):
            galho(x2, y2, ang + da, L * (.62 + R.random() * .12), w * .65, nv - 1)
    d.ellipse([px - 10, py - 3, px + 12, py + 5], fill=(0, 0, 0, 70))
    galho(px, py, math.pi / 2 + R.uniform(-.15, .15), h * .42, 4, 5)

def copa(px, py, h, rr, cor, n=7):
    d.ellipse([px - rr, py - rr * .35, px + rr * 1.3, py + rr * .45], fill=(0, 0, 0, 80))
    d.line([(px, py), (px + R.uniform(-2, 2), py - h * .55)], fill=(30, 24, 20, 255), width=3)
    for i in range(n):
        ox, oy = R.uniform(-rr * .8, rr * .8), R.uniform(-h, -h * .45)
        r = rr * R.uniform(.45, .7)
        d.ellipse([px + ox - r, py + oy - r * .85, px + ox + r, py + oy + r * .85], fill=sh(cor, R.uniform(.75, 1.05)))
    for i in range(3):
        ox, oy = R.uniform(-rr * .5, rr * .2), R.uniform(-h, -h * .75)
        r = rr * .3
        d.ellipse([px + ox - r, py + oy - r * .8, px + ox + r, py + oy + r * .8], fill=sh(cor, 1.35))

def salgueiro(px, py):
    copa(px, py, 40, 15, (52, 60, 42), 6)
    for i in range(16):
        x = px + R.uniform(-15, 15); y0 = py - R.uniform(30, 42)
        d.line([(x, y0), (x + R.uniform(-2, 2), y0 + R.uniform(18, 30))], fill=(66, 76, 52, 220), width=1)

def cipreste(px, py, h=44):
    d.ellipse([px - 6, py - 2, px + 9, py + 3], fill=(0, 0, 0, 80))
    d.polygon([(px - 6, py - 4), (px, py - h), (px + 6, py - 4), (px, py + 1)], fill=(24, 34, 28, 255), outline=(14, 20, 16, 255))
    d.line([(px - 1, py - h + 6), (px - 3, py - 10)], fill=(44, 58, 44, 255), width=2)

def poste(px, py, h, luz=None, quebrado=False):
    top = py - h if not quebrado else py - h * .6
    d.line([(px, py), (px + (5 if quebrado else 0), top)], fill=(30, 28, 26, 255), width=2)
    if luz:
        d.ellipse([px - 2, top - 3, px + 2, top + 1], fill=tuple(int(c * 255) for c in luz[:3]) + (255,))

def segmento(x, y, orient, h, cor, w=1.0, ralo=False):
    if orient == "x": a, b = (x - w / 2, y), (x + w / 2, y)
    else: a, b = (x, y - w / 2), (x, y + w / 2)
    p = [iso(*a), iso(*b), iso(*b, h), iso(*a, h)]
    d.polygon(p, fill=sh(cor, .9 if orient == "x" else .65), outline=sh(cor, .45))
    if ralo:
        for t in (.2, .5, .8):
            q = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
            px, py = iso(*q, h); d.line([(px, py), (px, py - 4)], fill=sh(cor, .6), width=1)

ALIAS = {"predio_enterrado": "telhado_enterrado", "bonde_veleiro": "bonde_veleiro_atracado", "bonde_queimado": "bonde_linha7_tombado",
         "poste_mastro": "poste_bonde_mastro", "ponte_pedra_ruina": "ponte_pedra", "pedras_rio": "pedras_margem", "tronco_margem": "tronco_caido",
         "mato_seco": "capim_seco", "arbusto_seco": "arbusto_espinhos", "toco_arvore": "toco", "cratera_cinza": "cratera",
         "soldado_morto": "armadura_enferrujada", "cupula_estacao": "claraboia_quebrada"}
for p in props:
    kd, x, y = ALIAS.get(p["kind"], p["kind"]), p["x"], p["y"]
    px, py = iso(x, y)
    if p.get("camada") == "chao" or p.get("invisivel"):
        if kd in ("poca_sangue", "poca_sangue_rastro"):
            r = 5 if kd == "poca_sangue" else 9; d.ellipse([px - r, py - r * .5, px + r, py + r * .5], fill=(70, 10, 8, 170))
        elif kd in ("cratera", "cratera_corte"):
            r = 13 if kd == "cratera" else 24
            d.ellipse([px - r, py - r * .55, px + r, py + r * .55], fill=(20, 18, 17, 200), outline=(96, 88, 80, 160))
        elif kd == "vidro_estilhacos":
            for i in range(3):
                qx, qy = px + R.uniform(-6, 6), py + R.uniform(-3, 3); d.line([(qx, qy), (qx + 2, qy - 1)], fill=(170, 220, 200, 200))
        elif kd == "duna_ondulacao":
            for i in range(3):
                d.arc([px - 14, py - 4 + i * 3, px + 14, py + 4 + i * 3], 200, 340, fill=(140, 134, 112, 120))
        elif kd == "claraboia_quebrada":
            d.polygon([iso(x - 1, y - 1), iso(x + 1, y - 1), iso(x + 1, y + 1), iso(x - 1, y + 1)], fill=(14, 20, 24, 200), outline=(150, 190, 200, 200))
        elif kd == "trigo_queimado":
            for i in range(5):
                qx, qy = px + R.uniform(-6, 6), py + R.uniform(-3, 3); d.line([(qx, qy), (qx + 1, qy - 4)], fill=(36, 30, 26, 200))
        elif kd in ("ossos_espalhados", "penas_espalhadas"):
            c = (190, 182, 160, 200) if kd == "ossos_espalhados" else (230, 226, 210, 230)
            for i in range(4):
                qx, qy = px + R.uniform(-5, 5), py + R.uniform(-2, 2); d.line([(qx, qy), (qx + 3, qy)], fill=c)
        elif kd == "cova_aberta":
            d.polygon([iso(x - .5, y - 1), iso(x + .5, y - 1), iso(x + .5, y + 1), iso(x - .5, y + 1)], fill=(18, 12, 10, 230))
        elif kd == "pedra_vau":
            d.ellipse([px - 4, py - 2, px + 4, py + 2], fill=(90, 90, 84, 255))
        elif kd == "poca_toxica":
            d.ellipse([px - 7, py - 3.5, px + 7, py + 3.5], fill=(60, 170, 50, 230)); glow.append((px, py, (90, 255, 70), 12))
        elif kd == "duna_areia":
            d.ellipse([px - 16, py - 5, px + 16, py + 5], fill=(110, 104, 88, 170))
        elif kd == "poca_agua":
            d.ellipse([px - 6, py - 3, px + 6, py + 3], fill=(20, 32, 34, 200))
        continue
    if kd in FP:
        fx_, fy_, h = FP[kd]
        x0, x1, y0, y1 = x - fx_ / 2, x + fx_ / 2, y - fy_ / 2, y + fy_ / 2
        if kd == "vala_aberta":
            w_, h_ = (7 if x < 60 else 6), 2
            pts = [iso(x - w_ / 2, y - h_ / 2), iso(x + w_ / 2, y - h_ / 2), iso(x + w_ / 2, y + h_ / 2), iso(x - w_ / 2, y + h_ / 2)]
            d.polygon(pts, fill=(14, 10, 9, 245), outline=(96, 80, 64, 255))
            for i in range(10):
                qx, qy = iso(x + R.uniform(-w_ / 2.4, w_ / 2.4), y + R.uniform(-.6, .6))
                d.line([(qx, qy), (qx + 3, qy - 1)], fill=(190, 180, 156, 220))
            continue
        if kd == "capela_sao_lazaro":
            # enterrada até as janelas do coro: só telhado e torre saem da areia
            box(x0, y0, x1, y1, 1.6, (92, 86, 80), (40, 38, 44), 4)
            for j in range(-4, 5, 2): janela(x1, y + j, 1.0, (120, 230, 140), 3)
            janela(x, y0, 1.2, (230, 60, 40), 5)
            box(x - 1.3, y0 - 1.4, x + 1.3, y0 + 1.2, 10, (98, 92, 86))
            tx, ty = iso(x, y0 - .1, 10)
            d.polygon([(tx - 17, ty + 8), (tx, ty - 50), (tx + 17, ty + 8)], fill=(44, 42, 50, 255), outline=(20, 20, 24, 255))
            # trombeta partida em chamas brancas no lugar da cruz
            d.line([(tx, ty - 50), (tx + 9, ty - 62)], fill=(200, 180, 120, 255), width=3)
            glow.append((tx + 7, ty - 60, (255, 245, 210), 40)); glow.append((tx + 7, ty - 60, (255, 245, 210), 14))
        elif kd == "abatedouro_carnica":
            box(x0, y0, x1, y1, 1.8, (100, 56, 44), (70, 66, 64), 2.5, eixo="x")
            for i in (-3, -1, 1, 3): janela(x + i, y0, 1.0, (255, 90, 30), 2)
            for (cx_, cy_) in ((x - 2.5, y + 2.5), (x + 2.5, y + 2.0)):
                box(cx_ - .5, cy_ - .5, cx_ + .5, cy_ + .5, 13, (92, 48, 38), z0=0)
                tx, ty = iso(cx_, cy_, 13)
                for s in range(9):
                    r = 6 + s * 3.2
                    d.ellipse([tx - r + s * 7, ty - s * 16 - r * .7, tx + r + s * 7, ty - s * 16 + r * .7], fill=(40, 36, 36, max(20, 110 - s * 11)))
                glow.append((tx, ty, (255, 80, 20), 16))
        elif kd in ("casa_ruina", "muro_reboco_janela"):
            hh = h * R.uniform(.6, 1.5); cc = R.choice([(74, 64, 58), (84, 70, 60), (66, 60, 58), (90, 80, 70)])
            box(x0 + R.uniform(0, .6), y0 + .2, x1 - R.uniform(0, .6), y1 - R.uniform(.2, 1.2), hh, cc, (44, 38, 36) if R.random() < .55 else None, R.uniform(1, 2.2))
            if p.get("light"): janela(x1 - .2, y, 2.2)
        elif kd == "torre_sino":
            box(x0 + .5, y0 + .5, x1 - .5, y1 - .5, h, (86, 84, 82), (40, 40, 46), 3.2)
            janela(x1 - .5, y, 8, (200, 200, 170), 3)
        elif kd == "casa_coveiro":
            box(x0, y0, x1, y1, h, (70, 62, 54), (50, 40, 34), 1.8)
            janela(x, y0, 1.8, (255, 190, 90), 3)
        elif kd == "moinho_ruina":
            box(x0, y0, x1, y1, h, (84, 78, 70), None)
        elif kd in ("tenda_vigilia", "tenda_demonio"):
            c = (96, 86, 64) if kd == "tenda_vigilia" else (90, 32, 28)
            pts = [iso(x0, y0), iso(x1, y0), iso(x1, y1), iso(x0, y1)]; apex = iso(x, y, h)
            d.polygon([(a_ + 5, b_ + 3) for a_, b_ in pts], fill=(0, 0, 0, 80))
            d.polygon([pts[0], pts[1], apex], fill=sh(c, 1)); d.polygon([pts[1], pts[2], apex], fill=sh(c, .65))
        elif kd == "bonde_veleiro_atracado":
            box(x0, y0, x1, y1, h, (120, 40, 30), (60, 60, 62), .5, eixo="x")
            mx, my = iso(x, y, h + .5); d.line([(mx, my), (mx, my - 50)], fill=(60, 50, 40, 255), width=2)
            d.polygon([(mx, my - 50), (mx + 30, my - 18), (mx, my - 10)], fill=(176, 164, 136, 235))
        elif kd in ("bonde_linha7_parado", "bonde_linha7_tombado"):
            c = (120, 40, 30)
            if kd.endswith("tombado"): box(x0, y0, x1, y1, h, c, None)
            else: box(x0, y0, x1, y1, h, c, (60, 60, 62), .5, eixo="x")
        elif kd == "asa_anjo_caida":
            for i in range(14):
                qx, qy = iso(x + R.uniform(-1.4, 1.4), y + R.uniform(-1, 1), R.uniform(0, .6))
                d.ellipse([qx - 5, qy - 2, qx + 5, qy + 2], fill=(222, 216, 196, 255))
            glow.append((px, py - 4, (255, 240, 200), 26))
        else:
            box(x0 + .1, y0 + .1, x1 - .1, y1 - .1, h, (78, 70, 62), (48, 42, 38) if h > 2 else None, .8)
        if kd == "entrada_cripta": glow.append((px, py - 6, (255, 70, 20), 22))
        continue
    if kd in ("telhado_enterrado", "telhado_no_abismo"):
        z0 = 0 if kd == "telhado_enterrado" else -4
        box(x - 1.8, y - 1.3, x + 1.8, y + 1.3, .3, R.choice([(86, 66, 56), (78, 70, 62), (96, 74, 60)]), (70, 44, 36), 1.8, z0=z0, eixo="x")
        if R.random() < .5: box(x + .6, y + .3, x + 1.1, y + .8, 2.6, (80, 60, 52), z0=z0)
    elif kd == "torre_relogio_enterrada":
        box(x - 1.3, y - 1.3, x + 1.3, y + 1.3, 7, (96, 90, 84), (44, 42, 48), 2.5)
        cx_, cy_ = iso(x, y - 1.3, 5.2); d.ellipse([cx_ - 6, cy_ - 6, cx_ + 6, cy_ + 6], fill=(230, 210, 150, 255)); glow.append((cx_, cy_, (255, 210, 140), 22))
    elif kd == "torre_no_abismo":
        box(x - 1, y - 1, x + 1, y + 1, 4, (70, 66, 62), (40, 38, 40), 2, z0=-6)
    elif kd in ("chamine_enterrada",):
        box(x - .35, y - .35, x + .35, y + .35, 2.6, (96, 62, 50))
    elif kd in ("poste_bonde_mastro", "poste_telegrafo", "mastro_bonde_naufragado"):
        d.line([(px, py), (px + 2, py - 34)], fill=(44, 40, 36, 255), width=2)
        if kd == "poste_telegrafo": d.line([(px - 6, py - 30), (px + 9, py - 30)], fill=(44, 40, 36, 255), width=2)
        if kd == "mastro_bonde_naufragado": d.polygon([(px + 2, py - 32), (px + 16, py - 18), (px + 2, py - 12)], fill=(150, 140, 116, 220))
    elif kd in ("ossada_animal", "ossada_viajante", "ossada_gigante"):
        r = 14 if kd == "ossada_gigante" else 5
        for i in range(4 if r > 5 else 1):
            d.arc([px - r + i * 3, py - r * .8, px + r - i * 3, py + r * .3], 200, 340, fill=(206, 198, 176, 255), width=1)
    elif kd == "bonde_veleiro_atracado":
        pass
    elif kd in ("corda_guarda",):
        d.line([iso(x, y - .5, .6), iso(x, y + .5, .6)], fill=(120, 100, 70, 255)); d.line([(px, py), (px, py - 9)], fill=(70, 56, 40, 255))
    elif kd == "guindaste_sucata":
        d.line([(px, py), (px, py - 60)], fill=(70, 50, 40, 255), width=3); d.line([(px, py - 60), (px - 40, py - 48)], fill=(70, 50, 40, 255), width=2)
        d.line([(px - 40, py - 48), (px - 40, py - 10)], fill=(90, 80, 70, 200))
    elif kd in ("torre_vigia_enterrada",):
        d.rectangle([px - 7, py - 14, px + 7, py - 5], fill=(70, 58, 46, 255)); glow.append((px, py - 12, (190, 210, 255), 14))
    elif kd == "barco_encalhado":
        d.polygon([iso(x - 1.4, y), iso(x, y - .6, .4), iso(x + 1.4, y), iso(x, y + .6, .4)], fill=(76, 60, 44, 255), outline=(30, 24, 20, 255))
    elif kd in ("muro_contencao_areia",):
        segmento(x, y, p.get("orient", "x"), 1.2, (110, 92, 70), 1.05)
    elif kd in ("janela_na_areia", "placa_rua_enterrada"):
        d.rectangle([px - 3, py - 6, px + 3, py], fill=(20, 16, 14, 255), outline=(110, 96, 80, 255))
    elif kd in ("arvore_morta",): arvore_morta(px, py)
    elif kd == "arvore_morta_grande": arvore_morta(px, py, 80, (30, 26, 24))
    elif kd == "planta_mutante":
        for i in range(5):
            ox_, oy_ = R.uniform(-6, 6), R.uniform(-14, -4); r_ = R.uniform(2.5, 4.5)
            d.line([(px, py), (px + ox_, py + oy_)], fill=(70, 80, 50, 255), width=2)
            d.ellipse([px + ox_ - r_, py + oy_ - r_, px + ox_ + r_, py + oy_ + r_], fill=(110, 200, 90, 255))
    elif kd == "mar_de_lapides":
        for i in range(6):
            qx, qy = px + R.uniform(-10, 10), py + R.uniform(-4, 4); hh = R.uniform(2, 6)
            d.rectangle([qx - 2, qy - hh, qx + 2, qy], fill=(118, 114, 106, 255))
    elif kd == "arvore_retorcida": copa(px, py, 44, 13, (46, 52, 36))
    elif kd == "arvore_enforcados":
        arvore_morta(px, py, 80, (22, 18, 18))
        for i in range(4):
            qx = px + R.uniform(-22, 22); d.line([(qx, py - 52), (qx, py - 34)], fill=(60, 54, 46, 255)); d.ellipse([qx - 2, py - 36, qx + 2, py - 26], fill=(40, 36, 34, 255))
    elif kd == "salgueiro_chorao": salgueiro(px, py)
    elif kd == "cipreste": cipreste(px, py)
    elif kd in ("juncos", "taboa", "capim_seco"):
        c = {"juncos": (78, 86, 56), "taboa": (70, 74, 48), "capim_seco": (110, 98, 66)}[kd]
        for i in range(5):
            qx = px + R.uniform(-4, 4); d.line([(qx, py), (qx + R.uniform(-2, 2), py - R.uniform(6, 11))], fill=c + (255,))
        if kd == "taboa": d.line([(px, py - 10), (px, py - 13)], fill=(60, 40, 26, 255), width=2)
    elif kd in ("moita_cardo", "arbusto_espinhos", "samambaia_seca"):
        c = {"moita_cardo": (60, 64, 44), "arbusto_espinhos": (44, 40, 32), "samambaia_seca": (92, 74, 46)}[kd]
        d.ellipse([px - 6, py - 7, px + 6, py + 1], fill=c + (255,))
        if kd == "moita_cardo":
            for i in range(3): qx, qy = px + R.uniform(-5, 5), py - R.uniform(4, 9); d.ellipse([qx - 1.5, qy - 1.5, qx + 1.5, qy + 1.5], fill=(150, 70, 170, 255))
    elif kd == "cogumelos_palidos":
        for i in range(3):
            qx, qy = px + R.uniform(-3, 3), py + R.uniform(-1, 1); d.ellipse([qx - 2, qy - 3, qx + 2, qy], fill=(170, 220, 180, 255))
    elif kd in ("tronco_caido", "toco"):
        if kd == "toco": d.ellipse([px - 3, py - 4, px + 3, py], fill=(56, 44, 34, 255))
        else: d.line([iso(x - 1, y - .3), iso(x + 1, y + .3)], fill=(56, 44, 34, 255), width=4)
    elif kd in ("lapide", "lapide_cruz_celta", "tumulo_aberto"):
        c = (120, 118, 112) if kd != "tumulo_aberto" else (100, 96, 90)
        d.rectangle([px - 3, py - 9, px + 2, py], fill=sh(c, 1)); d.rectangle([px + 2, py - 8, px + 3, py], fill=sh(c, .6))
        if kd == "lapide_cruz_celta": d.ellipse([px - 4, py - 13, px + 3, py - 6], outline=sh(c, 1))
        if kd == "tumulo_aberto": d.ellipse([px - 5, py, px + 5, py + 4], fill=(16, 10, 8, 230))
    elif kd == "cruz_madeira":
        d.line([(px, py), (px, py - 11)], fill=(70, 56, 42, 255), width=2); d.line([(px - 3, py - 8), (px + 3, py - 8)], fill=(70, 56, 42, 255), width=2)
    elif kd in ("palicada",):
        segmento(x, y, p.get("orient", "x"), 2.2, (70, 58, 46), 1.1, ralo=True)
    elif kd in ("muro_tijolo", "muro_tijolo_quebrado"):
        segmento(x, y, p.get("orient", "x"), 1.6 if kd == "muro_tijolo" else R.uniform(.6, 1.3), (96, 74, 62), 1.05)
    elif kd in ("cerca_ferro", "cerca_chiqueiro", "cerca_arame_torta", "estacas_cerca"):
        c = {"cerca_ferro": (40, 40, 44), "cerca_chiqueiro": (78, 64, 48), "cerca_arame_torta": (64, 58, 54), "estacas_cerca": (70, 58, 46)}[kd]
        o = p.get("orient", "x")
        a_, b_ = ((x - .5, y), (x + .5, y)) if o == "x" else ((x, y - .5), (x, y + .5))
        for t in (0, .5, 1):
            q = (a_[0] + (b_[0] - a_[0]) * t, a_[1] + (b_[1] - a_[1]) * t); qx, qy = iso(*q); d.line([(qx, qy), (qx, qy - 10)], fill=c + (255,), width=1)
        for z in (.4, .9): d.line([iso(*a_, z), iso(*b_, z)], fill=c + (255,), width=1)
    elif kd in ("barricada_sacos", "sacos_areia"):
        d.ellipse([px - 8, py - 7, px + 8, py + 2], fill=(98, 88, 66, 255), outline=(50, 44, 34, 255))
    elif kd in ("poste_gas", "poste_gas_quebrado", "lanterna_procissao"):
        poste(px, py, 34 if kd != "lanterna_procissao" else 18, p.get("light"), quebrado=kd.endswith("quebrado"))
    elif kd == "lampada_arco":
        d.line([(px, py), (px, py - 70)], fill=(44, 44, 50, 255), width=4)
        d.ellipse([px - 6, py - 78, px + 6, py - 66], fill=(220, 235, 255, 255))
        glow.append((px, py - 72, (180, 210, 255), 70)); glow.append((px, py - 72, (230, 240, 255), 18))
    elif kd == "torre_vigia":
        for o in (-6, 6): d.line([(px + o, py), (px + o * .6, py - 42)], fill=(60, 48, 38, 255), width=2)
        d.rectangle([px - 8, py - 50, px + 8, py - 40], fill=(70, 58, 46, 255))
        glow.append((px, py - 48, (190, 210, 255), 24))
    elif kd in ("tonel_fogo", "fogueira", "braseiro_sagrado"):
        c = (255, 140, 40) if kd != "braseiro_sagrado" else (255, 250, 220)
        d.rectangle([px - 3, py - 7, px + 3, py], fill=(50, 40, 34, 255)); d.ellipse([px - 3, py - 11, px + 3, py - 6], fill=c + (255,))
    elif kd in ("caixas", "barris", "carroca_quebrada", "entulho", "trono_sucata", "cocho", "mesa_acougue_rua", "bancada_ferreiro",
                "caldeirao_cardo", "carrinho_tobias", "roda_dagua_bomba", "varal_roupas", "pulpito_externo", "lama_porcos"):
        c = {"caixas": (100, 78, 52), "barris": (80, 58, 40), "carroca_quebrada": (76, 60, 44), "entulho": (84, 80, 74)}.get(kd, (86, 70, 54))
        if kd == "lama_porcos": d.ellipse([px - 8, py - 3, px + 8, py + 3], fill=(48, 36, 28, 230)); continue
        if kd in ("carroca_quebrada", "entulho"): box(x - .7, y - .5, x + .7, y + .5, .7, c)
        else: box(x - .35, y - .35, x + .35, y + .35, .8, c)
    elif kd in ("poste_ninho", "poste_ninho_gigante"):
        g = kd.endswith("gigante")
        d.line([(px, py), (px + 4, py - (60 if g else 40))], fill=(46, 40, 34, 255), width=2)
        r = 9 if g else 5; cx_, cy_ = px + 4, py - (60 if g else 40)
        d.ellipse([cx_ - r, cy_ - r * .6, cx_ + r, cy_ + r * .6], fill=(40, 34, 28, 255))
    elif kd == "espantalho_arame":
        d.line([(px, py), (px, py - 20)], fill=(60, 52, 44, 255), width=2); d.line([(px - 7, py - 15), (px + 7, py - 15)], fill=(60, 52, 44, 255), width=2)
        d.ellipse([px - 3, py - 25, px + 3, py - 19], fill=(110, 92, 70, 255))
    elif kd in ("armadura_enferrujada", "elmo_espada_fincada"):
        if kd == "elmo_espada_fincada": d.line([(px, py), (px + 1, py - 10)], fill=(120, 110, 100, 255), width=1)
        d.ellipse([px - 3, py - 3, px + 3, py + 1], fill=(96, 60, 40, 255))
    elif kd == "estandarte_rasgado":
        d.line([(px, py), (px, py - 30)], fill=(50, 40, 34, 255), width=2)
        d.polygon([(px, py - 30), (px + 11, py - 28), (px + 8, py - 18), (px + 11, py - 12), (px, py - 14)], fill=(120, 24, 20, 255))
    elif kd in ("gaiola_suspensa", "forca_ponte"):
        d.line([(px, py), (px, py - 30)], fill=(40, 36, 34, 255), width=2); d.line([(px, py - 30), (px + 8, py - 30)], fill=(40, 36, 34, 255), width=2)
        d.rectangle([px + 5, py - 26, px + 11, py - 17], outline=(70, 66, 60, 255))
    elif kd == "vela_tumulo":
        d.line([(px, py), (px, py - 3)], fill=(220, 210, 180, 255), width=2)
    elif kd in ("vala_aberta",):
        pass
    elif kd in ("poco",):
        d.ellipse([px - 7, py - 6, px + 7, py + 1], fill=(80, 76, 70, 255), outline=(40, 38, 36, 255)); d.ellipse([px - 5, py - 5, px + 5, py - 1], fill=(10, 10, 12, 255))
    elif kd.startswith("bau_"):
        c = {"bau_comum": (110, 76, 44), "bau_raro": (50, 46, 50)}.get(kd, (110, 76, 44))
        box(x - .35, y - .25, x + .35, y + .25, .5, c, None)
        glow.append((px, py - 4, (255, 210, 120), 9))
    elif kd in ("ponte_ferro_bonde", "ponte_pedra"):
        comp = p.get("comprimento", 14)
        a_, b_ = (x - comp / 2, y), (x + comp / 2, y)
        cor = (50, 46, 46) if kd == "ponte_ferro_bonde" else (110, 106, 98)
        for o in (-1.6, 1.6):
            d.line([iso(a_[0], y + o, .9), iso(b_[0], y + o, .9)], fill=cor + (255,), width=2)
        if kd == "ponte_ferro_bonde":
            for t in np.linspace(a_[0], b_[0], 9):
                d.line([iso(t, y - 1.6, .9), iso(t + 1.7, y - 1.6, 2.6)], fill=cor + (255,), width=1)
                d.line([iso(t, y + 1.6, .9), iso(t + 1.7, y + 1.6, 2.6)], fill=cor + (255,), width=1)
    elif kd == "roda_dagua":
        d.ellipse([px - 12, py - 26, px + 12, py - 2], outline=(70, 56, 40, 255), width=3)
    elif kd == "cano_esgoto":
        d.ellipse([px - 5, py - 6, px + 5, py + 1], fill=(70, 56, 50, 255)); d.ellipse([px - 3, py - 4, px + 3, py], fill=(20, 8, 6, 255))
    elif kd in ("estatua_anjo_quebrada",):
        d.rectangle([px - 5, py - 6, px + 5, py], fill=(110, 106, 100, 255)); d.polygon([(px - 3, py - 6), (px + 3, py - 6), (px + 2, py - 22), (px - 2, py - 22)], fill=(150, 146, 136, 255))
        d.polygon([(px + 2, py - 20), (px + 14, py - 26), (px + 4, py - 14)], fill=(170, 166, 156, 255))
    elif kd in ("ganchos_carne",):
        d.line([(px - 6, py - 26), (px + 6, py - 26)], fill=(60, 56, 54, 255), width=2)
        for o in (-4, 0, 4): d.ellipse([px + o - 2, py - 24, px + o + 2, py - 12], fill=(130, 40, 36, 255))
    elif kd in ("placa_aviso",):
        d.line([(px, py), (px, py - 12)], fill=(60, 50, 40, 255), width=2); d.rectangle([px - 6, py - 16, px + 6, py - 10], fill=(110, 92, 60, 255))
    elif kd in ("corpo_lacrado",):
        d.ellipse([px - 6, py - 2, px + 6, py + 2], fill=(100, 92, 84, 255)); d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(200, 30, 30, 255))
    elif kd in ("peixes_mortos", "lirio_negro"):
        d.ellipse([px - 2, py - 1, px + 2, py + 1], fill=(160, 160, 150, 200) if kd == "peixes_mortos" else (20, 30, 24, 230))
    elif kd in ("pedras_margem",):
        d.ellipse([px - 4, py - 3, px + 4, py + 1], fill=(84, 82, 76, 255))
    elif kd == "trilho_retorcido":
        d.line([(px - 10, py), (px, py - 14), (px + 6, py - 4)], fill=(110, 90, 80, 255), width=2)
    elif kd == "tanque_sebo":
        box(x - 1, y - 1, x + 1, y + 1, 2, (90, 80, 70))
    if p.get("light"):
        c = p["light"]; glow.append((px, py - 14, tuple(int(v * 255) for v in c[:3]), c[3] * 7))
    for e in p.get("luzes_extra", []):
        qx, qy = iso(e[0], e[1]); glow.append((qx, qy - 10, tuple(int(v * 255) for v in e[2:5]), e[5] * 7))

# poças verdes brilham à noite
_poca = C["AGUA"] & (C["HALF"] > 1.9)
for (px_i, py_i) in np.argwhere(_poca)[::9]:
    sx_, sy_ = iso(px_i + .5, py_i + .5); glow.append((sx_, sy_ - 2, (90, 255, 70), 16))
# ------------------------------------------------------------------ composição: noite, luzes, névoa
base = img.copy()
base.alpha_composite(layer)
arr = np.array(base.convert("RGB")).astype(float)
night = np.array([.60, .66, .66])
arr *= night
# luzes (aditivo)
L = np.zeros_like(arr)
gy_, gx_ = np.mgrid[0:H, 0:W]
for (lx, ly, cor, rr) in glow:
    rr = max(4, rr); x0, x1 = int(max(0, lx - rr * 3)), int(min(W, lx + rr * 3)); y0, y1 = int(max(0, ly - rr * 2)), int(min(H, ly + rr * 2))
    if x0 >= x1 or y0 >= y1: continue
    dx = (gx_[y0:y1, x0:x1] - lx) / rr; dy = (gy_[y0:y1, x0:x1] - ly) / (rr * .6)
    f = np.exp(-(dx * dx + dy * dy) * 1.2)
    L[y0:y1, x0:x1] += f[..., None] * np.array(cor) * .55
arr = arr * (1 + L / 255 * 1.6) + L * .35
# névoa: mais densa sobre o rio, a vala e o cemitério
fogmask = np.zeros((N, N))
for z in D["zonas"]:
    pass
ZID = C["ZID"]; cods = D["zonas_legenda"]
neb = {z["id"]: z["eco"]["neblina"] for z in D["zonas"]}
for c, zid in cods.items(): fogmask[ZID == c] = neb.get(zid, .2) * .6
fogmask[ZID == "."] = .2
fora = (ZID == "#")
dfo = ndimage.distance_transform_edt(fora)
fogmask[fora] = np.clip(.35 + dfo[fora] / 14, 0, 1)
fogmask[C["TEMP"]] = np.maximum(fogmask[C["TEMP"]], .75)
fog_g = ndimage.gaussian_filter(up(fogmask, 1), 20) * (0.6 + 0.5 * n1)
rajada = (np.sin((xx * .9 - yy * .6) * .05 + n2 * 9) * .5 + .5) ** 3
fog_g = np.clip(fog_g + up(C["TEMP"], 1) * rajada * .35, 0, 1.2)
fog_img = Image.fromarray(np.clip(fog_g * 255, 0, 255).astype(np.uint8)).transform((W, H), Image.AFFINE, coef, resample=Image.BILINEAR, fillcolor=255)
fogv = np.array(fog_img).astype(float) / 255
arr = arr * (1 - np.clip(fogv * .62, 0, .92)[..., None]) + np.array([104, 108, 92]) * np.clip(fogv * .62, 0, .92)[..., None]
# a moldura se dissolve em poeira: nenhuma borda dura do mundo aparece
dfo2 = np.where(fora, dfo, 0)
fade = np.clip((dfo2 - 3) / 11, 0, 1) ** 1.3
fade_img = Image.fromarray((ndimage.gaussian_filter(up(fade, 1), 14) * 255).astype(np.uint8)).transform((W, H), Image.AFFINE, coef, resample=Image.BILINEAR, fillcolor=255)
fv = np.array(fade_img).astype(float)[..., None] / 255
po = np.array([92, 94, 80]) * (0.85 + 0.3 * (np.array(Image.fromarray((n1 * 255).astype(np.uint8)).resize((W, H))).astype(float)[..., None] / 255))
arr = arr * (1 - fv) + po * fv
# vinheta
vx = (gx_ / W - .5) * 2; vy = (gy_ / H - .5) * 2
vig = np.clip(1 - (vx ** 2 * .55 + vy ** 2 * .7) ** 1.6 * .55, .35, 1)
arr *= vig[..., None]
# granulação
arr += (np.random.default_rng(3).random(arr.shape[:2]) - .5)[..., None] * 8
final = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")

# ------------------------------------------------------------------ rótulos
FD = AQUI
F_TIT = ImageFont.truetype(os.path.join(FD, "PirataOne-Regular.ttf"), 64)
F_ZONA = ImageFont.truetype(os.path.join(FD, "PirataOne-Regular.ttf"), 38)
F_ZONA_P = ImageFont.truetype(os.path.join(FD, "PirataOne-Regular.ttf"), 28)
F_SUB = ImageFont.truetype(os.path.join(FD, "IMFeENit28P.ttf"), 22)
F_PEQ = ImageFont.truetype(os.path.join(FD, "IMFeENrm28P.ttf"), 17)
F_SC = ImageFont.truetype(os.path.join(FD, "IMFeENsc28P.ttf"), 22)

def texto(dr, xy, t, f, cor=(226, 210, 176), anchor="mm", stroke=3):
    dr.text(xy, t, font=f, fill=cor + (255,), anchor=anchor, stroke_width=stroke, stroke_fill=(8, 6, 6, 235))

def rotulos(im, tatico=False):
    dr = ImageDraw.Draw(im)
    CT = C["CENTROS"]
    ZN = {"acampamento_vela": ("Acampamento da Vela", "Vigília · zona segura", (-4, -6)),
          "bairro_afogado": ("Bairro Afogado", "telhados na areia", (0, 0)),
          "capela_sao_lazaro": ("Capela de São Lázaro", "Arautos · zona segura", (8, -2)),
          "campos_cinza": ("Campos de Cinza", "nível 1 a 3", (0, 0)),
          "vala_comum": ("A Vala", "nível 2 a 4", (-2, -6)),
          "cemiterio_sao_lazaro": ("Cemitério de São Lázaro", "nível 3 a 5", (6, 4)),
          "abatedouro_carnica": ("Abatedouro Carniça", "nível 5 a 7 · entrada da cripta", (8, 4)),
          "bosque_viuvas": ("Bosque das Viúvas", "nível 4 a 5", (-2, -4)),
          "chiqueiros": ("Chiqueiros", "nível 4 a 6", (5, 4)),
          "mata_cardos": ("Mata dos Cardos", "", (-1, 2))}
    for zid, (nome, sub, (ox, oy)) in ZN.items():
        x, y = CT[zid]; sx, sy = iso(x + ox, y + oy)
        f = F_ZONA if zid not in ("chiqueiros", "mata_cardos", "bairro_afogado") else F_ZONA_P
        texto(dr, (sx, sy - 70), nome, f)
        if sub: texto(dr, (sx, sy - 40), sub, F_SUB, (190, 176, 150), stroke=2)
    # rio e pontos de interesse
    for (x, y, t) in [(70, 108, "Rio Amargo · leito seco"), (98, 14, "o rio desce vermelho do esgoto")]:
        sx, sy = iso(x + M, y + M); texto(dr, (sx, sy), t, F_SUB, (150, 180, 186), stroke=2)
    for (x, y, t) in [(81, 54.5, "Ponte do Bonde"), (75.5, 89.5, "Ponte dos Enforcados"), (80, 34, "Vau do Sebo"),
                      (45, 60.5, "Bonde tombado · Marco do Corte"), (43, 42.5, "Campo das Penas"), (63, 107.5, "Moinho Parado"),
                      (104, 103.5, "Árvore dos Enforcados"), (29, 66.5, "Poço Seco"), (111, 5, "Sumidouro"),
                      (8, 31.5, "a Linha 7 cai no abismo"), (99, 27, "porta do porão · Cripta"), (12, 61, "Relógio Afogado"),
                      (40, 7.5, "Estrada do Sul (engolida)")]:
        sx, sy = iso(x + M, y + M); texto(dr, (sx, sy), t, F_PEQ, (206, 196, 170), stroke=2)
    for (x, y, t) in [(60, 124, "Tempestade de Areia"), (-6, 64, "Precipício da Cidade Velha"), (126, 60, "Mar de Dunas")]:
        sx, sy = iso(x + M, y + M); texto(dr, (sx, sy), t, F_ZONA_P, (196, 200, 170), stroke=3)
        texto(dr, (sx, sy + 26), "limite do mapa", F_PEQ, (170, 170, 150), stroke=2)
    # título
    texto(dr, (60, 64), "Paróquia de São Lázaro", F_TIT, (232, 214, 170), anchor="lm", stroke=4)
    texto(dr, (64, 112), "área inicial · níveis 1 a 8 · level design v0.3 · Deserto de Absinto" + (" · mapa tático" if tatico else ""), F_SUB, (180, 166, 140), anchor="lm", stroke=2)
    # rosa: frente da câmera
    texto(dr, (W - 60, H - 40), "DARK PASSAGE", F_SC, (150, 40, 34), anchor="rm", stroke=2)

vis = final.copy(); rotulos(vis)
vis.convert("RGB").save(os.path.join(AQUI, "..", "visao_geral.png"), optimize=True)

# ------------------------------------------------------------------ mapa tático
tat = Image.fromarray((np.array(final.convert("RGB")).astype(float) * .62).astype(np.uint8)).convert("RGBA")
ov = Image.new("RGBA", (W, H)); o = ImageDraw.Draw(ov)
def ell(x, y, r, fill=None, outline=None, w=2):
    pts = [iso(x + r * math.cos(a), y + r * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40)]
    o.polygon(pts, fill=fill, outline=outline);
    if outline: o.line(pts + [pts[0]], fill=outline, width=w)
# zonas seguras
for z in D["safe_zones"]: ell(z["x"], z["y"], z["radius"], fill=(60, 120, 220, 34), outline=(120, 170, 255, 200))
# trilhas (nomes)
NOMES_MOB = {"carnical": "Carniçal", "corvo_de_cinza": "Corvo de Cinza", "cao_de_vala": "Cão de Vala", "nao_julgado": "Não-Julgado",
             "porco_pestilento": "Porco Pestilento", "acougueiro_oco": "Açougueiro Oco", "capataz_gancho": "Capataz Gancho (elite)",
             "patrulha_arauto": "Fanático (só p/ Vigília)", "patrulha_vigilia": "Saqueador (só p/ Arautos)", "filho_de_cardo": "Filho de Cardo (missão)"}
CORN = {1: (240, 230, 120), 2: (240, 200, 90), 3: (240, 160, 70), 4: (240, 120, 60), 5: (230, 80, 50), 6: (210, 50, 50), 7: (190, 30, 60)}
for s in D["spawns"]:
    c = CORN.get(s["level"], (200, 200, 200))
    if s.get("patrulha"):
        pts = [iso(*p) for p in s["patrulha"]] + [iso(*s["patrulha"][0])]
        for i in range(len(pts) - 1):
            (ax_, ay_), (bx_, by_) = pts[i], pts[i + 1]
            for t in np.arange(0, 1, .12):
                o.line([(ax_ + (bx_ - ax_) * t, ay_ + (by_ - ay_) * t), (ax_ + (bx_ - ax_) * (t + .06), ay_ + (by_ - ay_) * (t + .06))], fill=(170, 140, 255, 230), width=2)
        c = (170, 140, 255)
    ell(s["x"], s["y"], max(1.2, s["radius"] + .8), fill=c + (60,), outline=c + (230,))
for s in D["spawns"]:
    c = (170, 140, 255) if s.get("patrulha") else CORN.get(s["level"], (200, 200, 200))
    sx, sy = iso(s["x"], s["y"])
    lbl = f"{NOMES_MOB.get(s['kind'], s['kind'])} ×{s['count']} · Nv {s['level']}"
    o.text((sx, sy - 16), lbl, font=F_PEQ, fill=c + (255,), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0, 255))
NOME_NPC = {"capita_odete": "Odete", "doutor_anselmo": "Anselmo", "mae_cardo": "Mãe Cardo", "tobias_pavio": "Tobias", "gaspar_bigorna": "Gaspar",
            "madre_ivone": "Ivone", "comandante_abdiel": "Abdiel", "malfas": "Malfas", "irmao_lucio": "Lúcio", "simao_coveiro": "Simão"}
for n_ in D["npcs"]:
    sx, sy = iso(n_["x"], n_["y"])
    o.polygon([(sx, sy - 7), (sx + 6, sy), (sx, sy + 7), (sx - 6, sy)], fill=(255, 210, 90, 255), outline=(60, 40, 0, 255))
    o.text((sx + 9, sy), NOME_NPC[n_["id"]], font=F_PEQ, fill=(255, 220, 130, 255), anchor="lm", stroke_width=2, stroke_fill=(0, 0, 0, 255))
for b in D["baus"]:
    sx, sy = iso(b["x"], b["y"])
    o.rectangle([sx - 6, sy - 5, sx + 6, sy + 4], fill=(90, 220, 140, 255), outline=(0, 40, 10, 255))
for ob in D["objetos"]:
    sx, sy = iso(ob["x"], ob["y"])
    o.ellipse([sx - 4, sy - 4, sx + 4, sy + 4], fill=(120, 220, 255, 255), outline=(0, 30, 50, 255))
# nomes das trilhas
for t in D["trilhas"]:
    if t["id"] in ("vau_do_sebo", "linha_7"): continue
    pts = t["pontos"]; m = pts[len(pts) // 2]
    sx, sy = iso(*m)
    o.text((sx, sy + 12), t["nome"], font=F_PEQ, fill=(200, 200, 200, 230), anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0, 255))
tat.alpha_composite(ov); rotulos(tat, True)
# legenda
lg = ImageDraw.Draw(tat)
lx, ly = W - 430, H - 330
lg.rectangle([lx, ly, lx + 400, ly + 280], fill=(12, 10, 10, 225), outline=(120, 100, 70, 255), width=2)
texto(lg, (lx + 20, ly + 26), "Legenda", F_ZONA_P, anchor="lm")
itens = [("círculo", "grupo de monstros (cor = nível 1 amarelo até 7 vinho)"), ("roxo", "patrulha de facção (rota tracejada)"),
         ("losango", "NPC"), ("quadrado", "baú (história ou mundo)"), ("ponto", "objeto de missão"), ("azul", "zona segura")]
for i, (ic, t) in enumerate(itens):
    yy_ = ly + 70 + i * 34; xx_ = lx + 30
    if ic == "círculo": lg.ellipse([xx_ - 9, yy_ - 6, xx_ + 9, yy_ + 6], fill=(230, 80, 50, 120), outline=(230, 80, 50, 255), width=2)
    if ic == "roxo": lg.ellipse([xx_ - 9, yy_ - 6, xx_ + 9, yy_ + 6], fill=(170, 140, 255, 90), outline=(170, 140, 255, 255), width=2)
    if ic == "losango": lg.polygon([(xx_, yy_ - 7), (xx_ + 6, yy_), (xx_, yy_ + 7), (xx_ - 6, yy_)], fill=(255, 210, 90, 255))
    if ic == "quadrado": lg.rectangle([xx_ - 6, yy_ - 5, xx_ + 6, yy_ + 4], fill=(90, 220, 140, 255))
    if ic == "ponto": lg.ellipse([xx_ - 4, yy_ - 4, xx_ + 4, yy_ + 4], fill=(120, 220, 255, 255))
    if ic == "azul": lg.ellipse([xx_ - 9, yy_ - 6, xx_ + 9, yy_ + 6], fill=(60, 120, 220, 80), outline=(120, 170, 255, 255), width=2)
    lg.text((xx_ + 22, yy_), t, font=F_PEQ, fill=(220, 210, 190, 255), anchor="lm")
tat.convert("RGB").save(os.path.join(AQUI, "..", "mapa_tatico.png"), optimize=True)
print("ok", W, H)
