# Querubim Desfeito (cripta, andar 3): anjo-criança de igreja, metade estátua quebrada e metade boneco de
# porcelana. Sem rosto: uma placa lisa de porcelana com uma rachadura que deixa vazar luz. Braço direito
# arrancado (engrenagens de latão e eixo expostos), túnica de coroinha vermelha suja com sobrepeliz rasgada,
# auréola de latão torta presa por uma haste na nuca, asa esquerda de penas sujas e asa direita de chapa
# remendada (placas rebitadas, varetas e um remendo de couro).
# Brilho: luz branco-dourada fria na rachadura do rosto e na auréola (e nos raios do clarão / faísca do raio).
# Voa sempre ("ground": None), pairando a ~0,6 m; só a morte trava no chão (cai e se parte).
# Ossos extras: asas (wing1..3, mesmo arranjo do corvo), "burst" (raios do clarão, na cabeça), "spark"
# (faísca na ponta dos dedos) e "floor" (sem pai, fixo no chão: cacos, cabeça partida e auréola caída que
# só aparecem no fim da morte). Peças escondidas usam a chave de pose "scale" (0.001).
import bpy, bmesh, math, random
from mathutils import Vector, Quaternion
from mrig import *
from corvo_de_cinza import feathers, safe_ground, wings

INFO = {"px": 288, "target_z": 1.25, "rim": (.85, .82, .62), "colors": 44, "samples": 40,
        "loops": ("idle", "walk", "retreat"),
        "fps": {"idle": 8, "walk": 12, "attack": 12, "flash": 12, "retreat": 12, "hit": 12, "death": 10}}
SCALE = 1.22   # criança (~1,35 m) exagerada para ler ao lado do personagem
HOVER = .5     # altura do voo (unidades do modelo)

B = humanoid(.72)
B["neck"] = ((0, 0, 1.066), (0, -.005, 1.11), "chest")
B["head"] = ((0, -.005, 1.11), (0, -.005, 1.33), "neck")
for s, n in ((1, "L"), (-1, "R")):
    B[f"wing1.{n}"] = ((.06*s, .085, 1.0), (.24*s, .1, 1.1), "chest")
    B[f"wing2.{n}"] = ((.24*s, .1, 1.1), (.44*s, .12, 1.17), f"wing1.{n}")
    B[f"wing3.{n}"] = ((.44*s, .12, 1.17), (.64*s, .13, 1.19), f"wing2.{n}")
B["burst"] = ((0, -.135, 1.21), (0, -.25, 1.21), "head")
B["spark"] = ((.47, -.02, .69), (.5, -.03, .64), "hand.L")
B["floor"] = ((0, 0, 0), (0, 0, .1), None)
HIDE = ("burst", "spark", "floor")

def glow(name, rgb, strength):
    """Emissivo que só a câmera vê (não ilumina o resto nem gera vagalumes de ruído no render)."""
    if name in bpy.data.materials: return bpy.data.materials[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for nd in list(nt.nodes):
        if nd.type != 'OUTPUT_MATERIAL': nt.nodes.remove(nd)
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = (*rgb, 1)
    em.inputs["Strength"].default_value = strength
    df = nt.nodes.new("ShaderNodeBsdfDiffuse"); df.inputs["Color"].default_value = (*rgb, 1)
    lp = nt.nodes.new("ShaderNodeLightPath"); mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0]); nt.links.new(df.outputs[0], mx.inputs[1])
    nt.links.new(em.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], [nd for nd in nt.nodes if nd.type == 'OUTPUT_MATERIAL'][0].inputs["Surface"])
    return m

def gear(m, c, axis, r, th, teeth=10, hub=None):
    """Engrenagem: disco + dentes + cubo, centrada em c, eixo axis."""
    q = Vector(axis).normalized().to_track_quat('Z', 'Y')
    parts = [prim("primitive_cylinder_add", m, c, (r*.82, r*.82, th/2), vertices=16)]
    parts[0].rotation_euler = q.to_euler()
    for k in range(teeth):
        a = 2*math.pi*k/teeth; v = q @ Vector((math.cos(a), math.sin(a), 0))
        t = prim("primitive_cube_add", m, c + v*r*.9, (r*.12, r*.12, th/2*.9))
        t.rotation_euler = (q @ Quaternion((0, 0, 1), a)).to_euler(); parts.append(t)
    parts.append(prim("primitive_cylinder_add", hub or m, c, (r*.3, r*.3, th*.8), vertices=10))
    parts[-1].rotation_euler = q.to_euler()
    return parts

def plate(m, base, d, L, W, th=.008):
    """Pena de chapa: placa fina, comprida em d, larga no plano XZ (normal ~Y)."""
    d = Vector(d).normalized(); o = along("primitive_cube_add", m, base, Vector(base) + d*L, .01)
    o.scale = (W/2, th/2, L/2); return o

