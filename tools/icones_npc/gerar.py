"""Ícones de função dos NPCs (medalhão de latão com pictograma), gerados por código.

Saída: assets/ui/npc/<tipo>.png (64x64). O jogo lê game/assets/ext/ui/npc/ (sync.sh copia).
Uso:  python3 tools/icones_npc/gerar.py
"""
import math
import os
from PIL import Image, ImageDraw, ImageFilter

S = 4                 # supersampling
N = 64                # tamanho final
W = N * S
C = W // 2
OURO = (230, 194, 122, 255)
OURO_ESC = (150, 110, 48, 255)
SOMBRA = (8, 5, 3, 255)
RAIZ = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "ui", "npc")


def p(v):
    """Coordenadas de desenho em unidades de 256 (a arte inteira cabe nessa grade)."""
    return int(round(v * W / 256))


def medalhao():
    """Disco escuro com degradê radial, aro de latão e contorno."""
    im = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((p(2), p(2), W - p(2), W - p(2)), fill=(6, 4, 2, 255))
    raio = W // 2 - p(4)
    disco = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    px = disco.load()
    for y in range(W):
        for x in range(W):
            dx, dy = x - C, y - C
            r = math.hypot(dx, dy) / raio
            if r > 1.0:
                continue
            t = min(1.0, r * 0.9)
            cor = (int(70 * (1 - t) + 20 * t), int(46 * (1 - t) + 13 * t), int(26 * (1 - t) + 9 * t), 255)
            px[x, y] = cor
    im.alpha_composite(disco)
    d = ImageDraw.Draw(im)
    d.ellipse((p(4), p(4), W - p(4), W - p(4)), outline=OURO_ESC, width=p(9))
    d.ellipse((p(22), p(22), W - p(22), W - p(22)), outline=(90, 62, 26, 255), width=p(3))
    return im


def sombrear(glifo):
    """Sombra escura deslocada para o pictograma sair do fundo."""
    sombra = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    a = glifo.split()[3].filter(ImageFilter.GaussianBlur(p(4)))
    sombra.paste(SOMBRA, (p(6), p(10)), a)
    return sombra


def compor(desenhar):
    base = medalhao()
    glifo = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    desenhar(ImageDraw.Draw(glifo))
    base.alpha_composite(sombrear(glifo))
    base.alpha_composite(glifo)
    return base.resize((N, N), Image.LANCZOS)


def _rect(d, x0, y0, x1, y1, cor, r=0):
    if r:
        d.rounded_rectangle((p(x0), p(y0), p(x1), p(y1)), radius=p(r), fill=cor)
    else:
        d.rectangle((p(x0), p(y0), p(x1), p(y1)), fill=cor)


def _linha(d, a, b, larg, cor=OURO):
    d.line((p(a[0]), p(a[1]), p(b[0]), p(b[1])), fill=cor, width=p(larg))
    for ponto in (a, b):
        d.ellipse((p(ponto[0] - larg / 2), p(ponto[1] - larg / 2), p(ponto[0] + larg / 2), p(ponto[1] + larg / 2)), fill=cor)


def bau(d):
    _rect(d, 62, 116, 194, 182, OURO, 7)
    _rect(d, 62, 88, 194, 140, OURO, 22)
    _rect(d, 62, 116, 194, 124, OURO_ESC)
    for x in (92, 164):
        _rect(d, x - 4, 92, x + 4, 180, OURO_ESC)
    _rect(d, 116, 112, 140, 146, SOMBRA, 4)
    d.ellipse((p(122), p(122), p(134), p(134)), fill=OURO)


def pata(d):
    d.ellipse((p(92), p(124), p(164), p(190)), fill=OURO)
    for cx, cy, rx, ry in ((66, 110, 15, 19), (96, 82, 15, 19), (130, 76, 15, 19), (160, 98, 15, 19)):
        d.ellipse((p(cx - rx), p(cy - ry), p(cx + rx), p(cy + ry)), fill=OURO)


def ferreiro(d):
    # espada na diagonal, guarda e punho
    _linha(d, (74, 58), (150, 150), 13)
    d.polygon([(p(108), p(124)), (p(122), p(108)), (p(146), p(134)), (p(132), p(150))], fill=OURO_ESC)
    _linha(d, (150, 150), (174, 176), 16, OURO_ESC)
    # escudo no canto inferior esquerdo
    escudo = [(p(56), p(112)), (p(106), p(100)), (p(106), p(152)), (p(82), p(192)), (p(56), p(152))]
    d.polygon(escudo, fill=OURO)
    d.polygon([(p(64), p(120)), (p(98), p(112)), (p(98), p(150)), (p(81), p(180)), (p(64), p(150))], fill=OURO_ESC)


