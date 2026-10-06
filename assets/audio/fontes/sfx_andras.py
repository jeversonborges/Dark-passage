"""Andras, o General Partido (chefe do andar 1) e o Soldado Caido."""
from kit import *  # noqa
from registro import som


def C(id, desc, var=1, lufs=-14, espaco='cripta', mix=0.25, loop=False):
    return som('chefes/' + id, var=var, lufs=lufs, espaco=espaco, mix=mix, desc=desc, loop=loop)


def general(d, f0=62, contour=None, vw='a', vw2='o', growl=0.9, drive=4.0):
    """Voz do general: demonio grave, com fogo na garganta."""
    v = creature(d, f0, contour or [(0, 0.85), (0.25, 1.2), (1, 0.8)], vw, vw2, 'baixo', 0.6, growl, 0.9, drive, 0.6)
    ember = bbp(crackle(d, 60, 0.0015), 800, 5000) * env_pts(d, [(0, 0), (0.1, 1), (d, 0)]) * 0.25
    return add(v, ember)


def claws(d=0.5):
    """Unhas pretas cravando e raspando na pedra."""
    sc = bp(white(d) * (1 + 4 * np.abs(lp(white(d), 120) * 8)), np.linspace(3000, 1600, ns(d)), 2.5)
    sc *= env_pts(d, [(0, 0), (0.02, 1), (d * 0.6, 0.6), (d, 0)])
    return add(sc * 0.8, crunch(0.15, 300, 900, 4000, 0.6) * 0.5)


def banner(d=0.6, g=1.0):
    """Estandarte rasgado tremulando."""
    flap = bp(white(d), 900, 0.8) * (0.4 + np.abs(np.sin(2 * np.pi * ru(9, 13) * tt(d)))) * env_pts(d, [(0, 0), (d * 0.3, 1), (d, 0)])
    return add(flap * 0.7, cloth(d, 1.0, 1800)) * g


def pull_step(heavy=1.0):
    """Uma puxada: mao bate, unhas raspam, tronco escorrega, corrente das tripas arrasta."""
    d = 1.1
    y = np.zeros(ns(d))
    y = place(y, add(sat(thump(ru(40, 48), 0.6, 1.2, 0.14 * heavy, 0.5), 2) * 0.9, flesh(0.3, 0.6, 1.4) * 0.5), 0)
    y = place(y, claws(0.45) * 0.8, 0.05)
    slide = lp(white(0.6) * (1 + 2 * np.abs(lp(white(0.6), 30) * 8)), 700) * env_pts(0.6, [(0, 0), (0.15, 1), (0.6, 0)])
    y = place(y, slide * 0.9, 0.25)
    y = place(y, chain(0.7, 35, 0.8, 1.6) * 0.6, 0.25)
    return y


@C('andras_arrasto_passo', 'Andras: cada puxada do tronco (mao, unhas, corrente das tripas no chao)', var=4, lufs=-16)
def _(v):
    return pull_step(ru(0.9, 1.1))


@C('andras_brasa_loop', 'Andras: toco da cintura em brasa e corrente balancando (loop ocioso, perto dele)', lufs=-22, loop=True)
def _(v):
    d = 6.0
    y = add(fire(d + 1, 0.5, 30), steam(d + 1, 4000, 0.01, None) * 0.08, rumble(d + 1, 50, 0.4))
    for i in range(6):
        y = place(y, chain(ru(0.5, 1.0), 20, 0.2, 1.6) * 0.4, ru(0, d))
    return loopify(to_stereo(y[:ns(d + 1)]), 1.0)


