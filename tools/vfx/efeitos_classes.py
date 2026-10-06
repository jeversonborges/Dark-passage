"""Skills das 6 classes (design/classes.md). Uma rampa emissiva por classe:
Anjo=sagrado, Demonio=brasa/abismo, Cultista=rubro, Humano=fogo/faisca, Mutante=acido, Tecnomancer=eletrico/runa."""
import math
import numpy as np
from vfx import (effect, ease_out, ease_in, smooth, bell, fade, ballistic, lightning)

TAU = 2 * math.pi


# ---------------- ajudantes ----------------
def crescent(c, ramp, cx, cy, r, a0, a1, t, width=3.6, sy=.55, edge='faisca', edge_a=1.5):
    """Rastro em arco que nasce de a0 ate a1 e some pela cauda."""
    rev = ease_out(min(t / .4, 1), 3)
    cut = ease_in(max((t - .2) / .8, 0), 1.6)
    head = a0 + (a1 - a0) * rev; tail = a0 + (a1 - a0) * cut
    if abs(head - tail) < .04: return head
    n = 40
    for k in range(n):
        u = k / (n - 1)
        th = tail + (head - tail) * u
        g = (th - a0) / (a1 - a0)
        w = width * math.sin(math.pi * min(max(g, 0), 1)) ** .8 * (1 - .5 * t) + .4
        rr = r - w * .6
        c.blob(ramp, cx + math.cos(th) * rr, cy + math.sin(th) * rr * sy, w * .9, .6 * u ** .8)
        if edge:
            c.line(edge, cx + math.cos(th) * r, cy + math.sin(th) * r * sy,
                   cx + math.cos(th + .08) * r, cy + math.sin(th + .08) * r * sy, .5, edge_a * u ** .8 * (1 - t * .6))
    return head


def rune(c, ramp, x, y, s, seed, a=1.):
    """Glifo pequeno feito de 3 tracos (cada seed um glifo)."""
    r = np.random.default_rng(seed)
    pts = [(x + r.uniform(-1, 1) * s, y + r.uniform(-1, 1) * s * 1.3) for _ in range(4)]
    c.poly(ramp, pts, .35, a)
    c.line(ramp, x, y - s * 1.3, x, y + s * 1.3, .35, a)


def rune_circle(c, ramp, x, y, R, t, a=1., sy=.5, n=10, spin=1., seed=0, rings=True):
    if rings:
        c.ring(ramp, x, y, R, .7, 1.2 * a, sy=sy)
        c.ring(ramp, x, y, R * .8, .4, .9 * a, sy=sy)
    for k in range(n):
        th = TAU * k / n + t * spin
        rune(c, ramp, x + math.cos(th) * R * .9, y + math.sin(th) * R * .9 * sy, 1.3, seed + k, 1.3 * a)


def star(c, ramp, x, y, R, n, a=1., sy=.5, rot=0., w=.45, skip=2):
    """Estrela/pentagrama inscrito no chao."""
    pts = [(x + math.cos(rot + TAU * k / n) * R, y + math.sin(rot + TAU * k / n) * R * sy) for k in range(n)]
    for k in range(n):
        p, q = pts[k], pts[(k + skip) % n]
        c.line(ramp, *p, *q, w, a)


def burst(c, ramp, x, y, t, n, R, seed, a=1.6, g=0., s=.6, up=0.):
    r = np.random.default_rng(seed)
    for _ in range(n):
        th = r.uniform(0, TAU); v = r.uniform(.4, 1) * R
        px, py = ballistic((x, y), (math.cos(th) * v, math.sin(th) * v * .6 - up), t, g=g, k=2.5)
        c.blob(ramp, px, py, s * r.uniform(.7, 1.3), a * (1 - t))


def motes(c, ramp, x, y, t, n, w, h, seed, s=.55, a=1.7, loop=False, sway=2.):
    r = np.random.default_rng(seed)
    for _ in range(n):
        ox, ph, sp = r.uniform(-w, w), r.uniform(0, 1), r.uniform(.6, 1.2)
        u = (t * sp + ph) % 1 if loop else (t - ph * .5) / (1 - ph * .5)
        if not 0 < u < 1: continue
        c.blob(ramp, x + ox + math.sin(u * 6 + ox) * sway, y - h * u, s, a * bell(u, 0, 1))


def feather(c, x, y, ang, L, a=1.):
    dx, dy = math.cos(ang), math.sin(ang)
    c.line('osso', x, y, x + dx * L, y + dy * L, .5, a * 1.4, w1=1.1, hard=True)
    c.line('osso', x, y, x + dx * L * .6, y + dy * L * .6, .9, a * 1.4, w1=.6, hard=True)


# ======================================================================
# ANJO - ouro sagrado, penas sujas
# ======================================================================

@effect('anjo_lamina_veredito', 'anjo', (96, 96), 10, fps=18,
        desc='Lamina do Veredito: corte sagrado com cruz de luz no impacto.')
def _(rng):
    def f(c, t, i):
        crescent(c, 'sagrado', 48, 50, 30, -3.0, .6, t, width=4.2, edge='sagrado', edge_a=1.8)
        k = bell(t, .25, 1)
        if k > 0:
            x, y = 62, 58
            L = 22 * ease_out(min((t - .25) / .25, 1))
            c.line('sagrado', x, y - L, x, y + L * .7, 1.6 * k, 1.5 * k, w1=.4)
            c.line('sagrado', x - L * .5, y - L * .3, x + L * .5, y - L * .3, 1.3 * k, 1.4 * k)
            c.blob('sagrado', x, y - L * .3, 6 * k, 1.2 * k)
            burst(c, 'sagrado', x, y - 6, (t - .25) / .75, 12, 40, 3, up=20)
    return f


@effect('anjo_toque_graca', 'anjo', (64, 112), 18, fps=14, anchor=(32, 104), char='anjo',
        desc='Toque de Graca: penas douradas caem e uma cruz de luz cura o alvo.')
def _(rng):
    fe = [(rng.uniform(-18, 18), rng.uniform(0, .45), rng.uniform(0, TAU)) for _ in range(9)]
    def f(c, t, i):
        gx, gy = 32, 104
        k = bell(t, 0, 1)
        c.blob('sagrado', gx, gy - 2, 16 * k, .8 * k, sy=.4)
        c.ring('sagrado', gx, gy - 2, 14 + 4 * t, .5, 1.1 * k, sy=.4)
        # coluna suave
        c.line('sagrado', gx, gy, gx, gy - 95, 7 * k, .45 * k, w1=2 * k, a1=0)
        for x, d, ph in fe:
            u = (t - d) / (1 - d)
            if 0 < u < 1:
                y = gy - 96 + 90 * ease_out(u, 1.5)
                xx = gx + x + math.sin(u * 8 + ph) * 4
                feather(c, xx, y, .8 + math.sin(u * 8 + ph) * .6, 4, 1 - u ** 3)
                c.blob('sagrado', xx, y, 1.3, .9 * (1 - u))
        motes(c, 'sagrado', gx, gy, t, 14, 12, 80, 5)
    return f


@effect('anjo_asas_ascensao', 'anjo', (128, 96), 12, fps=18, anchor=(96, 80),
        desc='Asas da Ascensao: rastro de asas de luz e penas no voo curto (indo para a direita).')
def _(rng):
    fe = [(rng.uniform(10, 110), rng.uniform(40, 80), rng.uniform(0, TAU), rng.uniform(0, .3)) for _ in range(14)]
    def f(c, t, i):
        head = 20 + 80 * ease_out(min(t / .5, 1))
        k = 1 - ease_in(max(t - .3, 0) / .7)
        # imagens residuais de asas
        for j in range(4):
            x = head - j * 18
            if x < 10: continue
            a = k * (1 - j / 4)
            for s in (-1, 1):
                for q in range(6):
                    ang = -math.pi / 2 - s * (.35 + q * .22)
                    L = 26 - q * 2.5
                    c.line('sagrado', x, 50, x + math.cos(ang) * L * -.6, 50 + math.sin(ang) * L * .8, .9, .7 * a, w1=.3, a1=.2)
        c.line('sagrado', 14, 60, head, 60, .4, 0, w1=3.5 * k, a1=1.2 * k)
        c.blob('sagrado', head, 56, 8 * k, 1.1 * k)
        for x, y, ph, d in fe:
            u = (t - d) / (1 - d)
            if 0 < u < 1 and x < head:
                feather(c, x + 6 * u, y - 10 + 22 * u, ph + u * 4, 3.5, 1 - u)
    return f


