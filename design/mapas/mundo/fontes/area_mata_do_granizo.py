# Vinheta da Mata do Granizo (nível 15 a 30, 1ª trombeta): floresta de troncos carbonizados
# que ficaram de pé, chão de cinza preta fofa com rachaduras de brasa, granizo de sangue que
# não derrete. Marco: a Árvore-Mãe (sequoia oca) com a vila dos carvoeiros em palafitas.
# Regra Lorencia: um chão (cinza), 2 destaques (brasa exposta, crosta de granizo), paleta
# carvão / cinza clara / vermelho sangue + laranja brasa, vocabulário repetido, um marco.
import sys, os, math, random
try:
    import bpy
except ImportError:
    bpy = None

def fumaca_baixa(base, saida, forca=.5, seed=5):
    """Passo fora do Blender (python3 area_mata_do_granizo.py fumaca): bancos de fumaça baixa,
    alongados na horizontal e acesos por baixo pela brasa. Gera <saida>_raw.png e _mist.png para o pos.py."""
    import numpy as np, shutil
    from PIL import Image, ImageFilter
    im = np.asarray(Image.open(base + "_raw.png").convert("RGB")).astype(np.float32)/255
    H, Wd, _ = im.shape
    mist = np.asarray(Image.open(base + "_mist.png").convert("L").resize((Wd, H))).astype(np.float32)/255
    rng = np.random.default_rng(seed)
    n = np.zeros((H, Wd), np.float32); tot = 0
    for k, (gw, amp) in enumerate([(6, 1.0), (12, .55), (26, .3), (54, .15)]):
        gh = max(2, int(gw*H/Wd*2.6))
        g = (rng.random((gh, gw))*255).astype(np.uint8)
        up = np.asarray(Image.fromarray(g).resize((Wd, H), Image.BICUBIC)).astype(np.float32)/255
        n += up*amp; tot += amp
    n /= tot
    sm = np.clip((n - .45)*2.6, 0, 1)**1.4
    lum = im.max(axis=2)
    hot = np.clip(im - .35, 0, 1)
    glow = np.asarray(Image.fromarray((hot*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(Wd/40))).astype(np.float32)/255
    cor = np.array([.11, .075, .07]) + glow*np.array([2.2, 1.0, .45])
    a = (sm*forca*(.55 + .45*mist))[..., None]
    out = im*(1 - a) + cor*a
    Image.fromarray((np.clip(out, 0, 1)*255).astype(np.uint8)).save(saida + "_raw.png")
    shutil.copy(base + "_mist.png", saida + "_mist.png")
    print("fumaça ok", saida)

if bpy is None:
    _o = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "mata_do_granizo")
    fumaca_baixa(_o, _o + "_f", float(sys.argv[2]) if len(sys.argv) > 2 else .5)
    sys.exit(0)
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cena as C
import kit as K
from kit import N, L, ramp, mix, math_, noise, voronoi, box, cyl, sphere, along, torus, prism, point
Q = os.environ.get("Q") == "1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "mata_do_granizo")
SQ = 1 / math.sqrt(2)
FUMACA_VOL = False   # fumaça volumétrica fica cara demais na CPU compartilhada; a fumaça baixa vai no pós

def W(s, d):
    """Coordenada de tela (s = direita, d = fundo, em metros de chão) -> mundo (x, y)."""
    return ((s - d)*SQ, (s + d)*SQ)

# ================================================================ materiais
_MT = {}
def _c(key, fn):
    if key not in _MT: _MT[key] = fn()
    return _MT[key]

