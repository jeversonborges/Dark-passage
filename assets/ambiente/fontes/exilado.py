# ================================================================ ILHA DO EXILADO · kit da ilhota do Rio Amargo (17/10/2026)
# A ilhota no remanso do Rio Amargo (mapa da Cidade de São Lázaro) onde Pedro, o Exilado, ergueu a oficina: o velho
# mestre que a Vigília e o Coro dos Arautos expulsaram por ensinar os dois lados. Nenhum lado reclama a ilha; as
# pontes de corda só baixam para quem traz a carta do Simão. Na oficina há dois manequins vestidos com o que o
# jogador pode virar (as evoluções de classe do nível 50).
#
# Vocabulário (regra Lorencia): madeira de bonde e de caixote reaproveitada, tábuas desencontradas, corda de cânhamo
# encardida, lona azul-noite da Vigília costurada a pano rubro-negro do Coro, ferro com ferrugem, latão com verdete,
# couro. Pó das faces de cima: areia ruiva do Deserto de Absinto. Emissivos: o fogo do lampião (oficina) ou o verde do
# Amargo (limo nas estacas da ponte); no máximo um por peça.
#
# Registrado em assets.REG por render_assets.py (lista de kits). Render (bpy 4.2, mesmo pipeline do egito.py):
#   cd assets/ambiente/fontes && /opt/bpy42/bin/python render_assets.py -- /tmp/exilado_brutos ponte_corda oficina_exilado \
#       manequim_evolucao_a manequim_evolucao_b sino_ponte trapiche_exilado
#   python3 publicar.py /tmp/exilado_brutos
# (/opt/bpy42 = venv do Python 3.11 com `pip install bpy==4.2.0`, quando o Blender 4.2 oficial não estiver no container.)
#
# IDs (bioma "deserto_absinto"): ponte_corda oficina_exilado manequim_evolucao_a manequim_evolucao_b sino_ponte
#   trapiche_exilado
import bpy, math, random
from mathutils import Vector
import kit as K
from kit import box, cyl, sphere, along, torus
from assets import REG, rnd
import atlantida as atl
from atlantida import tubo, rbox, rovo
import egito as eg
from egito import madeira, corda, ferro, latao, lanterna, caixote, casco

AREIA = (.26, .19, .115)          # poeira ruiva do Deserto de Absinto nas faces de cima
AMARGO = (.35, 1.0, .18)          # verde do Amargo (o único brilho fora do fogo)
AZUL_NOITE = (.04, .06, .115)    # lona da Vigília
RUBRO = (.16, .02, .018)         # pano do Coro dos Arautos
NEGRO = (.018, .015, .014)

# ================================================================ registro
def ex(nome, fp=(1, 1), cat="props", samples=64, chao=False):
    def deco(fn):
        def wrap(m, seed=0):
            _MT.clear(); eg.limpar(); atl.limpar(); K.DUST = AREIA
            prev = atl.TERRA; atl.TERRA = AREIA
            try: r = fn() or {}
            finally: atl.TERRA = prev
            r.setdefault("bioma", "deserto_absinto")
            if chao: r["chao"] = True
            return r
        wrap.__doc__ = fn.__doc__ or ""
        REG[nome] = dict(fn=wrap, cat=cat, fp=fp, dungeon=False, walls=False, samples=samples, bury=0.0, no_catcher=False)
        return fn
    return deco

# ================================================================ materiais
_MT = {}
def _c(key, fn):
    if key not in _MT or _MT[key].name not in bpy.data.materials: _MT[key] = fn()
    return _MT[key]

def tabua(i):
    """Tábuas desencontradas: cada uma veio de um lugar (bonde, caixote, porta, banco de igreja)."""
    tons = [(.085, .06, .038), (.055, .042, .03), (.1, .085, .062), (.07, .048, .03), (.045, .036, .028)]
    k = i % 7
    if k == 5: return _c(("tab_az", 0), lambda: K.mat_wood("tabua_pintada_azul", (.07, .055, .04), 31.0, (.035, .05, .075)))
    if k == 6: return _c(("tab_rb", 0), lambda: K.mat_wood("tabua_pintada_rubra", (.07, .05, .035), 33.0, (.11, .03, .022)))
    c = tons[k % len(tons)]
    return _c(("tab", k), lambda: K.mat_wood(f"tabua_ex_{k}", c, 20.0 + k))

def tronco_mat(): return _c("tronco", lambda: K.mat_wood("tronco_ex", (.05, .038, .026), 41.0))
def corda_ex(): return _c("corda", lambda: K.mat_cloth("corda_canhamo", (.16, .125, .075), 9.0))
def lona_mat(cor, seed):
    """Pano tingido: a poeira que assenta é a própria cor desbotada com um pouco de areia (a tinta tem de ler de longe)."""
    def f():
        prev = K.DUST; K.DUST = tuple(c*1.7 + a*.18 for c, a in zip(cor, AREIA))
        try: return K.mat_cloth(f"lona_ex_{seed}", cor, seed)
        finally: K.DUST = prev
    return _c(("lona", cor, seed), f)
