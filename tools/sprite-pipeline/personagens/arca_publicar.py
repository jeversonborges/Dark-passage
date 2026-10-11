# Publica a Arca do Primarca no formato do kit de cenário (assets/ambiente/objetos/<kind>.png + .json).
# Uso: python3 arca_publicar.py <saida_do_blender> <pasta_objetos>
import sys, json, os
import numpy as np
from PIL import Image, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
m = json.load(open(f"{src}/meta.json")); W, H = m["frame"]; ax, ay = m["anchor"]
im2 = Image.open(f"{src}/arca_primarca.png").convert("RGBA")
im = im2.resize((W, H), Image.LANCZOS)
a = np.asarray(im).astype(np.float32)
body = a[..., 3] > 110
# paleta indexada sem dither, contorno escuro de 1 px, emissivos mantêm a cor e ganham brilho roxo
q = Image.fromarray(a[..., :3].astype(np.uint8)).quantize(56, method=Image.MEDIANCUT, dither=Image.NONE).convert("RGB")
out = np.zeros((H, W, 4), np.uint8); out[body, :3] = np.asarray(q)[body]; out[body, 3] = 255
edge = np.zeros_like(body)
for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)): edge |= np.roll(np.roll(body, dy, 0), dx, 1)
edge &= ~body; out[edge] = (10, 8, 8, 255)
hot = body & (a[..., 2] > 150) & (a[..., 2] > a[..., 1]*1.35)      # válvulas roxas
out[hot, :3] = np.clip(a[hot, :3]*[.8, .62, 1.1], 0, 255).astype(np.uint8)
g = Image.fromarray((hot*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
glow = Image.new("RGBA", (W, H), (170, 110, 255, 0)); glow.putalpha(g.point(lambda v: min(150, int(v*2.2))))
res = Image.alpha_composite(glow, Image.fromarray(out))
bb = res.getchannel("A").getbbox(); res = res.crop(bb)
os.makedirs(dst, exist_ok=True)
res.save(f"{dst}/arca_primarca.png")
json.dump({"w": res.width, "h": res.height, "anchor": [round(ax - bb[0]), round(ay - bb[1])], "estado": "fechado",
           "emissivo": "válvulas roxas", "categoria": "props", "footprint_tiles": [2, 1],
           "descricao": "Arca do Primarca: baú tecnomancer do Gustavo (armazém). Carvalho negro, cintas de ferro, volante de cofre, manômetros e cinco válvulas roxas no tampo.",
           "kind": "arca_primarca"}, open(f"{dst}/arca_primarca.json", "w"), indent=1, ensure_ascii=False)
print("ok", res.size)
