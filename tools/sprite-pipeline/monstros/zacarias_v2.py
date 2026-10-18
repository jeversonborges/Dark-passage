# Zacarias, o Arauto (chefe do andar 3: Câmara da Trombeta), visual 2 pedido pelo Jefin (11/10): "anjo guerreiro,
# com máscara e asa astral, ele todo é astral abaixo da armadura; carrega um ataque devastador por 4 s que mata
# o jogador se ele tomar o golpe".
# Alto (~2,8 m). Armadura gótica de prata enegrecida com filetes de ouro: peitoral com o sol do Coro, lâminas da
# barriga, ombreiras em três camadas, braçais, manoplas, coxotes, joelheiras, grevas e sapatos de placas, gorjal.
# Tabardo marfim com barra de ouro na frente e atrás. Por baixo da armadura não há corpo: só luz astral (azul-branca),
# que aparece nas juntas (cintura, cotovelos, joelhos, pescoço) e vaza pelas frestas da máscara. Máscara de ouro lisa,
# sem expressão, com duas frestas de olho; atrás dela, uma cabeça de luz com "cabelo" de chamas astrais e a auréola.
# Asas de penas de luz astral. Montante de duas mãos com runas acesas e guarda larga de ouro.
# Brilho: uma cor só, astral azul-branca (corpo, asas, frestas, runas, aura).
# Animações: idle, walk, attack (corte diagonal), charge (loop: ergue o montante com as duas mãos acima da cabeça,
# asas abertas, a aura na ponta da lâmina crescendo; o jogo repete por 4 s), release (desce o montante no chão à
# frente num golpe só: a aura estoura e some), hit, death (as asas se abrem num espasmo, cai de joelhos e tomba).
# Visual 1 (anjo de porcelana com a trombeta) ficou em zacarias_v1.py.
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion, Matrix
from mrig import *
from corvo_de_cinza import feathers, safe_ground, wings

INFO = {"px": 512, "target_z": 1.8, "rim": (.75, .85, 1), "rim_e": 6.5, "colors": 48, "samples": 32,
        "loops": ("idle", "walk", "charge"),
        "fps": {"idle": 7, "walk": 9, "attack": 13, "charge": 10, "release": 14, "hit": 12, "death": 10}}
SCALE = 1.5
V = {"name": "zacarias"}
def set_variant(name): pass

B = humanoid(1.0)
for s, n in ((1, "L"), (-1, "R")):
    B[f"wing1.{n}"] = ((.07*s, .12, 1.44), (.42*s, .17, 1.62), "chest")
    B[f"wing2.{n}"] = ((.42*s, .17, 1.62), (.82*s, .21, 1.74), f"wing1.{n}")
    B[f"wing3.{n}"] = ((.82*s, .21, 1.74), (1.18*s, .23, 1.77), f"wing2.{n}")
_h, _t = Vector(B["hand.R"][0]), Vector(B["hand.R"][1]); _d = (_t - _h).normalized()
B["sword"] = (tuple(_t - _d*.04), tuple(_t + _d*1.25), "hand.R")
_st = _t + _d*1.25
B["aura"] = (tuple(_st), tuple(_st + _d*.1), "sword")
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

def sheet_panel(name, m, z0, z1, w0, w1, y, curve, rows=7, cols=6, seed=1):
    rnd = random.Random(seed); bm = bmesh.new(); g = []
    for r in range(rows):
        tt = r/(rows - 1); z = z0 + (z1 - z0)*tt; w = w0 + (w1 - w0)*tt; row = []
        for c in range(cols):
            u = c/(cols - 1)*2 - 1
            row.append(bm.verts.new((u*w, y + (-.03*tt if y < 0 else .03*tt), z + (rnd.uniform(-.07, .02) if r == rows - 1 else 0))))
        g.append(row)
    for r in range(rows - 1):
        for c in range(cols - 1):
            bm.faces.new((g[r][c], g[r][c+1], g[r+1][c+1], g[r+1][c]))
    o = obj_from_bm(name, bm, m); o.modifiers.new("s", 'SOLIDIFY').thickness = .01; apply_mods(o)
    return o