def couro_ex(c=(.075, .042, .024), seed=0): return _c(("couro", c, seed), lambda: K.mat_cloth(f"couro_ex_{seed}", c, 60.0 + seed))
def livro_mat(c, seed): return _c(("livro", c, seed), lambda: K.mat_cloth(f"capa_livro_{seed}", c, 70.0 + seed))
def papel(): return _c("papel", lambda: K.mat_cloth("papel_velho", (.4, .34, .23), 80.0))

def limo():
    """Limo do Amargo nas estacas, na linha d'água: verde-escuro com um fio de brilho verde."""
    def f():
        m, nt, b = K.new_mat("limo_amargo")
        v = K.N(nt, "ShaderNodeTexCoord").outputs["Object"]
        n = K.noise(nt, v, None, 14, 5, .6, 3.0)
        col = K.mix(nt, (.012, .03, .01), (.05, .12, .03), n.outputs["Fac"])
        K.L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .25
        r = K.ramp(nt, [(.55, (0, 0, 0)), (.75, (1, 1, 1))]); K.L(nt, n.outputs["Fac"], r.inputs[0])
        b.inputs["Emission Color"].default_value = (*AMARGO, 1)
        K.L(nt, K.math_(nt, 'MULTIPLY', r.outputs[0], 1.4), b.inputs["Emission Strength"])
        return m
    return _c("limo", f)

