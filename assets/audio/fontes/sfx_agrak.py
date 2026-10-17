"""O Agrak, o Grande Coliseu: plateia, portões, Pião, leões, Golias, as duas vozes do ogro e a música da arena.
Pedido em design/pvp/agrak/coliseu_e_narrador.md (Efeitos e som). Só o timbre das vozes: as falas são texto.
"""
from kit import *  # noqa
from registro import som
from musica import Musica, F, p_taiko, p_tom, p_anvil, p_timpani, p_kick, p_cymbal, i_brass, i_bass


def A(id, desc, var=1, lufs=-16, espaco='abatedouro', mix=0.25):
    return som('agrak/' + id, var=var, lufs=lufs, espaco=espaco, mix=mix, desc=desc)


# ======================================================== multidão
def multidao(dur, n=48, f_lo=110, f_hi=290, vowels=('a', 'o', 'e'), contour=None, grito=1.0, aspero=0.4):
    """Muita gente gritando junto: cada voz com tom, entrada e duração próprias, um filtro de formantes por vogal."""
    N = ns(dur)
    tr = np.linspace(0, 1, N)
    fontes = {v: np.zeros(N) for v in vowels}
    for i in range(n):
        f0 = ru(f_lo, f_hi)
        cont = contour if contour is not None else [(0, ru(0.85, 0.95)), (ru(0.15, 0.35), ru(1.05, 1.2)), (1, ru(0.75, 0.9))]
        f = f0 * np.interp(tr, [c[0] for c in cont], [c[1] for c in cont])
        f = vibrato(f, dur, ru(4, 7), ru(0.005, 0.02), ru(0.1, 0.4))
        src = glottal(f, dur, 0.01 + aspero * 0.02, 0.1 + aspero * 0.2, 0.15 + aspero * 0.2, tilt=ru(900, 1800))
        t0 = ru(0, 0.12) * dur
        t1 = dur * ru(0.75, 1.0)
        env = env_pts(dur, [(0, 0), (t0, 0), (min(t0 + ru(0.05, 0.2), t1 - 0.01), 1), (t1 * 0.85, ru(0.6, 0.9)), (t1, 0), (dur, 0)])
        fontes[vowels[i % len(vowels)]] += src * env * ru(0.4, 1.0)
    y = np.zeros(N)
    for v, s in fontes.items():
        y += formant(s, v, 'tenor' if v != 'e' else 'alto', ru(0.95, 1.05)) * 2.0
    y /= np.sqrt(n)
    y = sat(y * grito * 2.0, 1.6)
    chiado = bbp(pink(dur), 400, 3500, 2) * env_pts(dur, [(0, 0), (0.1, 1), (dur * 0.8, 0.7), (dur, 0)]) * 0.35
    return blp(y + chiado, 7000, 2)


@A('plateia_urro', 'Plateia do Agrak: urro (morte, fera solta, vitória)', var=3, lufs=-14)
def _(v):
    d = ru(2.2, 3.0)
    y = multidao(d, 56, 120, 320, ('a', 'o', 'e'), grito=1.2)
    y = add(y, bp(crackle(d, 60, 0.004), 2500, 1.0) * 0.25)   # palmas e batidas no metal da arquibancada
    return widen(to_stereo(y), 0.5)


def silaba(dur, vowel, n=44, f_lo=150, f_hi=260, queda=0.85):
    return multidao(dur, n, f_lo, f_hi, (vowel,), [(0, 0.95), (0.2, 1.08), (1, queda)], grito=1.3, aspero=0.55)


@A('plateia_agrak', 'Plateia em coro: "A-GRAAAK!"', lufs=-13)
def _(v):
    y = np.zeros(ns(2.4))
    y = place(y, silaba(0.32, 'a'), 0.0)
    g = bp(brown(0.07), 300, 1.0) * env_exp(0.07, 0.03) * 1.6               # G
    y = place(y, g, 0.36)
    r = silaba(1.05, 'a', 50, 160, 280, 0.75)
    trilo = 1 - 0.55 * (np.sin(2 * np.pi * 26 * tt(1.05)) > 0) * env_pts(1.05, [(0, 1), (0.16, 1), (0.22, 0), (1.05, 0)])   # R
    y = place(y, r * trilo, 0.42)
    k = bp(white(0.06), 2200, 1.2) * env_exp(0.06, 0.012) * 2.0             # K
    y = place(y, k, 1.45)
    y = place(y, thump(55, 0.6, 2, 0.12, 0.2) * 1.2, 1.46)                  # pés batendo junto
    return widen(to_stereo(y), 0.45)