def casca(seed=0, brilho=1.0):
    """Casca carbonizada em placas (couro de jacaré), com brasa laranja viva nas fendas."""
    def f():
        m, nt, b = K.new_mat(f"casca_brasa_{seed}_{brilho}")
        tc = N(nt, "ShaderNodeTexCoord"); mp = N(nt, "ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (2.4, 2.4, .75); L(nt, tc.outputs["Object"], mp.inputs[0])
        v = mp.outputs[0]
        dn = noise(nt, v, None, 2.0, 4, .5, seed + 9)
        vd = N(nt, "ShaderNodeVectorMath", operation='ADD'); L(nt, v, vd.inputs[0])
        sc = N(nt, "ShaderNodeVectorMath", operation='SCALE'); L(nt, dn.outputs["Color"], sc.inputs[0]); sc.inputs["Scale"].default_value = .35
        L(nt, sc.outputs[0], vd.inputs[1]); v2 = vd.outputs[0]
        vo = voronoi(nt, v2, None, 2.6, 'DISTANCE_TO_EDGE', seed)
        crack = ramp(nt, [(0, (1, 1, 1)), (.07, (0, 0, 0))]); L(nt, vo.outputs["Distance"], crack.inputs[0])
        plate = ramp(nt, [(.05, (0, 0, 0)), (.35, (1, 1, 1))]); L(nt, vo.outputs["Distance"], plate.inputs[0])
        n = noise(nt, v, None, 3.5, 7, .62, seed + 1)
        base = ramp(nt, [(.3, (.006, .0055, .0055)), (.55, (.022, .02, .019)), (.8, (.07, .066, .062))]); L(nt, n.outputs["Fac"], base.inputs[0])
        col = mix(nt, base.outputs[0], (.11, .105, .1), math_(nt, 'MULTIPLY', plate.outputs[0], .25))
        # cinza clara assentada nas faces de cima
        geo = N(nt, "ShaderNodeNewGeometry"); ns = N(nt, "ShaderNodeSeparateXYZ"); L(nt, geo.outputs["Normal"], ns.inputs[0])
        up = ramp(nt, [(.45, (0, 0, 0)), (.8, (1, 1, 1))]); L(nt, ns.outputs[2], up.inputs[0])
        col = mix(nt, col, (.2, .19, .18), math_(nt, 'MULTIPLY', up.outputs[0], .8))
        col = mix(nt, col, (.002, .0015, .0015), crack.outputs[0])
        # brasa: só algumas fendas, mais forte embaixo
        ps = N(nt, "ShaderNodeSeparateXYZ"); L(nt, geo.outputs["Position"], ps.inputs[0])
        hz = ramp(nt, [(0, (1, 1, 1)), (.5, (.25, .25, .25)), (1, (.05, .05, .05))]); L(nt, math_(nt, 'DIVIDE', ps.outputs[2], 8.0), hz.inputs[0])
        gm = noise(nt, v, None, .9, 3, .5, seed + 4)
        gr = ramp(nt, [(.6, (0, 0, 0)), (.68, (1, 1, 1))]); L(nt, gm.outputs["Fac"], gr.inputs[0])
        glow = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', crack.outputs[0], gr.outputs[0]), hz.outputs[0])
        L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .92
        ec = mix(nt, (1, .12, .01), (1, .32, .04), n.outputs["Fac"])
        L(nt, ec, b.inputs["Emission Color"]); L(nt, math_(nt, 'MULTIPLY', glow, 3.0*brilho), b.inputs["Emission Strength"])
        K.bump(nt, b, math_(nt, 'SUBTRACT', plate.outputs[0], math_(nt, 'MULTIPLY', n.outputs["Fac"], .3)), .7, .06)
        return m
    return _c(("casca", seed, brilho), f)

def chao_cinza(nome, brasa=.2, seed=0.0):
    """Cinza preta fofa com montes de cinza clara e rachaduras; brasa = quanto das rachaduras brilha."""
    def f():
        m, nt, b = K.new_mat(nome)
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n1 = noise(nt, v, None, .09, 5, .55, seed)
        n2 = noise(nt, v, None, .9, 8, .6, seed + 1)
        n3 = noise(nt, v, None, 7, 5, .55, seed + 2)
        fz = math_(nt, 'ADD', math_(nt, 'MULTIPLY', n1.outputs["Fac"], .6), math_(nt, 'MULTIPLY', n2.outputs["Fac"], .4))
        r = ramp(nt, [(.36, (.008, .0075, .0075)), (.48, (.028, .027, .026)), (.6, (.1, .097, .094)), (.72, (.24, .235, .23))]); L(nt, fz, r.inputs[0])
        col = mix(nt, r.outputs[0], n3.outputs["Color"], .18, 'OVERLAY')
        # rachaduras (voronoi distorcido)
        vd = N(nt, "ShaderNodeVectorMath", operation='ADD'); L(nt, v, vd.inputs[0])
        sc = N(nt, "ShaderNodeVectorMath", operation='SCALE'); L(nt, n2.outputs["Color"], sc.inputs[0]); sc.inputs["Scale"].default_value = 1.2
        L(nt, sc.outputs[0], vd.inputs[1])
        vo = voronoi(nt, vd.outputs[0], None, .32, 'DISTANCE_TO_EDGE', seed + 5)
        cr = ramp(nt, [(0, (1, 1, 1)), (.03, (0, 0, 0))]); L(nt, vo.outputs["Distance"], cr.inputs[0])
        vo2 = voronoi(nt, vd.outputs[0], None, 1.3, 'DISTANCE_TO_EDGE', seed + 6)
        cr2 = ramp(nt, [(0, (1, 1, 1)), (.025, (0, 0, 0))]); L(nt, vo2.outputs["Distance"], cr2.inputs[0])
        crack = math_(nt, 'MAXIMUM', cr.outputs[0], math_(nt, 'MULTIPLY', cr2.outputs[0], .7))
        gm = noise(nt, v, None, .16, 3, .5, seed + 7)
        t0 = .74 - brasa*.4
        gr = ramp(nt, [(t0, (0, 0, 0)), (t0 + .06, (1, 1, 1))]); L(nt, gm.outputs["Fac"], gr.inputs[0])
        glow = math_(nt, 'MULTIPLY', crack, gr.outputs[0])
        col = mix(nt, col, (.003, .002, .002), crack)
        # brilho difuso em volta das rachaduras acesas (cinza aquecida)
        halo = ramp(nt, [(0, (1, 1, 1)), (.12, (0, 0, 0))]); L(nt, vo.outputs["Distance"], halo.inputs[0])
        col = mix(nt, col, (.09, .02, .005), math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', halo.outputs[0], gr.outputs[0]), .7))
        L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .97
        ec = mix(nt, (1, .1, .01), (1, .3, .04), n3.outputs["Fac"])
        L(nt, ec, b.inputs["Emission Color"])
        L(nt, math_(nt, 'ADD', math_(nt, 'MULTIPLY', glow, 3.0), math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', halo.outputs[0], gr.outputs[0]), .08)), b.inputs["Emission Strength"])
        K.bump(nt, b, math_(nt, 'SUBTRACT', fz, math_(nt, 'MULTIPLY', crack, .6)), .6, .08)
        return m
    return _c(("chao", nome), f)

def crosta_granizo():
    """Crosta de granizo vermelho derretido e recongelado no chão (destaque 2)."""
    def f():
        m, nt, b = K.new_mat("crosta_granizo")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        vo = voronoi(nt, v, None, 2.2, 'F1', 3.0)
        ve = voronoi(nt, v, None, 2.2, 'DISTANCE_TO_EDGE', 3.0)
        n = noise(nt, v, None, .6, 5, .6, 4.0)
        r = ramp(nt, [(.2, (.03, .001, .003)), (.6, (.13, .006, .012)), (.9, (.24, .02, .03))]); L(nt, math_(nt, 'ADD', math_(nt, 'MULTIPLY', vo.outputs["Distance"], .6), math_(nt, 'MULTIPLY', n.outputs["Fac"], .5)), r.inputs[0])
        e = ramp(nt, [(0, (.01, .002, .002)), (.05, (1, 1, 1))]); L(nt, ve.outputs["Distance"], e.inputs[0])
        col = mix(nt, r.outputs[0], e.outputs[0], 1, 'MULTIPLY')
        ash = ramp(nt, [(.55, (0, 0, 0)), (.68, (1, 1, 1))]); L(nt, n.outputs["Fac"], ash.inputs[0])
        col = mix(nt, col, (.05, .046, .044), ash.outputs[0])
        L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .5
        b.inputs["Emission Color"].default_value = (.5, .015, .02, 1); b.inputs["Emission Strength"].default_value = .12
        K.bump(nt, b, ve.outputs["Distance"], .4, .03)
        return m
    return _c("crosta", f)

def gelo_rubro():
    """Pedra de granizo: gelo translúcido vermelho-sangue que não derrete."""
    def f():
        m, nt, b = K.new_mat("granizo_rubro")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 6, 5, .6, 2.0)
        r = ramp(nt, [(.3, (.16, .004, .01)), (.7, (.42, .02, .03))]); L(nt, n.outputs["Fac"], r.inputs[0])
        L(nt, r.outputs[0], b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = .35
        b.inputs["Emission Color"].default_value = (.7, .02, .03, 1); b.inputs["Emission Strength"].default_value = .35
        K.bump(nt, b, n.outputs["Fac"], .3, .01)
        return m
    return _c("gelo", f)

def barro():
    return _c("barro", lambda: K.mat_stone("barro_meda", (.075, .055, .042), (.03, .022, .018), 1.6, 0, None, 1.6, 4.0))

def fumaca():
    def f():
        m = bpy.data.materials.new("fumaca"); m.use_nodes = True; nt = m.node_tree
        for n in list(nt.nodes):
            if n.type != 'OUTPUT_MATERIAL': nt.nodes.remove(n)
        out = [n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'][0]
        vp = N(nt, "ShaderNodeVolumePrincipled")
        vp.inputs["Color"].default_value = (.12, .1, .095, 1)
        tc = N(nt, "ShaderNodeTexCoord"); ns = noise(nt, tc.outputs["Object"], None, 1.4, 4, .6, 3.0)
        sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, tc.outputs["Object"], sep.inputs[0])
        # some para cima e nas bordas
        fz = ramp(nt, [(0, (1, 1, 1)), (1, (0, 0, 0))]); L(nt, math_(nt, 'DIVIDE', sep.outputs[2], 5.0), fz.inputs[0])
        d = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', ns.outputs["Fac"], fz.outputs[0]), 1.6)
        d = math_(nt, 'MAXIMUM', math_(nt, 'SUBTRACT', d, .45), 0)
        L(nt, d, vp.inputs["Density"])
        L(nt, vp.outputs[0], out.inputs["Volume"])
        return m
    return _c("fumaca", f)

# ================================================================ geometria orgânica
def tubo(mat, pts, raios, verts=12, seed=0, rug=.12, tampa=True, nome="tubo", sulcos=0, buraco=None):
    """Tubo ao longo de uma polilinha, com anéis irregulares (troncos, galhos, raízes)."""
    r = random.Random(seed)
    P = [Vector(p) for p in pts]
    fase = [r.uniform(0, 6.28) for _ in range(3)]
    vs, fs = [], []
    prev_n = None
    for i, p in enumerate(P):
        t = (P[min(i+1, len(P)-1)] - P[max(i-1, 0)]).normalized()
        a = prev_n if prev_n is not None else (Vector((0, 0, 1)) if abs(t.z) < .9 else Vector((1, 0, 0)))
        n = (a - t*a.dot(t)).normalized(); prev_n = n
        bnm = t.cross(n)
        for k in range(verts):
            ang = k/verts*2*math.pi
            rr = raios[i]*(1 + rug*(.55*math.sin(3*ang + fase[0] + i*.4) + .3*math.sin(7*ang + fase[1] - i*.7)) + rug*.5*r.uniform(-1, 1))
            if sulcos: rr *= 1 - .07*abs(math.sin(sulcos*ang/2 + p.z*.08 + .3*math.sin(p.z*.5 + k)))
            vs.append(p + (n*math.cos(ang) + bnm*math.sin(ang))*rr)
        if i:
            for k in range(verts):
                a0 = (i-1)*verts + k; a1 = (i-1)*verts + (k+1) % verts
                if buraco and buraco((k + .5)/verts*2*math.pi, (P[i].z + P[i-1].z)/2): continue
                fs.append((a0, a1, a1 + verts, a0 + verts))
    if tampa:
        c = len(vs); vs.append(P[-1]); base = (len(P)-1)*verts
        for k in range(verts): fs.append((base + k, base + (k+1) % verts, c))
    me = bpy.data.meshes.new(nome); me.from_pydata([tuple(v) for v in vs], [], fs); me.update()
    for pl in me.polygons: pl.use_smooth = True
    o = bpy.data.objects.new(nome, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat); return o

def galho(mat, p, d, L0, r0, rr, prof=1):
    pts, rad = [], []
    q = Vector(p); dd = Vector(d).normalized(); n = max(3, int(L0/.35))
    for i in range(n + 1):
        pts.append(q.copy()); rad.append(r0*(1 - .8*i/n) + .012)
        dd = (dd + Vector((rr.uniform(-.25, .25), rr.uniform(-.25, .25), rr.uniform(-.1, .15)))).normalized()
        q = q + dd*(L0/n)
    tubo(mat, pts, rad, 7, rr.randint(0, 999), .1)
    if prof and L0 > 1.0:
        k = rr.randint(1, n - 1)
        nd = (dd + Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(0, .6)))).normalized()
        galho(mat, pts[k], nd, L0*.5, rad[k]*.6, rr, prof - 1)

def lascas(mat, c, raio, h, rr, n=6):
    """Topo quebrado: lascas pontudas de madeira em volta da borda."""
    for k in range(n):
        a = k/n*2*math.pi + rr.uniform(-.3, .3)
        b0 = Vector((c[0] + math.cos(a)*raio*.75, c[1] + math.sin(a)*raio*.75, h - .1))
        tip = b0 + Vector((math.cos(a)*rr.uniform(.05, .25), math.sin(a)*rr.uniform(.05, .25), rr.uniform(.3, 1.6)))
        along(mat, b0, tip, raio*rr.uniform(.18, .35), .01, verts=5)

# ================================================================ vocabulário
def tronco_de_pe(seed, h, r):
    def fn(m):
        rr = random.Random(seed); mat = casca(seed % 3)
        lean = Vector((rr.uniform(-.04, .04), rr.uniform(-.04, .04), 1))
        pts, rad = [], []
        n = int(h/.45)
        for i in range(n + 1):
            t = i/n; z = -.3 + t*(h + .3)
            off = lean*z; off.z = 0
            off += Vector((math.sin(t*5 + seed)*.08, math.cos(t*4 + seed)*.08, 0))
            pts.append((off.x, off.y, z))
            rad.append(r*(1.0 - .42*t) * (1 + .45*max(0, .2 - t)/.2))
        tubo(mat, pts, rad, 14, seed, .1)
        top = pts[-1]
        lascas(mat, top, rad[-1], top[2], rr, rr.randint(4, 7))
        # galhos quebrados, curtos, apontando para cima
        for k in range(rr.randint(3, 6)):
            t = rr.uniform(.45, .92); i = int(t*n)
            a = rr.uniform(0, 6.28)
            p = Vector(pts[i]) + Vector((math.cos(a), math.sin(a), 0))*rad[i]*.6
            d = Vector((math.cos(a), math.sin(a), rr.uniform(.2, .9)))
            galho(mat, p, d, rr.uniform(.6, 2.6)*(r/.45), rad[i]*.3, rr, 1 if rr.random() < .5 else 0)
        # raízes
        for k in range(5):
            a = k/5*2*math.pi + rr.uniform(-.3, .3)
            p0 = Vector((math.cos(a)*r*.6, math.sin(a)*r*.6, .5))
            p1 = Vector((math.cos(a)*r*1.6, math.sin(a)*r*1.6, .12)); p2 = Vector((math.cos(a)*r*2.4, math.sin(a)*r*2.4, -.08))
            tubo(mat, [p0, p1, p2], [r*.35, r*.22, r*.08], 7, seed + k, .15)
    return fn

def tronco_tombado(seed, Lc, r):
    def fn(m):
        rr = random.Random(seed); mat = casca(seed % 3, 1.4)
        pts, rad = [], []
        n = int(Lc/.45)
        for i in range(n + 1):
            t = i/n
            pts.append((t*Lc - Lc/2, math.sin(t*3 + seed)*.15, r*.8 + math.sin(t*2.5)*.06))
            rad.append(r*(1 - .35*t))
        tubo(mat, pts, rad, 12, seed, .12)
        lascas(K.mat_wood("cerne_q", (.05, .03, .02)), (Lc/2, 0, 0), rad[-1], r*.8, rr, 0)
        # ponta quebrada com lascas horizontais
        for k in range(5):
            a = rr.uniform(0, 6.28)
            b0 = Vector((Lc/2, math.cos(a)*rad[-1]*.6, r*.8 + math.sin(a)*rad[-1]*.6))
            along(mat, b0, b0 + Vector((rr.uniform(.4, 1.2), rr.uniform(-.15, .15), rr.uniform(-.15, .15))), rad[-1]*.25, .01, verts=5)
        # raizes arrancadas no outro lado
        for k in range(6):
            a = k/6*2*math.pi
            p0 = Vector((-Lc/2, math.cos(a)*r*.5, r*.8 + math.sin(a)*r*.5))
            p1 = p0 + Vector((-rr.uniform(.4, 1.0), math.cos(a)*rr.uniform(.6, 1.4), math.sin(a)*rr.uniform(.4, 1.2)))
            p1.z = max(p1.z, .05)
            tubo(mat, [p0, p1], [r*.3, .03], 6, seed + k, .2)
        for k in range(rr.randint(2, 4)):
            t = rr.uniform(.2, .8); a = rr.uniform(-1.2, 1.2) + (0 if rr.random() < .5 else math.pi)
            p = Vector((t*Lc - Lc/2, math.sin(a)*r*.7, r*.8 + math.cos(a)*r*.7))
            galho(mat, p, Vector((rr.uniform(-.3, .3), math.sin(a), abs(math.cos(a)) + .3)), rr.uniform(.6, 1.8), r*.22, rr, 0)
    return fn

def toco_brasa(seed):
    def fn(m):
        rr = random.Random(seed); mat = casca(seed % 3, 1.6)
        h = rr.uniform(.6, 1.3); r = rr.uniform(.3, .5)
        tubo(mat, [(0, 0, -.2), (0, 0, h*.5), (0, 0, h)], [r*1.35, r*1.05, r], 12, seed, .14, tampa=False)
        cyl(K.mat_emit("brasa_cerne", (1, .32, .05), 7), (0, 0, h - .06), r*.82, .1, verts=12)
        cyl(K.mat_emit("brasa_cerne2", (1, .6, .2), 12), (0, 0, h - .03), r*.4, .06, verts=10)
        lascas(mat, (0, 0), r, h, rr, 5)
        for k in range(4):
            a = k/4*2*math.pi + rr.uniform(-.4, .4)
            tubo(mat, [(math.cos(a)*r*.6, math.sin(a)*r*.6, .3), (math.cos(a)*r*1.9, math.sin(a)*r*1.9, -.05)], [r*.35, r*.1], 7, seed + k, .15)
        point((0, 0, h + .3), (1, .38, .1), 45, .3)
    return fn

def granizo(seed, n=8, raio=.9, gmax=.32):
    def fn(m):
        rr = random.Random(seed); mat = gelo_rubro()
        for k in range(n):
            a = rr.uniform(0, 6.28); d = raio*math.sqrt(rr.random())
            s = rr.uniform(.07, gmax)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=s, location=(math.cos(a)*d, math.sin(a)*d, s*.35))
            o = bpy.context.object; o.scale = (rr.uniform(.8, 1.2), rr.uniform(.8, 1.2), rr.uniform(.7, 1.0))
            o.rotation_euler = (rr.uniform(0, 3), rr.uniform(0, 3), rr.uniform(0, 3))
            o.data.materials.append(mat)
            for pl in o.data.polygons: pl.use_smooth = rr.random() < .6
    return fn

def cogumelos(seed):
    def fn(m):
        rr = random.Random(seed)
        cap = K.mat_stone("cogumelo_cinza", (.28, .27, .26), (.12, .115, .11), 6, 0, None, .4, 9.0)
        stem = K.mat_solid("cog_pe", (.2, .19, .18), 0, .8)
        for k in range(rr.randint(4, 8)):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, .35)
            x, y = math.cos(a)*d, math.sin(a)*d; h = rr.uniform(.08, .32); cr = h*rr.uniform(.4, .7)
            along(stem, (x, y, 0), (x + rr.uniform(-.04, .04), y + rr.uniform(-.04, .04), h), cr*.22, cr*.15, verts=6)
            sphere(cap, (x, y, h), (cr, cr, cr*.45), segs=10)
    return fn

