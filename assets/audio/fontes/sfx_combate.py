"""Sons de combate: golpes no ar, impactos, armas de fogo, eventos e status."""
from kit import *  # noqa
from registro import som


# ======================================================== golpes no ar
@som('combate/ar_leve', var=4, lufs=-20, espaco='rua', mix=0.08, desc='golpe rapido no ar (adaga, punhos, espada leve)')
def _(v):
    d = ru(0.22, 0.3)
    return whoosh(d, ru(400, 600), ru(2200, 3200), 1.4, ru(0.4, 0.55), 0.0, ru(-0.6, -0.2), ru(0.2, 0.6))


@som('combate/ar_pesado', var=4, lufs=-18, espaco='rua', mix=0.1, desc='golpe pesado no ar (machado, marreta, braco mutante)')
def _(v):
    d = ru(0.45, 0.6)
    w = whoosh(d, ru(150, 220), ru(900, 1300), 0.9, ru(0.55, 0.65), 0.0, -0.4, 0.4, 0.6)
    w += to_stereo(lp(white(d), 250) * env_pts(d, [(0, 0), (d * 0.6, 1), (d, 0)], 2) * 0.8)
    return w


@som('combate/ar_lamina', var=4, lufs=-19, espaco='rua', mix=0.1, desc='lamina cortando o ar com assobio metalico (espada, foice, lanca)')
def _(v):
    d = ru(0.3, 0.4)
    return whoosh(d, ru(500, 700), ru(3000, 4200), 2.2, ru(0.45, 0.55), 1.0, ru(-0.7, -0.3), ru(0.3, 0.7))


@som('combate/ar_corrente', var=3, lufs=-19, espaco='rua', mix=0.1, desc='corrente/chicote cortando o ar')
def _(v):
    d = 0.5
    w = whoosh(d, 300, 2000, 1.2, 0.6, 0.0, -0.5, 0.5)
    w += to_stereo(chain(d, 50) * env_pts(d, [(0, 0.3), (0.3, 1), (d, 0)]) * 0.7)
    crack = hp(white(0.05), 2000) * env_exp(0.05, 0.004) * 1.5
    return place(w, crack, 0.3)


# ======================================================== impactos
def _impact(kind, size=1.0):
    d = 0.6 * size
    if kind == 'carne':
        y = flesh(d, ru(0.7, 1.2), size)
        y += thump(ru(55, 75) / size, d, 1.8, 0.09 * size, 0.2) * 0.8
    elif kind == 'metal':
        y = clang(ru(700, 1100) / size, d * 1.5, 1.3, 0.25, 0.8) * 0.7
        y = np.concatenate([y[:ns(d)], np.zeros(0)])
        y += thump(ru(80, 110), d, 1.0, 0.06, 0.4) * 0.8
        y += sparks(d, 60)[:ns(d)] * 0.3
    elif kind == 'osso':
        y = crunch(d, 700, 800, 6000, size) * 1.2 + wood_knock(ru(300, 500), d) * 0.7
        y += thump(90, d, 1.2, 0.05, 0.1) * 0.6
    return y


@som('combate/golpe_leve', var=5, lufs=-16, espaco='rua', mix=0.12, desc='acerto leve em carne (evento golpe_leve)')
def _(v):
    return _impact('carne', ru(0.75, 0.9))


@som('combate/golpe_pesado', var=4, lufs=-14, espaco='rua', mix=0.15, desc='acerto pesado em carne (evento golpe_pesado)')
def _(v):
    d = 1.0
    y = _impact('carne', 1.25)
    y = np.concatenate([y, np.zeros(ns(d) - len(y))]) if len(y) < ns(d) else y[:ns(d)]
    y += sat(thump(42, d, 2.5, 0.22, 0.1), 2) * 0.9
    y += crunch(d, 250, 500, 3000, 0.8) * 0.4
    return y


@som('combate/golpe_metal', var=4, lufs=-16, espaco='rua', mix=0.15, desc='acerto em armadura/metal')
def _(v):
    return _impact('metal', ru(0.8, 1.1))


