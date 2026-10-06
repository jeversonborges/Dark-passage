"""Area inicial como deserto radioativo (direcao do Jefin, 2026-10-04).

Substitui os ambientes externos da area inicial: vento com areia, contador Geiger,
metal de estrutura rangendo, estatica de radio e predios cedendo ao longe.
"""
from kit import *  # noqa
from registro import som
from ambiente import A, O, DUR, XF, bed, far, scatter, murmur
from sfx_monstros import caw, moan


# ======================================================== camadas
def sand_wind(d, strength=1.0, center=600, gust=0.07):
    """Vento de deserto: sopro largo e escuro + areia chicoteando (graos) nas rajadas."""
    out = []
    for c in range(2):
        g = slow(d, gust)
        g = (g - g.min()) / (np.ptp(g) + 1e-9)
        body = bp(pink(d), center * (0.6 + 0.8 * g), 0.7) * (0.3 + 0.7 * g)
        body += lp(brown(d), 140) * (0.4 + 0.6 * g) * 0.7
        gr = np.abs(lp(white(d), 260)) * 9
        grains = bbp(white(d), 1800, 5500) * gr ** 3 * g ** 2 * 0.05  # graos batendo
        moan_ = bp(white(d), center * 1.8 * (0.8 + 0.4 * g), 22) * g ** 3 * 0.5  # assobio em fresta de concreto
        out.append(blp(body + grains + moan_, 6000, 2) * strength)
    return np.stack(out, 1)


def geiger(d, rate_base=1.5, rate_peak=25, burst=0.12):
    """Contador Geiger: cliques Poisson com taxa que sobe em picos de radiacao."""
    n = ns(d)
    r = slow(d, burst)
    r = (r - r.min()) / (np.ptp(r) + 1e-9)
    rate = rate_base + (rate_peak - rate_base) * r ** 4
    p = rate / SR
    hits = R().uniform(size=n) < p
    y = np.zeros(n)
    y[hits] = R().uniform(0.6, 1.0, hits.sum())
    click = np.exp(-np.arange(ns(0.004)) / (0.0006 * SR)) * np.sin(2 * np.pi * 3200 * np.arange(ns(0.004)) / SR)
    y = np.convolve(y, click)[:n] + bp(np.convolve(y, np.ones(8))[:n], 1800, 2) * 0.3
    return y * 0.5


def radio(d, voice=0.6, tones=0.5):
    """Radio de ondas curtas: estatica, assobios de sintonia e vozes picotadas."""
    n = ns(d)
    st = bbp(white(d), 400, 4000) * (0.5 + 0.5 * np.clip(slow(d, 0.8), -1, 1)) * 0.5
    st += bbp(crackle(d, 200, 0.0008), 800, 5000) * 0.4
    tune = sine(np.clip(900 + 700 * slow(d, 0.4), 150, 3000), d) * np.clip(slow(d, 0.3), 0, 1) * 0.12 * tones
    y = st + tune
    if voice:
        t = ru(0.2, 1.0)
        while t < d - 1:
            ph = ru(0.6, 1.8)
            m = ns(ph)
            f0 = ru(110, 160) * (1 + 0.15 * slow(ph, 5))
            src = glottal(f0, ph, 0.01, 0.1, 0.2, 900)
            s = formant(src, R().choice(list('aeo')), 'tenor', 1.0, R().choice(list('iou')), np.abs(np.sin(np.linspace(0, ru(8, 16), m))))
            s *= np.clip(np.sin(np.linspace(0, ru(12, 26), m)) * 2, 0, 1)
            s = bbp(s, 400, 2800, 3)  # banda de radio AM
            s *= np.clip(slow(ph, 18) * 3 + 1.2, 0, 1)  # sinal caindo e voltando
            y = place(y, s * voice * 1.4, t)[:n]
            t += ph + ru(0.6, 3.0)
    return blp(sat(y * 1.3, 1.5), 4500, 2) * 0.6