@effect('anjo_halo_ardente', 'anjo', (176, 112), 16, fps=16, anchor=(88, 72),
        desc='Halo Ardente: anel de luz que se expande e cega; aliados no anel recebem cura.')
def _(rng):
    def f(c, t, i):
        cx, cy = 88, 72
        e = ease_out(t, 2.5)
        R = 8 + 72 * e
        a = 1 - ease_in(t, 1.5)
        c.ring('sagrado', cx, cy, R, 2.6 * (1 - t) + .6, 1.3 * a, sy=.5)
        c.ring('sagrado', cx, cy, R * .92, .5, 1.6 * a, sy=.5)
        c.ring('sagrado', cx, cy - 10 * e, R * .7, 1.2, .6 * a, sy=.45)
        # clarao inicial que cega
        fl = bell(t, 0, .35)
        c.blob('sagrado', cx, cy - 18, 16 * fl, 1.0 * fl, sy=.8)
        c.blob('sagrado', cx, cy - 18, 5 * fl, 2 * fl)
        for k in range(16):
            th = TAU * k / 16
            c.line('sagrado', cx + math.cos(th) * R * .8, cy + math.sin(th) * R * .4,
                   cx + math.cos(th) * R * 1.05, cy + math.sin(th) * R * .52 - 6 * a, .5, 1.2 * a, w1=.2)
        motes(c, 'sagrado', cx, cy, t, 20, R, 40, 9)
    return f


@effect('anjo_sentenca', 'anjo', (32, 44), 16, fps=12, loop=True, anchor=(16, 40),
        desc='Sentenca: marca dourada sobre a cabeca do alvo (espada em circulo).')
def _(rng):
    def f(c, t, i):
        p = .8 + .2 * math.sin(TAU * t)
        y = 18 + math.sin(TAU * t) * 1.5
        c.ring('sagrado', 16, y, 9, .45, 1.3 * p)
        c.line('sagrado', 16, y - 13, 16, y + 13, .55, 1.6 * p, w1=.2)
        c.line('sagrado', 11, y - 6, 21, y - 6, .5, 1.5 * p)
        c.blob('sagrado', 16, y, 5, .5 * p)
        c.line('sagrado', 16, y + 16, 16, 40, .3, 0, w1=.8, a1=.8 * p)
    return f


@effect('anjo_trombeta_juizo', 'anjo', (192, 208), 26, fps=16, anchor=(96, 176),
        desc='Trombeta do Juizo (suprema): halo gigante no ceu, lancas de luz caem e o circulo do juizo protege os aliados.')
def _(rng):
    sp = [(rng.uniform(-70, 70), rng.uniform(-22, 22), rng.uniform(.25, .7)) for _ in range(10)]
    def f(c, t, i):
        gx, gy = 96, 176
        on = smooth(min(t / .2, 1)) * (1 - smooth(max(t - .78, 0) / .22))
        # halo no ceu
        hy = 40
        c.ring('sagrado', gx, hy, 34 * ease_out(min(t / .3, 1)), 1.6, 1.4 * on, sy=.3,
               jag=lambda th: 1 + .06 * np.sign(np.sin(th * 12)))
        c.ring('sagrado', gx, hy, 26 * ease_out(min(t / .3, 1)), .6, 1.1 * on, sy=.3)
        c.blob('sagrado', gx, hy, 30, .25 * on, sy=.3)
        # cortina de luz do halo ao chao
        c.line('sagrado', gx, hy, gx, gy, 14 * on, .22 * on, w1=40 * on, a1=.12 * on)
        for k in range(-3, 4):
            c.line('sagrado', gx + k * 5, hy + 4, gx + k * 13, gy - 6, .4, .5 * on, a1=.1 * on)
        # circulo do juizo
        rune_circle(c, 'sagrado', gx, gy, 80 * ease_out(min(t / .3, 1)), t * 2, on, sy=.4, n=16, seed=50)
        star(c, 'sagrado', gx, gy, 66 * ease_out(min(t / .3, 1)), 8, .9 * on, sy=.4, rot=t, skip=3)
        # lancas de luz
        for x, y, d in sp:
            u = (t - d) / .22
            if 0 < u < 1.6:
                yy = gy + y - 150 * (1 - min(u, 1))
                if u < 1:
                    c.line('sagrado', gx + x, yy - 30, gx + x, yy, .3, .2, w1=1.6, a1=1.7)
                else:
                    v = u - 1
                    c.ring('sagrado', gx + x, gy + y, 4 + 14 * v / .6, 1, 1.4 * (1 - v / .6), sy=.45)
                    c.blob('sagrado', gx + x, gy + y - 4, 6 * (1 - v / .6), 1.4 * (1 - v / .6))
        motes(c, 'sagrado', gx, gy, t, 30, 70, 150, 51)
    return f


# ======================================================================
# CULTISTA - magia de sangue (rubro), cinzas e carne
# ======================================================================

@effect('cult_sangria_projetil', 'cultista', (40, 20), 6, fps=16, loop=True, anchor=(32, 10),
        desc='Sangria: orbe de sangue em voo com rastro (aponta para a direita).')
def _(rng):
    def f(c, t, i):
        ph = TAU * t
        c.line('rubro', 4, 10, 32, 10, .3, .1, w1=3, a1=.9)
        for k in range(5):
            x = 30 - k * 5 - 3 * t * 5 % 5
            c.blob('sangue', x, 10 + math.sin(ph + k) * 2, 1.2 - k * .18, 1.5, hard=True)
        c.blob('rubro', 32, 10, 5 + .6 * math.sin(ph * 2), 1.0)
        c.blob('sangue', 32, 10, 3, 1.6, hard=True)
        c.blob('rubro', 31, 9, 1.4, 1.6)
    return f


@effect('cult_sangria_impacto', 'cultista', (56, 56), 10, fps=18,
        desc='Sangria: orbe estoura em respingos e deixa o alvo sangrando (usar status_sangramento).')
def _(rng):
    d = [(rng.uniform(0, TAU), rng.uniform(40, 90), rng.uniform(.7, 1.4)) for _ in range(18)]
    def f(c, t, i):
        c.blob('rubro', 28, 28, 14 * (1 - t) ** 1.5, 1.5 * (1 - t) ** 2)
        c.ring('rubro', 28, 28, 4 + 18 * ease_out(t), 1.2 * (1 - t), 1.2 * (1 - t), sy=.8)
        for a, v, s in d:
            x, y = ballistic((28, 28), (math.cos(a) * v, math.sin(a) * v * .7 - 20), t * .7, g=200, k=2)
            c.blob('sangue', x, y, s, 1.5 * (1 - t ** 3), hard=True)
    return f


@effect('cult_pacto_rubro', 'cultista', (80, 120), 18, fps=14, anchor=(40, 110), char='cultista',
        desc='Pacto Rubro: o cultista sangra para cima, um anel de sangue o envolve e os olhos acendem.')
def _(rng):
    dr = [(rng.uniform(-14, 14), rng.uniform(0, .5), rng.uniform(.7, 1.2)) for _ in range(16)]
    def f(c, t, i):
        gx, gy = 40, 110
        on = bell(t, 0, 1)
        for k in range(3):
            y = gy - 10 - 34 * k - 6 * math.sin(t * 6 + k)
            c.ring('rubro', gx, y, 18 - k * 3, .6, 1.2 * on, sy=.35, ang=(t * 8 + k, t * 8 + k + 4.4))
        for x, d, s in dr:
            u = (t - d) / (1 - d)
            if 0 < u < 1:
                y = gy - 4 - 90 * ease_in(u, 1.4) * s
                c.line('sangue', gx + x, y + 4, gx + x, y, 1, 1.5 * (1 - u), w1=.5, hard=True)
                c.blob('rubro', gx + x, y, .7, 1.4 * (1 - u))
        c.blob('rubro', gx, gy - 2, 18 * on, .9 * on, sy=.35)
        c.blob('sangue', gx, gy, 12 * min(t * 3, 1), 1.4 * on, sy=.35, op='max')
    return f


