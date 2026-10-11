# Prévia do Agrak: o Estádio Municipal de São Lázaro enterrado na areia, com o gramado escavado virando fosso
# de arena. Arquibancadas com plateia do lado de lá (a do lado de cá desabou numa rampa de areia, para a câmera
# isométrica ver o fosso, como as meias-paredes da cripta), três portões, Círculo de Ferro no meio do antigo
# círculo central, placar com o camarote do ogro.
# Uso: blender -b -P previa_coliseu.py -- <saida.png> [amostras]
import bpy, bmesh, math, random, sys, os, json
from mathutils import Vector
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../../assets/ambiente/fontes"))
from kit import *
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--")+1:]
OUT = argv[0]; SAMPLES = int(argv[1]) if len(argv) > 1 else 48
W, H, PXM = 1920, 1080, 38
rnd = random.Random(3)
sc = reset(); sc.cycles.samples = SAMPLES; sc.cycles.sample_clamp_indirect = 1.0; sc.cycles.use_denoising = False  # o Blender do apt vem sem OIDN
sc.render.film_transparent = False
sc.world.color = (.006, .006, .009)
cam = make_cam(); cam.data.ortho_scale = W/PXM
TARGET = Vector((-2.6, .4, 3.5)); cam.location = TARGET + cam_dir()*120
sc.render.resolution_x, sc.render.resolution_y = W, H
lights()
for l in bpy.data.objects:
    if l.type == 'LIGHT' and l.name == "key": l.data.energy = 1.1   # noite: a lua é fraca, o fogo manda

RX, RY = 15.0, 11.0          # fosso 30 x 22 m
FAR = (10, 262)              # arco (graus) com arquibancada (fundo da tela = 135°); o resto é a rampa de areia desabada

def ang_in(a, lo, hi):
    a = (a - lo) % 360; return a <= (hi - lo) % 360

def band(name, m, ri, ro, z0, z1, a0, a1, seg=None, gaps=(), ry_k=RY/RX):
    """Faixa oval sólida entre os raios ri e ro (no eixo X; Y escala por ry_k), de a0 a a1 graus."""
    span = (a1 - a0) % 360 or 360
    seg = seg or max(8, int(span/2))
    bm = bmesh.new(); rows = []
    angs = [a0 + span*i/seg for i in range(seg + 1)]
    for a in angs:
        r = math.radians(a)
        if any(ang_in(a, g0, g1) for g0, g1 in gaps): rows.append(None); continue
        c, s = math.cos(r), math.sin(r)
        rows.append([bm.verts.new((ri*c, ri*ry_k*s, z0)), bm.verts.new((ro*c, ro*ry_k*s, z0)),
                     bm.verts.new((ro*c, ro*ry_k*s, z1)), bm.verts.new((ri*c, ri*ry_k*s, z1))])
    for A, B in zip(rows, rows[1:]):
        if A is None or B is None: continue
        for k in range(4):
            bm.faces.new((A[k], A[(k+1) % 4], B[(k+1) % 4], B[k]))
    for i, R_ in enumerate(rows):  # tampa as pontas
        if R_ is None: continue
        prev = rows[i-1] if i > 0 else None; nxt = rows[i+1] if i < len(rows)-1 else None
        if prev is None or nxt is None: bm.faces.new(R_ if nxt is None else R_[::-1])
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); sc.collection.objects.link(o); me.materials.append(m)
    return o

def oval(a, r, z=0):
    t = math.radians(a); return Vector((r*math.cos(t), r*RY/RX*math.sin(t), z))

concreto = mat_stone("concreto", c1=(.12, .11, .1), c2=(.05, .047, .044), scale=1.2, top=2.5)
concreto2 = mat_stone("concreto_escuro", c1=(.075, .07, .066), c2=(.03, .028, .027), scale=1.6, top=2.5, seed=4)
ferro = mat_metal("ferro", rust=.75); latao = mat_brass()
madeira = mat_wood("madeira"); osso = mat_bone()
sangue = mat_solid("sangue_velho", (.09, .018, .012), 0, .8)
cal = mat_solid("cal", (.42, .4, .35), 0, .95)
escuro = mat_solid("tunel", (.004, .004, .004), 0, 1)
olho = mat_emit("olho_amargo", (.45, 1, .2), 6)
lanterna = mat_emit("lanterna", (1, .55, .2), 4)
panos = [mat_cloth(f"pano{i}", c, seed=i) for i, c in enumerate([(.07, .06, .05), (.11, .05, .035), (.05, .05, .055),
                                                                  (.09, .08, .06), (.13, .09, .05)])]
