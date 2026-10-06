# Chefe do andar 1: Andras, o General Partido (Legião Rubra do Inferno). Só o tronco sobreviveu;
# anda apoiado nos braços enormes, arrastando a espinha e as tripas. Armadura de
# general em ruína (ombreiras com cravos, peitoral rachado, coroa-elmo com chifres),
# a espada que o partiu ainda cravada nas costas com o estandarte rasgado.
# Brilho: brasa (rachaduras no peito, olhos e boca).
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *

INFO = {"loops": ("idle", "walk", "eat", "tired"), "px": 400, "target_z": 1.3, "rim": (1, .42, .16), "rim_e": 7.0, "colors": 48, "samples": 28,
        "fps": {"idle": 6, "walk": 8, "attack": 12, "sweep": 14, "lunge": 12, "eat": 8, "roar": 10, "vomit": 10,
                "feast": 12, "tired": 5, "hit": 12, "death": 9}}

BONES = {
 "hips":  ((0, .18, .78), (0, .1, 1.08), None),
 "spine": ((0, .1, 1.08), (0, .05, 1.42), "hips"),
 "chest": ((0, .05, 1.42), (0, 0, 1.86), "spine"),
 "neck":  ((0, 0, 1.86), (0, -.1, 2.0), "chest"),
 "head":  ((0, -.1, 2.0), (0, -.14, 2.34), "neck"),
 "jaw":   ((0, -.1, 2.06), (0, -.3, 2.0), "head"),
 "tail1": ((0, .22, .76), (0, .55, .4), "hips"),
 "tail2": ((0, .55, .4), (0, .98, .14), "tail1"),
 "tail3": ((0, .98, .14), (0, 1.45, .06), "tail2"),
}
for s, n in ((1, "L"), (-1, "R")):
    BONES.update({
     f"upper_arm.{n}": ((.44*s, .02, 1.78), (.74*s, -.12, 1.06), "chest"),
     f"forearm.{n}":   ((.74*s, -.12, 1.06), (.82*s, -.3, .2), f"upper_arm.{n}"),
     f"hand.{n}":      ((.82*s, -.3, .2), (.86*s, -.5, .05), f"forearm.{n}"),
    })
_g = Vector((-.85, -.42, .12)); _d = Vector((-.12, -.3, .95)).normalized()
BONES["banner"] = (tuple(_g), tuple(_g + _d*2.2), "hand.R")

