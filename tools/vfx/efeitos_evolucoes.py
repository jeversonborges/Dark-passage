"""Skills das evoluções de classe (nível 50, entregas/evolucoes/evolucoes.json)."""
import math
import numpy as np
from vfx import effect, ease_out, ease_in, bell, ballistic, lightning
from efeitos_classes import crescent, rune_circle, star, burst, motes, feather

TAU = 2 * math.pi


# ======================================================================
# CEIFADOR - sombra com olhos violeta (rampa 'espectro')
# ======================================================================

def espirito(c, x, y, ang, s, a, eyes=True):
    """Cabeça de espírito negro: crânio de fumaça, mandíbula aberta e dois olhos violeta."""
    dx, dy = math.cos(ang), math.sin(ang)
    c.blob('sombra', x, y, 4.2 * s, 1.2 * a, hard=True)
    c.blob('sombra', x - dx * 3 * s, y - dy * 3 * s + 1.5 * s, 3.4 * s, 1.0 * a, hard=True)
    c.blob('espectro', x, y, 6.5 * s, .22 * a)
    if eyes:
        px, py = -dy, dx
        for e in (-1, 1):
            c.blob('espectro', x + dx * 1.6 * s + px * 1.5 * s * e, y + dy * 1.6 * s * .6 + py * 1.5 * s * e * .6 - .8 * s,
                   .6 * s, 2.2 * a)


@effect('ceifador_espiritos_malignos', 'ceifador', (320, 208), 26, fps=16, anchor=(160, 112),
        desc='Espíritos Malignos: espíritos negros saem do Ceifador em espiral e voam para todos os lados, atravessando os inimigos.')
def _(rng):
    sp = []
    for wave, t0 in enumerate((0., .22)):
        for k in range(8):
            sp.append(dict(t0=t0 + rng.uniform(0, .05), th=TAU * (k + .5 * wave) / 8 + rng.uniform(-.12, .12),
                           spin=(1 if wave == 0 else -1) * rng.uniform(1.6, 2.2), R=rng.uniform(128, 150),
                           wob=rng.uniform(4, 8), ph=rng.uniform(0, TAU), s=rng.uniform(1.9, 2.3), dur=rng.uniform(.62, .72)))

    def pos(p, u):
        th = p['th'] + p['spin'] * u
        r = p['R'] * ease_out(u, 1.6) + p['wob'] * math.sin(u * 9 + p['ph']) * u
        return 160 + math.cos(th) * r, 112 + math.sin(th) * r * .52 - 18 * math.sin(math.pi * u) - 22 * (1 - u)

    def f(c, t, i):
        cx, cy = 160, 112
        # selo de sombra no chão
        k = bell(t, 0, .85)
        c.ring('sombra', cx, cy, 40 + 30 * ease_out(min(t / .3, 1)), 4, .9 * k, sy=.5)
        c.disc('sombra', cx, cy, 30, .55 * k, sy=.5)
        c.ring('espectro', cx, cy, 34 + 30 * ease_out(min(t / .3, 1)), .6, .7 * k, sy=.5)
        # névoa que sobe do Ceifador
        for j in range(6):
            u = (t * 1.4 + j / 6) % 1
            c.blob('fumaca', cx + math.sin(j * 2.3 + t * 5) * 10, cy - 20 - 40 * u, 6 + 8 * u, .8 * bell(u, 0, 1) * (1 - t), op='max')
        for p in sp:
            u = (t - p['t0']) / p['dur']
            if not 0 < u < 1.15: continue
            a = min(1, u * 6) * (1 - ease_in(max(u - .8, 0) / .35, 1.5))
            uu = min(u, 1)
            # rastro: fumaça que afina e se desfaz
            prev = None
            for q in range(18):
                v = uu - q * .022
                if v <= 0: break
                x, y = pos(p, v)
                w = (3.4 - q * .16) * p['s']
                c.blob('sombra', x, y, w, .85 * a * (1 - q / 18), op='max')
                if q % 3 == 1: c.blob('espectro', x, y, w * 1.5, .08 * a * (1 - q / 18))
                prev = (x, y)
            x, y = pos(p, uu); x2, y2 = pos(p, max(uu - .02, 0))
            espirito(c, x, y, math.atan2(y - y2, x - x2 + 1e-6), p['s'], a)
            if u > .97:   # ao fim do voo, se desfaz em cinza violeta
                kk = (u - .97) / .18
                for m in range(5):
                    th = m * 1.3 + p['ph']
                    c.blob('espectro', x + math.cos(th) * 8 * kk, y + math.sin(th) * 5 * kk - 6 * kk, 1.1, 1.2 * (1 - kk))
    return f


