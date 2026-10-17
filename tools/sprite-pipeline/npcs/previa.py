# Prancha de prévia dos NPCs (estilo das pranchas do Egito): python3 previa.py <saida.png> "<título>" id1 id2 ...
# Mostra cada NPC no tamanho do jogo ampliado 2x (pixels nítidos): parado de frente (SE), de costas (NW) e andando,
# com nome e título tirados de design/missoes/dados/npcs.json (ou de NOMES abaixo, para NPCs ainda fora dele).
import sys, os, json
from PIL import Image, ImageDraw, ImageFont
H = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.join(H, "..", "..", "..")
F = os.path.join(RAIZ, "design", "mapas", "fontes")
out, titulo, ids = sys.argv[1], sys.argv[2], sys.argv[3:]
NPC = {n["id"]: n for n in json.load(open(os.path.join(RAIZ, "design/missoes/dados/npcs.json")))["npcs"]}
for f in ("entregas/jerusalem_hermon/npcs_acrescimo.json",):
    p = os.path.join(RAIZ, f)
    if os.path.exists(p):
        d = json.load(open(p)); d = d.get("npcs", d)
        for n in (d if isinstance(d, list) else d.values()): NPC.setdefault(n["id"], n)
K = int(os.environ.get("ESCALA", 2))
def frame(i, anim, d, f):
    p = os.path.join(RAIZ, "assets/personagens/npcs", i); m = json.load(open(f"{p}/sprites.json"))
    fw, fh = m["frame_size"]; r = m["rows_dirs"].index(d)
    sh = Image.open(f"{p}/{anim}.png"); im = sh.crop((f*fw, r*fh, f*fw + fw, r*fh + fh))
    return im, m
cards = []
for i in ids:
    vs = [frame(i, "idle", "SE", 0), frame(i, "idle", "NW", 0), frame(i, "walk", "SW", 2)]
    bb = None
    for im, _ in vs:
        b = im.getbbox(); bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    ims = [im.crop(bb).resize(((bb[2]-bb[0])*K, (bb[3]-bb[1])*K), Image.NEAREST) for im, _ in vs]
    cards.append((i, ims))
ft = ImageFont.truetype(f"{F}/PirataOne-Regular.ttf", 64); fn = ImageFont.truetype(f"{F}/IMFeENsc28P.ttf", 30)
fs = ImageFont.truetype(f"{F}/IMFeENit28P.ttf", 22)
gap = 18; cw = [sum(im.width for im in ims) + gap*2 for _, ims in cards]
mh = max(max(im.height for im in ims) for _, ims in cards)
por = int(os.environ.get("POR_LINHA", 3)); linhas = [cards[k:k+por] for k in range(0, len(cards), por)]
lw = [sum(sum(im.width for im in ims) + gap*2 + 60 for _, ims in l) for l in linhas]
W = max(lw) + 80; Hh = 140 + len(linhas)*(mh + 110) + 30
img = Image.new("RGB", (W, Hh), (19, 16, 17)); dr = ImageDraw.Draw(img)
OURO = (201, 168, 108); CINZA = (150, 138, 120)
tw = dr.textlength(titulo, font=ft); dr.text(((W - tw)/2, 30), titulo, font=ft, fill=OURO)
dr.line([(40, 118), (W - 40, 118)], fill=(70, 60, 45))
y = 150
for l, w in zip(linhas, lw):
    x = (W - w)/2 + 30
    for i, ims in l:
        cw_ = sum(im.width for im in ims) + gap*2; xx = x
        for im in ims:
            img.paste(im, (int(xx), int(y + mh - im.height)), im); xx += im.width + gap
        n = NPC.get(i, {}); nome = n.get("nome", i); tit = n.get("titulo", "")
        nw = dr.textlength(nome, font=fn); dr.text((x + (cw_ - nw)/2, y + mh + 14), nome, font=fn, fill=OURO)
        if tit:
            t2 = tit[0].upper() + tit[1:]; tw2 = dr.textlength(t2, font=fs); dr.text((x + (cw_ - tw2)/2, y + mh + 50), t2, font=fs, fill=CINZA)
        x += cw_ + 60
    y += mh + 110
img.save(out); print(out, img.size)
