"""DARK PASSAGE - motor de efeitos visuais procedurais (pixel art).

Cada efeito desenha campos de intensidade em alta resolucao (supersample),
que depois sao reduzidos para a resolucao nativa (640x360) e mapeados em
rampas de cor fixas, sem dither. O resultado sao sprite sheets PNG com
alfa reto, prontos para AnimatedSprite2D no Godot.

Rampas "glow" sao luz emissiva (fogo, ouro sagrado, acido, arco eletrico).
Rampas "solid" sao materia (sangue, fumaca, cinza, osso, pedra).
"""
import math, json, os
import numpy as np
from PIL import Image

def rgb(h):
    h = h.lstrip('#'); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], float) / 255

# nome: (tipo, cores do escuro ao claro, alfas por nivel, contorno)
RAMPS = {
    # luz emissiva - paleta "Ferrugem Sagrada" (brasa, ouro, verde acido, arco eletrico)
    'fogo':     ('glow', ['#4a0c08', '#8a1a0e', '#d4401a', '#ff7a1a', '#ffb347', '#fff0c0']),
    'brasa':    ('glow', ['#3a0806', '#7a1612', '#c2340f', '#ff7a1a', '#ffc070']),
    'sagrado':  ('glow', ['#3e2c12', '#7a5a22', '#c99a3e', '#f0cf6a', '#fff6d0', '#ffffff']),
    'acido':    ('glow', ['#18280a', '#335a10', '#62a81e', '#9cff3a', '#e2ffb0']),
    'eletrico': ('glow', ['#0f2238', '#285a86', '#5aa8e0', '#9fd8ff', '#f4fcff']),
    'rubro':    ('glow', ['#32060a', '#6e1016', '#b81c26', '#ff4646', '#ffc4b4']),
    'amargo':   ('glow', ['#121c0c', '#243e12', '#46781e', '#7cc236', '#c4f68c']),   # po Amargo a noite (mais fraco que o acido)
    'areia':    ('solid', ['#3a3630', '#4e4a42', '#6a6458', '#857e70'], [.35, .5, .65, .8], False),   # areia cinza do deserto
    'po_amargo':('solid', ['#2c3428', '#3e4a38', '#56644a', '#6e7e5c'], [.5, .7, .85, 1], False),
    'arco':     ('glow', ['#1a2430', '#3a5a74', '#8ab8d8', '#d8f0ff', '#ffffff']),   # luz da Vela (lampada de arco)
    'eco':      ('glow', ['#141c22', '#26343e', '#46606e', '#7896a6', '#b8d0dc']),   # rastro de silhueta (aco frio)
    'aviso':    ('glow', ['#32060a', '#6e1016', '#b81c26', '#ff4646', '#ffc4b4']),   # telegrafia de chefe (sem textura)
    'abismo':   ('glow', ['#22081a', '#4a0e2a', '#86183a', '#d03048', '#ff9a78']),
    'alma':     ('glow', ['#1c2626', '#3a5450', '#76a094', '#c4e2d4', '#f4fff6']),
    'faisca':   ('glow', ['#4a3a2c', '#a07a4a', '#ffd890', '#ffffff']),
    'runa':     ('glow', ['#3a1a06', '#7a3a0e', '#d06a1a', '#ff9a3a', '#ffe0a0']),
    # materia
    'sangue':   ('solid', ['#240404', '#460a08', '#6e140f', '#9a2018'], [1, 1, 1, 1], True),
    'fumaca':   ('solid', ['#141112', '#1f1a1b', '#2b2527', '#3a3335', '#4b4345'], [.45, .6, .72, .8, .85], False),
    'poeira':   ('solid', ['#3a322c', '#524638', '#6e5e4e', '#8a7866'], [.4, .55, .7, .8], False),
    'sombra':   ('solid', ['#050304', '#0b0708', '#130c0e', '#1c1215'], [.55, .75, .9, 1], False),
    'cinza':    ('solid', ['#2a2626', '#46404a', '#6a6266', '#8e8688'], [1, 1, 1, 1], True),
    'pedra':    ('solid', ['#1d1a1c', '#2e2a2a', '#4a4446', '#6a5e56'], [1, 1, 1, 1], True),
    'osso':     ('solid', ['#4e463c', '#7e7464', '#b0a690', '#d3cab7'], [1, 1, 1, 1], True),
    'latao':    ('solid', ['#3a2410', '#6a4420', '#b07a3a', '#e6b672'], [1, 1, 1, 1], True),
    'carne':    ('solid', ['#2a0e0c', '#4a1a16', '#5a2622', '#7a3a30'], [1, 1, 1, 1], True),
    'praga':    ('solid', ['#1a2008', '#2e3e10', '#46601a', '#6a7058'], [1, 1, 1, 1], True),
    'aco':      ('solid', ['#141c24', '#24384a', '#3c5468', '#6a8aa0'], [1, 1, 1, 1], True),
}
# rampas que recebem textura de ruido (chama, fumaca, gosma): tira o aspecto de degrade liso
TEXTURE = {'fogo': .45, 'brasa': .4, 'rubro': .3, 'acido': .3, 'abismo': .35, 'fumaca': .55,
           'poeira': .5, 'sombra': .45, 'sangue': .25, 'praga': .3, 'eletrico': .15, 'sagrado': .12, 'alma': .3}
