# Esqueleto e utilitários de quadrúpedes (cães, porcos, bestas de quatro patas).
# Eixos como no resto do pipeline: olha para -Y, X é a esquerda do bicho, Z para cima.
# Ossos: hips (raiz, garupa) -> spine -> chest -> neck -> head -> jaw; tail1..2 na garupa;
#   patas dianteiras (do chest): upper_arm.X (ombro->cotovelo), forearm.X (->pulso), hand.X (pulso->ponta da pata)
#   patas traseiras (do hips): thigh.X (quadril->joelho), shin.X (->jarrete), foot.X (jarrete->ponta da pata)
# Trava no chão: ground_bones = PAWS (só as quatro patas).
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from mrig import *

PAWS = ["hand.L", "hand.R", "foot.L", "foot.R"]
BODY = ["hips", "spine", "chest", "neck", "head"]

def quad_bones(sh=.75, hip=.7, y_sh=-.32, y_hip=.3, w=.1, neck=(-.48, .86), head=(-.74, .8),
               jaw=((-.53, .83), (-.71, .78)), tail=((.5, .6), (.66, .46)), back=.7, wh=None, extra=None):
    """Esqueleto quadrúpede em metros. sh/hip: altura do ombro/quadril (articulação, não o lombo);
    y_sh/y_hip: posição do ombro/quadril no comprimento; w: meia largura das patas da frente (wh: de trás);
    neck: (y,z) da ponta do pescoço; head: (y,z) da ponta do focinho; back: altura da coluna."""
    wh = wh or w
    B = {
        "hips":  ((0, y_hip + .02, back - .02), (0, y_hip*.3, back), None),
        "spine": ((0, y_hip*.3, back), (0, y_sh*.45, back), "hips"),
        "chest": ((0, y_sh*.45, back), (0, y_sh - .02, back - .02), "spine"),
        "neck":  ((0, y_sh - .02, back + .02), (0, neck[0], neck[1]), "chest"),
        "head":  ((0, neck[0], neck[1]), (0, head[0], head[1]), "neck"),
        "jaw":   ((0, *jaw[0]), (0, *jaw[1]), "head"),
        "tail1": ((0, y_hip + .04, back - .04), (0, *tail[0]), "hips"),
        "tail2": ((0, *tail[0]), (0, *tail[1]), "tail1"),
    }
    G = .025
    for s, n in ((1, "L"), (-1, "R")):
        # dianteira: ombro um pouco à frente, cotovelo atrás, pulso sob o ombro, pata para a frente
        el = (w*s, y_sh + .07*sh, sh*.5); wr = (w*s, y_sh + .03*sh, sh*.14)
        B[f"upper_arm.{n}"] = ((w*s*.9, y_sh, sh), el, "chest")
        B[f"forearm.{n}"] = (el, wr, f"upper_arm.{n}")
        B[f"hand.{n}"] = (wr, (w*s, y_sh - .07*sh, G), f"forearm.{n}")
        # traseira: joelho à frente, jarrete atrás, metatarso quase vertical
        kn = (wh*s, y_hip - .2*hip, hip*.56); hk = (wh*s, y_hip + .15*hip, hip*.27)
        B[f"thigh.{n}"] = ((wh*s*.9, y_hip, hip), kn, "hips")
        B[f"shin.{n}"] = (kn, hk, f"thigh.{n}")
        B[f"foot.{n}"] = (hk, (wh*s, y_hip + .02*hip, G), f"shin.{n}")
    B.update(extra or {})
    return B

class QRig(Rig):
    """Rig com escala não uniforme por osso: pose["bloat"] = {osso: (sx, sy, sz)} (eixos locais; y = ao longo do osso).
    Serve para inchar a barriga (osso sem filhos). Aplicar depois de keys_to_frames/merge (não interpola)."""
    def set_pose(self, pose, frame):
        Rig.set_pose(self, pose, frame)
        for b, k in (pose.get("bloat") or {}).items():
            pb = self.arm.pose.bones[b]; pb.scale = k; pb.keyframe_insert("scale", frame=frame)

# ------------------------------------------------------------------ malhas
def join(objs):
    objs = [o for o in objs if o]
    bpy.context.view_layer.update()
    for o in objs:
        o.data.transform(o.matrix_world); o.matrix_world = Matrix()
    if len(objs) > 1:
        with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs,
                                       selected_objects=objs, object=objs[0]):
            bpy.ops.object.join()
    return objs[0]

def _cr(p0, p1, p2, p3, t):
    t2, t3 = t*t, t*t*t
    return .5*((2*p1) + (-p0 + p2)*t + (2*p0 - 5*p1 + 4*p2 - p3)*t2 + (-p0 + 3*p1 - 3*p2 + p3)*t3)