faixa = mat_cloth("faixa", (.2, .04, .03), seed=9)

# ---------------------------------------------------------------- chão do fosso (antigo gramado)
bpy.ops.mesh.primitive_circle_add(vertices=96, radius=RX + .5, fill_type='NGON', location=(0, 0, 0))
fl = bpy.context.object; fl.scale.y = (RY + .5)/(RX + .5); bpy.ops.object.transform_apply(scale=True)
obj(fl, mat_ground("areia", (8, 8), 2.0))
bpy.ops.mesh.primitive_plane_add(size=140, location=(0, 0, -.05)); obj(bpy.context.object, mat_sand_obj())
# linhas de cal do campo, gastas e falhadas
def linha(a, b, w=.13):
    a, b = Vector(a), Vector(b); n = int((b - a).length/.6)
    for i in range(n):
        if rnd.random() < .22: continue
        p, q = a.lerp(b, i/n), a.lerp(b, (i + rnd.uniform(.6, .95))/n)
        box(cal, ((p + q)/2).to_tuple(), ((q - p).length, w, .012), (0, 0, math.degrees(math.atan2((q-p).y, (q-p).x))), 0)
linha((0, -RY + .3, .01), (0, RY - .3, .01))
for i in range(40):  # círculo central (9,15 m de diâmetro no futebol)
    if rnd.random() < .2: continue
    a0, a1 = 2*math.pi*i/40, 2*math.pi*(i + .8)/40
    p, q = Vector((4.6*math.cos(a0), 4.6*math.sin(a0), .01)), Vector((4.6*math.cos(a1), 4.6*math.sin(a1), .01))
    box(cal, ((p+q)/2).to_tuple(), ((q-p).length, .13, .012), (0, 0, math.degrees(math.atan2((q-p).y, (q-p).x))), 0)
for s in (1, -1):  # grandes áreas, cortadas pelo muro
    linha((s*(RX - 5), -5, .01), (s*(RX - 5), 5, .01)); linha((s*(RX - 5), -5, .01), (s*(RX - .6), -5, .01))
    linha((s*(RX - 5), 5, .01), (s*(RX - .6), 5, .01))
# Círculo de Ferro: anel de trilho cravado, com dormentes
for i in range(36):
    a0, a1 = 2*math.pi*i/36, 2*math.pi*(i + 1)/36
    p, q = Vector((3.5*math.cos(a0), 3.5*math.sin(a0), .07)), Vector((3.5*math.cos(a1), 3.5*math.sin(a1), .07))
    box(ferro, ((p+q)/2).to_tuple(), ((q-p).length + .02, .12, .14), (0, 0, math.degrees(math.atan2((q-p).y, (q-p).x))), .01)
    if i % 3 == 0:
        m_ = (p + q)/2; d = m_.normalized()
        box(madeira, (m_.x, m_.y, .03), (.22, .9, .08), (0, 0, math.degrees(math.atan2(d.y, d.x)) + 90), .01)
# sangue velho, ossos e marcas
for k in range(14):
    p = oval(rnd.uniform(0, 360), rnd.uniform(1, 13)); r = rnd.uniform(.25, .8)
    o = cyl(sangue, (p.x, p.y, .004), r, .006, verts=20); o.scale = (1, rnd.uniform(.35, .8), 1); o.rotation_euler.z = rnd.uniform(0, 3)
    displace(o, .0, .2, k, 1)
for k in range(30):
    p = oval(rnd.uniform(0, 360), rnd.uniform(4, 14)); a = rnd.uniform(0, 360)
    along(osso, (p.x, p.y, .04), (p.x + .35*math.cos(a), p.y + .35*math.sin(a), .05), .03)
