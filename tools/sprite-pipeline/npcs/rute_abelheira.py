# Rute, que cuida das colmeias da Enxertia (Novo Éden). Moça miúda de chapéu de abas largas com véu de tela (enrolado na aba), macacão
# remendado e um fumigador de latão sempre fumegando na mão. Abelhas pousadas nos ombros como broches. Sem brilho.
from kit import *

INFO = info("eden", tz=.84, escala=.92)

def build():
    R = rig("rute_abelheira")
    skin = pele("ru_pele", (.4, .27, .2), sujo=.3, rubor_amt=.4)
    mac = pano("ru_macacao", (.32, .3, .24), vinco=.5, desbote=.4, remendo=(.15, .12, .08), rem_amt=.3, grime=1.2)
    palha = mat("ru_palha", (.36, .28, .15), 0, .85, dirt=.6)
    tela = pano("ru_tela", (.06, .06, .055), vinco=0, desbote=0, trama=200, mancha_amt=.2)
    lat = latao("ru_latao"); cou = couro("ru_couro", (.12, .07, .035)); fumo = pano("ru_fumo", (.3, .3, .29), vinco=0, desbote=0, mancha_amt=0)
    ab = mat("ru_abelha", (.25, .16, .03), 0, .5); preto = mat("ru_listra", (.02, .02, .02), 0, .5)
    cab = cabelo("ru_cabelo", (.13, .07, .04))
    corpo(R, skin, mac, mac, mangas=mac, botas=couro("ru_bota", (.08, .055, .03)), maos=couro("ru_luva", (.25, .2, .12)), mulher=True, magro=.9, busto=.35)
    # abelhas nos ombros
    bz = []
    rr = random.Random(9)
    for k in range(5):
        sd = 1 if k % 2 else -1; p = Vector((.16*sd + rr.uniform(-.03, .03), rr.uniform(-.06, .04), 1.46 + rr.uniform(-.02, .02)))
        bz.append(prim("primitive_uv_sphere_add", ab, p, (.009, .014, .008), segments=8, ring_count=5))
        bz.append(prim("primitive_torus_add", preto, p, (1, 1, 1), rot=(90, 0, 0), major_radius=.008, minor_radius=.002))
    R.rigid(bz, "chest")
    # fumigador de latão com fole e fumaça saindo
    G = grip(R, "R"); fm = [prim("primitive_cylinder_add", lat, G + Vector((0, -.05, .08)), (.04, .04, .07), vertices=12),
                           along("primitive_cone_add", lat, G + Vector((0, -.05, .15)), G + Vector((.0, -.08, .2)), .04, vertices=10, radius1=1, radius2=.35),
                           prim("primitive_cube_add", cou, G + Vector((0, .03, .05)), (.03, .02, .05))]
    for k in range(4): fm.append(prim("primitive_ico_sphere_add", fumo, G + Vector((.01*k, -.09 - .015*k, .23 + .05*k)), (.02 + .01*k,)*3, subdivisions=2))
    R.rigid(fm, "prop.R")
    hd = cabeca(R, skin, mulher=True, idade=0, queixo=.9, sobrancelha=cab)
    hd += cabelo_curto(cab, 1.0)
    hd += aba_larga(palha, aba=.15, copa=.08)
    # véu de tela enrolado na fita do chapéu (ela levanta para falar)
    hd.append(prim("primitive_cylinder_add", tela, HC + Vector((0, .0, .1)), (.1, .11, .03), vertices=20))
    hd.append(prim("primitive_torus_add", tela, HC + Vector((0, 0, .085)), (1, 1.1, 1), major_radius=.1, minor_radius=.014))
    R.rigid(hd, "head")
    return fim(R, INFO)

BASE = {"upper_arm.R": {"y": -26, "x": -30}, "forearm.R": {"bend": -60}, "aim": {"prop.R": (0, -1, 0)},
        "upper_arm.L": {"y": 32, "x": -2}, "forearm.L": {"bend": -20}, "head": {"x": 3}}

def anims(R):
    def ex(i, n): return {"forearm.R": {"bend": 6*wave(i, n)}, "head": {"z": 6*wave(i, n*.5)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(1, 0), passo=19)
