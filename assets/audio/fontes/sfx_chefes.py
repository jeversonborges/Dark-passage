"""Sons dos tres chefes da Cripta da Trombeta Calada."""
from kit import *  # noqa
from registro import som
from sfx_monstros import keen, moan


def C(id, desc, var=1, lufs=-14, espaco='cripta', mix=0.25, loop=False):
    return som('chefes/' + id, var=var, lufs=lufs, espaco=espaco, mix=mix, desc=desc, loop=loop)


# ======================================================== ANDRAS (bloco gerado em sfx_andras.py)


# ======================================================== IRMA CELESTE, A CARPIDEIRA
@C('celeste_lamento_onda', 'Irma Celeste: onda de canto em anel (desviar pelos vaos)', var=2, espaco='ossario', mix=0.35, lufs=-13)
def _(v):
    d = 2.4
    y = np.zeros((ns(d), 2))
    nt = [hz('D5'), hz('F5')][v]
    k = keen(1.8, nt, 0.03)
    k2 = keen(1.8, nt * 1.5, 0.03) * 0.4
    y = place(y, widen(add(k, k2), 0.5) * 1.2, 0)
    ring = bp(white(1.8), np.linspace(400, 2500, ns(1.8)), 2) * env_pts(1.8, [(0, 0), (0.3, 1), (1.8, 0)])
    y = place(y, widen(ring * 0.6, 0.8), 0.1)
    return place(y, to_stereo(thump(60, 1.0, 0.5, 0.3, 0) * 0.4), 0.1)


@C('celeste_coro_loop', 'Irma Celeste: coro de cranios cantando, fase Coro (loop)', lufs=-15, espaco='ossario', mix=0.4, loop=True)
def _(v):
    d = 8.0
    y = np.zeros((ns(d + 1), 2))
    prog = [['D3', 'A3', 'D4', 'F4'], ['Bb2', 'F3', 'D4', 'F4'], ['C3', 'G3', 'C4', 'E4'], ['A2', 'E3', 'C#4', 'E4']]
    for i, ch in enumerate(prog):
        c = choir(ch, 2.6, 'o' if i % 2 == 0 else 'a', 'baixo', 4, 0.5, 0.6, vowel2='u' if i % 2 else 'a', vib=0.015)
        y = place(y, c * 1.0, i * 2.0 + 0.0)
        y = place(y, choir([n[:-1] + str(int(n[-1]) + 1) for n in ch[2:]], 2.6, 'a', 'alto', 3, 0.5, 0.6, vib=0.02) * 0.5, i * 2.0)
    for i in range(30):  # mandibulas batendo
        y = place(y, pan(wood_knock(ru(700, 1200), 0.08) * ru(0.1, 0.3), ru(-0.9, 0.9)), ru(0, d))
    return loopify(y[:ns(d + 1)], 1.0)


@C('celeste_coro_cala', 'Irma Celeste: coro silenciado (candelabros apagados), ela cai atordoada', espaco='ossario', mix=0.4)
def _(v):
    d = 3.0
    y = np.zeros((ns(d), 2))
    c = choir(['D3', 'A3', 'D4', 'F4'], 1.2, 'a', 'baixo', 4, 0.01, 1.1)
    c = varispeed(c, np.linspace(1.0, 0.5, len(c)))
    y = place(y, c * 0.9, 0)
    y = place(y, to_stereo(bones_rattle(1.0, 90)), 0.6)
    return place(y, to_stereo(add(cloth(0.6, 1.0, 2000), thump(55, 0.6, 0.8, 0.15, 0.3))), 1.6)


@C('celeste_baculo', 'Irma Celeste: golpe de baculo de femur', var=3, espaco='ossario')
def _(v):
    y = np.zeros((ns(1.2), 2))
    y = place(y, whoosh(0.4, 250, 1800, 1.0, 0.6, 0, 0.5, -0.5), 0)
    return place(y, to_stereo(add(wood_knock(ru(260, 340), 0.5) * 1.4, sat(thump(60, 0.6, 1.2, 0.12, 0.3), 2),
                                  crunch(0.2, 400, 700, 4000) * 0.4, bones_rattle(0.4, 40) * 0.4)), 0.3)


@C('celeste_grito', 'Irma Celeste: grito que causa medo (fase Requiem)', espaco='ossario', mix=0.4, lufs=-11)
def _(v):
    d = 3.0
    y = np.zeros((ns(d), 2))
    s = add(scream(2.4, 760, 'a', 'soprano', 3.5, 0.05), scream(2.4, 700, 'o', 'alto', 3, 0.04) * 0.6,
            scream(2.4, 1140, 'e', 'soprano', 3, 0.06) * 0.3)
    y = place(y, widen(s, 0.4), 0)
    return place(y, to_stereo(rumble(2.5, 50, 0.6) * env_exp(2.5, 0.8)), 0)


