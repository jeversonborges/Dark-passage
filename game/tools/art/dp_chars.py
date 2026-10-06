# Sprites animados do DARK PASSAGE (personagens e monstros) em 8 direções.
# Usa as funções de dp_models.py do pipeline aprovado (mesma câmera, luz e escala).
# Uso: blender -b -P dp_chars.py -- <anjo|humano|carnical|flagelado|acougueiro> <saida_dir> [px]
# Saída: <saida_dir>/<anim>_<frame>_d<dir>.png   anims: idle(1) walk(4) attack(3) death(2)
import bpy, math, sys, os
from mathutils import Vector
sys.path.insert(0, "/mnt/project-files/tools/sprite-pipeline/darkeden")
import dp_models as M
from dp_models import mat, prim, along, body, hands_boots, spikes, wing, chain, coat

argv = sys.argv[sys.argv.index("--")+1:]
kind, out = argv[0], argv[1]
px = int(argv[2]) if len(argv) > 2 else 112
only = argv[3].split(",") if len(argv) > 3 else None
SAMPLES = 40

def walk_pose(p, arms=True):
    """Pose de caminhada na fase p (0..1). Frente do personagem = -Y."""
    s, c = math.sin(2*math.pi*p), math.cos(2*math.pi*p)
    d = {}
    for side, sg in (("L", 1), ("R", -1)):
        x = .1*(1 if side == "L" else -1)
        k = s*sg
        lift = max(0, c*sg)*.1
        d["knee"+side] = (x*1.2, -.03-.14*k-lift*.6, .5+lift*.5, .06)
        d["ankle"+side] = (x*1.3, -.24*k, .1+lift, .048)
        d["toe"+side] = (x*1.3, -.24*k-.13, .03+lift, .04)
    if arms:
        d["elL"] = (.3, .03+.1*s, 1.14, .05); d["wrL"] = (.34, -.04+.2*s, .9+.03*abs(s), .038)
        d["elR"] = (-.3, .03-.1*s, 1.14, .05); d["wrR"] = (-.34, -.04-.2*s, .9+.03*abs(s), .038)
    return d

def pivot(parent, loc):
    e = bpy.data.objects.new("pivot", None); bpy.context.scene.collection.objects.link(e)
    e.parent = parent; e.location = loc; return e

# ---------------------------------------------------------------- classes jogáveis
def anjo(root, f):
    """Cópia do anjo aprovado em dp_models, com pose e ângulo da espada animáveis."""
    leather = mat("couro_negro", (.02,.018,.02), .2, .35)
    skin = mat("pele_palida", (.55,.5,.48), 0, .5)
    bone = mat("osso", (.85,.82,.72), 0, .5)
    gold = mat("ouro_sujo", (.35,.25,.08), 1, .45)
    blood = mat("vermelho_sangue", (.18,.01,.01), .1, .3)
    steel = mat("aco_escuro", (.5,.5,.52), 1, .25)
    feather = mat("pena_suja", (.16,.15,.14), 0, .8)
    halo = mat("halo_rachado", (1,.8,.4), emit=(1,.6,.2), strength=5)
    pose = {"wrR":(-.36,-.12,.98,.038), "elR":(-.33,-.02,1.14,.05)}
    sword = 0
    if f["anim"] == "walk":
        pose.update(walk_pose(f["p"])); pose["wrR"] = (-.36,-.12,.98,.038); pose["elR"] = (-.33,-.02,1.14,.05)
    elif f["anim"] == "attack":
        sword, wr, el = [(-70, (-.32,.05,1.45), (-.33,.08,1.3)),
                         (75, (-.2,-.42,1.05), (-.3,-.18,1.2)),
                         (110, (-.12,-.35,.8), (-.3,-.12,1.08))][f["i"]]
        pose["wrR"] = (*wr, .038); pose["elR"] = (*el, .05)
        pose["chest"] = (0, -.04 if f["i"] else .03, 1.33, .165)
    j = body("anjo_corpo", leather, root, pose)
    hands_boots(j, skin, leather, root)
    coat(leather, blood, root)
    for s in (-1,1):
        prim("primitive_uv_sphere_add", bone, (.21*s,0,1.47), (.12,.12,.08), parent=root)
        for k in range(3):
            along("primitive_cone_add", steel, (.21*s+.04*(k-1)*s,0,1.53), (.27*s+.06*(k-1)*s,0,1.7), 1, root, radius1=.018, radius2=0, vertices=6)
    chain(steel, (.15,-.17,1.38), (-.12,-.16,1.05), 9, root)
    prim("primitive_uv_sphere_add", skin, (0,-.01,1.65), (.095,.1,.115), parent=root)
    prim("primitive_cube_add", blood, (0,-.1,1.66), (.06,.01,.008), parent=root)
    spikes(bone, Vector((0,.04,1.72)), 18, .3, 1.0, root, up=(0,.7,.6), seed=3)
    prim("primitive_torus_add", halo, (0,.08,1.88), (1,1,1), (20,0,0), parent=root, major_radius=.13, minor_radius=.012)
    wing(-1, feather, root, (-.08,.14,1.38)); wing(1, feather, root, (.08,.14,1.38))
    pv = pivot(root, j["wrR"] + Vector((0,-.04,-.04))); pv.rotation_euler = (math.radians(sword), 0, 0)
    prim("primitive_cube_add", steel, (0,0,.55), (.05,.012,.48), parent=pv)
    prim("primitive_cube_add", gold, (0,0,.06), (.17,.025,.025), parent=pv)
    prim("primitive_cube_add", blood, (.02,-.013,.75), (.012,.002,.2), parent=pv)

