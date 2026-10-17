# Cetro do Demiurgo: a arma única do administrador (Jefin). Haste de ferro negro com embutido de ouro em espiral,
# pegada de couro com três anéis de ouro, selo de obsidiana no pomo com sete entalhes, coroa de sete garras de ouro
# segurando a esmeralda octaédrica (único brilho, verde-esmeralda pálido) dentro de uma esfera armilar de latão
# (três anéis inclinados + o equador com sete lascas de esmeralda), prumo de ouro pendurado da coroa por uma
# corrente fina e, no topo, o pequeno sol de oito raios. "Mediu o mundo com uma vara, e a vara é esta."
#
# Espaço do modelo (formato de assets/armas/modelos): metros, origem no centro da pegada, +Z da pegada para a
# cabeça, +X largura, +Y espessura. Materiais: emissivo = brilho; nome começando em "tinta" = cor do item.
#
# Uso: /opt/bpy42/bin/python cetro_demiurgo.py -- <saida_dir>
#   gera <saida>/cetro_do_demiurgo.glb (modelo), <saida>/cetro_render.png (prévia grande, fundo transparente)
#   e <saida>/cetro_cabeca.png (a coroa de perto, referência para o ícone).
import bpy, math, sys, os
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.read_factory_settings(use_empty=True)
from rig import mat, prim, along

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["/tmp/cetro"]
OUT = argv[0]; os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene

# ------------------------------------------------------------------ materiais
ESM = (.45, 1.0, .72)
ferro = mat("tinta_ferro_negro", (.045, .045, .05), 1, .42, dirt=.5, grime=.3)
ouro = mat("ouro_velho_cetro", (.6, .4, .12), 1, .32, dirt=.45, grime=.25)
latao = mat("latao_cetro", (.46, .3, .1), 1, .4, dirt=.55, grime=.3)
couro = mat("couro_cetro", (.04, .026, .02), .05, .5, dirt=.6)
obsid = mat("obsidiana_cetro", (.015, .015, .02), .3, .12, dirt=.3, grime=.1)
esmer = mat("brilho_esmeralda", (.12, .9, .55), 0, .08, emit=ESM, strength=7.0, dirt=0, grime=0)
esmer2 = mat("brilho_esmeralda_lasca", (.12, .9, .55), 0, .1, emit=ESM, strength=2.2, dirt=0, grime=0)
nucleo = mat("brilho_nucleo", (1, 1, 1), 0, .1, emit=(.85, 1, .92), strength=14.0, dirt=0, grime=0)

Z = Vector((0, 0, 1)); X = Vector((1, 0, 0)); Y = Vector((0, 1, 0))
objs = []
def P(z): return Vector((0, 0, z))

# ------------------------------------------------------------------ haste e pegada
objs.append(along("primitive_cylinder_add", ferro, P(-.56), P(.57), .016, vertices=12))
# embutido de ouro em espiral (6 voltas), feito de segmentos curtos
pts = []
for k in range(121):
    t = k / 120; a = t * math.pi * 2 * 6; z = -.5 + t * 1.0
    if -.15 < z < .15: pts.append(None); continue
    pts.append(Vector((math.cos(a) * .0165, math.sin(a) * .0165, z)))
for a_, b_ in zip(pts, pts[1:]):
    if a_ is None or b_ is None: continue
    objs.append(along("primitive_cylinder_add", ouro, a_, b_, .0032, vertices=5))
# pegada de couro com três anéis de ouro
objs.append(along("primitive_cylinder_add", couro, P(-.15), P(.15), .021, vertices=12))
for k in range(9):   # volta do couro
    objs.append(prim("primitive_torus_add", couro, P(-.14 + .035 * k), (1, 1, 1), major_radius=.021, minor_radius=.0035, major_segments=16, minor_segments=5))
for z in (-.155, 0, .155):
    objs.append(prim("primitive_torus_add", ouro, P(z), (1, 1, 1), major_radius=.022, minor_radius=.006, major_segments=20, minor_segments=8))
