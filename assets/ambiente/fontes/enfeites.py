# ================================================================ ENFEITES · props pequenos para as áreas carentes (17/10/2026)
# Pedido do Jefin: "criar mais props, pequenos enfeites, para as áreas mais carentes disso, que repetem muito; por exemplo
# o matadouro só tem uma carne espetada, coitado" + "algo mais bonito". Não entra na 0.9.3 (só adiantando).
# Barra de qualidade: kit do Egito (egito.py). Cada enfeite usa o vocabulário da área (regra Lorencia) e os mesmos
# materiais do kit dela, para não destoar: Matadouro reaproveita matadouro.py (carne, gordura, sangue, ferro, sal, sebo).
#
# Render (bpy 4.2; se /opt/bpy42 não existir: python3.11 -m pip install bpy==4.2.0 e use python3.11):
#   cd assets/ambiente/fontes && python3.11 render_assets.py -- /tmp/claude-0/enfeites_brutos <ids ...>
#   python3 publicar.py /tmp/claude-0/enfeites_brutos
# Integração (próxima versão depois da 0.9.3): entregas/enfeites/INTEGRACAO.md
import bpy, math
from mathutils import Vector, Matrix
import kit as K
from kit import box, cyl, sphere, along, torus, displace, point, N, L, ramp, mix, math_, noise, voronoi
import assets as A
from assets import REG, rnd
import atlantida as atl
from atlantida import tubo, rbox, rovo
import matadouro as MT
from matadouro import (ferro, ferrugem, latao, madeira, osso, solido, sombra, sangue, carne, gordura, pele, poca, pingos,
                       cutelo, caveira, rebites, ondula, subdiv, saco, corrente, gancho, podre)

ENFEITES = {}   # id -> bioma (o INTEGRACAO.md e a folha de prévia leem daqui)

def ef(nome, bioma, fp=(1, 1), samples=48, chao=False, cat="enfeites", dungeon=True):
    """Registra um enfeite. Cada bioma usa o pó e a luz do kit dele (masmorra: luz baixa e pó escuro; Egito: pó de
    calcário claro e a luz de fora, igual ao egito.py)."""
    def deco(fn):
        def wrap(m, seed=0):
            MT.limpar(); atl.limpar(); _MT.clear()
            po = MT.PO
            if bioma == "egito":
                import egito as EG; EG.limpar(); po = EG.PO
            K.DUST = po; prev = atl.TERRA; atl.TERRA = po
            if dungeon:
                for nm, e in (("key", 2.0), ("fill", .6), ("rim", 1.7)):
                    if nm in bpy.data.lights: bpy.data.lights[nm].energy = e
            try: r = fn() or {}
            finally: atl.TERRA = prev
            r.setdefault("bioma", bioma); r["enfeite"] = True
            if chao: r["chao"] = True
            return r
        wrap.__doc__ = fn.__doc__ or ""
        REG[nome] = dict(fn=wrap, cat="decalques" if chao else cat, fp=fp, dungeon=dungeon, walls=False, samples=samples, bury=0.0, no_catcher=False)
        ENFEITES[nome] = bioma
        return fn
    return deco

_MT = {}
def _c(key, fn):
    if key not in _MT or _MT[key].name not in bpy.data.materials: _MT[key] = fn()
    return _MT[key]

def piv_de(objs_antes, loc=(0, 0, 0), rot=(0, 0, 0)):
    """Agrupa tudo o que foi criado depois de objs_antes num pivô e move/gira o grupo (radianos)."""
    piv = bpy.data.objects.new("grp", None); bpy.context.scene.collection.objects.link(piv)
    for o in set(bpy.data.objects) - objs_antes - {piv}:
        if o.parent is None: o.parent = piv
    piv.location = loc; piv.rotation_euler = rot
    return piv

# ================================================================ materiais extras do açougue
def tripa(seed=0):
    """Tripa e miúdos: rosa-acinzentado molhado, veias arroxeadas, gordura amarelada em fiapos."""
    def f():
        m, nt, b = K.new_mat(f"tripa_mt_{seed}")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 6, 6, .6, seed); n2 = noise(nt, v, None, 22, 3, .5, seed + 1)
        cr = ramp(nt, [(.25, (.2, .07, .07)), (.55, (.34, .16, .15)), (.85, (.42, .25, .22))]); L(nt, n.outputs["Fac"], cr.inputs[0])
        col = mix(nt, cr.outputs[0], n2.outputs["Color"], .15, 'OVERLAY')
        vo = voronoi(nt, v, None, 14, 'DISTANCE_TO_EDGE', seed + 2)
        vr = ramp(nt, [(0, (1, 1, 1)), (.05, (0, 0, 0))]); L(nt, vo.outputs["Distance"], vr.inputs[0])
        col = mix(nt, col, (.12, .04, .09), math_(nt, 'MULTIPLY', vr.outputs[0], .55))          # veias
        gm = noise(nt, v, None, 4, 5, .6, seed + 3); gr = ramp(nt, [(.62, (0, 0, 0)), (.7, (1, 1, 1))]); L(nt, gm.outputs["Fac"], gr.inputs[0])
        col = mix(nt, col, (.5, .4, .24), math_(nt, 'MULTIPLY', gr.outputs[0], .7))              # gordura
        L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .22; b.inputs["Coat Weight"].default_value = .5
        b.inputs["Subsurface Weight"].default_value = .15; b.inputs["Subsurface Radius"].default_value = (1, .3, .2); b.inputs["Subsurface Scale"].default_value = .02
        K.bump(nt, b, math_(nt, 'ADD', n2.outputs["Fac"], vr.outputs[0]), .25, .008)
        return m
    return _c(("tripa", seed), f)

def figado():
    def f():
        m, nt, b = K.new_mat("figado_mt")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 5, 6, .6, 4.0)
        cr = ramp(nt, [(.3, (.05, .012, .01)), (.7, (.14, .035, .025))]); L(nt, n.outputs["Fac"], cr.inputs[0])
        L(nt, cr.outputs[0], b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .15; b.inputs["Coat Weight"].default_value = .7
        K.bump(nt, b, n.outputs["Fac"], .15, .01)
        return m
    return _c("figado", f)

def couro(seed=0, c=(.06, .04, .028)):
    return _c(("couro", seed, c), lambda: K.mat_cloth(f"couro_ef_{seed}", c, 20.0 + seed))
def zinco(): return _c("zinco", lambda: K.mat_metal("zinco_mt", (.11, .11, .105), .35, 21.0, .35))
def borracha(): return _c("borracha", lambda: K.mat_metal("borracha_mt", (.025, .022, .02), .1, 23.0, .8))
def sal_sujo(): return MT._c("sal_sujo", lambda: K.mat_stone("sal_sujo_mt", (.36, .34, .31), (.22, .2, .18), 9.0, 0, None, .5, 3.0))
def mosca_pouso():
    return _c("moscas", lambda: K.mat_metal("moscas_mt", (.01, .012, .01), 0, 31.0, .25))


def casca(seed=0):
    """Casca de tronco velho: rachas verticais fundas, cinza-marrom, pó nas fendas."""
    def f():
        m, nt, b = K.new_mat(f"casca_mt_{seed}")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        mp = N(nt, "ShaderNodeMapping"); mp.inputs["Scale"].default_value = (4, 4, .7); L(nt, v, mp.inputs[0])
        vo = N(nt, "ShaderNodeTexVoronoi", feature='DISTANCE_TO_EDGE'); vo.inputs["Scale"].default_value = 9; vo.inputs["Randomness"].default_value = 1
        L(nt, mp.outputs[0], vo.inputs["Vector"])
        cr = ramp(nt, [(0, (0, 0, 0)), (.09, (1, 1, 1))]); L(nt, vo.outputs["Distance"], cr.inputs[0])
        n = noise(nt, v, None, 9, 6, .6, seed)
        base = ramp(nt, [(.3, (.035, .028, .022)), (.7, (.09, .07, .05))]); L(nt, n.outputs["Fac"], base.inputs[0])
        col = mix(nt, (.012, .01, .008), base.outputs[0], cr.outputs[0])
        L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .9
        K.bump(nt, b, math_(nt, 'ADD', cr.outputs[0], math_(nt, 'MULTIPLY', n.outputs["Fac"], .3)), .8, .02)
        return m
    return _c(("casca", seed), f)

def topo_cepo():
    """Topo do cepo: anéis do lenho, talhado e encharcado de sangue velho no meio, mais claro na borda."""
    def f():
        m, nt, b = K.new_mat("topo_cepo_mt")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 6, 5, .6, 3.0)
        wv = N(nt, "ShaderNodeTexWave", wave_type='RINGS'); wv.inputs["Scale"].default_value = 6; wv.inputs["Distortion"].default_value = 3
        wv.inputs["Detail"].default_value = 3; L(nt, v, wv.inputs[0])
        rg = ramp(nt, [(.2, (.13, .085, .05)), (.8, (.22, .15, .09))]); L(nt, wv.outputs["Fac"], rg.inputs[0])
        geo = N(nt, "ShaderNodeNewGeometry"); sp = N(nt, "ShaderNodeSeparateXYZ"); L(nt, v, sp.inputs[0])
        d = math_(nt, 'ADD', math_(nt, 'MULTIPLY', sp.outputs[0], sp.outputs[0]), math_(nt, 'MULTIPLY', sp.outputs[1], sp.outputs[1]))
        d = math_(nt, 'ADD', d, math_(nt, 'MULTIPLY', n.outputs["Fac"], .03))
        sg = ramp(nt, [(.02, (1, 1, 1)), (.05, (0, 0, 0))]); L(nt, d, sg.inputs[0])
        col = mix(nt, rg.outputs[0], (.07, .012, .008), math_(nt, 'MULTIPLY', sg.outputs[0], .9))
        L(nt, col, b.inputs["Base Color"])
        L(nt, math_(nt, 'SUBTRACT', .75, math_(nt, 'MULTIPLY', sg.outputs[0], .45)), b.inputs["Roughness"])
        K.bump(nt, b, wv.outputs["Fac"], .3, .01)
        return m
    return _c("topo_cepo", f)

def defumado(seed=0, c=(.09, .03, .018)):
    """Embutido defumado: mogno escuro com brilho de gordura, pintas de toucinho e barbante de fumaça."""
    def f():
        m, nt, b = K.new_mat(f"defumado_mt_{seed}")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 7, 6, .6, seed)
        cr = ramp(nt, [(.3, (c[0]*.5, c[1]*.5, c[2]*.5)), (.75, c)]); L(nt, n.outputs["Fac"], cr.inputs[0])
        vo = voronoi(nt, v, None, 70, 'F1', seed + 1)
        vr = ramp(nt, [(0, (1, 1, 1)), (.18, (0, 0, 0))]); L(nt, vo.outputs["Distance"], vr.inputs[0])
        col = mix(nt, cr.outputs[0], (.42, .32, .2), math_(nt, 'MULTIPLY', vr.outputs[0], .55))
        L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .32; b.inputs["Coat Weight"].default_value = .3
        K.bump(nt, b, math_(nt, 'ADD', n.outputs["Fac"], vr.outputs[0]), .3, .006)
        return m
    return _c(("defum", seed, c), f)

def couro_avental():
    """Couro grosso de avental: marrom curtido, vincos, e sangue velho subindo da barra (escuro, quase preto)."""
    def f():
        m, nt, b = K.new_mat("avental_couro_mt")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 5, 6, .6, 2.0); n2 = noise(nt, v, None, 40, 3, .5, 3.0)
        cr = ramp(nt, [(.3, (.06, .036, .022)), (.7, (.13, .08, .045))]); L(nt, n.outputs["Fac"], cr.inputs[0])
        col = mix(nt, cr.outputs[0], n2.outputs["Color"], .12, 'OVERLAY')
        geo = N(nt, "ShaderNodeNewGeometry"); sp = N(nt, "ShaderNodeSeparateXYZ"); L(nt, geo.outputs["Position"], sp.inputs[0])
        sn = noise(nt, v, None, 3, 5, .65, 5.0)
        hz = math_(nt, "ADD", sp.outputs[2], math_(nt, "MULTIPLY", sn.outputs["Fac"], .25))
        sg = ramp(nt, [(.47, (1, 1, 1)), (.57, (0, 0, 0))]); L(nt, math_(nt, "MULTIPLY", hz, .5), sg.inputs[0])
        rs = noise(nt, v, None, 12, 6, .7, 6.0); rsr = ramp(nt, [(.68, (0, 0, 0)), (.71, (1, 1, 1))]); L(nt, rs.outputs["Fac"], rsr.inputs[0])
        sgt = math_(nt, 'MINIMUM', math_(nt, 'ADD', sg.outputs[0], rsr.outputs[0]), 1.0)
        col = mix(nt, col, (.05, .006, .004), math_(nt, 'MULTIPLY', sgt, .9))
        L(nt, col, b.inputs["Base Color"])
        L(nt, math_(nt, 'SUBTRACT', .7, math_(nt, 'MULTIPLY', sgt, .45)), b.inputs["Roughness"])
        K.bump(nt, b, math_(nt, 'ADD', n.outputs["Fac"], math_(nt, 'MULTIPLY', n2.outputs["Fac"], .3)), .35, .01)
        return m
    return _c("avental", f)

