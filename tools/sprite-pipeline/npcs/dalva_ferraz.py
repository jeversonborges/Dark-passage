# Dalva Ferraz, Engenheira Herege (Vigília, no Egito). Discípula de Gustavo, o Primarca. Mulher de uns trinta e cinco
# anos, cabelo curto grisalho, macacão de lona cheio de bolsos, óculos de solda na testa, mãos pretas de graxa. Uma
# pilha de cobre e zinco presa no cinto, sempre faiscando (único brilho, azul elétrico). Desenha enquanto fala: lápis
# de carpinteiro na mão e uma prancheta com um esquema.
from kit import *

INFO = info("vigilia", tz=.9)

def build():
    R = rig("dalva_ferraz")
    skin = pele("dv_pele", (.4, .27, .2), sujo=.5)
    graxa = mat("dv_graxa", (.02, .018, .016), .2, .45)
    lona = pano("dv_macacao", (.17, .16, .11), vinco=.55, desbote=.35, remendo=(.1, .1, .08), rem_amt=.15, mancha=(.03, .03, .025), mancha_amt=.7, grime=1.4)
    cou = couro("dv_couro", (.11, .065, .03)); lat = latao("dv_latao"); cob = cobre("dv_cobre"); fer = ferro("dv_ferro")
    bot = couro("dv_bota", (.05, .035, .025), rachado=.6)
    cab = cabelo("dv_cabelo", (.2, .19, .18), grisalho=.6)
    corpo(R, skin, lona, lona, mangas=lona, botas=bot, maos=graxa, mulher=True, magro=.95, busto=.35, punho=1.15)
    cinto(R, cou, fivela=lat, z=1.0)
    bl = []
    for x, z in ((.15, .72), (-.15, .72)):
        bl.append(prim("primitive_cube_add", lona, (x, -.13 if z > 1 else -.1, z), (.04, .012, .04)))
    R.rigid(bl, "hips")
    # pilha voltaica no cinto: discos de cobre e zinco empilhados entre varetas, faísca azul no topo
    zn = mat("dv_zinco", (.35, .36, .37), 1, .5, dirt=.6)
    P = Vector((.17, -.06, .97)); pl = []
    for k in range(9): pl.append(prim("primitive_cylinder_add", cob if k % 2 else zn, P + Vector((0, 0, .012*k)), (.03, .03, .005), vertices=12))
    for sd in (1, -1): pl.append(along("primitive_cylinder_add", fer, P + Vector((.034*sd, 0, -.01)), P + Vector((.034*sd, 0, .12)), .003, vertices=4))
    arco = glow("dv_faisca", (.45, .75, 1.0), 5.0)
    rr = random.Random(2); p = P + Vector((.034, 0, .12))
    for k in range(4):
        q = p + Vector((-.017, rr.uniform(-.01, .01), rr.uniform(.0, .02))); pl.append(along("primitive_cylinder_add", arco, p, q, .003, vertices=4)); p = q
    R.rigid(pl, "hips")
    # prancheta com o esquema e lápis
    G = grip(R, "L"); papel = pano("dv_papel", (.45, .42, .34), trama=30, mancha=(.05, .05, .05), mancha_amt=.5)
    R.rigid([prim("primitive_cube_add", madeira("dv_prancheta", (.18, .11, .05)), G + Vector((0, -.08, 0)), (.1, .13, .006)),
             prim("primitive_cube_add", papel, G + Vector((0, -.08, .007)), (.09, .12, .002))], "prop.L")
    G = grip(R, "R"); R.rigid([along("primitive_cylinder_add", mat("dv_lapis", (.3, .16, .05), 0, .6), G + Vector((0, .03, 0)), G + Vector((0, -.09, 0)), .005, vertices=6)], "prop.R")
    hd = cabeca(R, skin, mulher=True, idade=.3, queixo=1.0, sobrancelha=cab)
    hd += cabelo_curto(cab, 1.0, entradas=.1)
    lente = vidro("dv_lente", (.05, .12, .1))
    for sd in (1, -1):
        hd.append(along("primitive_cylinder_add", lat, HC + Vector((.035*sd, -.085, .06)), HC + Vector((.035*sd, -.115, .07)), .025, vertices=12))
        hd.append(along("primitive_cylinder_add", lente, HC + Vector((.035*sd, -.114, .07)), HC + Vector((.035*sd, -.118, .071)), .019, vertices=12))
    hd.append(prim("primitive_torus_add", cou, HC + Vector((0, -.005, .055)), (1, 1.12, 1.6), major_radius=.09, minor_radius=.008, rot=(-10, 0, 0)))
    R.rigid(hd, "head")
    return fim(R, INFO)

# segura a prancheta na esquerda e rabisca com a direita
BASE = {"upper_arm.L": {"y": 30, "x": -35}, "forearm.L": {"bend": -80}, "aim": {"prop.L": (0, -.5, .85)},
        "upper_arm.R": {"y": -30, "x": -35}, "forearm.R": {"bend": -95}, "head": {"x": 12}}

def anims(R):
    def ex(i, n):  # rabisca rápido, ergue os olhos de vez em quando
        return {"hand.R": {"z": 14*wave(i, n*.25), "x": 6*wave(i, n*.5)}, "head": {"x": -6*max(0, wave(i, n, ph=2))}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 0), passo=20)
