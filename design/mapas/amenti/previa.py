"""Prévia isométrica acabada de um trecho dos Salões de Amenti, montada como o jogo monta (losangos 64x32, objetos
pela âncora, por profundidade), com acabamento de print: escuro, luz só das coisas (poças de luz das `luzes`, brilho
dos emissivos), névoa baixa que envolve o pé das peças e vinheta. Se existirem as folhas dos Guardiões em
assets/monstros/<mob>/, desenha o quadro idle SE de cada um no lugar do spawn.

Uso: python3 previa.py sala N [largura]   (N = 1..7, 7 = sala_do_juizo; saída entregas/amenti/sala_N_<nome>.jpg)
     python3 previa.py [mapa.json] [saida.jpg] [x0 y0 x1 y1] [largura]
     (padrão: saloes_de_amenti.json, entregas/amenti/antecamara.jpg, a Antecâmara inteira, 1920 px)
"""
import sys, json, os, math
import numpy as np
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.abspath(os.path.join(AQUI, "..", "..", ".."))
A = os.path.join(RAIZ, "assets", "ambiente")
MON = os.path.join(RAIZ, "assets", "monstros")
arg = sys.argv[1:]
SAIDAS = {1: "sala_1_vestibulo_do_livro", 2: "sala_2_salao_do_universo", 3: "sala_3_o_vazio", 4: "sala_4_camaras_sombrias",
          5: "sala_5_salao_da_flor_da_vida", 6: "antecamara", 7: "sala_do_juizo"}
if arg and arg[0] == "sala":                              # python3 previa.py sala N  -> entregas/amenti/<sala N>.jpg
    n = int(arg[1]); m = json.load(open(os.path.join(AQUI, "saloes_de_amenti.json")))
    r = next(s["ret"] for s in m["salas_ordem"] if s["n"] == n)
    x0, y0, x1, y1 = (37, 146, 83, 194) if n == 6 else (r[0] - 3, r[1] - 3, r[2] + 4, r[3] + 4)
    out = os.path.join(RAIZ, "entregas", "amenti", SAIDAS[n] + ".jpg"); LARG = int(arg[2]) if len(arg) > 2 else 1920
    M = 0                                                  # só o que está no recorte (as salas vizinhas ficam de fora)
    ACESAS = 15 if n == 1 else 0                           # Vestíbulo: as estelas até o meio já acesas, como depois de passar
else:
    M, ACESAS = 4, 0
    m = json.load(open(arg[0] if arg else os.path.join(AQUI, "saloes_de_amenti.json")))
    out = arg[1] if len(arg) > 1 else os.path.join(RAIZ, "entregas", "amenti", "antecamara.jpg")
    x0, y0, x1, y1 = map(int, arg[2:6]) if len(arg) > 5 else (37, 146, 83, 194)
    LARG = int(arg[6]) if len(arg) > 6 else 1920
pisos = m["pisos"]; ter = m["terreno"]
x0, y0, x1, y1 = max(0, x0), max(0, y0), min(len(ter[0]), x1), min(len(ter), y1)


def scr(x, y): return (x + y)*32, (x - y)*16          # +X baixo-direita, +Y cima-direita


cs = [scr(x, y) for x in (x0, x1) for y in (y0, y1)]
mnx, mxx = min(c[0] for c in cs) - 60, max(c[0] for c in cs) + 60
mny, mxy = min(c[1] for c in cs) - 980, max(c[1] for c in cs) + 60
Wd, Hd = int(mxx - mnx), int(mxy - mny)
img = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))            # transparente: o que sobrar é o fundo (o nada)
FUNDOS = [f for f in m.get("fundos", []) if not (f["ret"][2] < x0 or f["ret"][0] > x1 or f["ret"][3] < y0 or f["ret"][1] > y1)]
ABISMO = any(f.get("nevoa_abismo") for f in FUNDOS); FUMACA = any(f.get("fumaca_baixa") for f in FUNDOS)

# camada de baixo: o que fica pendurado sob o chão (a parte de baixo das ilhas, lascas no abismo)
pend = []
for p in m["props"]:
    if not p.get("pendurado") or not (x0 - M <= p["x"] < x1 + M and y0 - M <= p["y"] < y1 + M): continue
    f = f"{A}/objetos/{p['k']}.png"
    if not os.path.exists(f): continue
    j = json.load(open(f[:-4] + ".json")); sx, sy = scr(p["x"], p["y"])
    pend.append((sy, Image.open(f).convert("RGBA"), j["anchor"], sx))
for (sy, im, anc, sx) in sorted(pend, key=lambda o: o[0]):
    img.alpha_composite(im, (int(sx - anc[0] - mnx), int(sy - anc[1] - mny)))
