# Modelos do kit de ambiente. Cada função monta o objeto em volta da origem
# (centro da base no chão) e devolve um dict com metadados.
# Escala: metros. Personagem tem 1,8 m. Tile = K.T (0,7071 m).
import bpy, math, random
from mathutils import Vector
import kit as K
from kit import prism, box, cyl, sphere, along, torus, displace, crumble, flame, candle, chain, point
T = K.T
REG = {}
def asset(cat, fp=(1, 1), dungeon=False, walls=False, samples=32, bury=0.0, name=None, base=None):
    """bury: metros enterrados na areia (o chão do kit esconde o que fica abaixo)."""
    def deco(fn):
        REG[name or fn.__name__] = dict(fn=fn, cat=cat, fp=fp, dungeon=dungeon, walls=walls, samples=samples, bury=bury); return fn
    return deco

# ---------------------------------------------------------------- materiais usados
def M():
    return dict(
        brick=K.mat_brick("tijolo", ("wall", T), 0.0),
        brick_p=K.mat_brick("tijolo_reboco", ("wall", T), 1.0, plaster=.85),
        stone=K.mat_stone("pedra", scale=1.5, moss=.6),
        stone_d=K.mat_stone("pedra_cripta", (.07, .07, .072), (.028, .028, .03), 2.2, .3, ("wall", T), 2.8, 3.0),
        dark_stone=K.mat_stone("pedra_escura", (.05, .048, .046), (.02, .019, .018), 2.5, .4),
        wood=K.mat_wood("madeira"), wood_d=K.mat_wood("madeira_escura", (.04, .028, .02)),
        iron=K.mat_metal("ferro", rust=.45), rust=K.mat_metal("ferrugem", (.06, .04, .03), .9, 2.0),
        tin=K.mat_metal("zinco", (.12, .12, .115), .55, 4.0, .45), brass=K.mat_brass(),
        bone=K.mat_bone(), cloth=K.mat_cloth("lona"), red_cloth=K.mat_cloth("pano_vermelho", (.12, .015, .012), 3.0),
        sack=K.mat_cloth("saco", (.11, .09, .06), 5.0), porcelain=K.mat_porcelain(),
        blood=K.mat_blood(), glass=K.mat_stained_glass(), meat=K.mat_solid("carne", (.13, .025, .02), 0, .35),
        coal=K.mat_solid("carvao", (.015, .013, .012), 0, .9),
    )

def rnd(seed): return random.Random(seed)

# ================================================================ PAREDES (2 orientações)
@asset("paredes", walls=True)
def muro_tijolo(m, seed=1):
    r = rnd(seed); L = T
    box(m["brick"], (0, 0, 1.2), (L, .3, 2.4), bevel=.004)
    box(m["dark_stone"], (0, 0, .09), (L+.02, .36, .18), bevel=.01)                  # embasamento
    box(m["dark_stone"], (0, 0, 2.44), (L+.02, .36, .08), bevel=.01)                 # capa
    return {}

@asset("paredes", walls=True)
def muro_tijolo_quebrado(m, seed=2):
    r = rnd(seed); L = T
    prof = [r.uniform(.6, 2.2) for _ in range(5)]
    n = 5
    for i in range(n):
        h = prof[i]; w = L/n
        o = box(m["brick"], (-L/2 + w*(i+.5), 0, h/2), (w+.002, .3, h), bevel=.004)
    for i in range(n):  # topo quebrado irregular
        h = prof[i]
        o = box(m["brick"], (-L/2 + L/n*(i+.5) + r.uniform(-.03, .03), r.uniform(-.03, .03), h+.05), (L/n*.8, .26, .14), (r.uniform(-15, 15), r.uniform(-10, 10), r.uniform(-8, 8)), .01)
        crumble(o, .04, seed+i)
    box(m["dark_stone"], (0, 0, .09), (L+.02, .36, .18), bevel=.01)
    for k in range(4):  # entulho no pé
        o = box(m["brick"], (r.uniform(-L/2, L/2), r.choice([-1, 1])*r.uniform(.2, .35), .05), (.2, .1, .07), (0, r.uniform(-20, 20), r.uniform(0, 90)), .005)
    return {}

@asset("paredes", walls=True)
def muro_reboco_janela(m, seed=3):
    """Muro rebocado com janela gótica estreita e grade."""
    L = T
    box(m["brick_p"], (-L/2+.12, 0, 1.3), (.24, .3, 2.6), bevel=.004)
    box(m["brick_p"], (L/2-.12, 0, 1.3), (.24, .3, 2.6), bevel=.004)
    box(m["brick_p"], (0, 0, .4), (L-.48, .3, .8), bevel=.004)
    box(m["brick_p"], (0, 0, 2.3), (L-.48, .3, 0.6), bevel=.004)
    box(m["dark_stone"], (0, -.02, .82), (L-.4, .36, .06), bevel=.01)   # peitoril
    for i in range(3):
        cyl(m["iron"], (-.1 + i*.1, 0, 1.4), .01, 1.1, verts=6)
    box(K.mat_emit("janela_quente", (1, .45, .12), 2.2), (0, .1, 1.4), (L-.48, .02, 1.1), bevel=0)
    box(m["dark_stone"], (0, 0, .09), (L+.02, .36, .18), bevel=.01)
    point((0, -.4, 1.4), (1, .5, .2), 12, .3)
    return {"emissivo": "janela"}

@asset("paredes", walls=True)
def cerca_ferro(m, seed=4):
    """Gradil de cemitério com pontas de lança, levemente torto."""
    r = rnd(seed); L = T
    for z in (.25, 1.35):
        box(m["iron"], (0, 0, z), (L, .03, .04), bevel=.005)
    for i in range(5):
        x = -L/2 + L/5*(i+.5); tilt = r.uniform(-4, 4)
        cyl(m["iron"], (x, 0, .8), .014, 1.6, (0, tilt, 0), 6)
        cyl(m["iron"], (x + math.sin(math.radians(tilt))*.8, 0, 1.66), .03, .12, (0, tilt, 0), 4, r2=0)
    box(m["stone"], (0, 0, .08), (L, .22, .16), bevel=.02)
    return {}

@asset("paredes", walls=True)
def palicada(m, seed=5):
    """Paliçada do Acampamento da Vela: estacas, chapas de zinco e arame."""
    r = rnd(seed); L = T
    for i in range(4):
        x = -L/2 + L/4*(i+.5); h = r.uniform(2.0, 2.5)
        cyl(m["wood"], (x, 0, h/2), .07, h, (r.uniform(-4, 4), r.uniform(-4, 4), 0), 8)
        cyl(m["wood"], (x, 0, h+.12), .07, .24, (0, 0, 0), 8, r2=0)
    for k in range(2):
        box(m["tin"], (r.uniform(-.1, .1), -.09, r.uniform(.5, 1.3)), (L*.9, .012, .7), (r.uniform(-5, 5), 0, r.uniform(-3, 3)), .003)
    box(m["wood"], (0, .09, 1.6), (L, .05, .1), (0, r.uniform(-4, 4), 0), .01)
    for i in range(8):
        torus(m["iron"], (-L/2 + i*L/8, -.08, 2.05), .07, .004, (90, 0, r.uniform(-20, 20)))
    return {}

@asset("paredes", walls=True)
def barricada_sacos(m, seed=6):
    r = rnd(seed); L = T
    for row in range(3):
        for i in range(2):
            x = -L/2 + L/2*(i+.5) + (L/4 if row % 2 else 0) - (L/8 if row % 2 else 0)
            o = sphere(m["sack"], (x, r.uniform(-.02, .02), .1 + row*.17), (L/4.2, .22, .1))
            displace(o, .02, .2, seed+row*3+i, 1)
    for i in range(10):
        torus(m["iron"], (-L/2 + i*L/10, 0, .62), .08, .004, (90+r.uniform(-20, 20), 0, r.uniform(-30, 30)))
    return {}

@asset("paredes", walls=True, dungeon=True)
def parede_matadouro(m, seed=7):
    """Porão do Matadouro: azulejo branco imundo sobre tijolo, canos de latão."""
    L = T
    tile = K.mat_stone("azulejo", (.32, .3, .26), (.12, .11, .09), 6, .0, ("wall", T), 2.8, 7.0)
    box(m["brick"], (0, .03, 1.5), (L, .24, 3.0), bevel=.004)
    box(tile, (0, -.1, .7), (L, .04, 1.4), bevel=.002)
    for k in range(3):
        box(K.mat_solid("rejunte", (.02, .02, .018)), (-L/2 + L/3*(k+.5), -.121, .7), (.006, .002, 1.4), bevel=0)
    for z in (.35, .7, 1.05):
        box(K.mat_solid("rejunte", (.02, .02, .018)), (0, -.121, z), (L, .002, .006), bevel=0)
    # sangue escorrido
    for k in range(3):
        x = -.2 + k*.17
        box(m["blood"], (x, -.123, .95 - k*.1), (.03, .002, .5 + k*.12), bevel=0)
    cyl(m["brass"], (0, -.16, 2.4), .06, L+.01, (0, 90, 0), 14)
    cyl(m["brass"], (0, -.14, 2.1), .035, L+.01, (0, 90, 0), 12)
    torus(m["brass"], (.15, -.16, 2.4), .068, .012, (0, 90, 0))
    return {}

@asset("paredes", walls=True, dungeon=True)
def parede_ossario(m, seed=8):
    """Ossário das Carpideiras: nichos com crânios e ossos empilhados."""
    r = rnd(seed); L = T
    box(m["stone_d"], (0, .05, 1.5), (L, .3, 3.0), bevel=.006)
    for row in range(3):
        z = .45 + row*.75
        box(K.mat_solid("nicho", (.005, .004, .004)), (0, -.1, z), (L*.8, .1, .5), bevel=.01)
        for i in range(4):
            x = -L*.3 + i*L*.2 + r.uniform(-.02, .02)
            sk = sphere(m["bone"], (x, -.12, z - .12), (.07, .075, .07), segs=12)
            sphere(K.mat_solid("orbita", (0, 0, 0)), (x - .025, -.18, z - .11), (.018, .01, .02), segs=8)
            sphere(K.mat_solid("orbita", (0, 0, 0)), (x + .025, -.18, z - .11), (.018, .01, .02), segs=8)
        for i in range(5):  # ossos longos atrás
            along(m["bone"], (-L*.38, -.07+i*.01, z+.05 + i*.035), (L*.38, -.07+i*.01, z+.05+i*.035+r.uniform(-.02, .02)), .018, verts=6)
    return {}

@asset("paredes", walls=True, dungeon=True)
def parede_trombeta(m, seed=9):
    """Câmara da Trombeta: pedra clara com placas de porcelana rachada e nervuras de ferro."""
    L = T
    box(m["stone_d"], (0, .05, 1.6), (L, .3, 3.2), bevel=.006)
    box(m["porcelain"], (0, -.11, 1.5), (L*.8, .04, 2.2), bevel=.01)
    for x in (-L/2+.03, L/2-.03):
        box(m["iron"], (x, -.12, 1.6), (.06, .08, 3.2), bevel=.01)
    for z in (.4, 2.6):
        box(m["iron"], (0, -.14, z), (L, .05, .05), bevel=.01)
    for k in range(2):
        sphere(m["brass"], (-.15 + k*.3, -.17, 2.6), (.025, .025, .025), segs=8)
    return {}

# ================================================================ PRÉDIOS
def gothic_window(m, glass, loc, w, h, face_y=True, depth=.35):
    """Janela ogival: vitral aceso, moldura de pedra e arco de ponta."""
    x, y, z = loc
    box(glass, (x, y, z + h/2), (w, .04, h), bevel=0)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=w/math.sqrt(2), depth=w*.7, location=(x, y, z + h + w*.35), rotation=(0, 0, math.radians(45)))
    o = bpy.context.object; o.scale = (1, .05/(w/math.sqrt(2)), 1); o.data.materials.append(glass)
    for sx in (-1, 1):
        box(m["stone"], (x + sx*(w/2 + .05), y - .05, z + h/2), (.1, .14, h + .1), bevel=.015)
    box(m["stone"], (x, y - .05, z - .04), (w + .25, .2, .08), bevel=.015)
    for k in range(3):   # caixilho de chumbo/ferro
        box(m["iron"], (x, y - .025, z + h*(k+1)/4), (w, .015, .015), bevel=0)
    box(m["iron"], (x, y - .025, z + h/2), (.015, .015, h), bevel=0)

@asset("predios", fp=(12, 16), samples=48)
def capela_sao_lazaro(m, seed=10):
    """Capela de São Lázaro, posto dos Arautos. Nave gótica com contrafortes,
    torre sineira partida, rosácea vermelha acesa e portal com trombeta partida."""
    r = rnd(seed)
    W, D, H = 5.6, 9.0, 6.0           # nave: largura (x), profundidade (y), altura da parede
    wall = K.mat_brick("silhar", ("wall", T*2), 4.0, (.085, .078, .07), 3.5, 0.0, T, .32, .018)
    # paredes da nave (fachada principal voltada para -Y, a câmera vê -Y e +X)
    box(wall, (0, D/2, H/2), (W, .5, H), bevel=.02)                       # fundo
    box(wall, (-W/2, 0, H/2), (.5, D, H), bevel=.02)                      # lateral esquerda
    # lateral direita (+X) com janelas ogivais
    nwin = 4; seg = D/nwin
    for i in range(nwin):
        y = -D/2 + seg*(i+.5)
        box(wall, (W/2, y - seg/2 + .35, H/2), (.5, .7, H), bevel=.02)
        box(wall, (W/2, y + seg/2 - .35, H/2), (.5, .7, H), bevel=.02)
        box(wall, (W/2, y, .9), (.5, seg - 1.4, 1.8), bevel=.02)
        box(wall, (W/2, y, H - .5), (.5, seg - 1.4, 1.0), bevel=.02)
        # vitral girado para +X
        g = m["glass"]
        box(g, (W/2 - .05, y, 1.8 + 1.35), (.04, seg - 1.4, 2.7), bevel=0)
        point((W/2 + 1.2, y, 2.8), (1, .15, .07), 60, .6)
        # contraforte
        if i < nwin:
            cb = box(wall, (W/2 + .45, y - seg/2, 1.6), (.8, .55, 3.2), bevel=.03)
            box(wall, (W/2 + .3, y - seg/2, 3.6), (.5, .5, 1.2), (0, -18, 0), .03)
            cyl(wall, (W/2 + .5, y - seg/2, 3.35), .28, .5, (0, 0, 45), 4, r2=0)
    cb = box(wall, (W/2 + .45, D/2, 1.6), (.8, .55, 3.2), bevel=.03)
    # fachada (-Y): portal ogival, rosácea, empena
    fy = -D/2
    for sx in (-1, 1):
        box(wall, (sx*(W/4 + .45), fy, H/2), (W/2 - .9, .6, H), bevel=.02)
    box(wall, (0, fy, H - 1.2), (1.8, .6, 2.4), bevel=.02)
    box(K.mat_solid("portal_escuro", (.004, .003, .003)), (0, fy + .1, 1.4), (1.8, .5, 2.8), bevel=0)
    # porta de madeira entreaberta com ferragens
    door = box(m["wood_d"], (-.45, fy - .05, 1.25), (.85, .08, 2.5), (0, 0, -25), .01)
    box(m["iron"], (-.45, fy - .1, 1.8), (.85, .02, .06), (0, 0, -25), 0)
    box(m["iron"], (-.45, fy - .1, .7), (.85, .02, .06), (0, 0, -25), 0)
    box(m["wood_d"], (.45, fy - .05, 1.25), (.85, .08, 2.5), bevel=.01)
    # arco do portal (aduelas)
    for k in range(9):
        a = math.radians(180 * k / 8)
        box(wall, (math.cos(a)*1.05, fy - .35, 2.8 + math.sin(a)*.9), (.32, .3, .22), (0, -math.degrees(a) + 90, 0), .02)
    # degraus
    for k in range(3):
        box(m["dark_stone"], (0, fy - .55 - k*.3, .1 + (2-k)*.0), (2.6 - k*.0 + (2-k)*.3, .35 + k*.0, .2 + (2-k)*.2 - (2-k)*.2 + (2-k)*.18), bevel=.02)
    # rosácea
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=.06, location=(0, fy - .28, 4.6), rotation=(math.radians(90), 0, 0))
    o = bpy.context.object; o.data.materials.append(m["glass"])
    torus(wall, (0, fy - .33, 4.6), 1.05, .12, (90, 0, 0))
    for k in range(8):
        a = math.radians(45*k)
        along(m["iron"], (0, fy - .33, 4.6), (math.cos(a)*1.0, fy - .33, 4.6 + math.sin(a)*1.0), .025, verts=6)
    point((0, fy - 1.5, 4.4), (1, .12, .05), 220, .8)
    # empena da fachada
    prism(wall, (0, fy, H), W + .5, .6, 2.6)
    prism(wall, (0, D/2, H), W + .5, .5, 2.6)
    # cruz quebrada no topo da empena
    box(m["iron"], (0, fy, H + 2.9), (.1, .1, .9), (0, 8, 0), .01)
    box(m["iron"], (.05, fy, H + 3.05), (.5, .08, .08), (0, 8, 0), .01)
    # telhado: duas águas de ardósia, com um buraco
    slate = K.mat_stone("ardosia", (.045, .045, .05), (.015, .015, .018), 6, .2)
    ang = math.degrees(math.atan2(2.6, W/2)); sl = math.hypot(2.6, W/2) + .35
    for sx in (-1, 1):
        o = box(slate, (sx*W/4, 0, H + 1.3 + .05), (sl, D + .4, .14), (0, sx*ang, 0), .01)
        if sx > 0:   # buraco no telhado (desabou)
            cut = box(slate, (W/4, -.6, H + 1.4), (1.6, 2.6, 2.0), (r.uniform(-10, 10), 0, 18), 0)
            displace(cut, .35, .4, seed, 3)
            bo = o.modifiers.new("buraco", 'BOOLEAN'); bo.object = cut; bo.operation = 'DIFFERENCE'
            cut.hide_render = True; cut.name = "_corte"
            for k in range(4):   # caibros expostos
                yy = -1.6 + k*.5
                box(m["wood_d"], (W/4 - .05, yy, H + 1.25), (sl*.9, .1, .12), (0, ang, 0), .01)
            for k in range(6):   # telhas caídas dentro
                box(slate, (r.uniform(.3, 2.2), r.uniform(-2.2, .8), r.uniform(.1, .5)), (.4, .3, .05), (r.uniform(-40, 40), r.uniform(-40, 40), r.uniform(0, 90)), .01)
    box(m["dark_stone"], (0, 0, H + 2.6), (.2, D + .3, .2), bevel=.02)
    point((W/4, -D/2 + D/6*2.5, H + .5), (1, .2, .08), 120, 1.0)    # luz saindo pelo buraco do telhado
    # torre sineira partida (canto esquerdo da fachada)
    tx, ty = -W/2 - .3, -D/2 + .2
    box(wall, (tx, ty, 4.5), (2.0, 2.0, 9.0), bevel=.03)
    for sx in (-1, 1):
        box(wall, (tx + sx*.75, ty, 10.2), (.5, 2.0, 2.4), bevel=.03)
    box(wall, (tx, ty - .75, 10.2), (1.0, .5, 2.4), bevel=.03)
    for k in range(4):  # topo quebrado
        o = box(wall, (tx + r.uniform(-.8, .8), ty + r.uniform(-.8, .8), 11.4 + r.uniform(0, .5)), (r.uniform(.4, .8), r.uniform(.4, .8), r.uniform(.3, .9)), (r.uniform(-10, 10), r.uniform(-10, 10), r.uniform(0, 30)), .02)
        crumble(o, .06, seed + k)
    # sino caído inclinado na abertura
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=.45, radius2=.22, depth=.7, location=(tx, ty, 9.6), rotation=(math.radians(18), 0, 0))
    o = bpy.context.object; o.data.materials.append(m["brass"])
    for z in (3.0, 6.5):
        gothic_window(m, m["glass"], (tx, ty - 1.02, z), .4, 1.1)
        point((tx, ty - 1.8, z + .6), (1, .12, .05), 25, .3)
    # janelas ogivais na fachada
    for sx in (-1, 1):
        gothic_window(m, m["glass"], (sx*1.75, fy - .31, 2.0), .55, 1.6)
        point((sx*1.75, fy - 1.2, 2.8), (1, .12, .05), 40, .4)
    # estandarte dos Arautos (trombeta partida) ao lado do portal
    for sx in (-1, 1):
        cyl(m["iron"], (sx*1.5, fy - .45, 2.4), .02, 1.4, (90, 0, 0), 6)
        box(m["red_cloth"], (sx*1.5, fy - 1.1, 1.7), (.6, .02, 1.5), bevel=0)
        box(K.mat_solid("ouro_sujo", (.4, .28, .09), .8, .4), (sx*1.5, fy - 1.12, 1.9), (.12, .01, .5), bevel=0)
        box(K.mat_solid("ouro_sujo", (.4, .28, .09), .8, .4), (sx*1.5, fy - 1.12, 2.05), (.3, .01, .07), bevel=0)
    # velas e braseiro na entrada
    for k in range(7):
        candle((r.uniform(-1.2, 1.2), fy - r.uniform(.9, 1.4), .2 + .0), r.uniform(.08, .2))
    for sx in (-1, 1):
        cyl(m["iron"], (sx*2.2, fy - 1.3, .45), .25, .1, verts=12)
        cyl(m["iron"], (sx*2.2, fy - 1.3, .2), .04, .4, verts=8)
        flame((sx*2.2, fy - 1.3, .52), .9)
    # sujeira, entulho
    for k in range(14):
        o = box(wall, (r.uniform(-W/2 - 1, W/2 + 1), r.uniform(-D/2 - 1.5, D/2), .08), (r.uniform(.15, .4), r.uniform(.15, .35), r.uniform(.1, .2)), (r.uniform(-20, 20), r.uniform(-20, 20), r.uniform(0, 90)), .02)
        crumble(o, .04, seed + 30 + k)
    return {"emissivo": "vitrais vermelhos, braseiros e velas"}

@asset("predios", fp=(8, 8))
def casa_ruina(m, seed=11):
    """Sobrado de tijolo com reboco caído, segundo andar desabado, janela acesa."""
    r = rnd(seed)
    W, D = 4.6, 4.6
    def wall_x(y, x0, x1, z0, z1, mat=m["brick_p"]):
        box(mat, ((x0+x1)/2, y, (z0+z1)/2), (x1-x0, .3, z1-z0), bevel=.01)
    def wall_y(x, y0, y1, z0, z1, mat=m["brick_p"]):
        box(mat, (x, (y0+y1)/2, (z0+z1)/2), (.3, y1-y0, z1-z0), bevel=.01)
    # fundo e lado esquerdo inteiros (2 andares)
    wall_x(D/2, -W/2, W/2, 0, 5.4); wall_y(-W/2, -D/2, D/2, 0, 5.4)
    # frente (-Y): porta e janelas, segundo andar quebrado
    wall_x(-D/2, -W/2, -1.4, 0, 2.8); wall_x(-D/2, -.4, .6, 0, 2.8); wall_x(-D/2, 1.6, W/2, 0, 2.8)
    wall_x(-D/2, -1.4, -.4, 2.2, 2.8); wall_x(-D/2, .6, 1.6, 2.4, 2.8); wall_x(-D/2, .6, 1.6, 0, .9)
    box(K.mat_solid("vao", (.003, .003, .003)), (-.9, -D/2 + .05, 1.1), (1.0, .2, 2.2), bevel=0)
    box(K.mat_emit("janela_quente", (1, .45, .12), 2.2), (1.1, -D/2 + .1, 1.65), (1.0, .05, 1.5), bevel=0)
    for k in range(3):
        box(m["wood_d"], (1.1, -D/2 - .17, 1.1 + k*.5), (1.1, .04, .14), (0, r.uniform(-12, 12), 0), .005)   # tábuas pregadas
    point((1.1, -D/2 - .8, 1.6), (1, .5, .2), 30, .3)
    for k in range(6):
        h = r.uniform(.4, 2.6); x = -W/2 + W/6*(k+.5)
        o = box(m["brick_p"], (x, -D/2, 2.8 + h/2), (W/6 + .01, .3, h), bevel=.01); crumble(o, .03, seed+k)
    # lado direito (+X): parede baixa quebrada com janela
    wall_y(W/2, -D/2, -.3, 0, 3.2); wall_y(W/2, .9, D/2, 0, 2.2)
    for k in range(5):
        h = r.uniform(.2, 1.8); y = -.3 + 1.2*(k+.5)/5
        o = box(m["brick_p"], (W/2, y, h/2), (.3, .25, h), bevel=.01); crumble(o, .03, seed+10+k)
    # laje do 2º andar caída em diagonal + vigas
    box(m["wood_d"], (0, .5, 2.0), (W - .4, 2.5, .12), (25, 8, 0), .01)
    for k in range(4):
        box(m["wood_d"], (-W/2 + .6 + k*1.1, 0, 2.85), (.14, D - .3, .18), (r.uniform(-8, 8), 0, 0), .01)
    # telhado remanescente no fundo
    box(K.mat_stone("telha", (.07, .03, .02), (.03, .015, .01), 5, .1), (0, D/2 - .6, 5.6), (W + .4, 1.6, .15), (-30, 0, 0), .01)
    # chaminé
    box(m["brick"], (-W/2 + .6, D/2 - .3, 6.0), (.6, .6, 1.4), bevel=.01)
    # entulho e móveis
    for k in range(18):
        o = box(m["brick"], (r.uniform(-W/2, W/2 + 1), r.uniform(-D/2 - .8, D/2), .07), (.22, .11, .07), (r.uniform(-30, 30), r.uniform(-30, 30), r.uniform(0, 180)), .005)
    box(m["wood"], (-1.2, 1.0, .4), (1.2, .7, .08), (0, 6, 20), .01)   # mesa virada
    return {"emissivo": "janela"}

