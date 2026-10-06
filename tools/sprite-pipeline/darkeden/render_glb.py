# Renderiza um modelo .glb rigado (com animações) em 8 direções na luz do DARK PASSAGE.
# Uso: blender -b -P render_glb.py -- <modelo.glb> <saida_dir> [acao] [frame] [px]
import bpy, math, sys, os
from mathutils import Vector
argv = sys.argv[sys.argv.index("--")+1:]
src, out = argv[0], argv[1]
action = argv[2] if len(argv) > 2 else None; frame = int(argv[3]) if len(argv) > 3 else 1
px = int(argv[4]) if len(argv) > 4 else 112
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
bpy.ops.import_scene.gltf(filepath=src)
for o in list(sc.objects):  # remove malhas auxiliares que não aparecem no jogo
    if o.type == 'MESH' and (o.hide_render or o.hide_get() or not o.material_slots or o.name.startswith("Icosphere")):
        bpy.data.objects.remove(o)
objs = list(sc.objects)
root = bpy.data.objects.new("root", None); sc.collection.objects.link(root)
for o in objs:
    if o.parent is None: o.parent = root
arm = next((o for o in objs if o.type == 'ARMATURE'), None)
if arm and action and action in bpy.data.actions:
    arm.animation_data_create(); arm.animation_data.action = bpy.data.actions[action]
sc.frame_set(frame); bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); pts = []
for o in objs:
    if o.type == 'MESH':
        ev = o.evaluated_get(dg); me = ev.to_mesh()
        pts += [ev.matrix_world @ v.co for v in me.vertices]; ev.to_mesh_clear()
zs = sorted(p.z for p in pts); zmin, zmax = zs[len(zs)//500], zs[-1-len(zs)//500]  # ignora vértices soltos
s = 1.8 / (zmax - zmin); root.scale = (s, s, s); root.location.z = -zmin*s
# escurece e dessatura os materiais (clima Dark Eden)
for m in bpy.data.materials:
    if m.use_nodes and "Principled BSDF" in m.node_tree.nodes:
        b = m.node_tree.nodes["Principled BSDF"]; nt = m.node_tree
        hsv = nt.nodes.new("ShaderNodeHueSaturation"); hsv.inputs["Saturation"].default_value = .75; hsv.inputs["Value"].default_value = .9
        link = next((l for l in nt.links if l.to_socket == b.inputs["Base Color"]), None)
        if link: nt.links.new(link.from_socket, hsv.inputs["Color"])
        else: hsv.inputs["Color"].default_value = b.inputs["Base Color"].default_value
        nt.links.new(hsv.outputs["Color"], b.inputs["Base Color"])
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.5
e, a, d = math.radians(35), math.radians(45), 30; t = Vector((0,0,.95))
cam.location = t + Vector((d*math.cos(e)*math.sin(a), -d*math.cos(e)*math.cos(a), d*math.sin(e)))
cam.rotation_euler = (t - cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera = cam
for name, rgb, en, rot in [("key",(.9,.92,1),4.5,(50,0,-35)),("rim",(.9,.3,.25),1.5,(-55,0,165)),("fill",(.3,.35,.5),.5,(70,0,110))]:
    l = bpy.data.objects.new(name, bpy.data.lights.new(name,'SUN')); sc.collection.objects.link(l)
    l.data.color = rgb; l.data.energy = en; l.rotation_euler = [math.radians(r) for r in rot]
sc.world = bpy.data.worlds.new("w"); sc.world.color = (.01,.01,.012)
sc.render.engine = 'CYCLES'; sc.cycles.samples = 64; sc.cycles.use_denoising = False
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'
sc.render.film_transparent = True; sc.render.resolution_x = sc.render.resolution_y = px*2
os.makedirs(out, exist_ok=True)
for i in range(8):
    root.rotation_euler = (0,0,math.radians(i*45))
    sc.render.filepath = f"{out}/dir_{i}.png"; bpy.ops.render.render(write_still=True)
print("ACTIONS:", [a.name for a in bpy.data.actions])
