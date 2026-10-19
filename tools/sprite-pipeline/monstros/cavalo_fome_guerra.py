# Cavalos dos Cavaleiros do Apocalipse: montarias de guerra com barda (armadura de cobertura).
# Mesma base quadrúpede dos monstros (quad.py), em escala de cavalo (~1,5 m de cernelha).
# Variantes (cada uma com silhueta e material próprios, não é só troca de cor):
#   cavalo_fome   (Agonia): cavalo morto-vivo esquelético. Costelas e quadril à vista, crânio de osso com
#                 chifres curtos, crista de vértebras no pescoço, manto de mortalha verde-amarelado rasgado
#                 na barda, cadeia de vértebras na cauda, medalhão de caveira com a balança.
#   cavalo_guerra (Danação): cavalo de guerra vermelho-sangue e musculoso. Chanfro de aço com espigão,
#                 barda de placas sobrepostas e enferrujadas com cravos, capa de couro rasgada,
#                 crina de ferro, medalhão de espada.
# Brilho: no máximo um emissivo por montaria (olhos de brasa).
import bpy, math, random
from mathutils import Vector, Matrix
from mrig import *
from quad import *

INFO = {"px": 384, "target_z": .8, "rim": (.9, .62, .4), "colors": 40, "samples": 48,
        "fps": {"idle": 6, "walk": 10, "attack": 12, "hit": 12, "death": 10},
        "loops": ("idle", "walk")}

