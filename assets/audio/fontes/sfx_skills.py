"""Sons das 36 habilidades (design/skills-itens/skills.json, campo 'som')."""
from kit import *  # noqa
from registro import som


def S(id, desc, lufs=-15, espaco='rua', mix=0.18, var=1):
    return som('skills/' + id, var=var, lufs=lufs, espaco=espaco, mix=mix, desc=desc)


def mono_choir_hit(notes, dur, vowel='a', voz='tenor', lpf=2500):
    c = choir(notes, dur, vowel, voz, 4, 0.02, dur * 0.8)
    return blp(c, lpf, 2)


# ======================================================== ANJO
@S('anjo_lamina_veredito', 'Lamina do Veredito: lamina pesada + coro curto abafado', var=3)
def _(v):
    d = 1.4
    y = whoosh(0.4, 400, 3500, 2, 0.6, 1.0, -0.5, 0.4)
    y = place(np.zeros((ns(d), 2)), y, 0)
    y = place(y, to_stereo(flesh(0.5, 0.6, 1.2) + thump(55, 0.5, 2, 0.12, 0.2) * 0.8), 0.25)
    y = place(y, to_stereo(clang(1500, 0.6, 1.4, 0.12, 0.4) * 0.25), 0.25)
    y = place(y, mono_choir_hit([['D4', 'A4', 'D5'], ['E4', 'B4', 'E5'], ['C4', 'G4', 'C5']][v], 1.0, 'a', 'tenor', 2200) * 0.7, 0.24)
    return y


@S('anjo_toque_graca', 'Toque de Graca: sino pequeno e luz subindo', espaco='catedral', mix=0.3)
def _(v):
    d = 2.2
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(bell(hz('A5'), 2.0, 1.3, 1.3) * 0.5), 0)
    y = place(y, to_stereo(bell(hz('E6'), 1.6, 0.9, 1.3) * 0.25), 0.12)
    y = place(y, choir(['A4', 'C#5', 'E5'], 1.8, 'u', 'soprano', 3, 0.3, 1.0, vowel2='a') * 0.4, 0.05)
    sh = bp(white(1.5), np.linspace(2000, 8000, ns(1.5)), 4) * env_pts(1.5, [(0, 0), (0.3, 1), (1.5, 0)]) * 0.4
    return place(y, widen(sh), 0)


@S('anjo_asas_ascensao', 'Asas da Ascensao: duas batidas pesadas de asa e pouso', mix=0.15)
def _(v):
    d = 1.6
    y = np.zeros((ns(d), 2))
    y = place(y, widen(wings(0.9, 2, 1.4, 1.2)), 0)
    y = place(y, whoosh(0.5, 200, 1500, 0.8, 0.5, 0, -0.6, 0.6), 0.6)
    y = place(y, to_stereo(add(cloth(0.5, 1.2, 4000), thump(60, 0.5, 0.8, 0.12, 0.2) * 0.7)), 1.05)
    return y


@S('anjo_halo_ardente', 'Halo Ardente: acorde de orgao + anel de fogo', espaco='catedral', mix=0.3, lufs=-14)
def _(v):
    d = 3.0
    y = np.zeros((ns(d), 2))
    y = place(y, organ(['D3', 'A3', 'D4', 'F#4', 'A4'], 2.6, 'pleno', 0.003, 0.02, 1.5) * 1.2, 0)
    y = place(y, to_stereo(whoomp(1.2, 70) * 0.8), 0)
    ring = fire(2.4, 0.5, 40) * env_pts(2.4, [(0, 0), (0.15, 1), (2.4, 0)])
    return place(y, widen(ring, 0.6), 0.1)


@S('anjo_sentenca', 'Sentenca: martelo de juiz / carimbo', espaco='catedral', mix=0.3, lufs=-13)
def _(v):
    d = 3.0
    y = np.zeros((ns(d), 2))
    gav = add(wood_knock(160, 0.5) * 1.6, sat(thump(48, 1.5, 2.5, 0.35, 0.4), 2.5) * 1.2)
    y = place(y, to_stereo(reverse(hp(white(0.25), 1500) * env_exp(0.25, 0.08))) * 0.4, 0)
    y = place(y, to_stereo(gav), 0.25)
    y = place(y, to_stereo(bell(hz('D3'), 2.6, 2.0, 1.0) * 0.6), 0.25)
    y = place(y, to_stereo(debris(1.0, 50, 300, 3000, 0.3) * 0.4), 0.27)
    return y


