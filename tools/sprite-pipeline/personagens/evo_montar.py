# Monta a prancha de prévia das evoluções: por classe, base e as duas evoluções (close + tamanho do jogo).
# Uso: python3 evo_montar.py <dir_renders> <saida.png> "<titulo>" linha1 [linha2...]
#   cada linha: base_tipo,evoA_tipo,evoB_tipo|Nome base,Nome A,Nome B|sub base;sub A;sub B
import sys, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
F = "/mnt/project-files/game/assets/ext/fontes/"
ft = lambda n, s: ImageFont.truetype(F + n, s)
src, dst, title = sys.argv[1], sys.argv[2], sys.argv[3]
rows = [r.split("|") for r in sys.argv[4:]]
CW, CH = 560, 760
def crop(path, h):
    im = Image.open(path).convert("RGBA"); bb = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    im = im.crop(bb); s = h / im.height
    if im.width * s > CW - 60: s = (CW - 60) / im.width
    return im.resize((int(im.width*s), int(im.height*s)), Image.LANCZOS)
def jogo(path):  # reduz para o tamanho do jogo com contorno de 1 px, depois amplia 2x sem filtro
    im = Image.open(path).convert("RGBA").resize((192, 192), Image.LANCZOS)
    body = im.getchannel("A").point(lambda v: 255 if v > 140 else 0)
    out = Image.new("RGBA", im.size, (0,0,0,0)); out.paste((10,8,8,255), mask=body.filter(ImageFilter.MaxFilter(3)))
    out.paste(im.convert("RGB"), mask=body)
    bb = out.getbbox(); out = out.crop(bb)
    return out.resize((out.width*2, out.height*2), Image.NEAREST)
W, H = CW*3 + 80, 150 + len(rows)*(CH + 30)
bg = Image.new("RGB", (W, H), (16, 14, 15)); d = ImageDraw.Draw(bg)
yy, xx = np.mgrid[0:H, 0:W]; v = 1 - .55*np.clip((((xx-W/2)/(W*.7))**2 + ((yy-H/2)/(H*.7))**2), 0, 1)
bg = Image.fromarray((np.asarray(bg).astype(float) * v[..., None]).astype(np.uint8)); d = ImageDraw.Draw(bg)
d.text((40, 36), title, font=ft("PirataOne-Regular.ttf", 64), fill=(214, 190, 150))
d.text((42, 108), "Nível 50 · a classe base e os dois caminhos de evolução · close na direção SE e, no canto, o tamanho real no jogo (2x)", font=ft("IMFeENit28P.ttf", 26), fill=(150, 135, 115))
for r, (kinds, names, subs) in enumerate(rows):
    kinds, names, subs = kinds.split(","), names.split(","), subs.split(";")
    y0 = 160 + r*(CH + 30)
    for c, k in enumerate(kinds):
        x0 = 40 + c*CW
        panel = Image.new("RGBA", (CW-20, CH), (26, 22, 23, 255)); bg.paste(panel, (x0, y0))
        d.rectangle([x0, y0, x0+CW-21, y0+CH-1], outline=(70, 56, 46) if c else (52, 48, 48), width=2)
        im = crop(f"{src}/{k}_close_SE.png", 560); bg.paste(im, (x0 + (CW-20-im.width)//2, y0 + 600 - im.height), im)
        g = jogo(f"{src}/{k}_jogo.png"); bg.paste(g, (x0 + CW - 40 - g.width, y0 + 640 - g.height), g)
        col = (190, 180, 170) if c == 0 else (232, 196, 120)
        d.text((x0 + 20, y0 + 640), names[c], font=ft("PirataOne-Regular.ttf", 44), fill=col)
        d.text((x0 + 22, y0 + 696), subs[c], font=ft("IMFeENit28P.ttf", 24), fill=(150, 138, 120))
        if c: d.text((x0 - 34, y0 + CH//2 - 30), "›", font=ft("PirataOne-Regular.ttf", 70), fill=(120, 90, 60))
bg.save(dst); print("ok", dst, bg.size)
