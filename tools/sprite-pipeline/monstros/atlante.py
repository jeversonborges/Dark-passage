# Utilitários comuns dos monstros de Atlântida (gadiro, filho_da_serpente, vigia_de_oricalco, cinocefalo).
# - XRig: cópia do rig da Larva de Carne (escala por osso "inf/sx/sy/sz", "vis", "lx/ly/lz" em ossos sem pai,
#   pseudo-osso "glow" para materiais emissivos), mais "follow": um osso sem pai que copia a pose de outro osso
#   (ex. a coroa do Gadiro presa à cabeça) e pode se soltar e rolar no chão ("drop").
# - Materiais atlantes: oricalco com azinhavre nas frestas (oclusão) e manchas, bronze, pedra, linho, lápis-lazúli,
#   brilho de câmera (emissivo que não ilumina o resto) e escamas por UV (não "nadam" quando a malha deforma).
# - tube(): corpo de serpente ao longo de um caminho 3D com moldura de transporte paralelo, UV em metros e pesos
#   por comprimento de arco (sem confundir espiras vizinhas).
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion, Matrix
from mrig import *
from base_rig import mat

# ======================================================================= rig
class XRig(Rig):
    """Rig com escala por osso, visibilidade, deslocamento de ossos sem pai, brilho e ossos que seguem outro.
    As poses são calculadas sem ação ligada (a trava no chão e o "follow" medem a pose certa) e só depois
    gravadas como quadros-chave."""
    def __init__(self, *a, **k):
        Rig.__init__(self, *a, **k)
        self.hidden = set(); self.glow = []; self.lamps = []
        self.follow = {}          # osso_sem_pai: osso_guia (copia a pose do guia como se fosse filho dele)
        self._drop = {}

    def _pose(self, pose):
        arm = self.arm
        for pb in arm.pose.bones:
            B = pb.bone.matrix_local.to_quaternion()
            pb.rotation_quaternion = B.inverted() @ self.q_for(pb.name, dict(pose.get(pb.name, {}))) @ B
            pb.scale = (1, 1, 1)
            if not pb.parent and pb.name != self.root: pb.location = (0, 0, 0)
        rb = arm.pose.bones[self.root]; RB = rb.bone.matrix_local.to_quaternion()
        off = Vector(pose.get("root", (0, 0, 0)))
        rb.location = RB.inverted() @ off
        for side, tz in (pose.get("plant") or {}).items():
            self._plant(pose, side, tz)
        for b, v in (pose.get("aim") or {}).items():
            bpy.context.view_layer.update()
            pb = arm.pose.bones[b]; v = Vector(v).normalized()
            cur = (pb.tail - pb.head).normalized()
            M = pb.matrix.copy(); R3 = cur.rotation_difference(v).to_matrix() @ M.to_3x3()
            M2 = R3.to_4x4(); M2.translation = M.translation; pb.matrix = M2
        # ossos sem pai: deslocamento
        for pb in arm.pose.bones:
            if pb.parent or pb.name == self.root or pb.name in self.follow: continue
            sp = pose.get(pb.name, {})
            o2 = Vector((sp.get("lx", 0), sp.get("ly", 0), sp.get("lz", 0)))
            pb.location = pb.bone.matrix_local.to_quaternion().inverted() @ o2
        g = pose.get("ground", self.ground)
        if g is not None:
            bpy.context.view_layer.update()
            gb = pose.get("gb") or (None if pose.get("ground_all") else self.gbones)
            low = min(min(p.head.z, p.tail.z) for p in arm.pose.bones
                      if (gb is None and p.name not in self.gexclude) or (gb is not None and p.name in gb))
            off = off + Vector((0, 0, g - low))
            rb.location = RB.inverted() @ off
        sc = pose.get("scale") or {}
        for pb in arm.pose.bones:
            k = sc.get(pb.name, 1)
            sp = pose.get(pb.name, {})
            base = sp.get("vis", 0 if pb.name in self.hidden else 1)*k
            i = sp.get("inf", 0)
            s = [base*(1 + i + sp.get("sx", 0)), base*(1 + .25*i + sp.get("sy", 0)), base*(1 + i + sp.get("sz", 0))]
            pb.scale = [max(.001, v) for v in s]
        if self.follow:
            bpy.context.view_layer.update()
            for b, guide in self.follow.items():
                pb = arm.pose.bones[b]; pg = arm.pose.bones[guide]
                Mt = pg.matrix @ pg.bone.matrix_local.inverted() @ pb.bone.matrix_local
                dr = (pose.get("drop") or {}).get(b)
                if dr and dr[0] > 0:
                    t, dest, rot = dr
                    if b not in self._drop: self._drop[b] = Mt.copy()
                    M0 = self._drop[b]; t = min(1, t)
                    loc = M0.translation.lerp(Vector(dest), t) + Vector((0, 0, .35*4*t*(1 - t)*(1 - t)))
                    q = M0.to_quaternion().slerp(Quaternion(rot), t)
                    Mt = Matrix.Translation(loc) @ q.to_matrix().to_4x4()
                else:
                    self._drop.pop(b, None)
                sc_ = pb.scale.copy(); pb.matrix = Mt
                bpy.context.view_layer.update(); pb.scale = sc_

    def _key(self, frame):
        for pb in self.arm.pose.bones:
            pb.keyframe_insert("rotation_quaternion", frame=frame); pb.keyframe_insert("scale", frame=frame)
            pb.keyframe_insert("location", frame=frame)

    def set_pose(self, pose, frame):
        self._pose(pose); self._key(frame)

    def action(self, name, frames):
        arm = self.arm; arm.animation_data_create(); arm.animation_data.action = None
        ids = {s.node.id_data for s, _ in self.glow} | {ld for ld, _ in self.lamps}
        for m in ids: m.animation_data_clear()
        self._drop = {}; rec = []
        for p in frames:
            self._pose(p)
            rec.append(({pb.name: (pb.location.copy(), pb.rotation_quaternion.copy(), pb.scale.copy()) for pb in arm.pose.bones},
                        p.get("glow", {}).get("v", 0), p.get("lamp", {}).get("v", 1)))
        act = bpy.data.actions.new(name); act.use_fake_user = True
        arm.animation_data.action = act
        for i, (bones, gv, lv) in enumerate(rec):
            for pb in arm.pose.bones:
                l, q, s = bones[pb.name]; pb.location = l; pb.rotation_quaternion = q; pb.scale = s
            self._key(i + 1)
            for sock, k in self.glow:
                sock.default_value = gv*k; sock.keyframe_insert("default_value", frame=i + 1)
            for ld, en in self.lamps:
                ld.energy = en*max(0, lv); ld.keyframe_insert("energy", frame=i + 1)
        for fc in act.fcurves:
            for k in fc.keyframe_points: k.interpolation = 'CONSTANT'
        for m in ids:
            if m.animation_data and m.animation_data.action:
                for fc in m.animation_data.action.fcurves:
                    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
        return act

