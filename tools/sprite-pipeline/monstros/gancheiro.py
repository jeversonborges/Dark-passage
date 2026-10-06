# Gancheiro (Cripta da Trombeta Calada, andar 1): ajudante do Abatedouro Carniça que a praga deixou
# magro e comprido. Atira ganchos de carne de longe e puxa o jogador para perto dos Açougueiros.
# Capuz de carrasco de couro com óculos de soldador de latão, camisa encardida de mangas arregaçadas,
# avental curto de couro, corrente enrolada no peito em bandoleira, ganchos pendurados no cinto e nas
# costas, rolo de corrente no ombro. Na mão direita, o gancho de arremesso com um pedaço de corrente.
# Brilho: as lentes dos óculos (brasa fraca). Extra: pull (puxa a corrente com o corpo todo; a corrente
# esticada aparece só nela, osso "line" escondido no resto). O gancho some em voo (attack) com a chave "scale".
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion, Matrix
from mrig import *
from acougueiro import apron_sheet
from larva_de_carne import XRig

INFO = {"px": 224, "target_z": .95, "rim": (.95, .55, .3), "colors": 40, "samples": 44,
        "fps": {"idle": 5, "walk": 9, "attack": 12, "pull": 10, "hit": 12, "death": 10}}

def bones():
    B = humanoid(1.07, .86)
    h, t = Vector(B["hand.R"][0]), Vector(B["hand.R"][1]); d = (t - h).normalized()
    B["hook"] = (tuple(h), tuple(h + d*.3), "hand.R")
    hl = Vector(B["hand.L"][0])
    B["line"] = (tuple(hl), tuple(hl + Vector((0, -.6, 0))), "hand.L")
    return B