@C('andras_estandarte', 'Andras: ataque basico com o estandarte partido', var=3, lufs=-14)
def _(v):
    y = np.zeros((ns(1.3), 2))
    y = place(y, whoosh(0.5, 150, 1200, 0.9, 0.7, 0.2, -0.6, 0.6) * 1.1, 0)
    y = place(y, to_stereo(banner(0.5, 0.6)), 0.05)
    hit = add(wood_knock(ru(150, 190), 0.4) * 1.2, sat(thump(48, 0.6, 1.8, 0.14, 0.4), 2), flesh(0.4, 0.8, 1.3) * 0.7,
              clang(ru(500, 650), 0.5, 1.0, 0.1, 0.4) * 0.3)
    return place(y, to_stereo(hit), 0.4)


@C('andras_golpe_estandarte', 'Andras: golpe de estandarte em cone (varre e esmaga)', var=2, lufs=-12)
def _(v):
    y = np.zeros((ns(2.2), 2))
    y = place(y, to_stereo(general(0.7, 70, [(0, 0.9), (1, 1.2)]) * 0.6), 0)
    y = place(y, whoosh(0.8, 120, 1000, 0.8, 0.75, 0.3, -0.8, 0.8) * 1.4, 0.3)
    y = place(y, to_stereo(banner(0.8, 0.9)), 0.35)
    hit = add(sat(thump(36, 1.2, 3, 0.35, 0.8), 3) * 1.3, wood_knock(140, 0.5) * 1.2, debris(1.2, 90, 300, 4000, 0.35),
              bones_rattle(0.6, 70) * 0.6, clang(300, 1.0, 0.9, 0.25, 0.6) * 0.4)
    return place(y, to_stereo(hit), 1.0)


@C('andras_arrasto_investida', 'Andras: crava as maos e se joga para frente (Arrasto, linha de 6 tiles)', var=2, lufs=-12)
def _(v):
    y = np.zeros((ns(2.4), 2))
    y = place(y, to_stereo(add(claws(0.4), general(0.6, 75, [(0, 1), (1, 1.3)], 'a', 'a') * 0.5)), 0)
    sl = 0.7
    slide = lp(white(sl) * (1 + 3 * np.abs(lp(white(sl), 40) * 8)), 900) * env_pts(sl, [(0, 0), (0.05, 1), (sl, 0.6)]) * 1.4
    y = place(y, pan(add(slide, chain(sl, 80, 1.2, 1.6) * 0.8, debris(sl, 120, 300, 3000, 0.5) * 0.6), np.linspace(-0.6, 0.6, ns(sl))), 0.45)
    y = place(y, whoosh(sl, 100, 700, 0.7, 0.4, 0, -0.6, 0.6), 0.45)
    end = add(sat(thump(34, 1.2, 3, 0.35, 0.8), 3) * 1.3, flesh(0.5, 1.0, 1.6), debris(1.0, 100, 300, 4000, 0.3) * 0.7)
    return place(y, to_stereo(end), 1.1)


@C('andras_devorar_loop', 'Andras: devorando uma Pilha de Mortos (loop durante a barra de conjuracao)', lufs=-14, loop=True)
def _(v):
    d = 5.0
    y = np.zeros(ns(d + 1))
    t = 0.0
    while t < d:
        y = place(y, add(flesh(0.4, 2.0, 1.6), crunch(0.25, 700, 500, 4000, 1.3) * 0.8), t)
        if R().uniform() < 0.35:
            y = place(y, clang(ru(500, 800), 0.4, 1.0, 0.08, 0.4) * 0.25, t + 0.1)  # armadura entre os dentes
        t += ru(0.32, 0.5)
    y = add(y, general(d + 1, 55, [(0, 1), (1, 1)], 'o', 'u', 0.6, 2.5) * 0.35, lp(liquid(d + 1, 12, 120, 350), 1000) * 0.5)
    return loopify(to_stereo(y[:ns(d + 1)]), 0.8)


