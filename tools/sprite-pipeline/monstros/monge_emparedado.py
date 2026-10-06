# Monge Emparedado (Cripta da Trombeta Calada, andar 2: Ossário das Carpideiras). Monge enorme (~2,3 m)
# emparedado vivo numa cela do ossário; virou parte da alvenaria. Hábito de lã podre com capuz caído,
# pele cinza de argamassa rachada, tijolos e pedras grudados no corpo, um pedaço de parede fundido nas
# costas, punhos de pedra com grilhões, correntes de penitência cruzadas no peito, rosário de ferro.
# Brilho: olhos (âmbar de vela, fraco).
# Extras: ambush (encolhido atrás de um pedaço de parede de tijolos, rompe para a frente; os pedaços
# voam em arco e ficam no chão), pray (prece de pedra: ajoelha e uma crosta de pedra cresce no corpo),
# broken (postura QUEBRADA, loop).
# A parede são ~20 pedaços, cada um preso a um osso sem pai ("wp*"): girar 180 graus em X leva o pedaço
# num arco por cima do pivô até o chão à frente (pivô na metade da altura e da distância). Fora de
# ambush esses ossos ficam com escala 0.001 (somem). A crosta da prece usa ossos "crust.*" do mesmo jeito.
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *

INFO = {"px": 256, "target_z": 1.05, "rim": (.8, .7, .5), "colors": 44, "samples": 40,
        "loops": ("idle", "walk", "broken"),
        "fps": {"idle": 5, "walk": 7, "attack": 12, "ambush": 12, "pray": 10, "broken": 7, "hit": 12, "death": 10}}
SCALE = 1.28          # modelado em 1,8 m e escalado no objeto (2,3 m)

# ------------------------------------------------------------------ esqueleto
B = humanoid(1.0, 1.25)
for _n in "LR":  # braços 12% mais longos (gorila)
    _sh = Vector(B[f"upper_arm.{_n}"][0])
    for _b in (f"upper_arm.{_n}", f"forearm.{_n}", f"hand.{_n}"):
        _h, _t, _p = B[_b]
        B[_b] = (tuple(_sh + (Vector(_h)-_sh)*1.12), tuple(_sh + (Vector(_t)-_sh)*1.12), _p)
BODY = list(B)
CRUST = {  # crosta de pedra da prece: (centro, osso pai)
    "crust.chest": ((0, -.2, 1.3), "chest"), "crust.back": ((.02, .24, 1.3), "chest"),
    "crust.head": ((0, -.03, 1.74), "head"), "crust.belly": ((0, -.2, 1.08), "spine"),
}
for _s, _n in ((1, "L"), (-1, "R")):
    _a, _b2 = Vector(B[f"upper_arm.{_n}"][0]), Vector(B[f"upper_arm.{_n}"][1])
    CRUST[f"crust.arm.{_n}"] = (tuple(_a.lerp(_b2, .45)), f"upper_arm.{_n}")
    _a, _b2 = Vector(B[f"forearm.{_n}"][0]), Vector(B[f"forearm.{_n}"][1])
    CRUST[f"crust.fore.{_n}"] = (tuple(_a.lerp(_b2, .5)), f"forearm.{_n}")
    _a, _b2 = Vector(B[f"thigh.{_n}"][0]), Vector(B[f"thigh.{_n}"][1])
    CRUST[f"crust.thigh.{_n}"] = (tuple(_a.lerp(_b2, .45) + Vector((0, -.06, 0))), f"thigh.{_n}")
for _k, (_c, _p) in CRUST.items():
    B[_k] = (_c, tuple(Vector(_c) + Vector((0, 0, .06))), _p)
for _s, _n in ((1, "L"), (-1, "R")):  # corrente pendurada do grilhão do pulso
    _w = Vector(B[f"hand.{_n}"][0])
    B[f"chain.{_n}"] = (tuple(_w + Vector((0, .02, .02))), tuple(_w + Vector((0, .04, -.3))), f"forearm.{_n}")
B["rosary"] = ((0, -.24, 1.27), (0, -.25, 1.05), "chest")

# parede: tijolos em amarração corrida, divididos em pedaços
WALL_Y0, WALL_D, WALL_W, WALL_H = -.2, .17, 1.36, 1.3
BR_L, BR_H, GAP = .17, .072, .012
def _wall_bricks():
    rnd = random.Random(7); out = []
    rows = int(WALL_H/(BR_H + GAP))
    for r in range(rows):
        z = .006 + r*(BR_H + GAP) + BR_H/2; off = (BR_L + GAP)/2 if r % 2 else 0
        x = -WALL_W/2 + off - (BR_L + GAP)/2
        while x < WALL_W/2 + BR_L:
            x0, x1 = max(x - BR_L/2, -WALL_W/2), min(x + BR_L/2, WALL_W/2)
            if x1 - x0 > .03:
                top = rows - r  # topo irregular (parede quebrada)
                miss = (top <= 3 and rnd.random() < .18*(4 - top) + abs((x0+x1)/2)*.25)
                if not miss and not (r == 9 and abs(x - .2) < .1): out.append(((x0+x1)/2, z, x1-x0, rnd))
            x += BR_L + GAP
    return out
