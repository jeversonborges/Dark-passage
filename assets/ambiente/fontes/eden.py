# ================================================================ NOVO ÉDEN · kit "Gênesis" (revisão de 15/10/2026)
# Pedido do Jefin: "revisando Novo Éden, deixando lindo, exuberante, com referências bíblicas do Éden".
# O jardim é o único lugar do mundo onde ainda há cor: copas verdes de verdade, flores, musgo, pedras cobertas,
# água limpa. A luz vem de lanternas de seiva (âmbar, a Enxertia) e da água (ciano, o Jordão limpo). Regra do
# estilo: 1 cor emissiva por objeto. Tudo procedural; usa o vocabulário de tronco/galho da Mata do Granizo.
# Registrado em assets.REG por `import eden` no fim de assets.py (render: render_assets.py <brutos> <nomes>).
import bpy, math, random
from mathutils import Vector
import kit as K
from kit import box, cyl, sphere, along, torus, displace, crumble, flame, point, N, L, ramp, mix, math_, noise, voronoi
import assets as A
from assets import REG, rnd

def _mata():
    return A._ne()
def tubo(*a, **k): return _mata()["tubo"](*a, **k)
def galho(*a, **k): return _mata()["galho"](*a, **k)
def lascas(*a, **k): return _mata()["lascas"](*a, **k)

_MT = {}
def _c(key, fn):
    if key not in _MT or _MT[key].name not in bpy.data.materials: _MT[key] = fn()
    return _MT[key]
def limpar(): _MT.clear(); _FOLHA.clear()

AMBAR = (1, .58, .18)       # seiva / lanternas da Enxertia
LUME = (.1, .85, 1.0)       # água limpa (o Jordão) e as campânulas
AMARGO = (.35, 1.0, .25)    # só na Árvore do Conhecimento

# ---------------------------------------------------------------- materiais
def folha_eden(k=0):
    """Folha de copa: verdes vivos (o Éden tem cor), umas poucas douradas; sem emissão."""
    def f():
        m, nt, b = K.new_mat(f"folha_eden_{k}")
        oi = N(nt, "ShaderNodeObjectInfo")
        if k == 0:    # copa comum
            r = ramp(nt, [(0, (.008, .035, .007)), (.45, (.025, .085, .018)), (.8, (.055, .15, .035)), (.92, (.11, .17, .04)), (1, (.26, .16, .04))])
        elif k == 1:  # figueira / folhas grandes, mais escuras e azuladas
            r = ramp(nt, [(0, (.006, .04, .015)), (.5, (.02, .08, .03)), (.9, (.05, .13, .05)), (1, (.13, .11, .035))])
        else:         # salgueiro: verde prateado
            r = ramp(nt, [(0, (.03, .08, .035)), (.5, (.07, .14, .06)), (1, (.14, .2, .1))])
        L(nt, oi.outputs["Random"], r.inputs[0])
        L(nt, r.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .5
        try: b.inputs["Subsurface Weight"].default_value = .3; b.inputs["Subsurface Radius"].default_value = (.1, .3, .05)
        except KeyError: pass
        return m
    return _c(("folha", k), f)

def folhagem_eden(k=0):
    """Material de moita/samambaia: verde com nervuras claras e manchas de musgo."""
    def f():
        m, nt, b = K.new_mat(f"folhagem_eden_{k}")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 3.0, 6, .6, 40.0 + k)
        vo = voronoi(nt, v, None, 16, 'DISTANCE_TO_EDGE', 41.0 + k)
        base = [(.25, (.015, .06, .015)), (.55, (.045, .13, .035)), (.85, (.1, .22, .07))]
        if k == 1: base = [(.25, (.02, .05, .01)), (.55, (.06, .11, .025)), (.85, (.14, .19, .05))]   # samambaia amarelada
        r = ramp(nt, base); L(nt, n.outputs["Fac"], r.inputs[0])
        nerv = ramp(nt, [(0, (1, 1, 1)), (.03, (0, 0, 0))]); L(nt, vo.outputs["Distance"], nerv.inputs[0])
        col = mix(nt, r.outputs[0], (.2, .3, .12), math_(nt, 'MULTIPLY', nerv.outputs[0], .5))
        L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .6
        try: b.inputs["Subsurface Weight"].default_value = .2
        except KeyError: pass
        K.bump(nt, b, nerv.outputs[0], .5, .02)
        return m
    return _c(("folhagem", k), f)

def casca_viva(seed=0):
    return _c(("casca", seed), lambda: K.mat_wood(f"casca_eden_{seed}", (.07, .052, .034), seed*.37))
def casca_musgo(seed=0):
    """Tronco com musgo nas faces de cima (as árvores velhas do jardim)."""
    def f():
        m, nt, b = K.new_mat(f"casca_musgo_{seed}")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 2.2, 7, .6, 50 + seed)
        wv = N(nt, "ShaderNodeTexWave", wave_type='BANDS', bands_direction='Z'); wv.inputs["Scale"].default_value = 9
        wv.inputs["Distortion"].default_value = 3.5; L(nt, v, wv.inputs["Vector"])
        base = ramp(nt, [(.3, (.03, .022, .015)), (.6, (.075, .055, .035)), (.85, (.13, .1, .065))])
        L(nt, math_(nt, 'ADD', math_(nt, 'MULTIPLY', wv.outputs["Fac"], .5), math_(nt, 'MULTIPLY', n.outputs["Fac"], .5)), base.inputs[0])
        geo = N(nt, "ShaderNodeNewGeometry"); ns = N(nt, "ShaderNodeSeparateXYZ"); L(nt, geo.outputs["Normal"], ns.inputs[0])
        up = ramp(nt, [(.2, (0, 0, 0)), (.75, (1, 1, 1))]); L(nt, ns.outputs[2], up.inputs[0])
        mn = noise(nt, v, None, 4.5, 4, .55, 51 + seed)
        mr = ramp(nt, [(.42, (0, 0, 0)), (.6, (1, 1, 1))]); L(nt, mn.outputs["Fac"], mr.inputs[0])
        musgo = math_(nt, 'MULTIPLY', math_(nt, 'ADD', math_(nt, 'MULTIPLY', up.outputs[0], .7), .3), mr.outputs[0])
        col = mix(nt, base.outputs[0], (.05, .12, .03), musgo)
        L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .85
        K.bump(nt, b, math_(nt, 'ADD', wv.outputs["Fac"], math_(nt, 'MULTIPLY', mr.outputs[0], .6)), .6, .05)
        return m
    return _c(("casca_musgo", seed), f)

