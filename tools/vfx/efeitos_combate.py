"""Efeitos de combate genericos, status, itens e progressao."""
import math
import numpy as np
from vfx import (effect, ease_out, ease_in, smooth, bell, fade, ballistic, lightning, fbm, value_noise)

TAU = 2 * math.pi


# ============================ COMBATE ============================

@effect('golpe_impacto', 'combate', (48, 48), 7, fps=20, desc='Acerto corpo a corpo comum: lampejo e estilhacos de luz.')
def _(rng):
    spikes = [(rng.uniform(0, TAU), rng.uniform(10, 20), rng.uniform(.8, 1.4)) for _ in range(7)]
    def f(c, t, i):
        cx, cy = 24, 24
        c.blob('faisca', cx, cy, 7 * (1 - t) ** 1.5 + 1, 1.3 * (1 - t) ** 2)
        c.blob('faisca', cx, cy, 3.2 * (1 - t), 2 * (1 - t))
        for a, L, w in spikes:
            r0 = 2 + 10 * ease_out(t); r1 = r0 + L * (1 - t) ** .7
            c.line('faisca', cx + math.cos(a) * r0, cy + math.sin(a) * r0 * .8,
                   cx + math.cos(a) * r1, cy + math.sin(a) * r1 * .8, w * (1 - t) + .3, 1.4 * (1 - t), w1=.2, a1=.2)
        c.ring('faisca', cx, cy, 4 + 14 * ease_out(t), 1.4 * (1 - t) + .3, .9 * (1 - t) ** 2, sy=.8)
    return f


@effect('golpe_corte', 'combate', (80, 64), 7, fps=20, desc='Rastro de lamina em arco (corte de espada/foice/machado).')
def _(rng):
    def f(c, t, i):
        cx, cy, r = 40, 34, 27
        a0, a1 = -3.0, .55                       # varre de tras-cima para frente-baixo
        rev = ease_out(min(t / .4, 1), 3)        # ponta avanca
        cut = ease_in(max((t - .2) / .8, 0), 1.6)  # cauda some
        head = a0 + (a1 - a0) * rev
        tail = a0 + (a1 - a0) * cut
        if head - tail < .04: return
        n = 40
        for k in range(n):
            u = k / (n - 1)
            th = tail + (head - tail) * u
            g = (th - a0) / (a1 - a0)            # posicao no arco completo
            w = 3.6 * math.sin(math.pi * min(max(g, 0), 1)) ** .8 * (1 - .5 * t) + .4
            rr = r - w * .6
            x, y = cx + math.cos(th) * rr, cy + math.sin(th) * rr * .55
            fadeu = u ** .8
            c.blob('faisca', x, y, w * .9, .55 * fadeu)
            c.line('faisca', cx + math.cos(th) * (r - .3), cy + math.sin(th) * (r - .3) * .55,
                   cx + math.cos(th + .08) * (r - .3), cy + math.sin(th + .08) * (r - .3) * .55, .55, 1.5 * fadeu * (1 - t * .6))
        c.blob('faisca', cx + math.cos(head) * r, cy + math.sin(head) * r * .55, 2, 1.4 * (1 - t))
    return f


@effect('golpe_critico', 'combate', (96, 96), 10, fps=18, desc='Acerto critico: X de luz, onda de choque e brasas.')
def _(rng):
    embers = [(rng.uniform(0, TAU), rng.uniform(30, 70), rng.uniform(.5, 1.1)) for _ in range(18)]
    def f(c, t, i):
        cx, cy = 48, 48
        k = ease_out(min(t / .3, 1))
        L = 30 * k
        for a in (math.radians(-35), math.radians(35)):
            dx, dy = math.cos(a) * L, math.sin(a) * L
            w = 3.2 * (1 - t) ** 1.3
            c.line('brasa', cx - dx, cy - dy, cx + dx, cy + dy, w * 1.8, 1.0 * (1 - t))
            c.line('faisca', cx - dx, cy - dy, cx + dx, cy + dy, w * .7, 1.6 * (1 - t) ** 1.2)
        c.blob('faisca', cx, cy, 10 * (1 - t) ** 2 + 1, 2 * (1 - t) ** 2)
        c.blob('brasa', cx, cy, 16 * (1 - t), .9 * (1 - t))
        c.ring('brasa', cx, cy, 6 + 34 * ease_out(t), 2.2 * (1 - t) + .4, 1.2 * (1 - t) ** 1.5, sy=.6)
        c.ring('faisca', cx, cy, 6 + 34 * ease_out(t), .8, 1.0 * (1 - t) ** 2, sy=.6)
        for a, v, s in embers:
            x, y = ballistic((cx, cy), (math.cos(a) * v, math.sin(a) * v - 30), t * .9, g=80, k=2.5)
            c.blob('brasa', x, y, s, 1.6 * (1 - t))
    return f


