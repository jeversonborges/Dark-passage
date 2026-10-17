# Panorâmica do Deserto de Absinto para o fundo da tela de entrada (estilo login do MU).
# Monta uma cena em perspectiva com os modelos do kit de ambiente (assets/ambiente/fontes) e renderiza com EEVEE.
# Uso (precisa de tela, por causa do EEVEE):
#   xvfb-run -a blender -b -P fontes/menu/panorama.py -- saida.png [largura altura]
import bpy, sys, os, math, random
from mathutils import Vector, noise

KIT = os.environ.get("KIT", "/mnt/project-files/assets/ambiente/fontes")
sys.path.insert(0, KIT)
import kit as K
import assets as A

argv = sys.argv[sys.argv.index("--") + 1:]
SAIDA = argv[0]
LARG, ALT = (int(argv[1]), int(argv[2])) if len(argv) > 2 else (3200, 1200)
rnd = random.Random(11)

K._cache.clear(); K.DUST = (.26, .19, .115); K.reset()
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
ee = sc.eevee
ee.taa_render_samples = int(os.environ.get('AMOSTRAS', 32))
ee.use_gtao = True; ee.gtao_distance = 2.0
ee.use_bloom = True; ee.bloom_threshold = 1.2; ee.bloom_intensity = .06; ee.bloom_radius = 6.5
ee.use_soft_shadows = True; ee.shadow_cube_size = '1024'; ee.shadow_cascade_size = '4096'
ee.use_volumetric_lights = True; ee.volumetric_tile_size = '4'; ee.volumetric_samples = 64
ee.volumetric_start = 1.0; ee.volumetric_end = 260.0
sc.render.film_transparent = False
sc.render.resolution_x, sc.render.resolution_y = LARG, ALT
sc.render.image_settings.color_mode = 'RGB'
sc.view_settings.view_transform = 'Filmic'
sc.view_settings.look = 'Medium High Contrast'
sc.view_settings.exposure = .6
M = A.M()

