# Vinheta da Costa Rubra (nível 30 a 45, segunda trombeta): o mar virou sangue e coalhou numa
# crosta ferrugem rachada. Um chão só (crosta), dois destaques (sal e poça viva de sangue), o
# mesmo vocabulário em toda parte (casco virado, mastro tombado, âncora, corrente, rede, costela
# de baleia, cais, barril, boia, guindaste, ossada de peixe) e o marco: o Porto dos Cascos com o
# Farol Cego ao fundo e a montanha em chamas no horizonte.
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from mathutils import Vector
import cena as C
from cena import por
K = C.K
from kit import box, cyl, sphere, along, torus, displace, chain, N, L, ramp, mix, math_, noise, voronoi, bump, new_mat
Q = os.environ.get("Q") == "1"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "costa_rubra")
S2 = math.sqrt(2)

def W(u, v):
    """(u, v) em metros de tela no chão (u para a direita, v para cima/fundo) -> (x, y) do mundo."""
    return ((u - v)/S2, (u + v)/S2)

def P(fn, u, v, rot=0.0, s=1.0, z=0.0, chave=None):
    x, y = W(u, v); return C.grupo(fn, x, y, rot, s, z, chave)

def PK(nome, u, v, rot=0.0, s=1.0, z=0.0, **kw):
    x, y = W(u, v); return por(nome, x, y, rot, s, z, **kw)

# ------------------------------------------------------------------ materiais
_MC = {}
def mm(nome, fn):
    if nome not in _MC: _MC[nome] = fn()
    return _MC[nome]

