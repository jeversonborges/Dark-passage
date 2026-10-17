# Utilitários do Egito (parte A: mumia, escaravelho, crocodilo, serpente).
# - rest_uv(): grava a posição de repouso de cada vértice em dois UVs ("rxy", "rz"). Os materiais abaixo leem
#   essas coordenadas, então faixas, listras e manchas não "nadam" quando a malha deforma com o esqueleto.
# - linho(): faixas de linho de múmia (duas camadas de faixas cruzadas, costuras escuras, resina preta
#   escorrendo em filetes verticais, sujeira de lodo para os pés).
# - listras(): pintura antiga em faixas (nemes azul e ouro, colares), gasta até o gesso.
# - manchas(): pelagem/couro com manchas (pele de leopardo, couro de boi malhado).
# - ouro(), bronze(), cobre(): metais antigos (patina de atlante.py).
# - faixas_em(): anéis de linho em volta de um osso (relevo das voltas) e pontas soltas.
import bpy, math, random
from mathutils import Vector, Quaternion
from mrig import *
from atlante import patina, glow, _tc, _math, _mixc, scales, add_uv, catmull, arclen, tube, bind_path, strip, chain_links, orient

TURQ = (.18, .95, .85)          # emissivo da área: azul-turquesa de faiança

def rest_uv(o):
    me = o.data
    if "rxy" in me.uv_layers: return o
    if len(me.uv_layers) > 6 or not me.polygons: return o
    me.uv_layers.new(name="rxy"); me.uv_layers.new(name="rz")
    a = me.uv_layers["rxy"]; b = me.uv_layers["rz"]   # buscar de novo: criar camada invalida referências antigas
    for p in me.polygons:
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            a.data[li].uv = (co.x, co.y); b.data[li].uv = (co.z, 0)
    return o

def finalize(R):
    """Grava as coordenadas de repouso em todas as malhas presas ao esqueleto (chamar no fim do build)."""
    bpy.context.view_layer.update()
    for o in R.arm.children:
        if o.type == 'MESH': rest_uv(o)

def _rest(nt):
    """Vetor com a posição de repouso (x, y, z) lido dos UVs rxy/rz."""
    u1 = nt.nodes.new("ShaderNodeUVMap"); u1.uv_map = "rxy"
    u2 = nt.nodes.new("ShaderNodeUVMap"); u2.uv_map = "rz"
    s1 = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(u1.outputs[0], s1.inputs[0])
    s2 = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(u2.outputs[0], s2.inputs[0])
    c = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(s1.outputs[0], c.inputs[0]); nt.links.new(s1.outputs[1], c.inputs[1]); nt.links.new(s2.outputs[0], c.inputs[2])
    return c.outputs[0]

