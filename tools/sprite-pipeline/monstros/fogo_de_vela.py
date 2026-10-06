# Fogo-de-Vela (Cripta da Trombeta Calada, andar 2, Ossário das Carpideiras): chama-fantasma presa num
# amontoado de velas de igreja derretidas, fundidas num corpinho meio humano. Cera amarelada escorrida
# com fuligem, pavios acesos nos ombros e na cabeça, rosto de cera derretido (órbitas fundas, boca caída),
# braços de vela pingando, um aro de lustre de ferro com espetos de vela preso no peito e um pedaço
# da corrente do lustre. Flutua um pouco: a cera escorre em fios que não tocam o chão.
# Brilho: a chama (única cor quente forte) e as brasas no fundo dos olhos; uma luz pontual presa à
# cabeça acende a cera por dentro e apaga junto (chave de pose "lamp").
# Extras: blink_out (encolhe numa bola de cera, vira poça e some) e blink_in (o contrário).
# death: derrete numa poça com tocos de vela e o rosto boiando; as chamas apagam uma a uma.
# Usa XRig de larva_de_carne.py: "sx"/"sy"/"sz" (escala por eixo), "vis" (0 = escondido), "lamp".
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from mrig import *
from larva_de_carne import XRig

INFO = {"px": 192, "target_z": .95, "rim": (1, .6, .3), "colors": 40, "samples": 44,
        "fps": {"idle": 8, "walk": 8, "attack": 12, "blink_out": 12, "blink_in": 12, "hit": 12, "death": 10},
        "loops": ("idle", "walk")}

FLOAT = .22   # altura do corpo acima do chão
# velas do corpo: (x, y, z_base, z_topo, raio, osso, chama?)
CANDLES = [
    (0, -.03, .78, 1.2, .1, "head", True),              # vela-cabeça (o rosto fica nela)
    (.075, .05, .9, 1.27, .038, "head", True), (-.08, .045, .9, 1.23, .034, "head", True),
    (.02, .09, .9, 1.32, .03, "head", False),
    (.19, .02, .6, .99, .055, "body", True), (-.19, .03, .6, .95, .05, "body", True),   # ombros
    (.12, .1, .55, .9, .045, "body", False), (-.1, .11, .55, .88, .04, "body", False),
    (.14, -.08, .5, .78, .05, "body", False), (-.13, -.07, .5, .74, .045, "body", False),
    (0, -.12, .45, .66, .055, "body", False), (.05, .14, .48, .84, .04, "body", True),
    (.24, .1, .55, .86, .03, "body", False), (-.24, .09, .55, .83, .028, "body", False),
]

def bones():
    B = {"base": ((0, 0, .3), (0, 0, .55), None),
         "body": ((0, 0, .55), (0, 0, .82), "base"),
         "head": ((0, -.02, .82), (0, -.03, 1.08), "body"),
         "jaw":  ((0, -.11, 1.0), (0, -.15, .93), "head"),
         "drip": ((0, 0, .3), (0, .02, .08), "base"),
         "pool": ((0, 0, 0), (0, 0, .1), None)}
    for s, n in ((1, "L"), (-1, "R")):
        B[f"arm.{n}"] = ((.22*s, 0, .8), (.33*s, -.05, .6), "body")
        B[f"hand.{n}"] = ((.33*s, -.05, .6), (.36*s, -.1, .44), f"arm.{n}")
    for i, (x, y, z0, z1, r, b, fl) in enumerate(CANDLES):
        if fl: B[f"fl{i}"] = ((x, y, z1 + .005), (x, y, z1 + .2), b)
    return B
FLAMES = [f"fl{i}" for i, c in enumerate(CANDLES) if c[6]]

def flame_mesh(base, h, r, m_out, m_in):
    """Chama em gota: bojo + ponta, com núcleo mais claro."""
    o = []
    o.append(prim("primitive_uv_sphere_add", m_out, base + Vector((0, 0, h*.22)), (r, r, h*.24), segments=12, ring_count=8))
    o.append(along("primitive_cone_add", m_out, base + Vector((0, 0, h*.25)), base + Vector((0, 0, h)), r*.96, vertices=12,
                   radius1=1, radius2=0))
    o.append(prim("primitive_uv_sphere_add", m_in, base + Vector((0, -r*.15, h*.2)), (r*.55, r*.55, h*.2), segments=10, ring_count=6))
    return o