@S('anjo_trombeta_juizo', 'Trombeta do Juizo (ultimate): trombeta longa distorcida + coro + tremor', espaco='catedral', mix=0.35, lufs=-12)
def _(v):
    d = 6.0
    y = np.zeros((ns(d), 2))
    f = hz('D4')
    tr = brass(np.concatenate([np.linspace(f * 0.94, f, ns(0.3)), np.full(ns(3.7), f)]), 4.0, 0.25, 1.0, 1.2, 0.8, 2.5)
    tr = add(tr, brass(f * 1.5, 4.0, 0.35, 1.0, 1.0, 0.6, 2.0) * 0.5, brass(f * 0.5, 4.0, 0.3, 1.0, 1.0, 0.8, 2.5) * 0.6)
    y = place(y, widen(blp(peq(tr, 1500, 4, 0.8), 5500, 3), 0.3), 0)
    y = place(y, choir(['D3', 'A3', 'D4', 'F#4'], 4.5, 'a', 'tenor', 5, 1.0, 1.5) * 0.7, 0.3)
    y = place(y, to_stereo(rumble(5, 45, 0.8) * env_pts(5, [(0, 0), (2, 1), (5, 0)])), 0.2)
    y = place(y, to_stereo(sat(thump(34, 2.0, 3, 0.7, 0.5), 2.5) * 1.1), 3.6)
    y = place(y, to_stereo(debris(2.0, 60, 300, 4000, 0.6) * 0.5), 3.6)
    return y


# ======================================================== CULTISTA
@S('cultista_sangria', 'Sangria: chiado umido (sangue arrancado do alvo)', var=2)
def _(v):
    d = 1.0
    y = np.zeros((ns(d), 2))
    sw = bp(white(0.7) * (1 + 3 * np.abs(lp(white(0.7), 50) * 8)), np.linspace(600, 2500, ns(0.7)), 2.5)
    sw *= env_pts(0.7, [(0, 0), (0.2, 1), (0.7, 0)])
    y = place(y, pan(sw, np.linspace(0.6, -0.6, ns(0.7))), 0)
    y = place(y, to_stereo(splat(0.5, 1.0) * 0.7 + liquid(0.5, 30, 300, 900) * 0.4), 0.15)
    y = place(y, to_stereo(steam(0.4, 3500, 0.01, 0.1) * 0.3), 0.2)
    return y


@S('cultista_pacto_rubro', 'Pacto Rubro: sussurros em coro + drone grave', espaco='ossario', mix=0.35)
def _(v):
    d = 2.6
    y = whispers(d, 8, 4)
    dr = lp(saw(hz('D2'), d) + saw(hz('D2') * 1.006, d), 400) * env_pts(d, [(0, 0), (0.6, 1), (d, 0)]) * 0.35
    y = add(y, to_stereo(dr))
    return add(y, to_stereo(reverse(bell(hz('D4'), 1.6, 0.8, 0.8)) * 0.3))


@S('cultista_servo_carne', 'Servo de Carne: carne e ossos estalando ao levantar', espaco='cripta', mix=0.25)
def _(v):
    d = 2.6
    y = np.zeros(ns(d))
    for i in range(6):
        y = place(y, crunch(0.25, 600, 500, 4000, 1.2) * ru(0.5, 1), ru(0, 1.4))
        y = place(y, flesh(0.4, 1.5, 1.1) * ru(0.4, 0.8), ru(0, 1.4))
    g = creature(1.2, 75, [(0, 0.7), (0.6, 1.1), (1, 0.9)], 'o', 'a', 'baixo', 0.65, 0.8, 0.6, 3)
    return place(y, g * 0.6, 1.2)