@asset("predios", fp=(14, 12), samples=48)
def abatedouro_carnica(m, seed=12):
    """Abatedouro Carniça: galpão industrial de tijolo, telhado de zinco em
    serra, chaminé, portão de correr e trilho de ganchos com carcaças."""
    r = rnd(seed)
    W, D, H = 8.5, 7.0, 4.2
    box(m["brick"], (0, D/2, H/2), (W, .4, H), bevel=.01)
    box(m["brick"], (-W/2, 0, H/2), (.4, D, H), bevel=.01)
    box(m["brick"], (W/2, 0, H/2), (.4, D, H), bevel=.01)
    # fachada -Y com portão grande
    box(m["brick"], (-W/2 + 1.2, -D/2, H/2), (2.4, .4, H), bevel=.01)
    box(m["brick"], (W/2 - 1.9, -D/2, H/2), (3.8, .4, H), bevel=.01)
    box(m["brick"], (-.4 + .0, -D/2, H - .5), (2.3, .4, 1.0), bevel=.01)
    box(K.mat_solid("vao", (.003, .003, .003)), (-.4, -D/2 + .1, 1.6), (2.3, .3, 3.2), bevel=0)
    # portão de correr de chapa, entreaberto
    gate = box(m["rust"], (.8, -D/2 - .3, 1.6), (1.6, .06, 3.2), bevel=.005)
    for z in (.4, 1.6, 2.8):
        box(m["iron"], (.8, -D/2 - .34, z), (1.6, .02, .08), bevel=0)
    box(m["iron"], (0, -D/2 - .3, 3.3), (3.6, .1, .1), bevel=.005)
    point((-.6, -D/2 + .5, 1.5), (1, .3, .1), 35, .4)     # brilho vermelho lá dentro
    # janelas altas industriais com luz
    for i in range(2):
        x = W/2 - 1.0 - i*1.6
        box(K.mat_emit("janela_suja", (.9, .35, .1), 1.4), (x, -D/2 - .21, 2.8), (1.1, .03, .9), bevel=0)
        for k in range(3):
            box(m["iron"], (x - .55 + k*.55, -D/2 - .23, 2.8), (.03, .02, .9), bevel=0)
        box(m["iron"], (x, -D/2 - .23, 2.8), (1.1, .02, .03), bevel=0)
    for i in range(3):
        y = -D/2 + 1.2 + i*2.2
        box(K.mat_emit("janela_suja", (.9, .35, .1), 1.4), (W/2 + .21, y, 2.8), (.03, 1.1, .9), bevel=0)
        for k in range(3):
            box(m["iron"], (W/2 + .23, y - .55 + k*.55, 2.8), (.02, .03, .9), bevel=0)
        point((W/2 + 1.0, y, 2.6), (1, .4, .12), 18, .4)
    # telhado em serra (shed) de zinco
    for k in range(3):
        y = -D/2 + D/3*(k+.5)
        box(m["tin"], (0, y, H + .55), (W + .4, D/3 + .1, .05), (-22, 0, 0), .003)
        box(m["brick"], (0, y + D/6, H + .55), (W, .2, 1.1), bevel=.01)
        if k == 1:  # placas soltas
            box(m["rust"], (W/2 - 1, y - .3, H + .9), (1.4, 1.0, .04), (-40, 10, 15), .003)
    # chaminé de tijolo com fumaça
    box(m["brick"], (-W/2 + 1.0, D/2 - .8, H + 2.5), (.9, .9, 5.0), bevel=.01)
    for k in range(3):
        box(m["iron"], (-W/2 + 1.0, D/2 - .8, H + 1.5 + k*1.3), (.95, .95, .08), bevel=0)
    # letreiro "CARNIÇA" de chapa
    box(m["rust"], (-.4, -D/2 - .25, H + .3), (3.2, .05, .6), bevel=.005)
    for k, ch in enumerate("CARNIÇA"):
        box(K.mat_solid("tinta_branca", (.3, .28, .24), 0, .8), (-1.6 + k*.4, -D/2 - .28, H + .3), (.22, .01, .38), bevel=0)
    # trilho com ganchos e carcaças na frente
    box(m["iron"], (W/2 - 1.9, -D/2 - 1.0, 3.0), (3.6, .1, .1), bevel=.005)
    for sx in (-1, 1):
        cyl(m["iron"], (W/2 - 1.9 + sx*1.8, -D/2 - 1.0, 1.5), .05, 3.0, verts=8)
    for k in range(3):
        x = W/2 - 3.2 + k*1.2
        chain(m["iron"], (x, -D/2 - 1.0, 2.95), (x, -D/2 - 1.0, 2.3), 5, .03)
        if k != 1:
            o = sphere(m["meat"], (x, -D/2 - 1.0, 1.75), (.25, .18, .55)); displace(o, .06, .15, seed+k, 1)
            for j in range(4):
                along(m["bone"], (x - .15, -D/2 - 1.15, 1.5 + j*.15), (x + .15, -D/2 - 1.15, 1.55 + j*.15), .015, verts=6)
    # barris e caixas, poça de sangue
    for k in range(3):
        cyl(m["rust"], (-W/2 + .6 + k*.62, -D/2 - .7, .45), .28, .9, verts=16)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.0, depth=.01, location=(-.4, -D/2 - .9, .005))
    o = bpy.context.object; o.scale = (1.3, .7, 1); o.data.materials.append(m["blood"])
    point((-W/2 + 1.0, D/2 - .8, H + 5.3), (1, .35, .1), 30, .3)
    return {"emissivo": "janelas"}

@asset("predios", fp=(5, 5))
def tenda_vigilia(m, seed=13):
    """Tenda de lona remendada do Acampamento da Vela."""
    r = rnd(seed)
    W, D, H = 2.6, 3.0, 2.2
    for sx in (-1, 1):
        o = box(m["cloth"], (sx*W/4, 0, H/2), (W/2*1.25, D, .04), (0, sx*58, 0), 0)
        displace(o, .06, .3, seed+sx, 3)
    for y in (-D/2, D/2):
        along(m["wood"], (-.05, y, H + .1), (.05, y, 0), .04, verts=6)
    along(m["wood"], (0, -D/2 - .1, H), (0, D/2 + .1, H), .035, verts=6)
    # remendos azul aço
    box(K.mat_cloth("remendo", (.04, .07, .1)), (W/4 + .12, -.3, H/2 + .1), (.6, .5, .01), (0, 58, 0), 0)
    # cordas
    for y in (-D/2 + .2, D/2 - .2):
        for sx in (-1, 1):
            along(K.mat_solid("corda", (.1, .08, .05)), (sx*W/2*.6, y, H*.55), (sx*W/2*1.3, y, 0), .008, verts=4)
    # caixote e lanterna na entrada
    box(m["wood"], (.4, -D/2 - .5, .25), (.5, .5, .5), (0, 0, 20), .02)
    cyl(m["brass"], (.4, -D/2 - .5, .6), .06, .18, verts=10)
    sphere(K.mat_emit("lanterna", (1, .6, .25), 8), (.4, -D/2 - .5, .6), (.04, .04, .06), segs=8)
    point((.4, -D/2 - .6, .7), (1, .55, .2), 8, .05)
    return {}

@asset("predios", fp=(4, 4), samples=48)
def lampada_arco(m, seed=14):
    """Lâmpada de arco do Acampamento da Vela: mastro de ferro e latão com
    bobinas de tesla e um arco elétrico azul que afasta os mortos."""
    r = rnd(seed)
    # base de concreto e caldeira
    box(m["dark_stone"], (0, 0, .2), (1.6, 1.6, .4), bevel=.04)
    cyl(m["brass"], (0, 0, 1.0), .45, 1.2, verts=24)
    for z in (.6, 1.0, 1.4):
        torus(m["iron"], (0, 0, z), .46, .025)
    for k in range(6):
        a = math.radians(60*k)
        sphere(m["iron"], (math.cos(a)*.46, math.sin(a)*.46, 1.55), (.03, .03, .03), segs=6)
    # manômetro e válvulas
    cyl(m["brass"], (.3, -.35, 1.2), .1, .05, (90, 0, 40), 16)
    cyl(K.mat_solid("vidro_manometro", (.6, .55, .4), 0, .1), (.32, -.38, 1.2), .08, .01, (90, 0, 40), 16)
    # canos
    along(m["brass"], (.45, 0, .9), (.75, .4, .4), .05)
    along(m["brass"], (.75, .4, .4), (.75, .4, 0), .05)
    # mastro treliçado
    for k in range(4):
        a = math.radians(45 + 90*k)
        along(m["iron"], (math.cos(a)*.35, math.sin(a)*.35, 1.6), (math.cos(a)*.12, math.sin(a)*.12, 5.5), .035, verts=6)
    for z in range(5):
        zz = 2.0 + z*.75; rr = .35 - (zz-1.6)/3.9*.23
        torus(m["iron"], (0, 0, zz), rr, .015)
    # bobinas
    for z in (3.0, 4.2):
        cyl(K.mat_solid("cobre", (.35, .14, .06), .9, .35), (0, 0, z), .2, .35, verts=20)
        for k in range(6):
            torus(K.mat_solid("cobre", (.35, .14, .06), .9, .35), (0, 0, z - .15 + k*.06), .21, .012)
    # esfera e coroa do arco
    sphere(m["brass"], (0, 0, 5.7), (.22, .22, .22))
    for k in range(5):
        a = math.radians(72*k)
        along(m["iron"], (0, 0, 5.7), (math.cos(a)*.6, math.sin(a)*.6, 6.0), .02, verts=6)
        sphere(m["brass"], (math.cos(a)*.6, math.sin(a)*.6, 6.0), (.05, .05, .05), segs=8)
    arc = K.mat_emit("arco_eletrico", (.62, .85, 1.0), 40)
    for k in range(5):  # raios do arco entre as pontas
        a0, a1 = math.radians(72*k), math.radians(72*(k+1))
        p0 = Vector((math.cos(a0)*.6, math.sin(a0)*.6, 6.0)); p1 = Vector((math.cos(a1)*.6, math.sin(a1)*.6, 6.0))
        pts = [p0.lerp(p1, t/4) + Vector((r.uniform(-.08, .08), r.uniform(-.08, .08), r.uniform(0, .2))) for t in range(5)]
        pts[0], pts[-1] = p0, p1
        for a, b in zip(pts, pts[1:]): along(arc, a, b, .012, verts=4)
    sphere(K.mat_emit("arco_nucleo", (.85, .95, 1.0), 60), (0, 0, 6.15), (.12, .12, .12))
    point((0, 0, 6.2), (.55, .8, 1.0), 900, .3)
    # símbolo da Vigília: vela dentro de engrenagem, numa placa
    box(m["rust"], (0, -.82, .7), (.9, .05, .6), bevel=.005)
    torus(m["brass"], (0, -.86, .72), .2, .03, (90, 0, 0))
    for k in range(8):
        a = math.radians(45*k)
        box(m["brass"], (math.cos(a)*.24, -.86, .72 + math.sin(a)*.24), (.06, .03, .06), (0, -math.degrees(a), 0), 0)
    box(K.mat_solid("cera", (.38, .33, .24)), (0, -.87, .7), (.06, .02, .18), bevel=0)
    sphere(K.mat_emit("chama_vela", (1, .6, .2), 25), (0, -.88, .82), (.02, .01, .04), segs=8)
    return {"emissivo": "arco elétrico azul (#9fd8ff)"}

@asset("predios", fp=(4, 4))
def torre_vigia(m, seed=15):
    """Torre de vigia de madeira e sucata com holofote."""
    r = rnd(seed); S = 1.4; H = 4.2
    for sx in (-1, 1):
        for sy in (-1, 1):
            along(m["wood"], (sx*S/2*1.2, sy*S/2*1.2, 0), (sx*S/2*.8, sy*S/2*.8, H + 1.2), .08, verts=8)
    for z in (1.2, 2.6):
        for sx in (-1, 1):
            along(m["wood"], (sx*S/2*1.1, -S/2*1.1, z), (sx*S/2*1.0, S/2*1.0, z + 1.0), .04, verts=6)
            along(m["wood"], (-S/2*1.1, sx*S/2*1.1, z + 1.0), (S/2*1.0, sx*S/2*1.0, z), .04, verts=6)
    box(m["wood_d"], (0, 0, H), (S + .3, S + .3, .12), bevel=.01)
    for k, (dx, dy, w, d) in enumerate([(0, -1, 1, 0), (1, 0, 0, 1), (0, 1, 1, 0), (-1, 0, 0, 1)]):
        box(m["tin"] if k % 2 else m["rust"], (dx*(S/2 + .14), dy*(S/2 + .14), H + .45), ((S + .3) if w else .04, (S + .3) if d else .04, .8), (0, 0, r.uniform(-3, 3)), .003)
    box(m["tin"], (0, 0, H + 1.6), (S + .7, S + .7, .05), (6, -4, 0), .003)
    # holofote
    cyl(m["iron"], (.3, -.4, H + 1.05), .18, .32, (70, 0, 30), 16)
    cyl(K.mat_emit("holofote", (.9, .95, 1.0), 30), (.37, -.52, H + 1.0), .15, .02, (70, 0, 30), 16)
    sl = bpy.data.objects.new("spot", bpy.data.lights.new("spot", 'SPOT')); bpy.context.scene.collection.objects.link(sl)
    sl.data.energy = 600; sl.data.spot_size = math.radians(28); sl.data.color = (.85, .9, 1.0)
    sl.location = (.4, -.6, H + 1.0); sl.rotation_euler = (math.radians(55), 0, math.radians(30))
    # escada
    for k in range(10):
        box(m["wood"], (S/2*1.2 + .2, -.2 + 0, .3 + k*.4), (.05, .5, .05), bevel=.005)
    for sy in (-1, 1):
        cyl(m["wood"], (S/2*1.2 + .2, -.2 + sy*.25, H/2), .03, H, verts=6)
    return {}

@asset("predios", fp=(4, 4))
def barraco_sucata(m, seed=16):
    """Barraco de sucata: chapas de zinco, portas velhas, placa de trânsito."""
    r = rnd(seed); W, D, H = 2.4, 2.2, 2.2
    for (x, y, w, d) in [(0, D/2, W, .05), (-W/2, 0, .05, D), (W/2, 0, .05, D)]:
        for k in range(3):
            mat = r.choice([m["tin"], m["rust"], m["wood"]])
            if d > w: box(mat, (x, -D/2 + D/3*(k+.5), H/2), (.05, D/3 + .05, H + r.uniform(-.2, .1)), (r.uniform(-3, 3), 0, 0), .003)
            else: box(mat, (-W/2 + W/3*(k+.5), y, H/2), (W/3 + .05, .05, H + r.uniform(-.2, .1)), (0, r.uniform(-3, 3), 0), .003)
    box(m["rust"], (-W/2 + .4, -D/2, H/2), (.8, .05, H), bevel=.003)
    box(m["wood_d"], (W/2 - .5, -D/2, H/2), (1.0, .05, H), bevel=.003)
    box(K.mat_solid("vao", (.003, .003, .003)), (.05, -D/2 + .02, 1.0), (.7, .05, 2.0), bevel=0)
    box(m["tin"], (0, 0, H + .15), (W + .5, D + .5, .04), (8, 0, 0), .003)
    box(m["rust"], (.3, .2, H + .2), (1.0, .9, .04), (8, 0, 12), .003)
    # placa de trânsito velha (pare) pregada
    cyl(K.mat_solid("placa_vermelha", (.25, .02, .015), .3, .5), (-W/2 + .4, -D/2 - .05, 1.5), .25, .02, (90, 0, 0), 8)
    # pneus
    for k in range(2):
        torus(K.mat_solid("borracha", (.012, .012, .012), 0, .8), (W/2 + .35, -D/2 + .4, .1 + k*.18), .26, .09)
    # fogareiro
    cyl(m["rust"], (-.6, -D/2 - .5, .25), .18, .5, verts=12); flame((-.6, -D/2 - .5, .5), .6)
    return {}

@asset("predios", fp=(4, 4), samples=48)
def entrada_cripta(m, seed=17):
    """Entrada do porão do Abatedouro que leva à Cripta da Trombeta Calada:
    alçapão de ferro arrombado, escada descendo, luz vermelha lá dentro."""
    r = rnd(seed)
    W, D = 1.6, 2.4
    for (x, y, w, d) in [(0, D/2, W + .5, .25), (-W/2 - .12, 0, .25, D), (W/2 + .12, 0, .25, D)]:
        box(m["dark_stone"], (x, y, .25), (w, d, .5), bevel=.03)
    box(m["dark_stone"], (0, -D/2 - .05, .05), (W + .5, .2, .1), bevel=.02)
    # poço escuro e degraus descendo
    box(K.mat_solid("abismo", (.002, .001, .001)), (0, 0, .0), (W, D, .02), bevel=0)
    for k in range(6):
        box(m["stone_d"], (0, -D/2 + .2 + k*.35, -.0 - k*.0 + .02 - k*.004), (W - .05, .3, .03), bevel=.01)
    # alçapão de ferro aberto e torto
    box(m["rust"], (0, D/2 + .4, 1.0), (W, .08, 1.6), (-12, 0, 4), .01)
    for k in range(4):
        box(m["iron"], (0, D/2 + .36, .4 + k*.42), (W, .03, .06), (-12, 0, 4), 0)
    chain(m["iron"], (-W/2 + .1, D/2 + .3, 1.6), (-W/2 - .2, D/2 - .3, .5), 8, .03)
    # brilho vermelho vindo de baixo
    box(K.mat_emit("brilho_porao", (.7, .07, .03), 3.0), (0, .4, -.0), (W - .2, D - .8, .01), bevel=0)
    point((0, .2, .3), (1, .12, .05), 60, .6)
    # placa de aviso
    cyl(m["wood"], (W/2 + .5, -D/2, .6), .04, 1.2, verts=6)
    box(m["wood"], (W/2 + .5, -D/2 - .04, 1.1), (.6, .04, .35), (0, 0, 0), .01)
    for k in range(3):
        box(m["blood"], (W/2 + .35 + k*.15, -D/2 - .07, 1.1), (.06, .01, .2), bevel=0)
    return {"emissivo": "brilho vermelho da escada"}

# ================================================================ PROPS (área inicial)
@asset("props")
def tonel_fogo(m, seed=20):
    cyl(m["rust"], (0, 0, .4), .28, .8, verts=20)
    for z in (.15, .65): torus(m["iron"], (0, 0, z), .285, .02)
    cyl(m["coal"], (0, 0, .78), .25, .04, verts=16)
    flame((0, 0, .8), 1.1)
    return {"emissivo": "fogo", "luz": "quente"}

@asset("props", fp=(2, 2))
def fogueira(m, seed=21):
    r = rnd(seed)
    for k in range(9):
        a = math.radians(40*k)
        o = sphere(m["dark_stone"], (math.cos(a)*.5, math.sin(a)*.5, .06), (.12, .1, .08), segs=8); displace(o, .02, .1, seed+k, 1)
    for k in range(5):
        a = math.radians(72*k)
        along(m["wood_d"], (math.cos(a)*.4, math.sin(a)*.4, .02), (0, 0, .35), .045, verts=7)
    cyl(m["coal"], (0, 0, .03), .35, .04, verts=16)
    flame((0, 0, .1), 1.4)
    # espeto com carne
    for sx in (-1, 1): along(m["wood"], (sx*.55, 0, 0), (sx*.5, 0, .7), .02, verts=5)
    along(m["iron"], (-.6, 0, .68), (.6, 0, .68), .01, verts=5)
    sphere(m["meat"], (0, 0, .68), (.15, .08, .07))
    return {"emissivo": "fogo", "luz": "quente"}

@asset("props")
def poste_gas(m, seed=22):
    """Poste a gás aceso, ferro fundido gótico."""
    cyl(m["iron"], (0, 0, .15), .16, .3, verts=8, r2=.1)
    cyl(m["iron"], (0, 0, 1.6), .045, 2.8, verts=10)
    torus(m["iron"], (0, 0, .5), .07, .02)
    along(m["iron"], (0, 0, 2.8), (.35, 0, 3.0), .025, verts=6)
    lamp = (.4, 0, 2.75)
    cyl(m["iron"], (lamp[0], 0, 2.98), .14, .14, verts=4, r2=.02)
    cyl(K.mat_emit("vidro_lampiao", (1, .62, .28), 5), (lamp[0], 0, 2.78), .1, .3, verts=4, r2=.13)
    for k in range(4):
        a = math.radians(45 + 90*k)
        along(m["iron"], (lamp[0] + math.cos(a)*.13, math.sin(a)*.13, 2.93), (lamp[0] + math.cos(a)*.1, math.sin(a)*.1, 2.62), .01, verts=4)
    point((lamp[0], 0, 2.7), (1, .6, .28), 80, .1)
    return {"emissivo": "lampião", "luz": "quente"}

@asset("props")
def poste_gas_quebrado(m, seed=23):
    cyl(m["iron"], (0, 0, .15), .16, .3, verts=8, r2=.1)
    o = cyl(m["iron"], (0, 0, .9), .045, 1.5, verts=10)
    along(m["iron"], (0, 0, 1.6), (.9, -.6, 2.3), .045, verts=10)
    cyl(m["iron"], (1.3, -.9, .12), .12, .2, (60, 0, 30), 4, r2=.02)
    for k in range(6):
        sphere(K.mat_solid("vidro", (.2, .2, .18), 0, .1), (1.1 + k*.08, -.8 + k*.03, .02), (.03, .02, .01), segs=6)
    return {}

@asset("props")
def caixas(m, seed=24):
    r = rnd(seed)
    box(m["wood"], (0, 0, .25), (.5, .5, .5), (0, 0, 10), .02)
    box(m["wood"], (.05, .02, .7), (.4, .4, .4), (0, 0, 35), .02)
    box(m["wood"], (-.45, .2, .2), (.4, .4, .4), (0, 0, -15), .02)
    for (x, y, z, s, rz) in [(0, 0, .25, .5, 10), (.05, .02, .7, .4, 35), (-.45, .2, .2, .4, -15)]:
        for dz in (-s*.3, s*.3):
            box(m["iron"], (x, y, z + dz), (s*1.02, s*1.02, .03), (0, 0, rz), 0)
    return {}

