# Vigilante (evento "O Cume dos Vigilantes", Monte Hermon; design em entregas/evento_hermon/).
# Um dos duzentos que desceram no Hermon e juraram lá (Livro de Enoque). O Coro afrouxou as correntes deles para
# ganhar a guerra; agora, toda vez que renovam o juramento, o cume desmorona e eles caçam quem subiu.
# Anjo alto e magro (~2,1 m), cinzento de cinza: sobretudo longo de lã encharcada de cinza, aberto na frente e
# rasgado na barra; arreio de couro cruzado no peito com fivelas de latão; calça de couro e botas de cano alto com
# fivelas; algemas de ferro nos dois pulsos com a corrente partida pendurada; venda de pano escrita no rosto com
# um lacre de cera no meio da testa (o juramento); asas grandes de penas sujas com as pontas queimadas e uma
# corrente enrolada no osso da asa; foice-falx forjada na mão direita (Azazel ensinou o ferro aos homens).
# Brilho: só a luz do juramento (branco-dourado), nos dois lacres (testa e peito). Contraluz fria.
# Variantes estilo MU (mesma base): vigilante_jurado (comum), vigilante_ferreiro (discípulo de Azazel: avental de
# couro de ferreiro, óculos de soldador de latão por cima da venda, fuligem) e vigilante_estrelado (elite, 1,15x,
# de Kokabiel: sobretudo azul-noite com constelações em rebites de latão e anéis de astrolábio atrás da cabeça).
# Animações: idle, walk, attack, hit, death + kneel (estátua ajoelhada, asas fechadas; loop parado), rise (levanta
# da estátua quando o juramento começa) e land (desce do céu de asas abertas: reforço quando um anel cai).
import bpy, bmesh, math, random, os
from mathutils import Vector, Quaternion
from mrig import *
from corvo_de_cinza import feathers, wings
from querubim_desfeito import glow

INFO = {"px": 288, "target_z": 1.15, "rim": (.62, .7, .95), "colors": 48, "samples": int(os.environ.get("AMOSTRAS", 40)),
        "loops": ("idle", "walk", "kneel"),
        "fps": {"idle": 6, "walk": 10, "attack": 12, "hit": 12, "death": 10, "kneel": 2, "rise": 10, "land": 12}}
SCALE = 1.17
JURA = (1.0, .82, .5)          # luz do juramento (lacres)

VARIANTS = {
    "vigilante_jurado": dict(coat=(.17, .16, .15), coat_stain=(.07, .06, .055), skin=(.42, .4, .38), feather=(.3, .29, .28),
                             scale=1.0, apron=False, goggles=False, stars=False, rings=False),
    "vigilante_ferreiro": dict(coat=(.085, .055, .035), coat_stain=(.02, .015, .012), skin=(.2, .185, .17), feather=(.12, .11, .1),
                               scale=1.0, apron=True, goggles=True, stars=False, rings=False),
    "vigilante_estrelado": dict(coat=(.022, .03, .06), coat_stain=(.01, .01, .02), skin=(.34, .33, .33), feather=(.24, .24, .25),
                                scale=1.15, apron=False, goggles=False, stars=True, rings=True),
}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name
set_variant("vigilante_jurado")

CHL = .07   # elo da corrente das algemas

def bones():
    B = humanoid(1.0, .96)
    for s, n in ((1, "L"), (-1, "R")):
        B[f"wing1.{n}"] = ((.07*s, .13, 1.42), (.34*s, .17, 1.6), "chest")
        B[f"wing2.{n}"] = ((.34*s, .17, 1.6), (.66*s, .2, 1.7), f"wing1.{n}")
        B[f"wing3.{n}"] = ((.66*s, .2, 1.7), (.96*s, .22, 1.66), f"wing2.{n}")
        h = Vector(B[f"hand.{n}"][0]) + Vector((0, 0, .03))
        B[f"cuff{n}1"] = (tuple(h), tuple(h + Vector((0, 0, -CHL))), f"forearm.{n}")
        B[f"cuff{n}2"] = (tuple(h + Vector((0, 0, -CHL))), tuple(h + Vector((0, 0, -2*CHL))), f"cuff{n}1")
        B[f"cuff{n}3"] = (tuple(h + Vector((0, 0, -2*CHL))), tuple(h + Vector((0, 0, -3*CHL))), f"cuff{n}2")
    return B

