# Arca do Primarca: o baú tecnomancer do Gustavo (armazém). Objeto de cenário renderizado na mesma
# câmera dos personagens (2:1, elevação 30°, azimute 45°, 64 px/m) e no formato de assets/ambiente/objetos.
# Uso: blender -b -P arca.py -- <saida_dir>      depois:  python3 arca_publicar.py <saida_dir> <destino>
import bpy, math, sys, os, json, random
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[sys.argv.index("--")+1]
bpy.ops.wm.read_factory_settings(use_empty=True)
from rig import mat, prim, along
sc = bpy.context.scene
VIOLETA = (.42, .18, 1)

wood = mat("carvalho_negro", (.11,.065,.035), 0, .7, dirt=.5, grime=.6)
wood2 = mat("carvalho_tabua", (.085,.05,.028), 0, .75, dirt=.5, grime=.6)
iron = mat("ferro_arca", (.08,.075,.07), 1, .55, dirt=.55, grime=.3)
brass = mat("latao_arca", (.6,.36,.1), 1, .3, dirt=.55, grime=.15)
brass_dk = mat("latao_escuro_arca", (.3,.17,.05), 1, .45, dirt=.5, grime=.2)
copper = mat("cobre_arca", (.45,.16,.06), 1, .4, dirt=.55, grime=.2)
dial = mat("mostrador_arca", (.5,.46,.36), 0, .6, dirt=.6, grime=0)
black = mat("preto_fosco", (.015,.013,.012), 0, .8, dirt=.9, grime=0)
rubber = mat("borracha_arca", (.025,.022,.02), 0, .6, dirt=.8, grime=0)
sand = mat("areia_arca", (.36,.29,.19), 0, .95, dirt=.6, grime=.2)
tube = mat("valvula_arca", (.6,.4,1), emit=VIOLETA, strength=3.5)
bulb = mat("vidro_arca", (.3,.18,.55), emit=VIOLETA, strength=.6)

W, D, H = .72, .42, .62     # meia largura, meia profundidade, altura do corpo
Z0 = .14                    # corpo erguido nos pés de garra
rnd = random.Random(5)
# corpo em tábuas horizontais
for k in range(5):
    z = Z0 + H*(k+.5)/5
    prim("primitive_cube_add", wood if k % 2 else wood2, (0, rnd.uniform(-.004,.004), z), (W, D, H/10 - .004))
# tampa abaulada
prim("primitive_cylinder_add", wood, (0, 0, Z0 + H), (D*.55, D*1.02, W), (0, 90, 0), vertices=32)
# cintas de ferro: verticais envolvendo corpo e tampa, horizontais na base e na boca
for x in (-W*.72, 0, W*.72):
    prim("primitive_cube_add", iron, (x, 0, Z0 + H/2), (.035, D + .012, H/2 + .005))
    prim("primitive_torus_add", iron, (x, 0, Z0 + H), (.55, 1, 1), (0, 90, 0), major_radius=D*1.02 + .012, minor_radius=.018, major_segments=32, minor_segments=6)
    for z in (Z0 + .08, Z0 + .3, Z0 + .52):
        for y in (-D - .016, D + .016):
            prim("primitive_uv_sphere_add", brass_dk, (x, y, z), (.013,)*3, segments=8, ring_count=5)
for z in (Z0 + .02, Z0 + H - .02):
    prim("primitive_cube_add", iron, (0, 0, z), (W + .012, D + .012, .025))
# cantoneiras de latão
for sx in (-1, 1):
    for sy in (-1, 1):
        for z in (Z0 + .06, Z0 + H - .06):
            prim("primitive_cube_add", brass, (sx*(W - .03), sy*(D - .03), z), (.05, .05, .07))
        # pés de garra
        f = Vector((sx*(W - .08), sy*(D - .08), 0))
        prim("primitive_cylinder_add", iron, f + Vector((0, 0, .09)), (.05, .05, .06), vertices=10)
        for a in (0, 2.1, 4.2):
            d = Vector((math.cos(a + (0 if sx > 0 else math.pi)), math.sin(a), 0))
            along("primitive_cone_add", iron, f + Vector((0, 0, .05)), f + d*.1 + Vector((0, 0, .0)), 1, radius1=.022, radius2=.004, vertices=6)