# ======================================================================= materiais
def _tc(nt):
    t = [n for n in nt.nodes if n.type == 'TEX_COORD']
    return t[0] if t else nt.nodes.new("ShaderNodeTexCoord")

def _noise_mask(nt, src, sc, lo, hi, det=4, dist=0.0):
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = sc
    nz.inputs["Detail"].default_value = det; nz.inputs["Distortion"].default_value = dist
    nt.links.new(src, nz.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].position = lo; r.color_ramp.elements[0].color = (0, 0, 0, 1)
    r.color_ramp.elements[1].position = hi; r.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(nz.outputs["Fac"], r.inputs[0]); return r.outputs[0]

def _math(nt, op, a, b=None, v=None):
    m = nt.nodes.new("ShaderNodeMath"); m.operation = op
    if isinstance(a, (int, float)): m.inputs[0].default_value = a
    else: nt.links.new(a, m.inputs[0])
    if b is not None:
        if isinstance(b, (int, float)): m.inputs[1].default_value = b
        else: nt.links.new(b, m.inputs[1])
    return m.outputs[0]

def _mixc(nt, fac, a, b):
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MIX'
    nt.links.new(fac, mx.inputs[0])
    if isinstance(a, tuple): mx.inputs[6].default_value = (*a, 1)
    else: nt.links.new(a, mx.inputs[6])
    if isinstance(b, tuple): mx.inputs[7].default_value = (*b, 1)
    else: nt.links.new(b, mx.inputs[7])
    return mx.outputs[2]

