# Prévia: sprites sobre chão isométrico escuro (pedra rachada, estilo Dark Eden).
import random
from PIL import Image, ImageDraw
random.seed(7)
W, H, TW, TH = 1024, 420, 64, 32
img = Image.new("RGBA", (W, H), (10, 9, 12, 255)); d = ImageDraw.Draw(img)
for gy in range(-2, H//(TH//2)+2):
    for gx in range(-1, W//TW+2):
        cx = gx*TW + (TW//2 if gy % 2 else 0); cy = gy*TH//2
        v = random.randint(22, 38); tint = random.choice([(0,0,0),(4,0,0),(0,2,4)])
        poly = [(cx, cy-TH//2), (cx+TW//2, cy), (cx, cy+TH//2), (cx-TW//2, cy)]
        d.polygon(poly, fill=(v+tint[0], v-2+tint[1], v+3+tint[2]), outline=(12,10,14))
        if random.random() < 0.15:
            d.line([(cx-8,cy-2),(cx+3,cy+4),(cx+10,cy)], fill=(8,7,9))
# vinheta
vig = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(vig)
for r in range(40):
    vd.rectangle([r*6, r*3, W-r*6, H-r*3], fill=int(r*5.5))
img = Image.composite(img, Image.new("RGBA", (W, H), (0,0,0,255)), vig)
for row, name in enumerate(["anjo", "demonio"]):
    s = Image.open(f"out/{name}_8dir.png"); fw = s.height
    for i in range(8):
        img.alpha_composite(s.crop((i*fw, 0, (i+1)*fw, fw)), (i*fw, 40 + row*170))
img.convert("RGB").save("out/preview_2000s.png"); print("ok")