@som('combate/golpe_osso', var=4, lufs=-16, espaco='rua', mix=0.15, desc='acerto em esqueleto/osso')
def _(v):
    return _impact('osso', ru(0.8, 1.1))


@som('combate/estalo_metal', var=3, lufs=-15, espaco='rua', mix=0.12, desc='camada extra do critico: estalo agudo metalico')
def _(v):
    d = 0.9
    y = clang(ru(1800, 2400), d, 2.0, 0.35, 1.5)
    y += hp(white(d), 3000) * env_exp(d, 0.006) * 1.5
    y += bp(white(d), 6000, 3) * env_exp(d, 0.05) * 0.3
    return y


@som('combate/golpe_critico', var=3, lufs=-13, espaco='rua', mix=0.18, desc='acerto critico completo (carne + estalo metalico + grave)')
def _(v):
    d = 1.3
    base = _impact('carne', 1.2)
    st = clang(ru(1900, 2300), d, 2.0, 0.22, 1.5)
    boom = sat(thump(38, d, 3.5, 0.35, 0), 3)
    rev = reverse(hp(white(0.12), 2000) * env_exp(0.12, 0.04)) * 0.7
    y = np.zeros(ns(d) + ns(0.12))
    y = place(y, rev, 0)
    y = place(y, base * 1.1, 0.12)
    y = place(y, st * 0.55, 0.12)
    y = place(y, boom * 0.9, 0.12)
    return y


@som('combate/sino_curto', var=3, lufs=-17, espaco='catedral', mix=0.25, desc='camada extra do golpe excelente: sino curto')
def _(v):
    f = hz(['A5', 'G5', 'B5'][v])
    return add(bell(f, 2.0, 1.2, 1.2) * 0.8, bell(f * 1.5, 1.5, 0.8, 1.2) * 0.3)


@som('combate/golpe_excelente', var=3, lufs=-14, espaco='rua', mix=0.18, desc='golpe excelente completo (impacto + sino curto)')
def _(v):
    d = 1.8
    y = np.zeros(ns(d))
    y = place(y, _impact('carne', 1.0), 0)
    y = place(y, bell(hz(['A5', 'G5', 'B5'][v]), 1.6, 1.0, 1.3) * 0.35, 0.01)
    y = place(y, bell(hz(['E6', 'D6', 'F#6'][v]), 1.2, 0.7, 1.3) * 0.15, 0.03)
    return y


@som('combate/errou', var=3, lufs=-22, espaco='rua', mix=0.1, desc='ataque errou (vento)')
def _(v):
    d = 0.5
    return whoosh(d, 250, 1400, 0.7, 0.35, 0, ru(-0.3, 0), ru(0.4, 0.8), 0.8) * 0.8


@som('combate/esquivou', var=3, lufs=-19, espaco='rua', mix=0.1, desc='esquiva: roupa + poeira')
def _(v):
    d = 0.5
    y = whoosh(d, 300, 1600, 0.8, 0.4, 0, ru(0.4, 0.7), ru(-0.7, -0.4))
    y += to_stereo(cloth(d, 1.2, 3000))
    y = place(y, debris(0.4, 60, 300, 3000, 0.12) * 0.7, 0.2)
    return y


@som('combate/abate', var=4, lufs=-14, espaco='rua', mix=0.18, desc='inimigo morre: osso quebrando + corpo caindo')
def _(v):
    d = 1.4
    y = np.zeros(ns(d))
    y = place(y, _impact('carne', 1.1), 0)
    y = place(y, crunch(0.35, 900, 600, 5000, 1.4) * 1.1, 0.02)
    y = place(y, sat(thump(40, 0.9, 2.5, 0.25, 0), 2) * 0.8, 0.0)
    # corpo caindo
    fall = add(lp(white(0.4), 600) * env_exp(0.4, 0.06) * 1.2, thump(60, 0.4, 0.8, 0.08, 0.2))
    y = place(y, fall * 0.7, ru(0.45, 0.6))
    y = place(y, debris(0.5, 40, 300, 2500, 0.15) * 0.4, 0.55)
    return y


