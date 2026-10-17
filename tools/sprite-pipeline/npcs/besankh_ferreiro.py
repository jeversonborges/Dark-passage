# Besankh, Fundidor de Bronze (Menfis, Egito). Era cantor de casamento em Gizé; o Amargo deixou o corpo largo e a voz
# rouca e ele trocou a música pelo martelo. Mutante enorme de pele cinza-esverdeada, um braço (o do martelo) mais
# grosso que o outro, avental de couro queimado, saiote de linho. Derrete o bronze das estátuas sem cabeça num forno
# de tijolo de lama. Mesma cena e animação da forja do Gaspar (gaspar_bigorna.py), com bronze no lugar do ferro.
from kit import *

INFO = info("egito", tz=.82, escala=1.14, px=272, fps_idle=8, fps_walk=8)
GOLPE = 3          # quadro do idle em que o martelo bate (faíscas e som)
BIG = Vector((-.04, -.5, 0))   # pé da bigorna
TOPO = BIG + Vector((0, 0, .74))
FX = [f"fx{k}" for k in range(11)]


def build():
    # (mesma cena do Gaspar: ver gaspar_bigorna.py)
    ex = {"bigorna": (tuple(BIG), tuple(BIG + Vector((0, 0, .3))), None)}
    for k in FX: ex[k] = (tuple(TOPO), tuple(TOPO + Vector((0, 0, .05))), None)
    R = rig("besankh_ferreiro", extra=ex)
    R.hidden |= set(FX)
    skin = pele("bk_pele", (.11, .125, .095), sujo=.6, marcas=(.06, .1, .05), marcas_amt=.7, rubor_amt=.05)
    cou = couro("bk_avental", (.1, .055, .03), rachado=.7, gasto=.6)
    calca = pano("bk_linho", (.36, .32, .24), vinco=.5, mancha=(.1, .07, .04), mancha_amt=.6, grime=1.3)
    luva = couro("bk_luva", (.13, .08, .04), rachado=.5)
    bot = couro("bk_bota", (.05, .035, .025))
    fer = ferro("bk_ferro", ferrugem=.55); br = bronze("bk_bronze", (.36, .22, .09), amount=.45)
    cab = cabelo("bk_barba", (.03, .03, .025), grisalho=.1)
    corpo(R, skin, skin, skin, mangas=skin, maos=luva, massa=1.16, larg=1.22, barriga=.5, punho=1.2, descalco=True)
    saiote(R, calca, z1=.55, plisse=False)
    # peitoral e braços musculosos (volumes por cima)
    mus = []
    for sd in (1, -1):
        mus.append(prim("primitive_uv_sphere_add", skin, (.07*sd, -.09, 1.36), (.085, .05, .06), segments=12, ring_count=8))
    R.rigid(mus, "chest")
    for n in "LR":
        a, el = R.P(f"upper_arm.{n}"), R.P(f"forearm.{n}")
        R.bind(skin_mesh(f"bk_biceps{n}", {"a": (*a.lerp(el, .2), .07), "b": (*a.lerp(el, .55), .078), "c": (*el, .06)},
                         [("a", "b"), ("b", "c")], skin, ), [f"upper_arm.{n}", f"forearm.{n}"])
        if n == "R":
            R.rigid([prim("primitive_uv_sphere_add", skin, a.lerp(el, .45) + Vector((0, 0, .01)), (.1, .095, .1), segments=12, ring_count=8)], f"upper_arm.{n}")
        # braçadeira de couro no antebraço
        o_, ax, u, sd_ = R.frame(f"forearm.{n}")
        R.rigid([along("primitive_cylinder_add", luva, o_ + ax*.1, o_ + ax*.22, .064, vertices=14)], f"forearm.{n}")
    avental(R, cou, z1=.4, w0=.18, w1=.21, y=-.15, curva=.06, seed=8, tiras=cou)
    # escaravelho de bronze num cordão (presente de casamento que ele nunca vendeu)
    R.rigid([prim("primitive_uv_sphere_add", br, (0, -.17, 1.33), (.022, .012, .028), segments=10, ring_count=6),
             prim("primitive_torus_add", couro("bk_cordao", (.1, .06, .03)), (0, -.04, 1.42), (1, 1.25, 1), rot=(-30, 0, 0), major_radius=.11, minor_radius=.004)], "chest")
    cinto(R, cou, fivela=fer, z=.97, r=.2)
    # molde de bala pendurado no cinto
    brasa = glow("bk_brasa", (1.0, .45, .12), 4.0)
    R.rigid([prim("primitive_cube_add", fer, (.2, -.03, .88), (.02, .04, .03)),
             along("primitive_cylinder_add", fer, (.2, -.03, .85), (.22, -.04, .7), .007, vertices=6),
             ], "hips")
    # martelo de fundidor: cabo curto de freixo, cabeça feita do badalo de um sino
    mad = madeira("bk_cabo", (.2, .12, .06))
    G = grip(R, "R"); mt = [along("primitive_cylinder_add", mad, G + Vector((0, .08, 0)), G + Vector((0, -.42, 0)), .018, vertices=8)]
    h = G + Vector((0, -.45, 0))
    mt.append(along("primitive_cylinder_add", br, h + Vector((-.08, 0, 0)), h + Vector((.09, 0, 0)), .045, vertices=14))
    mt.append(prim("primitive_uv_sphere_add", br, h + Vector((-.09, 0, 0)), (.028, .052, .052), segments=10, ring_count=6))
    mt.append(prim("primitive_torus_add", fer, h, (1, 1, 1), rot=(0, 90, 0), major_radius=.049, minor_radius=.008))
    R.rigid(mt, "prop.R")
    # tenaz na esquerda segurando o lingote em brasa
    G = grip(R, "L"); tz_ = [along("primitive_cylinder_add", fer, G + Vector((sd*.008, .06, 0)), G + Vector((sd*.004, -.4, 0)), .007, vertices=6) for sd in (1, -1)]
    tz_.append(prim("primitive_cube_add", brasa, G + Vector((0, -.44, 0)), (.03, .05, .016)))
    R.rigid(tz_, "prop.L")
    # bigorna (contrapeso de bonde) sobre um toco, fogareiro de tijolo com fole, balde de têmpera
    tij = stained("bk_tijolo", (.2, .14, .08), stain=(.05, .03, .02), amount=.6, scale=9, rough=.9, blotch=(.08, .05, .03), blotch_amt=.6, grime=.9)
    toco = madeira("bk_toco", (.14, .08, .04))
    bg = [prim("primitive_cylinder_add", toco, BIG + Vector((0, 0, .22)), (.17, .17, .22), vertices=14),
          prim("primitive_cube_add", fer, BIG + Vector((0, 0, .5)), (.07, .13, .06)),
          prim("primitive_cube_add", fer, BIG + Vector((0, 0, .6)), (.05, .1, .05)),
          prim("primitive_cube_add", fer, TOPO + Vector((0, .02, -.04)), (.085, .2, .04)),
          along("primitive_cone_add", fer, TOPO + Vector((0, -.18, -.035)), TOPO + Vector((0, -.36, -.03)), .04, vertices=8, radius1=1, radius2=.1)]
    for sd in (1, -1):  # cintas de ferro no toco
        bg.append(prim("primitive_torus_add", fer, BIG + Vector((0, 0, .1 + .22*(sd > 0))), (1, 1, 1), major_radius=.172, minor_radius=.008))
    F = Vector((.66, .22, 0))   # fogareiro ao lado esquerdo dele, um pouco atrás
    bg.append(prim("primitive_cube_add", tij, F + Vector((0, 0, .3)), (.26, .22, .3)))
    bg.append(prim("primitive_cube_add", tij, F + Vector((0, .2, .62)), (.26, .04, .1)))
    carvao = mat("bk_carvao", (.02, .018, .016), 0, .9)
    for k in range(22):
        rr = random.Random(k)
        bg.append(prim("primitive_ico_sphere_add", brasa if k % 4 == 0 else carvao, F + Vector((rr.uniform(-.19, .19), rr.uniform(-.16, .12), .6 + rr.uniform(0, .02))),
                       (.022 if k % 4 == 0 else .032,)*3, subdivisions=1))
    fole = couro("bk_fole", (.12, .07, .035), rachado=.5)
    bg.append(prim("primitive_uv_sphere_add", fole, F + Vector((.36, .05, .35)), (.12, .16, .07), segments=12, ring_count=8))
    bg.append(along("primitive_cylinder_add", toco, F + Vector((.36, .2, .35)), F + Vector((.36, .38, .38)), .015, vertices=6))
    bg.append(along("primitive_cylinder_add", fer, F + Vector((.3, -.08, .33)), F + Vector((.24, -.1, .3)), .02, vertices=6))
    Bd = BIG + Vector((-.5, -.08, 0))
    agua = vidro("bk_agua", (.04, .05, .04))
    bg += [prim("primitive_cylinder_add", toco, Bd + Vector((0, 0, .17)), (.15, .15, .17), vertices=14),
           prim("primitive_cylinder_add", agua, Bd + Vector((0, 0, .3)), (.135, .135, .01), vertices=14)]
    for z in (.05, .29): bg.append(prim("primitive_torus_add", fer, Bd + Vector((0, 0, z)), (1, 1, 1), major_radius=.152, minor_radius=.007))
    R.rigid(bg, "bigorna")
    # faíscas: riscos de brasa em ossos soltos que só aparecem depois do golpe
    rr = random.Random(11)
    for k in FX:
        fx = []
        for j in range(4):
            p = TOPO + Vector((rr.uniform(-.05, .05), rr.uniform(-.05, .05), .02))
            d = Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(.2, 1))).normalized()*rr.uniform(.035, .06)
            fx.append(along("primitive_cube_add", brasa, p, p + d, .006))
        R.rigid(fx, k)
    # luz quente do fogareiro (pulsa e clareia no golpe)
    ld = bpy.data.lights.new("bk_luz", 'POINT'); ld.color = (1, .5, .2); ld.shadow_soft_size = .15; ld.energy = 22
    lo = bpy.data.objects.new("bk_luz", ld); bpy.context.scene.collection.objects.link(lo)
    lo.parent = R.arm; lo.location = F + Vector((-.15, -.2, .95)); R.lamps.append((ld, 22))
    # cabeça: cara quadrada, nariz quebrado, barba cheia e longa, cabelo raspado nas laterais, queimadura na têmpora
    hd = cabeca(R, skin, idade=.55, queixo=1.25, nariz=1.25, sobrancelha=cab, esc=1.04)
    hd += barba(cab, comp=.05, larg=1.1)
    hd += careca(cab, coroa=.0)
    R.rigid(hd, "head")
    return fim(R, INFO)

