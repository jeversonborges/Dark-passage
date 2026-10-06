# Vinheta da Planície dos Cavaleiros (nível 60 a 80, 6ª trombeta).
# Chão-base de enxofre cristalizado; destaques: placas de basalto e rachaduras de fumaça.
# Vocabulário: cavaleiro petrificado (4 poses, repetido em fileiras), lança quebrada, estandarte
# de pedra, fumarola, cratera de fogo, carroça de guerra, corrente gigante, pilar de basalto,
# tenda rasgada. Marco: a Ponte Partida sobre o rio seco. Habitada: Acampamento da Ponte Partida.
# Uso: Q=1 blender42 -b -P area_planicie_dos_cavaleiros.py      (MODELO=1 renderiza só o cavaleiro)
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, Matrix
import cena as C
from cena import por
K = C.K
from kit import box, cyl, sphere, along, torus, displace, crumble, point
Q = os.environ.get("Q") == "1"
MODELO = os.environ.get("MODELO") == "1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "planicie_dos_cavaleiros")
ENXOFRE = (.36, .27, .055)
FOGO = (1.0, .62, .14)

# ================================================================ materiais
@K.cached
def mat_enxofre(seed=0.0):
    """Chão: enxofre amarelo-ocre cristalizado, com grão de cristal, crosta pálida e veios escuros."""
    m, nt, b = K.new_mat("chao_enxofre")
    v, w = K.coords(nt)
    n1 = K.noise(nt, v, w, .07, 6, .6, seed)
    n2 = K.noise(nt, v, w, .5, 8, .6, seed + 2)
    nf = K.noise(nt, v, w, 14, 4, .5, seed + 4)
    r = K.ramp(nt, [(.28, (.075, .052, .016)), (.45, (.2, .145, .035)), (.6, (.34, .26, .05)), (.78, (.44, .36, .12))])
    K.L(nt, K.math_(nt, 'ADD', K.math_(nt, 'MULTIPLY', n1.outputs["Fac"], .6), K.math_(nt, 'MULTIPLY', n2.outputs["Fac"], .4)), r.inputs[0])
    col = K.mix(nt, r.outputs[0], nf.outputs["Color"], .22, 'OVERLAY')
    # grão de cristal (facetas)
    vc = K.voronoi(nt, v, w, 5.0, 'F1', seed + 6)
    col = K.mix(nt, col, vc.outputs["Color"], .14, 'OVERLAY')
    ve = K.voronoi(nt, v, w, 5.0, 'DISTANCE_TO_EDGE', seed + 6)
    ver = K.ramp(nt, [(0, (.45, .4, .35)), (.06, (1, 1, 1))]); K.L(nt, ve.outputs["Distance"], ver.inputs[0])
    col = K.mix(nt, col, ver.outputs[0], 1, 'MULTIPLY')
    # crosta pálida em placas
    cn = K.noise(nt, v, w, .9, 5, .6, seed + 9)
    cr = K.ramp(nt, [(.58, (0, 0, 0)), (.66, (1, 1, 1))]); K.L(nt, cn.outputs["Fac"], cr.inputs[0])
    col = K.mix(nt, col, (.5, .43, .2), K.math_(nt, 'MULTIPLY', cr.outputs[0], .55))
    # veios escuros (lama de enxofre queimado)
    ck = K.voronoi(nt, v, w, .45, 'DISTANCE_TO_EDGE', seed + 11)
    ckm = K.noise(nt, v, w, .3, 3, .5, seed + 12)
    ckr = K.ramp(nt, [(0, (.05, .035, .015)), (.025, (1, 1, 1))]); K.L(nt, ck.outputs["Distance"], ckr.inputs[0])
    ckg = K.ramp(nt, [(.45, (1, 1, 1)), (.55, (0, 0, 0))]); K.L(nt, ckm.outputs["Fac"], ckg.inputs[0])
    col = K.mix(nt, col, ckr.outputs[0], K.math_(nt, 'SUBTRACT', 1.0, ckg.outputs[0]), 'MULTIPLY')
    # fuligem esparsa
    sn = K.noise(nt, v, w, .18, 4, .55, seed + 15)
    sr = K.ramp(nt, [(.6, (0, 0, 0)), (.75, (1, 1, 1))]); K.L(nt, sn.outputs["Fac"], sr.inputs[0])
    col = K.mix(nt, col, (.03, .026, .02), K.math_(nt, 'MULTIPLY', sr.outputs[0], .6))
    K.L(nt, col, b.inputs["Base Color"])
    K.L(nt, K.math_(nt, 'ADD', .5, K.math_(nt, 'MULTIPLY', ve.outputs["Distance"], 1.2)), b.inputs["Roughness"])
    h = K.math_(nt, 'ADD', K.math_(nt, 'MULTIPLY', ver.outputs[0], .5), K.math_(nt, 'MULTIPLY', nf.outputs["Fac"], .5))
    K.bump(nt, b, K.math_(nt, 'ADD', h, cr.outputs[0]), .5, .05)
    return m

@K.cached
def mat_basalto_chao(seed=0.0):
    """Placa de basalto: colunas hexagonais vistas de cima, juntas cheias de pó de enxofre."""
    m, nt, b = K.new_mat("basalto_chao")
    v, w = K.coords(nt)
    vo = K.voronoi(nt, v, w, 1.1, 'DISTANCE_TO_EDGE', seed, .55)
    vc = K.voronoi(nt, v, w, 1.1, 'F1', seed, .55)
    n = K.noise(nt, v, w, 3, 6, .6, seed + 1)
    st = K.ramp(nt, [(0, (.018, .017, .018)), (1, (.06, .057, .056))]); K.L(nt, vc.outputs["Color"], st.inputs[0])
    col = K.mix(nt, st.outputs[0], n.outputs["Color"], .3, 'OVERLAY')
    j = K.ramp(nt, [(0, (1, 1, 1)), (.05, (0, 0, 0))]); K.L(nt, vo.outputs["Distance"], j.inputs[0])
    col = K.mix(nt, col, (.3, .22, .05), K.math_(nt, 'MULTIPLY', j.outputs[0], .85))
    K.L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .6
    hd = K.ramp(nt, [(0, (0, 0, 0)), (.08, (1, 1, 1))]); K.L(nt, vo.outputs["Distance"], hd.inputs[0])
    K.bump(nt, b, K.math_(nt, 'ADD', hd.outputs[0], K.math_(nt, 'MULTIPLY', n.outputs["Fac"], .3)), .8, .06)
    return m

