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
