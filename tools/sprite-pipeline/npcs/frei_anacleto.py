# Frei Anacleto, o Emparedado (neutro, Ossário das Carpideiras). Fantasma de um monge magro, emparedado vivo por
# penitência há trezentos anos; translúcido e esverdeado, preso da cintura para baixo num trecho de parede de
# tijolos (a parede faz parte do sprite). Hábito de burel com capuz caído, tonsura, rosto chupado, o terço com que
# foi emparedado ainda nas mãos. Não anda: o "walk" é o mesmo balanço do idle, mais aflito (ele gesticula).
# O brilho é o próprio fantasma (verde pálido); no jogo usar "fantasma": true no substituto (transparência).
from kit import *

INFO = info("neutro", tz=.95, px=224)

def build():
    R = rig("frei_anacleto", extra={"parede": ((0, 0, 0), (0, 0, .3), None)})
    fant = glow("fa_fantasma", (.32, .78, .5), 1.4)
    fant2 = glow("fa_fantasma2", (.2, .5, .32), 1.1)
    corpo_m = pano("fa_habito", (.16, .36, .24), vinco=.6, desbote=.4, trama=60, grime=.2, rough=.5)
    corpo(R, fant, corpo_m, corpo_m, mangas=corpo_m, maos=fant, magro=.85, larg=.95, punho=1.7, manga_r=1.3, descalco=True)
    aba(R, corpo_m, z0=1.05, z1=.7, aberto=0, rodado=.8, jag=.06, seed=4, folds=8, famp=.06)
    R.rigid(capuz(corpo_m, caido=True), "chest")
    R.rigid([prim("primitive_torus_add", fant2, (0, 0, 1.03), (1, .8, 1.4), major_radius=.15, minor_radius=.012)], "hips")  # cordão
    # terço nas mãos
    G = grip(R, "R"); tc = []
    for k in range(10):
        a = k/10*2*math.pi
        tc.append(prim("primitive_uv_sphere_add", fant2, G + Vector((.025*math.sin(a), -.02, -.04 - .05*(1 - math.cos(a)))), (.008,)*3, segments=6, ring_count=4))
    tc.append(along("primitive_cube_add", fant2, G + Vector((0, -.02, -.14)), G + Vector((0, -.02, -.19)), .005))
    tc.append(along("primitive_cube_add", fant2, G + Vector((-.015, -.02, -.155)), G + Vector((.015, -.02, -.155)), .005))
    R.rigid(tc, "prop.R")
    # cabeça: tonsura, rosto chupado
    hd = cabeca(R, fant, idade=.9, magro=.75, nariz=1.15, sobrancelha=fant2)
    hd += careca(fant2, coroa=.018)
    R.rigid(hd, "head")
    # parede de tijolos do chão até a cintura (ele está dentro dela): bloco estreito, topo quebrado em degraus,
    # tijolos rentes com argamassa funda, rachaduras e tijolos caídos no pé
    tij = stained("fa_tijolo", (.17, .085, .055), stain=(.05, .04, .03), amount=.45, scale=6, rough=.85, blotch=(.1, .09, .08), blotch_amt=.6, grime=.8)
    arg = mat("fa_argamassa", (.05, .045, .04), 0, .95, dirt=.6)
    pw = []; rr = random.Random(5); W = .36; D = .13
    top = lambda x: .98 + .07*math.cos(x*7) - .12*abs(x)/W
    pw.append(prim("primitive_cube_add", arg, (0, .0, .48), (W - .005, D - .004, .48)))
    for row in range(11):
        z = .05 + row*.092
        for k in range(5):
            x = -W + (k + .5*(row % 2) + .5)*(2*W/4.5)
            if abs(x) > W - .04 or z > top(x): continue
            for y, nrm in ((-D, -1), (D, 1)):
                b = prim("primitive_cube_add", tij, (x, y + nrm*.004, z), (.07*rr.uniform(.9, 1.05), .012, .04),
                         rot=(rr.uniform(-1.5, 1.5), 0, rr.uniform(-1.5, 1.5)))
                b.modifiers.new("b", 'BEVEL').width = .006; pw.append(b)
        for sx in (-1, 1):  # topo das laterais
            pw.append(prim("primitive_cube_add", tij, (sx*(W + .004), 0, z), (.012, D*.9, .04)))
    for k in range(4):
        pw.append(rock(tij, (rr.uniform(-W, W), rr.choice((-1, 1))*(D + rr.uniform(.04, .14)), .03), (.06, .035, .03), 10 + k))
    R.rigid(pw, "parede")
    return fim(R, INFO)

BASE = {"upper_arm.R": {"y": -16, "x": -46}, "forearm.R": {"bend": -100}, "upper_arm.L": {"y": 16, "x": -46}, "forearm.L": {"bend": -100},
        "spine": {"x": 6}, "chest": {"x": 6}, "head": {"x": -4}}

def anims(R):
    def ex(i, n):  # flutua de leve; ergue a mão esquerda corrigindo o latim de alguém
        u = max(0, wave(i, n))
        return {"root": (0, 0, .015*wave(i, n)), "upper_arm.L": {"x": -30*u, "y": -10*u}, "forearm.L": {"bend": 30*u}, "head": {"z": 8*wave(i, n, ph=1)}, "ground": None}
    a = anims_npc(R, BASE, idle_extra=ex, balanco=(0, 0))
    a["walk"] = a["idle"]
    return a
