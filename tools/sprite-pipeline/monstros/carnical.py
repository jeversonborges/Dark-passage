# Carniçal: morto da praga, curvado e magro, garras longas, camisa e calça
# rasgadas, coleira de ferro com corrente partida. Brilho: olhos amarelo-pus.
import bpy, bmesh, math, random
from mathutils import Vector
from mrig import *

INFO = {"px": 192, "target_z": .85, "rim": (.85, .8, .45), "colors": 40, "samples": 48,
        "fps": {"idle": 5, "walk": 9, "attack": 12, "hit": 12, "death": 10}}

# Variantes da mesma base (ideia do Jefin: reaproveitar o modelo com mudanças, como os mobs do MU).
VARIANTS = {
    "carnical": {},
    # morto que levantou para o Juízo e ficou sem julgamento: mortalha, capuz de pano, mãos amarradas,
    # tabuleta de ferro pregada no peito; menos curvado; olhos de alma (branco-azulado).
    "nao_julgado": {"shroud": True, "hunch": .45, "eye": (.6, .8, 1), "skin": (.27, .27, .25), "rim": (.55, .65, .8),
                    "scale": 1.05},
    # Não Julgado da Tempestade (Beira da Tempestade): maior e mais curtido pelo Amargo; mortalha queimada de areia
    # cor de ferrugem, óculos de poeira de latão com lentes acesas sobre o capuz, lenço amarrado na boca e um
    # contador de radiação pendurado no peito; olhos verde-amargo.
    "nao_julgado_da_tempestade": {"shroud": True, "storm": True, "hunch": .55, "eye": (.75, 1, .3), "skin": (.3, .25, .19),
                                  "shroud_col": (.24, .15, .09), "shroud_stain": (.55, .45, .3), "rim": (.95, .7, .38), "scale": 1.17},
    # elite: inchado, maior, pele esverdeada, pústulas que brilham verde-ácido no lugar dos olhos
    "carnical_inchado": {"bloat": True, "scale": 1.18, "skin": (.2, .23, .15), "eye": None, "pus": (.6, 1, .2),
                         "rim": (.7, .85, .4)},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
    if "rim" in V: INFO["rim"] = V["rim"]

def build():
    skin = stained("c_pele", V.get("skin", (.25, .23, .19)), stain=(.22, .02, .012), amount=.3, scale=4, rough=.45,
                   blotch=(.13, .07, .1), blotch_amt=.8, grime=1.2)
    rot = mat("c_podre", (.13, .02, .015), 0, .3, dirt=.6)
    rag = stained("c_trapo", (.3, .26, .2), stain=(.26, .025, .012), amount=.5, scale=3.5, rough=.95, grime=1.3)
    band = stained("c_atadura", (.36, .32, .25), stain=(.16, .02, .012), amount=.4, scale=7, rough=.9, grime=.6)
    pants = stained("c_calca", (.05, .055, .06), stain=(.05, .035, .02), amount=.4, scale=3, rough=.9)
    iron = mat("c_ferro", (.11, .05, .025), .8, .65, dirt=.5)
    nail = mat("c_unha", (.25, .22, .15), 0, .4, dirt=.6, grime=.3)
    tooth = mat("c_dente", (.4, .36, .25), 0, .5, dirt=.6, grime=.2)
    ec = V.get("eye", (1, .85, .2))
    eye = mat("c_olho", (1, .9, .4), emit=ec, strength=22) if ec else mat("c_olho", (.02, .015, .01), 0, .3)
    shroud = stained("c_mortalha", V.get("shroud_col", (.27, .25, .21)), stain=V.get("shroud_stain", (.12, .07, .04)), amount=.6, scale=2.5, rough=.95,
                     blotch=(.1, .09, .07), blotch_amt=.6, grime=1.6)
    pus = mat("c_pus", (.5, 1, .2), emit=V["pus"], strength=9) if V.get("pus") else None
    hole = mat("c_buraco", (.01, .005, .005), 0, .9)
    brass = mat("c_latao", (.42, .28, .1), .9, .4, dirt=.6)
    scarf = stained("c_lenco", (.36, .05, .03), stain=(.3, .22, .12), amount=.6, scale=3, rough=.95, grime=1.4)

    B = humanoid(1.0, 1.0)
    for n in "LR":  # braços 18% mais longos
        sh = Vector(B[f"upper_arm.{n}"][0])
        for b in (f"upper_arm.{n}", f"forearm.{n}", f"hand.{n}"):
            h, t, p = B[b]
            B[b] = (tuple(sh + (Vector(h)-sh)*1.18), tuple(sh + (Vector(t)-sh)*1.18), p)
    R = Rig("carnical", B)
    P = R.P
    # ---- corpo magro (pernas, tronco, braços longos)
    j = {"pelvis": (0, 0, .95, .12, .09)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .07); j[f"knee{n}"] = (*k, .05); j[f"calf{n}"] = (*k.lerp(a, .35), .048)
        j[f"ank{n}"] = (*a, .035); j[f"heel{n}"] = (*(a + Vector((0, .035, -.05))), .03)
        j[f"toe{n}"] = (*(P(f"foot.{n}", 1) + Vector((0, -.04, 0))), .03, .022)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"knee{n}"), (f"knee{n}", f"calf{n}"), (f"calf{n}", f"ank{n}"),
              (f"ank{n}", f"heel{n}"), (f"ank{n}", f"toe{n}")]
    legs = skin_mesh("pernas", j, e, skin)
    R.bind(legs, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R", "foot.L", "foot.R"])
    bw = (.23, .21) if V.get("bloat") else (.095, .075)
    t = {"pelvis": (0, 0, .97, .12, .085), "waist": (0, -.03 if V.get("bloat") else .01, 1.12, *bw), "chest": (0, 0, 1.32, .15, .1),
         "neck": (0, -.01, 1.5, .045), "neck2": (0, -.02, 1.58, .04)}
    te = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, 0))), .055); t[f"el{n}"] = (*el, .038)
        t[f"fa{n}"] = (*el.lerp(wr, .4), .04); t[f"wr{n}"] = (*wr, .03)
        te += [("chest", f"sh{n}"), (f"sh{n}", f"el{n}"), (f"el{n}", f"fa{n}"), (f"fa{n}", f"wr{n}")]
    torso = skin_mesh("tronco", t, te, skin)
    R.bind(torso, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])

    # ---- calça rasgada até o meio da canela
    pj = {"pelvis": (0, 0, .97, .135, .1)}; pe = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        pj[f"hip{n}"] = (*h, .085); pj[f"knee{n}"] = (*k, .066); pj[f"cut{n}"] = (*k.lerp(a, .45 if s > 0 else .2), .062)
        pe += [("pelvis", f"hip{n}"), (f"hip{n}", f"knee{n}"), (f"knee{n}", f"cut{n}")]
    if not V.get("shroud"):
        pt = skin_mesh("calca", pj, pe, pants, levels=1)
        R.bind(pt, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R"])
    # cinto de corda
    belt = prim("primitive_torus_add", rag, (0, 0, 1.0), (1.02, .78, 1), major_radius=.13, minor_radius=.014,
                major_segments=20, minor_segments=5)
    # ---- camisa rasgada, aberta na frente (mostra as costelas)
    if V.get("shroud"):
        sh_ = skirt("mortalha", shroud, [(1.5, .1, .085, 0), (1.42, .17, .12, 0), (1.2, .165, .12, .005), (.95, .16, .13, .01),
                                         (.6, .19, .16, .02), (.3, .22, .18, .03), (.08, .24, .2, .04)], jag=.07, seed=9, thick=.01)
        R.bind(sh_, ["hips", "spine", "chest", "thigh.L", "thigh.R", "shin.L", "shin.R"], power=3)
        for s_, n in ((1, "L"), (-1, "R")):
            sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
            sj = {"a": (*(sh + Vector((-.02*s_, 0, 0))), .07), "b": (*el, .055), "c": (*wr.lerp(el, .15), .05)}
            o = skin_mesh(f"manga.{n}", sj, [("a", "b"), ("b", "c")], shroud, levels=1)
            R.bind(o, ["chest", f"upper_arm.{n}", f"forearm.{n}"])
    shirt = None if V.get("shroud") else skirt("camisa", rag, [(1.47, .1, .08, 0), (1.38, .165, .115, 0), (1.22, .16, .11, .005),
                                  (1.06, .125, .1, .01), (.9, .14, .11, .015)], open_front=.75, jag=.09, seed=5, thick=.008)
    if shirt: R.bind(shirt, ["hips", "spine", "chest"], power=3)
    for s, n in (() if V.get("shroud") else ((1, "L"),)):  # uma manga só, rasgada no cotovelo
        sh, el = P(f"upper_arm.{n}"), P(f"forearm.{n}")
        sj = {"a": (*(sh + Vector((-.02*s, 0, 0))), .068), "b": (*sh.lerp(el, .55), .058), "c": (*el.lerp(sh, .05), .052)}
        o = skin_mesh("manga", sj, [("a", "b"), ("b", "c")], rag, levels=1)
        R.bind(o, ["chest", f"upper_arm.{n}", f"forearm.{n}"])

    # ---- costelas, coleira e corrente (presas ao peito)
    R.rigid([belt], "hips")
    cp = []
    ribs = () if (V.get("shroud") or V.get("bloat")) else (1.4, 1.35, 1.3, 1.25)
    for i, z in enumerate(ribs):
        w = .13 - i*.005
        for s in (1, -1):
            pts = [Vector((s*w*math.sin(a), -(.085 + .012*math.cos(a))*math.cos(a)*1.05, z - .02*math.sin(a)))
                   for a in (0.15, .6, 1.05, 1.4)]
            for a, b in zip(pts, pts[1:]):
                cp.append(along("primitive_cylinder_add", skin, a, b, .011, vertices=6))
    collar = not V.get("shroud")
    if collar: cp.append(prim("primitive_torus_add", iron, (0, -.005, 1.52), (1, .95, 1.4), major_radius=.065, minor_radius=.016,
                              major_segments=16, minor_segments=6))
    for k in range(5 if collar else 0):  # corrente partida pendurada na frente
        z = 1.47 - k*.045
        lk = prim("primitive_torus_add", iron, (.02*math.sin(k), -.075 - .01*k, z), (1, 1, 1.5), major_radius=.018,
                  minor_radius=.006, major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0))
        cp.append(lk)
    for k in range(3 if collar else 0):  # cravos da coleira
        a = math.radians(-60 + 60*k)
        cp.append(along("primitive_cone_add", iron, (.06*math.sin(a), -.065*math.cos(a), 1.52),
                        (.1*math.sin(a), -.1*math.cos(a), 1.53), .012, vertices=6, radius1=1, radius2=0))
    # feridas podres
    for p, sc in () if V.get("shroud") else (((.11, .06, 1.38), (.05, .03, .04)), ((-.05, .08, 1.18), (.04, .02, .05)), ((-.13, -.03, 1.33), (.03, .03, .03))):
        cp.append(prim("primitive_uv_sphere_add", rot, p, sc, segments=10, ring_count=6))
    # vergalhão enferrujado atravessado no ombro esquerdo (sai pelas costas)
    sh = P("upper_arm.L")
    if V.get("shroud"):  # tabuleta de ferro pregada no peito (sem nome, sem sentença)
        cp.append(prim("primitive_cube_add", iron, (0, -.135, 1.3), (.075, .008, .09), rot=(-8, 0, 3)))
        for dx, dz in ((-.06, .075), (.06, .075), (-.06, -.075), (.06, -.075)):
            cp.append(prim("primitive_uv_sphere_add", nail, (dx, -.145, 1.3 + dz), (.01, .008, .01), segments=6, ring_count=4))
        cp.append(along("primitive_cylinder_add", rot, (0, -.15, 1.36), (0, -.15, 1.24), .006, vertices=4))
        cp.append(along("primitive_cylinder_add", rot, (-.04, -.15, 1.3), (.04, -.15, 1.3), .006, vertices=4))
    if V.get("storm"):  # contador de radiação pendurado por uma tira, com mostrador aceso
        cp.append(along("primitive_cylinder_add", scarf, (-.1, -.1, 1.45), (.09, -.15, 1.16), .008, vertices=4))
        cp.append(prim("primitive_cube_add", brass, (.1, -.155, 1.13), (.04, .02, .05), rot=(-6, 0, -10)))
        cp.append(prim("primitive_cylinder_add", eye, (.1, -.177, 1.145), (.022, .022, .004), rot=(90, 0, -10), vertices=12))
        cp.append(along("primitive_cylinder_add", iron, (.1, -.16, 1.18), (.12, -.16, 1.25), .006, vertices=5))
        rr = random.Random(9)  # areia grudada nos ombros
        for k in range(10):
            x = rr.uniform(-.17, .17)
            cp.append(prim("primitive_uv_sphere_add", shroud, (x, rr.uniform(-.06, .06), 1.47 - abs(x)*.25),
                           (rr.uniform(.02, .04),)*2 + (.012,), segments=6, ring_count=4))
    if V.get("bloat"):  # pústulas brilhando
        rr = random.Random(21)
        for k in range(9):
            a = rr.uniform(0, 2*math.pi); z = rr.uniform(1.05, 1.42)
            rx, ry = (.2, .18) if z < 1.25 else (.14, .09)
            cp.append(prim("primitive_uv_sphere_add", pus, (rx*math.cos(a), ry*math.sin(a) - .02, z), (.022, .022, .02),
                           segments=8, ring_count=5))
    if not V: cp.append(along("primitive_cylinder_add", iron, sh + Vector((-.06, -.16, .1)), sh + Vector((-.02, .3, -.14)), .011, vertices=6))
    if not V: cp.append(prim("primitive_uv_sphere_add", rot, sh + Vector((-.05, -.06, .05)), (.03, .02, .03), segments=8, ring_count=6))
    R.rigid(cp, "chest")
    # ataduras sujas: antebraço direito e canela esquerda, com pontas soltas
    def wrap(bone, t0, t1, r, n, seed):
        rr = random.Random(seed); a, b = P(bone), P(bone, 1); parts = []
        for k in range(n):
            c = a.lerp(b, t0 + (t1-t0)*k/(n-1))
            o = prim("primitive_torus_add", band, c, (1, 1, 1.6), major_radius=r, minor_radius=.008,
                     major_segments=12, minor_segments=4)
            o.rotation_euler = ((b-a).to_track_quat('Z', 'Y') @ __import__("mathutils").Quaternion((1, 0, 0), rr.uniform(-.3, .3))).to_euler()
            parts.append(o)
        end = a.lerp(b, t1)
        parts.append(along("primitive_cube_add", band, end + Vector((0, .02, 0)), end + Vector((.03, .05, -.12)), .012))
        R.rigid(parts, bone)
    if V.get("shroud"):  # mãos amarradas com corda arrebentada
        rope = mat("c_corda", (.2, .16, .1), 0, .9, dirt=.5)
        for n in "LR":
            a, b = P(f"forearm.{n}"), P(f"forearm.{n}", 1); c = a.lerp(b, .85)
            parts = []
            for k in range(3):
                o = prim("primitive_torus_add", rope, c + (b - a).normalized()*(.02*k), (1, 1, 1.3), major_radius=.05,
                         minor_radius=.011, major_segments=12, minor_segments=4)
                o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler(); parts.append(o)
            parts.append(along("primitive_cylinder_add", rope, c, c + Vector((.1 if n == "R" else -.1, -.04, -.14)), .01, vertices=5))
            R.rigid(parts, f"forearm.{n}")
    else:
        wrap("forearm.R", .25, .85, .04, 6, 1)
        wrap("shin.L", .2, .55, .05, 4, 2)

    # ---- cabeça: crânio alongado, mandíbula caída, olhos de pus, cabelo ralo
    hp = []
    hp.append(prim("primitive_uv_sphere_add", skin, (0, -.01, 1.7), (.085, .1, .105), segments=16, ring_count=10))
    hp.append(prim("primitive_uv_sphere_add", skin, (0, -.045, 1.64), (.06, .06, .05), segments=12, ring_count=8))
    jaw = prim("primitive_uv_sphere_add", skin, (0, -.075, 1.575), (.05, .055, .024), segments=12, ring_count=6, rot=(35, 0, 0))
    hp.append(jaw)
    hp.append(prim("primitive_uv_sphere_add", hole, (0, -.095, 1.615), (.035, .02, .03), segments=10, ring_count=6))
    for k in range(6):
        x = -.03 + .012*k
        hp.append(along("primitive_cone_add", tooth, (x, -.098, 1.64), (x, -.1, 1.615), .006, vertices=4, radius1=1, radius2=0))
        hp.append(along("primitive_cone_add", tooth, (x, -.105, 1.59), (x, -.103, 1.607), .005, vertices=4, radius1=1, radius2=0))
    for s in (1, -1):
        hp.append(prim("primitive_uv_sphere_add", hole, (.03*s, -.072, 1.705), (.022, .012, .016), segments=8, ring_count=6))
        hp.append(prim("primitive_uv_sphere_add", eye, (.03*s, -.083, 1.705), (.012, .007, .011), segments=8, ring_count=6))
    rnd = random.Random(3)
    if V.get("shroud"):  # capuz de pano amarrado sobre a cabeça, com furos nos olhos
        hood = prim("primitive_uv_sphere_add", shroud, (0, -.005, 1.69), (.1, .115, .125), segments=16, ring_count=10)
        hp.append(hood)
        hp.append(prim("primitive_torus_add", rope if False else shroud, (0, -.01, 1.6), (1, 1.1, 1), major_radius=.075,
                       minor_radius=.015, major_segments=14, minor_segments=4))
        for s_ in (1, -1):
            hp.append(prim("primitive_uv_sphere_add", hole, (.032*s_, -.105, 1.705), (.022, .012, .016), segments=8, ring_count=6))
            hp.append(prim("primitive_uv_sphere_add", eye, (.032*s_, -.113, 1.705), (.011, .006, .01), segments=8, ring_count=6))
            if V.get("storm"):  # óculos de poeira de latão
                hp.append(prim("primitive_torus_add", brass, (.034*s_, -.118, 1.705), (1, 1, 1), major_radius=.024,
                               minor_radius=.007, major_segments=12, minor_segments=5, rot=(90, 0, 0)))
                hp.append(prim("primitive_cylinder_add", eye, (.034*s_, -.12, 1.705), (.019, .019, .003), rot=(90, 0, 0), vertices=12))
        if V.get("storm"):
            hp.append(prim("primitive_torus_add", scarf, (0, -.005, 1.71), (1, 1.12, 1), major_radius=.112,
                           minor_radius=.008, major_segments=16, minor_segments=4))  # tira dos óculos
            hp.append(prim("primitive_uv_sphere_add", scarf, (0, -.06, 1.635), (.105, .085, .05), segments=12, ring_count=8))  # lenço na boca
            hp.append(along("primitive_cone_add", scarf, (.05, .08, 1.64), (.09, .17, 1.5), .03, vertices=5, radius1=1, radius2=.3))
            hp.append(along("primitive_cone_add", scarf, (.02, .085, 1.64), (.03, .19, 1.47), .025, vertices=5, radius1=1, radius2=.2))
    for k in range(0 if V.get("shroud") else 5):  # mechas de cabelo
        a = rnd.uniform(.4, 2.7); x, y = .07*math.cos(a), .06 + .03*math.sin(a)
        b = Vector((x*1.3 + rnd.uniform(-.02, .02), y + .05, 1.73 - rnd.uniform(.12, .22)))
        hp.append(along("primitive_cone_add", pants, (x, y, 1.76), b, .011, vertices=4, radius1=1, radius2=.2))
    R.rigid(hp, "head")

    # ---- mãos com garras longas
    for s, n in ((1, "L"), (-1, "R")):
        o, ax, u, sd = R.frame(f"hand.{n}")
        hand = [prim("primitive_uv_sphere_add", skin, o + ax*.04, (.03, .035, .045), segments=10, ring_count=6)]
        hand[0].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        for f in range(4):
            off = sd*(-.025 + .017*f) + u*(.012 - .004*abs(f-1.5))
            base = o + ax*.07 + off
            mid = base + ax*.07 + u*.015
            tip = mid + ax*.08 + u*.05
            hand.append(along("primitive_cylinder_add", skin, base, mid, .009, vertices=6))
            hand.append(along("primitive_cone_add", nail, mid, tip, .008, vertices=5, radius1=1, radius2=0))
        R.rigid(hand, f"hand.{n}")
    R.arm.scale = [1.08*V.get("scale", 1)]*3  # escala no objeto: poses e trava no chão continuam valendo
    return R, INFO