# faixas gravadas (runas: cubinhos de latão em volta)
for z in (-.34, .34):
    objs.append(prim("primitive_torus_add", latao, P(z), (1, 1, 1), major_radius=.019, minor_radius=.007, major_segments=20, minor_segments=8))
    for k in range(8):
        a = k * math.pi / 4
        objs.append(prim("primitive_cube_add", ouro, Vector((math.cos(a) * .025, math.sin(a) * .025, z)), (.004, .002, .006 if k % 2 else .004), rot=(0, 0, math.degrees(a))))

# ------------------------------------------------------------------ pomo: selo de obsidiana com sete entalhes
objs.append(along("primitive_cone_add", ferro, P(-.56), P(-.62), 1, radius1=.017, radius2=.03, vertices=12))
objs.append(prim("primitive_cylinder_add", obsid, P(-.635), (.036, .036, .012), vertices=24))
objs.append(prim("primitive_torus_add", ouro, P(-.635), (1, 1, 1), major_radius=.036, minor_radius=.004, major_segments=28, minor_segments=6))
for k in range(7):
    a = k * math.pi * 2 / 7
    objs.append(prim("primitive_cube_add", ouro, Vector((math.cos(a) * .03, math.sin(a) * .03, -.648)), (.004, .003, .003), rot=(0, 0, math.degrees(a))))
objs.append(prim("primitive_uv_sphere_add", ouro, P(-.655), (.012, .012, .008), segments=12, ring_count=8))

# ------------------------------------------------------------------ coroa: colar, sete garras, armilar, esmeralda
objs.append(along("primitive_cone_add", latao, P(.57), P(.63), 1, radius1=.018, radius2=.03, vertices=14))
objs.append(prim("primitive_torus_add", ouro, P(.63), (1, 1, 1), major_radius=.03, minor_radius=.006, major_segments=24, minor_segments=8))
C = P(.80)   # centro da esmeralda
for k in range(7):
    a = k * math.pi * 2 / 7; d = Vector((math.cos(a), math.sin(a), 0))
    curva = [P(.63) + d * .028, P(.70) + d * .07, P(.79) + d * .095, P(.88) + d * .085, P(.945) + d * .052, P(.975) + d * .03]
    for p0, p1 in zip(curva, curva[1:]):
        objs.append(along("primitive_cylinder_add", ouro, p0, p1, .0062, vertices=7))
    objs.append(prim("primitive_uv_sphere_add", ouro, curva[-1], (.009,) * 3, segments=10, ring_count=6))
    objs.append(prim("primitive_uv_sphere_add", ouro, curva[2], (.011, .011, .009), segments=10, ring_count=6))
# esfera armilar: três meridianos inclinados e o equador com lascas de esmeralda
for k, rot in enumerate(((90, 0, 0), (90, 0, 60), (90, 0, 120))):
    objs.append(prim("primitive_torus_add", latao, C, (1, 1, 1), rot=rot, major_radius=.068 - .004 * k, minor_radius=.0035, major_segments=40, minor_segments=6))
objs.append(prim("primitive_torus_add", ouro, C, (1, 1, 1), rot=(23, 0, 0), major_radius=.076, minor_radius=.0042, major_segments=44, minor_segments=6))
for k in range(7):
    a = k * math.pi * 2 / 7
    p = C + Vector((math.cos(a) * .076, math.sin(a) * .076 * math.cos(math.radians(23)), math.sin(a) * .076 * math.sin(math.radians(23))))
    objs.append(prim("primitive_uv_sphere_add", esmer2, p, (.0055,) * 3, segments=8, ring_count=6))
# esmeralda octaédrica (duas pirâmides) com o núcleo branco
objs.append(along("primitive_cone_add", esmer, C, C + P(.052), 1, radius1=.036, radius2=0, vertices=4))
objs.append(along("primitive_cone_add", esmer, C, C - P(.052), 1, radius1=.036, radius2=0, vertices=4))
objs.append(prim("primitive_uv_sphere_add", nucleo, C, (.012,) * 3, segments=12, ring_count=8))
# sol de oito raios no topo
T = P(1.0)
objs.append(along("primitive_cylinder_add", ouro, P(.975), T - P(.006), .005, vertices=8))
objs.append(prim("primitive_cylinder_add", ouro, T, (.018, .018, .004), rot=(90, 0, 0), vertices=20))
for k in range(8):
    a = k * math.pi / 4; d = Vector((math.cos(a), 0, math.sin(a)))
    objs.append(along("primitive_cone_add", ouro, T + d * .02, T + d * (.038 if k % 2 == 0 else .03), 1, radius1=.0035, radius2=0, vertices=6))