VARIANTS = {
    "cavalo_fome": {"coat": (.09, .085, .05), "sick": (.25, .26, .08), "bone": (.5, .47, .33),
                    "cloth": (.28, .3, .1), "ribs": 1.0, "muscle": 0.0, "crest": "ossos", "eye": (.5, 1, .15),
                    "rim": (.7, .9, .45), "symbol": "balanca", "tail": "vertebras"},
    "cavalo_guerra": {"coat": (.2, .03, .022), "sick": (.07, .01, .008), "bone": (.1, .1, .11),
                      "cloth": (.05, .045, .045), "ribs": .1, "muscle": 1.0, "crest": "espinhos", "eye": (1, .3, .05),
                      "rim": (.95, .45, .3), "symbol": "espada", "tail": "corrente"},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
    INFO["rim"] = V["rim"]

BACK = 1.45
def bones():
    return quad_bones(sh=1.5, hip=1.45, y_sh=-.75, y_hip=.7, w=.2, wh=.2, back=BACK, neck=(-1.3, 2.0),
                      head=(-1.9, 1.85), jaw=((-1.6, 1.86), (-1.92, 1.78)), tail=((1.15, 1.2), (1.4, .85)))

def cloth_rags(rings, mat_, n, seed, a_rng=(15, 165), length=.3):
    """Tiras pendentes na borda de baixo de um manto: cada uma com comprimento diferente."""
    rr = random.Random(seed); out = []
    for k in range(n):
        y = -.7 + .9*k/max(1, n - 1)
        ri = min(range(len(rings)), key=lambda i: abs(rings[i][0].y - y))
        p, nrm = surf(rings[ri], math.radians(rr.uniform(*a_rng)))
        L = length*rr.uniform(.35, 1.0)
        out.append(along("primitive_cube_add", mat_, p - Vector((0, 0, .02)), p - Vector((0, 0, .02 + L)), .022))
    return out

def build():
    # ---- materiais
    if V["name"] == "cavalo_fome":
        coat = stained("h_pelo_morto", V["coat"], stain=(.14, .12, .04), amount=.5, scale=4, rough=.8, blotch=(.04, .04, .03),
                       blotch_amt=.5, grime=1.5, dirt=.6)
        bone = stained("h_osso", V["bone"], stain=(.3, .3, .1), amount=.45, scale=6, rough=.45, grime=.6)
        cloth = stained("h_mortalha", V["cloth"], stain=(.07, .08, .03), amount=.8, scale=3, rough=.85, grime=1.4, dirt=.7)
        iron = stained("h_ferro_velho", (.1, .1, .09), stain=(.2, .22, .08), amount=.6, scale=5, metal=.7, rough=.6, grime=.9)
        brass = stained("h_latao_velho", (.35, .3, .14), stain=(.2, .22, .06), amount=.5, scale=6, metal=.8, rough=.5, grime=.7)
    else:
        coat = stained("h_pelo", V["coat"], stain=V["sick"], amount=.4, scale=4, rough=.7, blotch=(.12, .02, .015),
                       blotch_amt=.5, grime=1.1, dirt=.45)
        bone = stained("h_osso_negro", V["bone"], stain=(.14, .03, .02), amount=.3, scale=6, rough=.5, grime=.4)
        cloth = stained("h_capa", V["cloth"], stain=(.14, .02, .01), amount=.5, scale=3, rough=.85, grime=1.0, dirt=.6)
        iron = stained("h_placa_guerra", (.2, .2, .2), stain=(.36, .14, .05), amount=.6, scale=5, metal=.85, rough=.42, grime=.6)
        brass = stained("h_cravo", (.3, .28, .26), stain=(.3, .12, .04), amount=.45, scale=6, metal=.9, rough=.35, grime=.5)
    mane = mat("h_crina", tuple(c*.55 for c in V["coat"]), 0, .9, dirt=.6)
    hoof = mat("h_casco", (.04, .035, .04), 0, .4, dirt=.5, grime=.5)
    leather = stained("h_couro", (.1, .06, .035), stain=(.15, .03, .015), amount=.4, scale=4, rough=.7, grime=.6)
    dark = mat("h_boca", (.015, .008, .008), 0, .5)
    eye = mat("h_olho", V["eye"], emit=V["eye"], strength=40)

    R = Rig("cavalo", bones(), ground=.03, ground_bones=PAWS)
    P = R.P

    # ---- corpo: Agonia magra e fundo (costelas à vista); Danação larga, com musculatura
    if V["name"] == "cavalo_fome":
        keys = [(.95, 1.2, .24, .3), (.65, 1.22, .3, .36), (.3, 1.2, .32, .4), (-.1, 1.16, .3, .4),
                (-.45, 1.18, .28, .38), (-.75, 1.4, .24, .3), (-.95, 1.62, .2, .26), (-1.1, 1.85, .16, .18),
                (-1.22, 2.0, .12, .13)]
    else:
        keys = [(.95, 1.24, .38, .44), (.65, 1.24, .5, .52), (.3, 1.22, .56, .6), (-.1, 1.18, .54, .6),
                (-.45, 1.2, .5, .54), (-.75, 1.4, .38, .4), (-.95, 1.62, .3, .34), (-1.1, 1.85, .22, .23),
                (-1.22, 2.0, .16, .16)]
    rings = ring_path(keys)
    ribs, muscle = V["ribs"], V["muscle"]
    def rad(i, a, r):
        y = r[0].y; f = 1.0; side = abs(math.cos(a))
        if -.5 < y < .25 and math.sin(a) < .7:   # costelas: sulcos fundos e cinto de quadril magro
            f *= 1 - .3*ribs*side*(.5 - .5*math.cos(y*2*math.pi/.14))*min(1, (y + .5)/.1)
        if .35 < y < .8 and .2 < math.sin(a) < .9 and muscle:   # anca
            f *= 1 + .12*muscle*max(0, 1 - abs(y - .6)/.25)
        if -.95 < y < -.55 and .2 < math.sin(a) < .9 and muscle:   # ombro e peitoral
            f *= 1 + .1*muscle*max(0, 1 - abs(y + .75)/.22)
        if .2 < y < .5 and math.sin(a) > .85:   # vértebras
            f *= 1 + .05*max(0, math.cos(y*2*math.pi/.12))**3
        return f
    body = loft("cavalo_corpo", rings, coat, seg=36, rad=rad)
    parts = [body]
    parts += tufts(rings, mane, 50, (60, 120), (.1, .9), .14, .025, 21, back=.5, down=-.1)
    R.bind(body, ["hips", "spine", "chest", "neck", "thigh.L", "thigh.R", "upper_arm.L", "upper_arm.R"], power=4)

    # ---- pescoço: crina ou cristas de osso/espinho no topo
    nk = ring_path([(-.95, 1.62, .12, .14), (-1.22, 2.0, .06, .07)], .03)
    if V["crest"] == "ossos":
        # vértebras espetadas no alto do pescoço, afiladas para trás
        crest = []
        for k in range(12):
            t = k/11; p = Vector((0, -.95 - .27*t, 1.62 + .38*t)) + Vector((0, 0, .18*math.sin(t*math.pi)))
            crest.append(along("primitive_cone_add", bone, p, p + Vector((0, .05, .14 - .06*t)), .035 - .015*t,
                               vertices=6, radius1=1, radius2=.2))
        R.rigid(crest, "neck")
    else:
        mn = join(tufts(nk, mane, 44, (-40, 40), (0, 1), .26, .03, 23, back=-.2, down=.6, lmin=.6))
        R.bind(mn, ["neck", "head"])
        spikes = []
        for k in range(9):
            t = k/8; p = Vector((0, -.9 - .35*t, 1.6 + .42*t))
            spikes.append(along("primitive_cone_add", iron, p, p + Vector((0, .02, .15)), .03, vertices=6, radius1=1, radius2=.1))
        R.rigid(spikes, "neck")

    # ---- pernas: Agonia com juntas de osso visíveis, Danação com canela grossa
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr, tp = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}"), P(f"hand.{n}", 1)
        k = 1.0 if muscle else .8
        fl = limb(f"pata_f{n}", [(*(sh + Vector((0, .03, .05))), .19*k), (*sh.lerp(el, .5), .14*k), (*el, .09*k),
                                 (*el.lerp(wr, .5), .065*k), (*wr, .058*k), (*wr.lerp(tp, .6), .05*k), (*tp, .05*k)], coat)
        R.bind(fl, ["chest", f"upper_arm.{n}", f"forearm.{n}", f"hand.{n}"])
        hp, kn, hk, ft = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        hl = limb(f"pata_t{n}", [(*(hp + Vector((0, -.04, .05))), .24*k), (*hp.lerp(kn, .4) + Vector((0, .05, 0)), .15*k),
                                 (*kn, .08*k), (*kn.lerp(hk, .5), .06*k), (*hk, .05*k), (*hk.lerp(ft, .6), .045*k), (*ft, .045*k)], coat)
        R.bind(hl, ["hips", f"thigh.{n}", f"shin.{n}", f"foot.{n}"])
        for b, tip in ((f"hand.{n}", tp), (f"foot.{n}", ft)):   # casco
            R.rigid([along("primitive_cone_add", hoof, tip + Vector((0, 0, .02)), tip - Vector((0, .02, .06)), .05, vertices=8,
                           radius1=1, radius2=.85)], b)
        R.rigid([prim("primitive_uv_sphere_add", bone if ribs > .5 else coat, el + Vector((0, .04, 0)), (.05, .05, .06),
                      segments=8, ring_count=6)], f"forearm.{n}")
        if ribs > .5:   # joelhos e jarretes de osso
            R.rigid([prim("primitive_uv_sphere_add", bone, kn, (.05, .05, .055), segments=8, ring_count=6)], f"shin.{n}")
            R.rigid([prim("primitive_uv_sphere_add", bone, hk, (.045, .045, .05), segments=8, ring_count=6)], f"foot.{n}")

    # ---- cauda: vértebras em fileira (Agonia) ou corrente com espinhos (Danação)
    t1, t2, t3 = P("tail1"), P("tail2"), P("tail2", 1)
    if V["tail"] == "vertebras":
        vb = []
        for k in range(8):
            t = k/7; p = t1.lerp(t2, .0) + (t3 - t1)*t
            vb.append(prim("primitive_uv_sphere_add", bone, p, (.035 - .012*t, .035 - .012*t, .04 - .014*t), segments=8, ring_count=6))
        R.bind(join(vb), ["hips", "tail1", "tail2"])
    else:
        ch = []
        for k in range(10):
            t = k/9; p = t1 + (t3 - t1)*t
            ch.append(prim("primitive_torus_add", iron, p, (1, 1, 1), major_radius=.03, minor_radius=.008,
                           major_segments=8, minor_segments=4, rot=(90, 0, 0)))
            if k % 3 == 2:
                ch.append(along("primitive_cone_add", iron, p, p + Vector((0, .03, .06)), .02, vertices=5, radius1=1, radius2=.1))
        R.rigid(ch, "tail2")
        tl = limb("cauda", [(*t1, .05), (*t2, .035), (*t2.lerp(t3, .6), .03), (*t3, .015)], coat)
        R.bind(join([tl] + tufts(ring_path([(t1.y, t1.z, .08, .08), (t2.y, t2.z, .05, .05), (t3.y, t3.z, .03, .03)], .03),
                                 mane, 40, (0, 360), (0, 1), .3, .025, 27, back=1, down=.4, lmin=.6)), ["hips", "tail1", "tail2"])

    # ---- cabeça
    hd = []
    if V["name"] == "cavalo_fome":
        # crânio de cavalo: osso, órbitas fundas, focinho nu e dentes à vista
        hd.append(prim("primitive_uv_sphere_add", bone, (0, -1.6, 1.97), (.14, .2, .15), segments=16, ring_count=10))
        hd.append(along("primitive_cone_add", bone, Vector((0, -1.7, 1.93)), Vector((0, -2.0, 1.8)), .1, vertices=12, radius1=1, radius2=.6))
        for s in (1, -1):
            hd.append(prim("primitive_uv_sphere_add", dark, (.09*s, -1.6, 2.0), (.04, .045, .04), segments=10, ring_count=6))
            hd.append(prim("primitive_uv_sphere_add", eye, (.095*s, -1.66, 2.02), (.02, .014, .018), segments=8, ring_count=6))
            hd.append(along("primitive_cone_add", bone, (.08*s, -1.45, 2.14), (.14*s, -1.36, 2.26), .028, vertices=5, radius1=1, radius2=.1))
            for k in range(3):   # dentes
                y = -1.78 + .05*k
                hd.append(along("primitive_cone_add", bone, (.045*s, y, 1.78), (.045*s, y, 1.7), .012, vertices=4, radius1=1, radius2=0))
        hd.append(prim("primitive_uv_sphere_add", dark, (0, -2.0, 1.82), (.045, .04, .04), segments=8, ring_count=6))
        R.rigid(hd, "head")
        jw = [along("primitive_cone_add", bone, Vector((0, -1.62, 1.84)), Vector((0, -1.9, 1.77)), .07, vertices=10, radius1=1, radius2=.6)]
        R.rigid(jw, "jaw")
    else:
        # cabeça de guerra: crânio coberto, chanfro de aço com espigão na testa e placas laterais
        hd.append(prim("primitive_uv_sphere_add", coat, (0, -1.6, 1.97), (.15, .22, .16), segments=16, ring_count=10))
        hd.append(along("primitive_cone_add", coat, Vector((0, -1.7, 1.93)), Vector((0, -2.0, 1.8)), .12, vertices=14, radius1=1, radius2=.8))
        for s in (1, -1):
            hd.append(prim("primitive_uv_sphere_add", eye, (.105*s, -1.68, 2.01), (.024, .016, .02), segments=8, ring_count=6))
            hd.append(prim("primitive_uv_sphere_add", iron, (.1*s, -1.6, 2.02), (.07, .12, .04), segments=10, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", dark, (0, -2.0, 1.8), (.05, .05, .045), segments=10, ring_count=6))
        R.rigid(hd, "head")
        ch = []
        ch.append(along("primitive_cone_add", iron, Vector((0, -1.5, 2.18)), Vector((0, -1.42, 2.36)), .04, vertices=6, radius1=1, radius2=.1))
        for k in range(4):  # chanfro: placas de aço sobre a cara
            y = -1.85 + .11*k
            ch.append(prim("primitive_uv_sphere_add", iron, (0, y, 1.95 + .04*k), (.1, .1, .03), segments=12, ring_count=6))
        for s in (1, -1):
            ch.append(prim("primitive_uv_sphere_add", iron, (.13*s, -1.55, 1.98), (.05, .1, .07), segments=10, ring_count=6))
        ch.append(prim("primitive_torus_add", iron, (0, -1.8, 1.9), (1, 1, 1), major_radius=.13, minor_radius=.012,
                       major_segments=18, minor_segments=5, rot=(80, 0, 0)))
        R.rigid(ch, "head")
    jaw_rig = [prim("primitive_uv_sphere_add", dark, (0, -1.74, 1.79), (.05, .06, .03), segments=8, ring_count=6)]
    R.rigid(jaw_rig, "jaw")

    # ---- barda: manto de mortalha (Agonia) ou placas sobrepostas (Danação)
    rv = random.Random(31)
    if V["name"] == "cavalo_fome":
        # manto rasgado: tubo de tecido por cima do lombo, tiras pendentes na borda
        mrings = ring_path([(y, z + .03, rx + .06, rz + .05) for (y, z, rx, rz) in keys[1:-3]])
        man = loft("agonia_manto", mrings, cloth, seg=36,
                   rad=lambda i, a, r: (.9 if math.sin(a) < .15 else 1.0) * (1 - .06*abs(math.sin(i*1.7))))
        R.bind(man, ["hips", "spine", "chest"], power=4)
        R.rigid(cloth_rags(mrings, cloth, 12, 41, (25, 155), .34), "spine")
        # medalhão de caveira na altura do peito e balança no quarto traseiro
        med = []
        for ang, kind in ((62, "caveira"), (118, "balanca")):
            ri = min(range(len(rings)), key=lambda i: abs(rings[i][0].y - -.2))
            p, nrm = surf(rings[ri], math.radians(ang))
            med.append(prim("primitive_cylinder_add", brass, p + nrm*.09, (.12, .12, .014), vertices=18,
                            rot=tuple(math.degrees(x) for x in nrm.to_track_quat('Z', 'Y').to_euler())))
            c = p + nrm*.11
            if kind == "caveira":
                med.append(prim("primitive_uv_sphere_add", bone, c, (.07, .075, .06), segments=10, ring_count=8))
                for s in (1, -1):
                    med.append(prim("primitive_uv_sphere_add", dark, c + Vector((.03*s, -.06, .01)), (.018, .018, .016), segments=6, ring_count=4))
            else:
                med.append(along("primitive_cylinder_add", iron, c - Vector((0, 0, .08)), c + Vector((0, 0, .08)), .006, vertices=6))
                med.append(along("primitive_cylinder_add", iron, c + Vector((-.07, 0, .05)), c + Vector((.07, 0, .05)), .005, vertices=6))
                for sx in (-.07, .07):
                    med.append(prim("primitive_cylinder_add", brass, c + Vector((sx, 0, -.03)), (.035, .035, .006), vertices=14))
        R.rigid(med, "spine")
        # correntes presas no peitoral
        links = []
        for k in range(12):
            t = k/11
            p = P("chest") + Vector((-.25 + .5*t, -.45 + .12*math.sin(t*math.pi), .15 - .6*t*t))
            links.append(prim("primitive_torus_add", iron, p, (1, 1, 1), major_radius=.025, minor_radius=.007,
                              major_segments=8, minor_segments=4, rot=(rv.uniform(0, 90), 0, rv.uniform(0, 90))))
        R.rigid(links, "chest")
    else:
        # placas de aço sobrepostas (escamas), com cravos, em duas fileiras por lado
        plate = iron
        rust = stained("h_ferrugem", (.22, .09, .04), stain=(.4, .15, .05), amount=.6, scale=4, metal=.6, rough=.6, grime=.5)
        rows = []
        for row, y0 in enumerate((-.8, -.35, .1, .55)):
            for k in range(7):
                y = y0 + .15*(k % 2) + .02*row
                ri = min(range(len(rings)), key=lambda i: abs(rings[i][0].y - y))
                for side in (62, 118):
                    p, nrm = surf(rings[ri], math.radians(side + rv.uniform(-7, 7)))
                    pl = prim("primitive_uv_sphere_add", plate if (k + row) % 3 else rust, p + nrm*.07,
                              (.2, .24, .045), segments=10, ring_count=6)
                    pl.rotation_euler = (nrm.to_track_quat('Z', 'Y').to_matrix() @ Matrix.Rotation(rv.uniform(-.25, .25), 3, 'Z')).to_euler()
                    rows.append(pl)
                    for dy in (-.05, .05):
                        rows.append(prim("primitive_uv_sphere_add", brass, p + nrm*.075 + Vector((0, dy, 0)), (.012, .012, .01),
                                         segments=6, ring_count=4))
        R.rigid(rows, "spine")
        # capa de couro rasgada, pendendo do lombo até o jarrete
        cape = loft("danacao_capa", ring_path([(y, z - .04, rx + .06, rz + .02) for (y, z, rx, rz) in keys[2:-4]]), cloth, seg=32,
                    rad=lambda i, a, r: 1.0 if math.sin(a) > .4 else .12 + .4*(1 - math.sin(a)))
        R.bind(cape, ["hips", "spine", "chest"], power=4)
        R.rigid(cloth_rags(ring_path([(y, z, rx, rz) for (y, z, rx, rz) in keys[2:-4]]), cloth, 10, 42, (30, 150), .28), "spine")
        # medalhão de espada no peito
        med = []
        for ang in (62, 118):
            ri = min(range(len(rings)), key=lambda i: abs(rings[i][0].y - -.1))
            p, nrm = surf(rings[ri], math.radians(ang))
            med.append(prim("primitive_cylinder_add", brass, p + nrm*.08, (.11, .11, .014), vertices=20,
                            rot=tuple(math.degrees(x) for x in nrm.to_track_quat('Z', 'Y').to_euler())))
            c = p + nrm*.1
            med.append(along("primitive_cube_add", iron, c - Vector((0, 0, .09)), c + Vector((0, 0, .09)), .014))
            med.append(along("primitive_cube_add", brass, c + Vector((-.05, 0, -.08)), c + Vector((.05, 0, -.08)), .012))
            med.append(along("primitive_cylinder_add", leather, c + Vector((0, 0, -.1)), c + Vector((0, 0, -.14)), .009, vertices=6))
        R.rigid(med, "spine")

    return R, INFO

# ======================================================================= animações
# postura base: cabeça alta, cauda relaxada
BASE = {"neck": {"x": -4}, "head": {"x": 2}, "tail1": {"x": -10}, "tail2": {"x": -12},
        "upper_arm.L": {"x": -2}, "upper_arm.R": {"x": -2}, "thigh.L": {"x": 2}, "thigh.R": {"x": 2}}
def M(*p): return merge(BASE, *p)

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; s, c = math.sin(t), math.cos(t)
        idle.append(M({"spine": {"x": 1.2*s}, "chest": {"x": -1.2*s}, "neck": {"x": 2*c}, "head": {"x": 3*s, "z": 4*math.sin(t*.5)},
                       "tail1": {"z": 8*s}, "tail2": {"z": 12*math.sin(t - .8)}}))
    walk = []
    for i in range(8):
        p = i/8; s2 = math.sin(p*4*math.pi); s1 = math.sin(p*2*math.pi)
        legs = merge(leg_cycle("L", True, p, amp=22), leg_cycle("R", False, p, amp=22),
                     leg_cycle("R", True, (p + .5) % 1, amp=22), leg_cycle("L", False, (p + .5) % 1, amp=22))
        walk.append(M(legs, {"chest": {"z": 3*s1, "x": 2*s2}, "hips": {"z": -2.5*s1, "y": 2*s1}, "neck": {"x": -3*s2},
                             "head": {"x": 2*s2, "z": -3*s1}, "tail1": {"z": 10*s1, "x": -4}, "tail2": {"z": 14*s1}}))
    # empinada e golpe: patas da frente para cima, depois desabam
    rear = M({"neck": {"x": -30}, "head": {"x": -20}, "upper_arm.L": {"x": -75}, "upper_arm.R": {"x": -70},
              "forearm.L": {"bend": -30}, "forearm.R": {"bend": -30}, "hand.L": {"bend": 40}, "hand.R": {"bend": 40},
              "thigh.L": {"x": -20}, "thigh.R": {"x": -20}, "shin.L": {"bend": 25}, "shin.R": {"bend": 25},
              "tail1": {"x": -30}, "root": (0, .2, .08)})
    slam = M({"neck": {"x": 14}, "head": {"x": 10}, "upper_arm.L": {"x": 12}, "upper_arm.R": {"x": 8},
              "forearm.L": {"bend": -10}, "thigh.L": {"x": 8}, "thigh.R": {"x": 10}, "root": (0, -.1, -.02)})
    attack = keys_to_frames([(0, M()), (.3, rear), (.5, rear), (.66, slam), (.82, merge(slam, {"head": {"x": 4}})), (1, M())], 8)
    hitp = M({"hips": {"z": 6}, "chest": {"z": -8, "x": -5}, "neck": {"x": -20, "z": 10}, "head": {"x": -16},
              "upper_arm.L": {"x": 12}, "upper_arm.R": {"x": 8}, "thigh.L": {"x": -8}, "tail1": {"x": -20}, "root": (0, .1, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    buckle = M({"hips": {"x": -8, "y": 10}, "neck": {"x": 16}, "head": {"x": 16},
                "upper_arm.L": {"x": 30}, "upper_arm.R": {"x": 22}, "forearm.L": {"bend": -70}, "forearm.R": {"bend": -60},
                "hand.L": {"bend": 50}, "hand.R": {"bend": 40},
                "thigh.L": {"x": -40}, "thigh.R": {"x": -30}, "shin.L": {"bend": 60}, "shin.R": {"bend": 50},
                "foot.L": {"bend": -40}, "foot.R": {"bend": -30}, "tail1": {"x": 20}})
    tilt = merge(buckle, {"hips": {"y": 45}, "gb": BODY + PAWS, "ground": .1})
    side = {"hips": {"y": 88}, "neck": {"x": 10, "y": 6}, "head": {"x": -10, "y": 6},
            "upper_arm.L": {"x": -20, "y": 4}, "upper_arm.R": {"x": -30, "y": -14}, "forearm.L": {"bend": -20}, "forearm.R": {"bend": -8},
            "hand.L": {"bend": 20}, "hand.R": {"bend": 10},
            "thigh.L": {"x": 10, "y": 4}, "thigh.R": {"x": 22, "y": -12}, "shin.L": {"bend": 24}, "shin.R": {"bend": 8},
            "foot.L": {"bend": -10}, "foot.R": {"bend": -6}, "tail1": {"x": -20, "z": 10}, "tail2": {"z": 10},
            "gb": BODY, "ground": .2}
    death = keys_to_frames([(0, hitp), (.25, buckle), (.48, tilt), (.7, side), (.84, merge(side, {"thigh.R": {"x": 10}})),
                            (1, merge(side, {"jaw": {"x": 6}}))], 10)
    return {"idle": idle, "walk": walk, "attack": attack, "hit": hit, "death": death}
