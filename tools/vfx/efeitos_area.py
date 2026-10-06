"""Skills de area do nivel 5 (design/skills-itens/skills.json, v0.6).

Cones saem em 8 direcoes (dirs=8, uma linha da folha por direcao) e em duas camadas:
<nome>_tras (o que fica atras do personagem, chao incluido) e <nome>_frente.
Direcao d: angulo no plano do chao = d*45 graus, 0 = leste (direita da tela), 2 = norte (cima).
Ponto do chao a raio r (px no eixo x da tela) e angulo phi -> tela (cx + r cos phi, cy - r/2 sin phi)."""
import math
import numpy as np
from vfx import effect, ease_out, ease_in, smooth, bell

TAU = 2 * math.pi
D2R = math.pi / 180


def G(cx, cy, r, phi, h=0.):
    return cx + r * math.cos(phi), cy - .5 * r * math.sin(phi) - h


class Parte:
    """Filtra o desenho pela camada: atras (base acima do pe na tela) ou na frente."""
    def __init__(self, parte, cy):
        self.tras = parte == 'tras'; self.cy = cy

    def __call__(self, ybase):
        return (ybase < self.cy - .5) == self.tras


# ======================================================================
# ANJO - Leque do Juizo: corte + leque de fogo branco e dourado (cone 100 graus, 3,5 tiles)
# ======================================================================
LJ_W, LJ_H, LJ_CX, LJ_CY = 272, 176, 136, 104
LJ_R = 3.5 * 34          # 119 px
LJ_HALF = 50 * D2R