def build():
    rnd = random.Random(9)
    wax = stained("fv_cera", (.66, .55, .37), stain=(.07, .05, .035), amount=.3, scale=3.5, rough=.35,
                  blotch=(.34, .26, .16), blotch_amt=.55, grime=.45, dirt=.72)
    b = wax.node_tree.nodes["Principled BSDF"]
    b.inputs["Subsurface Weight"].default_value = .35; b.inputs["Subsurface Radius"].default_value = (.05, .025, .012)
    b.inputs["Subsurface Scale"].default_value = .3
    soot = stained("fv_fuligem", (.05, .04, .035), stain=(.1, .06, .03), amount=.3, scale=6, rough=.7, grime=0)
    wick = mat("fv_pavio", (.02, .015, .012), 0, .8)
    iron = stained("fv_ferro", (.08, .065, .055), stain=(.3, .1, .035), amount=.6, scale=8, metal=.75, rough=.55, grime=0)
    dark = mat("fv_buraco", (.012, .006, .004), 0, .9)
    fl_out = mat("fv_chama", (1, .5, .1), emit=(1, .36, .05), strength=4.5)
    fl_in = mat("fv_chama_nucleo", (1, .85, .5), emit=(1, .65, .2), strength=7)
    ember = mat("fv_brasa", (1, .4, .1), emit=(1, .35, .05), strength=14)

    R = XRig("fogo_de_vela", bones(), ground=None)
    R.hidden = {"pool"}
    P = R.P
    parts = {k: [] for k in ("base", "body", "head", "drip", "jaw")}
    # ------------------------------------------------ massa de cera fundida (tronco), base escorrendo
    j = {"b0": (0, .01, .3, .13, .12), "b1": (0, 0, .5, .2, .17), "b2": (0, .01, .7, .21, .16), "b3": (0, -.01, .84, .14, .12),
         "sL": (.2, .02, .78, .07), "sR": (-.2, .03, .76, .065)}
    mass = skin_mesh("massa", j, [("b0", "b1"), ("b1", "b2"), ("b2", "b3"), ("b2", "sL"), ("b2", "sR")], wax)
    R.bind(mass, ["base", "body", "head"], power=4)
    # fios de cera pendurados embaixo (não tocam o chão)
    dr = []
    for k in range(9):
        a = 2*math.pi*k/9 + rnd.uniform(-.2, .2); rr = rnd.uniform(.05, .11)
        top = Vector((rr*math.cos(a), rr*math.sin(a), .33)); L = rnd.uniform(.1, .24)
        bot = top + Vector((rnd.uniform(-.02, .02), .02, -L))
        dr.append(along("primitive_cone_add", wax, top, bot, rnd.uniform(.025, .045), vertices=8, radius1=1, radius2=.35))
        dr.append(prim("primitive_uv_sphere_add", wax, bot, (.02, .02, .028), segments=8, ring_count=6))
    R.rigid(dr, "drip")
    # cera derretida escorrendo pelo tronco (bolhas e cortinas de escorrido)
    for k in range(16):
        a = rnd.uniform(0, 2*math.pi); z = rnd.uniform(.4, .85)
        rr = .19 if z > .55 else .17
        p = Vector((rr*math.cos(a), rr*math.sin(a)*.85, z))
        bn = "body" if z > .55 else "base"
        parts[bn].append(prim("primitive_uv_sphere_add", wax, p, (.045, .045, .06), segments=10, ring_count=6))
        parts[bn].append(along("primitive_cone_add", wax, p, p + Vector((0, 0, -rnd.uniform(.08, .2))) + p.normalized()*.01, .03,
                               vertices=8, radius1=1, radius2=.5))
    # ------------------------------------------------ velas com escorridos, pavio e fuligem
    for i, (x, y, z0, z1, r, bn, fl) in enumerate(CANDLES):
        c = parts[bn]
        lean = Vector((rnd.uniform(-.02, .02), rnd.uniform(-.02, .02), 0))
        a0, a1 = Vector((x, y, z0)), Vector((x, y, z1)) + lean
        c.append(along("primitive_cylinder_add", wax, a0, a1, r, vertices=14))
        # borda derretida: anel abaulado + cratera escura
        c.append(prim("primitive_torus_add", wax, a1 - Vector((0, 0, .008)), (1, 1, 1), major_radius=r*.85, minor_radius=r*.28,
                      major_segments=14, minor_segments=5))
        c.append(prim("primitive_cylinder_add", soot, a1 + Vector((0, 0, .002)), (r*.6, r*.6, .004), vertices=12))
        c.append(along("primitive_cylinder_add", wick, a1, a1 + Vector((0, 0, .03)), .005, vertices=4))
        for k in range(3 if r > .04 else 2):   # escorridos
            aa = rnd.uniform(0, 2*math.pi); d = Vector((math.cos(aa), math.sin(aa), 0))
            top = a1 + d*r*.95 - Vector((0, 0, .01)); L = rnd.uniform(.06, .16)*(1 + r*5)
            c.append(along("primitive_cone_add", wax, top, top - Vector((0, 0, L)) + d*.008, r*.3, vertices=8, radius1=1, radius2=.6))
            c.append(prim("primitive_uv_sphere_add", wax, top - Vector((0, 0, L)) + d*.008, (r*.3, r*.3, r*.38), segments=8, ring_count=5))
        if rnd.random() < .5:   # fuligem lambendo a vela
            c.append(prim("primitive_uv_sphere_add", soot, a1 - Vector((0, 0, .05)) + Vector((0, -r*.6, 0)), (r*.55, r*.25, .05),
                          segments=8, ring_count=5))
    # ------------------------------------------------ rosto de cera derretido na vela-cabeça
    hc = Vector((0, -.03, 1.0))
    for s in (1, -1):
        e = hc + Vector((.04*s, -.088, .05 if s > 0 else .035))
        parts["head"].append(prim("primitive_uv_sphere_add", dark, e, (.026, .02, .03 if s > 0 else .022), segments=10, ring_count=6))
        parts["head"].append(prim("primitive_uv_sphere_add", ember, e + Vector((0, -.008, -.004)), (.008, .006, .008), segments=6, ring_count=4))
        # pálpebra de cera escorrendo sobre o olho
        parts["head"].append(along("primitive_cone_add", wax, e + Vector((0, -.012, .03)), e + Vector((.005*s, -.018, -.045)), .018,
                                   vertices=8, radius1=1, radius2=.4))
    parts["head"].append(prim("primitive_uv_sphere_add", wax, hc + Vector((0, -.1, .0)), (.018, .02, .03), segments=8, ring_count=5))  # nariz
    parts["head"].append(prim("primitive_uv_sphere_add", wax, hc + Vector((.0, -.085, .1)), (.08, .03, .025), segments=10, ring_count=5))  # testa
    jb, jt = P("jaw"), P("jaw", 1)
    jw = [prim("primitive_uv_sphere_add", dark, jb + Vector((0, -.003, -.035)), (.03, .015, .04), segments=10, ring_count=6),
          prim("primitive_uv_sphere_add", wax, jt + Vector((0, .02, -.01)), (.05, .03, .025), segments=10, ring_count=6)]
    jw.append(along("primitive_cone_add", wax, jt + Vector((.02, .01, -.02)), jt + Vector((.025, .0, -.12)), .014, vertices=6, radius1=1, radius2=.5))
    R.rigid(jw, "jaw")
    # ------------------------------------------------ aro de lustre de ferro no peito, com espetos e corrente
    ring = []
    for k in range(10):
        a = 2*math.pi*k/10
        ring.append(along("primitive_cylinder_add", iron, Vector((.235*math.cos(a), .2*math.sin(a), .62)),
                          Vector((.235*math.cos(a + .63), .2*math.sin(a + .63), .62)), .012, vertices=6))
        if k % 2 == 0:
            p = Vector((.235*math.cos(a), .2*math.sin(a), .62))
            ring.append(prim("primitive_cylinder_add", iron, p + Vector((0, 0, .01)), (.025, .025, .008), vertices=8))
            ring.append(along("primitive_cone_add", iron, p + Vector((0, 0, .015)), p + Vector((0, 0, .08)), .007, vertices=5, radius1=1, radius2=0))
    for k in range(6):   # corrente partida do lustre pendurada
        q = Vector((-.22, -.05 - .005*k, .6 - .045*k))
        ring.append(prim("primitive_torus_add", iron, q, (1, 1, 1.5), major_radius=.017, minor_radius=.005,
                         major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
    parts["body"] += ring
    for k, ob in parts.items():
        if ob: R.rigid(ob, k)
    # ------------------------------------------------ braços: velas finas fundidas, pingando
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"arm.{n}"), P(f"hand.{n}"), P(f"hand.{n}", 1)
        aj = {"a": (*sh, .055), "b": (*el, .04), "c": (*wr, .03)}
        am = skin_mesh(f"braco.{n}", aj, [("a", "b"), ("b", "c")], wax)
        R.bind(am, [f"arm.{n}", f"hand.{n}"])
        fg = []
        for f in range(3):   # dedos de cera derretidos
            d = (wr - el).normalized(); side = Vector((1, 0, 0))*(f - 1)*.02
            fg.append(along("primitive_cone_add", wax, wr + side, wr + side + d*.07 + Vector((0, 0, -.02)), .012, vertices=6, radius1=1, radius2=.5))
        fg.append(prim("primitive_uv_sphere_add", wax, wr + Vector((0, 0, -.11)), (.013, .013, .02), segments=6, ring_count=4))
        R.rigid(fg, f"hand.{n}")
    # ------------------------------------------------ chamas (um osso cada, tremulam)
    for i, (x, y, z0, z1, r, bn, fl) in enumerate(CANDLES):
        if not fl: continue
        h = .26 if i == 0 else .13 + r*1.2
        R.rigid(flame_mesh(Vector((x, y, z1 + .01)), h, (.05 if i == 0 else .022 + r*.25), fl_out, fl_in), f"fl{i}")
    # ------------------------------------------------ poça de cera (escondida; blink e morte)
    pl = []
    for k in range(7):
        a = rnd.uniform(0, 2*math.pi); rr = rnd.uniform(0, .25) if k else 0
        s_ = rnd.uniform(.18, .28) if k < 3 else rnd.uniform(.07, .12)
        pl.append(prim("primitive_uv_sphere_add", wax, (rr*math.cos(a), rr*math.sin(a), .0), (s_*1.15, s_, .035), segments=18, ring_count=8))
    pl.append(prim("primitive_uv_sphere_add", soot, (.05, .03, .03), (.12, .1, .008), segments=12, ring_count=5))
    for k in range(4):   # tocos de vela e o rosto boiando na poça
        a = 2*math.pi*k/4 + .4; p = Vector((.17*math.cos(a), .15*math.sin(a), .0))
        pl.append(along("primitive_cylinder_add", wax, p, p + Vector((.02, .01, .07 + .03*(k % 2))), .03, vertices=10))
        pl.append(along("primitive_cylinder_add", wick, p + Vector((.02, .01, .07 + .03*(k % 2))), p + Vector((.02, .01, .1 + .03*(k % 2))), .004, vertices=4))
    face = Vector((-.04, -.1, .03))
    pl.append(prim("primitive_uv_sphere_add", wax, face, (.08, .06, .03), segments=12, ring_count=6))
    for s in (1, -1):
        pl.append(prim("primitive_uv_sphere_add", dark, face + Vector((.03*s, -.01, .02)), (.016, .012, .01), segments=8, ring_count=4))
    pl.append(prim("primitive_uv_sphere_add", dark, face + Vector((0, -.04, .018)), (.025, .01, .008), segments=8, ring_count=4))
    pl.append(prim("primitive_cylinder_add", ember, (.1, .06, .03), (.035, .035, .004), vertices=10))   # brasa da poça
    R.rigid(pl, "pool")
    # ------------------------------------------------ luz da chama, presa à cabeça
    ld = bpy.data.lights.new("fv_luz", 'POINT'); ld.color = (1, .55, .22); ld.shadow_soft_size = .05; ld.energy = 9
    lo = bpy.data.objects.new("fv_luz", ld); bpy.context.scene.collection.objects.link(lo)
    lo.parent = R.arm; lo.parent_type = 'BONE'; lo.parent_bone = "head"
    bpy.context.view_layer.update()
    bone = R.arm.data.bones["head"]
    tailM = R.arm.matrix_world @ bone.matrix_local @ Matrix.Translation((0, bone.length, 0))
    lo.matrix_parent_inverse = tailM.inverted(); lo.location = (0, -.22, 1.12)   # na frente do rosto, na altura das chamas
    R.lamps.append((ld, 9))
    R.arm.scale = [1.3]*3
    return R, INFO

# ======================================================================= animações
def flick(t, k=1.0):
    """Tremulação das chamas (fase diferente para cada uma)."""
    o = {}
    for j, f in enumerate(FLAMES):
        ph = t*(1 + .3*j) + j*1.7
        o[f] = {"sy": k*(.18*math.sin(ph) + .1*math.sin(2.3*ph + 1)), "sx": -.08*math.sin(ph + .5)*k, "sz": -.08*math.sin(ph + .5)*k,
                "x": 8*math.sin(ph*1.3)*k, "y": 8*math.cos(ph*1.1)*k}
    return o

def flames(k):
    """Escala de todas as chamas (0 = apagadas)."""
    return {f: {"vis": k} for f in FLAMES}

BASE = {"root": (0, 0, FLOAT), "arm.L": {"y": 10, "x": -10}, "arm.R": {"y": -10, "x": -14}, "hand.L": {"x": -10}, "hand.R": {"x": -14},
        "head": {"x": -4}, "jaw": {"x": 8}}
def M(*p): return merge(BASE, *p)

def anims(R):
    idle = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t)
        idle.append(M(flick(t*2), {"root": (0, 0, FLOAT + .03*s), "body": {"x": 2*c, "z": 3*s}, "head": {"z": -4*s, "x": 2*c},
                                   "arm.L": {"x": 6*s, "y": 4*c}, "arm.R": {"x": -6*s, "y": -4*c}, "drip": {"x": 8*c, "y": 6*s},
                                   "jaw": {"x": 4*max(0, s)}}))
    walk = []   # desliza: inclina para a frente, fios de cera arrastam atrás, chamas deitam para trás
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t)
        lean = {f: {"x": -26} for f in FLAMES}
        walk.append(M(flick(t*2, .8), lean, {"root": (0, 0, FLOAT + .04*s), "base": {"x": 10}, "body": {"x": 4, "z": 5*s}, "head": {"z": -5*s},
                                             "arm.L": {"x": 26, "y": 4*c}, "arm.R": {"x": 26, "y": -4*c}, "hand.L": {"x": 10},
                                             "hand.R": {"x": 10}, "drip": {"x": -30 + 6*c, "y": 8*s}}))
    # faísca: estica para trás, a chama da cabeça cresce, avança e cospe (boca abre), recua
    back = M(flick(1), {"root": (0, .06, FLOAT + .06), "base": {"x": -10}, "body": {"x": -12}, "head": {"x": -16},
                        "arm.L": {"y": 50, "x": -20}, "arm.R": {"y": -50, "x": -20}, "hand.L": {"x": -20}, "hand.R": {"x": -20},
                        "fl0": {"sy": .6, "sx": .25, "sz": .25}, "drip": {"x": 20}})
    spit = M(flick(2), {"root": (0, -.12, FLOAT + .02), "base": {"x": 14}, "body": {"x": 14}, "head": {"x": 16}, "jaw": {"x": 40},
                        "arm.L": {"y": 20, "x": 30}, "arm.R": {"y": -20, "x": 30}, "hand.L": {"x": 10}, "hand.R": {"x": 10},
                        "fl0": {"sy": -.3, "x": 30, "sx": .1, "sz": .1}, "drip": {"x": -25}})
    attack = keys_to_frames([(0, idle[0]), (.35, back), (.5, spit), (.65, merge(spit, {"jaw": {"x": -14}, "head": {"x": -4}})), (1, idle[0])], 8)
    # some: encolhe numa bola de cera (escala do corpo inteiro no osso base), vira poça e some
    def melt(u):   # u: 0 em pé .. 1 bola de cera no chão
        return M(flick(u*6, 1 - u), flames(1 - u), {"base": {"sy": -.6*u, "sx": .25*u, "sz": .25*u}, "body": {"x": 10*u},
                                                     "head": {"x": 20*u}, "arm.L": {"vis": 1 - .85*u}, "arm.R": {"vis": 1 - .85*u},
                                                     "drip": {"sy": -.7*u}, "root": (0, 0, FLOAT*(1 - u) - .22*u),
                                                     "lamp": {"v": 1 - .7*u}})
    bo = []
    for i in range(8):
        u = i/7
        if i < 5:
            p = melt(min(1, (i/4)**1.2))
            if i >= 3: p["pool"] = {"vis": .4 + .3*(i - 3)}
        else:
            k = (i - 4)/3
            p = merge(melt(1), {"base": {"vis": max(.001, 1 - 1.2*k)}, "pool": {"vis": 1 - .5*k}, "lamp": {"v": .3*(1 - k)}})
            p["base"].update({"sy": -.6, "sx": .25, "sz": .25})
        bo.append(p)
    bo[-1]["pool"] = {"vis": .001}; bo[-1]["base"]["vis"] = .001; bo[-1]["lamp"] = {"v": 0}
    blink_in = []   # reaparece: a poça cresce, a bola de cera sobe e se abre, chamas reacendem com um estalo
    seq = [(0, .001, .6, 1), (.2, .5, 1, 1), (.4, .8, 1, .9), (.55, 1, .7, .7), (.7, 1, .3, .4), (.85, 1, 0, .1), (1, 1, 0, 0)]
    for t_, vis, pool, u in seq:
        p = melt(u)
        if vis < 1:
            p["base"]["vis"] = vis; p["base"].update({"sy": -.6, "sx": .25, "sz": .25})
        p["pool"] = {"vis": max(.001, pool)}
        if t_ == .85: p = merge(p, {f: {"sy": .5} for f in FLAMES}, {"root": (0, 0, FLOAT + .05)})
        blink_in.append(p)
    hitp = M(flick(3, 1.4), {"root": (0, .08, FLOAT + .03), "base": {"x": -14}, "body": {"x": -10, "z": 10}, "head": {"x": -18, "z": -14},
                             "jaw": {"x": 26}, "arm.L": {"y": 40}, "arm.R": {"y": -40}, "drip": {"x": 30},
                             **{f: {"x": 40, "sy": -.3} for f in FLAMES}})
    hit = [hitp, lerp_pose(hitp, idle[0], .5), idle[0]]
    # morte: perde a força, desce, derrete escorrendo e vira poça; as chamas apagam uma a uma
    death = []
    for i in range(10):
        u = i/9
        p = melt(min(1, u*1.15))
        p = merge(p, {"head": {"x": 30*u, "z": 20*u}, "jaw": {"x": 30*u}})
        for j, f in enumerate(FLAMES):
            off = min(1, max(0, u*1.6 - j*.12))
            p[f] = {"vis": max(.001, 1 - off), "sy": -.4*off}
        if i == 0: p = merge(hitp, {"root": (0, .04, FLOAT)})
        p["pool"] = {"vis": max(.001, min(1, (u - .25)*1.6))}
        if i >= 7:
            p["base"] = {"vis": .001}
        p["lamp"] = {"v": max(0, 1 - u*1.1)}
        death.append(p)
    return {"idle": idle, "walk": walk, "attack": attack, "blink_out": bo, "blink_in": blink_in, "hit": hit, "death": death}
