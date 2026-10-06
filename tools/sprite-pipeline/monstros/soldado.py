# Soldado Caído: guerreiro humano morto na Grande Batalha, levantado pela ordem do General Partido.
# Pele seca e cinzenta, gibão acolchoado podre, peitoral enferrujado rachado pelo golpe que o matou,
# tabardo rasgado com a faixa da resistência, chapéu de ferro amassado, flechas nas costas, espada
# enferrujada de ponta quebrada. Brilho: olhos em brasa (a mesma brasa do Andras, que o comanda).
# Variante soldado_escudeiro: escudo redondo rachado no braço esquerdo, elmo fechado em vez do chapéu.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from mrig import *

INFO = {"px": 208, "target_z": .9, "rim": (1, .45, .18), "colors": 44, "samples": 40,
        "fps": {"idle": 5, "walk": 8, "attack": 12, "hit": 12, "death": 10, "rise": 10}}

VARIANTS = {
    "soldado_caido": {},
    "soldado_escudeiro": {"shield": True, "scale": 1.06},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
    if "rim" in V: INFO["rim"] = V["rim"]
set_variant("soldado_caido")

def build():
    skin = stained("s_pele", (.24, .22, .19), stain=(.16, .03, .015), amount=.35, scale=4, rough=.5,
                   blotch=(.12, .1, .09), blotch_amt=.8, grime=1.4)
    gamb = stained("s_gibao", (.24, .2, .14), stain=(.2, .03, .012), amount=.55, scale=3, rough=.95,
                   blotch=(.09, .08, .06), blotch_amt=.7, grime=1.5)
    tab = stained("s_tabardo", (.15, .065, .05), stain=(.06, .04, .03), amount=.6, scale=2.5, rough=.95,
                  blotch=(.12, .1, .08), blotch_amt=.7, grime=1.6)
    stripe = stained("s_faixa", (.42, .36, .22), stain=(.1, .07, .04), amount=.6, scale=3, rough=.95, grime=1.2)
    pants = stained("s_calca", (.07, .065, .06), stain=(.08, .04, .02), amount=.4, scale=3, rough=.9)
    boot = stained("s_bota", (.06, .04, .028), stain=(.1, .03, .015), amount=.4, scale=4, rough=.6, grime=.8)
    rust = stained("s_ferrugem", (.16, .1, .07), stain=(.3, .1, .03), amount=.7, scale=5, metal=.8, rough=.6,
                   blotch=(.08, .07, .065), blotch_amt=.5, grime=.6)
    steel = stained("s_aco", (.3, .29, .27), stain=(.3, .11, .03), amount=.6, scale=6, metal=1, rough=.45, grime=.4)
    wood = stained("s_madeira", (.13, .08, .045), stain=(.08, .05, .03), amount=.4, scale=4, rough=.85, grime=.5)
    leather = stained("s_couro", (.1, .06, .035), stain=(.15, .02, .01), amount=.4, scale=3, rough=.6, grime=.6)
    rot = mat("s_podre", (.12, .02, .015), 0, .3, dirt=.6)
    hole = mat("s_buraco", (.008, .005, .004), 0, .95)
    tooth = mat("s_dente", (.38, .34, .24), 0, .5, dirt=.6, grime=.2)
    feather = mat("s_pena", (.05, .045, .04), 0, .9, dirt=.4)
    eye = mat("s_olho", (1, .6, .3), emit=(1, .42, .14), strength=20)

    B = humanoid(1.0, 1.0)
    R = Rig(V["name"], B); P = R.P
    # ------------------------------------------------ corpo seco
    j = {"pelvis": (0, 0, .95, .13, .1)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .08); j[f"knee{n}"] = (*k, .062); j[f"ank{n}"] = (*a, .045)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"knee{n}"), (f"knee{n}", f"ank{n}")]
    legs = skin_mesh("pernas", j, e, pants); R.bind(legs, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R"])
    for s, n in ((1, "L"), (-1, "R")):  # botas de couro gastas
        k, a, t = P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        bj = {"top": (*k.lerp(a, .5), .065), "ank": (*a, .06), "heel": (*(a + Vector((0, .04, -.05))), .045),
              "toe": (*(t + Vector((0, -.015, 0))), .05, .038)}
        o = skin_mesh(f"bota.{n}", bj, [("top", "ank"), ("ank", "heel"), ("ank", "toe")], boot)
        R.bind(o, [f"shin.{n}", f"foot.{n}"])
    t = {"pelvis": (0, 0, .98, .14, .1), "waist": (0, 0, 1.13, .12, .09), "chest": (0, 0, 1.33, .17, .11),
         "neck": (0, -.01, 1.5, .045), "neck2": (0, -.02, 1.58, .04)}
    te = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, 0))), .065); t[f"el{n}"] = (*el, .045)
        t[f"fa{n}"] = (*el.lerp(wr, .4), .045); t[f"wr{n}"] = (*wr, .034)
        te += [("chest", f"sh{n}"), (f"sh{n}", f"el{n}"), (f"el{n}", f"fa{n}"), (f"fa{n}", f"wr{n}")]
    torso = skin_mesh("tronco", t, te, skin)
    R.bind(torso, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])

    # ------------------------------------------------ gibão acolchoado até a coxa, mangas
    gb = skirt("gibao", gamb, [(1.5, .1, .085, 0), (1.42, .19, .13, 0), (1.25, .19, .13, .005), (1.05, .16, .12, .01),
                               (.9, .17, .13, .015), (.68, .2, .15, .02)], jag=.05, seed=12, thick=.014)
    R.bind(gb, ["hips", "spine", "chest", "thigh.L", "thigh.R"], power=3)
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        sj = {"a": (*(sh + Vector((-.02*s, 0, 0))), .08), "b": (*el, .062), "c": (*el.lerp(wr, .55 if n == "R" else .3), .058)}
        o = skin_mesh(f"manga.{n}", sj, [("a", "b"), ("b", "c")], gamb, levels=1)
        R.bind(o, ["chest", f"upper_arm.{n}", f"forearm.{n}"])
    # tabardo rasgado (frente e costas), com a faixa clara da resistência
    tf = apron("tabardo_f", tab, 1.44, .58, .13, .15, -.155, .05, jag=.08, seed=4)
    tb = apron("tabardo_c", tab, 1.44, .62, .13, .15, .145, -.05, jag=.09, seed=7)
    R.bind(tf, ["hips", "spine", "chest", "thigh.L", "thigh.R"], power=3)
    R.bind(tb, ["hips", "spine", "chest", "thigh.L", "thigh.R"], power=3)
    ch = []
    # peitoral de ferro enferrujado, rachado do ombro ao ventre
    bp = prim("primitive_uv_sphere_add", rust, (0, -.03, 1.3), (.17, .125, .17), segments=18, ring_count=10)
    ch.append(bp)
    crack = [Vector((.09, -.152, 1.43)), Vector((.05, -.162, 1.36)), Vector((.065, -.165, 1.3)), Vector((.01, -.163, 1.22)),
             Vector((.03, -.155, 1.15))]
    for a, b in zip(crack, crack[1:]):
        ch.append(along("primitive_cylinder_add", hole, a, b, .012, vertices=5))
    ch.append(prim("primitive_uv_sphere_add", rot, (.05, -.16, 1.33), (.03, .015, .04), segments=8, ring_count=6))
    for z in (1.18, 1.12):  # placas da barriga
        ch.append(prim("primitive_cylinder_add", rust, (0, -.01, z), (.15, .12, .025), vertices=16))
    for s in (1, -1):  # rebites
        for z in (1.4, 1.3, 1.2):
            ch.append(prim("primitive_uv_sphere_add", steel, (.13*s, -.115 + .02*abs(1.3 - z), z), (.009, .008, .009), segments=6, ring_count=4))
    # faixa clara pintada no tabardo (sinal da resistência: barra vertical cruzada)
    ch.append(prim("primitive_cube_add", stripe, (0, -.17, .95), (.03, .006, .17), rot=(-6, 0, 0)))
    ch.append(prim("primitive_cube_add", stripe, (0, -.168, 1.0), (.085, .006, .022), rot=(-6, 0, 0)))
    # cinto com bainha vazia e bolsa
    ch.append(prim("primitive_torus_add", leather, (0, 0, 1.02), (1.05, .82, 1), major_radius=.15, minor_radius=.016,
                   major_segments=20, minor_segments=4))
    ch.append(prim("primitive_cube_add", steel, (0, -.125, 1.02), (.025, .008, .022)))
    ch.append(along("primitive_cylinder_add", leather, (.15, -.03, 1.0), (.2, .12, .45), .025, vertices=6))
    ch.append(prim("primitive_cube_add", leather, (-.14, -.07, .97), (.04, .03, .05), rot=(0, 0, 30)))
    # ombreira de ferro no ombro esquerdo (a direita se perdeu), com tira de couro
    pc = P("upper_arm.L") + Vector((.03, 0, .05))
    for k in range(3):
        ch.append(prim("primitive_uv_sphere_add", rust, pc + Vector((.015*k, 0, -.04*k)), (.11 - .01*k, .1, .06),
                       segments=14, ring_count=8, rot=(0, -25 - 8*k, 0)))
    ch.append(along("primitive_cylinder_add", leather, pc + Vector((-.05, -.1, -.02)), pc + Vector((-.17, -.12, -.12)), .012, vertices=5))
    # flechas cravadas nas costas
    for p0, d in (((.06, .11, 1.36), (.1, .5, .25)), ((-.08, .12, 1.22), (-.15, .5, .12)), ((.02, .1, 1.08), (.05, .5, -.05))):
        p0 = Vector(p0); d = Vector(d).normalized(); p1 = p0 + d*.42
        ch.append(along("primitive_cylinder_add", wood, p0 - d*.04, p1, .006, vertices=4))
        for k in range(3):
            q = p1 - d*(.03 + .02*k); side = d.cross(Vector((0, 0, 1))).normalized()
            ch.append(along("primitive_cone_add", feather, q, q - d*.07 + side*.025*(1 if k % 2 else -1), .02,
                            vertices=3, radius1=1, radius2=.1))
    R.rigid(ch, "chest")

    # ------------------------------------------------ canelas e braçadeiras
    for n in "LR":
        k, a = P(f"shin.{n}"), P(f"foot.{n}")
        g = [along("primitive_cylinder_add", rust, k.lerp(a, .05), k.lerp(a, .55), .07, vertices=10)]
        g.append(prim("primitive_uv_sphere_add", rust, k + Vector((0, -.03, 0)), (.06, .05, .06), segments=10, ring_count=6))
        g.append(along("primitive_cylinder_add", leather, k.lerp(a, .3) + Vector((0, 0, 0)), k.lerp(a, .32), .075, vertices=10))
        R.rigid(g, f"shin.{n}")
    el, wr = P("forearm.R"), P("hand.R")
    R.rigid([along("primitive_cylinder_add", rust, el.lerp(wr, .4), el.lerp(wr, .95), .052, vertices=10)], "forearm.R")

    # ------------------------------------------------ cabeça: rosto seco, mandíbula caída, olhos de brasa
    hp = [prim("primitive_uv_sphere_add", skin, (0, -.01, 1.69), (.085, .098, .105), segments=16, ring_count=10)]
    hp.append(prim("primitive_uv_sphere_add", skin, (0, -.045, 1.63), (.058, .058, .048), segments=12, ring_count=8))
    hp.append(prim("primitive_uv_sphere_add", skin, (0, -.07, 1.57), (.048, .05, .022), segments=12, ring_count=6, rot=(30, 0, 0)))
    hp.append(prim("primitive_uv_sphere_add", hole, (0, -.092, 1.605), (.033, .02, .028), segments=10, ring_count=6))
    for k in range(5):
        x = -.024 + .012*k
        hp.append(along("primitive_cone_add", tooth, (x, -.095, 1.63), (x, -.098, 1.607), .006, vertices=4, radius1=1, radius2=0))
    for s in (1, -1):
        hp.append(prim("primitive_uv_sphere_add", hole, (.03*s, -.072, 1.7), (.024, .014, .018), segments=8, ring_count=6))
        hp.append(prim("primitive_uv_sphere_add", eye, (.03*s, -.083, 1.7), (.011, .006, .01), segments=8, ring_count=6))
    if not V.get("shield"):
        # chapéu de ferro (kettle hat) amassado, aba larga, furo de lança
        hp.append(prim("primitive_uv_sphere_add", rust, (0, -.005, 1.75), (.11, .115, .09), segments=16, ring_count=8))
        brim = prim("primitive_cylinder_add", rust, (0, -.005, 1.73), (.19, .19, .012), vertices=20, rot=(-8, 4, 0))
        hp.append(brim)
        hp.append(prim("primitive_torus_add", steel, (0, -.005, 1.73), (1, 1, 1), major_radius=.19, minor_radius=.01,
                       major_segments=20, minor_segments=4, rot=(-8, 4, 0)))
        hp.append(prim("primitive_uv_sphere_add", hole, (.06, -.08, 1.79), (.02, .015, .02), segments=8, ring_count=6))
        hp.append(prim("primitive_cube_add", rust, (0, .0, 1.84), (.012, .1, .01)))  # crista
        hp.append(along("primitive_cylinder_add", leather, (.08, -.06, 1.7), (.05, -.08, 1.56), .007, vertices=4))  # jugular
    else:
        # elmo fechado com fresta, amassado de um lado
        hp.append(prim("primitive_uv_sphere_add", rust, (0, -.01, 1.71), (.115, .125, .135), segments=16, ring_count=10))
        hp.append(prim("primitive_cube_add", hole, (0, -.13, 1.71), (.075, .012, .011)))
        hp.append(prim("primitive_uv_sphere_add", eye, (.03, -.128, 1.71), (.012, .006, .007), segments=8, ring_count=6))
        hp.append(prim("primitive_uv_sphere_add", eye, (-.03, -.128, 1.71), (.012, .006, .007), segments=8, ring_count=6))
        for k in range(4):
            hp.append(prim("primitive_uv_sphere_add", hole, (-.03 + .02*k, -.128, 1.64), (.005, .005, .005), segments=6, ring_count=4))
        hp.append(prim("primitive_cube_add", rust, (0, -.02, 1.84), (.012, .11, .02)))
        hp.append(prim("primitive_uv_sphere_add", hole, (-.09, -.06, 1.76), (.03, .03, .025), segments=8, ring_count=6))
        hp.append(prim("primitive_cylinder_add", rust, (0, 0, 1.58), (.1, .1, .03), vertices=14))
    R.rigid(hp, "head")

    # ------------------------------------------------ mãos, espada e escudo
    for s, n in ((1, "L"), (-1, "R")):
        o, ax, u, sd = R.frame(f"hand.{n}")
        g = prim("primitive_uv_sphere_add", skin, o + ax*.04, (.032, .036, .046), segments=10, ring_count=6)
        g.rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        parts = [g]
        for f in range(4):  # dedos secos
            base = o + ax*.07 + sd*(-.022 + .015*f)
            parts.append(along("primitive_cylinder_add", skin, base, base + ax*.045 + u*.02, .008, vertices=5))
        if n == "R":  # espada enferrujada de ponta quebrada
            hc = o + ax*.05
            parts.append(along("primitive_cylinder_add", leather, hc - u*.07, hc + u*.08, .018, vertices=8))
            parts.append(prim("primitive_uv_sphere_add", steel, hc - u*.09, (.026, .026, .026), segments=8, ring_count=6))
            parts.append(along("primitive_cylinder_add", steel, hc + u*.09 - sd*.11, hc + u*.09 + sd*.11, .014, vertices=6))
            for s2 in (1, -1):
                parts.append(along("primitive_cone_add", steel, hc + u*.09 + sd*.11*s2, hc + u*.07 + sd*.14*s2, .016,
                                   vertices=5, radius1=1, radius2=.4))
            bl = prim("primitive_cube_add", steel, hc + u*.46, (1, 1, 1))
            rot_ = Matrix((ax, sd, u)).transposed()  # x=ax (espessura), y=sd (largura), z=u (comprimento)
            bl.rotation_euler = rot_.to_euler(); bl.scale = (.008, .045, .36); parts.append(bl)
            # ponta quebrada em diagonal + mossas na lâmina
            parts.append(along("primitive_cone_add", steel, hc + u*.82 - sd*.01, hc + u*.9 + sd*.03, .044,
                               vertices=4, radius1=1, radius2=.2))
            for k, tt in enumerate((.3, .52, .7)):
                parts.append(prim("primitive_uv_sphere_add", hole, hc + u*(.1 + .72*tt) + sd*(.03*(1 if k % 2 else -1)),
                                  (.012, .012, .012), segments=6, ring_count=4))
            parts.append(along("primitive_cylinder_add", rust, hc + u*.15, hc + u*.6, .012, vertices=4))
        if n == "L" and V.get("shield"):  # escudo redondo de madeira, rachado, aro de ferro
            c = o - ax*.06 + u*.0 - sd*.08
            nrm = sd
            sh_ = prim("primitive_cylinder_add", wood, c, (.3, .3, .025), vertices=24)
            sh_.rotation_euler = nrm.to_track_quat('Z', 'Y').to_euler(); parts.append(sh_)
            rim = prim("primitive_torus_add", rust, c, (1, 1, 1), major_radius=.3, minor_radius=.018, major_segments=24, minor_segments=5)
            rim.rotation_euler = sh_.rotation_euler; parts.append(rim)
            boss = prim("primitive_uv_sphere_add", rust, c - nrm*.03, (.075, .075, .075), segments=12, ring_count=6)
            parts.append(boss)
            q = nrm.to_track_quat('Z', 'Y')
            for k in range(6):  # tábuas e cravos do aro
                a = 2*math.pi*k/6
                parts.append(prim("primitive_uv_sphere_add", steel, c + q @ Vector((.27*math.cos(a), .27*math.sin(a), .02)) - nrm*.02,
                                  (.012, .012, .012), segments=6, ring_count=4))
            for x in (-.1, .1):
                parts.append(along("primitive_cylinder_add", hole, c + q @ Vector((x, -.28, 0)) - nrm*.027,
                                   c + q @ Vector((x, .28, 0)) - nrm*.027, .004, vertices=4))
            # rachadura e pedaço faltando
            parts.append(along("primitive_cylinder_add", hole, c + q @ Vector((.05, .28, 0)) - nrm*.028,
                               c + q @ Vector((-.02, .05, 0)) - nrm*.028, .01, vertices=4))
            parts.append(prim("primitive_uv_sphere_add", rot, c + q @ Vector((-.16, -.12, 0)) - nrm*.028, (.04, .04, .01),
                              segments=8, ring_count=4))
            parts[-1].rotation_euler = sh_.rotation_euler
        R.rigid(parts, f"hand.{n}")
    R.arm.scale = [1.04*V.get("scale", 1)]*3
    return R, INFO

