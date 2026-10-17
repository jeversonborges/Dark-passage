# Nina (neutra, Bairro Afogado). Menina de uns onze anos que mora num quarto de 5º andar que hoje é porão. Cabelo
# raspado por causa dos piolhos, casaco de homem com as mangas enroladas cinco vezes (rolos grossos nos pulsos),
# barra arrastando na canela, máscara de pano no pescoço, mãos pretas de fuligem, botas grandes demais amarradas
# com barbante. Abraça contra o peito o caderno da mãe (capa de pano florido, fita amarrada). Sem brilho.
from kit import *

INFO = info("neutro", tz=.72, escala=.68, px=192)

def build():
    R = rig("nina")
    skin = pele("ni_pele", (.38, .28, .22), sujo=.55)
    fulig = pele("ni_fuligem", (.07, .06, .055), sujo=.2, rubor_amt=0)
    casaco = pano("ni_casaco", (.11, .1, .085), vinco=.5, desbote=.45, remendo=(.17, .12, .08), rem_amt=.2, grime=1.2)
    vest = pano("ni_vestido", (.2, .13, .1), vinco=.3, desbote=.3)
    meia = pano("ni_meia", (.12, .11, .1), listra=(.2, .18, .15), listra_per=.03)
    bot = couro("ni_bota", (.07, .05, .035), rachado=.7, gasto=.6)
    masc = pano("ni_mascara", (.3, .26, .2), vinco=.2, mancha_amt=.5)
    barb = mat("ni_barbante", (.3, .25, .15), 0, .9, dirt=.5)
    cab = cabelo("ni_cabelo", (.08, .055, .04), fios=200)
    corpo(R, skin, casaco, meia, mangas=casaco, botas=bot, maos=fulig, mulher=True, busto=0, magro=.72, larg=.88, punho=1.6,
          manga_r=1.22, cano=.28, bota_r=1.15)
    aba(R, casaco, z1=.3, aberto=.4, rodado=.95, larg=.9, jag=.08, seed=9, folds=8, famp=.07)
    gola(R, casaco, alta=.06, lapela=True)
    # mangas enroladas cinco vezes: rolos grossos nos pulsos
    for n in "LR":
        o_, ax, u, sd_ = R.frame(f"forearm.{n}"); rot = tuple(math.degrees(v) for v in ax.to_track_quat('Z', 'Y').to_euler())
        R.rigid([prim("primitive_torus_add", casaco, o_ + ax*(.13 + .02*k), (1, 1, 1), rot=rot, major_radius=.062 - .002*k,
                      minor_radius=.014, major_segments=14, minor_segments=6) for k in range(5)], f"forearm.{n}")
        R.rigid([prim("primitive_torus_add", barb, R.P(f"shin.{n}").lerp(R.P(f"foot.{n}"), .7), (1, 1, 1), major_radius=.075, minor_radius=.004)], f"shin.{n}")
    # caderno da mãe abraçado no peito
    cad = pano("ni_caderno", (.25, .12, .09), pintas=[((.4, .36, .2), 40, .14)], vinco=.1)
    papel = pano("ni_folhas", (.45, .42, .35), vinco=.05, mancha_amt=.3)
    R.rigid([prim("primitive_cube_add", cad, (0, -.2, 1.25), (.075, .016, .1), rot=(-12, 0, 6)),
             prim("primitive_cube_add", papel, (0, -.2, 1.25), (.07, .013, .096), rot=(-12, 0, 6)),
             prim("primitive_cube_add", mat("ni_fita", (.35, .06, .05), 0, .6), (0, -.2, 1.25), (.078, .02, .006), rot=(-12, 0, 6))], "chest")
    # cabeça: cabeça de criança, cabelo raspado, máscara de pano caída no pescoço
    hd = cabeca(R, skin, mulher=True, idade=0, esc=1.14, queixo=.85, nariz=.85, sobrancelha=cab)
    hd += raspado(cab)
    R.rigid(hd, "head")
    R.rigid([skirt("ni_masc", masc, [(1.53, .07, .066, -.01), (1.46, .085, .08, -.01), (1.42, .095, .088, -.01)], seg=24, thick=.008)], "neck")
    return fim(R, INFO)

# abraça o caderno com os dois braços
BASE = {"upper_arm.L": {"y": 26, "x": -34, "z": -20}, "forearm.L": {"bend": -105},
        "upper_arm.R": {"y": -26, "x": -34, "z": 20}, "forearm.R": {"bend": -105},
        "spine": {"x": 4}, "chest": {"x": 4}, "head": {"x": 8}}

def anims(R):
    def ex(i, n):  # aperta o caderno e olha desconfiada para os lados
        return {"head": {"z": 18*math.sin(i/n*2*math.pi)**3}}
    return anims_npc(R, BASE, idle_extra=ex, balanco=(0, 0), passo=18)
