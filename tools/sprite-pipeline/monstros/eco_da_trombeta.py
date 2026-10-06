# Eco da Trombeta (cripta, andar 3): a meia nota da quinta trombeta que ficou presa no escuro e ganhou forma.
# Torso sem pernas envolto em trapos de coro (batina preta e sobrepeliz suja, gola franzida), que termina em
# tiras de pano no lugar das pernas. No lugar da cabeça, o funil amassado de uma trombeta de latão com pistões
# e o tubo entrando no peito; a boca da trombeta é o rosto. Tubos de órgão saem das costas presos por uma
# armação de ferro e correias de couro; uma placa de chumbo (o lacre) pende da corrente no peito.
# Fiapos de pano flutuam dos ombros. Brilho: âmbar-dourado dentro da boca da trombeta (só a câmera vê).
# Sempre flutuando ("ground": None). Ossos extras: robe1/robe2 (barra do pano), fio1/fio2 (fiapos),
# "crush" (funil amassado da morte, escondido) e "floor" (sem pai, fixo no chão: monte de pano e trombeta
# caída do fim da morte). Peças escondidas usam a chave de pose "scale".
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *
from querubim_desfeito import glow

INFO = {"px": 256, "target_z": 1.1, "rim": (.8, .72, .55), "colors": 44, "samples": 40,
        "loops": ("idle", "walk", "resonate"),
        "fps": {"idle": 8, "walk": 10, "attack": 12, "wave": 12, "resonate": 10, "hit": 12, "death": 10}}

THROAT = Vector((0, -.12, 1.74)); BAX = Vector((0, -1, .32)).normalized()
BONES = {
 "hips":  ((0, 0, .95), (0, 0, 1.12), None),
 "spine": ((0, 0, 1.12), (0, 0, 1.32), "hips"),
 "chest": ((0, 0, 1.32), (0, 0, 1.56), "spine"),
 "neck":  ((0, 0, 1.56), (0, -.08, 1.7), "chest"),
 "head":  ((0, -.08, 1.7), tuple(THROAT + BAX*.42), "neck"),
 "robe1": ((0, 0, .95), (0, .03, .62), "hips"),
 "robe2": ((0, .03, .62), (0, .08, .22), "robe1"),
 "bell":  ((0, -.08, 1.7), (0, -.2, 1.75), "head"),
 "crush": ((0, -.081, 1.7), (0, -.2, 1.75), "head"),
 "floor": ((0, 0, 0), (0, 0, .1), None),
}
for s, n in ((1, "L"), (-1, "R")):
    BONES.update({
     f"upper_arm.{n}": ((.2*s, .0, 1.5), (.36*s, -.02, 1.24), "chest"),
     f"forearm.{n}":   ((.36*s, -.02, 1.24), (.48*s, -.08, 1.02), f"upper_arm.{n}"),
     f"hand.{n}":      ((.48*s, -.08, 1.02), (.52*s, -.11, .92), f"forearm.{n}"),
     f"fio1.{n}":      ((.17*s, .08, 1.52), (.34*s, .3, 1.6), "chest"),
     f"fio2.{n}":      ((.34*s, .3, 1.6), (.5*s, .55, 1.52), f"fio1.{n}"),
    })
HIDE = ("crush", "floor", "bell")

