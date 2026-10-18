# ================================================================ SÃO LÁZARO 1890 · kit da cidade da Vigília (18/10/2026)
# Pedido do Jefin: a região inicial da Vigília refeita como "uma cidade do século XIX, soturna mas linda", em isométrico,
# sem prédios gigantes. A rua de hoje é o telhado de ontem: a cidade está enterrada até o 4º andar, então o que sai da
# areia são os dois últimos andares dos sobrados e os telhados. As janelas do andar que virou térreo viraram portas.
#
# Vocabulário (regra Lorencia): reboco de cal manchado (ocre, rosa queimado, cinza-azul, branco sujo) sobre tijolo
# aparecendo nos cantos; cantaria cinza nos cunhais, peitoris e cimalhas; madeira pintada de verde-garrafa ou
# sangue-de-boi nas esquadrias; ferro batido nas sacadas e gradis; telha de barro escurecida; zinco e latão nos
# remendos da Vigília. Emissivo: ÂMBAR DE LAMPIÃO (janelas acesas e lanternas), uma cor só por peça; a Rádio é a
# exceção com o vermelho do mastro.
#
# Render (bpy 4.2):  cd assets/ambiente/fontes && /opt/bpy42/bin/python render_assets.py -- /tmp/claude-0/sl1890 <ids>
#                    python3 publicar.py /tmp/claude-0/sl1890
# Cada peça devolve "base": [xmin, ymin, xmax, ymax] em metros (o chão que as paredes ocupam de verdade), que o
# layout do mapa usa para bloquear o movimento. Peças com walls=True saem em _a (fachada para -Y, baixo-esquerda
# na tela) e _b (girada 90°, fachada para +X, baixo-direita).
import bpy, math, random
from mathutils import Vector
import kit as K
from kit import box, cyl, sphere, along, torus, prism, point, N, L, ramp, mix, math_, noise, crumble
import assets as A
from assets import REG, rnd, duna

T = K.T
AMBAR = (1, .58, .22)
_MT = {}
def _c(key, fn):
    if key not in _MT or _MT[key].name not in bpy.data.materials: _MT[key] = fn()
    return _MT[key]
def limpar(): _MT.clear()

def sl(nome, fp=(1, 1), cat="predios", samples=48, walls=True, kw=None, bury=0.0):
    def deco(fn):
        def wrap(m, seed=0):
            limpar()
            r = fn(m, **(kw or {})) or {}
            r.setdefault("bioma", "sao_lazaro")
            return r
        wrap.__doc__ = fn.__doc__ or ""
        REG[nome] = dict(fn=wrap, cat=cat, fp=fp, dungeon=False, walls=walls, samples=samples, bury=bury)
        return fn
    return deco

# ================================================================ materiais
def mat_reboco(name, tint, seed=0.0, desc=.5):
    """Reboco de cal pintado, manchado de cima para baixo, com o tijolo aparecendo onde caiu (desc = quanto caiu)."""
    m, nt, b = K.new_mat(name)
    v, w = K.coords(nt, ("wall", T*3), seed)
    n1 = noise(nt, v, w, 2.2, 6, .6, seed); n2 = noise(nt, v, w, 11, 4, .5, seed + 3)
    r = ramp(nt, [(.3, tuple(c*.55 for c in tint)), (.7, tint)]); L(nt, n1.outputs["Fac"], r.inputs[0])
    col = mix(nt, r.outputs[0], n2.outputs["Color"], .14, 'OVERLAY')
    # tijolo aparecendo (manchas grandes, mais embaixo)
    geo = N(nt, "ShaderNodeNewGeometry"); sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, geo.outputs["Position"], sep.inputs[0])
    pn = noise(nt, v, w, 1.1, 5, .65, seed + 9)
    hz = math_(nt, 'MULTIPLY', math_(nt, 'DIVIDE', sep.outputs[2], 6.0), .35)
    f = math_(nt, 'ADD', pn.outputs["Fac"], hz)
    pr = ramp(nt, [(.52 - desc*.1, (1, 1, 1)), (.56 - desc*.1, (0, 0, 0))]); L(nt, f, pr.inputs[0])
    tc = N(nt, "ShaderNodeTexCoord"); sep2 = N(nt, "ShaderNodeSeparateXYZ"); L(nt, tc.outputs["Object"], sep2.inputs[0])
    comb = N(nt, "ShaderNodeCombineXYZ")
    L(nt, math_(nt, 'ADD', sep2.outputs[0], sep2.outputs[1]), comb.inputs[0]); L(nt, sep2.outputs[2], comb.inputs[1])
    bk = N(nt, "ShaderNodeTexBrick", offset=.5, squash=1.0)
    bk.inputs["Scale"].default_value = 1.0; bk.inputs["Brick Width"].default_value = .24; bk.inputs["Row Height"].default_value = .07
    bk.inputs["Mortar Size"].default_value = .012; bk.inputs["Color1"].default_value = (.1, .045, .03, 1)
    bk.inputs["Color2"].default_value = (.07, .03, .022, 1); bk.inputs["Mortar"].default_value = (.03, .028, .025, 1)
    L(nt, comb.outputs[0], bk.inputs["Vector"])
    col = mix(nt, col, bk.outputs["Color"], pr.outputs[0])
    col = K.grime(nt, col, v, w, 5.5, .7)
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .92
    h = math_(nt, 'ADD', math_(nt, 'MULTIPLY', n2.outputs["Fac"], .35), math_(nt, 'MULTIPLY', pr.outputs[0], 1.0))
    K.bump(nt, b, h, .5, .03)
    return m

TINTAS = {"ocre": (.30, .20, .09), "rosa": (.30, .14, .11), "azul": (.12, .15, .17), "branco": (.26, .24, .20),
          "verde": (.11, .15, .09), "amarelo": (.32, .25, .10), "cinza": (.21, .2, .18)}
def reboco(cor, seed=0.0, desc=.5): return _c(("reb", cor, seed, desc), lambda: mat_reboco(f"reboco_{cor}_{seed}", TINTAS[cor], seed, desc))
def cantaria(): return _c("can", lambda: K.mat_stone("cantaria_sl", (.17, .16, .145), (.08, .075, .068), 1.6, .2, None, 3.0, 5.0))
def madeira(cor="verde"):
    c = {"verde": (.035, .07, .035), "sangue": (.11, .035, .025), "escura": (.04, .028, .02), "crua": (.09, .065, .04)}[cor]
    return _c(("mad", cor), lambda: K.mat_wood("madeira_" + cor, c, 3.0 + len(cor)))
def ferro(): return _c("fer", lambda: K.mat_metal("ferro_batido_sl", (.022, .022, .024), .3, 2.0, .45))
def zinco(): return _c("zn", lambda: K.mat_metal("zinco_sl", (.11, .11, .105), .6, 4.0, .5))
def latao(): return _c("lat", lambda: K.mat_brass("latao_sl"))
def telha(): return _c("tel", lambda: mat_telha())
def vao(): return _c("vao", lambda: K.mat_solid("vao_sl", (.004, .004, .004), 0, .9))
def vidro_aceso(): return _c("vac", lambda: K.mat_window_lit("janela_acesa_sl"))
def clarab_acesa():
    """Clarabóia do mercado: vidro sujo iluminado por dentro, bem mais fraco que uma janela acesa."""
    def f():
        m = K.mat_window_lit("claraboia_sl"); nt = m.node_tree; b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        for l in list(nt.links):
            if l.to_socket == b.inputs["Emission Strength"]: nt.links.remove(l)
        b.inputs["Emission Strength"].default_value = .45
        return m
    return _c("cla", f)
