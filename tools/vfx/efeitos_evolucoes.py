"""Skills das evoluções de classe (nível 50, entregas/evolucoes/evolucoes.json)."""
import math
import numpy as np
from vfx import effect, ease_out, ease_in, bell, ballistic

TAU = 2 * math.pi


# ======================================================================
# CEIFADOR - sombra com olhos violeta (rampa 'espectro')
# ======================================================================

def espirito(c, x, y, ang, s, a, eyes=True):
    """Cabeça de espírito negro: crânio de fumaça, mandíbula aberta e dois olhos violeta."""
    dx, dy = math.cos(ang), math.sin(ang)
    c.blob('sombra', x, y, 4.2 * s, 1.2 * a, hard=True)
    c.blob('sombra', x - dx * 3 * s, y - dy * 3 * s + 1.5 * s, 3.4 * s, 1.0 * a, hard=True)
    c.blob('espectro', x, y, 6.5 * s, .22 * a)
    if eyes:
        px, py = -dy, dx
        for e in (-1, 1):
            c.blob('espectro', x + dx * 1.6 * s + px * 1.5 * s * e, y + dy * 1.6 * s * .6 + py * 1.5 * s * e * .6 - .8 * s,
                   .6 * s, 2.2 * a)


@effect('ceifador_espiritos_malignos', 'ceifador', (320, 208), 26, fps=16, anchor=(160, 112),
        desc='Espíritos Malignos: espíritos negros saem do Ceifador em espiral e voam para todos os lados, atravessando os inimigos.')
def _(rng):
    sp = []
    for wave, t0 in enumerate((0., .22)):
        for k in range(8):
            sp.append(dict(t0=t0 + rng.uniform(0, .05), th=TAU * (k + .5 * wave) / 8 + rng.uniform(-.12, .12),
                           spin=(1 if wave == 0 else -1) * rng.uniform(1.6, 2.2), R=rng.uniform(128, 150),
                           wob=rng.uniform(4, 8), ph=rng.uniform(0, TAU), s=rng.uniform(1.9, 2.3), dur=rng.uniform(.62, .72)))

    def pos(p, u):
        th = p['th'] + p['spin'] * u
        r = p['R'] * ease_out(u, 1.6) + p['wob'] * math.sin(u * 9 + p['ph']) * u
        return 160 + math.cos(th) * r, 112 + math.sin(th) * r * .52 - 18 * math.sin(math.pi * u) - 22 * (1 - u)

    def f(c, t, i):
        cx, cy = 160, 112
        # selo de sombra no chão
        k = bell(t, 0, .85)
        c.ring('sombra', cx, cy, 40 + 30 * ease_out(min(t / .3, 1)), 4, .9 * k, sy=.5)
        c.disc('sombra', cx, cy, 30, .55 * k, sy=.5)
        c.ring('espectro', cx, cy, 34 + 30 * ease_out(min(t / .3, 1)), .6, .7 * k, sy=.5)
        # névoa que sobe do Ceifador
        for j in range(6):
            u = (t * 1.4 + j / 6) % 1
            c.blob('fumaca', cx + math.sin(j * 2.3 + t * 5) * 10, cy - 20 - 40 * u, 6 + 8 * u, .8 * bell(u, 0, 1) * (1 - t), op='max')
        for p in sp:
            u = (t - p['t0']) / p['dur']
            if not 0 < u < 1.15: continue
            a = min(1, u * 6) * (1 - ease_in(max(u - .8, 0) / .35, 1.5))
            uu = min(u, 1)
            # rastro: fumaça que afina e se desfaz
            prev = None
            for q in range(18):
                v = uu - q * .022
                if v <= 0: break
                x, y = pos(p, v)
                w = (3.4 - q * .16) * p['s']
                c.blob('sombra', x, y, w, .85 * a * (1 - q / 18), op='max')
                if q % 3 == 1: c.blob('espectro', x, y, w * 1.5, .08 * a * (1 - q / 18))
                prev = (x, y)
            x, y = pos(p, uu); x2, y2 = pos(p, max(uu - .02, 0))
            espirito(c, x, y, math.atan2(y - y2, x - x2 + 1e-6), p['s'], a)
            if u > .97:   # ao fim do voo, se desfaz em cinza violeta
                kk = (u - .97) / .18
                for m in range(5):
                    th = m * 1.3 + p['ph']
                    c.blob('espectro', x + math.cos(th) * 8 * kk, y + math.sin(th) * 5 * kk - 6 * kk, 1.1, 1.2 * (1 - kk))
    return f


