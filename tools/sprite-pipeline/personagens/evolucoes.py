# Evoluções de classe no nível 50 (estilo Ragnarok): dois caminhos por classe, estilo "Ferrugem Sagrada".
# Cada evolução parte do modelo base da classe (mesmo esqueleto e animações), troca peças e soma armadura,
# silhueta maior e um brilho mais forte, para ler na hora como um avanço. Uso: render.py / evo_previa.py.
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from rig import *
from classes import (bone_frame, L, body_parts, feather, wing, arc_tube, pauldron, chain_links, _apply_mods)
import classes, classes2, classes3
from classes2 import curve_tube, bezier, bat_wing, head_base, weapon_frame

# ---------------------------------------------------------------- utilidades
def drop(*mats):
    """Remove do modelo base as peças que usam algum destes materiais (arma, cabeça, capa...)."""
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and any(s.material and s.material.name in mats for s in o.material_slots):
            bpy.data.objects.remove(o, do_unlink=True)

def drop_named(*names):
    for o in list(bpy.data.objects):
        if o.type == 'MESH' and any(o.name.startswith(n) for n in names): bpy.data.objects.remove(o, do_unlink=True)

def xform(o, M, pivot):
    """Transforma a malha (na pose de ligação) em torno de um ponto: escala/gira uma peça já presa ao osso."""
    pv = Vector(pivot); o.data.transform(Matrix.Translation(pv) @ M @ Matrix.Translation(-pv))

def rot(axis, deg): return Matrix.Rotation(math.radians(deg), 4, axis)
def scl(s): return Matrix.Diagonal((s, s, s, 1)) if not isinstance(s, tuple) else Matrix.Diagonal((*s, 1))

def grow(arm, s):
    """Personagem evoluído um pouco mais alto e largo (a sombra continua nos pés)."""
    arm.scale = (s, s, s)

def ring_obj(m, c, r, rt, rot_=(90,0,0), seg=40):
    return prim("primitive_torus_add", m, c, (1,1,1), rot_, major_radius=r, minor_radius=rt, major_segments=seg, minor_segments=8)

def plate(m, c, s, r=(0,0,0)):
    o = prim("primitive_cube_add", m, c, s, r)
    b = o.modifiers.new("b", 'BEVEL'); b.width = min(s)*.6; b.segments = 2; _apply_mods(o); return o

def blade_mesh(name, m, pts, widths, normal, thick=.01):
    """Lâmina chata ao longo de uma polilinha: largura por ponto, na direção perpendicular a 'normal'."""
    bm = bmesh.new(); prev = None
    for i, (p, w) in enumerate(zip(pts, widths)):
        d = (pts[min(i+1, len(pts)-1)] - pts[max(i-1, 0)]).normalized(); side = d.cross(normal).normalized()
        pair = (bm.verts.new(p + side*w*.15), bm.verts.new(p - side*w))
        if prev: bm.faces.new((prev[0], prev[1], pair[1], pair[0]))
        prev = pair
    o = obj_from_bm(name, bm, m); o.modifiers.new("s", 'SOLIDIFY').thickness = thick; _apply_mods(o); return o

def cowl(name, m, seed=6, sc=1.0):
    """Capuz arredondado que cobre o topo da cabeça e cai para trás (sem bico para cima)."""
    rings = [(1.47,.17,.15,.02), (1.55,.13,.125,.01), (1.63,.107,.112,.0), (1.7,.1,.108,-.005), (1.76,.094,.104,-.008),
             (1.8,.078,.092,-.008), (1.83,.05,.068,-.002), (1.845,.012,.02,.01)]
    rings = [(z, rx*sc, ry*sc, yo) for z, rx, ry, yo in rings]
    return skirt(name, m, rings, open_front=.85, seed=seed, folds=5, famp=.025, thick=.012)

def tabard(name, m, x, y, z0, z1, w, seed=3, back=False):
    """Faixa de pano pendurada (tabardo/estola) com barra rasgada."""
    rnd = random.Random(seed); bm = bmesh.new(); rows = []
    n = 7
    for k in range(n+1):
        t = k/n; z = z0 + (z1 - z0)*t; ww = w*(1 + .15*t)
        yy = y + (.025*t*t if back else -.02*t*t)
        row = []
        for j in range(5):
            u = j/4 - .5; zz = z + (rnd.uniform(-.04, .01) if k == n else 0)
            row.append(bm.verts.new((x + u*ww*2, yy + .012*math.sin(u*6 + seed), zz)))
        rows.append(row)
    for k in range(n):
        for j in range(4): bm.faces.new((rows[k][j], rows[k][j+1], rows[k+1][j+1], rows[k+1][j]))
    o = obj_from_bm(name, bm, m); o.modifiers.new("s", 'SOLIDIFY').thickness = .008; _apply_mods(o); return o

# ====================================================================== ANJO → ARCANJO
def arcanjo():
    """General da hoste: armadura de placas de ouro sujo sobre a batina, quatro asas, coroa-halo em roda de sol
    e um montante flamejante de luz. Linha de frente que ainda cura (aura)."""
    mat("pena_suja", (.62,.58,.5), 0, .85, dirt=.45, grime=.7)
    arm, info = classes.anjo()
    drop("lamina_luz", "halo_brasa")   # espada e halo antigos (a cabeça sai junto e é refeita)
    leather = mat("couro_negro", (.016,.013,.014)); bone = mat("branco_osso", (.6,.54,.44))
    porcelain = mat("porcelana", (.68,.65,.6)); blood = mat("vermelho_sangue", (.28,.02,.012))
    gold = mat("ouro_sujo", (.6,.36,.08)); iron = mat("ferro_velho", (.1,.095,.09))
    f_light = mat("pena_suja", (.62,.58,.5)); f_dark = mat("pena_gasta", (.34,.31,.27))
    plate_m = mat("placa_ouro_velho", (.55,.4,.16), 1, .32, dirt=.5, grime=.35)
    steel = mat("aco_escurecido", (.2,.19,.18), 1, .38, dirt=.55, grime=.3)
    halo = mat("halo_sol", (1,.78,.4), emit=(1,.7,.3), strength=9)
    blade = mat("lamina_sol", (1,.82,.5), emit=(1,.74,.36), strength=2.6)
    parts = []
    # couraça de placas sobre a batina: peito em quilha, plaquetas da barriga, gorjal
    ch = [plate(plate_m, (0,-.105,1.36), (.16,.06,.12), (8,0,0)),
          plate(plate_m, (0,-.12,1.4), (.05,.04,.1), (8,0,45)),
          plate(steel, (0,-.11,1.2), (.15,.05,.035)), plate(steel, (0,-.115,1.13), (.145,.05,.03)),
          prim("primitive_torus_add", plate_m, (0,-.01,1.5), (1,1,1.4), major_radius=.1, minor_radius=.03)]
    ch.append(prim("primitive_cube_add", gold, (0,-.17,1.37), (.01,.006,.075), (8,0,0)))       # cruz partida em relevo
    ch.append(prim("primitive_cube_add", gold, (.008,-.17,1.4), (.045,.006,.009), (8,0,14)))
    for s in (1, -1):
        ch.append(along("primitive_cube_add", gold, (.15*s,-.13,1.46), (.12*s,-.16,1.25), .008))  # filete
    ch.append(plate(plate_m, (0,.11,1.33), (.15,.05,.13)))                                     # costas
    parts.append(rigid(ch, arm, "chest"))
    for n in "LR":
        s = 1 if n == "L" else -1; o, ax, up, sd = bone_frame(f"upper_arm.{n}")
        pa = []
        for i in range(4):  # ombreira grande em lâminas sobrepostas, com filete de ouro na borda
            c = o + ax*(.0 + .045*i) + Vector((0, 0, .05 - .018*i))
            e = prim("primitive_uv_sphere_add", plate_m if i % 2 == 0 else steel, c, (.14 - .015*i, .14 - .012*i, .07), segments=16, ring_count=8)
            e.rotation_euler = (0, math.radians(-34*s), 0); pa.append(e)
            pa.append(prim("primitive_torus_add", gold, c + Vector((0,0,-.014)), (1,1.05,1), (0,-34*s,0), major_radius=.135 - .015*i, minor_radius=.008, major_segments=20, minor_segments=4))
        for k in range(4):  # penas de metal subindo da ombreira
            b = o + ax*(.02 + .035*k) + Vector((0, .03, .1))
            pa.append(along("primitive_cone_add", gold, b, b + Vector((.05*s, .03, .16 - .03*k)), 1, radius1=.022, radius2=0, vertices=4))
        parts.append(rigid(pa, arm, f"upper_arm.{n}"))
        o, ax, up, sd = bone_frame(f"forearm.{n}")  # braçal
        parts.append(rigid([along("primitive_cone_add", plate_m, o + ax*.04, o + ax*.17, 1, radius1=.058, radius2=.05, vertices=12),
                            prim("primitive_torus_add", gold, o + ax*.17, (1,1,1), major_radius=.052, minor_radius=.008)], arm, f"forearm.{n}"))
        for nm in (f"thigh.{n}", f"shin.{n}"):  # coxote e grevas por baixo da batina
            o, ax, up, sd = bone_frame(nm)
            parts.append(rigid([along("primitive_cone_add", steel if nm[0] == "t" else plate_m, o + ax*.06, o + ax*.3, 1, radius1=.075, radius2=.062, vertices=12)], arm, nm))
    # tabardo vermelho na frente e atrás, com a cruz partida bordada
    tb = [tabard("tabardo", blood, 0, -.2, 1.0, .3, .09, seed=5), tabard("tabardo_c", blood, 0, .2, 1.0, .35, .1, seed=8, back=True)]
    tb.append(prim("primitive_cube_add", gold, (0,-.214,.78), (.008,.004,.07)))
    tb.append(prim("primitive_cube_add", gold, (.006,-.214,.81), (.04,.004,.008), (0,0,12)))
    for t in tb[:2]: bind(t, arm, ["hips","thigh.L","thigh.R"], power=2)
    parts += tb[:2]; parts.append(rigid(tb[2:], arm, "hips"))
    # cabeça: rosto de porcelana com elmo aberto de ouro e crista de penas de metal
    hf = [prim("primitive_uv_sphere_add", porcelain, (0,-.015,1.67), (.08,.09,.108)),
          prim("primitive_uv_sphere_add", porcelain, (0,-.09,1.655), (.012,.012,.02)),
          prim("primitive_torus_add", blood, (0,-.005,1.69), (1,1.08,1.7), major_radius=.087, minor_radius=.013),
          prim("primitive_uv_sphere_add", gold, (0,-.104,1.69), (.018,.006,.012))]
    helm = skirt("elmo", plate_m, [(1.6,.1,.11,.0), (1.7,.098,.108,.0), (1.79,.085,.095,.005), (1.84,.05,.06,.01)], open_front=.9, thick=.012)
    hf.append(helm)
    hf.append(prim("primitive_torus_add", gold, (0,.0,1.705), (1,1.1,1), major_radius=.096, minor_radius=.01))
    for s in (1, -1):  # asinhas do elmo
        for k in range(4):
            b = Vector((.09*s, .01 + .015*k, 1.72 + .015*k))
            hf.append(along("primitive_cone_add", gold, b, b + Vector((.1*s, .06 + .02*k, .07 + .04*k)), 1, radius1=.016, radius2=0, vertices=4))
    for k in range(7):  # crista
        b = Vector((0, -.04 + .03*k, 1.83 - .01*k)); hf.append(along("primitive_cone_add", gold, b, b + Vector((0, .04, .1 - .008*k)), 1, radius1=.014, radius2=0, vertices=4))
    # coroa-halo em roda de sol atrás da cabeça: dois anéis, raios de ferro e pontas de brasa
    hc = Vector((0, .13, 1.86)); R = rot('X', 78)
    hf += [ring_obj(halo, hc, .22, .014, (78,0,0), 48), ring_obj(iron, hc, .15, .012, (78,0,0), 32)]
    for k in range(16):
        a = 2*math.pi*k/16; d = (R @ Vector((math.cos(a), math.sin(a), 0))).normalized()
        hf.append(along("primitive_cylinder_add", iron, hc + d*.15, hc + d*.22, .005, vertices=4))
        hf.append(along("primitive_cone_add", halo if k % 2 == 0 else iron, hc + d*.22, hc + d*(.34 if k % 2 == 0 else .28), 1, radius1=.014, radius2=0, vertices=4))
    parts.append(rigid(hf, arm, "head"))
    # quatro asas: as de baixo maiores e as de cima menores, mais altas e abertas
    for side in (1, -1):
        n = "L" if side > 0 else "R"; root = P(f"wing.{n}")
        for o in [o for o in bpy.data.objects if o.name.startswith(f"anjo_wing.{n}")]: xform(o, scl(1.18), root)
        up_ = wing(arm, side, f_light, f_dark, leather, gold)
        xform(up_, rot('Y', -48*side) @ scl(.82), root); xform(up_, Matrix.Translation((0, .02, .2)), (0,0,0))
    # montante flamejante: lâmina de luz ondulada, guarda em asas de ouro, punho longo
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr
    sw = [along("primitive_cylinder_add", leather, g - bd*.2, g + bd*.08, .019, vertices=8),
          prim("primitive_uv_sphere_add", gold, g - bd*.22, (.03,.03,.03))]
    for s_ in (1, -1):
        sw += curve_tube(gold, [g + bd*.09, g + bd*.1 + sd*.1*s_, g + bd*.16 + sd*.2*s_], .022, .004, 6)
    sw.append(prim("primitive_uv_sphere_add", plate_m, g + bd*.1, (.035,.035,.035)))
    perp = bd.cross(sd).normalized()
    for k in range(12):  # lâmina ondulada (flamberge) em segmentos largos
        a_ = g + bd*(.12 + .095*k) + sd*.014*math.sin(k*1.6)*.0; b_ = g + bd*(.12 + .095*(k+1))
        sg = along("primitive_cube_add", blade, a_, b_, 1); sg.scale = (.04 + .012*(k % 2), .007, (b_ - a_).length/2 + .004); sw.append(sg)
    sw.append(along("primitive_cone_add", blade, g + bd*1.26, g + bd*1.38, 1, radius1=.045, radius2=0, vertices=4))
    parts.append(rigid(sw, arm, "hand.R"))
    grow(arm, 1.06)
    info.update({"rim": (1, .5, .22), "base": "anjo"}); return arm, info