class VRig(Rig):
    """A corrente das algemas sempre pende para baixo (com um balanço), depois da pose do corpo."""
    def set_pose(self, pose, frame):
        super().set_pose(pose, frame)
        bpy.context.view_layer.update()
        pbs = self.arm.pose.bones
        sw = pose.get("chain_sway") or 0
        for n in ("L", "R"):
            for i in (1, 2, 3):
                pb = pbs[f"cuff{n}{i}"]
                d = Vector((math.sin(math.radians(sw*i)), .25*math.cos(math.radians(sw*i*1.3)), -1)).normalized()
                cur = (pb.tail - pb.head).normalized()
                M = pb.matrix.copy(); R3 = cur.rotation_difference(d).to_matrix() @ M.to_3x3()
                M2 = R3.to_4x4(); M2.translation = M.translation; pb.matrix = M2
                bpy.context.view_layer.update()
                pb.keyframe_insert("rotation_quaternion", frame=frame)
OVERRIDE.add("chain_sway")

def build():
    rr = random.Random(23)
    pele = stained("vg_pele" + V["name"], V["skin"], stain=(.08, .07, .07), amount=.45, scale=6, rough=.65,
                   blotch=(.16, .15, .15), blotch_amt=.6, grime=1.1)
    casaco = stained("vg_casaco" + V["name"], V["coat"], stain=V["coat_stain"], amount=.6, scale=3, rough=.95, grime=1.4,
                     blotch=(.2, .19, .18), blotch_amt=.45)
    forro = stained("vg_forro", (.06, .02, .02), stain=(.02, .01, .01), amount=.4, scale=4, rough=.9, grime=.8)
    couro = stained("vg_couro", (.07, .045, .03), stain=(.02, .015, .01), amount=.5, scale=4, rough=.5, grime=1.0)
    ferro = stained("vg_ferro", (.09, .08, .075), stain=(.22, .08, .03), amount=.6, scale=7, metal=.85, rough=.55, grime=.5)
    aco = stained("vg_aco", (.34, .33, .32), stain=(.2, .07, .03), amount=.5, scale=8, metal=1, rough=.38, grime=.3)
    latao = stained("vg_latao", (.4, .26, .1), stain=(.08, .06, .03), amount=.45, scale=7, metal=1, rough=.42, grime=.4)
    pano = stained("vg_venda", (.42, .38, .32), stain=(.12, .07, .04), amount=.6, scale=5, rough=.95, grime=1.2)
    tinta = mat("vg_tinta", (.03, .025, .02), 0, .9)
    cera = mat("vg_cera", (.3, .05, .03), 0, .35)
    luz = glow("vg_juramento", JURA, 9)
    pena = stained("vg_pena" + V["name"], V["feather"], stain=(.04, .038, .036), amount=.5, scale=5, rough=.85,
                   blotch=(.36, .35, .33), blotch_amt=.5, grime=.3)
    queim = stained("vg_queimado", (.025, .022, .02), stain=(.14, .05, .02), amount=.35, scale=9, rough=.9, grime=0)
    lente = mat("vg_lente", (.05, .07, .06), .2, .15)

    B = bones(); R = VRig(V["name"], B); P = R.P
    R.gexclude = {f"cuff{n}{i}" for n in "LR" for i in (1, 2, 3)} | {f"wing{k}.{n}" for k in (1, 2, 3) for n in "LR"}
    # ------------------------------------------------ pernas (calça de couro justa) e botas de cano alto
    j = {"pelvis": (0, 0, .93, .15, .11)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .085); j[f"th{n}"] = (*h.lerp(k, .5), .075); j[f"knee{n}"] = (*k, .058)
        j[f"calf{n}"] = (*(k.lerp(a, .35) + Vector((0, .02, 0))), .062); j[f"ank{n}"] = (*a, .045)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"th{n}"), (f"th{n}", f"knee{n}"), (f"knee{n}", f"calf{n}"), (f"calf{n}", f"ank{n}")]
    legs = skin_mesh("pernas", j, e, couro); R.bind(legs, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R"])
    for s, n in ((1, "L"), (-1, "R")):
        k, a, t = P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        bt = [along("primitive_cylinder_add", couro, k.lerp(a, .15) + Vector((0, 0, 0)), a + Vector((0, 0, -.02)), .07, vertices=12)]
        for tt in (.3, .55, .8):  # fivelas do cano
            bt.append(prim("primitive_torus_add", couro, k.lerp(a, tt + .1), (1, 1, .7), major_radius=.073, minor_radius=.01,
                           major_segments=12, minor_segments=4))
            bt.append(prim("primitive_cube_add", latao, k.lerp(a, tt + .1) + Vector((.055*s, -.04, 0)), (.014, .006, .016)))
        bt.append(prim("primitive_torus_add", couro, k.lerp(a, .12), (1, 1, 1.4), major_radius=.078, minor_radius=.016,
                       major_segments=12, minor_segments=4))
        R.rigid(bt, f"shin.{n}")
        fj = {"ank": (*a, .055), "mid": (*a.lerp(t, .5), .058, .045), "toe": (*(t + Vector((0, -.02, -.005))), .05, .035),
              "heel": (*(a + Vector((0, .04, -.035))), .05)}
        f = skin_mesh(f"bota.{n}", fj, [("ank", "mid"), ("mid", "toe"), ("ank", "heel")], couro)
        R.bind(f, [f"shin.{n}", f"foot.{n}"])
        sola = prim("primitive_cube_add", ferro, a.lerp(t, .45) + Vector((0, 0, -.06)), (.05, .11, .012))
        R.rigid([sola], f"foot.{n}")

    # ------------------------------------------------ tronco magro dentro do sobretudo; mangas do sobretudo
    t = {"pelvis": (0, 0, .97, .16, .12), "belly": (0, 0, 1.1, .15, .11), "chest": (0, .0, 1.3, .19, .13),
         "neck": (0, -.01, 1.5, .065), "neck2": (0, -.015, 1.57, .055)}
    te = [("pelvis", "belly"), ("belly", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, .02))), .085); t[f"bi{n}"] = (*sh.lerp(el, .5), .07)
        t[f"el{n}"] = (*el, .06); t[f"fa{n}"] = (*el.lerp(wr, .5), .062); t[f"wr{n}"] = (*wr.lerp(el, .08), .066)
        te += [("chest", f"sh{n}"), (f"sh{n}", f"bi{n}"), (f"bi{n}", f"el{n}"), (f"el{n}", f"fa{n}"), (f"fa{n}", f"wr{n}")]
    torso = skin_mesh("tronco", t, te, casaco)
    R.bind(torso, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])
    # gola alta virada e lapelas
    gola = skirt("gola", casaco, [(1.47, .13, .11, .0), (1.56, .12, .105, .01), (1.64, .135, .12, .025)], seg=20,
                 open_front=.55, thick=.014)
    R.bind(gola, ["chest", "neck"], power=4)
    # sobretudo: barra até o meio da canela, aberto na frente, rasgado
    hem = .3 if not V["apron"] else .42
    sk = skirt("sobretudo", casaco, [(1.06, .175, .135, 0), (.96, .2, .155, .01), (.72, .25, .2, .02), (.5, .29, .23, .03),
                                     (hem, .32, .25, .04)], open_front=.42, seg=30, jag=.06, seed=4, thick=.016)
    R.bind(sk, ["hips", "spine", "thigh.L", "thigh.R", "shin.L", "shin.R"], power=3)
    fr = skirt("forro", forro, [(.96, .193, .148, .01), (.72, .243, .193, .02), (.5, .283, .223, .03), (hem + .03, .313, .243, .04)],
               open_front=.45, seg=30, jag=.04, seed=4, thick=0)
    R.bind(fr, ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R"], power=3)
    # punhos do sobretudo dobrados
    for n in ("L", "R"):
        o_, ax, u, sd = R.frame(f"forearm.{n}"); L = (P(f"forearm.{n}", 1) - P(f"forearm.{n}")).length
        cf = prim("primitive_cylinder_add", casaco, o_ + ax*L*.82, (.078, .078, .04), vertices=14)
        cf.rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        R.rigid([cf], f"forearm.{n}")

    ch = []
    # arreio de couro cruzado no peito (X na frente e nas costas) com fivelas e argolas de latão
    for sy in (-1, 1):
        y = .135*sy
        for a_, b_ in (((.17, y, 1.47), (-.15, y, 1.03)), ((-.17, y, 1.47), (.15, y, 1.03))):
            ch.append(along("primitive_cube_add", couro, a_, b_, .022))
        ch.append(prim("primitive_torus_add", latao, (0, y*1.05, 1.25), (1, 1, 1), major_radius=.032, minor_radius=.008,
                       major_segments=10, minor_segments=4, rot=(90, 0, 0)))
    for s in (1, -1):
        ch.append(prim("primitive_cube_add", latao, (.1*s, -.142, 1.36), (.02, .006, .016), rot=(0, 0, 0)))
    # cinto largo com fivela
    ch.append(prim("primitive_cylinder_add", couro, (0, 0, 1.0), (.168, .128, .035), vertices=22))
    ch.append(prim("primitive_cube_add", latao, (0, -.13, 1.0), (.035, .008, .03)))
    # lacre de cera do juramento no peito (centro do X), com a luz no meio e fitas de pergaminho
    ch.append(prim("primitive_cylinder_add", cera, (0, -.152, 1.25), (.04, .04, .012), vertices=14, rot=(90, 0, 0)))
    ch.append(prim("primitive_uv_sphere_add", luz, (0, -.164, 1.25), (.016, .006, .016), segments=8, ring_count=5))
    for k in range(2):
        ch.append(prim("primitive_cube_add", pano, (.02 - .04*k, -.15, 1.17 - .02*k), (.014, .004, .07), rot=(0, 0, 12 - 24*k)))
    if V["apron"]:  # avental de couro de ferreiro com bolso e marcas de queimado
        ap = skirt("avental", couro, [(1.32, .15, .14, -.005), (1.05, .17, .15, -.01), (.7, .22, .19, -.02), (.42, .25, .21, -.03)],
                   open_front=0, seg=24, thick=.012)
        # só a metade da frente: apaga os vértices de trás
        bm = bmesh.new(); bm.from_mesh(ap.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y > -.04], context='VERTS'); bm.to_mesh(ap.data); bm.free()
        R.bind(ap, ["hips", "spine", "chest", "thigh.L", "thigh.R"], power=3)
        ch.append(prim("primitive_cube_add", couro, (.05, -.19, .86), (.07, .01, .05)))
        for k in range(4):
            ch.append(prim("primitive_uv_sphere_add", queim, (rr.uniform(-.14, .14), -.2, rr.uniform(.55, 1.05)), (.03, .006, .025),
                           segments=8, ring_count=4))
    if V["stars"]:  # constelações de rebites de latão no sobretudo (frente e costas)
        for k in range(46):
            a = rr.uniform(0, 2*math.pi); z = rr.uniform(.45, 1.42)
            rx, ry = (.2 + .1*(1.0 - z)/.6, .15 + .08*(1.0 - z)/.6) if z < 1.0 else (.19, .135)
            if math.sin(a) < -.5 and z < 1.0: continue   # abertura da frente
            q = Vector((rx*1.04*math.cos(a), ry*1.06*math.sin(a) + (.02 if z < 1 else 0), z))
            ch.append(prim("primitive_uv_sphere_add", latao, q, (.009, .009, .009), segments=6, ring_count=4))
    R.rigid(ch, "spine")

    # ------------------------------------------------ cabeça: magra, cabelo comprido sujo, venda escrita, lacre na testa
    hc = Vector((0, -.02, 1.7))
    hd = [prim("primitive_uv_sphere_add", pele, hc, (.09, .1, .118), segments=18, ring_count=12)]
    hd.append(prim("primitive_uv_sphere_add", pele, hc + Vector((0, -.045, -.075)), (.06, .06, .05), segments=12, ring_count=8))  # queixo
    for s in (1, -1):  # maçãs fundas
        hd.append(prim("primitive_uv_sphere_add", pele, hc + Vector((.055*s, -.06, -.02)), (.025, .02, .03), segments=8, ring_count=5))
    nose = along("primitive_cone_add", pele, hc + Vector((0, -.095, .0)), hc + Vector((0, -.12, -.04)), .018, vertices=6,
                 radius1=1, radius2=.4)
    hd.append(nose)
    hd.append(prim("primitive_cube_add", tinta, hc + Vector((0, -.088, -.07)), (.03, .006, .004)))   # boca fina e escura
    # cabelo comprido escorrido (mechas) caindo nas costas e nos ombros
    cab = stained("vg_cabelo" + V["name"], (.05, .048, .045) if V["name"] != "vigilante_estrelado" else (.3, .3, .3),
                  stain=(.02, .02, .02), amount=.3, scale=6, rough=.7, grime=.4)
    hd.append(prim("primitive_uv_sphere_add", cab, hc + Vector((0, .045, .035)), (.094, .088, .1), segments=16, ring_count=10))
    for k in range(16):
        a = math.radians(-70 + 140*k/15)
        top = hc + Vector((.095*math.sin(a), .02 + .085*math.cos(a), .06))
        bot = top + Vector((.03*math.sin(a), .05 + .03*math.cos(a), -.26 - .1*rr.random()))
        hd.append(along("primitive_cone_add", cab, top, bot, .022, vertices=5, radius1=1, radius2=.25))
    # venda de pano em volta dos olhos, escrita, com as pontas soltas atrás
    vd = prim("primitive_cylinder_add", pano, hc + Vector((0, -.005, .015)), (.1, .108, .028), vertices=20)
    hd.append(vd)
    for k in range(7):  # letras do juramento (traços de tinta)
        a = math.radians(-60 + 120*k/6)
        hd.append(prim("primitive_cube_add", tinta, hc + Vector((.102*math.sin(a), -.109*math.cos(a) - .004, .015 + .008*((k % 3) - 1))),
                       (.006, .003, .01), rot=(0, 0, math.degrees(a))))
    for s in (1, -1):
        hd.append(prim("primitive_cube_add", pano, hc + Vector((.03*s, .12, -.04)), (.016, .006, .09), rot=(10, 0, 18*s)))
    hd.append(prim("primitive_cylinder_add", cera, hc + Vector((0, -.112, .05)), (.024, .024, .01), vertices=12, rot=(90, 0, 0)))
    hd.append(prim("primitive_uv_sphere_add", luz, hc + Vector((0, -.121, .05)), (.01, .004, .01), segments=8, ring_count=4))
    if V["goggles"]:  # óculos de soldador de latão por cima da venda
        for s in (1, -1):
            g = prim("primitive_cylinder_add", latao, hc + Vector((.042*s, -.11, .015)), (.032, .032, .022), vertices=14, rot=(90, 0, 0))
            hd.append(g)
            hd.append(prim("primitive_cylinder_add", lente, hc + Vector((.042*s, -.124, .015)), (.025, .025, .006), vertices=14, rot=(90, 0, 0)))
        hd.append(prim("primitive_cube_add", couro, hc + Vector((0, -.112, .015)), (.012, .008, .008)))
    if V["rings"]:  # anéis de astrolábio de latão atrás da cabeça, inclinados
        rc = hc + Vector((0, .1, .08))
        for k, (r, rot) in enumerate(((.2, (70, 0, 0)), (.165, (70, 35, 0)), (.13, (75, -40, 0)))):
            hd.append(prim("primitive_torus_add", latao, rc, (1, 1, 1), major_radius=r, minor_radius=.007,
                           major_segments=40, minor_segments=4, rot=rot))
        hd.append(along("primitive_cylinder_add", ferro, hc + Vector((0, .07, .0)), rc, .008, vertices=5))
        for k in range(7):
            a = 2*math.pi*k/7
            hd.append(prim("primitive_uv_sphere_add", latao, rc + Vector((.2*math.cos(a), .2*math.sin(a)*.34, .2*math.sin(a)*.94)),
                           (.012, .012, .012), segments=6, ring_count=4))
    R.rigid(hd, "head")

    # ------------------------------------------------ mãos cinzentas e magras, algemas com corrente partida
    for n, s in (("L", 1), ("R", -1)):
        o_, ax, u, sd = R.frame(f"hand.{n}")
        g = [prim("primitive_uv_sphere_add", pele, o_ + ax*.04, (.04, .05, .06), segments=10, ring_count=8)]
        g[0].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        for k in range(4):  # dedos compridos dobrados
            base = o_ + ax*.08 + sd*(.02*(k - 1.5))
            g.append(along("primitive_cylinder_add", pele, base, base + ax*.05 - u*.03, .009, vertices=5))
        R.rigid(g, f"hand.{n}")
        o_, ax, u, sd = R.frame(f"forearm.{n}"); L = (P(f"forearm.{n}", 1) - P(f"forearm.{n}")).length
        cuf = [prim("primitive_cylinder_add", ferro, o_ + ax*L*.93, (.07, .07, .04), vertices=16)]
        cuf[0].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
        for k in range(2):
            rv = prim("primitive_uv_sphere_add", latao, o_ + ax*L*.93 + sd*.07*(1 if k else -1), (.012, .012, .012), segments=6, ring_count=4)
            cuf.append(rv)
        R.rigid(cuf, f"forearm.{n}")
        for i in (1, 2, 3):
            o2, ax2, u2, sd2 = R.frame(f"cuff{n}{i}")
            lk = prim("primitive_torus_add", ferro, o2 + ax2*CHL*.5, (1, 1.6, 1), major_radius=.022, minor_radius=.008,
                      major_segments=10, minor_segments=4)
            q = ax2.to_track_quat('Z', 'Y') @ Quaternion((0, 0, 1), math.radians(90*(i % 2)))
            lk.rotation_euler = (q @ Quaternion((1, 0, 0), math.radians(90))).to_euler()
            R.rigid([lk], f"cuff{n}{i}")

    # ------------------------------------------------ falx forjada na mão direita (haste + lâmina curva para dentro)
    o_, ax, u, sd = R.frame("hand.R")
    gp = o_ + ax*.05
    fx = [along("primitive_cylinder_add", couro, gp - u*.18, gp + u*.5, .016, vertices=8)]       # cabo enfaixado
    for k in range(6):
        fx.append(prim("primitive_torus_add", couro, gp + u*(-.15 + .08*k), (1, 1, 1), major_radius=.019, minor_radius=.006,
                       major_segments=8, minor_segments=4, rot=(90, 0, 0)))
    fx.append(prim("primitive_cylinder_add", latao, gp + u*.52, (.026, .026, .02), vertices=10, rot=(90, 0, 0)))
    # lâmina: tira curva afinando, forjada (bm de quads)
    bm = bmesh.new(); prev = None; N = 14
    for i in range(N + 1):
        tt = i/N; ang = math.radians(-10 + 120*tt)
        c = gp + u*(.54 + .34*math.sin(ang)) + ax*(.28*(1 - math.cos(ang)) + .02)
        w = .065*(1 - .75*tt) + .008
        a_ = bm.verts.new(c - sd*.004); b_ = bm.verts.new(c + ax*w*.0 + (u*math.cos(ang)*-1 + ax*math.sin(ang)).normalized()*-w*.0 + sd*.004)
        e_ = c + (ax*math.cos(ang) - u*math.sin(ang)).normalized()*w
        cc = bm.verts.new(e_)
        row = (a_, cc)
        if prev:
            bm.faces.new((prev[0], prev[1], row[1], row[0]))
        prev = row
        bm.verts.remove(b_)
    bl = obj_from_bm("falx", bm, aco)
    sdm = bl.modifiers.new("s", 'SOLIDIFY'); sdm.thickness = .012; apply_mods(bl)
    fx.append(bl)
    R.rigid(fx, "hand.R")

    # ------------------------------------------------ asas grandes, penas sujas de pontas queimadas, corrente no osso
    DN = Vector((0, -1, 0)); rnd = random.Random(5)
    for s, n in ((1, "L"), (-1, "R")):
        X = lambda v: Vector((v[0]*s, v[1], v[2]))
        lj = {"a": (*X((.07, .13, 1.42)), .045, .035), "b": (*X((.34, .17, 1.6)), .04, .03),
              "c": (*X((.66, .2, 1.7)), .03, .022), "d": (*X((.96, .22, 1.66)), .016)}
        le = skin_mesh(f"borda.{n}", lj, [("a", "b"), ("b", "c"), ("c", "d")], pena, levels=1)
        R.bind(le, ["chest", f"wing1.{n}", f"wing2.{n}", f"wing3.{n}"], power=6)
        prim_specs = []
        for i in range(9):
            t_ = i/8
            base = X((.96 - .3*t_, .22 - .01*t_, 1.66 - .03*t_))
            ang = math.radians(14 + 66*t_)
            d = X((math.cos(ang), .14, -math.sin(ang)))
            prim_specs.append((base + Vector((0, .004*i, 0)), d, DN, (.78 - .1*t_)*rnd.uniform(.88, 1.05), .1, rnd.uniform(.55, .75), -.07))
        sec = [(X((.66 - .3*(k + .5)/6, .18 + .002*k, 1.68 - .08*(k + .5)/6)), X((.1, .16, -1)), DN,
                rnd.uniform(.62, .72), .11, rnd.uniform(.55, .75), -.05) for k in range(6)]
        ter = [(X((.34 - .26*(k + .5)/5, .14 + .002*k, 1.58 - .13*(k + .5)/5)), X((-.05, .16, -1)), DN,
                rnd.uniform(.55, .65), .1, rnd.uniform(.6, .8), -.04) for k in range(5)]
        cov = {1: [], 2: [], 3: []}
        for k in range(16):
            t_ = (k + .5)/16; x = .08 + .86*t_
            bn = 1 if x < .34 else (2 if x < .66 else 3)
            z = 1.42 + (1.68 - 1.42)*min(1, t_*1.4)
            cov[bn].append((X((x, .16 + .03*t_ - .012, z)), X((.08, .1, -1)), DN, rnd.uniform(.2, .26), .09, .9, -.03))
        R.rigid([feathers(f"prim.{n}", prim_specs, pena, queim, rnd), feathers(f"cob3.{n}", cov[3], pena, queim, rnd)], f"wing3.{n}")
        R.rigid([feathers(f"sec.{n}", sec, pena, queim, rnd), feathers(f"cob2.{n}", cov[2], pena, queim, rnd)], f"wing2.{n}")
        # corrente enrolada no primeiro osso da asa (as correntes afrouxadas)
        pa, pb = Vector(lj["a"][:3]), Vector(lj["b"][:3]); dv = (pb - pa).normalized()
        sdv = dv.cross(Vector((0, 0, 1))).normalized(); upv = sdv.cross(dv)
        links = []
        for k in range(9):
            tt = .15 + .7*k/8; ang = k*1.1
            c = pa.lerp(pb, tt) + (sdv*math.cos(ang) + upv*math.sin(ang))*.05
            lk = prim("primitive_torus_add", ferro, c, (1, 1.5, 1), major_radius=.02, minor_radius=.007, major_segments=8, minor_segments=4)
            lk.rotation_euler = (dv.to_track_quat('Z', 'Y') @ Quaternion((0, 0, 1), ang + (k % 2)*1.57)).to_euler(); links.append(lk)
        R.rigid([feathers(f"ter.{n}", ter, pena, queim, rnd), feathers(f"cob1.{n}", cov[1], pena, queim, rnd)] + links, f"wing1.{n}")

    sc = SCALE*V["scale"]
    R.arm.scale = [sc]*3
    return R, INFO