def vidro_escuro(): return _c("ves", lambda: K.mat_solid("vidro_escuro_sl", (.02, .025, .03), .1, .15))
def areia(): return _c("are", lambda: K.mat_sand_obj())

def mat_telha():
    """Telha de barro em fiadas (canal), escurecida, com musgo seco e poeira."""
    m, nt, b = K.new_mat("telha_sl")
    v, w = K.coords(nt, None, 4.0)
    tc = N(nt, "ShaderNodeTexCoord"); sep = N(nt, "ShaderNodeSeparateXYZ"); L(nt, tc.outputs["Object"], sep.inputs[0])
    u = math_(nt, 'ADD', sep.outputs[0], sep.outputs[1])
    wv = N(nt, "ShaderNodeTexWave", wave_type='BANDS', bands_direction='X'); wv.inputs["Scale"].default_value = 14.0; wv.inputs["Distortion"].default_value = .4
    comb = N(nt, "ShaderNodeCombineXYZ"); L(nt, u, comb.inputs[0]); L(nt, sep.outputs[2], comb.inputs[1])
    L(nt, comb.outputs[0], wv.inputs[0])
    rows = math_(nt, 'FRACT', math_(nt, 'MULTIPLY', sep.outputs[2], 5.0))
    n1 = noise(nt, v, w, 3.0, 5, .6, 4.0)
    r = ramp(nt, [(.3, (.075, .035, .022)), (.7, (.14, .07, .04))]); L(nt, n1.outputs["Fac"], r.inputs[0])
    col = mix(nt, r.outputs[0], (.04, .02, .015), math_(nt, 'MULTIPLY', wv.outputs["Fac"], .5))
    col = mix(nt, col, (.03, .02, .015), math_(nt, 'MULTIPLY', math_(nt, 'LESS_THAN', rows, .12), .8))
    col = K.grime(nt, col, v, w, 9.0, .5)
    L(nt, col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .9
    K.bump(nt, b, math_(nt, 'ADD', wv.outputs["Fac"], rows), .5, .03)
    return m

# ================================================================ peças de fachada
def janela(x, z, w, h, y, mat_m=None, tipo="escura", arco=True, sacada=False, venez=True, seed=0, axis="y", sinal=-1):
    """Janela alta de sobrado na parede y (normal para -Y). tipo: escura, acesa, tabuas, porta, quebrada."""
    r = rnd(seed); fr = mat_m or madeira("verde"); can = cantaria()
    def P(u, v_, du, dv, dz, zz, mat, bevel=.004):
        if axis == "y": return box(mat, (x + u, y + sinal*v_, zz), (du, dv, dz), bevel=bevel)
        return box(mat, (y + sinal*v_, x + u, zz), (dv, du, dz), bevel=bevel)
    def C(u, v_, rr, dd, zz, mat):
        if axis == "y": return cyl(mat, (x + u, y + sinal*v_, zz), rr, dd, (90, 0, 0), 20)
        return cyl(mat, (y + sinal*v_, x + u, zz), rr, dd, (0, 90, 0), 20)
    P(0, -.12, w, .3, h, z + h/2, vao(), 0)                               # rebaixo escuro (dentro da parede)
    if arco: C(0, -.12, w/2, .3, z + h, vao())
    fundo = {"acesa": vidro_aceso(), "quebrada": vidro_escuro()}.get(tipo, vidro_escuro())
    if tipo in ("acesa", "escura", "quebrada"):
        P(0, .05, w - .06, .02, h - .05, z + h/2, fundo, 0)
        if arco: C(0, .05, w/2 - .03, .02, z + h, fundo)
        P(0, .08, .04, .03, h + (w/2 if arco else 0), z + (h + (w/2 if arco else 0))/2, fr)      # montante
        for k in range(1, 3): P(0, .08, w, .03, .04, z + h*k/3, fr)                                   # travessas
        if venez:                                                                                      # veneziana aberta
            P(-w/2 - .18, .12, .32, .035, h*.98, z + h/2, fr); P(w/2 + .18, .12, .32, .035, h*.98, z + h/2, fr)
            for k in range(int(h/.09)):
                P(-w/2 - .18, .14, .26, .01, .04, z + .05 + k*.09, fr, 0); P(w/2 + .18, .14, .26, .01, .04, z + .05 + k*.09, fr, 0)
        if tipo == "acesa":
            P(-w*.3, .065, w*.35, .01, h*.9, z + h/2, K.mat_cloth("cortina_sl", (.13, .05, .03), 61.0), 0)
    if tipo == "tabuas":
        for k in range(4): P(0, .1, w + .14, .035, .13, z + .18 + k*(h - .3)/3, madeira("crua"), 0)
    if tipo == "porta":
        P(0, .06, w - .1, .04, h - .04, z + h/2, madeira("sangue"), 0)
        P(0, .09, .02, .01, h - .3, z + h/2, ferro(), 0)
        for k in range(2): P(-w*.2 + k*w*.4, .095, w*.3, .01, h*.4, z + h*.3, madeira("escura"), 0)
        if arco: C(0, .06, w/2 - .05, .02, z + h, vidro_escuro())                                     # bandeira de vidro
    # moldura de cantaria: ombreiras, peitoril, verga
    for s in (-1, 1): P(s*(w/2 + .07), .03, .14, .07, h + (w/2 if arco else .1), z + (h + (w/2 if arco else .1))/2, can)
    if tipo != "porta": P(0, .09, w + .5, .16, .09, z - .04, can)
    if arco: C(0, .03, w/2 + .14, .07, z + h, can); C(0, .0, w/2 - .02, .1, z + h, vao()); C(0, .05, w/2 - .03, .02, z + h, fundo)
    else: P(0, .03, w + .34, .07, .16, z + h + .08, can)
    if sacada:
        P(0, .34, w + .9, .62, .1, z - .02, can)
        for k in range(int((w + .8)/.16)):
            u = -(w + .8)/2 + .08 + k*.16; P(u, .62, .018, .018, .85, z + .45, ferro(), 0)
        P(0, .62, w + .9, .03, .035, z + .9, ferro(), 0); P(0, .62, w + .9, .03, .025, z + .4, ferro(), 0)
        for s in (-1, 1): P(s*(w + .9)/2, .34, .018, .56, .85, z + .45, ferro(), 0)
    if tipo == "porta":                                                                   # degraus de tábua até a areia
        for k in range(3): P(0, .3 + k*.22, w + .3, .22, .05, z - .12 - k*.1, madeira("crua"), 0)
    if tipo == "acesa":
        if axis == "y": point((x, y + sinal*.8, z + h*.5), AMBAR, 26, .3)
        else: point((y + sinal*.8, x, z + h*.5), AMBAR, 26, .3)

def lanterna(x, y, z, axis="y", sinal=-1):
    """Lanterna de latão presa no braço de ferro da parede, chama âmbar."""
    if axis == "y": p = lambda u, v_: (x + u, y + sinal*v_)
    else: p = lambda u, v_: (y + sinal*v_, x + u)
    a = p(0, .0); b_ = p(0, .45)
    along(ferro(), (*a, z + .1), (*b_, z + .1), .018, verts=6); along(ferro(), (*a, z - .25), (*b_, z + .08), .012, verts=5)
    cyl(latao(), (*b_, z - .1), .12, .36, verts=6, r2=.09)
    cyl(K.mat_emit("chama_lanterna", AMBAR, 9), (*b_, z - .1), .08, .28, verts=6)
    cyl(latao(), (*b_, z + .12), .14, .06, verts=6, r2=.03)
    point((*b_, z - .1), AMBAR, 70, .06)

def cimalha(W, D, z, saida=.22, alt=.22):
    """Cimalha de cantaria contornando o prédio."""
    can = cantaria()
    box(can, (0, 0, z + alt/2), (W + 2*saida, D + 2*saida, alt), bevel=.01)
    box(can, (0, 0, z - .08), (W + saida, D + saida, .16), bevel=.01)

def cunhais(W, D, H):
    can = cantaria()
    for sx in (-1, 1):
        for sy in (-1, 1):
            for k in range(int(H/.6)):
                box(can, (sx*(W/2 - .02), sy*(D/2 - .02), .3 + k*.6), (.44 if k % 2 else .3, .3 if k % 2 else .44, .5), bevel=.01)

def telhado_duas_aguas(W, D, z, h, mat=None, beiral=.45, ao_longo="x", buraco=None, seed=0):
    """Telhado de telhas de barro com beiral; ao_longo = eixo da cumeeira."""
    mat = mat or telha(); r = rnd(seed)
    if ao_longo == "x":
        o = prism(mat, (0, 0, z), D + 2*beiral, W + 2*beiral, h)
        o.rotation_euler = (0, 0, math.radians(90))
    else:
        o = prism(mat, (0, 0, z), W + 2*beiral, D + 2*beiral, h)
    # cumeeira
    L_ = (W if ao_longo == "x" else D) + 2*beiral
    cyl(mat, (0, 0, z + h), .07, L_, (0, 90, 0) if ao_longo == "x" else (90, 0, 0), 8)
    # ripas vistas no beiral da frente
    n = int(L_/.5)
    for k in range(n):
        u = -L_/2 + .25 + k*.5
        if ao_longo == "x": box(madeira("escura"), (u, -(D/2 + beiral*.5), z - .05), (.08, beiral, .08), (28, 0, 0), .003)
    if buraco:                                                             # parte do telhado desabou: caibros à vista
        bx, by, bw, bd = buraco
        box(vao(), (bx, by, z + h*.45), (bw, bd, .4), bevel=0)
        for k in range(4):
            box(madeira("escura"), (bx - bw/2 + bw*(k + .5)/4, by, z + h*.5), (.1, bd + .3, .1), (r.uniform(-6, 6), 0, 0), .003)
    return o

def platibanda(W, D, z, h=.9, urnas=True):
    """Platibanda de alvenaria com balaústres e urnas nos cantos (frente e lado direito)."""
    can = cantaria(); reb = reboco("branco", 2.0, .3)
    box(reb, (0, D/2 - .12, z + h/2), (W + .3, .24, h), bevel=.01)
    box(reb, (-W/2 + .12, 0, z + h/2), (.24, D + .3, h), bevel=.01)
    for face in ("y", "x"):
        n = int((W if face == "y" else D)/.3)
        for k in range(n):
            u = -(W if face == "y" else D)/2 + .15 + k*.3
            p = (u, -D/2 + .1, z + h*.45) if face == "y" else (W/2 - .1, u, z + h*.45)
            cyl(can, p, .045, h*.7, verts=8, r2=.06)
        if face == "y": box(can, (0, -D/2 + .1, z + h - .06), (W + .3, .3, .12), bevel=.01); box(can, (0, -D/2 + .1, z + .05), (W + .3, .3, .1), bevel=.01)
        else: box(can, (W/2 - .1, 0, z + h - .06), (.3, D + .3, .12), bevel=.01); box(can, (W/2 - .1, 0, z + .05), (.3, D + .3, .1), bevel=.01)
    if urnas:
        for (x, y) in [(-W/2, -D/2), (W/2, -D/2), (W/2, D/2)]:
            box(can, (x, y, z + h + .12), (.4, .4, .24), bevel=.01)
            cyl(can, (x, y, z + h + .5), .16, .5, verts=12, r2=.08); sphere(can, (x, y, z + h + .8), (.14, .14, .18), segs=10)

def chamine(x, y, z, h=1.2, mat=None):
    box(mat or A.M()["brick"], (x, y, z + h/2), (.5, .5, h), bevel=.01)
    box(cantaria(), (x, y, z + h + .05), (.62, .62, .1), bevel=.01)
    cyl(zinco(), (x, y, z + h + .3), .12, .4, verts=10)

def areia_na_base(W, D, seed, h=.55):
    """Areia escorrida contra as paredes (a rua é areia): montes baixos na frente e no lado."""
    r = rnd(seed)
    for k in range(5):
        x = r.uniform(-W/2 + .4, W/2 - .4); duna((x, -D/2 - .3, -h*.5), r.uniform(1.0, 1.9), r.uniform(.7, 1.1), h*r.uniform(.8, 1.3), seed + k)
    for k in range(3):
        y = r.uniform(-D/2 + .4, D/2 - .4); duna((W/2 + .3, y, -h*.5), r.uniform(.7, 1.1), r.uniform(1.0, 1.7), h*r.uniform(.7, 1.2), seed + 10 + k)
    duna((-W/2 - .4, -D/2 - .4, -h*.4), 1.4, 1.4, h*.9, seed + 20)

def remendo_vigilia(x, y, z, axis="y", sinal=-1, seed=0):
    """Chapa de zinco remendando a parede, com rebites."""
    r = rnd(seed)
    if axis == "y": box(zinco(), (x, y + sinal*.04, z), (r.uniform(.6, 1.1), .03, r.uniform(.5, .9)), (0, 0, r.uniform(-3, 3)), .003)
    else: box(zinco(), (y + sinal*.04, x, z), (.03, r.uniform(.6, 1.1), r.uniform(.5, .9)), (0, 0, r.uniform(-3, 3)), .003)

def corpo(W, D, H, cor, seed, desc=.5):
    """Corpo do sobrado: caixa de reboco com embasamento de cantaria."""
    box(reboco(cor, seed, desc), (0, 0, H/2), (W, D, H), bevel=.012)
    box(cantaria(), (0, 0, .2), (W + .1, D + .1, .4), bevel=.01)
    return [-W/2, -D/2, W/2, D/2]

def lado_x(D, z0, FH, n, seed, tipos=None):
    """Janelas da parede +X (lado visível em _a) e -X (visível em _b), mais simples."""
    r = rnd(seed)
    for sx in (1, -1):
        for f in range(2):
            for k in range(n):
                y = -D/2 + D*(k + .5)/n
                t = (tipos or ["escura", "tabuas", "escura", "quebrada"])[(k + f + (0 if sx > 0 else 1)) % 4]
                janela(y, z0 + f*FH + .55, .8, 1.7, sx*W_ATUAL[0]/2, tipo=t, axis="x", sinal=sx, seed=seed + k + f*7, venez=False, arco=(f == 0))
W_ATUAL = [0]

# ================================================================ SOBRADOS
def sobrado(m, W=6.4, D=5.2, cor="ocre", telhado="telhas", seed=1, loja=False, ruina=False, acesas=(1,), porta=1, cumeeira="x"):
    """Sobrado de dois andares da São Lázaro de 1890: reboco de cal, janelas altas de arco, sacada de ferro batido,
    cimalha e telhado de barro. O andar de baixo era o 4º andar antes da areia; a janela virou porta."""
    r = rnd(seed); FH = 3.1; H = 2*FH; W_ATUAL[0] = W
    base = corpo(W, D, H, cor, seed, .6 if ruina else .4)
    cunhais(W, D, H)
    n = max(2, int(W/1.7)); y = -D/2
    for k in range(n):
        x = -W/2 + W*(k + .5)/n
        t0 = "porta" if k == porta else ("tabuas" if (ruina and k == 0) else ("acesa" if k in acesas and False else "escura"))
        janela(x, .55, .9, 2.0, y, tipo=t0, seed=seed*3 + k, venez=(t0 != "porta"))
        t1 = "acesa" if k in acesas else ("tabuas" if ruina and k == n - 1 else ("quebrada" if r.random() < .25 else "escura"))
        janela(x, FH + .55, .9, 2.0, y, tipo=t1, seed=seed*5 + k, sacada=(k == porta or (n > 3 and k == n - 2)))
    box(cantaria(), (0, -D/2 - .06, FH - .03), (W + .3, .12, .14), bevel=.006)       # faixa entre andares
    lado_x(D, 0, FH, max(2, int(D/2.0)), seed + 40)
    if loja:
        box(madeira("sangue"), (0, -D/2 - .17, 2.72), (W*.86, .08, .55), bevel=.005)
        box(K.mat_solid("letreiro_ouro", (.45, .33, .1), .4, .35), (0, -D/2 - .22, 2.72), (W*.62, .01, .22), bevel=0)
        for k in range(3):
            along(ferro(), (-W*.3 + k*W*.3, -D/2 - .05, 2.4), (-W*.3 + k*W*.3, -D/2 - 1.1, 2.0), .02, verts=6)
        box(K.mat_cloth("toldo_sl", (.1, .06, .035), 8.0), (0, -D/2 - .6, 2.22), (W*.8, 1.15, .03), (-20, 0, 0), 0)
    lanterna(-W/2 + W*(porta + .5)/n + .75, -D/2, 2.3)
    cimalha(W, D, H)
    if telhado == "telhas":
        telhado_duas_aguas(W, D, H + .3, 1.6 if cumeeira == "x" else 1.9, ao_longo=cumeeira, buraco=((W*.25, -D*.15, W*.3, D*.35) if ruina else None), seed=seed)
        chamine(-W/2 + 1.0, D/2 - .9, H + .3 + 1.2, 1.0, m["brick"])
        if W > 7: chamine(W/2 - 1.2, .2, H + .3 + 1.0, 1.1, m["brick"])
    else:
        platibanda(W, D, H + .3)
        box(reboco("cinza", 7.0, .3), (0, 0, H + .36), (W - .4, D - .4, .12), bevel=.01)
        cyl(latao(), (-W/2 + 1.3, D/2 - 1.3, H + 1.0), .55, 1.2, verts=18)                     # caixa d'água de latão
        for z_ in (.3, .9): torus(ferro(), (-W/2 + 1.3, D/2 - 1.3, H + .4 + z_), .56, .02)
        along(ferro(), (W/2 - .8, -D/2 + .8, H + .4), (W/2 - .8, -D/2 + .8, H + 2.4), .02, verts=6)
    remendo_vigilia(W*.3, -D/2, 1.4, seed=seed); remendo_vigilia(-D*.2, W/2, FH + 1.1, axis="x", sinal=1, seed=seed + 1)
    if ruina:
        for k in range(10):
            o = box(m["brick"], (r.uniform(-W/2, W/2), -D/2 - r.uniform(.3, 1.2), .08), (.24, .12, .08), (0, 0, r.uniform(0, 180)), .004)
    areia_na_base(W, D, seed)
    return {"base": base, "emissivo": "janelas acesas e lanterna"}

sl("sobrado_ocre", fp=(9, 7), kw=dict(W=6.4, D=5.2, cor="ocre", seed=1, acesas=(1,)))(sobrado)
REG["sobrado_ocre"]["fn"].__doc__ = "Sobrado ocre de 1890: dois andares de janelas de arco, sacada de ferro, telhado de barro com chaminé; a janela do antigo 4º andar virou porta."
sl("sobrado_rosa", fp=(11, 7), kw=dict(W=8.0, D=5.4, cor="rosa", seed=2, acesas=(2,), porta=1, telhado="platibanda"))(sobrado)
REG["sobrado_rosa"]["fn"].__doc__ = "Sobrado rosa-queimado de platibanda com balaústres e urnas, caixa d'água de latão da Vigília no terraço."
sl("sobrado_azul", fp=(7, 7), kw=dict(W=5.0, D=5.0, cor="azul", seed=3, acesas=(0,), porta=1, cumeeira="y"))(sobrado)
REG["sobrado_azul"]["fn"].__doc__ = "Sobrado estreito cinza-azul, duas janelas por andar, telhado com a cumeeira para a rua."
sl("sobrado_loja", fp=(10, 7), kw=dict(W=7.2, D=5.2, cor="amarelo", seed=4, acesas=(0, 3), porta=2, loja=True))(sobrado)
REG["sobrado_loja"]["fn"].__doc__ = "Armazém de secos e molhados: letreiro dourado, toldo de lona remendada, janelas acesas em cima."
sl("sobrado_ruina", fp=(9, 7), kw=dict(W=6.4, D=5.2, cor="branco", seed=5, acesas=(), porta=2, ruina=True))(sobrado)
REG["sobrado_ruina"]["fn"].__doc__ = "Sobrado abandonado: janelas tapadas com tábuas, reboco caído, parte do telhado desabada com os caibros à vista."
sl("sobrado_verde", fp=(9, 7), kw=dict(W=6.0, D=5.2, cor="verde", seed=6, acesas=(2,), porta=0, telhado="platibanda"))(sobrado)
REG["sobrado_verde"]["fn"].__doc__ = "Sobrado verde-garrafa de platibanda, porta na ponta e sacada corrida."

@sl("sobrado_esquina", fp=(10, 10), samples=56, walls=False)
def sobrado_esquina(m, seed=7):
    """Sobrado de esquina com a porta chanfrada no canto da praça, lanterna grande e relógio de rua; reboco cinza,
    telhado de quatro águas de telha de barro."""
    r = rnd(seed); W, D = 7.0, 7.0; FH = 3.1; H = 2*FH; W_ATUAL[0] = W
    c = 1.1
    # corpo com o canto (+X, -Y) cortado: duas caixas e o chanfro
    reb = reboco("cinza", seed, .4)
    box(reb, (-c/2, 0, H/2), (W - c, D, H), bevel=.012); box(reb, (W/2 - c/2, c/2, H/2), (c, D - c, H), bevel=.012)
    box(cantaria(), (-c/2, 0, .2), (W - c + .1, D + .1, .4), bevel=.01); box(cantaria(), (W/2 - c/2, c/2, .2), (c + .1, D - c + .1, .4), bevel=.01)
    base = [-W/2, -D/2, W/2, D/2]
    can = cantaria()
    for (sx, sy) in [(-1, -1), (-1, 1), (1, 1)]:
        for k in range(int(H/.6)): box(can, (sx*(W/2 - .02), sy*(D/2 - .02), .3 + k*.6), (.44 if k % 2 else .3, .3 if k % 2 else .44, .5), bevel=.01)
    # canto chanfrado (+X, -Y): pilar oblíquo com a porta
    box(reboco("cinza", seed, .4), (W/2 - c*.5, -D/2 + c*.5, H/2), (c*1.42, .3, H), (0, 0, 45), .01)
    box(cantaria(), (W/2 - c*.5, -D/2 + c*.5, .2), (c*1.5, .4, .4), (0, 0, 45), .01)
    # porta no chanfro (feita à mão: sem a função janela, que só sabe eixos)
    rot = (0, 0, 45); dx, dy = .707*.16, .707*.16
    box(madeira("sangue"), (W/2 - c*.5 - dx, -D/2 + c*.5 - dy, 1.2), (1.1, .06, 2.3), rot, .004)
    box(vao(), (W/2 - c*.5 - dx*.5, -D/2 + c*.5 - dy*.5, 2.7), (1.1, .2, .5), rot, 0)
    cyl(cantaria(), (W/2 - c*.5 - dx*.6, -D/2 + c*.5 - dy*.6, 2.4), .72, .18, (90, 0, 45), 20)
    cyl(vao(), (W/2 - c*.5 - dx*.9, -D/2 + c*.5 - dy*.9, 2.4), .55, .1, (90, 0, 45), 20)
    for k in range(3): box(madeira("crua"), (W/2 - c*.5 - dx*(4 + k*1.5), -D/2 + c*.5 - dy*(4 + k*1.5), -.12 - k*.1), (1.3, .22, .05), rot, 0)
    # relógio de rua acima da porta
    cyl(cantaria(), (W/2 - c*.5 - dx*1.2, -D/2 + c*.5 - dy*1.2, FH + 2.2), .55, .14, (90, 0, 45), 24)
    cyl(K.mat_porcelain("mostrador_sl"), (W/2 - c*.5 - dx*1.5, -D/2 + c*.5 - dy*1.5, FH + 2.2), .45, .04, (90, 0, 45), 24)
    box(K.mat_solid("ponteiro_sl", (.02, .02, .02)), (W/2 - c*.5 - dx*1.8, -D/2 + c*.5 - dy*1.8, FH + 2.3), (.03, .03, .3), (0, 25, 45), 0)
    # janelas nas duas fachadas visíveis (-Y e +X)
    n = 3
    for k in range(n):
        x = -W/2 + (W - c)*(k + .5)/n
        janela(x, .55, .9, 2.0, -D/2, tipo=("acesa" if k == 1 else "escura"), seed=seed*3 + k)
        janela(x, FH + .55, .9, 2.0, -D/2, tipo=("escura" if k != 0 else "quebrada"), seed=seed*5 + k, sacada=True)
        y = D/2 - (D - c)*(k + .5)/n
        janela(y, .55, .9, 2.0, W/2, tipo=("escura" if k != 1 else "tabuas"), axis="x", sinal=1, seed=seed*7 + k)
        janela(y, FH + .55, .9, 2.0, W/2, tipo=("acesa" if k == 2 else "escura"), axis="x", sinal=1, seed=seed*9 + k, sacada=(k == 1), arco=False)
    box(cantaria(), (0, -D/2 - .06, FH - .03), (W + .3, .12, .14), bevel=.006); box(cantaria(), (W/2 + .06, 0, FH - .03), (.12, D + .3, .14), bevel=.006)
    lanterna(W/2 - c*.5 - 1.6, -D/2, 2.5)
    cimalha(W, D, H)
    # telhado de quatro águas: pirâmide achatada
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=(W + .9)*.707, radius2=.25, depth=1.9, location=(0, 0, H + .3 + .95), rotation=(0, 0, math.radians(45)))
    o = bpy.context.object; o.scale = (1, D/W, 1); bpy.ops.object.transform_apply(scale=True); o.data.materials.append(telha())
    chamine(-W/2 + 1.1, D/2 - 1.1, H + 1.2, 1.3, m["brick"])
    cyl(zinco(), (-1.0, 1.0, H + 2.3), .2, .5, verts=8, r2=.0)                                       # agulha de zinco
    remendo_vigilia(-W*.3, -D/2, FH + 1.2, seed=seed)
    areia_na_base(W, D, seed)
    return {"base": base, "emissivo": "janelas acesas e lanterna"}