def _mask(nt, vec, sc, lo, hi, det=4, dist=0.0, stretch=None):
    if stretch:
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = stretch
        nt.links.new(vec, mp.inputs[0]); vec = mp.outputs[0]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = sc
    nz.inputs["Detail"].default_value = det; nz.inputs["Distortion"].default_value = dist
    nt.links.new(vec, nz.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.elements[0].position = lo; r.color_ramp.elements[0].color = (0, 0, 0, 1)
    r.color_ramp.elements[1].position = hi; r.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(nz.outputs["Fac"], r.inputs[0]); return r.outputs[0]

def _wave(nt, vec, scale, rot, dist=2.0):
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = [math.radians(r) for r in rot]
    nt.links.new(vec, mp.inputs[0])
    w = nt.nodes.new("ShaderNodeTexWave"); w.wave_type = 'BANDS'; w.bands_direction = 'Z'; w.wave_profile = 'SAW'
    w.inputs["Scale"].default_value = scale; w.inputs["Distortion"].default_value = dist
    w.inputs["Detail"].default_value = 2; w.inputs["Detail Scale"].default_value = 1.5
    nt.links.new(mp.outputs[0], w.inputs["Vector"]); return w.outputs["Fac"]

def _ramp(nt, fac, stops):
    r = nt.nodes.new("ShaderNodeValToRGB"); cr = r.color_ramp
    cr.elements[0].position, cr.elements[0].color = stops[0][0], (*stops[0][1], 1)
    cr.elements[1].position, cr.elements[1].color = stops[1][0], (*stops[1][1], 1)
    for p, c in stops[2:]:
        e = cr.elements.new(p); e.color = (*c, 1)
    nt.links.new(fac, r.inputs[0]); return r.outputs[0]

def _mul(nt, a, b):
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1
    for i, v in ((6, a), (7, b)):
        if isinstance(v, tuple): mx.inputs[i].default_value = (*v, 1)
        else: nt.links.new(v, mx.inputs[i])
    return mx.outputs[2]

def _grime(nt, vec, col, grime, top=1.4):
    sz = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(vec, sz.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = 0; mr.inputs["From Max"].default_value = top
    mr.inputs["To Min"].default_value = 1 - .6*grime; mr.inputs["To Max"].default_value = 1
    nt.links.new(sz.outputs["Z"], mr.inputs["Value"])
    c = nt.nodes.new("ShaderNodeCombineXYZ")
    for k in "XYZ": nt.links.new(mr.outputs[0], c.inputs[k])
    return _mul(nt, col, c.outputs[0])

def linho(name, rgb=(.36, .31, .22), band=13, resin=.5, resin_col=(.014, .011, .008), mud=(.13, .11, .07), mud_amt=.6,
          grime=1.0, rough=.92, seam=.22, rot1=(18, 8, 0), rot2=(-14, -22, 0), stain2=None, stain2_amt=0):
    """Faixas de linho de múmia (lê o repouso por rest_uv)."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    P = _rest(nt)
    w1 = _wave(nt, P, band, rot1); w2 = _wave(nt, P, band*.83, rot2, 3.0)
    lay = _mask(nt, P, 3.0, .45, .55, 2, .5)        # qual camada de faixas fica por cima
    wsel = nt.nodes.new("ShaderNodeMix"); wsel.data_type = 'FLOAT'
    nt.links.new(lay, wsel.inputs[0]); nt.links.new(w1, wsel.inputs[2]); nt.links.new(w2, wsel.inputs[3])
    wv = wsel.outputs[0]
    sh = _ramp(nt, wv, [(0, (seam, seam*.95, seam*.9)), (.12, (1, 1, 1)), (.85, (.92, .92, .92)), (1, (seam*1.2,)*3)])
    fib = _mask(nt, P, 60, .3, .75, 3, .2)
    fibc = _ramp(nt, fib, [(0, (.86, .86, .86)), (1, (1.04, 1.02, 1))])
    col = _mul(nt, _mul(nt, rgb, sh), fibc)
    big = _mask(nt, P, 2.2, .4, .75, 3, .6)
    col = _mixc(nt, _math(nt, 'MULTIPLY', big, .55), col, tuple(c*.62 for c in rgb))
    if stain2: col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 4, .55, .7, 4, 1.0), stain2_amt), col, stain2)
    col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 5, .56, .7, 4, 1.2), mud_amt), col, mud)
    col = _grime(nt, P, col, grime)
    dr = _mask(nt, P, 9, .62, .7, 5, .8, stretch=(1, 1, .22))   # resina escorrendo em filetes
    rs = _math(nt, 'MULTIPLY', dr, resin)
    col = _mixc(nt, rs, col, resin_col)
    nt.links.new(col, b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = rough; rr.inputs["To Max"].default_value = .22
    nt.links.new(rs, rr.inputs["Value"]); nt.links.new(rr.outputs[0], b.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .45; bump.inputs["Distance"].default_value = .006
    bh = _math(nt, 'ADD', wv, _math(nt, 'MULTIPLY', fib, .25))
    nt.links.new(bh, bump.inputs["Height"]); nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m

def listras(name, c1, c2, period=.05, duty=.5, axis='Z', wear=.45, under=(.42, .38, .3), grime=.8, metal2=0.0,
            rough=.6, rot=(0, 0, 0)):
    """Pintura antiga em listras (c1/c2 alternadas a cada period m no eixo do repouso), gasta até o gesso."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    P = _rest(nt)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Rotation"].default_value = [math.radians(r) for r in rot]
    nt.links.new(P, mp.inputs[0])
    sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(mp.outputs[0], sp.inputs[0])
    ax = sp.outputs["XYZ".index(axis)]
    fr = _math(nt, 'FRACT', _math(nt, 'DIVIDE', ax, period))
    st = _math(nt, 'GREATER_THAN', fr, 1 - duty)
    col = _mixc(nt, st, c1, c2)
    wm = _mask(nt, P, 7, .6, .66, 5, 1.0)
    col = _mixc(nt, _math(nt, 'MULTIPLY', wm, wear*2), col, under)
    col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 3, .5, .7, 3, .5), .5), col, (.05, .04, .03))
    col = _grime(nt, P, col, grime, top=2.6)
    nt.links.new(col, b.inputs["Base Color"])
    nt.links.new(_math(nt, 'MULTIPLY', _math(nt, 'MULTIPLY', st, metal2), _math(nt, 'SUBTRACT', 1.0, wm)), b.inputs["Metallic"])
    b.inputs["Roughness"].default_value = rough
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .3; bump.inputs["Distance"].default_value = .004
    nt.links.new(wm, bump.inputs["Height"]); nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m

