"""Clima e ambiente do Deserto de Absinto (design/missoes/historia.md, secao 1.1).

Os efeitos de clima sao LADRILHAVEIS: podem ser repetidos lado a lado e em cima/baixo
cobrindo a tela inteira, e o ultimo quadro emenda no primeiro."""
import math
import numpy as np
from vfx import effect, ease_out, ease_in, smooth, bell, lightning
from efeitos_classes import motes

TAU = 2 * math.pi


def wrap_blob(c, ramp, x, y, r, a, W, H, **kw):
    """blob que da a volta nas bordas (para ladrilhar)."""
    x %= W; y %= H
    for dx in (-W, 0, W):
        for dy in (-H, 0, H):
            X, Y = x + dx, y + dy
            if -r * 3 < X < W + r * 3 and -r * 3 < Y < H + r * 3:
                c.blob(ramp, X, Y, r, a, **kw)


def wrap_line(c, ramp, x, y, dx, dy, w, a, W, H, **kw):
    x %= W; y %= H
    for ox in (-W, 0, W):
        for oy in (-H, 0, H):
            X, Y = x + ox, y + oy
            if -abs(dx) - 4 < X < W + abs(dx) + 4 and -abs(dy) - 4 < Y < H + abs(dy) + 4:
                c.line(ramp, X, Y, X + dx, Y + dy, w, a, **kw)


def tile_noise(c, t, W, H, waves, seed):
    """ruido periodico no espaco (ladrilha) e no tempo (loop): soma de ondas com frequencias inteiras."""
    xx, yy = c.grid()
    r = np.random.default_rng(seed)
    n = np.zeros((c.h * c.ss, c.w * c.ss), np.float32)
    tot = 0
    for kx, ky, om, amp in waves:
        ph = r.uniform(0, TAU)
        n += amp * np.sin(TAU * (kx * xx / W + ky * yy / H) - TAU * om * t + ph)
        tot += amp
    return n / tot          # -1..1


# ---------------- po Amargo caindo ----------------
def _po(rng, noite):
    W, H = 160, 120
    ps = []
    for _ in range(70 if noite else 90):
        ps.append(dict(x=rng.uniform(0, W), y=rng.uniform(0, H), m=int(rng.integers(1, 3)),
                       sw=rng.uniform(2, 6), k=int(rng.integers(1, 3)), ph=rng.uniform(0, TAU),
                       s=rng.uniform(.55, 1.0), tw=rng.uniform(0, TAU), big=rng.random() < .12))
    def f(c, t, i):
        c.notex = True
        for p in ps:
            y = p['y'] + p['m'] * H * t                  # cai m telas por ciclo
            x = p['x'] + 1 * W * t * (p['m'] - 1) + p['sw'] * math.sin(TAU * p['k'] * t + p['ph'])
            if noite:
                cint = .55 + .45 * math.sin(TAU * 2 * t + p['tw'])   # cintila
                wrap_blob(c, 'amargo', x, y, p['s'] * (2.4 if p['big'] else 1.1), (1.0 if p['big'] else 1.5) * cint, W, H)
            else:
                wrap_blob(c, 'po_amargo', x, y, p['s'] * (1.4 if p['big'] else .95), 1.4, W, H, hard=True)
                if p['big']: wrap_line(c, 'po_amargo', x, y - 3, 0, 3, .5, .2, W, H, a1=.9)
    return f


effect('amargo_po_dia', 'ambiente', (160, 120), 48, fps=12, loop=True, anchor=(0, 0),
       desc='Po Amargo caindo de dia: graos cinza-esverdeados descendo devagar. Ladrilhavel, cobrir a tela.')(lambda rng: _po(rng, False))
effect('amargo_po_noite', 'ambiente', (160, 120), 48, fps=12, loop=True, anchor=(0, 0),
       desc='Po Amargo caindo a noite: os graos brilham verde fraco e cintilam. Ladrilhavel, cobrir a tela.')(lambda rng: _po(rng, True))


# ---------------- tempestade de Amargo ----------------
@effect('tempestade_amargo_nevoa', 'ambiente', (192, 108), 32, fps=12, loop=True, anchor=(0, 0),
        desc='Tempestade de Amargo (camada de fundo): nuvens de po verde-cinza correndo com o vento. Ladrilhavel; por cima do mundo, com transparencia.')
