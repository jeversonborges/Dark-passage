# Serpente do Éden (Novo Éden, Ninho da Serpente, nível 24-27): "a serpente era o mais astuto de todos os
# animais" (Gn 3:1). Cobra de 4 m enrolada aos pés da Árvore do Conhecimento, que comeu do fruto do Amargo e
# ficou: escamas pretas-oliva com a barriga cor de osso, uma fileira de escamas acesas no verde do Amargo ao
# longo da espinha, capelo de naja com dois "olhos" desenhados (as marcas da Enxertia? não: são de nascença),
# olhos verdes, língua bífida. O terço da frente fica erguido o tempo todo, balançando; a cauda enrolada no chão.
# Brilho: verde do Amargo (olhos, escamas da espinha, dentro da boca). Neutra: só ataca se mexerem com ela.
# Variante a_serpente (elite, dados.json): tinta mais clara e 1,6x maior.
# Rig próprio: cadeia de ossos ao longo da curva do corpo (mid no chão -> b1..b3 para a cauda, f1..f5 para o
# pescoço erguido -> head, jaw, hood.L/R, tongue). Poses usam x (inclina para a frente) e z (gira) em graus.
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *
from quad import join

INFO = {"px": 256, "target_z": 1.2, "rim": (.5, 1, .55), "colors": 40, "samples": 44,
        "fps": {"idle": 6, "walk": 10, "attack": 12, "hit": 12, "death": 10}, "loops": ("idle", "walk")}

VARIANTS = {"serpente_do_eden": {}}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
set_variant("serpente_do_eden")

# pontos da curva do corpo (cauda -> cabeça)
PTS = [Vector(p) for p in [(.85, .55, .08), (.45, .9, .1), (-.3, .8, .12), (-.6, .25, .13), (-.15, -.08, .15), (.3, -.02, .17),
                            (.4, -.26, .5), (.16, -.4, 1.0), (-.04, -.33, 1.32), (0, -.48, 1.52)]]
HEAD_TIP = Vector((0, -.8, 1.46))
RADII = [.035, .08, .13, .15, .16, .15, .13, .115, .1, .095]
NAMES_BACK = ["b1", "b2", "b3"]; NAMES_FRONT = ["f1", "f2", "f3", "f4", "f5"]

def bones():
    B = {"mid": (tuple(PTS[3]), tuple(PTS[4]), None)}
    prev = "mid"
    for i, n in enumerate(NAMES_BACK):
        B[n] = (tuple(PTS[3 - i]), tuple(PTS[2 - i]), prev); prev = n
    prev = "mid"
    for i, n in enumerate(NAMES_FRONT):
        B[n] = (tuple(PTS[4 + i]), tuple(PTS[5 + i]), prev); prev = n
    B["head"] = (tuple(PTS[9]), tuple(HEAD_TIP), "f5")
    B["jaw"] = (tuple(PTS[9] + Vector((0, -.06, -.04))), (0, -.76, 1.36), "head")
    B["hood.L"] = (tuple(PTS[9] + Vector((.04, .03, -.02))), tuple(PTS[9] + Vector((.3, .06, -.1))), "f5")
    B["hood.R"] = (tuple(PTS[9] + Vector((-.04, .03, -.02))), tuple(PTS[9] + Vector((-.3, .06, -.1))), "f5")
    B["tongue"] = (tuple(HEAD_TIP + Vector((0, .02, -.03))), tuple(HEAD_TIP + Vector((0, -.2, -.06))), "head")
    return B