def humano(root, f):
    """Cópia do humano aprovado em dp_models, com caminhada e disparo da escopeta."""
    fatigue = mat("farda", (.09,.09,.07), 0, .8)
    skin = mat("pele", (.42,.3,.24), 0, .5)
    boot = mat("bota", (.02,.02,.02), 0, .4)
    vest = mat("colete_azul_aco", (.1,.13,.17), .3, .5)
    acid = mat("verde_acido", (.2,.6,.05), 0, .4, emit=(.4,1,.1), strength=1.5)
    ember = mat("laranja_brasa", (.6,.2,.02), 0, .4, emit=(1,.35,.05), strength=6)
    flash = mat("clarao", (1,.7,.3), emit=(1,.65,.2), strength=40)
    metal = mat("metal_gasto", (.15,.15,.15), 1, .4)
    wood = mat("madeira", (.18,.09,.04), 0, .6)
    leather = mat("couro_marrom", (.1,.05,.03), 0, .5)
    arms = {"elR":(-.24,-.15,1.12,.05), "wrR":(-.12,-.35,1.07,.038), "elL":(.28,-.1,1.12,.05), "wrL":(.12,-.42,1.12,.038)}
    pose = dict(arms)
    if f["anim"] == "walk":
        pose.update(walk_pose(f["p"], arms=False))
    elif f["anim"] == "attack":
        back = [0, .1, .04][f["i"]]; up = [0, .05, .02][f["i"]]
        pose = {k: (v[0], v[1]+back, v[2]+up, v[3]) for k, v in arms.items()}
        pose["chest"] = (0, back*.6, 1.33, .165)
    j = body("humano_corpo", fatigue, root, pose)
    hands_boots(j, skin, boot, root)
    prim("primitive_cube_add", vest, (0,-.01,1.24), (.17,.13,.17), parent=root)
    prim("primitive_uv_sphere_add", vest, (.2,0,1.44), (.09,.09,.06), parent=root)
    for i in range(8):
        t = i/7; p = Vector((.17,-.16,1.45)).lerp(Vector((-.17,-.16,1.02)), t)
        along("primitive_cylinder_add", ember, p, p+Vector((0,-.03,.02)), .012, root, vertices=6)
    prim("primitive_torus_add", leather, (0,0,.95), (1,1,.6), parent=root, major_radius=.165, minor_radius=.03)
    along("primitive_cylinder_add", leather, (0,.12,1.0), (0,.18,1.45), .07, root, vertices=10)
    prim("primitive_cylinder_add", acid, (.19,-.05,.88), (.035,.035,.06), parent=root)
    prim("primitive_uv_sphere_add", skin, (0,-.01,1.64), (.09,.1,.11), parent=root)
    for i in range(7):
        y = -.08 + i*.03
        along("primitive_cone_add", acid, (0,y,1.7+.01*math.sin(i)), (0,y+.04,1.86-abs(i-3)*.02), 1, root, radius1=.025, radius2=0, vertices=5)
    prim("primitive_cylinder_add", vest, (0,-.02,1.565), (.075,.08,.03), parent=root)
    prim("primitive_cube_add", ember, (0,-.105,1.66), (.06,.006,.007), parent=root)
    a, b = j["wrR"] + Vector((0,.1,.0)), j["wrL"] + Vector((0,-.25,.02))
    along("primitive_cylinder_add", metal, a, b, .022, root, vertices=10)
    along("primitive_cube_add", wood, a + Vector((0,.25,-.06)), a, .03, root)
    prim("primitive_cube_add", wood, j["wrL"], (.03,.06,.025), parent=root)
    if f["anim"] == "attack" and f["i"] == 1:
        d = (b - a).normalized()
        for k in range(4):
            prim("primitive_cone_add", flash, b + d*(.12+k*.03), (1,1,1), parent=root, radius1=.09-.02*k, depth=.25, vertices=7)
            bpy.context.object.rotation_euler = d.to_track_quat('Z','Y').to_euler()