def mat_crosta(seed=0.0, nome="crosta"):
    """Sangue coalhado: placas ferrugem-escuras de lama seca, rachaduras molhadas de sangue
    que brilham, crosta de sal nas bordas e brasas de enxofre no fundo de algumas fendas."""
    m, nt, b = new_mat(nome)
    tc = N(nt, "ShaderNodeTexCoord"); v = tc.outputs["Object"]; w = None
    n = noise(nt, v, w, .35, 8, .6, seed)
    n2 = noise(nt, v, w, 4.0, 6, .55, seed + 3)
    base = ramp(nt, [(.3, (.028, .009, .006)), (.5, (.07, .022, .012)), (.72, (.11, .045, .024)), (.9, (.13, .07, .045))])
    L(nt, n.outputs["Fac"], base.inputs[0])
    col = mix(nt, base.outputs[0], n2.outputs["Color"], .22, 'OVERLAY')
    # placas grandes e rachaduras finas
    vo = voronoi(nt, v, w, .32, 'DISTANCE_TO_EDGE', seed + 5, 1.0)
    vf = voronoi(nt, v, w, 1.3, 'DISTANCE_TO_EDGE', seed + 9, 1.0)
    vc = voronoi(nt, v, w, .32, 'F1', seed + 5, 1.0)
    big = ramp(nt, [(0, (0, 0, 0)), (.022, (1, 1, 1))]); L(nt, vo.outputs["Distance"], big.inputs[0])
    fin = ramp(nt, [(0, (0, 0, 0)), (.01, (1, 1, 1))]); L(nt, vf.outputs["Distance"], fin.inputs[0])
    fm = noise(nt, v, w, 1.2, 3, .5, seed + 11)
    fmr = ramp(nt, [(.5, (1, 1, 1)), (.6, (0, 0, 0))]); L(nt, fm.outputs["Fac"], fmr.inputs[0])
    fin2 = math_(nt, 'MAXIMUM', fin.outputs[0], fmr.outputs[0])
    plate = math_(nt, 'MINIMUM', big.outputs[0], fin2)          # 0 = fenda, 1 = placa
    dome = ramp(nt, [(0, (0, 0, 0)), (.15, (1, 1, 1))]); dome.color_ramp.interpolation = 'EASE'
    L(nt, vo.outputs["Distance"], dome.inputs[0])
    # cor por placa (umas mais secas e claras)
    pc = ramp(nt, [(0, (.75, .7, .7)), (1, (1.25, 1.15, 1.05))]); L(nt, vc.outputs["Color"], pc.inputs[0])
    col = mix(nt, col, pc.outputs[0], 1, 'MULTIPLY')
    # sal nas bordas levantadas das placas
    edge = ramp(nt, [(.022, (1, 1, 1)), (.07, (0, 0, 0))]); L(nt, vo.outputs["Distance"], edge.inputs[0])
    sn = noise(nt, v, w, 2.2, 5, .6, seed + 17)
    snr = ramp(nt, [(.48, (0, 0, 0)), (.62, (1, 1, 1))]); L(nt, sn.outputs["Fac"], snr.inputs[0])
    salt = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', edge.outputs[0], snr.outputs[0]), .55)
    col = mix(nt, col, (.32, .27, .22), salt)
    # fenda: sangue úmido e escuro
    wet = (.035, .002, .002)
    col = mix(nt, wet, col, plate)
    L(nt, col, b.inputs["Base Color"])
    rg = math_(nt, 'ADD', .3, math_(nt, 'MULTIPLY', plate, .6)); L(nt, rg, b.inputs["Roughness"])
    # brasa de enxofre no fundo de poucas fendas grandes
    em = noise(nt, v, w, .6, 3, .5, seed + 23)
    emr = ramp(nt, [(.7, (0, 0, 0)), (.76, (1, 1, 1))]); L(nt, em.outputs["Fac"], emr.inputs[0])
    deep = ramp(nt, [(0, (1, 1, 1)), (.012, (0, 0, 0))]); L(nt, vo.outputs["Distance"], deep.inputs[0])
    b.inputs["Emission Color"].default_value = (1, .3, .05, 1)
    L(nt, math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', emr.outputs[0], deep.outputs[0]), 3.0), b.inputs["Emission Strength"])
    h = math_(nt, 'ADD', math_(nt, 'MULTIPLY', dome.outputs[0], plate), math_(nt, 'MULTIPLY', n2.outputs["Fac"], .25))
    bump(nt, b, h, .9, .08)
    return m

def mat_sal():
    m, nt, b = new_mat("sal")
    tc = N(nt, "ShaderNodeTexCoord"); v = tc.outputs["Object"]
    n = noise(nt, v, None, 1.5, 8, .65, 4.0)
    vo = voronoi(nt, v, None, 3.0, 'DISTANCE_TO_EDGE', 2.0)
    r = ramp(nt, [(.3, (.14, .1, .08)), (.55, (.3, .26, .21)), (.8, (.42, .38, .32))]); L(nt, n.outputs["Fac"], r.inputs[0])
    cr = ramp(nt, [(0, (.25, .08, .05)), (.04, (1, 1, 1))]); L(nt, vo.outputs["Distance"], cr.inputs[0])
    col = mix(nt, r.outputs[0], cr.outputs[0], 1, 'MULTIPLY')
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .55
    bump(nt, b, math_(nt, 'ADD', n.outputs["Fac"], math_(nt, 'MULTIPLY', vo.outputs["Distance"], 2)), .6, .04)
    return m

def mat_poca():
    """Poça viva de sangue: vermelho fundo, espelhado, com ondinhas e borda coagulando."""
    m, nt, b = new_mat("sangue_vivo")
    tc = N(nt, "ShaderNodeTexCoord"); v = tc.outputs["Object"]
    n = noise(nt, v, None, 2.5, 4, .5, 8.0)
    col = mix(nt, (.035, .001, .002), (.075, .003, .004), n.outputs["Fac"])
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .03
    b.inputs["Coat Weight"].default_value = 1.0; b.inputs["Coat Roughness"].default_value = .02
    b.inputs["Emission Color"].default_value = (.5, .02, .01, 1); b.inputs["Emission Strength"].default_value = 0.0
    rp = N(nt, "ShaderNodeTexWave", wave_type='RINGS'); rp.inputs["Scale"].default_value = 1.6
    rp.inputs["Distortion"].default_value = 3; L(nt, v, rp.inputs[0])
    bump(nt, b, math_(nt, 'ADD', rp.outputs["Fac"], n.outputs["Fac"]), .12, .02)
    return m

def mat_casco(seed=0.0, tinta=(.11, .03, .02)):
    """Tábuas do casco (usa o UV: v = volta do casco, u = comprimento), piche, tinta descascada,
    sal e cracas embaixo e a marca de sangue onde o casco tocava o mar."""
    m, nt, b = new_mat(f"casco{seed}")
    uv = N(nt, "ShaderNodeUVMap"); sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, uv.outputs[0], sep.inputs[0])
    vv = math_(nt, 'MULTIPLY', sep.outputs[1], 13.0)
    fv = math_(nt, 'FRACT', vv); flo = math_(nt, 'FLOOR', vv)
    uu = math_(nt, 'ADD', math_(nt, 'MULTIPLY', sep.outputs[0], 5.0), math_(nt, 'MULTIPLY', flo, .37))
    fu = math_(nt, 'FRACT', uu)
    seam = ramp(nt, [(0, (0, 0, 0)), (.07, (1, 1, 1)), (.93, (1, 1, 1)), (1, (0, 0, 0))]); L(nt, fv, seam.inputs[0])
    butt = ramp(nt, [(0, (0, 0, 0)), (.012, (1, 1, 1))]); L(nt, fu, butt.inputs[0])
    lines = math_(nt, 'MINIMUM', seam.outputs[0], butt.outputs[0])
    tc = N(nt, "ShaderNodeTexCoord"); v = tc.outputs["Object"]
    wv = N(nt, "ShaderNodeTexWave", wave_type='BANDS', bands_direction='X'); wv.inputs["Scale"].default_value = 2
    wv.inputs["Distortion"].default_value = 8; wv.inputs["Detail"].default_value = 5; L(nt, uv.outputs[0], wv.inputs[0])
    wood = ramp(nt, [(.2, (.022, .015, .011)), (.8, (.075, .052, .036))]); L(nt, wv.outputs["Fac"], wood.inputs[0])
    # tábua a tábua varia
    pn = N(nt, "ShaderNodeTexWhiteNoise", noise_dimensions='2D')
    cmb = N(nt, "ShaderNodeCombineXYZ"); L(nt, flo, cmb.inputs[0]); L(nt, math_(nt, 'FLOOR', uu), cmb.inputs[1])
    L(nt, cmb.outputs[0], pn.inputs[0])
    pr = ramp(nt, [(0, (.6, .6, .6)), (1, (1.3, 1.25, 1.2))]); L(nt, pn.outputs["Value"], pr.inputs[0])
    col = mix(nt, wood.outputs[0], pr.outputs[0], 1, 'MULTIPLY')
    pnt = noise(nt, v, None, 1.4, 7, .65, seed)
    ptr = ramp(nt, [(.5, (0, 0, 0)), (.56, (1, 1, 1))]); L(nt, pnt.outputs["Fac"], ptr.inputs[0])
    col = mix(nt, col, tinta, math_(nt, 'MULTIPLY', ptr.outputs[0], .85))
    col = mix(nt, col, (.004, .003, .003), math_(nt, 'SUBTRACT', 1.0, lines))
    col = K.grime(nt, col, v, None, 4.0, .55)
    # marca de sangue/sal perto do chão
    geo = N(nt, "ShaderNodeNewGeometry"); gs = N(nt, "ShaderNodeSeparateXYZ"); L(nt, geo.outputs["Position"], gs.inputs[0])
    zn = noise(nt, v, None, 3, 4, .5, seed + 5)
    zz = math_(nt, 'ADD', gs.outputs[2], math_(nt, 'MULTIPLY', zn.outputs["Fac"], .5))
    tide = ramp(nt, [(.35, (1, 1, 1)), (.75, (0, 0, 0))]); L(nt, zz, tide.inputs[0])
    col = mix(nt, col, (.05, .006, .004), math_(nt, 'MULTIPLY', tide.outputs[0], .9))
    cr = voronoi(nt, v, None, 9, 'F1', seed + 7)
    crr = ramp(nt, [(0, (1, 1, 1)), (.25, (0, 0, 0))]); L(nt, cr.outputs["Distance"], crr.inputs[0])
    band = ramp(nt, [(.55, (0, 0, 0)), (.85, (1, 1, 1)), (1.4, (0, 0, 0))]); L(nt, zz, band.inputs[0])
    craca = math_(nt, 'MULTIPLY', crr.outputs[0], band.outputs[0])
    col = mix(nt, col, (.28, .24, .19), math_(nt, 'MULTIPLY', craca, .8))
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .8
    bump(nt, b, math_(nt, 'ADD', math_(nt, 'MULTIPLY', lines, .6), math_(nt, 'ADD', math_(nt, 'MULTIPLY', wv.outputs["Fac"], .15), craca)), .6, .03)
    return m

def mat_rede():
    m, nt, b = new_mat("rede_pesca")
    tc = N(nt, "ShaderNodeTexCoord"); sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, tc.outputs["Object"], sep.inputs[0])
    def grid(c):
        f = math_(nt, 'FRACT', math_(nt, 'MULTIPLY', c, 9.0))
        r = ramp(nt, [(0, (1, 1, 1)), (.12, (0, 0, 0)), (.88, (0, 0, 0)), (1, (1, 1, 1))]); L(nt, f, r.inputs[0]); return r.outputs[0]
    a = math_(nt, 'MAXIMUM', grid(math_(nt, 'ADD', sep.outputs[0], sep.outputs[1])), grid(math_(nt, 'SUBTRACT', sep.outputs[0], sep.outputs[1])))
    b.inputs["Base Color"].default_value = (.1, .085, .06, 1); b.inputs["Roughness"].default_value = .95
    L(nt, a, b.inputs["Alpha"]); return m

