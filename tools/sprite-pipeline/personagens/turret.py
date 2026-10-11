# Torreta Sentinela (invocação do Tecnomante, Vigília): torre de latão em andares, com núcleo de brasa numa gaiola
# de arame e cabeça de aço azul que gira com um par de canos e emissores de tesla. Forma inspirada nas torretas
# de tecnologia do Heimerdinger, adaptada ao estilo "Ferrugem Sagrada": sujo, com brilho laranja e verde ácido.
# Três ossos: base (fixa), giro (cabeça que varre) e cano (que recua no tiro).
import bpy, bmesh, math, random
from mathutils import Vector
from rig import *
from classes2 import curve_tube

TORRE_BONES = {
    "base": ((0, 0, 0), (0, 0, .1), None),
    "giro": ((0, 0, .52), (0, 0, .72), "base"),
    "cano": ((0, 0, .62), (0, -.5, .62), "giro"),
}

def torreta():
    steel = mat("aco_azul_torre", (.1,.18,.28), .4, .5, dirt=.55, grime=.8)
    rust = mat("ferrugem_torre", (.2,.09,.04), .6, .7, dirt=.5, grime=.4)
    iron = mat("ferro_velho", (.1,.095,.09), 1, .5, dirt=.6, grime=.3)
    copper = mat("cobre_torre", (.45,.16,.06), 1, .4, dirt=.55, grime=.2)
    brass = mat("latao_torre", (.55,.3,.08), 1, .35, dirt=.5, grime=.2)
    dark = mat("couro_escuro", (.03,.022,.017), 0, .5, dirt=.7)
    glow = mat("nucleo_brasa", (1,.6,.2), emit=(1,.55,.15), strength=24)
    acid = mat("verde_acido", (.3,1,.1), emit=(.4,1,.1), strength=1.4)
    arc = mat("arco_eletrico", (.6,.85,1), emit=(.55,.82,1), strength=12)
    bolt = mat("raio", (.7,.9,1), emit=(.6,.85,1), strength=22)
    arm = make_armature("torreta", extra=TORRE_BONES)

    # --- base: placa de ferro, três pernas de pistão e torre de latão em três andares
    base = [prim("primitive_cylinder_add", iron, (0, 0, .02), (.3, .3, .02), vertices=24)]
    for k in range(6):
        a = k*math.pi/3
        base.append(prim("primitive_uv_sphere_add", brass, (.27*math.cos(a), .27*math.sin(a), .045), (.013,)*3, segments=6, ring_count=4))
    hub = Vector((0, 0, .12))
    for a_deg in (90, 210, 330):
        a = math.radians(a_deg); foot = Vector((.34*math.cos(a), .34*math.sin(a), .02))
        base.append(along("primitive_cylinder_add", iron, hub, foot, .026, vertices=8))
        base.append(prim("primitive_cylinder_add", brass, foot + Vector((0, 0, .02)), (.045, .045, .012), vertices=10))
    for z0, z1, r in ((.1, .26, .17), (.26, .4, .13), (.4, .5, .1)):   # andares que afinam para cima
        base.append(along("primitive_cylinder_add", brass, (0, 0, z0), (0, 0, z1), r, vertices=24))
    for z, r in ((.26, .18), (.4, .14), (.5, .11)):
        base.append(prim("primitive_torus_add", copper, (0, 0, z), (1, 1, 1), major_radius=r, minor_radius=.012, major_segments=24, minor_segments=6))
    base.append(prim("primitive_uv_sphere_add", copper, (0, 0, .5), (.1, .1, .04), segments=20, ring_count=10))
    for k in range(10):
        a = k*2*math.pi/10 + .3
        base.append(prim("primitive_uv_sphere_add", brass, (.178*math.cos(a), .178*math.sin(a), .18), (.011,)*3, segments=6, ring_count=4))
    # manômetro na frente do andar de baixo, com agulha
    base.append(along("primitive_cylinder_add", copper, (0, -.17, .18), (0, -.2, .18), .045, vertices=14))
    base.append(along("primitive_cylinder_add", dark, (0, -.2, .18), (0, -.205, .18), .034, vertices=14))
    base.append(prim("primitive_cube_add", acid, (0, -.21, .18), (.005, .005, .028), rot=(0, 0, 25)))
    # tubulação curva ligando o andar de baixo à cabeça
    base += curve_tube(copper, [Vector((.17, -.02, .2)), Vector((.25, -.02, .36)), Vector((.16, 0, .53))], .016, .014, verts=8)
    rigid(base, arm, "base")

    # --- cabeça giratória: anel de latão, carcaça de aço azul, placa com rebites e lâmpada de brasa
    head = [prim("primitive_cylinder_add", steel, (0, 0, .6), (.15, .15, .07), vertices=24)]
    head.append(prim("primitive_torus_add", brass, (0, 0, .52), (1, 1, 1), major_radius=.19, minor_radius=.014, major_segments=24, minor_segments=6))
    head.append(prim("primitive_torus_add", brass, (0, 0, .67), (1, 1, 1), major_radius=.15, minor_radius=.01, major_segments=20, minor_segments=5))
    head.append(prim("primitive_cube_add", steel, (0, -.17, .6), (.17, .02, .11)))
    head.append(prim("primitive_cube_add", rust, (0, -.188, .6), (.18, .007, .12)))
    for x in (-.13, -.065, 0, .065, .13):
        for z in (.53, .67):
            head.append(prim("primitive_uv_sphere_add", brass, (x, -.198, z), (.011,)*3, segments=6, ring_count=4))
    for s in (1, -1):
        head.append(prim("primitive_cube_add", acid, (.17*s, -.02, .6), (.016, .045, .035)))
    rigid(head, arm, "giro")
    # gaiola de arame de latão em volta do núcleo, com lâmpada de brasa no meio
    cage = []
    for k in range(4):
        a = k*math.pi/2 + math.pi/4
        cage.append(along("primitive_cylinder_add", brass, (.085*math.cos(a), .085*math.sin(a), .7), (.085*math.cos(a), .085*math.sin(a), .9), .007, vertices=5))
    for z in (.72, .88):
        cage.append(prim("primitive_torus_add", brass, (0, 0, z), (1, 1, 1), major_radius=.085, minor_radius=.006, major_segments=16, minor_segments=4))
    cage.append(prim("primitive_cylinder_add", dark, (0, 0, .915), (.05, .05, .015), vertices=12))
    rigid(cage, arm, "giro")
    lamp_o = rigid([prim("primitive_uv_sphere_add", glow, (0, 0, .8), (.07, .07, .09), segments=12, ring_count=8)], arm, "giro")
    lamp_o.name = "nucleo"
    ant = [along("primitive_cylinder_add", iron, (.11, 0, .7), (.12, .04, .9), .006, vertices=6),
           prim("primitive_uv_sphere_add", arc, (.12, .04, .91), (.02,)*3, segments=8, ring_count=5)]
    rigid(ant, arm, "giro")

    # --- cano duplo: canos de ferro com anéis de cobre, cruzeta, emissores de tesla nas pontas
    cano = []
    for x in (-.07, .07):
        cano.append(along("primitive_cylinder_add", iron, (x, .0, .62), (x, -.5, .62), .033, vertices=10))
        for y in (-.14, -.3, -.44):
            cano.append(prim("primitive_torus_add", copper, (x, y, .62), (1, 1, 1), (90, 0, 0), major_radius=.04, minor_radius=.008, major_segments=12, minor_segments=5))
        cano.append(prim("primitive_uv_sphere_add", arc, (x, -.5, .62), (.035,)*3, segments=10, ring_count=6))
    cano.append(along("primitive_cube_add", iron, (-.07, -.25, .62), (.07, -.25, .62), .012))
    cano.append(prim("primitive_cylinder_add", brass, (0, .02, .62), (.09, .09, .02), (90, 0, 0), vertices=14))
    cano.append(prim("primitive_cube_add", steel, (0, .02, .7), (.06, .05, .03)))
    rigid(cano, arm, "cano")

    # efeitos do tiro: clarão na boca dos canos e arcos entre os emissores (só aparecem no quadro do tiro)
    clar = [along("primitive_cone_add", bolt, (0, -.52, .62), (0, -.72, .62), 1, radius1=.1, radius2=0, vertices=8),
            prim("primitive_uv_sphere_add", bolt, (0, -.52, .62), (.07, .07, .07), segments=10, ring_count=6)]
    clar_o = rigid(clar, arm, "cano"); clar_o.name = "clarao"
    rnd2 = random.Random(9); pts = []
    for k in range(6):
        t = k/5; x = -.07 + .14*t
        pts.append(Vector((x, -.5 + rnd2.uniform(-.02, .02), .62 + rnd2.uniform(-.03, .03) + .03*math.sin(math.pi*t))))
    arco_o = rigid(curve_tube(bolt, pts, .007, .004, verts=5), arm, "cano"); arco_o.name = "arco_tesla"
    fx = [(clar_o, "attack", [0, 1, 1, 0, 0, 0, 0, 0]), (arco_o, "attack", [0, 0, 1, 1, 1, 0, 0, 0]),
          (lamp_o, "idle", [1, 0, 1, 1])]
    arm.scale = (1.7, 1.7, 1.7)   # torre de ~1,4 m: precisa ocupar a altura de um personagem na folha
    return arm, {"rim": (.6, .85, 1), "anim": "turret", "fx": fx}

def torreta_anims(arm):
    """idle: a cabeça varre devagar e o núcleo pisca. attack: a cabeça trava e o cano recua com o tiro."""
    idle = []
    for i in range(4):
        t = i/4*2*math.pi
        idle.append({"giro": {"z": 16*math.sin(t)}, "cano": {"x": 1.5*math.sin(t)}})
    shoot = []
    REC = [0, -8, -13, -9, -4, -1, 0, 0]   # o cano sobe com o coice e assenta de volta
    for i in range(8):
        shoot.append({"giro": {"z": 0}, "cano": {"x": REC[i]}})
    return {"idle": make_action(arm, "idle", idle), "attack": make_action(arm, "attack", shoot)}