def pernil(p, s=1.0, rot=0.0, seed=0, mofo=False):
    """Pernil curado pendurado pelo osso: canela fina em cima, coxa em gota, capa de gordura (ou bolor) por fora e o
    corte voltado para a câmera mostrando carne, gordura e o osso redondo."""
    x0, y0, z0 = p; rr = rnd(seed)
    perf = [(0, .03), (.06, .035), (.14, .05), (.24, .085), (.36, .12), (.5, .145), (.64, .15), (.76, .135), (.86, .1), (.94, .06), (1.0, .02)]
    H = .55*s; ns = 18; rings = []
    for t, r in perf:
        r *= s; ring = []
        for k in range(ns):
            a = 2*math.pi*k/ns
            ry = r*(.85 if math.sin(a) > 0 else .55)          # achatado do lado do corte (-y)
            ring.append(Vector((r*math.cos(a)*(1 + .04*math.sin(3*a + seed)), ry*math.sin(a), -t*H)))
        rings.append(ring)
    R = Matrix.Rotation(rot, 4, 'Z')
    rings = [[(R @ q) + Vector((x0, y0, z0)) for q in rg] for rg in rings]
    capa = (_c("bolor", lambda: K.mat_stone("bolor_mt", (.24, .23, .2), (.12, .11, .09), 9.0, 0, None, 1.0, 14.0)) if mofo else gordura(seed))
    o = MT.aneis("pernil", rings, [capa]); subdiv(o, 2); ondula(o, .01*s, .06, seed)
    # face do corte: elipse de carne com orla de gordura
    nrm = R @ Vector((0, -1, 0)); c = Vector((x0, y0, z0 - .62*H)) + nrm*(.06*s)
    rot_e = (math.radians(90), 0, rot)
    o = rovo(gordura(seed + 1), c, (.125*s, .2*s, .012*s), rot_e, 18)
    o = rovo(carne(seed, .55), c + nrm*.006, (.105*s, .175*s, .01*s), rot_e, 18); ondula(o, .006*s, .04, seed)
    cyl(osso((.6, .54, .42)), c + nrm*.012 + Vector((0, 0, .03*s)), .022*s, .008, (90, 0, math.degrees(rot)), 14)
    cyl(solido("medula", (.14, .02, .02), 0, .4), c + nrm*.017 + Vector((0, 0, .03*s)), .011*s, .004, (90, 0, math.degrees(rot)), 10)
    # osso da canela saindo em cima e barbante
    ob = osso((.55, .5, .4))
    along(ob, (x0, y0, z0 + .02), (x0, y0, z0 - .08*s), .018*s, verts=8); sphere(ob, (x0, y0, z0 + .025), (.026*s, .026*s, .02*s), segs=10)
    for k in range(3): torus(MT.solido("barbante", (.3, .25, .17), 0, .9), (x0, y0, z0 - .04*s - k*.025*s), .03*s, .004)
    return o

# ================================================================ peças reutilizáveis
def tripas(p, n=5, raio=.032, esp=.32, seed=0, mat=None, z=None):
    """Monte de tripa enrolada no chão (tubos em laço, achatados no peso)."""
    rr = rnd(seed); x0, y0, z0 = p; mat = mat or tripa(seed % 3)
    for k in range(n):
        a0 = rr.uniform(0, 6.28); R0 = rr.uniform(.4, 1.0)*esp*.5; pts = []
        for j in range(14):
            a = a0 + j*.55; r = R0*(1 + .35*math.sin(j*1.3 + k))
            pts.append((x0 + math.cos(a)*r, y0 + math.sin(a)*r*.85, z0 + raio*.8 + (k*.6 + j*.04)*raio*.55))
        o = tubo(mat, pts, [raio*rr.uniform(.85, 1.1)]*13 + [raio*.5], 10, seed + k, .12); o.scale.z = .8

def linguica(pts, r=.028, gomos=5, mat=None, seed=0):
    """Linguiça em gomos amarrados: tubo com estrangulamentos regulares ao longo da polilinha."""
    P = [Vector(q) for q in pts]; dens = []
    for i in range(len(P) - 1):
        for k in range(6): dens.append(P[i].lerp(P[i + 1], k/6))
    dens.append(P[-1]); n = len(dens)
    raios = [r*(.35 + .65*abs(math.sin(math.pi*gomos*i/(n - 1)))) for i in range(n)]
    raios[0] = raios[-1] = r*.3
    m = mat or _c(("ling", seed), lambda: K.mat_metal(f"linguica_mt_{seed}", (.14, .035, .025), 0, 40.0 + seed, .35))
    return tubo(m, dens, raios, 10, seed, .05)

def balde(p, r=.15, h=.3, mat=None, rot=(0, 0, 0)):
    """Balde de chapa com aros, borda virada e alça de arame."""
    antes = set(bpy.data.objects); fe = mat or ferrugem(3)
    cyl(fe, (0, 0, h/2), r*.85, h, verts=24, r2=r)
    cyl(sombra(), (0, 0, h - .004), r*.95, .006, verts=24)
    torus(fe, (0, 0, h), r, .008); torus(fe, (0, 0, h*.25), r*.89, .006); torus(fe, (0, 0, h*.7), r*.96, .006)
    along(fe, (-r, 0, h*.9), (-r*.7, 0, h*1.45), .004, verts=4); along(fe, (r, 0, h*.9), (r*.7, 0, h*1.45), .004, verts=4)
    along(fe, (-r*.7, 0, h*1.45), (r*.7, 0, h*1.45), .004, verts=4)
    along(madeira(5, (.05, .03, .02)), (-r*.25, 0, h*1.45), (r*.25, 0, h*1.45), .012, verts=8)
    return piv_de(antes, p, rot)

def faca(p, rot=(0, 0, 0), s=1.0, tipo="faca"):
    """Faca de desossa / chaira / serrote pequeno; cabo de madeira com rebites."""
    antes = set(bpy.data.objects); aco = ferro(9, .25); mad = madeira(5, (.05, .03, .02))
    if tipo == "chaira":
        cyl(aco, (0, 0, -.16*s), .008*s, .3*s, verts=8, r2=.004*s)
    elif tipo == "serrote":
        box(aco, (0, 0, -.15*s), (.07*s, .003, .26*s), bevel=0)
        for k in range(12): box(aco, (-.036*s, 0, -.03*s - k*.02*s), (.012*s, .003, .01*s), (0, 45, 0), 0)
    else:
        o = box(aco, (0, 0, -.13*s), (.035*s, .003, .22*s), bevel=.001)
        sphere(aco, (.005*s, 0, -.24*s), (.018*s, .0015, .02*s), segs=8)
    box(mad, (0, 0, .05*s), (.03*s, .022*s, .11*s), bevel=.006)
    rebites(latao(), [(0, -.012*s, .02*s), (0, -.012*s, .08*s)], .004)
    return piv_de(antes, p, [math.radians(a) for a in rot])

def mosquedo(cx, cy, z, n, rr, raio=.12):
    """Varejeiras pousadas (pontinhos escuros e brilhantes): dá vida sem animação."""
    m = mosca_pouso()
    for k in range(n):
        a = rr.uniform(0, 6.28); d = rr.uniform(0, raio)
        sphere(m, (cx + math.cos(a)*d, cy + math.sin(a)*d, z + rr.uniform(0, .02)), (.007, .005, .004), segs=6)

# ================================================================ MATADOURO (Porão do Matadouro e Abatedouro Carniça)
@ef("cepo_cutelo", "matadouro", samples=56)
def cepo_cutelo():
    """Cepo de tronco de casca rachada com aro de ferro, topo de lenho talhado e encharcado, cutelo cravado de fio,
    um naco de costela e sangue escorrendo pela casca."""
    rr = rnd(501); fe = ferrugem(21); cs = casca(21)
    H = .56; rings = []
    for i in range(8):
        t = i/7; z = t*H; r = .3*(1.1 - .1*t) + (.06*(1 - i/2) if i < 2 else 0)
        rings.append([(math.cos(2*math.pi*k/32)*r*(1 + .045*math.sin(6*k*2*math.pi/32 + i*.7) + .02*math.sin(13*k*2*math.pi/32)),
                       math.sin(2*math.pi*k/32)*r*(1 + .045*math.sin(6*k*2*math.pi/32 + i*.7) + .02*math.sin(13*k*2*math.pi/32)), z) for k in range(32)])
    o = MT.aneis("cepo", rings, [cs], tampa=False); subdiv(o, 1); ondula(o, .01, .08, 1)
    o = cyl(topo_cepo(), (0, 0, H - .008), .3*1.0 - .004, .03, verts=40); displace(o, .006, .04, 2, 1)
    for k in range(22):   # talhos do cutelo
        x, y = rr.uniform(-.2, .2), rr.uniform(-.2, .2)
        box(sombra(), (x, y, H + .009), (rr.uniform(.06, .16), .005, .003), (0, 0, rr.uniform(0, 180)), 0)
    for z in (.12, .46): torus(fe, (0, 0, z), .3*(1.1 - .1*z/H) + .012, .016)
    rebites(fe, [(math.cos(a)*(.3*(1.1 - .1*z/H) + .028), math.sin(a)*(.3*(1.1 - .1*z/H) + .028), z) for a in (-2.6, -1.9, -1.2, -.5, .2) for z in (.12, .46)], .01)
    for k in range(6):    # raízes curtas
        a = k*1.047 + .3
        tubo(cs, [(math.cos(a)*.26, math.sin(a)*.26, .14), (math.cos(a)*.38, math.sin(a)*.38, .03), (math.cos(a)*.46, math.sin(a)*.46, .0)], [.07, .045, .015], 8, k, .2)
    cutelo((.06, -.03, H - .005), (0, 4, 30), 1.35)
    o = rovo(carne(23, .5), (-.11, .09, H + .035), (.13, .08, .03), (0, 0, .5), 14); subdiv(o, 1); ondula(o, .015, .05, 3)
    for k in range(4): along(osso((.6, .54, .43)), (-.2 + k*.045, .04 + k*.02, H + .045), (-.08 + k*.045, .16 + k*.02, H + .05), .012, verts=6)
    for k in range(4):    # escorridos pela casca no lado da câmera
        a = rr.uniform(-2.4, -.3)
        tubo(sangue(), [(math.cos(a)*.31, math.sin(a)*.31, H), (math.cos(a)*.325, math.sin(a)*.325, H - .14), (math.cos(a)*.33, math.sin(a)*.33, H - .25 - rr.uniform(0, .15))], [.014, .01, .005], 6, k, .2)
    poca(sangue(True), .1, -.15, .5, 503, 6, .001)
    for k in range(18): sphere(MT.solido("serragem", (.22, .15, .09), 0, .9), (rr.uniform(-.55, .55), rr.uniform(-.55, .55), .004), (.03, .02, .004), segs=6)
    mosquedo(-.11, .09, H + .065, 5, rr, .08)
    return {}

@ef("balde_miudos", "matadouro", samples=56)
def balde_miudos():
    """Dois baldes de chapa enferrujada: um cheio de miúdos até a borda, o outro tombado derramando tripa e sangue."""
    rr = rnd(511)
    balde((-.12, .12, 0), .16, .32)
    cyl(_c("sg_balde", lambda: K.mat_solid("sangue_balde", (.06, .004, .003), 0, .08)), (-.12, .12, .3), .155, .01, verts=24)
    for k in range(4):
        o = rovo(tripa(k % 3), (-.12 + rr.uniform(-.07, .07), .12 + rr.uniform(-.07, .07), .32), (.06, .045, .035), (0, 0, rr.uniform(0, 3)), 10)
    rovo(figado(), (-.08, .1, .34), (.07, .05, .025), (0, .3, .4), 12)
    # balde tombado, boca virada para a câmera
    balde((.2, -.1, .16), .15, .3, rot=(math.radians(-90), 0, math.radians(-30)))
    tripas((.14, -.36, 0), 4, .028, .34, 512)
    poca(sangue(), .1, -.38, .3, 513, 6, .002)
    poca(sangue(True), 0, 0, .55, 514, 6, .001)
    rovo(MT.carne(24, .3), (-.32, -.12, .03), (.07, .05, .03), (0, 0, .4), 10)
    mosquedo(.14, -.36, .07, 9, rr, .12)
    return {}

@ef("varal_linguica", "matadouro", fp=(2, 1), samples=56)
def varal_linguica():
    """Varal de defumar: cavaletes de madeira com uma vara de ferro, gomos de linguiça em laço e mantas de charque
    secando; pingos de gordura e serragem no chão."""
    rr = rnd(521); mad = madeira(25, (.07, .045, .03)); fe = ferro(25, .6)
    H = 1.45; X = .7
    for sx in (-1, 1):   # cavaletes em A
        for sy in (-1, 1): along(mad, (sx*X, sy*.28, 0), (sx*X, 0, H), .028, verts=8)
        along(mad, (sx*X, -.18, .45), (sx*X, .18, .45), .022, verts=8)
        box(fe, (sx*X, 0, H - .03), (.08, .1, .05), bevel=.006)
    along(fe, (-X - .1, 0, H), (X + .1, 0, H), .018, verts=10)
    for k in range(6):   # laços de linguiça
        x = -X + .2 + k*.22 + rr.uniform(-.02, .02); dz = rr.uniform(.35, .55)
        pts = [(x - .04, -.01, H), (x - .07, -.02, H - dz*.5), (x - .03, -.025, H - dz), (x + .03, -.025, H - dz), (x + .07, -.02, H - dz*.5), (x + .04, -.01, H)]
        linguica(pts, .034, 6, mat=defumado(k % 3, ((.1, .03, .018), (.075, .03, .02), (.12, .045, .025))[k % 3]), seed=k)
        torus(MT.solido("barbante", (.3, .25, .17), 0, .9), (x, 0, H + .005), .025, .004, (90, 0, 90))
    for k in range(2):   # mantas de charque (pendem por dobra na vara)
        x = -X + .5 + k*.9
        for lado in (-1, 1):
            o = rbox(defumado(7 + k, (.07, .022, .014)), (x, lado*.02, H - .22), (.15, .012, .42), (0, 0, 0), .004)
            sb = o.modifiers.new("s", 'SUBSURF'); sb.levels = sb.render_levels = 2; ondula(o, .02, .06, k*2 + (lado > 0))
            o.rotation_euler = (lado*.12, 0, 0)
    for k in range(9):   # pingos de gordura e sangue
        sphere(MT.solido("pingo_gordura", (.3, .24, .12), 0, .3), (rr.uniform(-X, X), rr.uniform(-.1, .1), .003), (.025, .02, .002), segs=8)
    poca(sangue(True), 0, 0, .35, 522, 4, .001)
    for k in range(20): sphere(MT.solido("serragem", (.22, .15, .09), 0, .9), (rr.uniform(-.9, .9), rr.uniform(-.4, .4), .004), (.03, .02, .004), segs=6)
    return {}