@sl("casario", fp=(13, 6), samples=56)
def casario(m, seed=8):
    """Casario geminado de três casas estreitas (ocre, rosa e branca), cada uma com a sua porta, telhados de barro em
    degrau e uma lanterna comum; a casa do meio tem a janela acesa."""
    r = rnd(seed); FH = 3.0; D = 4.4; cores = ["ocre", "rosa", "branco"]; ws = [3.2, 3.0, 3.4]; W = sum(ws)
    W_ATUAL[0] = W
    x0 = -W/2; base = [-W/2, -D/2, W/2, D/2]
    box(cantaria(), (0, 0, .2), (W + .1, D + .1, .4), bevel=.01)
    for i, (w, cor) in enumerate(zip(ws, cores)):
        cx = x0 + w/2; H = 2*FH + (0, .35, -.3)[i]
        box(reboco(cor, seed + i, .45), (cx, 0, H/2), (w, D, H), bevel=.01)
        for f in range(2):
            z = .55 + f*FH
            if f == 0: janela(cx - .55, z, .8, 1.9, -D/2, tipo="porta", seed=seed + i, venez=False); janela(cx + .65, z, .75, 1.9, -D/2, tipo=("tabuas" if i == 2 else "escura"), seed=seed + i + 3, venez=False)
            else:
                janela(cx - .55, z, .8, 1.9, -D/2, tipo=("acesa" if i == 1 else "escura"), seed=seed + i + 5, sacada=(i == 1))
                janela(cx + .65, z, .75, 1.9, -D/2, tipo=("quebrada" if i == 0 else "escura"), seed=seed + i + 7, arco=False)
        box(cantaria(), (cx, 0, H + .1), (w + .3, D + .3, .2), bevel=.01)
        o = prism(telha(), (cx, 0, H + .2), D + .6, w + .25, 1.3); o.rotation_euler = (0, 0, math.radians(90))
        cyl(telha(), (cx, 0, H + 1.5), .06, w + .25, (0, 90, 0), 8)
        box(reboco(cor, seed + i, .45), (x0 + w, 0, H/2 + .3), (.25, D - .2, H + .6), bevel=.01) if i < 2 else None   # empena entre casas
        x0 += w
    lanterna(-W/2 + ws[0] + ws[1]/2 - 1.6, -D/2, 2.3)
    chamine(-W/2 + 1.2, D/2 - .8, 2*FH + 1.0, 1.0, m["brick"]); chamine(W/2 - 1.3, .3, 2*FH + .6, 1.1, m["brick"])
    lado_x(D, 0, FH, 2, seed + 40)
    for sx in (-1, 1): box(cantaria(), (sx*(W/2 - .02), -D/2 + .1, 3.0), (.3, .4, 6.0), bevel=.01)
    remendo_vigilia(W*.25, -D/2, FH + 1.3, seed=seed)
    areia_na_base(W, D, seed)
    return {"base": base, "emissivo": "janela acesa e lanterna"}

