# Cavalo Esqueleto (montaria): cavalo morto que a Vigília e a Legião reanimaram para carregar.
# Anatomia de cavalo de sela: cernelha perto de 1,6 m, corpo de ~1,6 m do peito à anca, pescoço saindo
# da cernelha e cabeça ligada pela nuca. Escápula sobre as costelas; cotovelo, carpo, boleto; quadril,
# joelho, jarrete. Pele de couro seco esticada nas costelas, crina rala, órbitas vazias.
# Barda de ferro (placas sobrepostas) no tronco e no pescoço, chanfro na cabeça, sela com cilha e estribos.
# Brilho: uma brasa fraca nas órbitas (o único emissivo). Animações: idle e walk (passo de quatro tempos).
# Eixos: o cavalo olha para -Y, X é a esquerda do bicho, Z para cima; coordenadas em metros (x, y, z).
import bpy, math
from mathutils import Vector
from mrig import *
from quad import *

INFO = {"px": 256, "target_z": .85, "rim": (.7, .85, .4), "colors": 40, "samples": 40,
        "fps": {"idle": 6, "walk": 10}, "loops": ("idle", "walk")}

# Variantes (render: cavalo_esqueleto:corcel_negro). O padrão é o Cavalo Esqueleto de barda de ferro.
VARIANTS = {
    "corcel_negro": {"hide": (.06, .05, .05), "bone": (.2, .18, .16), "iron": (.05, .05, .055),
                     "steel": (.16, .15, .15), "mane": (.03, .025, .025)},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name

# Articulações (y, z) no plano sagital. y negativo é a frente.
ESC = (-.55, 1.35)      # escápula / ombro
COT = (-.56, .85)       # cotovelo
CAR = (-.6, .42)        # carpo (joelho da pata da frente)
BOL = (-.62, .12)       # boleto da frente
QUA = (.7, 1.3)         # quadril
JOE = (.55, .9)         # joelho de trás (stifle)
JAR = (.78, .5)         # jarrete
BOL2 = (.72, .12)       # boleto de trás

def bones():
    B = quad_bones(sh=1.35, hip=1.3, y_sh=ESC[0], y_hip=QUA[0], w=.15, wh=.14, back=1.45, neck=(-1.0, 1.84),
                   head=(-1.5, 1.5), jaw=((-1.1, 1.6), (-1.4, 1.45)), tail=((.98, 1.42), (1.1, 1.1)))
    for s, n in ((1, "L"), (-1, "R")):
        w, wh = .15*s, .14*s
        B[f"upper_arm.{n}"] = ((w*.9, ESC[0], ESC[1]), (w, COT[0], COT[1]), "chest")
        B[f"forearm.{n}"] = ((w, COT[0], COT[1]), (w, CAR[0], CAR[1]), f"upper_arm.{n}")
        B[f"hand.{n}"] = ((w, CAR[0], CAR[1]), (w, BOL[0], BOL[1]), f"forearm.{n}")
        B[f"thigh.{n}"] = ((wh*.9, QUA[0], QUA[1]), (wh, JOE[0], JOE[1]), "hips")
        B[f"shin.{n}"] = ((wh, JOE[0], JOE[1]), (wh, JAR[0], JAR[1]), f"thigh.{n}")
        B[f"foot.{n}"] = ((wh, JAR[0], JAR[1]), (wh, BOL2[0], BOL2[1]), f"shin.{n}")
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
    hoof = mat("ca_casco", (.06, .05, .045), 0, .4, dirt=.6)

    R = QRig("cavalo", bones(), ground=.03, ground_bones=PAWS)

    # ---- tronco: peito fundo, costelas à mostra, dorso reto, barriga recolhida, anca em degrau
    keys = [(.85, 1.2, .14, .14), (.7, 1.27, .26, .27), (.4, 1.3, .3, .3), (0, 1.28, .3, .31),
            (-.4, 1.27, .3, .3), (-.65, 1.25, .27, .28), (-.82, 1.2, .2, .2)]
    rings = ring_path(keys, .015)
    def rad(i, a, r):
        y = r[0].y; sn = math.sin(a); f = 1.0
        if -.4 < y < .3 and abs(sn) < .9:  # costelas: anéis finos que sobem da barriga
            f *= 1 + .05*math.cos(y*38)*(1 - abs(sn))
        if .5 < y < .85 and .2 < sn < .9:  # anca óssea
            f *= 1 + .05*max(0, 1 - abs(y - .65)/.15)
        return f
    parts = [loft("cavalo_corpo", rings, hide, seg=36, rad=rad)]
    parts += tufts(rings, mane, 50, (-30, 60), (.6, .99), .16, .014, 31, back=.5, down=-.2, lmin=.4)

    # ---- pescoço arqueado a partir da cernelha, ligado à cabeça pela nuca
    neck_keys = [(-.5, 1.46, .2, .2), (-.66, 1.6, .17, .17), (-.82, 1.74, .14, .14), (-.96, 1.84, .12, .12)]
    neck_rings = ring_path(neck_keys, .015)
    parts.append(loft("cavalo_pescoco", neck_rings, hide, seg=24))
    parts += tufts(neck_rings, mane, 40, (-40, 80), (.3, 1.0), .14, .013, 34, back=.7, down=.0)

    # ---- cabeça: crânio, focinho, órbitas com brasa, dentes (eixos: x lateral, y frente, z altura)
    parts.append(along("primitive_cylinder_add", bone, (0, -1.0, 1.80), (0, -1.3, 1.6), .11, vertices=12))   # crânio
    parts.append(along("primitive_cylinder_add", bone, (0, -1.3, 1.6), (0, -1.5, 1.42), .085, vertices=12))  # focinho
    parts.append(prim("primitive_uv_sphere_add", bone, (0, -.98, 1.82), (.12, .12, .12), segments=12, ring_count=8))  # nuca
    for s in (-1, 1):   # órbitas: buraco escuro e brasa no fundo
        parts.append(prim("primitive_uv_sphere_add", hole, (s*.095, -1.12, 1.74), (.04, .04, .04), segments=8, ring_count=6))
        parts.append(prim("primitive_uv_sphere_add", eye, (s*.095, -1.12, 1.74), (.016, .016, .016), segments=6, ring_count=4))
    for k in range(3):   # dentes da mandíbula
        parts.append(prim("primitive_cube_add", bone, (0, -1.36 - .05*k, 1.44), (.012, .012, .02)))

    # ---- sela com cilha, arção e estribos
    sp, nrm = surf(rings[int(.5*(len(rings)-1))], math.radians(90))
    parts.append(prim("primitive_cube_add", leather, sp + Vector((0, 0, .08)), scale=(.17, .3, .05)))
    parts.append(prim("primitive_cube_add", leather, sp + Vector((0, .3, .02)), scale=(.12, .06, .05)))
    for s in (-1, 1):
        parts.append(along("primitive_cylinder_add", leather, sp + Vector((s*.16, -.02, .0)), sp + Vector((s*.16, -.02, -.3)), .012, vertices=6))
        parts.append(prim("primitive_torus_add", iron, sp + Vector((s*.18, -.02, -.36)), (1, 1, 1), major_radius=.07,
                          minor_radius=.008, major_segments=10, minor_segments=4, rot=(90, 0, 0)))

    # ---- barda: placas sobrepostas sobre o tronco e o pescoço, rebites, chanfro de ferro
    torso = [i for i, r in enumerate(rings) if -.6 < r[0].y < .5]
    parts.append(loft("cavalo_barda_tronco", [rings[i] for i in torso], iron, seg=36, rad=lambda i, a, r: 1.09))
    parts.append(loft("cavalo_barda_pescoco", neck_rings, iron, seg=24, rad=lambda i, a, r: 1.2))
    for k in range(0, len(torso), 2):
        p, nrm = surf(rings[torso[k]], math.radians(60))
        parts.append(prim("primitive_uv_sphere_add", steel, p + nrm*.03, (.012, .012, .012), segments=6, ring_count=4))
    parts.append(prim("primitive_cube_add", iron, (0, -1.3, 1.5), scale=(.075, .15, .1)))   # chanfro

    body = join(parts)
    R.bind(body, ["hips", "spine", "chest", "neck", "head", "jaw", "thigh.L", "thigh.R", "upper_arm.L", "upper_arm.R"], power=4)

    # ---- pernas: osso fino e articulado, com cascos
    for s, n in ((1, "L"), (-1, "R")):
        fr = [(.15*s*.9, ESC[0], ESC[1], .05), (.15*s, COT[0], COT[1], .04), (.15*s, CAR[0], CAR[1], .038), (.15*s, BOL[0], BOL[1], .03)]
        tr = [(.14*s*.9, QUA[0], QUA[1], .055), (.14*s, JOE[0], JOE[1], .045), (.14*s, JAR[0], JAR[1], .04), (.14*s, BOL2[0], BOL2[1], .03)]
        R.bind(limb(f"cavalo_perna_f_{n}", fr, bone, levels=2), [f"upper_arm.{n}", f"forearm.{n}", f"hand.{n}"])
        R.bind(limb(f"cavalo_perna_t_{n}", tr, bone, levels=2), [f"thigh.{n}", f"shin.{n}", f"foot.{n}"])
        R.bind(prim("primitive_cylinder_add", hoof, (.15*s, BOL[0] - .01, .025), (.035, .03, .025), vertices=10), [f"hand.{n}"], power=2)
        R.bind(prim("primitive_cylinder_add", hoof, (.14*s, BOL2[0] - .01, .025), (.034, .03, .025), vertices=10), [f"foot.{n}"], power=2)

    return R, INFO

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; s = math.sin(t)
        idle.append(merge({"spine": {"x": 1.0*s}, "neck": {"x": 3 + 2*math.cos(t)}, "head": {"x": 5*s},
                           "tail1": {"z": 12*s}, "tail2": {"z": 16*math.sin(t - 1)}}))
    # Passo de quatro tempos (sequência lateral): posterior-esquerdo 0, anterior-esquerdo 0.25,
    # posterior-direito 0.5, anterior-direito 0.75. Só uma pata sai do chão por vez.
    walk = []
    for i in range(8):
        p = i/8; s1 = math.sin(p*2*math.pi); s2 = math.sin(p*4*math.pi)
        legs = merge(leg_cycle("L", False, p, amp=20, lift=.9, fold=.8),
                     leg_cycle("L", True, (p + .25) % 1, amp=22, lift=.9, fold=.8),
                     leg_cycle("R", False, (p + .5) % 1, amp=20, lift=.9, fold=.8),
                     leg_cycle("R", True, (p + .75) % 1, amp=22, lift=.9, fold=.8))
        walk.append(merge(legs, {"chest": {"z": 3*s1, "y": 2*s1}, "hips": {"z": -3*s1, "y": -2*s1},
                                 "neck": {"x": 2*s2}, "head": {"x": 3*s2}, "tail1": {"z": 10*s1}, "tail2": {"z": 14*s1}}))
    return {"idle": idle, "walk": walk}
