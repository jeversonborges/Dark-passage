# Irmã Celeste, a Carpideira (chefe do andar 2: Ossário das Carpideiras). Freira das carpideiras de São Lázaro
# que desceu ao ossário para cantar aos mortos até dormirem de novo, e cantou por anos. Rege um coro de esqueletos
# e chora lágrimas de cera.
# Alta (~2,5 m), flutua sobre o hábito negro que arrasta no chão. Touca e babete de linho amarelado, véu negro que
# cai pelas costas, coroa de velas de igreja acesas sobre o véu (a cera escorre pelo véu e pelo rosto), rosto de
# porcelana cinzenta com os olhos fundos e a boca aberta cantando, lágrimas de cera escorrendo até o peito.
# Escapulário com a cruz de ossos, cordão de nós com um hinário encadernado em osso, batuta de osso com sininho
# de latão na mão direita, terço de dentes e falanges na esquerda.
# Brilho: as chamas das velas (uma cor quente só) e o brilho fraco das lágrimas.
# Animações: idle, walk (desliza), attack (toque de luto), lament (cone), weep (pranto que cai), conduct (regência,
# loop), choir (fase 2: levita alto e canta com o coro, loop), exhausted (caída no chão, loop), snuff (requiem:
# apaga as velas da sala com um gesto), summon (chama as carpideiras), hit, death (as velas da coroa apagam).
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion, Matrix
from mrig import *
import carpideira_de_ossos as CP
from carpideira_de_ossos import tube, skirt_wave, PANELS, SKB
from acougueiro import apron_sheet

INFO = {"px": 416, "target_z": 1.6, "rim": (1, .7, .4), "rim_e": 6.5, "colors": 48, "samples": 36,
        "loops": ("idle", "walk", "conduct", "choir", "exhausted"),
        "fps": {"idle": 6, "walk": 8, "attack": 12, "lament": 11, "weep": 10, "conduct": 8, "choir": 8, "exhausted": 5,
                "snuff": 10, "summon": 10, "hit": 12, "death": 9}}
SCALE = 1.45
def set_variant(name): pass

BONES = {k: v for k, v in CP.BONES.items() if k != "censer"}
_h, _t = Vector(BONES["hand.R"][0]), Vector(BONES["hand.R"][1]); _d = (_t - _h).normalized()
BONES["baton"] = (tuple(_t), tuple(_t + _d*.42), "hand.R")
_lt = Vector(BONES["hand.L"][1])
BONES["beads"] = (tuple(_lt), tuple(_lt + Vector((0, 0, -.32))), "hand.L")
BONES["flames"] = ((0, -.01, 1.98), (0, -.01, 2.1), "head")

