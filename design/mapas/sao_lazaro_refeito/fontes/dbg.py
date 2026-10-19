# Vista de cima para conferir o layout (debug): python3 dbg.py saida.png [x0 y0 x1 y1] [px]
import json, sys
from PIL import Image, ImageDraw
M = json.load(open("../area_inicial.json")); NT = M["size"]
a = sys.argv[2:]; x0, y0, x1, y1 = map(int, a[:4]) if len(a) >= 4 else (0, 0, NT, NT); S = int(a[4]) if len(a) > 4 else 5
COR = {"a": (92, 78, 58), "u": (104, 88, 64), "d": (122, 104, 76), "h": (12, 10, 10), "y": (40, 62, 46), "s": (78, 64, 48), "t": (84, 70, 54),
       "z": (54, 52, 50), "c": (110, 106, 100), "g": (66, 66, 52), "l": (140, 130, 120), "m": (74, 54, 48), "w": (40, 90, 30), "r": (60, 120, 50),
       "b": (72, 58, 44), "e": (66, 74, 46), "p": (52, 70, 40), "f": (58, 54, 42), "v": (70, 56, 44), "k": (90, 86, 80), "n": (80, 70, 66), "i": (60, 60, 64)}
W, H = (x1 - x0) * S, (y1 - y0) * S
im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
B = set(map(tuple, M["blocked"]))
P = lambda x, y: ((x - x0) * S, (y1 - y) * S)
for x in range(x0, x1):
    for y in range(y0, y1):
        c = COR.get(M["terreno"][x][y], (255, 0, 255))
        if (x, y) in B: c = tuple(int(v * .55) for v in c)
        px, py = P(x, y); d.rectangle([px, py - S, px + S - 1, py - 1], fill=c)
for p in M["props"]:
    if not (x0 <= p["x"] < x1 and y0 <= p["y"] < y1): continue
    px, py = P(p["x"], p["y"]); c = (255, 60, 60) if p.get("pendente") else ((150, 150, 150) if p.get("camada") == "chao" else (230, 200, 120))
    d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=c)
for s in M["spots"]:
    px, py = P(s["x"], s["y"]); r = s["raio"] * S; d.ellipse([px - r, py - r, px + r, py + r], outline=(120, 255, 120)); d.text((px - 30, py), s["id"], fill=(200, 255, 200))
for z in M["safe_zones"]:
    px, py = P(z["x"], z["y"]); r = z["radius"] * S; d.ellipse([px - r, py - r, px + r, py + r], outline=(120, 170, 255), width=2)
for g in M["spawns"]:
    px, py = P(g["x"], g["y"]); d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 0, 0))
for n in M["npcs"]:
    px, py = P(n["x"], n["y"]); d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(80, 160, 255)); d.text((px + 4, py - 4), n["id"][:8], fill=(160, 200, 255))
for p in M["props"]:
    if p.get("ponto") and x0 <= p["x"] < x1 and y0 <= p["y"] < y1:
        px, py = P(p["x"], p["y"]); d.text((px + 3, py + 2), p["ponto"][:14], fill=(255, 230, 150))
for t in range(0, NT, 10):
    if x0 <= t < x1: d.text((P(t, y1)[0], 2), str(t - 20), fill=(255, 255, 255))
    if y0 <= t < y1: d.text((2, P(x0, t)[1]), str(t - 20), fill=(255, 255, 255))
im.save(sys.argv[1])
