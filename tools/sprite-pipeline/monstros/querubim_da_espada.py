# Querubim da Espada (Novo Éden, nível 18-22): "pôs querubins ao oriente do jardim do Éden, e uma espada
# flamejante que andava ao redor" (Gn 3:24). Sentinela que o Coro deixou no Portão do Oriente e nunca mais chamou.
# Anjo adulto, alto e seco, de sobretudo de couro de guarda até o joelho com a sobrepeliz branca rasgada por cima,
# peitoral de bronze com rosto de leão em relevo, grevas de bronze nos pés descalços. O rosto é uma máscara de
# bronze lisa cravejada de olhos ("cheios de olhos ao redor", Ez 10:12): só os olhos acendem. Quatro asas: duas
# grandes de penas sujas abertas nas costas, duas pequenas cruzadas sobre o peito (Is 6:2, "com duas cobria o
# rosto"). A espada: lâmina de bronze de 1,4 m que queima sem se consumir, fogo laranja.
# Brilho: laranja-fogo (lâmina, olhos da máscara). Anda no chão; territorial, patrulha a Estrada da Torre.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Quaternion
from mrig import *
from corvo_de_cinza import feathers, wings

INFO = {"px": 256, "target_z": 1.05, "rim": (1, .55, .2), "colors": 44, "samples": 40,
        "fps": {"idle": 6, "walk": 10, "attack": 12, "hit": 12, "death": 10}, "loops": ("idle", "walk")}

VARIANTS = {"querubim_da_espada": {}}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
set_variant("querubim_da_espada")

B = humanoid(1.08, 1.0)
for s, n in ((1, "L"), (-1, "R")):
    B[f"wing1.{n}"] = ((.07*s, .1, 1.42), (.3*s, .14, 1.62), "chest")
    B[f"wing2.{n}"] = ((.3*s, .14, 1.62), (.6*s, .17, 1.76), f"wing1.{n}")
    B[f"wing3.{n}"] = ((.6*s, .17, 1.76), (.9*s, .19, 1.8), f"wing2.{n}")
    B[f"asinha.{n}"] = ((.06*s, -.12, 1.36), (-.12*s, -.2, 1.2), "chest")
B["flame"] = ((0, 0, 0), (0, 0, .1), "hand.R")