@ef("cabide_avental", "matadouro", samples=56)
def cabide_avental():
    """Cabideiro de ferro do magarefe: avental de couro duro de sangue, luvas de borracha, chapéu de feltro e
    as botas de cano alto largadas embaixo."""
    rr = rnd(531); fe = ferro(26, .55)
    along(fe, (0, 0, 0), (0, 0, 1.75), .022, verts=10)
    for k in range(3): along(fe, (0, 0, .02), (math.cos(k*2.1 + .4)*.3, math.sin(k*2.1 + .4)*.3, 0), .016, verts=6)
    cyl(fe, (0, 0, 1.76), .03, .03, verts=12)
    for k in range(4):   # ganchos do topo
        a = k*math.pi/2 + .78
        tubo(fe, [(0, 0, 1.68), (math.cos(a)*.12, math.sin(a)*.12, 1.66), (math.cos(a)*.16, math.sin(a)*.16, 1.72)], [.01, .009, .006], 6, k, .02)
    # avental: placa de couro curvada pendendo do gancho da frente (-Y)
    cr = couro_avental()
    rings = []
    for i in range(9):
        t = i/8; z = 1.62 - t*1.0; w = .14 + .14*min(1, t*2.2)
        rings.append([(-w + 2*w*k/10, -.13 - .05*math.sin(math.pi*k/10) - .02*t, z) for k in range(11)])
    vs, fs = [], []
    for r_ in rings: vs += r_
    for i in range(len(rings) - 1):
        for k in range(10): fs.append((i*11 + k, i*11 + k + 1, (i + 1)*11 + k + 1, (i + 1)*11 + k))
    o = MT.malha("avental", vs, fs, [cr]); s = o.modifiers.new("so", 'SOLIDIFY'); s.thickness = .012; subdiv(o, 2); ondula(o, .02, .07, 3)
    al = tubo(cr, [(-.06, -.12, 1.62), (0, -.13, 1.7), (.06, -.12, 1.62)], [.008]*3, 6, 1, 0)   # alça no pescoço
    for q in (o, al): q.rotation_euler = (0, 0, .785)
    # luvas penduradas no gancho de trás-direita
    for sx in (-1, 1):
        a = .78 + (sx > 0)*1.57
        base = Vector((math.cos(a)*.15, math.sin(a)*.15, 1.66))
        tubo(borracha(), [base, base + Vector((.0, .0, -.12)), base + Vector((sx*.02, -.02, -.3))], [.035, .04, .03], 10, 5 + sx, .1)
        for f in range(3): along(borracha(), base + Vector((sx*.02 + (f - 1)*.018, -.02, -.29)), base + Vector((sx*.02 + (f - 1)*.022, -.03, -.36)), .009, verts=6)
    # chapéu de feltro no topo
    ch = couro(2, (.035, .028, .022))
    cyl(ch, (.02, .02, 1.79), .16, .012, (6, -4, 0), 24); cyl(ch, (.02, .02, 1.85), .085, .11, (6, -4, 0), 20, r2=.075)
    torus(MT.solido("fita_chapeu", (.05, .01, .01), 0, .6), (.02, .02, 1.815), .085, .008, (6, -4, 0))
    # botas no chão
    bt = MT.solido("bota", (.025, .018, .014), 0, .5)
    for k, (x, y, rz) in enumerate(((.25, -.3, .2), (.42, -.16, -.4))):
        tubo(bt, [(x, y, .02), (x, y, .32 if k == 0 else .05), (x, y, .36 if k == 0 else .07)], [.055, .052, .05], 12, k, .05)
        if k == 1: along(bt, (x, y, .05), (x + .3, y + .12, .05), .05, .045, verts=12)
        else: rovo(bt, (x + .06, y - .07, .04), (.06, .1, .04), (0, 0, rz), 12)
    poca(sangue(True), .15, -.2, .4, 532, 5, .001)
    return {}

@ef("bandeja_visceras", "matadouro", samples=56)
def bandeja_visceras():
    """Caixote virado de banco com uma bandeja de zinco amassada: coração, fígado, rins e tripa limpos para a salmoura."""
    rr = rnd(541); mad = madeira(27, (.09, .062, .04)); fe = ferrugem(27)
    W, D, H = .52, .42, .4
    for i in range(3):    # ripas com fresta entre elas, cantoneiras e a tampa por cima
        z = .07 + i*.125
        for sy in (-1, 1): box(mad, (0, sy*D/2, z), (W, .022, .1), (0, 0, rr.uniform(-1, 1)), .006)
        for sx in (-1, 1): box(mad, (sx*W/2, 0, z), (.022, D, .1), (0, 0, rr.uniform(-1, 1)), .006)
    for sx in (-1, 1):
        for sy in (-1, 1): box(mad, (sx*(W/2 - .015), sy*(D/2 - .015), H/2), (.045, .045, H), bevel=.006)
    box(sombra(), (0, 0, .2), (W - .04, D - .04, .36), bevel=0)
    for i in range(4): box(mad, (0, -D/2 + D/8 + i*D/4, H + .01), (W + .03, D/4 - .012, .022), bevel=.004)
    for sx in (-1, 1):
        for sy in (-1, 1): box(fe, (sx*W/2, sy*D/2, H - .04), (.05, .05, .07), bevel=.004)
    box(MT.solido("carimbo", (.1, .035, .025), 0, .9), (-.05, -D/2 - .012, .19), (.2, .004, .06), bevel=0)
    zn = zinco()
    o = box(zn, (0, 0, .445), (.6, .44, .05), bevel=.015); ondula(o, .006, .1, 2)
    box(_c("fundo_bandeja", lambda: K.mat_solid("fundo_bandeja", (.04, .006, .005), 0, .1)), (0, 0, .452), (.54, .38, .03), bevel=0)
    co = rovo(MT.carne(28, .2), (-.16, .06, .51), (.085, .075, .1), (.4, .2, 0), 14)                 # coração
    along(MT.solido("aorta", (.32, .2, .18), 0, .4), (-.16, .07, .6), (-.13, .11, .65), .025, verts=8)
    rovo(figado(), (.09, .08, .49), (.17, .11, .035), (0, 0, .3), 14)
    for k in range(2): rovo(figado(), (.2 - k*.09, -.11, .49), (.05, .035, .033), (0, 0, k), 10)       # rins
    tripas((-.07, -.09, .46), 3, .022, .2, 542)
    poca(sangue(), .25, -.22, .1, 543, 3, .001)
    pingos(sangue(), (.27, -.2, .4), .38, 3, rr)
    faca((.24, .15, .49), (90, 0, 70), 1.0)
    mosquedo(.09, .08, .52, 6, rr, .1)
    return {}

@ef("caveira_boi", "matadouro", samples=56)
def caveira_boi():
    """Cabeça de boi esfolada largada no chão: crânio com restos de carne, chifres longos, língua de fora e mandíbula solta."""
    rr = rnd(551); ob = osso((.5, .44, .34))
    rot = .35
    def R(x, y, z): c, s = math.cos(rot), math.sin(rot); return (c*x - s*y, s*x + c*y, z)
    o = MT.aneis("cranio_boi", [[R(math.cos(2*math.pi*k/16)*rx, yy + math.sin(2*math.pi*k/16)*rz*.2, .14 + math.sin(2*math.pi*k/16)*rz) for k in range(16)]
                                for yy, rx, rz in ((.2, .11, .09), (.12, .15, .12), (0, .14, .11), (-.15, .1, .08), (-.3, .075, .06), (-.38, .06, .04))], [ob])
    subdiv(o, 2); ondula(o, .01, .05, 1)
    for sx in (-1, 1):
        sphere(sombra(), R(sx*.09, -.02, .2), (.035, .03, .03), segs=10)                         # órbitas
        tubo(MT.solido("chifre", (.06, .05, .04), 0, .45), [R(sx*.12, .16, .2), R(sx*.26, .18, .24), R(sx*.38, .1, .33), R(sx*.42, .02, .44)],
             [.035, .028, .018, .004], 10, 3 + sx, .08)
        o = rovo(carne(29 + sx, .8), R(sx*.1, .05, .12), (.06, .08, .05), (0, 0, rot), 10); ondula(o, .015, .04, sx)
    sphere(sombra(), R(-.025, -.38, .14), (.015, .01, .02), segs=8); sphere(sombra(), R(.025, -.38, .14), (.015, .01, .02), segs=8)
    for k in range(6): box(ob, R(-.05 + k*.02, -.34, .07), (.016, .02, .02), bevel=.002)
    # mandíbula solta e torta
    tubo(ob, [R(-.15, -.4, .02), R(-.2, -.15, .03), R(-.16, .08, .05)], [.02, .022, .018], 8, 5, .05)
    tubo(MT.pele("porco", 7), [R(.0, -.33, .07), R(.04, -.45, .03), R(.02, -.52, .01)], [.04, .035, .02], 10, 6, .15).scale.z = .5   # língua
    poca(sangue(True), 0, -.1, .45, 552, 6, .001)
    for k in range(5): along(osso((.45, .4, .32)), (rr.uniform(-.5, .5), rr.uniform(-.5, .3), .015), (rr.uniform(-.5, .5), rr.uniform(-.5, .3), .02), .012, verts=6)
    mosquedo(.05, .0, .25, 6, rr, .1)
    return {}

@ef("pedra_amolar", "matadouro", samples=56)
def pedra_amolar():
    """Esmeril de pedal: rebolo de arenito num cavalete de madeira, bacia de água ferruginosa embaixo, facas esperando a vez."""
    rr = rnd(561); mad = madeira(28, (.07, .046, .03)); fe = ferro(28, .6)
    for sx in (-1, 1):
        for sy in (-1, 1): along(mad, (sx*.32, sy*.2, 0), (sx*.24, sy*.08, .62), .03, verts=8)
        box(mad, (sx*.24, 0, .64), (.08, .26, .07), bevel=.008)
    for sx in (-1, 1): box(mad, (0, sx*.17, .2), (.64, .05, .05), bevel=.006)
    pd = _c("arenito", lambda: K.mat_stone("rebolo_mt", (.2, .17, .13), (.09, .08, .065), 6.0, 0, None, 1.0, 12.0))
    o = cyl(pd, (0, 0, .78), .26, .1, (0, 90, 0), 40); displace(o, .004, .03, 3, 1)
    cyl(fe, (0, 0, .78), .05, .26, (0, 90, 0), 12); cyl(fe, (0, 0, .78), .08, .12, (0, 90, 0), 16)
    along(fe, (.33, 0, .78), (.33, -.05, .5), .012, verts=6)                             # biela até o pedal
    box(mad, (.2, -.18, .06), (.4, .12, .03), (0, 0, 10), .006)                          # pedal
    along(fe, (.33, -.05, .5), (.28, -.17, .08), .01, verts=6)
    # bacia de água embaixo do rebolo
    cyl(zinco(), (0, 0, .5), .2, .08, verts=24, r2=.24)
    cyl(_c("agua_ferro", lambda: K.mat_solid("agua_ferruginosa", (.05, .025, .012), 0, .05)), (0, 0, .535), .22, .006, verts=24)
    box(mad, (0, 0, .44), (.5, .3, .03), bevel=.006)
    for sx in (-1, 1): box(mad, (sx*.22, 0, .25), (.04, .28, .4), bevel=.006)
    # faisca de rebarba no chão: limalha
    for k in range(25): sphere(MT.solido("limalha", (.1, .06, .04), .6, .4), (rr.uniform(-.3, .3), rr.uniform(-.4, -.1), .003), (.008, .008, .002), segs=5)
    faca((-.3, -.32, .015), (90, 0, 20), 1.0); faca((-.12, -.38, .015), (90, 0, -40), .9, "chaira"); faca((.05, -.42, .015), (90, 0, 75), 1.0, "serrote")
    return {}

@ef("balanca_gancho", "matadouro", samples=56)
def balanca_gancho():
    """Balança de gancho num tripé de vigas: mostrador de latão com ponteiro, pernil pendurado no prato e contrapeso de ferro."""
    rr = rnd(571); fe = ferro(29, .55); lt = latao()
    H = 1.8
    for k in range(3):
        a = k*2.094 + .5
        along(fe, (math.cos(a)*.45, math.sin(a)*.45, 0), (0, 0, H), .025, verts=8)
        box(fe, (math.cos(a)*.45, math.sin(a)*.45, .015), (.1, .1, .03), (0, 0, math.degrees(a)), .005)
    cyl(fe, (0, 0, H), .05, .08, verts=14)
    torus(fe, (0, 0, H - .06), .025, .007, (90, 0, 0))
    # corpo da balança: mostrador redondo virado para a câmera
    along(fe, (0, 0, H - .08), (0, 0, H - .2), .008, verts=6)
    cyl(lt, (0, -.01, H - .32), .13, .05, (90, 0, 0), 32)
    cyl(MT.solido("mostrador", (.36, .33, .26), 0, .4), (0, -.037, H - .32), .11, .004, (90, 0, 0), 32)
    for k in range(12):   # marcas
        a = k*math.pi/6
        box(sombra(), (math.sin(a)*.09, -.04, H - .32 + math.cos(a)*.09), (.004, .002, .018), (0, math.degrees(a), 0), 0)
    along(MT.solido("ponteiro", (.08, .01, .01), 0, .4), (0, -.042, H - .32), (.07, -.042, H - .27), .004, verts=4)
    torus(lt, (0, -.01, H - .32), .13, .01, (90, 0, 0))
    along(fe, (0, 0, H - .45), (0, 0, H - .58), .008, verts=6)
    gancho(fe, (0, 0, H - .6), 1.1)
    pernil((0, 0, H - .8), 1.3, -.2, 31)
    pingos(sangue(), (0, -.02, H - 1.5), .3, 4, rr)
    poca(sangue(), 0, -.05, .22, 572, 4, .002)
    # contrapesos no chão
    for k, (x, y) in enumerate(((.3, -.25), (.42, -.12))):
        cyl(fe, (x, y, .05), .06 - k*.01, .1 - k*.02, verts=16, r2=.05 - k*.01); torus(fe, (x, y, .11 - k*.02), .018, .006)
    return {}

@ef("caixote_ossos", "matadouro", samples=56)
def caixote_ossos():
    """Caixote de ripas cheio de ossos de tutano para o caldo do cerco, uma caveira de chifres por cima e o carimbo do Carniça."""
    rr = rnd(581); mad = madeira(30, (.07, .05, .033))
    W, D, H = .62, .46, .42
    for i in range(4):
        z = .05 + i*.105
        for sy in (-1, 1): box(mad, (0, sy*D/2, z), (W, .025, .085), bevel=.006)
        for sx in (-1, 1): box(mad, (sx*W/2, 0, z), (.025, D, .085), bevel=.006)
    for sx in (-1, 1):
        for sy in (-1, 1): box(mad, (sx*(W/2 - .02), sy*(D/2 - .02), H/2), (.05, .05, H), bevel=.006)
    box(sombra(), (0, 0, .2), (W - .04, D - .04, .35), bevel=0)
    box(MT.solido("carimbo", (.08, .03, .025), 0, .9), (-.08, -D/2 - .014, .27), (.2, .004, .06), bevel=0)
    ob = osso((.52, .46, .36))
    for k in range(22):
        a = Vector((rr.uniform(-.25, .25), rr.uniform(-.17, .17), H + rr.uniform(-.06, .05)))
        d = Vector((rr.uniform(-1, 1), rr.uniform(-1, 1), rr.uniform(-.4, .4))).normalized()*rr.uniform(.14, .28)
        along(ob, a, a + d, rr.uniform(.015, .025), verts=8)
        for p in (a, a + d): sphere(ob, p, (.03, .028, .026), segs=8)
    caveira((.05, -.02, H + .04), 1.0, .4, chifre=True)
    # alguns caíram fora
    for k in range(4):
        a = Vector((rr.uniform(-.5, .5), rr.uniform(-.5, -.3), .015)); along(ob, a, a + Vector((rr.uniform(-.2, .2), rr.uniform(-.1, .1), 0)), .016, verts=6)
    along(MT.ferrugem(30), (-.4, -.35, .05), (-.15, -.48, .02), .01, verts=6)          # pé de cabra
    return {}

