"""Efeitos das armas do Gladiador Demoníaco (set PvP): lava na lâmina, aura infernal, rastro de golpe e faíscas
no cabo. Rampa dominante 'rubro' (vermelho-sangue incandescente) com 'brasa' e um fio de 'sagrado' dourado nas
bordas, como pede o set. Só ligados nas armas do set; nada aqui vai para o mundo."""
import math
from vfx import effect, ease_out, ballistic
TAU = math.tau


@effect('brasa_lamina', 'armas_pvp', (48, 72), 20, fps=14, loop=True, anchor=(24, 36),
        desc='Brasa da Lâmina: lava escorre pelo gume da arma em gotas incandescentes que caem e se apagam.')
def _(rng):
    drops = [(rng.uniform(0, 1), rng.uniform(-5, 5), rng.uniform(.8, 1.3)) for _ in range(6)]

    def f(c, t, i):
        # veio de lava no gume: a lâmina brilha por dentro, mais forte na ponta
        c.line('rubro', 24, 4, 24, 60, 2.2, .55, w1=1.2, a1=.75)
        c.line('brasa', 24, 5, 24, 58, 1.0, .9, w1=.4, a1=1)
        c.line('sagrado', 24, 6, 24, 56, .4, .5, w1=.2, a1=.7)
        for k, (ph, dx, sz) in enumerate(drops):
            u = (t + ph) % 1                          # cada gota desce no seu tempo
            y = 8 + u * 56
            x = 24 + dx * .4 + math.sin(u * TAU + k) * .8
            fade = min(u * 5, 1) * (1 - u) ** .6 + .08
            c.line('rubro', x, y - 9 * sz, x, y, 1.3 * sz, .95 * fade, w1=.5, a1=fade)   # rastro da gota
            c.blob('brasa', x, y, 2.4 * sz, fade)
            c.blob('sagrado', x, y, .9 * sz, .9 * fade)
        # brilho da ponta, pulsando devagar
        c.blob('brasa', 24, 5, 4.0, .6 + .4 * math.sin(TAU * t) ** 2)
    return f


@effect('aura_pulso_infernal', 'armas_pvp', (80, 64), 16, fps=12, loop=True, anchor=(40, 36),
        desc='Aura Pulso Infernal: anel de calor vermelho que pulsa em volta da arma, com brasas dourada nas bordas.')
def _(rng):
    spots = [(TAU * k / 12 + rng.uniform(-.2, .2), rng.uniform(.9, 1.4)) for k in range(12)]

    def f(c, t, i):
        pulse = .5 + .5 * math.sin(TAU * t)          # respiração do anel
        R = 25 + 4 * pulse
        c.disc('rubro', 40, 36, R, .12 + .08 * pulse, sy=.55, edge=8)   # névoa de calor por dentro
        c.ring('rubro', 40, 36, R, 2.2, .75 + .25 * pulse, sy=.55)     # anel principal
        c.ring('brasa', 40, 36, R - 3, .7, .5 + .3 * (1 - pulse), sy=.55)   # calor no miolo do anel
        for k, (a, s) in enumerate(spots):
            ang = a + TAU * t * .25
            x = 40 + math.cos(ang) * R
            y = 36 + math.sin(ang) * R * .55
            flick = .5 + .5 * math.sin(TAU * (t * 2 + k / 12))
            c.blob('brasa', x, y, 1.3 * s, .8 * flick + .2)
            if k % 3 == 0:
                c.blob('sagrado', x, y, .6, .7 * flick)
    return f


@effect('trail_sweep_infernal', 'armas_pvp', (96, 72), 10, fps=18, anchor=(48, 52),
        desc='Rastro do Golpe Infernal: arco de fogo vermelho e fio dourado que a lâmina deixa no ataque.')
def _(rng):
    cx, cy, rx, ry = 48, 52, 36, 18
    a0, a1 = -math.pi * .92, -math.pi * .08          # arco de cima, de um lado ao outro

    def f(c, t, i):
        head = a0 + (a1 - a0) * ease_out(min(t * 1.25, 1), 2)
        K = 34
        for k in range(K):                             # rastro: a cabeça é o mais forte, a cauda some
            a = head - k * .06
            if a < a0 - .2:
                break
            fade = (1 - k / K) ** 1.3
            x, y = cx + math.cos(a) * rx, cy + math.sin(a) * ry
            c.blob('rubro', x, y, 2.6 * fade + .5, 1.0 * fade * (1 - t * .3))
            if k % 4 == 0:
                c.blob('brasa', x, y - 1, 1.5 * fade, .8 * fade)
        hx, hy = cx + math.cos(head) * rx, cy + math.sin(head) * ry
        c.blob('brasa', hx, hy, 2.4, 1.0 * (1 - t * .5))       # ponta do golpe, quente
        c.blob('sagrado', hx, hy, 1.1, .9 * (1 - t))           # fio dourado no centro da ponta
    return f


@effect('faisca_cabo', 'armas_pvp', (40, 40), 12, fps=14, loop=True, anchor=(20, 20),
        desc='Faísca do Cabo: centelhas de brasa saltam do cabo e do guarda-mão quando a arma é segurada.')
def _(rng):
    sparks = []
    for k in range(7):
        ph = rng.uniform(0, 1)
        ang = rng.uniform(-math.pi * .9, -math.pi * .1)   # saem para cima, em leque
        spd = rng.uniform(18, 28)
        sparks.append((ph, ang, spd))

    def f(c, t, i):
        c.blob('brasa', 20, 20, 4.5, .4 + .2 * math.sin(TAU * t))   # brilho do guarda-mão
        for ph, ang, spd in sparks:
            u = (t + ph) % 1
            x0, y0 = 20, 21
            v = (math.cos(ang) * spd, math.sin(ang) * spd)
            x, y = ballistic((x0, y0), v, u * .6, g=50)     # sobe e cai
            fade = (1 - u) ** .7
            px, py = ballistic((x0, y0), v, max(u - .1, 0) * .6, g=50)
            c.line('faisca', px, py, x, y, .7, .9 * fade, w1=.35)   # rastro curto
            c.blob('faisca', x, y, 1.1, 1.0 * fade)
            c.blob('brasa', x, y, 1.6, .5 * fade)
    return f
