# Moradores da Vela (NPCs da cúpula): sprites próprios, um por ficha de design/missoes/dados/npcs.json (campo modelo).
# Usam o mesmo rig humanoide das classes, com silhueta e acessórios próprios. Só idle e andar (NPC não ataca).
import bpy, bmesh, math, random
from mathutils import Vector
from rig import *
from classes import body_parts, bone_frame, L, pauldron
from classes2 import curve_tube, bezier, head_base, mohawk
from anims import walk_legs

def _arms_swing(t, amp=18):
    s = math.sin(t)
    return {"upper_arm.L": {"x": amp*s}, "upper_arm.R": {"x": -amp*s}, "forearm.L": {"bend": -12}, "forearm.R": {"bend": -12}}

def npc_anims(arm):
    idle = []
    for i in range(4):
        b = math.sin(i/4*2*math.pi)
        idle.append(merge(ARMS_DOWN, {"chest": {"x": -1.2*b}, "head": {"x": 1.2*b}, "root": (0, 0, -.005*(1+b))}))
    walk = []
    for i in range(8):
        t = i/8*2*math.pi
        walk.append(merge(ARMS_DOWN, walk_legs(t, 20), _arms_swing(t, 14), {"head": {"z": 2*math.sin(t)}}))
    return {"idle": make_action(arm, "idle", idle), "walk": make_action(arm, "walk", walk)}

# ---- 1. Nhá Zulmira: faroleira cega, avental de couro, óculos de solda na testa, descalça
def zulmira():
    dress = mat("vestido_cinza", (.22,.22,.21), 0, .8, dirt=.6, grime=.8)
    leather = mat("avental_couro_queimado", (.12,.06,.03), 0, .55, dirt=.6, grime=.9)
    brass = mat("latao_oculos", (.55,.3,.08), 1, .35, dirt=.5, grime=.3)
    lens = mat("lente_rachada", (.2,.4,.35), .3, .1, dirt=.8)
    skin = mat("pele_velha", (.42,.33,.27), 0, .6, dirt=.5, grime=.4)
    white = mat("olho_cego", (.85,.85,.82), 0, .3, dirt=.4)
    hair = mat("cabelo_grisalho", (.3,.29,.28), 0, .7, dirt=.5)
    arm = make_armature("npc_zulmira")
    parts = body_parts(arm, dress, leather, dress, {"L": skin, "R": skin}, m_skin=skin, cuff=.05,
                       boot_top=.1, legs_r=.9, top_r=.9, sleeve_r=.9)
    sk = skirt("vestido", dress, [(.9,.2,.16,0), (.6,.23,.19,.01), (.25,.25,.21,.02), (.05,.26,.22,.02)],
               open_front=0, seg=48, jag=.05, seed=3, folds=6, famp=.04)
    bind(sk, arm, ["hips","thigh.L","thigh.R"], power=3); parts.append(sk)
    ap = skirt("avental_zulmira", leather, [(1.0,.14,.1,-.02), (.42,.16,.12,-.02)], open_front=0, seg=24, thick=.01, seed=2)
    bind(ap, arm, ["hips","thigh.L","thigh.R"], power=3); parts.append(ap)
    cl = [prim("primitive_cube_add", leather, (0,-.15,1.0), (.12,.012,.2)),
          prim("primitive_cube_add", brass, (.1,-.16,.86), (.03,.01,.025)),
          prim("primitive_cylinder_add", leather, (-.13,-.07,.9), (.024,.024,.06), vertices=8)]
    rigid(cl, arm, "hips")
    hd = [prim("primitive_uv_sphere_add", skin, (0,-.01,1.67), (.075,.085,.1), segments=14, ring_count=8),
          prim("primitive_uv_sphere_add", white, (-.034,-.09,1.685), (.018,.008,.014)),
          prim("primitive_uv_sphere_add", white, (.034,-.09,1.685), (.018,.008,.014)),
          prim("primitive_uv_sphere_add", hair, (0,.03,1.72), (.085,.09,.075), segments=12, ring_count=8)]
    for s in (1,-1):
        hd.append(prim("primitive_torus_add", brass, (.045*s,-.1,1.7), (1,1,1), major_radius=.03, minor_radius=.006, major_segments=10, minor_segments=4))
        hd.append(prim("primitive_cylinder_add", lens, (.045*s,-.105,1.7), (.025,.01,.025), (90,0,0), vertices=10))
    hd.append(prim("primitive_torus_add", brass, (0,-.01,1.8), (1,1,1), (0,0,0), major_radius=.07, minor_radius=.006, major_segments=14, minor_segments=4))
    rigid(hd, arm, "head")
    fr = bone_frame("hand.R"); o, ax, up, sd = fr
    chave = [along("primitive_cylinder_add", brass, L(fr, .02), L(fr, .4), .01, vertices=6),
             prim("primitive_torus_add", brass, L(fr, .4), (1,1,1), major_radius=.03, minor_radius=.008)]
    rigid(chave, arm, "hand.R")
    info = {"rim": (.5, .8, 1), "anim": "npc"}
    return arm, info