@effect('ceifador_espirito_impacto', 'ceifador', (64, 72), 10, fps=18, anchor=(32, 56),
        desc='Impacto de espírito: o espírito atravessa o alvo e arranca um fiapo de alma.')
def _(rng):
    def f(c, t, i):
        k = bell(t, 0, .6)
        c.blob('sombra', 32, 44, 12 * k, .9 * k, op='max')
        c.ring('espectro', 32, 44, 6 + 16 * ease_out(t), .7, 1.3 * (1 - t), sy=.7)
        for m in range(7):
            th = TAU * m / 7 + .4
            px, py = ballistic((32, 44), (math.cos(th) * 22, math.sin(th) * 14 - 10), t, g=0, k=2.5)
            c.blob('espectro', px, py, .9, 1.6 * (1 - t))
        u = ease_out(t)
        c.blob('sombra', 32, 44 - 30 * u, 3.5, 1.0 * (1 - t), hard=True)
        c.blob('espectro', 32, 44 - 30 * u, 5, .4 * (1 - t))
    return f


# ======================================================================
# ENGENHEIRO HEREGE - Bomba Atômica (fogo da explosão + verde do Amargo na radiação)
# ======================================================================

@effect('herege_bomba_arremesso', 'tecnomancer', (40, 40), 8, fps=16, loop=True, anchor=(20, 20),
        desc='Bomba Atômica (projétil): ogiva de latão com aletas, girando, luz verde piscando.')
def _(rng):
    def f(c, t, i):
        th = TAU * t
        dx, dy = math.cos(th), math.sin(th) * .8
        c.line('aco', 20 - dx * 9, 20 - dy * 9, 20 + dx * 9, 20 + dy * 9, 4.2, 1.4, w1=3.4, hard=True)
        c.blob('latao', 20 + dx * 8, 20 + dy * 8, 3.6, 1.2, hard=True)
        for s in (-1, 1):
            c.line('latao', 20 - dx * 9, 20 - dy * 9, 20 - dx * 13 - dy * 5 * s, 20 - dy * 13 + dx * 5 * s, .9, 1.4, hard=True)
        c.blob('amargo', 20 + dx * 2, 20 + dy * 2, 1.6, 1.8 if i % 2 == 0 else .6)
    return f


@effect('herege_bomba_explosao', 'tecnomancer', (400, 424), 40, fps=15, anchor=(200, 332),
        desc='Bomba Atômica: clarão, bola de fogo, onda de choque no chão, anel de condensação e cogumelo atômico que sobe e escurece.')
