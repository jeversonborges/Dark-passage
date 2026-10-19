# Prévia rápida da malha (sem rig): render de argila no Workbench, perfil e três quartos.
# Uso: /opt/bpy42/bin/python previa_malha.py -- <pasta de saída>
import bpy, math, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mathutils import Vector
from malha import build_malha

out = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
build_malha()
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
sc.cycles.device = 'CPU'
sc.cycles.samples = 24
sc.render.resolution_x = sc.render.resolution_y = 900
sc.render.film_transparent = False
sc.world = bpy.data.worlds.new("w"); sc.world.color = (.08, .08, .09)
sun = bpy.data.objects.new("sol", bpy.data.lights.new("sol", 'SUN')); sc.collection.objects.link(sun)
sun.rotation_euler = (math.radians(55), 0, math.radians(35))
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = 4.6; sc.camera = cam
alvo = Vector((0, -.45, 1.0))
for nome, az in (("perfil", 90), ("tres_quartos", 45)):
    a = math.radians(az)
    cam.location = alvo + Vector((6*math.cos(a)*0 + 6*math.sin(a), -6*math.cos(a), 1.0))
    cam.rotation_euler = (alvo - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = os.path.join(out, nome + ".png")
    bpy.ops.render.render(write_still=True)
    print("ok", nome)
