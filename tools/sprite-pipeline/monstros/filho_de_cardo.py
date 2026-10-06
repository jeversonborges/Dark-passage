# Filho de Cardo (raro de missão): mutante-besta de carne e espinho do cemitério do Morro do Coveiro.
# Massa de carne retorcida com cardos roxos secos e espinhos brotando, raízes no lugar das pernas,
# boca vertical cheia de espinhos (cospe 3), resto de lápide e cruz de ferro presos nas raízes.
# Brilho: seiva verde-ácido em pontos pequenos (fissuras, base dos espinhos, baba da boca).
# Esqueleto próprio: base (raiz do rig), corpo, topo, coroa, dois lábios, 4 tufos de espinhos,
# 2 cipós de 3 ossos, 6 raízes de 2 ossos e "occ" (oclusor do chão, ver abaixo).
# Enterrar/brotar: o root desce abaixo do chão ("ground": None) e um disco com material Holdout no
# nível do chão esconde o que fica embaixo. O disco fica preso ao osso "occ": na pose neutra ele está
# 12 m abaixo (fora do quadro); burrow/emerge giram "occ" 180 graus e o disco vai para z=0.
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *
from corvo_de_cinza import safe_ground

INFO = {"px": 256, "target_z": .9, "rim": (.62, .85, .38), "colors": 44, "samples": 40,
        "fps": {"idle": 6, "walk": 7, "attack": 12, "burrow": 10, "emerge": 12, "hit": 12, "death": 9}}

RA = [(235, .95), (305, 1.0), (180, .85), (0, .9), (125, .8), (55, .85)]   # ângulo (graus, 0 = +X) e alcance
BONES = {
 "base":  ((0, 0, .25), (0, 0, .6), None),
 "occ":   ((0, 0, -6), (0, 0, -5.8), None),
 "body":  ((0, 0, .6), (0, -.02, 1.05), "base"),
 "upper": ((0, -.02, 1.05), (0, -.04, 1.45), "body"),
 "crown": ((0, -.04, 1.45), (0, 0, 1.7), "upper"),
}
for s, n in ((1, "L"), (-1, "R")):
    BONES.update({
     f"lip.{n}":   ((.15*s, -.22, 1.08), (.15*s, -.22, 1.58), "upper"),
     f"vine1.{n}": ((.26*s, -.04, 1.3), (.5*s, -.1, 1.16), "upper"),
     f"vine2.{n}": ((.5*s, -.1, 1.16), (.67*s, -.16, .9), f"vine1.{n}"),
     f"vine3.{n}": ((.67*s, -.16, .9), (.73*s, -.22, .64), f"vine2.{n}"),
     f"spk_hi.{n}": ((.14*s, .16, 1.4), (.3*s, .34, 1.62), "upper"),
     f"spk_lo.{n}": ((.26*s, .2, .95), (.46*s, .38, 1.1), "body"),
    })
for i, (a, L) in enumerate(RA):
    d = Vector((math.cos(math.radians(a)), math.sin(math.radians(a)), 0))
    p0 = d*.3 + Vector((0, 0, .25)); p1 = d*(.3 + L*.5) + Vector((0, 0, .05)); p2 = d*(.3 + L) + Vector((0, 0, .02))
    BONES[f"root{i}.a"] = (tuple(p0), tuple(p1), "base")
    BONES[f"root{i}.b"] = (tuple(p1), tuple(p2), f"root{i}.a")
ROOTS = [f"root{i}.{k}" for i in range(len(RA)) for k in "ab"]