# pilares baixos de entulho (cobertura contra o bote dos leões)
for x, y in ((-8, -4.5), (8, 4.5), (-7, 5.5), (7.5, -5)):
    o = box(concreto2, (x, y, .6), (1.4, 1.2, 1.2), (0, 0, rnd.uniform(0, 90)), 0); crumble(o, .18, int(x*10))
    along(ferro, (x, y, .9), (x + .3, y - .2, 1.9), .02); along(ferro, (x + .2, y, .9), (x + .1, y + .3, 1.7), .02)

# ---------------------------------------------------------------- muro do fosso, portões
GATES = {"leoes": (125, 4.0, 3.2), "gigante": (48, 6.0, 4.6), "gladiadores": (315, 4.0, 2.4)}
def gap_of(a, w, r=RX + .4): d = math.degrees(w/2/r)*1.15; return (a - d, a + d)
gaps = [gap_of(a, w) for a, w, h in GATES.values()]
band("muro", concreto2, RX, RX + .7, 0, 3.0, FAR[0], FAR[1], gaps=gaps)
band("mureta", concreto2, RX, RX + .5, 0, 1.1, FAR[1], FAR[0] + 360, gaps=gaps)
# estacas no topo do muro
for a in range(FAR[0], FAR[1], 3):
    if any(ang_in(a, *g) for g in gaps): continue
    p = oval(a, RX + .15, 3.0); q = oval(a, RX - .35, 3.7 + rnd.uniform(-.15, .15))
    along(madeira, p, q, .05, .015, verts=6)
# grades dos portões
def portao(a, w, h, aberto, recheio=None):
    c = oval(a, RX + .35); t = Vector((-math.sin(math.radians(a)), math.cos(math.radians(a))*RY/RX, 0)).normalized()
    nrm = Vector((c.x, c.y, 0)).normalized(); ang = math.degrees(math.atan2(t.y, t.x))
    if aberto < 1: box(escuro, (c + nrm*.9 + Vector((0, 0, h/2))).to_tuple(), (w, 1.4, h), (0, 0, ang), 0)
    for s in (-1, 1):
        box(ferro, (c + t*s*(w/2 + .25) + Vector((0, 0, (h + .6)/2))).to_tuple(), (.5, .9, h + .6), (0, 0, ang), .03)
    box(ferro, (c + Vector((0, 0, h + .35))).to_tuple(), (w + 1, .9, .7), (0, 0, ang), .03)
    z0 = h*aberto
    n = int(w/.32)
    for i in range(n + 1):
        p = c + t*(-w/2 + w*i/n)
        along(ferro, (p + Vector((0, 0, z0))).to_tuple(), (p + Vector((0, 0, h + .1))).to_tuple(), .035, verts=6)
    for z in (z0 + .2, (z0 + h)/2, h - .1):
        if z < h: along(ferro, (c - t*w/2 + Vector((0, 0, z))).to_tuple(), (c + t*w/2 + Vector((0, 0, z))).to_tuple(), .03, verts=6)
    if z0 > .3:  # pontas da grade levantada
        for i in range(n + 1):
            p = c + t*(-w/2 + w*i/n); cyl(ferro, (p + Vector((0, 0, z0 - .08))).to_tuple(), .04, .16, r2=0, verts=6)
    return c, t, nrm, ang
c, t, nrm, ang = portao(125, 4.0, 3.2, .45)
for k, dx in enumerate((-1.1, .2, 1.3)):  # leões esperando no escuro: só os olhos
    p = c + t*dx + nrm*1.1 + Vector((0, 0, .9 + .1*k))
    for s in (-1, 1): sphere(olho, (p + t*.09*s).to_tuple(), (.03, .03, .02), segs=8)
c, t, nrm, ang = portao(48, 6.0, 4.6, 0)
# guincho de corrente do Portão do Gigante
g = c + Vector((0, 0, 5.4)) + nrm*.2
cyl(ferro, g.to_tuple(), .9, .35, (90, 0, ang), 20)
for i in range(8):
    a_ = 2*math.pi*i/8
    along(ferro, g.to_tuple(), (g + t*.85*math.cos(a_) + Vector((0, 0, .85*math.sin(a_)))).to_tuple(), .04)