@S('cultista_chuva_cinzas', 'Chuva de Cinzas: vento seco e cinza caindo', mix=0.2)
def _(v):
    d = 3.5
    env = env_pts(d, [(0, 0), (0.5, 1), (2.6, 1), (d, 0)])
    wind = bp(pink(d), 600 + 500 * lp(white(d), 1) * 30, 0.8) * env * 1.0
    ash = bbp(crackle(d, 500, 0.0015), 2000, 10000) * env * 0.4
    y = widen(wind + ash, 0.7)
    return add(y, to_stereo(whoomp(0.8, 60) * 0.4))


@S('cultista_profecia_sombria', 'Profecia Sombria: voz sussurrando o nome do alvo', espaco='ossario', mix=0.4)
def _(v):
    d = 2.2
    y = np.zeros((ns(d), 2))
    y = place(y, reverse(to_stereo(hp(white(0.8), 800) * env_exp(0.8, 0.3))) * 0.3, 0)
    # "sussurro de nome": silabas sopradas com vogais mudando
    t = 0.75
    for vw, vw2, dd in [('a', 'e', 0.18), ('i', 'a', 0.22), ('o', 'u', 0.35)]:
        s = add(bp(white(0.06), 6000, 2) * env_exp(0.06, 0.02) * 0.6,
                formant(white(dd) * 4, vw, 'tenor', 1.0, vw2, np.linspace(0, 1, ns(dd))) * env_pts(dd, [(0, 0), (0.03, 1), (dd, 0)]))
        y = place(y, widen(s, 0.4), t)
        t += dd + 0.04
    return add(y, whispers(d, 3, 3) * 0.3)


@S('cultista_setimo_selo', 'Setimo Selo (ultimate): coro grave crescendo ate o estouro', espaco='catedral', mix=0.3, lufs=-12)
def _(v):
    d = 6.5
    y = np.zeros((ns(d), 2))
    c = choir(['D2', 'A2', 'D3', 'Eb3', 'A3'], 3.6, 'u', 'baixo', 6, 3.2, 0.1, vowel2='a', vib=0.012)
    c = c * env_pts(3.6, [(0, 0), (3.5, 1), (3.6, 0)], 1.6)[:, None]
    y = place(y, c * 1.3, 0)
    y = place(y, to_stereo(rumble(3.5, 40, 0.8) * env_pts(3.5, [(0, 0), (3.5, 1)], 2)), 0)
    y = place(y, to_stereo(sat(thump(30, 2.5, 4, 0.9, 1.0), 3) * 1.3), 3.5)
    y = place(y, to_stereo(add(glass(1500, 1.5), glass(2300, 1.3) * 0.6, debris(2.0, 300, 1500, 9000, 0.4))), 3.5)
    y = place(y, to_stereo(bell(hz('D3'), 3, 2.5, 0.9) * 0.7), 3.5)
    return y


# ======================================================== MUTANTE
@S('mutante_golpe_purulento', 'Golpe Purulento: impacto umido pesado', var=3)
def _(v):
    d = 1.0
    y = add(flesh(0.8, 2.0, 1.4) * 1.1, sat(thump(45, d, 2.2, 0.25, 0.2), 2) * 1.0, splat(0.7, 1.4) * 0.7)
    return add(y, crunch(0.3, 300, 500, 3000) * 0.4)


@S('mutante_carapaca', 'Carapaca: estalo de couro secando e endurecendo', mix=0.12)
def _(v):
    d = 1.4
    y = np.zeros(ns(d))
    y = place(y, creak(1.0, 20, 45, (260, 600, 1300), 1.0) * 0.7, 0)
    for i in range(10):
        y = place(y, crunch(0.08, 300, 1200, 5000, 0.4) * ru(0.3, 0.7), ru(0.05, 1.0))
    return place(y, thump(80, 0.4, 0.5, 0.08, 0.3) * 0.6, 1.0)