@effect('sangue_jorro', 'combate', (64, 64), 12, fps=20, anchor=(24, 34),
        desc='Jorro de sangue ao ferir; gotas caem e mancham o chao. Espelhar para o outro lado.')
def _(rng):
    drops = []
    for _ in range(26):
        a = rng.normal(-.55, .55); v = rng.uniform(40, 110)
        drops.append((a, v, rng.uniform(.6, 1.6), rng.uniform(0, .12)))
    def f(c, t, i):
        cx, cy, ground = 24, 34, 56
        T = t * .9
        # nevoa vermelha inicial
        c.blob('sangue', cx + 6 * ease_out(t), cy - 2, 6 * bell(t, 0, .35), .9 * bell(t, 0, .35), sy=.7)
        for a, v, s, d in drops:
            tt = max(T - d, 0)
            if tt <= 0: continue
            v0 = (math.cos(a) * v, math.sin(a) * v - 25)
            x, y = ballistic((cx, cy), v0, tt, g=260, k=1.2)
            if y >= ground:  # gota no chao vira mancha
                # tempo de impacto aproximado -> mancha achatada
                c.blob('sangue', x, ground + (x - cx) * .05, s * 1.6, 1.4, sy=.45, hard=True)
                continue
            px, py = ballistic((cx, cy), v0, max(tt - .035, 0), g=260, k=1.2)
            c.line('sangue', px, py, x, y, s * .7, 1.3, w1=s, hard=True)
    return f


@effect('sangue_poca', 'combate', (56, 28), 10, fps=12, layer='chao', anchor=(28, 14),
        desc='Poca de sangue que se espalha sob o corpo (manter o ultimo quadro).')
def _(rng):
    blobs = [(rng.normal(0, 7), rng.normal(0, 3), rng.uniform(3, 7), rng.uniform(0, .5)) for _ in range(9)]
    def f(c, t, i):
        for x, y, r, d in blobs:
            k = ease_out(max(t - d * .6, 0) / (1 - d * .6), 3)
            c.blob('sangue', 28 + x * (.6 + .6 * k), 14 + y * (.6 + .5 * k), r * (.3 + .9 * k), 1.6, sy=.5, op='max')
        c.blob('sangue', 28, 14, 7 + 7 * ease_out(t, 3), 1.3, sy=.45, op='max')
    return f


@effect('faiscas_bloqueio', 'combate', (56, 48), 9, fps=20, desc='Metal contra metal: bloqueio, aparar, acerto em armadura.')
def _(rng):
    sparks = [(rng.uniform(-2.9, -.2), rng.uniform(60, 150), rng.uniform(.4, .8)) for _ in range(16)]
    def f(c, t, i):
        cx, cy = 28, 22
        c.blob('faisca', cx, cy, 5 * (1 - t) ** 3 + .5, 2 * (1 - t) ** 3)
        c.line('faisca', cx - 9 * (1 - t), cy, cx + 9 * (1 - t), cy, .6, 1.5 * (1 - t) ** 2)
        c.line('faisca', cx, cy - 6 * (1 - t), cx, cy + 6 * (1 - t), .5, 1.2 * (1 - t) ** 2)
        for a, v, s in sparks:
            T = t * .55
            x, y = ballistic((cx, cy), (math.cos(a) * v, math.sin(a) * v), T, g=420, k=1.5)
            px, py = ballistic((cx, cy), (math.cos(a) * v, math.sin(a) * v), max(T - .04, 0), g=420, k=1.5)
            life = 1 - t ** 1.5
            c.line('faisca', px, py, x, y, s * .6, .6 * life, w1=s, a1=1.6 * life)
    return f


