# Modelos procedurais do DARK PASSAGE no estilo Dark Eden: humanoides com
# corpo orgânico (Skin modifier), roupas punk/góticas e equipamentos.
import bpy, math
from mathutils import Vector

def mat(name, rgb, metal=0.0, rough=0.6, emit=None, strength=0.0):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m

def _link(o, parent):
    o.parent = parent; return o

def prim(op, m, loc, scale=(1,1,1), rot=(0,0,0), parent=None, smooth=True, **kw):
    getattr(bpy.ops.mesh, op)(location=loc, rotation=[math.radians(r) for r in rot], **kw)
    o = bpy.context.object; o.scale = scale; o.data.materials.append(m)
    if smooth: bpy.ops.object.shade_smooth()
    return _link(o, parent)

def along(op, m, a, b, r, parent, **kw):
    """Peça cilíndrica/cônica do ponto a ao ponto b."""
    a, b = Vector(a), Vector(b); d = b - a
    getattr(bpy.ops.mesh, op)(location=(a+b)/2, **kw)
    o = bpy.context.object; o.rotation_euler = d.to_track_quat('Z','Y').to_euler()
    o.scale = (r, r, d.length/2); o.data.materials.append(m); bpy.ops.object.shade_smooth()
    return _link(o, parent)

# Esqueleto base (personagem olhando para -Y, ~1.8 de altura)
BASE = {
 "pelvis":(0,0,0.95,.15), "spine":(0,0,1.15,.13), "chest":(0,0,1.33,.165), "neck":(0,0,1.52,.055),
 "hipL":(.1,0,.92,.085), "kneeL":(.12,-.03,.5,.06), "ankleL":(.13,0,.1,.048), "toeL":(.13,-.13,.03,.04),
 "hipR":(-.1,0,.92,.085), "kneeR":(-.12,-.03,.5,.06), "ankleR":(-.13,0,.1,.048), "toeR":(-.13,-.13,.03,.04),
 "shL":(.2,0,1.43,.065), "elL":(.3,.03,1.14,.05), "wrL":(.34,-.04,.9,.038),
 "shR":(-.2,0,1.43,.065), "elR":(-.3,.03,1.14,.05), "wrR":(-.34,-.04,.9,.038),
}
EDGES = [("pelvis","spine"),("spine","chest"),("chest","neck"),
 ("pelvis","hipL"),("hipL","kneeL"),("kneeL","ankleL"),("ankleL","toeL"),
 ("pelvis","hipR"),("hipR","kneeR"),("kneeR","ankleR"),("ankleR","toeR"),
 ("chest","shL"),("shL","elL"),("elL","wrL"),("chest","shR"),("shR","elR"),("elR","wrR")]

def body(name, m, parent, pose=None):
    j = dict(BASE); j.update(pose or {})
    keys = list(j); me = bpy.data.meshes.new(name)
    me.from_pydata([j[k][:3] for k in keys], [(keys.index(a), keys.index(b)) for a, b in EDGES], [])
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.modifiers.new("skin", 'SKIN')
    for i, k in enumerate(keys):
        o.data.skin_vertices[0].data[i].radius = (j[k][3], j[k][3])
    o.data.skin_vertices[0].data[0].use_root = True
    o.modifiers.new("sub", 'SUBSURF').levels = 2; o.modifiers["sub"].render_levels = 2
    me.materials.append(m)
    for p in me.polygons: p.use_smooth = True
    _link(o, parent)
    return {k: Vector(v[:3]) for k, v in j.items()}

def hands_boots(j, skin, boot, parent):
    for s in "LR":
        prim("primitive_uv_sphere_add", skin, j["wr"+s] + Vector((0,-.02,-.05)), (.045,.04,.055), parent=parent)
        along("primitive_cone_add", boot, j["ankle"+s] + Vector((0,0,.22)), j["ankle"+s] - Vector((0,0,.05)), 1, parent, radius1=.07, radius2=.065, vertices=10)
        prim("primitive_uv_sphere_add", boot, j["toe"+s] + Vector((0,0,.01)), (.06,.1,.045), parent=parent)

