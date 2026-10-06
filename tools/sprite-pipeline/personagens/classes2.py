# Demônio e Cultista (Arautos do Juízo), Mutante e Tecnomancer (Vigília), estilo "Ferrugem Sagrada".
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from rig import *
from classes import (bone_frame, L, body_parts, feather, wing, arc_tube, pauldron, chain_links, _apply_mods)

def curve_tube(m, pts, r0, r1, verts=8):
    """Tubo afinando ao longo de uma polilinha (chifres, canos, mechas)."""
    out = []
    for i in range(len(pts)-1):
        t = i/(len(pts)-1); r = r0 + (r1-r0)*t
        if i == len(pts)-2:
            out.append(along("primitive_cone_add", m, pts[i], pts[i+1], 1, radius1=max(r, .002), radius2=0, vertices=verts))
        else:
            out.append(along("primitive_cylinder_add", m, pts[i], pts[i+1], max(r, .002), vertices=verts))
            out.append(prim("primitive_uv_sphere_add", m, pts[i+1], (max(r, .002),)*3, segments=verts, ring_count=4))
    return out

def bezier(p0, p1, p2, p3, n=8):
    p0, p1, p2, p3 = map(Vector, (p0, p1, p2, p3))
    return [((1-t)**3)*p0 + 3*((1-t)**2)*t*p1 + 3*(1-t)*t*t*p2 + t**3*p3 for t in (i/n for i in range(n+1))]

def mohawk(m, tip, n=9, h=.14, seed=3):
    rnd = random.Random(seed); out = []
    for i in range(n):
        y = -.07 + i*.022; z = 1.74 + .03*math.sin(i/(n-1)*math.pi)
        b = Vector((0, y, z)); d = Vector((0, .25 + .1*i/n, 1)).normalized()
        L_ = h*(1 - abs(i - n/2)/n*.8)*rnd.uniform(.85, 1.1)
        out.append(along("primitive_cone_add", m, b, b + d*L_*.7, 1, radius1=.022, radius2=.012, vertices=5))
        out.append(along("primitive_cone_add", tip, b + d*L_*.7, b + d*L_, 1, radius1=.012, radius2=0, vertices=5))
    return out

def bat_wing(arm, side, m_skin, m_bone, rnd_seed=5):
    n = "L" if side > 0 else "R"; rnd = random.Random(rnd_seed + (0 if side > 0 else 9))
    root = P(f"wing.{n}"); el = Vector((.32*side, .3, 1.8)); wr = Vector((.58*side, .44, 1.72))
    tips = [Vector((.98*side, .52, 1.52)), Vector((.95*side, .58, 1.12)), Vector((.74*side, .52, .84)), Vector((.46*side, .4, .76))]
    body = Vector((.13*side, .2, 1.02))
    outer = tips + [body, root, el]
    bm = bmesh.new(); N = 7
    for A, B in zip(outer[:-1], outer[1:]):
        rows = [[bm.verts.new(wr)]]
        for k in range(1, N+1):
            row = []
            for j in range(k+1):
                u = j/k; e = A.lerp(B, u)
                sag = .22*math.sin(math.pi*u)*(k/N)**2 if (A in tips or B in tips) else .06*math.sin(math.pi*u)*(k/N)**2
                e = e.lerp(wr, sag)
                p = wr.lerp(e, k/N) + Vector((0, .04*math.sin(math.pi*u)*k/N, 0))
                row.append(bm.verts.new(p))
            rows.append(row)
        for k in range(N):
            r0, r1 = rows[k], rows[k+1]
            for j in range(len(r1)-1):
                torn = k > N*.5 and rnd.random() < .07
                if not torn: bm.faces.new((r1[j], r1[j+1], r0[min(j, len(r0)-1)]))
                if j < len(r0)-1 and not (torn and rnd.random() < .5): bm.faces.new((r0[j], r1[j+1], r0[j+1]))
    memb = obj_from_bm(f"membrana_morcego.{n}", bm, m_skin)
    memb.modifiers.new("s", 'SOLIDIFY').thickness = .006; _apply_mods(memb)
    bones = [along("primitive_cylinder_add", m_bone, root, el, .03, vertices=8), along("primitive_cylinder_add", m_bone, el, wr, .025, vertices=8)]
    for t in tips: bones += curve_tube(m_bone, [wr, wr.lerp(t, .5) + Vector((0, .03, .02)), t], .018, .006, 6)
    bones.append(along("primitive_cone_add", m_bone, el, el + Vector((.03*side, -.03, .13)), 1, radius1=.025, radius2=0, vertices=6))
    return rigid([memb] + bones, arm, f"wing.{n}")

def head_base(m, scale=(.08,.09,.105), z=1.67):
    return prim("primitive_uv_sphere_add", m, (0,-.012,z), scale)