def build():
    rnd = random.Random(12)
    silver = stained("z_prata", (.5, .51, .55), stain=(.2, .19, .19), amount=.25, scale=5, metal=.55, rough=.42,
                     blotch=(.38, .38, .42), blotch_amt=.3, grime=.3)
    dark = stained("z_prata_escura", (.12, .12, .14), stain=(.04, .04, .05), amount=.4, scale=6, metal=1, rough=.4, grime=.3)
    gold = stained("z_ouro", (.55, .4, .13), stain=(.1, .08, .04), amount=.4, scale=7, metal=1, rough=.3, grime=.2)
    cloth = stained("z_tabardo", (.42, .39, .32), stain=(.14, .1, .06), amount=.55, scale=3, rough=.9,
                    blotch=(.26, .23, .18), blotch_amt=.6, grime=1.4)
    leather = stained("z_couro", (.07, .045, .03), stain=(.1, .03, .02), amount=.4, scale=4, rough=.6, grime=.4)
    steel = stained("z_aco", (.5, .52, .55), stain=(.15, .15, .17), amount=.3, scale=7, metal=1, rough=.25, grime=.1)
    hole = mat("z_buraco", (.003, .004, .006), 0, .95)
    astral = glow("z_astral", (.2, .45, 1), 1.6)
    astral2 = glow("z_astral2", (.45, .72, 1), 3.2)
    core = glow("z_astral3", (.8, .92, 1), 8)
    wingA = mat("z_asa", (.2, .36, .8), 0, .45, emit=(.12, .3, 1), strength=.7)   # pena de luz com forma (sombreada)
    wingB = glow("z_asa_ponta", (.4, .68, 1), 2.4)

    R = Rig(V["name"], B); P = R.P
    R.gexclude = set(WB) | {"sword", "aura"}
    safe_ground(R)
    # ------------------------------------------------ corpo de luz astral (aparece nas juntas)
    j = {"pelvis": (0, 0, .95, .12, .09)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .07); j[f"knee{n}"] = (*k, .055); j[f"ank{n}"] = (*a, .04)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"knee{n}"), (f"knee{n}", f"ank{n}")]
    R.bind(skin_mesh("pernas", j, e, astral), ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R"])
    t = {"pelvis": (0, 0, .98, .12, .09), "waist": (0, 0, 1.13, .1, .075), "chest": (0, 0, 1.33, .15, .095),
         "neck": (0, -.01, 1.5, .045), "neck2": (0, -.02, 1.58, .04)}
    te = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, 0))), .055); t[f"el{n}"] = (*el, .04); t[f"wr{n}"] = (*wr, .03)
        te += [("chest", f"sh{n}"), (f"sh{n}", f"el{n}"), (f"el{n}", f"wr{n}")]
    R.bind(skin_mesh("tronco", t, te, astral), ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])

    # ------------------------------------------------ peitoral, lâminas da barriga, gorjal, tabardo
    ch = []
    ch.append(prim("primitive_uv_sphere_add", silver, (0, -.02, 1.34), (.19, .135, .17), segments=20, ring_count=12))
    ch.append(prim("primitive_uv_sphere_add", silver, (0, .03, 1.34), (.18, .12, .16), segments=16, ring_count=10))  # costas
    ch.append(along("primitive_cylinder_add", silver, (0, -.15, 1.47), (0, -.155, 1.22), .012, vertices=6))      # quilha
    # sol do Coro em ouro no peito: disco com raios
    sun = Vector((0, -.15, 1.36))
    ch.append(prim("primitive_cylinder_add", gold, sun, (.04, .04, .008), vertices=16, rot=(90, 0, 0)))
    for k in range(12):
        a = 2*math.pi*k/12; L_ = .085 if k % 2 == 0 else .06
        ch.append(along("primitive_cone_add", gold, sun + Vector((math.cos(a)*.035, -.002, math.sin(a)*.035)),
                        sun + Vector((math.cos(a)*L_, .01, math.sin(a)*L_)), .01, vertices=4, radius1=1, radius2=0))
    ch.append(prim("primitive_cylinder_add", core, sun + Vector((0, -.008, 0)), (.018, .018, .003), vertices=12, rot=(90, 0, 0)))
    # filete de ouro na borda do peitoral
    ch.append(prim("primitive_torus_add", gold, (0, -.02, 1.2), (1.2, .9, 1), major_radius=.15, minor_radius=.01,
                   major_segments=22, minor_segments=4))
    # gorjal em gomos
    for k in range(3):
        ch.append(prim("primitive_torus_add", silver if k else gold, (0, -.005, 1.52 - .03*k), (1, .85, .55), major_radius=.085 + .025*k,
                       minor_radius=.02, major_segments=20, minor_segments=5))
    R.rigid(ch, "chest")
    sp = []
    for k, z in enumerate((1.14, 1.08)):   # lâminas da barriga (frestas mostram a luz)
        sp.append(prim("primitive_cylinder_add", silver, (0, -.01, z), (.15 - .01*k, .115 - .01*k, .026), vertices=18))
        sp.append(prim("primitive_torus_add", gold, (0, -.01, z - .024), (1.2, .92, 1), major_radius=.125 - .008*k, minor_radius=.005,
                       major_segments=18, minor_segments=4))
    R.rigid(sp, "spine")
    hp_ = [prim("primitive_torus_add", leather, (0, 0, 1.0), (1.05, .85, 1), major_radius=.15, minor_radius=.02, major_segments=20, minor_segments=4),
           prim("primitive_cube_add", gold, (0, -.135, 1.0), (.04, .01, .035))]
    for x in (-.15, .15):   # escarcelas laterais
        hp_.append(prim("primitive_uv_sphere_add", silver, (x, 0, .93), (.07, .1, .1), segments=12, ring_count=8))
    R.rigid(hp_, "hips")
    tf = sheet_panel("tabardo_f", cloth, .99, .3, .11, .14, -.13, 0, seed=6)
    tb = sheet_panel("tabardo_c", cloth, .99, .26, .12, .15, .12, 0, seed=8)
    for o in (tf, tb): R.bind(o, ["hips", "thigh.L", "thigh.R"], power=3)
    hm = [prim("primitive_cube_add", gold, (0, -.14, .38), (.14, .006, .012)), prim("primitive_cube_add", gold, (0, .128, .34), (.15, .006, .012))]
    R.rigid(hm, "hips")

    # ------------------------------------------------ ombreiras, braçais, cotoveleiras, manoplas
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        pa = []
        for k in range(3):
            c = sh + Vector((.03*s + .015*k*s, 0, .07 - .045*k))
            pa.append(prim("primitive_uv_sphere_add", silver, c, (.13 - .015*k, .12 - .01*k, .075), segments=16, ring_count=8,
                           rot=(0, -28*s - 10*k*s, 0)))
            pa.append(prim("primitive_torus_add", gold, c + Vector((0, 0, -.035)), (1, .92, .45), major_radius=.12 - .015*k,
                           minor_radius=.008, major_segments=18, minor_segments=4, rot=(0, -28*s - 10*k*s, 0)))
        pa.append(along("primitive_cylinder_add", silver, sh.lerp(el, .3), sh.lerp(el, .85), .058, vertices=12))
        R.rigid(pa, f"upper_arm.{n}")
        fa = [along("primitive_cone_add", silver, el.lerp(wr, .15), el.lerp(wr, .92), .06, vertices=12, radius1=.8, radius2=1),
              prim("primitive_uv_sphere_add", silver, el + Vector((0, .03, 0)), (.05, .045, .05), segments=10, ring_count=6),
              prim("primitive_torus_add", gold, el.lerp(wr, .9), (1, 1, 1), major_radius=.062, minor_radius=.008, major_segments=14, minor_segments=4)]
        fa[-1].rotation_euler = (wr - el).to_track_quat('Z', 'Y').to_euler()
        R.rigid(fa, f"forearm.{n}")
        o, ax, u, sd = R.frame(f"hand.{n}")
        hp = [prim("primitive_uv_sphere_add", silver, o + ax*.045, (.04, .03, .055), segments=10, ring_count=6)]
        hp[0].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        for f in range(4):
            base = o + ax*.085 + sd*(-.027 + .018*f)
            hp.append(along("primitive_cylinder_add", dark, base, base + ax*.06 + u*.035, .011, vertices=6))
        hp.append(along("primitive_cylinder_add", dark, o + ax*.03 - sd*s*.035, o + ax*.07 - sd*s*.055 + u*.03, .012, vertices=6))
        R.rigid(hp, f"hand.{n}")

    # ------------------------------------------------ pernas: coxotes, joelheiras, grevas, sapatos de placas
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a, tt = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        R.rigid([along("primitive_cone_add", silver, h.lerp(k, .12), h.lerp(k, .85), .085, vertices=12, radius1=1, radius2=.78),
                 prim("primitive_uv_sphere_add", silver, h.lerp(k, .2) + Vector((.02*s, -.06, 0)), (.07, .04, .1), segments=10, ring_count=6)],
                f"thigh.{n}")
        R.rigid([prim("primitive_uv_sphere_add", silver, k + Vector((0, -.045, .01)), (.055, .04, .06), segments=12, ring_count=8),
                 prim("primitive_torus_add", gold, k + Vector((0, -.05, .01)), (1, .6, 1), major_radius=.05, minor_radius=.007,
                      major_segments=12, minor_segments=4, rot=(90, 0, 0)),
                 along("primitive_cone_add", silver, k.lerp(a, .15), k.lerp(a, .95), .062, vertices=12, radius1=1, radius2=.75)],
                f"shin.{n}")
        ft = [prim("primitive_uv_sphere_add", silver, a.lerp(tt, .5) + Vector((0, 0, -.02)), (.055, .1, .04), segments=12, ring_count=8)]
        for j_ in range(3):
            ft.append(prim("primitive_torus_add", dark, a.lerp(tt, .3 + .2*j_) + Vector((0, 0, -.005)), (1, .9, .6), major_radius=.05 - .006*j_,
                           minor_radius=.006, major_segments=12, minor_segments=4, rot=(80, 0, 0)))
        R.rigid(ft, f"foot.{n}")

    # ------------------------------------------------ cabeça: luz astral, máscara de ouro, chamas, auréola
    hc = Vector((0, -.02, 1.7)); hd = []
    hd.append(prim("primitive_uv_sphere_add", astral, hc, (.075, .085, .095), segments=16, ring_count=10))
    hd.append(prim("primitive_uv_sphere_add", gold, hc + Vector((0, -.035, -.005)), (.074, .06, .1), segments=18, ring_count=12))   # máscara
    hd.append(prim("primitive_uv_sphere_add", gold, hc + Vector((0, -.08, .005)), (.012, .02, .045), segments=8, ring_count=6))     # nariz
    for s in (1, -1):   # frestas dos olhos, com a luz vazando
        hd.append(prim("primitive_cube_add", hole, hc + Vector((.032*s, -.088, .02)), (.026, .008, .006), rot=(0, 8*s, -8*s)))
        hd.append(prim("primitive_cube_add", core, hc + Vector((.032*s, -.093, .02)), (.022, .004, .0035), rot=(0, 8*s, -8*s)))
    for k in range(5):   # frestas de respiro na boca
        x = -.024 + .012*k
        hd.append(prim("primitive_cube_add", hole, hc + Vector((x, -.088, -.05)), (.003, .006, .012)))
    hd.append(prim("primitive_torus_add", gold, hc + Vector((0, -.01, .0)), (1, 1.05, 1.3), major_radius=.082, minor_radius=.006,
                   major_segments=20, minor_segments=4, rot=(90, 0, 0)))   # borda da máscara
    # crista: lâmina de ouro do topo para trás
    for k in range(5):
        a = math.radians(60 + 25*k); q = hc + Vector((0, .1*math.cos(a)*-1 + .0, .1*math.sin(a)))
        hd.append(along("primitive_cone_add", gold, q, q + Vector((0, .04 + .02*k, .07 - .012*k)), .02, vertices=4, radius1=1, radius2=0))
    # cabelo de chamas astrais saindo de trás da máscara
    for k in range(9):
        a = math.radians(-70 + 140*k/8); q = hc + Vector((math.sin(a)*.07, .05 + math.cos(a)*.03, .05))
        tip = q + Vector((math.sin(a)*.05, .16 + rnd.uniform(0, .08), .1 + rnd.uniform(0, .08)))
        hd.append(along("primitive_cone_add", astral if k % 2 else astral2, q, tip, .022, vertices=6, radius1=1, radius2=0))
    # auréola de luz atrás da cabeça, com espinhos
    hcq = hc + Vector((0, .1, .08))
    hd.append(prim("primitive_torus_add", astral2, hcq, (1, 1, 1), major_radius=.16, minor_radius=.008, major_segments=28, minor_segments=4, rot=(80, 0, 0)))
    for k in range(12):
        a = 2*math.pi*k/12; d = Vector((math.cos(a), 0, math.sin(a)))
        q = hcq + Quaternion((1, 0, 0), math.radians(-10)) @ (d*.16)
        hd.append(along("primitive_cone_add", astral2, q, q + Quaternion((1, 0, 0), math.radians(-10)) @ (d*.05), .008, vertices=4, radius1=1, radius2=0))
    R.rigid(hd, "head")

    # ------------------------------------------------ montante: lâmina longa e larga com runas de luz, guarda de ouro
    hc_ = P("sword"); sdir = (P("sword", 1) - hc_).normalized()
    side_ = sdir.cross(Vector((0, 0, 1))).normalized() if abs(sdir.z) < .9 else Vector((1, 0, 0))
    nrm = sdir.cross(side_).normalized()
    sw = [along("primitive_cylinder_add", leather, hc_ - sdir*.18, hc_ + sdir*.1, .022, vertices=8),
          prim("primitive_uv_sphere_add", gold, hc_ - sdir*.2, (.035,)*3, segments=10, ring_count=6)]
    g0 = hc_ + sdir*.12
    sw.append(along("primitive_cylinder_add", gold, g0 - side_*.22, g0 + side_*.22, .02, vertices=8))
    for s2 in (1, -1):
        sw.append(along("primitive_cone_add", gold, g0 + side_*.2*s2, g0 + side_*.27*s2 + sdir*.06, .03, vertices=6, radius1=1, radius2=.2))
    sw.append(prim("primitive_uv_sphere_add", core, g0, (.025, .025, .025), segments=8, ring_count=6))
    bl = prim("primitive_cube_add", steel, g0 + sdir*.58, (1, 1, 1))
    bl.rotation_euler = Matrix((nrm, side_, sdir)).transposed().to_euler(); bl.scale = (.01, .06, .56); sw.append(bl)
    sw.append(along("primitive_cone_add", steel, g0 + sdir*1.13, g0 + sdir*1.3, .06, vertices=4, radius1=1, radius2=0))
    for k in range(9):   # runas de luz no meio da lâmina, dos dois lados
        q = g0 + sdir*(.1 + .11*k)
        for sg in (1, -1):
            sw.append(along("primitive_cube_add", astral2, q + nrm*.011*sg, q + sdir*.06 + nrm*.011*sg, .008))
    R.rigid(sw, "sword")
    # aura do golpe carregado, na ponta da lâmina (escondida fora de charge/release)
    ac = P("aura"); au = [prim("primitive_uv_sphere_add", core, ac, (.12, .12, .12), segments=14, ring_count=10),
                         prim("primitive_uv_sphere_add", astral, ac, (.24, .24, .24), segments=16, ring_count=10)]
    for k, r_ in enumerate((.32, .42)):
        au.append(prim("primitive_torus_add", astral2, ac, (1, 1, 1), major_radius=r_, minor_radius=.012, major_segments=28,
                       minor_segments=4, rot=(30 + 60*k, 20*k, 0)))
    for k in range(8):
        a = 2*math.pi*k/8; d = Vector((math.cos(a), math.sin(a), .3*math.sin(3*a))).normalized()
        au.append(along("primitive_cone_add", astral2, ac + d*.1, ac + d*.38, .025, vertices=4, radius1=1, radius2=0))
    R.rigid(au, "aura")

    # ------------------------------------------------ asas de penas de luz astral
    DN = Vector((0, -1, 0))
    for s, n in ((1, "L"), (-1, "R")):
        X = lambda v: Vector((v[0]*s, v[1], v[2]))
        lj = {"a": (*X((.07, .12, 1.44)), .045, .035), "b": (*X((.42, .17, 1.62)), .035, .026),
              "c": (*X((.82, .21, 1.74)), .026, .02), "d": (*X((1.18, .23, 1.77)), .014)}
        R.bind(skin_mesh(f"borda.{n}", lj, [("a", "b"), ("b", "c"), ("c", "d")], astral2, levels=1),
               ["chest", f"wing1.{n}", f"wing2.{n}", f"wing3.{n}"], power=6)
        prim_specs = []
        for i in range(11):
            tt = i/10; base = X((1.18 - .36*tt, .23 - .02*tt, 1.77 - .03*tt)); ang = math.radians(14 + 66*tt)
            d = X((math.cos(ang), .12, -math.sin(ang)))
            prim_specs.append((base + Vector((0, .004*i, 0)), d, DN, (1.05 - .15*tt)*rnd.uniform(.92, 1.05), .13, rnd.uniform(.55, .7), -.07))
        sec = [(X((.82 - .4*(k + .5)/8, .19 + .002*k, 1.72 - .1*(k + .5)/8)), X((.1, .15, -1)), DN,
                rnd.uniform(.75, .85), .13, rnd.uniform(.6, .75), -.05) for k in range(8)]
        ter = [(X((.42 - .34*(k + .5)/6, .15 + .002*k, 1.6 - .14*(k + .5)/6)), X((-.05, .15, -1)), DN,
                rnd.uniform(.58, .66), .12, rnd.uniform(.65, .8), -.05) for k in range(6)]
        cov = {1: [], 2: [], 3: []}
        for k in range(20):
            tt = (k + .5)/20; x = .08 + 1.08*tt; bn = 1 if x < .42 else (2 if x < .82 else 3)
            z = 1.44 + (1.77 - 1.44)*min(1, tt*1.4)
            cov[bn].append((X((x, .15 + .06*tt - .015, z)), X((.08, .1, -1)), DN, rnd.uniform(.24, .3), .11, .8, -.03))
        w3 = [feathers(f"prim.{n}", prim_specs, wingA, wingB, rnd), feathers(f"cob3.{n}", cov[3], wingA, wingB, rnd)]
        w2 = [feathers(f"sec.{n}", sec, wingA, wingB, rnd), feathers(f"cob2.{n}", cov[2], wingA, wingB, rnd)]
        w1 = [feathers(f"ter.{n}", ter, wingA, wingB, rnd), feathers(f"cob1.{n}", cov[1], wingA, wingB, rnd)]
        # suporte de prata nas costas onde a asa nasce
        w1.append(prim("primitive_uv_sphere_add", silver, X((.12, .14, 1.46)), (.06, .05, .08), segments=10, ring_count=6))
        R.rigid(w3, f"wing3.{n}"); R.rigid(w2, f"wing2.{n}"); R.rigid(w1, f"wing1.{n}")
    R.arm.scale = [SCALE]*3
    return R, INFO

