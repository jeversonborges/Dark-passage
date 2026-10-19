# Monta a prévia comparativa: 8 direções em grade 4x2; em cada célula, antiga (esquerda) e refeita (direita).
# Uso: python3 comparativo_arvore.py <pasta_do_arvore_refeita> <saida.png>
# Lê meta.json e os *_raw.png gerados por arvore_refeita.py. Alinha pela âncora (base da árvore).
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

src, saida = sys.argv[1], sys.argv[2]
meta = json.load(open(os.path.join(src, "meta.json")))["meta"]
ESC = .8                          # escala da prévia (sprites são ~460 a 730 px)
COL, LIN = 4, 2
CELL_W, CELL_H = 820, 560
MARGEM_TOPO = 120
FUNDO = (96, 84, 70)              # chão de areia neutro: a casca escura tem que aparecer
FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
ROTULOS = ["0°", "45°", "90°", "135°", "180°", "225°", "270°", "315°"]

f_tit = ImageFont.truetype(FONTE, 34)
f_rot = ImageFont.truetype(FONTE, 24)

W = CELL_W * COL
H = MARGEM_TOPO + CELL_H * LIN
img = Image.new("RGB", (W, H), FUNDO)
d = ImageDraw.Draw(img)
d.text((30, 24), "Árvore morta: antiga x refeita em low-poly", font=f_tit, fill=(245, 232, 205))
d.text((30, 72), "Esquerda: kit atual (assets.py)   ·   Direita: refeita, 1 002 tris, casca fosca", font=f_rot, fill=(235, 220, 195))

for k in range(8):
    cx0 = (k % COL) * CELL_W
    cy0 = MARGEM_TOPO + (k // COL) * CELL_H
    d.text((cx0 + 20, cy0 + 12), ROTULOS[k], font=f_rot, fill=(255, 240, 210))
    for chave, dx in (("antiga", CELL_W*.27), ("nova", CELL_W*.66)):
        m = meta[chave][str(k)]
        spr = Image.open(os.path.join(src, f"{chave}_{k}_raw.png")).convert("RGBA")
        spr = spr.resize((int(spr.width*ESC), int(spr.height*ESC)), Image.LANCZOS)
        ax, ay = m["anchor"][0]*ESC, m["anchor"][1]*ESC
        img.paste(spr, (int(cx0 + dx - ax), int(cy0 + CELL_H*.82 - ay)), spr)
    d.text((cx0 + CELL_W*.27 - 60, cy0 + CELL_H - 48), "antiga", font=f_rot, fill=(40, 30, 24))
    d.text((cx0 + CELL_W*.66 - 60, cy0 + CELL_H - 48), "refeita", font=f_rot, fill=(40, 30, 24))
img.save(saida, optimize=True)
print("OK", saida, img.size)