def pedra_musgo(seed=0, moss=.9):
    """Pedra cinza-clara com musgo verde grosso assentado nas faces de cima e líquen claro."""
    def f():
        m, nt, b = K.new_mat(f"pedra_eden_{seed}_{moss}")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n1 = noise(nt, v, None, 2.4, 8, .6, 80 + seed); n2 = noise(nt, v, None, 12, 4, .5, 81 + seed)
        r = ramp(nt, [(.3, (.035, .034, .032)), (.6, (.08, .078, .07)), (.85, (.14, .135, .12))]); L(nt, n1.outputs["Fac"], r.inputs[0])
        col = mix(nt, r.outputs[0], n2.outputs["Color"], .15, 'OVERLAY')
        lq = voronoi(nt, v, None, 5, 'F1', 82 + seed)
        lr = ramp(nt, [(0, (1, 1, 1)), (.12, (0, 0, 0))]); L(nt, lq.outputs["Distance"], lr.inputs[0])
        col = mix(nt, col, (.22, .23, .16), math_(nt, 'MULTIPLY', lr.outputs[0], .5))
        geo = N(nt, "ShaderNodeNewGeometry"); ns = N(nt, "ShaderNodeSeparateXYZ"); L(nt, geo.outputs["Normal"], ns.inputs[0])
        up = ramp(nt, [(-.1, (0, 0, 0)), (.6, (1, 1, 1))]); L(nt, ns.outputs[2], up.inputs[0])
        mn = noise(nt, v, None, 3.5, 5, .6, 83 + seed)
        mr = ramp(nt, [(.38, (0, 0, 0)), (.55, (1, 1, 1))]); L(nt, mn.outputs["Fac"], mr.inputs[0])
        mg = math_(nt, 'MULTIPLY', math_(nt, 'MULTIPLY', up.outputs[0], mr.outputs[0]), moss)
        mc = mix(nt, (.02, .06, .012), (.05, .11, .025), n2.outputs["Fac"])
        col = mix(nt, col, mc, mg)
        L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .88
        K.bump(nt, b, math_(nt, 'ADD', math_(nt, 'MULTIPLY', n1.outputs["Fac"], .6), math_(nt, 'MULTIPLY', mg, .8)), .7, .05)
        return m
    return _c(("pedra", seed, moss), f)
def musgo_mat():
    def f():
        m, nt, b = K.new_mat("musgo_eden")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 9, 6, .6, 60)
        r = ramp(nt, [(.3, (.02, .06, .015)), (.6, (.05, .12, .03)), (.85, (.1, .19, .06))]); L(nt, n.outputs["Fac"], r.inputs[0])
        L(nt, r.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .95
        K.bump(nt, b, n.outputs["Fac"], .8, .03); return m
    return _c("musgo", f)
def seiva(): return _c("seiva", lambda: K.mat_emit("seiva_ambar", AMBAR, 9))
def lume(): return _c("lume", lambda: K.mat_emit("lume_ciano", LUME, 12))
def agua_limpa():
    """Água da Nascente: superfície lisa que acende em ciano (a cor do Jordão limpo)."""
    def f():
        m, nt, b = K.new_mat("agua_limpa")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 6, 5, .5, 70)
        L(nt, mix(nt, (.02, .1, .12), (.05, .25, .3), n.outputs["Fac"]), b.inputs["Base Color"])
        b.inputs["Roughness"].default_value = .08; b.inputs["Emission Color"].default_value = (*LUME, 1)
        L(nt, math_(nt, 'MULTIPLY', n.outputs["Fac"], 1.6), b.inputs["Emission Strength"])
        K.bump(nt, b, n.outputs["Fac"], .3, .01); return m
    return _c("agua", f)
def flor_mat(cor):
    return _c(("flor", cor), lambda: K.mat_solid(f"flor_{int(cor[0]*99)}_{int(cor[1]*99)}", cor, 0, .55))
def petala_branca(): return flor_mat((.75, .72, .6))
def petala_ouro(): return flor_mat((.8, .55, .12))
def petala_rosa(): return flor_mat((.6, .22, .3))
def fruto_ouro(): return _c("fruto", lambda: K.mat_solid("fruto_ouro", (.5, .3, .06), 0, .3, emit=(1, .62, .15), strength=3.0))
def fruto_amargo(): return _c("fruto_am", lambda: K.mat_solid("fruto_amargo", (.05, .2, .03), 0, .25, emit=AMARGO, strength=1.6))
def cogumelo_mat(): return _c("cogu", lambda: K.mat_solid("cogumelo_eden", (.3, .22, .12), 0, .6))

# ---------------------------------------------------------------- folhas instanciadas
_FOLHA = {}
def folha_obj(k=0, tam=1.0):
    """Cartão de folha (gota) para instanciar nas copas; k = material; tam = escala."""
    key = (k, tam)
    if key in _FOLHA and _FOLHA[key].name in bpy.data.objects: return _FOLHA[key]
    s = .26*tam
    vs = [(0, 0, 0), (s*.4, s*.22, 0), (s*.75, s*.14, 0), (s, 0, 0), (s*.75, -s*.14, 0), (s*.4, -s*.22, 0)]
    me = bpy.data.meshes.new(f"folha_e{k}"); me.from_pydata(vs, [], [(0, 1, 2, 3, 4, 5)]); me.update()
    o = bpy.data.objects.new(f"folha_e{k}", me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(folha_eden(k)); o.hide_render = True
    _FOLHA[key] = o; return o

def copa(c, raio, rr, k=0, n=None, dens=1.0, tam=1.0, achatado=.78):
    """Copa: volumes escuros + centenas de folhas instanciadas por cima (fica cheia, não um balão)."""
    for i in range(n or rr.randint(7, 10)):
        a = rr.uniform(0, 6.28); d = rr.uniform(.15, .85)*raio
        p = (c[0] + math.cos(a)*d, c[1] + math.sin(a)*d, c[2] + rr.uniform(-.45, .4)*raio*(1 - d/raio*.5))
        s = raio*rr.uniform(.38, .6)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=s, location=p)
        o = bpy.context.object; o.scale = (1, 1, achatado*rr.uniform(.9, 1.1))
        o.data.materials.append(K.mat_solid("miolo_copa_eden", (.008, .03, .01), 0, .9))
        displace(o, s*.35, 1.4, rr.randint(0, 999), 1)
        ps = o.modifiers.new("folhas", 'PARTICLE_SYSTEM').particle_system
        st = ps.settings; st.type = 'HAIR'; st.use_advanced_hair = True; st.count = int((700*s*s + 120)*dens)
        st.hair_length = 1.0; st.render_type = 'OBJECT'; st.instance_object = folha_obj(k, tam)
        st.particle_size = rr.uniform(1.0, 1.5)*min(1.5, .6 + s*.45); st.size_random = .5
        st.use_rotations = True; st.rotation_mode = 'NOR'; st.phase_factor_random = 2.0; st.rotation_factor_random = .7
        st.emit_from = 'FACE'; st.use_emit_random = True
        ps.seed = rr.randint(0, 9999)

def raizes(mat, r, h0, rr, n=5, comp=2.2):
    for k in range(n):
        a = k/n*2*math.pi + rr.uniform(-.3, .3)
        tubo(mat, [(math.cos(a)*r*.6, math.sin(a)*r*.6, h0 + .45), (math.cos(a)*r*1.5, math.sin(a)*r*1.5, h0 + .1),
                   (math.cos(a)*r*comp, math.sin(a)*r*comp, h0 - .1)], [r*.38, r*.22, r*.07], 7, rr.randint(0, 999), .15)

