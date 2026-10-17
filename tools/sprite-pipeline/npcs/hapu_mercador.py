# Hapu, Mercador das Docas de Mênfis (Egito). Vendia antiguidade falsa para turista antes do Juízo; agora vende
# antiguidade verdadeira e pão. Homem gordo de barba trançada (anéis de cobre), galabia listrada, avental de couro
# cheio de bolsos e ferramentas de avaliador, óculos de solda pendurados no pescoço, turbante. Debaixo do braço,
# uma estatueta de gato de bronze embrulhada em papiro encerado; na mão, um pão redondo. Sem brilho.
from kit import *

INFO = info("egito", tz=.9)

def build():
    R = rig("hapu_mercador")
    skin = pele("hp_pele", (.25, .15, .09), sujo=.45, rubor_amt=.3)
    gal = pano("hp_galabia", (.32, .27, .18), listra=(.18, .12, .08), listra_per=.035, vinco=.45, desbote=.3, grime=1.1)
    cou = couro("hp_avental", (.14, .075, .035), rachado=.6)
    turb = pano("hp_turbante", (.38, .34, .27), vinco=.5, mancha_amt=.5)
    br = bronze("hp_bronze", (.38, .24, .1), amount=.5); cob = cobre("hp_cobre"); lat = latao("hp_latao")
    pap = pano("hp_papiro", (.4, .33, .2), vinco=.2, trama=40, mancha_amt=.5)
    pao = pele("hp_pao", (.4, .24, .1), sujo=.2, rubor=(.2, .1, .04), rubor_amt=.5, rough=.8)
    cab = cabelo("hp_barba", (.04, .03, .025), grisalho=.15)
    corpo(R, skin, gal, gal, mangas=gal, maos=skin, massa=1.06, barriga=1.0, larg=1.05, descalco=True, punho=1.4, manga_r=1.15)
    aba(R, gal, z0=1.05, z1=.1, aberto=0, rodado=.9, jag=.03, seed=4, folds=10, famp=.04)
    avental(R, cou, z1=.55, w0=.17, w1=.19, y=-.19, curva=.06, seed=3, tiras=cou)
    bl = []
    for k, x in enumerate((-.1, -.03, .05, .11)):
        bl.append(prim("primitive_cube_add", cou, (x, -.22, .82 + .04*(k % 2)), (.03, .012, .04)))
    bl.append(along("primitive_cylinder_add", lat, (-.1, -.235, .86), (-.1, -.24, .93), .005, vertices=6))
    bl.append(along("primitive_cylinder_add", br, (.05, -.235, .88), (.06, -.24, .95), .008, vertices=6))
    R.rigid(bl, "hips")
    for n in "LR":
        R.rigid([prim("primitive_cube_add", cou, R.P(f"foot.{n}") + Vector((0, -.05, -.077)), (.045, .1, .008))], f"foot.{n}")
    # estatueta de gato embrulhada debaixo do braço esquerdo, pão na direita
    o_, ax, u, sd_ = R.frame("upper_arm.L")
    R.rigid([prim("primitive_uv_sphere_add", pap, o_ + ax*.15 - u*.12, (.06, .09, .05), segments=10, ring_count=8),
             along("primitive_cone_add", br, o_ + ax*.15 - u*.17 + Vector((0, 0, .02)), o_ + ax*.15 - u*.2 + Vector((0, 0, .1)), .035, vertices=8, radius1=1, radius2=.4)], "upper_arm.L")
    G = grip(R, "R"); R.rigid([prim("primitive_uv_sphere_add", pao, G + Vector((0, -.05, .02)), (.07, .07, .035), segments=12, ring_count=8)], "prop.R")
    # cabeça: rosto redondo, barba trançada com anéis, turbante, óculos de solda no pescoço
    hd = cabeca(R, skin, idade=.45, queixo=1.2, nariz=1.2, sobrancelha=cab)
    hd.append(prim("primitive_uv_sphere_add", skin, HC + Vector((0, -.05, -.115)), (.07, .05, .035), segments=12, ring_count=8))
    hd += barba(cab, comp=.16, larg=1.1, trancada=True, fio=cob)
    hd.append(prim("primitive_uv_sphere_add", turb, HC + Vector((0, .01, .05)), (.1, .11, .075), segments=16, ring_count=10))
    for k in range(3): hd.append(prim("primitive_torus_add", turb, HC + Vector((0, .01, .03 + .025*k)), (1, 1.1, 1), rot=(8 - 8*k, 0, 0), major_radius=.092 - .006*k, minor_radius=.016))
    R.rigid(hd, "head")
    lente = vidro("hp_lente", (.05, .12, .1))
    oc = []
    for sd in (1, -1):
        oc.append(along("primitive_cylinder_add", lat, Vector((.035*sd, -.12, 1.45)), Vector((.035*sd, -.14, 1.44)), .022, vertices=12))
        oc.append(along("primitive_cylinder_add", lente, Vector((.035*sd, -.139, 1.44)), Vector((.035*sd, -.143, 1.44)), .017, vertices=12))
    oc.append(prim("primitive_torus_add", cou, (0, -.03, 1.47), (1, 1.2, 1), rot=(-25, 0, 0), major_radius=.08, minor_radius=.006))
    R.rigid(oc, "chest")
    return fim(R, INFO)

BASE = {"upper_arm.L": {"y": 26, "x": -8}, "forearm.L": {"bend": -70}, "upper_arm.R": {"y": -24, "x": -36}, "forearm.R": {"bend": -80},
        "hand.R": {"x": -15}, "head": {"z": 8}}

def anims(R):
    def ex(i, n):  # oferece o pão balançando, ri sacudindo a barriga
        return {"forearm.R": {"bend": 8*wave(i, n)}, "spine": {"x": 2*wave(i, n*.5)}, "head": {"x": 3*wave(i, n*.5)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, .3), passo=14)
