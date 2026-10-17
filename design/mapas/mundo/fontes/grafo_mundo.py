#!/usr/bin/env python3
"""Desenha o grafo do mundo (quais mapas ligam com quais e por onde): design/mapas/mundo/imagens/grafo_mundo.png."""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).resolve().parent
SAIDA = AQUI.parent / "imagens" / "grafo_mundo.png"
W, H = 1800, 1150
F = lambda n, s: ImageFont.truetype(str(AQUI / n), s)
TIT, NOME, TXT, PEQ = F("PirataOne-Regular.ttf", 64), F("IMFeENsc28P.ttf", 34), F("IMFeENrm28P.ttf", 25), F("IMFeENit28P.ttf", 22)
OSSO, SEPIA, FERRUGEM, AMARGO, CINZA = (226, 214, 188), (150, 128, 98), (168, 82, 52), (122, 214, 96), (110, 100, 88)

# áreas externas: (x, y, nome, níveis, legenda, cor)
AREAS = {
    "jerusalem": (330, 400, "Jerusalém e Monte Hermon", "nível 1-12", "início dos Arautos", (176, 140, 92)),
    "sao_lazaro": (900, 470, "Cidade de São Lázaro", "nível 1-12", "início da Vigília · Deserto de Absinto", (196, 162, 104)),
    "eden": (1380, 330, "Novo Éden", "nível 12-30", "a mata da Enxertia", (96, 170, 150)),
    "atlantida": (1500, 820, "Atlântida", "nível 30-45", "entra quando for integrada", (90, 140, 170)),
    "egito": (560, 880, "Egito, a Terra Negra", "nível 50-70", "Mênfis Reerguida", (190, 150, 70)),
}
# estradas a pé: (a, b, nome, nota, nova)
ESTRADAS = [
    ("jerusalem", "sao_lazaro", "Estrada dos Peregrinos", "sem trava de nível", True),
    ("sao_lazaro", "eden", "Linha de Cinza", "", False),
    ("eden", "atlantida", "A Fenda", "a partir do nível 30", False),
    ("jerusalem", "egito", "Estrada do Êxodo", "nova · a partir do nível 45", True),
]
# masmorras e eventos: área -> lista
FILHOS = {
    "jerusalem": [("Gruta de Pã", "Minas, Noivas, Altar"), ("Evento Hermon", "Cume dos Vigilantes")],
    "sao_lazaro": [("Abatedouro", "Cripta da Trombeta Calada"), ("Biblioteca Soterrada", ""), ("O Agrak", "arena")],
    "eden": [("Árvore-Mãe", "Catacumba das Raízes"), ("Elevador", "A Torre, 5 andares")],
    "atlantida": [("Salões de Amenti", "")],
    "egito": [("Faium", "Labirinto de Hawara"), ("Vale dos Reis", "O Coração Endurecido")],
}
ANG = {"jerusalem": [205, 160], "sao_lazaro": [235, 270, 305], "eden": [325, 25], "atlantida": [180], "egito": [180, 212]}
RAIO = {"sao_lazaro": 190}
NOME_ACIMA = {"eden", "jerusalem"}
T_ROTULO = {"Estrada dos Peregrinos": .6, "Estrada do Êxodo": .55, "A Fenda": .55}


def fundo():
    im = Image.new("RGB", (W, H), (16, 13, 11))
    px = im.load(); rnd = random.Random(7)
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - W / 2) / W, (y - H / 2) / H)
            v = max(0.0, 1.0 - d * 1.5)
            n = rnd.random() * 6
            px[x, y] = (int(16 + 26 * v + n), int(13 + 20 * v + n), int(11 + 14 * v + n))
    return im


def tracejado(dr, a, b, cor, larg, passo=18):
    L = math.dist(a, b); n = int(L // passo)
    for i in range(0, n, 2):
        t0, t1 = i / n, min(1, (i + 1) / n)
        dr.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=cor, width=larg)


def centro_txt(dr, xy, s, f, cor):
    w = dr.textlength(s, font=f); dr.text((xy[0] - w / 2, xy[1]), s, font=f, fill=cor)


