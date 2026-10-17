# Kit dos NPCs do DARK PASSAGE (2026-10-17). Mesma base dos monstros do Egito (mrig/XRig, malhas por Skin
# modifier, materiais que leem a posição de repouso e não "nadam" quando a malha deforma, kemet.finalize), com
# peças de gente: corpo vestido, cabeça com rosto, cabelos, chapéus, roupas em camadas e materiais de pano,
# couro, pele e cabelo com vincos, remendos, desbote, gasto nas quinas e sujeira subindo dos pés.
# Um módulo por NPC (npcs/<id>.py) com build() e anims(R), renderizado pelo render.py dos monstros.
# Eixos: o NPC olha para -Y, X é a sua esquerda, Z para cima. Corpo base de 1,8 m (escala por NPC).
import bpy, math, random, os, sys
from mathutils import Vector, Quaternion
_H = os.path.dirname(os.path.abspath(__file__))
for _p in (_H, os.path.join(_H, "..", "monstros")):
    if _p not in sys.path: sys.path.insert(0, _p)
from mrig import *
from atlante import XRig, patina, glow, strip, chain_links, panel, rock, orient, tube, catmull, _math, _mixc
from kemet import finalize, _rest, _mask, _wave, _ramp, _mul, _grime, linho, listras, manchas, ouro, bronze, cobre, \
    faixas_em, tira, TURQ
import bmesh
from base_rig import obj_from_bm

def skirt(name, m, rings, open_front=0.0, seg=48, jag=0.0, seed=1, thick=.012, folds=0, famp=0.0):
    """Saia/sobretudo: anéis [(z, rx, ry, yoff)], abertura frontal open_front (rad), barra rasgada (jag) e dobras
    (folds ondas em volta, famp de amplitude, crescendo para a barra). Igual a personagens/rig.skirt."""
    rnd = random.Random(seed); bm = bmesh.new()
    a0 = -math.pi/2 + open_front; a1 = 3*math.pi/2 - open_front
    closed = open_front <= 0; n = seg if closed else seg + 1; grid = []
    for ri, (z, rx, ry, yo) in enumerate(rings):
        row = []
        for i in range(n):
            t = i/seg; a = a0 + (a1 - a0)*t if not closed else 2*math.pi*t
            zz = z + (rnd.uniform(-jag, jag*.4) if ri == len(rings)-1 and jag else 0)
            k = ri/max(1, len(rings)-1)
            f = 1 + famp*k*(math.sin(folds*a + seed) + .5*math.sin(2.3*folds*a + 2*seed)) if folds else 1
            row.append(bm.verts.new((rx*f*math.cos(a), yo + ry*f*math.sin(a), zz)))
        grid.append(row)
    for r in range(len(grid)-1):
        for i in range(n if closed else n-1):
            j = (i+1) % n; bm.faces.new((grid[r][i], grid[r][j], grid[r+1][j], grid[r+1][i]))
    bm.normal_update(); o = obj_from_bm(name, bm, m)
    if thick:
        o.modifiers.new("solid", 'SOLIDIFY').thickness = thick; apply_mods(o)
        for p in o.data.polygons: p.use_smooth = True
    return o

# luz de recorte por facção (o render.py lê "rim")
RIM = {"vigilia": (.5, .8, 1.0), "arautos": (1.0, .5, .32), "neutro": (.9, .78, .58), "egito": (.95, .7, .42),
       "hermon": (1.0, .62, .38), "eden": (.62, .95, .62)}

def info(faccao="neutro", px=192, tz=.9, escala=1.0, amostras=None, rim_e=6.0, fps_idle=6, fps_walk=10):
    """INFO do render (quadro final px, alvo da câmera em tz metros)."""
    return {"px": px, "target_z": tz*escala, "rim": RIM.get(faccao, RIM["neutro"]), "rim_e": rim_e,
            "samples": int(os.environ.get("AMOSTRAS", amostras or 32)), "fps": {"idle": fps_idle, "walk": fps_walk},
            "loops": ("idle", "walk"), "escala": escala}

