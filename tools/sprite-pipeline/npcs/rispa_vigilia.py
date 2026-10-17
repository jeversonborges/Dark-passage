# Rispa, a Que Vigia (Monte Hermon). Como a Rispa da Bíblia, vela os mortos e espanta as aves. Mulher de meia-idade,
# saco de pano como manto, cabelo raspado, cajado com trapos pendurados para espantar abutres. Fica de pé junto à rocha
# e à fogueira que nunca apaga (a fogueira é do cenário). Sem brilho.
from kit import *

INFO = info("hermon", tz=.9, px=224)

def build():
    R = rig("rispa_vigilia")
    skin = pele("ri_pele", (.3, .19, .13), sujo=.5, marcas=(.15, .1, .07), marcas_amt=.4)
    saco = pano("ri_saco", (.24, .2, .14), vinco=.6, desbote=.4, remendo=(.12, .09, .06), rem_amt=.25, trama=40, grime=1.5)
    trapo = pano("ri_trapo", (.2, .06, .04), vinco=.4, desbote=.6, mancha_amt=.6)
    trapo2 = pano("ri_trapo2", (.3, .28, .24), vinco=.4, mancha_amt=.7)
    mad = madeira("ri_cajado", (.14, .1, .06)); cab = cabelo("ri_cabelo", (.05, .04, .035))
    corpo(R, skin, saco, saco, mangas=saco, maos=skin, mulher=True, busto=.3, magro=.92, descalco=True, manga_r=1.15)
    aba(R, saco, z0=1.05, z1=.1, aberto=0, rodado=.95, jag=.08, seed=15, folds=10, famp=.05)
    capa(R, saco, z1=.4, larg=1.05, jag=.1, seed=16, aberto=1.4, gola_alta=.04)
    G = grip(R, "R")
    cj = [along("primitive_cylinder_add", mad, G + Vector((0, .75, 0)), G + Vector((0, -1.0, 0)), .016, vertices=7)]
    rr = random.Random(5)
    for k in range(6):
        p = G + Vector((0, .5 + .045*k, 0))
        m = trapo if k % 2 else trapo2
        cj += tira(m, [p, p + Vector((rr.uniform(-.06, .06), rr.uniform(-.03, .03), -.2 - .04*k))], w=.035, t=.004)
    R.rigid(cj, "prop.R")
    hd = cabeca(R, skin, mulher=True, idade=.5, magro=.92, sobrancelha=cab)
    hd += raspado(cab)
    R.rigid(hd, "head")
    return fim(R, INFO)

# cajado erguido com os trapos para cima, olhando o céu
BASE = {"upper_arm.R": {"y": -26, "x": -30}, "forearm.R": {"bend": -55}, "aim": {"prop.R": (0, -.1, -1)},
        "upper_arm.L": {"y": 34, "x": 0}, "forearm.L": {"bend": -20}, "head": {"x": -12}}

def anims(R):
    def ex(i, n): return {"upper_arm.R": {"x": -8*wave(i, n*.5)}, "head": {"z": 12*wave(i, n*.5)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(1, 0), passo=16)
