# Senebtisi, Sacerdotisa de Sobek (Egito). Heródoto viu os sacerdotes de Crocodilópolis enfeitarem o crocodilo sagrado
# com brincos de ouro e pulseiras; ela é a última deles. Mulher idosa de cabeça raspada, pele marcada de escamas
# desenhadas a carvão, manto de couro de crocodilo (a cabeça do bicho sobre o ombro), braceletes de bronze com brincos
# de ouro pendurados. Serena e assustadora: fala dos crocodilos como de filhos. Sem brilho.
from kit import *

INFO = info("egito", tz=.9, px=208)

def build():
    R = rig("senebtisi_sacerdotisa")
    skin = pele("sn_pele", (.22, .13, .08), sujo=.3, marcas=(.02, .02, .02), marcas_amt=.75)
    linho_m = pano("sn_tunica", (.38, .34, .27), vinco=.55, mancha=(.1, .08, .05), mancha_amt=.5, grime=1.1)
    croc = mat("sn_croco", (.09, .1, .06), 0, .55, dirt=.7)
    try: croc = scales("sn_croco", (.09, .1, .06), belly=(.25, .22, .14), cell=.035, rough=.5)
    except Exception: pass
    br = bronze("sn_bronze"); our = ouro("sn_ouro"); dente = mat("sn_dente", (.45, .4, .3), 0, .5)
    corpo(R, skin, linho_m, linho_m, mangas=skin, maos=skin, mulher=True, magro=.9, busto=.3, descalco=True, corcunda=.15)
    aba(R, linho_m, z0=1.05, z1=.08, aberto=0, rodado=.8, jag=.03, seed=4, folds=20, famp=.02)
    capa(R, croc, z1=.25, larg=1.05, jag=.03, seed=6, aberto=1.0)
    # cabeça do crocodilo sobre o ombro direito
    S = Vector((-.17, .02, 1.5))
    cc = [prim("primitive_uv_sphere_add", croc, S + Vector((0, 0, .03)), (.07, .09, .045), segments=12, ring_count=8),
          along("primitive_cone_add", croc, S + Vector((0, -.06, .03)), S + Vector((-.01, -.26, .02)), .045, vertices=10, radius1=1, radius2=.35)]
    for k in range(6):
        for sd in (1, -1): cc.append(along("primitive_cone_add", dente, S + Vector((.03*sd, -.08 - .03*k, .012)), S + Vector((.032*sd, -.08 - .03*k, -.008)), .005, vertices=4, radius1=1, radius2=0))
    for sd in (1, -1): cc.append(prim("primitive_uv_sphere_add", our, S + Vector((.065*sd, -.02, .02)), (.008,)*3, segments=6, ring_count=4))
    R.rigid(cc, "chest")
    # braceletes de bronze com brincos de ouro pendurados
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"forearm.{n}")
        bl = [along("primitive_cylinder_add", br, o_ + ax*.17, o_ + ax*.22, .042, vertices=12)]
        for k in range(4):
            a = k*1.6; p = o_ + ax*.2 + Vector((.043*math.cos(a), .043*math.sin(a), -.02))
            bl.append(prim("primitive_torus_add", our, p, (1, 1, 1), rot=(90, 0, a*57), major_radius=.01, minor_radius=.0025))
        R.rigid(bl, f"forearm.{n}")
    hd = cabeca(R, skin, mulher=True, idade=.85, magro=.9, nariz=1.05, queixo=.95)
    for sd in (1, -1): hd.append(prim("primitive_torus_add", our, HC + Vector((.088*sd, 0, -.06)), (1, 1, 1), rot=(0, 90, 0), major_radius=.016, minor_radius=.0035))
    R.rigid(hd, "head")
    return fim(R, INFO)

# mãos juntas na frente, palmas para cima, oferenda ao rio
BASE = {"upper_arm.L": {"y": 26, "x": -30}, "forearm.L": {"bend": -70}, "upper_arm.R": {"y": -26, "x": -30}, "forearm.R": {"bend": -70},
        "head": {"x": 5}}

def anims(R):
    def ex(i, n):  # balança devagar, como quem canta para o rio
        return {"spine": {"y": 3*wave(i, n)}, "head": {"y": -3*wave(i, n)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.3, .3), passo=12)
