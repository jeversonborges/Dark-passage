"""Efeitos de chefe (masmorra com 3 chefes) e auras de classe/facção."""
import math
import numpy as np
from vfx import (effect, ease_out, ease_in, smooth, bell, ballistic, lightning)
from efeitos_classes import rune_circle, star, burst, motes, rune, feather

TAU = 2 * math.pi


# ============================ CHEFES ============================

@effect('chefe_aviso_area', 'chefes', (128, 72), 24, fps=16, layer='chao', anchor=(64, 36),
        desc='Aviso de golpe em area: o circulo vermelho enche do centro para a borda; o golpe cai no ultimo quadro. Esticar a duracao no motor.')
def _(rng):
    def f(c, t, i):
        cx, cy, R = 64, 36, 58
        p = .75 + .25 * math.sin(t * TAU * 4)
        c.ring('aviso', cx, cy, R, .8, 1.4 * p, sy=.5)
        c.ring('aviso', cx, cy, R - 3, .35, .7 * p, sy=.5)
        c.disc('aviso', cx, cy, R * ease_in(t, 1.2), .32, sy=.5, edge=3)
        c.ring('aviso', cx, cy, R * ease_in(t, 1.2), .8, 1.2, sy=.5)
        for k in range(8):
            th = TAU * k / 8
            x, y = cx + math.cos(th) * (R - 6), cy + math.sin(th) * (R - 6) * .5
            c.line('aviso', x, y, cx + math.cos(th) * (R - 12), cy + math.sin(th) * (R - 12) * .5, .45, 1.2 * p)
    return f


@effect('chefe_aviso_cone', 'chefes', (144, 112), 24, fps=16, layer='chao', anchor=(8, 56),
        desc='Aviso de golpe em cone (bafo, varredura). Aponta para a direita; girar no motor.')
def _(rng):
    def f(c, t, i):
        ox, oy, R, half = 8, 56, 132, .5
        p = .75 + .25 * math.sin(t * TAU * 4)
        for s in (-1, 1):
            c.line('aviso', ox, oy, ox + math.cos(s * half) * R, oy + math.sin(s * half) * R * .7, .7, 1.4 * p)
        c.ring('aviso', ox, oy, R, .8, 1.4 * p, sy=.7, ang=(-half, half))
        fill = R * ease_in(t, 1.2)
        for k in range(14):
            a = -half + 2 * half * k / 13
            c.line('aviso', ox, oy, ox + math.cos(a) * fill, oy + math.sin(a) * fill * .7, 3.2, .22)
        c.ring('aviso', ox, oy, fill, .8, 1.2, sy=.7, ang=(-half, half))
    return f


@effect('chefe_aviso_linha', 'chefes', (176, 32), 20, fps=16, layer='chao', anchor=(8, 16),
        desc='Aviso de investida/raio em linha reta (para a direita).')
def _(rng):
    def f(c, t, i):
        p = .75 + .25 * math.sin(t * TAU * 4)
        for y in (6, 26):
            c.line('aviso', 8, y, 170, y, .6, 1.4 * p)
        L = 8 + 162 * ease_in(t, 1.2)
        c.line('aviso', 8, 16, L, 16, 8, .26, hard=True)
        for k in range(6):
            x = 30 + k * 26 + (t * 26 * 3) % 26
            if x < 168:
                c.line('aviso', x - 5, 10, x, 16, .45, 1.2 * p); c.line('aviso', x - 5, 22, x, 16, .45, 1.2 * p)
    return f


@effect('chefe_onda_choque', 'chefes', (208, 128), 16, fps=16, anchor=(104, 84),
        desc='Pisao do chefe: chao racha, anel de poeira e pedras voando.')