# ====================================================================== ANJO → SERAFIM
def serafim():
    """O que arde diante do trono: seis asas (duas por cima da cabeça, duas cobrindo os pés), túnica longa de linho
    queimado com selos de oração, rodas de olhos em volta da cabeça e um turíbulo-lanterna de fogo branco.
    O suporte puro: cura, escudo de luz e ressurreição."""
    mat("branco_osso", (.72,.66,.54), 0, .7, dirt=.5, grime=1.1)
    mat("pena_suja", (.78,.72,.6), 0, .8, dirt=.5, grime=.5)
    mat("pena_gasta", (.55,.47,.36), 0, .9, dirt=.5, grime=.5)
    mat("vermelho_sangue", (.32,.12,.03), 0, .5, dirt=.6, grime=.6)
    arm, info = classes.anjo()
    drop("lamina_luz", "halo_brasa")
    leather = mat("couro_negro", (.016,.013,.014)); bone = mat("branco_osso", (.72,.66,.54))
    gold = mat("ouro_sujo", (.6,.36,.08)); iron = mat("ferro_velho", (.1,.095,.09))
    f_light = mat("pena_suja", (.78,.72,.6)); f_dark = mat("pena_gasta", (.55,.47,.36))
    paper = mat("papel_selo", (.62,.55,.4), 0, .9, dirt=.5, grime=.6)
    wax = mat("lacre_cera", (.35,.05,.03), 0, .4, dirt=.6, grime=.2)
    linen = mat("linho_queimado", (.56,.5,.4), 0, .85, dirt=.45, grime=1.4)
    fire = mat("fogo_branco", (1,.86,.6), emit=(1,.8,.5), strength=11)
    parts = []
    # túnica longa até o chão por cima da batina, bem larga, barra queimada
    t = skirt("tunica_serafim", linen, [(1.1,.17,.14,0), (.85,.23,.18,.01), (.55,.3,.23,.02), (.25,.36,.28,.035), (.02,.42,.33,.05)],
              open_front=.0, jag=.05, seed=31, folds=13, famp=.08)
    bind(t, arm, ["hips","spine","thigh.L","thigh.R"], power=3); parts.append(t)
    # estola dourada e selos de oração (tiras de papel com lacre) presos na cintura
    st = [tabard("estola_L", gold, .07, -.19, 1.42, .45, .025, seed=2), tabard("estola_R", gold, -.07, -.19, 1.42, .45, .025, seed=4)]
    for t_ in st: bind(t_, arm, ["chest","spine","hips","thigh.L","thigh.R"], power=2)
    parts += st
    sl = []
    rnd = random.Random(9)
    for k in range(9):
        a = math.radians(-70 + k*20); x = .19*math.sin(a); y = -.15*math.cos(a)
        ln = rnd.uniform(.16, .3)
        sl.append(prim("primitive_cube_add", paper, (x, y - .01, 1.0 - ln/2), (.022, .003, ln/2), (0, 0, math.degrees(a)*.3)))
        sl.append(prim("primitive_uv_sphere_add", wax, (x, y - .016, .99), (.018, .008, .018), segments=8, ring_count=5))
    sl.append(prim("primitive_torus_add", gold, (0,0,1.0), (1,.8,1.3), major_radius=.19, minor_radius=.014))
    parts.append(rigid(sl, arm, "hips"))
    # cabeça: véu de linho, máscara de ouro sem rosto com três olhos cegos
    hf = [prim("primitive_uv_sphere_add", gold, (0,-.02,1.67), (.08,.09,.108)),
          skirt("veu", linen, [(1.86,.06,.06,.0), (1.78,.11,.115,.0), (1.66,.12,.125,.01), (1.52,.15,.14,.02), (1.42,.2,.17,.02)], open_front=.55, thick=.01, folds=7, famp=.05)]
    for x, z in ((-.035,1.69), (.035,1.69), (0,1.735)):
        hf.append(prim("primitive_uv_sphere_add", iron, (x,-.104,z), (.017,.006,.011)))
        hf.append(prim("primitive_uv_sphere_add", bone, (x,-.108,z), (.009,.004,.007)))
    # rodas de olhos: dois anéis cruzados de ferro e fogo branco em volta da cabeça, com olhos de osso
    hc = Vector((0, .07, 1.76))
    for rx, rz in ((70, 28), (70, -34)):
        hf.append(prim("primitive_torus_add", fire, hc, (1,1,1), (rx, 0, rz), major_radius=.2, minor_radius=.008, major_segments=48, minor_segments=6))
        hf.append(prim("primitive_torus_add", iron, hc, (1,1,1), (rx, 0, rz), major_radius=.215, minor_radius=.01, major_segments=48, minor_segments=6))
        Rm = Matrix.Rotation(math.radians(rz), 3, 'Z') @ Matrix.Rotation(math.radians(rx), 3, 'X')
        for k in range(8):
            a = 2*math.pi*(k + .5)/8; p = hc + Rm @ Vector((.215*math.cos(a), .215*math.sin(a), 0))
            hf.append(prim("primitive_uv_sphere_add", bone, p, (.02,.02,.02), segments=10, ring_count=6))
            hf.append(prim("primitive_uv_sphere_add", leather, p + (p - hc).normalized()*.018, (.011,.011,.011), segments=8, ring_count=5))
    parts.append(rigid(hf, arm, "head"))
    # seis asas: o par do meio (base) maior; o de cima dobra para frente sobre a cabeça; o de baixo desce cobrindo os pés
    for side in (1, -1):
        n = "L" if side > 0 else "R"; root = P(f"wing.{n}")
        for o in [o for o in bpy.data.objects if o.name.startswith(f"anjo_wing.{n}")]: xform(o, scl(1.12), root)
        top = wing(arm, side, f_light, f_dark, leather, gold)
        xform(top, rot('X', -32) @ rot('Y', -20*side) @ scl(.72), root); xform(top, Matrix.Translation((0, -.02, .2)), (0,0,0))
        low = wing(arm, side, f_light, f_dark, leather, gold)
        xform(low, rot('Y', 52*side) @ rot('X', 18) @ scl(.78), root); xform(low, Matrix.Translation((0, .02, -.22)), (0,0,0))
    # turíbulo-lanterna: cajado de ferro com gaiola e fogo branco dentro, correntes e um selo
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr
    sw = [along("primitive_cylinder_add", iron, g - bd*.55, g + bd*.85, .017, vertices=8),
          along("primitive_cylinder_add", gold, g - bd*.04, g + bd*.08, .021, vertices=8),
          along("primitive_cone_add", iron, g - bd*.55, g - bd*.66, 1, radius1=.02, radius2=0, vertices=6)]
    top = g + bd*.95
    sw.append(prim("primitive_uv_sphere_add", fire, top, (.05,.05,.065), segments=12, ring_count=8))
    for k in range(6):
        a = 2*math.pi*k/6; d = (sd*math.cos(a) + bd.cross(sd).normalized()*math.sin(a))
        sw += curve_tube(gold, [top - bd*.09 + d*.02, top - bd*.04 + d*.075, top + bd*.05 + d*.075, top + bd*.11 + d*.02], .008, .008, 5)
    sw.append(along("primitive_cube_add", gold, top + bd*.12, top + bd*.24, .009))
    sw.append(along("primitive_cube_add", gold, top + bd*.19 + sd*.05, top + bd*.19 - sd*.05, .009))
    sw += chain_links(iron, top - bd*.1 + sd*.04, top - bd*.3 + sd*.07, 6, sag=.0)
    sw.append(prim("primitive_cube_add", paper, top - bd*.38 + sd*.07, (.018,.004,.06)))
    parts.append(rigid(sw, arm, "hand.R"))
    grow(arm, 1.04)
    info.update({"rim": (1, .7, .4), "base": "anjo"}); return arm, info

