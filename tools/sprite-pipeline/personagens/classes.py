# Anjo (Arautos do Juízo) e Humano (Vigília) no estilo "Ferrugem Sagrada".
# Cada função recebe nada, cria armadura + malhas pesadas e devolve (arm, extras).
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from rig import *

def J():
    j = {k: P(k) for k in BONES}
    return j

def bone_frame(b, up=Vector((0, -1, 0))):
    """Referencial de um osso na pose de ligação: (origem, eixo, cima, lado)."""
    o = P(b); ax = (P(b, 1) - o).normalized()
    u = (up - ax*up.dot(ax)).normalized(); s = ax.cross(u)
    return o, ax, u, s

def L(fr, a=0, u=0, s=0):
    o, ax, uu, ss = fr; return o + ax*a + uu*u + ss*s

def body_parts(arm, m_pants, m_boot, m_top, m_glove, m_skin=None, top_r=1.0, sleeve_r=1.0, cuff=None,
               boot_top=.40, buckle=None, m_arms=None, arm_scale=None, glove_scale=None, legs_r=1.0):
    """Corpo em camadas: calça, botas, tronco com mangas, luvas. Tudo pesado nos ossos."""
    parts = []
    legs = {"pelvis": (0,0,.95,.14,.11)}
    edges = []
    for s, n in ((1,"L"),(-1,"R")):
        h, k, a, t = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}",1)
        legs[f"hip{n}"] = (*h, .088*legs_r); legs[f"knee{n}"] = (*k, .062*legs_r); legs[f"ank{n}"] = (*a, .05*legs_r)
        edges += [("pelvis", f"hip{n}"), (f"hip{n}", f"knee{n}"), (f"knee{n}", f"ank{n}")]
    o = skin_mesh("pernas", legs, edges, m_pants); bind(o, arm, ["hips","thigh.L","thigh.R","shin.L","shin.R"]); parts.append(o)
    for s, n in ((1,"L"),(-1,"R")):
        k, a, t = P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}",1)
        top = k.lerp(a, (k.z-boot_top)/(k.z-a.z))
        bj = {"top": (*top, .07), "ank": (*(a+Vector((0,.0,.0))), .062), "heel": (*(a+Vector((0,.04,-.05))), .05),
              "toe": (*(t+Vector((0,-.01,.0))), .048, .042)}
        o = skin_mesh(f"bota.{n}", bj, [("top","ank"),("ank","heel"),("ank","toe")], m_boot)
        bind(o, arm, [f"shin.{n}", f"foot.{n}"]); parts.append(o)
        # cano dobrado e tira com fivela
        cuffs = [prim("primitive_torus_add", m_boot, top + Vector((0,0,.005)), (1,1,1.3), major_radius=.072, minor_radius=.016),
                 prim("primitive_torus_add", m_boot, a.lerp(top, .45), (1,1,1), major_radius=.066, minor_radius=.008)]
        if buckle: cuffs.append(prim("primitive_cube_add", buckle, a.lerp(top, .45) + Vector((.0,-.068,0)), (.014,.006,.012)))
        parts.append(rigid(cuffs, arm, f"shin.{n}"))
    r = top_r
    tj = {"pelvis": (0,0,.97,.15*r,.115*r), "spine": (0,.0,1.13,.15*r,.11*r), "chest": (0,0,1.33,.175*r,.12*r),
          "neck": (0,-.005,1.5,.06), "neck2": (0,-.01,1.56,.05)}
    te = [("pelvis","spine"),("spine","chest"),("chest","neck"),("neck","neck2")]
    for s, n in ((1,"L"),(-1,"R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        tj[f"sh{n}"] = (*(sh+Vector((-.02*s,0,0))), .075*sleeve_r); tj[f"el{n}"] = (*el, .055*sleeve_r)
        tj[f"wr{n}"] = (*wr.lerp(el, .08), (cuff or .045)*sleeve_r)
        if not m_arms: te += [("chest", f"sh{n}"), (f"sh{n}", f"el{n}"), (f"el{n}", f"wr{n}")]
        else:
            te += [("chest", f"sh{n}")]
            k_ = (arm_scale or {}).get(n, 1.0)
            aj = {"c": (*(sh+Vector((-.06*s,0,-.02))), .07*k_), "sh": (*sh, .075*sleeve_r*k_), "el": (*el, .058*sleeve_r*k_),
                  "wr": (*wr.lerp(el, .08), (cuff or .045)*sleeve_r*k_)}
            ao = skin_mesh(f"braco.{n}", aj, [("c","sh"),("sh","el"),("el","wr")], m_arms[n])
            bind(ao, arm, ["chest", f"upper_arm.{n}", f"forearm.{n}"]); parts.append(ao)
    o = skin_mesh("tronco", tj, te, m_top)
    bind(o, arm, ["hips","spine","chest","neck","upper_arm.L","upper_arm.R","forearm.L","forearm.R"]); parts.append(o)
    for n in "LR":
        fr = bone_frame(f"hand.{n}")
        gs = (glove_scale or {}).get(n, 1.0)
        g = prim("primitive_uv_sphere_add", m_glove if not isinstance(m_glove, dict) else m_glove[n], L(fr, .045*gs), (.04*gs, .05*gs, .058*gs), segments=12, ring_count=8)
        g.rotation_euler = fr[1].to_track_quat('Z','Y').to_euler()
        c = along("primitive_cone_add", m_glove if not isinstance(m_glove, dict) else m_glove[n], L(fr, -.04), L(fr, .01), 1, radius1=.052*gs, radius2=.042*gs, vertices=12)
        parts.append(rigid([g, c], arm, f"hand.{n}"))
    return parts


def feather(bm, base, d, n, length, width, rnd, curl=.06):
    """Pena achatada (lanceolada) no plano perpendicular a n, com ponta gasta."""
    w = n.cross(d).normalized(); prof = [.25, .55, .75, .7, .5, .22, 0]
    left, right = [], []
    for i, f in enumerate(prof):
        t = i/(len(prof)-1)
        p = base + d*length*t + n*curl*t*t
        jag = rnd.uniform(-.15, .15)*width if t > .6 else 0
        left.append(bm.verts.new(p + w*(width*f + jag)))
        right.append(bm.verts.new(p - w*width*f*.6))
    for i in range(len(prof)-1):
        bm.faces.new((left[i], left[i+1], right[i+1], right[i]))

def _apply_mods(o):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(o.evaluated_get(dg)); old = o.data; o.modifiers.clear(); o.data = me
    bpy.data.meshes.remove(old)
    for p in me.polygons: p.use_smooth = True

def wing(arm, side, m_light, m_dark, m_strap, m_metal):
    n = "L" if side > 0 else "R"; rnd = random.Random(7 if side > 0 else 11)
    root = P(f"wing.{n}")
    edge = [root, Vector((.32*side, .30, 1.84)), Vector((.72*side, .42, 1.62))]
    normal = Vector((-.3*side, 1, .1)).normalized()
    def at(t):  # ponto na borda de ataque (t de 0 a 1)
        if t < .45: return edge[0].lerp(edge[1], t/.45)
        return edge[1].lerp(edge[2], (t-.45)/.55)
    def fdir(t): return Vector((side*(.05 + .8*t**1.5), .08 + .1*t, -1)).normalized()
    # membrana por baixo das penas: fecha os buracos da silhueta
    bm = bmesh.new(); prev = None
    for k in range(25):
        t = k/24; a = at(t) + normal*.03; b = a + fdir(t)*(.5 + .35*t**1.3)
        pair = (bm.verts.new(a), bm.verts.new(b))
        if prev: bm.faces.new((prev[0], pair[0], pair[1], prev[1]))
        prev = pair
    memb = obj_from_bm(f"membrana.{n}", bm, m_dark)
    out = []
    for cnt, l0, l1, wd, off, m in [(30, .64, 1.0, .1, 0.0, m_dark), (22, .36, .52, .095, -.018, m_light),
                                    (16, .2, .28, .085, -.034, m_light), (9, .1, .14, .07, -.048, m_light)]:
        bm = bmesh.new()
        for k in range(cnt):
            t = .03 + .97*k/(cnt-1)
            ln = (l0 + (l1-l0)*t**1.3) * rnd.uniform(.9, 1.07)
            feather(bm, at(t) + normal*off - fdir(t)*.02, fdir(t), normal, ln, wd*rnd.uniform(.9,1.15), rnd)
        o = obj_from_bm(f"penas.{n}", bm, m)
        o.modifiers.new("solid", 'SOLIDIFY').thickness = .008; _apply_mods(o); out.append(o)
    # osso da asa (borda) com garra, tiras de couro com fivela
    for a, b in ((edge[0], edge[1]), (edge[1], edge[2])):
        out.append(along("primitive_cylinder_add", m_light, a, b, .034, vertices=10))
    out.append(along("primitive_cone_add", m_metal, edge[1], edge[1] + Vector((.04*side, -.02, .1)), 1, radius1=.02, radius2=0, vertices=6))
    for t in (.15, .35):
        p = at(t)
        out.append(prim("primitive_torus_add", m_strap, p, (1, 1, 1.5), major_radius=.05, minor_radius=.013,
                        major_segments=12, minor_segments=4))
        out.append(prim("primitive_cube_add", m_metal, p + Vector((0, -.05, 0)), (.014, .006, .016)))
    return rigid([memb] + out, arm, f"wing.{n}")

def arc_tube(m, center, radius, r_tube, a0, a1, rot, seg=24):
    """Anel parcial (halo quebrado)."""
    pts = [Vector((radius*math.cos(a0+(a1-a0)*i/seg), 0, radius*math.sin(a0+(a1-a0)*i/seg))) for i in range(seg+1)]
    objs = []
    R = Matrix.Rotation(math.radians(rot[0]), 3, 'X') @ Matrix.Rotation(math.radians(rot[2]), 3, 'Z')
    for i in range(seg):
        objs.append(along("primitive_cylinder_add", m, center + R @ pts[i], center + R @ pts[i+1], r_tube, vertices=6))
    return objs, R

def pauldron(arm, n, m, trim, rivet, layers=3, spikes=None):
    """Ombreira em camadas presa ao braço."""
    s = 1 if n == "L" else -1; o, ax, up, sd = bone_frame(f"upper_arm.{n}")
    objs = []
    for i in range(layers):
        c = o + ax*(.02 + .05*i) + Vector((0, 0, .03 - .012*i))
        objs.append(prim("primitive_uv_sphere_add", m, c, (.1 - .012*i, .115 - .01*i, .06), segments=16, ring_count=8))
        objs[-1].rotation_euler = (0, math.radians(-38*s), 0)
        objs.append(prim("primitive_torus_add", trim, c + Vector((0,0,-.012)), (1, 1.15, 1), (0, -38*s, 0),
                         major_radius=.095 - .012*i, minor_radius=.007, major_segments=16, minor_segments=4))
    for k in range(3):
        objs.append(prim("primitive_uv_sphere_add", rivet, o + ax*.03 + Vector((0, -.06 + .06*k, .095)), (.01, .01, .01),
                         segments=6, ring_count=4))
    if spikes:
        for k in range(3):
            b = o + ax*(.02 + .04*k) + Vector((0, 0, .08))
            objs.append(along("primitive_cone_add", spikes, b, b + Vector((.03*s, 0, .09 - .015*k)), 1, radius1=.016, radius2=0, vertices=6))
    return rigid(objs, arm, f"upper_arm.{n}")

def chain_links(m, a, b, links, sag=.05):
    a, b = Vector(a), Vector(b); out = []
    for i in range(links):
        p = a.lerp(b, i/(links-1)); p.z -= math.sin(math.pi*i/(links-1))*sag
        out.append(prim("primitive_torus_add", m, p, (1,1,1.4), (0, 90 if i%2 else 0, 0), major_radius=.014,
                        minor_radius=.004, major_segments=8, minor_segments=4))
    return out

# ====================================================================== ANJO
def anjo():
    leather = mat("couro_negro", (.016,.013,.014), .1, .35, dirt=.7)
    bone = mat("branco_osso", (.6,.54,.44), 0, .7, dirt=.48, grime=1.25)
    bone2 = mat("osso_sombra", (.42,.38,.31), 0, .7, dirt=.5, grime=1.0)
    porcelain = mat("porcelana", (.68,.65,.6), 0, .2, dirt=.8, grime=.2)
    blood = mat("vermelho_sangue", (.28,.02,.012), 0, .5, dirt=.6, grime=.6)
    gold = mat("ouro_sujo", (.6,.36,.08), 1, .4, dirt=.55, grime=.3)
    iron = mat("ferro_velho", (.1,.095,.09), 1, .5, dirt=.6, grime=.3)
    f_light = mat("pena_suja", (.55,.52,.45), 0, .85, dirt=.45, grime=.7)
    f_dark = mat("pena_gasta", (.34,.31,.27), 0, .9, dirt=.45, grime=.6)
    halo = mat("halo_brasa", (1,.75,.35), emit=(1,.68,.28), strength=8)
    blade = mat("lamina_luz", (1,.8,.45), emit=(1,.74,.38), strength=2.2)
    arm = make_armature("anjo", wings=True)
    parts = body_parts(arm, leather, leather, bone, leather, cuff=.06, sleeve_r=1.12, buckle=gold)
    # sobretudo-batina longo com dobras, aberto na frente, barra rasgada
    rings = [(1.04,.16,.125,0), (.92,.19,.148,.008), (.78,.215,.168,.014), (.6,.245,.19,.02),
             (.42,.272,.212,.028), (.26,.292,.232,.034), (.11,.312,.25,.04)]
    sk = skirt("batina", bone, rings, open_front=.3, jag=.05, seed=2, folds=9, famp=.07)
    bind(sk, arm, ["hips","spine","thigh.L","thigh.R"], power=3); parts.append(sk)
    ln = skirt("forro", blood, [(1.0,.152,.117,.0), (.62,.237,.182,.02), (.13,.3,.24,.04)], open_front=.34, seed=3,
               thick=.004, folds=9, famp=.06)
    ln.scale = (.96, .96, 1); bind(ln, arm, ["hips","spine","thigh.L","thigh.R"], power=3); parts.append(ln)
    # barra com faixa de couro negro (debrum)
    hem = skirt("barra", leather, [(.16,.305,.245,.038), (.11,.314,.252,.04)], open_front=.3, seed=2, folds=9, famp=.07, thick=.014)
    bind(hem, arm, ["hips","thigh.L","thigh.R"], power=3); parts.append(hem)
    # gola alta alargada
    ch = [skirt("gola", bone, [(1.48,.095,.09,.0), (1.58,.1,.095,.01), (1.67,.125,.12,.02)], open_front=.55, thick=.016)]
    ch.append(skirt("gola_debrum", gold, [(1.665,.124,.119,.02), (1.675,.127,.122,.02)], open_front=.55, thick=.006))
    # peitoral: placa de latão envelhecido com a cruz partida
    ch.append(prim("primitive_cube_add", bone2, (0,-.12,1.36), (.1,.02,.08), (8,0,0)))
    ch.append(prim("primitive_cube_add", gold, (0,-.142,1.37), (.008,.005,.05), (8,0,0)))
    ch.append(prim("primitive_cube_add", gold, (.005,-.142,1.39), (.03,.005,.007), (8,0,12)))
    # tiras vermelhas cruzadas no peito e nas costas, fivela de latão
    for s in (1, -1):
        ch.append(along("primitive_cube_add", blood, (.15*s,-.127,1.46), (-.13*s,-.137,1.02), .03))
        ch.append(along("primitive_cube_add", blood, (.15*s,.127,1.46), (-.13*s,.132,1.02), .03))
    ch.append(prim("primitive_cylinder_add", gold, (0,-.15,1.24), (.034,.01,.034), (90,0,0), vertices=12))
    ch.append(prim("primitive_cylinder_add", iron, (0,-.158,1.24), (.016,.006,.016), (90,0,0), vertices=8))
    ch.append(along("primitive_cube_add", leather, (.12,.15,1.42), (-.12,.15,1.42), .022))
    ch.append(along("primitive_cube_add", leather, (.1,.145,1.3), (-.1,.145,1.3), .022))
    parts.append(rigid(ch, arm, "chest"))
    for n in "LR": parts.append(pauldron(arm, n, bone, gold, iron))
    # faixa vermelha + cinto de couro com fivela; ponta da faixa e corrente com cruz na cintura
    hp = [prim("primitive_torus_add", blood, (0,0,1.0), (1,.78,2.3), major_radius=.178, minor_radius=.024),
          prim("primitive_torus_add", leather, (0,0,.945), (1,.8,1.2), major_radius=.182, minor_radius=.016),
          prim("primitive_cube_add", gold, (0,-.155,.945), (.03,.01,.024))]
    hp += chain_links(iron, (-.1,-.14,.95), (-.18,-.06,.9), 6, sag=.07)
    hp.append(prim("primitive_cube_add", iron, (-.19,-.06,.82), (.006,.006,.035)))
    hp.append(prim("primitive_cube_add", iron, (-.19,-.06,.835), (.02,.006,.006)))
    parts.append(rigid(hp, arm, "hips"))
    for nm, x, ln_ in (("faixa_ponta", .11, .5), ("faixa_ponta2", .06, .42)):
        t = skirt(nm, blood, [(.98,.035,.008,0),(.98-ln_,.04,.008,0)], open_front=0, seg=8, thick=.008, jag=.03, seed=4)
        t.data.transform(Matrix.Translation((x, -.135, 0))); bind(t, arm, ["hips","thigh.L"], power=2); parts.append(t)
    # cabeça: rosto de porcelana rachado, venda vermelha com olho dourado bordado, touca
    hf = [prim("primitive_uv_sphere_add", porcelain, (0,-.015,1.67), (.08,.09,.108))]
    hf.append(prim("primitive_uv_sphere_add", porcelain, (0,-.09,1.655), (.012,.012,.02)))     # nariz
    hf.append(prim("primitive_uv_sphere_add", bone, (0,.015,1.7), (.09,.092,.11)))              # touca
    hf.append(prim("primitive_cube_add", leather, (.025,-.098,1.63), (.003,.003,.04), (0,0,0)))  # rachadura
    hf.append(prim("primitive_cube_add", leather, (.035,-.096,1.6), (.003,.003,.02), (0,30,0)))
    hf.append(prim("primitive_torus_add", blood, (0,-.005,1.69), (1,1.08,1.7), major_radius=.087, minor_radius=.013))
    hf.append(along("primitive_cube_add", blood, (-.05,.07,1.68), (-.09,.12,1.56), .012))         # pontas da venda
    hf.append(along("primitive_cube_add", blood, (-.03,.08,1.68), (-.05,.13,1.58), .011))
    hf.append(prim("primitive_uv_sphere_add", gold, (0,-.104,1.69), (.018,.006,.012)))
    hf.append(prim("primitive_uv_sphere_add", leather, (0,-.108,1.69), (.007,.004,.007)))
    # halo de ferro quebrado com brasa (o único brilho junto com a espada)
    hc = Vector((0,.06,1.92))
    h_objs, R = arc_tube(halo, hc, .16, .013, math.radians(-50), math.radians(250), (72,0,0))
    for k in range(10):
        a = math.radians(-40 + k*30)
        p = hc + R @ Vector((.16*math.cos(a), 0, .16*math.sin(a)))
        q = hc + R @ Vector(((.23 if k % 2 else .2)*math.cos(a), 0, (.23 if k % 2 else .2)*math.sin(a)))
        h_objs.append(along("primitive_cone_add", iron, p, q, 1, radius1=.013, radius2=0, vertices=5))
    parts.append(rigid(hf + h_objs, arm, "head"))
    parts.append(wing(arm, 1, f_light, f_dark, leather, gold)); parts.append(wing(arm, -1, f_light, f_dark, leather, gold))
    # espada longa: lâmina de luz, guarda em cruz de ouro sujo, punho de couro
    fr = bone_frame("hand.R"); o, ax, up, sd = fr
    bd = (ax*.45 + up*.9).normalized()
    g = L(fr, .045); sw = []
    sw.append(along("primitive_cylinder_add", leather, g - bd*.1, g + bd*.07, .017, vertices=8))
    sw.append(along("primitive_cube_add", gold, g + bd*.08 + sd*.14, g + bd*.08 - sd*.14, .02))
    for s_ in (1, -1): sw.append(prim("primitive_uv_sphere_add", gold, g + bd*.08 + sd*.15*s_, (.022,.022,.022)))
    sw.append(prim("primitive_uv_sphere_add", gold, g - bd*.11, (.026,.026,.026)))
    bl = along("primitive_cube_add", blade, g + bd*.09, g + bd*.88, 1); bl.scale = (.03, .007, (.88-.09)/2)
    bl2 = along("primitive_cone_add", blade, g + bd*.88, g + bd*.96, 1, radius1=.042, radius2=0, vertices=4)
    sw += [bl, bl2]
    parts.append(rigid(sw, arm, "hand.R"))
    return arm, {"rim": (1, .38, .18)}

# ====================================================================== HUMANO
def hat_brim(m, z, r0=.1, r1=.27, curl=.09, dip=.03, seed=7):
    """Aba de chapéu de cowboy gasta: laterais viradas para cima, frente e trás caídas, borda irregular."""
    rnd = random.Random(seed); bm = bmesh.new(); seg = 40; rings = 5; grid = []
    for i in range(rings+1):
        t = i/rings; r = r0 + (r1-r0)*t; row = []
        for k in range(seg):
            a = 2*math.pi*k/seg
            rr = r*(1.05 if abs(math.sin(a)) > .7 else 1) * (1 - (rnd.uniform(0, .05) if i == rings else 0))
            zz = z + curl*(abs(math.cos(a))**2)*t*t - dip*(abs(math.sin(a))**3)*t
            row.append(bm.verts.new((rr*math.cos(a), rr*math.sin(a)*.95, zz)))
        grid.append(row)
    for i in range(rings):
        for k in range(seg):
            j = (k+1) % seg; bm.faces.new((grid[i][k], grid[i][j], grid[i+1][j], grid[i+1][k]))
    o = obj_from_bm("aba", bm, m); o.modifiers.new("s", 'SOLIDIFY').thickness = .012; _apply_mods(o)
    return o

def humano():
    duster = mat("guarda_po", (.15,.115,.085), 0, .7, dirt=.5, grime=.9)
    poncho = mat("poncho_la", (.17,.06,.03), 0, .9, dirt=.55, grime=.6)
    stripe = mat("poncho_faixa", (.38,.26,.1), 0, .9, dirt=.55, grime=.5)
    leather = mat("couro_velho", (.15,.085,.05), 0, .55, dirt=.55, grime=1.1)
    leather2 = mat("couro_capa", (.09,.045,.025), 0, .6, dirt=.6, grime=.8)
    dark = mat("couro_escuro", (.03,.022,.017), 0, .5, dirt=.7)
    felt = mat("feltro_chapeu", (.055,.04,.03), 0, .85, dirt=.6, grime=.3)
    chaps = mat("perneira", (.07,.045,.03), 0, .6, dirt=.6, grime=.9)
    steel = mat("azul_aco", (.15,.27,.42), 0, .65, dirt=.55, grime=.5)
    skin = mat("pele_suja", (.36,.22,.15), 0, .55, dirt=.7, grime=.3)
    hairm = mat("cabelo", (.03,.025,.02), 0, .7, dirt=.8, grime=0)
    brass = mat("latao", (.55,.29,.08), 1, .38, dirt=.5, grime=.2)
    iron = mat("ferro_gasto", (.12,.12,.12), 1, .42, dirt=.6, grime=.2)
    wood = mat("madeira_coronha", (.16,.065,.025), 0, .45, dirt=.6, grime=.2)
    shell = mat("cartucho", (.42,.06,.03), 0, .45, dirt=.7, grime=.2)
    lens = mat("lente", (.08,.2,.2), .6, .08, dirt=1, grime=0)
    blanket = mat("cobertor", (.2,.16,.1), 0, .95, dirt=.5, grime=.4)
    holy = mat("agua_benta", (.55,.8,1), emit=(.45,.75,1), strength=1.0)
    arm = make_armature("humano")
    parts = body_parts(arm, chaps, dark, duster, dark, cuff=.066, sleeve_r=1.16, top_r=1.04, boot_top=.36, buckle=brass)
    # guarda-pó longo e rasgado, aberto na frente
    rings = [(1.05,.165,.13,0), (.92,.2,.155,.008), (.74,.235,.18,.016), (.55,.268,.208,.024), (.38,.295,.23,.032), (.24,.312,.245,.038)]
    sk = skirt("guarda_po", duster, rings, open_front=.55, jag=.09, seed=5, folds=10, famp=.08)
    bind(sk, arm, ["hips","spine","thigh.L","thigh.R"], power=3); parts.append(sk)
    # poncho de lã por cima dos ombros, com faixa tecida e franja rasgada
    pr = [(1.57,.105,.095,0), (1.5,.22,.16,0), (1.4,.31,.22,.008), (1.27,.36,.26,.015), (1.12,.38,.28,.02)]
    po = skirt("poncho", poncho, pr, open_front=0, jag=.07, seed=9, folds=7, famp=.07)
    bind(po, arm, ["chest","neck","spine","upper_arm.L","upper_arm.R"], power=3); parts.append(po)
    for z0, z1, r0, r1 in ((1.3, 1.26, .362, .368), (1.21, 1.18, .373, .377)):
        st = skirt("poncho_faixa", stripe, [(z0, r0, r0*.72, .016), (z1, r1, r1*.72, .017)], open_front=0, folds=7, famp=.07, seed=9, thick=.006)
        bind(st, arm, ["chest","spine","upper_arm.L","upper_arm.R"], power=3); parts.append(st)
    ch = []
    # bainha da espada nas costas e cobertor enrolado
    ch.append(along("primitive_cube_add", leather2, (.2,.33,1.55), (-.2,.31,.95), .035))
    ch.append(along("primitive_cone_add", brass, (-.2,.31,.95), (-.23,.305,.9), 1, radius1=.035, radius2=.01, vertices=6))
    for t in (.2, .5):
        p_ = Vector((.2,.33,1.55)).lerp(Vector((-.2,.31,.95)), t)
        ch.append(prim("primitive_torus_add", brass, p_, (1,1,1), major_radius=.04, minor_radius=.006))
    parts.append(rigid(ch, arm, "chest"))
    # cinturão com cartucheira, coldre vazio e frascos de água benta
    bl = [prim("primitive_torus_add", dark, (0,0,.97), (1,.82,1.9), (0,6,0), major_radius=.19, minor_radius=.022),
          prim("primitive_cube_add", brass, (0,-.162,.975), (.036,.01,.028))]
    for k in range(14):
        a = math.radians(-60 - k*12); p_ = Vector((.2*math.cos(a), .16*math.sin(a), .975 + .02*math.cos(a)))
        bl.append(prim("primitive_cylinder_add", shell, p_ + Vector((0,0,.012)), (.009,.009,.022), vertices=6))
        bl.append(prim("primitive_cylinder_add", brass, p_ - Vector((0,0,.012)), (.0095,.0095,.005), vertices=6))
    bl.append(along("primitive_cube_add", leather2, (.2,-.04,.95), (.22,-.06,.72), .035))           # coldre
    bl.append(prim("primitive_uv_sphere_add", brass, (.205,-.075,.88), (.012,.006,.012)))
    for x, y in ((-.12,-.13), (-.17,-.08)):
        bl.append(prim("primitive_cylinder_add", holy, (x, y, .91), (.017,.017,.034), vertices=8))
        bl.append(prim("primitive_cylinder_add", brass, (x, y, .952), (.01,.01,.01), vertices=6))
    bl.append(prim("primitive_cylinder_add", blanket, (0,.2,1.0), (.06,.06,.17), (0,90,0), vertices=14))   # cobertor
    for x in (-.1, .1): bl.append(prim("primitive_torus_add", dark, (x,.2,1.0), (1,1,1), (0,90,0), major_radius=.062, minor_radius=.008))
    parts.append(rigid(bl, arm, "hips"))
    for n in "LR": parts.append(pauldron(arm, n, leather2, brass, brass, layers=1))
    # esporas de latão
    for n, s in (("L", 1), ("R", -1)):
        a_ = P(f"foot.{n}") + Vector((0, .07, -.03)); sp = [along("primitive_cylinder_add", brass, a_ - Vector((0,.0,0)), a_ + Vector((0,.05,0)), .006, vertices=4)]
        c_ = a_ + Vector((0,.06,0)); w_ = prim("primitive_torus_add", brass, c_, (1,1,1), (0,90,0), major_radius=.02, minor_radius=.003)
        sp.append(w_)
        for k in range(6):
            ang = k*math.pi/3
            sp.append(along("primitive_cone_add", brass, c_, c_ + Vector((0, .032*math.cos(ang), .032*math.sin(ang))), 1, radius1=.005, radius2=0, vertices=4))
        parts.append(rigid(sp, arm, f"foot.{n}"))
    # cabeça: barba por fazer, lenço contra o pó, cabelo comprido, chapéu de cowboy gasto com óculos
    hd = [prim("primitive_uv_sphere_add", skin, (0,-.012,1.67), (.08,.09,.105))]
    hd.append(prim("primitive_uv_sphere_add", skin, (0,-.098,1.665), (.013,.015,.022)))
    hd.append(prim("primitive_cube_add", dark, (0,-.094,1.695), (.058,.008,.012)))            # sombra do chapéu nos olhos
    hd.append(prim("primitive_uv_sphere_add", steel, (0,-.035,1.61), (.097,.094,.07)))
    hd.append(along("primitive_cone_add", steel, (.0,-.12,1.6), (.01,-.15,1.47), 1, radius1=.05, radius2=.0, vertices=6))
    hd.append(along("primitive_cone_add", steel, (.0,.06,1.6), (.03,.14,1.43), 1, radius1=.03, radius2=.008, vertices=6))
    rnd = random.Random(5)
    for k in range(10):
        a = math.radians(30 + k*12); b_ = Vector((.085*math.cos(a), .06 + .05*math.sin(a), 1.7))
        hd.append(along("primitive_cone_add", hairm, b_, b_ + Vector((rnd.uniform(-.02,.02), .03, -.16)), 1, radius1=.02, radius2=0, vertices=5))
    hd.append(hat_brim(felt, 1.765))
    hd.append(prim("primitive_cone_add", felt, (0,.005,1.83), (1,1.08,1), radius1=.105, radius2=.08, depth=.14, vertices=20))
    hd.append(prim("primitive_uv_sphere_add", felt, (0,.005,1.9), (.08,.087,.022)))
    hd.append(prim("primitive_cube_add", dark, (0,.0,1.912), (.012,.06,.008)))                # vinco da copa
    hd.append(prim("primitive_torus_add", leather, (0,.005,1.785), (1,1.08,1), major_radius=.104, minor_radius=.012))
    for k in range(5):
        a = math.radians(200 + k*35)
        hd.append(prim("primitive_cylinder_add", brass, (.106*math.cos(a), .005 + .112*math.sin(a), 1.785), (.011,.011,.004), (90,0,math.degrees(a)+90), vertices=8))
    for s in (1,-1):
        hd.append(along("primitive_cylinder_add", brass, (.04*s,-.085,1.81), (.04*s,-.115,1.825), .026, vertices=12))
        hd.append(along("primitive_cylinder_add", lens, (.04*s,-.114,1.825), (.04*s,-.119,1.827), .02, vertices=12))
    hd.append(along("primitive_cube_add", dark, (-.012,-.108,1.825), (.012,-.108,1.825), .006))
    parts.append(rigid(hd, arm, "head"))
    # espada larga de lâmina pesada: ferro gasto, fio afiado claro, guarda de latão e cabo longo de couro
    edge_m = mat("fio_afiado", (.7,.71,.73), 1, .18, dirt=.8, grime=.05)
    blade_m = mat("lamina_larga", (.32,.31,.3), 1, .32, dirt=.6, grime=.1)
    fr = bone_frame("hand.R"); o, ax, up, sd = fr
    bd = (ax*.45 + up*.9).normalized(); g = L(fr, .045); perp = bd.cross(sd).normalized()
    sw = [along("primitive_cylinder_add", dark, g - bd*.17, g + bd*.08, .019, vertices=8)]
    for k in range(5): sw.append(prim("primitive_torus_add", leather2, g + bd*(-.15 + .055*k), (1,1,1), major_radius=.02, minor_radius=.005))
    sw[-5:] = [t for t in sw[-5:]]
    for t in sw[-5:]: t.rotation_euler = bd.to_track_quat('Z','Y').to_euler()
    sw.append(prim("primitive_uv_sphere_add", brass, g - bd*.2, (.03,.03,.03), segments=10, ring_count=6))
    gd = g + bd*.09
    sw.append(along("primitive_cube_add", brass, gd + perp*.17, gd - perp*.17, .022))
    for s_ in (1, -1):
        sw.append(along("primitive_cone_add", brass, gd + perp*.17*s_, gd + perp*.2*s_ + bd*.06, 1, radius1=.022, radius2=.008, vertices=6))
    sw.append(along("primitive_cube_add", leather2, gd + bd*.02, gd + bd*.1, .05))   # ricasso enrolado
    rnd = random.Random(13); bm = bmesh.new(); prev = None; pts = []
    N = 12
    for k in range(N+1):
        t = k/N; c = g + bd*(.15 + .85*t)
        wd = .075*(1 - .25*t) if k < N else 0
        nick = rnd.uniform(0, .012) if 2 < k < N-1 else 0       # dentes de uso no fio
        pair = (bm.verts.new(c + perp*(wd - nick)), bm.verts.new(c - perp*wd))
        if prev: bm.faces.new((prev[0], prev[1], pair[1], pair[0]))
        prev = pair; pts.append((c, wd))
    bo = obj_from_bm("espada_larga", bm, blade_m); bo.modifiers.new("s", 'SOLIDIFY').thickness = .014
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(bo.evaluated_get(dg))
    old = bo.data; bo.modifiers.clear(); bo.data = me; bpy.data.meshes.remove(old)
    for pg in me.polygons: pg.use_smooth = False
    sw.append(bo)
    for k in range(N):  # fio claro dos dois lados e sulco central escuro
        (a_, wa), (b_, wb) = pts[k], pts[k+1]
        for s_ in (1, -1):
            sw.append(along("primitive_cube_add", edge_m, a_ + perp*wa*s_*.92, b_ + perp*max(wb, .004)*s_*.92, .006))
        if k < N-3: sw.append(along("primitive_cube_add", dark, a_, b_, .006))
    for k in range(3): sw.append(prim("primitive_uv_sphere_add", brass, g + bd*(.2 + .05*k), (.011,.011,.011), segments=6, ring_count=4))
    parts.append(rigid(sw, arm, "hand.R"))
    # escopeta calibre 12 de cano serrado na mão esquerda (segundo ataque: tiro)
    flash = mat("clarao", (1,.8,.4), emit=(1,.7,.3), strength=25)
    fr = bone_frame("hand.L", up=Vector((0, -1, 0))); o, ax, up, sd = fr
    g = L(fr, .04); gun = []
    for s_ in (1, -1):   # dois canos lado a lado, serrados
        gun.append(along("primitive_cylinder_add", iron, g + up*.04 + sd*.017*s_ - ax*.02, g + up*.04 + sd*.017*s_ + ax*.34, .017, vertices=10))
        gun.append(along("primitive_cylinder_add", dark, g + up*.04 + sd*.017*s_ + ax*.335, g + up*.04 + sd*.017*s_ + ax*.342, .01, vertices=8))
    gun.append(along("primitive_cube_add", iron, g + up*.062 - ax*.02, g + up*.062 + ax*.34, .005))                    # nervura
    gun.append(along("primitive_cube_add", wood, g + up*.018 + ax*.06, g + up*.018 + ax*.26, .022))                    # telha de madeira
    for t in (.1, .2, .3):
        gun.append(prim("primitive_torus_add", brass, g + up*.04 + ax*t, (1,1,1), (0,0,0), major_radius=.04, minor_radius=.004))
    gun.append(along("primitive_cube_add", iron, g + up*.035 - ax*.09, g + up*.035 - ax*.02, .032))                    # báscula
    gun.append(along("primitive_cone_add", brass, g + up*.065 - ax*.08, g + up*.09 - ax*.11, 1, radius1=.009, radius2=0, vertices=4))   # cão
    gun.append(along("primitive_cube_add", wood, g - ax*.08 + up*.02, g - ax*.2 - up*.07, .028))                       # coronha serrada
    gun.append(along("primitive_cube_add", leather, g - ax*.13 - up*.01, g - ax*.18 - up*.05, .031))                   # cabo enrolado em couro
    parts.append(rigid(gun, arm, "hand.L"))
    m0 = g + up*.04 + ax*.34
    flo = rigid([along("primitive_cone_add", flash, m0, m0 + ax*.34, 1, radius1=.11, radius2=0, vertices=8),
                 prim("primitive_uv_sphere_add", flash, m0 + ax*.04, (.09,.09,.09))], arm, "hand.L"); flo.name = "clarao"
    # rastro do giro (skill): arcos claros ao redor do corpo, na altura da espada
    trail_m = mat("rastro_giro", (1,.92,.8), emit=(1,.9,.75), strength=3)
    tr = []
    for k, (r0, z, a0) in enumerate(((1.0, 1.3, 60), (1.18, 1.26, 85), (.82, 1.33, 110))):
        pts_ = [Vector((r0*math.cos(math.radians(a)), r0*math.sin(math.radians(a)), z)) for a in range(a0, 196, 8)]
        for i_ in range(len(pts_)-1):
            tr.append(along("primitive_cylinder_add", trail_m, pts_[i_], pts_[i_+1], .006 + .016*i_/len(pts_), vertices=4))
    tro = rigid(tr, arm, "hips"); tro.name = "rastro"
    # linhas de velocidade e poeira do dash, atrás do corpo
    dust_m = mat("poeira", (.2,.17,.13), 0, 1, dirt=.8, grime=0)
    speed_m = mat("linha_velocidade", (.8,.75,.65), emit=(.8,.75,.65), strength=1.2)
    dl = []
    for k, (x, z, ln) in enumerate(((.12, 1.35, .55), (-.1, 1.15, .7), (.05, .9, .6), (-.15, 1.5, .45), (.18, .7, .5))):
        dl.append(along("primitive_cylinder_add", speed_m, (x, .35, z), (x, .35 + ln, z), .004, vertices=4))
    rnd = random.Random(3)
    for k in range(5):
        dl.append(prim("primitive_uv_sphere_add", dust_m, (rnd.uniform(-.2,.2), .25 + rnd.uniform(0,.45), .04 + rnd.uniform(0,.05)),
                       (rnd.uniform(.04,.07), rnd.uniform(.05,.09), rnd.uniform(.03,.05)), segments=8, ring_count=5))
    dso = rigid(dl, arm, "hips"); dso.name = "rastro_dash"
    # arco do corte horizontal do dash, à frente do corpo
    sl = []
    for r0, z, a0, a1 in ((1.0, 1.22, 200, 330), (1.15, 1.18, 215, 330), (.85, 1.26, 230, 325)):
        pts_ = [Vector((r0*math.cos(math.radians(a)), r0*math.sin(math.radians(a)), z)) for a in range(a0, a1+1, 8)]
        for i_ in range(len(pts_)-1):
            sl.append(along("primitive_cylinder_add", trail_m, pts_[i_], pts_[i_+1], .006 + .016*i_/len(pts_), vertices=4))
    slo = rigid(sl, arm, "hips"); slo.name = "corte_dash"
    return arm, {"rim": (1, .62, .35), "anim": "dual", "flash": flo,
                 "fx": [(tro, "spin", [0,1,1,1,1,1,1,1]), (dso, "dash", [0,0,1,1,1,1,1,0,0,0,0,0]), (slo, "dash", [0,0,0,0,0,0,1,1,1,0,0,0])]}