@C('andras_devorar_cadaver', 'Andras: devora rapido um cadaver fresco de Soldado Caido (2 s)', lufs=-14)
def _(v):
    y = np.zeros(ns(2.4))
    for i in range(5):
        y = place(y, add(flesh(0.35, 2.0, 1.4), crunch(0.2, 600, 500, 4000) * 0.6), i * 0.38)
    return place(y, general(0.8, 60, [(0, 1), (1, 0.85)], 'o', 'u', 0.5, 2) * 0.5, 1.6)


@C('andras_devorar_cancelado', 'Andras: postura quebrada enquanto come (engasga e fica exausto)', lufs=-13)
def _(v):
    y = np.zeros(ns(2.5))
    y = place(y, add(sat(thump(40, 0.8, 2, 0.2, 0.5), 2), bones_rattle(0.6, 80) * 0.8), 0)
    y = place(y, general(0.9, 85, [(0, 1.3), (0.3, 1.0), (1, 0.6)], 'a', 'u', 1.2, 4), 0.1)
    return place(y, lp(splat(0.6, 1.4), 2500) * 0.7, 0.4)


@C('andras_fome_saciada', 'Andras: terminou de comer e cresce (Fome Saciada +1)', lufs=-13)
def _(v):
    y = np.zeros(ns(2.6))
    for i in range(8):
        y = place(y, crunch(0.25, 600, 400, 3500, 1.4) * ru(0.5, 0.9), ru(0, 0.8))
    y = place(y, general(1.6, 58, [(0, 0.8), (0.4, 1.15), (1, 0.9)], 'o', 'a', 0.8, 3.5), 0.5)
    return place(y, whoomp(1.0, 50) * 0.5, 0.6)


@C('andras_ordem_levantar', 'Andras: "DE PE, SOLDADOS!" (berro + corneta de guerra + mortos levantando)', lufs=-12, espaco='catedral', mix=0.3)
def _(v):
    y = np.zeros((ns(4.0), 2))
    y = place(y, to_stereo(general(1.4, 80, [(0, 0.9), (0.15, 1.35), (0.6, 1.25), (1, 0.9)], 'e', 'a', 0.9, 4)), 0)
    horn = add(brass(hz('D3'), 1.6, 0.15, 0.6, 0.9, 1.5, 3), brass(hz('A2'), 1.6, 0.15, 0.6, 0.9, 1.5, 3) * 0.6)
    y = place(y, widen(blp(horn, 3000) * 0.8), 0.9)
    for i in range(10):
        y = place(y, pan(add(bones_rattle(0.5, 60) * 0.6, clang(ru(400, 900), 0.4, 1.0, 0.08, 0.4) * 0.3), ru(-0.9, 0.9)), 1.2 + ru(0, 1.5))
    return place(y, to_stereo(debris(2.0, 60, 300, 3000, 0.6) * 0.6), 1.3)


@C('andras_vomito_brasa', 'Andras: vomita brasa em cone (3 ticks + rastro de fogo)', var=2, lufs=-12)
def _(v):
    y = np.zeros((ns(3.0), 2))
    y = place(y, to_stereo(general(0.7, 70, [(0, 1), (1, 1.3)], 'o', 'a', 1.4, 4) * 0.8), 0)
    st = 1.5
    jet = add(fire(st, 1.2, 70), lp(brown(st), 400) * 1.5, splat(st, 1.6) * 0.5) * env_pts(st, [(0, 0), (0.08, 1), (1.2, 0.8), (st, 0)])
    y = place(y, widen(jet, 0.5), 0.6)
    return place(y, to_stereo(whoomp(1.0, 60) * 0.8), 0.6)


@C('andras_banquete', 'Andras: Banquete (agarra o jogador e morde, 5 ticks)', lufs=-12)
def _(v):
    y = np.zeros((ns(3.4), 2))
    y = place(y, whoosh(0.4, 200, 1500, 1.0, 0.6, 0, 0.6, -0.4), 0)
    y = place(y, to_stereo(add(flesh(0.4, 1.0, 1.3), cloth(0.4, 1.2), general(0.5, 90, [(0, 1), (1, 1.2)], 'a', 'a') * 0.5)), 0.35)
    for i in range(5):
        y = place(y, to_stereo(add(flesh(0.35, 2.0, 1.2), wood_knock(ru(900, 1200), 0.1) * 0.8, crunch(0.15, 500, 600, 3500) * 0.5)), 0.85 + i * 0.5)
    return y