def lanterna_seiva(p, rr, corda=1.2):
    """Lanterna de seiva da Enxertia pendurada por uma corda (a luz âmbar do jardim)."""
    lat = K.mat_brass(); hang = (p[0], p[1], p[2] - corda)
    along(K.mat_cloth("corda", (.09, .075, .05), 1.0), p, hang, .012, verts=4)
    cyl(lat, (hang[0], hang[1], hang[2] - .02), .1, .05, verts=10)
    for k in range(4):
        a = k/4*2*math.pi; along(lat, (hang[0] + math.cos(a)*.08, hang[1] + math.sin(a)*.08, hang[2] - .04), (hang[0] + math.cos(a)*.07, hang[1] + math.sin(a)*.07, hang[2] - .3), .008, verts=4)
    sphere(seiva(), (hang[0], hang[1], hang[2] - .17), (.085, .085, .12), segs=10)
    cyl(lat, (hang[0], hang[1], hang[2] - .31), .07, .03, verts=10)
    point((hang[0], hang[1], hang[2] - .4), AMBAR, 28, .1)

def musgo_pe(rr, r=.9, n=5, z=0.0):
    for k in range(n):
        a = rr.uniform(0, 6.28); d = rr.uniform(.2, 1.0)*r
        o = sphere(musgo_mat(), (math.cos(a)*d, math.sin(a)*d, z + .02), (rr.uniform(.2, .45), rr.uniform(.15, .35), .06), segs=10)
        displace(o, .03, .25, rr.randint(0, 99), 1)

def florzinhas(rr, c, r, n, mats, z=.1, tam=.035):
    for k in range(n):
        a = rr.uniform(0, 6.28); d = rr.uniform(0, r)
        p = (c[0] + math.cos(a)*d, c[1] + math.sin(a)*d, c[2] + z + rr.uniform(0, .08))
        sphere(rr.choice(mats), p, (tam, tam, tam*.6), segs=8)

def cogumelos(rr, c, n=4, tam=1.0):
    for k in range(n):
        a = rr.uniform(0, 6.28); d = rr.uniform(0, .35)*tam; h = rr.uniform(.08, .2)*tam
        p = (c[0] + math.cos(a)*d, c[1] + math.sin(a)*d, c[2])
        cyl(K.mat_solid("talo_cogu", (.3, .27, .2), 0, .7), (p[0], p[1], p[2] + h/2), .018*tam, h, verts=7)
        o = sphere(cogumelo_mat(), (p[0], p[1], p[2] + h), (.07*tam*rr.uniform(.8, 1.3), .07*tam*rr.uniform(.8, 1.3), .04*tam), segs=10)

# ---------------------------------------------------------------- vegetação
def arvore_eden(seed, h=8.0, r=.42, lanterna=True, k=0):
    """Árvore do jardim: tronco velho com musgo, raízes expostas, copa verde cheia; lanterna de seiva num galho baixo."""
    def fn(m):
        rr = rnd(seed); mat = casca_musgo(seed % 3)
        n = int(h/.5); pts, rad = [], []
        for i in range(n + 1):
            t = i/n; z = -.3 + t*(h + .3)
            pts.append((math.sin(t*4 + seed)*.12*t, math.cos(t*3.3 + seed)*.12*t, z))
            rad.append(r*(1.0 - .55*t) + r*.6*max(0, .18 - t)/.18)
        tubo(mat, pts, rad, 14, seed, .1, sulcos=5)
        raizes(mat, r, -.1, rr, 6, 2.4)
        cs = []
        for kk in range(rr.randint(4, 6)):
            t = rr.uniform(.5, .92); i = int(t*n)
            a = rr.uniform(0, 6.28); p = Vector(pts[i])
            d = Vector((math.cos(a), math.sin(a), rr.uniform(.35, .9)))
            Lg = rr.uniform(1.6, 3.0)*(.6 + h/10); galho(mat, p, d, Lg, rad[i]*.5, rr, 1)
            cs.append(p + d.normalized()*Lg)
        R = 2.2 + h*.15
        copa(Vector(pts[-1]) - Vector((0, 0, .8)), R, rr, k, 9)
        for c in cs: copa(c, R*.5, rr, k, rr.randint(2, 4))
        musgo_pe(rr, r*2.2, 6)
        florzinhas(rr, (0, 0, 0), r*2.6, 10, [petala_branca(), petala_ouro()])
        if lanterna and cs:
            c = min(cs, key=lambda q: q.z); lanterna_seiva((c.x*.9, c.y*.9, c.z - .2), rr, 1.0)
        return {"emissivo": "lanterna de seiva (âmbar)" if lanterna else "", "bioma": "novo_eden"}
    return fn

def figueira(seed, h=4.2):
    """Figueira: tronco curto e grosso, galhos abertos, copa larga e baixa de folhas grandes, figos escuros."""
    def fn(m):
        rr = rnd(seed); mat = casca_musgo(seed % 3)
        pts = [(math.sin(i*.7 + seed)*.1, math.cos(i*.6 + seed)*.1, -.3 + i/5*(h*.5 + .3)) for i in range(6)]
        tubo(mat, pts, [.5*(1 - .4*i/5) + .05 for i in range(6)], 14, seed, .12, sulcos=4)
        raizes(mat, .5, -.1, rr, 7, 2.0)
        top = Vector(pts[-1]); cs = []
        for kk in range(rr.randint(5, 7)):
            a = kk/6*2*math.pi + rr.uniform(-.3, .3)
            d = Vector((math.cos(a), math.sin(a), rr.uniform(.2, .55)))
            Lg = rr.uniform(2.0, 3.2); galho(mat, top, d, Lg, .2, rr, 1); cs.append(top + d.normalized()*Lg)
        for c in cs: copa(c + Vector((0, 0, .3)), 1.5, rr, 1, 3, 1.1, 1.6, .6)
        copa(top + Vector((0, 0, 1.2)), 1.8, rr, 1, 3, 1.0, 1.6, .6)
        figo = K.mat_solid("figo", (.12, .05, .08), 0, .45)
        for kk in range(22):
            c = rr.choice(cs); sphere(figo, (c.x + rr.uniform(-1, 1), c.y + rr.uniform(-1, 1), c.z + rr.uniform(-.4, .5)), (.07, .07, .09), segs=8)
        musgo_pe(rr, 1.0, 5)
        return {"bioma": "novo_eden"}
    return fn

