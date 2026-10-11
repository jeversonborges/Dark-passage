# Animações por quadro de sprite: parado (4), andar (8) e atacar (8).
import math
from rig import ARMS_DOWN, merge, make_action

LEG_LEN = .84

def walk_legs(t, amp=26):
    s, c = math.sin(t), math.cos(t)
    th = amp*s
    p = {"thigh.L": {"x": -th}, "thigh.R": {"x": th},
         "shin.L": {"bend": 6 + 48*max(0, c)**1.4}, "shin.R": {"bend": 6 + 48*max(0, -c)**1.4},
         "foot.L": {"x": .3*th - 10*max(0, c)}, "foot.R": {"x": -.3*th - 10*max(0, -c)},
         "hips": {"z": 6*s}, "spine": {"x": -4}, "chest": {"z": -9*s}}
    drop = LEG_LEN*(1 - math.cos(math.radians(amp*abs(s)))) + .012*abs(c)
    p["root"] = (0, 0, -drop)
    return p

def anjo_anims(arm, extra=None):
    """Golpe corpo a corpo com arma de uma mão (Anjo, Demônio, Mutante)."""
    base = merge(ARMS_DOWN, {"forearm.R": {"bend": -8}, "upper_arm.R": {"x": 4, "y": -6}, "hand.R": {"bend": 32},
                             "wing.L": {"z": 12}, "wing.R": {"z": -12}})
    idle = []
    for i in range(4):
        b = math.sin(i/4*2*math.pi)
        idle.append(merge(base, {"chest": {"x": -1.5*b}, "head": {"x": 1.5*b}, "wing.L": {"y": -3*b}, "wing.R": {"y": 3*b},
                                 "upper_arm.L": {"y": -2*b}, "root": (0, 0, -.006*(1+b))}))
    # andar em 12 quadros: passada mais longa, quadril que balança e inclina, tronco em contra-rotação,
    # braço que balança com atraso no antebraço e asas que acompanham o sobe e desce com atraso
    walk = []
    for i in range(12):
        t = i/12*2*math.pi; s, c = math.sin(t), math.cos(t)
        lag = math.sin(t - .9); bob = math.cos(2*t)
        walk.append(merge(base, walk_legs(t, 30), {
            "hips": {"z": 4*s, "y": 4*c}, "spine": {"x": -5, "y": -2*c}, "chest": {"z": -6*s, "x": -1.5*bob},
            "neck": {"z": 3*s}, "head": {"z": 5*s, "x": 2*bob, "y": 1.5*c},
            "upper_arm.L": {"x": 30*s, "y": -3*abs(s)}, "forearm.L": {"bend": -14 - 20*max(0, -lag)},
            "upper_arm.R": {"x": -12*s, "y": 3*abs(s)}, "forearm.R": {"bend": -6 - 8*max(0, lag)}, "hand.R": {"bend": 6*lag},
            "wing.L": {"y": -9*math.cos(2*t - .8), "z": 3*s}, "wing.R": {"y": 9*math.cos(2*t - .8), "z": 3*s}}))
    # ataque em 12 quadros com curvas suaves: antecipação (recolhe, agacha, abre as asas), segura no alto,
    # golpe rápido em diagonal com avanço, passa do ponto (follow-through) e assenta de volta
    KEYS = [  # (tempo, braço dir x, z, antebraço, tronco z, coluna x, asas, avanço, agacha)
        (0.00, -30, 0, -55, -8, 0, 0, 0, 0),
        (0.16, -110, 22, -85, -26, 5, 22, -.15, .05),
        (0.30, -180, 18, -100, -40, 8, 42, -.2, .06),
        (0.36, -170, 14, -95, -38, 7, 44, -.15, .05),
        (0.44, -110, -10, -30, 0, -6, 34, .5, .02),
        (0.50, -45, -38, -4, 34, -16, 26, 1, .06),
        (0.58, -12, -52, -2, 46, -20, 16, 1.08, .08),
        (0.70, -16, -38, -12, 34, -13, 10, .9, .06),
        (0.84, -18, -14, -26, 12, -5, 4, .4, .03),
        (1.00, -30, 0, -55, -8, 0, 0, 0, 0),
    ]
    def sample(t):
        for (t0, *a), (t1, *b) in zip(KEYS, KEYS[1:]):
            if t <= t1:
                u = (t - t0)/(t1 - t0); u = u*u*(3 - 2*u)
                return [x + (y - x)*u for x, y in zip(a, b)]
        return KEYS[-1][1:]
    attack = []
    for i in range(12):
        ax, az, fb, cz, sx, wg, lg, cr = sample(i/12)
        attack.append(merge(ARMS_DOWN, {
            "upper_arm.R": {"y": 34, "x": ax, "z": az}, "forearm.R": {"bend": fb}, "hand.R": {"bend": -.15*fb},
            "upper_arm.L": {"x": -15*lg + 10*cr, "y": -10*max(lg, 0) - 60*cr}, "forearm.L": {"bend": -30*max(lg, 0) - 200*cr},
            "chest": {"z": cz}, "spine": {"x": sx, "z": cz*.4}, "head": {"z": -cz*.5, "x": -sx*.3},
            "wing.L": {"z": 12 - wg, "y": -wg*.6}, "wing.R": {"z": -12 + wg, "y": wg*.6},
            "thigh.L": {"x": -28*lg - 120*cr}, "shin.L": {"bend": 25*lg + 300*cr}, "foot.L": {"x": 10*lg},
            "thigh.R": {"x": 18*lg - 100*cr}, "shin.R": {"bend": 12*lg + 260*cr}, "foot.R": {"x": 0},
            "root": (0, -.07*lg, -.06*max(lg, 0) - cr)}))
    if extra:
        idle, walk, attack = ([merge(f, extra) for f in L_] for L_ in (idle, walk, attack))
    return {"idle": make_action(arm, "idle", idle), "walk": make_action(arm, "walk", walk),
            "attack": make_action(arm, "attack", attack)}

