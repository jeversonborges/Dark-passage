"""DARK PASSAGE - motor de sintese de audio.

Tudo e gerado por sintese e processamento (numpy + numba + scipy), sem samples
externos. Sinais mono sao arrays 1D float64; estereo e (N, 2).
"""
import os
import subprocess
import numpy as np
import numba as nb
import scipy.signal as ss
import soundfile as sf

SR = 44100
_RNG = np.random.default_rng(1)


def seed(s):
    global _RNG
    _RNG = np.random.default_rng(s)


def rng():
    return _RNG


def ns(dur):
    return max(1, int(round(dur * SR)))


def tt(dur):
    return np.arange(ns(dur)) / SR


def arr(v, n):
    """Escalar ou array -> array de tamanho n (interpolado se tamanho diferente)."""
    if np.isscalar(v):
        return np.full(n, float(v))
    v = np.asarray(v, dtype=float)
    if len(v) == n:
        return v
    return np.interp(np.linspace(0, 1, n), np.linspace(0, 1, len(v)), v)


# ---------------------------------------------------------------- ruido
def white(dur):
    return _RNG.standard_normal(ns(dur)) * 0.3


def pink(dur):
    n = ns(dur)
    X = np.fft.rfft(_RNG.standard_normal(n))
    f = np.arange(len(X))
    f[0] = 1
    y = np.fft.irfft(X / np.sqrt(f), n)
    return y / (np.std(y) + 1e-12) * 0.3


def brown(dur):
    n = ns(dur)
    X = np.fft.rfft(_RNG.standard_normal(n))
    f = np.arange(len(X)).astype(float)
    f[0] = 1
    y = np.fft.irfft(X / f, n)
    y = ss.sosfilt(ss.butter(1, 20, 'hp', fs=SR, output='sos'), y)
    return y / (np.std(y) + 1e-12) * 0.3


def crackle(dur, density=30, decay=0.002):
    """Estalos esparsos (fogo, vinil, faiscas)."""
    n = ns(dur)
    y = np.zeros(n)
    k = _RNG.poisson(density * dur)
    pos = _RNG.integers(0, n, k)
    amps = _RNG.uniform(0.2, 1, k) * _RNG.choice([-1, 1], k)
    y[pos] = amps
    ir = np.exp(-np.arange(ns(decay * 6)) / (decay * SR)) * _RNG.standard_normal(ns(decay * 6))
    return np.convolve(y, ir)[:n]


# ---------------------------------------------------------------- envelopes
def env_exp(dur, decay, attack=0.0):
    t = tt(dur)
    e = np.exp(-t / max(decay, 1e-5))
    if attack > 0:
        e *= np.clip(t / attack, 0, 1)
    return e


def env_pts(dur, pts, curve=None):
    """pts = [(tempo, valor), ...] interpolacao linear (curve>0 deixa exponencial)."""
    t = tt(dur)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    e = np.interp(t, xs, ys)
    if curve:
        e = np.sign(e) * np.abs(e) ** curve
    return e


def env_adsr(dur, a=0.01, d=0.1, s=0.7, r=0.2):
    hold = max(dur - r, a + d)
    return env_pts(dur, [(0, 0), (a, 1), (a + d, s), (hold, s), (dur, 0)])


def fade(x, fin=0.002, fout=0.01):
    x = x.copy()
    a, b = ns(fin), ns(fout)
    if x.ndim == 1:
        x[:a] *= np.linspace(0, 1, a)
        x[-b:] *= np.linspace(1, 0, b)
    else:
        x[:a] *= np.linspace(0, 1, a)[:, None]
        x[-b:] *= np.linspace(1, 0, b)[:, None]
    return x


# ---------------------------------------------------------------- osciladores
def phase(freq, n):
    f = arr(freq, n)
    return np.cumsum(f) / SR


def sine(freq, dur, ph=0.0):
    n = ns(dur)
    return np.sin(2 * np.pi * phase(freq, n) + ph)


