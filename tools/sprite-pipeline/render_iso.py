# Blender headless: renderiza um modelo em 8 direções com câmera isométrica.
# Uso: blender -b -P render_iso.py -- <saida_dir> [tamanho_px]
import bpy, math, sys, os
argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
out = argv[0] if argv else "out"; size = int(argv[1]) if len(argv) > 1 else 96
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
# Placeholder: "cavaleiro" simples (troque por import de .glb/.fbx)
bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=1.2, location=(0,0,0.6))
body = bpy.context.object
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0,0,1.45))
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.45,0,0.8)); sword = bpy.context.object
sword.scale = (0.05, 0.05, 0.9)
mat = bpy.data.materials.new("armor"); mat.diffuse_color = (0.25,0.22,0.3,1)
for o in bpy.context.scene.objects: o.data.materials.append(mat)
root = bpy.data.objects.new("root", None); sc.collection.objects.link(root)
for o in list(sc.objects):
    if o is not root: o.parent = root
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.4
cam.rotation_euler = (math.radians(60), 0, math.radians(45))
d = 10; cam.location = (d*math.sin(math.radians(60))*math.sin(math.radians(45)), -d*math.sin(math.radians(60))*math.cos(math.radians(45)), 0.8 + d*math.cos(math.radians(60)))
sc.camera = cam
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", 'SUN')); sc.collection.objects.link(sun)
sun.rotation_euler = (math.radians(50), 0, math.radians(-30)); sun.data.energy = 3
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'; sc.display.shading.color_type = 'MATERIAL'
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = size
sc.render.filter_size = 0.0  # sem anti-aliasing: visual pixelado
os.makedirs(out, exist_ok=True)
for i in range(8):
    root.rotation_euler = (0, 0, math.radians(i*45))
    sc.render.filepath = os.path.join(out, f"dir_{i}.png")
    bpy.ops.render.render(write_still=True)