@som('combate/corpo_cai', var=3, lufs=-18, espaco='rua', mix=0.12, desc='corpo tombando no chao')
def _(v):
    d = 0.8
    y = np.zeros(ns(d))
    y = place(y, add(lp(white(0.3), 500) * env_exp(0.3, 0.05), thump(55, 0.4, 0.8, 0.09, 0.2)), 0)
    y = place(y, add(lp(white(0.25), 700) * env_exp(0.25, 0.04), thump(70, 0.3, 0.6, 0.06, 0.2)) * 0.6, ru(0.12, 0.2))
    y = place(y, add(cloth(0.3, 0.6), debris(0.4, 30, 400, 2500, 0.1) * 0.6), 0.05)
    return y


@som('combate/abate_chefe', var=1, lufs=-12, espaco='catedral', mix=0.35, desc='chefe morre (camera lenta): sucção, explosao grave, sino e coro')
def _(v):
    d = 6.0
    y = np.zeros((ns(d), 2))
    rise = reverse(to_stereo(hp(white(1.2), 300) * env_exp(1.2, 0.5))) * 0.6
    y = place(y, rise, 0)
    boom = sat(thump(32, 3.0, 3, 1.0, 0.3), 3) * 1.4
    y = place(y, boom, 1.2)
    y = place(y, to_stereo(crunch(0.5, 900, 500, 5000, 2) * 0.8), 1.2)
    y = place(y, to_stereo(bell(hz('D3'), 5, 4, 1)) * 0.8, 1.2)
    y = place(y, to_stereo(bell(hz('A3'), 5, 3, 1)) * 0.4, 1.25)
    y = place(y, choir(['D3', 'A3', 'D4', 'F4'], 3.8, 'a', 'tenor', 4, 0.02, 2.5) * 0.9, 1.2)
    y = place(y, to_stereo(debris(3, 30, 200, 2500, 1.2) * 0.4), 1.3)
    return y


@som('combate/postura_quebrada', var=2, lufs=-14, espaco='abatedouro', mix=0.2, desc='postura do inimigo quebrou: estilhaco + queda grave')
def _(v):
    d = 1.6
    y = np.zeros(ns(d))
    y = place(y, glass(ru(1800, 2400), 1.2) * 0.6, 0)
    y = place(y, glass(ru(2800, 3400), 1.0) * 0.4, 0.02)
    y = place(y, debris(1.0, 200, 2000, 9000, 0.25) * 0.8, 0.01)
    y = place(y, clang(600, 1.2, 1.0, 0.4, 1.0) * 0.5, 0)
    t = tt(1.4)
    drop = np.sin(2 * np.pi * np.cumsum(220 * np.exp(-t / 0.25) + 35) / SR) * env_exp(1.4, 0.4) * 0.8
    y = place(y, sat(drop, 2), 0.02)
    return y


@som('combate/bloqueio', var=3, lufs=-15, espaco='rua', mix=0.15, desc='bloqueio/postura do chefe: metal seco + faiscas')
def _(v):
    d = 0.8
    y = clang(ru(500, 800), d, 1.0, 0.12, 1.2) * 0.8
    y += thump(120, d, 0.5, 0.04, 0.6) * 0.6
    y += sparks(d, 90)[:ns(d)] * 0.5
    return y


@som('combate/jogador_ferido', var=4, lufs=-16, espaco='rua', mix=0.1, desc='jogador recebe dano: impacto abafado + gemido curto')
def _(v):
    d = 0.7
    y = np.zeros(ns(d))
    y = place(y, flesh(0.4, 0.6, 1.1) * 0.8, 0)
    g = creature(ru(0.22, 0.32), ru(110, 140), [(0, 1.1), (0.3, 1.2), (1, 0.8)], 'a', 'o', 'baixo', 1.0,
                 growl=0.15, sub=0.0, drive=1.5, breath=0.5)
    y = place(y, lp(g, 3500) * 0.35, 0.03)
    return y