@S('mutante_rugido_praga', 'Rugido da Praga: rugido animal com chiado de filtro (respirador)', espaco='abatedouro', mix=0.2, lufs=-13)
def _(v):
    d = 2.0
    r = creature(d, 70, [(0, 0.8), (0.2, 1.25), (0.7, 1.1), (1, 0.75)], 'a', 'o', 'baixo', 0.6, 1.0, 0.8, 4)
    hiss = bp(white(d), 3200, 2.0) * env_pts(d, [(0, 0), (0.1, 1), (1.7, 0.7), (d, 0)]) * 0.25
    filt = lp(r, 2200) + bp(r, 1200, 3) * 0.6  # som atras da mascara
    return add(filt, hiss, rumble(d, 50, 0.3) * env_exp(d, 0.8))


@S('mutante_regeneracao_profana', 'Regeneracao Profana (passiva, opcional): carne se fechando', mix=0.1, lufs=-20)
def _(v):
    d = 1.6
    y = np.zeros(ns(d))
    for i in range(5):
        y = place(y, flesh(0.35, 1.5, 0.8) * ru(0.3, 0.6), ru(0, 1.1))
    return add(y, lp(liquid(d, 20, 150, 400), 1500) * 0.4)


@S('mutante_investida_bestial', 'Investida Bestial: passos pesados acelerando + impacto', mix=0.15, lufs=-13)
def _(v):
    d = 1.8
    y = np.zeros(ns(d))
    t = 0.0
    for i, gap in enumerate([0.24, 0.2, 0.17, 0.15, 0.13]):
        y = place(y, add(sat(thump(48, 0.4, 1.2, 0.09, 0.4), 2) * 0.7, debris(0.3, 40, 300, 2500, 0.06) * 0.4), t)
        t += gap
    y = place(y, add(sat(thump(38, 1.0, 2.8, 0.3, 0.6), 2.5) * 1.2, flesh(0.6, 1.0, 1.5)), t)
    y = place(y, debris(0.9, 60, 300, 4000, 0.3) * 0.6, t)
    return add(y, whoosh(t, 150, 900, 0.8, 0.95, 0, -0.3, 0.3) * 0.6)


@S('mutante_forma_besta', 'Forma da Besta (ultimate): ossos quebrando + rugido grave', espaco='abatedouro', mix=0.25, lufs=-12)
def _(v):
    d = 4.5
    y = np.zeros((ns(d), 2))
    for i in range(14):
        at = ru(0, 1.6) ** 1.1
        y = place(y, pan(crunch(0.3, 700, 400, 5000, 1.3), ru(-0.6, 0.6)) * ru(0.5, 1), at)
        if i % 3 == 0:
            y = place(y, pan(flesh(0.5, 1.6, 1.4), ru(-0.5, 0.5)) * 0.6, at)
    r = creature(2.6, 55, [(0, 0.7), (0.15, 1.2), (0.6, 1.05), (1, 0.6)], 'a', 'o', 'baixo', 0.55, 1.0, 1.0, 5)
    y = place(y, widen(r, 0.3) * 1.2, 1.5)
    y = place(y, to_stereo(sat(thump(30, 2.5, 2, 0.8, 0.3), 2.5)), 1.5)
    return y


# ======================================================== DEMONIO
@S('demonio_garra_abismo', 'Garra do Abismo: tres cortes rapidos com chiado', var=2)
def _(v):
    d = 1.0
    y = np.zeros((ns(d), 2))
    for i in range(3):
        at = i * 0.13
        y = place(y, whoosh(0.18, 600, 4200, 2.2, 0.5, 0.3, [-0.6, 0.6, -0.2][i], [0.4, -0.4, 0.5][i]) * 0.8, at)
        y = place(y, to_stereo(flesh(0.25, 1.0, 0.7) * 0.6), at + 0.09)
        y = place(y, to_stereo(steam(0.3, 4000, 0.005, 0.08) * 0.35), at + 0.09)
    return y


@S('demonio_corrente_danacao', 'Corrente de Danacao: corrente arrastando + puxao', espaco='cripta', mix=0.2)
def _(v):
    d = 1.8
    y = np.zeros((ns(d), 2))
    y = place(y, whoosh(0.4, 300, 2500, 1.2, 0.6, 0, -0.6, 0.6), 0)
    y = place(y, to_stereo(chain(0.5, 60, 0, 1.2)), 0.05)
    y = place(y, to_stereo(add(clang(600, 0.5, 1.0, 0.1, 0.8) * 0.6, flesh(0.4, 0.6, 1.0) * 0.5)), 0.4)
    y = place(y, pan(chain(1.0, 50, 1.0, 1.3), np.linspace(0.5, -0.5, ns(1.0))), 0.55)
    return y