def glow(name, rgb, strength):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes):
        if nd.type != 'OUTPUT_MATERIAL': nt.nodes.remove(nd)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*rgb, 1); em.inputs["Strength"].default_value = strength
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = (*rgb, 1)
    lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); nt.links.new(df.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], [nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL'][0].inputs["Surface"])
    return m

def spline(pts, n):
    """Catmull-Rom pelos pontos; devolve n amostras (posição) de ponta a ponta."""
    out = []
    P = [pts[0]] + list(pts) + [pts[-1]]
    segs = len(pts) - 1
    for k in range(n):
        u = k/(n - 1)*segs; i = min(int(u), segs - 1); t = u - i
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        out.append(.5*((2*p1) + (-p0 + p2)*t + (2*p0 - 5*p1 + 4*p2 - p3)*t*t + (-p0 + 3*p1 - 3*p2 + p3)*t*t*t))
    return out

def body_mesh(name, pts, radii, m_top, m_belly, m_glow, n=70, seg=18, seed=5):
    """Tubo ao longo da curva com seção um pouco achatada; faces de baixo com a barriga clara; escamas em relevo
    (ruído radial) e uma fileira de escamas acesas na espinha."""
    rr = random.Random(seed)
    P = spline(pts, n); R = spline([Vector((r, 0, 0)) for r in radii], n)
    bm = bmesh.new(); rings = []
    up0 = Vector((0, 0, 1))
    for i, c in enumerate(P):
        t = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        side = t.cross(up0); side = side.normalized() if side.length > 1e-4 else Vector((1, 0, 0))
        up = side.cross(t).normalized()
        r = R[i].x; ring = []
        for j in range(seg):
            a = 2*math.pi*j/seg
            sx, sz = math.cos(a), math.sin(a)
            # seção: mais larga que alta, barriga chata
            rad = r*(1 + .06*math.sin(a*7 + i*.9)*(1 if sz > -.3 else 0))
            z = sz*.82 if sz > 0 else sz*.6
            ring.append(bm.verts.new(c + side*sx*rad + up*z*rad))
        rings.append(ring)
    for i in range(n - 1):
        for j in range(seg):
            f = bm.faces.new((rings[i][j], rings[i][(j + 1) % seg], rings[i + 1][(j + 1) % seg], rings[i + 1][j]))
            a = 2*math.pi*(j + .5)/seg
            f.material_index = 1 if math.sin(a) < -.45 else 0
            f.smooth = True
    # tampa da cauda
    bm.faces.new(rings[0][::-1]).smooth = True
    o = bpy.data.objects.new(name, bpy.data.meshes.new(name)); bm.to_mesh(o.data); bm.free()
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m_top); o.data.materials.append(m_belly)
    for p in o.data.polygons: p.use_smooth = True
    # escamas acesas na espinha (a cada 3 anéis, do meio do corpo até a nuca)
    parts = [o]
    for i in range(10, n - 7, 3):
        c = P[i]; t = (P[i + 1] - P[i - 1]).normalized(); side = t.cross(up0).normalized(); up = side.cross(t).normalized()
        r = R[i].x; s = r*.16
        g = prim("primitive_uv_sphere_add", m_glow, c + up*r*.8, (s, s*1.6, s*.5), segments=8, ring_count=5)
        g.rotation_euler = up.to_track_quat('Z', 'Y').to_euler(); parts.append(g)
    return join(parts)