def weapon_frame():
    fr = bone_frame("hand.R"); o, ax, up, sd = fr
    return fr, (ax*.45 + up*.9).normalized(), L(fr, .045)

# ====================================================================== DEMÔNIO
def demonio():
    leather = mat("couro_negro", (.016,.013,.014), .1, .35, dirt=.7)
    flesh = mat("carne_demoniaca", (.16,.035,.028), 0, .45, dirt=.65, grime=.6)
    pants = mat("calca_rasgada", (.03,.026,.026), 0, .8, dirt=.6)
    brass = mat("latao_velho", (.5,.27,.07), 1, .4, dirt=.5, grime=.3)
    iron = mat("ferro_velho", (.1,.095,.09), 1, .5, dirt=.6, grime=.3)
    horn = mat("chifre", (.07,.055,.045), 0, .35, dirt=.6, grime=.2)
    hair = mat("moicano_vermelho", (.3,.02,.012), 0, .6, dirt=.8, grime=0)
    wingm = mat("asa_couro", (.035,.012,.012), 0, .55, dirt=.55, grime=.5)
    ember = mat("brasa", (1,.4,.08), emit=(1,.35,.05), strength=5)
    arm = make_armature("demonio", wings=True)
    parts = body_parts(arm, pants, leather, flesh, leather, cuff=.05, buckle=brass, top_r=1.08, m_arms={"L": flesh, "R": flesh},
                       arm_scale={"L": 1.15, "R": 1.15})
    # sobretudo de couro sem mangas, bem aberto mostrando o peito
    coat = skirt("sobretudo_sem_manga", leather, [(1.5,.2,.135,0), (1.32,.205,.145,.005), (1.08,.185,.14,.01), (.86,.22,.17,.015),
                 (.6,.26,.2,.025), (.36,.29,.225,.035), (.2,.305,.24,.04)], open_front=.95, jag=.06, seed=12, folds=8, famp=.06)
    bind(coat, arm, ["chest","spine","hips","thigh.L","thigh.R"], power=3); parts.append(coat)
    ch = []
    # rachaduras de brasa no peito (o brilho da classe)
    rnd = random.Random(3)
    for x0 in (-.05, .04):
        p = Vector((x0, -.165, 1.42))
        for k in range(6):
            q = p + Vector((rnd.uniform(-.04, .04), -.004*k, -.06))
            ch.append(along("primitive_cube_add", ember, p, q, .0035)); p = q
            if k in (1, 3): ch.append(along("primitive_cube_add", ember, p, p + Vector((rnd.choice((-1,1))*.035, -.003, -.02)), .0025))
    ch.append(along("primitive_cube_add", ember, (0,-.17,1.25), (.05,-.165,1.16), .005))
    # coleira de espinhos
    ch.append(prim("primitive_torus_add", leather, (0,-.005,1.52), (1,1,1.6), major_radius=.075, minor_radius=.016))
    for k in range(8):
        a = math.radians(k*45); d = Vector((math.cos(a), math.sin(a), 0))
        b = Vector((0,-.005,1.52)) + d*.085
        ch.append(along("primitive_cone_add", iron, b, b + d*.05, 1, radius1=.012, radius2=0, vertices=5))
    ch.append(along("primitive_cube_add", leather, (.15,.15,1.42), (-.15,.15,1.42), .02))
    parts.append(rigid(ch, arm, "chest"))
    parts.append(pauldron(arm, "L", leather, iron, iron, layers=2, spikes=iron))
    # corrente enrolada no antebraço direito
    o, ax, up, sd = bone_frame("forearm.R")
    ring = []
    for k in range(9):
        c = o + ax*(.04 + .02*k)
        ring.append(prim("primitive_torus_add", iron, c, (1,1,1), major_radius=.06, minor_radius=.006, major_segments=10, minor_segments=4))
        ring[-1].rotation_euler = ax.to_track_quat('Z','Y').to_euler(); ring[-1].rotation_euler.x += .3*(k%2)
    parts.append(rigid(ring, arm, "forearm.R"))
    parts.append(rigid(chain_links(iron, (-.1,-.15,.95), (.12,-.12,.86), 8, sag=.06), arm, "hips"))
    # cabeça: carne, olhos de brasa, chifres com argolas de latão, moicano vermelho
    hd = [head_base(flesh, (.078,.088,.104))]
    hd.append(prim("primitive_uv_sphere_add", flesh, (0,-.06,1.6), (.06,.05,.04)))   # mandíbula
    for s in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", ember, (.03*s,-.09,1.685), (.014,.006,.008)))
        pts = bezier((.055*s,-.02,1.74), (.11*s,-.02,1.82), (.17*s,.04,1.9), (.15*s,.12,1.98), 6)
        hd += curve_tube(horn, pts, .03, .005, 8)
        hd.append(prim("primitive_torus_add", brass, pts[2], (1,1,1), major_radius=.024, minor_radius=.006))
    hd += mohawk(hair, hair, n=8, h=.15)
    parts.append(rigid(hd, arm, "head"))
    parts.append(bat_wing(arm, 1, wingm, horn)); parts.append(bat_wing(arm, -1, wingm, horn))
    # lâmina curva serrilhada com fio de brasa
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr
    w = [along("primitive_cylinder_add", leather, g - bd*.1, g + bd*.08, .018, vertices=8),
         along("primitive_cube_add", iron, g + bd*.08 + sd*.09, g + bd*.08 - sd*.09, .02)]
    perp = bd.cross(sd).normalized()
    bm = bmesh.new(); prev = None; spine_ = []
    for k in range(9):  # lâmina larga e curva no plano (bd, perp), alargando para a ponta
        t = k/8; c = g + bd*(.09 + .72*t) + perp*(.06*t*t); wdt = .045 + .04*math.sin(math.pi*min(t*1.2, 1)) if k < 8 else .0
        pair = (bm.verts.new(c + perp*.015), bm.verts.new(c - perp*(wdt + .01)))
        if prev: bm.faces.new((prev[0], prev[1], pair[1], pair[0]))
        prev = pair; spine_.append((c, wdt))
    bo = obj_from_bm("cutelo", bm, iron); bo.modifiers.new("s", 'SOLIDIFY').thickness = .012; _apply_mods(bo); w.append(bo)
    for k in range(8):
        (a_, wa), (b_, wb) = spine_[k], spine_[k+1]
        w.append(along("primitive_cube_add", ember, a_ - perp*(wa + .012), b_ - perp*(wb + .012), .0045))
        if k in (2, 4, 6): w.append(along("primitive_cone_add", iron, a_ + perp*.012, a_ + perp*.06 + bd*.03, 1, radius1=.014, radius2=0, vertices=4))
    parts.append(rigid(w, arm, "hand.R"))
    return arm, {"rim": (1, .25, .15), "anim": "melee"}

