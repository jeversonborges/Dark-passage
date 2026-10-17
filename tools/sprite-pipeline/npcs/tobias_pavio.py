# Tobias "Pavio", Mercador de Sucata (órfão do cerco, uns doze anos). Magrelo, cartola amassada grande demais,
# óculos de aviador com uma lente quebrada, casaco de homem cortado, suspensório de corda, calça curta remendada,
# botinas desparelhadas. Empurra um carrinho de mão lotado de lixo valioso (engrenagens, lampião, garrafas,
# um sino pequeno, o mapa rasgado dos esconderijos enrolado). Serve também para "tobias_carrinho" (fogueiras).
from kit import *

INFO = info("vigilia", tz=.75, escala=.74, px=208)

def build():
    R = rig("tobias_pavio", extra={"carrinho": ((0, -.55, .35), (0, -.75, .35), None)})
    R.follow = {"carrinho": "hips"}
    skin = pele("tb_pele", (.4, .27, .19), sujo=.6)
    casaco = pano("tb_casaco", (.13, .1, .07), vinco=.45, desbote=.4, remendo=(.2, .16, .1), rem_amt=.25)
    camisa = pano("tb_camisa", (.3, .27, .21), listra=(.16, .12, .09), listra_per=.025, vinco=.3)
    calca = pano("tb_calca", (.09, .1, .1), remendo=(.18, .12, .08), rem_amt=.3)
    bot = couro("tb_botina", (.09, .055, .03)); bot2 = couro("tb_botina2", (.05, .045, .04))
    feltro = pano("tb_cartola", (.03, .028, .03), vinco=.5, desbote=.4, trama=40)
    corda = mat("tb_corda", (.22, .17, .1), 0, .9, dirt=.5)
    lat = latao("tb_latao"); fer = ferro("tb_ferro"); mad = madeira("tb_madeira", (.19, .12, .06))
    cab = cabelo("tb_cabelo", (.12, .07, .04))
    corpo(R, skin, camisa, calca, mangas=casaco, botas=bot, maos=skin, magro=.72, larg=.85, punho=1.4, manga_r=1.15, cano=.24)
    # casaco de homem grande demais: aba até o joelho, aberto, mangas arregaçadas grossas
    aba(R, casaco, z1=.52, aberto=.65, rodado=.9, larg=.85, jag=.06, seed=6, folds=8, famp=.06)
    gola(R, casaco, alta=.04, lapela=True)
    sus = []
    for sd in (1, -1):
        sus += tira(corda, [Vector((.07*sd, -.1, 1.02)), Vector((.08*sd, -.115, 1.25)), Vector((.08*sd, -.08, 1.45)), Vector((.05*sd, .09, 1.42)),
                            Vector((.04*sd, .1, 1.05))], w=.015, t=.006)
    R.rigid(sus, "chest")
    # carrinho de mão (osso próprio que segue o quadril: fica nivelado na frente dele)
    c = Vector((0, -.78, .3)); ca = []
    ca.append(prim("primitive_cube_add", mad, c + Vector((0, 0, .05)), (.2, .26, .09)))
    for sd in (1, -1):
        ca.append(prim("primitive_cube_add", mad, c + Vector((.21*sd, 0, .1)), (.012, .27, .1)))
        ca.append(along("primitive_cylinder_add", mad, c + Vector((.17*sd, .2, .0)), Vector((.22*sd, -.36, .86)), .016, vertices=8))  # varais
        ca.append(along("primitive_cylinder_add", fer, c + Vector((.15*sd, .1, -.05)), c + Vector((.15*sd, .1, -.25)), .01, vertices=6))  # pés
    ca.append(prim("primitive_cylinder_add", fer, c + Vector((0, -.32, -.14)), (.14, .14, .025), rot=(0, 90, 0), vertices=18))     # roda
    ca.append(prim("primitive_torus_add", fer, c + Vector((0, -.32, -.14)), (1, 1, 1), rot=(0, 90, 0), major_radius=.14, minor_radius=.018))
    # a carga: engrenagens, lampião, garrafas, sino, canos, o mapa enrolado, um pano por cima
    rr = random.Random(2)
    for k in range(4):
        g = prim("primitive_cylinder_add", lat if k % 2 else fer, c + Vector((rr.uniform(-.12, .12), rr.uniform(-.15, .15), .16 + .03*k)),
                 (.06, .06, .012), rot=(rr.uniform(-30, 30), rr.uniform(-40, 40), 0), vertices=12)
        ca.append(g)
    ca.append(prim("primitive_cone_add", lat, c + Vector((.08, .1, .24)), (.06, .06, .07), vertices=14))                  # sino
    vd = vidro("tb_garrafa", (.08, .2, .1))
    for k in range(3):
        ca.append(along("primitive_cylinder_add", vd, c + Vector((-.1 + .04*k, -.08, .14)), c + Vector((-.13 + .04*k, -.12, .3)), .022, vertices=8))
    ca.append(along("primitive_cylinder_add", fer, c + Vector((-.18, .2, .2)), c + Vector((.2, -.25, .28)), .02, vertices=8))  # cano
    papel = pano("tb_mapa", (.45, .4, .3), vinco=.2, mancha=(.1, .07, .04), mancha_amt=.6)
    ca.append(along("primitive_cylinder_add", papel, c + Vector((.12, -.15, .2)), c + Vector((.02, .12, .25)), .025, vertices=10))
    ca.append(panel("tb_pano", casaco, c.z + .3, c.z + .12, .16, .2, c.y + .05, .02, rows=4, cols=5, jag=.04, seed=3, thick=.01))
    R.rigid(ca, "carrinho")
    # cabeça: rosto magro de criança, cabelo desgrenhado, óculos de aviador (lente quebrada) na cartola amassada
    hd = cabeca(R, skin, idade=0, esc=1.12, queixo=.85, nariz=.9, sobrancelha=cab)
    hd += cabelo_curto(cab, 1.06)
    for k in range(6):
        a = -1.2 + k*.5
        hd.append(along("primitive_cone_add", cab, HC + Vector((.07*math.sin(a), -.06*math.cos(a) + .02, .02)),
                        HC + Vector((.1*math.sin(a), -.08*math.cos(a) + .03, -.06)), .015, vertices=4, radius1=1, radius2=0))
    hd += cartola(feltro, alt=.18, amassada=True, fita=corda)
    lente = vidro("tb_lente", (.1, .16, .15))
    for sd in (1, -1):
        hd.append(along("primitive_cylinder_add", lat, HC + Vector((.04*sd, -.09, .1)), HC + Vector((.04*sd, -.12, .11)), .028, vertices=12))
        if sd == 1: hd.append(along("primitive_cylinder_add", lente, HC + Vector((.04*sd, -.118, .11)), HC + Vector((.04*sd, -.122, .111)), .022, vertices=12))
    R.rigid(hd, "head")
    return fim(R, INFO)

# segura os varais do carrinho, tronco inclinado para empurrar
BASE = {"upper_arm.L": {"y": 40, "x": -30}, "forearm.L": {"bend": -18}, "upper_arm.R": {"y": -40, "x": -30}, "forearm.R": {"bend": -18},
        "spine": {"x": 8}, "chest": {"x": 6}, "head": {"x": -10}}

def anims(R):
    def ex(i, n):  # olha para os lados, fareja negócio
        return {"head": {"z": 14*wave(i, n)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 0), passo=20)