@K.cached
def mat_leito(seed=0.0):
    """Leito seco do rio: cascalho de basalto e lama queimada rachada, com crosta de enxofre nas bordas."""
    m, nt, b = K.new_mat("leito_seco")
    v, w = K.coords(nt)
    n = K.noise(nt, v, w, .6, 8, .6, seed)
    r = K.ramp(nt, [(.3, (.02, .018, .016)), (.55, (.055, .048, .038)), (.8, (.1, .085, .055))]); K.L(nt, n.outputs["Fac"], r.inputs[0])
    col = r.outputs[0]
    pv = K.voronoi(nt, v, w, 9, 'F1', seed + 3)
    pr = K.ramp(nt, [(0, (.08, .075, .07)), (.25, (.06, .055, .05)), (.32, (0, 0, 0))]); K.L(nt, pv.outputs["Distance"], pr.inputs[0])
    col = K.mix(nt, col, pr.outputs[0], 1, 'ADD')
    mc = K.voronoi(nt, v, w, 1.6, 'DISTANCE_TO_EDGE', seed + 5)
    mr = K.ramp(nt, [(0, (.1, .1, .1)), (.035, (1, 1, 1))]); K.L(nt, mc.outputs["Distance"], mr.inputs[0])
    col = K.mix(nt, col, mr.outputs[0], 1, 'MULTIPLY')
    cn = K.noise(nt, v, w, 1.2, 4, .6, seed + 7)
    cr = K.ramp(nt, [(.62, (0, 0, 0)), (.7, (1, 1, 1))]); K.L(nt, cn.outputs["Fac"], cr.inputs[0])
    col = K.mix(nt, col, (.32, .25, .06), K.math_(nt, 'MULTIPLY', cr.outputs[0], .7))
    K.L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .9
    K.bump(nt, b, K.math_(nt, 'ADD', mr.outputs[0], K.math_(nt, 'MULTIPLY', n.outputs["Fac"], .5)), .7, .05)
    return m

@K.cached
def mat_estatua(name="estatua", brilho=0.0, seed=0.0):
    """Pedra cinza-escura das estátuas; com brilho > 0, rachaduras que soltam luz amarelo-fogo."""
    m, nt, b = K.new_mat(name)
    v, w = K.coords(nt, None, seed)
    n1 = K.noise(nt, v, w, 3.0, 8, .6, seed); n2 = K.noise(nt, v, w, 14, 4, .5, seed + 3)
    r = K.ramp(nt, [(.3, (.026, .025, .026)), (.7, (.085, .082, .08))]); K.L(nt, n1.outputs["Fac"], r.inputs[0])
    col = K.mix(nt, r.outputs[0], n2.outputs["Color"], .18, 'OVERLAY')
    # rachaduras finas
    ck = K.voronoi(nt, v, w, 2.2, 'DISTANCE_TO_EDGE', seed + 6)
    ckm = K.noise(nt, v, w, 1.5, 3, .5, seed + 8)
    ckr = K.ramp(nt, [(0, (1, 1, 1)), (.02, (0, 0, 0))]); K.L(nt, ck.outputs["Distance"], ckr.inputs[0])
    ckg = K.ramp(nt, [(.45, (0, 0, 0)), (.55, (1, 1, 1))]); K.L(nt, ckm.outputs["Fac"], ckg.inputs[0])
    crack = K.math_(nt, 'MULTIPLY', ckr.outputs[0], ckg.outputs[0])
    col = K.mix(nt, col, (.005, .005, .005), crack)
    col = K.grime(nt, col, v, w, 3.4, .55)
    K.L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .82
    if brilho:
        b.inputs["Emission Color"].default_value = (*FOGO, 1)
        K.L(nt, K.math_(nt, 'MULTIPLY', crack, brilho), b.inputs["Emission Strength"])
    h = K.math_(nt, 'SUBTRACT', K.math_(nt, 'ADD', n1.outputs["Fac"], K.math_(nt, 'MULTIPLY', n2.outputs["Fac"], .4)), K.math_(nt, 'MULTIPLY', crack, .6))
    K.bump(nt, b, h, .6, .03)
    return m

@K.cached
def mat_basalto():
    return K.mat_stone("basalto", (.05, .048, .05), (.014, .013, .014), 2.6, 0.0, None, 4.0, 5.0)

@K.cached
def mat_silhar():
    return K.mat_brick("silhar_basalto", ("wall", K.T*2), 7.0, (.05, .047, .046), 4.5, 0.0, K.T, .34, .018)

@K.cached
def mat_cristal():
    m, nt, b = K.new_mat("cristal_enxofre")
    v, w = K.coords(nt)
    n = K.noise(nt, v, w, 6, 4, .5, 1.0)
    col = K.mix(nt, (.55, .44, .08), (.3, .2, .03), n.outputs["Fac"])
    K.L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .28
    b.inputs["Subsurface Weight"].default_value = .25; b.inputs["Subsurface Radius"].default_value = (.4, .3, .05)
    return m

@K.cached
def mat_lava():
    """Enxofre derretido no fundo das crateras: amarelo-fogo pulsante."""
    m, nt, b = K.new_mat("enxofre_fundido")
    v, w = K.coords(nt)
    n = K.noise(nt, v, w, 2.5, 6, .6, 4.0)
    vo = K.voronoi(nt, v, w, 3.0, 'DISTANCE_TO_EDGE', 2.0)
    crust = K.ramp(nt, [(0, (0, 0, 0)), (.08, (1, 1, 1))]); K.L(nt, vo.outputs["Distance"], crust.inputs[0])
    hot = K.ramp(nt, [(.35, (1, .3, .03)), (.7, (1, .78, .25))]); K.L(nt, n.outputs["Fac"], hot.inputs[0])
    K.L(nt, K.mix(nt, hot.outputs[0], (.03, .02, .01), crust.outputs[0]), b.inputs["Base Color"])
    K.L(nt, hot.outputs[0], b.inputs["Emission Color"])
    K.L(nt, K.math_(nt, 'MULTIPLY', K.math_(nt, 'SUBTRACT', 1.0, crust.outputs[0]), 9.0), b.inputs["Emission Strength"])
    return m