for s in (-1, 1):
    chain(ferro, (g + t*s*.8).to_tuple(), (c + t*s*2.6 + Vector((0, 0, 3.6))).to_tuple(), 12, .07)
portao(315, 4.0, 2.4, 1.0)
# braseiros (holofotes mortos virados braseiro) no muro e na mureta
for a in list(range(FAR[0] + 12, FAR[1], 26)) + [285, 340]:
    if any(ang_in(a, *g) for g in gaps): continue
    zt = 3.0 if ang_in(a, *FAR) else 1.1
    p = oval(a, RX - .3, zt)
    along(ferro, p.to_tuple(), (p + Vector((0, 0, 1.0))).to_tuple(), .06)
    cyl(ferro, (p + Vector((0, 0, 1.1))).to_tuple(), .35, .3, verts=14, r2=.22)
    flame((p.x, p.y, p.z + 1.2), 1.4)

# ---------------------------------------------------------------- arquibancadas e plateia
STEPS = 8
for k in range(STEPS):
    ri = RX + .7 + k*.95; z1 = 3.0 + .6*(k + 1)
    band(f"degrau{k}", concreto if k % 2 else concreto2, ri, ri + .95, 0, z1, FAR[0], FAR[1])
# as pontas da arquibancada somem debaixo de rampas de areia (o estádio está enterrado)
for a0, sgn in ((FAR[0], -1), (FAR[1], 1)):
    lo, hi = (a0 - 16, a0 + 3) if sgn < 0 else (a0 - 3, a0 + 16)
    w_ = band(f"duna{a0}", mat_sand_obj(), RX + .2, RX + .7 + STEPS*.95 + 3, 0, 1, lo, hi, seg=24)
    for v in w_.data.vertices:
        if v.co.z <= 0: continue
        a = math.degrees(math.atan2(v.co.y*RX/RY, v.co.x)) % 360
        d = ((a - a0)*sgn) % 360
        d = d if d < 180 else d - 360
        u = max(0, min(1, (d + 3)/19)); r = Vector((v.co.x, v.co.y*RX/RY, 0)).length
        top = 3.0 + .6*STEPS + .4
        v.co.z = (top*(1 - u) + .4*u) * min(1, .55 + (r - RX)/(STEPS*.95 + 2))
    displace(w_, 1.1, 2.6, int(a0), 3)
# areia invadindo as pontas da arquibancada e a rampa desabada do lado de cá
rampa = band("rampa", mat_sand_obj(), RX + .5, RX + 34, -.1, .05, FAR[1] + 8, FAR[0] + 352)
bpy.context.view_layer.objects.active = rampa
for v in rampa.data.vertices:  # sobe devagar para fora (15°), para não tapar o fosso
    r = Vector((v.co.x, v.co.y*RX/RY, 0)).length
    if v.co.z > 0: v.co.z = 1.1 + (r - RX - .5)*.2
displace(rampa, .35, 1.6, 7, 2)
# o placar com o camarote do ogro (lado esquerdo do fundo)
pa = 196; pc = oval(pa, RX + .7 + STEPS*.95 + .6, 0); pr = Vector((pc.x, pc.y, 0)).normalized()
pt = Vector((-pr.y, pr.x, 0)); pang = math.degrees(math.atan2(pt.y, pt.x))
for s in (-1, 1): box(ferro, (pc + pt*s*3.6 + Vector((0, 0, 4.5))).to_tuple(), (.5, .5, 9), (0, 0, pang), .02)
placa = box(ferro, (pc + Vector((0, 0, 10.2))).to_tuple(), (8.6, .5, 3.6), (0, 0, pang), .04)
box(escuro, (pc - pr*.27 + Vector((0, 0, 10.4))).to_tuple(), (7.8, .05, 2.6), (0, 0, pang), 0)
numeros = mat_emit("placar_lampadas", (1, .5, .16), 1.6)
for txt, off in (("0", -2.2), ("x", 0), ("0", 2.2)):
    bpy.ops.object.text_add(location=(pc - pr*.32 + pt*off + Vector((0, 0, 9.6))).to_tuple())
    tx = bpy.context.object; tx.data.body = txt; tx.data.size = 2.0 if txt != "x" else 1.2; tx.data.extrude = .03
    tx.data.align_x = 'CENTER'; tx.rotation_euler = (math.radians(90), 0, math.radians(pang + 180)); obj(tx, numeros)
