# Familiar do Cultista (skill Pacto do Familiar): um demônio de estimação que evolui com o nível do dono.
#   familiar:diabrete  Diabrete de Fuligem (nível 1, 0,75 m): diabinho cinza-fuligem de cabeça grande, orelhas
#                      de morcego, óculos de soldador rachados na testa, avental de couro queimado, coleira com
#                      lacre de cera do pacto, asinhas rasgadas e rabo de ponta de seta.
#   familiar:algoz     Algoz de Enxofre (nível 6, 1,9 m): carrasco curvado, capuz de couro com chifres serrados,
#                      tronco costurado, colar de ferro com corrente e gancho, saiote de couro com fivelas,
#                      cutelo de açougue, pernas de bode com trapos.
#   familiar:tirano    Tirano da Fornalha (nível 16, 2,7 m): couraçado da Legião Blasfema. Chifres de carneiro,
#                      máscara de ferro na mandíbula, peitoral rebitado com a grade de uma fornalha acesa,
#                      duas chaminés nas costas, braço esquerdo com manopla de cravos, canhão de brasa no lugar
#                      do antebraço direito, perna direita de pistão, tabardo com o selo da Legião.
# Brilho único (regra da Ferrugem Sagrada): brasa laranja (olhos, boca, fornalha, cano do canhão).
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *

VARIANTS = {
 "diabrete": {"s": .44, "w": 1.15, "px": 160, "target_z": .4,  "samples": 40},
 "algoz":    {"s": 1.06, "w": 1.28, "px": 256, "target_z": 1.0, "samples": 36},
 "tirano":   {"s": 1.5, "w": 1.36, "px": 352, "target_z": 1.4, "samples": 32},
}
V = dict(VARIANTS["diabrete"], name="diabrete")
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name

def info():
    return {"px": V["px"], "target_z": V["target_z"], "rim": (1, .42, .16), "rim_e": 9.0, "colors": 44,
            "samples": V["samples"], "loops": ("idle", "walk"),
            "fps": {"idle": 6, "walk": 9, "attack": 12, "hit": 12, "death": 9}}

# ======================================================================= esqueleto
def bones():
    s, w = V["s"], V["w"]
    B = humanoid(s, w)
    hz = B["hips"][0][2]
    # rabo (3 ossos) saindo da base das costas, caindo até perto do chão
    t0 = Vector((0, .08*s, hz - .02*s))
    pts = [t0, t0 + Vector((0, .28, -.28))*s, t0 + Vector((.06, .62, -.62))*s, t0 + Vector((.16, .98, -.8))*s]
    if V["name"] == "diabrete":   # rabo erguido em S, mais longo que o corpo
        pts = [t0, t0 + Vector((0, .3, -.2))*s, t0 + Vector((.1, .62, .05))*s, t0 + Vector((.18, .8, .45))*s]
    for i in range(3):
        B[f"tail{i+1}"] = (tuple(pts[i]), tuple(pts[i+1]), "hips" if i == 0 else f"tail{i}")
    if V["name"] == "diabrete":   # asinhas
        for sd, n in ((1, "L"), (-1, "R")):
            B[f"wing.{n}"] = ((.08*sd*s*w, .1*s, 1.4*s), (.42*sd*s*w, .34*s, 1.72*s), "chest")
    if V["name"] == "algoz":      # cutelo na mão direita
        h, t = Vector(B["hand.R"][0]), Vector(B["hand.R"][1])
        B["cleaver"] = (tuple(t), tuple(t + Vector((0, -.05, -.6))), "hand.R")
    return B

# ======================================================================= materiais
def mats():
    nm = V["name"]
    M = {}
    if nm == "diabrete":
        M["skin"] = stained("f_pele", (.15, .12, .11), stain=(.25, .05, .02), amount=.4, scale=5, rough=.5,
                            blotch=(.2, .07, .04), blotch_amt=.6, grime=.9)
    elif nm == "algoz":
        M["skin"] = stained("f_pele", (.2, .085, .065), stain=(.06, .04, .035), amount=.45, scale=4, rough=.45,
                            blotch=(.09, .05, .045), blotch_amt=.7, grime=1.0)
    else:
        M["skin"] = stained("f_pele", (.2, .07, .05), stain=(.03, .02, .02), amount=.5, scale=3, rough=.42,
                            blotch=(.06, .03, .03), blotch_amt=.7, grime=.8)
    M["horn"] = stained("f_chifre", (.1, .085, .07), stain=(.02, .015, .01), amount=.35, scale=4, rough=.5, grime=.3)
    M["bone"] = stained("f_osso", (.4, .36, .28), stain=(.15, .04, .02), amount=.35, scale=5, rough=.6, grime=.6)
    M["leather"] = stained("f_couro", (.11, .065, .04), stain=(.2, .02, .01), amount=.55, scale=3, rough=.4, grime=.7)
    M["dleather"] = stained("f_couro_esc", (.035, .028, .026), stain=(.12, .03, .015), amount=.35, scale=4, rough=.5)
    M["iron"] = stained("f_ferro", (.08, .072, .066), stain=(.3, .1, .035), amount=.55, scale=5, metal=.85, rough=.5, grime=.5)
    M["steel"] = stained("f_aco", (.42, .4, .38), stain=(.25, .04, .02), amount=.5, scale=6, metal=1, rough=.38, grime=.3)
    M["brass"] = stained("f_latao", (.4, .26, .09), stain=(.08, .06, .03), amount=.4, scale=6, metal=1, rough=.4, grime=.3)
    M["cloth"] = stained("f_pano", (.16, .13, .1), stain=(.05, .04, .03), amount=.5, scale=3, rough=.95,
                         blotch=(.08, .06, .05), blotch_amt=.6, grime=1.2)
    M["wax"] = stained("f_cera", (.32, .03, .025), stain=(.1, .01, .01), amount=.3, scale=6, rough=.35, grime=.2)
    M["wing"] = stained("f_asa", (.13, .05, .04), stain=(.04, .02, .02), amount=.5, scale=3, rough=.6, grime=.4)
    M["ember"] = mat("f_brasa", (1, .5, .15), emit=(1, .38, .07), strength=8)
    M["ember_low"] = mat("f_brasa_funda", (.6, .15, .03), emit=(1, .3, .05), strength=2.2)   # discos grandes (fornalha, canos)
    M["crimson"] = stained("f_tabardo", (.13, .03, .025), stain=(.04, .03, .025), amount=.5, scale=3, rough=.9,
                           blotch=(.06, .04, .035), blotch_amt=.6, grime=1.0)
    M["dark"] = mat("f_escuro", (.01, .004, .003), 0, .9)
    return M