GLOW_ALPHA = [.42, .66, .86, 1, 1, 1]
OUTLINE = rgb('#0a0808')


class Canvas:
    """Um quadro. Coordenadas em pixels nativos (float)."""

    def __init__(self, w, h, ss=4):
        self.w, self.h, self.ss = w, h, ss
        self.f = {}          # rampa -> campo float (h*ss, w*ss)
        self.order = []
        self.frame = 0        # indice do quadro (textura rola com o tempo)

    def field(self, ramp):
        if ramp not in self.f:
            self.f[ramp] = np.zeros((self.h * self.ss, self.w * self.ss), np.float32)
            self.order.append(ramp)
        return self.f[ramp]

    def _win(self, x0, y0, x1, y1):
        s = self.ss
        X0 = max(0, int(math.floor(x0 * s))); X1 = min(self.w * s, int(math.ceil(x1 * s)))
        Y0 = max(0, int(math.floor(y0 * s))); Y1 = min(self.h * s, int(math.ceil(y1 * s)))
        if X1 <= X0 or Y1 <= Y0:
            return None
        xx = (np.arange(X0, X1, dtype=np.float32) + .5) / s
        yy = (np.arange(Y0, Y1, dtype=np.float32) + .5) / s
        return (slice(Y0, Y1), slice(X0, X1)), xx[None, :], yy[:, None]

    def _put(self, ramp, sl, v, op):
        F = self.field(ramp)
        if op == 'add': F[sl] += v
        elif op == 'max': np.maximum(F[sl], v, out=F[sl])
        elif op == 'sub': F[sl] = np.maximum(F[sl] - v, 0)
        elif op == 'mul': F[sl] *= v

    # ---------- primitivas ----------
    def blob(self, ramp, x, y, r, a=1., sy=1., hard=False, op='add'):
        if r <= 0 or a <= 0: return
        R = r * (1.05 if hard else 2.6)
        win = self._win(x - R, y - R * sy, x + R, y + R * sy)
        if not win: return
        sl, xx, yy = win
        d2 = (xx - x) ** 2 + ((yy - y) / sy) ** 2
        if hard:
            v = np.clip((r - np.sqrt(d2)) * self.ss * .5 + .5, 0, 1) * a
        else:
            v = a * np.exp(-d2 / (r * r))
        self._put(ramp, sl, v.astype(np.float32), op)

    def ring(self, ramp, x, y, r, w, a=1., sy=1., ang=None, op='add', jag=None):
        """Anel (elipse com sy<1 para o chao isometrico). ang=(a0,a1) em radianos.
        jag: funcao(theta)->fator de raio para bordas irregulares."""
        if r <= 0 or a <= 0: return
        R = r * (1.3 if jag else 1) + w * 3
        win = self._win(x - R, y - R * sy, x + R, y + R * sy)
        if not win: return
        sl, xx, yy = win
        dx, dy = xx - x, (yy - y) / sy
        d = np.sqrt(dx * dx + dy * dy)
        th = np.arctan2(dy, dx)
        rr = r * jag(th) if jag else r
        v = a * np.exp(-((d - rr) / max(w, .2)) ** 2)
        if ang is not None:
            a0, a1 = ang
            t = (th - a0) % (2 * math.pi)
            span = (a1 - a0) % (2 * math.pi) or 2 * math.pi
            fade = np.clip(np.minimum(t, span - t) / (span * .18 + 1e-6), 0, 1)
            v = v * np.where(t <= span, fade, 0)
        self._put(ramp, sl, v.astype(np.float32), op)

    def disc(self, ramp, x, y, r, a=1., sy=1., edge=1., op='add', inner=None):
        """Disco com degrade da borda (edge = largura do degrade)."""
        R = r + edge * 2
        win = self._win(x - R, y - R * sy, x + R, y + R * sy)
        if not win: return
        sl, xx, yy = win
        d = np.sqrt((xx - x) ** 2 + ((yy - y) / sy) ** 2)
        v = np.clip((r - d) / max(edge, .3), 0, 1) * a
        if inner is not None: v = v * inner(d / max(r, 1e-3))
        self._put(ramp, sl, v.astype(np.float32), op)

    def line(self, ramp, x0, y0, x1, y1, w, a=1., w1=None, a1=None, hard=False, op='add'):
        """Segmento com largura (e alfa) interpolados de uma ponta a outra."""
        w1 = w if w1 is None else w1
        a1 = a if a1 is None else a1
        if max(w, w1) <= 0: return
        R = max(w, w1) * (1.2 if hard else 2.6)
        win = self._win(min(x0, x1) - R, min(y0, y1) - R, max(x0, x1) + R, max(y0, y1) + R)
        if not win: return
        sl, xx, yy = win
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy + 1e-9
        t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1)
        px, py = x0 + t * dx - xx, y0 + t * dy - yy
        d = np.sqrt(px * px + py * py)
        ww = w + (w1 - w) * t
        aa = a + (a1 - a) * t
        if hard:
            v = np.clip((ww - d) * self.ss * .5 + .5, 0, 1) * aa
        else:
            v = aa * np.exp(-(d / np.maximum(ww, .15)) ** 2)
        self._put(ramp, sl, v.astype(np.float32), op)

    def poly(self, ramp, pts, w, a=1., w1=None, a1=None, hard=False, op='max'):
        n = len(pts) - 1
        if n < 1: return
        w1 = w if w1 is None else w1
        a1 = a if a1 is None else a1
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            self.line(ramp, *pts[i], *pts[i + 1], w + (w1 - w) * t0, a + (a1 - a) * t0,
                      w + (w1 - w) * t1, a + (a1 - a) * t1, hard=hard, op=op)

    def flame(self, ramp, x, y, w, h, ph=0., a=1., lean=0., op='max'):
        """Lingua de fogo com base em (x,y), largura w, altura h. ph anima a ondulacao.
        Miolo claro embaixo, ponta escura e fina em cima."""
        if h <= 0 or w <= 0 or a <= 0: return
        win = self._win(x - w * 1.6 - abs(lean) * h, y - h * 1.05, x + w * 1.6 + abs(lean) * h, y + w * .6)
        if not win: return
        sl, xx, yy = win
        v = np.clip((y - yy) / h, -.3, 1.2)                      # 0 base, 1 ponta
        wob = np.sin(v * 7 - ph * 6.283) * .22 * v + np.sin(v * 13 + ph * 12.57) * .08 * v
        cx = x + (lean * v * v + wob) * w * 1.6
        width = w * np.clip(1 - v, 0, 1) ** .55 * (1 + .25 * np.sin(v * 3.14))
        width = np.where(v < 0, w * np.sqrt(np.clip(1 + v / .3, 0, 1)), width)
        d = np.abs(xx - cx) / np.maximum(width, 1e-3)
        body = np.clip(1 - d, 0, 1) ** .7
        val = a * body * (1.25 - .9 * np.clip(v, 0, 1)) * np.where(v < 0, np.clip(1 + v / .3, 0, 1), 1)
        self._put(ramp, sl, val.astype(np.float32), op)

    def stamp(self, ramp, mask, x, y, a=1., op='max'):
        """Carimba uma mascara (alfa 0..1, em pixels nativos) com o canto superior esquerdo em (x,y)."""
        s = self.ss
        m = np.kron(mask.astype(np.float32), np.ones((s, s), np.float32)) * a
        X0, Y0 = int(round(x * s)), int(round(y * s))
        h, w = m.shape
        x0, y0 = max(X0, 0), max(Y0, 0)
        x1, y1 = min(X0 + w, self.w * s), min(Y0 + h, self.h * s)
        if x1 <= x0 or y1 <= y0: return
        self._put(ramp, (slice(y0, y1), slice(x0, x1)), m[y0 - Y0:y1 - Y0, x0 - X0:x1 - X0], op)

    def mul(self, ramp, arr):
        if ramp in self.f: self.f[ramp] *= arr

    def grid(self):
        s = self.ss
        xx = (np.arange(self.w * s, dtype=np.float32) + .5) / s
        yy = (np.arange(self.h * s, dtype=np.float32) + .5) / s
        return xx[None, :], yy[:, None]

    # ---------- composicao ----------
    def render(self, order=None):
        out = np.zeros((self.h, self.w, 4), np.float32)
        ramps = order or self.order
        solids = [r for r in ramps if r in self.f and RAMPS[r][0] == 'solid']
        glows = [r for r in ramps if r in self.f and RAMPS[r][0] == 'glow']
        s = self.ss
        for r in solids + glows:
            spec = RAMPS[r]
            cols = np.array([rgb(c) for c in spec[1]])
            n = len(cols)
            I = self.f[r].reshape(self.h, s, self.w, s).mean((1, 3))
            k = 0 if getattr(self, 'notex', False) else TEXTURE.get(r, 0)
            if k:
                nz = fbm(self.w, self.h, 5, 1000 + len(r) * 31, ox=self.frame * .7, oy=self.frame * 2.2)
                nz = (nz - nz.mean()) / (nz.std() + 1e-6)
                # o miolo mais quente fica intacto; bordas e meios-tons ganham textura
                I = I * (1 + k * np.clip(nz, -1.6, 1.6) * np.clip(1.4 - I, 0, 1))
            if spec[0] == 'glow':
                th = 0.07 + 0.88 * (np.arange(n) / n) ** 1.25
                al = np.array(GLOW_ALPHA[:n])
            else:
                th = 0.32 + 0.6 * (np.arange(n) / n)
                al = np.array(spec[2])
            lvl = (I[..., None] >= th).sum(-1) - 1
            m = lvl >= 0
            li = np.clip(lvl, 0, n - 1)
            c = cols[li]; a = np.where(m, al[li], 0)[..., None]
            if spec[0] == 'solid' and len(spec) > 3 and spec[3]:
                # contorno escuro de 1px nas gotas/detritos
                solid = (a[..., 0] > .99)
                edge = np.zeros_like(solid)
                for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    edge |= np.roll(np.roll(solid, dy, 0), dx, 1)
                edge &= ~solid & (out[..., 3] < .5)
                c = np.where(edge[..., None], OUTLINE, c)
                a = np.where(edge[..., None], 1., a)
            out[..., :3] = c * a + out[..., :3] * (1 - a)
            out[..., 3:] = a + out[..., 3:] * (1 - a)
        # acumulado e pre-multiplicado; o PNG guarda alfa reto (cor/alfa)
        res = np.concatenate([np.clip(out[..., :3], 0, 1), np.clip(out[..., 3:], 0, 1)], -1)
        a = res[..., 3:]
        res[..., :3] = np.where(a > 0, res[..., :3] / np.maximum(a, 1e-6), 0)
        res[..., :3] = np.clip(res[..., :3], 0, 1)
        return (res * 255 + .5).astype(np.uint8)


