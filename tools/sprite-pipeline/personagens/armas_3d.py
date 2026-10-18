# Modelos 3D das armas pintadas (ícones do Jefin): um construtor por item, no formato de assets/armas/modelos.
#
# Espaço do modelo: metros, origem no centro da pegada, +Z da pegada para a ponta, +X = fio da lâmina,
# +Y = espessura. Materiais: emissivo = brilho; nome começando em "tinta" = cor do item (R na máscara).
#
# Uso: blender -b --factory-startup -P armas_3d.py -- <saida_dir> <item> [<item> ...]
#   gera <saida>/<item>.glb e <saida>/<item>_render.png (prévia, fundo transparente).
import bpy, bmesh, math, sys, os
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.read_factory_settings(use_empty=True)
from rig import mat, prim, along

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["/tmp/armas3d", "cimitarra_de_janes"]
OUT = argv[0]; os.makedirs(OUT, exist_ok=True)
ITENS = argv[1:]

# ------------------------------------------------------------------ helpers
def malha(nome, material, verts_top, verts_bot):
    """Lâmina chata: contorno (lista de pontos XZ) extrudado em Y, de -espessura a +espessura."""
    me = bpy.data.meshes.new(nome); ob = bpy.data.objects.new(nome, me)
    bpy.context.scene.collection.objects.link(ob)
    bm = bmesh.new()
    top = [bm.verts.new(v) for v in verts_top]
    bot = [bm.verts.new(v) for v in verts_bot]
    n = len(top)
    bm.faces.new(top); bm.faces.new(list(reversed(bot)))
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([top[i], top[j], bot[j], bot[i]])
    bm.normal_update()
    bm.to_mesh(me); bm.free()
    me.materials.append(material)
    for p in me.polygons: p.use_smooth = True
    return ob

def lamina(material, base_x, z0, L, curva, larg_fio, larg_costas, esp, pontas=28, gancho=0.0):
    """Cimitarra: fio convexo em +X, costas finas em -X, ponta fechada no alto. Espessura plana em Y."""
    edge, back = [], []
    for k in range(pontas + 1):
        t = k / pontas
        xs = base_x + curva * t * t + gancho * t ** 8     # o gancho se fecha só na ponta
        z = z0 + L * t
        # fio: enche no início e some na ponta; cai com a curva
        de = larg_fio * (1 - t) ** 0.85 * (1 + 0.25 * math.sin(math.pi * t))
        db = larg_costas * (1 - t) ** 0.6
        edge.append((xs + de, z))
        back.append((xs - db, z))
    contorno = edge + list(reversed(back))
    topo = [(x, esp, z) for x, z in contorno]
    base = [(x, -esp, z) for x, z in contorno]
    return malha("lamina", material, topo, base)

def faixa(material, x, y, z_topo, comp, larg, dx=0.0):
    """Tira de tecido pendurada: retângulo fino no plano XZ, a ponta inferior um pouco mais estreita."""
    contorno = [(x - larg, z_topo), (x + larg, z_topo), (x + larg * .6 + dx, z_topo - comp), (x - larg * .6 + dx, z_topo - comp)]
    topo = [(a, y + .0008, b) for a, b in contorno]
    base = [(a, y - .0008, b) for a, b in contorno]
    return malha("tecido", material, topo, base)

def tubo(material, pontos, raios):
    """Haste com afinamento: segmentos ligados entre os pontos, raio de cada extremidade."""
    objs = []
    for a, b, r0, r1 in zip(pontos, pontos[1:], raios, raios[1:]):
        o = along("primitive_cylinder_add", material, a, b, (r0 + r1) / 2, vertices=12)
        objs.append(o)
    return objs

def curva_bezier(p0, p1, p2, n):
    out = []
    for k in range(n + 1):
        t = k / n
        out.append((1 - t) ** 2 * Vector(p0) + 2 * (1 - t) * t * Vector(p1) + t * t * Vector(p2))
    return out

