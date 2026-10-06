# Renderiza um personagem em 8 direções para cada animação.
# Uso: blender -b -P render.py -- <anjo|humano> <saida_dir> [teste]
#   teste: renderiza só alguns quadros para conferir pose e luz.
import bpy, math, sys, os, json
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[sys.argv.index("--")+1:]
kind, out = argv[0], argv[1]; test = len(argv) > 2
bpy.ops.wm.read_factory_settings(use_empty=True)
import classes, anims
from classes2 import *  # demonio, cultista, mutante, tecnomancer
import classes2
for _k in ("demonio", "cultista", "mutante", "tecnomancer"): setattr(classes, _k, getattr(classes2, _k))
sc = bpy.context.scene

PX = 192           # tamanho final do quadro (renderiza em 2x)
PPU = 64           # pixels por metro no sprite final (~100 px de altura)
ELEV, AZ = 30, 45  # isometria 2:1
TARGET = Vector((0, 0, 1.0))
DIRS = ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]  # direção para onde o personagem olha na tela

arm, info = getattr(classes, kind)()
style = info.get("anim", "melee"); flash = info.get("flash"); flash_frames = None
if style == "melee": acts = anims.anjo_anims(arm, info.get("extra"))
elif style == "gun": acts, flash_frames = anims.humano_anims(arm, flash)
elif style == "dual": acts, flash_frames = anims.humano_dual_anims(arm)
else: acts, flash_frames = anims.caster_anims(arm, info.get("extra"), info.get("hold_extra"))
if flash and not flash_frames: flash_frames = [0]*8
if flash and not isinstance(flash_frames, dict): flash_frames = {"attack": flash_frames}

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = PX/PPU
e, a, d = math.radians(ELEV), math.radians(AZ), 40
cam.location = TARGET + Vector((d*math.cos(e)*math.sin(a), -d*math.cos(e)*math.cos(a), d*math.sin(e)))
cam.rotation_euler = (TARGET - cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera = cam
def sun(name, rgb, energy, rot):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN')); sc.collection.objects.link(l)
    l.data.color = rgb; l.data.energy = energy; l.data.angle = math.radians(8)
    l.rotation_euler = [math.radians(r) for r in rot]
sun("lua", (.85,.88,1), 4.6, (52,0,-30))          # luz fria de cima, à esquerda da tela
sun("rim", info["rim"], 7.5, (-58,0,-35))         # contraluz da facção, à direita
sun("fill", (.32,.38,.6), 1.1, (65,0,140))
sc.world = bpy.data.worlds.new("w"); sc.world.color = (.025,.025,.032)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 40
sc.cycles.use_denoising = False; sc.cycles.max_bounces = 3
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'
sc.render.film_transparent = True; sc.render.resolution_x = sc.render.resolution_y = PX*2
sc.render.image_settings.color_mode = 'RGBA'
os.makedirs(out, exist_ok=True)

meta = {"classe": kind, "frame_size": [PX, PX], "dirs": DIRS,
        "anchor": [PX/2, round(PX/2 + TARGET.z*math.cos(e)*PPU, 1)], "pixels_per_meter": PPU,
        "camera": {"elevation": ELEV, "azimuth": AZ}, "anims": {}}
for name, act in acts.items():
    if os.environ.get("ONLY") and name not in os.environ["ONLY"].split(","): continue
    arm.animation_data.action = act
    n = int(act.frame_range[1])
    frames = range(1, n+1)
    dirs = range(8)
    if test: frames, dirs = ((list(range(1, n+1)), [1]) if argv[2] == "se" else ([1, n//2 + 1] if name != "idle" else [], [0, 1, 3]))
    meta["anims"][name] = {"frames": n, "fps": round({"idle": 4, "walk": 10*n/8, "attack": 12*n/8, "shoot": 12, "spin": 14, "dash": 18}[name]),
                           "loop": name not in ("attack", "shoot", "spin", "dash")}
    for f in frames:
        sc.frame_set(f)
        if flash: flash.hide_render = not (name in flash_frames and flash_frames[name][f-1])
        for fo, fa, ff in info.get("fx", []): fo.hide_render = not (name == fa and ff[f-1])
        for k in dirs:
            arm.rotation_euler = (0, 0, math.radians((k+1)*45))
            sc.render.filepath = f"{out}/{name}/{DIRS[k]}_{f-1:02d}.png"
            bpy.ops.render.render(write_still=True)
json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)
if not test:
    arm.rotation_euler = (0, 0, 0)
    if flash: flash.hide_render = False
    bpy.ops.wm.save_as_mainfile(filepath=f"{out}/{kind}.blend")
    for o in sc.objects: o.select_set(o.type in ('ARMATURE', 'MESH') and o not in [flash] + [fx[0] for fx in info.get('fx', [])])
    bpy.ops.export_scene.gltf(filepath=f"{out}/{kind}.glb", use_selection=True, export_animations=True,
                              export_force_sampling=True)