def build():
    rnd = random.Random(5)
    porc = stained("q_porcelana", (.5, .48, .43), stain=(.06, .05, .045), amount=.2, scale=14, rough=.35,
                   blotch=(.27, .25, .21), blotch_amt=.4, grime=.9)
    pedra = stained("q_pedra", (.27, .26, .24), stain=(.05, .045, .04), amount=.35, scale=9, rough=.8,
                    blotch=(.14, .13, .12), blotch_amt=.5, grime=0)
    face = stained("q_placa", (.72, .7, .64), stain=(.2, .17, .13), amount=.15, scale=5, rough=.15,
                   blotch=(.5, .47, .4), blotch_amt=.35, grime=0)
    oco = mat("q_oco", (.015, .012, .012), 0, .9)
    batina = stained("q_batina", (.11, .024, .022), stain=(.04, .02, .015), amount=.5, scale=4, rough=.85,
                     blotch=(.07, .05, .04), blotch_amt=.5, grime=1.2)
    sobre = stained("q_sobrepeliz", (.42, .39, .33), stain=(.16, .1, .05), amount=.55, scale=3.5, rough=.95,
                    blotch=(.2, .17, .13), blotch_amt=.6, grime=1.5)
    latao = stained("q_latao", (.3, .2, .08), stain=(.06, .09, .07), amount=.6, scale=7, metal=.9, rough=.55, grime=.2)
    ferro = stained("q_ferro", (.1, .085, .075), stain=(.28, .1, .04), amount=.55, scale=8, metal=.75, rough=.55, grime=.3)
    couro = stained("q_couro", (.06, .04, .028), stain=(.12, .03, .015), amount=.35, scale=6, rough=.6, grime=.3)
    pena = stained("q_pena", (.4, .38, .34), stain=(.07, .065, .06), amount=.45, scale=6, rough=.85,
                   blotch=(.14, .13, .12), blotch_amt=.6, grime=.2)
    queim = stained("q_pena_suja", (.08, .075, .07), stain=(.16, .07, .03), amount=.3, scale=9, rough=.9, grime=0)
    corda = mat("q_corda", (.25, .2, .13), 0, .9, dirt=.5, grime=.3)
    luz = glow("q_luz", (1, .8, .42), 12)
    luz_morta = stained("q_rachadura_apagada", (.2, .16, .08), stain=(.03, .03, .03), amount=.3, scale=8, rough=.5, grime=0)

    R = Rig("querubim", B, ground=None)
    R.gexclude = set(HIDE)
    P = R.P

    # ------------------------------------------------ corpo de porcelana (gordinho de querubim)
    j = {"pelvis": (0, 0, .69, .095, .08), "waist": (0, -.01, .8, .095, .085), "chest": (0, 0, .95, .11, .09),
         "neck": (0, -.005, 1.07, .05), "neck2": (0, -.008, 1.12, .045)}
    e = [("pelvis", "waist"), ("waist", "chest"), ("chest", "neck"), ("neck", "neck2")]
    sh, el, wr = P("upper_arm.L"), P("forearm.L"), P("hand.L")
    j.update({"shL": (*(sh + Vector((-.015, 0, 0))), .05), "biL": (*sh.lerp(el, .5), .042), "elL": (*el, .034),
              "faL": (*el.lerp(wr, .45), .036), "wrL": (*wr, .026)})
    e += [("chest", "shL"), ("shL", "biL"), ("biL", "elL"), ("elL", "faL"), ("faL", "wrL")]
    shR, elR = P("upper_arm.R"), P("forearm.R")
    j.update({"shR": (*(shR + Vector((.015, 0, 0))), .05), "stR": (*shR.lerp(elR, .38), .043)})
    e += [("chest", "shR"), ("shR", "stR")]
    for s, n in ((1, "L"), (-1, "R")):
        h, k, a = P(f"thigh.{n}"), P(f"shin.{n}"), P(f"foot.{n}")
        j[f"hip{n}"] = (*h, .058); j[f"th{n}"] = (*h.lerp(k, .5), .056); j[f"kn{n}"] = (*k, .042)
        j[f"ca{n}"] = (*k.lerp(a, .35), .042); j[f"an{n}"] = (*a, .027)
        j[f"toe{n}"] = (*(P(f"foot.{n}", 1) + Vector((0, .01, .005))), .028, .02)
        e += [("pelvis", f"hip{n}"), (f"hip{n}", f"th{n}"), (f"th{n}", f"kn{n}"), (f"kn{n}", f"ca{n}"),
              (f"ca{n}", f"an{n}"), (f"an{n}", f"toe{n}")]
    body = skin_mesh("porcelana", j, e, porc)
    R.bind(body, ["hips", "spine", "chest", "neck", "upper_arm.L", "forearm.L", "upper_arm.R",
                  "thigh.L", "thigh.R", "shin.L", "shin.R", "foot.L", "foot.R"])

    # juntas de boneco (latão) e rachaduras escuras
    for bn, at, r in (("forearm.L", 0, .04), ("shin.L", 0, .046), ("shin.R", 0, .046)):
        R.rigid([prim("primitive_uv_sphere_add", latao, P(bn, at), (r, r, r), segments=12, ring_count=8)], bn)
    # mão esquerda: palma e dedos (aponta no raio)
    o, ax, u, sd = R.frame("hand.L", up=Vector((0, -1, 0)))
    hp = [prim("primitive_uv_sphere_add", porc, o + ax*.03, (.032, .02, .036), segments=10, ring_count=6)]
    hp[0].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
    for f in range(4):
        b0 = o + ax*.055 + sd*(-.018 + .012*f)
        hp.append(along("primitive_cylinder_add", porc, b0, b0 + ax*(.045 - .006*abs(f - 1.5)) + u*.004, .007, vertices=6))
    hp.append(along("primitive_cylinder_add", porc, o + ax*.02 - sd*.03, o + ax*.05 - sd*.05 - u*.01, .007, vertices=6))
    hp.append(prim("primitive_torus_add", latao, o - ax*.005, (1, 1, 1.2), major_radius=.03, minor_radius=.006,
                   major_segments=12, minor_segments=4))
    hp[-1].rotation_euler = ax.to_track_quat('Z', 'Y').to_euler()
    R.rigid(hp, "hand.L")
    # faísca do raio (escondida fora do ataque)
    c = P("spark") + Vector((0, -.02, -.02))
    sp = [prim("primitive_uv_sphere_add", luz, c, (.03, .03, .03), segments=10, ring_count=6)]
    for k in range(6):
        a = 2*math.pi*k/6 + .3; v = Vector((math.cos(a), -.35, math.sin(a))).normalized()
        sp.append(along("primitive_cone_add", luz, c, c + v*(.09 + .05*(k % 2)), .012, vertices=4, radius1=1, radius2=0))
    R.rigid(sp, "spark")

    # ------------------------------------------------ braço direito arrancado: borda quebrada e mecanismo
    st = shR.lerp(elR, .38); ad = (elR - shR).normalized()
    mech = []
    for k in range(7):  # borda de porcelana lascada
        a = 2*math.pi*k/7; v = ad.to_track_quat('Z', 'Y') @ Vector((math.cos(a), math.sin(a), 0))
        mech.append(along("primitive_cone_add", porc, st - ad*.015 + v*.036, st + ad*(.02 + .025*rnd.random()) + v*.03, .014,
                          vertices=4, radius1=1, radius2=0))
    mech.append(prim("primitive_cylinder_add", oco, st + ad*.003, (.036, .036, .006), vertices=12))
    mech[-1].rotation_euler = ad.to_track_quat('Z', 'Y').to_euler()
    mech += gear(latao, st + ad*.03 + Vector((0, -.012, .004)), (0, 1, .3), .04, .012, 11, ferro)
    mech += gear(latao, st + ad*.05 + Vector((.006, .02, -.03)), (1, .2, 0), .028, .01, 8, ferro)
    mech.append(along("primitive_cylinder_add", ferro, st - ad*.02, st + ad*.13, .009, vertices=6))  # eixo partido
    mech.append(along("primitive_cone_add", ferro, st + ad*.13, st + ad*.15 + Vector((0, -.01, .01)), .009, vertices=5,
                      radius1=1, radius2=.3))
    for k in range(3):  # molas/fios soltos
        p0 = st + ad*.02 + Vector((0, .01*(k - 1), .012*(k - 1)))
        p1 = p0 + ad*.06 + Vector((.01, .015*(k - 1), -.04 - .02*k))
        mech.append(along("primitive_cylinder_add", latao if k % 2 else ferro, p0, p1, .003, vertices=4))
    R.rigid(mech, "upper_arm.R")
    # corrente partida pendurada do eixo (balança com o osso do antebraço)
    ch = []
    for k in range(4):
        cc = elR.lerp(shR, .55) + Vector((0, 0, -.035*k))
        ch.append(prim("primitive_torus_add", ferro, cc, (1, 1, 1.5), major_radius=.012, minor_radius=.004,
                       major_segments=8, minor_segments=4, rot=(0, 90*(k % 2), 0)))
    R.rigid(ch, "forearm.R")

    # ------------------------------------------------ batina de coroinha (vermelho sujo) e sobrepeliz rasgada
    bt = skirt("batina", batina, [(1.07, .07, .06, 0), (1.03, .11, .09, 0), (.92, .12, .1, 0), (.78, .115, .1, .005),
                                   (.66, .13, .11, .008), (.48, .165, .14, .015), (.3, .2, .17, .025)],
               jag=.05, seed=4, thick=.008)
    R.bind(bt, ["hips", "spine", "chest", "thigh.L", "thigh.R", "shin.L", "shin.R"], power=3)
    sp_ = skirt("sobrepeliz", sobre, [(1.085, .065, .055, 0), (1.05, .125, .1, 0), (.96, .135, .115, 0),
                                      (.82, .14, .12, .004), (.7, .17, .145, .01), (.58, .205, .175, .016)],
                jag=.07, seed=8, thick=.007)
    R.bind(sp_, ["hips", "spine", "chest"], power=3)
    # gola vermelha e manga larga (esquerda) da sobrepeliz
    R.rigid([prim("primitive_torus_add", batina, (0, -.005, 1.075), (1, .92, 1.6), major_radius=.052, minor_radius=.014,
                  major_segments=16, minor_segments=5)], "neck")
    o = skin_mesh("manga.L", {"a": (*(sh + Vector((-.02, 0, .005))), .06), "b": (*sh.lerp(el, .55), .062),
                              "c": (*sh.lerp(el, .95), .075)}, [("a", "b"), ("b", "c")], sobre, levels=1)
    R.bind(o, ["chest", "upper_arm.L"])
    # manga direita rasgada: farrapos pendurados
    rg = []
    for k in range(4):
        a = -1 + .7*k; p0 = shR + Vector((.015*math.cos(a), .05*math.sin(a) - .01, -.02))
        rg.append(along("primitive_cube_add", sobre, p0, p0 + ad*.05 + Vector((0, 0, -.08 - .03*(k % 2))), .006))
        rg[-1].scale = (.022, .004, rg[-1].scale[2])
    R.rigid(rg, "upper_arm.R")
    # renda puída na barra da sobrepeliz (furinhos escuros)
    lace = []
    for k in range(18):
        a = 2*math.pi*k/18
        lace.append(prim("primitive_uv_sphere_add", oco, (.2*math.cos(a), .016 + .171*math.sin(a), .615), (.012, .012, .012),
                         segments=6, ring_count=4))
    # cordão (cíngulo) com borla, cinta de couro das asas em X e placa de latão nas costas
    lace.append(prim("primitive_torus_add", corda, (0, .0, .8), (1, .87, 1), major_radius=.112, minor_radius=.009,
                     major_segments=18, minor_segments=4))
    for k in range(2):
        p0 = Vector((.06 - .025*k, -.1, .8)); p1 = p0 + Vector((.01, -.01, -.16 - .04*k))
        lace.append(along("primitive_cylinder_add", corda, p0, p1, .006, vertices=4))
        lace.append(prim("primitive_uv_sphere_add", corda, p1, (.014, .014, .022), segments=6, ring_count=4))
    R.rigid(lace, "hips")
    cs = []
    for s in (1, -1):
        cs.append(along("primitive_cylinder_add", couro, (.1*s, -.105, 1.02), (-.08*s, -.13, .8), .011, vertices=6))
        cs.append(along("primitive_cylinder_add", couro, (.1*s, -.105, 1.02), (.12*s, .09, 1.0), .011, vertices=6))
    cs.append(prim("primitive_cube_add", latao, (0, -.135, .9), (.025, .008, .025), rot=(-8, 0, 45)))
    cs.append(prim("primitive_cube_add", latao, (0, .12, .97), (.08, .015, .07), rot=(10, 0, 0)))  # placa das asas
    for dx, dz in ((-.06, .05), (.06, .05), (-.06, -.05), (.06, -.05)):
        cs.append(prim("primitive_uv_sphere_add", ferro, (dx, .108 + dz*.17, .97 + dz), (.011, .011, .011), segments=6, ring_count=4))
    # pistão do lado da asa de chapa
    cs.append(along("primitive_cylinder_add", ferro, (-.05, .13, .88), (-.2, .13, 1.06), .012, vertices=8))
    cs.append(along("primitive_cylinder_add", latao, (-.05, .13, .88), (-.11, .13, .95), .018, vertices=8))
    R.rigid(cs, "chest")

    # ------------------------------------------------ cabeça: nuca de estátua com cachos, placa lisa rachada
    hd = []
    hd.append(prim("primitive_uv_sphere_add", pedra, (0, .01, 1.225), (.11, .112, .12), segments=18, ring_count=12))
    for k in range(22):  # cachos de pedra (estátua de querubim)
        a = rnd.uniform(-2.3, 2.3); el_ = rnd.uniform(.15, 1.25)
        v = Vector((math.sin(a)*math.cos(el_), math.cos(a)*math.cos(el_)*.9 + .05, math.sin(el_)))
        if v.y < -.25 and v.z < .7: continue
        c = Vector((0, .01, 1.225)) + Vector((v.x*.11, v.y*.112, v.z*.12))
        hd.append(prim("primitive_uv_sphere_add", pedra, c, (.03, .03, .028), segments=8, ring_count=6))
    # lasca na lateral direita (oco escuro)
    hd.append(prim("primitive_uv_sphere_add", oco, (-.085, .02, 1.28), (.04, .045, .035), segments=10, ring_count=6))
    # placa lisa no lugar do rosto
    FZ, FX, FY, FT = 1.205, .1, .122, .045
    hd.append(prim("primitive_uv_sphere_add", face, (0, -.085, FZ), (FX, FT, FY), segments=18, ring_count=12))
    hd.append(prim("primitive_torus_add", ferro, (0, -.085, FZ), (FX/.1, FY/.1, 1), major_radius=.1, minor_radius=.006,
                   major_segments=24, minor_segments=4, rot=(90, 0, 0)))
    def surf(x, z, out=0):
        k = 1 - (x/FX)**2 - ((z - FZ)/FY)**2
        return Vector((x, -.085 - FT*math.sqrt(max(0, k)) - out, z))
    crack = [(-.055, .075), (-.03, .045), (-.035, .02), (-.005, .0), (.01, -.025), (-.002, -.05), (.025, -.08)]
    for (x0, z0), (x1, z1) in zip(crack, crack[1:]):
        a, b = surf(x0, FZ + z0, .0), surf(x1, FZ + z1, .0)
        hd.append(along("primitive_cylinder_add", oco, a + Vector((0, .002, 0)), b + Vector((0, .002, 0)), .011, vertices=6))
        hd.append(along("primitive_cylinder_add", luz, surf(x0, FZ + z0, .003), surf(x1, FZ + z1, .003), .0055, vertices=5))
    for (x0, z0), (x1, z1) in (((-.03, .045), (-.06, .03)), ((.01, -.025), (.04, -.02))):  # ramos
        hd.append(along("primitive_cylinder_add", oco, surf(x0, FZ + z0), surf(x1, FZ + z1), .006, vertices=5))
        hd.append(along("primitive_cylinder_add", luz, surf(x0, FZ + z0, .003), surf(x1, FZ + z1, .002), .003, vertices=4))
    # haste e auréola de latão torta
    hc = Vector((.035, .16, 1.43))
    hd.append(along("primitive_cylinder_add", ferro, (0, .1, 1.2), (.01, .17, 1.3), .009, vertices=6))
    hd.append(along("primitive_cylinder_add", ferro, (.01, .17, 1.3), hc + Vector((0, .01, -.03)), .008, vertices=6))
    hd.append(prim("primitive_torus_add", latao, (0, .105, 1.2), (1, 1, 1.4), major_radius=.02, minor_radius=.007,
                   major_segments=10, minor_segments=4, rot=(80, 0, 0)))  # braçadeira na nuca
    rot = (62, 8, 18)
    hd.append(prim("primitive_torus_add", latao, hc, (1, 1, 1), major_radius=.14, minor_radius=.014,
                   major_segments=28, minor_segments=6, rot=rot))
    hd.append(prim("primitive_torus_add", luz, hc, (1, 1, 1), major_radius=.125, minor_radius=.011,
                   major_segments=28, minor_segments=5, rot=rot))
    hq = Quaternion((1, 0, 0), math.radians(rot[0])); hq = Quaternion((0, 1, 0), math.radians(rot[1])) @ hq
    hq = Quaternion((0, 0, 1), math.radians(rot[2])) @ hq
    for k in range(8):  # rebites e uma lasca torta
        a = 2*math.pi*k/8; v = hq @ Vector((math.cos(a), math.sin(a), 0))
        hd.append(prim("primitive_uv_sphere_add", ferro, hc + v*.14 + (hq @ Vector((0, 0, .014))), (.01, .01, .01),
                       segments=6, ring_count=4))
    v = hq @ Vector((math.cos(2.2), math.sin(2.2), 0))
    hd.append(along("primitive_cone_add", latao, hc + v*.14, hc + v*.2 + Vector((0, 0, .04)), .013, vertices=5, radius1=1, radius2=.2))
    R.rigid(hd, "head")
    # raios do clarão (escondidos fora do flash)
    c0 = P("burst")
    br = [prim("primitive_uv_sphere_add", luz, c0 + Vector((0, -.01, 0)), (.07, .02, .085), segments=12, ring_count=8)]
    for k in range(16):
        a = 2*math.pi*k/16 + rnd.uniform(-.1, .1); L = (.42 if k % 2 else .26)*rnd.uniform(.8, 1.15)
        v = Vector((math.cos(a), -.35, math.sin(a))).normalized()
        br.append(along("primitive_cone_add", luz, c0 + v*.06, c0 + v*(.06 + L), .022 if k % 2 else .016, vertices=4,
                        radius1=1, radius2=0))
    R.rigid(br, "burst")

    # ------------------------------------------------ asas: esquerda de penas sujas, direita de chapa remendada
    DN = Vector((0, -1, 0))
    for s, n in ((1, "L"), (-1, "R")):
        X = lambda v: Vector((v[0]*s, v[1], v[2]))
        metal = n == "R"
        lj = {"a": (*X((.06, .085, 1.0)), .04, .03), "b": (*X((.24, .1, 1.1)), .034, .024),
              "c": (*X((.44, .12, 1.17)), .026, .018), "d": (*X((.64, .13, 1.19)), .014)}
        if metal:  # vareta de ferro com juntas de latão
            for k, (a, b) in enumerate((("a", "b"), ("b", "c"), ("c", "d"))):
                bn = f"wing{k+1}.{n}"
                pa, pb = Vector(lj[a][:3]), Vector(lj[b][:3])
                parts = [along("primitive_cylinder_add", ferro, pa, pb, .018 - .003*k, vertices=8),
                         prim("primitive_uv_sphere_add", latao, pa, (.03, .03, .03), segments=10, ring_count=6)]
                R.rigid(parts, bn)
        else:
            le = skin_mesh(f"borda.{n}", lj, [("a", "b"), ("b", "c"), ("c", "d")], pena, levels=1)
            R.bind(le, ["chest", f"wing1.{n}", f"wing2.{n}", f"wing3.{n}"], power=6)
        # primárias (ponta): de "para fora e para baixo" até "para baixo"
        prim_specs = []
        for i in range(7):
            t = i/6
            base = X((.64 - .2*t, .13 - .01*t, 1.19 - .02*t))
            ang = math.radians(18 + 62*t)
            d = X((math.cos(ang), .12, -math.sin(ang)))
            prim_specs.append((base + Vector((0, .004*i, 0)), d, DN, (.44 - .06*t)*rnd.uniform(.9, 1.05), .075, rnd.uniform(.6, .8), -.08))
        sec = [(X((.44 - .2*(k + .5)/5, .1 + .002*k, 1.15 - .05*(k + .5)/5)), X((.12, .15, -1)), DN,
                rnd.uniform(.33, .38), .08, rnd.uniform(.6, .8), -.06) for k in range(5)]
        ter = [(X((.24 - .17*(k + .5)/4, .085 + .002*k, 1.08 - .07*(k + .5)/4)), X((-.05, .15, -1)), DN,
                rnd.uniform(.27, .31), .075, rnd.uniform(.65, .85), -.05) for k in range(4)]
        cov = {1: [], 2: [], 3: []}
        for k in range(12):  # cobertoras: duas fileiras curtas na frente
            t = (k + .5)/12; x = .07 + .56*t
            bn = 1 if x < .24 else (2 if x < .44 else 3)
            z = 1.0 + (1.19 - 1.0)*min(1, t*1.3)
            cov[bn].append((X((x, .09 + .03*t - .012, z)), X((.08, .1, -1)), DN, rnd.uniform(.13, .17), .07, .9, -.03))
        if not metal:
            R.rigid([feathers(f"prim.{n}", prim_specs, pena, queim, rnd), feathers(f"cob3.{n}", cov[3], pena, queim, rnd)], f"wing3.{n}")
            R.rigid([feathers(f"sec.{n}", sec, pena, queim, rnd), feathers(f"cob2.{n}", cov[2], pena, queim, rnd)], f"wing2.{n}")
            R.rigid([feathers(f"ter.{n}", ter, pena, queim, rnd), feathers(f"cob1.{n}", cov[1], pena, queim, rnd)], f"wing1.{n}")
        else:
            for bn, specs in ((3, prim_specs), (2, sec), (1, ter)):
                parts = []
                for i, (b0, d, up, L, W, burnt, dr) in enumerate(specs):
                    if bn == 2 and i == 2:  # uma pena verdadeira que sobrou no meio das chapas
                        parts.append(feathers(f"sobra.{n}", [(b0 + Vector((0, .006, 0)), d, up, L*.95, W, .7, -.05)], pena, queim, rnd))
                        continue
                    mt = latao if (i + bn) % 3 == 0 else ferro
                    parts.append(plate(mt, b0 + Vector((0, .006*(i % 2), 0)), d, L*.92, W*.9))
                    tip = b0 + d.normalized()*L*.92
                    parts.append(along("primitive_cone_add", mt, tip - d.normalized()*.002, tip + d.normalized()*.05, W*.45,
                                       vertices=4, radius1=1, radius2=0))
                    parts[-1].scale = (W*.45, .004, parts[-1].scale[2])
                    for tt in (.12, .55):  # rebites
                        parts.append(prim("primitive_uv_sphere_add", latao, b0 + d.normalized()*L*tt + Vector((0, -.008, 0)),
                                          (.008, .006, .008), segments=6, ring_count=4))
                if bn == 2:  # remendo de couro costurado com arame
                    c = X((.36, .1, .95))
                    parts.append(prim("primitive_cube_add", couro, c + Vector((0, -.012, 0)), (.07, .005, .09), rot=(0, 12*s, 0)))
                    for k in range(4):
                        parts.append(along("primitive_cylinder_add", ferro, c + Vector((-.07, -.018, -.07 + .045*k)),
                                           c + Vector((.07, -.018, -.06 + .045*k)), .003, vertices=4))
                for i, cv in enumerate(cov[bn]):
                    b0, d, up, L, W = cv[:5]
                    parts.append(plate(ferro if i % 2 else latao, b0 + Vector((0, -.004, 0)), d, L, W*.95, .006))
                R.rigid(parts, f"wing{bn}.{n}")

    # ------------------------------------------------ cacos no chão (só no fim da morte; osso "floor" fixo no chão)
    fl = []
    hc2 = Vector((.12, -.66, .0))
    back = prim("primitive_uv_sphere_add", porc, hc2 + Vector((0, 0, .05)), (.11, .11, .1), segments=16, ring_count=10)
    fl.append(back)
    fl.append(prim("primitive_uv_sphere_add", oco, hc2 + Vector((0, -.02, .1)), (.085, .075, .03), segments=12, ring_count=6))
    for k in range(8):
        a = rnd.uniform(0, 2*math.pi)
        fl.append(prim("primitive_uv_sphere_add", porc, hc2 + Vector((.09*math.cos(a), .09*math.sin(a), .1)), (.028, .028, .024),
                       segments=8, ring_count=5))
    for k, (dx, dy, rz) in enumerate(((-.12, -.16, 25), (.04, -.24, -40))):  # placa partida em duas
        c = hc2 + Vector((dx, dy, .012))
        fl.append(prim("primitive_uv_sphere_add", face, c, (.075, .055, .014), segments=14, ring_count=8, rot=(0, 0, rz)))
        fl.append(along("primitive_cylinder_add", luz_morta, c + Vector((-.04, .01, .012)), c + Vector((.04, -.01, .012)), .005, vertices=4))
    hal = Vector((-.32, -.92, .016))
    fl.append(prim("primitive_torus_add", latao, hal, (1, 1, 1), major_radius=.14, minor_radius=.014, major_segments=28,
                   minor_segments=6, rot=(6, -4, 0)))
    fl.append(along("primitive_cylinder_add", ferro, hal + Vector((.13, .05, .01)), hal + Vector((.3, .14, .01)), .008, vertices=6))
    for k in range(14):  # cacos de porcelana
        a = rnd.uniform(0, 2*math.pi); r = rnd.uniform(.15, .55)
        c = Vector((.05 + r*math.cos(a), -.45 + r*math.sin(a)*.9, .008))
        o = prim("primitive_ico_sphere_add", porc if k % 4 else face, c, (rnd.uniform(.025, .05), rnd.uniform(.018, .035), .012),
                 subdivisions=1, rot=(0, 0, rnd.uniform(0, 180)), smooth=False)
        fl.append(o)
    for k, (dx, dy) in enumerate(((.3, -.3), (-.2, -.5), (.38, -.7))):
        fl += gear(latao, Vector((dx, dy, .006)), (0, .1, 1), .035 - .006*k, .008, 9, ferro)
    R.rigid(fl, "floor")

    R.arm.scale = [SCALE]*3
    safe_ground(R)
    return R, INFO