def patina(name, rgb, green=(.07, .2, .14), metal=1.0, rough=.36, amount=.6, scale=5, crev=1.0,
           stain=(.05, .035, .025), stain_amt=.5, dirt=.5, grime=.8):
    """Metal antigo: cor base metálica; azinhavre (verde fosco, não metálico) nas frestas (oclusão) e em
    manchas; escorridos escuros. amount: quanto de azinhavre; crev: peso das frestas."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = mat(name, rgb, metal, rough, dirt=dirt, grime=grime)
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]; tc = _tc(nt)
    base = b.inputs["Base Color"].links[0].from_socket
    geo = nt.nodes.new("ShaderNodeNewGeometry")   # frestas: "pointiness" baixo = côncavo (barato, sem raios de AO)
    cav = _math(nt, 'MINIMUM', _math(nt, 'MAXIMUM', _math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', .5, geo.outputs["Pointiness"]), 6.0), 0.0), 1.0)
    blot = _noise_mask(nt, tc.outputs["Object"], scale, .5, .68, 6, 1.2)
    fine = _noise_mask(nt, tc.outputs["Object"], scale*5, .45, .7, 3, .3)
    g = _math(nt, 'ADD', _math(nt, 'MULTIPLY', cav, 2.2*crev), _math(nt, 'MULTIPLY', blot, amount))
    g = _math(nt, 'MULTIPLY', g, _math(nt, 'ADD', .55, _math(nt, 'MULTIPLY', fine, .6)))
    g = _math(nt, 'MINIMUM', g, 1.0)
    st = _noise_mask(nt, tc.outputs["Object"], scale*.7, .55, .7, 5, 2.0)
    col = _mixc(nt, _math(nt, 'MULTIPLY', st, stain_amt), base, stain)
    gcol = nt.nodes.new("ShaderNodeMix"); gcol.data_type = 'RGBA'; gcol.blend_type = 'MULTIPLY'
    gcol.inputs[0].default_value = 1; gcol.inputs[6].default_value = (*green, 1)
    nt.links.new(fine, gcol.inputs[7])
    gmix = _mixc(nt, g, col, (green[0]*1.3, green[1]*1.3, green[2]*1.3))
    nt.links.new(gmix, b.inputs["Base Color"])
    nt.links.new(_math(nt, 'MULTIPLY', _math(nt, 'SUBTRACT', 1.0, g), metal), b.inputs["Metallic"])
    nt.links.new(_math(nt, 'ADD', rough, _math(nt, 'MULTIPLY', g, .9 - rough)), b.inputs["Roughness"])
    return m

def glow(name, rgb, strength):
    """Emissivo só para a câmera (não ilumina o resto da cena)."""
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

def scales(name, top, belly=None, edge=.35, cell=.045, rough=.32, coat=.5, blotch=None, blotch_amt=.6,
           scute=.06, uv="UVMap", ang="ang", grime=.7, var=.25):
    """Escamas por UV (u, v em metros: cell = tamanho da escama). belly: cor do ventre (usa o UV 'ang', x em
    0..1 com o ventre em 0/1 e o dorso em .5) com escudos transversais a cada 'scute' m. Brilho molhado (coat)."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat; b.inputs["Coat Roughness"].default_value = .18
    uvn = nt.nodes.new("ShaderNodeUVMap"); uvn.uv_map = uv
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1/cell, 1/cell*1.15, 1)
    nt.links.new(uvn.outputs[0], mp.inputs[0])
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.voronoi_dimensions = '2D'; vo.feature = 'DISTANCE_TO_EDGE'
    nt.links.new(mp.outputs[0], vo.inputs["Vector"])
    v1 = nt.nodes.new("ShaderNodeTexVoronoi"); v1.voronoi_dimensions = '2D'
    nt.links.new(mp.outputs[0], v1.inputs["Vector"])
    er = nt.nodes.new("ShaderNodeValToRGB"); cr = er.color_ramp
    cr.elements[0].position = 0; cr.elements[0].color = (edge, edge, edge, 1)
    cr.elements[1].position = .14; cr.elements[1].color = (1, 1, 1, 1)
    nt.links.new(vo.outputs["Distance"], er.inputs[0])
    # variação por escama
    sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(v1.outputs["Color"], sep.inputs[0])
    vv = _math(nt, 'ADD', 1 - var/2, _math(nt, 'MULTIPLY', sep.outputs[0], var))
    tc = _tc(nt)
    col = (*top,)
    topc = top
    if blotch:  # manchas grandes (losangos escuros no dorso)
        bm_ = _noise_mask(nt, uvn.outputs[0], 3.0, .5, .6, 2, .5)
        topc = _mixc(nt, _math(nt, 'MULTIPLY', bm_, blotch_amt), top, blotch)
    c = topc
    if belly:
        ua = nt.nodes.new("ShaderNodeUVMap"); ua.uv_map = ang
        sa = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(ua.outputs[0], sa.inputs[0])
        d = _math(nt, 'ABSOLUTE', _math(nt, 'SUBTRACT', sa.outputs[0], .5))
        bm = nt.nodes.new("ShaderNodeMapRange"); bm.inputs["From Min"].default_value = .27; bm.inputs["From Max"].default_value = .33
        nt.links.new(d, bm.inputs["Value"])
        su = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(uvn.outputs[0], su.inputs[0])
        fr = _math(nt, 'FRACT', _math(nt, 'DIVIDE', su.outputs[0], scute))
        sr = nt.nodes.new("ShaderNodeValToRGB"); c2 = sr.color_ramp
        c2.elements[0].position = 0; c2.elements[0].color = (.35, .35, .35, 1)
        c2.elements[1].position = .12; c2.elements[1].color = (1, 1, 1, 1)
        nt.links.new(fr, sr.inputs[0])
        bel = nt.nodes.new("ShaderNodeMix"); bel.data_type = 'RGBA'; bel.blend_type = 'MULTIPLY'; bel.inputs[0].default_value = 1
        bel.inputs[6].default_value = (*belly, 1); nt.links.new(sr.outputs[0], bel.inputs[7])
        tmul = nt.nodes.new("ShaderNodeMix"); tmul.data_type = 'RGBA'; tmul.blend_type = 'MULTIPLY'; tmul.inputs[0].default_value = 1
        if isinstance(topc, tuple): tmul.inputs[6].default_value = (*topc, 1)
        else: nt.links.new(topc, tmul.inputs[6])
        nt.links.new(er.outputs[0], tmul.inputs[7])
        c = _mixc(nt, bm.outputs[0], tmul.outputs[2], bel.outputs[2])
        edgef = None
    else:
        tmul = nt.nodes.new("ShaderNodeMix"); tmul.data_type = 'RGBA'; tmul.blend_type = 'MULTIPLY'; tmul.inputs[0].default_value = 1
        if isinstance(topc, tuple): tmul.inputs[6].default_value = (*topc, 1)
        else: nt.links.new(topc, tmul.inputs[6])
        nt.links.new(er.outputs[0], tmul.inputs[7]); c = tmul.outputs[2]
    vm = nt.nodes.new("ShaderNodeMix"); vm.data_type = 'RGBA'; vm.blend_type = 'MULTIPLY'; vm.inputs[0].default_value = 1
    nt.links.new(c, vm.inputs[6]); cv = nt.nodes.new("ShaderNodeCombineXYZ")
    for k in "XYZ": nt.links.new(vv, cv.inputs[k])
    nt.links.new(cv.outputs[0], vm.inputs[7]); c = vm.outputs[2]
    # sujeira de terra perto do chão e manchas de lodo
    sz = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sz.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0; mr.inputs["From Max"].default_value = .45
    mr.inputs["To Min"].default_value = 1 - .5*grime; mr.inputs["To Max"].default_value = 1
    nt.links.new(sz.outputs["Z"], mr.inputs["Value"])
    gm = nt.nodes.new("ShaderNodeMix"); gm.data_type = 'RGBA'; gm.blend_type = 'MULTIPLY'; gm.inputs[0].default_value = 1
    nt.links.new(c, gm.inputs[6]); cg = nt.nodes.new("ShaderNodeCombineXYZ")
    for k in "XYZ": nt.links.new(mr.outputs[0], cg.inputs[k])
    nt.links.new(cg.outputs[0], gm.inputs[7])
    mud = _noise_mask(nt, tc.outputs["Object"], 4, .58, .7, 4, 1.0)
    c = _mixc(nt, _math(nt, 'MULTIPLY', mud, .55), gm.outputs[2], (.075, .06, .04))
    nt.links.new(c, b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .55; bump.inputs["Distance"].default_value = .01
    nt.links.new(vo.outputs["Distance"], bump.inputs["Height"]); nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m

def add_uv(o, name="UVMap", sc=1.0):
    """Garante um UV simples (projeção cúbica em metros) em objetos de primitivas, para materiais de escamas."""
    me = o.data
    if name not in me.uv_layers: me.uv_layers.new(name=name)
    uvl = me.uv_layers[name].data
    for p in me.polygons:
        n = p.normal; ax = max(range(3), key=lambda i: abs(n[i]))
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            u, v = [co[i] for i in range(3) if i != ax]
            uvl[li].uv = (u*sc, v*sc)
    return o

# ======================================================================= malhas
def catmull(pts, step=.03):
    """Amostra uma polilinha suave (Catmull-Rom) a cada ~step."""
    P = [Vector(p) for p in pts]; out = []
    def cr(p0, p1, p2, p3, t):
        t2, t3 = t*t, t*t*t
        return .5*((2*p1) + (-p0 + p2)*t + (2*p0 - 5*p1 + 4*p2 - p3)*t2 + (-p0 + 3*p1 - 3*p2 + p3)*t3)
    for i in range(len(P) - 1):
        a0, a, b, b1 = P[max(0, i-1)], P[i], P[i+1], P[min(len(P)-1, i+2)]
        n = max(2, int((b - a).length/step))
        for j in range(n): out.append(cr(a0, a, b, b1, j/n))
    out.append(P[-1])
    return out

def arclen(pts):
    s = [0.0]
    for a, b in zip(pts, pts[1:]): s.append(s[-1] + (b - a).length)
    return s

def frames(pts, n0):
    """Moldura de transporte paralelo: [(T, N, B)] começando com N perpendicular a T na direção de n0."""
    out = []; T0 = (pts[1] - pts[0]).normalized(); N = (Vector(n0) - T0*Vector(n0).dot(T0)).normalized()
    for i in range(len(pts)):
        T = (pts[min(i+1, len(pts)-1)] - pts[max(i-1, 0)]).normalized()
        if out:
            Tp = out[-1][0]; q = Tp.rotation_difference(T); N = (q @ N)
            N = (N - T*N.dot(T)).normalized()
        out.append((T, N, T.cross(N).normalized()))
    return out

def tube(name, pts, radii, m, n0=(0, 1, 0), seg=28, belly_flat=.78, rad=None, cap0=True, cap1=True):
    """Tubo ao longo de pts (já densos) com raio radii[i] (escalar ou (rx, rz)). Ângulo a = 90° no dorso (N),
    270° no ventre. UV 'UVMap' = (s, a*r) em metros e 'ang' = (a/360 a partir do ventre, s).
    rad(i, a) -> multiplicador. Devolve (objeto, s por amostra)."""
    F = frames(pts, n0); S = arclen(pts)
    bm = bmesh.new(); uvl = bm.loops.layers.uv.new("UVMap"); ual = bm.loops.layers.uv.new("ang")
    grid = []
    for i, (c, (T, N, B)) in enumerate(zip(pts, F)):
        r = radii[i]; rx, rz = (r, r) if not isinstance(r, (tuple, list)) else r
        row = []
        for k in range(seg):
            a = -math.pi/2 + 2*math.pi*k/seg
            f = rad(i, a) if rad else 1.0
            zz = math.sin(a)*(belly_flat if math.sin(a) < 0 else 1)
            row.append(bm.verts.new(c + (B*math.cos(a)*rx + N*zz*rz)*f))
        grid.append(row)
    bm.verts.ensure_lookup_table()
    for i in range(len(grid) - 1):
        r = radii[i]; r = r if not isinstance(r, (tuple, list)) else (r[0] + r[1])/2
        r2 = radii[i+1]; r2 = r2 if not isinstance(r2, (tuple, list)) else (r2[0] + r2[1])/2
        for k in range(seg):
            k2 = k + 1; j = k2 % seg
            f = bm.faces.new((grid[i][k], grid[i][j], grid[i+1][j], grid[i+1][k]))
            for lp, (ii, kk, rr) in zip(f.loops, ((i, k, r), (i, k2, r), (i+1, k2, r2), (i+1, k, r2))):
                a = 2*math.pi*kk/seg
                lp[uvl].uv = (S[ii], a*rr); lp[ual].uv = (kk/seg, S[ii])
    for row, rev, cap in ((grid[0], True, cap0), (grid[-1], False, cap1)):
        if not cap: continue
        c = bm.verts.new(sum((v.co for v in row), Vector())/len(row))
        for k in range(seg):
            j = (k+1) % seg
            bm.faces.new((row[k], row[j], c) if not rev else (row[j], row[k], c))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = obj_from_bm(name, bm, m)
    return o, S

def bind_path(R, o, pts, S, segs, extra=None):
    """Pesos por comprimento de arco: cada vértice pega o s da amostra de eixo mais próxima e mistura os ossos
    vizinhos (função tenda). segs: [(osso, s0, s1)] em ordem. extra(v, s) -> {osso: peso} opcional."""
    bpy.context.view_layer.update()
    o.data.transform(o.matrix_world); o.matrix_world = Matrix()
    from mathutils.kdtree import KDTree
    kd = KDTree(len(pts))
    for i, p in enumerate(pts): kd.insert(p, i)
    kd.balance()
    groups = {}
    for b, _, _ in segs: groups[b] = o.vertex_groups.new(name=b)
    for v in o.data.vertices:
        # entre as 4 amostras mais próximas, a de menor distância (resolve espiras vizinhas)
        _, i, _ = kd.find(v.co); s = S[i]
        ws = {}
        for b, s0, s1 in segs:
            c = (s0 + s1)/2; L = max(1e-4, (s1 - s0))
            w = max(0.0, 1 - abs(s - c)/L)
            if s <= segs[0][2] and b == segs[0][0]: w = max(w, 1.0 if s <= c else w)
            if s >= segs[-1][1] and b == segs[-1][0]: w = max(w, 1.0 if s >= c else w)
            if w > 0: ws[b] = w
        if extra:
            for b, w in extra(v.co, s).items():
                if b not in groups: groups[b] = o.vertex_groups.new(name=b)
                ws[b] = ws.get(b, 0) + w
        t = sum(ws.values()) or 1
        for b, w in ws.items(): groups[b].add([v.index], w/t, 'REPLACE')
    R._attach(o); return o

def rock(m, c, size, seed, sub=1, flat=True):
    rr = random.Random(seed)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=1, location=(0, 0, 0))
    o = bpy.context.object; me = o.data
    for v in me.vertices: v.co = v.co*(1 + rr.uniform(-.22, .18))
    o.scale = size if isinstance(size, (tuple, list)) else (size,)*3
    o.rotation_euler = (rr.uniform(0, 6.3), rr.uniform(0, 6.3), rr.uniform(0, 6.3)); o.location = c
    me.materials.append(m)
    for p in me.polygons: p.use_smooth = not flat
    return o