@nb.njit(cache=True)
def _saw_blep(f, ph0):
    n = len(f)
    y = np.empty(n)
    p = ph0
    for i in range(n):
        dt = f[i] / 44100.0
        v = 2.0 * p - 1.0
        if p < dt:
            x = p / dt
            v -= x + x - x * x - 1.0
        elif p > 1.0 - dt:
            x = (p - 1.0) / dt
            v -= x * x + x + x + 1.0
        y[i] = v
        p += dt
        if p >= 1.0:
            p -= 1.0
    return y


def saw(freq, dur, ph=None):
    n = ns(dur)
    return _saw_blep(arr(freq, n), _RNG.uniform() if ph is None else ph)


def square(freq, dur, pw=0.5):
    n = ns(dur)
    f = arr(freq, n)
    p0 = _RNG.uniform()
    a = _saw_blep(f, p0)
    b = _saw_blep(f, (p0 + pw) % 1.0)
    return (a - b) * 0.5


def tri(freq, dur):
    n = ns(dur)
    p = phase(freq, n) % 1.0
    return 4 * np.abs(p - 0.5) - 1


def supersaw(freq, dur, voices=7, detune=0.012):
    y = 0
    for k in range(voices):
        d = 1 + detune * (k - (voices - 1) / 2) / max(1, (voices - 1) / 2)
        y = y + saw(arr(freq, ns(dur)) * d, dur)
    return y / np.sqrt(voices)


def glottal(freq, dur, jitter=0.004, shimmer=0.05, breath=0.05, tilt=900):
    """Fonte vocal: dente-de-serra com jitter/shimmer, inclinacao espectral e sopro."""
    n = ns(dur)
    f = arr(freq, n)
    jit = ss.sosfilt(ss.butter(2, 30, fs=SR, output='sos'), _RNG.standard_normal(n)) * jitter * 25
    src = _saw_blep(f * (1 + jit), _RNG.uniform())
    shim = 1 + ss.sosfilt(ss.butter(2, 20, fs=SR, output='sos'), _RNG.standard_normal(n)) * shimmer * 20
    src = -src * shim
    src = ss.sosfilt(ss.butter(1, tilt, fs=SR, output='sos'), src) * 3
    if breath:
        src = src + white(dur) * breath * (0.5 + 0.5 * np.sin(2 * np.pi * phase(f, n)))
    return src


def vibrato(freq, dur, rate=5.5, depth=0.01, delay=0.2):
    t = tt(dur)
    ramp = np.clip(t / max(delay, 1e-3), 0, 1)
    r = rate * (1 + 0.05 * np.sin(2 * np.pi * 0.3 * t))
    return arr(freq, len(t)) * (1 + depth * ramp * np.sin(2 * np.pi * np.cumsum(r) / SR))


# ---------------------------------------------------------------- filtros
@nb.njit(cache=True)
def _svf(x, fc, q, mode):
    n = len(x)
    y = np.empty(n)
    ic1 = 0.0
    ic2 = 0.0
    for i in range(n):
        f = fc[i]
        if f < 10.0:
            f = 10.0
        if f > 20000.0:
            f = 20000.0
        g = np.tan(np.pi * f / 44100.0)
        k = 1.0 / q[i]
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if mode == 0:
            y[i] = v2
        elif mode == 1:
            y[i] = v1
        elif mode == 2:
            y[i] = x[i] - k * v1 - v2
        elif mode == 3:
            y[i] = x[i] - k * v1
        else:
            y[i] = k * v1
    return y


def _filt(x, fc, q, mode):
    if x.ndim == 2:
        return np.stack([_filt(x[:, c], fc, q, mode) for c in range(2)], 1)
    n = len(x)
    return _svf(np.ascontiguousarray(x, dtype=np.float64), arr(fc, n), arr(q, n), mode)


def lp(x, fc, q=0.707):
    return _filt(x, fc, q, 0)