@S('demonio_pele_enxofre', 'Pele de Enxofre: chiado de chapa quente', mix=0.12)
def _(v):
    d = 2.0
    y = steam(d, 4500, 0.02, None) * 0.7
    y = add(y, bbp(crackle(d, 250, 0.0007), 2500, 12000) * env_pts(d, [(0, 0), (0.1, 1), (d, 0)]) * 0.6)
    return add(y, whoomp(0.8, 60) * 0.6)


@S('demonio_passo_sombrio', 'Passo Sombrio: sopro grave (teleporte por sombra)', espaco='cripta', mix=0.3)
def _(v):
    d = 1.4
    y = np.zeros((ns(d), 2))
    suck = reverse(lp(brown(0.5), 600) * env_exp(0.5, 0.15)) * 1.2
    y = place(y, to_stereo(suck), 0)
    y = place(y, to_stereo(breath(0.6, 'o', 'baixo', False, 1.0) * 0.6), 0.45)
    t = tt(0.8)
    y = place(y, to_stereo(sine(60 * np.exp(-t / 0.3) + 35, 0.8) * env_exp(0.8, 0.25) * 0.8), 0.48)
    return place(y, whoosh(0.5, 150, 900, 0.8, 0.3, 0, 0.6, -0.6) * 0.7, 0.45)


@S('demonio_banquete', 'Banquete (passiva, opcional): mordidas e rosnado de prazer', mix=0.1, lufs=-19)
def _(v):
    d = 1.3
    y = np.zeros(ns(d))
    for i in range(3):
        y = place(y, add(flesh(0.3, 1.5, 0.9), crunch(0.15, 400, 600, 3000) * 0.4), i * 0.22)
    return place(y, creature(0.6, 90, [(0, 1), (1, 0.85)], 'o', 'u', 'baixo', 0.7, 0.6, 0.4, 2) * 0.4, 0.65)


@S('demonio_portao_inferno', 'Portao do Inferno (ultimate): rugido de fornalha, terra se abrindo', espaco='catedral', mix=0.25, lufs=-12)
def _(v):
    d = 5.5
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(rumble(5, 40, 1.2) * env_pts(5, [(0, 0), (1.0, 1), (5, 0)])), 0)
    y = place(y, to_stereo(add(crunch(1.0, 200, 200, 2500, 4), debris(2.5, 60, 200, 3000, 0.9))), 0.6)
    y = place(y, to_stereo(whoomp(2.0, 40) * 1.4), 1.2)
    y = place(y, widen(fire(3.8, 1.0, 50) * env_pts(3.8, [(0, 0), (0.3, 1), (3.8, 0)]) * 0.9, 0.7), 1.3)
    y = place(y, widen(creature(2.5, 45, [(0, 0.8), (0.3, 1.2), (1, 0.7)], 'o', 'a', 'baixo', 0.5, 1.0, 1.0, 5)) * 0.7, 1.4)
    y = place(y, organ(['D2', 'Ab2', 'D3'], 3.5, 'grave', 0.01, 0.4, 2.5) * 0.8, 1.3)
    return y


# ======================================================== HUMANO
@S('humano_tiro_certeiro', 'Tiro Certeiro: estampido seco de rifle', lufs=-12, mix=0.25, var=2)
def _(v):
    d = 2.0
    y = gunshot(d, 1.1, 1.5, 75)
    return add(y, whoosh(0.3, 2000, 6000, 3, 0.1, 0.0, 0, 0.8).mean(1) * 0.2)


@S('humano_rajada', 'Rajada: tiro de escopeta duplo', lufs=-11, mix=0.25)
def _(v):
    d = 2.2
    y = np.zeros(ns(d))
    y = place(y, gunshot(1.6, 1.4, 1.2, 55), 0)
    y = place(y, gunshot(1.6, 1.4, 1.2, 52) * 0.95, 0.11)
    return place(y, debris(1.0, 200, 2000, 9000, 0.1) * 0.4, 0.05)