# camarote: plataforma, parapeito, o ogro narrador, dois braseiros
cp = pc - pr*1.6 + Vector((0, 0, 7.6))
box(concreto2, cp.to_tuple(), (6, 2.6, .4), (0, 0, pang), .03)
for i in range(13):
    q = cp - pr*1.25 + pt*(-3 + .5*i)
    along(ferro, (q + Vector((0, 0, .2))).to_tuple(), (q + Vector((0, 0, 1.1))).to_tuple(), .03, verts=6)
along(latao, (cp - pr*1.25 - pt*3 + Vector((0, 0, 1.1))).to_tuple(), (cp - pr*1.25 + pt*3 + Vector((0, 0, 1.1))).to_tuple(), .04)
q = cp + Vector((0, 0, .2)) - pr*.3   # o ogro de duas cabeças: Caim (megafone) e Abel (cartola com vela)
ogro = mat_solid("pele_ogro", (.17, .17, .11), 0, .6)
cyl(mat_cloth("casaca", (.3, .05, .03), seed=3), (q + Vector((0, 0, 1.0))).to_tuple(), .62, 2.0, verts=14, r2=.42)
sphere(ogro, (q + Vector((0, 0, 1.15)) - pr*.25).to_tuple(), (.5, .5, .45))
for s_ in (-1, 1):
    along(ogro, (q + pt*.55*s_ + Vector((0, 0, 1.85))).to_tuple(), (q + pt*.95*s_ - pr*.3 + Vector((0, 0, .9))).to_tuple(), .14, .11)
hc = q + pt*.22 + Vector((0, 0, 2.3)); ha = q - pt*.3 + Vector((0, 0, 2.18))
sphere(ogro, hc.to_tuple(), (.28, .28, .3)); sphere(ogro, ha.to_tuple(), (.2, .2, .22))
along(latao, (hc - pr*.18 - Vector((0, 0, .06))).to_tuple(), (hc - pr*.8).to_tuple(), .07, .26, verts=14)
cyl(mat_solid("cartola", (.02, .02, .022), 0, .6), (ha + Vector((0, 0, .32))).to_tuple(), .13, .34, verts=14)
cyl(mat_solid("cartola", (.02, .02, .022), 0, .6), (ha + Vector((0, 0, .17))).to_tuple(), .24, .03, verts=18)
along(madeira, (q - pt*.9 + Vector((0, 0, .9))).to_tuple(), (q - pt*1.1 - pr*.3 + Vector((0, 0, 3.2))).to_tuple(), .035)
candle((ha.x, ha.y, ha.z + .49), .08)
for s in (-1, 1):
    b_ = cp + pt*s*2.6 - pr*.8 + Vector((0, 0, .2))
    cyl(ferro, (b_ + Vector((0, 0, .4))).to_tuple(), .3, .25, verts=12, r2=.2); flame((b_.x, b_.y, b_.z + .55), 1.2)
# marquise quebrada sobre o fundo: lajes inclinadas em pilares, com ferragem exposta
for a in range(70, 175, 14):
    if rnd.random() < .25: continue
    pb = oval(a, RX + .7 + STEPS*.95 - .2, 0); pr2 = Vector((pb.x, pb.y, 0)).normalized()
    along(concreto2, pb.to_tuple(), (pb + Vector((0, 0, 11.5))).to_tuple(), .3, verts=8)
    if rnd.random() < .75:
        L_ = rnd.uniform(4, 7.5)
        s_ = box(concreto, (pb - pr2*L_/2 + Vector((0, 0, 11.6 - L_*.12))).to_tuple(), (L_, 4.6, .35),
                 (0, -7 if pr2.x > 0 else 7, math.degrees(math.atan2(pr2.y, pr2.x))), .02)
        crumble(s_, .12, a)
        for r_ in range(4):
            e = pb - pr2*L_ + Vector((0, 0, 11.6 - L_*.25)) + Vector((-pr2.y, pr2.x, 0))*rnd.uniform(-2, 2)
            along(ferro, e.to_tuple(), (e - pr2*rnd.uniform(.6, 1.4) + Vector((0, 0, rnd.uniform(-.8, .3)))).to_tuple(), .02, verts=5)
