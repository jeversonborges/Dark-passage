# Cervo de Lume (Novo Éden, Havilá, nível 12-14): o bicho que o Éden devolveu. Cervo magro de pelo cor de
# terra com manchas claras, barriga e peito pálidos, pescoço comprido; a galhada é de seiva viva (osso
# translúcido com nervuras acesas em âmbar) e as pontas pingam luz. Na cernelha a Enxertia prendeu uma
# cinta de latão com um sininho (os cervos de Havilá são marcados, ninguém os caça). Neutro: pasta,
# levanta a cabeça quando alguém chega e só ataca se apanhar (coice e galhada).
# Brilho: âmbar (galhada, olhos). Esqueleto quadrúpede de quad.py (patas compridas, trava no chão pelas patas).
import bpy, math, random
from mathutils import Vector
from mrig import *
from quad import *

INFO = {"px": 224, "target_z": .78, "rim": (1, .8, .45), "colors": 40, "samples": 44,
        "fps": {"idle": 6, "walk": 12, "attack": 12, "alert": 8, "hit": 12, "death": 10},
        "loops": ("idle", "walk")}

VARIANTS = {"cervo_de_lume": {}}
V = {}
def set_variant(name):
    V.clear(); V.update(VARIANTS[name]); V["name"] = name

BACK = 1.0
def bones():
    B = quad_bones(sh=.92, hip=.92, y_sh=-.34, y_hip=.34, w=.09, wh=.1, back=BACK, neck=(-.62, 1.42), head=(-.86, 1.38),
                   jaw=((-.7, 1.37), (-.87, 1.33)), tail=((.5, .98), (.58, .86)),
                   extra={"ear.L": ((.06, -.6, 1.46), (.15, -.56, 1.6), "head"), "ear.R": ((-.06, -.6, 1.46), (-.15, -.56, 1.6), "head"),
                          "antler.L": ((.05, -.58, 1.5), (.2, -.5, 1.95), "head"), "antler.R": ((-.05, -.58, 1.5), (-.2, -.5, 1.95), "head")})
    return B

