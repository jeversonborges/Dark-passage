# Pós-processo dos monstros: reduz o render 2x, paleta indexada compartilhada
# (sem dither), alpha binário, contorno escuro de 1 px e sombra "blob" no pé.
# Gera uma folha por animação (linhas = 8 direções, colunas = quadros),
# meta.json para o Godot e GIFs de prévia.
# Uso: python3 process.py <dir_brutos> <dir_saida> [cores] [largura_sombra_m]
import sys, os, json, glob
from PIL import Image, ImageDraw, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
colors = int(sys.argv[3]) if len(sys.argv) > 3 else 40
shw = float(sys.argv[4]) if len(sys.argv) > 4 else .7
meta = json.load(open(f"{src}/meta.json")); DIRS = meta["dirs"]
PX = meta["frame_size"][0]; ax, ay = meta["anchor"]; ppm = meta["pixels_per_meter"]
os.makedirs(dst, exist_ok=True)

def load(anim, d, f):
    im = Image.open(f"{src}/{anim}/{d}_{f:02d}.png").convert("RGBA")
    return im.resize((PX, PX), Image.LANCZOS)

anims = {a: m for a, m in meta["anims"].items() if os.path.isdir(f"{src}/{a}")}
# paleta comum: amostra de quadros de todas as animações
samples = []
for a, m in anims.items():
    for d in DIRS[::2]:
        for f in range(0, m["frames"], 2): samples.append(load(a, d, f))
strip = Image.new("RGB", (PX*len(samples), PX), (0, 0, 0))
for i, s in enumerate(samples):
    bg = Image.new("RGB", (PX, PX), (0, 0, 0)); body = s.getchannel("A").point(lambda v: 255 if v > 140 else 0)
    bg.paste(s.convert("RGB"), mask=body); strip.paste(bg, (i*PX, 0))
pal = strip.quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
# brilhos (olhos, brasa, pus): pontos pequenos e saturados que o MEDIANCUT engole. Reserva até 4 cores para eles.
hsv = strip.convert("HSV")
gm = Image.eval(hsv.getchannel("S"), lambda v: 255 if v > 120 else 0)
gm = Image.composite(gm, Image.new("L", strip.size, 0), Image.eval(hsv.getchannel("V"), lambda v: 255 if v > 170 else 0))
pix = [px for px, m in zip(strip.getdata(), gm.getdata()) if m]
if len(pix) >= 4:
    gi = Image.new("RGB", (len(pix), 1)); gi.putdata(pix)
    gp = gi.quantize(4, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).getpalette()[:12]
    base = pal.getpalette()[:colors*3]
    pal = Image.new("P", (1, 1)); pal.putpalette(base + gp + base[:3]*(256 - colors - 4))

sw, sh = shw*ppm, shw*ppm*.5
shadow = Image.new("L", (PX, PX), 0)
ImageDraw.Draw(shadow).ellipse([ax - sw/2, ay - sh/2, ax + sw/2, ay + sh/2], fill=255)
shadow = shadow.filter(ImageFilter.GaussianBlur(1.5)).point(lambda v: 255 if v > 110 else 0)

def finish(im):
    body = im.getchannel("A").point(lambda v: 255 if v > 140 else 0)
    outline = body.filter(ImageFilter.MaxFilter(3))
    rgb = im.convert("RGB").quantize(palette=pal, dither=Image.Dither.NONE).convert("RGB")
    res = Image.new("RGBA", im.size, (0, 0, 0, 0))
    res.paste((0, 0, 0, 120), mask=shadow)
    res.paste((10, 8, 8, 255), mask=outline)
    res.paste(rgb, mask=body)
    return res

out_meta = dict(meta); out_meta["sheets"] = {}
for a, m in anims.items():
    n = m["frames"]; sheet = Image.new("RGBA", (PX*n, PX*8), (0, 0, 0, 0))
    gif = []
    for r, d in enumerate(DIRS):
        for f in range(n):
            fr = finish(load(a, d, f)); sheet.paste(fr, (f*PX, r*PX))
            if d == "SE": gif.append(fr)
    name = f"{meta['monstro']}_{a}.png"; sheet.save(f"{dst}/{name}")
    out_meta["sheets"][a] = {"file": name, "rows": "dirs", "cols": "frames"}
    bgc = (24, 22, 24)
    frames = []
    for fr in gif:
        b = Image.new("RGB", fr.size, bgc); b.paste(fr, (0, 0), fr)
        frames.append(b.resize((PX*2, PX*2), Image.NEAREST))
    os.makedirs(f"{dst}/previa", exist_ok=True)
    frames[0].save(f"{dst}/previa/{a}_SE.gif", save_all=True, append_images=frames[1:],
                   duration=int(1000/m["fps"]), loop=0, disposal=2)
    print(a, sheet.size)
out_meta["post"] = {"colors": colors, "outline": "#0a0808", "shadow_width_m": shw}
json.dump(out_meta, open(f"{dst}/meta.json", "w"), indent=1, ensure_ascii=False)
