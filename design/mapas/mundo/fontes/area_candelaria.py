# Vinheta de Candelária, a Cidade sem Sol (nível 45 a 60, 4ª trombeta).
# Regra Lorencia: um chão só (paralelepípedo com geada), dois destaques do mesmo chão em outro
# estado (neve de fuligem e gelo negro), vocabulário curto que se repete (sobrado gótico, poste
# de gás, cano de gás, grade de ferro, banco congelado, monte de neve) e UM marco: o Gasômetro
# no meio da Praça dos Mil Lampiões. A luz é moeda: ilhas amarelas no meio do escuro azul.
import sys, os, math, random
import bpy
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cena as C
from cena import por, grupo
K, A = C.K, C.A
from kit import box, cyl, sphere, along, torus, displace, crumble, prism, point
Q = os.environ.get("Q") == "1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "candelaria")

C.iniciar(ceu=(.006, .009, .02), poeira=(.36, .38, .43), luzes=False)
C.sol((.42, .52, .85), .55, K.KEY_ROT, .08, "lua")          # luar frio e fraco
C.sol((.2, .26, .45), .22, (70, 0, 110), .3, "ceu")          # céu azul-noite de preenchimento
C.sol((.35, .4, .6), .18, (-55, 0, 165), .2, "contra")       # contraluz frio nos telhados

LAMP = (1.0, .66, .26)    # amarelo de lampião (a cor que brilha)

# ================================================================ materiais
@K.cached
def mat_neve(name="neve_fuligem", seed=0.0):
    """Neve suja de fuligem: branco-azulado com veios cinza."""
    m, nt, b = K.new_mat(name)
    v, w = K.coords(nt)
    n = K.noise(nt, v, w, 2.5, 6, .6, seed); n2 = K.noise(nt, v, w, 14, 3, .5, seed + 2)
    r = K.ramp(nt, [(.3, (.1, .1, .11)), (.55, (.27, .28, .31)), (.75, (.42, .44, .48))]); K.L(nt, n.outputs["Fac"], r.inputs[0])
    col = K.mix(nt, r.outputs[0], n2.outputs["Color"], .12, 'OVERLAY')
    K.L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .75
    b.inputs["Subsurface Weight"].default_value = .15
    K.bump(nt, b, K.math_(nt, 'ADD', n.outputs["Fac"], K.math_(nt, 'MULTIPLY', n2.outputs["Fac"], .5)), .35, .03)
    return m

@K.cached
def mat_gelo(name="gelo", c=(.12, .16, .22), rough=.08):
    m, nt, b = K.new_mat(name)
    v, w = K.coords(nt)
    n = K.noise(nt, v, w, 6, 5, .6, 4.0)
    col = K.mix(nt, c, (c[0]*1.8, c[1]*1.8, c[2]*1.7), n.outputs["Fac"])
    K.L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = .6
    K.bump(nt, b, n.outputs["Fac"], .2, .01)
    return m

@K.cached
def mat_telhado(name="telhado_neve", seed=0.0):
    """Ardósia escura com neve suja acumulada em faixas."""
    m, nt, b = K.new_mat(name)
    v, w = K.coords(nt)
    tc = K.N(nt, "ShaderNodeTexCoord")
    bk = K.N(nt, "ShaderNodeTexBrick", offset=.5, squash=1.0)
    bk.inputs["Scale"].default_value = 1.0; bk.inputs["Brick Width"].default_value = .32; bk.inputs["Row Height"].default_value = .16
    bk.inputs["Mortar Size"].default_value = .012
    bk.inputs["Color1"].default_value = (.045, .048, .058, 1); bk.inputs["Color2"].default_value = (.025, .027, .033, 1)
    bk.inputs["Mortar"].default_value = (.008, .008, .01, 1)
    sep = K.N(nt, "ShaderNodeSeparateXYZ"); K.L(nt, tc.outputs["Object"], sep.inputs[0])
    cb = K.N(nt, "ShaderNodeCombineXYZ"); K.L(nt, sep.outputs[0], cb.inputs[0])
    K.L(nt, K.math_(nt, 'ADD', sep.outputs[1], sep.outputs[2]), cb.inputs[1]); K.L(nt, cb.outputs[0], bk.inputs["Vector"])
    n = K.noise(nt, v, w, 1.6, 6, .6, seed)
    sr = K.ramp(nt, [(.42, (0, 0, 0)), (.5, (1, 1, 1))]); K.L(nt, n.outputs["Fac"], sr.inputs[0])
    n2 = K.noise(nt, v, w, 9, 3, .5, seed + 3)
    snow = K.mix(nt, (.3, .31, .35), (.14, .14, .16), n2.outputs["Fac"])
    col = K.mix(nt, bk.outputs["Color"], snow, sr.outputs[0])
    K.L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .7
    K.bump(nt, b, K.math_(nt, 'ADD', K.math_(nt, 'SUBTRACT', 1.0, bk.outputs["Fac"]), sr.outputs[0]), .5, .03)
    return m