def build():
    rnd = random.Random(4)
    skin = stained("g_pele", (.26, .22, .19), stain=(.2, .025, .015), amount=.3, scale=4, rough=.45,
                   blotch=(.14, .09, .1), blotch_amt=.7, grime=1.1)
    shirt = stained("g_camisa", (.34, .3, .23), stain=(.24, .03, .015), amount=.55, scale=3, rough=.95,
                    blotch=(.11, .09, .07), blotch_amt=.7, grime=1.3)
    pants = stained("g_calca", (.06, .06, .065), stain=(.06, .03, .02), amount=.4, scale=3, rough=.9)
    leather = stained("g_couro", (.13, .075, .045), stain=(.2, .015, .01), amount=.6, scale=3, rough=.38, grime=.8)
    hoodm = stained("g_capuz", (.09, .06, .042), stain=(.14, .02, .012), amount=.45, scale=4, rough=.42, grime=.4,
                    blotch=(.09, .06, .045), blotch_amt=.6)
    rubber = stained("g_bota", (.025, .022, .022), stain=(.2, .02, .01), amount=.35, scale=5, rough=.3)
    iron = stained("g_ferro", (.16, .13, .11), stain=(.32, .11, .04), amount=.55, scale=6, metal=.8, rough=.5, grime=.4)
    steel = stained("g_aco", (.5, .48, .45), stain=(.25, .04, .02), amount=.55, scale=6, metal=1, rough=.4, grime=.3)
    brass = stained("g_latao", (.4, .26, .09), stain=(.08, .06, .03), amount=.4, scale=6, metal=1, rough=.4, grime=.3)
    wood = stained("g_madeira", (.12, .07, .04), stain=(.2, .02, .01), amount=.4, scale=4, rough=.8, grime=.4)
    meat = stained("g_carne", (.3, .05, .045), stain=(.12, .1, .08), amount=.3, scale=6, rough=.25, grime=.2)
    hole = mat("g_buraco", (.01, .006, .005), 0, .9)
    lens = mat("g_lente", (1, .55, .2), emit=(1, .42, .1), strength=10)

    R = XRig("gancheiro", bones()); P = R.P
    R.hidden = {"line"}
    # ------------------------------------------------ corpo magro e comprido
    j = {"pelvis": (0, 0, .99, .11, .085)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .075); j[f"knee{n}"] = (*k, .058); j[f"calf{n}"] = (*k.lerp(a, .35), .055); j[f"ank{n}"] = (*a, .042)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"knee{n}"), (f"knee{n}", f"calf{n}"), (f"calf{n}", f"ank{n}")]
    legs = skin_mesh("pernas", j, e, pants); R.bind(legs, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R"])
    for s, n in ((1, "L"), (-1, "R")):  # botas de borracha
        k, a, t = P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        bj = {"top": (*k.lerp(a, .5), .068), "ank": (*a, .062), "heel": (*(a + Vector((0, .04, -.055))), .05),
              "toe": (*(t + Vector((0, -.02, 0))), .055, .045)}
        R.bind(skin_mesh(f"bota.{n}", bj, [("top", "ank"), ("ank", "heel"), ("ank", "toe")], rubber), [f"shin.{n}", f"foot.{n}"])
    t = {"pelvis": (0, 0, 1.0, .12, .09), "waist": (0, .005, 1.18, .1, .08), "chest": (0, 0, 1.4, .15, .1),
         "neck": (0, -.01, 1.58, .05), "neck2": (0, -.02, 1.66, .045)}
    te = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, 0))), .058); t[f"el{n}"] = (*el, .042)
        te += [("chest", f"sh{n}"), (f"sh{n}", f"el{n}")]
    torso = skin_mesh("tronco", t, te, shirt)
    R.bind(torso, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R"])
    for s, n in ((1, "L"), (-1, "R")):  # antebraços nus, mangas arregaçadas
        el, wr = P(f"forearm.{n}"), P(f"hand.{n}")
        fj = {"a": (*el, .038), "b": (*el.lerp(wr, .4), .036), "c": (*wr, .027)}
        R.bind(skin_mesh(f"antebraco.{n}", fj, [("a", "b"), ("b", "c")], skin), [f"upper_arm.{n}", f"forearm.{n}"])
        cf = []
        cf.append(prim("primitive_torus_add", shirt, el, (1, 1, 1.5), major_radius=.05, minor_radius=.02, major_segments=12, minor_segments=5))
        cf[-1].rotation_euler = (wr - el).to_track_quat('Z', 'Y').to_euler()
        R.rigid(cf, f"forearm.{n}")
    # braçadeira de couro com fivela no antebraço direito
    el, wr = P("forearm.R"), P("hand.R"); bd = (wr - el).normalized()
    br = [prim("primitive_cylinder_add", leather, el.lerp(wr, .62), (.045, .045, .07), vertices=10)]
    br[0].rotation_euler = bd.to_track_quat('Z', 'Y').to_euler()
    br.append(prim("primitive_cube_add", brass, el.lerp(wr, .62) + Vector((0, -.045, 0)), (.015, .006, .02)))
    R.rigid(br, "forearm.R")

    # ------------------------------------------------ avental curto de couro, cinto, ganchos pendurados
    ap = apron_sheet("avental", leather, 1.16, .66, .13, .2, lambda t: -.11 - .05*t, .07, jag=.04, seed=6)
    R.bind(ap, ["hips", "spine", "thigh.L", "thigh.R"], power=3)
    ch = []
    ch.append(prim("primitive_torus_add", leather, (0, 0, 1.06), (1.0, .82, 1), major_radius=.13, minor_radius=.02,
                   major_segments=20, minor_segments=4))
    ch.append(prim("primitive_cube_add", brass, (0, -.122, 1.06), (.03, .008, .025)))
    for s in (1, -1):  # alças do avental
        ch.append(along("primitive_cylinder_add", leather, (.11*s, -.11, 1.15), (.07*s, .02, 1.55), .01, vertices=5))
    def hookmesh(c, d, f, size, parts, m=steel):
        """Gancho de carne em S: c = olho de cima, d = para baixo, f = lado da curva."""
        parts.append(prim("primitive_torus_add", iron, c, (1, 1, 1), major_radius=.022*size, minor_radius=.006*size,
                          major_segments=8, minor_segments=4))
        parts[-1].rotation_euler = f.to_track_quat('Z', 'Y').to_euler()
        a0 = c + d*.02*size; a1 = a0 + d*.16*size
        parts.append(along("primitive_cylinder_add", m, a0, a1, .009*size, vertices=6))
        cc = a1 + f*.055*size
        pts = [cc + (-f*math.cos(math.radians(a)) + d*math.sin(math.radians(a)))*.055*size for a in range(0, 211, 30)]
        for k in range(len(pts)-1):
            parts.append(along("primitive_cylinder_add", m, pts[k], pts[k+1], .009*size*(1 - k/10), vertices=6))
        parts.append(along("primitive_cone_add", m, pts[-1], pts[-1] + (pts[-1] - pts[-2]).normalized()*.035*size, .007*size,
                           vertices=5, radius1=1, radius2=0))
    for k, (x, sz) in enumerate(((-.12, 1.1), (-.05, .9), (.13, 1.0))):
        c = Vector((x, -.1 + .25*abs(x), 1.02))
        hookmesh(c, Vector((0, 0, -1)), Vector((0, -1, 0)) if k != 1 else Vector((1, 0, 0)), sz, ch)
    ch.append(prim("primitive_uv_sphere_add", meat, (-.12, -.16, .82), (.03, .025, .045), segments=8, ring_count=6))
    # corrente em bandoleira (ombro esquerdo -> quadril direito), passando pelas costas
    for k in range(34):
        a = 2*math.pi*k/34
        q = Vector((.02 + .19*math.cos(a), .14*math.sin(a) - .01, 1.3 + .19*math.cos(a)))
        q += Vector((0, 0, 0)) if math.sin(a) < 0 else Vector((0, .01, 0))
        ch.append(prim("primitive_torus_add", iron, q, (1, 1, 1.5), major_radius=.028, minor_radius=.009,
                       major_segments=8, minor_segments=4, rot=(90*(k % 2), -50, math.degrees(a))))
    # rolo de corrente no ombro direito e dois ganchos grandes pendurados nas costas
    for k in range(14):
        a = 2*math.pi*k/14
        q = Vector((-.13 + .09*math.cos(a), .03 + .02*math.sin(a), 1.45 + .09*math.sin(a)))
        ch.append(prim("primitive_torus_add", iron, q, (1, 1, 1.5), major_radius=.02, minor_radius=.0065,
                       major_segments=8, minor_segments=4, rot=(90*(k % 2), 90, math.degrees(a))))
    for s in (1, -1):
        hookmesh(Vector((.07*s, .13, 1.42)), Vector((0, .15, -1)).normalized(), Vector((0, 1, 0)), 1.4, ch)
    R.rigid(ch, "chest")

    # ------------------------------------------------ cabeça: capuz de carrasco de couro + óculos de soldador
    hd = [prim("primitive_uv_sphere_add", skin, (0, -.02, 1.79), (.09, .1, .11), segments=14, ring_count=10)]
    hd.append(prim("primitive_uv_sphere_add", hoodm, (0, -.01, 1.8), (.105, .115, .13), segments=16, ring_count=10))
    hd.append(along("primitive_cone_add", hoodm, (0, .02, 1.87), (0, .1, 2.0), .06, vertices=8, radius1=1, radius2=.15))
    # costuras e rebites do capuz
    hd.append(prim("primitive_torus_add", leather, (0, -.01, 1.8), (1, 1.1, 1), major_radius=.11, minor_radius=.006,
                   major_segments=20, minor_segments=4, rot=(0, 90, 0)))
    for k in range(5):
        a = math.radians(-60 + 30*k)
        hd.append(prim("primitive_uv_sphere_add", brass, (.105*math.sin(a), -.11*math.cos(a)*.6 + .02, 1.7), (.008, .008, .008),
                       segments=6, ring_count=4))
    # óculos: dois copos de latão com lentes acesas, alça de couro
    for s in (1, -1):
        c = Vector((.042*s, -.112, 1.81))
        hd.append(prim("primitive_cylinder_add", brass, c, (.032, .032, .022), vertices=12, rot=(90, 0, 0)))
        hd.append(prim("primitive_torus_add", brass, c + Vector((0, -.022, 0)), (1, 1, 1), major_radius=.03, minor_radius=.006,
                       major_segments=12, minor_segments=4, rot=(90, 0, 0)))
        hd.append(prim("primitive_cylinder_add", lens, c + Vector((0, -.02, 0)), (.022, .022, .004), vertices=12, rot=(90, 0, 0)))
        for k in range(4):
            a = math.pi/2*k + .5
            hd.append(prim("primitive_uv_sphere_add", iron, c + Vector((.027*math.cos(a), -.024, .027*math.sin(a))), (.005, .005, .005),
                           segments=5, ring_count=3))
    hd.append(along("primitive_cylinder_add", brass, (-.012, -.13, 1.81), (.012, -.13, 1.81), .008, vertices=6))
    hd.append(prim("primitive_torus_add", leather, (0, -.01, 1.81), (1, 1.12, 1), major_radius=.112, minor_radius=.01,
                   major_segments=20, minor_segments=4))
    # fenda da boca com o queixo magro aparecendo e trapo amarrado
    hd.append(prim("primitive_uv_sphere_add", hole, (0, -.108, 1.72), (.035, .02, .012), segments=8, ring_count=5))
    hd.append(prim("primitive_uv_sphere_add", skin, (0, -.085, 1.7), (.035, .03, .022), segments=8, ring_count=5))
    # capa curta de couro sobre os ombros (gola do capuz)
    R.rigid(hd, "head")
    mant = skirt("gola", hoodm, [(1.72, .085, .085, 0), (1.67, .14, .12, 0), (1.61, .2, .14, .01), (1.56, .22, .15, .015)],
                 jag=.04, seed=3, thick=.01)
    R.bind(mant, ["chest", "neck", "head", "upper_arm.L", "upper_arm.R"], power=3)

    # ------------------------------------------------ mãos: direita segura o gancho; esquerda, um rolo de corrente
    for s, n in ((1, "L"), (-1, "R")):
        o, ax, u, sd = R.frame(f"hand.{n}")
        g = prim("primitive_uv_sphere_add", skin, o + ax*.045, (.038, .045, .055), segments=10, ring_count=6)
        g.rotation_euler = ax.to_track_quat('Z', 'Y').to_euler(); parts = [g]
        if n == "L":  # rolo de corrente pendurado da mão
            for k in range(16):
                a = 2*math.pi*k/16
                q = o + ax*.06 + ax*(.1 - .1*math.cos(a)) + u*.07*math.sin(a)
                parts.append(prim("primitive_torus_add", iron, q, (1, 1, 1.5), major_radius=.02, minor_radius=.0065,
                                  major_segments=8, minor_segments=4, rot=(90*(k % 2), 0, math.degrees(a))))
        R.rigid(parts, f"hand.{n}")
    # gancho de arremesso (osso "hook"): cabo em T na mão, haste, curva para a frente, pedaço de corrente
    o, ax, u, sd = R.frame("hand.R")
    hk = [along("primitive_cylinder_add", wood, o + ax*.05 - sd*.06, o + ax*.05 + sd*.06, .016, vertices=8)]
    hk.append(along("primitive_cylinder_add", steel, o + ax*.05, o + ax*.24, .012, vertices=8))
    c = o + ax*.24 + u*.07
    pts = [c + (-u*math.cos(math.radians(a)) + ax*math.sin(math.radians(a)))*.07 for a in range(0, 221, 20)]
    for k in range(len(pts) - 1):
        hk.append(along("primitive_cylinder_add", steel, pts[k], pts[k+1], .012*(1 - k/16), vertices=8))
    hk.append(along("primitive_cone_add", steel, pts[-1], pts[-1] + (pts[-1] - pts[-2]).normalized()*.05, .01, vertices=6, radius1=1, radius2=0))
    for k in range(5):  # corrente curta pendurada do cabo
        q = o + ax*.05 + sd*.06 + ax*(.03*k) + u*(.01*math.sin(k))
        hk.append(prim("primitive_torus_add", iron, q, (1, 1, 1.5), major_radius=.016, minor_radius=.005,
                       major_segments=8, minor_segments=4, rot=(90*(k % 2), 0, 0)))
        hk[-1].rotation_euler = (Quaternion(ax.to_track_quat('Z', 'Y')) @ Quaternion((0, 0, 1), math.pi/2*(k % 2))).to_euler()
    hk.append(prim("primitive_uv_sphere_add", meat, pts[5] + u*.01, (.025, .02, .03), segments=8, ring_count=5))
    for ob in hk:   # gancho grande, legível a 100 px
        ob.location = o + (ob.location - o)*1.6; ob.scale = ob.scale*1.6
    R.rigid(hk, "hook")
    # corrente esticada (só no pull): sai da mão esquerda para a frente
    h, tl = P("line"), P("line", 1); ln = []
    for k in range(22):
        q = h.lerp(tl, k/21)
        ln.append(prim("primitive_torus_add", iron, q, (1, 1, 1.6), major_radius=.018, minor_radius=.006,
                       major_segments=8, minor_segments=4, rot=(90, 90*(k % 2), 0)))
    hookmesh(tl + Vector((0, -.01, 0)), Vector((0, -1, -.25)).normalized(), Vector((0, 0, 1)), 1.4, ln)   # o gancho voltando na ponta
    R.rigid(ln, "line")
    R.arm.scale = [1.0]*3
    return R, INFO

# ======================================================================= animações
BASE = {"spine": {"x": 8}, "chest": {"x": 10}, "neck": {"x": -4}, "head": {"x": -10},
        "thigh.L": {"x": -4, "y": -5}, "thigh.R": {"x": -2, "y": 5}, "shin.L": {"bend": 10}, "shin.R": {"bend": 8},
        "foot.L": {"x": -5}, "foot.R": {"x": -4},
        "upper_arm.L": {"y": 30, "x": -14}, "upper_arm.R": {"y": -26, "x": -18},
        "forearm.L": {"bend": -30}, "forearm.R": {"bend": -36}, "hand.R": {"x": -8}}

def M(*p): return merge(BASE, *p)

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; b = math.sin(t); c = math.cos(t)
        idle.append(M({"chest": {"x": 2*b}, "head": {"x": -2*b, "z": 6*c}, "upper_arm.R": {"x": -6*b, "z": 4*c},
                       "forearm.R": {"bend": -6*b}, "hand.R": {"z": 14*c}, "upper_arm.L": {"x": 3*b}, "hips": {"y": 2*c}}))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 26*s
        walk.append(M({"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                       "shin.L": {"bend": 6 + 48*max(0, c)**1.3}, "shin.R": {"bend": 6 + 48*max(0, -c)**1.3},
                       "foot.L": {"x": .3*th - 12*max(0, c)}, "foot.R": {"x": -.3*th - 12*max(0, -c)},
                       "hips": {"z": 7*s, "y": 3*c}, "chest": {"z": -9*s, "y": -3*c}, "head": {"z": 6*s},
                       "upper_arm.L": {"x": 18*s}, "upper_arm.R": {"x": -12*s}, "hand.R": {"z": 10*c}}))
    # arremesso: gira o gancho atrás do ombro, passo à frente, solta (o gancho some), segue o braço, pega outro
    wind = M({"upper_arm.R": {"x": -40, "y": 70}, "forearm.R": {"bend": -80}, "hand.R": {"x": -30},
              "chest": {"z": 34, "x": -6}, "spine": {"z": 10}, "head": {"z": -20}, "upper_arm.L": {"x": -40, "y": -10},
              "forearm.L": {"bend": -40}, "thigh.L": {"x": -8}, "thigh.R": {"x": 10}, "root": (0, .06, 0)})
    wind2 = merge(wind, {"upper_arm.R": {"x": -40}, "hand.R": {"x": -20}, "chest": {"z": 6}})
    throw = M({"upper_arm.R": {"x": -95, "y": 10, "z": 15}, "forearm.R": {"bend": -6}, "hand.R": {"x": 10},
               "chest": {"z": -30, "x": 16}, "spine": {"z": -10, "x": 6}, "head": {"z": 18, "x": -12},
               "upper_arm.L": {"x": 25, "y": 10}, "thigh.L": {"x": -34}, "shin.L": {"bend": 20}, "thigh.R": {"x": 18},
               "foot.R": {"x": -12}, "root": (0, -.16, 0)})
    follow = merge(throw, {"upper_arm.R": {"x": 30}, "chest": {"x": 6, "z": -6}})
    keys = [(0, M()), (.22, wind), (.36, wind2), (.48, throw), (.62, follow), (.86, M({"upper_arm.R": {"x": 10}, "hand.R": {"x": 20}})), (1, M())]
    attack = keys_to_frames(keys, 10)
    for k in range(5, 9): attack[k]["scale"] = {"hook": .001}
    # puxada: segura a corrente esticada com as duas mãos, inclina para trás e puxa duas vezes, passo atrás
    LINE = {"aim": {"line": (0, -1, -.12)}, "line": {"vis": 1}}
    grip = M(LINE, {"upper_arm.L": {"x": -70, "y": -20, "z": -10}, "forearm.L": {"bend": -20},
                    "upper_arm.R": {"x": -60, "y": 15, "z": 25}, "forearm.R": {"bend": -40},
                    "chest": {"z": 10, "x": 4}, "thigh.L": {"x": -24}, "shin.L": {"bend": 14}, "thigh.R": {"x": 14}, "shin.R": {"bend": 16}})
    def haul(k): return M(LINE, {"upper_arm.L": {"x": -20 + 8*k, "y": -16}, "forearm.L": {"bend": -70},
                                 "upper_arm.R": {"x": 0, "y": 20, "z": 20}, "forearm.R": {"bend": -80},
                                 "chest": {"x": -24, "z": 26}, "spine": {"x": -12}, "head": {"x": 14, "z": -10},
                                 "thigh.L": {"x": -30}, "shin.L": {"bend": 10}, "thigh.R": {"x": 30}, "shin.R": {"bend": 30},
                                 "root": (0, .12 + .05*k, 0)})
    reach = M(LINE, {"upper_arm.L": {"x": -55, "y": -14}, "forearm.L": {"bend": -20}, "upper_arm.R": {"x": -80, "y": 10, "z": 30},
                     "forearm.R": {"bend": -10}, "chest": {"x": 12, "z": -6}, "spine": {"x": 4},
                     "thigh.L": {"x": -26}, "shin.L": {"bend": 20}, "thigh.R": {"x": 20}, "shin.R": {"bend": 20}, "root": (0, .05, 0)})
    pull = keys_to_frames([(0, grip), (.22, haul(0)), (.38, merge(haul(0), {"chest": {"z": -6}})), (.52, reach),
                           (.72, haul(1)), (.86, merge(haul(1), {"chest": {"z": -4}})), (1, grip)], 12)
    for p in pull: p["line"] = {"vis": 1}; p["aim"] = {"line": (0, -1, -.12)}; p["scale"] = {"hook": .001}
    hitp = M({"chest": {"x": -18, "z": 10}, "spine": {"x": -8}, "head": {"x": -20, "z": -12},
              "upper_arm.L": {"y": -14, "x": 20}, "upper_arm.R": {"y": 16, "x": 18}, "root": (0, .07, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: dobra os joelhos, cai sentado e tomba de costas, o gancho escapa da mão
    kneel = M({"thigh.L": {"x": -70}, "thigh.R": {"x": -50}, "shin.L": {"bend": 100}, "shin.R": {"bend": 95},
               "chest": {"x": 20}, "head": {"x": 22}, "upper_arm.L": {"y": 6, "x": 10}, "upper_arm.R": {"y": -10, "x": 20}})
    fall = merge(kneel, {"hips": {"x": -35, "y": -10}, "spine": {"x": -12}, "ground": .1})
    down = {"hips": {"x": -86, "y": -14}, "spine": {"x": -6}, "chest": {"x": -4}, "head": {"z": -45, "x": 10},
            "upper_arm.L": {"x": -30, "y": -10}, "upper_arm.R": {"x": -60, "y": 70}, "forearm.L": {"bend": -40},
            "forearm.R": {"bend": -10}, "thigh.L": {"x": -40}, "thigh.R": {"x": -12}, "shin.L": {"bend": 70},
            "shin.R": {"bend": 20}, "foot.L": {"x": -20}, "hook": {"x": 60}, "ground": .1}
    death = keys_to_frames([(0, hitp), (.3, kneel), (.6, fall), (.85, down), (1, merge(down, {"head": {"x": 4}}))], 8)
    return {"idle": idle, "walk": walk, "attack": attack, "pull": pull, "hit": hit, "death": death}
