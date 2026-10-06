# Açougueiro Oco e Capataz Gancho (mesma base): trabalhadores do abatedouro que a praga esvaziou.
# Açougueiro Oco: barriga aberta e vazia (costelas sobre um buraco escuro), capuz de saco com um olho,
#   avental de couro encharcado de sangue, cutelo enorme. Brilho: o olho (brasa fraca).
# Capataz Gancho (elite): maior, sobretudo de couro, máscara-respirador de focinho de porco, braço esquerdo
#   de ferro que termina num gancho de carne com corrente, porrete cravejado de pregos. Brilho: lanterna no cinto.
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *

INFO = {"px": 224, "target_z": .95, "rim": (.95, .55, .3), "colors": 44, "samples": 40,
        "fps": {"idle": 5, "walk": 8, "attack": 12, "heavy": 12, "hook": 12, "spin": 14, "shout": 10, "hit": 12, "death": 10}}

VARIANTS = {
    "acougueiro_oco": {"scale": 1.04},
    "capataz_gancho": {"scale": 1.2, "elite": True, "rim": (1, .5, .2)},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
    if "rim" in V: INFO["rim"] = V["rim"]
set_variant("acougueiro_oco")

def apron_sheet(name, m, z0, z1, w0, w1, y0, curve, rows=8, cols=9, jag=0, seed=1):
    """Folha curva na frente do corpo (avental): de z0 (topo) a z1 (barra)."""
    rnd = random.Random(seed); bm = bmesh.new(); g = []
    for r in range(rows):
        t = r/(rows-1); z = z0 + (z1 - z0)*t; w = w0 + (w1 - w0)*t; row = []
        for c in range(cols):
            u = c/(cols-1)*2 - 1
            zz = z + (rnd.uniform(-jag, jag*.3) if r == rows-1 else 0)
            row.append(bm.verts.new((u*w, y0(t) + curve*u*u, zz)))
        g.append(row)
    for r in range(rows-1):
        for c in range(cols-1):
            bm.faces.new((g[r][c], g[r][c+1], g[r+1][c+1], g[r+1][c]))
    o = obj_from_bm(name, bm, m); o.modifiers.new("s", 'SOLIDIFY').thickness = .012; apply_mods(o)
    return o

def build():
    E = V.get("elite")
    skin = stained("a_pele", (.27, .2, .18), stain=(.2, .02, .012), amount=.35, scale=4, rough=.45,
                   blotch=(.14, .08, .09), blotch_amt=.7, grime=1.1)
    leather = stained("a_couro", (.09, .05, .03), stain=(.22, .015, .01), amount=.65, scale=3, rough=.35, grime=.8)
    coat = stained("a_sobretudo", (.055, .045, .04), stain=(.12, .02, .01), amount=.4, scale=3, rough=.6, grime=1.2)
    pants = stained("a_calca", (.06, .06, .065), stain=(.06, .03, .02), amount=.4, scale=3, rough=.9)
    rubber = stained("a_bota", (.025, .022, .022), stain=(.2, .02, .01), amount=.35, scale=5, rough=.3)
    sack = stained("a_saco", (.22, .17, .1), stain=(.2, .025, .012), amount=.6, scale=3, rough=1, grime=.8,
                   blotch=(.08, .06, .04), blotch_amt=.6)
    steel = stained("a_aco", (.4, .39, .37), stain=(.2, .05, .02), amount=.5, scale=6, metal=1, rough=.4, grime=.3)
    iron = stained("a_ferro", (.09, .07, .06), stain=(.18, .07, .03), amount=.5, scale=5, metal=.85, rough=.55, grime=.5)
    brass = stained("a_latao", (.38, .24, .08), stain=(.08, .06, .03), amount=.4, scale=6, metal=1, rough=.45, grime=.4)
    wood = stained("a_madeira", (.12, .07, .04), stain=(.2, .02, .01), amount=.4, scale=4, rough=.8, grime=.4)
    meat = stained("a_carne", (.32, .05, .045), stain=(.12, .1, .08), amount=.3, scale=6, rough=.25, grime=.2)
    rope = mat("a_corda", (.2, .15, .09), 0, .9, dirt=.5)
    hole = mat("a_buraco", (.008, .004, .004), 0, .95)
    glow = mat("a_brilho", (1, .5, .2), emit=(1, .45, .12), strength=14)

    B = humanoid(1.0, 1.15)
    R = Rig(V["name"], B); P = R.P
    # ------------------------------------------------ corpo pesado
    j = {"pelvis": (0, 0, .95, .17, .12)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .1); j[f"knee{n}"] = (*k, .075); j[f"ank{n}"] = (*a, .055)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"knee{n}"), (f"knee{n}", f"ank{n}")]
    legs = skin_mesh("pernas", j, e, pants); R.bind(legs, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R"])
    for s, n in ((1, "L"), (-1, "R")):  # botas de borracha até a canela
        k, a, t = P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        bj = {"top": (*k.lerp(a, .4), .085), "ank": (*a, .075), "heel": (*(a + Vector((0, .045, -.05))), .06),
              "toe": (*(t + Vector((0, -.02, 0))), .062, .05)}
        o = skin_mesh(f"bota.{n}", bj, [("top", "ank"), ("ank", "heel"), ("ank", "toe")], rubber)
        R.bind(o, [f"shin.{n}", f"foot.{n}"])
    t = {"pelvis": (0, 0, .98, .19, .14), "belly": (0, -.04, 1.15, .23, .2), "chest": (0, 0, 1.34, .22, .15),
         "neck": (0, -.01, 1.5, .08), "neck2": (0, -.02, 1.57, .07)}
    te = [("pelvis", "belly"), ("belly", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, 0))), .1); t[f"bi{n}"] = (*sh.lerp(el, .45), .085)
        t[f"el{n}"] = (*el, .065); t[f"fa{n}"] = (*el.lerp(wr, .35), .07); t[f"wr{n}"] = (*wr, .05)
        te += [("chest", f"sh{n}"), (f"sh{n}", f"bi{n}"), (f"bi{n}", f"el{n}"), (f"el{n}", f"fa{n}"), (f"fa{n}", f"wr{n}")]
        if E and n == "L":  # o capataz não tem antebraço esquerdo: o braço de ferro entra no cotovelo
            te = te[:-2]; del t[f"fa{n}"], t[f"wr{n}"]
    torso = skin_mesh("tronco", t, te, skin)
    R.bind(torso, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])

    # ------------------------------------------------ avental de couro encharcado (frente) + alças
    ap = apron_sheet("avental", leather, 1.47, .42, .17, .27, lambda t: -.17 - .12*t + .05*(1 - t)**2, .1, jag=.04, seed=3)
    R.bind(ap, ["hips", "spine", "chest", "thigh.L", "thigh.R"], power=3)
    ch = []
    for s in (1, -1):
        ch.append(along("primitive_cylinder_add", leather, (.15*s, -.17, 1.46), (.08*s, .02, 1.56), .012, vertices=5))
    ch.append(prim("primitive_torus_add", leather, (0, 0, 1.1), (1.08, .92, 1), major_radius=.22, minor_radius=.02,
                   major_segments=20, minor_segments=4))
    if not E:
        # o "oco": barriga aberta e vazia, costelas sobre o buraco, tripas penduradas
        ch.append(prim("primitive_uv_sphere_add", hole, (0, -.235, 1.22), (.11, .06, .12), segments=14, ring_count=8))
        for i, z in enumerate((1.32, 1.27, 1.22, 1.17)):
            w = .1 - .006*i
            for s in (1, -1):
                pts = [Vector((s*w*math.sin(a), -.24 + .05*(1 - math.cos(a)), z - .015*math.sin(a))) for a in (.1, .7, 1.3)]
                for a_, b_ in zip(pts, pts[1:]):
                    ch.append(along("primitive_cylinder_add", skin, a_, b_, .011, vertices=6))
        for k, x in enumerate((-.04, .03)):
            pts = [Vector((x + .015*math.sin(i*1.3 + k), -.25 - .02*i*(1 - i/6), 1.12 - .07*i)) for i in range(6)]
            for a_, b_ in zip(pts, pts[1:]):
                ch.append(along("primitive_cylinder_add", meat, a_, b_, .02, vertices=6))
    else:
        # sobretudo de capataz por cima, ombreira de couro cravejada no ombro direito
        sk = skirt("sobretudo", coat, [(1.5, .13, .12, 0), (1.4, .25, .17, 0), (1.15, .25, .2, .01), (.9, .24, .18, .015),
                                       (.6, .28, .22, .03), (.3, .31, .25, .04)], open_front=.85, jag=.06, seed=4, thick=.012)
        R.bind(sk, ["hips", "spine", "chest", "thigh.L", "thigh.R"], power=3)
        c = Vector((-.26, 0, 1.47))
        pad = prim("primitive_uv_sphere_add", leather, c, (.15, .14, .09), segments=14, ring_count=8, rot=(0, -20, 0))
        ch.append(pad)
        for k in range(4):
            q = c + Vector((-.03 - .03*k, -.08 + .055*k, .07))
            ch.append(along("primitive_cone_add", iron, q, q + Vector((-.04, 0, .1)), .02, vertices=5, radius1=1, radius2=0))
        # corrente do gancho enrolada no ombro esquerdo
        for k in range(10):
            a = 2*math.pi*k/10
            q = Vector((.2 + .07*math.cos(a), .06*math.sin(a), 1.44 + .05*math.sin(a)))
            ch.append(prim("primitive_torus_add", iron, q, (1, 1, 1.5), major_radius=.025, minor_radius=.008,
                           major_segments=8, minor_segments=4, rot=(90*(k % 2), 0, 0)))
        # lanterna de latão com brasa no cinto
        lp = Vector((.2, -.12, 1.0))
        ch.append(prim("primitive_cylinder_add", brass, lp, (.04, .04, .06), vertices=8))
        ch.append(prim("primitive_cylinder_add", glow, lp + Vector((0, -.005, 0)), (.03, .03, .045), vertices=8))
        ch.append(prim("primitive_cone_add", brass, lp + Vector((0, 0, .08)), (.045, .045, .03), vertices=8))
    # ganchos de carne no cinto com pedaços pendurados
    for k, x in enumerate((-.18, -.1, .12)):
        q = Vector((x, -.2 + .05*abs(x), 1.06))
        ch.append(prim("primitive_torus_add", iron, q + Vector((0, 0, -.04)), (1, 1, 1.3), major_radius=.025, minor_radius=.007,
                       major_segments=8, minor_segments=4, rot=(0, 90, 0)))
        if k != 1: ch.append(prim("primitive_uv_sphere_add", meat, q + Vector((0, -.01, -.11)), (.035, .03, .055), segments=8, ring_count=6))
    R.rigid(ch, "chest")

    # ------------------------------------------------ cabeça
    hd = [prim("primitive_uv_sphere_add", skin, (0, -.02, 1.69), (.095, .105, .11), segments=14, ring_count=10)]
    if not E:  # capuz de saco amarrado, um furo com o olho aceso, boca costurada
        hd.append(prim("primitive_uv_sphere_add", sack, (0, -.01, 1.71), (.125, .135, .15), segments=16, ring_count=10))
        hd.append(along("primitive_cone_add", sack, (0, .0, 1.82), (0, .03, 1.9), .05, vertices=8, radius1=1, radius2=.35))
        hd.append(prim("primitive_torus_add", rope, (0, .01, 1.85), (1, 1, 1), major_radius=.035, minor_radius=.01,
                       major_segments=10, minor_segments=4))
        for s_ in (1, -1):  # pontas do saco caídas
            hd.append(along("primitive_cone_add", sack, (.02*s_, .03, 1.89), (.09*s_, .07, 1.8), .035, vertices=5, radius1=1, radius2=.2))
        hd.append(prim("primitive_torus_add", rope, (0, -.01, 1.6), (1, 1.05, 1), major_radius=.085, minor_radius=.013,
                       major_segments=14, minor_segments=4))
        hd.append(prim("primitive_uv_sphere_add", hole, (.045, -.128, 1.73), (.026, .012, .02), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", glow, (.045, -.134, 1.73), (.012, .006, .009), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", hole, (-.045, -.126, 1.735), (.02, .01, .006), segments=8, ring_count=4))
        for k in range(5):  # boca costurada
            x = -.045 + .022*k
            hd.append(along("primitive_cylinder_add", rope, (x - .008, -.138, 1.655), (x + .008, -.138, 1.635), .004, vertices=4))
        hd.append(along("primitive_cylinder_add", rope, (-.055, -.137, 1.645), (.055, -.137, 1.645), .004, vertices=4))
    else:  # máscara-respirador de focinho de porco (couro e latão), olhos de vidro escuro
        hd.append(prim("primitive_uv_sphere_add", leather, (0, -.03, 1.69), (.105, .11, .12), segments=16, ring_count=10))
        hd.append(prim("primitive_cylinder_add", brass, (0, -.15, 1.65), (.045, .045, .05), vertices=12, rot=(90, 0, 0)))
        hd.append(prim("primitive_cylinder_add", hole, (0, -.2, 1.65), (.035, .035, .005), vertices=12, rot=(90, 0, 0)))
        for s in (1, -1):
            hd.append(prim("primitive_uv_sphere_add", hole, (.012*s, -.205, 1.65), (.01, .006, .012), segments=6, ring_count=4))
            hd.append(prim("primitive_cylinder_add", brass, (.045*s, -.11, 1.73), (.028, .028, .012), vertices=10, rot=(90, 0, 0)))
            hd.append(prim("primitive_cylinder_add", hole, (.045*s, -.118, 1.73), (.02, .02, .006), vertices=10, rot=(90, 0, 0)))
            hd.append(along("primitive_cylinder_add", rubber, (.03*s, -.13, 1.62), (.11*s, .02, 1.55), .012, vertices=6))
        hd.append(prim("primitive_cylinder_add", leather, (0, -.01, 1.79), (.12, .13, .02), vertices=16))  # boné de couro
        hd.append(prim("primitive_uv_sphere_add", leather, (0, -.01, 1.8), (.1, .11, .05), segments=12, ring_count=6))
        hd.append(prim("primitive_cube_add", leather, (0, -.12, 1.785), (.08, .05, .008), rot=(-12, 0, 0)))
    R.rigid(hd, "head")

    # ------------------------------------------------ mãos e armas
    for s, n in ((1, "L"), (-1, "R")):
        if E and n == "L": continue
        o, ax, u, sd = R.frame(f"hand.{n}")
        g = prim("primitive_uv_sphere_add", skin, o + ax*.05, (.05, .055, .06), segments=10, ring_count=6)
        g.rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        parts = [g]
        if n == "R" and not E:  # cutelo enorme
            parts.append(along("primitive_cylinder_add", wood, o + ax*.05 - u*.06, o + ax*.05 + u*.14, .022, vertices=8))
            c = o + ax*.05 + u*.36 + ax*.05
            bl = prim("primitive_cube_add", steel, c, (1, 1, 1))
            from mathutils import Matrix
            rot = Matrix((sd, ax, u)).transposed()  # x=sd (espessura), y=ax (altura da lâmina), z=u (comprimento)
            bl.rotation_euler = rot.to_euler(); bl.scale = (.012, .12, .23); parts.append(bl)
            parts.append(prim("primitive_cylinder_add", hole, c + u*.17 - ax*.06, (.025, .025, .02), vertices=10))
            parts[-1].rotation_euler = rot.to_euler()
            edge = mat("a_fio", (.75, .73, .7), 1, .15, dirt=.8, grime=.1)
            parts.append(along("primitive_cylinder_add", edge, c - u*.22 + ax*.12, c + u*.23 + ax*.12, .008, vertices=6))
            parts.append(along("primitive_cylinder_add", steel, c - u*.22 - ax*.11, c + u*.23 - ax*.11, .012, vertices=6))
        if n == "R" and E:  # porrete cravejado de pregos
            a0, a1 = o + ax*.05 - u*.1, o + ax*.05 + u*.75
            parts.append(along("primitive_cone_add", wood, a0, a1, .055, vertices=10, radius1=.55, radius2=1))
            rr = random.Random(8)
            for k in range(14):
                tt = rr.uniform(.45, .95); p0 = a0.lerp(a1, tt)
                ang = rr.uniform(0, 2*math.pi); d = (sd*math.cos(ang) + ax*math.sin(ang)).normalized()
                parts.append(along("primitive_cone_add", iron, p0 + d*.045, p0 + d*.11, .008, vertices=4, radius1=1, radius2=0))
            for k in range(2):
                q = a0.lerp(a1, .3 + .05*k)
                parts.append(along("primitive_cylinder_add", iron, q - u*.015, q + u*.015, .06, vertices=10))
        R.rigid(parts, f"hand.{n}")
    if E:  # braço de ferro com o gancho (osso "hook" filho do antebraço)
        el, wr = P("forearm.L"), P("hand.L"); d = (wr - el).normalized()
        ar = [along("primitive_cylinder_add", iron, el, wr, .045, vertices=10)]
        for k in range(3):
            o2 = prim("primitive_cylinder_add", brass, el.lerp(wr, .2 + .3*k), (.055, .055, .015), vertices=10)
            o2.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); ar.append(o2)
        ar.append(prim("primitive_uv_sphere_add", brass, el, (.07, .07, .07), segments=10, ring_count=6))
        for k in range(3):  # pistões
            a = 2*math.pi*k/3; off = (Quaternion(d, a) @ Vector((0, .06, 0)))
            ar.append(along("primitive_cylinder_add", steel, el.lerp(wr, .1) + off, el.lerp(wr, .8) + off, .01, vertices=5))
        R.rigid(ar, "forearm.L")
        hk = []
        base = P("hook")
        f = Vector((0, -1, 0)) - d*(-d.y); f.normalize()
        hk.append(along("primitive_cylinder_add", iron, base, base + d*.08, .035, vertices=8))
        hk.append(along("primitive_cylinder_add", steel, base + d*.08, base + d*.3, .022, vertices=8))
        c = base + d*.3 + f*.1
        pts = [c + (-f*math.cos(math.radians(a_)) + d*math.sin(math.radians(a_)))*.1 for a_ in range(0, 221, 20)]
        for k in range(len(pts) - 1):
            hk.append(along("primitive_cylinder_add", steel, pts[k], pts[k+1], .022*(1 - k/14), vertices=8))
        hk.append(along("primitive_cone_add", steel, pts[-1], pts[-1] + (pts[-1] - pts[-2]).normalized()*.07, .016, vertices=6,
                        radius1=1, radius2=0))
        R.rigid(hk, "hook")
    R.arm.scale = [V.get("scale", 1)]*3
    return R, INFO