def _leque_juizo(rng, parte):
    rng = np.random.default_rng(5150)      # mesma semente nas duas camadas
    # campo de chamas: aneis do raio 20 ao 116, densidade pelo comprimento do arco
    pts = []
    r = 20.
    while r < LJ_R - 2:
        n = max(2, int(r * 2 * LJ_HALF / 13))
        for k in range(n):
            psi = (-LJ_HALF + 2 * LJ_HALF * (k + rng.uniform(.15, .85)) / n)
            rr = r + rng.uniform(-3, 3)
            pts.append(dict(r=rr, psi=psi, h=rng.uniform(16, 32) * (1 - .3 * rr / LJ_R),
                            w=rng.uniform(2.4, 3.4), ph=rng.uniform(0, 1), life=rng.uniform(.3, .46),
                            lean=rng.uniform(-.12, .12), hot=rng.uniform() < .3))
        r += 12.
    pts.sort(key=lambda p: -p['r'])        # mais longe primeiro (fica atras na tela de qualquer jeito)
    feathers = [dict(r=rng.uniform(30, LJ_R - 10), psi=rng.uniform(-LJ_HALF, LJ_HALF) * .85,
                     h0=rng.uniform(6, 22), v=rng.uniform(26, 44), sw=rng.uniform(2, 5),
                     rot=rng.uniform(-.6, .6) + math.pi * rng.integers(0, 2), spin=rng.uniform(-1.5, 1.5), L=rng.uniform(10, 14),
                     dt=rng.uniform(.02, .12)) for _ in range(9)]
    sparks = [dict(r=rng.uniform(15, LJ_R), psi=rng.uniform(-LJ_HALF, LJ_HALF), v=rng.uniform(30, 60),
                   t0=rng.uniform(.18, .7), sw=rng.uniform(-6, 6)) for _ in range(34)]

    def arrive(r): return .13 + .36 * (r - 18) / (LJ_R - 18)

    def f(c, t, i, d):
        cx, cy = LJ_CX, LJ_CY
        fd = d * 45 * D2R
        P = Parte(parte, cy)

        # --- 1. corte da espada: arco alto que desce e crava no chao a frente (0 a .3) ---
        sw = t / .3
        if sw < 1.25:
            rev = ease_out(min(sw / .55, 1), 2.5); cut = ease_in(max((sw - .3) / .95, 0), 1.4)
            a0, a1 = fd + 70 * D2R, fd - 55 * D2R
            head = a0 + (a1 - a0) * rev; tail = a0 + (a1 - a0) * cut
            n = 34
            for k in range(n):
                u = k / (n - 1)
                th = tail + (head - tail) * u
                g = (th - a0) / (a1 - a0)
                hgt = 34 - 26 * g                      # desce do ombro ate perto do chao
                x, y = G(cx, cy, 38, th, hgt)
                yb = G(cx, cy, 38, th)[1]
                if not P(yb): continue
                w = 4.2 * math.sin(math.pi * min(max(g, 0), 1)) ** .7 + .6
                c.blob('sagrado', x, y, w, .75 * u ** .7 * (1 - .4 * min(sw, 1)), sy=.7)
                x2, y2 = G(cx, cy, 42, th + .06, hgt)
                c.line('faisca', x, y - 1, x2, y2 - 1, .5, 1.6 * u ** .8 * (1 - .5 * min(sw, 1)))
        # cravada: clarao no chao onde a lamina bate (acende o leque)
        fl = bell(t, .1, .34)
        if fl > 0:
            x, y = G(cx, cy, 26, fd)
            if P(y):
                c.blob('sagrado', x, y, 13 * fl, .9 * fl, sy=.5)
                c.blob('sagrado', x, y - 2, 4 * fl, 2. * fl)
                for k in range(7):
                    th = fd + (k - 3) * 16 * D2R
                    x1, y1 = G(cx, cy, 26 + 20 * fl, th)
                    c.line('faisca', x, y, x1, y1 - 3 * fl, .45, 1.4 * fl, w1=.15)

        # --- 2. frente da onda varrendo o chao ---
        if .1 < t < .6:
            rw = 18 + (LJ_R - 18) * min(max((t - .13) / .36, 0), 1)
            aw = 1 - smooth((t - .45) / .15)
            n = 26
            for k in range(n):
                psi = -LJ_HALF + 2 * LJ_HALF * k / (n - 1)
                edge = smooth((LJ_HALF - abs(psi)) / (14 * D2R) + .3)
                x, y = G(cx, cy, rw, fd + psi)
                if P(y): c.blob('sagrado', x, y, 3.2, .55 * aw * edge, sy=.5)

        # --- 3. chamas brancas e douradas nascendo do chao ---
        for p in pts:
            ta = arrive(p['r'])
            u = (t - ta) / p['life']
            x, y = G(cx, cy, p['r'], fd + p['psi'])
            if not P(y): continue
            edge = smooth((LJ_HALF - abs(p['psi'])) / (16 * D2R) + .15)
            if 0 < u < 1:
                grow = ease_out(min(u / .22, 1), 2) * (1 - ease_in(max((u - .25) / .75, 0), 1.6))
                h = p['h'] * grow * (.55 + .45 * edge)
                c.blob('sagrado', x, y, p['w'] * 2.2, .16 * grow * edge, sy=.45)
                c.flame('sagrado', x, y, p['w'] * (.6 + .4 * grow), h, ph=p['ph'] + t * 2.4,
                        a=.9 * edge, lean=p['lean'])
                if p['hot']:
                    c.flame('faisca', x, y, p['w'] * .45, h * .55, ph=p['ph'] + t * 3, a=1.1 * grow * edge)
            # brasas que ficam queimando no chao
            if u > .55:
                e = (1 - min((t - ta - .55 * p['life']) / (1 - ta), 1)) * edge
                if e > 0 and p['hot']:
                    fl2 = .7 + .3 * math.sin(t * 40 + p['ph'] * 9)
                    c.blob('brasa', x, y, 1.3, 1.1 * e * fl2, sy=.6)
                    c.blob('fogo', x, y - 1, .6, 1.5 * e * fl2)

        # --- 4. penas queimando no ar ---
        for q in feathers:
            t0 = arrive(q['r']) + q['dt']
            u = (t - t0) / (1 - t0)
            if not 0 < u < 1: continue
            gx, gy = G(cx, cy, q['r'], fd + q['psi'])
            if not P(gy): continue
            x = gx + math.sin(u * 5 + q['rot']) * q['sw']
            y = gy - q['h0'] - q['v'] * u
            burn = ease_in(u, 1.3)
            L = q['L'] * (1 - burn)
            ang = q['rot'] + q['spin'] * u
            if L > .8:
                dx, dy = math.cos(ang), math.sin(ang) * .7
                # pena: palheta larga no meio, fina nas pontas, haste clara
                mx, my = x + dx * L * .45, y + dy * L * .45
                c.line('osso', x, y, mx, my, .5, 1.4, w1=1.9, hard=True)
                c.line('osso', mx, my, x + dx * L, y + dy * L, 1.9, 1.4, w1=.6, hard=True)
                c.line('sagrado', x - dx * 2, y - dy * 2, x + dx * L * .9, y + dy * L * .9, .28, .55)
                # ponta em brasa que vai comendo a pena
                c.blob('fogo', x + dx * L, y + dy * L, 1.5, 1.5 * (1 - u * .3))
                c.blob('sagrado', x + dx * L, y + dy * L, .7, 1.6)
            else:
                k = (u - .8) / .2 if u > .8 else 0
                c.blob('faisca', x, y, .7, 1.5 * (1 - k))

        # --- 5. fagulhas subindo ---
        for s in sparks:
            u = (t - s['t0']) / .32
            if not 0 < u < 1: continue
            gx, gy = G(cx, cy, s['r'], fd + s['psi'])
            if not P(gy): continue
            c.blob('faisca', gx + s['sw'] * u, gy - 6 - s['v'] * u * (1 - .3 * u), .55, 1.6 * (1 - u))
    return f


for _parte in ('tras', 'frente'):
    effect(f'anjo_leque_juizo_{_parte}', 'anjo', (LJ_W, LJ_H), 16, fps=16, anchor=(LJ_CX, LJ_CY),
           layer='frente', dirs=8, char='anjo',
           desc=('Leque do Juízo (' + ('atrás' if _parte == 'tras' else 'frente') + ' do personagem): '
                 'corte da espada que crava no chão e abre um leque de chamas brancas e douradas '
                 '(cone de 100 graus, 3,5 tiles) com penas queimando no ar.'))(
        (lambda p: (lambda rng: _leque_juizo(rng, p)))(_parte))