def palafita(seed, porta_luz=True):
    def fn(m):
        rr = random.Random(seed)
        wood = K.mat_wood("tabua_carvoeiro", (.07, .05, .036), seed); wd = m["wood_d"]
        H = 2.4; w, d = 3.4, 3.0
        for sx in (-1, 1):
            for sy in (-1, 1):
                tubo(casca(1, .3), [(sx*w/2*.9, sy*d/2*.9, -.2), (sx*w/2*.9 + rr.uniform(-.08, .08), sy*d/2*.9, H)], [.13, .11], 8, seed, .1)
        for sy in (-1, 1): along(wd, (-w/2*.9, sy*d/2*.9, .4), (w/2*.9, sy*d/2*.9, H - .2), .04, verts=6)
        for sx in (-1, 1): along(wd, (sx*w/2*.9, -d/2*.9, H - .2), (sx*w/2*.9, d/2*.9, .5), .04, verts=6)
        nP = int(w/.24)
        for i in range(nP):
            box(wood, (-w/2 + (i + .5)*w/nP, rr.uniform(-.05, .05), H), (w/nP - .025, d + rr.uniform(-.1, .2), .07), (rr.uniform(-1.5, 1.5), 0, rr.uniform(-1, 1)), .01)
        # cabana de tábuas
        hw, hd, hh = 2.5, 2.1, 2.0
        z0 = H + .04
        for face in range(4):
            if face < 2:
                sy = -1 if face == 0 else 1; n = 10
                for i in range(n):
                    box(wood, (-hw/2 + (i + .5)*hw/n, sy*hd/2, z0 + hh/2 + rr.uniform(-.04, .04)), (hw/n - .015, .06, hh + rr.uniform(-.05, .08)), (0, rr.uniform(-1.5, 1.5), 0), .008)
            else:
                sx = -1 if face == 2 else 1; n = 9
                for i in range(n):
                    box(wood, (sx*hw/2, -hd/2 + (i + .5)*hd/n, z0 + hh/2 + rr.uniform(-.04, .04)), (.06, hd/n - .015, hh + rr.uniform(-.05, .08)), (rr.uniform(-1.5, 1.5), 0, 0), .008)
        box(K.mat_solid("escuro", (.004, .003, .003), 0, .9), (0, 0, z0 + hh/2), (hw - .1, hd - .1, hh - .05), bevel=0)
        # porta (frente, -y) e janela acesa (lado +x)
        quente = K.mat_window_lit()
        box(quente if porta_luz else wd, (.4, -hd/2 - .02, z0 + .8), (.65, .03, 1.55), bevel=0)
        box(wd, (.4 - .38, -hd/2 - .05, z0 + .8), (.08, .05, 1.65), bevel=0); box(wd, (.4 + .38, -hd/2 - .05, z0 + .8), (.08, .05, 1.65), bevel=0)
        box(quente, (hw/2 + .02, 0, z0 + 1.25), (.03, .7, .55), bevel=0)
        for k in (-1, 0, 1): box(wd, (hw/2 + .05, k*.25, z0 + 1.25), (.04, .04, .6), bevel=0)
        box(wd, (hw/2 + .06, .45, z0 + 1.25), (.03, .3, .65), (0, 0, 25), 0)  # veneziana aberta
        point((hw/2 + .7, 0, z0 + 1.2), (1, .5, .2), 25, .2); point((.4, -hd/2 - .7, z0 + .9), (1, .5, .2), 20 if porta_luz else 0, .2)
        # telhado de tábuas e zinco remendado
        roof = K.mat_wood("telhado_carvoeiro", (.05, .035, .025), seed + 5)
        rh = 1.0; zt = z0 + hh
        for sx in (-1, 1):
            nb = 9
            for i in range(nb):
                y = -hd/2 - .35 + (i + .5)*(hd + .7)/nb
                o = box(roof if (i + seed) % 4 else m["rust"], (sx*(hw/4 + .15), y, zt + rh/2 - .02), (hw/2 + .55, (hd + .7)/nb - .02, .05), (0, 0, 0), .005)
                o.rotation_euler = (0, -sx*math.atan2(rh, hw/2 + .3), 0)
        prism(wd, (0, -hd/2, zt), hw, .06, rh)
        prism(wd, (0, hd/2, zt), hw, .06, rh)
        # chaminé de lata com brasa
        cyl(m["rust"], (-.7, .5, zt + .9), .1, 1.4, verts=8)
        cyl(K.mat_emit("brasa_cano", (1, .35, .08), 4), (-.7, .5, zt + 1.61), .07, .03, verts=8)
        # guarda-corpo e escada
        for i in range(6):
            x = -w/2 + .1 + i*(w - .2)/5
            along(wd, (x, -d/2 + .08, H), (x, -d/2 + .08, H + .9), .03, verts=5)
        along(wd, (-w/2 + .1, -d/2 + .08, H + .9), (w/2 - .1, -d/2 + .08, H + .88), .03, verts=5)
        for sx in (-1, 1): along(wd, (w/2 + .5, -.6 + sx*.25, 0), (w/2 - .05, -.6 + sx*.25, H + .1), .035, verts=5)
        for k in range(8):
            t = (k + .5)/8
            along(wd, (w/2 + .5 - .55*t, -.85, H*t), (w/2 + .5 - .55*t, -.35, H*t), .025, verts=4)
        # lanterna pendurada no beiral
        along(m["iron"], (-hw/2 - .1, -hd/2 - .3, zt + .1), (-hw/2 - .1, -hd/2 - .3, zt - .35), .008, verts=4)
        cyl(K.mat_emit("lanterna_v", (1, .55, .2), 9), (-hw/2 - .1, -hd/2 - .3, zt - .48), .07, .18, verts=6)
        point((-hw/2 - .1, -hd/2 - .3, zt - .5), (1, .5, .18), 22, .05)
        # sacos de carvão no deck
        for k in range(3):
            sphere(m["sack"], (w/2 - .4 - k*.45, d/2 - .35, H + .25), (.22, .2, .28), segs=10)
    return fn

