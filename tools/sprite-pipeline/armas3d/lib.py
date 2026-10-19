# Ferramentas comuns das armas 3D fiéis às artes (usadas por arma_*.py).
# Espaço do modelo: metros, origem na pegada, +Z da pegada para a ponta, +X largura, +Y espessura.
import bpy, bmesh, math, os, sys
from mathutils import Vector
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "personagens"))
from rig import mat

M = {}

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    M.clear()
    M.update(
        ferro=mat("ferro_negro_arma", (.05, .045, .045), .8, .45, dirt=.5, grime=.35),
        cobre=mat("cobre_arma", (.36, .19, .09), 1, .38, dirt=.45, grime=.3),
        osso=mat("osso_arma", (.26, .23, .19), 0, .5, dirt=.6, grime=.4),
        couro=mat("couro_arma", (.05, .03, .02), 0, .55, dirt=.6),
        pano=mat("pano_vermelho_arma", (.38, .03, .03), 0, .85, dirt=.45, grime=.3),
        lava=mat("lava_fenda_arma", (1, .3, .05), 0, .2, emit=(1, .25, .04), strength=2.2, dirt=0, grime=0),
        olho=mat("olho_brasa_arma", (1, .2, .05), 0, .2, emit=(1, .15, .02), strength=12.0, dirt=0, grime=0),
    )

def finish(o, m):
    o.data.materials.append(m)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.shade_smooth()
    return o

def add(op, m, loc, scale=(1, 1, 1), rot=(0, 0, 0), **kw):
    """Primitiva com rotação em graus; a escala entra depois da rotação."""
    getattr(bpy.ops.mesh, op)(location=loc, rotation=[math.radians(r) for r in rot], **kw)
    o = bpy.context.active_object
    o.scale = scale
    return finish(o, m)

def plate(name, pts, m, t, y=0.0):
    """Placa no plano XZ (lista de (x, z)), espessura t em Y centrada em y. Polígono não convexo OK."""
    bm = bmesh.new()
    front = [bm.verts.new((x, y - t / 2, z)) for x, z in pts]
    back = [bm.verts.new((x, y + t / 2, z)) for x, z in pts]
    bm.faces.new(front)
    bm.faces.new(back[::-1])
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([front[i], front[j], back[j], back[i]])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(o)
    return finish(o, m)

def ring(cx, cz, ro, ri, a0, a1, steps=10, tip=0.0):
    """Anel crescente: arco externo de a0 a a1 e volta pelo interno. tip > 0 faz gancho nas pontas."""
    outer = [(cx + ro * math.cos(a), cz + ro * math.sin(a)) for a in [a0 + (a1 - a0) * k / steps for k in range(steps + 1)]]
    inner = [(cx + ri * math.cos(a), cz + ri * math.sin(a)) for a in [a1 - (a1 - a0) * k / steps for k in range(steps + 1)]]
    if tip:
        outer.append((cx + (ro + tip) * math.cos(a1 + .16), cz + (ro + tip) * math.sin(a1 + .16)))
        inner.append((cx + (ri - tip * .4) * math.cos(a0 - .16), cz + (ri - tip * .4) * math.sin(a0 - .16)))
    return outer + inner

def espelha(pts):
    return [(-x, z) for x, z in pts]

def lado(pts, side):
    return espelha(pts) if side < 0 else pts

def cilindro(m, a, b, r, verts=10):
    """Haste entre dois pontos 3D."""
    a, b = Vector(a), Vector(b)
    d = b - a
    mid = (a + b) / 2
    o = add("primitive_cylinder_add", m, tuple(mid), scale=(r, r, d.length / 2), vertices=verts)
    o.rotation_mode = 'QUATERNION'
    o.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(d.normalized())
    return o

def render_8(out, objs, target, ortho, res=384, amostras=40):
    """Gira o conjunto (não a câmera) em 8 direções, câmera iso 2:1 (30 graus), fundo transparente."""
    sc = bpy.context.scene
    world = bpy.data.worlds.new("mundo"); sc.world = world; world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (0.01, 0.01, 0.012, 1)
    sun = bpy.data.lights.new("sol", 'SUN'); sun.energy = 2.2
    so = bpy.data.objects.new("sol", sun); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(55), 0, math.radians(35))
    luz = bpy.data.lights.new("brasa", 'POINT'); luz.energy = 120; luz.color = (1, .35, .12)
    lo = bpy.data.objects.new("brasa", luz); sc.collection.objects.link(lo); lo.location = (.6, -.9, .5)
    cd = bpy.data.cameras.new("cam"); cd.type = 'ORTHO'; cd.ortho_scale = ortho
    cam = bpy.data.objects.new("cam", cd); sc.collection.objects.link(cam); sc.camera = cam
    target = Vector(target)
    cam.location = target + Vector((0, -2.0, .9))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'
    sc.cycles.samples = amostras; sc.cycles.use_denoising = False
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = res
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    for k in range(8):
        for o in objs:
            o.rotation_euler = (0, 0, math.radians(k * 45))
        sc.render.filepath = os.path.join(out, f"render_{k}.png")
        bpy.ops.render.render(write_still=True)
    for o in objs:
        o.rotation_euler = (0, 0, 0)

def exporta(out, objs, nome):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, nome + ".glb"), export_format='GLB',
                              use_selection=True, export_apply=True)