@K.cached
def mat_halo(name="halo", c=LAMP, s=1.2):
    """Esfera de halo: emissão que some nas bordas (névoa iluminada em volta do lampião)."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs[0].default_value = .5
    r = K.ramp(nt, [(0, (1, 1, 1)), (.85, (0, 0, 0))]); r.color_ramp.interpolation = 'EASE'
    K.L(nt, lw.outputs["Facing"], r.inputs[0])
    f = K.math_(nt, 'MULTIPLY', K.math_(nt, 'POWER', r.outputs[0], 2.0), .55)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent"); em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (*c, 1); em.inputs[1].default_value = s
    mx = nt.nodes.new("ShaderNodeMixShader"); K.L(nt, f, mx.inputs[0])
    K.L(nt, tr.outputs[0], mx.inputs[1]); K.L(nt, em.outputs[0], mx.inputs[2])
    K.L(nt, mx.outputs[0], out.inputs[0])
    m.blend_method = 'BLEND'
    return m

def mat_chao_geada(seed=0.0):
    """Paralelepípedo azul-ferro com geada branca no topo das pedras e juntas escuras."""
    m, nt, b = K.new_mat("chao_geada")
    v, w = K.coords(nt)
    sc_ = 3.3
    vo = K.voronoi(nt, v, w, sc_, 'DISTANCE_TO_EDGE', seed, .8)
    vc = K.voronoi(nt, v, w, sc_, 'F1', seed, .8)
    gap = K.ramp(nt, [(0, (0, 0, 0)), (.05, (1, 1, 1))]); K.L(nt, vo.outputs["Distance"], gap.inputs[0])
    dome = K.ramp(nt, [(0, (0, 0, 0)), (.24, (1, 1, 1))]); dome.color_ramp.interpolation = 'EASE'; K.L(nt, vo.outputs["Distance"], dome.inputs[0])
    st = K.ramp(nt, [(0, (.035, .038, .046)), (1, (.085, .09, .1))]); K.L(nt, vc.outputs["Color"], st.inputs[0])
    n = K.noise(nt, v, w, 3, 8, .6, seed + 1); nf = K.noise(nt, v, w, 28, 3, .5, seed + 2)
    col = K.mix(nt, st.outputs[0], n.outputs["Color"], .25, 'OVERLAY')
    col = K.mix(nt, col, nf.outputs["Color"], .15, 'OVERLAY')
    # geada: no topo das pedras, mais forte em manchas largas
    fm = K.noise(nt, v, w, .35, 4, .55, seed + 5)
    fmr = K.ramp(nt, [(.38, (0, 0, 0)), (.62, (1, 1, 1))]); K.L(nt, fm.outputs["Fac"], fmr.inputs[0])
    fr = K.noise(nt, v, w, 40, 4, .7, seed + 6)
    frr = K.ramp(nt, [(.35, (0, 0, 0)), (.6, (1, 1, 1))]); K.L(nt, fr.outputs["Fac"], frr.inputs[0])
    frost = K.math_(nt, 'MULTIPLY', K.math_(nt, 'MULTIPLY', dome.outputs[0], fmr.outputs[0]), K.math_(nt, 'ADD', .35, frr.outputs[0]))
    frost = K.math_(nt, 'MINIMUM', frost, 1.0)
    col = K.mix(nt, col, (.36, .39, .45), frost)
    # neve de fuligem nas juntas
    col = K.mix(nt, (.05, .05, .055), col, gap.outputs[0])
    # gelo negro: manchas lisas e escuras
    ic = K.noise(nt, v, w, .6, 4, .5, seed + 9)
    icr = K.ramp(nt, [(.6, (0, 0, 0)), (.64, (1, 1, 1))]); K.L(nt, ic.outputs["Fac"], icr.inputs[0])
    col = K.mix(nt, col, (.012, .015, .022), K.math_(nt, 'MULTIPLY', icr.outputs[0], .85))
    K.L(nt, col, b.inputs["Base Color"])
    rough = K.math_(nt, 'SUBTRACT', K.math_(nt, 'ADD', .45, K.math_(nt, 'MULTIPLY', frost, .4)), K.math_(nt, 'MULTIPLY', icr.outputs[0], .4))
    K.L(nt, rough, b.inputs["Roughness"])
    h = K.math_(nt, 'ADD', dome.outputs[0], K.math_(nt, 'MULTIPLY', nf.outputs["Fac"], .15))
    h = K.math_(nt, 'ADD', h, K.math_(nt, 'MULTIPLY', frr.outputs[0], K.math_(nt, 'MULTIPLY', frost, .3)))
    K.bump(nt, b, K.math_(nt, 'SUBTRACT', h, K.math_(nt, 'MULTIPLY', icr.outputs[0], .5)), .7, .05)
    return m

TIJ = lambda: K.mat_brick("tijolo_noite", ("wall", K.T), 7.0, (.055, .036, .032), 3.0, 0.0)
PED = lambda: K.mat_stone("pedra_fria", (.075, .078, .088), (.028, .03, .036), 2.0, 0.0)
FER = lambda: K.mat_metal("ferro_frio", (.03, .032, .036), .3, 5.0, .45)
LANT = lambda s=9: K.mat_emit("vidro_lampiao_c", LAMP, s)

# ================================================================ peças
def lanterna(m, p, s=1.0, luz=260, halo=True):
    """Lanterna de gás de 4 vidros com capelo, armação e halo."""
    x, y, z = p; fe = FER()
    cyl(fe, (x, y, z + .3*s), .19*s, .16*s, verts=4, r2=.02*s, rot=(0, 0, 45))
    cyl(LANT(), (x, y, z + .05*s), .11*s, .36*s, verts=4, r2=.15*s, rot=(0, 0, 45))
    for k in range(4):
        a = math.radians(90*k)
        along(fe, (x + math.cos(a)*.15*s, y + math.sin(a)*.15*s, z + .23*s), (x + math.cos(a)*.11*s, y + math.sin(a)*.11*s, z - .13*s), .012*s, verts=4)
    cyl(fe, (x, y, z - .16*s), .08*s, .06*s, verts=8)
    sphere(fe, (x, y, z + .42*s), (.035*s, .035*s, .05*s), segs=8)
    if halo:
        o = sphere(mat_halo(), (x, y, z + .05*s), (.75*s, .75*s, .75*s), segs=20)
        o.visible_shadow = False; o.visible_diffuse = False; o.visible_glossy = False
    point((x, y, z + .02*s), LAMP, luz, .12*s, "lampiao")

def poste(m, bracos=1, h=3.4, luz=260):
    """Poste de gás de ferro fundido, gótico (bracos=1 simples, 2 duplo, 3 candelabro)."""
    fe = FER()
    cyl(fe, (0, 0, .18), .24, .36, verts=8, r2=.17)
    cyl(fe, (0, 0, .45), .15, .2, verts=8, r2=.11)
    cyl(fe, (0, 0, h/2 + .3), .065, h - .3, verts=10, r2=.045)
    for z in (.75, h - .2): torus(fe, (0, 0, z), .075, .022)
    for k in range(4):   # aletas da base
        a = math.radians(45 + 90*k)
        box(fe, (math.cos(a)*.13, math.sin(a)*.13, .5), (.04, .04, .4), (0, 0, math.degrees(a)), .005)
    if bracos == 1:
        lanterna(m, (0, 0, h + .25), 1.0, luz)
    else:
        for k in range(bracos):
            a = math.radians(-45 + 360*k/bracos)
            px, py = math.cos(a)*.6, math.sin(a)*.6
            along(fe, (0, 0, h - .1), (px, py, h + .1), .03, verts=6)
            torus(fe, (px*.55, py*.55, h - .05), .1, .012, (90, 0, math.degrees(a) + 90))
            lanterna(m, (px, py, h - .12), .85, luz*.7)
        sphere(fe, (0, 0, h + .2), (.06, .06, .12), segs=8)
        cyl(fe, (0, 0, h + .4), .015, .3, verts=4, r2=.001)
    # escadinha do acendedor: braço curto onde ele apoia a escada
    along(fe, (0, 0, h - .55), (-.4, 0, h - .55), .016, verts=4)

def janela_fundo(m, c, x, y, z, w, h, eixo, sinal, acesa=False):
    """Janela simples em parede lisa (lados de fundo)."""
    mat = K.mat_window_lit() if acesa else K.mat_solid("interior", (.006, .005, .005), 0, .9)
    if eixo == "x": box(mat, (x, y + sinal*.13, z), (w, .02, h), bevel=0)
    else: box(mat, (x + sinal*.13, y, z), (.02, w, h), bevel=0)

def sobrado(m, seed=0, nf=3, W=6.0, D=5.0, FH=3.0, acesas=(), escada=True, lanterna_porta=False):
    """Sobrado gótico de tijolo escuro: 3 andares, telhado íngreme com neve, chaminés,
    lucarnas, cano de gás pela fachada, escada de incêndio de ferro e pingentes de gelo."""
    r = random.Random(seed); c = TIJ(); st = PED(); fe = FER(); ice = mat_gelo("pingente", (.25, .3, .38), .05)
    Hh = nf*FH
    nbx, nby = 3, 2; bwx, bwy = W/nbx, D/nby
    for f in range(nf):
        z = f*FH
        for i in range(nbx):
            if f == 0 and i == 1: k_ = "door"
            elif (f, i) in acesas: k_ = "lit"
            else: k_ = r.choice(["dark", "dark", "dark", "boarded", "broken"]) if f else r.choice(["dark", "boarded", "dark"])
            cx = -W/2 + bwx*(i + .5)
            A.bay(m, c, cx, -D/2, z, bwx, FH, "x", k_, seed + f*10 + i)
            if k_ != "door":   # arco ogival de pedra sobre a janela
                ww, wh, wz = bwx*.5, FH*.48, z + FH*.32
                prism(st, (cx, -D/2 - .16, wz + wh + .1), ww + .26, .1, .42)
            if k_ == "lit": point((cx, -D/2 - .8, z + FH*.55), (1, .55, .2), 22, .3)
        for j in range(nby):
            k_ = "lit" if ("y", f, j) in acesas else r.choice(["dark", "dark", "boarded", "broken"])
            cy = -D/2 + bwy*(j + .5)
            A.bay(m, c, W/2, cy, z, bwy, FH, "y", k_, seed + 100 + f*10 + j)
            o = prism(st, (W/2 + .16, cy, z + FH*.32 + FH*.48 + .1), bwy*.5 + .26, .1, .42); o.rotation_euler.z = math.pi/2
            if k_ == "lit": point((W/2 + .8, cy, z + FH*.55), (1, .55, .2), 22, .3)
        box(st, (0, -D/2 - .15, z + FH - .08), (W + .12, .1, .18), bevel=.01)       # cornija entre andares
        box(st, (W/2 + .15, 0, z + FH - .08), (.1, D + .12, .18), bevel=.01)
        if f:
            for j in range(2):
                janela_fundo(m, c, -W/2, -D/2 + D*(j + .5)/2, z + FH*.55, 1.0, 1.4, "y", -1, ("w", f, j) in acesas)
    box(c, (0, D/2, Hh/2), (W, .25, Hh), bevel=.01)
    box(c, (-W/2, 0, Hh/2), (.25, D, Hh), bevel=.01)
    box(st, (0, 0, .2), (W + .2, D + .2, .4), bevel=.02)                           # embasamento
    # telhado íngreme de duas águas, cumeeira ao longo de X
    rf = mat_telhado(seed=float(seed % 7)); rh = 3.8; hd = D/2 + .4
    ang = math.degrees(math.atan2(rh, hd)); sl = math.hypot(rh, hd) + .15
    for sy in (-1, 1):
        box(rf, (0, sy*hd/2, Hh + rh/2), (W + .5, sl, .18), (-sy*ang, 0, 0), .01)
    box(st, (0, 0, Hh + rh + .02), (W + .55, .2, .18), bevel=.02)                 # cumeeira
    for sx in (-1, 1):
        o = prism(c, (sx*W/2, 0, Hh), D, .25, rh); o.rotation_euler.z = math.pi/2   # empenas
        cyl(fe, (sx*(W/2 + .2), 0, Hh + rh + .45), .03, .9, verts=6)              # agulha
        sphere(fe, (sx*(W/2 + .2), 0, Hh + rh + .2), (.07, .07, .07), segs=8)
    # janela redonda na empena da direita (+X)
    cyl(K.mat_window_lit() if ("g",) in acesas else K.mat_solid("interior", (.006, .005, .005), 0, .9), (W/2 + .13, 0, Hh + 1.4), .38, .05, (0, 90, 0), 16)
    torus(st, (W/2 + .16, 0, Hh + 1.4), .42, .07, (0, 90, 0))
    # lucarna na água da frente
    lx = r.choice([-1.6, 1.4])
    box(c, (lx, -1.15, Hh + 1.1), (1.0, 1.6, 2.0), bevel=.01)
    o = prism(rf, (lx, -1.15, Hh + 2.1), 1.25, 1.75, .9)
    janela_lit = ("d",) in acesas
    box(K.mat_window_lit() if janela_lit else K.mat_solid("interior", (.006, .005, .005), 0, .9), (lx, -1.96, Hh + 1.15), (.5, .02, .9), bevel=0)
    prism(st, (lx, -1.98, Hh + 1.62), .7, .08, .3)
    if janela_lit: point((lx, -2.6, Hh + 1.2), (1, .55, .2), 15, .2)
    # chaminés
    for k, cx in enumerate(r.sample([-W/2 + .7, -.4, W/2 - .8], 2)):
        cy = r.uniform(.4, 1.3); hc = rh + 1.4 + r.uniform(0, .8)
        box(c, (cx, cy, Hh + hc/2), (.8, .55, hc), bevel=.01)
        box(st, (cx, cy, Hh + hc + .06), (.95, .7, .14), bevel=.015)
        for j in range(r.choice([2, 3])):
            cyl(K.mat_solid("barro", (.09, .045, .03), 0, .8), (cx - .2 + j*.2, cy, Hh + hc + .3), .07, .35, verts=10, r2=.06)
    # cano de gás pela fachada, com medidor e braçadeiras
    px = -W/2 + .35 if seed % 2 else W/2 - .35
    along(fe, (px, -D/2 - .22, .3), (px, -D/2 - .22, Hh - .35), .055)
    along(fe, (-W/2 + .2, -D/2 - .22, Hh - .35), (W/2 - .2, -D/2 - .22, Hh - .35), .045)
    along(fe, (px, -D/2 - .22, FH - .45), (px + (1.2 if px < 0 else -1.2), -D/2 - .22, FH - .45), .035)
    for z in (1.0, 2.2, 3.8, 5.6, 7.4):
        if z < Hh - .5: torus(fe, (px, -D/2 - .22, z), .07, .015)
    box(K.mat_brass(), (px, -D/2 - .32, .9), (.35, .2, .45), bevel=.02)
    cyl(K.mat_emit("mostrador", (.9, .8, .55), .6), (px, -D/2 - .43, 1.0), .08, .02, (90, 0, 0), 12)
    # escada de incêndio no lado +X
    if escada:
        ex = W/2 + .75
        for f in range(1, nf):
            z = f*FH + .02
            box(fe, (ex, -.2, z), (1.0, D*.7, .05), bevel=.005)
            for yy in (-D*.35 - .2, D*.35 - .2):
                along(fe, (W/2 + .15, yy + .2 - .2, z - .9), (ex, yy + .2 - .2, z - .02), .02, verts=4)
            for j in range(9):
                yy = -D*.35 - .2 + j*D*.7/8
                cyl(fe, (ex + .47, yy, z + .5), .01, 1.0, verts=4)
            along(fe, (ex + .47, -D*.35 - .2, z + 1.0), (ex + .47, D*.35 - .2, z + 1.0), .018, verts=5)
            # lance de escada até o patamar de baixo (ou pendurado no primeiro)
            y0, y1 = D*.35 - .45, -D*.35 + .3
            z0 = z - FH if f > 1 else z - 1.6
            for sx in (-.3, .3):
                along(fe, (ex + sx, y0, z0), (ex + sx, y1, z), .018, verts=4)
            for j in range(10):
                t = j/9
                box(fe, (ex, y0 + (y1 - y0)*t, z0 + (z - z0)*t), (.6, .12, .025), bevel=0)
    # porta: degrau e lanterna (só alguns sobrados pagam o lampião)
    box(st, (0, -D/2 - .45, .1), (1.6, .7, .2), bevel=.02)
    if lanterna_porta:
        along(fe, (.85, -D/2 - .1, 2.6), (.85, -D/2 - .55, 2.6), .02, verts=5)
        lanterna(m, (.85, -D/2 - .55, 2.35), .6, 70, halo=True)
    # pingentes de gelo no beiral da frente e da cornija
    for k in range(int(W*4)):
        x = -W/2 - .2 + (W + .4)*k/(W*4) + r.uniform(-.05, .05); L_ = r.uniform(.12, .55)
        cyl(ice, (x, -hd + .1, Hh + .02 - L_/2), .004, L_, verts=6, r2=.035)
    for k in range(int(W*2.5)):
        x = -W/2 + W*k/(W*2.5) + r.uniform(-.05, .05); L_ = r.uniform(.08, .3)
        cyl(ice, (x, -D/2 - .18, FH - .17 - L_/2), .003, L_, verts=6, r2=.025)
    # neve de fuligem amontoada no pé da fachada
    sn = mat_neve()
    for k in range(5):
        x = r.uniform(-W/2, W/2)
        if abs(x) < .9: continue
        o = sphere(sn, (x, -D/2 - .45, -.05), (r.uniform(.5, 1.0), r.uniform(.35, .55), r.uniform(.25, .45)), segs=12)
        displace(o, .06, .25, seed + k, 1)

def monte_neve(m, seed=0):
    r = random.Random(seed); sn = mat_neve(seed=float(seed % 3))
    for k in range(r.randint(3, 5)):
        o = sphere(sn, (r.uniform(-.8, .8), r.uniform(-.5, .5), -.1), (r.uniform(.5, 1.1), r.uniform(.4, .8), r.uniform(.25, .55)), segs=14)
        displace(o, .08, .3, seed + k, 1)
    for k in range(6):   # pedaços de fuligem e lixo congelado
        box(K.mat_solid("fuligem", (.012, .012, .013), 0, .9), (r.uniform(-1, 1), r.uniform(-.7, .7), .2), (r.uniform(.05, .15), r.uniform(.05, .12), .03), (r.uniform(-20, 20), r.uniform(-20, 20), r.uniform(0, 90)), 0)

def banco(m, seed=0):
    """Banco de praça congelado: ferro fundido, ripas e neve no assento."""
    r = random.Random(seed); fe = FER(); wd = K.mat_wood("madeira_fria", (.05, .04, .035))
    for sx in (-.75, .75):
        box(fe, (sx, -.18, .22), (.05, .05, .44), bevel=0); box(fe, (sx, .18, .4), (.05, .05, .8), (-12, 0, 0), 0)
        torus(fe, (sx, -.05, .22), .14, .02, (0, 90, 0))
        box(fe, (sx, 0, .44), (.06, .5, .04), bevel=0)
    for k in range(4): box(wd, (0, -.2 + k*.13, .47), (1.7, .1, .035), bevel=.005)
    for k in range(3): box(wd, (0, .26, .62 + k*.13), (1.7, .035, .09), (-12, 0, 0), .005)
    o = box(mat_neve(seed=1.0), (r.uniform(-.2, .2), -.02, .53), (1.4, .42, .09), bevel=.04); displace(o, .03, .2, seed, 2)
    ice = mat_gelo("pingente", (.25, .3, .38), .05)
    for k in range(12):
        L_ = r.uniform(.05, .2); cyl(ice, (-.8 + k*.145, -.25, .45 - L_/2), .003, L_, verts=6, r2=.02)

def relogio(m, seed=0):
    """Relógio de rua: coluna de ferro com quatro mostradores pálidos."""
    fe = FER(); st = PED()
    box(st, (0, 0, .25), (.8, .8, .5), bevel=.04)
    cyl(fe, (0, 0, 2.2), .11, 3.5, verts=12, r2=.08)
    for z in (.9, 3.7): torus(fe, (0, 0, z), .13, .03)
    box(fe, (0, 0, 4.4), (.85, .85, .85), bevel=.04)
    face = K.mat_emit("mostrador_relogio", (.95, .88, .62), 1.6)
    for k in range(4):
        a = math.radians(90*k)
        nx, ny = math.cos(a), math.sin(a)
        cyl(face, (nx*.43, ny*.43, 4.4), .33, .03, (0, 90, math.degrees(a)), 24)
        torus(fe, (nx*.45, ny*.45, 4.4), .34, .03, (0, 90, math.degrees(a)))
        box(K.mat_solid("ponteiro", (.01, .01, .01)), (nx*.46, ny*.46, 4.47), (.02 if nx == 0 else .01, .01 if nx == 0 else .02, .2), (0, 0, 0), 0)
    cyl(mat_telhado(seed=3.0), (0, 0, 5.05), .7, .5, verts=4, r2=.02, rot=(0, 0, 45))
    sphere(fe, (0, 0, 5.4), (.06, .06, .1), segs=8)
    point((.9, -.9, 4.4), (1, .9, .6), 18, .3)

def estatua_gelo(m, seed=0):
    """Estátua do Primeiro Acendedor, coberta de gelo: ergue uma lanterna que ninguém acende mais."""
    st = PED(); ice = mat_gelo("gelo_estatua", (.16, .2, .27), .12); sn = mat_neve(seed=2.0)
    box(st, (0, 0, .2), (2.4, 2.4, .4), bevel=.04)
    box(st, (0, 0, .55), (1.9, 1.9, .3), bevel=.03)
    box(st, (0, 0, 1.4), (1.3, 1.3, 1.4), bevel=.05)
    box(st, (0, 0, 2.15), (1.5, 1.5, .15), bevel=.03)
    cyl(ice, (0, 0, 3.1), .55, 1.9, verts=16, r2=.25)          # manto
    sphere(ice, (0, 0, 4.25), (.22, .22, .27), segs=14)          # cabeça
    cyl(ice, (0, 0, 4.4), .3, .35, verts=12, r2=.15)             # capuz
    along(ice, (.2, -.05, 3.85), (.45, -.2, 4.9), .1, .07)        # braço erguido
    along(K.mat_metal("ferro_gelo", (.03, .035, .04), .7, 9.0), (.47, -.22, 4.7), (.6, -.3, 5.7), .025, verts=6)  # vara de acender
    cyl(FER(), (.62, -.32, 5.8), .12, .25, verts=4, r2=.16)       # lanterna morta
    along(ice, (-.2, -.05, 3.8), (-.35, -.3, 3.0), .1, .08)       # braço baixo
    for k in range(10):   # gelo escorrido
        a = math.radians(36*k)
        cyl(ice, (math.cos(a)*.66, math.sin(a)*.66, 1.85), .01, .5, verts=6, r2=.06)
    for k, (x, y) in enumerate([(-.9, -.8), (.8, -.9), (-.9, .7)]):
        o = sphere(sn, (x, y, .42), (.5, .4, .2), segs=10); displace(o, .04, .2, k, 1)
    o = sphere(sn, (0, 0, 2.25), (.75, .75, .1), segs=12); displace(o, .03, .2, 9, 1)

def carrinho(m, seed=0):
    """Carrinho do acendedor: botijão de gás, mangueira, escada e a vara com gancho."""
    r = random.Random(seed); fe = FER(); wd = K.mat_wood("madeira_fria", (.05, .04, .035))
    box(wd, (0, 0, .55), (1.4, .8, .08), bevel=.01)
    for sy in (-1, 1):
        box(wd, (0, sy*.4, .7), (1.4, .04, .3), bevel=.005)
        cyl(fe, (-.25, sy*.48, .38), .38, .06, (90, 0, 0), 20)
        torus(fe, (-.25, sy*.5, .38), .38, .03, (90, 0, 0))
        for k in range(6):
            a = math.radians(30*k)
            along(fe, (-.25, sy*.5, .38), (-.25 + math.cos(a)*.36, sy*.5, .38 + math.sin(a)*.36), .012, verts=4)
    for sy in (-.3, .3): along(wd, (.7, sy, .58), (1.4, sy, .75), .025, verts=6)
    along(wd, (.6, 0, .55), (.6, 0, .05), .03, verts=6)
    cyl(K.mat_metal("botijao", (.04, .06, .05), .5, 2.0), (-.2, 0, 1.0), .25, .85, verts=16)
    sphere(K.mat_metal("botijao", (.04, .06, .05), .5, 2.0), (-.2, 0, 1.42), (.25, .25, .15), segs=12)
    cyl(K.mat_brass(), (-.2, 0, 1.6), .05, .15, verts=8)
    torus(K.mat_solid("borracha", (.015, .014, .013), 0, .6), (.35, .05, .7), .18, .03)
    # escada encostada
    for sy in (-.18, .18): along(wd, (-.65, sy, .6), (.95, sy, 1.45), .025, verts=5)
    for k in range(6):
        t = (k + .5)/6; box(wd, (-.65 + 1.6*t, 0, .6 + .85*t), (.03, .36, .03), bevel=0)
    # vara de acender com lanterna acesa
    along(fe, (-.6, -.35, .6), (-.4, -.45, 3.0), .018, verts=5)
    lanterna(m, (-.4, -.45, 2.75), .55, 45, halo=True)
    o = box(mat_neve(seed=1.0), (.1, 0, .63), (1.0, .5, .06), bevel=.02); displace(o, .02, .2, seed, 2)

def banca(m, seed=0):
    """Posto do acendedor: banca de madeira onde se vende óleo, pavio e luz."""
    r = random.Random(seed); fe = FER(); wd = K.mat_wood("madeira_fria", (.06, .045, .035))
    W, D = 2.8, 1.6
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(wd, (sx*W/2, sy*D/2, 1.2 if sy > 0 else 1.0), .05, 2.4 if sy > 0 else 2.0, verts=6)
    box(wd, (0, D/2, 1.0), (W, .06, 2.0), bevel=.005)                          # fundo
    box(wd, (0, -D/2 + .2, .5), (W, .4, 1.0), bevel=.01)                        # balcão
    box(wd, (0, -D/2 + .2, 1.03), (W + .1, .5, .06), bevel=.01)
    o = box(K.mat_cloth("lona_azul", (.03, .045, .07), 4.0), (0, 0, 2.25), (W + .5, D + .8, .05), (-14, 0, 0), 0)
    displace(o, .05, .3, seed, 3)
    o = box(mat_neve(seed=2.0), (0, .15, 2.32), (W + .2, D + .2, .08), (-14, 0, 0), .03); displace(o, .04, .25, seed + 1, 2)
    for k in range(3):   # prateleira com latas de óleo
        for j in range(5):
            cyl(K.mat_brass() if (j + k) % 2 else K.mat_metal("lata", (.06, .05, .04), .5, 7.0), (-1.1 + j*.5, D/2 - .2, .4 + k*.45), .09, .25, verts=10)
        box(wd, (0, D/2 - .2, .26 + k*.45), (W - .2, .3, .03), bevel=0)
    for k in range(5):   # lâmpadas e pavios no balcão
        cyl(K.mat_brass(), (-1.0 + k*.5, -D/2 + .2, 1.12), .05, .12, verts=8)
        sphere(LANT(5), (-1.0 + k*.5, -D/2 + .2, 1.24), (.035, .035, .05), segs=8)
    for k, x in enumerate((-1.1, 0, 1.1)):   # lanternas penduradas no toldo
        along(fe, (x, -D/2 - .2, 2.15), (x, -D/2 - .2, 1.85), .008, verts=4)
        lanterna(m, (x, -D/2 - .2, 1.7), .45, 40, halo=k == 1)
    box(wd, (0, -D/2 - .35, 2.55), (1.6, .05, .45), (-10, 0, 0), .01)          # tabuleta
    box(LANT(1.2), (0, -D/2 - .39, 2.55), (1.0, .01, .08), (-10, 0, 0), 0)

def gasometro(m, seed=0):
    """O Gasômetro da Praça dos Mil Lampiões: tanque de gás de chapas rebitadas dentro de uma
    armação de colunas de treliça, com uma coroa de lanternas no topo."""
    r = random.Random(seed); fe = FER(); st = PED()
    tank = K.mat_metal("chapa_gasometro", (.04, .05, .055), .55, 3.0, .5)
    R, Ht, z0 = 4.4, 7.2, .7
    cyl(st, (0, 0, .35), R + .8, .7, verts=48)
    box(st, (0, 0, .02), (1, 1, .04), bevel=0)
    cyl(tank, (0, 0, z0 + Ht/2), R, Ht, verts=56)
    for k in range(7): torus(fe, (0, 0, z0 + .2 + k*Ht/6.2), R + .02, .06)
    for k in range(28):
        a = 2*math.pi*k/28
        box(fe, (math.cos(a)*(R + .02), math.sin(a)*(R + .02), z0 + Ht/2), (.06, .1, Ht), (0, 0, math.degrees(a)), 0)
    sphere(mat_neve(seed=4.0), (0, 0, z0 + Ht), (R*1.0, R*1.0, 1.1), segs=40)
    cyl(fe, (0, 0, z0 + Ht + 1.1), .5, .4, verts=12)
    # armação de treliça
    Rc, Hc, N = R + 1.25, 13.0, 12
    cols = []
    for k in range(N):
        a = 2*math.pi*(k + .5)/N; ca, sa = math.cos(a), math.sin(a)
        cx, cy = ca*Rc, sa*Rc; cols.append((cx, cy, a))
        box(st, (cx, cy, .45), (.8, .8, .9), (0, 0, math.degrees(a)), .03)
        tx, ty = -sa, ca
        for s in (-1, 1):
            for d in (-1, 1):
                box(fe, (cx + ca*d*.17 + tx*s*.17, cy + sa*d*.17 + ty*s*.17, Hc/2 + .45), (.07, .07, Hc), (0, 0, math.degrees(a)), 0)
        for j in range(int(Hc/.55)):   # treliça em zigue-zague nas duas faces
            z1, z2 = .9 + j*.55, .9 + (j + 1)*.55
            s1 = 1 if j % 2 else -1
            for d in (-1, 1):
                along(fe, (cx + ca*d*.17 + tx*s1*.17, cy + sa*d*.17 + ty*s1*.17, z1), (cx + ca*d*.17 - tx*s1*.17, cy + sa*d*.17 - ty*s1*.17, z2), .018, verts=4)
        sphere(fe, (cx, cy, Hc + 1.05), (.12, .12, .12), segs=8)
        cyl(fe, (cx, cy, Hc + .95), .25, .2, verts=4, rot=(0, 0, math.degrees(a)))
        # roldana guia contra o tanque
        cyl(K.mat_brass(), (ca*(R + .3), sa*(R + .3), z0 + Ht - .3), .2, .14, (90, 0, math.degrees(a) + 90), 12)
    for zr in (4.6, 8.8, Hc + .8):   # vigas em anel
        for k in range(N):
            x1, y1, _ = cols[k]; x2, y2, _ = cols[(k + 1) % N]
            along(fe, (x1, y1, zr), (x2, y2, zr), .09, verts=6)
            along(fe, (x1, y1, zr - .5), (x2, y2, zr - .5), .04, verts=4)
            for j in range(4):
                t1, t2 = j/4, (j + .5)/4
                along(fe, (x1 + (x2 - x1)*t1, y1 + (y2 - y1)*t1, zr - .5), (x1 + (x2 - x1)*t2, y1 + (y2 - y1)*t2, zr), .02, verts=4)
    for k in range(N):   # contraventamento em X no vão de baixo
        x1, y1, _ = cols[k]; x2, y2, _ = cols[(k + 1) % N]
        if k in (8,): continue
        along(fe, (x1, y1, .9), (x2, y2, 4.1), .03, verts=4); along(fe, (x2, y2, .9), (x1, y1, 4.1), .03, verts=4)
    # coroa de lanternas no topo da armação
    for (cx, cy, a) in cols:
        along(fe, (cx, cy, Hc + .8), (cx + math.cos(a)*.6, cy + math.sin(a)*.6, Hc + 1.0), .025, verts=4)
        lanterna(m, (cx + math.cos(a)*.6, cy + math.sin(a)*.6, Hc + .75), .8, 120, halo=True)
    # escada de marinheiro na coluna da frente e passarela no topo do tanque
    cx, cy, a = cols[8]
    for s in (-.25, .25):
        along(fe, (cx + math.cos(a)*.35 - math.sin(a)*s, cy + math.sin(a)*.35 + math.cos(a)*s, .9), (cx + math.cos(a)*.35 - math.sin(a)*s, cy + math.sin(a)*.35 + math.cos(a)*s, Hc), .02, verts=4)
    for j in range(int(Hc/.35)):
        along(fe, (cx + math.cos(a)*.35 + math.sin(a)*.25, cy + math.sin(a)*.35 - math.cos(a)*.25, 1.0 + j*.35), (cx + math.cos(a)*.35 - math.sin(a)*.25, cy + math.sin(a)*.35 + math.cos(a)*.25, 1.0 + j*.35), .012, verts=4)
    # medidor de pressão grande voltado para a câmera e válvula
    a = math.radians(-45); nx, ny = math.cos(a), math.sin(a)
    cyl(K.mat_brass(), (nx*(R + .1), ny*(R + .1), 3.2), .6, .12, (90, 0, 45), 24)
    cyl(K.mat_emit("mostrador_gas", (.95, .85, .55), 1.4), (nx*(R + .17), ny*(R + .17), 3.2), .5, .02, (90, 0, 45), 24)
    box(K.mat_solid("ponteiro", (.01, .01, .01)), (nx*(R + .19), ny*(R + .19), 3.3), (.03, .01, .4), (0, 25, -45), 0)
    point((nx*(R + 1.2), ny*(R + 1.2), 3.2), (1, .85, .55), 30, .3)
    # cano mestre saindo da base para a cidade, com volante
    a2 = math.radians(-10); bx, by = math.cos(a2), math.sin(a2)
    along(fe, (bx*(R - .2), by*(R - .2), 1.1), (bx*(R + 2.5), by*(R + 2.5), 1.1), .22)
    for t in (R + .4, R + 2.2): torus(fe, (bx*t, by*t, 1.1), .25, .04, (0, 90, math.degrees(a2)))
    along(fe, (bx*(R + 1.4), by*(R + 1.4), 1.3), (bx*(R + 1.4), by*(R + 1.4), 2.0), .04, verts=6)
    torus(K.mat_metal("volante", (.12, .02, .015), .4, 3.0), (bx*(R + 1.4), by*(R + 1.4), 2.0), .3, .035)
    # neve no topo das vigas e no pé
    sn = mat_neve(seed=4.0)
    for k in range(9):
        a = r.uniform(0, 2*math.pi); rr = R + r.uniform(.6, 1.6)
        o = sphere(sn, (math.cos(a)*rr, math.sin(a)*rr, .62), (r.uniform(.5, 1.0), r.uniform(.4, .7), .22), segs=10); displace(o, .05, .25, k, 1)

def cano_rua(p, q, h=.9):
    """Cano de gás aéreo sobre cavaletes de ferro, ligando o Gasômetro às casas."""
    fe = FER(); p = (p[0], p[1], h); q = (q[0], q[1], h)
    along(fe, p, q, .14)
    L = math.dist(p, q); n = max(2, int(L/3))
    for k in range(n + 1):
        t = k/n; x, y = p[0] + (q[0] - p[0])*t, p[1] + (q[1] - p[1])*t
        along(fe, (x, y, 0), (x, y, h - .1), .04, verts=6)
        along(fe, (x - .3, y, 0), (x, y, h - .4), .02, verts=4); along(fe, (x + .3, y, 0), (x, y, h - .4), .02, verts=4)
        if k % 2: torus(fe, (x, y, h), .17, .03, (90 if abs(q[0] - p[0]) < abs(q[1] - p[1]) else 0, 0 if abs(q[0] - p[0]) < abs(q[1] - p[1]) else 90, 0))

def calcada(x0, x1, y0, y1, h=.14):
    st = PED()
    box(st, ((x0 + x1)/2, (y0 + y1)/2, h/2), (x1 - x0, y1 - y0, h), bevel=.03)

# ================================================================ montagem
m = C.mats()
r = random.Random(41)
SOB = [  # variantes (chave, seed, andares, janelas acesas, lanterna na porta)
    ("sobA", 1, 3, {(1, 0), ("y", 2, 1), ("d",)}, True),
    ("sobB", 2, 3, {(2, 2), ("g",)}, False),
    ("sobC", 3, 4, {(1, 2), (3, 0), ("y", 1, 0)}, False),
    ("sobD", 4, 3, set(), False),
    ("sobE", 5, 4, {(2, 1), ("d",), ("y", 3, 1)}, True),
]
def sob(i, x, y, rot):
    k, sd, nf, ac, lp = SOB[i % len(SOB)]
    return grupo(lambda mm, sd=sd, nf=nf, ac=ac, lp=lp: sobrado(mm, sd, nf, acesas=ac, lanterna_porta=lp), x, y, rot, 1.0, chave=k)

# fileira A (frente para -Y), atrás à direita da praça; avenida entre x=1 e x=7
for i, x in enumerate([-26, -20, -14, -8, -2, 10, 16, 22, 28, 34]): sob(i, x, 15.5, 0)
# fileira B (frente para +X), atrás à esquerda; beco entre y=-12 e y=-7
for i, y in enumerate([8, 2, -4, -15, -21, -27, -33]): sob(i + 2, -15.5, y, -90)
# segunda linha de telhados, sumindo na névoa
for i, x in enumerate([-20, -14, -8, -2, 10, 16, 22, 28]): sob(i + 3, x, 27.5, 0)
for i, y in enumerate([2, -4, -15, -21, -27]): sob(i + 1, -27.5, y, -90)
# casas que fecham o fundo da avenida e do beco
sob(1, 4, 40, 0); sob(3, -40, -9.5, -90)

# calçadas de pedra na frente das fileiras
calcada(-29, 37, 11.2, 13.1); calcada(-13.1, -11.2, -36, 11.2)

# o marco: Gasômetro no centro da praça
GX, GY = -2.5, 2.5
grupo(gasometro, GX, GY, 0, 1.0, chave="gasometro")
# grade de ferro em volta, com abertura voltada para a câmera
Rg = 8.2
n_g = int(2*math.pi*Rg/K.T)
for k in range(n_g):
    a = 2*math.pi*k/n_g
    if abs(((math.degrees(a) + 45) + 180) % 360 - 180) < 9: continue
    por("cerca_ferro", GX + math.cos(a)*Rg, GY + math.sin(a)*Rg, math.degrees(a) + 90)

# a Praça dos Mil Lampiões: anel de candelabros, postes nas calçadas e na avenida
def P(x, y, b=1, rot=0, luz=260): grupo(lambda mm, b=b, luz=luz: poste(mm, b, 3.4 if b == 1 else 3.8, luz), x, y, rot, 1.0, chave=f"poste{b}_{luz}")
for k in range(10):
    a = 2*math.pi*(k + .5)/10
    P(GX + math.cos(a)*10.2, GY + math.sin(a)*10.2, 3, math.degrees(a), 240)
for x in (-22, -16, -10, 4, 13, 19, 25, 31): P(x, 11.7, 1, 0)
for y in (-30, -24, -18, -2, 4, 10): P(-11.7, y, 1, 0)
for y in (19, 25, 31, 37): P(1.6, y, 1, 0, 200); P(6.4, y + 3, 1, 0, 200)
for x in (-18, -24, -30, -36): P(x, -7.5, 1, 0, 200)
for (x, y) in [(13, -4), (6, -13), (-4, -16), (16, 4)]: P(x, y, 1, 0)
# postes apagados: quem não paga, fica no escuro
for (x, y, rt) in [(-11.7, -12.5, 0), (-6, 12, 0), (22, 1, 0)]:
    por("poste_gas_quebrado", x, y, rt)

# canos de gás aéreos do Gasômetro até as casas
cano_rua((GX + 6.9, GY - 1.2), (11.5, 1.3))
cano_rua((11.5, 1.3), (11.5, 11.4))

# vocabulário espalhado: bancos, relógio, estátua, montes de neve, carrinhos
grupo(relogio, 9.5, 7.5, 0, 1.0, chave="relogio")
grupo(estatua_gelo, -8.5, -9.0, 0, 1.0, chave="estatua")
for (x, y, rt) in [(-5.5, -12.0, 0), (-11.5, -5.8, 90), (7.5, -9.0, 45), (3.0, 9.6, 0), (-9.0, 9.6, 0), (16, 9.6, 0)]:
    grupo(banco, x, y, rt, 1.0, chave="banco")
for i, (x, y) in enumerate([(-10.5, 12.0), (-1, 11.6), (14.5, 11.9), (24, 12.2), (-12, 0), (-12.2, -9.5), (-11.8, -20), (8.5, 12.5),
                            (12.5, -8.5), (-3, -14.5), (17, -1.5), (-14, 12.5), (2.5, -10.5), (20, 6)]):
    grupo(monte_neve, x, y, r.uniform(0, 360), r.uniform(.8, 1.3), chave=f"neve{i % 4}")

# sobreviventes: o Posto do Acendedor, com braseiro e carrinhos
grupo(banca, 6.8, -5.2, 0, 1.0, chave="banca")
por("tonel_fogo", 4.6, -6.4); por("tonel_fogo", 9.6, -3.4)
por("caixas", 9.2, -6.6, 30); por("barris", 4.0, -3.8, 10); por("sacos_areia", 8.8, -2.2, 0)
grupo(carrinho, 3.2, -8.6, 25, 1.0, chave="carrinho")
grupo(carrinho, -6.8, 6.8 - 14, -60, 1.0, chave="carrinho")
por("tenda_vigilia", 11.6, -8.0, 90)
por("varal_roupas", 10.8, -1.0, 90)
C.ponto((6.8, -7.0, 1.4), (1, .5, .18), 220, .4)

# destaques do chão: neve de fuligem acumulada e gelo negro
NEVE = mat_neve(seed=7.0); GELO = mat_gelo("gelo_negro", (.006, .009, .016), .03)
C.faixa(NEVE, [(-30, 10.9), (38, 10.9)], 1.4, z=.01, nome="neve_calcada_a")
C.faixa(NEVE, [(-10.9, -38), (-10.9, 10.9)], 1.4, z=.01, nome="neve_calcada_b")
for i, (x, y, rr) in enumerate([(-6, 8.5, 2.2), (6, 12, 1.4), (14, 3, 2.6), (-10, -3, 1.8), (-1, -11, 2.0), (18, -6, 2.2)]):
    C.mancha(NEVE, (x, y), rr, seed=i + 3, irregular=.5, nome="neve_fuligem")
for i, (x, y, rr) in enumerate([(1.5, -6.5, 1.6), (-7.5, 1.5, 1.2), (12.5, 5.5, 1.3), (-4.0, -8.0, 1.0), (4.0, 22, 1.4), (-22, -9.5, 1.5)]):
    C.mancha(GELO, (x, y), rr, seed=20 + i, irregular=.45, z=.012, nome="gelo_negro")

C.chao(mat_chao_geada(3.0), 160)
C.render(OUT, centro=(-2, 2), largura=54, W=960 if Q else 1920, H=540 if Q else 1080, samples=16 if Q else 96)
