# Base dos personagens do DARK PASSAGE: esqueleto humanoide, corpo orgânico
# (Skin modifier) pesado automaticamente nos ossos, peças rígidas presas a
# ossos, materiais "sujos" e um sistema simples de poses por quadro-chave.
# Eixos: personagem olha para -Y, X é a sua esquerda, Z para cima. Altura ~1,8.
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion, Matrix

# ---------------------------------------------------------------- materiais
def mat(name, rgb, metal=0.0, rough=0.6, emit=None, strength=0.0, dirt=0.55, grime=1.0):
    """Material PBR com sujeira: manchas de ruído e escurecimento para os pés."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
        b.inputs["Base Color"].default_value = (*rgb, 1)
        return m
    tc = nt.nodes.new("ShaderNodeTexCoord")
    noise = nt.nodes.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 9
    noise.inputs["Detail"].default_value = 6
    nt.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = .35; ramp.color_ramp.elements[0].color = (dirt, dirt*.92, dirt*.85, 1)
    ramp.color_ramp.elements[1].position = .62; ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(noise.outputs["Fac"], ramp.inputs[0])
    # gradiente de altura: pés no escuro
    sep = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Object"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = 0.0; mr.inputs["From Max"].default_value = 1.3
    mr.inputs["To Min"].default_value = 1 - .55*grime; mr.inputs["To Max"].default_value = 1.0
    nt.links.new(sep.outputs["Z"], mr.inputs["Value"])
    m1 = nt.nodes.new("ShaderNodeMix"); m1.data_type = 'RGBA'; m1.blend_type = 'MULTIPLY'
    m1.inputs[0].default_value = 1; m1.inputs[6].default_value = (*rgb, 1)
    nt.links.new(ramp.outputs[0], m1.inputs[7])
    m2 = nt.nodes.new("ShaderNodeMix"); m2.data_type = 'RGBA'; m2.blend_type = 'MULTIPLY'
    m2.inputs[0].default_value = 1
    nt.links.new(m1.outputs[2], m2.inputs[6])
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    for k in "XYZ": nt.links.new(mr.outputs[0], comb.inputs[k])
    nt.links.new(comb.outputs[0], m2.inputs[7])
    nt.links.new(m2.outputs[2], b.inputs["Base Color"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .25
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m

# ---------------------------------------------------------------- esqueleto (pose de ligação em "A")
def _a(x, z, side):  # braço em A: 45 graus para baixo
    return (side*x, 0, z)
BONES = {  # nome: (cabeça, cauda, pai)
 "hips":   ((0,0,.92), (0,0,1.04), None),
 "spine":  ((0,0,1.04), (0,0,1.24), "hips"),
 "chest":  ((0,0,1.24), (0,0,1.48), "spine"),
 "neck":   ((0,0,1.48), (0,-.01,1.57), "chest"),
 "head":   ((0,-.01,1.57), (0,-.01,1.82), "neck"),
}
for s, n in ((1, "L"), (-1, "R")):
    BONES.update({
     f"thigh.{n}": ((.1*s,0,.93), (.11*s,-.01,.5), "hips"),
     f"shin.{n}":  ((.11*s,-.01,.5), (.12*s,.02,.09), f"thigh.{n}"),
     f"foot.{n}":  ((.12*s,.02,.09), (.13*s,-.13,.03), f"shin.{n}"),
     f"upper_arm.{n}": ((.19*s,0,1.44), (.40*s,0,1.23), "chest"),
     f"forearm.{n}":   ((.40*s,0,1.23), (.59*s,-.01,1.04), f"upper_arm.{n}"),
     f"hand.{n}":      ((.59*s,-.01,1.04), (.65*s,-.02,.98), f"forearm.{n}"),
     f"wing.{n}":      ((.07*s,.13,1.40), (.30*s,.30,1.62), "chest"),
    })
DEFORM = [b for b in BONES if not b.startswith("wing")]

def P(b, end=0):  # posição de repouso da cabeça (0) ou cauda (1) do osso
    return Vector(BONES[b][end])

def make_armature(name="rig", wings=False, extra=None):
    ad = bpy.data.armatures.new(name); arm = bpy.data.objects.new(name, ad)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    bones = dict(BONES); bones.update(extra or {})
    for n, (h, t, p) in bones.items():
        if n.startswith("wing") and not wings: continue
        e = ad.edit_bones.new(n); e.head, e.tail = h, t; e.roll = 0
    for n, (h, t, p) in bones.items():
        if n in ad.edit_bones and p:
            e = ad.edit_bones[n]; e.parent = ad.edit_bones[p]
            e.use_connect = (Vector(ad.edit_bones[p].tail) - Vector(h)).length < 1e-4
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in arm.pose.bones: pb.rotation_mode = 'QUATERNION'
    return arm

# ---------------------------------------------------------------- malhas
def skin_mesh(name, joints, edges, m, levels=2):
    """joints: {nome: (x,y,z,raio) ou (x,y,z,rx,ry)}. Gera malha orgânica e aplica modificadores."""
    keys = list(joints)
    me = bpy.data.meshes.new(name + "_src")
    me.from_pydata([joints[k][:3] for k in keys], [(keys.index(a), keys.index(b)) for a, b in edges], [])
    o = bpy.data.objects.new(name + "_src", me); bpy.context.scene.collection.objects.link(o)
    o.modifiers.new("skin", 'SKIN')
    sv = me.skin_vertices[0].data
    comp_root = set()
    for i, k in enumerate(keys):
        r = joints[k][3:]; sv[i].radius = (r[0], r[-1])
    # uma raiz por componente conectado
    import collections
    adj = collections.defaultdict(set)
    for a, b in edges: adj[a].add(b); adj[b].add(a)
    seen = set()
    for k in keys:
        if k in seen: continue
        sv[keys.index(k)].use_root = True
        st = [k]
        while st:
            x = st.pop()
            if x in seen: continue
            seen.add(x); st += list(adj[x])
    sub = o.modifiers.new("sub", 'SUBSURF'); sub.levels = sub.render_levels = levels
    dg = bpy.context.evaluated_depsgraph_get()
    new = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
    out = bpy.data.objects.new(name, new); bpy.context.scene.collection.objects.link(out)
    new.materials.append(m)
    for p in new.polygons: p.use_smooth = True
    return out

def obj_from_bm(name, bm, m):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    me.materials.append(m)
    for p in me.polygons: p.use_smooth = True
    return o

def skirt(name, m, rings, open_front=0.0, seg=64, jag=0.0, seed=1, thick=.012, folds=0, famp=0.0):
    """Saia/sobretudo: anéis [(z, rx, ry, yoff)]. open_front: ângulo (rad) da abertura frontal.
    jag: barra rasgada (variação aleatória na altura do último anel)."""
    rnd = random.Random(seed); bm = bmesh.new()
    a0 = -math.pi/2 + open_front; a1 = 3*math.pi/2 - open_front  # frente é -Y
    closed = open_front <= 0
    n = seg if closed else seg + 1
    grid = []
    for ri, (z, rx, ry, yo) in enumerate(rings):
        row = []
        for i in range(n):
            t = i/seg if closed else i/seg
            a = a0 + (a1 - a0)*t if not closed else 2*math.pi*t
            zz = z
            if ri == len(rings)-1 and jag: zz += rnd.uniform(-jag, jag*.4)
            k = ri/max(1, len(rings)-1)  # dobras crescem para a barra
            f = 1 + famp*k*(math.sin(folds*a + seed) + .5*math.sin(2.3*folds*a + 2*seed)) if folds else 1
            row.append(bm.verts.new((rx*f*math.cos(a), yo + ry*f*math.sin(a), zz)))
        grid.append(row)
    for r in range(len(grid)-1):
        for i in range(n if closed else n-1):
            j = (i+1) % n
            bm.faces.new((grid[r][i], grid[r][j], grid[r+1][j], grid[r+1][i]))
    bm.normal_update()
    o = obj_from_bm(name, bm, m)
    if thick:
        s = o.modifiers.new("solid", 'SOLIDIFY'); s.thickness = thick
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); old = o.data
        o.modifiers.clear(); o.data = me; bpy.data.meshes.remove(old)
        for p in me.polygons: p.use_smooth = True
    return o

def prim(op, m, loc, scale=(1,1,1), rot=(0,0,0), smooth=True, **kw):
    getattr(bpy.ops.mesh, op)(location=loc, rotation=[math.radians(r) for r in rot], **kw)
    o = bpy.context.object; o.scale = scale; o.data.materials.append(m)
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    return o

def along(op, m, a, b, r, **kw):
    """Peça cilíndrica/cônica do ponto a ao ponto b."""
    a, b = Vector(a), Vector(b); d = b - a
    getattr(bpy.ops.mesh, op)(location=(a+b)/2, **kw)
    o = bpy.context.object; o.rotation_euler = d.to_track_quat('Z','Y').to_euler()
    o.scale = (r, r, d.length/2); o.data.materials.append(m)
    for p in o.data.polygons: p.use_smooth = True
    return o

# ---------------------------------------------------------------- pesos
def _seg_dist(p, a, b):
    ab = b - a; t = max(0, min(1, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + ab*t)).length

def bind(o, arm, bones, power=5, top=3):
    """Pesa cada vértice nos ossos mais próximos (distância ao segmento) e liga à armadura."""
    bpy.context.view_layer.update()
    o.data.transform(o.matrix_world); o.matrix_world = Matrix(); mw = Matrix()
    segs = [(b, P(b), P(b, 1)) for b in bones]
    groups = {b: o.vertex_groups.new(name=b) for b in bones}
    for v in o.data.vertices:
        p = mw @ v.co
        ds = sorted(((_seg_dist(p, a, c) + 1e-3, b) for b, a, c in segs))[:top]
        ws = [(1/d**power, b) for d, b in ds]; s = sum(w for w, _ in ws)
        for w, b in ws:
            if w/s > .01: groups[b].add([v.index], w/s, 'REPLACE')
    attach(o, arm)

def rigid(objs, arm, bone):
    """Junta peças rígidas num objeto preso 100% a um osso."""
    objs = [o for o in objs if o]
    bpy.context.view_layer.update()
    for o in objs:  # aplica transformações
        o.data.transform(o.matrix_world); o.matrix_world = Matrix()
    if len(objs) > 1:
        with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs,
                                       selected_objects=objs, object=objs[0]):
            bpy.ops.object.join()
    o = objs[0]; o.name = f"{arm.name}_{bone}"
    g = o.vertex_groups.new(name=bone); g.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
    attach(o, arm); return o

def attach(o, arm):
    o.parent = arm
    md = o.modifiers.new("arm", 'ARMATURE'); md.object = arm

# ---------------------------------------------------------------- poses
def _rot(axis, deg): return Quaternion(Vector(axis).normalized(), math.radians(deg))

def hinge_axis(b):
    d = (P(b, 1) - P(b)).normalized(); a = d.cross(Vector((0, 1, 0)))
    return a.normalized() if a.length > 1e-4 else Vector((1, 0, 0))

def q_for(b, spec):
    """spec: dict com x,y,z (graus, eixos da armadura, aplicados Y->X->Z) e/ou bend
    (dobra de dobradiça: positivo leva o osso para trás, +Y)."""
    q = Quaternion()
    if "y" in spec: q = _rot((0,1,0), spec["y"]) @ q
    if "x" in spec: q = _rot((1,0,0), spec["x"]) @ q
    if "z" in spec: q = _rot((0,0,1), spec["z"]) @ q
    if "bend" in spec: q = q @ _rot(hinge_axis(b), spec["bend"])
    return q

# braços relaxados ao lado do corpo (sai da pose em A)
ARMS_DOWN = {"upper_arm.L": {"y": 34}, "upper_arm.R": {"y": -34},
             "forearm.L": {"bend": -12}, "forearm.R": {"bend": -12}}

def set_pose(arm, pose, frame):
    """pose: {osso: spec} ou {"root": (dx,dy,dz)}. Grava quadro-chave."""
    for pb in arm.pose.bones:
        spec = dict(pose.get(pb.name, {}))
        B = pb.bone.matrix_local.to_quaternion()
        q = q_for(pb.name, spec)
        pb.rotation_quaternion = B.inverted() @ q @ B
        pb.keyframe_insert("rotation_quaternion", frame=frame)
        if pb.name == "hips":
            off = Vector(pose.get("root", (0, 0, 0)))
            pb.location = B.inverted() @ off
            pb.keyframe_insert("location", frame=frame)

def merge(*poses):
    out = {}
    for p in poses:
        for k, v in p.items():
            if k == "root": out[k] = v; continue
            d = dict(out.get(k, {}))
            for kk, vv in v.items(): d[kk] = d.get(kk, 0) + vv
            out[k] = d
    return out

def make_action(arm, name, frames):
    """frames: lista de poses; uma pose por quadro de sprite."""
    arm.animation_data_create()
    act = bpy.data.actions.new(name); act.use_fake_user = True
    arm.animation_data.action = act
    for i, p in enumerate(frames): set_pose(arm, p, i + 1)
    for fc in act.fcurves:
        for k in fc.keyframe_points: k.interpolation = 'LINEAR'
    return act