# ---------------------------------------------------------------- céu: noite de tempestade, horizonte aceso pelo Amargo
# No mundo, "Generated" é a direção do raio: Z = 0 no horizonte, 1 no zênite.
w = sc.world; w.use_nodes = True; nt = w.node_tree; nt.nodes.clear()
N_ = lambda k, **kw: K.N(nt, k, **kw)
out = N_("ShaderNodeOutputWorld")
tc = N_("ShaderNodeTexCoord")
sep = N_("ShaderNodeSeparateXYZ"); nt.links.new(tc.outputs["Generated"], sep.inputs[0])
# altura no céu
alt = K.ramp(nt, [(0.0, (.55, .30, .12)), (.04, (.22, .13, .07)), (.12, (.035, .03, .035)), (.35, (.004, .005, .010))])
nt.links.new(sep.outputs["Z"], alt.inputs[0])
# lado: âmbar da tempestade à esquerda, verde do Amargo à direita (azimute pelo X da direção)
lado = K.ramp(nt, [(.25, (1.0, .45, .18)), (.5, (.85, .6, .4)), (.8, (.55, .75, .5))])
mxs = N_("ShaderNodeMath", operation='MULTIPLY_ADD'); mxs.inputs[1].default_value = .5; mxs.inputs[2].default_value = .5
nt.links.new(sep.outputs["X"], mxs.inputs[0]); nt.links.new(mxs.outputs[0], lado.inputs[0])
ceu = K.mix(nt, alt.outputs[0], lado.outputs[0], 1.0, 'MULTIPLY')
# nuvens rasgadas, mais densas no alto, iluminadas por baixo pelo horizonte
vec = N_("ShaderNodeVectorMath", operation='DIVIDE'); nt.links.new(tc.outputs["Generated"], vec.inputs[0])
zz = N_("ShaderNodeMath", operation='ADD'); nt.links.new(sep.outputs["Z"], zz.inputs[0]); zz.inputs[1].default_value = .12
cz = N_("ShaderNodeCombineXYZ"); nt.links.new(zz.outputs[0], cz.inputs[0]); nt.links.new(zz.outputs[0], cz.inputs[1]); nt.links.new(zz.outputs[0], cz.inputs[2])
nt.links.new(cz.outputs[0], vec.inputs[1])
nz = K.noise(nt, vec.outputs[0], None, 1.6, 10, .6, 3.0)
nr = K.ramp(nt, [(.42, (0, 0, 0)), (.68, (1, 1, 1))]); nt.links.new(nz.outputs["Fac"], nr.inputs[0])
nuv_cor = K.mix(nt, (.012, .012, .016), (.16, .15, .11), K.math_(nt, 'POWER', K.math_(nt, 'SUBTRACT', 1.0, sep.outputs["Z"]), 6.0))
ceu2 = K.mix(nt, ceu, nuv_cor, K.math_(nt, 'MULTIPLY', nr.outputs[0], .85))
# lua: disco frio com halo, alto à direita
lua_dir = Vector((.38, .82, .43)).normalized()
dp = N_("ShaderNodeVectorMath", operation='DOT_PRODUCT'); nt.links.new(tc.outputs["Generated"], dp.inputs[0]); dp.inputs[1].default_value = lua_dir
disco = K.ramp(nt, [(.99955, (0, 0, 0)), (.9997, (1, 1, 1))]); nt.links.new(dp.outputs["Value"], disco.inputs[0])
halo = K.ramp(nt, [(.96, (0, 0, 0)), (1.0, (1, 1, 1))]); nt.links.new(dp.outputs["Value"], halo.inputs[0])
tapa = K.math_(nt, 'SUBTRACT', 1.0, K.math_(nt, 'MULTIPLY', nr.outputs[0], .8))   # nuvem passando na frente
lua_c = K.math_(nt, 'MULTIPLY', K.math_(nt, 'ADD', K.math_(nt, 'MULTIPLY', disco.outputs[0], 14.0), K.math_(nt, 'MULTIPLY', K.math_(nt, 'POWER', halo.outputs[0], 3.0), .5)), tapa)
lua_rgb = K.mix(nt, (0, 0, 0), (.75, .85, 1.0), 1.0)
lua_m = N_("ShaderNodeVectorMath", operation='SCALE'); nt.links.new(lua_rgb, lua_m.inputs[0]); nt.links.new(lua_c, lua_m.inputs["Scale"])
soma = N_("ShaderNodeVectorMath", operation='ADD'); nt.links.new(ceu2, soma.inputs[0]); nt.links.new(lua_m.outputs[0], soma.inputs[1])
bg = N_("ShaderNodeBackground"); bg.inputs["Strength"].default_value = 1.0
nt.links.new(soma.outputs[0], bg.inputs["Color"]); nt.links.new(bg.outputs[0], out.inputs["Surface"])
# névoa do Amargo baixa (perspectiva atmosférica); um cubo de volume só perto do chão
bpy.ops.mesh.primitive_cube_add(location=(0, 120, 6)); nv = bpy.context.object; nv.scale = (260, 200, 9); nv.name = "nevoa"
vm = bpy.data.materials.new("nevoa"); vm.use_nodes = True; vn = vm.node_tree; vn.nodes.clear()
vo = vn.nodes.new("ShaderNodeOutputMaterial"); vp = vn.nodes.new("ShaderNodeVolumePrincipled")
vp.inputs["Color"].default_value = (.42, .40, .32, 1); vp.inputs["Density"].default_value = .0035; vp.inputs["Anisotropy"].default_value = .55
vn.links.new(vp.outputs[0], vo.inputs["Volume"]); nv.data.materials.append(vm)

# ---------------------------------------------------------------- chão: dunas, com o leito do Rio Amargo cortando até o horizonte
RIO0 = [(-30, -30), (-14, -8), (-8, 6), (4, 18), (8, 34), (2, 52), (12, 74), (34, 96), (40, 122), (70, 150), (90, 200), (130, 260)]
def _cr(p0, p1, p2, p3, t):
    return tuple(.5 * ((2*b) + (-a + c)*t + (2*a - 5*b + 4*c - d)*t*t + (-a + 3*b - 3*c + d)*t*t*t) for a, b, c, d in zip(p0, p1, p2, p3))