@sl("radio_sao_lazaro", fp=(10, 8), samples=56, walls=False)
def radio_sao_lazaro(m, seed=9):
    """Rádio São Lázaro: sobrado de platibanda da antiga Companhia Telefônica, com o mastro de rádio de treliça no
    terraço (luz vermelha piscando), fios descendo para a rua, alto-falantes de corneta e a janela do estúdio acesa."""
    r = rnd(seed); W, D = 7.0, 5.6; FH = 3.1; H = 2*FH; W_ATUAL[0] = W
    base = corpo(W, D, H, "branco", seed, .45)
    cunhais(W, D, H)
    n = 4
    for k in range(n):
        x = -W/2 + W*(k + .5)/n
        janela(x, .55, .85, 2.0, -D/2, tipo=("porta" if k == 1 else ("tabuas" if k == 3 else "escura")), seed=seed*3 + k, venez=(k != 1))
        janela(x, FH + .55, .85, 2.0, -D/2, tipo=("acesa" if k in (1, 2) else "escura"), seed=seed*5 + k, sacada=(k in (1, 2)), arco=False)
    box(cantaria(), (0, -D/2 - .06, FH - .03), (W + .3, .12, .14), bevel=.006)
    lado_x(D, 0, FH, 2, seed + 40)
    # letreiro de azulejo e lanterna
    box(K.mat_solid("azulejo_sl", (.08, .12, .17), .1, .35), (0, -D/2 - .17, 2.75), (W*.7, .04, .45), bevel=.003)
    box(K.mat_solid("letras_sl", (.3, .3, .28), 0, .5), (0, -D/2 - .2, 2.75), (W*.45, .01, .16), bevel=0)
    lanterna(-W/2 + W*1.5/n + .7, -D/2, 2.3)
    cimalha(W, D, H); platibanda(W, D, H + .3, .8, urnas=False)
    box(reboco("cinza", 7.0, .3), (0, 0, H + .36), (W - .4, D - .4, .12), bevel=.01)
    # mastro de treliça (3 pernas) com luz vermelha
    mz = H + .4; mh = 7.5
    for k in range(3):
        a = math.radians(120*k + 30); p0 = (1.2 + math.cos(a)*.5, .6 + math.sin(a)*.5, mz); p1 = (1.2 + math.cos(a)*.12, .6 + math.sin(a)*.12, mz + mh)
        along(ferro(), p0, p1, .03, verts=6)
    for z_ in range(1, 7):
        rr = .5 - .38*z_/7; zz = mz + mh*z_/7
        for k in range(3):
            a0 = math.radians(120*k + 30); a1 = math.radians(120*(k + 1) + 30)
            along(ferro(), (1.2 + math.cos(a0)*rr, .6 + math.sin(a0)*rr, zz), (1.2 + math.cos(a1)*rr, .6 + math.sin(a1)*rr, zz), .012, verts=4)
            along(ferro(), (1.2 + math.cos(a0)*rr, .6 + math.sin(a0)*rr, zz), (1.2 + math.cos(a1)*(rr + .05), .6 + math.sin(a1)*(rr + .05), zz + mh/7), .008, verts=4)
    cyl(ferro(), (1.2, .6, mz + mh + .4), .02, .8, verts=6)
    sphere(K.mat_emit("luz_radio", (1, .12, .06), 14), (1.2, .6, mz + mh + .85), (.12, .12, .12), segs=10)
    point((1.2, .6, mz + mh + .9), (1, .15, .08), 120, .1)
    for s in (-1, 1): along(ferro(), (1.2, .6, mz + mh*.8), (1.2 + s*2.6, .6 + s*1.8, mz + .3), .008, verts=4)   # estais
    # alto-falantes de corneta e fios para a rua
    for (x, sgn) in ((-2.2, -1), (2.4, -1)):
        cyl(zinco(), (x, -D/2 - .35, H - .3), .18, .5, (90 - 25*sgn, 0, 0), 10, r2=.05)
    for k in range(3):
        along(ferro(), (-W/2 + 1 + k*2.2, -D/2 - .1, H - .1), (-W/2 - 1.5 + k*2.2, -D/2 - 3.2, 3.2), .006, verts=4)
    cyl(ferro(), (-W/2 - 1.5, -D/2 - 3.2, 2.2), .05, 4.4, verts=8); box(madeira("escura"), (-W/2 - 1.5, -D/2 - 3.2, 4.1), (.9, .08, .08), bevel=.003)
    # gerador a vapor no beco (+X), fumaça
    cyl(ferro(), (W/2 + .9, .6, .55), .45, 1.1, (0, 90, 0), 16); cyl(latao(), (W/2 + .9, .6, 1.3), .09, .7, verts=8)
    remendo_vigilia(-W*.35, -D/2, FH + 1.3, seed=seed)
    areia_na_base(W, D, seed)
    return {"base": base, "emissivo": "janelas do estúdio (âmbar) e luz do mastro (vermelha)"}