def arvore_frutos(seed, h=5.0):
    """Árvore do pomar ("toda árvore agradável à vista e boa para comida"): copa redonda com frutos dourados acesos."""
    def fn(m):
        rr = rnd(seed); mat = casca_viva(seed % 3)
        pts = [(math.sin(i*.5 + seed)*.08, math.cos(i*.4 + seed)*.08, -.3 + i/8*(h*.62 + .3)) for i in range(9)]
        tubo(mat, pts, [.24*(1 - .5*i/8) + .03 for i in range(9)], 11, seed, .1, sulcos=3)
        raizes(mat, .25, -.1, rr, 5, 1.8)
        top = Vector(pts[-1]); cs = []
        for kk in range(rr.randint(4, 6)):
            a = rr.uniform(0, 6.28); d = Vector((math.cos(a), math.sin(a), rr.uniform(.5, 1.2)))
            Lg = rr.uniform(1.0, 1.8); galho(mat, top, d, Lg, .1, rr, 0); cs.append(top + d.normalized()*Lg)
        R = 1.5 + h*.12
        copa(top + Vector((0, 0, R*.7)), R, rr, 0, 6, 1.1, .9)
        for kk in range(16):
            a = rr.uniform(0, 6.28); b = rr.uniform(-.3, .9); d = R*rr.uniform(.85, 1.05)
            p = top + Vector((math.cos(a)*math.cos(b)*d, math.sin(a)*math.cos(b)*d, R*.7 + math.sin(b)*d*.8))
            sphere(fruto_ouro(), tuple(p), (.09, .09, .1), segs=8)
        musgo_pe(rr, .8, 4); florzinhas(rr, (0, 0, 0), 1.6, 8, [petala_branca()])
        point((0, 0, top.z + R*.7), (1, .65, .25), 40, .8)
        return {"emissivo": "frutos dourados", "bioma": "novo_eden"}
    return fn

def salgueiro(seed, h=6.0):
    """Salgueiro da margem: tronco inclinado para a água, ramos que caem em cortinas de folhas prateadas."""
    def fn(m):
        rr = rnd(seed); mat = casca_musgo(seed % 3)
        lean = Vector((rr.uniform(-.5, .5), rr.uniform(.3, .7), 0))
        pts = [tuple(Vector((0, 0, -.3 + i/8*(h*.6 + .3))) + lean*((i/8)**1.6)) for i in range(9)]
        tubo(mat, pts, [.34*(1 - .5*i/8) + .04 for i in range(9)], 12, seed, .1, sulcos=4)
        raizes(mat, .35, -.1, rr, 5, 2.0)
        top = Vector(pts[-1])
        ramo = K.mat_solid("ramo_salgueiro", (.05, .045, .03), 0, .7)
        for kk in range(rr.randint(26, 32)):
            a = rr.uniform(0, 6.28); d = rr.uniform(.5, 2.3)
            galho(mat, top, Vector((math.cos(a), math.sin(a), rr.uniform(.3, 1.0))), d, .07, rr, 0)
            q = top + Vector((math.cos(a), math.sin(a), rr.uniform(.3, 1.0))).normalized()*d
            L0 = rr.uniform(2.2, h*.65); nseg = 4
            for j in range(nseg):
                z0 = q.z - L0*j/nseg; z1 = q.z - L0*(j + 1)/nseg
                dx, dy = math.cos(a)*.12*(j + 1), math.sin(a)*.12*(j + 1)
                o = box(folha_eden(2), (q.x + dx, q.y + dy, (z0 + z1)/2), (.07 + .03*rr.random(), .03, L0/nseg*1.05), (rr.uniform(-6, 6), rr.uniform(-6, 6), math.degrees(a) + rr.uniform(-20, 20)), 0)
        copa(top + Vector((0, 0, 1.0)), 1.3, rr, 2, 4, .8, .8)
        musgo_pe(rr, .9, 5)
        return {"bioma": "novo_eden"}
    return fn

def samambaia(seed, n=None, tam=1.0):
    """Touceira de samambaias: frondes arqueadas com folíolos."""
    def fn(m):
        rr = rnd(seed); talo = K.mat_solid("talo_samambaia", (.05, .07, .025), 0, .6)
        for i in range(n or rr.randint(7, 11)):
            a = rr.uniform(0, 6.28); L0 = rr.uniform(.7, 1.3)*tam; alt = rr.uniform(.5, .9)*tam
            pts = [Vector((math.cos(a)*L0*t, math.sin(a)*L0*t, alt*math.sin(t*math.pi*.85))) for t in [j/7 for j in range(8)]]
            tubo(talo, pts, [.018*(1 - j/9) + .004 for j in range(8)], 5, seed + i, 0)
            mf = folhagem_eden(1 if seed % 3 == 0 else 0)
            for j in range(1, 7):
                p = pts[j]; q = pts[j + 1]; c = (p + q)/2; dv = (q - p)
                w = (.34*(1 - abs(j/7 - .45)) + .08)*tam
                o = sphere(mf, tuple(c), (dv.length*.62, w, .012), segs=10)
                o.rotation_euler = (0, -math.atan2(dv.z, math.hypot(dv.x, dv.y)), math.atan2(dv.y, dv.x))
                displace(o, .02, .12, seed + i*10 + j, 1)
        return {"bioma": "novo_eden"}
    return fn

def moita_florida(seed, cor="branca"):
    """Moita cheia com flores (brancas ou douradas) e folhas largas na base."""
    def fn(m):
        rr = rnd(seed)
        pet = {"branca": petala_branca(), "ouro": petala_ouro(), "rosa": petala_rosa()}[cor]
        for i in range(rr.randint(4, 7)):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, .55); s = rr.uniform(.3, .6)
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=s, location=(math.cos(a)*d, math.sin(a)*d, s*.5))
            o = bpy.context.object; o.scale = (1, 1, .75); o.data.materials.append(folhagem_eden(0))
            displace(o, s*.35, .6, rr.randint(0, 999), 1)
            for pl in o.data.polygons: pl.use_smooth = True
            ps = o.modifiers.new("folhas", 'PARTICLE_SYSTEM').particle_system
            st = ps.settings; st.type = 'HAIR'; st.use_advanced_hair = True; st.count = int(260*s*s) + 40
            st.hair_length = 1.0; st.render_type = 'OBJECT'; st.instance_object = folha_obj(0, .7)
            st.particle_size = 1.3; st.size_random = .4; st.use_rotations = True; st.rotation_mode = 'NOR'
            st.phase_factor_random = 2.0; st.emit_from = 'FACE'; st.use_emit_random = True; ps.seed = rr.randint(0, 9999)
            florzinhas(rr, (math.cos(a)*d, math.sin(a)*d, s*.5), s*.9, rr.randint(5, 9), [pet], s*.5, .04)
        florzinhas(rr, (0, 0, 0), 1.0, 6, [pet], .02, .03)
        return {"bioma": "novo_eden"}
    return fn

def tapete_flores(seed, cor="branca"):
    """Tapete de trevo e florzinhas no chão (decal rasteiro)."""
    def fn(m):
        rr = rnd(seed)
        pet = {"branca": petala_branca(), "ouro": petala_ouro(), "rosa": petala_rosa()}[cor]
        for i in range(rr.randint(26, 34)):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, 1.0)**.7*1.1
            o = sphere(folhagem_eden(0), (math.cos(a)*d, math.sin(a)*d, .03), (rr.uniform(.16, .26), rr.uniform(.12, .2), .035), segs=8)
            displace(o, .02, .2, rr.randint(0, 99), 1)
        for c in range(4):
            a = rr.uniform(0, 6.28); d = rr.uniform(.2, .8)
            florzinhas(rr, (math.cos(a)*d, math.sin(a)*d, 0), .35, rr.randint(8, 12), [pet, pet, petala_branca()], .06, .03)
        return {"chao": True, "bioma": "novo_eden"}
    return fn

