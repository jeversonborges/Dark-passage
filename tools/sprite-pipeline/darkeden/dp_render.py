# Uso:
#   blender -b -P dp_render.py -- sprite <anjo|humano> <saida_dir> [px]
#   blender -b -P dp_render.py -- scene <saida.png>
import bpy, math, sys, os, random
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dp_models as M
argv = sys.argv[sys.argv.index("--")+1:]
mode = argv[0]
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def iso_cam(scale, target=(0,0,.85), elev=35, az=45):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = scale; cam.data.clip_end = 200
    e, a, d = math.radians(elev), math.radians(az), 40
    t = Vector(target)
    cam.location = t + Vector((d*math.cos(e)*math.sin(a), -d*math.cos(e)*math.cos(a), d*math.sin(e)))
    cam.rotation_euler = (t - cam.location).to_track_quat('-Z','Y').to_euler()
    sc.camera = cam; return cam

def sun(name, rgb, energy, rot, angle=.1):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN')); sc.collection.objects.link(l)
    l.data.color = rgb; l.data.energy = energy; l.data.angle = angle
    l.rotation_euler = [math.radians(r) for r in rot]; return l

def point(loc, rgb, energy, radius=.1):
    l = bpy.data.objects.new("p", bpy.data.lights.new("p", 'POINT')); sc.collection.objects.link(l)
    l.data.color = rgb; l.data.energy = energy; l.data.shadow_soft_size = radius; l.location = loc

def base_render(samples):
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = samples
    sc.cycles.use_denoising = False; sc.cycles.max_bounces = 4
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'

if mode == "sprite":
    kind, out = argv[1], argv[2]; px = int(argv[3]) if len(argv) > 3 else 112
    root = M.make_root("root"); getattr(M, kind)(root)
    iso_cam(2.5, (0,0,.95))
    sun("key", (.9,.92,1), 3.2, (50,0,-35))                    # lua fria
    sun("rim", (1,.45,.2) if kind=="humano" else (.9,.3,.25), 2.2, (-55,0,165))
    sun("fill", (.3,.35,.5), .5, (70,0,110))
    sc.world = bpy.data.worlds.new("w"); sc.world.color = (.01,.01,.012)
    base_render(80); sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = px*2
    os.makedirs(out, exist_ok=True)
    for i in range(8):
        root.rotation_euler = (0,0,math.radians(i*45))
        sc.render.filepath = f"{out}/dir_{i}.png"; bpy.ops.render.render(write_still=True)
    sys.exit()

# ---------------- cena: rua em ruínas de uma cidade do Leste Europeu, à noite
out = argv[1]; rnd = random.Random(4)
def nodemat(name, build):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]; build(nt, b); return m

