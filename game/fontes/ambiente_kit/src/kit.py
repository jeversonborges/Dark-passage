# Kit de ambiente do DARK PASSAGE (estilo "Ferrugem Sagrada").
# Câmera isométrica 2:1 (elevação 30°, azimute 45°), 64 px por metro na
# resolução final. Um tile de chão mede 64x32 px = 0,7071 m de lado.
import bpy, bmesh, math, random, os, json
from mathutils import Vector, Matrix

PX_M = 64            # pixels por metro na saída final
SS = 2               # supersampling (render em 2x e reduz)
T = 1 / math.sqrt(2) # lado do tile em metros (64x32 px)
ELEV, AZ = 30.0, 45.0

# ---------------------------------------------------------------- cena
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = 48; sc.cycles.max_bounces = 4
    sc.cycles.use_denoising = False
    try: sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception: pass
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'Medium High Contrast'
    sc.render.film_transparent = True
    sc.render.image_settings.color_mode = 'RGBA'
    w = bpy.data.worlds.new("w"); sc.world = w; w.color = (.012, .013, .018)
    return sc

def cam_dir():
    e, a = math.radians(ELEV), math.radians(AZ)
    return Vector((math.cos(e)*math.sin(a), -math.cos(e)*math.cos(a), math.sin(e)))  # do alvo para a câmera

def make_cam():
    sc = bpy.context.scene
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'; cam.data.clip_start = .1; cam.data.clip_end = 400
    cam.location = cam_dir() * 120
    cam.rotation_euler = (-cam_dir()).to_track_quat('-Z', 'Y').to_euler()
    sc.camera = cam
    return cam

def screen_xy(p):
    """Projeção ortográfica em metros de tela (x para a direita, y para cima)."""
    right = Vector((math.cos(math.radians(AZ)), math.sin(math.radians(AZ)), 0))
    p = Vector(p); return p.dot(right), p.dot(up_vec())

def sun(name, rgb, energy, rot, angle=.08):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'SUN')); bpy.context.scene.collection.objects.link(l)
    l.data.color = rgb; l.data.energy = energy; l.data.angle = angle
    l.rotation_euler = [math.radians(r) for r in rot]; return l

def point(loc, rgb, energy, radius=.1, name="p"):
    l = bpy.data.objects.new(name, bpy.data.lights.new(name, 'POINT')); bpy.context.scene.collection.objects.link(l)
    l.data.color = rgb; l.data.energy = energy; l.data.shadow_soft_size = radius; l.location = loc; return l

KEY_ROT = (52, 0, -40)
def lights(dungeon=False):
    """Iluminação padrão do kit: lua fria do alto-esquerda, contraluz quente, fill azulado."""
    if dungeon:
        sun("key", (.55, .6, .8), 1.1, KEY_ROT, .15)
        sun("rim", (.9, .35, .15), 1.2, (-55, 0, 165))
        sun("fill", (.25, .28, .4), .35, (70, 0, 110))
    else:
        sun("key", (.78, .82, 1.0), 2.2, KEY_ROT, .06)
        sun("rim", (.9, .42, .2), 1.1, (-55, 0, 165))
        sun("fill", (.35, .37, .45), .45, (70, 0, 110))

def shadow_catcher(size=60):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, 0))
    o = bpy.context.object; o.name = "_catcher"; o.is_shadow_catcher = True
    o.data.materials.append(mat_solid("catcher", (.05, .05, .05), rough=1))
    return o

# ---------------------------------------------------------------- nós
def N(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items():
        if k.startswith("i_"):
            key = k[2:].replace("_", " ")
            n.inputs[key].default_value = v
        else:
            setattr(n, k, v)
    return n

def L(nt, a, b): nt.links.new(a, b)

def ramp(nt, stops):
    r = N(nt, "ShaderNodeValToRGB"); els = r.color_ramp.elements
    while len(els) < len(stops): els.new(0)
    for el, (pos, col) in zip(els, stops):
        el.position = pos; el.color = (*col, 1) if len(col) == 3 else col
    return r

def mix(nt, a, b, fac, mode='MIX'):
    m = N(nt, "ShaderNodeMix", data_type='RGBA', blend_type=mode)
    for src, idx in ((fac, 0), (a, 6), (b, 7)):
        if isinstance(src, (int, float)): m.inputs[idx].default_value = src
        elif isinstance(src, tuple): m.inputs[idx].default_value = (*src, 1) if len(src) == 3 else src
        else: L(nt, src, m.inputs[idx])
    return m.outputs[2]

def math_(nt, op, a, b=0.0):
    m = N(nt, "ShaderNodeMath", operation=op)
    for src, idx in ((a, 0), (b, 1)):
        if isinstance(src, (int, float)): m.inputs[idx].default_value = src
        else: L(nt, src, m.inputs[idx])
    return m.outputs[0]

def coords(nt, period=None, seed=0.0, space="Object"):
    """Coordenadas para texturas. Com period=(px,py) as texturas 4D ficam
    periódicas (toro plano), o que deixa tiles e muros sem emenda."""
    tc = N(nt, "ShaderNodeTexCoord"); v = tc.outputs[space]
    if not period: return v, None
    if period[0] == "wall":   # periódico ao longo do muro (x+y), livre na altura
        sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, v, sep.inputs[0])
        u = math_(nt, 'MULTIPLY', math_(nt, 'ADD', sep.outputs[0], sep.outputs[1]), 2*math.pi/period[1])
        R = period[1]/(2*math.pi)
        comb = N(nt, "ShaderNodeCombineXYZ")
        L(nt, math_(nt, 'MULTIPLY', math_(nt, 'COSINE', u), R), comb.inputs[0])
        L(nt, math_(nt, 'MULTIPLY', math_(nt, 'SINE', u), R), comb.inputs[1])
        L(nt, sep.outputs[2], comb.inputs[2])
        wv = N(nt, "ShaderNodeValue"); wv.outputs[0].default_value = seed
        return comb.outputs[0], wv.outputs[0]
    sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, v, sep.inputs[0])
    px, py = period
    def ang(c, p): return math_(nt, 'MULTIPLY', c, 2*math.pi/p)
    ax, ay = ang(sep.outputs[0], px), ang(sep.outputs[1], py)
    rx, ry = px/(2*math.pi), py/(2*math.pi)
    cx = math_(nt, 'MULTIPLY', math_(nt, 'COSINE', ax), rx)
    sx = math_(nt, 'MULTIPLY', math_(nt, 'SINE', ax), rx)
    cy = math_(nt, 'MULTIPLY', math_(nt, 'COSINE', ay), ry)
    sy = math_(nt, 'MULTIPLY', math_(nt, 'SINE', ay), ry)
    comb = N(nt, "ShaderNodeCombineXYZ"); L(nt, cx, comb.inputs[0]); L(nt, sx, comb.inputs[1]); L(nt, cy, comb.inputs[2])
    w = math_(nt, 'ADD', sy, seed)
    return comb.outputs[0], w