@S('humano_armadilha_prata', 'Armadilha de Prata: clangor metalico da armadilha armando/fechando')
def _(v):
    d = 1.6
    y = np.zeros(ns(d))
    y = place(y, gears(0.35, 25, 2600) * 0.6, 0)
    y = place(y, add(clang(1300, 1.2, 1.6, 0.4, 1.2), clang(1900, 0.9, 1.6, 0.3, 0.6) * 0.5,
                     thump(110, 0.4, 0.6, 0.05, 0.6) * 0.6), 0.38)
    return place(y, chain(0.5, 40) * 0.4, 0.4)


@S('humano_agua_benta_polvora', 'Agua Benta e Polvora: clique de recarga com cartuchos bentos', espaco='quarto', mix=0.12)
def _(v):
    d = 1.5
    y = np.zeros(ns(d))
    y = place(y, reload_click(0.3), 0)
    y = place(y, add(glass(3000, 0.5) * 0.3, liquid(0.3, 25, 600, 1400) * 0.3), 0.3)
    y = place(y, steam(0.6, 5000, 0.01, 0.2) * 0.25, 0.35)
    y = place(y, reload_click(0.35) * 1.2, 0.75)
    return place(y, bell(hz('A5'), 0.6, 0.3, 1.3) * 0.12, 0.9)


@S('humano_rolamento', 'Rolamento: tecido e cascalho', mix=0.1, var=2)
def _(v):
    d = 0.8
    y = add(cloth(d, 1.4, 2500), debris(d, 80, 300, 4000, 0.4) * 0.8)
    y = add(y, thump(70, 0.3, 0.5, 0.05, 0.3) * 0.5)
    return add(y, whoosh(d, 200, 1200, 0.8, 0.3, 0, -0.5, 0.5).mean(1) * 0.5)


@S('humano_ultimo_suspiro', 'Ultimo Suspiro (ultimate): batida de coracao e tempo parando', espaco='catedral', mix=0.3, lufs=-13)
def _(v):
    d = 5.0
    y = np.zeros((ns(d), 2))
    y = place(y, to_stereo(lp(heartbeat(4.0, 50, 1.4), 350) * 1.2), 0)
    y = place(y, to_stereo(breath(1.2, 'a', 'baixo', True, 0.8)), 0.2)
    t = tt(4.5)
    tone = sine(hz('D3'), 4.5) * env_pts(4.5, [(0, 0), (1.5, 1), (4.5, 0)]) * 0.15
    y = place(y, widen(tone), 0)
    y = place(y, to_stereo(reverse(bell(hz('D4'), 2.0, 1.2, 1.0)) * 0.4), 0)
    return place(y, to_stereo(bell(hz('D4'), 3, 2, 1.0) * 0.5), 2.0)


# ======================================================== TECNOMANCER
@S('tecnomancer_arco_voltaico', 'Arco Voltaico: estalo eletrico', var=3)
def _(v):
    d = 0.9
    y = zap(0.6, 1.2, ru(90, 130)) * env_pts(0.6, [(0, 1), (0.6, 0)])
    y = place(np.zeros(ns(d)), y, 0)
    y = place(y, hp(white(0.05), 1000) * env_exp(0.05, 0.004) * 2, 0)
    return place(y, thump(90, 0.4, 0.5, 0.06, 0.3) * 0.5, 0.0)


@S('tecnomancer_nanoreparo', 'Nanoreparo: zumbido de enxame mecanico')
def _(v):
    d = 2.4
    y = np.zeros((ns(d), 2))
    for i in range(14):
        f = ru(180, 320)
        b = saw(f * (1 + 0.03 * np.sin(2 * np.pi * ru(4, 9) * tt(d))), d) * 0.2
        b = bp(b, ru(1500, 3500), 2)
        y = add(y, pan(b, ru(-0.9, 0.9)))
    y = y * env_pts(d, [(0, 0), (0.3, 1), (1.9, 1), (d, 0)])[:, None]
    y = add(y, to_stereo(gears(d, 30, 4000) * 0.15))
    return y


