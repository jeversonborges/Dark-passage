# Moto de Sucata (montaria, estilo Mad Max): motocicleta de carcaça de sucata, sem pessoa em cima.
# O cavaleiro é uma camada à parte (pose "montado" das classes, entregue depois).
# Quadro estático do veículo: tanque remendado, banco de couro rasgado, guidão de tubo, garfo dianteiro
# com mola exposta, roda dianteira e traseira com pneu gasto e aro de chapa, escapamento de latão cromado
# com uma brasa no bocal (o único emissivo). Placas de sucata parafusadas no tanque e na roda da frente.
# Ossos: chassi (sobe e desce na suspensão, pose "root") -> frame (quadro, tanque, motor), wf e wr (eixos das rodas).
# Eixos como no resto do pipeline: a moto olha para -Y, X é a esquerda, Z para cima.
# Animações: idle (balanço do motor), walk (rodas giram e a suspensão pulsa).
import bpy, math, random
from mathutils import Vector
from mrig import Rig, stained, merge
from base_rig import mat, prim, along

INFO = {"px": 256, "target_z": .55, "rim": (.95, .6, .25), "colors": 40, "samples": 40,
        "fps": {"idle": 6, "walk": 12}, "loops": ("idle", "walk")}

WF = (0, -.85, .33)     # eixo da roda da frente
WR = (0, .78, .33)      # eixo da roda de trás
RW = .3                 # raio do pneu

def bones():
    return {
        "chassi": ((0, 0, 0), (0, 0, .6), None),
        "frame": ((0, 0, .05), (0, 0, .5), "chassi"),
        "wf":    (WF, (WF[0], WF[1], WF[2] + .03), "chassi"),
        "wr":    (WR, (WR[0], WR[1], WR[2] + .03), "chassi"),
    }