def main():
    im = fundo()
    brilho = Image.new("RGB", (W, H), (0, 0, 0)); bd = ImageDraw.Draw(brilho)
    dr = ImageDraw.Draw(im)
    # satélites (masmorras) primeiro, por baixo
    for k, lst in FILHOS.items():
        x, y = AREAS[k][:2]
        for (nome, sub), ang in zip(lst, ANG[k]):
            r = RAIO.get(k, 215); a = math.radians(ang)
            px, py = x + r * math.cos(a), y + r * math.sin(a)
            tracejado(dr, (x, y), (px, py), CINZA, 2, 10)
            dr.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(40, 34, 30), outline=SEPIA, width=2)
            centro_txt(dr, (px, py + 12), nome, PEQ, SEPIA)
            if sub: centro_txt(dr, (px, py + 36), sub, PEQ, CINZA)
    # estradas
    for a, b, nome, nota, nova in ESTRADAS:
        pa, pb = AREAS[a][:2], AREAS[b][:2]
        cor = AMARGO if nova else OSSO
        if nova: bd.line([pa, pb], fill=(60, 140, 50), width=22)
        dr.line([pa, pb], fill=(30, 26, 22), width=12)
        dr.line([pa, pb], fill=cor, width=5)
        t = T_ROTULO.get(nome, .5); mx, my = pa[0] + (pb[0] - pa[0]) * t, pa[1] + (pb[1] - pa[1]) * t
        w = max(dr.textlength(nome, font=TXT), dr.textlength(nota, font=PEQ)) + 30
        dr.rounded_rectangle([mx - w / 2, my - 26, mx + w / 2, my + (30 if nota else 8)], 8, fill=(22, 18, 15), outline=cor, width=2)
        centro_txt(dr, (mx, my - 22), nome, TXT, cor)
        if nota: centro_txt(dr, (mx, my + 4), nota, PEQ, AMARGO if nova else SEPIA)
    # áreas
    for k, (x, y, nome, nv, leg, cor) in AREAS.items():
        r = 62
        bd.ellipse([x - r - 30, y - r - 30, x + r + 30, y + r + 30], fill=tuple(c // 3 for c in cor))
        dr.ellipse([x - r, y - r, x + r, y + r], fill=(28, 23, 19), outline=cor, width=5)
        dr.ellipse([x - r + 10, y - r + 10, x + r - 10, y + r - 10], outline=tuple(c // 2 for c in cor), width=2)
        centro_txt(dr, (x, y - 18), nv, TXT, cor)
        ny = y - r - 92 if k in NOME_ACIMA else y + r + 8
        centro_txt(dr, (x, ny), nome, NOME, OSSO)
        centro_txt(dr, (x, ny + 38), leg, PEQ, SEPIA)
    brilho = brilho.filter(ImageFilter.GaussianBlur(26))
    im = Image.blend(im, Image.composite(brilho, im, Image.new("L", (W, H), 0)), 0)
    im = Image.fromarray(__import__("numpy").clip(__import__("numpy").asarray(im, dtype=float) + __import__("numpy").asarray(brilho, dtype=float) * .9, 0, 255).astype("uint8"))
    dr = ImageDraw.Draw(im)
    dr.text((60, 40), "Dark Passage · como os mapas se ligam", font=TIT, fill=OSSO)
    dr.text((62, 118), "a pé pelas estradas, além do teleporte (V) e da volta à fogueira (R)", font=PEQ, fill=SEPIA)
    ly = H - 70
    dr.line([(60, ly), (130, ly)], fill=OSSO, width=5); dr.text((145, ly - 15), "estrada que já existia", font=PEQ, fill=SEPIA)
    dr.line([(420, ly), (490, ly)], fill=AMARGO, width=5); dr.text((505, ly - 15), "nova ou destravada", font=PEQ, fill=AMARGO)
    tracejado(dr, (760, ly), (830, ly), CINZA, 2, 10); dr.text((845, ly - 15), "masmorra ou evento (porta própria)", font=PEQ, fill=SEPIA)
    v = Image.new("L", (W, H), 0); vd = ImageDraw.Draw(v); vd.rectangle([0, 0, W, H], fill=255)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    im.save(SAIDA)
    print(SAIDA)


if __name__ == "__main__":
    main()
