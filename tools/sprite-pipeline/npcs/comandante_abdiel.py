# Abdiel, Comandante Angélico da Capela (Arautos). Ex-escudeiro de Zacarias que recuou em vez de descer na noite da
# meia nota e carrega essa covardia como uma pedra. Anjo de quase três metros: sobretudo-batina branco osso até o
# chão, abotoado, com correias de couro cruzadas e o cinturão de espada; asas de penas sujas dobradas nas costas,
# presas com tiras de couro e fivelas (penas faltando); rosto de porcelana rachado, venda bordada com um olho
# dourado; halo de ferro com dois raios quebrados. Monta guarda com o espadão de ponta no chão e as duas mãos no
# punho. Sem brilho: o ouro da venda é só bordado.
from kit import *

INFO = info("arautos", tz=1.0, escala=1.5, px=320, rim_e=6.5)

def build():
    R = rig("comandante_abdiel", extra=dict(ASAS))
    porc = stained("ab_porcelana", (.55, .53, .5), stain=(.05, .045, .04), amount=.25, scale=14, rough=.18, grime=.15, dirt=.6)
    branco = pano("ab_batina", (.42, .4, .35), vinco=.55, desbote=.15, remendo=(.32, .29, .24), rem_amt=.1, mancha=(.12, .1, .07), mancha_amt=.55, grime=1.3)
    cou = couro("ab_couro", (.09, .05, .03), rachado=.6)
    luva = couro("ab_luva", (.18, .16, .13), rachado=.3)
    bot = couro("ab_bota", (.05, .04, .035))
    pclaro = pano("ab_penas", (.38, .36, .32), vinco=.25, desbote=.3, trama=150, mancha=(.1, .09, .07), mancha_amt=.6, grime=.6, rough=.8)
    pescuro = pano("ab_penas2", (.2, .19, .17), vinco=.2, desbote=.2, trama=150, mancha_amt=.5, grime=.5)
    fer = ferro("ab_ferro", ferrugem=.55); lat = latao("ab_latao"); ouro_m = ouro("ab_ouro", (.5, .35, .1), amount=.3)
    venda = pano("ab_venda", (.32, .3, .26), vinco=.2, desbote=.1, mancha_amt=.3)
    corpo(R, porc, branco, branco, mangas=branco, botas=bot, maos=luva, magro=.9, larg=1.05, punho=1.2, cano=.36)
    aba(R, branco, z1=.06, aberto=.18, rodado=.9, jag=.06, seed=12, folds=12, famp=.05)
    gola(R, branco, alta=.07, aberta=False, lapela=False)
    R.rigid([prim("primitive_uv_sphere_add", lat, (0, -.125 - .004*k, 1.42 - .065*k), (.008,)*3, segments=6, ring_count=4) for k in range(7)], "chest")
    bandoleira(R, cou, de=(.16, 1.46), para=(-.15, .98), larg=.045, fivelas=lat)
    bandoleira(R, cou, de=(-.16, 1.46), para=(.15, .98), larg=.045, fivelas=lat)
    cinto(R, cou, fivela=lat, z=1.0, r=.185)
    for s in (1, -1): asa(R, s, pclaro, pescuro, tira_m=cou, metal=lat, fechada=True, esc=1.0, falhas=.12, seed=7)
    # espadão de ponta no chão, mãos no punho
    G = grip(R, "R"); sp = []
    lam = ferro("ab_lamina", (.2, .2, .21), ferrugem=.3, rough=.3)
    sp.append(along("primitive_cylinder_add", cou, G + Vector((0, .05, 0)), G + Vector((0, -.12, 0)), .018, vertices=8))
    sp.append(prim("primitive_uv_sphere_add", fer, G + Vector((0, .07, 0)), (.03,)*3, segments=10, ring_count=6))
    sp.append(along("primitive_cube_add", fer, G + Vector((-.13, -.13, 0)), G + Vector((.13, -.13, 0)), .016))
    blade = [G + Vector((0, -.14, 0)), G + Vector((0, -1.12, 0))]
    b = along("primitive_cube_add", lam, blade[0], blade[1], 1); b.scale = (.045, .009, (blade[1] - blade[0]).length/2); sp.append(b)
    sp.append(along("primitive_cone_add", lam, blade[1], blade[1] + Vector((0, -.08, 0)), .045, vertices=4, radius1=1, radius2=0))
    R.rigid(sp, "prop.R")
    # cabeça de porcelana rachada, venda com o olho dourado bordado, halo de ferro quebrado
    hd = cabeca(R, porc, idade=0, magro=.9, nariz=1.05, orelhas=False)
    rr = random.Random(3)
    for k in range(6):  # rachaduras
        p0 = HC + Vector((rr.uniform(-.06, .06), -.1, rr.uniform(-.08, .08)))
        p1 = p0 + Vector((rr.uniform(-.04, .04), rr.uniform(-.005, .0), rr.uniform(-.05, .05)))
        hd.append(along("primitive_cylinder_add", escuro(), p0, p1, .0022, vertices=4))
    hd.append(prim("primitive_cylinder_add", venda, HC + Vector((0, -.004, .0)), (.092, .104, .022), vertices=24))
    hd.append(prim("primitive_cylinder_add", ouro_m, HC + Vector((0, -.106, .0)), (.018, .004, .01), rot=(90, 0, 0), vertices=12))
    hd.append(prim("primitive_uv_sphere_add", mat("ab_pupila", (.05, .03, .01), 0, .5), HC + Vector((0, -.11, .0)), (.006, .003, .006)))
    hd += cabelo_curto(cabelo("ab_cabelo", (.3, .28, .24)), 1.0)
    hd += halo(fer, HC + Vector((0, .08, .17)), r=.13, raios=8, quebrados=(1, 5))
    R.rigid(hd, "head")
    return fim(R, INFO)

# guarda: as duas mãos sobre o punho do espadão, ponta no chão à frente
BASE = {"upper_arm.R": {"y": -20, "x": -26, "z": 16}, "forearm.R": {"bend": -62}, "aim": {"prop.R": (0, -.12, -1)},
        "upper_arm.L": {"y": 20, "x": -26, "z": -16}, "forearm.L": {"bend": -62}, "chest": {"x": -3}, "head": {"x": 4}}

def anims(R):
    def ex(i, n):  # respira como estátua; o halo e as asas mal se mexem
        return {"chest": {"x": -1.5*wave(i, n)}, "wing.L": {"z": 2*wave(i, n)}, "wing.R": {"z": -2*wave(i, n)}}
    def wk(i, n):  # anda com o espadão na mão, ponta para baixo
        return {"wing.L": {"z": 3*wave(i, n)}, "wing.R": {"z": -3*wave(i, n)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.1, 0), passo=15, walk_extra=wk)