def caster_anims(arm, extra=None, hold_extra=None):
    """Conjurador com cajado/incensário na mão direita: ergue, lança a magia (efeito) e volta."""
    hold = merge(ARMS_DOWN, {"upper_arm.R": {"x": -12, "y": -4}, "forearm.R": {"bend": -62}}, hold_extra or {})
    idle = []
    for i in range(4):
        b = math.sin(i/4*2*math.pi)
        idle.append(merge(hold, {"chest": {"x": -1.5*b}, "head": {"x": 1.5*b}, "root": (0, 0, -.006*(1+b)),
                                 "upper_arm.L": {"x": -3*b}}))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s = math.sin(t)
        walk.append(merge(hold, walk_legs(t, 22), {"upper_arm.L": {"x": 18*s}, "upper_arm.R": {"x": -5*s},
                                                   "head": {"z": 3*s}}))
    K = [  # (braço dir x, antebraço, braço esq x, tronco x, tronco z, efeito)
        (-25, -60, -10, 0, -6, 0),
        (-60, -55, -30, 3, -14, 0),
        (-100, -40, -55, 6, -18, 0),
        (-80, -12, -75, -8, 4, 1),
        (-78, -10, -78, -10, 8, 1),
        (-60, -25, -50, -6, 4, 0),
        (-35, -45, -25, -2, 0, 0),
        (-14, -60, -5, 0, 0, 0),
    ]
    attack = []
    for ux, fb, lx, cx, cz, fx in K:
        attack.append(merge(ARMS_DOWN, {"upper_arm.R": {"x": ux, "y": -4}, "forearm.R": {"bend": fb},
                                        "upper_arm.L": {"x": lx, "y": -10}, "forearm.L": {"bend": -15},
                                        "chest": {"x": cx, "z": cz}, "spine": {"x": cx*.5, "z": cz*.4}, "head": {"z": -cz*.6},
                                        "thigh.L": {"x": -16*fx}, "shin.L": {"bend": 14*fx}, "thigh.R": {"x": 10*fx},
                                        "root": (0, -.03*fx, -.02*fx)}))
    if extra:
        idle, walk, attack = ([merge(f, extra) for f in L_] for L_ in (idle, walk, attack))
    acts = {"idle": make_action(arm, "idle", idle), "walk": make_action(arm, "walk", walk),
            "attack": make_action(arm, "attack", attack)}
    return acts, [k[5] for k in K]