def noise(nt, vec, w, scale, detail=6, rough=.55, seed=0.0):
    n = N(nt, "ShaderNodeTexNoise", noise_dimensions='4D', i_Scale=scale, i_Detail=detail, i_Roughness=rough)
    L(nt, vec, n.inputs["Vector"])
    if w is not None: L(nt, w, n.inputs["W"])
    else: n.inputs["W"].default_value = seed
    return n

def voronoi(nt, vec, w, scale, feature='F1', seed=0.0, rand=1.0):
    n = N(nt, "ShaderNodeTexVoronoi", voronoi_dimensions='4D', feature=feature, i_Scale=scale)
    n.inputs["Randomness"].default_value = rand
    L(nt, vec, n.inputs["Vector"])
    if w is not None: L(nt, w, n.inputs["W"])
    else: n.inputs["W"].default_value = seed
    return n

def new_mat(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    return m, nt, b

def grime(nt, col, vec, w, top=2.2, strength=.75):
    """Escurece de cima para baixo (pés no escuro) com manchas de sujeira."""
    geo = N(nt, "ShaderNodeNewGeometry"); sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, geo.outputs["Position"], sep.inputs[0])
    h = math_(nt, 'DIVIDE', sep.outputs[2], top)
    nz = noise(nt, vec, w, 3.0, 4)
    f = math_(nt, 'ADD', h, math_(nt, 'MULTIPLY', nz.outputs["Fac"], .5))
    r = ramp(nt, [(.25, (0, 0, 0)), (.75, (1, 1, 1))]); L(nt, f, r.inputs[0])
    inv = math_(nt, 'SUBTRACT', 1.0, r.outputs[0])
    return mix(nt, col, (.01, .009, .008), math_(nt, 'MULTIPLY', inv, strength))

def bump(nt, b, height, strength=.4, dist=.05):
    bp = N(nt, "ShaderNodeBump", i_Strength=strength, i_Distance=dist)
    L(nt, height, bp.inputs["Height"]); L(nt, bp.outputs[0], b.inputs["Normal"]); return bp

# ---------------------------------------------------------------- materiais
_cache = {}
def cached(fn):
    def w(*a, **k):
        key = (fn.__name__, a, tuple(sorted(k.items())))
        if key not in _cache: _cache[key] = fn(*a, **k)
        return _cache[key]
    w.__name__ = fn.__name__; return w

@cached
def mat_solid(name, rgb, metal=0., rough=.7, emit=None, strength=0.):
    m, nt, b = new_mat(name)
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Metallic"].default_value = metal; b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1); b.inputs["Emission Strength"].default_value = strength
    return m

@cached
def mat_stone(name="pedra", c1=(.085, .078, .072), c2=(.04, .037, .035), scale=2.0, moss=0.0, period=None, top=2.2, seed=0.0):
    m, nt, b = new_mat(name)
    v, w = coords(nt, period, seed)
    n1 = noise(nt, v, w, scale*2, 8, .6, seed); n2 = noise(nt, v, w, scale*9, 4, .5, seed+3)
    r = ramp(nt, [(.35, c2), (.65, c1)]); L(nt, n1.outputs["Fac"], r.inputs[0])
    col = mix(nt, r.outputs[0], n2.outputs["Color"], .12, 'OVERLAY')
    if moss:
        mn = noise(nt, v, w, scale*1.3, 5, .6, seed+7)
        mr = ramp(nt, [(.55, (0, 0, 0)), (.62, (1, 1, 1))]); L(nt, mn.outputs["Fac"], mr.inputs[0])
        col = mix(nt, col, (.03, .04, .022), math_(nt, 'MULTIPLY', mr.outputs[0], moss))
    col = grime(nt, col, v, w, top)
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .88
    h = math_(nt, 'ADD', n1.outputs["Fac"], math_(nt, 'MULTIPLY', n2.outputs["Fac"], .4))
    bump(nt, b, h, .55, .04); return m

