# Tadeu, último vigia de incêndio da Torre (Novo Éden). Velho alto e curvo, sobretudo de bombeiro florestal com faixas
# refletivas que já não refletem nada, binóculo de latão no pescoço, mão esquerda enfaixada de queimadura antiga.
# Carrega o livro de plantão da Torre amarrado com arame. Olha longe pelo binóculo de vez em quando. Sem brilho.
from kit import *

INFO = info("eden", tz=.97, escala=1.04, px=208)

def build():
    R = rig("tadeu_vigia")
    skin = pele("ta_pele", (.36, .24, .18), sujo=.45, marcas=(.22, .1, .07), marcas_amt=.3)
    cas = pano("ta_sobretudo", (.2, .12, .05), vinco=.45, desbote=.55, remendo=(.1, .08, .05), rem_amt=.15, grime=1.3)
    faixa = pano("ta_faixa", (.32, .32, .27), vinco=.2, desbote=.5, mancha=(.08, .07, .05), mancha_amt=.8, grime=1.5)
    calca = pano("ta_calca", (.08, .075, .06)); bot = couro("ta_bota", (.05, .035, .025), rachado=.6)
    lat = latao("ta_latao"); vd = vidro("ta_lente", (.05, .08, .07)); fer = ferro("ta_arame")
    bandagem = pano("ta_bandagem", (.4, .37, .3), mancha=(.15, .08, .04), mancha_amt=.7, grime=1.3)
    cou = couro("ta_livro", (.1, .05, .03)); cab = cabelo("ta_cabelo", (.4, .39, .37), grisalho=.9)
    corpo(R, skin, cas, calca, mangas=cas, botas=bot, maos=skin, magro=.88, larg=.98, corcunda=.35, punho=1.2, manga_r=1.1)
    aba(R, cas, z0=1.08, z1=.38, aberto=.4, rodado=1.0, jag=.05, seed=19, folds=8, famp=.05)
    gola(R, cas, alta=.07, lapela=False)
    R.rigid([prim("primitive_torus_add", faixa, (0, -.0, 1.2 - .02*k), (1, .8, 1), major_radius=.19, minor_radius=.012) for k in (0, 1)], "chest")
    R.rigid([prim("primitive_torus_add", faixa, (0, 0, .62), (1, .85, 1), major_radius=.22, minor_radius=.012)], "hips")
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"forearm.{n}")
        R.rigid([along("primitive_cylinder_add", faixa, o_ + ax*.15, o_ + ax*.19, .052, vertices=12)], f"forearm.{n}")
    o_, ax, u, sd_ = R.frame("hand.L"); R.rigid([along("primitive_cylinder_add", bandagem, o_, o_ + ax*.08, .036, vertices=10)], "hand.L")
    # binóculo no pescoço
    bn = [along("primitive_cylinder_add", lat, (sd*.03, -.15, 1.33), (sd*.03, -.2, 1.33), .02, vertices=10) for sd in (1, -1)]
    bn += [prim("primitive_cylinder_add", vd, (sd*.03, -.201, 1.33), (.016, .016, .002), rot=(90, 0, 0), vertices=10) for sd in (1, -1)]
    bn.append(prim("primitive_torus_add", cou, (0, -.05, 1.43), (1, 1.3, 1), rot=(-30, 0, 0), major_radius=.09, minor_radius=.004))
    R.rigid(bn, "chest")
    G = grip(R, "R"); R.rigid([prim("primitive_cube_add", cou, G + Vector((0, -.04, 0)), (.03, .1, .13)),
                              prim("primitive_cube_add", pano("ta_papel", (.42, .38, .3), trama=30), G + Vector((.0, -.04, 0)), (.034, .095, .12)),
                              prim("primitive_torus_add", fer, G + Vector((0, -.04, 0)), (1, 1.2, 1.4), rot=(0, 90, 0), major_radius=.1, minor_radius=.003)], "prop.R")
    hd = cabeca(R, skin, idade=.85, magro=.88, nariz=1.15, sobrancelha=cab)
    hd += cabelo_curto(cab, .97, entradas=.5) + barba(cab, comp=.04, larg=1.0)
    R.rigid(hd, "head")
    return fim(R, INFO)

BASE = {"upper_arm.R": {"y": -30, "x": -6}, "forearm.R": {"bend": -30}, "upper_arm.L": {"y": 32, "x": -6}, "forearm.L": {"bend": -25},
        "head": {"x": -4}}

def anims(R):
    def ex(i, n):  # ergue o rosto para o horizonte, devagar
        k = max(0, wave(i, n))
        return {"head": {"x": -8*k, "z": 10*wave(i, n*.5)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(1, .4), passo=14)