def _(rng):
    cx, gy = 200, 332
    puffs = [(rng.uniform(0, TAU), rng.uniform(.75, 1.1), rng.uniform(.8, 1.25), rng.uniform(0, 1)) for _ in range(80)]
    stem = [(rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(.7, 1.3)) for _ in range(44)]
    dust = [(rng.uniform(0, TAU), rng.uniform(.6, 1.15), rng.uniform(.7, 1.4)) for _ in range(110)]

    def f(c, t, i):
        rise = ease_out(min(t / .7, 1), 1.8)
        H = 40 + 200 * rise                         # altura do centro do chapéu
        Rc = 26 + 58 * ease_out(min(t / .8, 1), 1.5) # raio do chapéu
        heat = max(0., 1 - t / .7)                  # fogo -> fumaça
        # clarão
        if t < .14:
            k = 1 - t / .14
            c.blob('fogo', cx, gy - 30, 105 * (1 - k * .4), 1.2 * k)
            c.blob('fogo', cx, gy - 30, 40, 3 * k)
        # onda de choque no chão + poeira que corre
        wv = ease_out(min(t / .5, 1), 2)
        c.ring('fogo', cx, gy, 20 + 170 * wv, 3, 1.2 * (1 - wv), sy=.42)
        c.ring('poeira', cx, gy, 15 + 165 * wv, 7, .9 * (1 - wv * .7), sy=.42, op='max')
        for th, rr, s, in dust:
            r = (25 + 150 * rr) * ease_out(min(t / .6, 1), 2)
            c.blob('poeira', cx + math.cos(th) * r, gy + math.sin(th) * r * .42 - 6 * s * min(t * 3, 1),
                   (10 + 12 * t) * s, .95 * (1 - ease_in(t, 1.5) * .6), op='max')
        # coluna (caule)
        for ox, v, s in stem:
            y = gy - (H - Rc * .4) * v
            w = (13 + 9 * (1 - v)) * s * min(t * 4, 1)
            x = cx + ox * (6 + 10 * (1 - v))
            if heat > 0: c.blob('fogo', x, y, w * .8, .38 * heat * (1 - v * .3))
            c.blob('fumaca', x, y, w, .85 * min(t * 5, 1), op='max')
        # chapéu: anel que rola (toroide) + miolo incandescente
        cyy = gy - H
        for th, rr, s, ph in puffs:
            a = th + t * 1.2 * (1 if ph > .5 else .7)
            roll = TAU * (ph + t * .9)
            r = Rc * rr * (1 + .18 * math.cos(roll))
            x = cx + math.cos(a) * r
            y = cyy + math.sin(a) * r * .38 - math.sin(roll) * Rc * .28
            w = Rc * .42 * s
            c.blob('fumaca', x, y, w, .95, op='max')
            if heat > 0: c.blob('fogo', x, y + w * .3, w * .7, .32 * heat * (.5 + .5 * math.cos(roll)))
        if heat > 0:
            c.blob('fogo', cx, cyy + Rc * .1, Rc * .75, .55 * heat)
            c.blob('fogo', cx, cyy + Rc * .2, Rc * .3, 1.1 * heat)
        else:
            c.blob('fogo', cx, cyy + Rc * .25, Rc * .35, .25 * (1 - t))
        # saia do chapéu e anel de condensação (Wilson)
        if .12 < t < .75:
            k = bell(t, .12, .75)
            c.ring('fumaca', cx, cyy + Rc * .55, Rc * 1.35, 3.5, .7 * k, sy=.3, op='max')
            c.ring('fumaca', cx, gy - H * .45, Rc * .9 + 30 * t, 3, .55 * k, sy=.3, op='max')
        # fim: tudo se desfaz
        if t > .8:
            fade_ = (t - .8) / .2
            c.blob('fumaca', cx, cyy, Rc * 1.3, .4 * fade_, op='max')
    return f


@effect('herege_radiacao', 'tecnomancer', (288, 160), 24, fps=10, loop=True, layer='chao', anchor=(144, 80),
        desc='Zona radioativa da Bomba Atômica: chão queimado, brilho verde do Amargo e poeira radioativa subindo (repetir enquanto durar).')
def _(rng):
    mt = [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(.6, 1.3)) for _ in range(60)]
    pocas = [(x, y, ph, s) for x, y, ph, s in [(rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 1), rng.uniform(.6, 1.5)) for _ in range(40)] if x * x + y * y < .8]
    def f(c, t, i):
        cx, cy = 144, 80
        c.disc('sombra', cx, cy, 128, .55, sy=.5, edge=.5)
        pul = .8 + .2 * math.sin(TAU * t)
        c.ring('amargo', cx, cy, 120, 4, .35 * pul, sy=.5, jag=lambda th: 1 + .06 * np.sin(th * 5 + 2 * np.sin(th * 3)) + .03 * np.sin(th * 13 + TAU * t))
        c.disc('amargo', cx, cy, 112, .12 * pul, sy=.5, edge=.7)
        for x, y, ph, s in pocas:
            k = .6 + .4 * math.sin(TAU * (t + ph))
            c.blob('amargo', cx + x * 100, cy + y * 48, 9 * s, .3 * k, sy=.5)
            c.blob('amargo', cx + x * 100, cy + y * 48, 2.5 * s, .9 * k, sy=.5)
        for x, y, ph, s in mt:
            u = (t * s + ph) % 1
            r = math.hypot(x, y)
            if r > 1: continue
            c.blob('amargo' if s > 1 else 'po_amargo', cx + x * 118, cy + y * 58 - 50 * u, 1.3 * s, 1.4 * bell(u, 0, 1),
                   op='add' if s > 1 else 'max')
    return f


