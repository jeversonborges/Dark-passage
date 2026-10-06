# Vinheta da Cratera de Absinto (nível 80 a 100, 3ª trombeta): o lugar onde a estrela caiu.
# Regra Lorencia: um chão só (vidro verde-escuro rachado em placas, em anfiteatro), dois destaques
# do mesmo vidro em outro estado (cristal vivo e pó do Amargo), vocabulário curto repetido e
# UM marco: o Coração da Estrela no fundo da cratera. Sobreviventes: a Escavação da Vigília na borda.
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector, noise as MN
import cena as C
from cena import por
K = C.K; A = C.A
from kit import box, cyl, sphere, along, torus, displace, crumble, candle, chain, point, N, L, ramp, mix, math_
Q = os.environ.get("Q") == "1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "cratera_de_absinto")

# ------------------------------------------------------------- coordenadas
# a = direita da tela, b = "para dentro" da tela (no chão)
S2 = math.sqrt(2)
def P(a, b): return ((a - b)/S2, (a + b)/S2)
CA, CB = 0.0, 18.0                  # centro da cratera (onde está o Coração)
CX, CY = P(CA, CB)
R, D = 30.0, 7.0                    # raio e profundidade do anfiteatro
QT = 1.1                            # altura de cada degrau (bancada)

def ss(t): t = max(0., min(1., t)); return t*t*(3 - 2*t)
def h(x, y):
    r = math.hypot(x - CX, y - CY); t = r/R
    z = 0.0
    if t < 1:
        base = -D*(1 - t*t)**1.25
        s = -base/QT; k = math.floor(s); f = s - k
        zt = -QT*(k + ss((f - .7)/.3))
        ang = math.atan2(y - CY, x - CX)
        terr = .55 + .4*max(0, math.cos(ang - math.atan2(*reversed(P(1, -.4)))))   # mais degraus no lado da escavação
        z = base*(1 - terr) + zt*terr
    z += 1.3*math.exp(-((r - R)/3.5)**2)                       # beiço da cratera
    z += 1.6*math.exp(-(r/4.5)**2)                             # monte de vidro sob o Coração
    z += .35*MN.noise(Vector((x/7, y/7, .3))) + .12*MN.noise(Vector((x/2.2, y/2.2, 4.1)))
    return z

# ------------------------------------------------------------- materiais
_MC = {}
def memo(fn):
    def w(*a):
        k = (fn.__name__,) + a
        if k not in _MC: _MC[k] = fn(*a)
        return _MC[k]
    return w

def vm(nt, op, a, b):
    n = N(nt, "ShaderNodeVectorMath", operation=op)
    for src, i in ((a, 0), (b, 1)):
        if isinstance(src, tuple): n.inputs[i].default_value = src
        else: L(nt, src, n.inputs[i])
    return n.outputs["Value"] if op in ('DISTANCE', 'LENGTH', 'DOT_PRODUCT') else n.outputs[0]

