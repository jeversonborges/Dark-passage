# Árvore morta refeita em low-poly, no estilo Ferrugem Sagrada (fosco, sujo, faces planas).
# Mesma pegada do kit (3x3 tiles), âncora na base e mesmo render do kit, para trocar no jogo
# sem mexer no mapa. Exporta as partes separadas (skills/dark-passage-isometric-world, seção 4):
#   base   = tronco, raízes, galhos baixos e corda (sólido, ordenável no mundo)
#   copa   = galhos altos e ramos (overhead: some quando o player passa por baixo)
# Todas as camadas compartilham o mesmo quadro e âncora, então se sobrepõem sem deslocamento.
# Uso: blender -b -P arvore_refeita.py -- <pasta_de_saida>
# Orçamento: prop (skills_lib.ORCAMENTO), meta da thread 500 a 2000 tris; conta tris no log.
# Materiais: casca fosca, rugosidade alta, sem clearcoat (REFERENCIAS.md, seção 5).
import bpy, bmesh, math, os, sys, random, json
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
FONTES = os.path.join(HERE, "..", "..", "..", "assets", "ambiente", "fontes")
sys.path.insert(0, FONTES)
sys.path.insert(0, os.path.join(HERE, ".."))
import kit as K
import assets as A
from skills_lib import orcamento

LADOS_TRONCO = 8
LADOS_GALHO = 6
LADOS_RAMO = 5
ALTURA_COPA = 2.6   # galhos cujo ponto de partida passa disto ficam na camada copa

def tubo(bm, pts, lados, mat_idx=0, fechado=False, rnd=None, ruido=.07, ponta_quebrada=False):
    """Tubo de anéis por pts = [(centro, raio), ...]. Faces planas, sem subdivisão.
    fechado: laço (anel ligado ao primeiro). ponta_quebrada: último anel dentado, fechado em leque."""
    pts = [(Vector(c), r) for c, r in pts]
    n = len(pts)
    aneis = []
    for i, (c, r) in enumerate(pts):
        if fechado:
            a, b = pts[(i-1) % n][0], pts[(i+1) % n][0]
        else:
            a, b = pts[max(i-1, 0)][0], pts[min(i+1, n-1)][0]
        t = (b - a).normalized()
        ref = Vector((0, 0, 1)) if abs(t.z) < .9 else Vector((1, 0, 0))
        u = t.cross(ref).normalized(); v = t.cross(u)
        dentes = ponta_quebrada and i == n-1
        anel = []
        for k in range(lados):
            th = 2*math.pi*k/lados
            rr = r*(1 + rnd.uniform(-ruido, ruido)) if rnd else r
            if dentes: rr *= (.55 if k % 2 else 1.0)
            anel.append(bm.verts.new(c + (u*math.cos(th) + v*math.sin(th))*rr))
        aneis.append(anel)
    bm.verts.ensure_lookup_table()
    m = len(aneis) if fechado else len(aneis) - 1
    for i in range(m):
        A_, B_ = aneis[i], aneis[(i+1) % len(aneis)]
        for k in range(lados):
            f = bm.faces.new((A_[k], A_[(k+1) % lados], B_[(k+1) % lados], B_[k]))
            f.material_index = mat_idx
    if not fechado:
        if not ponta_quebrada:
            f = bm.faces.new(aneis[-1][::-1]); f.material_index = mat_idx
        else:
            topo = bm.verts.new(pts[-1][0])
            for k in range(lados):
                f = bm.faces.new((aneis[-1][k], aneis[-1][(k+1) % lados], topo)); f.material_index = mat_idx
        f = bm.faces.new(aneis[0]); f.material_index = mat_idx

# Tronco: base alargada, inclinado, quebrado no alto
TRONCO = [((0, 0, -.05), .52), ((0, 0, .18), .43), ((.08, .04, 1.3), .36), ((.22, -.02, 2.45), .29),
          ((.30, .05, 3.5), .21), ((.36, .0, 4.35), .16), ((.40, .02, 4.8), .12)]
# Galhos principais: (ponto, raio) do tronco para fora
GALHOS = [
    [((.25, 0, 2.5), .13), ((.9, .12, 2.75), .09), ((1.5, .2, 2.95), .06), ((2.0, .25, 3.05), .03)],   # sustenta a corda
    [((.28, .02, 3.0), .14), ((-.1, .25, 3.4), .10), ((-.6, .5, 3.95), .05), ((-.95, .62, 4.3), .02)],
    [((.30, 0, 3.7), .11), ((.35, -.45, 4.1), .08), ((.5, -.95, 4.55), .035)],
    [((.10, 0, 3.9), .10), ((-.15, -.3, 4.35), .06), ((-.45, -.55, 4.85), .025)],
    [((-.05, .05, 2.2), .12), ((-.5, -.2, 2.35), .08), ((-.95, -.35, 2.45), .04)],
]
RAIZES = [.0, 1.57, 3.14, 4.71]   # quatro raízes saindo da base

def _rot(axis, ang):
    return Matrix.Rotation(ang, 3, axis.normalized())

def _malha(nome, bm, mats):
    me = bpy.data.meshes.new(nome)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(nome, me)
    bpy.context.scene.collection.objects.link(ob)
    for mt in mats: me.materials.append(mt)
    for p in me.polygons: p.use_smooth = False
    return ob