RIO = []
for i in range(len(RIO0) - 1):
    p0 = RIO0[max(i - 1, 0)]; p1 = RIO0[i]; p2 = RIO0[i + 1]; p3 = RIO0[min(i + 2, len(RIO0) - 1)]
    for k in range(8): RIO.append(_cr(p0, p1, p2, p3, k / 8))
RIO.append(RIO0[-1])
def dist_rio(x, y):
    best = 1e9
    for (ax, ay), (bx, by) in zip(RIO, RIO[1:]):
        vx, vy = bx - ax, by - ay; L2 = vx*vx + vy*vy
        t = max(0, min(1, ((x - ax)*vx + (y - ay)*vy) / L2))
        best = min(best, math.hypot(x - (ax + t*vx), y - (ay + t*vy)))
    return best
def largura(y): return 2.6 + max(0, y) * .02

def altura(x, y):
    d = max(0.0, y - 20)
    h = noise.noise(Vector((x*.03, y*.03, 0.3))) * 1.6 + noise.noise(Vector((x*.1, y*.1, 1.7))) * .3
    h += (d * .045) * (1.2 + noise.noise(Vector((x*.012, y*.012, 5.0))))        # dunas que sobem para o horizonte
    h += max(0.0, -x - 20) * .08 * (1 + .5*noise.noise(Vector((x*.02, y*.02, 2.0))))   # morro da capela à esquerda
    dr = dist_rio(x, y); L = largura(y)
    f = min(1.0, max(0.0, (dr - L) / (5.0 + d * .03)))
    return h * f * f * (3 - 2*f) + (1 - f) * (-1.0)

import bmesh
bm = bmesh.new()
NX, NY = 240, 200
vs = {}
for i in range(NX + 1):
    for j in range(NY + 1):
        x = -200 + 400 * i / NX
        y = -40 + 360 * (j / NY) ** 1.6      # mais densa perto da câmera
        vs[i, j] = bm.verts.new((x, y, altura(x, y)))
for i in range(NX):
    for j in range(NY):
        bm.faces.new((vs[i, j], vs[i+1, j], vs[i+1, j+1], vs[i, j+1]))
me = bpy.data.meshes.new("chao"); bm.to_mesh(me); bm.free()
chao = bpy.data.objects.new("chao", me); sc.collection.objects.link(chao)
for p in me.polygons: p.use_smooth = True
# areia de deserto em escala de paisagem: manchas, ondulações de vento, pó verde nas baixadas
am, ant, ab = K.new_mat("areia_paisagem")
geo = K.N(ant, "ShaderNodeNewGeometry")
n1 = K.noise(ant, geo.outputs["Position"], None, .025, 6, .55, 2.0)
r1 = K.ramp(ant, [(.3, (.12, .085, .055)), (.55, (.25, .18, .11)), (.75, (.36, .27, .17))]); K.L(ant, n1.outputs["Fac"], r1.inputs[0])
sp = K.N(ant, "ShaderNodeSeparateXYZ"); K.L(ant, geo.outputs["Position"], sp.inputs[0])
baixo = K.ramp(ant, [(.0, (1, 1, 1)), (1.0, (0, 0, 0))]); K.L(ant, K.math_(ant, 'ADD', K.math_(ant, 'MULTIPLY', sp.outputs["Z"], .4), .4), baixo.inputs[0])
col = K.mix(ant, r1.outputs[0], (.05, .07, .035), K.math_(ant, 'MULTIPLY', baixo.outputs[0], .7))
K.L(ant, col, ab.inputs["Base Color"]); ab.inputs["Roughness"].default_value = .92
wv = K.N(ant, "ShaderNodeTexWave", wave_type='BANDS', bands_direction='X')
wv.inputs["Scale"].default_value = .9; wv.inputs["Distortion"].default_value = 6; wv.inputs["Detail"].default_value = 3
K.L(ant, geo.outputs["Position"], wv.inputs[0])
K.bump(ant, ab, wv.outputs["Fac"], .35, .05)
chao.data.materials.append(am)