def spikes(m, center, n, length, spread, parent, up=(0,.3,1), seed=1):
    import random; rnd = random.Random(seed)
    for i in range(n):
        d = Vector((rnd.uniform(-spread,spread), up[1]+rnd.uniform(-.3,.5), up[2])).normalized()
        along("primitive_cone_add", m, center, center + d*length*rnd.uniform(.7,1.2), 1, parent, radius1=.04, radius2=0, vertices=5)

def wing(side, feather, parent, base):
    base = Vector(base)
    for layer, (n, L0) in enumerate([(8, .62), (6, .38)]):
        for k in range(n):
            a = math.radians(35 + k*(75/(n-1)))
            d = Vector((side*math.cos(a)*.7, .75+.1*layer, math.sin(a)+.1)).normalized()
            L = L0*(1.15 - k*.06)
            o = prim("primitive_uv_sphere_add", feather, base + d*L*.5 + Vector((0,.03*layer,-.05*layer)), (.045, .012, L/2), parent=parent, segments=12, ring_count=8)
            o.rotation_euler = d.to_track_quat('Z','Y').to_euler()

def chain(m, a, b, links, parent):
    a, b = Vector(a), Vector(b)
    for i in range(links):
        p = a.lerp(b, i/(links-1)); p.z -= math.sin(math.pi*i/(links-1))*.04
        o = prim("primitive_torus_add", m, p, (1,1,1), (0, 90 if i%2 else 0, 0), parent=parent, major_radius=.018, minor_radius=.005, major_segments=8, minor_segments=4)

def make_root(name, loc=(0,0,0), face=0.0):
    r = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(r)
    r.location = loc; r.rotation_euler = (0, 0, face); return r

def coat(outer, lining, root, length=.55):
    """Sobretudo longo aberto na frente: aba traseira com forro e duas abas frontais."""
    o = prim("primitive_cube_add", outer, (0,.13,1.42-length), (.21,.025,length), (-6,0,0), parent=root)
    prim("primitive_cube_add", lining, (0,.1,1.42-length), (.19,.008,length*.95), (-6,0,0), parent=root)
    for s in (-1,1):
        prim("primitive_cube_add", outer, (.13*s,-.09,1.0-length*.35), (.075,.025,length*.75), (5,0,-8*s), parent=root)
        prim("primitive_cube_add", outer, (.16*s,.02,1.0-length*.35), (.025,.1,length*.75), (0,0,0), parent=root)
    prim("primitive_cube_add", outer, (0,-.02,1.48), (.24,.15,.07), parent=root)  # gola alta

# --- Arautos do Juízo: Anjo caído punk (branco osso, ouro sujo, vermelho sangue)
def anjo(root):
    leather = mat("couro_negro", (.02,.018,.02), .2, .35)
    skin = mat("pele_palida", (.55,.5,.48), 0, .5)
    bone = mat("osso", (.85,.82,.72), 0, .5)
    gold = mat("ouro_sujo", (.35,.25,.08), 1, .45)
    blood = mat("vermelho_sangue", (.18,.01,.01), .1, .3)
    steel = mat("aco_escuro", (.5,.5,.52), 1, .25)
    feather = mat("pena_suja", (.16,.15,.14), 0, .8)
    halo = mat("halo_rachado", (1,.8,.4), emit=(1,.6,.2), strength=5)
    j = body("anjo_corpo", leather, root, {"wrR":(-.36,-.12,.98,.038), "elR":(-.33,-.02,1.14,.05)})
    hands_boots(j, skin, leather, root)
    # sobretudo longo aberto com forro vermelho
    coat(leather, blood, root)
    # ombreiras de osso com cravos e corrente no peito
    for s in (-1,1):
        prim("primitive_uv_sphere_add", bone, (.21*s,0,1.47), (.12,.12,.08), parent=root)
        for k in range(3):
            along("primitive_cone_add", steel, (.21*s+.04*(k-1)*s,0,1.53), (.27*s+.06*(k-1)*s,0,1.7), 1, root, radius1=.018, radius2=0, vertices=6)
    chain(steel, (.15,-.17,1.38), (-.12,-.16,1.05), 9, root)
    # cabeça e cabelo espetado branco
    prim("primitive_uv_sphere_add", skin, (0,-.01,1.65), (.095,.1,.115), parent=root)
    prim("primitive_cube_add", blood, (0,-.1,1.66), (.06,.01,.008), parent=root)  # olhos vermelhos
    spikes(bone, Vector((0,.04,1.72)), 18, .3, 1.0, root, up=(0,.7,.6), seed=3)
    prim("primitive_torus_add", halo, (0,.08,1.88), (1,1,1), (20,0,0), parent=root, major_radius=.13, minor_radius=.012)
    wing(-1, feather, root, (-.08,.14,1.38)); wing(1, feather, root, (.08,.14,1.38))
    # espada-cruz pesada na mão direita
    w = j["wrR"] + Vector((0,-.04,-.04))
    prim("primitive_cube_add", steel, w + Vector((0,0,.55)), (.05,.012,.48), parent=root)
    prim("primitive_cube_add", gold, w + Vector((0,0,.06)), (.17,.025,.025), parent=root)
    prim("primitive_cube_add", blood, w + Vector((.02,-.013,.75)), (.012,.002,.2), parent=root)  # sangue na lâmina
    return j