# ---- 2. Mestre Bento Catraca: gordo, quepe de condutor com placa "7", sobretudo azul, catraca nas costas
def bento():
    navy = mat("azul_companhia", (.06,.11,.22), 0, .65, dirt=.5, grime=.7)
    brass = mat("latao_botao", (.55,.3,.08), 1, .35, dirt=.5, grime=.3)
    iron = mat("ferro_catraca", (.12,.12,.12), 1, .45, dirt=.6, grime=.3)
    skin = mat("pele_rosada", (.42,.28,.2), 0, .6, dirt=.5, grime=.3)
    bigode = mat("bigode_branco", (.7,.68,.64), 0, .8, dirt=.4)
    boot = mat("bota_areia", (.06,.045,.03), 0, .55, dirt=.7, grime=.8)
    pants = mat("calca_companhia", (.05,.07,.13), 0, .8, dirt=.5)
    arm = make_armature("npc_bento")
    parts = body_parts(arm, pants, boot, navy, {"L": skin, "R": skin}, m_skin=skin, cuff=.07, sleeve_r=1.25, top_r=1.45,
                       legs_r=1.3, boot_top=.3, buckle=brass)
    sk = skirt("sobretudo", navy, [(1.02,.2,.2,0), (.8,.25,.25,.01), (.5,.29,.28,.02), (.25,.3,.29,.02)],
               open_front=.25, seg=48, folds=4, famp=.03, seed=11)
    bind(sk, arm, ["hips","spine","thigh.L","thigh.R"], power=3); parts.append(sk)
    bt = []
    for k in range(5):
        bt.append(prim("primitive_uv_sphere_add", brass, (-.12 + .06*k, -.262, 1.31 - .03*(k%2)), (.012,)*3, segments=6, ring_count=4))
    rigid(bt, arm, "chest")
    catraca = []
    for z in (1.0, 1.2, 1.4):
        catraca.append(prim("primitive_torus_add", iron, (0,.3,z), (1,1,1), major_radius=.14, minor_radius=.012, major_segments=20, minor_segments=5))
    for a in range(6):
        ang = math.radians(a*60)
        catraca.append(along("primitive_cylinder_add", iron, (.14*math.cos(ang), .3, 1.0), (.14*math.cos(ang), .3, 1.4), .01, vertices=6))
    catraca.append(along("primitive_cylinder_add", iron, (-.14,.26,1.2), (-.14,.1,1.2), .012, vertices=6))
    rigid(catraca, arm, "chest")
    hd = [head_base(skin, (.09,.1,.095), z=1.66),
          prim("primitive_uv_sphere_add", bigode, (0,-.11,1.63), (.05,.02,.02))]
    hd.append(prim("primitive_cylinder_add", navy, (0,-.005,1.79), (.1,.1,.04), vertices=16))
    hd.append(prim("primitive_cube_add", navy, (0,-.1,1.79), (.1,.04,.012)))
    hd.append(prim("primitive_cube_add", brass, (0,-.125,1.79), (.035,.006,.035)))
    hd.append(along("primitive_cylinder_add", brass, (0,-.12,1.56), (0,-.14,1.52), .01, vertices=6))
    rigid(hd, arm, "head")
    info = {"rim": (.5, .8, 1), "anim": "npc"}
    return arm, info