def cobble(nt, b):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    v = nt.nodes.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = 2.6; v.feature = 'DISTANCE_TO_EDGE'
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = .35
    nt.links.new(tc.outputs["Object"], v.inputs["Vector"]); nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB"); r.color_ramp.elements[0].position = 0; r.color_ramp.elements[0].color = (.008,.008,.008,1)
    r.color_ramp.elements[1].position = .12; r.color_ramp.elements[1].color = (.07,.065,.06,1)
    r2 = nt.nodes.new("ShaderNodeValToRGB"); r2.color_ramp.elements[0].position=.45; r2.color_ramp.elements[0].color=(1,1,1,1)
    r2.color_ramp.elements[1].position=.62; r2.color_ramp.elements[1].color=(.35,.3,.22,1)   # lama
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1
    nt.links.new(v.outputs["Distance"], r.inputs[0]); nt.links.new(n.outputs["Fac"], r2.inputs[0])
    nt.links.new(r.outputs[0], mx.inputs[6]); nt.links.new(r2.outputs[0], mx.inputs[7])
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .35
    nt.links.new(r.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs[0], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = .85

def brick(nt, b):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    t = nt.nodes.new("ShaderNodeTexBrick"); t.inputs["Scale"].default_value = 3.5
    nt.links.new(tc.outputs["Object"], t.inputs["Vector"])
    t.inputs["Color1"].default_value = (.1,.045,.03,1); t.inputs["Color2"].default_value = (.07,.035,.025,1)
    t.inputs["Mortar"].default_value = (.03,.03,.03,1)
    nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .5
    nt.links.new(t.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = .9

ground = nodemat("calcamento", cobble)
bricks = nodemat("tijolo", brick)
iron = M.mat("ferro", (.05,.05,.05), 1, .5)
rust = M.mat("ferrugem", (.15,.06,.03), .4, .8)
sand = M.mat("saco_areia", (.09,.08,.055), 0, 1)
wood = M.mat("madeira_podre", (.07,.05,.035), 0, .8)
blood = M.mat("poca_sangue", (.045,0,.002), .1, .12)
fire = M.mat("fogo", (1,.3,.05), emit=(1,.28,.03), strength=10)
grey = M.mat("cadaver", (.18,.17,.16), 0, .7)

bpy.ops.mesh.primitive_plane_add(size=40); bpy.context.object.data.materials.append(ground)
def cube(m, loc, sc_, rot=0):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=(0,0,math.radians(rot))); o = bpy.context.object
    o.scale = sc_; o.data.materials.append(m); return o
# muros em ruínas (alturas quebradas)
for i in range(9):
    h = rnd.uniform(.4, 2.4); cube(bricks, (-4.5 + i*.6, 4.2, h/2), (.3,.25,h/2))
for i in range(6):
    h = rnd.uniform(.3, 1.8); cube(bricks, (4.6, 3.6 - i*.6, h/2), (.25,.3,h/2))
for i in range(10):  # entulho
    cube(bricks, (rnd.uniform(-4,4.5), rnd.uniform(2.5,4), .08), (rnd.uniform(.1,.25),.1,.08), rnd.uniform(0,90))
# barricada de sacos de areia com arame farpado
for row in range(2):
    for i in range(6):
        bpy.ops.mesh.primitive_uv_sphere_add(location=(1.2+i*.42+row*.2, -2.6, .12+row*.2)); o = bpy.context.object
        o.scale = (.24,.15,.11); o.data.materials.append(sand); bpy.ops.object.shade_smooth()
for i in range(12):
    bpy.ops.mesh.primitive_torus_add(location=(1.1+i*.22, -2.6, .62), rotation=(rnd.uniform(-.3,.3), math.radians(90), rnd.uniform(-.2,.4)), major_radius=.14, minor_radius=.006)
    bpy.context.object.data.materials.append(iron)
# poste de luz quebrado e tonel com fogo
bpy.ops.mesh.primitive_cylinder_add(radius=.05, depth=1.4, location=(-3.4,2.2,1.0), rotation=(math.radians(25),0,math.radians(30))); bpy.context.object.data.materials.append(iron)
bpy.ops.mesh.primitive_cylinder_add(radius=.25, depth=.75, location=(3.2,-1.2,.37)); bpy.context.object.data.materials.append(rust)
for k in range(7):
    bpy.ops.mesh.primitive_cone_add(radius1=rnd.uniform(.05,.1), depth=rnd.uniform(.25,.55), vertices=6,
        location=(3.2+rnd.uniform(-.12,.12), -1.2+rnd.uniform(-.12,.12), .85), rotation=(rnd.uniform(-.3,.3), rnd.uniform(-.3,.3), 0))
    bpy.context.object.data.materials.append(fire)
point((3.2,-1.2,1.3), (1,.45,.12), 450, .3)
# cemitério: cruzes tortas
for i in range(5):
    x, y = -4.2 + i*.75, -3.3 + rnd.uniform(-.3,.3); t = rnd.uniform(-15,15)
    a = cube(wood, (x,y,.5), (.05,.05,.5)); b_ = cube(wood, (x,y,.75), (.25,.05,.045))
    for o in (a,b_): o.rotation_euler = (math.radians(rnd.uniform(-10,10)), math.radians(t), 0)
# árvore morta
def branch(p, d, L, r, depth):
    q = p + d*L
    M.along("primitive_cylinder_add", wood, p, q, r, None, vertices=6)
    if depth:
        for s in (-1,1):
            nd = (d + Vector((rnd.uniform(-.8,.8), rnd.uniform(-.8,.8), .2))).normalized()
            branch(q, nd, L*.7, r*.65, depth-1)
branch(Vector((-3.8,3.2,0)), Vector((0,0,1)), 1.3, .09, 4)
# cadáver e poças de sangue
rc = M.make_root("cadaver", (2.0,-.2,.17)); rc.rotation_euler = (math.radians(-88), 0, math.radians(110)); M.humano(rc)
for (x,y,r) in [(1.9,-.3,.45),(2.25,-.05,.3),(1.6,-.5,.22),(.15,1.9,.18),(-1.0,-.2,.2),(-.85,-.35,.12),(1.5,-.2,.15),(-.2,-.9,.1)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=.01, location=(x,y,.005), vertices=24); o = bpy.context.object
    o.scale = (1, rnd.uniform(.5,.9), 1); o.data.materials.append(blood)

# personagens frente a frente
pa, ph = Vector((-1.5,-1.0,0)), Vector((.6,.9,0))
toward_cam = Vector((1.4,-1.4,0))
def face(frm, to):
    d = to - frm; return math.atan2(d.x, -d.y)
ra = M.make_root("anjo", pa, face(pa, ph + toward_cam)); M.anjo(ra)
rh = M.make_root("humano", ph, face(ph, pa + toward_cam)); M.humano(rh)
point(pa + Vector((0,.3,1.9)), (1,.6,.25), 40, .1)       # brilho do halo
point(ph + Vector((.25,-.1,.9)), (.4,1,.15), 25, .05)    # lanterna ácida

iso_cam(7.2, (-.1,-.1,.6))
sun("lua", (.55,.65,1), 1.8, (40,0,-50), .05)
sun("contra", (.8,.2,.12), 1.5, (-50,0,170))
sc.world = bpy.data.worlds.new("w"); sc.world.color = (.012,.014,.02)
sc.world.mist_settings.start = 30; sc.world.mist_settings.depth = 25
base_render(96)
sc.render.resolution_x, sc.render.resolution_y = 1280, 800
sc.view_layers[0].use_pass_mist = True
sc.use_nodes = True; nt = sc.node_tree
rl = nt.nodes["Render Layers"]; comp = nt.nodes["Composite"]
mix = nt.nodes.new("CompositorNodeMixRGB"); mix.inputs[2].default_value = (.03,.035,.045,1)
mr = nt.nodes.new("CompositorNodeMath"); mr.operation = 'MULTIPLY'; mr.inputs[1].default_value = .8
nt.links.new(rl.outputs["Mist"], mr.inputs[0]); nt.links.new(mr.outputs[0], mix.inputs[0])
nt.links.new(rl.outputs["Image"], mix.inputs[1]); nt.links.new(mix.outputs[0], comp.inputs["Image"])
sc.render.filepath = out; bpy.ops.render.render(write_still=True)
