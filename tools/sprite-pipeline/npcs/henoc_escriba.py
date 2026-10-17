# Henoc, Escriba do Bosque (Monte Hermon). Homem muito velho sem idade certa, batina cinza de lã grossa, dedos pretos de
# tinta, um diadema de bronze guardado numa caixa ao lado. Escreve o tempo todo: livro aberto apoiado no braço, pena na
# mão. Sem brilho.
from kit import *

INFO = info("hermon", tz=.9)

def build():
    R = rig("henoc_escriba")
    skin = pele("he_pele", (.36, .27, .21), sujo=.35, marcas=(.2, .14, .1), marcas_amt=.4)
    la = pano("he_batina", (.13, .125, .115), vinco=.5, desbote=.3, remendo=(.08, .075, .07), rem_amt=.15, grime=1.2, trama=60)
    tinta = mat("he_tinta", (.015, .015, .02), 0, .4)
    cou = couro("he_couro", (.1, .06, .03)); br = bronze("he_bronze"); mad = madeira("he_caixa", (.13, .08, .04))
    papel = pano("he_papel", (.45, .4, .3), trama=30, mancha=(.05, .04, .03), mancha_amt=.6)
    barb = cabelo("he_barba", (.6, .58, .54), grisalho=1, fios=150)
    corpo(R, skin, la, la, mangas=la, maos=tinta, magro=.85, descalco=True, corcunda=.4, manga_r=1.2)
    aba(R, la, z0=1.05, z1=.05, aberto=0, rodado=1.0, jag=.05, seed=14, folds=14, famp=.03)
    R.rigid([prim("primitive_torus_add", couro("he_corda", (.2, .16, .1)), (0, 0, 1.02), (1, .85, 1.3), major_radius=.15, minor_radius=.012)], "hips")
    # caixa do diadema pendurada do cinto
    R.rigid([prim("primitive_cube_add", mad, (.17, -.02, .88), (.05, .05, .035)), prim("primitive_torus_add", br, (.17, -.02, .925), (1, 1, .4), major_radius=.035, minor_radius=.006)], "hips")
    G = grip(R, "L"); R.rigid([prim("primitive_cube_add", cou, G + Vector((0, -.1, .02)), (.13, .1, .012)), prim("primitive_cube_add", papel, G + Vector((0, -.1, .033)), (.12, .09, .006))], "prop.L")
    G = grip(R, "R"); R.rigid([along("primitive_cone_add", pano("he_pena", (.4, .38, .34), vinco=.1), G + Vector((0, .02, 0)), G + Vector((0, -.16, .0)), .014, vertices=6, radius1=.2, radius2=1)], "prop.R")
    hd = cabeca(R, skin, idade=1.0, magro=.85, nariz=1.15, queixo=.95, sobrancelha=barb)
    hd += barba(barb, comp=.3, larg=1.0)
    hd += cabelo_longo(barb, comp=.2, volume=.9)
    R.rigid(hd, "head")
    return fim(R, INFO)

BASE = {"upper_arm.L": {"y": 22, "x": -40}, "forearm.L": {"bend": -80}, "aim": {"prop.L": (0, -.2, 1)},
        "upper_arm.R": {"y": -22, "x": -36}, "forearm.R": {"bend": -100}, "head": {"x": 18}}

def anims(R):
    def ex(i, n): return {"hand.R": {"z": 12*wave(i, n*.25), "x": 6*wave(i, n*.5)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 0), passo=11)