def structure_groan(d=None):
    """Viga/predio de metal rangendo com o vento: atrito lento num corpo metalico grande."""
    d = d or ru(2.0, 4.0)
    n = ns(d)
    f = np.interp(np.arange(n), [0, n * 0.4, n], [ru(25, 40), ru(55, 80), ru(30, 45)]) * (1 + 0.15 * slow(d, 6))
    pulses = np.maximum(saw(f, d), 0.55) - 0.55
    pulses *= 1 + 2 * np.abs(slow(d, 12))
    modes = [ru(90, 120), ru(210, 260), ru(380, 450), ru(640, 720), ru(1050, 1250)]
    y = resonate(pulses, modes, [30, 40, 45, 50, 50], [1.0, 0.8, 0.5, 0.3, 0.15])
    y = sat(y * 3, 1.5) * 0.4
    return blp(y, 3000) * env_pts(d, [(0, 0), (d * 0.3, 1), (d * 0.7, 0.8), (d, 0)])


def collapse(d=5.0):
    """Predio cedendo ao longe: rangido, estalo, avalanche de concreto e poeira."""
    y = np.zeros(ns(d))
    y = place(y, structure_groan(1.5) * 0.8, 0)
    y = place(y, add(crunch(0.5, 300, 200, 2500, 4), clang(ru(120, 200), 1.5, 0.8, 0.6, 0.6) * 0.5), 1.3)
    y = place(y, add(rumble(3.0, 50, 1.5) * env_pts(3.0, [(0, 0), (0.2, 1), (3.0, 0)]),
                     debris(3.0, 120, 150, 3000, 1.0) * 1.2), 1.4)
    for i in range(6):
        y = place(y, clang(ru(200, 500), 1.0, 0.9, 0.3, 0.4) * 0.3, 1.6 + ru(0, 1.8))
    return y


def sheet_flap(d=None):
    """Chapa de zinco solta batendo no vento."""
    d = d or ru(1.0, 2.0)
    y = np.zeros(ns(d))
    t = 0.0
    while t < d - 0.2:
        y = place(y, add(clang(ru(180, 260), 0.4, 0.8, 0.12, 0.3), wood_knock(ru(90, 130), 0.2) * 0.5) * ru(0.3, 0.8), t)
        t += ru(0.12, 0.45)
    return y


# ======================================================== loops (substituem os antigos)
@A('noite_vento', 'Deserto radioativo (generico): vento com areia, Geiger baixo, metal rangendo ao longe', espaco='rua', mix=0.2)
def _(v):
    d = DUR + XF
    y = sand_wind(d, 1.0, 550)
    y = add(y, pan(geiger(d, 0.8, 10), 0.35) * 0.18)
    y = scatter(y, 5, lambda: far(structure_groan(), 2500, 0.4, 'rua', ru(-0.9, 0.9)), (0.2, 0.4))
    return loopify(y, XF)


@A('campos_cinza', 'Campos de Cinza (deserto radioativo): dunas abertas, rajadas de areia, Geiger com picos, carcacas de carro rangendo, corvos', espaco='rua', mix=0.2)
def _(v):
    d = DUR + XF
    y = sand_wind(d, 1.2, 650, 0.09)
    y = add(y, pan(geiger(d, 1.0, 30, 0.1), 0.3) * 0.25)
    y = scatter(y, 6, lambda: far(structure_groan(), 3000, 0.3, 'rua', ru(-0.9, 0.9)), (0.2, 0.35))
    y = scatter(y, 4, lambda: far(sheet_flap(), 4000, 0.3, 'rua', ru(-0.9, 0.9)), (0.1, 0.2))
    y = scatter(y, 5, lambda: far(caw(ru(0.25, 0.4), ru(480, 600)), 2500, 0.4, 'rua', ru(-0.9, 0.9)), (0.06, 0.12))
    return loopify(y, XF)