# ================================================================ geometria
def lona(mat, p0, u, v, nu, nv, rr, sag=.04, rasgo=0.0, ondas=3, esp=.012):
    """Pano em grade (lona, cortina, saia de casaco): cede entre os apoios, borda de baixo rasgada."""
    p0, u, v = Vector(p0), Vector(u), Vector(v)
    nrm = u.cross(v).normalized()
    cortes = [1 - rasgo*rr.random()**1.5 for _ in range(nu + 1)]
    vs, fs = [], []
    for j in range(nv + 1):
        for i in range(nu + 1):
            a, bb = i/nu, j/nv
            bb2 = bb*(cortes[i] if j == nv else 1) if rasgo else bb
            s = sag*abs(math.sin(math.pi*a*ondas))*math.sin(math.pi*min(1, bb))**.7 + (rr.uniform(-.01, .01) if 0 < i < nu and 0 < j < nv else 0)
            vs.append(p0 + u*a + v*bb2 - nrm*s)
    for j in range(nv):
        for i in range(nu): q = j*(nu + 1) + i; fs.append((q, q + 1, q + nu + 2, q + nu + 1))
    me = bpy.data.meshes.new("lona"); me.from_pydata([tuple(x) for x in vs], [], fs); me.update()
    for pl in me.polygons: pl.use_smooth = True
    o = bpy.data.objects.new("lona", me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(mat)
    o.modifiers.new("s", 'SOLIDIFY').thickness = esp
    return o

def poste(p, h, r=.07, rr=None, base=-.5):
    """Poste de tronco torto, enterrado."""
    rr = rr or random.Random(int(p[0]*100 + p[1]*7))
    x, y = p[0], p[1]; pts = []; rad = []
    for k in range(6):
        t = k/5; pts.append((x + rr.uniform(-.02, .02), y + rr.uniform(-.02, .02), base + (h - base)*t)); rad.append(r*(1.05 - .2*t))
    return tubo(tronco_mat(), pts, rad, 9, rr.randint(0, 999), .14)

def corda_curva(a, b, queda, r=.012, n=14, mat=None, lado=None):
    """Corda pendurada de a até b com barriga 'queda' (catenária aproximada)."""
    a, b = Vector(a), Vector(b); pts = []
    for k in range(n + 1):
        t = k/n; p = a.lerp(b, t); p.z -= queda*math.sin(math.pi*t)
        if lado is not None: p.y += lado*math.sin(math.pi*t)
        pts.append(tuple(p))
    return tubo(mat or corda_ex(), pts, [r]*(n + 1), 6, n, .15, tampa=False)

def amarra(p, r=.08, voltas=3, mat=None):
    for k in range(voltas): torus(mat or corda_ex(), (p[0], p[1], p[2] + k*.022), r, .013)

def trapo(p, cor, seed, h=.45, larg=.07, rr=None):
    """Tira de pano amarrada num poste, caindo."""
    rr = rr or random.Random(seed)
    pts = [(p[0] + .02*k + rr.uniform(-.01, .01), p[1] - .07 - .01*k, p[2] - h*k/5) for k in range(6)]
    tubo(lona_mat(cor, seed), pts, [larg*(1 - .12*k) for k in range(6)], 4, seed, .3).scale = (1, 1, 1)

def livros(p, rr, n=4, amarrado=True, rot=0.0):
    """Pilha de livros grossos amarrados em cruz com corda."""
    x, y, z = p; zz = z
    cores = [(.09, .03, .02), (.04, .05, .07), (.07, .055, .035), (.035, .03, .025), (.1, .07, .04)]
    w0 = d0 = 0
    for k in range(n):
        w, d, h = rr.uniform(.22, .3), rr.uniform(.16, .21), rr.uniform(.04, .07)
        ang = rot + rr.uniform(-.15, .15)
        rbox(livro_mat(rr.choice(cores), k), (x, y, zz + h/2), (w, d, h), (0, 0, ang), .006)
        rbox(papel(), (x + .006, y - .004, zz + h/2), (w - .02, d - .01, h - .014), (0, 0, ang), 0)
        zz += h; w0, d0 = max(w0, w), max(d0, d)
    if amarrado:
        H = zz - z
        rbox(corda_ex(), (x, y, z + H/2), (.022, d0 + .02, H + .02), (0, 0, rot), .008)
        rbox(corda_ex(), (x, y, z + H/2), (w0 - .02, .022, H + .02), (0, 0, rot), .008)
        rbox(corda_ex(), (x, y, zz + .015), (.05, .05, .03), (0, 0, rot + .6), .01)
    return zz

def ferramentas_parede(x0, y, z, rr):
    """Ferramentas penduradas na parede de tábuas: serrote, martelo, tenaz, formões, compasso."""
    fe = ferro(951); md = madeira(952, (.08, .055, .035))
    rbox(fe, (x0, y, z), (.42, .008, .12), (0, 0, 0), .002)                                   # serrote
    rbox(md, (x0 + .25, y, z + .01), (.1, .03, .1), (0, 0, 0), .01)
    along(md, (x0 + .5, y, z + .12), (x0 + .5, y, z - .2), .015, verts=6); rbox(fe, (x0 + .5, y, z + .13), (.14, .05, .05), (0, 0, 0), .006)   # martelo
    along(fe, (x0 + .66, y, z + .14), (x0 + .7, y, z - .24), .009, verts=4); along(fe, (x0 + .72, y, z + .14), (x0 + .68, y, z - .24), .009, verts=4)   # tenaz
    for k in range(4):
        along(md, (x0 + .82 + k*.06, y, z + .1), (x0 + .82 + k*.06, y, z - .02), .012, verts=5)
        along(fe, (x0 + .82 + k*.06, y, z - .02), (x0 + .82 + k*.06, y, z - .16 - .02*k), .006, verts=4)
    la = latao()
    along(la, (x0 + 1.1, y, z + .14), (x0 + 1.05, y, z - .16), .006, verts=4); along(la, (x0 + 1.1, y, z + .14), (x0 + 1.16, y, z - .16), .006, verts=4)
    for k in range(6): cyl(fe, (x0 + k*.22, y + .01, z + .2), .008, .04, (90, 0, 0), 6)    # pregos

# ================================================================ PONTE DE CORDA
@ex("ponte_corda", (9, 3), "props", 64, chao=True)
def ponte_corda():
    """Ponte de corda da Ilha do Exilado: tábuas gastas e desencontradas (de bonde, caixote e banco de igreja) sobre dois
    cabos de cânhamo, corrimãos de corda presos em postes de tronco nas pontas, tirantes e espias amarradas em estacas;
    uma tábua falta e outra está rachada; o limo verde do Amargo agarrado nas estacas. Peça inteira de 6,4 m ao longo do
    eixo X do mapa (centro da ponte na âncora)."""
    rr = rnd(9101)
    HALF = 3.1; W = 1.25
    def zd(x): return .48 - .2*math.sin(math.pi*(x + HALF)/(2*HALF))
    # cabos de baixo (onde as tábuas assentam)
    for sy in (-1, 1):
        pts = [(x, sy*W*.36, zd(x) - .035) for x in [-HALF - .1 + 2*(HALF + .1)*k/16 for k in range(17)]]
        tubo(corda_ex(), pts, [.026]*17, 7, 3 + sy, .12, tampa=False)
    # tábuas
    x = -HALF + .12; i = 0; faltou = False
    while x < HALF - .1:
        w = rr.uniform(.15, .21); xc = x + w/2
        meio = abs(xc) < HALF - .9
        if meio and not faltou and rr.random() < .12: faltou = True; x += w + .14; i += 1; continue       # uma tábua faltando
        L = W*rr.uniform(.82, 1.05); off = rr.uniform(-.07, .07)
        incl = math.atan(-.2*math.pi/(2*HALF)*math.cos(math.pi*(xc + HALF)/(2*HALF)))
        rot = (rr.uniform(-.04, .04), -incl + rr.uniform(-.03, .03), rr.uniform(-.06, .06))
        if meio and rr.random() < .06:                                                    # tábua rachada, uma ponta caída
            rbox(tabua(i), (xc, off - L*.22, zd(xc) - .03), (w, L*.5, .035), (rot[0] - .25, rot[1], rot[2]), .006)
            rbox(tabua(i), (xc, off + L*.25, zd(xc)), (w, L*.46, .035), rot, .006)
        else:
            rbox(tabua(i), (xc, off, zd(xc)), (w, L, .035 + rr.uniform(0, .015)), rot, .006)
        for sy in (-1, 1):                                                                # amarração da tábua no cabo
            if rr.random() < .55: torus(corda_ex(), (xc, sy*W*.36, zd(xc) - .02), .035, .009, (90, 0, 90))
        x += w + rr.uniform(.015, .05); i += 1
    # postes, corrimãos, tirantes e espias
    tops = {}
    for sx in (-1, 1):
        for sy in (-1, 1):
            px, py = sx*(HALF + .08), sy*(W*.5 + .12)
            h = 1.35 + rr.uniform(-.06, .08)
            poste((px, py), h, .075, rr)
            tops[(sx, sy)] = Vector((px, py, h - .1))
            amarra((px, py, h - .2), .085); amarra((px, py, zd(px) - .06), .085, 2)
            sphere(limo(), (px, py, .0), (.12, .12, .07), segs=10)                          # limo na linha d'água
            # espia: corda do poste até a estaca na margem
            st = Vector((sx*(HALF + .75), sy*(W*.5 + .45), 0))
            along(madeira(953, (.06, .045, .03)), tuple(st + Vector((0, 0, -.1))), tuple(st + Vector((-sx*.05, 0, .32))), .035, .025, verts=6)
            along(corda_ex(), (px, py, h - .25), tuple(st + Vector((0, 0, .25))), .011, verts=5)
        # travessa no alto da cabeceira, com o trapo do coveiro (o sinal de que a ponte baixa)
        along(tronco_mat(), tuple(tops[(sx, -1)] + Vector((0, -.08, .06))), tuple(tops[(sx, 1)] + Vector((0, .08, .06))), .05, verts=8)
        trapo(tuple(tops[(sx, -1)] + Vector((0, .25, .05))), (.3, .27, .21), 960 + sx, .5)
    for sy in (-1, 1):
        a, b = tops[(-1, sy)], tops[(1, sy)]
        corda_curva(a, b, .62, .017, 20, lado=-sy*.08)                                      # corrimão
        corda_curva(a - Vector((0, 0, .32)), b - Vector((0, 0, .32)), .5, .011, 20, lado=-sy*.06)   # corda do meio
        n = 13
        for k in range(1, n):                                                             # tirantes do corrimão até o cabo
            t = k/n; p = a.lerp(b, t); p.z -= .62*math.sin(math.pi*t); p.y += -sy*.08*math.sin(math.pi*t)
            xq = p.x; q = Vector((xq + rr.uniform(-.03, .03), sy*W*.36, zd(xq) - .02))
            along(corda_ex(), tuple(p), tuple(q), .007, verts=4)
    # remendo: uma chapa de ferro pregada onde a tábua sumiu, um balde amarrado
    fe = ferro(954)
    cyl(fe, (-1.0, .42, zd(-1.0) + .14), .1, .22, verts=12, r2=.12)
    torus(fe, (-1.0, .42, zd(-1.0) + .26), .1, .008)
    return {"emissivo": "verde do Amargo (limo nas estacas)", "comprimento_m": 6.4,
            "nota": "peça inteira ao longo do eixo X do mapa; tabuleiro a 0,3-0,5 m sobre a água (z=0); usar como decalque (camada chao)"}

# ================================================================ OFICINA DO EXILADO
@ex("oficina_exilado", (5, 4), "props", 72)
def oficina_exilado():
    """Oficina de Pedro, o Exilado: telheiro de tábuas e troncos sobre um estrado, coberto com lona remendada de duas
    metades (a lona azul-noite da Vigília costurada ao pano rubro-negro do Coro), bancada com morsa, ferramentas na
    parede, livros amarrados com corda, bigorna num toco, retalho azul e rubro pregado na parede; o lampião de latão
    pendurado na viga da frente é a única luz."""
    rr = rnd(9201)
    X0, X1, YF, YB = -1.5, 1.5, -.55, 1.0          # telheiro: frente alta (y=YF), fundo baixo (y=YB)
    ZF, ZB = 2.4, 1.98
    def zt(y): return ZF + (ZB - ZF)*(y - YF)/(YB - YF)
    # estrado de tábuas sobre calços
    for k in range(17):
        x = -1.62 + k*.2 + rr.uniform(-.01, .01)
        rbox(tabua(k + 3), (x, .02 + rr.uniform(-.03, .03), .1), (.185, 2.15 + rr.uniform(-.1, .05), .04), (0, 0, rr.uniform(-.015, .015)), .005)
    for x in (-1.5, 0, 1.5):
        for y in (-.9, .95): box(madeira(955, (.05, .04, .03)), (x, y, .04), (.16, .16, .08), bevel=.01)
    # esteios e vigas
    for x in (X0, 0.05, X1):
        poste((x, YF), ZF + .05, .07, rr, 0); poste((x, YB), ZB + .05, .065, rr, 0)
    along(tronco_mat(), (X0 - .2, YF, ZF), (X1 + .2, YF, ZF), .065, verts=9)
    along(tronco_mat(), (X0 - .2, YB, ZB), (X1 + .2, YB, ZB), .06, verts=9)
    for x in (X0, -.72, .05, .78, X1): along(madeira(956), (x, YF - .25, ZF + .08), (x, YB + .2, ZB + .03), .035, verts=6)   # caibros
    # parede do fundo: tábuas verticais desencontradas, uma faltando
    for k in range(15):
        if k == 9: continue
        x = X0 + .1 + k*.2; h = ZB - .1 + rr.uniform(-.12, .05)
        rbox(tabua(k), (x, YB + .03, .12 + h/2), (.19, .03, h), (0, rr.uniform(-.02, .02), 0), .004)
    for z in (.55, 1.55): along(madeira(957), (X0, YB + .06, z), (X1, YB + .06, z), .03, verts=5)
    # lona do telhado: metade azul-noite (Vigília), metade rubro-negra (Coro), costura grossa no meio
    U = (0, YB - YF + .5, zt(YB + .25) - zt(YF - .25))
    lona(lona_mat(AZUL_NOITE, 961), (X0 - .22, YF - .25, ZF + .14), (1.62 + .25, 0, 0), U, 18, 14, rr, .05, 0, 2)
    lona(lona_mat(RUBRO, 962), (-.08, YF - .25, ZF + .145), (1.82, 0, 0), U, 18, 14, rr, .05, 0, 2)
    ang = math.atan2(ZF - ZB, YB - YF)
    for k in range(10):                                                                   # pontos da costura
        y = YF - .2 + k*(YB - YF + .4)/10
        rbox(corda_ex(), (-.03, y, zt(y) + .17), (.12, .02, .012), (-ang, 0, .5 if k % 2 else -.5), 0)
    for (x, y, w, c, s) in [(-1.0, .2, .32, (.09, .075, .05), 963), (-.45, -.25, .22, RUBRO, 964), (.7, .45, .3, AZUL_NOITE, 965), (1.15, -.2, .2, (.12, .1, .07), 966)]:
        rbox(lona_mat(c, s), (x, y, zt(y) + .175), (w, w*.8, .008), (-ang, 0, rr.uniform(-.3, .3)), 0)   # remendos de outra metade
    # bambinelas rasgadas na frente: azul de um lado, rubro do outro
    lona(lona_mat(AZUL_NOITE, 967), (X0 - .2, YF - .27, ZF + .14), (1.6, 0, 0), (0, 0, -.42), 12, 4, rr, .02, .55, 3)
    lona(lona_mat(RUBRO, 968), (-.06, YF - .27, ZF + .15), (1.78, 0, 0), (0, 0, -.38), 12, 4, rr, .02, .55, 3)
    # parede de lona azul do lado de trás (-X), caindo do telhado
    lona(lona_mat(AZUL_NOITE, 969), (X0 - .05, YF, ZF - .05), (0, YB - YF, ZB - ZF), (0, 0, -1.9), 10, 10, rr, .06, .25, 2)
    # bancada no fundo
    md = madeira(970, (.075, .052, .033))
    box(md, (-.5, .66, .9), (1.9, .58, .07), bevel=.008)
    for (x, y) in ((-1.4, .42), (-1.4, .9), (.4, .42), (.4, .9)): box(md, (x, y, .5), (.07, .07, .8), bevel=.005)
    box(md, (-.5, .66, .32), (1.8, .5, .04), bevel=.005)                                       # prateleira de baixo
    fe = ferro(971); la = latao()
    # morsa
    box(fe, (.15, .5, 1.0), (.14, .1, .14), bevel=.01); box(fe, (.15, .4, 1.0), (.14, .05, .12), bevel=.008)
    along(fe, (.15, .3, .98), (.15, .45, .98), .012, verts=6); along(fe, (.07, .3, .98), (.23, .3, .98), .008, verts=4)
    # na bancada: livro aberto, tinteiro, peças de armadura em conserto, compasso
    rbox(livro_mat((.07, .04, .025), 1), (-.95, .6, .955), (.42, .3, .03), (0, 0, .1), .004)
    rbox(papel(), (-1.05, .58, .975), (.19, .27, .012), (0, -.06, .1), .002); rbox(papel(), (-.84, .62, .975), (.19, .27, .012), (0, .06, .1), .002)
    cyl(K.mat_solid("tinteiro", (.02, .02, .025), 0, .15), (-.62, .8, .97), .03, .06, verts=10)
    along(K.mat_solid("pena", (.3, .27, .22), 0, .7), (-.62, .8, .98), (-.55, .9, 1.15), .006, verts=4)
    rovo(fe, (-.25, .65, .98), (.14, .11, .07), (0, 0, .4), 12)                                # ombreira em conserto
    for k in range(5): cyl(la, (-.25 + rr.uniform(-.1, .1), .52 + rr.uniform(-.04, .04), .94), .012, .015, verts=6)   # rebites
    livros((-1.25, .75, .935), rr, 3, True, .2)
    for k in range(3): caixote((-1.0 + k*.55, .66, .34), rr, .3, k == 1)                        # caixotes na prateleira
    # parede: ferramentas e o retalho de duas cores (o sinal do Pedro)
    ferramentas_parede(-1.35, YB - .005, 1.4, rr)
    rbox(lona_mat(AZUL_NOITE, 972), (.62, YB - .01, 1.45), (.2, .01, .34), (0, .05, 0), 0)
    rbox(lona_mat(RUBRO, 973), (.82, YB - .01, 1.45), (.2, .01, .34), (0, -.05, 0), 0)
    for k in range(6): rbox(corda_ex(), (.72, YB - .02, 1.3 + k*.055), (.06, .008, .012), (0, 0, 0), 0)
    for (x, z) in ((.54, 1.6), (.9, 1.6), (.54, 1.3), (.9, 1.3)): cyl(fe, (x, YB - .02, z), .012, .03, (90, 0, 0), 6)
    # bigorna no toco, à direita
    cyl(tronco_mat(), (1.05, .1, .37), .2, .55, verts=14)
    box(fe, (1.05, .1, .7), (.42, .16, .12), bevel=.015); box(fe, (1.05, .1, .62), (.22, .12, .1), bevel=.01)
    cyl(fe, (1.3, .1, .72), .06, .14, (0, 90, 0), 10, r2=.01)
    along(fe, (.95, .2, .77), (.82, .36, .78), .01, verts=4); box(fe, (.97, .17, .78), (.08, .04, .04), bevel=.004)
    # livros amarrados no chão, na frente; barril e corda enrolada
    livros((-.95, -.45, .12), rr, 5, True, -.3); livros((-.62, -.58, .12), rr, 3, True, .5)
    livros((-1.15, -.75, .12), rr, 2, True, .1)
    o = cyl(madeira(974, (.07, .05, .03)), (1.3, -.62, .5), .24, .76, verts=16)
    for z in (.22, .78): torus(fe, (1.3, -.62, z), .245, .012)
    for k in range(4): torus(corda_ex(), (.85, -.7, .14 + k*.03), .17 - k*.012, .02)
    # banquinho
    rbox(md, (-.3, -.1, .48), (.36, .36, .04), (0, 0, .3), .005)
    for (dx, dy) in ((-.13, -.13), (.13, -.13), (.13, .13), (-.13, .13)): along(md, (-.3 + dx*1.2, -.1 + dy*1.2, .12), (-.3 + dx, -.1 + dy, .47), .02, verts=5)
    # lampião de latão pendurado na viga da frente (a luz)
    along(fe, (.45, YF, ZF - .05), (.45, YF, ZF - .3), .006, verts=4)
    lanterna((.45, YF, ZF - .33), 1.1, 85)
    return {"emissivo": "fogo (lampião)", "npc": "Pedro, o Exilado", "luz": "quente"}

# ================================================================ MANEQUINS DAS EVOLUÇÕES
def manequim_base(rr):
    """Armação de costura: tripé de madeira, haste, torso de lona estofada e cabeça de forma de chapéu."""
    md = madeira(980, (.06, .042, .028))
    for k in range(3):
        a = k/3*2*math.pi + .3
        along(md, (0, 0, .3), (math.cos(a)*.34, math.sin(a)*.34, .02), .022, verts=6)
        sphere(md, (math.cos(a)*.34, math.sin(a)*.34, .02), (.03, .03, .02), segs=6)
    along(md, (0, 0, .02), (0, 0, 1.0), .025, verts=8)
    torus(latao(), (0, 0, .3), .035, .01)
    pts = [(0, 0, z) for z in (.92, 1.0, 1.1, 1.2, 1.32, 1.44, 1.52, 1.57)]
    o = tubo(lona_mat((.24, .2, .14), 981), pts, [.12, .16, .14, .13, .16, .18, .16, .06], 14, 981, .04)
    o.scale = (1, .72, 1)
    along(md, (0, 0, 1.56), (0, 0, 1.68), .035, verts=8)
    sphere(md, (0, 0, 1.78), (.085, .095, .11), segs=14)

def casaco(cor, seed, rr, aberto=.0):
    """Casaco longo vestido no manequim: corpo, saia aberta na frente, gola e mangas caídas."""
    m = lona_mat(cor, seed)
    pts = [(0, 0, z) for z in (1.53, 1.44, 1.3, 1.16, 1.0, .82, .62)]
    o = tubo(m, pts, [.17, .205, .185, .165, .2, .25, .3], 16, seed, .06, tampa=False); o.scale = (1, .78, 1)
    o.modifiers.new("s", 'SOLIDIFY').thickness = .012
    for sx in (-1, 1):                                                                    # mangas
        sp = [(sx*.2, 0, 1.47), (sx*.25, .0, 1.3), (sx*.27, .03, 1.1), (sx*.26, .05, .92)]
        tubo(m, sp, [.065, .06, .058, .055], 10, seed + sx, .1)
        torus(m, (sx*.26, .05, .92), .055, .012, (10, 0, 0))
    torus(m, (0, 0, 1.53), .085, .03)                                                     # gola
    for sx in (-1, 1):                                                                    # lapelas
        rbox(m, (sx*.065, -.15, 1.38), (.07, .015, .26), (0.15, 0, sx*.25), .004)
    rbox(K.mat_solid("vao_casaco", (.01, .009, .008), 0, 1), (0, -.205, .8), (.035, .02, .36), (0.08, 0, 0), 0)   # abertura da saia
    return m

@ex("manequim_evolucao_a", (1, 1), "props", 64)
def manequim_evolucao_a():
    """Manequim dos Arautos na oficina do Exilado: armação de costura vestida com o que um Arauto pode virar no nível
    50: sobretudo rubro-negro do Coro, ombreira de ferro negro com cravos de latão, corrente atravessada no peito, gorjal,
    máscara de gás de couro na cabeça e a auréola de latão partida espetada atrás numa haste."""
    rr = rnd(9301); manequim_base(rr)
    casaco(RUBRO, 931, rr)
    fe = _c("ferro_negro", lambda: K.mat_metal("ferro_negro", (.022, .02, .02), .3, 7.0, .45)); la = latao()
    # faixas pretas no casaco (o rubro-negro do Coro)
    for z in (.7, .76): torus(lona_mat(NEGRO, 932), (0, 0, z), .27 - (.76 - z)*.3, .012).scale = (1, .78, 1)
    # cinto de couro com fivela
    t = torus(couro_ex(), (0, 0, 1.02), .2, .022); t.scale = (1, .78, 1)
    box(la, (0, -.158, 1.02), (.06, .015, .05), bevel=.004)
    # ombreira esquerda com cravos
    o = rovo(fe, (-.22, 0, 1.5), (.13, .14, .08), (0, -.5, 0), 14)
    for k in range(4): cyl(la, (-.22 - .03*k, -.06 + .04*k, 1.57 - .015*k), .014, .07, (0, -35, 0), 6, r2=.001)
    rovo(fe, (-.27, 0, 1.4), (.09, .11, .05), (0, -.9, 0), 12)
    # gorjal e corrente atravessada
    t = torus(fe, (0, 0, 1.54), .1, .03); t.scale = (1, .85, .7)
    K.chain(fe, (-.17, -.15, 1.45), (.16, -.14, 1.08), 9, .022)
    # máscara de gás de couro com filtro de latão
    rovo(couro_ex((.05, .03, .02), 1), (0, -.06, 1.74), (.09, .07, .08), (0, 0, 0), 12)
    cyl(la, (0, -.14, 1.7), .04, .06, (90, 0, 0), 12); cyl(fe, (0, -.175, 1.7), .045, .015, (90, 0, 0), 12)
    for sx in (-1, 1): cyl(K.mat_solid("lente_fosca", (.05, .055, .05), 0, .15), (sx*.04, -.115, 1.79), .022, .02, (80, 0, 0), 10)
    # auréola partida numa haste atrás da cabeça
    along(fe, (0, .06, 1.5), (0, .14, 2.0), .008, verts=4)
    bpy.ops.mesh.primitive_torus_add(location=(0, .14, 2.02), rotation=(math.radians(75), 0, 0), major_radius=.16, minor_radius=.012, major_segments=24, minor_segments=6)
    h = bpy.context.object; h.data.materials.append(la)
    import bmesh
    bm = bmesh.new(); bm.from_mesh(h.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.x > .05 and v.co.y > -.02], context='VERTS'); bm.to_mesh(h.data); bm.free()
    # etiqueta de papel amarrada no pulso
    rbox(papel(), (.27, -.02, .86), (.05, .005, .08), (0, .2, .3), 0)
    return {"faccao": "arautos", "nota": "na oficina do Exilado: o que você pode virar (Arautos)"}