def _(rng):
    cracks = []
    for k in range(7):
        a = TAU * k / 7 + rng.uniform(-.3, .3)
        cracks.append(lightning(rng, 0, 0, math.cos(a) * rng.uniform(40, 70), math.sin(a) * rng.uniform(40, 70), .25, 4))
    rocks = [(rng.uniform(-3, -.1), rng.uniform(60, 140), rng.uniform(1.2, 2.6)) for _ in range(18)]
    def f(c, t, i):
        cx, cy = 104, 84
        g = ease_out(min(t / .2, 1)); on = 1 - smooth(max(t - .6, 0) / .4)
        for p in cracks:
            n = max(2, int(len(p) * g))
            pts = [(cx + x, cy + y * .45) for x, y in p[:n]]
            c.poly('pedra', pts, 1.1, 1.6 * on, hard=True)
            c.poly('brasa', pts, .35, .9 * on * (1 - t))
        c.blob('faisca', cx, cy - 4, 14 * (1 - t) ** 3, 1.6 * (1 - t) ** 3, sy=.5)
        for d in (0, .12):
            u = (t - d) / .8
            if 0 < u < 1:
                c.ring('poeira', cx, cy - 3, 10 + 86 * ease_out(u), 5 * (1 - u) + 1, 1.8 * (1 - u), sy=.45)
                c.ring('faisca', cx, cy, 10 + 86 * ease_out(u), .6, .9 * (1 - u) ** 2, sy=.45)
        for a, v, s in rocks:
            x, y = ballistic((cx, cy - 2), (math.cos(a) * v * .8, math.sin(a) * v), t * .9, g=320, k=.8)
            if y < cy + 20:
                c.blob('pedra', x, y, s, 1.6, hard=True)
    return f


@effect('chefe_meteoro', 'chefes', (128, 224), 18, fps=18, anchor=(64, 196),
        desc='Meteoro/bola de fogo do chefe caindo do ceu e explodindo no chao (usar com chefe_aviso_area).')
def _(rng):
    def f(c, t, i):
        gx, gy = 64, 196
        fall = min(t / .4, 1)
        if fall < 1:
            x = gx + 40 * (1 - fall); y = gy - 190 * (1 - ease_in(fall, 2))
            c.line('fogo', x + 26, y - 70, x, y, .5, .2, w1=6, a1=1.0)
            c.line('fumaca', x + 34, y - 90, x + 4, y - 10, 2, .6, w1=6, a1=1.2)
            c.blob('fogo', x, y, 8, 1.4)
            c.blob('pedra', x, y, 3.5, 1.6, hard=True)
            burst(c, 'brasa', x, y, .3, 6, 20, i)
        e = (t - .4) / .6
        if e > 0:
            k = 1 - e
            c.blob('faisca', gx, gy - 8, 16 * k ** 3, 1.6 * k ** 3)
            for j in range(7):
                ang = -math.pi / 2 + (j - 3) * .35
                h = 70 * ease_out(min(e * 3, 1)) * k
                c.flame('fogo', gx + (j - 3) * 7, gy, 7 - abs(j - 3), h * (1 - abs(j - 3) * .2), ph=t * 4 + j, a=1.0 * k ** .5, lean=(j - 3) * .1)
            c.ring('fogo', gx, gy, 8 + 50 * ease_out(e), 2.5 * k, 1.4 * k, sy=.45)
            for k2 in range(6):
                u = e
                c.blob('fumaca', gx + (k2 - 2.5) * 10, gy - 20 - 70 * u - k2 * 4, 8 + 10 * u, 1.3 * (1 - u ** 1.5), op='max')
            burst(c, 'pedra', gx, gy - 4, e * .8, 14, 120, 81, a=1.6, g=300, s=1.6, up=60)
            c.blob('sombra', gx, gy, 26 * min(e * 4, 1), 1.0, sy=.4, op='max')
    return f


@effect('chefe_portal', 'chefes', (112, 144), 16, fps=12, loop=True, anchor=(56, 132),
        desc='Fenda de invocacao do chefe: portal vertical do abismo de onde saem os servos (repetir enquanto aberto).')
