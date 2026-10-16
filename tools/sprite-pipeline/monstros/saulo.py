# Saulo, o Penitente (NPC da loja de PvP do Agrak): ex-carrasco da Legião Blasfema, demônio convertido à luz.
# Alto (2,4 m) e pesado, mas sereno, à maneira de um Buda/velho mestre: careca, pele branca de giz com as runas
# demoníacas cicatrizadas em relevo, orelhas compridas, sobrancelhas e bigode brancos e longos caindo até o peito,
# olhos fechados. Restos do demônio: chifres serrados com tampas de ouro velho, cauda enrolada na cintura como cinto,
# tocos de asa queimados nas costas, unhas pretas, cascos. Túnica de pano de saco com um ombro de fora, manto
# rasgado, rosário grande de pedaços de chifre e elos da corrente de carrasco. Brilho: só dourado (halo fino e
# quebrado atrás da cabeça, osso "halo", e as runas acendendo de leve).
# Animações (NPC): idle (respira, contas passando nos dedos), abencoar (abre os braços, o halo cresce),
# rezar (mãos juntas), rir (ri com a barriga).
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
from mrig import *

INFO = {"px": 384, "target_z": 1.1, "rim": (1, .82, .45), "colors": 48, "samples": 40,
        "fps": {"idle": 6, "abencoar": 9, "rezar": 8, "rir": 10},
        "loops": ("idle", "rezar", "rir")}
SCALE = 1.33
V = {"name": "saulo"}
def set_variant(name): V["name"] = name

def bones():
    return humanoid(1.0, 1.25, extra={"halo": ((0, .14, 1.78), (0, .16, 1.9), "head")})