# ------------------------------------------------------------------ Cimitarra de Janes (lendária) e a versão Deus
def cimitarra(deus=False):
    ferro = mat("tinta_lamina_janes", (.62, .5, .3), .95, .28, dirt=.5, grime=.35)
    ouro = mat("ouro_janes", (.72, .5, .14), 1, .26, dirt=.4, grime=.2)
    couro = mat("couro_janes", (.09, .05, .03), .05, .55, dirt=.6, grime=.4)
    tecido = mat("tecido_sangue_janes", (.55, .05, .04), 0, .75, dirt=.5, grime=.3)
    rubi = mat("rubi_janes", (.5, .02, .03), .1, .08, dirt=0, grime=0)
    penas = mat("penas_azuis_janes", (.1, .22, .42), 0, .6, dirt=.4, grime=.2)

    L = 0.42 if not deus else 0.5
    z0 = 0.17                                  # início da lâmina, acima do punho e da guarda
    curva = 0.16 if not deus else 0.2
    larg = 0.085 if not deus else 0.1
    gancho = 0.03 if not deus else 0.04
    lam = lamina(ferro, base_x=0.0, z0=z0, L=L, curva=curva, larg_fio=larg, larg_costas=0.014, esp=0.006, gancho=gancho)
    lam.name = "lamina_janes"
    # filete de ouro embutido no fio: uma faixa mais grossa que a lâmina, do espinhaço até metade da largura
    lamina(ouro, base_x=0.0, z0=z0 + .004, L=L - .01, curva=curva, larg_fio=larg * .45, larg_costas=0.0, esp=.0068)

    # fileiras de filigrana dourada ao longo da lâmina (pequenos cabos e pontos)
    for k in range(9):
        t = 0.1 + 0.85 * k / 8
        xs = curva * t * t
        de = larg * (1 - t) ** 0.85
        prim("primitive_uv_sphere_add", ouro, Vector((xs + de * .5, .0075, z0 + L * t)), (.0048, .0025, .0048), segments=8, ring_count=5)

    # guarda em garra: dois chifres de ouro que sobem do punho e se curvam para fora
    for lado in (1, -1):
        pts = curva_bezier((0, 0, z0 - .01), (lado * .075, 0, z0 - .01), (lado * .1, 0, z0 + .035), 6)
        raios = [.011, .0098, .0084, .0068, .0052, .0036, .0018]
        tubo(ouro, pts, raios)
        # ponta da garra
        prim("primitive_cone_add", ouro, pts[-1], (.0055, .0055, .018), rot=(0, 0, 0), vertices=10)
    # miolo da guarda: bloco de ouro com o rubi
    prim("primitive_cube_add", ouro, Vector((0, 0, z0 - .004)), (.024, .006, .014))
    prim("primitive_uv_sphere_add", rubi, Vector((0, .0065, z0 - .004)), (.0075, .0035, .0075), segments=10, ring_count=6)

    # punho de couro com anéis de latão/ouro
    tubo(couro, [Vector((0, 0, -.09)), Vector((0, 0, z0 - .02))], [.0135, .0145])
    for k in range(6):
        z = -.075 + k * .018
        prim("primitive_torus_add", ouro, Vector((0, 0, z)), (1, 1, 1), major_radius=.0148, minor_radius=.0028,
             major_segments=18, minor_segments=6)
    # pomo: esfera de ouro com uma argola
    prim("primitive_uv_sphere_add", ouro, Vector((0, 0, -.1)), (.026, .026, .026), segments=14, ring_count=8)
    prim("primitive_torus_add", ouro, Vector((0, 0, -.095)), (1, 1, 1), major_radius=.024, minor_radius=.0035,
         major_segments=20, minor_segments=6)

    # tassel de tecido vermelho pendurado da guarda (e, na versão Deus, penas azuis)
    for x, y, comp in ((-.03, 0, .13), (.03, 0, .11), (0, .02, .14)):
        faixa(tecido, x, y, z0 - .01, comp, .0085)
    if deus:
        for x in (-.035, -.012, .014):
            faixa(penas, x - .01, .004, z0 - .04, .075, .02, dx=.006)

    # selecionar tudo para exportar
    bpy.ops.object.select_all(action='SELECT')
    return bpy.context.selected_objects