def build():
    rnd = random.Random(7)
    habit = stained("ce_habito", (.03, .028, .032), stain=(.09, .085, .08), amount=.45, scale=2.5, rough=.85,
                    blotch=(.015, .013, .016), blotch_amt=.6, grime=1.5)
    veil = stained("ce_veu", (.022, .02, .026), stain=(.07, .065, .06), amount=.35, scale=3, rough=.6,
                   blotch=(.012, .011, .014), blotch_amt=.6, grime=.8)
    linen = stained("ce_linho", (.3, .27, .21), stain=(.16, .12, .07), amount=.55, scale=4, rough=.9,
                    blotch=(.26, .22, .16), blotch_amt=.6, grime=1.2)
    scap = stained("ce_escapulario", (.1, .095, .1), stain=(.13, .1, .08), amount=.5, scale=3, rough=.85, grime=1.2)
    skin = stained("ce_pele", (.36, .35, .33), stain=(.12, .1, .1), amount=.4, scale=6, rough=.35,
                   blotch=(.22, .2, .21), blotch_amt=.6, grime=.6)
    wax = stained("ce_cera", (.62, .55, .4), stain=(.35, .25, .12), amount=.35, scale=8, rough=.35, grime=.2)
    tearm = mat("ce_lagrima", (.75, .62, .4), 0, .25, emit=(1, .62, .3), strength=1.4)
    flame = mat("ce_chama", (1, .7, .3), emit=(1, .55, .18), strength=24)
    core = mat("ce_chama_nucleo", (1, .9, .6), emit=(1, .85, .5), strength=40)
    bone = stained("ce_osso", (.55, .5, .4), stain=(.1, .09, .07), amount=.45, scale=6, rough=.55, grime=.5)
    brass = stained("ce_latao", (.34, .22, .08), stain=(.06, .08, .05), amount=.5, scale=7, metal=1, rough=.4, grime=.3)
    iron = stained("ce_ferro", (.07, .06, .055), stain=(.22, .09, .04), amount=.55, scale=7, metal=.8, rough=.55, grime=.3)
    rope = mat("ce_cordao", (.16, .13, .09), 0, .9, dirt=.5)
    leather = stained("ce_couro", (.08, .05, .035), stain=(.12, .03, .02), amount=.4, scale=4, rough=.6, grime=.5)
    hole = mat("ce_buraco", (.004, .003, .003), 0, .95)
    tooth = mat("ce_dente", (.42, .38, .27), 0, .5, dirt=.6, grime=.2)

    R = Rig("irma_celeste", BONES, ground=None); P = R.P
    R.gexclude = {"veil1", "veil2", "baton", "beads", "flames"}

    # ------------------------------------------------ hábito negro: saia longa com cauda, sobretúnica rasgada
    def train(a, t):
        return Vector((0, .5*max(0, math.sin(a))*t**1.6, 0))
    zs = [1.06, .88, .68, .47, .26, .02]
    sk = tube("habito", habit, [(0, 0, z) for z in zs], [(.15, .13), (.2, .17), (.25, .21), (.29, .25), (.34, .3), (.42, .38)],
              seg=34, jag=.06, seed=4, holes=.03, offs=train, thick=.014)
    R.bind(sk, ["hips"] + SKB, power=4)
    ov = tube("sobretunica", veil, [(0, -.004, z) for z in (1.1, .92, .72, .52, .36)],
              [(.16, .14), (.22, .19), (.27, .23), (.31, .27), (.35, .31)], seg=30, jag=.16, seed=9, holes=.1,
              offs=lambda a, t: train(a, t*.7), thick=.01)
    R.bind(ov, ["hips"] + SKB, power=4)
    # escapulário cinza na frente, do peito até a barra, com a cruz de ossos e bainha puída
    sc = apron_sheet("escapulario", scap, 1.5, .1, .1, .12, lambda t: -.135 - .2*t**1.2, .03, rows=9, cols=5, jag=.05, seed=2)
    R.bind(sc, ["chest", "spine", "hips"] + SKB, power=4)

    # ------------------------------------------------ tronco vestido, guimpa de linho, braços com mangas de sino
    t = {"pelvis": (0, 0, 1.06, .14, .11), "waist": (0, 0, 1.2, .12, .095), "chest": (0, 0, 1.4, .155, .11),
         "neck": (0, -.01, 1.6, .05), "neck2": (0, -.025, 1.7, .045)}
    te = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh = P(f"upper_arm.{n}")
        t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, 0))), .06); te.append(("chest", f"sh{n}"))
    tor = skin_mesh("corpo", t, te, habit)
    R.bind(tor, ["hips", "spine", "chest", "neck"])
    bib = tube("guimpa", linen, [(0, -.02, 1.72), (0, -.015, 1.62), (0, -.005, 1.52), (0, 0, 1.44)],
               [(.075, .07), (.12, .1), (.19, .14), (.21, .15)], seg=26, jag=.03, seed=6, thick=.01)
    R.rigid([bib], "chest")
    cp = []
    # cruz de ossos no escapulário (fêmur e dois rádios amarrados)
    cx = Vector((0, -.15, 1.32))
    cp.append(along("primitive_cylinder_add", bone, cx + Vector((0, 0, .12)), cx + Vector((0, -.01, -.14)), .013, vertices=6))
    cp.append(along("primitive_cylinder_add", bone, cx + Vector((-.08, 0, .04)), cx + Vector((.08, 0, .04)), .011, vertices=6))
    for e_ in (cx + Vector((0, 0, .12)), cx + Vector((0, -.01, -.14)), cx + Vector((-.08, 0, .04)), cx + Vector((.08, 0, .04))):
        cp.append(prim("primitive_uv_sphere_add", bone, e_, (.017, .015, .017), segments=8, ring_count=5))
    cp.append(prim("primitive_torus_add", rope, cx + Vector((0, 0, .04)), (1, .6, 1), major_radius=.02, minor_radius=.006,
                   major_segments=10, minor_segments=4, rot=(90, 0, 45)))
    R.rigid(cp, "chest")
    # cordão de nós na cintura, pontas caídas, hinário encadernado em osso preso por corrente
    bl = [prim("primitive_torus_add", rope, (0, 0, 1.1), (1.05, .9, 1), major_radius=.15, minor_radius=.012, major_segments=22, minor_segments=5)]
    for k in range(2):
        x = .05 + .04*k; pts = [Vector((x, -.13, 1.09 - .12*i)) + Vector((.01*math.sin(i + k), -.01*i, 0)) for i in range(6)]
        for a_, b_ in zip(pts, pts[1:]):
            bl.append(along("primitive_cylinder_add", rope, a_, b_, .009, vertices=5))
        for p_ in pts[1::2]:
            bl.append(prim("primitive_uv_sphere_add", rope, p_, (.016,)*3, segments=6, ring_count=4))
    bk = Vector((-.17, -.06, .86))
    for k in range(5):
        bl.append(prim("primitive_torus_add", iron, Vector((-.15, -.07, 1.08)).lerp(bk + Vector((0, 0, .09)), k/4), (1, 1, 1.5),
                       major_radius=.011, minor_radius=.0035, major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
    book = prim("primitive_cube_add", leather, bk, (.065, .025, .085), rot=(0, 0, 25)); bl.append(book)
    bl.append(prim("primitive_cube_add", linen, bk + Vector((.004, -.002, 0)), (.06, .02, .08), rot=(0, 0, 25)))
    for dz in (-.06, 0, .06):
        bl.append(prim("primitive_cube_add", bone, bk + Vector((-.004, -.028, dz)), (.07, .006, .008), rot=(0, 0, 25)))
    R.rigid(bl, "hips")
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        arm_ = skin_mesh(f"braco.{n}", {"a": (*sh, .05), "b": (*el, .035), "c": (*wr, .028)}, [("a", "b"), ("b", "c")], skin)
        R.bind(arm_, ["chest", f"upper_arm.{n}", f"forearm.{n}"], power=4)
        d = (el - sh).normalized()
        slv = tube(f"manga.{n}", habit, [sh - d*.03, sh.lerp(el, .5), el, el + (wr - el)*.5],
                   [(.075, .07), (.085, .08), (.12, .11), (.19, .17)], seg=20, jag=.1, seed=20 + s, holes=.15, thick=.01)
        R.bind(slv, ["chest", f"upper_arm.{n}", f"forearm.{n}"], power=4)
        cuff = tube(f"punho.{n}", linen, [el + (wr - el)*.3, el + (wr - el)*.42], [(.055, .05), (.06, .055)], seg=14, thick=.006)
        R.rigid([cuff], f"forearm.{n}")
        # mãos longas e magras de porcelana, dedos de 3 falanges
        o, ax, u, sd = R.frame(f"hand.{n}")
        hp = [prim("primitive_uv_sphere_add", skin, o + ax*.035, (.034, .02, .045), segments=10, ring_count=6)]
        hp[0].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        curl = .6 if n == "R" else .35
        for f in range(4):
            base = o + ax*.07 + sd*(-.028 + .019*f); dd = (ax + sd*(f - 1.5)*.06).normalized(); L = .05 - .006*abs(f - 1.5)
            pts = [base]
            for k in range(3):
                dd = (Quaternion(sd, -curl*(k + 1)*.45) @ dd).normalized(); pts.append(pts[-1] + dd*L*(1 - .18*k))
            for a_, b_ in zip(pts, pts[1:]):
                hp.append(along("primitive_cylinder_add", skin, a_, b_, .0085, vertices=6))
        th = o + ax*.025 - sd*s*.03
        hp.append(along("primitive_cylinder_add", skin, th, th + ax*.05 - sd*s*.025 + u*.02, .009, vertices=6))
        R.rigid(hp, f"hand.{n}")

    # ------------------------------------------------ batuta de osso com fita preta e sininho de latão
    a, b = P("baton"), P("baton", 1); d = (b - a).normalized()
    bt = [along("primitive_cone_add", bone, a - d*.04, b, .014, vertices=8, radius1=1, radius2=.45),
          prim("primitive_uv_sphere_add", bone, a - d*.05, (.022,)*3, segments=8, ring_count=6)]
    for k in range(3):
        c_ = a + d*(.02 + .025*k)
        o2 = prim("primitive_torus_add", veil, c_, (1, 1, 1), major_radius=.016, minor_radius=.005, major_segments=10, minor_segments=4)
        o2.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); bt.append(o2)
    bt.append(along("primitive_cube_add", veil, a + d*.06, a + d*.06 + Vector((0, .03, -.16)), .008))
    bc = b + Vector((0, 0, -.035))
    bt.append(along("primitive_cylinder_add", iron, b, bc, .003, vertices=4))
    bt.append(along("primitive_cone_add", brass, bc + Vector((0, 0, .015)), bc - Vector((0, 0, .03)), .025, vertices=10, radius1=.35, radius2=1))
    R.rigid(bt, "baton")
    # terço de dentes e falanges pendurado na mão esquerda, com cruz de ferro
    a, b = P("beads"), P("beads", 1); bd = []
    for k in range(13):
        tt = k/12; c_ = a.lerp(b, tt) + Vector((.03*math.sin(tt*math.pi), -.02*math.sin(tt*math.pi*2), 0))
        if k % 3 == 0: bd.append(along("primitive_cylinder_add", bone, c_ + Vector((0, 0, .012)), c_ - Vector((0, 0, .012)), .008, vertices=5))
        else: bd.append(prim("primitive_uv_sphere_add", tooth, c_, (.009, .008, .011), segments=6, ring_count=4))
    bd.append(along("primitive_cube_add", iron, b, b + Vector((0, 0, -.1)), .008))
    bd.append(along("primitive_cube_add", iron, b + Vector((-.035, 0, -.03)), b + Vector((.035, 0, -.03)), .008))
    R.rigid(bd, "beads")

    # ------------------------------------------------ cabeça: rosto de porcelana, touca, lágrimas de cera, véu
    hd = []
    hc = Vector((0, -.035, 1.82))
    hd.append(prim("primitive_uv_sphere_add", skin, hc, (.075, .088, .098), segments=16, ring_count=10))
    hd.append(prim("primitive_uv_sphere_add", skin, hc + Vector((0, -.04, -.06)), (.045, .04, .035), segments=10, ring_count=6))
    for s in (1, -1):  # olhos fundos e fechados, maçãs magras
        hd.append(prim("primitive_uv_sphere_add", hole, hc + Vector((.03*s, -.078, .012)), (.022, .012, .014), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", skin, hc + Vector((.03*s, -.082, .018)), (.02, .008, .008), segments=8, ring_count=4))
        hd.append(prim("primitive_uv_sphere_add", skin, hc + Vector((.045*s, -.07, -.025)), (.018, .012, .015), segments=8, ring_count=5))
        # lágrimas de cera: escorrem dos olhos, engrossam e pingam sobre a guimpa
        pts = [hc + Vector((.032*s, -.088, .0)), hc + Vector((.036*s, -.09, -.04)), hc + Vector((.034*s, -.086, -.08)),
               hc + Vector((.03*s, -.075, -.12)), hc + Vector((.034*s, -.07, -.15))]
        for k, (a_, b_) in enumerate(zip(pts, pts[1:])):
            hd.append(along("primitive_cylinder_add", tearm, a_, b_, .0055 + .0015*k, vertices=6))
        hd.append(prim("primitive_uv_sphere_add", tearm, pts[-1] + Vector((0, 0, -.01)), (.011, .01, .015), segments=8, ring_count=5))
    hd.append(prim("primitive_uv_sphere_add", hole, hc + Vector((0, -.085, -.05)), (.022, .014, .028), segments=10, ring_count=6))  # boca cantando
    hd.append(prim("primitive_uv_sphere_add", skin, hc + Vector((0, -.096, .0)), (.01, .012, .028), segments=8, ring_count=5))       # nariz
    # touca de linho emoldurando o rosto
    hd.append(prim("primitive_torus_add", linen, hc + Vector((0, -.045, -.005)), (1, .7, 1.25), major_radius=.088, minor_radius=.02,
                   major_segments=22, minor_segments=6, rot=(90, 0, 0)))
    hd.append(prim("primitive_uv_sphere_add", linen, hc + Vector((0, .012, .02)), (.088, .095, .1), segments=14, ring_count=9))
    hd.append(prim("primitive_cube_add", linen, hc + Vector((0, -.02, .1)), (.1, .1, .012), rot=(-6, 0, 0)))  # banda da testa
    # coroa de velas: aro de ferro sobre o véu, 7 velas de igreja derretidas, cera escorrida
    ring_c = Vector((0, -.005, 1.98))
    hd.append(prim("primitive_torus_add", iron, ring_c, (1, 1.05, 1), major_radius=.1, minor_radius=.011, major_segments=20, minor_segments=5))
    fl = []
    rr = random.Random(5)
    for k in range(7):
        ang = math.radians(-90 + 360*k/7); v = Vector((math.cos(ang), math.sin(ang)*1.05, 0))
        h = rr.uniform(.08, .17) * (1.2 if k == 0 else 1)
        base = ring_c + v*.1
        hd.append(prim("primitive_cylinder_add", wax, base + Vector((0, 0, h/2)), (.017, .017, h/2), vertices=10))
        hd.append(prim("primitive_cylinder_add", iron, base + Vector((0, 0, .005)), (.024, .024, .008), vertices=10))
        for j in range(3):  # escorridos de cera pela vela e pelo aro
            q = base + v*.017 + Vector((0, 0, h*rr.uniform(.3, 1)))
            hd.append(along("primitive_cylinder_add", wax, q, q + Vector((0, 0, -rr.uniform(.04, .11))) + v*.004, .005, vertices=5))
        top = base + Vector((0, 0, h))
        hd.append(along("primitive_cylinder_add", hole, top, top + Vector((0, 0, .012)), .002, vertices=4))
        fl.append(prim("primitive_uv_sphere_add", flame, top + Vector((0, 0, .032)), (.012, .012, .03), segments=8, ring_count=6))
        fl.append(prim("primitive_uv_sphere_add", core, top + Vector((0, 0, .022)), (.006, .006, .014), segments=6, ring_count=4))
    for k in range(5):  # cera derretida pingada no véu, nas costas e nos lados da cabeça
        ang = math.radians(rr.uniform(-60, 240)); v = Vector((math.cos(ang), math.sin(ang), 0))
        q = ring_c + v*.11 - Vector((0, 0, .01))
        hd.append(along("primitive_cylinder_add", wax, q, q + v*.03 - Vector((0, 0, rr.uniform(.08, .2))), .007, vertices=5))
    R.rigid(hd, "head")
    R.rigid(fl, "flames")
    # véu negro: capuz sobre a touca que cai pelas costas até a cintura
    bm = bmesh.new(); rows, cols = 13, 15; g = []; vr = random.Random(41)
    for r in range(rows):
        tt = r/(rows - 1); row = []
        z = 1.95 - .95*tt
        rad = .07 + .055*min(1, tt/.12) + .2*max(0, tt - .12)
        yc = .0 + .26*max(0, tt - .1)**1.2
        for c in range(cols):
            u = c/(cols - 1); ang = math.radians(-112 + 224*u)
            row.append(bm.verts.new((rad*math.sin(ang), yc + rad*math.cos(ang)*(1.1 if tt < .14 else 1),
                                     z + (vr.uniform(-.1, .03) if r == rows - 1 else 0))))
        g.append(row)
    for r in range(rows - 1):
        for c in range(cols - 1):
            if r >= rows - 3 and vr.random() < .12: continue
            bm.faces.new((g[r][c], g[r][c+1], g[r+1][c+1], g[r+1][c]))
    vl = obj_from_bm("veu", bm, veil); vl.modifiers.new("s", 'SOLIDIFY').thickness = .009; apply_mods(vl)
    R.bind(vl, ["head", "veil1", "veil2"], power=4)
    R.rigid([prim("primitive_uv_sphere_add", hole, (0, -.13, 1.77), (.004,)*3, segments=4, ring_count=3)], "jaw")
    R.arm.scale = [SCALE]*3
    return R, INFO

# ======================================================================= animações
G = {"ground": None}
BASE = {"spine": {"x": 3}, "chest": {"x": 2}, "neck": {"x": 0}, "head": {"x": -6},
        "upper_arm.L": {"y": 30, "x": -24}, "upper_arm.R": {"y": -26, "x": -30},
        "forearm.L": {"bend": -55}, "forearm.R": {"bend": -60}, "hand.L": {"x": -10}, "hand.R": {"x": 20}}
AIM0 = {"veil1": (0, .3, -1), "veil2": (0, .22, -1), "beads": (0, 0, -1)}
H = .12  # altura que ela flutua

def M(*p): return merge(G, {k: dict(v) for k, v in BASE.items()}, {"root": (0, 0, H)}, *p)

def finish(frames):
    out = []
    for p in frames:
        p = dict(p); a = dict(AIM0); a.update(p.get("aim") or {}); p["aim"] = a; out.append(p)
    return out

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; b, c = math.sin(t), math.cos(t)
        idle.append(M(skirt_wave(t), {"root": (0, 0, H + .035*b), "chest": {"x": -2*b}, "head": {"x": 2*b, "z": 5*math.sin(t*.5)},
                                      "upper_arm.R": {"x": -4*b, "y": 3*c}, "hand.R": {"x": 8*c}, "forearm.L": {"bend": -3*b},
                                      "aim": {"beads": (.08*c, .06*b, -1), "veil1": (.04*b, .32, -1), "veil2": (.06*c, .28, -1)}}))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; b, c = math.sin(t), math.cos(t)
        walk.append(M(skirt_wave(t*2, 1.3, 16), {"root": (0, 0, H + .02 + .025*math.sin(2*t)), "hips": {"x": 5, "z": 3*b},
                                                 "chest": {"x": 4, "z": -5*b}, "head": {"z": 5*b},
                                                 "upper_arm.L": {"x": 8*b}, "upper_arm.R": {"x": -8*b},
                                                 "aim": {"beads": (.04, .35 + .12*c, -1), "veil1": (.05*b, .45, -1), "veil2": (.08*b, .55, -1)}}))
    # toque de luto: recolhe a mão esquerda junto ao peito e estende o toque à frente, devagar e frio
    gather = M(skirt_wave(0), {"upper_arm.L": {"x": -60, "y": -10, "z": -30}, "forearm.L": {"bend": -110}, "hand.L": {"x": -20},
                               "chest": {"z": 14, "x": -4}, "head": {"z": -8, "x": 6}, "root": (0, .05, H + .03)})
    reach = M(skirt_wave(1.2, 1, 12), {"upper_arm.L": {"x": -85, "y": 10, "z": 10}, "forearm.L": {"bend": -6}, "hand.L": {"x": 20},
                                      "chest": {"z": -18, "x": 12}, "spine": {"x": 6}, "head": {"x": -10, "z": 10},
                                      "root": (0, -.18, H), "aim": {"beads": (0, -.6, -1), "veil1": (0, .6, -1), "veil2": (0, .7, -1)}})
    attack = keys_to_frames([(0, M(skirt_wave(0))), (.3, gather), (.55, reach), (.72, merge(reach, {"hand.L": {"x": 12}})),
                             (1, M(skirt_wave(0)))], 9)
    # lamento: abraça o peito e abre os braços num grito em cone
    hug = M(skirt_wave(0, .6), {"upper_arm.L": {"x": -70, "y": -20, "z": -40}, "upper_arm.R": {"x": -70, "y": 20, "z": 40},
                                "forearm.L": {"bend": -110}, "forearm.R": {"bend": -110}, "spine": {"x": 8}, "chest": {"x": 12},
                                "head": {"x": 18}, "root": (0, .05, H - .02)})
    def scream(k):
        j = (-1)**k
        return M(skirt_wave(2 + k, 1.6, 22), {"upper_arm.L": {"x": -25 + 4*j, "y": -62}, "upper_arm.R": {"x": -25 - 4*j, "y": 62},
                                             "forearm.L": {"bend": -8}, "forearm.R": {"bend": -8}, "hand.L": {"x": 30}, "hand.R": {"x": -10},
                                             "spine": {"x": -8}, "chest": {"x": -6}, "head": {"x": -12, "z": 4*j},
                                             "root": (0, -.14, H + .1), "aim": {"veil1": (.1*j, .9, -.5), "veil2": (.15*j, 1, -.6), "beads": (.4, .5, -1)}})
    lament = keys_to_frames([(0, M(skirt_wave(0))), (.22, hug), (.42, scream(0)), (.56, scream(1)), (.7, scream(2)), (1, M(skirt_wave(0)))], 12)
    # pranto que cai: cobre o rosto chorando e depois ergue os braços ao teto (as lágrimas caem do alto)
    cover = M(skirt_wave(0, .5), {"upper_arm.L": {"x": -110, "y": -20, "z": -30}, "upper_arm.R": {"x": -110, "y": 20, "z": 30},
                                  "forearm.L": {"bend": -125}, "forearm.R": {"bend": -125}, "hand.L": {"x": -20}, "hand.R": {"x": -10},
                                  "spine": {"x": 10}, "chest": {"x": 12}, "head": {"x": 22}, "root": (0, .03, H - .02)})
    sob = lambda k: merge(cover, {"chest": {"x": 4*(-1)**k}, "head": {"x": 5*(-1)**k}, "root": (0, .03, H - .02 + .02*k)})
    raise_ = M(skirt_wave(1, 1.2, 8), {"upper_arm.L": {"x": -165, "y": -25}, "upper_arm.R": {"x": -165, "y": 25},
                                      "forearm.L": {"bend": -15}, "forearm.R": {"bend": -15}, "spine": {"x": -12}, "chest": {"x": -16},
                                      "head": {"x": -30}, "root": (0, 0, H + .22), "aim": {"veil1": (0, .5, -1), "beads": (.3, 0, -1)}})
    weep = keys_to_frames([(0, M(skirt_wave(0))), (.18, cover), (.3, sob(1)), (.42, sob(2)), (.6, raise_),
                           (.78, merge(raise_, {"upper_arm.L": {"x": 8}, "upper_arm.R": {"x": 8}})), (1, M(skirt_wave(0)))], 12)
    # regência (loop): rege o coro com a batuta em compasso de 4, a mão esquerda aberta segurando a nota
    conduct = []
    pat = [(-60, -20, 10), (-35, -5, 0), (-50, -50, -8), (-72, -10, 6), (-45, 30, 14), (-62, 5, 4), (-88, -10, -6), (-70, -22, 6)]
    for i, (x, y, hx) in enumerate(pat):
        t = i/8*2*math.pi
        conduct.append(M(skirt_wave(t, .8), {"upper_arm.R": {"x": x, "y": y - 20}, "forearm.R": {"bend": -40 + 10*math.sin(t)},
                                             "hand.R": {"x": hx}, "upper_arm.L": {"x": -70, "y": 20, "z": -10}, "forearm.L": {"bend": -30},
                                             "hand.L": {"x": 25}, "chest": {"z": 6*math.sin(t), "x": -4}, "head": {"x": -10, "z": -6*math.sin(t)},
                                             "root": (0, 0, H + .02 + .02*math.sin(2*t)), "aim": {"beads": (.1*math.sin(t), -.2, -1)}}))
    # coro completo (loop): sobe ao alto, braços abertos em cruz, cabeça para trás, véu e saia flutuando
    choir = []
    for i in range(8):
        t = i/8*2*math.pi; b = math.sin(t)
        choir.append(M(skirt_wave(t*2, 1.8, -4), {"root": (0, 0, H + .55 + .05*b), "upper_arm.L": {"x": -30 + 5*b, "y": -75},
                                                  "upper_arm.R": {"x": -30 - 5*b, "y": 75}, "forearm.L": {"bend": -10}, "forearm.R": {"bend": -12},
                                                  "hand.L": {"x": 30}, "hand.R": {"x": 15}, "spine": {"x": -8}, "chest": {"x": -10},
                                                  "head": {"x": -28 + 3*b}, "aim": {"veil1": (.15*b, .5, -.4), "veil2": (.2*b, .6, -.3), "beads": (0, 0, -1)}}))
    # exausta (loop): caída sentada no chão, o hábito espalhado, a cabeça pendendo, ofegando
    def spread(f, down):
        aim = {}
        for a, ba, bb in PANELS:
            o = Vector((math.cos(a), math.sin(a), 0))
            aim[ba] = tuple(o*f + Vector((0, 0, -1))); aim[bb] = tuple(o + Vector((0, 0, -down)))
        return aim
    exhausted = []
    for i in range(6):
        t = i/6*2*math.pi; b = math.sin(t)
        exhausted.append(M({"root": (0, .05, -.5 + .01*b), "spine": {"x": 22 + 2*b}, "chest": {"x": 18 + 3*b}, "neck": {"x": 14},
                            "head": {"x": 22 + 3*b, "z": 14}, "upper_arm.L": {"x": 12, "y": 18}, "upper_arm.R": {"x": 4, "y": -16},
                            "forearm.L": {"bend": -12}, "forearm.R": {"bend": -16}, "hand.L": {"x": 30}, "hand.R": {"x": 40},
                            "aim": dict(spread(1.1, .2), veil1=(0, .3, -1), veil2=(0, .5, -1), beads=(.2, -.3, -1))}))
    # requiem: leva a batuta à boca pedindo silêncio e varre o braço; as velas da sala apagam
    hush = M(skirt_wave(0, .5), {"upper_arm.R": {"x": -80, "y": -30, "z": 30}, "forearm.R": {"bend": -130}, "hand.R": {"x": -40},
                                 "head": {"x": 6}, "chest": {"z": 8}, "root": (0, 0, H + .04)})
    sweep = M(skirt_wave(1.5, 1.4, 10), {"upper_arm.R": {"x": -60, "y": -70, "z": -30}, "forearm.R": {"bend": -10}, "hand.R": {"x": 10},
                                        "upper_arm.L": {"x": -40, "y": -40}, "chest": {"z": -30}, "spine": {"z": -10}, "head": {"z": -20, "x": -6},
                                        "root": (0, 0, H + .06), "aim": {"veil1": (.5, .5, -.6), "veil2": (.6, .5, -.4)}})
    snuff = keys_to_frames([(0, M(skirt_wave(0))), (.25, hush), (.45, merge(hush, {"head": {"x": 4}})), (.7, sweep),
                            (.82, merge(sweep, {"chest": {"z": -6}})), (1, M(skirt_wave(0)))], 10)
    # chamado: ergue a batuta acima da cabeça e a desce de uma vez, chamando as carpideiras
    up = M(skirt_wave(.5, 1), {"upper_arm.R": {"x": -170, "y": -10}, "forearm.R": {"bend": -10}, "hand.R": {"x": -10},
                              "upper_arm.L": {"x": -90, "y": -30}, "forearm.L": {"bend": -40}, "chest": {"x": -12}, "head": {"x": -18},
                              "root": (0, .05, H + .18)})
    down = M(skirt_wave(1.6, 1.3, 14), {"upper_arm.R": {"x": -40, "y": -15}, "forearm.R": {"bend": -5}, "hand.R": {"x": 30},
                                       "upper_arm.L": {"x": -30, "y": 40}, "chest": {"x": 16}, "spine": {"x": 6}, "head": {"x": 8},
                                       "root": (0, -.08, H)})
    summon = keys_to_frames([(0, M(skirt_wave(0))), (.35, up), (.5, merge(up, {"upper_arm.R": {"x": -6}})), (.65, down),
                             (.8, merge(down, {"chest": {"x": -4}})), (1, M(skirt_wave(0)))], 10)
    hitp = M(skirt_wave(1.5, 1.2), {"chest": {"x": -18, "z": 10}, "spine": {"x": -6}, "head": {"x": -18, "z": 14},
                                    "upper_arm.L": {"y": -10, "x": 20}, "upper_arm.R": {"y": 14, "x": 20}, "root": (0, .1, H + .04),
                                    "aim": {"beads": (.3, -.3, -1)}})
    hit = [lerp_pose(M(skirt_wave(0)), hitp, .6), hitp, lerp_pose(hitp, M(skirt_wave(0)), .5), M(skirt_wave(0))]
    # morte: último canto para o alto, as velas da coroa se apagam e ela desaba sobre o próprio hábito
    wail = M(skirt_wave(1, 1.2), {"upper_arm.L": {"x": -120, "y": -25}, "upper_arm.R": {"x": -125, "y": 25}, "forearm.L": {"bend": -20},
                                  "forearm.R": {"bend": -20}, "spine": {"x": -14}, "chest": {"x": -18}, "head": {"x": -32},
                                  "root": (0, .05, H + .2)})
    slump = M({"root": (0, 0, -.42), "spine": {"x": 28}, "chest": {"x": 26}, "neck": {"x": 18}, "head": {"x": 26, "z": 18},
               "upper_arm.L": {"x": 10, "y": -10}, "upper_arm.R": {"x": 20, "y": 10}, "forearm.L": {"bend": -10}, "forearm.R": {"bend": -10},
               "scale": {"flames": .45}, "aim": dict(spread(.6, 1.2), veil1=(0, .5, -1), veil2=(0, .9, -.6), beads=(.2, .2, -1))})
    pile = M({"root": (0, 0, -.78), "hips": {"x": 25}, "spine": {"x": 45}, "chest": {"x": 30}, "neck": {"x": 15}, "head": {"x": 12, "z": 40},
              "upper_arm.L": {"x": -30, "y": 20}, "upper_arm.R": {"x": -55, "y": -25}, "forearm.L": {"bend": -20}, "forearm.R": {"bend": -10},
              "hand.R": {"x": 30}, "scale": {"flames": .001},
              "aim": dict(spread(1.4, .25), veil1=(.3, 1, -.6), veil2=(.4, 1, -.2), beads=(.6, -.3, -1))})
    death = keys_to_frames([(0, hitp), (.2, wail), (.38, merge(wail, {"head": {"x": -6}})), (.6, slump), (.82, pile), (1, pile)], 12)
    death = finish(death); CP.settle(R, death[6:])
    ex = finish(exhausted); CP.settle(R, ex)
    return {"idle": finish(idle), "walk": finish(walk), "attack": finish(attack), "lament": finish(lament), "weep": finish(weep),
            "conduct": finish(conduct), "choir": finish(choir), "exhausted": ex, "snuff": finish(snuff), "summon": finish(summon),
            "hit": finish(hit), "death": death}