def bp(x, fc, q=2.0):
    """Passa-banda com ganho unitario no pico."""
    return _filt(x, fc, q, 4)


def hp(x, fc, q=0.707):
    return _filt(x, fc, q, 2)


def notch(x, fc, q=2.0):
    return _filt(x, fc, q, 3)


def blp(x, fc, order=4):
    sos = ss.butter(order, min(fc, SR / 2 - 100), 'lp', fs=SR, output='sos')
    return ss.sosfilt(sos, x, axis=0)


def bhp(x, fc, order=4):
    sos = ss.butter(order, fc, 'hp', fs=SR, output='sos')
    return ss.sosfilt(sos, x, axis=0)


def bbp(x, lo, hi, order=3):
    sos = ss.butter(order, [lo, min(hi, SR / 2 - 100)], 'bp', fs=SR, output='sos')
    return ss.sosfilt(sos, x, axis=0)


def peq(x, f0, gain_db, q=1.0):
    A = 10 ** (gain_db / 40)
    w = 2 * np.pi * f0 / SR
    al = np.sin(w) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w), 1 - al * A]
    a = [1 + al / A, -2 * np.cos(w), 1 - al / A]
    return ss.lfilter(b, a, x, axis=0)


def shelf(x, f0, gain_db, high=True):
    A = 10 ** (gain_db / 40)
    w = 2 * np.pi * f0 / SR
    al = np.sin(w) / 2 * np.sqrt(2)
    c = np.cos(w)
    sA = 2 * np.sqrt(A) * al
    if high:
        b = [A * ((A + 1) + (A - 1) * c + sA), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - sA)]
        a = [(A + 1) - (A - 1) * c + sA, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - sA]
    else:
        b = [A * ((A + 1) - (A - 1) * c + sA), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sA)]
        a = [(A + 1) + (A - 1) * c + sA, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sA]
    return ss.lfilter(b, a, x, axis=0)


# formantes (Hz, dB, largura Hz) - tabela classica de canto
FORMANTS = {
    'baixo': {
        'a': ([600, 1040, 2250, 2450, 2750], [0, -7, -9, -9, -20], [60, 70, 110, 120, 130]),
        'e': ([400, 1620, 2400, 2800, 3100], [0, -12, -9, -12, -18], [40, 80, 100, 120, 120]),
        'i': ([250, 1750, 2600, 3050, 3340], [0, -30, -16, -22, -28], [60, 90, 100, 120, 120]),
        'o': ([400, 750, 2400, 2600, 2900], [0, -11, -21, -20, -40], [40, 80, 100, 120, 120]),
        'u': ([350, 600, 2400, 2675, 2950], [0, -20, -32, -28, -36], [40, 80, 100, 120, 120]),
    },
    'tenor': {
        'a': ([650, 1080, 2650, 2900, 3250], [0, -6, -7, -8, -22], [80, 90, 120, 130, 140]),
        'e': ([400, 1700, 2600, 3200, 3580], [0, -14, -12, -14, -20], [70, 80, 100, 120, 120]),
        'i': ([290, 1870, 2800, 3250, 3540], [0, -15, -18, -20, -30], [40, 90, 100, 120, 120]),
        'o': ([400, 800, 2600, 2800, 3000], [0, -10, -12, -12, -26], [40, 80, 100, 120, 120]),
        'u': ([350, 600, 2700, 2900, 3300], [0, -20, -17, -14, -26], [40, 60, 100, 120, 120]),
    },
    'alto': {
        'a': ([800, 1150, 2800, 3500, 4950], [0, -4, -20, -36, -60], [80, 90, 120, 130, 140]),
        'e': ([400, 1600, 2700, 3300, 4950], [0, -24, -30, -35, -60], [60, 80, 120, 150, 200]),
        'i': ([350, 1700, 2700, 3700, 4950], [0, -20, -30, -36, -60], [50, 100, 120, 150, 200]),
        'o': ([450, 800, 2830, 3500, 4950], [0, -9, -16, -28, -55], [70, 80, 100, 130, 135]),
        'u': ([325, 700, 2530, 3500, 4950], [0, -12, -30, -40, -64], [50, 60, 170, 180, 200]),
    },
    'soprano': {
        'a': ([800, 1150, 2900, 3900, 4950], [0, -6, -32, -20, -50], [80, 90, 120, 130, 140]),
        'e': ([350, 2000, 2800, 3600, 4950], [0, -20, -15, -40, -56], [60, 100, 120, 150, 200]),
        'i': ([270, 2140, 2950, 3900, 4950], [0, -12, -26, -26, -44], [60, 90, 100, 120, 120]),
        'o': ([450, 800, 2830, 3800, 4950], [0, -11, -22, -22, -50], [70, 80, 100, 130, 135]),
        'u': ([325, 700, 2700, 3800, 4950], [0, -16, -35, -40, -60], [50, 60, 170, 180, 200]),
    },
}


