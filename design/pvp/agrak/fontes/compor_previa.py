# Põe os sprites do jogo (gladiadores e o Golias) no render do coliseu, com vinheta e névoa baixa.
# Uso: python3 compor_previa.py <render.png> <golias_proc_dir> <saida.png>
import sys, json, os
from PIL import Image, ImageDraw, ImageFilter
ren, gdir, out = sys.argv[1:4]
RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../..")
img = Image.open(ren).convert("RGBA"); W, H = img.size
pts = json.load(open(os.path.splitext(ren)[0] + "_pontos.json")); k = pts["px_por_m"]/64
P = pts["pontos"]
def tela(x, y):  # chão (z=0) para pixel, relativo ao centro do fosso (câmera 30°/45°)
    cx, cy = P["centro"]; m = pts["px_por_m"]
    return (cx + (x + y)*.7071*m, cy - (y - x)*.7071*.5*m)
P["golias"] = tela(6.6, 6.8)   # saindo do Portão do Gigante, girando a bola

def colar(fr, anchor, pos):
    fr = fr.resize((round(fr.width*k), round(fr.height*k)), Image.LANCZOS)
    img.alpha_composite(fr, (round(pos[0] - anchor[0]*k), round(pos[1] - anchor[1]*k)))

def personagem(classe, anim, frame, dirn, pos):
    d = f"{RAIZ}/assets/personagens/{classe}"; m = json.load(open(f"{d}/sprites.json"))
    fs = m["frame_size"]; row = m["rows_dirs"].index(dirn)
    sh = Image.open(f"{d}/{m['anims'][anim]['file']}").convert("RGBA")
    colar(sh.crop((frame*fs[0], row*fs[1], (frame+1)*fs[0], (row+1)*fs[1])), m["anchor_feet"], pos)

gm = json.load(open(f"{gdir}/meta.json")); PX = gm["frame_size"][0]
gs = Image.open(f"{gdir}/golias_spin.png").convert("RGBA")
fila = [(n, ok) for n, ok in sorted(P.items()) if n.startswith("g") and n != "golias"]
classes = [("humano", "NW"), ("anjo", "NE"), ("mutante", "N"), ("cultista", "E"), ("tecnomancer", "NE"), ("demonio", "N")]
ordem = sorted([(P[f"g{i}"], c) for i, c in enumerate(classes)] + [(P["golias"], None)], key=lambda t: t[0][1])
for pos, c in ordem:
    if c is None: colar(gs.crop((3*PX, PX, 4*PX, 2*PX)), gm["anchor"], pos)
    else: personagem(c[0], "idle", 0, c[1], pos)

# névoa baixa quente perto do chão do fosso e vinheta
haze = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(haze)
cx, cy = P["centro"]
for i in range(18):
    r = 1 - i/18
    d.ellipse((cx - 900*r, cy - 330*r, cx + 900*r, cy + 330*r), fill=(120, 80, 45, 5))
img.alpha_composite(haze.filter(ImageFilter.GaussianBlur(40)))
vin = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(vin)
for i in range(60):
    t = i/60; dv.ellipse((-W*.25 + W*.3*t, -H*.3 + H*.33*t, W*1.25 - W*.3*t, H*1.3 - H*.33*t), fill=int(200*t))
vin = vin.filter(ImageFilter.GaussianBlur(80))
dark = Image.new("RGBA", (W, H), (4, 3, 3, 255)); img = Image.composite(img, dark, vin)
img.convert("RGB").save(out, quality=92)
