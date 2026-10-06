# Larva de Carne (Cripta da Trombeta Calada, andar 1): verme gordo de carne morta do tamanho de um cão
# grande, nascido das pilhas de corpos do porão do Abatedouro Carniça. Segmentado, pele de defunto
# pálida e roxa, pedaços de pano de mortalha e pregos de caixão presos na carne, boca circular de lampreia
# (4 lábios que abrem, anéis de dentes). Anda em bando, encosta no jogador, incha e estoura.
# Brilho: veias por dentro da pele (laranja de brasa) que acendem quando ela incha (chave de pose "glow").
# Variante elite larva_de_carne_mae: maior, mais roxa, quatro larvinhas presas nas costas que se mexem.
#
# Rig próprio (XRig, reaproveitado por outros módulos da cripta): cadeia de ossos na linha da barriga
# (mid -> f1 -> f2 para a frente, b1 -> b2 -> b3 para trás, na linha central do corpo) e um osso-folha "s_*" igual a cada um, que
# deforma a malha. Chaves de spec por osso além de x/y/z/bend:
#   "inf": incha (escala 1+inf em x e z do osso-folha), "sx"/"sy"/"sz": soma na escala de cada eixo,
#   "vis": escala uniforme (0 = escondido; ossos em R.hidden começam escondidos), "lx"/"ly"/"lz": desloca
#   um osso sem pai (pedaços que voam no estouro). Pseudo-osso "glow": {"v": 0..1} acende as veias.
# Tudo isso é número dentro de dict, então merge/lerp_pose/keys_to_frames interpolam normalmente.
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *
from quad import ring_path, surf, loft, join

INFO = {"px": 192, "target_z": .3, "rim": (.95, .55, .38), "colors": 40, "samples": 48,
        "fps": {"idle": 6, "walk": 10, "attack": 12, "hit": 12, "death": 12},
        "loops": ("idle", "walk")}

