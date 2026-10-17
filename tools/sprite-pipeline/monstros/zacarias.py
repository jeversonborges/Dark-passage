# Zacarias, o Arauto da Trombeta Calada (chefe do andar 3 da Cripta), visual 3 (padrão Egito/Amenti, 17/10/2026).
# Pedido do Jefin (11/10): "anjo guerreiro, com máscara e asa astral, ele todo é astral abaixo da armadura; carrega um
# ataque devastador por 4 s que mata o jogador se ele tomar o golpe". Em 16/10: "o padrão alcançado no Egito".
# ~2,7 m. Armadura gótica de prata enegrecida esculpida em cascas (peitoral em quilha com o sol do Coro, gorjal em gomos,
# faldas, escarcelas, ombreiras de três lâminas com chamas de ouro, braçais, cotoveleiras em leque, manoplas, coxotes,
# joelheiras, grevas e sapatos de placas), filigrana de ouro gasto, poeira e escorridos. Por baixo não há corpo: luz
# astral (núcleo azul profundo, bordas brancas, veios que correm) que aparece nas juntas e vaza pelas frestas.
# Máscara de ouro lisa, sem boca: onde seria a boca há um lacre de cera (a trombeta calou, ele também). Cabelo de
# chamas astrais para trás, crista de lâminas de ouro, auréola astral QUEBRADA (falta um pedaço do anel).
# A trombeta calada nas costas: latão amassado, a campânula tapada com cera e pregos, presa por uma corrente.
# Tabardo de linho sujo na frente e atrás, barra de ouro. Asas de penas astrais (cinza-azuladas, pontas acesas).
# Montante de duas mãos com runas que acendem na carga. Luz real na ponta da lâmina (ilumina a armadura na carga).
# Brilho: uma cor só, astral azul-branca.
# Animações (mesmos nomes do jogo): idle (laço: respira, asas ondulam, centelhas sobem), walk (passo pesado de armadura),
# attack (antecipação, corte diagonal com as asas abrindo, arrasto e volta), charge (laço que o jogo repete 4 s: montante
# erguido com as duas mãos, asas abertas no alto, aura, runas e luz crescendo e pulsando, centelhas subindo),
# release (ergue mais um pouco, desce o montante no chão à frente: a aura estoura numa onda de luz no chão e some),
# hit, death (espasmo das asas, cai de joelhos, a máscara pende, tomba; a luz astral apaga).
# Visual 1 (anjo de porcelana com a trombeta) em zacarias_v1.py; visual 2 (primeira armadura astral) em zacarias_v2.py.
import bpy, math, random
from mathutils import Vector, Matrix, Quaternion
from mrig import *
from amenti import *
from atlante import glow
import os

INFO = {"px": 512, "target_z": 1.8, "rim": (.72, .84, 1), "rim_e": 6.5, "colors": 56, "samples": 32,
        "loops": ("idle", "walk", "charge"),
        "fps": {"idle": 7, "walk": 9, "attack": 13, "charge": 10, "release": 14, "hit": 12, "death": 10}}
INFO["samples"] = int(os.environ.get("AMOSTRAS", INFO["samples"]))
INFO["denoise"] = os.environ.get("DENOISE", "1") == "1"
SCALE = 1.5
ASTRAL = (.5, .74, 1.0)
V = {"name": "zacarias"}
def set_variant(name): pass

# ======================================================================= esqueleto
WJ = [(.08, .15, 1.44), (.36, .29, 1.68), (.7, .4, 1.86), (1.04, .5, 1.96)]   # ombro, cotovelo, pulso, ponta (lado L)
WFALL = (.18, .16, -1)
def X(p, s): return Vector((p[0]*s, p[1], p[2]))

MOTES = [(-.25, -.2, 1.2), (.3, .1, 1.5), (-.4, .25, 1.75), (.55, .3, 1.7), (-.7, .35, 1.8), (.15, .2, 1.95),
         (-.1, -.25, .7), (.28, -.15, .9), (.0, .3, 1.3), (.8, .4, 1.9)]

def bones():
    B = humanoid(1.0)
    for s, n in ((1, "L"), (-1, "R")):
        for k in range(3):
            B[f"w{n}{k+1}"] = (tuple(X(WJ[k], s)), tuple(X(WJ[k+1], s)), "chest" if k == 0 else f"w{n}{k}")
    B["tab1"] = ((0, -.15, .97), (0, -.17, .62), "hips")
    B["tab2"] = ((0, -.17, .62), (0, -.18, .28), "tab1")
    B["bk1"] = ((0, .13, .97), (0, .16, .6), "hips")
    B["bk2"] = ((0, .16, .6), (0, .18, .24), "bk1")
    h, t = Vector(B["hand.R"][0]), Vector(B["hand.R"][1]); d = (t - h).normalized()
    B["sword"] = (tuple(t - d*.04), tuple(t + d*1.25), "hand.R")
    st = t + d*1.25
    B["aura"] = (tuple(st), tuple(st + d*.1), "sword")
    B["halo"] = ((0, .1, 1.78), (0, .1, 1.88), "head")
    B["onda"] = ((0, -1.0, .0), (0, -1.0, .1), None)       # onda de luz no chão (release), sem pai
    return B