@som('combate/jogador_morre', var=1, lufs=-14, espaco='catedral', mix=0.35, desc='jogador morre: impacto, zumbido no ouvido, coracao parando, coro')
def _(v):
    d = 7.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(sat(thump(35, 2, 3, 0.6, 0.3), 2.5) * 1.3), 0)
    y = place(y, to_stereo(flesh(0.6, 1.2, 1.3)), 0)
    t = tt(5)
    tin = np.sin(2 * np.pi * 3800 * t) * env_pts(5, [(0, 0), (0.05, 1), (5, 0)], 2) * 0.05
    y = place(y, to_stereo(tin), 0.05)
    hb = np.zeros(ns(5))
    for i, (at, g) in enumerate([(0.6, 1.0), (1.6, 0.8), (2.9, 0.6), (4.5, 0.4)]):
        hb = place(hb, heartbeat(0.6, 60, g), at)
    y = place(y, to_stereo(hb[:ns(5)]) * 1.2, 0)
    y = place(y, choir(['D2', 'A2', 'D3', 'F3'], 5.5, 'o', 'baixo', 5, 1.5, 2.5) * 0.9, 0.4)
    y = place(y, to_stereo(bell(hz('D2'), 5, 4, 0.8)) * 0.5, 0.4)
    return y


@som('combate/corpo_ferido_monstro', var=4, lufs=-17, espaco='rua', mix=0.1, desc='monstro recebe dano generico (sem voz)')
def _(v):
    return flesh(0.4, ru(0.8, 1.3), ru(0.9, 1.2))


# ======================================================== cura / escudo
@som('combate/cura', var=2, lufs=-18, espaco='catedral', mix=0.3, desc='cura recebida: brilho quente subindo')
def _(v):
    d = 1.8
    y = np.zeros((ns(d), 2))
    notes = ['D5', 'F5', 'A5', 'D6'] if v == 0 else ['A4', 'D5', 'E5', 'A5']
    for i, nt in enumerate(notes):
        y = place(y, pan(bell(hz(nt), 1.4, 0.6, 1.4) * 0.25, -0.5 + i * 0.33), i * 0.07)
    sw = bp(white(d), np.linspace(800, 5000, ns(d)), 3) * env_pts(d, [(0, 0), (0.4, 1), (d, 0)]) * 0.6
    y = place(y, widen(sw, 0.6), 0)
    return y


@som('combate/escudo_absorve', var=3, lufs=-17, espaco='rua', mix=0.12, desc='escudo absorve golpe: baque energetico')
def _(v):
    d = 0.7
    t = tt(d)
    y = thump(ru(140, 180), d, 0.6, 0.12, 0.2) * 0.8
    y += sine(ru(380, 420) * (1 + 0.3 * np.exp(-t / 0.05)), d) * env_exp(d, 0.18) * 0.5
    y += zap(d, 0.25)[:ns(d)] * env_exp(d, 0.08)
    return y


@som('combate/escudo_quebra', var=1, lufs=-14, espaco='abatedouro', mix=0.2, desc='escudo quebra: estilhaco + descarga')
def _(v):
    d = 1.4
    y = np.zeros(ns(d))
    y = place(y, add(glass(2600, 1.0), glass(1900, 1.2) * 0.7), 0)
    y = place(y, debris(1.0, 300, 3000, 10000, 0.3), 0.01)
    y = place(y, zap(0.6, 0.8) * env_exp(0.6, 0.2), 0)
    y = place(y, thump(60, 0.8, 2, 0.2, 0.2), 0)
    return y


