# Isaura Valente, a Voz da Rádio São Lázaro (neutro, linha D). Ex-radiotelegrafista do Comando Sul no Silo São
# Lázaro: leu em voz alta a ordem de lançamento da Absinto-1. Uns setenta anos, magra, cabelo branco curtíssimo,
# fones de baquelite pendurados no pescoço, farda verde do exército desbotada com divisas e bolsos, por cima um
# xale de crochê cor de mostarda, mãos com queimaduras antigas em forma de dedos. Nas costas o rádio de campanha
# com antena chicote e o fone de mão preso no fio enrolado; na mão a tira de papel da contagem da Absinto-2.
# Único brilho: o mostrador do rádio, âmbar.
from kit import *

INFO = info("neutro", tz=.88, escala=.97)

def build():
    R = rig("isaura_radialista")
    skin = pele("is_pele", (.36, .27, .22), sujo=.3, marcas=(.45, .22, .2), marcas_amt=.5)
    farda = pano("is_farda", (.13, .14, .09), vinco=.4, desbote=.5, remendo=(.1, .1, .07), rem_amt=.12)
    croche = pano("is_xale", (.32, .24, .08), vinco=.2, desbote=.3, trama=180, xadrez=(.2, .14, .05), listra_per=.03)
    bot = couro("is_bota", (.05, .04, .03))
    baq = stained("is_baquelite", (.08, .035, .02), stain=(.02, .01, .01), amount=.3, scale=10, rough=.3, grime=.2)
    fer = ferro("is_ferro"); lat = latao("is_latao"); lona = pano("is_lona", (.1, .11, .07), vinco=.3)
    papel = pano("is_papel", (.5, .46, .38), vinco=.1, mancha_amt=.3)
    cab = cabelo("is_cabelo", (.42, .41, .4), fios=140)
    corpo(R, skin, farda, farda, mangas=farda, botas=bot, maos=skin, mulher=True, magro=.85, busto=.25, cano=.3, punho=1.05)
    aba(R, farda, z0=1.05, z1=.62, aberto=0, rodado=.6, jag=.01, seed=4, folds=6, famp=.03)   # saia reta de farda
    gola(R, farda, alta=.04, lapela=True)
    # bolsos, divisas e botões da farda
    fd = []
    for sd in (1, -1):
        fd.append(prim("primitive_cube_add", farda, (.06*sd, -.118, 1.33), (.035, .008, .03)))
        fd.append(prim("primitive_uv_sphere_add", lat, (.06*sd, -.128, 1.355), (.006,)*3))
    R.rigid(fd, "chest")
    o_, ax, u, sd_ = R.frame("upper_arm.L")
    R.rigid([along("primitive_cube_add", lat, o_ + ax*.08 + u*.06 + sd_*(.02 - .015*k), o_ + ax*.1 + u*.06 + sd_*(-.0 - .015*k), .006) for k in range(3)], "upper_arm.L")
    xale(R, croche, z1=1.2, jag=.05, seed=6)
    cinto(R, lona, fivela=lat, z=1.02, r=.16, ry=.8, grosso=.018)
    # rádio de campanha nas costas: caixa de aço verde, mostrador âmbar, antena chicote, fone de mão no fio enrolado
    rd = []; c = Vector((0, .2, 1.22))
    rd.append(prim("primitive_cube_add", lona, c, (.13, .07, .17)))
    rd[-1].modifiers.new("b", 'BEVEL').width = .015
    rd.append(prim("primitive_cube_add", fer, c + Vector((0, .0, .19)), (.12, .06, .02)))
    rd.append(prim("primitive_cylinder_add", glow("is_mostrador", (1.0, .6, .2), 2.2), c + Vector((.06, .072, .2)), (.022, .022, .004), rot=(90, 0, 0), vertices=12))
    for k in range(3):
        rd.append(prim("primitive_cylinder_add", baq, c + Vector((-.06 + .04*k, .06, .205)), (.012, .012, .015), vertices=8))
    rd.append(along("primitive_cylinder_add", fer, c + Vector((-.1, .02, .2)), c + Vector((-.16, .1, .95)), .004, vertices=4))
    rd.append(prim("primitive_uv_sphere_add", fer, c + Vector((-.16, .1, .95)), (.008,)*3))
    for sd in (1, -1):
        rd += tira(lona, [Vector((.1*sd, -.1, 1.44)), Vector((.12*sd, .1, 1.45)), Vector((.12*sd, .14, 1.12))], w=.035, t=.008)
    R.rigid(rd, "chest")
    # fone de mão preso na cintura com fio em espiral até o rádio
    fn = [prim("primitive_cube_add", baq, (-.16, -.06, .96), (.018, .02, .07), rot=(10, 0, 0))]
    for k in range(10):
        t = k/9; p = Vector((-.16, -.06, .9)).lerp(Vector((-.12, .17, 1.07)), t)
        fn.append(prim("primitive_torus_add", baq, p + Vector((0, 0, -.04*math.sin(t*math.pi))), (1, 1, 1), major_radius=.012, minor_radius=.0025, rot=(0, 90, 0)))
    R.rigid(fn, "hips")
    # tira de papel com a contagem na mão direita
    G = grip(R, "R")
    R.rigid([prim("primitive_cube_add", papel, G + Vector((0, -.04, .05)), (.035, .003, .1), rot=(10, 0, 0))], "prop.R")
    # cabeça: rosto magro e firme, cabelo branco curtíssimo, fones de baquelite no pescoço
    hd = cabeca(R, skin, mulher=True, idade=.85, magro=.85, queixo=1.0, sobrancelha=cab)
    hd += raspado(cab)
    R.rigid(hd, "head")
    fo = [prim("primitive_torus_add", fer, (0, -.01, 1.5), (1, 1.1, 1), major_radius=.075, minor_radius=.006, rot=(-20, 0, 0))]
    for sd in (1, -1):
        fo.append(prim("primitive_cylinder_add", baq, (.07*sd, -.07, 1.47), (.032, .032, .016), rot=(70, 0, 25*sd), vertices=14))
    R.rigid(fo, "neck")
    return fim(R, INFO)

# lê a contagem na tira de papel (direita erguida), esquerda segura a alça do rádio
BASE = {"upper_arm.R": {"y": -24, "x": -38}, "forearm.R": {"bend": -96}, "hand.R": {"x": -15},
        "upper_arm.L": {"y": 22, "x": -10}, "forearm.L": {"bend": -100}, "head": {"x": 10, "z": -8}}

def anims(R):
    def ex(i, n):  # mexe os lábios contando; a cabeça marca o compasso
        return {"head": {"x": 3*max(0, wave(i, n*.5))}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, .3), passo=15)