# frente (-Y): roda de cofre com mostrador numerado, dois manômetros e espelho de fechadura
F = -D - .02
c = Vector((0, F, Z0 + H*.5))
prim("primitive_cylinder_add", brass_dk, c, (.2, .2, .02), (90, 0, 0), vertices=40)
prim("primitive_cylinder_add", black, c + Vector((0, -.022, 0)), (.16, .16, .006), (90, 0, 0), vertices=40)
for k in range(24):
    a = k*math.pi/12; r0 = .135 if k % 2 else .12
    along("primitive_cylinder_add", dial, c + Vector((r0*math.cos(a), -.03, r0*math.sin(a))), c + Vector((.152*math.cos(a), -.03, .152*math.sin(a))), .004, vertices=4)
prim("primitive_torus_add", brass, c + Vector((0, -.025, 0)), (1, 1, 1), (90, 0, 0), major_radius=.19, minor_radius=.018, major_segments=40, minor_segments=8)
prim("primitive_cylinder_add", brass, c + Vector((0, -.05, 0)), (.05, .05, .03), (90, 0, 0), vertices=16)
for k in range(6):   # raios do volante
    a = k*math.pi/3 + .2
    p = c + Vector((.27*math.cos(a), -.08, .27*math.sin(a)))
    along("primitive_cylinder_add", brass, c + Vector((0, -.06, 0)), p, .012, vertices=8)
    prim("primitive_uv_sphere_add", brass_dk, p, (.026,)*3, segments=10, ring_count=6)
prim("primitive_torus_add", brass_dk, c + Vector((0, -.08, 0)), (1, 1, 1), (90, 0, 0), major_radius=.27, minor_radius=.01, major_segments=40, minor_segments=6)
for sx in (-1, 1):  # manômetros
    g = Vector((sx*.48, F, Z0 + H*.66))
    prim("primitive_cylinder_add", dial, g, (.075, .075, .015), (90, 0, 0), vertices=24)
    prim("primitive_torus_add", brass, g + Vector((0, -.012, 0)), (1, 1, 1), (90, 0, 0), major_radius=.078, minor_radius=.012, major_segments=24, minor_segments=6)
    a = .6 if sx > 0 else 2.2
    along("primitive_cylinder_add", black, g + Vector((0, -.02, 0)), g + Vector((.055*math.cos(a), -.02, .055*math.sin(a))), .004, vertices=4)
    along("primitive_cylinder_add", copper, g + Vector((0, 0, -.075)), g + Vector((0, 0, -.2)), .012, vertices=8)
key = Vector((.48, F, Z0 + H*.28))
prim("primitive_cube_add", brass_dk, key, (.05, .012, .07))
prim("primitive_cylinder_add", black, key + Vector((0, -.014, .015)), (.012, .012, .006), (90, 0, 0), vertices=10)
prim("primitive_cube_add", black, key + Vector((0, -.014, -.012)), (.005, .006, .018))
prim("primitive_cube_add", brass_dk, (-.48, F, Z0 + H*.28), (.07, .012, .05))   # placa: vela da Vigília
along("primitive_cylinder_add", brass, (-.48, F - .015, Z0 + H*.22), (-.48, F - .015, Z0 + H*.31), .009, vertices=6)
prim("primitive_cone_add", brass, (-.48, F - .015, Z0 + H*.34), (1, 1, 1), radius1=.01, radius2=0, depth=.03, vertices=6)
# topo: coroa de cinco válvulas roxas numa gaiola de latão (a mesma assinatura do Gustavo)
T = Vector((0, .0, Z0 + H + D*.55 - .02))
prim("primitive_cube_add", iron, T + Vector((0, 0, .02)), (.26, .1, .03))
for k in range(5):
    x = -.2 + .1*k; h = .2 if k == 2 else .15
    b = T + Vector((x, 0, .05))
    along("primitive_cylinder_add", brass, b, b + Vector((0, 0, .03)), .03, vertices=12)
    along("primitive_cylinder_add", bulb, b + Vector((0, 0, .03)), b + Vector((0, 0, .03 + h)), .026, vertices=12)
    along("primitive_cylinder_add", tube, b + Vector((0, 0, .045)), b + Vector((0, 0, .02 + h)), .011, vertices=8)
    prim("primitive_uv_sphere_add", bulb, b + Vector((0, 0, .03 + h)), (.026,)*3, segments=10, ring_count=6)
    along("primitive_cone_add", brass_dk, b + Vector((0, 0, .05 + h)), b + Vector((0, 0, .09 + h)), 1, radius1=.008, radius2=0, vertices=6)
for x in (-.27, .27):  # gaiola
    along("primitive_cylinder_add", brass, T + Vector((x, -.06, .03)), T + Vector((x, -.06, .3)), .009, vertices=6)
    along("primitive_cylinder_add", brass, T + Vector((x, .06, .03)), T + Vector((x, .06, .3)), .009, vertices=6)
