"""Trilha sonora do DARK PASSAGE: composicoes escritas nota a nota e sintetizadas.

Todas em loop sem emenda (a cauda do fim volta para o comeco).
"""
from kit import *  # noqa
from registro import som

ALT = {'Bb': 'A#', 'Eb': 'D#', 'Ab': 'G#', 'Db': 'C#', 'Gb': 'F#'}


def F(n):
    return hz(n)


# ======================================================== instrumentos
def i_strings(f, d, bright=1600, attack=0.35, vib=0.005):
    return strings([f], d + 0.6, attack, 0.6, bright, 0.007, vib)


def i_solo(f, d, bright=2600, attack=0.12):
    """Violino/violoncelo solo: uma voz com vibrato expressivo e arco."""
    dd = d + 0.4
    fv = vibrato(f, dd, 5.6, 0.007, 0.25)
    y = saw(fv, dd) * 0.6 + saw(fv * 1.002, dd) * 0.4
    env = env_pts(dd, [(0, 0), (attack, 1), (max(attack, d - 0.05), 0.85), (dd, 0)], 1.3)
    y = lp(y, bright * (0.6 + 0.4 * env), 0.8)
    y = peq(y, 2800, 4, 1.5)  # corpo do violino
    y = peq(y, 450, 3, 1.2)
    y += bp(white(dd), 2500, 0.6) * env * 0.03
    return y * env * 0.35


def i_brass(f, d, bright=1.0, growl=0.0, drive=1.6):
    return blp(brass(f, d + 0.25, 0.06, 0.25, bright, growl, drive), 6000, 2)


def i_flute(f, d):
    dd = d + 0.25
    fv = vibrato(f, dd, 5.0, 0.006, 0.3)
    y = sine(fv, dd) + 0.25 * sine(fv * 2, dd) + 0.06 * sine(fv * 3, dd)
    env = env_pts(dd, [(0, 0), (0.07, 1), (max(0.07, d - 0.05), 0.8), (dd, 0)], 1.2)
    y += bp(white(dd), f * 2, 2) * 0.15
    return y * env * 0.3


def i_pluck(f, d, bright=0.45):
    y = pluck(f, max(d, 0.3) + 1.8, bright, 0.9965)
    y = add(y, bp(y, 220, 2) * 0.5, bp(y, 1100, 2) * 0.2)  # corpo de madeira
    return y * 0.5


def i_bass(f, d, cut=500, drive=1.5):
    dd = d + 0.12
    y = saw(f, dd) * 0.6 + square(f * 0.5, dd) * 0.3
    env = env_pts(dd, [(0, 0), (0.01, 1), (max(0.02, d - 0.03), 0.8), (dd, 0)])
    y = lp(y, cut * (0.6 + 0.8 * env), 1.1)
    return sat(y * env, drive) * 0.5


def i_musicbox(f, d=None):
    f = f * (1 + R().normal(0, 0.003))
    return modal(2.0, [f, f * 3.95, f * 9.2], [0.7, 0.18, 0.06], [1, 0.25, 0.08]) * 0.35


def i_voice(f, d, vowel='a', voz='soprano', vib=0.022):
    dd = d + 0.35
    fv = vibrato(f, dd, 5.4, vib, 0.15)
    src = glottal(fv, dd, 0.004, 0.05, 0.05, 2000)
    y = formant(src, vowel, voz, 1.0) * 2.2
    env = env_pts(dd, [(0, 0), (0.1, 1), (max(0.1, d - 0.05), 0.9), (dd, 0)], 1.2)
    return y * env * 0.5


def p_taiko(g=1.0, f=None):
    f = f or ru(48, 56)
    return drum(f, 1.4, 0.45, True, 0.7, 0.5) * g


def p_tom(f=110, g=1.0):
    return drum(f, 0.7, 0.18, True, 0.5, 0.4) * g


def p_timpani(f=hz('D2'), g=1.0):
    return drum(f, 2.5, 0.9, True, 0.3, 0.05) * g


def p_kick(g=1.0):
    return sat(thump(52, 0.5, 3.0, 0.14, 0.4), 2) * g


def p_anvil(g=1.0):
    return anvil(ru(1050, 1150), 0.9) * 0.5 * g


def p_snare(g=1.0):
    d = 0.4
    y = bbp(white(d), 300, 9000, 2) * env_exp(d, 0.07) * 1.2 + sine(185, d) * env_exp(d, 0.04) * 0.6
    y += metal(d, 450, 10, decay=0.06, bright=1.2) * 0.25
    return y * g


def p_hat(g=1.0, open_=False):
    d = 0.5 if open_ else 0.12
    y = hp(white(d), 7000) * env_exp(d, 0.18 if open_ else 0.025) + metal(d, 6200, 8, decay=0.04, bright=2) * 0.1
    return y * g * 0.5


def p_steam(g=1.0, d=0.3):
    return blp(steam(d, 5000, 0.003, d * 0.3), 9000, 2) * g * 0.28


def p_cymbal(g=1.0, d=3.0):
    """Prato: brilho metalico denso, chiado curto, cauda que escurece."""
    t = tt(d)
    shimmer = metal(d, ru(380, 460), 60, inharm=1.3, decay=d * 0.5, bright=2.2) * 0.5
    hiss = bbp(white(d), 4000, 11000, 2) * env_exp(d, 0.25) * 0.25
    y = blp(shimmer + hiss, 10000, 2)
    y = lp(y, 9000 * np.exp(-t / (d * 0.6)) + 2500)
    return y * g * 0.45


def p_swell(d=2.0, g=1.0):
    """Prato ao contrario: puxa para a proxima secao."""
    return reverse(p_cymbal(1.0, d)) * g


def p_bones(g=1.0):
    return add(wood_knock(ru(800, 1200), 0.1), wood_knock(ru(900, 1300), 0.1) * 0.6) * g