def arvore_nova(seed=7):
    """Versão nova em duas camadas: (base, copa). Tronco de 8 lados, galhos de 6, ramos de 5.
    A corda de enforcado fica na base (está na altura do player)."""
    rnd = random.Random(seed)
    bm_base, bm_copa = bmesh.new(), bmesh.new()
    tubo(bm_base, TRONCO, LADOS_TRONCO, 0, rnd=rnd, ruido=.08, ponta_quebrada=True)
    for ang in RAIZES:
        d = Vector((math.cos(ang + rnd.uniform(-.3, .3)), math.sin(ang + rnd.uniform(-.3, .3)), 0))
        tubo(bm_base, [(d*.2 + Vector((0, 0, .2)), .24), (d*.7 + Vector((0, 0, .06)), .11), (d*1.25 + Vector((0, 0, .01)), .03)],
             LADOS_RAMO, 0, rnd=rnd, ruido=.12)
    for g in GALHOS:
        bm = bm_base if g[0][0][2] < ALTURA_COPA else bm_copa
        tubo(bm, g, LADOS_GALHO, 0, rnd=rnd)
        # ramos finos saindo do meio e da ponta de cada galho
        for idx in (1, len(g)-1):
            p0, r0 = g[idx]
            d = (Vector(g[idx][0]) - Vector(g[idx-1][0])).normalized()
            for s in range(2):
                ang = rnd.uniform(.5, .9) * (1 if s else -1)
                axis = Vector((0, 0, 1)).cross(d) if abs(d.z) < .9 else Vector((1, 0, 0))
                nd = (_rot(axis, ang) @ d); nd.z += .2; nd.normalize()
                L = rnd.uniform(.3, .55)
                tubo(bm, [(Vector(p0), r0*.8), (Vector(p0) + nd*L*.5, .03), (Vector(p0) + nd*L, .008)], LADOS_RAMO, 0, rnd=rnd)
    # corda de enforcado presa ao galho 0 (camada base)
    tubo(bm_base, [((1.5, .2, 2.9), .014), ((1.5, .2, 2.2), .012), ((1.5, .2, 1.62), .012)], 4, 1, rnd=None)
    laço = [((1.5 + .085*math.cos(2*math.pi*k/8), .2, 1.5 + .085*math.sin(2*math.pi*k/8)), .012) for k in range(8)]
    tubo(bm_base, laço, 4, 1, fechado=True)
    casca = K.mat_wood("casca_lp", (.085, .062, .045))
    corda = K.mat_solid("corda", (.1, .08, .05), 0, .9)
    return _malha("arvore_base", bm_base, [casca, corda]), _malha("arvore_copa", bm_copa, [casca])

def tris(obs):
    dg = bpy.context.evaluated_depsgraph_get(); n = 0
    for ob in obs:
        ev = ob.evaluated_get(dg); me = ev.to_mesh(); me.calc_loop_triangles()
        n += len(me.loop_triangles); ev.to_mesh_clear()
    return n

def antiga():
    """Objetos antigos (assets.py, arvore_morta) em volta da origem."""
    before = set(bpy.data.objects)
    A.REG["arvore_morta"]["fn"](A.M())
    return [o for o in bpy.data.objects if o not in before and o.type == 'MESH']

def render_antiga(tag, ang, out, samples=64):
    K._cache.clear(); K.DUST = (.26, .19, .115); K.CLAMP = True
    K.reset(); K.make_cam(); K.lights(False)
    bpy.context.scene.cycles.use_denoising = False   # o blender do apt não tem OpenImageDenoise
    K.shadow_catcher()
    objs = antiga()
    for o in objs: o.rotation_euler.z = math.radians(ang)
    bpy.context.view_layer.update()
    return K.render_asset(f"{out}/{tag}", objs, samples=samples)

def render_nova(out, ang, samples=64):
    """Renderiza as duas camadas da árvore nova no mesmo quadro (mesma âncora e mesmo tamanho)."""
    K._cache.clear(); K.DUST = (.26, .19, .115); K.CLAMP = True
    K.reset(); K.make_cam(); K.lights(False)
    bpy.context.scene.cycles.use_denoising = False
    K.shadow_catcher()
    base, copa = arvore_nova()
    for o in (base, copa): o.rotation_euler.z = math.radians(ang)
    bpy.context.view_layer.update()
    pts = K.project_bounds([base, copa])     # quadro comum às duas camadas, com a sombra inteira dentro
    extra = pts + K.shadow_pts(pts)
    metas = {}
    for nome, ob, outro in (("base", base, copa), ("copa", copa, base)):
        outro.hide_render = True
        metas[nome] = K.render_asset(f"{out}/nova_{nome}_{ang}", [ob], samples=samples, shadows=False, extra=extra)
        outro.hide_render = False
    return metas

if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:]
    out = argv[0]; os.makedirs(out, exist_ok=True)
    lo, hi = orcamento("prop")
    meta = {"antiga": {}, "nova_base": {}, "nova_copa": {}}
    for k in range(8):
        ang = 45*k
        meta["antiga"][k] = render_antiga(f"antiga_{k}", ang, out)
        m = render_nova(out, ang)
        meta["nova_base"][k] = m["base"]; meta["nova_copa"][k] = m["copa"]
        print("OK direcao", k, flush=True)
    K._cache.clear(); K.reset(); K.make_cam(); K.lights(False)
    n_tris = tris(arvore_nova())
    print(f"tris nova={n_tris} (prop {lo}-{hi}; meta da thread 500-2000)", flush=True)
    json.dump({"tris_nova": n_tris, "meta": meta}, open(f"{out}/meta.json", "w"), ensure_ascii=False, indent=1)
