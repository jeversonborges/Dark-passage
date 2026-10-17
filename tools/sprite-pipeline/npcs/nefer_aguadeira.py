# Nefer, a Aguadeira (Egito; o mesmo modelo serve para nefer_carrinho nas fogueiras). Filha de barqueiro, leva água
# para quem passa o dia no spot. Moça magra de uns vinte anos, cabelo em muitas tranças com fios de cobre, braços
# com cicatrizes de corda, vestido de linho tingido de anil até a canela, faixa vermelha na cintura, pés descalços.
# Carrega dois potes de barro pendurados nas pontas de uma vara sobre os ombros (canga). Sem brilho.
from kit import *

INFO = info("egito", tz=.88, escala=.95, px=208)

def build():
    R = rig("nefer_aguadeira", extra={"canga": ((0, .02, 1.5), (0, .02, 1.6), None)})
    R.follow = {"canga": "chest"}
    skin = pele("nf_pele", (.23, .13, .075), sujo=.35, marcas=(.35, .2, .13), marcas_amt=.5)
    anil = pano("nf_vestido", (.08, .1, .2), vinco=.5, desbote=.5, grime=1.2)
    faixa = pano("nf_faixa", (.3, .05, .04), vinco=.3, desbote=.3)
    barro = stained("nf_barro", (.3, .14, .07), stain=(.12, .07, .04), amount=.5, scale=6, rough=.8, blotch=(.36, .2, .1), blotch_amt=.5, grime=.5)
    mad = madeira("nf_vara", (.2, .13, .07)); corda = mat("nf_corda", (.25, .19, .11), 0, .9, dirt=.5)
    cob = cobre("nf_cobre"); cab = cabelo("nf_cabelo", (.02, .018, .015), fios=140)
    corpo(R, skin, anil, anil, mangas=skin, maos=skin, mulher=True, magro=.85, busto=.5, descalco=True)
    aba(R, anil, z0=1.05, z1=.22, aberto=0, rodado=.75, jag=.06, seed=7, folds=10, famp=.05)
    R.rigid([prim("primitive_torus_add", faixa, (0, 0, 1.04), (1, .85, 1.4), major_radius=.125, minor_radius=.016)]
            + tira(faixa, [Vector((.1, -.1, 1.02)), Vector((.12, -.11, .85))], w=.03, t=.006), "hips")
    # canga nos ombros com os dois potes
    cg = [along("primitive_cylinder_add", mad, (-.62, .06, 1.41), (.62, .06, 1.41), .018, vertices=8)]
    for sd in (1, -1):
        p = Vector((.58*sd, .06, 1.41))
        for dx in (-.04, .04):
            cg.append(along("primitive_cylinder_add", corda, p, p + Vector((dx, 0, -.4)), .004, vertices=4))
        c = p + Vector((0, 0, -.55))
        cg.append(prim("primitive_uv_sphere_add", barro, c, (.11, .11, .13), segments=14, ring_count=10))
        cg.append(prim("primitive_cylinder_add", barro, c + Vector((0, 0, .14)), (.05, .05, .03), vertices=12))
        cg.append(prim("primitive_torus_add", barro, c + Vector((0, 0, .17)), (1, 1, 1), major_radius=.055, minor_radius=.012))
        cg.append(prim("primitive_torus_add", corda, c + Vector((0, 0, .1)), (1, 1, 1), major_radius=.095, minor_radius=.006))
    R.rigid(cg, "canga")
    # cabeça: rosto jovem, tranças com fios de cobre
    hd = cabeca(R, skin, mulher=True, idade=0, queixo=.9, sobrancelha=cab)
    hd += cabelo_curto(cab, 1.0)
    rr = random.Random(3)
    for k in range(10):
        a = math.pi*(.15 + .7*k/9); p0 = HC + Vector((.085*math.cos(a), .09*math.sin(a) - .02 + .03, .0))
        for j in range(5):
            p = p0 + Vector((.012*math.cos(a)*j, .01*j, -.035*j))
            hd.append(prim("primitive_uv_sphere_add", cab, p, (.011, .011, .014), segments=6, ring_count=4))
            if j == 3: hd.append(prim("primitive_torus_add", cob, p, (1, 1, 1), major_radius=.012, minor_radius=.003))
    R.rigid(hd, "head")
    return fim(R, INFO)

# a canga se equilibra sozinha nos ombros; braços soltos, prontos para servir
BASE = {"upper_arm.L": {"y": 30, "x": -4}, "forearm.L": {"bend": -30}, "upper_arm.R": {"y": -30, "x": -4}, "forearm.R": {"bend": -30},
        "head": {"x": -3}}

def anims(R):
    def ex(i, n):  # equilibra os potes, a canga balança
        return {"canga": {"z": 3*wave(i, n)}, "chest": {"y": 2*wave(i, n)}}
    def wk(i, n):
        return {"canga": {"z": 5*wave(i, n), "x": 2*wave(i, n*.5)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 0), passo=18, walk_extra=wk)