# ======================================================================
# SKILLS DE NÍVEL 65 (uma rampa emissiva por efeito, a da classe)
# ======================================================================

def espada_caindo(c, x, gy, u, L=70, ramp='sagrado'):
    """Montante de fogo sagrado caindo do céu e cravando no chão em (x, gy); u de 0 (alto) a 1 (cravada)."""
    y = gy - 160 * (1 - ease_in(min(u, 1), 2.2))
    a = 1 if u < 1.4 else max(0, 1 - (u - 1.4) / .5)
    c.line('aco', x, y - L, x, y, 4.2, 1.3 * a, w1=.8, hard=True)
    c.line(ramp, x, y - L, x, y, 2.4, 1.2 * a)
    c.line(ramp, x, y - L, x, y, 8, .25 * a)
    c.line('latao', x - 9, y - L + 10, x + 9, y - L + 10, 1.4, 1.4 * a, hard=True)
    c.line('latao', x, y - L + 10, x, y - L - 6, 1.6, 1.4 * a, hard=True)
    if u < 1: c.line(ramp, x, y - L - 40, x, y - L, 2.5, .5 * u, w1=.5)
    else:
        k = min((u - 1) / .4, 1)
        c.ring(ramp, x, gy, 6 + 22 * ease_out(k), 1.2, 1.4 * (1 - k), sy=.5)
        c.blob(ramp, x, gy, 10 * (1 - k), 1.4 * (1 - k))
        burst(c, ramp, x, gy - 4, k, 8, 26, int(x), a=1.5, g=40, up=30)


@effect('arcanjo_sete_espadas', 'anjo', (256, 240), 36, fps=16, anchor=(128, 168),
        desc='Sete Espadas do Juízo: sete montantes de fogo sagrado caem do céu em círculo e o último crava no centro.')
def _(rng):
    pos = [(128 + math.cos(TAU * k / 6 - 1.2) * 74, 168 + math.sin(TAU * k / 6 - 1.2) * 36) for k in range(6)] + [(128, 168)]
    def f(c, t, i):
        rune_circle(c, 'sagrado', 128, 168, 92, t, a=.8 * bell(t, 0, 1), n=14, seed=7)
        for k, (x, y) in enumerate(pos):
            t0 = .06 * k + (.08 if k == 6 else 0); u = (t - t0) / .2
            if u > 0: espada_caindo(c, x, y, u, L=88 if k == 6 else 66)
        if t > .55:
            k = (t - .55) / .45
            c.ring('sagrado', 128, 168, 30 + 90 * ease_out(k), 2, 1.3 * (1 - k), sy=.5)
            motes(c, 'sagrado', 128, 168, k, 24, 80, 70, 5)
    return f


@effect('serafim_coro', 'anjo', (288, 256), 32, fps=14, anchor=(144, 200),
        desc='Coro dos Seis Ais: seis asas de luz se abrem atrás do Serafim, colunas de luz ressuscitam os aliados e uma redoma protege o grupo.')