# ---- 3. Dona Celina: mãos de vidro verde translúcido com ossos visíveis, lenço vermelho, cana de sopro no ombro
def celina():
    lona = mat("lona_macacao", (.1,.09,.08), 0, .8, dirt=.6, grime=.9)
    glass = mat("vidro_verde", (.2,.85,.5), 0, .05, emit=(.1,.6,.3), strength=1.2)
    bone = mat("osso_vidro", (.7,.68,.6), 0, .4, dirt=.2)
    skin = mat("pele_cansada", (.4,.29,.22), 0, .6, dirt=.5, grime=.3)
    lenco = mat("lenco_vermelho", (.4,.07,.05), 0, .8, dirt=.6, grime=.4)
    leather = mat("avental_couro_celina", (.13,.07,.04), 0, .55, dirt=.6, grime=.8)
    cana = mat("cana_sopro", (.25,.4,.3), 0, .2, dirt=.4)
    boot = mat("bota_operaria", (.05,.04,.03), 0, .55, dirt=.7, grime=.7)
    arm = make_armature("npc_celina")
    parts = body_parts(arm, lona, boot, lona, {"L": glass, "R": glass}, m_skin=skin, cuff=.05, m_arms={"L": glass, "R": glass},
                       arm_scale={"L": 1.0, "R": 1.0}, glove_scale={"L": 1.15, "R": 1.15}, legs_r=1.02)
    ap = skirt("avental_celina", leather, [(.98,.15,.11,-.02), (.5,.16,.12,-.02)], open_front=0, seg=24, thick=.01, seed=5)
    bind(ap, arm, ["hips","spine","thigh.L","thigh.R"], power=3); parts.append(ap)
    for n in "LR":
        o_, ax_, up_, sd_ = bone_frame(f"forearm.{n}"); ln_ = (P(f"forearm.{n}",1)-P(f"forearm.{n}")).length
        bones = [curve_tube(bone, [o_ + ax_*ln_*t for t in (.15,.5,.85)], .011, .008, verts=5)]
        parts.append(rigid(bones[0], arm, f"forearm.{n}"))
    hd = [head_base(skin, (.078,.088,.1)),
          prim("primitive_torus_add", lenco, (0,.005,1.72), (1,1.02,1), major_radius=.088, minor_radius=.016, major_segments=16, minor_segments=5)]
    rigid(hd, arm, "head")
    fr = bone_frame("hand.L"); o, ax, up, sd = fr
    rigid([along("primitive_cylinder_add", cana, L(fr, .0), L(fr, .9), .016, vertices=8)], arm, "hand.L")
    info = {"rim": (.5, 1, .6), "anim": "npc"}
    return arm, info