@effect('disparo_cano', 'combate', (48, 32), 5, fps=24, anchor=(6, 16),
        desc='Clarao de boca de arma (escopeta/mosquete). Aponta para a direita; girar no motor.')
def _(rng):
    def f(c, t, i):
        x0, y = 6, 16
        L = [26, 34, 24, 14, 6][i]; k = [1.2, 1.4, 1, .6, .25][i]
        c.blob('fogo', x0 + L * .35, y, L * .35, 1.4 * k, sy=.45)
        c.line('fogo', x0, y, x0 + L, y, 4 * k, 1.3 * k, w1=.3)
        for s in (-1, 1):
            c.line('fogo', x0 + 2, y, x0 + L * .55, y + s * L * .3, 2 * k, 1.1 * k, w1=.3)
        c.blob('faisca', x0 + 3, y, 3 * k, 2 * k)
        if i >= 2:
            c.blob('fumaca', x0 + 10 + i * 3, y - i, 4 + i * 1.5, .9, sy=.8)
    return f


@effect('fumaca_tiro', 'combate', (40, 40), 12, fps=14, anchor=(10, 30),
        desc='Fumaca de polvora que sobe apos o disparo.')
def _(rng):
    puffs = [(rng.uniform(0, 8), rng.uniform(-3, 3), rng.uniform(3, 5), rng.uniform(0, .25)) for _ in range(7)]
    def f(c, t, i):
        for x, y, r, d in puffs:
            u = max(t - d, 0) / (1 - d)
            if u <= 0: continue
            c.blob('fumaca', 10 + x + 10 * ease_out(u), 30 + y - 22 * u, r * (.6 + 1.2 * u), 1.4 * (1 - u ** 1.6), op='max')
        c.mul('fumaca', 1)
    return f


@effect('projetil_bala', 'combate', (32, 8), 2, fps=20, loop=True, anchor=(28, 4),
        desc='Tracante de bala/virote em voo (aponta para a direita).')
def _(rng):
    def f(c, t, i):
        c.line('faisca', 4, 4, 29, 4, .5, .15, w1=1.1, a1=1.5)
        c.line('fogo', 10 + i * 2, 4, 30, 4, .6, .2, w1=1.5, a1=1.0)
        c.blob('faisca', 29, 4, 1.4, 1.6)
    return f


@effect('impacto_bala', 'combate', (40, 40), 8, fps=20, desc='Bala acertando: poeira, lascas e faiscas.')
def _(rng):
    chips = [(rng.uniform(-3, -.1), rng.uniform(40, 100)) for _ in range(9)]
    def f(c, t, i):
        cx, cy = 20, 24
        c.blob('faisca', cx, cy, 3 * (1 - t) ** 3 + .3, 2 * (1 - t) ** 3)
        for a, v in chips:
            x, y = ballistic((cx, cy), (math.cos(a) * v, math.sin(a) * v), t * .5, g=300, k=2)
            c.blob('pedra', x, y, .9, 1.5 * (1 - t ** 3), hard=True)
            c.blob('faisca', x, y, .6, 1.2 * (1 - t) ** 2)
        c.blob('poeira', cx, cy - 6 * t, 4 + 8 * ease_out(t), 1.3 * (1 - t) ** 1.3, sy=.8)
    return f


@effect('esquiva_poeira', 'combate', (56, 28), 10, fps=16, layer='chao', anchor=(28, 18),
        desc='Poeira levantada ao rolar, esquivar ou pisar forte.')
def _(rng):
    puffs = [(rng.uniform(-1, 1), rng.uniform(.4, 1)) for _ in range(10)]
    def f(c, t, i):
        for d, s in puffs:
            x = 28 + d * 20 * ease_out(t)
            y = 20 - 8 * ease_out(t) * s
            c.blob('poeira', x, y, (2 + 5 * s) * (.4 + ease_out(t)), 1.5 * (1 - t) ** 1.2, sy=.7, op='max')
    return f