# ====================================================================== DEMÔNIO → LORDE DAS TREVAS
def lorde_das_trevas():
    """O general que a Legião Blasfema perdeu, ou quem quer o lugar dele: placas de ferro negro sobre a carne,
    ombreiras com chifres, elmo coroado de chifres, capa pesada, escudo-torre com a cara do Juízo e espadão de brasa."""
    mat("asa_couro", (.03,.01,.01), 0, .55, dirt=.55, grime=.5)
    arm, info = classes2.demonio()
    drop("moicano_vermelho")                    # cabeça antiga (moicano)
    drop_named("demonio_hand.R")                # cutelo
    leather = mat("couro_negro", (.016,.013,.014)); flesh = mat("carne_demoniaca", (.16,.035,.028))
    iron = mat("ferro_velho", (.1,.095,.09)); horn = mat("chifre", (.07,.055,.045)); brass = mat("latao_velho", (.5,.27,.07))
    ember = mat("brasa", (1,.4,.08))
    black = mat("ferro_negro", (.05,.045,.045), 1, .42, dirt=.6, grime=.3)
    cape_m = mat("capa_sangue_seco", (.09,.012,.012), 0, .75, dirt=.55, grime=.8)
    parts = []
    # couraça negra com fissuras de brasa, faixa de placas na barriga, gorjal alto de espinhos
    ch = [plate(black, (0,-.1,1.36), (.2,.08,.14), (6,0,0)), plate(black, (0,.1,1.34), (.19,.06,.15)),
          plate(black, (0,-.12,1.18), (.17,.05,.04)), plate(black, (0,-.125,1.1), (.165,.05,.035)),
          prim("primitive_torus_add", black, (0,-.005,1.52), (1,1,1.9), major_radius=.1, minor_radius=.035)]
    rnd = random.Random(5)
    for x0 in (-.06, .05):
        p = Vector((x0, -.182, 1.46))
        for k in range(5):
            q = p + Vector((rnd.uniform(-.035, .035), -.003, -.05)); ch.append(along("primitive_cube_add", ember, p, q, .004)); p = q
    for k in range(5):
        a = math.radians(-60 + k*30); d = Vector((math.sin(a), -math.cos(a)*.6, 0)).normalized()
        b = Vector((0, .02, 1.56)) + Vector((d.x*.1, d.y*.1 + .03, 0))
        ch.append(along("primitive_cone_add", iron, b, b + Vector((d.x*.05, .06, .14)), 1, radius1=.02, radius2=0, vertices=5))
    parts.append(rigid(ch, arm, "chest"))
    for n in "LR":
        s = 1 if n == "L" else -1; o, ax, up, sd = bone_frame(f"upper_arm.{n}")
        pa = []
        for i in range(3):
            c = o + ax*(.0 + .05*i) + Vector((0, 0, .06 - .02*i))
            e = prim("primitive_uv_sphere_add", black, c, (.16 - .02*i, .15 - .015*i, .08), segments=16, ring_count=8)
            e.rotation_euler = (0, math.radians(-30*s), 0); pa.append(e)
            pa.append(prim("primitive_torus_add", iron, c + Vector((0,0,-.015)), (1,1,1), (0,-30*s,0), major_radius=.15 - .02*i, minor_radius=.009, major_segments=20, minor_segments=4))
        pa += curve_tube(horn, bezier(o + Vector((.03*s,.02,.1)), o + Vector((.1*s,.04,.24)), o + Vector((.2*s,.07,.28)), o + Vector((.24*s,.12,.2)), 6), .038, .004, 7)
        pa.append(along("primitive_cone_add", horn, o + Vector((.0,-.04,.1)), o + Vector((.04*s,-.08,.22)), 1, radius1=.025, radius2=0, vertices=6))
        parts.append(rigid(pa, arm, f"upper_arm.{n}"))
        o, ax, up, sd = bone_frame(f"forearm.{n}")
        g_ = [along("primitive_cone_add", black, o + ax*.02, o + ax*.19, 1, radius1=.07, radius2=.06, vertices=12)]
        for k in range(3): g_.append(along("primitive_cone_add", iron, o + ax*(.05 + .05*k) + Vector((0,.06,0)), o + ax*(.03 + .05*k) + Vector((0,.12,.02)), 1, radius1=.014, radius2=0, vertices=5))
        parts.append(rigid(g_, arm, f"forearm.{n}"))
        for nm in (f"thigh.{n}", f"shin.{n}"):
            o, ax, up, sd = bone_frame(nm)
            parts.append(rigid([along("primitive_cone_add", black, o + ax*.05, o + ax*.32, 1, radius1=.085, radius2=.07, vertices=12),
                                prim("primitive_uv_sphere_add", black, o + ax*.0, (.07,.07,.06))], arm, nm))
    # saiote de lâminas de ferro e capa pesada sob as asas
    sk = skirt("saiote_laminas", black, [(1.02,.2,.15,0), (.86,.23,.18,.005), (.66,.26,.21,.01)], open_front=.25, jag=.04, seed=7, folds=16, famp=.05)
    bind(sk, arm, ["hips","thigh.L","thigh.R"], power=3); parts.append(sk)
    cp = skirt("capa", cape_m, [(1.52,.2,.1,.08), (1.2,.26,.14,.12), (.8,.32,.16,.17), (.4,.37,.18,.21), (.08,.41,.2,.24)], open_front=1.9, jag=.08, seed=13, folds=9, famp=.08)
    bind(cp, arm, ["chest","spine","hips"], power=3); parts.append(cp)
    # cabeça: elmo fechado de ferro negro, viseira em fenda de brasa, coroa de chifres
    hd = [head_base(flesh, (.078,.088,.104)),
          skirt("elmo_lorde", black, [(1.56,.1,.11,0), (1.66,.105,.115,0), (1.76,.1,.11,.0), (1.84,.07,.08,.01), (1.88,.03,.04,.01)], open_front=0, thick=.014),
          prim("primitive_cube_add", black, (0,-.1,1.62), (.06,.03,.06), (20,0,0))]
    for s in (1, -1):
        hd.append(prim("primitive_cube_add", ember, (.032*s,-.108,1.69), (.024,.004,.006), (0,0,-10*s)))
    for s in (1, -1):
        hd += curve_tube(horn, bezier((.07*s,-.02,1.78), (.16*s,-.04,1.86), (.26*s,.02,1.96), (.24*s,.12,2.08), 7), .04, .005, 8)
        hd += curve_tube(horn, bezier((.05*s,.04,1.83), (.08*s,.04,1.95), (.1*s,.08,2.03), (.07*s,.14,2.1), 5), .025, .004, 6)
        hd.append(prim("primitive_torus_add", brass, (.16*s,-.035,1.87), (1,1,1), major_radius=.03, minor_radius=.007))
    hd += curve_tube(horn, bezier((0,-.05,1.84), (0,-.08,1.94), (0,-.06,2.02), (0,-.01,2.08), 5), .022, .003, 6)
    parts.append(rigid(hd, arm, "head"))
    # asas maiores
    for side in (1, -1):
        n = "L" if side > 0 else "R"
        for o in [o for o in bpy.data.objects if o.name.startswith(f"demonio_wing.{n}")]: xform(o, scl(1.2), P(f"wing.{n}"))
    # espadão negro com fissura de brasa no meio da lâmina
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr; perp = bd.cross(sd).normalized()
    w = [along("primitive_cylinder_add", leather, g - bd*.22, g + bd*.08, .02, vertices=8),
         prim("primitive_uv_sphere_add", iron, g - bd*.24, (.032,.032,.032)),
         along("primitive_cube_add", black, g + bd*.09 + sd*.15, g + bd*.09 - sd*.15, .026)]
    for s_ in (1, -1): w.append(along("primitive_cone_add", horn, g + bd*.09 + sd*.15*s_, g + bd*.2 + sd*.22*s_, 1, radius1=.022, radius2=0, vertices=5))
    pts = [g + bd*(.1 + .1*k) for k in range(12)] + [g + bd*1.32]
    bl = blade_mesh("espadao", black, pts, [.07 - .002*k for k in range(12)] + [0], perp, .016)
    w.append(bl)
    w.append(along("primitive_cube_add", ember, g + bd*.14 - bd.cross(perp).normalized()*.0, g + bd*1.12, .006))
    parts.append(rigid(w, arm, "hand.R"))
    # escudo-torre no braço esquerdo: ferro negro, máscara do Juízo em relevo com olhos de brasa
    o, ax, up, sd = bone_frame("forearm.L"); c = o + ax*.12 + Vector((.09, -.05, -.02))
    nrm = Vector((.75, -.6, 0)).normalized(); upv = Vector((0, 0, 1)); sv = nrm.cross(upv).normalized()
    bm = bmesh.new()
    outline = [(-.2, .38), (.2, .38), (.22, .1), (.2, -.3), (0, -.46), (-.2, -.3), (-.22, .1)]
    vs = [bm.verts.new(c + sv*x + upv*z - nrm*(.04*(1 - (x/.22)**2))) for x, z in outline]
    bm.faces.new(vs)
    sh = obj_from_bm("escudo", bm, black); sh.modifiers.new("s", 'SOLIDIFY').thickness = .035; _apply_mods(sh)
    shp = [sh]
    for x, z in outline: shp.append(prim("primitive_uv_sphere_add", iron, c + sv*x*.93 + upv*z*.93 + nrm*.012, (.016,.016,.016), segments=6, ring_count=4))
    face = c + nrm*.03 + upv*.06
    shp.append(prim("primitive_uv_sphere_add", iron, face, (.09,.09,.11)))
    for s in (1, -1):
        shp.append(prim("primitive_uv_sphere_add", ember, face + nrm*.07 + sv*.035*s + upv*.02, (.016,.016,.009)))
        shp += curve_tube(horn, [face + sv*.07*s + upv*.08, face + sv*.15*s + upv*.18 + nrm*.02, face + sv*.13*s + upv*.28 + nrm*.03], .025, .004, 6)
    shp.append(along("primitive_cube_add", ember, face + nrm*.07 - upv*.05 - sv*.03, face + nrm*.07 - upv*.05 + sv*.03, .005))
    parts.append(rigid(shp, arm, "forearm.L"))
    grow(arm, 1.12)
    info.update({"rim": (1, .3, .12), "base": "demonio"}); return arm, info

# ====================================================================== DEMÔNIO → CEIFADOR
def ceifador():
    """O que colhe a alma antes do Juízo: capuz e manto em farrapos, máscara de crânio, asas de ossos-lâmina
    sem membrana e uma foice longa de ferro com o fio em brasa. Assassino: some, aparece atrás e corta."""
    arm, info = classes2.demonio()
    drop("moicano_vermelho", "asa_couro")       # cabeça e asas antigas
    drop_named("demonio_hand.R", "sobretudo_sem_manga", "demonio_upper_arm.L")
    leather = mat("couro_negro", (.016,.013,.014)); flesh = mat("carne_demoniaca", (.16,.035,.028))
    iron = mat("ferro_velho", (.1,.095,.09)); horn = mat("chifre", (.07,.055,.045)); ember = mat("brasa", (1,.4,.08))
    shroud = mat("mortalha_negra", (.022,.02,.022), 0, .8, dirt=.55, grime=.6)
    bone = mat("osso_ceifa", (.42,.38,.31), 0, .6, dirt=.5, grime=.6)
    black = mat("ferro_negro", (.05,.045,.045), 1, .42, dirt=.6, grime=.3)
    parts = []
    # manto em farrapos até o chão, aberto, com tiras soltas
    m1 = skirt("manto_ceifa", shroud, [(1.5,.19,.13,0), (1.3,.23,.16,.01), (1.0,.25,.18,.02), (.7,.28,.2,.03), (.4,.3,.22,.04), (.1,.34,.25,.05)],
               open_front=.55, jag=.14, seed=41, folds=11, famp=.09)
    bind(m1, arm, ["chest","spine","hips","thigh.L","thigh.R","upper_arm.L","upper_arm.R"], power=3); parts.append(m1)
    rnd = random.Random(4)
    for k in range(7):
        a = math.radians(110 + k*22); x, y = .3*math.cos(a), .22*math.sin(a) + .04
        t = tabard(f"farrapo{k}", shroud, x, y, .55, .55 - rnd.uniform(.38, .55), .02, seed=k, back=True)
        bind(t, arm, ["hips","thigh.L","thigh.R"], power=2); parts.append(t)
    # correias cruzadas no peito e cinta com ossos pendurados
    ch = []
    for s in (1, -1): ch.append(along("primitive_cube_add", leather, (.16*s,-.15,1.45), (-.12*s,-.16,1.04), .022))
    ch.append(plate(black, (0,-.17,1.27), (.035,.02,.035), (0,0,45)))
    parts.append(rigid(ch, arm, "chest"))
    hp = [prim("primitive_torus_add", leather, (0,0,.98), (1,.8,1.4), major_radius=.19, minor_radius=.018)]
    for k in range(5):
        x = -.15 + .075*k
        hp.append(prim("primitive_uv_sphere_add", bone, (x, -.17 + abs(x)*.25, .9), (.022,.018,.03), segments=8, ring_count=6))
    parts.append(rigid(hp, arm, "hips"))
    # braçadeira de lâminas no antebraço esquerdo
    o, ax, up, sd = bone_frame("forearm.L")
    parts.append(rigid([along("primitive_cone_add", black, o + ax*.04, o + ax*.18, 1, radius1=.062, radius2=.052, vertices=10)] +
                       [along("primitive_cone_add", black, o + ax*(.06 + .05*k) + Vector((0,.05,0)), o + ax*(.11 + .05*k) + Vector((0,.15,.03)), 1, radius1=.012, radius2=0, vertices=4) for k in range(3)], arm, "forearm.L"))
    # capuz fundo com máscara de crânio cornudo e olhos de brasa
    hd = [head_base(bone, (.072,.082,.1)),
          cowl("capuz_ceifa", shroud, seed=41, sc=1.05),
          prim("primitive_uv_sphere_add", bone, (0,-.07,1.61), (.05,.04,.035))]
    for s in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", leather, (.03*s,-.088,1.69), (.022,.012,.016)))
        hd.append(prim("primitive_uv_sphere_add", ember, (.03*s,-.096,1.688), (.008,.005,.006)))
        hd += curve_tube(horn, bezier((.06*s,-.05,1.79), (.1*s,-.08,1.86), (.12*s,-.06,1.95), (.1*s,.0,2.02), 5), .02, .003, 6)
    for k in range(5): hd.append(prim("primitive_cube_add", bone, (-.024 + .012*k,-.104,1.6), (.004,.004,.012)))
    parts.append(rigid(hd, arm, "head"))
    # asas de ossos-lâmina: dedos longos de osso com lâminas de ferro negro e farrapos presos
    for side in (1, -1):
        n = "L" if side > 0 else "R"
        root = P(f"wing.{n}"); el = Vector((.32*side, .32, 1.86)); wr = Vector((.6*side, .48, 1.8))
        tips = [Vector((1.08*side, .56, 1.7)), Vector((1.1*side, .62, 1.3)), Vector((.9*side, .6, .95)), Vector((.62*side, .5, .74))]
        wb = [along("primitive_cylinder_add", bone, root, el, .028, vertices=8), along("primitive_cylinder_add", bone, el, wr, .024, vertices=8),
              prim("primitive_uv_sphere_add", bone, el, (.034,.034,.034)), prim("primitive_uv_sphere_add", bone, wr, (.03,.03,.03))]
        for i, t in enumerate(tips):
            mid = wr.lerp(t, .4) + Vector((0, .03, .03))
            wb += curve_tube(bone, [wr, mid, mid.lerp(t, .5)], .022, .012, 6)
            bl_ = along("primitive_cone_add", black, mid, t, 1, radius1=.05, radius2=0, vertices=4)
            bl_.scale = (.05, .012, (t - mid).length/2); wb.append(bl_)
        wb.append(along("primitive_cone_add", black, el, el + Vector((.04*side, -.03, .16)), 1, radius1=.024, radius2=0, vertices=5))
        parts.append(rigid(wb, arm, f"wing.{n}"))
    # foice longa: cabo de ferro com anéis, lâmina curva larga com o fio em brasa
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr; perp = bd.cross(sd).normalized()
    w = [along("primitive_cylinder_add", black, g - bd*.55, g + bd*.95, .017, vertices=8),
         along("primitive_cone_add", black, g - bd*.55, g - bd*.68, 1, radius1=.02, radius2=0, vertices=5)]
    for k in range(4):
        r_ = prim("primitive_torus_add", iron, g + bd*(-.35 + .32*k), (1,1,1), major_radius=.021, minor_radius=.006)
        r_.rotation_euler = bd.to_track_quat('Z','Y').to_euler(); w.append(r_)
    top = g + bd*.95; w.append(prim("primitive_uv_sphere_add", bone, top, (.045,.04,.05)))
    pts = [top + (-perp*math.sin(a)*.62 + bd*(math.cos(a) - 1)*.35 + bd*.02) for a in [k*.14 for k in range(14)]]
    w.append(blade_mesh("foice", black, pts, [.035 + .06*math.sin(math.pi*k/13) if k < 13 else 0 for k in range(14)], sd, .012))
    wid = [.035 + .06*math.sin(math.pi*k/13) if k < 13 else 0 for k in range(14)]
    edge = []
    for i, p_ in enumerate(pts):  # fio de brasa na borda de fora da lâmina
        d_ = (pts[min(i+1, 13)] - pts[max(i-1, 0)]).normalized(); edge.append(p_ - d_.cross(sd).normalized()*wid[i])
    w += [along("primitive_cube_add", ember, edge[k], edge[k+1], .005) for k in range(1, 13)]
    parts.append(rigid(w, arm, "hand.R"))
    grow(arm, 1.03)
    info.update({"rim": (1, .22, .14), "base": "demonio"}); return arm, info