# ---------- ruido ----------
def value_noise(w, h, cell, seed, ox=0., oy=0.):
    """Ruido suave (0..1), tamanho w x h, celula em pixels; deslocavel."""
    r = np.random.default_rng(seed)
    gw, gh = int(w / cell) + 4, int(h / cell) + 4
    g = r.random((gh, gw)).astype(np.float32)
    big = np.array(Image.fromarray((g * 255).astype(np.uint8)).resize((gw * 8, gh * 8), Image.BICUBIC), np.float32) / 255
    sx, sy = 8 / cell, 8 / cell
    ys = ((np.arange(h) + oy) * sy) % (gh * 8 - 1)
    xs = ((np.arange(w) + ox) * sx) % (gw * 8 - 1)
    return big[ys.astype(int)[:, None], xs.astype(int)[None, :]]


def fbm(w, h, cell, seed, ox=0., oy=0., oct=3):
    n = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(oct):
        n += amp * value_noise(w, h, cell / 2 ** o, seed + o * 17, ox * 2 ** o, oy * 2 ** o); tot += amp; amp *= .5
    return n / tot


# ---------- utilidades ----------
def ease_out(t, p=2): return 1 - (1 - min(max(t, 0), 1)) ** p
def ease_in(t, p=2): return min(max(t, 0), 1) ** p
def smooth(t): t = min(max(t, 0), 1); return t * t * (3 - 2 * t)
def bell(t, a=.0, b=1.):
    """0 fora de [a,b], sobe e desce em sino dentro."""
    if t <= a or t >= b: return 0.
    u = (t - a) / (b - a); return math.sin(math.pi * u)
