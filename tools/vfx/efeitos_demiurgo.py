"""Cetro do Demiurgo: os efeitos da arma do administrador. Rampa dominante 'alma' (verde-esmeralda pálido, só
dele no jogo); faíscas brancas 'faisca' e um toque de 'sagrado' nas runas. Nada de vermelho: ele não julga, mede."""
import math
from vfx import effect, ease_out, ease_in, bell
TAU = math.tau
from efeitos_classes import rune_circle, star, burst, motes


@effect('demiurgo_aura', 'itens', (128, 144), 24, fps=12, loop=True, anchor=(64, 132), char='qualquer',
        desc='Aura Demiurgica: tres aneis de luz esmeralda girando em volta de quem segura o cetro, com runas no chao '
             'e faiscas subindo; todos veem.')
def _(rng):
    def f(c, t, i):
        cx, cy = 64, 132
        # anel de runas no chão, girando devagar
        rune_circle(c, 'alma', cx, cy - 2, 34, t * .5, a=.55, sy=.42, n=14, spin=.6, seed=7)
        c.ring('alma', cx, cy - 2, 36, .9, .5, sy=.42)
        # três anéis armilares em volta do corpo, cada um com inclinação e fase
        for k, (ry, ph, h) in enumerate(((.28, 0, 70), (.18, .33, 62), (.36, .66, 78))):
            a = TAU * (t + ph)
            for j in range(28):
                u = j / 28; th = TAU * u + a
                x = cx + math.cos(th) * 30; y = cy - h + math.sin(th) * 30 * ry
                front = math.sin(th) > 0
                c.blob('alma', x, y, 1.1 if front else .7, (.9 if front else .35) * (1 + .3 * math.sin(TAU * u * 3)))
            c.blob('faisca', cx + math.cos(a) * 30, cy - h + math.sin(a) * 30 * ry, 1.6, 1.2)
        # luz subindo do chão até a coroa
        c.line('alma', cx, cy - 4, cx, cy - 118, 2.2, .18, w1=.2, a1=.02)
        motes(c, 'faisca', cx, cy - 10, t, 14, 22, 110, 11, s=.5, a=1.3, loop=True)
        motes(c, 'alma', cx, cy - 6, t, 10, 30, 90, 5, s=.7, a=.8, loop=True)
    return f


@effect('demiurgo_golpe', 'itens', (96, 112), 12, fps=18, anchor=(48, 100),
        desc='Golpe do cetro: a esmeralda abre um anel de luz no alvo e um feixe curto sobe; faiscas brancas.')
def _(rng):
    def f(c, t, i):
        cx, cy = 48, 60
        e = ease_out(t, 2.2); a = 1 - ease_in(t, 1.4)
        c.ring('alma', cx, cy, 6 + 34 * e, 2.4 * (1 - t) + .6, 1.5 * a, sy=.55)
        c.ring('alma', cx, cy, 4 + 24 * e, .8, 1.0 * a, sy=.55)
        fl = bell(t, 0, .4)
        c.blob('alma', cx, cy, 14 * fl, 1.0 * fl, sy=.7)
        c.blob('faisca', cx, cy, 4 * fl, 2.0 * fl)
        c.line('alma', cx, cy, cx, cy - 46 * ease_out(t, 3), 3.0 * (1 - t) + .5, 1.3 * a, w1=.3, a1=.2)
        star(c, 'faisca', cx, cy, 10 + 18 * e, 4, a=1.2 * a, sy=.6, rot=t * 1.2, w=.35)
        burst(c, 'faisca', cx, cy, t, 14, 34, 3, a=1.5, g=.6, s=.5, up=.5)
    return f


@effect('demiurgo_verbo', 'itens', (256, 128), 14, fps=16, layer='chao', anchor=(128, 64),
        desc='Verbo: a onda de luz esmeralda do ataque basico varre o chao em 8 m, com o circulo de runas que mede.')
def _(rng):
    def f(c, t, i):
        cx, cy = 128, 64
        e = ease_out(t, 2.0); a = 1 - ease_in(t, 1.6)
        R = 6 + 118 * e
        c.ring('alma', cx, cy, R, 3.2 * (1 - t) + .8, 1.4 * a, sy=.5)
        c.ring('alma', cx, cy, R * .86, .9, .8 * a, sy=.5)
        c.ring('faisca', cx, cy, R * 1.02, .5, .9 * a, sy=.5)
        rune_circle(c, 'sagrado', cx, cy, R * .55, t * .4, a=.6 * a, sy=.5, n=16, spin=.3, seed=3)
        star(c, 'alma', cx, cy, R * .5, 7, a=.5 * a, sy=.5, rot=-t * .6, w=.4, skip=3)
        for k in range(14):
            th = TAU * k / 14 + .2
            c.line('alma', cx + math.cos(th) * R * .75, cy + math.sin(th) * R * .375,
                   cx + math.cos(th) * R * 1.0, cy + math.sin(th) * R * .5, .6, 1.1 * a, w1=.15)
        fl = bell(t, 0, .3)
        c.blob('alma', cx, cy, 20 * fl, .9 * fl, sy=.5)
    return f


@effect('demiurgo_juizo', 'itens', (112, 232), 18, fps=18, anchor=(56, 220),
        desc='Juizo do Demiurgo: coluna de luz esmeralda desce do alto sobre o inimigo apagado; so sobram faiscas.')
def _(rng):
    def f(c, t, i):
        cx, cy = 56, 212
        d = ease_out(min(t * 2.2, 1), 3)             # a coluna desce rápido
        a = 1 - ease_in(max(0, (t - .35) / .65), 1.6)
        top = 4; y1 = cy - (cy - top) * (1 - d)
        c.line('alma', cx, top, cx, y1, 7 * a + 1, 1.5 * a, w1=.6, a1=1.2 * a)
        c.line('faisca', cx, top + 6, cx, y1, 1.0, .8 * a, w1=.3)
        # impacto no chão quando a coluna chega
        im = bell(t, .3, .75)
        c.ring('alma', cx, cy, 8 + 42 * ease_out(max(0, (t - .3) / .7), 2), 2.2 * (1 - t) + .5, 1.4 * im, sy=.45)
        c.blob('alma', cx, cy - 12, 18 * im, .9 * im, sy=.8)
        c.blob('faisca', cx, cy - 10, 5 * im, 2.2 * im)
        rune_circle(c, 'sagrado', cx, cy, 30, t * .3, a=.7 * im, sy=.45, n=12, spin=.4, seed=9)
        # o que sobra do inimigo: faíscas subindo e sumindo
        motes(c, 'faisca', cx, cy - 20, max(0, (t - .4) / .6), 26, 18, 150, 13, s=.5, a=1.6)
        motes(c, 'alma', cx, cy - 20, max(0, (t - .45) / .55), 16, 24, 120, 17, s=.8, a=.9)
    return f