@effect('morte_monstro', 'combate', (96, 112), 18, fps=14, anchor=(48, 100),
        desc='Morte de monstro: o corpo se desfaz em cinza e brasa, a alma sobe e se apaga. Tocar junto com o sprite do monstro sumindo.')
def _(rng):
    # particulas nascem dentro do volume do corpo (elipse ~18x44)
    ash = []
    for _ in range(70):
        h0 = rng.uniform(4, 48); x0 = rng.normal(0, 6 * (1 - h0 / 70))
        ash.append((x0, h0, rng.uniform(.5, 1.2), rng.normal(6, 8), rng.uniform(.25, .7), h0 / 48 * .35))
    emb = [(rng.normal(0, 7), rng.uniform(4, 44), rng.uniform(.4, .8), rng.uniform(0, .45)) for _ in range(26)]
    def f(c, t, i):
        gx, gy = 48, 100
        # contorno queimando (de cima para baixo), so no comeco
        burn = 1 - ease_in(t / .45, 1) if t < .45 else 0
        lvl = 48 * (1 - t / .45) if t < .45 else 0
        if burn > 0:
            for k in range(10):
                x = gx + (k - 4.5) * 2.2 + math.sin(k * 3 + i) * 1.2
                c.blob('brasa', x, gy - 4 - lvl + math.sin(k * 1.7 + i * 2) * 2, 1.6, 1.2 * burn)
        for x0, h0, s, drift, life, d in ash:
            d2 = (1 - h0 / 48) * .4               # de cima para baixo
            u = (t - d2) / life
            if u <= 0 or u >= 1: continue
            x = gx + x0 + drift * u * 1.4 + math.sin(u * 5 + x0) * 2.5
            y = gy - 4 - h0 - 34 * ease_in(u, 1.3)
            c.blob('cinza', x, y, s, 1.4 * (1 - u ** 2), hard=True)
            if u < .25: c.blob('brasa', x, y, s * .9, 1.4 * (1 - u / .25))
        for x0, h0, s, d in emb:
            u = (t - d) / .55
            if 0 < u < 1:
                c.blob('brasa', gx + x0 + math.sin(u * 7 + x0) * 4, gy - 6 - h0 - 30 * u, s, 1.7 * (1 - u))
        # alma subindo
        a = bell(t, .25, 1)
        sy_ = gy - 34 - 50 * ease_out(max(t - .25, 0) / .75)
        if a > 0:
            c.blob('alma', 48, sy_, 3.2, 1.3 * a, sy=1.3)
            for k in range(7):
                c.blob('alma', 48 + math.sin(t * 10 + k * .9) * (1 + k * .4), sy_ + 3 + k * 2.6, 2.6 - k * .3, .9 * a * (1 - k / 7))
        # sangue escuro no chao
        c.blob('sangue', gx, gy, 6 + 9 * ease_out(t, 3), 1.4 * min(t * 5, 1), sy=.4, op='max')
    return f


# ============================ STATUS (loops sobre o alvo) ============================

@effect('status_veneno', 'status', (40, 56), 16, fps=12, loop=True, anchor=(20, 50),
        desc='Envenenado: bolhas acidas sobem pelo corpo.')
def _(rng):
    b = [(rng.uniform(-10, 10), rng.uniform(0, 1), rng.uniform(.8, 1.8)) for _ in range(12)]
    def f(c, t, i):
        for x, ph, s in b:
            u = (t + ph) % 1
            y = 50 - 44 * u
            r = s * (.5 + u)
            c.ring('acido', 20 + x + math.sin(u * 8 + x) * 1.5, y, r, .45, 1.3 * bell(u, 0, 1))
            c.blob('acido', 20 + x + math.sin(u * 8 + x) * 1.5 - r * .4, y - r * .4, .5, 1.2 * bell(u, 0, 1))
    return f


