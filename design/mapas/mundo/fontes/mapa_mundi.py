# Mapa-múndi ilustrado da proposta: as terras das trombetas ligadas pela Linha 7.
import os, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy.ndimage import gaussian_filter, zoom
F = os.path.dirname(os.path.abspath(__file__))
W, H = 2400, 1500
rng = np.random.default_rng(4); R = random.Random(4)
def fbm(w, h, oct=6, base=4, seed=0):
    g = np.random.default_rng(seed); out = np.zeros((h, w)); a = 1; tot = 0
    for o in range(oct):
        s = base*2**o; n = g.random((int(h/w*s)+2, s+2))
        out += a*zoom(n, (h/n.shape[0], w/n.shape[1]), order=3)[:h, :w]; tot += a; a *= .5
    return out/tot
# pergaminho escuro
n1 = fbm(W, H, 7, 3, 1); n2 = fbm(W, H, 5, 12, 2)
base = np.array([.16, .13, .1])
img = base[None, None, :]*(.75 + .5*n1[..., None]) + (n2[..., None] - .5)*.05
xx, yy = np.meshgrid(np.linspace(-1, 1, W), np.linspace(-1, 1, H))
edge = np.clip(1 - (np.abs(xx)**6 + np.abs(yy)**6)*.9 - (xx**2 + yy**2)*.25, 0, 1)
img = img*(.35 + .65*edge[..., None])
# regiões
REG = [  # id, nome, nível, trombeta, centro, raio, cor base, cor brilho
    ("deserto", "Deserto de Absinto", "Nível 1 a 15", "3ª e 5ª trombeta", (560, 1060), 250, (.42, .34, .22), (.45, 1, .2)),
    ("mata", "Mata do Granizo", "Nível 15 a 30", "1ª trombeta", (520, 520), 230, (.12, .1, .09), (1, .4, .1)),
    ("costa", "Costa Rubra", "Nível 30 a 45", "2ª trombeta", (1180, 430), 230, (.32, .1, .08), (1, .55, .15)),
    ("candelaria", "Candelária", "Nível 45 a 60", "4ª trombeta", (1850, 430), 230, (.12, .15, .22), (1, .85, .4)),
    ("planicie", "Planície dos Cavaleiros", "Nível 60 a 80", "6ª trombeta", (1860, 1040), 250, (.45, .38, .12), (1, .8, .2)),
    ("cratera", "Cratera de Absinto", "Nível 80 a 100", "3ª trombeta, a estrela", (1220, 900), 200, (.06, .1, .07), (.4, 1, .45)),
]
ang = np.arctan2(*np.meshgrid(np.arange(H), np.arange(W), indexing="ij")[::-1][::-1])
masks = {}
for i, (k, nome, nv, tr, (cx, cy), rad, col, glow) in enumerate(REG):
    dx, dy = np.meshgrid(np.arange(W) - cx, np.arange(H) - cy)
    a = np.arctan2(dy, dx); d = np.hypot(dx, dy)
    ph = [R.uniform(0, 6.3) for _ in range(5)]
    rr = rad*(1 + .14*np.sin(3*a + ph[0]) + .09*np.sin(5*a + ph[1]) + .05*np.sin(9*a + ph[2]) + .03*np.sin(17*a + ph[3]))
    rr = rr*(1 + (fbm(W, H, 5, 6, 10 + i) - .5)*.35)
    m = np.clip((rr - d)/14, 0, 1); masks[k] = m
    tex = fbm(W, H, 6, 8, 20 + i)
    c = np.array(col)[None, None, :]*(.7 + .6*tex[..., None])
    inner = np.clip((rr - d)/rr, 0, 1)
    c = c + np.array(glow)[None, None, :]*(inner**2.5)[..., None]*.35
    img = img*(1 - m[..., None]*.92) + c*m[..., None]*.92
    # contorno em tinta
    ring = np.exp(-((rr - d)/3.0)**2)
    img = img*(1 - ring[..., None]*.75)