@effect('cult_servo_de_carne', 'cultista', (112, 112), 20, fps=14, anchor=(56, 84),
        desc='Servo de Carne: pentagrama de sangue no chao e pedacos de carne brotam (o zumbi surge em seguida).')
def _(rng):
    ch = [(rng.uniform(0, TAU), rng.uniform(30, 70), rng.uniform(1, 2.2)) for _ in range(14)]
    def f(c, t, i):
        cx, cy = 56, 84
        draw = min(t / .35, 1)
        on = 1 - smooth(max(t - .75, 0) / .25)
        c.ring('rubro', cx, cy, 34, .7, 1.3 * on, sy=.45, ang=(0, TAU * draw + .01))
        if draw > .3:
            star(c, 'rubro', cx, cy, 32, 5, 1.2 * on * (draw - .3) / .7, sy=.45, rot=-math.pi / 2)
        c.blob('rubro', cx, cy, 30 * on, .4 * on, sy=.45)
        e = (t - .4) / .6
        if e > 0:
            c.line('rubro', cx, cy, cx, cy - 70, 12 * (1 - e), .7 * (1 - e), w1=2, a1=0)
            for a, v, s in ch:
                x, y = ballistic((cx, cy - 4), (math.cos(a) * v * .6, -abs(math.sin(a)) * v - 20), e * .8, g=240, k=1)
                y = min(y, cy + 6)
                c.blob('carne', x, y, s, 1.5, hard=True)
                c.blob('sangue', x, y + .6, s * .6, 1.4, hard=True)
            c.blob('sangue', cx, cy, 14 * ease_out(e), 1.5, sy=.4, op='max')
    return f


@effect('cult_chuva_cinzas', 'cultista', (144, 112), 16, fps=12, loop=True, anchor=(72, 80),
        desc='Chuva de Cinzas: area amaldicoada, cinzas e brasas vermelhas caem num circulo escuro (repetir enquanto dura).')
def _(rng):
    ash = [(rng.uniform(-60, 60), rng.uniform(-24, 24), rng.uniform(0, 1), rng.uniform(.5, 1.2)) for _ in range(60)]
    def f(c, t, i):
        cx, cy = 72, 80
        c.blob('sombra', cx, cy, 52, 1.0, sy=.45)
        c.ring('rubro', cx, cy, 60, .9, 1.0 + .2 * math.sin(TAU * t), sy=.42)
        rune_circle(c, 'rubro', cx, cy, 52, t * TAU / 8, .7, sy=.42, n=12, seed=70, rings=False)
        for x, y, ph, s in ash:
            u = (t + ph) % 1
            yy = cy + y * .9 - 70 * (1 - u)
            xx = cx + x + 8 * u
            if (x / 60) ** 2 + (y / 24) ** 2 > 1: continue
            if s > 1.05:
                c.blob('rubro', xx, yy, .6, 1.6 * bell(u, 0, 1))
            else:
                c.blob('cinza', xx, yy, s * .8, 1.3 * bell(u, 0, .95), hard=True)
    return f


@effect('cult_profecia_sombria', 'cultista', (32, 44), 16, fps=12, loop=True, anchor=(16, 40),
        desc='Profecia Sombria: olho rubro num triangulo invertido sobre o alvo marcado.')
def _(rng):
    def f(c, t, i):
        p = .8 + .2 * math.sin(TAU * t)
        y = 16 + math.sin(TAU * t) * 1.2
        pts = [(5, y - 7), (27, y - 7), (16, y + 11), (5, y - 7)]
        c.poly('rubro', pts, .5, 1.4 * p)
        c.blob('rubro', 16, y - 1, 4, .7 * p, sy=.55)
        c.ring('rubro', 16, y - 1, 3.4, .4, 1.4 * p, sy=.55)
        c.blob('rubro', 16, y - 1, 1.2, 1.8 * p)
        c.line('sangue', 16, y + 11, 16, y + 14 + 3 * ((t * 2) % 1), .6, 1.4, hard=True)
    return f


@effect('cult_setimo_selo', 'cultista', (208, 176), 30, fps=15, anchor=(104, 128),
        desc='Setimo Selo (suprema): sete selos acendem um a um no grande circulo e o ritual explode em sangue e fogo rubro.')
def _(rng):
    def f(c, t, i):
        cx, cy = 104, 128
        ch = min(t / .7, 1)            # canalizacao
        on = 1 - smooth(max(t - .85, 0) / .15)
        R = 84
        c.blob('sombra', cx, cy, R, 1.0 * on, sy=.42)
        c.ring('rubro', cx, cy, R, 1, 1.2 * on, sy=.42)
        star(c, 'rubro', cx, cy, R * .92, 7, .9 * on, sy=.42, rot=-math.pi / 2, skip=3)
        for k in range(7):
            th = -math.pi / 2 + TAU * k / 7
            x, y = cx + math.cos(th) * R, cy + math.sin(th) * R * .42
            lit = smooth((ch * 7 - k) * 2)
            c.ring('rubro', x, y, 7, .6, (.4 + lit) * on, sy=.5)
            rune(c, 'rubro', x, y - 1, 2, 90 + k, 1.6 * lit * on)
            if lit > 0:
                c.line('rubro', x, y, x, y - 30 * lit, 2 * lit, .9 * lit * on, w1=.3, a1=0)
        # pulso de canalizacao
        c.blob('rubro', cx, cy, 20 * ch, .7 * ch * on, sy=.42)
        # explosao final
        e = min((t - .7) / .3, 1)
        if e > 0:
            c.line('rubro', cx, cy, cx, 0, 16 * (1 - e) + 2, .6 * (1 - e), w1=4 * (1 - e), a1=.1)
            c.ring('rubro', cx, cy, 20 + 80 * ease_out(e), 3 * (1 - e), 1.5 * (1 - e), sy=.42)
            c.blob('rubro', cx, cy - 16, 26 * (1 - e) ** .5, .7 * (1 - e), sy=.8)
            for k in range(10):
                q = k / 9
                c.blob('rubro', cx + math.sin(q * 9 + i) * 3, cy - 10 - q * 110 * ease_out(min(e * 2, 1)), (12 - q * 8) * (1 - e), 1.2 * (1 - e), sy=1.4)
            burst(c, 'sangue', cx, cy - 10, e, 30, 120, 77, a=1.6, g=200, s=1.2, up=60)
    return f


# ======================================================================
# MUTANTE - verde acido, gosma, carne
# ======================================================================

@effect('mut_golpe_purulento', 'mutante', (88, 72), 12, fps=18,
        desc='Golpe Purulento: pancada pesada que espirra gosma acida (envenena).')
def _(rng):
    g = [(rng.uniform(-3, 0), rng.uniform(40, 110), rng.uniform(.8, 1.8)) for _ in range(20)]
    def f(c, t, i):
        cx, cy = 44, 40
        c.blob('acido', cx, cy, 14 * (1 - t) ** 2 + 1, 1.6 * (1 - t) ** 2)
        c.ring('acido', cx, cy + 8, 6 + 28 * ease_out(t), 1.8 * (1 - t), 1.2 * (1 - t), sy=.45)
        for a, v, s in g:
            x, y = ballistic((cx, cy), (math.cos(a) * v, math.sin(a) * v), t * .8, g=300, k=1.5)
            if y > cy + 20:
                c.blob('praga', x, cy + 20, s * 1.4, 1.5, sy=.4, hard=True)
                c.blob('acido', x, cy + 20, s, .6, sy=.4)
            else:
                c.blob('praga', x, y, s, 1.5, hard=True)
                c.blob('acido', x - .3, y - .3, s * .5, 1.5)
    return f


@effect('mut_carapaca', 'mutante', (80, 112), 12, fps=10, loop=True, anchor=(40, 104), char='mutante',
        desc='Carapaca: placas de quitina acida brilham em volta do corpo (buff, repetir).')