def panel(name, m, z0, z1, w0, w1, y, curve, rows=7, cols=7, jag=0, seed=1, holes=0.0, thick=.01):
    """Pano pendurado na frente (y<0) ou atrás (y>0); barra rasgada (jag) e furos."""
    rnd = random.Random(seed); bm = bmesh.new(); g = []
    for r in range(rows):
        tt = r/(rows-1); z = z0 + (z1 - z0)*tt; w = w0 + (w1 - w0)*tt; row = []
        for c in range(cols):
            u = c/(cols-1)*2 - 1
            zz = z + (rnd.uniform(-jag, jag*.3) if r == rows-1 else 0)
            row.append(bm.verts.new((u*w, y + curve*u*u*(1 if y < 0 else -1), zz)))
        g.append(row)
    for r in range(rows-1):
        for c in range(cols-1):
            if holes and 0 < r < rows-2 and rnd.random() < holes: continue
            bm.faces.new((g[r][c], g[r][c+1], g[r+1][c+1], g[r+1][c]))
    bm.verts.ensure_lookup_table()
    for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
    o = obj_from_bm(name, bm, m); o.modifiers.new("s", 'SOLIDIFY').thickness = thick; apply_mods(o)
    return o

def strip(m, a, b, w, t=.008, twist=0.0):
    """Tira chata (couro, linho) de a até b com largura w."""
    a, b = Vector(a), Vector(b); d = b - a
    o = prim("primitive_cube_add", m, (a + b)/2, (1, 1, 1), smooth=False)
    q = d.to_track_quat('Z', 'Y') @ Quaternion((0, 0, 1), twist)
    o.rotation_euler = q.to_euler(); o.scale = (w/2, t/2, d.length/2)
    return o