def pocao(d):
    _rect(d, 104, 70, 152, 112, OURO_ESC, 4)
    _rect(d, 98, 52, 158, 74, OURO, 5)
    d.ellipse((p(74), p(98), p(182), p(206)), fill=OURO)
    d.ellipse((p(86), p(110), p(170), p(194)), fill=(8, 6, 4, 255))
    d.ellipse((p(94), p(128), p(162), p(196)), fill=(126, 196, 110, 255))
    d.ellipse((p(104), p(134), p(124), p(146)), fill=(214, 240, 190, 255))


def pvp(d):
    _linha(d, (62, 62), (194, 194), 20)
    _linha(d, (194, 62), (62, 194), 20)
    for a, b in (((98, 150), (110, 128)), ((158, 150), (146, 128))):
        _linha(d, a, b, 7, OURO_ESC)
    for ponto in ((62, 62), (194, 62), (62, 194), (194, 194)):
        d.ellipse((p(ponto[0] - 9), p(ponto[1] - 9), p(ponto[0] + 9), p(ponto[1] + 9)), fill=OURO_ESC)


def _pergaminho_base(d, x0, x1, y0, y1):
    _rect(d, x0, y0, x1, y1, (226, 206, 160, 255), 6)
    d.ellipse((p(x0 - 9), p(y0), p(x0 + 9), p(y1)), fill=OURO)
    d.ellipse((p(x1 - 9), p(y0), p(x1 + 9), p(y1)), fill=OURO)
    d.rectangle((p(x1 - 9), p(y0 + 2), p(x1 + 9), p(y1 - 2)), fill=(226, 206, 160, 255))


def missao(d):
    _pergaminho_base(d, 74, 182, 66, 190)
    for i, y in enumerate((94, 116, 138, 160)):
        _rect(d, 92, y, 164 - (i % 2) * 14, y + 5, (92, 60, 30, 255), 2)


def convite(d):
    _rect(d, 58, 100, 198, 156, (226, 206, 160, 255), 26)
    d.ellipse((p(44), p(98), p(74), p(158)), fill=OURO)
    d.ellipse((p(182), p(98), p(212), p(158)), fill=OURO)
    _rect(d, 118, 92, 138, 164, (168, 50, 42, 255), 2)
    d.ellipse((p(92), p(74), p(128), p(104)), fill=(168, 50, 42, 255))
    d.ellipse((p(128), p(74), p(164), p(104)), fill=(168, 50, 42, 255))
    d.ellipse((p(120), p(86), p(136), p(102)), fill=(120, 30, 26, 255))


def livro(d):
    d.polygon([(p(128), p(92)), (p(68), p(78)), (p(68), p(180)), (p(128), p(194))], fill=OURO)
    d.polygon([(p(128), p(92)), (p(188), p(78)), (p(188), p(180)), (p(128), p(194))], fill=OURO)
    d.polygon([(p(80), p(92)), (p(122), p(102)), (p(122), p(180)), (p(80), p(170))], fill=(226, 206, 160, 255))
    d.polygon([(p(176), p(92)), (p(134), p(102)), (p(134), p(180)), (p(176), p(170))], fill=(226, 206, 160, 255))
    _linha(d, (128, 92), (128, 194), 4, OURO_ESC)


def estrela(d):
    pontos = []
    for i in range(10):
        r = 76 if i % 2 == 0 else 32
        a = -math.pi / 2 + i * math.pi / 5
        pontos.append((p(128 + r * math.cos(a)), p(134 + r * math.sin(a))))
    d.polygon(pontos, fill=OURO)


ICONES = {
    "bau": bau,              # armazém, tesoureiro, vendedor
    "pata": pata,            # pet shop, coletor de pets
    "ferreiro": ferreiro,    # espada e escudo
    "pocao": pocao,          # alquimista
    "pvp": pvp,              # arena
    "missao": missao,        # missões
    "convite": convite,      # convites (Sariel, Zaqueu)
    "livro": livro,          # biblioteca, escriba
    "estrela": estrela,      # ascensão de classe, treinador
}


def main():
    os.makedirs(RAIZ, exist_ok=True)
    for nome, desenho in ICONES.items():
        compor(desenho).save(os.path.join(RAIZ, nome + ".png"))
        print("ok", nome)


if __name__ == "__main__":
    main()