# ======================================================================= animações
# Postura: alto, curvado para a frente como quem procura, falx baixa ao lado, asas meio abertas e caídas.
WREST = wings(-22, -14, -18, 40, 26, 16)
BASE = merge({"spine": {"x": 6}, "chest": {"x": 8}, "neck": {"x": 8}, "head": {"x": 6},
              "thigh.L": {"y": -4}, "thigh.R": {"y": 4}, "shin.L": {"bend": 6}, "shin.R": {"bend": 6},
              "upper_arm.L": {"y": 22, "x": -6}, "upper_arm.R": {"y": -26, "x": -12}, "forearm.L": {"bend": -16},
              "forearm.R": {"bend": -34}, "hand.R": {"x": 10}}, WREST)
def M(*p): return merge(BASE, *p)

def anims(R):
    out = {}
    out["idle"] = [M({"chest": {"x": -2.5*math.sin(i/6*2*math.pi)}, "head": {"z": 6*math.sin(i/6*2*math.pi), "x": 2*math.cos(i/6*2*math.pi)}},
                     wings(4*math.sin(i/6*2*math.pi), 3*math.sin(i/6*2*math.pi - .6), 3*math.sin(i/6*2*math.pi - 1.2)),
                     {"chain_sway": 8*math.sin(i/6*2*math.pi)}) for i in range(6)]
    walk = []
    for i in range(8):
        t = i/8*2*math.pi; s, c = math.sin(t), math.cos(t); th = 24*s
        walk.append(M({"thigh.L": {"x": -th}, "thigh.R": {"x": th},
                       "shin.L": {"bend": 6 + 44*max(0, c)**1.4}, "shin.R": {"bend": 6 + 44*max(0, -c)**1.4},
                       "foot.L": {"x": .3*th - 10*max(0, c)}, "foot.R": {"x": -.3*th - 10*max(0, -c)},
                       "hips": {"z": 6*s}, "chest": {"z": -7*s, "x": 4}, "head": {"z": 4*s},
                       "upper_arm.L": {"x": 18*s}, "upper_arm.R": {"x": -8*s}},
                      wings(6*c, 4*c, 3*c, 4*s, 2*s, 0), {"chain_sway": 18*s}))
    out["walk"] = walk
    # ataque: recolhe a falx atrás do ombro e corta na diagonal, as asas abrem para dar impulso
    wind = M({"upper_arm.R": {"x": 40, "y": 70, "z": -20}, "forearm.R": {"bend": -70}, "chest": {"z": -32, "x": -6}, "spine": {"z": -12},
              "head": {"z": 18}, "upper_arm.L": {"x": -30, "y": 10}, "thigh.L": {"x": -16}, "shin.L": {"bend": 18}},
             wings(40, 10, 6, 10, 6, 6), {"chain_sway": -20})
    cut = M({"upper_arm.R": {"x": -80, "y": -20, "z": 40}, "forearm.R": {"bend": -10}, "hand.R": {"x": -30}, "chest": {"z": 30, "x": 20},
             "spine": {"z": 10, "x": 6}, "head": {"z": -12, "x": -6}, "upper_arm.L": {"x": 20, "y": 30}, "forearm.L": {"bend": -40},
             "thigh.L": {"x": -34}, "shin.L": {"bend": 36}, "thigh.R": {"x": 14}, "root": (0, -.14, 0)},
            wings(-20, 20, 14, 40, 20, 10), {"chain_sway": 25})
    out["attack"] = keys_to_frames([(0, M()), (.32, wind), (.5, merge(wind, {"chest": {"z": 8}})), (.62, cut),
                                    (.8, merge(cut, {"chest": {"x": 4}})), (1, M())], 10)
    hitp = M({"chest": {"x": -16, "z": 10}, "spine": {"x": -8}, "head": {"x": -20, "z": 12}, "upper_arm.L": {"y": 20, "x": 20},
              "root": (0, .07, 0)}, wings(30, 12, 10, -6, -4, -4), {"chain_sway": -22})
    out["hit"] = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: cai de joelhos, as asas se abrem de uma vez e ele tomba de cara no chão, asas estendidas
    kneel = M({"thigh.L": {"x": -80}, "thigh.R": {"x": -40}, "shin.L": {"bend": 100}, "shin.R": {"bend": 96},
               "chest": {"x": -10}, "head": {"x": -26}, "upper_arm.L": {"y": 10, "x": 10}, "upper_arm.R": {"y": -10, "x": 10}},
              wings(60, 20, 14, -10, -6, -4))
    down = merge({"hips": {"x": 82}, "spine": {"x": 4}, "chest": {"x": 4}, "head": {"z": -50, "x": -8},
                  "upper_arm.L": {"x": -150, "y": 30}, "upper_arm.R": {"x": -40, "y": -50}, "forearm.L": {"bend": -20},
                  "forearm.R": {"bend": -10}, "thigh.L": {"x": 8}, "thigh.R": {"x": 2}, "shin.L": {"bend": 16},
                  "shin.R": {"bend": 6}, "ground": .06}, wings(-30, -10, -6, 60, 14, 6))
    out["death"] = keys_to_frames([(0, hitp), (.28, kneel), (.42, merge(kneel, {"head": {"x": 12}})),
                                   (.7, merge(lerp_pose(kneel, down, .5), {"ground": .06})), (.88, down),
                                   (1, merge(down, {"head": {"x": 4}}))], 10)
    # estátua: ajoelhado, cabeça baixa, falx fincada no chão à frente, asas fechadas por cima das costas
    stat = merge({"spine": {"x": 22}, "chest": {"x": 18}, "neck": {"x": 18}, "head": {"x": 22},
                  "thigh.L": {"x": -86, "y": -4}, "thigh.R": {"x": -20, "y": 4}, "shin.L": {"bend": 90}, "shin.R": {"bend": 120},
                  "foot.L": {"x": 10}, "foot.R": {"x": 40},
                  "upper_arm.L": {"x": -50, "y": 10}, "forearm.L": {"bend": -40}, "upper_arm.R": {"x": -60, "y": -16},
                  "forearm.R": {"bend": -30}, "hand.R": {"x": 40}},
                 wings(-40, -8, -14, 70, 30, 10))
    out["kneel"] = [stat, merge(stat, {"chest": {"x": -1}})]
    stand = M()
    shake = merge(stat, {"chest": {"x": -8}, "head": {"x": -20}})
    open_ = M({"chest": {"x": -16}, "head": {"x": -24}, "upper_arm.L": {"y": 30}, "upper_arm.R": {"y": -30}},
              wings(70, 26, 14, -10, -8, -6))
    out["rise"] = keys_to_frames([(0, stat), (.2, shake), (.35, stat), (.55, merge(lerp_pose(stat, open_, .5), {"chain_sway": 20})),
                                  (.78, open_), (1, stand)], 12)
    # pouso: desce do céu de asas abertas (root alto, sem trava no chão), freia batendo as asas e assenta
    land = []
    for i in range(10):
        u = i/9
        hgt = 2.6*(1 - u)**1.6
        flapw = wings(50 + 28*math.cos(u*3*math.pi), 18 + 8*math.cos(u*3*math.pi - .6), 10, 0, 6, 6)
        legs = {"thigh.L": {"x": -10*(1 - u)}, "thigh.R": {"x": 10*(1 - u)}, "shin.L": {"bend": 20*(1 - u)}, "shin.R": {"bend": 20*(1 - u)}}
        p = M(legs, flapw, {"chest": {"x": -10*(1 - u)}, "head": {"x": -10*(1 - u)}, "root": (0, 0, hgt)})
        p["ground"] = None if u < .99 else .03
        if u >= .99: p = M({"thigh.L": {"x": -20}, "shin.L": {"bend": 30}, "thigh.R": {"x": -10}, "shin.R": {"bend": 24}},
                           wings(20, 10, 6, 20, 10, 8))
        land.append(p)
    out["land"] = land
    return out