def formant(x, vowel='a', voz='baixo', shift=1.0, vowel2=None, morph=None):
    """Filtra x pelo banco de formantes. vowel2+morph (0..1 array) faz transicao."""
    fs, gs, bws = FORMANTS[voz][vowel]
    n = len(x)
    if vowel2 is not None:
        fs2, gs2, bws2 = FORMANTS[voz][vowel2]
        m = arr(morph, n)
    y = np.zeros(n)
    for i in range(5):
        if vowel2 is None:
            f = fs[i] * shift
            g = 10 ** (gs[i] / 20)
            q = fs[i] / bws[i]
            y += bp(x, f, q) * g
        else:
            f = (fs[i] * (1 - m) + fs2[i] * m) * shift
            g = 10 ** ((gs[i] * (1 - m) + gs2[i] * m) / 20)
            q = f / ((bws[i] * (1 - m) + bws2[i] * m) * shift)
            y += bp(x, f, q) * g
    return y


# ---------------------------------------------------------------- distorcao
def sat(x, drive=2.0):
    return np.tanh(x * drive) / np.tanh(drive)


def fold(x, amount=2.0):
    return np.sin(x * amount * np.pi / 2)


def crush(x, bits=8, down=1):
    q = 2 ** (bits - 1)
    y = np.round(x * q) / q
    if down > 1:
        y = np.repeat(y[::down], down, axis=0)[:len(x)]
    return y


# ---------------------------------------------------------------- modal / ressonadores
def modal(dur, freqs, decays, amps, phases=None, attack=0.0005):
    t = tt(dur)
    y = np.zeros(len(t))
    for i, (f, d, a) in enumerate(zip(freqs, decays, amps)):
        if f >= SR / 2 - 200:
            continue
        p = 0 if phases is None else phases[i]
        y += a * np.exp(-t / d) * np.sin(2 * np.pi * f * t + p)
    if attack:
        y *= np.clip(t / attack, 0, 1)
    return y


def metal(dur, f0, n=24, inharm=1.0, decay=1.0, bright=1.0, seed_=None):
    """Objeto metalico (chapa, lamina, sino pequeno): parciais inarmonicos."""
    r = np.random.default_rng(seed_) if seed_ is not None else _RNG
    ratios = np.sort(np.concatenate([[1.0], 1 + r.uniform(0.3, 9, n - 1) ** (1.0 + 0.2 * inharm)]))
    freqs = f0 * ratios
    dec = decay * (ratios ** -0.6) * r.uniform(0.6, 1.4, n)
    amps = (ratios ** (-1.0 / bright)) * r.uniform(0.3, 1, n)
    return modal(dur, freqs, dec, amps, r.uniform(0, 6.28, n))