# ====================================================================== CULTISTA → ARQUIMAGO
def arquimago():
    """O que leu o livro inteiro: mitra de ferro e osso sobre o capuz, gola alta de placas, três auréolas de sangue,
    grimório acorrentado flutuando, orbes de sangue em órbita e um cajado com um coração preso numa gaiola de costelas."""
    arm, info = classes2.cultista()
    drop_named("cultista_hand.R")              # cajado antigo (o efeito "rajada" é refeito abaixo)
    for o in list(bpy.data.objects):
        if o.name.startswith("rajada"): bpy.data.objects.remove(o, do_unlink=True)
    blk = mat("capuz_negro", (.025,.024,.03)); ash = mat("manto_chumbo", (.2,.2,.22)); wine_d = mat("tunica_quase_preta", (.07,.02,.025))
    leather = mat("couro_negro_sangue", (.02,.018,.018)); metal = mat("metal_escurecido", (.12,.12,.13))
    bone = mat("chifre_escuro", (.3,.26,.2)); gem = mat("gema_sangue", (1,.05,.03)); blood = mat("sangue_magia", (.8,0,0))
    burst = mat("rajada_sangue", (1,.12,.04))
    vel = mat("veludo_vinho", (.16,.015,.02), 0, .6, dirt=.55, grime=.7)
    page = mat("pergaminho_sujo", (.5,.43,.32), 0, .9, dirt=.5, grime=.5)
    parts = []
    # sobremanto de veludo vinho até o chão, com cauda que arrasta atrás
    sm = skirt("sobremanto", vel, [(1.5,.2,.14,.01), (1.25,.27,.19,.03), (.9,.32,.23,.05), (.5,.36,.27,.08), (.03,.42,.32,.13)], open_front=.85, jag=.06, seed=51, folds=12, famp=.07)
    bind(sm, arm, ["chest","spine","hips","upper_arm.L","upper_arm.R"], power=3); parts.append(sm)
    # gola alta em leque de placas de osso e ferro
    gl = []
    for k in range(11):
        a = math.radians(-100 + k*20); d = Vector((math.sin(a), math.cos(a)*.8 + .1, 0))
        b = Vector((d.x*.15, d.y*.12 + .02, 1.49))
        gl.append(along("primitive_cone_add", bone if k % 2 else metal, b, b + Vector((d.x*.1, d.y*.08 + .04, .26 - abs(k - 5)*.012)), 1, radius1=.03, radius2=.004, vertices=4))
    gl.append(prim("primitive_torus_add", metal, (0,.01,1.49), (1,.9,1), major_radius=.15, minor_radius=.014))
    # orbes de sangue em órbita (o brilho da classe), cada um preso num anel de ferro
    for k in range(3):
        a = 2*math.pi*k/3 + .5; p = Vector((.34*math.cos(a), .25*math.sin(a) + .05, 1.25 + .12*math.sin(2*a)))
        gl.append(prim("primitive_uv_sphere_add", blood, p, (.032,.032,.032), segments=10, ring_count=6))
        gl.append(prim("primitive_torus_add", metal, p, (1,1,1), (60,0,math.degrees(a)), major_radius=.045, minor_radius=.004))
    parts.append(rigid(gl, arm, "chest"))
    for n in "LR":  # ombreiras de crânio cornudo
        s = 1 if n == "L" else -1; o, ax, up, sd = bone_frame(f"upper_arm.{n}")
        c = o + ax*.04 + Vector((0, 0, .07))
        pa = [prim("primitive_uv_sphere_add", bone, c, (.085,.09,.075)), prim("primitive_uv_sphere_add", metal, c + Vector((0,0,-.03)), (.1,.1,.04))]
        for e in (1, -1): pa.append(prim("primitive_uv_sphere_add", leather, c + Vector((.025*e, -.075, .0)), (.02,.012,.018)))
        pa.append(prim("primitive_uv_sphere_add", gem, c + Vector((0,-.08,-.025)), (.012,.006,.01)))
        pa += curve_tube(bone, bezier(c + Vector((.04*s,.0,.05)), c + Vector((.12*s,.02,.12)), c + Vector((.18*s,.06,.08)), c + Vector((.15*s,.1,.0)), 5), .022, .004, 6)
        parts.append(rigid(pa, arm, f"upper_arm.{n}"))
    # grimório acorrentado flutuando ao lado esquerdo do quadril
    bk_c = Vector((.36, -.02, 1.02))
    bk = [plate(leather, bk_c, (.07,.025,.09), (0,0,-25)), plate(page, bk_c + Vector((.005,-.0,0)), (.064,.018,.084), (0,0,-25)),
          prim("primitive_uv_sphere_add", gem, bk_c + Vector((-.012,-.03,0)), (.016,.008,.016), segments=8, ring_count=5)]
    for z in (-.06, .06): bk.append(prim("primitive_cube_add", metal, bk_c + Vector((0,0,z)), (.074,.03,.008), (0,0,-25)))
    bk += chain_links(metal, (.18,-.05,.98), bk_c + Vector((-.05,0,.02)), 7, sag=.04)
    parts.append(rigid(bk, arm, "hips"))
    # mitra de ferro e osso sobre o capuz e três auréolas de sangue em ângulos diferentes
    hd = [skirt("mitra", metal, [(1.9,.09,.085,.03), (2.02,.08,.075,.04), (2.14,.055,.05,.06), (2.22,.02,.02,.08)], open_front=0, thick=.01)]
    for k in range(7):
        a = math.radians(-90 + k*30); d = Vector((math.cos(a), math.sin(a), 0))
        b = Vector((0,.03,1.95)) + Vector((d.x*.085, d.y*.08, 0))
        hd.append(along("primitive_cone_add", bone, b, b + Vector((d.x*.03, d.y*.03, .17 - abs(k - 3)*.025)), 1, radius1=.016, radius2=0, vertices=4))
    hd.append(prim("primitive_uv_sphere_add", gem, (0,-.055,2.01), (.02,.01,.024), segments=8, ring_count=5))
    for r_, rx, rz in ((.2, 84, 0), (.25, 70, 28), (.3, 62, -32)):
        hd.append(prim("primitive_torus_add", blood, (0,.13,1.84), (1,1,1), (rx,0,rz), major_radius=r_, minor_radius=.007 if r_ > .2 else .012, major_segments=56, minor_segments=8))
    parts.append(rigid(hd, arm, "head"))
    # cajado de ferro negro, gaiola de costelas com coração de sangue e asas de osso no topo
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr; g = L(fr, .05)
    top = g + bd*.85; perp = bd.cross(sd).normalized()
    cz = [along("primitive_cylinder_add", blk, g - bd*.7, top, .026, vertices=8),
          along("primitive_cone_add", metal, g - bd*.7, g - bd*.8, 1, radius1=.03, radius2=0, vertices=6)]
    for k in range(3): cz.append(along("primitive_cylinder_add", metal, g + bd*(-.3 + .3*k), g + bd*(-.27 + .3*k), .032, vertices=8))
    cz.append(prim("primitive_uv_sphere_add", blood, top + bd*.12, (.06,.06,.07), segments=12, ring_count=8))
    for k in range(6):
        a = 2*math.pi*k/6; d = sd*math.cos(a) + perp*math.sin(a)
        cz += curve_tube(bone, [top + d*.02, top + bd*.06 + d*.09, top + bd*.18 + d*.08, top + bd*.27 + d*.015], .011, .006, 5)
    for s_ in (1, -1):
        for k in range(4):
            cz.append(along("primitive_cone_add", bone, top + bd*.1 + sd*.07*s_, top + bd*(.22 + .05*k) + sd*(.2 + .03*k)*s_ - perp*.02, 1, radius1=.015, radius2=0, vertices=4))
    parts.append(rigid(cz, arm, "hand.R"))
    c = top + bd*.12
    fx = rigid([prim("primitive_uv_sphere_add", burst, c, (.13,.13,.13)),
                along("primitive_cone_add", burst, c, c + bd*.6, 1, radius1=.13, radius2=0, vertices=8)], arm, "hand.R")
    fx.name = "rajada"; info["flash"] = fx
    grow(arm, 1.05)
    info.update({"rim": (.6, .08, .06), "base": "cultista"}); return arm, info