# ---- 4. Cabo Damião Pé-de-Chumbo: capacete com vela pintada, fardas verdes, botas de chumbo, fuzil com baioneta
def damiao():
    green = mat("farda_verde", (.1,.16,.09), 0, .75, dirt=.6, grime=.7)
    leather = mat("remendo_couro", (.1,.06,.03), 0, .55, dirt=.6, grime=.9)
    steel = mat("aco_capacete", (.15,.16,.17), .7, .45, dirt=.5, grime=.5)
    lead = mat("chumbo_bota", (.22,.22,.24), .4, .35, dirt=.6, grime=.5)
    wood = mat("coronha_fuzil", (.18,.09,.04), 0, .5, dirt=.6, grime=.4)
    skin = mat("pele_magra", (.38,.25,.18), 0, .6, dirt=.5, grime=.4)
    wax = mat("cera_vela", (.9,.9,.85), 0, .4, dirt=.2)
    iron = mat("fuzil_ferro", (.1,.1,.1), 1, .45, dirt=.6, grime=.4)
    arm = make_armature("npc_damiao")
    parts = body_parts(arm, green, lead, green, {"L": skin, "R": skin}, m_skin=skin, cuff=.05, boot_top=.55, legs_r=.92,
                       top_r=.9, sleeve_r=.95, buckle=steel)
    for n in "LR":
        o_, ax_, up_, sd_ = bone_frame(f"shin.{n}")
        bt = [prim("primitive_cube_add", lead, P(f"shin.{n}") + Vector((0, -.02, -.22)), (.1, .12, .14))]
        rigid(bt, arm, f"foot.{n}")
    fz = []
    fr = bone_frame("hand.R"); o, ax, up, sd = fr
    fz.append(along("primitive_cylinder_add", iron, L(fr, .6, 0, 0), L(fr, -.2, 0, 0), .014, vertices=8))
    fz.append(along("primitive_cone_add", iron, L(fr, .6, 0, 0), L(fr, .9, 0, 0), 1, radius1=.012, radius2=.001, vertices=6))
    fz.append(along("primitive_cube_add", wood, L(fr, -.2, 0, 0), L(fr, -.36, 0, -.04), .02))
    rigid(fz, arm, "hand.R")
    hd = [head_base(skin, (.078,.09,.1), z=1.66),
          prim("primitive_uv_sphere_add", steel, (0,.0,1.74), (.105,.11,.075), segments=14, ring_count=8),
          prim("primitive_cylinder_add", steel, (0,.0,1.7), (.11,.11,.03), vertices=16)]
    hd.append(prim("primitive_uv_sphere_add", wax, (0,-.105,1.73), (.035,.005,.04), segments=10, ring_count=6))
    hd.append(prim("primitive_cube_add", wax, (0,-.106,1.7), (.01,.004,.02)))
    rigid(hd, arm, "head")
    info = {"rim": (.6, .85, 1), "anim": "npc"}
    return arm, info

# ---- 5. Lindalva, parteira: tranças com fios de cobre, avental branco acinzentado, bolsa de médico, caderno no cordão
def lindalva():
    white = mat("avental_branco", (.5,.5,.46), 0, .75, dirt=.5, grime=.5)
    dress = mat("vestido_marrom", (.14,.09,.06), 0, .8, dirt=.6, grime=.5)
    leather = mat("bolsa_couro", (.12,.06,.03), 0, .5, dirt=.6, grime=.8)
    copper = mat("cobre_trança", (.5,.25,.1), 1, .35, dirt=.5, grime=.2)
    skin = mat("pele_escura", (.2,.12,.08), 0, .55, dirt=.4, grime=.2)
    hair = mat("cabelo_trança", (.03,.02,.02), 0, .6, dirt=.6)
    boot = mat("bota_enfermeira", (.05,.04,.03), 0, .55, dirt=.7, grime=.5)
    paper = mat("caderno", (.5,.45,.35), 0, .9, dirt=.5, grime=.5)
    rubber = mat("mascara_gas", (.04,.035,.03), 0, .6, dirt=.5)
    arm = make_armature("npc_lindalva")
    parts = body_parts(arm, dress, boot, dress, {"L": skin, "R": skin}, m_skin=skin, cuff=.05, legs_r=1.02, top_r=1.04, sleeve_r=1.02)
    sk = skirt("avental_lindalva", white, [(1.0,.19,.16,0), (.55,.22,.19,.01), (.15,.24,.2,.02)], open_front=0, seg=40, jag=.03, seed=7, folds=5, famp=.03)
    bind(sk, arm, ["hips","thigh.L","thigh.R"], power=3); parts.append(sk)
    bag = [along("primitive_cube_add", leather, (.2,.22,1.27), (.02,.2,1.14), .02), prim("primitive_cube_add", leather, (.13,.17,1.18), (.07,.03,.06))]
    rigid(bag, arm, "chest")
    caderno = [prim("primitive_cube_add", paper, (0,-.2,1.22), (.035,.005,.045)), along("primitive_cylinder_add", copper, (0,-.18,1.36), (0,-.2,1.27), .004, vertices=4)]
    rigid(caderno, arm, "chest")
    mask = [prim("primitive_cylinder_add", rubber, (-.2,.0,1.04), (.05,.05,.07), vertices=12)]
    rigid(mask, arm, "hips")
    hd = [head_base(skin, (.082,.093,.102), z=1.67)]
    for k in range(6):   # tranças caindo atrás da cabeça, com fio de cobre enrolado em cada uma
        a = math.radians(-50 + k*20)
        x = .05*math.cos(a); y = .05 + .05*math.sin(a)
        trança = [Vector((x, y, 1.72)), Vector((x*1.3, y + .03, 1.6)), Vector((x*1.2, y + .05, 1.45))]
        hd += curve_tube(hair, trança, .016, .009, verts=5)
        hd.append(prim("primitive_torus_add", copper, trança[1], (1,1,1), major_radius=.013, minor_radius=.004, major_segments=8, minor_segments=4))
    hd.append(prim("primitive_torus_add", copper, (0,.005,1.72), (1,1,1), major_radius=.086, minor_radius=.008, major_segments=16, minor_segments=5))
    rigid(hd, arm, "head")
    info = {"rim": (.6, .9, 1), "anim": "npc"}
    return arm, info

