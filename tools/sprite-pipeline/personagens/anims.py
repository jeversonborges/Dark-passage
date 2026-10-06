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
