# Golias, o Pião do Agrak: mutante gigante (3,2 m) que o Agrak usa como segunda luta do evento de arena.
# Escravo de arena: corpo largo e assimétrico (o braço da corrente é o dobro do outro), tumor no ombro com
# pústulas do Amargo, colar de ferro de escravo com corrente partida. Roupa de gladiador feita de sucata:
# elmo de murmilão com grade, crista de arame, manica de placas no braço esquerdo, galerus (ombreira alta) no
# direito, cinturão largo com placas de latão, saiote de tiras de couro, caneleira só na perna esquerda.
# Arma: bola de ferro cravejada presa numa corrente de 6 elos (ossos ch1..ch6 + ball, filhos da mão direita).
# Brilho: só o verde do Amargo, em pontos pequenos (olhos atrás da grade e pústulas).
# Especial "spin" (Pião, o twisted slash): braços abertos, corrente esticada pela força centrífuga, giro contínuo
# (o anel de poeira do giro é efeito à parte, desenhado por cima pelo jogo).
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion, Matrix
from mrig import *
import os
OVERRIDE.add("chain")

INFO = {"px": 512, "target_z": 1.0, "rim": (1, .55, .25), "colors": 48, "samples": int(os.environ.get("AMOSTRAS", 40)),
        "fps": {"idle": 6, "walk": 8, "attack": 12, "spin_start": 12, "spin": 16, "spin_end": 10, "roar": 10,
                "hit": 12, "death": 10},
        "loops": ("idle", "walk", "spin")}
SCALE = 1.78
V = {"name": "golias"}
def set_variant(name): V["name"] = name

LINK = .24                     # comprimento de cada elo-osso (unidades do esqueleto, antes da escala)
CH = [f"ch{i}" for i in range(1, 7)]
BALL_R = .19
GROUND = .03

def bones():
    B = humanoid(1.0, 1.3)
    t = Vector(B["hand.R"][1]); p = "hand.R"
    for n in CH:
        B[n] = (tuple(t), tuple(t + Vector((0, 0, -LINK))), p); p = n; t = t + Vector((0, 0, -LINK))
    B["ball"] = (tuple(t), tuple(t + Vector((0, 0, -BALL_R))), p)
    return B

class GRig(Rig):
    """Rig com corrente: depois da pose do corpo, os elos são apontados um a um (modos drape, fling, dir),
    sem atravessar o chão."""
    def set_pose(self, pose, frame):
        super().set_pose(pose, frame)
        ch = pose.get("chain") or {"mode": "drape"}
        bpy.context.view_layer.update()
        pbs = self.arm.pose.bones
        n = len(CH)
        for i, b in enumerate(CH + ["ball"]):
            pb = pbs[b]; h = pb.head.copy(); L = (pb.tail - pb.head).length
            m = ch["mode"]
            if m == "drape":          # pendurada: desce até o chão e arrasta para trás (trail)
                tr = Vector(ch.get("trail", (0, 1, 0))); tr.z = 0; tr.normalize()
                tr = Quaternion((0, 0, 1), math.radians(ch.get("sway", 0)*(i+1)/n)) @ tr
                d = Vector((tr.x*.18, tr.y*.18, -1)).normalized()
            elif m == "fling":        # esticada pela força centrífuga, raio a partir do quadril
                c = pbs["hips"].head; r = pbs["hand.R"].tail - c; r.z = 0; r.normalize()
                lag = Quaternion((0, 0, 1), math.radians(ch.get("lag", 7)*(i+1)))
                r = lag @ r; tl = math.radians(ch.get("tilt", -6))
                d = Vector((r.x*math.cos(tl), r.y*math.cos(tl), math.sin(tl)))
            else:                     # dir: direção dada, curvando de d0 até d1 ao longo da corrente
                d0, d1 = Vector(ch["d"]).normalized(), Vector(ch.get("d1", ch["d"])).normalized()
                d = d0.lerp(d1, i/n).normalized()
            if b == "ball" and m == "drape":
                d = Vector((0, 0, 1))  # a bola descansa no chão ao lado do último elo
            floor = GROUND + .02 if b != "ball" else GROUND
            if b == "ball" and d.z < 0: floor = GROUND + 2*BALL_R  # a bola inteira acima do chão
            if h.z + d.z*L < floor:   # não atravessa o chão: deita o elo
                hz = max(-1, min(1, (floor - h.z)/L)); hor = Vector((d.x, d.y, 0))
                if hor.length < 1e-3: hor = Vector(ch.get("trail", (0, 1, 0)))
                hor.normalize(); d = hor*math.sqrt(max(0, 1 - hz*hz)) + Vector((0, 0, hz))
            cur = (pb.tail - pb.head).normalized()
            M = pb.matrix.copy(); R3 = cur.rotation_difference(d).to_matrix() @ M.to_3x3()
            M2 = R3.to_4x4(); M2.translation = M.translation; pb.matrix = M2
            bpy.context.view_layer.update()
            pb.keyframe_insert("rotation_quaternion", frame=frame)