# ---- 6. Ferrolho, moleque de recados: criança, terceiro braço pequeno nas costelas, óculos de aviador, boné de jornaleiro
def ferrolho():
    shirt = mat("camisa_listrada", (.24,.1,.08), 0, .75, dirt=.6, grime=.7)
    pants = mat("calcao_remendado", (.1,.09,.08), 0, .8, dirt=.6, grime=.7)
    skin = mat("pele_mirrada", (.36,.22,.15), 0, .55, dirt=.6, grime=.5)
    cable = mat("cabo_aco", (.3,.3,.3), 1, .4, dirt=.5, grime=.4)
    boot = mat("botina_gasta", (.05,.04,.03), 0, .55, dirt=.7, grime=.8)
    glass = mat("oculos_aviador", (.2,.3,.4), .2, .1, dirt=.5)
    brass = mat("latao_ferrolho", (.5,.27,.07), 1, .4, dirt=.5, grime=.3)
    cap = mat("bone_jornaleiro", (.2,.16,.1), 0, .8, dirt=.6, grime=.6)
    sack = mat("saco_sucata", (.12,.09,.06), 0, .9, dirt=.6, grime=.5)
    arm = make_armature("npc_ferrolho")
    parts = body_parts(arm, pants, boot, shirt, {"L": skin, "R": skin}, m_skin=skin, cuff=.04, sleeve_r=.95, top_r=.95,
                       legs_r=.92, boot_top=.25)
    rigid([prim("primitive_uv_sphere_add", sack, (-.1,.14,1.26), (.15,.1,.15), segments=10, ring_count=6)], arm, "chest")
    third = curve_tube(skin, [Vector((-.14,-.02,1.1)), Vector((-.2,-.06,1.02)), Vector((-.2,-.1,.96))], .024, .014, verts=6)
    third.append(prim("primitive_uv_sphere_add", skin, (-.2,-.1,.94), (.02,.02,.02), segments=6, ring_count=4))
    rigid(third, arm, "chest")
    rigid([along("primitive_cylinder_add", cable, (.0, -.04, 1.22), (.0, -.02, 1.02), .006, vertices=4)], arm, "chest")
    hd = [head_base(skin, (.07,.08,.088), z=1.5),
          prim("primitive_cylinder_add", cap, (0,.0,1.6), (.08,.08,.03), vertices=16)]
    hd.append(prim("primitive_cube_add", cap, (0,-.085,1.6), (.08,.05,.01)))
    for s in (1,-1):
        hd.append(prim("primitive_torus_add", glass, (.035*s,-.075,1.5), (1,1,1), major_radius=.032, minor_radius=.006, major_segments=10, minor_segments=4))
    rigid(hd, arm, "head")
    rigid([along("primitive_cylinder_add", brass, (0,.05,1.35), (0,-.02,1.3), .004, vertices=4)], arm, "chest")
    info = {"rim": (.6, .9, 1), "anim": "npc"}
    return arm, info