def meda(seed):
    """Meda de carvão: forno de barro em cúpula, fumegando, com brasa nos respiros."""
    def fn(m):
        rr = random.Random(seed); R = rr.uniform(1.3, 1.7)
        o = sphere(barro(), (0, 0, -.1), (R, R, R*.72), segs=24); K.displace(o, .1, .5, seed, 2)
        brasa = K.mat_emit("brasa_respiro", (1, .3, .05), 10)
        for k in range(7):
            a = k/7*2*math.pi + rr.uniform(-.2, .2)
            sphere(brasa, (math.cos(a)*R*.94, math.sin(a)*R*.94, .18), (.09, .09, .07), segs=8)
        cyl(brasa, (0, 0, R*.62), .18, .1, verts=10)
        point((0, 0, R*.62 + .4), (1, .38, .1), 40, .2)
        # cobertura de terra/cinza e lenha empilhada ao lado
        for k in range(14):
            a = rr.uniform(0, 6.28)
            along(casca(2, .5), (R*.9 + .4, -.6 + k*.1, .1 + (k % 4)*.13), (R*.9 + .4 + rr.uniform(-.1, .1), .6 + k*.1 - 1.2, .1 + (k % 4)*.13), .06, verts=6) if k < 8 else None
        along(m["wood_d"], (-R - .2, .2, 0), (-R + .2, .3, 1.5), .03, verts=5)   # pá encostada
        box(m["iron"], (-R - .22, .19, .12), (.2, .04, .28), (0, 15, 0), .005)
        # fumaça baixa saindo do topo
        if FUMACA_VOL:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=1.2, depth=5, location=(.4, .3, R*.6 + 2.3))
            f = bpy.context.object; f.rotation_euler = (math.radians(8), math.radians(10), 0)
            f.data.materials.append(fumaca())
    return fn