def build():
    flesh = stained("g_carne", (.12, .05, .042), stain=(.03, .022, .02), amount=.45, scale=3, rough=.45,
                    blotch=(.05, .035, .035), blotch_amt=.7, grime=.9)
    gut = stained("g_tripa", (.3, .06, .05), stain=(.12, .01, .01), amount=.4, scale=8, rough=.22, grime=.3)
    iron = stained("g_ferro", (.07, .065, .06), stain=(.16, .06, .025), amount=.45, scale=5, metal=.85, rough=.5, grime=.6)
    gold = stained("g_ouro", (.42, .28, .07), stain=(.06, .04, .02), amount=.4, scale=6, metal=1, rough=.4, grime=.4)
    horn = stained("g_chifre", (.12, .1, .085), stain=(.02, .015, .01), amount=.3, scale=4, rough=.55, grime=.2)
    bone = stained("g_osso", (.42, .38, .3), stain=(.15, .03, .02), amount=.35, scale=5, rough=.6, grime=.6)
    flag = stained("g_estandarte", (.2, .025, .02), stain=(.04, .03, .025), amount=.5, scale=3, rough=.9, grime=.4)
    leather = stained("g_couro", (.03, .025, .025), stain=(.1, .02, .01), amount=.3, scale=4, rough=.6)
    ember = mat("g_brasa", (1, .5, .15), emit=(1, .36, .06), strength=5)
    dark = mat("g_boca", (.01, .002, .002), 0, .9)

    R = Rig("general", BONES, ground=.3, ground_bones=["hips"]); R.gexclude = {"banner"}
    P = R.P
    rnd = random.Random(13)

    # ------------------------------------------------ tronco e braços (carne)
    t = {"stump": (0, .2, .8, .3, .26), "waist": (0, .12, 1.05, .34, .27), "belly": (0, .06, 1.3, .4, .3),
         "chest": (0, .02, 1.6, .5, .36), "neck": (0, -.04, 1.9, .18), "neck2": (0, -.1, 2.0, .15)}
    te = [("stump", "waist"), ("waist", "belly"), ("belly", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"trap{n}"] = (.25*s, .03, 1.86, .16); t[f"sh{n}"] = (*sh, .22)
        t[f"bi{n}"] = (*(sh.lerp(el, .4) + Vector((0, -.05, 0))), .2, .23); t[f"el{n}"] = (*el, .12)
        t[f"fa{n}"] = (*(el.lerp(wr, .22) + Vector((.02*s, -.03, 0))), .2, .17); t[f"fa2{n}"] = (*el.lerp(wr, .6), .13)
        t[f"wr{n}"] = (*wr, .095)
        te += [("chest", f"trap{n}"), (f"trap{n}", f"sh{n}"), (f"sh{n}", f"bi{n}"), (f"bi{n}", f"el{n}"),
               (f"el{n}", f"fa{n}"), (f"fa{n}", f"fa2{n}"), (f"fa2{n}", f"wr{n}")]
    body = skin_mesh("tronco", t, te, flesh)
    R.bind(body, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])

    # ------------------------------------------------ mãos com garras
    for s, n in ((1, "L"), (-1, "R")):
        o, ax, u, sd = R.frame(f"hand.{n}", up=Vector((0, 0, 1)))
        hp = [prim("primitive_uv_sphere_add", flesh, o + ax*.07, (.14, .12, .1), segments=14, ring_count=8)]
        hp[0].rotation_euler = ax.to_track_quat('Y', 'Z').to_euler()
        for f in range(4):
            side = -.1 + .067*f
            base = o + ax*.13 + sd*side
            mid = base + ax*.12 + sd*side*.3
            tip = mid + ax*.1 - u*.09
            hp.append(along("primitive_cylinder_add", flesh, base, mid, .035, vertices=8))
            hp.append(along("primitive_cone_add", horn, mid, tip, .03, vertices=6, radius1=1, radius2=0))
        th = o + ax*.04 - sd*s*.13
        hp.append(along("primitive_cone_add", horn, th, th - sd*s*.08 + ax*.08 - u*.06, .03, vertices=6, radius1=1, radius2=0))
        # bracelete de ferro com cravos
        wr = P(f"forearm.{n}").lerp(P(f"hand.{n}"), .75)
        R.rigid(hp, f"hand.{n}")
        br = [prim("primitive_cylinder_add", iron, wr, (.15, .15, .1), vertices=12)]
        fdir = (P(f"hand.{n}") - P(f"forearm.{n}")).normalized()
        br[0].rotation_euler = fdir.to_track_quat('Z', 'Y').to_euler()
        for k in range(5):
            a = 2*math.pi*k/5; v = Vector((math.cos(a), math.sin(a), 0))
            v = fdir.to_track_quat('Z', 'Y') @ v
            br.append(along("primitive_cone_add", iron, wr + v*.13, wr + v*.24, .03, vertices=6, radius1=1, radius2=0))
        R.rigid(br, f"forearm.{n}")
        sh, el = P(f"upper_arm.{n}"), P(f"forearm.{n}"); udir = (el - sh).normalized()
        ra = []
        for k, tt in enumerate((.55, .68)):
            o = prim("primitive_torus_add", gold if k else iron, sh.lerp(el, tt) + Vector((0, -.03, 0)), (1, 1, 1.4),
                     major_radius=.2 - .02*k, minor_radius=.03, major_segments=16, minor_segments=5)
            o.rotation_euler = udir.to_track_quat('Z', 'Y').to_euler(); ra.append(o)
        ra.append(along("primitive_cone_add", iron, el + Vector((0, .06, .02)), el + Vector((.05*s, .25, .02)), .05,
                        vertices=6, radius1=1, radius2=0))  # cravo do cotovelo
        R.rigid(ra, f"upper_arm.{n}")

    # ------------------------------------------------ cabeça: coroa-elmo com chifres, mandíbula, olhos de brasa
    hd = []
    hd.append(prim("primitive_uv_sphere_add", flesh, (0, -.13, 2.17), (.15, .16, .16), segments=16, ring_count=10))
    hd.append(prim("primitive_uv_sphere_add", flesh, (0, -.25, 2.12), (.1, .08, .07), segments=12, ring_count=8))
    hd.append(prim("primitive_uv_sphere_add", dark, (0, -.3, 2.07), (.07, .03, .035), segments=10, ring_count=6))
    for s in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", dark, (.06*s, -.27, 2.2), (.04, .02, .025), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", ember, (.06*s, -.285, 2.2), (.022, .01, .014), segments=8, ring_count=6))
        # chifres grossos curvados para trás e para cima
        pts = [Vector((.11*s, -.1, 2.27))]; d = Vector((.5*s, .1, .6)).normalized(); r = .06
        for k in range(7):
            d = (Quaternion(Vector((0, 1, 0)), -.12*s) @ Quaternion(Vector((1, 0, 0)), .22) @ d).normalized()
            pts.append(pts[-1] + d*.11)
        for k in range(len(pts)-1):
            hd.append(along("primitive_cone_add", horn, pts[k], pts[k+1], r*(1 - k/7.5), vertices=8,
                            radius1=1, radius2=1 - 1/7.5))
        hd.append(prim("primitive_torus_add", gold, pts[2], (1, 1, 1), major_radius=.055, minor_radius=.014,
                       major_segments=12, minor_segments=4))
        hd[-1].rotation_euler = (pts[3]-pts[1]).to_track_quat('Z', 'Y').to_euler()
    # coroa de ferro quebrada (aro com pontas irregulares)
    for k in range(9):
        a = math.radians(-160 + 40*k)
        if k in (3, 6): continue
        c = Vector((.16*math.sin(a), -.13 - .17*math.cos(a), 2.26))
        hd.append(prim("primitive_cube_add", gold, c, (.035, .015, .03)))
        hd[-1].rotation_euler = (0, 0, -a)
        hd.append(along("primitive_cone_add", gold, c + Vector((0, 0, .02)), c + Vector((0, 0, .06 + .05*rnd.random())), .02,
                        vertices=4, radius1=1, radius2=0))
    piv = Vector((0, -.1, 2.0))
    for o in hd:
        o.location = piv + (o.location - piv)*1.3; o.scale = o.scale*1.3
    R.rigid(hd, "head")
    jw = [prim("primitive_uv_sphere_add", flesh, (0, -.22, 2.02), (.1, .1, .045), segments=12, ring_count=8)]
    for k in range(7):
        x = -.06 + .02*k
        jw.append(along("primitive_cone_add", bone, (x, -.29 + abs(x)*.6, 2.04), (x, -.29 + abs(x)*.6, 2.1),
                        .011, vertices=4, radius1=1, radius2=0))
    jw.append(prim("primitive_uv_sphere_add", ember, (0, -.26, 2.06), (.04, .03, .012), segments=8, ring_count=6))
    for o in jw:
        o.location = piv + (o.location - piv)*1.3; o.scale = o.scale*1.3
    R.rigid(jw, "jaw")

    # ------------------------------------------------ armadura de general em ruína
    ch = []
    # peitoral rachado (só a metade esquerda e um pedaço da direita)
    for s, frac in ((1, 1.0), (-1, .45)):
        for i in range(5):
            z = 1.36 + i*.1
            if s < 0 and i < 2: continue
            w = .28 - abs(i-2.5)*.02
            ch.append(prim("primitive_cube_add", iron, (s*w*.5, -.3 - .02*(2-i)*.2, z), (w*.5*frac, .04, .05)))
            ch[-1].rotation_euler = (math.radians(-8), 0, math.radians(-12*s))
    ch.append(prim("primitive_cube_add", gold, (.02, -.34, 1.62), (.3, .02, .015)))
    # gorjal
    ch.append(prim("primitive_torus_add", iron, (0, -.03, 1.88), (1.1, .9, 1.2), major_radius=.2, minor_radius=.05,
                   major_segments=18, minor_segments=6))
    # ombreiras grandes com cravos e debrum de ouro
    for s in (1, -1):
        c = Vector((.5*s, .0, 1.86))
        pad = prim("primitive_uv_sphere_add", iron, c, (.3, .26, .17), segments=16, ring_count=8)
        pad.rotation_euler = (0, math.radians(22*s), 0); ch.append(pad)
        ch.append(prim("primitive_torus_add", gold, c - Vector((0, 0, .05)), (1.3, 1.1, 1), major_radius=.22, minor_radius=.02,
                       major_segments=20, minor_segments=4, rot=(0, 22*s, 0)))
        for k in range(4):
            a = .15 + k*.32
            b = c + Vector((.18*s*math.cos(a)*.6, -.15 + .1*k, .13))
            ch.append(along("primitive_cone_add", iron, b, b + Vector((.12*s, .02*(k-1.5), .28 - .03*k)), .05,
                            vertices=6, radius1=1, radius2=0))
        for k in range(9):  # dragona de general: franja de ouro podre
            a = math.radians(-70 + 140*k/8)
            q = c + Vector((.27*s*math.cos(a)*.95, .22*math.sin(a), -.1))
            ch.append(along("primitive_cylinder_add", gold, q, q + Vector((.03*s, 0, -.13 - .04*(k % 3))), .012, vertices=4))
        # crânios de troféu pendurados por correntes
        sk = c + Vector((.2*s, -.12, -.45))
        for k in range(4):
            ch.append(prim("primitive_torus_add", iron, c + (sk - c)*(k+.5)/4.5, (1, 1, 1.5), major_radius=.025,
                           minor_radius=.008, major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
        ch.append(prim("primitive_uv_sphere_add", bone, sk, (.065, .075, .075), segments=10, ring_count=8))
        ch.append(prim("primitive_uv_sphere_add", dark, sk + Vector((0, -.065, -.005)), (.04, .015, .02), segments=8, ring_count=4))
    # rachaduras de brasa no peito (lado sem armadura) e no ventre
    for seed, start in ((1, Vector((-.12, -.36, 1.55))), (2, Vector((-.05, -.36, 1.25))), (3, Vector((.12, -.33, 1.12)))):
        rr = random.Random(seed); p = start
        for k in range(6):
            q = p + Vector((rr.uniform(-.06, .06), 0, rr.uniform(-.09, .05)))
            q.y = -.33 - .05*(1 - abs(q.z - 1.4)*1.5)
            ch.append(along("primitive_cylinder_add", ember, p, q, .009, vertices=5)); p = q
    # espada que o partiu, ainda cravada nas costas
    hilt, tip = Vector((.3, .62, 2.05)), Vector((-.22, -.72, 1.08))
    dv = (tip - hilt).normalized()
    steel = stained("g_aco", (.3, .3, .3), stain=(.2, .02, .01), amount=.4, scale=6, metal=1, rough=.3, grime=.2)
    blade = prim("primitive_cube_add", steel, (hilt + tip)/2 + dv*.12, (.1, .014, (tip - hilt).length/2 - .12))
    blade.rotation_euler = dv.to_track_quat('Z', 'X').to_euler(); ch.append(blade)
    ch.append(along("primitive_cone_add", steel, tip, tip + dv*.2, .1, vertices=4, radius1=1, radius2=0))
    ch.append(along("primitive_cube_add", gold, hilt + Vector((-.22, .04, -.08)), hilt + Vector((.22, -.04, .08)), .035))
    grip_end = hilt - dv*.32
    ch.append(along("primitive_cylinder_add", leather, hilt, grip_end, .03, vertices=8))
    ch.append(prim("primitive_uv_sphere_add", gold, grip_end, (.055, .055, .055), segments=10, ring_count=6))
    ch.append(prim("primitive_uv_sphere_add", gut, tip - dv*.05, (.08, .05, .08), segments=8, ring_count=6))
    ch.append(prim("primitive_uv_sphere_add", gut, hilt + dv*.18, (.09, .06, .09), segments=8, ring_count=6))
    R.rigid(ch, "chest")

    # ------------------------------------------------ estandarte quebrado do próprio exército (arma, na mão direita)
    G, D = P("banner"), (P("banner", 1) - P("banner")).normalized()
    side = D.cross(Vector((0, 1, 0))).normalized()
    bn = []
    top = G + D*2.25
    bn.append(along("primitive_cylinder_add", leather, G - D*.22, top, .035, vertices=8))
    for k in range(5):  # ponta lascada
        a = 2*math.pi*k/5
        o = Vector((math.cos(a), math.sin(a), 0)); o = D.to_track_quat('Z', 'Y') @ o
        bn.append(along("primitive_cone_add", leather, top + o*.02, top + o*.03 + D*(.08 + .1*rnd.random()), .02, vertices=4, radius1=1, radius2=0))
    for k in range(3):  # anéis de ferro no mastro
        o = prim("primitive_cylinder_add", iron, G + D*(.35 + .6*k), (.05, .05, .03), vertices=10)
        o.rotation_euler = D.to_track_quat('Z', 'Y').to_euler(); bn.append(o)
    # águia/caveira de latão quebrada presa no mastro abaixo da quebra
    em = G + D*1.95
    bn.append(prim("primitive_uv_sphere_add", gold, em, (.09, .08, .1), segments=10, ring_count=8))
    bn.append(prim("primitive_uv_sphere_add", dark, em - Vector((0, .07, 0)) + D*.01, (.05, .02, .03), segments=8, ring_count=4))
    for s in (1, -1):
        bn.append(along("primitive_cone_add", gold, em + side*.06*s, em + side*.32*s + D*.18, .05, vertices=4, radius1=1, radius2=.1))
    # Lacre de Carne: naco de carne pregado no mastro com lacre de cera vermelha
    lc = G + D*1.25
    fwd = Vector((0, -1, 0)) - D*(-D.y); fwd.normalize()
    bn.append(prim("primitive_uv_sphere_add", gut, lc + fwd*.06, (.11, .07, .14), segments=12, ring_count=8))
    seal = prim("primitive_cylinder_add", flag, lc + fwd*.13, (.065, .065, .014), vertices=14)
    seal.rotation_euler = fwd.to_track_quat('Z', 'Y').to_euler(); bn.append(seal)
    bn.append(prim("primitive_uv_sphere_add", ember, lc + fwd*.145, (.025, .025, .025), segments=8, ring_count=6))
    for k, (dx, dz) in enumerate(((-.06, .08), (.06, .09), (0, -.1))):  # pregos
        q = lc + side*dx + D*dz
        bn.append(along("primitive_cylinder_add", iron, q + fwd*.16, q - fwd*.02, .008, vertices=5))
        bn.append(prim("primitive_cylinder_add", iron, q + fwd*.16, (.018, .018, .006), vertices=8))
        bn[-1].rotation_euler = fwd.to_track_quat('Z', 'Y').to_euler()
    # travessa e pano rasgado
    back = Vector((0, 1, 0)) - D*D.y; back.normalize()
    cross_a, cross_b = G + D*1.85 + back*.05, G + D*1.85 + back*.9
    bn.append(along("primitive_cylinder_add", leather, cross_a, cross_b, .02, vertices=6))
    bm = bmesh.new(); cols, rows = 10, 9; grid = []
    for r in range(rows):
        row = []
        for c in range(cols):
            u = c/(cols-1); p = cross_a.lerp(cross_b, u)
            drop = r*.14 * (1 - .2*abs(u - .5))
            row.append(bm.verts.new(p + Vector((.05*math.sin(u*6 + r*.8) + .015*r, 0, -drop))))
        grid.append(row)
    for r in range(rows-1):
        for c in range(cols-1):
            if r >= rows - 4 and rnd.random() < .22 + .12*(r - rows + 4): continue  # barra rasgada
            if r >= 2 and rnd.random() < .06: continue                            # furos de bala e lâmina
            bm.faces.new((grid[r][c], grid[r][c+1], grid[r+1][c+1], grid[r+1][c]))
    fl = obj_from_bm("estandarte", bm, flag); fl.modifiers.new("s", 'SOLIDIFY').thickness = .012; apply_mods(fl)
    bn.append(fl)
    mid = cross_a.lerp(cross_b, .5) + Vector((0, 0, -.48))
    for sx in (1, -1):  # sigilo dos dois lados do pano
        bn.append(prim("primitive_torus_add", gold, mid + Vector((.03*sx, 0, 0)), (.62, 1, 1), major_radius=.12, minor_radius=.016,
                       major_segments=18, minor_segments=4, rot=(0, 90, 0)))
        bn.append(prim("primitive_uv_sphere_add", ember, mid + Vector((.035*sx, 0, 0)), (.012, .035, .035), segments=8, ring_count=6))
    for k in range(4):  # franja de ouro velho na travessa
        q = cross_a.lerp(cross_b, (k + .5)/4)
        bn.append(along("primitive_cylinder_add", gold, q, q + Vector((.02, 0, -.16)), .01, vertices=4))
    R.rigid(bn, "banner")

    # ------------------------------------------------ toco: carne rasgada, costelas soltas, cinto de general
    st = []
    st.append(prim("primitive_torus_add", leather, (0, .15, .95), (1.15, .95, 1), major_radius=.3, minor_radius=.05,
                   major_segments=20, minor_segments=6))
    st.append(prim("primitive_cube_add", gold, (0, -.15, .95), (.08, .03, .06)))
    for k in range(10):  # farrapos de carne e pele pendurados na borda do toco
        a = 2*math.pi*k/10 + rnd.uniform(-.2, .2)
        p = Vector((.28*math.cos(a), .2 + .24*math.sin(a), .8))
        st.append(along("primitive_cone_add", gut if k % 3 else flesh, p, p + Vector((.05*math.cos(a), .05*math.sin(a), -.12 - .1*rnd.random())),
                        .05, vertices=6, radius1=1, radius2=.2))
    for s in (1, -1):  # costelas quebradas saindo
        for k in range(2):
            p = Vector((.2*s, .3 - .12*k, .88))
            st.append(along("primitive_cone_add", bone, p, p + Vector((.12*s, .08, -.15)), .02, vertices=5, radius1=1, radius2=.3))
    for k in range(14):  # crosta cauterizada com brasa por baixo
        a = 2*math.pi*k/14
        p = Vector((.24*math.cos(a), .2 + .2*math.sin(a), .74))
        st.append(prim("primitive_uv_sphere_add", ember if k % 2 else horn, p, (.06, .06, .03), segments=8, ring_count=4))
    st.append(prim("primitive_cylinder_add", ember, (0, .2, .73), (.2, .17, .02), vertices=16))
    R.rigid(st, "hips")
    # espinha e tripas arrastando
    for i, bn in enumerate(("tail1", "tail2", "tail3")):
        a, b = P(bn), P(bn, 1); parts = []
        nv = 5
        for k in range(nv):  # vértebras
            c = a.lerp(b, (k + .5)/nv)
            parts.append(prim("primitive_uv_sphere_add", bone, c, (.055 - .012*i, .05 - .01*i, .05 - .01*i), segments=10, ring_count=6))
            parts.append(along("primitive_cone_add", bone, c, c + Vector((0, 0, .07 - .015*i)), .02, vertices=4, radius1=1, radius2=0))
        for g, off in enumerate((Vector((.1, 0, .02)), Vector((-.09, .02, -.01)), Vector((.03, -.04, .04)))):
            if i == 2 and g == 2: continue
            pts = [a.lerp(b, k/6) + off*(1 + .4*math.sin(k + g)) + Vector((0, 0, .03*math.sin(k*1.7 + g)))
                   for k in range(7)]
            for p0, p1 in zip(pts, pts[1:]):
                parts.append(along("primitive_cylinder_add", gut, p0, p1, .045 - .008*i, vertices=8))
        for k in range(6):  # elos de corrente presos às tripas
            c = a.lerp(b, (k + .5)/6) + Vector((-.05, 0, .02))
            parts.append(prim("primitive_torus_add", iron, c, (1, 1, 1.6), major_radius=.04 - .006*i, minor_radius=.011,
                              major_segments=8, minor_segments=4, rot=(90*(k % 2), 0, 0)))
        R.rigid(parts, bn)
    return R, INFO

# ======================================================================= animações
# Postura base: deitado sobre o toco, tronco inclinado para a frente, apoiado nos cotovelos/mãos.
CRAWL = {"hips": {"x": 30}, "spine": {"x": 4}, "chest": {"x": 2}, "neck": {"x": -18}, "head": {"x": -14},
         "jaw": {"x": -6},
         "upper_arm.L": {"x": -38, "y": -14}, "upper_arm.R": {"x": -38, "y": 14},
         "forearm.L": {"bend": -45}, "forearm.R": {"bend": -45}, "hand.L": {"x": 25}, "hand.R": {"x": 25},
         "aim": {"banner": (-.55, -.1, 1)},
         "tail1": {"x": -40}, "tail2": {"x": -8}, "tail3": {"x": 4}, "plant": {"L": .05, "R": .05}}

def C(*p): return merge(CRAWL, *p)

def arm_cycle(side, ph):
    """Braço que se arrasta. ph 0..1: 0-.5 puxa (mão cravada, cotovelo dobra), .5-1 avança (mão no ar, estica)."""
    n = side
    if ph < .5:
        u = ph/.5
        return {f"forearm.{n}": {"bend": 6 - 70*u}, f"hand.{n}": {"x": -10 + 40*u}}, True
    u = (ph - .5)/.5; lift = math.sin(u*math.pi)
    return {f"upper_arm.{n}": {"x": -18*lift - 10*u}, f"forearm.{n}": {"bend": -64 + 70*u - 12*lift},
            f"hand.{n}": {"x": 30 - 40*u - 20*lift}}, False

def anims(R):
    UP = (-.25, -.15, 1)
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; b = math.sin(t)
        idle.append(C({"chest": {"x": -3*b}, "spine": {"x": -2*b}, "head": {"x": 4*b, "z": 7*math.sin(t*.5 + 1)},
                       "jaw": {"x": -5 - 6*max(0, b)}, "upper_arm.L": {"y": 2*b}, "upper_arm.R": {"y": -2*b},
                       "tail3": {"z": 6*math.sin(t + 1)}, "tail2": {"z": 3*math.sin(t)},
                       "aim": {"banner": (-.55 + .04*b, -.1, 1)}}))
    # andar: puxa o tronco com um braço de cada vez (cada puxada é um passo)
    walk = []
    for i in range(8):
        t = i/8
        aL, pL = arm_cycle("L", t); aR, pR = arm_cycle("R", (t + .5) % 1)
        pull = math.sin(t*2*math.pi)  # + puxando com a esquerda, - com a direita
        plant = {}
        if pL: plant["L"] = .05
        if pR: plant["R"] = .05
        walk.append(C(aL, aR, {"chest": {"z": 12*pull, "y": -5*pull}, "spine": {"z": 5*pull}, "hips": {"y": 6*pull, "z": -8*pull},
                               "head": {"z": -10*pull, "x": 4*abs(pull)}, "jaw": {"x": -6*abs(pull)},
                               "tail1": {"z": 10*pull}, "tail2": {"z": 10*pull}, "tail3": {"z": -14*pull},
                               "root": (0, -.06*abs(math.sin(t*4*math.pi)), 0),
                               "plant": plant, "aim": {"banner": (-.55 - .12*pull, -.05 + .1*pull, 1)}}))
    # estandarte (básico): ergue o mastro por cima do ombro e desce na frente
    lean = {"plant": {"L": .05}}
    wind = C(lean, {"upper_arm.R": {"x": -110, "y": 30}, "forearm.R": {"bend": -50}, "chest": {"x": -10, "z": -18},
                    "spine": {"x": -6}, "head": {"x": 6, "z": 10}, "jaw": {"x": -14}, "aim": {"banner": (-.2, .8, .6)}})
    chop = C(lean, {"upper_arm.R": {"x": -40, "y": 6}, "forearm.R": {"bend": -6}, "chest": {"x": 12, "z": 14},
                    "spine": {"x": 6}, "head": {"x": -10}, "jaw": {"x": -24}, "root": (0, -.18, 0),
                    "aim": {"banner": (-.1, -1, -.05)}})
    attack = keys_to_frames([(0, C()), (.32, wind), (.5, chop), (.7, merge(chop, {"chest": {"x": 3}})), (1, C())], 8)
    # golpe de estandarte: varre um leque de 100 graus da direita para a esquerda
    sw0 = C(lean, {"upper_arm.R": {"x": -60, "y": 50}, "forearm.R": {"bend": -20}, "chest": {"z": -32, "x": -6},
                   "spine": {"z": -10}, "head": {"z": 20}, "jaw": {"x": -10}, "aim": {"banner": (-1, .5, .25)}})
    sw1 = C(lean, {"upper_arm.R": {"x": -80, "y": 20, "z": 20}, "forearm.R": {"bend": -10}, "chest": {"z": 0, "x": 8},
                   "head": {"z": 0}, "jaw": {"x": -26}, "root": (0, -.12, 0), "aim": {"banner": (-.3, -1, .05)}})
    sw2 = C(lean, {"upper_arm.R": {"x": -70, "y": 0, "z": 50}, "forearm.R": {"bend": -10}, "chest": {"z": 34, "x": 8},
                   "spine": {"z": 12}, "head": {"z": -18}, "jaw": {"x": -20}, "root": (0, -.1, 0), "aim": {"banner": (1, -.5, .1)}})
    sweep = keys_to_frames([(0, C()), (.3, sw0), (.45, sw1), (.6, sw2), (.75, merge(sw2, {"chest": {"z": 4}})), (1, C())], 10)
    # arrasto: crava as mãos lá na frente e se joga
    reach = C({"hips": {"x": 12}, "chest": {"x": 6}, "upper_arm.L": {"x": -70, "y": -10}, "upper_arm.R": {"x": -70, "y": 10},
               "forearm.L": {"bend": 20}, "forearm.R": {"bend": 20}, "hand.L": {"x": -30}, "hand.R": {"x": -30},
               "head": {"x": -14}, "jaw": {"x": -20}, "plant": {}, "root": (0, .08, 0), "aim": {"banner": (-.3, -.7, .6)}})
    slam = C({"hips": {"x": 16}, "chest": {"x": 8}, "forearm.L": {"bend": 20}, "forearm.R": {"bend": 20},
              "hand.L": {"x": 0}, "hand.R": {"x": 0}, "jaw": {"x": -26}, "root": (0, -.1, 0),
              "plant": {"L": .05, "R": .05}, "aim": {"banner": (-.3, -.6, .7)}})
    hurl = C({"hips": {"x": 4}, "forearm.L": {"bend": -90}, "forearm.R": {"bend": -90}, "hand.L": {"x": 40}, "hand.R": {"x": 40},
              "head": {"x": -16}, "jaw": {"x": -30}, "root": (0, -.45, 0), "tail1": {"x": -10}, "tail2": {"x": -6},
              "plant": {"L": .05, "R": .05}, "aim": {"banner": (-.4, .2, 1)}})
    lunge = keys_to_frames([(0, C()), (.25, reach), (.42, slam), (.62, hurl), (.8, merge(hurl, {"jaw": {"x": 20}})), (1, C())], 8)
    # devorar (loop): cabeça enfiada na pilha, as duas mãos levando carne à boca
    eat = []
    for i in range(6):
        t = i/6*2*math.pi; c = math.cos(t)
        eat.append(C({"hips": {"x": 8}, "chest": {"x": 14 + 3*c}, "neck": {"x": 14}, "head": {"x": 22 + 5*c, "z": 6*math.sin(t)},
                      "jaw": {"x": -30*max(0, c) - 4}, "upper_arm.L": {"x": -25 + 8*c, "y": 10}, "upper_arm.R": {"x": -15, "y": -6},
                      "forearm.L": {"bend": -105 + 15*c}, "forearm.R": {"bend": -60}, "hand.L": {"x": -20},
                      "plant": {"R": .05}, "aim": {"banner": (-.6, .5, .8)}}))
    # ordem ao exército morto / troca de fase: ergue-se no toco e levanta o estandarte
    order_p = C({"hips": {"x": -26}, "spine": {"x": -6}, "chest": {"x": -6}, "neck": {"x": 4}, "head": {"x": -10},
                 "jaw": {"x": -42}, "upper_arm.R": {"x": -175, "y": 10}, "forearm.R": {"bend": -10},
                 "upper_arm.L": {"x": -20, "y": -55}, "forearm.L": {"bend": -50}, "hand.L": {"x": -20},
                 "tail1": {"x": 26}, "tail2": {"x": 6}, "plant": {}, "aim": {"banner": (-.15, .05, 1)}})
    shake = lambda k: merge(order_p, {"head": {"z": 6*(-1)**k}, "chest": {"z": 3*(-1)**k}, "jaw": {"x": -4*(k % 2)}})
    roar = keys_to_frames([(0, C()), (.28, order_p), (.42, shake(0)), (.56, shake(1)), (.7, shake(2)), (1, C())], 8)
    # vômito de brasa: ergue o peito e cospe para a frente (o fogo vem dos efeitos)
    puke0 = C({"hips": {"x": -12}, "chest": {"x": -14}, "neck": {"x": -10}, "head": {"x": -18}, "jaw": {"x": -8},
               "plant": {"L": .05, "R": .05}})
    puke1 = C({"hips": {"x": 6}, "chest": {"x": 12}, "neck": {"x": 18}, "head": {"x": 8}, "jaw": {"x": -48},
               "plant": {"L": .05, "R": .05}, "root": (0, -.08, 0)})
    vomit = keys_to_frames([(0, C()), (.3, puke0), (.45, puke1), (.6, merge(puke1, {"head": {"z": 8}})),
                            (.75, merge(puke1, {"head": {"z": -8}})), (1, C())], 8)
    # banquete: agarra com a mão esquerda, puxa para a boca e morde
    grab0 = C({"upper_arm.L": {"x": -70, "y": -20}, "forearm.L": {"bend": 10}, "hand.L": {"x": -40}, "chest": {"z": 20, "x": 10},
               "head": {"x": -16}, "jaw": {"x": -36}, "root": (0, -.3, 0), "plant": {"R": .05}})
    grab1 = C({"upper_arm.L": {"x": -40, "y": -10}, "forearm.L": {"bend": -125}, "hand.L": {"x": 20}, "chest": {"z": 6, "x": 6},
               "neck": {"x": 10}, "head": {"x": 16}, "jaw": {"x": -42}, "root": (0, -.1, 0), "plant": {"R": .05}})
    bite = merge(grab1, {"jaw": {"x": 44}, "head": {"x": 10, "z": 10}})
    feast = keys_to_frames([(0, C()), (.22, grab0), (.4, merge(grab0, {"forearm.L": {"bend": -40}})), (.58, grab1),
                            (.7, bite), (.82, merge(bite, {"head": {"z": -18}})), (1, C())], 10)
    # exausto (loop): desaba sobre o próprio peso, ofegante
    tired = []
    for i in range(6):
        t = i/6*2*math.pi; b = math.sin(t)
        tired.append(C({"hips": {"x": 16 + 3*b}, "chest": {"x": 8}, "neck": {"x": 20}, "head": {"x": 24 - 6*b, "z": 14},
                        "jaw": {"x": -18 - 8*max(0, b)}, "forearm.L": {"bend": -40}, "forearm.R": {"bend": -40},
                        "upper_arm.L": {"y": -14}, "upper_arm.R": {"y": 14}, "aim": {"banner": (-.9, .1, .35)}}))
    hitp = C({"hips": {"x": -8}, "chest": {"x": -14, "z": 8}, "head": {"x": -24, "z": 14}, "jaw": {"x": -22}, "root": (0, .1, 0)})
    hit = [hitp, lerp_pose(hitp, C(), .5), C()]
    # morte: tenta devorar o próprio estandarte e desaba; o estandarte fica caído no chão
    bannerbite = C({"hips": {"x": -6}, "upper_arm.R": {"x": -70, "y": -20}, "forearm.R": {"bend": -120}, "hand.R": {"x": 10},
                    "chest": {"z": -10}, "head": {"x": 6, "z": -14}, "jaw": {"x": -40}, "plant": {"L": .05},
                    "aim": {"banner": (-1, -.2, .45)}})
    chew = merge(bannerbite, {"jaw": {"x": 36}, "head": {"z": 6}})
    slump = C({"hips": {"x": 18}, "chest": {"x": 16}, "head": {"x": 30, "z": 20}, "jaw": {"x": -26},
               "upper_arm.L": {"x": 10, "y": -30}, "upper_arm.R": {"x": 0, "y": 30}, "forearm.L": {"bend": -30}, "forearm.R": {"bend": -40},
               "plant": {"L": .1}, "gb": ["spine", "chest", "hips"], "ground": .32, "aim": {"banner": (-1, -.3, .25)}})
    dead = C({"hips": {"x": 42}, "spine": {"x": 6}, "chest": {"x": 6}, "neck": {"x": 10}, "head": {"x": 16, "z": 40}, "jaw": {"x": -32},
              "upper_arm.L": {"x": -10, "y": -70}, "upper_arm.R": {"x": -10, "y": 70}, "forearm.L": {"bend": -10}, "forearm.R": {"bend": -20},
              "hand.L": {"x": 20}, "hand.R": {"x": 20}, "tail1": {"x": -20}, "tail3": {"z": 20},
              "plant": {"L": .1, "R": .1}, "gb": ["spine", "chest", "hips", "neck"], "ground": .3, "aim": {"banner": (-.35, -.94, -.02)}})
    death = keys_to_frames([(0, hitp), (.18, bannerbite), (.3, chew), (.42, bannerbite), (.52, chew), (.72, slump),
                            (.9, dead), (1, merge(dead, {"tail3": {"z": 8}}))], 12)
    return {"idle": idle, "walk": walk, "attack": attack, "sweep": sweep, "lunge": lunge, "eat": eat, "roar": roar,
            "vomit": vomit, "feast": feast, "tired": tired, "hit": hit, "death": death}