def _(rng):
    pl = [(rng.uniform(0, TAU), rng.uniform(20, 80), rng.uniform(0, 1)) for _ in range(16)]
    def f(c, t, i):
        gx, gy = 40, 104
        c.ring('acido', gx, gy - 46, 30, .6, .35 + .15 * math.sin(TAU * t), sy=1.6)
        for th, h, ph in pl:
            a = th + TAU * t / 3
            x = gx + math.cos(a) * 24
            y = gy - h + math.sin(a) * 6
            front = math.sin(a) > -.2
            lit = (.5 + .5 * math.sin(TAU * (t + ph))) * (1 if front else .4)
            # placa hexagonal
            pts = [(x + math.cos(k * TAU / 6) * 3.2 * abs(math.sin(a) * .5 + .5), y + math.sin(k * TAU / 6) * 3.2) for k in range(7)]
            c.poly('acido', pts, .35, 1.4 * lit)
        c.blob('acido', gx, gy, 18, .4, sy=.35)
    return f


@effect('mut_rugido_praga', 'mutante', (176, 112), 14, fps=16, anchor=(88, 72),
        desc='Rugido da Praga: ondas de choque acidas e poeira (provoca inimigos em volta).')
def _(rng):
    sp = [(rng.uniform(-2.6, -.5), rng.uniform(50, 100)) for _ in range(14)]
    def f(c, t, i):
        cx, cy = 88, 72
        for k, d in enumerate((0, .15, .3)):
            u = (t - d) / .7
            if 0 < u < 1:
                c.ring('acido', cx, cy, 10 + 72 * ease_out(u), 2.2 * (1 - u) + .4, 1.4 * (1 - u), sy=.5,
                       jag=lambda th: 1 + .05 * np.sin(th * 9))
                c.ring('poeira', cx, cy - 2, 8 + 66 * ease_out(u), 3 * (1 - u) + .5, 1.2 * (1 - u), sy=.5)
        c.blob('acido', cx, cy - 26, 10 * (1 - t), 1.4 * (1 - t))
        for a, v in sp:
            x, y = ballistic((cx, cy - 26), (math.cos(a) * v, math.sin(a) * v), t * .6, g=200, k=2)
            c.blob('praga', x, y, 1, 1.5 * (1 - t ** 2), hard=True)
    return f


@effect('mut_regeneracao', 'mutante', (64, 104), 16, fps=12, loop=True, anchor=(32, 98), char='mutante',
        desc='Regeneracao Profana: pustulas verdes pulsam e sobem em bolhas (cura passiva).')
def _(rng):
    def f(c, t, i):
        motes(c, 'acido', 32, 96, t, 14, 14, 80, 33, s=.7, loop=True)
        for k in range(6):
            u = (t + k / 6) % 1
            c.ring('acido', 32 + math.sin(k * 2.3) * 12, 90 - 70 * u, 1.2 + u, .35, 1.2 * bell(u, 0, 1))
        c.blob('acido', 32, 96, 14, .35 + .1 * math.sin(TAU * t), sy=.35)
    return f


@effect('mut_investida', 'mutante', (144, 72), 12, fps=18, anchor=(120, 56),
        desc='Investida Bestial: linhas de velocidade, poeira e impacto que derruba (indo para a direita).')
def _(rng):
    ln = [(rng.uniform(26, 52), rng.uniform(0, .3), rng.uniform(20, 60)) for _ in range(9)]
    def f(c, t, i):
        head = 20 + 100 * ease_in(min(t / .5, 1), 1.5)
        for y, d, L in ln:
            k = bell(t, d, d + .6)
            if k > 0:
                c.line('acido', head - L - 12, y, head - 8, y, .2, 0, w1=.7, a1=1.2 * k)
        for k in range(8):
            x = 20 + k * 13
            if x < head:
                u = (head - x) / 100
                c.blob('poeira', x, 58 - 6 * u, 3 + 6 * u, 1.4 * (1 - u) * (1 - t * .5), sy=.6, op='max')
        e = (t - .5) / .5
        if e > 0:
            c.blob('acido', 124, 44, 12 * (1 - e), 1.6 * (1 - e))
            c.ring('acido', 124, 56, 4 + 18 * ease_out(e), 1.5 * (1 - e), 1.3 * (1 - e), sy=.45)
            burst(c, 'faisca', 124, 44, e, 10, 60, 41)
    return f


@effect('mut_forma_besta', 'mutante', (176, 208), 24, fps=15, anchor=(88, 180),
        desc='Forma da Besta (suprema): casulo de gosma acida explode e a mutacao toma o corpo.')
def _(rng):
    pu = [(rng.uniform(0, TAU), rng.uniform(0, 70), rng.uniform(1.5, 3)) for _ in range(22)]
    gl = [(rng.uniform(-3.1, 0), rng.uniform(60, 150), rng.uniform(1, 2.4)) for _ in range(26)]
    def f(c, t, i):
        gx, gy = 88, 180
        grow = ease_in(min(t / .55, 1), 1.5)
        on = 1 - smooth(max(t - .55, 0) / .45)
        # casulo pulsante
        R = 18 + 26 * grow + 3 * math.sin(t * 40) * grow
        c.blob('praga', gx, gy - 50, R * .8, .9 * on, sy=1.5)
        for k in range(9):
            th = TAU * k / 9 + t
            c.line('acido', gx, gy - 50 - R * 1.2, gx + math.cos(th) * R * .9, gy - 50 + math.sin(th) * R * 1.2, .35, .9 * on * grow)
        c.ring('acido', gx, gy - 50, R, 1.2, 1.4 * on, sy=1.5)
        for a, h, s in pu:
            x = gx + math.cos(a) * R * .8
            y = gy - 50 + math.sin(a) * R * 1.3 * .8
            c.blob('acido', x, y, s * grow, 1.4 * on * (.6 + .4 * math.sin(t * 30 + a)))
        c.blob('acido', gx, gy, 40 * grow, .35 * on, sy=.35)
        e = min((t - .55) / .45, 1)
        if e > 0:
            c.blob('acido', gx, gy - 50, 28 * (1 - e) ** .6, .9 * (1 - e) ** 1.5, sy=1.2)
            c.blob('acido', gx, gy - 50, 8 * (1 - e), 2 * (1 - e))
            c.ring('acido', gx, gy, 20 + 70 * ease_out(e), 3 * (1 - e), 1.4 * (1 - e), sy=.4)
            for a, v, s in gl:
                x, y = ballistic((gx, gy - 50), (math.cos(a) * v, math.sin(a) * v), e * .9, g=260, k=1.2)
                if y > gy:
                    c.blob('praga', x, gy + (x - gx) * .05, s * 1.6, 1.5, sy=.35, hard=True)
                else:
                    c.blob('praga', x, y, s, 1.5, hard=True)
                    c.blob('acido', x, y, s * .5, 1.4 * (1 - e))
    return f


# ======================================================================
# DEMONIO - brasa, abismo, enxofre
# ======================================================================

@effect('dem_garra_abismo', 'demonio', (88, 80), 10, fps=20,
        desc='Garra do Abismo: tres cortes paralelos de brasa (repetir rapido no combo).')
def _(rng):
    def f(c, t, i):
        for k in range(3):
            tt = t * 1.25 - k * .08
            if not 0 < tt < 1: continue
            o = (k - 1) * 9
            crescent(c, 'abismo', 44 + o * .5, 40 + o, 26, -2.3, .4, tt, width=2.2, sy=.6, edge='brasa', edge_a=1.6)
        k = bell(t, .2, .9)
        burst(c, 'brasa', 58, 50, max(t - .2, 0) / .8, 10, 50, 13)
        c.blob('brasa', 58, 50, 6 * k, 1.2 * k)
    return f


@effect('dem_corrente_danacao', 'demonio', (176, 32), 12, fps=20, anchor=(8, 16),
        desc='Corrente de Danacao: corrente em brasa dispara, prende o alvo e puxa (para a direita, ate 160px).')
def _(rng):
    def f(c, t, i):
        # vai ate t=.4, segura, volta ate o fim
        if t < .4: L = 160 * ease_out(t / .4, 2)
        elif t < .55: L = 160
        else: L = 160 * (1 - ease_in((t - .55) / .45, 2))
        n = int(L / 6)
        for k in range(n):
            x = 10 + k * 6 + 3
            sag = math.sin(k / max(n, 1) * math.pi) * (4 if t > .55 else 1)
            y = 16 + sag
            if k % 2:
                c.ring('latao', x, y, 2.4, .5, 1.6, sy=.6)
            else:
                c.line('latao', x - 2.4, y, x + 2.4, y, .7, 1.6, hard=True)
            c.blob('brasa', x, y, 1.1, .8)
        hx = 10 + L
        c.line('latao', hx, 16, hx + 6, 12, .9, 1.6, hard=True)
        c.line('latao', hx, 16, hx + 6, 20, .9, 1.6, hard=True)
        c.blob('brasa', hx + 3, 16, 3, 1.3)
        if .35 < t < .7:
            k = bell(t, .35, .7)
            c.blob('brasa', 170, 16, 7 * k, 1.5 * k)
    return f


