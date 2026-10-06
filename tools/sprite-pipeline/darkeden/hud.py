# Pós-processo "tela de jogo 2003": dessatura, paleta de 256 cores e HUD de pedra.
import sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageFilter
src, dst = sys.argv[1], sys.argv[2]
img = Image.open(src).convert("RGB")
img = ImageEnhance.Color(img).enhance(.8)
img = img.quantize(256, method=Image.Quantize.FASTOCTREE, dither=Image.Dither.NONE).convert("RGB")
W, H = img.size; bar = 96
out = Image.new("RGB", (W, H + bar), (0,0,0)); out.paste(img, (0,0))
d = ImageDraw.Draw(out)
F = "/usr/share/fonts/truetype/dejavu/"
serif = ImageFont.truetype(F+"DejaVuSerif-Bold.ttf", 15); small = ImageFont.truetype(F+"DejaVuSansCondensed-Oblique.ttf", 12)
# painel de pedra/metal
for y in range(bar):
    v = 26 - abs(y - bar//2)//6
    d.line([(0,H+y),(W,H+y)], fill=(v, v-3, v-1))
d.line([(0,H),(W,H)], fill=(70,55,40), width=2); d.line([(0,H+3),(W,H+3)], fill=(10,8,8))
def orb(cx, color, label):
    r = 38; cy = H + bar//2
    d.ellipse([cx-r-4,cy-r-4,cx+r+4,cy+r+4], fill=(55,45,35), outline=(10,8,8), width=2)
    d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=color)
    d.chord([cx-r,cy-r,cx+r,cy+r], 205, 335, fill=(8,6,8))  # parte vazia do orbe
    d.ellipse([cx-r*.5,cy-r*.75,cx-r*.1,cy-r*.45], fill=tuple(min(255,c+70) for c in color))
    d.text((cx, cy+r+1), label, font=small, fill=(150,140,120), anchor="mt")
orb(60, (130,10,10), ""); orb(W-60, (20,40,110), "")
# slots de habilidade
for i in range(10):
    x = 150 + i*58; y = H + 22
    d.rectangle([x,y,x+50,y+50], fill=(14,12,12), outline=(85,68,45), width=2)
    d.text((x+4,y+3), str((i+1)%10), font=small, fill=(120,110,90))
icons = [(150,20,20),(200,170,90),(60,180,40),(220,90,20)]
for i, c in enumerate(icons):
    x = 150 + i*58 + 12; y = H + 34
    d.polygon([(x+13,y),(x+26,y+13),(x+13,y+26),(x,y+13)], fill=c)
d.text((W-420, H+22), "Anjo Caído  Nv. 47", font=serif, fill=(210,195,160))
d.text((W-420, H+44), "Arautos do Juízo", font=small, fill=(170,40,30))
d.text((W-420, H+62), "Ruínas de Velgrad - Cemitério Norte", font=small, fill=(120,115,105))
# nomes sobre os personagens são passados como "x,y,nome,r,g,b"
for spec in sys.argv[3:]:
    x, y, name, r, g, b = spec.split(",")
    d.text((int(x)+1,int(y)+1), name, font=serif, fill=(0,0,0), anchor="mm")
    d.text((int(x),int(y)), name, font=serif, fill=(int(r),int(g),int(b)), anchor="mm")
out.save(dst); print(dst, out.size)
