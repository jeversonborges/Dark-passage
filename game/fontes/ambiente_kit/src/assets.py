# Modelos do kit de ambiente. Cada função monta o objeto em volta da origem
# (centro da base no chão) e devolve um dict com metadados.
# Escala: metros. Personagem tem 1,8 m. Tile = K.T (0,7071 m).
import bpy, math, random
from mathutils import Vector
import kit as K
from kit import prism, box, cyl, sphere, along, torus, displace, crumble, flame, candle, chain, point
T = K.T
REG = {}
def asset(cat, fp=(1, 1), dungeon=False, walls=False, samples=48):
    def deco(fn):
        REG[fn.__name__] = dict(fn=fn, cat=cat, fp=fp, dungeon=dungeon, walls=walls, samples=samples); return fn
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

@asset("predios", fp=(12, 16), samples=64)
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
    for sx in (-1, 1):
        ang = math.degrees(math.atan2(2.6, W/2))
        if sx > 0:
            for k in range(6):
                if k in (2, 3): continue  # telhado desabado
                y0 = -D/2 + D/6*(k+.5)
                box(slate, (sx*W/4, y0, H + 1.3), (W/2*1.2, D/6 + .02, .14), (0, -sx*ang, 0), .01)
            for k in (2, 3):  # vigas expostas
                y0 = -D/2 + D/6*(k+.5)
                box(m["wood_d"], (sx*W/4, y0 - .4, H + 1.3), (W/2*1.15, .12, .14), (0, -sx*ang, 0), .01)
                box(m["wood_d"], (sx*W/4, y0 + .4, H + 1.3), (W/2*1.15, .12, .14), (0, -sx*ang + 4, 0), .01)
        else:
            box(slate, (sx*W/4, 0, H + 1.3), (W/2*1.2, D + .3, .14), (0, -sx*ang, 0), .01)
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

@asset("predios", fp=(14, 12), samples=64)
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

@asset("predios", fp=(4, 4), samples=64)
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

@asset("predios", fp=(4, 4), samples=64)
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

@asset("props", fp=(3, 3), samples=64)
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

@asset("props", fp=(2, 2), samples=64)
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

@asset("props", fp=(3, 3))
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

@asset("chefes", fp=(6, 6), dungeon=True, samples=64)
def arena_moedor(m, seed=53):
    """Chefe 1 (Porão do Matadouro): o grande moedor de carne a vapor, centro da arena."""
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

@asset("chefes", fp=(6, 6), dungeon=True, samples=64)
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

@asset("chefes", fp=(6, 6), dungeon=True, samples=64)
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
