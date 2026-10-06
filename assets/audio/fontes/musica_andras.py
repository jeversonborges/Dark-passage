"""Musica do chefe Andras, o General Partido: marcha de guerra infernal."""
from kit import *  # noqa
from musica import M, Musica, F, i_brass, i_bass, p_taiko, p_tom, p_cymbal, p_swell, p_timpani


def field_snare(g=1.0):
    """Caixa militar grave, com esteira solta."""
    d = 0.45
    y = bbp(white(d), 250, 7000, 2) * env_exp(d, 0.09) * 1.1 + sine(160, d) * env_exp(d, 0.05) * 0.7
    y += bp(white(d), 3500, 1.2) * env_exp(d, 0.14) * 0.35
    return y * g


def roll(m, bus, bar, beat, beats, g0=0.2, g1=0.8, step=0.125):
    k = int(beats / step)
    for i in range(k):
        m.put(bus, field_snare(g0 + (g1 - g0) * i / max(1, k - 1)) * 0.6, bar, beat + i * step, 1.0, 0.2)


def drag(d=1.2):
    """Metal arrastado: corrente e lamina raspando na pedra."""
    sc = creak(d, 14, 22, (700, 1700, 3300), 1.2) * 0.5
    return add(sc, chain(d, 40, 1.0, 1.6) * 0.7)


@M('chefe_andras', 'Chefe Andras, o General Partido: marcha de guerra infernal com tambores, caixa militar, metal arrastado, cornetas e coro de soldados', lufs=-15)
def _(v):
    m = Musica(104, 32, 4, tail=8)
    m.bus('tambor', 1.0, 'cripta', 0.25)
    m.bus('caixa', 0.8, 'cripta', 0.2)
    m.bus('metal', 0.7, 'cripta', 0.3)
    m.bus('metais', 0.9, 'catedral', 0.3)
    m.bus('baixo', 0.8, None, 0)
    m.bus('coro', 0.9, 'catedral', 0.4)
    m.bus('orgao', 0.6, 'catedral', 0.4)
    # ostinato de marcha (frigio em Re)
    ost = ['D2', 'D2', 'D2', 'Eb2', 'D2', 'D2', 'C2', 'D2']
    for b in range(32):
        # tambores de guerra: 1 e 3 sempre; colcheias de tom na secao B
        m.put('tambor', p_taiko(1.0, 46), b, 0)
        m.put('tambor', p_taiko(0.8, 50), b, 2)
        if 4 <= b < 28:
            m.put('tambor', p_taiko(0.45, 52), b, 3.5)
        if 16 <= b < 28:
            for bt in (1, 1.5, 3):
                m.put('tambor', p_tom(95, 0.45), b, bt, 1.0, -0.3)
        # caixa militar: padrao de marcha com flams
        if b >= 4:
            for bt, g in [(1, 0.8), (2.75, 0.4), (3, 0.9), (3.5, 0.35), (3.75, 0.45)]:
                m.put('caixa', field_snare(g), b, bt, 1.0, 0.2)
                if g > 0.7:
                    m.put('caixa', field_snare(g * 0.35), b, bt - 0.03, 1.0, 0.2)  # flam
        if b < 28 and b >= 4:
            for k in range(4):
                nt = ost[(b % 2) * 4 + k]
                m.put('baixo', i_bass(F(nt), 0.85 * m.spb, 380, 2.2), b, k, 0.9)
                m.put('metais', i_brass(F(nt) * 2, 0.6 * m.spb, 0.6, 0.8, 2.5) * 0.35, b, k)
        # metal arrastado a cada dois compassos
        if b % 2 == 1:
            m.put('metal', drag(1.5), b, 2.5, 0.8, 0.4 if b % 4 == 1 else -0.4)
    # intro: rufo crescendo e corneta de guerra
    roll(m, 'caixa', 2, 0, 8, 0.1, 0.9)
    for b, nts in [(1, [('D3', 2), ('A3', 1), ('D4', 3), ('Eb4', 2)]), (13, [('D3', 2), ('A3', 1), ('D4', 3), ('Eb4', 2)])]:
        m.seq('metais', lambda f, d: i_brass(f, d, 0.9, 1.2, 2.8), nts, b, 0, 0.9)
    m.put('orgao', organ(['D1', 'D2', 'A2'], 16 * m.spb, 'grave', 0.004, 2, 2), 0, 0, 0.8)
    m.put('orgao', organ(['D1', 'D2', 'Ab2'], 16 * m.spb, 'grave', 0.004, 2, 2), 28, 0, 0.8)
    # coro de soldados mortos: canto de marcha
    chant = [['D3', 'A3'], ['F3', 'C4'], ['Eb3', 'Bb3'], ['D3', 'A3']]
    for b in range(8, 28, 1):
        ch = chant[b % 4]
        m.put('coro', choir(ch, 1.8 * m.spb, 'o', 'baixo', 5, 0.03, 0.3, vib=0.004), b, 0, 0.7)
        m.put('coro', choir(ch, 1.8 * m.spb, 'a', 'baixo', 5, 0.03, 0.3, vib=0.004), b, 2, 0.55)
    # melodia da Legiao (secao B)
    mel = [('D4', 2), ('Eb4', 1), ('F4', 1), ('G4', 2), ('F4', 1), ('Eb4', 1), ('D4', 3), ('C4', 1), ('D4', 4),
           ('A4', 2), ('G4', 1), ('F4', 1), ('G4', 2), ('Eb4', 2), ('F4', 2), ('Eb4', 1), ('C4', 1), ('D4', 4)]
    m.seq('metais', lambda f, d: i_brass(f, d, 1.0, 0.8, 2.4), mel, 16, 0, 1.0, 0.1)
    m.seq('metais', lambda f, d: i_brass(f, d, 0.9, 0.8, 2.4), mel, 16, 0, 0.6, -0.1, oct_=-1)
    m.seq('metais', lambda f, d: i_brass(f, d, 1.0, 0.8, 2.4), mel[:9], 24, 0, 0.9, 0.1, oct_=1)
    for b in (4, 16, 24):
        m.put('tambor', p_cymbal(0.8, 3), b, 0)
    m.put('tambor', p_swell(2 * m.spb * 2, 0.6), 15, 0)
    m.put('tambor', p_timpani(F('D2'), 1.1), 28, 0)
    # ponte 28-31: so tambores, arrasto e o rufo levando de volta ao comeco
    roll(m, 'caixa', 31, 0, 4, 0.1, 0.7)
    return m.render()
