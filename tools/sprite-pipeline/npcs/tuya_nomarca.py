# Tuya, Nomarca de Mênfis Reerguida (Egito). Desenterrou a casa da avó em Mit Rahina e achou embaixo a de alguém de
# três mil anos; cobra dízimo de quem cava no planalto ("a terra é preta e a terra é minha"). Mulher de uns quarenta
# anos, alta, cabeça raspada sob um lenço de linho sujo de lodo, sobretudo de couro curtido sobre túnica de linho
# plissada até o tornozelo, peitoral largo de contas de faiança remendado com arame: uma única conta turquesa ainda
# acende (único brilho). Segura a vara de côvado (régua de medir terra) como cetro, a outra mão na cintura.
from kit import *

INFO = info("egito", tz=.92, escala=1.03)
CORES_EXTRA = "40f0d8"

def build():
    R = rig("tuya_nomarca")
    skin = pele("ty_pele", (.24, .14, .08), sujo=.4)
    cou = couro("ty_sobretudo", (.16, .09, .045), rachado=.6, gasto=.5)
    linho_m = pano("ty_tunica", (.4, .36, .28), vinco=.6, desbote=.2, mancha=(.12, .1, .06), mancha_amt=.5, grime=1.2, trama=110)
    lenco_m = pano("ty_lenco", (.2, .12, .07), vinco=.4, mancha=(.1, .08, .05), mancha_amt=.7)
    faixas = listras("ty_colar", (.08, .3, .3), (.35, .22, .08), period=.018, duty=.5, axis='Z', wear=.45, under=(.3, .26, .2), rough=.5)
    fer = ferro("ty_arame"); mad = madeira("ty_vara", (.16, .09, .045)); br = bronze("ty_bronze")
    corpo(R, skin, linho_m, linho_m, mangas=cou, maos=skin, mulher=True, magro=.95, busto=.4, descalco=True, punho=1.2)
    aba(R, linho_m, z0=1.05, z1=.08, aberto=0, rodado=.7, jag=.03, seed=3, folds=24, famp=.02)
    aba(R, cou, z0=1.08, z1=.4, aberto=.7, rodado=1.0, jag=.05, seed=5, folds=8, famp=.05, nome="ty_casaco")
    gola(R, cou, alta=.03, lapela=True)
    colar_largo(R, faixas, contas=br, conta_acesa=glow("ty_turquesa", TURQ, 2.5))
    R.rigid([along("primitive_cylinder_add", fer, (-.1, -.15, 1.38), (-.04, -.165, 1.36), .003, vertices=4),
             along("primitive_cylinder_add", fer, (.06, -.16, 1.37), (.11, -.15, 1.39), .003, vertices=4)], "chest")
    cinto(R, cou, fivela=br, z=1.02, r=.17, ry=.8, grosso=.016)
    # sandálias de couro
    for n in "LR":
        R.rigid([prim("primitive_cube_add", cou, R.P(f"foot.{n}") + Vector((0, -.05, -.077)), (.045, .1, .008))], f"foot.{n}")
    # vara de côvado (régua de madeira com marcas de bronze)
    G = grip(R, "R"); vr = [along("primitive_cube_add", mad, G + Vector((0, .5, 0)), G + Vector((0, -.6, 0)), .016)]
    for k in range(7): vr.append(prim("primitive_cube_add", br, G + Vector((0, .45 - .15*k, .0)), (.019, .005, .019)))
    vr.append(prim("primitive_uv_sphere_add", br, G + Vector((0, -.62, 0)), (.025,)*3, segments=8, ring_count=6))
    R.rigid(vr, "prop.R")
    # cabeça raspada sob o lenço de linho amarrado atrás, brincos de cobre
    hd = cabeca(R, skin, mulher=True, idade=.4, queixo=1.05, nariz=1.05, sobrancelha=cabelo("ty_sobr", (.03, .02, .015)))
    hd += lenco(lenco_m, no_=True)
    for sd in (1, -1): hd.append(prim("primitive_torus_add", cobre("ty_cobre"), HC + Vector((.088*sd, -.0, -.05)), (1, 1, 1), rot=(0, 90, 0), major_radius=.012, minor_radius=.003))
    R.rigid(hd, "head")
    return fim(R, INFO)

BASE = {"upper_arm.R": {"y": -24, "x": -20}, "forearm.R": {"bend": -55}, "aim": {"prop.R": (0, -.1, -1)},
        "upper_arm.L": {"y": 46, "x": 10, "z": -10}, "forearm.L": {"bend": -100}, "chest": {"x": -3}, "head": {"x": 2}}

def anims(R):
    def ex(i, n):  # bate a vara de côvado no chão de leve, olhar firme
        return {"upper_arm.R": {"x": -4*max(0, wave(i, n))}, "head": {"z": 6*wave(i, n, ph=1)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, .2), passo=16)
