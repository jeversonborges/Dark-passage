# Rig genérico para monstros: esqueleto definido por dicionário (humanoide
# escalável ou criaturas com ossos extras), pesos automáticos, peças rígidas,
# poses por quadro e trava no chão (os pés ou o corpo tocam o solo).
# Eixos: o monstro olha para -Y, X é a sua esquerda, Z para cima.
import bpy, math
from mathutils import Vector, Quaternion, Matrix
from base_rig import mat, skin_mesh, obj_from_bm, skirt, prim, along, BONES as _HB

_G = [0.03]
OVERRIDE = {"plant", "gb", "ground_all", "aim", "scale"}

def humanoid(s=1.0, w=1.0, extra=None):
    """Esqueleto humanoide do jogo (1,8 m) escalado: s na altura, w a mais na largura."""
    B = {}
    for n, (h, t, p) in _HB.items():
        if n.startswith("wing"): continue
        f = lambda v: (v[0]*s*w, v[1]*s, v[2]*s)
        B[n] = (f(h), f(t), p)
    B.update(extra or {})
    return B

class Rig:
    def __init__(self, name, bones, ground=0.03, ground_bones=None):
        self.B = bones; self.ground = ground; _G[0] = ground; self.gbones = ground_bones; self.gexclude = set()
        ad = bpy.data.armatures.new(name); arm = bpy.data.objects.new(name, ad)
        bpy.context.scene.collection.objects.link(arm)
        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='EDIT')
        for n, (h, t, p) in bones.items():
            e = ad.edit_bones.new(n); e.head, e.tail = h, t; e.roll = 0
        for n, (h, t, p) in bones.items():
            if p:
                e = ad.edit_bones[n]; e.parent = ad.edit_bones[p]
                e.use_connect = (Vector(ad.edit_bones[p].tail) - Vector(h)).length < 1e-4
        bpy.ops.object.mode_set(mode='OBJECT')
        for pb in arm.pose.bones: pb.rotation_mode = 'QUATERNION'
        self.arm = arm; self.root = [n for n, b in bones.items() if not b[2]][0]

    def P(self, b, end=0): return Vector(self.B[b][end])

    def frame(self, b, up=Vector((0, -1, 0))):
        """Referencial do osso na pose de ligação: (origem, eixo, cima, lado)."""
        o = self.P(b); ax = (self.P(b, 1) - o).normalized()
        u = (up - ax*up.dot(ax)).normalized(); s = ax.cross(u)
        return o, ax, u, s

    # ------------------------------------------------------------ pesos
    def bind(self, o, bones, power=5, top=3):
        bpy.context.view_layer.update()
        o.data.transform(o.matrix_world); o.matrix_world = Matrix()
        segs = [(b, self.P(b), self.P(b, 1)) for b in bones]
        groups = {b: o.vertex_groups.new(name=b) for b in bones}
        for v in o.data.vertices:
            p = v.co
            ds = sorted(((_seg_dist(p, a, c) + 1e-3, b) for b, a, c in segs))[:top]
            ws = [(1/d**power, b) for d, b in ds]; s = sum(w for w, _ in ws)
            for w, b in ws:
                if w/s > .01: groups[b].add([v.index], w/s, 'REPLACE')
        self._attach(o); return o

    def rigid(self, objs, bone):
        objs = [o for o in objs if o]
        bpy.context.view_layer.update()
        for o in objs:
            o.data.transform(o.matrix_world); o.matrix_world = Matrix()
        if len(objs) > 1:
            with bpy.context.temp_override(active_object=objs[0], selected_editable_objects=objs,
                                           selected_objects=objs, object=objs[0]):
                bpy.ops.object.join()
        o = objs[0]; o.name = f"{self.arm.name}_{bone}"
        g = o.vertex_groups.new(name=bone); g.add(list(range(len(o.data.vertices))), 1.0, 'REPLACE')
        self._attach(o); return o

    def _attach(self, o):
        o.parent = self.arm
        md = o.modifiers.new("arm", 'ARMATURE'); md.object = self.arm

    # ------------------------------------------------------------ poses
    def hinge_axis(self, b):
        d = (self.P(b, 1) - self.P(b)).normalized(); a = d.cross(Vector((0, 1, 0)))
        return a.normalized() if a.length > 1e-4 else Vector((1, 0, 0))

    def q_for(self, b, spec):
        """spec: x,y,z em graus (eixos do monstro, ordem Y->X->Z); bend = dobradiça (+ leva o osso para trás).
        x positivo inclina o topo do osso para a frente (-Y)."""
        q = Quaternion()
        if "y" in spec: q = _rot((0,1,0), spec["y"]) @ q
        if "x" in spec: q = _rot((1,0,0), spec["x"]) @ q
        if "z" in spec: q = _rot((0,0,1), spec["z"]) @ q
        if "bend" in spec: q = q @ _rot(self.hinge_axis(b), spec["bend"])
        return q

    def set_pose(self, pose, frame):
        """pose: {osso: spec}, "root": (dx,dy,dz), "ground": altura mínima do esqueleto (None = sem trava)."""
        arm = self.arm
        for pb in arm.pose.bones:
            B = pb.bone.matrix_local.to_quaternion()
            pb.rotation_quaternion = B.inverted() @ self.q_for(pb.name, dict(pose.get(pb.name, {}))) @ B
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
            k = sc.get(pb.name, 1); pb.scale = (k, k, k)  # "scale": {osso: 0.001} esconde uma peça (ex. gancho lançado)
            pb.keyframe_insert("scale", frame=frame)
            pb.keyframe_insert("rotation_quaternion", frame=frame)
            if pb.name == self.root: pb.keyframe_insert("location", frame=frame)

    def _plant(self, pose, side, tz):
        """Gira o braço (osso upper_arm, eixo X) até a mão tocar a altura tz (relativa ao chão travado)."""
        arm = self.arm; ub = f"upper_arm.{side}"; pb = arm.pose.bones[ub]
        B = pb.bone.matrix_local.to_quaternion(); spec = dict(pose.get(ub, {}))
        gb = pose.get("gb") or self.gbones
        def z(d):
            sp = dict(spec); sp["x"] = sp.get("x", 0) + d
            pb.rotation_quaternion = B.inverted() @ self.q_for(ub, sp) @ B
            bpy.context.view_layer.update()
            ps = arm.pose.bones; hb = ps[f"hand.{side}"]
            low = min(min(p.head.z, p.tail.z) for p in ps if gb is None or p.name in gb)
            return min(hb.head.z, hb.tail.z) - low + pose.get("ground", self.ground) - tz
        ds = [-100 + 10*k for k in range(19)]; vs = [z(d) for d in ds]
        best = None
        for (d0, v0), (d1, v1) in zip(zip(ds, vs), zip(ds[1:], vs[1:])):
            if v0 == 0 or v0*v1 < 0:
                if best is None or abs(d0) < abs(best[0]): best = (d0, d1, v0)
        if best is None: d = ds[min(range(len(vs)), key=lambda i: abs(vs[i]))]
        else:
            lo, hi, vlo = best
            for _ in range(14):
                m = (lo + hi)/2; vm = z(m)
                if (vm < 0) == (vlo < 0): lo, vlo = m, vm
                else: hi = m
            d = (lo + hi)/2
        spec["x"] = spec.get("x", 0) + d; pose[ub] = spec
        pb.rotation_quaternion = B.inverted() @ self.q_for(ub, spec) @ B

    def action(self, name, frames):
        arm = self.arm; arm.animation_data_create()
        act = bpy.data.actions.new(name); act.use_fake_user = True
        arm.animation_data.action = act
        for i, p in enumerate(frames): self.set_pose(p, i + 1)
        for fc in act.fcurves:
            for k in fc.keyframe_points: k.interpolation = 'CONSTANT'
        return act