# forja: tenaz na esquerda segura o lingote na bigorna, direita sobe o martelo e desce no GOLPE
BASE = {"upper_arm.L": {"x": -2, "y": 36, "z": -30}, "forearm.L": {"bend": -38}, "aim": {"prop.L": (-.4, -.6, -.5)},
        "upper_arm.R": {"y": -22, "x": -40}, "forearm.R": {"bend": -60}, "spine": {"x": -6}, "chest": {"x": -8}, "head": {"x": 14},
        "thigh.L": {"x": -6}, "thigh.R": {"x": 6}}
# (braço x, y, z, antebraço bend: somados ao BASE pelo merge; direção do martelo) por quadro: sobe 0-2, desce 3 (golpe), quica e volta 4-7.
# Mãos medidas no rig: golpe com a mão em (-.07, -.29, 1.07), cabeça do martelo no lingote; topo em (-.2, -.06, 1.85).
CICLO = [(10, -25, 0, -30, (0, -.2, .9)), (-30, -20, 0, -35, (0, .3, 1)), (-60, -20, 0, -30, (0, .45, .9)),
         (40, -20, 30, 0, (0, -.55, -.8)), (36, -20, 22, -8, (0, -.42, -.9)), (32, -22, 12, -18, (0, -.2, -1)),
         (26, -25, 4, -25, (0, -.05, -1)), (20, -25, 0, -30, (0, -.6, .1))]
