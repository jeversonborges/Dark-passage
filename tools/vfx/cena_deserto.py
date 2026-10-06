"""Monta duas cenas de demonstracao do Deserto de Absinto com os efeitos de ambiente
(noite com a Vela e Nao-Julgados; tempestade de Amargo) e salva GIFs em assets/efeitos/_previa."""
import json, os, math
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
FX = os.path.abspath(os.path.join(HERE, '..', '..', 'assets', 'efeitos'))
SPR = os.path.abspath(os.path.join(HERE, '..', '..', 'design', 'estilo', 'fontes'))
W, H = 480, 270
_cache = {}


def load(name):
    if name not in _cache:
        m = json.load(open(os.path.join(FX, 'ambiente', name + '.json')))
        sh = np.asarray(Image.open(os.path.join(FX, 'ambiente', m['sheet'])).convert('RGBA')).astype(np.float32) / 255
        _cache[name] = (m, sh)
    return _cache[name]


def frame(name, k):
    m, sh = load(name)
    k %= m['frames']
    c, r = k % m['cols'], k // m['cols']
    return sh[r * m['frame_h']:(r + 1) * m['frame_h'], c * m['frame_w']:(c + 1) * m['frame_w']], m


def over(bg, f, x, y, alpha=1.):
    h, w = f.shape[:2]
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, bg.shape[1]), min(y + h, bg.shape[0])
    if x1 <= x0 or y1 <= y0: return
    s = f[y0 - y:y1 - y, x0 - x:x1 - x]
    a = s[..., 3:] * alpha
    bg[y0:y1, x0:x1] = s[..., :3] * a + bg[y0:y1, x0:x1] * (1 - a)


def at(bg, name, k, x, y, alpha=1.):
    f, m = frame(name, k)
    over(bg, f, x - m['anchor'][0], y - m['anchor'][1], alpha)


def tile(bg, name, k, alpha=1., ox=0, oy=0):
    f, m = frame(name, k)
    for y in range(-m['frame_h'] + oy % m['frame_h'], H, m['frame_h']):
        for x in range(-m['frame_w'] + ox % m['frame_w'], W, m['frame_w']):
            over(bg, f, x, y, alpha)


def sand(night=True):
    """chao de areia cinza com dunas suaves e veios (so para a cena)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = (np.sin(xx / 38 + yy / 21) * .5 + np.sin(xx / 17 - yy / 9) * .25 + np.sin(xx / 70 + yy / 50) * .6)
    lvl = np.floor((d + 1.4) / 2.8 * 4).clip(0, 3)
    base = np.array([[42, 39, 35], [50, 47, 42], [58, 55, 49], [66, 62, 55]], np.float32) / 255
    img = base[lvl.astype(int)]
    if night: img *= np.array([.55, .6, .62])
    v = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    img *= np.clip(1.25 - v * 1.6, .25, 1)[..., None]
    return img


def sprite(n):
    return np.asarray(Image.open(os.path.join(SPR, f'sprite_{n}.png')).convert('RGBA')).astype(np.float32) / 255


def put_char(bg, n, x, y, dark=1.):
    s = sprite(n).copy(); s[..., :3] *= dark
    yy, xx = np.mgrid[-5:6, -14:15]
    sh = (xx / 14) ** 2 + (yy / 5) ** 2 < 1
    reg = bg[y - 5:y + 6, x - 14:x + 15]; reg[sh] *= .5
    over(bg, s, x - s.shape[1] // 2, y - s.shape[0] + 6)


def save(frames, name, fps):
    ims = [Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).resize((W * 2, H * 2), Image.NEAREST) for f in frames]
    ims[0].save(os.path.join(FX, '_previa', name), save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=0)


def noite():
    base = sand(True)
    out = []
    for k in range(48):
        im = base.copy()
        for x, y in ((90, 200), (400, 90), (330, 230), (60, 70)):
            at(im, 'areia_veios_noite', k // 2 + x, x, y)
        at(im, 'vela_ar_limpo_chao', k, 170, 160)
        put_char(im, 'humano', 150, 180)
        put_char(im, 'tecnomancer', 205, 172)
        for x, y, ph in ((390, 170, 0), (430, 215, 5), (330, 120, 9)):
            put_char(im, 'mutante', x, y, dark=.35)
            at(im, 'naojulgado_brilho_noite', k // 3 + ph, x, y)
        at(im, 'vela_lampada_arco', k, 176, 70)
        at(im, 'vela_ar_limpo_borda', k, 170, 184)
        po = im.copy(); tile(po, 'amargo_po_noite', k, .9)
        yy, xx = np.mgrid[0:H, 0:W]
        dentro = (((xx - 170) / 128) ** 2 + ((yy - 160) / 64) ** 2) < 1     # a Vela limpa o ar
        im = np.where(dentro[..., None], im, po)
        out.append(im)
    save(out, 'cena_deserto_noite.gif', 12)


def tempestade():
    base = sand(False) * .8
    out = []
    for k in range(48):
        im = base.copy()
        at(im, 'areia_duna_soprando', k, 120, 150)
        at(im, 'areia_duna_soprando', k + 7, 300, 110)
        put_char(im, 'humano', 220, 200)
        put_char(im, 'anjo', 300, 210)
        tile(im, 'tempestade_amargo_nevoa', k, .9)
        tile(im, 'amargo_po_dia', k)
        tile(im, 'tempestade_amargo_graos', k)
        if 18 <= k < 38:
            f, m = frame('tempestade_amargo_rajada', k - 18)
            big = np.kron(f, np.ones((2, 2, 1)))
            over(im, big, -40, 40)
        out.append(im)
    save(out, 'cena_tempestade_amargo.gif', 12)


if __name__ == '__main__':
    noite(); tempestade()
    print('ok')
