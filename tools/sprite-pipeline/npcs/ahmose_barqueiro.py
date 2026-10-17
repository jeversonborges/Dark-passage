# Ahmose, Barqueiro das Docas de Mênfis (Egito). Velho magro e queimado de sol, saiote de linho, chapéu de palha furado,
# remo comprido de acácia. Tatuagem do olho de Hórus no ombro. Atravessa a feluca da margem dos vivos para a dos mortos
# por três moedas. Fala devagar, como o rio. Apoia-se no remo fincado no chão. Sem brilho.
from kit import *

INFO = info("egito", tz=.95, px=224)

def build():
    R = rig("ahmose_barqueiro")
    skin = pele("ah_pele", (.2, .11, .06), sujo=.3, marcas=(.12, .07, .04), marcas_amt=.4)
    linho_m = pano("ah_saiote", (.42, .38, .3), vinco=.6, mancha=(.12, .1, .06), mancha_amt=.6, grime=1.4)
    palha = mat("ah_palha", (.4, .31, .16), 0, .85, dirt=.6)
    mad = madeira("ah_remo", (.22, .14, .07)); cob = cobre("ah_cobre")
    tinta = mat("ah_tatuagem", (.03, .05, .07), 0, .7)
    cab = cabelo("ah_cabelo", (.3, .29, .27), grisalho=.8)
    corpo(R, skin, skin, skin, mangas=skin, maos=skin, magro=.82, larg=.92, descalco=True, corcunda=.25)
    saiote(R, linho_m, z1=.6, plisse=True, cinto_m=pano("ah_faixa", (.25, .2, .12)))
    # olho de Hórus tatuado no ombro esquerdo
    o_, ax, u, sd_ = R.frame("upper_arm.L")
    R.rigid([prim("primitive_torus_add", tinta, o_ + ax*.06 + Vector((.05, -.01, .0)), (1, 1, .5), rot=(0, 90, 0), major_radius=.018, minor_radius=.003),
             along("primitive_cylinder_add", tinta, o_ + ax*.06 + Vector((.052, -.02, -.012)), o_ + ax*.06 + Vector((.052, -.015, -.035)), .003, vertices=4)], "upper_arm.L")
    # remo de acácia apoiado no chão, pá para cima
    G = grip(R, "R"); rm = remo(mad, G, comp=1.4, pa=.36, larg=.1, ferragem=cob)
    R.rigid(rm, "prop.R")
    # pulseira de cobre e as três moedas na palma
    hd = cabeca(R, skin, idade=.9, magro=.85, nariz=1.15, queixo=.95, sobrancelha=cab)
    hd += barba(cab, comp=.05, larg=.9)
    hd += chapeu_palha(palha, aba=.2, furos=True)
    R.rigid(hd, "head")
    return fim(R, INFO)

# remo na direita, fincado no chão (pá para cima, ao lado do rosto); esquerda solta
BASE = {"upper_arm.R": {"y": -26, "x": -24}, "forearm.R": {"bend": -70}, "aim": {"prop.R": (0, .05, -1)},
        "upper_arm.L": {"y": 34, "x": 4}, "forearm.L": {"bend": -20}, "head": {"x": 6}}

def anims(R):
    def ex(i, n):  # balança o peso no remo, devagar
        return {"spine": {"y": 2*wave(i, n)}, "head": {"z": 4*wave(i, n, ph=1)}}
    def wk(i, n):  # usa o remo como cajado
        return {"upper_arm.R": {"x": -8*wave(i, n)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.6, 0), passo=13, walk_extra=wk)