# ------------------------------------------------------------------ Escudo da Cruz Remida (Anjo, segunda mão)
def escudo_cruz():
    """Escudo de latão em gota: aro de ouro, campo de esmalte azul, cruz de ouro com as pontas abertas e penas
    brancas presas dos dois lados. Espaço do escudo (empunhadura "escudo"): +Z = antebraço (para cima),
    +Y = face de fora, +X = largura."""
    ouro = mat("ouro_cruz", (.95, .66, .24), .7, .24, dirt=.2, grime=.1)
    azul = mat("esmalte_azul_cruz", (.12, .32, .78), .25, .16, dirt=.2, grime=.08)
    penas = mat("pena_marfim_cruz", (.78, .74, .66), 0, .55, dirt=.4, grime=.25)
    tinta = mat("tinta_latao_escudo", (.4, .32, .18), .9, .35, dirt=.5, grime=.35)

    contorno = [(0, .33), (.12, .31), (.18, .24), (.19, .1), (.16, -.05), (.09, -.2), (0, -.36),
                (-.09, -.2), (-.16, -.05), (-.19, .1), (-.18, .24), (-.12, .31)]
    # aro de ouro (escudo cheio atrás), campo de esmalte azul à frente, mais estreito
    malha("aro_escudo", ouro, [(x, .012, z) for x, z in contorno], [(x, -.012, z) for x, z in contorno])
    campo = [(x * .8, z * .9 + .02) for x, z in contorno]
    malha("campo_escudo", azul, [(x, .02, z) for x, z in campo], [(x, .012, z) for x, z in campo])
    # cruz de ouro com as pontas abertas
    prim("primitive_cube_add", ouro, Vector((0, .03, .0)), (.022, .01, .27))
    prim("primitive_cube_add", ouro, Vector((0, .03, .1)), (.13, .01, .024))
    for z, x in ((.27, 0), (-.27, 0), (.1, .13), (.1, -.13)):
        prim("primitive_cone_add", ouro, Vector((x, .03, z)), (.026, .026, .05), rot=(0, 0, 0 if x == 0 else 90), vertices=8)
    # penas brancas presas do lado de trás, abrindo para fora
    for lado in (1, -1):
        for k, (z, ang) in enumerate(((.12, 28), (-.02, 36), (-.16, 44))):
            base = Vector((lado * .16, -.02, z)); tip = base + Vector((lado * .13, -.04, -.14))
            pena = [(base.x - .024, base.z), (base.x + .024, base.z), (tip.x + .008, tip.z), (tip.x - .008, tip.z)]
            malha("pena_escudo", penas, [(a, -.02 + k * .002, b) for a, b in pena], [(a, -.024 + k * .002, b) for a, b in pena])
    return bpy.context.scene.objects

# ------------------------------------------------------------------ export e render
def exporta(arquivo):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.gltf(filepath=arquivo, export_format='GLB', use_selection=True, export_apply=True)

def render(arquivo, frente=-1):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.samples = int(os.environ.get("AMOSTRAS", 64))
    sc.cycles.use_denoising = False
    try: sc.cycles.device = 'CPU'
    except Exception: pass
    sc.render.film_transparent = True
    sc.render.resolution_x, sc.render.resolution_y = 900, 1500
    sc.view_settings.look = 'None'
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (.02, .02, .025, 1)
    for nome, ld, loc, e in (("luz_chave", 'SUN', (2, -3, 4), 3.0), ("luz_fill", 'AREA', (-2, 2, 2), 60)):
        dados = bpy.data.lights.new(nome, ld); dados.energy = e
        if ld == 'AREA': dados.size = 2
        lo = bpy.data.objects.new(nome, dados); sc.collection.objects.link(lo); lo.location = loc
        lo.rotation_euler = (math.radians(50), 0, math.radians(35))
    # ortográfica, enquadrando a arma inteira; visão de frente levemente de lado, como o ícone
    cam = bpy.data.cameras.new("cam"); cam.type = 'ORTHO'
    co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
    # enquadra as malhas da cena inteira
    pts = [o.matrix_world @ Vector(c) for o in sc.objects if o.type == 'MESH' for c in o.bound_box]
    lo_ = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi_ = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    alvo = (lo_ + hi_) / 2; cam.ortho_scale = max(hi_ - lo_) * 1.12
    origem = alvo + Vector((1.1, 3.0 * frente, .25))
    co.location = origem
    co.rotation_euler = (alvo - origem).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = arquivo
    bpy.ops.render.render(write_still=True)

CONSTRUTORES = {
    "cimitarra_de_janes": lambda: cimitarra(deus=False),
    "deus_cimitarra_de_janes": lambda: cimitarra(deus=True),
    "escudo_da_cruz_remida": escudo_cruz,
}

for item in ITENS:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    CONSTRUTORES[item]()
    exporta(f"{OUT}/{item}.glb")
    # escudos mostram a face de fora (+Y); armas, a face de -Y, como no ícone
    render(f"{OUT}/{item}_render.png", frente=1 if item.startswith("escudo") else -1)
    print("ok", item)