def _(rng):
    def f(c, t, i):
        cx, gy = 144, 200
        op = ease_out(min(t / .35, 1), 2); k = bell(t, 0, 1)
        for side in (-1, 1):
            for j, (ang, L) in enumerate(((-.9, 110), (-.35, 125), (.2, 100))):
                for q in range(9):
                    a_ = ang * op - .25 + q * .06 * op
                    feather(c, cx + side * 6, gy - 70, math.pi / 2 + side * (math.pi / 2 + a_) + math.pi, L * op * (.6 + .05 * q), a=.9 * k)
                c.line('sagrado', cx, gy - 70, cx + side * math.cos(ang * op) * L * op, gy - 70 + math.sin(ang * op) * L * op, 3, .5 * k, w1=.5)
        for x in (60, 228, 100, 190):
            if t > .3:
                u = (t - .3) / .5
                c.line('sagrado', x, 0, x, gy - 10 + (x % 3) * 8, 7 * bell(u, 0, 1), .8 * bell(u, 0, 1))
                c.ring('sagrado', x, gy - 10 + (x % 3) * 8, 14, 1.2, 1.2 * bell(u, 0, 1), sy=.5)
        c.ring('sagrado', cx, gy, 120 * op, 2.2, 1.0 * k, sy=.5)
        c.ring('sagrado', cx, gy - 40, 118 * op, 1.2, .5 * k, sy=.95, ang=(math.pi, TAU))
        c.blob('sagrado', cx, gy - 70, 14, 1.6 * k)
        motes(c, 'sagrado', cx, gy, t, 30, 110, 140, 9, loop=True)
    return f


@effect('lorde_trono', 'demonio', (192, 208), 28, fps=12, anchor=(96, 168),
        desc='Trono da Legião: um trono de ossos e lâminas sobe do chão em brasa; correntes de provocação puxam os inimigos ao redor.')
def _(rng):
    def f(c, t, i):
        cx, gy = 96, 168
        up = ease_out(min(t / .4, 1), 2); k = bell(t, 0, 1.05)
        c.disc('abismo', cx, gy, 70, .35 * k, sy=.5, edge=20)
        star(c, 'brasa', cx, gy, 66, 5, a=1.2 * k, rot=t * .3)
        c.ring('brasa', cx, gy, 66, 1.4, 1.2 * k, sy=.5)
        h = 120 * up
        for s_ in (-1, 1):   # espaldar de ossos e lâminas
            for q in range(4):
                x = cx + s_ * (10 + q * 11); hh = h * (1 - q * .16)
                c.line('osso', x, gy - 10, x + s_ * q * 3, gy - 10 - hh, 3 - q * .4, 1.4, w1=.8, hard=True)
        c.line('osso', cx, gy - 10, cx, gy - 10 - h * 1.1, 3.5, 1.4, w1=1, hard=True)
        c.disc('pedra', cx, gy - 18, 26 * up, 1.4, sy=.5, edge=.5)
        c.blob('osso', cx, gy - 10 - h * 1.1, 6 * up, 1.4, hard=True)
        for s_ in (-1, 1): c.blob('brasa', cx + s_ * 2.5, gy - 12 - h * 1.08, 1.2 * up, 2.2)
        for q in range(8):   # correntes de provocação
            a_ = TAU * q / 8 + .3; r = 90 * (1 - ease_in(max(t - .3, 0) / .7, 1.5))
            x1, y1 = cx + math.cos(a_) * r, gy + math.sin(a_) * r * .5
            if t > .25: c.line('latao', cx, gy - 30, x1, y1, .6, 1.0 * k, hard=True); c.blob('brasa', x1, y1, 2.5, 1.2 * k)
        for q in range(14):
            u = (t * 1.5 + q / 14) % 1
            c.flame('fogo', cx + math.sin(q * 2.1) * 60, gy + math.cos(q * 1.7) * 26, 3, 16 * bell(u, 0, 1), ph=u, a=.7 * k)
    return f


@effect('arquimago_meteoros', 'cultista', (320, 320), 40, fps=16, anchor=(160, 250),
        desc='Chuva de Estrelas Rubras: o céu se rasga e catorze estrelas de sangue caem em diagonal, explodindo e deixando o chão em brasa.')