@cached
def mat_brick(name="tijolo", period=None, seed=0.0, tint=(.11, .048, .032), top=2.6, plaster=0.0, bw=None, rh=.075, mortar=.012):
    m, nt, b = new_mat(name)
    v, w = coords(nt, period, seed)
    tc = N(nt, "ShaderNodeTexCoord")
    mp = N(nt, "ShaderNodeMapping"); L(nt, tc.outputs["Object"], mp.inputs[0])
    # tijolo usa coordenada (x+y) ao longo do muro e z na altura
    sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, tc.outputs["Object"], sep.inputs[0])
    comb = N(nt, "ShaderNodeCombineXYZ")
    L(nt, math_(nt, 'ADD', sep.outputs[0], sep.outputs[1]), comb.inputs[0]); L(nt, sep.outputs[2], comb.inputs[1])
    bk = N(nt, "ShaderNodeTexBrick", offset=.5, squash=1.0)
    bk.inputs["Scale"].default_value = 1.0
    bk.inputs["Brick Width"].default_value = bw or T/3; bk.inputs["Row Height"].default_value = rh
    bk.inputs["Mortar Size"].default_value = mortar; bk.inputs["Mortar Smooth"].default_value = .3
    bk.inputs["Color1"].default_value = (*tint, 1)
    bk.inputs["Color2"].default_value = (tint[0]*.6, tint[1]*.65, tint[2]*.7, 1)
    bk.inputs["Mortar"].default_value = (.025, .024, .022, 1)
    L(nt, comb.outputs[0], bk.inputs["Vector"])
    nz = noise(nt, v, w, 6, 6, .6, seed)
    col = mix(nt, bk.outputs["Color"], nz.outputs["Color"], .18, 'OVERLAY')
    chip = noise(nt, v, w, 14, 3, .5, seed+2)
    cr = ramp(nt, [(.6, (1, 1, 1)), (.7, (.35, .33, .3))]); L(nt, chip.outputs["Fac"], cr.inputs[0])
    col = mix(nt, col, cr.outputs[0], 1, 'MULTIPLY')
    if plaster:
        pn = noise(nt, v, w, 1.6, 6, .65, seed+5)
        pr = ramp(nt, [(.48, (0, 0, 0)), (.52, (1, 1, 1))]); L(nt, pn.outputs["Fac"], pr.inputs[0])
        col = mix(nt, col, (.12, .11, .095), math_(nt, 'MULTIPLY', pr.outputs[0], plaster))
    col = grime(nt, col, v, w, top)
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .9
    h = math_(nt, 'SUBTRACT', 1.0, bk.outputs["Fac"])
    bump(nt, b, math_(nt, 'ADD', h, math_(nt, 'MULTIPLY', chip.outputs["Fac"], .3)), .6, .03)
    return m