BRICKS = _wall_bricks()
_rs = random.Random(5)
SEEDS = []
for _gz in range(4):
    for _gx in range(5):
        SEEDS.append((-WALL_W/2 + (_gx + .5 + _rs.uniform(-.3, .3))*WALL_W/5, (_gz + .5 + _rs.uniform(-.3, .3))*WALL_H/4))
CHUNKS = {}
for _b in BRICKS:
    _i = min(range(len(SEEDS)), key=lambda i: (SEEDS[i][0]-_b[0])**2 + ((SEEDS[i][1]-_b[1])*1.5)**2)
    CHUNKS.setdefault(_i, []).append(_b)
WALL = {}  # osso: (pivô, centro, alcance) — pivô no meio do caminho entre o pedaço e o ponto onde cai
_rl = random.Random(9)
for _i, _bs in sorted(CHUNKS.items()):
    cx = sum(b[0] for b in _bs)/len(_bs); cz = sum(b[1] for b in _bs)/len(_bs)
    ztop = max(b[1] for b in _bs) + BR_H/2; cy = WALL_Y0 - WALL_D/2
    land = WALL_Y0 - .3 - .4*cz/WALL_H - _rl.uniform(0, .15)
    piv = Vector((cx, (land + cy)/2, ztop/2 + .004))
    B[f"wp{_i}"] = (tuple(piv), tuple(piv + Vector((0, 0, .1))), None)
    WALL[f"wp{_i}"] = (_i, cx, cz)
WALLB = list(WALL)

def rock(m, c, size, seed, sub=1, flat=True):
    """Pedra irregular (icosfera amassada)."""
    rr = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=1, location=(0, 0, 0))
    o = bpy.context.object; me = o.data
    for v in me.vertices:
        v.co = v.co*(1 + rr.uniform(-.22, .18))
    o.scale = size if isinstance(size, (tuple, list)) else (size,)*3
    o.rotation_euler = (rr.uniform(0, 6.3), rr.uniform(0, 6.3), rr.uniform(0, 6.3)); o.location = c
    me.materials.append(m)
    for p in me.polygons: p.use_smooth = not flat
    return o

def brick(m, c, dims, rot=(0, 0, 0)):
    o = prim("primitive_cube_add", m, c, (dims[0]/2, dims[1]/2, dims[2]/2), rot=rot, smooth=False)
    bv = o.modifiers.new("b", 'BEVEL'); bv.width = .008; bv.segments = 1; apply_mods(o)
    return o

def chain(m, pts, r=.022, thick=.007):
    """Corrente: elos alternados ao longo de uma polilinha."""
    out = []; pts = [Vector(p) for p in pts]
    L = sum((b - a).length for a, b in zip(pts, pts[1:])); n = max(2, int(L/(r*1.55)))
    seg = [(a, b, (b - a).length) for a, b in zip(pts, pts[1:])]
    for k in range(n):
        d = L*k/(n - 1) if n > 1 else 0
        for a, b, l in seg:
            if d <= l + 1e-6:
                p = a.lerp(b, d/max(l, 1e-6)); dv = (b - a).normalized(); break
            d -= l
        o = prim("primitive_torus_add", m, p, (1, 1, 1.55), major_radius=r, minor_radius=thick,
                 major_segments=8, minor_segments=4)
        q = dv.to_track_quat('Z', 'Y') @ Quaternion((0, 0, 1), math.pi/2*(k % 2))
        o.rotation_euler = q.to_euler(); out.append(o)
    return out

