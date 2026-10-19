# Cavalo Esqueleto (montaria): cavalo morto que a Vigília e a Legião reanimaram para carregar. Carcaça com
# as costelas à mostra, pele de couro seco esticada, crina de cabelo ralo, olhos vazios, dentes de fora.
# Sela de couro com estribos de ferro e cilha. Sem cavaleiro: a pose de montado vem depois, por camada.
# Brilho: uma brasa fraca nas órbitas (o único emissivo). Animações: idle e walk (trote).
import bpy, math, random
from mathutils import Vector
from mrig import *
from quad import *

INFO = {"px": 256, "target_z": .9, "rim": (.7, .85, .4), "colors": 40, "samples": 40,
        "fps": {"idle": 6, "walk": 10}, "loops": ("idle", "walk")}

BACK = 1.22

# Variantes (render: cavalo_esqueleto:corcel_negro). O padrão é o Cavalo Esqueleto de barda de ferro.
VARIANTS = {
    "corcel_negro": {"hide": (.06, .05, .05), "bone": (.2, .18, .16), "iron": (.05, .05, .055),
                     "steel": (.16, .15, .15), "mane": (.03, .025, .025)},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
def bones():
    B = quad_bones(sh=1.2, hip=1.12, y_sh=-.72, y_hip=.66, w=.15, wh=.14, back=BACK, neck=(-.95, 1.55),
                   head=(-1.42, 1.22), jaw=((-1.0, 1.2), (-1.3, 1.13)), tail=((.98, 1.2), (1.08, .9)))
    for s, n in ((1, "L"), (-1, "R")):
        w, wh = .15*s, .14*s
        B[f"upper_arm.{n}"] = ((w*.9, -.72, 1.2), (w, -.66, .62), "chest")
        B[f"forearm.{n}"] = ((w, -.66, .62), (w, -.7, .2), f"upper_arm.{n}")
        B[f"hand.{n}"] = ((w, -.7, .2), (w, -.76, .025), f"forearm.{n}")
        B[f"thigh.{n}"] = ((wh*.9, .66, 1.12), (wh, .55, .6), "hips")
        B[f"shin.{n}"] = ((wh, .55, .6), (wh, .68, .26), f"thigh.{n}")
        B[f"foot.{n}"] = ((wh, .68, .26), (wh, .66, .025), f"shin.{n}")
    return B

def build():
    hide = stained("ca_couro", V.get("hide", (.3, .24, .17)), stain=(.2, .05, .02), amount=.5, scale=6, rough=.65, grime=1.0, dirt=.4)
    bone = stained("ca_osso", V.get("bone", (.5, .45, .36)), stain=(.2, .05, .02), amount=.45, scale=7, rough=.7, grime=.6)
    mane = mat("ca_crina", V.get("mane", (.08, .06, .05)), 0, .85, dirt=.6)
    leather = stained("ca_sela", (.13, .07, .04), stain=(.2, .03, .01), amount=.5, scale=4, rough=.4, grime=.8)
    iron = stained("ca_ferro", V.get("iron", (.12, .1, .09)), stain=(.3, .1, .03), amount=.55, scale=6, metal=.8, rough=.5, grime=.5)
    steel = stained("ca_aco", V.get("steel", (.42, .4, .38)), stain=(.25, .05, .02), amount=.45, scale=6, metal=.95, rough=.32, grime=.35)
    eye = mat("ca_brasa", (1, .42, .1), emit=(1, .42, .1), strength=12)
    hole = mat("ca_buraco", (.01, .006, .005), 0, .9)

    R = QRig("cavalo", bones(), ground=.03, ground_bones=PAWS)
    P = R.P

    # ---- corpo: barril magro, costelas à mostra (rad marca as costelas), garupa ossuda
    keys = [(.9, .9, .07, .07), (.72, 1.0, .19, .19), (.42, 1.04, .26, .25), (.1, 1.06, .27, .26), (-.2, 1.05, .26, .25),
            (-.5, 1.0, .23, .22), (-.75, .98, .16, .16), (-.9, .95, .1, .1)]
    rings = ring_path(keys, .015)
    def rad(i, a, r):
        y = r[0].y; sn = math.sin(a); f = 1.0
        if -.4 < y < .3 and abs(sn) < .9:  # costelas: anéis finos que sobem da barriga
            f *= 1 + .05*math.cos(y*38)*(1 - abs(sn))
        if .4 < y < .8 and .2 < sn < .9:  # ancas ossudas
            f *= 1 + .05*max(0, 1 - abs(y - .6)/.15)
        return f
    body = loft("cavalo_corpo", rings, hide, seg=36, rad=rad)
    parts = [body]
    # crina rala no pescoço e na cernelha
    parts += tufts(rings, mane, 60, (-30, 60), (.6, .99), .18, .014, 31, back=.5, down=-.2, lmin=.4)
    parts += tufts(rings, mane, 40, (60, 120), (.05, .5), .06, .012, 32, back=.4, down=0)

    # ---- pescoço e cabeça: crânio longo, ossos do focinho, órbitas e dentes
    neck_keys = [(-.5, 1.05, .2, .18), (-.65, 1.27, .16, .14), (-.8, 1.42, .13, .12), (-.92, 1.52, .11, .1)]
    neck = loft("cavalo_pescoco", ring_path(neck_keys, .015), hide, seg=24)
    parts.append(neck)
    # barda: placas de ferro sobre o tronco e o pescoço, com rebites; chanfro de ferro na cabeça
    torso = [i for i, r in enumerate(rings) if -.6 < r[0].y < .5]
    parts.append(loft("cavalo_barda_tronco", [rings[i] for i in torso], iron, seg=36, rad=lambda i, a, r: 1.09))
    parts.append(loft("cavalo_barda_pescoco", ring_path(neck_keys, .015), iron, seg=24, rad=lambda i, a, r: 1.2))
    for k in range(0, len(torso), 2):   # rebites da barda ao longo da cinta
        p, nrm = surf(rings[torso[k]], math.radians(60))
        parts.append(prim("primitive_uv_sphere_add", steel, p + nrm*.03, (.012, .012, .012), segments=6, ring_count=4))
    parts.append(prim("primitive_cube_add", iron, (-1.18, 1.32, 1.32), scale=(.07, .16, .1)))   # chanfro
    head = join([prim("primitive_uv_sphere_add", bone, (-1.16, 1.4, 1.36), (.13, .26, .14), segments=14, ring_count=10),
                 prim("primitive_uv_sphere_add", bone, (-1.3, 1.2, 1.26), (.1, .17, .09), segments=12, ring_count=8)])
    parts.append(head)
    for s in (-1, 1):   # órbitas: buraco e brasa no fundo
        parts.append(prim("primitive_uv_sphere_add", hole, (-1.26 + .0, 1.28, 1.25 + .0) if s < 0 else (-1.26, 1.28, 1.25),
                          (.035, .035, .035), segments=8, ring_count=6))
    parts.append(prim("primitive_uv_sphere_add", eye, (-1.3, 1.36, 1.3), (.012, .012, .012), segments=6, ring_count=4))
    for k in range(5):   # dentes da mandíbula
        parts.append(prim("primitive_cube_add", bone, (-1.12 - .05*k, 1.19 - .01*k, 1.1), (.012, .012, .02)))
    # crina solta na cabeça
    parts += tufts(rings[:1] + rings[:1], mane, 12, (-180, 180), (.0, .0), .05, .012, 33, back=.6, down=.0)

    # ---- sela de couro com estribos de ferro e cilha
    saddle_ring = rings[int(.5*(len(rings)-1))]
    sp, nrm = surf(saddle_ring, math.radians(90))
    parts.append(prim("primitive_cube_add", leather, sp + Vector((0, .02, .1)), scale=(.16, .3, .05)))
    parts.append(prim("primitive_cube_add", leather, sp + Vector((0, .3, .02)), scale=(.12, .06, .05)))  # arção
    for s in (-1, 1):   # cilha e estribo
        parts.append(along("primitive_cylinder_add", leather, sp + Vector((s*.16, -.02, .02)), sp + Vector((s*.16, -.02, -.25)),
                           .012, vertices=6))
        parts.append(prim("primitive_torus_add", iron, sp + Vector((s*.18, -.02, -.32)), (1, 1, 1), major_radius=.07,
                          minor_radius=.008, major_segments=10, minor_segments=4, rot=(90, 0, 0)))
    body = join(parts)
    R.bind(body, ["hips", "spine", "chest", "neck", "head", "jaw", "thigh.L", "thigh.R", "upper_arm.L", "upper_arm.R"], power=4)

    # ---- patas: ossos finos, cascos de chifre escuro
    hoof = mat("ca_casco", (.06, .05, .045), 0, .4, dirt=.6)
    for s, n in ((1, "L"), (-1, "R")):
        for pts, bones_ in (
            ([(.15*s*.9, -.72, 1.12, .045), (.15*s, -.66, .62, .038), (.15*s, -.7, .22, .028)], [f"upper_arm.{n}", f"forearm.{n}"]),
            ([(.14*s*.9, .66, 1.1, .05), (.14*s, .55, .6, .038), (.14*s, .68, .26, .028)], [f"thigh.{n}", f"shin.{n}"]),
        ):
            R.bind(limb(f"cavalo_perna_{n}_{bones_[0]}", pts, bone, levels=2), bones_)
        hoof_o = prim("primitive_cylinder_add", hoof, (.15*s, -.73, .025) if n == "L" else (.15*s, -.74, .025), (.035, .03, .025), vertices=10)
        R.bind(hoof_o, [f"hand.{n}"], power=2)
        R.bind(prim("primitive_cylinder_add", hoof, (.14*s, .66, .025), (.034, .03, .025), vertices=10), [f"foot.{n}"], power=2)

    # ---- animações: idle (respira, orelhas e rabo) e walk (trote)
    return R, INFO

def anims(R):
    M = lambda *p: merge(*p)
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; s = math.sin(t)
        idle.append(M({"spine": {"x": 1.0*s}, "neck": {"x": 3 + 2*math.cos(t)}, "head": {"x": 5*s}, "tail1": {"z": 12*s},
                       "tail2": {"z": 16*math.sin(t - 1)}}))
    walk = []
    for i in range(8):
        p = i/8; s1 = math.sin(p*2*math.pi); s2 = math.sin(p*4*math.pi)
        legs = merge(leg_cycle("L", True, p, amp=20, lift=.9, fold=.8), leg_cycle("R", False, (p + .05) % 1, amp=18, lift=.9, fold=.8),
                     leg_cycle("R", True, (p + .5) % 1, amp=20, lift=.9, fold=.8), leg_cycle("L", False, (p + .55) % 1, amp=18, lift=.9, fold=.8))
        walk.append(M(legs, {"chest": {"z": 3*s1, "y": 2*s1}, "hips": {"z": -3*s1, "y": -2*s1}, "neck": {"x": 2*s2},
                             "head": {"x": 3*s2}, "tail1": {"z": 10*s1}, "tail2": {"z": 14*s1}}))
    return {"idle": idle, "walk": walk}
