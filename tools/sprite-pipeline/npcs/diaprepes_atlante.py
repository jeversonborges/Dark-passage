# Diaprepes, Embaixador de Thotme (Atlântida, no Egito). Platão dá esse nome a um dos dez reis de Atlântida. Homem alto
# de pele cor de bronze e olhos verdes demais, túnica azul-mar sob armadura leve de oricalco riscada, cristal esverdeado
# preso no peito que zune baixinho (único brilho). Máscara de filtro pendurada no pescoço para quando o vento traz areia.
# Educado, triste, deslocado: segura a máscara olhando o horizonte.
from kit import *

INFO = info("egito", tz=.98, escala=1.06, px=208)
CORES_EXTRA = "5af0a0"

def build():
    R = rig("diaprepes_atlante")
    skin = pele("dp_pele", (.3, .17, .08), sujo=.25, rubor_amt=.15)
    mar = pano("dp_tunica", (.04, .12, .16), vinco=.5, desbote=.4, mancha_amt=.4, grime=1.0)
    ori = patina("dp_oricalco", (.6, .3, .14), green=(.06, .2, .14), rough=.46, amount=.55, scale=4.5)
    cou = couro("dp_couro", (.1, .06, .03)); vd = vidro("dp_visor", (.05, .1, .08))
    cab = cabelo("dp_cabelo", (.025, .02, .016), fios=120)
    corpo(R, skin, mar, mar, mangas=mar, botas=cou, maos=skin, larg=1.02, massa=1.0, magro=.95, punho=1.1)
    aba(R, mar, z0=1.05, z1=.42, aberto=.2, rodado=.9, jag=.03, seed=3, folds=16, famp=.025)
    # peitoral de oricalco em placas, ombreiras e cinto de placas
    ar = [prim("primitive_uv_sphere_add", ori, (0, -.03, 1.31), (.2, .145, .17), segments=18, ring_count=10)]
    for sd in (1, -1):
        for k in range(3): ar.append(prim("primitive_uv_sphere_add", ori, (.2*sd, -.0, 1.44 - .045*k), (.075 - .006*k, .08, .028), segments=12, ring_count=6, rot=(0, 18*sd, 0)))
    for k in range(4): ar.append(prim("primitive_torus_add", ori, (0, -.015, 1.17 - .03*k), (1, .78, 1.2), major_radius=.175 - .004*k, minor_radius=.014))
    crist = glow("dp_cristal", (.35, 1.0, .6), 4.0)
    ar.append(prim("primitive_cone_add", crist, (0, -.18, 1.33), (.022, .022, .035), vertices=6))
    ar.append(prim("primitive_cone_add", crist, (0, -.18, 1.27), (.022, .022, .03), vertices=6, rot=(180, 0, 0)))
    ar.append(prim("primitive_torus_add", ori, (0, -.172, 1.31), (1, .6, 1.3), rot=(90, 0, 0), major_radius=.034, minor_radius=.007))
    R.rigid(ar, "chest")
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"forearm.{n}")
        R.rigid([along("primitive_cylinder_add", ori, o_ + ax*.08, o_ + ax*.22, .05, vertices=12)], f"forearm.{n}")
    # máscara de filtro na mão esquerda
    G = grip(R, "L"); R.rigid(mascara_gas(cou, vd, ori, pos=G + Vector((0, -.06, -.02)), pendurada=True), "prop.L")
    hd = cabeca(R, skin, idade=.4, queixo=1.1, nariz=1.1, olhos=(.03, .025, .02), sobrancelha=cab)
    hd += cabelo_curto(cab, 1.02)
    for sd in (1, -1): hd.append(prim("primitive_uv_sphere_add", crist, HC + Vector((.032*sd, -.087, .005)), (.006,)*3, segments=6, ring_count=4))
    hd.append(prim("primitive_torus_add", ori, HC + Vector((0, 0, .06)), (1, 1.1, 1), major_radius=.092, minor_radius=.008))
    R.rigid(hd, "head")
    return fim(R, INFO)

BASE = {"upper_arm.L": {"y": 30, "x": -25}, "forearm.L": {"bend": -70}, "upper_arm.R": {"y": -32, "x": -2}, "forearm.R": {"bend": -15},
        "head": {"z": 18, "x": -4}, "chest": {"x": -2}}

def anims(R):
    def ex(i, n):  # olha o horizonte, suspira
        return {"chest": {"x": -2*wave(i, n)}, "head": {"z": 4*wave(i, n*.5)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 1), passo=18)