@A('plateia_golias', 'Plateia em coro: "GO-LI-AS! GO-LI-AS!" com os pés', lufs=-13)
def _(v):
    y = np.zeros(ns(3.6))
    for rep in range(2):
        base = rep * 1.6
        for i, (vw, dd) in enumerate([('o', 0.3), ('i', 0.25), ('a', 0.55)]):
            at = base + [0, 0.34, 0.62][i]
            y = place(y, silaba(dd, vw, 40, 140, 240, 0.8), at)
            y = place(y, thump(50, 0.5, 2, 0.1, 0.25) * 0.9, at)
        y = place(y, bp(white(0.05), 3500, 1.5) * env_exp(0.05, 0.01), base + 1.12)   # S
    return widen(to_stereo(y), 0.45)


@A('plateia_vaia', 'Plateia vaiando (tempo esgotado, ninguém venceu), com assobios', lufs=-15)
def _(v):
    d = 2.8
    y = multidao(d, 50, 100, 220, ('u', 'o'), [(0, 1.05), (0.3, 1.0), (1, 0.8)], grito=1.0, aspero=0.3)
    for i in range(5):   # assobios
        at = ru(0.1, 1.8)
        dd = ru(0.4, 0.9)
        f = ru(1800, 2600) * np.interp(np.linspace(0, 1, ns(dd)), [0, 0.5, 1], [1.0, 1.08, 0.82])
        w = sine(f, dd) * env_pts(dd, [(0, 0), (0.05, 1), (dd - 0.1, 0.8), (dd, 0)]) * 0.18
        y = place(y, w + bp(white(dd), 2200, 4) * 0.03, at)
    return widen(to_stereo(y), 0.5)


@som('ambiente/agrak_multidao', lufs=-24, espaco='abatedouro', mix=0.35, loop=True,
     desc='Agrak: murmúrio da plateia esperando sangue, gritos soltos, metal da arquibancada e vento')
def _(v):
    d = 32.0
    N = ns(d)
    y = np.zeros(N)
    # falatório: muitas vozes baixas, cada uma em frases curtas
    fontes = {'a': np.zeros(N), 'o': np.zeros(N), 'e': np.zeros(N), 'u': np.zeros(N)}
    for i in range(36):
        f = ru(95, 230) * (1 + 0.08 * lp(white(d), 3) * 6)
        src = glottal(f, d, 0.02, 0.2, 0.25, tilt=1100)
        fala = (lp(white(d), ru(2, 4)) > ru(0.0, 0.02)).astype(float)
        fala = lp(fala, 12)
        fontes[['a', 'o', 'e', 'u'][i % 4]] += src * fala * ru(0.3, 0.8)
    for vw, s in fontes.items():
        y += formant(s, vw, 'tenor', 1.0) * 1.3
    y /= 6.0
    y += bbp(pink(d), 250, 2500, 2) * 0.25
    out = to_stereo(y)
    out = widen(out, 0.6)
    # gritos soltos e batidas na arquibancada de metal
    for i in range(7):
        at = ru(0.5, d - 2.5)
        g = scream(ru(0.5, 0.9), ru(250, 420), R().choice(['a', 'e', 'o']), 'tenor', 2.0, 0.02) * 0.12
        out = place(out, pan(g, ru(-0.8, 0.8)), at)
    for i in range(10):
        at = ru(0.3, d - 1.0)
        out = place(out, pan(clang(ru(300, 600), 0.7, 0.8, 0.3, 0.4) * 0.05, ru(-0.9, 0.9)), at)
    return loopify(out, 3.0)


# ======================================================== portões e corrente
@A('grade_sobe', 'Grade do Portão dos Leões subindo: corrente na roldana, ferro rangendo e o baque lá em cima', lufs=-14)
def _(v):
    d = 2.6
    y = np.zeros((ns(d + 0.8), 2))
    y = place(y, to_stereo(chain(d, 55, 0.6, 1.2) * 0.9), 0)
    y = place(y, to_stereo(creak(d, 30, 70, (280, 690, 1500), 1.0) * 0.6), 0.05)
    y = place(y, to_stereo(gears(d, 14, 1800) * 0.25), 0)
    y = place(y, to_stereo(add(clang(420, 1.2, 1.1, 0.5, 0.8), thump(60, 0.6, 2, 0.15, 0.3)) * 0.9), d - 0.1)
    return y