def carroca_carvao(seed):
    def fn(m):
        rr = random.Random(seed); wood = K.mat_wood("tabua_carroca", (.06, .045, .032), seed); wd = m["wood_d"]
        box(wood, (0, 0, .7), (1.3, 2.3, .08), bevel=.01)
        for sx in (-1, 1): box(wood, (sx*.62, 0, .92), (.06, 2.3, .42), bevel=.01)
        for sy in (-1, 1): box(wood, (0, sy*1.12, .92), (1.3, .06, .42), bevel=.01)
        for sx in (-1, 1):
            torus(wd, (sx*.75, -.3, .55), .55, .05, (0, 90, 0))
            cyl(m["iron"], (sx*.75, -.3, .55), .09, .12, (0, 90, 0), 8)
            for k in range(8):
                a = math.radians(45*k)
                along(wd, (sx*.75, -.3, .55), (sx*.75, -.3 + math.cos(a)*.53, .55 + math.sin(a)*.53), .022, verts=5)
        for sx in (-1, 1): along(wd, (sx*.45, 1.15, .7), (sx*.4, 2.6, .05), .045, verts=6)
        box(wd, (0, -1.2, .45), (.08, .08, .9), bevel=.005)  # escora
        coal = K.mat_solid("carvao_brilho", (.012, .011, .011), 0, .35)
        for k in range(60):
            x, y = rr.uniform(-.55, .55), rr.uniform(-1.05, 1.05)
            z = 1.1 + .35*(1 - (x/.6)**2)*(1 - (y/1.1)**2) + rr.uniform(-.05, .05)
            o = sphere(coal, (x, y, z), (rr.uniform(.07, .14), rr.uniform(.07, .14), rr.uniform(.05, .1)), segs=6)
            o.rotation_euler = (rr.uniform(0, 3), rr.uniform(0, 3), rr.uniform(0, 3))
        for k in range(2): sphere(m["sack"], (.9 + k*.1, -1.2 + k*.55, .25), (.25, .22, .3), segs=10)
    return fn

def tabuas(seed):
    """Trilha de tábuas: segmento de 1,5 m de tábuas atravessadas sobre a cinza."""
    def fn(m):
        rr = random.Random(seed); wood = K.mat_wood("tabua_trilha", (.065, .048, .034), seed + 1)
        for i in range(5):
            if rr.random() < .1: continue
            box(wood, (-.6 + i*.3 + rr.uniform(-.03, .03), rr.uniform(-.08, .08), .05), (.25, 1.3 + rr.uniform(-.15, .15), .06), (rr.uniform(-2, 2), rr.uniform(-2, 2), rr.uniform(-6, 6)), .01)
        for sy in (-1, 1): box(m["wood_d"], (0, sy*.5, .015), (1.55, .1, .05), bevel=.005)
    return fn

