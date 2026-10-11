# Gustavo, o Primarca: Tecnomancer mestre, guardião da Arca (NPC do armazém).
# Homenagem ao primeiro jogador do DARK PASSAGE. Estilo "Ferrugem Sagrada".
# Silhueta: coroa de válvulas atrás da cabeça (a única cor que brilha: âmbar de válvula),
# barba branca trançada com anéis de latão, lupa de três lentes, sobretudo até o chão com
# debrum de latão, manto acolchoado de isolamento, braço mecânico com manômetro e o
# cajado-chave "Chave-Mestra".
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from rig import *
from classes import bone_frame, L, body_parts, arc_tube, pauldron, chain_links, _apply_mods
from classes2 import curve_tube, bezier, head_base

VIOLETA = (.42, .18, 1)   # a válvula do Primarca acende roxa (mesma cor da Chave-Mestra, item Lendário)

def _flicker(m, base, n=8, seed=3):
    """Brilho das válvulas tremula de leve a cada quadro (corrente irregular da caldeira)."""
    b = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]; rnd = random.Random(seed)
    for f in range(1, 17):
        b.default_value = base*(1 + .22*math.sin(f*1.7) + rnd.uniform(-.12, .12))
        b.keyframe_insert("default_value", frame=f)

def gustavo_primarca():
    coat = mat("sobretudo_primarca", (.045,.06,.085), 0, .7, dirt=.5, grime=.9)
    lapel = mat("veludo_gasto", (.16,.035,.03), 0, .85, dirt=.55, grime=.4)
    mantle = mat("manto_isolante", (.19,.14,.085), 0, .95, dirt=.5, grime=.5)
    stitch = mat("costura_escura", (.04,.03,.02), 0, .9, dirt=.8, grime=0)
    dark = mat("couro_escuro_g", (.03,.022,.017), 0, .5, dirt=.7)
    leather = mat("couro_cinto", (.12,.065,.035), 0, .55, dirt=.6, grime=.6)
    pants = mat("calca_lona_g", (.05,.048,.042), 0, .85, dirt=.6)
    brass = mat("latao_primarca", (.6,.36,.1), 1, .3, dirt=.55, grime=.15)
    brass_dk = mat("latao_escuro", (.3,.17,.05), 1, .45, dirt=.5, grime=.2)
    copper = mat("cobre_g", (.45,.16,.06), 1, .4, dirt=.55, grime=.2)
    iron = mat("ferro_velho_g", (.1,.095,.09), 1, .5, dirt=.6, grime=.3)
    rubber = mat("borracha_cabo", (.025,.022,.02), 0, .6, dirt=.8, grime=0)
    skin = mat("pele_velha", (.34,.22,.17), 0, .6, dirt=.7, grime=.3)
    beard = mat("barba_branca", (.6,.57,.52), 0, .8, dirt=.7, grime=0)
    glassd = mat("vidro_escuro", (.05,.07,.07), .5, .1, dirt=1, grime=0)
    dial = mat("mostrador", (.5,.46,.36), 0, .6, dirt=.6, grime=0)
    tube = mat("valvula_roxa", (.75,.55,1), emit=VIOLETA, strength=5)
    bulb = mat("vidro_valvula", (.4,.25,.6), emit=VIOLETA, strength=1.1)
    _flicker(tube, 5)
    _flicker(bulb, 1.1, seed=5)
    arm = make_armature("gustavo_primarca")
    parts = body_parts(arm, pants, dark, coat, {"L": iron, "R": dark}, cuff=.07, sleeve_r=1.18, top_r=1.1,
                       boot_top=.34, buckle=brass, m_arms={"L": iron, "R": coat}, arm_scale={"L": .92, "R": 1.0})

    # ------------------------------------------------ sobretudo até o chão, debrum duplo de latão
    OF = .38
    rings = [(1.05,.18,.14,0), (.9,.215,.165,.006), (.7,.25,.19,.012), (.5,.28,.215,.02), (.3,.305,.235,.026), (.12,.322,.25,.03), (.06,.326,.252,.03)]
    sk = skirt("sobretudo_g", coat, rings, open_front=OF, jag=.03, seed=41, folds=9, famp=.05)
    bind(sk, arm, ["hips","spine","thigh.L","thigh.R"], power=3); parts.append(sk)
    for z0, z1 in ((.15, .12), (.095, .065)):
        hem = skirt("debrum_g", brass, [(z0,.318,.247,.03), (z1,.324,.251,.03)], open_front=OF, seed=41, folds=9, famp=.05, thick=.008)
        bind(hem, arm, ["hips","thigh.L","thigh.R"], power=3); parts.append(hem)
    # faixas bordadas de latão nas duas bordas da abertura, com botões de válvula apagada
    edge = []
    for s in (1, -1):
        a = -math.pi/2 + OF*s
        pts = [Vector((rx*1.015*math.cos(a), yo + ry*1.015*math.sin(a), z)) for z, rx, ry, yo in rings]
        for p, q in zip(pts[:-1], pts[1:]): edge.append(along("primitive_cylinder_add", brass, p, q, .009, vertices=6))
        for p, q in zip(pts[:-1], pts[1:]):
            edge.append(along("primitive_cylinder_add", lapel, p + Vector((-.012*s, -.004, 0)), q + Vector((-.012*s, -.004, 0)), .012, vertices=6))
        for t in (.2, .45, .7):
            k = t*(len(pts)-1); i = int(k); p = pts[i].lerp(pts[i+1], k - i)
            edge.append(prim("primitive_uv_sphere_add", brass_dk, p + Vector((.0, -.01, 0)), (.013,)*3, segments=8, ring_count=5))
    sk2 = rigid(edge, arm, "hips"); parts.append(sk2)

    # ------------------------------------------------ manto acolchoado de isolamento nos ombros
    mr = [(1.58,.1,.09,0), (1.53,.21,.16,0), (1.45,.31,.22,.006), (1.34,.365,.26,.012), (1.2,.385,.28,.018), (1.12,.39,.285,.02)]
    ma = skirt("manto", mantle, mr, open_front=.42, jag=.05, seed=12, folds=12, famp=.06)
    bind(ma, arm, ["chest","neck","spine","upper_arm.L","upper_arm.R"], power=3); parts.append(ma)
    for z, rx, ry in ((1.43,.318,.226), (1.32,.37,.264), (1.2,.389,.283)):
        st = skirt("pesponto", stitch, [(z+.006,rx,ry,.01), (z-.006,rx*1.004,ry*1.004,.01)], open_front=.42, seed=12, folds=12, famp=.06, thick=.006)
        bind(st, arm, ["chest","neck","spine","upper_arm.L","upper_arm.R"], power=3); parts.append(st)
    # gola alta de couro com fivelas
    col = skirt("gola", dark, [(1.6,.092,.088,.02), (1.55,.1,.095,.01), (1.5,.12,.105,0)], open_front=1.1, seed=3, thick=.012)
    bind(col, arm, ["neck","chest","head"], power=3); parts.append(col)

    # ------------------------------------------------ peito: medalhão da engrenagem, cinto, chaveiro
    ch = []
    gc = Vector((0, -.175, 1.3))
    ch.append(prim("primitive_cylinder_add", brass, gc, (.06,.06,.008), (90,0,0), vertices=24))
    for k in range(12):
        a = k*math.pi/6
        ch.append(prim("primitive_cube_add", brass, gc + Vector((math.cos(a)*.068, 0, math.sin(a)*.068)), (.012,.008,.01), (0, -math.degrees(a), 0)))
    ch.append(prim("primitive_cylinder_add", iron, gc + Vector((0,-.008,0)), (.032,.032,.008), (90,0,0), vertices=16))
    # vela da Vigília gravada no medalhão
    ch.append(along("primitive_cylinder_add", brass_dk, gc + Vector((0,-.018,-.02)), gc + Vector((0,-.018,.012)), .007, vertices=6))
    ch.append(prim("primitive_cone_add", brass_dk, gc + Vector((0,-.018,.022)), (1,1,1), (0,0,0), radius1=.007, radius2=0, depth=.02, vertices=6))
    for s in (1, -1):  # correntes do medalhão até o manto
        ch += chain_links(brass_dk, gc + Vector((.06*s, 0, .02)), Vector((.17*s, -.14, 1.44)), 6, .02)
    parts.append(rigid(ch, arm, "chest"))
    bl = [prim("primitive_torus_add", leather, (0, 0, 1.0), (1, .78, 1.5), major_radius=.172, minor_radius=.02),
          prim("primitive_cube_add", brass, (0, -.137, 1.0), (.034, .01, .03)),
          prim("primitive_cube_add", iron, (0, -.143, 1.0), (.016, .006, .016))]
    # bolsas de ferramentas e o chaveiro com as chaves das covas da Arca
    for s, x in ((1, .15), (-1, -.13)):
        bl.append(prim("primitive_cube_add", leather, (x, -.08, .94), (.035, .03, .045)))
        bl.append(prim("primitive_cube_add", brass_dk, (x, -.112, .965), (.012, .004, .008)))
    kr = Vector((.2, -.03, .9))
    bl.append(prim("primitive_torus_add", brass, kr, (1,1,1), (90, 0, 20), major_radius=.04, minor_radius=.005))
    rnd = random.Random(8)
    for k in range(9):
        a = math.radians(-160 + k*16)
        top = kr + Vector((math.cos(a)*.04, 0, math.sin(a)*.04))
        d = Vector((rnd.uniform(-.25,.25), rnd.uniform(-.2,.1), -1)).normalized()
        km = brass if k % 3 else iron
        bl.append(along("primitive_cylinder_add", km, top, top + d*.075, .0035, vertices=5))
        bl.append(prim("primitive_cube_add", km, top + d*.07 + Vector((.006,0,0)), (.008,.002,.006)))
        bl.append(prim("primitive_torus_add", km, top + d*.006, (1,1,1), (90,0,0), major_radius=.008, minor_radius=.0025, major_segments=8, minor_segments=4))
    parts.append(rigid(bl, arm, "hips"))
    parts.append(pauldron(arm, "R", coat, brass, brass, layers=2))

    # ------------------------------------------------ costas: caldeira e a Coroa de Válvulas
    bk = []
    bk.append(prim("primitive_cylinder_add", copper, (0,.24,1.3), (.12,.1,.2), vertices=20))
    bk.append(prim("primitive_uv_sphere_add", copper, (0,.24,1.5), (.12,.1,.05)))
    bk.append(prim("primitive_uv_sphere_add", copper, (0,.24,1.1), (.12,.1,.04)))
    for z in (1.15, 1.3, 1.45): bk.append(prim("primitive_torus_add", brass, (0,.24,z), (1,.84,1), major_radius=.122, minor_radius=.009))
    bk.append(prim("primitive_cylinder_add", dial, (.0,.346,1.32), (.04,.04,.006), (90,0,0), vertices=16))
    bk.append(prim("primitive_torus_add", brass, (.0,.352,1.32), (1,1,1), (90,0,0), major_radius=.042, minor_radius=.006))
    # coroa: arco vertical atrás da cabeça, sete válvulas em leque (o "halo" do Primarca)
    C = Vector((0, .2, 1.66)); R = .3
    Rm = Matrix.Rotation(math.radians(-12), 3, 'X')   # inclina um pouco para trás
    def ap(a, r=R): return C + Rm @ Vector((r*math.cos(a), 0, r*math.sin(a)))
    seg = 22; a0, a1 = math.radians(8), math.radians(172)
    for i in range(seg):
        p, q = ap(a0 + (a1-a0)*i/seg), ap(a0 + (a1-a0)*(i+1)/seg)
        bk.append(along("primitive_cylinder_add", brass, p, q, .016, vertices=8))
        p2, q2 = ap(a0 + (a1-a0)*i/seg, R - .05), ap(a0 + (a1-a0)*(i+1)/seg, R - .05)
        bk.append(along("primitive_cylinder_add", brass_dk, p2, q2, .007, vertices=6))
    for a in (a0, a1):  # hastes do arco até a caldeira
        bk.append(along("primitive_cylinder_add", iron, ap(a), Vector((.1*math.cos(a)/abs(math.cos(a)), .26, 1.42)), .014, vertices=8))
    for k in range(7):
        a = math.radians(24 + k*22)
        b = ap(a); d = (b - C).normalized()
        h = .13 if k == 3 else .1
        bk.append(along("primitive_cylinder_add", brass, b - d*.02, b + d*.03, .022, vertices=10))     # soquete
        bk.append(along("primitive_cylinder_add", bulb, b + d*.03, b + d*(.03 + h), .02, vertices=10))  # bulbo
        bk.append(along("primitive_cylinder_add", tube, b + d*.045, b + d*(.02 + h), .009, vertices=8))   # filamento
        bk.append(prim("primitive_uv_sphere_add", bulb, b + d*(.03 + h), (.02,)*3, segments=10, ring_count=6))
        bk.append(along("primitive_cone_add", brass_dk, b + d*(.045 + h), b + d*(.085 + h), 1, radius1=.008, radius2=0, vertices=6))
        if k < 6:  # raios de ferro entre as válvulas
            a2 = a + math.radians(11); b2 = ap(a2); d2 = (b2 - C).normalized()
            bk.append(along("primitive_cone_add", iron, b2, b2 + d2*.07, 1, radius1=.008, radius2=0, vertices=5))
    # feixes de cabos da caldeira descendo pelos ombros até o peito
    for s in (1, -1):
        for j, off in enumerate((0, .025, .05)):
            pts = bezier((.07*s + off*s*.4, .3, 1.42), (.2*s, .28, 1.62 - off), (.26*s + off*s*.3, -.08, 1.56 - off), (.11*s + off*s, -.17, 1.36 - off*1.4), 7)
            bk += curve_tube(rubber if j != 1 else copper, pts, .011, .011, 6)[:-1]
    parts.append(rigid(bk, arm, "chest"))

    # ------------------------------------------------ braço mecânico esquerdo com manômetro e garra
    for bn in ("upper_arm.L", "forearm.L"):
        o, ax, up, sd = bone_frame(bn); ln = (P(bn, 1) - P(bn)).length
        mc = [along("primitive_cylinder_add", brass, o + ax*ln*.12 + up*.055, o + ax*ln*.62 + up*.055, .018, vertices=8),
              along("primitive_cylinder_add", iron, o + ax*ln*.62 + up*.055, o + ax*ln*.95 + up*.055, .01, vertices=8),
              along("primitive_cylinder_add", copper, o + ax*ln*.15 - up*.05, o + ax*ln*.85 - up*.05, .008, vertices=6),
              prim("primitive_uv_sphere_add", brass, o + ax*ln, (.046,)*3, segments=12, ring_count=8)]
        for t in (.25, .5, .75):
            mc.append(prim("primitive_torus_add", brass_dk, o + ax*ln*t, (1,1,1), major_radius=.054, minor_radius=.008))
            mc[-1].rotation_euler = ax.to_track_quat('Z','Y').to_euler()
        if bn == "forearm.L":
            gp = o + ax*ln*.45 + sd*.058
            g = prim("primitive_cylinder_add", dial, gp, (.03,.03,.008), vertices=16); g.rotation_euler = sd.to_track_quat('Z','Y').to_euler(); mc.append(g)
            g = prim("primitive_torus_add", brass, gp + sd*.004, (1,1,1), major_radius=.032, minor_radius=.006); g.rotation_euler = sd.to_track_quat('Z','Y').to_euler(); mc.append(g)
            mc.append(along("primitive_cylinder_add", stitch, gp + sd*.006, gp + sd*.006 + ax*.02 + up*.01, .0025, vertices=4))
        parts.append(rigid(mc, arm, bn))
    fr = bone_frame("hand.L"); o, ax, up, sd = fr
    cl = [prim("primitive_uv_sphere_add", brass, L(fr, .03), (.035,)*3, segments=10, ring_count=6)]
    for k in (-1.5, -.5, .5, 1.5):
        a, b, c = L(fr, .05, 0, .018*k), L(fr, .1, -.02, .022*k), L(fr, .14, -.05, .02*k)
        cl += [along("primitive_cylinder_add", iron, a, b, .007, vertices=6), prim("primitive_uv_sphere_add", brass, b, (.009,)*3, segments=6, ring_count=4),
               along("primitive_cone_add", iron, b, c, 1, radius1=.007, radius2=.001, vertices=5)]
    parts.append(rigid(cl, arm, "hand.L"))

    # ------------------------------------------------ cabeça: calva, barba trançada, lupa de três lentes
    hd = [head_base(skin, (.08,.09,.1), 1.67)]
    hd.append(along("primitive_cone_add", skin, (0,-.085,1.66), (0,-.112,1.635), 1, radius1=.018, radius2=.006, vertices=8))  # nariz
    for s in (1, -1):  # orelhas e sobrancelhas grossas
        hd.append(prim("primitive_uv_sphere_add", skin, (.08*s,-.005,1.665), (.012,.022,.03), segments=8, ring_count=6))
        hd.append(along("primitive_cone_add", beard, (.012*s,-.088,1.705), (.06*s,-.07,1.715), 1, radius1=.012, radius2=.004, vertices=5))
    rnd = random.Random(21)
    for k in range(26):   # cabelo branco só nas laterais e na nuca, puxado para trás
        a = rnd.uniform(-.35*math.pi, 1.35*math.pi)
        if -math.pi/2 - .9 < a - 2*math.pi < -math.pi/2 + .9 or -math.pi/2 - .9 < a < -math.pi/2 + .9: continue
        b = Vector((math.cos(a)*.082, math.sin(a)*.088 + .01, rnd.uniform(1.62, 1.7)))
        d = Vector((math.cos(a)*.3, .6 + abs(math.sin(a))*.3, -.75)).normalized()
        hd.append(along("primitive_cone_add", beard, b, b + d*rnd.uniform(.08, .14), 1, radius1=.018, radius2=0, vertices=5))
    # bigode
    for s in (1, -1):
        hd += curve_tube(beard, bezier((0,-.105,1.625), (.03*s,-.11,1.62), (.055*s,-.1,1.6), (.065*s,-.09,1.57), 4), .012, .003, 6)
    # barba: massa de mechas do queixo até o peito
    for k in range(34):
        a = rnd.uniform(-math.pi*.95, -math.pi*.05)
        b = Vector((math.cos(a)*.072, -.02 + math.sin(a)*.07, rnd.uniform(1.58, 1.63)))
        tip = Vector((b.x*.7 + rnd.uniform(-.02,.02), b.y - .05 - rnd.uniform(0,.03), rnd.uniform(1.4, 1.48)))
        mid = b.lerp(tip, .5) + Vector((0, -.035, 0))
        hd += curve_tube(beard, [b, mid, tip], .02, .004, 5)
    # duas tranças com anéis de latão
    for s in (1, -1):
        p0 = Vector((.025*s,-.12,1.46)); p1 = Vector((.03*s,-.14,1.34))
        for k in range(5):
            q = p0.lerp(p1, k/4)
            hd.append(prim("primitive_uv_sphere_add", beard, q, (.014,.012,.02), segments=8, ring_count=5))
        for t in (.3, .7): hd.append(prim("primitive_torus_add", brass, p0.lerp(p1, t), (1,1,.7), major_radius=.015, minor_radius=.005, major_segments=10, minor_segments=4))
        hd.append(prim("primitive_cone_add", beard, p1 + Vector((0,0,-.02)), (1,1,1), (180,0,0), radius1=.013, radius2=0, depth=.04, vertices=6))
    # óculos: lente simples na esquerda, lupa de três lentes na direita, alça de couro
    hd.append(prim("primitive_torus_add", dark, (0,-.005,1.69), (1,1.08,1.2), major_radius=.088, minor_radius=.01))
    hd.append(along("primitive_cylinder_add", brass, (.037,-.085,1.685), (.04,-.105,1.685), .024, vertices=12))
    hd.append(along("primitive_cylinder_add", glassd, (.04,-.104,1.685), (.04,-.108,1.685), .019, vertices=12))
    base = Vector((-.038,-.085,1.685))
    for k, (ln, r) in enumerate(((.03, .026), (.03, .02), (.035, .014))):
        nb = base + Vector((-.002, -ln, 0))
        hd.append(along("primitive_cylinder_add", brass if k != 1 else copper, base, nb, r, vertices=12))
        hd.append(prim("primitive_torus_add", brass_dk, nb, (1,1,1), (90,0,0), major_radius=r, minor_radius=.004, major_segments=12, minor_segments=4))
        base = nb
    hd.append(along("primitive_cylinder_add", glassd, base, base + Vector((0,-.004,0)), .012, vertices=10))
    # lente pequena articulada de lado
    hd.append(along("primitive_cylinder_add", iron, (-.07,-.06,1.72), (-.07,-.1,1.74), .004, vertices=4))
    hd.append(along("primitive_cylinder_add", brass, (-.07,-.1,1.74), (-.07,-.108,1.742), .014, vertices=10))
    parts.append(rigid(hd, arm, "head"))

    # ------------------------------------------------ cajado-chave "Chave-Mestra"
    fr = bone_frame("hand.R"); o, ax, up, sd = fr; g = L(fr, .045)
    sf = [along("primitive_cylinder_add", iron, g - up*.84, g + up*.98, .016, vertices=8)]
    for k in range(5): sf.append(prim("primitive_torus_add", brass, g + up*(-.62 + .38*k), (1,1,1), major_radius=.022, minor_radius=.006))
    for o_ in sf[1:]: o_.rotation_euler = up.to_track_quat('Z','Y').to_euler()
    # anel da chave (no alto) com uma válvula ao centro
    kc = g + up*1.1; Rk = up.to_track_quat('Z','Y').to_matrix()
    n = 18
    for i in range(n):
        a, b = 2*math.pi*i/n, 2*math.pi*(i+1)/n
        p = kc + sd*(.1*math.cos(a)) + up*(.1*math.sin(a)); q = kc + sd*(.1*math.cos(b)) + up*(.1*math.sin(b))
        sf.append(along("primitive_cylinder_add", brass, p, q, .014, vertices=8))
        if i % 3 == 0:
            sf.append(along("primitive_cone_add", brass_dk, p, p + (p - kc).normalized()*.04, 1, radius1=.01, radius2=0, vertices=5))
    for a in (0, math.pi/2, math.pi, 3*math.pi/2):
        sf.append(along("primitive_cylinder_add", iron, kc, kc + sd*(.1*math.cos(a)) + up*(.1*math.sin(a)), .005, vertices=5))
    sf.append(along("primitive_cylinder_add", glassd, kc - ax*.03, kc + ax*.03, .032, vertices=12))
    sf.append(along("primitive_cylinder_add", tube, kc - ax*.035, kc + ax*.035, .016, vertices=10))
    for s in (1, -1): sf.append(along("primitive_cylinder_add", brass, kc + ax*.03*s, kc + ax*.045*s, .036, vertices=12))
    # dentes da chave perto do pé do cajado
    bit = g - up*.66
    for k, (h, w) in enumerate(((.05, .03), (.03, .04), (.06, .025))):
        c = bit - up*(.05*k) + sd*(.016 + w)
        sf.append(prim("primitive_cube_add", brass_dk, c, (w, .01, h*.4)))
        sf[-1].rotation_euler = Rk.to_euler()
    sf.append(prim("primitive_cone_add", iron, g - up*.88, (1,1,1), radius1=.02, radius2=0, depth=.08, vertices=8))
    sf[-1].rotation_euler = (-up).to_track_quat('Z','Y').to_euler()
    parts.append(rigid(sf, arm, "hand.R"))
    return arm, {"rim": (1, .55, .3), "anim": "primarca"}


