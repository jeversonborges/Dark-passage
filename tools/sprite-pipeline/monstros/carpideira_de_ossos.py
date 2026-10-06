# Carpideira de Ossos (Cripta da Trombeta Calada, andar 2: Ossário das Carpideiras). Uma das mulheres
# pagas para chorar nos enterros de São Lázaro, que desceu com a Irmã Celeste para cantar aos mortos e
# virou ossada viva. Longa e curvada, flutua com a barra do vestido de luto arrastando no chão; véu negro
# rasgado sobre o crânio, máscara de ossos (dedos em leque como uma coroa) escondendo o rosto, mandíbula
# solta embaixo, costelas à mostra pelo xale aberto, mangas de sino, mãos longas de osso, relicário-turíbulo
# de latão e osso pendurado por corrente na mão esquerda.
# Brilho: frio e fraco (olhos da máscara, lágrimas negras com brilho, fogo-fátuo dentro do relicário).
# Conjuradora de suporte: attack (lágrima negra, arremesso), lament (lamento em cone: abre os braços e grita),
# heal (consolo: mãos juntas, loop curto de conjuração), death (desmorona em ossos e pano).
# Esqueleto próprio, sem pernas: o vestido tem 6 painéis de 2 ossos ("sk*") que arrastam, ondulam e se abrem
# no chão na morte (por "aim"). Voa sempre ("ground": None); na morte settle() mede a pose e baixa o root até tocar o chão.
# Variante elite carpideira_de_ossos_viuva: véu vermelho-escuro, 12% mais alta, relicário maior, coroa mais alta.
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *

INFO = {"px": 224, "target_z": 1.0, "rim": (.55, .68, .9), "colors": 44, "samples": 40,
        "loops": ("idle", "walk", "heal"),
        "fps": {"idle": 6, "walk": 8, "attack": 12, "lament": 10, "heal": 8, "hit": 12, "death": 10}}

