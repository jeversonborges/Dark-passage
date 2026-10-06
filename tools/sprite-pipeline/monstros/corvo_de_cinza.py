# Corvo de Cinza: corvo grande (envergadura ~1,4 m) que saiu das cinzas do Juízo. Penas cinzentas
# com as pontas queimadas e falhas, bico de ferro enferrujado e rachado (prótese rebitada no crânio),
# anel de latão com corrente partida na pata. Brilho: olhos de brasa.
# Voa o tempo todo: o corpo fica a ~1,3 m do chão (poses sem trava no chão, "ground": None);
# só a morte trava no chão (despenca e fica caído de asas abertas).
# Esqueleto próprio de ave: corpo, anca, cauda, pescoço, cabeça, bico inferior, asas em 3 ossos, pernas.
import bpy, bmesh, math, random
from mathutils import Vector
from mrig import *

INFO = {"px": 192, "target_z": 1.0, "rim": (.95, .55, .3), "colors": 40, "samples": 40,
        "fps": {"idle": 7, "walk": 12, "attack": 12, "hit": 12, "death": 10}}

VARIANTS = {
    # corvo mutado pela cinza: 1,6x o tamanho natural (envergadura ~2,2 m), para ler bem ao lado dos personagens
    "corvo_de_cinza": {"scale": 1.6, "px": 288, "tz": 1.45},
    # carniceiro: maior, penas quase pretas, pescoço pelado, bico em gancho, pedaços de carne pendurados
    "corvo_de_cinza_carnica": {"scale": 2.0, "tz": 1.75, "feather": (.06, .056, .055), "ash": (.13, .12, .115), "carrion": True,
                               "rim": (.9, .45, .32), "px": 352},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
    if "rim" in V: INFO["rim"] = V["rim"]
    if "px" in V: INFO["px"] = V["px"]
    if "tz" in V: INFO["target_z"] = V["tz"]

BONES = {
 "body":  ((0, .02, 1.3), (0, -.14, 1.33), None),
 "rump":  ((0, .02, 1.3), (0, .14, 1.28), "body"),
 "tail":  ((0, .14, 1.28), (0, .36, 1.27), "rump"),
 "neck":  ((0, -.14, 1.33), (0, -.22, 1.39), "body"),
 "head":  ((0, -.22, 1.39), (0, -.32, 1.41), "neck"),
 "jaw":   ((0, -.29, 1.385), (0, -.42, 1.37), "head"),
}
for s, n in ((1, "L"), (-1, "R")):
    BONES.update({
     f"wing1.{n}": ((.07*s, -.06, 1.34), (.21*s, -.05, 1.345), "body"),
     f"wing2.{n}": ((.21*s, -.05, 1.345), (.37*s, -.03, 1.345), f"wing1.{n}"),
     f"wing3.{n}": ((.37*s, -.03, 1.345), (.47*s, -.02, 1.345), f"wing2.{n}"),
     f"thigh.{n}": ((.045*s, -.02, 1.25), (.05*s, .02, 1.16), "body"),
     f"shin.{n}":  ((.05*s, .02, 1.16), (.05*s, 0, 1.05), f"thigh.{n}"),
    })

PROFILE = [(0, .25), (.1, .7), (.3, 1), (.55, .95), (.75, .75), (.9, .45), (1, .08)]

def feathers(name, specs, m0, m1, rnd, thick=.006):
    """Penas planas numa malha só. specs: (base, dir, cima, comprimento, largura, ini_queimado, caimento).
    A parte da ponta (t >= ini_queimado) usa o material queimado; bordas com falhas (barbas abertas)."""
    bm = bmesh.new()
    for base, d, up, L, W, burnt, droop in specs:
        d = Vector(d).normalized(); s = d.cross(Vector(up)).normalized(); n = s.cross(d)
        nl = rnd.random() < .35; nr = rnd.random() < .35
        ls, rs = [], []
        for i, (t, w) in enumerate(PROFILE):
            jl = rnd.uniform(.45, .8) if nl and .3 < t < .9 and rnd.random() < .5 else 1
            jr = rnd.uniform(.45, .8) if nr and .3 < t < .9 and rnd.random() < .5 else 1
            c = Vector(base) + d*t*L - n*(droop*L*t*t)
            ls.append(bm.verts.new(c + s*w*W*.5*jl)); rs.append(bm.verts.new(c - s*w*W*.5*jr))
        for i in range(len(PROFILE) - 1):
            f = bm.faces.new((ls[i], ls[i+1], rs[i+1], rs[i]))
            f.material_index = 1 if PROFILE[i][0] >= burnt else 0
    o = obj_from_bm(name, bm, m0); o.data.materials.append(m1)
    sd = o.modifiers.new("s", 'SOLIDIFY'); sd.thickness = thick; apply_mods(o)
    return o

def build():
    rnd = random.Random(7)
    car = V.get("carrion")
    pena = stained("cv_pena" + V.get("name", ""), V.get("feather", (.15, .145, .14)), stain=(.03, .028, .026), amount=.5,
                   scale=5, rough=.85, blotch=V.get("ash", (.32, .31, .29)), blotch_amt=.55, grime=.25)
    queim = stained("cv_queimado", (.03, .027, .025), stain=(.16, .06, .02), amount=.35, scale=9, rough=.9, grime=0)
    pele = stained("cv_pele", (.06, .05, .05), stain=(.12, .03, .02), amount=.3, scale=8, rough=.6, grime=0)
    ferro = stained("cv_ferro", (.1, .08, .07), stain=(.3, .1, .035), amount=.6, scale=9, metal=.7, rough=.55, grime=0)
    latao = stained("cv_latao", (.45, .3, .12), stain=(.08, .06, .03), amount=.4, scale=7, metal=1, rough=.4, grime=0)
    unha = mat("cv_unha", (.12, .11, .1), 0, .4, grime=0)
    olho = mat("cv_olho", (1, .5, .15), emit=(1, .36, .06), strength=28)
    escuro = mat("cv_escuro", (.01, .008, .008), 0, .9)
    carne = stained("cv_carne", (.26, .05, .04), stain=(.07, .01, .01), amount=.45, scale=7, rough=.3, grime=0)
    osso = stained("cv_osso", (.4, .36, .28), stain=(.15, .03, .02), amount=.35, scale=6, rough=.6, grime=0)

    R = Rig("corvo", BONES, ground=None)
    P = R.P
    # ---------------------------------------------------------------- corpo
    j = {"tail": (0, .2, 1.285, .04, .03), "rump": (0, .11, 1.29, .075, .065), "belly": (0, .0, 1.285, .115, .11),
         "chest": (0, -.1, 1.305, .11, .105), "neck": (0, -.18, 1.36, .06), "nape": (0, -.24, 1.4, .05)}
    e = [("tail", "rump"), ("rump", "belly"), ("belly", "chest"), ("chest", "neck"), ("neck", "nape")]
    body = skin_mesh("corpo", j, e, pena)
    R.bind(body, ["rump", "body", "neck", "tail"])
    # penas de contorno eriçadas no dorso e no peito (silhueta desgrenhada)
    sp = []
    for k in range(46):
        u = rnd.uniform(-.13, .13); a = rnd.uniform(-2.4, 2.4)   # a=0: topo; +/-pi: barriga
        cy = -.02 + u; rx, rz = .095*(1 - (u/.2)**2), .09*(1 - (u/.22)**2)
        p = Vector((rx*math.sin(a), cy, 1.3 + rz*math.cos(a)))
        nrm = Vector((math.sin(a), 0, math.cos(a)))
        d = Vector((0, 1, 0)) + nrm*rnd.uniform(.15, .45)
        if abs(a) > 1.6: d = Vector((0, .4, -1)) + nrm*.3    # peito: penas caem para baixo
        sp.append((p, d, nrm, rnd.uniform(.07, .11), rnd.uniform(.035, .05), rnd.uniform(.55, .9), -.15))
    R.rigid([feathers("contorno", sp, pena, queim, rnd)], "body")
    # papo de penas espetadas no pescoço (hackles)
    sp = []
    for k in range(0 if car else 18):
        a = rnd.uniform(-2.2, 2.2); p = Vector((.05*math.sin(a), -.19 + rnd.uniform(-.03, .03), 1.37 + .05*math.cos(a)))
        nrm = Vector((math.sin(a), 0, math.cos(a)))
        d = Vector((0, .6, -.2)) + nrm*.5 if abs(a) < 1.6 else Vector((0, .25, -1)) + nrm*.2
        sp.append((p, d, nrm, rnd.uniform(.07, .1), .022, .7, 0))
    neckp = [feathers("papo", sp, pena, queim, rnd)] if sp else []
    if car:  # pescoço pelado de carniceiro, pele enrugada e uma gola de penas
        neckp.append(prim("primitive_uv_sphere_add", pele, (0, -.2, 1.375), (.048, .07, .05), segments=12, ring_count=8,
                          rot=(-35, 0, 0)))
        sp = []
        for k in range(16):
            a = 2*math.pi*k/16; nrm = Vector((math.sin(a), 0, math.cos(a)))
            sp.append((Vector((0, -.15, 1.34)) + nrm*.07, Vector((0, .5, 0)) + nrm*.8, Vector((0, 1, 0)),
                       rnd.uniform(.07, .1), .035, .6, 0))
        neckp.append(feathers("gola", sp, pena, queim, rnd))
    R.rigid(neckp, "neck")

    # ---------------------------------------------------------------- cabeça e bico de ferro
    hp = []
    hp.append(prim("primitive_uv_sphere_add", pele if car else pena, (0, -.265, 1.41), (.052, .07, .055), segments=14, ring_count=9))
    if car:  # cabeça pelada com cicatrizes e restos de penas
        for k in range(5):
            a = rnd.uniform(-1, 1)
            hp.append(along("primitive_cone_add", pena, (.04*math.sin(a), -.24, 1.45), (.06*math.sin(a), -.18, 1.47 + .02*k % .04), .012,
                            vertices=4, radius1=1, radius2=0))
    else:
        for k in range(7):  # penas eriçadas na nuca
            x = rnd.uniform(-.03, .03)
            hp.append(along("primitive_cone_add", pena, (x, -.25, 1.445), (x*1.5, -.17, 1.47 + rnd.uniform(-.01, .02)), .016,
                            vertices=4, radius1=1, radius2=0))
    for s in (1, -1):
        hp.append(prim("primitive_uv_sphere_add", escuro, (.037*s, -.29, 1.425), (.018, .02, .016), segments=8, ring_count=6))
        hp.append(prim("primitive_uv_sphere_add", olho, (.045*s, -.293, 1.427), (.009, .011, .009), segments=8, ring_count=6))
    # bico superior de ferro: grosso, rebitado no crânio por uma cinta
    b0, b1 = Vector((0, -.3, 1.405)), Vector((0, -.45, 1.385))
    beak = along("primitive_cone_add", ferro, b0, b1, .032, vertices=6, radius1=1, radius2=.08)
    beak.scale = (.032, .026, (b1 - b0).length/2); hp.append(beak)
    hp.append(along("primitive_cone_add", ferro, b0 + Vector((0, 0, .02)), b1 + Vector((0, .02, .003)), .012, vertices=4,
                    radius1=1, radius2=.2))  # quilha do bico
    if car:  # gancho
        h0 = b1 + Vector((0, .012, .0)); h1 = h0 + Vector((0, -.03, -.02)); h2 = h1 + Vector((0, .005, -.035))
        hp.append(along("primitive_cone_add", ferro, h0, h1, .011, vertices=5, radius1=1, radius2=.75))
        hp.append(along("primitive_cone_add", ferro, h1, h2, .008, vertices=5, radius1=1, radius2=0))
    else:  # ponta lascada e rachadura escura
        hp.append(along("primitive_cylinder_add", escuro, b0.lerp(b1, .25) + Vector((.024, 0, .002)),
                        b0.lerp(b1, .7) + Vector((.012, 0, -.006)), .003, vertices=4))
        hp.append(along("primitive_cylinder_add", escuro, b0.lerp(b1, .25) + Vector((-.024, 0, .004)),
                        b0.lerp(b1, .5) + Vector((-.018, 0, -.004)), .003, vertices=4))
    band = prim("primitive_torus_add", ferro, (0, -.302, 1.405), (1, 1, 1.15), major_radius=.04, minor_radius=.009,
                major_segments=14, minor_segments=4, rot=(90, 0, 0))
    hp.append(band)
    for a in (-60, 0, 60, 180):
        r = math.radians(a)
        hp.append(prim("primitive_uv_sphere_add", latao, (.045*math.sin(r), -.304, 1.405 + .05*math.cos(r)), (.007, .007, .007),
                       segments=6, ring_count=4))
    R.rigid(hp, "head")
    jp = [along("primitive_cone_add", ferro, (0, -.3, 1.385), (0, -.425, 1.372), .022, vertices=6, radius1=1, radius2=.1)]
    jp[0].scale = (.022, .016, jp[0].scale[2])
    if car:  # tira de carne no bico
        p0 = Vector((.005, -.4, 1.37))
        for k in range(3):
            p1 = p0 + Vector((.01*(-1)**k, .012, -.045))
            jp.append(along("primitive_cylinder_add", carne, p0, p1, .012 - .002*k, vertices=6)); p0 = p1
        jp.append(prim("primitive_uv_sphere_add", carne, p0, (.022, .02, .03), segments=8, ring_count=6))
    R.rigid(jp, "jaw")

    # ---------------------------------------------------------------- asas (penas por osso, presas rígidas)
    for s, n in ((1, "L"), (-1, "R")):
        X = lambda v: Vector((v[0]*s, v[1], v[2]))
        up = Vector((0, 0, 1))
        # borda de ataque (antebraço emplumado) pesada nos três ossos
        lj = {"a": (*X((.06, -.05, 1.34)), .045, .03), "b": (*X((.21, -.05, 1.345)), .035, .022),
              "c": (*X((.37, -.03, 1.345)), .028, .018), "d": (*X((.47, -.02, 1.345)), .016)}
        le = skin_mesh(f"borda.{n}", lj, [("a", "b"), ("b", "c"), ("c", "d")], pena, levels=1)
        R.bind(le, ["body", f"wing1.{n}", f"wing2.{n}", f"wing3.{n}"], power=6)
        miss = {rnd.randrange(1, 4), 4 + rnd.randrange(0, 3)} if not car else {2}
        # primárias: dedos abertos na ponta
        sp = []
        for i in range(8):
            t = i/7
            base = X((.37 + .1*t, -.03 + .01*t, 1.345))
            ang = math.radians(10 + 78*t)
            d = X((math.sin(ang), math.cos(ang), 0))
            L = .2 + .08*t - (.06 if i == 5 else 0)
            sp.append((base, d, up, L, .05 - .008*t, rnd.uniform(.55, .8), .12))
        p3 = [feathers(f"primarias.{n}", sp, pena, queim, rnd)]
        # cobertoras da mão
        sp = [(X((.37 + .1*k/3, -.035, 1.352)), X((.25, 1, 0)), up, .1, .05, .8, .05) for k in range(4)]
        p3.append(feathers(f"cob3.{n}", sp, pena, queim, rnd))
        R.rigid(p3, f"wing3.{n}")
        # secundárias
        for bn, x0, x1, cnt, L0, L1 in ((f"wing2.{n}", .21, .37, 5, .22, .2), (f"wing1.{n}", .075, .21, 4, .2, .17)):
            sp = []
            for k in range(cnt):
                if bn.startswith("wing2") and k in miss: continue
                if bn.startswith("wing1") and k + 10 in miss: continue
                x = x0 + (x1 - x0)*(k + .5)/cnt
                ang = math.radians(4 + 8*(x - .07)/.3)
                L = L0 + (L1 - L0)*(1 - (k + .5)/cnt) + rnd.uniform(-.03, .015)
                sp.append((X((x, -.045, 1.343)), X((math.sin(ang), math.cos(ang), 0)), up, L, .055,
                           rnd.uniform(.5, .78), .1))
            ob = [feathers(f"sec.{bn}", sp, pena, queim, rnd)]
            sp = [(X((x0 + (x1 - x0)*(k + .5)/cnt, -.05, 1.355)), X((.1, 1, 0)), up, rnd.uniform(.09, .12), .05,
                   .85, .05) for k in range(cnt)]
            ob.append(feathers(f"cob.{bn}", sp, pena, queim, rnd))
            if car and bn.startswith("wing1"):  # naco de carne preso nas penas
                c = X((.15, .02, 1.33))
                ob.append(prim("primitive_uv_sphere_add", carne, c, (.035, .03, .025), segments=8, ring_count=6))
                ob.append(along("primitive_cylinder_add", carne, c, c + Vector((0, .01, -.08)), .008, vertices=5))
            R.rigid(ob, bn)

    # ---------------------------------------------------------------- cauda em leque, pontas queimadas
    sp = []
    for k in range(9):
        if k == 6: continue
        a = math.radians(-26 + 52*k/8)
        sp.append((Vector((0, .2, 1.287)), Vector((math.sin(a), math.cos(a), -.02)), Vector((0, 0, 1)),
                   .24 - .02*abs(k - 4)/4 - (.07 if k == 2 else 0), .06, rnd.uniform(.55, .75), .05))
    tp = [feathers("cauda", sp, pena, queim, rnd)]
    if car:  # tripa pendurada presa na cauda
        p0 = Vector((.03, .26, 1.27))
        for k in range(4):
            p1 = p0 + Vector((.015*(-1)**k, .01, -.05)); tp.append(along("primitive_cylinder_add", carne, p0, p1, .011, vertices=6)); p0 = p1
    R.rigid(tp, "tail")

    # ---------------------------------------------------------------- pernas, garras, anel de latão
    for s, n in ((1, "L"), (-1, "R")):
        a, b = P(f"thigh.{n}"), P(f"thigh.{n}", 1)
        R.rigid([along("primitive_cone_add", pena, a, b, .03, vertices=8, radius1=1, radius2=.55)], f"thigh.{n}")
        a, b = P(f"shin.{n}"), P(f"shin.{n}", 1)
        lp = [along("primitive_cylinder_add", pele, a, b, .011, vertices=6)]
        for k in range(4):  # dedos com garras
            ang = math.radians((-28, 0, 28, 180)[k])
            d = Vector((math.sin(ang)*s, -math.cos(ang), -.25)).normalized()
            L = .05 if k < 3 else .035
            m_ = b + d*L
            lp.append(along("primitive_cylinder_add", pele, b, m_, .007, vertices=5))
            lp.append(along("primitive_cone_add", unha, m_, m_ + d*.025 + Vector((0, 0, -.015)), .006, vertices=5,
                            radius1=1, radius2=0))
        if n == "L":  # anel de latão com corrente partida
            c = a.lerp(b, .55)
            lp.append(prim("primitive_cylinder_add", latao, c, (.018, .018, .012), vertices=12))
            for k in range(3):
                lp.append(prim("primitive_torus_add", ferro, c + Vector((.01, .006*k, -.022 - .02*k)), (1, 1, 1.5),
                               major_radius=.009, minor_radius=.003, major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
        if car and n == "R":  # garra segurando um pedaço de osso com carne
            c = b + Vector((0, -.03, -.03))
            lp.append(along("primitive_cylinder_add", osso, c + Vector((-.05, 0, 0)), c + Vector((.05, -.01, -.01)), .011, vertices=6))
            lp.append(prim("primitive_uv_sphere_add", carne, c, (.035, .028, .025), segments=8, ring_count=6))
        R.rigid(lp, f"shin.{n}")
    R.arm.scale = [V.get("scale", 1)]*3
    safe_ground(R)
    return R, INFO

def safe_ground(R):
    """Contorna a trava no chão de mrig num quadro travado logo após quadros sem trava: com a ação ligada,
    o depsgraph reavalia a animação e a trava mede a pose errada. Aqui a trava roda sem ação (rascunho)
    e o quadro de verdade é gravado sem trava, com o root já corrigido."""
    orig = R.set_pose
    def sp(pose, frame):
        if pose.get("ground", R.ground) is None: return orig(pose, frame)
        ad = R.arm.animation_data; act = ad.action if ad else None
        if ad: ad.action = None
        orig(dict(pose), 1)
        tmp = R.arm.animation_data.action
        rb = R.arm.pose.bones[R.root]
        off = rb.bone.matrix_local.to_quaternion() @ rb.location
        R.arm.animation_data.action = act
        if tmp and tmp != act: bpy.data.actions.remove(tmp)
        p2 = dict(pose); p2["ground"] = None; p2["root"] = tuple(off); p2.pop("plant", None)
        orig(p2, frame)
    R.set_pose = sp

# ======================================================================= animações
def wings(a1=0, a2=0, a3=0, f1=0, f2=0, f3=0, tw=0):
    """a: ergue a asa (graus, por osso, relativo ao pai); f: varre para trás; tw: torce a borda de ataque para baixo."""
    out = {}
    for s, n in ((1, "L"), (-1, "R")):
        for k, (a, f) in enumerate(((a1, f1), (a2, f2), (a3, f3)), 1):
            out[f"wing{k}.{n}"] = {"y": -a*s, "z": f*s, "x": tw if k == 1 else 0}
    return out

TUCK = {"thigh.L": {"x": 70}, "thigh.R": {"x": 70}, "shin.L": {"bend": 40}, "shin.R": {"bend": 40}}
DANGLE = {"thigh.L": {"x": 15, "y": -6}, "thigh.R": {"x": 15, "y": 6}, "shin.L": {"bend": 15}, "shin.R": {"bend": 15}}

def flap(t, amp=45, mid=12, fold=28):
    """Ciclo de batida, t 0..1: t=0 asas no alto, .5 embaixo; recolhe a mão na subida."""
    p = 2*math.pi*t; c = math.cos(p); up = max(0, -math.sin(p))
    return wings(mid + amp*c, 14*math.cos(p - .7) - 6*up, 18*math.cos(p - 1.3) - 10*up,
                 -8*up, 22*up, fold*up, tw=-8*math.sin(p)), c

def anims(R):
    G = {"ground": None}
    idle = []
    for i in range(6):  # pairando: corpo de pé, batida lenta, pernas soltas
        t = i/6; w, c = flap(t, 38, 18, 22)
        idle.append(merge(G, DANGLE, w, {"body": {"x": -24 + 3*c}, "neck": {"x": 14}, "head": {"x": 10 - 3*c, "z": 8*math.sin(2*math.pi*t)},
                                         "tail": {"x": 14}, "rump": {"x": 6}, "root": (0, 0, -.05*c)}))
    walk = []
    for i in range(8):
        t = i/8; w, c = flap(t, 48, 8, 30)
        walk.append(merge(G, TUCK, w, {"body": {"x": 4 + 3*c}, "neck": {"x": -6}, "head": {"x": -4 - 2*c},
                                       "tail": {"x": -3*c, "z": 4*math.sin(2*math.pi*t)}, "root": (0, 0, -.06*c)}))
    base = idle[0]
    rise = merge(G, DANGLE, wings(72, 18, 8, 0, 10, 14), {"body": {"x": -38}, "neck": {"x": 20}, "head": {"x": 14},
                 "tail": {"x": 20}, "jaw": {"x": 8}, "root": (0, .12, .18)})
    dive = merge(G, TUCK, wings(38, -6, -10, 10, 40, 40), {"body": {"x": 48}, "neck": {"x": -14}, "head": {"x": 6},
                 "tail": {"x": -12}, "jaw": {"x": 28}, "root": (0, -.32, -.45)})
    peck = merge(G, TUCK, wings(-18, -8, -10, -10, 6, 8, tw=10), {"body": {"x": 56}, "neck": {"x": 22}, "head": {"x": 18},
                 "tail": {"x": -22}, "jaw": {"x": -2}, "root": (0, -.44, -.54)})
    pull = merge(G, DANGLE, wings(-35, -5, -8, 0, 0, 0), {"body": {"x": -22}, "neck": {"x": 4}, "head": {"x": -6},
                 "tail": {"x": 16}, "root": (0, -.2, -.3)})
    attack = keys_to_frames([(0, base), (.25, rise), (.42, dive), (.55, peck), (.64, merge(peck, {"head": {"x": 6}, "neck": {"x": 4}})),
                             (.8, pull), (1, base)], 10)
    hitp = merge(G, DANGLE, wings(62, 25, 20, -10, -10, 0), {"body": {"x": -40, "y": 10}, "neck": {"x": -22},
                 "head": {"x": -20, "z": 18}, "jaw": {"x": 22}, "tail": {"x": 24}, "root": (0, .14, .08)})
    hit = [hitp, lerp_pose(hitp, base, .5), base]
    # morte: tranco, tomba de lado, despenca girando e fica caído de asas abertas
    tumble = merge(G, DANGLE, wings(30, 40, 30, -20, 30, 30), {"body": {"x": 30, "y": 70}, "neck": {"x": -30}, "head": {"x": -20, "z": 30},
                   "jaw": {"x": 20}, "tail": {"x": 20}, "root": (0, .05, -.35)})
    fall = merge(G, DANGLE, wings(55, 30, 10, -10, 10, 10), {"body": {"x": 70, "y": 140}, "neck": {"x": -20}, "head": {"x": -30, "z": 20},
                 "jaw": {"x": 22}, "tail": {"x": 10}, "root": (0, .02, -.86)})
    GB = ["body", "rump", "neck", "head", "wing1.L", "wing2.L", "wing3.L", "wing1.R", "wing2.R", "wing3.R"]
    land = merge(TUCK, wings(-16, -6, -4, 0, 4, 6), {"body": {"x": 6, "y": 18}, "neck": {"x": 30}, "head": {"x": 30, "z": 50},
                 "jaw": {"x": 18}, "tail": {"x": -4}, "ground": .07, "gb": GB, "root": (0, 0, -1.0)})
    dead = merge(TUCK, wings(-8, -2, -2, -4, 2, 0), {"body": {"x": 4, "y": 24}, "neck": {"x": 34}, "head": {"x": 36, "z": 64},
                 "jaw": {"x": 24}, "tail": {"x": -6, "z": 10}, "ground": .06, "gb": GB, "root": (0, 0, -1.0)})
    death = keys_to_frames([(0, hitp), (.22, tumble), (.5, fall), (.66, land), (.8, merge(land, {"wing3.L": {"y": 6}})),
                            (1, dead)], 10)
    for p in death[6:]:  # a partir do impacto, sempre travado no chão
        if p.get("ground") is None: p["ground"] = .07; p["gb"] = GB
    return {"idle": idle, "walk": walk, "attack": attack, "hit": hit, "death": death}