def _(rng):
    mt = [(rng.uniform(40, 280), 250 + rng.uniform(-40, 40) * .6, rng.uniform(0, .6), rng.uniform(.8, 1.3)) for _ in range(14)]
    def f(c, t, i):
        k = bell(t, 0, 1.05)
        c.ring('rubro', 160, 250, 130, 1.6, .8 * k, sy=.45)
        rune_circle(c, 'rubro', 160, 250, 120, t, a=.6 * k, sy=.45, n=12, seed=3, rings=False)
        for q in range(5): c.blob('rubro', 70 + q * 45, 14 + 6 * math.sin(q * 1.7), 18, .3 * k * bell(t, 0, .7))
        for x, y, t0, s in mt:
            u = (t - t0) / .22
            if u <= 0: continue
            if u < 1:
                px, py = x + 70 * (1 - u), y - 260 * (1 - ease_in(u, 1.6))
                c.line('rubro', px + 22, py - 80, px, py, 5 * s, .25, w1=1.5 * s, a1=1.2)
                c.blob('rubro', px, py, 5 * s, 1.8)
                c.blob('cinza', px, py, 3 * s, 1.2, hard=True)
            else:
                v = min((u - 1) / 1.6, 1)
                c.blob('rubro', x, y - 6, 22 * s * (1 - v * .5), 1.6 * (1 - v))
                c.ring('rubro', x, y, 8 + 28 * ease_out(v) * s, 1.5, 1.4 * (1 - v), sy=.5)
                burst(c, 'rubro', x, y - 4, v, 10, 40 * s, int(x), g=60, up=40)
                c.blob('fumaca', x, y - 20 - 30 * v, 10 + 14 * v, .8 * (1 - v), op='max')
                c.disc('rubro', x, y, 10 * s, .5 * (1 - v * .6), sy=.5, edge=4)
    return f


@effect('profeta_enxame', 'cultista', (96, 112), 24, fps=14, loop=True, anchor=(48, 96),
        desc='Enxame da Podridão: nuvem de moscas e mariposas podres girando em volta do alvo, pingando podridão verde (repetir enquanto durar).')
def _(rng):
    fl = [(rng.uniform(0, TAU), rng.uniform(10, 34), rng.uniform(20, 86), rng.uniform(.6, 1.4), rng.integers(1, 3)) for _ in range(70)]
    def f(c, t, i):
        for a0, r, h, sp, d in fl:
            a_ = a0 + TAU * t * sp * d
            x = 48 + math.cos(a_) * r; y = 96 - h + math.sin(a_) * r * .35 + math.sin(TAU * t * 3 + a0) * 3
            if sp > 1.25:   # mariposa
                fl_ = 2.2 * (1 if (i + int(a0 * 3)) % 2 else .4)
                c.blob('praga', x - fl_, y, 1.4, 1.3, hard=True); c.blob('praga', x + fl_, y, 1.4, 1.3, hard=True)
            else:
                c.blob('cinza', x, y, .7, 1.4, hard=True)
        c.blob('amargo', 48, 60, 30, .25)
        for q in range(4):
            u = (t + q / 4) % 1
            c.blob('amargo', 40 + q * 6, 56 + 40 * ease_in(u), 1.4, 1.3 * (1 - u))
        c.ring('amargo', 48, 96, 22, 1, .5, sy=.4)
    return f


@effect('pistoleiro_forma_vingativa', 'humano', (128, 160), 24, fps=14, anchor=(64, 140), char='humano',
        desc='Forma Vingativa: explosão de pólvora e brasa sobe do chão, o sobretudo pega fogo e os olhos do Vingador acendem (início da transformação).')
def _(rng):
    def f(c, t, i):
        cx, gy = 64, 140
        k = bell(t, 0, 1)
        c.ring('fogo', cx, gy, 10 + 50 * ease_out(min(t / .4, 1)), 2, 1.3 * (1 - t), sy=.45)
        for q in range(16):
            u = (t * 1.6 + q / 16) % 1
            x = cx + math.sin(q * 2.4) * (14 + 6 * u)
            c.flame('fogo', x, gy - 4 - q % 4 * 6, 3.4, (40 + q % 5 * 10) * bell(u, 0, 1) * k, ph=u + q, a=.9)
        burst(c, 'faisca', cx, gy - 40, t, 26, 60, 4, g=50, up=20)
        for s_ in (-1, 1):
            c.blob('fogo', cx + s_ * 3.5, gy - 92, 1.3, 2.4 * k)
            c.line('fogo', cx + s_ * 3.5, gy - 92, cx + s_ * 12, gy - 96, .7, 1.2 * k, a1=0)
        c.blob('fumaca', cx, gy - 70 - 30 * t, 18 + 10 * t, .7 * k, op='max')
    return f