# ======================================================================= animações
def fx(**k): return {"fx": k}

def finalize(poses):
    """Converte "fx" (interpolável) em "scale" (peças escondidas = 0.001)."""
    for p in poses:
        f = p.pop("fx", {}) or {}
        p["scale"] = {b: max(.001, f.get(b, 0)) for b in HIDE}
    return poses

def flap(t, amp=40, mid=22, sweep=24, fold=1.0):
    """Batida pairando. t 0..1: 0 asas no alto, .5 embaixo; recolhe a mão na subida."""
    p = 2*math.pi*t; c = math.cos(p); up = max(0, -math.sin(p))
    return wings(mid + amp*c, 12*math.cos(p - .7) - 8*up*fold, 16*math.cos(p - 1.3) - 14*up*fold,
                 sweep - 10*math.sin(p), 6 + 18*up*fold, 22*up*fold, tw=-6*math.sin(p)), c

LEGS = {"thigh.L": {"x": -12, "y": -3}, "thigh.R": {"x": -28, "y": 4}, "shin.L": {"bend": 55}, "shin.R": {"bend": 38},
        "foot.L": {"x": 38}, "foot.R": {"x": 30}}
BASE = merge(LEGS, {"chest": {"x": -2}, "head": {"x": 6}, "neck": {"x": 2},
                    "upper_arm.L": {"y": 30, "x": -12}, "forearm.L": {"bend": -28}, "hand.L": {"x": -8},
                    "upper_arm.R": {"y": -12, "x": -6}, "forearm.R": {"bend": 0}, "ground": None})