def _rot(axis, deg): return Quaternion(Vector(axis).normalized(), math.radians(deg))

def _seg_dist(p, a, b):
    ab = b - a; t = max(0, min(1, (p - a).dot(ab) / ab.length_squared))
    return (p - (a + ab*t)).length

def merge(*poses):
    """Soma poses (graus somam; root e ground: o último vence)."""
    out = {}
    for p in poses:
        for k, v in p.items():
            if k in OVERRIDE or not isinstance(v, dict): out[k] = v; continue
            d = dict(out.get(k, {}))
            for kk, vv in v.items(): d[kk] = d.get(kk, 0) + vv
            out[k] = d
    return out

def lerp_pose(a, b, t):
    """Interpola duas poses (specs numéricos e root)."""
    out = {}
    for k in set(a) | set(b):
        if k == "root":
            ra, rb = Vector(a.get(k, (0,0,0))), Vector(b.get(k, (0,0,0))); out[k] = tuple(ra.lerp(rb, t)); continue
        if k == "ground":
            ga, gb = a.get(k, _G[0]), b.get(k, _G[0])
            out[k] = None if ga is None or gb is None else ga + (gb-ga)*t; continue
        if k == "aim" and a.get(k) and b.get(k):
            out[k] = {bb: tuple(Vector(a[k].get(bb, b[k][bb])).normalized().lerp(Vector(b[k].get(bb, a[k].get(bb))).normalized(), t))
                      for bb in set(a[k]) | set(b[k]) if bb in a[k] or bb in b[k]}
            continue
        if k in OVERRIDE or not isinstance(a.get(k, b.get(k)), dict):
            out[k] = (b if t > .5 else a).get(k); continue
        da, db = a.get(k, {}), b.get(k, {})
        out[k] = {kk: da.get(kk, 0)*(1-t) + db.get(kk, 0)*t for kk in set(da) | set(db)}
    return out