@effect('status_sangramento', 'status', (40, 56), 16, fps=12, loop=True, anchor=(20, 50),
        desc='Sangrando: gotas escorrem e pingam do alvo.')
def _(rng):
    d = [(rng.uniform(-9, 9), rng.uniform(10, 34), rng.uniform(0, 1)) for _ in range(6)]
    def f(c, t, i):
        for x, y0, ph in d:
            u = (t + ph) % 1
            if u < .45:
                L = 6 * u / .45
                c.line('sangue', 20 + x, 50 - y0, 20 + x, 50 - y0 + L, .7, 1.4, w1=1.1, hard=True)
            else:
                v = (u - .45) / .55
                y = 50 - y0 + 6 + v * v * (y0 - 4)
                c.blob('sangue', 20 + x, y, 1, 1.6, sy=1.4, hard=True)
                if v > .85: c.blob('sangue', 20 + x, 50, 2.2, 1.6, sy=.4, hard=True)
    return f


@effect('status_queimando', 'status', (48, 80), 16, fps=14, loop=True, anchor=(24, 72),
        desc='Em chamas: linguas de fogo lambendo o corpo e fagulhas subindo.')
def _(rng):
    tg = [(rng.uniform(-10, 10), rng.uniform(0, 1), rng.uniform(.7, 1.1), rng.uniform(0, 40)) for _ in range(9)]
    sp = [(rng.uniform(-10, 10), rng.uniform(0, 1)) for _ in range(10)]
    def f(c, t, i):
        for x, ph, s, h0 in tg:
            u = (t * 2 + ph) % 1
            hh = (16 + 18 * s) * (.7 + .3 * math.sin(TAU * (t * 2 + ph)))
            c.flame('fogo', 24 + x * (1 - h0 / 80), 70 - h0, 3.4 * s, hh, ph=t * 2 + ph, a=.95, lean=math.sin(TAU * (t + ph)) * .25)
        for x, ph in sp:
            u = (t + ph) % 1
            c.blob('fogo', 24 + x + math.sin(u * 10) * 3, 66 - 70 * u, .5, 1.8 * (1 - u))
    return f


@effect('status_atordoado', 'status', (40, 20), 12, fps=12, loop=True, anchor=(20, 18),
        desc='Atordoado: aneis de faiscas girando acima da cabeca.')
def _(rng):
    def f(c, t, i):
        c.ring('faisca', 20, 10, 12, .3, .35, sy=.35)
        for k in range(4):
            a = TAU * (t + k / 4)
            x, y = 20 + math.cos(a) * 12, 10 + math.sin(a) * 4
            s = 1 + .5 * (math.sin(a) + 1) / 2
            c.line('faisca', x - 2 * s, y, x + 2 * s, y, .45, 1.6)
            c.line('faisca', x, y - 2 * s, x, y + 2 * s, .45, 1.6)
            c.blob('faisca', x, y, .8 * s, 1)
    return f


@effect('status_lentidao', 'status', (48, 24), 16, fps=10, loop=True, layer='chao', anchor=(24, 12),
        desc='Lento/preso: correntes fantasmas giram no chao em volta dos pes.')
def _(rng):
    def f(c, t, i):
        for k in range(14):
            a = TAU * (k / 14 - t / 3)
            x, y = 24 + math.cos(a) * 17, 12 + math.sin(a) * 7.5
            c.ring('alma', x, y, 1.6, .35, 1.1, sy=.6 if k % 2 else 1.2)
    return f


# ============================ ITENS ============================