def build():
    rr = random.Random(11)
    skin = stained("g_pele", (.2, .2, .15), stain=(.16, .03, .02), amount=.4, scale=4, rough=.5,
                   blotch=(.1, .12, .07), blotch_amt=.8, grime=1.2)
    tumor = stained("g_tumor", (.26, .17, .15), stain=(.1, .14, .05), amount=.6, scale=7, rough=.3,
                    blotch=(.14, .06, .08), blotch_amt=.9, grime=.6)
    leather = stained("g_couro", (.1, .06, .035), stain=(.2, .02, .01), amount=.5, scale=3, rough=.45, grime=.9)
    cloth = stained("g_pano", (.2, .05, .035), stain=(.07, .05, .03), amount=.6, scale=3, rough=.95, grime=1.3,
                    blotch=(.1, .08, .05), blotch_amt=.6)
    iron = stained("g_ferro", (.1, .085, .075), stain=(.2, .08, .03), amount=.6, scale=5, metal=.85, rough=.55, grime=.6)
    steel = stained("g_aco", (.33, .32, .3), stain=(.2, .07, .03), amount=.55, scale=6, metal=1, rough=.4, grime=.4)
    brass = stained("g_latao", (.36, .23, .08), stain=(.09, .07, .03), amount=.45, scale=6, metal=1, rough=.45, grime=.5)
    rope = mat("g_corda", (.18, .13, .08), 0, .9, dirt=.5)
    hole = mat("g_buraco", (.006, .005, .004), 0, .95)
    glow = mat("g_amargo", (.3, .9, .2), emit=(.3, 1, .15), strength=3)

    B = bones(); R = GRig(V["name"], B); P = R.P
    R.gexclude = set(CH) | {"ball"}
    # ------------------------------------------------ pernas grossas e tortas
    j = {"pelvis": (0, 0, .93, .2, .14)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        big = 1.12 if n == "R" else 1
        j[f"hip{n}"] = (*h, .13*big); j[f"th{n}"] = (*h.lerp(k, .5), .12*big); j[f"knee{n}"] = (*k, .09*big)
        j[f"calf{n}"] = (*(k.lerp(a, .35) + Vector((0, .03, 0))), .1*big); j[f"ank{n}"] = (*a, .065)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"th{n}"), (f"th{n}", f"knee{n}"), (f"knee{n}", f"calf{n}"),
              (f"calf{n}", f"ank{n}")]
    legs = skin_mesh("pernas", j, e, skin); R.bind(legs, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R"])
    for s, n in ((1, "L"), (-1, "R")):  # pés descalços enfaixados, dedos grossos
        a, t = P(f"foot.{n}"), P(f"foot.{n}", 1)
        fj = {"ank": (*a, .07), "mid": (*a.lerp(t, .5), .075, .06), "toe": (*(t + Vector((0, -.02, -.005))), .07, .045),
              "heel": (*(a + Vector((0, .05, -.04))), .065)}
        f = skin_mesh(f"pe.{n}", fj, [("ank", "mid"), ("mid", "toe"), ("ank", "heel")], skin)
        R.bind(f, [f"shin.{n}", f"foot.{n}"])
        wr = [prim("primitive_torus_add", cloth, a.lerp(t, .25*k) + Vector((0, 0, .02 - .005*k)), (1, 1.2, .6),
                   major_radius=.075, minor_radius=.014, major_segments=12, minor_segments=4) for k in range(3)]
        R.rigid(wr, f"foot.{n}")
    # caneleira (ocrea) só na perna esquerda: placa curva de sucata com tiras
    k, a = P("shin.L"), P("foot.L")
    oc = [along("primitive_cylinder_add", iron, k + Vector((0, -.02, -.02)), a + Vector((0, -.02, .08)), .118,
                vertices=12, end_fill_type='NOTHING')]
    oc[0].scale.x *= 1;
    for tt in (.25, .6):
        oc.append(prim("primitive_torus_add", leather, k.lerp(a, tt) + Vector((0, -.01, 0)), (1, 1, .8), major_radius=.125,
                       minor_radius=.012, major_segments=14, minor_segments=4))
    oc.append(prim("primitive_uv_sphere_add", iron, k + Vector((0, -.08, .02)), (.09, .06, .08), segments=10, ring_count=6))
    R.rigid(oc, "shin.L")

    # ------------------------------------------------ tronco enorme, barriga, tumor no ombro direito
    t = {"pelvis": (0, 0, .97, .23, .17), "belly": (0, -.06, 1.13, .28, .25), "chest": (0, 0, 1.33, .3, .2),
         "neck": (0, -.02, 1.5, .12), "neck2": (0, -.03, 1.58, .1)}
    te = [("pelvis", "belly"), ("belly", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        big = 1.45 if n == "R" else 1.0
        t[f"sh{n}"] = (*(sh + Vector((-.03*s, 0, .02))), .13*big); t[f"bi{n}"] = (*sh.lerp(el, .45), .11*big)
        t[f"el{n}"] = (*el, .085*big); t[f"fa{n}"] = (*el.lerp(wr, .4), .1*big); t[f"wr{n}"] = (*wr, .065*big)
        te += [("chest", f"sh{n}"), (f"sh{n}", f"bi{n}"), (f"bi{n}", f"el{n}"), (f"el{n}", f"fa{n}"), (f"fa{n}", f"wr{n}")]
    torso = skin_mesh("tronco", t, te, skin)
    R.bind(torso, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])
    ch = []
    # tumor: massa de carne no ombro direito/costas, com pústulas do Amargo
    tc = P("upper_arm.R") + Vector((-.02, .17, .02))
    ch.append(prim("primitive_uv_sphere_add", tumor, tc, (.16, .16, .14), segments=18, ring_count=10))
    ch.append(prim("primitive_uv_sphere_add", tumor, tc + Vector((.1, .07, -.06)), (.13, .12, .11), segments=14, ring_count=8))
    ch.append(prim("primitive_uv_sphere_add", tumor, tc + Vector((-.08, .12, -.12)), (.1, .1, .09), segments=12, ring_count=8))
    for k in range(16):
        a = rr.uniform(0, 2*math.pi); z = rr.uniform(-.3, .9)
        q = tc + Vector((.19*math.cos(a)*math.sqrt(1 - z*z*.5), .19*math.sin(a)*math.sqrt(1 - z*z*.5) + .02, .15*z))
        if q.y < tc.y + .04: continue  # pústulas só nas costas (de frente não parecem olhos)
        ch.append(prim("primitive_uv_sphere_add", glow if k % 2 == 0 else tumor, q, (.022, .022, .02), segments=8, ring_count=6))
    # veias grossas descendo do tumor pelo peito
    for k in range(3):
        pts = [tc + Vector((.12 - .07*k, -.12, -.05)) + Vector((.04*math.sin(i*1.4 + k), -.03*i, -.08*i)) for i in range(5)]
        for a_, b_ in zip(pts, pts[1:]):
            ch.append(along("primitive_cylinder_add", tumor, a_, b_, .014, vertices=6))
    # colar de escravo de ferro com corrente partida
    ch.append(prim("primitive_torus_add", iron, (0, -.02, 1.52), (1, 1, 1.6), major_radius=.14, minor_radius=.028,
                   major_segments=18, minor_segments=6))
    ch.append(prim("primitive_torus_add", iron, (0, -.17, 1.5), (1, 1, 1), major_radius=.03, minor_radius=.009,
                   major_segments=8, minor_segments=4, rot=(0, 90, 0)))
    for i in range(4):
        q = Vector((.01*i, -.18 - .005*i, 1.44 - .055*i))
        ch.append(prim("primitive_torus_add", iron, q, (1, 1, 1.4), major_radius=.022, minor_radius=.008,
                       major_segments=8, minor_segments=4, rot=(90*(i % 2), 0, 0)))
    # cinturão largo (balteus) com placas de latão e fivela
    ch.append(prim("primitive_cylinder_add", leather, (0, -.02, 1.02), (.29, .25, .11), vertices=24))
    for k in range(9):
        a = math.radians(-90 + 40*(k - 4))
        q = Vector((.3*math.cos(a), -.02 + .26*math.sin(a), 1.02))
        pl = prim("primitive_cube_add", brass, q, (.045, .012, .075))
        pl.rotation_euler = (0, 0, a + math.pi/2); ch.append(pl)
        ch.append(prim("primitive_uv_sphere_add", iron, q*1.02 + Vector((0, 0, .05)), (.01, .01, .01), segments=6, ring_count=4))
    ch.append(prim("primitive_cylinder_add", iron, (0, -.29, 1.02), (.07, .07, .02), vertices=12, rot=(90, 0, 0)))
    # alça cruzada de couro (do ombro esquerdo ao quadril direito) segurando o galerus
    for a_, b_ in ((Vector((.24, -.22, 1.45)), Vector((-.1, -.29, 1.2))), (Vector((-.1, -.29, 1.2)), Vector((-.28, -.18, 1.08)))):
        ch.append(along("primitive_cube_add", leather, a_, b_, .035))
    # galerus: ombreira alta curva no ombro direito (braço da corrente)
    gc = P("upper_arm.R") + Vector((-.02, -.04, .1))
    for k in range(4):
        pl = prim("primitive_cylinder_add", iron, gc + Vector((-.03*k, 0, -.06*k)), (.2 - .01*k, .19, .02), vertices=16)
        pl.rotation_euler = (0, math.radians(-38), 0); ch.append(pl)
    fin = prim("primitive_cube_add", iron, gc + Vector((.07, 0, .14)), (.015, .17, .13), rot=(0, -10, 0)); ch.append(fin)
    for k in range(5):
        ch.append(prim("primitive_uv_sphere_add", brass, gc + Vector((.08, -.13 + .065*k, .26)), (.016, .016, .016), segments=6, ring_count=4))
    R.rigid(ch, "chest")

    # saiote de tiras de couro (pteruges) sobre o subligaculum de pano
    sk = skirt("subligaculum", cloth, [(1.0, .27, .23, -.01), (.86, .29, .25, -.01), (.72, .31, .27, 0)], seg=24,
               jag=.05, seed=5, thick=.015)
    R.bind(sk, ["hips", "thigh.L", "thigh.R"], power=3)
    st = []
    for k in range(16):
        a = 2*math.pi*k/16
        x, y = .315*math.cos(a), -.01 + .275*math.sin(a)
        ln = .3 + .06*rr.random()
        o = prim("primitive_cube_add", leather, (x, y, .97 - ln/2), (.036, .009, ln/2))
        o.rotation_euler = (0, 0, a + math.pi/2); st.append(o)
        st.append(prim("primitive_uv_sphere_add", brass, (x*1.03, y*1.03, .97 - ln + .02), (.014, .014, .014), segments=6, ring_count=4))
    pt = st[0]
    with bpy.context.temp_override(active_object=pt, selected_editable_objects=st, selected_objects=st, object=pt):
        bpy.ops.object.join()
    R.bind(pt, ["hips", "thigh.L", "thigh.R"], power=3)

    # ------------------------------------------------ elmo de murmilão de sucata
    hd = [prim("primitive_uv_sphere_add", skin, (0, -.02, 1.69), (.11, .12, .12), segments=14, ring_count=10)]
    hd.append(prim("primitive_uv_sphere_add", iron, (0, -.01, 1.72), (.15, .16, .15), segments=20, ring_count=12))
    br = prim("primitive_cylinder_add", iron, (0, -.01, 1.64), (.22, .23, .012), vertices=24, rot=(-6, 0, 0)); hd.append(br)
    # rosto: grade de barras verticais e horizontais, escuro atrás, olhos verdes
    hd.append(prim("primitive_uv_sphere_add", hole, (0, -.13, 1.71), (.1, .045, .08), segments=12, ring_count=8))
    for k in range(7):
        x = -.075 + .025*k
        hd.append(along("primitive_cylinder_add", steel, (x, -.162, 1.78), (x, -.165 + .004*abs(k - 3), 1.63), .007, vertices=5))
    for z in (1.75, 1.7, 1.66):
        hd.append(along("primitive_cylinder_add", steel, (-.09, -.158, z), (.09, -.158, z), .006, vertices=5))
    for s in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", glow, (.035*s, -.135, 1.725), (.013, .008, .008), segments=8, ring_count=4))
    # crista de arame enferrujado (no lugar do pelo de cavalo) presa num trilho
    hd.append(prim("primitive_cube_add", brass, (0, .0, 1.88), (.018, .17, .025)))
    for k in range(26):
        y = -.15 + .3*k/25; h = .13 + .07*math.sin(math.pi*k/25) + rr.uniform(-.02, .02)
        hd.append(along("primitive_cylinder_add", iron, (rr.uniform(-.01, .01), y, 1.89),
                        (rr.uniform(-.02, .02), y + .05 + .02*k/25, 1.89 + h), .006, vertices=4))
    for s in (1, -1):  # rebites e bochecheiras
        hd.append(prim("primitive_cube_add", iron, (.13*s, -.06, 1.63), (.012, .07, .07), rot=(0, 0, 15*s)))
        for z in (1.66, 1.6): hd.append(prim("primitive_uv_sphere_add", brass, (.142*s, -.07, z), (.012, .012, .012), segments=6, ring_count=4))
    piv = Vector((0, -.02, 1.56))  # elmo 30% maior: é a peça que identifica o gladiador de longe
    for o in hd:
        o.location = piv + (Vector(o.location) - piv)*1.3; o.scale = Vector(o.scale)*1.3
    R.rigid(hd, "head")

    # ------------------------------------------------ manica: placas em faixas no braço esquerdo
    for b, r0, r1, nk in (("upper_arm.L", .115, .1, 5), ("forearm.L", .11, .085, 5)):
        o_, ax, u, sd = R.frame(b); L = (P(b, 1) - P(b)).length; mc = []
        for k in range(nk):
            c = o_ + ax*(L*(.12 + .8*k/(nk - 1))); r = r0 + (r1 - r0)*k/(nk - 1)
            pl = prim("primitive_cylinder_add", iron if k % 2 == 0 else steel, c, (r, r*.95, .03), vertices=14)
            pl.rotation_euler = ax.to_track_quat('Z', 'Y').to_euler(); mc.append(pl)
        R.rigid(mc, b)
    # punho esquerdo enfaixado (cestus) e punho direito segurando o cabo da corrente
    for n in ("L", "R"):
        o_, ax, u, sd = R.frame(f"hand.{n}"); big = 1.4 if n == "R" else 1
        g = [prim("primitive_uv_sphere_add", skin, o_ + ax*.06, (.07*big, .075*big, .08*big), segments=12, ring_count=8)]
        g[0].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        for k in range(3):
            w = prim("primitive_torus_add", cloth if n == "L" else leather, o_ + ax*(.02 + .035*k), (1, 1, 1),
                     major_radius=.075*big, minor_radius=.014, major_segments=12, minor_segments=4)
            w.rotation_euler = ax.to_track_quat('Z', 'Y').to_euler(); g.append(w)
        if n == "R":
            g.append(along("primitive_cylinder_add", iron, o_ + ax*.02, P("hand.R", 1) + ax*.04, .035, vertices=8))
        R.rigid(g, f"hand.{n}")
    # faixas de pano no antebraço direito (fascia)
    o_, ax, u, sd = R.frame("forearm.R"); L = (P("forearm.R", 1) - P("forearm.R")).length
    fs = []
    for k in range(5):
        w = prim("primitive_torus_add", cloth, o_ + ax*(L*(.25 + .15*k)), (1, 1, 1.3), major_radius=.13 - .008*k,
                 minor_radius=.016, major_segments=14, minor_segments=4)
        w.rotation_euler = ax.to_track_quat('Z', 'Y').to_euler(); fs.append(w)
    R.rigid(fs, "forearm.R")

    # ------------------------------------------------ corrente (elos alternados) e bola cravejada
    for i, b in enumerate(CH):
        o_, ax, u, sd = R.frame(b)
        lk = []
        for k in range(3):
            c = o_ + ax*(LINK*(k + .5)/3)
            t_ = prim("primitive_torus_add", iron, c, (1, 1, 1.55), major_radius=.03, minor_radius=.011,
                      major_segments=10, minor_segments=5)
            q = ax.to_track_quat('Z', 'Y') @ Quaternion((0, 0, 1), math.radians(90*((3*i + k) % 2)))
            t_.rotation_euler = (q @ Quaternion((1, 0, 0), math.radians(90))).to_euler()
            t_.scale = (1, 1.55, 1)
            lk.append(t_)
        R.rigid(lk, b)
    bc = P("ball", 1)
    bl = [prim("primitive_uv_sphere_add", iron, bc, (BALL_R, BALL_R, BALL_R), segments=22, ring_count=14)]
    bl.append(prim("primitive_torus_add", steel, bc, (1, 1, 1), major_radius=BALL_R*1.0, minor_radius=.018,
                   major_segments=22, minor_segments=5, rot=(90, 0, 0)))
    bl.append(prim("primitive_torus_add", steel, bc, (1, 1, 1), major_radius=BALL_R*1.0, minor_radius=.018,
                   major_segments=22, minor_segments=5, rot=(0, 90, 0)))
    bl.append(prim("primitive_torus_add", iron, P("ball") + Vector((0, 0, -.02)), (1, 1, 1.3), major_radius=.04,
                   minor_radius=.013, major_segments=10, minor_segments=5, rot=(90, 0, 0)))
    gold = (1 + 5**.5)/2
    for k in range(14):  # cravos distribuídos (espiral de Fibonacci)
        z = 1 - 2*(k + .5)/14; r = math.sqrt(1 - z*z); a = 2*math.pi*k/gold
        d = Vector((r*math.cos(a), r*math.sin(a), z))
        if d.z > .85: continue  # o topo prende o elo
        bl.append(along("primitive_cone_add", steel, bc + d*BALL_R*.85, bc + d*(BALL_R + .11), .032, vertices=6,
                        radius1=1, radius2=0))
    R.rigid(bl, "ball")

    R.arm.scale = [SCALE]*3
    return R, INFO

# ======================================================================= animações
# Postura base: pesado, curvado, pernas abertas, braço da corrente baixo e à frente.
BASE = {"spine": {"x": 8}, "chest": {"x": 8}, "neck": {"x": -10}, "head": {"x": -8},
        "thigh.L": {"x": -4, "y": -10}, "thigh.R": {"x": -2, "y": 10}, "shin.L": {"bend": 14}, "shin.R": {"bend": 12},
        "foot.L": {"x": -8, "z": 10}, "foot.R": {"x": -8, "z": -10},
        "upper_arm.L": {"y": 20, "x": -14}, "upper_arm.R": {"y": -12, "x": -26},
        "forearm.L": {"bend": -40}, "forearm.R": {"bend": -30}, "hand.R": {"x": -10}}

def M(*p): return merge(BASE, *p)
def C(**k): return {"chain": k}

def anims(R):
    out = {}
    # parado: respiração funda, ombros sobem, a bola descansa no chão
    out["idle"] = [M({"chest": {"x": -3*math.sin(i/6*2*math.pi)}, "spine": {"x": -1.5*math.sin(i/6*2*math.pi)},
                      "upper_arm.L": {"z": 3*math.sin(i/6*2*math.pi)}, "head": {"x": 2*math.sin(i/6*2*math.pi), "z": 3*math.cos(i/6*2*math.pi)}},
                     C(mode="drape", trail=(.3, -1, 0), sway=8*math.sin(i/6*2*math.pi))) for i in range(6)]
    # andar: passos pesados, tronco balança, a bola vem arrastando atrás
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 20*s
        walk.append(M({"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                       "shin.L": {"bend": 8 + 40*max(0, c)**1.3}, "shin.R": {"bend": 8 + 40*max(0, -c)**1.3},
                       "foot.L": {"x": .3*th - 8*max(0, c)}, "foot.R": {"x": -.3*th - 8*max(0, -c)},
                       "hips": {"z": 7*s, "y": 6*c}, "chest": {"z": -9*s, "y": -5*c}, "head": {"z": 5*s, "x": 3*abs(c)},
                       "upper_arm.L": {"x": 16*s}, "upper_arm.R": {"x": -5*s}},
                      C(mode="drape", trail=(.25, 1, 0), sway=10*s)))
    out["walk"] = walk
    # ataque: gira a bola por cima da cabeça e esmaga à frente (o chão é o alvo)
    wind = M({"upper_arm.R": {"y": 60, "x": 30}, "forearm.R": {"bend": -40}, "chest": {"z": -30, "x": -8}, "spine": {"z": -10},
              "head": {"z": 15}, "upper_arm.L": {"x": -30, "y": -10}, "thigh.R": {"x": 10}}, C(mode="dir", d=(-.3, .9, -.2), d1=(-.2, .9, .25)))
    over = M({"upper_arm.R": {"x": -160, "y": 10}, "forearm.R": {"bend": -30}, "chest": {"x": -18, "z": -10}, "spine": {"x": -8},
              "head": {"x": 10}, "upper_arm.L": {"x": -50, "y": -20}, "forearm.L": {"bend": -50}},
             C(mode="dir", d=(0, .8, .55), d1=(0, 1, -.3)))
    smash = M({"upper_arm.R": {"x": -70, "y": 8}, "forearm.R": {"bend": -6}, "hand.R": {"x": 20}, "chest": {"x": 30, "z": 8},
               "spine": {"x": 14}, "head": {"x": -24}, "upper_arm.L": {"x": -20, "y": -20}, "thigh.L": {"x": -36},
               "shin.L": {"bend": 46}, "thigh.R": {"x": 14}, "shin.R": {"bend": 30}, "root": (0, -.18, 0)},
              C(mode="dir", d=(0, -1, -.25), d1=(0, -1, -.6)))
    out["attack"] = keys_to_frames([(0, M(C(mode="drape", trail=(.3, -1, 0)))), (.22, wind), (.45, over), (.6, smash),
                                    (.78, merge(smash, {"chest": {"x": 4}})), (1, M(C(mode="drape", trail=(.3, -1, 0))))], 10)
    # o Pião (twisted slash): entrada, giro em loop e tontura no fim
    def spin_pose(ang, k=1.0, step=0):
        return M({"hips": {"z": ang}, "spine": {"x": -8*k, "z": -10*k}, "chest": {"x": -14*k, "z": -14*k},
                  "head": {"x": 6*k, "z": 18*k},
                  "upper_arm.R": {"y": -78*k, "x": -6*k, "z": 18*k}, "forearm.R": {"bend": -6*k},
                  "upper_arm.L": {"y": 70*k, "x": -18*k, "z": -22*k}, "forearm.L": {"bend": -26*k},
                  "thigh.L": {"x": -12 + 14*math.sin(step), "y": -14}, "thigh.R": {"x": 4 - 14*math.sin(step), "y": 14},
                  "shin.L": {"bend": 24 + 10*max(0, math.sin(step))}, "shin.R": {"bend": 24 + 10*max(0, -math.sin(step))}},
                 C(mode="fling", lag=7*k, tilt=-4 - 6*(1 - k)))
    st = []
    for i in range(8):  # entrada: abaixa, gira a bola pelo chão e ganha velocidade (meia volta)
        u = i/7; k = u**1.5
        p = spin_pose(-200*u**2, k, i*1.6)
        if u < .45:
            p = lerp_pose(M({"chest": {"x": 20}, "spine": {"x": 10}, "thigh.L": {"x": -30}, "shin.L": {"bend": 40},
                             "thigh.R": {"x": 10}, "shin.R": {"bend": 36}, "upper_arm.R": {"y": -40, "x": -20}},
                            C(mode="dir", d=(-1, -.4, -.3), d1=(-.6, .7, -.5))), p, u/.45)
        st.append(p)
    out["spin_start"] = st
    sp = []
    for i in range(12):  # loop: 12 quadros por volta (30 graus por quadro)
        p = spin_pose(-200 - 30*i, 1.0, i*math.pi/3)
        sp.append(p)
    out["spin"] = sp
    tired = M({"chest": {"x": 34}, "spine": {"x": 14}, "head": {"x": 10, "z": 16}, "upper_arm.L": {"x": 30, "y": 10},
               "forearm.L": {"bend": -70}, "upper_arm.R": {"x": 10, "y": -8}, "thigh.L": {"x": -20}, "shin.L": {"bend": 30},
               "thigh.R": {"x": 6}, "shin.R": {"bend": 26}}, C(mode="drape", trail=(1, .3, 0), sway=30))
    out["spin_end"] = keys_to_frames([(0, spin_pose(-200 - 360, .9, 0)),
                                      (.35, merge(tired, {"hips": {"z": 30}})), (.6, merge(tired, {"hips": {"z": 18}, "head": {"z": -10}})),
                                      (.8, merge(tired, {"hips": {"z": 8}, "head": {"z": 12}})), (1, tired)], 8)
    # rugido de entrada: bate no peito com o punho esquerdo e ergue a bola
    beat = M({"upper_arm.L": {"x": -70, "y": -40, "z": -30}, "forearm.L": {"bend": -110}, "chest": {"x": -24}, "spine": {"x": -10},
              "head": {"x": -30}, "neck": {"x": -10}, "upper_arm.R": {"x": -120, "y": -30}, "forearm.R": {"bend": -40}},
             C(mode="dir", d=(-.2, .3, -1), d1=(-.3, .6, -1)))
    beat2 = merge(beat, {"upper_arm.L": {"x": 25, "y": 20}, "forearm.L": {"bend": 30}, "chest": {"x": 6}})
    out["roar"] = keys_to_frames([(0, M(C(mode="drape", trail=(.3, -1, 0)))), (.25, beat), (.4, beat2), (.55, beat),
                                  (.7, beat2), (.85, beat), (1, M(C(mode="drape", trail=(.3, -1, 0))))], 12)
    hitp = M({"chest": {"x": -14, "z": 8}, "spine": {"x": -6}, "head": {"x": -18, "z": 10},
              "upper_arm.L": {"y": -10, "x": 14}, "root": (0, .06, 0)}, C(mode="drape", trail=(.3, -1, 0), sway=14))
    out["hit"] = [hitp, lerp_pose(hitp, M(C(mode="drape", trail=(.3, -1, 0))), .5), M(C(mode="drape", trail=(.3, -1, 0)))]
    kneel = M({"thigh.L": {"x": -75}, "thigh.R": {"x": -40}, "shin.L": {"bend": 100}, "shin.R": {"bend": 95},
               "chest": {"x": 22}, "head": {"x": 22}, "upper_arm.L": {"y": 6, "x": 10}, "upper_arm.R": {"y": -6, "x": 10},
               "forearm.R": {"bend": -20}}, C(mode="drape", trail=(.3, -1, 0)))
    down = merge({"hips": {"x": 80, "y": -10}, "spine": {"x": 6}, "chest": {"x": 4}, "head": {"z": -40, "x": -10},
                  "upper_arm.L": {"x": -150, "y": 30}, "upper_arm.R": {"x": -40, "y": -50}, "forearm.L": {"bend": -20},
                  "forearm.R": {"bend": -10}, "thigh.L": {"x": 10}, "thigh.R": {"x": 4}, "shin.L": {"bend": 20},
                  "shin.R": {"bend": 8}, "ground": .1}, C(mode="drape", trail=(-1, -.2, 0)))
    fall = merge(lerp_pose(kneel, down, .45), {"ground": .1})
    out["death"] = keys_to_frames([(0, hitp), (.3, kneel), (.45, merge(kneel, {"head": {"x": 10}})), (.7, fall), (.9, down),
                                   (1, merge(down, {"head": {"x": 4}}))], 10)
    return out