def manchas(name, base, spot, kind="leopardo", scale=22, rot_col=(.1, .12, .06), rot_amt=.5, rough=.85, grime=.8):
    """Pelagem com manchas: leopardo (rosetas pequenas) ou boi (manchas grandes)."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    P = _rest(nt)
    if kind == "leopardo":
        vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = scale
        vo.inputs["Randomness"].default_value = .9; nt.links.new(P, vo.inputs["Vector"])
        ring = _ramp(nt, vo.outputs["Distance"], [(0, (0, 0, 0)), (.2, (0, 0, 0)), (.24, (1, 1, 1)), (.3, (1, 1, 1)), (.34, (0, 0, 0))])
        sel = _mask(nt, P, scale*.5, .45, .55, 2)
        f = _math(nt, 'MULTIPLY', nt.nodes["Color Ramp"].outputs[0] if False else ring, sel)
        f = _math(nt, 'MINIMUM', f, 1.0)
    else:
        f = _mask(nt, P, scale, .5, .54, 3, .6)
    col = _mixc(nt, f, base, spot)
    col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 4, .5, .68, 4, 1), rot_amt), col, rot_col)
    col = _grime(nt, P, col, grime)
    nt.links.new(col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .25
    nt.links.new(_mask(nt, P, 70, .2, .8, 2), bump.inputs["Height"]); nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m

def ouro(name, rgb=(.55, .38, .12), amount=.35):
    return patina(name, rgb, green=(.12, .1, .05), rough=.4, amount=amount, scale=6, stain=(.03, .025, .015), stain_amt=.6)

def bronze(name, rgb=(.34, .2, .09), amount=.7):
    return patina(name, rgb, green=(.06, .2, .15), rough=.45, amount=amount, scale=5)

def cobre(name, rgb=(.42, .17, .08), amount=.55):
    return patina(name, rgb, green=(.07, .22, .17), rough=.42, amount=amount, scale=5)

def faixas_em(R, bone, m, t0=.1, t1=.9, n=5, r=.05, rnd=None, tilt=.45, minor=.006, sq=1.0, ends=0, end_len=.12, r1=None,
              flat=2.2):
    """Voltas de faixa de linho em volta de um osso (anéis achatados e inclinados, raio r -> r1 ao longo do osso,
    colados no corpo) e pontas soltas; devolve as peças."""
    rnd = rnd or random.Random(hash(bone) & 0xffff)
    r1 = r if r1 is None else r1
    a, b = R.P(bone), R.P(bone, 1); d = (b - a); ax = d.normalized(); out = []
    for k in range(n):
        tt = t0 + (t1 - t0)*k/max(1, n - 1); c = a.lerp(b, tt); rr_ = r + (r1 - r)*tt
        o = prim("primitive_torus_add", m, c, (1, 1, 1), major_radius=rr_*rnd.uniform(.97, 1.03), minor_radius=minor,
                 major_segments=16, minor_segments=4)
        q = ax.to_track_quat('Z', 'Y') @ Quaternion((1, 0, 0), rnd.uniform(-tilt, tilt)) @ Quaternion((0, 1, 0), rnd.uniform(-tilt*.5, tilt*.5))
        o.rotation_euler = q.to_euler(); o.scale = (1, sq, flat); out.append(o)
    for k in range(ends):
        tt = rnd.uniform(t0, t1); c = a.lerp(b, tt); rr_ = r + (r1 - r)*tt
        side = ax.cross(Vector((0, 0, 1)))
        if side.length < .1: side = Vector((1, 0, 0))
        side = (Quaternion(ax, rnd.uniform(0, 6.28)) @ side.normalized())
        p0 = c + side*rr_
        p1 = p0 + side*.02 + Vector((rnd.uniform(-.02, .02), rnd.uniform(-.01, .03), -end_len*rnd.uniform(.6, 1.2)))
        out.append(strip(m, p0, p0.lerp(p1, .5) + side*.01, .026, .004, twist=rnd.uniform(-.5, .5)))
        out.append(strip(m, p0.lerp(p1, .5) + side*.01, p1, .022, .004, twist=rnd.uniform(-.5, .5)))
    return out

def tira(m, pts, w=.03, t=.004):
    """Tira solta em vários segmentos (faixa pendurada)."""
    return [strip(m, a, b, w, t) for a, b in zip(pts, pts[1:])]

def hieroglifos(m, c, nrm, up=(0, 0, 1), size=.025, n=4, seed=1, depth=.003):
    """Coluna de hieróglifos simplificados em relevo (olho, junco, água, ankh, pássaro) numa superfície."""
    rr = random.Random(seed); nrm = Vector(nrm).normalized(); U = Vector(up); U = (U - nrm*U.dot(nrm)).normalized()
    X = U.cross(nrm); out = []; c = Vector(c)
    def seg(p, q, r=size*.12):
        out.append(along("primitive_cylinder_add", m, c + X*p[0] + U*p[1] + nrm*depth, c + X*q[0] + U*q[1] + nrm*depth, r, vertices=4))
    for k in range(n):
        y = -k*size*1.3; s = size*.5; kind = rr.randint(0, 4)
        if kind == 0:   # água (zigue-zague)
            pts = [(-s + 2*s*i/4, y + (s*.25 if i % 2 else -s*.25)) for i in range(5)]
            for p, q in zip(pts, pts[1:]): seg(p, q)
        elif kind == 1:  # junco
            seg((0, y - s), (0, y + s*.6)); seg((0, y + s*.6), (s*.4, y + s))
        elif kind == 2:  # ankh
            seg((0, y - s), (0, y + s*.2)); seg((-s*.5, y + s*.2), (s*.5, y + s*.2))
            t_ = prim("primitive_torus_add", m, c + U*(y + s*.55) + nrm*depth, (1, 1, 1), major_radius=s*.3, minor_radius=size*.1,
                      major_segments=8, minor_segments=3); t_.rotation_euler = nrm.to_track_quat('Z', 'Y').to_euler(); out.append(t_)
        elif kind == 3:  # olho
            seg((-s, y), (s, y)); seg((-s*.6, y + s*.3), (s*.6, y + s*.3)); seg((0, y), (-s*.3, y - s*.6))
        else:            # pássaro
            seg((-s, y - s*.2), (s*.4, y - s*.2)); seg((s*.4, y - s*.2), (s*.6, y + s*.4)); seg((-s*.2, y - s*.2), (-s*.2, y - s*.8))
    return out