# ======================================================================= materiais
def prata(name, base=(.3, .31, .34), metal=.55, **k):
    """Prata enegrecida: a placa de marfim de amenti com base de prata, metálica, filigrana de ouro gasta."""
    m = marfim(name, base=base, stain=(.05, .045, .045), stain_amt=.55, rough=.34, **k)
    nt = m.node_tree; b = [n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'][0]
    lk = b.inputs["Metallic"].links
    if lk:
        src = lk[0].from_socket; nt.links.remove(lk[0])
        mm = nt.nodes.new("ShaderNodeMath"); mm.operation = 'MULTIPLY_ADD'
        mm.inputs[1].default_value = 1 - metal; mm.inputs[2].default_value = metal
        nt.links.new(src, mm.inputs[0]); nt.links.new(mm.outputs[0], b.inputs["Metallic"])
    b.inputs["Coat Weight"].default_value = .12
    return m

def astral_mat(name, deep=(.03, .1, .55), mid=(.15, .4, 1.0), hi=(.8, .9, 1.0), strength=1.2, scale=7.0):
    """Luz astral: núcleo azul profundo, veios azuis que correm e bordas brancas (fresnel). Só para a câmera."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes):
        if nd.type != 'OUTPUT_MATERIAL': nt.nodes.remove(nd)
    out = [nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL'][0]
    def math_(op, a, b):
        n_ = nt.nodes.new("ShaderNodeMath"); n_.operation = op
        for i, v in enumerate((a, b)):
            if isinstance(v, (int, float)): n_.inputs[i].default_value = v
            else: nt.links.new(v, n_.inputs[i])
        return n_.outputs[0]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = scale; nz.inputs["Detail"].default_value = 6
    nz.inputs["Distortion"].default_value = 1.6; nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
    vr = nt.nodes.new("ShaderNodeValToRGB"); el = vr.color_ramp.elements     # veios: faixa estreita do ruído
    el[0].position = .47; el[0].color = (0, 0, 0, 1); el[1].position = .5; el[1].color = (1, 1, 1, 1)
    e2 = el.new(.53); e2.color = (0, 0, 0, 1)
    nt.links.new(nz.outputs["Fac"], vr.inputs["Fac"])
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = .3
    rim = math_('POWER', lw.outputs["Facing"], 2.2)
    def mix(fac, c0, c1):
        mc = nt.nodes.new("ShaderNodeMix"); mc.data_type = 'RGBA'
        for i, c in ((6, c0), (7, c1)):
            if isinstance(c, tuple): mc.inputs[i].default_value = (*c, 1)
            else: nt.links.new(c, mc.inputs[i])
        nt.links.new(fac, mc.inputs[0]); return mc.outputs[2]
    col = mix(math_('MULTIPLY', nz.outputs["Fac"], 1.0), deep, mid)
    col = mix(math_('MULTIPLY', vr.outputs["Color"], .7), col, hi)
    col = mix(rim, col, hi)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = strength
    nt.links.new(col, em.inputs["Color"])
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = (*deep, 1)
    lp = nt.nodes.new("ShaderNodeLightPath"); ms = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], ms.inputs[0]); nt.links.new(df.outputs[0], ms.inputs[1]); nt.links.new(em.outputs[0], ms.inputs[2])
    nt.links.new(ms.outputs[0], out.inputs["Surface"])
    return m

def cera(name, rgb=(.28, .05, .03)):
    """Lacre de cera vermelho-escuro, brilho úmido, borda escorrida."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = stained(name, rgb, stain=(.1, .02, .01), amount=.45, scale=9, rough=.35, grime=.3)
    return m

# ======================================================================= modelo
def build():
    B = bones(); MN = mote_bones(B, "mo", MOTES)
    rnd = random.Random(31)
    sil = prata("z_prata", base=(.36, .37, .41), grime=1.1); sil2 = prata("z_prata_lisa", base=(.28, .29, .33), plain=.75, grime=1.1)
    gold = ouro("z_ouro", rgb=(.58, .41, .14))
    cloth = pano("z_linho", (.5, .47, .4), grime=1.9, stain_amt=.6)
    leather = couro("z_couro", (.05, .035, .028))
    under = couro("z_cota", (.03, .03, .035), .5)
    steel = aco("z_aco", (.3, .32, .36), rough=.42, dirt=.7)
    brass = ouro("z_latao", rgb=(.45, .3, .12), amount=.75, rough=.42)
    iron = aco("z_ferro", (.16, .15, .15), rough=.5, dirt=.8)
    wax = cera("z_cera")
    hole = mat("z_fresta", (.003, .004, .006), 0, .9)
    body = astral_mat("z_astral", strength=1.1)
    flame = astral_mat("z_astral_chama", deep=(.05, .18, .8), strength=1.5, scale=4)
    luz = glow("z_luz", (.35, .62, 1), 1.7)                     # brilho fixo (frestas, auréola, ponta das penas)
    runa = glow("z_runa", (.3, .58, 1), 1.1)            # runas da lâmina: acendem na carga (canal "glow")
    core = glow("z_nucleo", (.85, .93, 1), 6.0)          # coração da aura e da onda
    pena = stained("z_pena", (.44, .5, .6), stain=(.12, .14, .2), amount=.3, scale=4, rough=.75,
                   blotch=(.3, .36, .48), blotch_amt=.4, grime=.2)
    pena2 = astral_mat("z_pena_ponta", deep=(.06, .2, .75), strength=.9, scale=3)

    R = XRig(V["name"], B); P = R.P
    R.gbones = ["foot.L", "foot.R"]
    R.hidden = {"aura", "onda"} | set(MN)

    # ------------------------------------------------ corpo de luz astral (fecha as frestas, aparece nas juntas)
    j = {"pelvis": (0, 0, .97, .13, .1), "waist": (0, 0, 1.14, .11, .085), "chest": (0, 0, 1.33, .15, .1),
         "neck": (0, -.01, 1.52, .05), "neck2": (0, -.02, 1.6, .045)}
    e = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        j[f"sh{n}"] = (*P(f"upper_arm.{n}"), .062); j[f"el{n}"] = (*P(f"forearm.{n}"), .045); j[f"wr{n}"] = (*P(f"hand.{n}"), .036)
        j[f"hp{n}"] = (*P(f"thigh.{n}"), .08); j[f"kn{n}"] = (*P(f"shin.{n}"), .058); j[f"an{n}"] = (*P(f"foot.{n}"), .045)
        e += [("chest", f"sh{n}"), (f"sh{n}", f"el{n}"), (f"el{n}", f"wr{n}"), ("pelvis", f"hp{n}"), (f"hp{n}", f"kn{n}"), (f"kn{n}", f"an{n}")]
    R.bind(skin_mesh("z_corpo", j, e, body), [b for b in B if b.split(".")[0] in
           ("hips", "spine", "chest", "neck", "upper_arm", "forearm", "thigh", "shin")])

    # ------------------------------------------------ peitoral em quilha, sol do Coro, gorjal
    def keel(p, u, v):
        f = max(0, math.cos(math.radians(u)))
        p.y -= .03*math.exp(-(p.x/.045)**2)*f*(.6 + .4*math.sin(math.radians(v + 40)))
        p.y -= .012*math.exp(-((abs(p.x) - .085)/.045)**2)*f*max(0, math.sin(math.radians(v + 10)))
        return p
    C = Vector((0, -.005, 1.31))
    ch = [shell("peito", sil, C, .19, .14, .22, -98, 98, -36, 72, 28, 14, .014, deform=keel),
          shell("costas", sil2, C, .19, .135, .22, 82, 278, -36, 72, 24, 12, .014)]
    ch.append(trim("peito_borda", gold, shell_edge(C, .19, .14, .22, -98, 98, -36, 26, deform=keel, out=1.03), .01))
    ch.append(trim("peito_gola", gold, shell_edge(C, .19, .14, .22, -98, 98, 70, 26, deform=keel, out=1.02), .009))
    ch.append(trim("peito_quilha", gold, [keel(ell((0, 0, 0), .19*1.04, .14*1.04, .22*1.04, 0, v), 0, v) + C for v in range(-34, 70, 8)], .006))
    for s in (1, -1):   # costelas de ouro curvas sobre os peitorais
        for k in range(2):
            pts = [keel(ell((0, 0, 0), .19*1.035, .14*1.035, .22*1.035, s*(16 + 55*t), 50 - 18*k - 70*t*t), s*(16 + 55*t), 50 - 18*k - 70*t*t) + C
                   for t in [i/10 for i in range(11)]]
            ch.append(trim(f"peito_fil{k}{s}", gold, pts, .005))
    sun = Vector((0, -.168, 1.37))
    ch.append(ring_at("sol_aro", gold, sun, (0, -1, 0), .042, .008))
    ch.append(prim("primitive_cylinder_add", gold, sun, (.03, .03, .01), rot=(90, 0, 0), vertices=20))
    ch.append(prim("primitive_uv_sphere_add", luz, sun + Vector((0, -.008, 0)), (.012, .006, .012), segments=10, ring_count=6))
    for k in range(16):
        a = 2*math.pi*k/16; d = Vector((math.cos(a), 0, math.sin(a))); L_ = .095 if k % 2 == 0 else .066
        sp = spike(gold, sun + d*.042, sun + d*L_ + Vector((0, .012, 0)), .013); sp.scale.y *= .35; ch.append(sp)
    for k in range(4):   # gorjal em gomos
        z = 1.46 + .026*k
        ch.append(rings_loft(f"gorjal{k}", sil if k % 2 == 0 else sil2, [(z - .02, .112 - .01*k, .098 - .008*k, -.005),
                                                                       (z + .012, .098 - .01*k, .086 - .008*k, -.005)], seg=28, cap_top=False, th=.008))
        ch.append(trim(f"gorjal_f{k}", gold, [Vector((math.sin(a)*(.114 - .01*k), -.005 - math.cos(a)*(.1 - .008*k), z - .02))
                                              for a in [2*math.pi*i/28 for i in range(28)]], .004, closed=True))
    # rebites no peitoral
    for s in (1, -1):
        for k in range(4):
            p = ell(C, .19*1.01, .14*1.01, .22*1.01, s*(62 + 8*k), -20 + 20*k)
            ch.append(prim("primitive_uv_sphere_add", gold, p, (.008, .008, .008), segments=8, ring_count=5))
    # suporte das asas nas costas
    ch.append(shell("costas_asas", sil2, (0, .12, 1.36), .12, .06, .13, 120, 240, -60, 80, 12, 8, .01))
    R.rigid(ch, "chest")

    # ------------------------------------------------ a trombeta calada nas costas (latão, campânula lacrada, corrente)
    tA = Vector((-.15, .2, 1.58)); tB = Vector((.2, .21, .98))
    td = (tB - tA).normalized()
    tr = [ttube("trombeta", brass, [tA, tA.lerp(tB, .5) + Vector((0, .025, 0)), tB], .012, seg=12,
                prof=lambda t: .011 + .006*t + .085*max(0, (t - .72)/.28)**2.6)]
    tr.append(ring_at("tromb_bocal", brass, tA - td*.01, td, .016, .006))
    for k, t in enumerate((.3, .55)):
        tr.append(ring_at(f"tromb_anel{k}", gold, tA.lerp(tB, t), td, .02, .005))
    bell = tB + td*.005
    tr.append(ring_at("tromb_borda", brass, bell, td, .095, .008, seg=32))
    tr.append(prim("primitive_cylinder_add", wax, bell, (.088, .088, .012), vertices=28))
    tr[-1].rotation_euler = td.to_track_quat('Z', 'Y').to_euler()
    for k in range(6):   # pregos atravessando a cera
        a = 2*math.pi*k/6 + .3; s_ = td.orthogonal().normalized(); u_ = td.cross(s_)
        p = bell + (s_*math.cos(a) + u_*math.sin(a))*.06
        tr.append(ttube(f"prego{k}", iron, [p - td*.02, p + td*.03], .005, .003, seg=6))
        tr.append(prim("primitive_cylinder_add", iron, p + td*.03, (.009, .009, .003), vertices=8))
        tr[-1].rotation_euler = td.to_track_quat('Z', 'Y').to_euler()
    tr.append(prim("primitive_cylinder_add", wax, bell + td*.012, (.03, .03, .008), vertices=16))   # selo do lacre
    tr[-1].rotation_euler = td.to_track_quat('Z', 'Y').to_euler()
    # corrente transversal do ombro esquerdo ao quadril direito, segurando a trombeta
    cA, cB = Vector((.17, .02, 1.5)), Vector((-.16, .02, 1.02))
    for k in range(14):
        t = k/13; c = cA.lerp(cB, t) + Vector((0, .155 + .02*math.sin(math.pi*t), 0))
        tr.append(ring_at(f"elo{k}", iron, c, (cB - cA) if k % 2 else Vector((0, 1, 0)), .012, .0035, seg=10, sq=1.6))
    R.rigid(tr, "chest")

    # ------------------------------------------------ faldas, cinto, escarcelas
    sp_ = []
    for k, z in enumerate((1.14, 1.08)):
        sp_.append(rings_loft(f"falda{k}", sil, [(z - .034, .155 + .012*k, .118 + .01*k, -.004), (z + .03, .146 + .01*k, .111 + .01*k, -.004)],
                              seg=32, cap_top=False, th=.01))
        sp_.append(trim(f"falda_f{k}", gold, [Vector((math.sin(a)*(.158 + .012*k), -.004 - math.cos(a)*(.121 + .01*k), z - .034))
                                              for a in [2*math.pi*i/32 for i in range(32)]], .005, closed=True))
    R.rigid(sp_, "spine")
    hp_ = [rings_loft("cinto", leather, [(.96, .168, .128, 0), (1.01, .165, .126, 0)], seg=32, cap_top=False, th=.012),
           ring_at("fivela", gold, (0, -.14, .985), (0, -1, 0), .028, .007),
           prim("primitive_uv_sphere_add", gold, (0, -.144, .985), (.016, .009, .016), segments=12, ring_count=8)]
    for s in (1, -1):
        for k in range(2):
            c = Vector((.115*s, -.05, .9 - .1*k)); Rm = Matrix.Rotation(math.radians(18*s), 3, 'Z') @ Matrix.Rotation(math.radians(-8), 3, 'X')
            hp_.append(shell(f"escarcela{k}{s}", sil if k == 0 else sil2, c, .095, .066, .08, -60, 60, -70, 60, 12, 8, .01, R=Rm))
            hp_.append(trim(f"escarcela_f{k}{s}", gold, shell_edge(c, .095, .066, .08, -60, 60, -70, 12, R=Rm, out=1.04), .005))
    R.rigid(hp_, "hips")

    # ------------------------------------------------ tabardo na frente e atrás (linho sujo, barra de ouro, rasgado)
    def tab(r, c, y0, w0, w1, z0, z1, jag=None, back=False):
        z = z0 + (z1 - z0)*r; w = w0 + (w1 - w0)*r; x = (c*2 - 1)*w
        sg = 1 if back else -1
        return Vector((x, y0 + sg*(.03*r + .012*math.cos(x*20)*r), z + (jag[int(c*12)] if jag and r > .99 else 0)))
    for nm, y0, w0, w1, z1, bn, back, sd in (("f", -.155, .1, .125, .3, ["hips", "tab1", "tab2"], False, 5),
                                              ("c", .14, .11, .135, .25, ["hips", "bk1", "bk2"], True, 9)):
        jg = [random.Random(sd).uniform(-.06, .01) for _ in range(13)]
        f_ = lambda r, c, jg=jg, y0=y0, w0=w0, w1=w1, z1=z1, back=back: tab(r, c, y0, w0, w1, .97, z1, jag=jg, back=back)
        objs = [sheet(f"tabardo_{nm}", cloth, 20, 9, f_, .01)]
        dy = Vector((0, .006 if back else -.006, 0))
        objs += [trim(f"tab_be_{nm}", gold, [f_(r/10, 0) + dy for r in range(11)], .006),
                 trim(f"tab_bd_{nm}", gold, [f_(r/10, 1) + dy for r in range(11)], .006),
                 trim(f"tab_barra_{nm}", gold, [f_(.86, c/8) + dy for c in range(9)], .006)]
        if not back:   # trombeta bordada, atravessada por um traço (calada)
            m0 = f_(.3, .5) + dy*1.3
            pts = [m0 + Vector((-.05, 0, .05)), m0 + Vector((0, 0, 0)), m0 + Vector((.04, 0, -.05))]
            objs.append(trim("bordado_tromb", gold, pts, .006))
            objs.append(ring_at("bordado_camp", gold, m0 + Vector((.05, 0, -.065)), (0, -1, 0), .028, .005))
            objs.append(trim("bordado_risco", gold, [m0 + Vector((-.06, 0, -.07)), m0 + Vector((.07, 0, .06))], .004))
        for o in objs: R.bind(o, bn, power=3)

    # ------------------------------------------------ ombreiras, braçais, cotoveleiras, manoplas
    for s, n in ((1, "L"), (-1, "R")):
        sh = P(f"upper_arm.{n}"); el = P(f"forearm.{n}"); wr = P(f"hand.{n}")
        pa = []
        for k in range(3):
            c = sh + Vector((.035*s + .028*k*s, .0, .065 - .05*k))
            Rm = Matrix.Rotation(math.radians(-(24 + 10*k)*s), 3, 'Y')
            rx, ry, rz = .145 - .012*k, .14 - .01*k, .085 - .006*k
            pa.append(shell(f"ombreira{k}.{n}", sil if k % 2 == 0 else sil2, c, rx, ry, rz, -180, 180, -8 if k else -25, 90, 28, 8, .013, R=Rm))
            pa.append(trim(f"ombreira_f{k}.{n}", gold, shell_edge(c, rx, ry, rz, -180, 180, -8 if k else -25, 30, R=Rm, out=1.02), .007, seg=6))
            for q in range(5):   # rebites na borda
                p = ell(c, rx*1.01, ry*1.01, rz*1.01, -80 + 40*q, 4 if k else -14, R=Rm)
                pa.append(prim("primitive_uv_sphere_add", gold, p, (.007, .007, .007), segments=8, ring_count=5))
        top = sh + Vector((.04*s, .02, .14))
        for k in range(3):   # chamas de ouro subindo para trás
            b = top + Vector((.03*s*k - .02*s, .035*(k - 1) + .02, -.02*k))
            pa.append(flame_spike(f"chama{k}.{n}", gold, b, Vector((.3*s, .45 + .1*(k - 1), 1)), Vector((s*.3, 1, .2)), .13 - .022*k, .024, curl=.5))
        pa.append(limb(f"braco.{n}", sil2, R, f"upper_arm.{n}", .38, .95, .06, .054, bulge=.08))
        R.rigid(pa, f"upper_arm.{n}")
        fa = [limb(f"bracal.{n}", sil, R, f"forearm.{n}", .14, .92, .052, .06, bulge=.1),
              ring_at(f"bracal_a.{n}", gold, el.lerp(wr, .92), wr - el, .062, .007),
              ring_at(f"bracal_b.{n}", gold, el.lerp(wr, .16), wr - el, .055, .006),
              shell(f"cotov.{n}", sil, el + Vector((0, .032, 0)), .055, .055, .065, 100, 260, -60, 70, 12, 8, .01)]
        for k in range(3):   # leque da cotoveleira
            fa.append(flame_spike(f"leque{k}.{n}", gold, el + Vector((.018*s*(k - 1), .065, -.01)), Vector((.3*s*(k - 1), .9, -.3)),
                                  Vector((0, 0, 1)), .065, .018, curl=.2))
        R.rigid(fa, f"forearm.{n}")
        o_, ax, u, sd = R.frame(f"hand.{n}")
        hp = [shell(f"manopla.{n}", sil, o_ + ax*.04, .042, .047, .056, -180, 180, -90, 90, 14, 8, .0, R=ax.to_track_quat('Z', 'Y').to_matrix())]
        for f in range(4):
            base = o_ + ax*.08 + sd*(-.028 + .019*f)
            hp.append(ttube(f"dedo{f}.{n}", sil2, [base, base + ax*.033 + u*.02, base + ax*.056 + u*.042], .011, .008, seg=6))
        hp.append(ttube(f"polegar.{n}", sil2, [o_ + ax*.03 - sd*s*.038, o_ + ax*.058 - sd*s*.056 + u*.02, o_ + ax*.076 - sd*s*.046 + u*.048], .012, .008, seg=6))
        R.rigid(hp, f"hand.{n}")

    # ------------------------------------------------ pernas
    for s, n in ((1, "L"), (-1, "R")):
        h, k_, a, tt = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        R.rigid([limb(f"coxote.{n}", sil2, R, f"thigh.{n}", .12, .88, .088, .07, bulge=.06),
                 trim(f"coxote_f.{n}", gold, [h.lerp(k_, .2) + Vector((0, -.085, 0)), h.lerp(k_, .55) + Vector((0, -.083, 0)), h.lerp(k_, .86) + Vector((0, -.07, 0))], .005)],
                f"thigh.{n}")
        R.rigid([shell(f"joelho.{n}", sil, k_ + Vector((0, -.038, .01)), .06, .048, .07, -80, 80, -80, 80, 14, 10, .01),
                 ring_at(f"joelho_a.{n}", gold, k_ + Vector((0, -.066, .01)), (0, -1, 0), .036, .006),
                 prim("primitive_uv_sphere_add", luz, k_ + Vector((0, -.07, .01)), (.008, .004, .008), segments=8, ring_count=5),
                 limb(f"greva.{n}", sil, R, f"shin.{n}", .1, .95, .066, .052, bulge=.12),
                 ring_at(f"greva_a.{n}", gold, k_.lerp(a, .93), a - k_, .053, .006),
                 trim(f"greva_q.{n}", gold, [k_.lerp(a, t) + Vector((0, -.066 + .02*t, 0)) for t in (.15, .5, .85)], .004)], f"shin.{n}")
        ft = [shell(f"sapato.{n}", sil, a.lerp(tt, .45) + Vector((0, 0, -.025)), .056, .115, .048, -180, 180, 0, 90, 20, 8, .01),
              ttube(f"bico.{n}", sil2, [a.lerp(tt, .6) + Vector((0, 0, -.01)), tt + Vector((0, -.05, -.005))], .038, .004, seg=8)]
        for jj in range(3):
            ft.append(trim(f"lamina{jj}.{n}", gold, shell_edge(a.lerp(tt, .3 + .2*jj) + Vector((0, 0, -.025)), .056 - .005*jj, .03, .048 - .006*jj,
                                                                -90, 90, 30, 12), .0035))
        R.rigid(ft, f"foot.{n}")

    # ------------------------------------------------ cabeça: máscara de ouro sem boca (lacre de cera), chamas, crista
    hc = Vector((0, -.015, 1.7)); hd = []
    hd.append(prim("primitive_uv_sphere_add", body, hc + Vector((0, .01, 0)), (.07, .08, .09), segments=16, ring_count=10))
    def face(p, u, v):
        f = max(0, math.cos(math.radians(u)))
        p.y -= .018*math.exp(-(p.x/.012)**2)*f*math.exp(-((p.z + .005)/.04)**2)     # nariz
        p.y -= .01*math.exp(-((p.z - .03)/.012)**2)*f                                # sobrancelha
        p.y += .008*math.exp(-((abs(p.x) - .033)/.015)**2)*math.exp(-((p.z - .018)/.012)**2)*f  # órbitas
        return p
    hd.append(shell("mascara", gold, hc + Vector((0, -.02, 0)), .076, .07, .1, -105, 105, -75, 80, 30, 18, .006, deform=face))
    hd.append(trim("mascara_borda", gold, shell_edge(hc + Vector((0, -.02, 0)), .076, .07, .1, -105, 105, 80, 22, out=1.02)
                   + shell_edge(hc + Vector((0, -.02, 0)), .076, .07, .1, 105, -105, -75, 22, out=1.02)[1:], .005))
    for s in (1, -1):   # frestas dos olhos com a luz vazando
        e0 = hc + Vector((.033*s, -.087, .018))
        hd.append(prim("primitive_cube_add", hole, e0, (.022, .008, .005), rot=(0, 10*s, -10*s)))
        hd.append(prim("primitive_cube_add", luz, e0 + Vector((0, -.004, 0)), (.018, .003, .0028), rot=(0, 10*s, -10*s)))
        hd.append(trim(f"lagrima{s}", gold, [e0 + Vector((.004*s, -.004, -.008)), e0 + Vector((.006*s, -.002, -.04)), e0 + Vector((.004*s, .006, -.07))], .0025))
    lac = hc + Vector((0, -.09, -.05))     # o lacre onde seria a boca
    hd.append(prim("primitive_cylinder_add", wax, lac, (.026, .026, .007), vertices=20, rot=(90, 0, 0)))
    for k in range(5):   # escorridos da cera
        a = math.radians(-60 - 15*k); p = lac + Vector((math.cos(a)*.022, -.002, math.sin(a)*.022))
        hd.append(ttube(f"cera_esc{k}", wax, [p, p + Vector((0, .002, -.012 - .006*(k % 3)))], .005, .002, seg=6))
    hd.append(ring_at("lacre_selo", wax, lac + Vector((0, -.005, 0)), (0, -1, 0), .014, .003))
    for k in range(5):   # crista: lâminas de ouro do topo para trás
        a = math.radians(70 + 22*k); q = hc + Vector((0, -.09*math.cos(a), .1*math.sin(a)))
        hd.append(flame_spike(f"crista{k}", gold, q, Vector((0, .5 + .12*k, .9 - .2*k)), Vector((1, 0, 0)), .08 + .015*k, .022, curl=.15))
    for k in range(11):   # cabelo de chamas astrais para trás
        a = math.radians(-75 + 150*k/10); q = hc + Vector((math.sin(a)*.068, .035 + math.cos(a)*.025, .04 + .02*math.cos(a)))
        d = Vector((math.sin(a)*.4, 1, .55 + rnd.uniform(-.1, .2)))
        hd.append(flame_spike(f"chama_cab{k}", flame, q, d, Vector((0, .3, 1)), rnd.uniform(.14, .24), .03, curl=.35))
    R.rigid(hd, "head")
    # auréola astral quebrada (falta um pedaço do anel; "calada")
    hc2 = P("halo"); hl = []
    for a0, a1 in ((-50, 150), (175, 290)):
        arc = [hc2 + Vector((math.cos(math.radians(a))*.2, .0, math.sin(math.radians(a))*.2)) for a in range(a0, a1 + 1, 6)]
        hl.append(trim(f"aureola{a0}", luz, arc, .008))
        hl.append(trim(f"aureola_o{a0}", flame, [p + (p - hc2).normalized()*.022 for p in arc], .004))
        for a in range(a0 + 8, a1 - 4, 16):
            d = Vector((math.cos(math.radians(a)), 0, math.sin(math.radians(a))))
            sp = spike(luz, hc2 + d*.2, hc2 + d*(.26 if (a // 16) % 2 else .235), .008); sp.scale.y *= .4; hl.append(sp)
    for k in range(3):   # cacos do pedaço que falta, soltos no ar
        a = math.radians(155 + 7*k); d = Vector((math.cos(a), 0, math.sin(a)))
        hl.append(spike(luz, hc2 + d*(.2 + .02*k) + Vector((0, .01*k, 0)), hc2 + d*(.23 + .02*k) + Vector((.006, .01*k, .01)), .007))
    R.rigid(hl, "halo")

    # ------------------------------------------------ montante: lâmina larga com runas, guarda de ouro, gema astral
    g = P("sword"); sdir = (P("sword", 1) - g).normalized()
    side = sdir.cross(Vector((0, -1, 0))).normalized() if abs(sdir.y) < .9 else Vector((1, 0, 0))
    nrm = sdir.cross(side).normalized()
    sw = [ttube("punho", leather, [g - sdir*.2, g + sdir*.09], .021, seg=8),
          prim("primitive_uv_sphere_add", gold, g - sdir*.23, (.032, .032, .032), segments=12, ring_count=8),
          ring_at("punho_a", gold, g - sdir*.19, sdir, .024, .006), ring_at("punho_b", gold, g + sdir*.08, sdir, .024, .006)]
    for k in range(9):
        sw.append(ring_at(f"tira{k}", leather, g - sdir*(.17 - .028*k), sdir, .022, .004))
    gc = g + sdir*.13
    sw.append(ttube("guarda", gold, [gc - side*.24 + sdir*.06, gc - side*.12, gc + side*.12, gc + side*.24 + sdir*.06], .016, seg=8,
                    prof=lambda t: .016 + .012*math.sin(math.pi*t)))
    for s_ in (1, -1):
        sw.append(flame_spike(f"guarda_p{s_}", gold, gc + side*.24*s_ + sdir*.06, side*s_ + sdir*.6, nrm, .08, .02, curl=.3))
    sw.append(ring_at("guarda_aro", gold, gc, nrm, .045, .01, seg=24))
    sw.append(prim("primitive_uv_sphere_add", luz, gc, (.028, .028, .028), segments=12, ring_count=8))
    b0 = gc + sdir*.05
    sw.append(blade("lamina", steel, b0, sdir, side, 1.07, .07, .055, th=.016, n=18, tipf=.14))
    sw.append(blade("ricasso", iron, b0, sdir, side, .14, .074, .072, th=.019, n=4, tipf=.0))
    for sg in (1, -1):   # runas: glifos curtos ao longo do sulco, dos dois lados (acendem na carga)
        for k in range(11):
            q = b0 + sdir*(.2 + .072*k) + nrm*.0175*sg
            w_ = side*(.012 if k % 3 else -.012)
            sw.append(trim(f"runa{k}{sg}", runa, [q - w_, q + sdir*.03, q + sdir*.05 + w_], .0035, seg=4))
        sw.append(trim(f"sulco{sg}", iron, [b0 + sdir*.16 + nrm*.016*sg, b0 + sdir*.98 + nrm*.016*sg], .004, seg=4))
    R.rigid(sw, "sword")
    # luz real presa à ponta da lâmina (só acende na carga e no golpe: chave "lamp")
    ld = bpy.data.lights.new("z_luz_aura", 'POINT'); ld.color = ASTRAL; ld.shadow_soft_size = .12; ld.energy = 60
    lo = bpy.data.objects.new("z_luz_aura", ld); bpy.context.scene.collection.objects.link(lo)
    lo.parent = R.arm; lo.parent_type = 'BONE'; lo.parent_bone = "sword"
    bpy.context.view_layer.update()
    bone = R.arm.data.bones["sword"]
    tailM = R.arm.matrix_world @ bone.matrix_local @ Matrix.Translation((0, bone.length, 0))
    lo.matrix_parent_inverse = tailM.inverted(); lo.location = P("aura")
    R.lamps.append((ld, 60))

    # ------------------------------------------------ aura do golpe carregado (na ponta da lâmina, escondida fora da carga)
    ac = P("aura"); au = [prim("primitive_uv_sphere_add", core, ac, (.07, .07, .07), segments=14, ring_count=10),
                          prim("primitive_uv_sphere_add", flame, ac, (.13, .13, .13), segments=16, ring_count=10)]
    for k in range(14):   # línguas de luz em volta
        a = 2*math.pi*k/14; d = Vector((math.cos(a), math.sin(a)*.5, math.sin(a)*.86)).normalized()
        up = d.cross(Vector((0, 0, 1))) if abs(d.z) < .9 else Vector((1, 0, 0))
        au.append(flame_spike(f"aura_l{k}", flame if k % 2 else luz, ac + d*.08, d, up, rnd.uniform(.16, .3), .03, curl=.5))
    for k in range(3):    # arcos quebrados girando
        Rm = Matrix.Rotation(math.radians(35 + 50*k), 3, 'X') @ Matrix.Rotation(math.radians(30*k), 3, 'Z')
        r_ = .2 + .06*k
        au.append(trim(f"aura_arco{k}", luz, [ac + Rm @ Vector((math.cos(t)*r_, math.sin(t)*r_, 0)) for t in
                                              [math.radians(a) for a in range(40*k, 40*k + 200, 10)]], .006))
    R.rigid(au, "aura")
    # onda de luz no chão (release)
    oc = P("onda"); on = [annulus("onda_aro", flame, oc + Vector((0, 0, .01)), .32, .37, .006, 64, axis=(0, 0, 1)),
                          annulus("onda_aro2", flame, oc + Vector((0, 0, .008)), .02, .3, .004, 64, axis=(0, 0, 1)),
                          prim("primitive_uv_sphere_add", core, oc + Vector((0, 0, .03)), (.06, .06, .035), segments=14, ring_count=8)]
    for k in range(12):   # rachaduras de luz e lascas subindo
        a = 2*math.pi*k/12 + rnd.uniform(-.15, .15); d = Vector((math.cos(a), math.sin(a), 0))
        pts = [oc + d*.1 + Vector((0, 0, .012))]
        for j_ in range(1, 5):
            pts.append(oc + (d*(.1 + .12*j_)) + Vector((rnd.uniform(-.03, .03), rnd.uniform(-.03, .03), .012)))
        on.append(trim(f"racha{k}", flame, pts, .006, seg=4))
        on.append(flame_spike(f"lasca{k}", flame, oc + d*.3, Vector((d.x*.3, d.y*.3, 1)), d, rnd.uniform(.12, .32), .025, curl=.15))
    R.rigid(on, "onda")

    # ------------------------------------------------ asas de penas astrais
    for s, n in ((1, "L"), (-1, "R")):
        feather_wing(R, f"w{n}", [X(p, s) for p in WJ], X(WFALL, s), Vector((0, -1, 0)), (pena, pena2), scale=.64,
                     seed=sum(map(ord, n))*11, gold=gold, bone_m=sil2, dense=1.0)

    motes(R, luz, MN, size=.011)
    finalize(R)
    sock = runa.node_tree.nodes["Emission"].inputs["Strength"]; R.glow.append((sock, sock.default_value))
    R.arm.scale = [SCALE]*3
    return R, INFO

# ======================================================================= animações
def wp(a1=0, a2=0, a3=0, f=0):
    """Pose das asas: ergue os três ossos (graus) e varre (f), espelhado."""
    out = {}
    for s, n in ((1, "L"), (-1, "R")):
        out[f"w{n}1"] = {"y": -a1*s, "z": f*s}; out[f"w{n}2"] = {"y": -a2*s}; out[f"w{n}3"] = {"y": -a3*s}
    return out

FOLD = wp(-14, -10, -6, 26)   # asas meio recolhidas para trás
BASE = {"spine": {"x": 2}, "chest": {"x": 0}, "neck": {"x": 2}, "head": {"x": 4},
        "thigh.L": {"x": -6, "y": -6}, "thigh.R": {"x": 6, "y": 6}, "shin.L": {"bend": 8}, "shin.R": {"bend": 6},
        "foot.L": {"z": 6}, "foot.R": {"z": -6},
        "upper_arm.L": {"y": 22, "x": -20, "z": -10}, "forearm.L": {"bend": -30}, "hand.L": {"x": -6},
        "upper_arm.R": {"y": -18, "x": -26}, "forearm.R": {"bend": -34}, "hand.R": {"x": -5},
        "glow": {"v": 1}, "lamp": {"v": 0}}

def M(*p): return merge(BASE, FOLD, *p)

def breath(t, amp=1.0):
    c = math.sin(2*math.pi*t); c2 = math.sin(2*math.pi*t + 1.2); c3 = math.sin(2*math.pi*t + 2.4)
    return merge({"spine": {"x": -.8*c*amp}, "chest": {"x": -1.6*c*amp}, "head": {"x": 1*c*amp, "z": 1.5*math.sin(2*math.pi*t - .6)*amp},
                  "upper_arm.L": {"y": -1*c*amp}, "upper_arm.R": {"x": -1.2*c*amp}, "hand.R": {"x": 1.5*c2*amp},
                  "tab1": {"x": .8*c2*amp}, "tab2": {"x": 1.6*c3*amp}, "bk1": {"x": -.8*c2*amp}, "bk2": {"x": -1.6*c3*amp}},
                 wp(5*c*amp, 3*c2*amp, 4*c3*amp, 2*c2*amp))

def anims(R):
    MN = [b for b in R.B if b.startswith("mo")]
    n = 8
    idle = [M(breath(i/n), mote_pose(MN[:6], i/n, rise=.5, seed=5)) for i in range(n)]

    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 22*s
        walk.append(M(wp(3*c, 4*s, 3*s, 0), {"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                       "shin.L": {"bend": 8 + 40*max(0, c)**1.3}, "shin.R": {"bend": 8 + 40*max(0, -c)**1.3},
                       "foot.L": {"x": .3*th - 10*max(0, c)}, "foot.R": {"x": -.3*th - 10*max(0, -c)},
                       "hips": {"z": 6*s, "y": 2*c}, "chest": {"z": -7*s, "x": 1.5*abs(c)}, "head": {"z": 4*s},
                       "upper_arm.R": {"x": -6*s}, "hand.R": {"x": 3*c}, "upper_arm.L": {"x": 12*s}, "forearm.L": {"bend": -6*max(0, s)},
                       "tab1": {"x": 6*s}, "tab2": {"x": 8*math.sin(t - .8)}, "bk1": {"x": -5*s}, "bk2": {"x": -7*math.sin(t - .8)}}))

    # ataque: recua e ergue o montante sobre o ombro (antecipação), corte diagonal com as asas abrindo, arrasto, volta
    wind = M(wp(10, 4, 2, 6), {"upper_arm.R": {"x": -150, "y": 30}, "forearm.R": {"bend": -70}, "hand.R": {"x": -25},
                               "upper_arm.L": {"x": -110, "y": 10, "z": -30}, "forearm.L": {"bend": -76},
                               "chest": {"z": -30, "x": -10}, "spine": {"z": -10, "x": -4}, "head": {"z": 12, "x": -4},
                               "thigh.L": {"x": -16}, "shin.L": {"bend": 14}, "thigh.R": {"x": 14}, "shin.R": {"bend": 18}, "root": (0, .06, -.02)})
    cut = M(wp(36, 10, 6, -20), {"upper_arm.R": {"x": -40, "y": 8, "z": 34}, "forearm.R": {"bend": -6}, "hand.R": {"x": 12},
                                "upper_arm.L": {"x": -50, "y": -10, "z": 40}, "forearm.L": {"bend": -30},
                                "chest": {"z": 32, "x": 18}, "spine": {"x": 10, "z": 10}, "head": {"z": -10, "x": -6},
                                "thigh.L": {"x": -34}, "shin.L": {"bend": 24}, "thigh.R": {"x": 20}, "root": (0, -.24, -.04),
                                "tab1": {"x": -14}, "tab2": {"x": -10}, "bk1": {"x": 16}, "bk2": {"x": 12}})
    drag = merge(cut, {"upper_arm.R": {"x": 16, "z": 8}, "chest": {"z": 6, "x": 4}, "tab1": {"x": 18}, "tab2": {"x": 14}}, wp(-8, -2, 4, 6))
    attack = keys_to_frames([(0, M()), (.22, wind), (.32, merge(wind, {"chest": {"z": -4}, "upper_arm.R": {"x": -6}})), (.46, cut),
                             (.6, drag), (.8, lerp_pose(drag, M(), .5)), (1, M())], 10)

    # carga (laço de 4 s no jogo): montante erguido acima da cabeça, asas abertas no alto, a aura e a luz pulsando
    HOLD = {"upper_arm.R": {"x": -172, "y": 8}, "forearm.R": {"bend": -14}, "hand.R": {"x": -8},
            "upper_arm.L": {"x": -168, "y": -14, "z": -10}, "forearm.L": {"bend": -22}, "hand.L": {"x": -10},
            "spine": {"x": -6}, "chest": {"x": -10}, "head": {"x": -16},
            "thigh.L": {"x": -18, "y": -10}, "thigh.R": {"x": 12, "y": 10}, "shin.L": {"bend": 18}, "shin.R": {"bend": 14},
            "tab1": {"x": -6}, "bk1": {"x": 8}}
    charge = []
    for i in range(8):
        t = i/8; b = math.sin(2*math.pi*t); v = math.sin(6*math.pi*t)
        charge.append(merge(BASE, wp(48 + 6*b, 16 + 3*b, 10 + 2*b, -22), HOLD, mote_pose(MN, t, rise=.9, drift=.12, seed=7, life=(.4, .7)),
                            {"chest": {"x": 1.5*v, "z": 1.5*math.cos(6*math.pi*t)}, "head": {"x": 2*v}, "root": (0, 0, .02*b),
                             "aura": {"vis": 1, "inf": .1*b + .05*v, "z": 360*t/2}, "aim": {"sword": (0, .05, 1)},
                             "glow": {"v": 1.2 + .5*(.5 + .5*b)}, "lamp": {"v": .55 + .25*(.5 + .5*b) + .1*v},
                             "tab2": {"x": 3*v}, "bk2": {"x": -3*v}}))

    # golpe: ergue mais um pouco, desce o montante no chão à frente, a aura vira uma onda de luz no chão e some
    def fx(p, **kw):   # troca (não soma) as chaves de efeito
        p = dict(p); p.update(kw); return p
    pre = fx(merge(charge[0], {"spine": {"x": -8}, "chest": {"x": -10}, "head": {"x": -6}}, wp(10, 4, 4, 0)),
             aura={"vis": 1, "inf": .45}, glow={"v": 1.6}, lamp={"v": 1.1})
    slam = merge(BASE, wp(18, 6, 2, -36), {"upper_arm.R": {"x": -55, "y": -8}, "forearm.R": {"bend": -8}, "hand.R": {"x": 30},
                 "upper_arm.L": {"x": -60, "y": 12, "z": 14}, "forearm.L": {"bend": -12}, "hand.L": {"x": 25},
                 "spine": {"x": 14}, "chest": {"x": 16}, "head": {"x": 6},
                 "thigh.L": {"x": -40}, "shin.L": {"bend": 42}, "thigh.R": {"x": 22}, "shin.R": {"bend": 18}, "foot.R": {"x": -10},
                 "root": (0, -.3, -.04), "aim": {"sword": (0, -1, -.45)}, "tab1": {"x": 20}, "tab2": {"x": 14}, "bk1": {"x": -12}})
    mid = fx(merge(lerp_pose(pre, slam, .5), {}), aura={"vis": 1, "inf": .5}, glow={"v": 2.4}, lamp={"v": 1.4})
    mid.pop("aim", None); mid = merge(mid, {"aim": {"sword": (0, -.6, .8)}})
    hitg = fx(slam, aura={"vis": 1, "inf": .7}, glow={"v": 3.0}, lamp={"v": 1.8})
    burst = fx(merge(slam, {"chest": {"x": 2}}, wp(14, 4, 2, 0)), aura={"vis": 1, "inf": .9}, onda={"vis": 1, "inf": .2},
               glow={"v": 2.6}, lamp={"v": 2.0})
    burst2 = fx(merge(slam, {"chest": {"x": -2}, "tab1": {"x": -8}, "tab2": {"x": -6}}), onda={"vis": 1, "inf": 1.4},
                glow={"v": 1.4}, lamp={"v": .5})
    after = fx(merge(slam, {"chest": {"x": -6}, "head": {"x": -8}, "tab1": {"x": -14}, "tab2": {"x": -10}}),
               onda={"vis": .6, "inf": 2.4}, glow={"v": .6}, lamp={"v": 0})
    after2 = fx(merge(slam, {"chest": {"x": -6}, "head": {"x": -8}}), glow={"v": .6}, lamp={"v": 0})
    rec = lambda k: fx(lerp_pose(after2, M(), k), glow={"v": .6 + .4*k}, lamp={"v": 0})
    release = [pre, mid, hitg, burst, burst2, after, rec(.25), rec(.55), rec(.82), M()]

    hitp = M(wp(26, 12, 10, -8), {"chest": {"x": -16, "z": 8}, "spine": {"x": -6}, "head": {"x": -18, "z": 12},
                                  "upper_arm.L": {"y": -10, "x": 18}, "upper_arm.R": {"y": 16, "x": 14}, "root": (0, .08, 0),
                                  "tab1": {"x": -10}, "bk1": {"x": 10}})
    hit = [lerp_pose(M(), hitp, .7), hitp, lerp_pose(hitp, M(), .5), M()]

    # morte: espasmo das asas, cai de joelhos, a cabeça pende, tomba de lado sobre uma asa; a luz astral apaga
    spasm = M(wp(60, 20, 10, -24), {"chest": {"x": -24}, "head": {"x": -30}, "upper_arm.L": {"x": -60, "y": -40},
                                    "upper_arm.R": {"x": -60, "y": 40}, "root": (0, .05, 0), "glow": {"v": .6}})
    kneel = M(wp(6, -10, -6, 30), {"thigh.L": {"x": -80}, "thigh.R": {"x": -70}, "shin.L": {"bend": 105}, "shin.R": {"bend": 110},
                                   "chest": {"x": 18}, "head": {"x": 30}, "upper_arm.R": {"x": 10, "y": -10}, "forearm.R": {"bend": -10},
                                   "upper_arm.L": {"x": 10, "y": 10}, "glow": {"v": -.3}, "tab1": {"x": -30}})
    fall = merge(kneel, {"hips": {"x": 30, "y": 30}, "spine": {"x": 10}, "ground": .1, "glow": {"v": -.3}})
    down = {"hips": {"x": 8, "y": 84}, "spine": {"x": 6}, "chest": {"x": 4}, "head": {"z": -20, "x": 14},
            "upper_arm.L": {"x": -40, "y": 30}, "upper_arm.R": {"x": -80, "y": -40}, "forearm.L": {"bend": -30}, "forearm.R": {"bend": -10},
            "thigh.L": {"x": -40}, "thigh.R": {"x": -20}, "shin.L": {"bend": 70}, "shin.R": {"bend": 40}, "ground": .05,
            "gb": ["hips", "spine", "chest", "head", "thigh.L", "thigh.R", "shin.L", "shin.R"], "glow": {"v": 0}, "lamp": {"v": 0}}
    down = merge(down, wp(-6, -4, -2, 40))
    death = keys_to_frames([(0, hitp), (.15, spasm), (.32, merge(spasm, {"head": {"x": -6}})), (.5, kneel), (.68, fall), (.86, down), (1, down)], 14)
    return {"idle": idle, "walk": walk, "attack": attack, "charge": charge, "release": release, "hit": hit, "death": death}