BELL_RATIOS = [0.5, 1.0, 1.183, 1.506, 2.0, 2.514, 2.662, 3.011, 4.166, 5.433, 6.796, 8.215]
BELL_AMPS = [0.6, 0.9, 0.7, 0.35, 1.0, 0.35, 0.25, 0.4, 0.25, 0.15, 0.1, 0.06]
BELL_DEC = [1.0, 0.75, 0.55, 0.45, 0.4, 0.3, 0.25, 0.22, 0.15, 0.1, 0.08, 0.06]


def bell(f0, dur, decay=6.0, bright=1.0, strike=True):
    """Sino de igreja: parciais de hum/prime/tierce/quint/nominal com batimentos."""
    y = 0
    for r, a, d in zip(BELL_RATIOS, BELL_AMPS, BELL_DEC):
        for dt in (-0.0015, 0.0015):  # pares levemente desafinados -> batimento
            y = y + modal(dur, [f0 * r * (1 + dt)], [decay * d], [a * (r ** (bright - 1)) * 0.5],
                          [_RNG.uniform(0, 6.28)])
    if strike:
        y = y + bp(white(dur) * env_exp(dur, 0.006), f0 * 5, 1.5) * 1.5
    return y


@nb.njit(cache=True)
def _ks(exc, delay, damp, fb):
    n = len(exc)
    y = np.zeros(n)
    buf_len = 4096
    buf = np.zeros(buf_len)
    w = 0
    last = 0.0
    for i in range(n):
        d = delay[i]
        rpos = w - d
        while rpos < 0:
            rpos += buf_len
        i0 = int(rpos)
        frac = rpos - i0
        s = buf[i0 % buf_len] * (1 - frac) + buf[(i0 + 1) % buf_len] * frac
        last = last + damp * (s - last)
        v = exc[i] + fb * last
        buf[w] = v
        y[i] = v
        w = (w + 1) % buf_len
    return y


def pluck(f0, dur, bright=0.5, decay=0.996, exc=None):
    """Corda dedilhada (Karplus-Strong)."""
    n = ns(dur)
    if exc is None:
        exc = np.zeros(n)
        k = max(2, int(SR / f0))
        e = _RNG.uniform(-1, 1, k)
        e = lp(e, 800 + 7000 * bright)
        exc[:k] = e
    d = arr(SR / np.asarray(f0, dtype=float), n) if not np.isscalar(f0) else np.full(n, SR / f0 - 0.5)
    return _ks(exc, d, 0.3 + 0.65 * bright, decay)


def resonate(x, freqs, qs, gains):
    y = np.zeros_like(x)
    for f, q, g in zip(freqs, qs, gains):
        y += bp(x, f, q) * g
    return y


# ---------------------------------------------------------------- tempo
@nb.njit(cache=True)
def _vdelay(x, d, fb, damp):
    n = len(x)
    L = 1 << 18
    buf = np.zeros(L)
    y = np.zeros(n)
    w = 0
    lpv = 0.0
    for i in range(n):
        rpos = w - d[i]
        while rpos < 0:
            rpos += L
        i0 = int(rpos)
        fr = rpos - i0
        s = buf[i0 % L] * (1 - fr) + buf[(i0 + 1) % L] * fr
        lpv = lpv + damp * (s - lpv)
        buf[w] = x[i] + fb * lpv
        y[i] = s
        w = (w + 1) % L
    return y


def delay(x, time, fb=0.3, damp=0.5, mix=0.3):
    n = len(x)
    d = arr(time * SR, n)
    return x + mix * _vdelay(np.ascontiguousarray(x, dtype=np.float64), d, fb, damp)


def chorus(x, voices=3, depth=0.004, rate=0.6, base=0.015):
    """Mono -> estereo com coro."""
    n = len(x)
    t = np.arange(n) / SR
    L = x * 0.6
    R = x * 0.6
    for v in range(voices):
        ph = _RNG.uniform(0, 6.28)
        r = rate * _RNG.uniform(0.7, 1.3)
        d = (base + depth * (1 + np.sin(2 * np.pi * r * t + ph)) / 2) * SR
        w = _vdelay(np.ascontiguousarray(x, dtype=np.float64), d, 0.0, 1.0)
        if v % 2 == 0:
            L += w * 0.5
            R += w * 0.25
        else:
            R += w * 0.5
            L += w * 0.25
    return np.stack([L, R], 1)