VARIANTS = {
    "larva_de_carne": {"scale": 1.25},
    # elite: mãe do bando, maior e mais roxa, com larvinhas agarradas nas costas
    "larva_de_carne_mae": {"scale": 1.55, "mother": True, "skin": (.25, .17, .17), "px": 256, "tz": .42,
                           "rim": (1, .5, .35)},
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
    if "rim" in V: INFO["rim"] = V["rim"]
    if "px" in V: INFO["px"] = V["px"]
    if "tz" in V: INFO["target_z"] = V["tz"]
set_variant("larva_de_carne")

# ======================================================================= rig com escala, deslocamento e brilho
class XRig(Rig):
    def __init__(self, *a, **k):
        Rig.__init__(self, *a, **k)
        self.hidden = set(); self.glow = []   # glow: [(socket, fator)]
        self.lamps = []                        # lamps: [(luz, energia)]; pose "lamp": {"v": 0..1} (padrão 1)

    def set_pose(self, pose, frame):
        Rig.set_pose(self, pose, frame)
        arm = self.arm
        for pb in arm.pose.bones:
            sp = pose.get(pb.name, {})
            keys = set(sp) & {"inf", "sx", "sy", "sz", "vis"}
            if not keys and pb.name not in self.hidden: continue
            base = pb.scale[0]
            if "vis" in sp: base = sp["vis"]
            elif pb.name in self.hidden: base = 0
            i = sp.get("inf", 0)
            s = [base*(1 + i + sp.get("sx", 0)), base*(1 + .25*i + sp.get("sy", 0)), base*(1 + i + sp.get("sz", 0))]
            pb.scale = [max(.001, v) for v in s]
            pb.keyframe_insert("scale", frame=frame)
        for pb in arm.pose.bones:
            if pb.parent or pb.name == self.root: continue
            sp = pose.get(pb.name, {})
            off = Vector((sp.get("lx", 0), sp.get("ly", 0), sp.get("lz", 0)))
            RB = pb.bone.matrix_local.to_quaternion()
            pb.location = RB.inverted() @ off
            pb.keyframe_insert("location", frame=frame)
        g = pose.get("glow", {}).get("v", 0)
        for sock, k in self.glow:
            sock.default_value = g*k
            sock.keyframe_insert("default_value", frame=frame)
        lv = pose.get("lamp", {}).get("v", 1)
        for ld, en in self.lamps:
            ld.energy = en*max(0, lv)
            ld.keyframe_insert("energy", frame=frame)

    def action(self, name, frames):
        ids = {s.node.id_data for s, _ in self.glow} | {ld for ld, _ in self.lamps}
        for m in ids:
            m.animation_data_clear()
        act = Rig.action(self, name, frames)
        for m in ids:
            if m.animation_data and m.animation_data.action:
                for fc in m.animation_data.action.fcurves:
                    for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'
        return act

def glow_veins(m, color, scale=3.0, base=.18, width=.035):
    """Põe veias emissivas (ruído em faixa estreita) num material; devolve o socket da força."""
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = [n for n in nt.nodes if n.type == 'TEX_COORD'][0]
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale
    nz.inputs["Detail"].default_value = 3; nz.inputs["Distortion"].default_value = 2.5
    nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    r = nt.nodes.new("ShaderNodeValToRGB"); cr = r.color_ramp
    cr.elements[0].position = .5 - width; cr.elements[0].color = (base, base, base, 1)
    cr.elements[1].position = .5 + width; cr.elements[1].color = (base, base, base, 1)
    e = cr.elements.new(.5); e.color = (1, 1, 1, 1)
    nt.links.new(nz.outputs["Fac"], r.inputs[0])
    mx = nt.nodes.new("ShaderNodeMix"); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs[0].default_value = 1
    nt.links.new(r.outputs[0], mx.inputs[6]); mx.inputs[7].default_value = (*color, 1)
    nt.links.new(mx.outputs[2], b.inputs["Emission Color"])
    s = b.inputs["Emission Strength"]; s.default_value = 0
    return s

# ======================================================================= esqueleto
Z0 = .29   # linha central do corpo (ossos da cadeia; trava no chão: a cadeia mais baixa fica em Z0)
BELLY = .28  # raio vertical do corpo (barriga a Z0 - BELLY do chão)
def gz(f): return .012 + BELLY*f   # trava para a escala vertical f (inchado/murcho): a barriga continua no chão
CHAIN = {"mid": (.05, -.2, None), "f1": (-.2, -.45, "mid"), "f2": (-.45, -.7, "f1"),
         "b1": (.05, .3, "mid"), "b2": (.3, .55, "b1"), "b3": (.55, .82, "b2")}
SEGS = list(CHAIN)
def bones():
    B = {}
    for n, (y0, y1, p) in CHAIN.items():
        B[n] = ((0, y0, Z0), (0, y1, Z0), p)
    for n, (y0, y1, p) in CHAIN.items():
        B["s_" + n] = ((0, y0, Z0 + .001), (0, y1, Z0 + .001), n)
    # lábios da boca (abrem para fora)
    c = Vector((0, -.71, .27))
    for nm, d in (("lip_u", (0, 0, 1)), ("lip_d", (0, 0, -1)), ("lip.L", (1, 0, 0)), ("lip.R", (-1, 0, 0))):
        h = c + Vector(d)*.13
        B[nm] = (tuple(h), tuple(h + Vector((0, -.08, 0))), "f2")
    # pedaços do estouro (sem pai) e a poça
    for i, (x, y) in enumerate(CHUNKS):
        B[f"k{i}"] = ((x, y, 0), (x, y, .1), None)
    B["pool"] = ((0, .02, 0), (0, .02, .1), None)
    B["rip"] = ((0, .0, Z0), (0, -.2, Z0), "mid")
    if V.get("mother"):
        for i, (bn, y, x, a) in enumerate(KIDS):
            h = Vector((x, y, .55)); d = Vector((math.sin(math.radians(a)), -math.cos(math.radians(a)), .25)).normalized()
            B[f"kid{i}"] = (tuple(h), tuple(h + d*.12), bn)
    return B

CHUNKS = [(.55, -.25), (-.5, -.35), (.35, .45), (-.42, .4), (.05, -.75), (.75, .15), (-.7, .02), (.12, .7)]
KIDS = [("b1", .2, .1, 30), ("mid", -.08, -.12, -40), ("b2", .45, -.06, 160), ("f1", -.32, .09, -10)]

# ======================================================================= modelo
def body_keys(k=1.0):
    return [(.86, .14, .03, .03), (.8, .17, .1*k, .09*k), (.67, .22, .19*k, .17*k), (.47, .27, .26*k, .24*k),
            (.22, .3, .31*k, .28*k), (-.05, .31, .33*k, .29*k), (-.3, .3, .32*k, .28*k), (-.5, .29, .28*k, .25*k),
            (-.64, .275, .23*k, .21*k), (-.71, .27, .19*k, .18*k), (-.725, .27, .1*k, .09*k)]

def build():
    rnd = random.Random(5)
    M = V.get("mother")
    skin = stained("lv_pele" + V["name"], V.get("skin", (.31, .26, .2)), stain=(.2, .03, .02), amount=.3, scale=2.2,
                   rough=.42, blotch=(.15, .08, .11), blotch_amt=.75, grime=.6, dirt=.45)
    crease = stained("lv_dobra", (.12, .04, .045), stain=(.05, .01, .01), amount=.3, scale=6, rough=.4, grime=.2)
    gum = stained("lv_gengiva", (.36, .07, .07), stain=(.1, .01, .01), amount=.4, scale=8, rough=.25, grime=0)
    tooth = stained("lv_dente", (.42, .37, .26), stain=(.15, .05, .02), amount=.35, scale=9, rough=.45, grime=0)
    dark = mat("lv_garganta", (.02, .005, .005), 0, .5)
    cloth = stained("lv_mortalha", (.26, .23, .17), stain=(.22, .03, .015), amount=.75, scale=3.5, rough=.95,
                    blotch=(.09, .07, .05), blotch_amt=.85, grime=.6, dirt=.4)
    bonec = stained("lv_osso", (.4, .35, .26), stain=(.18, .03, .02), amount=.4, scale=7, rough=.5, grime=0,
                    blotch=(.2, .17, .14), blotch_amt=.5)
    iron = stained("lv_prego", (.08, .065, .055), stain=(.3, .1, .035), amount=.6, scale=9, metal=.75, rough=.55, grime=0)
    blood = stained("lv_sangue", (.13, .012, .01), stain=(.05, .005, .005), amount=.4, scale=5, rough=.12, grime=0)
    meat = stained("lv_carne", (.3, .05, .045), stain=(.1, .08, .06), amount=.35, scale=6, rough=.25, grime=0)
    spiracle = mat("lv_furo", (.04, .01, .01), 0, .4, dirt=.6)
    glow_s = glow_veins(skin, (1, .36, .07), scale=2.6, base=.04, width=.022)

    R = XRig("larva", bones(), ground=Z0, ground_bones=SEGS)
    R.glow.append((glow_s, 3.5))
    R.hidden = {f"k{i}" for i in range(len(CHUNKS))} | {"pool", "rip"}
    P = R.P

    # ---- corpo segmentado (loft com dobras entre segmentos, barriga achatada)
    rings = ring_path(body_keys(), .01)
    SEGL = .16
    def rad(i, a, r):
        y = r[0].y; f = 1.0
        if -.68 < y < .78:
            ph = ((y + .7)/SEGL) % 1
            f *= 1 - .12*math.exp(-((ph - .5)/.08)**2)          # dobra entre segmentos
            f *= 1 + .025*math.sin(ph*math.pi)                   # cada anel abaulado
        f *= 1 + .035*math.sin(a*3 + y*23) + .025*math.sin(a*5 - y*41 + 1)   # carne irregular
        sn = math.sin(a)
        if sn < -.3: f *= 1 - .14*(-sn - .3)                      # barriga achatada
        return f
    body = loft("larva_corpo", rings, skin, seg=36, rad=rad)
    parts = [body]
    # dobras escuras (anéis finos afundados) para marcar os segmentos
    for k in range(9):
        y = -.7 + SEGL*(k + .5)
        ri = min(range(len(rings)), key=lambda i: abs(rings[i][0].y - y)); c, rx, rz, t = rings[ri]
        o = prim("primitive_torus_add", crease, c, (rx*.93, 1, rz*.93), major_radius=1, minor_radius=.012,
                 major_segments=32, minor_segments=4, rot=(90, 0, 0))
        o.scale = (rx*.93, rz*.93, 1); parts.append(o)
    def ring_at(y): return rings[min(range(len(rings)), key=lambda i: abs(rings[i][0].y - y))]
    # pezinhos de carne (falsas patas) na barriga e espiráculos nas laterais
    for k in range(8):
        y = -.58 + SEGL*k
        for s in (1, -1):
            p, n = surf(ring_at(y), math.radians(-90 + 52*s))
            o = prim("primitive_uv_sphere_add", skin, p + n*.005 + Vector((0, 0, -.01)), (.05, .045, .035), segments=10, ring_count=6)
            o.rotation_euler = n.to_track_quat('Z', 'Y').to_euler(); parts.append(o)
            if k % 2 == 0 and k < 7:
                p, n = surf(ring_at(y + .04), math.radians(15 if s > 0 else 165))
                o = prim("primitive_uv_sphere_add", spiracle, p, (.018, .018, .008), segments=8, ring_count=5)
                o.rotation_euler = n.to_track_quat('Z', 'Y').to_euler(); parts.append(o)
    # pregos de caixão cravados (grossos, alguns tortos), com mancha de ferrugem e sangue em volta
    for k in range(8 if not M else 11):
        y = -.5 + 1.08*(k + rnd.uniform(-.3, .3))/(8 if not M else 11); a = math.radians(rnd.uniform(25, 155))
        p, n = surf(ring_at(y), a)
        d = (n + Vector((rnd.uniform(-.45, .45), rnd.uniform(-.45, .45), .15))).normalized()
        L = rnd.uniform(.1, .17)
        if k % 3 == 2:   # torto
            m = p + d*L*.55; d2 = (d + Vector((rnd.choice((-1, 1))*.9, 0, -.4))).normalized()
            parts.append(along("primitive_cylinder_add", iron, p - d*.03, m, .012, vertices=6))
            parts.append(along("primitive_cylinder_add", iron, m, m + d2*L*.5, .012, vertices=6)); tip = m + d2*L*.5; dd = d2
        else:
            parts.append(along("primitive_cone_add", iron, p - d*.03, p + d*L, .014, vertices=6, radius1=.7, radius2=1))
            tip = p + d*L; dd = d
        hd = prim("primitive_cylinder_add", iron, tip, (.028, .028, .008), vertices=8)
        hd.rotation_euler = dd.to_track_quat('Z', 'Y').to_euler(); parts.append(hd)
        w = prim("primitive_uv_sphere_add", blood, p + n*.002, (.045, .04, .007), segments=8, ring_count=5)
        w.rotation_euler = n.to_track_quat('Z', 'Y').to_euler(); parts.append(w)
    # tumores e bolhas de gordura, feridas abertas em carne viva
    for k in range(10):
        y = rnd.uniform(-.5, .6); a = math.radians(rnd.uniform(-20, 200))
        p, n = surf(ring_at(y), a); sc = rnd.uniform(.035, .07)
        o = prim("primitive_uv_sphere_add", skin, p, (sc, sc*.9, sc*.7), segments=10, ring_count=6)
        o.rotation_euler = n.to_track_quat('Z', 'Y').to_euler(); parts.append(o)
    for k in range(5):
        y = rnd.uniform(-.45, .55); a = math.radians(rnd.uniform(10, 170))
        p, n = surf(ring_at(y), a); sc = rnd.uniform(.04, .07)
        o = prim("primitive_uv_sphere_add", meat, p + n*.004, (sc, sc*.7, .012), segments=10, ring_count=5)
        o.rotation_euler = n.to_track_quat('Z', 'Y').to_euler(); parts.append(o)
    # o que ela comeu: uma mão de defunto saindo do flanco e costelas espetadas no dorso
    p, n = surf(ring_at(.12), math.radians(-5))
    wr = p + n*.09 + Vector((0, .02, .03)); hand = [along("primitive_cylinder_add", bonec, p - n*.03, wr, .028, vertices=8)]
    hand.append(prim("primitive_uv_sphere_add", bonec, wr + n*.03, (.045, .03, .05), segments=10, ring_count=6))
    for f in range(4):
        b0 = wr + n*.055 + Vector((0, -.03 + .02*f, .01)); b1 = b0 + n*.05 + Vector((0, 0, -.03))
        hand.append(along("primitive_cylinder_add", bonec, b0, b1, .009, vertices=5))
        hand.append(along("primitive_cone_add", bonec, b1, b1 + Vector((0, 0, -.045)) - n*.01, .008, vertices=5, radius1=1, radius2=.4))
    hand.append(along("primitive_cylinder_add", bonec, wr + n*.03 + Vector((0, -.04, 0)), wr + n*.05 + Vector((0, -.07, .04)), .01, vertices=5))
    parts += hand
    for k, (y, a) in enumerate(((-.3, 70), (-.24, 78), (.48, 115))):
        p, n = surf(ring_at(y), math.radians(a))
        d = (n + Vector((0, .5, .3))).normalized()
        parts.append(along("primitive_cone_add", bonec, p - n*.02, p + d*.16 + Vector((0, 0, -.03)), .016, vertices=6, radius1=1, radius2=.35))
    # pedaços de mortalha grudados: faixas furadas com tiras penduradas
    def sheet(y0, y1, a0, a1, off, jag, seed, drop=0.0, holes=.15):
        rr = random.Random(seed); bm = bmesh.new(); g = []
        ny, na = 7, 14
        for iy in range(ny + 1):
            y = y0 + (y1 - y0)*iy/ny; row = []
            for ia in range(na + 1):
                a = math.radians(a0 + (a1 - a0)*ia/na)
                p, n = surf(ring_at(y), a); p = p + n*(off + rr.uniform(0, .006))
                if iy in (0, ny): p = p + Vector((0, (1 if iy else -1)*rr.uniform(-jag*.3, jag), 0))
                row.append(bm.verts.new(p))
            g.append(row)
        for iy in range(ny):
            for ia in range(na):
                if rr.random() < holes and 0 < iy < ny-1: continue
                bm.faces.new((g[iy][ia], g[iy][ia+1], g[iy+1][ia+1], g[iy+1][ia]))
        # tiras rasgadas penduradas nas pontas da faixa
        for ia_end, sgn in ((0, 1), (na, -1)):
            for iy in range(0, ny, 2):
                v0, v1 = g[iy][ia_end], g[iy+1][ia_end]; L = drop + rr.uniform(0, jag*2)
                lo0 = bm.verts.new(v0.co + Vector((0, rr.uniform(-.02, .02), -L))); lo1 = bm.verts.new(v1.co + Vector((0, 0, -L*.8)))
                bm.faces.new((v0, v1, lo1, lo0))
        bm.verts.ensure_lookup_table()
        for v in [v for v in bm.verts if not v.link_faces]: bm.verts.remove(v)
        o = obj_from_bm("mortalha", bm, cloth); sd = o.modifiers.new("s", 'SOLIDIFY'); sd.thickness = .008; apply_mods(o)
        return o
    parts.append(sheet(-.22, .02, 5, 175, .012, .04, 1, drop=.06))
    parts.append(sheet(.3, .46, 35, 150, .01, .04, 2, drop=.05))
    if M: parts.append(sheet(-.52, -.38, 10, 120, .012, .04, 3, drop=.05))
    bodyo = join(parts)
    R.bind(bodyo, ["s_" + n for n in SEGS], power=4)

    # ---- boca de lampreia: garganta, gengiva, anéis de dentes (presos à cabeça) e 4 lábios com dentes
    c = Vector((0, -.715, .27)); mo = []
    mo.append(prim("primitive_uv_sphere_add", dark, c + Vector((0, .02, 0)), (.115, .04, .105), segments=16, ring_count=8))
    mo.append(prim("primitive_torus_add", gum, c, (1, 1, .92), major_radius=.12, minor_radius=.03, major_segments=24,
                   minor_segments=6, rot=(90, 0, 0)))
    for ring, (r0, n, L) in enumerate(((.1, 14, .05), (.065, 10, .035))):
        for k in range(n):
            a = 2*math.pi*(k + .5*ring)/n; dv = Vector((math.cos(a), 0, math.sin(a)))
            base = c + dv*r0 + Vector((0, .01 + .025*ring, 0))
            mo.append(along("primitive_cone_add", tooth, base, base - dv*L + Vector((0, -.02, 0)), .011 - .003*ring,
                            vertices=5, radius1=1, radius2=0))
    R.rigid(mo, "f2")
    for nm in ("lip_u", "lip_d", "lip.L", "lip.R"):
        h, t = P(nm), P(nm, 1); out = (h - c).normalized()
        lp = [prim("primitive_uv_sphere_add", skin, h + Vector((0, -.03, 0)) - out*.01, (1, 1, 1), segments=14, ring_count=8)]
        lp[0].scale = (.1 if abs(out.z) > .5 else .055, .09, .055 if abs(out.z) > .5 else .1)
        lp.append(prim("primitive_uv_sphere_add", gum, h + Vector((0, -.06, 0)) - out*.035, (1, 1, 1), segments=10, ring_count=6))
        lp[-1].scale = (.05 if abs(out.z) > .5 else .02, .03, .02 if abs(out.z) > .5 else .05)
        side = Vector((1, 0, 0)) if abs(out.z) > .5 else Vector((0, 0, 1))
        for k in range(4):  # dentes do lábio, curvados para dentro
            b0 = h + Vector((0, -.09, 0)) - out*.03 + side*(-.06 + .04*k)
            lp.append(along("primitive_cone_add", tooth, b0, b0 - out*.09 + Vector((0, -.03, 0)), .015, vertices=5,
                            radius1=1, radius2=0))
        R.rigid(lp, nm)

    # ---- pedaços que voam no estouro (escondidos), poça de sangue, rasgo aberto no dorso
    for i, (x, y) in enumerate(CHUNKS):
        base = Vector((x, y, 0)); ch = []
        if i % 3 == 0:   # pedaço de pele com pano grudado
            s = rnd.uniform(.09, .13)
            o = prim("primitive_uv_sphere_add", skin, base + Vector((0, 0, .025)), (s, s*.8, .03), segments=12, ring_count=6)
            o.rotation_euler = (0, 0, rnd.uniform(0, 3)); ch.append(o)
            ch.append(prim("primitive_cube_add", cloth, base + Vector((.02, .01, .055)), (s*.7, s*.5, .006), rot=(0, 0, rnd.uniform(0, 90))))
        elif i % 3 == 1:  # nacos de carne crua com dentes/pregos
            for j in range(3):
                s = rnd.uniform(.035, .06)
                ch.append(prim("primitive_uv_sphere_add", meat, base + Vector((rnd.uniform(-.05, .05), rnd.uniform(-.05, .05), s*.6)),
                               (s, s*.85, s*.7), segments=10, ring_count=6))
            ch.append(along("primitive_cylinder_add", iron, base + Vector((0, 0, .03)), base + Vector((.06, .05, .07)), .007, vertices=6))
        else:            # pedaço de pele inchada virado, com a gordura por dentro
            s = rnd.uniform(.08, .11)
            ch.append(prim("primitive_uv_sphere_add", skin, base + Vector((0, 0, .03)), (s, s*.7, .045), segments=12, ring_count=6))
            ch.append(prim("primitive_uv_sphere_add", meat, base + Vector((0, 0, .06)), (s*.7, s*.5, .02), segments=10, ring_count=5))
        R.rigid(ch, f"k{i}")
    pool = []
    for j in range(9):
        a = rnd.uniform(0, 2*math.pi); r = rnd.uniform(0, .45) if j else 0
        s = rnd.uniform(.25, .4) if j < 4 else rnd.uniform(.08, .16)
        pool.append(prim("primitive_uv_sphere_add", blood, (r*math.cos(a)*1.3, .02 + r*math.sin(a), .002), (s*1.2, s, .006),
                         segments=16, ring_count=6))
    for p_ in pool: p_.visible_shadow = False
    R.rigid(pool, "pool").visible_shadow = False
    rip = [prim("primitive_uv_sphere_add", meat, (0, -.08, .38), (.2, .3, .05), segments=16, ring_count=8),
           prim("primitive_uv_sphere_add", dark, (0, -.08, .395), (.12, .2, .03), segments=14, ring_count=6)]
    for k in range(10):   # abas de pele rasgada em volta do buraco
        a = 2*math.pi*k/10; p = Vector((.2*math.cos(a), -.08 + .29*math.sin(a), .38))
        rip.append(along("primitive_cone_add", skin, p - Vector((0, 0, .02)), p + Vector((.1*math.cos(a), .12*math.sin(a), .07)), .06,
                         vertices=5, radius1=1, radius2=.2))
        rip[-1].scale.x *= .35
    R.rigid(rip, "rip")

    # ---- mãe: larvinhas agarradas nas costas (cada uma num osso, mexem no idle)
    if M:
        for i, (bn, y, x, a) in enumerate(KIDS):
            h, t = P(f"kid{i}"), P(f"kid{i}", 1); d = (t - h).normalized()
            ks = []
            L = .32; pts = [h - d*.06 + Vector((0, 0, -.06)), h + d*.06, h + d*.16 + Vector((0, 0, .03)), h + d*.25 + Vector((0, 0, .02))]
            j = {f"p{k}": (*p, r) for k, (p, r) in enumerate(zip(pts, (.045, .06, .055, .042)))}
            from base_rig import skin_mesh
            kb = skin_mesh(f"larvinha{i}", j, [(f"p{k}", f"p{k+1}") for k in range(3)], skin, levels=2)
            ks.append(kb)
            for k in range(3):  # dobras
                q = pts[1].lerp(pts[3], k/3)
                o = prim("primitive_torus_add", crease, q, (1, 1, 1), major_radius=.053, minor_radius=.006, major_segments=14,
                         minor_segments=4)
                o.rotation_euler = d.to_track_quat('Z', 'Y').to_euler(); ks.append(o)
            tip = pts[3] + d*.035
            ks.append(prim("primitive_uv_sphere_add", dark, tip, (.025, .025, .025), segments=8, ring_count=6))
            for k in range(6):
                aa = 2*math.pi*k/6; side = d.cross(Vector((0, 0, 1))).normalized(); up = side.cross(d)
                b0 = tip + (side*math.cos(aa) + up*math.sin(aa))*.03
                ks.append(along("primitive_cone_add", tooth, b0, b0 + d*.02 - (side*math.cos(aa) + up*math.sin(aa))*.015, .006,
                                vertices=4, radius1=1, radius2=0))
            ks.append(prim("primitive_uv_sphere_add", blood, pts[0] + Vector((0, 0, .02)), (.06, .06, .02), segments=8, ring_count=5))
            R.rigid(ks, f"kid{i}")
    R.arm.scale = [V.get("scale", 1)]*3
    return R, INFO

# ======================================================================= animações
def chain(front=(0, 0, 0), back=(0, 0, 0), side_f=(0, 0, 0), side_b=(0, 0, 0)):
    """Curva a cadeia: front/back = graus de x por osso (f1,f2 / b1,b2,b3 a partir do mid; front[0] = mid).
    x positivo abaixa a ponta da frente e levanta a de trás."""
    o = {}
    for n, v in zip(("mid", "f1", "f2"), front): o.setdefault(n, {})["x"] = v
    for n, v in zip(("b1", "b2", "b3"), back): o.setdefault(n, {})["x"] = v
    for n, v in zip(("mid", "f1", "f2"), side_f): o.setdefault(n, {})["z"] = o[n].get("z", 0) + v
    for n, v in zip(("b1", "b2", "b3"), side_b): o.setdefault(n, {})["z"] = o[n].get("z", 0) + v
    return o

def inflate(vals):
    """vals: {segmento: inf} -> spec nos ossos-folha."""
    return {"s_" + n: {"inf": v} for n, v in vals.items()}

def mouth(a):
    return {"lip_u": {"x": -a}, "lip_d": {"x": a}, "lip.L": {"z": a}, "lip.R": {"z": -a}}

def kids(t):
    o = {}
    for i in range(len(KIDS) if V.get("mother") else 0):
        o[f"kid{i}"] = {"x": -12*math.sin(t + i*1.7), "z": 18*math.sin(t*1.3 + i*2.1)}
    return o

def anims(R):
    # repouso: cabeça um pouco erguida, cauda caída
    REST = merge(chain((6, -24, -34), (0, -1, -2)), mouth(10))
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; s, c = math.sin(t), math.cos(t)
        idle.append(merge(REST, chain((0, -3*s, -4*s), (0, 2*c, 3*c), (0, 4*c, 6*c)), mouth(6 + 8*max(0, s)),
                          inflate({"mid": .03*s, "b1": .04*s, "f1": .02*s, "b2": .03*math.sin(t - 1)}), kids(t),
                          {"glow": {"v": .02}}))
    # rastejar: onda de contração da cauda para a cabeça (sobe um arco, a cabeça avança e estica)
    walk = []
    for i in range(8):
        t = i/8*2*math.pi
        ph = lambda k: math.sin(t - k*.9)
        front = (9*ph(2), -15*ph(3), -12*ph(4))
        back = (-9*ph(1), -15*ph(0), -12*ph(-1))
        sway = 7*math.sin(t)
        walk.append(merge(REST, chain(front, back, (0, sway, sway*.6), (0, -sway*.7, -sway)),
                          inflate({"mid": .07*ph(2), "f1": .07*ph(3), "b1": .07*ph(1), "b2": .07*ph(0), "b3": .05*ph(-1)}),
                          {"s_f1": {"sy": .06*ph(3)}, "s_mid": {"sy": .06*ph(2)}}, mouth(6 + 6*max(0, ph(4))), kids(t*2),
                          {"root": (0, -.03*math.cos(t), 0)}))
    # ataque: encosta e incha 0,8 s, pulsando; a pele estica e as veias acendem por dentro
    attack = []
    n = 10
    for i in range(n):
        u = i/(n - 1); grow = u**1.3; pulse = math.sin(u*math.pi*5)*(.3 + .7*u)
        inf = .05 + .5*grow + .06*pulse
        rear = 10*grow
        attack.append(merge(REST, chain((-rear*.3, -rear*.6 - 4*pulse, -rear*.4), (rear*.2, 4, 6)),
                            inflate({"mid": inf, "b1": inf*.95, "f1": inf*.8, "b2": inf*.7, "f2": inf*.35, "b3": inf*.4}),
                            mouth(10 + 30*grow + 8*pulse), kids(u*9), {"glow": {"v": .1 + .9*grow + .15*pulse}},
                            {"ground": gz(1 + inf)}))
    hitp = merge(REST, chain((-6, -14, -12), (-4, -8, -6), (0, 10, 10), (0, 6, 8)), inflate({"mid": -.06, "f1": -.05}),
                 mouth(24), {"root": (0, .06, 0)})
    hit = [hitp, lerp_pose(hitp, REST, .5), REST]
    # morte: incha num relance e estoura: o corpo murcha achatado e aberto, pedaços voam e caem em volta
    death = []
    nd = 12; burst = 4
    for i in range(nd):
        if i < burst:
            u = i/(burst - 1); inf = .08 + .55*u**1.5
            p = merge(REST, chain((-8*u, -10*u, -6*u), (4*u, 6, 8)),
                      inflate({"mid": inf, "b1": inf, "f1": inf*.85, "b2": inf*.75, "f2": inf*.4, "b3": inf*.45}),
                      mouth(14 + 30*u), {"glow": {"v": .3 + .9*u}, "ground": gz(1 + inf)})
            if i == 0: p = merge(p, chain((-4, -8, -6), (-2, -4, -4)))
        else:
            u = (i - burst)/(nd - 1 - burst); e = 1 - (1 - u)**2
            flat = {"s_" + nm: {"sx": .22 - .05*u, "sz": -.72 + .06*(1 - e), "sy": .04} for nm in SEGS}
            flat["s_f2"] = {"sx": .1, "sz": -.5, "sy": 0}
            flat["s_b3"] = {"sx": .1, "sz": -.45}
            p = merge(chain((0, 4, 10), (0, -4, -6), (0, -6, 10), (0, 8, -6)), flat, mouth(40 - 8*u),
                      {"glow": {"v": max(0, .6 - 1.2*u)}, "rip": {"vis": 1}, "pool": {"vis": .35 + .65*e},
                       "ground": gz(.28 + .06*(1 - e))})
            # pedaços: saem do centro no alto e caem rolando nas posições finais
            for k, (x, y) in enumerate(CHUNKS):
                tk = min(1, u*(1.25 + .12*(k % 3)))
                arc = 4*tk*(1 - tk)*(.45 + .1*(k % 2)) + .25*(1 - tk)**2
                p[f"k{k}"] = {"vis": 1, "lx": -x*(1 - tk)**1.5, "ly": -y*(1 - tk)**1.5, "lz": arc,
                              "x": (1 - tk)*(140 + 30*k), "y": (1 - tk)*(80 - 25*k)}
        death.append(p)
    return {"idle": idle, "walk": walk, "attack": attack, "hit": hit, "death": death}