def chain_links(m, pts, r=.022, thick=.007):
    out = []; pts = [Vector(p) for p in pts]
    L = sum((b - a).length for a, b in zip(pts, pts[1:])); n = max(2, int(L/(r*1.55)))
    seg = [(a, b, (b - a).length) for a, b in zip(pts, pts[1:])]
    for k in range(n):
        d = L*k/(n - 1) if n > 1 else 0
        for a, b, l in seg:
            if d <= l + 1e-6:
                p = a.lerp(b, d/max(l, 1e-6)); dv = (b - a).normalized(); break
            d -= l
        o = prim("primitive_torus_add", m, p, (1, 1, 1.55), major_radius=r, minor_radius=thick, major_segments=8, minor_segments=4)
        q = dv.to_track_quat('Z', 'Y') @ Quaternion((0, 0, 1), math.pi/2*(k % 2))
        o.rotation_euler = q.to_euler(); out.append(o)
    return out

def orient(o, d, up=None):
    """Gira o objeto para o eixo Z local apontar em d."""
    o.rotation_euler = Vector(d).to_track_quat('Z', 'Y').to_euler(); return o

def glyph(m, c, nrm, size=.03, kind=0, depth=.004):
    """Glifo hermético pequeno (linhas em relevo) numa superfície de normal nrm: círculo com traço,
    caduceu simplificado, triângulo com ponto. Devolve a lista de peças."""
    nrm = Vector(nrm).normalized(); q = nrm.to_track_quat('Z', 'Y'); c = Vector(c)
    X = q @ Vector((1, 0, 0)); Y = q @ Vector((0, 1, 0)); out = []
    def seg(p0, p1, r=size*.13):
        out.append(along("primitive_cylinder_add", m, c + X*p0[0]*size + Y*p0[1]*size + nrm*depth,
                         c + X*p1[0]*size + Y*p1[1]*size + nrm*depth, r, vertices=4))
    if kind == 0:
        t = prim("primitive_torus_add", m, c + nrm*depth, (1, 1, 1), major_radius=size*.7, minor_radius=size*.12,
                 major_segments=12, minor_segments=3); t.rotation_euler = q.to_euler(); out.append(t)
        seg((0, -1.1), (0, 1.1)); seg((-.5, .5), (.5, .5))
    elif kind == 1:
        seg((0, -1), (0, 1)); seg((-.6, .6), (.6, -.2)); seg((.6, .6), (-.6, -.2)); seg((-.6, -.2), (.6, -.8))
    else:
        seg((-.9, -.7), (.9, -.7)); seg((.9, -.7), (0, .9)); seg((0, .9), (-.9, -.7))
        out.append(prim("primitive_uv_sphere_add", m, c + nrm*depth, (size*.2,)*3, segments=6, ring_count=4))
    return out

