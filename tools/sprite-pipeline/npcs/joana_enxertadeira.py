# Joana, Mestra da Enxertia (Viveiro do Novo Éden). Mulher de uns cinquenta anos, magra e queimada de sol, avental de
# lona cheio de bolsos com canivetes de enxertia, cintas de latão enroladas no antebraço como pulseiras, luvas de couro
# furadas nos dedos. Uma campânula de vidro presa às costas com uma muda dentro. Segura um galho para enxertar. Sem brilho.
from kit import *

INFO = info("eden", tz=.9)

def build():
    R = rig("joana_enxertadeira")
    skin = pele("jo_pele", (.33, .2, .13), sujo=.45, marcas=(.2, .12, .07), marcas_amt=.4)
    camisa = pano("jo_camisa", (.2, .19, .15), vinco=.45, desbote=.4, grime=1.2)
    calca = pano("jo_calca", (.12, .11, .08), vinco=.4, remendo=(.15, .12, .07), rem_amt=.15)
    lona = pano("jo_avental", (.25, .22, .15), vinco=.5, mancha=(.08, .06, .03), mancha_amt=.7, grime=1.4)
    luva = couro("jo_luva", (.14, .09, .05), rachado=.6); lat = latao("jo_latao"); fer = ferro("jo_ferro")
    vd = vidro("jo_campanula", (.12, .16, .12)); folha = pano("jo_folha", (.08, .16, .05), vinco=.2, desbote=.2, mancha_amt=.3)
    terra = mat("jo_terra", (.07, .05, .03), 0, .95); galho = madeira("jo_galho", (.18, .12, .06))
    cab = cabelo("jo_cabelo", (.2, .17, .14), grisalho=.5)
    corpo(R, skin, camisa, calca, mangas=camisa, botas=couro("jo_bota", (.07, .05, .03)), maos=luva, mulher=True, magro=.9, busto=.35)
    avental(R, lona, z0=1.25, z1=.5, w0=.14, w1=.18, y=-.13, curva=.04, seed=18, tiras=couro("jo_tira", (.12, .08, .04)))
    bl = []
    for x in (-.1, -.03, .05, .11):
        bl.append(prim("primitive_cube_add", lona, (x, -.16, .82), (.03, .01, .04)))
        bl.append(along("primitive_cube_add", fer, (x, -.165, .86), (x, -.165, .9), .006))
    R.rigid(bl, "hips")
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"forearm.{n}")
        R.rigid([prim("primitive_torus_add", lat, o_ + ax*(.08 + .03*k), (1, 1, 1), rot=(90, 0, 0), major_radius=.045, minor_radius=.004) for k in range(4)], f"forearm.{n}")
    # campânula nas costas com a muda
    C = Vector((0, .2, 1.26)); cp = [prim("primitive_uv_sphere_add", vd, C, (.11, .11, .15), segments=16, ring_count=10),
                                     prim("primitive_cylinder_add", lat, C + Vector((0, 0, -.12)), (.11, .11, .015), vertices=16),
                                     prim("primitive_cylinder_add", terra, C + Vector((0, 0, -.1)), (.09, .09, .02), vertices=12),
                                     along("primitive_cylinder_add", galho, C + Vector((0, 0, -.09)), C + Vector((0, 0, .05)), .006, vertices=5)]
    for k in range(5):
        a = k*1.3; cp.append(prim("primitive_uv_sphere_add", folha, C + Vector((.035*math.cos(a), .035*math.sin(a), -.02 + .025*k)), (.03, .012, .02), segments=8, ring_count=5, rot=(0, 0, a*57)))
    cp += tira(couro("jo_alca", (.1, .06, .03)), [Vector((.12, -.05, 1.45)), Vector((.12, .14, 1.42)), Vector((.09, .2, 1.2))], w=.025, t=.005)
    cp += tira(couro("jo_alca2", (.1, .06, .03)), [Vector((-.12, -.05, 1.45)), Vector((-.12, .14, 1.42)), Vector((-.09, .2, 1.2))], w=.025, t=.005)
    R.rigid(cp, "chest")
    G = grip(R, "L"); gl = [along("primitive_cylinder_add", galho, G + Vector((0, .05, 0)), G + Vector((0, -.3, 0)), .008, vertices=6)]
    for k in range(3): gl.append(prim("primitive_uv_sphere_add", folha, G + Vector((.02*(-1)**k, -.15 - .05*k, .01)), (.025, .01, .015), segments=8, ring_count=5))
    R.rigid(gl, "prop.L")
    G = grip(R, "R"); R.rigid([along("primitive_cube_add", fer, G + Vector((0, 0, 0)), G + Vector((0, -.07, 0)), .007)], "prop.R")
    hd = cabeca(R, skin, mulher=True, idade=.55, magro=.9, sobrancelha=cab)
    hd += cabelo_curto(cab, 1.0) + lenco(pano("jo_lenco", (.15, .13, .08)), no_=True)
    R.rigid(hd, "head")
    return fim(R, INFO)

BASE = {"upper_arm.L": {"y": 24, "x": -40}, "forearm.L": {"bend": -70}, "aim": {"prop.L": (.6, -.6, .4)},
        "upper_arm.R": {"y": -24, "x": -40}, "forearm.R": {"bend": -78}, "aim2": None, "head": {"x": 14}}
BASE.pop("aim2")

def anims(R):
    def ex(i, n): return {"hand.R": {"z": 10*wave(i, n*.5)}, "head": {"z": 3*wave(i, n)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 0), passo=16)