def build():
    rnd = random.Random(9)
    escama = stained("se_escama", (.06, .08, .04), stain=(.02, .03, .015), amount=.5, scale=18, rough=.6,
                     blotch=(.2, .22, .09), blotch_amt=.7, grime=.8, dirt=.4)
    barriga = stained("se_barriga", (.42, .38, .26), stain=(.18, .12, .06), amount=.3, scale=8, rough=.5, grime=.5, dirt=.3)
    capelo = stained("se_capelo", (.09, .11, .05), stain=(.04, .05, .02), amount=.4, scale=10, rough=.45, blotch=(.16, .18, .08), blotch_amt=.5, grime=.5)
    mancha = mat("se_mancha", (.5, .46, .3), 0, .5, dirt=.3, grime=.3)
    boca = mat("se_boca", (.12, .22, .06), 0, .3, emit=(.3, 1, .35), strength=1.5)
    presa = mat("se_presa", (.5, .46, .36), 0, .35, dirt=.3)
    lingua = mat("se_lingua", (.1, .02, .02), 0, .3)
    lume = glow("se_lume", (.3, 1, .35), 2.0)
    olho = glow("se_olho", (.5, 1, .35), 14)

    R = Rig("serpente", bones(), ground=.03, ground_bones=["mid", "b1", "b2", "b3", "f1"]); P = R.P
    body = body_mesh("corpo", PTS, RADII, escama, barriga, lume)
    R.bind(body, ["mid"] + NAMES_BACK + NAMES_FRONT + ["head"], power=4, top=3)

    # cabeça em cunha, olhos, boca, presas, língua
    h0, h1 = P("head"), P("head", 1); d = (h1 - h0).normalized()
    hd = [prim("primitive_uv_sphere_add", escama, h0 + d*.13, (.115, .19, .085), segments=14, ring_count=10)]
    hd[0].rotation_euler = d.to_track_quat('Y', 'Z').to_euler()
    hd.append(prim("primitive_uv_sphere_add", escama, h0 + d*.27, (.075, .1, .055), segments=12, ring_count=8))   # focinho
    hd.append(prim("primitive_uv_sphere_add", barriga, h0 + d*.14 + Vector((0, 0, -.045)), (.08, .15, .03), segments=12, ring_count=6))
    for s in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", capelo, h0 + d*.1 + Vector((.075*s, 0, .035)), (.03, .035, .025), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", olho, h0 + d*.1 + Vector((.088*s, -.01, .04)), (.02, .024, .018), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", mancha, h0 + d*.1 + Vector((.09*s, -.005, .042)), (.006, .02, .006), segments=6, ring_count=4))  # pupila fendida
    R.rigid(hd, "head")
    j0, j1 = P("jaw"), P("jaw", 1); dj = (j1 - j0).normalized()
    jw = [prim("primitive_uv_sphere_add", escama, j0 + dj*.12, (.075, .14, .035), segments=12, ring_count=8)]
    jw[0].rotation_euler = dj.to_track_quat('Y', 'Z').to_euler()
    jw.append(prim("primitive_uv_sphere_add", boca, j0 + dj*.12 + Vector((0, 0, .012)), (.06, .12, .02), segments=10, ring_count=6))
    jw[-1].rotation_euler = jw[0].rotation_euler
    R.rigid(jw, "jaw")
    # céu da boca e presas presos na cabeça (aparecem quando a boca abre)
    pr = [prim("primitive_uv_sphere_add", boca, h0 + d*.16 + Vector((0, 0, -.03)), (.06, .11, .015), segments=10, ring_count=6)]
    pr[0].rotation_euler = hd[0].rotation_euler
    for s in (1, -1):
        pr.append(along("primitive_cone_add", presa, h0 + d*.24 + Vector((.035*s, 0, -.03)), h0 + d*.25 + Vector((.03*s, 0, -.1)), .012, vertices=6, radius1=1, radius2=0))
    R.rigid(pr, "head")
    t0, t1 = P("tongue"), P("tongue", 1)
    tg = [along("primitive_cylinder_add", lingua, t0, t0.lerp(t1, .65), .007, vertices=5)]
    for s in (1, -1):
        tg.append(along("primitive_cone_add", lingua, t0.lerp(t1, .65), t1 + Vector((.035*s, 0, -.01)), .006, vertices=4, radius1=1, radius2=0))
    R.rigid(tg, "tongue")
    # capelo de naja: duas abas achatadas com um "olho" claro desenhado em cada
    for s, n in ((1, "L"), (-1, "R")):
        a0, a1 = P(f"hood.{n}"), P(f"hood.{n}", 1); c = a0.lerp(a1, .55); dd = (a1 - a0).normalized()
        fl = prim("primitive_uv_sphere_add", capelo, c, (.2, .03, .27), segments=14, ring_count=10)
        fl.rotation_euler = (0, 0, math.atan2(dd.y, dd.x)); fl.rotation_euler.y = -.35*s
        parts = [fl, prim("primitive_uv_sphere_add", mancha, c + Vector((.01*s, -.03, .02)), (.05, .012, .07), segments=10, ring_count=6),
                 prim("primitive_uv_sphere_add", capelo, c + Vector((.01*s, -.04, .02)), (.025, .012, .035), segments=8, ring_count=5)]
        parts[1].rotation_euler = fl.rotation_euler; parts[2].rotation_euler = fl.rotation_euler
        R.rigid(parts, f"hood.{n}")
    R.arm.scale = [V.get("scale", 1)]*3
    return R, INFO