def build():
    rnd = random.Random(3)
    skin = stained("me_argamassa", (.33, .32, .3), stain=(.08, .075, .07), amount=.5, scale=5, rough=.85,
                   blotch=(.14, .135, .12), blotch_amt=.7, grime=1.1, dirt=.5)
    habit = stained("me_habito", (.07, .05, .035), stain=(.05, .06, .035), amount=.55, scale=3, rough=.95,
                    blotch=(.045, .04, .035), blotch_amt=.7, grime=1.4)
    brickm = stained("me_tijolo", (.14, .07, .05), stain=(.2, .2, .18), amount=.3, scale=6, rough=.9,
                     blotch=(.1, .055, .04), blotch_amt=.7, grime=.7)
    brick2 = stained("me_tijolo2", (.09, .055, .045), stain=(.03, .035, .02), amount=.4, scale=5, rough=.9,
                     blotch=(.07, .05, .04), blotch_amt=.6, grime=.7)
    mortar = stained("me_reboco", (.17, .165, .15), stain=(.1, .1, .08), amount=.4, scale=7, rough=.95, grime=.6)
    stone = stained("me_pedra", (.2, .195, .185), stain=(.07, .08, .05), amount=.45, scale=4, rough=.9,
                    blotch=(.11, .105, .1), blotch_amt=.6, grime=.5)
    iron = stained("me_ferro", (.08, .065, .055), stain=(.26, .1, .035), amount=.65, scale=7, metal=.75, rough=.6, grime=.3)
    rope = mat("me_corda", (.16, .13, .085), 0, .95, dirt=.5)
    hole = mat("me_buraco", (.006, .005, .005), 0, .95)
    crack = mat("me_fenda", (.03, .028, .026), 0, .9)
    eye = mat("me_olho", (1, .7, .3), emit=(1, .58, .16), strength=24)

    R = Rig("monge", B); P = R.P
    R.gexclude = set(WALLB) | {"chain.L", "chain.R", "rosary"} | set(CRUST)

    # ------------------------------------------------ corpo de argamassa
    j = {"pelvis": (0, .02, .95, .2, .15)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .13); j[f"thi{n}"] = (*h.lerp(k, .5), .12); j[f"knee{n}"] = (*k, .095)
        j[f"calf{n}"] = (*(k.lerp(a, .3) + Vector((0, .02, 0))), .1); j[f"ank{n}"] = (*a, .068)
        j[f"heel{n}"] = (*(a + Vector((0, .04, -.055))), .055)
        j[f"toe{n}"] = (*(P(f"foot.{n}", 1) + Vector((0, -.04, 0))), .06, .04)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"thi{n}"), (f"thi{n}", f"knee{n}"), (f"knee{n}", f"calf{n}"),
              (f"calf{n}", f"ank{n}"), (f"ank{n}", f"heel{n}"), (f"ank{n}", f"toe{n}")]
    legs = skin_mesh("pernas", j, e, skin)
    R.bind(legs, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R", "foot.L", "foot.R"])
    t = {"pelvis": (0, .02, .98, .22, .16), "belly": (0, -.02, 1.13, .24, .2), "chest": (0, .0, 1.32, .28, .2),
         "hump": (0, .12, 1.4, .22, .18), "neck": (0, .0, 1.5, .11), "neck2": (0, -.02, 1.58, .09)}
    te = [("pelvis", "belly"), ("belly", "chest"), ("chest", "hump"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"trap{n}"] = (.14*s, .03, 1.47, .12); t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, 0))), .14)
        t[f"bi{n}"] = (*sh.lerp(el, .45), .12); t[f"el{n}"] = (*el, .095)
        t[f"fa{n}"] = (*el.lerp(wr, .35), .12, .11); t[f"wr{n}"] = (*wr, .085)
        te += [("chest", f"trap{n}"), (f"trap{n}", f"sh{n}"), (f"sh{n}", f"bi{n}"), (f"bi{n}", f"el{n}"),
               (f"el{n}", f"fa{n}"), (f"fa{n}", f"wr{n}")]
    body = skin_mesh("tronco", t, te, skin)
    R.bind(body, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])

    # ------------------------------------------------ hábito podre: túnica até o tornozelo, rasgada
    robe = skirt("habito", habit, [(1.56, .12, .11, -.01), (1.49, .27, .2, .03), (1.36, .31, .24, .04),
                                   (1.18, .27, .23, .02), (.98, .25, .2, .02), (.75, .26, .21, .02),
                                   (.52, .27, .22, .03), (.36, .28, .22, .03)], open_front=.32, jag=.1, seed=4, thick=.012, seg=32)
    R.bind(robe, ["hips", "spine", "chest", "thigh.L", "thigh.R", "shin.L", "shin.R"], power=4)
    for s, n in ((1, "L"), (-1, "R")):  # mangas rasgadas até o cotovelo
        sh, el = P(f"upper_arm.{n}"), P(f"forearm.{n}")
        sj = {"a": (*(sh + Vector((-.03*s, 0, 0))), .155), "b": (*sh.lerp(el, .6), .14), "c": (*el.lerp(sh, .08), .135)}
        o = skin_mesh(f"manga.{n}", sj, [("a", "b"), ("b", "c")], habit, levels=1)
        R.bind(o, ["chest", f"upper_arm.{n}", f"forearm.{n}"])
        for k in range(4):  # farrapos pendurados da manga
            a = math.radians(40 + 70*k + rnd.uniform(-15, 15)); c = el.lerp(sh, .1)
            d = (el - sh).normalized(); side = d.cross(Vector((0, 1, 0))).normalized(); up = side.cross(d)
            p0 = c + (side*math.cos(a) + up*math.sin(a))*.13
            o = along("primitive_cone_add", habit, p0, p0 + d*.08 + Vector((0, 0, -.1 - .05*rnd.random())), .035,
                      vertices=4, radius1=1, radius2=.2)
            R.rigid([o], f"upper_arm.{n}")

    ch = []  # peças presas ao peito
    # capuz caído nas costas e gola
    ch.append(prim("primitive_torus_add", habit, (0, .02, 1.5), (1.15, 1.05, 1.2), major_radius=.14, minor_radius=.055,
                   major_segments=18, minor_segments=6))
    hood = prim("primitive_uv_sphere_add", habit, (0, .2, 1.45), (.17, .1, .16), segments=14, ring_count=8)
    ch.append(hood)
    ch.append(along("primitive_cone_add", habit, (0, .24, 1.36), (.03, .31, 1.12), .07, vertices=6, radius1=1, radius2=.15))
    # pedaço de parede fundido nas costas e no ombro esquerdo (3 fiadas, inclinado)
    qb = Quaternion((0, 1, 0), math.radians(-24)) @ Quaternion((1, 0, 0), math.radians(-12))
    base = Vector((.1, .28, 1.32))
    for r in range(4):
        for c in range(3 - (r == 3)):
            off = Vector(((c - 1 + .5*(r % 2))*(BR_L + GAP), 0, (r - 1.5)*(BR_H + GAP)))
            p = base + qb @ off
            o = brick(brickm if (r + c) % 3 else brick2, p, (BR_L, .1, BR_H)); o.rotation_euler = qb.to_euler()
            ch.append(o)
    ch.append(prim("primitive_cube_add", mortar, base + qb @ Vector((0, .035, 0)), (.24, .03, .15), smooth=False))
    ch[-1].rotation_euler = qb.to_euler()
    for k in range(5):  # argamassa escorrendo e grudando a parede ao corpo
        p = base + qb @ Vector((rnd.uniform(-.25, .25), -.05, rnd.uniform(-.2, .15)))
        ch.append(rock(mortar, p, (.06, .04, .05), 40 + k, flat=False))
    # tijolos e pedras grudados no peito, ombros e barriga
    for k, (p, rot, m) in enumerate(((Vector((-.2, -.17, 1.4)), (10, 20, -30), brickm), (Vector((-.24, -.1, 1.47)), (0, -40, 15), brick2),
                                     (Vector((.17, -.21, 1.18)), (-15, 10, 35), brickm), (Vector((-.05, -.23, 1.03)), (5, 0, -8), brick2))):
        o = brick(m, p, (BR_L*.9, .07, BR_H)); o.rotation_euler = [math.radians(a) for a in rot]; ch.append(o)
        ch.append(rock(mortar, p + Vector((0, .02, -.03)), (.07, .04, .04), 60 + k, flat=False))
    for k in range(6):
        a = rnd.uniform(-2.6, -.5); z = rnd.uniform(1.05, 1.42)
        ch.append(rock(stone, Vector((.27*math.cos(a), .21*math.sin(a), z)), rnd.uniform(.035, .06), 80 + k))
    # rachaduras escuras na argamassa (no peito, aparecendo pelo hábito aberto)
    for seed, start in ((1, Vector((.06, -.215, 1.42))), (2, Vector((-.1, -.22, 1.25)))):
        rr = random.Random(seed); p = start
        for k in range(4):
            q = p + Vector((rr.uniform(-.05, .05), 0, -rr.uniform(.04, .07))); q.y = -.215 - .01*rr.random()
            ch.append(along("primitive_cylinder_add", crack, p, q, .007, vertices=4)); p = q
    # correntes de penitência cruzadas no peito (bandoleira dupla) e na cintura
    ch += chain(iron, [(.27, -.08, 1.47), (.15, -.235, 1.32), (-.05, -.255, 1.14), (-.25, -.2, 1.0)], .026, .008)
    ch += chain(iron, [(-.25, -.2, 1.0), (-.3, .05, 1.0), (-.18, .26, 1.18), (.1, .3, 1.38), (.27, .14, 1.48)], .026, .008)
    # rosário de ferro: contas do pescoço ao peito
    for k in range(17):
        a = math.pi*k/16; x = .13*math.cos(a); zz = 1.5 - .22*math.sin(a); y = -.13 - .12*math.sin(a)
        ch.append(prim("primitive_uv_sphere_add", iron, (x, y, zz), (.018,)*3, segments=6, ring_count=4))
    R.rigid(ch, "chest")
    # cinto de corda com nós (cíngulo) e pontas penduradas
    cg = [prim("primitive_torus_add", rope, (0, .02, .99), (1.05, .86, 1), major_radius=.265, minor_radius=.022,
               major_segments=24, minor_segments=5)]
    for k, (x, l) in enumerate(((.1, .5), (.16, .38))):
        top = Vector((x, -.21, .98)); bot = top + Vector((.02*k, -.04, -l))
        cg.append(along("primitive_cylinder_add", rope, top, bot, .016, vertices=6))
        for u in (.35, .7, 1.0):
            cg.append(prim("primitive_uv_sphere_add", rope, top.lerp(bot, u), (.027,)*3, segments=8, ring_count=5))
    R.rigid(cg, "hips")
    # tijolos grudados na coxa e na canela
    for n, bone, p in (("L", "thigh.L", P("thigh.L").lerp(P("shin.L"), .5) + Vector((.07, -.12, 0))),
                       ("R", "shin.R", P("shin.R").lerp(P("foot.R"), .3) + Vector((-.05, -.08, 0)))):
        o = brick(brick2, p, (BR_L*.8, .06, BR_H)); o.rotation_euler = (0, math.radians(70), math.radians(15))
        R.rigid([o, rock(mortar, p + Vector((0, .03, 0)), (.05, .04, .06), 99, flat=False)], bone)

    # ------------------------------------------------ cabeça: careca cinza com tonsura, olhos fundos de brasa
    hp = []
    hc = Vector((0, -.04, 1.69))
    hp.append(prim("primitive_uv_sphere_add", skin, hc, (.1, .115, .12), segments=16, ring_count=10))
    hp.append(prim("primitive_uv_sphere_add", skin, hc + Vector((0, -.04, -.07)), (.085, .08, .065), segments=12, ring_count=8))
    hp.append(prim("primitive_uv_sphere_add", skin, hc + Vector((0, -.085, .02)), (.09, .03, .025), segments=10, ring_count=6))  # sobrancelha
    hp.append(prim("primitive_torus_add", habit, hc + Vector((0, .0, .045)), (1.02, 1.12, 1), major_radius=.095,
                   minor_radius=.022, major_segments=18, minor_segments=4))  # coroa de cabelo da tonsura
    for s in (1, -1):
        hp.append(prim("primitive_uv_sphere_add", hole, hc + Vector((.036*s, -.098, -.005)), (.026, .014, .017), segments=8, ring_count=6))
        hp.append(prim("primitive_uv_sphere_add", eye, hc + Vector((.036*s, -.106, -.005)), (.014, .007, .01), segments=8, ring_count=6))
        hp.append(prim("primitive_uv_sphere_add", skin, hc + Vector((.1*s, -.0, -.02)), (.018, .03, .035), segments=8, ring_count=6))
    hp.append(prim("primitive_uv_sphere_add", hole, hc + Vector((0, -.112, -.085)), (.04, .015, .016), segments=8, ring_count=6))
    hp.append(prim("primitive_cube_add", mortar, hc + Vector((0, -.118, -.085)), (.045, .008, .006), smooth=False))  # boca selada
    o = brick(brickm, hc + Vector((.07, -.02, .07)), (BR_L*.7, .05, BR_H*.8)); o.rotation_euler = (math.radians(20), math.radians(-35), math.radians(20)); hp.append(o)
    hp.append(rock(mortar, hc + Vector((.065, .0, .05)), (.05, .04, .04), 120, flat=False))
    hp.append(rock(stone, hc + Vector((-.08, .05, .02)), .04, 121))
    for o in hp:
        o.location = hc + (o.location - hc)*1.15 + Vector((0, 0, .02)); o.scale = o.scale*1.15
    R.rigid(hp, "head")

    # ------------------------------------------------ punhos de pedra com grilhões
    for s, n in ((1, "L"), (-1, "R")):
        o, ax, u, sd = R.frame(f"hand.{n}")
        c = o + ax*.1
        c = o + ax*.12
        fist = [rock(stone, c, (.16, .15, .17), 200 + s)]
        fist.append(rock(stone, c + ax*.08 + u*.08, (.1, .09, .09), 210 + s))
        fist.append(rock(stone, c - sd*s*.07 + ax*.04, (.07, .07, .08), 220 + s))
        for k in range(2):
            p = c + u*(.05 - .1*k) + sd*s*(.08 + .02*k)
            b = brick(brickm if k else brick2, p, (BR_L*.85, .075, BR_H))
            b.rotation_euler = (ax.to_track_quat('Z', 'Y') @ Quaternion((0, 0, 1), .6 + k)).to_euler(); fist.append(b)
        fist.append(rock(mortar, c - ax*.04, (.1, .1, .07), 230 + s, flat=False))
        R.rigid(fist, f"hand.{n}")
        fa, wr = P(f"forearm.{n}"), P(f"hand.{n}"); d = (wr - fa).normalized()
        cuff = prim("primitive_cylinder_add", iron, fa.lerp(wr, .82), (.105, .105, .055), vertices=12)
        cuff.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
        rivets = []
        for k in range(5):
            a = 2*math.pi*k/5; v = d.to_track_quat('Z', 'Y') @ Vector((math.cos(a), math.sin(a), 0))
            rivets.append(prim("primitive_uv_sphere_add", iron, fa.lerp(wr, .82) + v*.105, (.016,)*3, segments=6, ring_count=4))
        cr = [rock(stone, fa.lerp(wr, .4) + Vector((.06*s, -.07, 0)), .05, 240 + s),
              rock(stone, fa.lerp(wr, .55) + Vector((.08*s, .04, 0)), .045, 250 + s)]
        R.rigid([cuff] + rivets + cr, f"forearm.{n}")
        a, b = P(f"chain.{n}"), P(f"chain.{n}", 1)
        lk = chain(iron, [a, a.lerp(b, .5) + Vector((.02*s, 0, 0)), b], .026, .008)
        lk.append(prim("primitive_torus_add", iron, b, (1, 1, 1), major_radius=.04, minor_radius=.012,
                       major_segments=10, minor_segments=4, rot=(90, 0, 0)))  # elo partido maior na ponta
        R.rigid(lk, f"chain.{n}")
    # cruz do rosário
    a, b = P("rosary"), P("rosary", 1)
    ro = chain(iron, [a, a.lerp(b, .55)], .014, .005)
    cc = a.lerp(b, .8)
    ro.append(prim("primitive_cube_add", iron, cc, (.012, .012, .07), smooth=False))
    ro.append(prim("primitive_cube_add", iron, cc + Vector((0, 0, .025)), (.045, .012, .012), smooth=False))
    R.rigid(ro, "rosary")

    # ------------------------------------------------ crosta de pedra (prece), escondida por escala
    for k, (c, par) in CRUST.items():
        c = Vector(c); parts = []
        rr = random.Random(sum(map(ord, k)))
        nn = 3 if k == "crust.head" else 5
        for i in range(nn):
            off = Vector((rr.uniform(-.07, .07), rr.uniform(-.04, .04), rr.uniform(-.07, .07)))
            sz = (rr.uniform(.05, .08), rr.uniform(.04, .06), rr.uniform(.05, .08))
            parts.append(rock(stone, c + off, sz, 300 + i + len(k)))
        R.rigid(parts, k)

    # ------------------------------------------------ parede (pedaços com reboco atrás)
    for b, (i, cx, cz) in WALL.items():
        parts = []
        for (x, z, w, rr) in CHUNKS[i]:
            m = brick2 if rr.random() < .35 else brickm
            jit = Vector((0, rr.uniform(-.008, .008), 0))
            parts.append(brick(m, Vector((x, WALL_Y0 - .02 - (WALL_D - .03)/2, z)) + jit, (w, WALL_D - .03, BR_H)))
            parts.append(prim("primitive_cube_add", mortar, (x, WALL_Y0 - WALL_D/2, z), (w/2 + GAP*.6, WALL_D/2 - .025, BR_H/2 + GAP*.6), smooth=False))
            if rr.random() < .12:
                parts.append(rock(stone, Vector((x, WALL_Y0 - WALL_D + .02, z)), .03, int(rr.random()*1000)))
        R.rigid(parts, b)

    R.arm.scale = [SCALE]*3
    return R, INFO

