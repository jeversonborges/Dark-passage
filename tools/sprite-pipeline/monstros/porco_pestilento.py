# Porco Pestilento: javali enorme e doente, inchado de pústulas, presas quebradas, crina de cerdas
# no lombo, arreio de couro com fivelas de latão e uma placa de ferro rebitada na testa (aríete).
# Brilho: pus verde-ácido nas pústulas e nos olhinhos. Morte: tomba e incha (a explosão é efeito).
import bpy, math, random
from mathutils import Vector, Matrix
from mrig import *
from quad import *

INFO = {"px": 256, "target_z": .62, "rim": (.7, .85, .4), "colors": 40, "samples": 40,
        "fps": {"idle": 6, "walk": 9, "attack": 12, "scrape": 9, "charge": 14, "stun": 7, "hit": 12, "death": 10},
        "loops": ("idle", "walk", "scrape", "charge", "stun")}

BACK = .9
def bones():
    B = quad_bones(sh=.8, hip=.72, y_sh=-.45, y_hip=.46, w=.17, wh=.16, back=BACK, neck=(-.72, .9), head=(-1.18, .62),
                      jaw=((-.8, .74), (-1.1, .56)), tail=((.74, .8), (.8, .62)),
                      extra={"belly": ((0, .25, .66), (0, -.25, .66), "spine")})
    # patas de porco: colunas quase retas (o esqueleto base é de cão)
    for s, n in ((1, "L"), (-1, "R")):
        w, wh = .17*s, .16*s
        B[f"upper_arm.{n}"] = ((w*.9, -.45, .8), (w, -.41, .43), "chest")
        B[f"forearm.{n}"] = ((w, -.41, .43), (w, -.45, .13), f"upper_arm.{n}")
        B[f"hand.{n}"] = ((w, -.45, .13), (w, -.51, .025), f"forearm.{n}")
        B[f"thigh.{n}"] = ((wh*.9, .46, .72), (wh, .37, .45), "hips")
        B[f"shin.{n}"] = ((wh, .37, .45), (wh, .48, .2), f"thigh.{n}")
        B[f"foot.{n}"] = ((wh, .48, .2), (wh, .45, .025), f"shin.{n}")
    return B