def pedra_coberta(seed, tam=1.0):
    """Pedra grande coberta de musgo, com samambaia e florzinhas no pé."""
    def fn(m):
        rr = rnd(seed); mat = pedra_musgo(seed % 3, .9)
        for k, (x, y, z, s) in enumerate([(0, 0, .55*tam, (1.0*tam, .8*tam, .7*tam)), (-.6*tam, .3*tam, .3*tam, (.5*tam, .45*tam, .4*tam)), (.55*tam, -.25*tam, .25*tam, (.45*tam, .4*tam, .32*tam))][:2 + seed % 2]):
            o = sphere(mat, (x, y, z), s, segs=18); crumble(o, .1*tam, seed + k)
        musgo_pe(rr, 1.0*tam, 5, 0.0)
        samambaia(seed + 7, 4, .7)(m)
        florzinhas(rr, (0, 0, 0), 1.2*tam, 6, [petala_branca()])
        return {"bioma": "novo_eden"}
    return fn

def tronco_caido(seed):
    """Tronco tombado cheio de musgo, cogumelos e flores crescendo em cima (a vida voltando)."""
    def fn(m):
        rr = rnd(seed); mat = casca_musgo(seed % 3); Lc = 3.4; r = .38
        pts = [(-Lc/2 + Lc*i/6, math.sin(i*.9 + seed)*.08, r*.85 + math.sin(i*.6)*.05) for i in range(7)]
        tubo(mat, pts, [r*(1 - .25*i/6) for i in range(7)], 12, seed, .12, sulcos=5)
        lascas(mat, Vector(pts[0]) - Vector((.1, 0, 0)), r, r*.85, rr, 5)
        for k in range(3):
            a = rr.uniform(1.5, 4.5); galho(mat, Vector(pts[rr.randint(2, 5)]), (math.cos(a)*.6, math.sin(a), .6), rr.uniform(.6, 1.1), .06, rr, 0)
        for k in range(7):
            x = rr.uniform(-Lc/2 + .3, Lc/2 - .3)
            o = sphere(musgo_mat(), (x, rr.uniform(-.2, .2), r*1.55), (rr.uniform(.25, .4), rr.uniform(.2, .32), .08), segs=10)
        cogumelos(rr, (rr.uniform(-1.0, 0), rr.uniform(-.1, .1), r*1.6), 5, 1.2)
        cogumelos(rr, (rr.uniform(.4, 1.3), -.45, 0), 4, 1.0)
        florzinhas(rr, (0, 0, r*1.6), 1.2, 7, [petala_branca(), petala_ouro()], 0, .03)
        musgo_pe(rr, 1.4, 4)
        return {"bioma": "novo_eden"}
    return fn

def nenufares(seed):
    """Nenúfares: folhas redondas na água com flores brancas abertas (decal da margem do lago)."""
    def fn(m):
        rr = rnd(seed)
        for i in range(rr.randint(7, 10)):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, 1.1); R = rr.uniform(.18, .32)
            o = cyl(folhagem_eden(0), (math.cos(a)*d, math.sin(a)*d, .012), R, .02, (0, 0, rr.uniform(0, 360)), 14)
            box(K.mat_solid("corte", (.01, .02, .01)), (math.cos(a)*d + R*.6, math.sin(a)*d, .02), (R*.9, .035, .03), (0, 0, rr.uniform(0, 360)), 0)
            if rr.random() < .45:
                c = (math.cos(a)*d, math.sin(a)*d, .06)
                for k in range(7):
                    b = k/7*2*math.pi; sphere(petala_branca(), (c[0] + math.cos(b)*.07, c[1] + math.sin(b)*.07, c[2]), (.06, .03, .03), segs=6).rotation_euler = (0, -.5, b)
                sphere(petala_ouro(), c, (.03, .03, .03), segs=6)
        return {"chao": True, "bioma": "novo_eden"}
    return fn

def cogumelos_eden(seed):
    """Cogumelos cor de mel em touceira num toco com musgo."""
    def fn(m):
        rr = rnd(seed); mat = casca_musgo(seed % 3)
        tubo(mat, [(0, 0, -.2), (0, 0, .2), (.02, .02, .45)], [.3, .28, .25], 12, seed, .12)
        lascas(mat, Vector((0, 0, .45)), .25, .45, rr, 5)
        cogumelos(rr, (0, 0, .45), 6, 1.5); cogumelos(rr, (.4, .2, 0), 4, 1.0)
        musgo_pe(rr, .6, 4)
        return {"bioma": "novo_eden"}
    return fn

def juncos_eden(seed):
    """Juncos e taboas altos da margem, com algumas folhas de lume."""
    def fn(m):
        rr = rnd(seed); jm = folhagem_eden(1)
        for i in range(rr.randint(16, 22)):
            a = rr.uniform(0, 6.28); d = rr.uniform(0, .6); h = rr.uniform(.8, 1.6)
            o = box(jm, (math.cos(a)*d, math.sin(a)*d, h/2), (.035, .012, h), (rr.uniform(-10, 10), rr.uniform(-10, 10), rr.uniform(0, 180)), 0)
            if rr.random() < .3: cyl(K.mat_solid("taboa", (.16, .09, .04), 0, .8), (math.cos(a)*d, math.sin(a)*d, h - .08), .025, .16, verts=7)
        return {"bioma": "novo_eden"}
    return fn

def trelica_videira(seed):
    """Treliça de madeira da Enxertia com videira: parreira carregada de uvas (a vinha do jardim)."""
    def fn(m):
        rr = rnd(seed); wood = K.mat_wood("trelica", (.07, .05, .033), seed); vid = casca_viva(1)
        for x in (-1.1, 0, 1.1): cyl(wood, (x, 0, .95), .05, 2.1, verts=8)
        for z in (.7, 1.3, 1.85): box(wood, (0, 0, z), (2.5, .04, .05), bevel=.003)
        pts = [(-1.0, .02, -.2), (-.9, .04, .5), (-.6, .03, 1.0), (0, .05, 1.4), (.7, .03, 1.75), (1.2, .04, 1.9)]
        tubo(vid, pts, [.05, .045, .04, .035, .03, .02], 7, seed, .15)
        for kk in range(26):
            x = rr.uniform(-1.2, 1.2); z = rr.uniform(.5, 2.0)
            o = sphere(folha_eden(1), (x, rr.uniform(-.1, .1), z), (.16, .13, .02), segs=8); o.rotation_euler = (rr.uniform(-.5, .5), rr.uniform(-.5, .5), rr.uniform(0, 6.28))
        uva = K.mat_solid("uva", (.12, .04, .1), 0, .35)
        for kk in range(5):
            x = rr.uniform(-1.0, 1.0); z = rr.uniform(.9, 1.7)
            for j in range(8): sphere(uva, (x + rr.uniform(-.06, .06), rr.uniform(-.05, .05), z - j*.035 - rr.uniform(0, .03)), (.035, .035, .035), segs=6)
        return {"bioma": "novo_eden"}
    return fn