pend_mask = np.asarray(img)[..., 3] > 40
altura = np.full((Hd, Wd), 0.0, np.float32)            # altura (px de tela) acima do chão de cada pixel, para a névoa

atl = {}
def atlas(nome):
    if nome not in atl:
        p = f"{A}/tiles/{nome}.png"
        atl[nome] = Image.open(p).convert("RGBA") if os.path.exists(p) else None
    return atl[nome]

def cel(a, x, y): return a.crop(((x % 4)*64, (y % 4)*32, (x % 4)*64 + 64, (y % 4)*32 + 32))

LADOS = {(1, 0): "x+", (-1, 0): "x-", (0, 1): "y+", (0, -1): "y-"}
for x in range(x0, x1):
    for y in range(y1 - 1, y0 - 1, -1):
        ch = ter[y][x]
        if ch == " ": continue
        a = atlas(pisos.get(ch, "pedra_negra_veios"))
        if a is None: continue
        sx, sy = scr(x + .5, y + .5); px, py = int(sx - 32 - mnx), int(sy - 16 - mny)
        img.alpha_composite(cel(a, x, y), (px, py))
        for (dx, dy), lado in LADOS.items():                # transição macia entre pisos (tiles/bordas)
            if 0 <= y + dy < len(ter) and 0 <= x + dx < len(ter[0]):
                viz = ter[y + dy][x + dx]
                if viz not in (" ", ch):
                    p = f"{A}/tiles/bordas/{pisos.get(viz)}_{lado}.png"
                    if os.path.exists(p): img.alpha_composite(cel(Image.open(p).convert("RGBA"), x, y), (px, py))

# objetos e monstros por profundidade
objs = []
for p in m["props"]:
    if not (x0 - M <= p["x"] < x1 + M and y0 - M <= p["y"] < y1 + M) or p.get("invisivel") or p.get("pendurado"): continue
    if ACESAS and p["k"] == "estela_livro" and p["y"] < ACESAS: p = dict(p, k="estela_livro_acesa")   # quem já passou
    f = f"{A}/objetos/{p['k']}.png"
    if not os.path.exists(f): continue
    j = json.load(open(f[:-4] + ".json"))
    sx, sy = scr(p["x"], p["y"])
    objs.append((0 if p.get("chao") else 1, sy, Image.open(f).convert("RGBA"), j["anchor"], sx))
for s in m.get("spawns", []):
    meta = f"{MON}/{s['mob']}/meta.json"
    if not os.path.exists(meta): continue
    mt = json.load(open(meta)); fw, fh = mt["frame_size"]; d = mt["dirs"].index("SE")
    sheet = Image.open(f"{MON}/{s['mob']}/{mt['sheets']['idle']['file']}").convert("RGBA")
    fr = sheet.crop((0, d*fh, fw, d*fh + fh))
    sx, sy = scr(*s["pos"])
    objs.append((1, sy, fr, mt["anchor"], sx))
objs.sort(key=lambda o: (o[0], o[1]))
for (chao, sy, im, anc, sx) in objs:
    ox, oy = int(sx - anc[0] - mnx), int(sy - anc[1] - mny)
    img.alpha_composite(im, (ox, oy))
    if not chao:
        al = np.asarray(im)[..., 3] > 100
        hh = np.clip((anc[1] - np.arange(im.height))[:, None]*np.ones((1, im.width)), 0, None)
        ys, xs = slice(max(0, oy), min(Hd, oy + im.height)), slice(max(0, ox), min(Wd, ox + im.width))
        sub = (slice(ys.start - oy, ys.stop - oy), slice(xs.start - ox, xs.stop - ox))
        alt = altura[ys, xs]; alt[al[sub]] = hh[sub][al[sub]]

cheio = np.asarray(img)[..., 3].astype(np.float32)/255.0
chao_mask = (cheio > .15) & ~pend_mask
fundo = np.zeros((Hd, Wd, 3), np.float32) + np.array([3, 5, 5], np.float32)/255
if ABISMO:                                                 # estrelas tênues muito ao fundo
    rs = np.random.RandomState(11)
    for k in range(int(Wd*Hd/2600)):
        x_, y_ = rs.randint(0, Wd), rs.randint(0, Hd); b_ = rs.uniform(.08, .35)*(1 if rs.rand() > .08 else 2.2)
        fundo[y_, x_] += b_*np.array([.75, .85, 1.0])
        if b_ > .3 and 0 < x_ < Wd - 1 and 0 < y_ < Hd - 1: fundo[y_ - 1:y_ + 2, x_] += b_*.3; fundo[y_, x_ - 1:x_ + 2] += b_*.3
arr = np.asarray(img).astype(np.float32)[..., :3]/255.0
arr = arr*cheio[..., None] + fundo*(1 - cheio[..., None])
yy, xx = np.mgrid[0:Hd, 0:Wd].astype(np.float32)