def _(rng):
    def f(c, t, i):
        c.notex = True
        W, H = 192, 108
        n = tile_noise(c, t, W, H, [(1, 1, 1, 1), (2, 3, 2, .8), (3, 4, 2, .5), (1, 6, 3, .35), (4, 7, 3, .25), (6, 9, 4, .15)], 11)
        F = c.field('areia'); F += np.clip(.36 + .42 * n, 0, .62)
    return f


@effect('tempestade_amargo_graos', 'ambiente', (192, 108), 16, fps=16, loop=True, anchor=(0, 0),
        desc='Tempestade de Amargo (camada da frente): rajadas de graos riscando na diagonal e lascas verdes brilhando. Ladrilhavel.')
def _(rng):
    W, H = 192, 108
    st = [(rng.uniform(0, W), rng.uniform(0, H), int(rng.integers(1, 3)), rng.uniform(6, 16), rng.random() < .15) for _ in range(70)]
    def f(c, t, i):
        c.notex = True
        for x0, y0, k, L, glow in st:
            x = x0 + k * W * t                 # anda k telas por ciclo
            y = y0                             # vento horizontal: so x anda (k telas por ciclo)
            dx, dy = L, L * .18
            if glow:
                wrap_line(c, 'amargo', x, y, dx * .5, dy * .5, .35, 1.2, W, H, a1=.2)
            else:
                wrap_line(c, 'areia', x, y, dx, dy, .45, .2, W, H, w1=.6, a1=1.5)
    return f


@effect('tempestade_amargo_rajada', 'ambiente', (256, 96), 20, fps=14, anchor=(0, 48),
        desc='Rajada da tempestade: uma parede de po verde atravessa a tela da esquerda para a direita (evento, tocar de vez em quando).')
def _(rng):
    pf = [(rng.uniform(-60, 0), rng.uniform(10, 86), rng.uniform(8, 18)) for _ in range(40)]
    def f(c, t, i):
        head = -40 + 340 * ease_in(t, 1.2)
        for x0, y, r in pf:
            x = head + x0
            c.blob('areia', x, y, r * 1.4, .75, sy=.35, op='max')
            c.blob('areia', x - r, y + 2, r * .8, .55, sy=.3, op='max')
        for k in range(14):
            x = head + 10 - k * 9
            c.line('amargo', x, 20 + k * 5, x + 18, 22 + k * 5, .3, .1, a1=1.2)
    return f


# ---------------- areia soprando nas dunas ----------------
@effect('areia_duna_soprando', 'ambiente', (128, 48), 24, fps=12, loop=True, anchor=(24, 40),
        desc='Areia soprando da crista da duna: veu de graos levantando e correndo com o vento (ancora na crista).')
def _(rng):
    gr = [(rng.uniform(0, 1), rng.uniform(-6, 6), rng.uniform(.5, 1.2), rng.uniform(.6, 1)) for _ in range(60)]
    def f(c, t, i):
        cx, cy = 24, 40
        for ph, x0, s, sp in gr:
            u = (t * 2 * sp + ph) % 1
            x = cx + x0 + 100 * u
            y = cy - 2 - 22 * math.sqrt(u) * sp + 10 * u * u + math.sin(u * 9 + ph * 7) * 1.5
            a = 1.4 * bell(u, 0, 1)
            c.line('areia', x - 4 * s, y + .8, x, y, .55 * s, a * .8, a1=a * 1.4)
            if ph < .08:
                c.blob('amargo', x, y, .5, .9 * bell(u, 0, 1))
        for k in range(3):
            u = (t + k / 3) % 1
            c.blob('areia', cx + 20 + 70 * u, cy - 8 - 10 * u, 6 + 8 * u, 1.3 * bell(u, 0, 1), sy=.45, op='max')
    return f


@effect('areia_veios_noite', 'ambiente', (96, 48), 24, fps=10, loop=True, layer='chao', anchor=(48, 24),
        desc='Veios verdes da areia acesos a noite: decalque de chao (2x2 ladrilhos) que pulsa devagar. Espalhar pelo deserto.')