# ================================================================ PRAÇA
@sl("coreto", fp=(8, 8), samples=56, walls=False, cat="predios")
def coreto(m, seed=10):
    """Coreto da Praça da Matriz: base de cantaria com escada, oito colunas de ferro fundido com lambrequim, telhado de
    chapa pintada de verde em bico com catavento, gradil de ferro batido e quatro lanternas nos braços de fora."""
    r = rnd(seed); R = 2.6; can = cantaria(); fer = ferro()
    chapa = _c("chapa_coreto", lambda: K.mat_metal("chapa_coreto", (.05, .075, .06), .22, 6.0, .5))
    cyl(can, (0, 0, .35), R + .5, .7, verts=8, rot=(0, 0, 22.5))
    cyl(can, (0, 0, .75), R + .25, .1, verts=8, rot=(0, 0, 22.5))
    cyl(madeira("crua"), (0, 0, .82), R + .1, .06, verts=8, rot=(0, 0, 22.5))
    for k in range(3): box(can, (0, -(R + .7 + k*.35), .6 - k*.2), (1.4, .35, .2), bevel=.01)     # escada para a praça
    for k in range(8):
        a = math.radians(45*k + 22.5); x, y = math.cos(a)*R, math.sin(a)*R
        cyl(fer, (x, y, 2.3), .07, 3.0, verts=10); cyl(fer, (x, y, .95), .13, .2, verts=10); cyl(fer, (x, y, 3.72), .13, .16, verts=10)
        torus(fer, (x, y, 2.0), .09, .02)
        a2 = math.radians(45*(k + 1) + 22.5); x2, y2 = math.cos(a2)*R, math.sin(a2)*R
        along(fer, (x, y, 3.8), (x2, y2, 3.8), .04, verts=6)                                       # lambrequim (barra)
        for j in range(7):
            t = (j + .5)/7; px, py = x + (x2 - x)*t, y + (y2 - y)*t
            cyl(fer, (px, py, 3.6), .014, .34, verts=4, r2=0)
        if k != 5:                                                                                     # gradil (abre na escada)
            along(fer, (x, y, 1.8), (x2, y2, 1.8), .025, verts=5); along(fer, (x, y, 1.0), (x2, y2, 1.0), .025, verts=5)
            for j in range(7):
                t = (j + .5)/7; px, py = x + (x2 - x)*t, y + (y2 - y)*t
                cyl(fer, (px, py, 1.4), .012, .8, verts=4)
                if j % 2: torus(fer, (px, py, 1.4), .06, .008, (0, 0, math.degrees(a) + 90))
    bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=R + .55, radius2=.1, depth=1.7, location=(0, 0, 4.7), rotation=(0, 0, math.radians(22.5)))
    o = bpy.context.object; o.data.materials.append(chapa)
    for k in range(8):                                                                               # nervuras e beiral
        a = math.radians(45*k + 22.5)
        along(fer, (math.cos(a)*(R + .55), math.sin(a)*(R + .55), 3.85), (0, 0, 5.55), .03, verts=5)
        a2 = math.radians(45*(k + 1) + 22.5)
        along(fer, (math.cos(a)*(R + .55), math.sin(a)*(R + .55), 3.85), (math.cos(a2)*(R + .55), math.sin(a2)*(R + .55), 3.85), .03, verts=5)
    cyl(fer, (0, 0, 6.0), .02, 1.0, verts=6); box(fer, (0, 0, 6.3), (.5, .02, .18), (0, 0, 30), 0)   # catavento
    sphere(latao(), (0, 0, 5.6), (.12, .12, .12), segs=8)
    # lanternas nos braços de fora (nos postes que a câmera vê) e um lampião pendurado no meio
    for k in (4, 5, 6, 7):
        a = math.radians(45*k + 22.5); x, y = math.cos(a)*R, math.sin(a)*R
        ux, uy = math.cos(a), math.sin(a)
        along(fer, (x, y, 3.3), (x + ux*.55, y + uy*.55, 3.3), .018, verts=6); along(fer, (x, y, 3.0), (x + ux*.5, y + uy*.5, 3.28), .012, verts=5)
        cyl(latao(), (x + ux*.55, y + uy*.55, 3.08), .11, .34, verts=6, r2=.08)
        cyl(K.mat_emit("chama_coreto", AMBAR, 9), (x + ux*.55, y + uy*.55, 3.08), .075, .26, verts=6)
        cyl(latao(), (x + ux*.55, y + uy*.55, 3.3), .13, .05, verts=6, r2=.03)
        point((x + ux*.7, y + uy*.7, 3.0), AMBAR, 60, .06)
    along(fer, (0, 0, 4.6), (0, 0, 3.4), .012, verts=4)
    cyl(latao(), (0, 0, 3.2), .14, .4, verts=6, r2=.1); cyl(K.mat_emit("chama_coreto", AMBAR, 9), (0, 0, 3.2), .09, .3, verts=6)
    point((0, 0, 3.0), AMBAR, 70, .08)
    box(madeira("escura"), (0, .7, 1.2), (1.6, .5, .08), bevel=.005)                                 # banco da banda
    for k in range(3): box(madeira("escura"), (-.8 + k*.8, -.4, 1.1), (.4, .4, .5), (0, 0, r.uniform(-20, 20)), .003)   # cadeiras
    areia_na_base(2*R, 2*R, seed, .3)
    return {"base": [-R - .6, -R - .6, R + .6, R + .6], "emissivo": "lanternas (âmbar)"}

