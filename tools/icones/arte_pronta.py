# Ícones a partir de arte pronta (pintada fora do pipeline SVG), como os anéis e túnicas do Jefin (2026-10-15).
# Lê os itens com motivo "arte_pronta" de design/skills-itens/itens.json; cada um aponta para uma folha em
# assets/icones/fontes/ (grade 4x2) e o índice da peça. Gera os mesmos arquivos do gerar_itens.py:
#   itens/{64,40,32}/<id>.png, itens/mochila/<id>.png (30 px/célula) e itens/mochila_2x/<id>.png (60 px/célula).
# Uso: python3 arte_pronta.py [ids...]   (só pillow + numpy; não precisa do Chromium)
import json, os, sys
import numpy as np
from PIL import Image, ImageEnhance
from posproc import indexar, contorno, _hex
from gerar_itens_brilho import brilho
PF = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
COLS, ROWS = 4, 2
COR_RAR = {"magico":"#6f9fc9","raro":"#c99a3e","excelente":"#9cff3a","lendario":"#c8302a"}

def peca(folha, idx):
    im = Image.open(f"{PF}/{folha}").convert("RGBA")
    cw, ch = im.width / COLS, im.height / ROWS
    x, y = idx % COLS, idx // COLS
    c = im.crop((round(x*cw), round(y*ch), round((x+1)*cw), round((y+1)*ch)))
    a = np.asarray(c)[..., 3]
    m = a > 24                                           # ignora respingos soltos do recorte
    ys, xs = np.where(m)
    return c.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))

def caber(g, W, H, pad, cores):
    esc = min((W - 2*pad) / g.width, (H - 2*pad) / g.height)
    r = g.resize((max(1, round(g.width*esc)), max(1, round(g.height*esc))), Image.LANCZOS)
    r = ImageEnhance.Contrast(r).enhance(1.08)           # a redução apaga o relevo; devolve um pouco
    r = Image.fromarray(contorno(indexar(r, cores)))
    tela = Image.new("RGBA", (W, H), (0, 0, 0, 0)); tela.paste(r, ((W - r.width)//2, (H - r.height)//2), r)
    return tela

if __name__ == "__main__":
    so = set(sys.argv[1:])
    itens = [i for i in json.load(open(f"{PF}/design/skills-itens/itens.json"))["itens"] if i.get("motivo") == "arte_pronta" and (not so or i["id"] in so)]
    for it in itens:
        g = peca(it["arte"]["folha"], it["arte"]["indice"])
        cor = COR_RAR.get(it.get("raridade"))
        for tam in (64, 40, 32):
            out = caber(g, tam, tam, max(1, tam // 16), 48 if tam == 64 else 36)
            if cor: out = brilho(out, cor, tam)
            out.save(f"{PF}/assets/icones/itens/{tam}/{it['id']}.png")
        w, h = it.get("grade", [1, 1])
        for cel, pasta in ((30, "mochila"), (60, "mochila_2x")):
            out = caber(g, w*cel, h*cel, max(2, cel // 10), 48)
            if cor: out = brilho(out, cor, cel * min(w, h))
            out.save(f"{PF}/assets/icones/itens/{pasta}/{it['id']}.png")
    print("ok", len(itens))