def _(rng):
    vs = [lightning(rng, rng.uniform(10, 40), rng.uniform(14, 34), rng.uniform(56, 88), rng.uniform(14, 34), .35, 4) for _ in range(3)]
    sp = [(rng.uniform(16, 80), rng.uniform(12, 36), rng.uniform(0, 1)) for _ in range(8)]
    def f(c, t, i):
        p = .6 + .4 * math.sin(TAU * t)
        for k, v in enumerate(vs):
            q = .6 + .4 * math.sin(TAU * (t + k / 3))
            pts = [(x, 24 + (y - 24) * .9) for x, y in v]
            c.poly('amargo', pts, 1.2, .35 * q, op='max')
            c.poly('amargo', pts, .35, .9 * q, op='max')
        for x, y, ph in sp:
            c.blob('amargo', x, y, .5, 1.3 * bell((t + ph) % 1, 0, .5))
        # recorte em losango isometrico
        xx, yy = c.grid()
        mask = np.clip((1 - (np.abs(xx - 48) / 48 + np.abs(yy - 24) / 24)) * 6, 0, 1)
        c.mul('amargo', mask)
    return f


# ---------------- Nao-Julgados ----------------
@effect('naojulgado_brilho_noite', 'ambiente', (72, 120), 16, fps=10, loop=True, anchor=(36, 110),
        desc='Brilho dos Nao-Julgados a noite: halo verde de Amargo em volta do corpo, olhos acesos e fiapos subindo; mais forte que a areia. Desenhar por cima do sprite do morto.')
def _(rng):
    wisp = [(rng.uniform(-12, 12), rng.uniform(0, 1), rng.uniform(.6, 1), rng.uniform(10, 80)) for _ in range(16)]
    vein = [(rng.uniform(-8, 8), rng.uniform(20, 80), rng.uniform(0, TAU)) for _ in range(10)]
    def f(c, t, i):
        gx, gy = 36, 110
        p = .8 + .2 * math.sin(TAU * t)
        # halo do corpo: coluna suave com ombros (silhueta ~95px)
        c.blob('amargo', gx, gy - 46, 13, .13 * p, sy=3.4)
        c.blob('amargo', gx, gy - 72, 12, .1 * p, sy=1.2)
        # pontos de Amargo "na pele", piscando
        for x, h, ph in vein:
            c.blob('amargo', gx + x, gy - h, .7, 1.5 * (.4 + .6 * max(0, math.sin(TAU * t * 2 + ph))))
        # olhos
        e = .75 + .25 * math.sin(TAU * t * 2)
        c.blob('amargo', gx - 3, gy - 86, .8, 2.2 * e)
        c.blob('amargo', gx + 3, gy - 86, .8, 2.2 * e)
        # fiapos subindo do corpo
        for x, ph, s, h0 in wisp:
            u = (t + ph) % 1
            yy = gy - h0 - 30 * u
            xx = gx + x * (1 + u * .5) + math.sin(u * 7 + x) * 2
            c.line('amargo', xx, yy, xx + math.sin(u * 7 + x + .6) * 2, yy - 4, .4, 1.3 * bell(u, 0, 1) * s)
        c.blob('amargo', gx, gy, 14, .6 * p, sy=.35)
        c.ring('amargo', gx, gy, 12, .6, .7 * p, sy=.35)
    return f


# ---------------- a Vela: ar limpo ----------------
@effect('vela_ar_limpo_chao', 'ambiente', (320, 176), 24, fps=10, loop=True, layer='chao', anchor=(160, 88),
        desc='Ar limpo da Vela (chao): poca de luz branca-azulada da lampada de arco e anel de Amargo assentado na borda (raio ~140x70 px).')
def _(rng):
    sed = [(rng.uniform(0, TAU), rng.uniform(.96, 1.06), rng.uniform(.8, 2)) for _ in range(160)]
    def f(c, t, i):
        cx, cy, R = 160, 88, 140
        fl = .92 + .05 * math.sin(TAU * t * 3) + .03 * math.sin(TAU * t * 7)
        c.disc('arco', cx, cy, R * .9, .12 * fl, sy=.5, edge=6)
        c.blob('arco', cx, cy, 30, .2 * fl, sy=.5)
        c.blob('arco', cx, cy, 10, .5 * fl, sy=.5)
        # sedimento verde na borda (o Amargo assenta ali)
        for a, rr, s in sed:
            x, y = cx + math.cos(a) * R * rr, cy + math.sin(a) * R * rr * .5
            c.blob('po_amargo', x, y, s, 1.3, sy=.6, hard=True)
        c.ring('amargo', cx, cy, R * 1.01, 2.5, .35 + .1 * math.sin(TAU * t), sy=.5)
    return f


@effect('vela_ar_limpo_borda', 'ambiente', (320, 200), 32, fps=12, loop=True, anchor=(160, 112),
        desc='Ar limpo da Vela (frente): o po Amargo cai do lado de fora e para na borda da luz, assentando no chao; dentro o ar fica limpo.')
