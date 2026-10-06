# Renderiza um monstro em 8 direções para cada animação (quadros brutos em 2x).
# Uso: blender -b -P render.py -- <monstro> <saida_dir> [teste|anim1,anim2] [dirs ex. 0,1,3]
#   teste: só alguns quadros para conferir pose e luz.
import bpy, math, sys, os, json, importlib
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[sys.argv.index("--")+1:]
kind, out = argv[0], argv[1]
sel = argv[2] if len(argv) > 2 else ""
test = sel == "teste"; debug = sel == "debug"
only = set(sel.split(",")) if sel and not test and not debug else None
dirs_sel = [int(d) for d in argv[3].split(",")] if len(argv) > 3 else None
bpy.ops.wm.read_factory_settings(use_empty=True)
kind, _, var = kind.partition(":")
mod = importlib.import_module(kind)
if var: mod.set_variant(var)
name_out = var or kind
sc = bpy.context.scene

R, info = mod.build()
arm = R.arm
PX = info["px"]                 # tamanho final do quadro (renderiza em 2x)
PPU = 64                        # pixels por metro no sprite final (igual aos personagens)
ELEV, AZ = 30, 45               # isometria 2:1
TARGET = Vector((0, 0, info["target_z"]))
DIRS = ["S", "SE", "E", "NE", "N", "NW", "W", "SW"]

cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.type = 'ORTHO'; cam.data.ortho_scale = PX/PPU
e, a, d = math.radians(ELEV), math.radians(AZ), 40
cam.location = TARGET + Vector((d*math.cos(e)*math.sin(a), -d*math.cos(e)*math.cos(a), d*math.sin(e)))
cam.rotation_euler = (TARGET - cam.location).to_track_quat('-Z', 'Y').to_euler(); sc.camera = cam
def sun(name, rgb, energy, rot):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN')); sc.collection.objects.link(l)
    l.data.color = rgb; l.data.energy = energy; l.data.angle = math.radians(8)
    l.rotation_euler = [math.radians(r) for r in rot]
sun("lua", (.8, .86, 1), 3.4, (52, 0, -30))        # luz fria de cima, à esquerda da tela
sun("rim", info["rim"], info.get("rim_e", 6.0), (-58, 0, -35))        # contraluz à direita
sun("fill", (.3, .36, .55), .6, (65, 0, 140))
sc.world = bpy.data.worlds.new("w"); sc.world.color = (.012, .012, .016)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = info.get("samples", 32)
sc.cycles.use_denoising = info.get("denoise", False); sc.cycles.max_bounces = 3
sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = .02
sc.render.use_persistent_data = True
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'
sc.render.film_transparent = True; sc.render.resolution_x = sc.render.resolution_y = PX*2
sc.render.image_settings.color_mode = 'RGBA'
os.makedirs(out, exist_ok=True)

frames_by_anim = mod.anims(R)
meta = {"monstro": name_out, "frame_size": [PX, PX], "dirs": DIRS,
        "anchor": [PX/2, round(PX/2 + TARGET.z*math.cos(e)*PPU, 1)], "pixels_per_meter": PPU,
        "camera": {"elevation": ELEV, "azimuth": AZ}, "anims": {}}
for name, poses in frames_by_anim.items():
    n = len(poses)
    meta["anims"][name] = {"frames": n, "fps": info["fps"][name], "loop": name in info.get("loops", ("idle", "walk"))}
    if only and name not in only: continue
    act = R.action(name, poses)
    if debug:
        for f in range(1, n+1):
            sc.frame_set(f); pb = arm.pose.bones
            hz = {b: round(min(pb[b].head.z, pb[b].tail.z), 2) for b in ("hand.L", "hand.R") if b in pb}
            print("DBG", name, f, hz, "hips", round(pb[R.root].head.z, 2))
        continue
    frames = range(1, n+1); dirs = dirs_sel or range(8)
    if test: frames = sorted({1, n//2 + 1, n}); dirs = dirs_sel or [1]
    for f in frames:
        sc.frame_set(f)
        for k in dirs:
            arm.rotation_euler = (0, 0, math.radians((k+1)*45))
            sc.render.filepath = f"{out}/{name}/{DIRS[k]}_{f-1:02d}.png"
            bpy.ops.render.render(write_still=True)
json.dump(meta, open(f"{out}/meta.json", "w"), indent=1)
if not test and not only:
    arm.rotation_euler = (0, 0, 0)
    bpy.ops.wm.save_as_mainfile(filepath=f"{out}/{kind}.blend")
