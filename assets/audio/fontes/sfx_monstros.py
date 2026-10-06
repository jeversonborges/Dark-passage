"""Vozes e acoes dos monstros (design/missoes/dados/monstros.json)."""
from kit import *  # noqa
from registro import som


def M(id, desc, var=1, lufs=-16, espaco='rua', mix=0.15, loop=False):
    if not loop:
        return som('monstros/' + id, var=var, lufs=lufs, espaco=espaco, mix=mix, desc=desc)

    def deco(fn):
        som('monstros/' + id, var=var, lufs=lufs, espaco=espaco, mix=mix, desc=desc, loop=True)(
            lambda v: loopify(to_stereo(fn(v)), 0.6))
        return fn
    return deco


# ======================================================== Corvo de Cinza
def caw(dur=0.35, f0=520):
    n = ns(dur)
    f = f0 * np.interp(np.linspace(0, 1, n), [0, 0.2, 1], [0.9, 1.05, 0.8])
    src = glottal(f, dur, 0.03, 0.4, 0.4, tilt=3000)
    src *= 1 + 0.8 * np.sin(2 * np.pi * ru(55, 75) * tt(dur))  # aspereza
    y = formant(src, 'a', 'alto', ru(1.3, 1.5)) * 2
    y = sat(y, 2.5) + bp(white(dur), 2500, 1.5) * 0.3
    return blp(y, 6000, 2) * env_pts(dur, [(0, 0), (0.02, 1), (dur * 0.6, 0.7), (dur, 0)])


@M('corvo_grasnado', 'Corvo de Cinza: grasnado (alerta/ocioso)', var=3, lufs=-18)
def _(v):
    y = np.zeros(ns(1.2))
    k = int(ru(1, 3.99))
    for i in range(k):
        y = place(y, caw(ru(0.25, 0.4), ru(480, 600)), i * ru(0.32, 0.42))
    return y


@M('corvo_ataque', 'Corvo de Cinza: bicada com batida de asas', var=2)
def _(v):
    y = np.zeros(ns(0.8))
    y = place(y, wings(0.5, 2, 0.5, 1.4) * 0.8, 0)
    y = place(y, caw(0.2, 650) * 0.7, 0.15)
    return place(y, add(wood_knock(900, 0.1), flesh(0.2, 0.4, 0.5) * 0.5), 0.3)


@M('corvo_voo', 'Corvo de Cinza: bando batendo asas e soltando fuligem', var=2, lufs=-20)
def _(v):
    y = add(wings(1.6, 5, 0.5, 1.3), wings(1.6, 4, 0.5, 1.2) * 0.6)
    return add(y, bbp(crackle(1.6, 100, 0.002), 1500, 6000) * 0.15)


@M('corvo_morte', 'Corvo de Cinza: morte (guincho + penas caindo)')
def _(v):
    y = np.zeros(ns(1.2))
    y = place(y, caw(0.45, 700) * np.linspace(1, 0.3, ns(0.45)), 0)
    y = place(y, cloth(0.6, 1.0, 4500), 0.1)
    return place(y, thump(110, 0.3, 0.5, 0.05, 0.2) * 0.5, 0.6)


# ======================================================== Carnical
def ghoul(dur, f0=95, vw='u', vw2='a', growl=0.7):
    return creature(dur, f0, [(0, 0.9), (0.4, 1.1), (1, 0.8)], vw, vw2, 'baixo', 0.75, growl, 0.3, 2.5, 0.5)


@M('carnical_gemido', 'Carnical: gemido de fome (ocioso)', var=3, lufs=-19)
def _(v):
    return ghoul(ru(1.2, 1.8), ru(85, 110), 'u', 'o', 0.5)


@M('carnical_alerta', 'Carnical: viu o jogador e corre (rosnado subindo)', var=2)
def _(v):
    return creature(1.0, 110, [(0, 0.8), (0.5, 1.4), (1, 1.2)], 'o', 'a', 'baixo', 0.8, 0.9, 0.3, 3, 0.6)


@M('carnical_ataque', 'Carnical: unhada', var=3)
def _(v):
    y = np.zeros((ns(0.8), 2))
    y = place(y, whoosh(0.25, 600, 3500, 1.8, 0.5, 0.2, -0.4, 0.4), 0)
    y = place(y, to_stereo(ghoul(0.4, 130, 'a', 'a', 0.9) * 0.6), 0.02)
    return place(y, to_stereo(flesh(0.3, 0.8, 0.8)), 0.18)


@M('carnical_comendo', 'Carnical: comendo corpo caido (loop curto)', lufs=-20, loop=True)
def _(v):
    y = np.zeros(ns(3.0))
    t = 0.0
    while t < 2.7:
        y = place(y, add(flesh(0.25, 1.6, 0.7) * 0.6, crunch(0.1, 300, 600, 3000) * 0.2), t)
        t += ru(0.25, 0.5)
    return add(y, ghoul(3.0, 80, 'u', 'u', 0.3) * 0.3)


@M('carnical_morte', 'Carnical: morte (gorgolejo)', var=2)
def _(v):
    d = 1.4
    g = creature(d, 100, [(0, 1.1), (1, 0.5)], 'a', 'u', 'baixo', 0.75, 1.0, 0.4, 2, 0.4)
    return add(g * env_pts(d, [(0, 1), (d, 0)]), lp(liquid(d, 15, 150, 400), 1200) * 0.5)


