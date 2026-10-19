# Javali Blindado: montaria blindada menor e mais rápida. Javali de pelo eriçado e couro grosso, focinho
# coberto por uma couraça de ferro enferrujado com rebites, presas de javali com ponta de latão, placas em
# escama sobre o lombo e nos ombros, gualdrapa de couro e corrente no ventre. Brilho: olhos verde-Amargo.
import bpy, math, random
from mathutils import Vector, Matrix
from mrig import *
from quad import *
from barda import *

INFO = {"px": 256, "target_z": .6, "rim": (.8, .74, .5), "colors": 40, "samples": 40,
        "fps": {"idle": 7, "walk": 11, "charge": 15, "attack": 12, "hit": 12, "death": 10},
        "loops": ("idle", "walk", "charge")}

BACK = .98
def bones():
    B = quad_bones(sh=.7, hip=.66, y_sh=-.42, y_hip=.42, w=.14, wh=.13, back=BACK, neck=(-.6, .8), head=(-1.0, .62),
                   jaw=((-.66, .72), (-.94, .52)), tail=((.66, .72), (.74, .56)),
                   extra={"belly": ((0, .2, .6), (0, -.2, .6), "spine")})
    # patas curtas e ágeis de javali: colunas retas com casco
    for s, n in ((1, "L"), (-1, "R")):
        w, wh = .14*s, .13*s
        B[f"upper_arm.{n}"] = ((w*.9, -.42, .7), (w, -.38, .36), "chest")
        B[f"forearm.{n}"] = ((w, -.38, .36), (w, -.42, .12), f"upper_arm.{n}")
        B[f"hand.{n}"] = ((w, -.42, .12), (w, -.47, .025), f"forearm.{n}")
        B[f"thigh.{n}"] = ((wh*.9, .42, .64), (wh, .34, .4), "hips")
        B[f"shin.{n}"] = ((wh, .34, .4), (wh, .44, .18), f"thigh.{n}")
        B[f"foot.{n}"] = ((wh, .44, .18), (wh, .42, .025), f"shin.{n}")
    return B