# ---------------------------------------------------------------- monstros
def carnical(root, f):
    """Carniçal: morto da praga, curvado, trapos, olhos verde-ácido."""
    flesh = mat("carne_praga", (.075,.085,.06), 0, .7)
    rag = mat("trapo", (.03,.022,.015), 0, .95)
    bone = mat("osso_sujo", (.45,.42,.34), 0, .6)
    eye = mat("olho_acido", (.3,.9,.1), emit=(.5,1,.15), strength=8)
    gore = mat("sangue_seco", (.12,.01,.01), .1, .3)
    pose = {"chest":(0,-.12,1.25,.15), "neck":(0,-.2,1.4,.05), "spine":(0,-.05,1.1,.12),
            "shL":(.19,-.1,1.33,.06), "shR":(-.19,-.1,1.33,.06),
            "elL":(.25,-.35,1.2,.045), "wrL":(.22,-.6,1.15,.035),
            "elR":(-.25,-.3,1.15,.045), "wrR":(-.22,-.55,1.05,.035),
            "kneeL":(.13,-.1,.48,.06), "kneeR":(-.13,-.1,.48,.06)}
    if f["anim"] == "walk":
        w = walk_pose(f["p"], arms=False); w = {k: (v[0], v[1]*.6, v[2], v[3]) for k, v in w.items()}
        pose.update(w); pose["wrL"] = (.22,-.6+.08*math.sin(2*math.pi*f["p"]),1.15,.035)
    elif f["anim"] == "attack":
        r = [(.35,.1,1.55), (.05,-.7,1.0), (-.1,-.55,.8)][f["i"]]
        pose["wrR"] = (-r[0], r[1], r[2], .035); pose["elR"] = (-.3, (r[1]-.1)/2, 1.25, .045)
        pose["wrL"] = (r[0]*.8, r[1]-.05, r[2]+.05, .035)
    j = body("carnical_corpo", flesh, root, pose)
    for s in "LR":
        prim("primitive_uv_sphere_add", flesh, j["wr"+s] + Vector((0,-.04,-.03)), (.05,.06,.04), parent=root)
        for k in range(3):  # garras
            along("primitive_cone_add", bone, j["wr"+s] + Vector(((k-1)*.025,-.07,-.03)), j["wr"+s] + Vector(((k-1)*.03,-.17,-.08)), 1, root, radius1=.01, radius2=0, vertices=5)
        prim("primitive_uv_sphere_add", flesh, j["toe"+s], (.05,.09,.035), parent=root)
    prim("primitive_cube_add", rag, (0,-.05,1.0), (.17,.14,.22), (12,0,0), parent=root)
    for k in range(5):
        prim("primitive_cube_add", rag, ((k-2)*.07,-.12+abs(k-2)*.03,.72), (.035,.01,.12+.04*(k%2)), (8,0,(k-2)*6), parent=root)
    for k in range(4):  # costelas expostas
        prim("primitive_torus_add", bone, (0,-.14,1.32-k*.05), (1,.5,1), (80,0,0), parent=root, major_radius=.1, minor_radius=.008)
    head = j["neck"] + Vector((0,-.06,.1))
    prim("primitive_uv_sphere_add", flesh, head, (.085,.1,.1), parent=root)
    prim("primitive_cube_add", gore, head + Vector((0,-.08,-.06)), (.05,.03,.02), parent=root)
    for s in (-1,1):
        prim("primitive_uv_sphere_add", eye, head + Vector((.035*s,-.085,.02)), (.016,.01,.012), parent=root)
    spikes(bone, head + Vector((0,.03,.07)), 6, .1, .8, root, up=(0,.4,1), seed=9)