# ======================================================== Cao de Vala
@M('cao_rosnado', 'Cao de Vala: rosnado (ocioso/alerta)', var=2, lufs=-18)
def _(v):
    d = ru(1.5, 2.2)
    return creature(d, 65, [(0, 0.95), (0.5, 1.05), (1, 0.95)], 'u', 'o', 'baixo', 0.9, 1.0, 0.3, 2.5, 0.4)


@M('cao_latido', 'Cao de Vala: latido rouco', var=3)
def _(v):
    y = np.zeros(ns(1.0))
    for i in range(int(ru(1, 3.99))):
        b = creature(0.18, ru(260, 320), [(0, 0.8), (0.2, 1.2), (1, 0.7)], 'a', 'o', 'tenor', 1.0, 0.8, 0.2, 3, 0.3)
        y = place(y, b, i * ru(0.22, 0.3))
    return y


@M('cao_uivo', 'Cao de Vala: uivo que chama a matilha', lufs=-16, espaco='cripta', mix=0.3)
def _(v):
    d = 3.0
    n = ns(d)
    f = 380 * np.interp(np.linspace(0, 1, n), [0, 0.15, 0.6, 1], [0.8, 1.45, 1.35, 0.9])
    f = vibrato(f, d, 5, 0.015, 0.5)
    src = glottal(f, d, 0.01, 0.15, 0.3, tilt=1200)
    y = formant(src, 'u', 'alto', 1.0, 'o', np.linspace(0, 1, n) ** 2) * 2
    y = blp(sat(y, 1.8), 5000)
    return y * env_pts(d, [(0, 0), (0.2, 1), (2.4, 0.8), (d, 0)])


@M('cao_mordida', 'Cao de Vala: mordida (dentes batendo + carne)', var=3)
def _(v):
    y = np.zeros(ns(0.6))
    y = place(y, creature(0.25, 200, [(0, 1), (1, 1.2)], 'a', 'a', 'tenor', 1.0, 1.0, 0.2, 3) * 0.6, 0)
    y = place(y, add(wood_knock(1200, 0.08) * 1.2, wood_knock(1400, 0.08) * 0.8), 0.12)
    return place(y, flesh(0.3, 1.2, 0.7) * 0.8, 0.13)


@M('cao_morte', 'Cao de Vala: ganido de morte')
def _(v):
    d = 1.2
    n = ns(d)
    f = 900 * np.interp(np.linspace(0, 1, n), [0, 0.1, 1], [0.9, 1.1, 0.5])
    y = formant(glottal(f, d, 0.02, 0.2, 0.3, tilt=2000), 'i', 'soprano', 1.0, 'u', np.linspace(0, 1, n)) * 2
    return blp(sat(y, 1.5), 5000) * env_pts(d, [(0, 0), (0.03, 1), (d, 0)])


# ======================================================== Nao-Julgado
def moan(d, f0=110, voz='baixo'):
    n = ns(d)
    f = vibrato(f0 * np.interp(np.linspace(0, 1, n), [0, 0.5, 1], [0.95, 1.05, 0.85]), d, 4, 0.01, 0.3)
    src = glottal(f, d, 0.008, 0.08, 0.5, tilt=700)
    y = formant(src, 'u', voz, 0.9, 'o', np.linspace(0, 1, n)) * 2
    return lp(y, 2500) * env_pts(d, [(0, 0), (d * 0.3, 1), (d, 0)], 1.2)


@M('nao_julgado_gemido', 'Nao-Julgado: lamento baixo enquanto espera na fila (ocioso)', var=3, lufs=-21, espaco='cripta', mix=0.3)
def _(v):
    return moan(ru(2.0, 3.0), ru(95, 125))


@M('nao_julgado_alerta', 'Nao-Julgado: foi tocado (lamento sobe e o lacre estala)', var=2, espaco='cripta', mix=0.25)
def _(v):
    y = np.zeros(ns(1.8))
    y = place(y, crunch(0.2, 400, 600, 3500, 0.8) * 0.6, 0)
    m = creature(1.6, 120, [(0, 0.8), (0.5, 1.3), (1, 1.1)], 'u', 'a', 'baixo', 0.85, 0.4, 0.2, 2, 0.6)
    return place(y, m, 0.1)


@M('nao_julgado_fila', 'Nao-Julgado: a fila inteira vira (varios lamentos juntos)', espaco='cripta', mix=0.35, lufs=-15)
def _(v):
    y = np.zeros((ns(3.0), 2))
    for i in range(5):
        m = creature(2.0, ru(100, 140), [(0, 0.8), (0.5, 1.3), (1, 1.1)], 'u', 'a', 'baixo', 0.85, 0.4, 0.2, 2, 0.6)
        y = place(y, pan(m, ru(-0.8, 0.8)) * ru(0.5, 0.9), ru(0, 0.8))
    return y


@M('nao_julgado_ataque', 'Nao-Julgado: golpe com a mao enrolada na mortalha', var=2)
def _(v):
    y = np.zeros((ns(0.8), 2))
    y = place(y, whoosh(0.35, 250, 1500, 0.9, 0.5, 0, -0.3, 0.3), 0)
    y = place(y, to_stereo(add(cloth(0.3, 1.0, 2000), thump(70, 0.4, 1.0, 0.08, 0.2), flesh(0.3, 0.4, 1.0) * 0.6)), 0.25)
    return y


