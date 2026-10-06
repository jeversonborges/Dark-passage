# Zacarias, o Arauto da Trombeta Calada (chefe do andar 3: Câmara da Trombeta). O anjo que deu a meia nota do
# Juízo e ficou anos no escuro segurando uma trombeta que não soa. Enlouqueceu: quer tocar a nota inteira e
# julgar todos, Vigília e Arautos.
# Alto (~2,9 m), magro, rosto de porcelana rachado com remendos de ouro, olhos de luz fria, cabelo longo e ralo.
# A boca foi costurada com arame em volta do bocal de uma longa trombeta de arauto de latão esverdeado, que pende do
# rosto até a cintura, com a flâmula da Trombeta e o pavilhão tapado pelo lacre de chumbo da Vigília.
# Túnica de arauto marfim encardida com barra dourada, tabardo com a trombeta bordada, gorjal de latão, cintos com
# fivelas, algemas de ferro nos pulsos e nas asas com correntes partidas (ele se acorrentou ao posto).
# Asas grandes de penas sujas. Auréola de latão quebrada com dentes de engrenagem. Espada sagrada na mão direita.
# Brilho: uma cor só, branco-dourado frio (olhos, auréola, gravação da espada).
# Variante zacarias_chamas (fase 3, "Asas em Chamas"): as asas pegam fogo sagrado.
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion, Matrix
from mrig import *
from corvo_de_cinza import feathers, safe_ground, wings

INFO = {"px": 512, "target_z": 1.8, "rim": (.9, .82, .6), "rim_e": 6.5, "colors": 48, "samples": 32,
        "loops": ("idle", "walk", "channel", "exhausted"),
        "fps": {"idle": 7, "walk": 9, "attack": 13, "lance": 12, "wings": 14, "mark": 11, "channel": 9, "exhausted": 5,
                "hit": 12, "death": 10}}
SCALE = 1.55
VARIANTS = {"zacarias": {}, "zacarias_chamas": {"fire": True, "rim": (1, .75, .4)}}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
    INFO["rim"] = V.get("rim", (.9, .82, .6))
set_variant("zacarias")

B = humanoid(1.0)
for s, n in ((1, "L"), (-1, "R")):
    B[f"wing1.{n}"] = ((.07*s, .12, 1.44), (.42*s, .17, 1.62), "chest")
    B[f"wing2.{n}"] = ((.42*s, .17, 1.62), (.82*s, .21, 1.74), f"wing1.{n}")
    B[f"wing3.{n}"] = ((.82*s, .21, 1.74), (1.18*s, .23, 1.77), f"wing2.{n}")