def glow(name, rgb, strength):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes):
        if nd.type != 'OUTPUT_MATERIAL': nt.nodes.remove(nd)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*rgb, 1); em.inputs["Strength"].default_value = strength
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = (*rgb, 1)
    lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); nt.links.new(df.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], [nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL'][0].inputs["Surface"])
    return m

def build():
    rnd = random.Random(11)
    skin = stained("qe_pele", (.3, .27, .23), stain=(.12, .06, .04), amount=.3, scale=5, rough=.55, blotch=(.18, .16, .14), blotch_amt=.6, grime=1.0)
    couro = stained("qe_couro", (.08, .055, .035), stain=(.14, .04, .02), amount=.4, scale=4, rough=.65, blotch=(.05, .04, .03), blotch_amt=.6, grime=1.2)
    sobre = stained("qe_sobrepeliz", (.46, .43, .36), stain=(.18, .11, .05), amount=.5, scale=3.5, rough=.95, blotch=(.24, .2, .15), blotch_amt=.6, grime=1.5)
    bronze = stained("qe_bronze", (.42, .27, .1), stain=(.07, .14, .1), amount=.5, scale=7, metal=.9, rough=.5, grime=.3)
    bronze_esc = stained("qe_bronze_escuro", (.2, .13, .05), stain=(.06, .1, .08), amount=.5, scale=9, metal=.85, rough=.6, grime=.3)
    pena = stained("qe_pena", (.38, .36, .32), stain=(.08, .07, .06), amount=.45, scale=6, rough=.85, blotch=(.15, .14, .13), blotch_amt=.6, grime=.3)
    queim = stained("qe_pena_suja", (.07, .065, .06), stain=(.16, .07, .03), amount=.3, scale=9, rough=.9, grime=0)
    corda = mat("qe_corda", (.25, .2, .13), 0, .9, dirt=.5, grime=.3)
    oco = mat("qe_oco", (.012, .01, .01), 0, .9)
    lamina = mat("qe_lamina", (.5, .36, .16), .9, .3, emit=(1, .45, .1), strength=1.2, dirt=.2, grime=.2)
    fogo = glow("qe_fogo", (1, .5, .12), 9)
    fogo2 = glow("qe_fogo_claro", (1, .8, .35), 14)
    olho = glow("qe_olho", (1, .55, .15), 14)

    R = Rig("querubim_espada", B, ground=.03); P = R.P
    R.gexclude = {"flame"}
    # ------------------------------------------------ corpo magro e alto
    j = {"pelvis": (0, 0, 1.02, .12, .095)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .072); j[f"knee{n}"] = (*k, .055); j[f"ank{n}"] = (*a, .04)
        j[f"toe{n}"] = (*(P(f"foot.{n}", 1) + Vector((0, 0, .005))), .042, .025)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"knee{n}"), (f"knee{n}", f"ank{n}"), (f"ank{n}", f"toe{n}")]
    legs = skin_mesh("pernas", j, e, skin); R.bind(legs, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R", "foot.L", "foot.R"])
    t = {"pelvis": (0, 0, 1.05, .13, .095), "waist": (0, 0, 1.22, .11, .085), "chest": (0, 0, 1.44, .16, .105),
         "neck": (0, -.01, 1.62, .045), "neck2": (0, -.015, 1.7, .04)}
    te = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, 0))), .06); t[f"el{n}"] = (*el, .042)
        t[f"fa{n}"] = (*el.lerp(wr, .4), .042); t[f"wr{n}"] = (*wr, .032)
        te += [("chest", f"sh{n}"), (f"sh{n}", f"el{n}"), (f"el{n}", f"fa{n}"), (f"fa{n}", f"wr{n}")]
    torso = skin_mesh("tronco", t, te, skin)
    R.bind(torso, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])
    # grevas de bronze e pés descalços com dedos
    for n in "LR":
        k, a, tp = P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        g = [along("primitive_cylinder_add", bronze_esc, k.lerp(a, .08), k.lerp(a, .7), .062, vertices=10)]
        g[0].scale = (g[0].scale.x, g[0].scale.y*.8, g[0].scale.z)
        g.append(prim("primitive_uv_sphere_add", bronze_esc, k + Vector((0, -.03, -.02)), (.055, .045, .06), segments=10, ring_count=6))
        R.rigid(g, f"shin.{n}")
        dd = []
        for f in range(4):
            b0 = tp + Vector((-.03 + .02*f, .01, 0))
            dd.append(along("primitive_cylinder_add", skin, b0, b0 + Vector((0, -.04, -.005)), .009, vertices=5))
        R.rigid(dd, f"foot.{n}")

    # ------------------------------------------------ sobretudo de couro, sobrepeliz rasgada, peitoral de bronze
    cs = skirt("sobretudo", couro, [(1.6, .11, .09, 0), (1.52, .2, .14, 0), (1.36, .2, .13, .004), (1.15, .17, .12, .01),
                                     (1.0, .19, .13, .015), (.8, .22, .15, .02), (.62, .25, .17, .03)], open_front=.35, jag=.06, seed=3, thick=.012)
    R.bind(cs, ["hips", "spine", "chest", "thigh.L", "thigh.R", "shin.L", "shin.R"], power=3)
    sp_ = skirt("sobrepeliz", sobre, [(1.62, .1, .08, 0), (1.56, .19, .15, 0), (1.42, .2, .16, 0), (1.26, .2, .16, .004),
                                      (1.1, .23, .18, .01), (.98, .25, .2, .016)], jag=.08, seed=8, thick=.007)
    R.bind(sp_, ["hips", "spine", "chest"], power=3)
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        sj = {"a": (*(sh + Vector((-.02*s, 0, 0))), .075), "b": (*el, .06), "c": (*el.lerp(wr, .5), .062)}
        o = skin_mesh(f"manga.{n}", sj, [("a", "b"), ("b", "c")], couro, levels=1)
        R.bind(o, ["chest", f"upper_arm.{n}", f"forearm.{n}"])
        o = skin_mesh(f"manga_s.{n}", {"a": (*(sh + Vector((-.02*s, 0, .01))), .085), "b": (*sh.lerp(el, .55), .08)}, [("a", "b")], sobre, levels=1)
        R.bind(o, ["chest", f"upper_arm.{n}"])
        R.rigid([along("primitive_cylinder_add", bronze_esc, el.lerp(wr, .55), el.lerp(wr, .95), .04, vertices=8)], f"forearm.{n}")
    ch = []
    bp = prim("primitive_uv_sphere_add", bronze, (0, -.035, 1.42), (.165, .12, .17), segments=18, ring_count=10); ch.append(bp)
    # rosto de leão em relevo no peito: juba de gomos, focinho, olhos ocos
    for k in range(10):
        a = 2*math.pi*k/10
        ch.append(prim("primitive_uv_sphere_add", bronze_esc, (.08*math.cos(a), -.148 - .02*abs(math.sin(a)), 1.42 + .08*math.sin(a)), (.025, .012, .025), segments=6, ring_count=4))
    ch.append(prim("primitive_uv_sphere_add", bronze, (0, -.165, 1.41), (.035, .02, .03), segments=8, ring_count=6))
    for s in (1, -1): ch.append(prim("primitive_uv_sphere_add", oco, (.028*s, -.158, 1.445), (.009, .006, .009), segments=6, ring_count=4))
    for s in (1, -1):  # rebites e correias
        for z in (1.5, 1.4, 1.3): ch.append(prim("primitive_uv_sphere_add", bronze_esc, (.13*s, -.11 + .02*abs(1.4 - z), z), (.009, .008, .009), segments=6, ring_count=4))
        ch.append(along("primitive_cylinder_add", couro, (.1*s, -.12, 1.54), (.14*s, .1, 1.5), .012, vertices=6))
    ch.append(prim("primitive_torus_add", couro, (0, 0, 1.1), (1.1, .82, 1), major_radius=.15, minor_radius=.016, major_segments=20, minor_segments=4))
    ch.append(prim("primitive_cube_add", bronze, (0, -.13, 1.1), (.028, .008, .024)))
    # cíngulo de corda com borlas
    for k in range(2):
        p0 = Vector((.07 - .03*k, -.12, 1.1)); p1 = p0 + Vector((.01, -.01, -.2 - .05*k))
        ch.append(along("primitive_cylinder_add", corda, p0, p1, .006, vertices=4))
        ch.append(prim("primitive_uv_sphere_add", corda, p1, (.014, .014, .024), segments=6, ring_count=4))
    # placa das asas nas costas
    ch.append(prim("primitive_cube_add", bronze_esc, (0, .12, 1.44), (.09, .015, .09), rot=(10, 0, 0)))
    R.rigid(ch, "chest")

    # ------------------------------------------------ cabeça: máscara de bronze cheia de olhos, capuz de couro atrás
    hd = [prim("primitive_uv_sphere_add", couro, (0, .015, 1.83), (.1, .105, .115), segments=16, ring_count=10)]
    FZ, FX, FY, FT = 1.82, .092, .12, .055
    hd.append(prim("primitive_uv_sphere_add", bronze, (0, -.06, FZ), (FX, FT, FY), segments=18, ring_count=12))
    hd.append(prim("primitive_torus_add", bronze_esc, (0, -.06, FZ), (FX/.1, FY/.1, 1), major_radius=.1, minor_radius=.007, major_segments=24, minor_segments=4, rot=(90, 0, 0)))
    def surf(x, z, out=0):
        k = 1 - (x/FX)**2 - ((z - FZ)/FY)**2
        return Vector((x, -.06 - FT*math.sqrt(max(0, k)) - out, z))
    eyes = [(0, .06), (-.045, .04), (.045, .04), (-.06, -.01), (.06, -.01), (-.03, -.05), (.03, -.05), (0, -.085), (-.02, .01), (.02, .01)]
    for i, (x, dz) in enumerate(eyes):
        r = .013 if i < 3 else .01
        hd.append(prim("primitive_uv_sphere_add", bronze_esc, surf(x, FZ + dz, .004), (r*1.5, .006, r*1.5), segments=8, ring_count=4))
        hd.append(prim("primitive_uv_sphere_add", olho, surf(x, FZ + dz, .008), (r, .006, r), segments=8, ring_count=4))
    # auréola de bronze quebrada (meio arco) presa na nuca
    hc = Vector((0, .1, 1.98))
    hd.append(along("primitive_cylinder_add", bronze_esc, (0, .09, 1.86), hc + Vector((0, 0, -.03)), .008, vertices=6))
    for k in range(9):
        a = math.pi*.15 + math.pi*.7*k/8; b = math.pi*.15 + math.pi*.7*(k + 1)/8
        hd.append(along("primitive_cylinder_add", bronze, hc + Vector((.16*math.cos(a), 0, .16*math.sin(a) - .1)), hc + Vector((.16*math.cos(b), 0, .16*math.sin(b) - .1)), .011, vertices=6))
    R.rigid(hd, "head")

    # ------------------------------------------------ mãos e a espada flamejante (direita); esquerda aberta
    for s, n in ((1, "L"), (-1, "R")):
        o, ax, u, sd = R.frame(f"hand.{n}")
        g = prim("primitive_uv_sphere_add", skin, o + ax*.04, (.032, .036, .046), segments=10, ring_count=6)
        g.rotation_euler = ax.to_track_quat('Z', 'Y').to_euler(); parts = [g]
        for f in range(4):
            base = o + ax*.07 + sd*(-.022 + .015*f)
            parts.append(along("primitive_cylinder_add", skin, base, base + ax*.05 + u*.02, .008, vertices=5))
        if n == "R":
            hc = o + ax*.05
            parts.append(along("primitive_cylinder_add", couro, hc - u*.1, hc + u*.08, .018, vertices=8))
            parts.append(prim("primitive_uv_sphere_add", bronze, hc - u*.12, (.03, .03, .03), segments=8, ring_count=6))
            # guarda em asas abertas
            for s2 in (1, -1):
                parts.append(along("primitive_cone_add", bronze, hc + u*.09, hc + u*.14 + sd*.13*s2, .02, vertices=6, radius1=1, radius2=.3))
            bl = prim("primitive_cube_add", lamina, hc + u*.72, (1, 1, 1))
            rot_ = Matrix((ax, sd, u)).transposed(); bl.rotation_euler = rot_.to_euler(); bl.scale = (.007, .04, .6); parts.append(bl)
            parts.append(along("primitive_cone_add", lamina, hc + u*1.31, hc + u*1.45, .04, vertices=4, radius1=1, radius2=0))
            parts[-1].scale = (parts[-1].scale.x*.2, parts[-1].scale.y, parts[-1].scale.z)
            parts.append(along("primitive_cylinder_add", bronze_esc, hc + u*.15, hc + u*1.2, .006, vertices=4))   # sulco
        R.rigid(parts, f"hand.{n}")
    # fogo da lâmina: línguas de chama ao longo do gume (osso flame na mão, escala animada)
    o, ax, u, sd = R.frame("hand.R"); hc = o + ax*.05
    fl = []
    for k in range(14):
        tt = .18 + .08*k; side = sd*(.04 + .02*rnd.random())*(1 if k % 2 else -1)
        base = hc + u*tt + side*.5
        L = rnd.uniform(.08, .16) + .04*math.sin(k)
        fl.append(along("primitive_cone_add", fogo, base, base + side*1.4 + u*L + ax*rnd.uniform(-.02, .02), .022, vertices=5, radius1=1, radius2=0))
        if k % 3 == 0: fl.append(along("primitive_cone_add", fogo2, base, base + side*.9 + u*L*.6, .012, vertices=4, radius1=1, radius2=0))
    fl.append(prim("primitive_uv_sphere_add", fogo2, hc + u*1.42, (.03, .03, .05), segments=8, ring_count=6))
    fl.append(along("primitive_cone_add", fogo, hc + u*1.4, hc + u*1.62, .03, vertices=5, radius1=1, radius2=0))
    R.rigid(fl, "flame")

    # ------------------------------------------------ asas grandes de penas (costas) e asinhas cruzadas no peito
    DN = Vector((0, -1, 0))
    for s, n in ((1, "L"), (-1, "R")):
        X = lambda v: Vector((v[0]*s, v[1], v[2]))
        lj = {"a": (*X((.07, .1, 1.42)), .042, .03), "b": (*X((.3, .14, 1.62)), .034, .024), "c": (*X((.6, .17, 1.76)), .026, .018), "d": (*X((.9, .19, 1.8)), .014)}
        le = skin_mesh(f"borda.{n}", lj, [("a", "b"), ("b", "c"), ("c", "d")], pena, levels=1)
        R.bind(le, ["chest", f"wing1.{n}", f"wing2.{n}", f"wing3.{n}"], power=6)
        prim_specs = []
        for i in range(8):
            t = i/7; base = X((.9 - .28*t, .19 - .01*t, 1.8 - .03*t)); ang = math.radians(15 + 65*t)
            prim_specs.append((base + Vector((0, .004*i, 0)), X((math.cos(ang), .12, -math.sin(ang))), DN, (.62 - .1*t)*rnd.uniform(.9, 1.05), .09, rnd.uniform(.65, .85), -.08))
        sec = [(X((.6 - .28*(k + .5)/5, .15 + .002*k, 1.74 - .06*(k + .5)/5)), X((.12, .15, -1)), DN, rnd.uniform(.45, .5), .095, rnd.uniform(.65, .85), -.06) for k in range(5)]
        ter = [(X((.3 - .22*(k + .5)/4, .12 + .002*k, 1.6 - .1*(k + .5)/4)), X((-.05, .15, -1)), DN, rnd.uniform(.36, .42), .09, rnd.uniform(.7, .9), -.05) for k in range(4)]
        cov = {1: [], 2: [], 3: []}
        for k in range(14):
            t = (k + .5)/14; x = .08 + .8*t; bn = 1 if x < .3 else (2 if x < .6 else 3)
            z = 1.42 + (1.8 - 1.42)*min(1, t*1.25)
            cov[bn].append((X((x, .12 + .04*t - .012, z)), X((.08, .1, -1)), DN, rnd.uniform(.16, .2), .08, .9, -.03))
        R.rigid([feathers(f"prim.{n}", prim_specs, pena, queim, rnd), feathers(f"cob3.{n}", cov[3], pena, queim, rnd)], f"wing3.{n}")
        R.rigid([feathers(f"sec.{n}", sec, pena, queim, rnd), feathers(f"cob2.{n}", cov[2], pena, queim, rnd)], f"wing2.{n}")
        R.rigid([feathers(f"ter.{n}", ter, pena, queim, rnd), feathers(f"cob1.{n}", cov[1], pena, queim, rnd)], f"wing1.{n}")
        # asinha cruzada sobre o peito (do ombro ao quadril oposto)
        a0, a1 = P(f"asinha.{n}"), P(f"asinha.{n}", 1); d = (a1 - a0).normalized()
        sm = [(a0 + d*(.05*k) + Vector((0, -.01*k, 0)), d + Vector((.1*s, -.3, -.2)), DN, .14 - .01*k, .055, .85, -.02) for k in range(5)]
        R.rigid([feathers(f"asinha_p.{n}", sm, pena, queim, rnd), along("primitive_cylinder_add", pena, a0, a1, .016, vertices=6)], f"asinha.{n}")
    R.arm.scale = [V.get("scale", 1)]*3
    return R, INFO

