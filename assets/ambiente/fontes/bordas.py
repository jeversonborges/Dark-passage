# Gera tiles de transição: cada piso em versão com alpha que some aos poucos,
# para pintar por cima do piso vizinho e esconder a divisa reta entre dois pisos.
# Saída: tiles/bordas/<piso>_<lado>.png (atlas 4x4 igual ao piso) e <piso>_<canto>.png
#   lado x+ : o piso cobre o lado +X do tile (baixo-direita na tela) e some em direção a -X
#   lado x- , y+ , y- : idem
#   cantos xy++ , xy+- , xy-+ , xy-- : só a ponta do canto
# Uso: python3 bordas.py
import os, math
import numpy as np
from PIL import Image
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(B, "tiles"); dst = os.path.join(src, "bordas"); os.makedirs(dst, exist_ok=True)

# coordenadas do tile (x, y em -0.5..0.5) para cada pixel da célula 64x32
py, px = np.mgrid[0:32, 0:64].astype(np.float32)
sx, sy = (px + .5 - 32)/32, (py + .5 - 16)/16
TX, TY = (sx + sy)/2, (sx - sy)/2

def ruido(u, v, seed):
    """Ruído periódico com período 4 tiles nos dois eixos (casa com o atlas 4x4)."""
    r = np.random.RandomState(seed); s = np.zeros_like(u)
    for k in range(10):
        fx, fy = r.randint(-3, 4), r.randint(1, 5); ph = r.uniform(0, 6.283); a = 1/(1 + abs(fx) + fy)
        s += a*np.sin(2*math.pi*(fx*u + fy*v)/4 + ph)
    for k in range(10):
        fx, fy = r.randint(1, 5), r.randint(-3, 4); ph = r.uniform(0, 6.283); a = 1/(1 + fx + abs(fy))
        s += a*np.sin(2*math.pi*(fx*u + fy*v)/4 + ph)
    return s/np.abs(s).max()

def smooth(e0, e1, x):
    t = np.clip((x - e0)/(e1 - e0), 0, 1); return t*t*(3 - 2*t)

LADOS = {"x+": lambda X, Y: X, "x-": lambda X, Y: -X, "y+": lambda X, Y: Y, "y-": lambda X, Y: -Y}
CANTOS = {"xy++": (1, 1), "xy+-": (1, -1), "xy-+": (-1, 1), "xy--": (-1, -1)}
for f in sorted(os.listdir(src)):
    if not f.endswith(".png"): continue
    piso = f[:-4]; atlas = np.asarray(Image.open(f"{src}/{f}").convert("RGBA")).astype(np.float32)
    outs = {k: np.zeros_like(atlas) for k in list(LADOS) + list(CANTOS)}
    for i in range(4):
        for j in range(4):
            cell = atlas[j*32:(j+1)*32, i*64:(i+1)*64]
            U, V = i + .5 + TX, j + .5 + TY          # coordenada no bloco de 4x4
            n = ruido(U, V, 11)*.22 + ruido(U*2, V*2, 23)*.08
            for lado, fn in LADOS.items():
                d = fn(TX, TY) + n                     # 0.5 = borda coberta
                a = smooth(-.15, .35, d)
                o = cell.copy(); o[..., 3] *= a; outs[lado][j*32:(j+1)*32, i*64:(i+1)*64] = o
            for canto, (cx, cy) in CANTOS.items():
                d = np.minimum(cx*TX, cy*TY) + n
                a = smooth(.05, .42, d)
                o = cell.copy(); o[..., 3] *= a; outs[canto][j*32:(j+1)*32, i*64:(i+1)*64] = o
    for k, arr in outs.items():
        Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(f"{dst}/{piso}_{k}.png")
print("ok")