# ======================================================================= peças comuns
def membrane(name, a, fingers, m, scallop=.28, rows=5, cols=4, thick=.008, tears=(), seed=1):
    """Membrana de morcego entre dedos (pontos): grade do pulso até as pontas, borda de fora em arcos.
    tears: índices de vãos com um rasgo."""
    rnd = random.Random(seed); bm = bmesh.new(); a = Vector(a)
    for i in range(len(fingers) - 1):
        f0, f1 = Vector(fingers[i]), Vector(fingers[i+1]); grid = []
        for r in range(rows + 1):
            t = r/rows; row = []
            for c in range(cols + 1):
                u = c/cols; edge = f0.lerp(f1, u)
                k = 1 - scallop*math.sin(math.pi*u)*t**2
                p = a + (edge - a)*t*k + Vector((0, .01*math.sin(u*math.pi)*t, 0))
                row.append(bm.verts.new(p))
            grid.append(row)
        for r in range(rows):
            for c in range(cols):
                if i in tears and r >= rows - 2 and c in (1, 2) and (r == rows - 1 or c == 2): continue
                bm.faces.new((grid[r][c], grid[r][c+1], grid[r+1][c+1], grid[r+1][c]))
    bm.normal_update(); o = obj_from_bm(name, bm, m)
    o.modifiers.new("s", 'SOLIDIFY').thickness = thick; apply_mods(o)
    return o

def horn_curve(start, d0, turn, n, step, r0, m, parts, taper=1.0):
    """Chifre em segmentos cônicos: d0 direção inicial, turn = quaternion aplicado a cada passo."""
    pts = [Vector(start)]; d = Vector(d0).normalized()
    for k in range(n):
        d = (turn @ d).normalized(); pts.append(pts[-1] + d*step)
    for k in range(n):
        f0 = 1 - taper*k/n; f1 = 1 - taper*(k+1)/n
        parts.append(along("primitive_cone_add", m, pts[k], pts[k+1], r0*f0, vertices=8, radius1=1, radius2=max(f1/f0, .02)))
    return pts

def claws(R, n, m_skin, m_claw, size, fingers=4, parts=None):
    o, ax, u, sd = R.frame(f"hand.{n}", up=Vector((0, 0, 1)))
    out = parts if parts is not None else []
    g = prim("primitive_uv_sphere_add", m_skin, o + ax*.045*size, (.05*size, .06*size, .045*size), segments=12, ring_count=8)
    g.rotation_euler = ax.to_track_quat('Y', 'Z').to_euler(); out.append(g)
    for f in range(fingers):
        side = (-.04 + .08*f/(fingers-1))*size
        b = o + ax*.08*size + sd*side; mid = b + ax*.06*size - u*.02*size; tip = mid + ax*.05*size - u*.05*size
        out.append(along("primitive_cylinder_add", m_skin, b, mid, .014*size, vertices=6))
        out.append(along("primitive_cone_add", m_claw, mid, tip, .012*size, vertices=5, radius1=1, radius2=0))
    return out

def hoof(R, n, m_skin, m_horn, size):
    """Pé de bode: canela fina e casco fendido no lugar do pé."""
    a, t = R.P(f"foot.{n}"), R.P(f"foot.{n}", 1)
    parts = [prim("primitive_uv_sphere_add", m_horn, a.lerp(t, .45) + Vector((0, 0, -.01*size)), (.05*size, .07*size, .035*size),
                  segments=12, ring_count=6)]
    for sx in (1, -1):
        parts.append(prim("primitive_uv_sphere_add", m_horn, a.lerp(t, .85) + Vector((.022*sx*size, 0, -.012*size)),
                          (.024*size, .04*size, .025*size), segments=8, ring_count=5))
    return parts

def chain(a, b, n, r, m, parts, sag=0.0):
    a, b = Vector(a), Vector(b)
    for k in range(n):
        t = (k + .5)/n; q = a.lerp(b, t) + Vector((0, 0, -sag*4*t*(1-t)))
        parts.append(prim("primitive_torus_add", m, q, (1, 1, 1.5), major_radius=r, minor_radius=r*.3,
                          major_segments=8, minor_segments=4, rot=(90*(k % 2), 0, 0)))
        parts[-1].rotation_euler = ((b - a).to_track_quat('Z', 'Y') @ Quaternion((0, 0, 1), math.pi/2*(k % 2))).to_euler()

def wax_seal(c, normal, r, M, parts):
    """Lacre de cera do pacto: disco irregular, sinete com brilho de brasa no centro."""
    n = Vector(normal).normalized()
    d = prim("primitive_cylinder_add", M["wax"], c, (r, r, r*.22), vertices=14)
    d.rotation_euler = n.to_track_quat('Z', 'Y').to_euler(); parts.append(d)
    for k in range(5):
        a = 2*math.pi*k/5 + .3
        off = (n.to_track_quat('Z', 'Y') @ Vector((math.cos(a), math.sin(a), 0)))*r*.95
        parts.append(prim("primitive_uv_sphere_add", M["wax"], c + off, (r*.32, r*.32, r*.18), segments=8, ring_count=5))
    parts.append(prim("primitive_uv_sphere_add", M["ember"], c + n*r*.2, (r*.25, r*.25, r*.25), segments=8, ring_count=5))
    parts.append(prim("primitive_torus_add", M["dark"], c + n*r*.18, (1, 1, 1), major_radius=r*.55, minor_radius=r*.08,
                      major_segments=12, minor_segments=4))
    parts[-1].rotation_euler = n.to_track_quat('Z', 'Y').to_euler()

def tail(R, M, r0, tip, parts_tip=None):
    for i in range(3):
        b = f"tail{i+1}"; a, c = R.P(b), R.P(b, 1)
        f0, f1 = 1 - i/3.3, 1 - (i+1)/3.3
        ps = [along("primitive_cone_add", M["skin"], a, c, r0*f0, vertices=10, radius1=1, radius2=f1/f0)]
        for k in range(3):   # vértebras salientes
            q = a.lerp(c, (k + .5)/3)
            ps.append(along("primitive_cone_add", M["horn"], q, q + Vector((0, 0, r0*f0*1.1)), r0*f0*.35, vertices=4, radius1=1, radius2=0))
        if i == 2 and tip:
            d = (c - a).normalized(); sd = d.cross(Vector((0, 0, 1))).normalized()
            ps.append(along("primitive_cone_add", M["horn"], c - d*r0*.4, c + d*r0*3.2, r0*1.6, vertices=4, radius1=1, radius2=0))
            ps[-1].scale = (r0*1.6, r0*.35, ps[-1].scale[2])
        R.rigid(ps, b)