def primarca_anims(arm):
    """Parado longo (8 quadros): respira, olha a lupa, a garra mecânica tamborila.
    Andar com o cajado e um gesto (attack) de bater o cajado no chão, para quando o jogo pedir."""
    import anims as A
    hold = merge(ARMS_DOWN, {"upper_arm.R": {"x": -10, "y": -6}, "forearm.R": {"bend": -60},
                             "chest": {"x": -2}, "head": {"x": -5}})
    idle = []
    for i in range(8):
        t = i/8*2*math.pi; b = math.sin(t)
        idle.append(merge(hold, {"chest": {"x": -1.4*b}, "head": {"x": 1.6*b + 3*max(0, math.sin(t*.5))**2, "z": 6*math.sin(t*.5)},
                                 "root": (0, 0, -.006*(1+b)),
                                 "upper_arm.L": {"x": -6 - 4*max(0, math.sin(t*.5)), "y": -2}, "forearm.L": {"bend": -28 - 14*max(0, math.sin(t*.5))},
                                 "hand.L": {"x": 10*math.sin(2*t)}}))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s = math.sin(t)
        walk.append(merge(hold, A.walk_legs(t, 18), {"upper_arm.L": {"x": 14*s}, "upper_arm.R": {"x": -8*s}, "head": {"z": 2*s}}))
    K = [(-10, -60, 0), (-30, -70, -4), (-55, -60, -6), (-40, -30, 2), (-12, -35, 6), (-8, -55, 3), (-10, -60, 0), (-10, -60, 0)]
    attack = [merge(ARMS_DOWN, {"upper_arm.R": {"x": ux, "y": -6}, "forearm.R": {"bend": fb}, "spine": {"x": cx}, "chest": {"x": -2 + cx},
                                "upper_arm.L": {"x": -10}, "forearm.L": {"bend": -30}, "root": (0, 0, -.004*abs(cx))}) for ux, fb, cx in K]
    return {"idle": make_action(arm, "idle", idle), "walk": make_action(arm, "walk", walk), "attack": make_action(arm, "attack", attack)}
