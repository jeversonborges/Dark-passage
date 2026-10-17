# Abdu, o Reis da Escavação (Egito). Capataz de escavação há cinco gerações, desde os ingleses. Homem baixo e largo,
# galabia listrada amarrada na cintura, bengala de capataz com ponta de latão, caderno de contas preso ao cinto por uma
# corrente, turbante de pano. Grita, conta, paga em dia. Aponta a bengala para a escavação. Sem brilho.
from kit import *

INFO = info("egito", tz=.86, escala=.94)

def build():
    R = rig("reis_abdu")
    skin = pele("ab_pele", (.24, .14, .08), sujo=.45, rubor_amt=.3)
    gal = pano("ab_galabia", (.3, .26, .19), listra=(.12, .09, .07), listra_per=.03, vinco=.5, desbote=.3, grime=1.3)
    turb = pano("ab_turbante", (.33, .3, .24), vinco=.5, mancha_amt=.6)
    faixa = pano("ab_faixa", (.18, .07, .04), vinco=.3)
    cou = couro("ab_couro", (.13, .075, .035)); lat = latao("ab_latao"); fer = ferro("ab_ferro")
    mad = madeira("ab_bengala", (.12, .07, .035)); papel = pano("ab_caderno", (.38, .33, .22), trama=40)
    cab = cabelo("ab_bigode", (.04, .035, .03), grisalho=.3)
    corpo(R, skin, gal, gal, mangas=gal, botas=couro("ab_bota", (.07, .045, .03)), maos=skin, massa=1.12, larg=1.15, barriga=.6, punho=1.3, manga_r=1.1, perna_r=1.1)
    aba(R, gal, z0=1.05, z1=.42, aberto=.25, rodado=.95, jag=.04, seed=6, folds=10, famp=.04)
    R.rigid([prim("primitive_torus_add", faixa, (0, 0, 1.0), (1, .85, 1.6), major_radius=.18, minor_radius=.022)]
            + tira(faixa, [Vector((.12, -.12, .99)), Vector((.15, -.13, .84))], w=.035, t=.006), "hips")
    # caderno de contas na corrente
    cd = [prim("primitive_cube_add", cou, (-.16, -.1, .86), (.05, .012, .07)), prim("primitive_cube_add", papel, (-.16, -.112, .86), (.045, .004, .065))]
    cd += chain_links(fer, [(-.12, -.12, .99), (-.14, -.13, .95), (-.16, -.12, .93)], r=.009, thick=.003)
    R.rigid(cd, "hips")
    G = grip(R, "R"); R.rigid([along("primitive_cylinder_add", mad, G + Vector((0, .08, 0)), G + Vector((0, -.85, 0)), .014, vertices=8),
                              along("primitive_cone_add", lat, G + Vector((0, -.85, 0)), G + Vector((0, -.93, 0)), .016, vertices=8, radius1=1, radius2=.3),
                              prim("primitive_uv_sphere_add", lat, G + Vector((0, .1, 0)), (.022,)*3, segments=8, ring_count=6)], "prop.R")
    hd = cabeca(R, skin, idade=.55, queixo=1.2, nariz=1.25, sobrancelha=cab)
    hd += barba(cab, comp=.02, larg=1.1, bigode=True)
    hd.append(prim("primitive_uv_sphere_add", turb, HC + Vector((0, .01, .05)), (.1, .11, .07), segments=16, ring_count=10))
    for k in range(3): hd.append(prim("primitive_torus_add", turb, HC + Vector((0, .01, .03 + .022*k)), (1, 1.1, 1), rot=(8 - 8*k, 0, 0), major_radius=.092 - .006*k, minor_radius=.015))
    R.rigid(hd, "head")
    return fim(R, INFO)

# aponta a bengala para a frente (para a escavação); esquerda na cintura
BASE = {"upper_arm.R": {"y": -18, "x": -55}, "forearm.R": {"bend": -15}, "aim": {"prop.R": (0, -.55, -.85)},
        "upper_arm.L": {"y": 46, "x": 10, "z": -10}, "forearm.L": {"bend": -100}, "chest": {"x": 2}, "head": {"x": -4}}

def anims(R):
    def ex(i, n):  # sacode a bengala gritando ordens
        return {"upper_arm.R": {"x": -6*wave(i, n*.5)}, "head": {"z": 8*wave(i, n), "x": -2*wave(i, n*.5)}}
    def wk(i, n): return {"upper_arm.R": {"x": 40}, "aim": {"prop.R": (0, -.2, -1)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 0), passo=17, walk_extra=wk)