@K.cached
def mat_fumaca(name="fumaca", cor=(.42, .38, .26), dens=.55, seed=0.0):
    """Coluna de fumaça amarelada (volume) que afina e some no alto."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
    out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
    pv = K.N(nt, "ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (*cor, 1)
    pv.inputs["Anisotropy"].default_value = .3
    tc = K.N(nt, "ShaderNodeTexCoord")
    sep = K.N(nt, "ShaderNodeSeparateXYZ"); K.L(nt, tc.outputs["Generated"], sep.inputs[0])
    nz = K.noise(nt, tc.outputs["Object"], None, .9, 5, .62, seed)
    nr = K.ramp(nt, [(.42, (0, 0, 0)), (.68, (1, 1, 1))]); K.L(nt, nz.outputs["Fac"], nr.inputs[0])
    dx = K.math_(nt, 'SUBTRACT', sep.outputs[0], .5); dy = K.math_(nt, 'SUBTRACT', sep.outputs[1], .5)
    r2 = K.math_(nt, 'ADD', K.math_(nt, 'MULTIPLY', dx, dx), K.math_(nt, 'MULTIPLY', dy, dy))
    rad = K.math_(nt, 'MAXIMUM', K.math_(nt, 'SUBTRACT', 1.0, K.math_(nt, 'MULTIPLY', r2, 4.0)), 0.0)
    z = sep.outputs[2]
    fade = K.math_(nt, 'MULTIPLY', K.math_(nt, 'SUBTRACT', 1.0, z), K.math_(nt, 'MINIMUM', K.math_(nt, 'MULTIPLY', z, 8.0), 1.0))
    d = K.math_(nt, 'MULTIPLY', K.math_(nt, 'MULTIPLY', nr.outputs[0], rad), K.math_(nt, 'MULTIPLY', fade, dens))
    K.L(nt, d, pv.inputs["Density"])
    K.L(nt, pv.outputs[0], out.inputs["Volume"])
    return m

# ================================================================ helpers
def pedra(mat, loc, esc, seed, amt=.06):
    o = sphere(mat, loc, esc, segs=10); crumble(o, amt, seed); return o

def cone(mat, a, b, r, r2=.005, verts=6):
    return along(mat, a, b, r, r2, verts)

def fumaca(loc, h=6.0, r=.8, incl=(0, 0), dens=.55, seed=0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r, depth=h, location=(loc[0], loc[1], loc[2] + h/2),
                                        rotation=(math.radians(incl[0]), math.radians(incl[1]), 0))
    o = bpy.context.object; o.data.materials.append(mat_fumaca("fumaca", dens=dens, seed=float(seed % 7)))
    o.visible_shadow = False
    return o

def agrupar(objs, pivo, rot):
    """Gira um conjunto de objetos em volta de um pivô (graus em X, Y, Z)."""
    e = bpy.data.objects.new("pivo", None); bpy.context.scene.collection.objects.link(e)
    e.location = pivo; bpy.context.view_layer.update()
    for o in objs:
        if o.parent is None:
            o.parent = e; o.matrix_parent_inverse = e.matrix_world.inverted()
    e.rotation_euler = [math.radians(a) for a in rot]
    bpy.context.view_layer.update()
    return e

def novos(fn):
    before = set(bpy.data.objects); fn(); return [o for o in bpy.data.objects if o not in before]

# ================================================================ o cavaleiro petrificado
POSE_GALOPE = dict(
    fd=[(.7, -.2, 1.15), (1.12, -.23, .9), (1.45, -.23, .78), (1.6, -.23, .7)],   # dianteira estendida
    fe=[(.65, .2, 1.1), (.88, .23, .66), (.7, .23, .45), (.78, .23, .34)],         # dianteira recolhida
    td=[(-.72, -.22, 1.15), (-.58, -.25, .74), (-1.0, -.25, .48), (-1.15, -.25, .05)],
    te=[(-.7, .22, 1.15), (-.42, .25, .72), (-.74, .25, .42), (-.56, .25, .05)])
POSE_EMPINADO = dict(
    fd=[(.7, -.2, 1.15), (1.05, -.23, .75), (.82, -.23, .5), (.9, -.23, .36)],
    fe=[(.65, .2, 1.1), (1.0, .23, .88), (.86, .23, .58), (.98, .23, .48)],
    td=[(-.72, -.22, 1.15), (-.6, -.25, .7), (-.98, -.25, .42), (-.95, -.25, .02)],
    te=[(-.7, .22, 1.15), (-.5, .25, .7), (-.86, .25, .38), (-.78, .25, .02)])

def perna(S, pts, quebrada=False):
    rs = [.15, .1, .075, .07]
    n = 2 if quebrada else 3
    for i in range(n):
        along(S, pts[i], pts[i+1], rs[i], rs[i+1], 10)
        sphere(S, pts[i+1], (rs[i+1]*1.15,)*3, segs=10)
    if quebrada:
        pedra(S, pts[2], (.1, .1, .07), 3, .03)
    else:
        p = Vector(pts[3]); d = (Vector(pts[3]) - Vector(pts[2])).normalized()
        along(S, p, p + d*.12, .085, .095, 10)        # casco

def cabeca_leao(S, G, r, falta_orelha=False, luz=True):
    """Cabeça de leão na ponta do pescoço do cavalo: juba em espinhos, boca aberta com fogo dentro."""
    sphere(S, (1.32, 0, 2.12), (.3, .24, .26), segs=14)                      # crânio
    sphere(S, (1.24, 0, 2.28), (.2, .2, .1), segs=12)                        # testa
    sphere(S, (1.6, 0, 2.08), (.22, .16, .1), segs=12)                       # maxilar
    sphere(S, (1.79, 0, 2.11), (.07, .1, .06), segs=10)                      # focinho
    o = sphere(S, (1.53, 0, 1.86), (.2, .14, .055), segs=12)                 # mandíbula aberta
    o.rotation_euler = (0, math.radians(22), 0)
    sphere(G, (1.56, 0, 1.97), (.16, .095, .07), segs=12)                    # garganta em brasa
    for sy in (-1, 1):
        cone(S, (1.72, sy*.08, 2.02), (1.73, sy*.08, 1.9), .025, .004, 5)    # presas de cima
        cone(S, (1.66, sy*.08, 1.88), (1.68, sy*.07, 1.98), .02, .004, 5)    # presas de baixo
        sphere(S, (1.45, sy*.17, 2.2), (.07, .05, .05), segs=8)              # arcada do olho
        sphere(G, (1.5, sy*.15, 2.17), (.022, .02, .018), segs=6)            # olho em brasa
        if not (falta_orelha and sy < 0):
            cone(S, (1.2, sy*.13, 2.36), (1.12, sy*.18, 2.52), .06, .01, 6)
    # juba: três anéis de mechas pontudas varridas para trás
    for (c, R, L, n, back) in [((1.2, 0, 2.12), .22, .5, 16, .55), ((1.0, 0, 1.86), .24, .48, 14, .7), ((.84, 0, 1.6), .26, .4, 12, .8)]:
        for k in range(n):
            a = 2*math.pi*k/n + r.uniform(-.12, .12)
            if -.6 < math.cos(a) < .6 and math.sin(a) < -.75 and c[0] > 1.1: continue
            d = Vector((-back, math.cos(a), math.sin(a)*1.1)).normalized()
            base = Vector(c) + Vector((0, math.cos(a)*R, math.sin(a)*R*1.05))
            cone(S, base, base + d*L*r.uniform(.75, 1.15), .1, .012, 6)
    if luz:
        point((1.95, 0, 1.97), (1, .55, .16), 14, .08, "boca_luz")

def cavaleiro(m, var=0, seed=0):
    """Cavaleiro petrificado no galope. var: 0 carga (lança baixa), 1 estandarte de pedra,
    2 quebrado (sem cabeça, lança partida, perna caída), 3 empinado e desperto (rachaduras em brasa),
    4 tombado (de lado, como caiu no leito do rio)."""
    r = random.Random(seed)
    S = mat_estatua("estatua_brasa", 3.5, 2.0) if var == 3 else mat_estatua("estatua", 0.0, float(seed % 3))
    G = K.mat_emit("boca_leao", FOGO, 22)
    pose = POSE_EMPINADO if var == 3 else POSE_GALOPE

    def corpo():
        # ---- cavalo
        sphere(S, (0, 0, 1.3), (.85, .36, .4), segs=18)
        sphere(S, (.6, 0, 1.36), (.43, .34, .45), segs=16)
        sphere(S, (-.62, 0, 1.38), (.47, .38, .42), segs=16)
        along(S, (.72, 0, 1.45), (1.16, 0, 2.06), .27, .18, 14)
        for nome, pts in pose.items():
            perna(S, pts, quebrada=(var == 2 and nome == "fd"))
        # cauda
        cauda = [(-1.02, 0, 1.52), (-1.4, 0, 1.6), (-1.75, .05, 1.45), (-2.0, .08, 1.18), (-2.12, .1, .95)]
        for i in range(len(cauda) - 1):
            along(S, cauda[i], cauda[i+1], .09 - i*.015, .08 - i*.015, 8)
        cone(S, cauda[-1], (-2.18, .12, .72), .06, .015, 6)
        # caparazão (manta de guerra) e sela
        for sy in (-1, 1):
            o = box(S, (-.05, sy*.39, 1.12), (1.55, .04, .5), (sy*6, 0, 0), 0); displace(o, .05, .25, seed + sy + 3, 3)
            for k in range(5):
                box(S, (-.65 + k*.32, sy*.41, .84), (.22, .03, .1), (sy*6, 0, 0), .01)   # franjas
        box(S, (-.1, 0, 1.72), (.6, .64, .1), bevel=.03)
        along(S, (.42, -.3, 1.5), (.42, .3, 1.5), .06, None, 8)                   # peitoral
        cabeca_leao(S, G, r, falta_orelha=(var == 2))
        # ---- cavaleiro
        sem_cabeca = var == 2
        sphere(S, (-.1, 0, 1.85), (.2, .26, .15), segs=12)                         # quadril
        along(S, (-.1, 0, 1.85), (.05, 0, 2.3), .2, .24, 12)                       # tronco
        sphere(S, (.06, 0, 2.34), (.21, .27, .24), segs=14)                        # peito (couraça)
        box(S, (.2, 0, 2.3), (.08, .34, .34), (0, -10, 0), .03)                    # placa do peito
        for sy in (-1, 1):
            along(S, (-.05, sy*.2, 1.85), (.28, sy*.36, 1.62), .11, .085, 10)    # coxa
            along(S, (.28, sy*.36, 1.62), (.14, sy*.37, 1.18), .08, .065, 10)    # canela
            box(S, (.2, sy*.37, 1.12), (.26, .1, .08), bevel=.02)                 # bota
            torus(S, (.18, sy*.37, 1.06), .06, .012)                              # estribo
            sphere(S, (.04, sy*.31, 2.5), (.15, .14, .11), segs=12)              # ombreira
        if not sem_cabeca:
            cyl(S, (.08, 0, 2.62), .07, .14, verts=10)                             # gorjal
            cyl(S, (.1, 0, 2.8), .14, .32, verts=14)                               # elmo
            sphere(S, (.1, 0, 2.96), (.14, .14, .08), segs=12)
            box(K.mat_solid("visor", (.004, .003, .002)), (.235, 0, 2.82), (.03, .2, .025), bevel=0)
            box(S, (.02, 0, 3.05), (.42, .035, .12), (0, 8, 0), .01)              # crista
            for k in range(5):                                                     # penacho de pedra
                cone(S, (-.15, 0, 3.05 - k*.03), (-.6 - k*.07, r.uniform(-.05, .05), 2.95 - k*.08), .045, .01, 6)
        else:
            pedra(S, (.08, 0, 2.6), (.11, .1, .08), seed + 5, .04)               # pescoço partido
        # capa ao vento
        o = box(S, (-.52, 0, 2.28), (1.1, .56, .04), (0, -14, 0), 0); displace(o, .09, .35, seed + 7, 3)
        # escudo (lado esquerdo)
        o = box(S, (.12, .44, 2.12), (.06, .48, .66), (8, 0, 4), .02)
        box(S, (.12, .475, 2.15), (.02, .07, .5), (8, 0, 4), 0)
        box(S, (.12, .475, 2.25), (.02, .34, .07), (8, 0, 4), 0)
        # braço direito e arma
        sh = Vector((.04, -.33, 2.45))
        if var in (0, 2, 4):
            el, mao = Vector((-.02, -.44, 2.12)), Vector((.28, -.4, 2.12))
            along(S, sh, el, .085, .075, 10); sphere(S, el, (.08,)*3, segs=8)
            if var == 2:
                pedra(S, el, (.09, .08, .07), seed + 9, .03)                       # antebraço partido
            else:
                along(S, el, mao, .075, .065, 10)
                a, b = Vector((-.9, -.4, 2.0)), Vector((2.9, -.4, 2.62))
                cone(S, a, b, .06, .014, 10)                                        # lança deitada
                p = a.lerp(b, .3); d = (b - a).normalized()
                along(S, p, p + d*.4, .05, .17, 12)                                # guarda da lança
                o = box(S, tuple(a.lerp(b, .86) + Vector((-.15, 0, .16))), (.5, .02, .26), (0, -9, 0), 0)
                displace(o, .04, .15, seed + 11, 3)                                # flâmula
        else:
            el, mao = Vector((.12, -.45, 2.25)), Vector((.22, -.42, 2.62))
            along(S, sh, el, .085, .075, 10); along(S, el, mao, .075, .065, 10)
            if var == 1:                                                            # estandarte de pedra
                a, b = Vector((.12, -.42, 1.5)), Vector((.38, -.42, 4.9))
                along(S, a, b, .05, .04, 10)
                along(S, (.32, -.42, 4.25), (.32 - 1.2, -.42, 4.25 + .05), .03, .03, 6)
                o = box(S, (-.28, -.42, 3.78), (1.2, .05, .95), (0, -2, 0), 0); displace(o, .1, .4, seed + 13, 3)
                box(S, (-.28, -.45, 3.82), (.14, .02, .55), (0, -2, 0), 0)          # cruz em relevo
                box(S, (-.28, -.45, 3.92), (.42, .02, .12), (0, -2, 0), 0)
                cone(S, b, b + Vector((.02, 0, .3)), .07, .005, 8)
                sphere(S, b, (.08,)*3, segs=8)
            else:                                                                   # lança erguida
                a, b = Vector((-.55, -.42, 1.9)), Vector((1.7, -.42, 4.1))
                cone(S, a, b, .06, .014, 10)
                p = a.lerp(b, .28); d = (b - a).normalized()
                along(S, p, p + d*.4, .05, .17, 12)

    objs = novos(corpo)
    if var == 3:
        agrupar(objs, (-1.0, 0, .05), (0, -26, 0))
    if var == 4:
        e = agrupar(objs, (0, 0, .0), (78, 0, 0)); e.location.z = .45
        for k in range(6):
            pedra(S, (r.uniform(-1.5, 1.5), r.uniform(-1.2, 1.2), .05), (r.uniform(.15, .3),)*3, seed + k, .05)
        return
    # base de pedra e escora (estátua) com crosta de enxofre
    B = mat_basalto()
    o = box(B, (-.1, 0, -.02), (3.0, 1.25, .28), (0, 0, r.uniform(-3, 3)), 0); crumble(o, .12, seed)
    belly = Vector((-.05, 0, 1.0)) if var != 3 else Vector((-.05, 0, 1.2))
    o = along(S, (-.05, 0, 0), belly, .26, .2, 10); crumble(o, .05, seed + 1)
    for k in range(6):
        a = r.uniform(0, 6.28)
        sphere(mat_cristal(), (math.cos(a)*r.uniform(.4, 1.4), math.sin(a)*r.uniform(.3, .6), .1), (.12, .12, r.uniform(.08, .2)), segs=6)
    if var == 2:   # pedaços caídos: elmo, perna, ponta da lança
        sphere(S, (1.2, -.75, .12), (.14, .14, .12), segs=10)
        cyl(S, (1.25, -.7, .25), .13, .28, (70, 0, 30), 12)
        along(S, (1.5, .1, .08), (1.9, -.6, .1), .08, .07, 8)
        cone(S, (.6, -1.0, .06), (2.4, -1.4, .2), .055, .014, 8)
        for k in range(5):
            pedra(S, (r.uniform(.6, 2.0), r.uniform(-1.2, .4), .04), (r.uniform(.06, .14),)*3, seed + 20 + k, .03)

def kv(var, seed): return lambda m: cavaleiro(m, var, seed)

# ================================================================ vocabulário
def pilar_basalto(m, seed=0, n=6, hmax=6.0):
    """Feixe de colunas hexagonais de basalto, topo com pó de enxofre."""
    r = random.Random(seed); B = mat_basalto()
    for k in range(n):
        a = k*2.4 + r.uniform(-.3, .3); d = 0 if k == 0 else r.uniform(.45, .8)
        h = hmax*(1 if k == 0 else r.uniform(.35, .85))
        o = cyl(B, (math.cos(a)*d, math.sin(a)*d, h/2), r.uniform(.32, .42), h, (r.uniform(-4, 4), r.uniform(-4, 4), r.uniform(0, 60)), 6, smooth=False)
        crumble(o, .03, seed + k)
    for k in range(5):
        a = r.uniform(0, 6.28)
        pedra(B, (math.cos(a)*1.3, math.sin(a)*1.3, .1), (r.uniform(.2, .35),)*3, seed + 10 + k)

def corrente_gigante(m, seed=0, comp=9.0, alt=5.5):
    """Pilar de basalto com argola de ferro e uma corrente gigante que sai do chão e sobe até ele."""
    r = random.Random(seed); B = mat_basalto(); F = K.mat_metal("ferro_corrente", (.04, .036, .034), .75, 3.0)
    o = cyl(B, (0, 0, alt/2 + .5), 1.0, alt + 1, verts=6, smooth=False); crumble(o, .04, seed)
    for k in range(4):
        a = k*1.6 + .4
        o = cyl(B, (math.cos(a)*1.2, math.sin(a)*1.2, 1.2), .45, 2.4 + r.uniform(-.6, .6), verts=6, smooth=False); crumble(o, .03, seed + k)
    torus(F, (0, 0, alt), 1.08, .14)
    torus(F, (0, 0, alt - .6), 1.08, .1)
    a, b = Vector((-comp, 0, -.3)), Vector((-1.1, 0, alt - .2))
    L = (b - a).length; n = int(L/.62)
    for i in range(n):
        t = (i + .5)/n
        p = a.lerp(b, t) - Vector((0, 0, math.sin(t*math.pi)*.9))
        ang = math.degrees(math.atan2(b.z - a.z, b.x - a.x))
        torus(F, p, .42, .11, (90 if i % 2 else 0, -ang, 0)).scale = (1.0, 1.0, 1.0)
    # argola no chão, meio enterrada
    torus(F, (-comp, 0, -.1), .7, .16, (90, 0, 90))
    for k in range(6):
        aa = r.uniform(0, 6.28); pedra(B, (-comp + math.cos(aa)*1.0, math.sin(aa)*1.0, .05), (r.uniform(.2, .4),)*3, seed + 30 + k)

def lanca_quebrada(m, seed=0):
    r = random.Random(seed); S = mat_estatua("estatua", 0.0, 1.0)
    for k in range(r.randint(2, 3)):
        x, y = r.uniform(-.6, .6), r.uniform(-.6, .6)
        top = Vector((x + r.uniform(-.8, .8), y + r.uniform(-.8, .8), r.uniform(1.0, 2.2)))
        along(S, (x, y, -.1), top, .055, .045, 8)
        pedra(S, top, (.06, .06, .05), seed + k, .02)
    cone(S, (r.uniform(-1, 1), r.uniform(-1, 1), .06), (r.uniform(-1, 1), r.uniform(-1, 1), .1), .05, .012, 8)

def estandarte_pedra(m, seed=0):
    r = random.Random(seed); S = mat_estatua("estatua", 0.0, 2.0)
    lean = r.uniform(-12, 12)
    top = Vector((math.sin(math.radians(lean))*3.2, 0, 3.4))
    along(S, (0, 0, -.2), top, .07, .055, 10)
    along(S, top - Vector((0, 0, .4)) + Vector((-1.3, 0, 0)), top - Vector((0, 0, .4)), .035, .035, 6)
    o = box(S, tuple(top - Vector((.68, 0, 1.0))), (1.3, .05, 1.2), (0, lean*.3, 0), 0); displace(o, .12, .4, seed, 3)
    box(S, tuple(top - Vector((.68, .03, .95))), (.14, .02, .7), (0, lean*.3, 0), 0)
    box(S, tuple(top - Vector((.68, .03, .82))), (.5, .02, .14), (0, lean*.3, 0), 0)
    cone(S, top, top + Vector((0, 0, .35)), .08, .005, 8)
    for k in range(5):
        pedra(mat_basalto(), (r.uniform(-.6, .6), r.uniform(-.6, .6), .05), (r.uniform(.15, .3),)*3, seed + k)

def fumarola(m, seed=0, h=7.0):
    r = random.Random(seed); X = mat_cristal()
    o = cyl(mat_basalto(), (0, 0, .15), 1.0, .35, verts=14, r2=.45); crumble(o, .06, seed)
    cyl(K.mat_emit("respiro", FOGO, 6), (0, 0, .34), .32, .03, verts=12)
    for k in range(14):
        a = r.uniform(0, 6.28); d = r.uniform(.5, 1.5); hh = r.uniform(.15, .55)
        cyl(X, (math.cos(a)*d, math.sin(a)*d, hh/2), r.uniform(.05, .11), hh, (r.uniform(-25, 25), r.uniform(-25, 25), 0), 6, smooth=False, r2=.01)
    fumaca((0, 0, .2), h, .9, (r.uniform(-6, 6), r.uniform(-6, 6)), .6, seed)
    point((0, 0, .8), (1, .55, .15), 60, .3, "fumarola_luz")

def cratera_fogo(m, seed=0, R=2.4):
    r = random.Random(seed); B = mat_basalto()
    o = cyl(mat_lava(), (0, 0, .02), R*.78, .05, verts=24); displace(o, .05, .4, seed, 2)
    for k in range(22):
        a = 2*math.pi*k/22 + r.uniform(-.1, .1)
        pedra(B, (math.cos(a)*R, math.sin(a)*R*.85, .15), (r.uniform(.4, .7), r.uniform(.3, .5), r.uniform(.25, .5)), seed + k, .1)
    for k in range(8):
        a = r.uniform(0, 6.28); d = R + r.uniform(.6, 1.6)
        sphere(mat_cristal(), (math.cos(a)*d, math.sin(a)*d, .06), (.18, .18, .12), segs=6)
    fumaca((0, 0, .1), 9.0, 1.7, (4, -3), .45, seed + 2)
    point((0, 0, 1.2), (1, .5, .12), 900, 1.0, "cratera_luz")

def carroca_guerra(m, seed=0):
    """Carroça de guerra: caixa de tábuas com estacas afiadas, rodas de aro de ferro, toldo rasgado."""
    r = random.Random(seed); W, F = m["wood"], m["iron"]
    box(m["wood_d"], (0, 0, .75), (3.0, 1.4, .1), bevel=.01)
    for sy in (-1, 1):
        for k in range(4):
            box(W, (0, sy*.68, .88 + k*.17), (3.0, .07, .15), (r.uniform(-1, 1), 0, 0), .01)
        for x in (-1.4, -.45, .45, 1.4): box(F, (x, sy*.72, 1.08), (.08, .02, .7), bevel=0)
        for k in range(7):                                          # estacas
            x = -1.35 + k*.45
            cone(W, (x, sy*.7, .95), (x, sy*1.3, 1.25 + r.uniform(-.1, .1)), .045, .006, 6)
    for sx in (-1, 1):
        box(W, (sx*1.48, 0, 1.12), (.07, 1.4, .7), bevel=.01)
    for (x, y) in [(-1.0, -.85), (-1.0, .85), (1.0, -.85), (1.0, .85)]:
        torus(F, (x, y, .55), .52, .05, (90, 0, 0))
        torus(m["wood_d"], (x, y, .55), .47, .05, (90, 0, 0))
        cyl(F, (x, y, .55), .1, .22, (90, 0, 0), 10)
        for k in range(8):
            a = math.radians(22.5*k*2)
            along(m["wood_d"], (x, y, .55), (x + math.cos(a)*.47, y, .55 + math.sin(a)*.47), .025, verts=5)
    # toldo rasgado em arcos
    T_ = K.mat_cloth("lona_enxofre", (.12, .1, .06), 4.0)
    for x in (-1.2, -.4, .4, 1.2):
        bpy.ops.mesh.primitive_torus_add(location=(x, 0, 1.4), rotation=(0, math.radians(90), 0), major_radius=.72, minor_radius=.025, major_segments=24, minor_segments=6)
        o = bpy.context.object; o.data.materials.append(W)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.74, depth=2.2 if seed % 2 else 2.8, location=(-.3 if seed % 2 else 0, 0, 1.4), rotation=(0, math.radians(90), 0))
    o = bpy.context.object; o.data.materials.append(T_)
    import bmesh
    bm = bmesh.new(); bm.from_mesh(o.data)
    kill = [f for f in bm.faces if f.calc_center_median().z < -.05 or (r.random() < .18 and abs(f.normal.x) < .5)]
    bmesh.ops.delete(bm, geom=kill, context='FACES'); bm.to_mesh(o.data); bm.free()
    displace(o, .06, .3, seed, 2)
    along(W, (1.5, -.35, .7), (2.9, -.3, .25), .05, verts=6); along(W, (1.5, .35, .7), (2.9, .3, .25), .05, verts=6)
    box(m["sack"], (-.6, .2, .95), (.6, .5, .3), (0, 0, 20), .06)
    box(W, (.4, -.1, .95), (.5, .5, .4), (0, 0, 8), .02)

def tenda_rasgada(m, seed=0):
    """Tenda de campanha cônica, lona rasgada e manchada de enxofre, com mastro e flâmula."""
    r = random.Random(seed); T_ = K.mat_cloth("lona_tenda", (.13, .11, .07), 6.0 + seed)
    bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=2.3, radius2=.12, depth=3.0, location=(0, 0, 1.5))
    o = bpy.context.object; o.data.materials.append(T_)
    import bmesh
    bm = bmesh.new(); bm.from_mesh(o.data)
    kill = [f for f in bm.faces if f.calc_area() < 50 and f.calc_center_median().z < 0 and len(f.verts) > 4]
    side = [f for f in bm.faces if len(f.verts) == 4]
    kill += [side[(seed*3) % len(side)]]
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if len(f.verts) > 4], context='FACES')
    bmesh.ops.delete(bm, geom=[f for f in kill if f.is_valid], context='FACES')
    bm.to_mesh(o.data); bm.free()
    displace(o, .1, .5, seed, 3)
    cyl(m["wood_d"], (0, 0, 1.9), .06, 3.8, verts=8)
    o = box(T_, (.4, 0, 3.5), (.7, .02, .3), bevel=0); displace(o, .05, .2, seed, 3)
    for k in range(8):
        a = 2*math.pi*k/8
        along(K.mat_solid("corda", (.1, .08, .05)), (math.cos(a)*2.0, math.sin(a)*2.0, .3), (math.cos(a)*2.9, math.sin(a)*2.9, 0), .01, verts=4)
        cyl(m["wood"], (math.cos(a)*2.9, math.sin(a)*2.9, .1), .03, .3, verts=5)
    # aba rasgada pendurada
    o = box(T_, (1.5, -1.2, .7), (.9, .03, 1.2), (12, 0, -40), 0); displace(o, .1, .3, seed + 2, 3)
    box(m["wood"], (1.8, 1.4, .25), (.5, .5, .5), (0, 0, 20), .02)
    cyl(m["brass"], (1.8, 1.4, .62), .06, .2, verts=10)
    sphere(K.mat_emit("lanterna", (1, .6, .25), 9), (1.8, 1.4, .62), (.045, .045, .07), segs=8)
    point((1.9, 1.3, .8), (1, .55, .2), 25, .05)

def cristais(m, seed=0):
    r = random.Random(seed); X = mat_cristal()
    for k in range(r.randint(5, 9)):
        h = r.uniform(.2, .7)
        cyl(X, (r.uniform(-.3, .3), r.uniform(-.3, .3), h/2), r.uniform(.05, .12), h, (r.uniform(-30, 30), r.uniform(-30, 30), 0), 6, smooth=False, r2=.015)

def rocha_basalto(m, seed=0):
    r = random.Random(seed); B = mat_basalto()
    for k in range(r.randint(2, 4)):
        pedra(B, (r.uniform(-.6, .6), r.uniform(-.6, .6), .1), (r.uniform(.3, .7), r.uniform(.3, .6), r.uniform(.25, .55)), seed + k, .1)

# ================================================================ o marco: a Ponte Partida
def ponte_partida(m, seed=0):
    """Ponte de basalto de três arcos sobre o rio seco, com o arco do meio desabado.
    Eixo da ponte em X (de -10 a 10), tabuleiro a 3,2 m."""
    r = random.Random(seed); P = mat_silhar(); B = mat_basalto(); S = mat_estatua("estatua", 0.0, 1.0)
    Z, W = 3.2, 4.2
    def vao(cx, x0, x1, top=Z):
        o = box(P, ((x0 + x1)/2, 0, top/2), (x1 - x0, W, top), bevel=0)
        bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=2.45, depth=W + 1, location=(cx, 0, .3), rotation=(math.radians(90), 0, 0))
        h = bpy.context.object
        md = o.modifiers.new("arco", 'BOOLEAN'); md.object = h; md.operation = 'DIFFERENCE'
        bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier="arco")
        bpy.data.objects.remove(h)
        # aduelas do arco
        for k in range(15):
            a = math.pi*k/14
            if x0 <= cx + math.cos(a)*2.6 <= x1:
                box(B, (cx + math.cos(a)*2.6, 0, .3 + math.sin(a)*2.6), (.34, W + .14, .42), (0, -math.degrees(a) + 90, 0), .02)
        return o
    vao(-6.0, -9.0, -3.0); vao(6.0, 3.0, 9.0)
    # pilares do meio, partidos em alturas diferentes
    for (x, top) in [(-2.4, Z), (2.4, Z*.7)]:
        o = box(P, (x, 0, top/2), (1.2, W, top), bevel=0)
        box(B, (x, -W/2 - .35, 1.0), (1.4, .7, 2.0), bevel=.03)               # quebra-mar
        box(B, (x, W/2 + .35, 1.0), (1.4, .7, 2.0), bevel=.03)
    # toco do arco do meio (cantilever partido) com bordas irregulares
    for k in range(5):
        box(P, (-1.6 + k*.32, r.uniform(-.2, .2), Z - .3 - k*.18), (.36, W*(1 - k*.12), .6), (r.uniform(-4, 4), r.uniform(-6, 6), 0), .02)
    for k in range(3):
        box(P, (1.6 - k*.32, r.uniform(-.2, .2), Z*.7 - .1 - k*.2), (.36, W*(1 - k*.18), .5), (r.uniform(-4, 4), r.uniform(-6, 6), 0), .02)
    # tabuleiro, parapeitos e rampas
    for (x0, x1) in [(-9.0, -1.8)]:
        box(B, ((x0 + x1)/2, 0, Z + .12), (x1 - x0, W + .3, .24), bevel=.02)
    box(B, (5.6, 0, Z + .12), (6.8, W + .3, .24), bevel=.02)
    box(P, (2.7, 0, Z*.85), (1.0, W, Z*.3), (0, -18, 0), 0)
    for sy in (-1, 1):
        for x in [-8.6 + i*.75 for i in range(10)] + [3.0 + i*.75 for i in range(8)]:
            if r.random() < .22: continue
            h = .8 if r.random() > .2 else r.uniform(.3, .6)
            box(B, (x, sy*(W/2 + .02), Z + .24 + h/2), (.62, .3, h), (0, 0, r.uniform(-2, 2)), .02)
        box(B, (-9.0, sy*(W/2 + .05), Z + .9), (.6, .5, 1.8), bevel=.03)       # pilaretes das cabeceiras
        box(B, (9.0, sy*(W/2 + .05), Z + .9), (.6, .5, 1.8), bevel=.03)
        cone(S, (-9.0, sy*(W/2 + .05), Z + 1.8), (-9.0, sy*(W/2 + .05), Z + 2.3), .25, .02, 6)
    for sx in (-1, 1):
        o = box(P, (sx*12.2, 0, Z/2 - .1), (6.4, W, Z), (0, sx*28, 0), 0)       # rampa de terra/pedra
        crumble(o, .08, seed + sx)
        for k in range(6):
            pedra(B, (sx*(10.5 + r.uniform(0, 3)), r.uniform(-W/2 - .8, W/2 + .8), .2), (r.uniform(.3, .6),)*3, seed + 40 + k + sx)
    # blocos caídos no leito
    for k in range(16):
        x, y = r.uniform(-1.6, 2.2), r.uniform(-W/2 - .6, W/2 + .6)
        o = box(P if k % 2 else B, (x, y, .25), (r.uniform(.5, 1.1), r.uniform(.4, .9), r.uniform(.35, .6)),
                (r.uniform(-25, 25), r.uniform(-25, 25), r.uniform(0, 90)), .03)
    # correntes penduradas no vão
    F = K.mat_metal("ferro_corrente", (.04, .036, .034), .75, 3.0)
    for sy in (-1.2, 1.3):
        for k in range(7):
            torus(F, (-1.4, sy, Z - .2 - k*.32), .14, .04, (0, 0 if k % 2 else 90, 0))

# ================================================================ cena
def modelo_teste():
    C.iniciar(ceu=(.05, .04, .02), poeira=ENXOFRE, luzes=False)
    C.sol((1, .85, .6), 3.0, (52, 0, -40)); C.sol((.4, .4, .45), .6, (70, 0, 110), nome="fill")
    for i, v in enumerate([0, 1, 2, 3, 4]):
        C.grupo(kv(v, 7 + i), -6 + i*3.2, 6 - i*3.2, 0, 1.0, chave=f"cav{v}")
    C.chao(mat_enxofre(), 60)
    C.render(OUT + "_modelo", centro=(0, 0), largura=14, W=1280, H=720, samples=24)

def cena():
    C.iniciar(ceu=(.05, .04, .018), poeira=ENXOFRE, luzes=False)
    sc = bpy.context.scene; sc.world.mist_settings.start = 92; sc.world.mist_settings.depth = 50
    C.sol((1.0, .78, .42), 2.4, (52, 0, -40), .08)
    C.sol((.42, .4, .36), .55, (70, 0, 110), nome="fill")
    C.sol((1.0, .5, .15), 1.1, (-55, 0, 165), nome="rim")
    r = random.Random(23)
    # ---- rio seco ao longo de Y em x ~ -2, a Ponte Partida atravessando em y = 0
    rio = [(-2 + 1.6*math.sin(i*.35) + (.0 if i != 10 else 0), -48 + i*5) for i in range(20)]
    C.faixa(mat_leito(), rio, [7.0 + 1.2*math.sin(i*1.3) for i in range(20)], z=.01, nome="leito")
    C.faixa(mat_basalto_chao(), [(x - 4.6, y) for (x, y) in rio], 1.6, z=.012, nome="margem_e")
    C.faixa(mat_basalto_chao(), [(x + 4.6, y) for (x, y) in rio], 1.4, z=.012, nome="margem_d")
    for (x, y) in rio:
        for sx in (-1, 1):
            for k in range(2):
                C.grupo(rocha_basalto, x + sx*(4.0 + r.uniform(0, 1.2)), y + r.uniform(-2.4, 2.4), r.uniform(0, 360), r.uniform(.6, 1.1), chave=f"rocha{k}")
    C.grupo(ponte_partida, -2.0, 0, 0, 1.0, chave="ponte")
    # cavaleiros sobre a ponte e caídos no leito
    C.grupo(kv(3, 31), 1.2 - 2.0 - 3.6, -.9, 0, 1.15, z=3.32, chave="cav3")
    C.grupo(kv(1, 32), -6.8 - 2.0 + 1.0, 1.0, 0, 1.15, z=3.32, chave="cav1")
    C.grupo(kv(0, 33), -2.0 - 9.0 + 2.6, -1.1, 0, 1.15, z=3.32, chave="cav0")
    C.grupo(kv(4, 34), -1.6, -4.5, 200, 1.15, chave="cav4")
    C.grupo(kv(4, 34), -.2, 4.5, 30, 1.15, chave="cav4")
    # ---- a carga petrificada: fileiras ao longo de Y, galopando para +X (baixo-direita da tela)
    filas = [7.5, 12.0, -9.0, -13.5, -18.0, -22.5, -27.0, -31.5, -36.0]
    pesos = [0, 0, 0, 0, 1, 1, 2, 2, 3]
    acamp = lambda x, y: 13 < x < 26 and -16 < y < -1
    for j, fx in enumerate(filas):
        y = -46 + (j % 2)*1.6
        while y < 46:
            x = fx + r.uniform(-.5, .5)
            ok = not (abs(y) < 3.4 and -12 < x < 9) and not acamp(x, y)
            ok = ok and not (fx > 0 and r.random() < .1)
            if ok:
                v = r.choice(pesos)
                C.grupo(kv(v, 30 + v), x, y + r.uniform(-.3, .3), r.uniform(-7, 7), 1.15 * r.uniform(.96, 1.04), chave=f"cav{v}")
            y += 3.3
    # ---- basalto: placas e pilares; correntes gigantes nas margens
    for (x, y, rr, sd) in [(18, 14, 6.0, 1), (-24, -14, 7.0, 2), (30, -24, 5.0, 3), (-8, 26, 5.5, 4)]:
        C.mancha(mat_basalto_chao(), (x, y), rr, seed=sd, irregular=.45, z=.014, nome="placa")
    C.grupo(lambda m: pilar_basalto(m, 3, 7, 6.5), 19, 15, 0, 1.0, chave="pilar_a")
    C.grupo(lambda m: pilar_basalto(m, 5, 6, 5.0), -24, -15, 40, 1.0, chave="pilar_b")
    C.grupo(lambda m: pilar_basalto(m, 8, 5, 4.0), 31, -25, 10, 1.0, chave="pilar_c")
    C.grupo(lambda m: corrente_gigante(m, 1), 6.5, 9.0, 20, 1.0, chave="corrente")
    C.grupo(lambda m: corrente_gigante(m, 2), -8.5, -10.5, 200, 1.0, chave="corrente2")
    # ---- rachaduras que soltam fumaça
    brasa = K.mat_emit("rachadura", FOGO, 7)
    queim = mat_basalto_chao(9.0)
    for (x0, y0, ang, L, sd) in [(24, -28, 70, 16, 1), (34, 2, 120, 14, 2), (-16, 4, 40, 18, 3), (6, -24, 100, 12, 4), (-28, 18, 160, 14, 5), (14, 30, 20, 12, 6)]:
        rr = random.Random(sd); pts = []
        p = Vector((x0, y0)); d = Vector((math.cos(math.radians(ang)), math.sin(math.radians(ang))))
        for i in range(14):
            pts.append((p.x, p.y)); d = Matrix.Rotation(rr.uniform(-.5, .5), 2) @ d; p = p + d*L/13
        C.faixa(queim, pts, [.2 + .7*math.sin(math.pi*i/13) for i in range(14)], z=.016, nome="rachadura_borda")
        C.faixa(brasa, pts, [.03 + .14*math.sin(math.pi*i/13) for i in range(14)], z=.02, nome="rachadura")
        for i in (4, 9):
            bpy_o = fumaca((pts[i][0], pts[i][1], 0), rr.uniform(3.5, 5.5), .55, (rr.uniform(-5, 5), rr.uniform(-5, 5)), .4, sd + i)
        C.ponto((pts[7][0], pts[7][1], .5), (1, .55, .15), 120, .5)
    # ---- fumarolas e crateras de fogo
    for (x, y, sd) in [(28, -6, 1), (-14, 20, 2), (4, -36, 3), (38, 16, 4), (-32, -4, 5)]:
        C.grupo(lambda m, sd=sd: fumarola(m, sd), x, y, r.uniform(0, 360), 1.0, chave=f"fumarola{sd % 3}")
    C.grupo(lambda m: cratera_fogo(m, 1), 24.5, 6.5, 0, 1.0, chave="cratera")
    C.grupo(lambda m: cratera_fogo(m, 2, 1.8), -20, 30, 0, 1.0, chave="cratera2")
    # ---- vocabulário miúdo espalhado
    for k in range(40):
        x, y = r.uniform(-40, 42), r.uniform(-44, 40)
        if abs(x + 2) < 6 or acamp(x, y): continue
        C.grupo(lambda m, s=k % 3: lanca_quebrada(m, s), x, y, r.uniform(0, 360), 1.0, chave=f"lanca{k % 3}")
    for (x, y) in [(10, -3), (-6, -12), (-6, 13), (2.5, 22), (16, 24), (28, -14), (-14, -26)]:
        C.grupo(lambda m, s=int(x) % 3: estandarte_pedra(m, s), x, y, r.uniform(-20, 20), 1.1, chave=f"estand{int(x) % 3}")
    for k in range(70):
        x, y = r.uniform(-40, 42), r.uniform(-44, 40)
        if abs(x + 2) < 5: continue
        C.grupo(lambda m, s=k % 4: cristais(m, s), x, y, r.uniform(0, 360), r.uniform(.8, 1.4), chave=f"cristal{k % 4}")
    for k in range(18):
        x, y = r.uniform(-40, 42), r.uniform(-44, 40)
        if abs(x + 2) < 5 or acamp(x, y): continue
        C.grupo(rocha_basalto, x, y, r.uniform(0, 360), r.uniform(.8, 1.5), chave=f"rocha{k % 2}")
    # ---- Acampamento da Ponte Partida (primeiro plano, na frente da carga)
    C.mancha(K.mat_ground("terra", (8.0, 8.0), 4), (19.5, -8.5), 5.5, seed=7, irregular=.3, z=.015, nome="chao_batido")
    C.grupo(lambda m: tenda_rasgada(m, 0), 22, -5, 10, 1.0, chave="tenda0")
    C.grupo(lambda m: tenda_rasgada(m, 1), 15.5, -13, 70, .85, chave="tenda1")
    por("tenda_vigilia", 23.5, -12.5, 40)
    C.grupo(lambda m: carroca_guerra(m, 0), 16.5, -4, 75, 1.0, chave="carroca0")
    C.grupo(lambda m: carroca_guerra(m, 1), 25.5, -9, 160, 1.0, chave="carroca1")
    por("carroca_quebrada", 13.5, -8, 30)
    por("fogueira", 19.5, -8.5); C.ponto((19.5, -8.5, 1.0), (1, .5, .16), 700, .4)
    por("braseiro_ferro", 18, -11.5); por("braseiro_ferro", 21.5, -2.5); por("tonel_fogo", 13.8, -2.2)
    C.ponto((18, -11.5, 1.4), (1, .5, .16), 260, .3); C.ponto((21.5, -2.5, 1.4), (1, .5, .16), 260, .3)
    por("caixas", 20.5, -12); por("barris", 24, -7); por("sacos_areia", 13.2, -11, 70); por("sacos_areia", 13, -5.5, 100)
    por("estandarte_rasgado", 17, -6.6, 0); por("varal_roupas", 23, -16, 20)
    por("elmo_espada_fincada", 26, -14); por("elmo_espada_fincada", 27, -13, 40)
    # ---- chão por último
    C.chao(mat_enxofre(), 170, ondula=.1, seed=3, z=-.06)
    C.render(OUT, centro=(1.5, -1.0), largura=54, W=960 if Q else 1920, H=540 if Q else 1080, samples=16 if Q else 96)

if MODELO: modelo_teste()
else: cena()
