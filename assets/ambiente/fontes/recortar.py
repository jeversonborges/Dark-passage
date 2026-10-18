# Recorta a margem transparente dos renders brutos (as sombras compridas deixam metade do PNG vazia) e
# corrige a âncora no JSON. Uso: python3 recortar.py <raw_dir>   (antes do publicar.py)
import sys, os, json
from PIL import Image
raw = sys.argv[1]; PAD = 4
for f in sorted(os.listdir(raw)):
    if not f.endswith(".json"): continue
    kind = f[:-5]; png = f"{raw}/{kind}_raw.png"
    if not os.path.exists(png): continue
    im = Image.open(png).convert("RGBA"); bb = im.getchannel("A").point(lambda a: 255 if a > 2 else 0).getbbox()
    if not bb: continue
    x0, y0, x1, y1 = max(0, bb[0] - PAD), max(0, bb[1] - PAD), min(im.width, bb[2] + PAD), min(im.height, bb[3] + PAD)
    if (x0, y0, x1, y1) == (0, 0, im.width, im.height): continue
    m = json.load(open(f"{raw}/{f}"))
    im.crop((x0, y0, x1, y1)).save(png)
    m["w"], m["h"] = x1 - x0, y1 - y0; m["anchor"] = [m["anchor"][0] - x0, m["anchor"][1] - y0]
    json.dump(m, open(f"{raw}/{f}", "w"), ensure_ascii=False)
    print("recortado", kind, im.size, "->", (x1 - x0, y1 - y0))