VARIANTS = {
    "carpideira_de_ossos": {},
    "carpideira_de_ossos_viuva": {"veil": (.075, .011, .013), "scale": 1.12, "rel": 1.45, "crown": 1.35, "rim": (.7, .6, .8)},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
    INFO["rim"] = V.get("rim", (.55, .68, .9))
set_variant("carpideira_de_ossos")

# ------------------------------------------------------------------ esqueleto
BONES = {
 "hips":  ((0, 0, 1.0), (0, 0, 1.12), None),
 "spine": ((0, 0, 1.12), (0, .01, 1.34), "hips"),
 "chest": ((0, .01, 1.34), (0, 0, 1.58), "spine"),
 "neck":  ((0, 0, 1.58), (0, -.02, 1.7), "chest"),
 "head":  ((0, -.02, 1.7), (0, -.03, 1.95), "neck"),
 "jaw":   ((0, -.03, 1.76), (0, -.12, 1.7), "head"),
 "veil1": ((0, .12, 1.74), (0, .22, 1.36), "head"),
 "veil2": ((0, .22, 1.36), (0, .3, .95), "veil1"),
}
for s, n in ((1, "L"), (-1, "R")):
    BONES.update({
     f"upper_arm.{n}": ((.17*s, 0, 1.54), (.4*s, 0, 1.3), "chest"),
     f"forearm.{n}":   ((.4*s, 0, 1.3), (.63*s, -.01, 1.07), f"upper_arm.{n}"),
     f"hand.{n}":      ((.63*s, -.01, 1.07), (.73*s, -.02, .96), f"forearm.{n}"),
    })
BONES["censer"] = ((.73, -.02, .96), (.73, -.02, .56), "hand.L")
NP = 6
PANELS = []
for _k in range(NP):
    _a = math.radians(-90 + 60*_k); _c, _s = math.cos(_a), math.sin(_a); _tr = max(0, _s)
    _t = Vector((.13*_c, .11*_s, .98)); _m = Vector((.25*_c, .22*_s + .12*_tr, .5)); _h = Vector((.33*_c, .3*_s + .3*_tr, .03))
    BONES[f"sk{_k}.a"] = (tuple(_t), tuple(_m), "hips")
    BONES[f"sk{_k}.b"] = (tuple(_m), tuple(_h), f"sk{_k}.a")
    PANELS.append((_a, f"sk{_k}.a", f"sk{_k}.b"))
SKB = [p[1] for p in PANELS] + [p[2] for p in PANELS]

def tube(name, m, centers, radii, seg=24, jag=0, seed=1, holes=0, open_front=0, offs=None, thick=.01, ref=Vector((0, 1, 0))):
    """Tubo de pano ao longo de uma polilinha (saia, manga, xale). radii: [(rx, ry)]; offs(a, t) -> Vector extra.
    holes: chance de rasgo nas fileiras de baixo; open_front: meia abertura (rad) na frente (-Y)."""
    rnd = random.Random(seed); bm = bmesh.new(); grid = []; N = len(centers)
    for i, c in enumerate(centers):
        c = Vector(c); d = (Vector(centers[min(i+1, N-1)]) - Vector(centers[max(i-1, 0)])).normalized()
        side = d.cross(ref).normalized(); up = side.cross(d).normalized()
        rx, ry = radii[i]; row = []
        for k in range(seg + 1):
            a = -math.pi/2 + 2*math.pi*k/seg
            p = c + side*rx*math.cos(a) + up*ry*math.sin(a)
            if offs: p = p + offs(a, i/(N-1))
            if i == N-1 and jag: p = p + d*rnd.uniform(-jag*.4, jag)
            row.append(bm.verts.new(p))
        grid.append(row)
    for i in range(N-1):
        for k in range(seg):
            a = -math.pi/2 + 2*math.pi*(k + .5)/seg
            da = abs((a + math.pi/2 + math.pi) % (2*math.pi) - math.pi)
            if open_front and da < open_front*(1 + .25*i/(N-1)): continue
            if holes and i >= N - 3 and rnd.random() < holes*(i - N + 4)/3: continue
            bm.faces.new((grid[i][k], grid[i][k+1], grid[i+1][k+1], grid[i+1][k]))
    o = obj_from_bm(name, bm, m)
    if thick: o.modifiers.new("s", 'SOLIDIFY').thickness = thick; apply_mods(o)
    return o

def build():
    rnd = random.Random(31)
    E = V["name"].endswith("viuva")
    bone = stained("cp_osso", (.55, .51, .42), stain=(.1, .09, .07), amount=.45, scale=6, rough=.55,
                   blotch=(.2, .18, .14), blotch_amt=.6, grime=.5)
    oldb = stained("cp_osso_velho", (.38, .34, .27), stain=(.06, .05, .04), amount=.5, scale=8, rough=.6, grime=.3)
    vc = V.get("veil", (.032, .03, .038))
    veil = stained("cp_veu", vc, stain=(.06, .055, .06), amount=.35, scale=3, rough=.55,
                   blotch=tuple(c*.6 for c in vc), blotch_amt=.6, grime=.6)
    dress = stained("cp_vestido", (.055, .05, .055), stain=(.11, .1, .095), amount=.45, scale=2.5, rough=.9,
                    blotch=(.02, .018, .02), blotch_amt=.6, grime=1.4)
    lace = stained("cp_renda", (.06, .055, .06), stain=(.12, .11, .1), amount=.5, scale=6, rough=.8, grime=.5)
    brass = stained("cp_latao", (.3, .2, .08), stain=(.06, .08, .05), amount=.5, scale=7, metal=1, rough=.45, grime=.3)
    iron = stained("cp_ferro", (.07, .06, .055), stain=(.22, .09, .04), amount=.55, scale=7, metal=.8, rough=.55, grime=.3)
    hole = mat("cp_buraco", (.004, .004, .006), 0, .95)
    eye = mat("cp_olho", (.7, .85, 1), emit=(.5, .75, 1), strength=20)
    tear = mat("cp_lagrima", (.01, .012, .016), emit=(.3, .5, .8), strength=1.6)
    wisp = mat("cp_fatuo", (.6, .8, 1), emit=(.45, .7, 1), strength=7)

    R = Rig(V["name"], BONES, ground=None); P = R.P
    R.gexclude = {"censer", "veil1", "veil2"}

    # ------------------------------------------------ vestido de luto em camadas, cauda arrastando atrás
    def train(a, t):
        s = math.sin(a); return Vector((0, .32*max(0, s)*t**1.5, 0))
    zs = [1.04, .86, .66, .46, .26, .03]
    rr_ = [(.13, .11), (.18, .155), (.22, .19), (.26, .23), (.3, .27), (.35, .32)]
    sk = tube("vestido", dress, [(0, 0, z) for z in zs], rr_, seg=32, jag=.07, seed=3, holes=.05, offs=train, thick=.012)
    R.bind(sk, ["hips"] + SKB, power=4)
    over = tube("sobressaia", veil, [(0, -.005, z) for z in (1.06, .9, .7, .5)], [(.15, .13), (.21, .18), (.25, .22), (.29, .26)],
                seg=28, jag=.18, seed=8, holes=.12, open_front=.5, offs=lambda a, t: train(a, t*.6), thick=.01)
    R.bind(over, ["hips"] + SKB, power=4)

    # ------------------------------------------------ tronco de ossos: coluna, costelas, clavículas, pelve
    def vert(bn, n, r):
        a, b = P(bn), P(bn, 1); out = []
        for k in range(n):
            c = a.lerp(b, (k + .5)/n) + Vector((0, .05, 0))
            out.append(prim("primitive_uv_sphere_add", bone, c, (r, r*.9, r*.75), segments=8, ring_count=6))
            out.append(along("primitive_cone_add", oldb, c, c + Vector((0, .04, -.01)), r*.5, vertices=4, radius1=1, radius2=0))
        return out
    sp = vert("spine", 4, .03)
    sp.append(prim("primitive_uv_sphere_add", bone, (0, .02, 1.05), (.13, .08, .06), segments=12, ring_count=6))  # pelve
    R.rigid(sp, "spine")
    cp = vert("chest", 4, .028)
    for i, z in enumerate((1.52, 1.47, 1.42, 1.37, 1.32, 1.27)):
        w = .125 - abs(i - 1.5)*.008
        for s in (1, -1):
            pts = [Vector((s*w*math.sin(a)*1.05, .06 - (.095 + .012*math.cos(a))*math.cos(a) - .03*(1 - math.cos(a)), z - .03*math.sin(a)))
                   for a in (0.05, .5, 1.0, 1.45, 1.9, 2.4)]
            if i >= 4: pts = pts[1:]
            for a_, b_ in zip(pts, pts[1:]):
                cp.append(along("primitive_cylinder_add", bone, a_, b_, .011, vertices=6))
    cp.append(along("primitive_cube_add", bone, (0, -.11, 1.52), (0, -.105, 1.33), .016))  # esterno
    for s in (1, -1):
        cp.append(along("primitive_cylinder_add", bone, (.02*s, -.06, 1.56), (.17*s, -.0, 1.56), .013, vertices=6))
    # xale de véu aberto na frente (costelas à mostra), franja rasgada
    shawl = tube("xale", veil, [(0, .01, z) for z in (1.62, 1.55, 1.45, 1.36)], [(.09, .08), (.2, .15), (.2, .155), (.18, .15)],
                 seg=26, jag=.07, seed=5, holes=.2, open_front=1.0, thick=.008)
    R.rigid([shawl] + cp, "chest")
    # cinto de vértebras com relíquias penduradas (falanges e um crânio pequeno)
    bt = []
    for k in range(22):
        a = 2*math.pi*k/22
        bt.append(prim("primitive_uv_sphere_add", bone if k % 2 else oldb, (.145*math.cos(a), .125*math.sin(a), 1.02),
                       (.018, .018, .014), segments=6, ring_count=4))
    for k, a in enumerate((-2.0, -1.2, -.6)):
        top = Vector((.15*math.cos(a), .13*math.sin(a) - .01, 1.01)); bot = top + Vector((0, -.02, -.12 - .05*k))
        bt += [along("primitive_cylinder_add", iron, top, bot, .004, vertices=4),
               along("primitive_cylinder_add", bone, bot, bot + Vector((0, 0, -.06)), .009, vertices=5)]
    sk0 = Vector((-.13, -.08, .86))
    bt.append(along("primitive_cylinder_add", iron, Vector((-.14, -.07, 1.01)), sk0 + Vector((0, 0, .045)), .004, vertices=4))
    bt.append(prim("primitive_uv_sphere_add", bone, sk0, (.04, .045, .045), segments=10, ring_count=6))
    for s in (1, -1):
        bt.append(prim("primitive_uv_sphere_add", hole, sk0 + Vector((.015*s, -.038, .005)), (.011, .006, .01), segments=6, ring_count=4))
    R.rigid(bt, "hips")

    # ------------------------------------------------ braços: úmero/rádio, mangas de sino, mãos longas de osso
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        ua = [along("primitive_cylinder_add", bone, sh, el, .019, vertices=8),
              prim("primitive_uv_sphere_add", bone, sh, (.035,)*3, segments=8, ring_count=6),
              prim("primitive_uv_sphere_add", bone, el, (.028,)*3, segments=8, ring_count=6)]
        d = (el - sh).normalized()
        slv = tube(f"manga.{n}", veil, [sh - d*.02, sh.lerp(el, .5), el, el + (wr - el)*.45],
                   [(.06, .06), (.075, .07), (.1, .09), (.15, .13)], seg=18, jag=.14, seed=10 + s, holes=.3, thick=.008)
        R.bind(slv, ["chest", f"upper_arm.{n}", f"forearm.{n}"], power=4)
        R.rigid(ua, f"upper_arm.{n}")
        fa = [along("primitive_cylinder_add", bone, el + Vector((0, .012, 0)), wr + Vector((0, .012, 0)), .012, vertices=6),
              along("primitive_cylinder_add", bone, el + Vector((0, -.012, 0)), wr + Vector((0, -.012, 0)), .01, vertices=6)]
        R.rigid(fa, f"forearm.{n}")
        o, ax, u, sd = R.frame(f"hand.{n}")
        hp = [prim("primitive_uv_sphere_add", bone, o + ax*.03, (.03, .02, .035), segments=8, ring_count=6)]
        curl = .55 if n == "L" else .25
        for f in range(4):  # dedos longos, 3 falanges
            base = o + ax*.05 + sd*(-.03 + .02*f); dd = (ax + sd*(f - 1.5)*.08).normalized(); L = .065 - .008*abs(f - 1.5)
            pts = [base]
            for k in range(3):
                dd = (Quaternion(sd, -curl*(k + 1)*.5) @ dd).normalized()
                pts.append(pts[-1] + dd*L*(1 - .2*k))
            for a_, b_ in zip(pts, pts[1:]):
                hp.append(along("primitive_cylinder_add", bone, a_, b_, .0075, vertices=5))
                hp.append(prim("primitive_uv_sphere_add", oldb, b_, (.009,)*3, segments=5, ring_count=4))
        th = o + ax*.02 - sd*s*.035
        hp.append(along("primitive_cylinder_add", bone, th, th + ax*.06 - sd*s*.03 + u*.02, .008, vertices=5))
        R.rigid(hp, f"hand.{n}")

    # ------------------------------------------------ cabeça: crânio sob o véu, máscara de ossos em leque, mandíbula
    hd = []
    hc = Vector((0, -.03, 1.82))
    hd.append(prim("primitive_uv_sphere_add", bone, hc, (.085, .1, .1), segments=14, ring_count=9))
    mc = hc + Vector((0, -.088, -.005))
    mask = prim("primitive_uv_sphere_add", oldb, mc, (.08, .03, .1), segments=14, ring_count=9); hd.append(mask)
    for s in (1, -1):  # órbitas, olhos frios e lágrimas negras escorrendo
        hd.append(prim("primitive_uv_sphere_add", hole, mc + Vector((.032*s, -.026, .02)), (.022, .012, .016), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", eye, mc + Vector((.032*s, -.032, .02)), (.009, .005, .008), segments=8, ring_count=6))
        p0 = mc + Vector((.034*s, -.031, .003)); p1 = mc + Vector((.03*s, -.03, -.07)); p2 = mc + Vector((.036*s, -.012, -.12))
        hd.append(along("primitive_cylinder_add", tear, p0, p1, .0055, vertices=5))
        hd.append(along("primitive_cylinder_add", tear, p1, p2, .0045, vertices=5))
        hd.append(prim("primitive_uv_sphere_add", tear, p2 + Vector((0, 0, -.008)), (.009, .009, .012), segments=6, ring_count=4))
    hd.append(along("primitive_cylinder_add", hole, mc + Vector((0, -.03, -.03)), mc + Vector((0, -.03, -.06)), .006, vertices=4))
    cr = V.get("crown", 1.0)
    for k in range(11):  # coroa de falanges em leque em volta da máscara (atravessa o véu)
        a = math.radians(-75 + 150*k/10)
        dv = Vector((math.sin(a), -.25, math.cos(a))).normalized()
        b0 = mc + Vector((.07*math.sin(a), .0, .085*math.cos(a)))
        L = (.16 + .08*(1 - abs(a)/1.3))*cr
        b1 = b0 + dv*L*.55; b2 = b0 + dv*L
        hd.append(along("primitive_cylinder_add", bone if k % 2 else oldb, b0, b1, .012, vertices=5))
        hd.append(along("primitive_cone_add", bone, b1, b2, .011, vertices=5, radius1=1, radius2=.3))
        hd.append(prim("primitive_uv_sphere_add", oldb, b1, (.011,)*3, segments=5, ring_count=4))
    hd.append(prim("primitive_torus_add", iron, mc + Vector((0, .02, .0)), (1, .55, 1.25), major_radius=.085, minor_radius=.006,
                   major_segments=18, minor_segments=4, rot=(90, 0, 0)))
    # véu: capuz sobre o crânio (aberto na frente) que cai como cortina pelas costas
    bm = bmesh.new(); rows, cols = 13, 15; g = []
    vr = random.Random(77)
    for r in range(rows):
        t = r/(rows - 1); row = []
        z = 1.97 - .78*t*(1 + .1*E)
        rad = .06 + .065*min(1, t/.12) + .17*max(0, t - .12)
        yc = -.035 + .3*max(0, t - .1)**1.3
        for c in range(cols):
            u = c/(cols - 1); ang = math.radians(-108 + 216*u)
            if t < .02: rad0 = .03
            row.append(bm.verts.new((rad*math.sin(ang), yc + rad*math.cos(ang)*(1.15 if t < .14 else 1), z + (vr.uniform(-.09, .03) if r == rows-1 else 0))))
        g.append(row)
    for r in range(rows - 1):
        for c in range(cols - 1):
            if r >= rows - 4 and vr.random() < .1 + .1*(r - rows + 4): continue
            if 3 < r < rows - 4 and vr.random() < .07: continue
            bm.faces.new((g[r][c], g[r][c+1], g[r+1][c+1], g[r+1][c]))
    vl = obj_from_bm("veu", bm, veil); vl.modifiers.new("s", 'SOLIDIFY').thickness = .008; apply_mods(vl)
    R.rigid(hd, "head")
    R.bind(vl, ["head", "veil1", "veil2"], power=4)
    jw = [prim("primitive_uv_sphere_add", bone, (0, -.09, 1.73), (.06, .045, .022), segments=10, ring_count=6)]
    for k in range(7):
        x = -.033 + .011*k
        jw.append(along("primitive_cone_add", oldb, (x, -.122 + abs(x)*.5, 1.735), (x, -.122 + abs(x)*.5, 1.755), .006, vertices=4, radius1=1, radius2=.2))
    R.rigid(jw, "jaw")

    # ------------------------------------------------ relicário-turíbulo de latão e osso, preso por corrente
    rs = V.get("rel", 1.0)
    a, b = P("censer"), P("censer", 1)
    cs = []
    n = 11
    for k in range(n):
        c = a.lerp(b, (k + .5)/n*.82)
        cs.append(prim("primitive_torus_add", iron, c, (1, 1, 1.6), major_radius=.014, minor_radius=.004, major_segments=8,
                       minor_segments=4, rot=(0, 0, 90*(k % 2))))
        cs[-1].rotation_euler = (0, math.radians(90), math.radians(90*(k % 2)))
    cc = b + Vector((0, 0, .02*rs))
    top = cc + Vector((0, 0, .1*rs))
    cs.append(along("primitive_cone_add", brass, top, top + Vector((0, 0, .07*rs)), .07*rs, vertices=10, radius1=1, radius2=.15))
    cs.append(prim("primitive_cylinder_add", brass, top, (.075*rs, .075*rs, .01*rs), vertices=12))
    cs.append(prim("primitive_cylinder_add", brass, cc - Vector((0, 0, .1*rs)), (.08*rs, .08*rs, .012*rs), vertices=12))
    bowl = prim("primitive_uv_sphere_add", brass, cc - Vector((0, 0, .1*rs)), (.08*rs, .08*rs, .06*rs), segments=12, ring_count=8)
    cs.append(bowl)
    for k in range(8):  # gaiola de costelas
        ang = 2*math.pi*k/8; v = Vector((math.cos(ang), math.sin(ang), 0))
        p0 = cc + v*.075*rs - Vector((0, 0, .1*rs)); p1 = cc + v*.095*rs; p2 = top + v*.07*rs
        cs.append(along("primitive_cylinder_add", bone, p0, p1, .007*rs, vertices=5))
        cs.append(along("primitive_cylinder_add", bone, p1, p2, .007*rs, vertices=5))
    cs.append(prim("primitive_uv_sphere_add", oldb, cc - Vector((0, 0, .025*rs)), (.042*rs, .048*rs, .045*rs), segments=10, ring_count=6))
    for s in (1, -1):
        cs.append(prim("primitive_uv_sphere_add", wisp, cc + Vector((.015*s*rs, -.04*rs, -.02*rs)), (.009*rs,)*3, segments=6, ring_count=4))
    cs.append(prim("primitive_uv_sphere_add", wisp, cc + Vector((0, 0, .05*rs)), (.022*rs,)*3, segments=8, ring_count=5))
    tp = top + Vector((0, 0, .07*rs))
    cs.append(along("primitive_cylinder_add", bone, tp, tp + Vector((0, 0, .08*rs)), .007*rs, vertices=5))
    cs.append(along("primitive_cylinder_add", bone, tp + Vector((-.03*rs, 0, .055*rs)), tp + Vector((.03*rs, 0, .055*rs)), .006*rs, vertices=5))
    for k in range(3):  # fitas pretas de luto penduradas
        ang = 2*math.pi*k/3 + .4; v = Vector((math.cos(ang), math.sin(ang), 0))
        p = cc - Vector((0, 0, .14*rs)) + v*.04*rs
        cs.append(along("primitive_cube_add", lace, p, p + v*.03 + Vector((0, 0, -.15 - .05*k)), .006))
    R.rigid(cs, "censer")
    R.arm.scale = [1.06*V.get("scale", 1)]*3
    return R, INFO

# ======================================================================= animações
G = {"ground": None}
BASE = {"spine": {"x": 10}, "chest": {"x": 14}, "neck": {"x": 2}, "head": {"x": -8},
        "upper_arm.L": {"y": 30, "x": -14}, "upper_arm.R": {"y": -32, "x": -10},
        "forearm.L": {"bend": -30}, "forearm.R": {"bend": -22}, "hand.L": {"x": -10}, "hand.R": {"x": 10}}
AIM0 = {"veil1": (0, .3, -1), "veil2": (0, .22, -1), "censer": (0, 0, -1)}

def M(*p): return merge(G, {k: dict(v) for k, v in BASE.items()}, *p)

def skirt_wave(ph, amp=1.0, trail=0.0):
    """Painéis do vestido: ondulam com fase ph (rad) e se inclinam para trás (trail, graus)."""
    out = {}
    for k, (a, ba, bb) in enumerate(PANELS):
        w = math.sin(ph + k*1.05)
        back = max(0, math.sin(a))  # os de trás arrastam mais
        out[ba] = {"x": trail*(.6 + .4*back) + 3*amp*w, "y": 2*amp*math.cos(ph + k)}
        out[bb] = {"x": trail*(.4 + .8*back) + 5*amp*math.sin(ph + k*1.05 - .8)}
    return out

def settle(R, frames, floor=.03):
    """Trava no chão feita antes das ações: posa cada quadro num rascunho, mede o osso mais baixo e corrige o root
    (a trava do mrig falha em quadros travados seguidos depois de quadros sem trava)."""
    for p in frames:
        q = dict(p); q["ground"] = None
        Rig.set_pose(R, q, 1); bpy.context.view_layer.update()
        pb = R.arm.pose.bones
        lo = min(min(b.head.z, b.tail.z) for b in pb)
        r = Vector(p.get("root", (0, 0, 0))); r.z += floor - lo; p["root"] = tuple(r); p["ground"] = None
    ad = R.arm.animation_data
    if ad and ad.action:
        a = ad.action; ad.action = None; bpy.data.actions.remove(a)

def finish(frames, aim=None):
    out = []
    for i, p in enumerate(frames):
        p = dict(p); a = dict(AIM0)
        if aim: a.update(aim(i))
        a.update(p.get("aim") or {}); p["aim"] = a; out.append(p)
    return out

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; b, c = math.sin(t), math.cos(t)
        idle.append(M(skirt_wave(t), {"root": (0, 0, .04 + .035*b), "chest": {"x": -3*b}, "head": {"x": 3*b, "z": 6*math.sin(t*.5 + .5)},
                                      "upper_arm.L": {"y": -2*b}, "upper_arm.R": {"y": 2*b}, "forearm.R": {"bend": -4*c},
                                      "aim": {"censer": (.12*c, .1*b, -1), "veil1": (.04*b, .32, -1), "veil2": (.06*c, .28, -1)}}))
    # deslizar: inclina para a frente, o vestido e o véu arrastam para trás, o relicário balança
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; b, c = math.sin(t), math.cos(t)
        walk.append(M(skirt_wave(t*2, 1.3, 16), {"root": (0, 0, .05 + .03*math.sin(2*t)), "hips": {"x": 6, "z": 4*b},
                                                 "chest": {"x": 6, "z": -6*b}, "head": {"z": 6*b},
                                                 "upper_arm.L": {"x": 10*b}, "upper_arm.R": {"x": -10*b},
                                                 "aim": {"censer": (.05, .35 + .15*c, -1), "veil1": (.05*b, .45, -1), "veil2": (.08*b, .5, -1)}}))
    # lágrima negra: leva a mão direita à máscara (colhe a lágrima), recua e arremessa
    touch = M(skirt_wave(0), {"upper_arm.R": {"x": -95, "y": 18, "z": 30}, "forearm.R": {"bend": -120}, "hand.R": {"x": -20},
                              "chest": {"x": -6, "z": 10}, "head": {"x": 8, "z": -10}, "root": (0, .03, .06)})
    cock = M(skirt_wave(.8), {"upper_arm.R": {"x": -40, "y": 40, "z": -20}, "forearm.R": {"bend": -80}, "hand.R": {"x": -30},
                              "chest": {"x": -10, "z": -24}, "spine": {"z": -8}, "head": {"z": 14}, "root": (0, .08, .08),
                              "aim": {"veil1": (0, .1, -1), "veil2": (0, .1, -1), "censer": (-.2, .2, -1)}})
    fling = M(skirt_wave(1.8, 1, 14), {"upper_arm.R": {"x": -88, "y": -6, "z": 20}, "forearm.R": {"bend": -4}, "hand.R": {"x": 15},
                                      "chest": {"x": 8, "z": 20}, "spine": {"x": 0, "z": 6}, "head": {"x": -6, "z": -8},
                                      "jaw": {"x": 18}, "root": (0, -.12, .03), "aim": {"veil1": (0, .6, -1), "veil2": (0, .7, -1), "censer": (.2, .3, -1)}})
    attack = keys_to_frames([(0, M(skirt_wave(0))), (.25, touch), (.45, cock), (.58, fling), (.75, merge(fling, {"upper_arm.R": {"x": 6}})),
                             (1, M(skirt_wave(0)))], 10)
    # lamento: encolhe abraçando o peito (antecipação), abre os braços e grita para a frente em cone
    hug = M(skirt_wave(0, .6), {"upper_arm.L": {"x": -70, "y": -20, "z": -40}, "upper_arm.R": {"x": -70, "y": 20, "z": 40},
                                "forearm.L": {"bend": -110}, "forearm.R": {"bend": -110}, "spine": {"x": 8}, "chest": {"x": 14},
                                "neck": {"x": 6}, "head": {"x": 16}, "root": (0, .05, -.02)})
    rise = M(skirt_wave(1, .8), {"upper_arm.L": {"x": -40, "y": -55}, "upper_arm.R": {"x": -40, "y": 55},
                                 "forearm.L": {"bend": -20}, "forearm.R": {"bend": -20}, "hand.L": {"x": 20}, "hand.R": {"x": -20},
                                 "spine": {"x": -14}, "chest": {"x": -22}, "neck": {"x": -10}, "head": {"x": -26}, "jaw": {"x": 26},
                                 "root": (0, .06, .16), "aim": {"censer": (.4, .2, -1)}})
    def scream(k):
        j = (-1)**k
        return M(skirt_wave(2 + k, 1.6, 22), {"upper_arm.L": {"x": -20 + 4*j, "y": -60}, "upper_arm.R": {"x": -20 - 4*j, "y": 60},
                                             "forearm.L": {"bend": -10}, "forearm.R": {"bend": -10}, "hand.L": {"x": 30}, "hand.R": {"x": -30},
                                             "spine": {"x": -6}, "chest": {"x": -2}, "neck": {"x": -2}, "head": {"x": -4, "z": 5*j},
                                             "jaw": {"x": 40}, "root": (0, -.12, .1),
                                             "aim": {"veil1": (.1*j, .9, -.6), "veil2": (.15*j, 1, -.7), "censer": (.3, .5, -1)}})
    lament = keys_to_frames([(0, M(skirt_wave(0))), (.2, hug), (.38, rise), (.5, scream(0)), (.62, scream(1)), (.74, scream(2)),
                             (1, M(skirt_wave(0)))], 12)
    # consolo (loop curto): mãos juntas diante do peito, cabeça baixa, flutua devagar
    heal = []
    for i in range(6):
        t = i/6*2*math.pi; b = math.sin(t)
        heal.append(M(skirt_wave(t, .7), {"upper_arm.L": {"x": -62, "y": -14, "z": -38}, "upper_arm.R": {"x": -62, "y": 14, "z": 38},
                                          "forearm.L": {"bend": -95 - 4*b}, "forearm.R": {"bend": -95 - 4*b}, "hand.L": {"x": -20}, "hand.R": {"x": -20},
                                          "chest": {"x": 4 + 2*b}, "neck": {"x": 10}, "head": {"x": 18 + 3*b}, "root": (0, 0, .1 + .03*b),
                                          "aim": {"censer": (.15*math.cos(t), -.2, -1), "veil1": (0, .28, -1)}}))
    hitp = M(skirt_wave(1.5, 1.2), {"chest": {"x": -20, "z": 10}, "spine": {"x": -8}, "head": {"x": -18, "z": 14}, "jaw": {"x": 16},
                                    "upper_arm.L": {"y": -14, "x": 20}, "upper_arm.R": {"y": 18, "x": 20}, "root": (0, .1, .06),
                                    "aim": {"censer": (.3, -.3, -1)}})
    hit = [lerp_pose(M(skirt_wave(0)), hitp, .6), hitp, lerp_pose(hitp, M(skirt_wave(0)), .5), M(skirt_wave(0))]
    # morte: último grito para cima, desaba sobre o próprio vestido, que se abre no chão; ossos e véu por cima
    wail = M(skirt_wave(1, 1.2), {"upper_arm.L": {"x": -110, "y": -20}, "upper_arm.R": {"x": -120, "y": 20}, "forearm.L": {"bend": -20},
                                  "forearm.R": {"bend": -20}, "spine": {"x": -16}, "chest": {"x": -20}, "head": {"x": -30}, "jaw": {"x": 36},
                                  "root": (0, .05, .2)})
    def spread(f, down):
        aim = {}
        for a, ba, bb in PANELS:
            o = Vector((math.cos(a), math.sin(a), 0))
            aim[ba] = tuple(o*f + Vector((0, 0, -1))); aim[bb] = tuple(o + Vector((0, 0, -down)))
        return aim
    slump = M({"root": (0, 0, -.45), "spine": {"x": 30}, "chest": {"x": 30}, "neck": {"x": 20}, "head": {"x": 30, "z": 20},
               "upper_arm.L": {"x": 10, "y": -10}, "upper_arm.R": {"x": 20, "y": 10}, "forearm.L": {"bend": -10}, "forearm.R": {"bend": -10},
               "jaw": {"x": 30}, "aim": dict(spread(.6, 1.2), veil1=(0, .5, -1), veil2=(0, .9, -.6), censer=(.2, .2, -1))})
    GB = ["hips", "spine", "chest", "neck", "head"] + SKB
    pile = M({"root": (0, 0, -.8), "hips": {"x": 25}, "spine": {"x": 45}, "chest": {"x": 30}, "neck": {"x": 15}, "head": {"x": 10, "z": 40},
              "upper_arm.L": {"x": -30, "y": 20}, "upper_arm.R": {"x": -50, "y": -25}, "forearm.L": {"bend": -20}, "forearm.R": {"bend": -10},
              "hand.L": {"x": 30}, "jaw": {"x": 34},
              "aim": dict(spread(1.4, .25), veil1=(.3, 1, -.6), veil2=(.4, 1, -.2), censer=(.6, -.3, -1))})
    death = keys_to_frames([(0, hitp), (.22, wail), (.4, merge(wail, {"head": {"x": -6}})), (.62, slump), (.85, pile), (1, pile)], 12)
    death = finish(death); settle(R, death[6:])
    return {"idle": finish(idle), "walk": finish(walk), "attack": finish(attack), "lament": finish(lament),
            "heal": finish(heal), "hit": finish(hit), "death": death}