@A('vala_comum', 'A Vala (deserto radioativo): cratera de concreto, vento baixo, moscas, Geiger alto, caes ao longe', espaco='rua', mix=0.25)
def _(v):
    from ambiente import flies
    d = DUR + XF
    y = sand_wind(d, 0.6, 380)
    y = add(y, flies(d, 3) * 0.4, pan(geiger(d, 4, 45, 0.15), -0.2) * 0.3)
    y = scatter(y, 8, lambda: debris(ru(0.5, 1.5), 40, 200, 2500, 0.4) * 0.4, (0.1, 0.25))
    y = scatter(y, 4, lambda: far(creature(1.5, 65, [(0, 1), (1, 1)], 'u', 'o', 'baixo', 0.9, 1.0, 0.3, 2.5), 1200, 0.4, 'rua', ru(-0.9, 0.9)), (0.08, 0.15))
    return loopify(y, XF)


@A('cemiterio', 'Cemiterio de Sao Lazaro (deserto radioativo): lapides meio enterradas na areia, vento, lamentos da fila, sino rachado ao longe', espaco='rua', mix=0.25)
def _(v):
    d = DUR + XF
    y = sand_wind(d, 0.85, 480, 0.07)
    y = add(y, pan(geiger(d, 1.2, 15), 0.4) * 0.15)
    t = ru(3, 8)
    while t < d - 6:
        y = place(y, far(bell(hz('C#3'), 6, 4, 0.8), 1200, 0.6, 'catedral', 0.5) * 0.3, t)
        t += ru(16, 24)
    y = scatter(y, 6, lambda: far(moan(ru(2.0, 3.0), ru(95, 125)), 1600, 0.5, 'cripta', ru(-0.9, 0.9)), (0.12, 0.25))
    y = scatter(y, 4, lambda: far(structure_groan(), 2500, 0.4, 'rua', ru(-0.9, 0.9)), (0.15, 0.3))
    return loopify(y, XF)


@A('acampamento_vela', 'Acampamento da Vela (deserto radioativo): lampada de arco, fogueiras, radio de ondas curtas, forja, conversa baixa, areia batendo nas lonas', espaco='rua', mix=0.25)
def _(v):
    d = DUR + XF
    y = sand_wind(d, 0.5, 420)
    arc = hum(d, 60, 12, 0.0005) * 0.25 + bp(white(d), 3000, 1) * 0.03
    y = add(y, pan(arc, 0.15) * 0.8)
    y = add(y, pan(fire(d, 0.45, 18), -0.5), pan(fire(d, 0.3, 14), 0.6) * 0.7)
    y = add(y, murmur(d, 4) * 0.5, pan(far(radio(d, 0.6, 0.5), 5000, 0.15, 'quarto'), 0.55) * 0.5)
    y = add(y, pan(geiger(d, 0.6, 6), -0.3) * 0.1)
    t = ru(2, 6)
    while t < d - 4:
        for k in range(int(ru(3, 7))):
            y = place(y, far(anvil(ru(1000, 1200), 1.0), 3500, 0.35, 'rua', -0.6) * 0.18, t + k * ru(0.55, 0.7))
        t += ru(9, 16)
    y = scatter(y, 4, lambda: far(sheet_flap(), 5000, 0.2, 'rua', ru(-0.9, 0.9)), (0.08, 0.15))
    return loopify(y, XF)


@A('ruinas_cidade', 'Ruinas da cidade: predios quebrados, vigas rangendo, vidro e concreto caindo, radio perdido, Geiger', espaco='rua', mix=0.3)
def _(v):
    d = DUR + XF
    y = sand_wind(d, 0.9, 520, 0.08)
    y = add(y, pan(geiger(d, 1.5, 28, 0.1), 0.25) * 0.22)
    y = scatter(y, 8, lambda: far(structure_groan(), 2500, 0.45, 'abatedouro', ru(-0.9, 0.9)), (0.25, 0.45))
    y = scatter(y, 5, lambda: far(sheet_flap(), 4000, 0.3, 'rua', ru(-0.9, 0.9)), (0.1, 0.2))
    y = scatter(y, 6, lambda: add(debris(ru(0.6, 1.4), 60, 300, 5000, 0.4), glass(ru(2500, 4000), 0.5) * 0.3) * 0.5, (0.1, 0.25))
    y = scatter(y, 1, lambda: far(collapse(6.0), 1800, 0.5, 'catedral', ru(-0.7, 0.7)), (0.35, 0.45), margin=8)
    y = scatter(y, 2, lambda: far(radio(ru(4, 7), 0.5, 0.6), 3500, 0.4, 'abatedouro', ru(-0.8, 0.8)), (0.15, 0.25), margin=8)
    return loopify(y, XF)