# --- Vigília: Humano soldado punk (azul aço, verde ácido, laranja brasa)
def humano(root):
    fatigue = mat("farda", (.09,.09,.07), 0, .8)
    skin = mat("pele", (.42,.3,.24), 0, .5)
    boot = mat("bota", (.02,.02,.02), 0, .4)
    vest = mat("colete_azul_aco", (.1,.13,.17), .3, .5)
    acid = mat("verde_acido", (.2,.6,.05), 0, .4, emit=(.4,1,.1), strength=1.5)
    ember = mat("laranja_brasa", (.6,.2,.02), 0, .4, emit=(1,.35,.05), strength=6)
    metal = mat("metal_gasto", (.15,.15,.15), 1, .4)
    wood = mat("madeira", (.18,.09,.04), 0, .6)
    leather = mat("couro_marrom", (.1,.05,.03), 0, .5)
    pose = {"elR":(-.24,-.15,1.12,.05), "wrR":(-.12,-.35,1.07,.038), "elL":(.28,-.1,1.12,.05), "wrL":(.12,-.42,1.12,.038)}
    j = body("humano_corpo", fatigue, root, pose)
    hands_boots(j, skin, boot, root)
    # colete tático, bandoleira com cartuchos e cinto
    prim("primitive_cube_add", vest, (0,-.01,1.24), (.17,.13,.17), parent=root)
    prim("primitive_uv_sphere_add", vest, (.2,0,1.44), (.09,.09,.06), parent=root)  # ombreira só de um lado
    for i in range(8):
        t = i/7; p = Vector((.17,-.16,1.45)).lerp(Vector((-.17,-.16,1.02)), t)
        along("primitive_cylinder_add", ember, p, p+Vector((0,-.03,.02)), .012, root, vertices=6)
    prim("primitive_torus_add", leather, (0,0,.95), (1,1,.6), parent=root, major_radius=.165, minor_radius=.03)
    along("primitive_cylinder_add", leather, (0,.12,1.0), (0,.18,1.45), .07, root, vertices=10)  # mochila
    # lanterna de gás verde no cinto
    prim("primitive_cylinder_add", acid, (.19,-.05,.88), (.035,.035,.06), parent=root)
    # cabeça, moicano verde, lenço azul no rosto
    prim("primitive_uv_sphere_add", skin, (0,-.01,1.64), (.09,.1,.11), parent=root)
    for i in range(7):
        y = -.08 + i*.03
        along("primitive_cone_add", acid, (0,y,1.7+.01*math.sin(i)), (0,y+.04,1.86-abs(i-3)*.02), 1, root, radius1=.025, radius2=0, vertices=5)
    prim("primitive_cylinder_add", vest, (0,-.02,1.565), (.075,.08,.03), parent=root)
    prim("primitive_cube_add", ember, (0,-.105,1.66), (.06,.006,.007), parent=root)  # óculos de visão
    # escopeta de cano serrado
    a, b = j["wrR"] + Vector((0,.1,.0)), j["wrL"] + Vector((0,-.25,.02))
    along("primitive_cylinder_add", metal, a, b, .022, root, vertices=10)
    along("primitive_cube_add", wood, a + Vector((0,.25,-.06)), a, .03, root)
    prim("primitive_cube_add", wood, j["wrL"], (.03,.06,.025), parent=root)
    return j
