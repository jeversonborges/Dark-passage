# Cenário da área inicial do DARK PASSAGE, pré-renderizado como nos jogos da época.
#   blender -b -P dp_world.py -- props  <layout.json> <saida_dir>          # um sprite por tipo de objeto
#   blender -b -P dp_world.py -- ground <layout.json> <mascara.png> <saida.png>   # chão com sombras dos objetos
# Mesma câmera dos personagens: ortográfica, 35° de elevação, 45° de azimute, 44,8 px por metro.
import bpy, math, sys, os, json, random
from mathutils import Vector
sys.path.insert(0, "/mnt/project-files/tools/sprite-pipeline/darkeden")
import dp_models as M
from dp_models import mat, prim, along, chain

argv = sys.argv[sys.argv.index("--")+1:]
mode, layout = argv[0], json.load(open(argv[1]))
PXM = 44.8                     # pixels por metro no jogo
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene

def nodemat(name, build):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]; build(nt, b); return m

def brick(nt, b):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    t = nt.nodes.new("ShaderNodeTexBrick"); t.inputs["Scale"].default_value = 3.5
    nt.links.new(tc.outputs["Object"], t.inputs["Vector"])
    t.inputs["Color1"].default_value = (.1,.045,.03,1); t.inputs["Color2"].default_value = (.06,.035,.028,1)
    t.inputs["Mortar"].default_value = (.03,.03,.03,1)
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 4
    nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = .7
    nt.links.new(t.outputs["Color"], mx.inputs[6]); nt.links.new(n.outputs["Color"], mx.inputs[7])
    nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .5
    nt.links.new(t.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs[0], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = .9

BRICK = nodemat("tijolo", brick)
IRON = mat("ferro", (.05,.05,.05), 1, .5)
RUST = mat("ferrugem", (.15,.06,.03), .4, .8)
SAND = mat("saco_areia", (.09,.08,.055), 0, 1)
WOOD = mat("madeira_podre", (.07,.05,.035), 0, .8)
CANVAS = mat("lona", (.07,.07,.05), 0, .95)
STONE = mat("pedra", (.09,.085,.08), 0, .85)
BLOOD = mat("sangue", (.06,0,.003), .1, .15)
FLESH = mat("carne_pendurada", (.2,.05,.04), 0, .35)
FIRE = mat("fogo", (1,.3,.05), emit=(1,.28,.03), strength=12)
GLASS = mat("vitral", (.5,.02,.02), emit=(1,.05,.03), strength=6)
CANDLE = mat("vela", (1,.7,.3), emit=(1,.6,.2), strength=15)
LAMP = mat("lampiao", (1,.8,.5), emit=(1,.7,.35), strength=10)
ACID = mat("acido", (.3,.9,.1), emit=(.4,1,.12), strength=6)
GREY = mat("cadaver", (.14,.13,.12), 0, .7)

def cube(m, loc, s, rot=(0,0,0), parent=None):
    return prim("primitive_cube_add", m, loc, s, rot, parent=parent, smooth=False)

def flames(x, y, z, r, n, rnd):
    for k in range(n):
        o = prim("primitive_cone_add", FIRE, (x+rnd.uniform(-r,r), y+rnd.uniform(-r,r), z+.12), (1,1,1),
                 (rnd.uniform(-15,15), rnd.uniform(-15,15), 0), radius1=rnd.uniform(.04,.09), depth=rnd.uniform(.2,.5), vertices=6)

def build(kind, rnd):
    """Constrói o objeto com a base em (0,0,0), ocupando ~1 tile."""
    if kind.startswith("wall_"):
        ax, h = kind[5], [0, .7, 1.6, 2.6][int(kind[6])]
        for k in range(3):                         # topo quebrado em degraus
            hh = h*rnd.uniform(.75, 1.0) if k != 1 else h
            o = cube(BRICK, (0,0,hh/2), (.17 if ax == "x" else .2, .2 if ax == "x" else .17, hh/2))
            o.location[0 if ax == "x" else 1] = (k-1)*.33
        for k in range(3): cube(BRICK, (rnd.uniform(-.4,.4), rnd.uniform(-.4,.4), .05), (.1,.07,.05), (0,0,rnd.uniform(0,90)))
    elif kind == "rubble":
        for k in range(9):
            cube(BRICK if k % 3 else STONE, (rnd.uniform(-.4,.4), rnd.uniform(-.4,.4), rnd.uniform(.05,.25)),
                 (rnd.uniform(.08,.2), rnd.uniform(.06,.15), rnd.uniform(.05,.12)), (rnd.uniform(-20,20), rnd.uniform(-20,20), rnd.uniform(0,90)))
        along("primitive_cylinder_add", RUST, (-.4,.2,.05), (.3,-.3,.45), .025, None, vertices=6)
    elif kind.startswith("sandbag_"):
        ax = kind[-1]
        for row in range(3):
            for i in range(3 - row % 2):
                off = (i - 1 + (row % 2)*.5)*.34
                prim("primitive_uv_sphere_add", SAND, (off, 0, .1+row*.17) if ax == "x" else (0, off, .1+row*.17),
                     (.19,.13,.1) if ax == "x" else (.13,.19,.1))
    elif kind.startswith("wire_"):
        ax = kind[-1]
        for s in (-1, 1):
            p = (s*.45, 0) if ax == "x" else (0, s*.45)
            along("primitive_cylinder_add", WOOD, (p[0]-.1, p[1]+.1, 0), (p[0]+.1, p[1]-.1, .9), .03, None, vertices=6)
            along("primitive_cylinder_add", WOOD, (p[0]+.1, p[1]+.1, 0), (p[0]-.1, p[1]-.1, .9), .03, None, vertices=6)
        for i in range(6):
            o = prim("primitive_torus_add", IRON, ((i-2.5)*.17, 0, .45) if ax == "x" else (0, (i-2.5)*.17, .45),
                     (1,1,1), (rnd.uniform(-10,10), 90 if ax == "x" else 0, 90 if ax == "y" else 0), major_radius=.2, minor_radius=.006)
    elif kind == "bonfire":
        for k in range(8):
            a = k*45
            along("primitive_cylinder_add", WOOD, (.4*math.cos(math.radians(a)), .4*math.sin(math.radians(a)), 0), (0,0,.35), .05, None, vertices=6)
        for k in range(10): cube(STONE, (.5*math.cos(k*.63), .5*math.sin(k*.63), .07), (.1,.09,.07), (0,0,k*20))
        flames(0, 0, .1, .15, 10, rnd)
    elif kind == "tent":
        o = prim("primitive_cone_add", CANVAS, (0,0,.8), (1.3,.9,1), (0,0,30), radius1=1.1, depth=1.6, vertices=4, smooth=False)
        along("primitive_cylinder_add", WOOD, (0,0,0), (0,0,1.75), .03, None, vertices=6)
        cube(BLOOD, (.3,-.6,.4), (.15,.01,.2), (0,0,30))
    elif kind == "barrel_fire":
        prim("primitive_cylinder_add", RUST, (0,0,.37), (.25,.25,.37), smooth=False)
        for z in (.15, .6): prim("primitive_torus_add", IRON, (0,0,z), major_radius=.255, minor_radius=.015)
        flames(0, 0, .72, .12, 7, rnd)
    elif kind == "crate":
        cube(WOOD, (0,0,.25), (.28,.28,.25), (0,0,rnd.uniform(0,40)))
        cube(WOOD, (rnd.uniform(-.1,.1),0,.62), (.18,.18,.12), (0,0,rnd.uniform(0,40)))
    elif kind == "lamp":
        along("primitive_cylinder_add", IRON, (0,0,0), (0,0,2.6), .04, None, vertices=8)
        along("primitive_cylinder_add", IRON, (0,0,2.5), (.35,-.35,2.55), .02, None, vertices=6)
        prim("primitive_cylinder_add", IRON, (.35,-.35,2.42), (.09,.09,.12), smooth=False)
        prim("primitive_uv_sphere_add", LAMP, (.35,-.35,2.35), (.07,.07,.07))
    elif kind.startswith("cross"):
        t = rnd.uniform(-14, 14)
        h = [1.2, 1.5, 1.0][int(kind[-1])-1]
        root = M.make_root("c"); root.rotation_euler = (math.radians(rnd.uniform(-8,8)), math.radians(t), math.radians(45))
        cube(WOOD if kind != "cross3" else IRON, (0,0,h/2), (.05,.05,h/2), parent=root)
        cube(WOOD if kind != "cross3" else IRON, (0,0,h*.72), (.28,.05,.045), parent=root)
        prim("primitive_uv_sphere_add", STONE, (0,0,0), (.45,.3,.12), parent=None)
    elif kind.startswith("grave"):
        cube(STONE, (0,.2,.4 if kind == "grave1" else .3), (.3,.08,.4 if kind == "grave1" else .3), (rnd.uniform(-6,6),0,0))
        prim("primitive_uv_sphere_add", STONE if kind == "grave1" else BLOOD, (0,-.25,0), (.3,.5,.12))
        if kind == "grave2": prim("primitive_uv_sphere_add", CANDLE, (.2,.1,.08), (.03,.03,.05))
    elif kind.startswith("tree"):
        def branch(p, d, L, r, depth):
            q = p + d*L
            along("primitive_cylinder_add", WOOD, p, q, r, None, vertices=6)
            if depth:
                for s in (-1, 1):
                    nd = (d + Vector((rnd.uniform(-.8,.8), rnd.uniform(-.8,.8), .25))).normalized()
                    branch(q, nd, L*.7, r*.65, depth-1)
        branch(Vector((0,0,0)), Vector((0,0,1)), 1.5 if kind == "tree1" else 1.1, .11, 4)
    elif kind == "gibbet":
        along("primitive_cylinder_add", WOOD, (0,0,0), (0,0,3.0), .07, None, vertices=6)
        along("primitive_cylinder_add", WOOD, (0,0,2.9), (.0,-1.0,2.9), .05, None, vertices=6)
        chain(IRON, (0,-.95,2.9), (0,-.95,2.3), 6, None)
        for k in range(8):
            a = k*45; along("primitive_cylinder_add", RUST, (.25*math.cos(math.radians(a)), -.95+.25*math.sin(math.radians(a)), 1.3),
                            (.25*math.cos(math.radians(a)), -.95+.25*math.sin(math.radians(a)), 2.3), .015, None, vertices=4)
        r = M.make_root("preso", (0,-.95,1.35)); r.scale = (.55,.55,.55); r.rotation_euler = (0,math.radians(10),0)
        M.body("preso", GREY, r, {"kneeL":(.12,-.2,.55,.06), "kneeR":(-.12,-.25,.5,.06)})
        prim("primitive_uv_sphere_add", ACID, (0,-.95,2.32), (.06,.06,.06))
    elif kind == "window_y":
        cube(BRICK, (0,0,1.5), (.2,.5,1.5))
        cube(GLASS, (.21,0,1.7), (.01,.28,.6))
        prim("primitive_cylinder_add", GLASS, (.21,0,2.3), (.01,.28,.28), (0,90,0))
        cube(IRON, (.22,0,1.7), (.012,.02,.6)); cube(IRON, (.22,0,1.8), (.012,.28,.02))
    elif kind == "pew":
        cube(WOOD, (0,0,.25), (.2,.75,.04), (0,rnd.uniform(-8,8),0)); cube(WOOD, (.18,0,.45), (.03,.75,.2))
        for s in (-1,1): cube(WOOD, (0,s*.65,.12), (.18,.03,.12))
    elif kind == "altar":
        cube(STONE, (0,0,.45), (.4,.8,.45)); cube(BLOOD, (0,0,.91), (.38,.5,.01))
        along("primitive_cylinder_add", IRON, (-.2,0,.9), (-.2,0,2.2), .04, None, vertices=6)
        cube(IRON, (-.2,0,1.9), (.04,.45,.04))
        for k in range(6): prim("primitive_cylinder_add", CANDLE, (rnd.uniform(-.3,.3), rnd.uniform(-.7,.7), .98), (.025,.025,.08))
    elif kind == "hooks":
        cube(WOOD, (0,0,2.3), (.5,.05,.05))
        for s in (-1, 1): along("primitive_cylinder_add", WOOD, (s*.5,0,0), (s*.5,0,2.35), .05, None, vertices=6)
        for k in range(2):
            x = -.22 + k*.44; chain(IRON, (x,0,2.25), (x,0,1.9), 4, None)
            prim("primitive_uv_sphere_add", FLESH, (x,0,1.5), (.16,.12,.38))
            prim("primitive_uv_sphere_add", BLOOD, (x,0,.01), (.25,.18,.01))
    elif kind == "fence_y":
        for k in range(3): along("primitive_cylinder_add", WOOD, (0,(k-1)*.4,0), (rnd.uniform(-.05,.05),(k-1)*.4,1.2+rnd.uniform(-.2,.1)), .05, None, vertices=6)
        for z in (.4, .9): cube(WOOD, (0,0,z), (.03,.5,.05), (rnd.uniform(-5,5),0,0))
    elif kind == "cart":
        cube(WOOD, (0,0,.55), (.5,.8,.06), (0,8,0)); cube(WOOD, (.48,0,.75), (.03,.8,.2), (0,8,0))
        for s in (-1,1): prim("primitive_torus_add", WOOD, (-.55, s*.5, .45), (1,1,1), (0,90,0), major_radius=.4, minor_radius=.04)
        along("primitive_cylinder_add", WOOD, (.5,0,.5), (1.2,.2,.05), .04, None, vertices=6)
    elif kind == "corpse":
        r = M.make_root("corpo", (0,0,.17)); r.rotation_euler = (math.radians(-88), 0, math.radians(rnd.uniform(0,360)))
        r.location = (0,0,.12)
        M.body("cadaver", GREY, r, {}); prim("primitive_uv_sphere_add", GREY, (0,-.01,1.62), (.09,.1,.11), parent=r)
        prim("primitive_cylinder_add", BLOOD, (.2,.1,.004), (.6,.4,.004), vertices=20)

def camera(target, scale, w, h, shift_y=0.0):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = scale; cam.data.clip_end = 300; cam.data.shift_y = shift_y
    e, a, d = math.radians(35), math.radians(45), 80; t = Vector(target)
    cam.location = t + Vector((d*math.cos(e)*math.sin(a), -d*math.cos(e)*math.cos(a), d*math.sin(e)))
    cam.rotation_euler = (t - cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = w, h

def lights(moon=1.8):
    for name, rgb, en, rot in [("lua",(.55,.65,1),moon,(40,0,-50)), ("contra",(.8,.25,.15),1.0,(-50,0,170)), ("fill",(.3,.35,.5),.35,(70,0,110))]:
        l = bpy.data.objects.new(name, bpy.data.lights.new(name,'SUN')); sc.collection.objects.link(l)
        l.data.color = rgb; l.data.energy = en; l.data.angle = .05; l.rotation_euler = [math.radians(r) for r in rot]

sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.use_denoising = False; sc.cycles.max_bounces = 3
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'
sc.world = bpy.data.worlds.new("w"); sc.world.color = (.012,.014,.02)

KIND_SIZE = {"tree1": 6, "tree2": 5, "gibbet": 5, "lamp": 4.5, "tent": 4, "window_y": 4.5, "hooks": 4, "altar": 4, "wall_x3": 4, "wall_y3": 4, "cart": 4}

if mode == "props":
    out = argv[2]; os.makedirs(out, exist_ok=True)
    kinds = sorted({p["kind"] for p in layout["props"]})
    lights(); sc.render.film_transparent = True; sc.cycles.samples = 48
    meta = {}
    for kind in kinds:
        for o in list(bpy.data.objects):
            if o.type != 'LIGHT': bpy.data.objects.remove(o)
        build(kind, random.Random(kind))
        size = KIND_SIZE.get(kind, 3)
        px = int(size*PXM)
        camera((0,0,0), size, px*2, px*2, shift_y=.25)    # origem do tile a 75% da altura
        sc.render.filepath = f"{out}/{kind}.png"; bpy.ops.render.render(write_still=True)
        meta[kind] = {"size": px, "origin": [px/2, px*.75]}
    json.dump(meta, open(f"{out}/props.json", "w"))
    print("OK props", len(kinds))

else:
    mask, out = argv[2], argv[3]
    N = layout["size"]
    img = bpy.data.images.load(mask)
    def ground(nt, b):
        tc = nt.nodes.new("ShaderNodeTexCoord")
        mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1,-1,1); mp.inputs["Location"].default_value = (0,1,0)
        it = nt.nodes.new("ShaderNodeTexImage"); it.image = img; it.interpolation = 'Cubic'
        nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"]); nt.links.new(mp.outputs["Vector"], it.inputs["Vector"])
        sep = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(it.outputs["Color"], sep.inputs["Color"])
        # pedra: voronoi de calçamento
        v = nt.nodes.new("ShaderNodeTexVoronoi"); v.inputs["Scale"].default_value = 2.6; v.feature = 'DISTANCE_TO_EDGE'
        nt.links.new(tc.outputs["Object"], v.inputs["Vector"])
        rs = nt.nodes.new("ShaderNodeValToRGB"); rs.color_ramp.elements[0].color = (.004,.004,.004,1)
        rs.color_ramp.elements[1].position = .12; rs.color_ramp.elements[1].color = (.032,.03,.028,1)
        nt.links.new(v.outputs["Distance"], rs.inputs[0])
        # lama/terra com manchas de grama morta
        n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = .6; n.inputs["Detail"].default_value = 8
        nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
        rm = nt.nodes.new("ShaderNodeValToRGB")
        rm.color_ramp.elements[0].position = .35; rm.color_ramp.elements[0].color = (.012,.01,.007,1)
        rm.color_ramp.elements[1].position = .7; rm.color_ramp.elements[1].color = (.02,.021,.013,1)
        nt.links.new(n.outputs["Fac"], rm.inputs[0])
        grave = nt.nodes.new("ShaderNodeMix"); grave.data_type = 'RGBA'; grave.inputs[7].default_value = (.03,.022,.016,1)
        nt.links.new(rm.outputs[0], grave.inputs[6]); nt.links.new(sep.outputs["Green"], grave.inputs[0])
        n3 = nt.nodes.new("ShaderNodeTexNoise"); n3.inputs["Scale"].default_value = .18; n3.inputs["Detail"].default_value = 4
        nt.links.new(tc.outputs["Object"], n3.inputs["Vector"])
        r3 = nt.nodes.new("ShaderNodeValToRGB"); r3.color_ramp.elements[0].position = .45; r3.color_ramp.elements[1].position = .55
        nt.links.new(n3.outputs["Fac"], r3.inputs[0])
        mx3 = nt.nodes.new("ShaderNodeMath"); mx3.operation = 'MAXIMUM'
        nt.links.new(sep.outputs["Red"], mx3.inputs[0]); nt.links.new(r3.outputs[0], mx3.inputs[1])
        mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = 'RGBA'
        nt.links.new(mx3.outputs[0], mix.inputs[0]); nt.links.new(grave.outputs[2], mix.inputs[6]); nt.links.new(rs.outputs[0], mix.inputs[7])
        bl = nt.nodes.new("ShaderNodeMix"); bl.data_type = 'RGBA'; bl.inputs[7].default_value = (.018,0,.001,1)
        bn = nt.nodes.new("ShaderNodeTexNoise"); bn.inputs["Scale"].default_value = 3; nt.links.new(tc.outputs["Object"], bn.inputs["Vector"])
        bm = nt.nodes.new("ShaderNodeMath"); bm.operation = 'MULTIPLY'; bm.use_clamp = True
        nt.links.new(sep.outputs["Blue"], bm.inputs[0]); nt.links.new(bn.outputs["Fac"], bm.inputs[1])
        bm2 = nt.nodes.new("ShaderNodeMath"); bm2.operation = 'MULTIPLY'; bm2.inputs[1].default_value = 1.8; bm2.use_clamp = True
        nt.links.new(bm.outputs[0], bm2.inputs[0])
        nt.links.new(bm2.outputs[0], bl.inputs[0]); nt.links.new(mix.outputs[2], bl.inputs[6])
        nt.links.new(bl.outputs[2], b.inputs["Base Color"])
        # poças: rugosidade baixa onde o ruído é alto ou há sangue
        n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = .25
        nt.links.new(tc.outputs["Object"], n2.inputs["Vector"])
        rr = nt.nodes.new("ShaderNodeValToRGB"); rr.color_ramp.elements[0].position = .58; rr.color_ramp.elements[0].color = (.85,.85,.85,1)
        rr.color_ramp.elements[1].position = .63; rr.color_ramp.elements[1].color = (.1,.1,.1,1)
        nt.links.new(n2.outputs["Fac"], rr.inputs[0])
        mn = nt.nodes.new("ShaderNodeMath"); mn.operation = 'SUBTRACT'
        nt.links.new(rr.outputs[0], mn.inputs[0]); nt.links.new(sep.outputs["Blue"], mn.inputs[1])
        nt.links.new(mn.outputs[0], b.inputs["Roughness"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .35
        hm = nt.nodes.new("ShaderNodeMath"); hm.operation = 'MULTIPLY'
        nt.links.new(rs.outputs[0], hm.inputs[0]); nt.links.new(sep.outputs["Red"], hm.inputs[1])
        nt.links.new(hm.outputs[0], bp.inputs["Height"]); nt.links.new(bp.outputs[0], b.inputs["Normal"])
    gm = nodemat("chao", ground)
    bpy.ops.mesh.primitive_plane_add(size=N, location=(N/2, N/2, 0)); bpy.context.object.data.materials.append(gm)
    bpy.ops.mesh.primitive_plane_add(size=N*3, location=(N/2, N/2, -.01))     # fora do mapa: escuridão
    bpy.context.object.data.materials.append(mat("vazio", (.004,.004,.005), 0, 1))
    # objetos invisíveis à câmera, mas que projetam sombra e recebem a luz das fontes
    modelos = {}                      # cada tipo é construído uma vez e copiado (bem mais rápido)
    for i, p in enumerate(layout["props"]):
        k = p["kind"]
        if k not in modelos:
            before = set(bpy.data.objects)
            build(k, random.Random(k))
            modelos[k] = list(set(bpy.data.objects) - before)
            for o in modelos[k]:
                o.visible_camera = False; o.hide_render = True
        r = M.make_root(f"p{i}", (p["x"], p["y"], 0))
        mapa_c = {}
        for o in modelos[k]:
            c = o.copy(); sc.collection.objects.link(c); c.hide_render = False; mapa_c[o] = c
        for o, c in mapa_c.items():
            c.parent = mapa_c.get(o.parent, r) if o.parent else r
        if "light" in p:
            c = p["light"]; l = bpy.data.objects.new("pl", bpy.data.lights.new("pl", 'POINT')); sc.collection.objects.link(l)
            l.data.color = c[:3]; l.data.energy = c[3]*45; l.data.shadow_soft_size = .3
            l.location = (p["x"]+.3, p["y"]-.3, 1.4)
    lights(1.0)
    W, H = 3072, 1792
    camera((N/2, N/2, 0), W/PXM, W, H)
    sc.cycles.samples = int(argv[4]) if len(argv) > 4 else 48
    sc.render.film_transparent = False
    sc.render.filepath = out; bpy.ops.render.render(write_still=True)
    print("OK ground")
