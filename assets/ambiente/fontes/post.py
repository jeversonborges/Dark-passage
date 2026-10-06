# Pós-processo: reduz o render 2x, dessatura levemente, corta tiles em losango
# e monta atlas. Uso:
#   python3 post.py tiles <raw_dir> <saida_dir>
#   python3 post.py asset <raw_png> <saida_png>
import sys, os, json, math
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

SS = 1
def finish(img, sat=.85):
    """Redução suave 2x (como os sprites da época), dessatura e escurece os pretos."""
    w, h = img.size
    img = img.resize((w//SS, h//SS), Image.LANCZOS)
    rgb = img.convert("RGB"); a = img.getchannel("A") if img.mode == "RGBA" else None
    rgb = ImageEnhance.Color(rgb).enhance(sat)
    arr = np.asarray(rgb).astype(np.float32)
    # leve puxada para sépia fria nas sombras
    lum = arr.mean(2, keepdims=True) / 255
    tint = np.array([1.0, .98, 1.02]) * (1 - lum) + np.array([1.03, 1.0, .95]) * lum
    arr = np.clip(arr * tint, 0, 255).astype(np.uint8)
    rgb = Image.fromarray(arr)
    if a is not None: rgb.putalpha(a)
    return rgb

def diamond_mask(w=64, h=32, grow=0.0):
    m = np.zeros((h, w), np.uint8)
    for y in range(h):
        for x in range(w):
            if abs(x + .5 - w/2)/(w/2) + abs(y + .5 - h/2)/(h/2) <= 1 + grow: m[y, x] = 255
    return Image.fromarray(m)

def tiles(raw_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    mask = diamond_mask(grow=1/32)
    for f in sorted(os.listdir(raw_dir)):
        if not f.endswith(".json"): continue
        kind = f[:-5]; meta = json.load(open(f"{raw_dir}/{f}"))
        img = finish(Image.open(f"{raw_dir}/{kind}_raw.png").convert("RGBA"))
        atlas = Image.new("RGBA", (64*4, 32*4))
        for key, (cx, cy) in meta["centers"].items():
            i, j = map(int, key.split("_"))
            x0, y0 = int(round(cx - 32)), int(round(cy - 16))
            t = img.crop((x0, y0, x0+64, y0+32)); t.putalpha(mask)
            atlas.paste(t, (i*64, j*32))
        atlas.save(f"{out_dir}/{kind}.png")
        # amostra de 8x8 tiles montada como no jogo (para conferir emendas)
        prev = Image.new("RGBA", (32*16+64, 16*16+32), (0, 0, 0, 255))
        for i in range(8):
            for j in range(8):
                t = atlas.crop(((i % 4)*64, (j % 4)*32, (i % 4)*64+64, (j % 4)*32+32))
                # mundo +x vai para baixo-direita na tela, +y para cima-direita
                px, py = (i + j)*32, 16*8 + (i - j)*16
                prev.alpha_composite(t, (px, py))
        prev.save(f"{out_dir}/_amostra_{kind}.png")

def asset(src, dst, sat=.85):
    finish(Image.open(src).convert("RGBA"), sat).save(dst)

if __name__ == "__main__":
    if sys.argv[1] == "tiles": tiles(sys.argv[2], sys.argv[3])
    else: asset(sys.argv[2], sys.argv[3])
