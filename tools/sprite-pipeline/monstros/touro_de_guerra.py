# Touro de Guerra: montaria blindada (barda de ferro). Touro enorme de couro curtido e cascos de ferro,
# gualdrapa de couro sobre o lombo, placas de ferro enferrujado rebitadas nos flancos, peitoral de cota,
# testeira com chifres de ponta de aço e anel de latão no focinho. Brilho: olhos âmbar (única cor emissiva).
import bpy, math, random
from mathutils import Vector, Matrix
from mrig import *
from quad import *
from barda import *

INFO = {"px": 288, "target_z": .72, "rim": (.85, .6, .36), "colors": 40, "samples": 40,
        "fps": {"idle": 6, "walk": 9, "charge": 13, "attack": 11, "hit": 12, "death": 10},
        "loops": ("idle", "walk", "charge")}

BACK = 1.08
def bones():
    B = quad_bones(sh=.98, hip=.92, y_sh=-.52, y_hip=.5, w=.2, wh=.19, back=BACK, neck=(-.72, 1.02), head=(-1.14, .86),
                   jaw=((-.8, .9), (-1.08, .72)), tail=((.8, .92), (.9, .72)),
                   extra={"belly": ((0, .2, .72), (0, -.2, .72), "spine")})
    # pernas grossas de touro: colunas quase retas (o esqueleto base é de cão)
    for s, n in ((1, "L"), (-1, "R")):
        w, wh = .2*s, .19*s
        B[f"upper_arm.{n}"] = ((w*.9, -.52, .98), (w, -.48, .5), "chest")
        B[f"forearm.{n}"] = ((w, -.48, .5), (w, -.52, .15), f"upper_arm.{n}")
        B[f"hand.{n}"] = ((w, -.52, .15), (w, -.58, .025), f"forearm.{n}")
        B[f"thigh.{n}"] = ((wh*.9, .5, .9), (wh, .42, .5), "hips")
        B[f"shin.{n}"] = ((wh, .42, .5), (wh, .52, .22), f"thigh.{n}")
        B[f"foot.{n}"] = ((wh, .52, .22), (wh, .5, .025), f"shin.{n}")
    return B