@effect('pistoleiro_vingador_aura', 'humano', (80, 120), 16, fps=14, loop=True, anchor=(40, 112), char='humano',
        desc='Aura do Vingador: brasas no sobretudo e faíscas na espingarda enquanto a Forma Vingativa dura (repetir).')
def _(rng):
    def f(c, t, i):
        for q in range(10):
            u = (t * 2 + q / 10) % 1
            c.flame('fogo', 40 + math.sin(q * 2.7) * 13, 108 - q % 3 * 18, 2.2, 14 * bell(u, 0, 1), ph=u + q, a=.7)
        motes(c, 'faisca', 40, 108, t, 14, 18, 90, 2, loop=True)
        c.ring('fogo', 40, 112, 18, .8, .7 + .3 * math.sin(TAU * t), sy=.35)
    return f


@effect('cacador_chuva_virotes', 'humano', (256, 256), 30, fps=16, anchor=(128, 200),
        desc='Chuva de Virotes Benzidos: quarenta virotes caem em diagonal sobre a área, cravam no chão com respingos de água benta.')
def _(rng):
    vt = [(rng.uniform(-100, 100), rng.uniform(-46, 46), rng.uniform(0, .5)) for _ in range(40)]
    vt = [(x, y, t0) for x, y, t0 in vt if (x / 100) ** 2 + (y / 46) ** 2 < 1]
    def f(c, t, i):
        cx, gy = 128, 200
        c.ring('arco', cx, gy, 104, 1.2, .7 * bell(t, 0, 1), sy=.45)
        for x, y, t0 in vt:
            u = (t - t0) / .16; X, Y = cx + x, gy + y
            if u <= 0: continue
            if u < 1:
                px, py = X - 40 * (1 - u), Y - 180 * (1 - u)
                c.line('aco', px - 7, py - 30, px, py, 1.2, 1.4, hard=True)
                c.line('arco', px - 12, py - 52, px, py, 2.2, .45, w1=.8, a1=1.2)
            else:
                v = min((u - 1) / 2.5, 1); a_ = 1 if u < 3 else max(0, 1 - (u - 3) / 1.5)
                c.line('aco', X - 3, Y - 13, X, Y, 1.2, 1.4 * a_, hard=True)
                c.blob('arco', X, Y, 3, .5 * a_)
                c.line('pedra', X - 4, Y - 15, X - 3, Y - 13, 1.2, 1.4 * a_, hard=True)
                if v < 1: burst(c, 'arco', X, Y, v, 5, 14, int(X * 7), g=40, up=12, s=.5)
    return f


@effect('gladiador_arena', 'mutante', (288, 208), 30, fps=12, anchor=(144, 136),
        desc='Ave, Arena!: grades de ferro sobem do chão em círculo, tochas de ácido acendem e uma onda de poeira marca a arena.')
def _(rng):
    N = 22
    def f(c, t, i):
        cx, gy = 144, 136
        up = ease_out(min(t / .45, 1), 2.5); k = 1 - ease_in(max(t - .85, 0) / .15, 1)
        c.ring('poeira', cx, gy, 112 + 20 * up, 8, .8 * (1 - up), sy=.5, op='max')
        pts = [(cx + math.cos(TAU * q / N) * 112, gy + math.sin(TAU * q / N) * 56) for q in range(N)]
        for q, (x, y) in enumerate(sorted(pts, key=lambda p: p[1])):
            h = 46 * up * (.8 + .2 * math.sin(q * 3.1))
            c.line('aco', x, y, x, y - h, 1.4, 1.4 * k, hard=True)
            c.blob('aco', x, y - h - 2, 2, 1.4 * k, hard=True)
            if q % 4 == 0 and up > .6:
                c.flame('acido', x, y - h - 2, 3, 12 * (.8 + .2 * math.sin(TAU * t * 3 + q)), ph=t * 3 + q, a=1.1 * k)
        for z in (.35, .75):
            pp = [(cx + math.cos(TAU * q / 60) * 112, gy + math.sin(TAU * q / 60) * 56 - 46 * up * z) for q in range(61)]
            c.poly('aco', pp, .8, 1.3 * k * min(up * 2, 1), hard=True)
    return f