TENAZ = (-.4, -.6, -.5)
SPARK = {GOLPE: 0, GOLPE + 1: 1, GOLPE + 2: 2}   # quadro -> idade da faísca

def anims(R):
    rr = random.Random(5); vel = [Vector((rr.uniform(-1, 1), rr.uniform(-1, .4), rr.uniform(.5, 1.4))) for _ in FX]
    idle = []
    for i, (ax, ay, az, fb, hd) in enumerate(CICLO):
        p = merge(BASE, {"upper_arm.R": {"x": ax, "y": ay, "z": az}, "forearm.R": {"bend": fb}, "aim": {"prop.R": hd, "prop.L": TENAZ},
                         "chest": {"x": -8 - 4*(i == GOLPE), "z": -6 if i in (1, 2) else 0}, "spine": {"z": -4 if i in (1, 2) else 2},
                         "head": {"x": 14 + 4*(i == GOLPE)}})
        p["lamp"] = {"v": 1.35 if i == GOLPE else (1.1 if i == GOLPE + 1 else .9 + .1*wave(i, len(CICLO)))}
        a = SPARK.get(i)
        for k, v in zip(FX, vel):
            if a is None: p[k] = {"vis": 0}
            else:
                t = .1 + .17*a
                p[k] = {"vis": max(.35, 1 - .3*a), "lx": v.x*.9*t, "ly": v.y*.9*t, "lz": v.z*1.3*t - 1.8*t*t}
        idle.append(p)
    return {"idle": idle, "walk": idle}