def mat_vapor(dens=.35, brasa=.0):
    m = bpy.data.materials.new(f"vapor{dens}{brasa}"); m.use_nodes = True; nt = m.node_tree
    nt.nodes.clear(); out = N(nt, "ShaderNodeOutputMaterial")
    pv = N(nt, "ShaderNodeVolumePrincipled"); pv.inputs["Color"].default_value = (.55, .45, .4, 1)
    tc = N(nt, "ShaderNodeTexCoord"); sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, tc.outputs["Generated"], sep.inputs[0])
    n = noise(nt, tc.outputs["Object"], None, 1.3, 4, .6, 3.0)
    nr = ramp(nt, [(.35, (0, 0, 0)), (.7, (1, 1, 1))]); L(nt, n.outputs["Fac"], nr.inputs[0])
    fade = ramp(nt, [(0, (1, 1, 1)), (1, (0, 0, 0))]); L(nt, sep.outputs[2], fade.inputs[0])
    # some nas laterais (radial)
    gx = math_(nt, 'SUBTRACT', sep.outputs[0], .5); gy = math_(nt, 'SUBTRACT', sep.outputs[1], .5)
    rr = math_(nt, 'SQRT', math_(nt, 'ADD', math_(nt, 'MULTIPLY', gx, gx), math_(nt, 'MULTIPLY', gy, gy)))
    rad = ramp(nt, [(0, (1, 1, 1)), (.5, (0, 0, 0))]); L(nt, rr, rad.inputs[0])
    d = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', nr.outputs[0], fade.outputs[0]), rad.outputs[0])
    L(nt, math_(nt, 'MULTIPLY', d, dens), pv.inputs["Density"])
    if brasa:
        pv.inputs["Emission Color"].default_value = (1, .35, .08, 1)
        bot = ramp(nt, [(0, (1, 1, 1)), (.35, (0, 0, 0))]); L(nt, sep.outputs[2], bot.inputs[0])
        L(nt, math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', bot.outputs[0], d), brasa), pv.inputs["Emission Strength"])
    L(nt, pv.outputs[0], out.inputs["Volume"])
    return m

def mat_rocha_lava():
    m, nt, b = new_mat("rocha_lava")
    tc = N(nt, "ShaderNodeTexCoord"); v = tc.outputs["Object"]
    n = noise(nt, v, None, .25, 8, .6, 2.0)
    col = mix(nt, (.012, .009, .008), (.05, .03, .022), n.outputs["Fac"])
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .9
    vo = voronoi(nt, v, None, .6, 'DISTANCE_TO_EDGE', 4.0)
    vr = ramp(nt, [(0, (1, 1, 1)), (.025, (0, 0, 0))]); L(nt, vo.outputs["Distance"], vr.inputs[0])
    ln = noise(nt, v, None, .12, 3, .5, 9.0)
    lr = ramp(nt, [(.5, (0, 0, 0)), (.7, (1, 1, 1))]); L(nt, ln.outputs["Fac"], lr.inputs[0])
    b.inputs["Emission Color"].default_value = (1, .33, .06, 1)
    L(nt, math_(nt, 'MULTIPLY', math_(nt, 'ADD', math_(nt, 'MULTIPLY', vr.outputs[0], lr.outputs[0]), math_(nt, 'MULTIPLY', lr.outputs[0], .04)), 9.0), b.inputs["Emission Strength"])
    bump(nt, b, n.outputs["Fac"], .8, .5)
    return m

def mats():
    M = C.mats()
    M.setdefault("crosta_obj", mm("crosta_obj", lambda: mat_crosta(31.0, "crosta_obj")))
    return M

def corda(): return K.mat_solid("corda", (.1, .08, .05))
def osso(): return K.mat_bone("osso_sal", (.42, .38, .31))
def lanterna_mat(): return K.mat_emit("vidro_lampiao", (1, .62, .28), 6)

# ------------------------------------------------------------------ casco virado
def hull_w(t, W_): return W_/2*(max(0., 1 - t**2.2)**.75 if t > 0 else (1 - abs(t)**4*.28))
def hull_k(t, H_): return H_*(max(0., 1 - t**3)**.4 if t > 0 else (1 - abs(t)**5*.18))
def casco_pt(t, a, L_, W_, H_, enterra=.35, tilt=0.0):
    th = a*math.pi/2*1.1; c = math.cos(th)
    x = hull_w(t, W_)*math.sin(th); z = hull_k(t, H_)*math.copysign(abs(c)**.42, c) - enterra
    return Vector((x, t*L_/2, z + x*tilt))
def casco(m, L_=16.0, W_=5.5, H_=4.0, seed=1, tinta=(.11, .03, .02), buraco=None, enterra=.35, tilt=0.0):
    """Casco de navio de madeira virado de quilha para cima, cravado na crosta. buraco=(t0,t1,a0,a1)
    abre um rombo com as costelas à mostra (t em -1..1 ao longo do casco, a em -1..1 na volta)."""
    r = random.Random(seed)
    nt_, na = 40, 22
    vs, fs, uvs = [], [], []
    def pt(t, a): return casco_pt(t, a, L_, W_, H_, enterra, tilt)
    for i in range(nt_ + 1):
        t = -1 + 2*i/nt_
        for j in range(na + 1):
            a = -1 + 2*j/na; vs.append(pt(t, a))
    def ok(i, j):
        if not buraco: return True
        t = -1 + 2*(i + .5)/nt_; a = -1 + 2*(j + .5)/na
        t0, t1, a0, a1 = buraco
        jag = .08*math.sin(t*37 + a*11)
        return not (t0 + jag < t < t1 - jag and a0 + jag < a < a1)
    keep = []
    for i in range(nt_):
        for j in range(na):
            if ok(i, j):
                fs.append((i*(na+1) + j, (i+1)*(na+1) + j, (i+1)*(na+1) + j + 1, i*(na+1) + j + 1)); keep.append((i, j))
    ci = len(vs); vs.append(pt(-1, 0)*.5 + pt(-1, 1)*.5 * 0 + Vector((0, 0, 0)))
    vs[ci] = Vector((0, -L_/2, (hull_k(-1, H_) - enterra)*.45))
    for j in range(na):
        fs.append((ci, j + 1, j)); keep.append((0, j))
    me = bpy.data.meshes.new("casco"); me.from_pydata([tuple(v) for v in vs], [], fs); me.update()
    uvl = me.uv_layers.new(name="UVMap")
    for poly, (i, j) in zip(me.polygons, keep):
        if len(poly.loop_indices) == 3:
            for li in poly.loop_indices: uvl.data[li].uv = (vs[me.loops[li].vertex_index].x*.3, vs[me.loops[li].vertex_index].z*.25)
            continue
        for li, (di, dj) in zip(poly.loop_indices, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            uvl.data[li].uv = ((i + di)/nt_*L_/10, (j + dj)/na*2)
    o = bpy.data.objects.new("casco", me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mm(f"casco{seed}", lambda: mat_casco(float(seed), tinta)))
    for p in o.data.polygons: p.use_smooth = True
    so = o.modifiers.new("sol", 'SOLIDIFY'); so.thickness = .14; so.offset = -1
    wd = m["wood_d"]
    # quilha e roda de proa
    pts = [pt(-1 + 2*k/20, 0) + Vector((0, 0, .12)) for k in range(21)]
    for p, q in zip(pts, pts[1:]): along(wd, p, q, .13, verts=6)
    # cintas (verdugos) ao longo do costado: o que faz ler "navio"
    for a in (-.72, .72, -.45, .45):
        ok_pts = [pt(-1 + 2*k/24, a)*1.012 for k in range(25) if ok(int((1 + (-1 + 2*k/24))/2*nt_ - .01), int((a + 1)/2*na))]
        for p, q in zip(ok_pts, ok_pts[1:]):
            if (p - q).length < L_/8: along(wd, p, q, .07, verts=5)
    # espelho de popa: moldura
    for a in [i/6 - 1 for i in range(13)]:
        pass
    # costelas no rombo (e algumas soltas para fora)
    if buraco:
        t0, t1, a0, a1 = buraco
        for k in range(7):
            t = t0 + (t1 - t0)*(k + .5)/7
            ring = [pt(t, a)*.97 for a in [a0 - .15 + (min(a1, 1.05) - a0 + .3)*q/8 for q in range(9)]]
            for p, q in zip(ring, ring[1:]): along(wd, p, q, .09, verts=5)
        for k in range(5):
            t = r.uniform(t0, t1); a = r.uniform(a0, min(a1, 1))
            p = pt(t, a); box(m["wood"], (p.x*1.02, p.y, p.z), (.3, 1.6, .05), (r.uniform(-30, 30), r.uniform(-40, 40), r.uniform(-20, 20)), .005)
    # tábuas soltas e cracas de ferro (pregos/chapas)
    for k in range(4):
        t = r.uniform(-.8, .8); a = r.choice([-1, 1])*r.uniform(.3, .8); p = pt(t, a)
        box(m["rust"], (p.x*1.01, p.y, p.z), (.05, .7, .4), (0, -math.degrees(math.atan2(p.x, p.z + enterra)), 0), .01)
    # leme torto na popa
    p = pt(-1, 0)
    box(wd, (0, p.y - .5, p.z - 1.2), (.15, 1.2, 2.2), (r.uniform(-10, 10), 0, r.uniform(-25, 25)), .02)
    return o

def casco_morada(m, L_=16.0, W_=5.5, H_=4.0, seed=1, tinta=(.11, .03, .02), cabana=True, portas=2, chamine=True):
    """Casco virado habitado: portas cortadas no costado com luz quente, escada até a quilha,
    barraco de tábuas em cima, chaminé de lata soltando fumaça, lanternas penduradas."""
    o = casco(m, L_, W_, H_, seed, tinta)
    r = random.Random(seed + 100)
    wood, wd, iron = m["wood"], m["wood_d"], m["iron"]
    luz = K.mat_window_lit()
    def lado(t, sx, z):
        # ponto no costado a altura z (busca a)
        best = None
        for k in range(60):
            a = sx*(.4 + k/60*.7)
            p = casco_pt(t, a, L_, W_, H_)
            if best is None or abs(p.z - z) < abs(best[1] - z): best = (p.x, p.z)
        return best[0]
    ts = [-.5, .2, .55][:portas]
    for i, t in enumerate(ts):
        sx = 1 if i % 2 == 0 else -1
        y = t*L_/2; x = lado(t, sx, 1.0)
        # porta: batente, luz de dentro, degrau
        box(luz, (x + sx*.02, y, .95), (.12, 1.0, 1.9), bevel=0)
        for dy in (-.58, .58): box(wd, (x + sx*.1, y + dy, 1.0), (.14, .14, 2.1), bevel=.01)
        box(wd, (x + sx*.1, y, 2.05), (.16, 1.3, .14), bevel=.01)
        box(wood, (x + sx*.45, y, .1), (.7, 1.3, .2), bevel=.01)
        K.point((x + sx*.9, y, 1.2), (1, .5, .2), 70, .3)
        # janelinhas (vigias abertas na tábua)
        for dy in (-2.2, 2.0):
            xw = lado(t + dy/(L_/2), sx, 2.0)
            box(luz, (xw + sx*.04, y + dy, 2.0), (.1, .45, .35), bevel=0)
            box(wd, (xw + sx*.1, y + dy, 2.22), (.12, .6, .08), bevel=0)
        # lanterna pendurada ao lado da porta
        along(iron, (x + sx*.15, y + .9, 2.2), (x + sx*.6, y + .9, 2.25), .015, verts=4)
        cyl(iron, (x + sx*.6, y + .9, 2.0), .07, .05, verts=6)
        cyl(lanterna_mat(), (x + sx*.6, y + .9, 1.85), .06, .22, verts=6)
        K.point((x + sx*.6, y + .9, 1.8), (1, .58, .25), 25, .05)
    # escada de tábuas até a quilha
    sx = -1
    t = -.15; y = t*L_/2
    xs = lado(t, sx, .2)
    n = 12
    for k in range(n):
        f = k/(n - 1); z = .1 + f*(H_ - .35)
        xx = xs*(1 - f) + sx*.3*f + sx*1.4*(1 - f)
        box(wood, (xx, y, z), (.45, 1.1, .06), (0, 0, r.uniform(-4, 4)), .005)
    along(wd, (xs + sx*1.6, y - .6, 0), (sx*.4, y - .6, H_ - .1), .05, verts=5)
    along(wd, (xs + sx*1.6, y + .6, 0), (sx*.4, y + .6, H_ - .1), .05, verts=5)
    # cabana em cima da quilha
    if cabana:
        cy = .35*L_/2; ch = H_ - .4
        box(wood, (0, cy, ch + 1.0), (2.2, 3.0, 2.0), (0, 2, 0), .02)
        box(m["tin"], (.6, cy, ch + 2.25), (1.6, 3.4, .06), (0, 18, 0), .01)
        box(m["tin"], (-.6, cy, ch + 2.25), (1.6, 3.4, .06), (0, -18, 0), .01)
        box(luz, (1.11, cy - .5, ch + 1.2), (.04, .6, .5), bevel=0)
        box(luz, (-1.11, cy + .6, ch + 1.1), (.04, .5, .45), bevel=0)
        K.point((1.6, cy - .5, ch + 1.2), (1, .5, .2), 35, .2)
        for dy in (-1.4, 1.4):
            for dx in (-1, 1): along(wd, (dx*1.05, cy + dy, ch - .2), (dx*1.05, cy + dy, ch + 2.1), .06, verts=5)
    # passarela de tábuas ao longo da quilha
    for k in range(9):
        yy = -L_*.35 + k*L_*.07
        tt = yy/(L_/2)
        z = hull_k(tt, H_) - .35 + .2
        box(wood, (0, yy, z), (1.2, .5, .06), (0, r.uniform(-3, 3), r.uniform(-4, 4)), .005)
    if chamine:
        cx, cyy = .7, -.25*L_/2
        cyl(m["rust"], (cx, cyy, H_ + .6), .18, 2.4, verts=10)
        cyl(m["rust"], (cx, cyy, H_ + 1.9), .28, .25, verts=10, r2=.12)
        for z in (H_ + .1, H_ + 1.0): torus(iron, (cx, cyy, z), .19, .02)
        bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=1.4, depth=7, location=(cx + .4, cyy - .4, H_ + 5.6))
        f = bpy.context.object; f.data.materials.append(mm("fumaca", lambda: mat_vapor(.5, 0)))
    # varal entre a proa e uma estaca
    yb = .75*L_/2
    cyl(wd, (2.6, yb + 1.2, 1.2), .05, 2.4, verts=6)
    along(corda(), (2.6, yb + 1.2, 2.3), (0, yb, H_*.7), .008, verts=4)
    for k in range(4):
        f = (k + 1)/5; p = Vector((2.6, yb + 1.2, 2.3)).lerp(Vector((0, yb, H_*.7)), f)
        col = [(.12, .1, .08), (.09, .015, .01), (.2, .18, .15), (.05, .045, .04)][k]
        oo = box(K.mat_cloth(f"roupa_c{k}", col, 60.0 + k), (p.x, p.y, p.z - .3), (.04, .4, .55), (0, 0, -25), 0)
        displace(oo, .02, .2, seed + k, 2)
    return o

# ------------------------------------------------------------------ vocabulário
def mastro_tombado(m, L_=11.0, seed=1):
    r = random.Random(seed); wd = m["wood_d"]
    along(wd, (0, -L_/2, .18), (0, L_/2, .5), .2, .13, verts=10)
    for y in (-L_*.1, L_*.3):
        yy = y; along(wd, (-2.4, yy + .3, .15), (2.6, yy - .3, .9), .09, .06, verts=8)
    o = box(K.mat_cloth("vela_rasgada", (.16, .13, .09), 61.0), (1.2, -L_*.1 - 1.6, .12), (3.0, 2.6, .04), (0, r.uniform(4, 10), 15), 0)
    displace(o, .25, .9, seed, 4)
    for k in range(3):
        along(corda(), (0, r.uniform(-L_/2, L_/2), .4), (r.uniform(-3, 3), r.uniform(-L_/2, L_/2), .02), .02, verts=4)
    cyl(m["iron"], (0, L_/2 - .4, .5), .25, .2, (90, 0, 0), 10)   # cesto/gávea
    return o

def ancora(m, seed=1, corrente=8.0):
    ir = m["rust"]
    along(ir, (0, 0, -.6), (0, 0, 3.0), .16, .13, verts=10)       # haste (enterrada)
    cyl(ir, (0, 0, 2.6), .1, 2.0, (0, 90, 0), 8)                    # cepo
    torus(ir, (0, 0, 3.25), .3, .07, (90, 0, 0))                   # argola
    for sx in (-1, 1):
        pts = [Vector((sx*1.3*math.sin(a), 0, -.2 + 1.0*(1 - math.cos(a)) - .45)) for a in [i*.25 for i in range(6)]]
        for p, q in zip(pts, pts[1:]): along(ir, p, q, .12, .1, verts=8)
        e = pts[-1]; box(ir, (e.x + sx*.1, 0, e.z + .2), (.5, .14, .7), (0, sx*-35, 0), .02)
    rot = 0
    p0 = Vector((0, 0, 3.25)); prev = p0
    r = random.Random(seed)
    path = [p0 + Vector((0, -.4, -1.0)), Vector((0, -1.6, .05))] + [Vector((math.sin(k*.6)*.8, -1.6 - k*1.0, .05)) for k in range(1, int(corrente))]
    for p in path:
        chain(m["iron"], prev, p, max(3, int((p - prev).length/.22)), .09); prev = p
    return {}

def costela_baleia(m, seed=1):
    """Arco de costelas de baleia: portão do Porto dos Cascos."""
    b = osso(); r = random.Random(seed)
    for sx in (-1, 1):
        pts = [Vector((sx*(2.2 - 2.2*math.sin(a)*.0 - .2*a), 0, 0)) for a in [0]]
        P_ = [Vector((sx*(2.0 - 1.9*(1 - math.cos(a))*.55), 0, 6.0*math.sin(a))) for a in [i*math.pi/2/7 for i in range(8)]]
        for p, q in zip(P_, P_[1:]): along(b, p, q, .28 - p.z*.025, .28 - q.z*.025, verts=10)
        for dy in (-1.4, 1.4):
            P2 = [Vector((sx*(2.6 - 2.3*(1 - math.cos(a))*.55), dy, 4.4*math.sin(a))) for a in [i*math.pi/2/6 for i in range(7)]]
            for p, q in zip(P2, P2[1:]): along(b, p, q, .2, .18, verts=8)
    # lanternas e trapos no arco
    for (x, z) in [(-.9, 5.4), (.9, 5.4)]:
        along(corda(), (x, 0, z), (x, 0, z - .9), .01, verts=4)
        cyl(lanterna_mat(), (x, 0, z - 1.05), .08, .25, verts=6)
        K.point((x, 0, z - 1.1), (1, .58, .25), 60, .1)
    o = box(K.mat_cloth("pano_vermelho_c", (.12, .015, .012), 62.0), (0, 0, 5.75), (2.0, .05, .9), bevel=0); displace(o, .06, .3, seed, 3)
    return {}

def peixe_ossada(m, seed=1, L_=14.0):
    """Ossada de peixe gigante: espinha, raios em leque, crânio de bico e barbatanas."""
    b = osso(); r = random.Random(seed)
    sp = [Vector((math.sin(k*.35)*.6, -L_/2 + k*L_/20, .5 + .3*math.sin(k*.2))) for k in range(21)]
    for p, q in zip(sp, sp[1:]): along(b, p, q, .2, .16, verts=8)
    for k in range(2, 19):
        p = sp[k]; h = 2.4*math.sin(k/20*math.pi) + .4
        for sx in (-1, 1):
            q = p + Vector((sx*h*.8, -.4, h*.75)); q2 = q + Vector((sx*.5, -.3, -h*.9))
            along(b, p, q, .07, .05, verts=5); along(b, q, q2, .05, .02, verts=5)
        along(b, p, p + Vector((0, -.6, h*.6 + .6)), .05, .015, verts=5)
    hd = sp[-1]
    sphere(b, hd + Vector((0, 1.3, .6)), (1.0, 1.6, .9))
    sphere(K.mat_solid("orbita", (0, 0, 0)), hd + Vector((.75, 1.6, .9)), (.25, .3, .25))
    along(b, hd + Vector((0, 2.5, .5)), hd + Vector((.4, 5.2, .2)), .35, .05, verts=8)   # bico/mandíbula
    along(b, hd + Vector((0, 2.4, .1)), hd + Vector((-.2, 4.6, -.1)), .25, .05, verts=8)
    for k in range(9):
        a = (k - 4)*.22
        along(b, sp[0], sp[0] + Vector((math.sin(a)*2.5, -2.5*math.cos(a), .3 + k*.05)), .06, .02, verts=5)
    return {}

def cais(m, L_=14.0, seed=1, quebrado=True):
    """Cais de madeira sobre estacas, com amarras, boias e barris."""
    r = random.Random(seed); wood, wd = m["wood"], m["wood_d"]
    n = int(L_/.32)
    for k in range(n):
        y = k*.32
        if quebrado and y > L_*.78 and r.random() < .45: continue
        z = 1.0 - (max(0, y - L_*.8))**1.5*.12
        box(wood, (r.uniform(-.04, .04), y, z), (2.6 + r.uniform(-.1, .2), .28, .07), (r.uniform(-2, 2), 0, r.uniform(-3, 3)), .005)
    for k in range(int(L_/2.2) + 1):
        y = k*2.2
        for sx in (-1, 1):
            cyl(wd, (sx*1.25, y, .55), .14, 1.5 + (.6 if k % 2 else 0), (r.uniform(-4, 4), r.uniform(-4, 4), 0), 8)
        box(wd, (0, y, .8), (2.6, .15, .15), bevel=.01)
    for sx in (-1, 1):
        for k in range(int(L_/2.2)):
            y = k*2.2; along(corda(), (sx*1.25, y, 1.3), (sx*1.25, y + 2.2, 1.3), .015, verts=4)
    return {}

def boia(m, seed=1):
    r = random.Random(seed)
    red = K.mat_metal("boia_verm", (.16, .02, .012), .7, 7.0)
    cyl(red, (0, 0, .55), .55, 1.1, (r.uniform(10, 30), 0, 0), 14, r2=.25)
    cyl(m["rust"], (0, 0, 1.25), .06, .7, verts=6)
    for k in range(4):
        a = k*math.pi/2; along(m["iron"], (math.cos(a)*.25, math.sin(a)*.25, 1.0), (0, 0, 1.6), .02, verts=4)
    torus(m["iron"], (0, 0, .7), .5, .04)
    return {}

def rede_pesca(m, seed=1):
    r = random.Random(seed)
    for k in range(2):
        o = box(mm("rede", mat_rede), (r.uniform(-.5, .5), r.uniform(-.5, .5), .12 + k*.1), (2.6, 2.0, .02), (0, 0, r.uniform(0, 90)), 0)
        displace(o, .25, .5, seed + k, 4)
    for k in range(5):
        sphere(K.mat_cloth("cortica", (.12, .09, .05), 63.0), (r.uniform(-1.2, 1.2), r.uniform(-1, 1), .15), (.12, .12, .1), segs=8)
    return {}

def estacas_rede(m, seed=1):
    """Estacas com rede de pesca estendida para secar (o varal do porto)."""
    r = random.Random(seed); wd = m["wood_d"]
    for x in (-2.0, 0, 2.0):
        cyl(wd, (x, 0, 1.2), .06, 2.4, (r.uniform(-6, 6), r.uniform(-6, 6), 0), 6)
    o = box(mm("rede", mat_rede), (0, 0, 1.6), (4.0, .02, 1.5), bevel=0); displace(o, .12, .4, seed, 4)
    for k in range(4):
        sphere(K.mat_cloth("cortica", (.12, .09, .05), 63.0), (-1.6 + k*1.1, 0, 2.3), (.1, .1, .08), segs=8)
    return {}

def barrica(m, seed=1):
    r = random.Random(seed)
    for k in range(r.randint(2, 4)):
        x, y = r.uniform(-.7, .7), r.uniform(-.7, .7)
        if r.random() < .3:
            cyl(m["wood"], (x, y, .3), .3, .9, (90, 0, r.uniform(0, 180)), 16)
        else:
            cyl(m["wood"], (x, y, .45), .3, .9, verts=16)
            for z in (.12, .78): torus(m["iron"], (x, y, z), .305, .015)
    return {}

def farol_cego(m, seed=1):
    """O Farol Cego: torre de pedra com listras ferrugem, a lanterna vendada com um pano
    e tábuas pregadas; ninguém sabe quem apagou a luz."""
    st = K.mat_stone("pedra_farol", (.16, .14, .12), (.06, .05, .045), 1.4, 0.0)
    stripe = K.mat_stone("pedra_farol_rubra", (.13, .035, .02), (.05, .012, .01), 1.4, 0.0, seed=4.0)
    H = 10.0
    # rochedo
    for k, (x, y, s) in enumerate([(0, 0, 3.6), (2.0, -1.5, 2.2), (-2.4, 1.0, 2.6), (1.0, 2.6, 1.8)]):
        o = sphere(K.mat_stone("rochedo", (.06, .03, .025), (.02, .012, .01), 2.0, 0.0), (x, y, -.3), (s, s*.9, s*.45), segs=16)
        displace(o, .5, 1.2, seed + k, 2)
    nseg = 6
    for k in range(nseg):
        z0 = 1.2 + k*(H/nseg); r0 = 2.0 - k*.17
        cyl(stripe if k % 2 else st, (0, 0, z0 + H/nseg/2), r0, H/nseg, verts=8, smooth=False, r2=r0 - .17)
    zt = 1.2 + H
    cyl(m["iron"], (0, 0, zt + .1), 1.6, .2, verts=8, smooth=False)
    for k in range(16):
        a = k/16*2*math.pi; cyl(m["iron"], (math.cos(a)*1.5, math.sin(a)*1.5, zt + .55), .025, .9, verts=4)
    torus(m["iron"], (0, 0, zt + 1.0), 1.5, .03)
    cyl(K.mat_solid("vidro_morto", (.01, .012, .012), .3, .08), (0, 0, zt + 1.2), .95, 2.0, verts=8, smooth=False)
    for k in range(8):
        a = (k + .5)/8*2*math.pi; cyl(m["iron"], (math.cos(a)*.97, math.sin(a)*.97, zt + 1.2), .05, 2.0, verts=4)
    # a venda: faixa de pano vermelho amarrada em volta da lanterna, pontas soltas ao vento
    vend = K.mat_cloth("venda", (.16, .02, .015), 64.0)
    o = cyl(vend, (0, 0, zt + 1.25), 1.02, .65, verts=16); displace(o, .05, .3, seed, 2)
    for dz in (0, -.2):
        o = box(vend, (1.4, -.6, zt + 1.1 + dz), (1.6, .05, .25), (0, 25, -20), 0); displace(o, .06, .3, seed + 3, 3)
    for k in range(5):   # tábuas pregadas
        a = (k*.31 + .2)*2*math.pi
        box(m["wood_d"], (math.cos(a)*1.0, math.sin(a)*1.0, zt + 1.6 + (k % 2)*.2), (.08, .9, .14), (k*9 - 18, 0, math.degrees(a)), .005)
    cyl(m["rust"], (0, 0, zt + 2.4), 1.1, .5, verts=8, r2=.2, smooth=False)
    cyl(m["rust"], (0, 0, zt + 2.85), .08, .5, verts=6)
    # porta e janelinhas mortas
    box(K.mat_solid("buraco", (.005, .004, .004)), (1.95, 0, 2.2), (.2, 1.0, 1.9), (0, 0, 0), 0)
    for k in range(3):
        a = .9 + k*1.9; z = 4.5 + k*3.2
        box(K.mat_solid("buraco", (.005, .004, .004)), (math.cos(a)*(1.9 - z*.03), math.sin(a)*(1.9 - z*.03), z), (.2, .5, .7), (0, 0, math.degrees(a)), 0)
    # gaivotas-carniça: ninhos de gravetos na galeria
    for k in range(3):
        a = k*2.1 + .5
        o = sphere(m["wood_d"], (math.cos(a)*1.3, math.sin(a)*1.3, zt + .3), (.4, .4, .15), segs=8); displace(o, .1, .1, seed + k, 1)
    return {}

def montanha(m, seed=1):
    """A montanha que ardeu e caiu no mar, ainda em chamas no horizonte."""
    bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=30, radius2=5, depth=34, location=(0, 0, 17))
    o = bpy.context.object; o.data.materials.append(mm("rocha_lava", mat_rocha_lava))
    s = o.modifiers.new("sub", 'SUBSURF'); s.levels = s.render_levels = 3; s.subdivision_type = 'SIMPLE'
    t = bpy.data.textures.new("dt_mont", 'CLOUDS'); t.noise_scale = 6; t.noise_depth = 3
    d = o.modifiers.new("disp", 'DISPLACE'); d.texture = t; d.strength = 6; d.texture_coords = 'GLOBAL'
    return o

