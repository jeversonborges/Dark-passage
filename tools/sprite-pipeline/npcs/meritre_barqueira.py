# Meritre, Barqueira da Escavação (Egito). Filha de Ahmose: mulher forte de meia-idade, braços de remadora, véu de linho
# contra a areia, amuleto de escaravelho no pescoço. Pouca conversa, muita pressa: o remo no ombro, pronta para sair.
# Sem brilho.
from kit import *

INFO = info("egito", tz=.92, px=224)

def build():
    R = rig("meritre_barqueira")
    skin = pele("mr_pele", (.22, .12, .07), sujo=.35)
    vest = pano("mr_vestido", (.3, .24, .15), vinco=.5, desbote=.3, mancha_amt=.6, grime=1.3)
    veu = pano("mr_veu", (.4, .36, .28), vinco=.4, mancha_amt=.5)
    faixa = pano("mr_faixa", (.12, .14, .2), vinco=.3, desbote=.4)
    mad = madeira("mr_remo", (.2, .13, .06)); br = bronze("mr_bronze"); cou = couro("mr_couro", (.12, .07, .035))
    cab = cabelo("mr_cabelo", (.03, .025, .02))
    corpo(R, skin, vest, vest, mangas=skin, maos=skin, mulher=True, massa=1.05, larg=1.05, busto=.5, descalco=True, punho=1.15)
    aba(R, vest, z0=1.05, z1=.22, aberto=0, rodado=.85, jag=.05, seed=9, folds=12, famp=.04)
    R.rigid([prim("primitive_torus_add", faixa, (0, 0, 1.03), (1, .85, 1.5), major_radius=.15, minor_radius=.02)], "hips")
    # braçadeiras de couro (calos de remar)
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"forearm.{n}")
        R.rigid([along("primitive_cylinder_add", cou, o_ + ax*.12, o_ + ax*.2, .045, vertices=12)], f"forearm.{n}")
    # escaravelho no pescoço
    R.rigid([prim("primitive_uv_sphere_add", br, (0, -.13, 1.4), (.02, .01, .026), segments=10, ring_count=6),
             prim("primitive_torus_add", cou, (0, -.03, 1.47), (1, 1.2, 1), rot=(-25, 0, 0), major_radius=.085, minor_radius=.004)], "chest")
    # remo no ombro
    G = grip(R, "R"); R.rigid(remo(mad, G, comp=1.9, pa=.38, larg=.1, ferragem=br), "prop.R")
    hd = cabeca(R, skin, mulher=True, idade=.45, queixo=1.05, sobrancelha=cab)
    hd += cabelo_curto(cab, 1.0)
    hd += capuz(veu, caido=False, ponta=.03)
    R.rigid(hd, "head")
    return fim(R, INFO)

# remo apoiado no ombro direito (pá para trás); esquerda no quadril
BASE = {"upper_arm.R": {"y": -10, "x": -30, "z": 10}, "forearm.R": {"bend": -120}, "aim": {"prop.R": (0, .75, -.45)},
        "upper_arm.L": {"y": 40, "x": 8, "z": -12}, "forearm.L": {"bend": -95}, "chest": {"x": -2}}

def anims(R):
    def ex(i, n):  # bate o pé, impaciente
        return {"head": {"z": 7*wave(i, n)}, "foot.L": {"x": -10*max(0, wave(i, n*.5))}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.8, 0), passo=20)