def apron(name, m, z0, z1, w0, w1, y, curve, rows=7, cols=7, jag=0, seed=1):
    """Pano pendurado na frente (y<0) ou atrás (y>0) do corpo."""
    rnd = random.Random(seed); bm = bmesh.new(); g = []
    for r in range(rows):
        tt = r/(rows-1); z = z0 + (z1 - z0)*tt; w = w0 + (w1 - w0)*tt; row = []
        for c in range(cols):
            u = c/(cols-1)*2 - 1
            zz = z + (rnd.uniform(-jag, jag*.3) if r == rows-1 else 0)
            row.append(bm.verts.new((u*w, y + curve*u*u + (.04*tt if y < 0 else -.0)*-1, zz)))
        g.append(row)
    for r in range(rows-1):
        for c in range(cols-1):
            bm.faces.new((g[r][c], g[r][c+1], g[r+1][c+1], g[r+1][c]))
    o = obj_from_bm(name, bm, m); o.modifiers.new("s", 'SOLIDIFY').thickness = .01; apply_mods(o)
    return o

# ======================================================================= animações
# postura de morto-vivo disciplinado: ainda em guarda, cabeça um pouco tombada, espada baixa
BASE = {"spine": {"x": 8}, "chest": {"x": 6}, "neck": {"x": -4}, "head": {"x": -6, "z": 10, "y": 8},
        "thigh.L": {"x": -10, "y": -5}, "thigh.R": {"x": 6, "y": 5}, "shin.L": {"bend": 14}, "shin.R": {"bend": 10},
        "foot.L": {"x": -6}, "foot.R": {"x": -6},
        "upper_arm.L": {"y": 22, "x": -18}, "upper_arm.R": {"y": -16, "x": -22},
        "forearm.L": {"bend": -40}, "forearm.R": {"bend": -25}, "hand.R": {"x": 75}}