def colmeia(seed):
    """Colmeia da Enxertia: caixa de madeira sobre pernas, telhadinho de zinco, abelhas em volta."""
    def fn(m):
        rr = rnd(seed); wood = K.mat_wood("colmeia", (.09, .065, .04), seed)
        for (x, y) in [(-.3, -.22), (.3, -.22), (-.3, .22), (.3, .22)]: cyl(wood, (x, y, .22), .03, .44, verts=6)
        for k in range(3): box(wood if k % 2 else K.mat_wood("colmeia2", (.11, .08, .05), seed + 1), (0, 0, .62 + k*.28), (.72, .52, .26), bevel=.01)
        box(m["tin"], (0, 0, 1.33), (.84, .64, .05), (0, 4, 0), .003)
        box(K.mat_solid("entrada_colmeia", (.01, .008, .005)), (0, -.27, .55), (.3, .02, .05), bevel=0)
        ab = K.mat_solid("abelha", (.35, .25, .05), 0, .5)
        for k in range(9): sphere(ab, (rr.uniform(-.7, .7), rr.uniform(-.7, .3), rr.uniform(.3, 1.6)), (.022, .014, .012), segs=6)
        return {"bioma": "novo_eden"}
    return fn

def lanterna_eden(seed):
    """Poste de madeira com lanterna de seiva de latão (luz âmbar dos caminhos do jardim)."""
    def fn(m):
        rr = rnd(seed); wood = K.mat_wood("poste_eden", (.06, .043, .03), seed)
        cyl(wood, (0, 0, 1.15), .055, 2.3, verts=8); cyl(wood, (0, 0, 2.31), .07, .04, verts=8)
        along(wood, (0, 0, 2.1), (.45, 0, 2.28), .03, verts=6)
        lanterna_seiva((.45, 0, 2.28), rr, .25)
        tubo(casca_viva(2), [(.06, 0, -.1), (.07, .02, .6), (.04, .05, 1.3), (.0, .06, 1.9)], [.03, .025, .02, .012], 6, seed, .2)
        for kk in range(10):
            z = rr.uniform(.2, 1.9); a = rr.uniform(0, 6.28)
            sphere(folha_eden(0), (math.cos(a)*.1, math.sin(a)*.1, z), (.09, .07, .012), segs=6).rotation_euler = (0, rr.uniform(-.5, .5), a)
        musgo_pe(rr, .3, 3)
        return {"emissivo": "lanterna de seiva (âmbar)", "bioma": "novo_eden"}
    return fn

def placa_versiculo(seed):
    """Lápide de pedra fincada no chão com um versículo gravado (a Enxertia marca o jardim com o Gênesis)."""
    def fn(m):
        rr = rnd(seed); mat = pedra_musgo(seed % 3, .4)
        o = box(mat, (0, 0, .55), (.8, .14, 1.1), (rr.uniform(-4, 4), 0, 0), .02); crumble(o, .025, seed)
        sul = K.mat_solid("sulco_pedra", (.03, .028, .025), 0, 1)
        for k in range(6):
            w = rr.uniform(.35, .6); box(sul, (rr.uniform(-.08, .08), -.075, .95 - k*.13), (w, .01, .025), bevel=0)
        musgo_pe(rr, .45, 3); florzinhas(rr, (0, 0, 0), .5, 5, [petala_branca()])
        return {"bioma": "novo_eden"}
    return fn

# ---------------------------------------------------------------- marcos
def fonte_quatro_rios(seed=1):
    """A Nascente dos Quatro Rios: "um rio saía do Éden para regar o jardim e dali se dividia em quatro braços".
    Bacia de pedra coberta de musgo com um pilar partido no meio de onde a água limpa jorra em ciano, quatro
    calhas de pedra que levam a água para os quatro lados, nenúfares e flores."""
    def fn(m):
        rr = rnd(seed); ped = pedra_musgo(0, .8); ped2 = pedra_musgo(1, .5); R = 2.6
        torus(ped, (0, 0, .25), R, .32)                        # mureta
        for k in range(28):
            a = k/28*2*math.pi; o = sphere(ped2, (math.cos(a)*R, math.sin(a)*R, .28), (.42, .3, .3), segs=10)
            o.rotation_euler = (0, 0, a); crumble(o, .05, seed + k)
        cyl(agua_limpa(), (0, 0, .2), R - .2, .08, verts=40)     # espelho d'água
        pts = [(0, 0, 0), (.04, 0, .8), (.0, .05, 1.5), (-.04, .02, 2.1)]
        tubo(ped, pts, [.5, .42, .36, .3], 12, seed, .08)      # pilar partido
        lascas(ped, Vector((0, 0, 2.1)), .3, 2.1, rr, 5)
        for k in range(4):                                     # as quatro bocas e calhas (Pisom, Giom, Hidéquel, Eufrates)
            a = k/4*2*math.pi + math.pi/4
            cyl(ped2, (math.cos(a)*.42, math.sin(a)*.42, 1.1), .09, .4, (0, 90, math.degrees(a)), 10)
            cyl(agua_limpa(), (math.cos(a)*.6, math.sin(a)*.6, 1.05), .045, .5, (0, 90, math.degrees(a)), 8)
            jato = [(math.cos(a)*(.7 + t*.9), math.sin(a)*(.7 + t*.9), 1.05 - t*t*.85) for t in [j/6 for j in range(7)]]
            tubo(lume(), jato, [.04 - j*.003 for j in range(7)], 6, seed + k, .05)
            box(ped2, (math.cos(a)*(R + .9), math.sin(a)*(R + .9), .12), (1.3, .5, .24), (0, 0, math.degrees(a)), .02)
            box(agua_limpa(), (math.cos(a)*(R + .9), math.sin(a)*(R + .9), .2), (1.3, .28, .06), (0, 0, math.degrees(a)), 0)
        for k in range(10):                                    # musgo, samambaia, nenúfares
            a = rr.uniform(0, 6.28); d = rr.uniform(.5, R - .5)
            cyl(folhagem_eden(0), (math.cos(a)*d, math.sin(a)*d, .26), rr.uniform(.15, .28), .02, verts=12)
        musgo_pe(rr, R + .6, 10, .0)
        for k in range(6):
            a = rr.uniform(0, 6.28); o = sphere(musgo_mat(), (math.cos(a)*R, math.sin(a)*R, .55), (.35, .25, .1), segs=8)
        samambaia(seed + 3, 5, .8)(m)
        florzinhas(rr, (0, 0, 0), R + .8, 14, [petala_branca(), petala_ouro()], 0, .035)
        point((0, 0, 1.0), LUME, 90, .6); point((0, 0, 2.4), LUME, 40, .3)
        return {"emissivo": "água limpa (ciano)", "bioma": "novo_eden", "marco": "nascente"}
    return fn