# ======================================================================= animações
# sentinela: em guarda, espada apontada para baixo à frente, asas semiabertas, asinhas cruzadas no peito
BASE = merge(wings(14, 6, -4, 6, 4, 4), {"spine": {"x": 4}, "chest": {"x": 2}, "neck": {"x": -2}, "head": {"x": -4},
             "thigh.L": {"x": -8, "y": -5}, "thigh.R": {"x": 6, "y": 5}, "shin.L": {"bend": 10}, "shin.R": {"bend": 8},
             "upper_arm.L": {"y": 28, "x": 10}, "forearm.L": {"bend": -30},
             "upper_arm.R": {"y": -22, "x": -20}, "forearm.R": {"bend": -30}, "hand.R": {"x": 60}})
def M(*p): return merge(BASE, *p)
def fl(k): return {"flame": {"scale": k}}

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; b, c = math.sin(t), math.cos(t)
        idle.append(M(wings(14 + 5*c, 6 + 3*c, -4 + 2*b, 6, 4, 4), {"chest": {"x": 2 + 1.5*b}, "head": {"z": 6*c, "x": -4 - 2*b},
                      "hand.R": {"x": 60 + 4*c}}, fl(1 + .12*b)))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 24*s
        walk.append(M(wings(20 + 6*math.sin(2*t), 8, -2, 6, 4, 4), {"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                      "shin.L": {"bend": 8 + 45*max(0, c)**1.3}, "shin.R": {"bend": 8 + 45*max(0, -c)**1.3},
                      "foot.L": {"x": .3*th - 10*max(0, c)}, "foot.R": {"x": -.3*th - 10*max(0, -c)},
                      "hips": {"z": 4*s}, "chest": {"z": -5*s}, "head": {"z": 5*s}, "upper_arm.L": {"x": 10 + 10*s}, "upper_arm.R": {"x": -20 - 6*s}}, fl(1 + .1*s)))
    # golpe: asas abrem de uma vez, a espada sobe sobre a cabeça e desce em arco; chama cresce no corte
    up = M(wings(60, 20, 10, 20, 10, 8), {"upper_arm.R": {"x": -150, "y": 25}, "forearm.R": {"bend": -60}, "hand.R": {"x": -30},
            "chest": {"z": -22, "x": -10}, "spine": {"z": -8, "x": -4}, "head": {"z": 10, "x": 6},
            "thigh.R": {"x": 12}, "thigh.L": {"x": -14}, "root": (0, .04, 0)}, fl(1.3))
    strike = M(wings(75, 25, 10, -10, -6, -4), {"upper_arm.R": {"x": -40, "y": 6, "z": 28}, "forearm.R": {"bend": -6}, "hand.R": {"x": -20},
                "chest": {"z": 28, "x": 22}, "spine": {"x": 10, "z": 8}, "head": {"x": -14, "z": -8},
                "thigh.L": {"x": -36}, "shin.L": {"bend": 26}, "thigh.R": {"x": 20}, "shin.R": {"bend": 6}, "foot.R": {"x": -10},
                "root": (0, -.18, 0)}, fl(1.9))
    follow = merge(strike, {"upper_arm.R": {"x": 14, "z": 8}, "chest": {"x": 6, "z": 6}, "root": (0, -.02, 0)}, fl(1.4))
    attack = keys_to_frames([(0, M()), (.22, up), (.4, merge(up, {"upper_arm.R": {"x": -6}})), (.54, strike), (.7, follow), (1, M())], 10)
    hitp = M(wings(40, 10, 0, 20, 10, 6), {"chest": {"x": -18, "z": -10}, "spine": {"x": -8}, "head": {"x": -22, "z": 14},
              "upper_arm.L": {"y": -10, "x": 20}, "upper_arm.R": {"y": 20, "x": 15}, "forearm.R": {"bend": -20}, "root": (0, .07, 0)}, fl(.8))
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: a espada apaga, cai de joelhos com as asas abertas e tomba de bruços, asas caídas no chão
    kneel = M(wings(50, 15, 5, 10, 6, 4), {"thigh.L": {"x": -70}, "thigh.R": {"x": -55}, "shin.L": {"bend": 100}, "shin.R": {"bend": 110},
               "foot.L": {"x": -10}, "foot.R": {"x": -10}, "chest": {"x": 18}, "head": {"x": 25, "z": 15},
               "upper_arm.L": {"y": 8, "x": 10}, "upper_arm.R": {"y": -8, "x": 0}, "forearm.R": {"bend": -10}}, fl(.4))
    fall = merge(kneel, wings(20, 0, -10, 30, 10, 0), {"hips": {"x": 40}, "spine": {"x": 15}, "upper_arm.L": {"x": -50}, "upper_arm.R": {"x": -40}, "ground": .1}, fl(.15))
    prone = merge(wings(-20, -10, -10, 50, 20, 10), {"hips": {"x": 86, "z": 10}, "spine": {"x": 2}, "chest": {"x": -4}, "head": {"z": 55, "x": -10},
             "upper_arm.L": {"x": -150, "y": 50}, "upper_arm.R": {"x": -110, "y": -60}, "forearm.L": {"bend": -30}, "forearm.R": {"bend": -20}, "hand.R": {"x": 40},
             "thigh.L": {"x": 4, "y": -8}, "thigh.R": {"x": -6, "y": 12}, "shin.L": {"bend": 25}, "shin.R": {"bend": 8},
             "foot.L": {"x": 40}, "foot.R": {"x": 30}, "ground": .07}, fl(.001))
    death = keys_to_frames([(0, hitp), (.3, kneel), (.6, fall), (.85, prone), (1, merge(prone, {"head": {"x": 4}}))], 8)
    return {"idle": idle, "walk": walk, "attack": attack, "hit": hit, "death": death}