# ======================================================== telegrafos / fases
@som('combate/telegrafo_inicio', var=2, lufs=-17, espaco='cripta', mix=0.25, desc='aviso de ataque forte do inimigo (area vermelha aparece)')
def _(v):
    d = 1.2
    t = tt(d)
    env = env_pts(d, [(0, 0), (d * 0.85, 1), (d, 0)], 2)
    y = sat(saw(np.linspace(55, 75, ns(d)), d) * 0.5 + sine(110, d) * 0.4, 1.5)
    y = lp(y, 200 + 1600 * env) * env
    y += bp(white(d), 400 + 3000 * env, 2) * env * 0.4
    y += reverse(bell(hz('C#4'), d, 0.5, 1.2))[:ns(d)] * 0.2
    return y


@som('combate/telegrafo_impacto', var=2, lufs=-13, espaco='cripta', mix=0.25, desc='ataque forte do inimigo cai: explosao grave + detritos')
def _(v):
    d = 1.8
    y = sat(thump(36, d, 3.5, 0.45, 0.6), 3) * 1.3
    y += debris(d, 80, 300, 4000, 0.4) * 0.8
    y += lp(brown(d), 300) * env_exp(d, 0.4) * 1.0
    return y


@som('combate/chefe_fase', var=1, lufs=-13, espaco='catedral', mix=0.3, desc='chefe muda de fase: sino grave + baque + coro')
def _(v):
    d = 5.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(sat(thump(34, 2.5, 3, 0.8, 0.5), 2) * 1.2), 0)
    y = place(y, to_stereo(bell(hz('C#3'), 4.5, 3.5, 1.0)) * 0.8, 0)
    y = place(y, to_stereo(bell(hz('G3'), 4, 3, 1.0)) * 0.35, 0.02)  # tritono
    y = place(y, choir(['C#3', 'G3', 'C#4'], 3.0, 'a', 'baixo', 5, 0.03, 2.0) * 0.8, 0)
    y = place(y, to_stereo(rumble(4, 50, 0.6) * env_exp(4, 1.4)), 0)
    return y


# ======================================================== armas de fogo e besta
@som('combate/tiro_escopeta', var=3, lufs=-12, espaco='rua', mix=0.22, desc='escopeta de cano duplo (Humano)')
def _(v):
    d = 1.6
    y = gunshot(d, 1.4, 1.2, 55)
    y += debris(d, 120, 2000, 8000, 0.05) * 0.4
    return y


@som('combate/tiro_pistola', var=3, lufs=-14, espaco='rua', mix=0.2, desc='pistola / tiro unico')
def _(v):
    return gunshot(1.2, 0.8, 1.2, 90)


@som('combate/tiro_mosquete', var=2, lufs=-13, espaco='rua', mix=0.25, desc='mosquete de polvora negra (chiado de pavio + estampido)')
def _(v):
    d = 2.0
    y = np.zeros(ns(d))
    y = place(y, steam(0.15, 6000, 0.005, 0.04) * 0.4 + hp(crackle(0.15, 200, 0.0005), 3000) * 0.5, 0)
    y = place(y, gunshot(1.8, 1.6, 0.9, 50), 0.12)
    return y


@som('combate/besta_disparo', var=3, lufs=-17, espaco='rua', mix=0.1, desc='besta: estalo da corda + virote zunindo')
def _(v):
    d = 0.6
    t = tt(d)
    twang = pluck(ru(110, 140), d, 0.7, 0.99) * 0.6
    thunk = wood_knock(ru(220, 280), d) * 1.2
    zz = whoosh(0.35, 1500, 4000, 2, 0.2, 0.3, 0, 0.6)
    y = to_stereo(twang + thunk)
    return place(y, zz * 0.6, 0.02)


@som('combate/recarga', var=2, lufs=-18, espaco='quarto', mix=0.1, desc='recarga: cartuchos + trava')
def _(v):
    d = 1.0
    y = np.zeros(ns(d))
    y = place(y, metal(0.15, 1300, 10, decay=0.03, bright=1.4), 0)  # abre
    y = place(y, add(coin(2600, 0.2) * 0.3, wood_knock(700, 0.1) * 0.3), 0.25)  # cartucho
    y = place(y, add(coin(2400, 0.2) * 0.3, wood_knock(650, 0.1) * 0.3), 0.42)
    y = place(y, reload_click(0.35), 0.62)
    return y