def vapor(m, seed=1, h=4.0, r_=.7, brasa=1.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=r_, depth=h, location=(0, 0, h/2))
    f = bpy.context.object; f.data.materials.append(mm(f"vapor_b{brasa}", lambda: mat_vapor(.45, 2.0*brasa)))
    return {}

def passarela(m, L_=6.0, seed=1, z0=3.5, z1=3.5):
    """Passarela de corda e tábua entre dois cascos."""
    r = random.Random(seed); n = int(L_/.35)
    for k in range(n):
        f = k/(n - 1); z = z0*(1 - f) + z1*f - math.sin(f*math.pi)*.5
        box(m["wood"], (r.uniform(-.03, .03), -L_/2 + f*L_, z), (1.0, .26, .05), (0, 0, r.uniform(-5, 5)), .004)
    for sx in (-1, 1):
        pts = [Vector((sx*.55, -L_/2 + f*L_, (z0*(1 - f) + z1*f) - math.sin(f*math.pi)*.45 + .9)) for f in [i/8 for i in range(9)]]
        for p, q in zip(pts, pts[1:]): along(corda(), p, q, .015, verts=4)
    for k in range(3):
        f = (k + 1)/4; z = z0*(1 - f) + z1*f - math.sin(f*math.pi)*.5
        along(corda(), (0, -L_/2 + f*L_, z + .9), (0, -L_/2 + f*L_, z + .5), .01, verts=4)
        cyl(lanterna_mat(), (0, -L_/2 + f*L_, z + .4), .06, .18, verts=6)
        K.point((0, -L_/2 + f*L_, z + .35), (1, .58, .25), 18, .05)
    return {}