@C('celeste_lagrima_aviso', 'Irma Celeste: lagrima de cera prestes a cair do teto (aviso)', espaco='ossario', mix=0.3, lufs=-18)
def _(v):
    d = 1.0
    y = steam(d, 5000, 0.3, None) * 0.3
    return add(y, reverse(drip(1200, 0.4)) * 0.4, sine(hz('A6') * np.linspace(1, 1.2, ns(d)), d) * env_pts(d, [(0, 0), (d, 1)]) * 0.04)


@C('celeste_lagrima_cai', 'Irma Celeste: lagrima de cera cai (splash quente)', var=3, espaco='ossario', mix=0.3)
def _(v):
    y = add(splat(0.8, 1.6) * 1.2, sat(thump(70, 0.6, 1.2, 0.1, 0.4), 2) * 0.8)
    return add(y, steam(1.0, 4000, 0.01, 0.35) * 0.6)


@C('celeste_candelabro_apaga', 'Irma Celeste: jogador apaga um candelabro', espaco='ossario', mix=0.35)
def _(v):
    d = 1.5
    y = np.zeros(ns(d))
    y = place(y, bp(white(0.6), np.linspace(1500, 400, ns(0.6)), 1.0) * env_pts(0.6, [(0, 0), (0.05, 1), (0.6, 0)]), 0)
    y = place(y, clang(600, 1.0, 1.0, 0.3, 0.4) * 0.4, 0.1)
    return place(y, bell(hz('D4'), 1.2, 0.8, 0.8) * 0.2, 0.15)


@C('celeste_cauda_loop', 'Irma Celeste: cauda do habito se arrastando pelo chao (loop)', lufs=-22, espaco='ossario', mix=0.3, loop=True)
def _(v):
    d = 5.0
    y = cloth(d + 1, 1.0, 1500) + lp(white(d + 1), 600) * 0.4
    y *= 1 + 0.5 * np.sin(2 * np.pi * 0.4 * tt(d + 1))
    return loopify(y, 1.0)


@C('celeste_fala_curta', 'Irma Celeste: sussurro cantado (acompanha as falas em texto)', var=3, espaco='ossario', mix=0.4, lufs=-16)
def _(v):
    d = ru(1.4, 2.0)
    nt = [hz('D5'), hz('C5'), hz('F5')][v]
    k = keen(d, nt, 0.02) * 0.6
    return add(k, whispers(d, 2, 3) * 0.5)


@C('celeste_morte', 'Irma Celeste: morte (o canto se apaga ate o silencio)', espaco='infinito', mix=0.45, lufs=-13)
def _(v):
    d = 8.0
    y = np.zeros((ns(d), 2))
    k = keen(4.0, hz('D5'), 0.03)
    k = varispeed(k, np.linspace(1.0, 0.8, len(k)))
    k = k * np.linspace(1, 0, len(k)) ** 1.5
    y = place(y, widen(k), 0)
    c = choir(['D3', 'A3', 'D4'], 4.0, 'a', 'baixo', 4, 0.2, 3.5) * 0.5
    y = place(y, c, 0.2)
    y = place(y, to_stereo(bones_rattle(2.0, 40) * 0.5), 2.0)
    return place(y, to_stereo(breath(2.0, 'a', 'alto', False, 0.6)), 3.8)


# ======================================================== ZACARIAS, O ARAUTO DA TROMBETA CALADA
def zac_hum(d, f0=hz('D2'), intensity=1.0):
    """Voz com a boca costurada em volta do bocal: zumbido nasal abafado."""
    n = ns(d)
    f = vibrato(f0 * np.interp(np.linspace(0, 1, n), [0, 0.3, 1], [0.95, 1.05, 0.9]), d, 4, 0.01, 0.3)
    src = glottal(f, d, 0.01, 0.1, 0.2, 500)
    y = formant(src, 'u', 'baixo', 0.8) * 2.5
    y = add(y, bp(src, 250, 3) * 0.8)  # ressonancia nasal
    y = sat(lp(y, 1200) * intensity, 2)
    return y * env_pts(d, [(0, 0), (0.15, 1), (d - 0.3, 0.9), (d, 0)])


@C('zacarias_zumbido', 'Zacarias: zumbido grave atras do lacre (fala sem palavras / ocioso)', var=3, espaco='catedral', mix=0.4, lufs=-15)
def _(v):
    return zac_hum(ru(1.8, 2.6), [hz('D2'), hz('C2'), hz('E2')][v])