@sl("chafariz", fp=(6, 6), samples=48, walls=False)
def chafariz(m, seed=11):
    """Chafariz de ferro fundido da praça (1888): tanque de cantaria, coluna com quatro bicas de leão e a taça de cima;
    seco há trinta anos, com um fio de água verde do Amargo no fundo."""
    r = rnd(seed); can = cantaria(); fer = ferro(); R = 2.0
    cyl(can, (0, 0, .3), R, .6, verts=24); cyl(vao(), (0, 0, .55), R - .25, .2, verts=24)
    torus(can, (0, 0, .6), R - .1, .12)
    cyl(K.mat_emit("amargo_chafariz", (.35, 1.0, .35), 1.2), (0, 0, .46), R - .3, .02, verts=24)
    point((0, 0, .7), (.4, 1, .3), 10, .5)
    cyl(can, (0, 0, .85), .55, .5, verts=12); cyl(fer, (0, 0, 1.5), .22, .8, verts=12, r2=.18)
    for k in range(4):
        a = math.radians(90*k); x, y = math.cos(a)*.3, math.sin(a)*.3
        sphere(fer, (x, y, 1.35), (.14, .14, .12), segs=10); along(fer, (x, y, 1.3), (x*2.2, y*2.2, 1.1), .03, verts=6)
    cyl(fer, (0, 0, 1.95), .8, .12, verts=16, r2=.25); cyl(fer, (0, 0, 2.3), .14, .7, verts=10, r2=.1)
    cyl(fer, (0, 0, 2.85), .5, .1, verts=16, r2=.15)
    along(fer, (0, 0, 2.9), (0, 0, 3.5), .05, .02, verts=8); sphere(fer, (0, 0, 3.55), (.1, .1, .12), segs=8)
    for k in range(6):                                                                               # folhas secas e lixo no tanque
        box(madeira("crua"), (r.uniform(-1.2, 1.2), r.uniform(-1.2, 1.2), .5), (.3, .2, .03), (0, 0, r.uniform(0, 180)), 0)
    areia_na_base(2*R, 2*R, seed, .3)
    return {"base": [-R - .1, -R - .1, R + .1, R + .1], "emissivo": "água do Amargo (verde)"}