@effect('ceifador_espirito_impacto', 'ceifador', (64, 72), 10, fps=18, anchor=(32, 56),
        desc='Impacto de espírito: o espírito atravessa o alvo e arranca um fiapo de alma.')
def _(rng):
    def f(c, t, i):
        k = bell(t, 0, .6)
        c.blob('sombra', 32, 44, 12 * k, .9 * k, op='max')
        c.ring('espectro', 32, 44, 6 + 16 * ease_out(t), .7, 1.3 * (1 - t), sy=.7)
        for m in range(7):
            th = TAU * m / 7 + .4
            px, py = ballistic((32, 44), (math.cos(th) * 22, math.sin(th) * 14 - 10), t, g=0, k=2.5)
            c.blob('espectro', px, py, .9, 1.6 * (1 - t))
        u = ease_out(t)
        c.blob('sombra', 32, 44 - 30 * u, 3.5, 1.0 * (1 - t), hard=True)
        c.blob('espectro', 32, 44 - 30 * u, 5, .4 * (1 - t))
    return f


# ======================================================================
# ENGENHEIRO HEREGE - Bomba Atômica (fogo da explosão + verde do Amargo na radiação)
# ======================================================================

@effect('herege_bomba_arremesso', 'tecnomancer', (40, 40), 8, fps=16, loop=True, anchor=(20, 20),
        desc='Bomba Atômica (projétil): ogiva de latão com aletas, girando, luz verde piscando.')
def _(rng):
    def f(c, t, i):
        th = TAU * t
        dx, dy = math.cos(th), math.sin(th) * .8
        c.line('aco', 20 - dx * 9, 20 - dy * 9, 20 + dx * 9, 20 + dy * 9, 4.2, 1.4, w1=3.4, hard=True)
        c.blob('latao', 20 + dx * 8, 20 + dy * 8, 3.6, 1.2, hard=True)
        for s in (-1, 1):
            c.line('latao', 20 - dx * 9, 20 - dy * 9, 20 - dx * 13 - dy * 5 * s, 20 - dy * 13 + dx * 5 * s, .9, 1.4, hard=True)
        c.blob('amargo', 20 + dx * 2, 20 + dy * 2, 1.6, 1.8 if i % 2 == 0 else .6)
    return f


@effect('herege_bomba_explosao', 'tecnomancer', (400, 424), 40, fps=15, anchor=(200, 332),
        desc='Bomba Atômica: clarão, bola de fogo, onda de choque no chão, anel de condensação e cogumelo atômico que sobe e escurece.')