def body(R, M, rad, legs_mat=None):
    """Tronco, pernas e braços em malha orgânica. rad: raios (em metros, já na escala)."""
    P = R.P
    j = {"pelvis": (*P("hips"), rad["pelvis"], rad["pelvis"]*.8), "waist": (*P("spine"), rad["waist"], rad["waist"]*.78),
         "chest": (*P("chest").lerp(P("chest", 1), .4), rad["chest"], rad["chest"]*.72),
         "neck": (*P("neck"), rad["neck"]), "neck2": (*P("neck", 1), rad["neck"]*.9)}
    e = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        j[f"tr{n}"] = (*P("chest", 1).lerp(sh, .5), rad["trap"]); j[f"sh{n}"] = (*sh, rad["sh"])
        j[f"bi{n}"] = (*sh.lerp(el, .45), rad["bi"]); j[f"el{n}"] = (*el, rad["el"])
        j[f"fa{n}"] = (*el.lerp(wr, .3), rad["fa"]); j[f"wr{n}"] = (*wr, rad["wr"])
        e += [("chest", f"tr{n}"), (f"tr{n}", f"sh{n}"), (f"sh{n}", f"bi{n}"), (f"bi{n}", f"el{n}")]
        if not (V["name"] == "tirano" and n == "R"):
            e += [(f"el{n}", f"fa{n}"), (f"fa{n}", f"wr{n}")]
    torso = skin_mesh("tronco", j, e, M["skin"])
    R.bind(torso, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])
    # pernas de bode: coxa grossa, joelho alto, canela fina para trás
    j = {"pelvis": (*P("hips"), rad["pelvis"]*.9)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        if V["name"] == "tirano" and n == "R": continue
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, rad["thigh"]); j[f"th{n}"] = (*h.lerp(k, .5) + Vector((0, -.02*V["s"], 0)), rad["thigh"]*.92)
        j[f"knee{n}"] = (*k, rad["knee"]); j[f"calf{n}"] = (*k.lerp(a, .3) + Vector((0, .05*V["s"], 0)), rad["calf"])
        j[f"ank{n}"] = (*a, rad["ank"]); j[f"toe{n}"] = (*a.lerp(P(f"foot.{n}", 1), .6), rad["ank"]*.9)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"th{n}"), (f"th{n}", f"knee{n}"), (f"knee{n}", f"calf{n}"), (f"calf{n}", f"ank{n}"), (f"ank{n}", f"toe{n}")]
    legs = skin_mesh("pernas", j, e, legs_mat or M["skin"])
    R.bind(legs, ["hips"] + [b for n in ("L", "R") for b in (f"thigh.{n}", f"shin.{n}", f"foot.{n}")
                             if not (V["name"] == "tirano" and n == "R")])
    for n in ("L", "R"):
        if V["name"] == "tirano" and n == "R": continue
        R.rigid(hoof(R, n, M["skin"], M["horn"], V["s"]*1.1), f"foot.{n}")

# ======================================================================= formas
def build():
    s = V["s"]
    R = Rig("familiar_" + V["name"], bones()); P = R.P
    M = mats()
    globals()["_build_" + V["name"]](R, M, s, P)
    return R, info()

def _head_frame(P):
    h0, h1 = P("head"), P("head", 1)
    return h0.lerp(h1, .38)