def flagelado(root, f):
    """Flagelado: penitente encapuzado com corrente enferrujada e lentes vermelhas."""
    robe = mat("batina_vinho", (.045,.006,.008), 0, .9)
    skin = mat("pele_cinza", (.3,.27,.25), 0, .6)
    iron = mat("ferro_ferrugem", (.12,.06,.03), .6, .7)
    bone = mat("mascara_osso", (.6,.56,.46), 0, .6)
    lens = mat("lente_rubra", (.8,.05,.03), emit=(1,.05,.02), strength=10)
    pose = {}
    swing = 0
    if f["anim"] == "walk":
        pose.update(walk_pose(f["p"]))
    elif f["anim"] == "attack":
        r = [(-.3,.15,1.75), (-.25,-.5,1.3), (-.1,-.45,.85)][f["i"]]
        pose["wrR"] = (*r, .038); pose["elR"] = (-.32, r[1]/2, 1.3, .05)
        swing = [-120, 20, 70][f["i"]]
    j = body("flagelado_corpo", robe, root, pose)
    hands_boots(j, skin, iron, root)
    # túnica até o chão
    along("primitive_cone_add", robe, (0,0,1.35), (0,0,.04), 1, root, radius1=.2, radius2=.38, vertices=14)
    prim("primitive_torus_add", iron, (0,0,1.0), (1,1,.6), parent=root, major_radius=.2, minor_radius=.025)
    # capuz pontudo e máscara de osso com lentes
    prim("primitive_uv_sphere_add", robe, (0,0,1.66), (.13,.14,.14), parent=root)
    along("primitive_cone_add", robe, (0,.02,1.72), (0,.12,2.05), 1, root, radius1=.11, radius2=0, vertices=10)
    prim("primitive_uv_sphere_add", bone, (0,-.08,1.64), (.08,.05,.09), parent=root)
    for s in (-1,1):
        prim("primitive_cylinder_add", lens, (.035*s,-.13,1.67), (.022,.022,.01), (90,0,0), parent=root)
    along("primitive_cylinder_add", iron, (0,-.13,1.6), (0,-.18,1.55), .03, root, vertices=8)
    # flagelo: cabo + corrente com bola de pregos
    pv = pivot(root, j["wrR"]); pv.rotation_euler = (math.radians(swing), 0, 0)
    along("primitive_cylinder_add", iron, (0,0,-.02), (0,0,.18), .018, pv, vertices=6)
    chain(iron, (0,0,.18), (0,.05,.6), 7, pv)
    prim("primitive_uv_sphere_add", iron, (0,.05,.66), (.07,.07,.07), parent=pv)
    spikes(iron, Vector((0,.05,.66)), 7, .09, 1, pv, up=(0,0,1), seed=2)

