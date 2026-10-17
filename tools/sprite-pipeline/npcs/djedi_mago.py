# Djedi, Mago da Casa de Hermes (Egito). Velhíssimo, magro como um caniço, pele de papiro, barba branca até o cinto
# trançada com fios de ouro. Túnica de linho e sobretudo de couro de hermetista coberto de símbolos costurados. Um olho
# de faiança no lugar do esquerdo, aceso em turquesa (único brilho). Fala por enigmas e explica os enigmas; come cem
# pães e bebe um jarro de cerveja por dia, como no papiro. Apoia-se num cajado de junco com uma tábua de Toth na ponta.
from kit import *

INFO = info("egito", tz=.95, px=208)
CORES_EXTRA = "40f0d8"

def build():
    R = rig("djedi_mago")
    skin = pele("dj_pele", (.3, .21, .13), sujo=.4, marcas=(.18, .12, .07), marcas_amt=.5)
    linho_m = pano("dj_tunica", (.42, .39, .31), vinco=.6, mancha=(.12, .1, .06), mancha_amt=.5, grime=1.2, trama=120)
    cou = couro("dj_sobretudo", (.11, .065, .035), rachado=.6, gasto=.6)
    sim = mat("dj_simbolo", (.42, .3, .1), .7, .4)
    our = ouro("dj_ouro"); mad = madeira("dj_cajado", (.25, .18, .09))
    barb = cabelo("dj_barba", (.55, .53, .49), grisalho=1.0, fios=160)
    corpo(R, skin, linho_m, linho_m, mangas=cou, maos=skin, magro=.8, larg=.9, descalco=True, corcunda=.35, manga_r=1.15)
    aba(R, linho_m, z0=1.05, z1=.06, aberto=0, rodado=.75, jag=.03, seed=2, folds=18, famp=.02)
    aba(R, cou, z0=1.1, z1=.2, aberto=.6, rodado=1.05, jag=.07, seed=4, folds=9, famp=.05, nome="dj_casaco")
    gola(R, cou, alta=.08, lapela=False)
    # símbolos costurados no sobretudo (fios de latão: ankh, olho, espiral)
    sm = []
    for k, (x, z) in enumerate(((.13, 1.32), (-.12, 1.25), (.15, 1.12), (-.14, 1.05))):
        y = -.13
        sm.append(prim("primitive_torus_add", sim, (x, y, z + .03), (1, 1, 1.3), rot=(90, 0, 0), major_radius=.014, minor_radius=.002))
        sm.append(along("primitive_cylinder_add", sim, (x, y, z + .01), (x, y, z - .04), .002, vertices=4))
        sm.append(along("primitive_cylinder_add", sim, (x - .02, y, z), (x + .02, y, z), .002, vertices=4))
    R.rigid(sm, "chest")
    # cajado de junco com a tábua de Toth (paleta de escriba)
    G = grip(R, "R")
    cj = [along("primitive_cylinder_add", mad, G + Vector((0, .55, 0)), G + Vector((0, -1.05, 0)), .013, vertices=8)]
    for k in range(6): cj.append(prim("primitive_torus_add", mad, G + Vector((0, .5 - .3*k, 0)), (1, 1, 1), rot=(90, 0, 0), major_radius=.015, minor_radius=.004))
    cj.append(prim("primitive_cube_add", our, G + Vector((0, .6, 0)), (.035, .012, .07)))
    R.rigid(cj, "prop.R")
    # cabeça: rosto de papiro, barba trançada com ouro, olho de faiança aceso
    olho = glow("dj_faianca", TURQ, 3.0)
    hd = cabeca(R, skin, idade=1.0, magro=.8, nariz=1.2, queixo=.9, olho_vidro=(1, olho), sobrancelha=barb)
    hd += barba(barb, comp=.42, larg=1.0, trancada=True, fio=our)
    hd += careca(barb, coroa=.012)
    R.rigid(hd, "head")
    return fim(R, INFO)

# curvado sobre o cajado; esquerda erguida com o indicador (o enigma)
BASE = {"upper_arm.R": {"y": -28, "x": -28}, "forearm.R": {"bend": -50}, "aim": {"prop.R": (0, -.08, -1)},
        "upper_arm.L": {"y": 22, "x": -30}, "forearm.L": {"bend": -105}, "head": {"x": -6, "z": -6}}

def anims(R):
    def ex(i, n):  # mexe o dedo explicando, cabeça inclinada sorrindo
        return {"forearm.L": {"bend": 10*wave(i, n*.5)}, "head": {"y": 4*wave(i, n)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.5, 0), passo=11)
