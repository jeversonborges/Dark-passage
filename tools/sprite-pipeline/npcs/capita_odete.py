# Odete Ferrolho, Capitã da Vigília (Acampamento da Vela). Ex-guarda-freios do bonde da linha 7: mulher de uns
# cinquenta anos, magra e dura. Sobretudo azul aço remendado com dragonas puídas e a vela da Vigília no peito,
# tapa-olho de latão (perdeu o olho na viagem da meia nota), escopeta serrada no coldre da coxa, cigarro de palha
# apagado no canto da boca, a manivela de freio do bonde pendurada no cinto. Mão esquerda na cintura.
from kit import *

INFO = info("vigilia", tz=.9)

def build():
    R = rig("capita_odete")
    skin = pele("od_pele", (.36, .26, .2), sujo=.4, marcas=(.22, .12, .1), marcas_amt=.3)
    azul = pano("od_sobretudo", (.075, .1, .14), vinco=.45, desbote=.35, remendo=(.13, .1, .07), rem_amt=.12, grime=1.1)
    camisa = pano("od_camisa", (.2, .19, .17), vinco=.3, desbote=.2)
    calca = pano("od_calca", (.07, .065, .06), vinco=.35)
    bota = couro("od_bota", (.06, .04, .03), rachado=.6)
    cou = couro("od_couro", (.13, .07, .035))
    lat = latao("od_latao")
    fer = ferro("od_ferro")
    cab = cabelo("od_cabelo", (.13, .125, .12), grisalho=.45)
    luva = couro("od_luva", (.05, .035, .025), rachado=.3)
    corpo(R, skin, azul, calca, mangas=azul, botas=bota, maos=luva, mulher=True, magro=.92, busto=.3, punho=1.3, manga_r=1.08)
    # saia do sobretudo até a canela, aberta na frente, barra gasta
    aba(R, azul, z1=.3, aberto=.5, rodado=1.0, jag=.07, seed=7)
    gola(R, azul, alta=.06)
    # camisa aparecendo no decote
    R.rigid([panel("od_v", camisa, 1.46, 1.3, .045, .02, -.112, .0, rows=3, cols=3, thick=.004)], "chest")
    # dragonas puídas com franja de latão
    dr = []
    for sd in (1, -1):
        dr.append(prim("primitive_cube_add", azul, (.17*sd, 0, 1.475), (.06, .055, .012), rot=(0, -14*sd, 0)))
        for k in range(6):
            dr.append(along("primitive_cylinder_add", lat, (.22*sd, -.04 + .016*k, 1.462), (.235*sd, -.04 + .016*k, 1.43), .003, vertices=4))
    # vela da Vigília no peito (broche de latão) e botões
    dr.append(prim("primitive_cylinder_add", lat, (-.07, -.127, 1.37), (.018, .018, .004), rot=(90, 0, 0), vertices=12))
    dr.append(prim("primitive_cube_add", cou, (-.07, -.133, 1.37), (.004, .002, .012)))
    for k in range(4):
        dr.append(prim("primitive_uv_sphere_add", lat, (.06, -.128 + .004*k, 1.38 - .07*k), (.009, .005, .009), segments=6, ring_count=4))
    R.rigid(dr, "chest")
    # cinto, manivela de freio do bonde, coldre na coxa direita com a escopeta serrada
    cinto(R, cou, fivela=lat)
    mv = [along("primitive_cylinder_add", fer, (.15, -.06, 1.0), (.17, -.07, .78), .011, vertices=8),
          prim("primitive_cube_add", fer, (.17, -.07, .77), (.012, .03, .012)),
          along("primitive_cylinder_add", cou, (.17, -.1, .77), (.17, -.12, .77), .014, vertices=8)]
    R.rigid(mv, "hips")
    th = R.P("thigh.R"); kn = R.P("shin.R")
    c0 = th.lerp(kn, .35) + Vector((-.06, -.03, 0))
    co = [prim("primitive_cube_add", cou, c0, (.025, .045, .1), rot=(0, 6, 0)),
          strip(cou, th.lerp(kn, .2) + Vector((-.08, -.05, 0)), th.lerp(kn, .2) + Vector((.04, -.08, 0)), .02, .005)]
    # escopeta: canos serrados para baixo dentro do coldre, coronha de madeira para cima
    mad = madeira("od_madeira", (.16, .08, .035))
    co.append(along("primitive_cylinder_add", fer, c0 + Vector((-.006, -.02, -.07)), c0 + Vector((-.006, -.02, .12)), .011, vertices=8))
    co.append(along("primitive_cylinder_add", fer, c0 + Vector((.012, -.02, -.07)), c0 + Vector((.012, -.02, .12)), .011, vertices=8))
    co.append(along("primitive_cone_add", mad, c0 + Vector((0, -.02, .12)), c0 + Vector((-.05, .0, .3)), .036, vertices=8, radius1=.7, radius2=1.0))
    R.rigid(co, "thigh.R")
    # bolsa de cartuchos na cintura esquerda
    bolsa(R, cou, pos=(.13, .07, .97), tam=(.035, .03, .045), tampa=cou)
    # cabeça: rosto magro, tapa-olho de latão no olho direito, cabelo grisalho curto preso, cigarro de palha
    sob = cabelo("od_sobr", (.2, .19, .18))
    hd = cabeca(R, skin, mulher=True, idade=.55, magro=.9, queixo=1.05, tapa_olho=(-1, lat, cou), sobrancelha=sob)
    hd += cabelo_curto(cab, .98, entradas=.4)
    hd.append(prim("primitive_uv_sphere_add", cab, HC + Vector((0, .1, -.02)), (.04, .035, .04), segments=10, ring_count=6))  # rabo curto
    palha = mat("od_palha", (.42, .33, .17), 0, .8, dirt=.5)
    hd.append(along("primitive_cylinder_add", palha, HC + Vector((.015, -.105, -.07)), HC + Vector((.05, -.15, -.08)), .004, vertices=6))
    R.rigid(hd, "head")
    return fim(R, INFO)

# braço esquerdo solto, direita solta perto do coldre
BASE = {"upper_arm.L": {"y": 33, "x": -2}, "forearm.L": {"bend": -20},
        "upper_arm.R": {"y": -30, "x": -2}, "forearm.R": {"bend": -16},
        "chest": {"x": -2}, "head": {"x": 3}, "thigh.L": {"y": 3}, "thigh.R": {"y": -4, "x": 2}}

def anims(R):
    def ex(i, n):  # tamborila os dedos da direita no cabo da escopeta e vira o rosto devagar
        return {"forearm.R": {"bend": -6*max(0, wave(i, n))}, "head": {"z": 4*wave(i, n, ph=1.5)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.15, 1))