def arvore_conhecimento(seed=3):
    """A Árvore do Conhecimento do Bem e do Mal: tronco pálido retorcido em espiral, galhos nus que se fecham
    como mãos, frutos acesos no verde do Amargo (a única cor "errada" do jardim) e a Serpente enrolada na base.
    A Enxertia cerca a árvore com cordas e placas: ninguém come daquele fruto."""
    def fn(m):
        rr = rnd(seed); mat = K.mat_wood("casca_palida", (.2, .17, .13), 7.0); h = 6.0
        n = 18; pts, rad = [], []
        for i in range(n + 1):
            t = i/n; z = -.3 + t*(h + .3); a = t*5.0
            pts.append((math.cos(a)*.35*t, math.sin(a)*.35*t, z)); rad.append(.55*(1 - .6*t) + .05)
        tubo(mat, pts, rad, 16, seed, .18, sulcos=7)
        raizes(mat, .6, -.1, rr, 7, 2.6)
        cs = []
        for kk in range(8):
            t = rr.uniform(.45, .95); i = int(t*n); p = Vector(pts[i]); a = rr.uniform(0, 6.28)
            d = Vector((math.cos(a), math.sin(a), rr.uniform(.2, 1.0))); Lg = rr.uniform(2.0, 3.6)
            galho(mat, p, d, Lg, rad[i]*.55, rr, 2); cs.append(p + d.normalized()*Lg)
        copa(Vector(pts[-1]) - Vector((0, 0, .8)), 2.6, rr, 1, 5, .55, 1.2)
        for c in cs: copa(c, 1.1, rr, 1, 2, .5, 1.2)
        for kk in range(30):
            c = rr.choice(cs); p = c + Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-.9, .3)))
            sphere(fruto_amargo(), tuple(p), (.11, .11, .13), segs=8)
            along(K.mat_solid("pedunculo", (.1, .09, .07), 0, .7), tuple(p + Vector((0, 0, .5))), tuple(p + Vector((0, 0, .1))), .012, verts=4)
        # a serpente enrolada na base (a Serpente de verdade é um monstro; esta é a marca dela na casca)
        serp = K.mat_solid("escama_serpente", (.08, .11, .05), .2, .35)
        esp = [(math.cos(t*2.5)*(.75 - t*.1), math.sin(t*2.5)*(.75 - t*.1), .3 + t*1.6) for t in [j/24 for j in range(25)]]
        tubo(serp, esp, [.12 - j*.003 for j in range(25)], 9, seed + 9, .06)
        # cerca de cordas da Enxertia
        wood = K.mat_wood("estaca_cerca", (.06, .043, .03)); corda = K.mat_cloth("corda_cerca", (.1, .085, .06), 2.0)
        for k in range(6):
            a = k/6*2*math.pi; b = (k + 1)/6*2*math.pi
            o = cyl(wood, (math.cos(a)*3.4, math.sin(a)*3.4, .55), .09, 1.1, verts=7, r2=.06); o.rotation_euler = (rr.uniform(-.08, .08), rr.uniform(-.08, .08), a)
            for zz in (.95, .55):
                along(corda, (math.cos(a)*3.4, math.sin(a)*3.4, zz), (math.cos(b)*3.4, math.sin(b)*3.4, zz), .03, verts=5)
            sphere(K.mat_cloth("fita_cerca", (.45, .1, .08), 1.5), ((math.cos(a) + math.cos(b))*1.7, (math.sin(a) + math.sin(b))*1.7, .9), (.05, .05, .14), segs=6)
        placa_versiculo(seed + 1)(m)
        for o in bpy.data.objects:
            if o.name.startswith("Cube") and abs(o.location.x) < .5 and abs(o.location.y) < .5 and o.location.z < .6 and o.dimensions.z > .9: o.location += Vector((3.6, -1.6, 0))
        musgo_pe(rr, 2.2, 8)
        point((0, 0, 5.5), AMARGO, 60, 1.0)
        return {"emissivo": "frutos do Amargo (verde)", "bioma": "novo_eden", "marco": "conhecimento"}
    return fn

def espada_flamejante(seed=5):
    """"Pôs querubins ao oriente do jardim do Éden, e uma espada flamejante que andava ao redor": o Coro deixou a
    espada no Portão do Oriente: uma lâmina de 3 m fincada num pedestal de pedra, queimando sem se consumir."""
    def fn(m):
        rr = rnd(seed); ped = pedra_musgo(2, .35); ferro = K.mat_metal("lamina_velha", (.3, .3, .32), .25, seed, .35)
        o = cyl(ped, (0, 0, .3), .9, .6, verts=10); crumble(o, .04, seed)
        cyl(ped, (0, 0, .75), .55, .3, verts=10)
        box(ferro, (0, 0, 2.2), (.22, .05, 2.9), (0, 0, 20), .006)                # lâmina
        box(ferro, (0, 0, 3.65), (.14, .05, .3), (0, 0, 20), 0)                    # ponta
        box(K.mat_brass(), (0, 0, .95), (.9, .12, .12), (0, 0, 20), .01)          # guarda
        cyl(K.mat_wood("punho", (.05, .035, .025)), (0, 0, .7), .06, .5, verts=8)
        fm = K.mat_emit("fogo_espada", (1, .38, .08), 12)
        for k in range(14):
            z = 1.1 + k*.19; h = rr.uniform(.2, .45)
            cyl(fm, (rr.uniform(-.1, .1), rr.uniform(-.06, .06), z + h/2), rr.uniform(.04, .09), h, (rr.uniform(-15, 15), rr.uniform(-15, 15), 0), 7, r2=0)
        flame((0, 0, 3.6), 1.2, None, 16)
        point((0, 0, 2.2), (1, .45, .14), 220, .3)
        for k in range(5):
            a = rr.uniform(0, 6.28); sphere(K.mat_solid("brasa_chao", (.05, .02, .01), 0, .9, emit=(1, .3, .05), strength=2), (math.cos(a)*rr.uniform(1.0, 1.5), math.sin(a)*rr.uniform(1.0, 1.5), .03), (.06, .05, .03), segs=6)
        musgo_pe(rr, 1.2, 3)
        return {"emissivo": "fogo", "bioma": "novo_eden", "marco": "portao_oriente"}
    return fn

def pilar_portao(seed=6, lado=1):
    """Pilar do Portão do Oriente: coluna de pedra quebrada com hera e um querubim de pedra sem cabeça no topo."""
    def fn(m):
        rr = rnd(seed); ped = pedra_musgo(seed % 3, .6)
        box(ped, (0, 0, .25), (1.3, 1.3, .5), bevel=.03)
        o = cyl(ped, (0, 0, 2.3), .42, 3.6, verts=14); crumble(o, .05, seed)
        box(ped, (0, 0, 4.2), (1.1, 1.1, .3), bevel=.03)
        # querubim de pedra: corpo ajoelhado, asas abertas, sem cabeça
        sphere(ped, (0, 0, 4.9), (.38, .32, .55), segs=12)
        for s in (-1, 1):
            o = sphere(ped, (s*.42, -.05, 5.25), (.16, .4, .7), segs=12); o.rotation_euler = (0, s*.3, 0)
        cyl(ped, (0, 0, 5.5), .12, .15, verts=8)                                     # pescoço quebrado
        box(ped, (0, -.2, 5.1), (.5, .2, .3), bevel=.02)                              # braços cruzados
        hera = casca_viva(2)
        tubo(hera, [(.4*lado, .3, -.1), (.45*lado, .2, 1.0), (.3*lado, -.2, 2.2), (.1*lado, -.4, 3.4), (-.2*lado, -.3, 4.2)], [.04, .035, .03, .025, .02], 6, seed, .2)
        for kk in range(26):
            z = rr.uniform(.2, 4.2); a = rr.uniform(0, 6.28)
            sphere(folha_eden(1), (math.cos(a)*.46, math.sin(a)*.46, z), (.12, .09, .015), segs=6).rotation_euler = (0, rr.uniform(-.6, .6), a)
        musgo_pe(rr, 1.0, 5)
        return {"bioma": "novo_eden", "marco": "portao_oriente"}
    return fn

