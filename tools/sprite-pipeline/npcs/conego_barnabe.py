# Barnabé, Cônego do Coro (Arautos, no Egito). Anjo de meia-idade, gordo, asas cinzentas cobertas de pó, batina roxa
# desbotada sob um sobretudo de couro com fivelas de latão. Uma balança de bronze pequena presa ao cinto, que ele
# equilibra com os dedos quando pensa. Erudito, gentil, convicto: fala baixo das coisas mais terríveis. Sem brilho.
from kit import *

INFO = info("arautos", tz=1.0, escala=1.0, px=256)

def build():
    R = rig("conego_barnabe", extra=dict(ASAS))
    skin = pele("cb_pele", (.42, .3, .24), sujo=.35, rubor_amt=.45)
    roxo = pano("cb_batina", (.12, .06, .13), vinco=.45, desbote=.55, mancha_amt=.5, grime=1.1)
    cou = couro("cb_sobretudo", (.08, .05, .035), rachado=.5, gasto=.5)
    lat = latao("cb_latao"); br = bronze("cb_bronze"); bot = couro("cb_bota", (.05, .035, .025))
    pclaro = pano("cb_pena_c", (.36, .35, .33), vinco=.1, desbote=.2, mancha=(.2, .18, .15), mancha_amt=.8, grime=1.5)
    pescuro = pano("cb_pena_e", (.2, .2, .2), vinco=.1, mancha_amt=.7, grime=1.5)
    cab = cabelo("cb_cabelo", (.15, .13, .11), grisalho=.5)
    corpo(R, skin, roxo, roxo, mangas=cou, botas=bot, maos=skin, massa=1.1, barriga=1.1, larg=1.08, punho=1.25, manga_r=1.15)
    aba(R, roxo, z0=1.02, z1=.1, aberto=0, rodado=1.05, jag=.03, seed=5, folds=12, famp=.03)
    aba(R, cou, z0=1.08, z1=.38, aberto=.7, rodado=1.12, jag=.05, seed=8, folds=8, famp=.05, nome="cb_casaco")
    gola(R, cou, alta=.05, lapela=True)
    fv = []
    for k in range(3):
        for sd in (1, -1): fv.append(prim("primitive_cube_add", lat, (.11*sd, -.17 - .015*k, 1.34 - .09*k), (.016, .004, .011)))
    R.rigid(fv, "chest")
    cinto(R, cou, fivela=lat, z=1.0, r=.21)
    for s in (1, -1): asa(R, s, pclaro, pescuro, tira_m=cou, metal=lat, fechada=True, esc=.9, falhas=.05, seed=11)
    # balança pequena na mão esquerda (ele equilibra com os dedos)
    G = grip(R, "L"); b = [along("primitive_cylinder_add", br, G + Vector((-.08, -.04, .0)), G + Vector((.08, -.04, 0)), .004, vertices=6),
                           along("primitive_cylinder_add", br, G + Vector((0, -.04, 0)), G + Vector((0, -.04, .05)), .005, vertices=6)]
    for sd in (1, -1):
        for dx in (-.012, .012): b.append(along("primitive_cylinder_add", br, G + Vector((.08*sd, -.04, 0)), G + Vector((.08*sd + dx, -.04, -.07)), .0015, vertices=4))
        b.append(prim("primitive_cylinder_add", br, G + Vector((.08*sd, -.04, -.075)), (.03, .03, .004), vertices=12))
    R.rigid(b, "prop.L")
    hd = cabeca(R, skin, idade=.5, queixo=1.15, nariz=1.05, sobrancelha=cab)
    hd.append(prim("primitive_uv_sphere_add", skin, HC + Vector((0, -.05, -.115)), (.07, .05, .035), segments=12, ring_count=8))
    hd += careca(cab, coroa=.02)
    R.rigid(hd, "head")
    return fim(R, INFO)

BASE = {"upper_arm.L": {"y": 26, "x": -40}, "forearm.L": {"bend": -75}, "aim": {"prop.L": (0, -1, 0)},
        "upper_arm.R": {"y": -26, "x": -30}, "forearm.R": {"bend": -70}, "head": {"x": 10}}

def anims(R):
    def ex(i, n):  # equilibra a balança com o dedo, pensativo
        return {"hand.L": {"y": 8*wave(i, n)}, "forearm.R": {"bend": -6*wave(i, n*.5)}, "head": {"y": 3*wave(i, n)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, .4), passo=12)