@C('andras_exausto', 'Andras: exausto (respiracao pesada de fornalha, janela de punicao)', lufs=-16)
def _(v):
    y = np.zeros(ns(3.2))
    for i in range(3):
        y = place(y, add(lp(breath(0.5, 'a', 'baixo', True, 1.0), 1200), general(0.5, 50, [(0, 1), (1, 1)], 'u', 'u', 0.4, 1.5) * 0.3), i * 1.05)
        y = place(y, lp(breath(0.5, 'o', 'baixo', False, 1.2), 1000), i * 1.05 + 0.5)
    return add(y, fire(3.2, 0.3, 20))


@C('andras_fala_curta', 'Andras: voz de comando sem palavras (acompanha as falas em texto)', var=3, lufs=-14)
def _(v):
    d = ru(1.3, 2.0)
    y = np.zeros(ns(d))
    t = 0.0
    while t < d - 0.25:
        dd = ru(0.12, 0.28)
        y = place(y, general(dd, ru(70, 90), [(0, 1), (1, ru(0.85, 1.2))], R().choice(list('aeo')), R().choice(list('aou')), 0.7, 3), t)
        t += dd + ru(0.0, 0.08)
    return y


@C('andras_fase', 'Andras: muda de fase (urro de general + tambor de guerra)', lufs=-11, espaco='catedral', mix=0.3)
def _(v):
    y = np.zeros((ns(4.0), 2))
    y = place(y, widen(general(2.2, 60, [(0, 0.8), (0.2, 1.3), (1, 0.85)], 'a', 'o', 1.0, 5) * 1.2, 0.3), 0)
    for k in range(3):
        y = place(y, to_stereo(drum(48, 1.4, 0.45, True, 0.7, 0.5) * (0.8 + 0.1 * k)), 0.6 + k * 0.3)
    return place(y, to_stereo(add(whoomp(1.2, 45), chain(1.2, 40, 0.6, 1.8) * 0.6)), 0.6)


@C('andras_morte', 'Andras: tenta devorar o proprio estandarte e desaba; a brasa se apaga', lufs=-11, espaco='catedral', mix=0.35)
def _(v):
    y = np.zeros((ns(9.0), 2))
    for i in range(4):  # mordendo a haste do estandarte
        y = place(y, to_stereo(add(wood_knock(ru(150, 220), 0.4) * 1.2, crunch(0.3, 400, 400, 3000, 1.2) * 0.8)), i * 0.45)
    y = place(y, to_stereo(general(2.2, 70, [(0, 1.1), (0.3, 1.0), (1, 0.5)], 'a', 'u', 0.9, 3)), 1.7)
    y = place(y, to_stereo(add(sat(thump(30, 2.0, 2.5, 0.6, 0.6), 2.5) * 1.3, debris(1.6, 80, 300, 3000, 0.5),
                               chain(1.6, 50, 0.8, 1.8) * 0.7, bones_rattle(1.2, 50) * 0.6)), 3.6)
    y = place(y, to_stereo(add(banner(1.0, 0.8), wood_knock(130, 0.5) * 0.9)), 4.2)  # estandarte cai
    y = place(y, to_stereo(blp(steam(3.0, 3000, 0.05, 0.8), 5000, 2) * 0.2), 4.0)  # brasa apagando
    y = place(y, to_stereo(lp(breath(1.6, 'a', 'baixo', False, 0.7), 1500)), 5.2)
    return y