def varispeed(x, rate):
    """Muda velocidade/altura (rate escalar ou curva)."""
    n = len(x)
    if np.isscalar(rate):
        idx = np.arange(0, n - 1, rate)
    else:
        r = np.asarray(rate, float)
        pos = np.cumsum(np.interp(np.arange(int(n / np.min(r)) + 1), np.arange(len(r)), r))
        idx = pos[pos < n - 1]
    if x.ndim == 1:
        return np.interp(idx, np.arange(n), x)
    return np.stack([np.interp(idx, np.arange(n), x[:, c]) for c in range(2)], 1)


def reverse(x):
    return x[::-1].copy()


# ---------------------------------------------------------------- espaco
_IR_CACHE = {}

ESPACOS = {
    # rt60 graves/medios/agudos, pre-delay, densidade de reflexoes iniciais, largura
    'quarto': dict(rt=(0.5, 0.4, 0.25), pre=0.004, er=0.012, w=0.6),
    'rua': dict(rt=(1.2, 0.9, 0.5), pre=0.012, er=0.03, w=0.9),
    'abatedouro': dict(rt=(2.2, 1.8, 0.9), pre=0.02, er=0.035, w=0.9),
    'cripta': dict(rt=(3.5, 2.8, 1.2), pre=0.025, er=0.04, w=1.0),
    'ossario': dict(rt=(4.5, 3.6, 1.6), pre=0.03, er=0.05, w=1.0),
    'catedral': dict(rt=(7.5, 6.0, 2.8), pre=0.05, er=0.07, w=1.0),
    'infinito': dict(rt=(12.0, 10.0, 5.0), pre=0.08, er=0.1, w=1.0),
}


def make_ir(nome):
    if nome in _IR_CACHE:
        return _IR_CACHE[nome]
    p = ESPACOS[nome]
    r = np.random.default_rng(abs(hash(nome)) % 9999)
    rt_lo, rt_mid, rt_hi = p['rt']
    dur = rt_lo * 1.1 + p['pre']
    n = ns(dur)
    t = np.arange(n) / SR
    ir = np.zeros((n, 2))
    bands = [(None, 300, rt_lo), (300, 3000, rt_mid), (3000, None, rt_hi)]
    for c in range(2):
        nz = r.standard_normal(n)
        out = np.zeros(n)
        for lo, hi, rt in bands:
            if lo is None:
                b = ss.sosfilt(ss.butter(3, hi, 'lp', fs=SR, output='sos'), nz)
            elif hi is None:
                b = ss.sosfilt(ss.butter(3, lo, 'hp', fs=SR, output='sos'), nz)
            else:
                b = ss.sosfilt(ss.butter(3, [lo, hi], 'bp', fs=SR, output='sos'), nz)
            out += b * np.exp(-6.9 * t / rt)
        # entrada suave da cauda difusa
        out *= np.clip((t - p['pre']) / (p['er'] + 1e-3), 0, 1) ** 1.5
        # reflexoes iniciais esparsas
        for k in range(14):
            tk = p['pre'] + r.uniform(0.001, p['er'] * 1.5)
            ir[int(tk * SR), c] += r.uniform(0.2, 0.7) * r.choice([-1, 1]) * np.exp(-tk * 8)
        ir[:, c] += out * 0.12
    mid = ir.mean(1, keepdims=True)
    ir = mid + (ir - mid) * p['w']
    ir /= np.sqrt(np.sum(ir ** 2) / 2)
    _IR_CACHE[nome] = ir
    return ir


def to_stereo(x):
    if x.ndim == 2:
        return x
    return np.stack([x, x], 1)