# prumo de ouro pendurado da coroa por uma corrente fina
A = Vector((.04, 0, .63)); B = Vector((.052, 0, .40))
for k in range(16):
    p = A.lerp(B, k / 15)
    objs.append(prim("primitive_torus_add", ferro, p, (1, 1, 1), rot=(0, 90 * (k % 2), 0), major_radius=.0045, minor_radius=.0012, major_segments=10, minor_segments=5))
objs.append(prim("primitive_uv_sphere_add", ouro, B - P(.012), (.011, .011, .013), segments=12, ring_count=8))
objs.append(along("primitive_cone_add", ouro, B - P(.02), B - P(.055), 1, radius1=.011, radius2=0, vertices=10))

for o in objs:
    if o.type == 'MESH' and o.data.materials and o.data.materials[0] is ferro: o.name = "tinta_" + o.name
bpy.context.view_layer.update()

# ------------------------------------------------------------------ .glb
for o in bpy.data.objects: o.select_set(o.type == 'MESH')
bpy.ops.export_scene.gltf(filepath=f"{OUT}/cetro_do_demiurgo.glb", export_format='GLB', use_selection=True, export_apply=True)

# ------------------------------------------------------------------ prévia (Cycles, fundo transparente)
sc.render.engine = 'CYCLES'; sc.cycles.samples = int(os.environ.get("AMOSTRAS", 96)); sc.cycles.use_denoising = False
try: sc.cycles.device = 'CPU'
except Exception: pass
sc.render.film_transparent = True
sc.view_settings.view_transform = 'Filmic' if 'Filmic' in [i.name for i in sc.view_settings.bl_rna.properties['view_transform'].enum_items] else 'AgX'
sc.view_settings.look = 'None'
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs["Color"].default_value = (.02, .022, .02, 1); w.node_tree.nodes["Background"].inputs["Strength"].default_value = .6
def luz(nome, tipo, loc, cor, en, size=1.0, alvo=Vector((0, 0, .45))):
    ld = bpy.data.lights.new(nome, tipo); ld.color = cor; ld.energy = en
    if tipo == 'AREA': ld.size = size
    lo = bpy.data.objects.new(nome, ld); sc.collection.objects.link(lo); lo.location = loc
    lo.rotation_euler = (alvo - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return lo
luz("chave", 'AREA', (1.2, -1.4, 1.6), (1, .85, .65), 260, 1.2)
luz("contra", 'AREA', (-1.3, 1.1, 1.3), (.6, 1, .8), 220, .8)
luz("baixo", 'POINT', (.4, -.8, -.3), (.9, .7, .5), 25)
cam = bpy.data.cameras.new("cam"); cam.lens = 85; co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
def enquadra(loc, alvo, rx, ry, arquivo):
    co.location = loc; co.rotation_euler = (Vector(alvo) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    sc.render.filepath = arquivo; bpy.ops.render.render(write_still=True)
# a arma inteira, de pé; a câmera rola 14 graus para a inclinação da prévia
def enquadra_rolado(loc, alvo, rx, ry, arquivo, rolo):
    co.location = loc; q = (Vector(alvo) - Vector(loc)).to_track_quat('-Z', 'Y'); e = q.to_euler(); co.rotation_euler = e
    co.rotation_euler.rotate_axis('Z', math.radians(rolo))
    sc.render.resolution_x, sc.render.resolution_y = rx, ry
    sc.render.filepath = arquivo; bpy.ops.render.render(write_still=True)
enquadra_rolado((2.3, -3.1, .95), (0, 0, .2), 900, 1500, f"{OUT}/cetro_render.png", 14)
# a coroa de perto (referência do ícone)
enquadra((.9, -1.25, 1.05), (.1, 0, .78), 900, 900, f"{OUT}/cetro_cabeca.png")
print("ok", OUT)
