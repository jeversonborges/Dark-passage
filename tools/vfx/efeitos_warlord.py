"""Efeitos próprios do Warlord (Vigília) que ainda não tinham folha: Investida, Muralha e Estandarte."""
import math
from vfx import (effect, ease_out, bell)
from efeitos_classes import burst

TAU = 2 * math.pi


@effect('wl_investida_de_ferro', 'warlord', (96, 64), 10, fps=16, anchor=(48, 52),
        desc='Investida de Ferro: rastro de poeira e faíscas de aço no avanço com o escudo erguido.')
def _(rng):
    def f(c, t, i):
        for k in range(4):
            x = 70 - k * 14 * ease_out(min(t * 1.4, 1)) - k * 4
            c.blob('poeira', x, 46 + k * 2, 9 - k * 1.4, .8 * (1 - t) + .2)
        c.line('faisca', 46, 43, 14, 37, 2.6 * (1 - t) + .4, 1.0, w1=.5)
        burst(c, 'faisca', 56, 46, t, 10, 26, 3, up=10)
    return f


@effect('wl_muralha_de_escudo', 'warlord', (96, 96), 12, fps=14, anchor=(48, 70),
        desc='Muralha de Escudo: anel de aço se fecha ao redor do Warlord e devolve o golpe em faísca.')
def _(rng):
    def f(c, t, i):
        R = 34 - 8 * ease_out(min(t / .5, 1))
        c.ring('eco', 48, 58, R, 1.8, 1.5 * (1 - t) + .3, sy=.5)
        c.ring('faisca', 48, 58, R - 5, .7, .9 * (1 - t), sy=.5)
        k = bell(t, .35, 1)
        if k > 0:
            c.blob('rubro', 48, 52, 8 * k, 1.2 * k)
            for n in range(6):
                a = TAU * n / 6
                c.blob('faisca', 48 + math.cos(a) * 26, 58 + math.sin(a) * 13, 2.2 * k, 1.2 * k)
    return f


@effect('wl_estandarte_da_ruina', 'warlord', (64, 112), 14, fps=12, anchor=(32, 104),
        desc='Estandarte da Ruína: haste de ferro cravada no chão com pano rasgado que tremula e um anel rubro no solo.')
def _(rng):
    def f(c, t, i):
        sway = math.sin(t * TAU) * 3
        c.ring('rubro', 32, 98, 18, .6, .9, sy=.5)
        c.line('eco', 32, 98, 32, 20, 1.8, 1.4, w1=.4)
        for k in range(6):   # pano rasgado: tiras que balançam, mais soltas embaixo
            x = 34 + k * 3.2
            bot = 52 - (k % 2) * 6 + sway * (k / 5)
            c.line('sangue', x + sway * .3, 26, x + sway * (k / 5), bot, 3.4, .8, w1=2.2)
            c.blob('sangue', x + sway * (k / 5), bot, 1.6, .7)
        c.blob('rubro', 32 + sway, 24, 2.6, .9 * bell(t, .5, 1))
    return f


@effect('wl_redemoinho_de_aco', 'warlord', (96, 96), 12, fps=18, anchor=(48, 56), loop=False,
        desc='Redemoinho de Aço: rastro circular fechado e vermelho girando em volta do Warlord, com a faísca na ponta da lâmina.')
def _(rng):
    def f(c, t, i):
        head = TAU * t
        for k in range(64):           # rastro fechado: a cabeça é o ponto mais forte e a cauda dá a volta inteira
            a = head - k * (TAU / 64)
            fade = (1 - k / 64) ** 1.3
            c.blob('rubro', 48 + math.cos(a) * 28, 56 + math.sin(a) * 14, 1.8 * fade + .5, .8 * fade * (1 - t * .3))
        c.ring('sangue', 48, 56, 28, .7, .5 * (1 - t) + .15, sy=.5)
        hx, hy = 48 + math.cos(head) * 28, 56 + math.sin(head) * 14
        c.line('rubro', 48 + math.cos(head) * 4, 56 + math.sin(head) * 2, hx, hy, 1.8, .95, w1=.6)   # lâmina girando no eixo
        c.blob('faisca', hx, hy, 2.0, 1.0)
    return f
