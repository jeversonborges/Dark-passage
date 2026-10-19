# Machado do Gladiador Demoníaco: arma PvP do Mutante, fiel à sheet do Gladiador Demoníaco (2ª peça da linha de cima).
# Dois crescentes de lâmina com ganchos nas pontas, caveira de chifres no centro da cabeça, correntes pendendo com
# uma caveirinha, cabo de ferro com faixas de couro e rebite de cobre, pomo de caveira e pano vermelho rasgado.
# Brilho: só a fenda de lava de cada lâmina e os olhos da caveira (emissivos). Sem silhueta genérica: 1 modelo = 1 arma.
#
# Espaço do modelo (mesmo padrão do cetro): metros, origem no centro da pegada, +Z da pegada para a cabeça,
# +X largura da lâmina, +Y espessura.
#
# Uso: /root/bpy42/bin/python machado_gladiador.py -- <saida_dir>
#   gera <saida>/machado_gladiador_demoniaco.glb e <saida>/render_0..7.png (8 direções, fundo transparente).
import bpy, bmesh, math, sys, os
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "personagens"))
bpy.ops.wm.read_factory_settings(use_empty=True)
from rig import mat

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["/tmp/machado"]
OUT = argv[0]; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene

# ------------------------------------------------------------------ materiais
ferro = mat("ferro_negro_machado", (.05, .045, .045), .8, .45, dirt=.5, grime=.35)
cobre = mat("cobre_lamina_machado", (.36, .19, .09), 1, .38, dirt=.45, grime=.3)
osso = mat("osso_caveira_machado", (.26, .23, .19), 0, .5, dirt=.6, grime=.4)
couro = mat("couro_cabo_machado", (.05, .03, .02), 0, .55, dirt=.6)
pano = mat("pano_vermelho_machado", (.38, .03, .03), 0, .85, dirt=.45, grime=.3)
lava = mat("lava_fenda_machado", (1, .3, .05), 0, .2, emit=(1, .25, .04), strength=2.2, dirt=0, grime=0)
olho = mat("olho_brasa_machado", (1, .2, .05), 0, .2, emit=(1, .15, .02), strength=12.0, dirt=0, grime=0)

scene_col = sc.collection

def finish(o, m):
    o.data.materials.append(m)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_smooth()
    return o

def add(op, m, loc, scale=(1, 1, 1), rot=(0, 0, 0), **kw):
    """Primitiva com rotação em graus; scale aplicado depois da rotação."""
    getattr(bpy.ops.mesh, op)(location=loc, rotation=[math.radians(r) for r in rot], **kw)
    o = bpy.context.active_object
    o.scale = scale
    return finish(o, m)

def plate(name, pts, m, t, y=0.0):
    """Placa plana no plano XZ (lista de (x, z)), espessura t em Y centrada em y. Polígono não convexo OK."""
    bm = bmesh.new()
    front = [bm.verts.new((x, y - t / 2, z)) for x, z in pts]
    back = [bm.verts.new((x, y + t / 2, z)) for x, z in pts]
    bm.faces.new(front)
    bm.faces.new(back[::-1])
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([front[i], front[j], back[j], back[i]])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); scene_col.objects.link(o)
    return finish(o, m)

def ring(cx, cz, ro, ri, a0, a1, steps=10, tip=0.0):
    """Anel crescente: arco externo de a0 a a1 e de volta pelo arco interno. tip > 0 pontudo as pontas (gancho)."""
    outer = [(cx + ro * math.cos(a), cz + ro * math.sin(a)) for a in [a0 + (a1 - a0) * k / steps for k in range(steps + 1)]]
    inner = [(cx + ri * math.cos(a), cz + ri * math.sin(a)) for a in [a1 - (a1 - a0) * k / steps for k in range(steps + 1)]]
    if tip:
        outer.append((cx + (ro + tip) * math.cos(a1 + .16), cz + (ro + tip) * math.sin(a1 + .16)))
        inner.append((cx + (ri - tip * .4) * math.cos(a0 - .16), cz + (ri - tip * .4) * math.sin(a0 - .16)))
    return outer + inner

def espelha(pts):
    return [(-x, z) for x, z in pts]

# ------------------------------------------------------------------ cabo e pomo
add("primitive_cylinder_add", ferro, (0, 0, -.2), scale=(.022, .022, .66), vertices=10)
for z in (-.36, -.26, -.16, -.06, .04, .14, .24):           # faixas de couro enroladas no cabo
    add("primitive_torus_add", couro, (0, 0, z), major_radius=.0185, minor_radius=.0055,
        major_segments=14, minor_segments=5)
for z in (-.31, .19):                                         # rebites de cobre nas faixas
    add("primitive_torus_add", cobre, (0, 0, z), major_radius=.0205, minor_radius=.0035,
        major_segments=14, minor_segments=4)
add("primitive_ico_sphere_add", osso, (0, 0, -.50), scale=(.032, .03, .036), subdivisions=2)    # pomo caveira
add("primitive_cone_add", cobre, (0, 0, -.6), scale=(1, 1, 1), rot=(180, 0, 0), vertices=6,
    radius1=.024, radius2=.002, depth=.1)                    # ponta de cobre no pomo