@M('nao_julgado_morte', 'Nao-Julgado: lacre de cera quebra e ele suspira aliviado', var=2, espaco='cripta', mix=0.3)
def _(v):
    y = np.zeros(ns(2.4))
    y = place(y, crunch(0.3, 900, 800, 5000, 1.0), 0)
    y = place(y, breath(1.6, 'a', 'baixo', False, 0.8) * 0.7, 0.15)
    y = place(y, moan(1.4, 90) * 0.5, 0.2)
    return place(y, add(cloth(0.5, 0.8, 2000), thump(55, 0.5, 0.8, 0.1, 0.2) * 0.6), 1.2)


# ======================================================== Porco Pestilento
def squeal(d, f0=1100):
    n = ns(d)
    f = vibrato(f0 * np.interp(np.linspace(0, 1, n), [0, 0.2, 1], [0.8, 1.1, 0.75]), d, 9, 0.04, 0.02)
    src = glottal(f, d, 0.05, 0.4, 0.3, tilt=3500)
    y = formant(src, 'i', 'soprano', 1.1, 'e', np.linspace(0, 1, n)) * 2.5
    return blp(sat(y, 3), 6000) * env_pts(d, [(0, 0), (0.03, 1), (d * 0.7, 0.8), (d, 0)])


def grunt(d=0.25, f0=110):
    return creature(d, f0, [(0, 1), (1, 0.8)], 'o', 'u', 'baixo', 0.8, 1.2, 0.5, 3, 0.4)


@M('porco_grunhido', 'Porco Pestilento: grunhidos (ocioso)', var=3, lufs=-19, espaco='abatedouro', mix=0.2)
def _(v):
    y = np.zeros(ns(1.6))
    for i in range(int(ru(2, 4.99))):
        y = place(y, grunt(ru(0.15, 0.3), ru(90, 130)), i * ru(0.22, 0.35))
    return y


@M('porco_guincho', 'Porco Pestilento: guincho (alerta/dor)', var=2, espaco='abatedouro', mix=0.2)
def _(v):
    return squeal(ru(0.6, 0.9), ru(950, 1250))


@M('porco_investida', 'Porco Pestilento: investida (cascos + guincho + impacto que derruba)', espaco='abatedouro', mix=0.2, lufs=-13)
def _(v):
    y = np.zeros(ns(2.0))
    t = 0.0
    for i in range(8):
        y = place(y, add(thump(60, 0.25, 1.0, 0.05, 0.6) * 0.8, debris(0.2, 60, 300, 3000, 0.05) * 0.4), t)
        t += 0.11
    y = place(y, squeal(0.8, 1100) * 0.6, 0.1)
    return place(y, add(sat(thump(40, 1.0, 2.5, 0.3, 0.6), 2.5) * 1.2, flesh(0.6, 1.2, 1.6)), t)


@M('porco_explosao_gas', 'Porco Pestilento: morre e explode em gas toxico', espaco='abatedouro', mix=0.25, lufs=-13)
def _(v):
    y = np.zeros(ns(3.0))
    y = place(y, squeal(0.5, 1300) * 0.7, 0)
    y = place(y, add(splat(1.2, 2.0) * 1.3, sat(thump(45, 1.2, 2.0, 0.25, 0.5), 2), flesh(0.6, 2.0, 1.8)), 0.45)
    y = place(y, steam(2.0, 1800, 0.02, 0.8) * 0.8, 0.5)
    return place(y, lp(liquid(2.0, 25, 120, 400), 1200) * 0.6, 0.7)


# ======================================================== Acougueiro Oco
def masked_groan(d, f0=90):
    g = creature(d, f0, [(0, 0.9), (0.4, 1.1), (1, 0.85)], 'o', 'u', 'baixo', 0.7, 0.6, 0.4, 2.5, 0.3)
    return lp(g, 1400)  # abafado pela mascara de pano


@M('acougueiro_gemido', 'Acougueiro Oco: respiracao/gemido abafado pela mascara', var=2, lufs=-20, espaco='abatedouro', mix=0.25)
def _(v):
    return masked_groan(ru(1.4, 2.0), ru(80, 100))


@M('acougueiro_cutelo', 'Acougueiro Oco: golpe lento de cutelo', var=3, espaco='abatedouro', mix=0.2, lufs=-14)
def _(v):
    y = np.zeros((ns(1.2), 2))
    y = place(y, whoosh(0.6, 150, 1600, 1.0, 0.75, 0.6, -0.5, 0.4), 0)
    y = place(y, to_stereo(add(flesh(0.5, 1.2, 1.4), clang(900, 0.5, 1.2, 0.08, 0.6) * 0.4,
                               sat(thump(50, 0.6, 2, 0.15, 0.3), 2) * 0.8, crunch(0.2, 500, 600, 4000) * 0.6)), 0.45)
    return y


@M('acougueiro_afiar', 'Acougueiro Oco: para e afia a lamina (fica vulneravel)', espaco='abatedouro', mix=0.2, lufs=-17)
def _(v):
    y = np.zeros(ns(2.4))
    for i in range(4):
        d = 0.35
        sc = bp(white(d) * (1 + 2 * np.abs(lp(white(d), 150) * 8)), np.linspace(2500, 5500, ns(d)), 4)
        sc = add(sc * env_pts(d, [(0, 0), (0.05, 1), (0.3, 0.8), (d, 0)]), metal(d, 3200, 10, decay=0.1, bright=1.5) * 0.15)
        y = place(y, sc, 0.1 + i * 0.55)
    return y