def keys_to_frames(keys, n):
    """keys: [(t, pose)] com t em 0..1; devolve n poses interpoladas (suave)."""
    out = []
    for i in range(n):
        t = i/(n-1) if n > 1 else 0
        for j in range(len(keys)-1):
            if keys[j][0] <= t <= keys[j+1][0]:
                a, b = keys[j], keys[j+1]; u = (t - a[0])/max(1e-6, b[0]-a[0])
                u = u*u*(3-2*u); out.append(lerp_pose(a[1], b[1], u)); break
    return out

def apply_mods(o):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); old = o.data
    o.modifiers.clear(); o.data = me; bpy.data.meshes.remove(old)
    return o

def stained(name, rgb, stain=(.12, .012, .008), amount=.35, scale=6, metal=0, rough=.7,
            blotch=None, blotch_amt=0, grime=1.0, dirt=.55):
    """Material sujo com manchas (sangue, ferrugem, hematomas) por cima.
    stain: cor da mancha principal; blotch: segunda cor em manchas grandes (ex. hematoma)."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = mat(name, rgb, metal, rough, dirt=dirt, grime=grime)
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    src = b.inputs["Base Color"].links[0].from_socket
    tc = [n for n in nt.nodes if n.type == 'TEX_COORD'][0]
    def mask(sc, lo, hi, det=4, dist=.0):
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = sc
        nz.inputs["Detail"].default_value = det; nz.inputs["Distortion"].default_value = dist
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        r = nt.nodes.new("ShaderNodeValToRGB")
        r.color_ramp.elements[0].position = lo; r.color_ramp.elements[0].color = (0, 0, 0, 1)
        r.color_ramp.elements[1].position = hi; r.color_ramp.elements[1].color = (1, 1, 1, 1)
        nt.links.new(nz.outputs["Fac"], r.inputs[0]); return r.outputs[0]
    def mix(a, col, fac, k):
        mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MIX'
        mt = nt.nodes.new("ShaderNodeMath"); mt.operation = 'MULTIPLY'; mt.inputs[1].default_value = k
        nt.links.new(fac, mt.inputs[0]); nt.links.new(mt.outputs[0], mx.inputs[0])
        nt.links.new(a, mx.inputs[6]); mx.inputs[7].default_value = (*col, 1); return mx.outputs[2]
    out = src
    if blotch: out = mix(out, blotch, mask(1.6, .45, .7, 3), blotch_amt)
    if amount: out = mix(out, stain, mask(scale, .58, .66, 6, 1.5), amount*2.5)
    nt.links.new(out, b.inputs["Base Color"])
    return m