# ======================================================== musica
class Musica:
    def __init__(self, bpm, bars, beats=4, tail=8.0):
        self.spb = 60.0 / bpm
        self.beats = beats
        self.bars = bars
        self.L = bars * beats * self.spb
        self.buses = {}
        self.cfg = {}
        self.tail = tail

    def bus(self, name, gain=1.0, espaco='catedral', send=0.3, hp_=30):
        self.cfg[name] = (gain, espaco, send, hp_)
        self.buses[name] = np.zeros((ns(self.L + self.tail), 2))

    def t(self, bar, beat=0.0):
        return (bar * self.beats + beat) * self.spb

    def put(self, name, sig, bar, beat=0.0, g=1.0, p=0.0):
        at = self.t(bar, beat)
        if at >= self.L + self.tail:
            return
        s = pan(sig, p) if sig.ndim == 1 else sig
        b = place(self.buses[name], s * g, at)
        self.buses[name] = b[:ns(self.L + self.tail)]

    def seq(self, name, inst, notes, bar, beat=0.0, g=1.0, p=0.0, legato=1.0, oct_=0):
        """notes = [(nota|None, batidas), ...]"""
        pos = bar * self.beats + beat
        for n, b in notes:
            if n is not None:
                f = F(n) * 2 ** oct_
                self.put(name, inst(f, b * self.spb * legato), 0, pos, g, p)
            pos += b

    def render(self, lufs=-16, comp=True, loop=True):
        n = ns(self.L)
        out = np.zeros((ns(self.L + self.tail + 12), 2))
        for name, x in self.buses.items():
            g, esp, send, hp_ = self.cfg[name]
            if loop:  # dobra o que passa do fim e filtra em circulo (sem degrau na emenda)
                f = x[:n].copy()
                k = n
                while k < len(x):
                    seg = x[k:k + n]
                    f[:len(seg)] += seg
                    k += n
                pre = min(n, ns(3.0))
                x = bhp(np.concatenate([f[n - pre:], f]), hp_, 2)[pre:]
            else:
                x = bhp(x, hp_, 2)
            if esp:
                x = reverb(x, esp, send, tail=True)
            out = place(out, x * g, 0)
        if not loop:
            return out
        # loop: tudo que passa do fim volta para o comeco
        y = out[:n].copy()
        k = n
        while k < len(out):
            seg = out[k:k + n]
            y[:len(seg)] += seg
            k += n
        if comp:
            pre = ns(4.0)
            yy = np.concatenate([y[-pre:], y])
            yy = compress(yy, -20, 2.5, 0.02, 0.25)
            y = yy[pre:]
        return y


def M(id, desc, lufs=-17):
    return som('musica/' + id, lufs=lufs, loop=True, desc=desc, bus='musica')


def chord(m, name, inst, notes, bar, beats, g=1.0, p=0.0):
    for i, nt in enumerate(notes):
        m.put(name, inst(F(nt), beats * m.spb), bar, 0, g / np.sqrt(len(notes)), p + (i - len(notes) / 2) * 0.15)


def arp(m, name, inst, notes, bar, pattern, step=0.5, g=1.0, p=0.0, bars=1):
    """Arpejo: pattern = indices em notes, um por passo."""
    pos = 0.0
    total = bars * m.beats
    i = 0
    while pos < total - 1e-6:
        nt = notes[pattern[i % len(pattern)]]
        m.put(name, inst(F(nt), step * m.spb * 1.5), bar, pos, g, p)
        pos += step
        i += 1