# ====================================================================== CULTISTA → PROFETA DO AMARGO
def profeta_do_amargo():
    """Quem bebeu do Rio Amargo e voltou pregando: o sangue virou o verde da radiação. Aniagem e avental de chumbo,
    coroa de arame farpado, máscara de chumbo com visor rachado, turíbulo de Amargo e o estilhaço verde da 'estrela'."""
    mat("gema_sangue", (.3,1,.2), emit=(.35,1,.2), strength=10)
    mat("sangue_magia", (.2,.8,.1), emit=(.3,1,.15), strength=12)
    mat("rajada_sangue", (.4,1,.2), emit=(.3,1,.15), strength=4)
    mat("manto_chumbo", (.3,.26,.18), 0, .85, dirt=.55, grime=.9)
    mat("tunica_quase_preta", (.09,.08,.05), 0, .8, dirt=.5, grime=.9)
    mat("capuz_negro", (.12,.1,.07), 0, .8, dirt=.5, grime=.7)
    arm, info = classes2.cultista()
    drop_named("cultista_head", "cultista_hand.R")
    for o in list(bpy.data.objects):
        if o.name.startswith("rajada"): bpy.data.objects.remove(o, do_unlink=True)
    blk = mat("capuz_negro", (.12,.1,.07)); metal = mat("metal_escurecido", (.12,.12,.13)); skin = mat("mao_seca", (.3,.26,.24))
    gem = mat("gema_sangue", (.3,1,.2)); amargo = mat("sangue_magia", (.2,.8,.1)); burst = mat("rajada_sangue", (.4,1,.2))
    leather = mat("couro_negro_sangue", (.02,.018,.018))
    lead = mat("chumbo_fosco", (.2,.21,.22), 1, .6, dirt=.55, grime=.4)
    rust = mat("ferrugem_arame", (.25,.1,.04), 1, .7, dirt=.6, grime=.3)
    glass = mat("vidro_sujo", (.15,.2,.15), 0, .15, dirt=.7, grime=.2)
    sack = mat("aniagem", (.36,.3,.2), 0, .95, dirt=.5, grime=1.1)
    wood = mat("madeira_velha", (.2,.14,.08), 0, .8, dirt=.5, grime=.5)
    parts = []
    # avental de chumbo em placas, com a estrela caída riscada em verde
    av = tabard("avental_chumbo", lead, 0, -.19, 1.42, .42, .1, seed=7)
    bind(av, arm, ["chest","spine","hips","thigh.L","thigh.R"], power=2); parts.append(av)
    ap = []
    for k in range(5):
        a = math.radians(90 + k*72); b = math.radians(90 + (k + 2)*72)
        ap.append(along("primitive_cube_add", gem, (.05*math.cos(a), -.205, 1.25 + .05*math.sin(a)), (.05*math.cos(b), -.205, 1.25 + .05*math.sin(b)), .004))
    ap += chain_links(metal, (-.13,-.2,1.4), (-.13,-.2,1.52), 4, sag=0) + chain_links(metal, (.13,-.2,1.4), (.13,-.2,1.52), 4, sag=0)
    parts.append(rigid(ap, arm, "chest"))
    # xale de aniagem sobre os ombros, rasgado
    xl = skirt("xale", sack, [(1.56,.14,.12,0), (1.44,.24,.17,.01), (1.24,.3,.21,.02), (1.08,.31,.22,.02)], open_front=.35, jag=.07, seed=61, folds=9, famp=.08)
    bind(xl, arm, ["chest","neck","upper_arm.L","upper_arm.R"], power=3); parts.append(xl)
    # tábua de profecia pendurada nas costas
    bk = [plate(wood, (0,.2,1.28), (.15,.012,.2), (-6,0,0))]
    for k in range(4): bk.append(prim("primitive_cube_add", gem if k == 1 else leather, (-.08 + .05*k, .214, 1.34 - .04*(k % 2)), (.018,.004,.05)))
    parts.append(rigid(bk, arm, "chest"))
    # cabeça: capuz de aniagem, máscara de chumbo com visor de vidro rachado, coroa de arame farpado, olhos verdes
    hd = [head_base(skin, (.07,.08,.095), z=1.68),
          cowl("capuz_profeta", blk, seed=6),
          plate(lead, (0,-.095,1.66), (.06,.02,.075)), prim("primitive_uv_sphere_add", glass, (0,-.12,1.69), (.055,.015,.06))]
    for s in (1, -1): hd.append(prim("primitive_uv_sphere_add", gem, (.024*s,-.126,1.7), (.011,.005,.008)))
    hd.append(along("primitive_cylinder_add", lead, (0,-.11,1.6), (0,-.17,1.55), .022, vertices=8))
    hd.append(prim("primitive_cylinder_add", metal, (0,-.175,1.545), (.032,.032,.02), (55,0,0), vertices=10))
    for k in range(3):
        hd.append(prim("primitive_torus_add", rust, (0,-.005,1.745 + .008*k), (1,1,1), (10 + 3*(k - 1), 2*k, 0), major_radius=.118 - .004*k, minor_radius=.005, major_segments=24, minor_segments=4))
    for k in range(14):
        a = 2*math.pi*k/14; d = Vector((math.cos(a), math.sin(a), 0))
        b = Vector((0,-.005,1.75 + .025*max(0, d.y))) + d*.118
        hd.append(along("primitive_cone_add", rust, b, b + d*.04 + Vector((0,0,.03 if k % 2 else -.01)), 1, radius1=.006, radius2=0, vertices=4))
    parts.append(rigid(hd, arm, "head"))
    # turíbulo de Amargo pendurado da mão esquerda: esfera de chumbo furada com brilho verde
    fl = bone_frame("hand.L"); c0 = L(fl, .06)
    tb = chain_links(metal, c0, L(fl, .32), 9, sag=0)
    tc = L(fl, .4, .0, .03)
    tb += [prim("primitive_uv_sphere_add", lead, tc, (.065,.065,.07), segments=14, ring_count=8),
           prim("primitive_torus_add", metal, tc, (1,1,1), major_radius=.068, minor_radius=.008)]
    for k in range(5):
        a = 2*math.pi*k/5 + .4; tb.append(prim("primitive_uv_sphere_add", amargo, tc + Vector((.06*math.cos(a), .06*math.sin(a), .015)), (.014,.014,.018)))
    tb.append(prim("primitive_cone_add", lead, tc + Vector((0,0,.08)), (.04,.04,.04), vertices=10))
    parts.append(rigid(tb, arm, "hand.L"))
    # cajado de cano torto amarrado com trapos e, no topo, o estilhaço verde da "estrela" preso em arame
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr; g = L(fr, .05); perp = bd.cross(sd).normalized()
    top = g + bd*.78
    cz = [along("primitive_cylinder_add", lead, g - bd*.66, g + bd*.1, .024, vertices=8),
          along("primitive_cylinder_add", lead, g + bd*.1, top + sd*.03, .021, vertices=8)]
    for k in range(3): cz.append(along("primitive_cylinder_add", sack, g + bd*(-.4 + .25*k), g + bd*(-.34 + .25*k), .03, vertices=8))
    rnd = random.Random(3)
    for k in range(6):
        d = (bd*rnd.uniform(.6, 1.2) + sd*rnd.uniform(-.6, .6) + perp*rnd.uniform(-.6, .6)).normalized()
        cz.append(along("primitive_cone_add", amargo, top + bd*.1, top + bd*.1 + d*rnd.uniform(.12, .2), 1, radius1=.035, radius2=0, vertices=4))
    cz.append(prim("primitive_ico_sphere_add", amargo, top + bd*.1, (.06,.06,.08), subdivisions=1))
    for k in range(5): cz.append(prim("primitive_torus_add", rust, top + bd*(.04 + .03*k), (1,1,1), (rnd.uniform(0, 90), rnd.uniform(0, 90), 0), major_radius=.05, minor_radius=.004))
    parts.append(rigid(cz, arm, "hand.R"))
    c = top + bd*.1
    fx = rigid([prim("primitive_uv_sphere_add", burst, c, (.12,.12,.12)),
                along("primitive_cone_add", burst, c, c + bd*.55, 1, radius1=.12, radius2=0, vertices=8)], arm, "hand.R")
    fx.name = "rajada"; info["flash"] = fx
    grow(arm, 1.04)
    info.update({"rim": (.3, .5, .2), "base": "cultista"}); return arm, info

# ====================================================================== HUMANO → PISTOLEIRO
def _revolver(n, iron, wood, brass, holy, long_=.4):
    """Revólver de cano longo na mão n, com o tambor de balas bentas (brilho azul da água benta)."""
    fr = bone_frame(f"hand.{n}", up=Vector((0, -1, 0))); o, ax, up, sd = fr; g = L(fr, .04)
    gp = [along("primitive_cylinder_add", iron, g + up*.045 - ax*.02, g + up*.045 + ax*long_, .017, vertices=10),
          along("primitive_cube_add", iron, g + up*.06 - ax*.02, g + up*.06 + ax*long_, .005),
          along("primitive_cylinder_add", iron, g + up*.04 - ax*.06, g + up*.04 - ax*.0, .034, vertices=12),
          along("primitive_cube_add", iron, g + up*.035 - ax*.1, g + up*.035 - ax*.06, .024),
          along("primitive_cube_add", wood, g + up*.02 - ax*.1, g - up*.06 - ax*.15, .021),
          prim("primitive_uv_sphere_add", brass, g - up*.07 - ax*.155, (.016,.016,.016)),
          along("primitive_cone_add", brass, g + up*.07 - ax*.09, g + up*.09 - ax*.12, 1, radius1=.008, radius2=0, vertices=4)]
    for k in range(6):
        a = 2*math.pi*k/6; d = up*math.cos(a)*.017 + sd*math.sin(a)*.017
        gp.append(along("primitive_cylinder_add", holy, g + up*.04 + d - ax*.061, g + up*.04 + d - ax*.064, .006, vertices=6))
    gp.append(prim("primitive_torus_add", brass, g - up*.0 - ax*.03, (1,1,1), major_radius=.02, minor_radius=.004))
    return gp, g + up*.045 + ax*long_, ax

def pistoleiro():
    """A mão mais rápida da Vigília: guarda-pó longo até a bota com capa curta nos ombros, dois revólveres de cano longo
    com balas bentas, cartucheiras cruzadas, rifle de alavanca nas costas e chapéu de aba larga com cordão de dentes de anjo."""
    mat("guarda_po", (.07,.055,.045), 0, .7, dirt=.5, grime=.9)
    arm, info = classes.humano()
    drop_named("humano_hand.R", "humano_hand.L", "humano_chest", "poncho", "clarao", "rastro", "corte_dash")
    duster = mat("guarda_po", (.07,.055,.045)); leather = mat("couro_velho", (.15,.085,.05)); leather2 = mat("couro_capa", (.09,.045,.025))
    dark = mat("couro_escuro", (.03,.022,.017)); brass = mat("latao", (.55,.29,.08)); iron = mat("ferro_gasto", (.12,.12,.12))
    wood = mat("madeira_coronha", (.16,.065,.025)); shell = mat("cartucho", (.42,.06,.03)); holy = mat("agua_benta", (.55,.8,1))
    steel = mat("azul_aco", (.15,.27,.42)); bone = mat("dente_anjo", (.6,.55,.45), 0, .5, dirt=.5, grime=.3)
    parts = []
    # guarda-pó comprido até o chão, aberto, e capa curta de ombro (pelerine) azul aço da Vigília
    sk = skirt("guarda_po_longo", duster, [(1.05,.17,.13,0), (.8,.23,.18,.01), (.55,.28,.21,.025), (.3,.31,.24,.035), (.06,.34,.27,.05)], open_front=.55, jag=.08, seed=15, folds=11, famp=.08)
    bind(sk, arm, ["hips","spine","thigh.L","thigh.R"], power=3); parts.append(sk)
    pe = skirt("pelerine", mat("lona_azul_noite", (.035,.055,.085), 0, .8, dirt=.55, grime=.7), [(1.56,.11,.1,0), (1.48,.24,.18,.0), (1.36,.31,.23,.01), (1.24,.34,.25,.015)], open_front=.45, jag=.05, seed=17, folds=8, famp=.06)
    bind(pe, arm, ["chest","neck","upper_arm.L","upper_arm.R"], power=3); parts.append(pe)
    # cartucheiras cruzadas no peito e rifle de alavanca nas costas
    ch = []
    for s in (1, -1):
        a, b = Vector((.17*s,-.15,1.47)), Vector((-.14*s,-.17,1.02))
        ch.append(along("primitive_cube_add", dark, a, b, .026))
        for k in range(10):
            p_ = a.lerp(b, .08 + .085*k) + Vector((0,-.02,0))
            ch.append(along("primitive_cylinder_add", shell, p_, p_ + Vector((0,-.02,0)), .008, vertices=6))
            ch.append(along("primitive_cylinder_add", brass, p_ + Vector((0,-.02,0)), p_ + Vector((0,-.026,0)), .0085, vertices=6))
    ra, rb = Vector((-.22,.29,1.62)), Vector((.18,.28,.92))
    ch.append(along("primitive_cylinder_add", iron, ra, ra.lerp(rb, .62), .014, vertices=8))
    ch.append(along("primitive_cube_add", iron, ra.lerp(rb, .5), ra.lerp(rb, .66), .024))
    ch.append(along("primitive_cube_add", wood, ra.lerp(rb, .4), ra.lerp(rb, .5), .02))
    ch.append(along("primitive_cube_add", wood, ra.lerp(rb, .66), rb, .03))
    ch.append(prim("primitive_torus_add", brass, ra.lerp(rb, .66) + Vector((0,0,-.04)), (1,1,1), major_radius=.03, minor_radius=.005))
    ch.append(along("primitive_cylinder_add", brass, ra.lerp(rb, .3) + Vector((0,.03,.0)), ra.lerp(rb, .5) + Vector((0,.03,0)), .012, vertices=10))  # luneta
    ch.append(along("primitive_cube_add", leather2, (.15,.16,1.45), (-.1,.3,1.0), .012))
    parts.append(rigid(ch, arm, "chest"))
    # dois coldres na cintura
    hp = []
    for s in (1, -1):
        hp.append(along("primitive_cube_add", leather2, (.2*s,-.05,.96), (.22*s,-.07,.74), .036))
        hp.append(prim("primitive_uv_sphere_add", brass, (.21*s,-.09,.88), (.012,.006,.012)))
    parts.append(rigid(hp, arm, "hips"))
    # cordão de dentes de anjo no chapéu e lenço azul cobrindo o rosto
    hd = []
    for k in range(13):
        a = math.radians(-20 + k*16); p_ = Vector((.112*math.sin(a), -.012 - .112*math.cos(a)*-1, 1.83))
        p_ = Vector((.113*math.cos(math.radians(k*27.7)), .113*math.sin(math.radians(k*27.7)), 1.835))
        hd.append(along("primitive_cone_add", bone, p_, p_ + Vector((0,0,-.03)), 1, radius1=.008, radius2=0, vertices=4))
    hd.append(prim("primitive_torus_add", dark, (0,0,1.84), (1,1,1), major_radius=.113, minor_radius=.006))
    hd.append(skirt("lenco_rosto", mat("lona_azul_noite", (.035,.055,.085)), [(1.66,.083,.093,-.01), (1.6,.09,.1,-.01), (1.54,.1,.1,-.02)], open_front=0, thick=.006))
    parts.append(rigid(hd, arm, "head"))
    for n in "LR":
        gp, muzzle, ax = _revolver(n, iron, wood, brass, holy)
        parts.append(rigid(gp, arm, f"hand.{n}"))
    flash = mat("clarao", (1,.8,.4), emit=(1,.7,.3), strength=25)
    gp, muzzle, ax = _revolver("L", iron, wood, brass, holy)
    for o_ in gp: bpy.data.objects.remove(o_, do_unlink=True)
    flo = rigid([along("primitive_cone_add", flash, muzzle, muzzle + ax*.3, 1, radius1=.09, radius2=0, vertices=8),
                 prim("primitive_uv_sphere_add", flash, muzzle + ax*.03, (.07,.07,.07))], arm, "hand.L"); flo.name = "clarao"
    grow(arm, 1.03)
    info = {"rim": (.6, .75, 1), "anim": "gun", "flash": flo, "base": "humano"}
    return arm, info