def build():
    skin = stained("p_pele", (.17, .12, .105), stain=(.17, .03, .02), amount=.35, scale=4, rough=.55,
                   blotch=(.1, .085, .07), blotch_amt=.9, grime=1.2, dirt=.45)
    bristle = mat("p_cerda", (.05, .04, .035), 0, .85, dirt=.6)
    sore = mat("p_ferida", (.13, .03, .015), 0, .3, dirt=.6, grime=.2)
    pus = mat("p_pus", (.55, .8, .2), emit=(.45, 1, .1), strength=5)
    eye = mat("p_olho", (.6, 1, .2), emit=(.55, 1, .15), strength=18)
    iron = stained("p_ferro", (.08, .07, .065), stain=(.18, .07, .025), amount=.55, scale=5, metal=.85, rough=.5, grime=.5)
    leather = stained("p_couro", (.075, .045, .028), stain=(.12, .025, .012), amount=.35, scale=4, rough=.65, grime=.5)
    brass = stained("p_latao", (.4, .26, .1), stain=(.08, .1, .06), amount=.4, scale=6, metal=1, rough=.45, grime=.3)
    tusk = stained("p_presa", (.42, .36, .24), stain=(.14, .06, .02), amount=.35, scale=7, rough=.45, grime=.3)
    hoof = mat("p_casco", (.035, .03, .028), 0, .45, dirt=.6)
    dark = mat("p_boca", (.015, .008, .008), 0, .5)
    snoutm = stained("p_focinho", (.3, .19, .17), stain=(.12, .03, .02), amount=.4, scale=8, rough=.4, grime=.2)

    R = QRig("porco", bones(), ground=.03, ground_bones=PAWS)
    P = R.P

    # ---- corpo: barril enorme, corcova de músculo nos ombros, garupa caída
    keys = [(.8, .8, .06, .06), (.75, .81, .19, .19), (.64, .81, .28, .28), (.46, .8, .32, .33), (.24, .79, .35, .37),
            (.02, .79, .36, .38), (-.2, .8, .35, .37), (-.38, .85, .33, .34), (-.52, .87, .29, .3),
            (-.64, .86, .24, .25), (-.74, .84, .2, .21), (-.8, .83, .17, .18)]
    rings = ring_path(keys, .015)
    def rad(i, a, r):
        y = r[0].y; f = 1.0; sn = math.sin(a)
        if -.6 < y < -.2 and sn > .5:  # corcova
            f *= 1 + .1*max(0, 1 - abs(y + .4)/.2)*(sn - .5)*2
        if .3 < y < .6 and .2 < sn < .9:  # ancas ossudas
            f *= 1 + .05*max(0, 1 - abs(y - .45)/.12)
        return f
    body = loft("porco_corpo", rings, skin, seg=36, rad=rad)
    parts = [body]
    # crina de cerdas grossas no lombo (silhueta) e cerdas ralas pelo corpo
    parts += tufts(rings, bristle, 110, (70, 110), (.05, .97), .2, .022, 21, back=.7, down=-.3, lmin=.4)
    parts += tufts(rings, bristle, 70, (30, 150), (.1, .95), .08, .014, 22, back=.5, down=.1)
    parts += tufts(rings, bristle, 30, (-160, -20), (.2, .85), .07, .014, 23, back=.2, down=1)
    # pústulas: bolhas de carne com a ponta brilhando, feridas abertas
    rr = random.Random(7); pust = []
    for k in range(26):
        ri = rr.uniform(.08, .92); a = math.radians(rr.choice([rr.uniform(-30, 70), rr.uniform(110, 210)]))
        p, nrm = surf(rings[int(ri*(len(rings)-1))], a)
        s = rr.uniform(.035, .065)
        b = prim("primitive_uv_sphere_add", skin, p, (s, s, s*.8), segments=12, ring_count=8)
        b.rotation_euler = nrm.to_track_quat('Z', 'Y').to_euler(); parts.append(b)
        if k % 2 == 0:
            parts.append(prim("primitive_uv_sphere_add", pus, p + nrm*s*.64, (s*.36, s*.36, s*.25), segments=8, ring_count=6))
            parts[-1].rotation_euler = b.rotation_euler
    for k in range(7):
        ri = rr.uniform(.15, .85); a = math.radians(rr.uniform(-60, 240))
        p, nrm = surf(rings[int(ri*(len(rings)-1))], a); s = rr.uniform(.04, .07)
        w = prim("primitive_uv_sphere_add", sore, p - nrm*.006, (s, s*.8, s*.2), segments=10, ring_count=6)
        w.rotation_euler = nrm.to_track_quat('Z', 'Y').to_euler(); parts.append(w)
    # ---- arreio de couro: cilha atrás dos ombros, peitoral, tira do lombo até a garupa, fivelas de latão
    def ring_at(y): return min(range(len(rings)), key=lambda i: abs(rings[i][0].y - y))
    def strap(pts, w=.022, m=leather):
        out = []
        for a_, b_ in zip(pts, pts[1:]):
            o = along("primitive_cube_add", m, a_, b_, w); o.scale = (o.scale.x, o.scale.y*.35, o.scale.z*1.05)
            out.append(o)
        return out
    def ring_pts(y, a0, a1, n, off=.012, k=1.0):
        r = rings[ring_at(y)]; out = []
        for j in range(n+1):
            a = math.radians(a0 + (a1 - a0)*j/n); p, nrm = surf(r, a); out.append(r[0] + (p - r[0])*k + nrm*off)
        return out
    harn = []
    for y in (-.26, .3):
        pts = ring_pts(y, -90, 270, 24); harn += strap(pts, .028)
        for a in (0, 180):  # fivelas
            p, nrm = surf(rings[ring_at(y)], math.radians(a))
            o = prim("primitive_cube_add", brass, p + nrm*.02, (.012, .045, .04)); o.rotation_euler = nrm.to_track_quat('X', 'Z').to_euler()
            harn.append(o)
        for j in range(0, 24, 3):  # rebites
            harn.append(prim("primitive_uv_sphere_add", brass, pts[j] + (pts[j] - rings[ring_at(y)][0]).normalized()*.014,
                             (.01, .01, .01), segments=6, ring_count=4))
    # tira do lombo e peitoral
    top = [surf(rings[ring_at(y)], math.radians(90))[0] + Vector((0, 0, .015)) for y in (-.26, -.1, .1, .3)]
    harn += strap(top, .03)
    for s in (1, -1):
        chest = [surf(rings[ring_at(y)], math.radians(a))[0] for y, a in ((-.26, 90 - 75*s), (-.45, 90 - 60*s), (-.62, 90 - 45*s))]
        harn += strap([c + (c - Vector((0, c.y, .82))).normalized()*.015 for c in chest], .026)
    # argola lateral com corrente partida
    p, nrm = surf(rings[ring_at(-.26)], math.radians(200))
    harn.append(prim("primitive_torus_add", iron, p + nrm*.03, (1, 1, 1), major_radius=.035, minor_radius=.008, major_segments=12,
                     minor_segments=4, rot=(0, 90, 0)))
    for k in range(4):
        harn.append(prim("primitive_torus_add", iron, p + nrm*.035 + Vector((0, .02*k, -.04 - .045*k)), (1, 1, 1.5),
                         major_radius=.02, minor_radius=.006, major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
    body = join(parts + harn)
    R.bind(body, ["hips", "spine", "chest", "neck", "belly", "thigh.L", "thigh.R", "upper_arm.L", "upper_arm.R"], power=4)

    # ---- patas curtas e grossas com cascos
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr, tp = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}"), P(f"hand.{n}", 1)
        fl = limb(f"pata_f{n}", [(*(sh + Vector((-.02*s, .02, .02))), .18), (*sh.lerp(el, .55), .14), (*el, .1),
                                 (*el.lerp(wr, .5), .075), (*wr, .062), (*wr.lerp(tp, .5), .06)], skin)
        R.bind(fl, ["chest", f"upper_arm.{n}", f"forearm.{n}", f"hand.{n}"])
        hp, kn, hk, ft = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        hl = limb(f"pata_t{n}", [(*(hp + Vector((-.02*s, -.02, .02))), .2), (*hp.lerp(kn, .5) + Vector((0, .05, 0)), .15), (*kn, .09),
                                 (*kn.lerp(hk, .5), .07), (*hk, .055), (*hk.lerp(ft, .6), .05), (*ft.lerp(hk, .2), .05)], skin)
        R.bind(hl, ["hips", f"thigh.{n}", f"shin.{n}", f"foot.{n}"])
        for b, a_, tip in ((f"hand.{n}", wr, tp), (f"foot.{n}", hk, ft)):
            d = (tip - a_).normalized(); base = tip - d*.07
            hv = []
            for sx in (-1, 1):  # casco fendido
                c = base + Vector((.022*sx, -.015, 0))
                o = along("primitive_cone_add", hoof, c + Vector((0, .02, .045)), Vector((c.x, c.y - .045, .005)), .032,
                          vertices=8, radius1=1, radius2=.55)
                hv.append(o)
                hv.append(along("primitive_cone_add", hoof, base + Vector((.035*sx, .05, .08)), base + Vector((.04*sx, .07, .04)), .012,
                                vertices=5, radius1=1, radius2=0))  # esporões
            hv.append(prim("primitive_torus_add", bristle, base + Vector((0, 0, .06)), (1, 1, 1), major_radius=.05,
                           minor_radius=.014, major_segments=10, minor_segments=4))
            R.rigid(hv, b)
    # cauda fina e pelada com tufo
    t1, t2, t3 = P("tail1"), P("tail2"), P("tail2", 1)
    tl = limb("cauda", [(*t1, .035), (*t2, .022), (*t3, .012)], skin)
    tt = [along("primitive_cone_add", bristle, t3, t3 + Vector((rr.uniform(-.03, .03), .03, -.08)), .012, vertices=4,
                radius1=1, radius2=0) for _ in range(6)]
    R.bind(join([tl] + tt), ["hips", "tail1", "tail2"])

    # ---- cabeça: crânio grande, focinho em disco, orelhas rasgadas caídas, placa-aríete de ferro rebitada
    hb, ht = P("head"), P("head", 1); d = (ht - hb).normalized(); up = Vector((0, d.z, -d.y))
    if up.z < 0: up = -up
    def H(t, u=0, x=0): return hb + d*t + up*u + Vector((x, 0, 0))
    hd = []
    sk = prim("primitive_uv_sphere_add", skin, H(.12, .02), (.19, .2, .17), segments=18, ring_count=10)
    sk.rotation_euler = d.to_track_quat('Y', 'Z').to_euler(); hd.append(sk)
    sn = along("primitive_cone_add", skin, H(.15, -.01), H(.55, -.02), .15, vertices=16, radius1=1, radius2=.58)
    sn.scale = (sn.scale.x, sn.scale.y*.85, sn.scale.z); hd.append(sn)
    disc = prim("primitive_cylinder_add", snoutm, H(.55, -.02), (.085, .075, .025), vertices=16)
    disc.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); hd.append(disc)
    for sx in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", dark, H(.575, -.015, .032*sx), (.017, .02, .017), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", skin, H(.16, .1, .12*sx), (.06, .05, .045), segments=10, ring_count=6))  # sobrancelha
        hd.append(prim("primitive_uv_sphere_add", dark, H(.2, .07, .115*sx), (.024, .02, .02), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", eye, H(.212, .07, .118*sx), (.012, .01, .01), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", skin, H(.25, -.08, .12*sx), (.07, .1, .07), segments=10, ring_count=6))  # bochecha
        # orelhas caídas para o lado, a esquerda rasgada
        e0 = H(.0, .14, .12*sx); e1 = e0 + Vector((.16*sx, -.06, -.04 if sx > 0 else -.1))*(.65 if sx > 0 else 1)
        e = along("primitive_cone_add", skin, e0, e1, .075, vertices=6, radius1=1, radius2=.25)
        e.scale = (e.scale.x, e.scale.y*.3, e.scale.z); hd.append(e)
        # presa superior (curta, quebrada)
        hd.append(along("primitive_cone_add", tusk, H(.42, -.1, .06*sx), H(.44, -.02, .1*sx), .018, vertices=6, radius1=1, radius2=.5))
    hd.append(prim("primitive_uv_sphere_add", dark, H(.38, -.12), (.06, .14, .02), segments=10, ring_count=6))  # boca
    # placa-aríete: calota de ferro sobre a testa e chapa no focinho, rebitadas, com um cravo achatado
    side = d.cross(up).normalized()
    for t, u, sc in ((.13, .075, (.21, .2, .1)), (.36, .045, (.12, .13, .06))):
        c = H(t, u); o = prim("primitive_uv_sphere_add", iron, c, sc, segments=18, ring_count=10)
        o.rotation_euler = d.to_track_quat('Y', 'Z').to_euler(); hd.append(o)
        for k in range(12):
            a = 2*math.pi*k/12
            q = c + side*sc[0]*.86*math.cos(a) + d*sc[1]*.86*math.sin(a) + up*sc[2]*.55
            hd.append(prim("primitive_uv_sphere_add", brass if k % 6 == 0 else iron, q, (.017, .017, .013), segments=6, ring_count=4))
    hd.append(along("primitive_cone_add", iron, H(.12, .16), H(.2, .22), .05, vertices=6, radius1=1, radius2=.4))
    hd.append(along("primitive_cylinder_add", leather, H(-.02, .12, .17), H(.3, -.08, .14), .018, vertices=5))  # correias da placa
    hd.append(along("primitive_cylinder_add", leather, H(-.02, .12, -.17), H(.3, -.08, -.14), .018, vertices=5))
    for o in hd:
        o.location = hb + (o.location - hb)*1.2; o.scale = o.scale*1.2
    R.rigid(hd, "head")
    jb, jt = P("jaw"), P("jaw", 1); jd = (jt - jb).normalized()
    jw = [along("primitive_cone_add", skin, jb + jd*.04, jt, .1, vertices=12, radius1=1, radius2=.55)]
    jw[0].scale = (jw[0].scale.x, jw[0].scale.y*.55, jw[0].scale.z)
    for sx in (1, -1):  # presas de baixo: a direita inteira curvada para cima, a esquerda partida
        b0 = jt - jd*.1 + Vector((.07*sx, 0, .02)); pts = [b0]; v = Vector((.35*sx, -.3, 1)).normalized()
        nseg = 4 if sx < 0 else 2
        for k in range(nseg):
            v = (Matrix.Rotation(.35, 3, 'X') @ v).normalized() if False else (v + Vector((0, .25, -.05))).normalized()
            pts.append(pts[-1] + v*.07)
        for k in range(len(pts)-1):
            r0 = .03*(1 - k/(nseg + 1))
            jw.append(along("primitive_cone_add", tusk, pts[k], pts[k+1], r0, vertices=6, radius1=1, radius2=.75))
        if sx > 0:
            jw.append(prim("primitive_uv_sphere_add", tusk, pts[-1], (.014, .014, .01), segments=6, ring_count=4))
    for o in jw:
        o.location = hb + (o.location - hb)*1.2; o.scale = o.scale*1.2
    R.rigid(jw, "jaw")
    return R, INFO

