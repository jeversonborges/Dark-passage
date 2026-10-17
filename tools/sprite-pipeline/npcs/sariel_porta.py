# Sariel, Guardiã da Porta Dourada (Jerusalém, Arautos). Anjo alta e magra, sobretudo de couro preto com fivelas de ouro
# velho; uma asa inteira e a outra substituída por uma armação de latão e lona. Máscara de gás pendurada no pescoço.
# Uma brasa pequena acesa no olho esquerdo, o único ponto que brilha. Guarda a porta com uma lança de haste longa.
from kit import *

INFO = info("arautos", tz=1.0, escala=1.04, px=272)
CORES_EXTRA = "ff7a2a"

def build():
    R = rig("sariel_porta", extra=dict(ASAS))
    skin = pele("sa_pele", (.4, .32, .27), sujo=.3)
    cou = couro("sa_sobretudo", (.03, .025, .022), rachado=.5, gasto=.5)
    our = ouro("sa_ouro"); lat = latao("sa_latao"); fer = ferro("sa_ferro")
    lona = pano("sa_lona", (.3, .26, .19), vinco=.4, desbote=.4, remendo=(.15, .1, .06), rem_amt=.25, mancha_amt=.6)
    pc = pano("sa_pena_c", (.42, .4, .36), vinco=.1, mancha=(.2, .18, .15), mancha_amt=.6, grime=1.3)
    pe = pano("sa_pena_e", (.18, .17, .16), vinco=.1, mancha_amt=.6, grime=1.3)
    bot = couro("sa_bota", (.03, .025, .02)); cab = cabelo("sa_cabelo", (.05, .045, .04), fios=120)
    corpo(R, skin, cou, cou, mangas=cou, botas=bot, maos=couro("sa_luva", (.04, .03, .025)), mulher=True, magro=.9, busto=.35, punho=1.15, manga_r=1.05)
    aba(R, cou, z0=1.08, z1=.18, aberto=.45, rodado=1.0, jag=.05, seed=12, folds=9, famp=.05)
    gola(R, cou, alta=.09, lapela=False)
    fv = []
    for k in range(4):
        for sd in (1, -1): fv.append(prim("primitive_cube_add", our, (.1*sd, -.13 - .008*k, 1.36 - .08*k), (.016, .004, .01)))
    R.rigid(fv, "chest")
    cinto(R, cou, fivela=our, z=1.02, r=.17)
    asa(R, 1, pc, pe, tira_m=cou, metal=lat, fechada=True, esc=1.0, falhas=.08, seed=21)   # a asa inteira (esquerda)
    # a outra: armação de latão e lona, como uma asa de morcego remendada
    root = R.P("wing.R"); fr = []
    pts = [root + Vector((-.16, .14, .34)), root + Vector((-.24, .26, -.1)), root + Vector((-.22, .28, -.55)), root + Vector((-.14, .22, -.85))]
    for p in pts: fr.append(along("primitive_cylinder_add", lat, root, p, .007, vertices=6))
    fr.append(along("primitive_cylinder_add", lat, root, pts[0], .012, vertices=8))
    import bmesh as _bm
    bm = _bm.new(); vs = [bm.verts.new(root)] + [bm.verts.new(p) for p in pts]
    for a, b in zip(vs[1:], vs[2:]): bm.faces.new((vs[0], a, b))
    from base_rig import obj_from_bm
    fr.append(obj_from_bm("sa_lona_asa", bm, lona))
    for p in pts: fr.append(prim("primitive_uv_sphere_add", fer, p, (.012,)*3, segments=6, ring_count=4))
    R.rigid(fr, "wing.R")
    # lança de haste longa com ponta de ferro
    G = grip(R, "R"); mad = madeira("sa_haste", (.12, .07, .04))
    R.rigid([along("primitive_cylinder_add", mad, G + Vector((0, 1.1, 0)), G + Vector((0, -1.0, 0)), .015, vertices=8),
             along("primitive_cone_add", fer, G + Vector((0, 1.1, 0)), G + Vector((0, 1.32, 0)), .03, vertices=6, radius1=1, radius2=0),
             prim("primitive_torus_add", our, G + Vector((0, 1.08, 0)), (1, 1, 1), rot=(90, 0, 0), major_radius=.02, minor_radius=.005)], "prop.R")
    R.rigid(mascara_gas(cou, vidro("sa_visor", (.05, .07, .05)), lat, pendurada=True), "chest")
    brasa = glow("sa_brasa", (1.0, .45, .15), 5.0)
    hd = cabeca(R, skin, mulher=True, idade=.35, magro=.9, queixo=1.05, olho_vidro=(1, brasa), sobrancelha=cab)
    hd += cabelo_longo(cab, comp=.18, volume=.95)
    R.rigid(hd, "head")
    return fim(R, INFO)

# lança em pé ao lado (ponta para cima), esquerda solta
BASE = {"upper_arm.R": {"y": -30, "x": -18}, "forearm.R": {"bend": -60}, "aim": {"prop.R": (0, -.02, -1)},
        "upper_arm.L": {"y": 32, "x": -2}, "forearm.L": {"bend": -15}, "head": {"x": 2}}

def anims(R):
    def ex(i, n): return {"head": {"z": 10*wave(i, n*.5)}, "wing.L": {"x": 2*wave(i, n)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(1, 0), passo=18)