def build():
    skin = stained("j_pele", (.16, .12, .09), stain=(.16, .05, .03), amount=.4, scale=4, rough=.6, grime=1.0, dirt=.5)
    gual = stained("j_gualdrapa", (.13, .08, .05), stain=(.15, .04, .02), amount=.45, scale=3, rough=.7, grime=1.2, dirt=.6)
    bristle = mat("j_cerda", (.08, .06, .045), 0, .85, dirt=.6)
    iron = stained("j_ferro", (.12, .095, .08), stain=(.26, .1, .035), amount=.6, scale=5, metal=.85, rough=.5, grime=.7)
    cloth = stained("j_pano", (.09, .1, .08), stain=(.12, .1, .04), amount=.5, scale=3, rough=.85, grime=1.4, dirt=.7)
    chain = mat("j_corrente", (.2, .2, .21), 1, .38, dirt=.35)
    brass = stained("j_latao", (.42, .28, .11), stain=(.08, .1, .06), amount=.4, scale=6, metal=1, rough=.42, grime=.3)
    tusk = stained("j_presa", (.46, .4, .28), stain=(.14, .06, .02), amount=.35, scale=7, rough=.45, grime=.3)
    hoof = mat("j_casco", (.035, .03, .028), 0, .45, dirt=.6)
    dark = mat("j_boca", (.015, .008, .008), 0, .5)
    eye = mat("j_olho", (.6, 1, .2), emit=(.55, 1, .15), strength=18)

    R = QRig("javali", bones(), ground=.03, ground_bones=PAWS)
    P = R.P

    # ---- corpo: barril compacto, cerdas no lombo, ombros largos
    keys = [(.66, .66, .08, .08), (.62, .7, .2, .21), (.46, .72, .31, .31), (.26, .72, .34, .34), (.02, .7, .35, .35),
            (-.22, .7, .34, .34), (-.42, .72, .32, .32), (-.58, .72, .26, .27), (-.66, .7, .2, .21)]
    keys = [(y, z, rx*.86, rz*.86) for y, z, rx, rz in keys]
    rings = ring_path(keys, .014)
    def rad(i, a, r):
        y = r[0].y; f = 1.0; sn = math.sin(a)
        if -.5 < y < -.2 and sn > .5:  # cupim de ombro
            f *= 1 + .1*max(0, 1 - abs(y + .35)/.2)*(sn - .5)*2
        return f
    R.bind(loft("javali_corpo", rings, skin, seg=32, rad=rad), ["hips", "spine", "chest", "neck"])
    # crista de cerdas do cupim ao lombo (eriçada, de pé)
    R.bind(join(tufts(rings, bristle, 60, (40, 140), (.15, .75), .12, .02, seed=11, back=.4, down=.05, lmin=.6)),
           ["spine", "chest", "hips"])
    # ---- gualdrapa de couro e escamas de ferro em duas fileiras nos ombros e no lombo
    gu = gualdrapa("javali_gualdrapa", rings, gual, -.5, .5, grow=1.08, seg=32)
    R.bind(gu, ["spine", "hips"])
    fileiras = placas(rings, iron, rows=3, cols=5, size=.11, y0=-.5, y1=.5, arc=(-20, 200),
                      bone_at=lambda y: "chest" if y < -.2 else ("spine" if y < .18 else "hips"),
                      rivet_m=brass, seed=5)
    for b, objs in fileiras.items():
        R.rigid(objs, b)
    # corrente pendurada na barriga, presa ao osso do ventre
    ch = []
    for k in range(10):
        y = -.4 + k*.09; c = min(rings, key=lambda q: abs(q[0].y - y))
        p, n = surf(c, math.radians(-90))
        ch.append(prim("primitive_torus_add", chain, p + Vector((0, 0, .02)), (1, 1, 1), major_radius=.028, minor_radius=.007,
                       major_segments=8, minor_segments=4))
    R.rigid(ch, "belly")
    R.rigid(franjas(rings, cloth, -.5, .5, 12, .3, (200, 340), seed=9), "hips")   # franjas de pano
    R.rigid(espinhos(rings, iron, -.6, .5, 12, .08, seed=6, arc=(35, 145)), "spine")            # espinhos na crista
    # ---- pernas: braçadeiras de ferro e cascos
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr, tp = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}"), P(f"hand.{n}", 1)
        fl = limb(f"pata_f{n}", [(*(sh + Vector((-.02*s, .02, .02))), .13), (*sh.lerp(el, .55), .12), (*el, .1),
                                 (*el.lerp(wr, .5), .06), (*wr, .05), (*wr.lerp(tp, .5), .045)], skin)
        R.bind(fl, ["chest", f"upper_arm.{n}", f"forearm.{n}", f"hand.{n}"])
        R.rigid([prim("primitive_torus_add", iron, el.lerp(wr, .4), (1, 1, 1), major_radius=.08, minor_radius=.015,
                      major_segments=12, minor_segments=4)], f"forearm.{n}")
        hp, kn, hk, ft = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        hl = limb(f"pata_t{n}", [(*(hp + Vector((-.02*s, -.02, .02))), .14), (*hp.lerp(kn, .5) + Vector((0, .04, 0)), .14),
                                 (*kn, .095), (*kn.lerp(hk, .5), .055), (*hk, .045), (*hk.lerp(ft, .6), .04), (*ft.lerp(hk, .2), .04)], skin)
        R.bind(hl, ["hips", f"thigh.{n}", f"shin.{n}", f"foot.{n}"])
        for b, a_, tip in ((f"hand.{n}", wr, tp), (f"foot.{n}", hk, ft)):
            d = (tip - a_).normalized(); base = tip - d*.06
            hv = []
            for sx in (-1, 1):
                c = base + Vector((.02*sx, -.012, 0))
                hv.append(along("primitive_cone_add", hoof, c + Vector((0, .015, .04)), Vector((c.x, c.y - .04, .004)), .03,
                                vertices=8, radius1=1, radius2=.6))
            R.rigid(hv, b)
    # cauda fina com tufo
    t1, t2, t3 = P("tail1"), P("tail2"), P("tail2", 1)
    tl = limb("cauda", [(*t1, .025), (*t2, .016), (*t3, .01)], skin)
    tt = [along("primitive_cone_add", bristle, t3, t3 + Vector((rr.uniform(-.03, .03), .02, -.07)), .011, vertices=4,
                radius1=1, radius2=0) for rr in [random.Random(i) for i in range(6)]]
    R.bind(join([tl] + tt), ["hips", "tail1", "tail2"])

    # ---- cabeça: couraça de focinho de ferro enferrujado (rebitada), presas de latão, orelhas, olhos verdes
    hb, ht = P("head"), P("head", 1); d = (ht - hb).normalized(); up = Vector((0, d.z, -d.y))
    if up.z < 0: up = -up
    def H(t, u=0, x=0): return hb + d*t + up*u + Vector((x, 0, 0))
    hd = []
    sk = prim("primitive_uv_sphere_add", skin, H(.1, .02), (.15, .16, .14), segments=16, ring_count=8)
    sk.rotation_euler = d.to_track_quat('Y', 'Z').to_euler(); hd.append(sk)
    sn = along("primitive_cone_add", skin, H(.14, -.01), H(.42, -.02), .12, vertices=16, radius1=1, radius2=.8)
    hd.append(sn)
    hd += testeira(iron, brass, hb, d, up, size=.12)
    hd += chanfro(iron, iron, hb, d, up, size=.09, n=5)
    # couraça do focinho: cone de placa de ferro cobrindo o focinho, com rebites
    snout = along("primitive_cone_add", iron, H(.22, -.01), H(.5, -.02), .135, vertices=16, radius1=1, radius2=.84)
    hd.append(snout)
    for k in range(6):
        a = 2*math.pi*k/6; t = .3 + .04*(k % 2)
        hd.append(prim("primitive_uv_sphere_add", brass, H(t, -.02) + Vector((math.cos(a)*.13, 0, math.sin(a)*.13)),
                       (.012, .012, .012), segments=6, ring_count=4))
    for sx in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", dark, H(.5, -.02, .05*sx), (.016, .02, .016), segments=8, ring_count=6))  # focinho
        hd.append(prim("primitive_uv_sphere_add", eye, H(.19, .09, .1*sx), (.014, .014, .012), segments=8, ring_count=6))  # olho verde
        hd.append(prim("primitive_uv_sphere_add", dark, H(.19, .1, .1*sx), (.024, .022, .02), segments=8, ring_count=6))  # pálpebra
        e0 = H(.0, .14, .12*sx); e1 = e0 + Vector((.14*sx, -.05, -.02))
        hd.append(along("primitive_cone_add", skin, e0, e1, .06, vertices=6, radius1=1, radius2=.3))  # orelha
        # presa de javali para cima, com ponta de latão
        p0 = H(.36, -.1, .07*sx); p1 = H(.42, -.02, .14*sx)
        hd.append(along("primitive_cone_add", tusk, p0, p1, .03, vertices=8, radius1=1, radius2=.5))
        hd.append(prim("primitive_uv_sphere_add", brass, p1, (.012, .012, .012), segments=6, ring_count=4))
    R.rigid(hd, "head")
    jw = [prim("primitive_uv_sphere_add", dark, H(.26, -.2, .05*sx), (.04, .08, .03), segments=8, ring_count=6) for sx in (1, -1)]
    R.rigid(jw, "jaw")
    return R, INFO