def holdout(name):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes):
        if nd.type != 'OUTPUT_MATERIAL': nt.nodes.remove(nd)
    h = nt.nodes.new("ShaderNodeHoldout")
    nt.links.new(h.outputs[0], [nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL'][0].inputs["Surface"])
    return m

def build():
    rnd = random.Random(11)
    carne = stained("fc_carne", (.2, .075, .07), stain=(.06, .02, .02), amount=.45, scale=4, rough=.4,
                    blotch=(.11, .1, .05), blotch_amt=.75, grime=.8)
    raiz = stained("fc_raiz", (.075, .05, .035), stain=(.14, .025, .02), amount=.4, scale=6, rough=.85,
                   blotch=(.035, .03, .025), blotch_amt=.7, grime=.4)
    espinho = stained("fc_espinho", (.36, .32, .22), stain=(.13, .02, .015), amount=.35, scale=9, rough=.5, grime=.2)
    caule = stained("fc_caule", (.1, .11, .07), stain=(.05, .04, .03), amount=.4, scale=6, rough=.75, grime=.3)
    flor = stained("fc_cardo", (.2, .09, .2), stain=(.08, .05, .07), amount=.45, scale=7, rough=.85, grime=0)
    pedra = stained("fc_pedra", (.3, .29, .27), stain=(.07, .07, .05), amount=.5, scale=3, rough=.9,
                    blotch=(.1, .1, .08), blotch_amt=.6, grime=.8)
    ferro = stained("fc_ferro", (.09, .07, .06), stain=(.3, .1, .035), amount=.6, scale=8, metal=.7, rough=.55, grime=.3)
    seiva = mat("fc_seiva", (.6, 1, .2), emit=(.55, 1, .15), strength=14)
    escuro = mat("fc_boca", (.02, .005, .005), 0, .5)
    occm = holdout("fc_holdout")

    R = Rig("cardo", BONES, ground=.02, ground_bones=ROOTS); R.gexclude = {"occ"}
    P = R.P
    # ------------------------------------------------ oclusor do chão (Holdout), escondido na pose neutra
    occ = prim("primitive_circle_add", occm, (0, 0, -12), vertices=40, radius=4, fill_type='NGON')
    occ.visible_shadow = False
    R.rigid([occ], "occ").visible_shadow = False

    # ------------------------------------------------ massa de carne retorcida
    j = {"b0": (0, .02, .3, .44, .4), "b1": (.04, 0, .62, .41, .37), "b2": (-.03, -.02, .95, .35, .31),
         "b3": (.02, -.04, 1.24, .29, .27), "b4": (-.01, -.02, 1.48, .21, .19), "b5": (.01, 0, 1.64, .11),
         "lL": (.32, .06, .74, .19), "lR": (-.3, .1, 1.02, .17), "hump": (.02, .26, 1.12, .2), "hump2": (-.12, .24, .6, .2)}
    e = [("b0", "b1"), ("b1", "b2"), ("b2", "b3"), ("b3", "b4"), ("b4", "b5"), ("b1", "lL"), ("b2", "lR"),
         ("b3", "hump"), ("b1", "hump2")]
    body = skin_mesh("massa", j, e, carne)
    R.bind(body, ["base", "body", "upper", "crown"], power=4)
    def radius(z):  # raio aproximado da massa na altura z (para espalhar coisas na superfície)
        pts = [(.3, .44), (.62, .41), (.95, .35), (1.24, .29), (1.48, .21), (1.64, .11), (1.75, .02)]
        for (z0, r0), (z1, r1) in zip(pts, pts[1:]):
            if z <= z1: return r0 + (r1 - r0)*max(0, (z - z0)/(z1 - z0))
        return .02
    def bone_at(z): return "base" if z < .6 else "body" if z < 1.05 else "upper" if z < 1.45 else "crown"
    parts = {b: [] for b in ("base", "body", "upper", "crown")}
    # tumores e fissuras com seiva
    for k in range(12):
        z = rnd.uniform(.35, 1.45); a = rnd.uniform(0, 2*math.pi)
        if 1.0 < z and abs(math.degrees(a) - 270) < 35: continue
        r = radius(z)*.92; p = Vector((r*math.cos(a), r*math.sin(a), z)); sc = rnd.uniform(.06, .12)
        parts[bone_at(z)].append(prim("primitive_uv_sphere_add", carne, p, (sc, sc*.9, sc*1.1), segments=10, ring_count=7))
    for k in range(7):
        z = rnd.uniform(.4, 1.35); a = rnd.uniform(0, 2*math.pi)
        if 1.0 < z and abs(math.degrees(a) - 270) < 35: a += 1.2
        r = radius(z) + .005; n = Vector((math.cos(a), math.sin(a), 0)); t = Vector((-n.y, n.x, 0))
        p = Vector((r*n.x, r*n.y, z)); q = p + t*rnd.uniform(-.06, .06) + Vector((0, 0, rnd.uniform(.08, .16)))
        parts[bone_at(z)].append(along("primitive_cylinder_add", escuro, p, q, .016, vertices=5))
        for u in (.3, .75):
            parts[bone_at(z)].append(prim("primitive_uv_sphere_add", seiva, p.lerp(q, u) + n*.012, (.014, .014, .014),
                                          segments=6, ring_count=4))
    # espinhos espalhados pela massa
    for k in range(90):
        z = rnd.uniform(.3, 1.66); a = rnd.uniform(0, 2*math.pi)
        if 1.0 < z < 1.62 and abs(math.degrees(a) - 270) < 30: continue
        r = radius(z)*.95; n = Vector((math.cos(a), math.sin(a), 0))
        p = Vector((r*n.x, r*n.y, z))
        d = (n + Vector((0, 0, .5 + (z - .9))) + Vector((rnd.uniform(-.3, .3), rnd.uniform(-.3, .3), rnd.uniform(-.2, .3)))).normalized()
        L = rnd.uniform(.07, .22); rr = rnd.uniform(.012, .022)
        parts[bone_at(z)].append(along("primitive_cone_add", espinho, p, p + d*L, rr, vertices=5, radius1=1, radius2=0))
        if k % 11 == 0:
            parts[bone_at(z)].append(prim("primitive_uv_sphere_add", seiva, p + n*.01, (.012, .012, .012), segments=6, ring_count=4))
    # cardos (plantas secas com flor roxa) brotando da massa
    def thistle(base, top, size, bone):
        o = []
        mid = base.lerp(top, .5) + Vector((rnd.uniform(-.04, .04), rnd.uniform(-.04, .04), 0))
        o.append(along("primitive_cylinder_add", caule, base, mid, .014*size/.1, vertices=6))
        o.append(along("primitive_cylinder_add", caule, mid, top, .011*size/.1, vertices=6))
        for k in range(3):  # folhas espinhosas
            pl = base.lerp(top, .25 + .2*k); a = rnd.uniform(0, 2*math.pi)
            dv = Vector((math.cos(a), math.sin(a), -.2))
            lf = along("primitive_cone_add", caule, pl, pl + dv*size*1.4, .03*size/.1, vertices=4, radius1=1, radius2=0)
            lf.scale.x *= .25; o.append(lf)
        o.append(prim("primitive_uv_sphere_add", caule, top, (size*.55, size*.55, size*.5), segments=10, ring_count=7))
        for k in range(10):  # brácteas espetadas
            a = 2*math.pi*k/10; dv = Vector((math.cos(a), math.sin(a), -.3)).normalized()
            o.append(along("primitive_cone_add", espinho, top + dv*size*.45, top + dv*size*.95, size*.08, vertices=4, radius1=1, radius2=0))
        for k in range(14):  # tufo roxo seco
            a = 2*math.pi*k/14; rr = size*.35*(k % 2 + .4)
            b = top + Vector((rr*.5*math.cos(a), rr*.5*math.sin(a), size*.25))
            o.append(along("primitive_cone_add", flor, b, b + Vector((rr*math.cos(a), rr*math.sin(a), size*(.7 + .3*(k % 3)))),
                           size*.12, vertices=4, radius1=1, radius2=.3))
        parts[bone].extend(o)
    for base, top, size, bone in (((0, 0, 1.6), (.05, .03, 1.88), .11, "crown"), ((.08, .05, 1.52), (.24, .12, 1.78), .09, "crown"),
                                  ((-.08, .02, 1.52), (-.22, .02, 1.74), .08, "crown"),
                                  ((.36, .02, .78), (.6, .06, .98), .08, "body"), ((-.3, .18, .5), (-.5, .3, .72), .07, "base"),
                                  ((-.28, .12, 1.18), (-.42, .18, 1.38), .07, "upper")):
        thistle(Vector(base), Vector(top), size, bone)
    # cruz de ferro cravada nas costas, com corrente partida
    c0, c1 = Vector((-.12, .3, .55)), Vector((-.28, .46, 1.32))
    dv = (c1 - c0).normalized(); side = dv.cross(Vector((0, -1, 0))).normalized()
    cr = [along("primitive_cube_add", ferro, c0, c1, .028)]
    cc = c0.lerp(c1, .74)
    cr.append(along("primitive_cube_add", ferro, cc - side*.17, cc + side*.17, .025))
    for p_ in (c1, cc - side*.17, cc + side*.17):
        cr.append(prim("primitive_uv_sphere_add", ferro, p_, (.04, .04, .04), segments=8, ring_count=6))
    for k in range(4):
        cr.append(prim("primitive_torus_add", ferro, cc + side*.15 + Vector((0, 0, -.05 - .045*k)), (1, 1, 1.5), major_radius=.02,
                       minor_radius=.006, major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
    for k in range(5):  # raiz enrolada na cruz
        cr.append(prim("primitive_torus_add", raiz, c0.lerp(c1, .1 + .1*k), (1, 1, 1.4), major_radius=.05, minor_radius=.016,
                       major_segments=10, minor_segments=5, rot=(20*k, 30, 0)))
    parts["body"].extend(cr)
    for b, ob in parts.items():
        if ob: R.rigid(ob, b)

    # ------------------------------------------------ boca vertical: interior escuro, lábios com dentes de espinho
    mo = [prim("primitive_uv_sphere_add", escuro, (0, -.3, 1.32), (.1, .07, .27), segments=12, ring_count=10)]
    gum = stained("fc_gengiva", (.32, .06, .06), stain=(.1, .01, .01), amount=.4, scale=8, rough=.3, grime=0)
    for s_ in (1, -1):  # gengiva vermelha nas bordas da fenda
        mo.append(prim("primitive_uv_sphere_add", gum, (.07*s_, -.31, 1.32), (.03, .04, .25), segments=10, ring_count=8))
    for z in (1.18, 1.3, 1.44):  # garganta com seiva brilhando lá no fundo
        mo.append(prim("primitive_uv_sphere_add", seiva, (rnd.uniform(-.015, .015), -.345, z), (.012, .01, .016), segments=6, ring_count=4))
    for k in range(3):  # espinhos prontos para cuspir, e baba de seiva
        mo.append(along("primitive_cone_add", espinho, (0, -.28, 1.24 + .1*k), (0, -.37, 1.24 + .1*k), .012, vertices=5,
                        radius1=1, radius2=0))
    mo.append(prim("primitive_uv_sphere_add", seiva, (0, -.36, 1.08), (.012, .012, .02), segments=6, ring_count=4))
    mo.append(along("primitive_cylinder_add", seiva, (0, -.36, 1.08), (0, -.37, 1.0), .005, vertices=4))
    R.rigid(mo, "upper")
    for s, n in ((1, "L"), (-1, "R")):
        lj = {"a": (.05*s, -.3, 1.05, .045), "b": (.095*s, -.33, 1.2, .055), "c": (.095*s, -.33, 1.42, .055), "d": (.045*s, -.29, 1.58, .04)}
        lip = skin_mesh(f"labio.{n}", lj, [("a", "b"), ("b", "c"), ("c", "d")], carne, levels=1)
        lp = [lip]
        for k in range(8):
            z = 1.1 + .06*k; x = .07*s
            lp.append(along("primitive_cone_add", espinho, (x, -.35, z), (x - .065*s, -.35, z - .015), .011, vertices=4, radius1=1, radius2=0))
        for k in range(4):
            z = 1.12 + .13*k
            lp.append(along("primitive_cone_add", espinho, (.13*s, -.34, z), (.21*s, -.41, z + .06), .014, vertices=5, radius1=1, radius2=0))
        R.rigid(lp, f"lip.{n}")

    # ------------------------------------------------ tufos de espinhos grandes (abrem no emerge)
    for s, n in ((1, "L"), (-1, "R")):
        for nm, cnt, L in ((f"spk_hi.{n}", 6, .42), (f"spk_lo.{n}", 5, .34)):
            h, t = P(nm), P(nm, 1); dv = (t - h).normalized()
            q0 = dv.to_track_quat('Z', 'Y'); sp = []
            sp.append(prim("primitive_uv_sphere_add", carne, h, (.09, .09, .09), segments=10, ring_count=7))
            for k in range(cnt):
                a = 2*math.pi*k/cnt + rnd.uniform(-.3, .3); off = q0 @ Vector((math.cos(a), math.sin(a), 0))
                dd = (dv + off*.45).normalized()
                ll = L*rnd.uniform(.7, 1.1)
                sp.append(along("primitive_cone_add", espinho, h + off*.04, h + off*.04 + dd*ll, .026, vertices=6, radius1=1, radius2=0))
            sp.append(prim("primitive_uv_sphere_add", seiva, h + dv*.07, (.016, .016, .016), segments=6, ring_count=4))
            R.rigid(sp, nm)

    # ------------------------------------------------ cipós espinhosos (braços)
    for s, n in ((1, "L"), (-1, "R")):
        pts = [P(f"vine1.{n}") - Vector((.08*s, 0, 0)), P(f"vine2.{n}"), P(f"vine3.{n}"), P(f"vine3.{n}", 1)]
        vj = {f"v{k}": (*p, r) for k, (p, r) in enumerate(zip(pts, (.085, .06, .042, .018)))}
        vm = skin_mesh(f"cipo.{n}", vj, [("v0", "v1"), ("v1", "v2"), ("v2", "v3")], raiz, levels=1)
        R.bind(vm, ["upper", f"vine1.{n}", f"vine2.{n}", f"vine3.{n}"], power=6)
        for k in range(3):
            b = f"vine{k+1}.{n}"; h, t = P(b), P(b, 1); th = []
            for u in (.2, .5, .8):
                c = h.lerp(t, u); a = rnd.uniform(0, 2*math.pi)
                dd = Vector((math.cos(a), math.sin(a), rnd.uniform(-.3, .6))).normalized()
                th.append(along("primitive_cone_add", espinho, c, c + dd*(.1 - .02*k), .014, vertices=4, radius1=1, radius2=0))
            if k == 2:  # garra de espinhos na ponta
                for a in range(3):
                    dd = (t - h).normalized() + Vector((math.cos(a*2.1), math.sin(a*2.1), 0))*.6
                    th.append(along("primitive_cone_add", espinho, t, t + dd.normalized()*.12, .018, vertices=5, radius1=1, radius2=0))
            R.rigid(th, b)

    # ------------------------------------------------ raízes (pernas), lápide quebrada presa numa delas
    for i, (a, L) in enumerate(RA):
        p0, p1, p2 = P(f"root{i}.a"), P(f"root{i}.b"), P(f"root{i}.b", 1)
        mid1 = p0.lerp(p1, .5) + Vector((0, 0, .06)); mid2 = p1.lerp(p2, .5) + Vector((0, 0, .015))
        wob = Vector((-(p2 - p0).normalized().y, (p2 - p0).normalized().x, 0))*(.07 if i % 2 else -.07)
        rj = {"a": (*(p0*.7 + Vector((0, 0, .1))), .14), "m": (*(mid1 + wob + Vector((0, 0, .05))), .085), "b": (*p1, .065),
              "n": (*(mid2 - wob), .042), "c": (*p2, .012)}
        rm = skin_mesh(f"raiz{i}", rj, [("a", "m"), ("m", "b"), ("b", "n"), ("n", "c")], raiz, levels=1)
        R.bind(rm, ["base", f"root{i}.a", f"root{i}.b"], power=6)
        sub = []
        for k in range(2):  # raizinhas
            c = p1.lerp(p2, .3 + .4*k); dv = (p2 - p1).normalized()
            sd = Vector((-dv.y, dv.x, 0))*(1 if k else -1)
            sub.append(along("primitive_cone_add", raiz, c, c + sd*.18 + dv*.1 + Vector((0, 0, -.02)), .022, vertices=5, radius1=1, radius2=0))
        for k in range(3):  # nós e calos na casca
            c = p1.lerp(p2, .1 + .25*k) + Vector((0, 0, .04 - .01*k))
            sub.append(prim("primitive_uv_sphere_add", raiz, c, (.04 - .008*k, .035, .03), segments=8, ring_count=5))
        R.rigid(sub, f"root{i}.b")
    # lápide partida enroscada na raiz traseira esquerda
    i = 3; p0, p1 = P(f"root{i}.a"), P(f"root{i}.b"); c = p0.lerp(p1, .7) + Vector((0, 0, .2))
    dv = (p1 - p0).normalized()
    st = [prim("primitive_cube_add", pedra, c, (.2, .06, .2), rot=(0, 0, math.degrees(math.atan2(dv.y, dv.x)) + 80))]
    st[0].rotation_euler.x = math.radians(-14)
    st.append(prim("primitive_cylinder_add", pedra, c + Vector((0, 0, .18)), (.2, .06, .1), vertices=16,
                   rot=(90, 0, math.degrees(math.atan2(dv.y, dv.x)) + 80)))
    st[1].rotation_euler.x = math.radians(90 - 14)
    for k in range(2):
        st.append(prim("primitive_torus_add", raiz, c + Vector((0, 0, -.06 + .14*k)), (1.3, .7, 1), major_radius=.19, minor_radius=.025,
                       major_segments=14, minor_segments=5, rot=(10*k, 0, math.degrees(math.atan2(dv.y, dv.x)) + 80)))
    R.rigid(st, f"root{i}.a")
    safe_ground(R)
    return R, INFO

# ======================================================================= animações
def turn(R, bone, lift=0, swing=0):
    """Gira um osso (eixos do mundo na pose de ligação): lift ergue a ponta, swing gira em volta de Z."""
    d = (R.P(bone, 1) - R.P(bone)).normalized(); ax = d.cross(Vector((0, 0, 1)))
    q = Quaternion(Vector((0, 0, 1)), math.radians(swing))
    if ax.length > 1e-4: q = q @ Quaternion(ax.normalized(), math.radians(lift))
    e = q.to_euler('YXZ')
    return {bone: {"x": math.degrees(e.x), "y": math.degrees(e.y), "z": math.degrees(e.z)}}

def anims(R):
    T = lambda *a, **k: turn(R, *a, **k)
    def roots(lifts_a=None, lifts_b=None, swings=None):
        out = {}
        for i in range(len(RA)):
            out.update(T(f"root{i}.a", (lifts_a or [0]*6)[i], (swings or [0]*6)[i]))
            out.update(T(f"root{i}.b", (lifts_b or [0]*6)[i]))
        return out
    def spikes(open_=0):
        o = {}
        for s, n in ((1, "L"), (-1, "R")):
            o.update(T(f"spk_hi.{n}", open_)); o.update(T(f"spk_lo.{n}", open_))
        return o
    def lips(a): return {"lip.L": {"z": a}, "lip.R": {"z": -a}}
    BASE = merge({"body": {"x": 6, "z": -6}, "upper": {"x": 8, "z": 8}, "crown": {"x": -6},
                  "vine1.L": {"y": 10}, "vine1.R": {"y": -14}, "vine2.L": {"bend": -10}, "vine2.R": {"bend": -16}},
                 roots([0, 0, 0, 0, 0, 0], [-4]*6))
    B = lambda *p: merge(BASE, *p)
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; b = math.sin(t); c = math.cos(t)
        idle.append(B(lips(14 + 8*max(0, b)), spikes(6*b), {"body": {"x": 2*b, "z": 3*c}, "upper": {"x": -3*b, "z": -3*c},
                      "crown": {"x": 4*b}, "vine1.L": {"y": 4*b}, "vine1.R": {"y": -4*b}, "vine2.L": {"bend": -6*c},
                      "vine2.R": {"bend": 6*c}, "vine3.L": {"bend": -8*b}, "vine3.R": {"bend": 8*b}},
                    roots(None, [-4 + 4*b*(1 if k % 2 else -1) for k in range(6)])))
    # andar: arrasta-se sobre as raízes; as da frente avançam e cravam, as de trás empurram
    walk = []
    for i in range(8):
        t = i/8; p = 2*math.pi*t; s = math.sin(p); c = math.cos(p)
        la = [0]*6; lb = [-4]*6; sw = [0]*6
        for k, (a, L) in enumerate(RA):
            ph = p + (0 if k in (0, 3, 4) else math.pi)
            up = max(0, math.sin(ph))
            la[k] = 14*up; lb[k] = -4 - 10*up
            fwd = -math.sin(math.radians(a))  # componente para a frente (-Y)
            sw[k] = 14*math.cos(ph)*(1 if math.cos(math.radians(a)) > 0 else -1)*(.5 + .5*abs(fwd))
        walk.append(B(roots(la, lb, sw), lips(12), {"body": {"x": 4 + 4*abs(s), "y": 5*s, "z": 6*c}, "upper": {"x": 4*abs(c), "y": -4*s},
                                                    "crown": {"y": -6*s}, "vine1.L": {"y": -8*s, "x": -10*s}, "vine1.R": {"y": -8*s, "x": 10*s},
                                                    "vine2.L": {"bend": -10*max(0, s)}, "vine2.R": {"bend": -10*max(0, -s)},
                                                    "root": (0, -.03*s, 0)}))
    # ataque: recua, incha, projeta a boca para a frente e cospe (3 espinhos voam do jogo)
    back = B(lips(-6), spikes(10), {"body": {"x": -14}, "upper": {"x": -22}, "crown": {"x": -10},
                                    "vine1.L": {"y": -30, "x": -20}, "vine1.R": {"y": 30, "x": -20}, "root": (0, .08, 0)})
    spit = B(lips(34), spikes(-6), {"body": {"x": 20}, "upper": {"x": 4}, "crown": {"x": -4},
                                    "vine1.L": {"y": 20, "x": 10}, "vine1.R": {"y": -20, "x": 10}, "root": (0, -.1, 0)})
    attack = keys_to_frames([(0, idle[0]), (.32, back), (.46, spit), (.6, merge(spit, lips(-8), {"upper": {"x": -4}})),
                             (1, idle[0])], 10)
    hitp = B(lips(20), spikes(16), {"body": {"x": -12, "z": 8}, "upper": {"x": -18, "z": -10}, "crown": {"x": -14},
                                    "vine1.L": {"y": -25}, "vine1.R": {"y": 25}, "root": (0, .06, 0)})
    hit = [hitp, lerp_pose(hitp, idle[0], .5), idle[0]]
    # enterrar: crava as raízes, fecha os espinhos e afunda até sumir
    OCC = {"occ": {"x": 180}}
    grip = B(OCC, roots([-14]*6, [-12]*6), spikes(-30), lips(-2), {"body": {"x": 10}, "upper": {"x": 14}, "crown": {"x": 12},
             "vine1.L": {"y": 40}, "vine1.R": {"y": -40}, "vine2.L": {"bend": -40}, "vine2.R": {"bend": -40}, "ground": None,
             "root": (0, 0, -.05)})
    burrow = keys_to_frames([(0, B(OCC, {"ground": None})), (.2, grip),
                             (.45, merge(grip, {"body": {"z": 20}, "upper": {"z": 10}, "root": (0, 0, -.55)})),
                             (.7, merge(grip, {"body": {"z": -15}, "upper": {"z": -10}, "root": (0, 0, -1.3)})),
                             (.88, merge(grip, {"crown": {"x": -14}, "root": (0, 0, -1.95)})),
                             (1, merge(grip, {"root": (0, 0, -2.4)}))], 10)
    # brotar: sai do chão de uma vez, fechado, e abre os espinhos
    out_ = B(OCC, spikes(-35), lips(0), {"body": {"x": -6}, "upper": {"x": -8}, "crown": {"x": -4},
             "vine1.L": {"y": 40}, "vine1.R": {"y": -40}, "vine2.L": {"bend": -40}, "vine2.R": {"bend": -40}, "ground": None})
    flare = B(OCC, spikes(28), lips(30), roots([10]*6, [-14]*6), {"body": {"x": -14}, "upper": {"x": -18}, "crown": {"x": -16},
              "vine1.L": {"y": -30, "x": -10}, "vine1.R": {"y": 30, "x": -10}, "vine2.L": {"bend": 10}, "vine2.R": {"bend": 10},
              "ground": None, "root": (0, 0, .12)})
    emerge = keys_to_frames([(0, merge(out_, {"root": (0, 0, -1.5)})), (.14, merge(out_, {"root": (0, 0, -.7)})),
                             (.3, merge(out_, {"root": (0, 0, .1)})), (.5, flare),
                             (.7, merge(flare, spikes(-8), {"root": (0, 0, 0)})), (1, B(OCC, {"ground": None}))], 8)
    # morte: murcha e desaba para a frente; espinhos e cipós caem, raízes se enrolam
    sag = B(lips(26), spikes(-20), roots([6]*6, [10]*6), {"body": {"x": 10, "z": 14}, "upper": {"x": 24, "z": -10}, "crown": {"x": 20},
            "vine1.L": {"y": 30}, "vine1.R": {"y": -30}, "vine2.L": {"bend": -30}, "vine2.R": {"bend": -30}})
    dead = B(lips(34), spikes(-45), roots([10]*6, [22]*6), {"body": {"x": 42, "z": 20}, "upper": {"x": 46, "z": -16}, "crown": {"x": 40},
             "base": {"x": 8}, "vine1.L": {"y": 60, "x": 20}, "vine1.R": {"y": -60, "x": 20}, "vine2.L": {"bend": -10},
             "vine2.R": {"bend": -10}, "ground_all": True, "gb": None, "ground": .02})
    death = keys_to_frames([(0, hitp), (.25, merge(hitp, {"upper": {"x": -8}})), (.5, sag), (.8, dead),
                            (1, merge(dead, {"crown": {"x": 8}, "upper": {"x": 4}}))], 10)
    for p in death[5:]:
        p["ground_all"] = True; p["gb"] = None
    return {"idle": idle, "walk": walk, "attack": attack, "burrow": burrow, "emerge": emerge, "hit": hit, "death": death}
