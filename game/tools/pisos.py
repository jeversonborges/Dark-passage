"""Desentorta os atlas de piso do kit (4x4 losangos 64x32, periódicos) para texturas quadradas no espaço do mapa:
256x256 px = 4x4 tiles, 64 px por tile. O shader do chão amostra com coordenadas do mundo / 4 e repete."""
import glob, os
import numpy as np
from PIL import Image
G = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = f"{G}/assets/ext/ambiente/tiles"; OUT = f"{G}/assets/ext/ambiente/pisos_mundo"
os.makedirs(OUT, exist_ok=True)
N = 64
u = (np.arange(4 * N) + 0.5) / N
wx, wy = np.meshgrid(u, u)          # wx ao longo de X do mapa (colunas), wy ao longo de Y (linhas)
cx = np.floor(wx).astype(int) % 4; cy = np.floor(wy).astype(int) % 4
fx = wx - np.floor(wx); fy = wy - np.floor(wy)
px = cx * 64 + 32 * (fx + fy)
py = cy * 32 + 16 + 16 * (fx - fy)
for f in sorted(glob.glob(f"{SRC}/*.png")):
    a = np.asarray(Image.open(f).convert("RGBA")).astype(np.float32)
    h, w = a.shape[:2]
    xi = np.clip(px, 0.5, w - 1.5); yi = np.clip(py, 0.5, h - 1.5)
    # amostra só pixels opacos: puxa para dentro do losango para evitar a borda antisserrilhada
    x0 = np.floor(xi - 0.5).astype(int); y0 = np.floor(yi - 0.5).astype(int)
    tx = xi - 0.5 - x0; ty = yi - 0.5 - y0
    acc = np.zeros(px.shape + (4,), np.float32); wsum = np.zeros(px.shape, np.float32)
    for dy in (0, 1):
        for dx in (0, 1):
            wgt = (tx if dx else 1 - tx) * (ty if dy else 1 - ty)
            s = a[np.clip(y0 + dy, 0, h - 1), np.clip(x0 + dx, 0, w - 1)]
            wgt = wgt * (s[..., 3] / 255.0)
            acc += s * wgt[..., None]; wsum += wgt
    rgb = acc[..., :3] / np.maximum(wsum, 1e-4)[..., None]
    out = np.dstack([rgb, np.full(px.shape, 255.0)]).clip(0, 255).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(f"{OUT}/{os.path.basename(f)}")
print("pisos desentortados:", len(glob.glob(f"{OUT}/*.png")))