@C('zacarias_fase', 'Zacarias: muda de fase (urro abafado + correntes + halo)', espaco='catedral', mix=0.4, lufs=-11)
def _(v):
    d = 4.0
    y = np.zeros((ns(d), 2))
    y = place(y, widen(zac_hum(3.0, hz('D2'), 2.5) * 1.3, 0.3), 0)
    y = place(y, to_stereo(chain(2.5, 40, 0.5, 1.8)), 0.2)
    y = place(y, to_stereo(bell(hz('D3'), 3.5, 3, 1.0) * 0.5), 0)
    return place(y, to_stereo(steam(2.0, 6000, 0.05, 1.0) * 0.3), 0.3)


@C('zacarias_asa', 'Zacarias: golpe de asa em area (rajada enorme de penas)', var=2, espaco='catedral', mix=0.3, lufs=-12)
def _(v):
    d = 2.0
    y = np.zeros((ns(d), 2))
    y = place(y, widen(wings(1.0, 1, 2.2, 1.6) * 1.4), 0)
    y = place(y, whoosh(0.8, 120, 900, 0.7, 0.55, 0, -0.8, 0.8) * 1.3, 0.15)
    y = place(y, to_stereo(add(sat(thump(40, 1.0, 1.5, 0.25, 0.5), 2), debris(1.0, 80, 300, 4000, 0.3) * 0.6)), 0.55)
    return place(y, to_stereo(chain(0.8, 40, 0, 1.6) * 0.5), 0.4)


@C('zacarias_lanca_luz', 'Zacarias: lanca de luz a distancia (carga + impacto)', var=2, espaco='catedral', mix=0.3, lufs=-13)
def _(v):
    d = 2.2
    y = np.zeros((ns(d), 2))
    t = tt(0.7)
    charge = add(sine(np.linspace(hz('D5'), hz('D6'), ns(0.7)), 0.7) * 0.25, bp(white(0.7), np.linspace(2000, 7000, ns(0.7)), 4) * 0.5)
    charge = charge * env_pts(0.7, [(0, 0), (0.65, 1), (0.7, 0)], 2)
    y = place(y, widen(charge), 0)
    y = place(y, whoosh(0.3, 2000, 7000, 3, 0.3, 0.5, 0.6, -0.6) * 0.8, 0.65)
    boom = add(sat(thump(50, 1.2, 2.5, 0.25, 0.8), 2.5), bell(hz('A4'), 1.4, 1.0, 1.4) * 0.4, glass(3000, 0.8) * 0.4,
               debris(1.0, 120, 500, 6000, 0.3) * 0.6)
    return place(y, to_stereo(boom), 0.85)


@C('zacarias_corrente_arrancada', 'Zacarias: arranca uma corrente do teto, que cai e cria linha de dano', var=3, espaco='catedral', mix=0.3, lufs=-11)
def _(v):
    d = 4.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(add(creak(0.8, 20, 40, (220, 600, 1500), 1.4) * 0.8, zac_hum(0.9, hz('D2'), 2) * 0.6)), 0)
    y = place(y, to_stereo(add(clang(900, 1.2, 1.6, 0.4, 1.5), hp(white(0.05), 2000) * env_exp(0.05, 0.005) * 2)), 0.8)
    y = place(y, to_stereo(chain(1.2, 70, 0.3, 1.8) * 0.8), 0.85)
    line = np.zeros((ns(2.0), 2))
    for i in range(7):  # elos atingindo o chao em sequencia
        line = place(line, pan(add(sat(thump(48, 0.6, 1.2, 0.12, 0.7), 2), clang(ru(250, 400), 0.6, 1.0, 0.15, 0.6) * 0.5),
                               -0.8 + i * 0.27) * 0.8, i * 0.07)
    y = place(y, line, 1.6)
    return place(y, to_stereo(debris(2.0, 100, 300, 5000, 0.5) * 0.7), 1.65)


@C('zacarias_passos', 'Zacarias: passo de armadura de placas com correntes', var=4, espaco='catedral', mix=0.25, lufs=-15)
def _(v):
    d = 1.2
    return add(sat(thump(ru(35, 42), d, 1.2, 0.25, 0.4), 2), clang(ru(300, 400), 0.8, 1.0, 0.15, 0.4) * 0.4,
               chain(0.7, 30, 0, 1.6) * 0.4, debris(0.6, 40, 300, 3000, 0.15) * 0.3)


@C('zacarias_lacre_canaliza', 'Zacarias: tenta arrancar o lacre de chumbo (canalizacao, toca durante a barra)', espaco='catedral', mix=0.35, lufs=-12)
def _(v):
    d = 6.0
    y = np.zeros((ns(d), 2))
    env = env_pts(d, [(0, 0.2), (d, 1)], 1.5)
    y = place(y, to_stereo(creak(d, 10, 30, (180, 450, 1100), 1.5) * env * 0.8), 0)  # chumbo cedendo
    y = place(y, widen(zac_hum(d, hz('D2'), 1.0) * env * 1.2), 0)
    f = hz('D4')
    tr = brass(np.full(ns(d), f) * (1 + 0.02 * np.sin(2 * np.pi * 0.8 * tt(d))), d, 1.5, 0.2, 0.7, 1.5, 2.5)
    tr = lp(tr, 300 + 2500 * env)  # a trombeta tentando soar atraves do lacre
    y = place(y, widen(tr * env, 0.3) * 0.8, 0)
    y = place(y, choir(['D3', 'A3', 'D4', 'Eb4'], d, 'u', 'baixo', 4, d * 0.9, 0.2, vowel2='a') * 0.8, 0)
    y = place(y, to_stereo(rumble(d, 40, 1.0) * env), 0)
    return y


