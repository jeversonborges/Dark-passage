"""Blocos de construcao de efeitos sonoros do DARK PASSAGE."""
import numpy as np
from dsp import *  # noqa
from dsp import _tailfade


def R():
    return rng()


def ru(a, b):
    return R().uniform(a, b)


# ---------------------------------------------------------------- movimento / ar
def whoosh(dur=0.35, lo=300, hi=2500, q=1.2, peak=0.45, blade=0.0, pan_from=-0.5, pan_to=0.5, rough=0.3):
    """Golpe no ar. peak = posicao relativa do pico de energia."""
    n = ns(dur)
    t = np.linspace(0, 1, n)
    shape = np.where(t < peak, (t / peak) ** 2.2, np.exp(-(t - peak) / (1 - peak) * 3.5))
    fc = lo + (hi - lo) * shape
    src = white(dur) * (1 + rough * lp(white(dur), 40) * 6)
    y = bp(src, fc, q) * shape * 2.2
    y += bp(white(dur), fc * 2.2, q * 1.5) * shape ** 2 * 0.6
    if blade:
        tone = sine(fc * 1.9, dur) * shape ** 3 * 0.12 * blade
        ring = metal(dur, ru(2600, 3600), n=10, decay=0.25, bright=1.5) * 0.05 * blade
        y += tone + ring * np.clip((t - peak) * 8, 0, 1)
    return pan(y, np.linspace(pan_from, pan_to, n))


def cloth(dur=0.3, intensity=1.0, bright=4000):
    n = ns(dur)
    flut = np.abs(lp(white(dur), ru(25, 60))) * 8
    env = env_pts(dur, [(0, 0), (dur * 0.2, 1), (dur, 0)])
    y = bp(white(dur), bright * (0.7 + 0.6 * np.linspace(0, 1, n)), 0.8) * flut * env
    y += lp(white(dur), 900) * env * 0.4
    return y * intensity


# ---------------------------------------------------------------- impactos
def thump(f0=60, dur=0.5, drop=2.5, decay=0.15, click=0.3):
    t = tt(dur)
    f = f0 * (1 + drop * np.exp(-t / 0.025))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    y += lp(white(dur), 3000) * np.exp(-t / 0.004) * click
    return y


def flesh(dur=0.35, wet=1.0, size=1.0):
    """Tapa/corte em carne: estalo umido + corpo grave + chiado curto."""
    t = tt(dur)
    slap = bp(white(dur), 1200 / size, 0.7) * np.exp(-t / (0.012 * size))
    body = thump(70 / size, dur, 2.0, 0.08 * size, 0)
    sq_f = 2500 * np.exp(-t / 0.05) + 300
    squelch = bp(white(dur) * (1 + 3 * np.abs(lp(white(dur), 120))), sq_f, 3) * np.exp(-t / 0.07) * wet
    drops = bbp(crackle(dur, 25 * wet, 0.002), 1200, 4500, 2) * np.exp(-t / 0.06) * 0.25 * wet
    return blp(slap * 1.4 + squelch * 0.9 + drops, 7000, 2) + body * 0.9


def crunch(dur=0.25, density=600, lo=900, hi=5500, size=1.0):
    """Osso quebrando: rajada de estalos secos com ressonancia de madeira."""
    t = tt(dur)
    c = crackle(dur, density, 0.0008)
    env = np.exp(-t / (0.05 * size)) * np.clip(t / 0.002, 0, 1)
    y = bbp(c, lo, hi, 2) * env
    res = resonate(c * env, [ru(500, 800), ru(1100, 1600), ru(2000, 2800)], [12, 14, 16], [0.6, 0.4, 0.3])
    return y + res * 0.8


def clang(f0=900, dur=1.2, bright=1.4, decay=0.6, hit=0.6):
    t = tt(dur)
    y = metal(dur, f0, n=28, decay=decay, bright=bright)
    y += bp(white(dur), f0 * 4, 1.0) * np.exp(-t / 0.003) * hit * 3
    return y