@ef("faqueiro_parede", "matadouro", samples=56)
def faqueiro_parede():
    """Quadro de ferramentas do magarefe em pé: tábua grossa num cavalete de ferro com facas, cutelos, serrote e chaira
    pendurados, um amolador de couro e o rol de encomendas pregado."""
    antes = set(bpy.data.objects)
    rr = rnd(591); mad = madeira(31, (.075, .05, .033)); fe = ferro(31, .6)
    for sx in (-1, 1):
        along(fe, (sx*.4, 0, 0), (sx*.4, 0, 1.55), .02, verts=8)
        along(fe, (sx*.4, -.2, 0), (sx*.4, 0, .5), .014, verts=6); along(fe, (sx*.4, .2, 0), (sx*.4, 0, .5), .014, verts=6)
    o = box(madeira(34, (.045, .03, .02)), (0, .0, 1.15), (.92, .05, .6), bevel=.01); ondula(o, .004, .1, 3)
    box(fe, (0, -.03, 1.4), (.9, .02, .025), bevel=.003)
    rebites(latao(), [(x, -.032, 1.4) for x in (-.4, -.2, 0, .2, .4)], .008)
    ganchos = [(-.36, "faca"), (-.26, "faca"), (-.17, "chaira"), (.18, "serrote"), (.36, "faca")]
    for x, t in ganchos: faca((x, -.05, 1.38), (0, 0, 0), 1.35, t)
    cutelo((-.02, -.05, 1.05), (90, 0, 0), 1.0, False); cutelo((.04, -.05, .9), (90, 0, 180), .85, False)
    # amolador de couro e papel pregado
    tubo(couro(3, (.09, .06, .04)), [(.27, -.04, 1.4), (.27, -.045, 1.2), (.27, -.04, 1.0)], [.025, .024, .022], 6, 3, .02).scale.y = .3
    pap = _c("papel_rol", lambda: K.mat_cloth("papel_rol", (.32, .27, .19), 33.0))
    o = rbox(pap, (.1, -.03, .98), (.18, .004, .24), (0, .08, 0), .001); ondula(o, .006, .05, 4)
    for k in range(6): box(MT.solido("tinta", (.03, .02, .015), 0, .9), (.09 + rr.uniform(-.02, .02), -.034, 1.06 - k*.035), (.12, .002, .006), bevel=0)
    sphere(sangue(True), (.13, -.034, .92), (.03, .002, .025), segs=8)
    for k in range(5): pingos(sangue(), (rr.uniform(-.38, .38), -.06, 1.1), .9, 2, rr)
    poca(sangue(True), 0, -.15, .35, 592, 4, .001)
    balde((.32, -.32, 0), .12, .24)
    piv_de(antes, (0, 0, 0), (0, 0, .55))
    return {}

@ef("pernis_tripe", "matadouro", samples=56)
def pernis_tripe():
    """Tripé de ferro com corrente e três pernis curando no sal, um deles já cinzento de bolor; bacia de sal por baixo."""
    rr = rnd(601); fe = ferro(32, .6)
    H = 1.6
    for k in range(3):
        a = k*2.094 + .2
        along(fe, (math.cos(a)*.42, math.sin(a)*.42, 0), (0, 0, H), .022, verts=8)
    cyl(fe, (0, 0, H), .06, .06, verts=14)
    torus(fe, (0, 0, H - .25), .2, .012)
    for k in range(3):
        a = k*2.094 + .2 + 1.05
        corrente(fe, (0, 0, H - .03), (math.cos(a)*.2, math.sin(a)*.2, H - .25))
        p = Vector((math.cos(a)*.2, math.sin(a)*.2, H - .25))
        gancho(fe, (p.x, p.y, p.z - .18), .9, a)
        top = p.z - .37
        pernil((p.x, p.y, top), 1.05, a - math.pi/2 + .3*(k - 1), 33 + k, mofo=(k == 1))
        for j in range(8): sphere(sal_sujo(), (p.x + rr.uniform(-.12, .12), p.y + rr.uniform(-.12, .12), top - rr.uniform(.1, .45)), (.012, .012, .008), segs=5)
    cyl(madeira(33, (.06, .04, .028)), (0, 0, .06), .36, .12, verts=28, r2=.4)
    o = cyl(sal_sujo(), (0, 0, .12), .37, .03, verts=28); displace(o, .015, .04, 9, 1)
    for k in range(30): sphere(sal_sujo(), (rr.uniform(-.6, .6), rr.uniform(-.6, .6), .005), (.015, .015, .006), segs=5)
    return {}

@ef("restos_carne_chao", "matadouro", samples=40, chao=True)
def restos_carne_chao():
    """Decalque de chão: aparas de carne, nacos de gordura, um osso de joelho e sangue pisado com marcas de bota."""
    rr = rnd(611)
    poca(sangue(True), 0, 0, .55, 612, 7, .001)
    poca(sangue(), .1, -.05, .3, 613, 5, .002)
    for k in range(9):
        m = carne(40 + k % 3, .6) if k % 2 else gordura(40 + k % 3)
        o = rovo(m, (rr.uniform(-.45, .45), rr.uniform(-.35, .35), .015), (rr.uniform(.03, .07), rr.uniform(.025, .05), .018), (0, 0, rr.uniform(0, 3)), 10); ondula(o, .01, .04, k)
    along(osso((.5, .45, .36)), (-.2, .2, .025), (.02, .26, .03), .02, verts=8); sphere(osso((.5, .45, .36)), (-.21, .2, .03), (.04, .035, .03), segs=10)
    tripas((.25, .15, 0), 2, .018, .16, 614)
    for k in range(4):   # pegadas de bota no sangue
        x, y = -.35 + k*.2, -.3 + (k % 2)*.12
        rovo(MT.solido("pegada", (.03, .004, .003), 0, .4), (x, y, .0025), (.05, .022, .001), (0, 0, .3), 10)
    mosquedo(.0, .0, .03, 7, rr, .3)
    return {}

# ================================================================ EGITO (Hawara, Coração Endurecido e as ruínas de fora)
# Materiais e desenhos do egito.py (calcário, granito, faiança, ouro velho, linho, tinta gasta). Emissivo da área:
# turquesa de faiança; fogo só nas lamparinas e no incensário.
def _eg():
    import egito as EG; return EG

def pao_mat(seed=0, c=(.3, .18, .08)):
    return _c(("pao", seed, c), lambda: K.mat_stone(f"pao_mt_{seed}", c, (c[0]*.5, c[1]*.45, c[2]*.4), 7.0, 0, None, 1.0, 60.0 + seed))
def papiro(seed=0): return _c(("papiro", seed), lambda: K.mat_cloth(f"papiro_mt_{seed}", (.4, .34, .21), 70.0 + seed))
def uva(): return _c("uva", lambda: K.mat_metal("uva_mt", (.06, .02, .05), 0, 71.0, .25))
def figo(): return _c("figo", lambda: K.mat_stone("figo_mt", (.12, .05, .07), (.06, .025, .035), 9.0, 0, None, 1.0, 72.0))
def ebano(): return _c("ebano", lambda: K.mat_wood("ebano_mt", (.025, .018, .014), 73.0))
def alabastro(seed=0):
    return _c(("alab", seed), lambda: K.mat_stone(f"alabastro_mt_{seed}", (.55, .5, .4), (.4, .35, .26), 4.0, 0, None, .6, 74.0 + seed))