# faixas de campeão penduradas no muro
for a in (95, 160, 230):
    p = oval(a, RX - .05, 2.9); n_ = Vector((p.x, p.y, 0)).normalized()
    box(faixa, (p - n_*.02 + Vector((0, 0, -1.0))).to_tuple(), (1.6, .03, 2.0), (0, 0, math.degrees(math.atan2(-n_.x, n_.y))), 0)

# plateia: protótipos (capuz, braços erguidos, lanterna) duplicados com a mesma malha
def proto(kind, m):
    objs = [cyl(m, (0, 0, .5), .22, 1.0, verts=8, r2=.12)]
    objs.append(sphere(m, (0, 0, 1.08), (.13, .13, .15), segs=8))
    if kind == "bracos":
        for s in (-1, 1): objs.append(along(m, (.15*s, 0, .85), (.28*s, -.05, 1.5), .045, verts=5))
    if kind == "lanterna":
        objs.append(along(madeira, (.18, 0, .6), (.25, -.1, 1.45), .02, verts=4)); objs.append(sphere(lanterna, (.25, -.1, 1.5), (.07, .07, .09), segs=8))
    o = join(objs, f"proto_{kind}_{m.name}"); o.location = (0, -60, -60); return o
protos = [proto(k, m) for m in panos for k in ("sentado", "sentado", "sentado", "bracos", "bracos", "sentado", "sentado", "lanterna")]
def gente(p, face):
    pr_ = protos[rnd.randrange(len(protos))]
    o = pr_.copy(); sc.collection.objects.link(o)
    o.location = p; o.rotation_euler = (0, 0, face + rnd.uniform(-.4, .4)); s_ = rnd.uniform(.85, 1.05); o.scale = (s_, s_, s_*rnd.uniform(.85, 1.1))
for k in range(STEPS):
    r = RX + .7 + k*.95 + .45; z = 3.0 + .6*(k + 1)
    a = FAR[0] + 2*k + 3
    while a < FAR[1] - 2*k - 3:
        p = oval(a, r, z)
        if rnd.random() < .78 and not (190 < a < 220 and k > 3):
            gente(p.to_tuple(), math.atan2(-p.y, -p.x) + math.pi/2)
        a += math.degrees(.7/r)*rnd.uniform(.8, 1.25)
for i in range(170):  # gente sentada na rampa de areia do lado de cá
    a = rnd.uniform(FAR[1] + 15, FAR[0] + 345); r = RX + rnd.uniform(1.5, 9)
    p = oval(a, r); z = 1.1 + (r - RX - .5)*.2
    gente((p.x, p.y, z - .1), math.atan2(-p.y, -p.x) + math.pi/2)

# ---------------------------------------------------------------- render + posições de tela para os sprites
bpy.context.view_layer.update()
pts = {"centro": (0, 0, 0), "golias": (6.6, 6.8, 0)}
for i, (x, y) in enumerate(((-1.6, 1.2), (-.4, 2.2), (1.4, 2.0), (-2.2, -.6), (-1.0, -2.0), (.6, -2.6))):
    pts[f"g{i}"] = (x, y, 0)
scr = {}
for k, v in pts.items():
    c_ = world_to_camera_view(sc, cam, Vector(v)); scr[k] = (c_.x*W, (1 - c_.y)*H)
json.dump({"px_por_m": PXM, "pontos": scr}, open(os.path.splitext(OUT)[0] + "_pontos.json", "w"), indent=1)
sc.render.filepath = OUT
bpy.ops.render.render(write_still=True)
