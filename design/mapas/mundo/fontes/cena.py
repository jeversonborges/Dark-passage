# Harness das vinhetas de área (proposta de mundo). Usa o kit de ambiente do jogo
# (assets/ambiente/fontes: kit.py materiais/câmera, assets.py modelos) para que cada
# imagem saia no mesmo estilo e na mesma câmera isométrica do jogo.
# Uso dentro do Blender:  import cena as C; C.iniciar(...); C.chao(...); C.por(...); C.render(...)
import bpy, sys, os, math, random
from mathutils import Vector
KIT = "/mnt/project-files/assets/ambiente/fontes"
sys.path.insert(0, KIT)
import kit as K
import assets as A
T = K.T
_M = None
def mats():
    global _M
    if _M is None: _M = A.M()
    return _M

def iniciar(ceu=(.012, .013, .018), poeira=(.26, .19, .115), dungeon=False, luzes=True):
    """Cena nova com a câmera iso do kit. poeira = cor que assenta no topo dos objetos."""
    global _M
    _M = None; _INST.clear(); K._cache.clear(); K.DUST = poeira
    sc = K.reset(); K.make_cam()
    sc.render.film_transparent = False
    sc.world.color = ceu
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (*ceu, 1); bg.inputs[1].default_value = 1.0
    sc.view_layers[0].use_pass_mist = True
    sc.world.mist_settings.start = 95; sc.world.mist_settings.depth = 60; sc.world.mist_settings.falloff = 'LINEAR'
    if luzes: K.lights(dungeon)
    return sc

def sol(cor, energia, rot, ang=.06, nome="sol"): return K.sun(nome, cor, energia, rot, ang)
def ponto(loc, cor, energia, raio=.2): return K.point(loc, cor, energia, raio)

def chao(mat, tam=90, centro=(0, 0), ondula=0.0, seed=0, z=0.0, nome="chao"):
    """Plano de chão (mat = material ou nome de piso do kit: areia, vitrificada, leito, cinza, lama,
    agua_toxica, terra, cemiterio, asfalto, entulho, calcamento...). ondula = altura das dunas em m."""
    if isinstance(mat, str): mat = K.mat_ground(mat, (8.0, 8.0), seed)
    bpy.ops.mesh.primitive_plane_add(size=tam, location=(centro[0], centro[1], z))
    o = bpy.context.object; o.name = "_" + nome if not ondula else nome
    o.data.materials.append(mat)
    if ondula:
        K.displace(o, ondula, 6.0, seed, 0)
        s = o.modifiers.new("sub", 'SUBSURF'); s.levels = s.render_levels = 6; s.subdivision_type = 'SIMPLE'
        o.modifiers.move(o.modifiers.find("sub"), 0)
    return o

def faixa(mat, pts, larg, z=.004, seed=0, nome="faixa"):
    """Faixa de chão ao longo de uma polilinha (rio, estrada, trilha). larg em metros."""
    if isinstance(mat, str): mat = K.mat_ground(mat, (8.0, 8.0), seed)
    vs, fs = [], []
    P = [Vector((p[0], p[1], z)) for p in pts]
    for i, p in enumerate(P):
        d = (P[min(i+1, len(P)-1)] - P[max(i-1, 0)]).normalized()
        n = Vector((-d.y, d.x, 0)); w = larg[i] if isinstance(larg, (list, tuple)) else larg
        vs += [p + n*w/2, p - n*w/2]
        if i: fs.append((2*i-2, 2*i-1, 2*i+1, 2*i))
    me = bpy.data.meshes.new(nome); me.from_pydata(vs, [], fs); me.update()
    o = bpy.data.objects.new("_" + nome, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat); return o

def mancha(mat, centro, raio, seed=0, z=.006, irregular=.35, nome="mancha"):
    """Mancha irregular de outro piso (poça, vidro, cinza) sobre o chão."""
    if isinstance(mat, str): mat = K.mat_ground(mat, (8.0, 8.0), seed)
    r = random.Random(seed); n = 28
    ph = [r.uniform(0, 6.28) for _ in range(3)]
    vs = [(centro[0], centro[1], z)]
    for i in range(n):
        a = i/n*2*math.pi
        k = 1 + irregular*(.5*math.sin(2*a+ph[0]) + .3*math.sin(3*a+ph[1]) + .2*math.sin(5*a+ph[2]))
        vs.append((centro[0] + math.cos(a)*raio*k, centro[1] + math.sin(a)*raio*k, z))
    fs = [(0, i+1, (i+1) % n + 1) for i in range(n)]
    me = bpy.data.meshes.new(nome); me.from_pydata(vs, [], fs); me.update()
    o = bpy.data.objects.new("_" + nome, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat); return o