def build():
    hide = stained("t_couro", (.13, .085, .06), stain=(.14, .05, .025), amount=.4, scale=4, rough=.6, grime=1.0, dirt=.5)
    gual = stained("t_gualdrapa", (.12, .075, .05), stain=(.15, .04, .02), amount=.45, scale=3, rough=.7, grime=1.2, dirt=.6)
    bristle = mat("t_pelo", (.07, .05, .04), 0, .85, dirt=.6)
    iron = stained("t_ferro", (.1, .085, .075), stain=(.24, .09, .03), amount=.6, scale=5, metal=.85, rough=.5, grime=.6)
    steel = mat("t_aco", (.45, .45, .47), 1, .32, dirt=.2)
    brass = stained("t_latao", (.42, .28, .11), stain=(.08, .1, .06), amount=.4, scale=6, metal=1, rough=.42, grime=.3)
    horn = stained("t_chifre", (.4, .34, .25), stain=(.12, .05, .02), amount=.3, scale=6, rough=.5, grime=.4)
    hoof = mat("t_casco", (.035, .03, .028), 0, .45, dirt=.6)
    dark = mat("t_boca", (.015, .008, .008), 0, .5)
    bone = stained("t_osso", (.5, .46, .36), stain=(.2, .14, .05), amount=.3, scale=6, rough=.55, grime=.6)
    cloth = stained("t_pano", (.09, .1, .08), stain=(.12, .1, .04), amount=.5, scale=3, rough=.85, grime=1.4, dirt=.7)
    eye = mat("t_olho", (1, .62, .15), emit=(1, .52, .08), strength=14)

    R = QRig("touro", bones(), ground=.03, ground_bones=PAWS)
    P = R.P

    # ---- corpo: barril largo, cernelha alta, peito profundo, garupa larga
    keys = [(.86, .94, .1, .1), (.82, .98, .24, .26), (.64, 1.0, .38, .38), (.42, .98, .42, .42), (.16, .96, .44, .44),
            (-.1, .96, .44, .43), (-.36, .98, .42, .42), (-.56, .98, .36, .38), (-.7, .95, .3, .32),
            (-.82, .92, .24, .26), (-.9, .9, .18, .2)]
    rings = ring_path(keys, .015)
    def rad(i, a, r):
        y = r[0].y; f = 1.0; sn = math.sin(a)
        if -.7 < y < -.3 and sn > .5:  # cupim
            f *= 1 + .12*max(0, 1 - abs(y + .5)/.25)*(sn - .5)*2
        if .25 < y < .7 and sn > -.2:  # garupa musculosa
            f *= 1 + .05*max(0, 1 - abs(y - .45)/.3)
        return f
    parts = [loft("touro_corpo", rings, hide, seg=36, rad=rad)]
    R.bind(parts[0], ["hips", "spine", "chest", "neck"])
    # pelo ralo no pescoço e no cupim
    parts.append(join(tufts(rings, bristle, 40, (30, 150), (.2, .85), .09, .02, seed=7, back=.7)))
    # ---- gualdrapa de couro sobre o lombo e a garupa, borda de tachas de latão
    gu = gualdrapa("touro_gualdrapa", rings, gual, -.6, .6, grow=1.07)
    R.bind(gu, ["spine", "hips"])
    for k in range(18):
        y = -.55 + k*.065; c = min(rings, key=lambda q: abs(q[0].y - y))
        p, n = surf(c, math.radians(-14)) if k % 2 == 0 else surf(c, math.radians(194))
        t = prim("primitive_uv_sphere_add", brass, p + n*.04, (.02, .02, .02), segments=6, ring_count=4)
        R.rigid([t], "spine" if y > -.2 else "hips")

    # ---- barda: placas de ferro enferrujado em duas fileiras sobrepostas nos flancos e no lombo
    fileiras = placas(rings, iron, rows=4, cols=5, size=.15, y0=-.62, y1=.58, arc=(-30, 210),
                      bone_at=lambda y: "chest" if y < -.25 else ("spine" if y < .2 else "hips"),
                      rivet_m=brass, seed=3)
    for b, objs in fileiras.items():
        R.rigid(objs, b)
    # peitoral de placas e cota em volta do peito, presa ao tórax
    R.rigid(peitoral(iron, brass, Vector((0, -.98, .62)), (.3, .2, .34), rot=(0, 0, 0)), "chest")
    R.rigid(caveira(bone, dark, Vector((0, -1.05, .66)), size=.1), "chest")  # medalhão de caveira
    R.rigid(franjas(rings, cloth, -.6, .6, 18, .55, (160, 380)), "hips")   # caparazão rasgado
    R.rigid(espinhos(rings, iron, -.7, .6, 16, .13, arc=(30, 150)), "spine")               # crista de espinhos
    cota = []
    for k in range(16):
        y = -.9 + k*.06
        ring = min(rings, key=lambda q: abs(q[0].y - y))
        p, n = surf(ring, math.radians(-40 + 14*(k % 3)))
        cota.append(prim("primitive_uv_sphere_add", steel, p + n*.03, (.02, .02, .02), segments=6, ring_count=4))
    R.rigid(cota, "chest")
    # ---- pernas: grevas de ferro com faixa de latão, cascos de ferro
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr, tp = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}"), P(f"hand.{n}", 1)
        fl = limb(f"pata_f{n}", [(*(sh + Vector((-.02*s, .02, .02))), .3), (*sh.lerp(el, .55), .25), (*el, .19),
                                 (*el.lerp(wr, .5), .13), (*wr, .11), (*wr.lerp(tp, .5), .1)], hide)
        R.bind(fl, ["chest", f"upper_arm.{n}", f"forearm.{n}", f"hand.{n}"])
        gr = []
        for t in (.3, .7):
            c = el.lerp(wr, t); gr.append(prim("primitive_torus_add", iron, c, (1, 1, 1), major_radius=.12, minor_radius=.02,
                                              major_segments=14, minor_segments=5))
        gr.append(prim("primitive_torus_add", brass, el.lerp(wr, .5), (1, 1, 1), major_radius=.12, minor_radius=.012,
                       major_segments=14, minor_segments=4))
        R.rigid(gr, f"forearm.{n}")
        hp, kn, hk, ft = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        hl = limb(f"pata_t{n}", [(*(hp + Vector((-.02*s, -.02, .02))), .32), (*hp.lerp(kn, .5) + Vector((0, .05, 0)), .24),
                                 (*kn, .16), (*kn.lerp(hk, .5), .12), (*hk, .09), (*hk.lerp(ft, .6), .085), (*ft.lerp(hk, .2), .085)], hide)
        R.bind(hl, ["hips", f"thigh.{n}", f"shin.{n}", f"foot.{n}"])
        for b, a_, tip in ((f"hand.{n}", wr, tp), (f"foot.{n}", hk, ft)):
            d = (tip - a_).normalized(); base = tip - d*.08
            hv = []
            for sx in (-1, 1):  # casco fendido de ferro
                c = base + Vector((.026*sx, -.016, 0))
                hv.append(along("primitive_cone_add", hoof, c + Vector((0, .02, .05)), Vector((c.x, c.y - .05, .005)), .04,
                                vertices=8, radius1=1, radius2=.6))
            hv.append(prim("primitive_torus_add", iron, base + Vector((0, 0, .08)), major_radius=.06, minor_radius=.016,
                           major_segments=12, minor_segments=4))
            R.rigid(hv, b)
    # cauda curta de touro com pincel de pelo
    t1, t2, t3 = P("tail1"), P("tail2"), P("tail2", 1)
    tl = limb("cauda", [(*t1, .035), (*t2, .026), (*t3, .018)], hide)
    tt = [along("primitive_cone_add", bristle, t3, t3 + Vector((rr.uniform(-.04, .04), .03, -.12)), .02, vertices=4,
                radius1=1, radius2=0) for rr in [random.Random(i) for i in range(8)]]
    R.bind(join([tl] + tt), ["hips", "tail1", "tail2"])

    # ---- cabeça: crânio largo, focinho quadrado, anel de latão, testeira de ferro, chifres de aço
    hb, ht = P("head"), P("head", 1); d = (ht - hb).normalized(); up = Vector((0, d.z, -d.y))
    if up.z < 0: up = -up
    def H(t, u=0, x=0): return hb + d*t + up*u + Vector((x, 0, 0))
    hd = []
    sk = prim("primitive_uv_sphere_add", hide, H(.1, .02), (.3, .32, .27), segments=18, ring_count=10)
    sk.rotation_euler = d.to_track_quat('Y', 'Z').to_euler(); hd.append(sk)
    sn = along("primitive_cone_add", hide, H(.16, -.02), H(.62, -.04), .21, vertices=18, radius1=1, radius2=.78)
    sn.scale = (sn.scale.x, sn.scale.y*.9, sn.scale.z); hd.append(sn)
    hd += testeira(iron, brass, hb, d, up, size=.2)
    hd += chanfro(iron, iron, hb, d, up, size=.12, n=6)
    for sx in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", dark, H(.64, -.03, .075*sx), (.02, .026, .02), segments=8, ring_count=6))  # narina
        hd.append(prim("primitive_uv_sphere_add", eye, H(.2, .08, .15*sx), (.018, .018, .016), segments=8, ring_count=6))  # olho âmbar
        hd.append(prim("primitive_uv_sphere_add", dark, H(.2, .09, .15*sx), (.03, .03, .03), segments=8, ring_count=6))  # pálpebra
        e0 = H(.0, .18, .18*sx); e1 = e0 + Vector((.22*sx, -.06, .02))
        hd.append(along("primitive_cone_add", hide, e0, e1, .09, vertices=6, radius1=1, radius2=.3))  # orelha
        # chifre de touro com ponta de aço, saindo de trás da testeira para cima e para a frente
        c0 = H(.05, .24, .2*sx); c1 = c0 + Vector((.2*sx, -.12, .24)); c2 = c1 + Vector((.12*sx, -.12, .14))
        hd.append(along("primitive_cone_add", horn, c0, c1, .07, vertices=8, radius1=1, radius2=.55))
        hd.append(along("primitive_cone_add", horn, c1, c2, .05, vertices=8, radius1=1, radius2=.55))
        hd.append(along("primitive_cone_add", steel, c2, c2 + Vector((.05*sx, -.04, .06)), .035, vertices=8, radius1=1, radius2=0))
    # anel de latão no focinho e corrente de rédea
    hd.append(prim("primitive_torus_add", brass, H(.5, -.1), (1, 1, 1), major_radius=.075, minor_radius=.015,
                   major_segments=14, minor_segments=5))
    R.rigid(hd, "head")
    jw = []
    for sx in (1, -1):  # barbela
        jw.append(prim("primitive_uv_sphere_add", hide, H(.3, -.22, .09*sx), (.05, .09, .05), segments=8, ring_count=6))
    R.rigid(jw, "jaw")
    return R, INFO