# ----------------------------------------------------------------------- Diabrete de Fuligem
def _build_diabrete(R, M, s, P):
    rnd = random.Random(7)
    rad = {k: v*s for k, v in dict(pelvis=.15, waist=.13, chest=.17, neck=.07, trap=.08, sh=.075, bi=.06, el=.045,
                                   fa=.05, wr=.035, thigh=.09, knee=.06, calf=.055, ank=.035).items()}
    body(R, M, rad)
    bl = [prim("primitive_uv_sphere_add", M["skin"], P("spine") + Vector((0, -.05*s, -.02*s)), (.13*s, .12*s, .14*s), segments=16, ring_count=10)]
    for k2 in range(3):   # costelas aparecendo em cima da barriga
        for sd in (1, -1):
            q = P("chest") + Vector((.06*sd*s, -.12*s, -.02*s - .035*s*k2))
            bl.append(along("primitive_cylinder_add", M["skin"], q, q + Vector((.07*sd*s, .03*s, -.02*s)), .012*s, vertices=6))
    R.rigid(bl, "spine")
    for n in ("L", "R"): R.rigid(claws(R, n, M["skin"], M["horn"], s*1.45), f"hand.{n}")
    # cabeça grande (1,7x): crânio, focinho, sorriso de dentes, orelhas de morcego, chifrinhos, olhos de brasa
    c = _head_frame(P); hd = []; k = s*1.7
    hd.append(prim("primitive_uv_sphere_add", M["skin"], c, (.12*k, .12*k, .12*k), segments=18, ring_count=12))
    hd.append(prim("primitive_uv_sphere_add", M["skin"], c + Vector((0, -.09, -.05))*k, (.075*k, .06*k, .05*k), segments=14, ring_count=8))
    hd.append(prim("primitive_uv_sphere_add", M["skin"], c + Vector((0, -.06, .055))*k, (.1*k, .05*k, .03*k), segments=12, ring_count=6))  # testa franzida
    hd.append(prim("primitive_uv_sphere_add", M["dark"], c + Vector((0, -.125, -.075))*k, (.07*k, .03*k, .022*k), segments=12, ring_count=6))
    for i in range(9):   # dentinhos tortos no sorriso
        x = (-.055 + .0137*i)
        q = c + Vector((x, -.135 + abs(x)*.6, -.065))*k
        hd.append(along("primitive_cone_add", M["bone"], q, q + Vector((0, -.004, -.024 - .01*(i % 2)))*k, .006*k, vertices=4, radius1=1, radius2=0))
    hd.append(prim("primitive_uv_sphere_add", M["ember"], c + Vector((0, -.12, -.078))*k, (.045*k, .02*k, .008*k), segments=8, ring_count=4))
    for sd in (1, -1):
        e = c + Vector((.045*sd, -.105, .01))*k
        hd.append(prim("primitive_uv_sphere_add", M["dark"], e, (.028*k, .016*k, .02*k), segments=10, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", M["ember"], e + Vector((0, -.008, 0))*k, (.016*k, .01*k, .012*k), segments=8, ring_count=6))
        # orelha de morcego, grande e rasgada
        base = c + Vector((.1*sd, .0, .03))*k
        ear = membrane("orelha", base, [base + Vector((.03*sd, .0, .08))*k, base + Vector((.22*sd, .06, .11))*k,
                                        base + Vector((.16*sd, .05, -.02))*k, base + Vector((.04*sd, .01, -.05))*k],
                       M["wing"], scallop=.18, rows=4, cols=3, thick=.01*k, tears=(1,) if sd > 0 else (), seed=8)
        hd.append(ear)
        hd.append(along("primitive_cone_add", M["skin"], base, base + Vector((.2*sd, .05, .09))*k, .012*k, vertices=6, radius1=1, radius2=.2))
        for kk in range(2):  # brincos de argola de latão
            hd.append(prim("primitive_torus_add", M["brass"], base + Vector((.12*sd, .035, .03 - .025*kk))*k, (1, 1, 1),
                           major_radius=.012*k, minor_radius=.003*k, major_segments=10, minor_segments=4, rot=(0, 90, 0)))
        # chifrinhos curvos para trás
        horn_curve(c + Vector((.05*sd, -.02, .1))*k, (.3*sd, .2, 1), Quaternion(Vector((1, 0, 0)), .3), 5, .022*k, .018*k, M["horn"], hd)
    # óculos de soldador rachados empurrados para a testa
    for sd in (1, -1):
        g = c + Vector((.042*sd, -.085, .085))*k
        hd.append(prim("primitive_cylinder_add", M["brass"], g, (.03*k, .03*k, .02*k), vertices=12, rot=(70, 0, 0)))
        hd.append(prim("primitive_cylinder_add", M["dark"], g + Vector((0, -.012, .004))*k, (.023*k, .023*k, .006*k), vertices=12, rot=(70, 0, 0)))
        hd.append(prim("primitive_torus_add", M["brass"], g + Vector((0, -.014, .005))*k, (1, 1, 1), major_radius=.028*k, minor_radius=.005*k,
                       major_segments=12, minor_segments=4, rot=(70, 0, 0)))
    hd.append(prim("primitive_torus_add", M["dleather"], c + Vector((0, .0, .06))*k, (1, 1.05, .6), major_radius=.112*k, minor_radius=.01*k,
                   major_segments=24, minor_segments=4, rot=(-14, 0, 0)))
    R.rigid(hd, "head")
    # coleira de couro com o lacre de cera do pacto e um elo de corrente partido
    cl = [prim("primitive_torus_add", M["dleather"], P("neck") + Vector((0, -.01, .01)), (1, 1, .8), major_radius=rad["neck"]*1.25,
               minor_radius=.012*s*1.6, major_segments=18, minor_segments=5)]
    wax_seal(P("neck") + Vector((0, -rad["neck"]*1.4, -.02*s)), (0, -1, -.3), .035*s*1.6, M, cl)
    chain(P("neck") + Vector((0, -rad["neck"]*1.3, -.05*s)), P("neck") + Vector((.02, -rad["neck"]*1.5, -.2*s)), 3, .016*s*1.6, M["iron"], cl)
    R.rigid(cl, "chest")
    # avental de couro queimado com bolso, cinto e frascos
    ap = skirt("avental", M["leather"], [(P("chest")[2], rad["chest"]*.9, rad["chest"]*.72, -.005),
                                         (P("hips")[2], rad["pelvis"]*1.08, rad["pelvis"]*.95, 0),
                                         (P("shin")[2] if False else P("thigh.L", 1)[2] + .03*s, rad["pelvis"]*1.25, rad["pelvis"]*1.0, -.02*s)],
               open_front=0, seg=24, jag=.03*s, seed=5, thick=.01*s)
    # só a frente: corta a metade de trás
    ap_bm = bmesh.new(); ap_bm.from_mesh(ap.data)
    bmesh.ops.delete(ap_bm, geom=[f for f in ap_bm.faces if f.calc_center_median().y > rad["pelvis"]*.25], context='FACES')
    ap_bm.to_mesh(ap.data); ap_bm.free()
    R.bind(ap, ["hips", "spine", "chest", "thigh.L", "thigh.R"], power=3)
    bt = [prim("primitive_torus_add", M["dleather"], P("hips") + Vector((0, 0, .03*s)), (1, .85, 1), major_radius=rad["pelvis"]*1.1,
               minor_radius=.014*s*1.6, major_segments=20, minor_segments=4)]
    bt.append(prim("primitive_cube_add", M["brass"], P("hips") + Vector((0, -rad["pelvis"]*.98, .03*s)), (.022*s*1.6, .006*s, .018*s*1.6)))
    for sd, col in ((1, M["ember"]), (-1, M["iron"])):
        q = P("hips") + Vector((.11*sd*s*1.4, -.06*s, -.02*s))
        bt.append(prim("primitive_cylinder_add", M["steel"] if sd < 0 else M["brass"], q, (.018*s*1.6, .018*s*1.6, .035*s*1.6), vertices=10))
        bt.append(prim("primitive_cylinder_add", M["dleather"], q + Vector((0, 0, .04*s*1.6)), (.012*s*1.6, .012*s*1.6, .008*s*1.6), vertices=8))
    for k2 in range(4):   # remendos de chamuscado no avental
        bt.append(prim("primitive_uv_sphere_add", M["dark"], P("hips") + Vector((rnd.uniform(-.08, .08), -rad["pelvis"]*1.12, rnd.uniform(-.1, .02)))*1 ,
                       (.018*s*1.6, .004*s, .014*s*1.6), segments=8, ring_count=4))
    R.rigid(bt, "hips")
    # asas de morcego rasgadas: 3 dedos curvos, membrana com borda em arcos e um rasgo
    for sd, n in ((1, "L"), (-1, "R")):
        a, b = P(f"wing.{n}"), P(f"wing.{n}", 1)
        tips = [a + Vector((.5*sd, .4, .14))*s, a + Vector((.46*sd, .52, -.16))*s, a + Vector((.22*sd, .44, -.36))*s]
        ws = [membrane("asa", b, [b + (b - a)*.25] + tips + [a + Vector((.04*sd, .2, -.24))*s], M["wing"], scallop=.3,
                       thick=.006, tears=(2,), seed=3 + (sd > 0))]
        ws.append(along("primitive_cone_add", M["skin"], a, b, .022*s, vertices=8, radius1=1, radius2=.7))
        ws.append(along("primitive_cone_add", M["skin"], b, b + (b - a)*.25, .016*s, vertices=8, radius1=1, radius2=.6))
        for f in tips:
            mid = b.lerp(f, .5) + Vector((0, 0, .05*s))
            ws.append(along("primitive_cone_add", M["skin"], b, mid, .011*s, vertices=6, radius1=1, radius2=.8))
            ws.append(along("primitive_cone_add", M["skin"], mid, f, .009*s, vertices=6, radius1=1, radius2=.25))
        ws.append(along("primitive_cone_add", M["horn"], b, b + Vector((.03*sd, -.04, .08))*s, .014*s, vertices=6, radius1=1, radius2=0))
        R.rigid(ws, f"wing.{n}")
    tail(R, M, .035*s*1.4, True)
    R.gexclude = {"tail1", "tail2", "tail3", "wing.L", "wing.R"}

# ----------------------------------------------------------------------- Algoz de Enxofre
def _build_algoz(R, M, s, P):
    rnd = random.Random(11)
    rad = {k: v*s for k, v in dict(pelvis=.17, waist=.16, chest=.22, neck=.085, trap=.11, sh=.1, bi=.085, el=.06,
                                   fa=.075, wr=.05, thigh=.105, knee=.07, calf=.07, ank=.04).items()}
    body(R, M, rad)
    # costuras e cicatrizes no peito e barriga
    st = []
    for seed, (x0, z0, x1, z1) in enumerate(((-.12, 1.42, .1, 1.18), (.14, 1.36, .02, 1.08), (-.04, 1.3, -.15, 1.12))):
        a = Vector((x0*s, -rad["chest"]*.74, z0*s)); b = Vector((x1*s, -rad["waist"]*.84, z1*s))
        st.append(along("primitive_cylinder_add", M["dark"], a, b, .006*s, vertices=5))
        for k in range(6):
            q = a.lerp(b, (k + .5)/6); d = (b - a).normalized(); pp = d.cross(Vector((0, 1, 0))).normalized()
            st.append(along("primitive_cylinder_add", M["cloth"], q - pp*.02*s, q + pp*.02*s, .004*s, vertices=4))
    R.rigid(st, "spine")
    for n in ("L", "R"):
        ps = claws(R, n, M["skin"], M["horn"], s*1.15)
        el, wr = P(f"forearm.{n}"), P(f"hand.{n}"); d = (wr - el).normalized()
        br = prim("primitive_cylinder_add", M["leather"], el.lerp(wr, .6), (rad["fa"]*1.15, rad["fa"]*1.15, .09*s), vertices=12)
        br.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); ps2 = [br]
        for k in range(2):
            t = prim("primitive_torus_add", M["iron"], el.lerp(wr, .45 + .3*k), (1, 1, 1.4), major_radius=rad["fa"]*1.18,
                     minor_radius=.01*s, major_segments=14, minor_segments=4)
            t.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); ps2.append(t)
        R.rigid(ps, f"hand.{n}"); R.rigid(ps2, f"forearm.{n}")
    # cabeça: capuz de carrasco de couro com furos dos olhos acesos, chifres serrados atravessando, queixo de bode
    c = _head_frame(P); hd = []
    hd.append(prim("primitive_uv_sphere_add", M["skin"], c + Vector((0, -.04, -.06))*s, (.085*s, .09*s, .07*s), segments=14, ring_count=8))
    for i in range(7):
        x = -.045 + .015*i; q = c + Vector((x, -.12 + abs(x)*.5, -.085))*s
        hd.append(along("primitive_cone_add", M["bone"], q, q + Vector((0, -.004, .03 + .012*(i % 2)))*s, .007*s, vertices=4, radius1=1, radius2=0))
    hd.append(prim("primitive_uv_sphere_add", M["dark"], c + Vector((0, -.115, -.075))*s, (.05*s, .02*s, .015*s), segments=10, ring_count=5))
    hd.append(prim("primitive_uv_sphere_add", M["dleather"], c + Vector((0, 0, .02))*s, (.12*s, .13*s, .14*s), segments=18, ring_count=12))
    hd.append(along("primitive_cone_add", M["dleather"], c + Vector((0, .03, .1))*s, c + Vector((0, .14, .24))*s, .07*s, vertices=10, radius1=1, radius2=.1))
    hd.append(prim("primitive_torus_add", M["leather"], c + Vector((0, 0, .02))*s, (1, 1.08, 1), major_radius=.125*s, minor_radius=.007*s,
                   major_segments=24, minor_segments=4, rot=(0, 90, 0)))
    for sd in (1, -1):
        e = c + Vector((.045*sd, -.122, .035))*s
        hd.append(prim("primitive_uv_sphere_add", M["dark"], e, (.03*s, .012*s, .018*s), segments=10, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", M["ember"], e + Vector((0, -.006, 0))*s, (.014*s, .006*s, .01*s), segments=8, ring_count=5))
        pts = horn_curve(c + Vector((.09*sd, -.02, .1))*s, (.6*sd, .1, .8), Quaternion(Vector((0, 1, 0)), -.1*sd) @ Quaternion(Vector((1, 0, 0)), .12),
                         3, .06*s, .042*s, M["horn"], hd, taper=.35)
        hd.append(prim("primitive_cylinder_add", M["bone"], pts[-1], (.028*s, .028*s, .006*s), vertices=10))   # corte da serra
        hd[-1].rotation_euler = (pts[-1] - pts[-2]).to_track_quat('Z', 'Y').to_euler()
        hd.append(prim("primitive_torus_add", M["iron"], pts[1], (1, 1, 1), major_radius=.04*s, minor_radius=.008*s, major_segments=12, minor_segments=4))
        hd[-1].rotation_euler = (pts[2] - pts[0]).to_track_quat('Z', 'Y').to_euler()
    for k in range(6):  # rebites do capuz
        a = math.radians(-70 + 28*k)
        hd.append(prim("primitive_uv_sphere_add", M["brass"], c + Vector((.12*math.sin(a), -.12*math.cos(a)*.7 + .01, -.04))*s,
                       (.008*s, .008*s, .008*s), segments=6, ring_count=4))
    R.rigid(hd, "head")
    gola = skirt("gola", M["dleather"], [(P("neck", 1)[2] - .02*s, .09*s, .09*s, 0), (P("neck")[2] - .02*s, .2*s, .16*s, .01*s),
                                         (P("chest")[2] + .1*s, .3*s, .2*s, .02*s)], jag=.04*s, seed=9, thick=.012*s)
    R.bind(gola, ["chest", "neck", "head", "upper_arm.L", "upper_arm.R"], power=3)
    # colar de ferro com argola e a corrente do gancho em bandoleira até o quadril
    cl = [prim("primitive_torus_add", M["iron"], P("neck") + Vector((0, 0, .0)), (1, 1, 1.3), major_radius=rad["neck"]*1.35,
               minor_radius=.025*s, major_segments=18, minor_segments=6)]
    for k in range(8):
        a = 2*math.pi*k/8
        q = P("neck") + Vector((math.cos(a)*rad["neck"]*1.4, math.sin(a)*rad["neck"]*1.4, 0))
        cl.append(along("primitive_cone_add", M["iron"], q, q + Vector((math.cos(a), math.sin(a), 0))*.05*s, .012*s, vertices=5, radius1=1, radius2=0))
    ring = P("neck") + Vector((0, -rad["neck"]*1.5, -.03*s))
    cl.append(prim("primitive_torus_add", M["iron"], ring, (1, 1, 1), major_radius=.035*s, minor_radius=.008*s, major_segments=12, minor_segments=4, rot=(90, 0, 0)))
    hip_r = P("hips") + Vector((-.17*s, -.14*s, -.02*s))
    chain(ring, P("chest") + Vector((-.12*s, -rad["chest"]*.8, 0)), 7, .024*s, M["iron"], cl)
    chain(P("chest") + Vector((-.12*s, -rad["chest"]*.8, 0)), hip_r, 8, .024*s, M["iron"], cl)
    wax_seal(P("chest") + Vector((.09*s, -rad["chest"]*.76, .06*s)), (0, -1, 0), .04*s, M, cl)
    R.rigid(cl, "chest")
    # saiote de couro em tiras com fivelas, cinto largo, gancho pendurado
    sk = skirt("saiote", M["leather"], [(P("hips")[2] + .06*s, rad["pelvis"]*1.05, rad["pelvis"]*.88, 0),
                                       (P("hips")[2] - .12*s, rad["pelvis"]*1.35, rad["pelvis"]*1.15, 0),
                                       (P("thigh.L", 1)[2] + .02*s, rad["pelvis"]*1.55, rad["pelvis"]*1.3, -.01*s)],
               seg=30, jag=.05*s, seed=4, thick=.012*s)
    sbm = bmesh.new(); sbm.from_mesh(sk.data)   # abre fendas entre as tiras
    cut = [f for f in sbm.faces if (int((math.atan2(f.calc_center_median().y, f.calc_center_median().x) + math.pi)/(2*math.pi)*30) % 5) == 0
           and f.calc_center_median().z < P("hips")[2] - .05*s]
    bmesh.ops.delete(sbm, geom=cut, context='FACES'); sbm.to_mesh(sk.data); sbm.free()
    R.bind(sk, ["hips", "thigh.L", "thigh.R"], power=3)
    bt = [prim("primitive_torus_add", M["dleather"], P("hips") + Vector((0, 0, .07*s)), (1, .86, 1.6), major_radius=rad["pelvis"]*1.08,
               minor_radius=.025*s, major_segments=24, minor_segments=5)]
    bt.append(prim("primitive_cube_add", M["brass"], P("hips") + Vector((0, -rad["pelvis"]*.94, .07*s)), (.05*s, .012*s, .04*s)))
    bt.append(prim("primitive_cube_add", M["dleather"], P("hips") + Vector((0, -rad["pelvis"]*.97, .07*s)), (.03*s, .013*s, .022*s)))
    for k in range(4):   # crânios de bicho e ganchos no cinto
        a = math.radians(-50 + 100*k/3 + 180)
        q = P("hips") + Vector((math.cos(a)*rad["pelvis"]*1.15, math.sin(a)*rad["pelvis"]*.98, .02*s))
        if k % 2: bt.append(prim("primitive_uv_sphere_add", M["bone"], q + Vector((0, 0, -.06*s)), (.03*s, .035*s, .035*s), segments=8, ring_count=6))
        else: bt.append(along("primitive_cylinder_add", M["steel"], q, q + Vector((0, 0, -.14*s)), .008*s, vertices=6))
    R.rigid(bt, "hips")
    # trapos amarrados nas canelas
    for n in ("L", "R"):
        k, a = P(f"shin.{n}"), P(f"foot.{n}"); d = (a - k).normalized(); rg = []
        for i in range(3):
            t = prim("primitive_torus_add", M["cloth"], k.lerp(a, .3 + .16*i), (1, 1, 1.6), major_radius=rad["calf"]*(1.05 - .12*i),
                     minor_radius=.012*s, major_segments=12, minor_segments=4)
            t.rotation_euler = (d.to_track_quat('Z', 'Y') @ Quaternion((1, 0, 0), .2*(i - 1))).to_euler(); rg.append(t)
        R.rigid(rg, f"shin.{n}")
    # cutelo de açougue enorme (osso "cleaver")
    g0, g1 = P("cleaver"), P("cleaver", 1); d = (g1 - g0).normalized(); fw = Vector((0, -1, 0)); fw = (fw - d*fw.dot(d)).normalized()
    cv = [along("primitive_cylinder_add", M["leather"], g0 - d*.13*s, g0 + d*.08*s, .022*s, vertices=8)]
    cv.append(prim("primitive_uv_sphere_add", M["iron"], g0 - d*.14*s, (.03*s, .03*s, .03*s), segments=8, ring_count=6))
    bl = prim("primitive_cube_add", M["steel"], g0.lerp(g1, .6) + fw*.06*s, (.01*s, .12*s, .32*s))
    bl.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); cv.append(bl)
    cv.append(prim("primitive_cylinder_add", M["dark"], g0.lerp(g1, .28) + fw*.13*s, (.025*s, .025*s, .012*s), vertices=10))  # furo do cutelo
    cv[-1].rotation_euler = d.cross(fw).to_track_quat('Z', 'Y').to_euler()
    for k in range(6):   # dentes lascados no gume
        q = g0.lerp(g1, .3 + .12*k) + fw*.175*s
        cv.append(along("primitive_cone_add", M["steel"], q, q + fw*.02*s, .012*s, vertices=4, radius1=1, radius2=0))
    cv.append(prim("primitive_uv_sphere_add", M["wax"], g0.lerp(g1, .75) + fw*.1*s, (.035*s, .012*s, .05*s), segments=8, ring_count=5))  # sangue seco
    R.rigid(cv, "cleaver")
    tail(R, M, .045*s, True)
    R.gexclude = {"tail1", "tail2", "tail3", "cleaver"}

# ----------------------------------------------------------------------- Tirano da Fornalha
def _build_tirano(R, M, s, P):
    rnd = random.Random(16)
    rad = {k: v*s for k, v in dict(pelvis=.18, waist=.17, chest=.24, neck=.1, trap=.13, sh=.12, bi=.1, el=.075,
                                   fa=.085, wr=.055, thigh=.11, knee=.075, calf=.07, ank=.042).items()}
    body(R, M, rad)
    R.rigid(claws(R, "L", M["skin"], M["horn"], s*1.15), "hand.L")
    # manopla de ferro com cravos no braço esquerdo
    el, wr = P("forearm.L"), P("hand.L"); d = (wr - el).normalized(); mg = []
    g = prim("primitive_cylinder_add", M["iron"], el.lerp(wr, .55), (rad["fa"]*1.25, rad["fa"]*1.25, (wr - el).length*.42), vertices=14)
    g.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); mg.append(g)
    for k in range(6):
        a = 2*math.pi*k/6; v = d.to_track_quat('Z', 'Y') @ Vector((math.cos(a), math.sin(a), 0))
        q = el.lerp(wr, .5) + v*rad["fa"]*1.2
        mg.append(along("primitive_cone_add", M["iron"], q, q + v*.07*s, .016*s, vertices=5, radius1=1, radius2=0))
    for k in range(3):
        t = prim("primitive_torus_add", M["brass"], el.lerp(wr, .2 + .3*k), (1, 1, 1.3), major_radius=rad["fa"]*1.28, minor_radius=.009*s,
                 major_segments=16, minor_segments=4)
        t.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); mg.append(t)
    R.rigid(mg, "forearm.L")
    # canhão de brasa no lugar do antebraço direito
    el, wr = P("forearm.R"), P("hand.R"); d = (wr - el).normalized(); cn = []
    mouth = wr + d*.12*s
    cn.append(prim("primitive_uv_sphere_add", M["iron"], el, (rad["el"]*1.6,)*3, segments=14, ring_count=8))
    body_c = prim("primitive_cylinder_add", M["iron"], el.lerp(mouth, .45), (.085*s, .085*s, (mouth - el).length*.45), vertices=16)
    body_c.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); cn.append(body_c)
    for k in range(4):
        t = prim("primitive_torus_add", M["brass"], el.lerp(mouth, .15 + .23*k), (1, 1, 1.2), major_radius=.088*s, minor_radius=.012*s,
                 major_segments=16, minor_segments=4)
        t.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); cn.append(t)
    bore = prim("primitive_cylinder_add", M["iron"], mouth, (.07*s, .07*s, .035*s), vertices=16)
    bore.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); cn.append(bore)
    cn.append(prim("primitive_cylinder_add", M["ember_low"], mouth + d*.02*s, (.04*s, .04*s, .008*s), vertices=14))
    cn[-1].rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    side = d.cross(Vector((0, 0, 1))).normalized()
    for sd in (1, -1):   # canos de vapor ligando o canhão ao ombro
        a0 = el + side*.07*s*sd + Vector((0, 0, .06*s))
        a1 = el.lerp(mouth, .8) + side*.095*s*sd
        mid = a0.lerp(a1, .5) + side*.05*s*sd + Vector((0, 0, .03*s))
        cn.append(along("primitive_cylinder_add", M["brass"], a0, mid, .015*s, vertices=8))
        cn.append(along("primitive_cylinder_add", M["brass"], mid, a1, .015*s, vertices=8))
    cn.append(prim("primitive_cylinder_add", M["brass"], el.lerp(mouth, .35) + Vector((0, 0, .1*s)), (.03*s, .03*s, .02*s), vertices=12))  # manômetro
    cn.append(prim("primitive_cylinder_add", M["bone"], el.lerp(mouth, .35) + Vector((0, 0, .121*s)), (.022*s, .022*s, .002*s), vertices=12))
    R.rigid(cn, "forearm.R")
    # perna direita de pistão: coxa de ferro, haste, mola, casco de ferro
    h, k, a, t = P("thigh.R"), P("shin.R"), P("foot.R"), P("foot.R", 1)
    th = [prim("primitive_uv_sphere_add", M["iron"], h, (rad["thigh"]*1.1,)*3, segments=14, ring_count=8)]
    c1 = prim("primitive_cylinder_add", M["iron"], h.lerp(k, .5), (rad["thigh"]*.95, rad["thigh"]*.95, (k - h).length*.5), vertices=14)
    c1.rotation_euler = (k - h).normalized().to_track_quat('Z', 'Y').to_euler(); th.append(c1)
    for kk in range(5):
        q = h.lerp(k, .1 + .2*kk) + Vector((0, -rad["thigh"]*.95, 0))
        th.append(prim("primitive_uv_sphere_add", M["brass"], q, (.012*s,)*3, segments=6, ring_count=4))
    th.append(prim("primitive_uv_sphere_add", M["iron"], k, (rad["knee"]*1.25,)*3, segments=12, ring_count=8))
    R.rigid(th, "thigh.R")
    sh = []
    c2 = prim("primitive_cylinder_add", M["iron"], k.lerp(a, .3), (rad["calf"]*.9, rad["calf"]*.9, (a - k).length*.3), vertices=12)
    c2.rotation_euler = (a - k).normalized().to_track_quat('Z', 'Y').to_euler(); sh.append(c2)
    sh.append(along("primitive_cylinder_add", M["steel"], k.lerp(a, .5), a, .025*s, vertices=10))
    for kk in range(7):   # mola
        q = k.lerp(a, .55 + .055*kk)
        t2 = prim("primitive_torus_add", M["iron"], q, (1, 1, 1), major_radius=.04*s, minor_radius=.008*s, major_segments=12, minor_segments=4)
        t2.rotation_euler = (a - k).normalized().to_track_quat('Z', 'Y').to_euler(); sh.append(t2)
    R.rigid(sh, "shin.R")
    R.rigid(hoof(R, "R", M["iron"], M["iron"], s*1.2), "foot.R")
    # peitoral rebitado com a grade da fornalha acesa
    cz = P("chest").lerp(P("chest", 1), .4); ch = []
    plate = prim("primitive_uv_sphere_add", M["iron"], cz + Vector((0, -.03*s, .02*s)), (rad["chest"]*1.08, rad["chest"]*.85, .2*s), segments=20, ring_count=12)
    ch.append(plate)
    fc = cz + Vector((0, -rad["chest"]*.84, -.01*s))
    ch.append(prim("primitive_cylinder_add", M["dark"], fc, (.1*s, .1*s, .03*s), vertices=18, rot=(90, 0, 0)))
    ch.append(prim("primitive_cylinder_add", M["ember_low"], fc + Vector((0, -.006*s, 0)), (.085*s, .085*s, .02*s), vertices=18, rot=(90, 0, 0)))
    ch.append(prim("primitive_torus_add", M["brass"], fc + Vector((0, -.02*s, 0)), (1, 1, 1), major_radius=.1*s, minor_radius=.014*s,
                   major_segments=20, minor_segments=5, rot=(90, 0, 0)))
    for kk in range(5):   # barras da grade
        x = (-.06 + .03*kk)*s; hgt = math.sqrt(max(0, (.09*s)**2 - x*x))
        ch.append(along("primitive_cylinder_add", M["iron"], fc + Vector((x, -.03*s, -hgt)), fc + Vector((x, -.03*s, hgt)), .008*s, vertices=6))
    for kk in range(14):  # rebites em volta do peitoral
        a = 2*math.pi*kk/14
        q = cz + Vector((math.cos(a)*rad["chest"]*.95, -rad["chest"]*.62 - .02*s, math.sin(a)*.15*s + .02*s))
        ch.append(prim("primitive_uv_sphere_add", M["brass"], q, (.012*s,)*3, segments=6, ring_count=4))
    for sd in (1, -1):   # ombreiras de placas sobrepostas com cravos
        c = P(f"upper_arm.{'L' if sd > 0 else 'R'}") + Vector((.02*sd*s, 0, .05*s))
        for kk in range(3):
            pad = prim("primitive_uv_sphere_add", M["iron"], c + Vector((.03*sd*kk, 0, -.06*kk))*s, (.17*s, .15*s, .07*s), segments=16, ring_count=8)
            pad.rotation_euler = (0, math.radians(28*sd + 10*kk*sd), 0); ch.append(pad)
        for kk in range(3):
            q = c + Vector((.05*sd, -.05 + .05*kk, .06))*s
            ch.append(along("primitive_cone_add", M["iron"], q, q + Vector((.06*sd, 0, .2 - .03*kk))*s, .022*s, vertices=6, radius1=1, radius2=0))
    for sd in (1, -1):   # duas chaminés nas costas soltando brasa
        b0 = cz + Vector((.1*sd*s, rad["chest"]*.7, .0)); b1 = b0 + Vector((.04*sd, .1, .5))*s
        ch.append(along("primitive_cylinder_add", M["iron"], b0, b1, .045*s, vertices=12))
        ch.append(prim("primitive_cylinder_add", M["iron"], b1, (.06*s, .06*s, .03*s), vertices=12))
        ch.append(prim("primitive_cylinder_add", M["dark"], b1 + Vector((0, 0, .029*s)), (.045*s, .045*s, .003*s), vertices=12))
        ch.append(prim("primitive_cylinder_add", M["ember_low"], b1 + Vector((0, 0, .02*s)), (.025*s, .025*s, .004*s), vertices=10))
        for kk in range(2):
            ch.append(prim("primitive_torus_add", M["brass"], b0.lerp(b1, .3 + .35*kk), (1, 1, 1), major_radius=.05*s, minor_radius=.008*s,
                           major_segments=12, minor_segments=4))
    # corrente com o lacre de cera atravessando o peito (o juramento ao Cultista)
    chain(P("upper_arm.L") + Vector((0, -.12*s, .02*s)), cz + Vector((-.1*s, -rad["chest"]*.9, -.12*s)), 8, .026*s, M["iron"], ch)
    wax_seal(cz + Vector((.16*s, -rad["chest"]*.88, -.1*s)), (0, -1, 0), .045*s, M, ch)
    R.rigid(ch, "chest")
    # cabeça: crânio de bode, chifres de carneiro, máscara de ferro na mandíbula, olhos de brasa
    c = _head_frame(P); hd = []; k = s*1.1
    hd.append(prim("primitive_uv_sphere_add", M["skin"], c, (.1*k, .11*k, .11*k), segments=16, ring_count=10))
    hd.append(prim("primitive_uv_sphere_add", M["skin"], c + Vector((0, -.07, .045))*k, (.095*k, .05*k, .035*k), segments=12, ring_count=6))
    jaw = prim("primitive_uv_sphere_add", M["iron"], c + Vector((0, -.08, -.06))*k, (.085*k, .075*k, .055*k), segments=14, ring_count=8)
    hd.append(jaw)
    for kk in range(6):   # grade de respiro na máscara
        x = (-.04 + .016*kk)*k
        hd.append(along("primitive_cylinder_add", M["dark"], c + Vector((x/k, -.155, -.04))*k, c + Vector((x/k, -.15, -.085))*k, .005*k, vertices=4))
    for sd in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", M["brass"], c + Vector((.075*sd, -.1, -.05))*k, (.012*k,)*3, segments=6, ring_count=4))
        e = c + Vector((.04*sd, -.1, .015))*k
        hd.append(prim("primitive_uv_sphere_add", M["dark"], e, (.03*k, .015*k, .018*k), segments=10, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", M["ember"], e + Vector((0, -.008, 0))*k, (.018*k, .008*k, .01*k), segments=8, ring_count=5))
        # chifre de carneiro: espiral grossa para trás e para baixo, com anéis
        pts = horn_curve(c + Vector((.08*sd, -.02, .09))*k, (.6*sd, .5, .6),
                         Quaternion(Vector((1, 0, 0)), .5) @ Quaternion(Vector((0, 0, 1)), .12*sd), 10, .055*k, .05*k, M["horn"], hd, taper=.85)
        for kk in range(1, 8, 2):
            t = prim("primitive_torus_add", M["horn"], pts[kk], (1, 1, 1), major_radius=.05*k*(1 - .085*kk), minor_radius=.006*k,
                     major_segments=12, minor_segments=4)
            t.rotation_euler = (pts[kk+1] - pts[kk-1]).to_track_quat('Z', 'Y').to_euler(); hd.append(t)
    for kk in range(3):   # cravos na testa
        q = c + Vector((-.03 + .03*kk, -.06, .1))*k
        hd.append(along("primitive_cone_add", M["horn"], q, q + Vector((0, -.01, .05))*k, .01*k, vertices=5, radius1=1, radius2=0))
    R.rigid(hd, "head")
    gorj = [prim("primitive_torus_add", M["iron"], P("neck") + Vector((0, 0, .02*s)), (1, 1, 1.8), major_radius=rad["neck"]*1.3,
                 minor_radius=.04*s, major_segments=18, minor_segments=6)]
    R.rigid(gorj, "chest")
    # tabardo em farrapos com o selo da Legião Blasfema, cinto de placas e saia de cota
    sk = skirt("cota", M["iron"], [(P("hips")[2] + .05*s, rad["pelvis"]*1.05, rad["pelvis"]*.9, 0),
                                   (P("thigh.L", 1)[2] + .12*s, rad["pelvis"]*1.45, rad["pelvis"]*1.2, 0)],
               seg=30, jag=.03*s, seed=8, thick=.012*s)
    R.bind(sk, ["hips", "thigh.L", "thigh.R"], power=3)
    hz = P("hips")[2]
    tab = skirt("tabardo", M["crimson"], [(hz + .02*s, .12*s, rad["pelvis"]*.9 + .01*s, 0), (hz - .3*s, .13*s, rad["pelvis"]*1.15, -.03*s),
                                      (hz - .6*s, .12*s, rad["pelvis"]*1.25, -.06*s)], open_front=0, seg=16, jag=.05*s, seed=2, thick=.01*s)
    tbm = bmesh.new(); tbm.from_mesh(tab.data)
    bmesh.ops.delete(tbm, geom=[f for f in tbm.faces if f.calc_center_median().y > -rad["pelvis"]*.5], context='FACES')
    tbm.to_mesh(tab.data); tbm.free()
    R.bind(tab, ["hips", "thigh.L", "thigh.R"], power=3)
    bt = [prim("primitive_torus_add", M["dleather"], P("hips") + Vector((0, 0, .06*s)), (1, .86, 2.2), major_radius=rad["pelvis"]*1.1,
               minor_radius=.03*s, major_segments=24, minor_segments=5)]
    em = P("hips") + Vector((0, -rad["pelvis"]*1.0, .06*s))
    bt.append(prim("primitive_cylinder_add", M["brass"], em, (.06*s, .06*s, .015*s), vertices=16, rot=(90, 0, 0)))
    for kk in range(3):   # selo da Legião: tridente quebrado em latão
        x = (-.025 + .025*kk)*s
        bt.append(along("primitive_cone_add", M["iron"], em + Vector((x, -.018*s, -.03*s)), em + Vector((x*1.3, -.018*s, .035*s + .01*s*(kk == 1))),
                        .006*s, vertices=4, radius1=1, radius2=0))
    R.rigid(bt, "hips")
    tail(R, M, .055*s, True)
    R.gexclude = {"tail1", "tail2", "tail3"}

# ======================================================================= animações (prévia: idle; o resto no plano)
POSE = {
 "diabrete": {"spine": {"x": 10}, "chest": {"x": 14}, "neck": {"x": -8}, "head": {"x": -14},
              "thigh.L": {"x": -30, "y": -10}, "thigh.R": {"x": -26, "y": 10}, "shin.L": {"bend": 55}, "shin.R": {"bend": 50},
              "foot.L": {"x": -22}, "foot.R": {"x": -20},
              "upper_arm.L": {"y": 22, "x": -30}, "upper_arm.R": {"y": -22, "x": -36}, "forearm.L": {"bend": -60}, "forearm.R": {"bend": -66},
              "wing.L": {"z": 10}, "wing.R": {"z": -10}},
 "algoz":    {"spine": {"x": 12}, "chest": {"x": 16}, "neck": {"x": -6}, "head": {"x": -14},
              "thigh.L": {"x": -16, "y": -6}, "thigh.R": {"x": -4, "y": 6}, "shin.L": {"bend": 30}, "shin.R": {"bend": 22},
              "foot.L": {"x": -12}, "foot.R": {"x": -12},
              "upper_arm.L": {"y": 26, "x": -10}, "upper_arm.R": {"y": -18, "x": -16}, "forearm.L": {"bend": -30}, "forearm.R": {"bend": -40},
              "hand.R": {"x": -10}},
 "tirano":   {"spine": {"x": 8}, "chest": {"x": 10}, "neck": {"x": -2}, "head": {"x": -10},
              "thigh.L": {"x": -14, "y": -8}, "thigh.R": {"x": 4, "y": 8}, "shin.L": {"bend": 22}, "shin.R": {"bend": 10},
              "foot.L": {"x": -8}, "foot.R": {"x": -12},
              "upper_arm.L": {"y": 28, "x": -6}, "upper_arm.R": {"y": -16, "x": -34, "z": 10}, "forearm.L": {"bend": -26}, "forearm.R": {"bend": -50}},
}
TAIL = {"tail1": {"x": 0}, "tail2": {"x": 0}, "tail3": {"x": 0}}

def anims(R):
    base = POSE[V["name"]]
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; b, c = math.sin(t), math.cos(t)
        p = {"chest": {"x": 2*b}, "head": {"x": -2*b, "z": 5*c}, "upper_arm.L": {"x": 3*b}, "upper_arm.R": {"x": -3*b},
             "tail2": {"z": 10*c}, "tail3": {"z": 16*math.sin(t - 1)}}
        if V["name"] == "diabrete": p.update({"wing.L": {"z": 12*b}, "wing.R": {"z": -12*b}})
        idle.append(merge(base, p))
    return {"idle": idle}