# ======================================================================= animações
BASE = {"neck": {"x": 4}, "head": {"x": 4}, "tail1": {"x": -10}, "tail2": {"x": -10}}
def M(*p): return merge(BASE, *p)

def gallop(p):
    return merge(leg_cycle("L", True, p % 1, amp=42, lift=1.2), leg_cycle("R", True, (p + .9) % 1, amp=42, lift=1.2),
                 leg_cycle("R", False, (p + .5) % 1, amp=38, lift=1.1), leg_cycle("L", False, (p + .4) % 1, amp=38, lift=1.1))

def anims(R):
    # fungada e cabeça que anda de um lado para outro, cerdas tremendo
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; s, c = math.sin(t), math.cos(t)
        idle.append(M({"spine": {"x": 1.2*s}, "chest": {"x": -1.2*s}, "neck": {"x": 4 + 3*c}, "head": {"x": 6*s, "z": 8*math.sin(t*.5)},
                       "jaw": {"x": 3 + 3*max(0, s)}, "tail1": {"z": 18*s}, "tail2": {"z": 22*math.sin(t - 1)}}))
    walk = []
    for i in range(8):
        p = i/8; s1 = math.sin(p*2*math.pi); s2 = math.sin(p*4*math.pi)
        legs = merge(leg_cycle("L", True, p, amp=20, lift=.9, fold=.8), leg_cycle("R", False, (p + .05) % 1, amp=18, lift=.9, fold=.8),
                     leg_cycle("R", True, (p + .5) % 1, amp=20, lift=.9, fold=.8), leg_cycle("L", False, (p + .55) % 1, amp=18, lift=.9, fold=.8))
        walk.append(M(legs, {"chest": {"z": 4*s1, "y": 2*s1}, "hips": {"z": -4*s1, "y": -3*s1}, "neck": {"x": 2*s2},
                             "head": {"x": 3*s2, "z": -6*s1}, "tail1": {"z": 16*s1}, "tail2": {"z": 20*s1}}))
    # estocada: cabeça baixa e varre de lado com as presas
    low = M({"hips": {"x": -4}, "neck": {"x": 18}, "head": {"x": 24}, "jaw": {"x": 4},
             "upper_arm.L": {"x": 12}, "upper_arm.R": {"x": 12}, "forearm.L": {"bend": -16}, "forearm.R": {"bend": -16},
             "thigh.L": {"x": -10}, "thigh.R": {"x": -10}, "shin.L": {"bend": 12}, "shin.R": {"bend": 12}, "root": (0, .06, 0)})
    slash = M({"hips": {"x": -6}, "chest": {"x": -6, "z": 12}, "neck": {"x": -10, "z": 16}, "head": {"x": -16, "z": 26, "y": -22}, "jaw": {"x": 20},
               "upper_arm.L": {"x": -24}, "upper_arm.R": {"x": -6}, "forearm.L": {"bend": -30}, "hand.L": {"bend": 40},
               "thigh.L": {"x": 18}, "thigh.R": {"x": 22}, "root": (0, -.25, 0)})
    follow = merge(slash, {"head": {"z": 12, "y": -8}, "neck": {"z": 6}, "jaw": {"x": -10}, "root": (0, -.22, 0)})
    attack = keys_to_frames([(0, M()), (.28, low), (.46, slash), (.6, follow), (1, M())], 8)
    # investida (loop): galope rápido, cabeça baixa, cerdas para trás
    charge = []
    for i in range(6):
        p = i/6; s1 = math.sin(p*2*math.pi); c1 = math.cos(p*2*math.pi)
        charge.append(M(gallop(p), {"hips": {"x": 4*s1}, "chest": {"x": -4*s1}, "neck": {"x": 16}, "head": {"x": 14 - 4*s1},
                                    "jaw": {"x": 6}, "tail1": {"x": 40}, "tail2": {"x": 10}, "ground": .03 + .04*max(0, c1)}))
    hitp = M({"hips": {"z": 6}, "chest": {"z": -8, "x": -4}, "neck": {"x": -14, "z": 10}, "head": {"x": -14}, "jaw": {"x": 20},
              "upper_arm.L": {"x": 10}, "upper_arm.R": {"x": 6}, "tail1": {"x": 10}, "root": (0, .05, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: cai de lado sobre a barda
    kneel = M({"neck": {"x": 20}, "head": {"x": 20, "z": 10}, "jaw": {"x": 18},
               "upper_arm.L": {"x": 40}, "upper_arm.R": {"x": 34}, "forearm.L": {"bend": -90}, "forearm.R": {"bend": -80},
               "hand.L": {"bend": 60}, "hand.R": {"bend": 50}, "thigh.L": {"x": -10}, "thigh.R": {"x": -6}, "hips": {"y": 6}})
    tilt = merge(kneel, {"hips": {"y": 40}, "gb": BODY + PAWS, "ground": .04})
    side = {"hips": {"y": 86}, "neck": {"x": 8}, "head": {"x": 6, "y": 8}, "jaw": {"x": 20},
            "upper_arm.L": {"x": -16, "y": 4}, "upper_arm.R": {"x": -28, "y": -10}, "forearm.L": {"bend": -20}, "forearm.R": {"bend": -12},
            "thigh.L": {"x": 12, "y": 4}, "thigh.R": {"x": 24, "y": -10}, "shin.L": {"bend": 16}, "shin.R": {"bend": 6},
            "tail1": {"x": -20}, "gb": BODY, "ground": .24}
    puff = merge(side, {"upper_arm.R": {"x": -14, "y": -10}, "thigh.R": {"x": 14, "y": -8}, "head": {"x": -8}, "jaw": {"x": 10}, "ground": .28})
    death = keys_to_frames([(0, hitp), (.2, kneel), (.42, tilt), (.6, side), (.8, puff), (1, merge(puff, {"jaw": {"x": 6}}))], 10)
    return {"idle": idle, "walk": walk, "charge": charge, "attack": attack, "hit": hit, "death": death}