# ====================================================================== CULTISTA
def cultista():
    wine = mat("vinho_batina", (.15,.012,.018), 0, .7, dirt=.5, grime=1.1)
    wine2 = mat("vinho_remendo", (.09,.02,.02), 0, .75, dirt=.6, grime=.8)
    bone = mat("osso_mascara", (.55,.5,.4), 0, .5, dirt=.55, grime=.3)
    bandage = mat("atadura", (.45,.4,.32), 0, .8, dirt=.5, grime=.4)
    blood = mat("sangue_seco", (.15,.01,.008), 0, .4, dirt=.7, grime=.2)
    rope = mat("corda", (.3,.24,.15), 0, .9, dirt=.6, grime=.3)
    brass = mat("latao_velho", (.5,.27,.07), 1, .4, dirt=.5, grime=.3)
    iron = mat("ferro_velho", (.1,.095,.09), 1, .5, dirt=.6, grime=.3)
    book = mat("couro_grimorio", (.05,.02,.015), 0, .5, dirt=.6, grime=.2)
    wax = mat("cera", (.55,.5,.38), 0, .4, dirt=.6, grime=.2)
    lens = mat("lente_vermelha", (1,.1,.05), emit=(1,.08,.03), strength=10)
    flame = mat("chama_vela", (1,.35,.1), emit=(1,.3,.08), strength=6)
    burst = mat("rajada_sangue", (1,.12,.04), emit=(1,.08,.02), strength=4)
    arm = make_armature("cultista")
    parts = body_parts(arm, wine2, book, wine, bandage, cuff=.09, sleeve_r=1.3, top_r=1.06, boot_top=.25)
    # túnica até o chão, com dobras e remendos
    t = skirt("tunica", wine, [(1.2,.17,.13,0), (1.0,.2,.155,.005), (.75,.25,.19,.012), (.5,.29,.22,.02), (.25,.32,.245,.028), (.04,.34,.26,.035)],
              open_front=0, jag=.03, seed=21, folds=11, famp=.06)
    bind(t, arm, ["spine","hips","thigh.L","thigh.R"], power=3); parts.append(t)
    # manto e capuz pontudo
    mant = skirt("manto", wine2, [(1.56,.12,.1,0), (1.46,.24,.17,0), (1.3,.3,.21,.01), (1.16,.32,.23,.015)], open_front=0, jag=.03, seed=4, folds=12, famp=.05)
    bind(mant, arm, ["chest","neck","upper_arm.L","upper_arm.R"], power=3); parts.append(mant)
    hood = skirt("capuz", wine, [(1.56,.11,.11,.0), (1.68,.115,.125,.015), (1.8,.105,.12,.03), (1.92,.075,.09,.05), (2.02,.035,.045,.08), (2.08,.006,.008,.11)],
                 open_front=.75, seed=6, folds=6, famp=.04, thick=.014)
    # remendos costurados
    ch = [prim("primitive_cube_add", wine2, (.08,-.16,1.15), (.04,.01,.05), (0,0,8)),
          prim("primitive_cube_add", wine2, (-.1,-.15,1.32), (.035,.01,.03), (0,0,-12))]
    # colar de contas de osso
    for k in range(11):
        a = math.radians(200 + k*14)
        ch.append(prim("primitive_uv_sphere_add", bone, (.13*math.cos(a), -.03 + .13*math.sin(a)*.95, 1.42 - .1*math.sin(math.radians(k*16.4))), (.016,)*3, segments=8, ring_count=5))
    # velas no ombro esquerdo
    for k, (x, y, h) in enumerate(((.2,.02,.1), (.25,.06,.07), (.17,.08,.12))):
        c = prim("primitive_cylinder_add", wax, (x, y, 1.5 + h/2), (.016,.016,h/2), vertices=8); ch.append(c)
        ch.append(prim("primitive_uv_sphere_add", flame, (x, y, 1.5 + h + .018), (.008,.008,.018), segments=6, ring_count=4))
        ch.append(prim("primitive_cone_add", wax, (x, y, 1.5 + .01), (1,1,1), radius1=.03, radius2=.016, depth=.03, vertices=8))
    parts.append(rigid(ch, arm, "chest"))
    # cinto de corda, grimório acorrentado
    hp = [prim("primitive_torus_add", rope, (0,0,1.03), (1,.8,1.4), major_radius=.18, minor_radius=.016)]
    hp += [along("primitive_cylinder_add", rope, (.06,-.16,1.02), (.08,-.18,.7), .012, vertices=6),
           along("primitive_cylinder_add", rope, (.04,-.16,1.02), (.03,-.185,.75), .012, vertices=6)]
    hp.append(prim("primitive_cube_add", book, (-.2,-.06,.86), (.03,.075,.095), (0,0,10)))
    hp.append(prim("primitive_cube_add", bone, (-.205,-.06,.86), (.027,.07,.088), (0,0,10)))  # folhas
    hp.append(prim("primitive_uv_sphere_add", blood, (-.235,-.06,.88), (.004,.02,.02)))
    hp += chain_links(iron, (-.16,-.12,1.0), (-.2,-.1,.95), 5, sag=.02)
    parts.append(rigid(hp, arm, "hips"))
    # máscara de gás de osso com lentes vermelhas (único brilho)
    hd = [head_base(bandage, (.078,.088,.104)), prim("primitive_uv_sphere_add", bone, (0,-.045,1.66), (.078,.07,.095))]
    for s in (1, -1):
        hd.append(along("primitive_cylinder_add", iron, (.035*s,-.1,1.69), (.038*s,-.118,1.69), .026, vertices=12))
        hd.append(along("primitive_cylinder_add", lens, (.038*s,-.117,1.69), (.039*s,-.121,1.69), .02, vertices=12))
    hd.append(along("primitive_cylinder_add", iron, (0,-.1,1.61), (0,-.15,1.58), .028, vertices=10))
    hd.append(along("primitive_cylinder_add", bone, (0,-.15,1.58), (0,-.17,1.57), .033, vertices=10))
    hd.append(prim("primitive_cube_add", blood, (-.03,-.11,1.63), (.012,.003,.02)))
    parts.append(rigid(hd + [hood], arm, "head"))
    # mãos enfaixadas manchadas de sangue
    for n in "LR":
        fr = bone_frame(f"hand.{n}")
        parts.append(rigid([prim("primitive_uv_sphere_add", blood, L(fr, .05, 0, .02), (.018,.012,.02))], arm, f"hand.{n}"))
    # incensário de latão pendurado na mão direita
    fr = bone_frame("hand.R"); o, ax, up, sd = fr; g = L(fr, .05)
    cz = chain_links(iron, g, g + ax*.32, 8, sag=0)
    c = g + ax*.4
    cz.append(prim("primitive_uv_sphere_add", brass, c, (.055,.055,.06), segments=12, ring_count=8))
    cz.append(prim("primitive_cone_add", brass, c - ax*.06, (1,1,1), radius1=.035, radius2=.01, depth=.04, vertices=10))
    for k in range(6):
        a = k*math.pi/3
        cz.append(prim("primitive_uv_sphere_add", lens, c + up*.05*math.cos(a) + sd*.05*math.sin(a), (.008,)*3, segments=6, ring_count=4))
    parts.append(rigid(cz, arm, "hand.R"))
    fx = rigid([prim("primitive_uv_sphere_add", burst, c, (.1,.1,.1)),
                along("primitive_cone_add", burst, c, c + up*.0 + ax*.0 - Vector((0, .0, 0)) + (ax*.5), 1, radius1=.1, radius2=0, vertices=8)], arm, "hand.R")
    fx.name = "rajada"
    return arm, {"rim": (1, .28, .18), "anim": "caster", "flash": fx,
                 "hold_extra": {"forearm.R": {"bend": 48}, "upper_arm.R": {"x": 8}}}