# detalhes por região (marcas pintadas)
img = np.clip(img, 0, 1)
im = Image.fromarray((img*255).astype(np.uint8)).convert("RGBA")
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
def pts_in(k, n, seed):
    r = random.Random(seed); m = masks[k]; out = []
    while len(out) < n:
        x, y = r.randrange(W), r.randrange(H)
        if m[y, x] > .99: out.append((x, y))
    return out
ink = (20, 14, 10, 220)
for x, y in pts_in("deserto", 60, 1):  # dunas
    d.arc([x-22, y-8, x+22, y+10], 200, 340, fill=(80, 64, 40, 200), width=2)
for x, y in pts_in("deserto", 9, 2):  # prédios enterrados
    d.rectangle([x-5, y-16, x+5, y], fill=(40, 34, 30, 230)); d.rectangle([x-3, y-13, x-1, y-11], fill=(230, 150, 60, 255))
for x, y in pts_in("mata", 90, 3):  # troncos queimados
    d.line([(x, y), (x + R.uniform(-2, 2), y - R.uniform(14, 26))], fill=(10, 8, 7, 240), width=3)
    if R.random() < .3: d.ellipse([x-2, y-2, x+2, y+2], fill=(255, 110, 30, 220))
for x, y in pts_in("costa", 14, 4):  # cascos virados
    d.chord([x-16, y-12, x+16, y+8], 180, 360, fill=(50, 30, 22, 240), outline=ink)
for x, y in pts_in("costa", 40, 5): d.line([(x-6, y), (x+6, y)], fill=(150, 40, 30, 160), width=2)
for x, y in pts_in("candelaria", 26, 6):  # sobrados e lampiões
    d.polygon([(x-7, y), (x-7, y-14), (x, y-22), (x+7, y-14), (x+7, y)], fill=(25, 30, 42, 240), outline=ink)
    if R.random() < .6: d.ellipse([x-3, y-12, x+1, y-8], fill=(255, 210, 110, 255))
for x, y in pts_in("planicie", 70, 7):  # fileiras de cavaleiros
    d.line([(x, y), (x+8, y-4)], fill=(40, 34, 20, 230), width=4); d.line([(x+6, y-4), (x+12, y-16)], fill=(40, 34, 20, 230), width=1)
for x, y in pts_in("cratera", 50, 8):  # cristais
    s = R.uniform(4, 10); d.polygon([(x, y-2*s), (x+s*.5, y), (x, y+s*.3), (x-s*.5, y)], fill=(110, 255, 130, 230))
# Linha 7: ordem da jornada
ordem = ["deserto", "mata", "costa", "candelaria", "planicie", "cratera"]
C = {k: c for k, _, _, _, c, *_ in REG}
def curva(a, b, bend):
    (x0, y0), (x1, y1) = a, b; mx, my = (x0+x1)/2, (y0+y1)/2
    nx, ny = -(y1-y0), (x1-x0); L = math.hypot(nx, ny); mx += nx/L*bend; my += ny/L*bend
    return [((1-t)**2*x0 + 2*(1-t)*t*mx + t**2*x1, (1-t)**2*y0 + 2*(1-t)*t*my + t**2*y1) for t in np.linspace(0, 1, 120)]
trilho = []
for a, b, bend in zip(ordem, ordem[1:], [60, -80, 70, -60, 50]): trilho += curva(C[a], C[b], bend)
d.line(trilho, fill=(18, 12, 8, 255), width=9)
d.line(trilho, fill=(150, 110, 60, 255), width=3)
for i in range(0, len(trilho) - 1, 6):
    (x0, y0), (x1, y1) = trilho[i], trilho[i+1]; nx, ny = -(y1-y0), (x1-x0); L = math.hypot(nx, ny) or 1
    d.line([(x0 - nx/L*8, y0 - ny/L*8), (x0 + nx/L*8, y0 + ny/L*8)], fill=(30, 22, 14, 255), width=3)