# ======================================================== pontuais
@O('geiger_pico', 'Contador Geiger disparando (perto de fonte radioativa)', var=2, espaco=None, lufs=-20)
def _(v):
    d = 3.0
    g = geiger(d, 20, 120, 0.8)
    return g * env_pts(d, [(0, 0.3), (1.0, 1), (2.2, 1), (d, 0)])


@O('radio_estatica', 'Radio de ondas curtas chiando com vozes picotadas', var=3, espaco='quarto', mix=0.2)
def _(v):
    d = ru(4, 6)
    return radio(d, 0.7, 0.6) * env_pts(d, [(0, 0), (0.15, 1), (d - 0.6, 1), (d, 0)])


@O('predio_cede', 'Predio desabando ao longe', var=2, espaco='catedral', mix=0.5, lufs=-17)
def _(v):
    return blp(collapse(6.0), 2500)


@O('estrutura_range', 'Viga de metal rangendo no vento', var=3, espaco='abatedouro', mix=0.4)
def _(v):
    return structure_groan()


@O('rajada_areia', 'Rajada forte de areia passando', var=2, espaco='rua', mix=0.2, lufs=-18)
def _(v):
    d = 4.0
    w = sand_wind(d, 1.0, 700, 0.5)
    return w * env_pts(d, [(0, 0), (1.2, 1), (2.4, 0.8), (d, 0)])[:, None]


@O('chapa_batendo', 'Chapa de zinco solta batendo no vento', var=2, espaco='rua', mix=0.3)
def _(v):
    return sheet_flap(ru(2.0, 3.0))


@O('sirene_distante', 'Sirene antiaerea velha girando ao longe', espaco='catedral', mix=0.6, lufs=-19)
def _(v):
    d = 9.0
    f = 300 + 350 * env_pts(d, [(0, 0), (3, 1), (6, 1), (d, 0)], 1.5)
    s = sat(saw(f, d) * 0.4 + square(f * 1.005, d) * 0.3, 1.5) * env_pts(d, [(0, 0), (2, 1), (7, 0.8), (d, 0)])
    return blp(s, 2000)


# ======================================================== zonas do mapa (design/mapas/area_inicial.json)
def mud_bubbles(d, rate=1.5):
    """Lama amarga borbulhando: bolhas grossas e estalos molhados."""
    y = np.zeros(ns(d))
    t = ru(0, 1)
    while t < d - 1:
        b = ru(0.15, 0.4)
        f = ru(90, 220)
        bub = sine(f * np.linspace(1, 1.8, ns(b)), b) * env_pts(b, [(0, 0), (0.01, 1), (b, 0)], 2)
        bub = add(bub, bp(white(0.05), ru(300, 700), 3) * 0.4 * ru(0, 1))
        y = place(y, bub * ru(0.2, 0.7), t)
        t += R().exponential(1 / rate)
    return lp(y, 1500)


