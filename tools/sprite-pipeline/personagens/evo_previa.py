# Prévia rápida de personagens (sem a folha completa): um quadro parado em close e no tamanho do jogo.
# Uso: blender -b -P evo_previa.py -- <saida_dir> <tipo> [tipo...]   (tipos de render.py ou de evolucoes.py)
# Gera <saida>/<tipo>_close.png (S e SE em alta) e <tipo>_jogo.png (SE em 2x, para reduzir como no jogo).
import bpy, math, sys, os
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
argv = sys.argv[sys.argv.index("--")+1:]
out, kinds = argv[0], argv[1:]
os.makedirs(out, exist_ok=True)
for kind in kinds:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    import classes, classes2, classes3, anims, evolucoes, importlib
    for _k in ("demonio", "cultista", "mutante", "tecnomancer"): setattr(classes, _k, getattr(classes2, _k))
    classes.mutante = classes3.mutante
    fn = getattr(evolucoes, kind, None) or getattr(classes, kind)
    sc = bpy.context.scene
    arm, info = fn()
    style = info.get("anim", "melee"); base = info.get("base", kind)
    if base in ("anjo", "demonio") or info.get("fly"): acts = anims.flyer_anims(arm, info.get("extra"))
    elif style == "melee": acts = anims.anjo_anims(arm, info.get("extra"))
    elif style == "gun": acts, _ = anims.humano_anims(arm, info.get("flash"))
    elif style == "dual": acts, _ = anims.humano_dual_anims(arm)
    elif style == "besta": acts, _ = anims.humano_besta_anims(arm)
    else: acts, _ = anims.caster_anims(arm, info.get("extra"), info.get("hold_extra"))
    for o in [info.get("flash")] + [f[0] for f in info.get("fx", [])]:
        if o: o.hide_render = True
    pose = os.environ.get("POSE", "idle"); arm.animation_data.action = acts[pose]
    sc.frame_set(int(os.environ.get("FRAME", 1)))
    VW = float(os.environ.get("VIEW", 1)); T = Vector((0, 0, 1.05*VW))
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'; sc.camera = cam
    def sun(name, rgb, energy, rot):
        l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN')); sc.collection.objects.link(l)
        l.data.color = rgb; l.data.energy = energy; l.data.angle = math.radians(8)
        l.rotation_euler = [math.radians(r) for r in rot]
    sun("lua", (.85,.88,1), 4.6, (52,0,-30)); sun("rim", info["rim"], 7.5, (-58,0,-35)); sun("fill", (.32,.38,.6), 1.1, (65,0,140))
    sc.world = bpy.data.worlds.new("w"); sc.world.color = (.025,.025,.032)
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = int(os.environ.get("SAMPLES", 48))
    sc.cycles.use_denoising = False; sc.cycles.max_bounces = 3
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'
    sc.render.film_transparent = True; sc.render.image_settings.color_mode = 'RGBA'
    e = math.radians(30)
    for tag, k, size, res in (("close_S", 0, 3.0, 900), ("close_SE", 1, 3.0, 900), ("jogo", 1, 3.0, 384)):
        a = math.radians(45)
        cam.data.ortho_scale = size*VW
        cam.location = T + Vector((40*math.cos(e)*math.sin(a), -40*math.cos(e)*math.cos(a), 40*math.sin(e)))
        cam.rotation_euler = (T - cam.location).to_track_quat('-Z','Y').to_euler()
        arm.rotation_euler = (0, 0, math.radians((k+1)*45))
        sc.render.resolution_x = sc.render.resolution_y = res
        sc.render.filepath = f"{out}/{kind}_{tag}.png"
        bpy.ops.render.render(write_still=True)
    print("OK", kind)