for y in (-.06, .06):
    along("primitive_cylinder_add", brass, T + Vector((-.27, y, .3)), T + Vector((.27, y, .3)), .009, vertices=6)
# arco elétrico preso entre as pontas
p = T + Vector((-.2, 0, .27)); r2 = random.Random(3)
for k in range(1, 9):
    q = T + Vector((-.2 + .4*k/8, r2.uniform(-.02, .02), .27 + .05*math.sin(math.pi*k/8) + r2.uniform(-.02, .02)))
    along("primitive_cylinder_add", tube, p, q, .004, vertices=4); p = q
# lateral direita (+X): volante de válvula e canos descendo para a areia, feixe de cabos
s = Vector((W + .03, 0, Z0 + H*.55))
prim("primitive_cylinder_add", copper, s, (.045, .045, .04), (0, 90, 0), vertices=12)
along("primitive_cylinder_add", iron, s, s + Vector((.1, 0, 0)), .012, vertices=8)
prim("primitive_torus_add", iron, s + Vector((.11, 0, 0)), (1, 1, 1), (0, 90, 0), major_radius=.07, minor_radius=.01, major_segments=20, minor_segments=6)
for k in range(4):
    a = k*math.pi/2
    along("primitive_cylinder_add", iron, s + Vector((.11, 0, 0)), s + Vector((.11, .07*math.cos(a), .07*math.sin(a))), .006, vertices=4)
for y, r in ((-.2, .03), (.18, .024)):
    a = Vector((W, y, Z0 + .2)); b = Vector((W + .14, y, Z0 + .12)); e = Vector((W + .2, y, -.02))
    along("primitive_cylinder_add", copper, a, b, r, vertices=10); along("primitive_cylinder_add", copper, b, e, r, vertices=10)
    prim("primitive_torus_add", brass, b, (1, 1, 1), major_radius=r + .006, minor_radius=.007)
pts = [Vector((-W, .1, Z0 + H*.7)), Vector((-W - .12, .16, Z0 + .4)), Vector((-W - .2, .1, .02)), Vector((-W - .45, .25, -.01))]
for off in (0, .03, -.03):
    for a, b in zip(pts[:-1], pts[1:]):
        along("primitive_cylinder_add", rubber, a + Vector((0, off, 0)), b + Vector((0, off, 0)), .014, vertices=6)
# areia acumulada na base (some no alpha nas bordas)
mound = prim("primitive_uv_sphere_add", sand, (0, 0, -.08), (W + .3, D + .25, .1), segments=32, ring_count=12)

# câmera e luz iguais às dos personagens
PX, PPU, ELEV, AZ = 192, 64, 30, 45
TARGET = Vector((0, 0, .5))
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = PX/PPU
e, a, d = math.radians(ELEV), math.radians(AZ), 40
cam.location = TARGET + Vector((d*math.cos(e)*math.sin(a), -d*math.cos(e)*math.cos(a), d*math.sin(e)))
cam.rotation_euler = (TARGET - cam.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = cam
def sun(name, rgb, energy, rot):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN')); sc.collection.objects.link(l)
    l.data.color = rgb; l.data.energy = energy; l.data.angle = math.radians(8)
    l.rotation_euler = [math.radians(r) for r in rot]
sun("lua", (.85, .88, 1), 4.6, (52, 0, -30)); sun("rim", (1, .55, .3), 6.5, (-58, 0, -35)); sun("fill", (.32, .38, .6), 1.1, (65, 0, 140))
pl = bpy.data.objects.new("valv", bpy.data.lights.new("valv", 'POINT')); sc.collection.objects.link(pl)
pl.data.color = VIOLETA; pl.data.energy = 40; pl.location = T + Vector((0, -.3, .3))
sc.world = bpy.data.worlds.new("w"); sc.world.color = (.025, .025, .032)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 64; sc.cycles.use_denoising = False; sc.cycles.max_bounces = 3
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'
sc.render.film_transparent = True; sc.render.resolution_x = sc.render.resolution_y = PX*2
os.makedirs(out, exist_ok=True)
anchor = [PX/2, round(PX/2 + TARGET.z*math.cos(e)*PPU, 1)]
# a arca é vista de frente para a câmera (frente -Y gira para a tela), como os baús do kit
for o in sc.objects:
    if o.type == 'MESH': o.rotation_euler.z += 0  # já modelada com a frente em -Y
sc.render.filepath = f"{out}/arca_primarca.png"; bpy.ops.render.render(write_still=True)
json.dump({"anchor": anchor, "frame": [PX, PX]}, open(f"{out}/meta.json", "w"))
bpy.ops.wm.save_as_mainfile(filepath=f"{out}/arca_primarca.blend")