def common_mats(prefix="at"):
    """Paleta atlante (11 mil anos de pó, sol de fim de tarde)."""
    M = {}
    M["ori"] = patina(f"{prefix}_oricalco", (.6, .3, .14), green=(.06, .2, .14), rough=.46, amount=.55, scale=4.5)
    M["ori2"] = patina(f"{prefix}_oricalco_gasto", (.5, .26, .13), green=(.07, .22, .15), rough=.45, amount=.85, scale=3.5, crev=1.3)
    M["bronze"] = patina(f"{prefix}_bronze", (.36, .22, .1), green=(.07, .19, .13), rough=.42, amount=.6, scale=5)
    M["tin"] = patina(f"{prefix}_estanho", (.42, .41, .38), green=(.16, .17, .15), rough=.4, amount=.35, scale=6)
    M["lapis"] = stained(f"{prefix}_lapis", (.035, .06, .2), stain=(.3, .26, .14), amount=.25, scale=14, rough=.3,
                         blotch=(.06, .1, .3), blotch_amt=.6, grime=.3, dirt=.6)
    M["linen"] = stained(f"{prefix}_linho", (.45, .4, .3), stain=(.16, .1, .05), amount=.6, scale=3, rough=.95,
                         blotch=(.25, .21, .14), blotch_amt=.7, grime=1.3, dirt=.45)
    M["stone_w"] = stained(f"{prefix}_pedra_branca", (.52, .49, .42), stain=(.16, .14, .1), amount=.4, scale=4, rough=.8,
                           blotch=(.32, .3, .25), blotch_amt=.6, grime=.9)
    M["stone_r"] = stained(f"{prefix}_pedra_vermelha", (.3, .1, .07), stain=(.1, .05, .03), amount=.4, scale=5, rough=.75,
                           blotch=(.2, .08, .06), blotch_amt=.5, grime=.8)
    M["stone_b"] = stained(f"{prefix}_pedra_preta", (.04, .04, .04), stain=(.12, .1, .08), amount=.3, scale=5, rough=.6, grime=.5)
    M["leather"] = stained(f"{prefix}_couro", (.12, .07, .04), stain=(.05, .03, .02), amount=.4, scale=4, rough=.65, grime=.7)
    M["hole"] = mat(f"{prefix}_buraco", (.006, .006, .005), 0, .95)
    return M
