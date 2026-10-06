"""Ambientes em loop (60 s, sem emenda) e sons pontuais de fundo."""
from kit import *  # noqa
from registro import som
from sfx_monstros import caw, moan, keen, squeal, music_box

DUR = 60.0
XF = 3.0


def A(id, desc, lufs=-24, espaco=None, mix=0.3):
    return som('ambiente/' + id, lufs=lufs, espaco=espaco, mix=mix, loop=True, desc=desc, bus='ambiente')


def bed(d=DUR + XF):
    return np.zeros((ns(d), 2))


def wind(d, strength=1.0, center=450, gust=0.08, whistle=0.0):
    out = []
    for c in range(2):
        mod = slow(d, gust)  # rajadas lentas
        mod = (mod - mod.min()) / (np.ptp(mod) + 1e-9)
        fc = center * (0.6 + 0.9 * mod)
        w = bp(pink(d), fc, 0.7) * (0.35 + 0.65 * mod) * strength
        w += lp(brown(d), 160) * 0.5 * strength * (0.5 + 0.5 * mod)
        if whistle:
            w += bp(white(d), fc * 2.6, 18) * mod ** 2 * whistle * 2
        out.append(w)
    return np.stack(out, 1)


def far(x, lpf=1800, dist_mix=0.5, espaco='catedral', p=0.0):
    """Afasta um som: corta agudo e joga mais no reverb."""
    x = blp(x, lpf, 2) if x.ndim == 1 else blp(x.mean(1), lpf, 2)
    return reverb(pan(x, p), espaco, dist_mix)


def scatter(y, n, gen, gain=(0.3, 1.0), pan_=(-0.9, 0.9), margin=4.0, d=DUR + XF):
    for i in range(n):
        at = ru(0, d - margin)
        s = gen()
        s = pan(s, ru(*pan_)) if s.ndim == 1 else s
        y = place(y, s * ru(*gain), at)
    return y[:ns(d)]


def flies(d, k=3):
    y = bed(d)
    for i in range(k):
        f = ru(170, 230) * (1 + 0.06 * slow(d, 1.5))
        b = bp(saw(f, d), 600, 1.0) * 0.3 + bp(saw(f, d), 2400, 3) * 0.1
        amp = np.clip(slow(d, 0.3) * 0.6 + 0.3, 0, 1)
        y = add(y, pan(b * amp, np.clip(slow(d, 0.2) * 0.6, -1, 1)))
    return y


def murmur(d, voices=6):
    """Conversa distante sem palavras (acampamento)."""
    y = bed(d)
    for v in range(voices):
        t = ru(0, 5)
        f0 = ru(95, 180)
        p = ru(-0.7, 0.7)
        while t < d - 2:
            phr = ru(1.0, 3.0)
            n = ns(phr)
            fc = f0 * (1 + 0.12 * slow(phr, 4))
            src = glottal(fc, phr, 0.01, 0.1, 0.2, 800)
            vw = [R().choice(list('aeiou')) for _ in range(2)]
            s = formant(src, vw[0], 'tenor', 1.0, vw[1], np.abs(np.sin(np.linspace(0, ru(6, 14), n))))
            s *= np.clip(np.sin(np.linspace(0, ru(10, 25), n)) * 2, 0, 1)  # silabas
            y = place(y, pan(lp(s, 1200), p) * 0.5, t)
            t += phr + ru(1.0, 6.0)
    return y[:ns(d)]


# ======================================================== Area inicial
@A('acampamento_vela', 'Acampamento da Vela: lampada de arco zumbindo, fogueiras, forja ao longe, conversa baixa, vento', espaco='rua', mix=0.25)
def _(v):
    d = DUR + XF
    y = wind(d, 0.5, 380)
    arc = hum(d, 60, 12, 0.0005) * 0.25 + bp(white(d), 3000, 1) * 0.03
    arc = add(arc, blp(zap(d, 0.07), 5000, 2) * lp((slow(d, 0.5) > 1.2).astype(float), 30))
    y = add(y, pan(arc, 0.15) * 0.8)
    y = add(y, pan(fire(d, 0.45, 18), -0.5), pan(fire(d, 0.3, 14), 0.6) * 0.7)
    y = add(y, murmur(d, 5) * 0.6)
    t = ru(2, 6)
    while t < d - 4:  # ferreiro (Bigorna) trabalhando ao longe
        for k in range(int(ru(3, 7))):
            y = place(y, far(anvil(ru(1000, 1200), 1.0), 3500, 0.35, 'rua', -0.6) * 0.18, t + k * ru(0.55, 0.7))
        t += ru(9, 16)
    y = scatter(y, 6, lambda: chain(0.5, 25) * 0.3, (0.1, 0.25))
    y = scatter(y, 5, lambda: creak(ru(0.6, 1.2), 30, 50, (300, 700, 1500)) * 0.3, (0.05, 0.15))
    return loopify(y, XF)


