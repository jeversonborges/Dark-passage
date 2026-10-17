# Simão, o Coveiro (neutro). Velho muito alto e muito magro, pele cinza de quem já foi enterrado, faixas de linho
# velho enroladas nos pulsos e no pescoço, chapéu de aba larga caída, sobretudo comprido de lã preta puída, calça
# enfiada em botas de cano alto sujas de areia. Pá apoiada no ombro, lampião com vela de sebo na outra mão (único
# brilho, quente). Segredo (linha F): é o arcanjo Rafael; nas costas do sobretudo, duas fendas costuradas com linho
# deixam ver as faixas que escondem as cicatrizes das asas perdidas.
from kit import *

INFO = info("neutro", tz=.95, escala=1.1, px=224)

def build():
    R = rig("simao_coveiro")
    skin = pele("sm_pele", (.25, .25, .24), sujo=.5, rubor=(.18, .17, .17), rubor_amt=.3)
    la = pano("sm_sobretudo", (.045, .043, .042), vinco=.5, desbote=.45, remendo=(.1, .09, .08), rem_amt=.12, grime=1.2)
    camisa = pano("sm_camisa", (.2, .18, .15), vinco=.3)
    calca = pano("sm_calca", (.07, .065, .055))
    bot = couro("sm_bota", (.06, .045, .03), rachado=.6, gasto=.5)
    lin = linho("sm_linho", (.36, .32, .25), band=14, resin=.15, mud_amt=.5)
    feltro = pano("sm_chapeu", (.05, .045, .04), vinco=.5, desbote=.5, trama=40)
    fer = ferro("sm_ferro", ferrugem=.6); mad = madeira("sm_cabo", (.18, .12, .07)); lat = latao("sm_latao")
    cab = cabelo("sm_cabelo", (.3, .3, .29), grisalho=.5)
    corpo(R, skin, la, calca, mangas=la, botas=bot, maos=skin, magro=.82, larg=.95, punho=1.15, manga_r=1.05, cano=.42, corcunda=.2)
    aba(R, la, z1=.22, aberto=.45, rodado=.9, jag=.08, seed=11, folds=9, famp=.08)
    gola(R, la, alta=.08, lapela=True)
    # faixas de linho nos pulsos e no pescoço; fendas costuradas nas costas mostrando as faixas
    for n in "LR": R.rigid(faixas_em(R, f"forearm.{n}", lin, t0=.6, t1=.95, n=4, r=.05, ends=1, end_len=.1), f"forearm.{n}")
    R.rigid([prim("primitive_torus_add", lin, (0, -.01, 1.52 + .025*k), (1, 1, 1.5), major_radius=.052, minor_radius=.008,
                  rot=(8*(k % 2), 0, 0)) for k in range(3)], "neck")
    cs = []
    for sd in (1, -1):
        c = Vector((.09*sd, .135, 1.3))
        cs.append(prim("primitive_cube_add", lin, c, (.012, .012, .1), rot=(0, -10*sd, 0)))
        for k in range(5):
            cs.append(along("primitive_cylinder_add", lin, c + Vector((-.02, .006, -.08 + .04*k)), c + Vector((.02, .006, -.07 + .04*k)), .003, vertices=4))
    R.rigid(cs, "chest")
    # pá no ombro direito
    G = grip(R, "R"); pa = [along("primitive_cylinder_add", mad, G + Vector((0, .2, 0)), G + Vector((0, -.95, 0)), .016, vertices=8)]
    pa.append(prim("primitive_torus_add", mad, G + Vector((0, .23, 0)), (1, 1, 1.2), rot=(90, 0, 0), major_radius=.04, minor_radius=.012))
    b = G + Vector((0, -1.08, 0))
    lam = prim("primitive_uv_sphere_add", fer, b, (.11, .15, .015), segments=14, ring_count=8); pa.append(lam)
    pa.append(prim("primitive_cylinder_add", fer, G + Vector((0, -.96, 0)), (.025, .025, .04), rot=(90, 0, 0), vertices=8))
    R.rigid(pa, "prop.R")
    # lampião de latão com vela de sebo (a chama é o único brilho)
    G = grip(R, "L"); lp = [along("primitive_cylinder_add", fer, G + Vector((0, -.02, .02)), G + Vector((0, -.02, -.1)), .004, vertices=4)]
    c = G + Vector((0, -.02, -.2))
    lp.append(prim("primitive_cylinder_add", lat, c + Vector((0, 0, -.09)), (.05, .05, .015), vertices=12))
    lp.append(prim("primitive_cone_add", lat, c + Vector((0, 0, .09)), (.055, .055, .035), vertices=12))
    for k in range(4):
        a = k*math.pi/2 + .4
        lp.append(along("primitive_cylinder_add", lat, c + Vector((.045*math.cos(a), .045*math.sin(a), -.08)), c + Vector((.045*math.cos(a), .045*math.sin(a), .07)), .004, vertices=4))
    lp.append(prim("primitive_cylinder_add", vidro("sm_vidro", (.2, .17, .1)), c, (.042, .042, .07), vertices=12))
    lp.append(prim("primitive_cylinder_add", mat("sm_sebo", (.5, .45, .33), 0, .6), c + Vector((0, 0, -.04)), (.014, .014, .035), vertices=8))
    lp.append(prim("primitive_uv_sphere_add", glow("sm_chama", (1.0, .62, .25), 6.0), c + Vector((0, 0, .0)), (.01, .01, .022), segments=8, ring_count=6))
    R.rigid(lp, "prop.L")
    # cabeça: rosto comprido e encovado, barba rala grisalha, cabelo comprido e ralo, chapéu de aba larga caída
    hd = cabeca(R, skin, idade=.9, magro=.78, nariz=1.2, queixo=1.1, sobrancelha=cab)
    hd += barba(cab, comp=.05, larg=.9, bigode=True)
    hd += cabelo_longo(cab, comp=.2, volume=.98)
    hd += aba_larga(feltro, aba=.2, copa=.1, fita=lin, caido=1.0)
    R.rigid(hd, "head")
    return fim(R, INFO)

BASE = {"upper_arm.R": {"y": -6, "x": -30, "z": 10}, "forearm.R": {"bend": -128}, "aim": {"prop.R": (.05, .55, .85)},
        "upper_arm.L": {"y": 30, "x": -18}, "forearm.L": {"bend": -40}, "hand.L": {"x": 35},
        "spine": {"x": 4}, "chest": {"x": 5}, "neck": {"x": 4}, "head": {"x": 2}}

def anims(R):
    def ex(i, n):  # o lampião balança de leve; ele abaixa a cabeça devagar
        return {"hand.L": {"x": 5*wave(i, n)}, "head": {"x": 3*wave(i, n, ph=2)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.3, 0), passo=15)