_INST = {}
def _colecao(chave, construir):
    """Monta o modelo uma vez numa coleção escondida; os usos seguintes são instâncias (rápido)."""
    if chave in _INST: return _INST[chave]
    sc = bpy.context.scene
    col = bpy.data.collections.new("m_" + chave[:50]); sc.collection.children.link(col)
    before = set(bpy.data.objects)
    construir()
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        for c in list(o.users_collection): c.objects.unlink(o)
        col.objects.link(o)
    bpy.context.view_layer.layer_collection.children[col.name].exclude = True
    _INST[chave] = (col, new); return _INST[chave]

def _inst(col, x, y, rot, s, z):
    e = bpy.data.objects.new("i_" + col.name, None); bpy.context.scene.collection.objects.link(e)
    e.instance_type = 'COLLECTION'; e.instance_collection = col
    e.location = (x, y, z); e.rotation_euler = (0, 0, math.radians(rot)); e.scale = (s, s, s)
    return e

def por(nome, x, y, rot=0.0, s=1.0, z=0.0, **kw):
    """Coloca um modelo do kit (nome de assets.REG) em (x, y) metros, girado rot graus."""
    info = A.REG[nome]
    def construir():
        before = set(bpy.data.objects)
        info["fn"](mats(), **kw)
        new = [o for o in bpy.data.objects if o not in before]
        if info.get("bury"):
            for o in new:
                if o.parent is None:
                    mn = o.data.materials[0].name if getattr(o, "data", None) is not None and getattr(o.data, "materials", None) and len(o.data.materials) else ""
                    if not mn.startswith("areia_monte"): o.location.z -= info["bury"]
    col, _ = _colecao(nome + str(sorted(kw.items())), construir)
    return _inst(col, x, y, rot, s, z)

def grupo(fn, x, y, rot=0.0, s=1.0, z=0.0, chave=None):
    """Igual a por(), mas para um modelo novo escrito no script da área: fn(mats()) monta em volta
    da origem. Com chave, o modelo é montado uma vez e reaproveitado como instância."""
    col, _ = _colecao(chave or f"g{len(_INST)}", lambda: fn(mats()))
    return _inst(col, x, y, rot, s, z)

def render(out, centro=(0, 0), largura=44.0, W=1920, H=1080, samples=64):
    """Renderiza a vinheta: câmera iso do kit centrada em 'centro' (metros do mundo), mostrando
    'largura' metros de tela. Grava <out>_raw.png e <out>_mist.png (névoa por profundidade)."""
    sc = bpy.context.scene; cam = sc.camera
    cam.data.ortho_scale = largura
    right = Vector((math.cos(math.radians(K.AZ)), math.sin(math.radians(K.AZ)), 0))
    c = Vector((centro[0], centro[1], 0))
    sx, sy = c.dot(right), c.dot(K.up_vec())
    cam.location = right*sx + K.up_vec()*sy + K.cam_dir()*120
    sc.render.resolution_x, sc.render.resolution_y = W, H
    sc.cycles.samples = samples
    sc.use_nodes = True; nt = sc.node_tree; nt.nodes.clear()
    rl = nt.nodes.new("CompositorNodeRLayers")
    comp = nt.nodes.new("CompositorNodeComposite"); nt.links.new(rl.outputs["Image"], comp.inputs[0])
    fo = nt.nodes.new("CompositorNodeOutputFile"); fo.base_path = os.path.dirname(out) or "."
    fo.file_slots[0].path = os.path.basename(out) + "_mist_"; fo.format.color_mode = 'BW'; fo.format.color_depth = '16'
    nt.links.new(rl.outputs["Mist"], fo.inputs[0])
    sc.render.filepath = out + "_raw.png"
    bpy.ops.render.render(write_still=True)
    d = os.path.dirname(out) or "."
    for f in os.listdir(d):
        if f.startswith(os.path.basename(out) + "_mist_"): os.replace(os.path.join(d, f), out + "_mist.png")