@effect('dem_pele_enxofre', 'demonio', (80, 120), 16, fps=14, loop=True, anchor=(40, 112), char='demonio',
        desc='Pele de Enxofre: chamas baixas e fumaca de enxofre envolvem o demonio (buff, repetir).')
def _(rng):
    tg = [(rng.uniform(-16, 16), rng.uniform(0, 1), rng.uniform(.6, 1.2), rng.uniform(10, 90)) for _ in range(18)]
    def f(c, t, i):
        gx, gy = 40, 112
        for x, ph, s, h in tg:
            u = (t * 2 + ph) % 1
            y = gy - h * .9 - 14 * u
            xx = gx + x * (1 - h / 140)
            c.flame('fogo', xx, y + 8, 2.2 * s, 12 * s * bell(u, 0, 1) + 2, ph=t * 2 + ph, a=.8)
        for k in range(5):
            u = (t + k / 5) % 1
            c.blob('fumaca', gx + math.sin(k * 3.1) * 14, gy - 30 - 60 * u, 4 + 6 * u, 1.0 * bell(u, 0, 1), op='max')
        c.ring('brasa', gx, gy, 18, .6, .8 + .3 * math.sin(TAU * t), sy=.35)
    return f


@effect('dem_passo_sombrio', 'demonio', (80, 112), 12, fps=18, anchor=(40, 104),
        desc='Passo Sombrio: explosao de sombra com olhos em brasa (tocar na saida; ao contrario na chegada).')
def _(rng):
    wisps = [(rng.uniform(0, TAU), rng.uniform(25, 60), rng.uniform(3, 6)) for _ in range(28)]
    def f(c, t, i):
        gx, gy = 40, 104
        k = bell(t, 0, .6)
        c.blob('sombra', gx, gy - 44, 10 * k + 3 * (1 - t), 1.1 * (1 - t) ** .7, sy=2.4)
        for a, v, s in wisps:
            x, y = ballistic((gx, gy - 44), (math.cos(a) * v, math.sin(a) * v * 1.4 - 10), t * .8, k=2.5)
            c.blob('fumaca', x, y, s * (1 - t * .6), 1.3 * (1 - t), op='max')
            c.blob('abismo', x, y, .7, 1.2 * (1 - t) ** 2)
        e = bell(t, .05, .6)
        c.blob('abismo', gx - 3, gy - 78, 1, 2 * e)
        c.blob('abismo', gx + 3, gy - 78, 1, 2 * e)
        c.ring('abismo', gx, gy, 6 + 22 * ease_out(t), 1.2 * (1 - t), 1.4 * (1 - t), sy=.4)
    return f


@effect('dem_banquete', 'demonio', (112, 112), 16, fps=16, anchor=(56, 100), char='demonio',
        desc='Banquete: fios de alma rubra sao sugados para o demonio (roubo de vida).')
def _(rng):
    st = [(rng.uniform(0, TAU), rng.uniform(40, 54), rng.uniform(0, .4)) for _ in range(14)]
    def f(c, t, i):
        gx, gy = 56, 70
        for a, R, d in st:
            u = (t - d) / .6
            if 0 < u < 1:
                r = R * (1 - ease_in(u, 2))
                th = a + u * 2
                x, y = gx + math.cos(th) * r, gy + math.sin(th) * r * .7
                px, py = gx + math.cos(th - .25) * (r + 6), gy + math.sin(th - .25) * (r + 6) * .7
                c.line('abismo', px, py, x, y, .3, .4, w1=1.2, a1=1.6)
        k = bell(t, .3, 1)
        c.blob('abismo', gx, gy, 12 * k, 1.1 * k)
        c.blob('brasa', gx, gy, 4 * k, 1.5 * k)
    return f


@effect('dem_portao_inferno', 'demonio', (208, 176), 28, fps=15, anchor=(104, 120),
        desc='Portao do Inferno (suprema): o chao racha, a fenda se abre e colunas de fogo queimam tudo em volta.')
def _(rng):
    cracks = []
    for k in range(9):
        a = TAU * k / 9 + rng.uniform(-.2, .2)
        cracks.append(lightning(rng, 0, 0, math.cos(a) * rng.uniform(60, 92), math.sin(a) * rng.uniform(60, 92), .25, 4))
    cols = [(rng.uniform(-75, 75), rng.uniform(-28, 28), rng.uniform(.35, .75)) for _ in range(9)]
    def f(c, t, i):
        cx, cy = 104, 120
        on = 1 - smooth(max(t - .8, 0) / .2)
        g = ease_out(min(t / .35, 1))
        for p in cracks:
            n = max(2, int(len(p) * g))
            pts = [(cx + x, cy + y * .42) for x, y in p[:n]]
            c.poly('fogo', pts, 1.4, 1.0 * on, w1=.4, a1=.6 * on)
            c.poly('fogo', pts, .5, 1.6 * on, w1=.2, a1=1 * on)
        # fenda central
        o = smooth((t - .2) / .3)
        c.blob('sombra', cx, cy, 34 * o, 1.6 * on, sy=.4, hard=True)
        c.ring('fogo', cx, cy, 34 * o, 2, 1.5 * on, sy=.4, jag=lambda th: 1 + .12 * np.sin(th * 7) * np.sin(th * 3))
        c.blob('fogo', cx, cy - 10, 26 * o, .3 * on, sy=.6)
        for x, y, d in cols:
            u = (t - d) / .3
            if 0 < u < 1:
                h = 90 * ease_out(min(u * 2, 1)) * (1 - u ** 3)
                bx, by = cx + x, cy + y * .9
                c.flame('fogo', bx, by, 7 * (1 - u * .4), h, ph=t * 3 + x, a=1.0 * (1 - u * .5))
                c.flame('fogo', bx + 4, by, 4, h * .6, ph=t * 3 + x + .4, a=.9 * (1 - u * .5), lean=.3)
                c.flame('fogo', bx - 4, by, 4, h * .5, ph=t * 3 + x + .7, a=.9 * (1 - u * .5), lean=-.3)
                c.ring('fogo', bx, by, 6 + 8 * u, 1, 1.3 * (1 - u), sy=.45)
        motes(c, 'brasa', cx, cy, t, 40, 90, 140, 61, s=.6)
    return f


# ======================================================================
# HUMANO - polvora, prata, agua benta
# ======================================================================

@effect('hum_tiro_certeiro', 'humano', (176, 40), 9, fps=20, anchor=(8, 20),
        desc='Tiro Certeiro: clarao forte, tracante longo e impacto com faiscas (para a direita).')
def _(rng):
    def f(c, t, i):
        y = 20
        k = (1 - t) ** 1.5
        c.blob('fogo', 16, y, 10 * k, 1.5 * k, sy=.5)
        c.line('fogo', 6, y, 34, y, 3 * k, 1.4 * k, w1=.3)
        c.blob('faisca', 8, y, 3 * k, 2 * k)
        L = 168 * ease_out(min(t / .2, 1))
        tail = 10 + 160 * ease_in(min(t / .6, 1), 1.2)
        if L > tail:
            c.line('faisca', tail, y, L, y, .2, .3, w1=1, a1=1.8)
            c.line('fogo', tail, y, L, y, .3, .1, w1=1.8, a1=.9)
        e = (t - .2) / .8
        if e > 0:
            c.blob('faisca', 168, y, 5 * (1 - e) ** 2, 2 * (1 - e) ** 2)
            burst(c, 'faisca', 168, y, e * .7, 12, 70, 21, g=200, s=.5)
        if t > .2:
            c.blob('fumaca', 18 + 14 * t, y - 4 * t, 4 + 6 * t, 1.0 * (1 - t), op='max')
    return f


@effect('hum_rajada', 'humano', (144, 96), 9, fps=20, anchor=(8, 48),
        desc='Rajada: leque de chumbo em cone com clarao largo (para a direita).')