# ======================================================================= animações
BASE = {"neck": {"x": 4}, "head": {"x": 4}, "tail1": {"x": -10}, "tail2": {"x": -10}}
def M(*p): return merge(BASE, *p)

def gallop(p):
    """Galope de investida: pares quase juntos (dianteiras .0/.1, traseiras .5/.6)."""
    return merge(leg_cycle("L", True, p % 1, amp=40, lift=1.2), leg_cycle("R", True, (p + .9) % 1, amp=40, lift=1.2),
                 leg_cycle("R", False, (p + .5) % 1, amp=36, lift=1.1), leg_cycle("L", False, (p + .4) % 1, amp=36, lift=1.1))

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; s, c = math.sin(t), math.cos(t)
        idle.append(M({"spine": {"x": 1.2*s}, "chest": {"x": -1.2*s}, "neck": {"x": 4 + 3*c}, "head": {"x": 6*s, "z": 6*math.sin(t*.5)},
                       "jaw": {"x": 3 + 3*max(0, s)}, "tail1": {"z": 15*s}, "tail2": {"z": 20*math.sin(t - 1)}}))
    walk = []
    for i in range(8):
        p = i/8; s1 = math.sin(p*2*math.pi); s2 = math.sin(p*4*math.pi)
        legs = merge(leg_cycle("L", True, p, amp=18, lift=.8, fold=.7), leg_cycle("R", False, (p + .05) % 1, amp=16, lift=.8, fold=.7),
                     leg_cycle("R", True, (p + .5) % 1, amp=18, lift=.8, fold=.7), leg_cycle("L", False, (p + .55) % 1, amp=16, lift=.8, fold=.7))
        walk.append(M(legs, {"chest": {"z": 4*s1, "y": 2*s1}, "hips": {"z": -4*s1, "y": -3*s1}, "neck": {"x": 2*s2},
                             "head": {"x": 3*s2, "z": -5*s1}, "tail1": {"z": 14*s1}, "tail2": {"z": 18*s1}}))
    # chifrada: abaixa a cabeça e golpeia para cima e para o lado com as presas
    low = M({"hips": {"x": -4}, "neck": {"x": 18}, "head": {"x": 22}, "jaw": {"x": 4},
             "upper_arm.L": {"x": 12}, "upper_arm.R": {"x": 12}, "forearm.L": {"bend": -16}, "forearm.R": {"bend": -16},
             "thigh.L": {"x": -10}, "thigh.R": {"x": -10}, "shin.L": {"bend": 12}, "shin.R": {"bend": 12}, "root": (0, .08, 0)})
    gore = M({"hips": {"x": -6}, "chest": {"x": -6, "z": 10}, "neck": {"x": -10, "z": 10}, "head": {"x": -14, "z": 18, "y": -18}, "jaw": {"x": 22},
              "upper_arm.L": {"x": -24}, "upper_arm.R": {"x": -6}, "forearm.L": {"bend": -30}, "hand.L": {"bend": 40},
              "thigh.L": {"x": 18}, "thigh.R": {"x": 22}, "root": (0, -.3, 0)})
    follow = merge(gore, {"head": {"z": 10, "y": -6}, "neck": {"z": 6}, "jaw": {"x": -10}, "root": (0, -.28, 0)})
    attack = keys_to_frames([(0, M()), (.28, low), (.46, gore), (.6, follow), (1, M())], 8)
    # raspa a pata (loop): cabeça baixa, dianteira direita cava para trás, bufa
    scrape = []
    for i in range(6):
        u = i/6; up = max(0, math.sin(u*2*math.pi)); sw = math.cos(u*2*math.pi)
        scrape.append(M({"hips": {"x": -3}, "neck": {"x": 16}, "head": {"x": 18 + 3*up, "z": 4*sw}, "jaw": {"x": 3 + 5*up},
                         "upper_arm.L": {"x": -6 - 18*up + 20*(1 - up)*max(0, -sw)}, "forearm.L": {"bend": -40*up},
                         "hand.L": {"bend": 50*up},
                         "upper_arm.R": {"x": 6}, "forearm.R": {"bend": -8}, "thigh.L": {"x": -8}, "thigh.R": {"x": -8},
                         "shin.L": {"bend": 10}, "shin.R": {"bend": 10}, "tail1": {"x": 20, "z": 10*sw},
                         "gb": ["hand.R", "foot.L", "foot.R"]}))
    # investida (loop): galope com a cabeça baixa e a placa à frente
    charge = []
    for i in range(6):
        p = i/6; s1 = math.sin(p*2*math.pi); c1 = math.cos(p*2*math.pi)
        charge.append(M(gallop(p), {"hips": {"x": 4*s1}, "chest": {"x": -4*s1}, "neck": {"x": 16}, "head": {"x": 14 - 4*s1},
                                    "jaw": {"x": 6}, "tail1": {"x": 40}, "tail2": {"x": 10}, "ground": .03 + .05*max(0, c1)}))
    # tonto (loop): patas abertas, cambaleia, cabeça pendurada girando
    stun = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t)
        stun.append(M({"hips": {"y": 6*s, "z": 4*c}, "chest": {"y": -5*s, "z": -5*c}, "neck": {"x": 24, "z": 12*s}, "head": {"x": 18 + 6*c, "z": 14*s, "y": 10*c},
                       "jaw": {"x": 14 + 6*s}, "upper_arm.L": {"y": 10, "x": -8}, "upper_arm.R": {"y": -10, "x": -8},
                       "forearm.L": {"bend": -10}, "forearm.R": {"bend": -10}, "thigh.L": {"y": 8, "x": 6}, "thigh.R": {"y": -8, "x": 6},
                       "shin.L": {"bend": 14}, "shin.R": {"bend": 14}, "tail1": {"x": -20}, "tail2": {"z": 20*s}}))
    hitp = M({"hips": {"z": 6}, "chest": {"z": -8, "x": -4}, "neck": {"x": -14, "z": 10}, "head": {"x": -14}, "jaw": {"x": 20},
              "upper_arm.L": {"x": 10}, "upper_arm.R": {"x": 6}, "tail1": {"x": 10}, "root": (0, .06, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: cambaleia, ajoelha na frente, tomba de lado e incha
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
    # inchaço progressivo da barriga nos últimos quadros
    for i, k in enumerate((0, 0, 0, 0, 0, .05, .2, .45, .75, 1)):
        death[i]["bloat"] = {"belly": (1 + .45*k, 1 + .12*k, 1 + .45*k)}
    return {"idle": idle, "walk": walk, "attack": attack, "scrape": scrape, "charge": charge, "stun": stun, "hit": hit, "death": death}