@som('combate/projetil_zunido', var=3, lufs=-20, espaco='rua', mix=0.08, desc='bala/projetil passando perto')
def _(v):
    d = 0.35
    t = tt(d)
    f = 2800 * (1 - 0.35 * t / d)
    y = sine(f, d) * env_pts(d, [(0, 0), (d * 0.4, 1), (d, 0)], 2) * 0.3
    y += bp(white(d), f, 3) * env_pts(d, [(0, 0), (d * 0.4, 1), (d, 0)], 2)
    return pan(y, np.linspace(-0.8, 0.8, ns(d)))


@som('combate/impacto_bala', var=3, lufs=-17, espaco='rua', mix=0.1, desc='bala acertando (carne/pedra)')
def _(v):
    d = 0.5
    y = flesh(d, 0.8, 0.7) * 0.8 + debris(d, 150, 1500, 7000, 0.06) * 0.6
    y += hp(white(d), 3000) * env_exp(d, 0.003) * 1.2
    return y


@som('combate/sangue_jorro', var=3, lufs=-19, espaco='rua', mix=0.08, desc='jorro de sangue')
def _(v):
    return splat(0.6, ru(0.8, 1.1))


# ======================================================== status
@som('status/sangramento', var=1, lufs=-19, espaco='rua', mix=0.1, desc='status aplicado: sangramento')
def _(v):
    d = 0.8
    y = flesh(0.3, 1.5, 0.8) * 0.6
    y = place(np.zeros(ns(d)), y, 0)
    for i in range(4):
        y = place(y, drip(ru(700, 1100), 0.2) * 0.4, 0.2 + i * ru(0.08, 0.14))
    return y


@som('status/sangramento_tick', var=3, lufs=-24, espaco='rua', mix=0.08, desc='tick de sangramento (gotas)')
def _(v):
    y = np.zeros(ns(0.4))
    for i in range(2):
        y = place(y, add(drip(ru(600, 1000), 0.2), splat(0.15, 0.6) * 0.3), i * ru(0.06, 0.12))
    return y


@som('status/veneno', var=1, lufs=-19, espaco='rua', mix=0.1, desc='status aplicado: veneno (borbulhar + chiado acido)')
def _(v):
    d = 1.0
    y = liquid(d, 30, 250, 700) * env_pts(d, [(0, 0), (0.1, 1), (d, 0)]) * 0.9
    y += steam(d, 5000, 0.05, 0.3) * 0.4
    return y


@som('status/veneno_tick', var=3, lufs=-24, espaco='rua', mix=0.08, desc='tick de veneno')
def _(v):
    return liquid(0.35, 25, 200, 600) * env_exp(0.35, 0.15) + steam(0.35, 5000, 0.01, 0.08) * 0.2


@som('status/queimadura', var=1, lufs=-18, espaco='rua', mix=0.1, desc='status aplicado: queimadura (labareda)')
def _(v):
    return whoomp(1.0, 80) * 0.9


@som('status/queimadura_tick', var=3, lufs=-23, espaco='rua', mix=0.08, desc='tick de queimadura (chiado de carne)')
def _(v):
    d = 0.4
    return steam(d, 4500, 0.01, 0.12) * 0.6 + bbp(crackle(d, 120, 0.0008), 1500, 9000) * env_exp(d, 0.15)


@som('status/lento', var=1, lufs=-19, espaco='cripta', mix=0.2, desc='status aplicado: lentidao (som grosso que desacelera)')
def _(v):
    d = 1.0
    t = tt(d)
    f = 300 * np.exp(-t / 0.4) + 80
    y = lp(saw(f, d), 900) * env_exp(d, 0.35, 0.01) * 0.8
    y += lp(liquid(d, 10, 150, 300), 1500) * env_exp(d, 0.4) * 0.6
    return y