@A('guincho_corrente', 'Portão do Gigante: guincho de corrente grossa puxado por manivela', lufs=-14)
def _(v):
    d = 3.2
    y = np.zeros((ns(d + 0.6), 2))
    y = place(y, to_stereo(gears(d, 9, 1200) * 0.5), 0)
    y = place(y, to_stereo(chain(d, 35, 0.9, 1.6)), 0)
    for k in range(6):   # catraca
        y = place(y, to_stereo(clink(ru(1600, 2200), 0.1) * 0.6), 0.3 + k * 0.48)
    y = place(y, to_stereo(creak(d, 18, 40, (200, 520, 1200), 0.8) * 0.7), 0.2)
    y = place(y, to_stereo(thump(45, 0.8, 2.5, 0.2, 0.3)), d)
    return y


@A('corrente_girando', 'Pião do Golias: bola de ferro girando na corrente (10 s, uma volta a cada meio segundo)', lufs=-14, espaco='rua')
def _(v):
    d = 10.5
    y = np.zeros((ns(d + 0.5), 2))
    k = 0
    t0 = 0.0
    while t0 < d - 0.3:
        y = place(y, whoosh(0.5, 90, 900, 1.0, 0.7, 0.2, -0.8 if k % 2 == 0 else 0.8, 0.8 if k % 2 == 0 else -0.8, 0.5), t0)
        y = place(y, to_stereo(chain(0.4, 30, 0.2, 0.7) * 0.35), t0 + 0.1)
        t0 += 0.5
        k += 1
    return y * env_pts(d + 0.5, [(0, 0), (0.3, 1), (d - 0.4, 1), (d + 0.5, 0)])[:, None]


# ======================================================== feras
def rugido(d, f0, cont, growl, drive, sub, shift):
    a = creature(d, f0, cont, 'a', 'o', 'baixo', shift, growl, sub, drive, 0.45)
    ronco = lp(white(d), 70) * 8 * env_pts(d, [(0, 0), (0.1, 1), (d * 0.8, 0.6), (d, 0)])
    corpo = creature(d, f0 * 0.5, cont, 'o', 'u', 'baixo', shift * 0.8, growl * 0.6, 0.8, drive * 0.7, 0.2) * 0.6
    return add(a, corpo, ronco * 0.15)


@A('rugido_dalila', 'Dalila, a Leoa do Amargo: rugido curto e rápido', lufs=-13, espaco='rua')
def _(v):
    return rugido(1.4, 85, [(0, 0.8), (0.15, 1.25), (0.5, 1.1), (1, 0.6)], 0.7, 3.0, 0.4, 0.85)


@A('rugido_nabucodonosor', 'Nabucodonosor, o Leão Velho: rugido longo, rouco, que treme', lufs=-13, espaco='rua')
def _(v):
    y = rugido(2.6, 62, [(0, 0.75), (0.2, 1.2), (0.6, 1.05), (1, 0.55)], 1.0, 3.5, 0.6, 0.75)
    trem = 1 - 0.3 * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * tt(2.6)))
    return y * trem


@A('rugido_sansao', 'Sansão, o maior dos leões: rugido grave que enche o estádio', lufs=-12, espaco='abatedouro')
def _(v):
    return rugido(2.2, 48, [(0, 0.8), (0.18, 1.3), (0.55, 1.15), (1, 0.6)], 0.85, 4.0, 0.9, 0.68)


@A('rugido_morte', 'Fera do Agrak caindo: gemido que afunda e o corpo batendo na areia', lufs=-14, espaco='rua')
def _(v):
    d = 1.8
    y = creature(d, 70, [(0, 1.1), (0.2, 1.0), (1, 0.45)], 'o', 'u', 'baixo', 0.75, 0.8, 0.6, 3.0, 0.4)
    y = place(np.zeros(ns(d + 1.0)), y, 0)
    y = place(y, add(thump(40, 0.9, 2.5, 0.25, 0.35), debris(0.8, 50, 200, 2500, 0.4) * 0.4), d - 0.2)
    return y


@A('golias_urro', 'Golias, o Pião do Agrak: urro do gigante e três batidas no peito', lufs=-12)
def _(v):
    d = 2.4
    y = np.zeros(ns(d + 2.0))
    y = place(y, rugido(d, 40, [(0, 0.8), (0.25, 1.25), (0.7, 1.1), (1, 0.7)], 0.9, 4.0, 1.0, 0.62), 0)
    for k in range(3):
        y = place(y, add(thump(52, 0.7, 2, 0.12, 0.3) * 1.3, flesh(0.2, 0.3, 1.6) * 0.5), d + 0.05 + k * 0.42)
    return y