def humano_anims(arm, flash):
    # escopeta baixa, cruzando o corpo; mão esquerda segue a telha por IK
    def gun(ux, uz, fb, hz):
        return {"upper_arm.R": {"y": -30, "x": ux, "z": uz}, "forearm.R": {"bend": fb}, "hand.R": {"z": hz},
                "upper_arm.L": {"y": 30}}
    hold = gun(20, 20, -100, -10)
    idle = []
    for i in range(4):
        b = math.sin(i/4*2*math.pi)
        idle.append(merge(hold, {"chest": {"x": -1.5*b}, "head": {"x": 1.5*b, "z": 3}, "root": (0, 0, -.006*(1+b)),
                                 "forearm.R": {"bend": 2*b}}))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s = math.sin(t)
        walk.append(merge(hold, walk_legs(t, 24), {"forearm.R": {"bend": 3*math.cos(2*t)}, "head": {"z": 3*s}}))
    # ataque: ergue a arma na altura do peito, dispara (clarão + coice) e volta
    K = [  # (braço x, braço z, antebraço, mão z, tronco x, tronco z, recuo, clarão)
        (20, 20, -100, -10, 0, -4, 0, 0),
        (20, 10, -112, -15, -2, -10, 0, 0),
        (20, 0, -120, -20, -3, -14, 0, 0),
        (26, 0, -132, -20, 9, -14, 1, 1),
        (24, 0, -127, -20, 6, -14, .6, 0),
        (21, 0, -121, -20, 2, -13, .2, 0),
        (20, 10, -110, -15, 0, -8, 0, 0),
        (20, 20, -100, -10, 0, -3, 0, 0),
    ]
    attack = []
    for ux, uz, fb, hz, cx, cz, rc, fl in K:
        attack.append(merge(gun(ux, uz, fb, hz), {"chest": {"x": cx, "z": cz}, "spine": {"z": cz*.5},
                             "head": {"z": -cz*.7, "x": cx*.4},
                             "thigh.L": {"x": -14}, "shin.L": {"bend": 12}, "thigh.R": {"x": 10}, "shin.R": {"bend": 8},
                             "root": (0, .03*rc, -.02 - .01*rc)}))
    acts = {"idle": make_action(arm, "idle", idle), "walk": make_action(arm, "walk", walk),
            "attack": make_action(arm, "attack", attack)}
    return acts, [k[7] for k in K]

def humano_dual_anims(arm):
    """Humano: espada larga na direita (ataque corpo a corpo) e escopeta serrada na esquerda (tiro)."""
    acts = anjo_anims(arm)
    base = merge(ARMS_DOWN, {"forearm.R": {"bend": -8}, "upper_arm.R": {"x": 4, "y": -6}})
    K = [  # (braço esq x, antebraço esq, tronco x, tronco z, recuo, clarão)
        (-20, -30, 0, -4, 0, 0),
        (-60, -20, 0, -10, 0, 0),
        (-86, -4, -2, -16, 0, 0),
        (-98, -4, 7, -16, 1, 1),
        (-94, -7, 5, -15, .6, 0),
        (-86, -5, 2, -15, .2, 0),
        (-50, -22, 0, -9, 0, 0),
        (-15, -25, 0, -3, 0, 0),
    ]
    shoot = []
    for lx, lb, cx, cz, rc, fl in K:
        shoot.append(merge(base, {"upper_arm.L": {"x": lx}, "forearm.L": {"bend": lb}, "chest": {"x": cx, "z": cz},
                                  "spine": {"z": cz*.5}, "head": {"z": -cz*.7, "x": cx*.4},
                                  "thigh.L": {"x": -12}, "shin.L": {"bend": 10}, "thigh.R": {"x": 10}, "shin.R": {"bend": 8},
                                  "root": (0, .03*rc, -.02 - .01*rc)}))
    acts["shoot"] = make_action(arm, "shoot", shoot)
    # skill de giro: braços abertos, espada na horizontal, o corpo dá uma volta completa
    spin = []
    for i in range(8):
        t = i/8
        crouch = .05 + .03*math.sin(t*2*math.pi)
        spin.append({"hips": {"z": 45*i}, "spine": {"x": -8}, "chest": {"z": 10},
                     "upper_arm.R": {"y": 36, "x": -10}, "forearm.R": {"bend": -30}, "hand.R": {"bend": 55},
                     "upper_arm.L": {"y": -30, "x": 10}, "forearm.L": {"bend": -20},
                     "thigh.L": {"x": -18, "y": 8}, "shin.L": {"bend": 30}, "thigh.R": {"x": 12, "y": -8}, "shin.R": {"bend": 24},
                     "head": {"z": -8}, "root": (0, 0, -crouch)})
    acts["spin"] = make_action(arm, "spin", spin)
    # dash com espada (12 quadros): agacha, dispara para frente com a lâmina para trás e corta na horizontal
    D = [  # (incl., coxa E, joelho E, coxa D, joelho D, braço D z, braço D y, antebraço D, tronco z, braço E x, altura)
        (-6, -10, 30, 10, 30, -20, 0, -20, -10, -10, -.08),
        (-14, -18, 50, 18, 50, -40, 10, -15, -20, -15, -.13),
        (-30, -45, 30, 40, 10, -55, 25, -5, -28, -30, -.05),
        (-34, -55, 20, 48, 25, -60, 30, -5, -30, -35, -.02),
        (-34, -50, 45, 35, 60, -55, 32, -5, -28, -30, -.03),
        (-28, -42, 55, 25, 45, -10, 36, -5, -5, -20, -.07),
        (-24, -40, 55, 20, 40, 45, 36, -5, 25, -10, -.09),
        (-20, -38, 50, 18, 35, 90, 34, -10, 40, 0, -.1),
        (-16, -34, 45, 15, 30, 105, 30, -20, 42, 5, -.1),
        (-12, -25, 35, 12, 25, 80, 20, -30, 30, 0, -.08),
        (-8, -15, 25, 8, 15, 40, 8, -25, 15, -5, -.05),
        (-4, -6, 10, 4, 8, 10, 0, -15, 4, -5, -.02),
    ]
    dash = []
    for lean, tl, kl, tr_, kr, az, ay, fb, cz, al, h in D:
        dash.append(merge(ARMS_DOWN, {"spine": {"x": lean*.6, "z": cz*.4}, "chest": {"x": lean*.4, "z": cz*.6}, "head": {"x": -lean*.6, "z": -cz*.6},
                                      "thigh.L": {"x": tl}, "shin.L": {"bend": kl}, "thigh.R": {"x": tr_}, "shin.R": {"bend": kr},
                                      "foot.L": {"x": 10}, "foot.R": {"x": -15},
                                      "upper_arm.R": {"y": ay, "z": az}, "forearm.R": {"bend": fb}, "hand.R": {"bend": 45},
                                      "upper_arm.L": {"x": al}, "forearm.L": {"bend": -40},
                                      "root": (0, 0, h)}))
    acts["dash"] = make_action(arm, "dash", dash)
    return acts, {"shoot": [k[5] for k in K]}