def H(*p): return merge(BASE, *p)

def anims(R):
    idle = []
    for i in range(6):
        t = i/6; w, c = flap(t, 36, 24, 26)
        s = math.sin(2*math.pi*t)
        idle.append(H(w, {"chest": {"x": 2*c}, "head": {"x": -3*c, "z": 6*s}, "upper_arm.L": {"x": 4*c},
                          "thigh.L": {"x": 4*c}, "thigh.R": {"x": -3*c}, "forearm.R": {"x": 8*s},
                          "root": (0, 0, HOVER - .045*c)}))
    walk = []
    for i in range(8):
        t = i/8; w, c = flap(t, 48, 18, 30, 1.2)
        s = math.sin(2*math.pi*t)
        walk.append(H(w, {"hips": {"x": 14}, "spine": {"x": 6}, "chest": {"x": 4 + 2*c}, "head": {"x": -12, "z": 4*s},
                          "thigh.L": {"x": 18 + 5*c}, "thigh.R": {"x": 12 - 5*c}, "shin.L": {"bend": 10}, "shin.R": {"bend": 18},
                          "upper_arm.L": {"x": 18, "y": 6}, "forearm.L": {"bend": -10}, "forearm.R": {"x": 22},
                          "root": (0, 0, HOVER - .06*c)}))
    # raio: puxa o braço para trás (luz se junta na mão), estica apontando e dispara; o coice joga o corpo para trás
    w0, _ = flap(0, 36, 24, 26)
    base = H(w0, {"root": (0, 0, HOVER - .045)})
    wind = H(wings(55, 20, 12, 40, 14, 18), {"chest": {"x": -10, "z": 22}, "spine": {"z": 8}, "head": {"x": -6, "z": -14},
             "upper_arm.L": {"y": -40, "z": 50, "x": 0}, "forearm.L": {"bend": -70}, "hand.L": {"x": -20},
             "upper_arm.R": {"y": -30}, "root": (0, .06, HOVER + .04)}, fx(spark=.6))
    aim = H(wings(10, 5, -8, 10, 4, 6), {"chest": {"x": 8, "z": -14}, "spine": {"x": 4, "z": -6}, "head": {"x": 4, "z": 10},
            "upper_arm.L": {"y": -42, "z": -78, "x": 0}, "forearm.L": {"bend": 0}, "hand.L": {"x": 10},
            "upper_arm.R": {"y": -20, "x": 20}, "root": (0, -.05, HOVER - .02)}, fx(spark=1.7))
    kick = merge(aim, {"chest": {"x": -14}, "head": {"x": -8}, "upper_arm.L": {"y": -14}, "forearm.L": {"bend": -16},
                       "hips": {"x": -8}}, wings(40, 12, 0, 18, 8, 10), {"root": (0, .12, HOVER + .05)}, fx(spark=-.9))
    attack = finalize(keys_to_frames([(0, base), (.3, wind), (.42, aim), (.52, merge(aim, fx(spark=.2))), (.66, kick),
                                      (1, base)], 10))
    # clarão: se fecha (asas na frente do corpo), abre tudo de uma vez e a rachadura do rosto estoura em raios
    curl = H(wings(-25, -20, -18, -55, -25, -15), {"hips": {"x": 18}, "spine": {"x": 14}, "chest": {"x": 14}, "head": {"x": 22},
             "upper_arm.L": {"y": 50, "x": -40, "z": -30}, "forearm.L": {"bend": -95}, "upper_arm.R": {"y": 10, "x": -30},
             "thigh.L": {"x": -40}, "thigh.R": {"x": -48}, "shin.L": {"bend": 40}, "shin.R": {"bend": 50},
             "root": (0, 0, HOVER - .08)}, fx(burst=.15))
    open_ = H(wings(78, 22, 14, 6, -6, -4), {"hips": {"x": -10}, "spine": {"x": -10}, "chest": {"x": -12}, "head": {"x": -4},
              "neck": {"x": -4}, "upper_arm.L": {"y": -85, "x": -10}, "forearm.L": {"bend": -12}, "hand.L": {"x": -20},
              "upper_arm.R": {"y": -70, "x": -10}, "thigh.L": {"x": 10, "y": -10}, "thigh.R": {"x": 4, "y": 10},
              "shin.L": {"bend": -30}, "shin.R": {"bend": -20}, "foot.L": {"x": 10}, "foot.R": {"x": 10},
              "root": (0, .03, HOVER + .1)}, fx(burst=1.15))
    shake = lambda k: merge(open_, {"head": {"z": 4*(-1)**k}, "chest": {"z": 3*(-1)**k}},
                            wings(6*(-1)**k, 0, 0), fx(burst=.1*(-1)**k))
    flash = finalize(keys_to_frames([(0, base), (.28, curl), (.4, open_), (.52, shake(0)), (.64, shake(1)),
                                     (.78, merge(open_, fx(burst=-.75))), (1, base)], 10))
    # recuo (loop): corpo inclinado para trás, pernas para a frente, batidas fortes e braço protegendo o rosto
    retreat = []
    for i in range(8):
        t = i/8; w, c = flap(t, 52, 22, 6, 1.3)
        s = math.sin(2*math.pi*t)
        retreat.append(H(w, {"hips": {"x": -22}, "spine": {"x": -6}, "chest": {"x": -4 + 3*c}, "head": {"x": 16, "z": 5*s},
                             "thigh.L": {"x": -38 - 6*c}, "thigh.R": {"x": -30 + 6*c}, "shin.L": {"bend": 30}, "shin.R": {"bend": 22},
                             "upper_arm.L": {"y": -10, "x": -60, "z": -30}, "forearm.L": {"bend": -70}, "hand.L": {"x": -30},
                             "upper_arm.R": {"y": -25, "x": -20}, "forearm.R": {"x": -30},
                             "root": (0, .04*s, HOVER + .04 - .07*c)}))
    hitp = H(wings(60, 25, 22, 0, -10, 0), {"hips": {"x": -16, "y": 10}, "chest": {"x": -18}, "head": {"x": -26, "z": 16},
             "upper_arm.L": {"y": -10, "x": 30}, "forearm.L": {"bend": -40}, "upper_arm.R": {"y": -40},
             "forearm.R": {"x": -40}, "thigh.L": {"x": 10}, "thigh.R": {"x": 6}, "root": (0, .14, HOVER + .05)})
    hit = finalize([hitp, lerp_pose(hitp, base, .5), base])
    # morte: tranco, despenca girando, bate de cara no chão e a cabeça e o braço se partem em cacos
    GB = ["hips", "spine", "chest", "neck", "head", "upper_arm.L", "forearm.L", "thigh.L", "thigh.R", "shin.L", "shin.R",
          "wing1.L", "wing2.L", "wing1.R", "wing2.R"]
    stall = H(wings(85, 30, 25, -10, 10, 10), {"hips": {"x": -20, "y": -16}, "chest": {"x": -20}, "head": {"x": -30, "z": -20},
              "upper_arm.L": {"y": -60}, "forearm.L": {"bend": -20}, "root": (0, .08, HOVER + .12)})
    fall = H(wings(40, 10, 10, 30, 30, 20), {"hips": {"x": 50, "y": 30}, "chest": {"x": 10}, "head": {"x": 20, "z": 20},
             "upper_arm.L": {"y": -30, "x": -40}, "thigh.L": {"x": 30}, "thigh.R": {"x": 10}, "root": (0, -.1, HOVER - .3)})
    PRONE = {"hips": {"x": 84, "z": 12}, "spine": {"x": 4}, "chest": {"x": -6}, "neck": {"x": -10}, "head": {"x": -18, "z": 30},
             "upper_arm.L": {"y": -40, "x": -100}, "forearm.L": {"bend": -30}, "upper_arm.R": {"y": -60, "x": -40},
             "thigh.L": {"x": 4, "y": -6}, "thigh.R": {"x": -8, "y": 10}, "shin.L": {"bend": 30}, "shin.R": {"bend": 12},
             "foot.L": {"x": 30}, "foot.R": {"x": 20}, "gb": GB, "root": (0, -.05, 0)}
    land = merge(PRONE, wings(-8, -6, -4, 35, 10, 6), {"ground": .03})
    bounce = merge(PRONE, wings(4, -2, -6, 30, 8, 6), {"hips": {"x": -8}, "chest": {"x": -6}, "ground": .07})
    dead = merge(PRONE, wings(-14, -8, -2, 45, 10, 4), {"ground": .03})
    death = keys_to_frames([(0, hitp), (.15, stall), (.35, fall), (.5, land), (.62, bounce), (.78, dead), (1, dead)], 12)
    death = finalize(death)
    for i, p in enumerate(death):
        if i >= 6:  # impacto: cabeça e auréola viram cacos no chão
            p["ground"] = p.get("ground") if p.get("ground") is not None else .03; p["gb"] = GB
            p["scale"] = dict(p["scale"], head=.001, floor=1)
    return {"idle": finalize(idle), "walk": finalize(walk), "attack": attack, "flash": flash, "retreat": finalize(retreat),
            "hit": hit, "death": death}