@ef("mesa_oferendas", "egito", samples=56, dungeon=False)
def mesa_oferendas():
    """Mesa de oferendas (hotep) de calcário com bica: pães cônicos e redondos, figos, um cacho de uva, um ganso
    depenado, flores de lótus murchas e a jarra de cerveja, tudo que os vivos ainda deixam para os mortos do Faium."""
    EG = _eg(); rr = rnd(701); cal = EG.calcario(701, blocos=False, tom=1, erosao=.3)
    box(cal, (0, 0, .06), (.95, .62, .12), bevel=.015)
    box(cal, (0, 0, .2), (.78, .5, .16), bevel=.012)
    rbox(cal, (0, -.33, .16), (.14, .16, .06), (0, 0, 0), .01)                       # bica
    box(EG.sombra(), (0, -.33, .19), (.05, .17, .01), bevel=0)
    mb = EG.MB(); EG.relevo(mb, (-.32, -.252, .14), (1, 0, 0), (0, 0, 1), (0, -1, 0), EG.glifo(4), .12, .004, 0, 0)
    EG.relevo(mb, (.2, -.252, .14), (1, 0, 0), (0, 0, 1), (0, -1, 0), EG.glifo(0), .12, .004)
    mb.build(EG.tinta("ocre", 702, .5), "glifos", .002)
    z = .28
    for k in range(3):   # pães cônicos de molde
        x = -.28 + k*.1
        cyl(pao_mat(k), (x, .1, z + .1), .045, .2, verts=12, r2=.012)
    for k in range(3):   # pães redondos achatados
        o = rovo(pao_mat(3 + k, (.34, .22, .1)), (-.1 + k*.11, .14, z + .025), (.06, .06, .028), (0, 0, 0), 12); EG.ondula if False else None
    for k in range(6): sphere(figo(), (.1 + rr.uniform(-.06, .06), -.05 + rr.uniform(-.05, .05), z + .025), (.025, .025, .028), segs=8)
    for k in range(14):  # cacho de uva
        a = k*.9; r_ = .025 + (k % 4)*.006
        sphere(uva(), (.27 + math.cos(a)*r_, -.06 + math.sin(a)*r_*.6, z + .02 + (k//4)*.012), (.016, .016, .016), segs=8)
    # ganso depenado, pescoço caído pela borda
    gp = MT.pele("anjo", 9)
    o = rovo(gp, (-.15, -.08, z + .06), (.14, .08, .065), (0, 0, .3), 14)
    tubo(gp, [(-.03, -.04, z + .07), (.05, -.1, z + .04), (.1, -.2, z - .02), (.12, -.27, z - .1)], [.025, .02, .018, .015], 8, 3, .05)
    for k in range(2): along(MT.solido("pe_ganso", (.3, .16, .05), 0, .6), (-.28, -.1 + k*.05, z + .05), (-.36, -.12 + k*.07, z + .02), .01, verts=5)
    # lótus murchas (sépalas abertas, azul gasto)
    lt = EG.tinta("azul", 703, .55)
    for k in range(3):
        x, y = .02 + k*.1, .18
        along(MT.solido("caule_lotus", (.08, .1, .04), 0, .7), (x, y, z), (x + .12, y + .12, z - .2 + k*.03), .006, verts=4)
        for j in range(6):
            a = j*1.047; rbox(lt, (x + math.cos(a)*.025, y + math.sin(a)*.025, z + .02), (.045, .02, .006), (0, .5, a), .002)
    EG.jarro((.36, .16, z), EG.barro((.24, .12, .065)), .3, .09, rr)
    cyl(EG.barro((.3, .22, .13), 1), (.12, .16, z + .02), .06, .04, verts=14, r2=.04)
    for k in range(5): rovo(EG.barro(), (rr.uniform(-.5, .5), -.45 - rr.uniform(0, .1), .01), (.04, .03, .01), (0, 0, rr.uniform(0, 6)), 6)
    return {}

@ef("ushabtis", "egito", samples=56, dungeon=False)
def ushabtis():
    """Caixa de ushabtis em forma de capela, pintada e de tampa caída: dezenas de servidores de faiança azul enfileirados
    ("aqui estou") e alguns tombados no chão, um partido ao meio."""
    EG = _eg(); rr = rnd(711); md = EG.madeira(711, (.07, .045, .028))
    W, D, H = .5, .34, .28
    box(md, (0, 0, H/2), (W, D, H), bevel=.008)
    box(EG.sombra(), (0, 0, H - .005), (W - .04, D - .04, .02), bevel=0)
    for k in range(4): box(md, (0, 0, .015 + k*.0), (W + .04, D + .04, .03), bevel=.006) if k == 0 else None
    pt = EG.tinta("amarelo", 712, .35, (.06, .04, .025)); az = EG.tinta("azul", 713, .4, (.06, .04, .025))
    rbox(pt, (0, -D/2 - .002, H*.55), (W - .06, .004, H*.6), (0, 0, 0), 0)
    mb = EG.MB(); EG.relevo(mb, (-.18, -D/2 - .004, .08), (1, 0, 0), (0, 0, 1), (0, -1, 0), EG.glifo(12), .14, .003)
    EG.relevo(mb, (.05, -D/2 - .004, .08), (1, 0, 0), (0, 0, 1), (0, -1, 0), EG.glifo(8), .14, .003); mb.build(az, "glifos", .001)
    # tampa abobadada caída de lado
    o = cyl(md, (W/2 + .2, -.15, .1), .17, W*.95, (0, 90, 20), 16); o.scale = (1, .7, 1)
    fai = EG.faianca_fosca()
    def ush(p, rot=(0, 0, 0), s=1.0):
        antes = set(bpy.data.objects)
        cyl(fai, (0, 0, .045*s), .016*s, .09*s, verts=8, r2=.012*s)
        sphere(fai, (0, 0, .1*s), (.017*s, .016*s, .02*s), segs=8)
        cyl(fai, (0, 0, .087*s), .022*s, .025*s, verts=8, r2=.012*s)         # peruca tripartida
        box(EG.sombra(), (0, -.016*s, .05*s), (.022*s, .002, .04*s), bevel=0)  # coluna de texto
        piv_de(antes, p, rot)
    for i in range(4):
        for j in range(6): ush((-W/2 + .06 + j*.075, -D/2 + .06 + i*.075, H - .1))
    for k in range(7):
        a = rr.uniform(0, 6.28); ush((.0 + rr.uniform(-.45, .2), -.35 - rr.uniform(0, .25), .018), (math.pi/2, 0, a))
    for k in range(3): ush((-.42 + k*.07, -.2, 0), (0, 0, rr.uniform(-.3, .3)))
    return {}

@ef("cesto_papiros", "egito", samples=56, dungeon=False)
def cesto_papiros():
    """Cesto de junco cheio de rolos de papiro atados com fita de linho, e um rolo aberto no chão com colunas de escrita
    hierática e uma vinheta vermelha (o Livro dos Mortos de alguém que não chegou a ser enterrado)."""
    EG = _eg(); rr = rnd(721)
    EG.cesto((-.15, .1, 0), rr, .2, .3, cheio=False)
    for k in range(9):
        a = rr.uniform(0, 6.28); d = rr.uniform(0, .11)
        x, y = -.15 + math.cos(a)*d, .1 + math.sin(a)*d
        o = cyl(papiro(k % 3), (x, y, .3), .028, .32, (rr.uniform(-25, 25), rr.uniform(-25, 25), 0), 12)
        torus(EG.linho((.3, .26, .18), 2), (x, y, .3), .03, .004, (rr.uniform(-25, 25), rr.uniform(-25, 25), 0))
    # rolo aberto
    pap = papiro(5)
    o = rbox(pap, (.2, -.22, .004), (.62, .2, .004), (0, 0, .35), .001)
    sb = o.modifiers.new("s", 'SUBSURF'); sb.levels = sb.render_levels = 2; ondula(o, .006, .08, 3)
    cyl(pap, (.47, -.03, .03), .03, .21, (90, 0, 20), 12); cyl(pap, (-.07, -.42, .025), .022, .21, (90, 0, 20), 12)
    tinta_p = MT.solido("tinta_preta_pap", (.02, .016, .012), 0, .8); tinta_v = MT.solido("tinta_verm_pap", (.18, .03, .015), 0, .8)
    c, sn = math.cos(.35), math.sin(.35)
    for k in range(9):
        t = -.24 + k*.05
        for j in range(5):
            u = -.07 + j*.035
            if rr.random() < .8:
                x, y = .2 + c*t - sn*u, -.22 + sn*t + c*u
                rbox(tinta_p if k != 4 else tinta_v, (x, y, .0075), (.012, .02, .001), (0, 0, .35 + rr.uniform(-.3, .3)), 0)
    return {}

@ef("incensario_braco", "egito", samples=56, dungeon=False)
def incensario_braco():
    """Incensário em forma de braço, de bronze verde: cabo de papiro com cabeça de falcão numa ponta e a mão aberta na
    outra segurando a taça com brasa; pousado num suporte de calcário, com as bolinhas de resina num prato."""
    EG = _eg(); rr = rnd(731); bz = EG.bronze(731); cal = EG.calcario(731, blocos=False, tom=0, erosao=.4)
    cyl(cal, (0, 0, .3), .1, .6, verts=16, r2=.08); cyl(cal, (0, 0, .03), .16, .06, verts=16); cyl(cal, (0, 0, .62), .13, .04, verts=16)
    z = .66
    along(bz, (-.32, -.05, z + .02), (.28, .05, z + .04), .016, verts=10)
    tubo(bz, [(-.32, -.05, z + .02), (-.36, -.06, z + .05), (-.4, -.07, z + .06)], [.022, .026, .018], 8, 1, .05)   # cabeça de falcão
    cyl(bz, (-.415, -.07, z + .05), .01, .03, (0, 75, 0), 6, r2=.002)
    for sx in (.0, -.12):
        cyl(bz, (sx, -.03 + sx*.2, z + .045), .016, .04, verts=8)                     # caixinha de resina no meio
    # mão aberta com a taça
    sphere(bz, (.3, .055, z + .045), (.035, .03, .015), segs=10)
    for f in range(4): along(bz, (.32, .04 + f*.012, z + .05), (.36, .03 + f*.016, z + .07), .006, verts=5)
    cyl(bz, (.32, .05, z + .09), .045, .05, verts=16, r2=.03)
    cyl(MT.brasa(7), (.32, .05, z + .112), .038, .008, verts=14)
    for k in range(5): sphere(MT.brasa(10), (.32 + rr.uniform(-.02, .02), .05 + rr.uniform(-.02, .02), z + .118), (.01, .01, .006), segs=6)
    point((.32, .05, z + .2), (1, .45, .15), 18, .05, "brasa_incenso")
    # prato de resina
    cyl(EG.barro((.24, .12, .065)), (-.18, -.2, .02), .09, .025, verts=16, r2=.07)
    for k in range(10): sphere(MT.solido("resina", (.25, .14, .04), 0, .3), (-.18 + rr.uniform(-.05, .05), -.2 + rr.uniform(-.05, .05), .04), (.012, .012, .01), segs=6)
    return {"emissivo": "brasa do incenso", "luz": "fogo"}

@ef("vasos_alabastro", "egito", samples=56, dungeon=False)
def vasos_alabastro():
    """Vasos de alabastro translúcido do enxoval: a taça em lótus, um vaso de unguento com tampa, uma jarra alta, e
    os cacos de um que caiu."""
    EG = _eg(); rr = rnd(741); al = alabastro(1)
    al.node_tree.nodes.get("Principled BSDF").inputs["Subsurface Weight"].default_value = .3
    rings = []
    for t, r in ((0, .07), (.05, .05), (.1, .035), (.14, .05), (.2, .09), (.26, .12), (.3, .13)):   # taça em lótus
        rings.append([(-.2 + math.cos(2*math.pi*k/20)*r*(1 + .06*math.cos(16*math.pi*k/20)), .05 + math.sin(2*math.pi*k/20)*r*(1 + .06*math.cos(16*math.pi*k/20)), t) for k in range(20)])
    o = MT.aneis("taca", rings, [al], tampa=True); subdiv(o, 1)
    cyl(EG.sombra(), (-.2, .05, .295), .115, .006, verts=20)
    rings = []
    for t, r in ((0, .07), (.04, .08), (.15, .11), (.28, .1), (.36, .06), (.4, .065)):
        rings.append([(.1 + math.cos(2*math.pi*k/20)*r, .12 + math.sin(2*math.pi*k/20)*r, t) for k in range(20)])
    MT.aneis("unguento", rings, [al]); sphere(al, (.1, .12, .43), (.07, .07, .03), segs=12)
    rings = []
    for t, r in ((0, .05), (.06, .07), (.3, .1), (.5, .085), (.58, .045), (.62, .055)):
        rings.append([(.0 + math.cos(2*math.pi*k/20)*r, .3 + math.sin(2*math.pi*k/20)*r, t) for k in range(20)])
    MT.aneis("jarra_alta", rings, [al])
    for sx in (-1, 1): torus(al, (sx*.09, .3, .44), .03, .01, (90, 0, 0))
    for k in range(9):   # cacos
        a = rr.uniform(0, 6.28); d = rr.uniform(.05, .3)
        rbox(alabastro(2), (.25 + math.cos(a)*d, -.2 + math.sin(a)*d, .01), (rr.uniform(.03, .08), rr.uniform(.02, .05), .008), (rr.uniform(-.3, .3), rr.uniform(-.3, .3), a), .003)
    rbox(EG.tinta("azul", 742, .5, (.55, .5, .4)), (-.2, -.08, .2), (.002, .002, .002), (0, 0, 0), 0)
    return {}

@ef("cabeca_farao", "egito", fp=(2, 1), samples=56, dungeon=False)
def cabeca_farao():
    """Cabeça de granito de um faraó caída da estátua: toucado nemes listrado com restos de azul e ouro, o nariz
    quebrado, a barba postiça partida, meio afundada no lodo e no calcário que caiu junto."""
    EG = _eg(); rr = rnd(751); gr = EG.granito("rosa", 751, .45)
    antes = set(bpy.data.objects)
    EG.cabeca_nemes(gr, (EG.tinta("azul", 752, .5, (.3, .2, .18)), EG.tinta("amarelo", 754, .55, (.3, .2, .18))), (0, 0, 0), .75, rr, quebrado=True)
    piv = piv_de(antes, (0, 0, .52), (.12, -.22, -.6))
    EG.entulho(rr, (.1, .1, 0), .7, 7, EG.calcario(753, blocos=False, tom=1), (.08, .2))
    EG.pedriscos(rr, (0, 0), .8, 50)
    return {}

@ef("harpa_arco", "egito", samples=56, dungeon=False)
def harpa_arco():
    """Harpa de arco dos músicos do templo, de madeira com a cabeça de faraó entalhada no pé, cordas de tripa quase
    todas arrebentadas, e um sistro de bronze de Hathor largado ao lado."""
    EG = _eg(); rr = rnd(761); md = EG.madeira(761, (.08, .05, .03)); antes_h = set(bpy.data.objects)
    pts = []
    for k in range(10):   # braço em arco: sai da caixa e sobe em curva aberta
        a = k/9*2.0
        pts.append((.18 - math.sin(a)*.32 - k*.01, 0, .12 + (1 - math.cos(a))*.42))
    tubo(md, pts, [.042 - k*.0025 for k in range(10)], 10, 1, .03)
    rings = []                              # caixa de ressonância em pá, deitada
    for t, r in ((0, .02), (.15, .08), (.45, .11), (.75, .1), (1.0, .05)):
        rings.append([(.18 - t*.36, math.cos(2*math.pi*k/14)*r, .1 + math.sin(2*math.pi*k/14)*r*.55) for k in range(14)])
    caixa = MT.aneis("caixa_harpa", rings, [md]); subdiv(caixa, 1)
    for k in range(5): rbox(EG.tinta("azul" if k % 2 else "amarelo", 762 + k % 2, .4, (.08, .05, .03)), (.12 - k*.06, 0, .158), (.03, .1, .004), (0, 0, 0), 0)
    sphere(md, (.2, 0, .1), (.06, .055, .07), segs=12)                           # cabeça entalhada no pé
    rbox(EG.tinta("azul", 766, .3, (.08, .05, .03)), (.21, 0, .14), (.07, .09, .03), (0, 0, 0), .01)  # peruca
    corda_m = MT.solido("corda_tripa", (.35, .3, .2), 0, .5)
    top = [Vector(p) for p in pts]
    for k in range(8):
        a = Vector(top[min(9, 2 + k)]); b = Vector((-.15 + k*.04, 0, .14))
        if k in (1, 3, 4, 6): along(corda_m, a, b, .003, verts=4)
        else: along(corda_m, a, a.lerp(b, rr.uniform(.15, .35)), .0025, verts=4)
    piv_de(antes_h, (0, 0, 0), (0, 0, .785))
    # todo o conjunto inclinado, encostado no chão
    antes = set(bpy.data.objects)
    # sistro
    bz = EG.bronze(764)
    along(bz, (.35, -.3, .015), (.55, -.2, .015), .012, verts=8)
    o = torus(bz, (.63, -.16, .02), .07, .01, (0, 0, 0)); o.scale = (.7, 1.0, 1); o.rotation_euler = (0, 0, .45)
    for k in range(3): along(bz, (.58 + k*.03, -.22 + k*.01, .03), (.66 + k*.03, -.12 + k*.01, .03), .004, verts=4)
    sphere(EG.tinta("amarelo", 765, .5, (.2, .14, .06)), (.47, -.24, .03), (.03, .03, .025), segs=8)      # cara de Hathor
    return {}

@ef("cadeira_ebano", "egito", samples=56, dungeon=False)
def cadeira_ebano():
    """Cadeira de ébano do enxoval com pés de leão e encosto de folha de ouro gasta, o banquinho dos pés e o apoio de
    cabeça de alabastro; o assento de junco trançado afundou."""
    EG = _eg(); rr = rnd(771); eb = ebano(); au = EG.ouro(771)
    W, D, H = .5, .48, .42
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx*(W/2 - .04), sy*(D/2 - .04)
            tubo(eb, [(x, y, .06), (x, y, .22), (x, y, H)], [.026, .022, .02], 8, int(sx*3 + sy), .04)
            rovo(eb, (x + .02, y, .035), (.05, .04, .035), (0, 0, 0), 10)              # pata de leão
            cyl(au, (x, y, .065), .028, .02, verts=10)
    for sy in (-1, 1): box(eb, (0, sy*(D/2 - .04), H - .01), (W - .04, .035, .035), bevel=.006)
    for sx in (-1, 1): box(eb, (sx*(W/2 - .04), 0, H - .01), (.035, D - .04, .035), bevel=.006)
    o = box(EG.junco((.2, .15, .08)), (0, 0, H - .03), (W - .1, D - .1, .02), bevel=.004); ondula(o, .02, .1, 3); o.location.z -= .02
    # encosto inclinado com folha de ouro e o sol alado
    o = rbox(eb, (-W/2 + .02, 0, H + .3), (.03, D - .04, .6), (0, -.18, 0), .008)
    rbox(au, (-W/2 + .045, 0, H + .32), (.004, D - .12, .48), (0, -.18, 0), 0)
    mb = EG.MB(); EG.relevo(mb, (-W/2 + .07, -.17, H + .45), (0, 1, 0), (.18, 0, 1), (1, 0, 0), EG.fig_sol_alado(), .34, .006); mb.build(eb, "sol", .001)
    # banquinho e apoio de cabeça
    box(eb, (.42, -.2, .06), (.3, .2, .03), (0, 0, 20), .006)
    for k in range(4): box(eb, (.42 + (k % 2 - .5)*.22, -.2 + (k//2 - .5)*.12, .025), (.03, .03, .05), (0, 0, 20), .004)
    al = alabastro(3)
    rbox(al, (.2, -.42, .015), (.16, .07, .03), (0, 0, .4), .008)
    cyl(al, (.2, -.42, .09), .03, .13, verts=10)
    o = cyl(al, (.2, -.42, .16), .1, .07, (0, 90, 23), 16); o.scale.y = .6
    return {}

@ef("mumias_gato", "egito", samples=56, dungeon=False)
def mumias_gato():
    """Três múmias de gato de Bubástis em pé, enfaixadas em losango com a cara pintada e as orelhas de linho, e a
    Bastet de bronze sentada com o filhote; uma caiu e abriu."""
    EG = _eg(); rr = rnd(781)
    def gato(p, h=.42, rot=0.0, seed=0, deitado=False):
        antes = set(bpy.data.objects)
        ln = EG.linho((.32, .26, .17), seed); esc = EG.linho((.16, .11, .07), seed + 1)
        rings = []
        for t, r in ((0, .06), (.15, .085), .35 and (.4, .075), (.62, .05), (.72, .05), (.82, .07), (.95, .06), (1.0, .03)):
            rings.append([(math.cos(2*math.pi*k/16)*r, math.sin(2*math.pi*k/16)*r*.85, t*h) for k in range(16)])
        o = MT.aneis("gato", rings, [ln]); subdiv(o, 1)
        for k in range(9):   # faixas em losango (escuras, cruzadas)
            z = .06 + k*.045*h/.42
            o = torus(esc, (0, 0, z), .083 - abs(k - 3)*.006, .006, (14 if k % 2 else -14, 0, 0))
        rbox(EG.tinta("amarelo", 782 + seed, .3, (.3, .24, .16)), (0, -.055, .87*h), (.07, .004, .07), (0, 0, 0), 0)
        for sx in (-1, 1):
            sphere(EG.sombra(), (sx*.022, -.059, .89*h), (.012, .003, .008), segs=6)
            cyl(ln, (sx*.04, 0, h + .03), .022, .07, (sx*-15, 0, 0), 6, r2=.003)
        return piv_de(antes, p, (math.pi/2 if deitado else 0, 0, rot))
    gato((-.25, .12, 0), .44, 0, 1); gato((-.05, .2, 0), .36, .3, 2); gato((.25, -.15, .07), .4, 1.3, 3, deitado=True)
    for k in range(6): along(EG.linho((.3, .25, .16), 4), (.25 + rr.uniform(-.25, .25), -.35 + rr.uniform(-.1, .1), .005), (.25 + rr.uniform(-.3, .3), -.35 + rr.uniform(-.15, .15), .005), .008, verts=4)
    # Bastet de bronze
    bz = EG.bronze(783); x0, y0 = .2, .2
    cyl(bz, (x0, y0, .03), .09, .06, verts=16)
    rovo(bz, (x0, y0, .17), (.055, .065, .11), (0, 0, 0), 12); sphere(bz, (x0, y0 - .02, .31), (.045, .045, .045), segs=12)
    for sx in (-1, 1): cyl(bz, (x0 + sx*.025, y0 - .02, .36), .015, .05, verts=5, r2=.002)
    tubo(bz, [(x0 + .05, y0 + .05, .07), (x0 + .09, y0, .07), (x0 + .08, y0 - .06, .07)], [.012, .01, .006], 6, 5, .02)
    sphere(bz, (x0 - .06, y0 - .06, .1), (.03, .035, .045), segs=8)
    cyl(EG.faianca(6), (x0, y0 - .06, .26), .008, .004, (90, 0, 0), 6)                 # contas de faiança no colar
    return {}

@ef("lamparinas_chao", "egito", samples=56, dungeon=False)
def lamparinas_chao():
    """Lamparinas de barro acesas no chão diante de um nicho (o fogo dos que ainda rezam aqui), uma tigela de óleo,
    pavios de linho e amuletos ankh e olho de Hórus deixados como ex-voto."""
    EG = _eg(); rr = rnd(791)
    for k, (x, y) in enumerate([(-.2, -.05), (.0, -.15), (.18, .02), (-.05, .15)]):
        o = rovo(EG.barro((.2, .1, .05), k), (x, y, .035), (.1, .07, .035), (0, 0, k*.7), 12)
        cyl(EG.sombra(), (x, y, .07), .03, .006, verts=10)
        tubo(EG.barro((.2, .1, .05), k), [(x + .06*math.cos(k*.7), y + .06*math.sin(k*.7), .045), (x + .1*math.cos(k*.7), y + .1*math.sin(k*.7), .055)], [.025, .018], 8, k, .05)
        sphere(K.mat_emit("chama_lamp_ef", (1, .5, .15), 12), (x + .1*math.cos(k*.7), y + .1*math.sin(k*.7), .085), (.012, .012, .03), segs=6)
    point((0, 0, .6), (1, .55, .2), 14, .2, "lamparinas_luz")
    cyl(EG.barro((.24, .12, .065), 2), (.25, .25, .03), .1, .06, verts=16, r2=.08)
    cyl(MT.solido("oleo_lamp", (.05, .035, .012), 0, .05), (.25, .25, .058), .085, .004, verts=16)
    fai = EG.faianca_fosca()
    for k in range(5):
        a = rr.uniform(0, 6.28); d = rr.uniform(.25, .42); x, y = math.cos(a)*d, math.sin(a)*d - .1
        if k % 2:
            rbox(fai, (x, y, .006), (.05, .012, .006), (0, 0, a), .002); torus(fai, (x - .03*math.cos(a), y - .03*math.sin(a), .006), .015, .004)
        else:
            rovo(fai, (x, y, .006), (.025, .015, .005), (0, 0, a), 8)
    for k in range(12): sphere(MT.solido("cera_pingo", (.3, .26, .16), 0, .5), (rr.uniform(-.35, .35), rr.uniform(-.35, .3), .003), (.015, .015, .003), segs=6)
    return {"emissivo": "chama das lamparinas", "luz": "fogo"}

@ef("escaravelho_coracao", "egito", samples=56, dungeon=False)
def escaravelho_coracao():
    """Escaravelho do coração de pedra verde, do tamanho de um cão, num pedestal de calcário: as asas entalhadas e, na
    base, o feitiço 30B ("ó meu coração, não te levantes como testemunha contra mim")."""
    EG = _eg(); rr = rnd(801); cal = EG.calcario(801, blocos=False, tom=1, erosao=.4)
    box(cal, (0, 0, .08), (.7, .55, .16), bevel=.015); box(cal, (0, 0, .2), (.6, .46, .08), bevel=.01)
    mb = EG.MB(); EG.inscricao([(mb, 1)], (-.3, -.231, .17), (1, 0, 0), (0, 0, 1), (0, -1, 0), .6, .06, rr, 8, .004)
    EG.inscricao([(mb, 1)], (-.35, -.276, .02), (1, 0, 0), (0, 0, 1), (0, -1, 0), .7, .12, rr, 10, .005)
    mb.build(EG.tinta("ocre", 802, .5), "feitico", .002)
    vd = _c("pedra_verde", lambda: K.mat_stone("pedra_verde_mt", (.04, .09, .06), (.015, .035, .025), 6.0, 0, None, .5, 80.0))
    o = rovo(vd, (0, 0, .3), (.22, .17, .09), (0, 0, 0), 20); subdiv(o, 1)
    rovo(vd, (0, -.2, .29), (.09, .05, .06), (0, 0, 0), 14)                       # cabeça
    rovo(vd, (0, -.13, .32), (.12, .04, .05), (0, 0, 0), 12)                      # protórax
    box(EG.sombra(), (0, .04, .385), (.006, .26, .01), bevel=0)                    # sutura das asas
    box(EG.sombra(), (0, -.09, .37), (.2, .006, .01), bevel=0)
    for sx in (-1, 1):
        for k in range(3):
            along(vd, (sx*.12, -.08 + k*.1, .26), (sx*.22, -.12 + k*.12, .24), .015, verts=6)
    rovo(EG.ouro(803), (0, -.25, .3), (.025, .02, .02), (0, 0, 0), 8)
    return {"lore": "feitico_30b"}

@ef("modelo_barca", "egito", fp=(2, 1), samples=56, dungeon=False)
def modelo_barca():
    """Modelo de barca funerária de madeira pintada do enxoval: casco em lua, olho de Hórus na proa, remadores de
    madeira sentados, o dono sob o dossel e a vela de linho enrolada; sobre um suporte baixo."""
    EG = _eg(); rr = rnd(811); md = EG.madeira(811, (.11, .07, .04)); pt = EG.tinta("ocre", 812, .45, (.11, .07, .04))
    for x in (-.25, .25): box(md, (x, 0, .05), (.06, .22, .1), bevel=.008)
    rings = []
    L_ = .95
    for i in range(11):
        t = i/10; x = -L_/2 + t*L_; zc = .16 + .1*(2*t - 1)**4; w = .12*math.sin(math.pi*min(.98, max(.02, t)))**.6 + .01
        rings.append([(x, math.cos(math.pi*k/8)*w, zc - math.sin(math.pi*k/8)*w*.6) for k in range(9)])
    o = MT.aneis("casco", rings, [pt], tampa=True); s = o.modifiers.new("so", 'SOLIDIFY'); s.thickness = .01
    for sx in (-1, 1): tubo(md, [(sx*L_/2*.95, 0, .26), (sx*L_/2*1.02, 0, .33), (sx*L_/2*.98, 0, .37)], [.012, .01, .007], 6, 2 + sx, .02)
    mb = EG.MB(); EG.relevo(mb, (.3, -.07, .18), (1, 0, 0), (0, 0, 1), (0, -1, 0), EG.glifo(8), .1, .003); mb.build(EG.tinta("azul", 813, .3), "olho", .001)
    def remador(x, y):
        pl = EG.tinta("ocre", 814, .3, (.2, .1, .05))
        rovo(pl, (x, y, .2), (.02, .018, .035), (0, 0, 0), 8); sphere(EG.tinta("azul", 815, .2, (.02, .02, .02)), (x, y, .245), (.016, .016, .016), segs=8)
        along(md, (x + .02, y, .22), (x + .03, y - .17*(1 if y < 0 else -1), .12), .004, verts=4)
    for k in range(4):
        for y in (-.04, .04): remador(-.25 + k*.13, y)
    for x in (.15, .3):   # dossel
        for y in (-.05, .05): along(md, (x, y, .17), (x, y, .32), .006, verts=4)
    box(EG.linho((.32, .26, .17), 3), (.225, 0, .325), (.2, .14, .01), bevel=.002)
    rovo(EG.linho((.34, .3, .22), 4), (.225, 0, .21), (.05, .03, .03), (0, 0, 0), 8)
    along(md, (-.05, 0, .17), (-.05, 0, .5), .008, verts=6)
    cyl(EG.linho((.3, .25, .17), 5), (-.05, 0, .46), .02, .3, (0, 90, 0), 8)
    return {}

# ================================================================ CRIPTA (Câmara da Trombeta Calada, Ossário das Carpideiras, Catacumba das Raízes)
# Gótico de fim do mundo: pedra de cripta, ferro batido, latão com verdete, cera de vela, ossos, pano de luto.
# A cripta é a da Trombeta CALADA: trombetas amordaçadas e lacradas a cera são o motivo que amarra os três andares.
def cera(seed=0, c=(.42, .37, .27)):
    def f():
        m, nt, b = K.new_mat(f"cera_ef_{seed}")
        v = N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = noise(nt, v, None, 8, 5, .6, seed)
        cr = ramp(nt, [(.3, (c[0]*.7, c[1]*.68, c[2]*.6)), (.75, c)]); L(nt, n.outputs["Fac"], cr.inputs[0])
        col = K.grime(nt, cr.outputs[0], v, None, 1.5, .45)
        L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .45
        b.inputs["Subsurface Weight"].default_value = .35; b.inputs["Subsurface Radius"].default_value = (1, .7, .4); b.inputs["Subsurface Scale"].default_value = .03
        K.bump(nt, b, n.outputs["Fac"], .2, .005)
        return m
    return _c(("cera", seed, c), f)
def lacre(): return cera(9, (.24, .03, .025))
def pedra_cripta(seed=0): return _c(("pcr", seed), lambda: K.mat_stone(f"pedra_cripta_ef_{seed}", (.1, .095, .088), (.04, .038, .036), 3.0, .15, None, 1.6, 90.0 + seed))
def luto(seed=0): return _c(("luto", seed), lambda: K.mat_cloth(f"pano_luto_{seed}", (.03, .026, .028), 91.0 + seed))
def flor_seca(seed=0, c=(.16, .06, .05)): return _c(("flor", seed, c), lambda: K.mat_cloth(f"flor_seca_{seed}", c, 92.0 + seed))

def vela(p, h=.14, r=.02, acesa=True, luz=1.2, seed=0):
    """Vela de cera torta com escorridos e poça; chama pequena (o fogo da cripta)."""
    x, y, z = p; rr = rnd(seed)
    o = cyl(cera(seed % 3), (x, y, z + h/2), r, h, (rr.uniform(-6, 6), rr.uniform(-6, 6), 0), 10)
    for k in range(3):
        a = rr.uniform(0, 6.28)
        sphere(cera(seed % 3), (x + math.cos(a)*r, y + math.sin(a)*r, z + h - rr.uniform(.02, h*.7)), (.006, .006, rr.uniform(.015, .035)), segs=6)
    sphere(cera(seed % 3), (x, y, z + .004), (r*2.2, r*2.2, .006), segs=10)
    along(MT.sombra(), (x, y, z + h), (x, y, z + h + .012), .002, verts=4)
    if acesa:
        sphere(K.mat_emit("chama_vela_ef", (1, .58, .2), 22), (x, y, z + h + .028), (.008, .008, .022), segs=6)
        if luz: point((x, y, z + h + .07), (1, .55, .2), luz, .02, "vela_luz")

def trombeta(p, rot=(0, 0, 0), s=1.0, amassada=0.0, amordacada=True, seed=0):
    """Trombeta natural de latão (sem pistões): tubo longo dobrado em laço, campana aberta; amordaçada com pano e lacre."""
    antes = set(bpy.data.objects); rr = rnd(seed); lt = latao()
    L_ = .62*s
    pts = [(-L_/2, 0, 0), (-L_/4, 0, .0), (L_*.3, 0, 0), (L_*.42, 0, .04*s), (L_*.3, 0, .08*s), (-L_*.2, 0, .08*s), (-L_*.32, 0, .06*s)]
    pts = [(x + rr.uniform(-1, 1)*amassada*.02, y + rr.uniform(-1, 1)*amassada*.02, z) for x, y, z in pts]
    tubo(lt, pts, [.009*s]*len(pts), 8, seed, .05 + amassada*.2)
    rings = []
    for t, r in ((0, .012), (.4, .02), (.7, .04), (.9, .07), (1.0, .085)):
        rings.append([(L_*.3 + t*.16*s, math.cos(2*math.pi*k/18)*r*s*(1 - amassada*.3*math.sin(k)), math.sin(2*math.pi*k/18)*r*s) for k in range(18)])
    o = MT.aneis("campana", rings, [lt], tampa=False); sl = o.modifiers.new("so", 'SOLIDIFY'); sl.thickness = .003
    cyl(lt, (-L_/2 - .01*s, 0, 0), .012*s, .03*s, (0, 90, 0), 10)             # bocal
    if amordacada:   # pano de luto enfiado na campana e amarrado, lacre de cera vermelha com fita
        rovo(luto(seed), (L_*.42, 0, 0), (.04*s, .07*s, .07*s), (0, 0, 0), 12)
        for k in range(3): torus(MT.solido("barbante", (.3, .25, .17), 0, .9), (L_*.36 + k*.012*s, 0, 0), .03*s + k*.006*s, .003, (0, 90, 0))
        cyl(lacre(), (L_*.1, 0, .016*s), .022*s, .008*s, verts=12)
        tubo(MT.solido("fita_lacre", (.12, .02, .015), 0, .7), [(L_*.1, 0, .02*s), (L_*.12, -.03*s, -.01*s), (L_*.14, -.05*s, -.05*s)], [.006*s]*3, 4, seed, 0).scale.y = .4
    return piv_de(antes, p, [math.radians(a) for a in rot])

@ef("trombetas_caladas", "cripta", samples=56)
def trombetas_caladas():
    """Monte de trombetas de latão caladas: amassadas, as campanas entupidas de pano de luto, amarradas e lacradas
    com cera vermelha, como os Arautos fizeram com todas as que acharam depois que a sétima não tocou."""
    rr = rnd(901)
    for k, (x, y, z, rz, ry) in enumerate(((-.15, .05, .03, 20, 0), (.12, -.08, .03, -35, 0), (0, .12, .09, 70, 8), (-.1, -.15, .11, -5, -10), (.18, .15, .12, 110, 12))):
        trombeta((x*1.3, y*1.3, z*1.3), (rr.uniform(-8, 8), ry, rz), 1.3, rr.uniform(.2, .9), True, 900 + k)
    trombeta((.5, -.35, .08), (-90, 0, 40), 1.2, .5, False, 906)          # uma em pé apoiada, sem mordaça
    for k in range(6): vela((rr.uniform(-.45, .45), rr.uniform(-.4, .4), 0), rr.uniform(.04, .1), .016, False, 0, 910 + k)
    for k in range(8): cyl(lacre(), (rr.uniform(-.5, .5), rr.uniform(-.45, .45), .003), rr.uniform(.012, .03), .006, verts=10)
    return {}

@ef("relicario", "cripta", samples=56)
def relicario():
    """Relicário gótico de latão sobre coluna de pedra: caixinha de vidro com pináculos, um osso de dedo num coxim de
    veludo, ex-votos de fita amarrados na base e duas velas acesas."""
    rr = rnd(921); pc = pedra_cripta(1); lt = latao()
    cyl(pc, (0, 0, .03), .2, .06, verts=8); cyl(pc, (0, 0, .4), .1, .7, verts=8, r2=.085); cyl(pc, (0, 0, .78), .16, .06, verts=8)
    for k in range(8):
        a = k*math.pi/4; box(pc, (math.cos(a)*.1, math.sin(a)*.1, .4), (.03, .03, .66), (0, 0, math.degrees(a)), .004)
    z = .81
    box(lt, (0, 0, z + .02), (.26, .16, .04), bevel=.006)
    vid = _c("vidro_rel", lambda: K.mat_solid("vidro_relicario", (.3, .32, .3), 0, .05))
    vid.node_tree.nodes.get("Principled BSDF").inputs["Transmission Weight"].default_value = .85
    box(vid, (0, 0, z + .12), (.22, .12, .16), bevel=.002)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(lt, (sx*.115, sy*.065, z + .12), .008, .2, verts=6)
            cyl(lt, (sx*.115, sy*.065, z + .26), .012, .08, verts=6, r2=.001)       # pináculos
    MT.subdiv(box(lt, (0, 0, z + .22), (.26, .16, .03), bevel=.006), 0)
    cyl(lt, (0, 0, z + .3), .02, .14, verts=6, r2=.002); box(lt, (0, 0, z + .35), (.06, .008, .01), bevel=0)   # cruz no topo
    rovo(MT.solido("veludo", (.12, .015, .02), 0, .9), (0, 0, z + .06), (.07, .04, .02), (0, 0, 0), 10)
    ob = osso((.5, .44, .34))
    for k in range(3): along(ob, (-.04 + k*.03, 0, z + .08), (-.015 + k*.03, 0, z + .085), .006, verts=6)
    for k in range(6):   # fitas de promessa amarradas no fuste
        a = rr.uniform(0, 6.28); cor = rr.choice([(.25, .05, .04), (.05, .08, .2), (.3, .25, .12), (.2, .2, .18)])
        tubo(MT.solido(f"fita_prom_{k}", cor, 0, .8), [(math.cos(a)*.1, math.sin(a)*.1, .6), (math.cos(a)*.12, math.sin(a)*.12, .45), (math.cos(a + .2)*.14, math.sin(a + .2)*.14, .3 + rr.uniform(-.1, .1))], [.008, .007, .005], 4, k, 0).scale.z = 1
    vela((.14, -.14, .06), .1, .016, True, 1.0, 922); vela((-.16, -.1, .06), .07, .014, True, .8, 923)
    for k in range(5): cyl(cera(1), (rr.uniform(-.3, .3), rr.uniform(-.3, .3), .003), rr.uniform(.02, .04), .006, verts=10)
    return {"emissivo": "chama das velas", "luz": "vela"}

@ef("candelabro_ferro", "cripta", samples=56)
def candelabro_ferro():
    """Candelabro de chão de ferro batido com três pés de garra, coroa de sete pontas e velas grossas derretendo,
    a cera escorrida em estalactites pelos braços."""
    rr = rnd(931); fe = ferro(31, .5)
    for k in range(3):
        a = k*2.094 + .4
        tubo(fe, [(0, 0, .2), (math.cos(a)*.12, math.sin(a)*.12, .08), (math.cos(a)*.22, math.sin(a)*.22, .02), (math.cos(a)*.26, math.sin(a)*.26, .0)], [.016, .014, .012, .02], 8, k, .05)
    along(fe, (0, 0, .15), (0, 0, 1.35), .018, verts=10)
    for z in (.4, .8, 1.1): sphere(fe, (0, 0, z), (.035, .035, .03), segs=10)
    for k in range(7):
        a = k*math.pi*2/7; r_ = .2
        tubo(fe, [(0, 0, 1.3), (math.cos(a)*r_*.6, math.sin(a)*r_*.6, 1.33), (math.cos(a)*r_, math.sin(a)*r_, 1.4)], [.01, .009, .008], 6, k, .02)
        cyl(fe, (math.cos(a)*r_, math.sin(a)*r_, 1.41), .028, .015, verts=10)
        h = rr.uniform(.06, .16)
        vela((math.cos(a)*r_, math.sin(a)*r_, 1.42), h, .019, k % 3 != 1, .9 if k % 2 == 0 else 0, 930 + k)
        for j in range(2): sphere(cera(k % 3), (math.cos(a)*r_*.8, math.sin(a)*r_*.8, 1.36 - j*.04), (.006, .006, .03 + j*.01), segs=6)
    torus(fe, (0, 0, 1.4), .2, .008)
    for k in range(6): cyl(cera(2), (rr.uniform(-.3, .3), rr.uniform(-.3, .3), .003), rr.uniform(.02, .05), .006, verts=10)
    return {"emissivo": "chama das velas", "luz": "vela"}

@ef("ex_votos", "cripta", samples=56)
def ex_votos():
    """Sala dos milagres: tábua de promessas num cavalete com ex-votos de cera pendurados (cabeças, mãos, pernas, um
    coração), fotografias desbotadas, muletas encostadas e as velas de quem ainda pede."""
    rr = rnd(941); md = madeira(41, (.06, .04, .028))
    for sx in (-1, 1): along(md, (sx*.42, .05, 0), (sx*.4, 0, 1.5), .025, verts=8); along(md, (sx*.42, .3, 0), (sx*.4, 0, 1.0), .018, verts=6)
    o = box(md, (0, 0, 1.1), (.9, .04, .7), bevel=.008); ondula(o, .004, .1, 4)
    fe = ferro(41, .6)
    for x in (-.32, -.16, 0, .16, .32):
        for z in (1.38, 1.1, .85): along(fe, (x, -.02, z), (x, -.05, z - .02), .003, verts=4)
    cw = cera(4, (.5, .44, .32))
    def pend(x, z, tipo, k):
        along(MT.solido("barbante", (.3, .25, .17), 0, .9), (x, -.05, z - .02), (x, -.05, z - .07), .002, verts=3)
        if tipo == 0:   # cabeça
            sphere(cw, (x, -.06, z - .12), (.04, .035, .05), segs=10)
        elif tipo == 1:  # mão
            rbox(cw, (x, -.06, z - .12), (.05, .015, .07), (0, 0, 0), .008)
            for f in range(4): along(cw, (x - .018 + f*.012, -.06, z - .155), (x - .02 + f*.013, -.06, z - .19), .005, verts=5)
        elif tipo == 2:  # perna
            tubo(cw, [(x, -.06, z - .08), (x, -.06, z - .2), (x + .03, -.06, z - .23)], [.022, .016, .014], 8, k, .05)
        else:            # coração
            rovo(lacre(), (x, -.06, z - .12), (.035, .02, .04), (0, 0, 0), 10)
    tipos = [0, 1, 2, 3, 1]
    for i, x in enumerate((-.32, -.16, 0, .16, .32)):
        for j, z in enumerate((1.38, 1.1, .85)):
            if rr.random() < .8: pend(x, z, (i + j*2) % 4, i*3 + j)
    papel = _c("foto_velha", lambda: K.mat_cloth("foto_velha", (.3, .27, .2), 95.0))
    for k in range(6):
        rbox(papel, (rr.uniform(-.38, .38), -.025, rr.uniform(.85, 1.4)), (.06, .003, .08), (0, rr.uniform(-.3, .3), 0), 0)
    for sx in (-1, 1):   # muletas
        x = .55 + sx*.08
        along(md, (x, -.15, 0), (x - .02, -.05, 1.2), .014, verts=6); box(md, (x - .02, -.05, 1.22), (.04, .16, .03), (0, 0, 0), .006)
    for k in range(7): vela((rr.uniform(-.4, .3), rr.uniform(-.35, -.15), 0), rr.uniform(.05, .14), .016, k % 2 == 0, .6 if k == 0 else 0, 940 + k)
    return {"emissivo": "chama das velas", "luz": "vela"}

@ef("coroa_flores_secas", "cripta", samples=56)
def coroa_flores_secas():
    """Coroa de flores de finados num tripé de arame: rosas e cravos secos quase pretos, folhagem de cipreste ressecada
    e a faixa de luto escrita a tinta dourada desbotada."""
    rr = rnd(951); fe = ferro(51, .7)
    for k in range(3):
        a = k*2.094 + .5
        along(fe, (math.cos(a)*.25, math.sin(a)*.25 + .05, 0), (0, .02, 1.0), .007, verts=5)
    R = .3; zc = 1.0
    o = torus(_c("cipreste", lambda: K.mat_cloth("cipreste_seco", (.05, .06, .03), 96.0)), (0, 0, zc), R, .06, (90, 0, 0)); displace(o, .025, .04, 3, 1)
    for k in range(26):
        a = k/26*2*math.pi + rr.uniform(-.05, .05); r_ = R + rr.uniform(-.03, .03)
        p = (math.cos(a)*r_, -.05 + rr.uniform(-.02, .02), zc + math.sin(a)*r_)
        cor = rr.choice([(.12, .02, .025), (.18, .05, .04), (.22, .18, .12), (.08, .015, .02)])
        o = sphere(flor_seca(k % 4, cor), p, (.04, .03, .04), segs=8); displace(o, .015, .02, k, 1)
    pd = luto(2)
    for sx in (-1, 1):   # faixa de luto caindo
        tubo(pd, [(sx*.08, -.08, zc - R + .02), (sx*.12, -.09, zc - R - .2), (sx*.1, -.085, zc - R - .45)], [.04, .04, .035], 4, sx + 3, .1).scale.y = .15
    rbox(MT.solido("tinta_dourada", (.2, .15, .06), .5, .5), (-.1, -.1, zc - R - .25), (.005, .002, .2), (0, .05, 0), 0)
    for k in range(14): sphere(flor_seca(k % 3, (.12, .03, .03)), (rr.uniform(-.4, .4), rr.uniform(-.4, .2), .005), (.02, .015, .004), segs=6)
    return {}

@ef("sino_rachado", "cripta", samples=56)
def sino_rachado():
    """Sino de bronze caído da torre e rachado, de boca para o lado, com o badalo arrancado, a trave quebrada e a corda
    podre; verdete por fora e cera pingada por cima (alguém acende velas para ele)."""
    rr = rnd(961); bz = atl.metal("bronze", 961)
    rings = []
    for t, r in ((0, .02), (.05, .18), (.25, .2), (.55, .25), (.8, .34), (.92, .4), (1.0, .42)):
        rings.append([(math.cos(2*math.pi*k/32)*r, math.sin(2*math.pi*k/32)*r, -t*.7) for k in range(32)])
    o = MT.aneis("sino", rings, [bz], tampa=False); sl = o.modifiers.new("so", 'SOLIDIFY'); sl.thickness = .03
    for z in (-.08, -.55, -.62): torus(bz, (0, 0, z), .2 + (-z)*.3, .012)
    box(MT.sombra(), (.3, 0, -.5), (.01, .006, .35), (0, 30, 0), 0)           # a racha
    tubo(bz, [(0, 0, 0), (0, 0, .08), (0, .06, .1), (0, .06, .02)], [.02]*4, 8, 1, .02)   # alça
    piv_de(set(), (0, 0, 0), (0, 0, 0))
    antes = set(bpy.data.objects) - {o}
    o.rotation_euler = (math.radians(-80), 0, math.radians(30)); o.location = (0, 0, .42)
    o2 = o
    for ob_ in list(bpy.data.objects):
        if ob_.type == 'MESH' and ob_ is not o and ob_.parent is None and ob_.location.length < 1e-3 and ob_.name.startswith(("Torus", "Cube", "tubo")):
            ob_.parent = o
    along(fe := ferro(61, .7), (.45, .4, .02), (.65, .7, .03), .02, verts=8)                       # badalo
    sphere(fe, (.66, .72, .05), (.05, .05, .05), segs=12)
    md = madeira(61, (.05, .035, .025))
    rbox(md, (-.5, .35, .08), (.9, .16, .16), (0, .1, .6), .01); rbox(md, (-.2, .62, .05), (.4, .14, .1), (0, -.1, .2), .01)
    tubo(MT.solido("corda_podre", (.14, .11, .07), 0, .9), [(-.3, .4, .17), (-.1, .1, .02), (.2, -.2, .01), (.4, -.3, .01)], [.012]*4, 6, 3, .1)
    for k in range(4): vela((rr.uniform(-.6, .1), rr.uniform(-.5, -.25), 0), rr.uniform(.04, .1), .014, k < 2, .7 if k == 0 else 0, 960 + k)
    return {}

@ef("atril_partituras", "cripta", samples=56)
def atril_partituras():
    """Estante de coro de ferro batido com o hinário aberto na antífona do Juízo, partituras rasgadas no chão e uma
    trombeta calada no banquinho do lado."""
    rr = rnd(971); fe = ferro(71, .55)
    for k in range(3):
        a = k*2.094 + .2
        tubo(fe, [(0, 0, .25), (math.cos(a)*.2, math.sin(a)*.2, .05), (math.cos(a)*.25, math.sin(a)*.25, 0)], [.012, .012, .016], 6, k, .03)
    along(fe, (0, 0, .2), (0, 0, 1.1), .014, verts=8)
    rbox(fe, (0, -.02, 1.18), (.5, .02, .3), (math.radians(-55), 0, 0), .005)
    for k in range(5): along(fe, (-.22 + k*.11, -.0, 1.06), (-.22 + k*.11, -.1, 1.28), .005, verts=4)
    pap = _c("pagina_hino", lambda: K.mat_cloth("pagina_hino", (.36, .31, .22), 97.0))
    for sx in (-1, 1):
        o = rbox(pap, (sx*.115, -.04, 1.2), (.22, .006, .28), (math.radians(-55), sx*.08, 0), .002); ondula(o, .006, .06, sx)
    rbox(MT.solido("capa_hinario", (.12, .03, .02), 0, .7), (0, -.025, 1.19), (.47, .008, .3), (math.radians(-55), 0, 0), .003)
    tp = MT.solido("tinta_preta_pap", (.02, .016, .012), 0, .8)
    for sx in (-1, 1):
        for j in range(5):
            z = 1.27 - j*.045; y = -.045 - (1.27 - z)*.0 
            for kk in range(3): rbox(tp, (sx*.115, -.05 + (z - 1.2)*1.43*.0 - .003, z - .01*kk), (.18, .002, .002), (math.radians(-55), 0, 0), 0)
    for k in range(5):
        o = rbox(pap, (rr.uniform(-.5, .4), rr.uniform(-.45, -.1), .004), (.2, .26, .003), (rr.uniform(-.1, .1), rr.uniform(-.1, .1), rr.uniform(0, 3)), .001)
        sb = o.modifiers.new("s", 'SUBSURF'); sb.levels = sb.render_levels = 1; ondula(o, .015, .06, k)
    md = madeira(71, (.07, .045, .03))
    box(md, (.5, .2, .4), (.32, .32, .04), bevel=.008)
    for sx in (-1, 1):
        for sy in (-1, 1): box(md, (.5 + sx*.13, .2 + sy*.13, .19), (.035, .035, .38), bevel=.004)
    trombeta((.5, .2, .44), (0, 0, 30), .85, .3, True, 972)
    return {}

@ef("genuflexorio", "cripta", samples=56)
def genuflexorio():
    """Genuflexório de madeira escura com almofada de veludo puída, o terço de contas de osso pendendo e o missal
    aberto; a cera de anos de velas forma um monte na frente."""
    rr = rnd(981); md = madeira(81, (.055, .035, .025))
    box(md, (0, 0, .07), (.6, .32, .14), bevel=.01)
    rovo(MT.solido("veludo_puido", (.1, .02, .025), 0, .95), (0, -.04, .16), (.27, .12, .035), (0, 0, 0), 14)
    for sx in (-1, 1): box(md, (sx*.27, .12, .45), (.05, .07, .9), bevel=.008)
    box(md, (0, .14, .9), (.62, .2, .05), (math.radians(-12), 0, 0), .01)
    box(md, (0, .14, .6), (.5, .02, .55), bevel=.006)
    mb_ = MT.solido("almofada_entalhe", (.03, .02, .015), 0, .8)
    for k in range(3): box(mb_, (-.15 + k*.15, .128, .6), (.08, .004, .3), bevel=0)
    pap = _c("pagina_hino", lambda: K.mat_cloth("pagina_hino", (.36, .31, .22), 97.0))
    for sx in (-1, 1):
        o = rbox(pap, (sx*.08, .12, .935), (.15, .2, .006), (math.radians(-12), sx*.1, 0), .002); ondula(o, .004, .05, sx)
    ob = osso((.55, .5, .4))
    for k in range(18):   # terço pendendo pela beirada
        t = k/17; x = .2 + .06*math.sin(t*3.14); z = .9 - t*.35; y = .04 - .02*math.sin(t*6.28)
        sphere(ob, (x, y, z), (.008, .008, .008), segs=6)
    cyl(latao(), (.22, .04, .53), .004, .05, verts=4); box(latao(), (.22, .04, .54), (.03, .004, .006), bevel=0)
    o = sphere(cera(5), (0, -.32, .0), (.18, .12, .05), segs=14); displace(o, .015, .05, 4, 1)
    for k in range(5): vela((rr.uniform(-.15, .15), -.32 + rr.uniform(-.06, .06), .03), rr.uniform(.03, .1), .014, k < 3, .6 if k == 0 else 0, 980 + k)
    return {"emissivo": "chama das velas", "luz": "vela"}

@ef("ossuario_caixa", "cripta", samples=56)
def ossuario_caixa():
    """Caixas de ossuário empilhadas, com crânios pintados à moda velha (nome, data e uma coroa de folhas na testa),
    uma tampa aberta mostrando os ossos longos arrumados."""
    rr = rnd(991); md = madeira(91, (.07, .05, .033))
    def caixa(p, s=1.0, aberta=False, rot=0.0):
        antes = set(bpy.data.objects); W, D, H = .5*s, .26*s, .24*s
        box(md, (0, 0, H/2), (W, D, H), bevel=.008)
        box(MT.sombra(), (0, 0, H - .004), (W - .03, D - .03, .01), bevel=0)
        rbox(MT.solido("tinta_cruz", (.25, .22, .17), 0, .8), (0, -D/2 - .002, H*.55), (.12*s, .003, .02*s), (0, 0, 0), 0)
        rbox(MT.solido("tinta_cruz", (.25, .22, .17), 0, .8), (0, -D/2 - .002, H*.55), (.02*s, .003, .12*s), (0, 0, 0), 0)
        if aberta:
            for k in range(6): along(osso((.5, .45, .35)), (-W/2 + .05, -D/2 + .04 + k*.035, H - .03), (W/2 - .05, -D/2 + .04 + k*.035, H - .03), .014, verts=6)
        else:
            box(md, (0, 0, H + .015), (W + .02, D + .02, .03), bevel=.006)
        return piv_de(antes, p, (0, 0, rot))
    caixa((0, .1, 0), 1.0, False, .05); caixa((.02, .1, .27), .95, False, -.08); caixa((-.45, -.2, 0), 1.0, True, .3)
    rbox(md, (-.6, -.5, .015), (.52, .28, .03), (0, 0, .5), .006)        # a tampa no chão
    pinta = [MT.solido("coroa_verde", (.025, .05, .025), 0, .7), MT.solido("tinta_verm_nome", (.2, .03, .02), 0, .7)]
    for k, (x, y, z, r) in enumerate(((0, .02, .56, .3), (-.13, .03, .56, -.4), (.35, -.3, 0, .9), (-.4, -.24, .23, .1))):
        caveira((x, y, z), 1.0, r)
        a = r + math.pi/2
        for j in range(5):   # coroa de folhas pintada na testa
            aa = -.7 + j*.35
            sphere(pinta[0], (x + math.cos(r - math.pi/2)*.0 + math.cos(aa + r - math.pi/2)*.0, y - .03, z + .13), (.012, .006, .006), segs=6) if False else None
        rovo(pinta[0], (x + .0, y, z + .14), (.05, .04, .01), (0, 0, r), 8)
        rbox(pinta[1], (x + math.sin(r)*.05, y - math.cos(r)*.05, z + .1), (.04, .003, .01), (0, 0, r), 0)
    return {}

@ef("lacres_cera_chao", "cripta", samples=40, chao=True)
def lacres_cera_chao():
    """Decalque de chão: lacres de cera vermelha arrancados do peito dos Não-Julgados, tocos de vela, cera derramada e
    fitas com o selo, onde um deles se levantou."""
    rr = rnd(1001)
    o = sphere(cera(6), (0, 0, 0), (.35, .25, .01), segs=16); displace(o, .006, .06, 1, 1)
    for k in range(7):
        x, y = rr.uniform(-.45, .45), rr.uniform(-.35, .35)
        cyl(lacre(), (x, y, .006), rr.uniform(.03, .045), .01, verts=14)
        sphere(MT.sombra(), (x, y, .012), (.012, .012, .002), segs=6)
        if k % 2: tubo(MT.solido("fita_lacre", (.12, .02, .015), 0, .7), [(x, y, .01), (x + rr.uniform(-.1, .1), y + rr.uniform(-.1, .1), .004), (x + rr.uniform(-.2, .2), y + rr.uniform(-.2, .2), .003)], [.008]*3, 4, k, 0).scale.z = .3
    for k in range(5): vela((rr.uniform(-.4, .4), rr.uniform(-.3, .3), 0), rr.uniform(.02, .05), .016, False, 0, 1000 + k)
    for k in range(4): along(osso((.45, .4, .32)), (rr.uniform(-.4, .4), rr.uniform(-.3, .3), .01), (rr.uniform(-.4, .4), rr.uniform(-.3, .3), .012), .01, verts=6)
    return {}

@ef("raizes_ossos", "cripta", fp=(2, 1), samples=56)
def raizes_ossos():
    """Raízes grossas que furaram o piso da catacumba e saíram arrastando ossos e uma caveira presa no meio; lajes
    levantadas em volta e terra preta."""
    rr = rnd(1011); mr = _c("raiz", lambda: K.mat_wood("raiz_mt", (.05, .035, .025), 98.0)); pc = pedra_cripta(2)
    terra = _c("terra_preta", lambda: K.mat_stone("terra_preta_ef", (.04, .03, .022), (.015, .012, .01), 4.0, 0, None, 1.0, 99.0))
    o = sphere(terra, (0, 0, -.02), (.6, .4, .08), segs=16); displace(o, .04, .15, 2, 2)
    for k in range(5):
        x0, y0 = rr.uniform(-.3, .3), rr.uniform(-.2, .2)
        pts = [(x0, y0, -.1)]
        dx, dy = rr.uniform(-1, 1), rr.uniform(-1, 1); n = (dx*dx + dy*dy)**.5 or 1; dx, dy = dx/n, dy/n
        for j in range(1, 7):
            pts.append((x0 + dx*j*.13 + rr.uniform(-.04, .04), y0 + dy*j*.1 + rr.uniform(-.04, .04), .05*math.sin(j*.9) + .06*(j < 4)))
        tubo(mr, pts, [.07 - j*.01 for j in range(7)], 10, k, .2)
        for j in range(2): galho_ = tubo(mr, [pts[2 + j*2], (pts[2 + j*2][0] + rr.uniform(-.2, .2), pts[2 + j*2][1] + rr.uniform(-.2, .2), .02)], [.02, .006], 6, k*7 + j, .2)
    for k in range(4):   # lajes levantadas
        a = k*1.6 + .3; d = .55
        rbox(pc, (math.cos(a)*d, math.sin(a)*d*.7, .06), (.36, .3, .07), (rr.uniform(-.3, .3), rr.uniform(-.3, .3), a), .01)
    caveira((.05, -.05, .12), 1.0, .4)
    for k in range(6):
        a = Vector((rr.uniform(-.45, .45), rr.uniform(-.3, .3), rr.uniform(.03, .12)))
        along(osso((.45, .4, .32)), a, a + Vector((rr.uniform(-.25, .25), rr.uniform(-.25, .25), rr.uniform(-.05, .05))), .014, verts=6)
    return {}

@ef("cruz_ferro_tombada", "cripta", samples=56)
def cruz_ferro_tombada():
    """Cruz de túmulo de ferro batido com volutas e a plaquinha esmaltada do nome, tombada e meio torta sobre um monte de
    terra, uma guirlanda de arame com flores secas ainda presa."""
    rr = rnd(1021); fe = ferro(21, .7)
    antes = set(bpy.data.objects)
    along(fe, (0, 0, 0), (0, 0, 1.1), .018, verts=8); along(fe, (-.3, 0, .8), (.3, 0, .8), .016, verts=8)
    for sx in (-1, 1):
        for zc in (.8,):
            pts = [(sx*(.06 + .06*math.cos(a)), 0, zc + .1 + .06*math.sin(a)) for a in [i*.6 for i in range(10)]]
            tubo(fe, pts, [.006]*10, 6, sx + 5, .02)
            pts = [(sx*(.06 + .06*math.cos(a)), 0, zc - .1 - .06*math.sin(a)) for a in [i*.6 for i in range(10)]]
            tubo(fe, pts, [.006]*10, 6, sx + 7, .02)
    for p_ in ((0, 0, 1.12), (-.31, 0, .8), (.31, 0, .8)): sphere(fe, p_, (.03, .03, .03), segs=8)
    o = torus(fe, (0, 0, .8), .12, .006, (90, 0, 0))
    rbox(MT.solido("esmalte_placa", (.3, .3, .28), 0, .3), (0, -.02, .6), (.16, .006, .09), (0, 0, 0), .004)
    rbox(MT.solido("tinta_preta_pap", (.02, .016, .012), 0, .8), (0, -.024, .6), (.1, .002, .012), (0, 0, 0), 0)
    for k in range(10):
        a = k*.63; sphere(flor_seca(k % 3, rr.choice([(.12, .02, .025), (.2, .17, .1)])), (math.cos(a)*.12, -.02, .8 + math.sin(a)*.12), (.025, .02, .025), segs=6)
    piv_de(antes, (0, 0, .12), (math.radians(-72), math.radians(8), math.radians(20)))
    terra = _c("terra_preta", lambda: K.mat_stone("terra_preta_ef", (.04, .03, .022), (.015, .012, .01), 4.0, 0, None, 1.0, 99.0))
    o = sphere(terra, (-.05, .2, 0), (.35, .7, .14), segs=16); displace(o, .03, .15, 5, 2)
    for k in range(8): sphere(flor_seca(k % 2, (.15, .1, .06)), (rr.uniform(-.3, .3), rr.uniform(-.4, .6), .1), (.02, .015, .006), segs=6)
    return {}