@M('acougueiro_morte', 'Acougueiro Oco: cai como saco vazio, arame rangendo', espaco='abatedouro', mix=0.25)
def _(v):
    y = np.zeros(ns(2.0))
    y = place(y, masked_groan(0.9, 70), 0)
    y = place(y, creak(0.5, 60, 30, (900, 2100, 4200), 1.0) * 0.3, 0.3)  # arame
    y = place(y, clang(700, 0.8, 1.0, 0.2, 0.6) * 0.4, 0.9)  # cutelo cai
    return place(y, add(thump(55, 0.5, 0.8, 0.12, 0.3), cloth(0.4, 0.8)), 1.0)


# ======================================================== Capataz Gancho
@M('capataz_grito', 'Capataz Gancho: berro de alerta', espaco='abatedouro', mix=0.25, lufs=-14)
def _(v):
    return creature(1.2, 135, [(0, 0.9), (0.2, 1.25), (1, 0.9)], 'a', 'o', 'baixo', 0.95, 0.5, 0.3, 3, 0.2)


@M('capataz_gancho', 'Capataz Gancho: arremessa gancho na corrente e puxa o jogador', espaco='abatedouro', mix=0.2, lufs=-14)
def _(v):
    y = np.zeros((ns(1.8), 2))
    y = place(y, whoosh(0.35, 300, 2200, 1.2, 0.6, 0.6, -0.6, 0.6), 0)
    y = place(y, pan(chain(0.5, 70, 0, 1.3), np.linspace(-0.5, 0.5, ns(0.5))), 0.05)
    y = place(y, to_stereo(add(clang(800, 0.5, 1.2, 0.08, 0.8), flesh(0.4, 1.0, 1.0))), 0.4)
    y = place(y, pan(chain(0.8, 60, 1.0, 1.4), np.linspace(0.5, -0.5, ns(0.8))), 0.6)
    return place(y, to_stereo(creature(0.5, 120, [(0, 1), (1, 1.1)], 'a', 'a', 'baixo', 0.9, 0.6, 0.3, 3) * 0.6), 0.6)


@M('capataz_apito', 'Capataz Gancho: apito chamando Acougueiros (50% de vida)', espaco='abatedouro', mix=0.3, lufs=-15)
def _(v):
    y = np.zeros(ns(1.6))
    for at, d in [(0, 0.35), (0.45, 0.9)]:
        t = tt(d)
        f = 2900 * (1 + 0.05 * np.sign(np.sin(2 * np.pi * 28 * t)))  # trinado da bolinha
        s = sine(f, d) * 0.5 + bp(white(d), 2900, 4) * 0.3
        y = place(y, s * env_pts(d, [(0, 0), (0.02, 1), (d - 0.05, 1), (d, 0)]), at)
    return y


@M('capataz_morte', 'Capataz Gancho: morte (chaves e ganchos caindo)', espaco='abatedouro', mix=0.25)
def _(v):
    y = np.zeros(ns(2.4))
    y = place(y, creature(1.0, 110, [(0, 1.1), (1, 0.6)], 'a', 'u', 'baixo', 0.9, 0.7, 0.4, 2.5), 0)
    y = place(y, add(clang(600, 0.8, 1.0, 0.15, 0.6), clang(750, 0.7, 1.0, 0.12, 0.5) * 0.7), 0.9)
    y = place(y, chain(0.6, 50) * 0.6, 1.0)
    y = place(y, coins(0.6, 4) * 0.3, 1.05)  # chaves
    return place(y, add(sat(thump(45, 0.6, 1, 0.15, 0.4), 2), debris(0.5, 40, 300, 3000, 0.1)), 1.1)


# ======================================================== Joaquim, o Filho de Cardo
@M('joaquim_alerta', 'Joaquim, o Filho de Cardo: rugido que ainda tem voz de homem', espaco='abatedouro', mix=0.25, lufs=-14)
def _(v):
    d = 2.0
    beast = creature(d, 60, [(0, 0.8), (0.3, 1.2), (1, 0.8)], 'a', 'o', 'baixo', 0.6, 1.0, 0.8, 4, 0.5)
    man = creature(d, 150, [(0, 0.9), (0.3, 1.15), (1, 0.7)], 'a', 'o', 'tenor', 1.0, 0.2, 0, 1.5, 0.1, vib=0.01)
    return add(beast, man * 0.45)


@M('joaquim_ataque', 'Joaquim: patada / investida rapida', var=2, espaco='abatedouro', mix=0.2, lufs=-14)
def _(v):
    y = np.zeros((ns(1.0), 2))
    y = place(y, whoosh(0.35, 200, 1500, 1.0, 0.6, 0, -0.5, 0.5), 0)
    y = place(y, to_stereo(creature(0.4, 80, [(0, 1), (1, 1.2)], 'a', 'a', 'baixo', 0.7, 1.0, 0.5, 3) * 0.6), 0.0)
    return place(y, to_stereo(add(flesh(0.5, 1.0, 1.4), sat(thump(45, 0.6, 2, 0.15, 0.3), 2))), 0.25)