# ---- 7. Saulo, o Penitente (narrador do coliseu): ex-demônio convertido à luz. Careca, pele branca, túnica de monge
# com cordão, chifres quebrados em cotos e halo de luz dourada. Corpo largo e calmo, estilo Netero.
def saulo():
    robe = mat("tunica_penitente", (.78,.75,.68), 0, .75, dirt=.4, grime=.35)
    rope = mat("cordao_penitente", (.4,.3,.18), 0, .8, dirt=.5, grime=.3)
    skin = mat("pele_branca_luz", (.92,.9,.86), 0, .4, dirt=.15, grime=.05)
    horn = mat("chifre_quebrado", (.75,.62,.42), 0, .45, dirt=.2, grime=.1)
    gold = mat("halo_dourado", (1,.85,.45), emit=(1,.82,.4), strength=12)
    sandal = mat("sandalia_penitente", (.3,.22,.14), 0, .7, dirt=.5, grime=.4)
    arm = make_armature("npc_saulo")
    parts = body_parts(arm, robe, sandal, robe, {"L": skin, "R": skin}, m_skin=skin, cuff=.08,
                       boot_top=.04, legs_r=1.25, top_r=1.55, sleeve_r=1.6)
    sk = skirt("tunica", robe, [(1.12,.2,.19,0), (.92,.22,.21,.01), (.6,.23,.22,.02), (.3,.24,.23,.02)],
               open_front=0, seg=48, folds=6, famp=.035, seed=21)
    bind(sk, arm, ["hips","spine","thigh.L","thigh.R"], power=3); parts.append(sk)
    cordao = curve_tube(rope, [Vector((-.2,-.26,1.2)), Vector((0,-.3,1.18)), Vector((.2,-.26,1.2))], .018, .016, verts=8)
    cordao += [along("primitive_cylinder_add", rope, (.18,-.28,1.19), (.26,-.36,.98), .016, vertices=8)]
    rigid(cordao, arm, "hips")
    hd = [head_base(skin, (.13,.135,.13), z=1.68),
          prim("primitive_uv_sphere_add", skin, (0,-.02,1.8), (.12,.13,.07), segments=14, ring_count=8)]
    for s in (1,-1):
        hd.append(along("primitive_cone_add", horn, (.1*s,.0,1.78), (.2*s,-.01,1.92), 1, radius1=.04, radius2=.008, vertices=7))
    hd.append(prim("primitive_uv_sphere_add", gold, (0,.02,1.77), (.02,.02,.02), segments=8, ring_count=5))
    rigid(hd, arm, "head")
    halo = [prim("primitive_torus_add", gold, (0,.09,1.95), (1,1,1), (90,0,0), major_radius=.16, minor_radius=.022, major_segments=28, minor_segments=8)]
    halo_o = rigid(halo, arm, "head"); halo_o.name = "halo"
    info = {"rim": (1, .9, .6), "anim": "npc"}
    return arm, info

# ---- 8. Pedro, o Exilado (ascensão de classe, nível 50): homenagem do Jefin ao Pedro. Sobretudo costurado de dois,
# metade lona azul-noite da Vigília e metade rubro-negro do Coro; barba grisalha trançada com anéis de latão,
# cajado-lampião com lente de farol e bolsa de livros. Exilado pelos dois lados, ensina os dois.
def _duas_metades(o, m_left, m_right):
    """Pinta a metade esquerda (x > 0, lado esquerdo do personagem) com m_left e a direita com m_right."""
    me = o.data; me.materials.clear(); me.materials.append(m_left); me.materials.append(m_right)
    for p in me.polygons: p.material_index = 0 if p.center.x > 0 else 1