@C('pilha_mortos_dano', 'Pilha de Mortos: recebe dano (ossos e armaduras velhas)', var=3, lufs=-17)
def _(v):
    return add(bones_rattle(0.4, 70), flesh(0.3, 0.5, 1.0) * 0.6, clang(ru(500, 900), 0.4, 1.0, 0.06, 0.4) * 0.3)


@C('pilha_mortos_destruida', 'Pilha de Mortos: destruida (nao pode mais ser comida)', lufs=-13)
def _(v):
    y = np.zeros(ns(2.5))
    y = place(y, add(crunch(0.6, 400, 300, 3500, 3), bones_rattle(1.5, 70), debris(1.8, 80, 300, 4000, 0.6) * 0.7), 0)
    for i in range(5):
        y = place(y, clang(ru(300, 800), 0.8, 1.0, 0.2, 0.5) * 0.4, ru(0.05, 1.0))
    return place(y, sat(thump(42, 0.8, 1.5, 0.2, 0.5), 2) * 0.8, 0)


# ======================================================== Soldado Caido
def M(id, desc, var=1, lufs=-16, espaco='cripta', mix=0.2):
    return som('monstros/' + id, var=var, lufs=lufs, espaco=espaco, mix=mix, desc=desc)


@M('soldado_levanta', 'Soldado Caido: levanta da pilha (ossos, armadura misturada, espada raspando)', var=2, lufs=-15)
def _(v):
    y = np.zeros(ns(2.0))
    y = place(y, add(bones_rattle(1.0, 60), debris(1.2, 60, 300, 3000, 0.4) * 0.6), 0)
    for i in range(4):
        y = place(y, clang(ru(450, 1000), 0.5, 1.0, 0.1, 0.4) * 0.4, ru(0.1, 1.0))
    y = place(y, creature(1.0, 105, [(0, 0.8), (0.5, 1.15), (1, 0.9)], 'u', 'a', 'baixo', 0.85, 0.5, 0.3, 2), 0.7)
    sc = bp(white(0.4), np.linspace(2500, 4000, ns(0.4)), 4) * env_pts(0.4, [(0, 0), (0.05, 1), (0.4, 0)])
    return place(y, sc * 0.4, 1.4)


@M('soldado_ataque', 'Soldado Caido: golpe de espada enferrujada', var=3, lufs=-15)
def _(v):
    y = np.zeros((ns(0.9), 2))
    y = place(y, whoosh(0.3, 400, 3000, 1.6, 0.55, 0.6, -0.5, 0.5), 0)
    y = place(y, to_stereo(add(flesh(0.35, 0.7, 1.0), clang(ru(900, 1200), 0.4, 1.2, 0.06, 0.6) * 0.4)), 0.2)
    return place(y, to_stereo(chain(0.3, 30) * 0.3), 0.0)


@M('soldado_gemido', 'Soldado Caido: gemido de soldado morto (ocioso/dor)', var=3, lufs=-18)
def _(v):
    return add(creature(ru(0.8, 1.3), ru(100, 125), [(0, 1), (0.5, 1.1), (1, 0.8)], 'o', 'u', 'baixo', 0.85, 0.5, 0.3, 2, 0.6),
               chain(1.0, 10) * 0.2)


@M('soldado_morte', 'Soldado Caido: desaba e vira cadaver fresco', var=2, lufs=-15)
def _(v):
    y = np.zeros(ns(1.8))
    y = place(y, creature(0.6, 110, [(0, 1.1), (1, 0.6)], 'a', 'u', 'baixo', 0.85, 0.6, 0.3, 2), 0)
    y = place(y, add(clang(600, 0.7, 1.0, 0.15, 0.5) * 0.5, clang(850, 0.6, 1.0, 0.12, 0.4) * 0.3, bones_rattle(0.6, 60)), 0.45)
    return place(y, add(thump(55, 0.5, 0.8, 0.12, 0.3), flesh(0.4, 1.0, 1.1) * 0.6), 0.55)