# ======================================================================= animações
BASE = {"spine": {"x": 12}, "chest": {"x": 16}, "neck": {"x": -10}, "head": {"x": -14},
        "thigh.L": {"x": -10, "y": -4}, "thigh.R": {"x": -8, "y": 4}, "shin.L": {"bend": 18}, "shin.R": {"bend": 16},
        "foot.L": {"x": -8}, "foot.R": {"x": -8},
        "upper_arm.L": {"y": 22, "x": -14}, "upper_arm.R": {"y": -22, "x": -14},
        "forearm.L": {"bend": -22}, "forearm.R": {"bend": -22}, "hand.L": {}, "hand.R": {}}

def M(*p): return merge({k: dict(v) for k, v in BASE.items()}, *p)

DOWN = (0, 0, -1)
def finish(frames, wall=None, crust=0.001, hang=None):
    """Completa cada quadro: correntes e rosário pendurados (aim), parede e crosta escondidas por escala."""
    out = []
    for i, p in enumerate(frames):
        p = dict(p)
        aim = {"chain.L": DOWN, "chain.R": DOWN, "rosary": (0, -.25, -1)}
        if hang: aim.update(hang(i))
        aim.update(p.get("aim") or {}); p["aim"] = aim
        sc = {b: .001 for b in WALLB}
        c = crust(i) if callable(crust) else crust
        sc.update({b: c for b in CRUST})
        if wall: sc.update({b: 1 for b in WALLB}); p.update(wall(i))
        sc.update(p.get("scale") or {}); p["scale"] = sc
        out.append(p)
    return out

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; b, c = math.sin(t), math.cos(t)
        idle.append(M({"chest": {"x": 3*b}, "spine": {"x": 1*b}, "head": {"x": -3*b, "z": 5*math.sin(t*.5)},
                       "upper_arm.L": {"y": -2*b, "x": 2*c}, "upper_arm.R": {"y": 2*b, "x": -2*c},
                       "forearm.L": {"bend": -3*b}, "forearm.R": {"bend": -3*b}}))
    # andar pesado: passos curtos, o corpo tomba de um lado para o outro, punhos balançando
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 20*s
        walk.append(M({"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                       "shin.L": {"bend": 6 + 38*max(0, c)**1.3}, "shin.R": {"bend": 6 + 38*max(0, -c)**1.3},
                       "foot.L": {"x": .3*th - 10*max(0, c)}, "foot.R": {"x": -.3*th - 10*max(0, -c)},
                       "hips": {"z": 6*s, "y": 5*c}, "spine": {"y": -3*c}, "chest": {"z": -10*s, "y": -6*c},
                       "head": {"z": 8*s, "y": 5*c}, "upper_arm.L": {"x": 14*s, "y": 3*c}, "upper_arm.R": {"x": -14*s, "y": 3*c},
                       "forearm.L": {"bend": -10*max(0, s)}, "forearm.R": {"bend": -10*max(0, -s)}}))
    # punho de pedra: ergue o punho direito acima da cabeça (preparo longo) e martela para a frente e para baixo
    up = M({"upper_arm.R": {"x": -160, "y": 30}, "forearm.R": {"bend": -70}, "hand.R": {"x": -20},
            "upper_arm.L": {"x": 20, "y": -6}, "forearm.L": {"bend": -30},
            "spine": {"x": -10, "z": -8}, "chest": {"x": -14, "z": -22}, "neck": {"x": 6}, "head": {"x": 8, "z": 14},
            "thigh.L": {"x": -18}, "shin.L": {"bend": 10}, "thigh.R": {"x": 8}, "root": (0, .06, 0)})
    up2 = merge(up, {"upper_arm.R": {"x": -8}, "chest": {"x": -4, "z": -4}})
    slam = M({"upper_arm.R": {"x": -40, "y": 8, "z": 10}, "forearm.R": {"bend": -4}, "hand.R": {"x": 10},
              "upper_arm.L": {"x": -10, "y": -10}, "forearm.L": {"bend": -40},
              "spine": {"x": 22, "z": 6}, "chest": {"x": 26, "z": 18}, "neck": {"x": -10}, "head": {"x": -16, "z": -6},
              "thigh.L": {"x": -46}, "shin.L": {"bend": 40}, "thigh.R": {"x": 22}, "shin.R": {"bend": 10}, "foot.R": {"x": -12},
              "root": (0, -.2, 0)})
    slam2 = merge(slam, {"upper_arm.R": {"x": 8}, "chest": {"x": 4}, "spine": {"x": 2}, "root": (0, -.22, 0)})
    attack = keys_to_frames([(0, M()), (.25, up), (.48, up2), (.6, slam), (.74, slam2), (1, M())], 12)

    # emboscada: encolhido atrás da parede, os tijolos tremem, recua e rompe a parede com os dois punhos
    crouch = M({"root": (0, .46, 0), "thigh.L": {"x": -80}, "thigh.R": {"x": -76}, "shin.L": {"bend": 115}, "shin.R": {"bend": 112},
                "foot.L": {"x": 10}, "foot.R": {"x": 10}, "spine": {"x": 22}, "chest": {"x": 24}, "neck": {"x": -16}, "head": {"x": -18},
                "upper_arm.L": {"x": -40, "y": -6}, "upper_arm.R": {"x": -40, "y": 6}, "forearm.L": {"bend": -70}, "forearm.R": {"bend": -70}})
    coil = merge(crouch, {"root": (0, .52, 0), "spine": {"x": 6}, "chest": {"x": 6}, "upper_arm.L": {"x": 40}, "upper_arm.R": {"x": 40},
                          "forearm.L": {"bend": -30}, "forearm.R": {"bend": -30}, "head": {"x": 8}})
    burst = M({"root": (0, .16, 0), "thigh.L": {"x": -55}, "thigh.R": {"x": 10}, "shin.L": {"bend": 50}, "shin.R": {"bend": 30},
               "foot.R": {"x": -20}, "spine": {"x": 18}, "chest": {"x": 18}, "neck": {"x": -10}, "head": {"x": -14},
               "upper_arm.L": {"x": -88, "y": -12}, "upper_arm.R": {"x": -88, "y": 12}, "forearm.L": {"bend": -8}, "forearm.R": {"bend": -8}})
    through = M({"root": (0, -.04, 0), "thigh.L": {"x": -40}, "thigh.R": {"x": 16}, "shin.L": {"bend": 34}, "shin.R": {"bend": 18},
                 "spine": {"x": 6}, "chest": {"x": 0}, "neck": {"x": -4}, "head": {"x": 4},
                 "upper_arm.L": {"x": -70, "y": 40}, "upper_arm.R": {"x": -70, "y": -40}, "forearm.L": {"bend": -30}, "forearm.R": {"bend": -30}})
    roar = M({"root": (0, -.02, 0), "thigh.L": {"x": -22}, "thigh.R": {"x": 6}, "shin.L": {"bend": 24},
              "spine": {"x": -8}, "chest": {"x": -12}, "neck": {"x": 4}, "head": {"x": 12},
              "upper_arm.L": {"x": -30, "y": 36}, "upper_arm.R": {"x": -30, "y": -36}, "forearm.L": {"bend": -60}, "forearm.R": {"bend": -60}})
    body = keys_to_frames([(0, crouch), (.16, merge(crouch, {"head": {"x": 6}, "chest": {"x": -2}})), (.3, coil), (.4, burst),
                           (.55, through), (.72, roar), (1, M())], 16)
    rw = random.Random(17)
    times = {}
    for b, (i, cx, cz) in WALL.items():
        t0 = .34 + .04*abs(cx)/.68 + .05*abs(cz - .75) + rw.uniform(0, .05)
        times[b] = (t0, rw.uniform(.2, .3), rw.uniform(-18, 18), rw.uniform(-4, 4))
    def wall(i):
        t = i/15; p = {}
        for b, (t0, dur, zr, sh) in times.items():
            if t < t0:
                k = 2.5*math.sin(i*2.1 + t0*40) if .1 < t < t0 else 0  # tremor antes de romper
                p[b] = {"x": k*.6}
            else:
                u = min(1, (t - t0)/dur); u = 1 - (1 - u)**1.6
                p[b] = {"x": 180*u, "z": zr*u}
        return p
    ambush = finish(body, wall=wall)

    # prece de pedra: ajoelha, junta os punhos diante do rosto e a crosta de pedra cresce
    kneel = M({"thigh.L": {"x": -8}, "thigh.R": {"x": -4}, "shin.L": {"bend": 88}, "shin.R": {"bend": 92},
               "foot.L": {"x": 30}, "foot.R": {"x": 30}, "spine": {"x": 4}, "chest": {"x": 6}, "neck": {"x": 14}, "head": {"x": 22},
               "upper_arm.L": {"x": -60, "y": 6, "z": -30}, "upper_arm.R": {"x": -60, "y": -6, "z": 30},
               "forearm.L": {"bend": -105}, "forearm.R": {"bend": -105}, "hand.L": {"x": 10}, "hand.R": {"x": 10}})
    sink = M({"thigh.L": {"x": -50}, "thigh.R": {"x": -40}, "shin.L": {"bend": 80}, "shin.R": {"bend": 70},
              "spine": {"x": 14}, "chest": {"x": 10}, "head": {"x": 10}, "upper_arm.L": {"x": -20}, "upper_arm.R": {"x": -20},
              "forearm.L": {"bend": -50}, "forearm.R": {"bend": -50}})
    tight = merge(kneel, {"head": {"x": 6}, "chest": {"x": 4}, "forearm.L": {"bend": -5}, "forearm.R": {"bend": -5}})
    pbody = keys_to_frames([(0, M()), (.22, sink), (.4, kneel), (.62, tight), (.8, kneel), (1, tight)], 12)
    pray = finish(pbody, crust=lambda i: max(.001, min(1, (i - 4)/5)))

    # QUEBRADO (loop): cambaleia exposto, cabeça pendida, braços soltos, joelhos cedendo
    broken = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t)
        broken.append(M({"spine": {"x": 14, "y": 6*s}, "chest": {"x": 16, "y": 10*s, "z": 6*c}, "neck": {"x": 12},
                         "head": {"x": 26, "z": 18*s, "y": -10*s},
                         "hips": {"y": -5*s, "z": 4*c}, "root": (.07*s, .02*c, 0),
                         "thigh.L": {"x": -18 - 8*max(0, s), "y": -4}, "thigh.R": {"x": -18 - 8*max(0, -s), "y": 4},
                         "shin.L": {"bend": 34 + 14*max(0, s)}, "shin.R": {"bend": 34 + 14*max(0, -s)},
                         "upper_arm.L": {"y": 14 + 8*s, "x": 18 + 6*c}, "upper_arm.R": {"y": -14 + 8*s, "x": 18 - 6*c},
                         "forearm.L": {"bend": -6}, "forearm.R": {"bend": -6}}))
    hitp = M({"chest": {"x": -18, "z": 8}, "spine": {"x": -8}, "head": {"x": -20, "z": 12}, "upper_arm.L": {"x": 22, "y": -6},
              "upper_arm.R": {"x": 26, "y": 8}, "forearm.L": {"bend": -40}, "forearm.R": {"bend": -30}, "root": (0, .08, 0)})
    hit = [lerp_pose(M(), hitp, .6), hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: cai de joelhos, tomba para a frente sobre os punhos e desaba de cara no chão
    dk = M({"thigh.L": {"x": -60}, "thigh.R": {"x": -50}, "shin.L": {"bend": 100}, "shin.R": {"bend": 108},
            "foot.L": {"x": 10}, "foot.R": {"x": 10}, "chest": {"x": 10}, "head": {"x": 20, "z": 14},
            "upper_arm.L": {"y": 8, "x": 12}, "upper_arm.R": {"y": -8, "x": 12}})
    lean = merge(dk, {"hips": {"x": 42}, "spine": {"x": 10}, "upper_arm.L": {"x": -55}, "upper_arm.R": {"x": -50},
                      "forearm.L": {"bend": -10}, "forearm.R": {"bend": -10}, "ground": .1})
    prone = {"hips": {"x": 86, "z": 6}, "spine": {"x": 2}, "chest": {"x": -2}, "neck": {"x": -6}, "head": {"z": 50, "x": -6},
             "upper_arm.L": {"x": -140, "y": 52}, "upper_arm.R": {"x": -100, "y": -66},
             "forearm.L": {"bend": -30}, "forearm.R": {"bend": -40},
             "thigh.L": {"x": 4, "y": -8}, "thigh.R": {"x": -4, "y": 10}, "shin.L": {"bend": 20}, "shin.R": {"bend": 8},
             "foot.L": {"x": 40}, "foot.R": {"x": 30}, "ground": .05}
    death = keys_to_frames([(0, hitp), (.28, dk), (.5, lean), (.75, prone), (.87, merge(prone, {"chest": {"x": -4}, "head": {"x": -4}})),
                            (1, prone)], 11)
    lie = lambda i: {"chain.L": (0, -1, -.3), "chain.R": (0, -1, -.3), "rosary": (0, -1, -.5)} if i >= 7 else {}
    return {"idle": finish(idle), "walk": finish(walk), "attack": finish(attack), "ambush": ambush, "pray": pray,
            "broken": finish(broken), "hit": finish(hit), "death": finish(death, hang=lie)}