@cached
def mat_wood(name="madeira", c=(.075, .05, .033), seed=0.0, painted=None):
    m, nt, b = new_mat(name)
    tc = N(nt, "ShaderNodeTexCoord")
    mp = N(nt, "ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 14)
    L(nt, tc.outputs["Object"], mp.inputs[0])
    wv = N(nt, "ShaderNodeTexWave", wave_type='BANDS', bands_direction='Z')
    wv.inputs["Scale"].default_value = 3; wv.inputs["Distortion"].default_value = 9; wv.inputs["Detail"].default_value = 6
    L(nt, mp.outputs[0], wv.inputs[0])
    r = ramp(nt, [(.2, (c[0]*.45, c[1]*.45, c[2]*.45)), (.8, c)]); L(nt, wv.outputs["Fac"], r.inputs[0])
    col = r.outputs[0]
    v = tc.outputs["Object"]
    if painted:
        pn = noise(nt, v, None, 5, 6, .6, seed)
        pr = ramp(nt, [(.45, (0, 0, 0)), (.55, (1, 1, 1))]); L(nt, pn.outputs["Fac"], pr.inputs[0])
        col = mix(nt, col, painted, pr.outputs[0])
    col = grime(nt, col, v, None, 2.0, .6)
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .82
    bump(nt, b, wv.outputs["Fac"], .35, .02); return m

@cached
def mat_metal(name="ferro", base=(.045, .043, .042), rust=.6, seed=0.0, rough=.55):
    m, nt, b = new_mat(name)
    v, w = coords(nt)
    n = noise(nt, v, w, 7, 8, .65, seed)
    r = ramp(nt, [(.42, (0, 0, 0)), (.58, (1, 1, 1))]); L(nt, n.outputs["Fac"], r.inputs[0])
    rf = math_(nt, 'MULTIPLY', r.outputs[0], rust)
    n2 = noise(nt, v, w, 25, 3, .5, seed+1)
    rcol = mix(nt, (.16, .055, .02), (.07, .03, .015), n2.outputs["Fac"])
    col = mix(nt, base, rcol, rf)
    L(nt, col, b.inputs["Base Color"])
    met = math_(nt, 'SUBTRACT', 1.0, rf); L(nt, math_(nt, 'MULTIPLY', met, .85), b.inputs["Metallic"])
    rg = math_(nt, 'ADD', rough, math_(nt, 'MULTIPLY', rf, .4)); L(nt, rg, b.inputs["Roughness"])
    bump(nt, b, math_(nt, 'ADD', rf, math_(nt, 'MULTIPLY', n2.outputs["Fac"], .3)), .3, .01); return m

@cached
def mat_brass(name="latao"):
    m, nt, b = new_mat(name)
    v, w = coords(nt)
    n = noise(nt, v, w, 9, 6, .6)
    r = ramp(nt, [(.45, (.28, .17, .06)), (.6, (.06, .07, .05))]); L(nt, n.outputs["Fac"], r.inputs[0])  # verdete
    L(nt, r.outputs[0], b.inputs["Base Color"]); b.inputs["Metallic"].default_value = .85
    b.inputs["Roughness"].default_value = .38; return m

@cached
def mat_bone(name="osso", c=(.36, .32, .25)):
    m, nt, b = new_mat(name)
    v, w = coords(nt)
    n = noise(nt, v, w, 12, 6, .6)
    r = ramp(nt, [(.3, (c[0]*.35, c[1]*.32, c[2]*.28)), (.7, c)]); L(nt, n.outputs["Fac"], r.inputs[0])
    col = grime(nt, r.outputs[0], v, w, 1.2, .55)
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .6
    bump(nt, b, n.outputs["Fac"], .3, .01); return m

@cached
def mat_cloth(name="lona", c=(.09, .075, .05), seed=0.0):
    m, nt, b = new_mat(name)
    v, w = coords(nt)
    n = noise(nt, v, w, 4, 8, .65, seed)
    r = ramp(nt, [(.3, (c[0]*.4, c[1]*.4, c[2]*.4)), (.75, c)]); L(nt, n.outputs["Fac"], r.inputs[0])
    col = grime(nt, r.outputs[0], v, w, 2.4, .7)
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .95
    b.inputs["Sheen Weight"].default_value = .3
    bump(nt, b, n.outputs["Fac"], .2, .02); return m

@cached
def mat_porcelain(name="porcelana"):
    m, nt, b = new_mat(name)
    v, w = coords(nt)
    vo = voronoi(nt, v, w, 3, 'DISTANCE_TO_EDGE')
    cr = ramp(nt, [(0, (.02, .02, .02)), (.035, (1, 1, 1))]); L(nt, vo.outputs["Distance"], cr.inputs[0])
    n = noise(nt, v, w, 3, 5, .6)
    base = mix(nt, (.52, .49, .43), (.3, .27, .22), n.outputs["Fac"])
    col = mix(nt, base, cr.outputs[0], 1, 'MULTIPLY')
    col = grime(nt, col, v, w, 2.0, .6)
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .25
    b.inputs["Coat Weight"].default_value = .4
    bump(nt, b, cr.outputs[0], .3, .01); return m

@cached
def mat_blood(name="sangue", wet=True):
    return mat_solid(name, (.05, .002, .003), 0, .12 if wet else .6)

@cached
def mat_emit(name, rgb, strength):
    m, nt, b = new_mat(name)
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Emission Color"].default_value = (*rgb, 1); b.inputs["Emission Strength"].default_value = strength
    return m

@cached
def mat_stained_glass(name="vitral", hue=(.9, .06, .03), strength=3):
    """Vitral vermelho aceso com chumbo preto (padrão voronoi)."""
    m, nt, b = new_mat(name)
    v, w = coords(nt)
    vo = voronoi(nt, v, w, 7, 'F1')
    ed = voronoi(nt, v, w, 7, 'DISTANCE_TO_EDGE')
    lead = ramp(nt, [(0, (0, 0, 0)), (.06, (1, 1, 1))]); L(nt, ed.outputs["Distance"], lead.inputs[0])
    cr = ramp(nt, [(0, (hue[0]*.5, hue[1]*.4, hue[2]*.4)), (.5, hue), (.85, (.8, .1, .04)), (1, (1, .5, .15))]); L(nt, vo.outputs["Color"], cr.inputs[0])
    sep = N(nt, "ShaderNodeSeparateColor"); L(nt, vo.outputs["Color"], sep.inputs[0])
    col = mix(nt, cr.outputs[0], lead.outputs[0], 1, 'MULTIPLY')
    L(nt, col, b.inputs["Base Color"]); L(nt, col, b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = strength; b.inputs["Roughness"].default_value = .3
    return m

# solos extras do mapa do deserto (level design v0.3): cores, pedrisco, rachadura, poças, brilho verde
SOLOS = {
    "areia":  dict(ondas=1.0, cs=[(.3, (.07, .058, .04)), (.55, (.15, .125, .085)), (.8, (.22, .19, .13))], pc=(.2, .18, .14), pd=.62, ck=.7, poca=.9, verde=0.0),
    "duna":   dict(ondas=1.4, cs=[(.3, (.09, .075, .05)), (.6, (.17, .145, .1)), (.85, (.25, .21, .15))], pc=(.22, .2, .15), pd=.75, ck=.85, poca=.95, verde=0.0),
    "cinza":  dict(ondas=.4, cs=[(.3, (.03, .03, .03)), (.55, (.075, .073, .07)), (.8, (.13, .128, .12))], pc=(.05, .09, .07), pd=.5, ck=.55, poca=.75, verde=.25),
    "vidro":  dict(cs=[(.3, (.012, .02, .016)), (.55, (.04, .06, .045)), (.8, (.08, .11, .08))], pc=(.12, .25, .16), pd=.4, ck=.3, poca=.7, verde=.5),
    "leito":  dict(cs=[(.3, (.05, .04, .03)), (.55, (.1, .082, .06)), (.8, (.15, .125, .09))], pc=(.12, .1, .08), pd=.7, ck=.15, poca=.9, verde=0.0),
    "lama":   dict(cs=[(.3, (.008, .014, .008)), (.55, (.02, .04, .02)), (.8, (.04, .07, .035))], pc=(.04, .06, .03), pd=.8, ck=.9, poca=.45, verde=.7),
    "barranca": dict(cs=[(.3, (.04, .03, .02)), (.55, (.08, .065, .045)), (.8, (.12, .1, .07))], pc=(.1, .09, .07), pd=.55, ck=.3, poca=.85, verde=0.0),
    "musgo":  dict(cs=[(.3, (.02, .025, .012)), (.55, (.05, .06, .03)), (.8, (.08, .09, .045))], pc=(.08, .07, .05), pd=.6, ck=.6, poca=.7, verde=.3),
    "brejo":  dict(cs=[(.3, (.012, .016, .01)), (.55, (.035, .045, .028)), (.8, (.06, .07, .04))], pc=(.06, .06, .04), pd=.7, ck=.8, poca=.5, verde=.45),
    "mata":   dict(cs=[(.3, (.02, .015, .01)), (.55, (.055, .04, .025)), (.8, (.09, .065, .04))], pc=(.12, .08, .04), pd=.35, ck=.6, poca=.8, verde=.1),
    "vala":   dict(cs=[(.3, (.018, .012, .009)), (.55, (.05, .035, .025)), (.8, (.085, .06, .042))], pc=(.25, .22, .17), pd=.5, ck=.45, poca=.6, verde=0.0),
    "cascalho": dict(cs=[(.3, (.035, .032, .03)), (.55, (.07, .065, .06)), (.8, (.11, .1, .09))], pc=(.17, .155, .14), pd=.25, ck=.7, poca=.85, verde=0.0),
}

@cached
def mat_ground(kind, period, seed=0.0):
    """Materiais de chão periódicos (período = bloco de tiles)."""
    m, nt, b = new_mat(f"chao_{kind}_{seed}")
    v, w = coords(nt, period, seed)
    if kind in ("calcamento", "laje", "cripta", "capela"):
        sc_ = {"calcamento": 3.6, "laje": 1.7, "cripta": 2.2, "capela": 1.5}[kind]
        rnd_ = .85 if kind == "calcamento" else .35
        vo = voronoi(nt, v, w, sc_, 'DISTANCE_TO_EDGE', seed, rnd_)
        vc = voronoi(nt, v, w, sc_, 'F1', seed, rnd_)
        gap = {"calcamento": .045, "laje": .02, "cripta": .025, "capela": .015}[kind]
        dome = {"calcamento": .22, "laje": .06, "cripta": .08, "capela": .05}[kind]
        r = ramp(nt, [(0, (0, 0, 0)), (gap, (1, 1, 1))]); L(nt, vo.outputs["Distance"], r.inputs[0])
        hd = ramp(nt, [(0, (0, 0, 0)), (dome, (1, 1, 1))]); hd.color_ramp.interpolation = 'EASE'
        L(nt, vo.outputs["Distance"], hd.inputs[0])
        n = noise(nt, v, w, 4, 8, .6, seed+1)
        nf = noise(nt, v, w, 30, 3, .5, seed+2)
        if kind == "calcamento": c1, c2 = (.15, .13, .11), (.055, .05, .046)
        elif kind == "laje": c1, c2 = (.14, .13, .115), (.06, .056, .05)
        elif kind == "cripta": c1, c2 = (.1, .1, .1), (.04, .04, .042)
        else: c1, c2 = (.17, .155, .13), (.08, .072, .062)
        stone = ramp(nt, [(0, c2), (1, c1)]); L(nt, vc.outputs["Color"], stone.inputs[0])
        col = mix(nt, stone.outputs[0], n.outputs["Color"], .3, 'OVERLAY')
        col = mix(nt, col, nf.outputs["Color"], .2, 'OVERLAY')
        # rachaduras finas
        ck = voronoi(nt, v, w, sc_*3.1, 'DISTANCE_TO_EDGE', seed+6, 1.0)
        ckm = noise(nt, v, w, 2.5, 3, .5, seed+8)
        ckr = ramp(nt, [(0, (0, 0, 0)), (.012, (1, 1, 1))]); L(nt, ck.outputs["Distance"], ckr.inputs[0])
        ckg = ramp(nt, [(.5, (1, 1, 1)), (.56, (0, 0, 0))]); L(nt, ckm.outputs["Fac"], ckg.inputs[0])
        crack = math_(nt, 'MAXIMUM', ckr.outputs[0], ckg.outputs[0])
        col = mix(nt, col, crack, 1, 'MULTIPLY')
        # lama/água nas juntas
        mud = mix(nt, (.012, .01, .008), col, r.outputs[0])
        # manchas úmidas (brilham com a luz)
        wn = noise(nt, v, w, 1.2, 4, .5, seed+9)
        wr = ramp(nt, [(.55, (0, 0, 0)), (.62, (1, 1, 1))]); L(nt, wn.outputs["Fac"], wr.inputs[0])
        col = mix(nt, mud, (.02, .018, .017), math_(nt, 'MULTIPLY', wr.outputs[0], .5))
        L(nt, col, b.inputs["Base Color"])
        rough = math_(nt, 'SUBTRACT', .85, math_(nt, 'MULTIPLY', wr.outputs[0], .6)); L(nt, rough, b.inputs["Roughness"])
        h = math_(nt, 'ADD', hd.outputs[0], math_(nt, 'MULTIPLY', n.outputs["Fac"], .2))
        h = math_(nt, 'SUBTRACT', h, math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', 1.0, crack), .3))
        bump(nt, b, math_(nt, 'ADD', h, math_(nt, 'MULTIPLY', nf.outputs["Fac"], .12)), .8, .06)
    elif kind in ("terra", "cemiterio", "ossos") or kind in SOLOS:
        S = SOLOS.get(kind, {})
        n = noise(nt, v, w, 1.5, 10, .62, seed)
        n2 = noise(nt, v, w, 9, 6, .55, seed+4)
        if kind == "terra": cs = [(.3, (.025, .019, .014)), (.5, (.07, .052, .036)), (.75, (.12, .095, .066))]
        elif kind == "cemiterio": cs = [(.3, (.02, .02, .015)), (.5, (.06, .054, .04)), (.75, (.09, .085, .06))]
        else: cs = [(.3, (.025, .022, .02)), (.55, (.065, .058, .05)), (.8, (.1, .09, .075))]
        if S: cs = S["cs"]
        r = ramp(nt, cs); L(nt, n.outputs["Fac"], r.inputs[0])
        col = mix(nt, r.outputs[0], n2.outputs["Color"], .2, 'OVERLAY')
        # pedrisco
        pv = voronoi(nt, v, w, 7, 'F1', seed+3)
        pc = (.16, .145, .12) if kind != "ossos" else (.32, .29, .22)
        if S: pc = S["pc"]
        pr = ramp(nt, [(.0, pc), (.22, pc), (.3, (0, 0, 0))]); L(nt, pv.outputs["Distance"], pr.inputs[0])
        pm = noise(nt, v, w, 3, 3, .5, seed+13)
        pth = S.get("pd", .45)
        pmr = ramp(nt, [(pth, (0, 0, 0)), (pth + .15, (1, 1, 1))]); L(nt, pm.outputs["Fac"], pmr.inputs[0])
        col = mix(nt, col, pr.outputs[0], pmr.outputs[0], 'ADD')
        # lama seca rachada
        mc = voronoi(nt, v, w, 2.6, 'DISTANCE_TO_EDGE', seed+21, 1.0)
        mcr = ramp(nt, [(0, (.25, .25, .25)), (.03, (1, 1, 1))]); L(nt, mc.outputs["Distance"], mcr.inputs[0])
        mcm = noise(nt, v, w, 1.4, 3, .5, seed+22)
        ckt = S.get("ck", .42)
        mcg = ramp(nt, [(ckt, (1, 1, 1)), (ckt + .08, (0, 0, 0))]); L(nt, mcm.outputs["Fac"], mcg.inputs[0])
        mcrack = math_(nt, 'MAXIMUM', mcr.outputs[0], mcg.outputs[0])
        col = mix(nt, col, mcrack, 1, 'MULTIPLY')
        if kind == "cemiterio":  # grama morta
            gn = noise(nt, v, w, 2.2, 6, .6, seed+11)
            gr = ramp(nt, [(.5, (0, 0, 0)), (.58, (1, 1, 1))]); L(nt, gn.outputs["Fac"], gr.inputs[0])
            gs = noise(nt, v, w, 60, 2, .5, seed+12)
            gcol = mix(nt, (.05, .048, .025), (.09, .08, .04), gs.outputs["Fac"])
            col = mix(nt, col, gcol, gr.outputs[0])
        # poças de lama
        wn = noise(nt, v, w, 1.0, 5, .5, seed+9)
        pt = S.get("poca", .6)
        wr = ramp(nt, [(pt, (0, 0, 0)), (pt + .06, (1, 1, 1))]); L(nt, wn.outputs["Fac"], wr.inputs[0])
        col = mix(nt, col, (.012, .009, .007) if not S.get("verde") else (.01, .03, .012), wr.outputs[0])
        if S.get("verde"):  # Amargo: brilho verde nas poças e nos cacos
            b.inputs["Emission Color"].default_value = (.25, 1.0, .2, 1)
            L(nt, math_(nt, 'MULTIPLY', wr.outputs[0], S["verde"] * 1.2), b.inputs["Emission Strength"])
        rip = None
        if S.get("ondas"):  # marcas de vento na areia (faixas a partir do ruído periódico)
            nr = noise(nt, v, w, .8, 3, .4, seed+31)
            rip = math_(nt, 'SINE', math_(nt, 'MULTIPLY', nr.outputs["Fac"], 90.0))
            ripc = math_(nt, 'ADD', .85, math_(nt, 'MULTIPLY', rip, .15 * S["ondas"]))
            col = mix(nt, col, ripc, 1, 'MULTIPLY')
        L(nt, col, b.inputs["Base Color"])
        L(nt, math_(nt, 'SUBTRACT', .92, math_(nt, 'MULTIPLY', wr.outputs[0], .8)), b.inputs["Roughness"])
        h = math_(nt, 'ADD', n.outputs["Fac"], math_(nt, 'MULTIPLY', n2.outputs["Fac"], .5))
        h = math_(nt, 'SUBTRACT', h, math_(nt, 'MULTIPLY', wr.outputs[0], .4))
        h = math_(nt, 'ADD', h, math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', pr.outputs[0], pmr.outputs[0]), 4.0))
        h = math_(nt, 'ADD', h, math_(nt, 'MULTIPLY', mcrack, .6))
        if rip is not None: h = math_(nt, 'ADD', h, math_(nt, 'MULTIPLY', rip, .5 * S["ondas"]))
        bump(nt, b, h, .7, .06)
    elif kind == "grade":   # chapa de ferro rebitada (porão do matadouro)
        tc = N(nt, "ShaderNodeTexCoord")
        sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, tc.outputs["Object"], sep.inputs[0])
        def frac(c, p): return math_(nt, 'FRACT', math_(nt, 'DIVIDE', c, p))
        fx, fy = frac(sep.outputs[0], T), frac(sep.outputs[1], T)
        def edge(f): return math_(nt, 'MINIMUM', f, math_(nt, 'SUBTRACT', 1.0, f))
        e = math_(nt, 'MINIMUM', edge(fx), edge(fy))
        er = ramp(nt, [(0, (0, 0, 0)), (.02, (1, 1, 1))]); L(nt, e, er.inputs[0])
        n = noise(nt, v, w, 5, 8, .65, seed)
        rr = ramp(nt, [(.45, (0, 0, 0)), (.6, (1, 1, 1))]); L(nt, n.outputs["Fac"], rr.inputs[0])
        rcol = mix(nt, (.05, .048, .046), (.13, .05, .02), rr.outputs[0])
        nf = noise(nt, v, w, 40, 3, .5, seed+1)
        col = mix(nt, rcol, nf.outputs["Color"], .2, 'OVERLAY')
        col = mix(nt, (.008, .007, .006), col, er.outputs[0])
        L(nt, col, b.inputs["Base Color"])
        L(nt, math_(nt, 'SUBTRACT', .8, math_(nt, 'MULTIPLY', rr.outputs[0], -.15)), b.inputs["Roughness"])
        L(nt, math_(nt, 'SUBTRACT', .8, rr.outputs[0]), b.inputs["Metallic"])
        bump(nt, b, math_(nt, 'ADD', er.outputs[0], math_(nt, 'MULTIPLY', nf.outputs["Fac"], .2)), .6, .03)
    return m

# ---------------------------------------------------------------- geometria
def obj(o, m=None, parent=None, smooth=False, bevel=0.0, segs=2):
    if m is not None:
        o.data.materials.clear(); o.data.materials.append(m)
    if parent: o.parent = parent
    if bevel:
        bv = o.modifiers.new("bv", 'BEVEL'); bv.width = bevel; bv.segments = segs; bv.limit_method = 'ANGLE'
    if smooth:
        for p in o.data.polygons: p.use_smooth = True
    return o

def box(m, loc, size, rot=(0, 0, 0), bevel=.01, parent=None):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=[math.radians(r) for r in rot])
    o = bpy.context.object; o.scale = (size[0]/2, size[1]/2, size[2]/2)
    bpy.ops.object.transform_apply(scale=True)
    return obj(o, m, parent, bevel=bevel)

def cyl(m, loc, r, depth, rot=(0, 0, 0), verts=16, parent=None, smooth=True, bevel=0.0, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=[math.radians(x) for x in rot])
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc, rotation=[math.radians(x) for x in rot])
    return obj(bpy.context.object, m, parent, smooth, bevel)

def sphere(m, loc, scale, parent=None, segs=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=segs//2, location=loc)
    o = bpy.context.object; o.scale = scale; bpy.ops.object.transform_apply(scale=True)
    return obj(o, m, parent, True)

def along(m, a, b, r, r2=None, verts=10, parent=None):
    a, b = Vector(a), Vector(b); d = b - a
    if r2 is None: bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=(a+b)/2)
    else: bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=d.length, location=(a+b)/2)
    o = bpy.context.object; o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()
    return obj(o, m, parent, True)