@S('tecnomancer_torreta_sentinela', 'Torreta Sentinela: catraca, engrenagens e trava', espaco='abatedouro', mix=0.15)
def _(v):
    d = 2.2
    y = np.zeros(ns(d))
    y = place(y, add(clang(400, 0.6, 1.0, 0.1, 0.8), thump(80, 0.4, 0.8, 0.08, 0.4)), 0)
    y = place(y, gears(0.9, 22, 2000), 0.25)
    y = place(y, steam(0.5, 4000, 0.01, 0.15) * 0.5, 1.1)
    y = place(y, reload_click(0.35), 1.3)
    return place(y, hum(0.7, 120, 6) * env_exp(0.7, 0.3) * 0.3, 1.5)


@S('tecnomancer_campo_forca', 'Campo de Forca: zumbido grave de transformador ligando', espaco='abatedouro', mix=0.15)
def _(v):
    d = 2.0
    t = tt(d)
    f = 50 * (0.5 + 0.5 * np.clip(t / 0.5, 0, 1))
    h = 0
    for k in range(1, 9):
        h = h + np.sin(2 * np.pi * np.cumsum(f * k) / SR) / k
    h = h * env_pts(d, [(0, 0), (0.4, 1), (1.5, 0.7), (d, 0)]) * 0.5
    sh = bp(white(d), 5000, 2) * env_pts(d, [(0, 0), (0.4, 1), (d, 0)]) * 0.2
    return add(h, sh, zap(0.3, 0.6) * env_exp(0.3, 0.08))


@som('skills/tecnomancer_campo_forca_loop', lufs=-22, loop=True, desc='loop enquanto o Campo de Forca dura')
def _(v):
    d = 4.0
    y = hum(d + 2, 50, 8, 0.001)
    y = add(y, bp(white(d + 2), 5000, 3) * 0.06)
    return loopify(widen(y, 0.3), 1.0)


@S('tecnomancer_pulso_antidivino', 'Pulso Anti-Divino: pulso eletronico grave em anel', espaco='catedral', mix=0.25, lufs=-13)
def _(v):
    d = 2.5
    t = tt(d)
    f = 40 + 260 * np.exp(-t / 0.08)
    y = sat(np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(d, 0.5), 2.5) * 1.0
    y = add(y, sine(hz('A4') * (1 - 0.3 * t / d), d) * env_exp(d, 0.3) * 0.2)
    y = add(y, zap(0.5, 0.6) * env_exp(0.5, 0.1), bp(white(d), 1200, 1) * env_exp(d, 0.2) * 0.4)
    return y


@S('tecnomancer_maquina_juizo_reverso', 'Maquina do Juizo Reverso (ultimate): sirene reversa e descarga', espaco='catedral', mix=0.25, lufs=-12)
def _(v):
    d = 6.0
    y = np.zeros((ns(d), 2))
    t = tt(3.5)
    sir_f = 300 + 600 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t))
    sir = sat(saw(sir_f, 3.5) * 0.5 + square(sir_f * 0.5, 3.5) * 0.3, 2) * env_pts(3.5, [(0, 0), (3.3, 1), (3.5, 0)], 1.5)
    sir = reverse(sir)  # sirene tocando de tras pra frente
    y = place(y, widen(lp(sir, 3500), 0.3) * 0.7, 0)
    y = place(y, to_stereo(gears(3.5, 12, 1500) * np.linspace(0.2, 1, ns(3.5)) * 0.5), 0)
    y = place(y, to_stereo(hum(3.5, 50, 10) * np.linspace(0, 1, ns(3.5)) * 0.6), 0)
    y = place(y, to_stereo(sat(thump(32, 2.4, 4, 0.8, 1.0), 3) * 1.2), 3.5)
    y = place(y, widen(zap(2.0, 1.5, 100) * env_exp(2.0, 0.6)), 3.5)
    return place(y, to_stereo(bell(hz('C#3'), 2.4, 2, 0.9) * 0.4), 3.5)