# ======================================================================= materiais
def _novo(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    return m, m.node_tree, m.node_tree.nodes["Principled BSDF"]

def _cav(nt, col, fundo=.45, quina=.25):
    """Oclusão barata: frestas escurecem (fundo) e quinas clareiam (gasto)."""
    g = nt.nodes.new("ShaderNodeNewGeometry")
    r = _ramp(nt, g.outputs["Pointiness"], [(.42, (1 - fundo,)*3), (.5, (1, 1, 1)), (.6, (1 + quina,)*3)])
    return _mul(nt, col, r)

def _lin(c, k): return tuple(min(1, v*k) for v in c)
def _cinza(c, k=1.0):
    m = sum(c)/3; return (m*k, m*k*.97, m*k*.92)

def pano(name, rgb, vinco=.4, desbote=.3, remendo=None, rem_amt=.0, mancha=(.05, .04, .03), mancha_amt=.35,
         grime=1.0, rough=.9, trama=70, barra=None, listra=None, listra_per=.06, xadrez=None, pintas=None):
    """Tecido gasto: trama fina, vincos verticais (dobras que leem bem no sprite pequeno), desbote em manchas
    grandes, remendos (células de outra cor), manchas e sujeira subindo dos pés. listra/xadrez: segunda cor."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m, nt, b = _novo(name); P = _rest(nt)
    col = rgb
    if listra or xadrez:
        sp = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(P, sp.inputs[0])
        fx = _math(nt, 'GREATER_THAN', _math(nt, 'FRACT', _math(nt, 'DIVIDE', sp.outputs["X"], listra_per)), .5)
        if xadrez:
            fz = _math(nt, 'GREATER_THAN', _math(nt, 'FRACT', _math(nt, 'DIVIDE', sp.outputs["Z"], listra_per)), .5)
            fx = _math(nt, 'MULTIPLY', _math(nt, 'ADD', fx, fz), .5)
            col = _mixc(nt, fx, rgb, xadrez)
        else:
            col = _mixc(nt, fx, rgb, listra)
    if pintas:  # estampa de florzinhas/pintas: [(cor, escala, tamanho)]
        for k_, (pc, psc, ptam) in enumerate(pintas):
            vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = psc; vo.inputs["Randomness"].default_value = .8
            mp_ = nt.nodes.new("ShaderNodeMapping"); mp_.inputs["Location"].default_value = (k_*.37, k_*.11, k_*.23)
            nt.links.new(P, mp_.inputs[0]); nt.links.new(mp_.outputs[0], vo.inputs["Vector"])
            col = _mixc(nt, _math(nt, 'LESS_THAN', vo.outputs["Distance"], ptam), col, pc)
    w1 = _wave(nt, P, trama, (0, 0, 0), .4); w2 = _wave(nt, P, trama, (0, 90, 0), .4)
    tr = _math(nt, 'MULTIPLY', _math(nt, 'ADD', w1, w2), .5)
    trc = _ramp(nt, tr, [(0, (.86, .86, .86)), (1, (1.06, 1.05, 1.03))])
    col = _mul(nt, col, trc)
    vc = _mask(nt, P, 6, .3, .7, 3, .6, stretch=(1, 1, .12))      # vincos compridos no eixo Z
    vcc = _ramp(nt, vc, [(0, (1 - vinco,)*3), (1, (1, 1, 1))])
    col = _mul(nt, col, vcc)
    if desbote:
        col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 2.2, .45, .75, 3, .5), desbote), col, _cinza(rgb, 1.35))
    if remendo and rem_amt:
        vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.inputs["Scale"].default_value = 7; nt.links.new(P, vo.inputs["Vector"])
        sr = nt.nodes.new("ShaderNodeSeparateColor"); nt.links.new(vo.outputs["Color"], sr.inputs[0])
        pm = _math(nt, 'GREATER_THAN', sr.outputs[0], 1 - rem_amt)
        col = _mixc(nt, pm, col, remendo)
        ed = nt.nodes.new("ShaderNodeTexVoronoi"); ed.feature = 'DISTANCE_TO_EDGE'; ed.inputs["Scale"].default_value = 7
        nt.links.new(P, ed.inputs["Vector"])
        pe = _math(nt, 'MULTIPLY', _math(nt, 'LESS_THAN', ed.outputs["Distance"], .035), pm)
        col = _mixc(nt, _math(nt, 'MULTIPLY', pe, .8), col, _lin(remendo, .35))
    if barra:  # barra escura de outra cor (ex. bainha bordada)
        sz = nt.nodes.new("ShaderNodeSeparateXYZ"); nt.links.new(P, sz.inputs[0])
        bm = _math(nt, 'LESS_THAN', sz.outputs["Z"], barra[0])
        col = _mixc(nt, bm, col, barra[1])
    if mancha_amt:
        col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 4.5, .56, .7, 5, 1.2), mancha_amt*1.8), col, mancha)
    col = _grime(nt, P, col, grime, top=1.3)
    col = _cav(nt, col, .5, .15)
    nt.links.new(col, b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = rough
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .35; bump.inputs["Distance"].default_value = .004
    nt.links.new(_math(nt, 'ADD', tr, _math(nt, 'MULTIPLY', vc, 1.5)), bump.inputs["Height"])
    nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m

def couro(name, rgb, rachado=.5, gasto=.45, grime=.8, rough=.55, mancha=(.03, .02, .012)):
    """Couro curtido: craquelado fino escuro, quinas gastas mais claras, brilho irregular."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m, nt, b = _novo(name); P = _rest(nt)
    col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 3, .4, .7, 4, .5), .6), rgb, _lin(rgb, 1.45))
    vo = nt.nodes.new("ShaderNodeTexVoronoi"); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs["Scale"].default_value = 40
    nt.links.new(P, vo.inputs["Vector"])
    cr = _math(nt, 'MULTIPLY', _math(nt, 'LESS_THAN', vo.outputs["Distance"], .05), rachado)
    col = _mixc(nt, cr, col, _lin(rgb, .4))
    col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 5, .58, .7, 5, 1.0), .7), col, mancha)
    col = _grime(nt, P, col, grime, top=1.3)
    col = _cav(nt, col, .55, gasto)
    nt.links.new(col, b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange"); rr.inputs["To Min"].default_value = rough - .15; rr.inputs["To Max"].default_value = rough + .25
    nt.links.new(_mask(nt, P, 8, .3, .7, 3), rr.inputs["Value"]); nt.links.new(rr.outputs[0], b.inputs["Roughness"])
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .3; bump.inputs["Distance"].default_value = .003
    nt.links.new(cr, bump.inputs["Height"]); nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m

def pele(name, rgb, sujo=.35, rubor=(.3, .08, .06), rubor_amt=.25, rough=.55, marcas=None, marcas_amt=0):
    """Pele: rubor em manchas, poros, sujeira; marcas = cor de cicatriz/queimadura/pintura em manchas."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m, nt, b = _novo(name); P = _rest(nt)
    col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 6, .4, .75, 3, .4), rubor_amt), rgb, rubor)
    col = _mul(nt, col, _ramp(nt, _mask(nt, P, 90, .2, .8, 2), [(0, (.9, .9, .9)), (1, (1.04, 1.03, 1.02))]))
    if marcas: col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 7, .55, .62, 5, 1.0), marcas_amt), col, marcas)
    col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 5, .55, .72, 5, 1.0), sujo), col, (.05, .04, .03))
    col = _cav(nt, col, .45, .1)
    nt.links.new(col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    return m

def cabelo(name, rgb, fios=90, rough=.6, grisalho=0.0):
    """Cabelo/barba: fios (faixas finas no eixo vertical) e mechas mais claras."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m, nt, b = _novo(name); P = _rest(nt)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, .08); nt.links.new(P, mp.inputs[0])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = fios; nz.inputs["Detail"].default_value = 3
    nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    col = _mul(nt, rgb, _ramp(nt, nz.outputs["Fac"], [(.3, (.55, .55, .55)), (.7, (1.25, 1.22, 1.2))]))
    if grisalho:
        col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 12, .4, .6, 3, .3, stretch=(1, 1, .2)), grisalho), col, (.5, .49, .47))
    col = _cav(nt, col, .5, .1)
    nt.links.new(col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = rough
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .5; bump.inputs["Distance"].default_value = .003
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m

def ferro(name, rgb=(.09, .09, .09), ferrugem=.45, rough=.45):
    return stained(name, rgb, stain=(.16, .06, .02), amount=ferrugem, scale=7, metal=1, rough=rough, grime=.6, dirt=.5)

def latao(name, rgb=(.5, .34, .12), amount=.35):
    return patina(name, rgb, green=(.1, .16, .09), rough=.38, amount=amount, scale=6, stain=(.05, .035, .02), stain_amt=.5)

def madeira(name, rgb=(.17, .1, .05)):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m, nt, b = _novo(name); P = _rest(nt)
    mp = nt.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, .06); nt.links.new(P, mp.inputs[0])
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 40; nz.inputs["Distortion"].default_value = 2
    nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    col = _mul(nt, rgb, _ramp(nt, nz.outputs["Fac"], [(.35, (.6, .6, .6)), (.65, (1.2, 1.15, 1.1))]))
    col = _mixc(nt, _math(nt, 'MULTIPLY', _mask(nt, P, 5, .56, .7, 5, 1), .6), col, (.03, .02, .012))
    col = _cav(nt, col, .5, .3)
    nt.links.new(col, b.inputs["Base Color"]); b.inputs["Roughness"].default_value = .75
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = .4; bump.inputs["Distance"].default_value = .003
    nt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs[0], b.inputs["Normal"])
    return m