FLY_H = .3   # altura do voo (m); a sombra fica no chão, no ponto da âncora

def _beat(p, down=.4):
    """Batida de asa com ritmo de verdade: descida rápida (força) e subida lenta. p em voltas (0..1).
    Devolve (posição -1..1 com 1 = no alto, velocidade da descida 0..1)."""
    p %= 1
    if p < down: return math.cos(math.pi*p/down), math.sin(math.pi*p/down)
    return math.cos(math.pi + math.pi*(p - down)/(1 - down)), 0.0

def _wings(p, amp=30, open_=30, sweep=0, down=.4):
    """Asas abertas batendo. Na descida elas varrem para frente e abrem tudo; na subida recolhem um pouco
    (como um pássaro) e a ponta chega atrasada."""
    f, push = _beat(p, down); g, _ = _beat(p - .06, down)
    tuck = 10*(1 - push)*(f < .9)
    o = open_ - tuck
    return {"wing.L": {"y": -amp*g - o*.6, "z": 12 - o + sweep - 8*push},
            "wing.R": {"y": amp*g + o*.6, "z": -12 + o - sweep + 8*push}}

def _wings_at(f, amp, open_, push=0):
    """Asas numa posição fixa da batida (f: 1 = no alto, -1 = embaixo), para golpes com tempo próprio."""
    return {"wing.L": {"y": -amp*f - open_*.6, "z": 12 - open_ - 8*push},
            "wing.R": {"y": amp*f + open_*.6, "z": -12 + open_ + 8*push}}

def _lift(p, down=.4):
    """Sobe e desce do corpo: a descida da asa empurra o corpo para cima um pouco depois."""
    return math.sin(2*math.pi*(p - down*.9) + math.pi/2)

def _dangle(p, lean=0, amp=1):
    """Pernas soltas no ar, com atraso em relação ao corpo (peso e follow-through)."""
    s = _lift(p - .12)*amp; s2 = _lift(p - .2)*amp
    return {"thigh.L": {"x": -10 - 5*s + lean}, "shin.L": {"bend": 28 + 8*s2}, "foot.L": {"x": 22 + 6*s2},
            "thigh.R": {"x": -2 - 4*s + lean}, "shin.R": {"bend": 42 + 9*s2}, "foot.R": {"x": 26 + 6*s2}}

