# Hulda, Profetisa da Escada (Jerusalém, Arautos). Mulher de uns sessenta anos, batina vermelha desbotada, mãos
# enfaixadas de tanto mexer na Brasa do altar, óculos de lente rachada, rolos amarrados nas costas. Vende rolos e
# remédios. Lê um rolo aberto perto do rosto. Sem brilho.
from kit import *

INFO = info("arautos", tz=.88)

def build():
    R = rig("hulda_escada")
    skin = pele("hu_pele", (.38, .26, .2), sujo=.35, rubor_amt=.3)
    verm = pano("hu_batina", (.22, .05, .04), vinco=.45, desbote=.6, mancha_amt=.5, grime=1.1)
    faixa = pano("hu_faixa", (.42, .38, .3), vinco=.3, mancha=(.12, .05, .03), mancha_amt=.7, grime=1.2)
    perg = pano("hu_rolo", (.45, .38, .24), trama=30, vinco=.2, mancha_amt=.5)
    cou = couro("hu_couro", (.1, .06, .03)); lat = latao("hu_latao"); mad = madeira("hu_vara", (.15, .09, .05))
    cab = cabelo("hu_cabelo", (.35, .33, .3), grisalho=.85)
    corpo(R, skin, verm, verm, mangas=verm, maos=faixa, mulher=True, busto=.45, magro=.98, botas=couro("hu_bota", (.05, .035, .025)), manga_r=1.1)
    aba(R, verm, z0=1.05, z1=.08, aberto=0, rodado=1.0, jag=.04, seed=13, folds=12, famp=.03)
    cinto(R, cou, fivela=lat, z=1.02, r=.17)
    # rolos amarrados nas costas
    rl = []
    for k, (x, z) in enumerate(((-.07, 1.3), (.06, 1.32), (0, 1.18), (.09, 1.15))):
        rl.append(along("primitive_cylinder_add", perg, (x - .02, .15, z - .14), (x + .02, .17, z + .16), .028, vertices=10))
        rl.append(prim("primitive_cylinder_add", mad, (x + .02, .17, z + .17), (.012, .012, .02), vertices=8))
    rl += tira(cou, [Vector((.13, -.06, 1.46)), Vector((.12, .12, 1.4)), Vector((-.1, .2, 1.1)), Vector((-.13, -.04, .98))], w=.03, t=.006)
    R.rigid(rl, "chest")
    # rolo aberto seguro pela esquerda (a direita aponta a linha que lê)
    H = grip(R, "L")
    R.rigid([along("primitive_cylinder_add", mad, H + Vector((0, 0, -.1)), H + Vector((0, 0, .1)), .013, vertices=8),
             prim("primitive_cube_add", perg, H + Vector((0, -.13, 0)), (.004, .13, .09)),
             along("primitive_cylinder_add", perg, H + Vector((0, -.26, -.09)), H + Vector((0, -.26, .09)), .02, vertices=8)], "prop.L")
    hd = cabeca(R, skin, mulher=True, idade=.7, queixo=1.0, nariz=1.1, sobrancelha=cab)
    hd += coque(cab)
    lente = vidro("hu_lente", (.08, .09, .08))
    for sd in (1, -1):
        hd.append(prim("primitive_torus_add", lat, HC + Vector((.033*sd, -.098, .005)), (1, 1, 1), rot=(90, 0, 0), major_radius=.019, minor_radius=.0025))
        hd.append(prim("primitive_cylinder_add", lente, HC + Vector((.033*sd, -.098, .005)), (.018, .018, .001), rot=(90, 0, 0), vertices=10))
    R.rigid(hd, "head")
    return fim(R, INFO)

BASE = {"upper_arm.L": {"y": 22, "x": -38}, "forearm.L": {"bend": -95}, "aim": {"prop.L": (-.9, -.3, 0)}, "upper_arm.R": {"y": -22, "x": -34}, "forearm.R": {"bend": -90},
        "head": {"x": 12}}

def anims(R):
    def ex(i, n): return {"head": {"z": 6*wave(i, n*.5)}, "hand.L": {"z": 4*wave(i, n)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 0), passo=13)