# água do rio: fita que segue o leito; escura e espelhada, verde-amarga, brilho fraco por baixo
bm = bmesh.new(); ant_l = ant_r = None; prev = None
pts = RIO
for k, (x, y) in enumerate(pts):
    if k + 1 < len(pts): dx, dy = pts[k+1][0] - x, pts[k+1][1] - y
    nx, ny = -dy, dx; Ln = math.hypot(nx, ny) or 1; nx /= Ln; ny /= Ln
    L = largura(y) + .8
    l = bm.verts.new((x + nx*L, y + ny*L, -.55)); r = bm.verts.new((x - nx*L, y - ny*L, -.55))
    if prev: bm.faces.new((prev[0], prev[1], r, l))
    prev = (l, r)
me = bpy.data.meshes.new("rio"); bm.to_mesh(me); bm.free()
rio = bpy.data.objects.new("rio", me); sc.collection.objects.link(rio)
agua_m = bpy.data.materials.new("agua_amarga"); agua_m.use_nodes = True
an = agua_m.node_tree; b = an.nodes["Principled BSDF"]
b.inputs["Base Color"].default_value = (.004, .025, .02, 1); b.inputs["Roughness"].default_value = .06; b.inputs["Specular IOR Level"].default_value = .9
b.inputs["Emission Color"].default_value = (.25, 1.0, .18, 1); b.inputs["Emission Strength"].default_value = .04
nn = an.nodes.new("ShaderNodeTexNoise"); nn.inputs["Scale"].default_value = 2.5; nn.inputs["Detail"].default_value = 8
bp = an.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = .45; bp.inputs["Distance"].default_value = .1
an.links.new(nn.outputs["Fac"], bp.inputs["Height"]); an.links.new(bp.outputs["Normal"], b.inputs["Normal"])
rio.data.materials.append(agua_m)
ee.use_ssr = True; ee.ssr_quality = .5; ee.ssr_thickness = .5

# ---------------------------------------------------------------- modelos do kit
def colocar(nome, x, y, rot=0.0, esc=1.0, z=None, **kw):
    info = A.REG.get(nome)
    if info is None: print("SEM", nome); return None
    antes = set(bpy.data.objects)
    try: info["fn"](M, **kw)
    except Exception as ex:
        print("ERRO", nome, ex); return None
    novos = [o for o in bpy.data.objects if o not in antes]
    piv = bpy.data.objects.new("piv_" + nome, None); sc.collection.objects.link(piv)
    bury = info.get("bury", 0.0)
    for o in novos:
        if o.parent is None:
            if bury and not (o.data and getattr(o.data, "materials", None) and len(o.data.materials) and o.data.materials[0].name.startswith("areia_monte")):
                o.location.z -= bury
            o.parent = piv
    piv.location = (x, y, altura(x, y) - .05 if z is None else z)
    piv.rotation_euler = (0, 0, math.radians(rot)); piv.scale = (esc, esc, esc)
    return piv

def no_rio(t):
    i = min(int(t * (len(RIO) - 1)), len(RIO) - 2); f = t * (len(RIO) - 1) - i
    (ax, ay), (bx, by) = RIO[i], RIO[i + 1]
    return ax + (bx - ax) * f, ay + (by - ay) * f, math.degrees(math.atan2(by - ay, bx - ax))