# ======================================================== 1. TEMA PRINCIPAL
@M('tema_principal', 'Tema principal / menu: sinos, orgao e coro; tema no violoncelo, depois explode com trombetas e tambores', lufs=-16)
def _(v):
    m = Musica(72, 32, 4, tail=10)
    m.bus('orgao', 0.8, 'catedral', 0.45)
    m.bus('coro', 0.9, 'catedral', 0.5)
    m.bus('cordas', 1.0, 'catedral', 0.35)
    m.bus('solo', 1.0, 'catedral', 0.3)
    m.bus('metais', 0.85, 'catedral', 0.35)
    m.bus('tambor', 1.0, 'cripta', 0.3)
    m.bus('sino', 0.7, 'catedral', 0.5)
    prog = [(['D3', 'F3', 'A3'], 'D2'), (['D3', 'F3', 'A3'], 'D2'), (['D3', 'F3', 'Bb3'], 'Bb1'), (['D3', 'F3', 'Bb3'], 'Bb1'),
            (['D3', 'G3', 'Bb3'], 'G1'), (['D3', 'G3', 'Bb3'], 'G1'), (['C#3', 'E3', 'A3'], 'A1'), (['C#3', 'E3', 'A3'], 'A1')]
    # --- intro e ponte final (0-7 e 28-31): pedal, sinos, coro "u"
    for start, nb in [(0, 8), (28, 4)]:
        m.put('orgao', organ(['D1', 'D2', 'A2'], nb * 4 * m.spb + 1, 'grave', 0.002, 3, 3), start, 0, 0.9)
        for b in range(start, start + nb, 2):
            m.put('sino', bell(F('D3'), 7, 5, 0.9) * 0.8, b, 0)
            m.put('sino', bell(F('A2'), 6, 4, 0.9) * 0.4, b, 2)
    m.put('coro', choir(['D3', 'F3', 'A3'], 4 * 4 * m.spb + 1, 'u', 'baixo', 4, 3, 2), 0, 0, 0.8)
    m.put('coro', choir(['D3', 'F3', 'Bb3'], 2 * 4 * m.spb + 0.5, 'u', 'baixo', 4, 1.5, 1.5), 4, 0, 0.8)
    m.put('coro', choir(['C#3', 'E3', 'A3'], 2 * 4 * m.spb + 0.5, 'u', 'baixo', 4, 1.5, 2), 6, 0, 0.8)
    m.put('cordas', strings(['D2', 'A2'], 4 * 4 * m.spb, 3, 2, 900), 4, 0, 0.8)
    m.put('coro', choir(['D3', 'F3', 'A3'], 4 * 4 * m.spb, 'u', 'baixo', 4, 2, 3), 28, 0, 0.7)
    # --- tema A (8-15): violoncelo solo
    melA = [('D4', 2), ('F4', 1), ('E4', 1), ('D4', 3), ('A3', 1), ('Bb3', 2), ('C4', 1), ('D4', 1), ('F4', 3), ('E4', 1),
            ('D4', 2), ('Bb3', 1), ('G3', 1), ('A3', 2), ('Bb3', 1), ('C4', 1), ('C#4', 2), ('D4', 1), ('E4', 1), ('A3', 4)]
    m.seq('solo', lambda f, d: i_solo(f, d, 2200, 0.15), melA, 8, 0, 1.0, -0.1)
    for i, (ch, root) in enumerate(prog):
        b = 8 + i
        if i % 2 == 0:
            m.put('coro', choir(ch, 2 * 4 * m.spb + 0.6, 'o', 'baixo', 4, 0.8, 1.2), b, 0, 0.6)
            m.put('cordas', strings([root, F(root) * 2], 2 * 4 * m.spb, 0.8, 1.0, 900), b, 0, 0.9)
        if i >= 4:
            m.put('tambor', p_taiko(0.5 + 0.1 * (i - 4)), b, 0)
    m.put('tambor', p_swell(2 * m.spb * 2, 0.6), 14, 0)
    for k in range(8):
        m.put('tambor', p_tom(110 + 10 * (k % 2), 0.3 + 0.06 * k), 15, 2 + k * 0.25)
    # --- tema B (16-23): tudo junto
    melB = [('D5', 2), ('F5', 1), ('A5', 1), ('G5', 2), ('F5', 1), ('E5', 1), ('F5', 2), ('D5', 1), ('Bb4', 1), ('C5', 3), ('D5', 1),
            ('Bb4', 2), ('D5', 1), ('G5', 1), ('F5', 2), ('E5', 1), ('D5', 1), ('C#5', 2), ('E5', 2), ('A4', 4)]
    m.seq('metais', lambda f, d: i_brass(f, d, 0.9, 0.3, 1.8), melB, 16, 0, 0.9)
    m.seq('metais', lambda f, d: i_brass(f, d, 0.7, 0.3, 1.8), melB, 16, 0, 0.5, oct_=-1)
    m.seq('solo', lambda f, d: i_solo(f, d, 3000, 0.08), melB, 16, 0, 0.7, 0.2)
    for i, (ch, root) in enumerate(prog):
        b = 16 + i
        m.put('orgao', organ(ch + [root], 4 * m.spb + 0.3, 'pleno', 0.002, 0.05, 0.4), b, 0, 0.7)
        if i % 2 == 0:
            up = [n[:-1] + str(int(n[-1]) + 1) for n in ch]
            m.put('coro', choir(ch + up, 2 * 4 * m.spb + 0.6, 'a', 'tenor', 4, 0.3, 1.0), b, 0, 0.9)
            m.put('sino', bell(F(root) * 4, 4, 2.5, 1.0) * 0.4, b, 0)
        m.put('cordas', strings([root, F(root) * 2], 4 * m.spb, 0.1, 0.3, 1400), b, 0, 0.9)
        for bt, g in [(0, 1.0), (1.5, 0.5), (2, 0.8), (3, 0.6), (3.5, 0.5)]:
            m.put('tambor', p_taiko(g), b, bt)
    m.put('tambor', p_cymbal(0.8, 4), 16, 0)
    # --- resolucao (24-27)
    m.put('metais', i_brass(F('D5'), 4 * 4 * m.spb * 0.8, 0.8, 0.2, 1.6) * 0.8, 24, 0)
    m.put('metais', i_brass(F('A4'), 4 * 4 * m.spb * 0.8, 0.7, 0.2, 1.6) * 0.5, 24, 0)
    m.put('coro', choir(['D3', 'A3', 'D4', 'F4', 'A4'], 4 * 4 * m.spb, 'a', 'tenor', 5, 0.1, 5), 24, 0, 1.0)
    m.put('orgao', organ(['D2', 'A2', 'D3', 'F3', 'A3'], 4 * 4 * m.spb, 'pleno', 0.002, 0.05, 5), 24, 0, 0.8)
    m.put('tambor', p_timpani(F('D2'), 1.2), 24, 0)
    m.put('tambor', p_cymbal(1.0, 6), 24, 0)
    m.put('sino', bell(F('D3'), 8, 6, 0.9), 24, 0)
    return m.render()