@sl("mercado_ferro", fp=(14, 9), samples=56)
def mercado_ferro(m, seed=12):
    """Mercado Municipal de 1890: pavilhão de ferro fundido e vidro, aberto nos lados, com as tesouras arqueadas, a
    clarabóia da cumeeira, bancas por baixo e lampiões; metade das vidraças virou chapa de zinco."""
    r = rnd(seed); W, D, H = 10.0, 6.4, 4.2; fer = ferro(); can = cantaria()
    box(can, (0, 0, .15), (W + .6, D + .6, .3), bevel=.01)
    cols = []
    for i in range(5):
        x = -W/2 + W*i/4
        for sy in (-1, 1):
            cyl(fer, (x, sy*D/2, H/2), .09, H, verts=10); cyl(fer, (x, sy*D/2, .5), .16, .4, verts=10)
            cols.append((x, sy*D/2))
            # mãos-francesas
            along(fer, (x, sy*D/2, H - 1.0), (x, sy*D/2*.72, H - .1), .03, verts=5)
    for sy in (-1, 1): box(fer, (0, sy*D/2, H + .05), (W + .3, .14, .1), bevel=.003)
    for i in range(5):                                                                               # tesouras arqueadas
        x = -W/2 + W*i/4
        pts = [(x, -D/2 + D*t, H + math.sin(math.pi*t)*2.2) for t in [k/10 for k in range(11)]]
        for a, b_ in zip(pts, pts[1:]): along(fer, a, b_, .035, verts=6)
        for t in (.25, .5, .75):
            along(fer, (x, -D/2 + D*t, H + .02), (x, -D/2 + D*t, H + math.sin(math.pi*t)*2.2), .018, verts=4)
    # cobertura: faixas entre tesouras, metade vidro escuro e metade zinco
    for i in range(4):
        x0 = -W/2 + W*i/4; x1 = x0 + W/4
        for t0, t1 in [(0, .25), (.25, .5), (.5, .75), (.75, 1)]:
            z0, z1 = H + math.sin(math.pi*t0)*2.2, H + math.sin(math.pi*t1)*2.2
            mat = zinco() if (i + int(t0*4)) % 3 else vidro_escuro()
            a = Vector((x0, -D/2 + D*t0, z0)); b_ = Vector((x1, -D/2 + D*t1, z1))
            c_ = (a + b_)/2; d = (b_ - a); ang = math.atan2(z1 - z0, D*(t1 - t0))
            box(mat, c_, (W/4 + .02, math.hypot(D*(t1 - t0), z1 - z0), .04), (math.degrees(ang), 0, 0), 0)
    for i in range(6):                                                                               # clarabóia da cumeeira
        x = -W/2 + .9 + i*(W - 1.8)/5
        box(clarab_acesa() if i % 2 else vidro_escuro(), (x, 0, H + 2.3), (1.2, 1.4, .06), bevel=0)
    # bancas, caixotes e lampiões por baixo
    for i, x in enumerate((-3.3, -1.1, 1.1, 3.3)):
        box(madeira("escura"), (x, -.6, .75), (1.8, 1.0, .08), bevel=.004)
        for sx in (-1, 1): box(madeira("escura"), (x + sx*.8, -.6, .35), (.08, .9, .7), bevel=.003)
        box(K.mat_cloth("pano_banca", [(.1, .04, .03), (.06, .07, .09), (.12, .1, .05), (.08, .1, .06)][i], 20.0 + i), (x, -.6, .95), (1.7, .9, .3), bevel=0)
        along(fer, (x, -.6, H + .0), (x, -.6, H - .7), .01, verts=4)
        cyl(latao(), (x, -.6, H - .85), .08, .3, verts=6, r2=.06); cyl(K.mat_emit("chama_mercado", AMBAR, 8), (x, -.6, H - .85), .05, .22, verts=6)
        point((x, -.6, H - .95), AMBAR, 45, .06)
    for k in range(7):
        box(madeira("crua"), (r.uniform(-4, 4), 1.4 + r.uniform(-.6, .6), .5), (.6, .6, .55), (0, 0, r.uniform(0, 90)), .004)
    for k in range(4): cyl(madeira("escura"), (r.uniform(-4, 4), 2.3, .45), .3, .8, verts=12)
    # letreiro
    box(fer, (0, -D/2 - .3, H + .5), (W*.5, .06, .7), bevel=.005)
    box(K.mat_solid("letras_mercado", (.4, .32, .12), .3, .4), (0, -D/2 - .34, H + .5), (W*.4, .01, .28), bevel=0)
    areia_na_base(W, D, seed, .3)
    return {"base": [-W/2 - .3, -D/2 - .3, W/2 + .3, D/2 + .3], "emissivo": "lampiões e clarabóia (âmbar)"}