# patch: o capataz tem um osso a mais para o gancho
_orig_humanoid = humanoid
def humanoid(s=1.0, w=1.0, extra=None):
    B = _orig_humanoid(s, w, extra)
    if V.get("elite"):
        h, t = Vector(B["forearm.L"][1]), Vector(B["hand.L"][1]); d = (t - h).normalized()
        B["hook"] = (tuple(h), tuple(h + d*.35), "forearm.L")
    return B

# ======================================================================= animações
BASE = {"spine": {"x": 6}, "chest": {"x": 6}, "neck": {"x": -6}, "head": {"x": -6},
        "thigh.L": {"x": -6, "y": -6}, "thigh.R": {"x": -4, "y": 6}, "shin.L": {"bend": 12}, "shin.R": {"bend": 10},
        "foot.L": {"x": -6}, "foot.R": {"x": -6},
        "upper_arm.L": {"y": 26, "x": -10}, "upper_arm.R": {"y": -22, "x": -16},
        "forearm.L": {"bend": -24}, "forearm.R": {"bend": -28}, "hand.R": {"x": -6}}

def M(*p): return merge(BASE, *p)

def anims(R):
    E = V.get("elite")
    idle = []
    for i in range(4):
        b = math.sin(i/4*2*math.pi)
        idle.append(M({"chest": {"x": 2*b}, "head": {"x": -2*b, "z": 3*b}, "upper_arm.R": {"x": -3*b}, "forearm.L": {"bend": -3*b}}))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 22*s
        walk.append(M({"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                       "shin.L": {"bend": 6 + 42*max(0, c)**1.3}, "shin.R": {"bend": 6 + 42*max(0, -c)**1.3},
                       "foot.L": {"x": .3*th - 10*max(0, c)}, "foot.R": {"x": -.3*th - 10*max(0, -c)},
                       "hips": {"z": 6*s, "y": 4*c}, "chest": {"z": -8*s, "y": -3*c}, "head": {"z": 5*s},
                       "upper_arm.L": {"x": 14*s}, "upper_arm.R": {"x": -6*s}}))
    hitp = M({"chest": {"x": -16, "z": 8}, "spine": {"x": -6}, "head": {"x": -18, "z": 10},
              "upper_arm.L": {"y": -12, "x": 15}, "upper_arm.R": {"y": 14, "x": 10}, "root": (0, .07, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    out = {"idle": idle, "walk": walk}
    if not E:
        # cutelada: golpe lateral da direita para a esquerda
        wind = M({"upper_arm.R": {"y": 75, "x": 15}, "forearm.R": {"bend": -70}, "chest": {"z": -32, "x": -4},
                  "spine": {"z": -10}, "head": {"z": 14}, "upper_arm.L": {"x": -25}, "thigh.R": {"x": 8}})
        strike = M({"upper_arm.R": {"y": 32, "x": -70, "z": 40}, "forearm.R": {"bend": -12}, "hand.R": {"x": 10},
                    "chest": {"z": 36, "x": 10}, "spine": {"z": 12}, "head": {"z": -14},
                    "thigh.L": {"x": -26}, "shin.L": {"bend": 18}, "thigh.R": {"x": 16}, "root": (0, -.14, 0)})
        out["attack"] = keys_to_frames([(0, M()), (.32, wind), (.5, strike), (.72, merge(strike, {"chest": {"z": 4}})), (1, M())], 8)
        # golpe de açougue: ergue o cutelo (telegrafo longo), crava no chão e fica preso puxando
        up = M({"upper_arm.R": {"x": -165, "y": 18}, "forearm.R": {"bend": -70}, "upper_arm.L": {"x": -120, "y": -10},
                "forearm.L": {"bend": -60}, "chest": {"x": -16}, "spine": {"x": -8}, "head": {"x": 10},
                "thigh.L": {"x": -14}, "thigh.R": {"x": 10}, "root": (0, .04, 0)})
        slam = M({"upper_arm.R": {"x": -50, "y": 16}, "forearm.R": {"bend": -6}, "hand.R": {"x": 30},
                  "upper_arm.L": {"x": -40, "y": -6}, "forearm.L": {"bend": -20},
                  "chest": {"x": 34}, "spine": {"x": 16}, "head": {"x": -26},
                  "thigh.L": {"x": -40}, "shin.L": {"bend": 50}, "thigh.R": {"x": 10}, "shin.R": {"bend": 40}, "root": (0, -.2, 0)})
        tug = lambda k: merge(slam, {"chest": {"x": -6 - 4*k, "z": 4*(-1)**k}, "upper_arm.R": {"x": 6 + 3*k}, "head": {"x": 6},
                                     "upper_arm.L": {"x": 10}})
        out["heavy"] = keys_to_frames([(0, M()), (.18, up), (.32, merge(up, {"chest": {"x": -3}})), (.42, slam),
                                       (.52, tug(0)), (.62, tug(1)), (.72, tug(2)), (.84, tug(3)), (1, M())], 14)
    else:
        # porretada: de cima para baixo na diagonal
        wind = M({"upper_arm.R": {"x": -140, "y": 40}, "forearm.R": {"bend": -60}, "chest": {"z": -20, "x": -8},
                  "head": {"z": 10}, "upper_arm.L": {"x": -30, "y": -20}})
        strike = M({"upper_arm.R": {"x": -45, "y": 10, "z": 30}, "forearm.R": {"bend": -8}, "chest": {"z": 26, "x": 18},
                    "spine": {"x": 6}, "head": {"x": -12}, "thigh.L": {"x": -24}, "shin.L": {"bend": 20}, "root": (0, -.12, 0)})
        out["attack"] = keys_to_frames([(0, M()), (.3, wind), (.48, strike), (.7, merge(strike, {"chest": {"x": 4}})), (1, M())], 8)
        # gancho: gira o braço, arremessa (o gancho some em voo), puxa de volta com força
        h_up = M({"upper_arm.L": {"x": -150, "y": -30}, "forearm.L": {"bend": -30}, "chest": {"z": 20, "x": -6}, "head": {"z": -8}})
        h_back = M({"upper_arm.L": {"x": -60, "y": -80}, "forearm.L": {"bend": -40}, "chest": {"z": 34}, "head": {"z": -14}})
        throw = M({"upper_arm.L": {"x": -95, "y": -15, "z": -20}, "forearm.L": {"bend": 0}, "chest": {"z": -24, "x": 12},
                   "thigh.L": {"x": -24}, "shin.L": {"bend": 16}, "root": (0, -.1, 0), "scale": {"hook": .001}})
        pull = M({"upper_arm.L": {"x": 30, "y": -30}, "forearm.L": {"bend": -95}, "chest": {"z": 24, "x": -14}, "spine": {"x": -8},
                  "thigh.R": {"x": 16}, "thigh.L": {"x": -6}, "root": (0, .08, 0)})
        out["hook"] = keys_to_frames([(0, M()), (.15, h_up), (.3, h_back), (.42, throw), (.62, throw),
                                      (.75, merge(pull, {"scale": {"hook": 1}})), (1, M())], 12)
        # giro: braços abertos, uma volta completa
        spin = []
        for i in range(10):
            spin.append(M({"upper_arm.L": {"y": -70, "x": -20}, "upper_arm.R": {"y": 75, "x": -20}, "forearm.L": {"bend": -5},
                           "forearm.R": {"bend": -20}, "hips": {"z": -36*i}, "chest": {"z": -12, "x": 4},
                           "thigh.L": {"x": -8 + 10*math.sin(i)}, "thigh.R": {"x": 4 - 10*math.sin(i)}}))
        out["spin"] = spin
        # chamado: grita chamando os Carniçais
        sh = M({"chest": {"x": -20}, "spine": {"x": -8}, "neck": {"x": -10}, "head": {"x": -26},
                "upper_arm.L": {"y": -40, "x": -30}, "upper_arm.R": {"y": 40, "x": -30}, "forearm.L": {"bend": -40},
                "forearm.R": {"bend": -40}, "thigh.L": {"x": -10}, "thigh.R": {"x": 10}})
        out["shout"] = keys_to_frames([(0, M()), (.3, sh), (.5, merge(sh, {"head": {"z": 8}})), (.7, merge(sh, {"head": {"z": -8}})), (1, M())], 8)
    # morte: cai de joelhos e tomba de lado/para trás com o peso
    kneel = M({"thigh.L": {"x": -75}, "thigh.R": {"x": -40}, "shin.L": {"bend": 100}, "shin.R": {"bend": 95},
               "chest": {"x": 18}, "head": {"x": 20}, "upper_arm.L": {"y": 6, "x": 10}, "upper_arm.R": {"y": -6, "x": 10},
               "forearm.R": {"bend": -20}})
    fall = merge(kneel, {"hips": {"x": -30, "y": 20}, "spine": {"x": -10}, "ground": .12})
    down = {"hips": {"x": -84, "y": 24}, "spine": {"x": -4}, "chest": {"x": -2}, "head": {"z": 50, "x": 8},
            "upper_arm.L": {"x": -10, "y": -20}, "upper_arm.R": {"x": -40, "y": 60}, "forearm.L": {"bend": -30},
            "forearm.R": {"bend": -10}, "thigh.L": {"x": -30}, "thigh.R": {"x": -10}, "shin.L": {"bend": 50},
            "shin.R": {"bend": 15}, "foot.L": {"x": -20}, "ground": .12}
    out["hit"] = hit
    out["death"] = keys_to_frames([(0, hitp), (.3, kneel), (.6, fall), (.85, down), (1, merge(down, {"head": {"x": 4}}))], 8)
    return out