# ====================================================================== HUMANO → CAÇADOR DE ANJOS
def cacador_de_anjos():
    """Quem caça o que caiu do céu: casaco de couro remendado, um par de asas de anjo cortadas amarrado nas costas como troféu,
    máscara de porcelana tirada de um anjo, halos quebrados no cinto e um arpão de corrente com farpas de água benta."""
    mat("guarda_po", (.11,.075,.05), 0, .65, dirt=.55, grime=.9)
    mat("poncho_la", (.08,.07,.06), 0, .9, dirt=.55, grime=.6)
    arm, info = classes.humano()
    drop_named("humano_hand.R", "humano_chest", "rastro", "corte_dash", "humano_head", "poncho")
    duster = mat("guarda_po", (.11,.075,.05)); leather = mat("couro_velho", (.15,.085,.05)); leather2 = mat("couro_capa", (.09,.045,.025))
    dark = mat("couro_escuro", (.03,.022,.017)); brass = mat("latao", (.55,.29,.08)); iron = mat("ferro_gasto", (.12,.12,.12))
    wood = mat("madeira_coronha", (.16,.065,.025)); holy = mat("agua_benta", (.55,.8,1)); felt = mat("feltro_chapeu", (.055,.04,.03))
    hairm = mat("cabelo", (.03,.025,.02)); skin = mat("pele_suja", (.36,.22,.15))
    porcelain = mat("porcelana", (.68,.65,.6), 0, .2, dirt=.8, grime=.2)
    f_light = mat("pena_suja", (.55,.52,.45), 0, .85, dirt=.45, grime=.7); f_dark = mat("pena_gasta", (.34,.31,.27), 0, .9, dirt=.45, grime=.6)
    blood = mat("sangue_seco", (.2,.02,.01), 0, .6, dirt=.6, grime=.4)
    gold = mat("ouro_sujo", (.6,.36,.08), 1, .4, dirt=.55, grime=.3)
    parts = []
    # asas de anjo cortadas, dobradas e amarradas nas costas com correias (troféu); sangue seco no corte
    for side in (1, -1):
        w_ = wing(arm, side, f_light, f_dark, dark, iron)
        n = "L" if side > 0 else "R"; root = P(f"wing.{n}")
        for vg in list(w_.vertex_groups): w_.vertex_groups.remove(vg)
        xform(w_, rot('Y', 38*side) @ rot('X', 10) @ scl(.95), root); xform(w_, Matrix.Translation((-.05*side, .05, -.1)), (0,0,0))
        g_ = w_.vertex_groups.new(name="chest"); g_.add(list(range(len(w_.data.vertices))), 1.0, 'REPLACE')
        parts.append(w_)
    ch = [prim("primitive_uv_sphere_add", blood, (0,.17,1.42), (.1,.04,.05))]
    for z in (1.42, 1.2):
        ch.append(along("primitive_cube_add", dark, (.24,.26,z), (-.24,.26,z), .02))
        ch.append(prim("primitive_cube_add", brass, (0,.28,z), (.025,.008,.02)))
    for s in (1, -1): ch.append(along("primitive_cube_add", dark, (.16*s,-.14,1.46), (.24*s,.25,1.42), .02))
    # colar de penas no pescoço e placa de couro rebitada no peito
    for k in range(16):
        a = math.radians(-160 + k*21); d = Vector((math.cos(a), math.sin(a), 0))
        b = Vector((0,0,1.5)) + d*.12
        ch.append(along("primitive_cone_add", f_light if k % 2 else f_dark, b, b + d*.12 + Vector((0,0,-.06)), 1, radius1=.035, radius2=0, vertices=3))
    ch.append(plate(leather2, (0,-.13,1.33), (.11,.025,.1), (6,0,0)))
    for k in range(6): ch.append(prim("primitive_uv_sphere_add", brass, (-.08 + .032*k, -.158, 1.42), (.008,.008,.008), segments=6, ring_count=4))
    parts.append(rigid(ch, arm, "chest"))
    # halos quebrados e uma máscara de porcelana pendurados no cinto
    hp = []
    for k, (x, y) in enumerate(((.2,-.02), (-.19,-.06))):
        hp.append(prim("primitive_torus_add", gold, (x, y, .86), (1,1,1), (90, 0, 20*k), major_radius=.05, minor_radius=.006))
    hp.append(prim("primitive_uv_sphere_add", porcelain, (-.1,-.17,.86), (.045,.02,.055)))
    for s in (1, -1): hp.append(prim("primitive_uv_sphere_add", dark, (-.1 + .017*s,-.188,.87), (.009,.004,.006)))
    parts.append(rigid(hp, arm, "hips"))
    # cabeça: meia-máscara de porcelana de anjo (rachada) sobre a boca, chapéu de aba larga com pena de anjo
    hd = [prim("primitive_uv_sphere_add", skin, (0,-.012,1.67), (.08,.09,.105)),
          prim("primitive_uv_sphere_add", porcelain, (0,-.04,1.62), (.075,.07,.06)),
          prim("primitive_cube_add", dark, (.02,-.105,1.62), (.003,.003,.03)),
          prim("primitive_cube_add", dark, (0,-.094,1.695), (.058,.008,.012))]
    for s in (1, -1): hd.append(prim("primitive_uv_sphere_add", holy, (.032*s,-.092,1.69), (.008,.004,.005)))
    hd += [skirt("chapeu_copa", felt, [(1.79,.105,.1,0), (1.88,.1,.095,.0), (1.94,.085,.08,.0), (1.95,.0,.0,.0)], open_front=0, thick=.01)]
    brim = skirt("chapeu_aba", felt, [(1.79,.105,.1,0), (1.78,.2,.19,0), (1.8,.27,.25,0)], open_front=0, thick=.012, folds=5, famp=.05, seed=3)
    hd.append(brim)
    hd.append(prim("primitive_torus_add", dark, (0,0,1.8), (1,.95,1), major_radius=.107, minor_radius=.012))
    hd += curve_tube(f_light, [Vector((.09,.03,1.81)), Vector((.15,.08,1.9)), Vector((.17,.16,1.98))], .018, .003, 5)
    for k in range(10):
        a = math.radians(70 + k*22); b = Vector((.085*math.cos(a), .085*math.sin(a) + .01, 1.72))
        hd.append(along("primitive_cone_add", hairm, b, b + Vector((math.cos(a)*.03, math.sin(a)*.04 + .02, -.18)), 1, radius1=.025, radius2=0, vertices=5))
    parts.append(rigid(hd, arm, "head"))
    # arpão de corrente: haste de ferro, ponta farpada com runas de água benta, corrente enrolada no braço
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr; perp = bd.cross(sd).normalized()
    top = g + bd*1.05
    w = [along("primitive_cylinder_add", wood, g - bd*.45, g + bd*.45, .019, vertices=8),
         along("primitive_cylinder_add", iron, g + bd*.45, top, .016, vertices=8),
         along("primitive_cone_add", iron, top, top + bd*.24, 1, radius1=.045, radius2=0, vertices=4)]
    for s_ in (1, -1):
        w.append(along("primitive_cone_add", iron, top + bd*.06, top - bd*.1 + sd*.07*s_, 1, radius1=.018, radius2=0, vertices=4))
        w.append(along("primitive_cone_add", iron, top + bd*.0, top - bd*.12 + perp*.06*s_, 1, radius1=.014, radius2=0, vertices=4))
    for k in range(3): w.append(along("primitive_cube_add", holy, top + bd*(.03 + .05*k) + sd*.002, top + bd*(.05 + .05*k) + sd*.002, .02))
    for k in range(3): w.append(prim("primitive_torus_add", brass, g + bd*(-.3 + .3*k), (1,1,1), major_radius=.024, minor_radius=.005))
    w += chain_links(iron, top - bd*.05, g + bd*.05 + sd*.05, 14, sag=.12)
    parts.append(rigid(w, arm, "hand.R"))
    grow(arm, 1.04)
    info.update({"rim": (.55, .7, 1), "base": "humano"})
    info["fx"] = []
    return arm, info

# ====================================================================== MUTANTE → GLADIADOR
def gladiador():
    """Campeão das arenas de sucata: elmo-balde com grade e crista de ossos, ombreira grande de placa de bonde, escudo de
    vela de bonde-veleiro rebitada no braço mutado, saiote de correntes e um machado de carrasco no braço bom."""
    arm, info = classes3.mutante()
    drop_named("mutante_head", "mutante_hand.R")
    bone = mat("osso_quitina", (.46,.41,.32)); canvas = mat("lona_azul_aco", (.05,.09,.15)); leather = mat("couro_correia", (.13,.07,.04))
    dark = mat("couro_escuro", (.03,.022,.017)); iron = mat("ferro_velho", (.1,.095,.09)); rust = mat("placa_ferrugem", (.2,.09,.04))
    brass = mat("latao_velho", (.5,.27,.07)); sign = mat("placa_amarela", (.6,.45,.05)); steel = mat("fio_afiado", (.5,.5,.5))
    acid = mat("verde_acido", (.3,1,.1)); skin = mat("pele_cinza_doente", (.2,.18,.14))
    sail = mat("lona_vela_bonde", (.3,.26,.2), 0, .9, dirt=.5, grime=.8)
    parts = []
    # elmo-balde de ferro com grade na frente, crista de ossos e olhos de ácido atrás da grade
    hd = [head_base(skin, (.082,.092,.1), z=1.66),
          skirt("elmo_balde", iron, [(1.56,.105,.11,0), (1.66,.11,.115,0), (1.76,.108,.112,0), (1.8,.09,.095,0), (1.82,.0,.0,0)], open_front=0, thick=.014),
          prim("primitive_torus_add", rust, (0,0,1.765), (1,1.04,1), major_radius=.11, minor_radius=.012)]
    for k in range(5): hd.append(along("primitive_cube_add", dark, (-.05 + .025*k,-.118,1.6), (-.05 + .025*k,-.118,1.72), .005))
    for z in (1.64, 1.69): hd.append(along("primitive_cube_add", dark, (-.06,-.118,z), (.06,-.118,z), .005))
    for s in (1, -1): hd.append(prim("primitive_uv_sphere_add", acid, (.032*s,-.1,1.69), (.013,.006,.009)))
    for k in range(7):
        b = Vector((0, -.08 + .03*k, 1.8)); hd += curve_tube(bone, [b, b + Vector((0, .03, .12 - abs(k - 3)*.02))], .02, .004, 5)
    for k in range(10):
        a = 2*math.pi*k/10; hd.append(prim("primitive_uv_sphere_add", brass, (.11*math.cos(a), .115*math.sin(a), 1.62), (.01,.01,.01), segments=6, ring_count=4))
    parts.append(rigid(hd, arm, "head"))
    # ombreira grande de placa (amarela de sinal antigo) no braço bom, com correntes
    o, ax, up, sd = bone_frame("upper_arm.R"); pa = []
    for i in range(3):
        c = o + ax*(.0 + .05*i) + Vector((0, 0, .07 - .02*i))
        e = prim("primitive_uv_sphere_add", rust if i != 1 else iron, c, (.17 - .02*i, .16 - .015*i, .07), segments=16, ring_count=8)
        e.rotation_euler = (0, math.radians(32), 0); pa.append(e)
        pa.append(prim("primitive_torus_add", iron, c + Vector((0,0,-.015)), (1,1,1), (0,32,0), major_radius=.16 - .02*i, minor_radius=.01, major_segments=20, minor_segments=4))
    for k in range(4): pa.append(along("primitive_cube_add", sign, o + Vector((-.1 + .05*k, -.12, .06)), o + Vector((-.07 + .05*k, -.1, .14)), .012))
    parts.append(rigid(pa, arm, "upper_arm.R"))
    # escudo redondo grande feito de vela de bonde-veleiro esticada num aro de trilho, preso ao braço mutado
    o, ax, up, sd = bone_frame("forearm.L"); c = o + ax*.1 + Vector((.18, -.06, .0))
    nrm = Vector((.85, -.5, .1)).normalized()
    sh = [prim("primitive_cylinder_add", sail, c, (.36,.36,.02), vertices=32), prim("primitive_torus_add", rust, c, (1,1,1), major_radius=.36, minor_radius=.03, major_segments=32, minor_segments=6)]
    for o_ in sh: o_.rotation_euler = nrm.to_track_quat('Z','Y').to_euler()
    q = nrm.to_track_quat('Z','Y').to_matrix()
    for k in range(8):
        a = 2*math.pi*k/8; d = q @ Vector((math.cos(a), math.sin(a), 0))
        sh.append(along("primitive_cube_add", leather, c + d*.05 + nrm*.02, c + d*.34 + nrm*.02, .012))
    sh.append(prim("primitive_uv_sphere_add", iron, c + nrm*.03, (.09,.09,.09)))
    sh.append(along("primitive_cone_add", iron, c + nrm*.08, c + nrm*.22, 1, radius1=.05, radius2=0, vertices=8))
    sh.append(prim("primitive_uv_sphere_add", acid, c + nrm*.11, (.02,.02,.02)))
    parts.append(rigid(sh, arm, "forearm.L"))
    # saiote de correntes sobre o kilt e cinturão de campeão com fivela grande
    hp = [prim("primitive_torus_add", dark, (0,0,1.0), (1.18,.98,2.2), major_radius=.2, minor_radius=.024), plate(brass, (0,-.235,1.0), (.07,.015,.05))]
    hp.append(prim("primitive_uv_sphere_add", acid, (0,-.252,1.0), (.018,.006,.018)))
    for k in range(13):
        a = math.radians(-150 + k*20); p0 = Vector((.24*math.cos(a), .21*math.sin(a), .98))
        hp += chain_links(iron, p0, p0 + Vector((math.cos(a)*.04, math.sin(a)*.04, -.3)), 7, sag=0)
    parts.append(rigid(hp, arm, "hips"))
    # machado de carrasco: cabo longo, lâmina larga em meia-lua com fio claro
    fr, bd, g = weapon_frame(); o, ax, up, sd = fr; perp = bd.cross(sd).normalized()
    w = [along("primitive_cylinder_add", leather, g - bd*.25, g + bd*.85, .022, vertices=10),
         along("primitive_cone_add", iron, g - bd*.25, g - bd*.36, 1, radius1=.03, radius2=0, vertices=6)]
    for k in range(4): w.append(prim("primitive_torus_add", iron, g + bd*(-.1 + .24*k), (1,1,1), major_radius=.027, minor_radius=.007))
    hc = g + bd*.72
    pts = [hc + bd*(.18*math.cos(a)) + perp*(.05 + .26*math.sin(a)*0 + 0) for a in [0]]
    prof = [(-.2, .02), (-.12, .2), (0, .26), (.12, .2), (.2, .02)]
    bm = bmesh.new(); vs = [bm.verts.new(hc + bd*z + perp*x*0 + sd*0 - perp*(.0) + perp*0) for z, x in [(-.06,0)]]
    bm.free()
    blade = []
    for (z0, x0), (z1, x1) in zip(prof[:-1], prof[1:]):
        bm = bmesh.new()
        a, b, c_, d_ = hc + bd*z0, hc + bd*z0 - perp*(.04 + x0), hc + bd*z1 - perp*(.04 + x1), hc + bd*z1
        bm.faces.new([bm.verts.new(v) for v in (a, b, c_, d_)])
        ob = obj_from_bm("lamina_machado", bm, iron); ob.modifiers.new("s", 'SOLIDIFY').thickness = .02; _apply_mods(ob); blade.append(ob)
        blade.append(along("primitive_cube_add", steel, b - perp*.005, c_ - perp*.005, .007))
    w += blade
    w.append(along("primitive_cone_add", iron, hc + perp*.03, hc + perp*.15, 1, radius1=.03, radius2=0, vertices=5))
    parts.append(rigid(w, arm, "hand.R"))
    grow(arm, 1.08)
    info.update({"base": "mutante"}); return arm, info