@som('status/enraizado', var=1, lufs=-18, espaco='rua', mix=0.12, desc='status aplicado: enraizado (raizes rangendo e prendendo)')
def _(v):
    d = 0.9
    y = creak(0.7, 30, 60, (200, 520, 1100)) * 0.8
    y = place(np.zeros(ns(d)), y, 0)
    y = place(y, debris(0.5, 80, 200, 2000, 0.15), 0)
    y = place(y, crunch(0.2, 300, 400, 2500), 0.55)
    return y


@som('status/atordoado', var=1, lufs=-19, espaco='catedral', mix=0.3, desc='status aplicado: atordoado (sinos girando no ouvido)')
def _(v):
    d = 1.6
    y = np.zeros((ns(d), 2))
    for i in range(6):
        y = place(y, pan(bell(hz('E6') * (1 + 0.06 * (i % 3)), 0.8, 0.35, 1.5) * 0.2, np.sin(i * 1.3)), i * 0.12)
    y = place(y, to_stereo(thump(70, 0.5, 1, 0.1, 0.3)), 0)
    return y


@som('status/derrubado', var=1, lufs=-16, espaco='rua', mix=0.12, desc='status aplicado: derrubado')
def _(v):
    d = 0.8
    y = thump(50, d, 1.5, 0.15, 0.4) + lp(white(d), 700) * env_exp(d, 0.05) + debris(d, 60, 300, 3000, 0.2) * 0.6
    return y


@som('status/cegueira', var=1, lufs=-20, espaco='cripta', mix=0.2, desc='status aplicado: cegueira (zumbido agudo)')
def _(v):
    d = 1.5
    t = tt(d)
    y = sine(3000 + 300 * np.sin(2 * np.pi * 7 * t), d) * env_pts(d, [(0, 0), (0.03, 1), (d, 0)], 2) * 0.15
    y += hp(white(d), 4000) * env_exp(d, 0.15) * 0.5
    return y


@som('status/silenciado', var=1, lufs=-20, espaco='cripta', mix=0.25, desc='status aplicado: silenciado (sopro abafado "shhh")')
def _(v):
    d = 1.0
    y = bp(white(d), 3500, 1.2) * env_pts(d, [(0, 0), (0.1, 1), (d, 0)], 1.5)
    y = lp(y, np.linspace(8000, 600, ns(d)))
    return y


@som('status/provocado', var=1, lufs=-17, espaco='rua', mix=0.15, desc='status aplicado: provocado (rosnado curto)')
def _(v):
    return creature(0.6, 85, [(0, 0.9), (0.3, 1.1), (1, 0.9)], 'a', 'a', 'baixo', 0.75, 0.8, 0.6, 3)


@som('status/marcado', var=1, lufs=-19, espaco='catedral', mix=0.3, desc='status aplicado: marcado (badalada sinistra)')
def _(v):
    return add(bell(hz('F#4'), 2.5, 1.5, 1.1) * 0.6, bell(hz('C5'), 2.0, 1.0, 1.1) * 0.3)


@som('status/profecia', var=1, lufs=-19, espaco='ossario', mix=0.4, desc='status aplicado: profecia (sussurros)')
def _(v):
    return whispers(1.6, 5, 4)


@som('status/cura_reduzida', var=1, lufs=-20, espaco='rua', mix=0.15, desc='status aplicado: cura reduzida (acorde abafado caindo)')
def _(v):
    d = 1.0
    t = tt(d)
    y = 0
    for f in (440, 523, 660):
        y = y + sine(f * (1 - 0.15 * t / d), d) * env_exp(d, 0.35, 0.01) * 0.2
    return lp(y, 1500)


@som('status/exausto', var=1, lufs=-19, espaco='rua', mix=0.1, desc='status aplicado: exausto (respiracao pesada)')
def _(v):
    d = 2.0
    y = np.zeros(ns(d))
    for i in range(2):
        y = place(y, breath(0.45, 'a', 'baixo', True, 0.8), i * 0.95)
        y = place(y, breath(0.45, 'o', 'baixo', False, 1.0), i * 0.95 + 0.45)
    return lp(y, 5000)