def fade(t, fin=.1, fout=.3):
    """envelope: sobe ate fin, fica 1, cai nos ultimos fout."""
    if t < fin: return t / fin if fin > 0 else 1
    if t > 1 - fout: return max(0, (1 - t) / fout)
    return 1.


def ballistic(p0, v0, t, g=0., k=0.):
    """posicao com gravidade g (px/s2 para baixo) e arrasto k."""
    if k > 0:
        e = (1 - math.exp(-k * t)) / k
        x = p0[0] + v0[0] * e
        y = p0[1] + v0[1] * e + g / k * (t - e)
    else:
        x = p0[0] + v0[0] * t
        y = p0[1] + v0[1] * t + .5 * g * t * t
    return x, y


def lightning(rng, x0, y0, x1, y1, rough=.35, depth=5):
    pts = [(x0, y0), (x1, y1)]
    disp = math.hypot(x1 - x0, y1 - y0) * rough
    for _ in range(depth):
        new = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            mx, my = (ax + bx) / 2, (ay + by) / 2
            L = math.hypot(bx - ax, by - ay) + 1e-6
            nx, ny = -(by - ay) / L, (bx - ax) / L
            o = rng.uniform(-disp, disp)
            new += [(mx + nx * o, my + ny * o), (bx, by)]
        pts = new; disp *= .5
    return pts