@asset("props")
def barris(m, seed=25):
    for (x, y, rz) in [(0, 0, 0), (.55, .1, 0)]:
        o = cyl(m["wood"], (x, y, .45), .27, .9, verts=20)
        bpy.ops.object.modifier_add(type='SIMPLE_DEFORM'); o.modifiers[-1].deform_method = 'BEND'; o.modifiers[-1].angle = 0
        for z in (.12, .45, .78): torus(m["iron"], (x, y, z), .275, .015)
    o = cyl(m["wood"], (-.3, -.45, .27), .27, .9, (90, 0, 70), 20)
    for d in (-.33, 0, .33):
        torus(m["iron"], (-.3 + d*math.cos(math.radians(70+90))*0 + d*math.sin(math.radians(70))*-1*0 + d*math.cos(math.radians(-20)), -.45 + d*math.sin(math.radians(-20)), .27), .275, .015, (90, 0, 70))
    return {}

@asset("props")
def sacos_areia(m, seed=26):
    r = rnd(seed)
    for row in range(2):
        for i in range(3 - row):
            o = sphere(m["sack"], (-.35 + i*.35 + row*.17, r.uniform(-.03, .03), .1 + row*.17), (.18, .13, .1)); displace(o, .02, .2, seed+row*3+i, 1)
    return {}

@asset("props")
def cruz_madeira(m, seed=27):
    r = rnd(seed); t = r.uniform(-12, 12)
    box(m["wood"], (0, 0, .55), (.08, .08, 1.1), (r.uniform(-6, 6), t, 0), .01)
    box(m["wood"], (math.sin(math.radians(t))*.75, 0, .82), (.5, .07, .07), (0, t, r.uniform(-8, 8)), .01)
    o = sphere(K.mat_stone("monte_terra", (.06, .045, .03), (.02, .015, .01), 4), (0, 0, 0), (.35, .6, .12)); displace(o, .03, .15, seed, 1)
    torus(K.mat_solid("terco", (.25, .22, .17), 0, .5), (.03 + math.sin(math.radians(t))*.75, -.05, .74), .07, .006, (80, 0, 0))
    return {}

@asset("props")
def lapide(m, seed=28):
    r = rnd(seed)
    st = K.mat_stone("lapide", (.1, .1, .095), (.04, .04, .04), 3, .8)
    o = box(st, (0, 0, .45), (.5, .14, .9), (r.uniform(-6, 6), r.uniform(-10, 10), r.uniform(-8, 8)), .02)
    cyl(st, (0, 0, .9), .25, .14, (90, r.uniform(-10, 10), 0), 16)
    crumble(o, .015, seed)
    o = sphere(K.mat_stone("monte_terra", (.06, .045, .03), (.02, .015, .01), 4), (0, -.4, 0), (.3, .55, .1)); displace(o, .03, .15, seed, 1)
    candle((.2, -.2, .02), .1)
    return {}

@asset("props")
def lapide_cruz_celta(m, seed=29):
    st = K.mat_stone("lapide", (.1, .1, .095), (.04, .04, .04), 3, .8)
    box(st, (0, 0, .1), (.6, .4, .2), bevel=.02)
    box(st, (0, 0, .8), (.14, .14, 1.3), (0, 4, 0), .01)
    box(st, (.025, 0, 1.15), (.65, .13, .14), (0, 4, 0), .01)
    torus(st, (.03, 0, 1.15), .22, .04, (90, 0, 0))
    return {}

@asset("props", fp=(3, 3), samples=48)
def mausoleu(m, seed=30):
    """Pequeno mausoléu de família com porta de ferro e anjo de pedra sem cabeça."""
    st = K.mat_stone("pedra_tumulo", (.11, .105, .1), (.04, .04, .04), 2.5, .7)
    box(st, (0, 0, .15), (2.0, 2.4, .3), bevel=.03)
    box(st, (0, .1, 1.2), (1.7, 2.0, 1.8), bevel=.03)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=1.35, depth=.8, location=(0, .1, 2.5), rotation=(0, 0, math.radians(45)))
    o = bpy.context.object; o.scale = (.9, 1.05, 1); o.data.materials.append(st)
    for sx in (-1, 1): box(st, (sx*.75, -.95, 1.2), (.25, .25, 2.0), bevel=.02)
    box(K.mat_solid("vao", (.003, .003, .003)), (0, -.92, .95), (.8, .1, 1.3), bevel=0)
    for k in range(5): cyl(m["iron"], (-.3 + k*.15, -.98, .95), .012, 1.3, verts=6)
    box(m["iron"], (0, -.98, 1.55), (.8, .03, .05), bevel=0)
    # anjo de pedra sem cabeça no topo
    sphere(st, (0, -.4, 2.95), (.18, .14, .35))
    for sx in (-1, 1):
        o = box(st, (sx*.28, -.35, 3.1), (.35, .05, .55), (0, sx*-30, sx*20), .02)
    candle((.4, -1.2, .02), .15); candle((.5, -1.15, .02), .1); candle((-.45, -1.25, .02), .12)
    return {}

@asset("props", fp=(2, 2), samples=48)
def estatua_anjo_quebrada(m, seed=31):
    """Estátua de anjo de pedra caída, asa partida, sobre pedestal."""
    st = K.mat_stone("marmore_sujo", (.2, .19, .17), (.06, .058, .055), 3, .6)
    box(st, (0, 0, .4), (.9, .9, .8), bevel=.04)
    box(st, (0, 0, .85), (1.0, 1.0, .1), bevel=.02)
    # corpo de pé, braço erguido, rosto quebrado
    sphere(st, (0, 0, 1.5), (.2, .16, .55))
    o = sphere(st, (0, 0, 1.0), (.3, .26, .25))
    sphere(st, (0, -.02, 2.15), (.11, .12, .13))
    along(st, (.18, 0, 1.85), (.35, -.1, 2.55), .05)
    for sx in (-1, 1):
        w = box(st, (sx*.35, .2, 2.0), (.55, .06, 1.0), (0, sx*-25, sx*-25), .02)
        if sx > 0: w.scale = (1, 1, .55); w.location.z = 1.75
    o = box(st, (.7, -.5, .1), (.55, .06, .5), (80, 0, 30), .02)   # pedaço de asa no chão
    crumble(o, .03, seed)
    return {}

@asset("vegetacao", fp=(3, 3))
def arvore_morta(m, seed=32):
    r = rnd(seed)
    bark = K.mat_wood("casca", (.045, .035, .028))
    def branch(p, d, L, rad, depth):
        q = p + d*L
        along(bark, p, q, rad, rad*.7, verts=8)
        if depth:
            for s in range(2 if depth > 1 else 3):
                nd = (d + Vector((r.uniform(-.9, .9), r.uniform(-.9, .9), r.uniform(-.1, .4)))).normalized()
                branch(q, nd, L*.72, rad*.62, depth-1)
    branch(Vector((0, 0, -.1)), Vector((.05, 0, 1)), 1.6, .14, 4)
    for k in range(4):
        a = math.radians(90*k + 20)
        along(bark, (0, 0, .2), (math.cos(a)*.6, math.sin(a)*.6, -.02), .07, .02, verts=6)
    # corda de enforcado
    along(K.mat_solid("corda", (.1, .08, .05)), (.9, .2, 2.4), (.9, .2, 1.6), .01, verts=4)
    torus(K.mat_solid("corda", (.1, .08, .05)), (.9, .2, 1.5), .08, .012, (90, 0, 0))
    return {}

@asset("props", fp=(2, 3))
def carroca_quebrada(m, seed=33):
    r = rnd(seed)
    box(m["wood"], (0, 0, .55), (1.1, 2.0, .08), (0, 12, 0), .01)
    for sx in (-1, 1):
        box(m["wood"], (sx*.55, 0, .75), (.06, 2.0, .35), (0, 12, 0), .01)
    for sy in (-1, 1):
        torus(m["wood_d"], (.65, sy*.65, .45), .42, .04, (0, 90, 0))
        for k in range(6):
            a = math.radians(30*k)
            along(m["wood_d"], (.65, sy*.65, .45), (.65, sy*.65 + math.cos(a)*.42, .45 + math.sin(a)*.42), .02, verts=5)
    torus(m["wood_d"], (-.6, .9, .05), .42, .04, (0, 0, 0))   # roda caída
    along(m["wood"], (0, -1.0, .5), (.1, -2.0, .05), .04, verts=6)
    box(m["sack"], (.0, .3, .75), (.5, .8, .3), (0, 10, 10), .05)
    return {}

@asset("props")
def poco(m, seed=34):
    st = K.mat_stone("pedra_poco", (.09, .085, .08), (.035, .033, .03), 3, .7)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.6, depth=.75, location=(0, 0, .37))
    o = bpy.context.object; o.data.materials.append(st)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.45, depth=.8, location=(0, 0, .4))
    h = bpy.context.object
    mod = o.modifiers.new("b", 'BOOLEAN'); mod.object = h; mod.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier="b")
    bpy.data.objects.remove(h)
    cyl(K.mat_solid("agua_negra", (.005, .006, .006), 0, .05), (0, 0, .3), .45, .02, verts=24)
    for sx in (-1, 1): box(m["wood"], (sx*.55, 0, 1.0), (.08, .08, 1.3), bevel=.01)
    cyl(m["wood"], (0, 0, 1.45), .06, 1.2, (0, 90, 0), 10)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=.95, depth=.45, location=(0, 0, 1.85), rotation=(0, 0, math.radians(45)))
    o = bpy.context.object; o.scale = (1, .65, 1); o.data.materials.append(m["wood_d"])
    along(K.mat_solid("corda", (.1, .08, .05)), (0, 0, 1.4), (0, 0, .75), .01, verts=4)
    cyl(m["wood"], (0, 0, .7), .1, .15, verts=10)
    return {}

@asset("props")
def bau_comum(m, seed=35):
    """Baú comum (madeira e ferro), fechado."""
    _chest(m, open_=False, tier=0); return {"estado": "fechado"}

@asset("props")
def bau_comum_aberto(m, seed=36):
    _chest(m, open_=True, tier=0); return {"estado": "aberto"}

@asset("props")
def bau_raro(m, seed=37):
    """Baú raro: ferro preto, cantoneiras de latão, selo da trombeta e brilho dourado."""
    _chest(m, open_=False, tier=1); return {"estado": "fechado", "emissivo": "fresta dourada"}

@asset("props")
def bau_raro_aberto(m, seed=38):
    _chest(m, open_=True, tier=1); return {"estado": "aberto", "emissivo": "ouro"}

@asset("props")
def bau_chefe(m, seed=39):
    """Baú de chefe: relicário de porcelana e ferro com correntes e brilho vermelho."""
    _chest(m, open_=False, tier=2); return {"estado": "fechado", "emissivo": "runas vermelhas"}

@asset("props")
def bau_chefe_aberto(m, seed=40):
    _chest(m, open_=True, tier=2); return {"estado": "aberto"}

def _chest(m, open_, tier):
    W, D, H = .8, .5, .4
    body = [m["wood"], m["wood_d"], m["porcelain"]][tier]
    trim = [m["iron"], m["brass"], m["iron"]][tier]
    box(body, (0, 0, H/2), (W, D, H), bevel=.015)
    for x in (-W/2 + .05, W/2 - .05, 0):
        box(trim, (x, 0, H/2), (.05, D + .02, H + .02), bevel=.004)
    box(trim, (0, -D/2 - .01, H - .08), (.12, .03, .14), bevel=.005)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box(trim, (sx*(W/2 - .02), sy*(D/2 - .02), H/2), (.06, .06, H + .03), bevel=.005)
    # tampa (meio cilindro)
    lid_rot = (-105 if open_ else 0)
    import bpy as _b
    _b.ops.mesh.primitive_cylinder_add(vertices=20, radius=D/2, depth=W, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
    lid = _b.context.object
    bm_cut = lid  # meio cilindro: escala e corta com boolean simples
    lid.scale = (1, 1, 1)
    lid.data.materials.append(body)
    pivot = _b.data.objects.new("pivo", None); _b.context.scene.collection.objects.link(pivot)
    pivot.location = (0, D/2, H)
    lid.parent = pivot; lid.location = (0, -D/2, 0); lid.scale = (1, 1, .55)
    for x in (-W/2 + .05, W/2 - .05, 0):
        o = cyl(trim, (x, -D/2, 0), D/2 + .012, .05, (0, 90, 0), 20); o.parent = pivot; o.location = (x, -D/2, 0); o.scale = (1, 1, .55)
    pivot.rotation_euler = (math.radians(lid_rot), 0, 0)
    if tier == 2:
        chain(m["iron"], (-W/2, -D/2 - .02, .05), (W/2, -D/2 - .02, H - .1), 9, .03)
        box(K.mat_emit("runa_vermelha", (1, .1, .05), 6), (0, -D/2 - .015, H/2 - .05), (.2, .01, .03), bevel=0)
    if open_:
        gold = K.mat_emit("brilho_ouro", (1, .7, .25), 3) if tier else K.mat_solid("moedas", (.35, .25, .08), .9, .3)
        box(gold, (0, 0, H - .02), (W - .1, D - .1, .02), bevel=0)
        r = rnd(5)
        for k in range(12):
            cyl(K.mat_solid("moeda", (.5, .36, .1), 1, .25), (r.uniform(-.3, .3), r.uniform(-.15, .15), H + .01 + k*.004), .035, .01, (r.uniform(-30, 30), r.uniform(-30, 30), 0), 10)
        point((0, -.1, H + .3), (1, .7, .3), 6 if tier else 2, .1)
    elif tier >= 1:
        box(K.mat_emit("fresta", (1, .7, .25) if tier == 1 else (1, .1, .05), 6), (0, -D/2 - .002, H + .01), (W - .1, .01, .015), bevel=0)

@asset("props", fp=(2, 2))
def ganchos_carne(m, seed=41):
    """Varal de ganchos com carcaças (Abatedouro Carniça)."""
    for sx in (-1, 1): cyl(m["iron"], (sx*.9, 0, 1.2), .04, 2.4, verts=8)
    cyl(m["iron"], (0, 0, 2.38), .04, 1.9, (0, 90, 0), 8)
    for k, x in enumerate((-.55, 0, .55)):
        chain(m["iron"], (x, 0, 2.35), (x, 0, 1.9), 4, .025)
        if k != 1:
            o = sphere(m["meat"], (x, 0, 1.4), (.2, .14, .45)); displace(o, .05, .15, seed+k, 1)
            for j in range(4): along(m["bone"], (x - .12, -.13, 1.2 + j*.13), (x + .12, -.13, 1.24 + j*.13), .013, verts=6)
        else:
            cyl(m["iron"], (x, 0, 1.75), .04, .15, (0, 90, 0), 8, r2=0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.6, depth=.01, location=(0, 0, .005))
    o = bpy.context.object; o.scale = (1.2, .7, 1); o.data.materials.append(m["blood"])
    return {}

@asset("props", fp=(2, 1))
def bancada_ferreiro(m, seed=42):
    """Bigorna, forja pequena e ferramentas (NPC ferreiro do acampamento)."""
    box(m["wood_d"], (0, 0, .2), (.35, .35, .4), bevel=.02)
    box(m["iron"], (0, 0, .5), (.55, .2, .18), bevel=.02)
    cyl(m["iron"], (.33, 0, .52), .08, .2, (0, 90, 0), 10, r2=0)
    cyl(m["brick"], (-.9, 0, .35), .35, .7, verts=12)
    cyl(m["coal"], (-.9, 0, .71), .3, .02, verts=12)
    sphere(K.mat_emit("brasa", (1, .35, .06), 8), (-.9, 0, .72), (.25, .25, .04))
    point((-.9, 0, 1.0), (1, .4, .1), 60, .2)
    along(m["wood"], (.1, .08, .6), (.2, -.2, .62), .015, verts=5)
    box(m["iron"], (.22, -.24, .62), (.08, .04, .05), bevel=.005)
    return {"luz": "quente"}

@asset("props")
def placa_aviso(m, seed=43):
    cyl(m["wood"], (0, 0, .75), .04, 1.5, verts=6)
    for k, (z, rz, txt) in enumerate([(1.3, 20, 1), (1.0, -25, 1)]):
        box(m["wood"], (.3*math.cos(math.radians(rz)), .3*math.sin(math.radians(rz)), z), (.7, .04, .18), (0, 0, rz), .01)
    sphere(m["bone"], (0, 0, 1.55), (.08, .09, .08), segs=10)
    return {}

@asset("props", fp=(2, 2))
def entulho(m, seed=44):
    r = rnd(seed)
    for k in range(16):
        mat = r.choice([m["brick"], m["brick"], m["stone"], m["wood_d"]])
        o = box(mat, (r.uniform(-.6, .6), r.uniform(-.6, .6), r.uniform(.05, .3)), (r.uniform(.12, .35), r.uniform(.1, .25), r.uniform(.07, .18)), (r.uniform(-40, 40), r.uniform(-40, 40), r.uniform(0, 180)), .01)
    along(m["iron"], (-.6, .2, .05), (.5, -.3, .5), .02, verts=6)
    return {}

@asset("props")
def gaiola_suspensa(m, seed=45):
    """Gaiola de ferro pendurada num poste, com ossos dentro."""
    along(m["wood"], (0, 0, 0), (0, 0, 3.0), .07, verts=8)
    along(m["wood"], (0, 0, 2.9), (.9, 0, 2.9), .05, verts=6)
    chain(m["iron"], (.85, 0, 2.85), (.85, 0, 2.3), 5, .025)
    for k in range(10):
        a = math.radians(36*k)
        along(m["iron"], (.85 + math.cos(a)*.3, math.sin(a)*.3, 1.2), (.85 + math.cos(a)*.25, math.sin(a)*.25, 2.2), .01, verts=4)
    for z in (1.2, 1.7, 2.2): torus(m["iron"], (.85, 0, z), .3 if z < 2 else .25, .012)
    sphere(m["bone"], (.85, 0, 1.3), (.08, .09, .08), segs=10)
    for k in range(3): along(m["bone"], (.7, -.1 + k*.1, 1.23), (1.0, 0 + k*.05, 1.25), .015, verts=5)
    return {}

# ================================================================ DUNGEON: andar 1 Porão do Matadouro
@asset("dungeon", fp=(2, 2), dungeon=True)
def caldeira_vapor(m, seed=50):
    cyl(m["rust"], (0, 0, .8), .55, 1.6, verts=24)
    sphere(m["rust"], (0, 0, 1.6), (.55, .55, .25))
    for z in (.3, .8, 1.3): torus(m["iron"], (0, 0, z), .56, .03)
    for k in range(10):
        a = math.radians(36*k)
        sphere(m["brass"], (math.cos(a)*.565, math.sin(a)*.565, .8), (.025, .025, .025), segs=6)
    box(m["iron"], (0, -.56, .35), (.4, .05, .3), bevel=.01)
    box(K.mat_emit("fornalha", (1, .35, .06), 6), (0, -.585, .35), (.3, .01, .2), bevel=0)
    point((0, -.9, .4), (1, .4, .1), 40, .2)
    along(m["brass"], (0, 0, 1.8), (0, 0, 2.6), .08)
    along(m["brass"], (0, 0, 2.6), (.7, .3, 2.8), .08)
    cyl(m["brass"], (.4, -.45, 1.2), .1, .05, (90, 0, 20), 16)
    for k in range(4):  # vapor
        o = sphere(K.mat_solid("vapor", (.25, .25, .25), 0, 1), (.1 + k*.08, -.1, 2.0 + k*.25), (.12 + k*.05, .12 + k*.05, .1 + k*.04))
        mtl = o.data.materials[0]
    return {"emissivo": "fornalha", "luz": "quente"}

@asset("dungeon", fp=(2, 1), dungeon=True)
def mesa_acougue(m, seed=51):
    box(m["wood_d"], (0, 0, .85), (1.4, .7, .1), bevel=.01)
    for sx in (-1, 1):
        for sy in (-1, 1): box(m["iron"], (sx*.6, sy*.28, .4), (.06, .06, .8), bevel=.005)
    o = sphere(m["meat"], (.1, 0, .97), (.35, .2, .1)); displace(o, .03, .1, seed, 1)
    box(m["iron"], (-.4, .1, .91), (.35, .12, .01), (0, 0, 20), 0)   # cutelo
    box(m["wood"], (-.62, .16, .92), (.12, .04, .03), (0, 0, 20), 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=.5, depth=.01, location=(0, -.3, .005))
    o = bpy.context.object; o.scale = (1.3, .8, 1); o.data.materials.append(m["blood"])
    cyl(m["rust"], (.75, .2, .3), .22, .6, verts=16)
    return {}

@asset("dungeon", fp=(2, 1), dungeon=True)
def canos_parede(m, seed=52):
    for k, (z, r_) in enumerate([(.4, .1), (.9, .07), (1.6, .12)]):
        cyl(m["brass"] if k != 2 else m["rust"], (0, 0, z), r_, 1.6, (0, 90, 0), 14)
        for x in (-.6, .6): torus(m["iron"], (x, 0, z), r_ + .01, .015, (0, 90, 0))
    cyl(m["brass"], (.2, -.12, .9), .12, .04, (90, 0, 0), 12)
    for k in range(4): box(m["iron"], (.2, -.15, .9), (.2, .02, .02), (0, 45*k, 0), 0)
    return {}

@asset("dungeon", fp=(6, 6), dungeon=True, samples=48)
def moedor_vapor(m, seed=53):
    """Porão do Matadouro: o grande moedor de carne a vapor (peça central de sala)."""
    r = rnd(seed)
    box(m["iron"], (0, 0, .2), (3.0, 3.0, .4), bevel=.04)
    cyl(m["rust"], (0, 0, 1.4), 1.0, 2.0, verts=32)
    cyl(m["rust"], (0, 0, 2.6), 1.2, .5, verts=32, r2=1.0)
    for z in (.6, 1.4, 2.2): torus(m["iron"], (0, 0, z), 1.02, .05)
    # boca do funil com dentes
    for k in range(12):
        a = math.radians(30*k)
        cyl(m["iron"], (math.cos(a)*1.05, math.sin(a)*1.05, 2.95), .06, .3, (math.degrees(math.sin(a))*0 + 25*math.sin(a), -25*math.cos(a), 0), 5, r2=0)
    cyl(K.mat_emit("carne_viva", (.5, .03, .02), 1.2), (0, 0, 2.86), .95, .02, verts=32)
    # engrenagens laterais
    for sx in (-1, 1):
        cyl(m["brass"], (sx*1.25, 0, 1.6), .55, .12, (0, 90, 0), 24)
        for k in range(12):
            a = math.radians(30*k)
            box(m["brass"], (sx*1.25, math.cos(a)*.6, 1.6 + math.sin(a)*.6), (.12, .12, .12), (math.degrees(a), 0, 0), .005)
    # bica de saída com carne moída e sangue
    along(m["rust"], (0, -1.0, .9), (0, -1.6, .6), .25, .2, verts=16)
    o = sphere(m["meat"], (0, -1.8, .2), (.5, .45, .2)); displace(o, .06, .08, seed, 2)
    bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1.6, depth=.01, location=(0, -1.6, .005))
    o = bpy.context.object; o.scale = (1.2, .8, 1); o.data.materials.append(m["blood"])
    # caldeira e canos
    for sx in (-1, 1):
        along(m["brass"], (sx*.9, .8, 2.2), (sx*1.6, 1.6, 3.6), .1)
    for k in range(5):
        sphere(K.mat_solid("vapor", (.3, .3, .3), 0, 1), (r.uniform(-1, 1), 1.6 + r.uniform(-.2, .2), 3.7 + k*.3), (.25 + k*.06,)*3)
    for k in range(6):  # correntes pendentes
        a = math.radians(60*k + 30)
        chain(m["iron"], (math.cos(a)*1.4, math.sin(a)*1.4, 3.6), (math.cos(a)*1.45, math.sin(a)*1.45, 2.3), 7, .03)
    point((0, -1.4, 1.2), (1, .2, .08), 120, .6)
    return {"chefe": 1, "emissivo": "carne viva no funil"}

# ================================================================ DUNGEON: andar 2 Ossário das Carpideiras
@asset("dungeon", dungeon=True)
def pilha_cranios(m, seed=54):
    r = rnd(seed)
    pts = []
    for layer in range(4):
        n = 9 - layer*2
        for k in range(n):
            a = math.radians(360*k/n + layer*20); rad = .45 - layer*.11
            pts.append((math.cos(a)*rad, math.sin(a)*rad, .07 + layer*.13))
    for (x, y, z) in pts:
        sphere(m["bone"], (x, y, z), (.08, .09, .08), segs=12)
        sphere(K.mat_solid("orbita", (0, 0, 0)), (x + .025, y - .07, z + .01), (.02, .012, .022), segs=6)
        sphere(K.mat_solid("orbita", (0, 0, 0)), (x - .025, y - .07, z + .01), (.02, .012, .022), segs=6)
    candle((.0, -.55, .0), .2); candle((.15, -.5, 0), .12)
    return {}