# poças de luz das fontes locais (só as luzes do mapa; nada de sol)
luz = np.zeros((Hd, Wd, 3), np.float32)
for l in m["luzes"]:
    if not (x0 - 4 <= l[0] < x1 + 4 and y0 - 4 <= l[1] < y1 + 4): continue
    sx, sy = scr(l[0], l[1]); sx -= mnx; sy -= mny
    r = l[5]*34
    a0, a1, b0, b1 = int(max(0, sx - r)), int(min(Wd, sx + r)), int(max(0, sy - r*.5)), int(min(Hd, sy + r*.5))
    if a0 >= a1 or b0 >= b1: continue
    d = np.sqrt(((xx[b0:b1, a0:a1] - sx)/r)**2 + ((yy[b0:b1, a0:a1] - sy)/(r*.5))**2)
    k = np.clip(1 - d, 0, 1)**2.2
    luz[b0:b1, a0:a1] += k[..., None]*np.array(l[2:5], np.float32)*min(1.0, .25 + l[5]*.05)
base = arr*.82                                            # tudo um pouco mais escuro: o salão é fundo
arr = base + base*luz*2.0 + luz*.07

# névoa baixa: ruído suave em camadas, densa no chão e rala no alto das peças; acende onde há luz
rng = np.random.RandomState(7)
def ruido(esc):
    h, w = max(2, Hd//esc), max(2, Wd//esc)
    return np.asarray(Image.fromarray((rng.rand(h, w)*255).astype(np.uint8)).resize((Wd, Hd), Image.BICUBIC)).astype(np.float32)/255
nv = ruido(220)*.55 + ruido(90)*.3 + ruido(40)*.15
nv = np.clip((nv - .3)*1.8, 0, 1)
dens = nv*np.exp(-altura/(50.0 if FUMACA else 80.0))*(.85 if FUMACA else .6)
neb = np.array([.07, .085, .08] if FUMACA else [.06, .1, .09], np.float32) + luz*.3
arr = arr*(1 - dens[..., None]) + neb*dens[..., None]
if ABISMO:                                                 # névoa verde subindo do abismo: só no nada e por cima do que pende
    def ruido_v(esc_x, esc_y):
        h, w = max(2, Hd//esc_y), max(2, Wd//esc_x)
        return np.asarray(Image.fromarray((rng.rand(h, w)*255).astype(np.uint8)).resize((Wd, Hd), Image.BICUBIC)).astype(np.float32)/255
    fios = np.clip((ruido_v(140, 220)*.55 + ruido_v(50, 90)*.45 - .38)*1.8, 0, 1)
    sobe = np.clip((yy/Hd - .3)/.7, 0, 1)**1.6
    peso = np.where(chao_mask, 0.0, np.where(pend_mask, .55, 1.0))
    a_ = (fios*sobe*peso*.32)[..., None]
    arr = arr*(1 - a_) + np.array([.05, .32, .2], np.float32)*a_ + np.array([.01, .05, .03])*sobe[..., None]*peso[..., None]

# brilho (bloom) dos emissivos: só o que já é claro e verde
lum = arr.max(2)
br = np.clip((lum - .45)/.55, 0, 1)[..., None]*arr
bl = np.zeros_like(arr)
for raio, peso in ((6, .55), (18, .45), (46, .35)):
    im = Image.fromarray(np.clip(br*255, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(raio))
    bl += np.asarray(im).astype(np.float32)/255*peso
arr = arr + bl

# grade de cor: pretos frios esverdeados, curva suave, vinheta
arr = np.clip(arr, 0, None)
arr = arr/(1 + arr*.35)*1.22
arr = arr*np.array([.95, 1.0, .97]) + np.array([.004, .008, .008])
v = np.sqrt(((xx - Wd/2)/(Wd/2))**2 + ((yy - Hd*.52)/(Hd/2))**2)
arr *= np.clip(1.12 - .62*v**2.2, .12, 1)[..., None]
img = Image.fromarray(np.clip(arr*255, 0, 255).astype(np.uint8))
# corta o vazio de cima e de baixo
cols = np.where(cheio.max(0) > .1)[0]; rows = np.where(cheio.max(1) > .1)[0]
if len(rows):
    t, b = max(0, rows[0] - 90), min(Hd, rows[-1] + 90); l_, r_ = max(0, cols[0] - 90), min(Wd, cols[-1] + 90)
    img = img.crop((l_, t, r_, b))
img = img.resize((LARG, int(img.height*LARG/img.width)), Image.LANCZOS)
os.makedirs(os.path.dirname(out), exist_ok=True)
img.save(out, quality=92)
print(out, img.size, len(objs), "objetos")