# ======================================================================= animações
FOLD = wings(-24, -18, -12, 70, 30, 20)   # asas meio recolhidas para trás
BASE = {"spine": {"x": 2}, "chest": {"x": 0}, "neck": {"x": 2}, "head": {"x": 4},
        "thigh.L": {"x": -6, "y": -6}, "thigh.R": {"x": 6, "y": 6}, "shin.L": {"bend": 8}, "shin.R": {"bend": 6},
        "upper_arm.L": {"y": 22, "x": -20, "z": -10}, "forearm.L": {"bend": -30}, "hand.L": {"x": -6},
        "upper_arm.R": {"y": -18, "x": -26}, "forearm.R": {"bend": -34}, "hand.R": {"x": -5}}
OFF = {"scale": {"aura": .001}}

def M(*p): return merge(BASE, FOLD, OFF, *p)

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; b, c = math.sin(t), math.cos(t)
        idle.append(M(wings(5*b, 3*c, 2*b, 3*c, 0, 0), {"chest": {"x": 2*b}, "head": {"x": -2*b, "z": 3*c},
                                                       "upper_arm.R": {"x": -3*b}, "hand.R": {"x": 4*c}}))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 24*s
        walk.append(M(wings(3*c, 4*s, 2, 0, 0, 0), {"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                       "shin.L": {"bend": 6 + 42*max(0, c)**1.3}, "shin.R": {"bend": 6 + 42*max(0, -c)**1.3},
                       "foot.L": {"x": .3*th - 10*max(0, c)}, "foot.R": {"x": -.3*th - 10*max(0, -c)},
                       "hips": {"z": 6*s}, "chest": {"z": -7*s}, "head": {"z": 4*s}, "upper_arm.R": {"x": -8*s},
                       "upper_arm.L": {"x": 10*s}}))
    # corte diagonal com o montante, as asas se abrem no golpe
    up = M(wings(14, 4, 2, 10, 10, 6), {"upper_arm.R": {"x": -150, "y": 25}, "forearm.R": {"bend": -60}, "hand.R": {"x": -20},
                                       "upper_arm.L": {"x": -120, "y": 10, "z": -30}, "forearm.L": {"bend": -70},
                                       "chest": {"z": -24, "x": -8}, "spine": {"z": -8}, "head": {"z": 10},
                                       "thigh.L": {"x": -12}, "thigh.R": {"x": 10}})
    cut = M(wings(30, 8, 4, -12, 0, 0), {"upper_arm.R": {"x": -40, "y": 8, "z": 30}, "forearm.R": {"bend": -6}, "hand.R": {"x": 10},
                                         "upper_arm.L": {"x": -50, "y": -10, "z": 40}, "forearm.L": {"bend": -30},
                                         "chest": {"z": 30, "x": 16}, "spine": {"x": 8, "z": 8}, "head": {"z": -10, "x": -6},
                                         "thigh.L": {"x": -32}, "shin.L": {"bend": 22}, "thigh.R": {"x": 18}, "root": (0, -.2, 0)})
    attack = keys_to_frames([(0, M()), (.3, up), (.5, cut), (.7, merge(cut, {"upper_arm.R": {"x": 12}})), (1, M())], 10)
    # carga (loop): montante erguido com as duas mãos acima da cabeça, asas abertas no alto, a aura pulsando
    HOLD = {"upper_arm.R": {"x": -172, "y": 8}, "forearm.R": {"bend": -14}, "hand.R": {"x": -8},
            "upper_arm.L": {"x": -168, "y": -14, "z": -10}, "forearm.L": {"bend": -22}, "hand.L": {"x": -10},
            "spine": {"x": -6}, "chest": {"x": -10}, "head": {"x": -16},
            "thigh.L": {"x": -18, "y": -10}, "thigh.R": {"x": 12, "y": 10}, "shin.L": {"bend": 18}, "shin.R": {"bend": 14}}
    charge = []
    for i in range(8):
        t = i/8*2*math.pi; b = math.sin(t); v = math.sin(3*t)
        charge.append(merge(BASE, wings(62 + 6*b, 18 + 3*b, 10, -26, -18, -12), HOLD,
                            {"chest": {"x": 1.5*v, "z": 1.5*math.cos(3*t)}, "head": {"x": 2*v}, "root": (0, 0, .015*b),
                             "scale": {"aura": .85 + .2*(.5 + .5*b)}, "aim": {"sword": (0, .05, 1)}}))
    # golpe (o jogo dispara depois dos 4 s): desce o montante de uma vez no chão à frente, a aura estoura e some
    pre = merge(charge[0], {"spine": {"x": -6}, "chest": {"x": -8}, "scale": {"aura": 1.15}})
    slam = merge(BASE, wings(20, 6, 2, -40, -24, -14), {"upper_arm.R": {"x": -55, "y": -8}, "forearm.R": {"bend": -8}, "hand.R": {"x": 30},
                 "upper_arm.L": {"x": -60, "y": 12, "z": 14}, "forearm.L": {"bend": -12}, "hand.L": {"x": 25},
                 "spine": {"x": 12}, "chest": {"x": 14}, "head": {"x": 4},
                 "thigh.L": {"x": -38}, "shin.L": {"bend": 40}, "thigh.R": {"x": 20}, "shin.R": {"bend": 16}, "foot.R": {"x": -10},
                 "root": (0, -.28, 0), "scale": {"aura": 1.8}, "aim": {"sword": (0, -1, -.45)}})
    burst = merge(slam, {"scale": {"aura": 2.4}, "chest": {"x": 2}})
    after = merge(slam, {"scale": {"aura": .001}, "chest": {"x": -4}, "head": {"x": -6}})
    release = [pre, lerp_pose(pre, slam, .55), slam, burst, after, after, lerp_pose(after, M(), .35), lerp_pose(after, M(), .7), M(), M()]
    for p in release[2:5]: p["scale"] = dict(p.get("scale", {}))
    hitp = M(wings(30, 14, 10, 10, 6, 4), {"chest": {"x": -16, "z": 8}, "spine": {"x": -6}, "head": {"x": -16, "z": 12},
                                          "upper_arm.L": {"y": -10, "x": 18}, "upper_arm.R": {"y": 16, "x": 14}, "root": (0, .08, 0)})
    hit = [lerp_pose(M(), hitp, .6), hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: as asas se abrem num espasmo, cai de joelhos e tomba de lado sobre uma asa
    kneel = M(wings(10, -10, -6, 30, 20, 14), {"thigh.L": {"x": -80}, "thigh.R": {"x": -70}, "shin.L": {"bend": 105}, "shin.R": {"bend": 110},
                                              "chest": {"x": 18}, "head": {"x": 26}, "upper_arm.R": {"x": 10, "y": -10}, "forearm.R": {"bend": -10},
                                              "upper_arm.L": {"x": 10, "y": 10}})
    spasm = M(wings(70, 20, 10, -20, -10, -6), {"chest": {"x": -24}, "head": {"x": -30}, "upper_arm.L": {"x": -60, "y": -40},
                                               "upper_arm.R": {"x": -60, "y": 40}, "root": (0, .05, 0)})
    fall = merge(kneel, {"hips": {"x": 30, "y": 30}, "spine": {"x": 10}, "ground": .1})
    down = {"hips": {"x": 8, "y": 84}, "spine": {"x": 6}, "chest": {"x": 4}, "head": {"z": -20, "x": 14},
            "upper_arm.L": {"x": -40, "y": 30}, "upper_arm.R": {"x": -80, "y": -40}, "forearm.L": {"bend": -30}, "forearm.R": {"bend": -10},
            "thigh.L": {"x": -40}, "thigh.R": {"x": -20}, "shin.L": {"bend": 70}, "shin.R": {"bend": 40}, "ground": .05,
            "gb": ["hips", "spine", "chest", "head", "thigh.L", "thigh.R", "shin.L", "shin.R"], "scale": {"aura": .001}}
    down = merge(down, wings(-6, -4, -2, 50, 20, 10))
    death = keys_to_frames([(0, hitp), (.15, spasm), (.32, merge(spasm, {"head": {"x": -6}})), (.5, kneel), (.68, fall), (.86, down), (1, down)], 14)
    return {"idle": idle, "walk": walk, "attack": attack, "charge": charge, "release": release, "hit": hit, "death": death}