def sparks(dur=0.5, density=120):
    """Faiscas: estalinhos agudos esparsos que somem rapido."""
    y = np.zeros(ns(dur))
    k = max(3, int(density * dur * 0.2))
    for i in range(k):
        at = (ru(0, 1) ** 1.8) * dur * 0.7
        d = 0.04
        tink = hp(white(d), 5000) * env_exp(d, 0.0012) + metal(d, ru(5500, 9500), 4, decay=0.006, bright=2) * 0.4
        y = place(y, tink * ru(0.1, 0.5) * np.exp(-at / (dur * 0.3)), at)
    return y[:ns(dur)]


def debris(dur=0.8, density=40, lo=200, hi=3000, decay=0.5):
    """Cascalho/pedrinhas caindo."""
    t = tt(dur)
    y = bbp(crackle(dur, density, 0.003), lo, hi, 2) * np.exp(-t / decay)
    return y


# ---------------------------------------------------------------- metal / correntes
def clink(f0=None, dur=0.12):
    f0 = f0 or ru(1800, 4200)
    return metal(dur, f0, n=8, decay=ru(0.02, 0.06), bright=1.6) + \
        bp(white(dur), f0 * 1.5, 2) * env_exp(dur, 0.002) * 0.5


def chain(dur=1.0, density=40, drag=0.0, heavy=1.0):
    """Corrente: elos batendo (+ arrasto no chao se drag>0)."""
    y = np.zeros(ns(dur))
    k = int(density * dur)
    for i in range(k):
        at = ru(0, dur - 0.1)
        c = clink(ru(1400, 3800) / heavy, 0.12) * ru(0.2, 0.8)
        y = place(y, c, at)
    y = y[:ns(dur)]
    if drag:
        scrape = bp(white(dur) * (1 + 4 * np.abs(lp(white(dur), 30))), 1800, 0.8) * drag * 0.5
        y += scrape + lp(white(dur), 400) * drag * 0.4
    if heavy > 1:
        y = lp(y, 9000 / heavy) + thump(90, dur, 0.5, dur / 3, 0) * 0.1 * heavy
    return y


def gears(dur=1.0, rate=18, f=2500):
    """Catraca/engrenagens: cliques regulares com ressonancia."""
    y = np.zeros(ns(dur))
    t = 0.0
    while t < dur - 0.05:
        c = metal(0.05, f * ru(0.9, 1.1), n=6, decay=0.01, bright=2) + bp(white(0.05), 4000, 2) * env_exp(0.05, 0.002)
        y = place(y, c * ru(0.5, 1), t)
        t += 1 / rate * ru(0.85, 1.15)
    return y[:ns(dur)]


# ---------------------------------------------------------------- madeira / vidro / moedas
def creak(dur=1.0, f_from=40, f_to=90, res=(320, 750, 1600), bright=1.0):
    """Rangido (madeira/dobradica): stick-slip em ressonadores."""
    n = ns(dur)
    f = np.linspace(f_from, f_to, n) * (1 + 0.25 * lp(white(dur), 8) * 8)
    pulses = np.maximum(saw(f, dur), 0.7) - 0.7
    pulses *= 1 + 0.6 * np.abs(lp(white(dur), 20)) * 6
    y = resonate(pulses, list(res), [8, 10, 12], [1.0, 0.7 * bright, 0.4 * bright])
    return y * env_pts(dur, [(0, 0), (0.05, 1), (dur - 0.08, 1), (dur, 0)])


def wood_knock(f0=180, dur=0.3):
    t = tt(dur)
    y = modal(dur, [f0, f0 * 2.4, f0 * 3.9, f0 * 5.4], [0.06, 0.03, 0.02, 0.012], [1, 0.6, 0.4, 0.2])
    y += bp(white(dur), 2500, 1) * np.exp(-t / 0.004) * 0.6
    return y


def glass(f0=2400, dur=0.6):
    ratios = [1, 2.32, 4.25, 6.63, 9.38]
    return modal(dur, [f0 * r * ru(0.99, 1.01) for r in ratios],
                 [0.4, 0.25, 0.15, 0.1, 0.06], [1, 0.6, 0.4, 0.2, 0.1]) + \
        bp(white(dur), 6000, 1) * env_exp(dur, 0.002) * 0.4


def coin(f0=None, dur=0.5):
    f0 = f0 or ru(3200, 4800)
    ratios = [1, 2.76, 5.40, 8.93]
    y = modal(dur, [f0 * r for r in ratios], [0.35, 0.18, 0.1, 0.05], [1, 0.5, 0.3, 0.15])
    return y + hp(white(dur), 5000) * env_exp(dur, 0.0015) * 0.5