def vidro(name, rgb, rough=.08):
    if name in bpy.data.materials: return bpy.data.materials[name]
    m, nt, b = _novo(name)
    b.inputs["Base Color"].default_value = (*rgb, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = .3
    return m

def escuro(name="k_buraco"): return mat(name, (.006, .005, .004), 0, .95)

# ======================================================================= esqueleto
PROPS = ["prop.R", "prop.L"]

def ossos(extra=None):
    B = humanoid(1.0, 1.0)
    for n in "LR":
        h, t, p = B[f"hand.{n}"]; g = Vector(h).lerp(Vector(t), .6)
        B[f"prop.{n}"] = (tuple(g), tuple(g + Vector((0, -.15, 0))), f"hand.{n}")
    B.update(extra or {})
    return B

def rig(nome, extra=None, ground=.03):
    R = XRig(nome, ossos(extra), ground=ground)
    R.gexclude = set(PROPS) | set((extra or {}).keys())
    return R

def grip(R, n): return R.P(f"prop.{n}")

def fim(R, INFO):
    finalize(R)
    R.arm.scale = [INFO.get("escala", 1.0)]*3
    return R, INFO

# ======================================================================= corpo
def corpo(R, pele_m, tronco, calca, mangas=None, botas=None, maos=None, mulher=False, massa=1.0, larg=1.0,
          barriga=0.0, busto=.6, magro=1.0, cano=.34, bota_r=1.0, descalco=False, pescoco=None, corcunda=0.0,
          punho=1.0, manga_r=1.0, perna_r=1.0):
    """Corpo vestido (volumes de roupa, como as classes): pernas (calça), tronco, braços (mangas), pescoço e
    mãos (pele ou luva), botas com cano dobrado. massa: escala geral; larg: ombros; barriga 0..1; magro < 1 afina;
    corcunda 0..1; punho: largura do punho da manga; manga_r/perna_r: folga das mangas/calças."""
    P = R.P; k = massa*magro; mangas = mangas or tronco; maos = maos or pele_m
    hx = 1.1 if mulher else 1.0; pr = perna_r
    j = {"pelvis": (0, 0, .95, .14*k*hx, .108*k)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, kn, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .09*k*hx*pr); j[f"th{n}"] = (*h.lerp(kn, .5), .078*k*pr); j[f"knee{n}"] = (*kn, .06*k*pr)
        j[f"calf{n}"] = (*kn.lerp(a, .32), .062*k*pr); j[f"ank{n}"] = (*a, .046*k*pr)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"th{n}"), (f"th{n}", f"knee{n}"), (f"knee{n}", f"calf{n}"), (f"calf{n}", f"ank{n}")]
        if descalco or not botas:
            j[f"heel{n}"] = (*(a + Vector((0, .035, -.05))), .036); j[f"toe{n}"] = (*(P(f"foot.{n}", 1) + Vector((0, -.02, 0))), .04, .026)
            e += [(f"ank{n}", f"heel{n}"), (f"ank{n}", f"toe{n}")]
    legs = skin_mesh("k_pernas", j, e, calca)
    R.bind(legs, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R", "foot.L", "foot.R"])
    if descalco:
        for n in "LR":
            a = P(f"foot.{n}"); t = P(f"foot.{n}", 1)
            pj = {"a": (*a, .042*k), "h": (*(a + Vector((0, .03, -.05))), .038), "t": (*(t + Vector((0, -.02, 0))), .042, .024)}
            R.bind(skin_mesh(f"k_pe{n}", pj, [("a", "h"), ("a", "t")], pele_m), [f"shin.{n}", f"foot.{n}"])
    elif botas:
        for n in "LR":
            kn, a, t = P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
            top = kn.lerp(a, max(0, (kn.z - cano)/(kn.z - a.z)))
            br = bota_r
            bj = {"top": (*top, .068*br), "ank": (*a, .06*br), "heel": (*(a + Vector((0, .04, -.05))), .05*br),
                  "toe": (*(t + Vector((0, -.01, 0))), .048*br, .04*br)}
            bo = skin_mesh(f"k_bota{n}", bj, [("top", "ank"), ("ank", "heel"), ("ank", "toe")], botas)
            R.bind(bo, [f"shin.{n}", f"foot.{n}"])
            R.rigid([prim("primitive_torus_add", botas, top + Vector((0, 0, .005)), (1, 1, 1.3), major_radius=.07*br, minor_radius=.015),
                     prim("primitive_torus_add", botas, a.lerp(top, .45), (1, 1, 1), major_radius=.064*br, minor_radius=.007)], f"shin.{n}")
    # tronco
    bb = barriga; ch = (.16 if mulher else .175)*larg
    t = {"pelvis": (0, 0, .97, .15*k*hx, .115*k), "waist": (0, -.02*bb, 1.13, (.145 + .06*bb)*k*(.93 if mulher else 1), (.11 + .07*bb)*k),
         "chest": (0, .025*corcunda, 1.33, ch*k, .12*k), "neck": (0, .03*corcunda - .005, 1.49, .062*k), "neck2": (0, -.01, 1.55, .05)}
    te = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    if bb: t["belly"] = (0, -.05*bb, 1.2, (.15 + .05*bb)*k, (.12 + .06*bb)*k); te.append(("waist", "belly"))
    if corcunda: t["hump"] = (0, .11*corcunda, 1.4, .13*k, .1*k*(1 + .6*corcunda)); te.append(("chest", "hump"))
    torso = skin_mesh("k_tronco", t, te, tronco)
    R.bind(torso, ["hips", "spine", "chest", "neck"])
    if mulher and busto:
        R.rigid([prim("primitive_uv_sphere_add", tronco, (.058*s*larg, -.085*k, 1.335), (.058*k*busto + .02, .05*k*busto + .02, .05*k*busto + .02),
                      segments=12, ring_count=8) for s in (1, -1)], "chest")
    # braços (manga larga, punho)
    mr = manga_r
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        aj = {"c": (*(sh + Vector((-.06*s, 0, -.02))), .07*k*larg), "sh": (*sh, .072*k*mr*larg), "el": (*el, .056*k*mr),
              "wr": (*wr.lerp(el, .08), .045*punho*k*mr)}
        ar = skin_mesh(f"k_braco{n}", aj, [("c", "sh"), ("sh", "el"), ("el", "wr")], mangas)
        R.bind(ar, ["chest", f"upper_arm.{n}", f"forearm.{n}"])
        mao(R, n, maos, k)
    pj = {"a": (0, -.005, 1.47, .052*k), "b": (0, -.012, 1.56, .047*k), "c": (0, -.015, 1.62, .045*k)}
    R.bind(skin_mesh("k_pescoco", pj, [("a", "b"), ("b", "c")], pescoco or pele_m), ["chest", "neck", "head"])
    return R

def mao(R, n, m, k=1.0, aberta=False):
    o_, ax, u, sd = R.frame(f"hand.{n}")
    hd = [prim("primitive_uv_sphere_add", m, o_ + ax*.05, (.036*k, .042*k, .052), segments=10, ring_count=8)]
    hd[0].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
    for f in range(4):
        c = o_ + ax*.09 + sd*(-.025 + .017*f)
        if aberta: hd.append(along("primitive_cylinder_add", m, c, c + ax*.04, .008, vertices=6))
        else: hd.append(prim("primitive_uv_sphere_add", m, c + u*.012, (.013, .017, .015), segments=6, ring_count=4))
    hd.append(prim("primitive_uv_sphere_add", m, o_ + ax*.05 - u*.028, (.012, .018, .011), segments=6, ring_count=4))
    R.rigid(hd, f"hand.{n}")

# ======================================================================= cabeça
HC = Vector((0, -.012, 1.68))   # centro do crânio

def cabeca(R, pele_m, mulher=False, idade=.4, olhos=(.03, .025, .02), nariz=1.0, queixo=1.0, orelhas=True, cego=False,
           magro=1.0, esc=1.0, olho_vidro=None, tapa_olho=None, sobrancelha=None):
    """Cabeça com rosto: crânio, maçãs, mandíbula, nariz, arcada, órbitas com olhos, orelhas.
    idade: 0 jovem .. 1 velho (bochecha cai, órbita funda). Devolve a lista de peças (ainda não presa)."""
    c = HC; s = esc; rx = (.08 if mulher else .086)*s; out = []
    out.append(prim("primitive_uv_sphere_add", pele_m, c, (rx, .098*s, .108*s), segments=18, ring_count=12))
    jw = (.06 if mulher else .067)*queixo*s
    out.append(prim("primitive_uv_sphere_add", pele_m, c + Vector((0, -.04*s, -.075*s)), (jw, .06*s*magro, .048*s), segments=14, ring_count=10))
    out.append(prim("primitive_uv_sphere_add", pele_m, c + Vector((0, -.085*s, -.105*s)), (.026*s*queixo, .02*s, .022*s), segments=10, ring_count=6))
    for sd in (1, -1):  # maçãs do rosto
        out.append(prim("primitive_uv_sphere_add", pele_m, c + Vector((.045*sd*s, -.075*s, -.025*s - .012*idade)),
                        (.028*s, .022*s, .022*s), segments=10, ring_count=6))
    out.append(prim("primitive_uv_sphere_add", pele_m, c + Vector((0, -.088*s, .022*s)), (.068*s, .018*s, .016*s), segments=12, ring_count=6))  # arcada
    out.append(along("primitive_cone_add", pele_m, c + Vector((0, -.096*s, .01*s)), c + Vector((0, -.118*s*nariz, -.035*s)), .016*s,
                     vertices=8, radius1=.7, radius2=1.0))
    out.append(prim("primitive_uv_sphere_add", pele_m, c + Vector((0, -.112*s*nariz, -.038*s)), (.017*s, .013*s, .011*s), segments=8, ring_count=6))
    buraco = escuro()
    branco = mat("k_olho_branco", (.55, .52, .46) if not cego else (.75, .74, .7), 0, .3, dirt=.3)
    for sd in (1, -1):
        e = c + Vector((.032*sd*s, -.088*s, -.002*s))
        out.append(prim("primitive_uv_sphere_add", buraco, e + Vector((0, .006, 0)), (.022*s, .012*s, .013*s*(1 + .2*idade)), segments=10, ring_count=6))
        if olho_vidro and sd == olho_vidro[0]:
            out.append(prim("primitive_uv_sphere_add", olho_vidro[1], e + Vector((0, -.005, 0)), (.012*s, .007*s, .01*s), segments=8, ring_count=6))
        elif tapa_olho and sd == tapa_olho[0]:
            tp = prim("primitive_cylinder_add", tapa_olho[1], e + Vector((0, -.012, 0)), (.024*s, .024*s, .005), rot=(90, 0, 0), vertices=12)
            out.append(tp)
            out.append(strip(tapa_olho[2], e + Vector((-.02*sd, -.004, .016)), c + Vector((.088*sd*s, .02, .03*s)), .007, .003))
        else:
            out.append(prim("primitive_uv_sphere_add", branco, e + Vector((0, -.002, 0)), (.011*s, .006*s, .007*s), segments=8, ring_count=6))
        if sobrancelha:
            out.append(along("primitive_cylinder_add", sobrancelha, e + Vector((-.018*sd, -.018*s, .022*s)), e + Vector((.016*sd, -.014*s, .02*s)),
                             .0055*s, vertices=5))
        if orelhas:
            out.append(prim("primitive_uv_sphere_add", pele_m, c + Vector((.086*sd*s, .01*s, -.01*s)), (.012*s, .022*s, .03*s), segments=8, ring_count=6))
    labio = mat("k_labio", (.16, .07, .06), 0, .5, dirt=.5)
    out.append(prim("primitive_uv_sphere_add", labio, c + Vector((0, -.1*s, -.068*s)), (.022*s, .006*s, .005*s), segments=8, ring_count=4))
    return out

# ----------------------------------------------------------------------- cabelos (devolvem peças para a cabeça)
def cabelo_curto(m, volume=1.0, entradas=0.0):
    c = HC; out = [prim("primitive_uv_sphere_add", m, c + Vector((0, .012, .022 + .01*entradas)), (.09*volume, .101*volume, .1*volume),
                        segments=16, ring_count=10)]
    for sd in (1, -1):
        out.append(prim("primitive_uv_sphere_add", m, c + Vector((.07*sd, .0, -.015)), (.025, .05, .045), segments=8, ring_count=6))
    return out

def careca(m, coroa=.0):
    """Careca com coroa de cabelo baixa nos lados e na nuca (coroa: espessura)."""
    c = HC; out = []
    if coroa:
        t = prim("primitive_torus_add", m, c + Vector((0, .02, -.01)), (1, 1.12, .55), major_radius=.084, minor_radius=coroa,
                 major_segments=24, minor_segments=6, rot=(-12, 0, 0))
        out.append(t)
    return out

def fios_em_pe(m, n=14, alt=.07, seed=3):
    """Fios ralos arrepiados (careca com estática da bobina)."""
    rr = random.Random(seed); out = []
    for k in range(n):
        a = rr.uniform(0, 2*math.pi); r = rr.uniform(.03, .08)
        p = HC + Vector((r*math.cos(a), r*math.sin(a)*1.1 + .01, .1 - r*.4))
        q = p + Vector((math.cos(a)*.02, math.sin(a)*.02, alt*rr.uniform(.6, 1.2)))
        out.append(along("primitive_cone_add", m, p, q, .004, vertices=4, radius1=1, radius2=.2))
    return out

def raspado(m):
    c = HC
    return [prim("primitive_uv_sphere_add", m, c + Vector((0, .006, .012)), (.088, .1, .104), segments=16, ring_count=10)]

def coque(m, lapis=None):
    c = HC; out = cabelo_curto(m, 1.0)
    out.append(prim("primitive_uv_sphere_add", m, c + Vector((0, .1, .04)), (.05, .045, .05), segments=12, ring_count=8))
    if lapis:
        for a in (-30, 25):
            out.append(along("primitive_cylinder_add", lapis, c + Vector((-.06, .1, .03 + a*.001)), c + Vector((.06, .12, .07 - a*.001)), .005, vertices=6))
    return out

def trancas(m, n=2, comp=.32, fio=None):
    c = HC; out = cabelo_curto(m, 1.0)
    for sd in ((1, -1) if n == 2 else (0,)):
        p0 = c + Vector((.06*sd, .06, -.04))
        for k in range(int(comp/.035)):
            p = p0 + Vector((.01*sd, .02 + .012*k, -.035*k))
            out.append(prim("primitive_uv_sphere_add", m, p, (.02, .02, .024), segments=8, ring_count=6))
            if fio and k % 3 == 1:
                out.append(prim("primitive_torus_add", fio, p, (1, 1, 1), major_radius=.021, minor_radius=.004, major_segments=10, minor_segments=3))
    return out

def cabelo_longo(m, comp=.3, volume=1.0):
    out = cabelo_curto(m, volume)
    c = HC
    sk = skirt("k_cabelo_longo", m, [(c.z + .05, .09*volume, .1*volume, .01), (c.z - .05, .1*volume, .1*volume, .03),
                                     (c.z - comp, .11*volume, .07*volume, .06)], open_front=1.1, seg=20, jag=.04, seed=3, thick=.015)
    out.append(sk); return out

def barba(m, comp=.12, larg=1.0, trancada=False, fio=None, bigode=True):
    c = HC; out = []
    out.append(prim("primitive_uv_sphere_add", m, c + Vector((0, -.06, -.09)), (.065*larg, .05, .05), segments=12, ring_count=8))
    if comp > .06:
        p0 = c + Vector((0, -.08, -.12)); p1 = p0 + Vector((0, -.01, -comp))
        out.append(along("primitive_cone_add", m, p0, p1, .05*larg, vertices=10, radius1=1, radius2=.35 if not trancada else .2))
        if trancada and fio:
            for k in range(1, int(comp/.04)):
                out.append(prim("primitive_torus_add", fio, p0.lerp(p1, k*.04/comp), (1, 1, .6), major_radius=.03*larg*(1 - .5*k*.04/comp),
                                minor_radius=.004, major_segments=10, minor_segments=3))
    if bigode:
        for sd in (1, -1):
            out.append(along("primitive_cone_add", m, c + Vector((0, -.108, -.055)), c + Vector((.04*sd, -.1, -.075)), .01,
                             vertices=6, radius1=1, radius2=.4))
    return out

# ----------------------------------------------------------------------- chapéus
def aba_larga(m, aba=.17, copa=.09, fita=None, caido=0.0, furos=0):
    c = HC + Vector((0, .0, .075)); out = []
    b = prim("primitive_cylinder_add", m, c, (aba, aba*1.02, .006), vertices=28)
    if caido:  # aba amassada caindo na frente e atrás
        me = b.data
        for v in me.vertices: v.co.z -= caido*(v.co.y**2)*30
    out.append(b)
    out.append(prim("primitive_uv_sphere_add", m, c + Vector((0, 0, .045)), (.085, .095, copa*.75), segments=16, ring_count=10))
    out.append(prim("primitive_cylinder_add", m, c + Vector((0, 0, .02)), (.088, .098, .03), vertices=20))
    if fita: out.append(prim("primitive_cylinder_add", fita, c + Vector((0, 0, .016)), (.091, .101, .012), vertices=20))
    return out

def cartola(m, alt=.16, amassada=True, fita=None):
    c = HC + Vector((0, .0, .085)); out = [prim("primitive_cylinder_add", m, c, (.13, .13, .005), vertices=24)]
    t = prim("primitive_cylinder_add", m, c + Vector((0, 0, alt/2)), (.083, .09, alt/2), vertices=20, rot=(8 if amassada else 0, -6 if amassada else 0, 0))
    out.append(t)
    if fita: out.append(prim("primitive_cylinder_add", fita, c + Vector((0, 0, .02)), (.087, .094, .014), vertices=20))
    return out

def quepe(m, pala, placa=None):
    c = HC + Vector((0, 0, .07)); out = []
    out.append(prim("primitive_cylinder_add", m, c + Vector((0, .005, .02)), (.1, .108, .035), vertices=20))
    out.append(prim("primitive_cylinder_add", m, c + Vector((0, .01, .05)), (.11, .118, .012), vertices=20))
    pl = prim("primitive_cylinder_add", pala, c + Vector((0, -.09, -.005)), (.085, .05, .005), vertices=16, rot=(-14, 0, 0)); out.append(pl)
    if placa: out.append(prim("primitive_cube_add", placa, c + Vector((0, -.105, .025)), (.018, .004, .012)))
    return out

def lenco(m, no_=True, aba=0.0):
    """Lenço amarrado na cabeça (com nó na nuca e pontas soltas)."""
    c = HC; out = [prim("primitive_uv_sphere_add", m, c + Vector((0, .015, .03)), (.094, .106, .095), segments=16, ring_count=10)]
    if no_:
        n0 = c + Vector((0, .1, -.04))
        out.append(prim("primitive_uv_sphere_add", m, n0, (.025, .02, .02), segments=8, ring_count=6))
        out.append(strip(m, n0, n0 + Vector((.03, .03, -.1)), .03, .005, .3))
        out.append(strip(m, n0, n0 + Vector((-.025, .035, -.08)), .028, .005, -.3))
    return out

def capuz(m, caido=False, ponta=.06):
    c = HC
    if caido:  # capuz caído nas costas
        return [skirt("k_capuz", m, [(1.5, .1, .09, .06), (1.44, .15, .12, .09), (1.32, .13, .08, .12)], open_front=1.6, seg=18, thick=.012)]
    out = [skirt("k_capuz", m, [(c.z + .13, .02, .02, .03 + ponta), (c.z + .1, .1, .11, .01), (c.z - .02, .115, .12, .0),
                                (c.z - .12, .12, .12, .01), (1.47, .17, .13, .03)], open_front=.75, seg=22, thick=.012)]
    return out

def chapeu_palha(m, aba=.19, furos=True):
    out = aba_larga(m, aba=aba, copa=.07, caido=.5)
    if furos:
        bur = escuro()
        for p in ((.11, -.05), (-.08, .1), (.02, .14)):
            out.append(prim("primitive_cylinder_add", bur, HC + Vector((p[0], p[1], .077)), (.012, .012, .008), vertices=8))
    return out

# ======================================================================= roupas
def aba(R, m, z0=1.05, z1=.3, larg=1.0, aberto=.5, fundo=1.0, rodado=1.0, jag=.06, seed=1, nome="k_aba", thick=.012,
        folds=10, famp=.07, ossos=("hips", "spine", "thigh.L", "thigh.R")):
    """Saia de casaco/sobretudo/batina da cintura (z0) até z1, aberta na frente (aberto em rad, 0 = fechada),
    com dobras crescendo para a barra e barra rasgada (jag)."""
    rings = []; n = 6
    for i in range(n):
        t = i/(n - 1); z = z0 + (z1 - z0)*t; tt = t*(1.0 - z1/3)
        rings.append((z, (.165 + .15*tt*rodado)*larg, (.13 + .115*tt*rodado)*larg*fundo, .008*i))
    sk = skirt(nome, m, rings, open_front=aberto, seg=48, jag=jag, seed=seed, thick=thick, folds=folds, famp=famp)
    R.bind(sk, list(ossos), power=3)
    return sk

def avental(R, m, z0=1.22, z1=.55, w0=.13, w1=.17, y=-.12, curva=.03, holes=0.0, seed=2, peito=True, tiras=None):
    """Avental na frente (peitilho opcional) preso ao quadril, com tiras ao pescoço."""
    o = panel("k_avental", m, z0 if not peito else 1.08, z1, w0, w1, y, curva, rows=8, cols=7, jag=.03, seed=seed, holes=holes, thick=.008)
    R.rigid([o], "hips")
    if peito:
        pe = panel("k_peitilho", m, 1.38, 1.08, .1, .12, -.13, .03, rows=4, cols=5, seed=seed + 1, thick=.008)
        tt = [pe]
        if tiras:
            for sd in (1, -1):
                tt.append(strip(tiras, Vector((.09*sd, -.13, 1.38)), Vector((.06*sd, -.02, 1.5)), .018, .004))
        R.rigid(tt, "chest")
    return o

def cinto(R, m, fivela=None, z=.98, r=.19, ry=.82, grosso=.022, alto=1.9):
    """Cinturão (toro achatado por cima da saia do casaco) com fivela na frente."""
    out = [prim("primitive_torus_add", m, (0, 0, z), (1, ry, alto), (0, 4, 0), major_radius=r, minor_radius=grosso)]
    if fivela: out.append(prim("primitive_cube_add", fivela, (0, -r*ry - .008, z), (.032, .009, .026)))
    R.rigid(out, "hips"); return out

def bandoleira(R, m, de=(.15, 1.45), para=(-.15, 1.0), larg=.04, lado=1, fivelas=None):
    """Tira cruzando o peito (frente e costas)."""
    out = []
    a = Vector((de[0]*lado, -.12, de[1])); b = Vector((para[0]*lado, -.13, para[1]))
    out += tira(m, [a, a.lerp(b, .5) + Vector((0, -.03, 0)), b], w=larg, t=.008)
    a2 = Vector((de[0]*lado, .11, de[1])); b2 = Vector((para[0]*lado, .12, para[1]))
    out += tira(m, [a2, a2.lerp(b2, .5) + Vector((0, .02, 0)), b2], w=larg, t=.008)
    if fivelas:
        out.append(prim("primitive_cube_add", fivelas, a.lerp(b, .45) + Vector((0, -.035, 0)), (.015, .006, .015)))
    R.rigid(out, "chest"); return out

def gola(R, m, alta=.07, aberta=True, lapela=True):
    out = [skirt("k_gola", m, [(1.49 + alta, .085, .08, .01), (1.47, .1, .09, .01), (1.43, .13, .1, .0)],
                 open_front=.55 if aberta else 0, seg=24, thick=.01)]
    if lapela:
        for sd in (1, -1):
            out.append(panel("k_lapela", m, 1.44, 1.2, .03, .045, -.115, .0, rows=3, cols=3, thick=.008))
            out[-1].location.x = .055*sd; out[-1].rotation_euler = (0, 0, math.radians(-12*sd))
    R.rigid(out, "chest"); return out

def capa(R, m, z1=.5, larg=1.0, jag=.06, seed=4, aberto=1.2, gola_alta=0.0):
    """Capa/manto dos ombros até z1, aberta na frente."""
    rings = [(1.5 + gola_alta, .13*larg, .1, .02), (1.42, .22*larg, .13, .02)]
    for i in range(1, 5):
        t = i/4; rings.append((1.42 + (z1 - 1.42)*t, (.24 + .06*t)*larg, (.14 + .06*t), .03 + .02*t))
    sk = skirt("k_capa", m, rings, open_front=aberto, seg=40, jag=jag, seed=seed, thick=.012)
    R.bind(sk, ["chest", "spine", "hips", "thigh.L", "thigh.R"], power=3); return sk

def xale(R, m, z1=1.18, jag=.04, seed=5, franja=None):
    rings = [(1.5, .12, .1, .01), (1.42, .2, .14, .01), (1.3, .23, .15, .02), (z1, .22, .15, .02)]
    sk = skirt("k_xale", m, rings, open_front=.5, seg=32, jag=jag, seed=seed, thick=.01)
    R.bind(sk, ["chest", "spine", "upper_arm.L", "upper_arm.R"], power=3)
    return sk

def bolsa(R, m, osso="hips", pos=(.15, -.04, .93), tam=(.05, .03, .06), tampa=None):
    out = [prim("primitive_cube_add", m, pos, tam)]
    out[0].modifiers.new("b", 'BEVEL').width = .01
    if tampa: out.append(prim("primitive_cube_add", tampa, Vector(pos) + Vector((0, -tam[1] - .003, tam[2]*.5)), (tam[0]*1.02, .004, tam[2]*.5)))
    R.rigid(out, osso); return out

def mascara_gas(m, vidro_m, filtro_m, pos=Vector((0, -.12, 1.42)), pendurada=True):
    """Máscara de gás (pendurada no pescoço ou no rosto): corpo de borracha, dois olhos de vidro, filtro redondo."""
    out = [prim("primitive_uv_sphere_add", m, pos, (.06, .04, .055), segments=12, ring_count=8)]
    for sd in (1, -1):
        e = pos + Vector((.026*sd, -.03, .02))
        out.append(prim("primitive_cylinder_add", filtro_m, e, (.018, .018, .008), rot=(90, 0, 0), vertices=12))
        out.append(prim("primitive_cylinder_add", vidro_m, e + Vector((0, -.004, 0)), (.014, .014, .006), rot=(90, 0, 0), vertices=12))
    out.append(along("primitive_cylinder_add", filtro_m, pos + Vector((0, -.03, -.02)), pos + Vector((0, -.07, -.04)), .025, vertices=12))
    return out

# ======================================================================= poses e animação
ARMS = {"upper_arm.L": {"y": 32, "x": -4}, "forearm.L": {"bend": -18}, "upper_arm.R": {"y": -32, "x": -4},
        "forearm.R": {"bend": -18}}

def wave(i, n, k=1.0, ph=0.0): return math.sin(i/n*2*math.pi + ph)*k

def walk_cycle(n=8, step=20, quadril=6):
    out = []
    for i in range(n):
        t = i/n*2*math.pi; s, c = math.sin(t), math.cos(t); th = step*s
        out.append({"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                    "shin.L": {"bend": 6 + 34*max(0, c)**1.3}, "shin.R": {"bend": 6 + 34*max(0, -c)**1.3},
                    "foot.L": {"x": .3*th - 10*max(0, c)}, "foot.R": {"x": -.3*th - 10*max(0, -c)},
                    "hips": {"z": quadril*s, "y": 3*c}, "chest": {"z": -quadril*1.2*s, "y": -3*c}, "head": {"z": 4*s, "y": 2*c},
                    "root": (0, 0, -.012*abs(c))})
    return out

def anims_npc(R, base, n_idle=8, n_walk=8, idle_extra=None, balanco=(1, 1), passo=18, walk_extra=None, aims=None):
    """idle: respiração + olhar lento + gesto do NPC (idle_extra(i, n) -> pose); walk: passo com balanco dos braços
    (balanco = (esq, dir): 0 trava o braço que segura algo)."""
    def B(*p):
        out = merge(base, *p); a = dict(base.get("aim") or {})
        for d in p: a.update(d.get("aim") or {})
        if aims: a.update(aims)
        if a: out["aim"] = a
        return out
    idle = []
    for i in range(n_idle):
        b = wave(i, n_idle); c = math.cos(i/n_idle*2*math.pi)
        p = {"chest": {"x": 1.6*b}, "spine": {"x": .8*b}, "head": {"z": 5*math.sin(i/n_idle*2*math.pi + .8), "x": -1.2*b},
             "upper_arm.L": {"y": -1.2*b}, "upper_arm.R": {"y": 1.2*b}, "root": (0, 0, -.004*(1 + b))}
        if idle_extra: p = merge(p, idle_extra(i, n_idle))
        idle.append(B(p))
    walk = []
    for i, p in enumerate(walk_cycle(n_walk, passo)):
        s = wave(i, n_walk)
        arms = {"upper_arm.L": {"x": 16*s*balanco[0]}, "upper_arm.R": {"x": -16*s*balanco[1]},
                "forearm.L": {"bend": -8*max(0, s)*balanco[0]}, "forearm.R": {"bend": -8*max(0, -s)*balanco[1]}}
        if walk_extra: arms = merge(arms, walk_extra(i, n_walk))
        walk.append(B(p, arms))
    return {"idle": idle, "walk": walk}

# ======================================================================= asas (anjos)
ASAS = {f"wing.{n}": ((.07*s, .13, 1.40), (.30*s, .30, 1.62), "chest") for s, n in ((1, "L"), (-1, "R"))}

def _pena(bm, base, d, n, length, width, rnd, curl=.06):
    w = n.cross(d).normalized(); prof = [.25, .55, .75, .7, .5, .22, 0]; left, right = [], []
    for i, f in enumerate(prof):
        t = i/(len(prof)-1); p = base + d*length*t + n*curl*t*t
        jag = rnd.uniform(-.15, .15)*width if t > .6 else 0
        left.append(bm.verts.new(p + w*(width*f + jag))); right.append(bm.verts.new(p - w*width*f*.6))
    for i in range(len(prof)-1): bm.faces.new((left[i], left[i+1], right[i+1], right[i]))

def asa(R, lado, claro, escuro, tira_m=None, metal=None, fechada=True, esc=1.0, falhas=0.0, seed=7):
    """Asa de penas (cópia adaptada de personagens/classes.wing). fechada: dobrada nas costas, ponta perto do chão.
    falhas: fração de penas arrancadas. Presa ao osso wing.L/wing.R (use rig(..., extra=ASAS))."""
    n = "L" if lado > 0 else "R"; rnd = random.Random(seed + (0 if lado > 0 else 4)); s = lado
    root = R.P(f"wing.{n}")
    if fechada:
        edge = [root, root + Vector((.16*s, .14, .34))*esc, root + Vector((.22*s, .26, -.25))*esc]
        normal = Vector((-.85*s, .5, 0)).normalized()
        def fdir(t): return Vector((s*(.02 + .08*t), .05 + .1*t, -1)).normalized()
    else:
        edge = [root, root + Vector((.25*s, .17, .22))*esc, root + Vector((.65*s, .29, 0))*esc]
        normal = Vector((-.3*s, 1, .1)).normalized()
        def fdir(t): return Vector((s*(.05 + .8*t**1.5), .08 + .1*t, -1)).normalized()
    def at(t):
        if t < .45: return edge[0].lerp(edge[1], t/.45)
        return edge[1].lerp(edge[2], (t-.45)/.55)
    bm = bmesh.new(); prev = None
    for k in range(25):
        t = k/24; a = at(t) + normal*.03; b = a + fdir(t)*(.5 + .35*t**1.3)*esc
        pair = (bm.verts.new(a), bm.verts.new(b))
        if prev: bm.faces.new((prev[0], pair[0], pair[1], prev[1]))
        prev = pair
    out = [obj_from_bm(f"k_membrana{n}", bm, escuro)]
    for cnt, l0, l1, wd, off, m in [(30, .64, 1.0, .1, 0.0, escuro), (22, .36, .52, .095, -.018, claro),
                                    (16, .2, .28, .085, -.034, claro), (9, .1, .14, .07, -.048, claro)]:
        bm = bmesh.new()
        for k in range(cnt):
            if falhas and rnd.random() < falhas: continue
            t = .03 + .97*k/(cnt-1); ln = (l0 + (l1-l0)*t**1.3)*rnd.uniform(.9, 1.07)*esc
            _pena(bm, at(t) + normal*off - fdir(t)*.02, fdir(t), normal, ln, wd*rnd.uniform(.9, 1.15)*esc, rnd)
        o = obj_from_bm(f"k_penas{n}", bm, m); o.modifiers.new("solid", 'SOLIDIFY').thickness = .008; apply_mods(o); out.append(o)
    for a, b in ((edge[0], edge[1]), (edge[1], edge[2])):
        out.append(along("primitive_cylinder_add", claro, a, b, .034*esc, vertices=10))
    if tira_m:
        for t in (.15, .35):
            p = at(t)
            out.append(prim("primitive_torus_add", tira_m, p, (1, 1, 1.5), major_radius=.05*esc, minor_radius=.013,
                            major_segments=12, minor_segments=4))
            if metal: out.append(prim("primitive_cube_add", metal, p + Vector((0, -.05, 0)), (.014, .006, .016)))
    R.rigid(out, f"wing.{n}")
    return out

def halo(m, c, r=.13, raios=8, quebrados=(), grosso=.008, comp=.07):
    """Auréola de ferro com raios (alguns quebrados ao meio)."""
    out = [prim("primitive_torus_add", m, c, (1, 1, 1), major_radius=r, minor_radius=grosso, major_segments=32, minor_segments=6)]
    for k in range(raios):
        a = 2*math.pi*k/raios; d = Vector((math.cos(a), math.sin(a), 0))
        L = comp*(.4 if k in quebrados else 1)
        out.append(along("primitive_cone_add", m, c + d*r, c + d*(r + L), grosso*1.4, vertices=5, radius1=1, radius2=.15 if k not in quebrados else .8))
    return out

def chifre(m, base, d, comp=.12, r=.025, curva=Vector((0, .5, -.2)), n=6, aneis=None, quebrado=False):
    """Chifre curvo em segmentos cônicos (base, direção inicial d, curva puxando para trás)."""
    out = []; p = Vector(base); dv = Vector(d).normalized(); segs = n if not quebrado else n//2
    for k in range(segs):
        t = k/n; q = p + dv*comp/n
        out.append(along("primitive_cone_add", m, p, q, r*(1 - t*.85), vertices=8, radius1=1, radius2=(1 - (t + 1/n)*.85)/(1 - t*.85)))
        if aneis and k in (1, 3): out.append(prim("primitive_torus_add", aneis, p.lerp(q, .5), (1, 1, 1), major_radius=r*(1 - t*.85)*1.15,
                                                  minor_radius=.004, rot=tuple(math.degrees(v) for v in dv.to_track_quat('Z', 'Y').to_euler())))
        p = q; dv = (dv + Vector(curva)*(1/n)*2).normalized()
    return out
pena = _pena

# ======================================================================= Egito (peças de Khem)
def saiote(R, m, z1=.62, plisse=True, avental_m=None, cinto_m=None):
    """Saiote de linho plissado (shendyt) da cintura até z1, com avental frontal opcional."""
    rings = [(1.02, .145, .11, 0), (.92, .158, .123, -.006), (.8, .17, .133, -.01), (z1, .18, .14, -.012)]
    k = skirt("k_saiote", m, rings, seg=40, jag=.025, seed=2, thick=.008, folds=22 if plisse else 0, famp=.02)
    R.bind(k, ["hips", "thigh.L", "thigh.R"], power=3)
    out = []
    if cinto_m: out.append(prim("primitive_torus_add", cinto_m, (0, -.005, 1.01), (1, .8, 1.4), major_radius=.15, minor_radius=.014))
    if avental_m: out.append(prim("primitive_cube_add", avental_m, (0, -.152, .84), (.055, .008, .14), rot=(-8, 0, 0)))
    if out: R.rigid(out, "hips")
    return k

def colar_largo(R, faixas, contas=None, raio=.075, n=4, conta_acesa=None):
    """Colar largo (wesekh): anéis de contas listradas assentados no peito e nos ombros (descem junto do corpo, sem
    abrir em aba); conta_acesa = material emissivo de uma única conta."""
    rings = [(1.5 - .028*k, raio + .021*k, raio*.85 + .013*k, -.006 - .003*k) for k in range(n + 1)]
    c = skirt("k_colar", faixas, rings, seg=36, thick=.008)
    out = [c]; rx, ry, z = raio + .021*n, raio*.85 + .013*n, 1.5 - .028*n
    if contas:
        for k in range(14):
            a = -math.pi/2 + (k - 6.5)*.2
            out.append(prim("primitive_uv_sphere_add", contas, (rx*math.cos(a), ry*math.sin(a) - .008, z - .012), (.01,)*3,
                            segments=6, ring_count=4))
    if conta_acesa:
        out.append(prim("primitive_uv_sphere_add", conta_acesa, (0, -ry - .02, z - .016), (.014,)*3, segments=8, ring_count=6))
    R.rigid(out, "chest"); return out

def remo(m, G, comp=1.8, pa=.35, larg=.11, ferragem=None):
    """Remo comprido ao longo do osso de pegada (para baixo: pá no fim)."""
    out = [along("primitive_cylinder_add", m, G + Vector((0, comp*.25, 0)), G + Vector((0, -comp*.75 + pa, 0)), .018, vertices=8)]
    c = G + Vector((0, -comp*.75 + pa/2, 0))
    out.append(prim("primitive_uv_sphere_add", m, c, (larg, pa/2, .012), segments=12, ring_count=8))
    if ferragem: out.append(prim("primitive_torus_add", ferragem, G + Vector((0, -comp*.75 + pa + .02, 0)), (1, 1, 1), rot=(90, 0, 0), major_radius=.022, minor_radius=.005))
    return out