for nome, rampa, rot in (('item_brilho_excelente', 'acido', 'Item excelente (verde acido)'),
                         ('item_brilho_raro', 'sagrado', 'Item raro (ouro)'),
                         ('item_brilho_lendario', 'rubro', 'Item lendario (vermelho)'),
                         ('item_brilho_tecnico', 'eletrico', 'Item de set/tecnologia (azul eletrico)')):
    def mk(rampa=rampa):
        def setup(rng):
            gl = [(rng.uniform(-9, 9), rng.uniform(0, 1), rng.uniform(.6, 1)) for _ in range(7)]
            def f(c, t, i):
                p = .75 + .25 * math.sin(TAU * t)
                c.blob(rampa, 20, 30, 10, .55 * p, sy=.4)
                c.ring(rampa, 20, 30, 9 + p, .5, .7 * p, sy=.42)
                for x, ph, s in gl:
                    u = (t + ph) % 1
                    y = 30 - 26 * u
                    a = bell(u, 0, 1) * 1.6
                    c.line(rampa, 20 + x, y - 1.6 * s, 20 + x, y + 1.6 * s, .35, a)
                    c.line(rampa, 20 + x - 1.2 * s, y, 20 + x + 1.2 * s, y, .3, a * .8)
            return f
        return setup
    effect(nome, 'itens', (40, 40), 12, fps=10, loop=True, anchor=(20, 30),
           desc=f'{rot} no chao: poca de luz e cintilas subindo. Estilo MU.')(mk())


for nome, rampa, rot in (('item_feixe_raro', 'sagrado', 'ouro'), ('item_feixe_lendario', 'rubro', 'vermelho')):
    def mk(rampa=rampa):
        def setup(rng):
            m = [(rng.uniform(-3, 3), rng.uniform(0, 1)) for _ in range(6)]
            def f(c, t, i):
                p = .8 + .2 * math.sin(TAU * t)
                c.line(rampa, 12, 2, 12, 90, .8, .1, w1=3.2, a1=.9 * p)
                c.line(rampa, 12, 30, 12, 90, .3, .2, w1=1, a1=1.6)
                c.blob(rampa, 12, 90, 7, .9 * p, sy=.4)
                for x, ph in m:
                    u = (t + ph) % 1
                    c.blob(rampa, 12 + x, 90 - 80 * u, .5, 1.6 * bell(u, 0, 1))
            return f
        return setup
    effect(nome, 'itens', (24, 96), 12, fps=10, loop=True, anchor=(12, 90),
           desc=f'Feixe de luz ({rot}) que marca um drop valioso de longe.')(mk())


@effect('bau_abertura', 'itens', (96, 96), 18, fps=16, anchor=(48, 70),
        desc='Bau abrindo: frestas de luz, explosao dourada, moedas e po saindo.')
def _(rng):
    rays = [(rng.uniform(-2.6, -.5), rng.uniform(.7, 1.2)) for _ in range(9)]
    coins = [(rng.uniform(-2.5, -.6), rng.uniform(60, 110), rng.uniform(0, TAU)) for _ in range(12)]
    motes = [(rng.uniform(-14, 14), rng.uniform(0, .4), rng.uniform(.5, 1)) for _ in range(16)]
    def f(c, t, i):
        cx, cy = 48, 66
        # 1) frestas antes de abrir
        crack = bell(t, 0, .3)
        c.line('sagrado', cx - 12, cy, cx + 12, cy, .6, 1.4 * crack)
        c.blob('sagrado', cx, cy, 10 * crack, .5 * crack, sy=.3)
        # 2) estouro
        b = max(t - .2, 0) / .8
        if b > 0:
            for a, s in rays:
                L = 50 * s * ease_out(min(b / .3, 1)) * (1 - b ** 2)
                c.line('sagrado', cx, cy - 2, cx + math.cos(a) * L, cy - 2 + math.sin(a) * L, 3 * s * (1 - b), .9 * (1 - b), w1=.3, a1=.1)
            c.blob('sagrado', cx, cy - 4, 9 * (1 - b) ** 1.5 + 2, 1.5 * (1 - b) ** 1.5, sy=.7)
            c.ring('sagrado', cx, cy, 6 + 34 * ease_out(b), 1.6 * (1 - b), 1.1 * (1 - b) ** 1.4, sy=.45)
            for a, v, ph in coins:
                x, y = ballistic((cx, cy - 4), (math.cos(a) * v * .6, math.sin(a) * v), b * .9, g=230, k=.8)
                y = min(y, cy + 12)
                spin = abs(math.cos(ph + b * 20))
                c.blob('latao', x, y, 1.6, 1.6 * (1 - b ** 4), sy=max(spin, .35), hard=True)
                c.blob('sagrado', x, y - .5, .6, 1.4 * (1 - b) * spin)
            for x, d, s in motes:
                u = max(b - d, 0) / (1 - d)
                if u > 0:
                    c.blob('sagrado', cx + x + math.sin(u * 6 + x) * 3, cy - 6 - 50 * u * s, .5, 1.8 * bell(u, 0, 1))
    return f