@A('capela_sao_lazaro', 'Capela de Sao Lazaro (Arautos): nave de pedra, orgao desafinado distante, velas, sussurros de prece', espaco='catedral', mix=0.45)
def _(v):
    d = DUR + XF
    y = wind(d, 0.15, 250) * 0.6
    chords = [['D2', 'A2', 'D3', 'F3'], ['Bb1', 'F2', 'D3', 'F3'], ['G1', 'D2', 'Bb2', 'D3'], ['A1', 'E2', 'C#3', 'E3']]
    t = 0.0
    i = 0
    while t < d:
        o = organ(chords[i % 4], 9.0, 'flauta', 0.008, 2.5, 3.0, 0.1, 0.03)
        y = place(y, widen(lp(o, 1400), 0.5) * 0.6, t)
        t += 7.8
        i += 1
    y = y[:ns(d)]
    y = add(y, whispers(d, 4, 0.5) * 0.25)
    y = add(y, to_stereo(lp(fire(d, 0.1, 6), 3000)) * 0.4)  # velas
    y = scatter(y, 4, lambda: wood_knock(ru(120, 200), 0.3) * 0.3, (0.05, 0.15))  # bancos rangendo
    return loopify(y, XF)


@A('campos_cinza', 'Campos de Cinza: vento seco forte, palha queimada, corvos distantes, espantalhos de arame', espaco='rua', mix=0.2)
def _(v):
    d = DUR + XF
    y = wind(d, 1.0, 500, 0.1, 0.25)
    grass = bbp(crackle(d, 250, 0.002), 2000, 9000) * (0.3 + np.clip(slow(d, 0.15) * 0.4, 0, 0.7))
    y = add(y, widen(grass * 0.25, 0.8))
    y = scatter(y, 9, lambda: far(caw(ru(0.25, 0.4), ru(480, 600)), 2500, 0.4, 'rua', ru(-0.9, 0.9)), (0.1, 0.25))
    y = scatter(y, 6, lambda: creak(ru(0.8, 1.5), 15, 30, (900, 2100, 4200), 1.0) * 0.3, (0.04, 0.1))  # arame
    y = scatter(y, 3, lambda: far(wings(1.5, 4, 0.5, 1.2), 3000, 0.3, 'rua', ru(-0.8, 0.8)), (0.1, 0.2))
    return loopify(y, XF)


@A('vala_comum', 'A Vala: vento baixo na vala, moscas, terra escorrendo, caes ao longe', espaco='rua', mix=0.25)
def _(v):
    d = DUR + XF
    y = wind(d, 0.6, 300)
    y = add(y, flies(d, 4) * 0.5)
    y = scatter(y, 8, lambda: debris(ru(0.5, 1.5), 40, 200, 2500, 0.4) * 0.4, (0.1, 0.25))
    def dog():
        n = ns(2.5)
        f = 380 * np.interp(np.linspace(0, 1, n), [0, 0.15, 0.6, 1], [0.8, 1.45, 1.35, 0.9])
        s = formant(glottal(vibrato(f, 2.5, 5, 0.015, 0.5), 2.5, 0.01, 0.15, 0.3, 1200), 'u', 'alto', 1.0) * 2
        return far(s * env_pts(2.5, [(0, 0), (0.2, 1), (2.0, 0.8), (2.5, 0)]), 1500, 0.6, 'cripta', ru(-0.9, 0.9))
    y = scatter(y, 3, dog, (0.08, 0.15))
    y = scatter(y, 5, lambda: far(creature(1.5, 65, [(0, 1), (1, 1)], 'u', 'o', 'baixo', 0.9, 1.0, 0.3, 2.5), 1200, 0.4, 'rua', ru(-0.9, 0.9)), (0.08, 0.15))
    return loopify(y, XF)


@A('cemiterio', 'Cemiterio de Sao Lazaro: vento entre lapides, sino da torre ao longe, lamentos da fila, terra remexida', espaco='rua', mix=0.25)
def _(v):
    d = DUR + XF
    y = wind(d, 0.75, 420, 0.08, 0.35)
    t = ru(3, 8)
    while t < d - 6:
        y = place(y, far(bell(hz('C#3'), 7, 5, 0.8), 1500, 0.6, 'catedral', 0.5) * 0.35, t)
        t += ru(14, 22)
    y = scatter(y, 6, lambda: far(moan(ru(2.0, 3.0), ru(95, 125)), 1600, 0.5, 'cripta', ru(-0.9, 0.9)), (0.12, 0.25))
    y = scatter(y, 5, lambda: far(caw(0.35, 520), 2500, 0.4, 'rua', ru(-0.9, 0.9)), (0.06, 0.12))
    y = scatter(y, 6, lambda: debris(ru(0.4, 1.2), 50, 200, 2500, 0.3) * 0.5, (0.08, 0.2))
    y = scatter(y, 3, lambda: creak(ru(1.2, 2.0), 25, 45, (280, 640, 1400)) * 0.3, (0.05, 0.12))  # portao
    return loopify(y, XF)


