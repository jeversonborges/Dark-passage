# Cão de Vala: cão de praga sarnento e magro das valas de cadáveres. Costelas e vértebras à mostra,
# pelagem rala com tufos e feridas abertas, coleira de espinhos com corrente partida do antigo dono e
# focinheira de ferro arrebentada. Brilho: olhos pequenos cor de brasa. Caça em matilha.
# Variante elite cao_de_vala_alfa: maior, mais escuro, placas de sucata parafusadas e cicatrizes.
import bpy, math, random
from mathutils import Vector
from mrig import *
from quad import *

INFO = {"px": 192, "target_z": .5, "rim": (.9, .6, .38), "colors": 40, "samples": 48,
        "fps": {"idle": 6, "walk": 12, "attack": 14, "leap": 12, "howl": 8, "hit": 12, "death": 10},
        "loops": ("idle", "walk")}

VARIANTS = {
    "cao_de_vala": {},
    # elite: maior, pelo quase preto, placas de sucata parafusadas no lombo e nos ombros, cicatrizes
    "cao_de_vala_alfa": {"scale": 1.22, "fur": (.075, .065, .06), "bare": (.2, .13, .13), "plates": True,
                         "scars": True, "rim": (.95, .5, .3)},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
    if "rim" in V: INFO["rim"] = V["rim"]

BACK = .68
def bones():
    return quad_bones(sh=.6, hip=.6, y_sh=-.3, y_hip=.3, w=.085, wh=.09, back=BACK, neck=(-.5, .84), head=(-.76, .8),
                      jaw=((-.54, .8), (-.72, .755)), tail=((.48, .56), (.6, .36)))

HEAD_PIV = Vector((0, -.5, .84))
def HS(objs, k=1.15):
    for o in objs:
        o.location = HEAD_PIV + (o.location - HEAD_PIV)*k; o.scale = o.scale*k

def build():
    fur = stained("q_pelo", V.get("fur", (.13, .105, .08)), stain=(.16, .02, .012), amount=.35, scale=5, rough=.8,
                  blotch=V.get("bare", (.26, .16, .14)), blotch_amt=.9, grime=1.2, dirt=.4)
    tuft = mat("q_tufo", tuple(c*.5 for c in V.get("fur", (.13, .105, .08))), 0, .9, dirt=.6)
    wound = mat("q_ferida", (.11, .012, .008), 0, .3, dirt=.6, grime=.2)
    iron = stained("q_ferro", (.08, .07, .065), stain=(.17, .065, .025), amount=.5, scale=6, metal=.85, rough=.5, grime=.5)
    leather = stained("q_couro", (.07, .045, .03), stain=(.1, .02, .01), amount=.3, scale=5, rough=.7, grime=.4)
    bone = stained("q_osso", (.42, .37, .27), stain=(.14, .03, .02), amount=.3, scale=7, rough=.5, grime=.3)
    dark = mat("q_boca", (.015, .008, .008), 0, .5)
    eye = mat("q_olho", (1, .4, .1), emit=(1, .3, .05), strength=40)
    scar = mat("q_cicatriz", (.32, .16, .15), 0, .5, dirt=.8, grime=.2)

    R = Rig("cao", bones(), ground=.03, ground_bones=PAWS)
    P = R.P

    # ---- corpo: garupa ossuda, cintura fina, peito fundo com costelas, pescoço
    keys = [(.42, .62, .05, .05), (.37, .635, .1, .1), (.3, .64, .115, .125), (.2, .65, .1, .11), (.1, .66, .08, .085),
            (.02, .64, .095, .12), (-.08, .605, .12, .17), (-.18, .59, .13, .195), (-.27, .61, .125, .18),
            (-.34, .66, .105, .14), (-.41, .73, .085, .105), (-.47, .79, .075, .085), (-.52, .84, .065, .07)]
    rings = ring_path(keys)
    def rad(i, a, r):
        y = r[0].y; f = 1.0
        side = abs(math.cos(a)); low = max(0, -math.sin(a))
        if -.3 < y < .02:   # costelas: sulcos nas laterais
            f *= 1 - .13*side*(.5 - .5*math.cos(y*2*math.pi/.05))**2*min(1, (y + .3)/.05)*min(1, (.02 - y)/.05)
        if -.32 < y < .36 and math.sin(a) > .85:  # vértebras do lombo
            f *= 1 + .1*max(0, math.cos(y*2*math.pi/.05))**3
        if .22 < y < .36 and .3 < math.sin(a) < .9:  # ossos do quadril saltando
            f *= 1 + .12*max(0, 1 - abs(y - .3)/.06)
        if -.32 < y < -.22 and .2 < math.sin(a) < .8:  # escápulas
            f *= 1 + .1*max(0, 1 - abs(y + .27)/.05)
        return f
    body = loft("cao_corpo", rings, fur, seg=32, rad=rad)
    parts = [body]
    parts += tufts(rings, tuft, 70, (55, 125), (.05, .95), .1, .016, 11, back=.5, down=-.1)  # crista do lombo eriçada
    parts += tufts(rings, tuft, 40, (20, 160), (.75, 1), .12, .02, 15, back=.8, down=-.3)  # crista do lombo eriçada
    parts += tufts(rings, tuft, 40, (-30, 50), (.0, 1), .06, .012, 12)
    parts += tufts(rings, tuft, 40, (130, 210), (.0, 1), .06, .012, 13)
    parts += tufts(rings, tuft, 18, (-140, -40), (.35, .75), .07, .012, 14, back=.1, down=1)  # franja na barriga
    # feridas abertas e peladas
    rr = random.Random(5)
    for (ri, a, s) in ((.35, 30, .03), (.55, 150, .035), (.2, 160, .025), (.7, 20, .025), (.12, 60, .02)):
        p, nrm = surf(rings[int(ri*(len(rings)-1))], math.radians(a))
        w = prim("primitive_uv_sphere_add", wound, p - nrm*.006, (s, s*.9, s*.25), segments=10, ring_count=6)
        w.rotation_euler = nrm.to_track_quat('Z', 'Y').to_euler(); parts.append(w)
    if V.get("scars"):
        for (ri, a, L) in ((.4, 15, .1), (.45, 35, .08), (.6, 165, .11), (.25, 140, .07)):
            r0 = rings[int(ri*(len(rings)-1))]; p, nrm = surf(r0, math.radians(a))
            d = Vector((0, .5, -1)).normalized()
            parts.append(along("primitive_cylinder_add", scar, p - d*L/2 + nrm*.002, p + d*L/2 + nrm*.002, .007, vertices=5))
    body = join(parts)
    R.bind(body, ["hips", "spine", "chest", "neck", "thigh.L", "thigh.R", "upper_arm.L", "upper_arm.R"], power=4)

    # ---- patas magras
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr, tp = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}"), P(f"hand.{n}", 1)
        fl = limb(f"pata_f{n}", [(*(sh + Vector((0, .02, .03))), .06), (*sh.lerp(el, .55), .045), (*el, .034),
                                 (*el.lerp(wr, .5), .024), (*wr, .02), (*wr.lerp(tp, .55), .026), (*(tp + Vector((0, .01, .005))), .022)], fur)
        R.bind(fl, ["chest", f"upper_arm.{n}", f"forearm.{n}", f"hand.{n}"])
        hp, kn, hk, ft = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        hl = limb(f"pata_t{n}", [(*(hp + Vector((0, -.02, .03))), .09), (*hp.lerp(kn, .45) + Vector((0, .03, 0)), .07), (*kn, .036),
                                 (*kn.lerp(hk, .5), .028), (*hk, .022), (*hk.lerp(ft, .6), .019), (*(ft + Vector((0, .005, .005))), .024)], fur)
        R.bind(hl, ["hips", f"thigh.{n}", f"shin.{n}", f"foot.{n}"])
        for b, tip in ((f"hand.{n}", tp), (f"foot.{n}", ft)):  # garras
            cl = []
            for k in (-1, 0, 1):
                q = tip + Vector((.012*k, -.012, .0))
                cl.append(along("primitive_cone_add", bone, q, q + Vector((.006*k, -.03, -.015)), .006, vertices=5, radius1=1, radius2=0))
            # tufo e calo na pata
            cl.append(prim("primitive_uv_sphere_add", tuft, tip + Vector((0, .01, .02)), (.025, .03, .02), segments=8, ring_count=5))
            R.rigid(cl, b)
        # cotovelo e jarrete ossudos
        R.rigid([prim("primitive_uv_sphere_add", fur, el + Vector((0, .02, 0)), (.025, .025, .028), segments=8, ring_count=6)], f"forearm.{n}")
        R.rigid([along("primitive_cone_add", fur, hk, hk + Vector((0, .04, .01)), .02, vertices=6, radius1=1, radius2=.3)], f"foot.{n}")

    # ---- cauda rala, pelada na ponta
    t1, t2, t3 = P("tail1"), P("tail2"), P("tail2", 1)
    tl = limb("cauda", [(*t1, .04), (*t2, .024), (*t2.lerp(t3, .6), .015), (*t3, .008)], fur)
    tt = tufts(ring_path([(t1.y, t1.z, .03, .03), (t2.y, t2.z, .018, .018)], .02), tuft, 10, (0, 360), (0, 1), .05, .01, 17, back=1, down=.6)
    R.bind(join([tl] + tt), ["hips", "tail1", "tail2"])

    # ---- cabeça: crânio estreito, focinho comprido, orelhas rasgadas, olhos de brasa
    hd = []
    hd.append(prim("primitive_uv_sphere_add", fur, (0, -.535, .875), (.062, .075, .062), segments=16, ring_count=10))
    sn = along("primitive_cone_add", fur, Vector((0, -.56, .865)), Vector((0, -.745, .82)), .045, vertices=14, radius1=1, radius2=.6)
    sn.scale = (sn.scale.x*.85, sn.scale.y, sn.scale.z); hd.append(sn)
    hd.append(prim("primitive_uv_sphere_add", dark, (0, -.752, .83), (.022, .015, .016), segments=10, ring_count=6))  # nariz
    hd.append(prim("primitive_uv_sphere_add", dark, (0, -.66, .815), (.03, .085, .012), segments=10, ring_count=6))  # boca
    for s in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", fur, (.032*s, -.575, .9), (.03, .03, .018), segments=10, ring_count=6))  # sobrancelha
        hd.append(prim("primitive_uv_sphere_add", dark, (.035*s, -.588, .887), (.016, .012, .012), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", eye, (.038*s, -.597, .888), (.013, .008, .01), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", fur, (.05*s, -.53, .845), (.025, .04, .03), segments=8, ring_count=6))  # bochecha
        # orelhas: em pé, viradas para trás; a direita rasgada pela metade
        base = Vector((.04*s, -.5, .925)); top = base + Vector((.03*s, .05, .1 if s > 0 else .055))
        e = along("primitive_cone_add", fur, base, top + Vector((0, .01, .025 if s > 0 else 0)), .036, vertices=4, radius1=1, radius2=0)
        e.scale = (e.scale.x, e.scale.y*.35, e.scale.z); hd.append(e)
        # presas superiores
        hd.append(along("primitive_cone_add", bone, (.02*s, -.72, .81), (.022*s, -.725, .785), .006, vertices=5, radius1=1, radius2=0))
        for k in range(3):
            y = -.7 + .04*k
            hd.append(along("primitive_cone_add", bone, (.024*s, y, .815), (.024*s, y, .8), .004, vertices=4, radius1=1, radius2=0))
    # focinheira de ferro arrebentada: aro sobre o focinho, tira lateral e pedaço solto
    for y, r in ((-.68, .043), (-.62, .05)):
        o = prim("primitive_torus_add", iron, (0, y, .835), (1, 1, .85), major_radius=r, minor_radius=.007,
                 major_segments=14, minor_segments=4, rot=(80, 0, 0))
        hd.append(o)
    hd.append(along("primitive_cylinder_add", iron, (0, -.69, .87), (0, -.55, .925), .007, vertices=5))
    hd.append(along("primitive_cylinder_add", leather, (.045, -.62, .84), (.06, -.48, .88), .01, vertices=5))
    hd.append(along("primitive_cylinder_add", iron, (-.045, -.65, .8), (-.06, -.6, .72), .006, vertices=5))  # haste partida pendurada
    hd.append(prim("primitive_torus_add", iron, (-.06, -.6, .715), (1, 1, 1), major_radius=.014, minor_radius=.004,
                   major_segments=8, minor_segments=4, rot=(0, 90, 0)))
    if V.get("scars"):
        hd.append(along("primitive_cylinder_add", scar, (.045, -.6, .915), (.03, -.68, .855), .006, vertices=5))
        hd.append(along("primitive_cylinder_add", scar, (-.05, -.53, .9), (-.06, -.6, .85), .006, vertices=5))
    HS(hd)
    R.rigid(hd, "head")
    jw = [along("primitive_cone_add", fur, Vector((0, -.55, .81)), Vector((0, -.72, .775)), .032, vertices=12, radius1=1, radius2=.55)]
    jw[0].scale = (jw[0].scale.x*.85, jw[0].scale.y*.55, jw[0].scale.z)
    for s in (1, -1):
        jw.append(along("primitive_cone_add", bone, (.017*s, -.705, .79), (.018*s, -.71, .815), .005, vertices=5, radius1=1, radius2=0))
        for k in range(2):
            y = -.68 + .04*k
            jw.append(along("primitive_cone_add", bone, (.02*s, y, .792), (.02*s, y, .806), .004, vertices=4, radius1=1, radius2=0))
    HS(jw)
    R.rigid(jw, "jaw")

    # ---- coleira de couro com espinhos, argola e corrente partida
    a, b = P("neck"), P("neck", 1); c = a.lerp(b, .45) + Vector((0, 0, -.01)); d = (b - a).normalized()
    q = d.to_track_quat('Z', 'Y')
    cl = [prim("primitive_torus_add", leather, c, (1, 1.1, 1.8), major_radius=.072, minor_radius=.014,
               major_segments=18, minor_segments=5)]
    cl[0].rotation_euler = q.to_euler()
    ns = 10 if V.get("plates") else 7
    for k in range(ns):
        ang = 2*math.pi*k/ns + .3
        v = q @ Vector((math.cos(ang), math.sin(ang), 0))
        cl.append(along("primitive_cone_add", iron, c + v*.075, c + v*(.13 if V.get("plates") else .115), .011, vertices=6, radius1=1, radius2=0))
    lo = c + q @ Vector((0, -.08, 0))  # argola embaixo (frente do pescoço)
    cl.append(prim("primitive_torus_add", iron, lo, (1, 1, 1), major_radius=.018, minor_radius=.005, major_segments=10, minor_segments=4,
                   rot=(0, 90, 0)))
    for k in range(4):
        cl.append(prim("primitive_torus_add", iron, lo + Vector((.004*k, -.006*k, -.022 - .028*k)), (1, 1, 1.5), major_radius=.012,
                       minor_radius=.004, major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
    R.rigid(cl, "neck")

    # ---- alfa: placas de sucata parafusadas no lombo e nos ombros
    if V.get("plates"):
        rv = random.Random(8)
        scrap = stained("q_sucata", (.2, .12, .07), stain=(.3, .12, .04), amount=.6, scale=5, metal=.7, rough=.55, grime=.3)
        for bone_n, items in (("chest", [(-.24, 70, .07, .055), (-.24, 110, .07, .055), (-.12, 90, .06, .05)]),
                              ("spine", [(.0, 90, .055, .05), (.1, 75, .05, .045)]),
                              ("hips", [(.28, 90, .065, .05), (.3, 40, .05, .04)])):
            pl = []
            for (y, ang, sx, sy) in items:
                ri = min(range(len(rings)), key=lambda i: abs(rings[i][0].y - y))
                p, nrm = surf(rings[ri], math.radians(ang))
                o = prim("primitive_cube_add", scrap, p + nrm*.012, (sx, sy, .007))
                o.rotation_euler = (nrm.to_track_quat('Z', 'Y').to_matrix() @
                                    __import__("mathutils").Matrix.Rotation(rv.uniform(-.3, .3), 3, 'Z')).to_euler()
                pl.append(o)
                for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                    off = o.rotation_euler.to_matrix() @ Vector((dx*sx*.75, dy*sy*.7, .008))
                    pl.append(prim("primitive_uv_sphere_add", iron, o.location + off, (.009, .009, .006), segments=6, ring_count=4))
            R.rigid(pl, bone_n)
        # espinhos de sucata cravados nos ombros
        sp = []
        for s in (1, -1):
            for k in range(3):
                p = Vector((.07*s, -.3 + .05*k, .79 - .01*k))
                sp.append(along("primitive_cone_add", iron, p, p + Vector((.03*s, .04, .07)), .012, vertices=5, radius1=1, radius2=0))
        R.rigid(sp, "chest")

    R.arm.scale = [V.get("scale", 1)]*3
    return R, INFO

# ======================================================================= animações
# postura base: cabeça baixa à frente (caçando), cauda caída
BASE = {"neck": {"x": 12}, "head": {"x": 6}, "tail1": {"x": -12}, "tail2": {"x": -18},
        "upper_arm.L": {"x": -3}, "upper_arm.R": {"x": -3}, "thigh.L": {"x": 2}, "thigh.R": {"x": 2}}
def M(*p): return merge(BASE, *p)

def anims(R):
    # idle: respira com as costelas, fareja, abana a cauda devagar, orelha mexe
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; s, c = math.sin(t), math.cos(t)
        idle.append(M({"spine": {"x": 1.5*s}, "chest": {"x": -1.5*s}, "neck": {"x": 3*c}, "head": {"x": 4*s, "z": 5*math.sin(t*.5)},
                       "jaw": {"x": 4 + 4*max(0, s)}, "tail1": {"z": 10*s}, "tail2": {"z": 14*math.sin(t - .8)}}))
    # trote: pares diagonais (dianteira esquerda + traseira direita)
    walk = []
    for i in range(8):
        p = i/8; s2 = math.sin(p*4*math.pi); s1 = math.sin(p*2*math.pi)
        legs = merge(leg_cycle("L", True, p), leg_cycle("R", False, p),
                     leg_cycle("R", True, (p + .5) % 1), leg_cycle("L", False, (p + .5) % 1))
        walk.append(M(legs, {"chest": {"z": 4*s1, "x": 2*s2}, "hips": {"z": -3*s1, "y": 2*s1}, "neck": {"x": -4*s2},
                             "head": {"x": 3*s2, "z": -4*s1}, "jaw": {"x": 8}, "tail1": {"z": 12*s1, "x": -4}, "tail2": {"z": 16*s1}}))
    # mordida rápida: recolhe, avança o pescoço com a boca aberta e fecha sacudindo
    cock = M({"hips": {"x": 4}, "neck": {"x": -12}, "head": {"x": -10}, "jaw": {"x": 6},
              "thigh.L": {"x": -10}, "thigh.R": {"x": -6}, "shin.L": {"bend": 14}, "shin.R": {"bend": 10},
              "upper_arm.L": {"x": 10}, "upper_arm.R": {"x": 6}, "forearm.L": {"bend": -12}, "tail1": {"x": -14}, "root": (0, .06, 0)})
    lunge = M({"hips": {"x": 4}, "chest": {"x": 8}, "neck": {"x": 34}, "head": {"x": -30}, "jaw": {"x": 50},
               "upper_arm.L": {"x": -40}, "upper_arm.R": {"x": -14}, "forearm.L": {"bend": -30}, "hand.L": {"bend": 40},
               "thigh.L": {"x": 26}, "thigh.R": {"x": 16}, "shin.L": {"bend": -8}, "tail1": {"x": 10}, "root": (0, -.3, 0)})
    snap = merge(lunge, {"jaw": {"x": -48}, "head": {"z": 14, "x": 8}, "neck": {"z": -6}})
    shake = merge(snap, {"head": {"z": -28}, "neck": {"z": 10}, "root": (0, -.26, 0)})
    attack = keys_to_frames([(0, M()), (.22, cock), (.4, lunge), (.52, snap), (.66, shake), (1, M())], 8)
    # bote: agacha, salta esticado (o jogo desloca), aterrissa mordendo
    crouch = M({"hips": {"x": 6}, "neck": {"x": 12}, "head": {"x": -8}, "jaw": {"x": 10},
                "upper_arm.L": {"x": 26}, "upper_arm.R": {"x": 26}, "forearm.L": {"bend": -55}, "forearm.R": {"bend": -55},
                "hand.L": {"bend": 30}, "hand.R": {"bend": 30},
                "thigh.L": {"x": -38}, "thigh.R": {"x": -38}, "shin.L": {"bend": 40}, "shin.R": {"bend": 40},
                "foot.L": {"bend": -26}, "foot.R": {"bend": -26}, "tail1": {"x": -10}, "root": (0, .08, 0)})
    push = M({"hips": {"x": -16}, "neck": {"x": -10}, "head": {"x": -10}, "jaw": {"x": 20},
              "upper_arm.L": {"x": -60}, "upper_arm.R": {"x": -50}, "forearm.L": {"bend": -30}, "forearm.R": {"bend": -40},
              "hand.L": {"bend": 40}, "hand.R": {"bend": 40}, "thigh.L": {"x": 40}, "thigh.R": {"x": 44},
              "shin.L": {"bend": -10}, "shin.R": {"bend": -10}, "foot.L": {"bend": -10}, "foot.R": {"bend": -10},
              "tail1": {"x": 10}, "tail2": {"x": 5}, "ground": .05})
    fly = M({"hips": {"x": -6}, "neck": {"x": -2}, "head": {"x": -18}, "jaw": {"x": 50},
             "upper_arm.L": {"x": -75}, "upper_arm.R": {"x": -70}, "forearm.L": {"bend": -6}, "forearm.R": {"bend": -10},
             "hand.L": {"bend": 20}, "hand.R": {"bend": 20}, "thigh.L": {"x": 70}, "thigh.R": {"x": 66},
             "shin.L": {"bend": -20}, "shin.R": {"bend": -20}, "foot.L": {"bend": -20}, "foot.R": {"bend": -20},
             "tail1": {"x": 30}, "tail2": {"x": 15}, "ground": .42})
    fall = M({"hips": {"x": 10}, "neck": {"x": 18}, "head": {"x": -20}, "jaw": {"x": 54},
              "upper_arm.L": {"x": -40}, "upper_arm.R": {"x": -34}, "forearm.L": {"bend": -10}, "forearm.R": {"bend": -10},
              "thigh.L": {"x": 40}, "thigh.R": {"x": 36}, "shin.L": {"bend": 20}, "shin.R": {"bend": 20},
              "tail1": {"x": 15}, "ground": .22})
    land = M({"hips": {"x": 8}, "chest": {"x": 6}, "neck": {"x": 30}, "head": {"x": -6}, "jaw": {"x": -10},
              "upper_arm.L": {"x": 4}, "upper_arm.R": {"x": 10}, "forearm.L": {"bend": -40}, "forearm.R": {"bend": -46},
              "hand.L": {"bend": 30}, "hand.R": {"bend": 30},
              "thigh.L": {"x": -10}, "thigh.R": {"x": -6}, "shin.L": {"bend": 30}, "shin.R": {"bend": 30},
              "foot.L": {"bend": -20}, "foot.R": {"bend": -20}, "tail1": {"x": -16}})
    leap = keys_to_frames([(0, M()), (.18, crouch), (.3, crouch), (.4, push), (.55, fly), (.68, fall), (.8, land),
                           (.88, merge(land, {"head": {"z": -20}, "neck": {"z": 8}})), (1, M())], 12)
    # uivo: senta nas patas de trás e ergue a cabeça
    sit = M({"hips": {"x": -26}, "spine": {"x": -6}, "neck": {"x": -40}, "head": {"x": -46}, "jaw": {"x": 10},
             "upper_arm.L": {"x": 30}, "upper_arm.R": {"x": 30}, "forearm.L": {"bend": 0},
             "thigh.L": {"x": -60}, "thigh.R": {"x": -60}, "shin.L": {"bend": 80}, "shin.R": {"bend": 80},
             "foot.L": {"bend": -50}, "foot.R": {"bend": -50}, "tail1": {"x": 0}, "tail2": {"x": 10}})
    howl_p = merge(sit, {"neck": {"x": -10}, "head": {"x": -16}, "jaw": {"x": 30}})
    howl = keys_to_frames([(0, M()), (.22, sit), (.36, howl_p), (.5, merge(howl_p, {"head": {"z": 5}, "jaw": {"x": 6}})),
                           (.64, merge(howl_p, {"head": {"z": -5}, "jaw": {"x": -4}})), (.78, merge(howl_p, {"jaw": {"x": 4}})), (1, M())], 12)
    # golpe recebido
    hitp = M({"hips": {"z": 8}, "chest": {"z": -10, "x": -6}, "neck": {"x": -24, "z": 12}, "head": {"x": -16}, "jaw": {"x": 30},
              "upper_arm.L": {"x": 14}, "upper_arm.R": {"x": 8}, "thigh.L": {"x": -8}, "tail1": {"x": -20}, "root": (0, .08, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: gane, as patas cedem e tomba de lado
    buckle = M({"hips": {"x": -8, "y": 10}, "neck": {"x": 20}, "head": {"x": 20}, "jaw": {"x": 20},
                "upper_arm.L": {"x": 30}, "upper_arm.R": {"x": 22}, "forearm.L": {"bend": -70}, "forearm.R": {"bend": -60},
                "hand.L": {"bend": 50}, "hand.R": {"bend": 40},
                "thigh.L": {"x": -40}, "thigh.R": {"x": -30}, "shin.L": {"bend": 60}, "shin.R": {"bend": 50},
                "foot.L": {"bend": -40}, "foot.R": {"bend": -30}, "tail1": {"x": 20}})
    tilt = merge(buckle, {"hips": {"y": 45}, "gb": BODY + PAWS, "ground": .04})
    side = {"hips": {"y": 88}, "neck": {"x": 10, "y": 6}, "head": {"x": -10, "y": 6}, "jaw": {"x": 22},
            "upper_arm.L": {"x": -20, "y": 4}, "upper_arm.R": {"x": -30, "y": -14}, "forearm.L": {"bend": -20}, "forearm.R": {"bend": -8},
            "hand.L": {"bend": 20}, "hand.R": {"bend": 10},
            "thigh.L": {"x": 10, "y": 4}, "thigh.R": {"x": 22, "y": -12}, "shin.L": {"bend": 24}, "shin.R": {"bend": 8},
            "foot.L": {"bend": -10}, "foot.R": {"bend": -6}, "tail1": {"x": -20, "z": 10}, "tail2": {"z": 10},
            "gb": BODY, "ground": .1}
    death = keys_to_frames([(0, hitp), (.25, buckle), (.48, tilt), (.7, side), (.84, merge(side, {"thigh.R": {"x": 10}, "upper_arm.R": {"x": -8}})),
                            (1, merge(side, {"jaw": {"x": 6}}))], 10)
    return {"idle": idle, "walk": walk, "attack": attack, "leap": leap, "howl": howl, "hit": hit, "death": death}