def coins(dur=0.8, k=8):
    y = np.zeros(ns(dur))
    for i in range(k):
        at = ru(0, 0.35) ** 1.4
        y = place(y, coin(None, 0.45) * ru(0.3, 1), at)
    return y[:ns(dur)]


def liquid(dur=0.6, rate=14, f_lo=400, f_hi=1400):
    """Bolhas/glub: senoides curtas com glissando ascendente."""
    y = np.zeros(ns(dur))
    t = 0.0
    while t < dur - 0.06:
        d = ru(0.02, 0.06)
        f0 = ru(f_lo, f_hi)
        tb = tt(d)
        b = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2.5 * tb / d)) / SR) * np.exp(-tb / (d * 0.4))
        y = place(y, b * ru(0.3, 1), t)
        t += ru(0.3, 1.7) / rate
    return y[:ns(dur)]


# ---------------------------------------------------------------- fogo / vapor / eletricidade
def fire(dur=2.0, intensity=1.0, crackles=25):
    t = tt(dur)
    roar = lp(brown(dur), 350) * (1 + 0.5 * lp(white(dur), 3) * 10) * 1.2
    hiss = bp(white(dur), 2500, 0.6) * (0.3 + 0.7 * np.abs(lp(white(dur), 6) * 8)) * 0.25
    pops = bbp(crackle(dur, crackles, 0.0015), 700, 5000, 2) * 0.6
    return (roar + hiss + pops) * intensity


def whoomp(dur=1.0, f0=70):
    """Ignicao: sucção grave + rajada de fogo."""
    t = tt(dur)
    env = env_pts(dur, [(0, 0), (0.06, 1), (dur, 0)], 2)
    y = lp(brown(dur), 200 + 1800 * env) * env * 2.5
    y += thump(f0, dur, 1.0, 0.25, 0) * 0.6
    y += fire(dur, 0.6, 50) * env
    return y


def steam(dur=1.0, f=3500, attack=0.02, decay=None, whistle=0.0):
    n = ns(dur)
    env = env_pts(dur, [(0, 0), (attack, 1), (dur * 0.6, 0.8), (dur, 0)]) if decay is None else env_exp(dur, decay, attack)
    y = bp(white(dur), f, 0.6) * env * 1.5 + hp(white(dur), 6000) * env * 0.6
    y += lp(white(dur), 600) * env * 0.4
    if whistle:
        y += sine(f * 0.5 * (1 + 0.01 * lp(white(dur), 10) * 10), dur) * env * whistle * 0.15
    return y


def zap(dur=0.5, intensity=1.0, buzz=100):
    """Arco eletrico: rajadas irregulares + zumbido harmonico."""
    t = tt(dur)
    gate = (lp(white(dur), ru(60, 140)) * 10 > ru(-0.2, 0.3)).astype(float)
    gate = lp(gate, 2000)
    crack = bbp(white(dur), 1200, 6500, 2) * gate * 1.1
    b = saw(buzz * (1 + 0.05 * lp(white(dur), 20) * 10), dur)
    b = bp(b, 1800, 0.8) * gate * 0.6
    snaps = bbp(crackle(dur, 60, 0.0004), 2000, 9000, 2) * 1.2
    return (crack + b + snaps) * intensity


def hum(dur=2.0, f0=50, harm=10, drift=0.002):
    t = tt(dur)
    y = np.zeros(len(t))
    for k in range(1, harm + 1):
        a = (1 / k) * (1.4 if k % 2 == 0 else 1.0)
        f = f0 * k * (1 + drift * np.sin(2 * np.pi * ru(0.05, 0.2) * t))
        y += a * np.sin(2 * np.pi * np.cumsum(f) / SR + ru(0, 6))
    return y * 0.4