# ------------------------------------------------------------------ caveira central e chifres
HZ = .42
add("primitive_ico_sphere_add", osso, (0, 0, HZ), scale=(.064, .05, .074), subdivisions=2)
add("primitive_ico_sphere_add", ferro, (0, -.012, HZ - .02), scale=(.05, .03, .048), subdivisions=2)   # mandíbula/sombra
for s in (-1, 1):
    add("primitive_ico_sphere_add", olho, (s * .026, -.046, HZ + .014), scale=(.014, .01, .013), subdivisions=1)
    add("primitive_cone_add", ferro, (s * .074, 0, HZ + .05), rot=(0, s * 42, 0), vertices=6,
        radius1=.024, radius2=.003, depth=.14)              # chifre curvado para fora
add("primitive_cone_add", cobre, (0, 0, HZ + .1), vertices=6, radius1=.02, radius2=.002, depth=.12)  # espinho do topo
# espinha que segura as lâminas
plate("espinha_machado", [(-.13, HZ - .014), (.13, HZ - .014), (.13, HZ + .014), (-.13, HZ + .014)], ferro, .02)

# ------------------------------------------------------------------ lâminas crescentes com ganchos
# Crescente fino envolvendo a caveira: a borda de corte é o arco externo, as pontas se curvam de volta para o cabo.
CX, CZ, RO, RI = -.10, .40, .34, .245
for side in (1, -1):
    tag = 'd' if side > 0 else 'e'
    def lado(pts):
        return espelha(pts) if side < 0 else pts
    plate(f"lamina_{tag}", lado(ring(CX, CZ, RO, RI, -.8, .8, steps=12, tip=.045)), cobre, .026)
    # fenda de lava no meio da lâmina (emissiva, um pouco fora do plano)
    plate(f"fenda_lava_{tag}", lado(ring(CX, CZ, RO - .035, RO - .05, -.62, .62, steps=10)), lava, .036)
    # espinhos de cobre na borda de fora
    for a in (-.45, 0, .45):
        px, pz = CX + (RO + .012) * math.cos(a), CZ + (RO + .012) * math.sin(a)
        rot_y = math.degrees(math.atan2(math.cos(a), math.sin(a)))
        x = px if side > 0 else -px
        add("primitive_cone_add", cobre, (x, 0, pz), rot=(0, side * rot_y, 0), vertices=5,
            radius1=.02, radius2=.002, depth=.09)

# ------------------------------------------------------------------ correntes com caveirinha
for s in (-1, 1):
    x = s * .075
    n = 9
    for k in range(n):
        z = .36 - k * .026
        rot = (90, 0, 0) if k % 2 == 0 else (0, 90, 0)
        add("primitive_torus_add", cobre, (x, 0, z), rot=rot, major_radius=.0075, minor_radius=.0017,
            major_segments=8, minor_segments=4)
add("primitive_ico_sphere_add", osso, (.075, 0, .10), scale=(.02, .018, .022), subdivisions=1)  # caveirinha

# ------------------------------------------------------------------ panos rasgados (atrás do cabo)
def pano_pts(x0, ztop, zbot, w):
    return [(x0 - w / 2, ztop), (x0 + w / 2, ztop), (x0 + w * .4, zbot + .07), (x0 + w * .2, zbot),
            (x0, zbot + .05), (x0 - w * .3, zbot + .01), (x0 - w * .45, zbot + .08)]

plate("pano_c", pano_pts(-.01, .34, -.1, .04), pano, .006, y=-.03)
plate("pano_d", pano_pts(.04, .30, -.02, .035), pano, .006, y=-.04)

# ------------------------------------------------------------------ 8 direções
bpy.ops.object.select_all(action='SELECT')
# Escopo do render: tudo selecionado acima; os pedaços ficam juntos para o glb e para a rotação.
world = bpy.data.worlds.new("mundo"); sc.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.01, 0.012, 1)

sun = bpy.data.lights.new("sol", 'SUN'); sun.energy = 2.2
sun_o = bpy.data.objects.new("sol", sun); scene_col.objects.link(sun_o)
sun_o.rotation_euler = (math.radians(55), 0, math.radians(35))
luz = bpy.data.lights.new("brasa", 'POINT'); luz.energy = 120; luz.color = (1, .35, .12)
luz_o = bpy.data.objects.new("brasa", luz); scene_col.objects.link(luz_o)
luz_o.location = (.6, -.9, .5)

cam_d = bpy.data.cameras.new("cam"); cam_d.type = 'ORTHO'; cam_d.ortho_scale = 1.35
cam = bpy.data.objects.new("cam", cam_d); scene_col.objects.link(cam); sc.camera = cam
TARGET = Vector((0, 0, -.02))
cam.location = TARGET + Vector((0, -2.0, .9))
cam.rotation_euler = (TARGET - cam.location).to_track_quat('-Z', 'Y').to_euler()

sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = int(os.environ.get("AMOSTRAS", 48)); sc.cycles.use_denoising = False
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = int(os.environ.get("RES", 384))
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'

# gira o modelo (não a câmera) para cada uma das 8 direções
armas = [o for o in scene_col.objects if o.type == 'MESH']
for k in range(8):
    ang = math.radians(k * 45)
    for o in armas:
        o.rotation_euler = (0, 0, ang)
    sc.render.filepath = os.path.join(OUT, f"render_{k}.png")
    bpy.ops.render.render(write_still=True)

# ------------------------------------------------------------------ glb para o jogo
for o in armas:
    o.rotation_euler = (0, 0, 0)
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT, "machado_gladiador_demoniaco.glb"), export_format='GLB',
                          use_selection=True, export_apply=True)
tris = sum(len(p.vertices) - 2 for o in armas for p in o.data.polygons)
print("ok", OUT, "tris~", tris)
