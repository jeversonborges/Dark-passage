# Sprite sheet no estilo 2000s: reduz o supersample com suavização (sprites
# da época eram renders com AA), paleta indexada de até 256 cores
# compartilhada pela sheet, alpha binário e contorno escuro de 1px.
# Uso: python3 make_sheet_2000s.py <dir_frames> <saida.png> [cores]
import sys, glob
from PIL import Image, ImageFilter
colors = int(sys.argv[3]) if len(sys.argv) > 3 else 64
frames = [Image.open(f).convert("RGBA") for f in sorted(glob.glob(sys.argv[1] + "/*.png"))]
w, h = frames[0].width // 2, frames[0].height // 2
sheet = Image.new("RGBA", (w*len(frames), h))
for i, f in enumerate(frames):
    sheet.paste(f.resize((w, h), Image.LANCZOS), (i*w, 0))
a = sheet.getchannel("A")
body = a.point(lambda v: 255 if v > 160 else 0)
# sombra "blob" elíptica sob os pés, como nos jogos da época
from PIL import ImageDraw
shadow = Image.new("L", sheet.size, 0); sd = ImageDraw.Draw(shadow)
for i in range(len(frames)):
    cx = i*w + w//2; sd.ellipse([cx-w*0.2, h*0.84, cx+w*0.2, h*0.95], fill=255)
shadow = shadow.filter(ImageFilter.GaussianBlur(2)).point(lambda v: 255 if v > 100 else 0)
outline = body.filter(ImageFilter.MaxFilter(3))
rgb = sheet.convert("RGB").quantize(colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).convert("RGB")
res = Image.new("RGBA", sheet.size, (0,0,0,0))
res.paste((8,6,10,255), mask=outline)
res.paste((0,0,0,110), mask=shadow)                    # sombra semitransparente
res.paste(rgb, mask=body)
res.save(sys.argv[2]); print(sys.argv[2], res.size)
