# Mutante v2 (Vigília): tanque corcunda, braço esquerdo mutado com placas de osso e veias de ácido,
# kilt e lenço azul aço da Vigília, emblema da vela na engrenagem, respirador e machado de placa.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix, Quaternion
from rig import *
from classes import bone_frame, L, body_parts, pauldron, chain_links
from classes2 import curve_tube, bezier, head_base, weapon_frame

def _orient(o, d):
    o.rotation_euler = Vector(d).to_track_quat('Z', 'Y').to_euler(); return o

def mutante():
    skin = mat("pele_cinza_doente", (.2,.18,.14), 0, .5, dirt=.6, grime=.5)
    bruise = mat("pele_roxa", (.1,.06,.07), 0, .5, dirt=.6, grime=.3)
    flesh = mat("carne_mutada", (.22,.075,.06), 0, .38, dirt=.55, grime=.4)
    bone = mat("osso_quitina", (.46,.41,.32), 0, .45, dirt=.6, grime=.4)
    canvas = mat("lona_azul_aco", (.05,.09,.15), 0, .85, dirt=.55, grime=.8)
    pants = mat("calca_lona_suja", (.06,.05,.04), 0, .85, dirt=.6, grime=.9)
    leather = mat("couro_correia", (.13,.07,.04), 0, .55, dirt=.6, grime=.7)
    dark = mat("couro_escuro", (.03,.022,.017), 0, .5, dirt=.7)
    bandage = mat("atadura", (.42,.37,.28), 0, .9, dirt=.75, grime=.9)
    iron = mat("ferro_velho", (.1,.095,.09), 1, .5, dirt=.6, grime=.3)
    rust = mat("placa_ferrugem", (.2,.09,.04), .6, .7, dirt=.5, grime=.3)
    brass = mat("latao_velho", (.5,.27,.07), 1, .4, dirt=.5, grime=.3)
    sign = mat("placa_amarela", (.6,.45,.05), .3, .5, dirt=.5, grime=.2)
    steel = mat("fio_afiado", (.5,.5,.5), 1, .25, dirt=.4, grime=.1)
    acid = mat("verde_acido", (.3,1,.1), emit=(.4,1,.1), strength=1.4)
    ember = mat("chama_vela", (1,.5,.15), emit=(1,.45,.1), strength=6)
    arm = make_armature("mutante")
    parts = body_parts(arm, pants, dark, skin, {"L": bone, "R": dark}, cuff=.05, buckle=iron, top_r=1.32, legs_r=1.22,
                       boot_top=.38, m_arms={"L": flesh, "R": bandage}, arm_scale={"L": 2.3, "R": 1.2},
                       glove_scale={"L": 2.2, "R": 1.05})
    rnd = random.Random(11)

    # --- braço esquerdo mutado: placas de osso por fora, veias de ácido, pústulas e garras curvas
    for bn, n_pl, r in (("upper_arm.L", 4, .16), ("forearm.L", 4, .13)):
        o, ax, up, sd = bone_frame(bn); ln = (P(bn, 1) - P(bn)).length; ob = []
        out = Vector((1, 0, .35)).normalized()  # lado de fora do braço
        for k in range(n_pl):
            c = o + ax*ln*(.15 + .75*k/n_pl) + out*r*.9 + up*.02*k
            pl = prim("primitive_uv_sphere_add", bone, c, (.075, .05, .022), segments=12, ring_count=6)
            _orient(pl, out); ob.append(pl)
            ob.append(along("primitive_cone_add", bone, c + out*.01, c + out*.07 + ax*.04, 1, radius1=.018, radius2=0, vertices=6))
        for k in range(2):   # veias brilhando que serpenteiam pelo braço
            a = rnd.uniform(0, 2*math.pi); w = (up*math.cos(a) + sd*math.sin(a))
            pts = [o + ax*ln*t + (w*math.cos(t*2.5) + ax.cross(w)*math.sin(t*2.5)*.4).normalized()*r*1.0 for t in (.05, .3, .55, .8, .97)]
            ob += curve_tube(acid, pts, .0045, .002, verts=5)
        for k in range(5):
            a = rnd.uniform(0, 2*math.pi); t = rnd.uniform(.15, .85)
            c = o + ax*ln*t + (up*math.cos(a) + sd*math.sin(a))*r*.95; sz = rnd.uniform(.016, .03)
            ob.append(prim("primitive_uv_sphere_add", acid if k % 3 == 0 else bruise, c, (sz,)*3, segments=8, ring_count=5))
        parts.append(rigid(ob, arm, bn))
    # espinhos de osso saindo do ombro esquerdo
    sh = P("upper_arm.L"); sp = []
    for k, (dx, dy, dz, h) in enumerate(((.02, -.05, 1, .2), (.07, .03, .9, .24), (.1, .1, .7, .17), (-.03, .09, 1, .14))):
        b = sh + Vector((.04 + .03*k, -.04 + .05*k, .08))
        tip = b + Vector((dx + .25, dy, dz)).normalized()*h
        sp += curve_tube(bone, [b, b.lerp(tip, .5) + Vector((0, 0, .02)), tip], .03, .01, verts=6)
    parts.append(rigid(sp, arm, "upper_arm.L"))
    # mão gigante: garras curvas
    fr = bone_frame("hand.L"); o, ax, up, sd = fr; cl = []
    for k in range(4):
        b = L(fr, .16, -.02, -.07 + .045*k)
        pts = bezier(b, b + ax*.06, b + ax*.12 + up*.02, b + ax*.14 + up*.09, n=4)
        cl += curve_tube(bone, pts, .02, .004, verts=6)
    cl.append(along("primitive_cone_add", bone, L(fr, .08, .06, .06), L(fr, .14, .13, .07), 1, radius1=.02, radius2=0, vertices=6))
    parts.append(rigid(cl, arm, "hand.L"))

    # --- braço direito humano: ataduras, braçadeira rebitada e ombreira de ferro
    o, ax, up, sd = bone_frame("forearm.R"); ln = (P("forearm.R", 1) - P("forearm.R")).length; br = []
    br.append(along("primitive_cylinder_add", iron, o + ax*ln*.35, o + ax*ln*.85, .07, vertices=10))
    for t in (.4, .6, .8):
        for a in range(0, 360, 60):
            w = up*math.cos(math.radians(a)) + sd*math.sin(math.radians(a))
            br.append(prim("primitive_uv_sphere_add", brass, o + ax*ln*t + w*.071, (.007,)*3, segments=6, ring_count=4))
    parts.append(rigid(br, arm, "forearm.R"))
    o, ax, up, sd = bone_frame("upper_arm.R"); ln = (P("upper_arm.R", 1) - P("upper_arm.R")).length; bd_ = []
    for k in range(5):
        t_ = prim("primitive_torus_add", bandage, o + ax*ln*(.3 + .12*k), (1,1,1), major_radius=.075, minor_radius=.008)
        _orient(t_, ax + up*.25*(1 if k % 2 else -1)); bd_.append(t_)
    parts.append(rigid(bd_, arm, "upper_arm.R"))
    parts.append(pauldron(arm, "R", iron, rust, brass, layers=2, spikes=iron))

    # --- tronco: arreio em X, cinturão com bolsas, emblema da Vigília (vela dentro da engrenagem)
    ch = []
    for s in (1, -1):
        ch.append(along("primitive_cube_add", leather, (.2*s, -.17, 1.47), (-.17*s, -.2, 1.0), .022))
        ch.append(along("primitive_cube_add", leather, (.2*s, .17, 1.47), (-.17*s, .19, 1.0), .022))
    gc = Vector((0, -.235, 1.25));
    ch.append(_orient(prim("primitive_cylinder_add", brass, gc, (.06, .06, .012), vertices=16), (0, -1, 0)))
    ch.append(_orient(prim("primitive_cylinder_add", dark, gc + Vector((0, -.008, 0)), (.038, .038, .008), vertices=16), (0, -1, 0)))
    for k in range(10):
        a = k*math.pi/5; d = Vector((math.cos(a), 0, math.sin(a)))
        ch.append(_orient(prim("primitive_cube_add", brass, gc + d*.068, (.012, .012, .012)), d))
    ch.append(prim("primitive_cylinder_add", bandage, gc + Vector((0, -.016, -.008)), (.011, .011, .02), vertices=8))
    ch.append(along("primitive_cone_add", ember, gc + Vector((0, -.018, .014)), gc + Vector((0, -.018, .05)), 1, radius1=.011, radius2=0, vertices=8))
    for k in range(5):   # cicatrizes e pústulas no peito
        ch.append(prim("primitive_uv_sphere_add", acid if k % 2 else bruise,
                       (rnd.uniform(.08, .2), -.2, rnd.uniform(1.12, 1.4)), (.013,)*3, segments=6, ring_count=4))
    # espinhos de osso ao longo da coluna (silhueta de corcunda)
    for k in range(5):
        b = Vector((0, .2 + .015*k, 1.48 - .09*k)); h = .17 - .025*k
        ch += curve_tube(bone, [b, b + Vector((0, .07, .05))*h/.12, b + Vector((0, .15, .14))*h/.17], .028 - .003*k, .006, verts=6)
    # lenço azul aço no pescoço, com pontas soltas
    ch.append(prim("primitive_torus_add", canvas, (0, -.01, 1.5), (1, 1.05, 1.0), (8, 0, 0), major_radius=.092, minor_radius=.03, major_segments=18, minor_segments=8))
    ch += curve_tube(canvas, [Vector((.05, .1, 1.49)), Vector((.08, .17, 1.38)), Vector((.06, .2, 1.24))], .035, .012, verts=6)
    parts.append(rigid(ch, arm, "chest"))
    bl = [prim("primitive_torus_add", leather, (0, 0, .99), (1.15, .95, 1.4), major_radius=.19, minor_radius=.022),
          prim("primitive_cube_add", iron, (0, -.205, .99), (.04, .012, .032))]
    for x, y in ((.17, -.12), (-.18, -.1), (.2, .06)):
        bl.append(prim("primitive_cube_add", dark, (x, y, .93), (.04, .03, .05)))
        bl.append(prim("primitive_cube_add", leather, (x, y - .006, .975), (.042, .032, .012)))
    bl += chain_links(iron, (-.2, -.08, .95), (-.05, -.21, .92), 7, .03)
    parts.append(rigid(bl, arm, "hips"))
    # kilt rasgado de lona azul da Vigília
    kr = [(.99, .23, .18, 0), (.85, .26, .21, .01), (.7, .28, .23, .02), (.58, .29, .24, .025)]
    kt = skirt("kilt", canvas, kr, open_front=.35, jag=.08, seed=4, folds=8, famp=.06)
    bind(kt, arm, ["hips", "thigh.L", "thigh.R"], power=3); parts.append(kt)

    # --- cabeça: tumor no crânio, chifres de osso nascendo, respirador com filtros e olhos verdes
    hd = [head_base(skin, (.082, .092, .1), z=1.66),
          prim("primitive_uv_sphere_add", bruise, (-.055, .0, 1.72), (.05, .055, .05)),
          prim("primitive_uv_sphere_add", skin, (-.04, .02, 1.75), (.04, .045, .035))]
    for s, b, tip in ((1, (.045, .02, 1.74), (.09, .07, 1.86)), (1, (.02, .05, 1.75), (.04, .11, 1.83))):
        hd += curve_tube(bone, [Vector(b), Vector(b).lerp(Vector(tip), .5) + Vector((.01, 0, .02)), Vector(tip)], .016, .004, verts=6)
    hd.append(along("primitive_cylinder_add", iron, (0, -.065, 1.61), (0, -.125, 1.595), .048, vertices=14))
    hd.append(along("primitive_cylinder_add", dark, (0, -.125, 1.595), (0, -.132, 1.593), .03, vertices=12))
    for s in (1, -1):
        hd.append(along("primitive_cylinder_add", rust, (.05*s, -.1, 1.6), (.09*s, -.13, 1.57), .028, vertices=10))
        hd.append(along("primitive_cylinder_add", iron, (.088*s, -.128, 1.572), (.096*s, -.134, 1.568), .03, vertices=10))
        hd.append(prim("primitive_uv_sphere_add", acid, (.034*s, -.09, 1.682), (.014, .007, .01)))
        hd.append(prim("primitive_uv_sphere_add", dark, (.034*s, -.084, 1.684), (.024, .012, .018)))
    hd += curve_tube(dark, [Vector((0, -.11, 1.57)), Vector((0, -.08, 1.5)), Vector((.05, .02, 1.48)), Vector((.08, .15, 1.45))], .012, .01, verts=6)
    hd.append(along("primitive_cube_add", leather, (-.085, -.02, 1.64), (.085, -.02, 1.64), .012))
    parts.append(rigid(hd, arm, "head"))

    # --- machado de placa de trânsito: cano grosso, placa dobrada com fio afiado soldado, corrente
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr
    perp = bd.cross(sd).normalized()
    w = [along("primitive_cylinder_add", iron, g - bd*.18, g + bd*.82, .02, vertices=10),
         along("primitive_cylinder_add", rust, g + bd*.6, g + bd*.84, .026, vertices=10)]
    for k in range(4): w.append(prim("primitive_torus_add", leather, g + bd*(-.08 + .045*k), (1,1,1), major_radius=.024, minor_radius=.007))
    pc = g + bd*.7 - perp*.12
    plate = _orient(prim("primitive_cylinder_add", sign, pc, (.16, .16, .007), vertices=8), sd); w.append(plate)
    w.append(_orient(prim("primitive_cylinder_add", iron, pc, (.17, .17, .005), vertices=8), sd))
    w.append(along("primitive_cube_add", steel, pc - perp*.17 + bd*.12, pc - perp*.17 - bd*.12, .012))
    for k in range(3): w.append(prim("primitive_uv_sphere_add", iron, g + bd*(.6 + .1*k) - perp*.02, (.014,)*3, segments=6, ring_count=4))
    stripe = along("primitive_cube_add", dark, pc - perp*.1 + bd*.08, pc + perp*.1 - bd*.08, 1); stripe.scale = (.02, .0085, .13); w.append(stripe)
    w.append(along("primitive_cone_add", iron, g + bd*.82, g + bd*.95, 1, radius1=.022, radius2=0, vertices=6))
    w += chain_links(iron, g - bd*.18, g - bd*.18 - up*.12 + sd*.03, 5, .0)
    parts.append(rigid(w, arm, "hand.R"))
    # corcunda: tronco para a frente, cabeça erguida para olhar adiante, braço gigante afastado do corpo
    return arm, {"rim": (.85, .75, .55), "anim": "melee",
                 "extra": {"upper_arm.L": {"y": -16}, "forearm.L": {"bend": -8}, "spine": {"x": 9}, "chest": {"x": 7},
                           "neck": {"x": -10}, "head": {"x": -8}}}