def build():
    skin = stained("p_pele_giz", (.72, .7, .64), stain=(.2, .18, .14), amount=.25, scale=4, rough=.6,
                   blotch=(.6, .58, .52), blotch_amt=.5, grime=.6, dirt=.75)
    scarm = stained("p_cicatriz", (.62, .58, .5), stain=(.15, .12, .08), amount=.3, scale=6, rough=.5)
    rune = mat("p_runa", (.6, .45, .2), 0, .4, emit=(1, .72, .3), strength=1.6)
    hair = stained("p_pelo_branco", (.82, .8, .76), stain=(.2, .18, .15), amount=.2, scale=6, rough=.7, dirt=.85)
    sack = stained("p_saco", (.3, .24, .16), stain=(.12, .08, .04), amount=.55, scale=3, rough=1, grime=1.0,
                   blotch=(.2, .16, .1), blotch_amt=.5)
    mantle = stained("p_manto", (.17, .14, .11), stain=(.06, .04, .02), amount=.5, scale=3, rough=.95, grime=1.0)
    rope = mat("p_corda", (.24, .18, .1), 0, .9, dirt=.6)
    horn = stained("p_chifre", (.12, .09, .08), stain=(.04, .03, .02), amount=.5, scale=7, rough=.45)
    oldgold = stained("p_ouro_velho", (.5, .36, .14), stain=(.1, .08, .04), amount=.45, scale=6, metal=.85, rough=.4, grime=.4)
    iron = stained("p_ferro", (.08, .07, .065), stain=(.17, .07, .03), amount=.5, scale=5, metal=.8, rough=.5)
    nail = mat("p_unha", (.02, .015, .015), 0, .3)
    hoof = mat("p_casco", (.04, .035, .03), 0, .4)
    burnt = stained("p_queimado", (.05, .04, .035), stain=(.15, .05, .02), amount=.5, scale=6, rough=.8)
    dark = mat("p_escuro", (.05, .04, .035), 0, .6)
    halo = mat("p_halo", (.8, .55, .2), metal=.6, rough=.3, emit=(1, .62, .18), strength=3.5)

    R = Rig("saulo", bones()); P = R.P
    rr = random.Random(12)
    # ---------------------------------------------- pernas (quase cobertas pela túnica), cascos
    j = {"pelvis": (0, 0, .95, .22, .17)}; e = []
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .13); j[f"knee{n}"] = (*k, .085); j[f"ank{n}"] = (*a, .06)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"knee{n}"), (f"knee{n}", f"ank{n}")]
    R.bind(skin_mesh("pernas", j, e, skin), ["hips", "thigh.L", "thigh.R", "shin.L", "shin.R"])
    for s, n in ((1, "L"), (-1, "R")):
        a, t = P(f"foot.{n}"), P(f"foot.{n}", 1)
        d = t - a; d.z = 0; d.normalize(); hv = []
        for sx in (-1, 1):
            c = a + Vector((.035*sx, 0, -.045)) + d*.05
            hv.append(along("primitive_cone_add", hoof, c + Vector((0, .04, .05)), c + d*.09 + Vector((0, 0, -.02)), .048, vertices=8, radius1=1, radius2=.5))
        R.rigid(hv, f"foot.{n}")
    # ---------------------------------------------- tronco largo e barriga de mestre, braços fortes
    t = {"pelvis": (0, 0, .98, .23, .19), "belly": (0, -.06, 1.14, .29, .26), "chest": (0, -.01, 1.34, .29, .2),
         "neck": (0, -.01, 1.52, .1), "neck2": (0, -.02, 1.6, .09)}
    te = [("pelvis", "belly"), ("belly", "chest"), ("chest", "neck"), ("neck", "neck2")]
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}")
        t[f"sh{n}"] = (*(sh + Vector((-.02*s, 0, .01))), .12); t[f"bi{n}"] = (*sh.lerp(el, .45), .095)
        t[f"el{n}"] = (*el, .07); t[f"fa{n}"] = (*el.lerp(wr, .4), .075); t[f"wr{n}"] = (*wr, .055)
        te += [("chest", f"sh{n}"), (f"sh{n}", f"bi{n}"), (f"bi{n}", f"el{n}"), (f"el{n}", f"fa{n}"), (f"fa{n}", f"wr{n}")]
    torso = skin_mesh("tronco", t, te, skin)
    R.bind(torso, ["hips", "spine", "chest", "neck", "upper_arm.L", "upper_arm.R", "forearm.L", "forearm.R"])
    # runas cicatrizadas: no ombro e no braço direitos (o ombro de fora), acesas de leve
    rn = []
    for k in range(9):
        a = P("upper_arm.R").lerp(P("forearm.R"), .1 + .09*k) + Vector((0, -.09, .03 - .005*k))
        w_ = .03 if k % 3 else .045
        rn.append(prim("primitive_cube_add", scarm, a, (w_, .006, .008), rot=(0, 30*(k % 2) - 15, 0)))
        if k % 2 == 0:
            rn.append(prim("primitive_cube_add", rune, a + Vector((0, -.004, 0)), (w_*.7, .004, .004), rot=(0, 30*(k % 2) - 15, 0)))
    na = len(rn)
    for k in range(6):  # runas no peito direito, aparecendo pela abertura da túnica
        q = Vector((-.12 + .03*math.sin(k), -.25, 1.4 - .05*k))
        rn.append(prim("primitive_cube_add", scarm, q, (.03, .006, .007), rot=(0, 25*(-1)**k, 0)))
        rn.append(prim("primitive_cube_add", rune, q + Vector((0, -.004, 0)), (.022, .004, .004), rot=(0, 25*(-1)**k, 0)))
    R.rigid(rn[:na], "upper_arm.R"); R.rigid(rn[na:], "chest")
    # ---------------------------------------------- túnica de saco (ombro direito de fora), corda, manto rasgado
    tu = skirt("tunica", sack, [(1.46, .2, .14, .02), (1.32, .32, .22, .0), (1.12, .33, .3, -.04), (.95, .3, .27, -.02),
                               (.6, .3, .25, 0), (.3, .31, .26, .02), (.12, .32, .27, .02)], open_front=0, jag=.05, seed=3, thick=.014)
    R.bind(tu, ["hips", "spine", "chest", "thigh.L", "thigh.R", "shin.L", "shin.R"], power=3)
    ch = []
    # alça da túnica só no ombro esquerdo; recorte do lado direito mostrado pela pele por cima
    ch.append(along("primitive_cube_add", sack, Vector((.1, -.2, 1.42)), Vector((.18, .0, 1.5)), .09))
    ch.append(along("primitive_cube_add", sack, Vector((.18, .0, 1.5)), Vector((.12, .2, 1.4)), .09))
    ch.append(prim("primitive_uv_sphere_add", skin, (-.2, -.02, 1.42), (.16, .16, .1), segments=14, ring_count=8))  # ombro de fora
    # manto rasgado caindo pelas costas
    mt = skirt("manto", mantle, [(1.5, .22, .14, .08), (1.3, .36, .2, .12), (.9, .4, .22, .16), (.45, .42, .24, .2), (.2, .44, .26, .22)],
               open_front=1.6, jag=.12, seed=9, thick=.012)
    R.bind(mt, ["hips", "spine", "chest", "thigh.L", "thigh.R"], power=3)
    # cauda de demônio enrolada na cintura servindo de cinto, a ponta pendurada; mais um nó de corda
    for k in range(26):
        a = 2*math.pi*k/24
        q = Vector((math.cos(a)*.33, -.04 + math.sin(a)*.3, .96 + .006*k))
        q2 = Vector((math.cos(a + .26)*.33, -.04 + math.sin(a + .26)*.3, .96 + .006*(k + 1)))
        ch.append(along("primitive_cylinder_add", skin, q, q2, .03, vertices=8))
    tip = Vector((.3, -.18, .95))
    ch.append(along("primitive_cylinder_add", skin, tip, tip + Vector((.02, -.03, -.16)), .022, vertices=8))
    sp = prim("primitive_cone_add", skin, tip + Vector((.025, -.035, -.2)), (.04, .012, .05), vertices=4, radius1=1, radius2=0, rot=(0, 0, 0))
    sp.rotation_euler = (math.radians(180), 0, 0); ch.append(sp)
    ch.append(prim("primitive_torus_add", rope, (0, -.04, 1.04), (1.06, .98, 1), major_radius=.32, minor_radius=.014, major_segments=24, minor_segments=4))
    for s in (1, -1):
        ch.append(along("primitive_cylinder_add", rope, Vector((-.05*s, -.33, 1.03)), Vector((-.07*s, -.35, .78)), .01, vertices=4))
    # rosário grande: contas de chifre e elos da corrente de carrasco, pendurado no pescoço até a barriga
    for k in range(30):
        a = 2*math.pi*k/30
        q = Vector((math.sin(a)*.19, -.05 - .2*max(0, math.cos(a))**.7 - .05, 1.5 - .3*max(0, math.cos(a))**1.5))
        if math.cos(a) < -.2: q = Vector((math.sin(a)*.17, .1, 1.52))
        if k % 3 == 0:
            ch.append(prim("primitive_torus_add", iron, q, (1, 1, 1.4), major_radius=.022, minor_radius=.006, major_segments=8, minor_segments=4, rot=(0, 90, 0)))
        else:
            ch.append(prim("primitive_uv_sphere_add", horn, q, (.022, .022, .025), segments=8, ring_count=5))
    ch.append(along("primitive_cone_add", horn, Vector((0, -.32, 1.18)), Vector((0, -.33, 1.06)), .03, vertices=6, radius1=1, radius2=0))  # pingente: ponta de chifre
    # tocos de asa queimados nas costas
    for s in (1, -1):
        b0 = Vector((.1*s, .17, 1.4)); b1 = b0 + Vector((.12*s, .12, .14))
        ch.append(along("primitive_cone_add", burnt, b0, b1, .06, vertices=8, radius1=1, radius2=.55))
        for k in range(3):
            q = b1 + Vector((rr.uniform(-.02, .02)*s, rr.uniform(0, .03), rr.uniform(-.03, .02)))
            ch.append(along("primitive_cone_add", burnt, b1, q + Vector((.04*s, .05, .05 - .04*k)), .02, vertices=5, radius1=1, radius2=0))
    R.rigid(ch, "chest")

    # ---------------------------------------------- cabeça: careca, orelhas de Buda, olhos fechados, sobrancelhas e bigode longos
    hb = P("head"); c = hb + Vector((0, -.02, .11))
    hd = [prim("primitive_uv_sphere_add", skin, c, (.115, .125, .135), segments=22, ring_count=12)]
    hd.append(prim("primitive_uv_sphere_add", skin, c + Vector((0, -.03, -.08)), (.1, .1, .07), segments=16, ring_count=8))  # queixo e bochechas
    hd.append(prim("primitive_uv_sphere_add", skin, c + Vector((0, -.125, -.01)), (.025, .03, .035), segments=10, ring_count=6))  # nariz
    for s in (1, -1):
        # olhos fechados: fenda curva
        hd.append(along("primitive_cylinder_add", dark, c + Vector((.025*s, -.112, .025)), c + Vector((.065*s, -.1, .022)), .004, vertices=4))
        # orelha comprida de Buda, lóbulo até o queixo
        ear = prim("primitive_uv_sphere_add", skin, c + Vector((.12*s, .0, -.04)), (.025, .04, .1), segments=10, ring_count=8)
        hd.append(ear)
        hd.append(prim("primitive_uv_sphere_add", skin, c + Vector((.125*s, -.005, -.13)), (.022, .03, .035), segments=8, ring_count=5))
        # sobrancelhas longas caindo para os lados
        for k in range(6):
            b0 = c + Vector((.02*s + .01*k*s, -.11, .05))
            hd.append(along("primitive_cone_add", hair, b0, b0 + Vector((.07*s + .01*k*s, .03, -.1 - .02*k)), .012, vertices=5, radius1=1, radius2=0))
        # bigode branco até o peito
        for k in range(7):
            m0 = c + Vector((.015*s + .004*k*s, -.13, -.045))
            hd.append(along("primitive_cone_add", hair, m0, m0 + Vector((.06*s + .012*k*s, -.03, -.36 + .02*k)), .016, vertices=5, radius1=1, radius2=0))
        # chifres serrados com tampa de ouro velho
        h0 = c + Vector((.07*s, -.02, .1)); h1 = h0 + Vector((.05*s, .02, .07))
        hd.append(along("primitive_cone_add", horn, h0, h1, .04, vertices=10, radius1=1, radius2=.8))
        hd.append(along("primitive_cylinder_add", oldgold, h1, h1 + (h1 - h0).normalized()*.02, .034, vertices=10))
        for k in range(3):
            hd.append(prim("primitive_torus_add", horn, h0.lerp(h1, .3 + .25*k), (1, 1, 1), major_radius=.036 - .003*k, minor_radius=.004,
                           major_segments=10, minor_segments=3))
    # runas cicatrizadas na testa
    hd.append(prim("primitive_cube_add", scarm, c + Vector((0, -.12, .08)), (.008, .006, .03)))
    hd.append(prim("primitive_cube_add", rune, c + Vector((0, -.125, .08)), (.004, .004, .022)))
    hd.append(prim("primitive_cube_add", scarm, c + Vector((0, -.12, .09)), (.03, .006, .006)))
    for o in hd:
        o.location = hb + (o.location - hb)*1.12; o.scale = o.scale*1.12
    R.rigid(hd, "head")
    # halo fino e quebrado atrás da cabeça (osso próprio)
    hc = P("halo") + Vector((0, 0, .04)); hl = []
    for k in range(28):
        if 17 <= k <= 20: continue  # quebrado
        a0, a1 = 2*math.pi*k/30, 2*math.pi*(k + 1)/30
        hl.append(along("primitive_cylinder_add", halo, hc + Vector((math.cos(a0)*.2, 0, math.sin(a0)*.2)),
                        hc + Vector((math.cos(a1)*.2, 0, math.sin(a1)*.2)), .006, vertices=6))
    R.rigid(hl, "halo")
    # ---------------------------------------------- mãos grandes, unhas pretas, contas na esquerda
    for s, n in ((1, "L"), (-1, "R")):
        o, ax, u, sd = R.frame(f"hand.{n}")
        g = [prim("primitive_uv_sphere_add", skin, o + ax*.06, (.07, .08, .075), segments=12, ring_count=8)]
        for k in range(4):
            q = o + ax*.11 + sd*(-.04 + .027*k)
            g.append(along("primitive_cylinder_add", skin, q, q + ax*.06, .017, vertices=8))
            g.append(along("primitive_cone_add", nail, q + ax*.06, q + ax*.085, .014, vertices=6, radius1=1, radius2=.2))
        if n == "L":
            for k in range(8):
                g.append(prim("primitive_uv_sphere_add", horn, o + ax*.1 - u*.06 + sd*(-.05 + .015*k) - ax*.01*abs(k - 3.5),
                              (.015, .015, .016), segments=6, ring_count=4))
        R.rigid(g, f"hand.{n}")
    R.arm.scale = [SCALE]*3
    return R, INFO

