"""Musica da area inicial como deserto radioativo (direcao do Jefin, 2026-10-04).

Substitui musica/sao_lazaro: gotico de deserto. Guitarra com tremolo e eco de mola,
drone grave, metal arqueado, tambor de moldura como coracao, radio perdido e um
violino sozinho em Re frigio dominante.
"""
from kit import *  # noqa
from musica import M, Musica, F, i_solo
from ambiente_deserto import sand_wind, radio


def twang(f, d, trem=5.2, depth=0.45):
    """Guitarra de corda metalica, meio estourada, com tremolo."""
    dd = max(d, 0.4) + 2.2
    y = pluck(f, dd, 0.72, 0.9985)
    y = add(y, bp(y, 2400, 1.5) * 0.4, bp(y, 160, 2) * 0.4)
    y = sat(y * 2.2, 1.6) * 0.5
    t = tt(dd)
    y *= 1 - depth * 0.5 * (1 + np.sin(2 * np.pi * trem * t))
    return blp(y, 5000, 2) * 0.55


def bowed_metal(f, d):
    """Serrote/chapa arqueada: ruido de arco excitando modos metalicos."""
    n = ns(d)
    exc = pink(d) * env_pts(d, [(0, 0), (d * 0.4, 1), (d * 0.75, 0.8), (d, 0)])
    fv = 1 + 0.004 * np.sin(2 * np.pi * 4.5 * tt(d))
    y = np.zeros(n)
    for r, g in [(1.0, 1.0), (2.41, 0.45), (4.17, 0.25), (6.6, 0.1)]:
        y += bp(exc, f * r, 120) * g
    y = y * fv
    return blp(y * 6, 4000, 2)


def frame_drum(g=1.0, f=68):
    d = 1.4
    y = drum(f, d, 0.35, True, 0.4, 0.3) + bbp(white(d), 200, 1200) * env_exp(d, 0.03) * 0.3
    return blp(y, 2500, 2) * g


def drone(L, notes=('D1', 'A1', 'D2')):
    d = L + 4
    y = np.zeros(ns(d))
    for i, nt in enumerate(notes):
        f = F(nt) * (1 + 0.002 * slow(d, 0.1))
        y += sine(f, d) * (1.0 / (i + 1)) + saw(f, d) * 0.08
    y = lp(sat(y, 1.4), 260, 0.8) * (0.7 + 0.3 * np.clip(slow(d, 0.05) + 0.5, 0, 1))
    return loopify(np.stack([y, y], 1) * 0.5, 4.0)


@M('sao_lazaro', 'Area inicial (deserto radioativo): guitarra com tremolo e eco, drone grave, metal arqueado, tambor de moldura, radio perdido e violino sozinho', lufs=-19)
def _(v):
    m = Musica(66, 32, 4, tail=10)
    m.bus('drone', 0.8, None, 0)
    m.bus('vento', 0.7, None, 0)
    m.bus('guitarra', 0.9, 'rua', 0.35)
    m.bus('metal', 0.6, 'catedral', 0.55)
    m.bus('tambor', 0.75, 'rua', 0.3)
    m.bus('solo', 0.8, 'catedral', 0.45)
    m.bus('radio', 0.5, 'quarto', 0.3)
    n = ns(m.L)
    m.buses['drone'][:n] += drone(m.L)[:n]  # camadas em loop entram direto (sem fade de cauda)
    m.buses['vento'][:n] += loopify(sand_wind(m.L + 3, 0.6, 420), 3.0)[:n] * 0.4
    # harmonia em Re frigio dominante, 4 compassos por acorde
    roots = ['D', 'Eb', 'D', 'C', 'Bb', 'Eb', 'C', 'D']
    shapes = {'D': ['D3', 'A3', 'D4', 'F#4'], 'Eb': ['Eb3', 'Bb3', 'Eb4', 'G4'], 'C': ['C3', 'G3', 'C4', 'Eb4'],
              'Bb': ['Bb2', 'F3', 'Bb3', 'D4']}
    for b in range(32):
        sh = shapes[roots[b // 4]]
        spb = m.spb
        # dedilhado esparso com eco: grave no 1, resposta no 2.5, e as vezes no 3.5
        notes = [(0, sh[0], 0.8), (1.5, sh[2], 0.45), (2.5, sh[1], 0.55)]
        if b % 2 == 1:
            notes.append((3.5, sh[3], 0.4))
        for bt, nt, g in notes:
            s = twang(F(nt), spb * 2)
            dry = pan(s, -0.25)
            wet = pan(delay(s, spb * 0.75, 0.35, 0.6, 1.0) - s, 0.5) * 0.45  # eco pontuado no outro lado
            m.put('guitarra', add(dry, wet), b, bt, g)
        if b >= 8 and b % 4 == 0:
            m.put('tambor', frame_drum(0.9), b, 0, 1.0, -0.1)
        if b >= 8:
            m.put('tambor', frame_drum(0.4, 74), b, 2.5, 1.0, 0.15)
            m.put('tambor', frame_drum(0.6, 64), b, 3.0, 1.0, 0.15)
    # metal arqueado nos pontos de virada
    for b, nt in [(0, 'A4'), (8, 'Bb4'), (14, 'G4'), (20, 'F#4'), (28, 'D5')]:
        m.put('metal', bowed_metal(F(nt), 7 * m.spb), b, 0, 0.8, ru(-0.5, 0.5))
    # violino sozinho no deserto (secao B)
    mel1 = [('A4', 2), ('Bb4', 1), ('A4', 1), ('G4', 2), ('F#4', 2), ('Eb4', 3), ('D4', 1), ('D4', 4), (None, 4),
            ('F#4', 1), ('G4', 1), ('A4', 2), ('Bb4', 2), ('C5', 2), ('Bb4', 1), ('A4', 1), ('G4', 2), ('F#4', 2), ('Eb4', 4), (None, 4)]
    mel2 = [('D5', 3), ('C5', 1), ('Bb4', 2), ('A4', 2), ('Bb4', 2), ('A4', 1), ('G4', 1), ('F#4', 4), (None, 4),
            ('G4', 1), ('A4', 1), ('Bb4', 2), ('A4', 2), ('G4', 2), ('F#4', 2), ('Eb4', 2), ('F#4', 2), ('D4', 6)]
    m.seq('solo', lambda f, d: i_solo(f, d, 2600, 0.3), mel1, 12, 0, 0.75, 0.25)
    m.seq('solo', lambda f, d: i_solo(f, d, 2600, 0.3), mel2, 22, 0, 0.75, 0.25)
    # radio perdido sintonizando ao longe
    for b in (5, 19):
        d = 5.0
        r = radio(d, 0.6, 0.7) * env_pts(d, [(0, 0), (1, 1), (4, 1), (d, 0)])
        m.put('radio', blp(r, 3000, 2) * 0.5, b, 1, 1.0, 0.7 if b == 5 else -0.7)
    return m.render(-19)