# a Capela de São Lázaro no morro à esquerda, rosácea acesa, contra o brilho âmbar da tempestade
colocar("capela_sao_lazaro", -40, 58, rot=-62, esc=1.6)
colocar("mar_de_lapides", -30, 44, rot=-40, esc=1.3)
colocar("torre_sino", -56, 74, rot=-30, esc=1.6)
# a Ponte do Bonde cruzando o rio no meio do caminho
bx, by, ang = no_rio(.36)
colocar("ponte_ferro_bonde", bx, by, rot=ang, esc=1.5, z=-.3)
# São Lázaro engolida pela areia, recortada no horizonte
colocar("predio_enterrado", 30, 170, rot=12, esc=2.6)
colocar("predio_enterrado", 74, 196, rot=-20, esc=2.2)
colocar("torre_relogio_enterrada", 52, 150, rot=-15, esc=2.4)
colocar("chamine_enterrada", 8, 186, rot=0, esc=2.8)
colocar("cupula_estacao", -34, 176, rot=20, esc=2.2)
colocar("torre_tombada", 104, 172, rot=40, esc=2.2)
colocar("moinho_ruina", 26, 64, rot=10, esc=1.3)
colocar("ossada_gigante", 46, 88, rot=-35, esc=2.2)
colocar("bonde_veleiro", -20, 26, rot=60, esc=1.2)
# postes do telégrafo seguindo a estrada morta até a capela
for k in range(9): colocar("poste_telegrafo", -6 - k * 3.6, 8 + k * 6.5, rot=-30, esc=1.2)
# árvores secas emoldurando
colocar("arvore_morta_grande", 15, -4, rot=200, esc=1.7)
colocar("arvore_morta", -13, 2, rot=40, esc=1.2)
colocar("arvore_morta_grande", 36, 40, rot=80, esc=1.3)
for k in range(14):
    x, y = rnd.uniform(-70, 90), rnd.uniform(16, 110)
    if dist_rio(x, y) > 9: colocar(rnd.choice(["arvore_morta", "arvore_morta_2"]), x, y, rot=rnd.uniform(0, 360), esc=rnd.uniform(.9, 1.4))
# juncos e pedras na beira da água
for k in range(60):
    t = rnd.uniform(0, .5)
    x, y, ang = no_rio(t)
    lado = rnd.choice([-1, 1]); a = math.radians(ang + 90)
    off = (largura(y) + rnd.uniform(.6, 2.2)) * lado
    x += math.cos(a) * off; y += math.sin(a) * off
    if y > -6: colocar(rnd.choice(["juncos", "juncos", "pedras_rio"]), x, y, rot=rnd.uniform(0, 360), esc=rnd.uniform(.9, 1.4))
# acampamento da Vigília em primeiro plano, à direita: lâmpada de arco e fogueira
colocar("lampada_arco", 11, 6, rot=-20, esc=1.1)
colocar("fogueira", 6, 2)
colocar("tenda_vigilia", 16, 10, rot=-30)
colocar("estandarte_rasgado", 3, 8, rot=10, esc=1.2)

# ---------------------------------------------------------------- luz
K.sun("lua", (.62, .72, 1.0), 1.4, (62, 0, 160), .02)      # vem da lua, alta atrás à direita: contraluz nas silhuetas
K.sun("fill", (.35, .3, .25), .18, (70, 0, -20))
K.point((6, 2, 1.0), (1, .45, .15), 700, .3, "fogo")
K.point((11, 6, 6.5), (.6, .85, 1.0), 900, .2, "arco")
K.point((-40, 58, 6.0), (1, .3, .12), 2500, 2.0, "rosacea")
for t in (.12, .22, .32, .42):
    x, y, _ = no_rio(t)
    K.point((x, y, 2.5), (.35, 1, .25), 35 + y * .6, 4.0, "amargo")

# ---------------------------------------------------------------- câmera: baixa, na beira do rio, olhando o vale até o horizonte
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
cam.data.lens = 22; cam.data.sensor_width = 36; cam.data.clip_end = 800
cam.location = (-2, -22, 3.4)
alvo = Vector((4, 60, 7.5))
cam.rotation_euler = (alvo - cam.location).to_track_quat('-Z', 'Y').to_euler()
sc.camera = cam

sc.render.filepath = SAIDA
bpy.ops.render.render(write_still=True)
print("PANORAMA_OK", SAIDA)