# ======================================================================= animações
BASE = {"spine": {"x": -3}, "neck": {"x": 4}, "head": {"x": 4},
        "upper_arm.L": {"y": 40, "x": -24}, "upper_arm.R": {"y": -40, "x": -10},
        "forearm.L": {"bend": -60}, "forearm.R": {"bend": -20}, "scale": {"halo": 1}}
def M(*p): return merge(BASE, *p)

def anims(R):
    idle = []
    for i in range(6):
        t = i/6*2*math.pi; s, c = math.sin(t), math.cos(t)
        idle.append(M({"spine": {"x": 1.5*s}, "chest": {"x": -1*s}, "head": {"x": 1.5*c},
                       "hand.L": {"bend": 10*s}, "forearm.L": {"bend": -3*c}, "root": (0, 0, .005*s)}))
    # abençoar: abre os braços para a frente e para cima, cabeça ergue, o halo cresce
    open_ = M({"chest": {"x": -6}, "head": {"x": -10}, "upper_arm.L": {"x": -70, "y": -20}, "upper_arm.R": {"x": -70, "y": 20},
               "forearm.L": {"bend": 30}, "forearm.R": {"bend": -10}, "scale": {"halo": 1.5}})
    abencoar = keys_to_frames([(0, M()), (.3, open_), (.7, merge(open_, {"head": {"x": 4}, "chest": {"x": 3}})), (1, M())], 10)
    for i, k in enumerate((1, 1.15, 1.35, 1.5, 1.6, 1.6, 1.5, 1.35, 1.15, 1)):
        abencoar[i]["scale"] = {"halo": k}
    # rezar: mãos juntas diante do peito, cabeça baixa
    pray = M({"head": {"x": 14}, "neck": {"x": 6}, "upper_arm.L": {"x": -30, "y": -22}, "upper_arm.R": {"x": -30, "y": 22},
              "forearm.L": {"bend": -100}, "forearm.R": {"bend": -100}})
    rezar = [merge(pray, {"spine": {"x": 1.5*math.sin(i/6*2*math.pi)}, "head": {"x": 2*math.sin(i/6*2*math.pi)}}) for i in range(6)]
    # rir: barriga sacode, cabeça para trás, mão na pança
    rir = []
    for i in range(8):
        s = math.sin(i/8*4*math.pi)
        rir.append(M({"spine": {"x": -8 + 4*s}, "chest": {"x": -5 + 3*s}, "head": {"x": -18 + 6*s},
                      "upper_arm.R": {"x": -20, "y": 16}, "forearm.R": {"bend": -80}, "root": (0, 0, .015*abs(s))}))
    return {"idle": idle, "abencoar": abencoar, "rezar": rezar, "rir": rir}