def _(rng):
    pel = [(rng.uniform(-.5, .5), rng.uniform(.75, 1)) for _ in range(14)]
    def f(c, t, i):
        k = (1 - t) ** 1.5
        c.blob('fogo', 18, 48, 12 * k, 1.6 * k, sy=.7)
        for s in (-1, 0, 1):
            c.line('fogo', 6, 48, 34, 48 + s * 12, 3 * k, 1.3 * k, w1=.3)
        for a, s in pel:
            d = 130 * s * ease_out(min(t / .35, 1))
            tl = 130 * s * ease_in(min(t / .7, 1))
            x0, y0 = 8 + math.cos(a) * tl, 48 + math.sin(a) * tl
            x1, y1 = 8 + math.cos(a) * d, 48 + math.sin(a) * d
            if d > tl: c.line('faisca', x0, y0, x1, y1, .2, .3, w1=.6, a1=1.6 * (1 - t ** 2))
        if t > .25:
            c.blob('fumaca', 26 + 20 * t, 46, 6 + 10 * t, 1.1 * (1 - t), sy=.7, op='max')
    return f


@effect('hum_armadilha_prata', 'humano', (56, 40), 16, fps=16, anchor=(28, 28), layer='chao',
        desc='Armadilha de Prata: a armadilha brilha armada e fecha com faiscas prateadas e runa benta.')
def _(rng):
    def f(c, t, i):
        cx, cy = 28, 28
        snap = t > .55
        o = 1 if not snap else max(0, 1 - (t - .55) / .1)
        c.ring('aco', cx, cy, 10, 1, 1.5, sy=.5)
        for k in range(10):
            th = TAU * k / 10
            x, y = cx + math.cos(th) * 10, cy + math.sin(th) * 5
            tipy = y - 6 * o - (2 if not snap else 0)
            c.line('aco', x, y, x + math.cos(th) * -2 * (1 - o), tipy, .6, 1.5, w1=.2, hard=True)
        p = .5 + .5 * math.sin(t * 20)
        c.ring('alma', cx, cy, 14, .4, (.4 + .5 * p) * (1 if not snap else 0), sy=.5)
        star(c, 'alma', cx, cy, 8, 5, .7 * (1 if not snap else 0), sy=.5, rot=-math.pi / 2)
        if snap:
            e = min((t - .55) / .45, 1)
            c.blob('alma', cx, cy - 4, 10 * (1 - e) ** 2, 1.6 * (1 - e) ** 2)
            burst(c, 'faisca', cx, cy - 4, e * .6, 14, 60, 31, g=260, s=.5, up=40)
    return f


@effect('hum_agua_benta_polvora', 'humano', (72, 112), 16, fps=12, loop=True, anchor=(36, 104), char='humano',
        desc='Agua Benta e Polvora: municao carregada, gotas bentas e brasas giram em volta (buff, repetir).')
def _(rng):
    def f(c, t, i):
        gx, gy = 36, 104
        for k in range(10):
            a = TAU * (t + k / 10)
            r = 18
            x, y = gx + math.cos(a) * r, gy - 50 + math.sin(a) * 8 + math.sin(a * 2) * 6
            front = math.sin(a) > 0
            ramp = 'alma' if k % 2 else 'fogo'
            c.blob(ramp, x, y, .9 if front else .6, 1.7 if front else .9)
            c.line(ramp, x, y, gx + math.cos(a - .3) * r, gy - 50 + math.sin(a - .3) * 8 + math.sin((a - .3) * 2) * 6, .2, .2, w1=.6, a1=.9)
        c.blob('fogo', gx, gy, 14, .35, sy=.35)
    return f


@effect('hum_rolamento', 'humano', (112, 48), 10, fps=18, anchor=(88, 36), layer='chao',
        desc='Rolamento: poeira e rastro baixo da esquiva (para a direita).')
def _(rng):
    def f(c, t, i):
        head = 20 + 70 * ease_out(min(t / .5, 1))
        for k in range(10):
            x = 16 + k * 8
            if x > head: continue
            u = (head - x) / 70
            c.blob('poeira', x, 36 - 5 * u, 3 + 6 * u, 1.9 * (1 - u * .7) * (1 - t ** 2), sy=.55, op='max')
        burst(c, 'poeira', head, 34, t * .5, 8, 40, 12, a=1.4, s=1.2, up=20)
    return f


@effect('hum_ultimo_suspiro', 'humano', (128, 168), 22, fps=15, anchor=(64, 152), char='humano',
        desc='Ultimo Suspiro (suprema): o humano recusa a morte, pulso vermelho e dourado e chama de coragem nos olhos.')
def _(rng):
    def f(c, t, i):
        gx, gy = 64, 152
        # batidas
        for d in (0, .22, .44):
            u = (t - d) / .4
            if 0 < u < 1:
                c.ring('rubro', gx, gy - 50, 10 + 40 * ease_out(u), 1.6 * (1 - u), 1.3 * (1 - u), sy=1.2)
        on = smooth(min(t / .4, 1)) * (1 - smooth(max(t - .8, 0) / .2))
        c.line('sagrado', gx, gy, gx, gy - 140, 9 * on, .3 * on, w1=3 * on, a1=0)
        c.ring('sagrado', gx, gy, 24, .8, 1.2 * on, sy=.4)
        c.ring('rubro', gx, gy, 30 + 4 * math.sin(t * 20), .6, 1.0 * on, sy=.4)
        motes(c, 'fogo', gx, gy, t, 26, 22, 120, 71)
        e = bell(t, .4, 1)
        c.blob('fogo', gx - 3, gy - 92, 1.3, 2 * e)
        c.blob('fogo', gx + 3, gy - 92, 1.3, 2 * e)
    return f


# ======================================================================
# TECNOMANCER - arco eletrico azul + runas laranja
# ======================================================================

@effect('tec_arco_voltaico', 'tecnomancer', (176, 96), 10, fps=20, anchor=(10, 50),
        desc='Arco Voltaico: raio que salta entre ate 3 alvos (pontos de salto em 70,60 / 120,40 / 160,64).')
def _(rng):
    pts = [(10, 50), (70, 60), (120, 40), (160, 64)]
    bolts = [[lightning(np.random.default_rng(i * 10 + j), *pts[j], *pts[j + 1], .3, 5) for j in range(3)] for i in range(10)]
    def f(c, t, i):
        reach = min(t / .35, 1) * 3
        for j in range(3):
            if reach <= j: continue
            k = min(reach - j, 1)
            p = bolts[i][j]
            n = max(2, int(len(p) * k))
            a = (1 - ease_in(max(t - .4, 0) / .6))
            c.poly('eletrico', p[:n], 1.6, .7 * a)
            c.poly('eletrico', p[:n], .45, 1.8 * a)
            if k >= 1:
                x, y = pts[j + 1]
                c.blob('eletrico', x, y, 6 * a, 1.4 * a)
                if i % 2: c.ring('eletrico', x, y, 7, .4, 1.2 * a)
        c.blob('eletrico', 10, 50, 5 * (1 - t), 1.6 * (1 - t))
    return f


@effect('tec_nanoreparo', 'tecnomancer', (64, 104), 16, fps=12, loop=True, anchor=(32, 98), char='tecnomancer',
        desc='Nanoreparo: enxame de nanomaquinas azuis costura o alvo (cura continua, repetir).')
def _(rng):
    sw = [(rng.uniform(0, TAU), rng.uniform(6, 16), rng.uniform(10, 90), rng.choice([-1, 1])) for _ in range(26)]
    def f(c, t, i):
        gx, gy = 32, 98
        for a, r, h, s in sw:
            th = a + s * TAU * t * 2
            x, y = gx + math.cos(th) * r, gy - h + math.sin(th) * r * .3
            front = math.sin(th) > 0
            c.blob('eletrico', x, y, .5, 1.8 if front else .8)
        # linha de varredura subindo
        y = gy - 90 * ((t * 2) % 1)
        c.line('eletrico', gx - 14, y, gx + 14, y, .4, .9)
        c.blob('eletrico', gx, gy, 14, .4, sy=.35)
    return f


@effect('tec_torreta_invocacao', 'tecnomancer', (96, 80), 16, fps=16, anchor=(48, 56),
        desc='Torreta Sentinela: circulo de runas no chao e descarga eletrica onde a torreta e montada.')