@ex("manequim_evolucao_b", (1, 1), "props", 64)
def manequim_evolucao_b():
    """Manequim da Vigília na oficina do Exilado: armação de costura vestida com o que um combatente da Vigília pode
    virar no nível 50: guarda-pó azul-noite remendado, peitoral de chapa rebitada sobre o casaco, bandoleira de couro com
    cartuchos de latão, lenço no pescoço, chapéu de aba larga na cabeça e a escopeta serrada encostada no tripé."""
    rr = rnd(9401); manequim_base(rr)
    casaco(AZUL_NOITE, 941, rr)
    fe = ferro(942); la = latao(); cr = couro_ex((.08, .045, .025), 2)
    # remendos no guarda-pó
    for (x, z, w) in ((.15, .8, .1), (-.1, 1.2, .08), (.2, 1.05, .07)):
        rbox(lona_mat((.12, .1, .07), 943), (x, -.215 + abs(x)*.25, z), (w, .01, w*1.2), (0.1, 0, rr.uniform(-.3, .3)), 0)
    # peitoral de chapa rebitada
    rovo(fe, (0, -.06, 1.3), (.19, .13, .2), (0, 0, 0), 16)
    for k in range(7):
        a = -1.2 + k*.4; cyl(la, (math.sin(a)*.17, -.16 - math.cos(a)*.02, 1.42), .012, .01, (90, 0, 0), 6)
    along(cr, (-.15, -.1, 1.45), (-.17, .0, 1.53), .015, verts=4); along(cr, (.15, -.1, 1.45), (.17, .0, 1.53), .015, verts=4)
    # bandoleira com cartuchos
    a, b = Vector((.17, -.2, 1.48)), Vector((-.2, -.21, .95))
    along(cr, tuple(a), tuple(b), .03, verts=6).scale = (1, .5, 1)
    for k in range(9):
        p = a.lerp(b, .08 + k*.1)
        cyl(la, tuple(p + Vector((0, -.03, 0))), .014, .06, (60, 0, -35), 8)
        cyl(K.mat_solid("cartucho_verm", (.16, .03, .02), 0, .5), tuple(p + Vector((.015, -.03, .03))), .0145, .03, (60, 0, -35), 8)
    # lenço de pescoço (cinza encardido)
    t = torus(lona_mat((.17, .16, .14), 944), (0, -.01, 1.55), .09, .035); t.scale = (1, .9, .8)
    rovo(lona_mat((.17, .16, .14), 944), (.02, -.1, 1.47), (.05, .02, .08), (0, .2, .2), 8)
    # chapéu de aba larga
    hm = _c("chapeu", lambda: K.mat_cloth("feltro_chapeu", (.07, .055, .04), 12.0))
    o = cyl(hm, (0, 0, 1.86), .22, .02, verts=24); o.scale = (1, 1, 1)
    cyl(hm, (0, 0, 1.93), .1, .13, verts=18, r2=.09); torus(cr, (0, 0, 1.88), .1, .012)
    # escopeta serrada encostada no tripé
    s0 = Vector((.3, -.12, .02)); s1 = Vector((.12, -.1, .72))
    for dy in (-.017, .017): along(fe, tuple(s0 + Vector((0, dy, .25))), tuple(s1 + Vector((0, dy, 0))), .016, verts=8)
    rbox(madeira(945, (.08, .05, .03)), tuple(s0 + Vector((0, 0, .12))), (.07, .05, .28), (0, -.25, 0), .01)
    return {"faccao": "vigilia", "nota": "na oficina do Exilado: o que você pode virar (Vigília)"}