def bell(name, m, o, ax, L, r0, r1, dents, rnd, crush=0.0, seg=26, rings=18):
    """Funil de trombeta ao longo de ax a partir de o: raio r0 -> r1 (abertura exponencial), com amassados."""
    ax = Vector(ax).normalized(); q = ax.to_track_quat('Z', 'Y')
    bm = bmesh.new(); grid = []
    for i in range(rings + 1):
        t = i/rings; r = r0 + (r1 - r0)*t**3.2
        row = []
        for k in range(seg):
            a = 2*math.pi*k/seg; v = Vector((math.cos(a), math.sin(a), 0))
            p = Vector((0, 0, L*t)) + v*r
            for (da, dt, dep, w) in dents:  # amassado: empurra para dentro perto de (ângulo, t)
                dd = math.acos(max(-1, min(1, math.cos(a - da))))
                p -= v*dep*r*math.exp(-(dd/w)**2 - ((t - dt)/.18)**2)
            if crush:
                p.x *= 1 - crush*.5*t; p.y *= 1 + crush*.15*t; p += v*rnd.uniform(-.03, .03)*crush*r
            row.append(bm.verts.new(o + q @ p))
        grid.append(row)
    for i in range(rings):
        for k in range(seg):
            bm.faces.new((grid[i][k], grid[i][(k+1) % seg], grid[i+1][(k+1) % seg], grid[i+1][k]))
    bm.normal_update()
    ob = obj_from_bm(name, bm, m); sd = ob.modifiers.new("s", 'SOLIDIFY'); sd.thickness = .008; apply_mods(ob)
    return ob, q

def ribbon(name, m, pts, w, rnd, twist=0.0):
    """Tira de pano plana ao longo de pts (largura w, pontas rasgadas)."""
    bm = bmesh.new(); L, Rr = [], []
    for i, p in enumerate(pts):
        d = (pts[min(i+1, len(pts)-1)] - pts[max(i-1, 0)]).normalized()
        sd = d.cross(Vector((0, 0, 1)) if abs(d.z) < .9 else Vector((1, 0, 0))).normalized()
        sd = Quaternion(d, twist*i) @ sd
        ww = w*(1 - .6*(i/(len(pts)-1))**2)*rnd.uniform(.8, 1.1)
        L.append(bm.verts.new(p + sd*ww/2)); Rr.append(bm.verts.new(p - sd*ww/2))
    for i in range(len(pts)-1): bm.faces.new((L[i], L[i+1], Rr[i+1], Rr[i]))
    ob = obj_from_bm(name, bm, m); sd = ob.modifiers.new("s", 'SOLIDIFY'); sd.thickness = .006; apply_mods(ob)
    return ob