def _(rng):
    cx, cy, R = 160, 112, 140
    ps = []
    for _ in range(140):
        x, y = rng.uniform(0, 320), rng.uniform(0, 200)
        ps.append((x, y, rng.uniform(0, 1), rng.uniform(.6, 1.0), rng.uniform(0, TAU)))
    def f(c, t, i):
        for x, y0, ph, s, tw in ps:
            u = (t + ph) % 1
            y = y0 - 60 + 120 * u                 # cai 120px por ciclo
            # distancia (isometrica) ate o centro da Vela, no ponto de chao abaixo do grao
            gy = min(y + 30, 200)
            d = math.hypot(x - cx, (gy - cy) * 2) / R
            if d < 1.0:
                # perto da borda: o grao desacelera, desce e apaga
                k = smooth((d - .82) / .18)
                if k <= 0: continue
                a = k
            else:
                a = 1
            cint = .6 + .4 * math.sin(TAU * 2 * t + tw)
            c.blob('amargo', x + math.sin(u * 6 + tw) * 2, y, s, 1.5 * a * cint * bell(u, 0, 1) ** .3)
        # cortina leve marcando a fronteira
        c.ring('amargo', cx, cy, R, 5, .16, sy=.5, ang=(math.pi * 1.05, TAU * .975))
    return f


@effect('vela_lampada_arco', 'ambiente', (72, 72), 16, fps=16, loop=True, anchor=(36, 36),
        desc='A Vela acesa: arco eletrico estalando entre as bobinas e halo branco-azulado (centro da lampada na ancora).')
def _(rng):
    def f(c, t, i):
        cx, cy = 36, 36
        fl = .85 + .15 * ((i * 7) % 5) / 4
        c.blob('arco', cx, cy, 22, .45 * fl)
        c.blob('arco', cx, cy, 8, 1.3 * fl)
        c.blob('arco', cx, cy, 2.5, 2)
        for j in range(2):
            p = lightning(np.random.default_rng(i * 5 + j), cx - 12, cy + (j - .5) * 4, cx + 12, cy - (j - .5) * 4, .35, 4)
            c.poly('arco', p, .4, 1.6)
        for k in range(6):
            a = TAU * k / 6 + t * TAU
            c.line('arco', cx + math.cos(a) * 10, cy + math.sin(a) * 10, cx + math.cos(a) * (22 + 4 * fl), cy + math.sin(a) * (22 + 4 * fl), .5, .5, a1=0)
    return f


# ---------------- limite do mundo disfarcado ----------------
@effect('limite_tempestade', 'ambiente', (192, 144), 32, fps=12, loop=True, anchor=(0, 144),
        desc='Limite do mundo disfarcado: muralha de tempestade de Amargo que fica mais densa para o lado de fora (topo do quadro = fora do mapa). Ladrilhavel na horizontal; girar para cada borda e escurecer o jogador que insistir.')
def _(rng):
    W, H = 192, 144
    st = [(rng.uniform(0, W), rng.uniform(0, H), int(rng.integers(1, 3)), rng.uniform(8, 18), rng.random() < .12) for _ in range(90)]
    def f(c, t, i):
        c.notex = True
        xx, yy = c.grid()
        dens = np.clip(1 - yy / H, 0, 1) ** 1.3                 # 1 no topo (fora), 0 embaixo (dentro do mapa)
        n = tile_noise(c, t, W, 10 ** 6, [(1, 0, 1, 1), (2, 0, -1, .7), (3, 0, 2, .5), (5, 0, -2, .35), (7, 0, 3, .25), (11, 0, -3, .15)], 21)
        m = tile_noise(c, t, W, 10 ** 6, [(4, 0, 2, 1), (7, 0, 3, .5)], 22)
        F = c.field('areia'); F += np.clip(dens * (1.05 + .25 * n) + .12 * m * dens - .05, 0, 1.2)
        S = c.field('sombra'); S += np.clip((dens - .45) * 1.8 + .15 * n, 0, 1.1)
        for x0, y0, k, L, glow in st:
            x = x0 + k * W * t
            d = max(0, 1 - y0 / H)
            if glow:
                wrap_line(c, 'amargo', x, y0, L * .5, 1, .35, 1.1 * d, W, 10 ** 6, a1=.2)
            else:
                wrap_line(c, 'areia', x, y0, L, 2, .45, .2 * d, W, 10 ** 6, w1=.6, a1=1.4 * d)
    return f