# ================================================================ SINO DA PONTE E TRAPICHE
@ex("sino_ponte", (2, 2), "props", 56)
def sino_ponte():
    """Sino de chamar a ponte: forca de troncos com um sino de bronze rachado (de capela afogada), a corda de puxar
    amarrada no poste e, no pé, o sarilho de madeira que arria a ponte de corda, com o cabo enrolado e a manivela."""
    rr = rnd(9501)
    poste((0, 0), 2.3, .08, rr, -.4)
    along(tronco_mat(), (-.05, 0, 2.15), (.7, 0, 2.2), .05, verts=8)
    along(tronco_mat(), (0, 0, 1.6), (.45, 0, 2.18), .035, verts=6)
    amarra((0, 0, 2.05), .09); amarra((.4, 0, 2.12), .06, 2)
    br = eg.bronze(951)
    along(ferro(952), (.62, 0, 2.17), (.62, 0, 2.04), .01, verts=4)
    o = cyl(br, (.62, 0, 1.88), .07, .2, verts=18, r2=.13); torus(br, (.62, 0, 1.78), .13, .015)
    cyl(br, (.62, 0, 2.0), .05, .05, verts=12)
    sphere(ferro(952), (.62, 0, 1.76), (.025, .025, .03), segs=8)
    pts = [(.62, 0, 1.78), (.6, -.02, 1.4), (.45, -.04, 1.1), (.12, -.05, 1.0)]
    tubo(corda_ex(), pts, [.012]*4, 5, 1, .1, tampa=False); amarra((0, 0, .98), .09, 2)
    # sarilho
    md = madeira(953, (.07, .05, .033))
    for sy in (-.3, .3):
        along(md, (.25, sy, 0), (.25, sy, .7), .04, verts=6); along(md, (.05, sy, 0), (.25, sy, .7), .03, verts=5); along(md, (.45, sy, 0), (.25, sy, .7), .03, verts=5)
    cyl(md, (.25, 0, .62), .12, .52, (90, 0, 0), 14)
    for k in range(9): torus(corda_ex(), (.25, -.22 + k*.055, .62), .135, .018, (90, 0, 0))
    fe = ferro(954)
    along(fe, (.25, -.3, .62), (.25, -.45, .62), .015, verts=5); along(fe, (.25, -.45, .62), (.25, -.45, .4), .012, verts=4)
    along(md, (.25, -.47, .4), (.25, -.6, .4), .02, verts=5)
    corda_curva((.3, .25, .55), (1.2, .5, .05), .15, .014, 10)
    trapo((0, -.05, 1.75), (.3, .27, .21), 955, .4)
    return {"nota": "fica na cabeceira da ponte de corda, do lado da ilha"}