def acougueiro(root, f):
    """Açougueiro de Velgrad: chefe gordo com avental, máscara de gás e cutelo."""
    flesh = mat("carne_palida", (.17,.12,.1), 0, .6)
    apron = mat("avental_sangue", (.08,.065,.05), 0, .8)
    blood = mat("sangue_fresco", (.25,.0,.0), .1, .25)
    leather = mat("couro_negro", (.02,.018,.02), .2, .35)
    steel = mat("aco_cutelo", (.45,.45,.47), 1, .3)
    brass = mat("latao", (.35,.22,.08), 1, .4)
    eye = mat("lente_brasa", (1,.4,.05), emit=(1,.35,.05), strength=10)
    pose = {"chest":(0,0,1.33,.24), "spine":(0,-.02,1.12,.25), "pelvis":(0,0,.95,.2),
            "shL":(.26,0,1.43,.08), "shR":(-.26,0,1.43,.08),
            "elL":(.38,.03,1.14,.07), "wrL":(.4,-.06,.9,.05), "elR":(-.36,-.05,1.14,.07), "wrR":(-.36,-.18,.98,.05)}
    chop = 20
    if f["anim"] == "walk":
        w = walk_pose(f["p"]); w.pop("elR"); w.pop("wrR"); pose.update(w)
    elif f["anim"] == "attack":
        r = [(-.3,.1,1.7), (-.2,-.5,1.1), (-.1,-.45,.75)][f["i"]]
        pose["wrR"] = (*r, .05); pose["elR"] = (-.38, r[1]/2, 1.35, .07)
        chop = [-60, 80, 120][f["i"]]
    j = body("acougueiro_corpo", flesh, root, pose)
    hands_boots(j, flesh, leather, root)
    prim("primitive_uv_sphere_add", flesh, (0,-.05,1.15), (.3,.27,.32), parent=root)  # barriga
    prim("primitive_cube_add", apron, (0,-.2,.95), (.25,.06,.45), (6,0,0), parent=root)
    for (x,z,r) in [(.08,1.1,.07),(-.1,.85,.09),(.05,.7,.05)]:
        prim("primitive_uv_sphere_add", blood, (x,-.27,z), (r,.01,r*1.4), parent=root)
    chain(steel, (.25,-.15,1.4), (-.2,-.2,1.1), 10, root)
    prim("primitive_uv_sphere_add", flesh, (0,-.01,1.67), (.11,.11,.12), parent=root)
    prim("primitive_uv_sphere_add", leather, (0,-.06,1.66), (.1,.08,.1), parent=root)  # máscara de gás
    for s in (-1,1):
        prim("primitive_cylinder_add", eye, (.045*s,-.14,1.69), (.03,.03,.012), (90,0,0), parent=root)
    along("primitive_cylinder_add", brass, (0,-.13,1.6), (0,-.22,1.52), .045, root, vertices=10)
    pv = pivot(root, j["wrR"]); pv.rotation_euler = (math.radians(chop), 0, 0)
    along("primitive_cylinder_add", leather, (0,0,-.05), (0,0,.15), .025, pv, vertices=8)
    prim("primitive_cube_add", steel, (0,-.1,.33), (.02,.17,.2), parent=pv)
    prim("primitive_cube_add", blood, (.021,-.18,.3), (.002,.06,.12), parent=pv)


def skin_mesh(name, m, parent, j, edges):
    keys = list(j); me = bpy.data.meshes.new(name)
    me.from_pydata([j[k][:3] for k in keys], [(keys.index(a), keys.index(b)) for a, b in edges], [])
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.modifiers.new("skin", 'SKIN')
    for i, k in enumerate(keys):
        o.data.skin_vertices[0].data[i].radius = (j[k][3], j[k][3])
    o.data.skin_vertices[0].data[0].use_root = True
    o.modifiers.new("sub", 'SUBSURF').levels = 2; o.modifiers["sub"].render_levels = 2
    me.materials.append(m)
    for p in me.polygons: p.use_smooth = True
    o.parent = parent
    return {k: Vector(v[:3]) for k, v in j.items()}

