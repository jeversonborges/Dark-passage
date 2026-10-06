# Folha de contato para conferir poses: python3 contato.py <dir_brutos> <saida.png> [escala]
import sys, glob, os
from PIL import Image, ImageDraw
src, dst = sys.argv[1], sys.argv[2]; sc = float(sys.argv[3]) if len(sys.argv) > 3 else .5
rows = []
for d in sorted(glob.glob(src + "/*/")):
    fs = sorted(glob.glob(d + "*.png"))
    if fs: rows.append((os.path.basename(d[:-1]), fs))
im0 = Image.open(rows[0][1][0]); w, h = int(im0.width*sc), int(im0.height*sc)
cols = max(len(f) for _, f in rows)
out = Image.new("RGB", (cols*w, len(rows)*h), (40, 38, 42)); dr = ImageDraw.Draw(out)
for r, (name, fs) in enumerate(rows):
    for c, f in enumerate(fs):
        im = Image.open(f).convert("RGBA").resize((w, h), Image.LANCZOS)
        out.paste(im, (c*w, r*h), im); dr.text((c*w+3, r*h+3), f"{name} {os.path.basename(f)[:-4]}", fill=(200, 200, 200))
    dr.line([(0, r*h), (out.width, r*h)], fill=(70, 70, 70))
out.save(dst); print(dst, out.size)