# ---------- registro e exportacao ----------
EFFECTS = {}

def effect(name, cat, size, frames, fps=15, loop=False, anchor=None, layer='frente', desc='', char=None, dirs=1):
    """anchor: ponto (px) do quadro que vai no pe/centro do alvo.
    layer: 'chao' (abaixo dos personagens) ou 'frente'.
    dirs=8: efeito direcional desenhado nas 8 direcoes do chao isometrico; a folha tem uma
    linha por direcao (d=0 leste/direita da tela, d=2 norte/cima, d=4 oeste, d=6 sul, de 45 em 45
    graus no plano do chao, sentido anti-horario visto de cima). A funcao recebe (c, t, i, d)."""
    def deco(fn):
        EFFECTS[name] = dict(name=name, cat=cat, w=size[0], h=size[1], frames=frames, fps=fps,
                             loop=loop, anchor=anchor or (size[0] // 2, size[1] // 2), layer=layer,
                             desc=desc, fn=fn, char=char, dirs=dirs)
        return fn
    return deco


def build(name, outdir, ss=4):
    e = EFFECTS[name]
    W, H, N = e['w'], e['h'], e['frames']
    rng_seed = abs(hash(name)) % (2 ** 31)
    setup = e['fn'](np.random.default_rng(sum(map(ord, name)) * 7919))
    frames = []
    D = e.get('dirs', 1)
    for d in range(D):
        for i in range(N):
            c = Canvas(W, H, ss); c.frame = i
            t = i / N if e['loop'] else i / max(N - 1, 1)
            if D > 1: setup(c, t, i, d)
            else: setup(c, t, i)
            frames.append(c.render())
    if D > 1:
        cols = N; rows = D                      # uma linha por direcao
    else:
        cols = min(N, max(1, 2048 // W), 8)
        rows = math.ceil(N / cols)
    sheet = np.zeros((rows * H, cols * W, 4), np.uint8)
    for i, f in enumerate(frames):
        r, cl = divmod(i, cols)
        sheet[r * H:(r + 1) * H, cl * W:(cl + 1) * W] = f
    d = os.path.join(outdir, e['cat']); os.makedirs(d, exist_ok=True)
    Image.fromarray(sheet).save(os.path.join(d, name + '.png'), optimize=True)
    meta = {k: e[k] for k in ('name', 'cat', 'frames', 'fps', 'loop', 'anchor', 'layer', 'desc', 'char')}
    from acentos import acentuar, titulo
    meta['desc'] = acentuar(meta['desc'])
    meta['title'] = titulo(name, meta['desc'])
    if meta['desc'].startswith(meta['title'] + ':'):
        rest = meta['desc'][len(meta['title']) + 1:].strip()
        meta['resumo'] = rest[:1].upper() + rest[1:]
    else:
        meta['resumo'] = meta['desc']
    meta.update(frame_w=W, frame_h=H, cols=cols, rows=rows, sheet=name + '.png')
    if D > 1:
        meta.update(directions=D, dir_order='linha d = direcao d: 0 leste (direita da tela), 1 nordeste, 2 norte (cima), 3 noroeste, 4 oeste, 5 sudoeste, 6 sul (baixo), 7 sudeste; angulos no plano do chao')
    with open(os.path.join(d, name + '.json'), 'w') as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=1)
    return frames, meta