# ---------------------------------------------------------------- vozes / criaturas
def creature(dur=1.0, f0=90, contour=None, vowel='a', vowel2='o', voz='baixo', shift=0.7,
             growl=0.6, sub=0.5, drive=3.0, breath=0.3, vib=0.0):
    """Vocalizacao monstruosa. contour = pontos (t_rel, multiplicador de f0)."""
    n = ns(dur)
    if contour is None:
        contour = [(0, 0.85), (0.25, 1.15), (1, 0.7)]
    tr = np.linspace(0, 1, n)
    f = f0 * np.interp(tr, [c[0] for c in contour], [c[1] for c in contour])
    if vib:
        f = vibrato(f, dur, 6, vib, 0.05)
    src = glottal(f, dur, jitter=0.02 + growl * 0.04, shimmer=0.15 + growl * 0.3, breath=0.1)
    if sub:
        src += glottal(f * 0.5, dur, 0.03, 0.3, 0) * sub * 0.8
    rough = 1 + growl * lp(white(dur), ru(25, 45)) * 12
    src *= rough
    y = formant(src, vowel, voz, shift, vowel2, np.linspace(0, 1, n))
    y = blp(sat(y * 2, drive), 4500, 2)
    y += blp(formant(white(dur) * 3, vowel, voz, shift), 6000, 2) * breath
    env = env_pts(dur, [(0, 0), (min(0.08, dur * 0.2), 1), (dur * 0.7, 0.8), (dur, 0)])
    return y * env


def scream(dur=1.0, f0=600, vowel='a', voz='soprano', drive=2.0, vib=0.03):
    n = ns(dur)
    f = vibrato(f0 * np.interp(np.linspace(0, 1, n), [0, 0.15, 1], [0.8, 1.1, 0.85]), dur, 7, vib, 0.05)
    src = glottal(f, dur, 0.01, 0.1, 0.2, tilt=2500)
    y = formant(src, vowel, voz, 1.0) * 2
    y = sat(y, drive) + hp(white(dur), 3000) * 0.1
    return y * env_pts(dur, [(0, 0), (0.05, 1), (dur * 0.6, 0.8), (dur, 0)])


def breath(dur=1.0, vowel='a', voz='baixo', inhale=False, intensity=1.0):
    n = ns(dur)
    env = env_pts(dur, [(0, 0), (dur * (0.6 if inhale else 0.2), 1), (dur, 0)])
    y = formant(white(dur) * 4, vowel, voz, 1.0) + hp(white(dur), 4000) * 0.3
    return y * env * intensity


def whispers(dur=3.0, voices=8, density=3.0, espaco=None):
    """Murmurio de sussurros (sem palavras): fonemas de sopro com formantes e sibilantes."""
    y = np.zeros((ns(dur), 2))
    for v in range(voices):
        p = ru(-0.9, 0.9)
        t = ru(0, 0.4)
        while t < dur - 0.3:
            d = ru(0.08, 0.3)
            if R().uniform() < 0.3:
                s = bp(white(d), ru(4500, 7000), 2) * env_pts(d, [(0, 0), (d * 0.3, 1), (d, 0)]) * 0.8
            else:
                vw = R().choice(list('aeiou'))
                vw2 = R().choice(list('aeiou'))
                s = blp(formant(white(d) * 4, vw, 'tenor' if v % 2 else 'alto', ru(0.9, 1.1), vw2,
                                np.linspace(0, 1, ns(d))), 5000, 2) * env_pts(d, [(0, 0), (d * 0.2, 1), (d, 0)])
            y = place(y, pan(s, p) * ru(0.4, 1), t)
            t += d + ru(0.0, 1.0 / density)
    return y[:ns(dur)]


# ---------------------------------------------------------------- instrumentos
def choir(notes, dur, vowel='a', voz='baixo', voices=6, attack=0.4, release=0.8, vib=0.008,
          breath=0.06, vowel2=None, detune=0.006):
    """Coro: varias vozes por nota, mesmo filtro de formantes (linear) -> eficiente."""
    n = ns(dur)
    src = np.zeros(n)
    for note in notes:
        f0 = hz(note) if isinstance(note, (str, int)) else note
        for v in range(voices):
            d = 1 + R().normal(0, detune)
            f = vibrato(f0 * d, dur, ru(4.8, 6.2), vib * ru(0.6, 1.4), ru(0.2, 0.6))
            src += glottal(f, dur, 0.004, 0.06, breath) * ru(0.6, 1.0)
    src /= np.sqrt(len(notes) * voices)
    if vowel2:
        y = formant(src, vowel, voz, 1.0, vowel2, np.linspace(0, 1, n) ** 0.7)
    else:
        y = formant(src, vowel, voz, 1.0)
    env = env_pts(dur, [(0, 0), (attack, 1), (max(attack, dur - release), 0.9), (dur, 0)], 1.3)
    return chorus(y * env * 2.5, 2, 0.003, 0.4, 0.012)