# estações
for k in ordem:
    x, y = C[k]; d.ellipse([x-13, y-13, x+13, y+13], fill=(30, 20, 12, 255), outline=(201, 154, 62, 255), width=3)
    d.ellipse([x-5, y-5, x+5, y+5], fill=(255, 200, 110, 255))
im = Image.alpha_composite(im, lay)
# brilho por região
gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
for k, nome, nv, tr, (cx, cy), rad, col, glow in REG:
    c = tuple(int(v*255) for v in glow)
    if k == "cratera": g.ellipse([cx-40, cy-40, cx+40, cy+40], fill=c + (200,))
    for x, y in pts_in(k, 14, hash(k) % 99): g.ellipse([x-4, y-4, x+4, y+4], fill=c + (120,))
gl = gl.filter(ImageFilter.GaussianBlur(16))
im = Image.alpha_composite(im, gl)
# a sétima: silêncio
d = ImageDraw.Draw(im)
fT = ImageFont.truetype(f"{F}/PirataOne-Regular.ttf", 50); fS = ImageFont.truetype(f"{F}/IMFeENsc28P.ttf", 27); fI = ImageFont.truetype(f"{F}/IMFeENit28P.ttf", 25)
fG = ImageFont.truetype(f"{F}/PirataOne-Regular.ttf", 96)
def rotulo(x, y, t1, t2, t3, acc):
    for dx in (-2, 0, 2):
        for dy in (-2, 0, 2): d.text((x+dx, y+dy), t1, font=fT, fill=(8, 6, 4), anchor="mm")
    d.text((x, y), t1, font=fT, fill=(236, 224, 198), anchor="mm")
    for dx in (-2, 2): d.text((x+dx, y+40), t2, font=fS, fill=(8, 6, 4), anchor="mm")
    d.text((x, y+40), t2, font=fS, fill=acc, anchor="mm")
    d.text((x, y+72), t3, font=fI, fill=(200, 188, 165), anchor="mm")
OFF = {"deserto": (0, 120), "mata": (0, -175), "costa": (0, -150), "candelaria": (0, -175), "planicie": (0, 130), "cratera": (0, 110)}
for k, nome, nv, tr, (cx, cy), rad, col, glow in REG:
    ox, oy = OFF[k]; acc = tuple(int(150 + 105*v) for v in glow)
    rotulo(cx + ox, cy + oy, nome, nv, tr, acc)
d.text((2160, 1330), "7ª trombeta", font=fS, fill=(120, 110, 95), anchor="mm")
d.text((2160, 1365), "“houve silêncio no céu”", font=fI, fill=(110, 100, 85), anchor="mm")
d.text((W/2, 90), "As Terras das Trombetas", font=fG, fill=(232, 220, 196), anchor="mm")
d.text((W/2, 160), "a Linha 7 do bonde-veleiro liga todas as áreas", font=fI, fill=(201, 154, 62), anchor="mm")
# rosa dos ventos
cx, cy = 2200, 230
for a, L in [(0, 70), (90, 50), (180, 50), (270, 50)]:
    t = math.radians(a - 90); x, y = cx + math.cos(t)*L, cy + math.sin(t)*L
    p = math.radians(a); d.polygon([(x, y), (cx + math.cos(t + 1.57)*9, cy + math.sin(t + 1.57)*9), (cx + math.cos(t - 1.57)*9, cy + math.sin(t - 1.57)*9)], fill=(201, 154, 62))
d.text((cx, cy - 90), "N", font=fS, fill=(201, 154, 62), anchor="mm")
im = im.convert("RGB")
a = np.asarray(im).astype(np.float32)/255
a = a + np.random.default_rng(2).normal(0, .015, a.shape)
out = os.path.join(F, "..", "imagens", "00_mapa_mundi.png")
Image.fromarray((np.clip(a, 0, 1)*255).astype(np.uint8)).save(out, optimize=True); print(out)