def torus(m, loc, R, r, rot=(0, 0, 0), parent=None):
    bpy.ops.mesh.primitive_torus_add(location=loc, rotation=[math.radians(x) for x in rot], major_radius=R, minor_radius=r, major_segments=24, minor_segments=8)
    return obj(bpy.context.object, m, parent, True)

def displace(o, strength=.03, scale=.3, seed=0, subdiv=2):
    if subdiv:
        s = o.modifiers.new("sub", 'SUBSURF'); s.levels = s.render_levels = subdiv; s.subdivision_type = 'SIMPLE'
    t = bpy.data.textures.new(f"dt{seed}", 'CLOUDS'); t.noise_scale = scale; t.noise_depth = 2
    d = o.modifiers.new("disp", 'DISPLACE'); d.texture = t; d.strength = strength; d.mid_level = .5
    d.texture_coords = 'GLOBAL'
    return o

def crumble(o, amount=.08, seed=0):
    """Desgasta arestas: subdivide e desloca (pedra quebrada)."""
    return displace(o, amount, .18 + (seed % 5) * .02, seed, 2)

def chain(m, a, b, links=10, r=.035, parent=None):
    a, b = Vector(a), Vector(b)
    for i in range(links):
        t = (i + .5) / links
        p = a.lerp(b, t) - Vector((0, 0, math.sin(t*math.pi) * .25 * (b-a).length * .3))
        torus(m, p, r, r*.28, (90 if i % 2 else 0, 0, math.degrees(math.atan2((b-a).y, (b-a).x))), parent)