def ring_path(keys, step=.012):
    """keys: [(y, z, rx, rz)] ao longo do corpo (de trás para a frente ou vice-versa).
    Devolve anéis interpolados (Catmull-Rom) [(centro, rx, rz, tangente)] a cada ~step m."""
    K = [(Vector((0, k[0], k[1])), k[2], k[3]) for k in keys]
    out = []
    for i in range(len(K) - 1):
        a, b = K[i], K[i+1]; a0 = K[max(0, i-1)]; b1 = K[min(len(K)-1, i+2)]
        n = max(2, int((b[0] - a[0]).length/step))
        for j in range(n):
            t = j/n
            c = _cr(a0[0], a[0], b[0], b1[0], t)
            rx = _cr(Vector((a0[1], 0, 0)), Vector((a[1], 0, 0)), Vector((b[1], 0, 0)), Vector((b1[1], 0, 0)), t).x
            rz = _cr(Vector((a0[2], 0, 0)), Vector((a[2], 0, 0)), Vector((b[2], 0, 0)), Vector((b1[2], 0, 0)), t).x
            out.append([c, max(.004, rx), max(.004, rz)])
    out.append([K[-1][0], K[-1][1], K[-1][2]])
    for i, r in enumerate(out):
        a = out[max(0, i-1)][0]; b = out[min(len(out)-1, i+1)][0]
        r.append((b - a).normalized())
    return out

def surf(ring, a):
    """Ponto e normal na superfície de um anel, ângulo a (0 = esquerda +X, 90° = topo)."""
    c, rx, rz, t = ring
    X = Vector((1, 0, 0)); U = t.cross(X).normalized()
    if U.z < 0: U = -U
    p = c + X*rx*math.cos(a) + U*rz*math.sin(a)
    n = (X*math.cos(a)/rx + U*math.sin(a)/rz).normalized()
    return p, n

def loft(name, rings, m, seg=28, rad=None, levels=1):
    """Tubo fechado pelos anéis de ring_path. rad(i, a, ring) -> multiplicador do raio (costelas, vértebras)."""
    bm = bmesh.new(); grid = []
    for i, r in enumerate(rings):
        row = []
        for k in range(seg):
            a = 2*math.pi*k/seg
            p, nrm = surf(r, a)
            f = rad(i, a, r) if rad else 1.0
            row.append(bm.verts.new(r[0] + (p - r[0])*f))
        grid.append(row)
    for i in range(len(grid)-1):
        for k in range(seg):
            j = (k+1) % seg
            bm.faces.new((grid[i][k], grid[i][j], grid[i+1][j], grid[i+1][k]))
    for row, rev in ((grid[0], True), (grid[-1], False)):
        c = bm.verts.new(sum((v.co for v in row), Vector())/len(row))
        for k in range(seg):
            j = (k+1) % seg
            f = (row[k], row[j], c) if not rev else (row[j], row[k], c)
            bm.faces.new(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj_from_bm(name, bm, m)
    if levels:
        s = o.modifiers.new("sub", 'SUBSURF'); s.levels = s.render_levels = levels; apply_mods(o)
        for p in o.data.polygons: p.use_smooth = True
    return o

def tufts(rings, m, n, a_rng, i_rng, length, r, seed, back=.6, down=.2, lmin=.5):
    """Tufos de pelo ralo (cones) espetados na superfície, penteados para trás."""
    rr = random.Random(seed); out = []
    for _ in range(n):
        i = rr.randint(int(i_rng[0]*(len(rings)-1)), int(i_rng[1]*(len(rings)-1)))
        a = math.radians(rr.uniform(*a_rng))
        p, nrm = surf(rings[i], a)
        d = (nrm + Vector((0, back, -down)) + Vector((rr.uniform(-.3, .3), rr.uniform(-.2, .2), rr.uniform(-.2, .2)))).normalized()
        L = length*rr.uniform(lmin, 1)
        out.append(along("primitive_cone_add", m, p - nrm*.012, p + d*L, r*rr.uniform(.7, 1.2), vertices=4,
                         radius1=1, radius2=0))
    return out

def limb(name, pts, m, levels=2):
    """Pata em cadeia: pts [(x,y,z,raio)] na ordem."""
    j = {f"p{i}": p for i, p in enumerate(pts)}
    e = [(f"p{i}", f"p{i+1}") for i in range(len(pts)-1)]
    return skin_mesh(name, j, e, m, levels=levels)

# ------------------------------------------------------------------ marcha
def leg_cycle(side, front, p, amp=24, lift=1.0, fold=1.0):
    """Ciclo de uma pata no trote. p 0..1: 0-.5 apoio (varre da frente para trás), .5-1 balanço (dobra e avança)."""
    n = side
    if p < .5:
        u = p/.5; ang = -amp + 2*amp*u; lf = 0
    else:
        u = (p - .5)/.5; s = u*u*(3 - 2*u); ang = amp - 2*amp*s; lf = math.sin(math.pi*u)*lift
    if front:
        return {f"upper_arm.{n}": {"x": ang - 14*lf}, f"forearm.{n}": {"bend": -38*lf*fold},
                f"hand.{n}": {"bend": 95*lf*fold, "x": -.5*ang*(1 - lf)}}
    return {f"thigh.{n}": {"x": ang - 18*lf}, f"shin.{n}": {"bend": 30*lf*fold},
            f"foot.{n}": {"bend": -60*lf*fold, "x": -.4*ang*(1 - lf)}}