@M('joaquim_caldo', 'Joaquim: para perto do caldo derramado e cantarola triste', espaco='abatedouro', mix=0.3, lufs=-18)
def _(v):
    d = 3.0
    n = ns(d)
    notes = [hz('A3'), hz('C4'), hz('B3'), hz('G3')]
    f = np.repeat(notes, n // 4 + 1)[:n]
    f = lp(f, 6)  # deslizando entre as notas
    hum_ = formant(glottal(vibrato(f, d, 5, 0.01, 0.2), d, 0.015, 0.1, 0.2, 700), 'u', 'tenor', 1.0) * 2
    beast = creature(d, 55, [(0, 1), (1, 1)], 'u', 'u', 'baixo', 0.6, 0.5, 0.5, 2) * 0.3
    return add(hum_ * env_pts(d, [(0, 0), (0.3, 1), (2.5, 0.8), (d, 0)]), beast)


@M('joaquim_morte', 'Joaquim: morte (o bicho cala e sobra o suspiro do homem)', espaco='abatedouro', mix=0.3, lufs=-15)
def _(v):
    y = np.zeros(ns(3.5))
    y = place(y, creature(1.2, 55, [(0, 1.1), (1, 0.6)], 'a', 'u', 'baixo', 0.6, 1.0, 0.8, 3), 0)
    y = place(y, add(sat(thump(40, 0.8, 1.5, 0.25, 0.4), 2), debris(0.7, 40, 300, 3000, 0.2)), 1.0)
    y = place(y, breath(1.4, 'a', 'tenor', False, 0.5), 1.6)
    return place(y, lp(creature(1.0, 140, [(0, 1), (1, 0.8)], 'a', 'u', 'tenor', 1.0, 0.1, 0, 1.2, 0.3), 2000) * 0.4, 1.7)


# ======================================================== Patrulhas (humanos)
def shout(d=0.8, f0=170, vw='a', vw2='o', voz='tenor'):
    n = ns(d)
    f = f0 * np.interp(np.linspace(0, 1, n), [0, 0.2, 1], [0.9, 1.15, 0.85])
    src = glottal(f, d, 0.01, 0.12, 0.15, tilt=1500)
    y = formant(src, vw, voz, 1.0, vw2, np.linspace(0, 1, n)) * 2
    return blp(sat(y, 2.2), 6000) * env_pts(d, [(0, 0), (0.04, 1), (d * 0.7, 0.8), (d, 0)])


@M('fanatico_grito', 'Fanatico da Capela: grito chamando outros (Arautos)', var=2, lufs=-15)
def _(v):
    return add(shout(0.9, ru(170, 200), 'a', 'e'), shout(0.9, ru(170, 200) * 1.01, 'a', 'e') * 0.3)


@M('fanatico_morte', 'Fanatico da Capela: morte', var=2)
def _(v):
    y = np.zeros(ns(1.6))
    y = place(y, shout(0.7, 210, 'a', 'u') * np.linspace(1, 0.4, ns(0.7)), 0)
    return place(y, add(thump(60, 0.4, 0.8, 0.09, 0.2), cloth(0.4, 0.8), clang(700, 0.4, 1.0, 0.05, 0.3) * 0.2), 0.6)


@M('saqueador_grito', 'Saqueador da Vigilia: grito de alerta (atras do lenco)', var=2, lufs=-15)
def _(v):
    return lp(shout(0.7, ru(150, 175), 'e', 'a'), 3000)


@M('saqueador_frasco', 'Saqueador da Vigilia: joga frasco de agua benta (vidro + chiado sagrado)')
def _(v):
    y = np.zeros(ns(2.0))
    y = place(y, whoosh(0.4, 400, 2000, 1.0, 0.5, 0, -0.4, 0.4).mean(1) * 0.6, 0)
    y = place(y, add(glass(2600, 0.8), glass(1900, 0.9) * 0.7, debris(0.6, 250, 2000, 9000, 0.15)), 0.4)
    y = place(y, steam(1.0, 4500, 0.01, 0.4) * 0.7, 0.42)
    return place(y, bell(hz('E6'), 1.0, 0.5, 1.3) * 0.2, 0.42)


@M('saqueador_morte', 'Saqueador da Vigilia: morte', var=2)
def _(v):
    y = np.zeros(ns(1.6))
    y = place(y, lp(shout(0.6, 180, 'a', 'u'), 3000) * np.linspace(1, 0.4, ns(0.6)), 0)
    return place(y, add(thump(60, 0.4, 0.8, 0.09, 0.2), chain(0.3, 30) * 0.4, debris(0.4, 40, 300, 3000, 0.1)), 0.55)


# ======================================================== Larva de Carne
@M('larva_rastejar', 'Larva de Carne: rastejando (loop curto, molhado)', lufs=-21, espaco='cripta', mix=0.2, loop=True)
def _(v):
    d = 3.0
    y = lp(white(d) * (1 + 3 * np.abs(lp(white(d), 3) * 20)), 900) * 0.6
    t = 0.0
    while t < 2.7:
        y = place(y, flesh(0.3, 1.3, 1.2) * 0.3, t)
        t += ru(0.35, 0.6)
    return y[:ns(d)]


@M('larva_cuspe', 'Larva de Carne: cospe acido', var=2, espaco='cripta', mix=0.2)
def _(v):
    y = np.zeros(ns(1.4))
    y = place(y, creature(0.3, 160, [(0, 0.8), (1, 1.3)], 'u', 'a', 'tenor', 1.0, 1.0, 0.2, 3) * 0.5, 0)
    y = place(y, splat(0.4, 0.8), 0.25)
    return place(y, add(steam(0.9, 4000, 0.01, 0.3) * 0.6, liquid(0.6, 30, 400, 1000) * 0.4), 0.3)


@M('larva_morte_divide', 'Larva de Carne: morre e se divide em duas', espaco='cripta', mix=0.25, lufs=-14)
def _(v):
    y = np.zeros(ns(2.0))
    y = place(y, creature(0.6, 140, [(0, 1.2), (1, 0.6)], 'i', 'u', 'tenor', 1.0, 1.0, 0.2, 3) * 0.6, 0)
    y = place(y, add(flesh(0.7, 2.0, 1.6), splat(0.8, 1.5)), 0.3)
    y = place(y, crunch(0.3, 300, 400, 2000) * 0.4, 0.5)
    for i in range(2):
        y = place(y, flesh(0.3, 1.5, 0.6) * 0.6, 0.9 + i * 0.25)
    return y


# ======================================================== Gancheiro
@M('gancheiro_chicote', 'Gancheiro: corrente em arco como chicote', var=2, espaco='abatedouro', mix=0.2, lufs=-15)
def _(v):
    y = np.zeros((ns(1.2), 2))
    y = place(y, whoosh(0.45, 250, 2400, 1.1, 0.7, 0, -0.7, 0.7), 0)
    y = place(y, pan(chain(0.6, 80, 0, 1.2), np.linspace(-0.6, 0.6, ns(0.6))), 0.0)
    y = place(y, to_stereo(add(hp(white(0.05), 2500) * env_exp(0.05, 0.003) * 1.5, clang(1000, 0.4, 1.3, 0.06, 0.5) * 0.5,
                               flesh(0.3, 0.6, 0.8) * 0.6)), 0.32)
    return y


@M('gancheiro_cai_teto', 'Gancheiro: solta do teto e cai em cima do jogador', espaco='cripta', mix=0.25, lufs=-13)
def _(v):
    y = np.zeros(ns(1.8))
    y = place(y, chain(0.6, 60, 0.4, 1.2), 0)
    y = place(y, whoosh(0.4, 150, 1000, 0.8, 0.85, 0, 0, 0).mean(1), 0.3)
    return place(y, add(sat(thump(42, 1.0, 2, 0.25, 0.5), 2) * 1.2, flesh(0.6, 1.2, 1.5), chain(0.8, 60, 0.2, 1.2) * 0.6,
                        debris(0.8, 50, 300, 3000, 0.2) * 0.6), 0.7)


@M('gancheiro_gemido', 'Gancheiro: gemido de dor e corrente balancando', var=2, lufs=-19, espaco='cripta', mix=0.3)
def _(v):
    return add(moan(1.8, ru(90, 110)) * 0.8, chain(1.8, 8, 0.2) * 0.4)


@M('gancheiro_morte', 'Gancheiro: morte', espaco='cripta', mix=0.25)
def _(v):
    y = np.zeros(ns(2.0))
    y = place(y, creature(0.8, 100, [(0, 1.1), (1, 0.6)], 'a', 'u', 'baixo', 0.8, 0.8, 0.3, 2), 0)
    return place(y, add(chain(1.0, 50, 0.6, 1.3), thump(55, 0.5, 0.8, 0.1, 0.3)), 0.6)


# ======================================================== Monge Emparedado
@M('monge_sai_parede', 'Monge Emparedado: sai da parede (tijolos e argamassa caindo)', espaco='ossario', mix=0.3, lufs=-14)
def _(v):
    y = np.zeros(ns(2.5))
    y = place(y, crunch(0.8, 300, 200, 2500, 4), 0)
    for i in range(7):
        y = place(y, add(wood_knock(ru(140, 260), 0.3) * 1.2, thump(ru(70, 100), 0.3, 0.5, 0.05, 0.4) * 0.6), ru(0.2, 1.4))
    y = place(y, debris(2.0, 100, 300, 5000, 0.6), 0.1)
    return place(y, moan(1.2, 85) * 0.5, 1.0)


@M('monge_terco', 'Monge Emparedado: golpe de terco (contas de osso) que silencia', var=2, espaco='ossario', mix=0.25)
def _(v):
    y = np.zeros((ns(1.2), 2))
    y = place(y, whoosh(0.35, 400, 2400, 1.2, 0.6, 0, -0.5, 0.5), 0)
    y = place(y, to_stereo(add(bones_rattle(0.4, 80), flesh(0.3, 0.4, 0.8) * 0.6)), 0.25)
    sh = bp(white(0.6), 3500, 1.2) * env_pts(0.6, [(0, 0), (0.05, 1), (0.6, 0)]) * 0.3
    return place(y, to_stereo(sh), 0.3)


@M('monge_canto', 'Monge Emparedado: murmurio de reza em loop (ocioso)', lufs=-22, espaco='ossario', mix=0.4, loop=True)
def _(v):
    d = 4.0
    n = ns(d)
    f = np.full(n, hz('D3'))
    f[n // 2:] = hz('C3')
    f = lp(f, 5)
    vows = [('a', 'e'), ('o', 'u'), ('e', 'i'), ('u', 'o')]
    y = np.zeros(n)
    seg = n // 8
    src = glottal(vibrato(f, d, 4, 0.004, 0.3), d, 0.006, 0.06, 0.4, 700)
    for k in range(8):
        a, b = vows[k % 4]
        s = src[k * seg:(k + 1) * seg]
        y[k * seg:k * seg + len(s)] = formant(s, a, 'baixo', 0.95, b, np.linspace(0, 1, len(s))) * \
            env_pts(len(s) / SR, [(0, 0.3), (0.05, 1), (len(s) / SR - 0.05, 1), (len(s) / SR, 0.3)])
    return lp(y * 2, 2200)


@M('monge_morte', 'Monge Emparedado: ossos desmontando no chao', espaco='ossario', mix=0.3)
def _(v):
    y = np.zeros(ns(2.0))
    y = place(y, bones_rattle(1.2, 50), 0)
    y = place(y, crunch(0.4, 500, 500, 4000, 1.5), 0)
    return place(y, add(cloth(0.5, 0.6), thump(70, 0.4, 0.5, 0.08, 0.3) * 0.6), 0.8)


# ======================================================== Carpideira de Ossos
def keen(d, f0=hz('D5'), vib=0.025):
    n = ns(d)
    f = vibrato(f0 * np.interp(np.linspace(0, 1, n), [0, 0.3, 0.7, 1], [0.94, 1.0, 1.06, 0.9]), d, 5.5, vib, 0.2)
    src = glottal(f, d, 0.006, 0.06, 0.3, tilt=1800)
    y = formant(src, 'o', 'soprano', 1.0, 'a', np.linspace(0, 1, n)) * 2
    return y * env_pts(d, [(0, 0), (0.3, 1), (d - 0.4, 0.9), (d, 0)])


@M('carpideira_canto', 'Carpideira de Ossos: canto de lamento que cura os mortos (loop curto)', lufs=-18, espaco='ossario', mix=0.4, loop=True)
def _(v):
    y = np.zeros(ns(4.0))
    for i, nt in enumerate(['D5', 'F5', 'E5', 'C5']):
        y = place(y, keen(1.1, hz(nt)), i * 0.95)
    return y


@M('carpideira_grito', 'Carpideira de Ossos: grito de morte que causa medo', espaco='ossario', mix=0.35, lufs=-13)
def _(v):
    y = np.zeros(ns(2.4))
    y = place(y, add(scream(1.6, 820, 'a', 'soprano', 3, 0.04), scream(1.6, 870, 'e', 'soprano', 3, 0.05) * 0.6), 0)
    return place(y, bones_rattle(0.8, 60) * 0.6, 1.3)


@M('carpideira_ataque', 'Carpideira de Ossos: arranhao', var=2, espaco='ossario', mix=0.25)
def _(v):
    y = np.zeros((ns(0.9), 2))
    y = place(y, whoosh(0.25, 600, 3500, 1.6, 0.5, 0.2, 0.4, -0.4), 0)
    y = place(y, to_stereo(keen(0.35, hz('A5'), 0.05) * 0.4), 0)
    return place(y, to_stereo(add(flesh(0.3, 0.6, 0.7), bones_rattle(0.2, 60) * 0.5)), 0.18)


# ======================================================== Fogo-de-Vela
@M('fogo_vela_crepitar', 'Fogo-de-Vela: crepitar com risinho derretido (loop)', lufs=-22, espaco='ossario', mix=0.25, loop=True)
def _(v):
    d = 4.0
    y = fire(d, 0.6, 30)
    y = lp(y, 5000)
    for i in range(3):
        g = creature(0.4, ru(380, 450), [(0, 1), (1, 0.8)], 'i', 'e', 'soprano', 1.0, 0.5, 0, 2, 0.6)
        g = g * (1 + np.sign(np.sin(2 * np.pi * 9 * tt(0.4)))) * 0.5  # "hi-hi-hi"
        y = place(y, g * 0.25, ru(0.2, 3.3))
    return y[:ns(d)]


@M('fogo_vela_explosao', 'Fogo-de-Vela: explode em fogo ao tocar o jogador', var=2, espaco='ossario', mix=0.25, lufs=-13)
def _(v):
    y = add(whoomp(1.2, 70) * 1.3, sat(thump(55, 0.8, 1.5, 0.15, 0.5), 2) * 0.7)
    return add(y, splat(0.5, 0.6) * 0.3)


@M('fogo_vela_apaga', 'Fogo-de-Vela: morre (sopro e chama apagando)', espaco='ossario', mix=0.3)
def _(v):
    d = 1.2
    y = bp(white(d), np.linspace(1200, 300, ns(d)), 1.0) * env_pts(d, [(0, 0), (0.05, 1), (d, 0)]) * 1.2
    return add(y, steam(0.6, 4000, 0.01, 0.2) * 0.4, creature(0.5, 420, [(0, 1), (1, 0.4)], 'i', 'u', 'soprano', 1.0, 0.3, 0, 1.5, 0.5) * 0.3)


# ======================================================== Querubim Desfeito
def music_box(notes, step=0.16, detune=0.012):
    y = np.zeros(ns(step * len(notes) + 1.5))
    for i, nt in enumerate(notes):
        f = hz(nt) * (1 + R().normal(0, detune))
        tone = modal(1.2, [f, f * 3.9, f * 9.1], [0.6, 0.15, 0.05], [1, 0.3, 0.1])
        y = place(y, tone * ru(0.6, 1), i * step * ru(0.9, 1.15))
    return y


@M('querubim_voo', 'Querubim Desfeito: asas de ferro batendo (loop de voo)', lufs=-20, espaco='catedral', mix=0.2, loop=True)
def _(v):
    d = 3.0
    y = np.zeros(ns(d))
    t = 0.0
    while t < d - 0.3:
        flap = add(wings(0.25, 1, 0.4, 0.2), metal(0.25, ru(500, 650), 12, decay=0.08, bright=1.0) * 0.3,
                   chain(0.2, 40) * 0.2)
        y = place(y, flap, t)
        t += ru(0.17, 0.22)
    return y[:ns(d)]


@M('querubim_risada', 'Querubim Desfeito: caixinha de musica desafinada (alerta)', var=2, espaco='catedral', mix=0.35, lufs=-17)
def _(v):
    nots = [['E6', 'G6', 'B6', 'C7', 'B6', 'G6', 'F#6'], ['A5', 'C6', 'E6', 'D#6', 'E6', 'B5']][v]
    y = music_box(nots, 0.14, 0.02)
    return varispeed(y, np.linspace(1.0, 0.85, len(y)))


@M('querubim_ataque', 'Querubim Desfeito: unhas de prego arranhando', var=2, espaco='catedral', mix=0.2)
def _(v):
    y = np.zeros((ns(0.8), 2))
    y = place(y, whoosh(0.25, 800, 4500, 2, 0.5, 0.5, -0.5, 0.5), 0)
    sc = bp(white(0.3) * (1 + 3 * np.abs(lp(white(0.3), 200) * 8)), 5000, 3) * env_exp(0.3, 0.1)
    return place(y, to_stereo(add(sc, flesh(0.25, 0.4, 0.6) * 0.6, glass(4200, 0.3) * 0.2)), 0.15)


@M('querubim_quebra', 'Querubim Desfeito: porcelana quebra em pedacos', var=2, espaco='catedral', mix=0.3, lufs=-14)
def _(v):
    y = np.zeros(ns(2.0))
    for i in range(5):
        y = place(y, glass(ru(1800, 4200), 0.8) * ru(0.4, 0.9), ru(0, 0.06))
    y = place(y, debris(1.6, 200, 1500, 9000, 0.4), 0.01)
    y = place(y, clang(500, 0.6, 1.0, 0.12, 0.4) * 0.5, 0.2)  # asa de ferro cai
    return place(y, music_box(['C6', 'B5'], 0.2, 0.04) * 0.3, 0.3)


@M('querubim_remonta', 'Querubim Desfeito: pedacos se arrastando e encaixando de volta', espaco='catedral', mix=0.3)
def _(v):
    y = reverse(debris(1.6, 120, 1500, 8000, 0.7))
    y = place(np.zeros(ns(2.4)), y, 0)
    for i in range(6):
        y = place(y, glass(ru(2500, 4500), 0.25) * 0.4, 1.0 + i * 0.12)
    return place(y, music_box(['G6', 'C7'], 0.12, 0.01) * 0.3, 1.8)


# ======================================================== Eco da Trombeta
@M('eco_presenca', 'Eco da Trombeta: brilho distorcido quando chega perto (loop)', lufs=-22, espaco='catedral', mix=0.4, loop=True)
def _(v):
    d = 4.0
    t = tt(d)
    y = 0
    for f in (hz('D5'), hz('A5'), hz('D6')):
        y = y + sine(f * (1 + 0.004 * np.sin(2 * np.pi * ru(0.2, 0.5) * t)), d) * 0.2
    y = y * (0.6 + 0.4 * np.sin(2 * np.pi * 0.5 * t))
    y = add(y, bp(white(d), 6000, 3) * 0.1)
    return widen(y, 0.7)


@M('eco_grito', 'Eco da Trombeta: grito que empurra e atordoa', var=2, espaco='catedral', mix=0.3, lufs=-12)
def _(v):
    d = 1.6
    f = hz('D4')
    tr = brass(f * np.interp(np.linspace(0, 1, ns(d)), [0, 0.1, 1], [0.8, 1.0, 0.9]), d, 0.03, 0.6, 1.4, 1.0, 3)
    sc = scream(d, 600, 'a', 'alto', 2.5, 0.03)
    y = add(blp(tr, 5000) * 0.8, sc * 0.5)
    y = add(y, sat(thump(45, 1.0, 1.5, 0.3, 0.3), 2) * 0.7)
    return add(y, whoosh(1.0, 200, 1500, 0.7, 0.15, 0, 0, 0).mean(1) * 0.8)


@M('eco_morte', 'Eco da Trombeta: se desfaz como onda de calor', espaco='catedral', mix=0.4)
def _(v):
    d = 2.0
    t = tt(d)
    y = 0
    for f in (hz('D5'), hz('A5'), hz('D6')):
        y = y + sine(f * (1 - 0.3 * t / d), d) * 0.2
    y = y * env_exp(d, 0.6)
    return add(y, reverse(bp(white(d), 5000, 2) * env_exp(d, 0.4)) * 0.4)