def join(objs, name):
    objs = [o for o in objs if o]
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join(); o = bpy.context.object; o.name = name; return o

def flame(loc, s=1.0, parent=None, strength=14):
    """Chama: cones emissivos + luz pontual quente."""
    rnd = random.Random(int(loc[0]*100 + loc[1]*37))
    fm = mat_emit("fogo", (1, .32, .06), strength); core = mat_emit("fogo_nucleo", (1, .75, .35), strength*1.5)
    for k in range(6):
        h = rnd.uniform(.18, .38) * s
        cyl(fm if k else core, (loc[0]+rnd.uniform(-.06, .06)*s, loc[1]+rnd.uniform(-.06, .06)*s, loc[2]+h/2),
            rnd.uniform(.035, .07)*s, h, (rnd.uniform(-12, 12), rnd.uniform(-12, 12), 0), 7, parent, r2=0)
    return point((loc[0], loc[1], loc[2] + .35*s), (1, .45, .14), 160*s*s, .15*s, "fogo_luz")

def candle(loc, h=.12, parent=None, light=True):
    wax = mat_solid("cera", (.38, .33, .24), 0, .5)
    cyl(wax, (loc[0], loc[1], loc[2]+h/2), .018, h, verts=8, parent=parent)
    sphere(mat_emit("chama_vela", (1, .6, .2), 25), (loc[0], loc[1], loc[2]+h+.025), (.012, .012, .03), parent, 8)
    if light: point((loc[0], loc[1], loc[2]+h+.06), (1, .55, .2), 1.6, .02, "vela_luz")