@effect('abominacao_forma_colossal', 'mutante', (224, 240), 28, fps=14, anchor=(112, 200), char='mutante',
        desc='Forma Colossal: a carne explode em sangue e ácido, tentáculos rompem o chão e uma onda de choque marca a transformação.')
def _(rng):
    tn = [(rng.uniform(0, TAU), rng.uniform(40, 80), rng.uniform(40, 110), rng.uniform(0, .3)) for _ in range(10)]
    def f(c, t, i):
        cx, gy = 112, 200
        c.ring('acido', cx, gy, 20 + 90 * ease_out(min(t / .5, 1)), 2, 1.2 * (1 - t), sy=.45)
        c.ring('poeira', cx, gy, 15 + 85 * ease_out(min(t / .6, 1)), 8, .9 * (1 - t), sy=.45, op='max')
        burst(c, 'acido', cx, gy - 70, min(t / .6, 1), 30, 90, 8, g=120, up=40)
        if t < .5: burst(c, 'sangue', cx, gy - 70, t / .5, 24, 80, 9, a=1.4, g=140, up=50, s=1.1)
        for a0, r, h, t0 in tn:
            u = (t - t0) / .5
            if u <= 0: continue
            x0, y0 = cx + math.cos(a0) * r, gy + math.sin(a0) * r * .45
            hh = h * ease_out(min(u, 1), 2) * (1 - ease_in(max(u - 1.1, 0), 1))
            pts = [(x0 + math.sin(q * .5 + a0 + t * 6) * 6 * q / 8, y0 - hh * q / 8) for q in range(9)]
            c.poly('carne', pts, 8, 1.4, w1=1.2, hard=True)
            c.poly('praga', pts[1:], 3, 1.2, w1=.6, hard=True)
            c.blob('acido', *pts[-1], 2, 1.6 * min(u, 1))
        c.blob('acido', cx, gy - 70, 30 * bell(t, 0, .4), 1.2 * bell(t, 0, .4))
    return f


@effect('mechanicus_legiao', 'tecnomancer', (256, 224), 32, fps=14, anchor=(128, 176),
        desc='Legião de Servos: engrenagem de runas gira no chão e quatro crânios-servos de latão sobem em espiral, ligados por arcos de sobrecarga.')
def _(rng):
    def f(c, t, i):
        cx, gy = 128, 176
        k = bell(t, 0, 1.05); sp = ease_out(min(t / .5, 1), 2)
        for q in range(16):
            a_ = TAU * q / 16 + t * 2
            c.line('runa', cx + math.cos(a_) * 70, gy + math.sin(a_) * 35, cx + math.cos(a_) * 82, gy + math.sin(a_) * 41, 2.2, 1.2 * k)
        c.ring('runa', cx, gy, 70, 1.6, 1.2 * k, sy=.5)
        rune_circle(c, 'runa', cx, gy, 52, t, a=.8 * k, n=8, spin=-2, seed=11)
        heads = []
        for q in range(4):
            a_ = TAU * q / 4 + t * 3
            x = cx + math.cos(a_) * 60 * sp; y = gy - 40 - 70 * sp + math.sin(a_) * 22 * sp + math.sin(TAU * t * 2 + q) * 4
            heads.append((x, y))
            c.blob('latao', x, y, 10, 1.4, hard=True)
            c.blob('osso', x, y + 3, 7, 1.4, hard=True)
            for s_ in (-1, 1): c.blob('runa', x + s_ * 3, y + 2, 1.5, 2.4)
            c.line('latao', x - 13, y - 3, x + 13, y - 3, 1.2, 1.4, hard=True)
            c.flame('runa', x, y + 9, 2.2, -9, ph=t * 4 + q, a=.9)
        if t > .4:
            for q in range(4):
                (x0, y0), (x1, y1) = heads[q], heads[(q + 1) % 4]
                if (i + q) % 3 == 0: c.poly('eletrico', lightning(rng, x0, y0, x1, y1, .3, 4), .5, 1.4)
    return f