# ====================================================================== MUTANTE → ABOMINAÇÃO
def abominacao():
    """O Amargo venceu: o corpo inteiro cresceu, a coluna virou uma serra de ossos, um segundo braço nasce do peito, sacos de
    ácido verde pulsam nas costas, a cabeça tem seis olhos e o braço direito virou uma lâmina de osso."""
    mat("pele_cinza_doente", (.17,.16,.12), 0, .5, dirt=.6, grime=.5)
    arm, info = classes3.mutante()
    drop_named("mutante_hand.R", "mutante_head")
    skin = mat("pele_cinza_doente", (.17,.16,.12)); bruise = mat("pele_roxa", (.1,.06,.07)); flesh = mat("carne_mutada", (.22,.075,.06))
    bone = mat("osso_quitina", (.46,.41,.32)); iron = mat("ferro_velho", (.1,.095,.09)); rust = mat("placa_ferrugem", (.2,.09,.04))
    dark = mat("couro_escuro", (.03,.022,.017)); acid = mat("verde_acido", (.3,1,.1)); leather = mat("couro_correia", (.13,.07,.04))
    parts = []
    rnd = random.Random(21)
    # serra de ossos ao longo das costas e sacos de ácido brilhando
    ch = []
    for k in range(9):
        b = Vector((rnd.uniform(-.06, .06), .2 + .02*k, 1.55 - .07*k)); h = .32 - .025*k
        ch += curve_tube(bone, [b, b + Vector((0, .1, .08))*h/.25, b + Vector((rnd.uniform(-.05,.05), .22, .24))*h/.3], .034 - .002*k, .006, 6)
    for k in range(4):
        c = Vector((rnd.choice((-1, 1))*rnd.uniform(.08, .16), .22, rnd.uniform(1.1, 1.45)))
        ch.append(prim("primitive_uv_sphere_add", flesh, c, (.1,.08,.1), segments=12, ring_count=8))
        ch.append(prim("primitive_uv_sphere_add", acid, c + Vector((0,.045,0)), (.085,.06,.085), segments=12, ring_count=8))
        ch += curve_tube(bruise, [c + Vector((0,.0,.07)), c + Vector((.04,-.03,.14))], .012, .006, 5)
    # segundo braço pequeno, de carne crua, nascendo do lado direito do peito, com garras
    a0 = Vector((-.15,-.12,1.32)); a1 = Vector((-.3,-.25,1.2)); a2 = Vector((-.35,-.32,1.0))
    ch += curve_tube(flesh, [a0, a1, a2], .055, .035, 8)
    for k in range(3): ch.append(along("primitive_cone_add", bone, a2 + Vector((.02*(k-1),0,0)), a2 + Vector((.03*(k-1), -.07, -.1)), 1, radius1=.014, radius2=0, vertices=5))
    for k in range(6):
        ch.append(prim("primitive_uv_sphere_add", acid if k % 2 else bruise, (rnd.uniform(-.2, .2), -.21, rnd.uniform(1.05, 1.45)), (.02,.02,.02), segments=8, ring_count=5))
    parts.append(rigid(ch, arm, "chest"))
    # cabeça afundada nos ombros: mandíbula partida, seis olhos verdes, chifres de osso e respirador arrancado pendurado
    hd = [head_base(skin, (.095,.1,.1), z=1.64), prim("primitive_uv_sphere_add", bruise, (-.05,.02,1.71), (.07,.07,.06)),
          prim("primitive_uv_sphere_add", flesh, (0,-.07,1.57), (.07,.06,.04))]
    for s in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", flesh, (.05*s,-.1,1.56), (.03,.03,.035)))
        hd.append(along("primitive_cone_add", bone, (.04*s,-.11,1.58), (.05*s,-.13,1.5), 1, radius1=.012, radius2=0, vertices=5))
    for x, z in ((-.035,1.67), (.035,1.67), (-.06,1.7), (.06,1.7), (-.02,1.715), (.025,1.72)):
        hd.append(prim("primitive_uv_sphere_add", acid, (x,-.095 + abs(x)*.3,z), (.011,.007,.009)))
    for s in (1, -1):
        hd += curve_tube(bone, bezier((.06*s,.0,1.72), (.14*s,-.02,1.78), (.2*s,.03,1.86), (.17*s,.1,1.92), 5), .03, .005, 7)
    hd.append(along("primitive_cylinder_add", iron, (.06,-.08,1.52), (.09,-.1,1.42), .035, vertices=12))
    parts.append(rigid(hd, arm, "head"))
    # braço direito: o antebraço virou uma lâmina longa de osso serrilhado, pele rasgada na base
    o, ax, up, sd = bone_frame("forearm.R"); ln = (P("forearm.R", 1) - P("forearm.R")).length
    base_ = o + ax*ln*.6; tip = o + ax*(ln + .85) + Vector((0, -.08, 0))
    fa = [prim("primitive_uv_sphere_add", flesh, base_, (.09,.09,.1)),
          along("primitive_cone_add", bone, base_, tip, 1, radius1=1, radius2=0, vertices=5)]
    fa[-1].scale = (.11, .035, (tip - base_).length/2)
    for k in range(7):
        p_ = base_.lerp(tip, .12 + .11*k)
        fa.append(along("primitive_cone_add", bone, p_, p_ + up*.05*(1 - k/9) - ax*.03, 1, radius1=.014, radius2=0, vertices=4))
    for k in range(2):
        pts = [base_.lerp(tip, t) + sd*.02*(1 - 2*k) for t in (.0, .2, .4, .55)]
        fa += curve_tube(acid, pts, .005, .002, 5)
    parts.append(rigid(fa, arm, "forearm.R"))
    for o_ in [o_ for o_ in bpy.data.objects if o_.name.startswith("mutante_hand.R")]: bpy.data.objects.remove(o_, do_unlink=True)
    # braço mutado esquerdo ainda maior
    for o_ in [o_ for o_ in bpy.data.objects if o_.name.startswith(("mutante_forearm.L", "mutante_hand.L", "braco.L"))]:
        xform(o_, scl(1.15), P("forearm.L"))
    grow(arm, 1.16)
    info.update({"base": "mutante"}); return arm, info

# ====================================================================== TECNOMANCER → MECHANICUS
def _servo_arm(m_a, m_b, m_c, base_, pts, tool):
    """Braço mecânico extra saindo da caldeira: segmentos de latão, juntas de ferro e a ferramenta na ponta."""
    out = []; prev = Vector(base_)
    for i, p in enumerate(pts):
        p = Vector(p)
        out.append(along("primitive_cylinder_add", m_a, prev, p, .02 - .003*i, vertices=10))
        out.append(prim("primitive_uv_sphere_add", m_b, p, (.032 - .004*i,)*3, segments=10, ring_count=6))
        out.append(along("primitive_cylinder_add", m_b, prev.lerp(p, .2), prev.lerp(p, .6), .006, vertices=6))
        prev = p
    d = (Vector(pts[-1]) - Vector(pts[-2])).normalized()
    if tool == "garra":
        for k in (-1, 0, 1):
            side = d.cross(Vector((0, 0, 1))).normalized()
            out += curve_tube(m_a, [prev, prev + d*.06 + side*.03*k, prev + d*.11 + side*.015*k - Vector((0,0,.02))], .01, .002, 5)
    else:  # maçarico com chama laranja
        out.append(along("primitive_cylinder_add", m_b, prev, prev + d*.08, .012, vertices=8))
        out.append(along("primitive_cone_add", m_c, prev + d*.08, prev + d*.17, 1, radius1=.018, radius2=0, vertices=8))
    return out