@ex("trapiche_exilado", (4, 2), "props", 56)
def trapiche_exilado():
    """Trapiche da ilha: tábuas desencontradas sobre estacas de tronco com limo verde do Amargo, uma canoa de casco
    remendado amarrada, remo, balde e um puçá secando."""
    rr = rnd(9601)
    for k in range(11):
        x = -1.05 + k*.2 + rr.uniform(-.01, .01)
        rbox(tabua(k + 2), (x, rr.uniform(-.04, .04), .4), (.18, .95 + rr.uniform(-.1, .1), .04), (0, 0, rr.uniform(-.03, .03)), .005)
    for x in (-1.0, 0, 1.0):
        for y in (-.42, .42):
            poste((x, y), .55 if x == 1.0 else .38, .06, rr, -.4)
            sphere(limo(), (x, y, 0), (.1, .1, .06), segs=10)
    along(madeira(961), (-1.1, -.42, .33), (1.1, -.42, .33), .03, verts=5)
    cas = _c("casco_canoa", lambda: K.mat_wood("casco_canoa", (.05, .038, .027), 5.0, (.04, .055, .07)))
    o = casco(cas, 2.2, .55, .18, 9601, .25, .3); o.location = (.2, -.95, 0); o.rotation_euler = (0, 0, .06)
    for k in range(4): rbox(tabua(k), (-.4 + k*.4, -.95, .14), (.08, .42, .02), (0, 0, 0), .003)
    along(madeira(962), (-.6, -.85, .2), (.9, -1.1, .35), .018, verts=5); rbox(madeira(962), (1.0, -1.12, .36), (.25, .09, .015), (0, .2, -.15), .004)
    corda_curva((1.0, -.42, .5), (1.2, -.9, .2), .1, .012, 8)
    fe = ferro(963)
    cyl(fe, (.6, .2, .52), .1, .2, verts=12, r2=.12)
    torus(fe, (-.6, .25, .42), .2, .01, (0, 0, 0))
    for k in range(8):
        a = k/8*2*math.pi; along(corda_ex(), (-.6 + math.cos(a)*.2, .25 + math.sin(a)*.2, .42), (-.6, .25, .18), .004, verts=3)
    return {"emissivo": "verde do Amargo (limo nas estacas)", "nota": "linha d'água em z=0"}