# ---------------------------------------------------------------- render
def project_bounds(objs, extra_pts=()):
    pts = list(extra_pts)
    dg = bpy.context.evaluated_depsgraph_get()
    for o in objs:
        if o.type != 'MESH' or o.name.startswith("_"): continue
        oe = o.evaluated_get(dg)
        for c in oe.bound_box:
            pts.append(o.matrix_world @ Vector(c))
    return pts

def shadow_pts(pts, key_rot=KEY_ROT):
    """Pontos no chão onde caem as sombras dos pontos dados (luz 'key')."""
    l = Matrix.Rotation(math.radians(key_rot[2]), 4, 'Z') @ Matrix.Rotation(math.radians(key_rot[0]), 4, 'X')
    d = (l.to_3x3() @ Vector((0, 0, -1))).normalized()   # direção da luz
    out = []
    for p in pts:
        if d.z < -1e-3 and p.z > 0:
            t = -p.z / d.z; out.append(p + d*t)
    return out

def render_asset(path, objs=None, anchor=(0, 0, 0), samples=48, pad=6, shadows=True, extra=()):
    """Renderiza os objetos da cena enquadrados, a 64 px/m, e grava PNG + dados de âncora."""
    sc = bpy.context.scene
    if objs is None: objs = [o for o in sc.objects if o.type == 'MESH']
    cam = sc.camera or make_cam()
    pts = project_bounds(objs, extra)
    if shadows: pts += shadow_pts([p for p in pts])
    xs, ys = zip(*[screen_xy(p) for p in pts])
    ax, ay = screen_xy(anchor)
    x0, x1 = min(xs) - pad/PX_M, max(xs) + pad/PX_M
    y0, y1 = min(ys) - pad/PX_M, max(ys) + pad/PX_M
    W = int(math.ceil((x1 - x0) * PX_M)); H = int(math.ceil((y1 - y0) * PX_M))
    W += W % 2; H += H % 2
    # alinha o pixel da âncora a um inteiro
    x0 = ax - round((ax - x0) * PX_M) / PX_M; y1 = ay + round((y1 - ay) * PX_M) / PX_M
    cx, cy = x0 + W/PX_M/2, y1 - H/PX_M/2
    sc.render.resolution_x, sc.render.resolution_y = W*SS, H*SS
    cam.data.ortho_scale = max(W, H) / PX_M
    # posiciona a câmera sobre o centro (em coordenadas de tela)
    right = Vector((math.cos(math.radians(AZ)), math.sin(math.radians(AZ)), 0))
    cam.location = right*cx + up_vec()*cy + cam_dir()*120
    sc.cycles.samples = samples
    sc.render.filepath = path + "_raw.png"
    bpy.ops.render.render(write_still=True)
    meta = {"w": W, "h": H, "anchor": [round((ax - x0) * PX_M), round((y1 - ay) * PX_M)]}
    return meta

def up_vec():
    right = Vector((math.cos(math.radians(AZ)), math.sin(math.radians(AZ)), 0))
    u = cam_dir().cross(right)
    return u if u.z > 0 else -u

def prism(m, loc, w, d, h, parent=None):
    """Empena triangular: base w (eixo X) por d (eixo Y), altura h."""
    x, y, z = loc
    vs = [(-w/2, -d/2, 0), (w/2, -d/2, 0), (0, -d/2, h), (-w/2, d/2, 0), (w/2, d/2, 0), (0, d/2, h)]
    fs = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    me = bpy.data.meshes.new("prisma"); me.from_pydata(vs, [], fs); me.update()
    o = bpy.data.objects.new("prisma", me); bpy.context.scene.collection.objects.link(o)
    o.location = loc
    return obj(o, m, parent)