def frogs(d, k=2):
    """Sapos mutantes: coaxar grave e torto, em grupos."""
    y = bed(d)
    for i in range(k):
        t = ru(0, 4)
        p = ru(-0.8, 0.8)
        f0 = ru(55, 90)
        while t < d - 2:
            for c in range(int(ru(2, 6))):
                c_d = ru(0.18, 0.32)
                src = glottal(f0 * (1 + 0.3 * np.linspace(0, 1, ns(c_d))), c_d, 0.02, 0.2, 0.1, 500)
                s = formant(src, 'o', 'baixo', 0.8, 'a', np.linspace(0, 1, ns(c_d))) * env_pts(c_d, [(0, 0), (0.02, 1), (c_d, 0)])
                s *= 1 + 0.8 * np.sin(2 * np.pi * ru(25, 40) * tt(c_d))  # ronco
                y = place(y, pan(blp(s, 1800), p) * 0.5, t)
                t += c_d + ru(0.05, 0.2)
            t += ru(3, 9)
    return y[:ns(d)]


def thistles(d, amt=1.0):
    """Cardos e espinhos secos chacoalhando no vento."""
    g = slow(d, 0.2)
    g = (g - g.min()) / (np.ptp(g) + 1e-9)
    out = []
    for c in range(2):
        gr = np.abs(lp(white(d), 60)) * 14
        rustle = bbp(white(d), 1500, 6000) * gr ** 2 * (0.2 + g) * 0.04
        out.append(blp(rustle, 7000, 2) * amt)
    return np.stack(out, 1)


def owl(f0=None):
    f0 = f0 or ru(330, 400)
    y = np.zeros(ns(2.0))
    for k, (at, dd) in enumerate([(0, 0.25), (0.45, 0.6), (1.2, 0.35)]):
        f = f0 * (1 + 0.04 * np.sin(np.linspace(0, np.pi, ns(dd))))
        s = (sine(f, dd) + 0.1 * sine(f * 2, dd) + bp(white(dd), f0, 6) * 0.15) * env_pts(dd, [(0, 0), (0.05, 1), (dd, 0)], 1.4)
        y = place(y, s, at)
    return y


@A('bairro_afogado', 'Bairro Afogado: telhados saindo da areia, vento assobiando nas chamines, telhas e calhas batendo, radio esquecido num sotao', espaco='rua', mix=0.3)
def _(v):
    d = DUR + XF
    y = sand_wind(d, 0.9, 500, 0.08)
    for i in range(2):  # chamines assobiando
        f = ru(380, 700)
        g = np.clip(slow(d, 0.06) * 1.5, 0, 1) ** 2
        y = add(y, pan(bp(pink(d), f * (1 + 0.03 * slow(d, 0.3)), 30) * g * 1.2, ru(-0.7, 0.7)))
    y = scatter(y, 5, lambda: far(sheet_flap(), 4000, 0.3, 'rua', ru(-0.9, 0.9)), (0.1, 0.2))
    y = scatter(y, 5, lambda: far(structure_groan(), 2500, 0.4, 'abatedouro', ru(-0.9, 0.9)), (0.15, 0.3))
    y = scatter(y, 6, lambda: debris(ru(0.4, 1.0), 40, 300, 4000, 0.3) * 0.4, (0.08, 0.18))
    y = scatter(y, 3, lambda: far(caw(ru(0.25, 0.4), ru(480, 600)), 2500, 0.4, 'rua', ru(-0.9, 0.9)), (0.05, 0.1))
    y = scatter(y, 1, lambda: far(radio(ru(5, 7), 0.6, 0.6), 2500, 0.5, 'quarto', ru(-0.6, 0.6)), (0.12, 0.18), margin=8)
    y = add(y, pan(geiger(d, 1.0, 14), 0.3) * 0.15)
    return loopify(y, XF)


@A('rio_amargo', 'Rio Amargo (o Jordao seco): lama borbulhando, sapos mutantes, moscas, vento baixo no leito rachado, Geiger alto', espaco='rua', mix=0.25)
def _(v):
    from ambiente import flies
    d = DUR + XF
    y = sand_wind(d, 0.5, 350)
    y = add(y, pan(mud_bubbles(d, 2.0), -0.3) * 0.5, pan(mud_bubbles(d, 1.4), 0.4) * 0.4)
    y = add(y, frogs(d, 3) * 0.7, flies(d, 2) * 0.3, pan(geiger(d, 3, 40, 0.12), 0.2) * 0.25)
    y = scatter(y, 3, lambda: far(structure_groan(), 2500, 0.4, 'rua', ru(-0.9, 0.9)), (0.1, 0.2))
    return loopify(y, XF)