@C('zacarias_a_nota', 'Zacarias: A NOTA (canalizacao completa, dano massivo em toda a arena)', espaco='infinito', mix=0.35, lufs=-10)
def _(v):
    d = 9.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(add(clang(250, 2.0, 1.0, 0.8, 1.5), crunch(0.4, 600, 300, 4000, 2))), 0)  # lacre arrebenta
    f = hz('D4')
    for mul, g in [(1, 1.0), (0.5, 0.7), (1.5, 0.45), (2, 0.3), (1.0 * 2 ** (1 / 12), 0.2)]:
        tr = brass(np.full(ns(5.5), f * mul) * (1 + 0.004 * np.sin(2 * np.pi * 5 * tt(5.5))), 5.5, 0.12, 1.5, 1.5, 1.2, 3.5)
        y = place(y, widen(blp(tr, 6000, 2), 0.4) * g, 0.15)
    y = place(y, choir(['D2', 'A2', 'D3', 'A3', 'D4', 'F#4', 'A4'], 5.5, 'a', 'tenor', 5, 0.1, 2.5) * 1.2, 0.15)
    y = place(y, to_stereo(sat(thump(28, 4.0, 4, 1.5, 1.0), 3) * 1.4), 0.15)
    y = place(y, to_stereo(rumble(6.0, 35, 1.5) * env_pts(6, [(0, 1), (6, 0)])), 0.15)
    y = place(y, to_stereo(debris(5.0, 120, 200, 6000, 1.5) * 0.6), 0.2)
    for nt in ('D3', 'A3', 'D4'):
        y = place(y, to_stereo(bell(hz(nt), 6, 4, 1.0) * 0.35), 0.15)
    return y


@C('zacarias_nota_interrompida', 'Zacarias: canalizacao interrompida (trombeta engasga, lacre volta)', espaco='catedral', mix=0.35, lufs=-12)
def _(v):
    d = 3.0
    y = np.zeros((ns(d), 2))
    f = hz('D4')
    tr = brass(f * np.interp(np.linspace(0, 1, ns(0.8)), [0, 0.5, 1], [1, 0.95, 0.6]), 0.8, 0.02, 0.4, 1.0, 2.0, 3)
    y = place(y, to_stereo(blp(tr, 4000)), 0)
    y = place(y, to_stereo(add(clang(220, 1.5, 0.9, 0.5, 1.2), sat(thump(40, 1.0, 2, 0.25, 0.5), 2))), 0.6)
    return place(y, to_stereo(zac_hum(1.8, hz('C2'), 1.5) * 0.8), 0.8)


@C('zacarias_morte', 'Zacarias: morte (correntes caem, halo esfria, ultimo sopro na trombeta)', espaco='infinito', mix=0.45, lufs=-11)
def _(v):
    d = 11.0
    y = np.zeros((ns(d), 2))
    y = place(y, widen(zac_hum(2.5, hz('D2'), 2.0) * env_pts(2.5, [(0, 1), (2.5, 0)])), 0)
    for i in range(6):
        y = place(y, pan(chain(1.5, 50, 0.4, 1.8), ru(-0.8, 0.8)) * 0.6, 0.5 + i * 0.3)
    y = place(y, to_stereo(add(sat(thump(28, 3.0, 3, 1.0, 0.8), 3) * 1.3, clang(200, 3.0, 0.8, 1.2, 1.0) * 0.6,
                               debris(3.0, 100, 200, 4000, 0.8) * 0.7)), 2.4)
    y = place(y, to_stereo(steam(3.5, 5000, 0.1, 1.5) * 0.5), 3.0)  # halo incandescente esfriando
    f = hz('D4')
    last = brass(f * np.interp(np.linspace(0, 1, ns(3.0)), [0, 1], [1.0, 0.85]), 3.0, 0.6, 2.0, 0.5, 0.5, 1.5)
    y = place(y, widen(lp(last, 1800) * 0.6), 5.0)
    y = place(y, choir(['D3', 'A3', 'D4', 'F#4'], 5.0, 'a', 'soprano', 4, 2.0, 2.8) * 0.5, 5.2)
    return place(y, to_stereo(bell(hz('D3'), 6, 5, 0.9) * 0.4), 5.0)
