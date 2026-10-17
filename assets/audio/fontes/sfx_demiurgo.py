"""Cetro do Demiurgo: os sons da arma do administrador (vidro, sino alto, coro e órgão; sem metal sujo)."""
from kit import *  # noqa
from registro import som


@som('itens/cetro_golpe', var=3, lufs=-14, espaco='catedral', mix=0.3, desc='golpe do Cetro do Demiurgo: sino de vidro esmeralda, estalo de luz e um sopro de coro')
def _(v):
    d = 1.6
    y = np.zeros(ns(d))
    y = place(y, whoosh(0.3, 500, 6000, 1.0, 0.4) * 0.5, 0)
    y = place(y, add(glass(ru(2300, 2600), 0.9), glass(ru(3400, 3700), 0.6) * 0.5, glass(ru(1150, 1300), 1.2) * 0.4), 0.05)
    y = place(y, zap(0.25, 0.6, 60) * 0.25, 0.04)
    y = place(y, choir([hz('E5'), hz('B5')], 0.9, 'a', 'soprano', voices=4, attack=0.03, release=0.5) * 0.22, 0.08)
    y = place(y, sparks(0.5, 160) * 0.35, 0.06)
    return y


@som('itens/cetro_juizo', var=1, lufs=-12, espaco='catedral', mix=0.4, desc='Juizo do Demiurgo: coluna de luz desce (coro + orgao subindo), impacto de vidro e o silencio depois')
def _(v):
    d = 3.2
    y = np.zeros(ns(d))
    y = place(y, organ([hz('E2'), hz('B2'), hz('E3'), hz('G#3')], 1.4, stop='pleno', attack=0.4, release=0.6) * 0.5, 0)
    y = place(y, choir([hz('E4'), hz('G#4'), hz('B4'), hz('E5')], 1.6, 'o', 'soprano', voices=8, attack=0.5, release=0.9) * 0.45, 0.1)
    y = place(y, rumble(1.5, 45, 1.0) * 0.5, 0.2)
    y = place(y, whoosh(0.5, 200, 8000, 0.8, 0.5) * 0.7, 0.9)
    y = place(y, add(glass(2500, 1.6), glass(3800, 1.0) * 0.6, glass(1250, 2.0) * 0.5), 1.25)
    y = place(y, thump(50, 0.8, 2.0, 0.3, 0.2) * 0.8, 1.25)
    y = place(y, sparks(1.2, 220) * 0.4, 1.3)
    y = place(y, choir([hz('E5'), hz('B5')], 1.5, 'a', 'soprano', voices=3, attack=0.02, release=1.2) * 0.2, 1.3)
    return y


@som('itens/cetro_aura', var=1, lufs=-26, espaco='catedral', mix=0.3, loop=True, bus='ambiente', desc='aura do Cetro do Demiurgo em loop: zumbido de vidro bem baixo, os tres aneis girando, um coro longe')
def _(v):
    d = 12.0
    y = np.zeros(ns(d))
    y = add(y, hum(d, 82.4, 8, 0.0008) * 0.35)
    y = add(y, hum(d, 164.8, 4, 0.0012) * 0.15)
    t = 0.3
    while t < d - 1.5:
        y = place(y, glass(ru(2300, 2700), 1.2) * ru(0.08, 0.16), t)
        t += ru(0.9, 1.8)
    y = add(y, choir([hz('E4'), hz('B4'), hz('E5')], d, 'o', 'soprano', voices=6, attack=2.0, release=2.0) * 0.12)
    return loopify(y, 2.0)