def entulho_naval(m, seed=1):
    """Tábuas de casco, caixotes e um pedaço de corrente jogados na crosta."""
    r = random.Random(seed)
    for k in range(6):
        box(m["wood_d"], (r.uniform(-1.5, 1.5), r.uniform(-1.5, 1.5), .05), (.25, r.uniform(1.2, 2.6), .06), (r.uniform(-8, 8), r.uniform(-8, 8), r.uniform(0, 180)), .005)
    box(m["wood"], (r.uniform(-1, 1), r.uniform(-1, 1), .25), (.5, .5, .5), (0, 0, r.uniform(0, 90)), .02)
    chain(m["iron"], (-1.2, .4, .05), (1.4, -.3, .05), 12, .07)
    return {}

# ------------------------------------------------------------------ cena
C.iniciar(ceu=(.03, .012, .008), poeira=(.2, .16, .13), luzes=False)
C.sol((1.0, .42, .16), 1.3, (64, 0, -135), .08, "montanha")      # contraluz da montanha (do fundo)
C.sol((.62, .58, .55), .55, (48, 0, -10), .2, "sal")              # luz fria de sal, da frente
C.sol((.5, .25, .2), .25, (80, 0, 100), .5, "fill")
r = random.Random(7)

# horizonte: a montanha em chamas
P(montanha, -14, 52, 0, 1.0, chave="montanha")
for (u, v, e) in [(-14, 28, 3500), (4, 33, 2000), (-30, 30, 2000)]:
    x, y = W(u, v); C.ponto((x, y, 6), (1, .38, .1), e, 4)