def M(*p):
    b = {k: dict(v) for k, v in BASE.items()}
    if V.get("shield"):  # escudo na frente do corpo
        b["upper_arm.L"] = {"y": 20, "x": -40, "z": 20}; b["forearm.L"] = {"bend": -80}
    return merge(b, *p)

def anims(R):
    idle = []
    for i in range(4):
        b = math.sin(i/4*2*math.pi); c = math.cos(i/4*2*math.pi)
        idle.append(M({"chest": {"x": 2*b, "z": 2*c}, "head": {"z": 5*c, "x": -3*b}, "upper_arm.R": {"x": -3*b},
                       "hand.R": {"x": 4*c}}))
    # andar duro: a perna direita (ferida) mal dobra e arrasta, o corpo pende para ela
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 22*s
        walk.append(M({"thigh.L": {"x": -th}, "thigh.R": {"x": .8*th},
                       "shin.L": {"bend": 8 + 48*max(0, c)**1.3}, "shin.R": {"bend": 6 + 12*max(0, -c)},
                       "foot.L": {"x": .3*th - 12*max(0, c)}, "foot.R": {"x": -.2*th},
                       "hips": {"z": 6*s, "y": 3*c - 3}, "chest": {"z": -8*s, "y": -4*c + 3}, "head": {"z": 8*s + 8, "y": 5*c + 8},
                       "upper_arm.L": {"x": 12*s}, "upper_arm.R": {"x": -6*s}}))
    # golpe: ergue a espada sobre o ombro (preparo longo, tremendo) e desce na diagonal
    up = M({"upper_arm.R": {"x": -150, "y": 30}, "forearm.R": {"bend": -70}, "hand.R": {"x": -35},
            "chest": {"z": -24, "x": -10}, "spine": {"z": -8, "x": -4}, "head": {"z": 12, "x": 6},
            "thigh.R": {"x": 12}, "thigh.L": {"x": -14}, "root": (0, .04, 0)})
    up2 = merge(up, {"upper_arm.R": {"x": -6}, "chest": {"z": -4}, "head": {"z": -6}})
    strike = M({"upper_arm.R": {"x": -40, "y": 6, "z": 28}, "forearm.R": {"bend": -6}, "hand.R": {"x": -25},
                "chest": {"z": 28, "x": 22}, "spine": {"x": 10, "z": 8}, "head": {"x": -16, "z": -8},
                "thigh.L": {"x": -36}, "shin.L": {"bend": 26}, "thigh.R": {"x": 20}, "shin.R": {"bend": 6},
                "foot.R": {"x": -10}, "root": (0, -.18, 0)})
    follow = merge(strike, {"upper_arm.R": {"x": 14, "z": 8}, "chest": {"x": 6, "z": 6}, "root": (0, -.02, 0)})
    attack = keys_to_frames([(0, M()), (.22, up), (.42, up2), (.56, strike), (.72, follow), (1, M())], 10)
    hitp = M({"chest": {"x": -18, "z": -10}, "spine": {"x": -8}, "head": {"x": -24, "z": 16},
              "upper_arm.L": {"y": -10, "x": 20}, "upper_arm.R": {"y": 20, "x": 15}, "forearm.R": {"bend": -20},
              "root": (0, .07, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: perde a ordem e desaba de cara no chão, espada solta ao lado (vira cadáver fresco)
    kneel = M({"thigh.L": {"x": -70}, "thigh.R": {"x": -55}, "shin.L": {"bend": 100}, "shin.R": {"bend": 110},
               "foot.L": {"x": -10}, "foot.R": {"x": -10}, "chest": {"x": 18}, "head": {"x": 25, "z": 20},
               "upper_arm.L": {"y": 8, "x": 10}, "upper_arm.R": {"y": -8, "x": 0}, "forearm.R": {"bend": -10}})
    fall = merge(kneel, {"hips": {"x": 40}, "spine": {"x": 15}, "upper_arm.L": {"x": -50}, "upper_arm.R": {"x": -40},
                         "ground": .1})
    prone = {"hips": {"x": 86, "z": 10}, "spine": {"x": 2}, "chest": {"x": -4}, "head": {"z": 60, "x": -10},
             "upper_arm.L": {"x": -150, "y": 50}, "upper_arm.R": {"x": -110, "y": -60},
             "forearm.L": {"bend": -30}, "forearm.R": {"bend": -20}, "hand.R": {"x": 40},
             "thigh.L": {"x": 4, "y": -8}, "thigh.R": {"x": -6, "y": 12}, "shin.L": {"bend": 25}, "shin.R": {"bend": 8},
             "foot.L": {"x": 40}, "foot.R": {"x": 30}, "ground": .07}
    death = keys_to_frames([(0, hitp), (.3, kneel), (.6, fall), (.85, prone), (1, merge(prone, {"head": {"x": 4}}))], 8)
    # levantar: deitado de bruços, os olhos acendem, empurra o chão com as mãos, fica de joelhos e se ergue
    push = {"hips": {"x": 70, "z": 4}, "spine": {"x": 10}, "chest": {"x": 6}, "neck": {"x": -20}, "head": {"x": -30},
            "upper_arm.L": {"x": -40, "y": 20}, "upper_arm.R": {"x": -40, "y": -20},
            "forearm.L": {"bend": -20}, "forearm.R": {"bend": -20}, "hand.R": {"x": 40},
            "thigh.L": {"x": -20}, "thigh.R": {"x": -10}, "shin.L": {"bend": 60}, "shin.R": {"bend": 40},
            "foot.L": {"x": 30}, "foot.R": {"x": 30}, "ground": .07}
    knees = merge(kneel, {"chest": {"x": 10}, "head": {"x": -10, "z": -10}, "upper_arm.R": {"x": -10}})
    rise = keys_to_frames([(0, prone), (.12, merge(prone, {"head": {"x": -14}})), (.35, push), (.6, knees),
                           (.8, lerp_pose(knees, M(), .6)), (1, M())], 10)
    return {"idle": idle, "walk": walk, "attack": attack, "hit": hit, "death": death, "rise": rise}