def build():
    rnd = random.Random(17)
    sobre = stained("e_sobrepeliz", (.38, .37, .33), stain=(.14, .1, .06), amount=.5, scale=3.5, rough=.95,
                    blotch=(.18, .17, .15), blotch_amt=.6, grime=1.4)
    batina = stained("e_batina", (.045, .04, .045), stain=(.1, .07, .05), amount=.4, scale=4, rough=.9,
                     blotch=(.08, .075, .08), blotch_amt=.5, grime=.6)
    pele = stained("e_pele", (.2, .21, .22), stain=(.05, .05, .06), amount=.4, scale=7, rough=.6,
                   blotch=(.13, .13, .15), blotch_amt=.5, grime=.4)
    latao = stained("e_latao", (.24, .16, .065), stain=(.06, .11, .085), amount=.75, scale=6, metal=.8, rough=.62,
                    blotch=(.1, .075, .04), blotch_amt=.6, grime=.1)
    latao_in = mat("e_latao_dentro", (.06, .04, .02), .6, .7, grime=0)
    ferro = stained("e_ferro", (.09, .075, .065), stain=(.28, .1, .04), amount=.55, scale=8, metal=.75, rough=.55, grime=.3)
    chumbo = stained("e_chumbo", (.2, .2, .21), stain=(.08, .08, .08), amount=.4, scale=6, metal=.5, rough=.6, grime=0)
    couro = stained("e_couro", (.06, .04, .028), stain=(.12, .03, .015), amount=.35, scale=6, rough=.6, grime=.3)
    oco = mat("e_oco", (.012, .01, .01), 0, .9)
    luz = glow("e_luz", (1, .6, .2), 2.6)

    R = Rig("eco", BONES, ground=None); R.gexclude = set(HIDE)
    P = R.P

    # ------------------------------------------------ corpo espectral (só aparece nos braços e mãos)
    j = {"waist": (0, 0, 1.0, .13, .1), "chest": (0, 0, 1.35, .17, .12), "top": (0, 0, 1.52, .15, .1)}
    e = [("waist", "chest"), ("chest", "top")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        j[f"sh{n}"] = (*sh, .05); j[f"el{n}"] = (*el, .035); j[f"wr{n}"] = (*wr, .026)
        e += [("top", f"sh{n}"), (f"sh{n}", f"el{n}"), (f"el{n}", f"wr{n}")]
    body = skin_mesh("corpo", j, e, pele, levels=1)
    R.bind(body, ["hips", "spine", "chest", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])
    for s, n in ((1, "L"), (-1, "R")):  # mãos magras de dedos longos
        o, ax, u, sd = R.frame(f"hand.{n}", up=Vector((0, -1, 0)))
        hp = [prim("primitive_uv_sphere_add", pele, o + ax*.03, (.03, .02, .04), segments=10, ring_count=6)]
        hp[0].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        for f in range(4):
            b0 = o + ax*.06 + sd*(-.022 + .015*f)
            m_ = b0 + ax*.06 + u*.01
            hp.append(along("primitive_cylinder_add", pele, b0, m_, .0065, vertices=5))
            hp.append(along("primitive_cone_add", pele, m_, m_ + ax*.05 + u*.025, .006, vertices=5, radius1=1, radius2=.2))
        hp.append(along("primitive_cylinder_add", pele, o + ax*.02 - sd*s*.03, o + ax*.07 - sd*s*.06 - u*.01, .007, vertices=5))
        R.rigid(hp, f"hand.{n}")

    # ------------------------------------------------ batina preta (termina em farrapos) e sobrepeliz
    bt = skirt("batina", batina, [(1.57, .1, .08, 0), (1.5, .18, .13, 0), (1.32, .18, .135, 0), (1.1, .17, .135, .005),
                                   (.85, .17, .14, .02), (.6, .145, .12, .04), (.38, .11, .095, .06)],
               jag=.12, seed=3, thick=.008)
    R.bind(bt, ["hips", "spine", "chest", "robe1", "robe2"], power=3)
    sp = skirt("sobrepeliz", sobre, [(1.6, .09, .075, 0), (1.53, .19, .14, 0), (1.4, .2, .15, 0), (1.2, .2, .155, .005),
                                     (1.05, .23, .18, .015), (.92, .26, .2, .025)], jag=.09, seed=6, thick=.007)
    R.bind(sp, ["hips", "spine", "chest", "robe1"], power=3)
    for s, n in ((1, "L"), (-1, "R")):  # mangas largas em sino
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        o = skin_mesh(f"manga.{n}", {"a": (*(sh + Vector((-.02*s, 0, .01))), .08), "b": (*el, .085),
                                     "c": (*el.lerp(wr, .8), .12)}, [("a", "b"), ("b", "c")], sobre, levels=1)
        R.bind(o, ["chest", f"upper_arm.{n}", f"forearm.{n}"])
        for k in range(3):  # farrapos pendurados da manga
            p0 = el.lerp(wr, .75) + Vector((.05*math.cos(k*2.1), .05*math.sin(k*2.1), -.05))
            R.rigid([ribbon(f"farrapo.{n}{k}", sobre, [p0 + Vector((.01*i*s, .02*i, -.07*i)) for i in range(4)], .04, rnd)],
                    f"forearm.{n}")
    # farrapos compridos no lugar das pernas
    for k in range(11):
        a = 2*math.pi*k/11 + rnd.uniform(-.15, .15)
        r0 = .13; p0 = Vector((r0*math.cos(a), .03 + .11*math.sin(a), .5))
        L = rnd.uniform(.32, .45); pts = [p0 + Vector((.03*math.cos(a)*i, .04*i + .02*math.sin(a)*i, -L*i/4)) for i in range(5)]
        rb = ribbon(f"tira{k}", batina if k % 3 else sobre, pts, rnd.uniform(.06, .09), rnd, twist=.15)
        R.bind(rb, ["robe1", "robe2"], power=4)
    # gola franzida de coro
    ruff = []
    for k in range(20):
        a = 2*math.pi*k/20
        ruff.append(prim("primitive_uv_sphere_add", sobre, (.1*math.cos(a), .085*math.sin(a), 1.585), (.035, .035, .03),
                         segments=8, ring_count=5))
    R.rigid(ruff, "chest")

    # ------------------------------------------------ trombeta no lugar da cabeça
    dents = [(.6, .75, .35, .5), (2.6, .55, .25, .4), (4.3, .85, .5, .35), (5.4, .35, .2, .5)]
    bo, q = bell("funil", latao, THROAT, BAX, .42, .045, .3, dents, rnd)
    hd = [bo]
    mouth = THROAT + BAX*.42
    rim = prim("primitive_torus_add", latao, mouth, (1, 1, 1), major_radius=.295, minor_radius=.016, major_segments=30, minor_segments=6)
    rim.rotation_euler = q.to_euler(); hd.append(rim)
    # brilho por dentro: cone de luz na garganta e disco escuro atrás
    hd.append(along("primitive_cone_add", luz, THROAT + BAX*.06, THROAT + BAX*.3, .1, vertices=16, radius1=.3, radius2=1))
    # chumbo derretido escorrendo da borda (o lacre que calou a trombeta)
    for k, (a, L) in enumerate(((1.9, .1), (2.2, .16), (2.45, .07))):
        p = mouth + q @ Vector((math.cos(a)*.245, math.sin(a)*.295, .005))
        hd.append(along("primitive_cylinder_add", chumbo, p, p + Vector((0, 0, -L)), .016 - .003*k, vertices=6))
        hd.append(prim("primitive_uv_sphere_add", chumbo, p + Vector((0, 0, -L)), (.02, .02, .025), segments=8, ring_count=5))
    for k in range(10):  # rebites de um remendo no funil
        tz = .2 + .016*k; rt = .045 + .255*(tz/.42)**3.2 + .007; aa = -.4 + (.35 if k % 2 else 0)
        hd.append(prim("primitive_uv_sphere_add", ferro, THROAT + q @ Vector((math.cos(aa)*rt, math.sin(aa)*rt, tz)),
                       (.009, .009, .009), segments=6, ring_count=4))
    R.rigid(hd, "bell")
    # tubo de ligação, pistões e volta de tubo (o "pescoço")
    nk = []
    pts = [Vector((0, .0, 1.5)), Vector((0, -.02, 1.6)), Vector((0, -.06, 1.69)), THROAT + BAX*.01]
    for a, b in zip(pts, pts[1:]):
        nk.append(along("primitive_cylinder_add", latao, a, b, .035, vertices=10))
    for k in range(3):
        c = Vector((.075, -.02 - .045*k, 1.66 + .012*k))
        nk.append(prim("primitive_cylinder_add", latao, c, (.022, .022, .07), vertices=10))
        nk.append(prim("primitive_cylinder_add", ferro, c + Vector((0, 0, .08)), (.026, .026, .012), vertices=10))
        nk.append(along("primitive_cylinder_add", latao, c + Vector((0, 0, .09)), c + Vector((0, 0, .11 + .015*(k == 1))), .007, vertices=6))
        nk.append(prim("primitive_cylinder_add", couro if k != 1 else ferro, c + Vector((0, 0, .12 + .015*(k == 1))), (.02, .02, .008), vertices=10))
    loop = prim("primitive_torus_add", latao, (.13, -.07, 1.62), (1, 1.6, 1), major_radius=.07, minor_radius=.016,
                major_segments=18, minor_segments=6, rot=(0, 90, 0))
    nk.append(loop)
    R.rigid(nk, "neck")
    # funil amassado da morte (escondido)
    cb, _ = bell("funil_amassado", latao, THROAT, BAX, .38, .045, .24, dents + [(1.6, .9, .7, .6), (3.6, .8, .6, .5)], rnd, crush=1.0)
    R.rigid([cb], "crush")

    # ------------------------------------------------ tubos de órgão nas costas
    og = []
    xs = [-.21, -.13, -.05, .04, .12, .2]; tops = [1.88, 2.08, 2.22, 2.16, 1.98, 1.82]
    for k, (x, tz) in enumerate(zip(xs, tops)):
        r = .032 + .01*(1 - abs(k - 2.5)/2.5)
        b0 = Vector((x, .2, 1.2)); b1 = Vector((x*1.25 + (.04 if k == 4 else 0), .25 + (.05 if k == 1 else 0), tz))
        og.append(along("primitive_cylinder_add", latao, b0, b1, r, vertices=12))
        og.append(prim("primitive_cylinder_add", oco, b1, (r*.82, r*.82, .006), vertices=12))
        d = (b1 - b0).normalized(); mz = b0 + d*.22  # boca do tubo (fenda escura)
        og.append(prim("primitive_cube_add", oco, mz + Vector((0, -r*.9, 0)), (r*.6, .006, .025)))
        og.append(along("primitive_cone_add", latao, mz - d*.12, mz - d*.02, r*1.0, vertices=12, radius1=.3, radius2=1))
        if k == 4:  # ponta amassada torta
            og.append(along("primitive_cylinder_add", latao, b1, b1 + Vector((.05, .06, .06)), r*.9, vertices=10))
    for z in (1.3, 1.62):  # armação de ferro com rebites
        og.append(prim("primitive_cube_add", ferro, (0, .22, z), (.27, .025, .018)))
        for x in (-.24, -.08, .08, .24):
            og.append(prim("primitive_uv_sphere_add", latao, (x, .195, z), (.01, .01, .01), segments=6, ring_count=4))
    for s in (1, -1):  # correias de couro pelos ombros
        og.append(along("primitive_cylinder_add", couro, (.12*s, .19, 1.62), (.14*s, .02, 1.58), .016, vertices=6))
        og.append(along("primitive_cylinder_add", couro, (.14*s, .02, 1.58), (.1*s, -.16, 1.4), .016, vertices=6))
        og.append(along("primitive_cylinder_add", couro, (.1*s, -.16, 1.4), (.0, -.19, 1.2), .016, vertices=6))
    # corrente e placa de chumbo (o lacre) no peito
    for k in range(5):
        og.append(prim("primitive_torus_add", ferro, (.03*math.sin(k), -.2 - .005*k, 1.5 - .04*k), (1, 1, 1.5), major_radius=.016,
                       minor_radius=.005, major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
    og.append(prim("primitive_cylinder_add", chumbo, (0, -.215, 1.24), (.065, .065, .014), vertices=14, rot=(80, 0, 0)))
    og.append(prim("primitive_cube_add", oco, (0, -.232, 1.24), (.035, .004, .006)))
    og.append(prim("primitive_cube_add", oco, (0, -.232, 1.24), (.006, .004, .035)))
    R.rigid(og, "chest")
    # fiapos de pano flutuando dos ombros
    for s, n in ((1, "L"), (-1, "R")):
        for k in range(2):
            a, b = P(f"fio1.{n}"), P(f"fio1.{n}", 1)
            pts = [a.lerp(b, i/3) + Vector((0, 0, .03*k - .02*i*k)) for i in range(4)]
            R.rigid([ribbon(f"fio1.{n}{k}", sobre if k else batina, pts, .11 - .03*k, rnd, .35)], f"fio1.{n}")
            a, b = P(f"fio2.{n}"), P(f"fio2.{n}", 1)
            pts = [a.lerp(b, i/3) + Vector((0, 0, .03*k - .04*i*k + .02*math.sin(i*2))) for i in range(4)]
            R.rigid([ribbon(f"fio2.{n}{k}", sobre if k else batina, pts, .09 - .025*k, rnd, .35)], f"fio2.{n}")

    # ------------------------------------------------ monte de pano no chão + trombeta amassada (fim da morte)
    fl = []
    for layer, (m, rad, h, z0) in enumerate(((batina, .5, .1, 0), (sobre, .36, .08, .05))):
        bm = bmesh.new(); seg = 24; rings = 5; grid = []
        cen = bm.verts.new((0, -.05, z0 + h))
        for i in range(1, rings + 1):
            row = []
            for k in range(seg):
                a = 2*math.pi*k/seg; rr = rad*i/rings*(1 + .25*math.sin(3*a + layer) + rnd.uniform(-.1, .1)*(i == rings))
                z = z0 + h*(1 - (i/rings)**1.5) + rnd.uniform(-.015, .025)
                row.append(bm.verts.new((rr*math.cos(a), -.05 + rr*math.sin(a)*.9, max(.004, z))))
            grid.append(row)
        for k in range(seg): bm.faces.new((cen, grid[0][k], grid[0][(k+1) % seg]))
        for i in range(rings - 1):
            for k in range(seg):
                bm.faces.new((grid[i][k], grid[i+1][k], grid[i+1][(k+1) % seg], grid[i][(k+1) % seg]))
        ob = obj_from_bm(f"monte{layer}", bm, m); s_ = ob.modifiers.new("s", 'SOLIDIFY'); s_.thickness = .01
        ob.modifiers.new("sub", 'SUBSURF').levels = 1; apply_mods(ob); fl.append(ob)
    for k in range(7):  # tiras soltas espalhadas
        a = 2*math.pi*k/7 + .3
        p0 = Vector((.35*math.cos(a), -.05 + .32*math.sin(a), .01))
        fl.append(ribbon(f"tira_chao{k}", batina if k % 2 else sobre,
                         [p0 + Vector((.08*i*math.cos(a + .3*i), .08*i*math.sin(a + .3*i), 0)) for i in range(4)], .07, rnd))
    tb, _ = bell("trombeta_caida", latao, Vector((.05, .12, .2)), Vector((-.3, -1, -.35)), .38, .045, .24,
                 dents + [(1.6, .9, .7, .6)], rnd, crush=1.0)
    fl.append(tb)
    fl.append(along("primitive_cylinder_add", latao, (.05, .12, .2), (.1, .3, .16), .035, vertices=10))
    for k, (x, y, L) in enumerate(((-.3, .2, .6), (.25, .28, .45))):  # tubos de órgão caídos
        fl.append(along("primitive_cylinder_add", latao, (x, y, .04), (x + L*.8*(-1)**k, y + L*.4, .04), .035, vertices=12))
    R.rigid(fl, "floor")
    return R, INFO

# ======================================================================= animações
DEF = {"crush": 0, "floor": 0, "hips": 1, "bell": 1}
def fx(**k): return {"fx": k}

def finalize(poses):
    for p in poses:
        f = p.pop("fx", {}) or {}
        p["scale"] = {b: max(.001, DEF[b] + f.get(b, 0)) for b in DEF}
    return poses

BASE = {"ground": None, "upper_arm.L": {"y": 18, "x": -10}, "upper_arm.R": {"y": -18, "x": -10},
        "forearm.L": {"bend": -30}, "forearm.R": {"bend": -30}, "hand.L": {"x": -10}, "hand.R": {"x": -10},
        "head": {"x": 4}, "robe1": {"x": 6}, "robe2": {"x": 8}}
def E(*p): return merge(BASE, *p)

def fios(t, amp=12, up=0):
    out = {}
    for s, n in ((1, "L"), (-1, "R")):
        ph = t*2*math.pi + (0 if s > 0 else 1.3)
        out[f"fio1.{n}"] = {"y": -s*(amp*math.sin(ph) + up), "x": 6*math.cos(ph)}
        out[f"fio2.{n}"] = {"y": -s*(amp*1.3*math.sin(ph - 1) + up*.6), "x": 8*math.cos(ph - 1)}
    return out

def buzz(k, a=1.0):
    """Vibração de um quadro: tremida alternada no funil e no tronco."""
    sg = (-1)**k
    return {"head": {"z": 5*a*sg, "x": 3*a*sg}, "chest": {"z": -2*a*sg}, "root": (.012*a*sg, 0, 0)}

def anims(R):
    idle = []
    for i in range(6):
        t = i/6; s, c = math.sin(2*math.pi*t), math.cos(2*math.pi*t)
        idle.append(E(fios(t), buzz(i, .6), {"chest": {"x": 2*s}, "head": {"x": -3*s}, "robe1": {"x": 4*c, "z": 4*s},
                                              "robe2": {"x": 5*c, "z": 6*s}, "upper_arm.L": {"x": 4*s}, "upper_arm.R": {"x": -4*s},
                                              "root": (buzz(i, .6)["root"][0], 0, .05*s)}))
    walk = []
    for i in range(8):
        t = i/8; s, c = math.sin(2*math.pi*t), math.cos(2*math.pi*t)
        walk.append(E(fios(t, 16, -10), {"hips": {"x": 10}, "chest": {"x": 6}, "head": {"x": -4 + 2*s}, "robe1": {"x": 22 + 4*c, "z": 3*s},
                                          "robe2": {"x": 18 + 6*c, "z": 6*s}, "upper_arm.L": {"x": 25 + 5*s, "y": 6},
                                          "upper_arm.R": {"x": 25 - 5*s, "y": -6}, "forearm.L": {"bend": -10}, "forearm.R": {"bend": -10},
                                          "root": (0, 0, .06*s)}))
    base = idle[0]
    # zumbido: puxa o funil para trás e o projeta para a frente vibrando
    rear = E(fios(0, 8, 10), {"hips": {"x": -6}, "chest": {"x": -14}, "neck": {"x": -10}, "head": {"x": -18},
             "upper_arm.L": {"y": -10, "x": 20}, "upper_arm.R": {"y": 10, "x": 20}, "forearm.L": {"bend": -60}, "forearm.R": {"bend": -60},
             "robe1": {"x": -8}, "root": (0, .08, .04)})
    blast = E(fios(.5, 8, -20), {"hips": {"x": 12}, "chest": {"x": 18}, "neck": {"x": 10}, "head": {"x": 14},
              "upper_arm.L": {"y": -30, "x": -30}, "upper_arm.R": {"y": 30, "x": -30}, "forearm.L": {"bend": -10}, "forearm.R": {"bend": -10},
              "robe1": {"x": 20}, "robe2": {"x": 14}, "root": (0, -.1, 0)})
    attack = keys_to_frames([(0, base), (.28, rear), (.42, blast), (.56, merge(blast, buzz(0, 1.4))), (.68, merge(blast, buzz(1, 1.4))),
                             (.8, merge(blast, buzz(0, .8))), (1, base)], 9)
    # onda: se contrai (encolhe, abraça o funil), segura tremendo e solta tudo de uma vez
    contract = E(fios(0, 4, -30), {"hips": {"x": 16}, "spine": {"x": 14}, "chest": {"x": 22}, "neck": {"x": 18}, "head": {"x": 26},
                 "upper_arm.L": {"y": 40, "x": -60, "z": -30}, "upper_arm.R": {"y": -40, "x": -60, "z": 30},
                 "forearm.L": {"bend": -100}, "forearm.R": {"bend": -100}, "robe1": {"x": -18}, "robe2": {"x": -20},
                 "root": (0, 0, -.12)})
    release = E(fios(.3, 18, 40), {"hips": {"x": -12}, "spine": {"x": -8}, "chest": {"x": -16}, "neck": {"x": -8}, "head": {"x": -16},
                "upper_arm.L": {"y": -80, "x": -10}, "upper_arm.R": {"y": 80, "x": -10}, "forearm.L": {"bend": -6}, "forearm.R": {"bend": -6},
                "hand.L": {"x": 20}, "hand.R": {"x": 20}, "robe1": {"x": 26, "y": 10}, "robe2": {"x": 20}, "root": (0, .04, .14)})
    wave = keys_to_frames([(0, base), (.22, contract), (.32, merge(contract, buzz(0, 1.2))), (.42, merge(contract, buzz(1, 1.2))),
                           (.52, release), (.62, merge(release, buzz(0, 1.6))), (.72, merge(release, buzz(1, 1.6))),
                           (.82, merge(release, buzz(0, .8))), (1, base)], 12)
    # ressoar (loop de 3 s): braços abertos para o alto, funil para cima, tudo vibrando
    resonate = []
    for i in range(8):
        t = i/8; s = math.sin(2*math.pi*t)
        resonate.append(E(fios(t, 20, 30), buzz(i, 1.2), {"hips": {"x": -6}, "chest": {"x": -10 + 2*s}, "neck": {"x": -12},
                                                          "head": {"x": -26 + 3*s},
                                                          "upper_arm.L": {"y": -105 + 6*s, "x": -15}, "upper_arm.R": {"y": 105 - 6*s, "x": -15},
                                                          "forearm.L": {"bend": -30 - 10*s}, "forearm.R": {"bend": -30 + 10*s},
                                                          "hand.L": {"x": -20}, "hand.R": {"x": -20},
                                                          "robe1": {"x": 4, "z": 6*s}, "robe2": {"x": 6, "z": 10*s},
                                                          "root": (buzz(i, 1.2)["root"][0], 0, .1 + .04*s)}))
    hitp = E(fios(.2, 10, 20), {"hips": {"x": -10}, "chest": {"x": -18, "z": 10}, "neck": {"x": -10}, "head": {"x": -22, "z": 14},
             "upper_arm.L": {"y": -20, "x": 30}, "upper_arm.R": {"y": 20, "x": 30}, "forearm.L": {"bend": -50}, "forearm.R": {"bend": -50},
             "robe1": {"x": 20}, "robe2": {"x": 10}, "root": (0, .1, .04)})
    hit = [hitp, lerp_pose(hitp, base, .5), base]
    # morte: o funil amassa, o corpo murcha e o pano desaba num monte no chão
    crushp = merge(hitp, {"head": {"x": 30, "z": -20}, "neck": {"x": 20}, "chest": {"x": 10}}, fx(crush=1))
    sag = E(fios(.6, 4, -50), {"hips": {"x": 22}, "spine": {"x": 18}, "chest": {"x": 26}, "neck": {"x": 30}, "head": {"x": 40, "z": -24},
            "upper_arm.L": {"y": 45}, "upper_arm.R": {"y": -45}, "forearm.L": {"bend": -10}, "forearm.R": {"bend": -10},
            "robe1": {"x": -20}, "robe2": {"x": -30}, "root": (0, 0, -.32)}, fx(crush=1))
    sink = merge(sag, {"root": (0, -.02, -.82)}, fx(hips=-.55, floor=.55))
    gone = merge(sag, {"root": (0, -.02, -.95)}, fx(hips=-1, floor=1))
    death = keys_to_frames([(0, hitp), (.12, crushp), (.22, merge(crushp, buzz(0, 2))), (.32, merge(crushp, buzz(1, 2))),
                            (.5, sag), (.7, sink), (.85, gone), (1, gone)], 12)
    for p in death[1:]:  # o funil amassa de uma vez (troca de peça, sem interpolar)
        f = dict(p.get("fx") or {}); f["crush"] = 1; f["bell"] = -1; p["fx"] = f
    return {k: finalize(v) for k, v in {"idle": idle, "walk": walk, "attack": attack, "wave": wave, "resonate": resonate,
                                         "hit": hit, "death": death}.items()}