@asset("dungeon", dungeon=True)
def candelabro_ossos(m, seed=55):
    along(m["bone"], (0, 0, 0), (0, 0, 1.5), .04, verts=8)
    sphere(m["bone"], (0, 0, 1.55), (.1, .11, .1), segs=12)
    for k in range(5):
        a = math.radians(72*k)
        along(m["bone"], (0, 0, 1.1), (math.cos(a)*.35, math.sin(a)*.35, 1.25), .02, verts=6)
        candle((math.cos(a)*.35, math.sin(a)*.35, 1.25), .12)
    for k in range(3):
        a = math.radians(120*k)
        along(m["bone"], (0, 0, .2), (math.cos(a)*.3, math.sin(a)*.3, 0), .025, verts=6)
    return {"luz": "velas"}

@asset("dungeon", fp=(2, 1), dungeon=True)
def sarcofago(m, seed=56):
    st = K.mat_stone("pedra_sarcofago", (.09, .088, .085), (.03, .03, .03), 3, .5)
    box(st, (0, 0, .35), (2.0, .8, .7), bevel=.03)
    o = box(st, (.15, -.1, .78), (1.9, .85, .15), (0, 0, 8), .03)
    sphere(st, (-.55, -.05, .92), (.15, .13, .1), segs=12)
    sphere(st, (.25, -.05, .9), (.55, .2, .08), segs=12)
    box(m["iron"], (0, -.41, .5), (2.0, .02, .05), bevel=0)
    for k in range(5): candle((-.9 + k*.4, -.5, 0), .1 + (k % 2)*.06)
    return {}