def cerca_galhos(seed):
    """Cerca de galhos queimados (segmento de 3 m ao longo de X)."""
    def fn(m):
        rr = random.Random(seed); mat = casca(2, .4)
        xs = [-1.5 + i*.75 for i in range(5)]
        tops = []
        for x in xs:
            h = rr.uniform(1.0, 1.6)
            tubo(mat, [(x, 0, -.1), (x + rr.uniform(-.1, .1), rr.uniform(-.08, .08), h)], [.07, .045], 6, seed + int(x*10), .2)
            tops.append(h)
        for zz in (.45, .9):
            p = [Vector((x, rr.uniform(-.05, .05), zz + rr.uniform(-.1, .1))) for x in xs]
            for a, b in zip(p, p[1:]):
                tubo(mat, [a, (a + b)/2 + Vector((0, 0, rr.uniform(-.08, .08))), b], [.035, .03, .03], 5, seed, .2)
    return fn

def ninho_corvo(seed):
    def fn(m):
        rr = random.Random(seed); twig = casca(2, 0.0)
        for k in range(26):
            a = rr.uniform(0, 6.28); r0 = rr.uniform(.25, .45)
            p = Vector((math.cos(a)*r0, math.sin(a)*r0, rr.uniform(0, .25)))
            dd = Vector((-math.sin(a), math.cos(a), rr.uniform(-.2, .2)))*rr.uniform(.3, .6)
            along(twig, p - dd, p + dd, .018, verts=4)
        crow = K.mat_solid("corvo", (.01, .01, .012), 0, .4)
        sphere(crow, (0, 0, .35), (.1, .17, .1), segs=8); sphere(crow, (0, -.15, .45), (.06, .07, .06), segs=8)
        along(crow, (0, -.2, .45), (0, -.3, .43), .02, .002, verts=4)
    return fn

# ================================================================ marco: a Árvore-Mãe
def arvore_mae(cx, cy, cz_rot=0.0):
    """Sequoia carbonizada gigante e oca; a vila dos carvoeiros mora dentro e em volta."""
    m = C.mats(); rr = random.Random(77)
    before = set(bpy.data.objects)
    mat = casca(0, 1.3)
    R0, H = 4.6, 15.5
    # casca: casco cilíndrico (solidify) com a boca aberta de frente para a câmera
    pts, rad = [], []
    n = 40
    for i in range(n + 1):
        t = i/n; z = -.5 + t*(H + .5)
        pts.append((math.sin(t*4)*.25, math.cos(t*3)*.25, z))
        rad.append(R0*(1 - .45*t)*(1 + .5*max(0, .12 - t)/.12))
    face = math.radians(-50)
    tangent = Vector((-math.sin(face), math.cos(face), 0)); radial = Vector((math.cos(face), math.sin(face), 0))
    def dang(a): return abs(((a - face + math.pi) % (2*math.pi)) - math.pi)
    def buraco(a, z):
        # boca em ogiva, alta e irregular, de frente para a câmera; e três janelas lá em cima
        if dang(a) < .42*max(0, 1 - max(0, z - 3.2)/3.6)**.5 and z < 6.8: return True
        for (fa, zz, ww) in JAN:
            if abs(((a - math.radians(fa) + math.pi) % (2*math.pi)) - math.pi) < ww and abs(z - zz) < ww*3.2: return True
        return False
    JAN = [(-15, 10.0, .09), (-95, 8.4, .08), (-40, 12.2, .07)]
    o = tubo(mat, pts, rad, 72, 5, .06, tampa=False, nome="mae_casca", sulcos=22, buraco=buraco)
    s = o.modifiers.new("sol", 'SOLIDIFY'); s.thickness = .75; s.offset = -1; s.use_rim = True
    # janelas pequenas mais acima (luz de dentro)
    for (fa, zz, ww) in JAN:
        a = math.radians(fa); rad_ = R0*(1 - .45*zz/H)
        point((math.cos(a)*(rad_ - 1.2), math.sin(a)*(rad_ - 1.2), zz), (1, .45, .15), 60, .3)
    # topo partido: lascas enormes
    top = pts[-1]
    for k in range(16):
        a = k/16*2*math.pi + rr.uniform(-.15, .15)
        rt = rad[-1] + .25
        b0 = Vector((top[0] + math.cos(a)*rt, top[1] + math.sin(a)*rt, H - .3))
        tip = b0 + Vector((math.cos(a)*rr.uniform(-.2, .6), math.sin(a)*rr.uniform(-.2, .6), rr.uniform(.8, 4.5)))
        along(mat, b0, tip, rr.uniform(.25, .5), .02, verts=6)
    # raízes enormes
    for k in range(9):
        a = k/9*2*math.pi + rr.uniform(-.2, .2)
        if dang(a) < .5: continue
        p0 = Vector((math.cos(a)*R0*.85, math.sin(a)*R0*.85, 1.6))
        p1 = Vector((math.cos(a)*R0*1.25, math.sin(a)*R0*1.25, .5)); p2 = Vector((math.cos(a + .08)*R0*1.7, math.sin(a + .08)*R0*1.7, .05))
        p3 = Vector((math.cos(a + .12)*R0*2.2, math.sin(a + .12)*R0*2.2, -.5))
        tubo(mat, [p0, p1, p2, p3], [.9, .75, .5, .3], 10, 30 + k, .15)
    # galhos mortos grandes
    for (zz, fa, Lg) in [(13.5, 150, 5.5), (15.5, 30, 4.5), (11.5, -150, 4.0), (16.5, -80, 3.2)]:
        a = math.radians(fa); rz = R0*(1 - .45*zz/H)
        galho(mat, (math.cos(a)*rz*.9, math.sin(a)*rz*.9, zz), (math.cos(a), math.sin(a), .55), Lg, .45, rr, 1)
    # interior: chão de tábuas, plataformas, luz quente (a vila dentro)
    wood = K.mat_wood("tabua_mae", (.07, .05, .036), 3.0)
    cyl(wood, (0, 0, .05), R0*.95, .1, verts=32)
    for zz in (4.0, 8.0):
        rz = R0*(1 - .45*zz/H) - .1
        cyl(wood, (0, 0, zz), rz, .15, verts=32)
        for k in range(10):
            a = k/10*2*math.pi
            along(m["wood_d"], (math.cos(a)*(rz - .1), math.sin(a)*(rz - .1), zz - .1), (math.cos(a)*(rz - 1.2), math.sin(a)*(rz - 1.2), zz - 1.4), .08, verts=6)
    point((radial.x*1.6, radial.y*1.6, 2.0), (1, .45, .15), 900, .6)
    point((radial.x*1.0, radial.y*1.0, 6.0), (1, .45, .15), 400, .5)
    point((0, 0, 10.0), (1, .45, .15), 300, .5)
    sphere(K.mat_emit("fogo", (1, .32, .06), 8), (radial.x*.5 - tangent.x*1.0, radial.y*.5 - tangent.y*1.0, .3), (.5, .5, .35), segs=10)
    # fogueira e cortina de lona na boca
    for k in range(5):
        p = radial*(R0 - .6) + tangent*(-1.2 + k*.6)
        box(m["red_cloth"] if k % 2 else m["cloth"], (p.x, p.y, 4.6), (.08, .55, 1.2), (0, 0, math.degrees(face) + rr.uniform(-8, 8)), .01)
    # escada em espiral por fora até a varanda de cima
    st = []
    a0, a1, z1 = math.radians(40), math.radians(-200), 8.0
    nst = 46
    for i in range(nst):
        t = i/(nst - 1); a = a0 + (a1 - a0)*t; zz = .3 + t*(z1 - .3)
        rz = R0*(1 - .45*zz/H)*(1 + .06) + .7
        box(wood, (math.cos(a)*rz, math.sin(a)*rz, zz), (.32, 1.2, .07), (0, 0, math.degrees(a)), .01)
        if i % 3 == 0:
            along(m["wood_d"], (math.cos(a)*(rz + .6), math.sin(a)*(rz + .6), zz), (math.cos(a)*(rz + .6), math.sin(a)*(rz + .6), zz + 1.0), .03, verts=5)
            along(m["wood_d"], (math.cos(a)*(rz - .3), math.sin(a)*(rz - .3), zz - .05), (math.cos(a)*(R0*(1 - .45*zz/H)), math.sin(a)*(R0*(1 - .45*zz/H)), zz - .9), .05, verts=5)
            st.append(Vector((math.cos(a)*(rz + .6), math.sin(a)*(rz + .6), zz + 1.0)))
    for p, q in zip(st, st[1:]): along(K.mat_cloth("corda", (.09, .075, .05), 1.0), p, q, .015, verts=4)
    # varanda baixa (deck em anel) a 2,4 m, ligada às passarelas
    for k in range(34):
        a = math.radians(-165 + k*7.5)
        if abs(((a - face + math.pi) % (2*math.pi)) - math.pi) < .35: continue
        rz = R0*1.04 + 1.0
        box(wood, (math.cos(a)*rz, math.sin(a)*rz, 2.4), (1.9, .55, .07), (0, 0, math.degrees(a) + rr.uniform(-2, 2)), .01)
        if k % 3 == 0:
            tubo(casca(1, .3), [(math.cos(a)*(rz + .8), math.sin(a)*(rz + .8), -.2), (math.cos(a)*(rz + .8), math.sin(a)*(rz + .8), 3.3)], [.1, .09], 7, k, .1)
        if k % 6 == 0:
            p = (math.cos(a)*(rz + .9), math.sin(a)*(rz + .9), 3.0)
            cyl(K.mat_emit("lanterna_v", (1, .55, .2), 9), (p[0], p[1], p[2] - .2), .08, .2, verts=6)
            point((p[0], p[1], p[2] - .3), (1, .5, .18), 30, .05)
    # lanternas penduradas em cordas no alto
    for k in range(6):
        a = math.radians(-120 + k*25); zz = 6 + (k % 3)*1.6; rz = R0*(1 - .45*zz/H) + .6
        cyl(K.mat_emit("lanterna_v", (1, .55, .2), 9), (math.cos(a)*rz, math.sin(a)*rz, zz), .07, .18, verts=6)
        point((math.cos(a)*rz, math.sin(a)*rz, zz - .1), (1, .5, .18), 18, .05)
    new = [ob for ob in bpy.data.objects if ob not in before]
    root = bpy.data.objects.new("arvore_mae", None); bpy.context.scene.collection.objects.link(root)
    for ob in new:
        if ob.parent is None: ob.parent = root
    root.location = (cx, cy, 0); root.rotation_euler = (0, 0, math.radians(cz_rot))
    return root, R0, face