# ======================================================================= animações
BASE = {"hood.L": {"z": 10}, "hood.R": {"z": -10}, "jaw": {"x": -3}}
def M(*p): return merge(BASE, *p)
def neck(x2=0, x3=0, x4=0, x5=0, hx=0, z=0):
    return {"f2": {"x": x2, "z": z}, "f3": {"x": x3, "z": z*.6}, "f4": {"x": x4, "z": z*.4}, "f5": {"x": x5}, "head": {"x": hx, "z": -z*.5}}
def tail(t, amp=10, ph=.9):
    return {"b1": {"z": amp*math.sin(t)}, "b2": {"z": amp*math.sin(t - ph)}, "b3": {"z": amp*1.4*math.sin(t - 2*ph)}}
def tongue(k): return {"scale": {"tongue": k}}

def anims(R):
    idle = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t)
        idle.append(M(neck(2*s, 3*c, -3*s, 2*c, -3*c, 8*s), tail(t*.5, 4), {"hood.L": {"z": 10 + 4*c}, "hood.R": {"z": -10 - 4*c}},
                      tongue(1 if 2 <= i <= 4 else .001)))
    # rastejar: a cauda ondula e o corpo avança; o pescoço fica erguido, oscilando
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s = math.sin(t)
        walk.append(M(neck(-4 + 3*s, 4*math.sin(t - .6), -2*s, 2*s, 2*s, 10*math.sin(t - 1.2)), tail(t, 16, 1.1),
                      {"mid": {"z": 5*s}, "f1": {"z": -6*s}, "root": (0, .03*math.cos(t), 0)}, tongue(1 if i % 4 == 0 else .001)))
    # bote: recua e abre o capelo, dispara para a frente com a boca aberta, volta
    back = M(neck(-14, -18, -10, 4, -12, 0), {"hood.L": {"z": 28}, "hood.R": {"z": -28}, "jaw": {"x": 12}, "root": (0, .08, 0)})
    strike = M(neck(26, 30, 22, 14, 10, 0), {"hood.L": {"z": 30}, "hood.R": {"z": -30}, "jaw": {"x": 42}, "f1": {"x": 10}, "root": (0, -.3, -.02)}, tongue(.001))
    bite = merge(strike, {"jaw": {"x": 6}, "head": {"x": 16}})
    attack = keys_to_frames([(0, M()), (.25, back), (.4, back), (.52, strike), (.62, bite), (.8, lerp_pose(bite, M(), .5)), (1, M())], 10)
    hitp = M(neck(-10, -14, -8, -4, -16, 12), {"jaw": {"x": 18}, "hood.L": {"z": 22}, "hood.R": {"z": -22}, "root": (0, .06, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: o pescoço cede e o corpo da frente desaba no chão, a boca fica aberta, o capelo fecha
    sag = M(neck(14, 20, 18, 14, 20, 15), {"jaw": {"x": 20}, "hood.L": {"z": 0}, "hood.R": {"z": 0}})
    down = M(neck(40, 55, 40, 25, 20, 25), {"jaw": {"x": 26}, "hood.L": {"z": -15, "x": 20}, "hood.R": {"z": 15, "x": 20}, "f1": {"x": 12}, "ground_all": True, "ground": .04})
    flat = M(neck(55, 70, 45, 28, 15, 30), {"jaw": {"x": 30}, "hood.L": {"z": -20, "x": 30}, "hood.R": {"z": 20, "x": 30}, "f1": {"x": 16},
             "b1": {"z": 8}, "b2": {"z": -6}, "ground_all": True, "ground": .04}, tongue(.001))
    death = keys_to_frames([(0, hitp), (.3, sag), (.6, down), (.85, flat), (1, merge(flat, {"jaw": {"x": 24}}))], 10)
    return {"idle": idle, "walk": walk, "attack": attack, "hit": hit, "death": death}
