# Pós-processo das vinhetas: névoa por profundidade, partículas no ar, gradação de cor,
# vinheta, grão e o título da área. Uso: python3 pos.py <base> '<json de opções>'
import sys, json, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
F = os.path.dirname(os.path.abspath(__file__))
base = sys.argv[1]; o = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
im = np.asarray(Image.open(base + "_raw.png").convert("RGB")).astype(np.float32)/255
H, W, _ = im.shape
mist = np.asarray(Image.open(base + "_mist.png").convert("L").resize((W, H))).astype(np.float32)/255 if os.path.exists(base + "_mist.png") else np.zeros((H, W), np.float32)
neb = np.array(o.get("nevoa_cor", [.16, .14, .12])); k = o.get("nevoa", .55)
yy = np.linspace(0, 1, H)[:, None]
f = np.clip(mist*k + (1 - yy)**3 * o.get("nevoa_topo", .35), 0, 1)[..., None]
im = im*(1 - f) + neb*f
# partículas (cinza, Amargo, neve, brasas...)
rnd = random.Random(3)
lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
for p in o.get("particulas", []):
    for _ in range(p.get("n", 300)):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H); r = rnd.uniform(*p.get("r", [.6, 1.8]))
        c = tuple(int(255*v) for v in p["cor"]) + (int(255*rnd.uniform(*p.get("a", [.2, .7]))),)
        L = p.get("rastro", 0)
        if L: d.line([(x, y), (x + L*p.get("dx", .3), y + L)], fill=c, width=max(1, int(r)))
        else: d.ellipse([x-r, y-r, x+r, y+r], fill=c)
glow = lay.filter(ImageFilter.GaussianBlur(3))
P = np.asarray(lay).astype(np.float32)/255; G = np.asarray(glow).astype(np.float32)/255
im = im*(1 - P[..., 3:]) + P[..., :3]*P[..., 3:] + G[..., :3]*G[..., 3:]*.8
# bloom leve
b = Image.fromarray((np.clip(im, 0, 1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(18))
B = np.asarray(b).astype(np.float32)/255
im = im + np.clip(B - .35, 0, 1)*o.get("bloom", .6)
# gradação
g = np.array(o.get("grade", [1, 1, 1])); im = im*g
lift = np.array(o.get("lift", [.012, .011, .014])); im = im*(1 - lift) + lift
im = np.clip((im - .5)*o.get("contraste", 1.05) + .5, 0, 1)
# vinheta
xx = np.linspace(-1, 1, W)[None, :]; yv = np.linspace(-1, 1, H)[:, None]
v = np.clip(1 - (xx**2*.55 + yv**2*.8)*o.get("vinheta", .55), 0, 1)[..., None]
im = im*v
im = im + np.random.default_rng(1).normal(0, .012, im.shape)
out = Image.fromarray((np.clip(im, 0, 1)**(1/o.get("gama", 1.0))*255).astype(np.uint8))
# título
d = ImageDraw.Draw(out)
if o.get("titulo"):
    t1 = ImageFont.truetype(f"{F}/PirataOne-Regular.ttf", 84); t2 = ImageFont.truetype(f"{F}/IMFeENsc28P.ttf", 34); t3 = ImageFont.truetype(f"{F}/IMFeENit28P.ttf", 28)
    x, y = 70, H - 210
    sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.rectangle([0, H - 260, W, H], fill=(0, 0, 0, 120)); sh = sh.filter(ImageFilter.GaussianBlur(40))
    out = Image.alpha_composite(out.convert("RGBA"), sh).convert("RGB"); d = ImageDraw.Draw(out)
    acc = tuple(o.get("acento", [201, 154, 62]))
    d.text((x, y), o["titulo"], font=t1, fill=(232, 222, 200))
    d.text((x + 4, y + 96), o.get("sub", ""), font=t2, fill=acc)
    if o.get("frase"): d.text((x + 4, y + 140), o["frase"], font=t3, fill=(190, 180, 165))
out.save(o.get("saida", base + ".png"), optimize=True)
print("ok", o.get("saida", base + ".png"))