def _(rng):
    def f(c, t, i):
        cx, cy = 48, 56
        on = smooth(min(t / .3, 1)) * (1 - smooth(max(t - .7, 0) / .3))
        rune_circle(c, 'runa', cx, cy, 26 * ease_out(min(t / .3, 1)), t * 3, on, sy=.45, n=8, seed=101)
        if .35 < t < .8:
            for j in range(3):
                p = lightning(np.random.default_rng(i * 7 + j), cx + (j - 1) * 12, cy - 40, cx + (j - 1) * 4, cy, .35, 4)
                c.poly('eletrico', p, .4, 1.6)
        e = (t - .45) / .55
        if e > 0:
            c.blob('eletrico', cx, cy - 6, 12 * (1 - e), 1.5 * (1 - e))
            burst(c, 'faisca', cx, cy - 6, e * .6, 12, 60, 51, g=240, s=.5, up=30)
    return f


@effect('tec_torreta_disparo', 'tecnomancer', (40, 16), 4, fps=20, anchor=(4, 8),
        desc='Disparo da torreta: pulso eletrico curto (para a direita).')
def _(rng):
    def f(c, t, i):
        k = 1 - t
        c.blob('eletrico', 6, 8, 5 * k, 1.6 * k)
        c.line('eletrico', 6, 8, 6 + 34 * min(t * 3, 1), 8, 1.2 * k, 1.6 * k, w1=.3)
    return f


@effect('tec_campo_forca', 'tecnomancer', (128, 120), 16, fps=12, loop=True, anchor=(64, 96),
        desc='Campo de Forca: cupula hexagonal azul que absorve dano (repetir enquanto dura).')
def _(rng):
    def f(c, t, i):
        cx, cy, R = 64, 96, 52
        c.ring('eletrico', cx, cy, R, 1, 1.1, sy=.42)
        # silhueta da cupula
        c.ring('eletrico', cx, cy, R, .8, .9, sy=1.6, ang=(math.pi, TAU))
        # malha hexagonal desenhada como linhas de latitude/longitude
        for k in range(1, 4):
            h = k / 4
            c.ring('eletrico', cx, cy - R * 1.6 * math.sin(h * math.pi / 2) * .98, R * math.cos(h * math.pi / 2), .35, .55, sy=.42,
                   ang=(math.pi * .02, math.pi * .98))
        for k in range(7):
            th = math.pi * (k + .5) / 7 + (t * TAU / 7)
            xs = math.cos(th)
            pts = [(cx + xs * R * math.cos(u * math.pi / 2), cy + math.sin(th) * R * .42 * math.cos(u * math.pi / 2) - R * 1.6 * math.sin(u * math.pi / 2)) for u in np.linspace(0, 1, 8)]
            if math.sin(th) > 0: c.poly('eletrico', pts, .3, .6)
        # ondulacao que percorre
        y = cy - R * 1.6 * ((t * 1.5) % 1)
        c.blob('eletrico', cx + math.sin(t * TAU) * 20, cy - R * .8, 10, .35 + .15 * math.sin(TAU * t), sy=1.2)
        c.blob('eletrico', cx, cy, R * .9, .14, sy=.42)
    return f


@effect('tec_pulso_antidivino', 'tecnomancer', (176, 112), 14, fps=16, anchor=(88, 72),
        desc='Pulso Anti-Divino: onda de runas laranja e estalos eletricos que silenciam a area.')
def _(rng):
    def f(c, t, i):
        cx, cy = 88, 72
        e = ease_out(t, 2.5)
        R = 8 + 76 * e
        a = 1 - ease_in(t, 1.3)
        c.ring('eletrico', cx, cy, R, 1.5 * (1 - t) + .4, 1.4 * a, sy=.5)
        rune_circle(c, 'runa', cx, cy, R * .85, -t * 2, a, sy=.5, n=14, seed=120, rings=False)
        for j in range(5):
            th = TAU * j / 5 + i
            p = lightning(np.random.default_rng(i * 13 + j), cx, cy - 20, cx + math.cos(th) * R, cy + math.sin(th) * R * .5, .3, 4)
            c.poly('eletrico', p, .4, 1.4 * a * (1 if (i + j) % 2 else .3))
        c.blob('eletrico', cx, cy - 20, 14 * (1 - t) ** 2, 1.6 * (1 - t) ** 2)
    return f


@effect('tec_maquina_juizo', 'tecnomancer', (192, 208), 28, fps=15, anchor=(96, 176),
        desc='Maquina do Juizo Reverso (suprema): engrenagem de runas gira no chao e uma coluna de arcos sobe da maquina.')
def _(rng):
    def f(c, t, i):
        gx, gy = 96, 176
        on = smooth(min(t / .25, 1)) * (1 - smooth(max(t - .8, 0) / .2))
        R = 80 * ease_out(min(t / .3, 1))
        # engrenagem: anel com dentes
        c.ring('runa', gx, gy, R, 1, 1.3 * on, sy=.4, jag=lambda th: 1 + .05 * (np.sin(th * 24 + t * 6) > 0))
        rune_circle(c, 'runa', gx, gy, R * .78, -t * 3, on, sy=.4, n=16, seed=140)
        star(c, 'eletrico', gx, gy, R * .55, 6, .9 * on, sy=.4, rot=t * 2, skip=2)
        # coluna de arcos
        col = bell(t, .2, .95)
        c.line('eletrico', gx, gy, gx, 10, 8 * col, .5 * col, w1=3 * col, a1=.1)
        for j in range(3):
            p = lightning(np.random.default_rng(i * 5 + j), gx + (j - 1) * 4, gy - 4, gx + (j - 1) * 6, 12, .12, 5)
            c.poly('eletrico', p, .45, 1.6 * col)
        for j in range(4):
            th = TAU * j / 4 + t * 3
            p = lightning(np.random.default_rng(i * 9 + j + 50), gx, gy - 40, gx + math.cos(th) * R, gy + math.sin(th) * R * .4, .3, 4)
            c.poly('eletrico', p, .35, 1.2 * col * (1 if (i + j) % 3 else .2))
        c.blob('eletrico', gx, gy - 40, 10 * col, 1.4 * col)
        motes(c, 'runa', gx, gy, t, 26, 70, 120, 141)
    return f