def _(rng):
    sw = [(rng.uniform(0, TAU), rng.uniform(.3, 1), rng.uniform(0, 1)) for _ in range(30)]
    def f(c, t, i):
        cx, cy, rx, ry = 56, 72, 26, 56
        c.blob('sombra', cx, cy, rx * .95, 1.6, sy=ry / rx, hard=True)
        c.ring('abismo', cx, cy, rx, 1.6, 1.4, sy=ry / rx, jag=lambda th: 1 + .08 * np.sin(th * 7 + t * TAU) * np.sin(th * 3))
        c.ring('abismo', cx, cy, rx * .78, .7, .9, sy=ry / rx, jag=lambda th: 1 + .1 * np.sin(th * 5 - t * TAU * 2))
        for a, r, ph in sw:
            u = (t + ph) % 1
            th = a + u * 5
            rr = r * (1 - u) * rx
            c.blob('abismo', cx + math.cos(th) * rr, cy + math.sin(th) * rr * ry / rx, .7, 1.5 * bell(u, 0, 1))
        c.blob('abismo', cx, cy, 6 + math.sin(t * TAU) * 1.5, .9)
        c.blob('abismo', cx, 132, 30, .5, sy=.35)
        motes(c, 'abismo', cx, 132, t, 10, 30, 120, 9, loop=True)
    return f


@effect('chefe_furia', 'chefes', (128, 168), 16, fps=14, loop=True, anchor=(64, 156),
        desc='Furia do chefe (fase 2): chamas vermelhas sobem do corpo e o chao arde (repetir).')
def _(rng):
    tg = [(rng.uniform(-30, 30), rng.uniform(0, 1), rng.uniform(.7, 1.2)) for _ in range(14)]
    def f(c, t, i):
        gx, gy = 64, 156
        for x, ph, s in tg:
            h = (40 + 50 * s) * (.6 + .4 * math.sin(TAU * (t + ph)))
            c.flame('rubro', gx + x, gy - 4 - abs(x) * .3, 5 * s, h, ph=t + ph, a=.75)
        c.ring('rubro', gx, gy, 40 + 2 * math.sin(TAU * t * 2), 1, 1.3, sy=.4)
        c.blob('rubro', gx, gy, 36, .5, sy=.4)
        motes(c, 'brasa', gx, gy, t, 22, 34, 150, 3, loop=True)
    return f


@effect('chefe_raio_ceu', 'chefes', (80, 224), 10, fps=20, anchor=(40, 210),
        desc='Raio que cai do ceu no ponto marcado (usar com chefe_aviso_area pequeno).')
def _(rng):
    def f(c, t, i):
        gx, gy = 40, 210
        k = 1 - ease_in(t, 1.5)
        if i < 6:
            for j in range(2):
                p = lightning(np.random.default_rng(i * 3 + j), gx + (j - .5) * 18, 0, gx, gy, .18, 6)
                c.poly('eletrico', p, 2.2 * k, .6 * k)
                c.poly('eletrico', p, .6, 1.8 * k)
        c.blob('eletrico', gx, gy - 4, 16 * k, 1.5 * k, sy=.6)
        c.ring('eletrico', gx, gy, 6 + 30 * ease_out(t), 1.4 * k, 1.3 * k, sy=.45)
        burst(c, 'faisca', gx, gy - 4, t * .7, 12, 80, 5, g=300, s=.5, up=50)
        c.blob('sombra', gx, gy, 14 * min(t * 3, 1), 1.0, sy=.4, op='max')
    return f


@effect('chefe_escudo', 'chefes', (128, 160), 16, fps=12, loop=True, anchor=(64, 146),
        desc='Fase invulneravel: casca de runas do abismo gira em volta do chefe (repetir).')
def _(rng):
    def f(c, t, i):
        gx, gy = 64, 146
        for k in range(3):
            y = gy - 20 - k * 40
            rr = 44 - abs(k - 1) * 8
            rune_circle(c, 'abismo', gx, y, rr, t * TAU * (1 if k % 2 else -1) / 3, .9, sy=.35, n=12, seed=200 + k * 20)
        c.ring('abismo', gx, gy - 60, 50, .8, .55 + .2 * math.sin(TAU * t), sy=1.6)
        c.blob('abismo', gx, gy, 40, .4, sy=.4)
    return f


