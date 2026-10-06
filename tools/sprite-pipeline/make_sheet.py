# Junta frames em sprite sheet e reduz a paleta (estilo retrô).
# Uso: python3 make_sheet.py <dir_frames> <saida.png> [cores]
import sys, glob
from PIL import Image
frames = [Image.open(f).convert("RGBA") for f in sorted(glob.glob(sys.argv[1] + "/*.png"))]
colors = int(sys.argv[3]) if len(sys.argv) > 3 else 16
w, h = frames[0].size
sheet = Image.new("RGBA", (w*len(frames), h), (0,0,0,0))
for i, f in enumerate(frames):
    alpha = f.getchannel("A").point(lambda a: 255 if a > 128 else 0)
    q = f.convert("RGB").quantize(colors, method=Image.Quantize.MEDIANCUT).convert("RGBA")
    q.putalpha(alpha); sheet.paste(q, (i*w, 0))
sheet.save(sys.argv[2]); print(sys.argv[2], sheet.size)