# ====================================================================== MUTANTE
def mutante():
    plague = mat("pele_praga", (.15,.17,.1), 0, .5, dirt=.6, grime=.5)
    plague2 = mat("pele_praga_escura", (.08,.1,.05), 0, .5, dirt=.6, grime=.4)
    vest = mat("colete_couro", (.04,.03,.022), 0, .5, dirt=.65)
    pants = mat("calca_lona", (.05,.048,.042), 0, .85, dirt=.6)
    boot = mat("couro_escuro", (.03,.022,.017), 0, .5, dirt=.7)
    rust = mat("placa_ferrugem", (.2,.09,.04), .6, .7, dirt=.5, grime=.3)
    iron = mat("ferro_velho", (.1,.095,.09), 1, .5, dirt=.6, grime=.3)
    rubber = mat("pneu", (.015,.015,.015), 0, .85, dirt=.7, grime=.2)
    brass = mat("latao_velho", (.5,.27,.07), 1, .4, dirt=.5, grime=.3)
    sign = mat("placa_amarela", (.6,.45,.05), .3, .5, dirt=.5, grime=.2)
    claw = mat("garra", (.4,.37,.3), 0, .4, dirt=.6, grime=.2)
    acid = mat("verde_acido", (.3,1,.1), emit=(.4,1,.1), strength=3)
    arm = make_armature("mutante")
    parts = body_parts(arm, pants, boot, vest, {"L": plague, "R": plague}, cuff=.05, buckle=iron, top_r=1.2, legs_r=1.18,
                       m_arms={"L": plague, "R": plague}, arm_scale={"L": 2.1, "R": 1.15}, glove_scale={"L": 2.1, "R": 1.0})
    # garras no braço gigante, pústulas e veias de ácido
    fr = bone_frame("hand.L"); o, ax, up, sd = fr
    cl = []
    for k in range(4):
        b = L(fr, .13, -.03 + .0*k, -.06 + .04*k)
        cl.append(along("primitive_cone_add", claw, b, b + ax*.1 + up*.05, 1, radius1=.018, radius2=0, vertices=6))
    parts.append(rigid(cl, arm, "hand.L"))
    rnd = random.Random(8)
    for bn, n_ in (("upper_arm.L", 9), ("forearm.L", 8)):
        o, ax, up, sd = bone_frame(bn); pu = []
        ln = (P(bn, 1) - P(bn)).length
        for k in range(n_):
            a = rnd.uniform(0, 2*math.pi); t = rnd.uniform(.1, .9); r = (.15 if bn.startswith("upper") else .12)
            c = o + ax*ln*t + (up*math.cos(a) + sd*math.sin(a))*r
            sz = rnd.uniform(.014, .028)
            pu.append(prim("primitive_uv_sphere_add", acid if k % 3 == 0 else plague2, c, (sz,)*3, segments=8, ring_count=5))
        for k in range(3):
            a = rnd.uniform(0, 2*math.pi); a2 = a + rnd.uniform(-.6, .6)
            p = o + ax*ln*.1 + (up*math.cos(a) + sd*math.sin(a))*.14
            q = o + ax*ln*.8 + (up*math.cos(a2) + sd*math.sin(a2))*.13
            pu.append(along("primitive_cylinder_add", acid, p, q, .003, vertices=4))
        parts.append(rigid(pu, arm, bn))
    # braço direito de placas soldadas
    for bn in ("upper_arm.R", "forearm.R"):
        o, ax, up, sd = bone_frame(bn); ln = (P(bn, 1) - P(bn)).length; pl = []
        for k in range(3):
            c = o + ax*ln*(.2 + .3*k)
            for a in (0, 2.1, 4.2):
                q = prim("primitive_cube_add", rust, c + (up*math.cos(a) + sd*math.sin(a))*.062, (.035,.008,.05))
                q.rotation_euler = (ax.to_track_quat('Z','Y') @ Quaternion(Vector((0,0,1)), a)).to_euler(); pl.append(q)
            pl.append(prim("primitive_torus_add", iron, c + ax*.06, (1,1,1), major_radius=.068, minor_radius=.005))
            pl[-1].rotation_euler = ax.to_track_quat('Z','Y').to_euler()
        parts.append(rigid(pl, arm, bn))
    # colete de couro com tachas, pneu no ombro esquerdo
    ch = []
    for k in range(12):
        x = -.12 + (k % 4)*.08; z = 1.1 + (k // 4)*.1
        ch.append(prim("primitive_uv_sphere_add", brass, (x, -.19 + abs(x)*.25, z), (.011,.007,.011), segments=6, ring_count=4))
    tire = prim("primitive_torus_add", rubber, (.23,0,1.47), (1,1,1), (0,-35,0), major_radius=.16, minor_radius=.055, major_segments=24, minor_segments=8)
    ch.append(tire)
    for k in range(12):
        a = k*math.pi/6; R = Matrix.Rotation(math.radians(-35), 3, 'Y')
        ch.append(prim("primitive_cube_add", rubber, Vector((.23,0,1.47)) + R @ Vector((.21*math.cos(a), .21*math.sin(a), 0)), (.012,.012,.03)))
    for k in range(6):
        a = rnd.uniform(0, 6.28)
        ch.append(prim("primitive_uv_sphere_add", acid, (rnd.uniform(.02,.14), -.19, rnd.uniform(1.18,1.42)), (.012,)*3, segments=6, ring_count=4))
    parts.append(rigid(ch, arm, "chest"))
    # tala de metal na perna direita
    for bn in ("thigh.R", "shin.R"):
        o, ax, up, sd = bone_frame(bn); ln = (P(bn, 1) - P(bn)).length
        tl = [along("primitive_cube_add", iron, o + ax*ln*.1 + up*.075, o + ax*ln*.9 + up*.075, .012)]
        for t in (.25, .7):
            tl.append(prim("primitive_torus_add", boot, o + ax*ln*t, (1,1,1), major_radius=.08, minor_radius=.01))
            tl[-1].rotation_euler = ax.to_track_quat('Z','Y').to_euler()
        parts.append(rigid(tl, arm, bn))
    # cabeça careca, respirador, olhos verdes, moicano de cravos
    hd = [head_base(plague, (.085,.095,.105)), prim("primitive_uv_sphere_add", plague2, (.03,-.06,1.72), (.03,.02,.025))]
    hd.append(along("primitive_cylinder_add", iron, (0,-.07,1.62), (0,-.13,1.6), .045, vertices=12))
    for s in (1, -1):
        hd.append(along("primitive_cylinder_add", rust, (.045*s,-.1,1.6), (.08*s,-.14,1.58), .025, vertices=10))
        hd.append(prim("primitive_uv_sphere_add", acid, (.033*s,-.092,1.685), (.012,.006,.009)))
    hd += mohawk(iron, acid, n=7, h=.11, seed=5)
    parts.append(rigid(hd, arm, "head"))
    # machado de placa de trânsito
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr
    perp = bd.cross(sd).normalized()
    w = [along("primitive_cylinder_add", iron, g - bd*.15, g + bd*.8, .016, vertices=8)]
    for k in range(3): w.append(prim("primitive_torus_add", boot, g + bd*(-.05 + .04*k), (1,1,1), major_radius=.02, minor_radius=.006))
    pc = g + bd*.68 - perp*.11
    plate = prim("primitive_cylinder_add", sign, pc, (.15,.15,.006), vertices=8)
    plate.rotation_euler = sd.to_track_quat('Z','Y').to_euler(); w.append(plate)
    edge = prim("primitive_cylinder_add", iron, pc, (.16,.16,.004), vertices=8)
    edge.rotation_euler = sd.to_track_quat('Z','Y').to_euler(); w.append(edge)
    for k in range(2): w.append(prim("primitive_uv_sphere_add", iron, g + bd*(.6 + .14*k) - perp*.015, (.012,)*3, segments=6, ring_count=4))
    stripe = along("primitive_cube_add", rubber, pc - perp*.1 + bd*.08, pc + perp*.1 - bd*.08, 1); stripe.scale = (.02, .0075, .13); w.append(stripe)
    parts.append(rigid(w, arm, "hand.R"))
    return arm, {"rim": (.6, 1, .35), "anim": "melee", "extra": {"upper_arm.L": {"y": -14}, "spine": {"x": -6}, "neck": {"x": -10}}}

# ====================================================================== TECNOMANCER
def tecnomancer():
    coat = mat("azul_aco_casaco", (.12,.2,.3), 0, .6, dirt=.55, grime=.8)
    apron = mat("avental_couro", (.15,.08,.04), 0, .55, dirt=.55, grime=.8)
    dark = mat("couro_escuro", (.03,.022,.017), 0, .5, dirt=.7)
    pants = mat("calca_lona", (.05,.048,.042), 0, .85, dirt=.6)
    brass = mat("latao_debrum", (.55,.3,.08), 1, .35, dirt=.5, grime=.2)
    copper = mat("cobre", (.45,.16,.06), 1, .4, dirt=.55, grime=.2)
    iron = mat("ferro_velho", (.1,.095,.09), 1, .5, dirt=.6, grime=.3)
    skin = mat("pele_suja", (.36,.22,.15), 0, .55, dirt=.7, grime=.3)
    hairm = mat("cabelo", (.03,.025,.02), 0, .7, dirt=.8, grime=0)
    rune = mat("runa_laranja", (1,.5,.1), emit=(1,.45,.08), strength=8)
    arc = mat("arco_eletrico", (.6,.85,1), emit=(.55,.82,1), strength=12)
    bolt = mat("raio", (.7,.9,1), emit=(.6,.85,1), strength=22)
    arm = make_armature("tecnomancer")
    parts = body_parts(arm, pants, dark, coat, {"L": brass, "R": dark}, cuff=.06, sleeve_r=1.1, buckle=brass,
                       m_arms={"L": iron, "R": coat}, arm_scale={"L": .9, "R": 1.0})
    sk = skirt("sobretudo", coat, [(1.05,.165,.13,0), (.9,.2,.155,.008), (.7,.235,.18,.015), (.5,.265,.205,.022), (.3,.29,.228,.03), (.16,.305,.24,.035)],
               open_front=.5, jag=.04, seed=31, folds=8, famp=.05)
    bind(sk, arm, ["hips","spine","thigh.L","thigh.R"], power=3); parts.append(sk)
    hem = skirt("debrum", brass, [(.2,.3,.236,.034), (.16,.307,.242,.035)], open_front=.5, seed=31, folds=8, famp=.05, thick=.01)
    bind(hem, arm, ["hips","thigh.L","thigh.R"], power=3); parts.append(hem)
    ap = skirt("avental", apron, [(1.02,.14,.1,-.02), (.5,.15,.1,-.03)], open_front=0, seg=24, thick=.01, jag=.02, seed=2)
    # recorta só a frente do avental
    bm = bmesh.new(); bm.from_mesh(ap.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > -.05], context='VERTS'); bm.to_mesh(ap.data); bm.free()
    bind(ap, arm, ["hips","thigh.L","thigh.R"], power=3); parts.append(ap)
    ch = [prim("primitive_cube_add", apron, (0,-.13,1.3), (.1,.02,.14))]
    # sigilo oculto no peito
    sig, R = arc_tube(rune, Vector((0,-.155,1.33)), .04, .005, 0, 2*math.pi, (90,0,0), seg=12); ch += sig
    for a, b in (((0,-.157,1.37), (-.035,-.157,1.31)), ((-.035,-.157,1.31), (.035,-.157,1.31)), ((.035,-.157,1.31), (0,-.157,1.37))):
        ch.append(along("primitive_cube_add", rune, a, b, .004))
    # caldeira de cobre nas costas com bobinas de tesla e arco elétrico
    ch.append(prim("primitive_cylinder_add", copper, (0,.24,1.28), (.13,.12,.24), vertices=20))
    ch.append(prim("primitive_uv_sphere_add", copper, (0,.24,1.52), (.13,.12,.06)))
    for z in (1.1, 1.28, 1.45): ch.append(prim("primitive_torus_add", brass, (0,.24,z), (1,.93,1), major_radius=.132, minor_radius=.01))
    ch.append(prim("primitive_cylinder_add", iron, (0,.12,1.2), (.03,.03,.03), (90,0,0), vertices=10))
    tops = []
    for s in (1, -1):
        b = Vector((.08*s,.26,1.55)); t = b + Vector((.06*s,.03,.32))
        ch.append(along("primitive_cylinder_add", iron, b, t, .012, vertices=8))
        for k in range(5):
            ch.append(prim("primitive_torus_add", copper, b.lerp(t, .2 + .12*k), (1,1,1), major_radius=.03, minor_radius=.008))
        ch.append(prim("primitive_uv_sphere_add", arc, t, (.03,)*3, segments=10, ring_count=6)); tops.append(t)
    rnd = random.Random(4); p = tops[0]
    for k in range(1, 7):
        q = tops[0].lerp(tops[1], k/6) + Vector((0, rnd.uniform(-.03,.03), .05*math.sin(math.pi*k/6) + rnd.uniform(-.03,.03)))
        ch.append(along("primitive_cylinder_add", arc, p, q, .004, vertices=4)); p = q
    # cano da caldeira até o braço mecânico
    ch += curve_tube(copper, bezier((.1,.18,1.4), (.25,.2,1.5), (.3,.05,1.5), (.22,0,1.45), 6), .016, .016, 8)[:-1]
    parts.append(rigid(ch, arm, "chest"))
    parts.append(pauldron(arm, "R", coat, brass, brass, layers=2))
    # braço mecânico esquerdo: pistões e juntas de latão, mão-garra
    for bn in ("upper_arm.L", "forearm.L"):
        o, ax, up, sd = bone_frame(bn); ln = (P(bn, 1) - P(bn)).length
        mc = [along("primitive_cylinder_add", brass, o + ax*ln*.15 + up*.05, o + ax*ln*.6 + up*.05, .016, vertices=8),
              along("primitive_cylinder_add", iron, o + ax*ln*.6 + up*.05, o + ax*ln*.95 + up*.05, .009, vertices=8),
              prim("primitive_uv_sphere_add", brass, o + ax*ln, (.042,)*3, segments=12, ring_count=8)]
        for t in (.3, .7):
            mc.append(prim("primitive_torus_add", brass, o + ax*ln*t, (1,1,1), major_radius=.05, minor_radius=.008))
            mc[-1].rotation_euler = ax.to_track_quat('Z','Y').to_euler()
        parts.append(rigid(mc, arm, bn))
    fr = bone_frame("hand.L"); o, ax, up, sd = fr
    parts.append(rigid([along("primitive_cone_add", brass, L(fr, .07, 0, .025*k), L(fr, .14, -.03, .03*k), 1, radius1=.01, radius2=.002, vertices=5) for k in (-1, 0, 1)], arm, "hand.L"))
    # cabeça: cabelo espetado, óculos de soldador com lentes laranja, máscara de couro
    hd = [head_base(skin), prim("primitive_uv_sphere_add", dark, (0,-.05,1.61), (.075,.06,.045))]
    hd.append(along("primitive_cylinder_add", iron, (0,-.1,1.6), (0,-.13,1.58), .02, vertices=8))
    for s in (1, -1):
        hd.append(along("primitive_cylinder_add", brass, (.037*s,-.085,1.69), (.04*s,-.115,1.69), .026, vertices=12))
        hd.append(along("primitive_cylinder_add", rune, (.04*s,-.114,1.69), (.041*s,-.119,1.69), .019, vertices=12))
    hd.append(prim("primitive_torus_add", dark, (0,-.005,1.69), (1,1.08,1.4), major_radius=.088, minor_radius=.009))
    rnd = random.Random(2)
    for k in range(16):
        a = rnd.uniform(0, 2*math.pi); el = rnd.uniform(.3, 1.2)
        b = Vector((0,.0,1.7)) + Vector((math.cos(a)*math.cos(el)*.08, .01 + math.sin(a)*math.cos(el)*.085, math.sin(el)*.09))
        d = (b - Vector((0,.02,1.62))).normalized()
        if d.y < -.6: continue
        hd.append(along("primitive_cone_add", hairm, b, b + d*rnd.uniform(.07,.12), 1, radius1=.022, radius2=0, vertices=5))
    parts.append(rigid(hd, arm, "head"))
    # cajado com lanterna rúnica
    fr = bone_frame("hand.R"); o, ax, up, sd = fr; g = L(fr, .045)
    st = [along("primitive_cylinder_add", iron, g - up*.8, g + up*1.0, .015, vertices=8)]
    for k in range(4): st.append(prim("primitive_torus_add", brass, g + up*(-.6 + .45*k), (1,1,1), major_radius=.02, minor_radius=.006))
    lc = g + up*1.08
    st.append(prim("primitive_cylinder_add", rune, lc, (.04,.04,.06), vertices=8))
    st[-1].rotation_euler = up.to_track_quat('Z','Y').to_euler()
    for k in range(4):
        a = k*math.pi/2
        st.append(along("primitive_cylinder_add", brass, lc - up*.07 + (sd*math.cos(a) + ax*math.sin(a))*.048,
                        lc + up*.07 + (sd*math.cos(a) + ax*math.sin(a))*.048, .006, vertices=4))
    st.append(prim("primitive_cone_add", brass, lc + up*.09, (1,1,1), radius1=.06, radius2=.0, depth=.05, vertices=8))
    st[-1].rotation_euler = up.to_track_quat('Z','Y').to_euler()
    st.append(prim("primitive_cone_add", brass, lc - up*.08, (1,1,1), radius1=.0, radius2=.05, depth=.04, vertices=8))
    st[-1].rotation_euler = up.to_track_quat('Z','Y').to_euler()
    parts.append(rigid(st, arm, "hand.R"))
    # raio lançado pela lanterna (efeito do ataque)
    rnd = random.Random(9); p = lc; bl = []
    fwd = (ax*.9 - up*.15).normalized()
    for k in range(9):
        q = lc + fwd*(.13*(k+1)) + sd*rnd.uniform(-.06,.06) + up*rnd.uniform(-.05,.05)
        bl.append(along("primitive_cylinder_add", bolt, p, q, .012 - .0008*k, vertices=4)); p = q
    bl.append(prim("primitive_uv_sphere_add", bolt, lc, (.09,)*3))
    fx = rigid(bl, arm, "hand.R"); fx.name = "raio"
    return arm, {"rim": (1, .55, .3), "anim": "caster", "flash": fx}