ORGAN_STOPS = {
    # (multiplicador de frequencia, amplitude)
    'pleno': [(0.5, 0.6), (1, 1.0), (2, 0.7), (3, 0.35), (4, 0.4), (6, 0.15), (8, 0.18)],
    'flauta': [(1, 1.0), (2, 0.25), (3, 0.06)],
    'grave': [(0.5, 1.0), (1, 0.8), (2, 0.35), (3, 0.1)],
    'trombeta': [(1, 1.0), (2, 0.8), (3, 0.6), (4, 0.5), (5, 0.4), (6, 0.3), (7, 0.25), (8, 0.2)],
}


def organ(notes, dur, stop='pleno', detune=0.0, attack=0.06, release=0.5, chiff=0.3, trem=0.0):
    """Orgao de tubos (aditivo). detune em fracao (0.01 = desafinado)."""
    n = ns(dur)
    t = tt(dur)
    y = np.zeros(n)
    for note in notes:
        f0 = hz(note) if isinstance(note, (str, int)) else note
        for mul, a in ORGAN_STOPS[stop]:
            for k in (1, 2, 3):  # cada fileira com parciais proprios
                f = f0 * mul * k * (1 + R().normal(0, detune))
                if f > 12000:
                    continue
                y += a * (1 / k ** 1.6) * np.sin(2 * np.pi * f * t + ru(0, 6))
        if chiff:
            y += bp(white(dur), f0 * 6, 2) * env_exp(dur, 0.04) * chiff
    y /= np.sqrt(len(notes))
    if trem:
        y *= 1 + trem * np.sin(2 * np.pi * 5.8 * t)
    env = env_pts(dur, [(0, 0), (attack, 1), (max(attack, dur - release), 1), (dur, 0)])
    return y * env * 0.25


def strings(notes, dur, attack=0.6, release=1.0, bright=1800, detune=0.008, vib=0.004):
    n = ns(dur)
    y = np.zeros(n)
    for note in notes:
        f0 = hz(note) if isinstance(note, (str, int)) else note
        f = vibrato(f0, dur, 5.2, vib, 0.3)
        y += supersaw(f, dur, 5, detune)
    y /= np.sqrt(len(notes))
    env = env_pts(dur, [(0, 0), (attack, 1), (max(attack, dur - release), 0.85), (dur, 0)], 1.5)
    y = lp(y, bright * (0.5 + 0.5 * env), 0.9)
    y += bp(white(dur), 3000, 0.5) * env * 0.04  # arco
    return y * env * 0.35


def brass(f0, dur, attack=0.08, release=0.3, bright=1.0, growl=0.0, drive=1.5):
    n = ns(dur)
    f = vibrato(f0, dur, 5, 0.006, 0.4)
    if growl:
        f = f * (1 + growl * 0.02 * lp(white(dur), 70) * 10)
    src = saw(f, dur) * 0.7 + saw(f * 1.003, dur) * 0.5
    env = env_pts(dur, [(0, 0), (attack, 1), (max(attack, dur - release), 0.85), (dur, 0)], 1.2)
    cut = f0 * (1.5 + 6 * env * bright)
    y = lp(src, cut, 1.2)
    y = sat(y * drive, drive)
    return y * env * 0.5


def drum(f0=55, dur=1.2, decay=0.5, membrane=True, hit=0.6, drop=0.6):
    """Tambor grande (taiko/timpano)."""
    t = tt(dur)
    f = f0 * (1 + drop * np.exp(-t / 0.04))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    if membrane:
        for r, a, d in [(1.59, 0.35, 0.4), (2.14, 0.25, 0.3), (2.30, 0.18, 0.25), (2.65, 0.12, 0.2), (3.6, 0.06, 0.1)]:
            y += a * np.sin(2 * np.pi * np.cumsum(f * r) / SR) * np.exp(-t / (decay * d))
    y += lp(white(dur), 2500) * np.exp(-t / 0.012) * hit
    return y