@sl("banco_praca", fp=(2, 1), cat="props", samples=32, walls=True)
def banco_praca(m, seed=13):
    """Banco de praça de ferro fundido e ripas de madeira, uma ripa faltando."""
    fer = ferro(); md = madeira("verde")
    for sx in (-1, 1):
        box(fer, (sx*.7, 0, .22), (.06, .5, .44), (0, 0, 0), .004)
        box(fer, (sx*.7, .22, .55), (.06, .08, .5), (-12, 0, 0), .004)
    for k in range(4):
        if k == 2: continue
        box(md, (0, -.2 + k*.12, .46), (1.6, .1, .035), bevel=.003)
    for k in range(3): box(md, (0, .24 + k*.02, .62 + k*.14), (1.6, .035, .1), (-12, 0, 0), .003)
    return {"base": [-.8, -.3, .8, .3]}

@sl("poste_relogio", fp=(1, 1), cat="props", samples=32, walls=False)
def poste_relogio(m, seed=14):
    """Relógio de rua de ferro fundido, de quatro faces, parado nas 3 e 12 (a hora da terceira trombeta)."""
    fer = ferro()
    cyl(fer, (0, 0, .15), .25, .3, verts=10, r2=.14); cyl(fer, (0, 0, 1.6), .05, 2.7, verts=10, r2=.04)
    for z in (.5, 2.6): torus(fer, (0, 0, z), .07, .015)
    box(fer, (0, 0, 3.4), (.7, .7, .7), bevel=.02)
    for (x, y, rz) in [(0, -.36, 0), (.36, 0, 90)]:
        cyl(K.mat_porcelain("mostrador_rua"), (x, y, 3.4), .26, .03, (90, 0, rz), 24)
        box(K.mat_solid("ponteiro_rua", (.02, .02, .02)), (x - (.0 if rz else 0), y - (.02 if rz == 0 else 0), 3.5), (.02, .02, .2), (0, 0, rz), 0)
        box(K.mat_solid("ponteiro_rua", (.02, .02, .02)), (x + (.08 if rz == 0 else 0), y + (.0 if rz == 0 else .08), 3.4), (.16 if rz == 0 else .02, .02 if rz == 0 else .16, .02), bevel=0)
    cyl(fer, (0, 0, 3.9), .3, .25, verts=4, r2=.0, rot=(0, 0, 45)); sphere(fer, (0, 0, 4.05), (.05, .05, .05), segs=6)
    return {"base": [-.3, -.3, .3, .3]}

@sl("quiosque", fp=(4, 4), cat="predios", samples=40, walls=False)
def quiosque(m, seed=15):
    """Quiosque de jornais da praça: casinha octogonal de madeira pintada, cartazes da Vigília colados, lampião e
    balcão fechado com tábua; vende velas, não jornal."""
    r = rnd(seed); R = 1.3; md = madeira("verde"); fer = ferro()
    cyl(cantaria(), (0, 0, .1), R + .2, .2, verts=8, rot=(0, 0, 22.5))
    cyl(md, (0, 0, 1.45), R, 2.5, verts=8, rot=(0, 0, 22.5))
    cyl(zinco(), (0, 0, 2.95), R + .35, .6, verts=8, r2=.1, rot=(0, 0, 22.5)); cyl(fer, (0, 0, 3.45), .02, .5, verts=6)
    box(vao(), (0, -R + .02, 1.6), (1.1, .1, .9), bevel=0); box(madeira("crua"), (0, -R - .05, 1.15), (1.3, .25, .08), bevel=.004)
    for k, cor in enumerate([(.3, .25, .18), (.12, .06, .04), (.08, .1, .14)]):
        a = math.radians(45*(k + 2) + 22.5 + 45)
        box(K.mat_solid(f"cartaz_{k}", cor, 0, .9), (math.cos(a)*(R + .02), math.sin(a)*(R + .02), 1.4 + k*.2), (.5, .02, .7), (0, 0, math.degrees(a) + 90), 0)
    along(fer, (-.5, -R, 2.4), (-.5, -R - .4, 2.4), .015, verts=5)
    cyl(latao(), (-.5, -R - .4, 2.25), .07, .26, verts=6, r2=.05); cyl(K.mat_emit("chama_quiosque", AMBAR, 8), (-.5, -R - .4, 2.25), .045, .2, verts=6)
    point((-.5, -R - .5, 2.2), AMBAR, 40, .06)
    return {"base": [-R - .2, -R - .2, R + .2, R + .2], "emissivo": "lampião"}

@sl("portao_cidade", fp=(6, 2), cat="paredes", samples=48, walls=True)
def portao_cidade(m, seed=16):
    """Portão da Cerca da Vigília: dois pilares de cantaria com braseiros, portão de ferro batido aberto e a placa
    'SÃO LÁZARO · VIGÍLIA' pendurada em correntes; bloqueia nos pilares, passa no meio."""
    can = cantaria(); fer = ferro()
    for sx in (-1, 1):
        box(can, (sx*2.0, 0, 1.8), (.8, .8, 3.6), bevel=.015); box(can, (sx*2.0, 0, 3.75), (1.0, 1.0, .3), bevel=.01)
        cyl(fer, (sx*2.0, 0, 4.1), .28, .4, verts=10, r2=.2)
        cyl(K.mat_emit("brasa_portao", (1, .45, .15), 10), (sx*2.0, 0, 4.25), .2, .2, verts=8)
        point((sx*2.0, 0, 4.4), (1, .5, .2), 90, .15)
        # folha do portão aberta (girada 70°)
        ang = -70*sx
        o = box(fer, (sx*(1.6 - .0), -.6*1, 1.4), (1.5, .04, 2.6), (0, 0, ang), .003)
        for k in range(6):
            x = sx*1.6 + (k - 2.5)*.25*math.cos(math.radians(ang)); y = -.6 + (k - 2.5)*.25*math.sin(math.radians(ang))
            cyl(fer, (x, y, 1.5), .02, 2.7, verts=5); cyl(fer, (x, y, 2.9), .04, .12, verts=4, r2=0)
    box(fer, (0, 0, 4.0), (3.4, .08, .08), bevel=.003)
    for sx in (-1, 1): along(fer, (sx*.9, 0, 3.96), (sx*.9, 0, 3.4), .012, verts=4)
    box(madeira("escura"), (0, 0, 3.15), (2.0, .06, .5), bevel=.004)
    box(K.mat_solid("letras_portao", (.32, .3, .26), 0, .5), (0, -.035, 3.15), (1.6, .01, .2), bevel=0)
    return {"base": [-2.5, -.5, 2.5, .5], "passagem": [-1.4, 1.4], "emissivo": "braseiros"}