@A('abatedouro', 'Abatedouro Carnica: maquinas, chamines, ganchos balancando, gordura pingando, porcos ao longe', espaco='abatedouro', mix=0.35)
def _(v):
    d = DUR + XF
    y = to_stereo(hum(d, 50, 10, 0.003) * 0.35)
    y = add(y, widen(rumble(d, 60, 0.6), 0.5))
    t = 0.0
    while t < d - 1:  # maquina de esteira: batida ritmica
        y = place(y, pan(add(clang(ru(180, 230), 0.6, 0.9, 0.2, 0.3) * 0.4, thump(70, 0.4, 0.4, 0.08, 0.3) * 0.5), -0.4) * 0.35, t)
        t += 1.6
    y = add(y, widen(steam(d, 3000, 0.5, None) * 0.08 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.07 * tt(d)))))
    y = scatter(y, 14, lambda: chain(ru(0.5, 1.0), 20, 0, 1.3) * 0.5, (0.1, 0.3))
    y = scatter(y, 30, lambda: drip(ru(500, 1200), 0.25) * 0.5, (0.05, 0.2))
    y = scatter(y, 4, lambda: far(squeal(ru(0.5, 0.8), ru(950, 1200)), 2000, 0.5, 'abatedouro', ru(-0.9, 0.9)), (0.06, 0.12))
    return loopify(y, XF)


@A('noite_vento', 'Vento noturno generico para areas externas sem ambiente proprio', espaco='rua', mix=0.2)
def _(v):
    d = DUR + XF
    y = wind(d, 0.9, 400, 0.07, 0.3)
    y = scatter(y, 4, lambda: debris(ru(0.5, 1.2), 40, 300, 3000, 0.3) * 0.4, (0.05, 0.15))
    return loopify(y, XF)


# ======================================================== Cripta
@A('cripta_porao', 'Cripta 1, Porao do Matadouro: camaras frias, vapor, trilhos de ganchos, gordura pingando, caldeiras', espaco='cripta', mix=0.4)
def _(v):
    d = DUR + XF
    y = widen(rumble(d, 45, 0.8), 0.6)
    y = add(y, to_stereo(hum(d, 50, 6, 0.002) * 0.15))
    y = add(y, widen(steam(d, 2800, 0.5, None) * 0.05))
    y = scatter(y, 6, lambda: steam(ru(1.0, 2.5), ru(2500, 4000), 0.05, 0.6) * 0.4, (0.2, 0.4))
    y = scatter(y, 40, lambda: drip(ru(400, 1000), 0.3), (0.05, 0.25))
    y = scatter(y, 6, lambda: add(gears(ru(1.5, 3.0), 5, 800) * 0.4, creak(1.5, 10, 14, (300, 700, 1500), 0.6) * 0.2), (0.15, 0.3))
    y = scatter(y, 8, lambda: chain(ru(0.6, 1.2), 15, 0, 1.4) * 0.5, (0.1, 0.25))
    y = scatter(y, 3, lambda: far(clang(ru(120, 180), 3.0, 0.8, 1.0, 0.3), 1500, 0.5, 'cripta'), (0.1, 0.2))
    return loopify(y, XF)


@A('cripta_ossario', 'Cripta 2, Ossario das Carpideiras: milhares de velas, eco de canto ao longe, poeira de osso', espaco='ossario', mix=0.5)
def _(v):
    d = DUR + XF
    y = wind(d, 0.15, 200) * 0.5
    y = add(y, to_stereo(lp(fire(d, 0.2, 10), 3000)) * 0.5)
    def far_song():
        nts = [hz('D5'), hz('F5'), hz('E5'), hz('C5'), hz('D5')]
        s = np.zeros(ns(6))
        for i, f in enumerate(nts[:int(ru(2, 5))]):
            s = place(s, keen(1.2, f, 0.025), i * 1.05)
        return far(s, 1400, 0.75, 'ossario', ru(-0.8, 0.8))
    y = scatter(y, 5, far_song, (0.15, 0.3), margin=7)
    y = scatter(y, 10, lambda: bones_rattle(ru(0.3, 0.8), 25) * 0.4, (0.05, 0.15))
    y = scatter(y, 8, lambda: debris(ru(0.6, 1.5), 60, 1500, 7000, 0.4) * 0.3, (0.05, 0.12))
    y = add(y, whispers(d, 3, 0.3) * 0.12)
    return loopify(y, XF)