def pedro_exilado():
    vig = mat("lona_azul_noite_exilado", (.035,.055,.085), 0, .8, dirt=.55, grime=.8)
    coro = mat("pano_rubro_coro", (.1,.022,.02), 0, .75, dirt=.6, grime=.9)
    seam = mat("costura_grossa", (.32,.27,.19), 0, .8, dirt=.6, grime=.5)
    trousers = mat("calca_lona", (.09,.075,.06), 0, .8, dirt=.6, grime=.9)
    boots = mat("bota_gasta", (.05,.035,.025), 0, .55, dirt=.6, grime=.6)
    skin = mat("pele_curtida", (.36,.23,.16), 0, .55, dirt=.6, grime=.3)
    beard = mat("barba_grisalha", (.3,.29,.27), 0, .85, dirt=.55, grime=.3)
    brass = mat("latao_aneis", (.55,.3,.08), 1, .35, dirt=.5, grime=.3)
    wood = mat("cajado_madeira", (.15,.08,.04), 0, .6, dirt=.6, grime=.4)
    leather = mat("bolsa_couro", (.13,.07,.035), 0, .55, dirt=.6, grime=.8)
    paper = mat("livro_velho", (.42,.36,.25), 0, .8, dirt=.6, grime=.4)
    lamp = mat("luz_lampiao", (1,.75,.4), emit=(1,.7,.35), strength=8)
    glass = mat("lente_farol", (.5,.45,.35), .2, .05, dirt=.4)
    arm = make_armature("npc_pedro_exilado")
    parts = body_parts(arm, trousers, boots, vig, {"L": skin, "R": skin}, m_skin=skin, cuff=.06, boot_top=.4, legs_r=1.0,
                       top_r=1.06, sleeve_r=1.1, buckle=brass)
    for o_ in [o_ for o_ in bpy.data.objects if o_.name.startswith("npc_pedro_exilado_") and o_.type == 'MESH']:
        if any(k in o_.name for k in ("chest", "spine", "upper_arm", "forearm")): _duas_metades(o_, vig, coro)
    # sobretudo longo de dois panos, aberto embaixo, com a costura grossa subindo pelo meio
    rings = [(1.5,.16,.13,0), (1.3,.215,.16,.0), (1.05,.2,.155,.005), (.8,.24,.18,.015), (.55,.27,.2,.025), (.3,.3,.225,.035), (.12,.32,.24,.04)]
    sk = skirt("sobretudo_exilado", vig, rings, open_front=.32, jag=.07, seed=21, folds=9, famp=.07)
    _duas_metades(sk, vig, coro); bind(sk, arm, ["chest", "spine", "hips", "thigh.L", "thigh.R"], power=3); parts.append(sk)
    ch = []
    for k in range(13):   # costura de corda no meio das costas e pontos de linha cruzados
        z = 1.5 - k*.1; y = .14 + .02*min(k, 4)/4 + .03*max(0, k - 4)/8
        ch.append(along("primitive_cylinder_add", seam, (0, y, z), (0, y + .004, z - .1), .012, vertices=6))
        ch.append(along("primitive_cube_add", seam, (-.022, y, z - .05), (.022, y + .004, z - .03), .004))
    for s_ in (1, -1):   # gola alta e alamares de latão
        ch.append(prim("primitive_uv_sphere_add", brass, (.06*s_, -.15, 1.36), (.012,.012,.012)))
        ch.append(prim("primitive_uv_sphere_add", brass, (.06*s_, -.155, 1.22), (.012,.012,.012)))
    gola = skirt("gola_exilado", vig, [(1.62,.09,.09,0), (1.5,.14,.12,0)], open_front=.5, thick=.012)
    _duas_metades(gola, vig, coro); ch.append(gola)
    # bolsa de livros no quadril, presa por correia cruzada
    ch.append(along("primitive_cube_add", leather, (.15,-.13,1.48), (-.19,-.11,.98), .012))
    parts.append(rigid(ch, arm, "chest"))
    hp = [prim("primitive_cube_add", leather, (-.22,-.02,.92), (.05,.11,.09)),
          prim("primitive_cube_add", paper, (-.22,-.02,1.02), (.035,.08,.012)),
          prim("primitive_cube_add", paper, (-.22,.0,1.035), (.03,.07,.01))]
    hp.append(prim("primitive_torus_add", brass, (-.27,-.02,.92), (1,1,1), (0,90,0), major_radius=.03, minor_radius=.005))
    parts.append(rigid(hp, arm, "hips"))
    # cabeça: cabelo grisalho curto, barba longa trançada com anéis de latão
    hd = [head_base(skin, (.08,.09,.1), z=1.66), prim("primitive_uv_sphere_add", beard, (0,.015,1.705), (.081,.085,.06))]
    hd += [prim("primitive_uv_sphere_add", beard, (0,-.05,1.6), (.075,.06,.06))]
    pts = [Vector((0,-.07,1.58)), Vector((0,-.1,1.5)), Vector((.005,-.11,1.42)), Vector((0,-.1,1.35))]
    hd += curve_tube(beard, pts, .04, .014, 8)
    for t in (.45, .75): hd.append(prim("primitive_torus_add", brass, pts[1].lerp(pts[3], t), (1,1,1), (90,0,0), major_radius=.022, minor_radius=.006))
    for s_ in (1, -1):
        hd.append(prim("primitive_uv_sphere_add", beard, (.035*s_,-.083,1.695), (.024,.008,.008)))   # sobrancelhas grossas
        hd.append(prim("primitive_uv_sphere_add", boots, (.033*s_,-.082,1.675), (.011,.005,.007)))   # olhos fundos
    hd.append(prim("primitive_cone_add", skin, (0,-.098,1.64), (1,1,1), (100,0,0), radius1=.016, radius2=.004, depth=.04, vertices=6))
    hd.append(prim("primitive_uv_sphere_add", beard, (0,-.07,1.565), (.085,.05,.07)))   # barba cheia
    # chapéu de peregrino de aba larga e caída, com fita de latão
    felt = mat("feltro_exilado", (.055,.042,.032), 0, .85, dirt=.6, grime=.4)
    hd.append(skirt("chapeu_exilado_copa", felt, [(1.74,.098,.1,0), (1.82,.09,.092,.0), (1.87,.07,.072,.0), (1.88,.0,.0,0)], open_front=0, thick=.01))
    hd.append(skirt("chapeu_exilado_aba", felt, [(1.75,.098,.1,0), (1.72,.2,.2,0), (1.68,.25,.24,0)], open_front=0, thick=.012, folds=6, famp=.06, seed=4))
    hd.append(prim("primitive_torus_add", brass, (0,0,1.765), (1,1.02,1), major_radius=.099, minor_radius=.008))
    parts.append(rigid(hd, arm, "head"))
    # cajado-lampião: madeira gasta, gaiola de latão com a lente de farol e a chama (único brilho)
    fr = bone_frame("hand.R"); o, ax, up, sd = fr; g = L(fr, .04)
    top = g - ax*.95; bot = g + ax*.9
    st = [along("primitive_cylinder_add", wood, bot, top, .02, vertices=8)]
    for t in (.3, .6): st.append(prim("primitive_torus_add", brass, bot.lerp(top, t), (1,1,1), major_radius=.025, minor_radius=.005))
    c = top - ax*.1
    st.append(prim("primitive_uv_sphere_add", lamp, c, (.04,.04,.05)))
    st.append(prim("primitive_uv_sphere_add", glass, c + Vector((0,-.04,0)), (.04,.012,.04)))
    for k in range(6):
        a = 2*math.pi*k/6
        st.append(along("primitive_cylinder_add", brass, c + Vector((math.cos(a)*.055, math.sin(a)*.055, -.07)), c + Vector((math.cos(a)*.055, math.sin(a)*.055, .07)), .005, vertices=4))
    for z in (-.075, .075): st.append(prim("primitive_torus_add", brass, c + Vector((0,0,z)), (1,1,1), major_radius=.058, minor_radius=.008))
    st.append(prim("primitive_cone_add", brass, c + Vector((0,0,.11)), (1,1,1), radius1=.06, radius2=.01, depth=.06, vertices=8))
    parts.append(rigid(st, arm, "hand.R"))
    info = {"rim": (.95, .78, .55), "anim": "npc"}
    return arm, info