@asset("dungeon", fp=(2, 1), dungeon=True)
def monge_emparedado(m, seed=57):
    """Nicho com um monge emparedado (as Carpideiras), parede meio aberta."""
    st = m["stone_d"]
    box(st, (0, .1, 1.2), (1.2, .4, 2.4), bevel=.02)
    box(K.mat_solid("nicho", (.004, .003, .003)), (0, -.02, 1.1), (.6, .2, 1.6), bevel=0)
    robe = K.mat_cloth("habito", (.05, .04, .035))
    o = sphere(robe, (0, -.05, .95), (.22, .14, .75)); displace(o, .03, .15, seed, 1)
    sphere(K.mat_cloth("capuz", (.04, .03, .028)), (0, -.08, 1.72), (.15, .14, .17))
    sphere(m["bone"], (0, -.17, 1.68), (.08, .06, .1), segs=10)
    for k in range(6):
        o = box(m["brick"], (-.25 + (k % 3)*.25, -.12, .3 + (k//3)*.2), (.24, .14, .19), (0, 0, 0), .01)
    for k in range(2): candle((-.4 + k*.8, -.35, 0), .14)
    box(m["red_cloth"], (0, -.12, 2.0), (.65, .02, .25), bevel=0)
    return {}

@asset("chefes", fp=(6, 6), dungeon=True, samples=48)
def arena_carpideiras(m, seed=58):
    """Chefe 2 (Ossário): trono de ossos das Carpideiras com mar de velas."""
    r = rnd(seed)
    st = m["stone_d"]
    for k in range(3):
        box(st, (0, .3 + k*.2, .1 + k*.2), (3.4 - k*.6, 2.6 - k*.4, .2), bevel=.02)
    # trono
    box(m["bone"], (0, .6, .9), (1.0, .8, .2), bevel=.02)
    for k in range(9):
        along(m["bone"], (-.5 + k*.125, .95, .9), (-.5 + k*.125 + r.uniform(-.05, .05), 1.0, 2.6 + math.sin(k/8*math.pi)*.6), .035, verts=6)
    for k in range(7):
        a = math.radians(180*k/6)
        sphere(m["bone"], (math.cos(a)*.6, 1.0, 2.4 + math.sin(a)*.9), (.11, .12, .11), segs=12)
    for sx in (-1, 1):
        along(m["bone"], (sx*.5, .3, .7), (sx*.5, .9, .8), .05, verts=6)
        sphere(m["bone"], (sx*.5, .25, .8), (.1, .11, .1), segs=12)
    # véus pendurados
    for sx in (-1, 1):
        o = box(K.mat_cloth("veu", (.06, .055, .05)), (sx*1.2, 1.0, 1.5), (.6, .02, 2.6), (0, 0, sx*10), 0); displace(o, .05, .3, seed+sx, 3)
    # mar de velas
    for k in range(40):
        a = r.uniform(0, 2*math.pi); rad = r.uniform(1.2, 2.2)
        candle((math.cos(a)*rad, math.sin(a)*rad*.8 - .2, 0), r.uniform(.08, .25), light=(k % 4 == 0))
    # círculo de sangue
    torus(K.mat_emit("runa_sangue", (.6, .03, .02), 2.0), (0, -.6, .01), 1.0, .025, (0, 0, 0))
    point((0, -.2, 1.5), (1, .45, .18), 60, .6)
    return {"chefe": 2, "luz": "velas"}

# ================================================================ DUNGEON: andar 3 Câmara da Trombeta
@asset("dungeon", fp=(2, 2), dungeon=True)
def pilar_porcelana(m, seed=59):
    box(m["iron"], (0, 0, .15), (.9, .9, .3), bevel=.02)
    o = cyl(m["porcelain"], (0, 0, 1.8), .3, 3.0, verts=24)
    for z in (.4, 1.4, 2.4, 3.3): torus(m["iron"], (0, 0, z), .31, .04)
    for k in range(4):
        a = math.radians(90*k + 45)
        along(m["iron"], (math.cos(a)*.32, math.sin(a)*.32, .3), (math.cos(a)*.32, math.sin(a)*.32, 3.3), .025, verts=6)
    box(m["iron"], (0, 0, 3.45), (.9, .9, .25), bevel=.02)
    return {}

@asset("dungeon", fp=(2, 2), dungeon=True)
def anjo_porcelana_caido(m, seed=60):
    """Estátua angelical de porcelana partida no chão, máscara rachada."""
    r = rnd(seed)
    sphere(m["porcelain"], (0, 0, .25), (.6, .25, .22))
    sphere(m["porcelain"], (-.75, .05, .25), (.16, .18, .2))
    box(K.mat_solid("venda", (.05, .01, .01), 0, .8), (-.75, -.12, .3), (.2, .02, .06), bevel=0)
    for sx in (-1, 1):
        o = box(m["porcelain"], (.1, sx*.5, .15), (1.0, .5, .05), (sx*12, 0, sx*10), .02)
    for k in range(10):
        o = box(m["porcelain"], (r.uniform(-1, 1), r.uniform(-.8, .8), .03), (r.uniform(.05, .15),)*2 + (.03,), (0, 0, r.uniform(0, 90)), .005)
    torus(K.mat_solid("halo_ferro", (.06, .055, .05), .9, .4), (-1.05, .2, .03), .25, .025)
    return {}

@asset("dungeon", dungeon=True)
def braseiro_ferro(m, seed=61):
    for k in range(3):
        a = math.radians(120*k)
        along(m["iron"], (math.cos(a)*.3, math.sin(a)*.3, 0), (math.cos(a)*.15, math.sin(a)*.15, .8), .025, verts=6)
    cyl(m["iron"], (0, 0, .85), .3, .2, verts=16, r2=.2)
    cyl(m["coal"], (0, 0, .94), .27, .02, verts=16)
    flame((0, 0, .95), 1.0)
    return {"luz": "quente"}

@asset("chefes", fp=(6, 6), dungeon=True, samples=48)
def arena_trombeta(m, seed=62):
    """Chefe 3: a Trombeta Calada, enorme trombeta de ferro e porcelana sobre
    altar, presa por correntes, com halo de ferro partido."""
    r = rnd(seed)
    st = m["stone_d"]
    for k in range(3):
        cyl(st, (0, 0, .1 + k*.2), 2.0 - k*.45, .2, verts=8)
    box(m["porcelain"], (0, 0, 1.0), (1.2, .8, .6), bevel=.03)
    # trombeta: tubo + campânula, inclinada
    import bpy as _b
    path = [Vector((-.6, 0, 1.4)), Vector((0, 0, 1.6)), Vector((.6, 0, 1.8)), Vector((1.2, 0, 2.1))]
    for a, b in zip(path, path[1:]): along(m["brass"], a, b, .08, verts=14)
    _b.ops.mesh.primitive_cone_add(vertices=32, radius1=.12, radius2=.85, depth=1.0, location=(1.6, 0, 2.3), rotation=(0, math.radians(62), 0))
    o = _b.context.object; o.data.materials.append(m["brass"])
    torus(m["iron"], (2.05, 0, 2.53), .85, .04, (0, 62, 0))
    # rachadura de porcelana enrolada no tubo
    for k in range(4): torus(m["porcelain"], (-.4 + k*.4, 0, 1.47 + k*.1), .1, .03, (0, 70, 0))
    # bocal com brilho
    sphere(K.mat_emit("brilho_sagrado", (1, .82, .45), 10), (1.75, 0, 2.35), (.4, .4, .4))
    point((1.9, -.3, 2.4), (1, .8, .45), 200, .5)
    # halo partido flutuando
    for k in range(7):
        a = math.radians(40*k + 10)
        box(K.mat_solid("halo_ferro", (.06, .055, .05), .9, .4), (math.cos(a)*1.3, math.sin(a)*.3 + .4, 3.4 + math.sin(a)*1.3*.6), (.4, .06, .08), (0, -math.degrees(a) + 90, 0), .01)
    # correntes para os 4 cantos
    for sx in (-1, 1):
        for sy in (-1, 1):
            chain(m["iron"], (sx*.5, sy*.3, 1.3), (sx*1.8, sy*1.8, .1), 12, .035)
            cyl(m["iron"], (sx*1.8, sy*1.8, .1), .08, .2, verts=8)
    # velas e penas espalhadas
    for k in range(14):
        a = r.uniform(0, 2*math.pi); rad = r.uniform(1.3, 2.0)
        candle((math.cos(a)*rad, math.sin(a)*rad, .2 if rad < 1.6 else 0), r.uniform(.08, .2), light=(k % 4 == 0))
    feather = K.mat_solid("pena", (.3, .28, .24), 0, .7)
    for k in range(12):
        box(feather, (r.uniform(-2, 2), r.uniform(-2, 2), .02), (.2, .05, .005), (0, 0, r.uniform(0, 180)), 0)
    return {"chefe": 3, "emissivo": "luz sagrada na campânula"}

# ================================================================ portas e escadas (dungeon)
@asset("dungeon", fp=(2, 1), dungeon=True)
def portao_ferro(m, seed=63):
    st = m["stone_d"]
    for sx in (-1, 1): box(st, (sx*.9, 0, 1.4), (.4, .5, 2.8), bevel=.02)
    for k in range(9):
        a = math.radians(180*k/8)
        box(st, (math.cos(a)*.75, 0, 2.3 + math.sin(a)*.6), (.3, .5, .2), (0, -math.degrees(a) + 90, 0), .02)
    for k in range(6):
        cyl(m["iron"], (-.55 + k*.22, 0, 1.25), .02, 2.5, verts=6)
        cyl(m["iron"], (-.55 + k*.22, 0, .02), .04, .1, verts=4, r2=0)
    for z in (.6, 1.6): box(m["iron"], (0, 0, z), (1.4, .05, .06), bevel=0)
    box(K.mat_solid("abismo", (.002, .001, .001)), (0, .2, 1.3), (1.4, .1, 2.6), bevel=0)
    return {}

@asset("dungeon", fp=(2, 3), dungeon=True)
def escada_descida(m, seed=64):
    st = m["stone_d"]
    for sx in (-1, 1): box(st, (sx*.8, 0, .3), (.3, 2.0, .6), bevel=.02)
    for k in range(7):
        box(st, (0, -.9 + k*.28, -.0 + .3 - k*.0 - 0.04*k), (1.3, .3, .06), bevel=.01)
    box(K.mat_solid("abismo", (.002, .001, .001)), (0, .3, .0), (1.3, 1.2, .02), bevel=0)
    for sx in (-1, 1): candle((sx*.8, -.9, .6), .15)
    return {}

# ================================================================ DECALQUES (chão, sem sombra)
def _pool(mat, rx, ry, seed, n=5, z=.004):
    r = rnd(seed)
    for k in range(n):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=1, depth=.005, location=(r.uniform(-rx*.4, rx*.4), r.uniform(-ry*.4, ry*.4), z))
        o = bpy.context.object; s_ = r.uniform(.3, .7)
        o.scale = (rx*s_, ry*s_*r.uniform(.6, 1), 1); o.data.materials.append(mat)
        displace(o, .0, .5, seed+k, 0)

@asset("decalques")
def poca_sangue(m, seed=70):
    _pool(m["blood"], .6, .5, seed, 6); return {}

@asset("decalques")
def poca_sangue_rastro(m, seed=71):
    r = rnd(seed)
    for k in range(9):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1, depth=.005, location=(-.8 + k*.2, r.uniform(-.05, .05), .004))
        o = bpy.context.object; o.scale = (.14, .08 + k*.012, 1); o.data.materials.append(m["blood"])
    _pool(m["blood"], .4, .35, seed, 3)
    return {}

@asset("decalques")
def poca_agua(m, seed=72):
    _pool(K.mat_solid("agua", (.01, .012, .014), 0, .02), .7, .55, seed, 5); return {}

@asset("decalques")
def ossos_espalhados(m, seed=73):
    r = rnd(seed)
    for k in range(9):
        a = Vector((r.uniform(-.5, .5), r.uniform(-.4, .4), .02)); d = Vector((r.uniform(-1, 1), r.uniform(-1, 1), 0)).normalized()
        along(m["bone"], a, a + d*r.uniform(.15, .35), .018, verts=6)
    sphere(m["bone"], (.1, -.1, .07), (.08, .09, .08), segs=12)
    return {}

@asset("decalques")
def folhas_papeis(m, seed=74):
    r = rnd(seed)
    paper = K.mat_solid("papel", (.25, .22, .17), 0, .9); leaf = K.mat_solid("folha_seca", (.08, .045, .02), 0, .8)
    for k in range(18):
        box(paper if k % 3 == 0 else leaf, (r.uniform(-.6, .6), r.uniform(-.5, .5), .004), (r.uniform(.05, .18), r.uniform(.04, .12), .003), (r.uniform(-5, 5), r.uniform(-5, 5), r.uniform(0, 180)), 0)
    return {}

@asset("decalques", dungeon=True)
def ralo_ferro(m, seed=75):
    box(m["iron"], (0, 0, .005), (.5, .5, .01), bevel=.005)
    for k in range(6): box(K.mat_solid("abismo", (.002, .001, .001)), (-.2 + k*.08, 0, .011), (.03, .42, .002), bevel=0)
    _pool(m["blood"], .5, .4, seed, 3, .002)
    return {}

# ================================================================ Campos de Cinza e Vala da Grande Batalha
def corpo(m, loc, rot_z, seed, burnt=False, helmet=True):
    """Soldado morto deitado (Grande Batalha): uniforme, capacete, membros tortos."""
    r = rnd(seed); x, y, z = loc
    uni = K.mat_cloth("uniforme_queimado" if burnt else "uniforme", (.025, .022, .02) if burnt else (.06, .065, .05), 9.0)
    skin = K.mat_solid("pele_morta", (.09, .08, .07), 0, .7) if not burnt else K.mat_solid("carvao_corpo", (.02, .015, .012), 0, .9)
    piv = bpy.data.objects.new("corpo", None); bpy.context.scene.collection.objects.link(piv)
    piv.location = (x, y, z); piv.rotation_euler = (0, 0, math.radians(rot_z))
    sphere(uni, (0, 0, .11), (.17, .28, .1), piv)
    sphere(uni, (0, -.38, .09), (.14, .14, .09), piv)
    sphere(skin, (0, .38, .1), (.08, .09, .08), piv)
    if helmet: sphere(K.mat_metal("capacete", (.05, .055, .045), .5, seed), (r.uniform(-.05, .05), .4, .15), (.12, .12, .06), piv)
    for sx in (-1, 1):
        a = Vector((sx*.17, .18, .1)); b = a + Vector((sx*r.uniform(.15, .35), r.uniform(-.1, .3), -.05))
        along(uni, a, b, .045, parent=piv)
        along(uni, (sx*.08, -.45, .07), (sx*r.uniform(.1, .3), -.85, .05), .055, parent=piv)
        sphere(K.mat_solid("bota", (.012, .01, .009), 0, .6), (sx*r.uniform(.1, .3), -.9, .06), (.05, .08, .05), piv)
    return piv

@asset("props", fp=(2, 2))
def pilha_mortos(m, seed=80):
    """Pilha de mortos da Grande Batalha, alimento do Andras."""
    r = rnd(seed)
    for k in range(7):
        corpo(m, (r.uniform(-.4, .4), r.uniform(-.3, .3), .02 + (k//3)*.16), r.uniform(0, 360), seed+k, burnt=k % 3 == 0)
    _pool(m["blood"], .9, .7, seed, 4)
    return {}

@asset("props", fp=(2, 1))
def soldado_morto(m, seed=81):
    corpo(m, (0, 0, .0), 70, seed); _pool(m["blood"], .5, .35, seed, 3)
    along(m["iron"], (-.6, -.3, .03), (.4, -.5, .05), .02, verts=6)    # fuzil
    box(m["wood_d"], (-.45, -.27, .04), (.3, .07, .05), (0, 0, -11), .01)
    return {}

@asset("paredes", walls=True)
def trilho_bonde(m, seed=82):
    """Trilhos do bonde da linha 7 (segmento de 1 tile, enterrado na cinza)."""
    L = T
    for k in range(2):
        box(m["dark_stone"], (-L/2 + L/4 + k*L/2, 0, .02), (.12, 1.1, .04), bevel=.01)
    for sy in (-1, 1):
        box(m["rust"], (0, sy*.36, .06), (L + .002, .05, .07), bevel=.003)
        box(m["iron"], (0, sy*.36, .1), (L + .002, .07, .02), bevel=.003)
    return {"nota": "segmento contínuo: encaixe lado a lado ao longo do eixo"}

@asset("predios", fp=(8, 4), samples=48)
def bonde_queimado(m, seed=83):
    """Bonde da linha 7 tombado e queimado nos Campos de Cinza."""
    r = rnd(seed)
    burnt = K.mat_metal("lataria_queimada", (.03, .028, .026), .8, 7.0, .7)
    paint = K.mat_metal("pintura_bonde", (.16, .1, .03), .55, 8.0, .6)
    piv = bpy.data.objects.new("bonde", None); bpy.context.scene.collection.objects.link(piv)
    L, W, H = 5.0, 2.0, 2.4
    box(burnt, (0, 0, .5), (W, L, .4), bevel=.04, parent=piv)
    box(paint, (0, 0, 1.1), (W, L, .8), bevel=.04, parent=piv)
    for sx in (-1, 1):
        for k in range(6):
            box(burnt, (sx*W/2, -L/2 + .4 + k*.84, 1.85), (.06, .12, .7), bevel=.01, parent=piv)
        box(K.mat_solid("interior_escuro", (.004, .003, .003)), (sx*(W/2 - .05), 0, 1.85), (.05, L - .4, .7), bevel=0, parent=piv)
    box(burnt, (0, 0, 2.3), (W + .1, L + .1, .12), bevel=.04, parent=piv)
    box(burnt, (0, -L/2 - .1, 1.4), (W*.9, .2, 1.8), bevel=.06, parent=piv)
    box(K.mat_solid("placa_linha", (.3, .27, .2), 0, .6), (0, -L/2 - .21, 2.15), (.7, .02, .28), bevel=0, parent=piv)
    box(K.mat_solid("numero", (.02, .02, .02)), (0, -L/2 - .22, 2.15), (.12, .01, .2), bevel=0, parent=piv)
    along(m["iron"], (0, .5, 2.36), (.3, .5, 3.2), .025, parent=piv)          # alavanca do pantógrafo
    for sy in (-1, 1):
        for sx in (-1, 1):
            cyl(m["iron"], (sx*.75, sy*1.6, .3), .32, .12, (0, 90, 0), 16, parent=piv)
    piv.rotation_euler = (0, math.radians(-78), math.radians(15)); piv.location = (0, 0, W/2 - .1)
    # brasas e fumaça
    for k in range(4):
        sphere(K.mat_emit("brasa", (1, .3, .05), 3), (r.uniform(-.8, .8), r.uniform(-2, 2), .05), (.12, .12, .04))
    point((.3, -.5, .8), (1, .35, .1), 40, .4)
    for k in range(5):
        o = box(m["dark_stone"], (r.uniform(-2, 2), r.uniform(-3, 3), .04), (.3, .2, .08), (r.uniform(-20, 20), 0, r.uniform(0, 90)), .01)
    return {"emissivo": "brasas"}

@asset("props", fp=(2, 2))
def cratera_cinza(m, seed=84):
    """Cratera de bomba com estilhaços e uma bandeira da Vigília rasgada."""
    r = rnd(seed)
    for k in range(14):
        a = math.radians(360*k/14)
        o = sphere(K.mat_stone("terra_queimada", (.07, .066, .062), (.015, .014, .013), 3), (math.cos(a)*.75, math.sin(a)*.6, .05), (.25, .18, .1)); displace(o, .04, .15, seed+k, 1)
    cyl(K.mat_solid("fundo_cratera", (.006, .005, .005), 0, .9), (0, 0, .005), .6, .01, verts=24)
    cyl(m["wood_d"], (.5, .3, .6), .025, 1.2, (12, -8, 0), 6)
    o = box(K.mat_cloth("bandeira_vigilia", (.03, .05, .08), 11.0), (.75, .35, 1.0), (.5, .02, .35), (0, 0, 10), 0); displace(o, .04, .2, seed, 3)
    for k in range(6):
        box(m["rust"], (r.uniform(-.8, .8), r.uniform(-.7, .7), .03), (r.uniform(.05, .2), .05, .02), (0, 0, r.uniform(0, 180)), .003)
    return {}

@asset("chefes", fp=(8, 8), dungeon=True, samples=48)
def arena_vala(m, seed=85):
    """Chefe 1: a Vala da Grande Batalha, fosso de cadáveres no porão do abatedouro,
    covil do Andras, o General Partido. Montes de mortos, estandartes rasgados e ganchos."""
    r = rnd(seed)
    st = m["stone_d"]
    # borda do fosso (anel de pedra e tijolo quebrado)
    for k in range(16):
        a = math.radians(360*k/16)
        o = box(m["brick"], (math.cos(a)*2.4, math.sin(a)*2.4, .25), (.9, .45, .5 + r.uniform(-.2, .3)), (0, 0, math.degrees(a) + 90), .01)
        crumble(o, .04, seed+k)
    cyl(K.mat_solid("lama_sangue", (.03, .006, .004), 0, .25), (0, 0, .01), 2.3, .02, verts=32)
    # montes de mortos
    for k in range(22):
        a = r.uniform(0, 2*math.pi); rad = r.uniform(.3, 2.0)
        corpo(m, (math.cos(a)*rad, math.sin(a)*rad, .02 + r.uniform(0, .25)), r.uniform(0, 360), seed+20+k, burnt=k % 4 == 0)
    # estandartes da Grande Batalha cravados
    for k, a in enumerate((40, 160, 280)):
        aa = math.radians(a); x, y = math.cos(aa)*1.7, math.sin(aa)*1.7
        cyl(m["wood_d"], (x, y, 1.1), .03, 2.2, (r.uniform(-15, 15), r.uniform(-15, 15), 0), 6)
        o = box(K.mat_cloth("estandarte", (.1, .015, .01) if k != 1 else (.03, .05, .08), 12.0 + k), (x + .25, y, 1.8), (.5, .02, .8), (0, 0, 0), 0)
        displace(o, .05, .2, seed+k, 3)
    # ganchos e correntes pendurados do teto (cortados no alto)
    for k in range(5):
        a = math.radians(72*k + 15); x, y = math.cos(a)*1.2, math.sin(a)*1.2
        chain(m["iron"], (x, y, 3.6), (x, y, 2.0), 10, .03)
        cyl(m["iron"], (x, y, 1.9), .04, .2, (0, 90, 0), 8, r2=0)
    # ossos e crânios na borda
    for k in range(18):
        a = r.uniform(0, 2*math.pi); rad = r.uniform(2.0, 2.6)
        sphere(m["bone"], (math.cos(a)*rad, math.sin(a)*rad, .55), (.07, .08, .07), segs=10)
    # braseiros nos quatro cantos
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(m["iron"], (sx*2.9, sy*2.9, .5), .25, .15, verts=12)
            cyl(m["iron"], (sx*2.9, sy*2.9, .22), .04, .45, verts=8)
            flame((sx*2.9, sy*2.9, .58), .9)
    point((0, 0, 2.5), (.8, .1, .05), 80, 1.0)
    return {"chefe": 1, "boss": "Andras, o General Partido"}

# ================================================================ VEGETAÇÃO
def _twigs(mat, base, n, L, seed, spread=1.0, up=.6):
    r = rnd(seed)
    for k in range(n):
        d = Vector((r.uniform(-spread, spread), r.uniform(-spread, spread), r.uniform(up, 1))).normalized()
        a = Vector(base); b = a + d*L*r.uniform(.6, 1.1)
        along(mat, a, b, .012, .003, verts=4)
        if k % 2 == 0:
            d2 = (d + Vector((r.uniform(-.8, .8), r.uniform(-.8, .8), .2))).normalized()
            m_ = a.lerp(b, .55); along(mat, m_, m_ + d2*L*.45, .007, .002, verts=4)

@asset("vegetacao")
def arbusto_seco(m, seed=90):
    """Arbusto seco e espinhento."""
    br = K.mat_wood("galho_seco", (.06, .045, .03))
    _twigs(br, (0, 0, 0), 26, .7, seed)
    leaf = K.mat_solid("folha_morta", (.07, .045, .02), 0, .8)
    r = rnd(seed)
    for k in range(20):
        sphere(leaf, (r.uniform(-.3, .3), r.uniform(-.3, .3), r.uniform(.25, .6)), (.04, .03, .015), segs=6)
    return {}

@asset("vegetacao")
def arbusto_seco_2(m, seed=91):
    br = K.mat_wood("galho_seco", (.06, .045, .03))
    _twigs(br, (0, 0, 0), 18, 1.0, seed, .6, .7)
    _twigs(br, (.2, .1, 0), 10, .5, seed+1)
    return {}

@asset("vegetacao")
def mato_seco(m, seed=92):
    """Tufo de capim seco (espalhe vários pelo mapa)."""
    r = rnd(seed)
    grass = [K.mat_solid("capim_seco", (.11, .09, .045), 0, .8), K.mat_solid("capim_escuro", (.05, .045, .025), 0, .8)]
    for k in range(70):
        a = Vector((r.gauss(0, .12), r.gauss(0, .12), 0))
        d = Vector((r.uniform(-.5, .5), r.uniform(-.5, .5), 1)).normalized()
        along(grass[k % 2], a, a + d*r.uniform(.2, .45), .008, .001, verts=3)
    return {}

@asset("vegetacao")
def mato_seco_2(m, seed=93):
    r = rnd(seed)
    grass = [K.mat_solid("capim_seco", (.11, .09, .045), 0, .8), K.mat_solid("capim_escuro", (.05, .045, .025), 0, .8)]
    for c in range(3):
        cx, cy = r.uniform(-.35, .35), r.uniform(-.25, .25)
        for k in range(35):
            a = Vector((cx + r.gauss(0, .07), cy + r.gauss(0, .07), 0))
            d = Vector((r.uniform(-.6, .6), r.uniform(-.6, .6), 1)).normalized()
            along(grass[k % 2], a, a + d*r.uniform(.12, .3), .007, .001, verts=3)
    return {}

@asset("vegetacao", fp=(3, 3))
def arvore_morta_2(m, seed=94):
    """Árvore morta torta, mais baixa e larga."""
    return _tree(m, seed, 1.2, .16, 4)

@asset("vegetacao", fp=(4, 4), samples=48)
def arvore_morta_grande(m, seed=95):
    """Carvalho morto grande, com corvos."""
    _tree(m, seed, 2.2, .26, 5)
    crow = K.mat_solid("corvo", (.01, .01, .012), 0, .4)
    r = rnd(seed)
    for k in range(3):
        p = (r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(2.8, 3.6))
        sphere(crow, p, (.06, .1, .06), segs=8); sphere(crow, (p[0], p[1] - .08, p[2] + .05), (.035, .04, .035), segs=8)
    return {}

@asset("vegetacao")
def toco_arvore(m, seed=96):
    bark = K.mat_wood("casca", (.045, .035, .028))
    cyl(bark, (0, 0, .25), .25, .5, verts=12, r2=.2)
    cyl(K.mat_wood("cerne", (.12, .08, .05)), (0, 0, .5), .2, .01, verts=12)
    for k in range(4):
        a = math.radians(90*k + 30)
        along(bark, (0, 0, .15), (math.cos(a)*.45, math.sin(a)*.45, -.02), .07, .02, verts=6)
    along(bark, (.3, -.2, .05), (1.2, -.6, .1), .12, .09, verts=10)   # tronco caído
    return {}

def _tree(m, seed, L0, R0, depth):
    r = rnd(seed)
    bark = K.mat_wood("casca", (.045, .035, .028))
    def branch(p, d, L, rad, dep):
        q = p + d*L
        along(bark, p, q, rad, rad*.7, verts=8)
        if dep:
            for s in range(2 if dep > 1 else 3):
                nd = (d + Vector((r.uniform(-.9, .9), r.uniform(-.9, .9), r.uniform(-.1, .4)))).normalized()
                branch(q, nd, L*.72, rad*.62, dep-1)
    branch(Vector((0, 0, -.1)), Vector((r.uniform(-.15, .15), r.uniform(-.15, .15), 1)).normalized(), L0, R0, depth)
    for k in range(5):
        a = math.radians(72*k + 20)
        along(bark, (0, 0, .25), (math.cos(a)*R0*5, math.sin(a)*R0*5, -.02), R0*.5, .02, verts=6)
    return {}

# ================================================================ RIO
@asset("rio")
def juncos(m, seed=100):
    """Juncos e taboas de beira d'água."""
    r = rnd(seed)
    g = [K.mat_solid("junco", (.06, .07, .035), 0, .7), K.mat_solid("junco_seco", (.1, .085, .045), 0, .8)]
    for k in range(40):
        a = Vector((r.gauss(0, .2), r.gauss(0, .15), 0)); d = Vector((r.uniform(-.25, .25), r.uniform(-.25, .25), 1)).normalized()
        h = r.uniform(.5, 1.1); along(g[k % 2], a, a + d*h, .01, .002, verts=3)
        if k % 6 == 0:
            cyl(K.mat_solid("taboa", (.06, .03, .015), 0, .8), tuple(a + d*h*.85), .022, .14, verts=6)
    return {}

@asset("rio")
def pedras_rio(m, seed=101):
    r = rnd(seed)
    st = K.mat_stone("pedra_rio", (.1, .1, .095), (.035, .035, .033), 3, .9)
    for k in range(6):
        o = sphere(st, (r.uniform(-.5, .5), r.uniform(-.4, .4), .05), (r.uniform(.1, .28), r.uniform(.1, .22), r.uniform(.06, .14))); displace(o, .03, .15, seed+k, 1)
    return {}

@asset("rio", fp=(3, 1))
def tronco_margem(m, seed=102):
    bark = K.mat_wood("casca_molhada", (.035, .03, .025))
    along(bark, (-1.0, -.2, .12), (1.0, .2, .2), .18, .14, verts=12)
    along(bark, (.3, .05, .2), (.6, -.5, .6), .05, .02, verts=6)
    along(bark, (-.5, -.1, .2), (-.7, .4, .55), .04, .015, verts=6)
    for k in range(5): along(bark, (-1.0, -.2, .1), (-1.3 + k*.1, -.5 + k*.15, -.02), .04, .01, verts=5)
    return {}

@asset("paredes", walls=True)
def ponte_madeira(m, seed=103):
    """Segmento de ponte de tábuas sobre estacas (encaixe lado a lado ao longo do eixo)."""
    r = rnd(seed); L = T
    for k in range(5):
        box(m["wood"], (-L/2 + L/5*(k+.5), 0, .45), (L/5 - .015, 1.6, .06), (r.uniform(-2, 2), 0, r.uniform(-2, 2)), .005)
    for sy in (-1, 1):
        box(m["wood_d"], (0, sy*.7, .38), (L, .12, .1), bevel=.01)
        cyl(m["wood_d"], (0, sy*.75, .0), .07, 1.0, verts=8)
        cyl(m["wood_d"], (0, sy*.75, .8), .04, .7, verts=6)
        box(m["wood"], (0, sy*.75, 1.1), (L, .06, .06), (r.uniform(-3, 3), 0, 0), .005)
    return {"nota": "a altura da tábua (0,45 m) fica acima da água; estacas descem abaixo do chão"}

@asset("predios", fp=(6, 4), samples=48)
def ponte_pedra_ruina(m, seed=104):
    """Ponte de pedra em arco, com um vão desabado e tábuas improvisadas."""
    r = rnd(seed)
    st = K.mat_brick("silhar_ponte", ("wall", T*2), 6.0, (.08, .075, .068), 2.5, 0.0, T, .3, .018)
    for sx in (-1, 1):
        box(st, (sx*1.9, 0, .6), (.8, 2.2, 1.2), bevel=.02)
        box(st, (sx*1.1, 0, 1.15), (1.0, 2.0, .3), (0, sx*-12, 0), .02)
    for k in range(5):  # arco quebrado
        a = math.radians(20 + k*14)
        if k == 3: continue
        box(st, (-math.cos(a)*1.2, 0, .1 + math.sin(a)*1.0), (.35, 2.0, .25), (0, math.degrees(a) - 90, 0), .02)
    for k in range(4):
        box(m["wood"], (.4 + k*.0, -.6 + k*.4, 1.25), (1.4, .3, .05), (0, r.uniform(-4, 4), r.uniform(-4, 4)), .005)
    for k in range(8):
        o = box(st, (r.uniform(-.6, .6), r.uniform(-1.2, 1.2), .08), (.3, .25, .2), (r.uniform(-20, 20), 0, r.uniform(0, 90)), .02)
    for sx in (-1, 1):
        for sy in (-1, 1): box(st, (sx*1.9, sy*1.0, 1.5), (.25, .25, .6), bevel=.02)
    return {}

@asset("rio", fp=(3, 2))
def barco_afundado(m, seed=105):
    """Barco de pesca meio afundado na lama, com remo e rede."""
    w = m["wood_d"]
    for sx in (-1, 1):
        box(w, (sx*.45, 0, .2), (.06, 2.2, .35), (sx*-20, 12, 0), .01)
    box(w, (0, 0, .05), (.9, 2.1, .06), (0, 12, 0), .01)
    for k in range(3): box(w, (0, -.6 + k*.6, .3), (.95, .15, .05), (0, 12, 0), .005)
    along(m["wood"], (.6, -.6, .05), (1.0, .8, .3), .025, verts=6)
    o = box(K.mat_cloth("rede", (.08, .075, .06)), (-.6, .7, .08), (.8, .7, .03), (0, 0, 20), 0); displace(o, .05, .2, seed, 3)
    return {}

# ================================================================ DESERTO RADIOATIVO (área inicial)
def concreto(seed=0.0):
    return K.mat_brick("concreto", ("wall", T*2), 20.0 + seed, (.13, .125, .115), 3.0, 0.0, 1.41, .9, .01)

def areia_obj():
    return K.mat_sand_obj()

def duna(loc, sx, sy, h, seed):
    """Monte de areia liso, com crista assimétrica (vento) e ondulações."""
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40, ring_count=20, location=loc)
    o = bpy.context.object; o.scale = (sx, sy, h); bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(areia_obj())
    for p in o.data.polygons: p.use_smooth = True
    t = bpy.data.textures.new(f"dt_duna{seed}", 'CLOUDS'); t.noise_scale = max(sx, sy)*.8; t.noise_depth = 1
    d = o.modifiers.new("disp", 'DISPLACE'); d.texture = t; d.strength = h*.35; d.texture_coords = 'GLOBAL'
    sm = o.modifiers.new("smooth", 'SMOOTH'); sm.iterations = 6
    return o

def vergalhoes(m, base, n, seed, L=.6):
    r = rnd(seed)
    for k in range(n):
        a = Vector(base) + Vector((r.uniform(-.4, .4), r.uniform(-.1, .1), 0))
        d = Vector((r.uniform(-.5, .5), r.uniform(-.5, .5), 1)).normalized()
        along(m["rust"], a, a + d*r.uniform(L*.4, L), .012, verts=5)

def glow_green(strength=6): return K.mat_emit("radiacao", (.45, 1, .12), strength)

@asset("predios", fp=(10, 8), samples=48)
def predio_concreto(m, seed=110):
    """Bloco de apartamentos de concreto partido, meio enterrado na areia; sobreviventes
    vivem no térreo com remendos de sucata e uma janela acesa."""
    r = rnd(seed); c = concreto()
    W, D, FH = 6.0, 4.5, 2.8
    floors = [4, 4, 3, 2]   # andares restantes por coluna (de -X para +X)
    cols = len(floors); cw = W/cols
    dark = K.mat_solid("vao", (.004, .004, .004))
    for i, nf in enumerate(floors):
        x = -W/2 + cw*(i+.5)
        for f in range(nf):
            z = f*FH
            if f == nf-1 and i >= 2: continue
            # lajes
            box(c, (x, 0, z + FH - .1), (cw + .02, D, .2), bevel=.01)
            # pilares e paredes da fachada (-Y) com vão de janela
            box(c, (x, -D/2, z + FH/2), (cw + .02, .25, FH), bevel=.01)
            box(dark, (x, -D/2 - .01, z + FH*.55), (cw*.55, .27, FH*.45), bevel=0)
            box(c, (x, -D/2 - .12, z + FH*.3), (cw*.7, .12, .08), bevel=.005)   # peitoril
            # lateral +X só na última coluna
            if i == cols-1:
                box(c, (W/2, 0, z + FH/2), (.25, D, FH), bevel=.01)
                box(dark, (W/2 + .01, 0, z + FH*.55), (.27, D*.4, FH*.45), bevel=0)
        # topo quebrado da coluna
        top = nf*FH
        for k in range(3):
            o = box(c, (x + r.uniform(-.4, .4), r.uniform(-1.5, 1.5), top - .1 + r.uniform(0, .4)), (r.uniform(.4, .9), r.uniform(.4, 1.0), r.uniform(.2, .6)), (r.uniform(-15, 15), r.uniform(-15, 15), r.uniform(0, 40)), .01)
            crumble(o, .05, seed + i*7 + k)
        vergalhoes(m, (x, -D/2 + .2, top - .1), 6, seed + i)
    box(c, (0, D/2, sum(floors)/len(floors)*FH/2), (W, .25, 3*FH), bevel=.01)
    box(c, (-W/2, 0, 2*FH), (.25, D, 4*FH), bevel=.01)
    # térreo habitado: porta de chapa, janela acesa, remendos e cano de latão
    box(m["rust"], (-W/2 + cw*.5, -D/2 - .15, 1.0), (1.0, .05, 2.0), bevel=.005)
    box(K.mat_emit("janela_quente", (1, .5, .15), 2.5), (-W/2 + cw*1.5, -D/2 - .14, 1.5), (cw*.55, .02, FH*.45), bevel=0)
    for k in range(3): box(m["wood_d"], (-W/2 + cw*1.5, -D/2 - .17, 1.2 + k*.3), (cw*.6, .03, .1), (0, r.uniform(-8, 8), 0), .005)
    point((-W/2 + cw*1.5, -D/2 - .9, 1.5), (1, .5, .18), 25, .3)
    for k in range(4): box(m["tin"], (-W/2 + cw*(k % 2 + 2.5), -D/2 - .15, FH*(k//2) + 1.5), (cw*.6, .03, FH*.5), (0, r.uniform(-5, 5), 0), .003)
    along(m["brass"], (-W/2 + cw*1.0, -D/2 - .3, 0), (-W/2 + cw*1.0, -D/2 - .3, 2*FH + .5), .06)
    along(m["brass"], (-W/2 + cw*1.0, -D/2 - .3, 2*FH + .5), (-W/2 + cw*1.6, -D/2 - .6, 2*FH + .9), .06)
    # varal de panos e antena de rádio no topo
    for k in range(4):
        box(K.mat_cloth("pano", [(.1, .02, .015), (.04, .06, .08), (.12, .1, .07), (.06, .05, .03)][k], 30.0 + k), (-W/2 + .6 + k*.45, -D/2 - .5, 3.6), (.35, .02, .45), (0, 0, r.uniform(-8, 8)), 0)
    along(m["iron"], (-W/2 + .3, -D/2 - .5, 3.85), (-W/2 + 2.3, -D/2 - .5, 3.85), .006, verts=4)
    along(m["iron"], (-W/2 + .5, 0, 4*FH), (-W/2 + .5, 0, 4*FH + 2.5), .025, verts=6)
    for k in range(3): along(m["iron"], (-W/2 + .5, 0, 4*FH + .8 + k*.6), (-W/2 + .5 + .4 - k*.1, 0, 4*FH + .8 + k*.6), .012, verts=4)
    # duna engolindo o prédio
    duna((1.5, -1.0, .0), 4.0, 2.4, 1.6, seed)
    duna((W/2 + .5, 1.0, 0), 1.8, 2.8, 2.2, seed+1)
    for k in range(8):
        o = box(c, (r.uniform(-W/2, W/2 + 1.5), r.uniform(-D/2 - 2, -D/2 - .5), .1), (r.uniform(.3, .8), r.uniform(.3, .6), r.uniform(.15, .35)), (r.uniform(-20, 20), r.uniform(-20, 20), r.uniform(0, 90)), .01)
        crumble(o, .04, seed + 50 + k)
    return {"emissivo": "janela acesa"}

@asset("predios", fp=(6, 6), samples=48)
def torre_tombada(m, seed=111):
    """Resto de torre de concreto tombada e cravada na areia, em ângulo."""
    r = rnd(seed); c = concreto(1.0)
    piv = bpy.data.objects.new("torre", None); bpy.context.scene.collection.objects.link(piv)
    S, FH = 2.6, 2.8
    dark = K.mat_solid("vao", (.004, .004, .004))
    for f in range(4):
        z = f*FH
        for (x, y, w, d) in [(0, -S/2, S, .22), (0, S/2, S, .22), (-S/2, 0, .22, S), (S/2, 0, .22, S)]:
            box(c, (x, y, z + FH/2), (w, d, FH), bevel=.01, parent=piv)
        box(dark, (0, -S/2 - .01, z + FH*.55), (S*.5, .24, FH*.45), bevel=0, parent=piv)
        box(dark, (S/2 + .01, 0, z + FH*.55), (.24, S*.5, FH*.45), bevel=0, parent=piv)
        box(c, (0, 0, z + FH - .1), (S, S, .2), bevel=.01, parent=piv)
    piv.rotation_euler = (math.radians(-35), math.radians(20), math.radians(10)); piv.location = (0, .8, -1.5)
    duna((0, 0, 0), 3.0, 3.0, 1.4, seed)
    vergalhoes(m, (0, -1.5, 1.0), 5, seed)
    sphere(glow_green(3), (1.4, -1.6, .02), (.5, .3, .02))
    point((1.4, -1.8, .3), (.4, 1, .15), 20, .4)
    return {"emissivo": "poça radioativa"}

@asset("predios", fp=(4, 3))
def ruina_concreto(m, seed=112):
    """Canto de parede de concreto com janela e vergalhões, meio soterrado."""
    r = rnd(seed); c = concreto(2.0)
    box(c, (0, 0, 1.6), (3.0, .25, 3.2), bevel=.01)
    box(c, (1.5, .9, 1.2), (.25, 1.8, 2.4), bevel=.01)
    box(K.mat_solid("vao", (.004, .004, .004)), (-.5, -.01, 1.8), (1.0, .27, 1.0), bevel=0)
    for k in range(4):
        o = box(c, (-1.5 + k*.8, 0, 3.2 + r.uniform(-.2, .2)), (.8, .25, r.uniform(.2, .6)), (0, r.uniform(-15, 15), 0), .01); crumble(o, .04, seed+k)
    vergalhoes(m, (-.5, 0, 3.3), 7, seed, .8)
    duna((-.5, -1.0, 0), 2.2, 1.4, .7, seed)
    return {}

def _carro(m, seed, van=False):
    r = rnd(seed)
    body = K.mat_metal("lataria", (.09, .05, .03), .85, seed*1.0, .6)
    L, W = (4.2, 1.8) if not van else (4.6, 1.9)
    box(body, (0, 0, .55), (W, L, .55), bevel=.06)
    if van: box(body, (0, -.2, 1.35), (W - .05, L - .8, 1.1), bevel=.06)
    else: box(body, (0, .2, 1.05), (W - .2, L*.45, .5), bevel=.08)
    dark = K.mat_solid("vidro_quebrado", (.01, .012, .012), 0, .1)
    box(dark, (0, .2 if not van else -.2, 1.05 if not van else 1.4), (W - .15, L*.45 - .2 if not van else L - 1.0, .4 if not van else .7), bevel=0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            torus(K.mat_solid("aro", (.04, .03, .025), .8, .6), (sx*(W/2 - .05), sy*L*.33, .3), .22, .04, (0, 90, 0))
    box(m["rust"], (0, -L/2 - .05, .5), (W, .1, .2), bevel=.01)
    duna((.4, .6, 0), 1.6, 2.2, .45, seed)
    return {}

def carro_carcaca(m, seed=113):
    """Carcaça de carro enferrujada, sem rodas, afundando na areia."""
    return _carro(m, seed)

def furgao_carcaca(m, seed=114):
    """Carcaça de furgão com chapas de sucata soldadas (vira abrigo)."""
    _carro(m, seed, True)
    box(m["tin"], (.97, -.3, 1.3), (.04, 1.6, 1.0), (0, 0, 0), .003)
    cyl(m["brass"], (-.5, 1.2, 2.2), .08, .8, verts=10)
    return {}

@asset("props", fp=(1, 5))
def poste_tombado(m, seed=115):
    """Poste de concreto tombado com fios e isoladores."""
    c = concreto(3.0)
    along(c, (0, -2.5, .15), (0, 2.5, .25), .12, .09, verts=8)
    box(m["rust"], (0, 2.1, .3), (1.4, .1, .1), bevel=.005)
    for x in (-.6, 0, .6): cyl(K.mat_solid("isolador", (.25, .22, .18), 0, .2), (x, 2.1, .4), .04, .12, verts=8)
    for x in (-.6, .6): along(m["iron"], (x, 2.1, .4), (x + .3, -1.0, .02), .006, verts=4)
    duna((0, -2.3, 0), .6, .7, .3, seed)
    return {}

@asset("props")
def tambores_radioativos(m, seed=116):
    """Tambores amarelos de lixo radioativo vazando brilho verde."""
    r = rnd(seed)
    yel = K.mat_metal("tambor_amarelo", (.22, .16, .02), .6, seed*1.0, .5)
    for (x, y, rot) in [(0, 0, 0), (.55, .15, 0), (-.3, -.5, 90)]:
        if rot:
            cyl(yel, (x, y, .27), .27, .85, (90, 0, 60), 20)
        else:
            cyl(yel, (x, y, .43), .27, .85, verts=20)
            for z in (.15, .7): torus(m["iron"], (x, y, z), .275, .015)
            cyl(K.mat_solid("simbolo", (.015, .012, .01)), (x, y - .27, .45), .1, .01, (90, 0, 0), 3)
    _pool(glow_green(2.5), .5, .35, seed, 3, .006)
    point((-.3, -.7, .3), (.4, 1, .15), 30, .3)
    return {"emissivo": "verde tóxico", "luz": "radiacao"}

@asset("decalques")
def poca_toxica(m, seed=117):
    _pool(glow_green(2.0), .7, .55, seed, 5); return {"emissivo": "verde tóxico"}

@asset("vegetacao")
def planta_mutante(m, seed=118):
    """Planta mutante carnuda com pústulas verdes brilhantes."""
    r = rnd(seed)
    flesh = K.mat_solid("planta_carne", (.08, .06, .04), 0, .5)
    for k in range(6):
        a = Vector((r.uniform(-.15, .15), r.uniform(-.15, .15), 0))
        d = Vector((r.uniform(-.5, .5), r.uniform(-.5, .5), 1)).normalized()
        h = r.uniform(.4, .9)
        o = along(flesh, a, a + d*h, .07, .03, verts=10)
        for j in range(3):
            p = a + d*h*r.uniform(.3, 1)
            sphere(glow_green(4), tuple(p + Vector((r.uniform(-.06, .06), r.uniform(-.06, .06), 0))), (.03, .03, .03), segs=8)
    point((0, -.3, .5), (.4, 1, .15), 6, .2)
    return {"emissivo": "pústulas"}

@asset("vegetacao")
def cacto_seco(m, seed=119):
    r = rnd(seed)
    sk = K.mat_solid("cacto", (.06, .065, .04), 0, .7)
    along(sk, (0, 0, 0), (0, 0, 1.4), .14, .11, verts=12)
    for sx in (-1, 1):
        h = r.uniform(.5, .9)
        along(sk, (0, 0, h), (sx*.35, 0, h + .1), .08, verts=10)
        along(sk, (sx*.35, 0, h + .1), (sx*.38, 0, h + .6), .08, .06, verts=10)
    return {}

@asset("props")
def placa_radiacao(m, seed=120):
    cyl(m["iron"], (0, 0, .7), .03, 1.4, (4, -6, 0), 6)
    cyl(K.mat_solid("placa_amarela", (.25, .19, .03), .3, .5), (0, -.04, 1.35), .3, .02, (90, 0, 0), 3)
    cyl(K.mat_solid("simbolo", (.015, .012, .01)), (0, -.06, 1.33), .1, .01, (90, 0, 0), 3)
    return {}

@asset("predios", fp=(3, 3))
def caixa_dagua_sucata(m, seed=121):
    """Caixa d'água de sobreviventes: tanque de latão sobre estrutura de vigas, com filtro."""
    for sx in (-1, 1):
        for sy in (-1, 1): along(m["rust"], (sx*.7, sy*.7, 0), (sx*.5, sy*.5, 3.0), .06, verts=6)
    for z in (1.0, 2.0):
        box(m["rust"], (0, -.6, z), (1.3, .05, .05), (0, 30, 0), 0)
        box(m["rust"], (.6, 0, z), (.05, 1.3, .05), (30, 0, 0), 0)
    cyl(m["brass"], (0, 0, 3.6), .75, 1.2, verts=24)
    sphere(m["brass"], (0, 0, 4.2), (.75, .75, .3))
    for z in (3.2, 3.9): torus(m["iron"], (0, 0, z), .76, .025)
    along(m["brass"], (.5, -.5, 3.1), (.6, -.6, .3), .05)
    cyl(m["brass"], (.6, -.6, .3), .2, .5, verts=12)
    box(K.mat_emit("lampada", (1, .6, .25), 6), (0, -.77, 3.6), (.08, .02, .08), bevel=0)
    point((0, -1.1, 3.4), (1, .6, .25), 15, .1)
    return {}

@asset("vegetacao", fp=(3, 3))
def duna_areia(m, seed=122):
    duna((0, 0, 0), 1.6, 1.2, .6, seed); return {}


# ================================================================ SÃO LÁZARO ENTERRADA (Deserto de Absinto)
def dunas_em_volta(fp, seed, h=1.0):
    """Dunas encostadas no prédio enterrado, cobrindo o corte na linha da areia."""
    r = rnd(seed); w, d = fp[0]*T/2, fp[1]*T/2
    for k in range(10):
        a = 2*math.pi*k/10 + r.uniform(-.2, .2)
        x, y = math.cos(a)*w*.75, math.sin(a)*d*.75
        hh = h*r.uniform(1.1, 1.8)
        duna((x, y, -hh*.65), r.uniform(1.6, 2.4)*max(w, d)*.45, r.uniform(1.6, 2.4)*max(w, d)*.4, hh, seed + k)

def _green_glow(pts, e=80):
    for p in pts: point(p, (.4, 1, .15), e, .6)

asset("predios", fp=(12, 16), samples=48, bury=4.6, name="capela_enterrada")(lambda m: (capela_sao_lazaro(m), _green_glow([(0, -1, .5), (1.4, 0, 1.0), (0, 2, .5)], 120), dunas_em_volta((12, 16), 7, 1.3), {"emissivo": "rosácea (entrada) e nave verde", "descricao_extra": "enterrada até o coro; entra-se pela rosácea"})[-1])
REG["capela_enterrada"]["fn"].__doc__ = "Capela de São Lázaro enterrada até o coro: a rosácea vira a entrada e a nave brilha verde lá dentro."

asset("predios", fp=(14, 12), samples=48, bury=3.4, name="frigorifico_enterrado")(lambda m: (abatedouro_carnica(m), _claraboias(m), dunas_em_volta((14, 12), 9, 1.2), {"emissivo": "claraboias", "descricao_extra": "entrada pelas claraboias"})[-1])
REG["frigorifico_enterrado"]["fn"].__doc__ = "Abatedouro Carniça (frigorífico) enterrado até o segundo andar; entra-se pelas claraboias do telhado em serra."

def _claraboias(m):
    W, D, H = 8.5, 7.0, 4.2
    glass = K.mat_solid("vidro_sujo", (.05, .06, .05), 0, .15)
    for k in range(3):
        y = -D/2 + D/3*(k+.5) + D/6 - .12
        box(glass, (0, y, H + .55), (W - .3, .03, .9), bevel=0)
        for j in range(8):
            box(m["iron"], (-W/2 + .3 + j*W/8, y - .02, H + .55), (.04, .03, .95), bevel=0)
    # claraboia aberta com escada de corda e brilho vermelho
    y = -D/2 + D/6*2 - .12
    box(K.mat_emit("brilho_porao", (.8, .1, .04), 2.5), (1.2, y + .02, H + .55), (1.0, .02, .8), bevel=0)
    point((1.2, y - .8, H + .6), (1, .15, .06), 40, .4)
    for k in range(6):
        box(m["wood"], (1.2, y - .3 - k*.15, H + .9 - k*.18), (.5, .04, .03), bevel=0)

@asset("predios", fp=(10, 8), samples=48, bury=8.4)
def predio_enterrado(m, seed=130):
    """Prédio de São Lázaro enterrado até o quarto andar: os moradores vivem nos andares
    de cima e entram pelas janelas por pranchas e escadas de corda."""
    r = rnd(seed); c = concreto()
    W, D, FH = 6.4, 4.8, 2.8
    nb_x, nb_y = 4, 3; bw, bd = W/nb_x, D/nb_y
    NF = 6; zs = 8.4
    plan = {  # (andar, vão) -> tipo; resto escuro
        ("x", 3, 0): "door", ("x", 3, 1): "lit", ("x", 3, 2): "boarded", ("x", 3, 3): "broken",
        ("x", 4, 0): "lit", ("x", 4, 1): "dark", ("x", 4, 2): "broken", ("x", 4, 3): "lit",
        ("x", 5, 1): "boarded", ("x", 5, 2): "dark",
        ("y", 3, 1): "lit", ("y", 4, 0): "broken", ("y", 4, 2): "boarded", ("y", 5, 0): "dark",
    }
    missing = {("x", 5, 3), ("y", 5, 2), ("y", 5, 1), ("x", 5, 0)}   # canto desabado no topo
    for f in range(NF):
        z = f*FH
        for i in range(nb_x):
            key = ("x", f, i)
            if key in missing: continue
            k_ = plan.get(key, "dark" if f > 2 else "dark")
            bay(m, c, -W/2 + bw*(i + .5), -D/2, z, bw, FH, "x", k_, seed + f*10 + i)
            if k_ == "lit": point((-W/2 + bw*(i + .5), -D/2 - .7, z + FH*.55), (1, .5, .18), 14, .3)
        for j in range(nb_y):
            key = ("y", f, j)
            if key in missing: continue
            k_ = plan.get(key, "dark")
            bay(m, c, W/2, -D/2 + bd*(j + .5), z, bd, FH, "y", k_, seed + 100 + f*10 + j)
            if k_ == "lit": point((W/2 + .7, -D/2 + bd*(j + .5), z + FH*.55), (1, .5, .18), 14, .3)
        box(c, (0, 0, z + FH - .1), (W, D, .2), bevel=.01)                       # laje
        box(c, (0, -D/2 - .14, z + FH - .1), (W + .1, .08, .22), bevel=.01)       # friso
        box(c, (W/2 + .14, 0, z + FH - .1), (.08, D + .1, .22), bevel=.01)
    box(c, (0, D/2, NF*FH/2), (W, .25, NF*FH), bevel=.01)
    box(c, (-W/2, 0, NF*FH/2), (.25, D, NF*FH), bevel=.01)
    # topo quebrado e vergalhões no canto desabado
    for k in range(6):
        o = box(c, (W/2 - r.uniform(.3, 1.8), -D/2 + r.uniform(.2, 1.5), NF*FH - FH + r.uniform(.1, .6)), (r.uniform(.4, 1.0), r.uniform(.3, .8), r.uniform(.2, .5)), (r.uniform(-25, 25), r.uniform(-25, 25), r.uniform(0, 60)), .01)
        crumble(o, .05, seed + 40 + k)
    vergalhoes(m, (W/2 - 1.0, -D/2 + .3, (NF - 1)*FH), 9, seed, 1.0)
    vergalhoes(m, (-W/2 + 1.0, -D/2 + .2, NF*FH), 5, seed + 3, .7)
    # caixa d'água de latão e antena no telhado
    cyl(m["brass"], (-W/2 + 1.2, D/2 - 1.0, NF*FH + .7), .5, 1.2, verts=20)
    for z_ in (.3, 1.0): torus(m["iron"], (-W/2 + 1.2, D/2 - 1.0, NF*FH + z_), .51, .02)
    along(m["iron"], (-W/2 + .5, 0, NF*FH), (-W/2 + .5, 0, NF*FH + 2.8), .025, verts=6)
    for k in range(3): along(m["iron"], (-W/2 + .5, 0, NF*FH + 1.0 + k*.6), (-W/2 + .5 + .45 - k*.1, 0, NF*FH + 1.0 + k*.6), .012, verts=4)
    # varanda de sucata no 5º andar
    vz = 4*FH
    box(m["rust"], (-W/2 + bw*.5, -D/2 - .6, vz + .05), (bw*1.6, 1.1, .06), bevel=.005)
    for k in range(7): cyl(m["iron"], (-W/2 + bw*.5 - bw*.75 + k*bw*.25, -D/2 - 1.12, vz + .5), .012, .9, verts=5)
    box(m["iron"], (-W/2 + bw*.5, -D/2 - 1.12, vz + .95), (bw*1.6, .03, .04), bevel=0)
    for sx in (-1, 1): along(m["rust"], (-W/2 + bw*.5 + sx*bw*.7, -D/2 - .15, vz - .8), (-W/2 + bw*.5 + sx*bw*.7, -D/2 - 1.1, vz), .03, verts=5)
    for k in range(3): box(K.mat_cloth("pano", [(.1, .02, .015), (.04, .06, .08), (.12, .1, .07)][k], 30.0 + k), (-W/2 + bw*.1 + k*.4, -D/2 - 1.15, vz + .6), (.32, .02, .5), (0, 0, r.uniform(-8, 8)), 0)
    # cano de latão descendo com válvulas
    px = -W/2 + bw*2.0
    along(m["brass"], (px, -D/2 - .3, zs - .2), (px, -D/2 - .3, NF*FH - .5), .065)
    along(m["brass"], (px, -D/2 - .3, NF*FH - .5), (px, -D/2 - .05, NF*FH - .5), .065)
    for z_ in (zs + 1.0, zs + 3.5): torus(m["iron"], (px, -D/2 - .3, z_), .075, .015)
    cyl(m["brass"], (px + .12, -D/2 - .32, zs + 2.0), .09, .04, (0, 90, 0), 12)
    # entradas: prancha até a porta do 4º andar e escada de corda até a janela do 5º
    box(m["wood"], (-W/2 + bw*.5, -D/2 - 1.0, zs + .25), (.6, 2.0, .06), (-14, 0, 0), .005)
    for k in range(7): box(m["wood"], (W/2 + .2, -D/2 + bd*.5, zs + .15 + k*.36), (.04, .5, .04), bevel=0)
    for s in (-1, 1): along(K.mat_solid("corda", (.1, .08, .05)), (W/2 + .2, -D/2 + bd*.5 + s*.25, zs), (W/2 + .2, -D/2 + bd*.5 + s*.25, zs + 2.8), .01, verts=4)
    # lanterna na porta e placa da Vigília
    cyl(m["brass"], (-W/2 + bw*.5 + .45, -D/2 - .25, zs + 2.1), .07, .2, verts=10)
    sphere(K.mat_emit("lanterna", (1, .6, .25), 8), (-W/2 + bw*.5 + .45, -D/2 - .25, zs + 2.1), (.05, .05, .07), segs=8)
    point((-W/2 + bw*.5 + .45, -D/2 - .6, zs + 2.0), (1, .55, .2), 25, .05)
    # pó Amargo brilhando na areia ao pé
    sphere(K.mat_emit("radiacao_fraca", (.45, 1, .12), .5), (1.4, -3.6, zs + .02), (1.4, .6, .02))
    dunas_em_volta((10, 8), seed, 1.2)
    return {"emissivo": "janelas acesas e lanterna", "linha_da_areia_m": 0}

@asset("predios", fp=(14, 14), samples=48, bury=1.2)
def cupula_estacao(m, seed=131):
    """Cúpula de vidro da estação de bonde, base do Acampamento da Vela: costelas de ferro,
    vidraças quebradas e remendadas com lona, e a lâmpada de arco no topo."""
    r = rnd(seed)
    R = 4.2
    glass = K.mat_solid("vidro_cupula", (.03, .04, .04), 0, .08)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=R, location=(0, 0, 0))
    dome = bpy.context.object; dome.data.materials.append(glass)
    bpy.ops.mesh.primitive_cube_add(size=2*R+1, location=(0, 0, -R - .5)); cut = bpy.context.object
    bo = dome.modifiers.new("b", 'BOOLEAN'); bo.object = cut; bo.operation = 'DIFFERENCE'
    bpy.context.view_layer.objects.active = dome; bpy.ops.object.modifier_apply(modifier="b"); bpy.data.objects.remove(cut)
    for p in dome.data.polygons: p.use_smooth = True
    for k in range(16):  # costelas
        a = 2*math.pi*k/16
        pts = [Vector((math.cos(a)*R*math.cos(t), math.sin(a)*R*math.cos(t), R*math.sin(t))) for t in [i*math.pi/2/8 for i in range(9)]]
        for p, q in zip(pts, pts[1:]): along(m["iron"], p*1.01, q*1.01, .05, verts=6)
    for t in (.35, .7, 1.05):
        torus(m["iron"], (0, 0, R*math.sin(t)), R*math.cos(t)*1.01, .045)
    # painéis remendados com lona e chapas
    for k in range(9):
        a = r.uniform(0, 2*math.pi); t = r.uniform(.2, 1.0)
        p = Vector((math.cos(a)*R*math.cos(t), math.sin(a)*R*math.cos(t), R*math.sin(t)))*1.02
        o = box(r.choice([m["cloth"], m["tin"], m["rust"]]), tuple(p), (.9, .9, .03), (0, math.degrees(math.pi/2 - t), math.degrees(a)), .003)
        o.rotation_euler = p.normalized().to_track_quat('Z', 'Y').to_euler()
    # interior iluminado (velas da Vigília)
    for k in range(5):
        point((r.uniform(-2, 2), r.uniform(-2, 2), 1.0), (1, .55, .2), 120, .5)
    # lâmpada de arco no topo
    cyl(m["iron"], (0, 0, R + .3), .3, .6, verts=12)
    along(m["iron"], (0, 0, R + .6), (0, 0, R + 2.4), .06, verts=8)
    sphere(m["brass"], (0, 0, R + 2.5), (.2, .2, .2))
    arc = K.mat_emit("arco_eletrico", (.62, .85, 1.0), 40)
    for k in range(5):
        a0, a1 = math.radians(72*k), math.radians(72*(k+1))
        p0 = Vector((math.cos(a0)*.5, math.sin(a0)*.5, R + 2.7)); p1 = Vector((math.cos(a1)*.5, math.sin(a1)*.5, R + 2.7))
        along(m["iron"], (0, 0, R + 2.5), p0, .015, verts=4)
        mid = p0.lerp(p1, .5) + Vector((r.uniform(-.1, .1), r.uniform(-.1, .1), .15))
        along(arc, p0, mid, .012, verts=4); along(arc, mid, p1, .012, verts=4)
    sphere(K.mat_emit("arco_nucleo", (.85, .95, 1.0), 60), (0, 0, R + 2.85), (.1, .1, .1))
    point((0, 0, R + 2.9), (.55, .8, 1.0), 900, .3)
    # entrada: rampa de tábuas até uma vidraça aberta
    for k in range(6): box(m["wood"], (0, -R - 1.2 + k*.25, .2 + k*.15), (1.2, .3, .05), (0, 0, 0), .005)
    box(K.mat_emit("vao_quente", (1, .5, .18), 1.5), (0, -R*.93, 1.3), (1.0, .05, 1.2), (-20, 0, 0), 0)
    dunas_em_volta((14, 14), seed, 1.0)
    return {"emissivo": "arco elétrico azul e interior quente"}

@asset("predios", fp=(10, 4), samples=48)
def bonde_veleiro(m, seed=132):
    """Bonde da linha 7 adaptado como bonde-veleiro: mastro, vela de lona remendada,
    rodas sobre os trilhos que aparecem na areia."""
    r = rnd(seed)
    paint = K.mat_metal("pintura_bonde", (.16, .1, .03), .5, 8.0, .6)
    L, W = 5.0, 2.0
    for k in range(3):   # trilhos
        for sx in (-1, 1): box(m["iron"], (sx*.72, -3.2 + k*3.2, .05), (.07, 3.2, .06), bevel=.003)
    box(m["iron"], (0, 0, .5), (W*.9, L, .3), bevel=.03)
    box(paint, (0, 0, 1.2), (W, L, 1.0), bevel=.05)
    for sx in (-1, 1):
        for k in range(6): box(paint, (sx*W/2, -L/2 + .4 + k*.84, 2.05), (.06, .12, .7), bevel=.01)
        box(K.mat_solid("interior_escuro", (.004, .003, .003)), (sx*(W/2 - .05), 0, 2.05), (.05, L - .4, .7), bevel=0)
    box(paint, (0, 0, 2.5), (W + .1, L + .1, .12), bevel=.04)
    box(K.mat_solid("placa_linha", (.3, .27, .2), 0, .6), (0, -L/2 - .03, 2.3), (.7, .02, .28), bevel=0)
    for sy in (-1, 1):
        for sx in (-1, 1): cyl(m["iron"], (sx*.72, sy*1.6, .35), .32, .1, (0, 90, 0), 16)
    # mastro e vela
    cyl(m["wood_d"], (0, -.4, 4.6), .08, 4.4, verts=10)
    along(m["wood_d"], (0, -.4, 3.0), (0, 1.9, 3.1), .05, verts=6)        # retranca
    sail = K.mat_cloth("vela_remendada", (.16, .13, .09), 33.0)
    bpy.ops.mesh.primitive_plane_add(size=1)
    o = bpy.context.object; o.data.materials.append(sail)
    o.data.vertices[0].co = (0, -.35, 3.15); o.data.vertices[1].co = (0, 1.85, 3.2)
    o.data.vertices[2].co = (0, -.35, 6.6); o.data.vertices[3].co = (0, -.3, 6.6)
    displace(o, .12, .6, seed, 4)
    box(K.mat_cloth("remendo", (.04, .07, .1)), (.03, .5, 4.2), (.02, .5, .6), bevel=0)
    for (a, b) in [((0, -.4, 6.8), (0, -2.6, 2.6)), ((0, -.4, 6.8), (0, 2.6, 2.6)), ((0, -.4, 6.8), (.9, 0, 2.6))]:
        along(K.mat_solid("corda", (.1, .08, .05)), a, b, .008, verts=4)
    # bandeira da Vigília no topo e lanterna
    box(K.mat_cloth("bandeira_vigilia", (.03, .05, .08), 11.0), (0, -.1, 6.7), (.02, .5, .3), bevel=0)
    cyl(m["brass"], (.9, -L/2, 2.0), .06, .18, verts=10)
    sphere(K.mat_emit("lanterna", (1, .6, .25), 8), (.9, -L/2, 2.0), (.04, .04, .06), segs=8)
    point((.9, -L/2 - .3, 2.0), (1, .55, .2), 12, .05)
    duna((1.5, 2.0, -.2), 1.4, 1.6, .5, seed)
    return {}

@asset("props", fp=(1, 1), bury=3.5)
def poste_mastro(m, seed=133):
    """Poste a gás de São Lázaro saindo da areia como mastro de navio afundado."""
    poste_gas(m); duna((0, 0, 0), .6, .6, .25, seed); return {"emissivo": "lampião", "luz": "quente"}

@asset("predios", fp=(3, 3), bury=6.0)
def chamine_enterrada(m, seed=134):
    """Chaminé de fábrica saindo da areia, com fumaça e escada de ferro."""
    b = m["brick"]
    cyl(b, (0, 0, 5.0), 1.0, 10.0, verts=20, r2=.75)
    for z in (6.5, 8.0, 9.5): torus(m["iron"], (0, 0, z), .9 - (z - 6)*.025, .05)
    for k in range(12): box(m["iron"], (.0, -.95 + k*0, 6.2 + k*.3), (.35, .04, .03), (0, 0, 0), 0)
    for k in range(4):
        sphere(K.mat_solid("fumaca", (.15, .15, .14), 0, 1), (.2*k, .1*k, 10.3 + k*.45), (.4 + k*.12,)*3)
    duna((0, 0, 0), 2.0, 2.0, .6, seed)
    return {}

@asset("props", fp=(4, 4))
def mar_de_lapides(m, seed=135):
    """Cemitério de São Lázaro: lápides e cruzes que a duna cobre e descobre."""
    r = rnd(seed)
    st = K.mat_stone("lapide", (.1, .1, .095), (.04, .04, .04), 3, .8)
    duna((0, 0, -.1), 1.4, 1.2, .35, seed)
    for k in range(9):
        x, y = r.uniform(-1.2, 1.2), r.uniform(-1.1, 1.1); s = r.uniform(.6, 1.1)
        tilt = (r.uniform(-20, 20), r.uniform(-20, 20), r.uniform(-15, 15))
        if k % 3 == 0:
            box(m["wood"], (x, y, .35*s), (.07, .07, .8*s), tilt, .01)
            box(m["wood"], (x, y, .55*s), (.35*s, .06, .06), tilt, .01)
        else:
            box(st, (x, y, .3*s), (.4*s, .12, .7*s), tilt, .02)
    candle((.3, -.9, .05), .12); candle((-.4, -.6, .1), .1)
    return {}

# ================================================================ LOTE 2: props pendentes do level design
def alias(new, old, **over):
    info = dict(REG[old]); info.update(over); REG[new] = info

def ossos_costela(mat, c, n, L, R, seed, axis_y=True):
    r = rnd(seed)
    for k in range(n):
        y = c[1] - L/2 + k*L/(n-1)
        for sx in (-1, 1):
            pts = [Vector((c[0] + sx*R*math.sin(t), y, c[2] + R*math.cos(t)*.9)) for t in [i*.35 for i in range(6)]]
            for p, q in zip(pts, pts[1:]): along(mat, p, q, R*.035, verts=5)

@asset("limites", fp=(6, 4), samples=40)
def ossada_gigante(m, seed=140):
    """Ossada de criatura gigante meio enterrada (Mar de Dunas)."""
    b = m["bone"]
    along(b, (0, -3.0, .3), (0, 3.0, .6), .18, .12, verts=10)   # espinha
    ossos_costela(b, (0, .2, .5), 9, 4.0, 1.6, seed)
    sphere(b, (0, -3.6, .6), (.7, .9, .55)); sphere(K.mat_solid("orbita", (0, 0, 0)), (.35, -4.0, .8), (.15, .1, .12))
    along(b, (.3, -4.1, .4), (1.6, -4.8, 1.8), .12, .03, verts=8)   # chifre
    duna((1.0, 1.5, -.2), 2.5, 2.0, .7, seed); duna((-1.2, -2.0, -.2), 1.8, 1.4, .5, seed+1)
    return {}

@asset("limites", fp=(2, 2))
def ossada_viajante(m, seed=141):
    """Ossada de quem tentou atravessar a tempestade: esqueleto, mochila e cantil."""
    b = m["bone"]
    sphere(b, (0, .45, .08), (.08, .09, .08), segs=10)
    along(b, (0, .35, .05), (0, -.2, .05), .02, verts=5)
    ossos_costela(b, (0, .15, .05), 5, .3, .12, seed)
    for sx in (-1, 1):
        along(b, (sx*.1, -.2, .04), (sx*.15, -.7, .03), .018, verts=5)
        along(b, (sx*.15, .3, .04), (sx*.4, .2, .03), .014, verts=5)
    box(K.mat_cloth("mochila", (.08, .06, .04), 40.0), (.35, -.1, .12), (.3, .35, .22), (0, 0, 20), .03)
    cyl(m["brass"], (-.3, -.3, .06), .07, .2, (90, 0, 30), 10)
    duna((.2, .6, -.1), .8, .6, .25, seed)
    return {}

@asset("props")
def ossada_animal(m, seed=142):
    b = m["bone"]
    sphere(b, (0, .45, .1), (.1, .2, .09), segs=10)
    for sx in (-1, 1): along(b, (sx*.05, .55, .15), (sx*.3, .6, .35), .02, .005, verts=5)
    along(b, (0, .3, .08), (0, -.5, .08), .025, verts=5)
    ossos_costela(b, (0, -.05, .06), 6, .5, .15, seed)
    return {}

@asset("paredes", walls=True)
def corda_guarda(m, seed=143):
    """Estacas com corda de guarda na beira do precipício (segmento de 1 tile)."""
    r = rnd(seed); L = T
    for x in (-L/2, L/2): cyl(m["wood"], (x, 0, .45), .04, .9, (r.uniform(-6, 6), r.uniform(-6, 6), 0), 6)
    rope = K.mat_solid("corda", (.1, .08, .05))
    for z in (.5, .8):
        pts = [Vector((-L/2 + L*t/6, 0, z - math.sin(t/6*math.pi)*.08)) for t in range(7)]
        for p, q in zip(pts, pts[1:]): along(rope, p, q, .01, verts=4)
    box(K.mat_cloth("trapo", (.12, .02, .015), 41.0), (0, -.02, .74), (.08, .01, .18), bevel=0)
    return {}

@asset("limites", fp=(1, 1))
def poste_telegrafo(m, seed=144):
    """Poste de telégrafo de madeira inclinado, com isoladores e fios caídos."""
    along(m["wood_d"], (0, 0, 0), (.25, .1, 4.5), .09, .07, verts=8)
    box(m["wood_d"], (.24, .1, 4.1), (1.2, .08, .08), (0, 3, 0), .005)
    for x in (-.4, 0, .4): cyl(K.mat_solid("isolador", (.25, .22, .18), 0, .2), (.24 + x, .1, 4.2), .035, .1, verts=8)
    for x in (-.4, .4): along(m["iron"], (.24 + x, .1, 4.2), (.6 + x, 1.8, 0), .006, verts=4)
    duna((0, 0, -.1), .7, .6, .3, seed)
    return {}

@asset("props", fp=(2, 2))
def poste_ninho(m, seed=145):
    """Poste com ninho de corvos (galhos, ossos e trapos) e corvos."""
    along(m["wood_d"], (0, 0, 0), (0, 0, 3.2), .07, .06, verts=8)
    br = K.mat_wood("galho_seco", (.06, .045, .03)); r = rnd(seed)
    for k in range(30):
        a = r.uniform(0, 2*math.pi); p = Vector((math.cos(a)*.35, math.sin(a)*.35, 3.2 + r.uniform(-.05, .15)))
        along(br, p, p + Vector((math.cos(a + 1.6)*.4, math.sin(a + 1.6)*.4, r.uniform(-.05, .05))), .012, verts=4)
    crow = K.mat_solid("corvo", (.01, .01, .012), 0, .4)
    for k in range(2):
        p = (r.uniform(-.25, .25), r.uniform(-.25, .25), 3.4)
        sphere(crow, p, (.06, .1, .06), segs=8); sphere(crow, (p[0], p[1] - .08, p[2] + .05), (.035, .04, .035), segs=8)
    return {}

@asset("props", fp=(3, 3), samples=40)
def poste_ninho_gigante(m, seed=146):
    """Torre de ferro com ninho gigante (algo grande mora aqui)."""
    for k in range(3):
        a = math.radians(120*k)
        along(m["rust"], (math.cos(a)*.7, math.sin(a)*.7, 0), (math.cos(a)*.2, math.sin(a)*.2, 5.0), .06, verts=6)
    br = K.mat_wood("galho_seco", (.06, .045, .03)); r = rnd(seed)
    for k in range(70):
        a = r.uniform(0, 2*math.pi); rad = r.uniform(.4, 1.1); p = Vector((math.cos(a)*rad, math.sin(a)*rad, 5.0 + r.uniform(-.1, .3)))
        along(br, p, p + Vector((math.cos(a + 1.6)*.8, math.sin(a + 1.6)*.8, r.uniform(-.1, .1))), .025, verts=4)
    for k in range(5): sphere(m["bone"], (r.uniform(-.6, .6), r.uniform(-.6, .6), 5.3), (.08, .09, .08), segs=8)
    return {}

@asset("props")
def trilho_retorcido(m, seed=147):
    """Trilhos da Linha 7 arrancados e retorcidos para cima."""
    for sx in (-1, 1):
        pts = [Vector((sx*.36, -1.0 + t*.3, .05 + max(0, t - 3)**2*.12)) for t in range(8)]
        for p, q in zip(pts, pts[1:]): along(m["rust"], p, q, .035, verts=6)
    for k in range(4): box(m["wood_d"], (0, -.9 + k*.3, .03), (1.0, .12, .05), (0, 0, k*4), .01)
    return {}

@asset("limites", fp=(3, 4), samples=40)
def trilhos_no_abismo(m, seed=148):
    """Fim da Linha 7: trilhos e dormentes pendurados sobre o precipício."""
    r = rnd(seed)
    for sx in (-1, 1):
        pts = [Vector((sx*.36, -1.5 + t*.35, -max(0, t - 3)**1.6*.35)) for t in range(10)]
        for p, q in zip(pts, pts[1:]): along(m["rust"], p, q, .035, verts=6)
    for k in range(9):
        y = -1.4 + k*.35; z = -max(0, (y + 1.5)/.35 - 3)**1.6*.35
        box(m["wood_d"], (r.uniform(-.05, .05), y, z - .02), (1.0, .12, .05), (r.uniform(-10, 10), 0, r.uniform(-8, 8)), .01)
    return {"nota": "a ponta desce abaixo da linha do chão; coloque na borda do precipício"}

@asset("limites", fp=(5, 5), samples=40, bury=6.0)
def telhado_no_abismo(m, seed=149):
    """Telhado de casa da Cidade Velha visto lá embaixo no abismo (cenário da moldura)."""
    tile = K.mat_stone("telha", (.07, .03, .02), (.03, .015, .01), 5, .1)
    for sx in (-1, 1): box(tile, (sx*1.0, 0, 1.0), (2.4, 3.6, .12), (0, sx*40, 0), .01)
    box(m["brick"], (0, 0, -.3), (3.2, 3.4, 2.0), bevel=.01)
    box(m["brick"], (.8, .8, 2.0), (.5, .5, 1.2), bevel=.01)
    return {}

@asset("limites", fp=(3, 3), samples=40, bury=3.0)
def torre_no_abismo(m, seed=150):
    """Torre de igreja da Cidade Velha emergindo do abismo (cenário da moldura)."""
    st = K.mat_brick("silhar", ("wall", T*2), 4.0, (.085, .078, .07), 3.5, 0.0, T, .32, .018)
    box(st, (0, 0, 2.5), (1.8, 1.8, 5.0), bevel=.02)
    cyl(K.mat_stone("ardosia", (.045, .045, .05), (.015, .015, .018), 6, .2), (0, 0, 6.0), 1.3, 2.4, verts=4, r2=0)
    gothic_window(m, K.mat_stone_glass() if hasattr(K, "mat_stone_glass") else K.mat_stained_glass("vitral_verde", (.2, .8, .1), 2), (0, -.92, 3.0), .4, 1.0)
    return {}

@asset("limites", fp=(4, 4), samples=40)
def guindaste_sucata(m, seed=151):
    """Guindaste de sucata na beira do precipício, com gancho e corrente."""
    box(m["rust"], (0, 0, .3), (1.6, 1.6, .6), bevel=.02)
    for k in range(4):
        a = math.radians(45 + 90*k)
        along(m["rust"], (math.cos(a)*.6, math.sin(a)*.6, .6), (math.cos(a)*.15, math.sin(a)*.15, 4.0), .05, verts=6)
    along(m["rust"], (0, 0, 4.0), (0, -3.5, 4.6), .08, verts=8)
    along(m["rust"], (0, 0, 4.0), (0, 1.2, 3.6), .08, verts=8)
    box(m["dark_stone"], (0, 1.3, 3.3), (.6, .6, .6), bevel=.02)
    chain(m["iron"], (0, -3.4, 4.5), (0, -3.4, 2.4), 12, .04)
    cyl(m["iron"], (0, -3.4, 2.3), .06, .3, (0, 90, 0), 8, r2=0)
    cyl(m["brass"], (.5, .5, .9), .3, .6, (0, 90, 0), 16)
    return {}

@asset("limites", fp=(3, 6), samples=40)
def ponte_rompida(m, seed=152):
    """Ponte de tábuas rompida pendendo no abismo."""
    r = rnd(seed)
    for k in range(10):
        y = -1.8 + k*.38; z = -max(0, k - 4)**1.5*.2
        box(m["wood"], (r.uniform(-.05, .05), y, .3 + z), (1.4, .3, .05), (r.uniform(-12, 12), 0, r.uniform(-6, 6)), .005)
    rope = K.mat_solid("corda", (.1, .08, .05))
    for sx in (-1, 1):
        cyl(m["wood_d"], (sx*.75, -1.9, .5), .07, 1.2, verts=8)
        along(rope, (sx*.75, -1.9, 1.0), (sx*.7, 1.6, -1.0), .012, verts=4)
    return {}

@asset("limites", fp=(4, 4), samples=40, bury=3.5)
def torre_vigia_enterrada(m, seed=153):
    """Torre de vigia da Linha do Impasse engolida pela tempestade."""
    torre_vigia(m); return {}

@asset("predios", fp=(5, 5), samples=40, bury=7.0)
def torre_relogio_enterrada(m, seed=154):
    """Torre do relógio de São Lázaro enterrada: só o mostrador e o telhado saem da areia."""
    st = K.mat_brick("silhar", ("wall", T*2), 4.0, (.085, .078, .07), 3.5, 0.0, T, .32, .018)
    box(st, (0, 0, 5.0), (2.4, 2.4, 10.0), bevel=.02)
    for (x, y, rz) in [(0, -1.22, 0), (1.22, 0, 90)]:
        cyl(K.mat_porcelain(), (x, y, 8.6), .8, .06, (90, 0, rz), 32)
        torus(m["brass"], (x, y, 8.6), .82, .05, (90, 0, rz))
        for k in range(12):
            a = math.radians(30*k)
            p = (x + (math.cos(a)*.65 if rz == 0 else 0), y + (math.cos(a)*.65 if rz else 0), 8.6 + math.sin(a)*.65)
            sphere(K.mat_solid("marca", (.02, .02, .02)), p, (.04, .04, .04), segs=6)
        n = -.04 if rz == 0 else .04
        box(K.mat_solid("ponteiro", (.02, .02, .02), .8, .4), (x + (0 if rz == 0 else n), y + (n if rz == 0 else 0), 8.75), (.04 if rz == 0 else .02, .02 if rz == 0 else .04, .35), (0, 30 if rz == 0 else 0, 0), 0)
    cyl(K.mat_stone("ardosia", (.045, .045, .05), (.015, .015, .018), 6, .2), (0, 0, 11.0), 1.9, 2.2, verts=4, r2=0)
    box(m["iron"], (0, 0, 12.4), (.06, .06, .8), bevel=0)
    box(K.mat_solid("vao", (.004, .004, .004)), (0, -1.21, 7.4), (.7, .05, .8), bevel=0)     # janela de entrada
    for k in range(5): box(m["wood"], (0, -1.6 - k*.2, 7.1 - k*.08), (.6, .2, .04), bevel=0)
    dunas_em_volta((5, 5), seed, 1.0)
    return {}

@asset("predios", fp=(4, 4), samples=40, bury=2.0)
def torre_sino(m, seed=155):
    """Campanário de madeira e ferro com o sino rachado (Rua do Sino)."""
    for sx in (-1, 1):
        for sy in (-1, 1): along(m["wood_d"], (sx*.8, sy*.8, 0), (sx*.5, sy*.5, 5.5), .09, verts=8)
    for z in (2.5, 4.0):
        for sx in (-1, 1): box(m["wood_d"], (sx*.6, 0, z), (.08, 1.3, .08), bevel=.005); box(m["wood_d"], (0, sx*.6, z), (1.3, .08, .08), bevel=.005)
    box(m["tin"], (0, 0, 5.9), (1.6, 1.6, .05), (12, 0, 0), .003)
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=.5, radius2=.25, depth=.8, location=(0, 0, 4.9))
    o = bpy.context.object; o.data.materials.append(m["brass"])
    box(K.mat_solid("racha", (.01, .01, .01)), (.25, -.37, 4.8), (.02, .02, .6), (0, 15, 0), 0)
    along(K.mat_solid("corda", (.1, .08, .05)), (0, 0, 4.5), (.4, -.6, 2.0), .012, verts=4)
    dunas_em_volta((4, 4), seed, .8)
    return {}

@asset("props", bury=1.6)
def janela_na_areia(m, seed=156):
    """Janela de sobrado aparecendo na areia: entrada para as casas de baixo."""
    c = m["brick_p"]
    box(c, (0, 0, 1.4), (1.6, .3, 2.8), bevel=.01)
    box(K.mat_solid("vao", (.004, .004, .004)), (0, -.01, 1.9), (.8, .32, 1.1), bevel=0)
    box(m["wood_d"], (0, -.17, 2.5), (.9, .04, .08), bevel=0)
    box(m["wood_d"], (-.45, -.25, 1.9), (.06, .25, 1.1), (0, 0, -40), 0)
    for k in range(4): box(m["wood"], (0, -.4 - k*.2, 1.5 - k*.07), (.6, .2, .04), bevel=0)
    duna((0, -.6, 1.4), 1.2, .9, .35, seed)
    return {}

@asset("props", bury=1.2)
def placa_rua_enterrada(m, seed=157):
    """Placa esmaltada de rua de São Lázaro, só o topo para fora da areia."""
    cyl(m["iron"], (0, 0, 1.0), .03, 2.0, (6, 0, 0), 6)
    box(K.mat_solid("esmalte_azul", (.03, .05, .09), .2, .3), (.3, -.03, 1.85), (.6, .02, .18), (0, 0, 0), .005)
    box(K.mat_solid("letras", (.3, .28, .24)), (.3, -.045, 1.85), (.45, .005, .05), bevel=0)
    duna((0, 0, 1.2), .5, .5, .15, seed)
    return {}

@asset("paredes", walls=True)
def muro_contencao_areia(m, seed=158):
    """Muro de contenção de tábuas e sacos segurando a duna (adro da capela)."""
    r = rnd(seed); L = T
    for x in (-L/2 + .05, L/2 - .05): cyl(m["wood_d"], (x, 0, .7), .05, 1.4, (r.uniform(-5, 5), 8, 0), 6)
    for k in range(5): box(m["wood"], (0, .02, .15 + k*.25), (L, .04, .22), (r.uniform(-2, 2), 0, r.uniform(-2, 2)), .005)
    for k in range(2):
        o = sphere(m["sack"], (r.uniform(-.15, .15), -.15, .12 + k*.18), (.2, .12, .09)); displace(o, .015, .2, seed+k, 1)
    duna((0, .5, -.1), L*.7, .5, 1.3, seed)
    return {}

@asset("predios", fp=(10, 4), samples=40)
def ponte_ferro_bonde(m, seed=159):
    """Ponte de ferro treliçada da Linha 7 sobre o leito seco do rio."""
    Lp, W = 6.0, 1.6
    for sx in (-1, 1):
        box(m["rust"], (sx*W/2, 0, 1.2), (.12, Lp, .15), bevel=.005)
        box(m["rust"], (sx*W/2, 0, 2.6), (.12, Lp, .12), bevel=.005)
        for k in range(9):
            y = -Lp/2 + k*Lp/8
            box(m["rust"], (sx*W/2, y, 1.9), (.08, .08, 1.4), bevel=0)
            if k < 8: along(m["rust"], (sx*W/2, y, 1.2), (sx*W/2, y + Lp/8, 2.6), .04, verts=4)
        for k in range(2): cyl(m["dark_stone"], (sx*W/2, (k*2 - 1)*Lp/2, .5), .35, 1.4, verts=8)
    for k in range(20): box(m["wood_d"], (0, -Lp/2 + .15 + k*.3, 1.3), (W + .2, .14, .06), bevel=.005)
    for sx in (-1, 1): box(m["iron"], (sx*.36, 0, 1.38), (.06, Lp, .06), bevel=0)
    for k in range(4): box(m["iron"], (0, -Lp/2 + k*2, 2.6), (W, .06, .06), bevel=0)
    return {}

@asset("predios", fp=(5, 5), samples=40)
def moinho_ruina(m, seed=160):
    """Moinho de vento de ferro parado, com pás rasgadas."""
    for k in range(4):
        a = math.radians(45 + 90*k)
        along(m["rust"], (math.cos(a)*.9, math.sin(a)*.9, 0), (math.cos(a)*.2, math.sin(a)*.2, 6.0), .05, verts=6)
    for z in (1.5, 3.0, 4.5):
        rr = .9 - z/6*.7
        for k in range(4):
            a0, a1 = math.radians(45 + 90*k), math.radians(135 + 90*k)
            along(m["rust"], (math.cos(a0)*rr, math.sin(a0)*rr, z), (math.cos(a1)*rr, math.sin(a1)*rr, z + .6), .02, verts=4)
    cyl(m["iron"], (0, -.3, 6.1), .15, .6, (90, 0, 0), 10)
    r = rnd(seed)
    for k in range(10):
        a = math.radians(36*k + 7)
        if k in (3, 7): continue
        along(m["tin"], (0, -.6, 6.1), (math.cos(a)*1.6, -.6, 6.1 + math.sin(a)*1.6), .015, verts=4)
        box(m["tin"], (math.cos(a)*1.1, -.62, 6.1 + math.sin(a)*1.1), (.5, .02, .25), (0, -math.degrees(a), 0), 0)
    box(m["tin"], (0, .7, 6.1), (.02, 1.0, .6), bevel=0)
    cyl(m["brass"], (1.2, 1.0, .5), .5, 1.0, verts=16)
    return {}

@asset("props", fp=(2, 3), samples=40)
def roda_dagua(m, seed=161):
    """Roda d'água parada no leito seco, com pás quebradas."""
    for sx in (-1, 1):
        torus(m["wood_d"], (sx*.3, 0, 1.2), 1.1, .06, (0, 90, 0))
        torus(m["wood_d"], (sx*.3, 0, 1.2), .3, .05, (0, 90, 0))
    for k in range(12):
        a = math.radians(30*k)
        if k == 5: continue
        box(m["wood"], (0, math.cos(a)*1.05, 1.2 + math.sin(a)*1.05), (.7, .04, .3), (math.degrees(a), 0, 0), .005)
        along(m["wood_d"], (.3, 0, 1.2), (.3, math.cos(a)*1.1, 1.2 + math.sin(a)*1.1), .025, verts=4)
    cyl(m["iron"], (0, 0, 1.2), .08, 1.2, (0, 90, 0), 10)
    for sx in (-1, 1): box(m["dark_stone"], (sx*.7, 0, .6), (.3, .6, 1.2), bevel=.02)
    return {}

@asset("props", fp=(2, 3), samples=40)
def roda_dagua_bomba(m, seed=162):
    """Roda d'água convertida em bomba a vapor pelos sobreviventes (puxa lama amarga)."""
    roda_dagua(m, seed)
    cyl(m["brass"], (1.0, .3, .6), .3, 1.2, verts=16)
    along(m["brass"], (1.0, .3, 1.2), (1.0, .3, 2.0), .06)
    along(m["brass"], (1.0, .3, 2.0), (1.8, 1.0, 1.9), .06)
    cyl(m["brass"], (1.05, -.02, .8), .1, .04, (90, 0, 0), 12)
    box(K.mat_emit("fornalha", (1, .35, .06), 4), (1.0, .0, .35), (.2, .02, .12), bevel=0)
    point((1.0, -.4, .4), (1, .4, .1), 15, .1)
    return {"luz": "quente"}

@asset("props", fp=(3, 3), samples=40)
def tanque_sebo(m, seed=163):
    """Tanque de sebo do abatedouro: caldeirão de ferro com gordura borbulhando."""
    cyl(m["rust"], (0, 0, .8), 1.0, 1.6, verts=28)
    for z in (.3, 1.3): torus(m["iron"], (0, 0, z), 1.01, .04)
    cyl(K.mat_solid("sebo", (.22, .18, .1), 0, .2), (0, 0, 1.55), .95, .04, verts=28)
    for k in range(4): sphere(K.mat_solid("sebo", (.22, .18, .1), 0, .2), (.3*k - .4, .2*(k % 2), 1.58), (.1, .1, .05), segs=8)
    for k in range(3):
        a = math.radians(120*k)
        along(m["iron"], (math.cos(a)*.9, math.sin(a)*.9, 0), (math.cos(a)*1.2, math.sin(a)*1.2, -.05), .06, verts=6)
    cyl(m["coal"], (0, 0, .05), .7, .05, verts=16)
    flame((0, -.8, .05), 1.0)
    along(m["rust"], (.9, .4, .5), (1.8, 1.0, .1), .1, verts=10)
    return {"luz": "quente"}

@asset("paredes", walls=True)
def cerca_chiqueiro(m, seed=164):
    r = rnd(seed); L = T
    for x in (-L/2 + .04, L/2 - .04): cyl(m["wood_d"], (x, 0, .45), .045, .9, (r.uniform(-5, 5), r.uniform(-5, 5), 0), 6)
    for z in (.25, .55, .8): box(r.choice([m["wood"], m["tin"]]), (0, 0, z), (L, .03, .15), (r.uniform(-4, 4), 0, 0), .005)
    return {}

@asset("paredes", walls=True)
def cerca_arame_torta(m, seed=165):
    r = rnd(seed); L = T
    for x in (-L/2, L/2): cyl(m["rust"], (x, 0, .5), .025, 1.0, (r.uniform(-12, 12), r.uniform(-12, 12), 0), 6)
    for z in (.3, .6, .9):
        pts = [Vector((-L/2 + L*t/5, r.uniform(-.03, .03), z - math.sin(t/5*math.pi)*r.uniform(.05, .2))) for t in range(6)]
        for p, q in zip(pts, pts[1:]): along(m["iron"], p, q, .005, verts=3)
    return {}

@asset("props")
def estacas_cerca(m, seed=166):
    r = rnd(seed)
    for k in range(5): cyl(m["wood_d"], (-.6 + k*.3, r.uniform(-.05, .05), .4), .045, r.uniform(.5, .9), (r.uniform(-15, 15), r.uniform(-15, 15), 0), 6)
    return {}

@asset("props", fp=(3, 2))
def toca_caes(m, seed=167):
    """Toca da matilha: buraco na duna com ossos roídos e trapos."""
    duna((0, .3, -.1), 1.2, .9, .9, seed)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, location=(0, -.35, .25)); o = bpy.context.object
    o.scale = (.45, .3, .3); o.data.materials.append(K.mat_solid("buraco", (.003, .002, .002), 0, 1))
    r = rnd(seed)
    for k in range(8):
        a = Vector((r.uniform(-.8, .8), r.uniform(-1.0, -.5), .02)); d = Vector((r.uniform(-1, 1), r.uniform(-1, 1), 0)).normalized()
        along(m["bone"], a, a + d*r.uniform(.12, .25), .015, verts=5)
    return {}

@asset("props", fp=(3, 2))
def vala_aberta(m, seed=168):
    """Vala aberta pela maré de areia, com soldados da Grande Batalha aparecendo."""
    cyl(K.mat_solid("fundo_vala", (.008, .006, .005), 0, .9), (0, 0, .005), 1.0, .01, verts=24).scale = (1.4, .6, 1)
    for k in range(3): corpo(m, (-.6 + k*.6, 0, .0), 90 + k*15, seed + k)
    for sx in (-1, 1): duna((0, sx*.75, -.1), 1.5, .35, .3, seed + sx)
    return {}

@asset("props")
def cova_aberta(m, seed=169):
    box(K.mat_solid("fundo_vala", (.008, .006, .005), 0, .9), (0, 0, .005), (.7, 1.5, .01), bevel=0)
    for sx in (-1, 1): duna((sx*.55, 0, -.05), .3, .8, .25, seed + sx)
    along(m["wood"], (.5, .5, 0), (.7, .9, 1.0), .025, verts=5)
    box(m["rust"], (.72, .95, 1.05), (.18, .03, .22), (0, 20, 0), .003)
    return {}

@asset("props")
def tumulo_aberto(m, seed=170):
    st = K.mat_stone("pedra_tumulo", (.11, .105, .1), (.04, .04, .04), 2.5, .7)
    for (x, y, w, d) in [(0, .7, 1.0, .12), (0, -.7, 1.0, .12), (-.45, 0, .12, 1.4), (.45, 0, .12, 1.4)]:
        box(st, (x, y, .2), (w, d, .4), bevel=.02)
    box(K.mat_solid("vao", (.004, .004, .004)), (0, 0, .2), (.8, 1.3, .02), bevel=0)
    box(st, (.6, .3, .1), (.9, 1.5, .1), (0, 20, 25), .02)
    sphere(m["bone"], (0, .4, .25), (.08, .09, .08), segs=10)
    return {}

@asset("props")
def vela_tumulo(m, seed=171):
    r = rnd(seed)
    for k in range(5): candle((r.uniform(-.15, .15), r.uniform(-.15, .15), 0), r.uniform(.06, .18), light=k == 0)
    cyl(K.mat_solid("cera", (.38, .33, .24), 0, .5), (0, 0, .01), .2, .02, verts=12)
    return {"luz": "velas"}

@asset("props", fp=(3, 1))
def varal_roupas(m, seed=172):
    r = rnd(seed)
    for x in (-1.0, 1.0): cyl(m["wood_d"], (x, 0, .9), .035, 1.8, (0, r.uniform(-5, 5), 0), 6)
    along(K.mat_solid("corda", (.1, .08, .05)), (-1, 0, 1.7), (1, 0, 1.7), .006, verts=4)
    for k in range(5):
        col = [(.1, .02, .015), (.04, .06, .08), (.12, .1, .07), (.06, .05, .03), (.15, .14, .12)][k]
        o = box(K.mat_cloth(f"roupa{k}", col, 50.0 + k), (-.8 + k*.4, 0, 1.45), (.3, .02, .45), (0, 0, r.uniform(-10, 10)), 0); displace(o, .02, .2, seed + k, 2)
    return {}

@asset("props")
def espantalho_arame(m, seed=173):
    """Espantalho de arame e trapos com máscara de gás."""
    cyl(m["wood_d"], (0, 0, .9), .04, 1.8, verts=6)
    cyl(m["wood_d"], (0, 0, 1.45), .03, 1.2, (0, 90, 0), 6)
    o = box(K.mat_cloth("trapos", (.08, .06, .04), 51.0), (0, 0, 1.15), (.5, .2, .7), bevel=0); displace(o, .04, .2, seed, 2)
    sphere(K.mat_solid("mascara", (.05, .05, .045), .3, .5), (0, 0, 1.75), (.12, .13, .14))
    for sx in (-1, 1): sphere(K.mat_emit("lente_verde", (.4, 1, .15), 3), (sx*.05, -.12, 1.78), (.035, .02, .035), segs=8)
    cyl(m["rust"], (0, -.15, 1.68), .04, .1, (90, 0, 0), 8)
    for k in range(6): torus(m["iron"], (0, 0, .5 + k*.15), .12, .004, (k*20, 0, 0))
    return {"emissivo": "lentes"}

@asset("props")
def estandarte_rasgado(m, seed=174):
    cyl(m["wood_d"], (0, 0, 1.2), .03, 2.4, (8, -6, 0), 6)
    o = box(K.mat_cloth("estandarte", (.1, .015, .01), 12.0), (.3, 0, 1.9), (.55, .02, .9), bevel=0); displace(o, .05, .2, seed, 3)
    box(K.mat_solid("ouro_sujo", (.4, .28, .09), .8, .4), (.3, -.02, 2.0), (.1, .01, .4), bevel=0)
    return {}

@asset("props")
def elmo_espada_fincada(m, seed=175):
    """Espada fincada na areia com elmo pendurado: túmulo de soldado da Grande Batalha."""
    box(m["iron"], (0, 0, .5), (.06, .015, 1.0), (0, 6, 0), .003)
    box(m["brass"], (0, 0, 1.0), (.3, .04, .04), (0, 6, 0), .003)
    sphere(K.mat_metal("capacete", (.05, .055, .045), .5, 3.0), (.06, -.02, 1.12), (.14, .14, .1))
    duna((0, 0, -.05), .4, .4, .12, seed)
    return {}

@asset("props", fp=(3, 2), samples=40)
def asa_anjo_caida(m, seed=176):
    """Asa de anjo gigante caída na areia, penas sujas e tira de couro."""
    feather = K.mat_solid("pena", (.3, .28, .24), 0, .7); r = rnd(seed)
    along(m["bone"], (-1.2, 0, .1), (1.2, .3, .3), .06, verts=8)
    for k in range(18):
        t = k/17; base = Vector((-1.2 + 2.4*t, .3*t, .2))
        box(feather, tuple(base + Vector((0, -.5, 0))), (.18, 1.0 - t*.4, .015), (r.uniform(-8, 8), 0, r.uniform(-10, 10)), 0)
    box(K.mat_solid("couro", (.05, .03, .02), 0, .6), (-1.0, .05, .22), (.1, .5, .02), bevel=0)
    duna((.3, .4, -.1), 1.0, .5, .25, seed)
    return {}

@asset("props")
def braseiro_sagrado(m, seed=177):
    """Braseiro dos Arautos com chama branca."""
    for k in range(3):
        a = math.radians(120*k)
        along(K.mat_solid("ouro_sujo", (.4, .28, .09), .8, .4), (math.cos(a)*.3, math.sin(a)*.3, 0), (math.cos(a)*.18, math.sin(a)*.18, .9), .025, verts=6)
    cyl(K.mat_solid("ouro_sujo", (.4, .28, .09), .8, .4), (0, 0, .95), .3, .2, verts=16, r2=.2)
    fm = K.mat_emit("chama_branca", (1, .92, .8), 14)
    rr = rnd(seed)
    for k in range(6): cyl(fm, (rr.uniform(-.06, .06), rr.uniform(-.06, .06), 1.2), rr.uniform(.04, .07), rr.uniform(.2, .4), (rr.uniform(-10, 10), rr.uniform(-10, 10), 0), 7, r2=0)
    point((0, 0, 1.4), (1, .9, .8), 120, .15)
    return {"luz": "sagrada"}

@asset("props")
def lanterna_procissao(m, seed=178):
    cyl(m["wood_d"], (0, 0, 1.0), .025, 2.0, verts=6)
    along(m["iron"], (0, 0, 2.0), (.3, 0, 2.05), .015, verts=4)
    cyl(m["iron"], (.3, 0, 1.85), .08, .25, verts=6)
    cyl(K.mat_emit("vidro_lampiao", (1, .62, .28), 5), (.3, 0, 1.85), .065, .2, verts=6)
    box(K.mat_cloth("fita", (.1, .015, .01), 52.0), (.05, 0, 1.6), (.04, .01, .5), bevel=0)
    point((.3, 0, 1.85), (1, .6, .28), 30, .05)
    return {"luz": "quente"}

@asset("vegetacao")
def moita_cardo(m, seed=179):
    """Moita de cardo roxo, a única planta que gosta do Amargo."""
    r = rnd(seed)
    stem = K.mat_solid("cardo_caule", (.05, .055, .035), 0, .7)
    flower = K.mat_solid("cardo_flor", (.18, .04, .2), 0, .6)
    for k in range(9):
        a = Vector((r.gauss(0, .12), r.gauss(0, .12), 0)); d = Vector((r.uniform(-.4, .4), r.uniform(-.4, .4), 1)).normalized()
        h = r.uniform(.4, .8); top = a + d*h
        along(stem, a, top, .015, .008, verts=5)
        sphere(stem, tuple(top), (.05, .05, .05), segs=8)
        for j in range(10):
            dd = Vector((r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(.3, 1))).normalized()
            along(flower, top, top + dd*.07, .006, .001, verts=3)
        for j in range(3):
            p = a + d*h*r.uniform(.2, .7); dd = Vector((r.uniform(-1, 1), r.uniform(-1, 1), .2)).normalized()
            along(stem, p, p + dd*.15, .02, .002, verts=3)
    return {}

@asset("vegetacao")
def cogumelos_palidos(m, seed=180):
    """Cogumelos pálidos que brilham verde fraco (Bosque das Viúvas)."""
    r = rnd(seed)
    cap = K.mat_solid("cogumelo", (.3, .3, .25), 0, .5)
    for k in range(9):
        x, y = r.gauss(0, .2), r.gauss(0, .2); h = r.uniform(.06, .22)
        cyl(K.mat_solid("pe_cogumelo", (.25, .24, .2), 0, .6), (x, y, h/2), .015 + h*.08, h, verts=8)
        sphere(cap, (x, y, h), (.04 + h*.35, .04 + h*.35, .02 + h*.15), segs=12)
        sphere(glow_green(1.5), (x, y, h - .01), (.035 + h*.3, .035 + h*.3, .008), segs=10)
    point((0, 0, .2), (.4, 1, .15), 4, .2)
    return {"emissivo": "verde fraco"}

@asset("vegetacao", fp=(4, 4), samples=40)
def arvore_enforcados(m, seed=181):
    """Árvore morta grande com cordas de enforcados (Ponte dos Enforcados / bosque)."""
    _tree(m, seed, 2.0, .24, 5)
    rope = K.mat_solid("corda", (.1, .08, .05)); r = rnd(seed)
    for k in range(3):
        x, y = r.uniform(-1, 1), r.uniform(-1, 1)
        along(rope, (x, y, 3.0), (x, y, 1.8), .01, verts=4)
        torus(rope, (x, y, 1.75), .08, .012, (90, 0, 0))
    return {}

@asset("decalques")
def vidro_estilhacos(m, seed=182):
    r = rnd(seed); g = K.mat_solid("vidro_verde", (.05, .1, .06), 0, .05)
    for k in range(25):
        box(g, (r.uniform(-.6, .6), r.uniform(-.5, .5), .005), (r.uniform(.03, .12), r.uniform(.02, .08), .006), (0, 0, r.uniform(0, 180)), 0)
    return {}

@asset("decalques")
def penas_espalhadas(m, seed=183):
    r = rnd(seed); f = K.mat_solid("pena", (.3, .28, .24), 0, .7)
    for k in range(16): box(f, (r.uniform(-.6, .6), r.uniform(-.5, .5), .006), (.15, .04, .006), (r.uniform(-8, 8), 0, r.uniform(0, 180)), 0)
    return {}

@asset("vegetacao", fp=(4, 3))
def duna_ondulacao(m, seed=184):
    """Duna baixa e larga com crista (Mar de Dunas e Estrada do Sul)."""
    duna((0, 0, -.2), 2.2, 1.4, .8, seed); duna((.9, .6, -.2), 1.4, 1.0, .55, seed + 1); return {}

@asset("props", fp=(4, 4), samples=40)
def sumidouro(m, seed=185):
    """O Sumidouro: funil de areia onde o rio some, com brilho verde no fundo."""
    r = rnd(seed)
    for k in range(14):
        a = math.radians(360*k/14)
        duna((math.cos(a)*1.4, math.sin(a)*1.2, -.15), .7, .6, .35, seed + k)
    cyl(K.mat_solid("fundo", (.004, .004, .003), 0, .9), (0, 0, .005), 1.1, .01, verts=32)
    sphere(glow_green(2.5), (0, 0, .0), (.5, .4, .02))
    point((0, 0, .4), (.4, 1, .15), 40, .4)
    return {"emissivo": "brilho verde"}

@asset("props")
def cano_esgoto(m, seed=186):
    """Boca de cano de esgoto do abatedouro despejando lama vermelha no leito."""
    cyl(m["rust"], (0, .4, .35), .35, 1.2, (80, 0, 0), 16)
    torus(m["iron"], (0, -.18, .3), .36, .04, (80, 0, 0))
    _pool(K.mat_solid("lama_vermelha", (.06, .01, .006), 0, .15), .8, .5, seed, 4)
    duna((0, .8, -.1), .9, .6, .55, seed)
    return {}

@asset("props", fp=(2, 3))
def corpo_lacrado(m, seed=187):
    """Corpo lacrado em mortalha costurada com ferro (aguardando o Juízo)."""
    shroud = K.mat_cloth("mortalha", (.14, .12, .09), 53.0)
    o = sphere(shroud, (0, 0, .15), (.22, .85, .14)); displace(o, .02, .2, seed, 1)
    for k in range(5): torus(m["iron"], (0, -.6 + k*.3, .15), .2, .012, (90, 0, 0))
    box(K.mat_solid("lacre", (.2, .02, .015), 0, .4), (0, .1, .29), (.08, .08, .02), bevel=0)
    return {}

@asset("props", fp=(2, 2))
def carrinho_tobias(m, seed=188):
    """Carrinho de mão de sucata do Tobias, cheio de quinquilharias."""
    box(m["rust"], (0, 0, .45), (.7, 1.0, .35), bevel=.01)
    torus(m["iron"], (0, -.65, .2), .2, .04, (0, 90, 0))
    for sx in (-1, 1): along(m["wood_d"], (sx*.3, .4, .5), (sx*.35, 1.1, .7), .025, verts=5)
    r = rnd(seed)
    for k in range(8):
        mat = r.choice([m["brass"], m["tin"], m["wood"], m["bone"]])
        box(mat, (r.uniform(-.25, .25), r.uniform(-.35, .35), .7 + r.uniform(0, .15)), (r.uniform(.08, .2),)*3, (r.uniform(0, 40),)*3, .005)
    return {}

@asset("props", fp=(2, 1))
def cocho(m, seed=189):
    box(m["wood_d"], (0, 0, .2), (1.2, .4, .3), bevel=.01)
    box(K.mat_solid("lavagem", (.07, .05, .03), 0, .2), (0, 0, .33), (1.1, .32, .02), bevel=0)
    return {}

@asset("decalques")
def lama_porcos(m, seed=190):
    _pool(K.mat_solid("lama", (.03, .022, .015), 0, .3), .9, .7, seed, 6); return {}

@asset("props", fp=(2, 2), samples=40)
def capelinha_beira(m, seed=191):
    """Capelinha de beira de estrada com santo sem rosto e velas."""
    st = K.mat_stone("pedra_tumulo", (.11, .105, .1), (.04, .04, .04), 2.5, .7)
    box(st, (0, 0, .5), (.6, .5, 1.0), bevel=.02)
    box(st, (0, 0, 1.25), (.7, .6, .5), bevel=.02)
    cyl(st, (0, 0, 1.65), .5, .35, verts=4, r2=0)
    box(K.mat_solid("vao", (.004, .004, .004)), (0, -.26, 1.25), (.4, .05, .4), bevel=0)
    sphere(K.mat_porcelain(), (0, -.2, 1.2), (.06, .05, .14))
    for k in range(3): candle((-.15 + k*.15, -.35, 1.0), .08, light=k == 1)
    return {"luz": "velas"}

@asset("predios", fp=(4, 4), samples=40)
def posto_odete(m, seed=192):
    """Posto da Odete: barraca de sucata e lona junto ao bonde tombado, com balcão e lanterna."""
    barraco_sucata(m, seed)
    box(m["wood"], (0, -1.6, .5), (1.6, .4, .08), bevel=.01)
    for sx in (-1, 1): box(m["wood_d"], (sx*.7, -1.6, .25), (.08, .35, .5), bevel=.005)
    o = box(m["cloth"], (0, -1.7, 2.1), (2.4, 1.2, .03), (-15, 0, 0), 0); displace(o, .04, .3, seed, 3)
    return {}

@asset("props", fp=(2, 2))
def pulpito_externo(m, seed=193):
    """Púlpito dos Arautos no adro, de pedra com estandarte e livro acorrentado."""
    st = K.mat_stone("marmore_sujo", (.2, .19, .17), (.06, .058, .055), 3, .6)
    for k in range(2): box(st, (0, .2 - k*.3, .1 + k*.2), (1.2, .5 - k*.1, .2), bevel=.02)
    cyl(st, (0, 0, .9), .35, 1.2, verts=8, r2=.45)
    box(K.mat_solid("livro", (.08, .02, .015), 0, .5), (0, -.1, 1.55), (.4, .3, .08), (-20, 0, 0), .01)
    chain(m["iron"], (.2, -.2, 1.5), (.35, -.3, .9), 6, .02)
    estandarte_rasgado(m, seed)
    return {}

@asset("props", fp=(2, 2), samples=40)
def trono_sucata(m, seed=194):
    """Trono de sucata dos demônios no telhado dos fundos da capela."""
    r = rnd(seed)
    box(m["rust"], (0, 0, .25), (1.0, .8, .5), bevel=.01)
    box(m["rust"], (0, .35, 1.1), (1.0, .12, 1.4), bevel=.01)
    for k in range(7):
        along(m["iron"], (-.45 + k*.15, .4, 1.7), (-.45 + k*.15 + r.uniform(-.1, .1), .45, 2.2 + r.uniform(0, .4)), .03, .005, verts=5)
    for sx in (-1, 1): box(m["tin"], (sx*.5, 0, .7), (.1, .7, .3), bevel=.005)
    sphere(m["bone"], (.35, -.2, .58), (.08, .09, .08), segs=10)
    box(K.mat_emit("brasa", (1, .3, .05), 5), (0, .29, 1.0), (.3, .01, .05), bevel=0)
    return {"emissivo": "brasa"}

@asset("predios", fp=(4, 4), samples=40)
def tenda_demonio(m, seed=195):
    """Tenda dos demônios: couro negro esticado em ossos, com brasa e correntes."""
    tenda_vigilia(m, seed)
    return {}

@asset("props", fp=(2, 2))
def caldeirao_cardo(m, seed=196):
    """Caldeirão com caldo de cardo roxo fervendo (alquimia da Vigília)."""
    sphere(m["iron"], (0, 0, .4), (.45, .45, .35))
    cyl(K.mat_emit("caldo_cardo", (.5, .1, .6), 1.5), (0, 0, .62), .38, .02, verts=20)
    for k in range(3):
        a = math.radians(120*k); along(m["iron"], (math.cos(a)*.35, math.sin(a)*.35, .2), (math.cos(a)*.5, math.sin(a)*.5, 0), .03, verts=5)
    flame((0, 0, .02), .8)
    moita_cardo(m, seed)
    return {"emissivo": "caldo roxo", "luz": "quente"}

@asset("props", fp=(2, 3))
def forca_ponte(m, seed=197):
    for sx in (-1, 1): cyl(m["wood_d"], (sx*.7, 0, 1.4), .07, 2.8, verts=8)
    box(m["wood_d"], (0, 0, 2.8), (1.6, .14, .14), bevel=.01)
    rope = K.mat_solid("corda", (.1, .08, .05))
    along(rope, (0, 0, 2.75), (0, 0, 1.9), .01, verts=4); torus(rope, (0, 0, 1.82), .09, .012, (90, 0, 0))
    return {}

@asset("decalques")
def ralo_ferro_chao(m, seed=198):
    box(m["iron"], (0, 0, .005), (.5, .5, .01), bevel=.005)
    for k in range(6): box(K.mat_solid("abismo", (.002, .001, .001)), (-.2 + k*.08, 0, .011), (.03, .42, .002), bevel=0)
    return {}

alias("casa_coveiro", "mausoleu")
alias("cratera_corte", "cratera_cinza")
alias("mesa_acougue_rua", "mesa_acougue", dungeon=False, cat="props")

for _n in ("trilhos_no_abismo", "ponte_rompida", "telhado_no_abismo", "torre_no_abismo"):
    REG[_n]["no_catcher"] = True

# ================================================================ fachadas detalhadas (v2)
def bay(m, c, cx, cy, z, bw, FH, axis, kind="dark", seed=0, t=.25):
    """Vão de fachada com janela de verdade: pilares, peitoril, verga, rebaixo escuro,
    caixilho e variações (acesa com cortina, vidro quebrado, tapada com tábuas, porta)."""
    r = rnd(seed)
    ww, wh, wz = bw*.5, FH*.48, z + FH*.32
    if kind == "door": ww, wh, wz = bw*.42, FH*.78, z + .02
    def P(u, v_, du, dv, dz, zz, mat, inset=0.0):
        # u ao longo da fachada, v_ para fora (normal)
        if axis == "x": return box(mat, (cx + u, cy - v_ - inset, zz), (du, dv, dz), bevel=.006)
        else: return box(mat, (cx + v_ + inset, cy + u, zz), (dv, du, dz), bevel=.006)
    side = (bw - ww)/2
    P(-bw/2 + side/2, 0, side + .01, t, FH, z + FH/2, c)
    P(bw/2 - side/2, 0, side + .01, t, FH, z + FH/2, c)
    if wz - z > .01: P(0, 0, ww + .01, t, wz - z, z + (wz - z)/2, c)
    top = z + FH - (wz + wh); P(0, 0, ww + .01, t, top, wz + wh + top/2, c)
    # rebaixo e fundo
    inner = K.mat_solid("interior", (.006, .005, .005), 0, .9)
    if kind == "lit": inner = K.mat_window_lit()
    P(0, -t*.5, ww, .02, wh, wz + wh/2, inner)
    for s in (-1, 1): P(s*(ww/2 - .02), -.0, .04, t*.9, wh, wz + wh/2, K.mat_solid("reboco_interno", (.05, .045, .04), 0, .9))
    # peitoril saliente e verga
    if kind != "door": P(0, t/2 + .04, ww + .2, .1, .06, wz - .03, c)
    P(0, t/2 + .02, ww + .14, .06, .1, wz + wh + .05, c)
    if kind in ("dark", "lit", "broken"):
        frame = m["rust"] if r.random() < .5 else m["wood_d"]
        P(0, t*.2, ww, .03, .035, wz + wh*.5, frame); P(0, t*.2, .035, .03, wh, wz + wh/2, frame)
    if kind == "lit":
        P(-ww*.28, t*.15, ww*.4, .01, wh*.9, wz + wh*.52, K.mat_cloth("cortina", (.12, .03, .02), 60.0))
    if kind == "broken":
        for k in range(3): P(r.uniform(-ww/3, ww/3), t*.25, r.uniform(.05, .15), .005, r.uniform(.1, .3), wz + r.uniform(.1, wh - .1), K.mat_solid("vidro_verde", (.05, .1, .06), 0, .05))
    if kind == "boarded":
        for k in range(3): P(0, t/2 + .02, ww + .1, .03, .12, wz + wh*(k + .5)/3, m["wood"], 0)
    if kind == "door":
        P(0, t*.3, ww*.9, .04, wh*.95, wz + wh/2, m["rust"])
        for k in range(3): P(0, t*.3 + .03, ww*.9, .01, .05, wz + wh*(k + .5)/3, m["iron"])