def passarela(a, b, z, larg=1.0, seed=0, alturas=None):
    """Passarela de tábuas sobre estacas entre dois pontos do mundo (na altura z)."""
    m = C.mats(); rr = random.Random(seed)
    wood = K.mat_wood("tabua_passarela", (.068, .05, .035), 7.0)
    a, b = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0)); d = b - a; Ln = d.length; u = d.normalized()
    nrm = Vector((-u.y, u.x, 0)); ang = math.degrees(math.atan2(u.y, u.x))
    n = int(Ln/.28)
    za = z if alturas is None else alturas[0]; zb = z if alturas is None else alturas[1]
    for i in range(n):
        t = (i + .5)/n; p = a + d*t; zz = za + (zb - za)*t - math.sin(t*math.pi)*.12
        if rr.random() < .05: continue
        box(wood, (p.x, p.y, zz), (.24, larg + rr.uniform(-.1, .1), .06), (rr.uniform(-2, 2), 0, ang + rr.uniform(-3, 3)), .008)
    k = max(2, int(Ln/1.8))
    rail = []
    for i in range(k + 1):
        t = i/k; p = a + d*t; zz = za + (zb - za)*t
        for sgn in (-1, 1):
            q = p + nrm*sgn*larg*.55
            tubo(casca(1, .25), [(q.x, q.y, -.2), (q.x, q.y, zz + .9)], [.08, .07], 6, seed + i, .12)
        rail.append(Vector((*(p + nrm*(-larg*.55)).xy, zz + .85)))
    corda = K.mat_cloth("corda", (.09, .075, .05), 1.0)
    for p, q in zip(rail, rail[1:]):
        along(corda, p, q, .018, verts=4)

# ================================================================ cena
C.iniciar(ceu=(.05, .012, .01), poeira=(.12, .115, .11), luzes=False)
C.sol((1, .32, .2), 2.2, (58, 0, -135), .1, "contraluz")
C.sol((.45, .45, .6), .35, K.KEY_ROT, .2, "fill")
C.sol((.9, .3, .2), .4, (25, 0, 160), .3, "rasante")
sc = bpy.context.scene
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 1.4
rnd = random.Random(23)

# marco: Árvore-Mãe no plano médio, um pouco à esquerda
MX, MY = W(-4, -1)
root, R0, FACE = arvore_mae(MX, MY)
def em_volta(ang_deg, dist):
    a = math.radians(ang_deg); return (MX + math.cos(a)*dist, MY + math.sin(a)*dist)

# vila dos carvoeiros em palafitas, ligada à varanda da árvore por passarelas
casas = [(-15, 11.0, 15), (-95, 11.5, -10), (25, 12.0, 40), (-140, 11.0, 70)]
deck = R0*1.04 + 1.6
for i, (ang, dist, rot) in enumerate(casas):
    x, y = em_volta(ang, dist)
    C.grupo(palafita(40 + i, i != 2), x, y, ang + 90 + rot*.0, 1.0, chave=f"palafita{i}")
    a2 = em_volta(ang, deck); b2 = em_volta(ang, dist - 1.8)
    passarela(a2, b2, 2.42, 1.0, 10 + i)
# passarela entre duas casas
passarela(em_volta(-15, 12.4), em_volta(25, 12.6), 2.42, .9, 31)

# medas de carvão e a carvoaria em volta da vila
for i, (s, d) in enumerate([(9, -2), (13, 3), (6, -7), (-19, -4)]):
    x, y = W(s, d); C.grupo(meda(60 + i), x, y, rnd.uniform(0, 360), 1.0, chave=f"meda{i % 3}")
x, y = W(3, -5.5); C.grupo(carroca_carvao(1), x, y, 115, 1.0, chave="carroca")
x, y = W(11.5, -6.5); C.grupo(carroca_carvao(2), x, y, 200, 1.0, chave="carroca2")
for (s, d) in [(4.5, -2.5), (10.5, 1.0), (-15, -2), (1, -9.5), (7.5, -9.5)]:
    x, y = W(s, d); C.por("lanterna_procissao", x, y, rnd.uniform(0, 360))