# destaques do chão: sal e poças vivas de sangue
sal = mm("sal", mat_sal); poca = mm("poca", mat_poca)
for (u, v, rr, sd) in [(14, -8, 5.0, 3), (-24, 16, 4.0, 5), (6, 20, 3.0, 8)]:
    x, y = W(u, v); C.mancha(sal, (x, y), rr, seed=sd, irregular=.5, nome="sal")
for (u, v, rr, sd) in [(5, -13, 2.6, 11), (-11, -22, 3.2, 12), (19, 3, 2.0, 13), (-19, 7, 2.4, 14), (-3, -8, 1.3, 15), (22, -20, 2.2, 16), (-24, -10, 1.8, 17)]:
    x, y = W(u, v); C.mancha(poca, (x, y), rr, seed=sd, z=.012, irregular=.55, nome="poca")

# Porto dos Cascos (plano médio): cascos habitados ligados por passarelas
P(lambda m: casco_morada(m, 18, 6.2, 4.6, 1, (.11, .03, .02), True, 3, True), -5, 7, 0, chave="morada1")
P(lambda m: casco_morada(m, 16, 5.6, 4.2, 2, (.02, .018, .016), True, 2, True), 6, 10, 90, chave="morada2")
P(lambda m: casco_morada(m, 14, 5.0, 3.8, 3, (.2, .17, .13), False, 2, False), 9, 2, 20, chave="morada3")
P(lambda m: casco_morada(m, 15, 5.2, 4.0, 4, (.06, .05, .04), True, 2, True), -14, 14, 70, chave="morada4")
P(lambda m: passarela(m, 7.5, 1, 4.3, 3.9), .5, 9.5, 45, chave="pass1")
P(lambda m: passarela(m, 6.0, 2, 3.8, 3.6), 7.5, 5.5, -40, chave="pass2")
P(lambda m: passarela(m, 6.5, 3, 4.0, 4.3), -10, 11, 15, chave="pass3")
# o Farol Cego, no fundo, em cima do rochedo
P(farol_cego, 16, 10, 20, chave="farol")
# portão de costelas de baleia na entrada do porto
P(costela_baleia, -1, -3, 45, chave="costela")
# guindaste de porto e o cais que entra no "mar"
PK("guindaste_sucata", -9, -3, 160, 1.1)
P(lambda m: cais(m, 15, 1), -6, -4, 90+45+20, chave="cais1")
P(lambda m: cais(m, 9, 2), 13, -4, -60, chave="cais2")
# vida do porto: fogo, barris, caixas, redes, varal
PK("tonel_fogo", 1.5, -6.5); PK("tonel_fogo", -4.5, 0.5); PK("fogueira", 3.5, 3.0)
PK("caixas", -3.5, -6.5, 20); PK("caixas", 3, -1.5, 70); PK("barris", 4.5, -5.5, 10)
PK("lanterna_procissao", -3.2, -2.5); PK("lanterna_procissao", 2.8, -4.0, 180)
PK("poste_gas", 11.5, -1.0, 0); PK("poste_gas_quebrado", -7, -8.5, 40)
for k, (u, v, rt) in enumerate([(-1, 1.5, 30), (13, 7, -20), (-16, 4, 60)]):
    P(lambda m, k=k: estacas_rede(m, k), u, v, rt, chave=f"estacas{k}")
