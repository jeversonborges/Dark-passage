# Barda de montaria: peças de armadura compartilhadas pelas montarias blindadas (touro e javali).
# Gualdrapa de couro sobre o lombo, placas de ferro enferrujado rebitadas em fileiras que se sobrepõem,
# peitoral de cota e rebites de latão. Tudo em volta dos anéis do corpo (ring_path/surf), então acompanha
# a forma do bicho e as animações (as peças são rígidas nos ossos do corpo).
import math, random
from mathutils import Vector
from mrig import *
from quad import surf, loft

def gualdrapa(name, rings, m, y0, y1, grow=1.06, seg=36):
    """Manta de couro sobre o lombo: anéis do corpo entre y0 e y1, um pouco maiores que a pele."""
    sub = [(c, rx*grow, rz*grow, t) for c, rx, rz, t in rings if y0 <= c.y <= y1]
    return loft(name, sub, m, seg=seg, levels=1)

def placas(rings, m, rows, cols, size, y0, y1, arc, bone_at, rivet_m, seed=1):
    """Fileiras de placas (esferas achatadas) em volta do corpo, de y0 a y1 e de arc[0] a arc[1] graus
    (0 = flanco esquerdo, 90 = lombo). Cada fileira desloca meia coluna, como escama de armadura.
    Devolve {osso: [objetos]} para o caller prender com R.rigid."""
    rr = random.Random(seed); out = {}
    for r in range(rows):
        y = y0 + (y1 - y0)*(r + .5)/rows
        ring = min(rings, key=lambda q: abs(q[0].y - y))
        for c in range(cols):
            f = (c + .35 + .5*(r % 2))/cols
            a = math.radians(arc[0] + (arc[1] - arc[0])*f)
            p, n = surf(ring, a)
            jit = rr.uniform(-.06, .06)
            loc = p + n*size*.15
            o = prim("primitive_uv_sphere_add", m, loc, (size*(1 + jit), size*.9, size*.32), segments=10, ring_count=6)
            o.rotation_euler = n.to_track_quat('Z', 'Y').to_euler()
            rv = prim("primitive_uv_sphere_add", rivet_m, p + n*size*.3, (size*.1, size*.1, size*.1), segments=6, ring_count=4)
            out.setdefault(bone_at(y), []).extend([o, rv])
    return out

def peitoral(m, rivet_m, centro, size, rot=(0, 0, 0)):
    """Peitoral de placa de ferro, cobrindo o peito (virado para a frente, -Y), com rebites de latão."""
    o = prim("primitive_uv_sphere_add", m, centro, (size[0], size[1], size[2]), segments=16, ring_count=10)
    o.rotation_euler = [math.radians(r) for r in rot]
    rv = []
    for k in range(8):
        a = 2*math.pi*k/8
        q = centro + Vector((math.cos(a)*size[0]*.8, -size[1]*.9, math.sin(a)*size[2]*.7))
        rv.append(prim("primitive_uv_sphere_add", rivet_m, q, (.014, .014, .014), segments=6, ring_count=4))
    return [o] + rv

def testeira(m, rivet_m, hb, d, up, size=.13):
    """Placa frontal de ferro rebitada sobre a testa da cabeça (hb = base, d = direção, up = cima)."""
    c = hb + d*.2 + up*.1
    o = prim("primitive_uv_sphere_add", m, c, (size, size*1.1, size*.6), segments=16, ring_count=10)
    o.rotation_euler = d.to_track_quat('Y', 'Z').to_euler()
    rv = [prim("primitive_uv_sphere_add", rivet_m, c + Vector((math.cos(a)*size*.7, 0, math.sin(a)*size*.4)) + d*size*.1,
               (.014, .014, .014), segments=6, ring_count=4) for a in [k*math.pi/3 for k in range(6)]]
    return [o] + rv

def franjas(rings, m, y0, y1, n, comp, arc, seed=2):
    """Caparazão rasgado: tiras de pano pendendo do flanco de baixo (arc em graus, de 180 a 360 = ventre).
    comp = comprimento médio da tira. Devolve a lista de objetos (prender no caller)."""
    rr = random.Random(seed); out = []
    for k in range(n):
        y = y0 + (y1 - y0)*(k + rr.uniform(.2, .8))/n
        ring = min(rings, key=lambda q: abs(q[0].y - y))
        p, _ = surf(ring, math.radians(arc[0] + (arc[1] - arc[0])*rr.random()))
        L = comp*rr.uniform(.6, 1.25)
        out.append(along("primitive_cone_add", m, p, p + Vector((rr.uniform(-.01, .01), rr.uniform(-.01, .01), -L)), comp*.16,
                         vertices=5, radius1=1, radius2=.55))
    return out

def espinhos(rings, m, y0, y1, n, size, arc=(45, 135), seed=4):
    """Espinhos de ferro na crista (cones apontando para fora, arc = ângulos do topo)."""
    rr = random.Random(seed); out = []
    for k in range(n):
        y = y0 + (y1 - y0)*(k + .5)/n
        ring = min(rings, key=lambda q: abs(q[0].y - y))
        p, nrm = surf(ring, math.radians(arc[0] + (arc[1] - arc[0])*rr.random()))
        tip = p + nrm*size*rr.uniform(.8, 1.2)
        out.append(along("primitive_cone_add", m, p, tip, size*.18, vertices=6, radius1=1, radius2=0))
    return out

def caveira(bone_m, dark_m, centro, size=.11):
    """Medalhão de caveira de osso no peito: crânio, órbitas fundas e dentes."""
    o = [prim("primitive_uv_sphere_add", bone_m, centro, (size, size*.9, size*.95), segments=14, ring_count=8)]
    for sx in (1, -1):
        o.append(prim("primitive_uv_sphere_add", dark_m, centro + Vector((sx*size*.35, -size*.8, size*.1)),
                      (size*.22, size*.2, size*.25), segments=8, ring_count=6))
    o.append(prim("primitive_cube_add", bone_m, centro + Vector((0, -size*.6, -size*.7)), (size*.5, size*.25, size*.18)))
    return o

def chanfro(m, sp, hb, d, up, size=.1, n=5):
    """Cabeçote de ferro sobre o focinho: placa comprida em cone e uma crista de espinhos apontando para a frente."""
    plate = along("primitive_cone_add", m, hb + d*.12 + up*size*.8, hb + d*.52 + up*size*.4, size, vertices=12, radius1=1, radius2=.7)
    spikes = []
    for k in range(n):
        p = hb + d*(.18 + .07*k) + up*size*.9
        spikes.append(along("primitive_cone_add", sp, p, p + up*size*1.1 + d*size*.25, size*.22, vertices=6, radius1=1, radius2=0))
    return [plate] + spikes