def _(rng):
    cx, gy = 200, 332
    puffs = [(rng.uniform(0, TAU), rng.uniform(.75, 1.1), rng.uniform(.8, 1.25), rng.uniform(0, 1)) for _ in range(80)]
    stem = [(rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(.7, 1.3)) for _ in range(44)]
    dust = [(rng.uniform(0, TAU), rng.uniform(.6, 1.15), rng.uniform(.7, 1.4)) for _ in range(110)]

    def f(c, t, i):
        rise = ease_out(min(t / .7, 1), 1.8)
        H = 40 + 200 * rise                         # altura do centro do chapéu
        Rc = 26 + 58 * ease_out(min(t / .8, 1), 1.5) # raio do chapéu
        heat = max(0., 1 - t / .7)                  # fogo -> fumaça
        # clarão
        if t < .14:
            k = 1 - t / .14
            c.blob('fogo', cx, gy - 30, 105 * (1 - k * .4), 1.2 * k)
            c.blob('fogo', cx, gy - 30, 40, 3 * k)
        # onda de choque no chão + poeira que corre
        wv = ease_out(min(t / .5, 1), 2)
        c.ring('fogo', cx, gy, 20 + 170 * wv, 3, 1.2 * (1 - wv), sy=.42)
        c.ring('poeira', cx, gy, 15 + 165 * wv, 7, .9 * (1 - wv * .7), sy=.42, op='max')
        for th, rr, s, in dust:
            r = (25 + 150 * rr) * ease_out(min(t / .6, 1), 2)
            c.blob('poeira', cx + math.cos(th) * r, gy + math.sin(th) * r * .42 - 6 * s * min(t * 3, 1),
                   (10 + 12 * t) * s, .95 * (1 - ease_in(t, 1.5) * .6), op='max')
        # coluna (caule)
        for ox, v, s in stem:
            y = gy - (H - Rc * .4) * v
            w = (13 + 9 * (1 - v)) * s * min(t * 4, 1)
            x = cx + ox * (6 + 10 * (1 - v))
            if heat > 0: c.blob('fogo', x, y, w * .8, .38 * heat * (1 - v * .3))
            c.blob('fumaca', x, y, w, .85 * min(t * 5, 1), op='max')
        # chapéu: anel que rola (toroide) + miolo incandescente
        cyy = gy - H
        for th, rr, s, ph in puffs:
            a = th + t * 1.2 * (1 if ph > .5 else .7)
            roll = TAU * (ph + t * .9)
            r = Rc * rr * (1 + .18 * math.cos(roll))
            x = cx + math.cos(a) * r
            y = cyy + math.sin(a) * r * .38 - math.sin(roll) * Rc * .28
            w = Rc * .42 * s
            c.blob('fumaca', x, y, w, .95, op='max')
            if heat > 0: c.blob('fogo', x, y + w * .3, w * .7, .32 * heat * (.5 + .5 * math.cos(roll)))
        if heat > 0:
            c.blob('fogo', cx, cyy + Rc * .1, Rc * .75, .55 * heat)
            c.blob('fogo', cx, cyy + Rc * .2, Rc * .3, 1.1 * heat)
        else:
            c.blob('fogo', cx, cyy + Rc * .25, Rc * .35, .25 * (1 - t))
        # saia do chapéu e anel de condensação (Wilson)
        if .12 < t < .75:
            k = bell(t, .12, .75)
            c.ring('fumaca', cx, cyy + Rc * .55, Rc * 1.35, 3.5, .7 * k, sy=.3, op='max')
            c.ring('fumaca', cx, gy - H * .45, Rc * .9 + 30 * t, 3, .55 * k, sy=.3, op='max')
        # fim: tudo se desfaz
        if t > .8:
            fade_ = (t - .8) / .2
            c.blob('fumaca', cx, cyy, Rc * 1.3, .4 * fade_, op='max')
    return f


@effect('herege_radiacao', 'tecnomancer', (288, 160), 24, fps=10, loop=True, layer='chao', anchor=(144, 80),
        desc='Zona radioativa da Bomba Atômica: chão queimado, brilho verde do Amargo e poeira radioativa subindo (repetir enquanto durar).')
def _(rng):
    mt = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(.6, 1.3)) for _ in range(60)]
    pocas = [(x, y, ph, s) for x, y, ph, s in [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(.6, 1.5)) for _ in range(40)] if x * x + y * y < .8]
    def f(c, t, i):
        cx, cy = 144, 80
        c.disc('sombra', cx, cy, 128, .55, sy=.5, edge=.5)
        pul = .8 + .2 * math.sin(TAU * t)
        c.ring('amargo', cx, cy, 120, 4, .35 * pul, sy=.5, jag=lambda th: 1 + .06 * np.sin(th * 5 + 2 * np.sin(th * 3)) + .03 * np.sin(th * 13 + TAU * t))
        c.disc('amargo', cx, cy, 112, .12 * pul, sy=.5, edge=.7)
        for x, y, ph, s in pocas:
            k = .6 + .4 * math.sin(TAU * (t + ph))
            c.blob('amargo', cx + x * 100, cy + y * 48, 9 * s, .3 * k, sy=.5)
            c.blob('amargo', cx + x * 100, cy + y * 48, 2.5 * s, .9 * k, sy=.5)
        for x, y, ph, s in mt:
            u = (t * s + ph) % 1
            r = math.hypot(x, y)
            if r > 1: continue
            c.blob('amargo' if s > 1 else 'po_amargo', cx + x * 118, cy + y * 58 - 50 * u, 1.3 * s, 1.4 * bell(u, 0, 1),
                   op='add' if s > 1 else 'max')
    return f
