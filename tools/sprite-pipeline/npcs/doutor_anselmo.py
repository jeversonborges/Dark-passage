# Anselmo Graxa, Doutor e Guardião da Vela. Ex-pároco de São Lázaro que desmontou o motor de um bonde e acendeu a
# primeira Vela. Gordo e careca, batina preta cortada no joelho com o colarinho romano encardido, avental de couro
# de oficina por cima, óculos de soldador na testa, bobina de tesla nas costas (os fios ralos da careca ficam em pé
# com a estática). Na mão esquerda o contador de Amargo: um terço de contas de vidro que ele ergue para ouvir
# estalar. Único brilho: o arco azul na ponta da bobina.
from kit import *

INFO = info("vigilia", tz=.9)

def build():
    R = rig("doutor_anselmo")
    skin = pele("an_pele", (.42, .28, .21), sujo=.45, rubor_amt=.4)
    batina = pano("an_batina", (.035, .033, .032), vinco=.4, desbote=.4, remendo=(.08, .07, .06), rem_amt=.1, grime=1.0)
    calca = pano("an_calca", (.08, .07, .06))
    cou = couro("an_avental", (.15, .085, .04), rachado=.6, gasto=.55)
    bota = couro("an_bota", (.05, .035, .025))
    lat = latao("an_latao"); cob = cobre("an_cobre", (.45, .2, .09), amount=.35); fer = ferro("an_ferro")
    branco = pano("an_colarinho", (.5, .48, .42), vinco=.1, desbote=0, mancha_amt=.5, grime=.4)
    cab = cabelo("an_cabelo", (.11, .1, .09), grisalho=.4)
    corpo(R, skin, batina, calca, botas=bota, maos=skin, massa=1.06, barriga=.9, larg=1.05, punho=1.25, manga_r=1.1)
    aba(R, batina, z1=.5, aberto=0.0, rodado=1.05, jag=.03, seed=3, folds=8, famp=.05)
    # colarinho romano encardido
    R.rigid([prim("primitive_cylinder_add", batina, (0, -.008, 1.5), (.07, .066, .03), vertices=20),
             prim("primitive_cube_add", branco, (0, -.072, 1.505), (.018, .006, .014))], "chest")
    avental(R, cou, z1=.62, w0=.16, w1=.19, y=-.165, curva=.05, seed=4, tiras=cou)
    R.rigid([prim("primitive_cube_add", cou, (.07, -.2, .95), (.05, .012, .045)),          # bolso com ferramentas
             along("primitive_cylinder_add", fer, (.05, -.21, .98), (.045, -.215, 1.06), .006, vertices=6),
             along("primitive_cylinder_add", cob, (.085, -.21, .98), (.09, -.214, 1.04), .008, vertices=6)], "hips")
    # bobina de tesla nas costas: alças de couro, base de latão, enrolamento de cobre, toroide e o arco azul
    tb = []
    base = Vector((0, .2, 1.18))
    tb.append(prim("primitive_cylinder_add", lat, base, (.07, .07, .03), vertices=16))
    tb.append(prim("primitive_cylinder_add", cob, base + Vector((0, 0, .17)), (.045, .045, .14), vertices=16))
    for k in range(9):
        tb.append(prim("primitive_torus_add", cob, base + Vector((0, 0, .05 + .028*k)), (1, 1, 1), major_radius=.047,
                       minor_radius=.006, major_segments=14, minor_segments=4))
    tb.append(prim("primitive_torus_add", fer, base + Vector((0, 0, .34)), (1, 1, .55), major_radius=.065, minor_radius=.028,
                   major_segments=18, minor_segments=8))
    arco = glow("an_arco", (.45, .75, 1.0), 5.0)
    rr = random.Random(4); p = base + Vector((.03, 0, .37))
    for k in range(5):
        q = p + Vector((rr.uniform(.0, .05), rr.uniform(-.03, .03), rr.uniform(.02, .05)))
        tb.append(along("primitive_cylinder_add", arco, p, q, .0045, vertices=4)); p = q
    for sd in (1, -1):
        tb += tira(cou, [Vector((.12*sd, -.06, 1.46)), Vector((.13*sd, .08, 1.47)), Vector((.08*sd, .17, 1.28)), Vector((.06*sd, .17, 1.12))], w=.035, t=.008)
    R.rigid(tb, "chest")
    # contador de Amargo: terço de contas de vidro verde e cruz de latão, pendurado da mão esquerda
    vd = vidro("an_contas", (.12, .3, .12))
    G = grip(R, "L"); tc = []
    for k in range(9):
        a = k/9*2*math.pi
        tc.append(prim("primitive_uv_sphere_add", vd, G + Vector((.03*math.sin(a), -.02, -.05 - .06*(1 - math.cos(a)))), (.009,)*3,
                       segments=8, ring_count=5))
    tc.append(along("primitive_cube_add", lat, G + Vector((0, -.02, -.17)), G + Vector((0, -.02, -.23)), .006))
    tc.append(along("primitive_cube_add", lat, G + Vector((-.018, -.02, -.19)), G + Vector((.018, -.02, -.19)), .006))
    R.rigid(tc, "prop.L")
    # cabeça: careca suada, fios em pé, óculos de soldador na testa, papada
    hd = cabeca(R, skin, idade=.6, queixo=1.15, nariz=1.1, sobrancelha=cab)
    hd.append(prim("primitive_uv_sphere_add", skin, HC + Vector((0, -.05, -.115)), (.07, .05, .035), segments=12, ring_count=8))  # papada
    hd += careca(cab, coroa=.016) + fios_em_pe(cab, 9, .045)
    lente = vidro("an_lente", (.05, .12, .1))
    for sd in (1, -1):
        hd.append(along("primitive_cylinder_add", lat, HC + Vector((.035*sd, -.085, .06)), HC + Vector((.035*sd, -.115, .07)), .026, vertices=12))
        hd.append(along("primitive_cylinder_add", lente, HC + Vector((.035*sd, -.114, .07)), HC + Vector((.035*sd, -.118, .071)), .02, vertices=12))
    hd.append(prim("primitive_torus_add", cou, HC + Vector((0, -.005, .055)), (1, 1.12, 1.6), major_radius=.09, minor_radius=.008, rot=(-10, 0, 0)))
    R.rigid(hd, "head")
    return fim(R, INFO)

# ergue o terço na altura do rosto para ouvir as contas; a direita apoiada na barriga
BASE = {"upper_arm.L": {"y": 34, "x": -52}, "forearm.L": {"bend": -118}, "hand.L": {"x": -20},
        "upper_arm.R": {"y": -26, "x": -18}, "forearm.R": {"bend": -55}, "head": {"z": 14, "x": 4}, "chest": {"x": -3}}

def anims(R):
    def ex(i, n):  # sacode o terço de leve e inclina a cabeça ouvindo
        return {"hand.L": {"z": 10*wave(i, n, ph=.5)}, "head": {"y": 5*wave(i, n)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.2, .5), passo=15)