# ======================================================================= animações
BASE = {"spine": {"x": 24}, "chest": {"x": 30}, "neck": {"x": -22}, "head": {"x": -30, "z": 8},
        "thigh.L": {"x": -20, "y": -4}, "thigh.R": {"x": -16, "y": 4}, "shin.L": {"bend": 34}, "shin.R": {"bend": 30},
        "foot.L": {"x": -14}, "foot.R": {"x": -14},
        "upper_arm.L": {"y": 30, "x": -50}, "upper_arm.R": {"y": -28, "x": -62},
        "forearm.L": {"bend": -26}, "forearm.R": {"bend": -34}, "hand.L": {"x": -10}, "hand.R": {"x": -10}}

def M(*p):
    h = V.get("hunch", 1)
    b = {k: dict(v) for k, v in BASE.items()}
    for k in ("spine", "chest", "neck", "head"): b[k]["x"] *= h
    for k in ("upper_arm.L", "upper_arm.R"): b[k]["x"] *= .45 + .55*h
    return merge(b, *p)

def anims(R):
    idle = []
    for i in range(4):
        b = math.sin(i/4*2*math.pi); c = math.cos(i/4*2*math.pi)
        idle.append(M({"chest": {"x": 3*b}, "head": {"z": 7*c, "x": -3*b}, "upper_arm.L": {"x": 4*b},
                       "upper_arm.R": {"x": -4*b}, "forearm.R": {"bend": -4*c}}))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 24*s
        walk.append(M({"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                       "shin.L": {"bend": 6 + 46*max(0, c)**1.3}, "shin.R": {"bend": 6 + 40*max(0, -c)**1.3},
                       "foot.L": {"x": .3*th - 12*max(0, c)}, "foot.R": {"x": -.3*th - 12*max(0, -c)},
                       "hips": {"z": 7*s, "y": 3*c}, "chest": {"z": -12*s, "y": -5*c}, "head": {"z": 10*s, "y": 6*c},
                       "upper_arm.L": {"x": 16*s}, "upper_arm.R": {"x": -16*s},
                       "forearm.L": {"bend": -8*max(0, s)}, "forearm.R": {"bend": -8*max(0, -s)}}))
    # ataque: arranca com a garra direita de cima para baixo e emenda a esquerda
    # ataque: ergue as duas garras acima da cabeça, salta para a frente e rasga de cima para baixo
    wind = M({"upper_arm.L": {"x": -105, "y": -10}, "upper_arm.R": {"x": -100, "y": 10},
              "forearm.L": {"bend": -55}, "forearm.R": {"bend": -55}, "hand.L": {"x": -30}, "hand.R": {"x": -30},
              "spine": {"x": -14}, "chest": {"x": -14}, "head": {"x": 10}, "neck": {"x": 6},
              "thigh.L": {"x": 10}, "thigh.R": {"x": 14}, "shin.L": {"bend": 14}, "shin.R": {"bend": 16}, "root": (0, .05, 0)})
    strike = M({"upper_arm.L": {"x": 10, "y": -6, "z": -18}, "upper_arm.R": {"x": 4, "y": 6, "z": 18},
                "forearm.L": {"bend": -6}, "forearm.R": {"bend": -6}, "hand.L": {"x": 25}, "hand.R": {"x": 25},
                "spine": {"x": 12}, "chest": {"x": 14}, "head": {"x": -18}, "neck": {"x": -10},
                "thigh.L": {"x": -40}, "shin.L": {"bend": 20}, "thigh.R": {"x": 30}, "shin.R": {"bend": 4},
                "foot.R": {"x": -10}, "root": (0, -.32, 0)})
    strike2 = merge(strike, {"chest": {"z": -10}, "upper_arm.R": {"x": 10}, "root": (0, -.3, 0)})
    attack = keys_to_frames([(0, M()), (.3, wind), (.46, strike), (.62, strike2), (1, M())], 8)
    hitp = M({"chest": {"x": -20}, "spine": {"x": -8}, "head": {"x": -22, "z": 10}, "upper_arm.L": {"y": -18, "x": 25},
              "upper_arm.R": {"y": 18, "x": 25}, "forearm.L": {"bend": -40}, "forearm.R": {"bend": -40},
              "root": (0, .08, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: cambaleia, cai de joelhos e tomba de cara no chão
    kneel = M({"thigh.L": {"x": -70}, "thigh.R": {"x": -55}, "shin.L": {"bend": 95}, "shin.R": {"bend": 110},
               "foot.L": {"x": -10}, "foot.R": {"x": -10}, "chest": {"x": 15}, "head": {"x": 15},
               "upper_arm.L": {"y": 8, "x": 10}, "upper_arm.R": {"y": -8, "x": 10}})
    fall = merge(kneel, {"hips": {"x": 40}, "spine": {"x": 15}, "upper_arm.L": {"x": -50}, "upper_arm.R": {"x": -40},
                         "ground": .1})
    prone = {"hips": {"x": 86, "z": 10}, "spine": {"x": 2}, "chest": {"x": -4}, "head": {"z": 60, "x": -10},
             "upper_arm.L": {"x": -150, "y": 50}, "upper_arm.R": {"x": -120, "y": -55},
             "forearm.L": {"bend": -30}, "forearm.R": {"bend": -60},
             "thigh.L": {"x": 4, "y": -8}, "thigh.R": {"x": -6, "y": 12}, "shin.L": {"bend": 25}, "shin.R": {"bend": 8},
             "foot.L": {"x": 40}, "foot.R": {"x": 30}, "ground": .07}
    death = keys_to_frames([(0, hitp), (.3, kneel), (.6, fall), (.85, prone),
                            (1, merge(prone, {"head": {"x": 4}}))], 8)
    return {"idle": idle, "walk": walk, "attack": attack, "hit": hit, "death": death}