@effect('chefe_morte', 'chefes', (240, 240), 32, fps=15, anchor=(120, 200),
        desc='Morte de chefe: clarao, onda de choque, coluna de fogo e fumaca, detritos e a alma enorme subindo.')
def _(rng):
    deb = [(rng.uniform(-3.1, 0), rng.uniform(80, 200), rng.uniform(1.4, 3), rng.choice(['pedra', 'osso', 'carne'])) for _ in range(30)]
    smk = [(rng.normal(0, 14), rng.uniform(0, .3), rng.uniform(.7, 1.3)) for _ in range(16)]
    def f(c, t, i):
        gx, gy = 120, 200
        # 1) tremores e brasas vazando (0-.3)
        pre = bell(t, 0, .35)
        for k in range(6):
            a = TAU * k / 6 + i
            c.line('brasa', gx, gy - 50, gx + math.cos(a) * 30 * pre, gy - 50 + math.sin(a) * 40 * pre, 1.2 * pre, 1.5 * pre, w1=.2)
        c.blob('brasa', gx, gy - 50, 12 * pre, 1.3 * pre)
        e = (t - .28) / .72
        if e > 0:
            k = 1 - e
            c.blob('faisca', gx, gy - 50, 40 * k ** 4, 1.6 * k ** 4)
            for d in (0, .1):
                u = (e - d) / .6
                if 0 < u < 1:
                    c.ring('fogo', gx, gy, 14 + 104 * ease_out(u), 3 * (1 - u) + .5, 1.4 * (1 - u), sy=.42)
                    c.ring('poeira', gx, gy - 2, 12 + 100 * ease_out(u), 6 * (1 - u) + 1, 1.6 * (1 - u), sy=.42)
            # coluna
            h = 170 * ease_out(min(e * 2.5, 1)) * (1 - ease_in(max(e - .4, 0) / .6))
            c.flame('fogo', gx, gy, 18 * (1 - e * .5), h, ph=t * 3, a=1.0)
            c.flame('fogo', gx - 12, gy, 9, h * .6, ph=t * 3 + .3, a=.9, lean=-.3)
            c.flame('fogo', gx + 12, gy, 9, h * .6, ph=t * 3 + .6, a=.9, lean=.3)
            for x, d, s in smk:
                u = (e - d) / (1 - d)
                if 0 < u < 1:
                    c.blob('fumaca', gx + x * (1 + u), gy - 40 - 140 * ease_out(u) * s, 10 + 14 * u, 1.4 * (1 - u ** 2), op='max')
            for a, v, s, mat in deb:
                x, y = ballistic((gx, gy - 40), (math.cos(a) * v * .8, math.sin(a) * v), e * 1.2, g=300, k=.6)
                if y < gy + 30:
                    c.blob(mat, x, y, s, 1.6, hard=True)
            # alma
            a = bell(e, .3, 1)
            sy_ = gy - 80 - 120 * ease_out(max(e - .3, 0) / .7)
            if a > 0:
                c.blob('alma', gx, sy_, 8, 1.3 * a, sy=1.3)
                for q in range(9):
                    c.blob('alma', gx + math.sin(t * 9 + q * .8) * (2 + q * .8), sy_ + 8 + q * 5, 6 - q * .55, .9 * a * (1 - q / 9))
            c.blob('sombra', gx, gy, 50 * min(e * 3, 1), 1.0, sy=.4, op='max')
            motes(c, 'brasa', gx, gy, e, 40, 90, 200, 7, s=.6)
    return f


# ============================ AURAS (equipamento/estagio 3, repetir) ============================

