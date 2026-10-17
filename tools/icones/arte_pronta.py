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

def _cortes(occ, n):
    """Fronteiras entre peças: perto de cada divisão igual, a coluna (ou linha) com menos tinta."""
    L = len(occ); c = [0]
    for k in range(1, n):
        x0 = round(k * L / n); r = round(0.3 * L / n)
        c.append(x0 - r + int(np.argmin(occ[x0 - r:x0 + r])))
    return c + [L]

def peca(folha, idx, grade=(COLS, ROWS), cortes_x=None):
    im = Image.open(f"{PF}/{folha}").convert("RGBA")
    cols, rows = grade
    a = np.asarray(im)[..., 3] > 200
    cx, cy = ([0] + list(cortes_x) + [im.width]) if cortes_x else _cortes(a.sum(0), cols), _cortes(a.sum(1), rows)
    x, y = idx % cols, idx // cols
    c = im.crop((cx[x], cy[y], cx[x+1], cy[y+1]))
    a = np.asarray(c)[..., 3]
    m = a > 120                                          # ignora brilho solto e respingos do recorte
    ys, xs = np.where(m)
    return c.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))

def _pecas_auto(im, n, limiar=200, dilata=1):
    """Folha sem grade: acha as n maiores manchas (silhuetas) e ordena por linha, da esquerda para a direita."""
    a = np.asarray(im)[..., 3] > limiar
    E = 4; h, w = a.shape[0] // E, a.shape[1] // E
    m = a[:h*E, :w*E].reshape(h, E, w, E).any((1, 3))
    for _ in range(dilata):                              # fecha frestas (correntes, fitas soltas)
        m = m | np.roll(m, 1, 0) | np.roll(m, -1, 0) | np.roll(m, 1, 1) | np.roll(m, -1, 1)
    lab = np.zeros(m.shape, int); comps = []
    for y0, x0 in zip(*np.nonzero(m)):
        if lab[y0, x0]: continue
        cid = len(comps) + 1; pilha = [(y0, x0)]; lab[y0, x0] = cid; pts = []
        while pilha:
            y, x = pilha.pop(); pts.append((y, x))
            for yy, xx in ((y+1, x), (y-1, x), (y, x+1), (y, x-1)):
                if 0 <= yy < h and 0 <= xx < w and m[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = cid; pilha.append((yy, xx))
        ys, xs = zip(*pts); comps.append((len(pts), cid, min(xs), min(ys), max(xs), max(ys)))
    comps = sorted(comps, reverse=True)[:n]
    altura = np.median([c[5] - c[3] for c in comps])
    comps.sort(key=lambda c: c[3] + c[5]); linhas = []
    for c in comps:                                      # nova linha quando o centro desce mais de meia peça
        if linhas and (c[3] + c[5]) / 2 - (linhas[-1][0][3] + linhas[-1][0][5]) / 2 < altura * 0.5: linhas[-1].append(c)
        else: linhas.append([c])
    comps = [c for l in linhas for c in sorted(l, key=lambda c: c[2])]
    out = []
    for _, cid, x0, y0, x1, y1 in comps:
        sel = np.kron(lab[y0:y1+1, x0:x1+1] == cid, np.ones((E, E), bool))
        c = np.asarray(im.crop((x0*E, y0*E, (x1+1)*E, (y1+1)*E))).copy()
        c[..., 3] = np.where(sel[:c.shape[0], :c.shape[1]], c[..., 3], 0)
        out.append(Image.fromarray(c))
    return out

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
        if it["arte"].get("auto"):
            g = _pecas_auto(Image.open(f"{PF}/{it['arte']['folha']}").convert("RGBA"), it["arte"]["auto"], it["arte"].get("limiar", 200), it["arte"].get("dilata", 1))[it["arte"]["indice"]]
            ys, xs = np.where(np.asarray(g)[..., 3] > 120); g = g.crop((xs.min(), ys.min(), xs.max()+1, ys.max()+1))
        else: g = peca(it["arte"]["folha"], it["arte"]["indice"], it["arte"].get("grade", (COLS, ROWS)), it["arte"].get("cortes_x"))
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