def contato(out, res=384):
    from PIL import Image
    ims = [Image.open(os.path.join(out, f"render_{k}.png")).convert("RGBA") for k in range(8)]
    sheet = Image.new("RGBA", (res * 4, res * 2), (12, 12, 14, 255))
    for k, im in enumerate(ims):
        sheet.alpha_composite(im, ((k % 4) * res, (k // 4) * res))
    sheet.save(os.path.join(out, "contact_8dir.png"))

def tris(objs):
    return sum(len(p.vertices) - 2 for o in objs for p in o.data.polygons)

def main(build, nome, alvo, ortho, res=384):
    """Ponto de entrada comum: uso `python arma_x.py -- <saida>`."""
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["/tmp/arma"]
    out = argv[0]; os.makedirs(out, exist_ok=True)
    reset()
    objs = build()
    render_8(out, objs, alvo, ortho, res=res, amostras=int(os.environ.get("AMOSTRAS", 40)))
    contato(out, res)
    exporta(out, objs, nome)
    print("ok", out, "tris~", tris(objs))

def corrente(m, a, b, elos=9, r=.0075, fio=.0017):
    """Corrente de elos entre dois pontos 3D, elos alternando de plano (como em corrente de verdade)."""
    a, b = Vector(a), Vector(b)
    out = []
    for k in range(elos):
        p = a.lerp(b, k / max(1, elos - 1))
        rot = (90, 0, 0) if k % 2 == 0 else (0, 90, 0)
        out.append(add("primitive_torus_add", m, tuple(p), rot=rot, major_radius=r, minor_radius=fio,
                       major_segments=8, minor_segments=4))
    return out

def cone(m, loc, direcao_deg_y=0, rot_x=0, raio=.02, comp=.08, lados=6):
    """Espinho cônico com base em raio, ponta para +Z girado em Y (graus); rot_x=180 aponta para baixo."""
    return add("primitive_cone_add", m, loc, rot=(rot_x, direcao_deg_y, 0), vertices=lados,
               radius1=raio, radius2=.002, depth=comp)

def _cubo(nome, loc, dims, m):
    """Cubo unitário com as dimensões dadas, escala aplicada (o modificador trabalha no espaço local)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = nome
    o.scale = dims
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(m)
    return o

def _modifica(o, tipo, nome, **kw):
    bpy.context.view_layer.objects.active = o
    md = o.modifiers.new(name=nome, type=tipo)
    for k, v in kw.items():
        setattr(md, k, v)
    bpy.ops.object.modifier_apply(modifier=md.name)

def caveira(loc, tam, m_osso, m_olho):
    """Caveira pela técnica do tutorial 'Easy Skull Modelling' (Blender): cubo chanfrado, subdivisão, órbitas e
    abertura do nariz cortadas por booleano, mandíbula separada com fileira de dentes, olhos de brasa dentro das órbitas.
    Retorna [objeto de osso (unido), olhos]. Tudo em metros, centro em `loc`, face para -Y, crânio para +Z."""
    craneo = _cubo("craneo", loc, (.42 * tam, .38 * tam, .44 * tam), m_osso)
    _modifica(craneo, 'BEVEL', "chanfro", width=.13 * tam, segments=3)
    _modifica(craneo, 'SUBSURF', "suave", levels=2, render_levels=2)
    # órbitas e nariz
    x0, y0, z0 = loc
    cortes = []
    for s in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=.105 * tam, location=(x0 + s * .14 * tam, y0 - .17 * tam, z0 + .03 * tam))
        cortes.append(bpy.context.active_object)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x0, y0 - .2 * tam, z0 - .07 * tam))
    nariz = bpy.context.active_object
    nariz.scale = (.09 * tam, .14 * tam, .12 * tam)
    bpy.ops.object.transform_apply(scale=True)
    cortes.append(nariz)
    for c in cortes:
        _modifica(craneo, 'BOOLEAN', "corte", operation='DIFFERENCE', object=c)
        bpy.ops.object.select_all(action='DESELECT'); c.select_set(True); bpy.ops.object.delete()
    # mandíbula separada
    mandibula = _cubo("mandibula", (x0, y0 + .02 * tam, z0 - .34 * tam), (.34 * tam, .3 * tam, .15 * tam), m_osso)
    _modifica(mandibula, 'BEVEL', "chanfro", width=.05 * tam, segments=2)
    _modifica(mandibula, 'SUBSURF', "suave", levels=1, render_levels=1)
    partes = [craneo, mandibula]
    # dentes: fileira de blocos chanfrados na borda da mandíbula
    for k in range(6):
        x = x0 + (-.12 + k * .048) * tam
        d = _cubo(f"dente_{k}", (x, y0 - .13 * tam, z0 - .25 * tam), (.035 * tam, .03 * tam, .06 * tam), m_osso)
        _modifica(d, 'BEVEL', "chanfro", width=.008 * tam, segments=1)
        partes.append(d)
    # une tudo num objeto só
    bpy.ops.object.select_all(action='DESELECT')
    for p in partes:
        p.select_set(True)
    bpy.context.view_layer.objects.active = craneo
    bpy.ops.object.join()
    osso = bpy.context.active_object
    osso.name = "caveira"
    # olhos de brasa, dentro das órbitas
    olhos = [add("primitive_uv_sphere_add", m_olho, (x0 + s * .14 * tam, y0 - .19 * tam, z0 + .03 * tam),
                 scale=(.035 * tam, .03 * tam, .035 * tam)) for s in (-1, 1)]
    return [osso] + olhos