def arco_eden(seed=8):
    """Arco de pedra do Portão do Oriente coberto de hera e flores (a entrada do jardim)."""
    def fn(m):
        rr = rnd(seed); ped = pedra_musgo(0, .6)
        for x in (-2.2, 2.2):
            o = cyl(ped, (x, 0, 1.6), .38, 3.2, verts=12); crumble(o, .04, seed + int(x))
            box(ped, (x, 0, .2), (1.0, 1.0, .4), bevel=.03)
        pts = [(-2.2 + 4.4*t, 0, 3.2 + 1.5*math.sin(t*math.pi)) for t in [j/12 for j in range(13)]]
        tubo(ped, pts, [.38]*13, 10, seed, .05)
        hera = casca_viva(2)
        for t0 in (0.0, .5):
            seg = [(p[0], p[1] - .3, p[2] + .25) for p in pts[int(t0*12):int(t0*12) + 7]]
            tubo(hera, seg, [.03]*len(seg), 5, seed + int(t0*10), .2)
        for kk in range(60):
            t = rr.uniform(0, 1); p = pts[int(t*12)]
            sphere(folha_eden(1), (p[0] + rr.uniform(-.3, .3), p[1] - .35 + rr.uniform(-.1, .1), p[2] + rr.uniform(-.3, .4)), (.13, .1, .015), segs=6).rotation_euler = (rr.uniform(-.6, .6), 0, rr.uniform(0, 6.28))
        florzinhas(rr, (0, -.35, 3.4), 2.2, 18, [petala_branca(), petala_rosa()], 0, .04)
        musgo_pe(rr, 2.6, 6)
        return {"bioma": "novo_eden", "marco": "portao_oriente"}
    return fn

def ponte_tabuas(seed=9, orient="a"):
    """Pontezinha de tábuas sobre o riacho, com corrimão de galhos e musgo."""
    def fn(m):
        rr = rnd(seed); wood = K.mat_wood("ponte_eden", (.075, .052, .034), seed); L0 = 3.0
        for i in range(9):
            x = -L0/2 + L0*(i + .5)/9
            box(wood if i % 2 else K.mat_wood("ponte_eden2", (.065, .045, .03), seed + 1), (x, 0, .22 + .05*math.sin(i/8*math.pi)), (L0/9*.9, 1.3, .05), (0, 0, rr.uniform(-2, 2)), .004)
        for y in (-.62, .62):
            box(wood, (0, y, .16), (L0, .08, .1), bevel=.005)
            for x in (-L0/2 + .2, 0, L0/2 - .2): cyl(wood, (x, y, .55), .035, .7, verts=6)
            tubo(casca_viva(1), [(-L0/2 + .2, y, .9), (-.5, y + .03, .95), (.5, y - .02, .92), (L0/2 - .2, y, .9)], [.03]*4, 6, seed, .15)
        for k in range(5): sphere(musgo_mat(), (rr.uniform(-1.2, 1.2), rr.choice((-.62, .62)), .3), (.15, .1, .05), segs=8)
        return {"bioma": "novo_eden"}
    return fn

# ---------------------------------------------------------------- registro
def _reg(nome, fn, cat="vegetacao", fp=(1, 1), samples=48):
    def wrap(m, seed=0):
        limpar(); meta = fn(m) or {}
        # as folhas instanciadas não entram no render como objeto próprio
        return meta
    REG[nome] = dict(fn=wrap, cat=cat, fp=fp, dungeon=False, walls=False, samples=samples, bury=0.0)
    wrap.__doc__ = fn.__doc__ or ""

for _n, _fn, _fp in [
    ("arvore_eden", arvore_eden(11, 5.2, .34), (2, 2)), ("arvore_eden_2", arvore_eden(23, 5.8, .38, True, 0), (2, 2)),
    ("arvore_eden_3", arvore_eden(37, 4.6, .32, False, 0), (2, 2)),
    ("figueira", figueira(41, 3.2), (3, 3)), ("figueira_2", figueira(43, 2.8), (3, 3)),
    ("arvore_frutos", arvore_frutos(51, 4.2), (2, 2)), ("arvore_frutos_2", arvore_frutos(53, 3.8), (2, 2)),
    ("salgueiro", salgueiro(61, 4.8), (2, 2)), ("salgueiro_2", salgueiro(67, 4.2), (2, 2)),
    ("samambaia", samambaia(71), (1, 1)), ("samambaia_2", samambaia(72, 9, 1.2), (1, 1)), ("samambaia_3", samambaia(73, 6, .8), (1, 1)),
    ("moita_florida", moita_florida(81, "branca"), (1, 1)), ("moita_florida_2", moita_florida(83, "ouro"), (1, 1)), ("moita_florida_3", moita_florida(85, "rosa"), (1, 1)),
    ("tapete_flores", tapete_flores(91, "branca"), (1, 1)), ("tapete_flores_2", tapete_flores(93, "ouro"), (1, 1)), ("tapete_flores_3", tapete_flores(95, "rosa"), (1, 1)),
    ("pedra_coberta", pedra_coberta(101), (2, 2)), ("pedra_coberta_2", pedra_coberta(102, 1.3), (2, 2)), ("pedra_coberta_3", pedra_coberta(105, .7), (1, 1)),
    ("tronco_caido_eden", tronco_caido(111), (3, 1)), ("tronco_caido_eden_2", tronco_caido(113), (3, 1)),
    ("nenufares", nenufares(121), (1, 1)), ("nenufares_2", nenufares(123), (1, 1)),
    ("cogumelos_eden", cogumelos_eden(131), (1, 1)), ("juncos_eden", juncos_eden(141), (1, 1)),
]:
    _reg(_n, _fn, "vegetacao", _fp)
for _n, _fn, _fp, _s in [
    ("trelica_videira", trelica_videira(151), (3, 1), 48), ("colmeia", colmeia(161), (1, 1), 40), ("lanterna_eden", lanterna_eden(171), (1, 1), 40),
    ("placa_versiculo", placa_versiculo(181), (1, 1), 40), ("fonte_quatro_rios", fonte_quatro_rios(), (5, 5), 64),
    ("arvore_conhecimento", arvore_conhecimento(), (4, 4), 64), ("espada_flamejante", espada_flamejante(), (2, 2), 56),
    ("pilar_portao", pilar_portao(6, 1), (1, 1), 48), ("pilar_portao_2", pilar_portao(7, -1), (1, 1), 48),
    ("arco_eden", arco_eden(), (4, 1), 56), ("ponte_tabuas", ponte_tabuas(), (3, 1), 40),
]:
    _reg(_n, _fn, "props", _fp, _s)
