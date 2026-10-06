# Blender headless: visual de MMORPG anos 2000 (Dark Eden / MU / Lineage).
# Sprite pré-renderizado em 3D: luz dramática, rim light colorido, sombra
# no chão, brilho em armas, 8 direções. Uso:
#   blender -b -P render_2000s.py -- <anjo|demonio> <saida_dir> [px]
import bpy, math, sys, os
from mathutils import Vector
argv = sys.argv[sys.argv.index("--")+1:]
kind, out = argv[0], argv[1]; size = int(argv[2]) if len(argv) > 2 else 128
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
root = bpy.data.objects.new("root", None); sc.collection.objects.link(root)

def mat(name, rgb, metal=0.0, rough=0.5, emit=None, strength=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m

def add(op, m, loc, scale=(1,1,1), rot=(0,0,0), **kw):
    getattr(bpy.ops.mesh, op)(location=loc, rotation=[math.radians(r) for r in rot], **kw)
    o = bpy.context.object; o.scale = scale; o.data.materials.append(m); o.parent = root
    bpy.ops.object.shade_smooth(); return o

def humanoid(armor, cloth, skin):
    add("primitive_cylinder_add", armor, (0,0,0.95), (0.26,0.18,0.32), vertices=12)        # torso
    add("primitive_cone_add", cloth, (0,0,0.45), (0.32,0.26,0.45), vertices=12)            # saia/túnica
    for s in (-1, 1):
        add("primitive_cylinder_add", armor, (0.11*s,0,0.25), (0.08,0.08,0.25), vertices=8)  # pernas
        add("primitive_uv_sphere_add", armor, (0.3*s,0,1.22), (0.14,0.13,0.11))            # ombreiras
        add("primitive_cylinder_add", armor, (0.33*s,0,0.95), (0.06,0.06,0.22), vertices=8)  # braços
    add("primitive_uv_sphere_add", skin, (0,0,1.42), (0.12,0.12,0.14))                     # cabeça

if kind == "anjo":   # Arautos: branco osso, ouro sujo, vermelho sangue
    armor = mat("osso", (0.78,0.74,0.66), 0.6, 0.35)
    gold = mat("ouro", (0.55,0.4,0.15), 1.0, 0.3)
    red = mat("sangue", (0.12,0.015,0.015), 0, 0.85)
    holy = mat("luz", (1,0.95,0.8), emit=(1,0.85,0.5), strength=6)
    humanoid(armor, red, armor)
    add("primitive_torus_add", holy, (0,0,1.62), (0.12,0.12,0.12), major_radius=1, minor_radius=0.12)  # halo
    for s in (-1, 1):  # asas
        add("primitive_cone_add", armor, (0.22*s,0.2,1.2), (0.05,0.28,0.38), (20,0,30*s), vertices=4)
    add("primitive_cube_add", holy, (0.42,-0.05,1.0), (0.025,0.025,0.55))                  # espada
    add("primitive_cube_add", gold, (0.42,-0.05,0.5), (0.12,0.03,0.025))
    rim = (1.0,0.75,0.4)
else:                # Vigília/Demônio: placas negras com brasas
    armor = mat("negro", (0.05,0.045,0.05), 0.8, 0.4)
    ember = mat("brasa", (0.3,0.05,0), emit=(1,0.3,0.05), strength=8)
    skin = mat("pele", (0.09,0.02,0.02), 0, 0.6)
    humanoid(armor, armor, skin)
    for s in (-1, 1):
        add("primitive_cone_add", mat("chifre",(0.12,0.1,0.08),0,0.5), (0.09*s,0,1.58), (0.04,0.04,0.16), (0,-30*s,0), vertices=6)
        add("primitive_cone_add", skin, (0.24*s,0.22,1.25), (0.03,0.32,0.34), (20,0,30*s), vertices=3)  # asas rasgadas
    add("primitive_cube_add", ember, (0,-0.19,1.0), (0.12,0.01,0.05))                      # fenda no peito
    add("primitive_cylinder_add", armor, (0.45,-0.05,1.0), (0.025,0.025,0.75))             # cabo da foice
    add("primitive_cone_add", ember, (0.3,-0.05,1.72), (0.03,0.3,0.05), (0,90,0), vertices=3)
    rim = (1.0,0.3,0.05)

# Câmera isométrica clássica (~30° de elevação da época de Lineage/Dark Eden)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.1
elev, az, d = math.radians(35), math.radians(45), 12
cam.location = Vector((d*math.cos(elev)*math.sin(az), -d*math.cos(elev)*math.cos(az), 0.85 + d*math.sin(elev)))
cam.rotation_euler = (Vector((0,0,0.85)) - cam.location).to_track_quat('-Z','Y').to_euler()
sc.camera = cam

def light(kind_, rgb, energy, rot, size_=0.2):
    l = bpy.data.objects.new(kind_, bpy.data.lights.new(kind_, 'SUN')); sc.collection.objects.link(l)
    l.data.color = rgb; l.data.energy = energy; l.data.angle = size_
    l.rotation_euler = [math.radians(r) for r in rot]
light("key", (1,0.92,0.82), 3.5, (45,0,-40))           # luz principal fria do alto
light("rim", rim, 6.0, (-60,0,160))                    # contraluz colorido da facção
light("fill", (0.35,0.4,0.6), 0.6, (70,0,120))         # preenchimento azulado e fraco
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.01,0.01,0.015)


sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
sc.cycles.samples = 96; sc.cycles.use_denoising = False
sc.render.film_transparent = True
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'
sc.render.resolution_x = sc.render.resolution_y = size * 2   # supersample, reduz depois
os.makedirs(out, exist_ok=True)
for i in range(8):
    root.rotation_euler = (0, 0, math.radians(i*45))
    sc.render.filepath = os.path.join(out, f"dir_{i}.png")
    bpy.ops.render.render(write_still=True)