# ======================================================== as duas vozes do ogro (só o timbre)
@A('megafone', 'Caim: berro no megafone de latão (timbre, as falas são texto)', var=3, lufs=-15, espaco='abatedouro', mix=0.3)
def _(v):
    d = ru(0.7, 1.0)
    n = ns(d)
    f = ru(150, 175) * np.interp(np.linspace(0, 1, n), [0, 0.2, 0.7, 1], [0.95, 1.12, 1.05, 0.85])
    src = glottal(vibrato(f, d, 5.5, 0.01, 0.1), d, 0.02, 0.25, 0.15, tilt=2200)
    vw = [('a', 'e'), ('o', 'a'), ('e', 'o')][v % 3]
    y = formant(src, vw[0], 'baixo', 1.0, vw[1], np.linspace(0, 1, n)) * 2.5
    # cone de latão: corta grave e agudo, ressoa e distorce
    y = bbp(y, 450, 3600, 3)
    y = resonate(y, [1150, 2300, 3100], [9, 12, 14], [0.5, 0.35, 0.25]) + y
    y = sat(y * 3.0, 3.0)
    sil = (lp(white(d), 9) > -0.02).astype(float)
    y *= lp(sil, 25) * env_pts(d, [(0, 0), (0.03, 1), (d - 0.12, 0.9), (d, 0)])
    return y


@A('abel_resmungo', 'Abel: resmungo rouco e baixo, debochando (timbre, as falas são texto)', var=3, lufs=-17, espaco='quarto', mix=0.15)
def _(v):
    d = ru(0.6, 0.9)
    n = ns(d)
    f = ru(88, 102) * np.interp(np.linspace(0, 1, n), [0, 0.4, 1], [1.05, 0.95, 0.8])
    src = glottal(f, d, 0.04, 0.4, 0.35, tilt=700)
    y = formant(src, 'u', 'baixo', 1.0, 'o', np.linspace(0, 1, n)) * 2.2
    y = blp(sat(y, 1.6), 2600, 2) + bp(white(d), 1400, 0.8) * 0.05
    risada = 1 - 0.5 * (np.sin(2 * np.pi * 6.5 * tt(d)) > 0.2) * (v == 2)   # a terceira é uma risadinha
    return y * risada * env_pts(d, [(0, 0), (0.05, 1), (d - 0.1, 0.8), (d, 0)])


# ======================================================== música da arena
@som('musica/agrak_arena', lufs=-15, loop=True, bus='musica',
     desc='O Agrak (lutas): tambores de guerra, metal batido na arquibancada, baixo de metais e a plateia ao fundo')
def _(v):
    m = Musica(104, 24, 4, tail=6)
    m.bus('perc', 1.0, 'abatedouro', 0.2)
    m.bus('metal', 0.7, 'abatedouro', 0.35)
    m.bus('baixo', 0.75, None, 0)
    m.bus('metais', 0.6, 'cripta', 0.3)
    raizes = ['D2', 'D2', 'C2', 'C2', 'Bb1', 'Bb1', 'A1', 'A1']
    for b in range(24):
        # batida: taiko no 1 e no 3, tom em síncope, bigorna no 4
        m.put('perc', p_taiko(1.0, 48), b, 0)
        m.put('perc', p_kick(0.6), b, 1.5)
        m.put('perc', p_taiko(0.8, 52), b, 2)
        m.put('perc', p_tom(110, 0.5), b, 2.75)
        m.put('perc', p_tom(90, 0.45), b, 3.25)
        if b % 2 == 1: m.put('metal', p_anvil(0.6), b, 3)
        if b >= 8: m.put('metal', p_anvil(0.35), b, 1)
        if b % 4 == 3: m.put('perc', p_timpani(F('D2'), 0.7), b, 3.5)
        r = raizes[b % 8]
        m.put('baixo', i_bass(F(r), 4 * m.spb * 0.95, 380, 1.8), b, 0, 0.8)
        if b >= 8 and b % 2 == 0:
            m.put('metais', i_brass(F(r) * 2, 2 * m.spb, 0.8, 0.4, 2.0), b, 0, 0.5)
            m.put('metais', i_brass(F(r) * 3, 1.5 * m.spb, 0.7, 0.3, 1.8), b, 2.5, 0.35)
    for b in [0, 8, 16]:
        m.put('metal', p_cymbal(0.4, 3.0), b, 0)
        m.put('metal', to_stereo(multidao(3.0, 30, 120, 300, ('a', 'o'), grito=0.8)) * 0.25, b, 0)
    return m.render(lufs=-15)