@A('rio_lama', 'Linha do rio (emissor ao longo do leito): lama amarga borbulhando e escorrendo', espaco='rua', mix=0.15, lufs=-22)
def _(v):
    d = DUR + XF
    y = add(pan(mud_bubbles(d, 3.0), -0.3), pan(mud_bubbles(d, 2.5), 0.3) * 0.8)
    ooze = np.stack([lp(brown(d), 300) * (0.5 + 0.5 * np.clip(slow(d, 0.2) + 0.5, 0, 1)) for _ in range(2)], 1) * 0.3
    return loopify(add(y, ooze), XF)


@A('mata_cardos', 'Mata dos Cardos: vento nos espinhos, cardos secos chacoalhando, mariposas, corvos', espaco='rua', mix=0.2)
def _(v):
    d = DUR + XF
    y = add(sand_wind(d, 0.7, 520, 0.08), thistles(d, 1.0))
    y = add(y, pan(geiger(d, 0.6, 8), -0.3) * 0.1)
    y = scatter(y, 4, lambda: far(caw(ru(0.25, 0.4), ru(480, 600)), 2500, 0.4, 'rua', ru(-0.9, 0.9)), (0.06, 0.12))
    y = scatter(y, 8, lambda: bp(white(0.25), ru(150, 250), 4) * env_pts(0.25, [(0, 0), (0.1, 1), (0.25, 0)]) * 0.2, (0.1, 0.25))  # asas de mariposa
    return loopify(y, XF)


@A('bosque_viuvas', 'Bosque das Viuvas: mata morta, troncos e galhos rangendo, corujas, corvos, vento baixo', espaco='rua', mix=0.3)
def _(v):
    d = DUR + XF
    y = add(sand_wind(d, 0.6, 420, 0.07), thistles(d, 0.4))
    y = scatter(y, 8, lambda: far(creak(ru(1.0, 2.5), ru(15, 30), ru(30, 60), (ru(200, 300), ru(500, 700), ru(1100, 1500)), 0.6), 3000, 0.35, 'rua', ru(-0.9, 0.9)), (0.15, 0.3))
    y = scatter(y, 3, lambda: far(owl(), 2500, 0.5, 'catedral', ru(-0.9, 0.9)), (0.08, 0.14), margin=5)
    y = scatter(y, 3, lambda: far(caw(ru(0.25, 0.4), ru(480, 600)), 2500, 0.4, 'rua', ru(-0.9, 0.9)), (0.05, 0.1))
    y = scatter(y, 4, lambda: wood_knock(ru(300, 500), 0.2) * 0.3, (0.05, 0.12))
    return loopify(y, XF)


@A('tempestade_areia', 'Tempestade de areia (borda do mapa): parede de vento e areia, Geiger estalando sem parar, metal arrancado', espaco='rua', mix=0.15, lufs=-21)
def _(v):
    d = DUR + XF
    y = add(sand_wind(d, 1.6, 800, 0.15), sand_wind(d, 0.8, 300, 0.2))
    out = []
    for c in range(2):
        gr = np.abs(lp(white(d), 400)) * 9
        out.append(bbp(white(d), 1500, 5000) * gr ** 3 * 0.06)
    y = add(y, np.stack(out, 1), pan(geiger(d, 25, 90, 0.2), 0.0) * 0.3)
    y = scatter(y, 4, lambda: far(sheet_flap(), 3000, 0.3, 'rua', ru(-0.9, 0.9)), (0.1, 0.2))
    y = scatter(y, 3, lambda: far(structure_groan(), 2000, 0.4, 'rua', ru(-0.9, 0.9)), (0.15, 0.3))
    return loopify(y, XF)