@memo
def mat_vidro_chao():
    """Vidro verde quase preto, rachado em placas; as rachaduras brilham mais perto do Coração
    e pulsam em anéis; manchas de pó do Amargo assentado."""
    m, nt, b = K.new_mat("vidro_cratera")
    v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
    n = K.noise(nt, v, None, .12, 6, .55, 2.0)
    pl = K.voronoi(nt, v, None, .85, 'F1', 5.0)
    ed = K.voronoi(nt, v, None, .85, 'DISTANCE_TO_EDGE', 5.0)
    ed2 = K.voronoi(nt, v, None, 2.6, 'DISTANCE_TO_EDGE', 9.0)
    cr = ramp(nt, [(0, (0, 0, 0)), (.022, (1, 1, 1))]); L(nt, ed.outputs["Distance"], cr.inputs[0])
    cr2 = ramp(nt, [(0, (.45, .45, .45)), (.012, (1, 1, 1))]); L(nt, ed2.outputs["Distance"], cr2.inputs[0])
    sep = N(nt, "ShaderNodeSeparateColor"); L(nt, pl.outputs["Color"], sep.inputs[0])
    base = ramp(nt, [(.0, (.006, .011, .008)), (.55, (.018, .034, .022)), (1, (.045, .06, .05))]); L(nt, math_(nt, 'ADD', math_(nt, 'MULTIPLY', sep.outputs[0], .6), math_(nt, 'MULTIPLY', n.outputs["Fac"], .5)), base.inputs[0])
    col = mix(nt, base.outputs[0], cr.outputs[0], 1, 'MULTIPLY')
    col = mix(nt, col, cr2.outputs[0], 1, 'MULTIPLY')
    # pó do Amargo (destaque 2): manchas foscas verde-acinzentadas
    dn = K.noise(nt, v, None, .35, 5, .6, 31.0)
    dr = ramp(nt, [(.52, (0, 0, 0)), (.62, (1, 1, 1))]); L(nt, dn.outputs["Fac"], dr.inputs[0])
    col = mix(nt, col, (.07, .11, .055), math_(nt, 'MULTIPLY', dr.outputs[0], .85))
    L(nt, col, b.inputs["Base Color"])
    rough = math_(nt, 'ADD', math_(nt, 'MULTIPLY', sep.outputs[1], .18), .05)
    L(nt, math_(nt, 'ADD', rough, math_(nt, 'MULTIPLY', dr.outputs[0], .7)), b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = .7
    # brilho das rachaduras: perto do centro + anéis de pulsação
    dist = vm(nt, 'DISTANCE', v, (CX, CY, -5.0))
    prox = ramp(nt, [(.0, (1, 1, 1)), (.12, (.6, .6, .6)), (.4, (.08, .08, .08)), (.8, (.01, .01, .01))]); L(nt, math_(nt, 'DIVIDE', dist, 42.0), prox.inputs[0])
    wave = math_(nt, 'SINE', math_(nt, 'MULTIPLY', dist, .55))
    wr = ramp(nt, [(.45, (.35, .35, .35)), (.92, (1.6, 1.6, 1.6))]); L(nt, math_(nt, 'ADD', math_(nt, 'MULTIPLY', wave, .5), .5), wr.inputs[0])
    crack = math_(nt, 'SUBTRACT', 1.0, cr.outputs[0])
    crack = math_(nt, 'ADD', crack, math_(nt, 'MULTIPLY', math_(nt, 'SUBTRACT', 1.0, cr2.outputs[0]), .5))
    em = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', crack, prox.outputs[0]), wr.outputs[0])
    em = math_(nt, 'ADD', math_(nt, 'MULTIPLY', em, 2.4), math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', dr.outputs[0], prox.outputs[0]), .12))
    b.inputs["Emission Color"].default_value = (.35, 1, .12, 1)
    L(nt, em, b.inputs["Emission Strength"])
    K.bump(nt, b, math_(nt, 'ADD', cr.outputs[0], math_(nt, 'MULTIPLY', sep.outputs[2], .6)), .45, .04)
    return m

@memo
def mat_cristal(nome, forca, tom=(.03, .16, .04)):
    m, nt, b = K.new_mat(nome)
    g = N(nt, "ShaderNodeTexCoord").outputs["Generated"]
    sz = N(nt, "ShaderNodeSeparateXYZ"); L(nt, g, sz.inputs[0])
    lw = N(nt, "ShaderNodeLayerWeight"); lw.inputs[0].default_value = .35
    nz = K.noise(nt, N(nt, "ShaderNodeTexCoord").outputs["Object"], None, 3.0, 4, .5, 3.0)
    b.inputs["Base Color"].default_value = (*tom, 1); b.inputs["Roughness"].default_value = .06
    b.inputs["Coat Weight"].default_value = 1.0
    b.inputs["Emission Color"].default_value = (.1, 1, .05, 1)
    f = math_(nt, 'ADD', .25, math_(nt, 'MULTIPLY', sz.outputs[2], .9))
    f = math_(nt, 'MULTIPLY', f, math_(nt, 'ADD', .45, math_(nt, 'MULTIPLY', lw.outputs["Facing"], 1.1)))
    f = math_(nt, 'MULTIPLY', f, math_(nt, 'ADD', .6, math_(nt, 'MULTIPLY', nz.outputs["Fac"], .8)))
    L(nt, math_(nt, 'MULTIPLY', f, forca), b.inputs["Emission Strength"])
    return m

@memo
def mat_rocha_vit():
    """Rocha vitrificada: preta-esverdeada, brilho prateado, veios verdes."""
    m, nt, b = K.new_mat("rocha_vitrificada")
    v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
    n = K.noise(nt, v, None, 2.2, 7, .6, 4.0)
    r = ramp(nt, [(.3, (.008, .012, .01)), (.6, (.03, .04, .034)), (.8, (.09, .1, .095))]); L(nt, n.outputs["Fac"], r.inputs[0])
    vo = K.voronoi(nt, v, None, 2.0, 'DISTANCE_TO_EDGE', 1.0)
    cr = ramp(nt, [(0, (1, 1, 1)), (.03, (0, 0, 0))]); L(nt, vo.outputs["Distance"], cr.inputs[0])
    col = K.grime(nt, r.outputs[0], v, None, 1.6, .5)
    L(nt, col, b.inputs["Base Color"]); b.inputs["Metallic"].default_value = .45
    L(nt, math_(nt, 'ADD', .12, math_(nt, 'MULTIPLY', n.outputs["Fac"], .3)), b.inputs["Roughness"])
    b.inputs["Emission Color"].default_value = (.35, 1, .12, 1)
    L(nt, math_(nt, 'MULTIPLY', cr.outputs[0], 2.5), b.inputs["Emission Strength"])
    K.bump(nt, b, math_(nt, 'ADD', n.outputs["Fac"], cr.outputs[0]), .5, .03)
    return m

@memo
def mat_chumbo(seed):
    return K.mat_metal(f"chumbo{seed}", (.085 + .02*seed, .092 + .02*seed, .1 + .02*seed), .18, float(seed)*3 + 1, .5)

@memo
def mat_estrada():
    """Estrada dos Peregrinos: pó do Amargo pisado, mais claro e fosco, com pegadas."""
    m, nt, b = K.new_mat("estrada_peregrinos")
    v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
    n = K.noise(nt, v, None, .8, 6, .6, 8.0); n2 = K.noise(nt, v, None, 9, 3, .5, 9.0)
    r = ramp(nt, [(.3, (.035, .05, .035)), (.65, (.085, .11, .075)), (.85, (.13, .15, .11))]); L(nt, n.outputs["Fac"], r.inputs[0])
    col = mix(nt, r.outputs[0], n2.outputs["Color"], .2, 'OVERLAY')
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .9
    b.inputs["Emission Color"].default_value = (.35, 1, .12, 1)
    vr = ramp(nt, [(.7, (0, 0, 0)), (.75, (.25, .25, .25))]); L(nt, n2.outputs["Fac"], vr.inputs[0])
    L(nt, vr.outputs[0], b.inputs["Emission Strength"])
    K.bump(nt, b, n2.outputs["Fac"], .4, .03)
    return m

# ------------------------------------------------------------- modelos
def prisma(mat, a, d, Lc, rad):
    a = Vector(a); d = Vector(d).normalized()
    bpt = a + d*Lc*.78; tip = a + d*Lc
    along(mat, a, bpt, rad, verts=6); along(mat, bpt, tip, rad, r2=0.0, verts=6)

def cristal(seed, n=7, H=1.6, forca=7.0, rochas=2):
    def fn(m):
        r = random.Random(seed)
        mats = [mat_cristal("cristal", forca), mat_cristal("cristal_escuro", forca*.35, (.01, .05, .02))]
        for k in range(n):
            az = r.uniform(0, 6.28); tl = math.radians(r.uniform(0, 12) if k == 0 else r.uniform(15, 55))
            Lc = H*(1 if k == 0 else r.uniform(.3, .8))
            a = (r.uniform(-.25, .25)*H*.4, r.uniform(-.25, .25)*H*.4, -.15)
            prisma(mats[0] if r.random() < .75 else mats[1], a, (math.sin(tl)*math.cos(az), math.sin(tl)*math.sin(az), math.cos(tl)), Lc, Lc*.11 + .03)
        for k in range(rochas):
            o = sphere(mat_rocha_vit(), (r.uniform(-.5, .5)*H*.4, r.uniform(-.5, .5)*H*.4, .05), (H*.22, H*.18, H*.12), segs=10)
            crumble(o, .06*H, seed + k)
    return fn

def rocha(seed, s=1.0):
    def fn(m):
        r = random.Random(seed)
        o = sphere(mat_rocha_vit(), (0, 0, .2*s), (s*r.uniform(.7, 1.1), s*r.uniform(.5, .9), s*r.uniform(.35, .6)), segs=12)
        crumble(o, .22*s, seed); displace(o, .06*s, .12, seed + 9, 1)
        if r.random() < .6:
            o = sphere(mat_rocha_vit(), (s*.8, s*.3, .1*s), (s*.4, s*.35, s*.25), segs=10); crumble(o, .1*s, seed + 3)
    return fn

def coracao(m):
    """O Coração da Estrela: prisma colossal pulsante sobre um monte de vidro, estilhaços em volta
    e fragmentos flutuando como se ainda caíssem."""
    r = random.Random(7)
    core = mat_cristal("coracao", 9.0, (.08, .4, .06)); cri = mat_cristal("cristal_grande", 4.5)
    esc = mat_cristal("cristal_escuro", 1.0, (.01, .05, .02))
    o = sphere(mat_rocha_vit(), (0, 0, -.6), (5.5, 5.0, 1.8), segs=24); crumble(o, .6, 3)
    prisma(core, (0, 0, -1.0), (.08, .05, 1), 13.0, 1.35)
    prisma(core, (.6, -.4, -.5), (.35, -.25, 1), 8.0, .8)
    for k in range(9):
        az = k*2*math.pi/9 + r.uniform(-.2, .2); tl = math.radians(r.uniform(28, 58))
        Lc = r.uniform(3.0, 7.0); rr = r.uniform(1.0, 2.2)
        prisma(cri if k % 3 else esc, (math.cos(az)*rr, math.sin(az)*rr, -.4), (math.sin(tl)*math.cos(az), math.sin(tl)*math.sin(az), math.cos(tl)), Lc, Lc*.12)
    for k in range(34):
        az = r.uniform(0, 6.28); rr = r.uniform(2.5, 6.5); tl = math.radians(r.uniform(20, 70)); Lc = r.uniform(.6, 2.2)
        prisma(cri if r.random() < .7 else esc, (math.cos(az)*rr, math.sin(az)*rr, -.3), (math.sin(tl)*math.cos(az), math.sin(tl)*math.sin(az), math.cos(tl)), Lc, Lc*.12)
    for k in range(16):   # fragmentos suspensos
        az = r.uniform(0, 6.28); rr = r.uniform(2.2, 6.0); z = r.uniform(4, 13); Lc = r.uniform(.4, 1.3)
        d = Vector((r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(-1, 1))).normalized()
        c = Vector((math.cos(az)*rr, math.sin(az)*rr, z))
        prisma(cri, c - d*Lc*.5, d, Lc, Lc*.13); prisma(cri, c - d*Lc*.45, -d, Lc*.5, Lc*.13)
    point((0, 0, 7.0), (.3, 1, .2), 14000, 2.5, "coracao_luz")
    point((0, -3, 1.5), (.35, 1, .25), 1500, 1.0, "coracao_luz2")

def andaime(seed):
    def fn(m):
        r = random.Random(seed); W, Dd, nb = 4.2, 1.3, 3
        wd, ir = m["wood_d"], m["iron"]
        xs = [-W/2 + i*W/nb for i in range(nb + 1)]
        for x in xs:
            for y in (0, Dd): along(wd, (x, y, -.3), (x + r.uniform(-.04, .04), y, 4.0), .05, verts=6)
        for z in (1.5, 3.0, 3.9):
            for y in (0, Dd): along(wd, (-W/2 - .1, y, z), (W/2 + .1, y, z), .04, verts=6)
            for x in xs: along(wd, (x, -.05, z), (x, Dd + .05, z), .035, verts=6)
        for i in range(nb):
            along(wd, (xs[i], -.04, .1), (xs[i + 1], -.04, 1.5), .03, verts=5)
            along(wd, (xs[i + 1], -.04, 1.5), (xs[i], -.04, 3.0), .03, verts=5)
        for z in (1.5, 3.0):
            for k in range(5):
                box(m["wood"], (r.uniform(-.05, .05), .13 + k*.26, z + .06), (W + .2, .24, .04), (0, 0, r.uniform(-1, 1)), .005)
        for k in range(9): box(m["wood"], (W/2 + .25, .6, .2 + k*.4), (.05, .5, .05), bevel=.005)
        for y in (.35, .85): cyl(m["wood"], (W/2 + .25, y, 1.9), .025, 3.8, verts=6)
        for x in xs:
            for z in (1.5, 3.0): box(ir, (x, 0, z), (.1, .1, .1), bevel=.005)
        # carga: caixa e saco no andaime, lampião pendurado
        box(m["wood"], (-1.2, .6, 1.8), (.5, .5, .5), (0, 0, 12), .02); sphere(m["sack"], (.6, .7, 3.2), (.25, .2, .18))
        along(ir, (xs[1], -.05, 3.9), (xs[1], -.5, 3.9), .015, verts=4)
        cyl(m["brass"], (xs[1], -.5, 3.55), .08, .22, verts=8)
        sphere(K.mat_emit("lanterna", (1, .6, .25), 10), (xs[1], -.5, 3.55), (.06, .06, .09), segs=8)
        point((xs[1], -.6, 3.5), (1, .55, .2), 70, .08)
        chain(ir, (xs[2], -.05, 3.9), (xs[2] + .3, -.4, 2.5), 8, .03)
    return fn

def guindaste(m):
    """Guindaste de mineração: torre de madeira com roda de polia, lança sobre a fenda e caçamba de cristal."""
    wd, ir = m["wood_d"], m["iron"]; Ht = 7.5
    for sx in (-1, 1):
        for sy in (-1, 1): along(wd, (sx*1.4, sy*1.4, -.3), (sx*.5, sy*.5, Ht), .1, verts=6)
    for z in (1.8, 3.6, 5.4):
        k = 1.4 - .9*z/Ht
        for sx in (-1, 1):
            along(wd, (sx*k, -k, z), (sx*k, k, z), .05, verts=6); along(wd, (-k, sx*k, z), (k, sx*k, z), .05, verts=6)
            along(wd, (sx*k, -k, z), (sx*(k - .17), k - .17, z + 1.8), .035, verts=5)
    along(wd, (0, 3.2, -.3), (0, .5, Ht - .4), .09, verts=6)      # escora de trás
    box(wd, (0, 0, Ht + .1), (1.4, 1.4, .2), bevel=.01)
    along(wd, (0, 0, Ht + .2), (0, -4.2, Ht + 1.1), .11, verts=6)  # lança
    along(ir, (0, .6, Ht + .2), (0, -4.2, Ht + 1.1), .02, verts=4)
    for (y, z, R0) in [(0, Ht + .9, .85), (-4.1, Ht + .9, .45)]:
        torus(ir, (0, y, z), R0, .05, (0, 90, 0))
        for k in range(6):
            a = k*math.pi/3; along(ir, (0, y, z), (0, y + math.cos(a)*R0, z + math.sin(a)*R0), .02, verts=4)
    along(K.mat_solid("cabo", (.04, .035, .03), .3, .6), (0, -4.5, Ht + .9), (0, -4.5, 2.4), .02, verts=4)
    along(K.mat_solid("cabo", (.04, .035, .03), .3, .6), (0, .8, Ht + .9), (0, 1.8, 1.1), .02, verts=4)
    c = cyl(m["rust"], (0, -4.5, 1.9), .5, .9, verts=12, r2=.38)
    torus(ir, (0, -4.5, 2.35), .5, .04)
    for k in range(7):
        a = k*.9; prisma(mat_cristal("cristal", 3.0), (math.cos(a)*.25, -4.5 + math.sin(a)*.25, 2.0), (math.cos(a)*.3, math.sin(a)*.3, 1), .8, .08)
    # guincho
    box(m["wood"], (0, 2.3, .2), (1.6, 1.4, .4), bevel=.02)
    cyl(m["iron"], (0, 2.0, .9), .35, 1.2, (0, 90, 0), 14)
    for sx in (-1, 1): box(m["wood"], (sx*.7, 2.0, .6), (.12, .3, .9), bevel=.01)
    along(ir, (.75, 2.0, .9), (.95, 2.0, 1.3), .03, verts=5)
    # lampião no alto
    cyl(m["brass"], (.75, -.75, Ht - .2), .09, .25, verts=8)
    sphere(K.mat_emit("lanterna", (1, .6, .25), 12), (.75, -.75, Ht - .2), (.07, .07, .1), segs=8)
    point((.8, -.85, Ht - .3), (1, .55, .2), 160, .1)

def vagonete(seed, cheio=True):
    def fn(m):
        r = random.Random(seed); ir, ru = m["iron"], m["rust"]
        for sx in (-1, 1):
            for sy in (-1, 1): cyl(ir, (sx*.38, sy*.3, .16), .15, .06, (90, 0, 0), 12)
        for sx in (-1, 1): along(ir, (sx*.38, -.33, .16), (sx*.38, .33, .16), .025, verts=5)
        box(ru, (0, 0, .34), (.95, .6, .08), bevel=.01)
        for sy in (-1, 1): box(ru, (0, sy*.38, .62), (1.1, .05, .52), (sy*-10, 0, 0), .01)
        for sx in (-1, 1): box(ru, (sx*.52, 0, .62), (.05, .78, .52), (0, sx*10, 0), .01)
        for sx in (-1, 1): box(ir, (sx*.3, 0, .9), (.06, .86, .04), bevel=.004)
        if cheio:
            for k in range(6):
                o = sphere(mat_rocha_vit(), (r.uniform(-.3, .3), r.uniform(-.2, .2), .8), (.18, .15, .12), segs=8); crumble(o, .04, seed + k)
            for k in range(6):
                a = r.uniform(0, 6.28); prisma(mat_cristal("cristal", 3.0), (r.uniform(-.3, .3), r.uniform(-.15, .15), .75), (math.cos(a)*.4, math.sin(a)*.4, 1), r.uniform(.3, .55), .05)
    return fn

def barraca_chumbo(seed):
    def fn(m):
        r = random.Random(seed); W, Dd, H = 3.4, 2.6, 2.2
        cs = [mat_chumbo(0), mat_chumbo(1), mat_chumbo(2)]
        for sy in (-1, 1):   # paredes de frente e fundos, com vão de porta na frente
            x = -W/2 + .4
            while x < W/2 - .3:
                if not (sy < 0 and abs(x - .5) < .45):
                    hh = H - .25 + (x + W/2)*.08*(1 if sy > 0 else .4)
                    box(r.choice(cs), (x, sy*Dd/2, hh/2), (.82, .035, hh), (r.uniform(-2, 2), 0, r.uniform(-2, 2)), .004)
                x += .78
        for sx in (-1, 1):
            y = -Dd/2 + .4
            while y < Dd/2 - .3:
                box(r.choice(cs), (sx*W/2, y, H/2 - .05), (.035, .82, H - .1), (0, r.uniform(-2, 2), 0), .004); y += .78
        for k in range(6):   # telhado de uma água, chapas sobrepostas
            box(r.choice(cs), (-W/2 - .2 + k*.66, 0, H + .05), (.7, Dd + .7, .03), (r.uniform(-6, -3), r.uniform(-2, 2), 0), .003)
        for x in (-W/2 + .1, W/2 - .1):
            for y in (-Dd/2 + .1, Dd/2 - .1): along(m["wood_d"], (x, y, 0), (x, y, H + .1), .05, verts=6)
        for k in range(10): box(m["iron"], (-W/2 + .3*k + .2, -Dd/2 - .03, H - .35), (.03, .01, .03), bevel=0)
        # dentro aceso
        box(K.mat_window_lit(), (.5, -Dd/2 + .25, .9), (.8, .04, 1.8), bevel=0)
        point((.5, -Dd/2 + .6, 1.2), (1, .5, .18), 120, .2)
        point((.5, -Dd/2 - .6, 1.0), (1, .5, .18), 50, .3)
        cyl(m["iron"], (-W/2 + .6, Dd/2 - .5, H + .7), .1, 1.6, verts=10)
        cyl(m["iron"], (-W/2 + .6, Dd/2 - .5, H + 1.55), .2, .12, verts=10, r2=.05)
        # placa de radiação pintada
        cyl(K.mat_solid("placa_amarela", (.25, .19, .03), .3, .5), (-.9, -Dd/2 - .04, 1.4), .28, .02, (90, 0, 0), 3)
        cyl(K.mat_solid("simbolo", (.015, .012, .01)), (-.9, -Dd/2 - .06, 1.38), .09, .01, (90, 0, 0), 3)
        for k in range(4):
            o = sphere(m["sack"], (-W/2 + .5 + k*.42, -Dd/2 - .25, .1), (.2, .14, .1)); displace(o, .02, .2, seed + k, 1)
        box(r.choice(cs), (W/2 + .25, -.3, .55), (.05, .9, 1.1), (0, 18, 0), .004)
    return fn

def contador(m):
    """Contador de radiação da Vigília: caixa de latão num tripé, mostrador aceso e sonda no cabo."""
    for k in range(3):
        a = k*2.094; along(m["iron"], (math.cos(a)*.45, math.sin(a)*.45, 0), (0, 0, 1.1), .02, verts=5)
    box(m["brass"], (0, 0, 1.25), (.42, .28, .32), bevel=.02)
    cyl(K.mat_emit("mostrador", (.75, 1, .5), 3.5), (0, -.145, 1.28), .1, .02, (90, 0, 0), 16)
    along(K.mat_solid("agulha", (.02, .02, .02)), (0, -.16, 1.24), (.06, -.16, 1.34), .006, verts=4)
    sphere(K.mat_emit("lampada_alerta", (1, .35, .05), 14), (.15, -.1, 1.45), (.035, .035, .035), segs=8)
    along(m["iron"], (.12, 0, 1.42), (.12, 0, 1.9), .006, verts=4)
    along(K.mat_solid("cabo", (.04, .035, .03), .3, .6), (-.2, 0, 1.15), (-.5, -.3, .05), .012, verts=4)
    cyl(m["brass"], (-.6, -.35, .05), .035, .3, (90, 0, 40), 8)
    point((0, -.4, 1.3), (.7, 1, .4), 4, .05)

def altar(seed):
    def fn(m):
        r = random.Random(seed)
        for k in range(4):
            o = sphere(mat_rocha_vit(), (r.uniform(-.1, .1), r.uniform(-.1, .1), .15 + k*.22), (.42 - k*.08, .36 - k*.07, .14), segs=10); crumble(o, .04, seed + k)
        prisma(mat_cristal("cristal", 3.0), (0, 0, .85), (.05, .05, 1), .55, .07)
        # estrela de ferro dos romeiros num poste
        along(m["wood_d"], (-.55, .25, 0), (-.55, .25, 1.9), .03, verts=6)
        for k in range(4):
            a = k*math.pi/4; along(m["iron"], (-.55 - math.cos(a)*.22, .25, 1.95 - math.sin(a)*.22), (-.55 + math.cos(a)*.22, .25, 1.95 + math.sin(a)*.22), .012, verts=4)
        for k in range(3):
            o = box(K.mat_cloth("fita_peregrino", (.13, .12, .1), 61.0), (-.5 + k*.04, .27, 1.5 - k*.05), (.05, .01, .45 + k*.1), (0, r.uniform(-12, 12), 0), 0)
        for k in range(9):
            a = r.uniform(0, 6.28); rr = r.uniform(.4, .7)
            candle((math.cos(a)*rr, math.sin(a)*rr, 0), r.uniform(.06, .2), light=(k % 3 == 0))
        for k in range(3):
            cyl(K.mat_solid("cuia", (.06, .045, .03), 0, .7), (r.uniform(-.4, .4), -.5, .04), .07, .08, verts=10, r2=.05)
        point((0, -.3, .4), (1, .55, .2), 14, .2)
    return fn

def ossada(seed):
    def fn(m):
        r = random.Random(seed); b = m["bone"]
        sphere(b, (0, .45, .08), (.08, .1, .085), segs=10)
        along(b, (0, .35, .05), (0, -.2, .05), .02, verts=5)
        A.ossos_costela(b, (0, .15, .05), 5, .3, .12, seed)
        for sx in (-1, 1):
            along(b, (sx*.1, -.2, .04), (sx*.15 + r.uniform(-.1, .1), -.7, .03), .018, verts=5)
            along(b, (sx*.15, .3, .04), (sx*.4, .2 + r.uniform(-.2, .2), .03), .014, verts=5)
        o = box(K.mat_cloth("manto_peregrino", (.1, .095, .08), 62.0), (.05, -.1, .06), (.6, .9, .05), (0, 0, r.uniform(-15, 15)), 0); displace(o, .06, .15, seed, 3)
        along(m["wood_d"], (-.5, -.6, .03), (.4, 1.0, .03), .025, verts=5)
        if r.random() < .6:
            prisma(mat_cristal("cristal", 2.5), (.0, .1, .05), (.2, .1, 1), .35, .05)   # o cristal brotando do peito
    return fn

def trilho(pts, folga=.45, suporte=True):
    """Trilho de mina ao longo de pontos (a,b); z = rampa linear acima do chão, com cavaletes."""
    m = C.mats(); W = [P(a, b) for a, b in pts]
    z0, z1 = h(*W[0]) + folga, h(*W[-1]) + folga
    tot = sum((Vector(W[i + 1]) - Vector(W[i])).length for i in range(len(W) - 1))
    s = 0.0; seg = []
    for i in range(len(W) - 1):
        p, q = Vector(W[i]), Vector(W[i + 1]); Lg = (q - p).length; n = max(1, int(Lg/.65))
        for k in range(n):
            t0 = (s + Lg*k/n)/tot; pp = p.lerp(q, k/n)
            seg.append((pp, z0 + (z1 - z0)*t0, (q - p).normalized()))
        s += Lg
    seg.append((Vector(W[-1]), z1, (Vector(W[-1]) - Vector(W[-2])).normalized()))
    for i, (p, z, d) in enumerate(seg):
        nrm = Vector((-d.y, d.x))
        a = p - nrm*.6; bq = p + nrm*.6
        along(m["wood_d"], (a.x, a.y, z), (bq.x, bq.y, z), .06, verts=4)
        if suporte and i % 3 == 0 and z - h(p.x, p.y) > .25:
            for sg in (-1, 1):
                c = p + nrm*.45*sg; along(m["wood_d"], (c.x, c.y, z), (c.x, c.y, h(c.x, c.y) - .2), .05, verts=5)
        if i:
            p0, zp, _ = seg[i - 1]
            for sg in (-1, 1):
                along(m["iron"], (p0.x + nrm.x*.36*sg, p0.y + nrm.y*.36*sg, zp + .07), (p.x + nrm.x*.36*sg, p.y + nrm.y*.36*sg, z + .07), .03, verts=5)
    return z0, z1

def estrada(pts, larg=2.4):
    """Faixa que segue o relevo (a Estrada dos Peregrinos)."""
    W = [Vector(P(a, b)) for a, b in pts]
    dens = []
    for i in range(len(W) - 1):
        n = max(1, int((W[i + 1] - W[i]).length/.4))
        for k in range(n): dens.append(W[i].lerp(W[i + 1], k/n))
    dens.append(W[-1])
    vs, fs = [], []; cols = 5
    for i, p in enumerate(dens):
        d = (dens[min(i + 1, len(dens) - 1)] - dens[max(i - 1, 0)]).normalized(); nrm = Vector((-d.y, d.x))
        w = larg*(1 + .25*math.sin(i*.37))
        for c in range(cols):
            q = p + nrm*w*(c/(cols - 1) - .5); vs.append((q.x, q.y, h(q.x, q.y) + .05))
        if i:
            for c in range(cols - 1): fs.append(((i - 1)*cols + c, (i - 1)*cols + c + 1, i*cols + c + 1, i*cols + c))
    me = bpy.data.meshes.new("estrada"); me.from_pydata(vs, [], fs); me.update()
    for pg in me.polygons: pg.use_smooth = True
    o = bpy.data.objects.new("_estrada", me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(mat_estrada())
    return dens

def chao_cratera():
    a0, a1, b0, b1, st = -38, 38, -40, 58, .3
    na, nb = int((a1 - a0)/st) + 1, int((b1 - b0)/st) + 1
    vs = []
    for j in range(nb):
        for i in range(na):
            x, y = P(a0 + i*st, b0 + j*st); vs.append((x, y, h(x, y)))
    fs = [(j*na + i, j*na + i + 1, (j + 1)*na + i + 1, (j + 1)*na + i) for j in range(nb - 1) for i in range(na - 1)]
    me = bpy.data.meshes.new("cratera"); me.from_pydata(vs, [], fs); me.update()
    for pg in me.polygons: pg.use_smooth = True
    o = bpy.data.objects.new("_chao", me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(mat_vidro_chao())
    return o

def g(fn, a, b, rot=0.0, s=1.0, chave=None, dz=0.0):
    x, y = P(a, b); return C.grupo(fn, x, y, rot, s, h(x, y) + dz, chave=chave)
def k_(nome, a, b, rot=0.0, s=1.0, dz=0.0):
    x, y = P(a, b); return por(nome, x, y, rot, s, h(x, y) + dz)
def ang_radial(a, b):   # rotação (graus) que vira o eixo +Y do modelo para o centro
    x, y = P(a, b); return math.degrees(math.atan2(CY - y, CX - x)) - 90

# ------------------------------------------------------------- cena
C.iniciar(ceu=(.006, .011, .008), poeira=(.06, .11, .045), luzes=False)
C.sol((.72, .8, .82), 2.2, (52, 0, -40), .05, "lua")
C.sol((.3, 1, .35), .35, (-55, 0, 165), .1, "contraluz")
C.sol((.3, .34, .36), .25, (70, 0, 110), .2, "fill")
r = random.Random(23)

# marco
g(coracao, CA, CB, 0, 1, "coracao", dz=-.4)

# Estrada dos Peregrinos: desce da borda esquerda até o Coração
ESTR = [(-24, -36), (-20, -26), (-15, -16), (-11, -7), (-9, 0), (-7.5, 6), (-5, 10.5), (-2.8, 13.5)]
estrada(ESTR)
def perto_estrada(a, b, d=2.2):
    best = 1e9
    for (a0, b0), (a1, b1) in zip(ESTR, ESTR[1:]):
        dx, dy = a1 - a0, b1 - b0; t = max(0, min(1, ((a - a0)*dx + (b - b0)*dy)/(dx*dx + dy*dy)))
        best = min(best, math.hypot(a - a0 - t*dx, b - b0 - t*dy))
    return best < d
for i, (a, b, lado) in enumerate([(-20.5, -29, 1), (-16.5, -19, -1), (-12.2, -9.5, 1), (-9.6, -1.5, -1), (-7.7, 5.5, 1)]):
    g(altar(40 + i % 3), a + 2.0*lado, b - .6*lado, r.uniform(0, 360), 1, f"altar{i % 3}")
for i, (a, b) in enumerate([(-18.5, -22), (-14.6, -13.5), (-12.9, -11), (-10, -3.5), (-8.8, 2.5), (-6.5, 8), (-4.6, 11.4), (-22.5, -32), (-11, -6)]):
    g(ossada(60 + i % 4), a + r.uniform(-1.8, 1.8), b, r.uniform(0, 360), 1, f"ossada{i % 4}")
for (a, b) in [(-21.5, -30), (-17.5, -21), (-13.2, -12.5), (-8.0, 2.5)]:
    k_("lanterna_procissao", a - 1.6, b + .5, r.uniform(0, 360))
k_("estandarte_rasgado", -19, -24.5, 30)
k_("placa_radiacao", -22.5, -33, 20); k_("placa_radiacao", -13.4, -16.8, -10)

# Escavação da Vigília: guindaste na borda direita, andaimes nos degraus, trilho descendo
g(guindaste, 10.5, -9.5, ang_radial(10.5, -9.5) + 180, 1, "guindaste", dz=-.2)
for i, (a, b) in enumerate([(14, -2), (7.5, -1.5), (17.5, 4.5), (11.5, 6.5)]):
    g(andaime(80 + i % 2), a, b, ang_radial(a, b) + 180, 1, f"andaime{i % 2}", dz=-.15)
RAIL = [(16, -24), (15.5, -16), (13.5, -8), (10.5, 0), (7, 7.5)]
z0, z1 = trilho(RAIL)
def em_trilho(t):
    W = [Vector(P(a, b)) for a, b in RAIL]
    tot = sum((W[i + 1] - W[i]).length for i in range(len(W) - 1)); s = t*tot
    for i in range(len(W) - 1):
        Lg = (W[i + 1] - W[i]).length
        if s <= Lg or i == len(W) - 2:
            p = W[i].lerp(W[i + 1], min(1, s/Lg)); d = (W[i + 1] - W[i]).normalized(); break
        s -= Lg
    z = z0 + (z1 - z0)*t; pitch = math.atan2(z1 - z0, tot)
    return p, z, d, pitch
for i, t in enumerate([.2, .27, .55, .9]):
    p, z, d, pitch = em_trilho(t)
    e = C.grupo(vagonete(90 + i % 2, i != 1), p.x, p.y, 0, 1, z + .07, chave=f"vag{i % 2}{i != 1}")
    e.rotation_euler = (0, -pitch, math.atan2(d.y, d.x))
trilho([(19.5, -27), (19, -20), (18.5, -14)], .3, False)
# acampamento de chumbo no plano da borda
for i, (a, b, rt) in enumerate([(20.5, -30, 45), (24.5, -24, 60), (11, -27.5, 30)]):
    g(barraca_chumbo(100 + i), a, b, rt, 1, f"barraca{i}")
g(contador, 17.5, -21.5, 220, 1, "contador"); g(contador, 9.5, -6.2, 200, 1, "contador")
g(contador, -16, -18, 160, 1, "contador")
k_("tonel_fogo", 16.8, -28.5); k_("tonel_fogo", 22.5, -20)
k_("poste_gas", 13.5, -23.5, 10); k_("poste_gas", 17.5, -15.5, 60); k_("poste_gas", 23.8, -28.6, 0)
k_("caixas", 22, -26.5, 20); k_("caixas", 13.2, -12.8, 70); k_("barris", 12, -21, 0); k_("barris", 24.5, -20.5, 40)
k_("sacos_areia", 15, -26, 30); k_("sacos_areia", 11.5, -11.5, 120)
k_("placa_radiacao", 12.3, -14.5, 30); k_("placa_radiacao", 8.6, -8.3, 0); k_("placa_radiacao", 26, -31, 0)
k_("estandarte_rasgado", 19.5, -33, 0)
C.ponto((*P(17.5, -26), h(*P(17.5, -26)) + 2.5), (1, .5, .2), 600, 1.0)

# cristais: brotam do vidro, mais densos e maiores perto do Coração
VAR = [(1, 7, 1.1, 2.2), (2, 6, 1.6, 2.6), (3, 9, 2.1, 3.0), (4, 7, 2.9, 3.4), (5, 11, 3.8, 4.0)]
n_ok = 0
for k in range(900):
    a, b = r.uniform(-34, 34), r.uniform(-38, 46)
    rr = math.hypot(a - CA, b - CB)
    w = max(0, 1 - rr/(R + 8))**1.6 + .03
    if r.random() > w or rr < 6.5 or perto_estrada(a, b, 2.0): continue
    if 5 < a < 27 and -34 < b < -12: continue      # acampamento
    if 5 < a < 20 and -12 < b < 9 and r.random() < .7: continue   # escavação (pouco cristal: já minerado)
    near = 1 - min(1, rr/R)
    vi = min(4, max(0, int(near*4.2 + r.uniform(-.8, .8))))
    sd, n, H, f = VAR[vi]
    g(cristal(sd, n, H, f), a, b, r.uniform(0, 360), r.uniform(.8, 1.2), f"cris{vi}", dz=-.1)
    n_ok += 1
    if n_ok > 105: break
# veio exposto na escavação, sob o guindaste
for (a, b) in [(7.5, -7), (6.5, -5.2), (8.7, -5.5)]:
    g(cristal(3, 9, 1.8, 8.0), a, b, r.uniform(0, 360), 1.0, "cris2", dz=-.1)
# rocha vitrificada espalhada
for k in range(55):
    a, b = r.uniform(-34, 34), r.uniform(-38, 46)
    if perto_estrada(a, b, 1.8) or (8 < a < 27 and -34 < b < -12): continue
    g(rocha(200 + k % 5), a, b, r.uniform(0, 360), r.uniform(.6, 1.6), f"rocha{k % 5}", dz=-.15)

chao_cratera()
C.render(OUT, centro=P(0, 2), largura=56, W=960 if Q else 1920, H=540 if Q else 1080, samples=16 if Q else 96)