# ======================================================== 2. SAO LAZARO (exploracao)
@M('sao_lazaro', 'Area inicial (exploracao): orgao desafinado distante, vento, sinos abafados e um violino solitario', lufs=-19)
def _(v):
    m = Musica(60, 32, 4, tail=12)
    m.bus('orgao', 0.9, 'catedral', 0.6, 60)
    m.bus('solo', 0.85, 'catedral', 0.45)
    m.bus('alaude', 0.8, 'cripta', 0.35)
    m.bus('fundo', 0.8, None, 0)
    m.bus('sino', 0.6, 'catedral', 0.6)
    chords = [['D3', 'F3', 'A3', 'D4'], ['D3', 'G3', 'Bb3', 'D4'], ['D3', 'F3', 'Bb3', 'D4'], ['C#3', 'E3', 'A3', 'C#4'],
              ['D3', 'F3', 'A3', 'D4'], ['Eb3', 'G3', 'Bb3', 'Eb4'], ['C3', 'E3', 'G3', 'C4'], ['C#3', 'E3', 'A3', 'C#4']]
    for i in range(8):
        o = organ(chords[i], 4 * 4 * m.spb + 2.5, 'flauta', 0.009, 2.0, 2.5, 0.15, 0.02)
        m.put('orgao', blp(o, 1500, 2), i * 4, 0, 0.9, 0)
    m.put('orgao', organ(['D1', 'D2'], m.L, 'grave', 0.003, 4, 4, 0, 0) * 0.5, 0, 0, 1.0)
    from ambiente import wind
    w = wind(m.L + 3, 0.5, 380, 0.08, 0.2)
    w = loopify(w, 3.0)
    m.put('fundo', w * 0.35, 0, 0)
    for b in [2, 10, 18, 26]:
        m.put('sino', blp(bell(F('D3'), 8, 6, 0.8), 1200, 2) * 0.8, b, 1, 1.0, 0.4)
    mel1 = [('A4', 3), ('G4', 1), ('F4', 2), ('E4', 2), ('D4', 4), (None, 2), ('E4', 1), ('F4', 1),
            ('G4', 3), ('F4', 1), ('E4', 2), ('C#4', 2), ('D4', 4), (None, 4)]
    mel2 = [('D5', 3), ('C5', 1), ('Bb4', 2), ('A4', 2), ('G4', 2), ('Bb4', 2), ('A4', 4),
            ('F4', 2), ('G4', 1), ('A4', 1), ('Bb4', 2), ('A4', 1), ('G4', 1), ('E4', 2), ('C#4', 2), ('D4', 4)]
    m.seq('solo', lambda f, d: i_solo(f, d, 3000, 0.25), mel1, 8, 0, 0.8, 0.2)
    m.seq('solo', lambda f, d: i_solo(f, d, 3000, 0.25), mel2, 20, 0, 0.8, 0.2)
    arps = [[0, 1, 2, 3, 2, 1, 2, 3]]
    for i in range(16, 32):
        ch = chords[i // 4]
        lo = [n[:-1] + str(int(n[-1]) - 1) for n in ch[:1]] + ch[1:]
        arp(m, 'alaude', lambda f, d: i_pluck(f, d, 0.35), lo, i, arps[0], 0.5, 0.35, -0.3)
    return m.render()


# ======================================================== 3. ACAMPAMENTO DA VELA
@M('acampamento_vela', 'Acampamento da Vela (base segura): violao em 6/8, violoncelo, flauta de lata e um coro baixinho', lufs=-18)
def _(v):
    m = Musica(168, 48, 6, tail=8)  # batida = colcheia, compasso 6/8
    m.bus('violao', 0.9, 'quarto', 0.25)
    m.bus('cello', 0.8, 'cripta', 0.35)
    m.bus('flauta', 0.8, 'cripta', 0.35)
    m.bus('coro', 0.6, 'catedral', 0.5)
    m.bus('fogo', 0.5, None, 0)
    P = [('A2', ['A3', 'C4', 'E4']), ('F2', ['F3', 'A3', 'C4']), ('C3', ['G3', 'C4', 'E4']), ('G2', ['G3', 'B3', 'D4']),
         ('A2', ['A3', 'C4', 'E4']), ('F2', ['F3', 'A3', 'C4']), ('E2', ['E3', 'G#3', 'B3']), ('E2', ['E3', 'G#3', 'B3']),
         ('F2', ['F3', 'A3', 'C4']), ('G2', ['G3', 'B3', 'D4']), ('A2', ['A3', 'C4', 'E4']), ('A2', ['A3', 'C4', 'E4']),
         ('D3', ['F3', 'A3', 'D4']), ('A2', ['A3', 'C4', 'E4']), ('E2', ['E3', 'G#3', 'B3']), ('A2', ['A3', 'C4', 'E4'])]
    for b in range(48):
        root, tri = P[b % 16]
        notes = [root] + tri
        arp(m, 'violao', lambda f, d: i_pluck(f, d, 0.5), notes, b, [0, 1, 2, 3, 2, 1], 1, 0.55, -0.2)
        if b % 2 == 0:
            m.put('cello', i_strings(F(root), 12 * m.spb, 1100, 0.4), b, 0, 0.8, 0.2)
    melA = [('E5', 3), ('D5', 1), ('C5', 2), ('A4', 3), ('C5', 3), ('G4', 2), ('E4', 1), ('G4', 3), ('D5', 4), ('B4', 2),
            ('C5', 3), ('B4', 1), ('A4', 2), ('C5', 2), ('A4', 1), ('F4', 3), ('G#4', 3), ('B4', 3), ('E5', 6)]
    melB = [('F5', 3), ('E5', 1), ('D5', 2), ('D5', 3), ('B4', 3), ('C5', 2), ('B4', 1), ('A4', 3), ('E4', 6),
            ('F4', 3), ('A4', 1), ('D5', 2), ('C5', 3), ('A4', 3), ('B4', 2), ('G#4', 1), ('B4', 3), ('A4', 6)]
    m.seq('flauta', i_flute, melA, 16, 0, 0.9, 0.1, 0.95)
    m.seq('flauta', i_flute, melB, 24, 0, 0.9, 0.1, 0.95)
    m.seq('cello', lambda f, d: i_solo(f, d, 2400, 0.2), melA, 32, 0, 0.8, -0.1, oct_=-1)
    m.seq('cello', lambda f, d: i_solo(f, d, 2400, 0.2), melB, 40, 0, 0.8, -0.1, oct_=-1)
    for b in range(32, 48, 2):
        root, tri = P[b % 16]
        m.put('coro', choir(tri, 12 * m.spb + 0.5, 'u', 'alto', 3, 0.8, 1.0), b, 0, 0.5)
    from kit import fire as _fire
    fz = loopify(to_stereo(blp(_fire(m.L + 2, 0.3, 10), 4000)), 2.0)
    m.put('fogo', fz * 0.3, 0, 0)
    return m.render()


# ======================================================== 4. CAPELA (Arautos)
@M('capela', 'Capela de Sao Lazaro (base dos Arautos): coral solene de orgao e coro, majestoso e corrompido', lufs=-18)
def _(v):
    m = Musica(60, 24, 4, tail=12)
    m.bus('orgao', 0.9, 'catedral', 0.5)
    m.bus('coro', 1.0, 'catedral', 0.5)
    m.bus('sino', 0.6, 'catedral', 0.6)
    # coral a 4 vozes: (soprano, contralto, tenor, baixo) por meia-nota
    S = ['D5', 'D5', 'C#5', 'D5', 'D5', 'C5', 'Bb4', 'A4', 'F5', 'E5', 'C5', 'D5', 'D5', 'C#5', 'D5', 'D5']
    A_ = ['A4', 'Bb4', 'A4', 'A4', 'F4', 'F4', 'G4', 'E4', 'A4', 'G4', 'A4', 'F4', 'G4', 'E4', 'F4', 'F4']
    T = ['F4', 'G4', 'E4', 'F4', 'D4', 'C4', 'D4', 'C#4', 'D4', 'C4', 'F4', 'Bb3', 'Bb3', 'A3', 'A3', 'A3']
    B = ['D3', 'G2', 'A2', 'D3', 'Bb2', 'F2', 'G2', 'A2', 'D3', 'C3', 'F2', 'Bb2', 'G2', 'A2', 'D2', 'D2']
    for rep in range(3):
        for k in range(16):
            bar = rep * 8 + k // 2
            beat = (k % 2) * 2
            dur = 2 * m.spb
            ch = [B[k], T[k], A_[k], S[k]]
            if rep == 1:
                m.put('orgao', organ(ch + [B[k][:-1] + str(int(B[k][-1]) - 1)], dur + 0.15, 'pleno', 0.003, 0.04, 0.3), bar, beat, 0.9)
                m.put('coro', choir([S[k]], dur + 0.4, 'a', 'soprano', 5, 0.08, 0.4), bar, beat, 0.8)
                m.put('coro', choir([T[k], A_[k]], dur + 0.4, 'a', 'tenor', 4, 0.08, 0.4), bar, beat, 0.6)
                m.put('coro', choir([B[k]], dur + 0.4, 'o', 'baixo', 4, 0.08, 0.4), bar, beat, 0.6)
            else:
                m.put('orgao', organ(ch, dur + 0.2, 'flauta', 0.004, 0.08, 0.4, 0.1, 0.02), bar, beat, 0.9)
                m.put('coro', choir([S[k], A_[k]], dur + 0.4, 'u', 'alto', 4, 0.15, 0.5), bar, beat, 0.5)
        m.put('sino', bell(F('D3'), 7, 5, 0.9) * 0.6, rep * 8, 0)
    m.put('sino', bell(F('A3'), 6, 4, 0.9) * 0.4, 8, 2)
    m.put('sino', bell(F('D4'), 6, 4, 0.9) * 0.3, 12, 0)
    return m.render()


# ======================================================== 5. CRIPTA (exploracao da dungeon)
@M('cripta', 'Cripta da Trombeta Calada (exploracao): drones graves, pulso de coracao, coro dissonante e metal raspando', lufs=-20)
def _(v):
    m = Musica(60, 30, 4, tail=12)  # 120 s, tempo livre
    m.bus('drone', 1.0, 'cripta', 0.3, 20)
    m.bus('coro', 0.8, 'ossario', 0.6)
    m.bus('pulso', 0.9, 'cripta', 0.2, 20)
    m.bus('metal', 0.6, 'catedral', 0.6)
    m.bus('cordas', 0.6, 'catedral', 0.5)
    d = m.L
    t = tt(d)
    t2 = tt(d + 4)
    dr2 = 0
    for f, a in [(F('D1'), 0.5), (F('D1') * 1.003, 0.4), (F('A1'), 0.25), (F('Eb2'), 0.08), (F('D2'), 0.15)]:
        dr2 = dr2 + np.sin(2 * np.pi * f * t2 + ru(0, 6)) * a
    dr2 = loopify(widen(dr2 * 0.6 + lp(brown(d + 4), 120) * 0.3, 0.3), 4.0)
    dr2 = dr2 * (0.75 + 0.25 * np.sin(2 * np.pi * t / d * 3))[:, None]  # 3 respiracoes por loop
    m.put('drone', dr2, 0, 0)
    for b in range(8, 22, 1):  # pulso de coracao no meio
        m.put('pulso', lp(heartbeat(4 * m.spb, 60, 0.8), 250), b, 0, 0.7)
    for b, ch, vw in [(2, ['D3', 'Eb3', 'A3'], 'u'), (10, ['C#3', 'D3', 'G#3'], 'o'), (18, ['D3', 'Eb3', 'Bb3'], 'u'), (24, ['C3', 'D3', 'Ab3'], 'o')]:
        c = choir(ch, 14, vw, 'baixo', 4, 6, 6, vib=0.01)
        m.put('coro', c, b, 0, 0.8)
    for b in [5, 13, 21, 27]:
        m.put('metal', reverse(bell(F(R().choice(['D5', 'Eb5', 'A4'])), 4, 2, 1.0)) * 0.5, b, 0, 1.0, ru(-0.7, 0.7))
        m.put('metal', creak(3.0, 12, 18, (900, 2300, 4100), 1.0) * 0.25, b, 2, 1.0, ru(-0.7, 0.7))
    for b in [14, 22]:
        m.put('cordas', strings(['A4', 'Bb4'], 6 * 4 * m.spb * 0.5, 4, 4, 2500, 0.003, 0.01) * 0.5, b, 0)
    for b in [16, 17, 18, 19]:
        m.put('pulso', p_taiko(0.35, 42), b, 0)
    for b, nts in [(9, ['D5', 'Eb5', 'A4']), (25, ['A4', 'Eb5', 'D5'])]:
        for i, nt in enumerate(nts):
            m.put('metal', i_musicbox(F(nt)) * 0.6, b, i * 1.5, 1.0, 0.3)
    return m.render()


# ======================================================== 6. COMBATE
@M('combate', 'Combate (elites e encrencas fora da dungeon): ostinato de cordas, taikos, metais e coro', lufs=-16)
def _(v):
    m = Musica(132, 32, 4, tail=6)
    m.bus('cordas', 0.9, 'cripta', 0.25)
    m.bus('baixo', 0.8, None, 0)
    m.bus('metais', 0.85, 'cripta', 0.3)
    m.bus('coro', 0.8, 'catedral', 0.35)
    m.bus('perc', 1.0, 'cripta', 0.2)
    roots = ['D', 'D', 'Bb', 'Bb', 'G', 'G', 'A', 'A']
    oct3 = {'D': 'D3', 'Bb': 'Bb2', 'G': 'G2', 'A': 'A2'}
    pat = [0, 0, 3, 0, 5, 0, 3, 2]  # semitons sobre a raiz (ostinato menor)
    for b in range(32):
        r = roots[b % 8]
        f0 = F(oct3[r])
        for k, s in enumerate(pat):
            m.put('cordas', i_strings(f0 * 2 ** (s / 12) * 2, 0.5 * m.spb, 2600, 0.01, 0.002) * 1.4, b, k * 0.5, 1.0, -0.3)
            m.put('baixo', i_bass(f0 / 2, 0.45 * m.spb, 450, 1.6), b, k * 0.5, 0.9)
        for bt, g in [(0, 1.0), (0.5, 0.35), (2, 0.8), (2.75, 0.4), (3, 0.6)]:
            m.put('perc', p_taiko(g), b, bt)
        if b >= 8:
            m.put('perc', p_snare(0.5), b, 1)
            m.put('perc', p_snare(0.6), b, 3)
        if b % 4 == 3:
            for k in range(4):
                m.put('perc', p_tom(130 - 12 * k, 0.5), b, 3 + k * 0.25)
        if b % 2 == 0:
            chd = {'D': ['D3', 'F3', 'A3'], 'Bb': ['Bb2', 'D3', 'F3'], 'G': ['G2', 'Bb2', 'D3'], 'A': ['A2', 'C#3', 'E3']}[r]
            for bt in (0, 1.5):
                for nt in chd:
                    m.put('metais', i_brass(F(nt), 0.4 * m.spb, 0.9, 0.4, 2) * 0.4, b, bt)
            if b >= 16:
                m.put('coro', choir([n[:-1] + str(int(n[-1]) + 1) for n in chd], 2 * 4 * m.spb, 'a', 'tenor', 4, 0.05, 0.5), b, 0, 0.8)
    mel = [('D5', 2), ('A4', 1), ('D5', 1), ('F5', 2), ('E5', 1), ('D5', 1), ('Bb4', 2), ('F5', 2), ('D5', 4),
           ('G4', 2), ('Bb4', 1), ('D5', 1), ('G5', 2), ('F5', 1), ('E5', 1), ('E5', 2), ('C#5', 2), ('A4', 4)]
    m.seq('metais', lambda f, d: i_brass(f, d, 1.0, 0.3, 2.0), mel, 16, 0, 1.0, 0.1)
    m.seq('metais', lambda f, d: i_brass(f, d, 1.0, 0.3, 2.0), mel, 24, 0, 1.0, 0.1)
    m.seq('cordas', lambda f, d: i_solo(f, d, 3200, 0.05), mel, 24, 0, 0.5, 0.3, oct_=1)
    m.put('perc', p_swell(2 * m.spb * 2, 0.6), 7, 0)
    m.put('perc', p_cymbal(0.8, 3), 8, 0)
    m.put('perc', p_swell(2 * m.spb * 2, 0.7), 15, 0)
    m.put('perc', p_cymbal(1.0, 3), 16, 0)
    m.put('perc', p_cymbal(0.7, 3), 24, 0)
    m.put('perc', p_swell(2 * m.spb * 2, 0.5), 31, 0)
    return m.render()


# ======================================================== 7. CHEFE: ANDRAS (em musica_andras.py)


# ======================================================== 8. CHEFE: IRMA CELESTE
@M('chefe_celeste', 'Chefe Irma Celeste, a Carpideira: valsa-requiem em 3/4 com voz solo, caixinha de musica, coro e ossos', lufs=-16)
def _(v):
    m = Musica(108, 48, 3, tail=8)
    m.bus('valsa', 0.8, 'ossario', 0.3)
    m.bus('voz', 1.0, 'ossario', 0.45)
    m.bus('coro', 0.8, 'ossario', 0.5)
    m.bus('cordas', 0.8, 'ossario', 0.4)
    m.bus('caixinha', 0.7, 'ossario', 0.45)
    m.bus('perc', 0.9, 'ossario', 0.3)
    P = [('D2', ['D3', 'F3', 'A3']), ('D2', ['D3', 'F3', 'A3']), ('G2', ['G3', 'Bb3', 'D4']), ('G2', ['G3', 'Bb3', 'D4']),
         ('A1', ['G3', 'C#4', 'E4']), ('A1', ['G3', 'C#4', 'E4']), ('D2', ['D3', 'F3', 'A3']), ('D2', ['D3', 'F3', 'A3']),
         ('Bb1', ['D3', 'F3', 'Bb3']), ('Bb1', ['D3', 'F3', 'Bb3']), ('G2', ['G3', 'Bb3', 'D4']), ('G2', ['G3', 'Bb3', 'D4']),
         ('Eb2', ['Eb3', 'G3', 'Bb3']), ('Eb2', ['Eb3', 'G3', 'Bb3']), ('A1', ['A3', 'C#4', 'E4']), ('A1', ['A3', 'C#4', 'E4'])]
    mel = [('A4', 3), ('D5', 2), ('E5', 1), ('F5', 2), ('E5', 1), ('D5', 3), ('C#5', 2), ('D5', 1), ('E5', 2), ('G5', 1),
           ('F5', 2), ('E5', 1), ('D5', 3), ('D5', 2), ('F5', 1), ('Bb5', 3), ('A5', 2), ('G5', 1), ('D5', 3),
           ('Eb5', 2), ('G5', 1), ('Bb5', 2), ('A5', 1), ('A5', 2), ('G5', 1), ('E5', 2), ('C#5', 1)]
    for b in range(48):
        root, tri = P[b % 16]
        cyc = b // 16
        m.put('valsa', i_pluck(F(root), 1.0, 0.3) * 1.3, b, 0, 1.0, -0.1)
        for bt in (1, 2):
            for nt in tri:
                m.put('valsa', i_pluck(F(nt), 0.8, 0.25) * 0.4, b, bt, 1.0, 0.2)
        if cyc >= 1:
            m.put('perc', p_timpani(F(root) * (2 if F(root) < 60 else 1), 0.5), b, 0)
        if cyc == 2:
            m.put('perc', p_bones(0.5), b, 1, 1.0, -0.5)
            m.put('perc', p_bones(0.4), b, 2, 1.0, 0.5)
        if b % 2 == 0:
            m.put('cordas', strings([root, F(root) * 2], 2 * 3 * m.spb, 0.3, 0.6, 1100), b, 0, 0.9)
            if cyc >= 1:
                m.put('coro', choir(tri, 2 * 3 * m.spb + 0.4, 'o' if cyc == 1 else 'a', 'baixo' if cyc == 1 else 'tenor', 4, 0.3, 0.8), b, 0, 0.7)
    m.seq('caixinha', lambda f, d: i_musicbox(f * 2), mel, 0, 0, 1.0, 0.3)
    m.seq('voz', lambda f, d: i_voice(f, d, 'a', 'soprano', 0.025), mel, 16, 0, 1.0)
    m.seq('voz', lambda f, d: i_voice(f, d, 'o', 'soprano', 0.025), mel, 32, 0, 0.9)
    m.seq('cordas', lambda f, d: i_solo(f, d, 3000, 0.1), mel, 32, 0, 0.6, -0.2)
    for b in (16, 32):
        m.put('perc', bell(F('D4'), 6, 4, 1.0) * 0.4, b, 0)
    m.put('perc', p_swell(3 * m.spb * 2, 0.5), 30, 0)
    return m.render()


# ======================================================== 9. CHEFE: ZACARIAS
@M('chefe_zacarias', 'Chefe Zacarias, o Arauto: epico com orgao pleno, coro, trombetas, taikos e o motivo da meia nota', lufs=-15)
def _(v):
    m = Musica(96, 40, 4, tail=10)
    m.bus('orgao', 0.8, 'catedral', 0.4)
    m.bus('coro', 1.0, 'catedral', 0.4)
    m.bus('cordas', 0.9, 'catedral', 0.3)
    m.bus('metais', 0.9, 'catedral', 0.3)
    m.bus('perc', 1.0, 'catedral', 0.2)
    m.bus('sino', 0.6, 'catedral', 0.5)

    def motivo(bar):  # a meia nota: A4 longo que tenta subir para D5 e engasga
        m.put('metais', i_brass(F('A4'), 2.6 * m.spb, 1.0, 0.4, 2.2), bar, 0, 0.9)
        m.put('metais', blp(i_brass(F('D5'), 0.5 * m.spb, 1.3, 1.2, 3.0), 3000), bar, 3, 0.7)

    # intro 0-3
    m.put('orgao', organ(['D1', 'D2', 'A2', 'D3', 'F3', 'A3'], 4 * 4 * m.spb + 1, 'pleno', 0.002, 3, 2), 0, 0, 0.8)
    m.put('coro', choir(['D3', 'A3', 'D4', 'F4'], 4 * 4 * m.spb, 'a', 'baixo', 5, 5, 2), 0, 0, 0.8)
    motivo(2)
    m.put('sino', bell(F('D3'), 8, 6, 0.9), 0, 0)
    # A 4-19
    progA = [(['D3', 'F3', 'A3'], 'D2'), (['D3', 'F3', 'Bb3'], 'Bb1'), (['D3', 'G3', 'Bb3'], 'G1'), (['C#3', 'E3', 'A3'], 'A1')]
    for i in range(8):
        ch, root = progA[i % 4]
        b = 4 + i * 2
        m.put('coro', choir(ch + [n[:-1] + str(int(n[-1]) + 1) for n in ch], 2 * 4 * m.spb + 0.5, 'a', 'tenor', 4, 0.3, 0.8), b, 0, 0.8)
        m.put('cordas', strings([root, F(root) * 2], 2 * 4 * m.spb, 0.2, 0.4, 1200), b, 0, 0.9)
        for bb in (b, b + 1):
            for k in range(8):
                m.put('cordas', i_strings(F(ch[k % 3]) * 2, 0.45 * m.spb, 2800, 0.01, 0.002) * 1.2, bb, k * 0.5, 0.8, 0.3)
            for bt, g in [(0, 1.0), (1, 0.6), (2, 0.9), (3, 0.6), (3.5, 0.5)]:
                m.put('perc', p_taiko(g), bb, bt)
            for nt in ch:
                m.put('metais', i_brass(F(nt), 0.9 * m.spb, 0.8, 0.3, 2) * 0.35, bb, 0)
    for b in (11, 19):
        m.put('perc', p_swell(2 * m.spb * 2, 0.7), b, 0)
    motivo(10)
    motivo(18)
    # B 20-35
    progB = [(['D3', 'F3', 'A3'], 'D2'), (['D3', 'G3', 'Bb3'], 'G1'), (['Eb3', 'G3', 'Bb3'], 'Eb2'), (['C#3', 'E3', 'A3'], 'A1'),
             (['D3', 'F3', 'A3'], 'D2'), (['D3', 'F3', 'Bb3'], 'Bb1'), (['C#3', 'E3', 'A3'], 'A1'), (['C#3', 'E3', 'A3'], 'A1'),
             (['D3', 'F3', 'A3'], 'D2'), (['D3', 'G3', 'Bb3'], 'G1'), (['Eb3', 'G3', 'Bb3'], 'Eb2'), (['C#3', 'E3', 'A3'], 'A1'),
             (['D3', 'F3', 'Bb3'], 'Bb1'), (['D3', 'G3', 'Bb3'], 'G1'), (['C#3', 'E3', 'A3'], 'A1'), (['D3', 'F3', 'A3'], 'D2')]
    mel = [('D5', 3), ('A4', 1), ('Bb4', 2), ('C5', 1), ('D5', 1), ('Eb5', 3), ('D5', 1), ('C#5', 4),
           ('D5', 2), ('F5', 2), ('G5', 3), ('F5', 1), ('E5', 2), ('C#5', 1), ('E5', 1), ('A5', 4),
           ('D5', 3), ('A4', 1), ('Bb4', 2), ('C5', 1), ('D5', 1), ('Eb5', 3), ('D5', 1), ('C#5', 4),
           ('D5', 2), ('Bb5', 2), ('A5', 3), ('G5', 1), ('E5', 2), ('C#5', 2), ('D5', 4)]
    m.seq('metais', lambda f, d: i_brass(f, d, 1.1, 0.4, 2.2), mel, 20, 0, 1.0)
    m.seq('metais', lambda f, d: i_brass(f, d, 1.0, 0.4, 2.2), mel, 20, 0, 0.55, oct_=-1)
    m.seq('coro', lambda f, d: i_voice(f, d, 'a', 'soprano', 0.018), mel, 20, 0, 0.7)
    for i, (ch, root) in enumerate(progB):
        b = 20 + i
        m.put('orgao', organ(ch + [root], 4 * m.spb + 0.3, 'pleno', 0.002, 0.04, 0.4), b, 0, 0.8)
        m.put('coro', choir(ch + [n[:-1] + str(int(n[-1]) + 1) for n in ch], 4 * m.spb + 0.5, 'a', 'tenor', 4, 0.1, 0.5), b, 0, 0.8)
        for k in range(8):
            m.put('cordas', i_strings(F(ch[k % 3]) * 2, 0.45 * m.spb, 3000, 0.01, 0.002) * 1.2, b, k * 0.5, 0.8, 0.3)
        for bt, g in [(0, 1.0), (0.5, 0.4), (1, 0.7), (2, 1.0), (2.5, 0.4), (3, 0.7), (3.5, 0.6), (3.75, 0.5)]:
            m.put('perc', p_taiko(g), b, bt)
        m.put('perc', p_snare(0.4), b, 1)
        m.put('perc', p_snare(0.5), b, 3)
        if i % 4 == 0:
            m.put('perc', p_cymbal(0.9, 3), b, 0)
            m.put('sino', bell(F(root) * 4, 5, 3, 1.0) * 0.4, b, 0)
    # ponte 36-39 (volta para a intro)
    m.put('orgao', organ(['D1', 'D2', 'A2', 'D3'], 4 * 4 * m.spb, 'grave', 0.002, 0.1, 4), 36, 0, 0.9)
    m.put('perc', p_timpani(F('D2'), 1.2), 36, 0)
    m.put('perc', p_cymbal(1.0, 5), 36, 0)
    m.put('sino', bell(F('D3'), 8, 6, 0.9), 36, 0)
    motivo(37)
    m.put('coro', choir(['D3', 'A3', 'D4'], 3 * 4 * m.spb, 'u', 'baixo', 4, 2, 3), 37, 0, 0.7)
    return m.render()


# ======================================================== vinhetas (nao sao loop)
def V(id, desc, lufs=-15):
    return som('musica/vinheta/' + id, lufs=lufs, desc=desc, bus='musica', espaco=None)


@V('vitoria_chefe', 'Vinheta: chefe derrotado (fanfarra em Re maior, sinos e coro)')
def _(v):
    m = Musica(80, 5, 4, tail=8)
    m.bus('metais', 0.9, 'catedral', 0.35)
    m.bus('coro', 1.0, 'catedral', 0.4)
    m.bus('orgao', 0.8, 'catedral', 0.4)
    m.bus('perc', 1.0, 'catedral', 0.3)
    fan = [('D4', 0.5), ('D4', 0.5), ('A4', 1), ('D5', 1), ('F#5', 1), ('E5', 0.5), ('F#5', 0.5), ('A5', 4)]
    m.seq('metais', lambda f, d: i_brass(f, d, 1.0, 0.2, 1.8), fan, 0, 0, 1.0)
    m.seq('metais', lambda f, d: i_brass(f, d, 1.0, 0.2, 1.8), fan, 0, 0, 0.5, oct_=-1)
    m.put('coro', choir(['D3', 'A3', 'D4', 'F#4', 'A4'], 3 * 4 * m.spb, 'a', 'tenor', 5, 0.3, 3), 2, 0, 1.0)
    m.put('orgao', organ(['D2', 'A2', 'D3', 'F#3', 'A3', 'D4'], 3 * 4 * m.spb, 'pleno', 0.002, 0.05, 3), 2, 0, 0.9)
    m.put('perc', p_timpani(F('D2'), 1.2), 2, 0)
    m.put('perc', p_cymbal(1.0, 5), 2, 0)
    for i, nt in enumerate(['D5', 'F#5', 'A5', 'D6']):
        m.put('perc', bell(F(nt), 4, 2.5, 1.2) * 0.3, 2, i * 0.25)
    m.put('perc', p_taiko(0.9), 0, 0)
    m.put('perc', p_taiko(0.7), 0, 2)
    return m.render(comp=False, loop=False)


@V('descoberta_area', 'Vinheta: entrou numa area nova (coro sobe + sino)', lufs=-18)
def _(v):
    y = np.zeros((ns(7), 2))
    y = place(y, choir(['D3', 'A3', 'D4', 'E4'], 5, 'u', 'alto', 4, 1.8, 2.5, vowel2='a'), 0)
    y = place(y, to_stereo(bell(F('D4'), 5, 3.5, 1.0) * 0.5), 1.6)
    y = place(y, to_stereo(bell(F('A4'), 4, 3, 1.0) * 0.3), 1.7)
    return reverb(y, 'catedral', 0.4)


@V('entrar_cripta', 'Vinheta: desce para a cripta (metais graves, tambor e coro)', lufs=-16)
def _(v):
    y = np.zeros((ns(9), 2))
    y = place(y, to_stereo(blp(add(brass(F('D2'), 4, 0.8, 2, 0.8, 0.8, 2.5), brass(F('A2'), 4, 0.8, 2, 0.8, 0.8, 2.5) * 0.6), 3000)), 0)
    y = place(y, choir(['D2', 'A2', 'D3', 'Eb3'], 5, 'o', 'baixo', 5, 1.5, 3), 0.5)
    y = place(y, to_stereo(p_timpani(F('D2'), 1.0)), 0)
    y = place(y, to_stereo(p_taiko(0.9, 45)), 2.2)
    y = place(y, to_stereo(bell(F('D3'), 7, 5, 0.8) * 0.5), 2.2)
    return reverb(y, 'catedral', 0.35)
