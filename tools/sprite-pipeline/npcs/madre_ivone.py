# Ivone das Chagas, Madre Superiora do Culto (Arautos, Capela de São Lázaro). Ex-enfermeira do hospício; quer o
# fim por misericórdia e bebe água com Amargo todo dia como comunhão. Mulher alta, túnica vinho até o chão bordada
# com fios de ouro sujo (barra e faixa do peito), escapulário, véu curto de enfermeira por baixo do capuz, máscara de
# gás de osso pendurada no pescoço, cálice de lata na cintura. As mãos enfaixadas sangram sempre no mesmo ponto das
# palmas, e as feridas brilham verde (único brilho: o Amargo nas palmas). Ergue as duas mãos abertas, mostrando-as.
from kit import *

INFO = info("arautos", tz=.95, escala=1.06, px=208)

def build():
    R = rig("madre_ivone")
    skin = pele("iv_pele", (.33, .25, .22), sujo=.25, rubor_amt=.15)
    vinho = pano("iv_tunica", (.17, .025, .035), vinco=.5, desbote=.35, barra=(.1, (.3, .2, .06)), grime=1.0)
    ouro_b = pano("iv_bordado", (.36, .24, .07), vinco=.1, desbote=.3, trama=200, rough=.4, mancha_amt=.5)
    branco = pano("iv_veu", (.4, .38, .34), vinco=.4, desbote=.1, mancha_amt=.4)
    faixa = linho("iv_faixas", (.38, .33, .26), band=16, resin=.0, mud_amt=.3, stain2=(.25, .02, .02), stain2_amt=.7)
    osso = stained("iv_osso", (.45, .4, .3), stain=(.15, .1, .06), amount=.5, scale=8, rough=.6, grime=.4)
    bot = couro("iv_sapato", (.04, .02, .02))
    lat = latao("iv_lata", (.3, .28, .25), amount=.2); fer = ferro("iv_ferro")
    amargo = glow("iv_amargo", (.35, 1.0, .35), 3.0)
    corpo(R, skin, vinho, vinho, mangas=vinho, botas=bot, maos=faixa, mulher=True, magro=.9, busto=.35, cano=.1, punho=1.5, manga_r=1.12)
    aba(R, vinho, z0=1.05, z1=.06, aberto=0, rodado=.85, jag=.03, seed=5, folds=11, famp=.05)
    R.rigid(capuz(vinho, caido=True), "chest")
    # faixa bordada a ouro descendo do peito (estola) e escapulário
    est = []
    for sd in (1, -1):
        est += tira(ouro_b, [Vector((.07*sd, -.07, 1.49)), Vector((.08*sd, -.13, 1.35)), Vector((.075*sd, -.14, 1.15))], w=.045, t=.006)
    R.rigid(est, "chest")
    est = []
    for sd in (1, -1):
        est += tira(ouro_b, [Vector((.075*sd, -.15, 1.12)), Vector((.08*sd, -.18, .8)), Vector((.085*sd, -.2, .45)), Vector((.09*sd, -.21, .14))], w=.045, t=.006)
    R.rigid(est, "hips")
    R.rigid([prim("primitive_torus_add", ouro_b, (0, 0, 1.02), (1, .78, 1.6), major_radius=.16, minor_radius=.014)], "hips")
    # cálice de lata pendurado no cordão
    R.rigid([prim("primitive_cone_add", lat, (.15, -.08, .9), (.03, .03, .035), vertices=12, rot=(180, 0, 0)),
             along("primitive_cylinder_add", lat, (.15, -.08, .86), (.15, -.08, .82), .006, vertices=6),
             prim("primitive_cylinder_add", lat, (.15, -.08, .815), (.022, .022, .004), vertices=12)], "hips")
    # máscara de gás de osso pendurada no pescoço
    R.rigid(mascara_gas(osso, vidro("iv_lente", (.05, .08, .06)), fer, pos=Vector((0, -.13, 1.38))), "chest")
    # chagas acesas nas palmas
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"hand.{n}")
        R.rigid([prim("primitive_uv_sphere_add", amargo, o_ + ax*.05 - u*.04, (.012, .012, .008), segments=8, ring_count=6),
                 prim("primitive_uv_sphere_add", mat("iv_sangue", (.2, .01, .01), 0, .3), o_ + ax*.05 - u*.037, (.02, .02, .006), segments=8, ring_count=6)], f"hand.{n}")
    # cabeça: rosto sereno e cansado, véu de enfermeira branco sob o capuz caído
    hd = cabeca(R, skin, mulher=True, idade=.55, magro=.9, sobrancelha=cabelo("iv_sobr", (.1, .08, .07)))
    hd += lenco(branco, no_=False)
    hd.append(skirt("iv_veu2", branco, [(HC.z + .06, .1, .11, .01), (HC.z - .06, .11, .11, .03), (1.5, .14, .13, .05)], open_front=1.3, seg=24, thick=.008))
    R.rigid(hd, "head")
    return fim(R, INFO)

# mãos erguidas à frente, palmas viradas para quem fala com ela
BASE = {"upper_arm.L": {"y": 24, "x": -38}, "forearm.L": {"bend": -62}, "hand.L": {"x": 55},
        "upper_arm.R": {"y": -24, "x": -38}, "forearm.R": {"bend": -62}, "hand.R": {"x": 55}, "head": {"x": 5}}

def anims(R):
    def ex(i, n):  # mãos sobem e descem devagar como quem abençoa
        return {"upper_arm.L": {"x": -5*wave(i, n)}, "upper_arm.R": {"x": -5*wave(i, n)}, "head": {"x": 2*wave(i, n, ph=1)}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(.2, .2), passo=14)