@A('cripta_camara', 'Cripta 3, Camara da Trombeta: zumbido grave constante, correntes, vitrais acesos, poeira dourada', espaco='catedral', mix=0.45)
def _(v):
    d = DUR + XF
    t = tt(d)
    drone = 0
    for f, a in [(hz('D1'), 0.5), (hz('D1') * 1.004, 0.4), (hz('A1'), 0.3), (hz('D2'), 0.2), (hz('D2') * 1.5 * 1.003, 0.08)]:
        drone = drone + np.sin(2 * np.pi * f * t + ru(0, 6)) * a
    drone *= 0.8 + 0.2 * np.sin(2 * np.pi * 0.05 * t)
    y = widen(drone * 0.6, 0.3)
    choir_pad = choir(['D3', 'A3', 'D4'], d, 'u', 'baixo', 3, 6, 6, vib=0.006) * 0.25
    y = add(y, lp(choir_pad, 1200))
    sparkle = np.zeros((ns(d), 2))
    for i in range(70):  # poeira dourada
        f = hz(R().choice(['D6', 'A6', 'F#6', 'E6', 'D7']))
        s = modal(2.0, [f], [0.5], [1]) * 0.05
        sparkle = place(sparkle, pan(s, ru(-1, 1)), ru(0, d - 2))
    y = add(y, sparkle[:ns(d)])
    y = scatter(y, 10, lambda: chain(ru(1.0, 2.0), 10, 0.1, 1.8) * 0.5, (0.1, 0.25))
    return loopify(y, XF)


# ======================================================== pontuais
def O(id, desc, var=1, lufs=-20, espaco='catedral', mix=0.5):
    return som('ambiente/pontual/' + id, var=var, lufs=lufs, espaco=espaco, mix=mix, desc=desc, bus='ambiente')


@O('sino_distante', 'Sino da torre tocando ao longe', var=2)
def _(v):
    y = np.zeros(ns(10))
    for i in range(int(ru(1, 3.99))):
        y = place(y, blp(bell(hz(['C#3', 'A2'][v]), 7, 5, 0.8), 1500), i * 2.8)
    return y


@O('corvo_distante', 'Corvo grasnando longe', var=3, espaco='rua', mix=0.4)
def _(v):
    y = np.zeros(ns(1.2))
    for i in range(int(ru(1, 3.99))):
        y = place(y, blp(caw(ru(0.25, 0.4), ru(480, 600)), 2500), i * 0.38)
    return y


@O('trovao_distante', 'Trovao seco ao longe (sem chuva)', var=2, espaco='rua', mix=0.3, lufs=-18)
def _(v):
    d = 6.0
    y = lp(brown(d), 300) * env_pts(d, [(0, 0), (0.15, 1), (0.8, 0.6), (d, 0)], 1.5) * 2
    y = add(y, debris(d, 30, 60, 600, 1.5) * 1.5)
    return y * (1 + 0.4 * slow(d, 4))


@O('uivo_distante', 'Cao de Vala uivando longe', espaco='cripta', mix=0.6)
def _(v):
    n = ns(3.0)
    f = 380 * np.interp(np.linspace(0, 1, n), [0, 0.15, 0.6, 1], [0.8, 1.45, 1.35, 0.9])
    s = formant(glottal(vibrato(f, 3.0, 5, 0.015, 0.5), 3.0, 0.01, 0.15, 0.3, 1200), 'u', 'alto', 1.0) * 2
    return blp(s * env_pts(3.0, [(0, 0), (0.2, 1), (2.4, 0.8), (3.0, 0)]), 1500)


@O('porta_distante', 'Porta pesada rangendo e batendo ao longe', espaco='cripta', mix=0.6)
def _(v):
    y = np.zeros(ns(3.0))
    y = place(y, creak(1.5, 20, 40, (220, 540, 1300), 1.2), 0)
    return blp(place(y, add(wood_knock(110, 0.6), thump(50, 0.6, 0.5, 0.15, 0.3)), 1.6), 2000)


@O('coro_distante', 'Eco de coro ao longe (ossario)', espaco='ossario', mix=0.7)
def _(v):
    return blp(choir(['D4', 'F4', 'A4'], 4.0, 'o', 'alto', 3, 1.2, 1.8), 1600)


@O('caixinha_distante', 'Caixinha de musica quebrada tocando no escuro (querubins por perto)', espaco='catedral', mix=0.6)
def _(v):
    y = music_box(['E6', 'G6', 'B6', 'C7', 'B6', 'G6', 'E6', 'D#6'], 0.3, 0.02)
    return varispeed(blp(y, 4000), np.linspace(1.0, 0.8, len(y)))