# ---------------- Humano: giro de lamina (pedido do Jefin) ----------------
def _giro(rng, parte):
    """Giro com espada larga cortando 360 graus. parte='tras' (metade de cima da elipse, desenhar
    ATRAS do personagem) ou 'frente' (metade de baixo, desenhar NA FRENTE). Mesmo tamanho e ancora."""
    sparks = [(rng.uniform(0, 1), rng.uniform(40, 90), rng.uniform(.4, .8)) for _ in range(26)]
    dust = [(rng.uniform(0, TAU), rng.uniform(.6, 1.2), rng.uniform(2, 4.5)) for _ in range(48)]
    # raio de 2 tiles (ladrilho 48x24 -> elipse 68x34 no chao); giro de 0,45 s dentro de 0,8 s de efeito
    CX, FY, R, SY, H = 88, 100, 68, .5, 42         # centro, chao, raio, achatamento, altura da cintura
    turns = 1.08
    SPIN = .45 / .8

    def head_at(t):
        return -math.pi * .6 + TAU * turns * ease_out(min(t / SPIN, 1), 1.6)

    def f(c, t, i):
        cy = FY - H
        head = head_at(t)
        start = -math.pi * .6
        L = min(head - start, math.pi * 1.5) * (1 - ease_in(max(t - SPIN, 0) / (1 - SPIN), 1.3))
        n = 70
        for k in range(n):
            u = k / (n - 1)                       # 0 cauda -> 1 ponta
            th = head - L * (1 - u)
            sn = math.sin(th)
            if (parte == 'tras') != (sn < 0):
                continue
            x, y = CX + math.cos(th) * R, cy + sn * R * SY
            w = (.5 + 4.2 * u ** 1.4) * (1 - .4 * t)
            a = u ** 1.1
            # lamina larga: faixa que vai do quadril ao alcance da espada
            xi, yi = CX + math.cos(th) * (R - w * 2.2), cy + sn * (R - w * 2.2) * SY
            c.line('faisca', xi, yi, x, y, .9, .32 * a, w1=1.2, a1=.75 * a)
            c.line('eco', xi, yi + 1, x, y + 1, 1.2, .5 * a, w1=1.6, a1=.9 * a)
            c.blob('fogo', x, y, w * .45, .3 * a)
            # fio da lamina
            th2 = th + .05
            c.line('faisca', x, y, CX + math.cos(th2) * R, cy + math.sin(th2) * R * SY, .55, 1.6 * a * (1 - t * .5))
        # ponta da espada
        if (parte == 'tras') == (math.sin(head) < 0) and t < .8:
            hx, hy = CX + math.cos(head) * R, cy + math.sin(head) * R * SY
            c.blob('faisca', hx, hy, 2.2, 1.6 * (1 - t))
        # faiscas soltas pela tangente
        for ph, v, s in sparks:
            t0 = ph * SPIN
            if t < t0: continue
            th = head_at(t0)
            sx, sy_ = CX + math.cos(th) * R, cy + math.sin(th) * R * SY
            vx, vy = -math.sin(th) * v, math.cos(th) * v * SY - 20
            age = (t - t0) * 1.4
            if age > .45: continue
            x, y = ballistic((sx, sy_), (vx, vy), age, g=240, k=2)
            back = (y < cy)
            if (parte == 'tras') != back: continue
            px, py = ballistic((sx, sy_), (vx, vy), max(age - .04, 0), g=240, k=2)
            c.line('faisca', px, py, x, y, s * .5, .5 * (1 - age / .45), w1=s, a1=1.5 * (1 - age / .45))
        # poeira de areia levantada no chao (anel que abre)
        e = ease_out(min(t / .8, 1))
        for a0, sp, r in dust:
            th = a0
            rr = 16 + 56 * e * sp
            x, y = CX + math.cos(th) * rr, FY + math.sin(th) * rr * .45 - 6 * e * sp
            back = math.sin(th) < 0
            if (parte == 'tras') != back: continue
            c.blob('areia', x, y, r * (.5 + e), 1.3 * (1 - t ** 1.3), sy=.5, op='max')
        if parte == 'tras':
            c.ring('poeira', CX, FY, 18 + 52 * e, 2.5 * (1 - t) + .5, 1.2 * (1 - t), sy=.45)
    return f


effect('hum_corte_largo_tras', 'humano', (176, 128), 16, fps=20, anchor=(88, 100), layer='chao', char='humano',
       desc='Corte Giratorio (corte_largo), camada de tras: corte 360 graus, raio de 2 tiles, giro de 0,45 s, com espada larga em volta do humano; metade de tras do arco, faiscas e poeira de areia. Desenhar ATRAS do personagem, junto com a camada da frente.')(lambda rng: _giro(rng, 'tras'))
effect('hum_corte_largo_frente', 'humano', (176, 128), 16, fps=20, anchor=(88, 100), char='humano',
       desc='Corte Giratorio (corte_largo), camada da frente: metade da frente do arco de corte, faiscas e poeira. Desenhar NA FRENTE do personagem, no mesmo ponto e no mesmo quadro da camada de tras.')(lambda rng: _giro(rng, 'frente'))


# ---------------- Humano: Arrancada (id arrancada) ----------------
def _silhueta(nome='humano'):
    import os
    from PIL import Image
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'design', 'estilo', 'fontes', f'sprite_{nome}.png')
    a = np.asarray(Image.open(p).convert('RGBA'))[..., 3].astype(np.float32) / 255
    return a


@effect('hum_arrancada', 'humano', (192, 112), 12, fps=24, anchor=(20, 96),
        desc='Arrancada (arrancada): dash de 4 tiles em 0,18 s com a espada larga estendida, cortando numa faixa de 1,2 tile e empurrando os alvos para os lados; rastro de silhueta e de lamina, impactos ao longo do caminho e areia levantada (para a direita; o personagem sai da ancora e chega 136 px adiante). Tocar junto com esquiva_poeira no ponto de saida.')
def _(rng):
    sil = _silhueta()
    sh, sw = sil.shape
    X0, FY, D = 20, 96, 136
    DASH = .18 / .5                                  # 0,18 s de dash dentro de 0,5 s de efeito
    gr = [(rng.uniform(0, 1), rng.uniform(-5, 5), rng.uniform(.6, 1.3)) for _ in range(30)]
    def pos(t):
        return X0 + D * ease_out(min(t / DASH, 1), 1.6)
    def f(c, t, i):
        px = pos(t)
        # ecos de silhueta: deixados a cada trecho do caminho, somem com o tempo
        for k in range(5):
            tk = DASH * k / 5
            if tk > t: break
            age = t - tk
            a = .42 * (1 - age / .45) * (.5 + .5 * k / 5)
            if a <= 0: continue
            x = pos(tk)
            c.stamp('eco', sil, x - sw / 2, FY - sh + 6, a)
        # rastro de lamina na altura da cintura, com o fio claro
        y = FY - 42
        tail = X0 + D * ease_in(max((t - DASH * .6) / (1 - DASH * .6), 0), 1.2)
        if px - tail > 2:
            c.line('faisca', tail, y + 2, px + 10, y - 1, .3, .15, w1=2.6, a1=.9)
            c.line('faisca', tail, y + 1, px + 12, y - 2, .2, .3, w1=.6, a1=1.7)
            c.line('fogo', tail, y + 3, px + 8, y, .2, 0, w1=1.6, a1=.5)
        # faixa de corte no chao: 1,2 tile de largura (~20 px na vertical da tela), some depois do dash
        band = 1 - ease_in(max((t - DASH) / (1 - DASH), 0), 1.2)
        reach = min(px, X0 + D)
        if reach - X0 > 2 and band > 0:
            for s in (-1, 1):
                c.line('eco', X0, FY + s * 10, reach + 6, FY + s * 10, .45, .15 * band, a1=.9 * band)
            c.line('eco', X0, FY, reach, FY, 8, .08 * band, a1=.28 * band)
        # impactos ao longo do caminho: clarao, faiscas e empurrao para os dois lados
        for k, xc in enumerate((X0 + D * .3, X0 + D * .6, X0 + D * .88)):
            tc = DASH * ((xc - X0) / D) ** .7         # quando a espada passa ali
            u = (t - tc) / .4
            if not 0 < u < 1: continue
            yc = y + 4 + (k - 1) * 3
            c.blob('faisca', xc, yc, 8 * (1 - u) ** 2 + .6, 1.9 * (1 - u) ** 2)
            c.ring('faisca', xc, yc, 3 + 9 * ease_out(u), .6 * (1 - u), .8 * (1 - u) ** 1.5, sy=.6)
            c.line('faisca', xc - 9 * (1 - u), yc, xc + 9 * (1 - u), yc, .6, 1.5 * (1 - u) ** 1.5)
            r = np.random.default_rng(300 + k)
            for _ in range(14):
                side = r.choice([-1, 1])
                vx, vy = r.uniform(10, 70), side * r.uniform(70, 150)
                bx, by = ballistic((xc, yc), (vx, vy), u * .45, g=120, k=3)
                qx, qy = ballistic((xc, yc), (vx, vy), max(u * .45 - .03, 0), g=120, k=3)
                c.line('faisca', qx, qy, bx, by, .35, .5 * (1 - u), w1=.8, a1=1.7 * (1 - u))
            # areia empurrada para os lados (os alvos sao jogados para fora da faixa)
            for s in (-1, 1):
                c.blob('areia', xc + 6 * u, FY + s * (6 + 14 * ease_out(u)), 3 + 5 * u, 1.4 * (1 - u), sy=.5, op='max')
                c.line('eco', xc, FY + s * 4, xc + 4, FY + s * (8 + 16 * ease_out(u)), .4, .2 * (1 - u), a1=1.0 * (1 - u))
        # faiscas na ponta durante o dash
        if t < DASH * 1.2:
            c.blob('faisca', px + 12, y - 2, 3, 1.4)
        # areia levantada ao longo do chao
        for ph, oy, s in gr:
            xg = X0 + D * ph
            if xg > px: continue
            tg = DASH * ph                           # quando o personagem passou ali
            age = (t - tg) / .45
            if 0 < age < 1:
                c.blob('areia', xg - 10 * age, FY + oy * .5 - 9 * age * s, (2 + 5 * age) * s, 1.6 * (1 - age), sy=.55, op='max')
    return f