def anvil(f0=1100, dur=1.5):
    return clang(f0, dur, 1.2, 0.9, 0.8) + thump(140, dur, 0.4, 0.05, 0.2) * 0.4


def heartbeat(dur=1.0, bpm=60, strength=1.0):
    y = np.zeros(ns(dur))
    beat = 60 / bpm
    t = 0.0
    while t < dur:
        y = place(y, lp(thump(48, 0.3, 0.6, 0.07, 0.05), 300), t, 1.0 * strength)
        y = place(y, lp(thump(42, 0.3, 0.5, 0.06, 0.05), 250), t + 0.16, 0.7 * strength)
        t += beat
    return y[:ns(dur)]


def gunshot(dur=1.6, size=1.0, crack=1.0, low=70):
    """Arma de polvora: estalo + explosao grave + cauda."""
    t = tt(dur)
    c = hp(white(dur), 2000) * np.exp(-t / 0.0025) * crack * 2.5
    blast = lp(white(dur), 2500 * size) * np.exp(-t / (0.03 * size)) * 2
    boom = thump(low, dur, 1.5, 0.12 * size, 0) * 1.5
    tail = lp(brown(dur), 900) * np.exp(-t / (0.35 * size)) * 0.8
    y = sat(c + blast + boom, 1.6) + tail
    return y


def reload_click(dur=0.3):
    y = metal(0.06, 2200, n=10, decay=0.015, bright=2) + bp(white(0.06), 3000, 1.5) * env_exp(0.06, 0.003)
    out = np.zeros(ns(dur))
    out = place(out, y, 0.0)
    out = place(out, metal(0.08, 1500, n=10, decay=0.02, bright=1.5) * 1.2 + bp(white(0.08), 1800, 1.2) * env_exp(0.08, 0.004), 0.12)
    return out[:ns(dur)]


def bones_rattle(dur=1.0, density=30):
    y = np.zeros(ns(dur))
    for i in range(int(density * dur)):
        y = place(y, wood_knock(ru(600, 1600), 0.08) * ru(0.2, 0.7), ru(0, dur - 0.1))
    return y[:ns(dur)]


def drip(f0=None, dur=0.25):
    f0 = f0 or ru(900, 2200)
    t = tt(dur)
    f = f0 * (1 + 1.2 * np.clip(t / 0.03, 0, 1))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.025) * np.clip(t / 0.001, 0, 1)


def wings(dur=1.0, flaps=2, heavy=1.0, feathers=1.0):
    """Batidas de asa: rajada grave de ar + farfalhar de penas."""
    y = np.zeros(ns(dur))
    gap = dur / (flaps + 0.5)
    for i in range(flaps):
        d = gap * 1.1
        e = env_pts(d, [(0, 0), (d * 0.35, 1), (d, 0)], 1.5)
        air = lp(white(d), 500 * heavy ** -0.5) * e * 2.0 * heavy + thump(55, d, 0.3, d * 0.3, 0) * e * 0.6 * heavy
        fe = cloth(d, feathers, 3500)
        y = place(y, air + fe, i * gap)
    return y[:ns(dur)]


def rumble(dur=3.0, f=60, intensity=1.0):
    t = tt(dur)
    y = lp(brown(dur), f * 2) * (1 + 0.6 * lp(white(dur), 2) * 10) * 2
    return y * intensity


def splat(dur=0.5, size=1.0):
    """Liquido espesso caindo / jorro."""
    t = tt(dur)
    y = bp(white(dur), 800 / size, 0.6) * np.exp(-t / (0.04 * size)) * 1.4
    y += liquid(dur, 30, 300 / size, 900 / size) * np.exp(-t / 0.2) * 0.6
    y += hp(crackle(dur, 80, 0.001), 2000) * np.exp(-t / 0.15) * 0.4
    return y


def finish(x, lufs=-16, espaco=None, mix_=0.2, peak=-1.0, tail=True, hp_=30):
    """Espacializa, masteriza e corta silencio."""
    x = _tailfade(to_stereo(x), 0.012)
    if espaco:
        x = reverb(x, espaco, mix_, tail)
    x = bhp(x, hp_, 2)
    x = master(x, lufs, peak)
    x = trim(x, -60, 0.05)
    return fade(x, 0.0005, min(0.08, len(x) / SR * 0.2))