for k, (u, v) in enumerate([(5.5, -2.5), (-6.5, -1), (12, -3), (-12, 7.5), (2, 14)]):
    P(lambda m, k=k: barrica(m, k + 1), u, v, r.uniform(0, 360), chave=f"barrica{k%3}")
for k, (u, v) in enumerate([(0, -9.5), (8.5, -7.5), (-13, -1)]):
    P(lambda m, k=k: rede_pesca(m, k + 2), u, v, r.uniform(0, 360), chave=f"rede{k%2}")
PK("varal_roupas", 3.5, 6.0, 40)
# Cemitério de Quilhas: cascos mortos, com rombos, em toda a costa
P(lambda m: casco(m, 17, 6.0, 4.4, 11, (.03, .025, .02), (-.3, .45, -.2, 1.2)), 22, -6, 60, chave="morto1")
P(lambda m: casco(m, 14, 5.0, 3.6, 12, (.12, .03, .02), (-.7, -.1, -1.2, .3), tilt=.15), -21, -3, -30, chave="morto2")
P(lambda m: casco(m, 12, 4.4, 3.2, 13, (.2, .17, .13), (.1, .7, -.5, 1.2)), 17, -20, 10, chave="morto3")
P(lambda m: casco(m, 19, 6.4, 4.8, 14, (.03, .025, .02), (-.5, .2, .1, 1.2), enterra=1.2), -22, 22, 100, chave="morto4")
P(lambda m: casco(m, 15, 5.2, 4.0, 15, (.11, .03, .02), (.2, .8, -1.2, -.2), enterra=.8), 26, 14, 30, chave="morto5")
P(lambda m: casco(m, 13, 4.6, 3.4, 16, (.06, .05, .04), (-.6, 0, -.3, 1.2), enterra=.9), 1, 24, -50, chave="morto6")
P(lambda m: casco(m, 10, 3.8, 2.8, 17, (.12, .03, .02), (-.2, .5, -1.2, .2), enterra=.6), -26, -18, 120, chave="morto7")
P(lambda m: casco(m, 16, 5.6, 4.2, 18, (.2, .17, .13), None, enterra=1.4), 12, 28, 80, chave="morto8")
# mastros tombados, âncoras e correntes
P(lambda m: mastro_tombado(m, 12, 1), -14, -9, 15, chave="mastro1")
P(lambda m: mastro_tombado(m, 10, 2), 24, 4, 100, chave="mastro2")
P(lambda m: mastro_tombado(m, 9, 3), -6, 18, -40, chave="mastro3")
P(lambda m: ancora(m, 1, 9), -3, -17, 30, chave="ancora1")
P(lambda m: ancora(m, 2, 6), 21, -12, -70, 1.2, z=-.5, chave="ancora2")
P(lambda m: ancora(m, 3, 5), -18, 18, 120, .9, chave="ancora3")
# ossada de peixe gigante no primeiro plano
P(lambda m: peixe_ossada(m, 1, 15), 9, -19, 70, chave="peixe")
P(lambda m: peixe_ossada(m, 2, 10), -27, 9, -20, .8, chave="peixe2")
# boias, entulho e barris espalhados
for k, (u, v) in enumerate([(-8, -14), (15, -14), (-17, 2), (26, -12), (-4, -24), (19, 9), (-25, -6)]):
    P(lambda m, k=k: boia(m, k), u, v, r.uniform(0, 360), r.uniform(.8, 1.1), z=-.15, chave=f"boia{k%3}")
