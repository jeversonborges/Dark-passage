"""Gera todos os efeitos em assets/efeitos/ e as previas.

uso: python3 build.py [filtro...]
"""
import sys, os, json
from concurrent.futures import ProcessPoolExecutor
import numpy as np
from PIL import Image
import vfx
import efeitos_combate  # noqa
try:
    import efeitos_classes  # noqa
except ImportError:
    pass
try:
    import efeitos_chefes  # noqa
except ImportError:
    pass
try:
    import efeitos_ambiente  # noqa
except ImportError:
    pass
try:
    import efeitos_area  # noqa
except ImportError:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, '..', '..', 'assets', 'efeitos'))
PREV = os.path.join(OUT, '_previa')
SPR = os.path.abspath(os.path.join(HERE, '..', '..', 'design', 'estilo', 'fontes'))


def floor(w, h):
    """chao isometrico escuro para a previa."""
    img = np.zeros((h, w, 3), np.float32) + np.array([14, 12, 13]) / 255
    yy, xx = np.mgrid[0:h, 0:w]
    u = (xx / 24 + yy / 12); v = (xx / 24 - yy / 12)
    chk = ((np.floor(u) + np.floor(v)) % 2)
    base = np.where(chk[..., None] > 0, np.array([34, 31, 31]), np.array([28, 26, 26])) / 255
    edge = (np.abs(u - np.round(u)) < .04) | (np.abs(v - np.round(v)) < .04)
    img = np.where(edge[..., None], np.array([19, 17, 17]) / 255, base)
    # vinheta
    d = np.sqrt(((xx - w / 2) / w) ** 2 + ((yy - h / 2) / h) ** 2)
    img *= np.clip(1.25 - d * 1.5, .25, 1)[..., None]
    return img


def comp(bg, fr, x, y):
    out = bg.copy()
    h, w = fr.shape[:2]
    x0, y0 = max(x, 0), max(y, 0)
    x1, y1 = min(x + w, bg.shape[1]), min(y + h, bg.shape[0])
    if x1 <= x0 or y1 <= y0: return out
    f = fr[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32) / 255
    a = f[..., 3:]
    out[y0:y1, x0:x1] = f[..., :3] * a + out[y0:y1, x0:x1] * (1 - a)
    return out


def sprite(name):
    p = os.path.join(SPR, f'sprite_{name}.png')
    return np.asarray(Image.open(p).convert('RGBA')) if os.path.exists(p) else None


def job(name):
    frames, meta = vfx.build(name, OUT)
    e = vfx.EFFECTS[name]
    W, H = e['w'], e['h']
    PW, PH = max(W + 24, 72), max(H + 24, 72)
    bg = floor(PW, PH)
    ax, ay = e['anchor']
    ox, oy = PW // 2 - W // 2, PH // 2 - H // 2
    # alvo de referencia: personagem quando o efeito e de corpo
    chr_ = e.get('char')
    gifs = []
    for fr in frames:
        im = bg
        if chr_ is not None:
            s = sprite(chr_)
            if s is not None:
                if e['layer'] == 'chao':
                    im = comp(im, fr, ox, oy); fr = None
                im = comp(im, s, ox + ax - s.shape[1] // 2, oy + ay - s.shape[0] + 6)
        if fr is not None:
            im = comp(im, fr, ox, oy)
        gifs.append(Image.fromarray((np.clip(im, 0, 1) * 255).astype(np.uint8)).resize((PW * 2, PH * 2), Image.NEAREST))
    os.makedirs(PREV, exist_ok=True)
    gifs[0].save(os.path.join(PREV, name + '.gif'), save_all=True, append_images=gifs[1:],
                 duration=int(1000 / e['fps']), loop=0, disposal=1)
    # tira com todos os quadros
    strip = Image.new('RGB', (PW * 2 * min(len(gifs), 8), PH * 2 * ((len(gifs) + 7) // 8)))
    for k, g in enumerate(gifs):
        strip.paste(g, ((k % 8) * PW * 2, (k // 8) * PH * 2))
    strip.save(os.path.join(PREV, name + '_quadros.png'))
    return meta


def main():
    names = [n for n in vfx.EFFECTS if not sys.argv[1:] or any(a in n for a in sys.argv[1:])]
    with ProcessPoolExecutor(4) as ex:
        metas = list(ex.map(job, names))
    # indice geral
    idx_p = os.path.join(OUT, 'efeitos.json')
    idx = {}
    if os.path.exists(idx_p):
        idx = {m['name']: m for m in json.load(open(idx_p))}
    for m in metas:
        m = dict(m); m['sheet'] = f"{m['cat']}/{m['sheet']}"; idx[m['name']] = m
    idx = {k: v for k, v in idx.items() if k in vfx.EFFECTS}
    json.dump(sorted(idx.values(), key=lambda m: (m['cat'], m['name'])), open(idx_p, 'w'), ensure_ascii=False, indent=1)
    print(len(metas), 'efeitos gerados em', OUT)


if __name__ == '__main__':
    main()
