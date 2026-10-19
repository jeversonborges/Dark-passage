# Cavalos do Apocalipse (montarias com armadura): Cavalo da Perdição (Conquista) e Cavalo do Lamento (Peste).
# Mesmo esqueleto de cavalo do Cavalo Esqueleto (cavalo_esqueleto.py), com barda de placas, sela e estribos.
# Conquista: branco e imponente, barda dourada com rebites e faixa azuis, coroa de ouro na cabeça
#   (único emissivo: os olhos de ouro).
# Peste: pálido e esverdeado, pele coberta de bolhas (único emissivo: a luz verde do Amargo sob a pele),
#   barda de ferro enferrujado e trapos pendurados, e uma mosca negra que zumbe em volta da cabeça.
# Animações: idle (respira, sacode a cabeça, cauda; a mosca orbita) e walk (trote em diagonais).
# Render: cavalo_apocalipse:conquista e cavalo_apocalipse:peste.
import bpy, math, random
from mathutils import Vector
from mrig import *
from quad import *
from cavalo_esqueleto import bones as cavalo_bones

INFO = {"px": 256, "target_z": .9, "rim": (.7, .85, .4), "samples": 40,
        "fps": {"idle": 8, "walk": 10}, "loops": ("idle", "walk")}

VARIANTS = {
    "conquista": {"hide": (.86, .84, .78), "hide_stain": (.5, .42, .3), "mane": (.78, .74, .66),
                  "barda": (.8, .58, .2), "barda_stain": (.32, .18, .05), "rebite": (.1, .2, .55),
                  "eye": (1, .8, .4), "glow": None, "crown": True, "tattered": False, "fly": False, "bolhas": 0},
    "peste": {"hide": (.5, .56, .4), "hide_stain": (.26, .32, .1), "mane": (.16, .18, .1),
              "barda": (.2, .2, .16), "barda_stain": (.42, .26, .1), "rebite": (.35, .3, .2),
              "eye": None, "glow": (.5, 1, .3), "crown": False, "tattered": True, "fly": True, "bolhas": 90},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name

def bones():
    B = cavalo_bones()
    if V.get("fly"):   # a mosca: osso preso à cabeça, a ponta gira em volta do ponto de apoio
        B["fly"] = ((0, -1.0, 1.62), (0, -1.0, 1.9), "head")
    return B

def pustulas(rings_, n, seed, mat_):
    """Bolhas meio enterradas na pele: esferas pequenas em ângulos sorteados dos anéis."""
    rr = random.Random(seed); out = []
    for _ in range(n):
        i = rr.randint(0, len(rings_) - 1)
        p, nrm = surf(rings_[i], math.radians(rr.uniform(0, 360)))
        r = rr.choice((.012, .016, .022, .03))*rr.uniform(.8, 1.2)
        out.append(prim("primitive_uv_sphere_add", mat_, p + nrm*r*.35, (r, r, r*.8), segments=6, ring_count=4))
    return out

def build():
    n = "ap_" + V["name"]
    hide = stained(f"{n}_couro", V["hide"], stain=V["hide_stain"], amount=.5, scale=6, rough=.55, grime=.8, dirt=.35)
    barda = stained(f"{n}_barda", V["barda"], stain=V["barda_stain"], amount=.45, scale=5, metal=.85, rough=.36, grime=.5)
    mane = mat(f"{n}_crina", V["mane"], 0, .85, dirt=.6)
    rebite = mat(f"{n}_rebite", V["rebite"], .3, .3, dirt=.2)
    leather = stained(f"{n}_sela", (.13, .07, .04), stain=(.2, .03, .01), amount=.5, scale=4, rough=.4, grime=.8)
    iron = stained(f"{n}_ferro", (.12, .1, .09), stain=(.3, .1, .03), amount=.55, scale=6, metal=.8, rough=.5, grime=.5)
    gold = mat(f"{n}_ouro", (.85, .62, .24), .95, .22, dirt=.15)
    hole = mat(f"{n}_buraco", (.01, .006, .005), 0, .9)
    hoof = mat(f"{n}_casco", (.06, .05, .045), 0, .4, dirt=.6)
    cloth = stained(f"{n}_trapo", (.3, .27, .2), stain=(.25, .1, .04), amount=.5, scale=8, rough=.9, grime=1.0, dirt=.6)
    eye = mat(f"{n}_olho", V["eye"], emit=V["eye"], strength=12) if V["eye"] else hole
    glow = mat(f"{n}_bolha", (.62, .7, .42), 0, .3, emit=V["glow"], strength=1.5, dirt=.2) if V["glow"] else hide
    fly_m = mat(f"{n}_mosca", (.02, .02, .02), .2, .25, dirt=.3)
    wing = mat(f"{n}_asa_mosca", (.35, .36, .38), 0, .1, dirt=.1)

    R = QRig(n, bones(), ground=.03, ground_bones=PAWS)

    # ---- corpo (mesmo barril magro e costelas do cavalo esqueleto)
    keys = [(.9, .9, .07, .07), (.72, 1.0, .19, .19), (.42, 1.04, .26, .25), (.1, 1.06, .27, .26), (-.2, 1.05, .26, .25),
            (-.5, 1.0, .23, .22), (-.75, .98, .16, .16), (-.9, .95, .1, .1)]
    rings = ring_path(keys, .015)
    def rad(i, a, r):
        y = r[0].y; sn = math.sin(a); f = 1.0
        if -.4 < y < .3 and abs(sn) < .9: f *= 1 + .05*math.cos(y*38)*(1 - abs(sn))
        if .4 < y < .8 and .2 < sn < .9: f *= 1 + .05*max(0, 1 - abs(y - .6)/.15)
        return f
    parts = [loft(f"{n}_corpo", rings, hide, seg=36, rad=rad)]
    parts += tufts(rings, mane, 60, (-30, 60), (.6, .99), .18, .014, 31, back=.5, down=-.2, lmin=.4)
    parts += tufts(rings, mane, 40, (60, 120), (.05, .5), .06, .012, 32, back=.4, down=0)

    # ---- pescoço e cabeça
    neck_keys = [(-.5, 1.05, .2, .18), (-.65, 1.27, .16, .14), (-.8, 1.42, .13, .12), (-.92, 1.52, .11, .1)]
    neck_rings = ring_path(neck_keys, .015)
    parts.append(loft(f"{n}_pescoco", neck_rings, hide, seg=24))

    # ---- barda: placas de metal sobre o tronco e o pescoço, faixa de rebites e a faixa de cor
    torso = [i for i, r in enumerate(rings) if -.6 < r[0].y < .5]
    parts.append(loft(f"{n}_barda_tronco", [rings[i] for i in torso], barda, seg=36, rad=lambda i, a, r: 1.09))
    parts.append(loft(f"{n}_barda_pescoco", neck_rings, barda, seg=24, rad=lambda i, a, r: 1.2))
    edges = [rings[torso[0]], rings[torso[1]], rings[torso[-2]], rings[torso[-1]]]
    parts.append(loft(f"{n}_faixa", edges[:2], rebite, seg=36, rad=lambda i, a, r: 1.105, levels=0))
    parts.append(loft(f"{n}_faixa_traseira", edges[2:], rebite, seg=36, rad=lambda i, a, r: 1.105, levels=0))
    for k in range(0, len(torso), 2):   # rebites ao longo da cinta
        p, nrm = surf(rings[torso[k]], math.radians(60))
        parts.append(prim("primitive_uv_sphere_add", rebite, p + nrm*.03, (.013, .013, .013), segments=6, ring_count=4))
    parts.append(prim("primitive_cube_add", iron, (0, -1.18, 1.32), scale=(.07, .16, .1)))   # chanfro de ferro
    head = join([prim("primitive_uv_sphere_add", hide, (0, -1.16, 1.36), (.13, .26, .14), segments=14, ring_count=10),
                 prim("primitive_uv_sphere_add", hide, (0, -1.3, 1.26), (.1, .17, .09), segments=12, ring_count=8)])
    parts.append(head)
    for s in (-1, 1):   # órbitas e olhos, um de cada lado do crânio
        parts.append(prim("primitive_uv_sphere_add", hole, (s*.1, -1.26, 1.25), (.035, .035, .035), segments=8, ring_count=6))
        parts.append(prim("primitive_uv_sphere_add", eye, (s*.11, -1.3, 1.3), (.012, .012, .012), segments=6, ring_count=4))
    for k in range(5):   # dentes
        parts.append(prim("primitive_cube_add", hide, (0, -1.12 - .05*k, 1.14 - .01*k), (.012, .012, .02)))
    parts += tufts(rings[:1] + rings[:1], mane, 12, (-180, 180), (.0, .0), .05, .012, 33, back=.6, down=.0)

    if V["crown"]:   # coroa de ouro na nuca: aro com cinco pontas e uma gema azul na frente
        C = Vector((0, -1.0, 1.6))
        parts.append(prim("primitive_torus_add", gold, C, (1, 1, 1), major_radius=.055, minor_radius=.011,
                          major_segments=14, minor_segments=5))
        for k in range(5):
            a = 2*math.pi*k/5 + math.pi/2
            base = C + Vector((.055*math.cos(a), .055*math.sin(a), 0))
            tip_h = .075 if k != 2 else .095
            parts.append(along("primitive_cone_add", gold, base, base + Vector((0, 0, tip_h)), .011, vertices=6,
                               radius1=1, radius2=0))
        gem = C + Vector((0, -.055, .0))
        parts.append(prim("primitive_uv_sphere_add", rebite, gem, (.014, .014, .014), segments=6, ring_count=4))

    if V["bolhas"]:   # bolhas no corpo e no pescoço
        parts += pustulas(rings, V["bolhas"], 52, glow)
        parts += pustulas(neck_rings, 14, 53, glow)

    # ---- trapos da barda esfarrapada, pendurados das bordas inferiores
    if V["tattered"]:
        rr = random.Random(41); rags = []
        for k in range(12):
            i = torso[rr.randrange(len(torso))]
            p, nrm = surf(rings[i], math.radians(rr.uniform(200, 340)))
            L = rr.uniform(.12, .3)
            rags.append(prim("primitive_cube_add", cloth, p + nrm*.02 - Vector((0, 0, L/2)), scale=(.012, .05, L/2),
                             rot=(0, 0, rr.uniform(-20, 20))))
        cloth_o = join(rags)
        R.bind(cloth_o, ["spine", "chest", "hips"], power=4)

    # ---- sela de couro com estribos de ferro e cilha
    saddle_ring = rings[int(.5*(len(rings)-1))]
    sp, nrm = surf(saddle_ring, math.radians(90))
    parts.append(prim("primitive_cube_add", leather, sp + Vector((0, .02, .1)), scale=(.16, .3, .05)))
    parts.append(prim("primitive_cube_add", leather, sp + Vector((0, .3, .02)), scale=(.12, .06, .05)))
    for s in (-1, 1):
        parts.append(along("primitive_cylinder_add", leather, sp + Vector((s*.16, -.02, .02)), sp + Vector((s*.16, -.02, -.25)),
                           .012, vertices=6))
        parts.append(prim("primitive_torus_add", iron, sp + Vector((s*.18, -.02, -.32)), (1, 1, 1), major_radius=.07,
                          minor_radius=.008, major_segments=10, minor_segments=4, rot=(90, 0, 0)))
    body = join(parts)
    R.bind(body, ["hips", "spine", "chest", "neck", "head", "jaw", "thigh.L", "thigh.R", "upper_arm.L", "upper_arm.R"], power=4)

    # ---- patas e cascos
    for s, n_ in ((1, "L"), (-1, "R")):
        for pts, bones_ in (
            ([(.15*s*.9, -.72, 1.12, .045), (.15*s, -.66, .62, .038), (.15*s, -.7, .22, .028)], [f"upper_arm.{n_}", f"forearm.{n_}"]),
            ([(.14*s*.9, .66, 1.1, .05), (.14*s, .55, .6, .038), (.14*s, .68, .26, .028)], [f"thigh.{n_}", f"shin.{n_}"]),
        ):
            R.bind(limb(f"{n}_perna_{n_}_{bones_[0]}", pts, hide, levels=2), bones_)
        hoof_o = prim("primitive_cylinder_add", hoof, (.15*s, -.73, .025) if n_ == "L" else (.15*s, -.74, .025), (.035, .03, .025), vertices=10)
        R.bind(hoof_o, [f"hand.{n_}"], power=2)
        R.bind(prim("primitive_cylinder_add", hoof, (.14*s, .66, .025), (.034, .03, .025), vertices=10), [f"foot.{n_}"], power=2)

    # ---- mosca (só a Peste): corpo e asas, presas ao osso "fly"
    if V["fly"]:
        f_parts = [prim("primitive_uv_sphere_add", fly_m, (0, -1.0, 1.9), (.028, .035, .024), segments=8, ring_count=5)]
        for s in (-1, 1):
            f_parts.append(prim("primitive_uv_sphere_add", wing, (.03*s, -1.0, 1.93), (.035, .012, .02), segments=6, ring_count=4,
                                rot=(0, 0, 20*s)))
        fly = join(f_parts)
        R.bind(fly, ["fly"], power=2)

    return R, INFO

def anims(R):
    idle = []
    for i in range(8):
        t = i/8*2*math.pi; s = math.sin(t)
        pose = {"spine": {"x": 1.0*s}, "neck": {"x": 3 + 2*math.cos(t)}, "head": {"x": 5*s, "z": 2*math.sin(t + 1)},
                "hips": {"z": .8*math.sin(t + .5)}, "tail1": {"z": 12*s}, "tail2": {"z": 16*math.sin(t - 1)}}
        if V.get("fly"): pose["fly"] = {"x": 32*math.sin(t), "y": 32*math.cos(t)}
        idle.append(merge(pose))
    walk = []
    for i in range(10):
        p = i/10; s1 = math.sin(p*2*math.pi); s2 = math.sin(p*4*math.pi)
        legs = merge(leg_cycle("L", True, p, amp=20, lift=.9, fold=.8), leg_cycle("R", False, (p + .05) % 1, amp=18, lift=.9, fold=.8),
                     leg_cycle("R", True, (p + .5) % 1, amp=20, lift=.9, fold=.8), leg_cycle("L", False, (p + .55) % 1, amp=18, lift=.9, fold=.8))
        pose = merge(legs, {"chest": {"z": 3*s1, "y": 2*s1}, "hips": {"z": -3*s1, "y": -2*s1}, "neck": {"x": 2*s2},
                            "head": {"x": 3*s2, "z": 1.5*s1}, "tail1": {"z": 10*s1}, "tail2": {"z": 14*s1}})
        if V.get("fly"): pose["fly"] = {"x": 32*math.sin(4*math.pi*p), "y": 32*math.cos(4*math.pi*p)}
        walk.append(pose)
    return {"idle": idle, "walk": walk}