_h, _t = Vector(B["hand.R"][0]), Vector(B["hand.R"][1]); _d = (_t - _h).normalized()
B["sword"] = (tuple(_t - _d*.04), tuple(_t + _d*1.05), "hand.R")
WB = [f"wing{k}.{n}" for k in (1, 2, 3) for n in "LR"]

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
    rnd = random.Random(12)
    porc = stained("z_porcelana", (.55, .53, .48), stain=(.07, .06, .05), amount=.25, scale=12, rough=.3,
                   blotch=(.34, .32, .28), blotch_amt=.4, grime=.8)
    robe = stained("z_tunica", (.4, .37, .3), stain=(.14, .1, .06), amount=.55, scale=3, rough=.9,
                   blotch=(.24, .21, .16), blotch_amt=.6, grime=1.6)
    tabard = stained("z_tabardo", (.06, .07, .1), stain=(.1, .08, .06), amount=.5, scale=3, rough=.85,
                     blotch=(.03, .035, .05), blotch_amt=.6, grime=1.3)
    gold = stained("z_ouro", (.5, .36, .12), stain=(.08, .07, .04), amount=.45, scale=7, metal=1, rough=.35, grime=.3)
    brass = stained("z_latao", (.32, .23, .1), stain=(.09, .2, .14), amount=.6, scale=6, metal=.9, rough=.5,
                    blotch=(.12, .22, .16), blotch_amt=.6, grime=.3)
    lead = stained("z_chumbo", (.17, .17, .18), stain=(.07, .07, .07), amount=.5, scale=6, metal=.6, rough=.6, grime=.4)
    iron = stained("z_ferro", (.07, .06, .055), stain=(.25, .1, .04), amount=.6, scale=7, metal=.8, rough=.55, grime=.3)
    steel = stained("z_aco", (.5, .5, .5), stain=(.2, .15, .1), amount=.35, scale=7, metal=1, rough=.3, grime=.2)
    leather = stained("z_couro", (.09, .055, .035), stain=(.12, .03, .02), amount=.4, scale=4, rough=.6, grime=.5)
    feather = stained("z_pena", (.5, .48, .43), stain=(.12, .1, .08), amount=.55, scale=4, rough=.9,
                      blotch=(.3, .28, .25), blotch_amt=.6, grime=1.1)
    burnt = stained("z_pena_suja", (.2, .19, .17), stain=(.06, .05, .04), amount=.5, scale=5, rough=.9, grime=.4)
    hair = stained("z_cabelo", (.42, .4, .37), stain=(.1, .09, .08), amount=.4, scale=6, rough=.8, grime=.3)
    wax = stained("z_cera", (.42, .07, .05), stain=(.1, .03, .02), amount=.4, scale=6, rough=.4, grime=.2)
    hole = mat("z_buraco", (.004, .004, .005), 0, .95)
    light = glow("z_luz", (1, .9, .62), 14)
    fire = glow("z_fogo", (1, .62, .22), 18) if V.get("fire") else None
    fire2 = glow("z_fogo2", (1, .85, .5), 26) if V.get("fire") else None

    R = Rig(V["name"], B); P = R.P
    R.gexclude = set(WB) | {"sword"}
    safe_ground(R)
    # ------------------------------------------------ corpo magro (pele de porcelana nas mãos e no rosto)
    j = {"pelvis": (0, 0, .95, .13, .1)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .075); j[f"knee{n}"] = (*k, .055); j[f"ank{n}"] = (*a, .04)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"knee{n}"), (f"knee{n}", f"ank{n}")]
    legs = skin_mesh("pernas", j, e, robe); R.bind(legs, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R"])
    for s, n in ((1, "L"), (-1, "R")):  # sandálias de couro com grevas de latão
        k, a, t = P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        bj = {"top": (*k.lerp(a, .35), .06), "ank": (*a, .052), "heel": (*(a + Vector((0, .04, -.05))), .04),
              "toe": (*(t + Vector((0, -.02, 0))), .045, .032)}
        o = skin_mesh(f"bota.{n}", bj, [("top", "ank"), ("ank", "heel"), ("ank", "toe")], leather); R.bind(o, [f"shin.{n}", f"foot.{n}"])
        R.rigid([along("primitive_cylinder_add", brass, k.lerp(a, .08), k.lerp(a, .5), .062, vertices=10),
                 prim("primitive_uv_sphere_add", brass, k + Vector((0, -.03, 0)), (.055, .045, .06), segments=10, ring_count=6)], f"shin.{n}")
    t = {"pelvis": (0, 0, .98, .13, .1), "waist": (0, 0, 1.13, .11, .085), "chest": (0, 0, 1.33, .16, .1),
         "neck": (0, -.01, 1.5, .045), "neck2": (0, -.02, 1.58, .04)}
    te = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, 0))), .06); t[f"el{n}"] = (*el, .042); t[f"wr{n}"] = (*wr, .032)
        te += [("chest", f"sh{n}"), (f"sh{n}", f"el{n}"), (f"el{n}", f"wr{n}")]
    torso = skin_mesh("tronco", t, te, robe)
    R.bind(torso, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])
    # túnica longa até os tornozelos, aberta dos lados, barra dourada; tabardo azul-noite por cima
    tu = skirt("tunica", robe, [(1.5, .1, .085, 0), (1.42, .19, .13, 0), (1.2, .18, .13, .005), (1.0, .17, .13, .01),
                                (.7, .22, .17, .02), (.4, .26, .21, .03), (.12, .3, .25, .04)], jag=.05, seed=4, thick=.012)
    R.bind(tu, ["hips", "spine", "chest", "thigh.L", "thigh.R", "shin.L", "shin.R"], power=3)
    tf = sheet_panel("tabardo_f", tabard, 1.46, .32, .12, .14, -.13, -.1, seed=6)
    tb = sheet_panel("tabardo_c", tabard, 1.46, .36, .12, .14, .12, .1, seed=8)
    for o in (tf, tb): R.bind(o, ["hips", "spine", "chest", "thigh.L", "thigh.R"], power=3)
    ch = []
    # trombeta bordada no tabardo (fios de ouro) e barra dourada
    for a_, b_ in ((( -.05, -.15, 1.25), (.04, -.165, .9)), ((.04, -.165, .9), (.07, -.17, .82)), ((-.07, -.15, 1.27), (-.03, -.15, 1.23))):
        ch.append(along("primitive_cylinder_add", gold, Vector(a_), Vector(b_), .012, vertices=6))
    ch.append(prim("primitive_cone_add", gold, (.07, -.172, .78), (.05, .01, .06), vertices=10, rot=(-90, 0, 0)))
    ch.append(prim("primitive_cube_add", gold, (0, -.155, 1.4), (.11, .006, .01)))
    # gorjal de latão em gomos, cintos cruzados com fivelas
    for k in range(3):
        ch.append(prim("primitive_torus_add", brass, (0, -.005, 1.53 - .035*k), (1, .85, .5), major_radius=.1 + .025*k,
                       minor_radius=.02, major_segments=20, minor_segments=5))
    for s in (1, -1):
        ch.append(along("primitive_cylinder_add", leather, Vector((.15*s, -.12, 1.42)), Vector((-.1*s, -.13, 1.05)), .013, vertices=5))
    ch.append(prim("primitive_torus_add", leather, (0, 0, 1.02), (1.05, .85, 1), major_radius=.15, minor_radius=.018, major_segments=20, minor_segments=4))
    ch.append(prim("primitive_cube_add", gold, (0, -.13, 1.02), (.035, .01, .03)))
    # lacres de cera vermelha com fitas (selos de arauto) presos ao cinto
    for x in (-.11, .12):
        q = Vector((x, -.12, .99)); ch.append(prim("primitive_cylinder_add", wax, q + Vector((0, -.01, -.03)), (.025, .025, .008), vertices=12, rot=(90, 0, 0)))
        ch.append(along("primitive_cube_add", robe, q, q + Vector((0, -.01, -.16)), .01))
    R.rigid(ch, "chest")
    # algemas nos pulsos com correntes partidas penduradas
    for s, n in ((1, "L"), (-1, "R")):
        el, wr = P(f"forearm.{n}"), P(f"hand.{n}"); c = el.lerp(wr, .85); d = (wr - el).normalized()
        cu = prim("primitive_cylinder_add", iron, c, (.05, .05, .03), vertices=12); cu.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        lk = [cu]
        for k in range(5):
            lk.append(prim("primitive_torus_add", iron, c + Vector((0, .01*k, -.05 - .04*k)), (1, 1, 1.5), major_radius=.016,
                           minor_radius=.005, major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
        R.rigid(lk, f"forearm.{n}")
        o, ax, u, sd = R.frame(f"hand.{n}")
        hp = [prim("primitive_uv_sphere_add", porc, o + ax*.04, (.035, .025, .05), segments=10, ring_count=6)]
        hp[0].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        for f in range(4):
            base = o + ax*.08 + sd*(-.027 + .018*f)
            hp.append(along("primitive_cylinder_add", porc, base, base + ax*.07 + u*.03, .009, vertices=6))
        hp.append(along("primitive_cylinder_add", porc, o + ax*.03 - sd*s*.03, o + ax*.07 - sd*s*.05 + u*.03, .01, vertices=6))
        R.rigid(hp, f"hand.{n}")

    # ------------------------------------------------ cabeça: porcelana rachada com ouro, olhos de luz, boca costurada
    hd = []
    hc = Vector((0, -.03, 1.69))
    hd.append(prim("primitive_uv_sphere_add", porc, hc, (.082, .095, .105), segments=16, ring_count=10))
    hd.append(prim("primitive_uv_sphere_add", porc, hc + Vector((0, -.05, -.07)), (.05, .045, .04), segments=10, ring_count=6))
    for s in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", hole, hc + Vector((.032*s, -.083, .01)), (.022, .012, .014), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", light, hc + Vector((.032*s, -.09, .01)), (.011, .006, .007), segments=8, ring_count=5))
    # rachaduras remendadas a ouro (kintsugi)
    for pts in (((.02, -.095, .09), (.04, -.098, .04), (.025, -.1, -.01)), ((-.05, -.08, .07), (-.06, -.075, .0), (-.045, -.085, -.05))):
        pts = [hc + Vector(p) for p in pts]
        for a_, b_ in zip(pts, pts[1:]): hd.append(along("primitive_cylinder_add", gold, a_, b_, .004, vertices=4))
    # boca: bocal enfiado, lábios de porcelana franzidos e costurados com arame
    mp = hc + Vector((0, -.1, -.065))
    for k in range(7):
        a = 2*math.pi*k/7; v = Vector((math.cos(a), 0, math.sin(a)))
        hd.append(along("primitive_cylinder_add", iron, mp + v*.012 + Vector((0, -.004, 0)), mp + v*.04 + Vector((0, .01, 0)), .0028, vertices=4))
    hd.append(prim("primitive_torus_add", porc, mp + Vector((0, .006, 0)), (1, 1, 1), major_radius=.028, minor_radius=.012,
                   major_segments=14, minor_segments=5, rot=(90, 0, 0)))
    # cabelo longo e ralo caindo pelas costas
    for k in range(14):
        a = math.radians(-100 + 200*k/13); x, y = .085*math.sin(a), .09*math.cos(a)
        top = hc + Vector((x*.9, y*.9 + .01, .07))
        hd.append(along("primitive_cone_add", hair, top, top + Vector((x*.6, .05 + .06*abs(math.cos(a)), -.32 - .1*rnd.random())), .018,
                        vertices=4, radius1=1, radius2=.15))
    # auréola de latão quebrada com dentes, presa por uma haste
    hcen = hc + Vector((0, .16, .12))
    arc = []
    for k in range(26):
        a0 = math.radians(-30 + 290*k/26); a1 = math.radians(-30 + 290*(k + 1)/26)
        p0 = hcen + Vector((.19*math.cos(a0), 0, .19*math.sin(a0))); p1 = hcen + Vector((.19*math.cos(a1), 0, .19*math.sin(a1)))
        hd.append(along("primitive_cylinder_add", brass, p0, p1, .013, vertices=6))
        if k % 2 == 0:
            hd.append(along("primitive_cube_add", brass, p0, p0 + (p0 - hcen).normalized()*.035, .01))
    for k in range(8):
        a0 = math.radians(-30 + 290*k/8); p0 = hcen + Vector((.165*math.cos(a0), -.005, .165*math.sin(a0)))
        hd.append(prim("primitive_uv_sphere_add", light, p0, (.011,)*3, segments=6, ring_count=4))
    hd.append(along("primitive_cylinder_add", iron, hc + Vector((0, .07, .02)), hcen + Vector((0, 0, -.19)), .008, vertices=5))
    R.rigid(hd, "head")

    # ------------------------------------------------ a trombeta costurada à boca, com flâmula e lacre de chumbo
    tp = []
    a = mp; d = Vector((0, -.35, -1)).normalized(); L = 1.0; b = a + d*L
    tp.append(along("primitive_cylinder_add", brass, a, a + d*.06, .012, vertices=8))  # bocal
    tp.append(along("primitive_cylinder_add", brass, a + d*.06, b - d*.25, .016, vertices=10))
    for tt in (.25, .5, .7):
        q = a.lerp(b, tt); o = prim("primitive_torus_add", gold, q, (1, 1, 1), major_radius=.02, minor_radius=.006, major_segments=10, minor_segments=4)
        o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); tp.append(o)
    tp.append(along("primitive_cone_add", brass, b - d*.3, b, .14, vertices=18, radius1=.14, radius2=1))
    lid = prim("primitive_cylinder_add", lead, b - d*.01, (.135, .135, .022), vertices=18); lid.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); tp.append(lid)
    side = d.cross(Vector((1, 0, 0))).normalized()
    q0 = d.to_track_quat('Z', 'Y')
    for k in range(6):  # pregos do lacre
        ang = 2*math.pi*k/6; p = b + (q0 @ Vector((.075*math.cos(ang), .075*math.sin(ang), 0)))
        tp.append(along("primitive_cylinder_add", iron, p - d*.03, p + d*.02, .007, vertices=4))
    tp.append(prim("primitive_cylinder_add", wax, b + d*.012, (.035, .035, .008), vertices=12)); tp[-1].rotation_euler = lid.rotation_euler
    # flâmula pendurada do tubo: pano azul-noite rasgado com a trombeta bordada
    fa, fb = a.lerp(b, .3), a.lerp(b, .62)
    bm = bmesh.new(); rows, cols = 6, 6; g = []
    for r in range(rows):
        tt = r/(rows - 1); row = []
        for c in range(cols):
            u = c/(cols - 1); top = fa.lerp(fb, u)
            ln = .32 + .1*math.sin(u*3) - (.12 if u > .7 else 0)
            row.append(bm.verts.new(top + Vector((.006*math.sin(u*7 + tt*3), .02*tt, -ln*tt))))
        g.append(row)
    for r in range(rows - 1):
        for c in range(cols - 1):
            if r == rows - 2 and rnd.random() < .3: continue
            bm.faces.new((g[r][c], g[r][c+1], g[r+1][c+1], g[r+1][c]))
    fl = obj_from_bm("flamula", bm, wax); fl.modifiers.new("s", 'SOLIDIFY').thickness = .008; apply_mods(fl); tp.append(fl)
    mid = fa.lerp(fb, .5) + Vector((-.012, 0, -.15))
    tp.append(prim("primitive_cone_add", gold, mid, (.03, .006, .05), vertices=8, rot=(0, 0, 0)))
    tp.append(along("primitive_cylinder_add", gold, mid + Vector((0, 0, .05)), mid + Vector((0, 0, .12)), .006, vertices=4))
    R.rigid(tp, "head")

    # ------------------------------------------------ espada sagrada: lâmina longa com gravação de luz, guarda de ouro
    o, ax, u, sd = R.frame("hand.R")
    hc_ = P("sword"); sdir = (P("sword", 1) - hc_).normalized()
    sw = [along("primitive_cylinder_add", leather, hc_ - sdir*.1, hc_ + sdir*.08, .02, vertices=8),
          prim("primitive_uv_sphere_add", gold, hc_ - sdir*.12, (.032,)*3, segments=10, ring_count=6)]
    side_ = sdir.cross(Vector((0, 0, 1))).normalized() if abs(sdir.z) < .9 else Vector((1, 0, 0))
    g0 = hc_ + sdir*.1
    sw.append(along("primitive_cylinder_add", gold, g0 - side_*.15, g0 + side_*.15, .016, vertices=8))
    for s2 in (1, -1):
        sw.append(prim("primitive_uv_sphere_add", gold, g0 + side_*.16*s2, (.025,)*3, segments=8, ring_count=5))
    bl = prim("primitive_cube_add", steel, g0 + sdir*.47, (1, 1, 1))
    bl.rotation_euler = Matrix((sdir.cross(side_), side_, sdir)).transposed().to_euler(); bl.scale = (.008, .04, .45); sw.append(bl)
    sw.append(along("primitive_cone_add", steel, g0 + sdir*.92, g0 + sdir*1.05, .04, vertices=4, radius1=1, radius2=0))
    nrm = sdir.cross(side_).normalized()
    for k in range(7):  # gravação de luz ao longo da lâmina
        q = g0 + sdir*(.1 + .11*k)
        sw.append(along("primitive_cube_add", light, q + nrm*.009, q + sdir*.06 + nrm*.009, .007))
    R.rigid(sw, "sword")

    # ------------------------------------------------ asas grandes de penas sujas, algemas e correntes partidas
    DN = Vector((0, -1, 0))
    for s, n in ((1, "L"), (-1, "R")):
        X = lambda v: Vector((v[0]*s, v[1], v[2]))
        lj = {"a": (*X((.07, .12, 1.44)), .055, .04), "b": (*X((.42, .17, 1.62)), .045, .032),
              "c": (*X((.82, .21, 1.74)), .034, .024), "d": (*X((1.18, .23, 1.77)), .018)}
        le = skin_mesh(f"borda.{n}", lj, [("a", "b"), ("b", "c"), ("c", "d")], feather, levels=1)
        R.bind(le, ["chest", f"wing1.{n}", f"wing2.{n}", f"wing3.{n}"], power=6)
        prim_specs = []
        for i in range(10):
            tt = i/9; base = X((1.18 - .36*tt, .23 - .02*tt, 1.77 - .03*tt)); ang = math.radians(14 + 66*tt)
            d = X((math.cos(ang), .12, -math.sin(ang)))
            prim_specs.append((base + Vector((0, .004*i, 0)), d, DN, (.95 - .15*tt)*rnd.uniform(.9, 1.05), .14, rnd.uniform(.7, .85), -.07))
        sec = [(X((.82 - .4*(k + .5)/8, .19 + .002*k, 1.72 - .1*(k + .5)/8)), X((.1, .15, -1)), DN,
                rnd.uniform(.7, .8), .14, rnd.uniform(.7, .85), -.05) for k in range(8)]
        ter = [(X((.42 - .34*(k + .5)/6, .15 + .002*k, 1.6 - .14*(k + .5)/6)), X((-.05, .15, -1)), DN,
                rnd.uniform(.55, .62), .13, rnd.uniform(.75, .9), -.05) for k in range(6)]
        cov = {1: [], 2: [], 3: []}
        for k in range(20):
            tt = (k + .5)/20; x = .08 + 1.08*tt; bn = 1 if x < .42 else (2 if x < .82 else 3)
            z = 1.44 + (1.77 - 1.44)*min(1, tt*1.4)
            cov[bn].append((X((x, .15 + .06*tt - .015, z)), X((.08, .1, -1)), DN, rnd.uniform(.24, .3), .12, .92, -.03))
        w3 = [feathers(f"prim.{n}", prim_specs, feather, burnt, rnd), feathers(f"cob3.{n}", cov[3], feather, burnt, rnd)]
        w2 = [feathers(f"sec.{n}", sec, feather, burnt, rnd), feathers(f"cob2.{n}", cov[2], feather, burnt, rnd)]
        w1 = [feathers(f"ter.{n}", ter, feather, burnt, rnd), feathers(f"cob1.{n}", cov[1], feather, burnt, rnd)]
        # algema de ferro no osso da asa com corrente partida
        c = X((.5, .18, 1.64)); cu = prim("primitive_torus_add", iron, c, (1, 1, 1.4), major_radius=.05, minor_radius=.016,
                                          major_segments=14, minor_segments=5); cu.rotation_euler = (0, math.radians(70*s), 0); w2.append(cu)
        for k in range(7):
            w2.append(prim("primitive_torus_add", iron, c + Vector((.01*s*k, .02*k, -.05 - .045*k)), (1, 1, 1.5), major_radius=.018,
                           minor_radius=.0055, major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
        if fire:  # fogo sagrado nas pontas e na borda das asas
            for wl, x0, x1, cnt in ((w3, .82, 1.18, 9), (w2, .42, .82, 7), (w1, .1, .42, 4)):
                for k in range(cnt):
                    x = x0 + (x1 - x0)*(k + .5)/cnt
                    z = 1.44 + (1.77 - 1.44)*min(1, (x - .07)/1.11*1.4)
                    drop = .25 + .55*(x - .1)/1.1
                    for m_, sc_ in ((fire, 1), (fire2, .55)):
                        base = X((x, .2, z - drop*rnd.uniform(.4, 1)))
                        wl.append(along("primitive_cone_add", m_, base, base + Vector((0, .05, .18 + .1*rnd.random()))*sc_, .05*sc_,
                                        vertices=6, radius1=1, radius2=0))
        R.rigid(w3, f"wing3.{n}"); R.rigid(w2, f"wing2.{n}"); R.rigid(w1, f"wing1.{n}")
    R.arm.scale = [SCALE]*3
    return R, INFO

def sheet_panel(name, m, z0, z1, w0, w1, y, curve, rows=7, cols=6, seed=1):
    rnd = random.Random(seed); bm = bmesh.new(); g = []
    for r in range(rows):
        tt = r/(rows - 1); z = z0 + (z1 - z0)*tt; w = w0 + (w1 - w0)*tt; row = []
        for c in range(cols):
            u = c/(cols - 1)*2 - 1
            row.append(bm.verts.new((u*w, y + curve*u*u*0 + (-.03*tt if y < 0 else .03*tt), z + (rnd.uniform(-.07, .02) if r == rows - 1 else 0))))
        g.append(row)
    for r in range(rows - 1):
        for c in range(cols - 1):
            bm.faces.new((g[r][c], g[r][c+1], g[r+1][c+1], g[r+1][c]))
    o = obj_from_bm(name, bm, m); o.modifiers.new("s", 'SOLIDIFY').thickness = .01; apply_mods(o)
    return o

# ======================================================================= animações
FOLD = wings(-30, -20, -14, 78, 34, 22)   # asas recolhidas, caídas para trás
BASE = {"spine": {"x": 4}, "chest": {"x": 2}, "neck": {"x": 4}, "head": {"x": 10},
        "thigh.L": {"x": -4, "y": -4}, "thigh.R": {"x": 4, "y": 4}, "shin.L": {"bend": 6}, "shin.R": {"bend": 4},
        "upper_arm.L": {"y": 16, "x": -42, "z": -18}, "forearm.L": {"bend": -62}, "hand.L": {"x": -6},
        "upper_arm.R": {"y": -18, "x": -26}, "forearm.R": {"bend": -34}, "hand.R": {"x": -5}}

def M(*p): return merge(BASE, FOLD, *p)

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; b, c = math.sin(t), math.cos(t)
        idle.append(M(wings(4*b, 3*c, 2*b, 2*c, 0, 0), {"chest": {"x": 2*b}, "head": {"x": -2*b, "z": 4*c},
                                                       "upper_arm.R": {"x": -3*b}, "hand.R": {"x": 4*c}}))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 22*s
        walk.append(M(wings(3*c, 4*s, 2, 0, 0, 0), {"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                       "shin.L": {"bend": 6 + 40*max(0, c)**1.3}, "shin.R": {"bend": 6 + 40*max(0, -c)**1.3},
                       "foot.L": {"x": .3*th - 10*max(0, c)}, "foot.R": {"x": -.3*th - 10*max(0, -c)},
                       "hips": {"z": 5*s}, "chest": {"z": -6*s}, "head": {"z": 4*s}, "upper_arm.R": {"x": -8*s}}))
    # espada sagrada: ergue sobre o ombro e corta na diagonal, as asas se abrem um pouco no golpe
    up = M(wings(14, 4, 2, 10, 10, 6), {"upper_arm.R": {"x": -150, "y": 25}, "forearm.R": {"bend": -60}, "hand.R": {"x": -20},
                                       "chest": {"z": -24, "x": -8}, "spine": {"z": -8}, "head": {"z": 10},
                                       "thigh.L": {"x": -12}, "thigh.R": {"x": 10}})
    cut = M(wings(28, 8, 4, -10, 0, 0), {"upper_arm.R": {"x": -40, "y": 8, "z": 30}, "forearm.R": {"bend": -6}, "hand.R": {"x": 10},
                                         "chest": {"z": 30, "x": 16}, "spine": {"x": 8, "z": 8}, "head": {"z": -10, "x": -6},
                                         "thigh.L": {"x": -32}, "shin.L": {"bend": 22}, "thigh.R": {"x": 18}, "root": (0, -.2, 0)})
    attack = keys_to_frames([(0, M()), (.3, up), (.5, cut), (.7, merge(cut, {"upper_arm.R": {"x": 12}})), (1, M())], 10)
    # lança do juízo: puxa a mão esquerda para trás (forma a lança de luz) e arremessa em linha reta
    draw = M(wings(30, 10, 6, 20, 10, 8), {"upper_arm.L": {"x": -150, "y": -40, "z": 40}, "forearm.L": {"bend": -70}, "hand.L": {"x": -10},
                                           "chest": {"z": 34, "x": -10}, "spine": {"z": 12}, "head": {"z": -18},
                                           "thigh.L": {"x": 10}, "thigh.R": {"x": -16}, "root": (0, .08, 0)})
    throw = M(wings(40, 14, 8, -20, -10, -6), {"upper_arm.L": {"x": -80, "y": -10, "z": -20}, "forearm.L": {"bend": -4}, "hand.L": {"x": 20},
                                               "chest": {"z": -30, "x": 14}, "spine": {"z": -10}, "head": {"z": 14},
                                               "thigh.L": {"x": -34}, "shin.L": {"bend": 20}, "thigh.R": {"x": 22}, "root": (0, -.22, 0)})
    lance = keys_to_frames([(0, M()), (.22, draw), (.45, merge(draw, {"chest": {"z": 4}})), (.58, throw),
                            (.75, merge(throw, {"upper_arm.L": {"x": 10}})), (1, M())], 12)
    # asas cortantes: abre as asas e gira uma volta inteira com elas esticadas
    spin = []
    for i in range(12):
        k = i/11; open_ = min(1, i/2) if i < 10 else (11 - i)/2
        spin.append(M(wings(60*open_, 6*open_, 2*open_, -30*open_, -26*open_, -18*open_),
                      {"hips": {"z": -360*k*(i < 11)}, "upper_arm.R": {"y": -60*open_}, "upper_arm.L": {"y": 50*open_},
                       "chest": {"x": 6, "z": -10*open_}, "thigh.L": {"x": -10}, "thigh.R": {"x": 6},
                       "shin.L": {"bend": 20}, "shin.R": {"bend": 16}}))
    # marca do juízo: aponta a espada para o céu, segura, e baixa apontando o alvo
    sky = M(wings(46, 14, 8, -10, -6, -4), {"upper_arm.R": {"x": -175, "y": -8}, "forearm.R": {"bend": -6}, "hand.R": {"x": -40},
                                            "chest": {"x": -14}, "spine": {"x": -6}, "head": {"x": -26},
                                            "upper_arm.L": {"x": -30, "y": 50}, "forearm.L": {"bend": -20}})
    point = M(wings(30, 10, 4, -6, -4, -2), {"upper_arm.R": {"x": -90, "y": -4}, "forearm.R": {"bend": -4}, "hand.R": {"x": -30},
                                            "chest": {"x": 8, "z": -10}, "head": {"x": -4}, "thigh.L": {"x": -20}, "shin.L": {"bend": 10}})
    mark = keys_to_frames([(0, M()), (.25, sky), (.45, merge(sky, {"head": {"x": -4}})), (.6, sky), (.78, point),
                           (1, M())], 12)
    # primeira nota (loop): paira no alto, asas abertas, ergue a trombeta e sopra, o corpo vibrando
    channel = []
    for i in range(8):
        t = i/8*2*math.pi; b = math.sin(t); v = math.sin(4*t)
        channel.append(M(wings(52 + 10*b, 14 + 4*b, 8, -20, -14, -10), {"ground": None, "root": (0, 0, .7 + .05*b),
                          "spine": {"x": -14 + 1.5*v}, "chest": {"x": -14}, "neck": {"x": -14}, "head": {"x": -32 + 2*v},
                          "upper_arm.L": {"x": -120, "y": -8, "z": -20}, "forearm.L": {"bend": -40}, "hand.L": {"x": -10},
                          "upper_arm.R": {"x": -20, "y": -50}, "forearm.R": {"bend": -20}, "hand.R": {"x": 20},
                          "thigh.L": {"x": -12}, "thigh.R": {"x": 8}, "shin.L": {"bend": 40}, "shin.R": {"bend": 30},
                          "foot.L": {"x": 30}, "foot.R": {"x": 30}}))
    # exausto (loop): de joelho, apoiado na espada cravada, asas caídas no chão, ofegando
    exhausted = []
    for i in range(6):
        t = i/6*2*math.pi; b = math.sin(t)
        exhausted.append(M(wings(-12 + 2*b, -14, -10, 40, 30, 24), {"thigh.L": {"x": -80}, "shin.L": {"bend": 90}, "foot.L": {"x": -6},
                            "thigh.R": {"x": 10, "y": 6}, "shin.R": {"bend": 100}, "foot.R": {"x": 40},
                            "spine": {"x": 20 + 2*b}, "chest": {"x": 14 + 3*b}, "neck": {"x": 10}, "head": {"x": 20 + 3*b},
                            "upper_arm.R": {"x": -40, "y": -10}, "forearm.R": {"bend": -40}, "hand.R": {"x": 60},
                            "upper_arm.L": {"x": -20, "y": 20}, "forearm.L": {"bend": -40}, "gb": ["foot.L", "shin.R", "foot.R"]}))
    hitp = M(wings(30, 14, 10, 10, 6, 4), {"chest": {"x": -16, "z": 8}, "spine": {"x": -6}, "head": {"x": -16, "z": 12},
                                          "upper_arm.L": {"y": -10, "x": 18}, "upper_arm.R": {"y": 16, "x": 14}, "root": (0, .08, 0)})
    hit = [lerp_pose(M(), hitp, .6), hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: as asas se abrem num último espasmo, cai de joelhos e tomba de lado sobre uma asa
    kneel = M(wings(10, -10, -6, 30, 20, 14), {"thigh.L": {"x": -80}, "thigh.R": {"x": -70}, "shin.L": {"bend": 105}, "shin.R": {"bend": 110},
                                              "chest": {"x": 18}, "head": {"x": 26}, "upper_arm.R": {"x": 10, "y": -10}, "forearm.R": {"bend": -10},
                                              "upper_arm.L": {"x": 10, "y": 10}})
    spasm = M(wings(70, 20, 10, -20, -10, -6), {"chest": {"x": -24}, "head": {"x": -30}, "upper_arm.L": {"x": -60, "y": -40},
                                               "upper_arm.R": {"x": -60, "y": 40}, "root": (0, .05, 0)})
    fall = merge(kneel, {"hips": {"x": 30, "y": 30}, "spine": {"x": 10}, "ground": .1})
    down = {"hips": {"x": 8, "y": 84}, "spine": {"x": 6}, "chest": {"x": 4}, "head": {"z": -20, "x": 14},
            "upper_arm.L": {"x": -40, "y": 30}, "upper_arm.R": {"x": -80, "y": -40}, "forearm.L": {"bend": -30}, "forearm.R": {"bend": -10},
            "thigh.L": {"x": -40}, "thigh.R": {"x": -20}, "shin.L": {"bend": 70}, "shin.R": {"bend": 40}, "ground": .05,
            "gb": ["hips", "spine", "chest", "head", "thigh.L", "thigh.R", "shin.L", "shin.R"]}
    down = merge(down, wings(-6, -4, -2, 50, 20, 10))
    death = keys_to_frames([(0, hitp), (.15, spasm), (.32, merge(spasm, {"head": {"x": -6}})), (.5, kneel), (.68, fall), (.86, down), (1, down)], 14)
    return {"idle": idle, "walk": walk, "attack": attack, "lance": lance, "wings": spin, "mark": mark, "channel": channel,
            "exhausted": exhausted, "hit": hit, "death": death}