def mechanicus():
    """Sacerdote da Máquina da Vigília: capuz de lona com máscara de latão de três lentes, caldeira-relicário maior com tubos
    de órgão, dois braços mecânicos saindo das costas (garra e maçarico) e um cajado de engrenagem com a lanterna rúnica dentro."""
    arm, info = classes2.tecnomancer()
    drop_named("tecnomancer_head", "tecnomancer_hand.R")
    for o_ in list(bpy.data.objects):
        if o_.name.startswith("raio"): bpy.data.objects.remove(o_, do_unlink=True)
    coat = mat("azul_aco_casaco", (.12,.2,.3)); dark = mat("couro_escuro", (.03,.022,.017)); brass = mat("latao_debrum", (.55,.3,.08))
    copper = mat("cobre", (.45,.16,.06)); iron = mat("ferro_velho", (.1,.095,.09)); rune = mat("runa_laranja", (1,.5,.1))
    arc = mat("arco_eletrico", (.6,.85,1)); bolt = mat("raio", (.7,.9,1)); skin = mat("pele_suja", (.36,.22,.15))
    canvas = mat("lona_capuz", (.1,.13,.17), 0, .85, dirt=.55, grime=.6)
    parts = []
    # tubos de órgão saindo da caldeira e dois braços mecânicos
    ch = []
    for k in range(5):
        x = -.12 + .06*k; h = .32 + .1*(2 - abs(k - 2))
        ch.append(along("primitive_cylinder_add", brass, (x,.33,1.42), (x,.35,1.42 + h), .018, vertices=10))
        ch.append(along("primitive_cone_add", brass, (x,.35,1.42 + h), (x,.355,1.46 + h), 1, radius1=.026, radius2=.018, vertices=10))
        ch.append(prim("primitive_uv_sphere_add", iron, (x,.335,1.42 + h*.5), (.022,.022,.012)))
    ch.append(prim("primitive_cylinder_add", copper, (0,.33,1.42), (.17,.06,.04), vertices=16))
    ch += _servo_arm(brass, iron, rune, (.14,.3,1.45), [(.32,.25,1.62), (.48,.05,1.6), (.52,-.12,1.45)], "garra")
    ch += _servo_arm(brass, iron, rune, (-.14,.3,1.45), [(-.34,.24,1.66), (-.5,.02,1.58), (-.46,-.15,1.42)], "macarico")
    # estola de lona com rebites e o sigilo da engrenagem bordado
    for s in (1, -1): ch.append(along("primitive_cube_add", canvas, (.08*s,-.16,1.48), (.09*s,-.2,1.02), .028))
    parts.append(rigid(ch, arm, "chest"))
    tb = tabard("estola_mech", canvas, 0, -.2, 1.0, .35, .08, seed=11); bind(tb, arm, ["hips","thigh.L","thigh.R"], power=2); parts.append(tb)
    gc = Vector((0,-.215,.8))
    parts.append(rigid([prim("primitive_cylinder_add", brass, gc, (.05,.05,.008), (90,0,0), vertices=16)] +
                       [prim("primitive_cube_add", brass, gc + Vector((math.cos(k*math.pi/4)*.058, 0, math.sin(k*math.pi/4)*.058)), (.01,.006,.01)) for k in range(8)] +
                       [prim("primitive_cylinder_add", rune, gc + Vector((0,-.008,0)), (.018,.018,.004), (90,0,0), vertices=10)], arm, "hips"))
    # cabeça: capuz de lona, máscara de latão com três lentes laranja, tubos até a caldeira
    hd = [head_base(skin),
          cowl("capuz_mech", canvas, seed=11),
          plate(brass, (0,-.09,1.66), (.06,.03,.075))]
    for x, z, r in ((-.03,1.69,.018), (.03,1.69,.018), (0,1.635,.013)):
        hd.append(along("primitive_cylinder_add", iron, (x,-.115,z), (x,-.14,z), r + .006, vertices=12))
        hd.append(along("primitive_cylinder_add", rune, (x,-.139,z), (x,-.143,z), r, vertices=12))
    for s in (1, -1): hd += curve_tube(dark, [Vector((.04*s,-.11,1.6)), Vector((.08*s,-.06,1.52)), Vector((.12*s,.1,1.46)), Vector((.1*s,.22,1.45))], .012, .012, 6)
    hd.append(along("primitive_cylinder_add", iron, (0,-.11,1.6), (0,-.14,1.57), .022, vertices=8))
    parts.append(rigid(hd, arm, "head"))
    # cajado de engrenagem: haste de ferro, engrenagem grande de latão com a lanterna rúnica no centro
    fr = bone_frame("hand.R"); o, ax, up, sd = fr; g = L(fr, .045)
    st = [along("primitive_cylinder_add", iron, g - up*.8, g + up*.98, .017, vertices=8)]
    for k in range(4): st.append(prim("primitive_torus_add", brass, g + up*(-.6 + .45*k), (1,1,1), major_radius=.022, minor_radius=.006))
    gc = g + up*1.12; nrm = ax
    q = nrm.to_track_quat('Z','Y')
    gear = prim("primitive_torus_add", brass, gc, (1,1,1), major_radius=.12, minor_radius=.022, major_segments=32, minor_segments=6); gear.rotation_euler = q.to_euler(); st.append(gear)
    qm = q.to_matrix()
    for k in range(12):
        a = 2*math.pi*k/12; d = qm @ Vector((math.cos(a), math.sin(a), 0))
        t_ = prim("primitive_cube_add", brass, gc + d*.15, (.025,.025,.018)); t_.rotation_euler = (q @ Quaternion((0,0,1), a)).to_euler() if False else q.to_euler(); st.append(t_)
    for k in range(4):
        a = 2*math.pi*k/4 + .4; d = qm @ Vector((math.cos(a), math.sin(a), 0))
        st.append(along("primitive_cylinder_add", iron, gc + d*.04, gc + d*.11, .01, vertices=6))
    st.append(prim("primitive_uv_sphere_add", rune, gc, (.045,.045,.045), segments=12, ring_count=8))
    st.append(prim("primitive_torus_add", iron, gc, (1,1,1), major_radius=.05, minor_radius=.008)); st[-1].rotation_euler = q.to_euler()
    parts.append(rigid(st, arm, "hand.R"))
    rnd = random.Random(9); p = gc; bl = []
    fwd = (ax*.9 - up*.15).normalized()
    for k in range(9):
        q_ = gc + fwd*(.13*(k+1)) + sd*rnd.uniform(-.06,.06) + up*rnd.uniform(-.05,.05)
        bl.append(along("primitive_cylinder_add", bolt, p, q_, .014 - .0008*k, vertices=4)); p = q_
    bl.append(prim("primitive_uv_sphere_add", bolt, gc, (.1,)*3))
    fx = rigid(bl, arm, "hand.R"); fx.name = "raio"; info["flash"] = fx
    grow(arm, 1.05)
    info.update({"base": "tecnomancer"}); return arm, info

# ====================================================================== TECNOMANCER → ENGENHEIRO HEREGE
def engenheiro_herege():
    """O que fundiu o sino da igreja para fazer um canhão: exoesqueleto de pistões nas pernas e na coluna, canhão-sino no
    ombro, máscara de solda com um olho só, avental de chumbo e um martelo-chave com bobina de tesla."""
    mat("azul_aco_casaco", (.08,.1,.13), 0, .6, dirt=.55, grime=.9)
    arm, info = classes2.tecnomancer()
    drop_named("tecnomancer_head", "tecnomancer_hand.R")
    for o_ in list(bpy.data.objects):
        if o_.name.startswith("raio"): bpy.data.objects.remove(o_, do_unlink=True)
    coat = mat("azul_aco_casaco", (.08,.1,.13)); dark = mat("couro_escuro", (.03,.022,.017)); brass = mat("latao_debrum", (.55,.3,.08))
    copper = mat("cobre", (.45,.16,.06)); iron = mat("ferro_velho", (.1,.095,.09)); rune = mat("runa_laranja", (1,.5,.1))
    bolt = mat("raio", (.7,.9,1)); skin = mat("pele_suja", (.36,.22,.15)); hairm = mat("cabelo", (.03,.025,.02))
    bronze = mat("bronze_sino", (.38,.26,.12), 1, .45, dirt=.5, grime=.3)
    parts = []
    # exoesqueleto: hastes e pistões nas pernas, presos com cintas
    for n in "LR":
        s = 1 if n == "L" else -1
        for bn in (f"thigh.{n}", f"shin.{n}"):
            o, ax, up, sd = bone_frame(bn); ln = (P(bn, 1) - P(bn)).length
            out = Vector((s, 0, 0))
            ex = [along("primitive_cylinder_add", iron, o + out*.1, o + ax*ln*.6 + out*.1, .018, vertices=8),
                  along("primitive_cylinder_add", brass, o + ax*ln*.55 + out*.1, o + ax*ln + out*.1, .011, vertices=8),
                  prim("primitive_uv_sphere_add", brass, o + out*.1, (.035,.035,.035), segments=10, ring_count=6)]
            for t in (.25, .75):
                r_ = prim("primitive_torus_add", dark, o + ax*ln*t, (1,1,1), major_radius=.085, minor_radius=.012); r_.rotation_euler = ax.to_track_quat('Z','Y').to_euler(); ex.append(r_)
            parts.append(rigid(ex, arm, bn))
    # coluna mecânica nas costas e canhão-sino no ombro direito, preso num braço articulado
    ch = []
    for k in range(6):
        ch.append(plate(iron, (0,.24 - .01*k,1.5 - .09*k), (.05,.03,.035)))
    ch += curve_tube(copper, [Vector((-.1,.3,1.3)), Vector((-.25,.3,1.52)), Vector((-.27,.2,1.68))], .022, .022, 8)[:-1]
    bc = Vector((-.27,.12,1.78)); bdir = Vector((-.1,-1,.25)).normalized()
    bell = skirt("sino", bronze, [(0,.02,.02,0), (.05,.06,.06,0), (.14,.075,.075,0), (.26,.1,.1,0), (.32,.13,.13,0), (.34,.14,.14,0)], open_front=0, thick=.014)
    Mq = bdir.to_track_quat('Z','Y').to_matrix().to_4x4(); bell.data.transform(Matrix.Translation(bc - bdir*.2) @ Mq); ch.append(bell)
    ch.append(prim("primitive_torus_add", brass, bc + bdir*.12, (1,1,1), major_radius=.135, minor_radius=.012)); ch[-1].rotation_euler = bdir.to_track_quat('Z','Y').to_euler()
    ch.append(prim("primitive_uv_sphere_add", rune, bc + bdir*.08, (.07,.07,.07)))
    for k in range(4):
        a = 2*math.pi*k/4; d = Vector((math.cos(a), 0, math.sin(a)))
        ch.append(along("primitive_cylinder_add", iron, bc - bdir*.2 + d*.04, bc - bdir*.32 + d*.04, .01, vertices=6))
    ch.append(prim("primitive_cylinder_add", iron, bc - bdir*.25, (.06,.06,.06), vertices=12))
    ch.append(plate(dark, (0,-.17,1.15), (.15,.02,.22), (4,0,0)))
    parts.append(rigid(ch, arm, "chest"))
    # cabeça: máscara de solda inteira de ferro com um olho grande laranja, mangueira, cabelo de fora
    hd = [head_base(skin), plate(iron, (0,-.06,1.67), (.085,.06,.105)),
          along("primitive_cylinder_add", brass, (0,-.12,1.69), (0,-.15,1.69), .04, vertices=14),
          along("primitive_cylinder_add", rune, (0,-.149,1.69), (0,-.154,1.69), .032, vertices=14)]
    for k in range(4): hd.append(prim("primitive_cube_add", dark, (-.05 + .033*k,-.13,1.6), (.008,.004,.015)))
    hd += curve_tube(dark, [Vector((0,-.11,1.58)), Vector((.08,-.05,1.5)), Vector((.14,.1,1.47)), Vector((.1,.22,1.42))], .012, .012, 6)
    rnd = random.Random(5)
    for k in range(10):
        a = rnd.uniform(.5, 2.6); b = Vector((math.cos(a)*.06, .04 + math.sin(a)*.04, 1.77))
        hd.append(along("primitive_cone_add", hairm, b, b + Vector((math.cos(a)*.04, .06, .07)), 1, radius1=.02, radius2=0, vertices=5))
    parts.append(rigid(hd, arm, "head"))
    # martelo-chave: cabo de ferro, cabeça de chave inglesa num lado e marreta com bobina do outro
    fr = bone_frame("hand.R"); o, ax, up, sd = fr; g = L(fr, .045)
    hc = g + up*.75
    w = [along("primitive_cylinder_add", iron, g - up*.3, hc, .02, vertices=8),
         along("primitive_cylinder_add", dark, g - up*.12, g + up*.12, .025, vertices=8),
         along("primitive_cylinder_add", iron, hc - ax*.2, hc + ax*.16, .055, vertices=12),
         along("primitive_cylinder_add", brass, hc - ax*.22, hc - ax*.19, .065, vertices=12)]
    for k in range(5): w.append(prim("primitive_torus_add", copper, hc - ax*(.15 - .03*k), (1,1,1), major_radius=.06, minor_radius=.009)); w[-1].rotation_euler = ax.to_track_quat('Z','Y').to_euler()
    w.append(prim("primitive_uv_sphere_add", rune, hc - ax*.23, (.03,.03,.03)))
    for s_ in (1, -1): w.append(along("primitive_cube_add", iron, hc + ax*.16 + up*.05*s_, hc + ax*.3 + up*.07*s_, .025))
    parts.append(rigid(w, arm, "hand.R"))
    rnd = random.Random(9); p = hc; bl = []
    fwd = (ax*.9 - up*.15).normalized()
    for k in range(9):
        q_ = hc + fwd*(.13*(k+1)) + sd*rnd.uniform(-.06,.06) + up*rnd.uniform(-.05,.05)
        bl.append(along("primitive_cylinder_add", bolt, p, q_, .012, vertices=4)); p = q_
    fx = rigid(bl, arm, "hand.R"); fx.name = "raio"; info["flash"] = fx
    grow(arm, 1.07)
    info.update({"base": "tecnomancer"}); return arm, info