for (s, d) in [(5.5, -4.0), (12, -3.5)]:
    x, y = W(s, d); C.por("caixas", x, y, rnd.uniform(0, 360));
x, y = W(14.5, -1); C.por("sacos_areia", x, y, 30)
x, y = W(7.5, -1.0); C.por("fogueira", x, y, 0)

# trilha de tábuas: do primeiro plano até a boca da árvore
trilha = [(16, -30), (14, -24), (10.5, -18), (7, -13.5), (3.5, -9.5), (0, -6), (-2.5, -2.0)]
segs = []
for (s0, d0), (s1, d1) in zip(trilha, trilha[1:]):
    a, b = Vector(W(s0, d0)), Vector(W(s1, d1)); Ln = (b - a).length; n = max(1, round(Ln/1.5))
    for k in range(n):
        p = a + (b - a)*((k + .5)/n); segs.append(p)
        ang = math.degrees(math.atan2((b - a).y, (b - a).x))
        C.grupo(tabuas(len(segs) % 4), p.x, p.y, ang, 1.0, chave=f"tabuas{len(segs) % 4}")
# cerca de galhos ao longo da trilha, perto da vila
for i, (s, d, r_) in enumerate([(12.5, -16, 0), (4.5, -15.5, 0), (9.5, -10.5, 0), (1, -11.2, 0)]):
    x, y = W(s, d)
    C.grupo(cerca_galhos(i % 3), x, y, 45 + 60 + rnd.uniform(-12, 12), 1.0, chave=f"cerca{i % 3}")

def livre(s, d, folga=0):
    if (s + 4)**2 + (d + 1)**2 < (18 + folga)**2 and d > -14: return False   # vila e árvore
    if -12 < d < -0 and -22 < s < 16 and d > -9: return False
    for (ts, td) in trilha:
        if (s - ts)**2 + (d - td)**2 < (3.2 + folga)**2: return False
    return True

# troncos carbonizados de pé (o vocabulário principal), mais densos no fundo e nas bordas
var = [(101, 9.5, .42), (102, 12.0, .5), (103, 8.0, .36), (104, 13.5, .55), (105, 10.5, .45)]
pos = []
tent = 0
while len(pos) < 70 and tent < 4000:
    tent += 1
    s, d = rnd.uniform(-48, 48), rnd.uniform(-34, 52)
    if not livre(s, d): continue
    # menos no primeiro plano central (legibilidade), mais nas bordas e no fundo
    if d < -14 and abs(s) < 18 and rnd.random() < .85: continue
    if any((s - a)**2 + (d - b)**2 < 4.0**2 for a, b in pos): continue
    pos.append((s, d))
for i, (s, d) in enumerate(pos):
    k = i % len(var); x, y = W(s, d)
    C.grupo(tronco_de_pe(*var[k]), x, y, rnd.uniform(0, 360), rnd.uniform(.85, 1.15), chave=f"tronco{k}")
# troncos de moldura no primeiro plano (bordas)
for (s, d, k) in [(-27, -22, 1), (27, -16, 3), (-22, -30, 4)]:
    x, y = W(s, d); C.grupo(tronco_de_pe(*var[k]), x, y, rnd.uniform(0, 360), 1.1, chave=f"tronco{k}")
# troncos tombados
tvar = [(201, 7.0, .45), (202, 9.0, .55), (203, 5.5, .38)]
for i, (s, d) in enumerate([(19, -21), (-14, -17), (24, 8), (-34, 6), (-8, 26), (20, 30), (31, -6), (-26, 22)]):
    if not livre(s, d, -1.5): continue
    x, y = W(s, d); C.grupo(tronco_tombado(*tvar[i % 3]), x, y, rnd.uniform(0, 360), 1.0, chave=f"tombado{i % 3}")
# tocos em brasa
for i, (s, d) in enumerate([(9, -24), (-6, -21), (21, -12), (-17, -10), (17, 17), (-30, -6), (2, 20), (26, -26), (-12, 33), (35, 14)]):
    x, y = W(s, d); C.grupo(toco_brasa(300 + i % 4), x, y, rnd.uniform(0, 360), 1.0, chave=f"toco{i % 4}")

# destaque 1: brasa exposta (rachaduras abertas) em manchas; destaque 2: crosta de granizo rubro
brasa_m = chao_cinza("chao_brasa", brasa=1.1, seed=3.0)
for (s, d, r_) in [(13, -21, 3.2), (-9, -24, 2.6), (22, 2, 4.0), (-28, 10, 3.5), (6, 26, 3.0)]:
    C.mancha(brasa_m, W(s, d), r_, seed=int(s*3 + d) % 97, irregular=.5, z=.05, nome="brasa")
crosta = crosta_granizo()
lagos = [(-1, -22, 3.4), (25, -9, 3.0), (-22, 18, 4.5), (14, 22, 3.0)]
for (s, d, r_) in lagos:
    C.mancha(crosta, W(s, d), r_, seed=int(s*5 + d) % 97, irregular=.45, z=.06, nome="crosta")
    for k in range(5):
        a = rnd.uniform(0, 6.28); rr_ = rnd.uniform(0, r_*.8)
        x, y = W(s + math.cos(a)*rr_, d + math.sin(a)*rr_)
        C.grupo(granizo(500 + k % 3, 10, .8, .3), x, y, rnd.uniform(0, 360), 1.0, chave=f"granizo_l{k % 3}")
# pedras de granizo espalhadas como frutas podres por toda parte
for k in range(110):
    s, d = rnd.uniform(-40, 40), rnd.uniform(-32, 45)
    if (s + 4)**2 + (d + 1)**2 < 6.5**2: continue
    x, y = W(s, d)
    C.grupo(granizo(600 + k % 5, rnd.randint(2, 6), .6, .22), x, y, rnd.uniform(0, 360), rnd.uniform(.8, 1.3), chave=f"granizo{k % 5}")
# cogumelos de cinza
for k in range(45):
    s, d = rnd.uniform(-38, 38), rnd.uniform(-30, 40)
    if not livre(s, d, -2): continue
    x, y = W(s, d); C.grupo(cogumelos(700 + k % 4), x, y, rnd.uniform(0, 360), rnd.uniform(.9, 1.6), chave=f"cog{k % 4}")
# ninhos de corvo no alto de dois troncos (perto do topo)
for i in (2, 7):
    if i < len(pos):
        s, d = pos[i]; x, y = W(s, d)
        C.grupo(ninho_corvo(800 + i), x + .3, y, 0, 1.0, z=var[i % len(var)][1]*.8, chave=f"ninho{i}")

# chão-base: cinza preta fofa com rachaduras de brasa (por último)
C.chao(chao_cinza("chao_cinza", brasa=0.0, seed=0.0), 220, ondula=.1, seed=4)
cx, cy = W(0, 0)
C.render(OUT, centro=(cx, cy), largura=56, W=960 if Q else 1920, H=540 if Q else 1080, samples=16 if Q else 96)