def reverb(x, espaco='cripta', mix=0.3, tail=True, hp_send=120, lp_send=9000):
    """Convolucao com resposta de sala sintetica. Retorna estereo."""
    x = to_stereo(x)
    ir = make_ir(espaco)
    send = bhp(blp(x, lp_send, 2), hp_send, 2)
    wet = np.stack([ss.fftconvolve(send[:, c], ir[:, c]) for c in range(2)], 1)
    if not tail:
        wet = wet[:len(x)]
    out = np.zeros((len(wet), 2))
    out[:len(x)] = x * (1 - mix * 0.5)
    out += wet * mix
    return out


# ---------------------------------------------------------------- mixagem
def pan(x, p=0.0):
    """p em -1..1 (pode ser curva). Lei de potencia constante."""
    if x.ndim == 2:
        x = x.mean(1)
    p = arr(p, len(x))
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1)


def widen(x, amt=0.3, ms=0.012):
    """Mono -> estereo largo (Haas + decorrelacao suave)."""
    if x.ndim == 2:
        x = x.mean(1)
    d = ns(ms)
    side = np.concatenate([np.zeros(d), x[:-d]]) - x
    side = bbp(side, 300, 9000, 2)
    return np.stack([x + amt * side, x - amt * side], 1)


def place(dst, src, at, gain=1.0):
    """Soma src em dst a partir de 'at' segundos (cresce dst se preciso)."""
    i = int(round(at * SR))
    src = _tailfade(src)
    if src.ndim == 1 and dst.ndim == 2:
        src = to_stereo(src)
    if dst.ndim == 1 and src.ndim == 2:
        dst = to_stereo(dst)
    end = i + len(src)
    if end > len(dst):
        pad = np.zeros((end - len(dst),) + dst.shape[1:])
        dst = np.concatenate([dst, pad])
    dst[i:end] += src * gain
    return dst


def mix(*items, dur=None):
    """items = (sinal, inicio_s, ganho[, pan]) ..."""
    out = np.zeros((ns(dur) if dur else 1, 2))
    for it in items:
        sig, at, g = it[0], it[1], it[2]
        if len(it) > 3:
            sig = pan(sig, it[3])
        out = place(out, to_stereo(sig), at, g)
    return out


def silence(dur, stereo=True):
    return np.zeros((ns(dur), 2)) if stereo else np.zeros(ns(dur))


@nb.njit(cache=True)
def _env_follow(x, att, rel):
    n = len(x)
    e = np.zeros(n)
    v = 0.0
    for i in range(n):
        a = x[i]
        if a > v:
            v = att * v + (1 - att) * a
        else:
            v = rel * v + (1 - rel) * a
        e[i] = v
    return e


def compress(x, thresh_db=-18, ratio=4, attack=0.005, release=0.12, makeup_db=0.0):
    mono = np.abs(x).max(1) if x.ndim == 2 else np.abs(x)
    att = np.exp(-1 / (attack * SR))
    rel = np.exp(-1 / (release * SR))
    e = _env_follow(mono, att, rel)
    db = 20 * np.log10(e + 1e-9)
    over = np.maximum(db - thresh_db, 0)
    g = 10 ** ((-over * (1 - 1 / ratio) + makeup_db) / 20)
    return x * (g[:, None] if x.ndim == 2 else g)


def limit(x, ceiling_db=-1.0, release=0.06):
    """Limitador com lookahead simples."""
    c = 10 ** (ceiling_db / 20)
    mono = np.abs(x).max(1) if x.ndim == 2 else np.abs(x)
    la = ns(0.003)
    pk = ss.maximum_filter1d(mono, la * 2 + 1) if hasattr(ss, 'maximum_filter1d') else _maxf(mono, la)
    need = np.maximum(pk / c, 1.0)
    rel = np.exp(-1 / (release * SR))
    g = 1 / _env_follow(need, 0.0, rel)
    g = np.minimum(g, 1.0)
    y = x * (g[:, None] if x.ndim == 2 else g)
    return np.clip(y, -c, c)