# ============================ PROGRESSAO ============================

@effect('level_up', 'progresso', (128, 192), 24, fps=16, anchor=(64, 168),
        desc='Subida de nivel: circulo de runas no chao, coluna de luz dourada e cinzas brilhantes subindo.')
def _(rng):
    sp = [(rng.uniform(0, TAU), rng.uniform(8, 26), rng.uniform(0, .5), rng.uniform(.6, 1.3)) for _ in range(34)]
    def f(c, t, i):
        gx, gy = 64, 168
        on = smooth(min(t / .25, 1)) * (1 - smooth(max(t - .7, 0) / .3))
        # circulo de runas no chao
        R = 30 * ease_out(min(t / .3, 1))
        c.ring('sagrado', gx, gy, R, .8, 1.2 * on, sy=.5)
        c.ring('sagrado', gx, gy, R * .78, .45, .9 * on, sy=.5)
        for k in range(12):
            a = TAU * k / 12 + t * 1.5
            x, y = gx + math.cos(a) * R * .89, gy + math.sin(a) * R * .89 * .5
            c.line('sagrado', x - 1.2, y - 1.5, x + 1.2, y + 1.5, .35, 1.4 * on)
            c.line('sagrado', x - 1.2, y + 1.5, x + 1.2, y - 1.5, .35, 1.1 * on)
        # coluna de luz
        col = bell(t, .12, .8)
        c.line('sagrado', gx, gy, gx, gy - 160, 14 * col, .5 * col, w1=6 * col, a1=.12)
        c.line('sagrado', gx, gy, gx, gy - 160, 6 * col, .7 * col, w1=2 * col, a1=.2)
        c.line('sagrado', gx, gy, gx, gy - 150 * min(t / .35, 1), 2.5 * col, 1.6 * col, w1=.6, a1=.3)
        c.blob('sagrado', gx, gy - 4, 20 * col, .8 * col, sy=.45)
        # anel que sobe
        for k, d in enumerate((.15, .3, .45)):
            u = (t - d) / .5
            if 0 < u < 1:
                c.ring('sagrado', gx, gy - 130 * ease_out(u), 22 * (1 - u * .5), .7, 1.3 * (1 - u), sy=.35)
        # particulas
        for a, r, d, s in sp:
            u = (t - d) / (1 - d)
            if 0 < u < 1:
                x = gx + math.cos(a + u * 3) * r * (1 - u * .4)
                y = gy + math.sin(a + u * 3) * r * .4 - 140 * ease_in(u, 1.4)
                c.blob('sagrado', x, y, .55 * s, 1.8 * (1 - u))
    return f


@effect('cura_generica', 'progresso', (56, 96), 16, fps=14, anchor=(28, 88),
        desc='Cura recebida (pocao, Nanoreparo, Toque de Graca neutro): cruzes de luz subindo.')
def _(rng):
    m = [(rng.uniform(-12, 12), rng.uniform(0, .5), rng.uniform(.8, 1.3)) for _ in range(9)]
    def f(c, t, i):
        c.blob('sagrado', 28, 86, 14 * bell(t, 0, 1), .6 * bell(t, 0, 1), sy=.4)
        for x, d, s in m:
            u = (t - d) / (1 - d)
            if 0 < u < 1:
                y = 84 - 70 * ease_out(u)
                a = 1.6 * bell(u, 0, 1)
                c.line('sagrado', 28 + x, y - 2.2 * s, 28 + x, y + 2.2 * s, .5, a)
                c.line('sagrado', 28 + x - 1.5 * s, y - .7 * s, 28 + x + 1.5 * s, y - .7 * s, .5, a)
    return f