for k, (u, v) in enumerate([(4, -23), (-15, -18), (14, -10), (-9, 22), (25, -26), (-22, 3)]):
    P(lambda m, k=k: entulho_naval(m, k), u, v, r.uniform(0, 360), chave=f"entulho{k%3}")
for k, (u, v) in enumerate([(-12, -11), (18, -16), (-25, 13), (9, -12)]):
    P(lambda m, k=k: barrica(m, k + 5), u, v, r.uniform(0, 360), chave=f"barrica{k%3 + 3}")
for k in range(6):
    PK("ossos_espalhados", r.uniform(-26, 26), r.uniform(-26, 10), r.uniform(0, 360))
# vapor saindo das fendas
for k, (u, v, h) in enumerate([(-8, -18, 4.5), (12, -15, 3.5), (-18, -4, 5), (20, -8, 4), (-2, -12, 3), (-22, 12, 5), (14, 18, 5), (24, -22, 4), (-12, -26, 3.5)]):
    P(lambda m, h=h, k=k: vapor(m, k, h, .7 + (k % 3)*.25, 1.0), u, v, 0, chave=f"vapor{k}")

C.chao(mat_crosta(1.0), 180, ondula=.18, seed=4)
cx, cy = W(0, 5)
C.render(OUT, centro=(cx, cy), largura=56, W=960 if Q else 1920, H=540 if Q else 1080, samples=16 if Q else 96)