def _maxf(x, r):
    from scipy.ndimage import maximum_filter1d
    return maximum_filter1d(x, 2 * r + 1)


def trim(x, thresh_db=-70, pad=0.02):
    mono = np.abs(x).max(1) if x.ndim == 2 else np.abs(x)
    th = 10 ** (thresh_db / 20) * mono.max()
    idx = np.where(mono > th)[0]
    if len(idx) == 0:
        return x
    end = min(len(x), idx[-1] + ns(pad))
    start = max(0, idx[0] - ns(0.001))
    return x[start:end]


def normalize(x, peak_db=-1.0):
    m = np.abs(x).max()
    return x * (10 ** (peak_db / 20) / (m + 1e-12))


def loudness(x):
    import pyloudnorm as pyln
    meter = pyln.Meter(SR, block_size=min(0.4, len(x) / SR * 0.99))
    return meter.integrated_loudness(to_stereo(x))


def master(x, lufs=-16.0, peak_db=-1.0, dc=True):
    """Ajusta loudness alvo e limita pico. Retorna estereo."""
    x = to_stereo(x).astype(np.float64)
    if dc:
        x = bhp(x, 25, 2)
    try:
        L = loudness(x)
        if np.isfinite(L):
            x = x * 10 ** ((lufs - L) / 20)
    except Exception:
        x = normalize(x, -6)
    return limit(x, peak_db)


def loopify(x, xfade=2.0):
    """Faz o fim casar com o comeco (crossfade de potencia constante)."""
    x = to_stereo(x)
    k = ns(xfade)
    head = x[:k]
    tail = x[-k:]
    a = np.linspace(0, np.pi / 2, k)[:, None]
    blend = tail * np.cos(a) + head * np.sin(a)
    return np.concatenate([blend, x[k:-k]])


# ---------------------------------------------------------------- saida
def write(path, x, fmt='ogg', q=6):
    x = to_stereo(x).astype(np.float32)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if fmt == 'wav':
        sf.write(path, x, SR, subtype='PCM_16')
        return path
    tmp = path + '.tmp.wav'
    sf.write(tmp, x, SR, subtype='FLOAT')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'libvorbis',
                    '-q:a', str(q), path], check=True)
    os.remove(tmp)
    return path


# ---------------------------------------------------------------- musica
NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}


def hz(note):
    """'A4' -> 440; aceita numero MIDI."""
    if not isinstance(note, str):
        return 440.0 * 2 ** ((note - 69) / 12)
    name = note[:-1]
    octv = int(note[-1])
    m = NOTE[name] + 12 * (octv + 1)
    return 440.0 * 2 ** ((m - 69) / 12)


def midi(note):
    name = note[:-1]
    return NOTE[name] + 12 * (int(note[-1]) + 1)


def add(*xs):
    """Soma sinais de tamanhos diferentes (mono/estereo)."""
    st = any(x.ndim == 2 for x in xs)
    n = max(len(x) for x in xs)
    out = np.zeros((n, 2)) if st else np.zeros(n)
    for x in xs:
        if st:
            x = to_stereo(x)
        out[:len(x)] += _tailfade(x)
    return out


def _tailfade(x, ms=0.004):
    k = min(len(x) // 4, ns(ms))
    if k < 2:
        return x
    x = x.copy()
    r = np.linspace(1, 0, k)
    x[-k:] *= r[:, None] if x.ndim == 2 else r
    return x


def slow(dur, rate):
    """Ruido de controle suave (~N(0,1)) que varia 'rate' vezes por segundo."""
    from scipy.interpolate import CubicSpline
    k = max(4, int(dur * rate) + 4)
    pts = _RNG.standard_normal(k)
    xs = np.linspace(-1.0 / rate, dur + 1.0 / rate, k)
    return CubicSpline(xs, pts)(np.arange(ns(dur)) / SR)