def _aura(name, rotulo, ramp, extra):
    @effect(name, 'auras', (80, 120), 16, fps=12, loop=True, anchor=(40, 110), char=name.split('_')[1],
            desc=f'Aura de {rotulo}: brilho de equipamento lendario / estagio 3 (repetir, desenhar atras e na frente do personagem).')
    def _(rng):
        def f(c, t, i):
            gx, gy = 40, 110
            p = .8 + .2 * math.sin(TAU * t)
            c.ring(ramp, gx, gy, 20, .7, 1.2 * p, sy=.4)
            c.blob(ramp, gx, gy, 18, .35 * p, sy=.4)
            extra(c, t, i, gx, gy)
        return f


def _anjo(c, t, i, gx, gy):
    for k in range(6):
        u = (t + k / 6) % 1
        feather(c, gx + math.sin(k * 2.1) * 18 + math.sin(u * 6) * 3, gy - 100 + 95 * u, 1 + math.sin(u * 6 + k), 3.5, bell(u, 0, 1))
    motes(c, 'sagrado', gx, gy, t, 12, 18, 100, 1, loop=True)
    c.ring('sagrado', gx, gy - 102, 7, .5, 1.2, sy=.35)


def _demonio(c, t, i, gx, gy):
    for k in range(7):
        ph = k / 7
        c.flame('brasa', gx + (k - 3) * 5, gy, 2.6, 10 + 6 * math.sin(TAU * (t + ph)), ph=t + ph, a=.8)
    motes(c, 'brasa', gx, gy, t, 16, 18, 100, 2, loop=True)


def _cultista(c, t, i, gx, gy):
    for k in range(5):
        u = (t + k / 5) % 1
        c.blob('rubro', gx + math.sin(k * 2.7 + u * 3) * 14, gy - 10 - 70 * u, 4 + 4 * u, .5 * bell(u, 0, 1))
    rune_circle(c, 'rubro', gx, gy, 20, t * TAU / 4, .8, sy=.4, n=7, seed=300, rings=False)
    for k in range(4):
        u = (t + k / 4) % 1
        c.blob('sangue', gx + (k - 1.5) * 8, gy - 60 + 55 * u * u, .9, 1.5, sy=1.4, hard=True)


def _humano(c, t, i, gx, gy):
    for k in range(8):
        a = TAU * (t + k / 8)
        x, y = gx + math.cos(a) * 18, gy - 50 + math.sin(a) * 6
        c.blob('faisca' if k % 2 else 'alma', x, y, .7, 1.6 if math.sin(a) > 0 else .7)
    motes(c, 'fogo', gx, gy, t, 8, 16, 90, 4, loop=True)


def _mutante(c, t, i, gx, gy):
    for k in range(9):
        u = (t + k / 9) % 1
        c.ring('acido', gx + math.sin(k * 2.3) * 16, gy - 4 - 90 * u, 1 + u * 1.5, .35, 1.3 * bell(u, 0, 1))
    c.blob('praga', gx, gy, 14, 1.1, sy=.35, hard=True)
    c.blob('acido', gx, gy, 10, .5, sy=.35)


def _tecno(c, t, i, gx, gy):
    for j in range(2):
        if (i + j) % 3 == 0: continue
        a = TAU * (i / 16 + j * .5)
        p = lightning(np.random.default_rng(i * 4 + j), gx + math.cos(a) * 20, gy + math.sin(a) * 8, gx + math.cos(a + 1) * 14, gy - 60 - j * 20, .3, 4)
        c.poly('eletrico', p, .35, 1.4)
    rune_circle(c, 'runa', gx, gy, 20, -t * TAU / 4, .8, sy=.4, n=8, seed=320, rings=False)


for _n, _r, _ramp, _x in (('aura_anjo', 'Anjo (ouro sagrado)', 'sagrado', _anjo),
                          ('aura_demonio', 'Demonio (brasa)', 'brasa', _demonio),
                          ('aura_cultista', 'Cultista (nevoa de sangue)', 'rubro', _cultista),
                          ('aura_humano', 'Humano (prata e polvora)', 'faisca', _humano),
                          ('aura_mutante', 'Mutante (acido)', 'acido', _mutante),
                          ('aura_tecnomancer', 'Tecnomancer (arco e runas)', 'eletrico', _tecno)):
    _aura(_n, _r, _ramp, _x)