# ======================================================================= animações
BASE = {"neck": {"x": 4}, "head": {"x": 4}, "tail1": {"x": -10}, "tail2": {"x": -10}}
def M(*p): return merge(BASE, *p)

def gallop(p):
    return merge(leg_cycle("L", True, p % 1, amp=40, lift=1.1), leg_cycle("R", True, (p + .9) % 1, amp=40, lift=1.1),
                 leg_cycle("R", False, (p + .5) % 1, amp=36, lift=1.0), leg_cycle("L", False, (p + .4) % 1, amp=36, lift=1.0))

def anims(R):
    # respiração pesada e bufada: o cupim sobe e desce, a cabeça se mexe devagar
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; s, c = math.sin(t), math.cos(t)
        idle.append(M({"spine": {"x": 1.4*s}, "chest": {"x": -1.6*s, "z": .6*c}, "neck": {"x": 4 + 3*c}, "head": {"x": 5*s, "z": 4*math.sin(t*.5)},
                       "jaw": {"x": 2 + 2*max(0, s)}, "tail1": {"z": 16*s}, "tail2": {"z": 20*math.sin(t - 1)}}))
    walk = []
    for i in range(8):
        p = i/8; s1 = math.sin(p*2*math.pi); s2 = math.sin(p*4*math.pi)
        legs = merge(leg_cycle("L", True, p, amp=16, lift=.7, fold=.7), leg_cycle("R", False, (p + .05) % 1, amp=14, lift=.7, fold=.7),
                     leg_cycle("R", True, (p + .5) % 1, amp=16, lift=.7, fold=.7), leg_cycle("L", False, (p + .55) % 1, amp=14, lift=.7, fold=.7))
        walk.append(M(legs, {"chest": {"z": 3*s1, "y": 2*s1}, "hips": {"z": -3*s1, "y": -2*s1}, "neck": {"x": 2*s2},
                             "head": {"x": 3*s2, "z": -4*s1}, "tail1": {"z": 14*s1}, "tail2": {"z": 18*s1}}))
    # chifrada: abaixa a cabeça e joga para cima, de lado, com os chifres
    low = M({"hips": {"x": -4}, "neck": {"x": 20}, "head": {"x": 24}, "jaw": {"x": 4},
             "upper_arm.L": {"x": 12}, "upper_arm.R": {"x": 12}, "forearm.L": {"bend": -16}, "forearm.R": {"bend": -16},
             "thigh.L": {"x": -10}, "thigh.R": {"x": -10}, "shin.L": {"bend": 12}, "shin.R": {"bend": 12}, "root": (0, .08, 0)})
    gore = M({"hips": {"x": -6}, "chest": {"x": -6, "z": 10}, "neck": {"x": -12, "z": 14}, "head": {"x": -16, "z": 22, "y": -20}, "jaw": {"x": 20},
              "upper_arm.L": {"x": -24}, "upper_arm.R": {"x": -6}, "forearm.L": {"bend": -30}, "hand.L": {"bend": 40},
              "thigh.L": {"x": 18}, "thigh.R": {"x": 22}, "root": (0, -.3, 0)})
    follow = merge(gore, {"head": {"z": 10, "y": -6}, "neck": {"z": 6}, "jaw": {"x": -10}, "root": (0, -.28, 0)})
    attack = keys_to_frames([(0, M()), (.28, low), (.46, gore), (.6, follow), (1, M())], 8)
    # investida (loop): galope pesado com a cabeça baixa e a barda balançando
    charge = []
    for i in range(6):
        p = i/6; s1 = math.sin(p*2*math.pi); c1 = math.cos(p*2*math.pi)
        charge.append(M(gallop(p), {"hips": {"x": 4*s1}, "chest": {"x": -4*s1}, "neck": {"x": 16}, "head": {"x": 14 - 4*s1},
                                    "jaw": {"x": 6}, "tail1": {"x": 40}, "tail2": {"x": 10}, "ground": .03 + .05*max(0, c1)}))
    hitp = M({"hips": {"z": 6}, "chest": {"z": -8, "x": -4}, "neck": {"x": -14, "z": 10}, "head": {"x": -14}, "jaw": {"x": 20},
              "upper_arm.L": {"x": 10}, "upper_arm.R": {"x": 6}, "tail1": {"x": 10}, "root": (0, .06, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: cambaleia, ajoelha na frente, tomba de lado com a barda
    kneel = M({"neck": {"x": 20}, "head": {"x": 20, "z": 10}, "jaw": {"x": 18},
               "upper_arm.L": {"x": 40}, "upper_arm.R": {"x": 34}, "forearm.L": {"bend": -90}, "forearm.R": {"bend": -80},
               "hand.L": {"bend": 60}, "hand.R": {"bend": 50}, "thigh.L": {"x": -10}, "thigh.R": {"x": -6}, "hips": {"y": 6}})
    tilt = merge(kneel, {"hips": {"y": 40}, "gb": BODY + PAWS, "ground": .05})
    side = {"hips": {"y": 86}, "neck": {"x": 8}, "head": {"x": 6, "y": 8}, "jaw": {"x": 20},
            "upper_arm.L": {"x": -16, "y": 4}, "upper_arm.R": {"x": -28, "y": -10}, "forearm.L": {"bend": -20}, "forearm.R": {"bend": -12},
            "thigh.L": {"x": 12, "y": 4}, "thigh.R": {"x": 24, "y": -10}, "shin.L": {"bend": 16}, "shin.R": {"bend": 6},
            "tail1": {"x": -20}, "gb": BODY, "ground": .3}
    puff = merge(side, {"upper_arm.R": {"x": -14, "y": -10}, "thigh.R": {"x": 14, "y": -8}, "head": {"x": -8}, "jaw": {"x": 10}, "ground": .36})
    death = keys_to_frames([(0, hitp), (.2, kneel), (.42, tilt), (.6, side), (.8, puff), (1, merge(puff, {"jaw": {"x": 6}}))], 10)
    return {"idle": idle, "walk": walk, "charge": charge, "attack": attack, "hit": hit, "death": death}