def flyer_anims(arm, extra=None):
    """Personagens com asas (Anjo, Demônio): pairam no ar como no MU Online, batendo as asas."""
    base = merge(ARMS_DOWN, {"forearm.R": {"bend": -8}, "upper_arm.R": {"x": 4, "y": -6}, "hand.R": {"bend": 32}})
    idle = []
    for i in range(12):   # pairando: 1 batida por segundo, corpo e membros respondem com atraso
        p = i/12; b = _lift(p); b1 = _lift(p - .08); b2 = _lift(p - .16)
        idle.append(merge(base, _wings(p), _dangle(p), {
            "hips": {"x": 9, "z": 2*math.sin(2*math.pi*p)}, "spine": {"x": 3 - 1.5*b1}, "chest": {"x": 2 + 2*b1},
            "neck": {"x": -5 - 1.5*b2}, "head": {"x": -6 - 2.5*b2},
            "upper_arm.L": {"x": -4*b2, "y": -5 - 2*b1}, "forearm.L": {"bend": -14 - 6*b2},
            "upper_arm.R": {"x": 3*b2, "y": -1*b1}, "forearm.R": {"bend": -4*b2}, "hand.R": {"bend": 4*b2},
            "root": (0, 0, FLY_H + .05*b)}))
    walk = []
    for i in range(12):   # voando para frente: corpo inclinado, pernas arrastando atrás, batidas mais fortes
        p = i/12; b = _lift(p, .35); b1 = _lift(p - .08, .35); b2 = _lift(p - .16, .35)
        walk.append(merge(base, _wings(p, 36, 24, 10, .35), _dangle(p, 8, 1.3), {
            "hips": {"x": 18, "z": 3*math.sin(2*math.pi*p)}, "spine": {"x": 6 - 2*b1, "z": -2*math.sin(2*math.pi*p)},
            "chest": {"x": 4 + 2.5*b1}, "neck": {"x": -12}, "head": {"x": -16 - 2*b2},
            "upper_arm.L": {"x": 26 + 6*b2, "y": -6 - 3*b1}, "forearm.L": {"bend": -18 - 8*b2},
            "upper_arm.R": {"x": 18 + 5*b2, "y": 4}, "forearm.R": {"bend": -14 - 6*b2}, "hand.R": {"bend": 10 + 5*b2},
            "root": (0, 0, FLY_H + .06*b)}))
    # ataque no ar: recolhe e sobe com as asas abertas, desce o golpe junto com uma batida forte,
    # passa do ponto e volta a pairar com as asas ainda abertas
    KEYS = [  # (tempo, braço dir x, z, antebraço, tronco z, coluna x, asas abertas, avanço, asa (1 alto, -1 baixo), altura extra)
        (0.00, -30, 0, -55, -8, 0, 30, 0, .3, 0),
        (0.16, -110, 22, -85, -26, 6, 40, -.2, .8, .06),
        (0.30, -180, 18, -100, -40, 9, 50, -.3, 1.1, .11),
        (0.36, -172, 14, -96, -38, 8, 52, -.25, 1.15, .12),
        (0.44, -110, -10, -30, 0, -8, 48, .5, .3, .06),
        (0.50, -45, -38, -4, 34, -18, 44, 1, -.45, -.01),
        (0.58, -12, -52, -2, 46, -22, 40, 1.12, -.6, -.04),
        (0.70, -16, -40, -12, 36, -15, 36, .95, -.3, -.03),
        (0.84, -20, -16, -26, 14, -6, 32, .45, .1, 0),
        (1.00, -30, 0, -55, -8, 0, 30, 0, .3, 0),
    ]
    def sample(t):
        for (t0, *a), (t1, *b) in zip(KEYS, KEYS[1:]):
            if t <= t1:
                u = (t - t0)/(t1 - t0); u = u*u*(3 - 2*u)
                return [x + (y - x)*u for x, y in zip(a, b)]
        return KEYS[-1][1:]
    attack = []
    for i in range(16):
        ax, az, fb, cz, sx, wg, lg, wf, h = sample(i/16)
        _, axp, azp, fbp, *_r = sample(max(0, i - 1)/16)
        wfp = sample(max(0, i - 1)/16)[7]; push = max(0, min(1, (wfp - wf)*1.5))
        attack.append(merge(ARMS_DOWN, _wings_at(wf, 32, wg, push), _dangle(i/16 + .3, 12*lg, .8), {
            "upper_arm.R": {"y": 34, "x": ax, "z": az}, "forearm.R": {"bend": fb}, "hand.R": {"bend": -.15*fbp},
            "upper_arm.L": {"x": -15*lg, "y": -10*max(lg, 0)}, "forearm.L": {"bend": -30*max(lg, 0) - 10},
            "chest": {"z": cz}, "spine": {"x": -.7*sx, "z": cz*.4}, "head": {"z": -cz*.45, "x": sx*.4 - 6},
            "hips": {"x": 9 + 8*max(lg, 0), "z": cz*.15}, "neck": {"x": -4},
            "root": (0, -.1*lg, FLY_H + h)}))
    if extra:
        idle, walk, attack = ([merge(f, extra) for f in L_] for L_ in (idle, walk, attack))
    return {"idle": make_action(arm, "idle", idle), "walk": make_action(arm, "walk", walk),
            "attack": make_action(arm, "attack", attack)}