def build():
    rnd = random.Random(7)
    paint = stained("mt_pintura", (.2, .17, .13), stain=(.3, .08, .03), amount=.6, scale=5, rough=.6, grime=1.2)
    steel = stained("mt_aco", (.36, .35, .33), stain=(.3, .06, .02), amount=.6, scale=6, metal=.9, rough=.42, grime=.5)
    rust = stained("mt_ferrugem", (.3, .13, .05), stain=(.2, .03, .01), amount=.5, scale=4, metal=.25, rough=.85, grime=.8)
    leather = stained("mt_couro", (.12, .07, .04), stain=(.2, .02, .01), amount=.6, scale=3, rough=.4, grime=.8)
    rubber = stained("mt_borracha", (.025, .024, .024), stain=(.2, .03, .01), amount=.4, scale=5, rough=.82, grime=.9)
    brass = stained("mt_latao", (.42, .27, .1), stain=(.1, .08, .04), amount=.45, scale=6, metal=1, rough=.4, grime=.4)
    glow = mat("mt_brasa", (1, .42, .1), emit=(1, .42, .1), strength=10)

    R = Rig("moto_sucata", bones(), ground=0.0, ground_bones=None)
    P = R.P

    # ------------------------------------------------ quadro, tanque, motor (osso "frame")
    fr = []
    fr.append(along("primitive_cylinder_add", steel, (0, -.7, .72), (0, .75, .62), .035, vertices=10))   # trilho superior
    fr.append(along("primitive_cylinder_add", steel, (0, -.55, .62), (0, .25, .2), .03, vertices=10))     # tubo de baixo
    fr.append(along("primitive_cylinder_add", steel, (0, .25, .2), (0, .8, .58), .03, vertices=10))       # tubo de trás
    fr.append(along("primitive_cylinder_add", steel, (0, -.85, .72), (0, -.85, .33), .028, vertices=10))  # garfo, esquerda
    fr.append(along("primitive_cylinder_add", steel, (.09, -.85, .72), (.09, -.85, .33), .028, vertices=10))  # garfo, direita
    fr.append(along("primitive_cylinder_add", steel, (-.2, -.82, 1.02), (.2, -.82, 1.02), .022, vertices=10))  # guidão
    fr.append(along("primitive_cylinder_add", steel, (0, -.55, 1.02), (0, -.82, 1.02), .026, vertices=10))     # coluna
    for s in (-1, 1):   # manoplas de borracha
        fr.append(along("primitive_cylinder_add", rubber, (s*.21, -.82, 1.02), (s*.27, -.82, 1.02), .035, vertices=10))
    fr.append(prim("primitive_cube_add", paint, (0, -.12, .86), scale=(.17, .36, .1)))      # tanque
    fr.append(prim("primitive_cube_add", leather, (0, .32, .92), scale=(.15, .22, .05)))   # banco
    fr.append(prim("primitive_cube_add", rust, (0, -.12, .6), scale=(.2, .2, .17)))        # motor
    fr.append(prim("primitive_cube_add", steel, (0, -.36, .34), scale=(.07, .04, .12), rot=(0, 0, 0)))  # radiador/carcaça
    fr.append(prim("primitive_cube_add", rust, (.2, .05, .86), scale=(.025, .22, .12), rot=(0, 0, 14)))  # placa de sucata
    fr.append(prim("primitive_cube_add", steel, (-.19, -.32, .88), scale=(.01, .14, .06), rot=(0, 0, -6)))  # placa parafusada
    fr.append(prim("primitive_cube_add", rust, (-.02, -.74, .54), scale=(.03, .05, .03), rot=(0, 0, 0)))  # trava solta
    # escapamento de latão com brasa no bocal
    fr.append(along("primitive_cylinder_add", brass, (.13, -.25, .42), (.13, .6, .3), .045, vertices=12))
    fr.append(prim("primitive_uv_sphere_add", glow, (.13, .62, .3), scale=(.035, .035, .035)))
    R.rigid([o for o in fr if o], "frame")

    # ------------------------------------------------ rodas (osso wf e wr): pneu, aro de chapa, cubo
    for axle, bone, dirty in ((WF, "wf", .9), (WR, "wr", .6)):
        parts = []
        t = prim("primitive_torus_add", rubber, axle, rot=(0, 90, 0), major_radius=RW - .04, minor_radius=.045,
                 major_segments=28, minor_segments=8)
        parts.append(t)
        parts.append(prim("primitive_torus_add", steel, axle, rot=(0, 90, 0), major_radius=RW - .12, minor_radius=.018,
                          major_segments=24, minor_segments=6))
        for k in range(6):   # raios de arame
            a = k/6*math.pi*2
            c = Vector(axle) + Vector((0, math.cos(a), math.sin(a))) * (RW - .12) / 2
            parts.append(along("primitive_cylinder_add", steel, c - Vector((0, math.cos(a), math.sin(a))) * (RW - .12) / 2,
                               c + Vector((0, math.cos(a), math.sin(a))) * (RW - .12) / 2, .008, vertices=6))
        parts.append(along("primitive_cylinder_add", steel, Vector(axle) + Vector((-.06, 0, 0)),
                           Vector(axle) + Vector((.06, 0, 0)), .05, vertices=12))   # cubo
        if dirty > .8:   # chapa parafusada na roda da frente
            parts.append(prim("primitive_cube_add", rust, (Vector(axle) + Vector((.07, .08, .17))), scale=(.02, .09, .05),
                              rot=(rnd.uniform(-12, 12), 0, 20)))
        R.rigid([o for o in parts if o], bone)

    return R, INFO

def anims(R):
    # Os mesmos quadros de idle/walk servem para o render: as rodas giram no walk.
    idle = [{"root": (0, 0, .004*math.sin(i/6*2*math.pi)), "frame": {"x": .6*math.sin(i/6*2*math.pi)}} for i in range(6)]
    walk = []
    for i in range(8):
        p = i/8; s = math.sin(p*2*math.pi)
        walk.append(merge({"wf": {"x": -45*i}, "wr": {"x": -45*i}},
                          {"root": (0, 0, .006*abs(s) - .003), "frame": {"x": .9*s}}))
    return {"idle": idle, "walk": walk}
