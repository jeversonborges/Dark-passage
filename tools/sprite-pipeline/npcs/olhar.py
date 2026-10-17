# Mosaico de conferência dos quadros brutos: python3 olhar.py <dir_brutos> <saida.png> [anim] [quadro]
# Uma coluna por direção (o quadro pedido de cada anim), fundo escuro, no tamanho bruto (2x).
import sys, os, glob
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
anims = [sys.argv[3]] if len(sys.argv) > 3 else sorted(d for d in os.listdir(src) if os.path.isdir(f"{src}/{d}"))
DIRS = ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]
rows = []
for a in anims:
    fs = sorted(glob.glob(f"{src}/{a}/*.png"))
    if len(sys.argv) > 4: fs = [f for f in fs if f.endswith(f"_{int(sys.argv[4]):02d}.png")]
    fs.sort(key=lambda f: (DIRS.index(os.path.basename(f).split("_")[0]), f))
    rows.append([Image.open(f).convert("RGBA") for f in fs])
# recorte comum (caixa de todo o conteúdo) e ampliação para conferir detalhes
bb = None
for r in rows:
    for f in r:
        b = f.getbbox()
        if b: bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
bb = (max(0, bb[0]-8), max(0, bb[1]-8), bb[2]+8, bb[3]+8); Z = float(os.environ.get("ZOOM", 2))
rows = [[f.crop(bb).resize((int((bb[2]-bb[0])*Z), int((bb[3]-bb[1])*Z)), Image.LANCZOS) for f in r] for r in rows]
w = max(len(r) for r in rows); s = rows[0][0].size[0]; sh = rows[0][0].size[1]
im = Image.new("RGB", (w*s, len(rows)*sh), (26, 23, 25))
for y, r in enumerate(rows):
    for x, f in enumerate(r): im.paste(f, (x*s, y*sh), f)
if os.environ.get("JOGO"):   # tamanho do jogo (metade do bruto) ampliado em pixels nítidos
    g = im.resize((im.size[0]//2, im.size[1]//2), Image.LANCZOS); k = int(os.environ["JOGO"])
    im = g.resize((g.size[0]*k, g.size[1]*k), Image.NEAREST)
im.save(out)