def cao_praga(root, f):
    """Cão da Praga: vira-lata esfolado, costelas à mostra, espinhos de osso e olhos ácidos."""
    flesh = mat("carne_esfolada", (.09,.03,.025), .05, .45)
    fur = mat("pelo_sujo", (.03,.028,.024), 0, .95)
    bone = mat("osso_sujo", (.45,.42,.34), 0, .6)
    eye = mat("olho_acido", (.3,.9,.1), emit=(.5,1,.15), strength=8)
    j = {"pelvis":(0,.32,.52,.11), "spine":(0,.05,.56,.12), "chest":(0,-.25,.58,.14), "neck":(0,-.42,.7,.07),
         "head":(0,-.55,.76,.08), "snout":(0,-.74,.7,.045),
         "shL":(.09,-.28,.48,.06), "elL":(.1,-.3,.27,.04), "pawL":(.1,-.33,.04,.035),
         "shR":(-.09,-.28,.48,.06), "elR":(-.1,-.3,.27,.04), "pawR":(-.1,-.33,.04,.035),
         "hipL":(.09,.33,.45,.07), "knL":(.11,.42,.27,.045), "rpL":(.1,.38,.04,.035),
         "hipR":(-.09,.33,.45,.07), "knR":(-.11,.42,.27,.045), "rpR":(-.1,.38,.04,.035),
         "tail":(0,.55,.6,.03), "tail2":(0,.72,.5,.02)}
    if f["anim"] == "walk":
        sn = math.sin(2*math.pi*f["p"])
        for leg, sg in (("pawL",1),("rpR",1),("pawR",-1),("rpL",-1)):
            x, y, z, r = j[leg]; j[leg] = (x, y - .14*sn*sg, z + max(0, math.cos(2*math.pi*f["p"])*sg)*.06, r)
    elif f["anim"] == "attack":
        k = [-.05, .18, .08][f["i"]]
        for n in ("chest","neck","head","snout","shL","shR"):
            x, y, z, r = j[n]; j[n] = (x, y - k, z - k*.5, r)
    edges = [("pelvis","spine"),("spine","chest"),("chest","neck"),("neck","head"),("head","snout"),
             ("chest","shL"),("shL","elL"),("elL","pawL"),("chest","shR"),("shR","elR"),("elR","pawR"),
             ("pelvis","hipL"),("hipL","knL"),("knL","rpL"),("pelvis","hipR"),("hipR","knR"),("knR","rpR"),
             ("pelvis","tail"),("tail","tail2")]
    jj = skin_mesh("cao", flesh, root, j, edges)
    for k in range(5):
        prim("primitive_torus_add", bone, (0,-.2+k*.09,.56), (1,1,1), (0,90,0), parent=root, major_radius=.12, minor_radius=.009)
    for k in range(6):
        along("primitive_cone_add", bone, (0,.25-k*.1,.66), (0,.3-k*.1,.82+.03*(k%2)), 1, root, radius1=.02, radius2=0, vertices=5)
    prim("primitive_uv_sphere_add", fur, (0,.3,.58), (.13,.18,.1), parent=root)
    for s_ in (-1,1):
        prim("primitive_uv_sphere_add", eye, jj["head"] + Vector((.045*s_,-.06,.03)), (.015,.012,.012), parent=root)
        along("primitive_cone_add", bone, jj["snout"] + Vector((.02*s_,-.02,-.02)), jj["snout"] + Vector((.02*s_,-.04,-.08)), 1, root, radius1=.01, radius2=0, vertices=4)
        along("primitive_cone_add", fur, jj["head"] + Vector((.04*s_,.02,.05)), jj["head"] + Vector((.07*s_,.06,.15)), 1, root, radius1=.025, radius2=0, vertices=4)

def automato(root, f):
    """Autômato Enferrujado: sentinela a vapor da Vigília abandonada, martelo-pistão e fornalha nas costas."""
    rust = mat("ferrugem_pesada", (.13,.05,.025), .5, .7)
    iron = mat("ferro_negro", (.04,.04,.045), 1, .45)
    brass = mat("latao", (.35,.22,.08), 1, .4)
    furnace = mat("fornalha", (1,.4,.05), emit=(1,.35,.05), strength=12)
    eye = mat("olho_lampiao", (.6,.85,1), emit=(.6,.85,1), strength=10)
    pose = {"chest":(0,0,1.33,.2), "spine":(0,0,1.12,.18), "shL":(.24,0,1.43,.07), "shR":(-.24,0,1.43,.07)}
    ham = 0
    if f["anim"] == "walk":
        w = walk_pose(f["p"]); w = {k: (v[0], v[1]*.7, v[2], v[3]) for k, v in w.items()}; pose.update(w)
    elif f["anim"] == "attack":
        r = [(-.3,.1,1.6), (-.2,-.5,1.2), (-.12,-.5,.85)][f["i"]]
        pose["wrR"] = (*r, .05); pose["elR"] = (-.36, r[1]/2, 1.3, .06)
        ham = [-80, 30, 75][f["i"]]
    j = body("automato_corpo", iron, root, pose)
    hands_boots(j, iron, rust, root)
    prim("primitive_cylinder_add", rust, (0,0,1.2), (.24,.2,.28), parent=root)       # tronco-caldeira
    for z in (1.0, 1.4): prim("primitive_torus_add", brass, (0,0,z), (1,.85,1), parent=root, major_radius=.24, minor_radius=.02)
    prim("primitive_cylinder_add", iron, (0,.22,1.25), (.16,.16,.3), parent=root)    # fornalha nas costas
    prim("primitive_cube_add", furnace, (0,.38,1.15), (.08,.01,.06), parent=root)
    for s_ in (-1,1): along("primitive_cylinder_add", brass, (.08*s_,.25,1.5), (.1*s_,.28,1.85), .03, root, vertices=8)
    for s_ in (-1,1): prim("primitive_uv_sphere_add", rust, (.25*s_,0,1.47), (.12,.12,.09), parent=root)
    prim("primitive_cylinder_add", iron, (0,-.01,1.66), (.1,.1,.12), parent=root)    # cabeça-lampião
    prim("primitive_cone_add", brass, (0,-.01,1.82), (1,1,1), parent=root, radius1=.13, depth=.1, vertices=8)
    prim("primitive_uv_sphere_add", eye, (0,-.1,1.67), (.04,.02,.04), parent=root)
    pv = pivot(root, j["wrR"]); pv.rotation_euler = (math.radians(ham), 0, 0)
    along("primitive_cylinder_add", brass, (0,0,0), (0,0,.35), .03, pv, vertices=8)
    prim("primitive_cylinder_add", iron, (0,0,.45), (.11,.11,.14), (90,0,0), parent=pv)

