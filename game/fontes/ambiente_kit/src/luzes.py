# Sprites de luz (poças de luz no chão, elipse 2:1) para somar no Godot
# (PointLight2D.texture ou CanvasItem com blend "add"). Uso: python3 luzes.py <saida_dir>
import sys, os
import numpy as np
from PIL import Image
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
LUZES = {  # nome: (cor, raio em px, intensidade)
    "luz_fogo": ((255, 120, 40), 160, 1.0), "luz_vela": ((255, 150, 70), 60, .8),
    "luz_lampiao": ((255, 165, 80), 200, .9), "luz_vitral": ((220, 30, 18), 220, .9),
    "luz_arco": ((150, 205, 255), 320, 1.0), "luz_porao": ((200, 25, 12), 140, .9),
    "luz_sagrada": ((255, 210, 130), 260, 1.0), "luz_lua": ((120, 140, 190), 300, .5),
}
for name, (col, R, k) in LUZES.items():
    W, H = R*2, R
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W/2 + .5)/(W/2))**2 + ((y - H/2 + .5)/(H/2))**2)
    a = np.clip(1 - d, 0, 1) ** 2.2 * k
    img = np.zeros((H, W, 4), np.uint8)
    img[..., :3] = col; img[..., 3] = (a*255).astype(np.uint8)
    Image.fromarray(img).save(f"{out}/{name}.png")
print("ok")