def glow(name, rgb, strength):
    """Emissivo que só a câmera vê (sem vagalumes no render)."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes):
        if nd.type != 'OUTPUT_MATERIAL': nt.nodes.remove(nd)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*rgb, 1); em.inputs["Strength"].default_value = strength
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = (*rgb, 1)
    lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); nt.links.new(df.outputs[0], mx.inputs[1]); nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], [nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL'][0].inputs["Surface"])
    return m

def build():
    fur = stained("c_pelo", (.26, .18, .1), stain=(.1, .06, .03), amount=.3, scale=5, rough=.85,
                  blotch=(.34, .27, .17), blotch_amt=.7, grime=.5, dirt=.3)
    pale = stained("c_barriga", (.36, .31, .22), stain=(.14, .09, .05), amount=.25, scale=6, rough=.85, grime=.3)
    tuft = mat("c_tufo", (.1, .07, .04), 0, .9, dirt=.4)
    hoof = mat("c_casco", (.05, .04, .035), 0, .4)
    dark = mat("c_boca", (.02, .012, .01), 0, .5)
    nose = mat("c_nariz", (.04, .025, .02), 0, .25)
    antler = stained("c_galhada", (.42, .3, .14), stain=(.6, .32, .08), amount=.5, scale=9, rough=.5, grime=.2, dirt=.15)
    tip = glow("c_ponta", (1, .55, .15), 5)
    eye = glow("c_olho", (1, .62, .2), 12)
    brass = stained("c_latao", (.5, .35, .12), stain=(.08, .14, .09), amount=.4, scale=6, metal=.85, rough=.4, grime=.4)

    R = Rig("cervo", bones(), ground=.03, ground_bones=PAWS)
    P = R.P
    # ---- corpo: garupa alta, barriga recolhida, peito fundo, cernelha; loft com barriga pálida separada
    keys = [(.44, .9, .05, .05), (.4, .93, .1, .11), (.32, .95, .14, .17), (.2, .95, .145, .19), (.08, .94, .135, .19),
            (-.04, .93, .13, .2), (-.16, .93, .14, .22), (-.28, .95, .14, .23), (-.36, .99, .12, .2), (-.44, 1.06, .09, .14), (-.5, 1.12, .07, .1)]
    rings = ring_path(keys)
    def rad(i, a, r):
        y = r[0].y; f = 1.0
        side = abs(math.cos(a))
        if -.3 < y < .0: f *= 1 - .05*side*(.5 - .5*math.cos(y*2*math.pi/.06))**2     # costelas de leve
        if .2 < y < .36 and .3 < math.sin(a) < .9: f *= 1 + .08*max(0, 1 - abs(y - .3)/.07)  # ossos do quadril
        if math.sin(a) < -.4: f *= 1 - .04*(-math.sin(a))                                   # barriga recolhida
        return f
    body = loft("cervo_corpo", rings, fur, seg=32, rad=rad)
    belly = loft("cervo_barriga", [[r[0] + Vector((0, 0, -.02)), r[1]*.78, r[2]*.62, r[3]] for r in rings[8:-10]], pale, seg=20)
    parts = [body, belly]
    parts += tufts(rings, tuft, 50, (60, 120), (.55, 1), .07, .012, 21, back=.8, down=-.2)    # crina curta na cernelha e pescoço
    parts += tufts(rings, tuft, 16, (-120, -60), (.3, .55), .05, .01, 22, back=.2, down=1)
    for (ri, a, s) in ((.3, 40, .03), (.5, 150, .035), (.62, 25, .03), (.42, 100, .025), (.72, 160, .028), (.22, 130, .03)):
        p, nrm = surf(rings[int(ri*(len(rings)-1))], math.radians(a))             # manchas claras de corço
        w = prim("primitive_uv_sphere_add", pale, p + nrm*.004, (s, s*1.4, s*.3), segments=10, ring_count=6)
        w.rotation_euler = nrm.to_track_quat('Z', 'Y').to_euler(); parts.append(w)
    n0, n1 = P("neck"), P("neck", 1)
    parts.append(limb("pescoco", [(*(n0 + Vector((0, .06, -.1))), .11), (*(n0 + Vector((0, .0, -.02))), .09), (*n0.lerp(n1, .35), .075),
                                  (*n0.lerp(n1, .7), .066), (*(n1 + Vector((0, .0, .0))), .062)], fur))
    parts.append(limb("garganta", [(*(n0 + Vector((0, .0, -.06))), .06), (*(n0.lerp(n1, .5) + Vector((0, 0, -.04))), .05), (*(n1 + Vector((0, 0, -.03))), .04)], pale))
    body = join(parts)
    R.bind(body, ["hips", "spine", "chest", "neck", "head", "thigh.L", "thigh.R", "upper_arm.L", "upper_arm.R"], power=4)
    # cinta de latão com sininho na cernelha (marca da Enxertia)
    a_, b_ = P("chest"), P("chest", 1); c = a_.lerp(b_, .35)
    cl = [prim("primitive_torus_add", brass, c + Vector((0, 0, -.08)), (1, 1, 1.4), major_radius=.19, minor_radius=.012, major_segments=20, minor_segments=5, rot=(0, 90, 0))]
    cl.append(prim("primitive_uv_sphere_add", brass, c + Vector((0, 0, -.31)), (.03, .03, .035), segments=10, ring_count=6))
    R.rigid(cl, "chest")

    # ---- patas compridas e finas, cascos fendidos
    for s, n in ((1, "L"), (-1, "R")):
        sh, el, wr, tp = P(f"upper_arm.{n}"), P(f"forearm.{n}"), P(f"hand.{n}"), P(f"hand.{n}", 1)
        fl = limb(f"pata_f{n}", [(*(sh + Vector((0, .02, .04))), .07), (*sh.lerp(el, .5), .05), (*el, .035), (*el.lerp(wr, .5), .025),
                                 (*wr, .022), (*wr.lerp(tp, .6), .024), (*(tp + Vector((0, .0, .01))), .02)], fur)
        R.bind(fl, ["chest", f"upper_arm.{n}", f"forearm.{n}", f"hand.{n}"])
        hp, kn, hk, ft = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}"), P(f"foot.{n}", 1)
        hl = limb(f"pata_t{n}", [(*(hp + Vector((0, -.02, .04))), .1), (*hp.lerp(kn, .45) + Vector((0, .03, 0)), .075), (*kn, .04),
                                 (*kn.lerp(hk, .5), .028), (*hk, .024), (*hk.lerp(ft, .6), .022), (*(ft + Vector((0, .0, .01))), .02)], fur)
        R.bind(hl, ["hips", f"thigh.{n}", f"shin.{n}", f"foot.{n}"])
        for b, t in ((f"hand.{n}", tp), (f"foot.{n}", ft)):
            cs = []
            for k in (-1, 1):
                cs.append(prim("primitive_cube_add", hoof, t + Vector((.014*k, -.01, .02)), (.013, .03, .022)))
            R.rigid(cs, b)
    # ---- cauda curta de pelo claro
    t1, t2, t3 = P("tail1"), P("tail2"), P("tail2", 1)
    tl = limb("cauda", [(*t1, .035), (*t2, .03), (*t3, .015)], pale)
    R.bind(tl, ["hips", "tail1", "tail2"])
    # ---- cabeça: crânio estreito, focinho fino, olhos grandes acesos, orelhas
    hd = [prim("primitive_uv_sphere_add", fur, (0, -.64, 1.43), (.07, .09, .075), segments=16, ring_count=10)]
    sn = along("primitive_cone_add", fur, Vector((0, -.68, 1.42)), Vector((0, -.87, 1.36)), .05, vertices=14, radius1=1, radius2=.55)
    sn.scale = (sn.scale.x*.8, sn.scale.y, sn.scale.z); hd.append(sn)
    hd.append(prim("primitive_uv_sphere_add", nose, (0, -.875, 1.365), (.024, .016, .018), segments=10, ring_count=6))
    hd.append(prim("primitive_uv_sphere_add", pale, (0, -.84, 1.33), (.03, .05, .02), segments=10, ring_count=6))   # queixo claro
    for s in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", dark, (.048*s, -.69, 1.455), (.02, .017, .017), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", eye, (.054*s, -.7, 1.457), (.015, .011, .012), segments=8, ring_count=6))
        hd.append(prim("primitive_uv_sphere_add", pale, (.03*s, -.7, 1.43), (.02, .02, .015), segments=8, ring_count=5))
    R.rigid(hd, "head")
    jw = [along("primitive_cone_add", fur, Vector((0, -.68, 1.385)), Vector((0, -.85, 1.335)), .034, vertices=12, radius1=1, radius2=.5)]
    jw[0].scale = (jw[0].scale.x*.8, jw[0].scale.y*.5, jw[0].scale.z); R.rigid(jw, "jaw")
    for s, n in ((1, "L"), (-1, "R")):
        a_, b_ = P(f"ear.{n}"), P(f"ear.{n}", 1)
        e = along("primitive_cone_add", fur, a_, b_, .03, vertices=6, radius1=1, radius2=0); e.scale = (e.scale.x, e.scale.y*.4, e.scale.z)
        e2 = along("primitive_cone_add", pale, a_ + (b_ - a_)*.15, b_ - (b_ - a_)*.1, .018, vertices=5, radius1=1, radius2=0); e2.scale = (e2.scale.x, e2.scale.y*.3, e2.scale.z)
        R.rigid([e, e2], f"ear.{n}")
        # galhada de seiva: haste principal + 3 pontas, pontas acesas
        a_, b_ = P(f"antler.{n}"), P(f"antler.{n}", 1); rr = random.Random(3 + s)
        pts = [a_, a_.lerp(b_, .35) + Vector((.04*s, -.02, 0)), a_.lerp(b_, .7) + Vector((.03*s, .02, 0)), b_]
        ant = [along("primitive_cone_add", antler, pts[i], pts[i + 1], .03 - .006*i, vertices=7, radius1=1, radius2=.8) for i in range(3)]
        for (i, d) in ((1, Vector((.16*s, -.12, .16))), (2, Vector((.14*s, .06, .2))), (3, Vector((.05*s, -.04, .2)))):
            q = pts[i]; tipo = q + d
            ant.append(along("primitive_cone_add", antler, q, tipo, .018, vertices=6, radius1=1, radius2=.35))
            ant.append(prim("primitive_uv_sphere_add", tip, tipo, (.011, .011, .016), segments=8, ring_count=6))
        ant.append(prim("primitive_uv_sphere_add", tip, b_, (.012, .012, .018), segments=8, ring_count=6))
        R.rigid(ant, f"antler.{n}")
    R.arm.scale = [V.get("scale", 1)]*3
    return R, INFO

# ======================================================================= animações
BASE = {"neck": {"x": -8}, "head": {"x": 10}, "tail1": {"x": -10}, "ear.L": {"z": 10}, "ear.R": {"z": -10}}
def M(*p): return merge(BASE, *p)

def anims(R):
    # idle: pasta (cabeça baixa), mastiga, levanta e olha, orelha mexe
    graze = M({"neck": {"x": 64}, "head": {"x": 34}, "jaw": {"x": 4}})
    idle = []
    for i in range(8):
        t = i/8*2*math.pi; s = math.sin(t)
        base = graze if i < 5 else M({"neck": {"x": -14}, "head": {"x": 6, "z": 12*math.sin(t)}})
        idle.append(merge(base, {"spine": {"x": 1.2*s}, "jaw": {"x": 3 + 3*max(0, math.sin(t*3))}, "tail1": {"z": 12*s},
                                 "ear.L": {"z": 10 + 14*max(0, s)}, "ear.R": {"z": -10 - 10*max(0, -s)}}))
    # trote leve
    walk = []
    for i in range(8):
        p = i/8; s2 = math.sin(p*4*math.pi); s1 = math.sin(p*2*math.pi)
        legs = merge(leg_cycle("L", True, p, 28, 1.0, 1.0), leg_cycle("R", False, p, 26, 1.0, 1.0),
                     leg_cycle("R", True, (p + .5) % 1, 28, 1.0, 1.0), leg_cycle("L", False, (p + .5) % 1, 26, 1.0, 1.0))
        walk.append(M(legs, {"chest": {"z": 3*s1, "x": 2*s2}, "hips": {"z": -2*s1, "y": 1.5*s1}, "neck": {"x": -4 - 3*s2},
                             "head": {"x": 8 + 3*s2, "z": -3*s1}, "tail1": {"z": 10*s1}}))
    # alerta: levanta a cabeça de repente, orelhas para a frente, bate a pata
    up = M({"neck": {"x": -26}, "head": {"x": -4}, "ear.L": {"z": 25, "x": -20}, "ear.R": {"z": -25, "x": -20}, "tail1": {"x": 20}})
    stamp = merge(up, {"upper_arm.L": {"x": -30}, "forearm.L": {"bend": -40}, "hand.L": {"bend": 60}})
    alert = keys_to_frames([(0, graze), (.2, up), (.45, stamp), (.6, up), (.8, merge(up, {"head": {"z": 18}})), (1, M())], 8)
    # ataque: recua, empina e vem com a galhada / coice da frente
    rear = M({"hips": {"x": -18}, "spine": {"x": -8}, "chest": {"x": -10}, "neck": {"x": -30}, "head": {"x": 10},
              "upper_arm.L": {"x": -60}, "upper_arm.R": {"x": -50}, "forearm.L": {"bend": -70}, "forearm.R": {"bend": -60},
              "hand.L": {"bend": 60}, "hand.R": {"bend": 50},
              "thigh.L": {"x": -30}, "thigh.R": {"x": -30}, "shin.L": {"bend": 40}, "shin.R": {"bend": 40}, "foot.L": {"bend": -30}, "foot.R": {"bend": -30},
              "tail1": {"x": 15}, "gb": ["foot.L", "foot.R"], "ground": .03})
    strike = M({"hips": {"x": 10}, "chest": {"x": 12}, "neck": {"x": 50}, "head": {"x": 40},
                "upper_arm.L": {"x": -20}, "upper_arm.R": {"x": -20}, "forearm.L": {"bend": -20}, "forearm.R": {"bend": -20},
                "thigh.L": {"x": 20}, "thigh.R": {"x": 20}, "tail1": {"x": -10}, "root": (0, -.2, 0)})
    toss = merge(strike, {"head": {"z": 25, "x": 20}, "neck": {"z": -10, "x": 30}})
    attack = keys_to_frames([(0, M()), (.2, rear), (.36, rear), (.5, strike), (.64, toss), (.8, merge(strike, {"neck": {"x": 20}})), (1, M())], 9)
    # golpe recebido
    hitp = M({"hips": {"z": 6}, "chest": {"z": -8, "x": -6}, "neck": {"x": -30, "z": 10}, "head": {"x": -10}, "jaw": {"x": 20},
              "ear.L": {"x": 30}, "ear.R": {"x": 30}, "tail1": {"x": 20}, "root": (0, .08, 0)})
    hit = [hitp, lerp_pose(hitp, M(), .5), M()]
    # morte: as patas cedem, tomba de lado, a galhada apaga por último (fica acesa: o jogo esmaece)
    buckle = M({"hips": {"x": -6, "y": 8}, "neck": {"x": 30}, "head": {"x": 20},
                "upper_arm.L": {"x": 30}, "upper_arm.R": {"x": 24}, "forearm.L": {"bend": -80}, "forearm.R": {"bend": -70},
                "hand.L": {"bend": 60}, "hand.R": {"bend": 50},
                "thigh.L": {"x": -40}, "thigh.R": {"x": -32}, "shin.L": {"bend": 60}, "shin.R": {"bend": 50}, "foot.L": {"bend": -40}, "foot.R": {"bend": -30}})
    tilt = merge(buckle, {"hips": {"y": 45}, "gb": BODY + PAWS, "ground": .04})
    side = {"hips": {"y": 88}, "neck": {"x": 20, "y": 6}, "head": {"x": -10, "y": 6}, "jaw": {"x": 15},
            "upper_arm.L": {"x": -20, "y": 4}, "upper_arm.R": {"x": -30, "y": -14}, "forearm.L": {"bend": -20}, "forearm.R": {"bend": -8},
            "thigh.L": {"x": 10, "y": 4}, "thigh.R": {"x": 22, "y": -12}, "shin.L": {"bend": 24}, "shin.R": {"bend": 8},
            "tail1": {"x": -20, "z": 10}, "ear.L": {"x": 40}, "ear.R": {"x": 40}, "gb": BODY, "ground": .12}
    death = keys_to_frames([(0, hitp), (.25, buckle), (.48, tilt), (.7, side), (.86, merge(side, {"thigh.R": {"x": 10}})), (1, merge(side, {"jaw": {"x": 6}}))], 10)
    return {"idle": idle, "walk": walk, "attack": attack, "alert": alert, "hit": hit, "death": death}