KINDS = {"anjo": (anjo, 1.0, (.9,.3,.25)), "humano": (humano, 1.0, (1,.45,.2)),
         "carnical": (carnical, 1.0, (.4,.8,.2)), "flagelado": (flagelado, 1.0, (.9,.2,.15)),
         "acougueiro": (acougueiro, 1.3, (1,.4,.1)),
         "cao_praga": (cao_praga, 1.0, (.4,.8,.2)), "automato": (automato, 1.0, (1,.45,.15))}
FRAMES = [{"anim":"idle","i":0}] + [{"anim":"walk","i":i,"p":i/4} for i in range(4)] \
       + [{"anim":"attack","i":i} for i in range(3)] + [{"anim":"death","i":i} for i in range(2)]

def setup(rim):
    sc = bpy.context.scene
    for o in list(bpy.data.objects): bpy.data.objects.remove(o)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam)
    cam.data.type = 'ORTHO'; cam.data.ortho_scale = 2.5 * KINDS[kind][1]; cam.data.clip_end = 200
    e, a, d = math.radians(35), math.radians(45), 40; t = Vector((0,0,.95*KINDS[kind][1]))
    cam.location = t + Vector((d*math.cos(e)*math.sin(a), -d*math.cos(e)*math.cos(a), d*math.sin(e)))
    cam.rotation_euler = (t - cam.location).to_track_quat('-Z','Y').to_euler(); sc.camera = cam
    for name, rgb, en, rot in [("key",(.9,.92,1),3.2,(50,0,-35)), ("rim",rim,2.2,(-55,0,165)), ("fill",(.3,.35,.5),.5,(70,0,110))]:
        l = bpy.data.objects.new(name, bpy.data.lights.new(name,'SUN')); sc.collection.objects.link(l)
        l.data.color = rgb; l.data.energy = en; l.data.angle = .1; l.rotation_euler = [math.radians(r) for r in rot]

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.world = bpy.data.worlds.new("w"); sc.world.color = (.01,.01,.012)
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = SAMPLES
sc.cycles.use_denoising = False; sc.cycles.max_bounces = 4
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'Medium High Contrast'
sc.render.film_transparent = True
sc.render.resolution_x = sc.render.resolution_y = int(px*2*KINDS[kind][1])
os.makedirs(out, exist_ok=True)
build, scale, rim = KINDS[kind]
for f in FRAMES:
    tag = f"{f['anim']}_{f['i']}"
    if only and f["anim"] not in only: continue
    setup(rim)
    dirn = M.make_root("dir")           # gira para as 8 direções
    tilt = M.make_root("tilt"); tilt.parent = dirn
    root = M.make_root("root"); root.parent = tilt; root.scale = (scale,)*3
    if f["anim"] == "walk":
        root.location.z = .025*abs(math.cos(2*math.pi*f["p"]))
    if f["anim"] == "death":            # cai de costas
        if kind == "cao_praga":           # cai de lado
            tilt.rotation_euler = (0, math.radians(45 if f["i"] == 0 else 85), 0); tilt.location = (0, 0, .05)
        else:
            tilt.rotation_euler = (math.radians(-45 if f["i"] == 0 else -88), 0, 0)
            tilt.location = (0, (-.5 if f["i"] == 0 else -.9)*scale, .08)
        dirn.location = (0, 0, 0)
    build(root, f if f["anim"] != "death" else {"anim":"idle","i":0})
    for d in range(8):
        dirn.rotation_euler = (0, 0, math.radians(d*45))
        sc.render.filepath = f"{out}/{tag}_d{d}.png"; bpy.ops.render.render(write_still=True)
print("OK", kind)
